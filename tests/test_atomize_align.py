"""T12 — identity across edits: new atoms aligned to a changed block's old nodes (F3 §4.6, P-6).

Tier: unit.
"""
from __future__ import annotations

from sdd_compiler.atomize.align import NewAtom, align


def old(node_id, text, subject="link", response="expire"):
    return {"id": node_id, "text": text, "canonical": {"subject": subject, "response": response}}


def new(index, text, subject="link", response="expire"):
    return NewAtom(index=index, text=text, subject=subject, response=response)


def test_identical_text_is_unchanged_and_keeps_its_id():
    result = align([old("N-000001", "Links must expire.")], [new(0, "Links must expire.")])
    assert result.assigned == {0: ("N-000001", "unchanged")}
    assert result.dropped == {}


def test_an_edited_claim_keeps_its_id():
    result = align([old("N-000001", "Links must expire after 30 days.")],
                   [new(0, "Links must expire after 31 days.")])
    assert result.assigned == {0: ("N-000001", "edited")}


def test_a_split_keeps_the_old_id_on_the_best_match_and_marks_the_other_split():
    result = align([old("N-000001", "Links must expire and must be revocable.")],
                   [new(0, "Links must expire."), new(1, "Links must be revocable and logged.")])
    kept = [i for i, (node, _) in result.assigned.items() if node == "N-000001"]
    assert len(kept) == 1
    other = 1 - kept[0]
    assert result.assigned[other] == (None, "split")


def test_a_merge_keeps_the_best_old_id_and_drops_the_other():
    result = align([old("N-000001", "Links must expire."), old("N-000002", "Links must be revocable.")],
                   [new(0, "Links must expire and must be revocable.")])
    [(kept, kind)] = result.assigned.values()
    assert kind == "edited" and kept in ("N-000001", "N-000002")
    assert list(result.dropped.values()) == ["merged"]


def test_unrelated_text_is_new_and_the_old_node_removed():
    result = align([old("N-000001", "Links must expire.")],
                   [new(0, "Invoices are archived yearly.", subject="invoice", response="be archived")])
    assert result.assigned == {0: (None, "new")}
    assert result.dropped == {"N-000001": "removed"}


def test_a_rewording_with_the_same_canonical_form_keeps_the_id():
    result = align([old("N-000001", "Share links must expire.", "share link", "expire")],
                   [new(0, "Every shared URL has to lapse eventually.", "share link", "expire")])
    assert result.assigned == {0: ("N-000001", "edited")}


def test_ties_break_by_id_so_the_result_is_deterministic():
    olds = [old("N-000002", "Links must expire."), old("N-000001", "Links must expire.")]
    result = align(olds, [new(0, "Links must expire.")])
    assert result.assigned == {0: ("N-000001", "unchanged")}


def test_a_case_change_is_an_edit_not_unchanged():
    """Live, T12: "run by a person" → "run BY a person" was kept as unchanged, with stale text."""
    result = align([old("N-000001", "One command, run by a person")],
                   [new(0, "One command, run BY a person")])
    assert result.assigned == {0: ("N-000001", "edited")}


def test_layout_alone_is_still_unchanged():
    result = align([old("N-000001", "Links must\nexpire.")], [new(0, "Links must expire.")])
    assert result.assigned == {0: ("N-000001", "unchanged")}
