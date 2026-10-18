"""Plant the conflicts into a copy of case006's public spec. No model call.

    python3 notes/plant.py work/spec-planted P1 P2 P3 P4 P5 P6 R1

Copies Zero2Repo case006's `public/*.md` to the output folder and applies the side-B edit of each item
named. Each edit adds or changes text in **one** place, in the spec's own voice and with no marker,
so the other place still states side A (`ANSWER_KEY.md`). Every anchor must occur exactly once.
Zero2Repo has no licence file: the output stays in git-ignored `work/`; this script holds only the
short anchors and the planted sentences.
"""
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PUBLIC = HERE.parents[2] / "benchmarks/zero2repo/download/Zero2Repo/benchmark/cases/case006/public"
PRD, IC = "Full_PRD.md", "Interface_Contract.md"

# item: (file, anchor, replacement)
EDITS = {
    "P1": (PRD, "under that parent and is left in place.",
           "under that parent and is left in place. The new directory is always left in place after the "
           "block ends, so its files can still be inspected."),
    "P2": (PRD, "Optlyn emits a deprecation warning that is distinguishable",
           "Optlyn emits a deprecation warning on standard output, ahead of the command’s own output, "
           "that is distinguishable"),
    "P3": (IC, "a group’s map nests a `dict` under each child name |",
           "a group’s map nests a `dict` under each child name; its values take precedence over "
           "environment variables |"),
    "P4": (PRD, "Parameter callbacks receive the converted value and may replace it or refuse it. |",
           "Parameter callbacks receive the converted value and may replace it or refuse it. A parameter "
           "callback is not called for a parameter that was omitted and received no value from any "
           "source. |"),
    "P5": (PRD, "(including the prefix) turned into underscores.",
           "(including the prefix) turned into underscores. For example, with the prefix `TOOL`, the "
           "option `--user-name` of the subcommand `greet` under the top-level group `cli` is filled "
           "from `TOOL_CLI_GREET_USER_NAME`."),
    "P6": (PRD, "- Text wrapping accepts any string without failing.",
           "- Text wrapping accepts any string without failing. Help pages and wrapped text use a "
           "maximum content width of 100 columns unless the caller sets another."),
    "P7": (PRD, "unless that type supplies its own placeholder (a choice type does);",
           "unless that type supplies its own placeholder (a choice type does); for example, an integer "
           "option `--count` appears on the help page as `--count COUNT`;"),
    "R1": (IC, "| `confirm(text, default=False, abort=False, ...) -> bool` | |",
           "| `confirm(text, default=False, abort=False, ...) -> bool` | an answer other than yes, no or "
           "an empty line counts as no |"),
    "R2": (PRD, "| **Group** |",
           "| **Leaf** | A command without subcommands. Invoked with no arguments at all, a leaf shows its "
           "help page instead of running, as a group does. |\n| **Group** |"),
}

out, items = Path(sys.argv[1]), sys.argv[2:]
assert items and all(i in EDITS for i in items), items
if out.exists():
    shutil.rmtree(out)
out.mkdir(parents=True)
for f in PUBLIC.glob("*.md"):
    shutil.copy(f, out / f.name)
for item in items:
    name, old, new = EDITS[item]
    text = (out / name).read_text(encoding="utf-8")
    assert text.count(old) == 1, (item, text.count(old))
    (out / name).write_text(text.replace(old, new), encoding="utf-8")
    print(item, name, "planted")
print("words", sum(len(f.read_text(encoding="utf-8").split()) for f in out.glob("*.md")))
