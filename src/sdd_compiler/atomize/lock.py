"""F3 §4.7 — the judgment lock: every accepted answer recorded; a hit replays it (CT-3.2).

The graph is a build artifact (vision O1): with the same sources, profile and
lock, a compile must produce the same bytes and cost nothing. That only holds if
model answers are recorded and replayed, because the model will not answer the
same way twice.

⚑ F3 D21 — the lock is kept **per item**, not per call. Q-ATOM, Q-DESC and Q-TERM
are batched (rel01 D30); keyed by batch, editing one block would change its
20-block batch and re-ask all twenty. Each block's, atom's or term's accepted
answer is its own record, keyed by its own input. A call's usage is stored once,
on its first record; the others point at it with `batch_of`, so costs are never
counted twice.

⚑ The key hashes the question kind, schema version, **the question's
instructions** and the item's canonical input. Adding the instructions to F3
§4.7's formula means a prompt change re-asks instead of replaying answers given
to a different prompt.

The item's id is not part of its input, so a block that moved keeps its answer.
A replayed answer still goes through every guard; if a guard now rejects it, the
item is asked again. The latest record for a key wins.
"""
from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from ..llm import Answer
from ..store.jsonl import read_jsonl
from ..store.transaction import Transaction

LOCK_DIR = "lock"
RECORD_KEYS = ("id", "kind", "schema_version", "input_hash", "backend", "model", "cli_version",
               "provisional",      # F6 §4.4: the verdict touched an ambiguous node
               "answer", "attempts", "usage", "batch_of", "duration_ms", "confirmed", "run")


class JudgmentLock:
    def __init__(self, store: Path, start: int, replay: bool = True, run_id: str | None = None) -> None:
        self.store = Path(store)
        self.counter = start
        self.replay = replay
        self.run_id = run_id
        self.records: dict[str, dict[str, Any]] = {}
        folder = self.store / LOCK_DIR
        if folder.is_dir():
            for path in sorted(folder.glob("*.jsonl")):
                for record in read_jsonl(path):
                    self.records[record["id"]] = record
        self.new_records: list[dict[str, Any]] = []
        self.replayed = 0
        self._indexed = -1
        self._index: dict[tuple[str, str], str] = {}

    @staticmethod
    def key(kind: str, schema_version: str, instructions: str, item_input: Mapping[str, Any]) -> str:
        canonical = json.dumps(
            {"kind": kind, "schema": schema_version, "instructions": instructions, "input": item_input},
            ensure_ascii=False, sort_keys=True, separators=(",", ":"),
        )
        return "sha256:" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    def lookup(self, kind: str, input_hash: str) -> dict[str, Any] | None:
        if not self.replay:
            return None
        if self._indexed != len(self.records):
            self._index = {(r["kind"], r["input_hash"]): r["id"]
                           for r in sorted(self.records.values(), key=lambda r: r["id"])}
            self._indexed = len(self.records)
        found = self._index.get((kind, input_hash))
        return self.records[found] if found else None

    def record(self, kind: str, schema_version: str, input_hash: str, answer_entry: Mapping[str, Any],
               answer: Answer, attempts: int, batch_of: str | None,
               provisional: bool | None = None) -> str:
        self.counter += 1
        identifier = f"J-{self.counter:06d}"
        first_of_call = batch_of is None
        record = {
            "id": identifier, "kind": kind, "schema_version": schema_version,
            "input_hash": input_hash, "backend": answer.backend, "model": answer.model,
            "provisional": provisional,
            "cli_version": answer.cli_version, "answer": dict(answer_entry), "attempts": attempts,
            "usage": ({"input_tokens": answer.usage.get("input_tokens", 0),
                       "output_tokens": answer.usage.get("output_tokens", 0),
                       "cache_read_tokens": answer.usage.get("cache_read_tokens", 0),
                       "cost_usd": answer.cost_usd} if first_of_call else None),
            "batch_of": batch_of,
            "duration_ms": answer.duration_ms if first_of_call else 0,
            "confirmed": "auto", "run": self.run_id,
        }
        self.records[identifier] = record
        self.new_records.append(record)
        return identifier

    def stage(self, transaction: Transaction) -> None:
        """Write every kind's file whole, sorted by id (F4 §4.2 determinism)."""
        kinds = sorted({r["kind"] for r in self.new_records})
        for kind in kinds:
            records = [r for r in self.records.values() if r["kind"] == kind]
            transaction.write_jsonl(f"{LOCK_DIR}/{kind}.jsonl", records, RECORD_KEYS)

    def save_to(self, store: Path) -> None:
        with Transaction(Path(store)) as transaction:
            self.stage(transaction)
