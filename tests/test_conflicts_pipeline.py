"""T17 — F6 §4.1, §4.5 … §4.7: the check phase and the conflict lifecycle.

Covers AC-6.9, AC-6.12 … AC-6.16, AC-6.18, AC-6.19. No live model: the fake backend answers.

Tier: unit, integration, contract.
"""
from __future__ import annotations

import pytest

from sdd_compiler.atomize.lock import JudgmentLock
from sdd_compiler.conflicts.pipeline import check
from sdd_compiler.errors import ExitCode, SddcError
from sdd_compiler.llm import CallBudget, FakeBackend
from sdd_compiler.model.status import derive_status
from sdd_compiler.profile import DEFAULT_CONFLICTS, DEFAULT_RETRIEVAL, ConflictSettings, RetrievalSettings
from sdd_compiler.store.graph import Graph

RETRIEVAL = RetrievalSettings(**DEFAULT_RETRIEVAL)
CONFLICTS = ConflictSettings(**DEFAULT_CONFLICTS)


def node(node_id, text, *, status="unchecked", line=5, family="term:share_link", quantities=()):
    record = {
        "id": node_id, "kind": "requirement", "text": text, "layer": "L1", "family": family,
        "canonical": {"state": None, "trigger": None, "scope": None, "subject": "share link",
                      "modality": "MUST", "response": text, "quantities": list(quantities)},
        "source": {"file": "specs/sharing.md", "block_id": f"B-{line:06d}", "heading_path": ["Sharing"],
                   "lines": [line, line], "spans": [[0, len(text)]]},
        "terms": [{"term": "term:share_link", "role": "subject", "quote": "share link"}],
        "label": None, "primary_term": family, "layer_answers": {}, "layer_hint": None,
        "family_rule": "subject", "components": [], "verifies": None, "scope_selector": None,
        "decision": None, "annotations": [], "keywords": [], "ambiguity": [], "conflict_ids": [],
        "related_conflict_nodes": [], "stale_reasons": [], "last_checked_run": None, "flags": [],
        "status": status, "judgments": [],
    }
    if status == "ambiguous":
        record["ambiguity"] = [{"kind": "vague_term", "quote": None, "detail": "vague"}]
    record["status"] = derive_status(record)
    return record


def term(term_id="term:share_link"):
    return {"id": term_id, "canonical": "share link", "aliases": [], "kind": "entity",
            "definition": None, "defined_by": None, "status": "confirmed", "broader": None}


def graph_of(*nodes, conflicts=()):
    return Graph(nodes={n["id"]: n for n in nodes}, terms={term()["id"]: term()},
                 links=[], conflicts={c["id"]: c for c in conflicts}, reviews={},
                 counters={"node": len(nodes), "conflict": len(conflicts), "judgment": 0, "review": 0})


def answer(relation="contradicts", quote_a=None, quote_b=None, direction="symmetric",
           confidence="high", rationale="both set the lifetime, to different values"):
    # "share link" is in every node's text here, so an answer fits whichever pair it lands on:
    # the fake backend answers in the order retrieval proposes, which the test does not fix.
    return {"relation": relation, "direction": direction, "rationale": rationale,
            "quotes": {"a": quote_a or "share link", "b": quote_b or "share link"},
            "confidence": confidence}


A = "A share link expires 30 days after it is created."
B = "A share link is valid for one hour."


class Judge:
    """A fake that answers a *batch* of pairs, as Q-PAIR is asked since R21.

    `answers` are consumed one per pair, in the order the pairs are asked about, so a test still
    scripts "the first verdict, the second verdict…"; pairs beyond the script get `none`.
    """

    name = "fake"

    def __init__(self, answers, budget=None):
        self._answers = list(answers)
        self.budget = budget
        self.asked = []

    def ask(self, question):
        if self.budget is not None:
            self.budget.spend()
        self.asked.append(question)
        pairs = []
        for pair_id in question.payload["pair_ids"]:
            entry = self._answers.pop(0) if self._answers else answer(relation="none")
            pairs.append({**entry, "pair_id": pair_id})
        from sdd_compiler.llm import Answer
        return Answer(data={"pairs": pairs}, backend="fake", model="fake",
                      usage={"input_tokens": 0, "output_tokens": 0, "cache_read_tokens": 0,
                             "cache_creation_tokens": 0},
                      cost_usd=0.0, duration_ms=0, cli_version=None)


def run_check(graph, answers, lock, *, budget=None, run_id="R-000002"):
    backend = Judge(list(answers), budget=budget)
    return check(graph, backend=backend, retrieval=RETRIEVAL, settings=CONFLICTS,
                 run_id=run_id, lock=lock), backend


@pytest.fixture()
def lock(tmp_path):
    return JudgmentLock(tmp_path / ".sdd", start=0, run_id="R-000002")


# -- R21 (A): Q-PAIR is batched, as Q-ATOM and Q-DESC already are (rel01 D30) ---------------

def many_nodes(count):
    texts = [f"A share link rule number {n}, about links and archives." for n in range(count)]
    return [node("N-%06d" % (n + 1), t, line=n + 1) for n, t in enumerate(texts)]


def test_r21_one_call_carries_many_pairs(lock):
    graph = graph_of(*many_nodes(6))                       # 6 nodes → 15 pairs
    answers = [answer(relation="none")] * 15
    result, backend = run_check(graph, answers, lock)
    assert result.counts["pairs_judged"] == 15
    assert len(backend.asked) == 2                          # ceil(15 / 8), not 15
    assert all(q.kind == "q-pair" for q in backend.asked)
    assert result.counts["calls"] == 2


def test_r21_a_pair_whose_answer_fails_is_re_asked_alone(lock):
    graph = graph_of(*many_nodes(4))                        # 6 pairs, one call
    bad = answer(quote_a="this phrase is not in the node")
    result, backend = run_check(graph, [bad, answer(relation="none")], lock)
    assert len(backend.asked) == 2                          # the batch, then one pair alone
    assert result.counts["pairs_judged"] == 6               # the re-ask fixed the whole batch's item
    assert result.counts["unjudged_failed"] == 0


def test_r21_a_batch_still_replays_pair_by_pair(lock, tmp_path):
    graph = graph_of(*many_nodes(5))                        # 10 pairs
    first, backend = run_check(graph, [answer(relation="none")] * 10, lock)
    assert first.counts["pairs_judged"] == 10 and len(backend.asked) == 2

    again = JudgmentLock(tmp_path / ".sdd", start=lock.counter, run_id="R-000003")
    again.records = dict(lock.records)
    second, backend = run_check(graph, [], again, run_id="R-000003")
    assert backend.asked == []
    assert second.counts["pairs_replayed"] == 10


def test_r21_a_budget_that_runs_out_keeps_the_batches_already_judged(lock):
    graph = graph_of(*many_nodes(6))                        # 15 pairs → 2 calls
    result, backend = run_check(graph, [answer(relation="none")] * 15, lock, budget=CallBudget(1))
    assert len(backend.asked) == 1
    assert result.incomplete is True and result.stopped == "call_cap"
    assert result.counts["pairs_judged"] == 8               # the first batch is kept
    assert result.unjudged == 7


# -- AC-6.9 the phase never stops at a conflict -------------------------------------------

def test_ac_6_9_every_pair_is_judged_and_two_records_open(lock):
    texts = [A, B, "A share link may be revoked.", "A share link is valid for one week.",
             "Only the owner may revoke a share link."]
    graph = graph_of(*[node("N-%06d" % (n + 1), t, line=n + 1) for n, t in enumerate(texts)])
    answers = [answer(relation="none")] * 10
    answers[1] = answer()
    answers[3] = answer()
    result, backend = run_check(graph, answers, lock)

    assert len(backend.asked) == 2                          # 10 pairs, batched 8 at a time (R21)
    assert len(result.conflicts) == 2
    assert result.counts["pairs_judged"] == 10
    assert result.counts["by_relation"]["contradicts"] == 2
    assert result.counts["by_relation"]["none"] == 8
    assert result.counts["opened"] == 2
    assert result.incomplete is False


def test_r19_the_phase_tells_the_judge_how_the_two_namings_relate(lock):
    """F6 D17: the graph already knows `export_archive` and `workspace_export` are kinds of
    `export` (F2 D16). The judge refused such a pair for lack of that fact (I-76)."""
    a_node = node("N-000001", A, line=1, family="term:export_archive")
    b_node = node("N-000002", B, line=2, family="term:workspace_export")
    for record, term in ((a_node, "term:export_archive"), (b_node, "term:workspace_export")):
        record["terms"] = [{"term": term, "role": "subject", "quote": "export"}]
    graph = graph_of(a_node, b_node)
    graph.terms = {
        "term:export": {"id": "term:export", "canonical": "export", "aliases": [], "kind": "entity",
                        "definition": None, "defined_by": None, "status": "confirmed", "broader": None},
        "term:export_archive": {"id": "term:export_archive", "canonical": "export archive",
                                "aliases": [], "kind": "entity", "definition": None, "defined_by": None,
                                "status": "confirmed", "broader": "term:export"},
        "term:workspace_export": {"id": "term:workspace_export", "canonical": "workspace export",
                                  "aliases": [], "kind": "entity", "definition": None, "defined_by": None,
                                  "status": "confirmed", "broader": "term:export"},
    }
    _, backend = run_check(graph, [answer()], lock)
    [question] = backend.asked
    assert "HOW THEIR TERMS RELATE" in question.prompt
    assert "term:export_archive" in question.prompt and "kinds of term:export" in question.prompt


# -- AC-6.12 the budget stops the phase without losing what it judged ----------------------

def test_ac_6_12_an_exhausted_budget_keeps_what_was_judged_and_says_it_is_incomplete(lock):
    graph = graph_of(node("N-000001", A, line=1), node("N-000002", B, line=2),
                     node("N-000003", "A share link may be revoked.", line=3))
    budget = CallBudget(0)                                   # nothing left for the check phase
    result, backend = run_check(graph, [answer()] * 3, lock, budget=budget)

    assert backend.asked == []
    assert result.incomplete is True
    assert result.counts["pairs_judged"] == 0
    assert result.unjudged == 3
    assert result.counts["incomplete"] is True
    assert result.conflicts == {}                           # nothing judged, nothing invented


def test_the_stop_says_which_limit_stopped_it(lock):
    """M4 gate (I-72): the fixture run stopped after 72 of 123 pairs with 93 of 200 calls used —
    a backend 429, reported as "the call cap stopped the run" and exit 5. A report that names the
    wrong cause sends the reader to the wrong fix."""
    graph = graph_of(node("N-000001", A, line=1), node("N-000002", B, line=2))
    backend = FakeBackend([], budget=CallBudget(0))
    result = check(graph, backend=backend, retrieval=RETRIEVAL, settings=CONFLICTS,
                   run_id="R-000002", lock=lock)
    assert result.incomplete and result.stopped == "call_cap"

    class Refusing:
        name = "fake"

        def ask(self, question):
            raise SddcError("claude exited 1: session limit (API status 429)", ExitCode.BACKEND)

    again = check(graph, backend=Refusing(), retrieval=RETRIEVAL, settings=CONFLICTS,
                  run_id="R-000002", lock=lock)
    assert again.stopped == "backend"
    assert "429" in again.stop_reason


# -- AC-6.13 replay: a second run asks nothing ---------------------------------------------

def test_ac_6_13_a_second_run_replays_every_verdict_without_a_call(lock, tmp_path):
    graph = graph_of(node("N-000001", A, line=1), node("N-000002", B, line=2))
    first, _ = run_check(graph, [answer()], lock)
    assert first.counts["pairs_judged"] == 1

    replayed = JudgmentLock(tmp_path / ".sdd", start=lock.counter, run_id="R-000003")
    replayed.records = dict(lock.records)
    second, backend = run_check(graph, [], replayed, run_id="R-000003")     # no answer scripted
    assert backend.asked == []
    assert second.counts["pairs_replayed"] == 1
    assert second.counts["pairs_judged"] == 0
    assert [c["kind"] for c in second.conflicts.values()] == ["contradiction"]


# -- AC-6.14, AC-6.15, AC-6.16 the lifecycle ------------------------------------------------

def open_record(members, run="R-000001", kind="contradiction"):
    return {"id": "CF-000001", "kind": kind, "members": sorted(members),
            "rationale": "both set the lifetime", "quotes": {m: "share link" for m in members},
            "state": "open", "resolved_reason": None, "detected_run": run, "resolved_run": None,
            "judgment": "J-000001"}


def test_ac_6_14_an_edit_changes_the_pair_key_so_the_verdict_is_not_reused(lock, tmp_path):
    graph = graph_of(node("N-000001", A, line=1), node("N-000002", B, line=2))
    run_check(graph, [answer()], lock)

    edited = graph_of(node("N-000001", A, line=1),
                      node("N-000002", "A share link is valid for one day.", line=2))
    again = JudgmentLock(tmp_path / ".sdd", start=lock.counter, run_id="R-000003")
    again.records = dict(lock.records)
    result, backend = run_check(edited, [answer(quote_b="valid for one day")], again,
                                run_id="R-000003")
    assert len(backend.asked) == 1                          # the old verdict does not fit the new key
    assert result.counts["pairs_replayed"] == 0


def test_ac_6_15_an_edit_alone_does_not_close_a_conflict(lock):
    """F6 D4: the record closes when a re-judgement says so, never because the text moved."""
    graph = graph_of(node("N-000001", A, line=1),
                     node("N-000002", "A share link is valid for one day.", line=2),
                     conflicts=[open_record(["N-000001", "N-000002"])])
    result, _ = run_check(graph, [answer(quote_b="valid for one day")], lock)
    record = result.conflicts["CF-000001"]
    assert record["state"] == "open"
    assert record["quotes"]["N-000002"] == "valid for one day"      # new quotes, same record
    assert result.counts["closed"] == {"rejudged": 0, "member_deleted": 0}


def test_ac_6_16_a_re_judgement_that_says_none_closes_the_record(lock):
    graph = graph_of(node("N-000001", A, line=1), node("N-000002", B, line=2),
                     conflicts=[open_record(["N-000001", "N-000002"])])
    result, _ = run_check(graph, [answer(relation="none")], lock)
    record = result.conflicts["CF-000001"]
    assert (record["state"], record["resolved_reason"]) == ("resolved", "fixed")
    assert record["resolved_run"] == "R-000002"
    assert result.counts["closed"]["rejudged"] == 1


def test_a_re_judgement_that_finds_another_relation_also_closes_the_record(lock):
    graph = graph_of(node("N-000001", A, line=1), node("N-000002", B, line=2),
                     conflicts=[open_record(["N-000001", "N-000002"])])
    result, _ = run_check(graph, [answer(relation="refines", direction="a_to_b")], lock)
    assert result.conflicts["CF-000001"]["state"] == "resolved"
    assert [l["type"] for l in result.links] == ["refines"]


# -- AC-6.18 an ambiguous node is judged, provisionally --------------------------------------

def test_ac_6_18_a_verdict_touching_an_ambiguous_node_is_provisional(lock):
    graph = graph_of(node("N-000001", A, line=1, status="ambiguous"), node("N-000002", B, line=2))
    result, _ = run_check(graph, [answer()], lock)
    [record] = lock.new_records
    assert record["provisional"] is True
    assert result.counts["provisional"] == 1


def test_an_ambiguous_node_can_be_left_unjudged_by_the_profile(lock):
    graph = graph_of(node("N-000001", A, line=1, status="ambiguous"), node("N-000002", B, line=2))
    backend = FakeBackend([])
    settings = ConflictSettings(**{**DEFAULT_CONFLICTS, "judge_ambiguous": False})
    result = check(graph, backend=backend, retrieval=RETRIEVAL, settings=settings,
                   run_id="R-000002", lock=lock)
    assert backend.asked == [] and result.counts["pairs_judged"] == 0


# -- AC-6.19 the counts (CT-6.2) --------------------------------------------------------------

def test_ac_6_19_judged_plus_replayed_equals_the_candidate_pairs(lock, tmp_path):
    graph = graph_of(node("N-000001", A, line=1), node("N-000002", B, line=2),
                     node("N-000003", "A share link may be revoked.", line=3))
    first, _ = run_check(graph, [answer(relation="none")] * 3, lock)
    assert first.counts["pairs_judged"] + first.counts["pairs_replayed"] == first.counts["candidates"]

    again = JudgmentLock(tmp_path / ".sdd", start=lock.counter, run_id="R-000003")
    again.records = dict(lock.records)
    second, _ = run_check(graph, [answer(relation="none")], again, run_id="R-000003")
    assert second.counts["pairs_replayed"] == 3
    assert second.counts["pairs_judged"] + second.counts["pairs_replayed"] == second.counts["candidates"]
    assert sorted(second.counts) == ["by_relation", "calls", "candidates", "closed", "incomplete",
                                     "opened", "pairs_judged", "pairs_replayed", "provisional",
                                     "retrieval", "suppressed", "unjudged_failed"]   # F6 D12, D16


def test_a_guard_failure_on_one_pair_leaves_the_rest_judged(lock):
    """F6 §4.2: a second failed check records no verdict — and never stops the phase (D26)."""
    graph = graph_of(node("N-000001", A, line=1), node("N-000002", B, line=2),
                     node("N-000003", "A share link may be revoked.", line=3))
    bad = answer(quote_a="this is not in the node")
    # The batch of 3 consumes three answers, then the re-ask of the first consumes the fourth.
    result, backend = run_check(graph, [bad, answer(relation="none"), answer(relation="none"), bad],
                                lock)
    assert result.counts["pairs_judged"] == 2                  # the first pair failed twice
    assert result.counts["unjudged_failed"] == 1
    assert result.incomplete is False


def test_the_budget_is_shared_with_atomization(lock):
    """F6 D5: one budget for the run. A cap already spent by atomizing leaves nothing to judge."""
    graph = graph_of(node("N-000001", A, line=1), node("N-000002", B, line=2))
    budget = CallBudget(1)
    budget.spend()                                              # atomization used it
    with pytest.raises(SddcError) as error:
        budget.spend()
    assert error.value.exit_code == ExitCode.CALL_CAP
    result, backend = run_check(graph, [answer()], lock, budget=CallBudget(0))
    assert backend.asked == [] and result.incomplete is True


def test_i85_a_stopped_phase_leaves_the_nodes_it_did_not_reach_unchecked(lock):
    """AC-6.12's clause no test held: "unjudged nodes keep `unchecked` or `stale`". R18 round 6
    stopped with 1 866 pairs unjudged and marked every node checked, so the next run never saw them."""
    graph = graph_of(*many_nodes(6))                       # 15 pairs, two batches
    budget = CallBudget(1)                                  # the first batch only
    result, _ = run_check(graph, [answer(relation="none")] * 15, lock, budget=budget)
    assert result.incomplete and result.unjudged == 7
    unreached = {n for pair in result.unreached for n in pair}
    assert unreached                                        # the second batch touched some nodes
    assert not unreached & set(result.checked)             # … and none of them is discharged
    assert set(result.checked) | unreached == set(graph.nodes)


def test_ac_6_24_a_pair_that_failed_twice_is_not_counted_as_judged(lock):
    """Only a pair that received a verdict has its old links replaced (F6 D20)."""
    graph = graph_of(node("N-000001", A, line=1), node("N-000002", B, line=2))
    bad = answer(quote_a="this phrase is not in the node")
    result, _ = run_check(graph, [bad, bad], lock)
    assert result.counts["unjudged_failed"] == 1
    assert result.judged_pairs == []
    good, _ = run_check(graph, [answer()], JudgmentLock(lock.store, start=lock.counter, run_id="R-000003"))
    assert good.judged_pairs == [("N-000001", "N-000002")]
