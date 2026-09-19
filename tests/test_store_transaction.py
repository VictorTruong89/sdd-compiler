"""T2 — the all-or-nothing transaction.

Serves F4 AC-4.4 (a failed transaction changes nothing) and F1 §4 "runs are atomic".
Tier: integration.
"""
from __future__ import annotations

import pytest

from sdd_compiler.store.jsonl import read_jsonl
from sdd_compiler.store.transaction import Transaction

ORDER = ("id", "text")


def test_a_committed_transaction_writes_every_file(tmp_path):
    with Transaction(tmp_path) as tx:
        tx.write_jsonl("blocks.jsonl", [{"id": "B-1", "text": "x"}], ORDER)
        tx.write_text("views/map.md", "# map\n")
    assert read_jsonl(tmp_path / "blocks.jsonl") == [{"id": "B-1", "text": "x"}]
    assert (tmp_path / "views" / "map.md").read_text(encoding="utf-8") == "# map\n"


def test_ac_4_4_a_failed_transaction_changes_nothing(tmp_path):
    (tmp_path / "blocks.jsonl").write_text('{"id": "B-0", "text": "before"}\n', encoding="utf-8")
    before = (tmp_path / "blocks.jsonl").read_bytes()

    with pytest.raises(RuntimeError):
        with Transaction(tmp_path) as tx:
            tx.write_jsonl("blocks.jsonl", [{"id": "B-1", "text": "after"}], ORDER)
            tx.write_text("runs.jsonl", "{}\n")
            raise RuntimeError("something failed mid-run")

    assert (tmp_path / "blocks.jsonl").read_bytes() == before
    assert not (tmp_path / "runs.jsonl").exists()


def test_no_temporary_files_survive_either_outcome(tmp_path):
    with Transaction(tmp_path) as tx:
        tx.write_jsonl("blocks.jsonl", [{"id": "B-1", "text": "x"}], ORDER)
    with pytest.raises(RuntimeError):
        with Transaction(tmp_path) as tx:
            tx.write_text("other.md", "x")
            raise RuntimeError("boom")
    leftovers = [p.name for p in tmp_path.rglob("*") if ".sddc-tmp" in p.name]
    assert leftovers == []


def test_a_later_write_in_one_transaction_wins(tmp_path):
    with Transaction(tmp_path) as tx:
        tx.write_text("note.md", "first")
        tx.write_text("note.md", "second")
    assert (tmp_path / "note.md").read_text(encoding="utf-8") == "second"
