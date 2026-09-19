"""F3 §4.6 — identity across edits: a changed block's new atoms keep its old nodes' ids (P-6).

Without this, every edit would look like "node deleted, node added": judgments,
conflict records and links about a claim would be thrown away because one word
changed.

Matching, deterministic, one-to-one:

1. **text overlap** — `difflib` ratio of the old node's text and the new atom's
   text, normalized (case, whitespace, `*` and backticks); pairs at or above
   `MIN_OVERLAP` are taken best first, ties by old id then atom order;
2. **same canonical form** — for what is left, equal `subject` and `response`.

Outcomes: `unchanged` (same text up to whitespace — case counts: same id, record kept), `edited` (same id, new
content), `split` (a new atom overlapping an old node another atom kept: new id),
`new`, and for old nodes not kept: `merged` (it overlapped a kept atom) or
`removed`. Both are deleted with the F2 §4.9 cascade.

⚑ F3 D22: "span overlap" in §4.6 is computed as text overlap, because the old
block's text is gone once ingest has replaced it; the old node's `text` is what
remains of its spans.
"""
from __future__ import annotations

import difflib
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any

MIN_OVERLAP = 0.5


@dataclass(frozen=True)
class NewAtom:
    index: int
    text: str
    subject: str
    response: str


@dataclass
class Alignment:
    assigned: dict[int, tuple[str | None, str]] = field(default_factory=dict)   # atom -> (old id, kind)
    dropped: dict[str, str] = field(default_factory=dict)                        # old id -> merged|removed


def align(old_nodes: Sequence[Mapping[str, Any]], atoms: Sequence[NewAtom]) -> Alignment:
    result = Alignment()
    scores = {(o["id"], a.index): _overlap(o["text"], a.text) for o in old_nodes for a in atoms}
    taken_old: set[str] = set()

    for (old_id, index), score in sorted(scores.items(), key=lambda kv: (-kv[1], kv[0][0], kv[0][1])):
        if score < MIN_OVERLAP or old_id in taken_old or index in result.assigned:
            continue
        old = next(o for o in old_nodes if o["id"] == old_id)
        atom = next(a for a in atoms if a.index == index)
        same = _layout(old["text"]) == _layout(atom.text)
        result.assigned[index] = (old_id, "unchanged" if same else "edited")
        taken_old.add(old_id)

    for atom in atoms:
        if atom.index in result.assigned:
            continue
        for old in sorted(old_nodes, key=lambda o: o["id"]):
            if old["id"] in taken_old:
                continue
            canonical = old.get("canonical") or {}
            if (_norm(canonical.get("subject", "")) == _norm(atom.subject)
                    and _norm(canonical.get("response", "")) == _norm(atom.response)):
                result.assigned[atom.index] = (old["id"], "edited")
                taken_old.add(old["id"])
                break

    kept = {old_id for old_id, _ in result.assigned.values() if old_id}
    for atom in atoms:
        if atom.index not in result.assigned:
            overlaps_kept = any(scores[(k, atom.index)] >= MIN_OVERLAP for k in kept)
            result.assigned[atom.index] = (None, "split" if overlaps_kept else "new")
    assigned_atoms = [i for i, (old_id, _) in result.assigned.items() if old_id]
    for old in old_nodes:
        if old["id"] not in kept:
            merged = any(scores[(old["id"], i)] >= MIN_OVERLAP for i in assigned_atoms)
            result.dropped[old["id"]] = "merged" if merged else "removed"
    return result


def _overlap(a: str, b: str) -> float:
    return difflib.SequenceMatcher(None, _norm(a), _norm(b)).ratio()


def _norm(text: str) -> str:
    """For *scoring* only: case and inline marks do not make two texts less alike."""
    return " ".join(text.replace("*", "").replace("`", "").lower().split())


def _layout(text: str) -> str:
    """For *equality*: only whitespace may differ — case is meaning (F1 §4 normalization)."""
    return " ".join(text.split())
