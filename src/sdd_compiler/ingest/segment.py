"""F1 §4 — split Markdown into blocks, deterministically and without a model.

A block is a *structural* unit: a paragraph, a list item, a table body row, or a
fenced code block. Splitting a paragraph into claims is a language judgment and
belongs to the atomizer (F3), so nothing here looks at meaning.

Two properties the rest of the compiler depends on:

- **`text` is the verbatim source slice** of `lines`, so a quote found in a block
  can be anchored back to the file by offset (F3 guard G2);
- a block that belongs to a list item says so: `parent_relation` is `nested` for a
  sub-item and `continuation` for a second paragraph inside one item (F1 D11);
- the result depends only on the input text, so a run is reproducible (F4 AC-4.3).

Line numbers are 1-based and inclusive; `markdown-it-py` reports 0-based
half-open ranges, and the conversion happens in one place (`_lines`).
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from markdown_it import MarkdownIt

_FRONT_MATTER = re.compile(r"\A---\n.*?\n---[ \t]*(?:\n|\Z)", re.DOTALL)

#: Kinds a block may have (F1 CT-1.1).
PARAGRAPH = "paragraph"
LIST_ITEM = "list_item"
TABLE_ROW = "table_row"
CODE = "code"


#: How a block relates to its parent block (F1 D11).
NESTED = "nested"
CONTINUATION = "continuation"


@dataclass(frozen=True)
class Segment:
    """One block, before it is given an id (ids are assigned by identity, T4)."""

    kind: str
    text: str
    lines: tuple[int, int]
    heading_path: tuple[str, ...]
    parent_index: int | None = None
    parent_relation: str | None = None
    table_header: str | None = None
    in_blockquote: bool = False


def segment_markdown(source: str) -> list[Segment]:
    """Split one Markdown document into blocks, in source order."""
    text = _blank_out_front_matter(source)
    lines = text.split("\n")
    tokens = _parser().parse(text)
    return _Walker(lines).walk(tokens)


def _parser() -> MarkdownIt:
    # CommonMark plus tables: tables carry acceptance criteria in real spec sets.
    return MarkdownIt("commonmark").enable("table")


def _blank_out_front_matter(source: str) -> str:
    """Replace YAML front matter with blank lines, keeping every line number intact."""
    match = _FRONT_MATTER.match(source)
    if not match:
        return source
    blanks = "\n" * match.group(0).count("\n")
    return blanks + source[match.end() :]


class _Walker:
    """Turn a token stream into blocks, tracking headings, lists and blockquotes."""

    def __init__(self, lines: list[str]) -> None:
        self._lines = lines
        self._segments: list[Segment] = []
        self._headings: list[tuple[int, str]] = []
        # One entry per open list item: the index of the block that item emitted,
        # or None until it emits one. A continuation belongs to that block (F1 D11).
        self._list_item_stack: list[dict[str, int | None]] = []
        self._blockquote_depth = 0
        self._in_heading = False
        self._heading_level = 0
        self._table_header: str | None = None
        self._in_thead = False

    def walk(self, tokens: list[Any]) -> list[Segment]:
        for index, token in enumerate(tokens):
            handler = getattr(self, f"_on_{token.type}", None)
            if handler is not None:
                handler(token, tokens, index)
        return self._segments

    # -- headings --------------------------------------------------------
    def _on_heading_open(self, token: Any, tokens: list[Any], index: int) -> None:
        self._in_heading = True
        self._heading_level = int(token.tag[1:])

    def _on_heading_close(self, token: Any, tokens: list[Any], index: int) -> None:
        self._in_heading = False

    def _on_inline(self, token: Any, tokens: list[Any], index: int) -> None:
        if not self._in_heading:
            return
        while self._headings and self._headings[-1][0] >= self._heading_level:
            self._headings.pop()
        self._headings.append((self._heading_level, token.content.strip()))

    # -- containers ------------------------------------------------------
    def _on_blockquote_open(self, *_: Any) -> None:
        self._blockquote_depth += 1

    def _on_blockquote_close(self, *_: Any) -> None:
        self._blockquote_depth -= 1

    def _on_list_item_open(self, token: Any, tokens: list[Any], index: int) -> None:
        # The item's own block is emitted by the first paragraph inside it.
        self._list_item_stack.append({"emitted": None})

    def _on_list_item_close(self, *_: Any) -> None:
        if self._list_item_stack:
            self._list_item_stack.pop()

    # -- leaf blocks -----------------------------------------------------
    def _on_paragraph_open(self, token: Any, tokens: list[Any], index: int) -> None:
        start, end = _lines(token)
        item = self._list_item_stack[-1] if self._list_item_stack else None

        if item is None:
            self._emit(PARAGRAPH, start, end)
            return

        if item["emitted"] is None:
            # The item's own block. Its parent, if any, is the enclosing item.
            parent = self._list_item_stack[-2]["emitted"] if len(self._list_item_stack) > 1 else None
            item["emitted"] = len(self._segments)
            self._emit(
                LIST_ITEM, start, end,
                parent_index=parent,
                parent_relation=NESTED if parent is not None else None,
            )
            return

        # A second paragraph inside the same item: it continues that item (F1 D11).
        self._emit(PARAGRAPH, start, end, parent_index=item["emitted"], parent_relation=CONTINUATION)

    def _on_fence(self, token: Any, tokens: list[Any], index: int) -> None:
        start, end = _lines(token)
        item = self._list_item_stack[-1] if self._list_item_stack else None
        if item is not None and item["emitted"] is not None:
            self._emit(CODE, start, end, parent_index=item["emitted"], parent_relation=CONTINUATION)
        else:
            self._emit(CODE, start, end)

    # -- tables ----------------------------------------------------------
    def _on_thead_open(self, *_: Any) -> None:
        self._in_thead = True

    def _on_thead_close(self, *_: Any) -> None:
        self._in_thead = False

    def _on_tr_open(self, token: Any, tokens: list[Any], index: int) -> None:
        start, end = _lines(token)
        if self._in_thead:
            self._table_header = self._slice(start, end)
            return
        self._emit(TABLE_ROW, start, end, table_header=self._table_header)

    def _on_table_close(self, *_: Any) -> None:
        self._table_header = None

    # -- helpers ---------------------------------------------------------
    def _emit(
        self,
        kind: str,
        start: int,
        end: int,
        parent_index: int | None = None,
        parent_relation: str | None = None,
        table_header: str | None = None,
    ) -> None:
        self._segments.append(
            Segment(
                kind=kind,
                text=self._slice(start, end),
                lines=(start, end),
                heading_path=tuple(text for _, text in self._headings),
                parent_index=parent_index,
                parent_relation=parent_relation,
                table_header=table_header,
                in_blockquote=self._blockquote_depth > 0,
            )
        )

    def _slice(self, start: int, end: int) -> str:
        """The verbatim source lines, 1-based and inclusive."""
        return "\n".join(self._lines[start - 1 : end]).rstrip()


def _lines(token: Any) -> tuple[int, int]:
    """markdown-it's 0-based half-open `map` as 1-based inclusive lines."""
    start, end = token.map
    return start + 1, end
