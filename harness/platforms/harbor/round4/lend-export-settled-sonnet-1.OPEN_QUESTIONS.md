# Open questions

1. **Borrowing limit: 5 vs 3.** loans/spec.md (N-000054) says 5; CHANGELOG 2026-05-10 (N-000001/N-000002) says 3 and calls itself the current rule. Chose **3**.
2. **Overdue at 18:00 vs the day after.** reports/spec.md (N-000099) says overdue from 18:00 on the due date; loans/spec.md (N-000067/68) says the day after. Settled conflict verdict: loans wins. Chose overdue only when today > due date, everywhere including the report.
3. **Email in the report.** reports/spec.md (N-000109) forbids email; ops/notes.md (N-000084) wants it. Settled verdict: sixth column `email`. Chose header `item,title,member,due,days_overdue,email`; the member name is still never included.
4. **Fees over $5 block borrowing?** ops/notes.md (N-000085/86) says the tool does not go out; loans/spec.md (N-000057/58) says late fees never stop borrowing, only a reminder. Chose loans/spec.md: no block; checkout prints a reminder on stdout when the member has a balance.
5. **Renewal worked example.** The table shows 15 June -> 24 June -> 4 July (+9, +10 days), but the rule adds one 14-day period to the current due date (-> 29 June -> 13 July). Chose the rule text.
6. **Exit code for refusals on renew** (overdue, third renewal): chose 3 (lending rule), with the rule named in the message. Renewing a non-loaned item is 2; returning a non-loaned item is 2.
7. **Blocked member checking out**: exit 3 (glossary N-000009). Check order: unknown ids (2), item on loan (3), blocked (3), limit (3).
8. **Missing values vs missing arguments.** Missing positional args or unknown commands exit 1; missing `--email`/`--name` on `member add` exits 2 (spec says input error). Missing `--title` or `--out` exits 1 (argparse usage error).
9. **`status` without `--json`**: also prints the JSON (only the JSON form is specified).
10. **Invalid `LEND_NOW`**: exit 2. Datetimes use their date part with no timezone conversion.
11. **CSV line endings** are `\n`; quoting is minimal. Report to an unwritable path exits 2.
12. **Registering a duplicate/invalid value before store check**: missing store (4) takes precedence over input errors.
13. **Blocked flag in status**: true iff the member has an overdue loan.
