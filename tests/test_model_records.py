"""T9 — F2 §5 record contracts, §4.8 ids, keywords (AC-2.14, AC-2.17 … AC-2.21).

Tier: contract, unit and property.
"""
from __future__ import annotations

import copy
import random

import pytest

from sdd_compiler.errors import SddcError
from sdd_compiler.model.ids import (IdCounter, adopt_human_ids, find_human_id, find_local_label,
                                   human_labels, term_id)
from sdd_compiler.model.keywords import STOP_WORDS, STOP_WORDS_VERSION, keywords
from sdd_compiler.model.schema import RecordError, validate

NODE = {
    "id": "N-000042",
    "kind": "requirement",
    "source": {"file": "sdd/specs/F9/spec.md", "block_id": "B-000123",
               "heading_path": ["Sharing"], "lines": [42, 42], "spans": [[0, 52]]},
    "text": "A share link must expire 30 days after it is created.",
    "canonical": {"state": None, "trigger": None, "scope": None, "subject": "share link",
                  "modality": "MUST", "response": "expire 30 days after it is created",
                  "quantities": [{"value": 30, "unit": "day",
                                  "normalized": {"value": 2592000, "unit": "s"},
                                  "quote": "30 days"}]},
    "terms": [{"term": "term:share_link", "role": "subject", "quote": "share link"}],
    "label": None,
    "primary_term": "term:share_link",
    "layer": "L1",
    "layer_answers": {"Q3": {"answer": "yes", "quote": "expire 30 days after it is created"}},
    "layer_hint": None,
    "family": "term:share_link",
    "family_rule": "subject",
    "components": [],
    "scope_selector": None,
    "verifies": None,
    "decision": None,
    "annotations": [],
    "keywords": ["created", "expire", "link", "share"],
    "ambiguity": [],
    "conflict_ids": [],
    "related_conflict_nodes": [],
    "stale_reasons": [],
    "last_checked_run": None,
    "flags": [],
    "status": "unchecked",
    "judgments": ["J-000321"],
}


def changed(**fields):
    record = copy.deepcopy(NODE)
    record.update(fields)
    return record


# -- AC-2.17, AC-2.14, AC-2.18 --------------------------------------------------

def test_a_valid_node_passes():
    validate("node", NODE)


@pytest.mark.parametrize(
    ("record", "field"),
    [
        ({k: v for k, v in NODE.items() if k != "layer"}, "layer"),
        (changed(layer="L9"), "layer"),
        (changed(kind="wish"), "kind"),
        (changed(canonical={**NODE["canonical"], "modality": "MIGHT"}), "canonical/modality"),
        (changed(ambiguity=[{"kind": "spooky", "quote": None, "detail": ""}]), "ambiguity/0/kind"),
    ],
)
def test_ac_2_17_a_bad_node_is_rejected_naming_the_field(record, field):
    with pytest.raises(RecordError) as error:
        validate("node", record)
    assert field in str(error.value)


def test_ac_2_17_a_judged_link_needs_its_judgment():
    link = {"from": "N-000001", "type": "refines", "to": "N-000002", "provenance": "judgment",
            "judgment": None, "rationale": None, "quotes": []}
    with pytest.raises(RecordError) as error:
        validate("link", link)
    assert "judgment" in str(error.value)


def test_a_code_link_and_a_term_pass():
    validate("link", {"from": "N-000001", "type": "uses_term", "to": "term:file",
                      "provenance": "code", "judgment": None, "rationale": None, "quotes": []})
    validate("term", {"id": "term:share_link", "canonical": "share link", "aliases": [],
                      "kind": "entity", "definition": None, "defined_by": None, "status": "proposed", "broader": None})


def test_a_conflict_record_needs_two_sorted_members():
    base = {"id": "CF-000001", "kind": "contradiction", "members": ["N-000001", "N-000002"],
            "rationale": "r", "quotes": {}, "state": "open", "resolved_reason": None,
            "detected_run": "R-0001", "resolved_run": None, "judgment": "J-000001"}
    validate("conflict", base)
    for members in (["N-000001"], ["N-000002", "N-000001"]):
        with pytest.raises(RecordError) as error:
            validate("conflict", {**base, "members": members})
        assert "members" in str(error.value)


def test_ac_2_14_a_stored_status_that_disagrees_with_the_facts_is_rejected():
    with pytest.raises(RecordError) as error:
        validate("node", changed(status="validated"))
    assert "status" in str(error.value)


def test_d14_null_modality_needs_its_ambiguity():
    bare = changed(canonical={**NODE["canonical"], "modality": None})
    with pytest.raises(RecordError) as error:
        validate("node", bare)
    assert "modality" in str(error.value)
    flagged = changed(canonical=bare["canonical"], status="ambiguous",
                      ambiguity=[{"kind": "missing_modality", "quote": None, "detail": ""}])
    validate("node", flagged)


@pytest.mark.parametrize(
    ("record", "field"),
    [
        (changed(scope_selector={"families": [], "layers": [], "terms": [], "categories": []}),
         "scope_selector"),
        (changed(decision={"chosen": "x", "rejected": [], "affects": []}), "decision"),
        (changed(verifies=["N-000001"]), "verifies"),
    ],
)
def test_ac_2_18_kind_specific_fields_only_on_their_kind(record, field):
    with pytest.raises(RecordError) as error:
        validate("node", record)
    assert field in str(error.value)


def test_ac_2_18_a_decision_needs_chosen():
    decision = changed(kind="decision", canonical={**NODE["canonical"], "modality": None},
                       decision={"rejected": [], "affects": []})
    with pytest.raises(RecordError) as error:
        validate("node", decision)
    assert "chosen" in str(error.value)


# -- AC-2.19 human ids ------------------------------------------------------------

@pytest.mark.parametrize(
    ("text", "kind", "found"),
    [
        ("- **AC-1.4** *(idempotent)* — **Given** …", "list_item", "AC-1.4"),
        ("**CT-2.1 — Node record**", "paragraph", "CT-2.1"),
        ("AC-12.30 covers it.", "paragraph", "AC-12.30"),
        ("AC-2.1.", "paragraph", "AC-2.1"),                     # sentence-final period
        ("AC-2.1.3 is not an id form", "paragraph", None),
        ("See AC-1.4 for details.", "paragraph", None),         # a mention, not a label
        ("| AC-1.4 | tests/test_x.py |", "table_row", None),     # traceability rows never adopt
        ("- **D9 — Lock wait 15 seconds**", "list_item", None),  # spec-scoped: not unique
    ],
)
def test_ac_2_19_only_a_repository_unique_label_is_a_human_id(text, kind, found):
    assert find_human_id({"text": text, "kind": kind}) == found


def test_ac_2_19_a_unique_human_id_is_adopted_when_its_block_forms_one_node():
    blocks = {
        "B-1": {"text": "- **AC-1.4** — Given …", "kind": "list_item", "source": "a.md", "lines": [5, 5]},
        "B-2": {"text": "- **AC-1.5** — Given … and …", "kind": "list_item", "source": "a.md", "lines": [6, 6]},
    }
    adopted = adopt_human_ids(blocks, atoms_per_block={"B-1": 1, "B-2": 2})
    assert adopted == {"B-1": "AC-1.4"}


def test_ac_2_19_a_duplicate_human_id_fails_the_build_naming_both_places():
    blocks = {
        "B-1": {"text": "- **AC-1.4** — Given …", "kind": "list_item", "source": "a.md", "lines": [5, 5]},
        "B-9": {"text": "- **AC-1.4** — Given …", "kind": "list_item", "source": "b.md", "lines": [8, 9]},
    }
    with pytest.raises(SddcError) as error:
        adopt_human_ids(blocks, atoms_per_block={"B-1": 1, "B-9": 1})
    assert "a.md:5" in str(error.value) and "b.md:8" in str(error.value)


def test_d12_every_node_of_a_labelled_block_carries_the_label():
    """F2 Q4 option c: an AC split into three nodes keeps "AC-1.5" on all three."""
    blocks = {
        "B-1": {"text": "- **AC-1.4** — Given …", "kind": "list_item", "source": "a.md", "lines": [5, 5]},
        "B-2": {"text": "- **AC-1.5** — Given … and …", "kind": "list_item", "source": "a.md", "lines": [6, 6]},
        "B-3": {"text": "Plain prose.", "kind": "paragraph", "source": "a.md", "lines": [7, 7]},
    }
    assert human_labels(blocks, {"B-1": 1, "B-2": 3, "B-3": 1}) == {"B-1": "AC-1.4", "B-2": "AC-1.5"}


@pytest.mark.parametrize(
    ("text", "kind", "found"),
    [
        ("| **S1 same family** | Same `family` | family id |", "table_row", "S1"),
        ("| T1 | F1/F3/F6 write records | `transaction` |", "table_row", "T1"),
        ("- **D1 — ⚑ Two extra candidate sources**", "list_item", "D1"),
        ("| AC-1.4 | tests/test_x.py |", "table_row", None),     # a global id is never local
        ("- **AC-1.4** — Given …", "list_item", None),
        ("See S1 for details.", "paragraph", None),              # a mention
        ("- S1 is plain", "list_item", None),                    # a list item needs the bold lead
        ("| Source | Rule |", "table_row", None),
    ],
)
def test_f2_d20_a_local_label_names_a_row_or_item_inside_one_file(text, kind, found):
    """F2 D20 (M3 gate, I-56): F5's criteria cite "S1" … "S7", ids unique only inside F5."""
    assert find_local_label({"text": text, "kind": kind}) == found


def test_d12_a_label_is_part_of_the_node_contract():
    validate("node", changed(label="AC-1.5"))
    validate("node", changed(label="S1"))                    # F2 D20, a local label
    with pytest.raises(RecordError) as error:
        validate("node", changed(label="see AC-1.5"))
    assert "label" in str(error.value)


# -- AC-2.20 id counters ------------------------------------------------------------

def test_ac_2_20_a_deleted_id_is_never_issued_again():
    counter = IdCounter("N-", start=0)
    issued = [counter.next_id() for _ in range(7)]
    assert issued[-1] == "N-000007"
    # N-000007 is deleted; the counter is never rewound.
    assert counter.next_id() == "N-000008"
    assert counter.value == 8


def test_ac_2_20_property_ids_stay_unique_through_any_create_delete_sequence():
    rng = random.Random(20260919)
    counter = IdCounter("N-", start=0)
    live, ever = set(), set()
    for _ in range(2000):
        if live and rng.random() < 0.4:
            live.discard(rng.choice(sorted(live)))
        else:
            new = counter.next_id()
            assert new not in ever
            ever.add(new)
            live.add(new)


def test_term_ids_are_snake_case_from_the_canonical_name():
    assert term_id("Share link") == "term:share_link"
    assert term_id("  ID-families / test tiers ") == "term:id_families_test_tiers"


# -- AC-2.21 keywords -------------------------------------------------------------------

def test_ac_2_21_keywords_are_deterministic_and_free_of_stop_words():
    text = "A share link must expire 30 days after it is created; the link is shared."
    first, second = keywords(text), keywords(text)
    assert first == second == sorted(set(first))
    assert not set(first) & STOP_WORDS
    assert {"share", "link", "expire", "created"} <= set(first)
    assert "30" not in first
    assert STOP_WORDS_VERSION
