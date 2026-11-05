"""Round 20 (copied from round 19, unchanged in method; reads footprint-G.. jobs). Read the footprint runs (notes/footprint.sh): for each alternative copy, the hidden tests whose result
differs from the base build. Writes notes/footprint.json. No model call; only the judge's reports.

    python3 notes/footprint.py
"""
import json
from pathlib import Path

T = Path(__file__).resolve().parents[1]


def failed(v):
    detail = next((T / "work/jobs" / f"footprint-{v}").rglob("verifier/reward_detail.json"))
    return {t.split("/")[-1] for t in json.loads(detail.read_text())["failed_tests"] or []}


base = failed("BASE")
out = {"BASE_failed": sorted(base)}
for d in sorted((T / "work/jobs").glob("footprint-*")):
    v = d.name.removeprefix("footprint-")
    if v == "BASE" or not d.is_dir():
        continue
    f = failed(v)
    out[v] = {"newly_failed": sorted(f - base), "newly_passed": sorted(base - f)}
    print(v, "footprint", len(f ^ base), sorted(f ^ base))
(T / "notes/footprint.json").write_text(json.dumps(out, indent=1) + "\n")
