"""F5 §4.1, §4.3, §4.4 — which nodes are checked, which pairs survive, and how a pair is named.

The run's shape: for every node that needs checking, in `(source file, first line, node id)`
order, score it against every other node; drop what scores below `min_score`; keep the best
`max_pairs_per_node`; then the run's pairs are the distinct ones among what survived.

⚑ **F5 D10 — the counts count proposals, not distinct pairs** (T15). CT-5.3's identity
(`proposed = capped + dropped_below_min_score + dropped_by_cap`, AC-5.16) only holds if every
number counts the same thing, and a pair both of whose ends were checked is proposed twice.
So `candidates_proposed`, `pairs_capped` and both `dropped_` counts are per proposal, while
`pairs` — what F6 judges — holds each `pair_key` once (AC-5.13).
"""
from __future__ import annotations

import hashlib
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any

from .score import score_of
from .sources import evidence_for

CHECK_STATUSES = ("unchecked", "stale", "conflict")


@dataclass
class Retrieval:
    """One run's retrieval: the pairs to judge, and the counts CT-5.3 records."""

    checked: list[str] = field(default_factory=list)
    pairs: list[dict[str, Any]] = field(default_factory=list)
    counts: dict[str, int] = field(default_factory=dict)


def needs_checking(node: Mapping[str, Any]) -> bool:
    """F5 §4.1, AC-5.14. A `validated` node is skipped; an `ambiguous` one is checked until
    it has been judged once, because nothing has yet looked at it. "Judged" means by the check
    phase: `judgments` lists the answers that formed the node, and is never empty (I-86)."""
    if node["status"] in CHECK_STATUSES:
        return True
    return node["status"] == "ambiguous" and node.get("last_checked_run") is None


def checking_order(nodes: Sequence[Mapping[str, Any]]) -> list[Mapping[str, Any]]:
    """`(source file, first line, node id)` — so a run is reproducible (F5 §4.1)."""
    return sorted(nodes, key=lambda n: (n["source"]["file"], n["source"]["lines"][0], n["id"]))


def pair_key(a: Mapping[str, Any], b: Mapping[str, Any]) -> str:
    """F5 §4.4 — unordered, and sensitive to both texts: the key changes exactly when the
    pair must be judged again (F5 D4). F6 uses it for the judgment lock."""
    first, second = sorted((a, b), key=lambda n: n["id"])
    parts = [first["id"], second["id"], _text_hash(first), _text_hash(second)]
    return "sha256:" + hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()


def _text_hash(node: Mapping[str, Any]) -> str:
    return hashlib.sha256(node["text"].encode("utf-8")).hexdigest()


def propose(nodes: Mapping[str, Mapping[str, Any]], *, terms: Mapping[str, Mapping[str, Any]],
            settings: Any, judged: Sequence[str] = ()) -> Retrieval:
    """Every pair worth judging in this run. `judged` holds `pair_key`s already settled in the
    judgment lock: they are replayed, not proposed again (F5 §4.1, §4.4)."""
    result = Retrieval()
    counts = dict.fromkeys(
        ("nodes_checked", "candidates_proposed", "pairs_capped",
         "dropped_below_min_score", "dropped_by_cap", "replayed"), 0)
    settled = set(judged)
    seen: dict[str, dict[str, Any]] = {}

    for node in checking_order([n for n in nodes.values() if needs_checking(n)]):
        result.checked.append(node["id"])
        counts["nodes_checked"] += 1
        scored = []
        for other in sorted(nodes.values(), key=lambda n: n["id"]):
            if other["id"] == node["id"]:                       # never its own candidate (AC-5.13)
                continue
            evidence = evidence_for(node, other, terms=terms, settings=settings)
            if not evidence:
                continue
            counts["candidates_proposed"] += 1
            key = pair_key(node, other)
            if key in settled:
                counts["replayed"] += 1
                continue
            score = score_of(evidence)
            if score < settings.min_score:
                counts["dropped_below_min_score"] += 1
                continue
            scored.append({"pair_key": key, "score": score, "evidence": evidence, "other": other})

        # Ranked by score, then by node id (F5 §4.3); the cap is per checked node.
        scored.sort(key=lambda c: (-c["score"], c["other"]["id"]))
        kept, dropped = scored[:settings.max_pairs_per_node], scored[settings.max_pairs_per_node:]
        counts["pairs_capped"] += len(kept)
        counts["dropped_by_cap"] += len(dropped)
        for candidate in kept:
            first, second = sorted((node["id"], candidate["other"]["id"]))
            seen.setdefault(candidate["pair_key"], {
                "pair_key": candidate["pair_key"], "a": first, "b": second,
                "score": candidate["score"], "evidence": candidate["evidence"]})

    ranked = sorted(seen.values(), key=lambda c: (-c["score"], c["a"], c["b"]))
    result.pairs = [{**candidate, "rank": rank} for rank, candidate in enumerate(ranked, start=1)]
    result.counts = counts
    return result
