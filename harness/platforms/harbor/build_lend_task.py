"""Package our task `lend-messy` as a Harbor task, one spec format per task. No model, no network.

    python3 build_lend_task.py download/lend-markdown
    python3 build_lend_task.py download/lend-export --format export --export-dir ~/sddc-runs/lend-export
    python3 build_lend_task.py download/lend-markdown --claude-version 2.1.296 --agent-network allowlist

Writes a Harbor task folder from `harness/tasks/lend-messy/`:
  task.md (+ the format's spec line)  ->  instruction.md
  spec/ or the export folder          ->  environment/spec/, copied into the image at /app/spec
  hidden_tests/ and scoring/          ->  tests/   (Harbor uploads /tests only for verification)
  reference/                          ->  solution/reference/, installed by solution/solve.sh
Options:
  --claude-version V    install that Claude Code release into the image, so every run uses the same
                        version and Harbor skips its own install (run with `--ak version=V`)
  --agent-network MODE  `public` (default) or `allowlist`: during the agent phase only the model API
                        and PyPI are reachable. The verifier keeps public network to install pytest.
  --settled P2=A,P3=B   contradictions the owner settled; the scorer checks the build against them
  --decisions FILE      Markdown format only: add FILE to the spec folder as spec/DECISIONS.md (round 5
                        control: the owner's decisions as plain text, no graph)
The output is generated, so it lives under download/ (ignored by git).
"""
import argparse
import json
import shutil
from pathlib import Path

TASK = Path(__file__).resolve().parents[2] / "tasks" / "lend-messy"
AGENT_HOSTS = ["api.anthropic.com", "pypi.org", "files.pythonhosted.org"]

ap = argparse.ArgumentParser()
ap.add_argument("out", type=Path)
ap.add_argument("--format", choices=("markdown", "export"), default="markdown")
ap.add_argument("--export-dir", type=Path)
ap.add_argument("--claude-version")
ap.add_argument("--agent-network", choices=("public", "allowlist"), default="public")
ap.add_argument("--settled", default="")
ap.add_argument("--decisions", type=Path)
a = ap.parse_args()
out = a.out.resolve()
if out.exists():
    shutil.rmtree(out)
(out / "environment").mkdir(parents=True)
(out / "solution").mkdir()

inputs = json.loads((TASK / "inputs.json").read_text(encoding="utf-8"))
spec_line = inputs["formats"][a.format]["spec_line"]
(out / "instruction.md").write_text(
    (TASK / "task.md").read_text(encoding="utf-8").replace("{SPEC_LINE}", spec_line), encoding="utf-8")

if a.format == "markdown":
    shutil.copytree(TASK / "spec", out / "environment" / "spec")
    if a.decisions:
        shutil.copy(a.decisions, out / "environment" / "spec" / "DECISIONS.md")
else:
    if not a.export_dir or not (a.export_dir.expanduser() / "MAP.md").is_file():
        raise SystemExit("--format export needs --export-dir pointing at a folder with MAP.md")
    shutil.copytree(a.export_dir.expanduser(), out / "environment" / "spec")

dockerfile = "FROM python:3.12-slim\n"
if a.claude_version:
    dockerfile += (
        "RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates procps"
        " && rm -rf /var/lib/apt/lists/*\n"
        "RUN curl -fsSL https://downloads.claude.ai/claude-code-releases/bootstrap.sh"
        f" | bash -s -- {a.claude_version}\n"
        'ENV PATH="/root/.local/bin:$PATH"\n')
dockerfile += "WORKDIR /app\nCOPY spec /app/spec\n"
(out / "environment" / "Dockerfile").write_text(dockerfile, encoding="utf-8")

shutil.copytree(TASK / "hidden_tests", out / "tests", ignore=shutil.ignore_patterns("__pycache__"))
shutil.copy(TASK / "scoring" / "lend_score.py", out / "tests" / "lend_score.py")
(out / "tests" / "test.sh").write_text('''#!/bin/bash
# Keep what the agent wrote, install it, run the hidden tests, then score (lend_score.py).
mkdir -p /logs/verifier/agent_files
cp /app/OPEN_QUESTIONS.md /app/IMPLEMENTATION_NOTES.md /app/pyproject.toml /logs/verifier/agent_files/ 2>/dev/null
tar -czf /logs/verifier/agent_files/app.tgz -C /app --exclude=./spec --exclude='*.egg-info' \\
  --exclude=__pycache__ --exclude=.venv --exclude=venv --exclude=.pytest_cache . 2>/dev/null
python -m venv /tmp/venv
if ! /tmp/venv/bin/pip install -q -e /app pytest > /logs/verifier/pip.log 2>&1; then
  /tmp/venv/bin/python /tests/lend_score.py --not-installable --app /app --out-dir /logs/verifier SETTLED
  exit 0
fi
cd /tmp && LEND_CMD=/tmp/venv/bin/lend /tmp/venv/bin/python -m pytest /tests/test_lend_hidden.py \\
  -q -p no:cacheprovider --junitxml /logs/verifier/junit.xml > /logs/verifier/pytest.out 2>&1
/tmp/venv/bin/python /tests/lend_score.py --cmd /tmp/venv/bin/lend --app /app \\
  --junit /logs/verifier/junit.xml --out-dir /logs/verifier SETTLED
'''.replace(" SETTLED", f" --settled {a.settled}" if a.settled else ""), encoding="utf-8")

shutil.copytree(TASK / "reference", out / "solution" / "reference",
                ignore=shutil.ignore_patterns("__pycache__", "*.egg-info"))
(out / "solution" / "solve.sh").write_text('''#!/bin/bash
# Reference solution: copy the reference implementation into the workspace.
cp -r /solution/reference/. /app/
# Probes for the trial record: what can the agent phase see and reach?
echo "PROBE tests dir during agent phase: $(ls /tests 2>&1 | tr '\\n' ' ')"
echo "PROBE files under /app: $(cd /app && find . -maxdepth 2 -not -path './spec/*' | sort | tr '\\n' ' ')"
echo "PROBE claude: $(claude --version 2>&1 | head -1)"
for host in pypi.org api.anthropic.com example.com github.com; do
  echo "PROBE network $host: $(python - "$host" <<'PY'
import sys, urllib.request, urllib.error
try:
    urllib.request.urlopen("https://" + sys.argv[1], timeout=10)
    print("reached")
except urllib.error.HTTPError as e:
    print("reached (HTTP %d)" % e.code)
except Exception as e:
    print("blocked:", type(e).__name__)
PY
)"
done
''', encoding="utf-8")

agent_network = ""
if a.agent_network == "allowlist":
    agent_network = 'network_mode = "allowlist"\nallowed_hosts = ' + json.dumps(AGENT_HOSTS) + "\n"
(out / "task.toml").write_text(f'''schema_version = "1.4"
artifacts = []

[task]
name = "sdd-compiler/lend-messy-{a.format}"
version = "0.0.2"
description = "lend: a tool-library loan CLI specified messily; specification in {a.format} format"
authors = []
keywords = []

[metadata]

[verifier]
timeout_sec = 600.0
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
print("wrote", out)
