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
        ("S6", *_same_measured_property(a, b)),
        ("S7", *_same_block(a, b)),
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
    def subjects(node):
        return {t["term"] for t in node["terms"]
                if (registry.get(t["term"], {}) or {}).get("kind") in SUBJECT_KINDS}

    shared = sorted(subjects(a) & subjects(b))
    return ({"terms": shared}, len(shared)) if shared else (None, 0)


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


def _same_measured_property(a, b):
    """A shared term **and** a quantity of the same dimension on both (F5 D1: the
    "30 days versus 1 hour" shape, the most common real contradiction)."""
    if not {t["term"] for t in a["terms"]} & {t["term"] for t in b["terms"]}:
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
