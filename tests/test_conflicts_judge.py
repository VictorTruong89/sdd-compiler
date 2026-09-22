"""T16 — F6 §4.2, §4.3: Q-PAIR, its guards, and what a verdict records (AC-6.1 … AC-6.8).

No live model: every answer here comes from F3's recorded fake backend.

Tier: unit, contract.
"""
from __future__ import annotations

import pytest

from sdd_compiler.atomize.guards import GuardFailure
from sdd_compiler.conflicts.judge import SCHEMA_VERSION, build_question, judge
from sdd_compiler.conflicts.records import Outcome, outcome_for
from sdd_compiler.llm import FakeBackend
from sdd_compiler.model.schema import AMBIGUITY_KINDS, validate
from sdd_compiler.profile import DEFAULT_CONFLICTS, ConflictSettings

SETTINGS = ConflictSettings(**DEFAULT_CONFLICTS)
A_TEXT = "A share link expires 30 days after it is created."
B_TEXT = "A share link is valid for one hour."


def node(node_id, text, *, layer="L1", family="term:share_link", status="unchecked",
         modality="MUST", quantities=(), line=5):
    return {
        "id": node_id, "text": text, "layer": layer, "family": family, "status": status,
        "canonical": {"state": None, "trigger": None, "scope": None, "subject": "share link",
                      "modality": modality, "response": text, "quantities": list(quantities)},
        "source": {"file": "specs/sharing.md", "block_id": "B-000001", "lines": [line, line],
                   "heading_path": ["Sharing"]},
        "terms": [{"term": "term:share_link", "role": "subject", "quote": "share link"}],
        "keywords": [], "ambiguity": [], "conflict_ids": [], "judgments": [],
    }


A = node("N-000017", A_TEXT)
B = node("N-000042", B_TEXT, line=22, quantities=[{"value": 1, "unit": "hour", "quote": "one hour",
                                                   "normalized": {"value": 3600, "unit": "s"}}])


def answer(relation="contradicts", direction="symmetric", confidence="high",
           quote_a="expires 30 days after it is created", quote_b="valid for one hour",
           rationale="both set the lifetime of a share link, to different values"):
    return {"relation": relation, "direction": direction, "rationale": rationale,
            "quotes": {"a": quote_a, "b": quote_b}, "confidence": confidence}


def verdict_for(*answers, a=A, b=B):
    backend = FakeBackend(list(answers))
    return judge(a, b, backend, settings=SETTINGS), backend


# -- the question (F6 §4.2) --------------------------------------------------------------

def test_the_question_shows_both_nodes_with_what_the_judge_needs():
    prompt = build_question(A, B).prompt
    for part in (A_TEXT, B_TEXT, "N-000017", "N-000042", "L1", "term:share_link",
                 "specs/sharing.md", "MUST"):
        assert part in prompt, part
    assert build_question(A, B).schema_version == SCHEMA_VERSION


# -- AC-6.7 the direction rule is part of the schema --------------------------------------

@pytest.mark.parametrize("relation", ["none", "duplicates", "contradicts"])
def test_ac_6_7_a_symmetric_relation_with_a_direction_is_rejected(relation):
    with pytest.raises(GuardFailure) as error:
        judge(A, B, FakeBackend([answer(relation=relation, direction="a_to_b")] * 2), settings=SETTINGS)
    assert "direction" in str(error.value).lower()


@pytest.mark.parametrize("relation", ["refines", "depends_on", "subsumes"])
def test_a_directed_relation_keeps_its_direction(relation):
    verdict, _ = verdict_for(answer(relation=relation, direction="b_to_a"))
    assert (verdict.relation, verdict.direction) == (relation, "b_to_a")


# -- AC-6.6 the quote guard ---------------------------------------------------------------

def test_ac_6_6_a_quote_that_is_not_in_the_node_is_re_asked_once_then_fails():
    good = answer()
    verdict, backend = verdict_for(answer(quote_b="valid for one day"), good)
    assert verdict.relation == "contradicts"                       # the re-ask was accepted
    assert len(backend.asked) == 2
    with pytest.raises(GuardFailure) as error:
        judge(A, B, FakeBackend([answer(quote_b="valid for one day")] * 2), settings=SETTINGS)
    assert "verbatim" in str(error.value).lower()


def test_a_quote_may_differ_in_layout_only():
    """F3 D9: sources are hard-wrapped and carry `**` marks; the words must match exactly."""
    wrapped = node("N-000099", "A share link\nexpires **30 days** after it is created.")
    verdict, _ = verdict_for(answer(quote_a="expires 30 days after it is created"), a=wrapped)
    assert verdict.relation == "contradicts"


# -- what a verdict records (AC-6.1 … AC-6.5, AC-6.8) -------------------------------------

def record_for(relation, **kwargs):
    verdict, _ = verdict_for(answer(relation=relation, **kwargs))
    return outcome_for(verdict, A, B, settings=SETTINGS, run_id="R-000001",
                       conflict_id="CF-000001", judgment="J-000400")


def test_ac_6_1_a_contradiction_opens_a_record_naming_both_members():
    outcome = record_for("contradicts")
    record = outcome.conflict
    assert record["kind"] == "contradiction"
    assert record["members"] == ["N-000017", "N-000042"]                      # sorted
    assert record["quotes"] == {"N-000017": "expires 30 days after it is created",
                                "N-000042": "valid for one hour"}
    assert (record["state"], record["detected_run"], record["judgment"]) == ("open", "R-000001",
                                                                            "J-000400")
    assert record["rationale"].startswith("both set the lifetime")
    validate("conflict", record)
    [link] = outcome.links
    assert (link["from"], link["type"], link["to"]) == ("N-000017", "conflicts_with", "N-000042")
    validate("link", link)


def test_ac_6_2_none_records_nothing_but_the_judgment():
    outcome = record_for("none")
    assert outcome == Outcome(links=[], conflict=None, ambiguity={})


@pytest.mark.parametrize("relation", ["refines", "depends_on"])
def test_ac_6_3_refines_and_depends_on_make_one_link_and_no_record(relation):
    outcome = record_for(relation, direction="b_to_a")
    assert outcome.conflict is None
    [link] = outcome.links
    assert (link["from"], link["type"], link["to"]) == ("N-000042", relation, "N-000017")
    assert (link["provenance"], link["judgment"]) == ("judgment", "J-000400")
    assert link["rationale"] and link["quotes"]
    validate("link", link)


def test_ac_6_4_duplication_makes_both_a_link_and_a_record():
    outcome = record_for("duplicates")
    assert outcome.conflict["kind"] == "duplication"
    assert [l["type"] for l in outcome.links] == ["duplicates"]


def test_ac_6_5_subsumption_is_a_conflict_only_when_the_two_differ():
    same = outcome_for(verdict_for(answer(relation="subsumes", direction="a_to_b"))[0],
                       A, node("N-000042", B_TEXT, line=22), settings=SETTINGS,
                       run_id="R-000001", conflict_id="CF-000001", judgment="J-000400")
    assert same.conflict is None and [l["type"] for l in same.links] == ["subsumes"]

    weaker = node("N-000042", B_TEXT, line=22, modality="SHOULD")
    differing = outcome_for(verdict_for(answer(relation="subsumes", direction="a_to_b"))[0],
                            A, weaker, settings=SETTINGS, run_id="R-000001",
                            conflict_id="CF-000001", judgment="J-000400")
    assert differing.conflict["kind"] == "subsumption"

    # A differing quantity counts too (F6 D2): same modality, different amounts.
    quantified = outcome_for(verdict_for(answer(relation="subsumes", direction="a_to_b"))[0],
                             A, B, settings=SETTINGS, run_id="R-000001",
                             conflict_id="CF-000001", judgment="J-000400")
    assert quantified.conflict["kind"] == "subsumption"


def test_ac_6_5_the_rule_can_be_turned_off_in_the_profile():
    """CT-6.3 `subsumption_conflict_only_when_differing: false` — every subsumption is a conflict."""
    settings = ConflictSettings(**{**DEFAULT_CONFLICTS, "subsumption_conflict_only_when_differing": False})
    verdict, _ = verdict_for(answer(relation="subsumes", direction="a_to_b"))
    outcome = outcome_for(verdict, A, node("N-000042", B_TEXT), settings=settings,
                          run_id="R-000001", conflict_id="CF-000001", judgment="J-000400")
    assert outcome.conflict["kind"] == "subsumption"


def test_ac_6_8_a_low_confidence_verdict_is_recorded_and_flags_both_nodes():
    outcome = record_for("contradicts", confidence="low")
    assert outcome.conflict["kind"] == "contradiction"            # recorded, not suppressed
    assert set(outcome.ambiguity) == {"N-000017", "N-000042"}
    for entries in outcome.ambiguity.values():
        assert [e["kind"] for e in entries] == ["low_confidence_verdict"]
    assert "low_confidence_verdict" in AMBIGUITY_KINDS          # F2 CT-2.1 accepts it on a node


def test_a_verdict_over_an_ambiguous_node_is_provisional():
    """F6 §4.4, D3: a vague claim can still contradict a precise one; T17 stores the flag."""
    ambiguous = node("N-000017", A_TEXT, status="ambiguous")
    verdict = judge(ambiguous, B, FakeBackend([answer()]), settings=SETTINGS)
    assert verdict.provisional is True
    assert judge(A, B, FakeBackend([answer()]), settings=SETTINGS).provisional is False
