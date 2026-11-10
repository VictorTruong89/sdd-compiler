"""Round 22: the readings of notes/readings.md as data, and every count the TRIAL.md reports.

    python3 notes/score.py            → prints the tables, writes notes/scores.json

`FOUND`: planted items each run's CONFLICTS.md names under the TRIAL.md rule. `OTHER`: its entries that
match no planted item, each read against the original Zero2Repo text as `real` (holds in the planted
text: a genuine inconsistency of the original spec) or `false` (a rule and its stated exception, two
cases, a misreading, or unclear wording). Several entries on one planted item: none occurred.
Cost and time are read from runs/<run>/result.json and run_queue.log.
"""
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
TRIAL = HERE.parent

KEYS = {
    "case006": "C01 C02 C03 C04 C05 C06 C07 C08 C09 C10 C12 C13 C14 C15 C17 C18 C20 C21 C22 C23 C25 C26 C27 C29".split(),
    "case010": "C01 C03 C04 C05 C08 C09 C11 C13 C14 C15 C16 C17 C18 C21 C22".split(),
    "case016": "C01 C06 C08 C09 C11 C12 C13 C15 C16 C17 C18 C19 C20 C21 C22 C23 C25".split(),
}
COMPILER = {   # notes/recall.json of rounds 17, 19, 21 (one full compile each, Haiku)
    "case006": "C02 C04 C05 C07 C08 C09 C13 C14 C15 C17 C21 C22 C26 C27".split(),
    "case010": "C01 C03 C09 C11 C15 C16 C18 C21 C22".split(),
    "case016": "C06 C08 C09 C11 C15 C16 C18 C21 C23".split(),
}
COMPILER_PRECISION = {"case006": (18, 69), "case010": (13, 46), "case016": (16, 67)}   # contradictions real / raised
COMPILER_COST = {"case006": (757, 2.8935), "case010": (386, 1.49), "case016": (860, 3.5773)}  # calls, $ est.


def missing(case, *items):
    return sorted(set(KEYS[case]) - set(items))


FOUND = {
    "r22-sonnet-case006-1": missing("case006", "C03", "C05", "C06", "C17"),
    "r22-sonnet-case006-2": missing("case006", "C03", "C13", "C17", "C18"),
    "r22-sonnet-case006-3": missing("case006", "C03", "C05", "C17"),
    "r22-haiku-case006-1": missing("case006", "C08", "C22"),
    "r22-haiku-case006-2": missing("case006", "C03", "C05", "C13", "C22"),
    "r22-haiku-case006-3": missing("case006", "C05"),
    "r22-sonnet-case010-1": missing("case010", "C21", "C22"),
    "r22-sonnet-case010-2": missing("case010", "C21", "C22"),
    "r22-sonnet-case010-3": missing("case010", "C14", "C21", "C22"),
    "r22-haiku-case010-1": missing("case010", "C21", "C22"),
    "r22-haiku-case010-2": missing("case010", "C21", "C22"),
    "r22-haiku-case010-3": missing("case010", "C21", "C22"),
    "r22-sonnet-case016-1": missing("case016", "C01"),
    "r22-sonnet-case016-2": missing("case016", "C12", "C13"),
    "r22-sonnet-case016-3": missing("case016", "C13"),
    "r22-haiku-case016-1": missing("case016", "C11", "C12"),
    "r22-haiku-case016-2": missing("case016", "C12"),
    "r22-haiku-case016-3": missing("case016", "C12", "C13"),
}

# Entries matching no planted item: (topic, reading). Topics are named in notes/readings.md.
OTHER = {
    "r22-sonnet-case006-2": [("interactive-session definition", "false")],
    "r22-haiku-case006-1": [("prompting option fully omitted", "false"), ("interactive-session definition", "false"),
                            ("group with options only: help or error", "false")],
    "r22-haiku-case006-2": [("chained subcommand: option after argument", "false"),
                            ("prompting option fully omitted", "false")],
    "r22-haiku-case006-3": [("prompting option fully omitted", "false"), ("nested group callback", "false")],
    "r22-sonnet-case010-2": [("nonterminal symbol: str allowed vs not str in rhs()", "real")],
    "r22-haiku-case010-1": [("underivable list: empty iterator vs raise", "false"),
                            ("nonterminal symbol: str allowed vs not str in rhs()", "real")],
    "r22-haiku-case010-3": [("bare trailing apostrophe split vs kept", "false")],
    "r22-haiku-case016-1": [("zero-width character always invisible", "false"), ("show message promises .pdf rows", "real"),
                            ("at most one file operand vs several succeed", "real"),
                            ("model-dialect needs two hits", "false"), ("welcome names prosecheck vs silent contract", "false")],
    "r22-haiku-case016-2": [("model-dialect needs two hits", "false"), ("Node.js needed for the detector", "false")],
    "r22-haiku-case016-3": [("model-dialect needs two hits", "false"),
                            ("at most one file operand vs several succeed", "real"),
                            ("score_ci omitted vs null (borderline)", "false"),
                            ("findings inside code vs invisible characters counted", "false")],
}


def run_cost(run):
    try:
        res = json.load(open(TRIAL / "runs" / run / "result.json"))
    except Exception:
        return None
    log = (TRIAL / "run_queue.log").read_text()
    m = re.search(rf"harbor {re.escape(run)} exit \d+ after (\d+) s", log)
    c = re.search(rf"done {re.escape(run)} turns (\d+) cost_usd_est ([\d.]+)", log)
    return {"seconds": int(m.group(1)) if m else None, "turns": int(c.group(1)) if c else None,
            "cost": float(c.group(2)) if c else None}


def main():
    out = {"runs": {}, "cells": {}, "items": {}}
    for run, found in FOUND.items():
        case = run.split("-")[2]
        other = OTHER.get(run, [])
        real = sum(1 for _, r in other if r == "real")
        entries = len(found) + len(other)
        out["runs"][run] = {"case": case, "found": len(found), "of": len(KEYS[case]), "entries": entries,
                            "planted_entries": len(found), "real_other": real,
                            "false": len(other) - real, "missed": sorted(set(KEYS[case]) - set(found)),
                            **(run_cost(run) or {})}
    print("| Case | Model | Found per run | Mean recall | Correct entries / entries | Precision | $ est. per run | s per run |")
    print("|---|---|---|---|---|---|---|---|")
    for case in KEYS:
        for model in ("haiku", "sonnet"):
            rs = [out["runs"][f"r22-{model}-{case}-{n}"] for n in (1, 2, 3)]
            good = sum(r["planted_entries"] + r["real_other"] for r in rs)
            ent = sum(r["entries"] for r in rs)
            rec = sum(r["found"] for r in rs) / (3 * len(KEYS[case]))
            cost = [r["cost"] for r in rs]
            secs = [r["seconds"] for r in rs]
            out["cells"][f"{case}-{model}"] = {"found": [r["found"] for r in rs], "recall": rec,
                                               "correct": good, "entries": ent, "cost": cost, "seconds": secs}
            print(f"| {case} | {model} | {' · '.join(str(r['found']) for r in rs)} / {len(KEYS[case])} | "
                  f"{rec:.1%} | {good} / {ent} | {good / ent:.1%} | "
                  f"{min(cost):.2f}–{max(cost):.2f} | {min(secs)}–{max(secs)} |")
        n, d = COMPILER_PRECISION[case]
        calls, usd = COMPILER_COST[case]
        print(f"| {case} | compiler (Haiku) | {len(COMPILER[case])} / {len(KEYS[case])} (1 compile) | "
              f"{len(COMPILER[case]) / len(KEYS[case]):.1%} | {n} / {d} contradictions | {n / d:.1%} | "
              f"{usd:.2f} ({calls} calls) | — |")
    tot = {m: [0, 0, 0, 0] for m in ("haiku", "sonnet")}
    for run, r in out["runs"].items():
        t = tot[run.split("-")[1]]
        t[0] += r["found"]; t[1] += r["of"]; t[2] += r["planted_entries"] + r["real_other"]; t[3] += r["entries"]
    for m, t in tot.items():
        print(f"all cases, {m}: recall {t[0]} / {t[1]} = {t[0] / t[1]:.1%}; precision {t[2]} / {t[3]} = {t[2] / t[3]:.1%}")
    cp = sum(v[0] for v in COMPILER_PRECISION.values()), sum(v[1] for v in COMPILER_PRECISION.values())
    cr = sum(len(v) for v in COMPILER.values()), sum(len(v) for v in KEYS.values())
    print(f"all cases, compiler: recall {cr[0]} / {cr[1]} = {cr[0] / cr[1]:.1%}; contradictions real {cp[0]} / {cp[1]} = {cp[0] / cp[1]:.1%}")

    print("\nPer item: review runs that found it (of 6), and the compiler")
    for case in KEYS:
        for item in KEYS[case]:
            k = sum(item in FOUND[f"r22-{m}-{case}-{n}"] for m in ("haiku", "sonnet") for n in (1, 2, 3))
            comp = item in COMPILER[case]
            out["items"][f"{case}-{item}"] = {"review_runs": k, "compiler": comp}
        never = [i for i in KEYS[case] if out["items"][f"{case}-{i}"]["review_runs"] == 0]
        only_compiler = [i for i in never if out["items"][f"{case}-{i}"]["compiler"]]
        comp_missed_review_all = [i for i in KEYS[case] if not out["items"][f"{case}-{i}"]["compiler"]
                                  and out["items"][f"{case}-{i}"]["review_runs"] == 6]
        print(f"{case}: never found by review {never} (compiler found {only_compiler}); "
              f"missed by the compiler, found by all 6 review runs: {comp_missed_review_all}")
    allcost = [r["cost"] for r in out["runs"].values()]
    print(f"\ntotal $ est. {sum(allcost):.2f} for {len(allcost)} runs")
    out["total_cost"] = sum(allcost)
    json.dump(out, open(HERE / "scores.json", "w"), indent=1)


if __name__ == "__main__":
    main()
