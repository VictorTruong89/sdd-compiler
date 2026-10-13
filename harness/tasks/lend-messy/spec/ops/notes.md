# Counter operations notes

*Kept by the Saturday volunteers. These notes record how we run things at the counter; the
specifications in `loans/` and `reports/` say the same in more detail.*

**Power tools go out for a week.** Since the cordless-drill shortage last winter, every power tool is
lent for 7 days instead of the usual period. Hand tools and garden equipment are not affected.

**Limits.** A member can have several tools out at once, up to the borrowing limit. We do not make
exceptions at the counter, even for board members.

**Renewals.** Twice is the most. When someone asks for a third renewal, the tool has to come back to
the counter first.

**The board's overdue list.** We print it on the first Saturday of the month. It lists the most overdue
loans first; loans that are equally overdue are listed by item id. Each row should carry the member's
contact email so the board can write to them directly.

**Fees over five dollars.** When a patron owes more than $5.00 in late fees, we ask them to settle
before they borrow again, and the tool does not go out until they have.

**Clock.** The counter laptop's clock has drifted twice. The tool reads the date from the `LEND_NOW`
environment variable when it is set (an ISO-8601 date or date-time); the treasurer uses this to
re-run last month's report.
