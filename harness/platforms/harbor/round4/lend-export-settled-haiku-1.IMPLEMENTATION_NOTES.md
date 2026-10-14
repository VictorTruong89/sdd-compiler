# Implementation notes

## What was built

`lend` is a Python 3.12 command-line tool for the Eastside Tool Library counter. It keeps members, items
and loans in a `.lend/` folder in the current directory. Standard library only at run time. `pytest` is the
only test dependency.

| Command | Behaviour |
| --- | --- |
| `lend init` | Create `.lend/`. Exit 2, nothing changed, if it already exists. |
| `lend member add ID --name NAME --email EMAIL` | Register a member. Email required (exit 2 if missing). |
| `lend item add ID --title TITLE [--category hand\|power\|garden]` | Register an item; default `hand`. |
| `lend checkout ITEM MEMBER` | Lend an item. Due = today + 14 days (power tools 7). Refused (exit 3) if the item is on loan, the member has an overdue loan, or the member is at the 3-item limit. |
| `lend return ITEM` | End the loan. A late return adds 50 cents a day, capped at $10.00 per loan, to the member's balance. |
| `lend renew ITEM` | Add one loan period (of the item's category) to the current due date. At most 2 renewals; refused (exit 3) when overdue or when the 2 renewals are used. |
| `lend status --json` | One JSON object: `today`, `loans`, `members` (with `fees_cents`, `blocked`), `available`. |
| `lend report --out FILE` | Write the overdue CSV for the board, most overdue first, then item id. Header only when nothing is overdue. |

Exit codes: 0 done, 1 usage error (unknown command or missing argument), 2 input error, 3 refused by a
lending rule (the message names the rule), 4 no store in this folder (says to run `lend init`).

`LEND_NOW` (ISO-8601 date or date-time) replaces the system date when set.

### Layout

```
pyproject.toml                 package metadata; `lend = "lend.cli:main"`; pytest in the `test` extra
src/lend/cli.py                argparse wiring, command handlers, exit-code mapping
src/lend/store.py              .lend/store.json persistence and the lending operations
src/lend/rules.py              constants (limit, periods, fee) and pure date and money functions
src/lend/report.py             overdue report CSV writer
src/lend/errors.py             LendError classes carrying the exit codes
tests/conftest.py              fixture that runs `lend` in a temp folder with a fixed LEND_NOW
tests/test_rules.py            fee, period, overdue-day rules
tests/test_cli.py              command behaviour, exit codes, status JSON
tests/test_report.py           report contents, order, quoting, overwrite
tests/test_spec_ids.py         tests for ids not covered by the others
OPEN_QUESTIONS.md              every contradiction and gap, and the choice made
```

Code and tests carry `# spec: N-…` markers. Test names contain the node id (for example
`test_N_000013_…`). The spec has no acceptance criteria (every pack says `AC labels: none`), so node ids are
the test names.

## How it was verified

- `python3.12 -m venv .venv && .venv/bin/pip install -e '.[test]'` installs the `lend` command.
- `.venv/bin/python -m pytest -q` → **77 passed**.
- Manual end-to-end run in a temp folder (init, add, checkout, late return, status, report, usage and
  no-store errors), with the exit codes checked.

## Requirements not implemented, and why

Every checklist id (124) is accounted for below. "Implemented" means the behaviour exists and is tested by the
test named. Five ids are not implemented, and one is partial.

| Id | Requirement | Status and reason |
| --- | --- | --- |
| N-000054 | MAY: a member may have up to 5 items on loan | **Not implemented as written.** The 2026-05-10 changelog lowers the limit to 3 and says it is the current rule (N-000001, N-000002). The code uses 3. See OPEN_QUESTIONS #1. |
| N-000081 | MUST: the board's list is printed on the first Saturday of the month | **Not implemented.** Printing is a human counter routine, not something the tool can do. The tool writes the file on demand (`lend report`). |
| N-000086 | MUST NOT: the tool does not go out until a patron over $5 settles | **Not implemented.** Contradicts the loan spec (N-000057, N-000058), which says fees never stop borrowing. The tool prints a reminder and a request to settle instead. See OPEN_QUESTIONS #4. |
| N-000099 | MUST: a loan counts as overdue from 18:00 on its due date (for the report) | **Not implemented.** Settled against it: overdue starts the day after the due date (loan spec N-000067, N-000068). Verdict recorded in the export (CF-000001, CF-000010). See OPEN_QUESTIONS #2. |
| N-000109 | MUST NOT: the report never contains a member's email address or name | **Email not implemented; the name is never written.** Settled against it: the report carries the member's email in a sixth column (CF-000004, CF-000009, ops N-000084). See OPEN_QUESTIONS #3. |
| N-000122 | MUST: a monthly list of overdue loans for the board | **Partial.** The list is produced by `lend report`. The monthly schedule is an operational routine and is not built. |

Requirements that are not a separate tool behaviour (met by the design or by leaving something out):

- N-000006 (glossary definitions are binding): followed as the definitions of the code, not a separate feature.
- N-000020, N-000021 (paying fees is outside `lend`; there is no pay command): met by leaving out any pay command.
  `test_N_000021_no_command_to_pay_fees` checks that.
- N-000090 (MAY: the board can read the report without access to the counter laptop): the report is a plain CSV
  file that does not depend on the laptop once written.
- N-000121 (SHOULD: status is fast): status reads one local JSON file and does no network or server work. No timing
  test was written.

Requirements that are implemented but with a choice recorded in OPEN_QUESTIONS.md, not a silent one:

- Renewal due dates follow the rule text (current due date + period), not the worked-example table
  (OPEN_QUESTIONS #5).
- Missing `--email` exits 2 (input error), while a missing `--name`, `--title` or positional id exits 1 (OPEN_QUESTIONS #7).
- The report adds an `email` column (OPEN_QUESTIONS #3).

## Traceability (all 124 checklist ids)

| Pack / source | Ids | Status and where |
| --- | --- | --- |
| 00 vision | N-000111 | Implemented: the tool itself (`cli.py`). |
| 00 vision | N-000112, N-000124 | Implemented: one local folder (`store.py`); `test_N_000026…`, `test_N_000124_…`. |
| 00 vision | N-000113, N-000115 | Implemented: `status --json` and report; `test_N_000113_N_000115_…`. |
| 00 vision | N-000114 | Implemented: one loan per item; `test_N_000114_…`. |
| 00 vision | N-000116, N-000117 | Implemented: same period per category, 14 days; `test_N_000116_…`, `test_N_000055_…`. |
| 00 vision | N-000118, N-000119 | Implemented: $10 cap, below $15; `test_N_000015_…`, `test_N_000118_N_000119_…`. |
| 00 vision | N-000120 | Implemented: overdue member refused; `test_N_000009_N_000120_…`. |
| 00 vision | N-000121 | Implemented; no timing test (see above). |
| 00 vision | N-000122 | Partial: on-demand report; schedule not built (see above). |
| 00 vision | N-000123 | Implemented by absence: no reservations, payments, reminders or server. `test_N_000117_N_000124_…`. |
| 02 changelog 05-10 | N-000001, N-000002 | Implemented: limit 3; `test_N_000053_N_000054_…`, `test_N_000002_…`. |
| 02 changelog 05-10 | N-000003 | Implemented: equally overdue by item id; `test_N_000108_…`. |
| 03 changelog 03-02 | N-000004 | Implemented: power tools 7 days; `test_N_000075_…`. |
| 03 changelog 03-02 | N-000005 | Implemented: email required; `test_N_000005_…`, `test_N_000042_…`. |
| 05 fees | N-000011, N-000012 | Implemented: small and capped; `test_N_000013_…`, `test_N_000015_…`. |
| 06 fees, computed | N-000013, N-000014 | Implemented: 50 cents a day, nothing if on time; `test_N_000013_…`, `test_N_000014_…`. |
| 06 fees, computed | N-000015 | Implemented: $10 cap per loan; `test_N_000015_…`. |
| 06 fees, computed | N-000016 | Implemented: whole cents; `test_N_000016_…`. |
| 06 fees, computed | N-000017, N-000018 | Implemented: balance sum, `fees_cents` in status; `test_N_000010_N_000017_N_000018_…`. |
| 07 fees, not | N-000019 | Implemented: fee on return; `test_N_000066_N_000019_…`. |
| 07 fees, not | N-000020 | Implemented by absence (no pay command). |
| 07 fees, not | N-000021 | Implemented: no pay command; `test_N_000021_…`. |
| 07 fees, not | N-000022, N-000023 | Implemented: renewal costs nothing and keeps fees; `test_N_000022_N_000023_…`. |
| 08 fees, board | N-000024 | Implemented: members with balances in status; `test_N_000024_…`. |
| 08 fees, board | N-000025 | Implemented: the report has no money; `test_N_000025_…`. |
| 09 ops | N-000075 | Implemented: power 7 days; `test_N_000075_…`. |
| 09 ops | N-000076 | Implemented: hand and garden unaffected; `test_N_000076_…`, `test_N_000116_…`. |
| 09 ops | N-000077 | Implemented: several items up to the limit; `test_N_000053_N_000054_…`. |
| 09 ops | N-000078 | Implemented: no override; `test_N_000078_…`. |
| 09 ops | N-000079 | Implemented: two renewals; `test_N_000061_N_000079_…`. |
| 09 ops | N-000080 | Implemented: third renewal refused, return first; `test_N_000080_…`. |
| 09 ops | N-000081 | **Not implemented** (see above). |
| 09 ops | N-000082 | Implemented: most overdue first; `test_N_000107_…`. |
| 09 ops | N-000083 | Implemented: equal overdue by item id; `test_N_000108_…`. |
| 09 ops | N-000084 | Implemented: email in the report, column six; `test_N_000109_N_000084_…`. |
| 09 ops | N-000085 | Implemented as a reminder, not a refusal; `test_N_000085_…`. |
| 09 ops | N-000086 | **Not implemented** (see above). |
| 09 ops | N-000087, N-000088 | Implemented: `LEND_NOW`; `test_N_000087_N_000088_…`, `test_N_000088_…`. |
| 10–11 loans | (no nodes) | Context only. |
| 12 store and CLI | N-000026, N-000027 | Implemented: `lend init`; cwd only; `test_N_000026_…`, `test_N_000027_…`. |
| 12 store and CLI | N-000028 | Implemented: `.lend/store.json` layout (MAY). |
| 12 store and CLI | N-000029, N-000030 | Implemented: init twice, exit 2, nothing changed; `test_N_000029_N_000030_…`. |
| 12 store and CLI | N-000031, N-000032 | Implemented: exit 4 and "run lend init"; `test_N_000031_N_000032_…`. |
| 12 store and CLI | N-000033 | Implemented: exit codes; all command tests. |
| 12 store and CLI | N-000034 | Implemented: exit 0; `test_N_000033_N_000034_…`. |
| 12 store and CLI | N-000035 | Implemented: exit 1; `test_N_000035_…`. |
| 12 store and CLI | N-000036 | Implemented: exit 2; `test_N_000029_…`, `test_N_000042_…`, `test_N_000065_…`, and others. |
| 12 store and CLI | N-000037 | Implemented: exit 3 with rule named; `test_N_000052_…`, `test_N_000061_N_000079_…`. |
| 12 store and CLI | N-000038 | Implemented: exit 4; `test_N_000031_…`. |
| 12 store and CLI | N-000039 | Implemented: today from `LEND_NOW` or the system date; `test_N_000087_N_000088_…`. |
| 13 members and items | N-000040, N-000041 | Implemented: member add with email; `test_N_000040_N_000041_…`. |
| 13 members and items | N-000042 | Implemented: missing email exits 2; `test_N_000042_…`. |
| 13 members and items | N-000043, N-000044 | Implemented: duplicate member id exits 2; `test_N_000043_N_000044_…`. |
| 13 members and items | N-000045 | Implemented: item add; `test_N_000045_…`. |
| 13 members and items | N-000046 | Implemented: category check; `test_N_000046_…`. |
| 13 members and items | N-000047 | Implemented: default `hand`; `test_N_000045_…`. |
| 13 members and items | N-000048 | Implemented: other categories exit 2; `test_N_000046_…`. |
| 13 members and items | N-000049 | Implemented: duplicate item id exits 2; `test_N_000049_…`. |
| 14 checkout | N-000050 | Implemented: checkout; `test_N_000055_…`, `test_N_000114_…`. |
| 14 checkout | N-000051 | Implemented: both ids must exist; `test_N_000050_N_000051_…`. |
| 14 checkout | N-000052 | Implemented: item on loan refused; `test_N_000052_…`. |
| 14 checkout | N-000053 | Implemented: member at limit refused; `test_N_000053_N_000054_…`. |
| 14 checkout | N-000054 | **Not implemented as written** (limit 3, not 5; see above). |
| 14 checkout | N-000055, N-000056 | Implemented: due = today + period; `test_N_000055_N_000056_…`. |
| 14 checkout | N-000057, N-000058 | Implemented: fees do not stop borrowing; reminder printed; `test_N_000057_N_000058_…`. |
| 15 renewal | N-000059 | Implemented: renew; `test_N_000059_N_000060_…`. |
| 15 renewal | N-000060 | Implemented: current due + category period; `test_N_000059_N_000060_…`, `test_N_000060_…`. |
| 15 renewal | N-000061 | Implemented: at most two; `test_N_000061_N_000079_…`. |
| 15 renewal | N-000062 | Implemented: overdue not renewable; `test_N_000062_…`. |
| 15 renewal | N-000063 | Implemented: not on loan exits 2; `test_N_000063_…`. |
| 16 return | N-000064 | Implemented: return frees the item; `test_N_000064_…`. |
| 16 return | N-000065 | Implemented: not on loan exits 2; `test_N_000065_…`. |
| 16 return | N-000066 | Implemented: late return adds fee; `test_N_000066_N_000019_…`. |
| 16 return | N-000067, N-000068 | Implemented: overdue from the day after; `test_N_000067_N_000068_…` (rules), `test_N_000097_N_000098_…`. |
| 17 status | N-000069 | Implemented: `status --json`; `test_N_000069_…`. |
| 17 status | N-000070 | Implemented: JSON shape; `test_N_000070_…`. |
| 17 status | N-000071 | Implemented: loans sorted by item id; `test_N_000070_…`. |
| 17 status | N-000072 | Implemented: members sorted by id; `test_N_000072_…`. |
| 17 status | N-000073 | Implemented: members' count, fees, blocked; `test_N_000070_…`. |
| 17 status | N-000074 | Implemented: available sorted; `test_N_000070_…`. |
| 18 glossary | N-000006 | Followed as the code's definitions (see above). |
| 18 glossary | N-000007 | Implemented: exactly one category; `test_N_000046_…`. |
| 18 glossary | N-000008 | Implemented: garden uses the standard period; `test_N_000116_…`. |
| 18 glossary | N-000009 | Implemented: blocked member; `test_N_000009_N_000120_…`. |
| 18 glossary | N-000010 | Implemented: cents; `test_N_000010_N_000017_N_000018_…`. |
| 20 report purpose | N-000089 | Implemented: CSV; `test_N_000105_…`, `test_N_000089_…`. |
| 20 report purpose | N-000090 | Met by design (plain CSV file). |
| 21 report command | N-000091, N-000092 | Implemented: `--out` writes and replaces; `test_N_000091_N_000092_…`. |
| 21 report command | N-000093 | Implemented: exit 0; `test_N_000093_…`. |
| 21 report command | N-000094, N-000095 | Implemented: header only when nothing overdue; `test_N_000094_N_000095_…`. |
| 22 report contents | N-000096 | Implemented: one row per overdue loan; `test_N_000096_to_N_000104_…`. |
| 22 report contents | N-000097, N-000098 | Implemented: on-time and returned loans excluded; `test_N_000097_N_000098_…`. |
| 22 report contents | N-000099 | **Not implemented** (see above). |
| 22 report contents | N-000100 to N-000104 | Implemented: columns and values; `test_N_000096_to_N_000104_…`. |
| 22 report contents | N-000105 | Implemented: exact header; `test_N_000105_…`. |
| 22 report contents | N-000106 | Implemented: CSV quoting; `test_N_000106_…`. |
| 23 report order | N-000107 | Implemented: most overdue first; `test_N_000107_…`. |
| 23 report order | N-000108 | Implemented: item-id tie-break; `test_N_000108_…`. |
| 24 privacy | N-000109 | **Not implemented as written** (email carried, per verdict; see above). |
| 24 privacy | N-000110 | Implemented: email required, so kept on file; `test_N_000110_…`. |

The checklist also contains N-000001 to N-000124 in full. Nothing is listed as "not done" without one of the
reasons above.
