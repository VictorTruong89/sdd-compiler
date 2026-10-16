"""Make a Harbor task from any Zero2Repo case, Markdown specification, under our conditions.

    python3 build_task.py case001 ../work/tasks/case001-markdown

Generalised from ../../r13-zero2repo-case004/notes/build_task.py (same conditions, same two adapter
fixes). Differences from that builder:
  - any case; the spec files are whatever is in the case's public/ folder;
  - Node.js 22 is in the image (as in Zero2Repo's own image), for cases with JavaScript parts;
  - no second pytest pass: the per-test score comes from the judge's own report
    (final_report.json: passed_count, total_count, failed_tests), so each case's own test command,
    PYTHONPATH and runner are used unchanged.
Needs the adapter's output for the case: `zero2repo-harbor --case-id <case> --force`.
"""
import json
import re
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
Z = HERE.parents[2] / "benchmarks" / "zero2repo" / "download" / "Zero2Repo" / "benchmark"
CLAUDE_VERSION = "2.1.296"
AGENT_HOSTS = ["api.anthropic.com", "pypi.org", "files.pythonhosted.org"]

case, out = sys.argv[1], Path(sys.argv[2]).resolve()
CASE, ADAPTER = Z / "cases" / case, Z / "output" / case
assert CASE.is_dir() and ADAPTER.is_dir(), (CASE, ADAPTER)
if out.exists():
    shutil.rmtree(out)
env = out / "environment"
(env / "spec").mkdir(parents=True)
public = sorted(p.name for p in (CASE / "public").iterdir() if p.is_file())
for name in public:
    shutil.copy(CASE / "public" / name, env / "spec" / name)
spec_line = "The specification is the Markdown files in `spec/`: " + ", ".join(f"`spec/{n}`" for n in public) + "."

adapter_text = (ADAPTER / "instruction.md").read_text(encoding="utf-8")
contract = re.search(r"## Build contract\n\n(.*?)\n\n", adapter_text, re.S).group(1)
(out / "instruction.md").write_text(f"""# Task

Build the project described by the specification, from scratch, in the current directory (`/app`).
{spec_line}

## Build contract

{contract}

- Keep `spec/` as it is. Put the code where the specification says.
- The project will be checked by hidden tests you cannot see. Do not look for them and do not use the
  network to fetch an existing implementation of this project.
""", encoding="utf-8")

(env / "Dockerfile").write_text(f"""FROM python:3.13-slim-bookworm
RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates procps git \\
    && rm -rf /var/lib/apt/lists/*
# Node.js, as in Zero2Repo's own image (cases with JavaScript parts)
RUN curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \\
    && apt-get install -y --no-install-recommends nodejs && rm -rf /var/lib/apt/lists/*
RUN curl -fsSL https://downloads.claude.ai/claude-code-releases/bootstrap.sh | bash -s -- {CLAUDE_VERSION}
ENV PATH="/root/.local/bin:$PATH"
# the verifier's test runner, as in Zero2Repo's own image, so scoring needs no network
RUN python3 -m pip install --no-cache-dir pytest==8.4.1 pytest-json-ctrf==0.3.5
WORKDIR /app
COPY spec /app/spec
""", encoding="utf-8")

# Zero2Repo's judge unchanged; test folder and manifest from the case itself (adapter faults 1 and 2,
# r13-zero2repo-case004/TRIAL.md).
shutil.copytree(ADAPTER / "tests", out / "tests")
shutil.rmtree(out / "tests" / "final" / "tests")
shutil.copytree(CASE / "milestones" / "final" / "tests", out / "tests" / "final" / "tests")
shutil.copy(CASE / "milestones" / "final" / "test_manifest.json", out / "tests" / "final" / "test_manifest.json")
(out / "tests" / "test.sh").write_text("""#!/bin/bash
# Keep the workspace, run Zero2Repo's judge unchanged (binary), then take per-test counts from its report.
set -u
mkdir -p /logs/verifier/agent_files
tar -czf /logs/verifier/agent_files/app.tgz -C /app --exclude=./spec --exclude='*.egg-info' \\
  --exclude=__pycache__ --exclude=.venv --exclude=venv --exclude=.pytest_cache --exclude=node_modules . 2>/dev/null
python3 /tests/final_judge.py
mv /logs/verifier/reward.json /logs/verifier/official_reward.json 2>/dev/null
rm -f /logs/verifier/reward.txt
python3 - <<'PY'
import json
try:
    rep = json.load(open("/logs/verifier/final_report.json"))
except Exception:
    rep = {}
f = rep.get("final") or {}
total, passed = f.get("total_count") or 0, f.get("passed_count") or 0
try:
    official = json.load(open("/logs/verifier/official_reward.json"))["reward"]
except Exception:
    official = rep.get("reward")
# Harbor reads every value in reward.json as a number, so only numbers go there; the rest goes to
# reward_detail.json (found 2026-10-14: a null judge_error made Harbor reject the run).
json.dump({"reward": (passed / total) if total else 0.0, "tests_passed": passed, "tests_total": total,
           "tests_failed": f.get("failed_count") or 0, "tests_error": f.get("error_count") or 0,
           "official_reward": float(official or 0)},
          open("/logs/verifier/reward.json", "w"))
json.dump({"judge_error": rep.get("judge_error"), "official_reward_raw": official,
           "failed_tests": f.get("failed_tests"), "error_tests": f.get("error_tests")},
          open("/logs/verifier/reward_detail.json", "w"))
PY
exit 0
""", encoding="utf-8")

(out / "solution").mkdir()
(out / "solution" / "solve.sh").write_text("#!/bin/bash\necho 'no reference solution ships with Zero2Repo'\n", encoding="utf-8")
(out / "task.toml").write_text(f'''schema_version = "1.4"
artifacts = []

[task]
name = "sdd-compiler/zero2repo-{case}-markdown"
version = "0.0.1"
description = "Zero2Repo {case}, Markdown specification, our conditions"
authors = []
keywords = []

[metadata]

[verifier]
timeout_sec = 1800.0
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
print(f"wrote {out} | {case} | spec files {public} | words {sum(len((env / 'spec' / n).read_text(encoding='utf-8').split()) for n in public)}")
