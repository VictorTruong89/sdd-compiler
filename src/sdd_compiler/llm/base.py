"""The model interface: one small, closed, schema-bound question at a time.

Everything the compiler asks a model goes through this interface (vision O3), so
there is exactly one place that knows how a question is sent, how an answer is
checked for shape, and what a call cost. Guards on the *content* of an answer
live in the atomizer (F3 §4.4); this layer only guarantees an answer arrived and
matched its schema.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol

from ..errors import ExitCode, SddcError


@dataclass(frozen=True)
class Question:
    """One closed question. `schema` is the JSON Schema the answer must satisfy."""

    kind: str
    schema_version: str
    schema: dict[str, Any]
    prompt: str
    payload: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Answer:
    """One answer, with what it cost. The fields G4 needs are all here."""

    data: dict[str, Any]
    backend: str
    model: str
    usage: dict[str, int] = field(default_factory=dict)
    cost_usd: float | None = None
    duration_ms: int = 0
    cli_version: str | None = None


class Backend(Protocol):
    """What every backend must provide."""

    name: str

    def ask(self, question: Question) -> Answer: ...


@dataclass
class CallBudget:
    """A per-run cap on model calls, shared by every phase (F3 §4.1, F6 D5).

    A run that would exceed it stops with exit 5 rather than quietly doing less:
    an incomplete check that looks complete is the failure this project keeps
    designing against.
    """

    max_calls: int
    used: int = 0

    @property
    def remaining(self) -> int:
        return max(0, self.max_calls - self.used)

    def spend(self) -> None:
        if self.used >= self.max_calls:
            raise SddcError(
                f"model call cap reached ({self.max_calls} calls this run); "
                f"what was completed is written, the rest stays pending",
                ExitCode.CALL_CAP,
            )
        self.used += 1
