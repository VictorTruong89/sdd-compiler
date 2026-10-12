"""T9 — F2 §4.3 placement into exactly one layer (AC-2.1 … AC-2.5).

Tier: unit, with one exhaustive property test over all 128 answer patterns.
"""
from __future__ import annotations

import itertools

import pytest

from sdd_compiler.model.layers import LAYER_OF_QUESTION, QUESTIONS
from sdd_compiler.model.placement import place

TEXT_SPAN = (0, 40)


def answers(**yes):
    """`yes` maps a question to its span; every other question is `no`."""
    result = {}
    for question in QUESTIONS:
        span = yes.get(question)
        result[question] = (
            {"answer": "yes", "quote": f"quote for {question}", "span": span}
            if span else {"answer": "no", "quote": None, "span": None}
        )
    return result


def test_ac_2_1_the_first_yes_wins_and_an_overlapping_later_yes_is_recorded():
    placed = place("requirement", answers(Q3=(10, 30), Q6=(20, 40)))
    assert placed.layer == "L1"
    assert placed.split_required is None
    assert placed.overlapping == ["Q6"]


def test_ac_2_2_non_overlapping_yeses_on_two_layers_require_a_split():
    placed = place("requirement", answers(Q4=(0, 10), Q5=(20, 30)))
    assert placed.layer is None
    assert placed.split_required == {
        "first": {"question": "Q4", "quote": "quote for Q4", "span": (0, 10)},
        "second": {"question": "Q5", "quote": "quote for Q5", "span": (20, 30)},
    }


def test_ac_2_3_seven_noes_are_unplaceable():
    placed = place("requirement", answers())
    assert placed.layer is None
    assert placed.split_required is None
    assert [a["kind"] for a in placed.ambiguity] == ["unplaceable"]


def test_ac_2_4_a_verification_goes_to_v_whatever_it_answered():
    placed = place("verification", answers(Q4=(0, 10), Q5=(20, 30)))
    assert placed.layer == "V"
    assert placed.split_required is None


def test_touching_spans_do_not_overlap():
    """Overlap means sharing at least one character offset; end offsets are exclusive."""
    placed = place("requirement", answers(Q3=(0, 10), Q6=(10, 20)))
    assert placed.split_required is not None


@pytest.mark.parametrize("pattern", list(itertools.product([False, True], repeat=7)))
def test_ac_2_5_with_overlapping_quotes_the_layer_is_always_the_first_yes(pattern):
    chosen = {q: TEXT_SPAN for q, on in zip(QUESTIONS, pattern) if on}
    placed = place("requirement", answers(**chosen))
    if not chosen:
        assert placed.layer is None
        return
    first = next(q for q in QUESTIONS if q in chosen)
    assert placed.layer == LAYER_OF_QUESTION[first]
    assert placed.split_required is None
