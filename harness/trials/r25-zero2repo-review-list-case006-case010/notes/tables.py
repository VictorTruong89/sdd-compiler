"""Round 25 (review list) against round 18 (case006) and round 19 (case010): Markdown and oracle export.
No model call.     python3 notes/tables.py  -> prints, writes notes/tables.json
Reads each round's notes/detection.tsv (named, built A/B) and scores.json (core, cost)."""
import csv
import json
from pathlib import Path

T = Path(__file__).resolve().parents[1]
TR = T.parent
SRC = {"case006": (TR / "r18-zero2repo-case006-notes-both-sides", 24, {"C08", "C22"}, 445),
       "case010": (TR / "r19-zero2repo-case010-conflicts", 15, {"C21", "C22"}, 173)}


def load(det, scores):
    out = {}
    for r in csv.DictReader(open(det), delimiter="\t"):
        if not r["item"].startswith("C"):
            continue
        d = out.setdefault(r["run"], {"named": set(), "B": set()})
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
    r25 = {}
    for case in SRC:
        p = T / f"score/{case}/notes/scores.json"
        if p.exists():
            r25.update({k: v for k, v in load(T / "notes/detection.tsv", p).items() if case in k})
    for case, (folder, n_items, unl, core_n) in SRC.items():
        old = load(folder / "notes/detection.tsv", folder / "notes/scores.json")
        for model in ("haiku", "sonnet"):
            arms = {"markdown": {k: v for k, v in old.items() if f"-{model}-markdown" in k},
                    "oracle export": {k: v for k, v in old.items() if f"-{model}-export" in k},
                    "review list": {k: v for k, v in r25.items() if f"-{model}-{case}" in k}}
            for arm, rs in arms.items():
                n = len(rs)
                if not n:
                    continue
                listed = set(f"C{i:02d}" for i in range(1, 30)) - unl
                named = [len(v["named"]) for v in rs.values()]
                row = {"runs": n, "named_per_run": named, "named_pct": round(100 * sum(named) / (n_items * n), 1),
                       "listed_pct": round(100 * sum(len(v["named"] - unl) for v in rs.values()) / ((n_items - len(unl)) * n), 1),
                       "unlisted": f"{sum(len(v['named'] & unl) for v in rs.values())} / {len(unl) * n}",
                       "side_b": f"{sum(len(v['B']) for v in rs.values())} / {n_items * n}",
                       "side_b_unnamed": sum(len(v["B"] - v["named"]) for v in rs.values()),
                       "core": [v["core"] for v in rs.values()],
                       "core_pct": round(100 * sum(v["core"] for v in rs.values()) / (core_n * n), 1),
                       "cost_mean": round(sum(v["cost"] for v in rs.values()) / n, 2)}
                out[f"{case}-{model}-{arm}"] = row
                print(f"{case} {model:6s} {arm:13s} n={n} named {row['named_pct']:5}% listed {row['listed_pct']:5}% unlisted {row['unlisted']:6s} "
                      f"B {row['side_b']:7s} B-unnamed {row['side_b_unnamed']} core {row['core_pct']}% $ {row['cost_mean']}")
    json.dump(out, open(T / "notes/tables.json", "w"), indent=1)


if __name__ == "__main__":
    main()
