"""F2 §4.8 — ids: assigned once, never reused, never encoding layer, family or status.

Node ids are `N-000001`… unless the source already names the claim (P-12): an
author who wrote `AC-1.4` should find node `AC-1.4`, not `N-000317`.

⚑ Which human ids are adopted (F2 D10, found while building T9):

- only families unique across the whole repository by construction —
  `AC-<n>.<k>` and `CT-<n>.<k>`, which embed their spec number. `D<n>`, `Q<n>`
  and `T<n>` are unique only inside one spec (constitution §1), so F1 D9 and F3 D9
  would "collide" and fail every multi-spec build;
- only as the **label** of a paragraph or list item — the id at its start, as in
  `- **AC-1.4** …`. A mention ("see AC-1.4") and a traceability table row are
  not the claim itself;
- only when the block forms **exactly one** node; a block split into several
  atoms cannot give one id to all of them, so they get `N-` ids.

Whatever the id, **every** node formed from a labelled block carries the human
id as its `label` (F2 D12), so "which nodes came from AC-1.8" is a query.
"""
from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from ..errors import ExitCode, SddcError

ID_DIGITS = 6
_HUMAN_ID = re.compile(
    r"^(?:[-*+]\s+|\d+[.)]\s+)?(?:\*\*|__)?(?P<id>(?:AC|CT)-\d+\.\d+)(?!\w|\.\d)"
)
_LABELLED_KINDS = ("paragraph", "list_item")


@dataclass
class IdCounter:
    """A monotonic counter; F4 persists `value` in `graph.meta.json` (AC-2.20)."""

    prefix: str
    start: int = 0

    def __post_init__(self) -> None:
        self.value = self.start

    def next_id(self) -> str:
        self.value += 1
        return f"{self.prefix}{self.value:0{ID_DIGITS}d}"


def term_id(name: str) -> str:
    """`term:<snake_case>` from a canonical name; never renamed afterwards."""
    slug = re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")
    return f"term:{slug}"


def find_human_id(block: Mapping[str, Any]) -> str | None:
    if block.get("kind") not in _LABELLED_KINDS:
        return None
    match = _HUMAN_ID.match(block["text"].lstrip())
    return match.group("id") if match else None


def human_labels(
    blocks: Mapping[str, Mapping[str, Any]], atoms_per_block: Mapping[str, int]
) -> dict[str, str]:
    """Block id → human id, for every node-forming labelled block (F2 D12).

    A human id carried by two node-forming blocks is a build error: it must name
    one claim.
    """
    carriers: dict[str, list[str]] = {}
    for block_id, block in blocks.items():
        if atoms_per_block.get(block_id, 0) < 1:
            continue
        human = find_human_id(block)
        if human is not None:
            carriers.setdefault(human, []).append(block_id)

    duplicates = {human: ids for human, ids in carriers.items() if len(ids) > 1}
    if duplicates:
        lines = [
            f"{human} is used by " + " and ".join(
                f"{blocks[b]['source']}:{blocks[b]['lines'][0]}" for b in sorted(ids)
            )
            for human, ids in sorted(duplicates.items())
        ]
        raise SddcError(
            "duplicate human id(s) — each must name one claim (F2 §4.8): " + "; ".join(lines),
            ExitCode.INPUT,
        )

    return {ids[0]: human for human, ids in carriers.items()}


def adopt_human_ids(
    blocks: Mapping[str, Mapping[str, Any]], atoms_per_block: Mapping[str, int]
) -> dict[str, str]:
    """Block id → adopted node id: a labelled block that forms exactly one node (AC-2.19)."""
    return {
        block_id: human
        for block_id, human in human_labels(blocks, atoms_per_block).items()
        if atoms_per_block.get(block_id) == 1
    }
