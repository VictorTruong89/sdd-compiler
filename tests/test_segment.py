"""T3 — F1 §4 segmentation: Markdown into blocks, deterministically.

Covers F1 AC-1.1 … AC-1.7. Tier: unit.
"""
from __future__ import annotations

from sdd_compiler.ingest.segment import Segment, segment_markdown

AC_1_1_DOC = """\
# Feature

## Behaviour
First paragraph.

Second paragraph.

Third paragraph.

- item one
- item two

| AC | Tier |
|---|---|
| AC-1.1 | unit |
| AC-1.2 | contract |
"""


def kinds(segments: list[Segment]) -> list[str]:
    return [segment.kind for segment in segments]


def test_ac_1_1_block_kinds_positions_and_heading_paths():
    """AC-1.1 — 3 paragraphs, a 2-item list, a table with 2 body rows = 7 blocks."""
    segments = segment_markdown(AC_1_1_DOC)
    assert len(segments) == 7
    assert kinds(segments) == [
        "paragraph", "paragraph", "paragraph",
        "list_item", "list_item",
        "table_row", "table_row",
    ]
    assert segments[0].text == "First paragraph."
    assert segments[0].lines == (4, 4)
    assert segments[3].text == "- item one"
    assert segments[3].lines == (10, 10)
    assert segments[5].text == "| AC-1.1 | unit |"
    assert segments[5].lines == (15, 15)
    assert all(segment.heading_path == ("Feature", "Behaviour") for segment in segments)


def test_ac_1_2_heading_path_tracks_nesting_and_headings_are_not_blocks():
    doc = "## A\n\npara a\n\n### B\n\npara b\n\n## C\n\npara c\n"
    segments = segment_markdown(doc)
    assert kinds(segments) == ["paragraph", "paragraph", "paragraph"]
    assert segments[0].heading_path == ("A",)
    assert segments[1].heading_path == ("A", "B")
    assert segments[2].heading_path == ("C",)


def test_ac_1_3_nested_list_items_are_separate_blocks_with_a_parent():
    doc = "- outer\n  - inner\n- sibling\n"
    segments = segment_markdown(doc)
    assert kinds(segments) == ["list_item", "list_item", "list_item"]
    assert segments[0].text == "- outer"
    assert segments[1].text == "  - inner"
    assert segments[1].parent_index == 0
    assert segments[1].parent_relation == "nested"
    assert segments[0].parent_index is None
    assert segments[2].parent_index is None


def test_ac_1_4_table_rows_carry_the_header_and_no_block_for_header_or_delimiter():
    doc = "| AC | Tier |\n|---|---|\n| AC-1.1 | unit |\n"
    segments = segment_markdown(doc)
    assert len(segments) == 1
    assert segments[0].kind == "table_row"
    assert segments[0].text == "| AC-1.1 | unit |"
    assert segments[0].table_header == "| AC | Tier |"
    assert segments[0].lines == (3, 3)


def test_ac_1_5_blockquote_content_keeps_its_kind_and_is_flagged():
    doc = "> ⚠ Tokens must never be logged.\n"
    segments = segment_markdown(doc)
    assert len(segments) == 1
    assert segments[0].kind == "paragraph"
    assert segments[0].in_blockquote is True
    assert segments[0].text == "> ⚠ Tokens must never be logged."


def test_ac_1_6_fenced_code_is_one_block_of_kind_code():
    doc = 'Intro.\n\n```json\n{"a": 1}\n```\n'
    segments = segment_markdown(doc)
    assert kinds(segments) == ["paragraph", "code"]
    assert segments[1].lines == (3, 5)
    assert segments[1].text.startswith("```json")
    assert segments[1].text.rstrip().endswith("```")


def test_ac_1_7_front_matter_comments_and_rules_produce_no_block():
    doc = (
        "---\ntitle: x\n---\n\n<!-- a comment -->\n\n---\n\nReal paragraph.\n"
    )
    segments = segment_markdown(doc)
    assert kinds(segments) == ["paragraph"]
    assert segments[0].text == "Real paragraph."
    assert segments[0].lines == (9, 9)


def test_text_is_the_verbatim_source_slice(tmp_path):
    """CT-1.1 — `text` is exactly the source lines, not a re-rendering."""
    doc = "Line one\nstill the same paragraph.\n"
    segments = segment_markdown(doc)
    assert segments[0].text == "Line one\nstill the same paragraph."
    assert segments[0].lines == (1, 2)


def test_segmentation_is_deterministic():
    first = segment_markdown(AC_1_1_DOC)
    second = segment_markdown(AC_1_1_DOC)
    assert first == second


def test_an_empty_document_has_no_blocks():
    assert segment_markdown("") == []
    assert segment_markdown("\n\n   \n") == []


def test_ordered_lists_are_list_items_too():
    segments = segment_markdown("1. first\n2. second\n")
    assert kinds(segments) == ["list_item", "list_item"]
    assert segments[1].text == "2. second"


def test_ac_1_30_a_continuation_paragraph_belongs_to_its_item():
    """AC-1.30 (F1 D11) — a second paragraph inside one list item names that item."""
    segments = segment_markdown("- first para\n\n  second para in same item\n\n- next item\n")
    assert kinds(segments) == ["list_item", "paragraph", "list_item"]
    assert segments[1].parent_index == 0
    assert segments[1].parent_relation == "continuation"
    assert segments[0].parent_relation is None
    assert segments[2].parent_index is None


def test_ac_1_30_nested_items_are_marked_nested_not_continuation():
    segments = segment_markdown("- outer\n  - inner\n")
    assert segments[1].parent_index == 0
    assert segments[1].parent_relation == "nested"


def test_ac_1_30_a_code_fence_inside_an_item_continues_it():
    doc = "- the rule:\n\n  ```json\n  {\"a\": 1}\n  ```\n"
    segments = segment_markdown(doc)
    assert kinds(segments) == ["list_item", "code"]
    assert segments[1].parent_index == 0
    assert segments[1].parent_relation == "continuation"


def test_a_top_level_block_has_no_parent():
    segments = segment_markdown("Just a paragraph.\n\n```txt\ncode\n```\n")
    assert all(segment.parent_index is None for segment in segments)
    assert all(segment.parent_relation is None for segment in segments)


def test_deeper_nesting_points_at_the_immediate_parent():
    segments = segment_markdown("- a\n  - b\n    - c\n")
    assert [segment.parent_index for segment in segments] == [None, 0, 1]
