# r27b-zero2repo-haiku-topup-case010

> Opened 2026-11-16 by Claude Code. State: **closed 2026-11-17** (8 of 8 runs scored, read by reader 1 and reader 2). Round 27b of
> `docs/MIA5150-Project/extra-trials-plan.md` §2: the optional Haiku top-up, run because budget remained after
> round 28 (7-day window at 0.07 on 2026-11-16 18:42). Owner, 2026-11-16: "complete all remaining runs of round
> 27a and 28 … then proceed to the next runs".

## Question

With case010's Haiku cells at n = 3 in every arm, does adding 2 runs per arm (n = 5, as on the other four cases)
change any arm's core, naming or built sides?

## Design

| Item | Value |
|---|---|
| Arms and tasks | the frozen tasks of the earlier rounds, linked, not rebuilt: Markdown and oracle export from round 19 (`r19-zero2repo-case010-conflicts/work/tasks`), review list from round 25, compiler export from round 27 (`work/tasks/case010-<arm>` are symlinks) |
| Runs | Haiku only, 2 per arm (`-4`, `-5`), 8 runs, interleaved across the four arms (`queue.tsv`) |
| Conditions | `trial.env`: Claude Code 2.1.316, no budget cap, `RUN_TIMEOUT=9000`, early-stop rerun rule with threshold 99 (half of 197): the earlier rounds' conditions |
| Scoring | round 19's scorer, probes and footprint on the saved code; readings by reader 1 under the same strict rule; reader 2 by `r26-…/notes/reader2.py` |
| Confound | these runs are a week or more after the cells they join (rounds 19, 25, 27); the report keeps n = 3 tables and gives n = 5 beside them |

## Runs

| Step | Result |
|---|---|
| Queue | started 2026-11-16 (-05:00), `nohup bash run_queue.sh r27b-zero2repo-haiku-topup-case010`; 8 of 8 done by 2026-11-17 04:32; no early stop |
| Scores | `python3 score/case010/notes/score.py runs/r27b-*` (round 27's copies of round 19's scorer, probes and footprint, unchanged) → `score/case010/notes/scores.json` |
| Readings | reader 1 → `notes/readings.txt`, `python3 notes/detection.py` → `notes/detection.tsv` (round 27's columns) |

## Results (2026-11-17)

| Run | Tests | Core (of 173) | Named | Turns | $ est. |
|---|---|---|---|---|---|
| `r27b-case010-haiku-compiler-4` | 174/197 | 164 | 13 of 15 | 89 | 0.98 |
| `r27b-case010-haiku-compiler-5` | 176/197 | 159 | 12 of 15 | 45 | 0.64 |
| `r27b-case010-haiku-markdown-4` | 170/197 | 156 | 9 of 15 | 37 | 0.65 |
| `r27b-case010-haiku-markdown-5` | 166/197 | 156 | 7 of 15 | 44 | 0.80 |
| `r27b-case010-haiku-oracle-4` | 171/197 | 162 | 14 of 15 | 54 | 0.88 |
| `r27b-case010-haiku-oracle-5` | 180/197 | 162 | 14 of 15 | 48 | 0.76 |
| `r27b-case010-haiku-review-4` | 178/197 | 162 | 13 of 15 | 27 | 0.42 |
| `r27b-case010-haiku-review-5` | 175/197 | 159 | 13 of 15 | 56 | 0.49 |

Total $5.62 est. **Reader 2** (round key `r27bb`): 120 readings, agreement 1.000, κ 1.000.
n = 5 cells (with rounds 18/19, 25, 27) and the tests over 6 cases are in `harness/trials/stats/power_plan_topup.json`
(`TOPUP=1 python3 stats/power_plan.py`) and in the final report draft §4.1–4.2.

## Files

| Path | Tracked | What |
|---|---|---|
| `TRIAL.md`, `trial.env`, `queue.tsv` | yes | Description, conditions, queue |
| `work/` | **no** | Task links, Harbor jobs |
