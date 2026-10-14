# Decisions

Decisions of the library's owner on points where the specification contradicts itself. A decision
wins over the text it names.

## 2026-10-13 — When a loan is overdue

`loans/spec.md` wins. A loan is overdue only from the day after its due date, in the report too; the
18:00 rule in `reports/spec.md` is dropped.

## 2026-10-13 — Email in the overdue report

`ops/notes.md` wins. Each report row carries the member's contact email in a sixth column named
`email`; the sentence in `reports/spec.md` that the report never contains an email is dropped.
