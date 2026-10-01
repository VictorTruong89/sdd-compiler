# Answer key — planted items in `spec/` (never shown to the agent)

> Written 2026-10-01 with the spec. Every other statement in `spec/` was written to be consistent; it
> was **not audited** by a second person. Anything else the compiler or an agent reports is judged on
> its merits.

| # | Kind | Statement A (file) | Statement B (file) | Scored |
|---|---|---|---|---|
| P1 | Contradiction | Fee cap **$10.00** per loan (`loans/fees.md`) | "Nobody should owe more than **$15** for one late tool" (`vision.md`) | A1 |
| P2 | Contradiction, boundary | "Overdue the day after its due date: on the due date itself it is still on time" (`loans/spec.md`) | "Counts as overdue from **18:00 on its due date**" (`reports/spec.md`) | A2 |
| P3 | Contradiction, negative constraint | Report "never contains a member's email address or name" (`reports/spec.md`) | "Each row should carry the member's contact email" (`ops/notes.md`) | A3 |
| P4 | Contradiction through an alias | "Late fees never stop a member from borrowing" (`loans/spec.md`) | "When a **patron** owes more than $5.00 … the tool does not go out" (`ops/notes.md`); "a patron is a member" (`glossary.md`) | A4 |
| P5 | Superseded rule | "Up to **5** items on loan at once" (`loans/spec.md`, revised 2026-03-02) | "Lowered to **3** … the loan specification still shows the old number" (`CHANGELOG.md`, 2026-05-10) | R9 |
| P6 | Duplicate, same rule | Report order (`reports/spec.md`) | Same order (`ops/notes.md`, and `CHANGELOG.md` 2026-05-10) | R21 |
| P7 | Duplicate, drifted wording | "Renewed at most two times" (`loans/spec.md`) | "Twice is the most … a third renewal" (`ops/notes.md`) | R15 |
| P8 | Scattered refinement | Standard period 14 days (`loans/spec.md`) | Power tools 7 days (`ops/notes.md`); garden follows the standard (`glossary.md`) | R6 |
| P9 | Rule buried in a definition | — | "A member with any overdue loan is *blocked*" — only in `glossary.md` (and in prose in `vision.md`) | R18 |
| P10 | Example contradicts its rule | Renewal adds a period to the **current due date** (`loans/spec.md`) | The worked example extends from the renewal date (10 June → 24 June) (`loans/spec.md`) | A5 |
| P11 | Subsumption, modality differs | "Every member MUST have an email" (`loans/spec.md`; `CHANGELOG.md` 2026-03-02) | "A member SHOULD keep an email on file" (`reports/spec.md`) | R4 |
| P12 | Vague | "Status should be fast" (`vision.md`) | — | A6 |

## Resolutions used by the reference implementation

The reference (`reference/`) takes one side only so that it runs; the hidden tests never depend on it:
cap $10 (P1) · overdue the day after (P2) · no email in the report (P3) · fees never block (P4) ·
renew from the current due date (P10).

## What the compiler should find, for the record

Detectable as conflicts by `sddc compile`: P1, P2, P3, P4, P10 (contradictions), P5 (contradiction or
subsumption between the spec and the changelog), P6, P7 (duplications), P11 (subsumption). P8 and P9
are not conflicts; the graph helps only if it puts the scattered pieces in the same pack or list.
Compiler recall on this key is a by-product of the study, *to be measured*.
