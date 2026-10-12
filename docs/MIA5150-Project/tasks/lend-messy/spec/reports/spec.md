# The overdue report

*Requested by the board, 2026-01-15; revised 2026-05-10.*

## Purpose

Once a month the board reviews which tools are overdue and decides whom to call. The report gives them
that list as a CSV file they can open in a spreadsheet, without access to the counter laptop.

## Command

`lend report --out FILE` writes the report to `FILE`, replacing it if it exists, and exits with code 0.
It is written even when nothing is overdue: then it holds only the header row.

## What is in it

One row per overdue loan, and nothing else: loans that are on time do not appear, and neither do
returned loans. For the purpose of the report, a loan counts as overdue from 18:00 on its due date,
when the counter closes for the day; the board would rather call a day early than a day late.

The columns, in this order:

| Column | Content |
|---|---|
| `item` | The item id |
| `title` | The item's title |
| `member` | The member id |
| `due` | The due date, `YYYY-MM-DD` |
| `days_overdue` | Whole days between the due date and today |

The first row is the header, with exactly these column names. Values are written as plain CSV, quoted
only when they contain a comma or a quote.

## Order

The most overdue loans come first. Loans that are equally overdue are listed by item id.

## Privacy

The report leaves the library: board members open it on their own computers and sometimes forward it.
It therefore never contains a member's email address or name — only ids. The board looks members up
at the counter when it decides to call. (A member SHOULD keep an email on file so the board can reach
them, but the report does not carry it.)
