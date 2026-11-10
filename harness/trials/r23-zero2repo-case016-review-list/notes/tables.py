"""Round 23 against round 21's three arms on case016: every number of TRIAL.md's results. No model call.

    python3 notes/tables.py        → prints the tables, writes notes/tables.json

Reads both rounds' notes/detection.tsv (named, flagged, built per run and item) and notes/scores.json
(tests, core, cost). Gaps scored: the 15 of round 21 (G01 reported apart, round 21 TRIAL.md step 3).
"""
import csv
import json
from pathlib import Path

T = Path(__file__).resolve().parents[1]
R21 = T.parent / "r21-zero2repo-case016-conflicts-gaps"
LISTED = "C01 C06 C08 C09 C13 C15 C16 C17 C18 C19 C20 C21 C22 C23 C25".split()   # in the review list
UNLISTED = ["C11", "C12"]
COMPILER_FLAGGED = "C06 C08 C09 C11 C13 C15 C16 C18 C21 C23".split()            # round 21's compiler export
GAPS = "G02 G03 G04 G05 G06 G07 G08 G09 G10 G11 G12 G13 G21 G30 G33".split()


def load(folder):
    rows = list(csv.DictReader(open(folder / "notes/detection.tsv"), delimiter="\t"))
    scores = json.loads((folder / "notes/scores.json").read_text())
    return rows, scores


def arm_of(run):
    parts = run.split("-")
    return parts[1], parts[2]          # model, arm


def main():
    data = {}
    for folder in (R21, T):
        rows, scores = load(folder)
        for r in rows:
            model, arm = arm_of(r["run"])
            d = data.setdefault((model, arm), {}).setdefault(r["run"], {"named": set(), "flagged": set(), "built": {}})
            if r["item"].startswith("C") and r["named"] == "yes":
                d["named"].add(r["item"])
            if r["item"].startswith("G") and r["flagged"] == "yes":
                d["flagged"].add(r["item"])
            d["built"][r["item"]] = r["built"]
        for run, s in scores.items():
            model, arm = arm_of(run)
            if (model, arm) in data and run in data[(model, arm)]:
                data[(model, arm)][run]["core"] = s.get("core_passed", s.get("core"))
                data[(model, arm)][run]["cost"] = s.get("cost_usd", s.get("cost"))
    out = {}
    print("| Model | Arm | Runs | Named / 17 per run | Named, all 17 | On the 15 listed | On C11, C12 | Side B built (conflicts) | Silent / 15, mean | Core / 338, mean | $ est., mean |")
    print("|---|---|---|---|---|---|---|---|---|---|---|")
    for model in ("haiku", "sonnet"):
        for arm in ("markdown", "compiler", "oracle", "review"):
            runs = data.get((model, arm), {})
            if not runs:
                continue
            n = len(runs)
            named = [len(v["named"]) for v in runs.values()]
            listed = sum(len(v["named"] & set(LISTED)) for v in runs.values())
            unl = sum(len(v["named"] & set(UNLISTED)) for v in runs.values())
            sideb = sum(sum(1 for i in v["built"] if i.startswith("C") and v["built"][i] == "alternative") for v in runs.values())
            silent = [sum(1 for g in GAPS if g not in v["flagged"] and v["built"].get(g) in ("upstream", "alternative"))
                      for v in runs.values()]
            core = [v.get("core") for v in runs.values()]
            cost = [v.get("cost") for v in runs.values()]
            core_vals = [c if isinstance(c, (int, float)) else (c[0] if isinstance(c, list) else None) for c in core]
            row = {"runs": n, "named": named, "named_pct": sum(named) / (17 * n), "listed_pct": listed / (15 * n),
                   "unlisted": f"{unl} / {2 * n}", "side_b": sideb, "silent_mean": sum(silent) / n,
                   "core": core_vals, "cost": cost}
            out[f"{model}-{arm}"] = row
            cm = [c for c in core_vals if c is not None]
            cs = [c for c in cost if c is not None]
            print(f"| {model} | {arm} | {n} | {' · '.join(map(str, named))} | {row['named_pct']:.1%} | "
                  f"{row['listed_pct']:.1%} | {row['unlisted']} | {sideb} / {17 * n} | {row['silent_mean']:.1f} | "
                  f"{sum(cm) / len(cm):.1f} | {sum(cs) / len(cs):.2f} |")
    json.dump(out, open(T / "notes/tables.json", "w"), indent=1)


if __name__ == "__main__":
    main()
