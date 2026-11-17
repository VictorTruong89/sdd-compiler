# Round 28 review readings (one reader, Claude Code, 2026-11-11)

Each `CONFLICTS.md` read in full against the case's `ANSWER_KEY.md`. **Found** = an entry states both
sides of a planted conflict (round 22's rule); `notes/triage.py` only pointed at candidate items. Entries
that are not planted items are judged against the **original** spec: **real** (a disagreement the original
text already has) or **false** (the two statements can both hold). Machine-readable form: `notes/score.py`.

## case005 (17 planted)

| Run | Entries | Found | Missed | Other entries |
|---|---|---|---|---|
| haiku-1 | 16 | 15 | C12, C18 | #16 false (after an accepted switch, an empty chunk then bytes: the feed-order runtime error is caller misuse, not parsing; both rules hold) |
| haiku-2 | 15 | 15 | C12, C15 | — |
| haiku-3 | 17 | 17 | — | — |
| sonnet-1 | 15 | 15 | C12, C15 | — |
| sonnet-2 | 16 | 16 | C12 | — |
| sonnet-3 | 16 | 16 | C12 | — |

## case011 (12 planted)

| Run | Entries | Found | Missed | Other entries |
|---|---|---|---|---|
| haiku-1 | 14 | 11 | C19 | #12 false (`length(string, array or object)` lists the types of one argument); #13 real (whitespace between tokens vs flatten "written with nothing between them"); #14 real (a trailing dot is both "incomplete" by FP-01's general rule and "syntax" by its explicit rule) |
| haiku-2 | 15 | 12 | — | #5 real (trailing dot, as above); #14 real (FP-01 refers to FP-08's options against "never the reverse"); #15 real (FP-04 uses FP-06's comparators, same rule) |
| haiku-3 | 13 | 12 | — | #13 real (trailing dot) |
| sonnet-1 | 12 | 12 | — | — |
| sonnet-2 | 12 | 12 | — | — |
| sonnet-3 | 12 | 12 | — | — |

## case001 (15 planted)

| Run | Entries | Found | Missed | Other entries |
|---|---|---|---|---|
| haiku-1 | 14 | 14 | C16 | — |
| haiku-2 | 12 | 12 | C12, C16, C17 | — |
| haiku-3 | 14 | 13 | C16, C17 | #6 false (more dotted keys in the same section extend the implicit table; reopening is from a later section, TOML v1.1.0; as the compiler's CF-000011) |
| sonnet-1 | 16 | 15 | — | #15 false (same as haiku-3 #6) |
| sonnet-2 | 14 | 14 | C17 | — |
| sonnet-3 | 16 | 15 | — | #13 false (same as haiku-3 #6) |
