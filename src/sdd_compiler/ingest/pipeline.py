"""F1 — the ingest phase: spec files in, blocks in the store out.

One run does the whole set, under the store lock, in one transaction: either
every file's blocks are written, or none are (AC-1.22). The graph is a build
artifact, so a half-written store must never exist.

The phase is deliberately model-free. In M2 the atomizer runs after it, inside
the same `compile` command, over the pending blocks this phase reports.
"""
from __future__ import annotations

import fnmatch
import hashlib
import os
from collections.abc import Iterable, Sequence
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .. import __version__
from ..errors import ExitCode, SddcError
from ..profile import Profile, STORE_DIR, load_profile
from ..store.jsonl import read_jsonl
from ..store.lock import DEFAULT_WAIT_SECONDS, StoreLock
from ..store.transaction import Transaction
from .identity import BLOCK_KEY_ORDER, IdAllocator, is_live, pending_status, reconcile
from .segment import segment_markdown

BLOCKS_FILE = "blocks.jsonl"
SOURCES_FILE = "sources.jsonl"
RUNS_FILE = "runs.jsonl"

SOURCE_KEY_ORDER = ("path", "file_hash", "last_ingest_run")
#: `conflicts` (F6 CT-6.2, with F5 CT-5.3 inside) is null until a check phase runs (I-97); records
#: written before it existed read as null.
RUN_KEY_ORDER = ("id", "started_at", "command", "files", "counts", "cli_version", "conflicts")


@dataclass
class IngestResult:
    run_id: str
    counts: dict[str, int] = field(default_factory=dict)
    files: list[str] = field(default_factory=list)


def find_root(start: Path | None = None) -> Path:
    """The nearest parent holding `.sdd/`, or the start directory itself."""
    current = Path(start or Path.cwd()).resolve()
    for candidate in [current, *current.parents]:
        if (candidate / STORE_DIR).is_dir():
            return candidate
    return current


def lock_wait_seconds() -> float:
    """The lock wait, overridable for tests (F1 D9: 15 s in normal use)."""
    return float(os.environ.get("SDDC_LOCK_WAIT_SECONDS", DEFAULT_WAIT_SECONDS))


def ingest(root: Path, paths: Sequence[str] | None = None, command: str = "compile") -> IngestResult:
    """Segment every named spec file (or all of them) and update the store."""
    root = Path(root).resolve()
    profile = load_profile(root)
    sources = _select_sources(root, profile, paths)

    with StoreLock(root / STORE_DIR, wait_seconds=lock_wait_seconds()):
        blocks = read_jsonl(root / STORE_DIR / BLOCKS_FILE)
        known_sources = read_jsonl(root / STORE_DIR / SOURCES_FILE)
        runs = read_jsonl(root / STORE_DIR / RUNS_FILE)
        run_id = _next_run_id(runs)

        # Read every file before writing anything: one unreadable file must not
        # leave half the store updated (AC-1.22).
        texts = {source: _read_text(root / source) for source in sources}

        allocator = IdAllocator.from_records(blocks)
        by_source: dict[str, list[dict[str, Any]]] = {}
        for block in blocks:
            by_source.setdefault(block["source"], []).append(block)

        counts = {"new": 0, "changed": 0, "unchanged": 0, "removed": 0}
        for source, text in texts.items():
            result = reconcile(
                by_source.get(source, []),
                segment_markdown(text),
                source=source,
                run=run_id,
                allocator=allocator,
            )
            by_source[source] = result.records
            for key, value in result.counts.items():
                counts[key] += value

        # `last_ingest_run` is stamped only when the file's content actually
        # changed. Stamping every run would make the store differ after a compile
        # that found nothing, and "nothing changed" must leave no trace but a run
        # record (F1 AC-1.8).
        source_records = {record["path"]: record for record in known_sources}
        for source, text in texts.items():
            digest = "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()
            previous = source_records.get(source)
            unchanged = previous is not None and previous["file_hash"] == digest
            source_records[source] = {
                "path": source,
                "file_hash": digest,
                "last_ingest_run": previous["last_ingest_run"] if unchanged else run_id,
            }

        run_record = {
            "id": run_id,
            "started_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "command": command,
            "files": list(texts),
            "counts": counts,
            "cli_version": __version__,
            "conflicts": None,
        }

        with Transaction(root / STORE_DIR) as transaction:
            transaction.write_jsonl(
                BLOCKS_FILE, _flatten(by_source), BLOCK_KEY_ORDER
            )
            transaction.write_jsonl(
                SOURCES_FILE, source_records.values(), SOURCE_KEY_ORDER,
                sort_key=lambda record: record["path"],
            )
            transaction.write_jsonl(
                RUNS_FILE, [*map(with_run_defaults, runs), run_record], RUN_KEY_ORDER,
                sort_key=lambda record: record["id"],
            )

    return IngestResult(run_id=run_id, counts=counts, files=list(texts))


def status(root: Path) -> dict[str, Any]:
    """CT-1.5 — what exists, and what the atomizer still has to look at."""
    root = Path(root).resolve()
    profile = load_profile(root)  # AC-1.24: a missing store is a store error
    blocks = read_jsonl(root / STORE_DIR / BLOCKS_FILE)
    sources = read_jsonl(root / STORE_DIR / SOURCES_FILE)
    runs = read_jsonl(root / STORE_DIR / RUNS_FILE)

    # Derived, never stored (F1 D13).
    marked = [(block, pending_status(block, profile.include_code_blocks, profile.skip_headings,
                                        profile.contract_languages))
              for block in blocks]
    pending = [(block, state) for block, state in marked if state is not None]
    return {
        "run": runs[-1]["id"] if runs else None,
        "counts": {
            "sources": len(sources),
            "blocks": len([block for block in blocks if is_live(block)]),
            "pending": len(pending),
        },
        "pending": [
            {
                "id": block["id"],
                "status": state,
                "source": block["source"],
                "lines": block["lines"],
                "heading_path": block["heading_path"],
                "kind": block["kind"],
                "text": block["text"],
            }
            for block, state in pending
        ],
    }


# -- helpers ----------------------------------------------------------------

def _flatten(by_source: dict[str, list[dict[str, Any]]]) -> list[dict[str, Any]]:
    return [record for records in by_source.values() for record in records]


def _next_run_id(runs: Sequence[dict[str, Any]]) -> str:
    highest = 0
    for run in runs:
        identifier = str(run.get("id", ""))
        if identifier.startswith("R-") and identifier[2:].isdigit():
            highest = max(highest, int(identifier[2:]))
    return f"R-{highest + 1:06d}"


def with_run_defaults(record: dict[str, Any]) -> dict[str, Any]:
    """A run record from before I-97 has no `conflicts`; it reads as not recorded (null)."""
    return {**record, "conflicts": record.get("conflicts")}


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SddcError(f"{path}: no such file", ExitCode.INPUT) from exc
    except UnicodeDecodeError as exc:
        raise SddcError(f"{path}: not valid UTF-8", ExitCode.INPUT) from exc
    except OSError as exc:
        raise SddcError(f"{path}: cannot be read ({exc.strerror})", ExitCode.INPUT) from exc


def _select_sources(root: Path, profile: Profile, paths: Sequence[str] | None) -> list[str]:
    """Resolve arguments to repo-relative spec sources, or fail loud."""
    if not paths:
        return sorted(_all_sources(root, profile))

    selected: list[str] = []
    for raw in paths:
        candidate = (root / raw).resolve() if not Path(raw).is_absolute() else Path(raw).resolve()
        relative = _relative_to_root(candidate, root)
        if candidate.is_dir():
            matches = sorted(
                source for source in _all_sources(root, profile)
                if source == relative or source.startswith(f"{relative}/")
            )
            if not matches:
                raise SddcError(
                    f"{relative}: no files under it match spec_globs "
                    f"({', '.join(profile.spec_globs)})",
                    ExitCode.INPUT,
                )
            selected.extend(matches)
            continue
        if not _matches(relative, profile):
            raise SddcError(
                f"{relative}: not a spec source; spec_globs are "
                f"{', '.join(profile.spec_globs)}",
                ExitCode.INPUT,
            )
        selected.append(relative)
    return sorted(dict.fromkeys(selected))


def _relative_to_root(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError as exc:
        raise SddcError(f"{path}: outside the repository root {root}", ExitCode.INPUT) from exc


def _all_sources(root: Path, profile: Profile) -> Iterable[str]:
    for pattern in profile.spec_globs:
        for path in root.glob(pattern):
            if path.is_file():
                relative = path.relative_to(root).as_posix()
                if not _excluded(relative, profile):
                    yield relative


def _matches(relative: str, profile: Profile) -> bool:
    if _excluded(relative, profile):
        return False
    return any(fnmatch.fnmatch(relative, pattern) for pattern in profile.spec_globs)


def _excluded(relative: str, profile: Profile) -> bool:
    return any(fnmatch.fnmatch(relative, pattern) for pattern in profile.exclude_globs)
