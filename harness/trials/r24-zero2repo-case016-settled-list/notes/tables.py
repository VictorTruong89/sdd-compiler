"""Round 24 (settled list) against round 23 (unruled list) and round 21's arms on case016. No model call.

    python3 notes/tables.py        -> prints the tables, writes notes/tables.json

Rulings (TRIAL.md): side B ruled for RULED_B, side A for RULED_A; C11, C12 not in RULINGS.md.
"Ruling built" = the probe reads the ruled side (B -> "alternative", A -> "upstream").
"""
import csv
import json
from pathlib import Path

T = Path(__file__).resolve().parents[1]
R23 = T.parent / "r23-zero2repo-case016-review-list"
R21 = T.parent / "r21-zero2repo-case016-conflicts-gaps"
RULED_B = "C06 C25 C16 C21 C08 C18 C23".split()
RULED_A = "C09 C01 C15 C13 C20 C17 C19 C22".split()
GAPS = "G02 G03 G04 G05 G06 G07 G08 G09 G10 G11 G12 G13 G21 G30 G33".split()


def runs(folder):
    out = {}
    for r in csv.DictReader(open(folder / "notes/detection.tsv"), delimiter="\t"):
        d = out.setdefault(r["run"], {"named": set(), "flagged": set(), "built": {}})
        if r["item"].startswith("C") and r["named"] == "yes":
            d["named"].add(r["item"])
        if r["item"].startswith("G") and r["flagged"] == "yes":
            d["flagged"].add(r["item"])
        d["built"][r["item"]] = r["built"]
    sc = json.loads((folder / "notes/scores.json").read_text())
    for run, d in out.items():
        d["core"] = sc[run].get("core_passed", sc[run].get("core"))
        d["cost"] = sc[run].get("cost_usd", sc[run].get("cost"))
    return out


def summary(rs, model):
    rs = {k: v for k, v in rs.items() if f"-{model}-" in k}
    n = len(rs)
    if not n:
        return None
    b = sum(v["built"][i] == "alternative" for v in rs.values() for i in RULED_B)
    a = sum(v["built"][i] == "upstream" for v in rs.values() for i in RULED_A)
    g01 = sum(v["built"].get("G01") == "alternative" for v in rs.values())
    silent = [sum(1 for g in GAPS if g not in v["flagged"] and v["built"].get(g) in ("upstream", "alternative")) for v in rs.values()]
    core = [v["core"] for v in rs.values()]
    cost = [v["cost"] for v in rs.values()]
    named = [len(v["named"]) for v in rs.values()]
    return {"runs": n, "B_ruled_built": f"{b} / {7 * n}", "A_ruled_built": f"{a} / {8 * n}",
            "all_ruled_built": f"{a + b} / {15 * n}", "G01_one_hit": f"{g01} / {n}", "named": named,
            "silent_mean": round(sum(silent) / n, 1), "core": core, "core_mean": round(sum(core) / n, 1),
            "cost_mean": round(sum(cost) / n, 2), "per_run_ruled": {k: sum(v["built"][i] == "alternative" for i in RULED_B) + sum(v["built"][i] == "upstream" for i in RULED_A) for k, v in rs.items()}}


def main():
    out = {}
    for label, folder in (("r21", R21), ("r23", R23), ("r24", T)):
        rs = runs(folder)
        for model in ("haiku", "sonnet"):
            if label == "r21":
                for arm in ("markdown", "compiler", "oracle"):
                    s = summary({k: v for k, v in rs.items() if f"-{arm}-" in k}, model)
                    out[f"{label}-{arm}-{model}"] = s
            else:
                out[f"{label}-{model}"] = summary(rs, model)
    for k, s in out.items():
        if s:
            print(f"{k:24s} side-B rulings/planted side built {s['B_ruled_built']:8s} side-A {s['A_ruled_built']:8s} G01 one hit {s['G01_one_hit']:6s} "
                  f"silent {s['silent_mean']:4} core {s['core_mean']:6} $ {s['cost_mean']}")
    json.dump(out, open(T / "notes/tables.json", "w"), indent=1)


if __name__ == "__main__":
    main()
