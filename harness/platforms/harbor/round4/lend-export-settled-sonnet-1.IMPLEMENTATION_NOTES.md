# Implementation notes

Built the `lend` CLI (`src/lend/cli.py`, no third-party dependencies, Python 3.12). Data lives in `.lend/data.json` (written atomically). Commands: `init`, `member add`, `item add`, `checkout`, `renew`, `return`, `status --json`, `report --out`. Requirement ids are marked with `# spec: N-…` comments. Tests are in `tests/test_lend.py`; run with `pytest`.

All ids in CHECKLIST.md are covered, with the resolutions listed in OPEN_QUESTIONS.md. Not implemented, with reasons:
- N-000085 / N-000086 (block borrowing when fees exceed $5): contradicts N-000057/N-000058; the latter was chosen.
- N-000099 (overdue from 18:00 on the due date) and N-000109 (report never contains email): dropped per the owner verdicts in the spec (CF-000001/10, CF-000004/09).
- Borrowing limit of 5 (N-000054) replaced by 3 per N-000001/N-000002.
- N-000081 (printing the list on the first Saturday), N-000020 (treasurer handles payment): process statements, no code. No payment command exists (N-000021).
- N-000117/N-000090/N-000121 (qualitative: loan period length, usable without the laptop, fast status): satisfied by design (single JSON read), not tested for speed.
