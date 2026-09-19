"""F2 §4.4 — exactly one family per node: its primary term, by a fixed rule (P-9).

The rules are tried in the order the spec gives, and the first that applies
wins (⚑ F2 D9: literally, so a constraint whose subject is an entity belongs to
that entity's family before the constraint rule is reached):

1. **subject** — the subject is an `entity`, `data` or `event` term;
2. **response** — the subject is an actor, a component, an external system or
   "the system": the first `entity`/`data`/`event` term in the response;
3. **verification** — a `V` node takes the family of what it verifies; several
   families → the first, flagged `family_disputed`. ⚑ F2 D18: for a `V` node that
   resolved `verifies`, this rule comes **first** — a criterion's Given clause
   ("Given two nodes…") names its fixture, not what it tests;
4. **constraint** — a `C` node scoped to exactly one family belongs to it,
   otherwise to `(global)`;
5. **mention** — the first `entity`/`data`/`event` term the node uses in any
   role (F2 D17, rel01 D32 R4): a last resort, better than no family;
6. **component** — ⚑ F2 D19: a `component` subject, when nothing above applies
   ("exhaustive mode" had no family at all);
7. **fallback** — family null, ambiguity `unresolved_term`.

A pin overrides them all. Actors and categories never seed a family, and a
component only by rule 6: otherwise "user" or "the service" would absorb half the graph.
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

    if layer == "V" and verified_families:                              # F2 D18
        return _verification(verified_families)

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

    if layer == "C":
        distinct = sorted(set(scope_families))
        return Family(distinct[0] if len(distinct) == 1 else GLOBAL, "constraint")

    mentioned = next((t for t in terms if t["kind"] in SEEDS), None)
    if mentioned is not None:
        return Family(mentioned["term"], "mention")

    if subject_term is not None and subject_term["kind"] == "component":   # F2 D19
        return Family(subject_term["term"], "component")

    return Family(None, "fallback", ambiguity=[{
        "kind": "unresolved_term", "quote": None,
        "detail": "no entity, data or event term to name the node's family",
    }])


def _verification(verified_families: Sequence[str]) -> Family:
    disputed = len(set(verified_families)) > 1
    return Family(verified_families[0], "verification", flags=["family_disputed"] if disputed else [])


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
