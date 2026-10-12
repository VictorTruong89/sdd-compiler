"""The `.sdd/` store: plain text, deterministic, written all-or-nothing.

Three primitives, used by every writer in the compiler:

- `jsonl`        — one record per line, fixed key order, sorted by id;
- `transaction`  — write temporary files, then rename them together;
- `lock`         — one writer at a time (F1 D9: a 15 s wait, then exit 4).
"""
from __future__ import annotations

from .jsonl import read_jsonl, write_jsonl
from .lock import StoreLock
from .transaction import Transaction

__all__ = ["read_jsonl", "write_jsonl", "StoreLock", "Transaction"]
