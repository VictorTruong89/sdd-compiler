# Round 22 readings

One reader (Claude, not blind to the key), rule of `TRIAL.md` §Scoring rule. Per run: each entry →
item (planted), `real-other`, `false` or `not-a-conflict`; then recall against the key. Borderline
readings are counted as not found and named.

## r22-sonnet-case016-1 (gate run)

16 entries. Key: r21 `ANSWER_KEY.md`, 17 conflicts (C01 C06 C08 C09 C11 C12 C13 C15 C16 C17 C18 C19
C20 C21 C22 C23 C25).

| Entry | Reading |
|---|---|
| 1 ledger 7 days vs one day | C19 |
| 2 newest 20 vs 50 records | C18 |
| 3 first vs last operand scanned | C08 |
| 4 tailing-negation form score-moving vs weight zero | C25 |
| 5 env word only when nothing stored vs takes precedence | C20 |
| 6 apply_patch 16 vs ten paths | C17 |
| 7 stats slice 200 vs 500 characters | C22 |
| 8 named transcript wins vs newer read | C23 |
| 9 decisive always ≥ 45 vs only above `low` | C06 |
| 10 usage to error stream vs stdout | C09 |
| 11 every no-break space converted vs kept beside digits | C15 |
| 12 two trailing spaces kept vs removed | C16 |
| 13 single transition fires 37 vs two or more | C11 |
| 14 `stop prosecheck` anywhere vs entire prompt | C21 |
| 15 any `utm_source` vs listed hosts only | C13 |
| 16 "from 9 to 5" a false range vs rhetorical sweep only | C12 |

**Found 16 / 17** (missed C01: stacked hedges as writing advice vs adding to the score). **Precision
16 / 16** (all planted; none real-other, false or not-a-conflict).

## All runs (the data is in `notes/score.py`, `FOUND` and `OTHER`)

Entries were mapped to items by what both sides say (the run's own entry headings are listed by
`grep -E "^#+ |^[0-9]+\. \*\*" runs/<run>/CONFLICTS.md`). No entry restated a planted item twice; no
entry stated only one side of an item it was mapped to. Missed items per run:

| Run | Entries | Missed | Other entries (reading) |
|---|---|---|---|
| sonnet-case006-1 | 20 | C03 C05 C06 C17 | — |
| sonnet-case006-2 | 21 | C03 C13 C17 C18 | interactive-session definition (false: one definition, unclear wording, in the original) |
| sonnet-case006-3 | 21 | C03 C05 C17 | — |
| haiku-case006-1 | 25 | C08 C22 | prompting option fully omitted (false: rule and its stated case, PRD 268–269); interactive session (false); group given only options: help or error (false: two cases, no arguments vs options only) |
| haiku-case006-2 | 22 | C03 C05 C13 C22 | chained subcommand option after argument (false: chain mode is the stated exception, FP-10); prompting option omitted (false) |
| haiku-case006-3 | 25 | C05 | prompting option omitted (false); nested group callback (false: default vs configured) |
| sonnet-case010-1 | 13 | C21 C22 | — |
| sonnet-case010-2 | 14 | C21 C22 | nonterminal symbol `str` allowed (IC 169) vs "not a `str`" in `rhs()` (IC 170) — **real**, in the original |
| sonnet-case010-3 | 12 | C14 C21 C22 | — |
| haiku-case010-1 | 15 | C21 C22 | underivable list empty iterator vs raise (false: general rule and its stated case, IC 174–175); nonterminal symbol (**real**) |
| haiku-case010-2 | 13 | C21 C22 | — |
| haiku-case010-3 | 14 | C21 C22 | bare trailing apostrophe split vs kept (false: listed with the clitics, PRD 104–106) |
| sonnet-case016-1 (gate) | 16 | C01 | — |
| sonnet-case016-2 | 15 | C12 C13 | — |
| sonnet-case016-3 | 16 | C13 | — |
| haiku-case016-1 | 20 | C11 C12 | zero-width always invisible (false: stated exception); `show` promises `.pdf` rows though `.pdf` is never scored (**real**, PRD 291 vs 195, in the original); "at most one file operand" (IC 21) vs two or more succeed (IC 82, 180; PRD 169) (**real**, in the original); model-dialect two hits (false: PRD 102 says two hits too); welcome names prosecheck vs silent contract (false: a stated one-time exception) |
| haiku-case016-2 | 18 | C12 | model-dialect two hits (false); Node.js in the hardware setup vs detector needs only Python (false: the setup covers the hooks) |
| haiku-case016-3 | 19 | C12 C13 | model-dialect two hits (false); at most one operand (**real**); `score_ci` omitted vs `null` (false, borderline: "omitted" may mean null); findings inside code vs invisible characters counted (false: the code exclusion is stated) |

"Real" readings were checked against the original Zero2Repo text in
`harness/benchmarks/zero2repo/download/Zero2Repo/benchmark/cases/<case>/public/`: each statement is
there unplanted.
