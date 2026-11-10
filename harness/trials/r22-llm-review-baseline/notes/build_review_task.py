"""Round 22: build the three review-only Harbor tasks (no code is written, no hidden tests run).

    python3 notes/build_review_task.py            (from the trial folder)

Each task's `spec/` is copied from the Markdown arm of the round whose answer key it is scored against,
so the reviewer reads exactly the planted text the coding agents read:

    case006 ← r18 work/tasks/case006-planted24-markdown   (answer key: r18 ANSWER_KEY.md, 24 conflicts)
    case010 ← r19 work/tasks/case010-planted15-markdown   (answer key: r19 ANSWER_KEY.md, 15 conflicts)
    case016 ← r21 work/tasks/case016-r21-markdown         (answer key: r21 ANSWER_KEY.md, 17 conflicts;
                                                           its 16 removed facts are not scored here)

The Dockerfile is the same as those arms' (same image, so the agent's environment is unchanged). The
verifier only saves `/app/CONFLICTS.md` and writes reward 0: scoring is done afterwards by reading.
"""
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
TRIAL = HERE.parent
TRIALS = TRIAL.parent
SOURCES = {
    "case006": TRIALS / "r18-zero2repo-case006-notes-both-sides/work/tasks/case006-planted24-markdown",
    "case010": TRIALS / "r19-zero2repo-case010-conflicts/work/tasks/case010-planted15-markdown",
    "case016": TRIALS / "r21-zero2repo-case016-conflicts-gaps/work/tasks/case016-r21-markdown",
}

INSTRUCTION = """# Task

Review the specification in `spec/`: {files}. Do not write any code.

Find every place where two parts of the specification disagree: two statements that cannot both hold
for the same case. Write them to `CONFLICTS.md` in the current directory (`/app`), one entry per
disagreement: quote or state what each side says and where it is (file and section), then say in one
sentence why they cannot both hold. A conflict id or topic alone is not enough.

- List only disagreements inside the specification. Do not list missing information, unclear wording
  or style.
- Keep `spec/` as it is. Do not use the network to look up an existing implementation of this project.
"""

TEST_SH = """#!/bin/bash
# Round 22 review task: keep the reviewer's CONFLICTS.md; there are no hidden tests to run.
set -u
mkdir -p /logs/verifier
if [ -f /app/CONFLICTS.md ]; then cp /app/CONFLICTS.md /logs/verifier/CONFLICTS.md; found=1; else found=0; fi
printf '{"reward": %s}' "$found" > /logs/verifier/reward.json
exit 0
"""

TASK_TOML = """schema_version = "1.4"
artifacts = []

[task]
name = "sdd-compiler/r22-review-{case}"
version = "0.0.1"
description = "Round 22: list the contradictions in Zero2Repo {case}'s planted Markdown (review only)"
authors = []
keywords = []

[metadata]

[verifier]
timeout_sec = 300.0
collect = []
network_mode = "public"

[verifier.env]

[agent]
timeout_sec = 3600.0
network_mode = "allowlist"
allowed_hosts = ["api.anthropic.com"]

[environment]
network_mode = "public"
build_timeout_sec = 900.0
os = "linux"
mcp_servers = []

[environment.env]

[solution.env]
"""


def main() -> None:
    for case, src in SOURCES.items():
        out = TRIAL / "work" / "tasks" / f"review-{case}"
        if out.exists():
            shutil.rmtree(out)
        (out / "environment").mkdir(parents=True)
        shutil.copytree(src / "environment" / "spec", out / "environment" / "spec")
        shutil.copy(src / "environment" / "Dockerfile", out / "environment" / "Dockerfile")
        files = sorted(p.name for p in (out / "environment" / "spec").iterdir())
        (out / "instruction.md").write_text(
            INSTRUCTION.format(files=", ".join(f"`spec/{n}`" for n in files)), encoding="utf-8")
        (out / "tests").mkdir()
        (out / "tests" / "test.sh").write_text(TEST_SH, encoding="utf-8")
        (out / "tests" / "test.sh").chmod(0o755)
        (out / "solution").mkdir()
        (out / "solution" / "solve.sh").write_text("#!/bin/bash\necho 'review task: no reference solution'\n")
        (out / "solution" / "solve.sh").chmod(0o755)
        (out / "task.toml").write_text(TASK_TOML.format(case=case), encoding="utf-8")
        print(f"built {out.relative_to(TRIAL)}: {', '.join(files)}")


if __name__ == "__main__":
    main()
