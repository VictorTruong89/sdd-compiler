"""F3 §4.5 step 9, D38 — `definition` sentences become term definitions, attached by code.

Tier: unit. No model call: Q-ATOM's answer is given.
"""
from __future__ import annotations

from sdd_compiler.atomize.definitions import Definition, attach_definitions, block_definitions
from sdd_compiler.atomize.qatom import atomize_blocks
from sdd_compiler.llm import FakeBackend


def term(name, *aliases, definition=None, defined_by=None):
    key = "term:" + name.replace(" ", "_")
    return key, {"id": key, "canonical": name, "aliases": list(aliases), "kind": "entity",
                 "definition": definition, "defined_by": defined_by, "status": "proposed",
                 "broader": None}


def registry(*entries):
    return dict(entries)


def definition(text, block="B-000001", line=3, start=0):
    return Definition(block_id=block, file="spec.md", lines=(line, line), start=start, text=text)


def test_ac_3_31_a_definition_opening_with_a_registered_term_is_attached():
    text = "A **block** is a structural unit found by code."
    outcome = attach_definitions(registry(term("block")), [definition(text)], invalidated=set())
    assert outcome.changed["term:block"]["definition"] == text          # as it appears in the block
    assert outcome.changed["term:block"]["defined_by"] == "B-000001"
    assert [a["term"] for a in outcome.attached] == ["term:block"]
    assert outcome.unattached == []


def test_ac_3_32_unmatched_and_repeated_definitions_are_reported_not_dropped():
    first = definition("A **block** is a structural unit found by code.", line=3)
    sentences = [
        first,
        definition("Both cannot hold.", block="B-000002", line=5),
        definition("A block is not an atomic spec.", block="B-000003", line=7),
        definition("A requirement or constraint that states no modal verb has this ambiguity.",
                   block="B-000004", line=9),
    ]
    terms = registry(term("block"), term("requirement"))
    outcome = attach_definitions(terms, list(reversed(sentences)), invalidated=set())
    assert outcome.changed["term:block"]["definition"] == first.text      # first in reading order
    assert "term:requirement" not in outcome.changed
    reasons = {u["text"]: u["reason"] for u in outcome.unattached}
    assert reasons == {
        "Both cannot hold.": "no_term",
        "A block is not an atomic spec.": "already_defined",
        "A requirement or constraint that states no modal verb has this ambiguity.": "no_term",
    }
    assert all(u["file"] == "spec.md" and u["lines"] for u in outcome.unattached)


def test_d38_the_name_must_be_followed_by_a_definitional_boundary():
    terms = registry(term("stale"), term("sddc map"), term("mention"), term("label"))
    cases = {
        '`stale` means "needs re-checking"': "term:stale",
        "`sddc map` — a table of families (rows) × layers (columns).": "term:sddc_map",
        "**Mention** (D17) — the first term the node uses in any role.": "term:mention",
        "`label` is the human id of the block the node was formed from": "term:label",
        "Label reading happens once per block.": None,                  # no boundary after it
    }
    for text, expected in cases.items():
        outcome = attach_definitions(terms, [definition(text)], invalidated=set())
        got = [a["term"] for a in outcome.attached]
        assert got == ([expected] if expected else []), text


def test_d38_aliases_plurals_and_the_longest_name_match():
    terms = registry(term("share link", "shared link"), term("share"), term("block"))
    for text, expected in [("A shared link is a URL that grants read access.", "term:share_link"),
                           ("Blocks are what F1 stores.", "term:block"),
                           ("The share link is a URL.", "term:share_link")]:
        outcome = attach_definitions(terms, [definition(text)], invalidated=set())
        assert [a["term"] for a in outcome.attached] == [expected], text


def test_d38_a_table_row_is_never_matched():
    outcome = attach_definitions(registry(term("intent")),
                                 [definition("| `L0` Intent | Why the system exists")], invalidated=set())
    assert outcome.attached == [] and outcome.unattached[0]["reason"] == "no_term"


def test_ac_3_33_an_invalidated_block_loses_the_definitions_it_gave():
    terms = registry(term("block", definition="A block is a unit.", defined_by="B-000001"),
                     term("pair", definition="A pair is unordered.", defined_by="B-000009"))
    outcome = attach_definitions(terms, [], invalidated={"B-000001"})
    assert outcome.changed["term:block"]["definition"] is None
    assert outcome.changed["term:block"]["defined_by"] is None
    assert "term:pair" not in outcome.changed                      # its block was not touched


def test_d38_a_re_atomized_block_re_derives_its_definition():
    terms = registry(term("block", definition="A block is a unit.", defined_by="B-000001"))
    new = "A block is a structural unit."
    outcome = attach_definitions(terms, [definition(new)], invalidated={"B-000001"})
    assert outcome.changed["term:block"]["definition"] == new


def test_d38_quotes_are_located_and_stored_as_the_block_says_them():
    block = {"id": "B-000001", "source": "spec.md", "lines": [3, 4],
             "text": "A **block** is a structural\nunit found by code. It must be stored."}
    found, dropped = block_definitions(block, ["A **block** is a structural unit found by code.",
                                               "A page is paper."])
    assert [d.text for d in found] == ["A **block** is a structural\nunit found by code."]
    assert found[0].start == 0 and found[0].lines == (3, 4)
    assert dropped == [{"block": "B-000001", "file": "spec.md", "lines": [3, 4],
                        "text": "A page is paper.", "reason": "not_in_block"}]


def test_d38_q_atom_keeps_the_definition_sentences_of_a_block():
    block = {"id": "B-000001", "source": "spec.md", "lines": [1, 1], "kind": "paragraph",
             "heading_path": [], "text": "A block is a unit. It must be stored."}
    backend = FakeBackend([{"blocks": [{"block_id": "B-000001", "sentences": [
        {"quote": "A block is a unit.", "role": "definition"},
        {"quote": "It must be stored.", "role": "requirement"}],
        "atoms": [{"kind": "requirement", "quotes": ["It must be stored."]}]}]}])
    outcome = atomize_blocks([block], backend)
    assert outcome.definitions == {"B-000001": ["A block is a unit."]}


def test_d38_leading_markup_stays_with_the_stored_sentence():
    """R18: G2 treats `*` and backticks as layout, so the located span began after them."""
    block = {"id": "B-000001", "source": "spec.md", "lines": [1, 1],
             "text": 'Terms: `stale` means "needs re-checking". **Mention** (D17) — the first term.'}
    found, _ = block_definitions(block, ['`stale` means "needs re-checking"',
                                         "**Mention** (D17) — the first term."])
    assert [d.text for d in found] == ['`stale` means "needs re-checking"',
                                       "**Mention** (D17) — the first term."]
