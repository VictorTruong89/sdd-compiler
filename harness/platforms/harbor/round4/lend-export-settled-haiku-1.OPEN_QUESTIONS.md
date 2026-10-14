# Open questions

Every place where the specification in `spec/` is unclear, contradicts itself, or is silent and I had
to choose. Each entry says what the spec says (file and section), and what I chose. Pack numbers
refer to `spec/MAP.md`. Node ids are from `spec/CHECKLIST.md`.

## Contradictions

### 1. Borrowing limit: 5 or 3?

- **Spec says:** `loans/spec.md` › Checkout (pack 14, N-000054, MAY): "a member may have up to 5 items
  on loan at once." `CHANGELOG.md` › 2026-05-10 (pack 02, N-000001, MUST NOT): "The borrowing limit is
  lowered to **3** tools at once per member", and N-000002 (decision): "this entry is the current rule."
- **Chose:** 3. The changelog says it is the current rule and that the loan spec "still shows the old
  number in one place." `rules.BORROWING_LIMIT = 3`. Test: `test_N_000053_N_000054_…`.

### 2. When does a loan become overdue?

- **Spec says:** `loans/spec.md` › Return (pack 16, N-000067, N-000068): a loan "becomes overdue the day
  after its due date"; "on the due date itself it is still on time." `reports/spec.md` › What is in it
  (pack 22, N-000099): for the report "a loan counts as overdue from 18:00 on its due date."
- **Chose:** the day after the due date, everywhere (status, blocking, renewal, report). The export
  records this as settled (CF-000001, CF-000010): "Owner verdict 2026-10-13: loans/spec.md wins." The
  18:00 rule is not implemented. The tool has no notion of time of day.

### 3. Does the overdue report carry the member's email?

- **Spec says:** `reports/spec.md` › Privacy (pack 24, N-000109, MUST NOT): the report "never contains a
  member's email address or name — only ids." `operations/notes.md` (`ops/notes.md`, pack 09, N-000084,
  SHOULD): "Each row should carry the member's contact email so the board can write to them directly."
  The report's column table (pack 22) lists five columns, and N-000105 says the header has "exactly these
  column names."
- **Chose:** the ops note, following the export's settled verdict (CF-000004, CF-000009: "ops/notes.md
  wins. Each report row carries the member's contact email in a sixth column named `email`"). The report
  header is `item,title,member,due,days_overdue,email`. The member's name is never written to the report.
  The "never contains an email" sentence is dropped, as the verdict says.

### 4. Do late fees stop a member borrowing?

- **Spec says:** `loans/spec.md` › Checkout (pack 14, N-000057, MUST NOT): "Late fees never stop a member
  from borrowing." (N-000058, MUST): "A member who owes money is reminded at the counter, but the tool
  goes out." `operations/notes.md` › Fees over five dollars (pack 09, N-000085, MUST): when a patron owes
  more than $5.00, "we ask them to settle before they borrow again"; (N-000086, MUST NOT): "the tool does
  not go out until they have."
- **Not in the export's conflict list.** `MAP.md` reports "unsettled contradictions: 0", but these two
  rules cannot both hold for a member over $5.00.
- **Chose:** the loan spec. The tool does not block checkout for fees. The notes say they "say the same in
  more detail" as the loan spec, which they do not, and the loan spec is the spec for the command. When
  a balance is over $5.00 the checkout still succeeds and prints "Please ask <member> to settle late fees
  before borrowing again." A balance above $0 prints a reminder. N-000086 is not implemented. The owner should
  confirm this; if the $5.00 rule is wanted, it needs a loan-spec change and an exit-3 path.

### 5. Renewal worked example vs. the renewal rule

- **Spec says:** `loans/spec.md` › Renewal (pack 15, N-000060): a renewal "adds one loan period of the
  item's category to the **current due date**, so a member who renews early does not lose the days they
  had left." The worked example table (no node) for a hand tool, 14 days: checkout 1 June → due 15 June;
  renewal on 10 June → due **24 June**; renewal on 20 June → due **4 July**.
- **Problem:** the table is not what the rule produces. 15 June + 14 days is 29 June, and 29 June + 14 days
  is 13 July. The table's numbers are "renewal date + 14 days" (10 June + 14 = 24 June, 20 June + 14 = 4 July),
  which loses the days left. The rule says the opposite.
- **Chose:** the rule text (N-000060). Due date after renewal = current due date + loan period. Test
  `test_N_000059_N_000060_renewal_adds_period_to_current_due_date` asserts 29 June.

## Ambiguities and gaps

### 6. Late fee cap: $10 or $15?

- **Spec says:** `loans/fees.md` › How the fee is computed (pack 06, N-000015): the fee for a single loan
  "is capped at **$10.00**." `vision.md` (pack 00, N-000119, MUST NOT): "Nobody should owe more than $15 for
  one late tool."
- **Not a contradiction:** $10 satisfies the $15 limit. **Chose:** the $10 cap (1000 cents), which is the
  more specific rule.

### 7. Missing `--email` on `member add`

- **Spec says:** `loans/spec.md` › Members and items (pack 13, N-000042): "a member added without one is an
  input error" (exit 2). The exit-code table (pack 12, N-000036): exit 2 is an input error; exit 1 is a
  usage error, "unknown command or missing argument".
- **Chose:** the email is not required by argparse. A missing email exits **2**, as the spec says. A missing
  `--name`, a missing positional id, or a missing `--title` still exits **1** (argparse "missing argument").

### 8. Invalid category and other value errors

- **Spec says:** `loans/spec.md` › Members and items (pack 13, N-000048): "Any other category is an input
  error." (N-000036): an invalid value is exit 2.
- **Chose:** an invalid `--category` exits 2, not argparse's exit 1, so the code does its own validation.

### 9. Format of ids and email addresses

- **Spec says:** members and items are "identified by a short member id such as `M7`" and "an item id such as
  `T12`" (glossary, pack 18). Email is required (N-000041) with no format given. "Ids are unique" (N-000043)
  does not say whether member and item ids share one namespace.
- **Chose:** an id must be non-empty with no whitespace. Member ids and item ids are unique within their own
  kind, so `M1` and `T1` are independent. An email must match `something@something` with no whitespace.
  A name or title must not be blank.

### 10. `lend status` without `--json`

- **Spec says:** only `lend status --json` is defined (pack 17, N-000069).
- **Chose:** `--json` is required, so `lend status` alone is a usage error (exit 1). No plain-text status
  is invented.

### 11. Text output of the other commands

- **Spec says:** only `status --json` and the report have a defined output. The rest say nothing about
  what is printed.
- **Chose:** one short confirmation line on stdout for success (for example "Checked out T1 to M1; due
  2026-06-15."). Errors go to stderr as `lend: <message>`. Refusals name the rule, as N-000037 requires.

### 12. Order of checks when several rules fail

- **Spec says:** nothing about the order. N-000050, N-000051 require both ids to exist.
- **Chose:** for `checkout`: unknown member or item (exit 2), then item on loan, then member has an overdue
  loan, then borrowing limit (all exit 3). For `renew`: not on loan (exit 2), then overdue (exit 3), then the
  two-renewal limit (exit 3). For `return`: not on loan (exit 2).

### 13. Late-fee amount on a return, and the balance message

- **Spec says:** fees are recorded when the item comes back (N-000019); the balance is the sum of fees (N-000017).
- **Chose:** days late = return date minus due date, so a return on the due date or earlier costs nothing.
  The fee is `min(days × 50, 1000)` cents and adds to the member's balance. A balance is only ever increased
  by the tool, since payment is handled outside it (N-000020).

### 14. Sorting

- **Spec says:** `loans` "sorted by item id"; `members` "sorted by id"; `available` "sorted"; the report lists
  the most overdue first, and equally overdue loans "by item id" (N-000107, N-000108).
- **Chose:** plain string order for all of them, so `T10` sorts before `T2`. "Most overdue" means largest
  `days_overdue` first.

### 15. CSV quoting and line endings

- **Spec says:** "Values are written as plain CSV, quoted only when they contain a comma or a quote"
  (N-000106). It does not say what line endings to use.
- **Chose:** Python's `csv` module, minimal quoting, CRLF line endings (RFC 4180). The module also quotes a
  value that contains a line break. The spec does not mention line breaks, but without quoting they would
  break the row structure.

### 16. Store layout

- **Spec says:** "how the data is laid out inside it is up to the implementation" (N-000028, MAY).
- **Chose:** `.lend/store.json`, one JSON object, written atomically (temp file, then rename). Each item has at
  most one loan record, which enforces "a tool is lent to one member at a time."

### 17. An unreadable store

- **Spec says:** nothing.
- **Chose:** if `.lend/store.json` cannot be read or parsed, exit 2 with a message. The spec's exit codes do not
  fit this case better.

### 18. `LEND_NOW`

- **Spec says:** "an ISO-8601 date or date-time"; the date part is used (N-000087, N-000088, N-000039). The spec
  does not say what a time zone means.
- **Chose:** the date part as written. Any time part and zone offset are ignored, not converted. An empty
  `LEND_NOW` counts as unset. A value Python's `date.fromisoformat` or `datetime.fromisoformat` (3.12) cannot
  parse is an input error (exit 2). Week dates and ordinal dates are not accepted.

### 19. The report's directory and existing file

- **Spec says:** `lend report --out FILE` writes to FILE, "replacing it if it exists" (N-000092).
- **Chose:** FILE is relative to the current directory. If it cannot be written (for example its folder does
  not exist), exit 2 with a message. Existing content is overwritten.

### 20. Blocked members asked to return items first

- **Spec says:** `vision.md` (N-000120): a member with something overdue "is asked to bring it back before
  borrowing anything else." `glossary.md` (N-000009): an overdue member "cannot check anything out."
- **Chose:** the glossary, which is the binding definition (N-000006). A checkout by a blocked member is refused
  with exit 3, and the message names the overdue items. Renewals of other items are not blocked, because the
  spec only restricts checkout.
