# Implementation notes

## What was built

A Python 3.12 package, `lend`, installed with `pip install -e .` (declared in `pyproject.toml`; the
console script is `lend = lend.cli:main`). It uses only the standard library at runtime. `pytest` is an
optional `test` extra.

Layout:

- `src/lend/cli.py`: argument parsing (argparse), dispatch, and exit codes.
- `src/lend/commands.py`: lending operations on the store (members, items, checkout, renewal, return,
  status, overdue rows, and the CSV report).
- `src/lend/rules.py`: loan periods, borrowing limit, renewal limit, late fees, and the overdue rule.
- `src/lend/store.py`: the `.lend/` folder and its JSON data file (written atomically).
- `src/lend/clock.py`: "today", from the system date or `LEND_NOW`.
- `src/lend/errors.py`: the exit codes and the error type.
- `tests/test_lend.py`: 35 tests covering the commands, rules, fees, status and report.

Run the tests with `python3 -m pytest` (35 pass).

Commands implemented, all against the `.lend/` folder of the current directory:

- `lend init`
- `lend member add ID --name NAME --email EMAIL`
- `lend item add ID --title TITLE [--category hand|power|garden]`
- `lend checkout ITEM MEMBER`
- `lend renew ITEM`
- `lend return ITEM`
- `lend status --json`
- `lend report --out FILE`

Behaviour that follows the spec:

- Exit codes 0–4 as the table in `loans/spec.md`.
- Loan periods: hand and garden 14 days, power 7 days.
- Borrowing limit 3, renewals at most 2, no renewal of an overdue loan.
- Overdue from the day after the due date. Members with an overdue loan are blocked from checkout.
- Late fee of 50 cents per day late, capped at $10.00 per loan, recorded in cents at return.
- Late fees do not block checkout. A reminder is printed when the member owes money.
- The status JSON has the keys and sort order in `loans/spec.md`.
- The report has one row per overdue loan, most overdue first, then by item id. Columns are
  `item,title,member,due,days_overdue,email`, and a header row is always written.

Every interpretation I had to choose is listed in `OPEN_QUESTIONS.md`.

## Requirements not implemented, and why

1. **Borrowing limit of 5** (`loans/spec.md`). Replaced by 3, per the 2026-05-10 changelog. See
   `OPEN_QUESTIONS.md` item 1.
2. **18:00 overdue rule for the report** (`reports/spec.md`). Dropped per `spec/DECISIONS.md`
   (2026-10-13).
3. **"Report never contains an email"** (`reports/spec.md`). Dropped per `spec/DECISIONS.md`
   (2026-10-13). The email column is included. The member's name is still left out.
4. **Renewal worked example's dates** (`loans/spec.md`: 24 June and 4 July). Not reproduced. The
   prose rule (add the period to the current due date) was implemented, giving 29 June and 13 July.
   See `OPEN_QUESTIONS.md` item 4.
5. **$5.00 fee block at checkout** (`ops/notes.md`). Not implemented. It contradicts
   `loans/spec.md`, which says late fees never stop a member from borrowing. See `OPEN_QUESTIONS.md`
   item 5.
6. **`lend status` in human-readable form.** Not implemented. The spec describes only `--json`, so
   `lend status` without it is a usage error.
7. **Out of scope, as the vision states:** online reservations, payments, email reminders, and any
   server. No payment command exists; fees are only recorded and shown.
8. **Commands not in the spec** (for example listing or removing members and items, or viewing a
   member's loans). Not implemented.
9. **"Status should be fast."** No timing test was written. The store is a single JSON file read
   once per command, and no performance was measured.
10. **Non-functional and operational requirements** (the first Saturday printing, the board's monthly
    review): these are processes, not behaviour of the tool. The report is produced on demand.

## Not verified

- `pip install -e '.[test]'` was run in this environment, and `lend` resolves on the PATH after the
  final edits. An install into a clean virtual environment was not tested.
- The tests run under Python 3.12.15 in this environment.
