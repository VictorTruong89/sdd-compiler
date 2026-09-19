"""F1 §4 — stable block ids, and what changed since the last run (P-6).

A block keeps its id when its text is unchanged, even if it moved; it keeps its
id when it is edited in place; and an id is never reused once issued. Without
that, every edit would look like "everything deleted, everything added", and the
change detection the whole compiler rests on would be worthless.

Matching runs in three passes over one file's blocks, in the order the spec
gives:

1. **exact** — same normalized text and same heading path → `unchanged`;
2. **positional** — same heading path and same position under that heading →
   `changed`;
3. **the rest** — new blocks get new ids, old blocks become `removed`.

⚑ A `removed` record never matches again (F1 D12): re-adding deleted prose gives
a new id, so "this id existed, then was removed" stays a fact rather than
something that can be quietly undone.

The record stores **facts only** (F1 D13). What a run did to a block —
`new · changed · unchanged · removed` — is returned and reported, never stored,
and whether a block is still pending is derived from `atomized_hash`: a stored
per-run flag would flip to `unchanged` on the next run and silently drop blocks
the atomizer never reached.
"""
from __future__ import annotations

import hashlib
import re
from collections.abc import Iterable, Sequence
from dataclasses import dataclass, field
from typing import Any

from .segment import Segment

ID_PREFIX = "B-"
ID_DIGITS = 6

NEW = "new"
CHANGED = "changed"
UNCHANGED = "unchanged"
REMOVED = "removed"

#: CT-1.1, in the order records are written.
BLOCK_KEY_ORDER = (
    "id", "source", "kind", "heading_path", "lines", "text", "text_hash",
    "parent_block", "parent_relation", "table_header", "in_blockquote",
    "first_seen_run", "last_changed_run", "removed_run", "atomized_hash",
)

_TRAILING_WHITESPACE = re.compile(r"[ \t]+$", re.MULTILINE)
_BLANK_RUN = re.compile(r"\n{3,}")


def normalize(text: str) -> str:
    """Drop what never changes meaning; keep everything that does (F1 §4).

    Line endings, trailing whitespace and runs of blank lines are noise. Case,
    punctuation and inner spacing are not: "MUST" and "must", "5 GB" and "5GB",
    are different claims.
    """
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = _TRAILING_WHITESPACE.sub("", text)
    text = _BLANK_RUN.sub("\n\n", text)
    return text.strip("\n")


def text_hash(text: str) -> str:
    return "sha256:" + hashlib.sha256(normalize(text).encode("utf-8")).hexdigest()


@dataclass
class IdAllocator:
    """Issues block ids, and never issues one twice."""

    counter: int = 0

    @classmethod
    def from_records(cls, records: Iterable[dict[str, Any]]) -> IdAllocator:
        highest = 0
        for record in records:
            identifier = str(record.get("id", ""))
            if identifier.startswith(ID_PREFIX) and identifier[len(ID_PREFIX):].isdigit():
                highest = max(highest, int(identifier[len(ID_PREFIX):]))
        return cls(counter=highest)

    def next_id(self) -> str:
        self.counter += 1
        return f"{ID_PREFIX}{self.counter:0{ID_DIGITS}d}"


@dataclass
class ReconcileResult:
    """The file's blocks after a run, plus what the run did to each of them."""

    records: list[dict[str, Any]] = field(default_factory=list)
    counts: dict[str, int] = field(default_factory=dict)
    changes: dict[str, str] = field(default_factory=dict)   # block id -> delta


def is_live(record: dict[str, Any]) -> bool:
    return record.get("removed_run") is None


def pending_status(record: dict[str, Any], include_code: bool = False) -> str | None:
    """F1 D13 — `new` or `changed` if the atomizer still owes this block work, else None."""
    if not is_live(record):
        return None
    if record["kind"] == "code" and not include_code:
        return None
    atomized = record.get("atomized_hash")
    if atomized == record["text_hash"]:
        return None
    return NEW if atomized is None else CHANGED


def reconcile(
    existing: Sequence[dict[str, Any]],
    segments: Sequence[Segment],
    source: str,
    run: str,
    allocator: IdAllocator,
) -> ReconcileResult:
    """Match this run's segments against the file's known blocks."""
    live = [record for record in existing if is_live(record)]
    dead = [record for record in existing if not is_live(record)]

    matched: dict[int, dict[str, Any]] = {}   # segment index -> old record
    taken: set[str] = set()

    _match_exact(segments, live, matched, taken)
    _match_positional(segments, live, matched, taken)

    records: list[dict[str, Any]] = []
    ids: list[str] = []
    counts = {NEW: 0, CHANGED: 0, UNCHANGED: 0, REMOVED: 0}
    changes: dict[str, str] = {}

    for index, segment in enumerate(segments):
        old = matched.get(index)
        if old is None:
            identifier, status = allocator.next_id(), NEW
        else:
            identifier = old["id"]
            status = UNCHANGED if old["text_hash"] == text_hash(segment.text) else CHANGED
        ids.append(identifier)
        counts[status] += 1
        changes[identifier] = status
        records.append(_record(segment, identifier, source, status, run, old, ids))

    for record in live:
        if record["id"] not in taken:
            counts[REMOVED] += 1
            changes[record["id"]] = REMOVED
            records.append({**record, "removed_run": run})

    records.extend(dead)
    return ReconcileResult(records=records, counts=counts, changes=changes)


def _match_exact(
    segments: Sequence[Segment],
    live: Sequence[dict[str, Any]],
    matched: dict[int, dict[str, Any]],
    taken: set[str],
) -> None:
    """Same text, same heading path: the block moved at most."""
    index_by_key: dict[tuple[str, tuple[str, ...]], list[dict[str, Any]]] = {}
    for record in live:
        key = (record["text_hash"], tuple(record["heading_path"]))
        index_by_key.setdefault(key, []).append(record)

    for position, segment in enumerate(segments):
        key = (text_hash(segment.text), segment.heading_path)
        candidates = index_by_key.get(key, [])
        for record in candidates:
            if record["id"] not in taken:
                matched[position] = record
                taken.add(record["id"])
                break


def _match_positional(
    segments: Sequence[Segment],
    live: Sequence[dict[str, Any]],
    matched: dict[int, dict[str, Any]],
    taken: set[str],
) -> None:
    """Same heading path and same ordinal under it: the block was edited in place."""
    old_by_heading: dict[tuple[str, ...], list[dict[str, Any]]] = {}
    for record in live:
        old_by_heading.setdefault(tuple(record["heading_path"]), []).append(record)

    seen: dict[tuple[str, ...], int] = {}
    for position, segment in enumerate(segments):
        ordinal = seen.get(segment.heading_path, 0)
        seen[segment.heading_path] = ordinal + 1
        if position in matched:
            continue
        candidates = old_by_heading.get(segment.heading_path, [])
        if ordinal < len(candidates):
            record = candidates[ordinal]
            if record["id"] not in taken:
                matched[position] = record
                taken.add(record["id"])


def _record(
    segment: Segment,
    identifier: str,
    source: str,
    status: str,
    run: str,
    old: dict[str, Any] | None,
    ids: Sequence[str],
) -> dict[str, Any]:
    parent = ids[segment.parent_index] if segment.parent_index is not None else None
    changed_run = run if status in (NEW, CHANGED) else (old or {}).get("last_changed_run", run)
    return {
        "id": identifier,
        "source": source,
        "kind": segment.kind,
        "heading_path": list(segment.heading_path),
        "lines": [segment.lines[0], segment.lines[1]],
        "text": segment.text,
        "text_hash": text_hash(segment.text),
        "parent_block": parent,
        "parent_relation": segment.parent_relation,
        "table_header": segment.table_header,
        "in_blockquote": segment.in_blockquote,
        "first_seen_run": (old or {}).get("first_seen_run", run),
        "last_changed_run": changed_run,
        "removed_run": None,
        # Written only by the atomizer (F3 §4.5 step 8); ingest carries it forward.
        "atomized_hash": (old or {}).get("atomized_hash"),
    }
