# `lend` — requirement list for scoring

> Source: `spec/` (7 files). Scoring is against this list, never the graph's node list. **Test** = a
> hidden test in `hidden_tests/test_lend_hidden.py`; **audit** = judged by reading the agent's code and
> `OPEN_QUESTIONS.md`, blind to format where possible. Planted items: `ANSWER_KEY.md`.

| # | Requirement | Source | Scored by |
|---|---|---|---|
| R1 | `init` creates `.lend/`; a second `init` exits 2 | loans §store | test `test_r1_*` |
| R2 | Without a store, commands exit 4 and name `lend init` | loans §store | test `test_r2_*` |
| R3 | Members are added once; a duplicate id exits 2 | loans §members | test `test_r3_*` |
| R4 | A member without an email is refused (P11) | loans §members, reports §privacy | test `test_r4_*` |
| R5 | Items: category `hand`/`power`/`garden`, default `hand`; bad category or duplicate exits 2 | loans §members and items | test `test_r5_*` |
| R6 | Loan period: hand 14, garden 14, power 7 days (P8) | loans §checkout, ops, glossary | test `test_r6_*` |
| R7 | Unknown item or member at checkout exits 2 | loans §checkout | test `test_r7_*` |
| R8 | An item on loan cannot go out again (exit 3) | loans §checkout, vision | test `test_r8_*` |
| R9 | Borrowing limit 3 (P5: changelog supersedes the spec's 5) | loans §checkout, CHANGELOG | test `test_r9_*` |
| R10 | Return frees the item; returning an item not on loan exits 2 | loans §return | test `test_r10_*` |
| R11 | Returning on the due date costs nothing | fees | test `test_r11_*` |
| R12 | 50 cents per day late | fees | test `test_r12_*` |
| R13 | Fees add up in the member's balance | fees | test `test_r13_*` |
| R14 | A renewal adds one period (on the due date) | loans §renewal | test `test_r14_*` |
| R15 | At most two renewals (P7) | loans §renewal, ops | test `test_r15_*` |
| R16 | An overdue loan cannot be renewed (exit 3) | loans §renewal | test `test_r16_*` |
| R17 | Renewing an item not on loan exits 2 | loans §renewal | test `test_r17_*` |
| R18 | A member with an overdue loan is blocked until it is back (P9) | glossary, vision | test `test_r18_*` |
| R19 | `status --json` shape, sorting, `overdue`, `days_overdue`, `available` | loans §status | test `test_r19_*` |
| R20 | The report lists only overdue loans, with the five columns and values | reports | test `test_r20_*` |
| R21 | Report order: most overdue first, then item id (P6) | reports, ops, CHANGELOG | test `test_r21_*` |
| R22 | An empty report is a header; the file is replaced | reports §command | test `test_r22_*` |
| R23 | An unknown command exits 1 | loans §store | test `test_r23_*` |
| R24 | `LEND_NOW` may carry a time; its date is used | loans §store, ops | test `test_r24_*` |
| A1 | Fee cap: $10 (fees) vs $15 (vision) — P1 | | **audit**: noticed? chosen? |
| A2 | Overdue from the day after the due date (loans) vs from 18:00 on it (reports) — P2 | | **audit** |
| A3 | Report never carries email (reports) vs carries contact email (ops) — P3 | | **audit** |
| A4 | Fees never block borrowing (loans) vs a *patron* owing > $5 cannot borrow (ops; glossary: patron = member) — P4 | | **audit** |
| A5 | Renewal adds to the current due date (rule) vs from the renewal date (worked example) — P10 | | **audit** |
| A6 | "Status should be fast" — vague, untestable — P12 | | **audit**: listed as open? |

**Audit scale per item A1–A6:** 0 not noticed · 1 noticed (named in `OPEN_QUESTIONS.md` or a code comment)
· 2 noticed and the choice stated with its source. The audit never judges which side was chosen.
