"""Repackage one DevEval Python project as a clean Harbor task: empty source tree, hidden tests, no reference.

    python3 build_clean_task.py python-hone markdown download/clean/hone-markdown
    python3 build_clean_task.py python-hone export   download/clean/hone-export  ~/sddc-runs/deveval-hone/export
    python3 build_clean_task.py python-lice markdown download/clean/lice-markdown \\
        --claude-version 2.1.296 --agent-network allowlist

Reads `download/deveval/<project>-implementation/environment/deveval_source_repo/` (the Harbor dataset,
see TRIAL.md) and writes a Harbor task in which the agent's container holds only:
  /app/spec/             the specification, in one format
  /app/<seed files>      the project's `required_files`, every data file (not `.py`) under a package
                         directory, and test helper modules the tests import (HELPERS)
The unit and acceptance tests and the dependency list go to tests/ (Harbor uploads /tests only for
verification); every other `.py` file is the reference and goes to solution/ (uploaded only for the
`oracle` agent). No model, no network.
Options (the same as `harness/platforms/harbor/build_lend_task.py`):
  --claude-version V    install that Claude Code release into the image (run with `--ak version=V`)
  --agent-network MODE  `public` (default) or `allowlist`: the agent phase reaches only the model API
                        and PyPI. The verifier keeps public network.
Python projects only; a project is usable once the `oracle` agent passes every test and `nop` passes none.
"""
import argparse
import json
import re
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
DOCS = ("PRD", "UML_class", "UML_sequence", "architecture_design")
# test helpers that live in the product tree and are imported by the tests
HELPERS = {"python-hone": ["hone/utils/test_utils.py"]}
# system libraries a project's dependencies need at import time (opencv needs these)
SYSTEM_PACKAGES = {"python-hybrid-images": "libxcb1 libgl1 libglib2.0-0"}
NOT_PRODUCT = {"examples", "docs", ".git"}        # top-level folders that are neither product nor seed
AGENT_HOSTS = ["api.anthropic.com", "pypi.org", "files.pythonhosted.org"]
SPEC_LINE = {
    "markdown": "The specification is the Markdown files in `spec/`. Start with `spec/PRD.md`.",
    "export": "The specification is the compiled export in `spec/`. Start with `spec/MAP.md`; "
              "account for every id in `spec/CHECKLIST.md`.",
}
TASK_TEXT = """# Task

Build the Python project described by the specification. {spec_line}

- Work in the current directory (`/app`). Put the code where the specification's architecture says.
- Files already present outside `spec/` are the project's data files, its dependency list, or test
  helpers; keep them where they are.{seed_line}
- Dependencies, if any, go in `requirements.txt` at the top level.
- The project will be checked by tests you cannot see. Do not look for them and do not use the network
  to fetch an existing implementation of this project.
"""

ap = argparse.ArgumentParser()
ap.add_argument("project")
ap.add_argument("format", choices=("markdown", "export"))
ap.add_argument("out", type=Path)
ap.add_argument("export_dir", nargs="?", type=Path)
ap.add_argument("--claude-version")
ap.add_argument("--agent-network", choices=("public", "allowlist"), default="public")
a = ap.parse_args()
project, fmt, out = a.project, a.format, a.out.resolve()
repo = HERE / "download" / "deveval" / f"{project}-implementation" / "environment" / "deveval_source_repo"
cfg = json.loads((repo / "repo_config.json").read_text(encoding="utf-8"))
if cfg.get("language") != "python":
    raise SystemExit(f"{project}: language {cfg.get('language')!r}; this script handles Python projects only")
tests = [cfg["unit_tests"], cfg["acceptance_tests"]]
if out.exists():
    shutil.rmtree(out)
env = out / "environment"
(env / "seed").mkdir(parents=True)
(out / "tests").mkdir()
(out / "solution" / "reference").mkdir(parents=True)


def put(rel: str, root: Path) -> None:
    (root / rel).parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(repo / rel, root / rel)


# specification
if fmt == "markdown":
    (env / "spec").mkdir()
    for key in DOCS:
        shutil.copy(repo / cfg[key], env / "spec" / Path(cfg[key]).name)
else:
    if not a.export_dir:
        raise SystemExit("format export needs the export folder as the fourth argument")
    shutil.copytree(a.export_dir.expanduser(), env / "spec")

# sort every file of the project: specification, test, seed, reference, or left out
spec_files = {cfg[key] for key in DOCS}
required = set()
for pattern in cfg.get("required_files", []):
    for hit in (repo.glob(pattern) if "*" in pattern else [repo / pattern]):
        required |= {str(f.relative_to(repo)) for f in ([hit] if hit.is_file() else hit.rglob("*")) if f.is_file()}
dag = cfg.get("code_file_DAG", {})
packages = {Path(f).parts[0] for f in set(dag) | {d for deps in dag.values() for d in deps} if len(Path(f).parts) > 1}
seed, reference = set(required) | set(HELPERS.get(project, [])), set()
for f in sorted(p for p in repo.rglob("*") if p.is_file() and "__pycache__" not in p.parts):
    rel = str(f.relative_to(repo))
    top = f.relative_to(repo).parts[0]
    if rel in seed or rel in spec_files or top in tests or top in NOT_PRODUCT:
        continue
    if f.suffix == ".py":
        reference.add(rel)
    elif top in packages:
        seed.add(rel)                                    # a data file inside the package
for rel in sorted(seed):
    put(rel, env / "seed")
for rel in sorted(reference):
    put(rel, out / "solution" / "reference")

dockerfile = "FROM python:3.12-slim\n"
if project in SYSTEM_PACKAGES:
    dockerfile += (f"RUN apt-get update && apt-get install -y --no-install-recommends {SYSTEM_PACKAGES[project]}"
                   " && rm -rf /var/lib/apt/lists/*\n")
if a.claude_version:
    dockerfile += (
        "RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates procps"
        " && rm -rf /var/lib/apt/lists/*\n"
        "RUN curl -fsSL https://downloads.claude.ai/claude-code-releases/bootstrap.sh"
        f" | bash -s -- {a.claude_version}\n"
        'ENV PATH="/root/.local/bin:$PATH"\n')
dockerfile += "WORKDIR /app\nCOPY seed/ /app/\nCOPY spec /app/spec\n"
(env / "Dockerfile").write_text(dockerfile, encoding="utf-8")

tops = sorted({Path(rel).parts[0] + ("/" if len(Path(rel).parts) > 1 else "") for rel in seed})
seed_line = f" Present now: {', '.join(f'`{t}`' for t in tops)}." if tops else ""
(out / "instruction.md").write_text(TASK_TEXT.format(spec_line=SPEC_LINE[fmt], seed_line=seed_line), encoding="utf-8")

# hidden tests, and the project's own dependency list so scoring does not depend on the agent keeping it
n_tests = 0
for folder in tests:
    shutil.copytree(repo / folder, out / "tests" / folder, ignore=shutil.ignore_patterns("__pycache__"))
    n_tests += sum(len(re.findall(r"^\s*def test_", p.read_text(encoding="utf-8"), re.M))
                   for p in (out / "tests" / folder).rglob("*.py"))
deps = cfg.get("dependencies") or ""
if deps and (repo / deps).is_file():
    shutil.copy(repo / deps, out / "tests" / "project_requirements.txt")
(out / "tests" / "test.sh").write_text(f'''#!/bin/bash
# Keep what the agent wrote, copy the hidden tests beside it, run them, write named rewards.
mkdir -p /logs/verifier/agent_files
tar -czf /logs/verifier/agent_files/app.tgz -C /app --exclude=./spec --exclude='*.egg-info' \\
  --exclude=__pycache__ --exclude=.venv --exclude=venv --exclude=.pytest_cache . 2>/dev/null
# Test folders the agent wrote are set aside (they are in app.tgz): only the hidden tests are scored.
rm -rf /app/{tests[0]} /app/{tests[1]}
cp -r /tests/{tests[0]} /tests/{tests[1]} /app/
cd /app
python -m venv /tmp/venv
/tmp/venv/bin/pip install -q pytest > /logs/verifier/pip.log 2>&1
# One requirement at a time: some DevEval lists name standard-library modules, which pip cannot install.
for req in /tests/project_requirements.txt requirements.txt; do
  [ -f "$req" ] && grep -vE '^[[:space:]]*(#|$)' "$req" | while read -r line; do
    /tmp/venv/bin/pip install -q "$line" >> /logs/verifier/pip.log 2>&1 || echo "NOT INSTALLED: $line" >> /logs/verifier/pip.log
  done
done
# Unit and acceptance tests in separate processes, as DevEval runs them.
for folder in {tests[0]} {tests[1]}; do
  PYTHONPATH=/app /tmp/venv/bin/python -m pytest $folder \\
    -q -p no:cacheprovider --confcutdir=$folder --junitxml /logs/verifier/junit-$folder.xml >> /logs/verifier/pytest.out 2>&1
done
/tmp/venv/bin/python - <<'PY'
import json, xml.etree.ElementTree as ET
TOTAL = {n_tests}
cases = []
for folder in ("{tests[0]}", "{tests[1]}"):
    try:
        cases += list(ET.parse(f"/logs/verifier/junit-{{folder}}.xml").getroot().iter("testcase"))
    except Exception:
        pass
passed = sum(1 for c in cases if all(c.find(t) is None for t in ("failure", "error", "skipped")))
json.dump({{"reward": passed / TOTAL, "tests_passed": passed, "tests_total": TOTAL,
           "tests_collected": len(cases)}}, open("/logs/verifier/reward.json", "w"))
PY
''', encoding="utf-8")

(out / "solution" / "solve.sh").write_text('''#!/bin/bash
cp -r /solution/reference/. /app/
echo "PROBE /tests during agent phase: $(ls /tests 2>&1 | tr '\\n' ' ')"
echo "PROBE files under /app: $(cd /app && find . -maxdepth 3 -not -path './spec/*' | sort | head -60 | tr '\\n' ' ')"
''', encoding="utf-8")

agent_network = ""
if a.agent_network == "allowlist":
    agent_network = 'network_mode = "allowlist"\nallowed_hosts = ' + json.dumps(AGENT_HOSTS) + "\n"
(out / "task.toml").write_text(f'''schema_version = "1.4"
artifacts = []

[task]
name = "sdd-compiler/deveval-{project}-{fmt}"
version = "0.0.2"
description = "DevEval project {project}, repackaged clean: specification in {fmt} format"
authors = []
keywords = []

[metadata]

[verifier]
timeout_sec = 900.0
collect = []
network_mode = "public"

[verifier.env]

[agent]
timeout_sec = 3600.0
{agent_network}
[environment]
network_mode = "public"
build_timeout_sec = 900.0
os = "linux"
mcp_servers = []

[environment.env]

[solution.env]
''', encoding="utf-8")
print(f"wrote {out} | tests: {n_tests} | seed files: {len(seed)} | reference files: {sorted(reference)}")
