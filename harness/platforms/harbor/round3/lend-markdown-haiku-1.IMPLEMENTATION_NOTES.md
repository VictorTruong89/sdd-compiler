# Implementation notes

## What was built

`lend`, a command-line tool for the Eastside Tool Library, following `spec/`. It keeps members,
items and loans in a `.lend/` folder in the current directory.

Install and run:

```
pip install -e ".[test]"   # editable install; the test extra adds pytest
lend init
lend member add M1 --name Ana --email ana@example.org
lend item add T1 --title "Hand saw" [--category hand|power|garden]
lend checkout T1 M1
lend renew T1
lend return T1
lend status [--json]
lend report --out board.csv
```

- **Python:** 3.12. The package uses only the standard library at runtime. The only declared
  dependency is `pytest`, in the `test` extra.
- **Layout:** `pyproject.toml`; `src/lend/` with `cli.py` (argument parsing and exit codes),
  `library.py` (the lending rules, in memory), `store.py` (the `.lend/store.json` file, written
  atomically), `status.py`, `report.py`, `clock.py` (the system date or `LEND_NOW`) and `errors.py`;
  `tests/` with `test_rules.py` and `test_cli.py`.
- **Store:** one JSON file, `.lend/store.json`, with a `format` field set to 1.
- **Tests:** 33 tests, all passing (`python3 -m pytest`). They cover the fee table and the other
  worked examples in `spec/`, the lending rules, the exit codes, `status --json`, the report
  (ordering, columns, privacy, the 18:00 cutoff, header-only output), and `LEND_NOW`. I also ran the
  installed `lend` command by hand in a scratch folder.

The specification choices are listed in `OPEN_QUESTIONS.md`. Where the spec contradicts itself, I
picked the value and recorded the reason there.

## Requirements not implemented

These are the requirements I left out, with the reason for each.

| Requirement | Where | Reason |
|---|---|---|
| Members with more than $5.00 in late fees cannot borrow until they settle | `ops/notes.md` ("Fees over five dollars") | Contradicts `loans/spec.md`, which says late fees never stop a member from borrowing. The loans spec was followed. See OPEN_QUESTIONS 6. |
| Each report row carries the member's email address | `ops/notes.md` ("The board's overdue list") | Contradicts `reports/spec.md`, which says the report never contains an email or a name. The report spec was followed. See OPEN_QUESTIONS 5. |
| Renewal dates as printed in the worked example (24 June, 4 July) | `loans/spec.md` (Renewal) | Contradicts the rule stated in the same section (extend the current due date). The rule was followed. See OPEN_QUESTIONS 2. |
| Paying late fees | `loans/fees.md` | The spec says there is no command for it in this version, and that the treasurer handles payment outside `lend`. |
| Online reservations, payments, email reminders, any server | `vision.md` | Out of scope for the first version. |
| Commands to list, edit or remove members and items | Not in `spec/` | The spec defines only `init`, `member add`, `item add`, `checkout`, `renew`, `return`, `status` and `report`. Adding more would go beyond the spec. As a result, a mistaken member or item can't be corrected or removed without editing `.lend/store.json` by hand. |
| Automatic migration between store formats | Not in `spec/` | Only format 1 exists. A store with any other `format` value is refused with exit 2. |

## Not verified

- **"Status should be fast."** I did not measure timing. Each command reads and rewrites the whole
  JSON store, which is fine for a few thousand records but was not benchmarked.
- **Concurrent use.** Two `lend` processes writing at the same moment can overwrite each other's
  changes, since there is no locking. The spec describes one laptop and one folder, and says nothing
  about this, so I did not add locking.
- **Windows.** Only Linux was tested. The atomic replace uses `os.replace`, which should work on
  Windows, but that is unchecked.
