"""Split a DevEval score by how each hidden test relates to the specification.

    python3 score_by_class.py <project> <verifier dir with junit-*.xml> [...]
    python3 score_by_class.py --check <project> <verifier dir of the reference run>

Classes are in test-classification.json (one reader's judgement, by reading; method in TRIAL.md §10):
  S  the names and the expected behaviour are stated in the specification or its seed data
  U  the names are stated, the expected value or behaviour is not (a fair reading may differ)
  R  needs a name, default, key or exact string that the specification does not give
  C  expects a value that contradicts the specification
"""
import glob
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

CLASSES = json.loads((Path(__file__).parent / "test-classification.json").read_text())


def results(verifier: str) -> dict[str, bool]:
    out = {}
    for path in sorted(glob.glob(f"{verifier}/junit-*.xml")):
        for case in ET.parse(path).getroot().iter("testcase"):
            ok = all(case.find(t) is None for t in ("failure", "error", "skipped"))
            out[f"{case.get('classname')}::{case.get('name')}"] = ok
    return out


def main() -> None:
    args = sys.argv[1:]
    check = args[0] == "--check"
    project, dirs = (args[1], args[2:]) if check else (args[0], args[1:])
    tests = CLASSES[project]["tests"]
    for verifier in dirs:
        seen = results(verifier)
        if check:
            missing, extra = sorted(set(tests) - set(seen)), sorted(set(seen) - set(tests))
            print("classified", len(tests), "| in reference run", len(seen), "| missing", missing, "| extra", extra)
            if missing or extra:
                sys.exit(1)
            continue
        row = {}
        for cls in "SURC":
            ids = [t for t, v in tests.items() if v[0] == cls]
            row[cls] = f"{sum(seen.get(t, False) for t in ids)}/{len(ids)}"
        row["all"] = f"{sum(seen.get(t, False) for t in tests)}/{len(tests)}"
        print(json.dumps(row), verifier)


if __name__ == "__main__":
    main()
