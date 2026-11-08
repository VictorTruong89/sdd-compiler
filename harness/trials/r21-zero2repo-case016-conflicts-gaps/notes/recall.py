"""Compiler recall on round 21's answer key (copied from round 19; conflicts only: KEPT_C)

Compiler recall on round 19's answer key: which planted conflicts the compiled store reports. No model call.

(Copied from ../r17-zero2repo-case006-conflicts-24/notes/recall.py, unchanged in method.)
    python3 notes/recall.py work/compile-full        -> notes/recall.json, table on stdout

For each kept item: the node(s) holding the side-A and side-B phrases (`PHRASES`, `FIND` and `KEPT`
in notes/plant.py), and every conflict the store holds between an A node and a B node, with its kind and state. **Found** = a `contradiction` between an A node and a B node. Also
counts every conflict in the store by kind, for the false-alarm reading the owner does.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from plant import FIND, KEPT_C as KEPT, PHRASES                             # noqa: E402

root = Path(sys.argv[1]).resolve()
nodes = {}
for f in (root / ".sdd/nodes").glob("*.jsonl"):
    for line in f.read_text().splitlines():
        if line.strip():
            n = json.loads(line)
            nodes[n["id"]] = n
conflicts = [json.loads(l) for l in (root / ".sdd/conflicts.jsonl").read_text().splitlines() if l.strip()]


def holding(text):
    return sorted(i for i, n in nodes.items() if text and text in n["text"])


out, found = {}, 0
for item in KEPT:
    a_text, b_text = FIND.get(item, (None, None))
    a_nodes, b_nodes = holding(a_text or PHRASES[item][0]), holding(b_text or PHRASES[item][1])
    hits = [c for c in conflicts if any(m in a_nodes for m in c["members"]) and any(m in b_nodes for m in c["members"])]
    contradiction = [c for c in hits if c["kind"] == "contradiction"]
    found += bool(contradiction)
    out[item] = {"a_nodes": a_nodes, "b_nodes": b_nodes,
                 "conflicts": [{"id": c["id"], "kind": c["kind"], "state": c.get("state")} for c in hits],
                 "found": bool(contradiction)}
    print(f"{item}  {'FOUND' if contradiction else 'missed'}  A={a_nodes} B={b_nodes}  "
          f"{[(c['id'], c['kind'], c.get('state')) for c in hits] or '-'}")
by_kind = {}
for c in conflicts:
    key = (c["kind"], c.get("state"))
    by_kind[f"{key[0]}/{key[1]}"] = by_kind.get(f"{key[0]}/{key[1]}", 0) + 1
(HERE / "recall.json").write_text(json.dumps({"store": str(root), "found": found, "of": len(KEPT),
                                              "items": out, "store_conflicts": by_kind}, indent=1) + "\n")
print(f"recall {found} of {len(KEPT)}; store conflicts by kind/state: {by_kind}")
