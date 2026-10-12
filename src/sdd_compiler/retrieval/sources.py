"""F5 §4.2 — the seven candidate sources (AC-5.1 … AC-5.8).

Each source answers one question about a pair of nodes and, when it fires, records what it
matched. Nothing here reads the model, and nothing reads a whole file: everything is on the
two node records plus the term registry.

⚑ Why a family of `(global)` or `null` never fires S1: neither is a family. `(global)` holds
constraints with no stated scope (F2 §4.4 rule 4), and `null` means no family was resolved —
pairing either wholesale would propose most of the graph.
"""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from ..model.layers import LAYERS
from ..model.scope import covers
from .score import points_for

SUBJECT_KINDS = ("entity", "data", "event")
ORDERED_LAYERS = [layer for layer in LAYERS if layer.startswith("L")]


def evidence_for(a: Mapping[str, Any], b: Mapping[str, Any], *,
                 terms: Mapping[str, Mapping[str, Any]],
                 settings: Any) -> list[dict[str, Any]]:
    """Every source that fires for this pair, in source order (S1 … S7)."""
    evidence = []
    for source, detail, count in (
        ("S1", *_same_family(a, b)),
        ("S2", *_shared_subject_terms(a, b, terms)),
        ("S3", *_constraint_scope(a, b)),
        ("S4", *_adjacent_layer(a, b)),
        ("S5", *_shared_keywords(a, b, settings.min_shared_keywords)),
        ("S6", *_same_measured_property(a, b, settings)),
        ("S7", *_same_block(a, b)),
        ("S8", *_sibling_terms(a, b, terms)),
    ):
        if detail is not None:
            evidence.append({"source": source, "detail": detail, "points": points_for(source, count)})
    return evidence


def _same_family(a, b):
    family = a["family"]
    if family and family == b["family"] and family != "(global)":
        return {"family": family}, 1
    return None, 0


def _shared_subject_terms(a, b, registry):
    """A shared term, or one that is **a kind of** the other (F5 D11, R15).

    `broader` (F2 D16) is already recorded by Q-TERM, and without it the two sides of a real
    conflict — "download link" and "share link" — look like strangers (M4 gate, I-73).
    """
    def subjects(node):
        return {t["term"] for t in node["terms"]
                if (registry.get(t["term"], {}) or {}).get("kind") in SUBJECT_KINDS}

    mine, theirs = subjects(a), subjects(b)
    matched = sorted(mine & theirs)
    for term in sorted(mine ^ theirs):
        for ancestor in _ancestors(term, registry):
            if ancestor in (theirs if term in mine else mine):
                matched.append(f"{term} → {ancestor}")
                break
    return ({"terms": sorted(matched)}, len(matched)) if matched else (None, 0)


def _ancestors(term: str, registry: Mapping[str, Mapping[str, Any]]) -> list[str]:
    """The `broader` chain above a term, shallowest first; cycles stop it."""
    found, seen = [], {term}
    current = (registry.get(term) or {}).get("broader")
    while current and current not in seen:
        found.append(current)
        seen.add(current)
        current = (registry.get(current) or {}).get("broader")
    return found


def _sibling_terms(a, b, registry):
    """Two terms that are kinds of the same thing (F5 D12, I-76).

    Q-TERM files "export archive" and "workspace export" as narrower than "export" — and then
    nothing paired the claims about them, because neither term is the other's ancestor. A shared
    parent is a weaker signal than a shared term, and it is scored that way.
    """
    def subjects(node):
        return {t["term"] for t in node["terms"]
                if (registry.get(t["term"], {}) or {}).get("kind") in SUBJECT_KINDS}

    mine, theirs = subjects(a), subjects(b)
    if mine & theirs:
        return None, 0                      # an exact match is S2's, not ours
    shared, matched = set(), set()
    for term in mine:
        line = set(_ancestors(term, registry))
        if term in {t for other in theirs for t in _ancestors(other, registry)}:
            return None, 0                  # one is above the other: S2's case (R15)
        for other in theirs:
            if other in line:
                return None, 0
            common = line & set(_ancestors(other, registry))
            if common:
                shared |= common
                matched |= {term, other}
    if not shared:
        return None, 0
    return {"shared": sorted(shared), "terms": sorted(matched)}, 1


def _constraint_scope(a, b):
    for constraint, other in ((a, b), (b, a)):
        if constraint["layer"] == "C" and covers(constraint, other):
            return {"selector": constraint["scope_selector"]}, 1
    return None, 0


def _adjacent_layer(a, b):
    if not a["family"] or a["family"] != b["family"]:
        return None, 0
    if a["layer"] not in ORDERED_LAYERS or b["layer"] not in ORDERED_LAYERS:
        return None, 0
    if abs(ORDERED_LAYERS.index(a["layer"]) - ORDERED_LAYERS.index(b["layer"])) > 1:
        return None, 0
    return {"layers": sorted({a["layer"], b["layer"]})}, 1


def _shared_keywords(a, b, minimum):
    shared = sorted(set(a["keywords"]) & set(b["keywords"]))
    return ({"keywords": shared}, len(shared)) if len(shared) >= minimum else (None, 0)


def _same_measured_property(a, b, settings):
    """A quantity of the same dimension on both, in claims that are **about the same words**
    (F5 D1: the "30 days versus 1 hour" shape, the most common real contradiction).

    ⚑ F5 D11 (R15, M4 gate I-73): "about the same words" means a shared term **or** a shared
    keyword. Requiring a shared *term* lost "at most 5 GB" against "at most 5 GiB", because the
    atomizer had named one an export archive and the other a workspace export. Requiring nothing
    would pair every number in the corpus with every other.
    """
    shared_terms = {t["term"] for t in a["terms"]} & {t["term"] for t in b["terms"]}
    if not shared_terms and not (set(a["keywords"]) & set(b["keywords"])):
        return None, 0
    for dimension, first in _dimensions(a):
        for other_dimension, second in _dimensions(b):
            if dimension == other_dimension:
                return {"dimension": dimension, "values": [_amount(first), _amount(second)]}, 1
    return None, 0


def _dimensions(node) -> Sequence[tuple[str, Mapping[str, Any]]]:
    found = []
    for quantity in node["canonical"].get("quantities") or []:
        normalized = quantity.get("normalized")
        if normalized:
            found.append((_dimension_of(normalized["unit"]), quantity))
    return found


_DIMENSIONS = {"s": "time", "B": "size", "%": "percent", "": "count"}


def _dimension_of(unit: str) -> str:
    return _DIMENSIONS.get(unit, unit)


def _amount(quantity) -> str:
    return f"{quantity['value']} {quantity['unit']}".strip()


def _same_block(a, b):
    block = a["source"]["block_id"]
    return ({"block_id": block}, 1) if block == b["source"]["block_id"] else (None, 0)
