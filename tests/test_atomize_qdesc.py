"""T8 — Q-DESC and guards G2, G4, G5, G6 on described atoms (F3 §4.2, §4.4).

AC-3.9 (G4) and AC-3.11 (G6) are covered here up to the *description*: the flag
and the ambiguity entries. The node status `ambiguous` and the `inferred_node`
review item they lead to are written by node forming (T9, T10).

Tier: unit, with a scripted fake backend.
"""
from __future__ import annotations

import copy

from sdd_compiler.atomize.describe import DescribeItem, build_question, describe_atoms
from sdd_compiler.atomize.qatom import Atom
from sdd_compiler.llm import FakeBackend

BLOCK = {
    "id": "B-000001",
    "text": "A share link must expire 30 days after it is created. Uploads must be fast.",
    "heading_path": ["Sharing"],
    "kind": "paragraph",
    "table_header": None,
}


def atom(quote, kind="requirement"):
    start = BLOCK["text"].index(quote)
    return Atom(block_id=BLOCK["id"], kind=kind, quotes=[quote], spans=[(start, start + len(quote))])


EXPIRY = atom("A share link must expire 30 days after it is created.")
SPEED = atom("Uploads must be fast.")

NO = {"answer": "no", "quote": None}


def answers(q3=None, **override):
    base = {f"Q{n}": dict(NO) for n in range(1, 8)}
    base["Q3"] = q3 or {"answer": "yes", "quote": "expire 30 days after it is created"}
    base.update(override)
    return base


def entry(atom_id="A-1", **changes):
    value = {
        "atom_id": atom_id,
        "canonical": {
            "state": None, "trigger": None, "scope": None,
            "subject": "share link", "modality": "MUST",
            "response": "expire 30 days after it is created",
        },
        "layer_answers": answers(),
        "terms": [{"name": "share link", "kind": "entity", "role": "subject", "quote": "share link"}],
        "ambiguity": [],
        "scope_layers": [],
        "scope_description": None,
        "verifies_text": None,
        "decision": None,
    }
    for key, new in changes.items():
        value[key] = new
    return value


def run(items, *scripted, weak_words=("fast",), aliases=None):
    backend = FakeBackend([{"atoms": list(batch)} for batch in scripted])
    outcome = describe_atoms(items, backend, weak_words=list(weak_words), aliases=aliases or {})
    return outcome, backend


ONE = [DescribeItem("A-1", EXPIRY, BLOCK)]


# -- the happy path -----------------------------------------------------------

def test_a_valid_answer_becomes_a_description_in_one_call():
    outcome, backend = run(ONE, [entry()])
    assert len(backend.asked) == 1
    assert outcome.failures == {}

    described = outcome.descriptions["A-1"]
    assert described.kind == "requirement"
    assert described.canonical["subject"] == "share link"
    assert described.canonical["modality"] == "MUST"
    assert described.flags == []
    assert described.ambiguity == []


def test_quotes_are_anchored_by_code():
    described = run(ONE, [entry()])[0].descriptions["A-1"]
    q3 = described.layer_answers["Q3"]
    assert BLOCK["text"][q3["span"][0]:q3["span"][1]] == "expire 30 days after it is created"
    assert described.layer_answers["Q1"] == {"answer": "no", "quote": None, "span": None}
    term = described.terms[0]
    assert BLOCK["text"][term["span"][0]:term["span"][1]] == "share link"


def test_quantities_come_from_the_quotes_not_the_model():
    described = run(ONE, [entry()])[0].descriptions["A-1"]
    assert described.canonical["quantities"] == [{
        "value": 30, "unit": "day", "normalized": {"value": 2_592_000, "unit": "s"}, "quote": "30 days",
    }]


def test_the_question_states_the_canonical_form_and_the_seven_layer_questions():
    prompt = build_question(ONE, None).prompt
    assert "MUST NOT" in prompt and "SHOULD" in prompt
    for n in range(1, 8):
        assert f"Q{n}" in prompt
    assert "A share link must expire 30 days" in prompt
    assert "A-1" in prompt


# -- G4 no injection (AC-3.9) ----------------------------------------------------

def test_ac_3_9_a_value_absent_from_the_quotes_marks_the_description_inferred():
    injected = entry(canonical={**entry()["canonical"],
                                "response": "expire 30 days after it is created, encrypted with AES-256"})
    outcome, backend = run(ONE, [injected])
    described = outcome.descriptions["A-1"]

    assert len(backend.asked) == 1                      # a fact, not a failure: no re-ask
    assert described.flags == ["inferred"]
    [finding] = [a for a in described.ambiguity if a["kind"] == "inferred"]
    assert "AES-256" in finding["detail"]
    assert finding["quote"] is None


def test_context_from_the_same_block_or_its_heading_is_not_an_injection():
    """F3 Q5: resolving "here" from the heading is not inventing (rel01 S21)."""
    contextual = entry(canonical={**entry()["canonical"], "scope": "Sharing, alongside uploads"},
                       terms=[{"name": "upload", "kind": "event", "role": "scope", "quote": "Uploads"}])
    described = run(ONE, [contextual])[0].descriptions["A-1"]
    assert described.flags == []


def test_a_value_found_nowhere_in_the_source_is_inferred_even_with_context():
    invented = entry(canonical={**entry()["canonical"], "scope": "Sharing, version 2"})
    described = run(ONE, [invented])[0].descriptions["A-1"]
    assert described.flags == ["inferred"]
    assert "'2'" in described.ambiguity[-1]["detail"]


def test_a_term_named_by_a_registered_alias_is_not_inferred():
    renamed = entry(terms=[{"name": "sharing link", "kind": "entity", "role": "subject",
                            "quote": "share link"}])
    described = run(ONE, [renamed], aliases={"sharing link": ["share link"]})[0].descriptions["A-1"]
    assert described.flags == []


def test_a_term_whose_quote_is_in_the_block_is_grounded_even_if_renamed():
    """The quote proves the term is in the source; naming it is Q-TERM's job, not G4's."""
    renamed = entry(terms=[{"name": "shared link", "kind": "entity", "role": "subject",
                            "quote": "share link"}])
    described = run(ONE, [renamed])[0].descriptions["A-1"]
    assert described.flags == []


# -- G6 weak words (AC-3.11) and unbounded quantities -----------------------------

def test_ac_3_11_a_weak_word_is_a_vague_term():
    speed = entry(canonical={**entry()["canonical"], "subject": "uploads", "response": "be fast"},
                  layer_answers=answers(q3={"answer": "yes", "quote": "Uploads must be fast."}),
                  terms=[{"name": "upload", "kind": "event", "role": "subject", "quote": "Uploads"}])
    described = run([DescribeItem("A-1", SPEED, BLOCK)], [speed])[0].descriptions["A-1"]
    assert {"kind": "vague_term", "quote": "fast", "detail": "weak word 'fast'"} in described.ambiguity
    assert described.flags == []


def test_a_vague_amount_is_an_unbounded_quantity():
    block = {**BLOCK, "text": "The cache must refresh after a few minutes."}
    item = Atom(block_id=block["id"], kind="requirement", quotes=[block["text"]],
                spans=[(0, len(block["text"]))])
    vague = entry(canonical={**entry()["canonical"], "subject": "cache",
                             "response": "refresh after a few minutes"},
                  layer_answers=answers(q3={"answer": "yes", "quote": "refresh after a few minutes"}),
                  terms=[{"name": "cache", "kind": "component", "role": "subject", "quote": "cache"}])
    described = run([DescribeItem("A-1", item, block)], [vague])[0].descriptions["A-1"]
    assert {"kind": "unbounded_quantity", "quote": "a few minutes",
            "detail": "an amount with no bound"} in described.ambiguity


def test_model_ambiguity_candidates_are_kept_when_anchored():
    flagged = entry(ambiguity=[{"kind": "referential", "quote": "it"}])
    described = run(ONE, [flagged])[0].descriptions["A-1"]
    assert described.ambiguity == [
        {"kind": "referential", "quote": "it", "detail": "proposed by the model"}
    ]


# -- re-ask rules: G2, G5, and a yes without a quote -------------------------------

def test_a_quote_absent_from_the_block_is_re_asked_once_then_fails():
    bad = entry(layer_answers=answers(q3={"answer": "yes", "quote": "links vanish after a month"}))
    outcome, backend = run(ONE, [bad], [bad])
    assert len(backend.asked) == 2
    assert "links vanish after a month" in backend.asked[1].prompt
    assert "A-1" in outcome.failures
    assert "A-1" not in outcome.descriptions


def test_a_yes_without_a_quote_is_re_asked():
    bad = entry(layer_answers=answers(q3={"answer": "yes", "quote": None}))
    outcome, backend = run(ONE, [bad], [entry()])
    assert len(backend.asked) == 2
    assert "Q3" in backend.asked[1].prompt
    assert outcome.failures == {}


def test_a_schema_failure_is_re_asked():
    bad = entry()
    del bad["layer_answers"]
    outcome, backend = run(ONE, [bad], [entry()])
    assert len(backend.asked) == 2
    assert outcome.failures == {}


def test_in_a_batch_only_the_failed_atom_is_re_asked():
    items = [DescribeItem("A-1", EXPIRY, BLOCK), DescribeItem("A-2", EXPIRY, BLOCK)]
    bad = entry("A-2", layer_answers=answers(q3={"answer": "yes", "quote": "not in the block"}))
    outcome, backend = run(items, [entry("A-1"), bad], [entry("A-2")])

    assert len(backend.asked) == 2
    assert backend.asked[1].payload["atom_ids"] == ["A-2"]
    assert set(outcome.descriptions) == {"A-1", "A-2"}


def test_a_failed_first_answer_leaves_no_trace_in_the_accepted_one():
    bad = copy.deepcopy(entry())
    bad["terms"].append({"name": "ghost", "kind": "entity", "role": "response", "quote": "ghost"})
    outcome, _ = run(ONE, [bad], [entry()])
    assert [term["name"] for term in outcome.descriptions["A-1"].terms] == ["share link"]


def test_atoms_are_asked_in_batches_of_the_given_size():
    items = [DescribeItem(f"A-{n}", EXPIRY, BLOCK) for n in range(1, 6)]
    scripted = [[entry("A-1"), entry("A-2")], [entry("A-3"), entry("A-4")], [entry("A-5")]]
    backend = FakeBackend([{"atoms": batch} for batch in scripted])
    outcome = describe_atoms(items, backend, weak_words=[], aliases={}, batch_size=2)
    assert [q.payload["atom_ids"] for q in backend.asked] == [["A-1", "A-2"], ["A-3", "A-4"], ["A-5"]]
    assert len(outcome.descriptions) == 5


def test_a_block_shared_by_several_atoms_is_sent_once():
    items = [DescribeItem("A-1", EXPIRY, BLOCK), DescribeItem("A-2", SPEED, BLOCK)]
    prompt = build_question(items, None).prompt
    assert prompt.count(BLOCK["text"]) == 1


def test_the_question_says_the_section_line_is_not_quotable():
    assert "never quote it" in build_question(ONE, None).prompt


def test_markdown_code_marks_do_not_make_a_term_look_injected():
    block = {**BLOCK, "text": "The `PostToolUse` hook adapter is deferred."}
    item = Atom(block_id=block["id"], kind="decision", quotes=[block["text"]],
                spans=[(0, len(block["text"]))])
    answer = entry(canonical={**entry()["canonical"], "subject": "PostToolUse hook adapter",
                              "modality": None, "response": "is deferred"},
                   layer_answers=answers(q3={"answer": "yes", "quote": "is deferred"}),
                   terms=[{"name": "PostToolUse hook adapter", "kind": "component",
                           "role": "subject", "quote": "hook adapter"}],
                   decision={"chosen": "defer", "rejected": []})
    described = run([DescribeItem("A-1", item, block)], [answer])[0].descriptions["A-1"]
    assert described.flags == []


def test_the_model_may_not_propose_vague_terms():
    """`vague_term` belongs to G6 and the owner's weak-word list."""
    kinds = model_ambiguity_kinds()
    assert "vague_term" not in kinds
    assert {"missing_actor", "referential", "scope"} <= set(kinds)


def model_ambiguity_kinds():
    from sdd_compiler.atomize.describe import SCHEMA
    item = SCHEMA["properties"]["atoms"]["items"]["properties"]["ambiguity"]["items"]
    return item["properties"]["kind"]["enum"]


def test_d14_a_requirement_without_modality_is_described_and_flagged():
    bare = entry(canonical={**entry()["canonical"], "modality": None})
    outcome, backend = run(ONE, [bare])
    assert len(backend.asked) == 1                      # no re-ask: a fact, not a failure
    described = outcome.descriptions["A-1"]
    assert described.canonical["modality"] is None
    assert [a["kind"] for a in described.ambiguity] == ["missing_modality"]
