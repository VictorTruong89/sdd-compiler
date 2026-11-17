"""Round 28 case001 tables (copied from round 21; four arms incl. the review list; run ids r28-case001-<model>-<arm>-<i>).

Round 21 tables from notes/scores.json and notes/detection.tsv. No model call. Descriptive only.

    python3 notes/tables.py        -> notes/tables.json, tables on stdout

Flagged in each arm (step 3 and the review list): compiler = the 11 found + C29 (CF-000023); oracle = all 15; review list = all but C16.
Set 2b counts every kept gap.
"""
import csv
import json
import statistics as st
import sys
from collections import defaultdict
from pathlib import Path

T = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(T / "notes"))
from plant import KEPT_C, KEPT_G                                   # noqa: E402
STATED_G = set()

FLAGGED = {"markdown": set(),
           "compiler": {"C03", "C04", "C07", "C08", "C10", "C11", "C12", "C13", "C16", "C18", "C29", "C36"},
           "oracle": set(KEPT_C),
           "review": set(KEPT_C) - {"C16"}}
GAPS = [g for g in KEPT_G if g not in STATED_G]
scores = json.loads((T / "notes/scores.json").read_text())
det = defaultdict(dict)
for r in csv.DictReader(open(T / "notes/detection.tsv"), delimiter="\t"):
    det[r["run"]][r["item"]] = r
per_run = {}
for run, s in sorted(scores.items()):
    arm = run.split("-")[3]
    d = det[run]
    fl = FLAGGED[arm]
    named = {i for i in KEPT_C if d[i]["named"] == "yes"}
    gflag = {g for g in GAPS if d[g]["flagged"] == "yes"}
    built = {g: d[g]["built"] for g in GAPS}
    silent = {g for g in GAPS if g not in gflag and built[g] in ("upstream", "alternative")}
    per_run[run] = {"model": run.split("-")[2], "arm": arm, "tests": s["tests"], "core": s["core"], "turns": s["turns"],
                    "cost": s["cost"], "named": len(named), "named_flagged": len(named & fl), "n_flagged": len(fl),
                    "named_unflagged": len(named - fl), "n_unflagged": len(set(KEPT_C) - fl),
                    "gaps_flagged": len(gflag), "gaps_silent": len(silent),
                    "gaps_not_built": sum(1 for g in GAPS if built[g] not in ("upstream", "alternative")),
                    "gaps_alternative": sum(1 for g in GAPS if built[g] == "alternative"),
                    "flagged_ids": sorted(gflag)}
groups = defaultdict(list)
for run, r in per_run.items():
    groups[(r["model"], r["arm"])].append(r)
out = {"per_run": per_run, "groups": {}}
print(f"{'model':7}{'arm':10}{'n':>2} {'core':>22} {'mean':>6} {'named':>18} {'nmd|flag':>10} {'nmd|unfl':>10} {'silent':>16} {'flag':>12} {'alt':>12} {'$':>6}")
for (m, a), rs in sorted(groups.items(), key=lambda x: (x[0][0], ["markdown", "compiler", "oracle", "review"].index(x[0][1]))):
    g = {"n": len(rs), "core": [r["core"] for r in rs], "core_mean": round(st.mean(r["core"] for r in rs), 1),
         "named": [r["named"] for r in rs], "named_mean": round(st.mean(r["named"] for r in rs), 2),
         "named_flagged": f"{sum(r['named_flagged'] for r in rs)}/{sum(r['n_flagged'] for r in rs)}",
         "named_unflagged": f"{sum(r['named_unflagged'] for r in rs)}/{sum(r['n_unflagged'] for r in rs)}",
         "silent": [r["gaps_silent"] for r in rs], "silent_mean": round(st.mean(r["gaps_silent"] for r in rs), 2),
         "flagged": [r["gaps_flagged"] for r in rs], "alternative": [r["gaps_alternative"] for r in rs],
         "not_built": sum(r["gaps_not_built"] for r in rs), "cost": round(sum(r["cost"] for r in rs), 2)}
    out["groups"][f"{m} {a}"] = g
    print(f"{m:7}{a:10}{g['n']:>2} {str(g['core']):>22} {g['core_mean']:>6} {str(g['named']):>18} {g['named_flagged']:>10} {g['named_unflagged']:>10} {str(g['silent']):>16} {str(g['flagged']):>12} {str(g['alternative']):>12} {g['cost']:>6}")
# per item
items = {}
for i in KEPT_C:
    items[i] = {a: sum(1 for r, d in det.items() if r.split("-")[3] == a and d[i]["named"] == "yes") for a in FLAGGED}
for g in KEPT_G:
    items[g] = {a: sum(1 for r, d in det.items() if r.split("-")[3] == a and d[g]["flagged"] == "yes") for a in FLAGGED}
    items[g]["alternative"] = sum(1 for d in det.values() if d[g]["built"] == "alternative")
    items[g]["not_built"] = sum(1 for d in det.values() if d[g]["built"] not in ("upstream", "alternative"))
out["items"] = items
print("\nper item (runs out of 8 per arm): named / flagged by arm; gaps also: built alternative, not built (of 32)")
for i, v in items.items():
    print(i, v)
(T / "notes/tables.json").write_text(json.dumps(out, indent=1) + "\n")
