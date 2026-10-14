# Implementation notes

Built `lend` (package in `src/lend/cli.py`, installed via `pip install -e .`, no runtime dependencies): `init`, `member add`, `item add`, `checkout`, `renew`, `return`, `status --json`, `report --out`. Data is a single JSON file at `.lend/data.json`, written atomically. Tests: `tests/test_cli.py` (pytest, 5 passing).

Rules: limit 3, 14/7-day periods, max two renewals from the current due date, 50c/day late fee capped at 1000c, overdue members blocked, exit codes 0–4 as specified.

Choices where the spec conflicts are in `OPEN_QUESTIONS.md`.

Not implemented:
- Fee-based borrowing block (>$5, `ops/notes.md`): contradicts the loan spec.
- Email column in the report: contradicts the privacy section.
- No reminder at checkout about owed fees ("reminded at the counter"): no output format was specified.
