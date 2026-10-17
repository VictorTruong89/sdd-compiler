"""Build notes/detection_audit.md: for each planted item and run, the lines of the run's NOTES.md
that touch the item, beside the assistant's reading (notes/detection.tsv), with a blank column for
the owner's verdict. No model call. Not blind to format: the export runs' notes cite conflict ids.

    python3 notes/audit_sheet.py
"""
import csv
import re
from pathlib import Path

T = Path(__file__).resolve().parents[1]
WHAT = {
    "P1": ("isolated filesystem: removed on exit (A) / always left in place (B)", r"isolated|left in place|temp_dir"),
    "P2": ("deprecated command's warning: stderr (A) / stdout (B)", r"deprecat"),
    "P3": ("environment beats default map (A) / default map beats environment (B)", r"default[_ ]map|value order|precedence"),
    "P4": ("callback for an omitted parameter: runs (A) / not called (B)", r"callback"),
    "P6": ("max content width: 80 (A) / 100 (B)", r"\b80\b|\b100\b|content width|wrap width"),
    "P7": ("integer option metavar: INTEGER (A) / COUNT (B)", r"metavar|--count|\bCOUNT\b"),
    "R1": ("confirm, other answer: asks again (A) / counts as no (B)", r"confirm"),
}
rows = list(csv.DictReader(open(T / "notes/detection.tsv"), delimiter="\t"))
runs = sorted({r["run"] for r in rows}, key=lambda r: (r[:2], "export" in r, r))
reading = {(r["run"], r["item"]): r for r in rows}
out = ["# Detection audit (round 14) — for the owner", "",
       "One table per planted item. **Lines** are every line of the run's `runs/<run>/NOTES.md` that",
       "matches the item's keywords (cut at 300 characters); **Reading** is the assistant's",
       "(`notes/detection.tsv`: noticed · stated side · side the probe found in the code). Fill",
       "**Owner** with `agree` or your reading. A line about something else that happens to match the",
       "keywords is not a detection. `r2-haiku-markdown-3` stopped early and is left out.", ""]
for item, (what, pattern) in WHAT.items():
    out += [f"## {item} — {what}", "", "| Run | Lines from NOTES.md | Reading | Owner |", "|---|---|---|---|"]
    for run in runs:
        r = reading[(run, item)]
        text = (T / "runs" / run / "NOTES.md").read_text(errors="replace")
        hits = [ln.strip()[:300] for ln in text.splitlines() if re.search(pattern, ln, re.I)]
        cell = "<br>".join(h.replace("|", "\\|") for h in hits) or "*(none)*"
        out.append(f"| {run} | {cell} | {r['noticed']} · {r['stated']} · {r['built']} | |")
    out.append("")
(T / "notes/detection_audit.md").write_text("\n".join(out) + "\n")
print("wrote", T / "notes/detection_audit.md", len(out), "lines")
