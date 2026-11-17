"""Build round 28's review-list task for case001 (rule of rounds 23 and 25). No model call.

    python3 notes/review_list_task.py        (from the trial folder)

A copy of the Markdown task (work/tasks/case001-r28-markdown) plus spec/CONFLICTS.md, which is the first Haiku
review of this case (../r28-zero2repo-reviews/runs/r28-haiku-review-case001-1/CONFLICTS.md), verbatim and
unfiltered; the instruction gets round 23's one sentence after the spec line; task.toml's name and
description change. Nothing else differs (checked with diff -r). Fails loud if the review is missing.
"""
import shutil
from pathlib import Path

T = Path(__file__).resolve().parents[1]
SRC = T / "work/tasks/case001-r28-markdown"
OUT = T / "work/tasks/case001-r28-review-list"
LIST = T.parent / "r28-zero2repo-reviews/runs/r28-haiku-review-case001-1/CONFLICTS.md"
SENTENCE = " `spec/CONFLICTS.md` is a reviewer's list of places where those files disagree; it is not part of the specification."

assert LIST.is_file(), f"review list missing: {LIST}"
if OUT.exists():
    shutil.rmtree(OUT)
shutil.copytree(SRC, OUT)
shutil.copy(LIST, OUT / "environment/spec/CONFLICTS.md")
ins = (OUT / "instruction.md").read_text()
line = next(l for l in ins.split("\n") if l.startswith("The specification is the Markdown files in `spec/`"))
assert ins.count(line) == 1
(OUT / "instruction.md").write_text(ins.replace(line, line + SENTENCE))
toml = (OUT / "task.toml").read_text()
assert toml.count("-markdown\"") == 1, "task name"
toml = toml.replace("-markdown\"", "-review-list\"").replace("specification in markdown format,", "specification in markdown format plus a review conflict list,")
(OUT / "task.toml").write_text(toml)
print("built", OUT.relative_to(T))
