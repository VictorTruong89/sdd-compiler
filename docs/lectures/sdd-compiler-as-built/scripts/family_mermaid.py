"""One family and its judged neighbours as a Mermaid diagram (paste into any Markdown viewer).

Usage:  PYTHONPATH=<repo>/src python family_mermaid.py <.sdd dir> <family> > family.mmd
"""
import sys  # run with PYTHONPATH=<repo>/src
from pathlib import Path

from sdd_compiler.store.graph import load_graph

def resolve_family(g, name):
    """Accept `model_call`, `model call` or `term:model_call`; fail loud on an unknown name."""
    import difflib
    families = {n["family"] for n in g.nodes.values() if n["family"]}
    wanted = name if name.startswith("term:") or name == "(global)" else "term:" + name.strip().replace(" ", "_")
    if wanted in families:
        return wanted
    close = difflib.get_close_matches(wanted, sorted(families), n=5)
    sys.exit(f"unknown family {name!r}. Close: {', '.join(close) or '(none)'} — see .sdd/views/map.md")


store, family = Path(sys.argv[1]), sys.argv[2]
g = load_graph(store)
family = resolve_family(g, family)
core = {i for i, n in g.nodes.items() if n["family"] == family}
# One entry per (from, type, to): the R18 store repeats replayed links (build-plan I-89).
links = list({(l["from"], l["type"], l["to"]): l for l in g.links
              if l["provenance"] == "judgment" and (l["from"] in core or l["to"] in core)}.values())
shown = core | {l["from"] for l in links} | {l["to"] for l in links}
ARROW = {"conflicts_with": "-. contradicts .->", "duplicates": "-. duplicates .->",
         "subsumes": "-- subsumes -->", "refines": "-- refines -->", "depends_on": "-- depends on -->"}


def key(node_id):
    return node_id.replace("-", "_").replace(".", "_")


print("graph LR")
for node_id in sorted(shown):
    n = g.nodes[node_id]
    label = " ".join(n["text"].split())[:40]
    label = label.replace('"', "'").replace("*", "").replace("`", "")
    print(f'  {key(node_id)}["{node_id} [{n["layer"]}]<br/>{label}"]')
for l in sorted(links, key=lambda l: (l["from"], l["to"], l["type"])):
    print(f"  {key(l['from'])} {ARROW[l['type']]} {key(l['to'])}")
for node_id in sorted(shown):
    if g.nodes[node_id]["status"] == "conflict":
        print(f"  style {key(node_id)} stroke:#c00,stroke-width:2px")
