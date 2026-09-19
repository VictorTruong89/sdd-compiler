"""T2 — JSON Lines writing: fixed key order, sorted lines, byte determinism.

Serves F4 AC-4.3 (byte determinism). Tier: property + unit.
"""
from __future__ import annotations

import json

import pytest

from sdd_compiler.errors import SddcError
from sdd_compiler.store.jsonl import dumps_record, read_jsonl, write_jsonl

ORDER = ("id", "source", "lines", "text")

RECORDS = [
    {"id": "B-000002", "source": "b.md", "lines": [3, 4], "text": "second"},
    {"id": "B-000001", "source": "a.md", "lines": [1, 2], "text": "first ⚠ ★"},
]


def test_records_are_sorted_by_id(tmp_path):
    path = tmp_path / "blocks.jsonl"
    write_jsonl(path, RECORDS, ORDER)
    ids = [json.loads(line)["id"] for line in path.read_text(encoding="utf-8").splitlines()]
    assert ids == ["B-000001", "B-000002"]


def test_ac_4_3_insertion_order_does_not_change_the_bytes(tmp_path):
    """F4 AC-4.3 — the same records in a different order give identical bytes."""
    first, second = tmp_path / "a.jsonl", tmp_path / "b.jsonl"
    write_jsonl(first, RECORDS, ORDER)
    write_jsonl(second, list(reversed(RECORDS)), ORDER)
    assert first.read_bytes() == second.read_bytes()


def test_key_order_is_the_given_order_not_python_order(tmp_path):
    path = tmp_path / "blocks.jsonl"
    scrambled = [{"text": "t", "lines": [1, 1], "id": "B-000001", "source": "a.md"}]
    write_jsonl(path, scrambled, ORDER)
    line = path.read_text(encoding="utf-8").splitlines()[0]
    assert list(json.loads(line)) == list(ORDER)


def test_unicode_is_kept_verbatim_and_file_ends_with_newline(tmp_path):
    path = tmp_path / "blocks.jsonl"
    write_jsonl(path, RECORDS, ORDER)
    raw = path.read_bytes().decode("utf-8")
    assert "⚠ ★" in raw
    assert raw.endswith("\n")
    assert "\r" not in raw


def test_round_trip(tmp_path):
    path = tmp_path / "blocks.jsonl"
    write_jsonl(path, RECORDS, ORDER)
    assert read_jsonl(path) == sorted(RECORDS, key=lambda record: record["id"])


def test_reading_a_missing_file_gives_an_empty_list(tmp_path):
    assert read_jsonl(tmp_path / "absent.jsonl") == []


def test_a_key_outside_the_order_is_rejected_by_name():
    """Fail loud: an unexpected field must never be written silently."""
    with pytest.raises(SddcError) as excinfo:
        dumps_record({"id": "B-1", "surprise": 1}, ("id",))
    assert "surprise" in str(excinfo.value)


def test_a_missing_required_key_is_rejected_by_name():
    with pytest.raises(SddcError) as excinfo:
        dumps_record({"source": "a.md"}, ("id", "source"))
    assert "id" in str(excinfo.value)


def test_corrupt_line_is_reported_with_its_line_number(tmp_path):
    path = tmp_path / "blocks.jsonl"
    path.write_text('{"id": "B-1"}\nnot json\n', encoding="utf-8")
    with pytest.raises(SddcError) as excinfo:
        read_jsonl(path)
    message = str(excinfo.value)
    assert "line 2" in message and "blocks.jsonl" in message
