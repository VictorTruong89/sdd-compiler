# Open questions

Each entry says what the specification says (node id and pack), and what this implementation chose.
Items 1 to 4 are the contradictions the export marks UNSETTLED; items 5 onward are conflicts or gaps
I found while reading the packs.

## 1. When does a loan become overdue? (CF-000001, CF-000010)

- **Spec:** N-000067 (pack 16, Return): "A loan becomes overdue the day after its due date." N-000068:
  "on the due date itself it is still on time." The glossary (pack 18) agrees: a loan is overdue when
  "its due date has passed".
  N-000099 (pack 22, The overdue report): "a loan counts as overdue from 18:00 on its due date".
- **Chosen:** two rules, each where its text places it.
  - Everything except the report uses the date rule: status (`overdue`, `days_overdue`), blocking at
    checkout (N-000009), refusing renewal of an overdue loan (N-000062). A loan is overdue when today is
    after its due date.
  - The report alone uses the 18:00 rule, because N-000099 says "for the purpose of the report". A loan
    appears in the report from 18:00 on its due date. Its `days_overdue` is then 0.
  - Consequence: on its due date after 18:00, a loan is listed in the report while `lend status --json`
    still says `"overdue": false`.

## 2. Does the report carry a contact email? (CF-000004, CF-000009)

- **Spec:** N-000084 (pack 09, counter notes, SHOULD): each row "should carry the member's contact
  email". N-000105 (pack 22): "The first row is the header, with exactly these column names." The
  column table in pack 22 has five columns and no email. N-000109 (pack 24, MUST NOT): the report
  "never contains a member's email address or name — only ids."
- **Chosen:** the report has exactly the five columns in the table, and no email or name. N-000109 is a
  MUST NOT and N-000084 is only a SHOULD, so the email is not written. N-000084 is listed as not done in
  `IMPLEMENTATION_NOTES.md`.

## 3. Borrowing limit: 3 or 5? (not flagged by the MAP)

- **Spec:** N-000054 (pack 14, Checkout, MAY): "up to 5 items on loan at once". N-000001 (pack 02,
  2026-05-10 changelog, MUST NOT): "The borrowing limit is lowered to **3** tools at once per member".
  N-000002 (decision): the changelog entry "is the current rule".
- **Chosen:** 3. The changelog says it is the current rule and is the newer decision. The
  checkout refusal names the limit as "borrowing limit of 3".

## 4. Renewal: from the current due date or from the renewal date? (not flagged by the MAP)

- **Spec:** N-000060 (pack 15, MUST): a renewal "adds one loan period … to the **current due date**, so a
  member who renews early does not lose the days they had left." The worked example in the same pack
  contradicts this: checkout 1 June (due 15 June); renewal on 10 June gives "24 June", and renewal on
  20 June gives "4 July". Both are 14 days after the renewal date, not after the due date.
- **Chosen:** the rule text, because it is the normative statement and the example's own numbers
  contradict its stated purpose. Renewing on 10 June gives 29 June, and a second renewal adds another 14
  days. The example's numbers are not reproduced.

## 5. Do fees over $5.00 stop a checkout? (not flagged by the MAP)

- **Spec:** N-000057 (pack 14, MUST NOT): "Late fees never stop a member from borrowing." N-000058
  (MUST): a member who owes money "is reminded at the counter, but the tool goes out." Against this,
  N-000085 (pack 09, MUST): when a patron owes more than $5.00, "we ask them to settle before they borrow
  again", and N-000086 (MUST NOT): "the tool does not go out until they have."
- **Chosen:** the loans specification (pack 14) wins. Fees never stop a checkout. A member who owes money
  gets a reminder line. Above $5.00 the reminder asks the volunteer to ask the member to settle. The
  refusal in N-000086 is not implemented. The pack-09 notes say they record how the counter works and
  that the loans specification "say[s] the same in more detail", which points to pack 14 when they differ.

## 6. Missing `--email`: input error or usage error?

- **Spec:** N-000042 (pack 13): "a member added without one is an input error" (exit 2). The exit-code
  table (pack 12, N-000035/36): a missing argument is a usage error (exit 1).
- **Chosen:** a missing or blank `--email` is an input error (exit 2), since N-000042 names it
  specifically. A missing `--name` or `--title` is a usage error (exit 1), since those are plain required
  arguments.

## 7. `lend status` without `--json`

- **Spec:** N-000069 (pack 17) defines only `lend status --json`. It says nothing about the bare command.
- **Chosen:** usage error, exit 1, with the message "status needs --json". No human-readable format is
  invented.

## 8. Format of ids, names, titles and emails

- **Spec:** the examples use `T12`, `M7`. No format rule is given (pack 18, glossary). Email addresses
  are required (N-000041) but their format is not defined.
- **Chosen:** an id is one non-empty word with no whitespace. A name or title is one non-empty line. An
  email must have the shape `something@something` with no spaces. Titles are one line only, because a
  line break would break the CSV report. A bad value is an input error (exit 2).

## 9. Storage layout and a damaged store

- **Spec:** N-000028 (pack 12, MAY): the layout inside `.lend/` is up to the implementation.
- **Chosen:** `.lend/store.json` holds members, items and open loans, written atomically. A `.lend/`
  folder without `store.json` is an empty store. A `store.json` that cannot be parsed is an input error
  (exit 2); the spec does not give a code for this case.

## 10. `LEND_NOW` details

- **Spec:** N-000087 (pack 09) and N-000088 (ISO-8601 date or date-time). N-000039 (pack 12): the date
  part of `LEND_NOW` is "today".
- **Chosen:** an empty or blank `LEND_NOW` is treated as unset. A value that is not a valid ISO-8601 date
  or date-time is an input error (exit 2). A date-time with a time zone keeps its wall-clock fields, and
  the offset is dropped. When `LEND_NOW` is a bare date, the report's 18:00 cutoff uses the system clock's
  time of day on that date. A time-less `LEND_NOW` therefore makes the report depend on when it is run,
  for due-date loans only.

## 11. Several checks can fail at once

- **Spec:** not stated.
- **Chosen:** checkout checks, in order: both ids exist (exit 2); the item is not already on loan; the
  member is not blocked by an overdue loan; the member is under the limit (all three exit 3). The first
  failing check is reported. Renewal checks overdue before the renewal count.

## 12. Blocking applies to checkout only

- **Spec:** N-000009 (pack 18): a blocked member "cannot check anything out until every overdue item is
  back". N-000120 (pack 00): an overdue member "is asked to bring it back before borrowing anything else".
- **Chosen:** blocking applies to checkout. Renewing an item that is not overdue is still allowed for a
  member with another overdue loan. The spec calls renewal an extension, not a checkout, and says nothing
  to the contrary.

## 13. Report file encoding and line endings

- **Spec:** the report is "plain CSV" (N-000106) and must be quoted "only when they contain a comma or a
  quote" (N-000106). It says nothing about encoding or line endings.
- **Chosen:** UTF-8 with `\n` line endings. The Python `csv` module is used with its standard quoting,
  which also quotes fields containing a line break. Line breaks cannot occur because of item 8.
