# Late fees

*Written by the treasurer, 2026-02-20.*

The library charges a late fee so that tools come back, not to raise money. The fee is deliberately
small, and it is capped so that a forgotten tool does not turn into a debt nobody can pay.

## How the fee is computed

When an item is returned after its due date, the member is charged **50 cents for every day** between
the due date and the return date. An item returned on its due date, or earlier, costs nothing.

The fee for a single loan is capped at **$10.00**. However late the item is, one loan never adds more
than 1000 cents to a member's balance.

Fees are recorded in whole cents. A member's balance is the sum of the fees from all their late
returns; the `fees_cents` field of `lend status --json` shows it.

Examples:

| Due date | Returned | Days late | Fee |
|---|---|---|---|
| 10 March | 10 March | 0 | $0.00 |
| 10 March | 13 March | 3 | $1.50 |
| 10 March | 30 March | 20 | $10.00 |
| 10 March | 15 April | 36 | $10.00 |

## What a fee does not do

A fee is recorded when the item comes back, not while it is out: an overdue loan has no fee until it is
returned. Paying fees is handled by the treasurer outside `lend`; there is no command for it in this
version.

Renewing a loan never costs anything, and renewal does not affect fees already owed.

## For the board

The treasurer reads the balances from `lend status --json`. Members with a balance are listed there;
the board's overdue report (`../reports/spec.md`) is about items still out, not about money.
