"""F4 — the graph on disk: family shards, derived files, checks, one transaction.

```
.sdd/terms.jsonl  nodes/<family>.jsonl  edges/<family>.jsonl  conflicts.jsonl
     conflicted_nodes.json  review.jsonl  graph.meta.json
```

Writing is all or nothing (§4.2): derive what is derived (status, conflict
fields, the registry, counts), validate every record against F2, run every
consistency check (§4.3), stage every file, then rename them together. A
violation aborts with exit 4 and names every problem, not just the first.

Reading is the reverse, and `check_store` runs the same checks on what is on
disk, so a hand-edited or damaged store is caught (AC-4.7, AC-4.8).
"""
from __future__ import annotations

import json
import re
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .. import __version__
from ..errors import ExitCode, SddcError
from ..model.schema import CONFLICT_SCHEMA, LINK_SCHEMA, NODE_SCHEMA, TERM_SCHEMA, RecordError, validate
from ..model.status import derive_status, refresh_conflict_fields
from .jsonl import read_jsonl
from .transaction import Transaction

NODE_KEYS = tuple(NODE_SCHEMA["properties"])
TERM_KEYS = tuple(TERM_SCHEMA["properties"])
LINK_KEYS = tuple(LINK_SCHEMA["properties"])
CONFLICT_KEYS = tuple(CONFLICT_SCHEMA["properties"])
REVIEW_KEYS = ("id", "type", "subject", "detail", "source", "state", "opened_run", "closed_run")

QUESTION_SCHEMAS = {"q-atom": "q-atom/1", "q-desc": "q-desc/1", "q-term": "q-term/1"}
COUNTER_KEYS = ("node", "conflict", "judgment", "review")
_COUNTER_PREFIX = {"node": "N-", "conflict": "CF-", "judgment": "J-", "review": "RV-"}
_LINK_SORT = staticmethod(lambda link: (link["from"], link["type"], link["to"]))


@dataclass
class Graph:
    nodes: dict[str, dict[str, Any]] = field(default_factory=dict)
    terms: dict[str, dict[str, Any]] = field(default_factory=dict)
    links: list[dict[str, Any]] = field(default_factory=list)
    conflicts: dict[str, dict[str, Any]] = field(default_factory=dict)
    reviews: dict[str, dict[str, Any]] = field(default_factory=dict)
    counters: dict[str, int] = field(default_factory=lambda: dict.fromkeys(COUNTER_KEYS, 0))


def shard_name(family: str | None) -> str:
    """F4 §4.1, D4: `term:share_link` → `share_link.jsonl`; `(global)`, null → reserved names."""
    if family is None:
        return "_unplaced.jsonl"
    if family == "(global)":
        return "_global.jsonl"
    return f"{family.removeprefix('term:')}.jsonl"


# -- reading --------------------------------------------------------------------

@dataclass
class _Loaded:
    graph: Graph
    placement: list[tuple[str, str, str | None]]   # (node id, shard read from, its family) — every copy
    duplicates: list[str]
    registry: dict[str, Any] | None
    meta: dict[str, Any] | None


def load_graph(store: Path) -> Graph:
    return _load(Path(store)).graph


def _load(store: Path) -> _Loaded:
    graph, placement, duplicates = Graph(), [], []
    first_seen: dict[str, str] = {}
    for shard in sorted((store / "nodes").glob("*.jsonl")) if (store / "nodes").is_dir() else []:
        for record in read_jsonl(shard):
            placement.append((record["id"], shard.name, record.get("family")))
            if record["id"] in graph.nodes:
                duplicates.append(f"node {record['id']} in {first_seen[record['id']]} and {shard.name}")
                continue
            graph.nodes[record["id"]] = record
            first_seen[record["id"]] = shard.name
    for shard in sorted((store / "edges").glob("*.jsonl")) if (store / "edges").is_dir() else []:
        graph.links += read_jsonl(shard)
    graph.links.sort(key=lambda link: (link["from"], link["type"], link["to"]))
    graph.terms = {t["id"]: t for t in read_jsonl(store / "terms.jsonl")}
    graph.conflicts = {c["id"]: c for c in read_jsonl(store / "conflicts.jsonl")}
    graph.reviews = {r["id"]: r for r in read_jsonl(store / "review.jsonl")}
    meta = _read_json(store / "graph.meta.json")
    if meta:
        graph.counters = {key: meta["id_counters"].get(key, 0) for key in COUNTER_KEYS}
    return _Loaded(graph, placement, duplicates, _read_json(store / "conflicted_nodes.json"), meta)


def _read_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SddcError(f"{path.name} is not valid JSON: {exc}", ExitCode.STORE) from exc


# -- deleting (F2 §4.9) ------------------------------------------------------------

def delete_node(graph: Graph, node_id: str, run_id: str) -> None:
    """Remove a node and everything that pointed at it, in memory; `write_graph` persists it.

    ⚑ F2 D14: a conflict record left with fewer than two members is resolved
    (`member_deleted`) and keeps its member list as history; an open record
    never lists a deleted node.
    """
    graph.nodes.pop(node_id)
    for link in graph.links:
        if node_id in (link["from"], link["to"]) and link["provenance"] == "judgment":
            other = link["to"] if link["from"] == node_id else link["from"]
            if other in graph.nodes:
                reason = {"link": [link["from"], link["type"], link["to"]], "since_run": run_id}
                neighbour = graph.nodes[other]
                graph.nodes[other] = {**neighbour, "stale_reasons": [*neighbour["stale_reasons"], reason]}
    graph.links = [l for l in graph.links if node_id not in (l["from"], l["to"])]

    for cf_id, record in list(graph.conflicts.items()):
        if record["state"] != "open" or node_id not in record["members"]:
            continue
        remaining = [m for m in record["members"] if m != node_id]
        if len(remaining) >= 2:
            graph.conflicts[cf_id] = {**record, "members": remaining}
        else:
            graph.conflicts[cf_id] = {**record, "state": "resolved",
                                      "resolved_reason": "member_deleted", "resolved_run": run_id}
    _derive(graph)


def _derive(graph: Graph) -> None:
    records = list(graph.conflicts.values())
    graph.nodes = {nid: refresh_conflict_fields(node, records) for nid, node in graph.nodes.items()}


# -- writing -----------------------------------------------------------------------------

def write_graph(store: Path, graph: Graph, transaction: Transaction | None = None,
                sources: Mapping[str, str] | None = None,
                other_counters: Mapping[str, int] | None = None,
                staged_judgments: Iterable[str] = ()) -> None:
    """Derive, validate, check, then stage every graph file (and commit, unless a caller's
    transaction is given — `compile` also stages `blocks.jsonl` in the same one)."""
    store = Path(store)
    _derive(graph)
    problems = _validate_records(graph)
    previous = _read_json(store / "graph.meta.json")
    problems += _checks(graph, placement=None, duplicates=[], registry=None, meta=None,
                        previous_counters=(previous or {}).get("id_counters"),
                        judgment_ids=_judgment_ids(store) | set(staged_judgments))
    if problems:
        raise SddcError("graph not written — " + "; ".join(problems), ExitCode.STORE)

    own = transaction is None
    transaction = transaction or Transaction(store)
    try:
        _stage(store, graph, transaction, sources, other_counters)
    except BaseException:
        if own:
            transaction.rollback()
        raise
    if own:
        transaction.commit()


def _stage(store: Path, graph: Graph, tx: Transaction, sources: Mapping[str, str] | None,
           other_counters: Mapping[str, int] | None) -> None:
    shards: dict[str, list[dict[str, Any]]] = {}
    for node in graph.nodes.values():
        shards.setdefault(shard_name(node["family"]), []).append(node)
    edge_shards: dict[str, list[dict[str, Any]]] = {}
    for link in graph.links:
        edge_shards.setdefault(shard_name(graph.nodes[link["from"]]["family"]), []).append(link)

    for folder, groups, keys, sort in (("nodes", shards, NODE_KEYS, None),
                                       ("edges", edge_shards, LINK_KEYS, _LINK_SORT.__func__)):
        existing = {p.name for p in (store / folder).glob("*.jsonl")} if (store / folder).is_dir() else set()
        for name, records in groups.items():
            tx.write_jsonl(f"{folder}/{name}", records, keys, sort_key=sort)
        for name in existing - set(groups):
            tx.delete(f"{folder}/{name}")

    tx.write_jsonl("terms.jsonl", graph.terms.values(), TERM_KEYS)
    tx.write_jsonl("conflicts.jsonl", graph.conflicts.values(), CONFLICT_KEYS)
    tx.write_jsonl("review.jsonl", graph.reviews.values(), REVIEW_KEYS)
    tx.write_text("conflicted_nodes.json", _dump(registry_of(graph)))
    tx.write_text("graph.meta.json", _dump(_meta(graph, sources or {}, other_counters or {})))
    from ..views.render import stage_views          # the views read the index, which reads us
    stage_views(tx, store, graph)


def registry_of(graph: Graph) -> dict[str, Any]:
    """CT-4.2 — derived from the nodes' facts, never edited, never from a stored status."""
    nodes = [
        {"id": n["id"], "family": n["family"], "layer": n["layer"],
         "source": {"file": n["source"]["file"], "lines": n["source"]["lines"]},
         "conflict_ids": n["conflict_ids"]}
        for n in sorted(graph.nodes.values(), key=lambda n: n["id"]) if derive_status(n) == "conflict"
    ]
    return {"count": len(nodes), "nodes": nodes}


def _meta(graph: Graph, sources: Mapping[str, str], other_counters: Mapping[str, int]) -> dict[str, Any]:
    by_status: dict[str, int] = {}
    for node in graph.nodes.values():
        by_status[node["status"]] = by_status.get(node["status"], 0) + 1
    return {
        "schema_version": "graph/1",
        "compiler_version": __version__,
        "question_schemas": QUESTION_SCHEMAS,
        "layer_mapping_version": "layers/1",
        "sources": dict(sorted(sources.items())),
        "counts": {"nodes": len(graph.nodes), "terms": len(graph.terms), "links": len(graph.links),
                   "open_conflicts": sum(1 for c in graph.conflicts.values() if c["state"] == "open"),
                   "by_status": dict(sorted(by_status.items()))},
        "id_counters": {**{key: graph.counters.get(key, 0) for key in COUNTER_KEYS},
                        **{key: other_counters[key] for key in ("block", "run") if key in other_counters}},
    }


def _dump(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=1) + "\n"


# -- checking --------------------------------------------------------------------------------

def check_store(store: Path) -> list[str]:
    """Every §4.3 violation in what is on disk (the function behind the deferred `sddc check`)."""
    store = Path(store)
    loaded = _load(store)
    return _validate_records(loaded.graph, stored=True) + _checks(
        loaded.graph, loaded.placement, loaded.duplicates, loaded.registry, loaded.meta,
        previous_counters=None, judgment_ids=_judgment_ids(store))


def _validate_records(graph: Graph, stored: bool = False) -> list[str]:
    problems = []
    for kind, records in (("node", graph.nodes.values()), ("term", graph.terms.values()),
                          ("link", graph.links), ("conflict", graph.conflicts.values())):
        for record in records:
            try:
                validate(kind, record)
            except RecordError as error:
                if stored and "status: stored" in str(error):
                    continue            # reported once, by the "status derived" check
                problems.append(f"record: {error}")
    return problems


def _checks(graph: Graph, placement: Iterable[tuple[str, str, str | None]] | None,
            duplicates: Iterable[str],
            registry: Mapping[str, Any] | None, meta: Mapping[str, Any] | None,
            previous_counters: Mapping[str, int] | None, judgment_ids: set[str]) -> list[str]:
    problems = [f"unique ids: {d}" for d in duplicates]

    targets = set(graph.nodes) | set(graph.terms) | {"scope"}
    for link in graph.links:
        missing = [end for end in (link["from"], link["to"]) if end not in targets]
        if missing or link["from"] not in graph.nodes:
            problems.append(f"links resolve: {link['from']} -{link['type']}-> {link['to']} "
                            f"points at {', '.join(missing or [link['from']])}, which does not exist")

    for node in graph.nodes.values():
        if node["status"] != derive_status(node):
            problems.append(f"status derived: {node['id']} stores {node['status']!r}, "
                            f"its facts derive {derive_status(node)!r}")

    for record in graph.conflicts.values():
        if record["state"] != "open":
            continue
        for member in record["members"]:
            if member not in graph.nodes:
                problems.append(f"conflict membership: {record['id']} lists {member}, which does not exist")
            elif record["id"] not in graph.nodes[member]["conflict_ids"]:
                problems.append(f"conflict membership: {member} does not list open record {record['id']}")
    for node in graph.nodes.values():
        for cf_id in node["conflict_ids"]:
            record = graph.conflicts.get(cf_id)
            if record is None or record["state"] != "open" or node["id"] not in record["members"]:
                problems.append(f"conflict membership: {node['id']} lists {cf_id}, "
                                f"which is not an open record naming it")

    if registry is not None and registry != registry_of(graph):
        problems.append("registry derived: conflicted_nodes.json differs from the nodes with status conflict")

    for node_id, shard, family in placement or ():
        expected = shard_name(family)
        if shard != expected:
            problems.append(f"shard placement: {node_id} is in nodes/{shard}, its family belongs in nodes/{expected}")

    referenced = [(n["id"], j) for n in graph.nodes.values() for j in n["judgments"]]
    referenced += [(f"link {l['from']}->{l['to']}", l["judgment"]) for l in graph.links if l["judgment"]]
    referenced += [(c["id"], c["judgment"]) for c in graph.conflicts.values()]
    for owner, judgment in referenced:
        if judgment not in judgment_ids:
            problems.append(f"judgment references: {owner} cites {judgment}, which is not in the lock")

    counters = (meta or {}).get("id_counters") or graph.counters
    for key in COUNTER_KEYS:
        highest = _highest(key, graph, judgment_ids)
        value = counters.get(key, 0)
        if value < highest:
            problems.append(f"counters monotonic: id_counters.{key} is {value}, below the highest id issued ({highest})")
        if previous_counters is not None and value < previous_counters.get(key, 0):
            problems.append(f"counters monotonic: id_counters.{key} would fall from "
                            f"{previous_counters[key]} to {value}")
    return problems


def _highest(key: str, graph: Graph, judgment_ids: Iterable[str] = ()) -> int:
    # Judgment ids live in the lock, not the graph (I-83: an empty stand-in hid a lagging counter).
    ids: Iterable[str] = {"node": graph.nodes, "conflict": graph.conflicts, "review": graph.reviews,
                          "judgment": judgment_ids}[key]
    pattern = re.compile(re.escape(_COUNTER_PREFIX[key]) + r"(\d+)$")
    return max((int(m.group(1)) for i in ids if (m := pattern.match(i))), default=0)


def _judgment_ids(store: Path) -> set[str]:
    folder = store / "lock"
    if not folder.is_dir():
        return set()
    return {record["id"] for path in sorted(folder.glob("*.jsonl")) for record in read_jsonl(path)}
