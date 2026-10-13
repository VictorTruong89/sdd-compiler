"""Hidden tests for the `lend` task — black-box, through the command, never shown to the agent.

They test the consistent part of the spec and the planted items that have one right answer (P5–P9,
P11). They never depend on how a planted contradiction (P1–P4, P10) is resolved: no fee reaches the
cap (P1), no check falls on a due date (P2), the report's extra columns are allowed (P3), no member
with more than $5 in fees borrows again (P4), and renewals happen on the due date, where both readings
of P10 agree. Requirement ids: ../requirements.md.

Run: LEND_CMD=/path/to/venv/bin/lend pytest hidden_tests/
"""
from __future__ import annotations

import csv
import json
import os
import shlex
import subprocess
from pathlib import Path

import pytest

LEND = shlex.split(os.environ.get("LEND_CMD", "lend"))
DAY0 = "2026-06-01"


def lend(root: Path, *args: str, now: str = DAY0) -> subprocess.CompletedProcess:
    env = {**os.environ, "LEND_NOW": now}
    return subprocess.run([*LEND, *args], cwd=root, env=env, capture_output=True, text=True, timeout=60)


def ok(root: Path, *args: str, now: str = DAY0) -> subprocess.CompletedProcess:
    result = lend(root, *args, now=now)
    assert result.returncode == 0, f"lend {' '.join(args)} → {result.returncode}: {result.stderr}"
    return result


def status(root: Path, now: str = DAY0) -> dict:
    return json.loads(ok(root, "status", "--json", now=now).stdout)


def loan(root: Path, item: str, now: str = DAY0) -> dict:
    [found] = [l for l in status(root, now)["loans"] if l["item"] == item]
    return found


def member(root: Path, member_id: str, now: str = DAY0) -> dict:
    [found] = [m for m in status(root, now)["members"] if m["id"] == member_id]
    return found


@pytest.fixture()
def root(tmp_path: Path) -> Path:
    ok(tmp_path, "init")
    return tmp_path


@pytest.fixture()
def library(root: Path) -> Path:
    for m, name in (("M1", "Ana"), ("M2", "Bo")):
        ok(root, "member", "add", m, "--name", name, "--email", f"{name.lower()}@example.org")
    for item, title, category in (("T1", "Hammer", "hand"), ("T2", "Rake", "garden"),
                                  ("T3", "Drill", "power"), ("T4", "Saw", "hand"),
                                  ("T5", "Sander", "power"), ("T6", "Level", "hand")):
        ok(root, "item", "add", item, "--title", title, "--category", category)
    return root


# -- store and command line ---------------------------------------------------------------------------

def test_r1_init_creates_a_store_and_refuses_twice(tmp_path):
    assert lend(tmp_path, "init").returncode == 0
    assert (tmp_path / ".lend").is_dir()
    assert lend(tmp_path, "init").returncode == 2


def test_r2_without_a_store_commands_exit_4_and_name_init(tmp_path):
    for args in (("status", "--json"), ("checkout", "T1", "M1")):
        result = lend(tmp_path, *args)
        assert result.returncode == 4, args
        assert "lend init" in result.stderr + result.stdout


def test_r23_an_unknown_command_is_a_usage_error(root):
    assert lend(root, "frobnicate").returncode == 1


# -- members and items --------------------------------------------------------------------------------

def test_r3_members_are_added_once(root):
    ok(root, "member", "add", "M1", "--name", "Ana", "--email", "ana@example.org")
    assert member(root, "M1")["name"] == "Ana"
    assert lend(root, "member", "add", "M1", "--name", "Ann", "--email", "ann@example.org").returncode == 2


def test_r4_p11_a_member_without_an_email_is_refused(root):
    """Exit 1 or 2: the spec calls a missing value an input error and a missing argument a usage error."""
    assert lend(root, "member", "add", "M9", "--name", "Nil").returncode in (1, 2)
    assert all(m["id"] != "M9" for m in status(root)["members"])


def test_r5_items_have_a_category_defaulting_to_hand(root):
    ok(root, "item", "add", "T1", "--title", "Hammer")
    assert lend(root, "item", "add", "T2", "--title", "Laser", "--category", "laser").returncode == 2
    assert lend(root, "item", "add", "T1", "--title", "Other").returncode == 2
    ok(root, "member", "add", "M1", "--name", "Ana", "--email", "ana@example.org")
    ok(root, "checkout", "T1", "M1")
    assert loan(root, "T1")["due"] == "2026-06-15"                    # a hand tool's period


# -- checkout -----------------------------------------------------------------------------------------

def test_r6_p8_the_loan_period_depends_on_the_category(library):
    for item in ("T1", "T2", "T3"):
        ok(library, "checkout", item, "M1")
    assert loan(library, "T1")["due"] == "2026-06-15"                  # hand: 14 days
    assert loan(library, "T2")["due"] == "2026-06-15"                  # garden: the standard period
    assert loan(library, "T3")["due"] == "2026-06-08"                  # power: 7 days


def test_r7_unknown_item_or_member_is_an_input_error(library):
    assert lend(library, "checkout", "T99", "M1").returncode == 2
    assert lend(library, "checkout", "T1", "M99").returncode == 2


def test_r8_an_item_on_loan_cannot_go_out_again(library):
    ok(library, "checkout", "T1", "M1")
    assert lend(library, "checkout", "T1", "M2").returncode == 3
    assert loan(library, "T1")["member"] == "M1"


def test_r9_p5_the_borrowing_limit_is_three(library):
    for item in ("T1", "T2", "T4"):
        ok(library, "checkout", item, "M1")
    assert lend(library, "checkout", "T6", "M1").returncode == 3
    assert member(library, "M1")["loans"] == 3
    assert "T6" in status(library)["available"]


# -- return and fees -------------------------------------------------------------------------------------

def test_r10_return_frees_the_item_and_an_unknown_return_is_an_input_error(library):
    ok(library, "checkout", "T1", "M1")
    ok(library, "return", "T1", now="2026-06-05")
    st = status(library, "2026-06-05")
    assert "T1" in st["available"] and all(l["item"] != "T1" for l in st["loans"])
    assert lend(library, "return", "T1", now="2026-06-05").returncode == 2


def test_r11_returning_on_the_due_date_costs_nothing(library):
    ok(library, "checkout", "T3", "M1")
    ok(library, "return", "T3", now="2026-06-08")
    assert member(library, "M1", "2026-06-08")["fees_cents"] == 0


def test_r12_a_late_return_costs_50_cents_a_day(library):
    ok(library, "checkout", "T3", "M1")                                 # due 2026-06-08
    ok(library, "return", "T3", now="2026-06-12")
    assert member(library, "M1", "2026-06-12")["fees_cents"] == 200


def test_r13_fees_add_up_over_returns(library):
    ok(library, "checkout", "T3", "M1")
    ok(library, "checkout", "T5", "M1")
    ok(library, "return", "T3", now="2026-06-11")
    ok(library, "return", "T5", now="2026-06-11")
    assert member(library, "M1", "2026-06-11")["fees_cents"] == 300


# -- renewal --------------------------------------------------------------------------------------------

def test_r14_a_renewal_adds_one_period(library):
    ok(library, "checkout", "T3", "M1")                                 # due 2026-06-08
    ok(library, "renew", "T3", now="2026-06-08")
    found = loan(library, "T3", "2026-06-08")
    assert found["due"] == "2026-06-15" and found["renewals"] == 1


def test_r15_p7_a_third_renewal_is_refused(library):
    ok(library, "checkout", "T3", "M1")
    ok(library, "renew", "T3", now="2026-06-08")
    ok(library, "renew", "T3", now="2026-06-15")
    assert lend(library, "renew", "T3", now="2026-06-22").returncode == 3
    assert loan(library, "T3", "2026-06-22")["renewals"] == 2


def test_r16_an_overdue_loan_cannot_be_renewed(library):
    ok(library, "checkout", "T3", "M1")
    assert lend(library, "renew", "T3", now="2026-06-10").returncode == 3


def test_r17_renewing_an_item_not_on_loan_is_an_input_error(library):
    assert lend(library, "renew", "T1").returncode == 2


# -- overdue ----------------------------------------------------------------------------------------------

def test_r18_p9_a_member_with_an_overdue_loan_is_blocked(library):
    ok(library, "checkout", "T3", "M1")                                 # due 2026-06-08
    assert lend(library, "checkout", "T1", "M1", now="2026-06-10").returncode == 3
    assert member(library, "M1", "2026-06-10")["blocked"] is True
    assert member(library, "M2", "2026-06-10")["blocked"] is False
    ok(library, "return", "T3", now="2026-06-10")                       # fee 100 cents, under $5
    assert member(library, "M1", "2026-06-10")["blocked"] is False
    ok(library, "checkout", "T1", "M1", now="2026-06-10")


def test_r19_status_shape_order_and_overdue_days(library):
    ok(library, "checkout", "T4", "M2")
    ok(library, "checkout", "T3", "M1")
    st = status(library, "2026-06-11")
    assert st["today"] == "2026-06-11"
    assert [l["item"] for l in st["loans"]] == ["T3", "T4"]
    t3, t4 = st["loans"]
    assert (t3["overdue"], t3["days_overdue"], t3["member"], t3["due"], t3["renewals"]) == (True, 3, "M1", "2026-06-08", 0)
    assert (t4["overdue"], t4["days_overdue"]) == (False, 0)
    assert [m["id"] for m in st["members"]] == ["M1", "M2"]
    assert {"id", "name", "loans", "fees_cents", "blocked"} <= set(st["members"][0])
    assert st["available"] == ["T1", "T2", "T5", "T6"]


def test_r24_lend_now_may_carry_a_time(library):
    ok(library, "checkout", "T3", "M1", now="2026-06-01T10:30:00")
    assert loan(library, "T3")["due"] == "2026-06-08"


# -- the report ---------------------------------------------------------------------------------------------

def read_report(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


COLUMNS = ["item", "title", "member", "due", "days_overdue"]


def test_r20_the_report_lists_only_overdue_loans(library, tmp_path):
    ok(library, "checkout", "T3", "M1")                                 # due 06-08 → overdue on 06-12
    ok(library, "checkout", "T1", "M2")                                 # due 06-15 → on time
    out = tmp_path / "report.csv"
    ok(library, "report", "--out", str(out), now="2026-06-12")
    header = next(csv.reader(out.open(encoding="utf-8")))
    assert [c for c in header if c in COLUMNS] == COLUMNS               # P3: an extra column is not judged here
    rows = read_report(out)
    assert [(r["item"], r["title"], r["member"], r["due"], r["days_overdue"]) for r in rows] == \
        [("T3", "Drill", "M1", "2026-06-08", "4")]


def test_r21_p6_the_most_overdue_first_then_by_item(library, tmp_path):
    ok(library, "checkout", "T5", "M1")                                 # power, due 06-08
    ok(library, "checkout", "T3", "M2")                                 # power, due 06-08
    ok(library, "checkout", "T1", "M2", now="2026-05-20")               # hand, due 06-03
    out = tmp_path / "report.csv"
    ok(library, "report", "--out", str(out), now="2026-06-12")
    assert [r["item"] for r in read_report(out)] == ["T1", "T3", "T5"]


def test_r22_an_empty_report_is_a_header_and_replaces_the_file(library, tmp_path):
    out = tmp_path / "report.csv"
    out.write_text("old content\n", encoding="utf-8")
    ok(library, "report", "--out", str(out))
    lines = out.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1 and [c for c in next(csv.reader(lines)) if c in COLUMNS] == COLUMNS
