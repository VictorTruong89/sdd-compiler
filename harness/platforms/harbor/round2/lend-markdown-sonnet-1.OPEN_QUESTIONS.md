# Open questions

1. **Borrowing limit.** `loans/spec.md` (Checkout) says 5; `CHANGELOG.md` (2026-05-10) says 3 and calls itself the current rule. Chose **3**.
2. **Power-tool loan period.** `loans/spec.md` says the standard period is 14 days with no exception; `CHANGELOG.md` 2026-03-02 and `ops/notes.md` say power tools get 7 days. Chose **7 days** for power (also used for renewals, per "loan period of the item's category"); hand and garden 14.
3. **Late-fee cap.** `vision.md` says nobody owes more than $15 per late tool; `loans/fees.md` says 1000 cents. Chose **1000 cents** (the detailed, treasurer-written rule).
4. **Fees blocking borrowing.** `ops/notes.md` says owing more than $5 blocks checkout; `loans/spec.md` and `fees.md` say fees never stop borrowing. Chose **fees never block**; only overdue loans block.
5. **Overdue blocking exit.** Glossary/vision say overdue members are blocked, but `loans/spec.md` doesn't list it as a checkout refusal. Chose refusal with exit 3 ("blocked").
6. **Report overdue timing.** `reports/spec.md` says a loan counts as overdue in the report from 18:00 on its due date, while `loans/spec.md` says it is overdue only the day after. Chose: status/blocking/renewal/fees use the date rule; the report uses the 18:00 rule against the current time (the time part of `LEND_NOW` if given, a date-only `LEND_NOW` is midnight, so nothing is reported on the due date). `days_overdue` in the report is whole days (today - due), hence 0 on the due date after 18:00.
7. **Report email.** `ops/notes.md` says each row should carry the member's email; `reports/spec.md` says the report never contains email or name, and fixes the columns. Chose **no email** (privacy, and explicit column list).
8. **Report order tie-break.** CHANGELOG (item id) vs. older "member id": used item id (string order).
9. **Missing values exit code.** "Missing argument" is exit 1, "missing value" is exit 2. Chose: missing positional arguments or unknown commands → 1; missing `--name/--email/--title` (and empty values) → 2; missing `--out` → 1.
10. **Email validation.** Only checked that it has a non-empty local and domain part around `@`.
11. **Renew refusals.** Overdue and third renewal are refused with exit 3; unknown item id → 2.
12. **Invalid `LEND_NOW`** → exit 2.
13. **`status` without `--json`** prints the same JSON.
