"""F6 §4.3 — what a verdict becomes: links, a conflict record, and ambiguity on the nodes.

Nothing here asks anything. Given a checked verdict (`judge.py`) and the two nodes, it returns
the records the graph should hold, so the caller (T17) can write them in one transaction.

⚑ **F6 D2** — a `subsumes` verdict is a *conflict* only when the two claims differ in modality
or in a quantity: "every request must be logged" subsuming "login requests must be logged" is
design, not a defect. With `subsumption_conflict_only_when_differing: false` (CT-6.3) every
subsumption opens a record.
"""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any

from .judge import Verdict

#: relation -> (link type, conflict kind or None)
EFFECTS: dict[str, tuple[str | None, str | None]] = {
    "none": (None, None),
    "refines": ("refines", None),
    "depends_on": ("depends_on", None),
    "duplicates": ("duplicates", "duplication"),
    "subsumes": ("subsumes", "subsumption"),
    "contradicts": ("conflicts_with", "contradiction"),
}


@dataclass
class Outcome:
    links: list[dict[str, Any]] = field(default_factory=list)
    conflict: dict[str, Any] | None = None
    ambiguity: dict[str, list[dict[str, Any]]] = field(default_factory=dict)
    suppressed: str | None = None          # a verdict the graph itself refutes (F6 D16)


def outcome_for(verdict: Verdict, a: Mapping[str, Any], b: Mapping[str, Any], *,
                settings: Any, run_id: str, conflict_id: str, judgment: str,
                contracts: frozenset[str] = frozenset()) -> Outcome:
    link_type, conflict_kind = EFFECTS[verdict.relation]
    outcome = Outcome()
    if conflict_kind in ("duplication", "subsumption") and _verifies_each_other(a, b):
        # ⚑ F6 D16 (R17, I-77): a criterion restating the requirement it verifies is the
        # specification's design. F6 D15 says so in the prompt and the judge did it anyway, so the
        # graph settles it: `verifies` was resolved from the criterion's own citation (F2 D13).
        # A *contradiction* between a test and its rule is left alone — that one is a real defect.
        outcome.suppressed = "verifies_its_own_requirement"
        return outcome
    if conflict_kind in ("duplication", "subsumption"):
        # ⚑ F6 D19 (I-81): the same lever where no citation exists — the document's own form
        # says these two were written to overlap. Contradictions are never suppressed here.
        if _criterion_in_its_own_spec(a, b):
            outcome.suppressed = "criterion_restates_its_own_spec"
            return outcome
        if a["source"]["block_id"] == b["source"]["block_id"]:
            outcome.suppressed = "same_block"
            return outcome
        # ⚑ F6 D24 (I-94): a spec states a contract, then writes rules about its fields.
        if ((a["id"] in contracts) != (b["id"] in contracts)
                and a["source"]["file"] == b["source"]["file"]):
            outcome.suppressed = "contract_restated_in_its_own_spec"
            return outcome
    if link_type is None:
        return outcome                                   # `none`: only the judgment is kept

    source, target = (a, b) if verdict.direction != "b_to_a" else (b, a)
    outcome.links.append({
        "from": source["id"], "type": link_type, "to": target["id"],
        "provenance": "judgment", "judgment": judgment, "rationale": verdict.rationale,
        "quotes": [verdict.quotes["a"], verdict.quotes["b"]],
    })

    if conflict_kind == "subsumption" and settings.subsumption_conflict_only_when_differing \
            and not _differ(a, b):
        conflict_kind = None
    if conflict_kind is not None:
        members = sorted((a["id"], b["id"]))
        outcome.conflict = {
            "id": conflict_id, "kind": conflict_kind, "members": members,
            "rationale": verdict.rationale,
            "quotes": {a["id"]: verdict.quotes["a"], b["id"]: verdict.quotes["b"]},
            "state": "open", "resolved_reason": None, "detected_run": run_id,
            "resolved_run": None, "judgment": judgment,
        }
    if verdict.confidence == "low":
        entry = {"kind": "low_confidence_verdict", "quote": None,
                 "detail": f"the judge was unsure: {verdict.rationale}"}
        outcome.ambiguity = {a["id"]: [dict(entry)], b["id"]: [dict(entry)]}
    return outcome


def _verifies_each_other(a: Mapping[str, Any], b: Mapping[str, Any]) -> bool:
    return b["id"] in (a.get("verifies") or []) or a["id"] in (b.get("verifies") or [])


def _criterion_in_its_own_spec(a: Mapping[str, Any], b: Mapping[str, Any]) -> bool:
    """Exactly one of the two is a criterion (two criteria alike are a copied test), same file."""
    return (a.get("layer") == "V") != (b.get("layer") == "V") \
        and a["source"]["file"] == b["source"]["file"]


def _differ(a: Mapping[str, Any], b: Mapping[str, Any]) -> bool:
    """F6 D2 — different modality, or different amounts of the same dimension."""
    if a["canonical"]["modality"] != b["canonical"]["modality"]:
        return True
    return _amounts(a) != _amounts(b)


def _amounts(node: Mapping[str, Any]) -> set[tuple[Any, str]]:
    found = set()
    for quantity in node["canonical"].get("quantities") or []:
        normalized = quantity.get("normalized")
        if normalized:
            found.add((normalized["value"], normalized["unit"]))
    return found
