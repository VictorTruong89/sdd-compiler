"""Exit codes and the one error type the CLI turns into them (F1 CT-1.6).

`0` success · `1` usage · `2` input · `3` conflicts exist (F6) · `4` store
· `5` call cap reached (F3) · `6` model backend unavailable (F3).
"""
from __future__ import annotations

from enum import IntEnum


class ExitCode(IntEnum):
    OK = 0
    USAGE = 1
    INPUT = 2
    CONFLICTS = 3
    STORE = 4
    CALL_CAP = 5
    BACKEND = 6


class SddcError(Exception):
    """An error that names what is wrong and which exit code it carries.

    Fail loud (vision §3 O4): every message names the offending file or field.
    """

    def __init__(self, message: str, exit_code: ExitCode = ExitCode.INPUT) -> None:
        super().__init__(message)
        self.exit_code = exit_code
