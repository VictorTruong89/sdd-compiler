"""Make a Harbor task from any Zero2Repo case, Markdown or spec-graph export, under our conditions.

Round 19 (copied from ../../r18-zero2repo-case006-notes-both-sides/notes/build_task.py), one change:
  - model files for the verifier only. A case with `source/env/resources.json` (of the Python cases,
    only case010) needs pinned files in `/opt/models` when its hidden tests run (round 13c: 20 of
    case010's 197 tests stop with "host resource is missing" without them). The builder copies the
    manifest and the archives, downloaded once and checked into `RESOURCES_DIR` (default: the trial's
    git-ignored `work/resources/<id>.zip`), into the task's `tests/resources/`, and `test.sh` unpacks
    them into the manifest's destination before the judge runs (`tests/install_resources.py`: the
    size and sha256 check and the zip extraction of Zero2Repo's `cbrun/fetch_resources.py`, without
    the download). Zero2Repo's env recipe (`source/recipe.lock.json`, `runner.install_command`,
    `_cb_boot`) also writes a site-packages hook that puts `/opt/models` first on any `<pkg>.data`
    module's `path`; its script is decoded verbatim from the recipe into `tests/resources/cb_boot.py`
    and run in the verifier phase too (`MODELS_HOOK=0` leaves it out). Harbor uploads `tests/` to the container only in the verifier phase, after the
    agent has finished (harbor/verifier/verifier.py, `verify`), as it does for the hidden tests, so
    the agent's container, image and instruction are unchanged. `RESOURCES_DIR=none` builds the task
    without them (for the `diff -r` check). The builder stops if a declared file is missing or
    differs from the manifest.

    python3 build_task.py case010 ../work/tasks/case010-markdown
    python3 build_task.py case010 ../work/tasks/case010-export ../work/compile-case010/export

Round 14 (copied from ../../r13d-zero2repo-case006-lean-export/notes/build_task.py), two changes:
  - env SPEC_DIR=<folder>: the Markdown comes from that folder (the planted spec, and in the settled
    round `DECISIONS.md` beside it) instead of the case's public/ folder;
  - one instruction line for both formats, the owner's choice (rel02 S17): disagreements are listed in
    `NOTES.md`.

Copied from ../../r13b-zero2repo-haiku-sweep/notes/build_task.py; the export mode added as in
../../r13-zero2repo-case004/notes/build_task.py (spec/ holds the export; one sentence differs).

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
export = Path(sys.argv[3]).resolve() if len(sys.argv) > 3 else None
fmt = "export" if export else "markdown"
CASE, ADAPTER = Z / "cases" / case, Z / "output" / case
assert CASE.is_dir() and ADAPTER.is_dir(), (CASE, ADAPTER)
if out.exists():
    shutil.rmtree(out)
env = out / "environment"
env.mkdir(parents=True)
import os
SRC = Path(os.environ["SPEC_DIR"]).resolve() if os.environ.get("SPEC_DIR") else CASE / "public"
public = sorted(p.name for p in SRC.iterdir() if p.is_file())
if export:
    shutil.copytree(export, env / "spec")
    spec_line = ("The specification is the compiled export in `spec/`. Start with `spec/MAP.md`; "
                 "account for every id in `spec/CHECKLIST.md`.")
else:
    (env / "spec").mkdir()
    for name in public:
        shutil.copy(SRC / name, env / "spec" / name)
    spec_line = "The specification is the Markdown files in `spec/`: " + ", ".join(f"`spec/{n}`" for n in public) + "."

adapter_text = (ADAPTER / "instruction.md").read_text(encoding="utf-8")
contract = re.search(r"## Build contract\n\n(.*?)\n\n", adapter_text, re.S).group(1)
(out / "instruction.md").write_text(f"""# Task

Build the project described by the specification, from scratch, in the current directory (`/app`).
{spec_line}

## Build contract

{contract}

- Keep `spec/` as it is. Put the code where the specification says.
- If parts of the specification disagree, choose one and list each disagreement in `NOTES.md`:
  quote or state what each side says and where it is, then what you built. A conflict id or topic
  alone is not enough.
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
if [ -f /tests/resources/resources.json ]; then
  python3 /tests/install_resources.py /tests/resources > /logs/verifier/install_resources.log 2>&1 \
    || echo "install_resources failed (see install_resources.log)" >&2
  [ -f /tests/resources/cb_boot.py ] && python3 /tests/resources/cb_boot.py >> /logs/verifier/install_resources.log 2>&1
fi
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
name = "sdd-compiler/zero2repo-{case}-{fmt}"
version = "0.0.1"
description = "Zero2Repo {case}, specification in {fmt} format, our conditions"
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
# Round 19: model files for the verifier phase only (docstring).
MANIFEST = CASE / "source" / "env" / "resources.json"
RES = os.environ.get("RESOURCES_DIR") or str(HERE.parent / "work" / "resources")
if MANIFEST.is_file() and RES != "none":
    import hashlib
    man = json.loads(MANIFEST.read_text(encoding="utf-8"))
    dst = out / "tests" / "resources"
    dst.mkdir()
    shutil.copy(MANIFEST, dst / "resources.json")
    for it in man["resources"]:
        src = Path(RES) / f"{it['id']}.zip"
        data = src.read_bytes()
        if len(data) != it["size"] or hashlib.sha256(data).hexdigest() != it["sha256"]:
            sys.exit(f"resource {it['id']}: size or sha256 differs from {MANIFEST}")
        shutil.copy(src, dst / src.name)
    (out / "tests" / "install_resources.py").write_text('''"""Install the case's pinned resources from /tests/resources (verifier phase only; no network).
Size and sha256 check and zip extraction as Zero2Repo's cbrun/fetch_resources.py."""
import hashlib, json, shutil, stat, sys, zipfile
from pathlib import Path
src = Path(sys.argv[1])
man = json.loads((src / "resources.json").read_text(encoding="utf-8"))
dest = Path(man["destination"]); dest.mkdir(parents=True, exist_ok=True)
for it in man["resources"]:
    archive = src / f"{it['id']}.zip"
    data = archive.read_bytes()
    if len(data) != it["size"] or hashlib.sha256(data).hexdigest() != it["sha256"]:
        raise SystemExit(f"resource checksum/size mismatch: {it['id']}")
    target = (dest / it["directory"]).resolve()
    if not target.is_relative_to(dest.resolve()):
        raise SystemExit("resource directory escapes destination")
    target.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive) as bundle:
        members = bundle.infolist()
        if sum(m.file_size for m in members) > int(it.get("unpacked_size") or it["size"]):
            raise SystemExit("archive exceeds declared unpacked size")
        for m in members:
            t = (target / m.filename).resolve()
            if not t.is_relative_to(target) or stat.S_ISLNK(m.external_attr >> 16):
                raise SystemExit("unsafe archive member")
        bundle.extractall(target)
    print(f"installed verified resource: {it['id']}", flush=True)
shutil.copyfile(src / "resources.json", dest / "resources.json")
''', encoding="utf-8")
    if os.environ.get("MODELS_HOOK", "1") != "0":
        import base64
        cmd = json.loads((CASE / "source" / "recipe.lock.json").read_text(encoding="utf-8"))["runner"]["install_command"]
        boots = re.findall(r"b64decode\('([A-Za-z0-9+/=]+)'\)", cmd)
        assert len(boots) == 1, "expected one _cb_boot script in the recipe"
        (dst / "cb_boot.py").write_text(base64.b64decode(boots[0]).decode(), encoding="utf-8")
    print(f"model files for the verifier: {len(man['resources'])} from {RES}; hook {os.environ.get('MODELS_HOOK', '1') != '0'}")

words = sum(len(p.read_text(encoding="utf-8").split()) for p in (env / "spec").rglob("*.md"))
print(f"wrote {out} | {case} | {fmt} | spec words (.md) {words}")
