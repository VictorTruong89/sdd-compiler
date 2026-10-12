"""F2 §4.3 — placement into exactly one layer, from seven recorded answers (P-8).

The model answers seven yes/no questions, each `yes` with a quote; code decides.
The quote offsets are the ones G2 computed in the source, never the model's.

1. a verification goes to `V`, whatever it answered;
2. otherwise the **first yes** in Q1 → Q7 order decides;
3. a later yes whose quote overlaps an earlier yes quote is the same words seen
   from another angle: recorded, and ignored;
4. a later yes overlapping **no** earlier yes is a second claim on another layer —
   atom test T3 failed, so the atom must be split (`split_required`);
5. seven noes: layer null, ambiguity `unplaceable`.
"""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any

from .layers import LAYER_OF_QUESTION, QUESTIONS


@dataclass
class Placement:
    layer: str | None
    ambiguity: list[dict[str, Any]] = field(default_factory=list)
    split_required: dict[str, Any] | None = None
    overlapping: list[str] = field(default_factory=list)   # later yeses that were ignored


def place(kind: str, answers: Mapping[str, Mapping[str, Any]]) -> Placement:
    if kind == "verification":
        return Placement(layer="V")

    yeses = [question for question in QUESTIONS if answers[question]["answer"] == "yes"]
    if not yeses:
        return Placement(layer=None, ambiguity=[{
            "kind": "unplaceable", "quote": None,
            "detail": "all seven layer questions were answered no",
        }])

    first = yeses[0]
    placement = Placement(layer=LAYER_OF_QUESTION[first])
    earlier = [first]
    for question in yeses[1:]:
        span = tuple(answers[question]["span"])
        if any(_overlaps(span, tuple(answers[prior]["span"])) for prior in earlier):
            placement.overlapping.append(question)
            earlier.append(question)
            continue
        return Placement(layer=None, split_required={
            "first": _cite(first, answers[first]),
            "second": _cite(question, answers[question]),
        })
    return placement


def _cite(question: str, answer: Mapping[str, Any]) -> dict[str, Any]:
    return {"question": question, "quote": answer["quote"], "span": tuple(answer["span"])}


def _overlaps(a: tuple[int, int], b: tuple[int, int]) -> bool:
    """Sharing at least one character offset; ends are exclusive."""
    return a[0] < b[1] and b[0] < a[1]
