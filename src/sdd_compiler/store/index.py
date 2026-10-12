"""F4 §4.4 — indexes over the graph, built in memory on load (P-10; F4 D3: no SQLite cache yet).

Every lookup a view or a query needs, computed once from the records. Deleted
nodes are in no index: they no longer exist (F2 §4.9). Lists are sorted, so any
output built from an index is deterministic.
"""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any

from ..atomize.terms import normalize_name


@dataclass
class GraphIndex:
    by_id: dict[str, dict[str, Any]] = field(default_factory=dict)
    by_term: dict[str, list[str]] = field(default_factory=dict)      # term id, and each name/alias
    by_family: dict[str | None, list[str]] = field(default_factory=dict)
    by_layer: dict[str | None, list[str]] = field(default_factory=dict)
    by_component: dict[str, list[str]] = field(default_factory=dict)
    by_status: dict[str, list[str]] = field(default_factory=dict)
    by_source: dict[str, list[str]] = field(default_factory=dict)    # file -> ids by line
    edges_out: dict[str, dict[str, list[str]]] = field(default_factory=dict)
    edges_in: dict[str, dict[str, list[str]]] = field(default_factory=dict)
    by_keyword: dict[str, list[str]] = field(default_factory=dict)
    names: dict[str, str] = field(default_factory=dict)              # normalized name -> term id

    @classmethod
    def build(cls, graph: Any) -> GraphIndex:
        index = cls()
        nodes = sorted(graph.nodes.values(), key=lambda n: n["id"])
        for node in nodes:
            node_id = node["id"]
            index.by_id[node_id] = node
            index.by_family.setdefault(node["family"], []).append(node_id)
            index.by_layer.setdefault(node["layer"], []).append(node_id)
            index.by_status.setdefault(node["status"], []).append(node_id)
            for component in node["components"]:
                index.by_component.setdefault(component, []).append(node_id)
            for keyword in node["keywords"]:
                index.by_keyword.setdefault(keyword, []).append(node_id)
            for term in sorted({t["term"] for t in node["terms"]}):
                index.by_term.setdefault(term, []).append(node_id)

        for term in sorted(graph.terms.values(), key=lambda t: t["id"]):
            for name in [term["id"].removeprefix("term:"), term["canonical"], *term.get("aliases", [])]:
                index.names.setdefault(normalize_name(name.replace("_", " ")), term["id"])
            users = index.by_term.get(term["id"], [])
            for name in [term["canonical"], *term.get("aliases", [])]:
                if name not in index.by_term:
                    index.by_term[name] = users

        by_line: dict[str, list[tuple[int, str]]] = {}
        for node in nodes:
            by_line.setdefault(node["source"]["file"], []).append((node["source"]["lines"][0], node["id"]))
        index.by_source = {f: [i for _, i in sorted(pairs)] for f, pairs in sorted(by_line.items())}

        for link in sorted(graph.links, key=lambda l: (l["from"], l["type"], l["to"])):
            index.edges_out.setdefault(link["from"], {}).setdefault(link["type"], []).append(link["to"])
            index.edges_in.setdefault(link["to"], {}).setdefault(link["type"], []).append(link["from"])
        return index

    def family_of(self, name: str) -> str | None:
        """A family from its id, its name, or an alias; `global` names `(global)`, and the map's
        `(no family)` row names the unplaced nodes, returned as `None`. Unknown: `KeyError`."""
        text = name.strip()
        if text in self.by_family:
            return text
        if text.lower() in ("global", "(global)", "_global"):
            text = "(global)"
        elif text.lower() in ("no family", "(no family)", "_unplaced", "unplaced"):
            text = None
        else:
            text = self.names.get(normalize_name(text.removeprefix("term:").replace("_", " ")), "")
        if text in self.by_family:
            return text
        raise KeyError(name)


def counts(graph: Any) -> Mapping[str, Any]:
    """The node counts `sddc status` reports (T13)."""
    index = GraphIndex.build(graph)
    return {
        "nodes": len(index.by_id),
        "by_status": {status: len(ids) for status, ids in sorted(index.by_status.items())},
        "families": sum(1 for f in index.by_family if f and f.startswith("term:")),
        "open_conflicts": sum(1 for c in graph.conflicts.values() if c["state"] == "open"),
        "attention_items": sum(1 for r in graph.reviews.values() if r["state"] == "open"),
    }
