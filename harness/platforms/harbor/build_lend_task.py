"""Package our task `lend-messy` (Markdown format) as a Harbor task. No model, no network.

    python3 build_lend_task.py download/lend-task

Writes a Harbor task folder from `harness/tasks/lend-messy/`:
  task.md (+ the Markdown spec line)  ->  instruction.md
  spec/                               ->  environment/spec/, copied into the image at /app/spec
  hidden_tests/                       ->  tests/   (Harbor uploads /tests only for verification)
  reference/                          ->  solution/reference/, installed by solution/solve.sh
The output is generated, so it lives under download/ (ignored by git).
"""
import json
import shutil
import sys
from pathlib import Path

TASK = Path(__file__).resolve().parents[2] / "tasks" / "lend-messy"
out = Path(sys.argv[1]).resolve()
if out.exists():
    shutil.rmtree(out)
(out / "environment").mkdir(parents=True)
(out / "tests").mkdir()
(out / "solution").mkdir()

inputs = json.loads((TASK / "inputs.json").read_text(encoding="utf-8"))
spec_line = inputs["formats"]["markdown"]["spec_line"]
(out / "instruction.md").write_text(
    (TASK / "task.md").read_text(encoding="utf-8").replace("{SPEC_LINE}", spec_line), encoding="utf-8")

shutil.copytree(TASK / "spec", out / "environment" / "spec")
(out / "environment" / "Dockerfile").write_text(
    "FROM python:3.12-slim\nWORKDIR /app\nCOPY spec /app/spec\n", encoding="utf-8")

shutil.copy(TASK / "hidden_tests" / "test_lend_hidden.py", out / "tests" / "test_lend_hidden.py")
(out / "tests" / "test.sh").write_text('''#!/bin/bash
# Install what the agent built, run the hidden tests, write several named rewards.
python -m venv /tmp/venv
/tmp/venv/bin/pip install -q -e /app pytest > /logs/verifier/pip.log 2>&1 \\
  || { echo '{"reward": 0, "tests_passed": 0, "tests_total": 24, "installable": 0}' > /logs/verifier/reward.json; exit 0; }
cd /tmp && LEND_CMD=/tmp/venv/bin/lend /tmp/venv/bin/python -m pytest /tests/test_lend_hidden.py \\
  -q -p no:cacheprovider --junitxml /logs/verifier/junit.xml > /logs/verifier/pytest.out 2>&1
/tmp/venv/bin/python - <<'PY'
import json, xml.etree.ElementTree as ET
cases = list(ET.parse("/logs/verifier/junit.xml").getroot().iter("testcase"))
passed = sum(1 for c in cases if all(c.find(t) is None for t in ("failure", "error", "skipped")))
json.dump({"reward": passed / len(cases) if cases else 0, "tests_passed": passed,
           "tests_total": len(cases), "installable": 1}, open("/logs/verifier/reward.json", "w"))
PY
''', encoding="utf-8")

shutil.copytree(TASK / "reference", out / "solution" / "reference",
                ignore=shutil.ignore_patterns("__pycache__", "*.egg-info"))
(out / "solution" / "solve.sh").write_text('''#!/bin/bash
# Reference solution: copy the reference implementation into the workspace.
cp -r /solution/reference/. /app/
# Probe for the trial record: can the agent phase see the hidden tests?
echo "PROBE tests dir during agent phase: $(ls /tests 2>&1 | tr '\\n' ' ')"
echo "PROBE files under /app: $(cd /app && find . -maxdepth 2 -not -path './spec/*' | sort | tr '\\n' ' ')"
''', encoding="utf-8")

(out / "task.toml").write_text('''schema_version = "1.4"
artifacts = []

[task]
name = "sdd-compiler/lend-messy-markdown"
version = "0.0.1"
description = "lend: a tool-library loan CLI specified messily across 7 Markdown files"
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
print("wrote", out)
