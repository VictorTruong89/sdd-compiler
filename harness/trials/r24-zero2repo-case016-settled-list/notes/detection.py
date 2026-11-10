# Round 24: copied from round 23 (from round 21), run ids start with r24-, and 8 runs.
"""Build notes/detection.tsv from the reader's per-run readings (notes/readings.txt) and the probes
(notes/scores.json). No model call.

notes/readings.txt holds one line per run, written by the one reader (Claude Code) after reading the
run's whole NOTES.md, under TRIAL.md's strict rules: the conflicts *named* and the gaps *flagged*, and
remarks (borderline readings are named there and counted as not named / not flagged).

    python3 notes/detection.py      -> notes/detection.tsv, summary on stdout
"""
import csv
import json
import sys
from pathlib import Path

T = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(T / "notes"))
from plant import KEPT_C, KEPT_G                                  # noqa: E402

scores = json.loads((T / "notes/scores.json").read_text())
rows = []
for line in (T / "notes/readings.txt").read_text().splitlines():
    if not line.strip() or line.startswith("#"):
        continue
    run, named, flagged, remark = [x.strip() for x in line.split("|")]
    run = "r24-" + run
    named, flagged = set(named.split()) - {"-"}, set(flagged.split()) - {"-"}
    assert run in scores, run
    assert named <= set(KEPT_C) and flagged <= set(KEPT_G), (run, named - set(KEPT_C), flagged - set(KEPT_G))
    built = scores[run]["built"]
    for i in KEPT_C:
        rows.append({"run": run, "item": i, "named": "yes" if i in named else "no",
                     "stated": "both" if i in named else "", "flagged": "",
                     "built": built[i], "note": remark if i in remark else ""})
    for i in KEPT_G:
        rows.append({"run": run, "item": i, "named": "", "stated": "", "flagged": "yes" if i in flagged else "no",
                     "built": built[i], "note": remark if i in remark else ""})
assert len({r["run"] for r in rows}) == 8, len({r["run"] for r in rows})
with open(T / "notes/detection.tsv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0]), delimiter="\t")
    w.writeheader()
    w.writerows(rows)
print(len(rows), "rows")
