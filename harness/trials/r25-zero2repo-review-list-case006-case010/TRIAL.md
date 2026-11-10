# r25-zero2repo-review-list-case006-case010

> Opened 2026-11-09. State: **closed** 2026-11-10 (12 of 12 runs scored). Approved by the owner 2026-11-09: "do all A-B-C-D by yourself and
> report the results to me" (B = more cases; done here as the review-list arm on the two other planted
> cases, not on new cases — see "Why not new cases"). Update this file at every step.

## Question

Does round 23's result — the Markdown plus a review's conflict list gives the flag effect — hold on
case006 (24 planted conflicts) and case010 (15)?

## Why not new cases

Option B as proposed (two new Zero2Repo cases, each with an answer key, footprints, probes and three
arms) costs about $40 est. per case and several days of planting before any run. The review-list arm
on the two cases already planted reuses their answer keys, probes, footprints and round 18/19 arms, and
gives the round-23 comparison on three cases in total, which is the generality question that matters
for the report. New cases remain open.

## Design

| Item | Value |
|---|---|
| Cases | case006: round 18's planted spec (24 conflicts, core 445); case010: round 19's (15 conflicts, core 173) |
| Arm | **Review list**: the round's Markdown task, `spec/` unchanged, plus `spec/CONFLICTS.md` |
| The lists | **Rule as round 23, fixed before any run:** the first Haiku review of each case in round 22. `r22-haiku-case006-1` (25 entries: flags 22 of 24, misses C08 and C22; 3 false entries) and `r22-haiku-case010-1` (15 entries: flags 13 of 15, misses C21 and C22; 1 false, 1 real original disagreement). Verbatim, unfiltered. Leak check (`planted\|oracle\|answer key\|r1x/r2x\|Cnn\|Gnn\|CF-`): 0 matches |
| Instruction | The round's Markdown instruction plus round 23's sentence: "`spec/CONFLICTS.md` is a reviewer's list of places where those files disagree; it is not part of the specification." (`diff -r`: that line, the list file, `task.toml`'s name) |
| Models, n | Haiku 3, Sonnet 3 per case (rounds 18/19's n) |
| Conditions | rounds 18/19's: Claude Code 2.1.316, no dollar ceiling, early-stop rerun. Threshold half the tests: **case010 99, case006 238**. The driver reads one threshold, so the queue runs in two phases: phase 1 the 6 case010 rows (threshold 99), phase 2 the 6 case006 rows (held, then threshold 238 set before phase 2's driver starts) |
| Comparison | round 18 (case006) and round 19 (case010): Markdown and oracle export arms, same tasks otherwise. No compiler-export arm exists for these cases |
| Measures | set 1 core (445 / 173); set 2a named under the strict rule (24 / 15); named on listed / unlisted items; side B built; cost |
| Scorer | rounds 18/19's `notes/score.py`, `probe.sh`, `footprint.json`, `plant.py` (copied, unchanged except run paths); readings by the same one reader |

**Comparisons fixed before any run.** (1) Named over all items: review list vs Markdown and oracle
export of the same case. (2) Named on the listed and on the unlisted items. (3) Set 1, descriptive.
(4) Whether a false list entry changes what is built.

## Runs

| Step | What | Result |
|---|---|---|
| Check run | `run_queue.sh … --one`: `r25-sonnet-case010-1`, 23:27–23:38 (-05:00), in parallel with round 24's check run (machine: 20 cores, 31 GB; rounds 18–23 ran one run at a time) | 185 / 197, core 165, 14 turns, $1.26 est.; 13 / 13 listed named; token in no file |
| Phase 1 | the other 5 case010 rows, 23:54–04:52, threshold 99 | 5 done; paused 00:37–04:25 (5-hour window) |
| Phase 2 | `trial.env` set to 238 at 04:54:39 by a watcher after phase 1's driver ended (logged in `trial.env`); the 6 case006 rows released from hold | 6 done 05:13–10:19; paused 05:49–09:25; none retried, rerun or stopped early; token string in no saved file |
| Scores | `python3 score/<case>/notes/score.py runs/r25-*<case>*` (round 18/19's scorers, copied unchanged) → `score/<case>/notes/scores.json` | tests, core, sides for all 12 |
| Readings | one reader (Claude Code), every `NOTES.md` → `notes/readings.txt`; `python3 notes/detection.py` → `notes/detection.tsv` | 6 × 24 + 6 × 15 items |
| Tables | `python3 notes/tables.py` → `notes/tables.json` | below; rounds 18 and 19 reproduce the interim report's §4.6 and §4.7 exactly |

## Results

| Case | Model | Arm | Named, all items | On listed items | Unlisted named | Side B built | Side B built unnamed | Core | $ est. mean |
|---|---|---|---|---|---|---|---|---|---|
| case006 (24) | Haiku | Markdown (r18) | 36.1 % | 39.4 % | 0 / 6 | 11 / 72 | 7 | 87.6 % | 0.46 |
| | | oracle export (r18) | 100 % | 100 % | 6 / 6 | 7 / 72 | 0 | 91.8 % | 1.22 |
| | | **review list** | **94.4 %** | **100 %** | 2 / 6 | 2 / 72 | 0 | 91.2 % | 0.89 |
| | Sonnet | Markdown (r18) | 73.6 % | 77.3 % | 2 / 6 | 4 / 72 | 1 | 98.6 % | 2.12 |
| | | oracle export (r18) | 100 % | 100 % | 6 / 6 | 28 / 72 | 0 | 98.4 % | 2.22 |
| | | **review list** | **90.3 %** | **95.5 %** | 2 / 6 | 4 / 72 | 1 | 98.6 % | 2.02 |
| case010 (15) | Haiku | Markdown (r19) | 51.1 % | 59.0 % | 0 / 6 | 15 / 45 | 9 | 89.8 % | 0.52 |
| | | oracle export (r19) | 95.6 % | 94.9 % | 6 / 6 | 18 / 45 | 0 | 91.9 % | 0.98 |
| | | **review list** | **86.7 %** | **100 %** | 0 / 6 | 16 / 45 | 6 | 92.5 % | 0.62 |
| | Sonnet | Markdown (r19) | 66.7 % | 76.9 % | 0 / 6 | 10 / 45 | 6 | 97.1 % | 1.44 |
| | | oracle export (r19) | 93.3 % | 92.3 % | 6 / 6 | 11 / 45 | 0 | 96.9 % | 1.57 |
| | | **review list** | **86.7 %** | **100 %** | 0 / 6 | 6 / 45 | 6 | 96.3 % | 1.34 |

n = 3 per cell. Named per run: case006 Haiku 22 · 22 · 24, Sonnet 22 · 23 · 20 (of 24); case010 13 in all 6 runs (of 15). Tests per run: case006 Haiku 408, 434, 458, Sonnet 468, 468, 469 (of 476); case010 Haiku 178, 171, 173, Sonnet 185, 190, 185 (of 197). Turns: case006 Haiku 63–77, Sonnet 19–21; case010 Haiku 34–49, Sonnet 14–21. **Cost: $14.61 est.** for 12 runs.

**Listed items.** 207 of 210 listed-item readings named: case010 78 / 78; case006 Haiku 66 / 66, Sonnet 63 / 66 (run 1 missed C01, run 3 missed C01 and C29, each giving only the built behaviour).

**Unlisted items.** case010's C21 and C22 were named in 0 of 12 readings and built on side B unnamed in every run — the same as round 19's Markdown runs, while the oracle export (which flags them) got 12 / 12. case006's C08 and C22: 4 of 12 (Haiku run 3 named both; two Sonnet runs named C22), against 2 / 12 from the Markdown.

**False entries.** case006's list has 3 false entries and case010's 1. No run built a behaviour the spec does not state because of them: each run resolved them by the stated rule and its stated case (prompting option, interactive session, group with options only; empty iterator vs raise). The misleading build of round 23 (model-dialect hits) did not recur on these cases.

## Findings

1. **Round 23's result holds on both other cases.** With the review list, every Haiku run named every listed conflict on both cases, and Sonnet named 95.5–100 %. Over all items the list arm reached 86.7–94.4 %, against 36.1–73.6 % from the Markdown and 93.3–100 % from the oracle export. On case016 (round 23) it was 89.4 and 96.1 %.
2. **The help is item by item on three of three cases.** Unlisted conflicts gained nothing on case010 (0 / 12, as the Markdown) and little on case006 (4 / 12 vs 2 / 12). The oracle export's lead over the list (5.6–9.7 points over all items) comes mostly from its flags on the 2 items the list misses (for case006 Haiku, entirely: 4 readings of 72; for Sonnet, 4 of the 7 readings).
3. **No cost on code.** Core is between, or within 0.8 points of, the Markdown and oracle arms in every cell (case006 Haiku 91.2 vs 87.6 / 91.8 %, Sonnet 98.6 vs 98.6 / 98.4 %; case010 92.5 vs 89.8 / 91.9 %, 96.3 vs 97.1 / 96.9 %).
4. **False entries did not travel here.** 4 false entries across the two lists caused no unsupported build; round 23's one misleading entry was a statement that one side of the spec had no condition, which these lists did not contain.
5. **Cheaper than the export.** Coding runs cost about the same as the Markdown arm for Sonnet and 1.2–1.9× for Haiku; the lists cost $0.02–0.04 est. each (round 22), against a compile of $1.49–2.89 est. plus verdicts.

**What this does not show.** n = 3 per cell; one list per case, chosen by rule; one non-blind reader (second reader: round 26); the comparison arms ran in rounds 18 and 19 (same conditions and tasks, a week earlier), not interleaved with this round; this round ran in parallel with round 24, where earlier rounds ran one run at a time.

## Files

| Path | Tracked | What |
|---|---|---|
| `TRIAL.md`, `trial.env`, `queue.tsv`, `run_queue.log` | yes | Description, conditions, queue, driver log |
| `runs/<run_id>/` | yes | Run files, `NOTES.md`, `app.tgz`, `agent.tgz` |
| `notes/` | yes | Copied scorers, readings, scores, tables |
| `work/` | **no** | The tasks (hidden tests, planted spec), Harbor jobs |
