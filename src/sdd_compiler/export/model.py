"""F7 — everything the export reads, loaded once and resolved: blocks, graph, verdicts, units.

The export only reads `.sdd/` (§2 non-goal). Two things are decided here, because every file
depends on them: which blocks are **excluded as real duplicates** (D13) and each unit's place in
the build order.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from ..conflicts.adjudicate import verdicts_for
from ..errors import ExitCode, SddcError
from ..ingest.identity import heading_skipped, is_live
from ..ingest.pipeline import BLOCKS_FILE
from ..profile import STORE_DIR, Profile, load_profile
from ..store.graph import Graph, load_graph
from ..store.jsonl import read_jsonl
from .units import Order, UnitKey, Units, compute_needs, form_units, order_units

REAL_DUPLICATE = "real_duplicate"


@dataclass
class Model:
    root: Path
    profile: Profile
    graph: Graph
    blocks: dict[str, dict[str, Any]]
    verdicts: dict[str, dict[str, Any]]
    excluded: dict[str, str] = field(default_factory=dict)      # block id → reason
    keeper: dict[str, str] = field(default_factory=dict)        # node in an excluded block → kept node
    units: Units | None = None
    order: Order | None = None                                   # work units in build order
    home: dict[str, UnitKey] = field(default_factory=dict)      # node id → unit key
    omitted_nodes: list[str] = field(default_factory=list)
    needs: dict[tuple[UnitKey, UnitKey], int] = field(default_factory=dict)

    # -- lookups -----------------------------------------------------------------------

    def resolve(self, node_id: str) -> str:
        """A node in an excluded block stands for the node it duplicated (D13)."""
        while node_id in self.keeper:
            node_id = self.keeper[node_id]
        return node_id

    def open_conflicts(self) -> list[dict[str, Any]]:
        return [c for _, c in sorted(self.graph.conflicts.items()) if c["state"] == "open"]

    def links(self) -> list[dict[str, Any]]:
        """Every link between nodes that are in the export, ends resolved past exclusions."""
        out, seen = [], set()
        for link in self.graph.links:
            a, z = self.resolve(link["from"]), self.resolve(link["to"])
            if a == z or a not in self.home or (z not in self.home and z in self.graph.nodes):
                continue
            key = (a, link["type"], z)
            if key in seen:
                continue
            seen.add(key)
            out.append({**link, "from": a, "to": z})
        return out

    def node_block(self, node_id: str) -> dict[str, Any]:
        return self.blocks[self.graph.nodes[node_id]["source"]["block_id"]]


def load_model(root: Path) -> Model:
    root = Path(root)
    store = root / STORE_DIR
    profile = load_profile(root)
    graph = load_graph(store)
    blocks = {b["id"]: b for b in read_jsonl(store / BLOCKS_FILE)}
    for node in graph.nodes.values():
        block = blocks.get(node["source"]["block_id"])
        if block is None or not is_live(block):
            raise SddcError(f"{node['id']} points at block {node['source']['block_id']}, which is "
                            f"not a live block — run sddc compile first", ExitCode.STORE)
    model = Model(root, profile, graph, blocks, verdicts_for(store))
    model.excluded, model.keeper = _real_duplicates(model)
    model.units = form_units(blocks.values(), profile.export.foundation_globs,
                             profile.skip_headings, excluded=model.excluded)
    _home_nodes(model)
    model.needs = compute_needs(model.links(), model.home,
                                model.units.foundation.key if model.units.foundation else None)
    model.order = order_units(model.units.units, model.needs)
    return model


def _node_order(graph: Graph, node_id: str) -> tuple[str, int, str]:
    source = graph.nodes[node_id]["source"]
    return (source["file"], source["lines"][0], node_id)


def _real_duplicates(model: Model) -> tuple[dict[str, str], dict[str, str]]:
    """D13 — a block is excluded when every node in it is the later member of a current, `real`
    duplication whose other member sits in a different block."""
    graph = model.graph
    earlier: dict[str, list[str]] = {}
    for record in model.open_conflicts():
        verdict = model.verdicts.get(record["id"])
        if record["kind"] != "duplication" or not verdict or verdict["stale"] \
                or verdict["verdict"] != "real":
            continue
        a, z = sorted(record["members"], key=lambda m: _node_order(graph, m))[:2]
        if graph.nodes[a]["source"]["block_id"] != graph.nodes[z]["source"]["block_id"]:
            earlier.setdefault(z, []).append(a)
    by_block: dict[str, list[str]] = {}
    for node_id, node in graph.nodes.items():
        by_block.setdefault(node["source"]["block_id"], []).append(node_id)
    excluded: dict[str, str] = {}
    keeper: dict[str, str] = {}
    for block_id, node_ids in by_block.items():
        block = model.blocks[block_id]
        if heading_skipped(block["heading_path"], model.profile.skip_headings):
            continue
        if all(node_id in earlier for node_id in node_ids):
            excluded[block_id] = REAL_DUPLICATE
            for node_id in node_ids:
                keeper[node_id] = min(earlier[node_id], key=lambda m: _node_order(graph, m))
    return excluded, keeper


def _home_nodes(model: Model) -> None:
    unit_of: dict[str, UnitKey] = {}
    assert model.units is not None
    for unit in [*([model.units.foundation] if model.units.foundation else []), *model.units.units]:
        for block_id in unit.block_ids:
            unit_of[block_id] = unit.key
    for node_id, node in sorted(model.graph.nodes.items()):
        block_id = node["source"]["block_id"]
        if block_id in unit_of:
            model.home[node_id] = unit_of[block_id]
        elif block_id not in model.excluded:
            model.omitted_nodes.append(node_id)
