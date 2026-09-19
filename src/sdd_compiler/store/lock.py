"""One writer at a time (F1 §4, D9).

A run takes the lock before it writes anything and releases it at the end. A
second run waits, and after 15 seconds it exits `4` rather than waiting forever
or writing on top of another run.

⚑ A lock whose holder is gone — a crashed run, a killed terminal — is reclaimed
rather than honoured. Otherwise one crash wedges the repository until someone
deletes a file by hand, and the tool would have taught its user to delete locks.
"""
from __future__ import annotations

import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from types import TracebackType

from ..errors import ExitCode, SddcError

DEFAULT_WAIT_SECONDS = 15
LOCK_NAME = "run.lock"   # not `lock`: F4 §4.1 reserves `lock/` for the judgment lock
_POLL_SECONDS = 0.05


class StoreLock:
    """A context manager holding the store lock for the life of a run."""

    def __init__(self, store_dir: Path, wait_seconds: float = DEFAULT_WAIT_SECONDS) -> None:
        self.store_dir = Path(store_dir)
        self.path = self.store_dir / LOCK_NAME
        self.wait_seconds = wait_seconds
        self.reclaimed = False

    def __enter__(self) -> StoreLock:
        self.store_dir.mkdir(parents=True, exist_ok=True)
        deadline = time.monotonic() + self.wait_seconds
        while True:
            if self._try_acquire():
                return self
            if self._holder_is_gone():
                self.path.unlink(missing_ok=True)
                self.reclaimed = True
                continue
            if time.monotonic() >= deadline:
                raise SddcError(
                    f"another sddc run holds the store lock ({self.path}); "
                    f"waited {self.wait_seconds:g}s",
                    ExitCode.STORE,
                )
            time.sleep(_POLL_SECONDS)

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.release()

    def release(self) -> None:
        self.path.unlink(missing_ok=True)

    def _try_acquire(self) -> bool:
        payload = json.dumps(
            {"pid": os.getpid(), "started_at": datetime.now(timezone.utc).isoformat()}
        )
        try:
            descriptor = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError:
            return False
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(payload)
        return True

    def _holder_is_gone(self) -> bool:
        """True when the recorded pid is not running, or the file is unreadable."""
        try:
            holder = json.loads(self.path.read_text(encoding="utf-8"))
            pid = int(holder["pid"])
        except (OSError, ValueError, KeyError, TypeError):
            return True
        if pid == os.getpid():
            return False
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            return True
        except PermissionError:
            return False
        return False
