"""F5 §4.3 — the score of a candidate: fixed additive weights, capped per source (F5 D2).

    score = 3.0·S1 + 2.0·S2(per shared term, max 4.0) + 2.0·S3 + 1.0·S4
          + 0.5·S5(per shared keyword, max 2.0) + 2.5·S6 + 1.5·S7

The weights are starting values to tune with measurement (F5 D6), not findings. Every
candidate carries the evidence its points came from, so a score can always be explained
(CT-5.1, AC-5.9).
"""
from __future__ import annotations

from collections.abc import Sequence
from typing import Any

WEIGHTS: dict[str, float] = {
    "S1": 3.0, "S2": 2.0, "S3": 2.0, "S4": 1.0, "S5": 0.5, "S6": 2.5, "S7": 1.5,
}
CAPS: dict[str, float] = {"S2": 4.0, "S5": 2.0}


def points_for(source: str, count: int = 1) -> float:
    """`count` is how many times the source fired: shared terms (S2) or keywords (S5)."""
    total = WEIGHTS[source] * count
    return round(min(total, CAPS.get(source, total)), 4)


def score_of(evidence: Sequence[dict[str, Any]]) -> float:
    return round(sum(entry["points"] for entry in evidence), 4)
