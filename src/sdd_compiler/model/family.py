"""F2 §4.4 — exactly one family per node: its primary term, by a fixed rule (P-9).

The rules are tried in the order the spec gives, and the first that applies
wins (⚑ F2 D9: literally, so a constraint whose subject is an entity belongs to
that entity's family before the constraint rule is reached):

1. **subject** — the subject is an `entity`, `data` or `event` term;
2. **response** — the subject is an actor, a component, an external system or
   "the system": the first `entity`/`data`/`event` term in the response;
3. **verification** — a `V` node takes the family of what it verifies; several
   families → the first, flagged `family_disputed`;
4. **constraint** — a `C` node scoped to exactly one family belongs to it,
   otherwise to `(global)`;
5. **fallback** — family null, ambiguity `unresolved_term`.

A pin overrides all five. Actors, components and categories never seed a family:
otherwise "user" or "the service" would absorb half the graph.
"""
from __future__ import annotations

import re
from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Any

GLOBAL = "(global)"
SEEDS = ("entity", "data", "event")
DELEGATES = ("actor", "component", "external_system")
_THE_SYSTEM = re.compile(r"^\s*(the\s+)?system\s*$", re.IGNORECASE)


@dataclass
class Family:
    family: str | None
    rule: str
    flags: list[str] = field(default_factory=list)
    ambiguity: list[dict[str, Any]] = field(default_factory=list)


def derive_family(
    layer: str | None,
    subject: str,
    terms: Sequence[dict[str, Any]],
    verified_families: Sequence[str] = (),
    scope_families: Sequence[str] = (),
    pin: str | None = None,
) -> Family:
    """`terms` are resolved tags in answer order: `{term, kind, role, quote}`."""
    if pin:
        return Family(pin, "pinned", flags=["pinned_family"])

    subject_term = next((t for t in terms if t["role"] == "subject"), None)
    if subject_term is not None and subject_term["kind"] in SEEDS:
        return Family(subject_term["term"], "subject")

    delegating = (subject_term is not None and subject_term["kind"] in DELEGATES) or bool(
        _THE_SYSTEM.match(subject or "")
    )
    if delegating:
        response = next(
            (t for t in terms if t["role"] == "response" and t["kind"] in SEEDS), None
        )
        if response is not None:
            return Family(response["term"], "response")

    if layer == "V" and verified_families:
        disputed = len(set(verified_families)) > 1
        return Family(verified_families[0], "verification",
                      flags=["family_disputed"] if disputed else [])

    if layer == "C":
        distinct = sorted(set(scope_families))
        return Family(distinct[0] if len(distinct) == 1 else GLOBAL, "constraint")

    return Family(None, "fallback", ambiguity=[{
        "kind": "unresolved_term", "quote": None,
        "detail": "no entity, data or event term to name the node's family",
    }])


def term_links(node_id: str, terms: Sequence[dict[str, Any]]) -> list[dict[str, Any]]:
    """AC-2.11 — every term a node mentions is linked; mentioning is never membership."""
    seen: list[str] = []
    for entry in terms:
        if entry["term"] not in seen:
            seen.append(entry["term"])
    return [
        {"from": node_id, "type": "uses_term", "to": term, "provenance": "code",
         "judgment": None, "rationale": None, "quotes": []}
        for term in seen
    ]
