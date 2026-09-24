"""Context pack for one family, read straight from a .sdd store (no sddc command needed).

Usage:  PYTHONPATH=<repo>/src python context_pack.py <.sdd dir> <family>
"""
import json, sys
from pathlib import Path

from sdd_compiler.store.graph import load_graph
from sdd_compiler.model.scope import covers

def resolve_family(g, name):
    """Accept `model_call`, `model call` or `term:model_call`; fail loud on an unknown name."""
    import difflib
    families = {n["family"] for n in g.nodes.values() if n["family"]}
    wanted = name if name.startswith("term:") or name == "(global)" else "term:" + name.strip().replace(" ", "_")
    if wanted in families:
        return wanted
    close = difflib.get_close_matches(wanted, sorted(families), n=5)
    sys.exit(f"unknown family {name!r}. Close: {', '.join(close) or '(none)'} — see .sdd/views/map.md")


store, family = Path(sys.argv[1]), sys.argv[2]            # e.g.  .sdd  term:model_call
g = load_graph(store)
family = resolve_family(g, family)
LAYER_ORDER = ["L0", "L1", "L2", "L3", "L4", "L5", "C", "V", None]

core = [n for n in g.nodes.values() if n["family"] == family]
core_ids = {n["id"] for n in core}
constraints = [n for n in g.nodes.values()
               if n["layer"] == "C" and n["id"] not in core_ids and any(covers(n, c) for c in core)]
tests = [n for n in g.nodes.values()
         if n["layer"] == "V" and n["id"] not in core_ids and core_ids & set(n.get("verifies") or [])]
conflicts = [c for c in g.conflicts.values()
             if c["state"] == "open" and core_ids & set(c["members"])]

def line(n):
    s = n["source"]
    flag = {"conflict": "✗", "ambiguous": "?", "stale": "~", "unchecked": "·", "validated": "✓"}[n["status"]]
    return f'{flag} {n["id"]:<10} {n["layer"] or "—":<3} {s["file"]}:{s["lines"][0]}  {n["text"][:90]!r}'

print(f"# context pack: {family}")
for title, group in (("core", sorted(core, key=lambda n: LAYER_ORDER.index(n["layer"]))),
                     ("constraints in scope", constraints), ("verifications", tests)):
    print(f"\n## {title} ({len(group)})")
    for n in group:
        print(line(n))
print(f"\n## open conflicts touching it ({len(conflicts)})")
for c in sorted(conflicts, key=lambda c: c["id"]):
    print(f'{c["id"]} {c["kind"]}: {" vs ".join(c["members"])} — {c["rationale"][:100]}')
