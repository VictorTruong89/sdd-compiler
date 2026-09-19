"""T11 — `sddc compile`: ingest, atomize the pending blocks, write the graph (build plan B1).

In-process, with the fake backend: no test calls a live model (F3 D2).

Tier: integration.
"""
from __future__ import annotations

import json

import pytest

from sdd_compiler.commands import init
from sdd_compiler.errors import ExitCode
from sdd_compiler.ingest.pipeline import status
from sdd_compiler.llm import CallBudget, FakeBackend
from sdd_compiler.pipeline import compile_graph
from sdd_compiler.store.graph import check_store, load_graph
from sdd_compiler.store.jsonl import read_jsonl

EXPIRY = "A share link must expire 30 days after it is created."
REVOKE = "A share link must be revocable."
NO = {"answer": "no", "quote": None}


def desc(atom_id, quote, response):
    answers = {f"Q{n}": dict(NO) for n in range(1, 8)}
    answers["Q3"] = {"answer": "yes", "quote": quote}
    return {"atom_id": atom_id,
            "canonical": {"state": None, "trigger": None, "scope": None, "subject": "share link",
                          "modality": "MUST", "response": response},
            "layer_answers": answers,
            "terms": [{"name": "share link", "kind": "entity", "role": "subject", "quote": "share link"}],
            "ambiguity": [], "scope_layers": [], "scope_description": None,
            "verifies_text": None, "decision": None}


def atom_answer(*pairs):
    return {"blocks": [{"block_id": b, "sentences": [{"quote": q, "role": "requirement"}],
                        "atoms": [{"kind": "requirement", "quotes": [q]}]} for b, q in pairs]}


@pytest.fixture()
def repo(tmp_path):
    spec = tmp_path / "sdd" / "specs" / "F9_demo" / "spec.md"
    spec.parent.mkdir(parents=True)
    spec.write_text(f"## Sharing\n\n{EXPIRY}\n\n{REVOKE}\n", encoding="utf-8")
    init(tmp_path)
    return tmp_path


def first_compile(repo, **options):
    backend = FakeBackend([
        atom_answer(("B-000001", EXPIRY), ("B-000002", REVOKE)),
        {"atoms": [desc("B-000001#1", EXPIRY, "expire 30 days after it is created"),
                   desc("B-000002#1", REVOKE, "be revocable")]},
    ], **options)
    return compile_graph(repo, backend=backend), backend


def test_compile_writes_a_checked_graph_and_empties_the_pending_set(repo):
    result, backend = first_compile(repo)
    assert result.exit_code == ExitCode.OK
    store = repo / ".sdd"
    graph = load_graph(store)
    assert sorted(graph.nodes) == ["N-000001", "N-000002"]
    assert {n["family"] for n in graph.nodes.values()} == {"term:share_link"}
    assert (store / "nodes" / "share_link.jsonl").exists()
    assert check_store(store) == []
    assert status(repo)["counts"]["pending"] == 0                  # F1 D13: atomized_hash set
    meta = json.loads((store / "graph.meta.json").read_text())
    assert meta["id_counters"]["node"] == 2
    assert "sdd/specs/F9_demo/spec.md" in meta["sources"]


def test_a_second_compile_with_nothing_pending_asks_nothing_and_changes_nothing(repo):
    first_compile(repo)
    before = {p: p.read_bytes() for p in (repo / ".sdd").rglob("*.json*") if "runs" not in p.name}
    backend = FakeBackend([])
    result = compile_graph(repo, backend=backend)
    assert backend.asked == [] and result.exit_code == ExitCode.OK
    after = {p: p.read_bytes() for p in (repo / ".sdd").rglob("*.json*") if "runs" not in p.name}
    assert after == before


def test_an_edited_block_is_re_atomized_and_keeps_its_node_id(repo):
    first_compile(repo)
    spec = repo / "sdd" / "specs" / "F9_demo" / "spec.md"
    edited = "A share link must be revocable by its owner."
    spec.write_text(spec.read_text().replace(REVOKE, edited), encoding="utf-8")
    backend = FakeBackend([atom_answer(("B-000002", edited)),
                           {"atoms": [desc("B-000002#1", edited, "be revocable by its owner")]}])
    compile_graph(repo, backend=backend)
    graph = load_graph(repo / ".sdd")
    texts = sorted(n["text"] for n in graph.nodes.values())
    assert texts == sorted([EXPIRY, edited])
    assert graph.nodes["N-000002"]["text"] == edited                # F3 §4.6: the id survives the edit
    assert graph.counters["node"] == 2
    assert check_store(repo / ".sdd") == []


def test_a_removed_block_takes_its_nodes_with_it(repo):
    first_compile(repo)
    spec = repo / "sdd" / "specs" / "F9_demo" / "spec.md"
    spec.write_text(spec.read_text().replace(f"{REVOKE}\n", ""), encoding="utf-8")
    compile_graph(repo, backend=FakeBackend([]))
    assert sorted(load_graph(repo / ".sdd").nodes) == ["N-000001"]


def test_the_call_cap_writes_what_finished_and_exits_5(repo):
    backend = FakeBackend([atom_answer(("B-000001", EXPIRY), ("B-000002", REVOKE))],
                          budget=CallBudget(max_calls=1))
    result = compile_graph(repo, backend=backend)
    assert result.exit_code == ExitCode.CALL_CAP
    assert load_graph(repo / ".sdd").nodes == {}
    assert status(repo)["counts"]["pending"] == 2                  # nothing lost: still pending


def test_a_failed_block_stays_pending_and_is_on_the_attention_list(repo):
    bad = desc("B-000002#1", "not in the block", "be revocable")
    backend = FakeBackend([
        atom_answer(("B-000001", EXPIRY), ("B-000002", REVOKE)),
        {"atoms": [desc("B-000001#1", EXPIRY, "expire 30 days after it is created"), bad]},
        {"atoms": [bad]},
    ])
    result = compile_graph(repo, backend=backend)
    assert result.exit_code == ExitCode.OK
    reviews = read_jsonl(repo / ".sdd" / "review.jsonl")
    assert [(r["type"], r["subject"]) for r in reviews] == [("atomize_failed", "B-000002")]
    assert [p["id"] for p in status(repo)["pending"]] == ["B-000002"]


# -- attention items close when their cause is gone (F3 §4.9) ------------------------

def failing_compile(repo):
    bad = desc("B-000002#1", "not in the block", "be revocable")
    return compile_graph(repo, backend=FakeBackend([
        atom_answer(("B-000001", EXPIRY), ("B-000002", REVOKE)),
        {"atoms": [desc("B-000001#1", EXPIRY, "expire 30 days after it is created"), bad]},
        {"atoms": [bad]},
    ]))


def test_a_block_failing_again_keeps_one_open_item(repo):
    failing_compile(repo)
    bad = desc("B-000002#1", "still not in the block", "be revocable")
    compile_graph(repo, backend=FakeBackend([atom_answer(("B-000002", REVOKE)),
                                             {"atoms": [bad]}, {"atoms": [bad]}]))
    items = [r for r in read_jsonl(repo / ".sdd" / "review.jsonl") if r["type"] == "atomize_failed"]
    assert [(r["id"], r["state"]) for r in items] == [("RV-000001", "open")]
    assert "still not in the block" in items[0]["detail"]


def test_an_item_closes_when_its_block_completes(repo):
    failing_compile(repo)
    compile_graph(repo, backend=FakeBackend([atom_answer(("B-000002", REVOKE)),
                                             {"atoms": [desc("B-000002#1", REVOKE, "be revocable")]}]))
    [item] = read_jsonl(repo / ".sdd" / "review.jsonl")
    assert (item["state"], item["closed_run"]) == ("resolved", "R-000002")


# -- the run report counts the model's work (F3 §4.8) --------------------------------

def test_the_report_counts_model_calls_and_cost(repo):
    result, _ = first_compile(repo)
    summary = result.summary()
    assert summary["model_calls"] == 2
    assert summary["cost_usd"] == 0.0


# -- T12: identity across edits and the judgment lock (F3 AC-3.17 … AC-3.20) --------

import shutil  # noqa: E402

from sdd_compiler.store.graph import write_graph  # noqa: E402


def add_judged_link(repo, a, b):
    store = repo / ".sdd"
    graph = load_graph(store)
    lock_id = sorted(json.loads(l)["id"] for l in (store / "lock" / "q-atom.jsonl").read_text().splitlines())[0]
    graph.links.append({"from": a, "type": "refines", "to": b, "provenance": "judgment",
                        "judgment": lock_id, "rationale": "narrower", "quotes": []})
    write_graph(store, graph)


def test_ac_3_17_an_edited_block_keeps_its_node_id_and_marks_the_neighbour_stale(repo):
    first_compile(repo)
    add_judged_link(repo, "N-000001", "N-000002")
    spec = repo / "sdd" / "specs" / "F9_demo" / "spec.md"
    edited = "A share link must be revocable at any time."
    spec.write_text(spec.read_text().replace(REVOKE, edited), encoding="utf-8")
    result = compile_graph(repo, backend=FakeBackend([
        atom_answer(("B-000002", edited)), {"atoms": [desc("B-000002#1", edited, "be revocable at any time")]}]))

    graph = load_graph(repo / ".sdd")
    assert graph.nodes["N-000002"]["text"] == edited
    assert graph.nodes["N-000001"]["stale_reasons"] == [
        {"link": ["N-000001", "refines", "N-000002"], "since_run": "R-000002"}]
    assert [(a["node"], a["kind"]) for a in result.summary()["alignments"]] == [("N-000002", "edited")]
    assert check_store(repo / ".sdd") == []


def test_ac_3_18_a_split_keeps_one_id_and_adds_one(repo):
    first_compile(repo)
    spec = repo / "sdd" / "specs" / "F9_demo" / "spec.md"
    two = "A share link must be revocable. A revoked link must return 404."
    second = "A revoked link must return 404."
    spec.write_text(spec.read_text().replace(REVOKE, two), encoding="utf-8")
    compile_graph(repo, backend=FakeBackend([
        {"blocks": [{"block_id": "B-000002",
                     "sentences": [{"quote": REVOKE, "role": "requirement"},
                                   {"quote": second, "role": "requirement"}],
                     "atoms": [{"kind": "requirement", "quotes": [REVOKE]},
                               {"kind": "requirement", "quotes": [second]}]}]},
        {"atoms": [desc("B-000002#1", REVOKE, "be revocable"),
                   desc("B-000002#2", second, "return 404")]},
    ]))
    graph = load_graph(repo / ".sdd")
    assert graph.nodes["N-000002"]["text"] == REVOKE
    assert graph.nodes["N-000003"]["text"] == second


def test_ac_3_18_a_removed_block_deletes_its_nodes_and_stales_judged_neighbours(repo):
    first_compile(repo)
    add_judged_link(repo, "N-000001", "N-000002")
    spec = repo / "sdd" / "specs" / "F9_demo" / "spec.md"
    spec.write_text(spec.read_text().replace(f"{REVOKE}\n", ""), encoding="utf-8")
    compile_graph(repo, backend=FakeBackend([]))
    graph = load_graph(repo / ".sdd")
    assert "N-000002" not in graph.nodes
    assert graph.links == [l for l in graph.links if "N-000002" not in (l["from"], l["to"])]
    assert graph.nodes["N-000001"]["stale_reasons"][0]["link"] == ["N-000001", "refines", "N-000002"]


def graph_bytes(repo):
    store = repo / ".sdd"
    return {str(p.relative_to(store)): p.read_bytes()
            for folder in ("nodes", "edges") for p in sorted((store / folder).glob("*.jsonl"))} | {
        "terms.jsonl": (store / "terms.jsonl").read_bytes()}


def test_ac_3_19_the_same_sources_and_lock_rebuild_the_same_graph_with_no_calls(repo, tmp_path):
    first_compile(repo)
    rebuilt = tmp_path / "rebuilt"
    shutil.copytree(repo / "sdd", rebuilt / "sdd")
    init(rebuilt)
    shutil.copytree(repo / ".sdd" / "lock", rebuilt / ".sdd" / "lock")

    backend = FakeBackend([])                                  # any call fails the test
    result = compile_graph(rebuilt, backend=backend)
    assert backend.asked == []
    assert result.summary()["replayed"] == 4                    # 2 blocks (Q-ATOM) + 2 atoms (Q-DESC)
    assert graph_bytes(rebuilt) == graph_bytes(repo)


def test_ac_3_20_no_replay_asks_again(repo, tmp_path):
    first_compile(repo)
    rebuilt = tmp_path / "rebuilt"
    shutil.copytree(repo / "sdd", rebuilt / "sdd")
    init(rebuilt)
    shutil.copytree(repo / ".sdd" / "lock", rebuilt / ".sdd" / "lock")
    backend = FakeBackend([
        atom_answer(("B-000001", EXPIRY), ("B-000002", REVOKE)),
        {"atoms": [desc("B-000001#1", EXPIRY, "expire 30 days after it is created"),
                   desc("B-000002#1", REVOKE, "be revocable")]},
    ])
    compile_graph(rebuilt, backend=backend, replay=False)
    assert len(backend.asked) == 2


def test_nodes_cite_the_judgments_that_formed_them(repo):
    first_compile(repo)
    node = load_graph(repo / ".sdd").nodes["N-000001"]
    assert len(node["judgments"]) == 2
    assert check_store(repo / ".sdd") == []                     # every cited judgment is in the lock


# -- I-43: a backend failure keeps what finished ---------------------------------------

from sdd_compiler.errors import SddcError  # noqa: E402


class FailingAfter:
    """Answers `n` calls from a fake backend, then fails like a usage-limit 429."""

    name = "failing"

    def __init__(self, n, answers):
        self.inner, self.left = FakeBackend(answers), n

    def ask(self, question):
        if self.left == 0:
            raise SddcError("claude exited 1: You've hit your session limit (API status 429)",
                            ExitCode.BACKEND)
        self.left -= 1
        return self.inner.ask(question)


def test_i43_a_backend_failure_keeps_finished_chunks_and_their_answers(repo):
    backend = FailingAfter(2, [atom_answer(("B-000001", EXPIRY)),
                               {"atoms": [desc("B-000001#1", EXPIRY, "expire 30 days after it is created")]}])
    result = compile_graph(repo, backend=backend, block_batch=1)

    assert result.exit_code == ExitCode.BACKEND
    assert "session limit" in result.summary()["stop_reason"]
    assert sorted(load_graph(repo / ".sdd").nodes) == ["N-000001"]           # chunk 1 kept
    assert [p["id"] for p in status(repo)["pending"]] == ["B-000002"]       # chunk 2 still pending
    assert len((repo / ".sdd" / "lock" / "q-atom.jsonl").read_text().splitlines()) == 1
