# r28-zero2repo-reviews

> Opened 2026-11-11 by Claude Code. State: **done** (18 of 18 reviews scored, 2026-11-11). Round 28's reviews (plan §3; owner's go-ahead
> 2026-11-11, "Go ahead with round 28"): Haiku 3 + Sonnet 3 reviews of each new case's planted Markdown.

## Question

Claim 3 of the final report (a review is the better detector) on three more cases: per case, recall and
precision of a one-shot review against the answer key, as round 22. The first Haiku review of each case
(`r28-haiku-review-<case>-1`) becomes that case's **review list** arm, verbatim and unfiltered (rule of
rounds 23 and 25, fixed before any review ran).

## Design (round 22's, unchanged)

| Item | Value |
|---|---|
| Tasks | `notes/build_review_task.py` (round 22's; sources are round 28's Markdown tasks, so `spec/` is byte-identical to the Markdown arm's: `diff -r` against each case's `work/spec-planted`, no difference) |
| Instruction | round 22's, word for word: list every disagreement in `CONFLICTS.md`, both sides and where, no code |
| Runs | 18: per case Haiku 3, Sonnet 3 (`queue.tsv`) |
| Conditions | `trial.env`: Claude Code 2.1.316, no budget cap, `RUN_TIMEOUT=5400`, no early-stop rule |
| Scoring | one reader, every `CONFLICTS.md` in full against the case's `ANSWER_KEY.md` (found = both sides stated, as round 22); entries that are not planted items are judged true or false against the original spec |

## Runs

| Step | Result |
|---|---|
| Queue | started 2026-11-11 16:29 (-05:00), `nohup bash run_queue.sh r28-zero2repo-reviews` |
| Queue end | 2026-11-11 17:41: **18 done**, 0 retried, 0 limited; token prefix in no file under `runs/` or `work/jobs/`; 7-day window 0.49 → 0.54 (shared with the compiles) |
| Readings | one reader, every `CONFLICTS.md` in full; `notes/readings.md`; `notes/triage.py` points the reader only |
| Scores | `python3 notes/score.py` → `notes/scores.json` |

## Results

Found = entries that state both sides of a planted conflict. Precision = (found + real original
disagreements) / entries. Compiler recall from each case's `notes/recall.json`; "flagged" adds a planted
item caught through another sentence that states side A (round 21's rule).

| Case | Planted | Compiler recall (flagged) | Haiku found (each) | Sonnet found (each) | Haiku recall mean | Sonnet recall mean | False entries H / S | Precision mean H / S | $ est. H / S |
|---|---|---|---|---|---|---|---|---|---|
| case005 | 17 | 7 (8) | 15, 15, 17 | 15, 16, 16 | 92.1 % | 92.1 % | 1 / 0 | 97.9 / 100 % | 0.06 / 0.47 |
| case011 | 12 | 7 (7) | 11, 12, 12 | 12, 12, 12 | 97.2 % | 100 % | 1 / 0 | 97.6 / 100 % | 0.06 / 0.39 |
| case001 | 15 | 11 (12) | 14, 12, 13 | 15, 14, 15 | 86.7 % | 97.8 % | 1 / 2 | 97.6 / 95.9 % | 0.03 / 0.24 |

**Review lists** (the first Haiku review, verbatim): case005 flags 15 of 17 (misses C12, C18; 1 false
entry), case011 11 of 12 (misses C19; 1 false, 2 real original), case001 14 of 15 (misses C16; no other
entry). Never-found items: case005 C12 (0 of 6 reviews; the compiler also missed it), case001 C16 by
Haiku (0 of 3), C17 by 3 of 6. Real original disagreements found: case011's trailing dot (incomplete vs
syntax, 4 reviews), flatten whitespace (1), feature-point ordering (2).

Same direction as round 22 on its three cases: a one-shot review finds 87–100 % of the planted conflicts
for a few cents, against 41–73 % for the compiler's conflict check.
