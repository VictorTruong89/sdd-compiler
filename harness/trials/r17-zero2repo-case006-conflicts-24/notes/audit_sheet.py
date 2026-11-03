"""Build notes/detection_audit.md for round 17: for each planted item and run, the lines of the run's
NOTES.md that touch the item, beside the assistant's reading (notes/detection.tsv), with a blank column
for the owner's verdict. No model call. Not blind to format: the export runs' notes cite conflict ids.
Same layout as round 15's sheet (../r15-zero2repo-case006-conflicts-v2/notes/audit_sheet.py); the
keywords are notes/score.py's triage keywords, and for export runs the item's CF ids are matched too.

    python3 notes/audit_sheet.py
"""
import csv
import json
import re
import sys
from pathlib import Path

T = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(T / "notes"))
from score import KEYWORDS                                        # noqa: E402

# Answer-key line per item: side A / side B (ANSWER_KEY.md, "Kept items").
WHAT = {}
for line in (T / "ANSWER_KEY.md").read_text().splitlines():
    m = re.match(r"\| (C\d\d) \| [^|]+ \| (.+?) \| (.+?) \| `", line)
    if m:
        WHAT[m[1]] = f"A: {m[2]} · B: {m[3]}"
# CF ids per item in the oracle export: the compiler's (work/recall-full.json) and the injected ones.
CF = {i: [c["id"] for c in v["conflicts"] if c["kind"] == "contradiction"]
      for i, v in json.loads((T / "work/recall-full.json").read_text())["items"].items()}
for item, cf, *_ in json.loads((T / "work/compile-oracle/oracle.json").read_text())["injected"]:
    CF[item].append(cf)
STOPPED = "r17-haiku-markdown-2"  # stopped after 15 turns; partial build, no planted item in its notes
reading = {(r["run"], r["item"]): r for r in csv.DictReader(open(T / "notes/detection.tsv"), delimiter="\t")}
runs = sorted({r for r, _ in reading}, key=lambda r: ("export" in r, r))
out = ["# Detection audit (round 17) — for the owner", "",
       "One table per planted item. **Lines** are every line of the run's `NOTES.md` that matches the",
       "item's keywords (or, in export runs, one of its conflict ids), cut at 300 characters. **Reading**",
       "is the assistant's (`detection.tsv`): named · stated sides · side the probe found in the code.",
       "**Named** needs both sides' content stated as disagreeing (TRIAL.md, \"Detection rule\"); a CF id",
       "with a topic only is not enough. Fill **Owner** with `agree` or your reading. A line about",
       f"something else that happens to match the keywords is not a detection. `{STOPPED}` stopped early",
       "(partial build) and is left out, as round 15's stopped run was.", ""]
for item in WHAT:
    ids = [c.removeprefix("CF-").lstrip("0") for c in CF[item]]
    id_pattern = r"CF-0*(" + "|".join(ids) + r")\b|\b0*(" + "|".join(ids) + r")\b" if ids else r"$^"
    out += [f"## {item} — {WHAT[item]}", "", f"Conflict ids in the export: {', '.join(CF[item])}", "",
            "| Run | Lines from NOTES.md | Reading | Owner |", "|---|---|---|---|"]
    for run in runs:
        if run == STOPPED:
            continue
        r = reading[(run, item)]
        text = (T / "runs" / run / "NOTES.md").read_text(errors="replace")
        hits = [ln.strip()[:300] for ln in text.splitlines()
                if re.search(KEYWORDS[item], ln, re.I) or ("export" in run and re.search(id_pattern, ln))]
        cell = "<br>".join(h.replace("|", "\\|") for h in hits) or "*(none)*"
        out.append(f"| {run} | {cell} | {r['named']} · {r['stated']} · {r['built']} | |")
    out.append("")
(T / "notes/detection_audit.md").write_text("\n".join(out) + "\n")
print("wrote", T / "notes/detection_audit.md", len(out), "lines")
