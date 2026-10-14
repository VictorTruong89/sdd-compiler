# Open questions

1. **Borrowing limit.** `loans/spec.md` says 5; `CHANGELOG.md` (2026-05-10) says 3 and calls itself the current rule. Chose **3**.
2. **Power-tool loan period.** `loans/spec.md` says only a 14-day standard period; `CHANGELOG.md` (2026-03-02) and `ops/notes.md` say 7 days for power tools. Chose **7** for `power`; 14 for hand and garden. Renewals add the category's period.
3. **When a loan is overdue.** `reports/spec.md` says from 18:00 on the due date; `loans/spec.md` says the day after. `DECISIONS.md` picks the day after. Followed that; `days_overdue` = today − due.
4. **Email in the report.** `reports/spec.md` says never; `ops/notes.md` says a sixth column. `DECISIONS.md` picks the email column named `email`. Followed that.
5. **Report order.** `CHANGELOG.md` and `ops/notes.md`: most overdue first, ties by item id. `reports/spec.md` is consistent with this. The changelog says ties used to be by member id; used item id.
6. **Fees over $5 block borrowing.** `ops/notes.md` says the tool does not go out; `loans/spec.md` and `glossary.md` say fees never stop borrowing, and "blocked" means overdue only. No decision covers this. Chose **`loans/spec.md`**: fees never block; checkout prints a reminder when fees are owed.
7. **Fee cap.** `vision.md` says nobody owes more than $15 for one late tool; `fees.md` caps at $10.00. Chose **$10** (the specific rule; it also satisfies the vision's bound).
8. **Missing `--name`/`--email`/`--title`.** "Missing argument" is exit 1 but "missing value" is exit 2. Chose: missing positional args or a missing command = 1; missing option values (`--name`, `--email`, `--title`) = 2. `report` without `--out` = 1.
9. **Email validity.** Spec only requires one. Chose: must contain `@` with text on both sides, else exit 2.
10. **Unknown ids on return/renew.** Unknown item is exit 2 (same as "not on loan").
11. **Check order at checkout.** Unknown ids (2), item on loan (3), member blocked (3), limit (3).
12. **`lend init` on existing store** exits 2 with no change; "no store" is detected by missing `.lend/` directory.
13. **LEND_NOW** accepts ISO date or date-time (date part used, no timezone conversion); an unparseable value is exit 2.
14. **Plain `lend status`** (without `--json`) is not defined; I print a short human-readable summary.
15. **Report output.** Written with `\n` line endings; the CSV email column is quoted only when needed.
