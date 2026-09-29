"""F3 §4.5a, D39; F2 D21 — a fenced contract block is one node, formed whole, with its title's id.

Tier: unit. No model call.
"""
from __future__ import annotations

from sdd_compiler.atomize.contracts import annotate, contract_atom
from sdd_compiler.atomize.describe import DescribeItem, build_question, describe_atoms, lock_input
from sdd_compiler.llm import FakeBackend
from sdd_compiler.atomize.qatom import Atom
from sdd_compiler.model.ids import adopt_human_ids, human_labels

LANGUAGES = ("json", "yaml", "text")
BODY = '{ "id": "B-000123",\n  "text": "exact source text" }'


def block(block_id, kind, text, line, heading=("5. Contracts",), source="spec.md"):
    return {"id": block_id, "source": source, "kind": kind, "heading_path": list(heading),
            "lines": [line, line + text.count("\n")], "text": text}


TITLE = block("B-000001", "paragraph", "**CT-1.1 — Block record** (`.sdd/blocks.jsonl`):", 3)
FENCE = block("B-000002", "code", f"```json\n{BODY}\n```", 5)


def test_ac_3_35_a_contract_atom_is_the_text_between_the_fences():
    atom = contract_atom(FENCE)
    assert atom.kind == "requirement" and atom.quotes == [BODY]
    start, end = atom.spans[0]
    assert FENCE["text"][start:end] == BODY


def test_d39_a_contract_takes_the_paragraph_directly_before_it_as_its_lead():
    annotated = {b["id"]: b for b in annotate([TITLE, FENCE], [TITLE, FENCE], LANGUAGES)}
    assert annotated["B-000002"]["contract"] == {"lead": TITLE["text"], "id": "CT-1.1"}
    assert annotated["B-000001"]["id_given_to"] == "B-000002"
    assert "contract" not in annotated["B-000001"]
    assert "contract" not in TITLE and "contract" not in FENCE        # copies, never the records


def test_d39_the_lead_is_found_among_all_blocks_even_when_only_the_contract_is_pending():
    [only] = annotate([FENCE], [TITLE, FENCE], LANGUAGES)
    assert only["contract"]["id"] == "CT-1.1"


def test_ac_3_38_a_block_that_opens_its_section_has_no_lead():
    other = block("B-000003", "paragraph", "Scoring is additive.", 1, heading=("4.2 Scores",))
    formula = block("B-000004", "code", "```text\nscore = sum of points\n```", 3, heading=("4.3 Scoring",))
    [annotated] = annotate([formula], [other, formula], LANGUAGES)
    assert annotated["contract"] == {"lead": None, "id": None}


def test_d39_a_lead_without_a_ct_id_gives_context_but_no_id():
    lead = block("B-000005", "paragraph", "At the end of a run, `compile` prints:", 1)
    sample = block("B-000006", "code", "```text\nR-0001: compiled 1 file(s)\n```", 3)
    annotated = {b["id"]: b for b in annotate([lead, sample], [lead, sample], LANGUAGES)}
    assert annotated["B-000006"]["contract"] == {"lead": lead["text"], "id": None}
    assert "id_given_to" not in annotated["B-000005"]


def test_d39_code_in_another_language_is_not_a_contract():
    script = block("B-000007", "code", "```python\nprint(1)\n```", 5)
    [annotated] = annotate([script], [TITLE, script], LANGUAGES)
    assert "contract" not in annotated


def test_ac_2_29_the_contract_carries_the_id_and_the_title_only_the_label():
    annotated = {b["id"]: b for b in annotate([TITLE, FENCE], [TITLE, FENCE], LANGUAGES)}
    counts = {"B-000001": 1, "B-000002": 1}
    assert human_labels(annotated, counts) == {"B-000001": "CT-1.1", "B-000002": "CT-1.1"}
    assert adopt_human_ids(annotated, counts) == {"B-000002": "CT-1.1"}


def test_ac_3_37_an_ordinary_lock_input_is_unchanged_and_a_contract_adds_its_lead():
    plain = block("B-000009", "paragraph", "A share link must expire.", 1)
    atom = Atom("B-000009", "requirement", ["A share link must expire."], [(0, 25)])
    assert lock_input(DescribeItem("B-000009#1", atom, plain)) == {
        "kind": "requirement", "quotes": ["A share link must expire."],
        "block_text": "A share link must expire.", "heading_path": ["5. Contracts"]}
    item = DescribeItem("B-000002#1", contract_atom(FENCE), FENCE, contract=True, lead=TITLE["text"])
    assert lock_input(item)["lead"] == TITLE["text"] and lock_input(item)["contract"] is True


NO = {"answer": "no", "quote": None}


def described(layer_quote, term_quote):
    answers = {f"Q{n}": dict(NO) for n in range(1, 8)}
    answers["Q6"] = {"answer": "yes", "quote": layer_quote}
    return {"canonical": {"state": None, "trigger": None, "scope": None, "subject": "block record",
                          "modality": "MUST", "response": "have this shape"},
            "layer_answers": answers,
            "terms": [{"name": "block record", "kind": "data", "role": "subject", "quote": term_quote}],
            "ambiguity": [{"kind": "scope", "quote": "unclear which records"}],
            "scope_layers": [], "scope_description": None, "verifies_text": None, "decision": None}


def test_ac_3_39_a_contracts_unfound_quotes_are_replaced_not_re_asked():
    item = DescribeItem("B-000002#1", contract_atom(FENCE), FENCE, contract=True, lead=TITLE["text"])
    backend = FakeBackend([{"atoms": [{"atom_id": "B-000002#1",
                                       **described('"id", "text"', "the block record type")}]}])
    outcome = describe_atoms([item], backend, weak_words=[], aliases={})
    assert len(backend.asked) == 1 and outcome.failures == {}
    description = outcome.descriptions["B-000002#1"]
    start, end = item.atom.spans[0]
    assert description.layer_answers["Q6"]["span"] == (start + item.offset, end + item.offset)
    [term] = description.terms
    assert term["quote"] == "Block record"                         # as the title writes it
    assert description.ambiguity == [{"kind": "scope", "quote": None, "detail": "proposed by the model"}]
    assert [r["quote"] for r in description.replaced] == [
        '"id", "text"', "the block record type", "unclear which records"]


def test_ac_3_39_a_term_whose_name_is_nowhere_is_dropped():
    item = DescribeItem("B-000002#1", contract_atom(FENCE), FENCE, contract=True, lead=TITLE["text"])
    answer = described('"id": "B-000123"', "the ledger")
    answer["terms"][0]["name"] = "ledger"
    outcome = describe_atoms([item], FakeBackend([{"atoms": [{"atom_id": "B-000002#1", **answer}]}]),
                             weak_words=[], aliases={})
    assert outcome.descriptions["B-000002#1"].terms == []


def test_ac_3_39_an_ordinary_atom_is_still_re_asked():
    plain = block("B-000009", "paragraph", "A share link must expire.", 1)
    atom = Atom("B-000009", "requirement", ["A share link must expire."], [(0, 25)])
    bad = {"atom_id": "B-000009#1", **described('"id", "text"', "share link")}
    backend = FakeBackend([{"atoms": [bad]}, {"atoms": [bad]}])
    outcome = describe_atoms([DescribeItem("B-000009#1", atom, plain)], backend, weak_words=[], aliases={})
    assert len(backend.asked) == 2 and "B-000009#1" in outcome.failures


def test_ac_3_39_the_contract_hint_is_gone_and_the_quote_rule_is_per_item():
    item = DescribeItem("B-000002#1", contract_atom(FENCE), FENCE, contract=True, lead=TITLE["text"])
    prompt = build_question([item]).prompt
    assert "shape, format or output" not in prompt
    assert "one whole line" in prompt
    assert "one whole line" not in build_question([]).prompt      # not in the lock key's instructions
