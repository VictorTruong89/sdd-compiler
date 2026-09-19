"""F2 §4.6, §4.7 — status is derived from facts, never set (D1, D9, D15, D17).

Precedence: conflict > ambiguous > stale > unchecked > validated. The facts stay
in their own fields and the status is recomputed from them, so the two cannot
drift apart; the record schema rejects a stored status that disagrees (AC-2.14).
"""
from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any


def derive_status(node: Mapping[str, Any]) -> str:
    if node.get("conflict_ids"):
        return "conflict"
    if node.get("ambiguity"):
        return "ambiguous"
    if node.get("stale_reasons"):
        return "stale"
    if node.get("last_checked_run") is None:
        return "unchecked"
    return "validated"


def refresh_conflict_fields(
    node: Mapping[str, Any], records: Iterable[Mapping[str, Any]]
) -> dict[str, Any]:
    """Recompute `conflict_ids`, `related_conflict_nodes` and `status` from the records."""
    identifier = node["id"]
    mine = sorted(
        (record for record in records
         if record["state"] == "open" and identifier in record["members"]),
        key=lambda record: record["id"],
    )
    related = sorted({m for record in mine for m in record["members"] if m != identifier})
    refreshed = {**node, "conflict_ids": [record["id"] for record in mine],
                 "related_conflict_nodes": related}
    refreshed["status"] = derive_status(refreshed)
    return refreshed
