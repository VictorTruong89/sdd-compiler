"""T2 — the store lock: one writer at a time.

Serves F1 AC-1.26 (a second run waits, then exits 4). Tier: integration.
"""
from __future__ import annotations

import os
import time

import pytest

from sdd_compiler.errors import ExitCode, SddcError
from sdd_compiler.store.lock import DEFAULT_WAIT_SECONDS, StoreLock


def test_the_default_wait_is_fifteen_seconds():
    """F1 D9 — the lock wait is 15 s."""
    assert DEFAULT_WAIT_SECONDS == 15


def test_the_lock_is_released_after_use(tmp_path):
    with StoreLock(tmp_path):
        assert (tmp_path / "run.lock").exists()
    assert not (tmp_path / "run.lock").exists()


def test_ac_1_26_a_second_holder_waits_then_exits_4(tmp_path):
    with StoreLock(tmp_path):
        started = time.monotonic()
        with pytest.raises(SddcError) as excinfo:
            with StoreLock(tmp_path, wait_seconds=0.3):
                pass
        waited = time.monotonic() - started
    assert excinfo.value.exit_code is ExitCode.STORE
    assert "lock" in str(excinfo.value)
    assert waited >= 0.3


def test_a_lock_left_by_a_dead_process_is_reclaimed(tmp_path):
    """A crashed run must not wedge the repository forever."""
    (tmp_path).mkdir(exist_ok=True)
    (tmp_path / "run.lock").write_text('{"pid": 2147483640, "started_at": "x"}', encoding="utf-8")
    with StoreLock(tmp_path, wait_seconds=0.2) as lock:
        assert lock.reclaimed is True
    assert not (tmp_path / "run.lock").exists()


def test_the_lock_records_the_holder(tmp_path):
    with StoreLock(tmp_path):
        payload = (tmp_path / "run.lock").read_text(encoding="utf-8")
    assert str(os.getpid()) in payload
