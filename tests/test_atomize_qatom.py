"""M2 T7 — Q-ATOM with guards G2, G3, G5, and the re-ask rule.

Covers F3 AC-3.6, AC-3.7, AC-3.8, AC-3.10, and the batching allowed by F3 §4.3
rule 4 (rel01 D31). Tier: unit.
"""
from __future__ import annotations

import pytest

from sdd_compiler.atomize.qatom import Atom, atomize_blocks, build_question
from sdd_compiler.llm import FakeBackend

BLOCK_A = {
    "id": "B-000001",
    "text": "Owners can create a share link. A share link must expire after 30 days.",
    "heading_path": ["Sharing"],
    "kind": "paragraph",
    "table_header": None,
}
BLOCK_B = {
    "id": "B-000002",
    "text": "The system should send a notification.",
    "heading_path": ["Sharing"],
    "kind": "paragraph",
    "table_header": None,
}


def answer_for(*blocks):
    """A well-formed answer covering every normative sentence of each block."""
    return {
        "blocks": [
            {
                "block_id": block["id"],
                "sentences": [{"quote": block["text"], "role": "requirement"}],
                "atoms": [{"kind": "requirement", "quotes": [block["text"]]}],
            }
            for block in blocks
        ]
    }


# -- the question -----------------------------------------------------------

def test_one_call_carries_a_batch_of_blocks():
    """rel01 D31 — batching is what makes a compile affordable."""
    question = build_question([BLOCK_A, BLOCK_B])
    assert question.kind == "q-atom"
    assert question.schema_version.startswith("q-atom/")
    assert "B-000001" in question.prompt and "B-000002" in question.prompt
    assert BLOCK_A["text"] in question.prompt
    assert question.schema["properties"]["blocks"]["type"] == "array"


def test_the_prompt_states_the_atom_tests_and_the_quote_rule():
    prompt = build_question([BLOCK_A]).prompt
    assert "verbatim" in prompt.lower()
    for marker in ("one observation", "dispute", "one layer", "stands alone"):
        assert marker in prompt.lower()


def test_the_prompt_keeps_a_rule_stated_in_a_table_row_as_a_claim():
    """M3 gate (I-56): Q-ATOM labelled F5's seven source rows `definition` and formed nothing, so
    F5's core rules were absent from the graph. `definition` is for what a word means."""
    prompt = build_question([BLOCK_A]).prompt.lower()
    assert "table row" in prompt and "what a word means" in prompt


# -- the happy path ---------------------------------------------------------

def test_a_valid_batch_yields_atoms_per_block():
    backend = FakeBackend([answer_for(BLOCK_A, BLOCK_B)])
    outcome = atomize_blocks([BLOCK_A, BLOCK_B], backend)

    assert len(backend.asked) == 1
    assert outcome.failures == {}
    assert [atom.block_id for atom in outcome.atoms] == ["B-000001", "B-000002"]
    assert isinstance(outcome.atoms[0], Atom)
    assert outcome.atoms[0].kind == "requirement"


def test_ac_3_7_g2_anchors_quotes_to_offsets_computed_by_code():
    """AC-3.7 — a quote occurring twice anchors to the first unclaimed occurrence."""
    block = {**BLOCK_A, "text": "Tokens expire. Tokens expire."}
    answer = {"blocks": [{
        "block_id": block["id"],
        "sentences": [{"quote": "Tokens expire.", "role": "requirement"}],
        "atoms": [
            {"kind": "requirement", "quotes": ["Tokens expire."]},
            {"kind": "requirement", "quotes": ["Tokens expire."]},
        ],
    }]}
    outcome = atomize_blocks([block], FakeBackend([answer]))
    assert [atom.spans for atom in outcome.atoms] == [[(0, 14)], [(15, 29)]]
    assert block["text"][0:14] == "Tokens expire."
    assert block["text"][15:29] == "Tokens expire."


# -- guards -----------------------------------------------------------------

def test_ac_3_6_a_quote_that_is_not_verbatim_is_re_asked_once_then_fails():
    """AC-3.6 — G2 fails twice: two calls, no atoms, the block is named."""
    bad = {"blocks": [{
        "block_id": "B-000001",
        "sentences": [{"quote": BLOCK_A["text"], "role": "requirement"}],
        "atoms": [{"kind": "requirement", "quotes": ["Owners may create a share link"]}],
    }]}
    backend = FakeBackend([bad, bad])
    outcome = atomize_blocks([BLOCK_A], backend)

    assert len(backend.asked) == 2
    assert outcome.atoms == []
    assert "B-000001" in outcome.failures
    assert "verbatim" in outcome.failures["B-000001"].lower()


def test_ac_3_6_the_re_ask_quotes_the_failed_check():
    bad = {"blocks": [{
        "block_id": "B-000001",
        "sentences": [{"quote": BLOCK_A["text"], "role": "requirement"}],
        "atoms": [{"kind": "requirement", "quotes": ["not in the block at all"]}],
    }]}
    backend = FakeBackend([bad, answer_for(BLOCK_A)])
    outcome = atomize_blocks([BLOCK_A], backend)

    assert len(backend.asked) == 2
    assert "not in the block at all" in backend.asked[1].prompt
    assert outcome.failures == {}
    assert len(outcome.atoms) == 1


def test_the_re_ask_covers_only_the_failed_block():
    """F3 §4.3 rule 4 — batching is allowed only if a failure re-asks one item."""
    bad_b = {"blocks": [
        answer_for(BLOCK_A)["blocks"][0],
        {"block_id": "B-000002", "sentences": [], "atoms": [
            {"kind": "requirement", "quotes": ["invented text"]}]},
    ]}
    backend = FakeBackend([bad_b, answer_for(BLOCK_B)])
    outcome = atomize_blocks([BLOCK_A, BLOCK_B], backend)

    assert len(backend.asked) == 2
    assert "B-000002" in backend.asked[1].prompt
    assert "B-000001" not in backend.asked[1].prompt
    assert {atom.block_id for atom in outcome.atoms} == {"B-000001", "B-000002"}


def test_ac_3_8_g3_coverage_names_the_uncovered_sentence():
    """AC-3.8 — a 'must' sentence nobody covered triggers a re-ask."""
    block = {**BLOCK_A, "text": "Files must be scanned. Links must expire."}
    partial = {"blocks": [{
        "block_id": block["id"],
        "sentences": [{"quote": "Files must be scanned.", "role": "requirement"}],
        "atoms": [{"kind": "requirement", "quotes": ["Files must be scanned."]}],
    }]}
    backend = FakeBackend([partial, partial])
    outcome = atomize_blocks([block], backend)

    assert len(backend.asked) == 2
    assert "Links must expire." in backend.asked[1].prompt
    assert "coverage" in outcome.failures[block["id"]].lower()


def test_g3_accepts_a_sentence_labelled_non_normative():
    block = {**BLOCK_A, "text": "Files must be scanned. This may change later."}
    answer = {"blocks": [{
        "block_id": block["id"],
        "sentences": [
            {"quote": "Files must be scanned.", "role": "requirement"},
            {"quote": "This may change later.", "role": "context"},
        ],
        "atoms": [{"kind": "requirement", "quotes": ["Files must be scanned."]}],
    }]}
    outcome = atomize_blocks([block], FakeBackend([answer]))
    assert outcome.failures == {}


def test_ac_3_10_g5_a_malformed_answer_is_re_asked():
    """AC-3.10 — an answer missing `atoms` fails the schema."""
    malformed = {"blocks": [{"block_id": "B-000001", "sentences": []}]}
    backend = FakeBackend([malformed, answer_for(BLOCK_A)])
    outcome = atomize_blocks([BLOCK_A], backend)

    assert len(backend.asked) == 2
    assert outcome.failures == {}


def test_g5_a_block_the_model_invented_is_refused():
    answer = {"blocks": [{
        "block_id": "B-999999",
        "sentences": [],
        "atoms": [{"kind": "requirement", "quotes": ["anything"]}],
    }]}
    backend = FakeBackend([answer, answer])
    outcome = atomize_blocks([BLOCK_A], backend)
    assert outcome.atoms == []
    assert "B-000001" in outcome.failures


def test_a_block_missing_from_the_answer_is_a_failure_for_that_block_only():
    answer = {"blocks": [answer_for(BLOCK_A)["blocks"][0]]}
    backend = FakeBackend([answer, answer_for(BLOCK_B)])
    outcome = atomize_blocks([BLOCK_A, BLOCK_B], backend)
    assert {atom.block_id for atom in outcome.atoms} == {"B-000001", "B-000002"}


def test_roles_that_are_not_atoms_are_kept_as_annotations():
    block = {**BLOCK_A, "text": "Links must expire. This protects shared files."}
    answer = {"blocks": [{
        "block_id": block["id"],
        "sentences": [
            {"quote": "Links must expire.", "role": "requirement"},
            {"quote": "This protects shared files.", "role": "rationale"},
        ],
        "atoms": [{"kind": "requirement", "quotes": ["Links must expire."]}],
    }]}
    outcome = atomize_blocks([block], FakeBackend([answer]))
    assert outcome.annotations[block["id"]] == [("rationale", "This protects shared files.")]


# -- G2 and hard-wrapped prose (F3 Q4) --------------------------------------

WRAPPED = {
    "id": "B-000010",
    "text": "A block is a structural unit found by code: a paragraph, a list item, or a\nfenced code block. Splitting blocks into claims is a language judgment.",
    "heading_path": ["Goal"],
    "kind": "paragraph",
    "table_header": None,
}


def test_a_quote_spanning_a_line_break_is_accepted_and_anchored_truly():
    """The model returns a space where the source wraps; the words still match."""
    answer = {"blocks": [{
        "block_id": WRAPPED["id"],
        "sentences": [{"quote": "Splitting blocks into claims is a language judgment.",
                       "role": "requirement"}],
        "atoms": [{"kind": "requirement",
                   "quotes": ["a list item, or a fenced code block"]}],
    }]}
    backend = FakeBackend([answer])
    outcome = atomize_blocks([WRAPPED], backend)

    assert len(backend.asked) == 1
    assert outcome.failures == {}
    start, end = outcome.atoms[0].spans[0]
    assert WRAPPED["text"][start:end] == "a list item, or a\nfenced code block"


@pytest.mark.parametrize(
    "quote",
    [
        "a list item, or a compressed code block",   # a word changed
        "A LIST ITEM, or a fenced code block",       # case changed
        "a list item or a fenced code block",        # punctuation dropped
        "blocks are split into claims",              # paraphrase
    ],
)
def test_g2_still_rejects_anything_but_whitespace_differences(quote):
    answer = {"blocks": [{
        "block_id": WRAPPED["id"],
        "sentences": [{"quote": WRAPPED["text"], "role": "requirement"}],
        "atoms": [{"kind": "requirement", "quotes": [quote]}],
    }]}
    outcome = atomize_blocks([WRAPPED], FakeBackend([answer, answer]))
    assert WRAPPED["id"] in outcome.failures


QUOTED = {
    "id": "B-000011",
    "text": "> ⛔ **Coding gated (rel01 D20):** implementation does not start until G2, G3\n"
            "> and G4 are reviewed and the build plan exists.\n"
            "> **Governs:** `constitution.md` §6.",
    "heading_path": [],
    "kind": "paragraph",
    "table_header": None,
}


def test_a_quote_crossing_a_blockquote_marker_is_accepted_and_anchored_truly():
    """Markdown repeats `>` on every wrapped line; the model quotes the prose."""
    prose = "implementation does not start until G2, G3 and G4 are reviewed"
    answer = {"blocks": [{
        "block_id": QUOTED["id"],
        "sentences": [{"quote": prose, "role": "requirement"}],
        "atoms": [{"kind": "requirement", "quotes": [prose]}],
    }]}
    backend = FakeBackend([answer])
    outcome = atomize_blocks([QUOTED], backend)

    assert len(backend.asked) == 1
    assert outcome.failures == {}
    start, end = outcome.atoms[0].spans[0]
    assert QUOTED["text"][start:end] == (
        "implementation does not start until G2, G3\n> and G4 are reviewed"
    )


def test_a_quote_may_also_carry_the_markers_it_was_given():
    quoted = "does not start until G2, G3\n> and G4 are reviewed"
    answer = {"blocks": [{
        "block_id": QUOTED["id"],
        "sentences": [{"quote": quoted, "role": "requirement"}],
        "atoms": [{"kind": "requirement", "quotes": [quoted]}],
    }]}
    outcome = atomize_blocks([QUOTED], FakeBackend([answer]))
    assert outcome.failures == {}



def test_emphasis_marks_are_formatting_not_words():
    """Live: 14 of 20 acceptance-criteria blocks failed on `**Given**` quoted as `Given` (rel01 S22)."""
    block = {"id": "B-000012", "kind": "list_item", "heading_path": [], "table_header": None,
             "text": "- **AC-1.2** — **Given** a paragraph, **when** ingested, **then** it is a block."}
    quote = "Given a paragraph, when ingested, then it is a block."
    answer = {"blocks": [{"block_id": block["id"],
                          "sentences": [{"quote": quote, "role": "verification"}],
                          "atoms": [{"kind": "verification", "quotes": [quote]}]}]}
    outcome = atomize_blocks([block], FakeBackend([answer]))
    assert outcome.failures == {}
    start, end = outcome.atoms[0].spans[0]
    assert block["text"][start:end] == "Given** a paragraph, **when** ingested, **then** it is a block."
    assert "**Given" not in block["text"][start:end]


# -- rel01 D32: R5 backticks and R10 a sentence-initial capital are layout ----------------

def _one(block_text, quote):
    block = {"id": "B-000020", "kind": "paragraph", "heading_path": [], "table_header": None, "text": block_text}
    answer = {"blocks": [{"block_id": block["id"], "sentences": [{"quote": quote, "role": "requirement"}],
                          "atoms": [{"kind": "requirement", "quotes": [quote]}]}]}
    return block, atomize_blocks([block], FakeBackend([answer, answer]))


def test_r5_dropped_backticks_still_anchor():
    """Live gate: `SDD_COMPILER_CHILD=1` quoted without its backticks failed the block (G-7)."""
    block, outcome = _one("The child has `SDD_COMPILER_CHILD=1` set.", "The child has SDD_COMPILER_CHILD=1 set.")
    assert outcome.failures == {}
    start, end = outcome.atoms[0].spans[0]
    assert "SDD_COMPILER_CHILD=1" in block["text"][start:end]


def test_r10_a_lowercased_first_letter_still_anchors():
    """Live gate: "a Q-TERM…" for "A Q-TERM…" failed B-000410 in both runs (G-13)."""
    block, outcome = _one("A Q-TERM verdict merges at once.", "a Q-TERM verdict merges at once.")
    assert outcome.failures == {}
    assert outcome.atoms[0].spans == [(0, len(block["text"]))]


def test_r10_case_elsewhere_still_counts():
    _, outcome = _one("A Q-TERM verdict MUST merge.", "A Q-TERM verdict must merge.")
    assert "B-000020" in outcome.failures
