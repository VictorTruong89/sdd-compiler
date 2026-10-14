# Open questions

1. **Borrowing limit** — checkout spec (pack 14, N-000054) says 5; changelog 2026-05-10 (N-000001/N-000002) says 3 and calls itself the current rule. Chose **3**.
2. **Overdue: day after due date vs 18:00 on due date** (CF-000001, CF-000010; N-000067/N-000068 vs N-000099). Chose: everywhere except the report (status, blocking, renewal, fees, `days_overdue` in status) a loan is overdue from the day after its due date; the *report* (which the spec scopes with "for the purpose of the report") includes a loan from 18:00 on its due date. With `LEND_NOW` as a date only (midnight) or the date part, the due date itself is before 18:00, so not listed. Report `days_overdue` is whole days today − due (0 on the due date after 18:00).
3. **Report email column** (CF-000004, CF-000009; N-000084 vs N-000105/N-000109). Chose the privacy rule: no email or name; exactly the five columns.
4. **Fees over $5 stop lending?** Counter notes (N-000085/N-000086) say the tool does not go out until settled; checkout spec (N-000057/N-000058) says fees never block, only a reminder; and no pay command exists. Chose: never block; print a reminder on checkout when a balance is owed.
5. **Renewal worked example** (pack 15) shows 15 June → 24 June after renewing on 10 June, which is not +14 days from the current due date (would be 29 June). Followed the prose ("add one period to the current due date"): 29 June, then 13 July.
6. **Missing `--name`/`--email`/`--title`**: "missing argument" is exit 1 but "member added without email" is an input error (2). Chose 2 for these option values; exit 1 for missing positionals/commands/`--out`.
7. **Blocked member checkout** (glossary N-000009): refused with exit 3 naming the rule. Check order: unknown ids (2), item on loan (3), blocked (3), limit (3).
8. **Renewal limit / overdue renewal** are refusals by lending rule (exit 3); renewing an item not on loan is exit 2.
9. **`lend status`** without `--json` is a usage error (exit 1). `lend report` without `--out` exits 1.
10. **N-000081 (print on the first Saturday)** is a human process; not implemented.
11. **Timezone in `LEND_NOW`**: offsets are dropped, the wall-clock value is used. Invalid value: exit 2.
