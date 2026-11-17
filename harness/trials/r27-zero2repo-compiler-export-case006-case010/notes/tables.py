"""Round 27 (compiler export) against rounds 18/19 (Markdown, oracle export) and 25 (review list), per case and model.
No model call.     python3 notes/tables.py  -> prints, writes notes/tables.json
Named % split on the items the compiler export flags and the items it does not (round 21's comparison)."""
import csv
import json
from pathlib import Path

T = Path(__file__).resolve().parents[1]
TR = T.parent
R25 = TR / "r25-zero2repo-review-list-case006-case010"
CASES = {"case006": (TR / "r18-zero2repo-case006-notes-both-sides", 24, 445),
         "case010": (TR / "r19-zero2repo-case010-conflicts", 15, 173)}
UNFLAGGED = {"case006": set("C01 C03 C06 C12 C18 C20 C23 C25 C29".split()),
             "case010": set("C04 C05 C08 C13 C14 C17".split())}


def load(det, scores):
    out = {}
    for r in csv.DictReader(open(det), delimiter="\t"):
        if not r["item"].startswith("C"):
            continue
        d = out.setdefault(r["run"], {"named": set(), "B": set(), "items": set()})
        d["items"].add(r["item"])
        if r["named"] == "yes":
            d["named"].add(r["item"])
        if r["built"] == "B":
            d["B"].add(r["item"])
    sc = json.loads(Path(scores).read_text())
    out = {k: v for k, v in out.items() if k in sc}
    for run, d in out.items():
        d["core"] = sc[run].get("core_passed", sc[run].get("core"))
        d["cost"] = sc[run].get("cost_usd", sc[run].get("cost"))
    return out


def main():
    out = {}
    for case, (folder, n_items, core_n) in CASES.items():
        old = load(folder / "notes/detection.tsv", folder / "notes/scores.json")
        r25 = load(R25 / "notes/detection.tsv", R25 / f"score/{case}/notes/scores.json")
        r27 = load(T / "notes/detection.tsv", T / f"score/{case}/notes/scores.json")
        unf = UNFLAGGED[case]
        for model in ("haiku", "sonnet"):
            arms = {"markdown": {k: v for k, v in old.items() if f"-{model}-markdown" in k},
                    "compiler export": {k: v for k, v in r27.items() if f"-{model}-{case}" in k},
                    "oracle export": {k: v for k, v in old.items() if f"-{model}-export" in k},
                    "review list": {k: v for k, v in r25.items() if f"-{model}-{case}" in k}}
            for arm, rs in arms.items():
                n = len(rs)
                if not n:
                    continue
                named = [len(v["named"]) for v in rs.values()]
                nf = n_items - len(unf)
                row = {"runs": n, "named_per_run": named,
                       "named_pct": round(100 * sum(named) / (n_items * n), 1),
                       "flagged_pct": round(100 * sum(len(v["named"] - unf) for v in rs.values()) / (nf * n), 1),
                       "flagged": f"{sum(len(v['named'] - unf) for v in rs.values())} / {nf * n}",
                       "unflagged": f"{sum(len(v['named'] & unf) for v in rs.values())} / {len(unf) * n}",
                       "unflagged_pct": round(100 * sum(len(v["named"] & unf) for v in rs.values()) / (len(unf) * n), 1),
                       "side_b": f"{sum(len(v['B']) for v in rs.values())} / {n_items * n}",
                       "side_b_unnamed": sum(len(v["B"] - v["named"]) for v in rs.values()),
                       "core": [v["core"] for v in rs.values()],
                       "core_pct": round(100 * sum(v["core"] for v in rs.values()) / (core_n * n), 1),
                       "cost_mean": round(sum(v["cost"] for v in rs.values()) / n, 2)}
                out[f"{case}-{model}-{arm}"] = row
                print(f"{case} {model:6s} {arm:15s} n={n} named {row['named_pct']:5}% flagged {row['flagged']:8s} ({row['flagged_pct']}%) "
                      f"unflagged {row['unflagged']:7s} ({row['unflagged_pct']}%) B {row['side_b']:7s} B-unn {row['side_b_unnamed']:2d} "
                      f"core {row['core']} {row['core_pct']}% $ {row['cost_mean']}")
    json.dump(out, open(T / "notes/tables.json", "w"), indent=1)


if __name__ == "__main__":
    main()
