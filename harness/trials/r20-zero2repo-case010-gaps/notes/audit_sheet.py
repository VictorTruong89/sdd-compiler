"""Build notes/detection_audit.md for round 20: for each kept gap and run, the lines of the run's NOTES.md
that touch the gap, beside the assistant's reading (notes/detection.tsv), with a blank column for the
owner's verdict. No model call.

Round 20: round 19's sheet (../r19-zero2repo-case010-conflicts/notes/audit_sheet.py) adapted to gaps:
the item line is the removed fact (ANSWER_KEY.md), the reading is flagged · built, and no conflict ids
are matched (no gap is flagged in either format). Not blind to format.

    python3 notes/audit_sheet.py
"""
import csv
import re
import sys
from pathlib import Path

T = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(T / "notes"))
from remove import KEPT                                           # noqa: E402
from score import KEYWORDS                                        # noqa: E402

# Answer-key line per gap: removed fact / upstream / alternative (ANSWER_KEY.md, "Kept gaps").
WHAT = {}
for line in (T / "ANSWER_KEY.md").read_text().splitlines():
    m = re.match(r"\| (G\d\d) \| ([^|]+) \| [^|]+ \| ([^|]+) \| ([^|]+) \|", line)
    if m:
        WHAT[m[1]] = f"{m[2].strip()} · upstream: {m[3].strip()} · alternative: {m[4].strip()}"
reading = {(r["run"], r["item"]): r for r in csv.DictReader(open(T / "notes/detection.tsv"), delimiter="\t")}
runs = sorted({r for r, _ in reading}, key=lambda r: ("export" in r, r))
out = ["# Gap reading audit (round 20) — for the owner", "",
       "One table per kept gap. **Lines** are every line of the run's `NOTES.md` that matches the gap's",
       "keywords, cut at 300 characters, with their line numbers. **Reading** is the assistant's",
       "(`detection.tsv`): flagged · built (probe) · note. **Flagged** needs the notes to name *this* point",
       "as not stated in the specification, in words, and give the value assumed (TRIAL.md, \"Strict",
       "rule\"). Fill **Owner** with `agree` or your reading. A line about something else that happens to",
       "match the keywords is not a flag.", ""]
for item in KEPT:
    out += [f"## {item} — {WHAT.get(item, '')}", "", "| Run | Lines from NOTES.md | Reading | Owner |", "|---|---|---|---|"]
    for run in runs:
        r = reading.get((run, item))
        if r is None:
            continue
        p = T / "runs" / run / "NOTES.md"
        text = p.read_text(errors="replace") if p.exists() else ""
        hits = [f"{n}: {ln.strip()[:300]}" for n, ln in enumerate(text.splitlines(), 1) if re.search(KEYWORDS[item], ln, re.I)]
        cell = "<br>".join(h.replace("|", "\\|") for h in hits) or "*(none)*"
        out.append(f"| {run} | {cell} | {r['flagged']} · {r['built']} · {r['note'].replace('|', '/')} | |")
    out.append("")
(T / "notes/detection_audit.md").write_text("\n".join(out) + "\n")
print("wrote", T / "notes/detection_audit.md", len(out), "lines")
