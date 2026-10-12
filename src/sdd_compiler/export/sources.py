"""F7 §4.2 step 2, D7 — are the specs on disk the ones the graph was compiled from?"""
from __future__ import annotations

import hashlib
from pathlib import Path

from ..errors import ExitCode, SddcError
from ..ingest.pipeline import SOURCES_FILE, _all_sources, _read_text
from ..profile import STORE_DIR, Profile
from ..store.jsonl import read_jsonl


def check_sources(root: Path, profile: Profile, raise_on_problem: bool = False) -> list[str]:
    """Each changed, missing or new spec file, as a line; empty when the graph is current.

    The hash is the one ingest recorded: sha256 of the UTF-8 of `read_text` (universal newlines).
    """
    root = Path(root)
    recorded = {r["path"]: r["file_hash"] for r in read_jsonl(root / STORE_DIR / SOURCES_FILE)}
    current = set(_all_sources(root, profile))
    problems = []
    for path in sorted(recorded):
        file = root / path
        if not file.is_file():
            problems.append(f"missing: {path}")
        elif "sha256:" + hashlib.sha256(_read_text(file).encode("utf-8")).hexdigest() != recorded[path]:
            problems.append(f"changed: {path}")
    problems += [f"new: {path}" for path in sorted(current - set(recorded))]
    if problems and raise_on_problem:
        raise SddcError("the specs changed since the last compile — run sddc compile first:\n  "
                        + "\n  ".join(problems), ExitCode.INPUT)
    return problems
