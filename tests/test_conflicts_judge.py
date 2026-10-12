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
         modality="MUST", quantities=(), line=5, file="specs/sharing.md", block=None):
    return {
        "id": node_id, "text": text, "layer": layer, "family": family, "status": status,
        "canonical": {"state": None, "trigger": None, "scope": None, "subject": "share link",
                      "modality": modality, "response": text, "quantities": list(quantities)},
        "source": {"file": file, "block_id": block or f"B-{node_id}", "lines": [line, line],
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


def test_r19_the_question_shows_the_terms_and_warns_about_two_names_for_one_thing():
    """I-76: R15 delivered the 5 GB / 5 GiB pair to the judge and it answered `none` — "the two
    claims govern different export types (export archive vs workspace export)". The graph knows
    both are kinds of `export`; the question now says so (F6 D17)."""
    a = {**A, "terms": [{"term": "term:export_archive", "role": "subject", "quote": "archive"}]}
    b = {**B, "terms": [{"term": "term:workspace_export", "role": "subject", "quote": "export"}]}
    prompt = build_question(a, b, related_terms=["term:export_archive and term:workspace_export "
                                                 "are both kinds of term:export"]).prompt
    assert "term:export_archive" in prompt and "term:workspace_export" in prompt
    assert "both kinds of term:export" in prompt
    lowered = prompt.lower()
    assert "same thing" in lowered and "different name" in lowered


def test_r16_the_prompt_says_when_two_numbers_are_not_a_contradiction():
    """M4 gate I-74: 5 of 8 false positives were one mistake — a 24-hour link inside a 30-day
    archive, a 13-day restore inside a 14-day window, read as contradictions; and once the judge
    computed "day 30 versus day 31", arithmetic the text does not do."""
    prompt = build_question(A, B).prompt.lower()
    assert "same thing at the same time" in prompt
    assert "inside" in prompt and "window" in prompt
    assert "do not calculate" in prompt or "never compute" in prompt
    assert "acceptance criterion" in prompt          # restating a requirement is not duplication


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


def test_i77_a_criterion_never_duplicates_the_requirement_it_verifies():
    """R17 (I-77): the judge opened a duplication between AC-1.1 and the requirement it verifies,
    the exact case F6 D15's prompt names. A prompt rule is a request; this one is checked in code
    (F6 D16). A *contradiction* between a test and its rule is still reported — that one matters."""
    requirement = node("N-000008", "A request whose archive would be larger is rejected when queued.")
    criterion = {**node("AC-1.1", "Given a project whose archive would exceed the limit, then it is "
                                  "rejected at queue time.", layer="V"),
                 "verifies": ["N-000008"]}
    verdict, _ = verdict_for(answer(relation="duplicates", quote_a="rejected", quote_b="rejected"),
                             a=criterion, b=requirement)
    outcome = outcome_for(verdict, criterion, requirement, settings=SETTINGS, run_id="R-000001",
                          conflict_id="CF-000001", judgment="J-000400")
    assert outcome.conflict is None and outcome.links == []
    assert outcome.suppressed == "verifies_its_own_requirement"

    subsumed, _ = verdict_for(answer(relation="subsumes", direction="a_to_b",
                                     quote_a="rejected", quote_b="rejected"),
                              a=criterion, b=requirement)
    assert outcome_for(subsumed, criterion, requirement, settings=SETTINGS, run_id="R-000001",
                       conflict_id="CF-000001", judgment="J-000400").conflict is None

    clash, _ = verdict_for(answer(relation="contradicts", quote_a="rejected", quote_b="rejected"),
                           a=criterion, b=requirement)
    kept = outcome_for(clash, criterion, requirement, settings=SETTINGS, run_id="R-000001",
                       conflict_id="CF-000001", judgment="J-000400")
    assert kept.conflict["kind"] == "contradiction"          # a test that denies its rule is a defect
    assert kept.suppressed is None


def _judged(relation, a, b):
    verdict, _ = verdict_for(answer(relation=relation, quote_a=a["text"][:12], quote_b=b["text"][:12],
                                    **({"direction": "a_to_b"} if relation == "subsumes" else {})),
                             a=a, b=b)
    return outcome_for(verdict, a, b, settings=SETTINGS, run_id="R-000001",
                       conflict_id="CF-000001", judgment="J-000400")


REQUIREMENT = node("N-000008", "A request whose archive would be larger is rejected when queued.")
CRITERION = node("AC-1.1", "Given a project whose archive would exceed the limit, then it is "
                           "rejected at queue time.", layer="V")          # cites nothing: verifies []


@pytest.mark.parametrize("relation", ["duplicates", "subsumes"])
def test_ac_6_22_a_criterion_never_duplicates_a_claim_of_its_own_spec(relation):
    """I-81: on our own specs most criteria cite nothing, so D16 could not fire; 22 of 70 dogfood
    conflicts were a criterion restating prose of its own file. The file is the fact (F6 D19)."""
    outcome = _judged(relation, CRITERION, REQUIREMENT)
    assert outcome.conflict is None and outcome.links == []
    assert outcome.suppressed == "criterion_restates_its_own_spec"


def test_ac_6_22_what_the_criterion_rule_leaves_alone():
    # A criterion that contradicts its own spec's prose is a real defect (CF-000038 was one).
    assert _judged("contradicts", CRITERION, REQUIREMENT).conflict["kind"] == "contradiction"
    # Another spec's claim: duplication across files is what the compiler is for.
    elsewhere = node("N-000009", REQUIREMENT["text"], file="specs/limits.md")
    assert _judged("duplicates", CRITERION, elsewhere).conflict["kind"] == "duplication"
    # Two criteria duplicating each other in one file are a copied test, not the spec's form.
    twin = node("AC-1.2", CRITERION["text"], layer="V")
    assert _judged("duplicates", CRITERION, twin).conflict["kind"] == "duplication"


@pytest.mark.parametrize("relation", ["duplicates", "subsumes"])
def test_ac_6_23_two_claims_of_one_block_never_duplicate_each_other(relation):
    """I-81: a decision entry's heading summarises its body — one block, written to overlap."""
    heading = node("N-000118", "Q-PAIR is batched: 8 pairs per call", block="B-000280")
    body = node("N-000119", "each pair's answer is validated on its own", block="B-000280")
    outcome = _judged(relation, heading, body)
    assert outcome.conflict is None and outcome.links == []
    assert outcome.suppressed == "same_block"


def test_ac_6_23_a_contradiction_inside_one_block_is_still_reported():
    """CF-000001 was two sentences of one paragraph, and real."""
    first = node("N-000005", "A stale node needs checking.", block="B-000045")
    second = node("N-000006", "Unchanged nodes are skipped.", block="B-000045")
    assert _judged("contradicts", first, second).conflict["kind"] == "contradiction"
    apart = node("N-000007", "Unchanged nodes are skipped.", block="B-000046")
    assert _judged("duplicates", first, apart).conflict["kind"] == "duplication"


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
