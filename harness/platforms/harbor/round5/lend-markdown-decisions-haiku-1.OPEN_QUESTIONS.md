# Open questions

Each entry says what the specification states, where, and what was implemented. Where
`spec/DECISIONS.md` settles a point, that decision is applied.

## 1. Borrowing limit

- **Spec says:** `spec/loans/spec.md` (Checkout): "a member may have up to 5 items on loan at once".
  `spec/CHANGELOG.md` (2026-05-10): the limit "is lowered to **3** tools at once per member ... this
  entry is the current rule."
- **Chose:** 3. The changelog says it is the current rule and the loan spec's 5 is stale. Constant
  `BORROWING_LIMIT` in `src/lend/rules.py`.

## 2. When a loan is overdue (and the 18:00 rule)

- **Spec says:** `spec/loans/spec.md` (Return): a loan is overdue "the day after its due date: on the
  due date itself it is still on time." `spec/reports/spec.md` (What is in it): a loan "counts as
  overdue from 18:00 on its due date".
- **Chose:** the day after the due date, for the report and for everything else. `spec/DECISIONS.md`
  (2026-10-13) says the loan spec wins and the 18:00 rule is dropped.

## 3. Email in the overdue report

- **Spec says:** `spec/reports/spec.md` (Privacy): the report "never contains a member's email address
  or name — only ids." `spec/ops/notes.md` (The board's overdue list): "Each row should carry the
  member's contact email."
- **Chose:** a sixth column `email` after `days_overdue`, per `spec/DECISIONS.md` (2026-10-13), which
  drops only the sentence about email. The member's **name** is still excluded, because the decision
  does not touch that part of the Privacy paragraph.

## 4. Renewal arithmetic: the worked example contradicts the rule

- **Spec says:** `spec/loans/spec.md` (Renewal): a renewal "adds one loan period ... to the **current
  due date**, so a member who renews early does not lose the days they had left." The worked example
  in the same section shows checkout 1 June (due 15 June), renewal 10 June → due **24 June**, renewal
  20 June → due **4 July**.
- **Problem:** 15 June + 14 days is 29 June, not 24 June. The example's dates are each *renewal date +
  14 days*, which is the behaviour the prose explicitly rules out.
- **Chose:** the prose rule. A renewal adds the category's loan period to the current due date, so the
  example becomes 15 June → **29 June** → **13 July**. The tests in `tests/test_lend.py` check this.
  If the example was intended, change `renew()` in `src/lend/commands.py` to add the period to the
  renewal date.

## 5. Late fees and checkout (the $5.00 rule)

- **Spec says:** `spec/loans/spec.md` (Checkout): "Late fees never stop a member from borrowing. A
  member who owes money is reminded at the counter, but the tool goes out." `spec/ops/notes.md` (Fees
  over five dollars): when a patron owes more than $5.00, "the tool does not go out until they have"
  settled.
- **Chose:** the loan specification. It is the normative spec and says "never" explicitly. The
  counter note is operational practice, and its claim that the specifications "say the same in more
  detail" is not true here. `spec/CHANGELOG.md` does not mention fees either. Checkout prints a
  reminder when the member owes money, and does not block. The $5.00 block is **not implemented**.
  If the board does want it, it is a small addition to `checkout()`.

## 6. Which exit code for a member added without an email

- **Spec says:** `spec/loans/spec.md` (Members and items): "a member added without one is an input
  error" (exit 2). The exit-code table says a "missing argument" is a usage error (exit 1).
- **Chose:** exit 2 for a missing `--email`, because the specific rule is about members. Other missing
  arguments (`--name`, `--title`, ids, positionals) exit 1. `--email` is therefore not marked required
  to argparse; `add_member()` raises the input error itself.

## 7. `lend status` without `--json`

- **Spec says:** only `lend status --json` is described.
- **Chose:** `lend status` without `--json` is a usage error (exit 1). No human-readable format is
  invented.

## 8. Email and name validation

- **Spec says:** "Every member MUST have an email address", with no format. Exit 2 covers "invalid value".
- **Chose:** an address must contain exactly one `@`, with non-empty parts on each side and no
  whitespace. Names and titles must not be blank. The email is kept as given.

## 9. Ids

- **Spec says:** examples such as `M7` and `T12`; no rule for the format.
- **Chose:** any non-empty id with no whitespace. Member and item ids are separate namespaces.

## 10. Sort order for ids

- **Spec says:** "sorted by id" and "sorted by item id", with no rule for comparing.
- **Chose:** plain string order. So `T10` comes before `T2`. Natural numeric ordering was not chosen
  because the spec gives no basis for it.

## 11. Blocking

- **Spec says:** the glossary says a member with any overdue loan is "blocked: they cannot check
  anything out until every overdue item is back." The vision says the same. The loan spec does not
  state the refusal in its Checkout section.
- **Chose:** refuse checkout (exit 3, rule named) for a blocked member. The status field `blocked`
  is true exactly when the member has an overdue loan.

## 12. Renewing on the due date

- **Spec says:** a loan is overdue only from the day after its due date. The loan spec says overdue
  loans cannot be renewed.
- **Chose:** a loan on its due date is not overdue, so it can be renewed that day. The consequence
  follows from item 2.

## 13. Unspecified behaviour around the store and I/O

- **Unreadable data file** (corrupt JSON): exit 2, with the reason on stderr. The exit-code table has
  no code for this.
- **`.lend/` present but its data file missing:** treated as an empty store, since `lend init` must not
  overwrite it.
- **`LEND_NOW`:** empty or non-ISO values are an input error (exit 2). For a date-time, the date part
  written in the string is used, with no timezone conversion.
- **Report `--out` that cannot be written** (missing folder, a directory): exit 2 with the reason.
- **CSV line endings:** the Python `csv` default, `\r\n` (RFC 4180).
- **Success messages:** the spec gives none. The commands print one short line each.

## 14. Commands the spec does not describe

- **Spec says:** the commands are `init`, `member add`, `item add`, `checkout`, `renew`, `return`,
  `status --json`, and `report --out`. The vision mentions "anything that needs a server" as out of
  scope but does not list other commands.
- **Chose:** implement only these. Anything else, such as listing members, removing items, or recording
  payments, is an unknown command (exit 1). Payments are out of scope per `spec/loans/fees.md`.

## 15. Fee cap versus the vision's promise

- **Spec says:** `spec/vision.md`: nobody owes more than $15 for one late tool. `spec/loans/fees.md`:
  the fee per loan is capped at $10.00.
- **Chose:** the $10.00 cap in `fees.md`. It satisfies the $15 promise, so the two do not conflict.
