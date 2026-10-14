# Implementation notes

## What was built
- Python 3.12 package `lend` (`src/lend/cli.py`), installed with `pip install -e .`, no runtime dependencies (stdlib only; pytest for tests).
- Commands: `init`, `member add`, `item add`, `checkout`, `renew`, `return`, `status [--json]`, `report --out FILE`, with exit codes 0–4 as specified.
- Store: `.lend/data.json` (written atomically via temp file + rename).
- Rules: limit 3, 14-day standard / 7-day power loans, max 2 renewals, no renewal when overdue, overdue from the day after due, overdue members blocked from checkout, fee 50¢/day capped at 1000¢ recorded at return, `LEND_NOW` support.
- Report: CSV with columns item, title, member, due, days_overdue, email; sorted by days overdue desc then item id; header only when empty.
- Tests: `tests/test_cli.py` (run with `pytest`).

## Not implemented / deviations
- Blocking checkout for fees over $5 (`ops/notes.md`): not implemented because `loans/spec.md` says fees never stop borrowing (see OPEN_QUESTIONS #6).
- The 18:00 overdue rule and the "report never contains email" rule: dropped per `DECISIONS.md`.
- Limit of 5 and the $15 cap: superseded by the changelog and `fees.md`.
- No payment command (out of scope per `fees.md`). Plain-text `status` format is my own, as the spec defines only `--json`.
