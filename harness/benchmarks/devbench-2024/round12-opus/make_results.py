"""Build round12-opus/results.json from runs/<project>/ (never edit results.json by hand).

    python3 make_results.py

Per project: tests passed of the hidden set (counted from test-classification.json, which --check tied
to the reference runs), tests collected, whether the reward is accepted (collected <= hidden), the split
by class S/U/R/C, and the agent's turns, time and Claude Code's total_cost_usd (an estimated
API-equivalent on the subscription, not spend). hybrid-images is also scored on the tests the reference
passes (REFERENCE_FAILS).
"""
import json
import tarfile
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
CLASSES = json.loads((HERE.parent / "test-classification.json").read_text())
# The 8 tests the reference fails under today's NumPy (r6-oracle-hybrid-images and r12-oracle-hybrid-images).
REFERENCE_FAILS = {"hybrid-images": [
    f"unit_tests.unit_test.{c}::test_{t}"
    for c in ("TestCrossCorrelation2D", "TestConvolve2D")
    for t in ("identity_filter_grey", "mean_filter_grey", "mean_filter_rect_grey", "big_filter_grey")]}


def junit(run: Path) -> tuple[dict[str, bool], list[str]]:
    """Test results, and the modules pytest could not collect (junit rows with an empty classname)."""
    out, errors = {}, []
    for path in sorted(run.glob("junit-*.xml")):
        for case in ET.parse(path).getroot().iter("testcase"):
            if not case.get("classname"):
                errors.append(case.get("name"))
                continue
            out[f"{case.get('classname')}::{case.get('name')}"] = all(
                case.find(t) is None for t in ("failure", "error", "skipped"))
    return out, errors


def agent_result(run: Path) -> dict:
    """The last `result` line of agent/claude-code.txt, read from agent.tgz."""
    with tarfile.open(run / "agent.tgz") as tar:
        member = next(m for m in tar.getmembers() if m.name.endswith("/agent/claude-code.txt"))
        lines = tar.extractfile(member).read().decode().splitlines()
    return json.loads(next(line for line in reversed(lines) if '"type":"result"' in line))


def seconds(span: dict | None) -> float | None:
    if not span or not span.get("started_at") or not span.get("finished_at"):
        return None
    return round((datetime.fromisoformat(span["finished_at"]) - datetime.fromisoformat(span["started_at"])).total_seconds(), 1)


def split(tests: dict, seen: dict, ids) -> dict:
    row = {c: [sum(seen.get(t, False) for t in ids if tests[t][0] == c), sum(tests[t][0] == c for t in ids)] for c in "SURC"}
    row["all"] = [sum(seen.get(t, False) for t in ids), len(ids)]
    return row


records = {}
for run in sorted(p for p in (HERE / "runs").iterdir() if p.is_dir()):
    project = run.name
    tests = CLASSES[project]["tests"]
    seen, collection_errors = junit(run)
    reward = json.loads((run / "reward.json").read_text())
    trial = json.loads((run / "result.json").read_text())
    res = agent_result(run)
    rec = {
        "job": trial.get("trial_name"),
        "model": res.get("modelUsage") and list(res["modelUsage"]),
        "hidden_tests": len(tests),
        "tests_collected": len(seen),
        "accepted": len(seen) <= len(tests) and not (set(seen) - set(tests)),
        "unknown_test_ids": sorted(set(seen) - set(tests)),
        "collection_errors": collection_errors,
        "reward_json": reward,
        "by_class": split(tests, seen, list(tests)),
        "turns": res.get("num_turns"),
        "subtype": res.get("subtype"),
        "agent_seconds": seconds(trial.get("agent_execution")),
        "total_cost_usd_est": res.get("total_cost_usd"),
        "exception_info": trial.get("exception_info"),
    }
    if project in REFERENCE_FAILS:
        kept = [t for t in tests if t not in REFERENCE_FAILS[project]]
        rec["reference_passes_basis"] = split(tests, seen, kept)
        rec["reference_fails"] = REFERENCE_FAILS[project]
    records[project] = rec

total = {"projects": len(records), "n_per_project": 1}
for key in ("all", "S", "U", "R", "C"):
    total[key] = [sum(r["by_class"][key][i] for r in records.values()) for i in (0, 1)]
total["total_cost_usd_est"] = round(sum(r["total_cost_usd_est"] or 0 for r in records.values()), 4)
out = {"_about": "Built by make_results.py from runs/; one Opus run per project (n = 1). "
                 "Pairs are [passed, in class]. Costs are Claude Code total_cost_usd, estimated API-equivalent.",
       "total": total, "projects": records}
(HERE / "results.json").write_text(json.dumps(out, indent=1) + "\n")
for p, r in records.items():
    print(f"{p:28} {r['by_class']['all'][0]:>3}/{r['by_class']['all'][1]:<3} S {r['by_class']['S'][0]}/{r['by_class']['S'][1]}"
          f"  accepted {r['accepted']}  turns {r['turns']}  ${r['total_cost_usd_est']}")
print("total", total)
