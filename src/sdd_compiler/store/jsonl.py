"""JSON Lines with a fixed key order, sorted lines and stable bytes.

Determinism is a contract (F4 AC-4.3, F3 AC-3.19): the same records must always
produce the same file, so a rebuild that changed nothing has an empty git diff.
Three rules make that true:

1. the caller passes the key order — never Python's insertion order;
2. lines are sorted by a key (the record id by default);
3. no timestamps are written here; they live in `runs.jsonl` only.
"""
from __future__ import annotations

import json
from collections.abc import Callable, Iterable, Mapping, Sequence
from pathlib import Path
from typing import Any

from ..errors import ExitCode, SddcError

Record = Mapping[str, Any]


def dumps_record(record: Record, key_order: Sequence[str]) -> str:
    """Serialize one record, in the given key order.

    A key outside the order, or a missing one, is an error: a field written by
    accident is a field nobody validated, and a silently dropped field is worse.
    """
    unexpected = [key for key in record if key not in key_order]
    if unexpected:
        raise SddcError(
            f"record {record.get('id', '<no id>')}: unexpected field(s) "
            f"{', '.join(sorted(unexpected))}",
            ExitCode.STORE,
        )
    missing = [key for key in key_order if key not in record]
    if missing:
        raise SddcError(
            f"record {record.get('id', '<no id>')}: missing field(s) {', '.join(missing)}",
            ExitCode.STORE,
        )
    ordered = {key: record[key] for key in key_order}
    return json.dumps(ordered, ensure_ascii=False)


def dumps_records(
    records: Iterable[Record],
    key_order: Sequence[str],
    sort_key: Callable[[Record], Any] | None = None,
) -> str:
    """The full file body, sorted and newline-terminated (empty when there are none)."""
    key = sort_key or (lambda record: record.get("id", ""))
    lines = [dumps_record(record, key_order) for record in sorted(records, key=key)]
    return "".join(f"{line}\n" for line in lines)


def write_jsonl(
    path: Path,
    records: Iterable[Record],
    key_order: Sequence[str],
    sort_key: Callable[[Record], Any] | None = None,
) -> None:
    """Write a JSONL file directly. Inside a run, prefer `Transaction.write_jsonl`."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(dumps_records(records, key_order, sort_key), encoding="utf-8", newline="\n")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    """Read a JSONL file. A missing file is an empty list; a corrupt line names itself."""
    path = Path(path)
    if not path.exists():
        return []
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise SddcError(f"{path.name} is not valid UTF-8", ExitCode.STORE) from exc

    records: list[dict[str, Any]] = []
    for number, line in enumerate(text.splitlines(), start=1):
        if not line.strip():
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise SddcError(f"{path.name} line {number} is not valid JSON: {exc.msg}", ExitCode.STORE) from exc
    return records
