"""T12 — the judgment lock: every accepted answer recorded, replayed through the guards (F3 §4.7).

Tier: unit.
"""
from __future__ import annotations

import json

from sdd_compiler.atomize.lock import JudgmentLock
from sdd_compiler.atomize.qatom import atomize_blocks
from sdd_compiler.llm import FakeBackend

BLOCK = {"id": "B-000001", "text": "Links must expire.", "kind": "paragraph",
         "heading_path": ["Sharing"], "table_header": None}
OTHER = {"id": "B-000002", "text": "Links must be revocable.", "kind": "paragraph",
         "heading_path": ["Sharing"], "table_header": None}


def answer(*blocks):
    return {"blocks": [{"block_id": b["id"], "sentences": [{"quote": b["text"], "role": "requirement"}],
                        "atoms": [{"kind": "requirement", "quotes": [b["text"]]}]} for b in blocks]}


def test_an_accepted_answer_is_recorded_per_item_with_the_call_usage_once(tmp_path):
    lock = JudgmentLock(tmp_path, start=0)
    outcome = atomize_blocks([BLOCK, OTHER], FakeBackend([answer(BLOCK, OTHER)]), lock=lock)
    first, second = lock.new_records
    assert (first["id"], second["id"]) == ("J-000001", "J-000002")
    assert first["kind"] == "q-atom" and first["schema_version"] == "q-atom/1"
    assert first["usage"] is not None and first["batch_of"] is None
    assert second["usage"] is None and second["batch_of"] == "J-000001"
    assert first["confirmed"] == "auto" and first["attempts"] == 1
    assert outcome.judgments == {"B-000001": "J-000001", "B-000002": "J-000002"}


def test_a_lock_hit_replays_without_a_call_and_through_the_guards(tmp_path):
    lock = JudgmentLock(tmp_path, start=0)
    atomize_blocks([BLOCK], FakeBackend([answer(BLOCK)]), lock=lock)
    lock.save_to(tmp_path)

    again = JudgmentLock(tmp_path, start=lock.counter)
    backend = FakeBackend([])                               # any call would fail the test
    outcome = atomize_blocks([BLOCK], backend, lock=again)
    assert backend.asked == []
    assert [a.quotes for a in outcome.atoms] == [["Links must expire."]]
    assert outcome.judgments == {"B-000001": "J-000001"}
    assert again.replayed == 1 and again.new_records == []


def test_the_key_ignores_the_block_id_so_a_moved_block_still_hits(tmp_path):
    lock = JudgmentLock(tmp_path, start=0)
    atomize_blocks([BLOCK], FakeBackend([answer(BLOCK)]), lock=lock)
    moved = {**BLOCK, "id": "B-000009"}
    outcome = atomize_blocks([moved], FakeBackend([]), lock=lock)
    assert outcome.atoms[0].block_id == "B-000009"


def test_only_the_misses_of_a_batch_are_asked(tmp_path):
    lock = JudgmentLock(tmp_path, start=0)
    atomize_blocks([BLOCK], FakeBackend([answer(BLOCK)]), lock=lock)
    backend = FakeBackend([answer(OTHER)])
    atomize_blocks([BLOCK, OTHER], backend, lock=lock)
    assert [q.payload["block_ids"] for q in backend.asked] == [["B-000002"]]


def test_ac_3_20_no_replay_asks_even_on_a_hit(tmp_path):
    lock = JudgmentLock(tmp_path, start=0)
    atomize_blocks([BLOCK], FakeBackend([answer(BLOCK)]), lock=lock)
    fresh = JudgmentLock(tmp_path, start=lock.counter, replay=False)
    fresh.records.update(lock.records)
    backend = FakeBackend([answer(BLOCK)])
    atomize_blocks([BLOCK], backend, lock=fresh)
    assert len(backend.asked) == 1 and fresh.replayed == 0


def test_a_changed_prompt_is_a_miss(tmp_path, monkeypatch):
    """The key includes the question's instructions, so tuning a prompt re-asks."""
    lock = JudgmentLock(tmp_path, start=0)
    atomize_blocks([BLOCK], FakeBackend([answer(BLOCK)]), lock=lock)
    import sdd_compiler.atomize.qatom as qatom
    monkeypatch.setattr(qatom, "_INSTRUCTIONS", qatom._INSTRUCTIONS + "\nBe brief.")
    backend = FakeBackend([answer(BLOCK)])
    atomize_blocks([BLOCK], backend, lock=lock)
    assert len(backend.asked) == 1


def test_a_replayed_answer_that_now_fails_a_guard_is_asked_again(tmp_path):
    lock = JudgmentLock(tmp_path, start=0)
    atomize_blocks([BLOCK], FakeBackend([answer(BLOCK)]), lock=lock)
    [record] = lock.records.values()
    record["answer"]["atoms"][0]["quotes"] = ["not in the block"]      # as if guards got stricter
    backend = FakeBackend([answer(BLOCK)])
    atomize_blocks([BLOCK], backend, lock=lock)
    assert len(backend.asked) == 1


def test_saved_lock_files_are_sorted_json_lines_per_kind(tmp_path):
    lock = JudgmentLock(tmp_path, start=0)
    atomize_blocks([BLOCK, OTHER], FakeBackend([answer(BLOCK, OTHER)]), lock=lock)
    lock.save_to(tmp_path)
    lines = (tmp_path / "lock" / "q-atom.jsonl").read_text().splitlines()
    assert [json.loads(l)["id"] for l in lines] == ["J-000001", "J-000002"]
