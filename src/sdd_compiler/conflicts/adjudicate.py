"""G4 §4 — the human verdict on a reported conflict, kept across runs (F6 AC-6.20).

M2 (precision) is *the* number the release close is about: of the conflicts the compiler reported,
how many a person judged real. Nothing else in the store records that, and it cannot be
reconstructed later — hence this file, the only code G4 asked for.

⚑ **F6 D14 — an adjudication is about one model verdict, not about a conflict id.** Each record
keeps the `judgment` id it was answering and the members at the time. When the pair is judged
again — an edit, `--no-replay` — the stored verdict is marked **stale** rather than deleted or
silently counted: the person answered a question about the old text. History is appended, never
rewritten, so a change of mind is visible.
"""
from __future__ import annotations

import json
from collections.abc import Mapping
from datetime import date as _date
from pathlib import Path
from typing import Any

from ..errors import ExitCode, SddcError
from ..store.graph import load_graph
from ..store.jsonl import read_jsonl

FILE = "adjudications.jsonl"
VERDICTS = ("real", "false")
KEYS = ("id", "conflict", "verdict", "note", "members", "judgment", "date")


def adjudications(store: Path) -> list[dict[str, Any]]:
    """Every recorded verdict, oldest first."""
    return read_jsonl(Path(store) / FILE)


def record_adjudication(store: Path, conflict_id: str, verdict: str, note: str | None = None,
                        date: str | None = None) -> dict[str, Any]:
    store = Path(store)
    if verdict not in VERDICTS:
        raise SddcError(f"verdict must be one of {', '.join(VERDICTS)}, not {verdict!r}",
                        ExitCode.USAGE)
    graph = load_graph(store)
    record = graph.conflicts.get(conflict_id)
    if record is None:
        known = ", ".join(sorted(graph.conflicts)[:10]) or "none yet"
        raise SddcError(f"no conflict {conflict_id!r} in this graph; known: {known}", ExitCode.INPUT)

    existing = adjudications(store)
    entry = {
        "id": f"ADJ-{len(existing) + 1:06d}",
        "conflict": conflict_id,
        "verdict": verdict,
        "note": note,
        "members": list(record["members"]),
        "judgment": record["judgment"],
        "date": date or _date.today().isoformat(),
    }
    with (store / FILE).open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps({key: entry[key] for key in KEYS}, ensure_ascii=False) + "\n")
    return entry


def verdicts_for(store: Path) -> dict[str, dict[str, Any]]:
    """Conflict id → the latest human verdict, and whether it is stale (F6 D14)."""
    graph = load_graph(Path(store))
    latest: dict[str, dict[str, Any]] = {}
    for entry in adjudications(store):
        latest[entry["conflict"]] = entry
    return {conflict_id: _state(entry, graph.conflicts.get(conflict_id))
            for conflict_id, entry in latest.items()}


def _state(entry: Mapping[str, Any], record: Mapping[str, Any] | None) -> dict[str, Any]:
    stale = record is None or record["judgment"] != entry["judgment"] \
        or list(record["members"]) != list(entry["members"])
    return {"verdict": entry["verdict"], "stale": stale, "note": entry["note"]}
