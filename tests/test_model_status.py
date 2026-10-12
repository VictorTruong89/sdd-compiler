"""T9 — F2 §4.6, §4.7 status derivation and conflict membership (AC-2.12 … AC-2.16).

Tier: unit and property.
"""
from __future__ import annotations

import itertools

import pytest

from sdd_compiler.model.status import derive_status, refresh_conflict_fields


def node(conflict=False, ambiguous=False, stale=False, checked=False):
    return {
        "conflict_ids": ["CF-000001"] if conflict else [],
        "ambiguity": [{"kind": "vague_term", "quote": "fast", "detail": ""}] if ambiguous else [],
        "stale_reasons": [{"link": ["N-1", "refines", "N-2"], "since_run": "R-0002"}] if stale else [],
        "last_checked_run": "R-0001" if checked else None,
    }


def test_ac_2_12_conflict_beats_ambiguity():
    assert derive_status(node(conflict=True, ambiguous=True)) == "conflict"


@pytest.mark.parametrize("facts", list(itertools.product([False, True], repeat=4)))
def test_ac_2_12_precedence_over_every_combination(facts):
    conflict, ambiguous, stale, checked = facts
    expected = (
        "conflict" if conflict else
        "ambiguous" if ambiguous else
        "stale" if stale else
        "unchecked" if not checked else
        "validated"
    )
    assert derive_status(node(*facts)) == expected


def test_ac_2_13_a_fresh_node_is_unchecked_never_validated():
    assert derive_status(node()) == "unchecked"


def record(cf_id, members, state="open"):
    return {"id": cf_id, "members": sorted(members), "state": state}


def test_ac_2_15_related_nodes_are_the_union_of_other_members_of_open_records():
    records = [
        record("CF-000001", ["N-000001", "N-000002"]),
        record("CF-000002", ["N-000001", "N-000003", "N-000002"]),
        record("CF-000003", ["N-000001", "N-000009"], state="resolved"),
        record("CF-000004", ["N-000004", "N-000005"]),
    ]
    refreshed = refresh_conflict_fields({"id": "N-000001", **node()}, records)
    assert refreshed["conflict_ids"] == ["CF-000001", "CF-000002"]
    assert refreshed["related_conflict_nodes"] == ["N-000002", "N-000003"]
    assert refreshed["status"] == "conflict"


def test_ac_2_16_resolving_the_only_record_clears_the_fields():
    records = [record("CF-000001", ["N-000001", "N-000002"], state="resolved")]
    before = {"id": "N-000001", **node(conflict=True, checked=True)}
    refreshed = refresh_conflict_fields(before, records)
    assert refreshed["conflict_ids"] == []
    assert refreshed["related_conflict_nodes"] == []
    assert refreshed["status"] == "validated"
