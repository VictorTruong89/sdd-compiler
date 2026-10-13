"""Repackage one DevEval project as a clean Harbor task: empty source tree, hidden tests, no reference.

    python3 build_clean_task.py python-hone markdown download/clean/hone-markdown
    python3 build_clean_task.py python-hone export   download/clean/hone-export  ~/sddc-runs/deveval-hone/export

Reads `download/deveval/<project>-implementation/environment/deveval_source_repo/` (the Harbor dataset,
see TRIAL.md) and writes a Harbor task in which the agent's container holds only:
  /app/spec/                  the specification, in one format
  /app/<required_files>       the project's data files named in its repo_config.json
  /app/<test helper modules>  source files the tests import that are test helpers, not the product
The unit and acceptance tests go to tests/ (Harbor uploads /tests only for verification); the
reference source goes to solution/ (uploaded only for the `oracle` agent). No model, no network.
Written for the pilot on `python-hone`; other projects need their own HELPERS entry and a check that
their tests run under pytest.
"""
import json
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DOCS = ("PRD", "UML_class", "UML_sequence", "architecture_design")
# test helpers that live in the product tree and are imported by the tests
HELPERS = {"python-hone": ["hone/utils/test_utils.py"]}
SPEC_LINE = {
    "markdown": "The specification is the Markdown files in `spec/`. Start with `spec/PRD.md`.",
    "export": "The specification is the compiled export in `spec/`. Start with `spec/MAP.md`; "
              "account for every id in `spec/CHECKLIST.md`.",
}
TASK_TEXT = """# Task

Build the Python project described by the specification. {spec_line}

- Work in the current directory (`/app`). Put the code where the specification's architecture says.
- `data_file/` holds the project's sample data. Files already present under the package directory are
  test helpers; keep them.
- Dependencies, if any, go in `requirements.txt` at the top level.
- The project will be checked by tests you cannot see. Do not look for them and do not use the network
  to fetch an existing implementation of this project.
"""

project, fmt, out = sys.argv[1], sys.argv[2], Path(sys.argv[3]).resolve()
repo = HERE / "download" / "deveval" / f"{project}-implementation" / "environment" / "deveval_source_repo"
cfg = json.loads((repo / "repo_config.json").read_text(encoding="utf-8"))
if out.exists():
    shutil.rmtree(out)
env = out / "environment"
(env / "seed").mkdir(parents=True)
(out / "tests").mkdir()
(out / "solution" / "reference").mkdir(parents=True)

# specification
if fmt == "markdown":
    (env / "spec").mkdir()
    for key in DOCS:
        shutil.copy(repo / cfg[key], env / "spec" / Path(cfg[key]).name)
else:
    shutil.copytree(Path(sys.argv[4]).expanduser(), env / "spec")

# what the agent starts with besides the specification
for rel in cfg.get("required_files", []):
    src = repo / rel
    (shutil.copytree if src.is_dir() else shutil.copy)(src, env / "seed" / rel)
for rel in HELPERS.get(project, []):
    (env / "seed" / rel).parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(repo / rel, env / "seed" / rel)
(env / "Dockerfile").write_text(
    "FROM python:3.12-slim\nWORKDIR /app\nCOPY seed/ /app/\nCOPY spec /app/spec\n", encoding="utf-8")

(out / "instruction.md").write_text(TASK_TEXT.format(spec_line=SPEC_LINE[fmt]), encoding="utf-8")

# hidden tests
n_tests = 0
for key in ("unit_tests", "acceptance_tests"):
    shutil.copytree(repo / cfg[key], out / "tests" / cfg[key], ignore=shutil.ignore_patterns("__pycache__"))
    n_tests += sum(p.read_text(encoding="utf-8").count("    def test_") for p in (out / "tests" / cfg[key]).glob("*.py"))
(out / "tests" / "test.sh").write_text(f'''#!/bin/bash
# Copy the hidden tests beside the agent's code, run them, write named rewards.
cp -r /tests/{cfg["unit_tests"]} /tests/{cfg["acceptance_tests"]} /app/
cd /app
python -m venv /tmp/venv
/tmp/venv/bin/pip install -q pytest > /logs/verifier/pip.log 2>&1
[ -f requirements.txt ] && /tmp/venv/bin/pip install -q -r requirements.txt >> /logs/verifier/pip.log 2>&1
PYTHONPATH=/app /tmp/venv/bin/python -m pytest {cfg["unit_tests"]} {cfg["acceptance_tests"]} \\
  -q -p no:cacheprovider --junitxml /logs/verifier/junit.xml > /logs/verifier/pytest.out 2>&1
/tmp/venv/bin/python - <<'PY'
import json, xml.etree.ElementTree as ET
TOTAL = {n_tests}
try:
    cases = list(ET.parse("/logs/verifier/junit.xml").getroot().iter("testcase"))
except Exception:
    cases = []
passed = sum(1 for c in cases if all(c.find(t) is None for t in ("failure", "error", "skipped")))
json.dump({{"reward": passed / TOTAL, "tests_passed": passed, "tests_total": TOTAL,
           "tests_collected": len(cases)}}, open("/logs/verifier/reward.json", "w"))
PY
''', encoding="utf-8")

# reference: every source file of the project's file graph that the agent does not start with
dag = cfg.get("code_file_DAG", {})
for rel in sorted(set(dag) | {f for deps in dag.values() for f in deps} | {"hone/utils/__init__.py"}):
    if (repo / rel).is_file():
        (out / "solution" / "reference" / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(repo / rel, out / "solution" / "reference" / rel)
(out / "solution" / "solve.sh").write_text('''#!/bin/bash
cp -r /solution/reference/. /app/
echo "PROBE /tests during agent phase: $(ls /tests 2>&1 | tr '\\n' ' ')"
echo "PROBE files under /app: $(cd /app && find . -maxdepth 3 -not -path './spec/*' -not -path './data_file/*' | sort | tr '\\n' ' ')"
''', encoding="utf-8")

(out / "task.toml").write_text(f'''schema_version = "1.4"
artifacts = []

[task]
name = "sdd-compiler/deveval-{project}-{fmt}"
version = "0.0.1"
description = "DevEval project {project}, repackaged clean: specification in {fmt} format"
authors = []
keywords = []

[metadata]

[verifier]
timeout_sec = 600.0
collect = []

[verifier.env]

[agent]
timeout_sec = 3600.0

[environment]
network_mode = "public"
build_timeout_sec = 600.0
os = "linux"
mcp_servers = []

[environment.env]

[solution.env]
''', encoding="utf-8")
print("wrote", out, "| tests:", n_tests)
