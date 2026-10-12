# Loans

*Last revised 2026-03-02.*

## Purpose

This specification covers the `lend` command: the store, members, items, and the life of a loan from
checkout to return. Fees are in `fees.md`; the board's report is in `../reports/spec.md`.

## The store and the command line

`lend init` creates a `.lend/` folder in the current directory. Every other command works on the
`.lend/` folder of the current directory; how the data is laid out inside it is up to the
implementation. Running `lend init` where `.lend/` already exists changes nothing and exits with
code 2. Any other command run where there is no `.lend/` exits with code 4 and says to run `lend init`.

Exit codes are the same for every command:

| Code | Meaning |
|---|---|
| 0 | Done |
| 1 | Usage error: unknown command or missing argument |
| 2 | Input error: an unknown or duplicate id, a missing or invalid value |
| 3 | Refused by a lending rule (the rule is named in the message) |
| 4 | No store here |

The date "today" is the system date, or the date part of `LEND_NOW` when that variable is set.

## Members and items

`lend member add ID --name NAME --email EMAIL` registers a member. Every member MUST have an email
address; a member added without one is an input error. Ids are unique: adding an id that exists is an
input error.

`lend item add ID --title TITLE [--category CATEGORY]` registers an item. The category is `hand`,
`power` or `garden`, and is `hand` when not given. Any other category is an input error, and so is a
duplicate id.

## Checkout

`lend checkout ITEM MEMBER` lends an item to a member. Both must exist (otherwise an input error). The
checkout is refused when the item is already on loan, or when the member is at the borrowing limit: a
member may have up to 5 items on loan at once.

The due date is today plus the loan period. The standard loan period is 14 days.

Late fees never stop a member from borrowing. A member who owes money is reminded at the counter, but
the tool goes out.

## Renewal

`lend renew ITEM` extends the loan of an item that is on loan. A renewal adds one loan period of the
item's category to the **current due date**, so a member who renews early does not lose the days they
had left. A loan can be renewed at most two times. An overdue loan cannot be renewed; it has to be
returned. Renewing an item that is not on loan is an input error.

Worked example (a hand tool, 14-day period):

| Event | Date | Due date afterwards |
|---|---|---|
| Checkout | 1 June | 15 June |
| Renewal | 10 June | 24 June |
| Renewal | 20 June | 4 July |

## Return

`lend return ITEM` ends the loan of an item; the item is available again. Returning an item that is not
on loan is an input error. A late return adds a late fee to the member's balance (see `fees.md`).

A loan becomes overdue the day after its due date: on the due date itself it is still on time.

## Status

`lend status --json` prints one JSON object describing the store as of today:

```json
{
  "today": "2026-06-01",
  "loans": [
    {"item": "T1", "member": "M1", "due": "2026-06-15", "renewals": 0,
     "overdue": false, "days_overdue": 0}
  ],
  "members": [
    {"id": "M1", "name": "Ana", "loans": 1, "fees_cents": 0, "blocked": false}
  ],
  "available": ["T2", "T3"]
}
```

`loans` lists every open loan, sorted by item id. `days_overdue` is the number of days between the due
date and today when the loan is overdue, and 0 otherwise. `members` lists every member, sorted by id,
with the number of items they have on loan, the late fees they owe in cents, and whether they are
blocked from borrowing. `available` lists the ids of items not on loan, sorted.
