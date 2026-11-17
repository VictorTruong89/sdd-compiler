# r26-second-reader-detection

> Opened 2026-11-09. State: **closed** 2026-11-10 (rounds 18, 19, 21, 23, 24, 25). Approved by the owner 2026-11-09: "do all A-B-C-D by yourself and
> report the results to me" (C = a second reader for conflict naming). No coding run; model calls only for
> reading. Update this file at every step.

## Question

Does the "conflict named" reading (set 2a, strict rule), on which every detection result of rounds
18–25 rests, survive an independent second reader who is blind to arm?

*Why:* every naming figure so far is one reader's (the assistant in Claude Code), not blind to arm
(threat #5 of the interim report). The owner's own audit sheets are prepared but not filled. A human
second reader is still the stronger check; this round gives an independent, arm-blind model reading
now and says where the two disagree.

## Design

| Item | Value |
|---|---|
| Reader 1 | the readings already recorded in each round's `notes/detection.tsv` (conflicts only) |
| Reader 2 | `claude -p --model sonnet --tools "" --setting-sources ""` in an empty temporary folder: no tools, no project files, no memory; one fresh call per run |
| What reader 2 sees | the strict rule (round 21 `TRIAL.md`, word for word); each item's side A and side B from the round's `ANSWER_KEY.md`; the run's `NOTES.md` under a code (N001...). **Not** the run id, arm, model, or reader 1's reading. Not fully blind: export runs' notes may cite conflict ids |
| Runs read | rounds 18 (12 runs × 24), 19 (12 × 15), 21 (24 × 17), 23 (8 × 17) = 1 012 item readings; rounds 24 and 25 added when read by reader 1 |
| Output | `notes/reader2.tsv` (both readings, reader 2's quote); `notes/agreement.json`: per group, n, raw agreement, Cohen's κ, and the two disagreement directions |
| Script | `notes/reader2.py read` (model calls), `notes/reader2.py table` (no model call); raw answers in `work/raw/` |

**Fixed before reading the agreement:** reader 1's figures stay the report's figures; the agreement and
the list of disagreements are reported beside them. If reader 2's counts would change a comparison
(an arm's order), that is reported as a finding, not used to re-score.

## Steps

| Step | Result |
|---|---|
| Test call | one r23 run: the first prompt's example used the id `C02`, and the reply added keys for ids not asked; example made generic, call redone: 17 keys, $0.05 est. Extra keys are ignored when tabulating and logged |
| Read | rounds 18, 19, 21, 23: 56 calls, 23:35–00:40 (-05:00), none failed, $2.28 est. in all (`notes/agreement.json`) |
| Table | `python3 notes/reader2.py table` → `notes/reader2.tsv`, `notes/agreement.json` |
| Read, rounds 24 and 25 | 20 calls on 10 November after reader 1's readings were written; none failed; $3.09 est. for all 76 calls |

## Results (rounds 18, 19, 21, 23)

| Group | Item readings | Agreement | Cohen's κ | Reader 1 named | Reader 2 named |
|---|---|---|---|---|---|
| **All** | 1 012 | **99.5 %** | **0.985** | 809 | 810 |
| Round 18 (case006), Markdown / oracle export | 144 / 144 | 99.3 % / 99.3 % | 0.986 / — ¹ | 79 / 144 | 80 / 143 |
| Round 19 (case010), Markdown / oracle export | 90 / 90 | 100 % / 98.9 % | 1.000 / 0.903 | 53 / 85 | 53 / 84 |
| Round 21 (case016), Markdown / compiler / oracle | 136 each | 100 / 100 / 98.5 % | 1.000 / 1.000 / 0.901 | 91 / 108 / 124 | 91 / 108 / 126 |
| Round 23 (case016), review list | 136 | 100 % | 1.000 | 125 | 125 |

¹ κ is undefined in use when one reader says *named* for every item (reader 1: 144 of 144); raw agreement is the measure there.

**The 5 disagreements, adjudicated against the notes** (by Claude, the first reader; to be checked by the owner):

| Run | Item | Reader 1 | Reader 2 | Notes say | Verdict |
|---|---|---|---|---|---|
| r18-sonnet-markdown-2 | C26 | no | yes | "PRD: ellipsized to fit the line; IC §2: cut at 45 characters" — the key's side A is "the first sentence of the docstring" | borderline: a disagreement on the same point, with a different side A |
| r18-sonnet-export-3 | C27 | yes | no | "FP-02 'end of help page' vs Contract 'right after the description, before the options'" | reader 1 (both sides stated) |
| r19-haiku-export-2 | C14 | yes | no | "A: … gives no trees. B: … parsing does not succeed (raises)" (reader 2 quoted it, then said no) | reader 1 |
| r21-sonnet-oracle-1 | C16 | no | yes | only the built side ("trailing spaces … removed … the collapse required") | reader 1 (one side) |
| r21-sonnet-oracle-1 | C23 | no | yes | conflict ids plus the built side only | reader 1 (one side) |

**Findings.** (1) The naming reading is reproducible: an arm-blind second reader agrees on 1 007 of
1 012 item readings (κ 0.985), and the counts per arm differ by at most 2 readings. **No arm comparison
of the interim report changes** (each arm's named total moves by 0–2 of 85–144). (2) All 5 disagreements
are in export arms or one borderline Markdown reading; every Markdown, compiler-export and review-list
cell of rounds 19, 21 and 23 agrees exactly. (3) Reader 2 is not more lenient overall (810 vs 809) but
leans on conflict ids twice (accepting one side plus an id), the case the strict rule excludes.

## Results added: rounds 24 and 25

| Group | Item readings | Agreement | Cohen's κ | Reader 1 named | Reader 2 named |
|---|---|---|---|---|---|
| Round 24 (case016), settled list | 136 | 100 % | 1.000 | 108 | 108 |
| Round 25 case006, review list | 144 | 98.6 % | 0.893 | 133 | 135 |
| Round 25 case010, review list | 90 | 100 % | 1.000 | 78 | 78 |
| **All six rounds** | **1 382** | **99.5 %** | **0.983** | 1 128 | 1 131 |

Three disagreements came up in rounds 24–25. **One changed reader 1's reading:** `r24-haiku-settled-3` C20
gives only locations ("PRD line 246 vs IC line 63"), not either side's content, so it is *not named* under the
strict rule; reader 1 had counted it, reader 2 did not. Reader 1's reading was corrected (round 24
`notes/readings.txt`; Haiku named 16 · 15 · 14 · 14 · 15), and the round-24 row above is after the correction.
The other two (`r25-sonnet-case006-1` and `-3`, C01) give only the built behaviour; reader 2 counted them,
reader 1 did not, and reader 1's reading stands.

Over all six rounds, 8 disagreements in 1 382 readings: reader 1 held on 6, reader 2 was right on 1 (corrected),
1 is borderline (C26, round 18). No arm comparison changes.

**What this does not show.** Reader 2 is a Claude model like reader 1 (Sonnet; reader 1 is Claude Code, Opus 5.5 in rounds 23–25), so shared
model biases are not excluded; it saw the answer key's sides, as reader 1 did; export notes cite conflict
ids, so it is blind to arm by label, not by content. A human sample (the owner's audit sheets) remains
the stronger check.

## Results added: rounds 27, 27b and 28 (2026-11-16 to 2026-11-17)

`ROUNDS` and `KEY_OF` gained r27 (rounds 18/19 keys by case), r27ba / r27bb (round 27b, keys of rounds 18 and 19)
and r28a / r28b / r28c (case005, case011, case001, their own keys). Same prompt, model, rule and blinding; codes
continue the seeded shuffle (`work/codes.json`). `python3 notes/reader2.py read r27 r28a r28b r28c r27ba r27bb`,
then `table`.

| Round | n | Agreement | κ | Reader 1 yes | Reader 2 yes | R1 yes, R2 no | R1 no, R2 yes |
|---|---|---|---|---|---|---|---|
| r27 | 234 | 0.991 | 0.954 | 209 | 211 | 0 | 2 |
| r27ba | 192 | 1.000 | 1.000 | 169 | 169 | 0 | 0 |
| r27bb | 120 | 1.000 | 1.000 | 95 | 95 | 0 | 0 |
| r28a | 544 | 0.998 | 0.990 | 491 | 490 | 1 | 0 |
| r28b | 384 | 1.000 | 1.000 | 323 | 323 | 0 | 0 |
| r28c | 480 | 0.983 | 0.944 | 389 | 395 | 1 | 7 |
| all | 3336 | 0.995 | 0.980 | 2804 | 2814 | 4 | 14 |

Adjudication by reader 1 on re-reading: round 27's 2 (case010 C18, emoticon clash only) and case005's 1
(`haiku-compiler-5` C04, both sides stated) hold. On case001, 10 disagreed before adjudication: 2 were corrected
(`haiku-markdown-1`, `haiku-review-2` C16, now named; "corrected 2026-11-16 after reader 2" in its readings)
and 8 hold. Over rounds 18–28: 21 disagreements, 3 corrected reader 1 (with round 26's one), 18 held. The
table above is after the corrections. Cost of reader 2 so far $8.44 est.
