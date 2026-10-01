# Lend — vision

The Eastside Tool Library lends hand tools, power tools and garden equipment to its members, the way a
book library lends books. Until now the volunteers at the counter have kept loans in a shared
spreadsheet. It breaks in predictable ways: two people lend the same drill on the same afternoon,
nobody notices a hedge trimmer that has been out since spring, and the treasurer rebuilds the fee
totals by hand at the end of every month.

`lend` replaces the spreadsheet with a small command-line tool that a volunteer runs on the counter
laptop. It keeps the members, the tools and the loans in one folder, and it answers the questions
the volunteers actually ask: is this tool in, who has that one, what is overdue, and what does a member
owe.

What we promise members:

- A tool is lent to one member at a time, and the counter can always tell you who has it.
- Everyone gets the same loan period for the same kind of tool, long enough to finish most weekend
  projects twice.
- Late fees are small and capped. Nobody should owe more than $15 for one late tool, however late it
  comes back.
- A member who has something overdue is asked to bring it back before borrowing anything else.
- Status should be fast: a volunteer with a queue at the counter cannot wait for it.

What we promise the board: a monthly list of overdue loans they can read without the spreadsheet.

Out of scope for the first version: online reservations, payments, reminders by email, and anything
that needs a server. Everything runs on one laptop, from one folder.
