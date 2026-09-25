"""Build a self-contained HTML explorer of a compiled spec graph.

Usage:  PYTHONPATH=<repo>/src python build_viewer.py <.sdd dir> <out.html> [--fragment] [--label TEXT]

Reads the store with the compiler's own loader (so it sees exactly what the checks see), keeps the
judged links and `verifies` links (the 2 800 `uses_term` links are summarised as each node's terms),
and fills `viewer_template.html`. The output is one file with no server and no build step.
`--fragment` omits the <!doctype>/<html> wrapper (for publishing as an Artifact page).
"""
import argparse
import json
from pathlib import Path

from sdd_compiler.store.graph import load_graph

HERE = Path(__file__).parent


def export(store: Path) -> dict:
    g = load_graph(store)
    nodes = []
    for n in sorted(g.nodes.values(), key=lambda n: n["id"]):
        c = n["canonical"]
        nodes.append({
            "id": n["id"], "k": n["kind"], "l": n["layer"], "f": n["family"], "s": n["status"],
            "t": " ".join(n["text"].split()), "file": n["source"]["file"], "ln": n["source"]["lines"][0],
            "h": " › ".join(n["source"]["heading_path"][-2:]),
            "c": [c.get("state"), c.get("trigger"), c.get("scope"), c.get("subject"), c.get("modality"), c.get("response")],
            "q": [q.get("quote") for q in c.get("quantities") or []],
            "terms": [t["term"] for t in n["terms"]], "amb": [a["kind"] for a in n["ambiguity"]],
            "cf": n["conflict_ids"], "flags": n["flags"], "label": n["label"], "rule": n["family_rule"],
        })
    links = {}
    for l in g.links:
        if l["type"] == "uses_term":
            continue
        links[(l["from"], l["type"], l["to"])] = {"a": l["from"], "r": l["type"], "b": l["to"],
                                                  "why": l.get("rationale")}
    conflicts = [{"id": c["id"], "k": c["kind"], "m": c["members"], "why": c["rationale"]}
                 for c in sorted(g.conflicts.values(), key=lambda c: c["id"]) if c["state"] == "open"]
    terms = {t["id"]: {"n": t["canonical"], "a": t["aliases"], "b": t["broader"]} for t in g.terms.values()}
    meta = json.loads((store / "graph.meta.json").read_text())
    return {"nodes": nodes, "links": list(links.values()), "conflicts": conflicts, "terms": terms,
            "meta": {"compiler": meta.get("compiler_version"), "store": str(store)}}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("store", type=Path, help="the .sdd directory")
    parser.add_argument("out", type=Path, help="the HTML file to write")
    parser.add_argument("--fragment", action="store_true", help="no <!doctype>/<html> wrapper")
    parser.add_argument("--label", default=None, help="a name for the graph, shown in the header")
    args = parser.parse_args()
    if not (args.store / "graph.meta.json").exists():
        parser.error(f"{args.store} is not a compiled .sdd store (no graph.meta.json)")
    data = export(args.store)
    data["meta"]["label"] = args.label or str(args.store)
    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    page = (HERE / "viewer_template.html").read_text(encoding="utf-8").replace("/*__DATA__*/null", payload)
    if not args.fragment:
        page = ("<!doctype html>\n<html lang=\"en\">\n<head><meta charset=\"utf-8\">"
                "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1, viewport-fit=cover\">"
                "</head>\n<body>\n" + page + "\n</body>\n</html>\n")
    args.out.write_text(page, encoding="utf-8")
    print(f"{args.out}: {len(data['nodes'])} nodes, {len(data['links'])} links, "
          f"{len(data['conflicts'])} open conflicts, {args.out.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
