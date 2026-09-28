"""T11 — F4 graph store: shards, meta, checks, one transaction; F2 §4.9 deletion.

Covers F4 AC-4.1 … AC-4.8 and F2 AC-2.23. `sddc check` itself is deferred (build
plan B2); its function, `check_store`, is tested here.

Tier: unit, property and integration.
"""
from __future__ import annotations

import copy
import itertools
import json
import random

import pytest

from sdd_compiler.errors import ExitCode, SddcError
from sdd_compiler.model.status import derive_status
from sdd_compiler.store.graph import (
    Graph, check_store, delete_node, load_graph, shard_name, write_graph,
)


def node(node_id, family="term:a", **extra):
    record = {
        "id": node_id, "kind": "requirement",
        "source": {"file": "spec.md", "block_id": "B-000001", "heading_path": [], "lines": [1, 1],
                   "spans": [[0, 5]]},
        "text": "Links must expire.",
        "canonical": {"state": None, "trigger": None, "scope": None, "subject": "link",
                      "modality": "MUST", "response": "expire", "quantities": []},
        "terms": [], "label": None, "primary_term": family if family and family.startswith("term:") else None,
        "layer": "L1", "layer_answers": {}, "layer_hint": None,
        "family": family, "family_rule": "subject" if family else "fallback",
        "components": [], "scope_selector": None, "verifies": None, "decision": None,
        "annotations": [], "keywords": ["expire", "links"],
        "ambiguity": [] if family else [{"kind": "unresolved_term", "quote": None, "detail": "x"}],
        "conflict_ids": [], "related_conflict_nodes": [], "stale_reasons": [],
        "last_checked_run": "R-0001", "flags": [], "status": "validated", "judgments": [],
    }
    record.update(extra)
    record["status"] = derive_status(record)
    return record


def term(term_id):
    return {"id": term_id, "canonical": term_id[5:].replace("_", " "), "aliases": [],
            "kind": "entity", "definition": None, "defined_by": None, "status": "proposed", "broader": None}


def link(a, kind, b, judged=False):
    return {"from": a, "type": kind, "to": b, "provenance": "judgment" if judged else "code",
            "judgment": None, "rationale": "because" if judged else None, "quotes": []}


def conflict(cf_id, members, state="open"):
    return {"id": cf_id, "kind": "contradiction", "members": sorted(members), "rationale": "r",
            "quotes": {}, "state": state, "resolved_reason": None, "detected_run": "R-0001",
            "resolved_run": None, "judgment": "J-000001"}


def graph(nodes=(), terms=(), links=(), conflicts=(), counters=None):
    return Graph(nodes={n["id"]: n for n in nodes}, terms={t["id"]: t for t in terms},
                 links=list(links), conflicts={c["id"]: c for c in conflicts}, reviews={},
                 counters=counters or {"node": 9, "conflict": 9, "judgment": 9, "review": 0})


@pytest.fixture()
def store(tmp_path):
    """A store whose judgment lock holds J-000001 — the judgment the conflict fixtures cite."""
    (tmp_path / ".sdd" / "lock").mkdir(parents=True)
    (tmp_path / ".sdd" / "lock" / "q-pair.jsonl").write_text('{"id": "J-000001"}\n')
    return tmp_path / ".sdd"


# -- AC-4.1 / AC-4.2 shards ----------------------------------------------------

def test_ac_4_1_nodes_are_sharded_by_family(store):
    write_graph(store, graph([node("N-000001", "term:a"), node("N-000002", "(global)"),
                              node("N-000003", None)], [term("term:a")]))
    assert {p.name for p in (store / "nodes").iterdir()} == {"a.jsonl", "_global.jsonl", "_unplaced.jsonl"}
    assert shard_name("term:share_link") == "share_link.jsonl"


def test_ac_4_2_a_family_move_moves_the_node_and_its_links(store):
    a = node("N-000001", "term:a")
    write_graph(store, graph([a, node("N-000002", "term:a")], [term("term:a"), term("term:b")],
                             [link("N-000001", "uses_term", "term:a")]))
    loaded = load_graph(store)
    loaded.nodes["N-000001"] = {**a, "family": "term:b", "primary_term": "term:b"}
    write_graph(store, loaded)

    assert "N-000001" not in (store / "nodes" / "a.jsonl").read_text()
    assert "N-000001" in (store / "nodes" / "b.jsonl").read_text()
    assert "N-000001" in (store / "edges" / "b.jsonl").read_text()
    assert not (store / "edges" / "a.jsonl").exists()


def test_an_emptied_shard_file_is_removed(store):
    write_graph(store, graph([node("N-000001", "term:a")], [term("term:a")]))
    loaded = load_graph(store)
    delete_node(loaded, "N-000001", run_id="R-0002")
    write_graph(store, loaded)
    assert not (store / "nodes" / "a.jsonl").exists()


# -- AC-4.3 determinism ------------------------------------------------------------

def test_ac_4_3_the_same_records_in_any_order_give_the_same_bytes(tmp_path):
    nodes = [node(f"N-00000{i}", "term:a" if i % 2 else "term:b") for i in range(1, 7)]
    links = [link(n["id"], "uses_term", n["family"]) for n in nodes]
    terms = [term("term:a"), term("term:b")]
    outputs = []
    for seed in (1, 2, 3):
        rng = random.Random(seed)
        shuffled = [rng.sample(items, len(items)) for items in (nodes, terms, links)]
        store = tmp_path / f"s{seed}" / ".sdd"
        store.mkdir(parents=True)
        write_graph(store, graph(*shuffled))
        outputs.append({str(p.relative_to(store)): p.read_bytes()
                        for p in sorted(store.rglob("*")) if p.is_file()})
    assert outputs[0] == outputs[1] == outputs[2]
    assert b"20" not in outputs[0]["graph.meta.json"].replace(b"graph/1", b"")  # no timestamps


# -- AC-4.4 atomic --------------------------------------------------------------------

def test_ac_4_4_a_bad_last_record_changes_nothing(store):
    write_graph(store, graph([node("N-000001")], [term("term:a")]))
    before = {p: p.read_bytes() for p in store.rglob("*") if p.is_file()}
    bad = node("N-000002")
    bad["layer"] = "L9"
    with pytest.raises(SddcError) as error:
        write_graph(store, graph([node("N-000001"), bad], [term("term:a")]))
    assert error.value.exit_code is ExitCode.STORE
    assert "N-000002" in str(error.value)
    after = {p: p.read_bytes() for p in store.rglob("*") if p.is_file()}
    assert after == before


# -- AC-4.5 … AC-4.8 checks and registry ---------------------------------------------------

def test_ac_4_5_a_dangling_link_aborts_naming_it(store):
    with pytest.raises(SddcError) as error:
        write_graph(store, graph([node("N-000001")], [term("term:a")],
                                 [link("N-000001", "refines", "N-000404", judged=True)]))
    assert error.value.exit_code is ExitCode.STORE
    assert "N-000404" in str(error.value)


def test_ac_4_6_the_registry_follows_the_conflict_records(store):
    nodes = [node("N-000001"), node("N-000002"), node("N-000003")]
    write_graph(store, graph(nodes, [term("term:a")], conflicts=[conflict("CF-000001", ["N-000001", "N-000002"])]))
    registry = json.loads((store / "conflicted_nodes.json").read_text())
    assert registry["count"] == 2
    assert [(n["id"], n["conflict_ids"]) for n in registry["nodes"]] == [
        ("N-000001", ["CF-000001"]), ("N-000002", ["CF-000001"])]

    loaded = load_graph(store)
    loaded.conflicts["CF-000001"] = {**loaded.conflicts["CF-000001"], "state": "resolved",
                                     "resolved_reason": "fixed", "resolved_run": "R-0002"}
    write_graph(store, loaded)
    assert json.loads((store / "conflicted_nodes.json").read_text()) == {"count": 0, "nodes": []}
    assert load_graph(store).nodes["N-000001"]["status"] == "validated"


def test_ac_4_7_a_missing_membership_is_reported(store):
    write_graph(store, graph([node("N-000001"), node("N-000002")], [term("term:a")],
                             conflicts=[conflict("CF-000001", ["N-000001", "N-000002"])]))
    shard = store / "nodes" / "a.jsonl"
    lines = [json.loads(line) for line in shard.read_text().splitlines()]
    lines[0]["conflict_ids"] = []
    shard.write_text("".join(json.dumps(l, ensure_ascii=False) + "\n" for l in lines))
    violations = check_store(store)
    assert any("N-000001" in v and "CF-000001" in v for v in violations)


def test_ac_4_8_every_check_reports(store):
    """One violation of each of the eight checks in F4 §4.3 (the AC's "seven" predates D24)."""
    write_graph(store, graph([node("N-000001"), node("N-000002")], [term("term:a")],
                             [link("N-000001", "uses_term", "term:a")],
                             conflicts=[conflict("CF-000001", ["N-000001", "N-000002"])]))
    shard = store / "nodes" / "a.jsonl"
    records = [json.loads(line) for line in shard.read_text().splitlines()]
    duplicate = copy.deepcopy(records[1])
    records[0]["conflict_ids"] = []                          # membership (status still derives)
    records[0]["status"] = "validated"
    records[1]["status"] = "unchecked"                       # status derived: it is in a conflict
    records[1]["judgments"] = ["J-000777"]                   # judgment reference
    shard.write_text("".join(json.dumps(r) + "\n" for r in records))
    (store / "nodes" / "b.jsonl").write_text(json.dumps(duplicate) + "\n")   # duplicate + shard
    (store / "edges" / "a.jsonl").write_text(json.dumps(link("N-000001", "refines", "N-000404", True)) + "\n")
    (store / "conflicted_nodes.json").write_text('{"count": 0, "nodes": []}')
    meta = json.loads((store / "graph.meta.json").read_text())
    meta["id_counters"]["node"] = 1
    (store / "graph.meta.json").write_text(json.dumps(meta))

    violations = check_store(store)
    for check in ("unique ids", "links resolve", "status derived", "conflict membership",
                  "registry derived", "shard placement", "judgment references", "counters monotonic"):
        assert any(v.startswith(check) for v in violations), check


def test_counters_never_decrease_between_transactions(store):
    write_graph(store, graph([node("N-000001")], [term("term:a")],
                             counters={"node": 5, "conflict": 0, "judgment": 1, "review": 0}))
    with pytest.raises(SddcError) as error:
        write_graph(store, graph([node("N-000001")], [term("term:a")],
                                 counters={"node": 4, "conflict": 0, "judgment": 1, "review": 0}))
    assert "counters monotonic" in str(error.value)


# -- F2 AC-2.23 deletion cascade --------------------------------------------------------------

def test_f2_ac_2_23_deleting_a_node_cascades():
    a, b, c = node("N-000001"), node("N-000002"), node("N-000003")
    g = graph([a, b, c], [term("term:a")],
              [link("N-000001", "uses_term", "term:a"), link("N-000003", "refines", "N-000001", judged=True)],
              conflicts=[conflict("CF-000001", ["N-000001", "N-000002"])])
    for member in ("N-000001", "N-000002"):
        g.nodes[member] = {**g.nodes[member], "conflict_ids": ["CF-000001"]}

    delete_node(g, "N-000001", run_id="R-0005")

    assert "N-000001" not in g.nodes
    assert all("N-000001" not in (l["from"], l["to"]) for l in g.links)
    record = g.conflicts["CF-000001"]
    assert (record["state"], record["resolved_reason"], record["resolved_run"]) == (
        "resolved", "member_deleted", "R-0005")
    assert g.nodes["N-000002"]["status"] != "conflict"
    assert g.nodes["N-000003"]["stale_reasons"] == [
        {"link": ["N-000003", "refines", "N-000001"], "since_run": "R-0005"}]
    assert g.nodes["N-000003"]["status"] == "stale"
    assert g.counters["node"] == 9                          # never rewound


def test_a_written_graph_loads_back_equal(store):
    g = graph([node("N-000001"), node("N-000002", "(global)")], [term("term:a")],
              [link("N-000001", "uses_term", "term:a")])
    write_graph(store, g)
    loaded = load_graph(store)
    assert loaded.nodes == g.nodes and loaded.terms == g.terms and loaded.links == g.links
    assert check_store(store) == []


def test_i83_the_judgment_counter_is_checked_against_the_lock(store):
    """F4 §4.3 counters monotonic covers `judgment` too: its ids live in the lock, not the graph.
    R18 round 7 found the counter 532 behind the lock and `check_store` silent (I-83)."""
    (store / "lock" / "q-pair.jsonl").write_text('{"id": "J-000001"}\n{"id": "J-000012"}\n')
    write_graph(store, graph([node("N-000001")], [term("term:a")],
                             counters={"node": 9, "conflict": 0, "judgment": 12, "review": 0}))
    meta = json.loads((store / "graph.meta.json").read_text())
    meta["id_counters"]["judgment"] = 9
    (store / "graph.meta.json").write_text(json.dumps(meta))
    assert any(v.startswith("counters monotonic: id_counters.judgment is 9")
               for v in check_store(store))


def test_i89_a_duplicate_link_key_is_reported(store):
    """F4 §4.3 unique ids, read with F2 §4.8: a link's id is its key `(from, type, to)`."""
    write_graph(store, graph([node("N-000001"), node("N-000002")], [term("term:a")],
                             [link("N-000001", "uses_term", "term:a")]))
    shard = store / "edges" / "a.jsonl"
    shard.write_text(shard.read_text() * 2)
    assert any(v.startswith("unique ids: link N-000001 -uses_term-> term:a")
               for v in check_store(store))
