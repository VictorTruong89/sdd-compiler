"""Headless Claude Code as a model backend (rel01 D7, default).

`claude -p --model <model> --output-format json --json-schema <schema>` returns
the answer in `structured_output`, with usage and an estimated cost beside it.

Two rules the child process must obey (brainstorm hazards 1 and 3):

- **`SDD_COMPILER_CHILD=1`** marks the child, so anything that might invoke the
  compiler again can refuse and break a loop before it starts;
- **`ANTHROPIC_API_KEY` is removed** unless the profile explicitly asks for it,
  so a key meant for the API backend cannot silently change who is billed for a
  headless call.

Extended thinking is switched off (`MAX_THINKING_TOKENS=0`) unless the profile
sets `atomizer.thinking: true` (F3 D10).

`--bare` is never passed: it skips the Claude Code login and would demand a key.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import time
from typing import Any

from ..errors import ExitCode, SddcError
from .base import Answer, AnswerRejected, Question

EXECUTABLE = "claude"
DEFAULT_TIMEOUT_S = 120


class ClaudeCodeBackend:
    name = "claude-code"

    def __init__(
        self,
        model: str,
        pass_api_key: bool = False,
        timeout_s: int = DEFAULT_TIMEOUT_S,
        budget: Any | None = None,
        thinking: bool = False,
    ) -> None:
        self.model = model
        self.pass_api_key = pass_api_key
        self.thinking = thinking
        self.timeout_s = timeout_s
        self.budget = budget
        self._cli_version: str | None = None

    # -- the call --------------------------------------------------------
    def ask(self, question: Question) -> Answer:
        if self.budget is not None:
            self.budget.spend()
        executable = shutil.which(EXECUTABLE)
        if executable is None:
            raise SddcError(
                f"`{EXECUTABLE}` is not on PATH — install Claude Code, or set "
                f"atomizer.backend to anthropic-api",
                ExitCode.BACKEND,
            )

        argv = self._argv(question)
        started = time.monotonic()
        try:
            process = subprocess.run(
                argv, capture_output=True, text=True, env=self._child_env(),
                timeout=self.timeout_s, stdin=subprocess.DEVNULL,
            )
        except subprocess.TimeoutExpired as exc:
            raise SddcError(
                f"{EXECUTABLE} did not answer within {self.timeout_s}s", ExitCode.BACKEND
            ) from exc
        duration_ms = int((time.monotonic() - started) * 1000)

        if process.returncode != 0:
            raise SddcError(
                f"{EXECUTABLE} exited {process.returncode}: {_failure_detail(process)}",
                ExitCode.BACKEND,
            )
        return self._answer(process.stdout, duration_ms)

    # -- pieces ----------------------------------------------------------
    def _argv(self, question: Question) -> list[str]:
        return [
            EXECUTABLE,
            "-p", question.prompt,
            "--model", self.model,
            "--output-format", "json",
            "--json-schema", json.dumps(question.schema, ensure_ascii=False),
        ]

    def _child_env(self) -> dict[str, str]:
        env = dict(os.environ)
        env["SDD_COMPILER_CHILD"] = "1"
        if not self.pass_api_key:
            env.pop("ANTHROPIC_API_KEY", None)
        if not self.thinking:
            # Claude Code thinks by default. For a small closed question it cost
            # ~2,900 of ~3,600 output tokens and 25-35 s instead of ~5 s (F3 D10).
            env["MAX_THINKING_TOKENS"] = "0"
        return env

    def _answer(self, stdout: str, duration_ms: int) -> Answer:
        try:
            payload = json.loads(stdout)
        except json.JSONDecodeError as exc:
            head = stdout.strip()[:120] or "<empty>"
            raise SddcError(
                f"{EXECUTABLE} returned output that is not JSON: {head}", ExitCode.BACKEND
            ) from exc

        if "structured_output" not in payload:
            # I-79: this call produced nothing usable; the backend is fine. The batch layer
            # re-asks each item alone, which is both smaller and usually enough.
            raise AnswerRejected(
                f"{EXECUTABLE} returned no structured_output — the answer did not match the "
                f"schema, or --json-schema was rejected")

        usage = payload.get("usage") or {}
        return Answer(
            data=payload["structured_output"],
            backend=self.name,
            model=payload.get("model", self.model),
            usage={
                "input_tokens": int(usage.get("input_tokens", 0)),
                "output_tokens": int(usage.get("output_tokens", 0)),
                "cache_read_tokens": int(usage.get("cache_read_input_tokens", 0)),
                "cache_creation_tokens": int(usage.get("cache_creation_input_tokens", 0)),
            },
            cost_usd=payload.get("total_cost_usd"),
            duration_ms=duration_ms,
            cli_version=self.cli_version,
        )

    @property
    def cli_version(self) -> str | None:
        """Read once per run and recorded with every judgment (hazard 2)."""
        if self._cli_version is None:
            self._cli_version = self._read_cli_version()
        return self._cli_version

    def _read_cli_version(self) -> str | None:
        try:
            result = subprocess.run(
                [EXECUTABLE, "--version"], capture_output=True, text=True, timeout=15
            )
        except (OSError, subprocess.SubprocessError):
            return None
        return result.stdout.strip() or None


def _failure_detail(process: subprocess.CompletedProcess[str]) -> str:
    """The reason in words. Claude Code puts API errors (e.g. a 429 usage limit) in the
    JSON `result` on stdout, while stderr may hold only an unrelated warning (I-11)."""
    try:
        payload = json.loads(process.stdout or "")
    except json.JSONDecodeError:
        payload = None
    if isinstance(payload, dict) and payload.get("result"):
        status = payload.get("api_error_status")
        return f"{payload['result']}" + (f" (API status {status})" if status else "")
    lines = (process.stderr or process.stdout or "").strip().splitlines()
    return lines[-1] if lines else "no output"

