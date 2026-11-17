# r27b-zero2repo-haiku-topup-case006

> Opened 2026-11-16 by Claude Code. State: **closed 2026-11-17** (8 of 8 runs scored, read by reader 1 and reader 2). Round 27b of
> `docs/MIA5150-Project/extra-trials-plan.md` §2: the optional Haiku top-up, run because budget remained after
> round 28 (7-day window at 0.07 on 2026-11-16 18:42). Owner, 2026-11-16: "complete all remaining runs of round
> 27a and 28 … then proceed to the next runs".

## Question

With case006's Haiku cells at n = 3 in every arm, does adding 2 runs per arm (n = 5, as on the other four cases)
change any arm's core, naming or built sides?

## Design

| Item | Value |
|---|---|
| Arms and tasks | the frozen tasks of the earlier rounds, linked, not rebuilt: Markdown and oracle export from round 18 (`r18-zero2repo-case006-notes-both-sides/work/tasks`), review list from round 25, compiler export from round 27 (`work/tasks/case006-<arm>` are symlinks) |
| Runs | Haiku only, 2 per arm (`-4`, `-5`), 8 runs, interleaved across the four arms (`queue.tsv`) |
| Conditions | `trial.env`: Claude Code 2.1.316, no budget cap, `RUN_TIMEOUT=9000`, early-stop rerun rule with threshold 238 (half of 476): the earlier rounds' conditions |
| Scoring | round 18's scorer, probes and footprint on the saved code; readings by reader 1 under the same strict rule; reader 2 by `r26-…/notes/reader2.py` |
| Confound | these runs are a week or more after the cells they join (rounds 18, 25, 27); the report keeps n = 3 tables and gives n = 5 beside them |

## Runs

| Step | Result |
|---|---|
| Queue | started 2026-11-16 (-05:00), `nohup bash run_queue.sh r27b-zero2repo-haiku-topup-case006`; 8 of 8 done by 2026-11-17 06:05; markdown-4 stopped early on its first attempt (kept as `.earlystop-…`) and was rerun once under the rule |
| Scores | `python3 score/case006/notes/score.py runs/r27b-*` (round 27's copies of round 18's scorer, probes and footprint, unchanged) → `score/case006/notes/scores.json` |
| Readings | reader 1 → `notes/readings.txt`, `python3 notes/detection.py` → `notes/detection.tsv` (round 27's columns) |

## Results (2026-11-17)

| Run | Tests | Core (of 445) | Named | Turns | $ est. |
|---|---|---|---|---|---|
| `r27b-case006-haiku-compiler-4` | 467/476 | 438 | 22 of 24 | 74 | 1.72 |
| `r27b-case006-haiku-compiler-5` | 438/476 | 410 | 24 of 24 | 80 | 1.50 |
| `r27b-case006-haiku-markdown-4` | 464/476 | 434 | 17 of 24 | 55 | 1.06 |
| `r27b-case006-haiku-markdown-5` | 435/476 | 406 | 13 of 24 | 70 | 0.50 |
| `r27b-case006-haiku-oracle-4` | 468/476 | 438 | 24 of 24 | 54 | 1.21 |
| `r27b-case006-haiku-oracle-5` | 449/476 | 420 | 24 of 24 | 67 | 1.35 |
| `r27b-case006-haiku-review-4` | 462/476 | 432 | 23 of 24 | 49 | 1.27 |
| `r27b-case006-haiku-review-5` | 460/476 | 430 | 22 of 24 | 64 | 1.33 |

Total $9.93 est. **Reader 2** (round key `r27ba`): 192 readings, agreement 1.000, κ 1.000.
n = 5 cells (with rounds 18/19, 25, 27) and the tests over 6 cases are in `harness/trials/stats/power_plan_topup.json`
(`TOPUP=1 python3 stats/power_plan.py`) and in the final report draft §4.1–4.2.

## Files

| Path | Tracked | What |
|---|---|---|
| `TRIAL.md`, `trial.env`, `queue.tsv` | yes | Description, conditions, queue |
| `work/` | **no** | Task links, Harbor jobs |
