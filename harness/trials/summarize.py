"""Build <trial-dir>/results.json from <trial-dir>/runs/ (never edit results.json by hand).

    python3 summarize.py <trial-dir>

Per run: the queue row (task, model), the reward file(s), per-test results from any junit-*.xml
(passed, failed, collection errors), and the agent's turns, time and Claude Code total_cost_usd (an
estimated API-equivalent on the subscription, not spend). Groups runs by (task, model) with the mean.
"""
import json
import sys
import tarfile
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from statistics import mean

T = Path(sys.argv[1]).resolve()
queue = [line.split("\t") for line in (T / "queue.tsv").read_text().splitlines()]
rows = {r[0]: dict(zip(queue[0], r)) for r in queue[1:] if r}


def junit(run: Path) -> dict:
    passed = failed = 0
    errors = []
    for path in sorted(run.glob("junit*.xml")):
        for case in ET.parse(path).getroot().iter("testcase"):
            if not case.get("classname"):
                errors.append(case.get("name"))
            elif all(case.find(t) is None for t in ("failure", "error", "skipped")):
                passed += 1
            else:
                failed += 1
    return {"passed": passed, "failed": failed, "collection_errors": errors}


def agent_result(run: Path) -> dict:
    try:
        with tarfile.open(run / "agent.tgz") as tar:
            m = next(m for m in tar.getmembers() if m.name.endswith("/agent/claude-code.txt"))
            lines = tar.extractfile(m).read().decode().splitlines()
        return json.loads(next(line for line in reversed(lines) if '"type":"result"' in line))
    except Exception:
        return {}


def seconds(span):
    if not span or not span.get("started_at") or not span.get("finished_at"):
        return None
    return round((datetime.fromisoformat(span["finished_at"]) - datetime.fromisoformat(span["started_at"])).total_seconds(), 1)


def tests_of(run, rewards):
    """Per-test counts from junit files; without any, from reward.json's tests_passed / tests_total."""
    if any(run.glob("junit-*.xml")):
        return junit(run)
    r = rewards.get("reward.json", {})
    passed = r.get("tests_passed", 0)
    return {"passed": passed, "failed": r.get("tests_total", 0) - passed, "collection_errors": 0,
            "source": "reward.json"}


runs = {}
for run in sorted(p for p in (T / "runs").iterdir() if p.is_dir()):
    trial = json.loads((run / "result.json").read_text()) if (run / "result.json").exists() else {}
    res = agent_result(run)
    rewards = {f.name: json.loads(f.read_text()) for f in sorted(run.glob("*reward*.json"))}
    runs[run.name] = {
        "task": rows.get(run.name, {}).get("task"), "model": rows.get(run.name, {}).get("model"),
        "status": rows.get(run.name, {}).get("status"),
        "rewards": rewards, "tests": tests_of(run, rewards),
        "turns": res.get("num_turns"), "subtype": res.get("subtype"),
        "agent_seconds": seconds(trial.get("agent_execution")),
        "total_cost_usd_est": res.get("total_cost_usd"),
        "exception_info": trial.get("exception_info"),
    }

groups = {}
for name, r in runs.items():
    groups.setdefault(f"{r['task']} | {r['model']}", []).append(name)
summary = {}
for key, names in groups.items():
    rs = [runs[n] for n in names]
    summary[key] = {"runs": names, "tests_passed": [r["tests"]["passed"] for r in rs],
                    "mean_tests_passed": round(mean(r["tests"]["passed"] for r in rs), 2),
                    "turns": [r["turns"] for r in rs],
                    "cost_usd_est": [r["total_cost_usd_est"] for r in rs]}
total_cost = round(sum(r["total_cost_usd_est"] or 0 for r in runs.values()), 4)
(T / "results.json").write_text(json.dumps({
    "_about": "Built by harness/trials/summarize.py from runs/. Costs: Claude Code total_cost_usd, estimated API-equivalent.",
    "total_cost_usd_est": total_cost, "groups": summary, "runs": runs}, indent=1) + "\n")
for key, s in summary.items():
    print(f"{key:60} passed {s['tests_passed']}  turns {s['turns']}  $ {s['cost_usd_est']}")
print("total cost est.", total_cost)
