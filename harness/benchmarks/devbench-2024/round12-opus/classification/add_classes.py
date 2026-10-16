"""Add one project's classes to test-classification.json (keeps the other projects untouched).

    python3 add_classes.py <project> <classes.json>   # classes.json: {"tests": {id: [class, reason]}}
"""
import json
import sys
from pathlib import Path

path = Path(__file__).resolve().parents[2] / "test-classification.json"
data = json.loads(path.read_text())
project, new = sys.argv[1], json.loads(Path(sys.argv[2]).read_text())
assert all(v[0] in "SURC" for v in new["tests"].values()), "class must be S, U, R or C"
data[project] = new
path.write_text(json.dumps(data, indent=1, ensure_ascii=False))
print(project, {c: sum(v[0] == c for v in new["tests"].values()) for c in "SURC"}, "->", path.name)
