"""Round 28 review scores from the reader's readings (notes/readings.md). No model call.

    python3 notes/score.py      -> notes/scores.json, table on stdout
"""
import json
from pathlib import Path

T = Path(__file__).resolve().parents[1]
N = {"case005": 17, "case011": 12, "case001": 15}
# run: (entries, found, missed, real-other, false-other) -- from notes/readings.md
R = {
    "case005": {"haiku-1": (16, 15, "C12 C18", 0, 1), "haiku-2": (15, 15, "C12 C15", 0, 0), "haiku-3": (17, 17, "", 0, 0),
                "sonnet-1": (15, 15, "C12 C15", 0, 0), "sonnet-2": (16, 16, "C12", 0, 0), "sonnet-3": (16, 16, "C12", 0, 0)},
    "case011": {"haiku-1": (14, 11, "C19", 2, 1), "haiku-2": (15, 12, "", 3, 0), "haiku-3": (13, 12, "", 1, 0),
                "sonnet-1": (12, 12, "", 0, 0), "sonnet-2": (12, 12, "", 0, 0), "sonnet-3": (12, 12, "", 0, 0)},
    "case001": {"haiku-1": (14, 14, "C16", 0, 0), "haiku-2": (12, 12, "C12 C16 C17", 0, 0), "haiku-3": (14, 13, "C16 C17", 0, 1),
                "sonnet-1": (16, 15, "", 0, 1), "sonnet-2": (14, 14, "C17", 0, 0), "sonnet-3": (16, 15, "", 0, 1)},
}
out = {}
for case, runs in R.items():
    for run, (entries, found, missed, real, false) in runs.items():
        assert entries == found + real + false, (case, run)
        assert N[case] - found == len(missed.split()), (case, run)
        m, i = run.split("-")
        rid = f"r28-{m}-review-{case}-{i}"
        res = [json.loads(l) for l in (T / "runs" / rid / "result.json").read_text().splitlines()[:1]] if False else None
        out[rid] = {"case": case, "model": m, "entries": entries, "found": found, "of": N[case], "missed": missed.split(),
                    "real_other": real, "false": false, "recall": round(found / N[case], 3),
                    "precision": round((found + real) / entries, 3)}
log = (T / "run_queue.log").read_text().splitlines()
for rid in out:
    line = next(l for l in log if f"done {rid} " in l)
    out[rid]["cost"] = float(line.split("cost_usd_est ")[1].split()[0])
(T / "notes/scores.json").write_text(json.dumps(out, indent=1) + "\n")
for case in N:
    for m in ("haiku", "sonnet"):
        rs = [v for v in out.values() if v["case"] == case and v["model"] == m]
        print(case, m, "found", [r["found"] for r in rs], f"of {N[case]}", "recall mean", round(sum(r["recall"] for r in rs) / 3, 3),
              "false", sum(r["false"] for r in rs), "precision mean", round(sum(r["precision"] for r in rs) / 3, 3), "$", round(sum(r["cost"] for r in rs), 2))
