# Implementation notes

## What was built

`lend` is a command-line lending desk for a tool library. It runs from one folder on one laptop, with
no server. It is a Python 3.12 package with no runtime dependencies (standard library only). The test
suite uses `pytest`, declared as the `test` extra.

Commands:

| Command | Behaviour |
| --- | --- |
| `lend init` | Creates `.lend/` here. Exits 2 and changes nothing if it already exists. |
| `lend member add ID --name NAME --email EMAIL` | Registers a member. Email is required. |
| `lend item add ID --title TITLE [--category hand\|power\|garden]` | Registers an item. Category defaults to `hand`. |
| `lend checkout ITEM MEMBER` | Lends an item. Due today + 14 days, or + 7 days for power tools. |
| `lend renew ITEM` | Adds one loan period to the current due date. At most two renewals; overdue loans cannot be renewed. |
| `lend return ITEM` | Ends the loan. Adds a late fee of 50 cents per day late, capped at $10.00 per loan. |
| `lend status --json` | One JSON object: `today`, `loans`, `members` (with `fees_cents`, `blocked`), `available`. |
| `lend report --out FILE` | Writes the overdue CSV, replacing FILE. Header only when nothing is overdue. |

Exit codes follow the table in pack 12: 0 done, 1 usage, 2 input, 3 refused by a lending rule (the rule
is named in the message), 4 no store here.

Layout:

- `pyproject.toml`: package metadata, the `lend` console script (`lend.cli:main`), and the `test` extra.
- `src/lend/cli.py`: argument parsing, dispatch, and mapping of failures to exit codes.
- `src/lend/lending.py`: the lending rules (members, items, checkout, renewal, return, status, report
  rows). It does no file I/O.
- `src/lend/store.py`: the `.lend/store.json` store, read and written atomically.
- `src/lend/clock.py`: "today" and the moment used for the report cutoff, read from `LEND_NOW`.
- `src/lend/report.py`: the CSV report.
- `src/lend/errors.py`: exit codes and the error type.
- `tests/test_lend.py`: 51 tests, named after the spec node ids they check.
- `OPEN_QUESTIONS.md`: every contradiction or gap, with the choice made.

Verification: `pip install -e ".[test]"` succeeded on Python 3.12.15. `python3 -m pytest` gives
51 passed. `lend` was also run by hand in a scratch folder: checkout, a late return, the status JSON,
and the report output matched the spec.

## Requirement accounting

All 124 checklist ids (N-000001 to N-000124) are accounted for. Each one is marked in the code with a
`# spec: N-…` comment where it is satisfied. 89 ids have a test named after them. The other 35 are
either exercised by a test named for a related id (for example, N-000002 is checked by the limit test,
named for N-000001 and N-000053), or are rationale and process statements with no code of their own.

### Not implemented, with reasons

| Id | Requirement | Reason |
| --- | --- | --- |
| N-000054 | Up to 5 items on loan (MAY) | Superseded by N-000001 and N-000002 (the 2026-05-10 changelog): the limit is 3. Implemented as 3. See OPEN_QUESTIONS.md item 3. |
| N-000084 | Each report row should carry the member's contact email (SHOULD) | Conflicts with N-000109 (MUST NOT: the report never carries a member's email) and with the fixed five-column report (N-000100 to N-000105). The export marks this as unsettled (CF-000004, CF-000009). The report keeps the five columns. See OPEN_QUESTIONS.md item 2. |
| N-000086 | The tool does not go out while fees are over $5.00 (MUST NOT) | Conflicts with N-000057 (MUST NOT: late fees never stop borrowing) and N-000058 (the tool goes out). The loans spec wins. The reminder in N-000085 is implemented: the volunteer is asked to ask the member to settle. See OPEN_QUESTIONS.md item 5. |
| N-000081 | The list is printed on the first Saturday of the month (MUST) | A counter practice, not software behaviour. `lend report` produces the list on demand. Nothing schedules or prints it. |
| N-000020 | Paying fees is handled by the treasurer outside `lend` (MUST) | A process statement with nothing to build. It is satisfied by there being no payment command, which N-000021 requires and a test checks. |

### Implemented by absence or as design (no separate code)

- N-000078: no exceptions at the counter. There is no override flag.
- N-000111: the design decision to replace the spreadsheet with this tool.
- N-000123: out of scope. There are no reservations, payments, reminders or server.
- N-000124: runs on one laptop from one folder.
- N-000006: the glossary terms are used as defined.

## Not verified

- N-000121 (status should be fast, SHOULD): the status command does one JSON read, but its speed was
  not measured.
- Every command that changes the store saves it at once. Two `lend` processes writing at the same
  moment are not guarded against. The spec does not ask for concurrency control.

## Other choices outside the spec

- The store keeps open loans only. Returned loans are removed and not kept as history. The spec asks for
  no history.
- A damaged `store.json` exits 2 with a message. The spec gives no code for this case.
- The report file is replaced atomically through a temporary file next to it.
- Titles and names may not contain line breaks, so each stays on one CSV line.
- Titles are written as-is. A title beginning with `=` is not escaped for spreadsheets. Titles are typed
  by volunteers, and the spec does not ask for this protection.
