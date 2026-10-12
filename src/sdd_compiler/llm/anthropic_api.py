"""The optional Anthropic API backend (rel01 D7).

This is the **only** module that may read `.env`. Keeping the key here is what
stops it reaching a headless `claude` child, where it would silently change who
is billed (brainstorm hazard 3).
"""
from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Any

from ..errors import ExitCode, SddcError
from .base import Answer, Question

KEY_NAME = "ANTHROPIC_API_KEY"


def read_api_key(root: Path | None = None) -> str:
    """The key from the environment, or from `<root>/.env`. Never printed."""
    key = os.environ.get(KEY_NAME)
    if key:
        return key
    env_file = Path(root or Path.cwd()) / ".env"
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            name, _, value = line.partition("=")
            if name.strip() == KEY_NAME:
                return value.strip().strip('"').strip("'")
    raise SddcError(
        f"{KEY_NAME} is not set and no .env holds it; the anthropic-api backend needs a key "
        f"(or use atomizer.backend: claude-code)",
        ExitCode.BACKEND,
    )


class AnthropicApiBackend:
    name = "anthropic-api"

    def __init__(self, model: str, root: Path | None = None, budget: Any | None = None) -> None:
        self.model = model
        self.root = root
        self.budget = budget

    def ask(self, question: Question) -> Answer:
        if self.budget is not None:
            self.budget.spend()
        key = read_api_key(self.root)
        try:
            import anthropic  # noqa: F401  (imported lazily: the SDK is optional)
        except ImportError as exc:  # pragma: no cover - environment dependent
            raise SddcError(
                "the anthropic SDK is not installed (`pip install anthropic`), "
                "or use atomizer.backend: claude-code",
                ExitCode.BACKEND,
            ) from exc
        raise SddcError(  # pragma: no cover - M2 T6 ships the interface, not this path
            "the anthropic-api backend is not implemented yet; rel01 default is claude-code",
            ExitCode.BACKEND,
        )
        _ = (key, time)  # keep the imports honest until the path is built
