"""T4 — F1 §4 identity and change detection (AC-1.8 … AC-1.12).

Tier: unit, with one property test for id reuse.
"""
from __future__ import annotations

from sdd_compiler.ingest.identity import (
    IdAllocator, heading_skipped, normalize, pending_status, reconcile, text_hash,
)
from sdd_compiler.ingest.segment import segment_markdown

SOURCE = "spec.md"

DOC = """\
## Behaviour
First paragraph.

- item one
- item two
"""


def compile_once(doc, existing=None, run="R-0001"):
    segments = segment_markdown(doc)
    allocator = IdAllocator.from_records(existing or [])
    return reconcile(existing or [], segments, source=SOURCE, run=run, allocator=allocator)


def by_text(records, fragment):
    return next(record for record in records if fragment in record["text"])


def delta(result, fragment):
    """What the run did to one block — reported, never stored (F1 D13)."""
    return result.changes[by_text(result.records, fragment)["id"]]


def atomized(records, *fragments):
    """Stand-in for the atomizer (F3 §4.5 step 8): mark these blocks processed."""
    return [
        {**record, "atomized_hash": record["text_hash"]}
        if any(fragment in record["text"] for fragment in fragments) else record
        for record in records
    ]


# -- normalization and hashing ---------------------------------------------

def test_normalization_keeps_meaning_and_drops_noise():
    assert normalize("a  \r\nb\t\n") == normalize("a\nb")
    assert normalize("a\n\n\n\nb") == normalize("a\n\nb")
    assert normalize("MUST") != normalize("must")
    assert normalize("5 GB") != normalize("5GB")


def test_hash_is_stable_and_prefixed():
    digest = text_hash("Files must be scanned.")
    assert digest.startswith("sha256:")
    assert digest == text_hash("Files must be scanned.  \n")


# -- the four outcomes ------------------------------------------------------

def test_first_ingest_makes_everything_new():
    result = compile_once(DOC)
    assert list(result.changes.values()) == ["new"] * 3
    assert [record["id"] for record in result.records] == ["B-000001", "B-000002", "B-000003"]
    assert result.counts == {"new": 3, "changed": 0, "unchanged": 0, "removed": 0}


def test_ac_1_8_re_ingesting_an_unchanged_file_changes_nothing():
    first = compile_once(DOC)
    second = compile_once(DOC, existing=first.records, run="R-0002")
    assert second.counts == {"new": 0, "changed": 0, "unchanged": 3, "removed": 0}
    assert [record["id"] for record in second.records] == ["B-000001", "B-000002", "B-000003"]
    assert [record["last_changed_run"] for record in second.records] == ["R-0001"] * 3


def test_ac_1_9_inserting_a_paragraph_above_keeps_every_existing_id():
    first = compile_once(DOC)
    edited = DOC.replace("First paragraph.", "Brand new paragraph.\n\nFirst paragraph.")
    second = compile_once(edited, existing=first.records, run="R-0002")

    assert second.counts == {"new": 1, "changed": 0, "unchanged": 3, "removed": 0}
    assert by_text(second.records, "First paragraph.")["id"] == "B-000001"
    assert by_text(second.records, "item two")["id"] == "B-000003"
    assert delta(second, "Brand new") == "new"
    assert by_text(second.records, "First paragraph.")["lines"] == [4, 4]


def test_ac_1_10_editing_one_item_keeps_its_id_and_leaves_the_others_alone():
    first = compile_once(DOC)
    second = compile_once(DOC.replace("item one", "item ONE"), existing=first.records, run="R-0002")

    edited = by_text(second.records, "item ONE")
    assert edited["id"] == "B-000002"
    assert delta(second, "item ONE") == "changed"
    assert edited["last_changed_run"] == "R-0002"
    assert edited["first_seen_run"] == "R-0001"
    assert second.counts == {"new": 0, "changed": 1, "unchanged": 2, "removed": 0}


def test_ac_1_11_a_deleted_block_is_kept_as_removed():
    first = compile_once(DOC)
    second = compile_once(DOC.replace("- item two\n", ""), existing=first.records, run="R-0002")

    gone = by_text(second.records, "item two")
    assert gone["removed_run"] == "R-0002"
    assert gone["id"] == "B-000003"
    assert second.changes["B-000003"] == "removed"
    assert second.counts == {"new": 0, "changed": 0, "unchanged": 2, "removed": 1}


def test_ac_1_11_a_removed_id_is_never_reused():
    first = compile_once(DOC)
    without = compile_once(DOC.replace("- item two\n", ""), existing=first.records, run="R-0002")
    restored = compile_once(DOC, existing=without.records, run="R-0003")

    assert by_text(restored.records, "item two")["id"] == "B-000004"
    removed = [r for r in restored.records if r["removed_run"] is not None]
    assert [r["id"] for r in removed] == ["B-000003"]


def test_ac_1_12_whitespace_and_line_endings_do_not_count_as_a_change():
    first = compile_once(DOC)
    noisy = DOC.replace("First paragraph.", "First paragraph.   ").replace("\n", "\r\n")
    second = compile_once(noisy, existing=first.records, run="R-0002")
    assert second.counts["changed"] == 0
    assert second.counts["unchanged"] == 3


def test_ac_1_12_a_case_change_is_a_change():
    first = compile_once(DOC)
    second = compile_once(DOC.replace("First", "FIRST"), existing=first.records, run="R-0002")
    assert second.counts["changed"] == 1


# -- record shape -----------------------------------------------------------

def test_records_match_ct_1_1():
    record = compile_once(DOC).records[0]
    assert set(record) == {
        "id", "source", "kind", "heading_path", "lines", "text", "text_hash",
        "parent_block", "parent_relation", "table_header", "in_blockquote",
        "first_seen_run", "last_changed_run", "removed_run", "atomized_hash",
    }
    assert record["removed_run"] is None
    assert record["atomized_hash"] is None
    assert record["source"] == SOURCE
    assert record["heading_path"] == ["Behaviour"]
    assert record["parent_block"] is None


def test_parent_index_becomes_a_parent_block_id():
    result = compile_once("- outer\n  - inner\n")
    outer, inner = result.records
    assert inner["parent_block"] == outer["id"]
    assert inner["parent_relation"] == "nested"


def test_ids_keep_growing_across_files():
    first = compile_once("Only paragraph.\n")
    allocator = IdAllocator.from_records(first.records)
    assert allocator.next_id() == "B-000002"


# -- the pending set is derived (F1 D13) --------------------------------------

def pending(records, include_code=False):
    return {
        record["id"]: pending_status(record, include_code)
        for record in records
        if pending_status(record, include_code) is not None
    }


def test_ac_1_31_unprocessed_blocks_stay_pending_across_runs():
    """The bug D13 fixes: a run that ended early must not lose its unprocessed blocks."""
    first = compile_once(DOC)
    second = compile_once(DOC, existing=first.records, run="R-0002")
    assert second.counts["unchanged"] == 3
    assert pending(second.records) == {"B-000001": "new", "B-000002": "new", "B-000003": "new"}


def test_ac_1_31_an_atomized_block_leaves_the_pending_set():
    first = compile_once(DOC)
    processed = atomized(first.records, "item one")
    second = compile_once(DOC, existing=processed, run="R-0002")
    assert pending(second.records) == {"B-000001": "new", "B-000003": "new"}


def test_ac_1_31_editing_an_atomized_block_makes_it_pending_as_changed():
    first = compile_once(DOC)
    processed = atomized(first.records, "item one")
    second = compile_once(DOC.replace("item one", "item ONE"), existing=processed, run="R-0002")
    assert pending(second.records)["B-000002"] == "changed"


def test_ingest_carries_atomized_hash_forward_untouched():
    first = compile_once(DOC)
    processed = atomized(first.records, "First paragraph.")
    second = compile_once(DOC, existing=processed, run="R-0002")
    record = by_text(second.records, "First paragraph.")
    assert record["atomized_hash"] == record["text_hash"]


def test_removed_and_code_blocks_are_not_pending():
    doc = DOC + "\n```\ncode\n```\n"
    first = compile_once(doc)
    second = compile_once(doc.replace("- item two\n", ""), existing=first.records, run="R-0002")
    ids = pending(second.records)
    assert "B-000003" not in ids                              # removed
    assert by_text(second.records, "code")["id"] not in ids   # code, not opted in
    assert by_text(second.records, "code")["id"] in pending(second.records, include_code=True)


# -- skipped headings (F1 D14) -------------------------------------------------

TRACEABILITY_DOC = """\
## 4. Behaviour
A share link must expire.

## 9. Traceability
| AC | Test | Code |
|---|---|---|
| AC-9.1 | `tests/test_x.py` | `src/x.py` |
"""


def test_ac_1_32_a_block_under_a_skipped_heading_is_stored_but_never_pending():
    records = compile_once(TRACEABILITY_DOC).records
    row = by_text(records, "AC-9.1")
    paragraph = by_text(records, "share link")
    assert row["kind"] == "table_row"                           # stored as usual
    assert pending_status(row, skip_headings=("Traceability",)) is None
    assert pending_status(paragraph, skip_headings=("Traceability",)) == "new"
    assert pending_status(row, skip_headings=()) == "new"


def test_ac_1_32_a_heading_matches_without_its_section_number_or_case():
    assert heading_skipped(["F1", "9. Traceability"], ("Traceability",))
    assert heading_skipped(["F1", "4.10 traceability"], ("TRACEABILITY",))
    assert heading_skipped(["Traceability", "Details"], ("Traceability",))     # any level
    assert not heading_skipped(["F1", "9. Traceability matrix"], ("Traceability",))
    assert not heading_skipped(["F1", "Behaviour"], ())
