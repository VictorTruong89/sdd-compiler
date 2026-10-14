# Open questions

Places where the specification in `spec/` is unclear or contradicts itself, and what this
implementation does. Each entry says what the specification says, where, and the choice made.
Paths are relative to `spec/`.

## Contradictions

### 1. Borrowing limit: 5 or 3?

- **Spec says:** `loans/spec.md` (Checkout): "a member may have up to 5 items on loan at once."
  `CHANGELOG.md` (2026-05-10): the limit "is lowered to **3** tools at once per member"; the
  entry notes that the loan specification "still shows the old number in one place; this entry is
  the current rule."
- **Chose:** 3. The changelog is the later decision by the board, and it says so explicitly.
  Constant `BORROWING_LIMIT` in `src/lend/library.py`.

### 2. Renewal: new due date from the current due date, or from the renewal date?

- **Spec says:** `loans/spec.md` (Renewal) states the rule: a renewal "adds one loan period … to the
  **current due date**, so a member who renews early does not lose the days they had left." The
  worked example in the same section, for a 14-day hand tool, gives due 15 June, renewed 10 June →
  24 June, renewed 20 June → 4 July. Those figures are the renewal date plus 14 days, so the
  example drops the days left, which the rule says must be kept.
- **Chose:** the rule. The same example becomes 15 June → 29 June (10 June) → 13 July (20 June).
  The example's figures are not implemented. See `Library.renew` in `src/lend/library.py`.

### 3. Loan period for power tools: 14 or 7 days?

- **Spec says:** `loans/spec.md` (Checkout): "The standard loan period is 14 days." `CHANGELOG.md`
  (2026-03-02): "Power tools are lent for 7 days." `ops/notes.md`: "every power tool is lent for 7
  days instead of the usual period." `glossary.md`: "Garden equipment follows the standard loan
  period; only power tools differ."
- **Chose:** power tools 7 days; hand and garden tools 14 days. Renewals add the same period for the
  item's category. See `loan_period_days` in `src/lend/library.py`.

### 4. When does a loan count as overdue?

- **Spec says:** `loans/spec.md` (Return): "A loan becomes overdue the day after its due date: on the
  due date itself it is still on time." `reports/spec.md` (What is in it): "For the purpose of the
  report, a loan counts as overdue from 18:00 on its due date."
- **Chose:** both, in their own scope. The status command, blocking and renewal use "the day after".
  The report includes a loan once the report's clock reaches 18:00 on its due date, so on the due
  date itself the report shows the loan with `days_overdue` 0. The report's clock is `LEND_NOW` when
  set, or the system clock otherwise. A date-only `LEND_NOW` means midnight, so loans due on that
  date are not included. Time zones in `LEND_NOW` are ignored. See `overdue_rows` in
  `src/lend/report.py`.

### 5. Does the board's report carry member emails?

- **Spec says:** `reports/spec.md` (Privacy): the report "never contains a member's email address or
  name — only ids." `ops/notes.md` (The board's overdue list): "Each row should carry the member's
  contact email so the board can write to them directly."
- **Chose:** the report spec. The CSV has only the five columns it defines, and no name or email.
  The ops note is not implemented.

### 6. Do unpaid late fees block borrowing?

- **Spec says:** `loans/spec.md` (Checkout): "Late fees never stop a member from borrowing. A member
  who owes money is reminded at the counter, but the tool goes out." `ops/notes.md` (Fees over five
  dollars): when a member owes more than $5.00 "the tool does not go out until they have" settled.
- **Chose:** the loans spec. Fees never block checkout. Any member with a balance above zero gets a
  reminder line when they check out, which is how "reminded at the counter" is read here. The $5
  rule from the ops notes is not implemented.

### 7. Missing `--email` on `member add`: usage error (1) or input error (2)?

- **Spec says:** `loans/spec.md` (Members and items): "a member added without one is an input
  error", which is exit 2. The exit-code table in the same file says a "missing argument" is a usage
  error, exit 1.
- **Chose:** exit 2 for a missing or empty `--email`, because the specific rule wins over the general
  one. Other missing arguments (`--name`, `--title`, command arguments, `--out`) exit 1.

## Gaps and unstated details

### 8. Sort order for ids

- **Spec says:** loans "sorted by item id" (`loans/spec.md`, Status), and report rows "listed by item
  id" (`reports/spec.md`, Order). The spec does not say whether `T10` sorts before or after `T2`.
- **Chose:** plain string order everywhere, so `T10` sorts before `T2`. Member ids are sorted the same
  way.

### 9. `lend status` without `--json`

- **Spec says:** only `lend status --json` is defined (`loans/spec.md`, Status).
- **Chose:** without `--json`, print a plain-text version of the same information for the counter.
  The JSON contract is unchanged. The text layout is my own.

### 10. Output text of the other commands

- **Spec says:** nothing about the messages printed by `init`, `member add`, `item add`, `checkout`,
  `renew`, `return` or `report`. Only the exit codes and the `.lend/` requirement are given.
- **Chose:** short one-line confirmations on stdout. Errors go to stderr as `lend: <message>`.

### 11. Exit codes for renewal refusals

- **Spec says:** an overdue loan "cannot be renewed", and a loan "can be renewed at most two times"
  (`loans/spec.md`, Renewal). The exit-code table gives 3 for "Refused by a lending rule".
- **Chose:** exit 3 for both refusals, with the rule named in the message. An item that is not on
  loan is an input error (exit 2), as the spec says.

### 12. Checkout by a blocked member

- **Spec says:** `glossary.md` says a member with an overdue loan is blocked and "cannot check anything
  out". `loans/spec.md` (Checkout) lists only "already on loan" and "at the borrowing limit" as
  refusals.
- **Chose:** refuse with exit 3 and rule `overdue`. Returning items is still allowed. Checks run in
  this order: item already on loan, then blocked, then borrowing limit.

### 13. Late fee on a renewed loan

- **Spec says:** the fee is "50 cents for every day between the due date and the return date"
  (`fees.md`). A renewal moves the due date.
- **Chose:** the current due date, which is the date after any renewals. A loan's total fee is still
  capped at $10.00.

### 14. Email and name format

- **Spec says:** every member "MUST have an email address" (`loans/spec.md`). It does not say what
  counts as an address. Exit code 2 covers "invalid value".
- **Chose:** an email is valid if it has the shape `something@something` with no spaces. A name
  cannot be blank. Both failures exit 2. Ids may be any non-empty string without whitespace. The
  spec's examples, `M7` and `T12`, are not enforced.

### 15. Unreadable or damaged store, or unwritable report path

- **Spec says:** nothing.
- **Chose:** a store file that is missing, unreadable or damaged exits 2 with a message. A report
  path that cannot be written exits 2. Both use the existing codes, since the spec defines no others.

### 16. Invalid `LEND_NOW`

- **Spec says:** `LEND_NOW` "is an ISO-8601 date or date-time" (`ops/notes.md`). It does not say what
  to do with a value that is not one.
- **Chose:** exit 2 with a message naming the variable. An empty `LEND_NOW` is treated as unset.

### 17. CSV line endings

- **Spec says:** "plain CSV, quoted only when they contain a comma or a quote" (`reports/spec.md`). It
  does not give a line terminator.
- **Chose:** `\n` line endings. Fields are quoted when they contain a comma, a quote, or a line break,
  which is the standard library's minimal quoting. This is not RFC 4180's CRLF.

## Checked, no conflict

- The vision promises that nobody owes more than $15 for one late tool. The fee cap is $10.00
  (`fees.md`), which satisfies that promise, so no change was needed.
- The changelog's "members must give an email address" agrees with `loans/spec.md`.
- `reports/spec.md` says a member "SHOULD keep an email on file". That is weaker than the MUST in
  `loans/spec.md`, and the two do not conflict.
