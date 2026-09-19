"""All-or-nothing writes (F1 §4, F4 §4.2, AC-4.4).

Every file a run produces is written to a temporary neighbour first. Only when
the whole run succeeds are they renamed into place. A failure part-way leaves
the store exactly as it was, so a half-compiled graph never exists on disk.

Rename is atomic within a directory on POSIX, which is why the temporary file
sits beside its target rather than in a system temp directory.
"""
from __future__ import annotations

import os
from collections.abc import Callable, Iterable, Mapping, Sequence
from pathlib import Path
from types import TracebackType
from typing import Any

from .jsonl import dumps_records

TEMP_SUFFIX = ".sddc-tmp"


class Transaction:
    """Collect writes, then commit them together.

    Used as a context manager: leaving the block normally commits; leaving it
    through an exception discards every staged file and re-raises.
    """

    def __init__(self, root: Path) -> None:
        self.root = Path(root)
        self._staged: dict[Path, Path] = {}
        self._deleted: set[Path] = set()

    # -- staging ---------------------------------------------------------
    def write_text(self, relative_path: str | Path, text: str) -> Path:
        target = self.root / relative_path
        temporary = target.with_name(f"{target.name}{TEMP_SUFFIX}")
        temporary.parent.mkdir(parents=True, exist_ok=True)
        with open(temporary, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        self._staged[target] = temporary
        return target

    def write_jsonl(
        self,
        relative_path: str | Path,
        records: Iterable[Mapping[str, Any]],
        key_order: Sequence[str],
        sort_key: Callable[[Mapping[str, Any]], Any] | None = None,
    ) -> Path:
        return self.write_text(relative_path, dumps_records(records, key_order, sort_key))

    def delete(self, relative_path: str | Path) -> None:
        """Remove a file at commit time — e.g. a family shard that emptied (F4 §4.1)."""
        self._deleted.add(self.root / relative_path)

    # -- lifecycle -------------------------------------------------------
    def commit(self) -> None:
        for target, temporary in self._staged.items():
            os.replace(temporary, target)
        for target in self._deleted - set(self._staged):
            target.unlink(missing_ok=True)
        self._staged.clear()
        self._deleted.clear()

    def rollback(self) -> None:
        for temporary in self._staged.values():
            temporary.unlink(missing_ok=True)
        self._staged.clear()
        self._deleted.clear()

    def __enter__(self) -> Transaction:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        if exc_type is None:
            self.commit()
        else:
            self.rollback()
