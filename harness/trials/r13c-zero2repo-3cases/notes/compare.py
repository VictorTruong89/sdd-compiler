"""Compare failed tests between Markdown and export runs, per case and model.

    python3 notes/compare.py            (from the trial folder) → notes/compare.md and notes/compare.json

Reads runs/<run_id>/reward.json (passed / total) and reward_detail.json (failed_tests, error_tests),
both written by the judge-based test.sh (notes/build_task.py). Run ids: <model>-<case>-<format>-<n>.
Also reads round 13b's single Haiku Markdown run per case, shown apart (not counted in n).
For each (case, model): tests failed in every Markdown run but no export run (export gain), in every
export run but no Markdown run (export loss), in some runs of either format (unstable), in all runs.
"""
import json
import re
from collections import defaultdict
from pathlib import Path

T = Path(__file__).resolve().parents[1]
SWEEP = T.parent / "r13b-zero2repo-haiku-sweep" / "runs"


def load(run_dir):
    r = json.loads((run_dir / "reward.json").read_text())
    d = json.loads((run_dir / "reward_detail.json").read_text()) if (run_dir / "reward_detail.json").exists() else {}
    failed = {t.split("::", 1)[-1] for t in (d.get("failed_tests") or []) + (d.get("error_tests") or [])}
    feature = {t.split("::", 1)[-1]: Path(t.split("::", 1)[0]).name.split("_")[0]
               for t in (d.get("failed_tests") or []) + (d.get("error_tests") or [])}
    return {"passed": r.get("tests_passed"), "total": r.get("tests_total"), "official": r.get("official_reward"),
            "failed": failed, "feature": feature}


cells = defaultdict(dict)          # (case, model) -> fmt -> {run_id: data}
for run in sorted((T / "runs").iterdir()):
    m = re.fullmatch(r"(haiku|sonnet)-(case\d+)-(markdown|export)-(\d+)", run.name)
    if m and (run / "reward.json").exists():
        cells[(m[2], m[1])].setdefault(m[3], {})[run.name] = load(run)
sweep = {}
for run in sorted(SWEEP.iterdir()) if SWEEP.exists() else []:
    m = re.fullmatch(r"haiku-(case\d+)-1", run.name)
    if m and (run / "reward.json").exists():
        sweep[m[1]] = load(run)

out, md = {}, ["# Markdown vs export: failed tests per case and model", "",
               "Built by `notes/compare.py` from `runs/*/reward.json` and `reward_detail.json`.", ""]
for (case, model) in sorted(cells):
    fm = cells[(case, model)]
    mk, ex = fm.get("markdown", {}), fm.get("export", {})
    allruns = {**mk, **ex}
    if not allruns:
        continue
    # a run whose tests did not load (judge total 0) lists no failed test; it is shown in the table
    # but left out of the test-set comparison, or it would read as "failed nothing"
    fail_md = [v["failed"] for v in mk.values() if v["total"]]
    fail_ex = [v["failed"] for v in ex.values() if v["total"]]
    every = lambda sets: set.intersection(*sets) if sets else set()
    some = lambda sets: set.union(*sets) if sets else set()
    feature = {}
    for v in allruns.values():
        feature.update(v["feature"])
    res = {
        "runs": {k: {"passed": v["passed"], "total": v["total"], "official": v["official"]} for k, v in allruns.items()},
        "export_gain": sorted(every(fail_md) - some(fail_ex)) if fail_md and fail_ex else [],
        "export_loss": sorted(every(fail_ex) - some(fail_md)) if fail_md and fail_ex else [],
        "failed_in_all_runs": sorted(every(fail_md + fail_ex)),
        "unstable": sorted(some(fail_md + fail_ex) - every(fail_md + fail_ex)),
    }
    out[f"{case}|{model}"] = res
    md += [f"## {case}, {model}", "",
           "| Run | Passed | Official |", "|---|---|---|"]
    md += [f"| {k} | {v['passed']} / {v['total']} | {v['official']} |" + (" tests did not load; left out of the sets below" if not v["total"] else "")
           for k, v in sorted(res["runs"].items())]
    if model == "haiku" and case in sweep:
        s = sweep[case]
        md += [f"| (13b sweep, Markdown) | {s['passed']} / {s['total']} | {s['official']} |"]
    md.append("")
    for key, title in [("export_gain", "Failed in every Markdown run, in no export run"),
                       ("export_loss", "Failed in every export run, in no Markdown run"),
                       ("failed_in_all_runs", "Failed in every run, both formats"),
                       ("unstable", "Failed in some runs only")]:
        items = res[key]
        md.append(f"**{title}** ({len(items)})" + (":" if items else ""))
        md += [f"- `{feature.get(t, '?')}` {t}" for t in items]
        md.append("")
(T / "notes" / "compare.json").write_text(json.dumps(out, indent=1))
(T / "notes" / "compare.md").write_text("\n".join(md) + "\n")
print("\n".join(md[:60]))
