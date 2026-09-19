"""Model backends: one interface, two real implementations and a fake."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from ..profile import AtomizerSettings
from .base import Answer, Backend, CallBudget, Question
from .claude_code import ClaudeCodeBackend
from .fake import FakeBackend

__all__ = [
    "Answer", "Backend", "CallBudget", "ClaudeCodeBackend", "FakeBackend",
    "Question", "get_backend",
]


def get_backend(
    settings: AtomizerSettings,
    root: Path | None = None,
    budget: CallBudget | None = None,
    **kwargs: Any,
) -> Backend:
    """The backend the profile asks for (rel01 D7)."""
    if settings.backend == "claude-code":
        return ClaudeCodeBackend(
            model=settings.model,
            pass_api_key=settings.pass_api_key,
            timeout_s=settings.timeout_s,
            thinking=settings.thinking,
            budget=budget,
            **kwargs,
        )
    if settings.backend == "anthropic-api":
        from .anthropic_api import AnthropicApiBackend

        return AnthropicApiBackend(model=settings.model, root=root, budget=budget)
    raise ValueError(f"unknown backend {settings.backend!r}")  # pragma: no cover - profile validates
