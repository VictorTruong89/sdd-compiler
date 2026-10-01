# Glossary

Terms used across the Lend specifications. Where a definition says more than a name, it is binding.

**Member** — a person registered with the library, identified by a short member id such as `M7`.
Some older pages say *patron*; a patron is a member.

**Item** — one physical tool, identified by an item id such as `T12`. Two identical drills are two
items.

**Category** — every item belongs to exactly one category: `hand`, `power` or `garden`. Garden
equipment follows the standard loan period; only power tools differ.

**Loan** — the record that one item is out with one member, from checkout until it is returned.

**Due date** — the calendar date by which a loan should be returned. It is a date, not a time.

**Overdue** — a loan whose due date has passed and which has not been returned. A member with any
overdue loan is *blocked*: they cannot check anything out until every overdue item is back.

**Renewal** — extending a loan that is not overdue, without bringing the item to the counter.

**Late fee** — the amount a member owes for returning an item after its due date. Fees are kept in
cents.

**Available** — an item that exists and is not on loan.

**Report** — the overdue list for the board (see `reports/spec.md`).
