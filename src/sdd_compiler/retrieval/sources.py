"""F5 §4.2 — the candidate sources S1 … S10 (AC-5.1 … AC-5.8, AC-5.17, AC-5.19 … AC-5.21).

Each source answers one question about a pair of nodes and, when it fires, records what it
matched. Nothing here reads the model, and nothing reads a whole file: everything is on the
two node records plus the term registry.

⚑ Why a family of `(global)` or `null` never fires S1: neither is a family. `(global)` holds
constraints with no stated scope (F2 §4.4 rule 4), and `null` means no family was resolved —
pairing either wholesale would propose most of the graph.
"""
from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from typing import Any

from ..model.layers import LAYERS
from ..model.scope import covers
from .score import points_for

SUBJECT_KINDS = ("entity", "data", "event")
ORDERED_LAYERS = [layer for layer in LAYERS if layer.startswith("L")]


def evidence_for(a: Mapping[str, Any], b: Mapping[str, Any], *,
                 terms: Mapping[str, Mapping[str, Any]],
                 settings: Any, keyword_counts: Mapping[str, Any] | None = None) -> list[dict[str, Any]]:
    """Every source that fires for this pair, in source order (S1 … S10). `keyword_counts` is the
    graph's keyword counts (`keyword_counts()`); without them S9 cannot tell a rare word and is off."""
    evidence = []
    for source, detail, count in (
        ("S1", *_same_family(a, b, terms)),
        ("S2", *_shared_subject_terms(a, b, terms)),
        ("S3", *_constraint_scope(a, b)),
        ("S4", *_adjacent_layer(a, b)),
        ("S5", *_shared_keywords(a, b, settings.min_shared_keywords)),
        ("S6", *_same_measured_property(a, b, settings)),
        ("S7", *_same_block(a, b)),
        ("S8", *_sibling_terms(a, b, terms)),
        ("S9", *_rare_keywords(a, b, keyword_counts, getattr(settings, "rare_keyword_share", None))),
        ("S10", *_topic_named(a, b, terms)),
    ):
        if detail is not None:
            evidence.append({"source": source, "detail": detail, "points": points_for(source, count)})
    return evidence


def _same_family(a, b, registry):
    """Same family, or one family a kind of the other (F5 D15: `broader`, any depth, as S2 does)."""
    family, other = a["family"], b["family"]
    if not family or not other or "(global)" in (family, other):
        return None, 0
    if family == other:
        return {"family": family}, 1
    if other in _ancestors(family, registry) or family in _ancestors(other, registry):
        return {"family": family, "other_family": other}, 1
    return None, 0


def _topic_named(a, b, registry):
    """S10 (F5 D17): one node's family is among the other's terms, in any role, or a name of two
    or more words of that family's term is in the other's text. Not when S1 fires."""
    if _same_family(a, b, registry)[0] is not None:
        return None, 0
    for topic_node, other in ((a, b), (b, a)):
        family = topic_node["family"]
        if not family or family == "(global)":
            continue
        if family in {t["term"] for t in other["terms"]}:
            return {"family": family, "found": "term"}, 1
        entry = registry.get(family) or {}
        for name in [entry.get("canonical"), *(entry.get("aliases") or [])]:
            if name and len(name.split()) >= 2 and _names(name, other["text"]):
                return {"family": family, "found": "text"}, 1
    return None, 0


def _names(name: str, text: str) -> bool:
    """`name` as whole words in `text`, ignoring case; space, `_` and `-` are one separator, and a
    final `s` is allowed ("prompts" names "prompt")."""
    words = [re.escape(w) for w in re.split(r"[\s_-]+", name.strip()) if w]
    pattern = r"(?<![\w-])" + r"[\s_-]+".join(words) + r"s?(?![\w-])"
    return re.search(pattern, text, re.IGNORECASE) is not None


def keyword_counts(nodes) -> dict[str, Any]:
    """F5 D16: in how many nodes each keyword occurs, counted once per run over the whole graph."""
    counts: dict[str, int] = {}
    total = 0
    for node in nodes:
        total += 1
        for keyword in set(node["keywords"]):
            counts[keyword] = counts.get(keyword, 0) + 1
    return {"nodes": total, "counts": counts}


def _rare_keywords(a, b, keyword_counts, share):
    """S9 (F5 D16): shared keywords found in at most `share` of the graph's nodes. Off in a graph so
    small that `share` of it is under 2 nodes: there, every shared word would look rare."""
    if not keyword_counts or share is None:
        return None, 0
    limit = share * keyword_counts["nodes"]
    if limit < 2:
        return None, 0
    rare = sorted(k for k in set(a["keywords"]) & set(b["keywords"])
                  if keyword_counts["counts"].get(k, 0) <= limit)
    return ({"keywords": rare}, len(rare)) if rare else (None, 0)


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
