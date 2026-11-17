"""Sample-size estimate for the final report's claims, from the measured runs of rounds 18–25. No model call.

    python3 harness/trials/stats/power_plan.py      -> prints the tables, writes harness/trials/stats/power_plan.json

Unit of analysis: the CASE (the claims are about specifications in general); runs inside a case make that
case's mean more precise. Each model is analysed on its own. Method as interim report §7.1 (2026-11-03),
re-estimated here on all rounds to 25.

Data (per run): core % and named % from round 21/23/24 (r24 notes/tables.json, which recomputes rounds 21 and
23 from their files), rounds 18/19/25 (r25 notes/tables.json) and round 27's compiler export (r27 notes/tables.json); silent inventions from round 20 and round 21
notes/detection.tsv by the round's strict rule (flagged = no; built upstream or alternative).
"""
import csv
import json
import math
import random
from pathlib import Path
from statistics import mean, stdev

TR = Path(__file__).resolve().parents[1]
import os
# TOPUP=1 (added 2026-11-17): add round 27b's Haiku runs (-4, -5) to the case006 and case010 Haiku cells
# (n = 5 there, as on the other cases) and write power_plan_topup.json; the default run keeps n = 3.
TOPUP = os.environ.get("TOPUP") == "1"
OUT = Path(__file__).resolve().parent / ("power_plan_topup.json" if TOPUP else "power_plan.json")
R27B = {"case006": "r27b-zero2repo-haiku-topup-case006", "case010": "r27b-zero2repo-haiku-topup-case010"}
CORE_N = {"case006": 445, "case010": 173, "case016": 338, "case005": 335, "case011": 271, "case001": 265}
ITEMS = {"case006": 24, "case010": 15, "case016": 17, "case005": 17, "case011": 12, "case001": 15}
# Round 28 (added 2026-11-16): three new cases, four arms each, one folder per case.
R28 = {"case005": "r28-zero2repo-case005-conflicts-gaps", "case011": "r28-zero2repo-case011-conflicts-gaps",
       "case001": "r28-zero2repo-case001-conflicts-gaps"}
CASES = ["case006", "case010", "case016", "case005", "case011", "case001"]
ARM_NAMES = {"markdown": "markdown", "oracle export": "oracle", "review list": "review", "compiler": "compiler",
             "oracle": "oracle", "r23": "review"}


def load_runs():
    """{(case, model, arm): {"core": [%], "named": [%]}}"""
    d = {}
    t24 = json.loads((TR / "r24-zero2repo-case016-settled-list/notes/tables.json").read_text())
    for k, v in t24.items():
        if not v:
            continue
        parts = k.split("-")
        if parts[0] == "r21":
            arm, model = parts[1], parts[2]
        elif parts[0] == "r23":
            arm, model = "review", parts[1]
        else:
            arm, model = "settled", parts[1]
        d[("case016", model, ARM_NAMES.get(arm, arm))] = {
            "core": [100 * c / CORE_N["case016"] for c in v["core"]],
            "named": [100 * x / ITEMS["case016"] for x in v["named"]]}
    t25 = json.loads((TR / "r25-zero2repo-review-list-case006-case010/notes/tables.json").read_text())
    for k, v in t25.items():
        case, model, arm = k.split("-", 2)
        d[(case, model, ARM_NAMES[arm])] = {"core": [100 * c / CORE_N[case] for c in v["core"]],
                                           "named": [100 * x / ITEMS[case] for x in v["named_per_run"]]}
    # Round 27 (added 2026-11-11): the compiler-export arm on case006 and case010 (its tables.json also repeats
    # rounds 18/19/25's arms, already loaded above; only the compiler rows are taken).
    t27 = json.loads((TR / "r27-zero2repo-compiler-export-case006-case010/notes/tables.json").read_text())
    for k, v in t27.items():
        case, model, arm = k.split("-", 2)
        if arm != "compiler export":
            continue
        d[(case, model, "compiler")] = {"core": [100 * c / CORE_N[case] for c in v["core"]],
                                        "named": [100 * x / ITEMS[case] for x in v["named_per_run"]]}
    # Round 28: each case's notes/tables.json "per_run" (core tests and conflicts named per run).
    for case, folder in R28.items():
        for run, v in json.loads((TR / folder / "notes/tables.json").read_text())["per_run"].items():
            cell = d.setdefault((case, v["model"], v["arm"]), {"core": [], "named": []})
            cell["core"].append(100 * v["core"] / CORE_N[case])
            cell["named"].append(100 * v["named"] / ITEMS[case])
    if TOPUP:
        for case, folder in R27B.items():
            sc = json.loads((TR / folder / f"score/{case}/notes/scores.json").read_text())
            named = {}
            for r in csv.DictReader(open(TR / folder / "notes/detection.tsv"), delimiter="\t"):
                named[r["run"]] = named.get(r["run"], 0) + (r["named"] == "yes")
            for run in sorted(named):
                arm = run.split("-")[3]
                cell = d[(case, "haiku", arm)]
                cell["core"].append(100 * sc[run]["core"] / CORE_N[case])
                cell["named"].append(100 * named[run] / ITEMS[case])
    return d


def silent_runs():
    """{(case, model, arm): [silent count per run]} for round 20 (case010, 14 gaps), round 21 and 23 (case016, 15;
    round 23 is the review list on the same planted spec) and round 28 (case005 11, case011 12, case001 4 gaps;
    each case's tables.json "gaps_silent", the same strict rule)."""
    out = {}
    r21_gaps = "G02 G03 G04 G05 G06 G07 G08 G09 G10 G11 G12 G13 G21 G30 G33".split()
    for case, folder in R28.items():
        for run, v in json.loads((TR / folder / "notes/tables.json").read_text())["per_run"].items():
            out.setdefault((case, v["model"], v["arm"]), []).append(v["gaps_silent"])
    for folder, case, gaps in (("r20-zero2repo-case010-gaps", "case010", None),
                               ("r21-zero2repo-case016-conflicts-gaps", "case016", r21_gaps),
                               ("r23-zero2repo-case016-review-list", "case016", r21_gaps)):
        per = {}
        for r in csv.DictReader(open(TR / folder / "notes/detection.tsv"), delimiter="\t"):
            if not r["item"].startswith("G") or (gaps and r["item"] not in gaps):
                continue
            silent = r["flagged"] != "yes" and r["built"] in ("upstream", "alternative")
            per.setdefault(r["run"], 0)
            per[r["run"]] += silent
        for run, n in per.items():
            _, model, arm, _ = run.split("-")
            out.setdefault((case, model, {"export": "compiler"}.get(arm, arm)), []).append(n)
    return out


def pooled_sd(groups):
    num = sum((len(g) - 1) * stdev(g) ** 2 for g in groups if len(g) > 1)
    den = sum(len(g) - 1 for g in groups if len(g) > 1)
    return math.sqrt(num / den)


def t_quantile(p, df):
    """Student t quantile by bisection on the regularized incomplete beta (no scipy)."""
    def cdf(t):
        x = df / (df + t * t)
        ib = betainc(df / 2, 0.5, x)
        return 1 - 0.5 * ib if t > 0 else 0.5 * ib
    lo, hi = -50.0, 50.0
    for _ in range(200):
        mid = (lo + hi) / 2
        if cdf(mid) < p:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def betainc(a, b, x):
    """Regularized incomplete beta I_x(a, b), continued fraction (Numerical Recipes)."""
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0
    lbeta = math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b) + a * math.log(x) + b * math.log(1 - x)
    front = math.exp(lbeta)
    if x < (a + 1) / (a + b + 2):
        return front * cf(a, b, x) / a
    return 1 - front * cf(b, a, 1 - x) / b


def cf(a, b, x):
    tiny = 1e-30
    c, d = 1.0, 1 - (a + b) * x / (a + 1)
    d = 1 / (d if abs(d) > tiny else tiny)
    h = d
    for m in range(1, 300):
        m2 = 2 * m
        aa = m * (b - m) * x / ((a + m2 - 1) * (a + m2))
        d = 1 + aa * d; d = 1 / (d if abs(d) > tiny else tiny)
        c = 1 + aa / c if abs(1 + aa / c) > tiny else tiny
        h *= d * c
        aa = -(a + m) * (a + b + m) * x / ((a + m2) * (a + m2 + 1))
        d = 1 + aa * d; d = 1 / (d if abs(d) > tiny else tiny)
        c = 1 + aa / c if abs(1 + aa / c) > tiny else tiny
        de = d * c
        h *= de
        if abs(de - 1) < 1e-12:
            break
    return h


def t_test_p(diffs):
    """Two-sided one-sample t-test p of the mean case difference against 0."""
    k = len(diffs)
    m, s = mean(diffs), stdev(diffs)
    t = m / (s / math.sqrt(k))
    x = (k - 1) / (k - 1 + t * t)
    return betainc((k - 1) / 2, 0.5, x), t


def lower_bound(diffs):
    k = len(diffs)
    return mean(diffs) - t_quantile(0.95, k - 1) * stdev(diffs) / math.sqrt(k)


def sim_noninf(sigma, tau, delta, k, n, true=0.0, reps=4000, seed=7):
    rng = random.Random(seed)
    q = t_quantile(0.95, k - 1)
    ok = 0
    for _ in range(reps):
        diffs = []
        for _ in range(k):
            eff = true + rng.gauss(0, tau)
            a = [rng.gauss(eff, sigma) for _ in range(n)]
            b = [rng.gauss(0, sigma) for _ in range(n)]
            diffs.append(mean(a) - mean(b))
        lb = mean(diffs) - q * stdev(diffs) / math.sqrt(k)
        ok += lb > -delta
    return ok / reps


def sim_superiority(effect, tau, sigma, k, n, reps=4000, seed=11):
    """Power of the two-sided t-test over k case differences (alpha 0.05)."""
    rng = random.Random(seed)
    q = t_quantile(0.975, k - 1)
    ok = 0
    for _ in range(reps):
        diffs = []
        for _ in range(k):
            eff = effect + rng.gauss(0, tau)
            diffs.append(mean(rng.gauss(eff, sigma) for _ in range(n)) - mean(rng.gauss(0, sigma) for _ in range(n)))
        s = stdev(diffs)
        ok += s > 0 and abs(mean(diffs)) / (s / math.sqrt(k)) > q
    return ok / reps


def tau_estimate(diffs, sampling_vars):
    v = stdev(diffs) ** 2 - mean(sampling_vars)
    return math.sqrt(max(v, 0.0))


def main():
    d = load_runs()
    out = {"cases": CASES}
    print("== Per-case effects (arm mean minus Markdown mean, points of %)")
    effects = {}
    for model in ("haiku", "sonnet"):
        for arm in ("oracle", "review", "compiler"):
            for measure in ("core", "named"):
                diffs, svars = [], []
                for case in out["cases"]:
                    if (case, model, arm) not in d:
                        continue
                    a, b = d[(case, model, arm)][measure], d[(case, model, "markdown")][measure]
                    diffs.append(mean(a) - mean(b))
                    svars.append(stdev(a) ** 2 / len(a) + stdev(b) ** 2 / len(b))
                effects[(model, arm, measure)] = (diffs, svars)
                print(f"  {model:6s} {arm:8s} {measure:5s} " + "  ".join(f"{x:+6.1f}" for x in diffs))
    sig = {}
    for model in ("haiku", "sonnet"):
        for measure in ("core", "named"):
            groups = [v[measure] for (c, m, a), v in d.items() if m == model and a in ("markdown", "oracle", "review", "compiler")]
            sig[(model, measure)] = pooled_sd(groups)
    print("\n== Run-to-run SD, pooled within cells (points of %)")
    for k, v in sig.items():
        print(f"  {k[0]:6s} {k[1]:5s} {v:5.2f}")
    print("\n== Tests over the cases (t over case differences; sign test needs all K same sign: p = 2 x 0.5^K)")
    tests = {}
    for (model, arm, measure), (diffs, svars) in effects.items():
        if len(diffs) < 3:
            continue
        p, t = t_test_p(diffs)
        lb = lower_bound(diffs)
        tau = tau_estimate(diffs, svars)
        tests[f"{model}-{arm}-{measure}"] = {"diffs": [round(x, 2) for x in diffs], "mean": round(mean(diffs), 2),
                                             "t_p_two_sided": round(p, 4), "lower95": round(lb, 2), "tau_est": round(tau, 2),
                                             "sign_test_p": round(2 * 0.5 ** len(diffs), 3) if all(x > 0 for x in diffs) or all(x < 0 for x in diffs) else None}
        print(f"  {model:6s} {arm:7s} {measure:5s} mean {mean(diffs):+6.2f}  t-test p {p:.3f}  one-sided 95% lower bound {lb:+6.2f}  tau {tau:4.2f}")
    out["tests"] = tests
    out["run_sd"] = {f"{k[0]}-{k[1]}": round(v, 2) for k, v in sig.items()}
    # Non-inferiority power for set 1 (core), true difference 0.
    print("\n== Power, set 1 non-inferiority (true difference 0; one-sided 95 % lower bound over cases > -delta)")
    plan = {}
    for model, delta in (("sonnet", 2.0), ("haiku", 5.0), ("haiku", 3.0)):
        sigma = sig[(model, "core")]
        taus = [tests[f"{model}-oracle-core"]["tau_est"], tests[f"{model}-review-core"]["tau_est"]]
        tau = max(max(taus), 0.5)
        for n in (3, 5, 8):
            row = {}
            for k in (3, 4, 5, 6, 8):
                row[k] = sim_noninf(sigma, tau, delta, k, n)
            plan[f"{model}-delta{delta:g}-n{n}"] = {"sigma": round(sigma, 2), "tau": round(tau, 2), **{str(k): v for k, v in row.items()}}
            print(f"  {model:6s} delta {delta:3g} n {n}: sigma {sigma:4.2f} tau {tau:4.2f}  " +
                  "  ".join(f"K={k}: {v:.2f}" for k, v in row.items()))
    out["power_noninferiority_core"] = plan
    # Superiority power for set 2a (named): smallest observed mean effect among oracle and review arms.
    print("\n== Power, set 2a superiority (t-test over cases, alpha 0.05), effect = smallest observed arm mean")
    sup = {}
    for model in ("haiku", "sonnet"):
        cands = [tests[f"{model}-{a}-named"] for a in ("oracle", "review")]
        eff = min(c["mean"] for c in cands)
        tau = max(c["tau_est"] for c in cands)
        sigma = sig[(model, "named")]
        for n in (3, 5):
            row = {k: sim_superiority(eff, tau, sigma, k, n) for k in (3, 4, 5, 6)}
            sup[f"{model}-n{n}"] = {"effect": eff, "tau": tau, "sigma": round(sigma, 2), **{str(k): v for k, v in row.items()}}
            print(f"  {model:6s} n {n}: effect {eff:5.1f} tau {tau:5.2f} sigma {sigma:5.2f}  " + "  ".join(f"K={k}: {v:.2f}" for k, v in row.items()))
    out["power_superiority_named"] = sup
    # Silent invention (set 2b): equivalence margin of 2 gaps per run.
    s = silent_runs()
    print("\n== Silent inventions per run (set 2b), cases with gaps")
    sil = {}
    for k, v in sorted(s.items()):
        sil["-".join(k)] = v
        print(f"  {k}: {v}  mean {mean(v):.2f}")
    sd_s = pooled_sd(list(s.values()))
    print(f"  pooled run SD {sd_s:.2f} gaps")
    eq = {}
    for k in (2, 3, 4, 6):
        for n in (3, 5):
            eq[f"K{k}-n{n}"] = sim_noninf(sd_s, 0.5, 2.0, k, n)
    print("  power to show export - Markdown > -2 gaps (one side of an equivalence test): " +
          "  ".join(f"{k}: {v:.2f}" for k, v in eq.items()))
    # Equivalence test (TOST, margin 2 gaps per run): 90 % interval of the mean case difference (arm minus
    # Markdown) inside (-2, +2); with and without case001 (4 gaps only, decided 2026-11-11 before any run).
    print("\n== Silent invention, equivalence over cases (90 % interval of arm - Markdown, margin 2 gaps)")
    eqt = {}
    for model in ("haiku", "sonnet"):
        for arm in ("compiler", "oracle", "review"):
            for drop in (None, "case001"):
                diffs = [mean(s[(c, model, arm)]) - mean(s[(c, model, "markdown")]) for c in CASES
                         if c != drop and (c, model, arm) in s and (c, model, "markdown") in s]
                if len(diffs) < 3:
                    continue
                half = t_quantile(0.95, len(diffs) - 1) * stdev(diffs) / math.sqrt(len(diffs))
                lo, hi = mean(diffs) - half, mean(diffs) + half
                key = f"{model}-{arm}" + ("" if drop is None else "-without-case001")
                eqt[key] = {"diffs": [round(x, 2) for x in diffs], "mean": round(mean(diffs), 2),
                            "ci90": [round(lo, 2), round(hi, 2)], "equivalent": lo > -2 and hi < 2}
                print(f"  {key:30s} K={len(diffs)} mean {mean(diffs):+5.2f}  90% CI [{lo:+5.2f}, {hi:+5.2f}]  "
                      f"{'equivalent' if lo > -2 and hi < 2 else 'not shown'}")
    out["silent"] = {"runs": sil, "run_sd": round(sd_s, 2), "power_margin2": eq, "equivalence": eqt}
    OUT.write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
