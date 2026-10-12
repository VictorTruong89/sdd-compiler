"""F7 §4.3–§4.4 — work units, the foundation, omitted headings, and build order.

A unit is `(source, heading_path[:2])`. Every block of a foundation-glob file joins one foundation
unit, first in the order. The specs, not the sections, are ordered: by the fewest `depends_on` links
pointing to a later spec, since those links are model verdicts — votes, not facts (⚑ D3, I-96).
"""
from __future__ import annotations

import fnmatch
import itertools
from collections import Counter
from collections.abc import Collection, Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any

from ..ingest.identity import heading_skipped, is_live

UnitKey = tuple[str, tuple[str, ...]]
FOUNDATION_KEY: UnitKey = ("", ("foundation",))


@dataclass
class Unit:
    key: UnitKey
    block_ids: list[str] = field(default_factory=list)
    first_line: int = 0

    @property
    def source(self) -> str:
        return self.key[0]

    @property
    def headings(self) -> tuple[str, ...]:
        return self.key[1]

    @property
    def sort_key(self) -> tuple[str, int]:
        return (self.source, self.first_line)


@dataclass
class Units:
    units: list[Unit]                         # work units in source order (not build order)
    foundation: Unit | None
    omitted: list[str]                        # live blocks under a skipped heading
    excluded: list[str]                       # live blocks excluded as real duplicates (D13)


def unit_key(block: Mapping[str, Any]) -> UnitKey:
    return (block["source"], tuple(block["heading_path"][:2]))


def foundation_index(source: str, globs: Sequence[str]) -> int | None:
    """Index of the first glob the source matches. `**/x.md` also matches a file at the root."""
    for index, pattern in enumerate(globs):
        if fnmatch.fnmatch(source, pattern) or fnmatch.fnmatch("/" + source, pattern):
            return index
    return None


def form_units(blocks: Iterable[Mapping[str, Any]], foundation_globs: Sequence[str],
               skip_headings: Sequence[str], excluded: Collection[str] = ()) -> Units:
    live = sorted((b for b in blocks if is_live(b)), key=lambda b: (b["source"], b["lines"][0]))
    omitted: list[str] = []
    dropped: list[str] = []
    foundation_blocks: list[tuple[int, Mapping[str, Any]]] = []
    by_key: dict[UnitKey, Unit] = {}
    for b in live:
        if heading_skipped(b["heading_path"], skip_headings):
            omitted.append(b["id"])
            continue
        if b["id"] in excluded:
            dropped.append(b["id"])
            continue
        glob = foundation_index(b["source"], foundation_globs)
        if glob is not None:
            foundation_blocks.append((glob, b))
            continue
        unit = by_key.setdefault(unit_key(b), Unit(unit_key(b), first_line=b["lines"][0]))
        unit.block_ids.append(b["id"])
    foundation = None
    if foundation_blocks:
        foundation_blocks.sort(key=lambda gb: (gb[0], gb[1]["source"], gb[1]["lines"][0]))
        foundation = Unit(FOUNDATION_KEY, [b["id"] for _, b in foundation_blocks],
                          foundation_blocks[0][1]["lines"][0])
    units = sorted(by_key.values(), key=lambda u: u.sort_key)
    return Units(units, foundation, omitted, dropped)


def compute_needs(links: Iterable[Mapping[str, Any]], home: Mapping[str, UnitKey],
                  foundation: UnitKey | None = None) -> Counter:
    """(X, Y) → how many `depends_on` links go from a node homed in X to one homed in Y, X ≠ Y,
    neither the foundation."""
    needs: Counter = Counter()
    for link in links:
        if link["type"] != "depends_on":
            continue
        x, y = home.get(link["from"]), home.get(link["to"])
        if x is None or y is None or x == y or foundation in (x, y):
            continue
        needs[(x, y)] += 1
    return needs


@dataclass
class Order:
    units: list[Unit]
    backward: list[tuple[UnitKey, UnitKey, int]]       # cross-file needs pointing to a later unit


EXACT_LIMIT = 8


def order_units(units: Sequence[Unit], needs: Mapping[tuple[UnitKey, UnitKey], int]) -> Order:
    """§4.4, D3 — order the files by the fewest backward needs; units keep source order inside a file."""
    files = sorted({u.source for u in units})
    weight: Counter = Counter()
    for (x, y), count in needs.items():
        if x[0] != y[0]:
            weight[(x[0], y[0])] += count               # file x[0] needs file y[0]
    chosen = _exact(files, weight) if len(files) <= EXACT_LIMIT else _greedy(files, weight)
    rank = {f: i for i, f in enumerate(chosen)}
    ordered = sorted(units, key=lambda u: (rank[u.source], u.first_line))
    position = {u.key: i for i, u in enumerate(ordered)}
    backward = sorted(((x, y, count) for (x, y), count in needs.items()
                       if x[0] != y[0] and position[y] > position[x]),
                      key=lambda t: (position[t[0]], position[t[1]]))
    return Order(ordered, backward)


def _cost(order: Sequence[str], weight: Mapping[tuple[str, str], int]) -> int:
    rank = {f: i for i, f in enumerate(order)}
    return sum(w for (f, g), w in weight.items() if rank[g] > rank[f])


def _exact(files: list[str], weight: Mapping[tuple[str, str], int]) -> list[str]:
    """Every order; the least backward weight, then the smallest paths (permutations of a sorted list
    come in that order, so the first minimum wins)."""
    best, best_cost = list(files), None
    for perm in itertools.permutations(files):
        cost = _cost(perm, weight)
        if best_cost is None or cost < best_cost:
            best, best_cost = list(perm), cost
    return best


def _greedy(files: list[str], weight: Mapping[tuple[str, str], int]) -> list[str]:
    remaining, order = set(files), []
    while remaining:
        def score(f: str) -> tuple[int, str]:
            needs = sum(weight.get((f, g), 0) for g in remaining if g != f)
            needed = sum(weight.get((g, f), 0) for g in remaining if g != f)
            return (needs - needed, f)
        pick = min(remaining, key=score)
        order.append(pick)
        remaining.discard(pick)
    improved = True
    while improved:
        improved = False
        for i in range(len(order) - 1):
            swapped = order[:i] + [order[i + 1], order[i]] + order[i + 2:]
            if _cost(swapped, weight) < _cost(order, weight):
                order, improved = swapped, True
    return order
