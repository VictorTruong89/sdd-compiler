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


def no_conflicts(count: int = 8):
    """T17: `compile` now judges pairs too. These tests are about atomization, so every pair
    comes back `none`; extra answers are never used."""
    return [{"relation": "none", "direction": "symmetric", "rationale": "independent claims",
             "quotes": {"a": "share link", "b": "share link"}, "confidence": "high"}] * count


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
                   desc("B-000002#1", REVOKE, "be revocable")]}, *no_conflicts()], **options)
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
    backend = FakeBackend([*no_conflicts()])
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
                           {"atoms": [desc("B-000002#1", edited, "be revocable by its owner")]}, *no_conflicts()])
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
    compile_graph(repo, backend=FakeBackend([*no_conflicts()]))
    assert sorted(load_graph(repo / ".sdd").nodes) == ["N-000001"]


def test_the_call_cap_writes_what_finished_and_exits_5(repo):
    backend = FakeBackend([atom_answer(("B-000001", EXPIRY), ("B-000002", REVOKE)), *no_conflicts()],
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
        {"atoms": [bad]}, *no_conflicts()])
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
        {"atoms": [bad]}, *no_conflicts()]))


def test_a_block_failing_again_keeps_one_open_item(repo):
    failing_compile(repo)
    bad = desc("B-000002#1", "still not in the block", "be revocable")
    compile_graph(repo, backend=FakeBackend([atom_answer(("B-000002", REVOKE)),
                                             {"atoms": [bad]}, {"atoms": [bad]}, *no_conflicts()]))
    items = [r for r in read_jsonl(repo / ".sdd" / "review.jsonl") if r["type"] == "atomize_failed"]
    assert [(r["id"], r["state"]) for r in items] == [("RV-000001", "open")]
    assert "still not in the block" in items[0]["detail"]


def test_an_item_closes_when_its_block_completes(repo):
    failing_compile(repo)
    compile_graph(repo, backend=FakeBackend([atom_answer(("B-000002", REVOKE)),
                                             {"atoms": [desc("B-000002#1", REVOKE, "be revocable")]}, *no_conflicts()]))
    [item] = read_jsonl(repo / ".sdd" / "review.jsonl")
    assert (item["state"], item["closed_run"]) == ("resolved", "R-000002")


# -- the run report counts the model's work (F3 §4.8) --------------------------------

def test_the_report_counts_model_calls_and_cost(repo):
    result, _ = first_compile(repo)
    summary = result.summary()
    assert summary["model_calls"] == 3          # 2 to atomize, 1 to judge the pair (T17)
    assert summary["cost_usd"] == 0.0


def test_f3_d33_the_report_counts_blocks_that_formed_no_node(repo):
    """I-59: F5's seven source rows were labelled `definition` and formed nothing, and the run
    reported 65 of 65 completed. A silent zero is a failure the report must show."""
    backend = FakeBackend([
        {"blocks": [{"block_id": "B-000001", "sentences": [{"quote": EXPIRY, "role": "requirement"}],
                     "atoms": [{"kind": "requirement", "quotes": [EXPIRY]}]},
                    {"block_id": "B-000002", "sentences": [{"quote": REVOKE, "role": "definition"}],
                     "atoms": []}]},
        {"atoms": [desc("B-000001#1", EXPIRY, "expire 30 days after it is created")]}, *no_conflicts()])
    result = compile_graph(repo, backend=backend)
    summary = result.summary()
    assert (summary["completed"], summary["failed"], summary["nodes_formed"]) == (2, 0, 1)
    assert summary["empty_blocks"] == 1
    assert summary["empty"] == [{"block": "B-000002", "file": "sdd/specs/F9_demo/spec.md",
                                 "lines": [5, 5], "roles": ["definition"]}]


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
        atom_answer(("B-000002", edited)), {"atoms": [desc("B-000002#1", edited, "be revocable at any time")]}, *no_conflicts()]))

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
                   desc("B-000002#2", second, "return 404")]}, *no_conflicts()]))
    graph = load_graph(repo / ".sdd")
    assert graph.nodes["N-000002"]["text"] == REVOKE
    assert graph.nodes["N-000003"]["text"] == second


def test_ac_3_18_a_removed_block_deletes_its_nodes_and_stales_judged_neighbours(repo):
    first_compile(repo)
    add_judged_link(repo, "N-000001", "N-000002")
    spec = repo / "sdd" / "specs" / "F9_demo" / "spec.md"
    spec.write_text(spec.read_text().replace(f"{REVOKE}\n", ""), encoding="utf-8")
    compile_graph(repo, backend=FakeBackend([*no_conflicts()]))
    graph = load_graph(repo / ".sdd")
    assert "N-000002" not in graph.nodes
    assert graph.links == [l for l in graph.links if "N-000002" not in (l["from"], l["to"])]
    # The cascade records why N-000001 must be looked at again (F2 AC-2.23, tested on the store in
    # `test_store_graph.py`); the check phase in the same run looks at it and discharges the reason
    # (F6 D13). What must never happen is a node left stale with nobody scheduled to re-check it.
    assert graph.nodes["N-000001"]["stale_reasons"] == []
    assert graph.nodes["N-000001"]["last_checked_run"] == "R-000002"
    assert graph.nodes["N-000001"]["status"] != "stale"


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

    backend = FakeBackend([*no_conflicts()])                                  # any call fails the test
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
                   desc("B-000002#1", REVOKE, "be revocable")]}, *no_conflicts()])
    compile_graph(rebuilt, backend=backend, replay=False)
    assert len(backend.asked) == 3          # 2 to atomize, 1 to judge: --no-replay asks everything


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


# -- T17: the check phase inside compile (F6 §4.1, AC-6.1, AC-6.11, AC-6.13, AC-6.16) ---------

def pair(relation="contradicts", quote_a="share link", quote_b="share link", direction="symmetric"):
    return {"relation": relation, "direction": direction,
            "rationale": "both set the lifetime of a share link, to different values",
            "quotes": {"a": quote_a, "b": quote_b}, "confidence": "high"}


def compile_two_nodes(repo, *pairs, **options):
    """Both blocks atomize into one node each, then the single candidate pair is judged."""
    backend = FakeBackend([
        atom_answer(("B-000001", EXPIRY), ("B-000002", REVOKE)),
        {"atoms": [desc("B-000001#1", EXPIRY, "expire 30 days after it is created"),
                   desc("B-000002#1", REVOKE, "be revocable")]},
        *pairs,
    ], **options)
    return compile_graph(repo, backend=backend), backend


def test_ac_6_1_a_contradiction_is_written_with_its_members_and_the_registry(repo):
    result, backend = compile_two_nodes(repo, pair())
    graph = load_graph(repo / ".sdd")
    [record] = graph.conflicts.values()

    assert record["kind"] == "contradiction" and record["state"] == "open"
    assert record["members"] == sorted(graph.nodes)
    for node_id in record["members"]:
        assert graph.nodes[node_id]["conflict_ids"] == [record["id"]]
        assert graph.nodes[node_id]["status"] == "conflict"
    registry = json.loads((repo / ".sdd" / "conflicted_nodes.json").read_text())
    assert registry["count"] == 2
    assert check_store(repo / ".sdd") == []
    assert result.exit_code == ExitCode.CONFLICTS                      # AC-6.10: exit 3
    assert result.summary()["conflicts"]["opened"] == 1
    assert [l["type"] for l in graph.links if l["provenance"] == "judgment"] == ["conflicts_with"]


def test_ac_6_11_a_clean_run_says_so_and_exits_zero(repo):
    result, _ = compile_two_nodes(repo, pair(relation="none"))
    graph = load_graph(repo / ".sdd")
    assert graph.conflicts == {}
    assert result.exit_code == ExitCode.OK
    assert result.summary()["conflicts"]["by_relation"]["none"] == 1
    assert all(n["status"] == "validated" for n in graph.nodes.values())    # checked, nothing found


def test_ac_6_13_a_second_compile_judges_nothing_again(repo):
    compile_two_nodes(repo, pair())
    result, backend = compile_two_nodes(repo)                  # no pair answer scripted
    assert [q.kind for q in backend.asked] == []
    assert result.summary()["conflicts"]["pairs_replayed"] == 1
    assert result.exit_code == ExitCode.CONFLICTS              # the record is still open


def test_ac_6_16_a_re_judgement_that_says_none_closes_the_record_and_clears_the_nodes(repo):
    compile_two_nodes(repo, pair())
    spec = repo / "sdd" / "specs" / "F9_demo" / "spec.md"
    spec.write_text(f"## Sharing\n\n{EXPIRY}\n\nA share link must be revocable by its owner.\n",
                    encoding="utf-8")
    revoke = "A share link must be revocable by its owner."
    backend = FakeBackend([
        atom_answer(("B-000002", revoke)),
        {"atoms": [desc("B-000002#1", revoke, "be revocable by its owner")]},
        pair(relation="none"), *no_conflicts()])
    result = compile_graph(repo, backend=backend)
    graph = load_graph(repo / ".sdd")
    [record] = graph.conflicts.values()

    assert (record["state"], record["resolved_reason"]) == ("resolved", "fixed")
    assert all(n["conflict_ids"] == [] for n in graph.nodes.values())
    assert all(n["status"] != "conflict" for n in graph.nodes.values())
    assert json.loads((repo / ".sdd" / "conflicted_nodes.json").read_text())["count"] == 0
    assert result.exit_code == ExitCode.OK
    assert result.summary()["conflicts"]["closed"]["rejudged"] == 1


def test_ac_6_12_a_cap_reached_in_the_check_phase_reports_incomplete_and_exits_five(repo):
    result, backend = compile_two_nodes(repo, pair(), budget=CallBudget(2))   # 2 calls atomize
    assert result.exit_code == ExitCode.CALL_CAP
    summary = result.summary()
    assert summary["conflicts"]["incomplete"] is True
    assert summary["conflicts"]["unjudged"] == 1
    assert load_graph(repo / ".sdd").conflicts == {}            # nothing judged, nothing invented


def test_ac_6_17_deleting_a_member_closes_the_record_and_the_run_counts_it(repo):
    compile_two_nodes(repo, pair())
    spec = repo / "sdd" / "specs" / "F9_demo" / "spec.md"
    spec.write_text(f"## Sharing\n\n{EXPIRY}\n", encoding="utf-8")        # REVOKE removed
    result = compile_graph(repo, backend=FakeBackend([*no_conflicts()]))
    graph = load_graph(repo / ".sdd")
    [record] = graph.conflicts.values()

    assert (record["state"], record["resolved_reason"]) == ("resolved", "member_deleted")
    assert record["members"] == ["N-000001", "N-000002"]          # kept as history (F2 D14)
    assert graph.nodes["N-000001"]["conflict_ids"] == []
    assert result.summary()["conflicts"]["closed"]["member_deleted"] == 1
    assert result.exit_code == ExitCode.OK


# -- the M4 gate fixture stays alive in the suite (G4 §3 corpus 2) -----------------------------

def test_the_planted_fixture_ingests_and_still_holds_its_six_pairs(tmp_path):
    """The fixture is the denominator for M1 recall. A fixture nobody runs rots: this ingests it
    (no model call) and checks the claims the answer key names are still in the files."""
    import shutil
    from pathlib import Path as _Path
    fixture = _Path(__file__).parent / "fixtures" / "planted"
    shutil.copytree(fixture / "sdd", tmp_path / "sdd")
    init(tmp_path)
    from sdd_compiler.ingest.pipeline import ingest as ingest_only
    result = ingest_only(tmp_path, command="ingest")
    assert result.counts["new"] == 28

    # The sources are hard-wrapped, so compare on words, not on layout (the F3 D9 lesson).
    text = " ".join(" ".join((fixture / "sdd" / "specs" / p).read_text(encoding="utf-8").split())
                    for p in ("F1_exports/spec.md", "F1_exports/sharing.md", "F2_retention/spec.md"))
    for claim in ("kept for 30 days", "7 days after it was created",       # P1
                  "at most 5 GB", "at most 5 GiB",                          # P2, P5
                  "must never contain the owner's email address",           # P3
                  "email address of the member who uploaded it",
                  "Every export must be encrypted", "should be encrypted",  # P4
                  "A shared link expires 30 days"):                         # P6
        assert claim in text, claim


def test_i83_the_judgment_counter_covers_the_check_phases_records(repo):
    """The counter was saved before the check phase wrote its Q-PAIR records, so the next
    compile re-issued their ids (R18 round 7, I-83)."""
    compile_two_nodes(repo, pair())
    meta = json.loads((repo / ".sdd" / "graph.meta.json").read_text())
    issued = [json.loads(line)["id"] for path in (repo / ".sdd" / "lock").glob("*.jsonl")
              for line in path.read_text().splitlines()]
    assert meta["id_counters"]["judgment"] == max(int(i[2:]) for i in issued)
    assert check_store(repo / ".sdd") == []


def judged_keys(repo):
    graph = load_graph(repo / ".sdd")
    return [(l["from"], l["type"], l["to"]) for l in graph.links if l["provenance"] == "judgment"]


def test_i89_a_replayed_verdict_does_not_store_its_link_again(repo):
    """F2 §4.8: a link is unique per `(from, type, to)`. A `conflict` node is re-checked every run
    and its verdict replays from the lock; R18 stored `AC-3.19 refines N-000008` nine times (I-89)."""
    compile_two_nodes(repo, pair())
    compile_two_nodes(repo)                                     # replayed, no call
    compile_two_nodes(repo)
    keys = judged_keys(repo)
    assert len(keys) == len(set(keys)) == 1
    assert check_store(repo / ".sdd") == []


def test_i89_a_store_already_holding_duplicate_links_heals_on_the_next_compile(repo):
    compile_two_nodes(repo, pair())
    for shard in (repo / ".sdd" / "edges").glob("*.jsonl"):     # what an R18 store looks like
        lines = shard.read_text().splitlines()
        shard.write_text("\n".join(lines + [l for l in lines if '"judgment"' in l and '"J-' in l]) + "\n")
    assert any(v.startswith("unique ids") for v in check_store(repo / ".sdd"))
    compile_two_nodes(repo)
    keys = judged_keys(repo)
    assert len(keys) == len(set(keys)) == 1
    assert check_store(repo / ".sdd") == []


def test_i89_the_heal_also_happens_when_the_cap_stops_atomization(repo):
    compile_two_nodes(repo, pair())
    for shard in (repo / ".sdd" / "edges").glob("*.jsonl"):
        lines = shard.read_text().splitlines()
        shard.write_text("\n".join(lines + lines) + "\n")
    spec = repo / "sdd" / "specs" / "F9_demo" / "spec.md"
    spec.write_text(spec.read_text() + "\nA share link must be logged.\n", encoding="utf-8")
    result = compile_graph(repo, backend=FakeBackend([], budget=CallBudget(0)))   # stops at once
    assert result.exit_code == ExitCode.CALL_CAP
    keys = [(l["from"], l["type"], l["to"]) for l in load_graph(repo / ".sdd").links]
    assert len(keys) == len(set(keys))
    assert check_store(repo / ".sdd") == []


def rejudge(repo, verdict):
    """Edit B so the pair's key changes and it is asked again, answered with `verdict`."""
    spec = repo / "sdd" / "specs" / "F9_demo" / "spec.md"
    revoke = "A share link must be revocable by its owner."
    spec.write_text(f"## Sharing\n\n{EXPIRY}\n\n{revoke}\n", encoding="utf-8")
    compile_graph(repo, backend=FakeBackend([
        atom_answer(("B-000002", revoke)),
        {"atoms": [desc("B-000002#1", revoke, "be revocable by its owner")]},
        verdict, *no_conflicts()]))


def test_ac_6_24_a_pair_re_judged_none_keeps_no_judged_link(repo):
    """F6 D20 (I-91): the record closed on re-judgment, but its `conflicts_with` link stayed."""
    compile_two_nodes(repo, pair())
    rejudge(repo, pair(relation="none"))
    assert judged_keys(repo) == []
    assert check_store(repo / ".sdd") == []


def test_ac_6_24_a_changed_relation_replaces_the_old_link(repo):
    compile_two_nodes(repo, pair(relation="refines", direction="a_to_b"))
    rejudge(repo, pair(relation="depends_on", direction="b_to_a"))
    assert [k[1] for k in judged_keys(repo)] == ["depends_on"]
