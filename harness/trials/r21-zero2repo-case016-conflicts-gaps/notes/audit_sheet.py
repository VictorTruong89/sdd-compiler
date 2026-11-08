"""Build notes/detection_audit.md for round 21: for each kept item and run, the lines of the run's NOTES.md
that touch the item, beside the assistant's reading (notes/detection.tsv), with a blank column for the
owner's verdict. No model call.

Round 21: rounds 19 and 20's sheets in one. A conflict's heading gives side A and side B (ANSWER_KEY.md)
and its reading is named · stated · built; a gap's heading gives the removed fact, upstream and
alternative, and its reading is flagged · built. Not blind to format.

    python3 notes/audit_sheet.py
"""
import csv
import re
import sys
from pathlib import Path

T = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(T / "notes"))
from plant import KEPT_C, KEPT_G                                  # noqa: E402
from score import KEYWORDS                                        # noqa: E402

# Answer-key line per item: the first table cells after the id (ANSWER_KEY.md, "Kept conflicts" and "Kept gaps").
WHAT = {}
for line in (T / "ANSWER_KEY.md").read_text().splitlines():
    m = re.match(r"\| ([CG]\d\d) \| ([^|]+) \| ([^|]+) \| ([^|]+) \|", line)
    if m:
        WHAT[m[1]] = f"{m[2].strip()} · {m[3].strip()} · {m[4].strip()}"
reading = {(r["run"], r["item"]): r for r in csv.DictReader(open(T / "notes/detection.tsv"), delimiter="\t")}
runs = sorted({r for r, _ in reading}, key=lambda r: ("export" in r, "oracle" in r, r))
out = ["# Detection audit (round 21) — for the owner", "",
       "One table per kept item. **Lines** are every line of the run's `NOTES.md` that matches the item's",
       "keywords, cut at 300 characters, with their line numbers. **Reading** is the assistant's",
       "(`detection.tsv`). Conflicts (C..): named · sides stated · side built; *named* needs side A's",
       "content, side B's content, and the two presented as disagreeing. Gaps (G..): flagged · built;",
       "*flagged* needs the notes to say this point is not stated and give the value assumed (TRIAL.md,",
       "\"Strict rules\"). Fill **Owner** with `agree` or your reading. A line about something else that",
       "happens to match the keywords is not a reading.", ""]
for item in list(KEPT_C) + list(KEPT_G):
    out += [f"## {item} — {WHAT.get(item, '')}", "", "| Run | Lines from NOTES.md | Reading | Owner |", "|---|---|---|---|"]
    for run in runs:
        r = reading.get((run, item))
        if r is None:
            continue
        p = T / "runs" / run / "NOTES.md"
        text = p.read_text(errors="replace") if p.exists() else ""
        hits = [f"{n}: {ln.strip()[:300]}" for n, ln in enumerate(text.splitlines(), 1) if re.search(KEYWORDS[item], ln, re.I)]
        cell = "<br>".join(h.replace("|", "\\|") for h in hits[:12]) or "*(none)*"
        if len(hits) > 12:
            cell += f"<br>*(+{len(hits) - 12} more)*"
        key = "named" if item.startswith("C") else "flagged"
        extra = f" · {r.get('stated', '')}" if item.startswith("C") else ""
        out.append(f"| {run} | {cell} | {r[key]}{extra} · {r['built']} · {r['note'].replace('|', '/')} | |")
    out.append("")
(T / "notes/detection_audit.md").write_text("\n".join(out) + "\n")
print("wrote", T / "notes/detection_audit.md", len(out), "lines")
