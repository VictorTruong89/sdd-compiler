"""Triage for the reader (no model call): split each review's CONFLICTS.md into entries and show, per entry,
which planted conflicts have BOTH sides' phrases (or their distinctive words) in it. The reading recorded
in notes/readings.md is the reader's, not this script's.

    python3 notes/triage.py <case> [run ...]
"""
import re
import sys
from pathlib import Path

T = Path(__file__).resolve().parents[1]
case = sys.argv[1]
sys.path.insert(0, str(T.parent / f"r28-zero2repo-{case}-conflicts-gaps/notes"))
from plant import KEPT_C, PHRASES  # noqa: E402

STOP = set("the a an of to in is are be and or it its that this with for as by on at not no any one".split())


def words(s):
    return {w for w in re.findall(r"[a-z0-9_`\-]+", s.lower()) if w not in STOP and len(w) > 2}


runs = sys.argv[2:] or sorted(p.name for p in (T / "runs").glob(f"r28-*-review-{case}-*"))
for run in runs:
    text = (T / "runs" / run / "CONFLICTS.md").read_text(errors="replace")
    parts = re.split(r"(?m)^(?=#{2,3} |\d+\. \*\*|\*\*\d+)", text)
    entries = [p for p in parts if p.strip() and not p.startswith("# ")]
    print(f"=== {run}: {len(entries)} entries")
    for n, e in enumerate(entries, 1):
        hits = []
        for i in KEPT_C:
            a, b = (words(x) for x in PHRASES[i])
            ew = words(e)
            fa, fb = len(a & ew) / max(len(a), 1), len(b & ew) / max(len(b), 1)
            if fa >= 0.6 and fb >= 0.6:
                hits.append(f"{i}({fa:.1f},{fb:.1f})")
        title = e.strip().split("\n")[0][:90]
        print(f"  {n:2d}. {title}  -> {' '.join(hits) or '-'}")
