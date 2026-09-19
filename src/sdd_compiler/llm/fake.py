"""A scripted backend, so no test ever calls a live model (F3 D2).

Tests hand it the answers a real model would have given. It records every
question, which is how the guard tests check that a failed answer really was
re-asked exactly once.
"""
from __future__ import annotations

from typing import Any

from .base import Answer, Question


class FakeBackend:
    name = "fake"

    def __init__(self, answers: list[dict[str, Any]], budget: Any | None = None) -> None:
        self._answers = list(answers)
        self.budget = budget
        self.asked: list[Question] = []

    def ask(self, question: Question) -> Answer:
        if self.budget is not None:
            self.budget.spend()
        self.asked.append(question)
        assert self._answers, (
            f"FakeBackend ran out of answers: nothing scripted for {question.kind}. "
            f"A test that runs out here is asking more questions than it expected."
        )
        return Answer(
            data=self._answers.pop(0),
            backend=self.name,
            model="fake",
            usage={"input_tokens": 0, "output_tokens": 0,
                   "cache_read_tokens": 0, "cache_creation_tokens": 0},
            cost_usd=0.0,
            duration_ms=0,
            cli_version=None,
        )
