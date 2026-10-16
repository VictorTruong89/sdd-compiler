"""Make a Harbor task from one Zero2Repo case under our conditions, in Markdown or export format.

    python3 build_task.py markdown ../work/tasks/case004-markdown
    python3 build_task.py export   ../work/tasks/case004-export   ../work/compile/export

Reads the case from the Zero2Repo clone (CASE below) and the judge files that Zero2Repo's own Harbor
adapter wrote for it (ADAPTER, made by `zero2repo-harbor --case-id case004 --force`). Differences from
Zero2Repo's own task, so the conditions match our DevEval rounds (harness/benchmarks/devbench-2024):
  - the specification is files in /app/spec/, not pasted into instruction.md, so the two formats differ
    only in spec/ and one sentence;
  - Claude Code is pinned (CLAUDE_VERSION) instead of `@latest`; no Node.js, opencode or codex;
  - the agent phase reaches only the model API and PyPI (allow-list);
  - test.sh keeps the agent's workspace (app.tgz), runs Zero2Repo's own judge unchanged (binary
    reward, kept as official_reward.json and final_report.json), then runs the same hidden test files
    once more with --junitxml for a per-test score; reward.json holds the per-test fraction.
"""
import json
import re
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
Z = HERE.parents[2] / "benchmarks" / "zero2repo" / "download" / "Zero2Repo" / "benchmark"
CASE = Z / "cases" / "case004"
ADAPTER = Z / "output" / "case004"
CLAUDE_VERSION = "2.1.296"
AGENT_HOSTS = ["api.anthropic.com", "pypi.org", "files.pythonhosted.org"]
PUBLIC = ("Full_PRD.md", "Interface_Contract.md", "Hardware_Requirements.md")
SPEC_LINE = {
    "markdown": "The specification is the Markdown files in `spec/`: `spec/Full_PRD.md` (requirements), "
                "`spec/Interface_Contract.md` (the public interface) and `spec/Hardware_Requirements.md`.",
    "export": "The specification is the compiled export in `spec/`. Start with `spec/MAP.md`; "
              "account for every id in `spec/CHECKLIST.md`.",
}

fmt, out = sys.argv[1], Path(sys.argv[2]).resolve()
assert fmt in SPEC_LINE, fmt
if out.exists():
    shutil.rmtree(out)
env = out / "environment"
env.mkdir(parents=True)

# specification
if fmt == "markdown":
    (env / "spec").mkdir()
    for name in PUBLIC:
        shutil.copy(CASE / "public" / name, env / "spec" / name)
else:
    shutil.copytree(Path(sys.argv[3]).resolve(), env / "spec")

# the build contract the adapter derives from the case's runner (not part of the specification)
adapter_text = (ADAPTER / "instruction.md").read_text(encoding="utf-8")
contract = re.search(r"## Build contract\n\n(.*?)\n\n", adapter_text, re.S).group(1)
(out / "instruction.md").write_text(f"""# Task

Build the project described by the specification, from scratch, in the current directory (`/app`).
{SPEC_LINE[fmt]}

## Build contract

{contract}

- Keep `spec/` as it is. Put the code where the specification says.
- The project will be checked by hidden tests you cannot see. Do not look for them and do not use the
  network to fetch an existing implementation of this project.
""", encoding="utf-8")

(env / "Dockerfile").write_text(f"""FROM python:3.13-slim-bookworm
RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates procps git \\
    && rm -rf /var/lib/apt/lists/*
RUN curl -fsSL https://downloads.claude.ai/claude-code-releases/bootstrap.sh | bash -s -- {CLAUDE_VERSION}
ENV PATH="/root/.local/bin:$PATH"
# the verifier's test runner, as in Zero2Repo's own image, so scoring needs no network
RUN python3 -m pip install --no-cache-dir pytest==8.4.1 pytest-json-ctrf==0.3.5
WORKDIR /app
COPY spec /app/spec
""", encoding="utf-8")

# hidden tests and Zero2Repo's judge, unchanged. The adapter's copy lacks the support files the tests
# import (_harness.py, conftest.py; found 2026-10-14), so the test folder comes from the case itself.
shutil.copytree(ADAPTER / "tests", out / "tests")
shutil.rmtree(out / "tests" / "final" / "tests")
shutil.copytree(CASE / "milestones" / "final" / "tests", out / "tests" / "final" / "tests")
# The adapter also rewrites test_command to absolute /tests/final/... paths; the judge then appends the
# same files again, so every test runs twice and its collection audit fails (reward 0 for any build).
# The case's own manifest (relative paths) is used instead (found 2026-10-14).
shutil.copy(CASE / "milestones" / "final" / "test_manifest.json", out / "tests" / "final" / "test_manifest.json")
test_dir = out / "tests" / "final" / "tests"
n_tests = sum(len(re.findall(r"^\s*def test", p.read_text(encoding="utf-8"), re.M)) for p in test_dir.glob("F*_acceptance.py"))
manifest = json.loads((out / "tests" / "final" / "test_manifest.json").read_text())
files = " ".join(f"/tests/final/{f}" for f in manifest["test_files"])
(out / "tests" / "test.sh").write_text(f"""#!/bin/bash
# Keep the workspace, run Zero2Repo's judge unchanged (binary), then the same tests per test (junit).
set -u
mkdir -p /logs/verifier/agent_files
tar -czf /logs/verifier/agent_files/app.tgz -C /app --exclude=./spec --exclude='*.egg-info' \\
  --exclude=__pycache__ --exclude=.venv --exclude=venv --exclude=.pytest_cache . 2>/dev/null
python3 /tests/final_judge.py
mv /logs/verifier/reward.json /logs/verifier/official_reward.json 2>/dev/null
rm -f /logs/verifier/reward.txt
cd /app
PYTHONPATH=/app/src python3 -m pytest {files} -q -p no:cacheprovider --rootdir=/tests/final/tests \\
  --confcutdir=/tests/final/tests --junitxml=/logs/verifier/junit-final.xml > /logs/verifier/pytest.out 2>&1
python3 - <<'PY'
import json, xml.etree.ElementTree as ET
TOTAL = {n_tests}
try:
    cases = list(ET.parse("/logs/verifier/junit-final.xml").getroot().iter("testcase"))
except Exception:
    cases = []
tests = [c for c in cases if c.get("classname")]
passed = sum(1 for c in tests if all(c.find(t) is None for t in ("failure", "error", "skipped")))
try:
    official = json.load(open("/logs/verifier/official_reward.json"))["reward"]
except Exception:
    official = None
json.dump({{"reward": passed / TOTAL, "tests_passed": passed, "tests_total": TOTAL,
           "tests_collected": len(tests), "collection_errors": len(cases) - len(tests),
           "official_reward": official}}, open("/logs/verifier/reward.json", "w"))
PY
exit 0
""", encoding="utf-8")

(out / "solution").mkdir()
(out / "solution" / "solve.sh").write_text("#!/bin/bash\necho 'no reference solution ships with Zero2Repo'\n", encoding="utf-8")

(out / "task.toml").write_text(f'''schema_version = "1.4"
artifacts = []

[task]
name = "sdd-compiler/zero2repo-case004-{fmt}"
version = "0.0.1"
description = "Zero2Repo case004 (Signtoken), specification in {fmt} format, our conditions"
authors = []
keywords = []

[metadata]

[verifier]
timeout_sec = 900.0
collect = []
network_mode = "public"

[verifier.env]

[agent]
timeout_sec = 7200.0
network_mode = "allowlist"
allowed_hosts = {json.dumps(AGENT_HOSTS)}

[environment]
network_mode = "public"
build_timeout_sec = 900.0
os = "linux"
mcp_servers = []

[environment.env]

[solution.env]
''', encoding="utf-8")
print(f"wrote {out} | format {fmt} | hidden tests {n_tests} | spec files {sorted(p.name for p in (env / 'spec').iterdir())}")
