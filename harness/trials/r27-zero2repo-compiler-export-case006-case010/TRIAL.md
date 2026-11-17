# r27-zero2repo-compiler-export-case006-case010

> Opened 2026-11-10. State: **closed** 2026-11-11 (12 of 12 runs scored and read by reader 1); reader 2 read 2026-11-16 (see Results).
> Round 27a of `docs/MIA5150-Project/extra-trials-plan.md`.
> Approved by the owner 2026-11-10: "start running round 27a as discussed in
> docs/MIA5150-Project/extra-trials-plan.md". Round 27b (Haiku top-up) is **not** approved and not queued.
> Update this file at every step.

## Question

Does the compiler's own export (`sddc export`, nothing injected) raise naming on case006 and case010
where it flags, as it did on case016 (round 21)? Fills Table 2's empty compiler-export cells (claim 2b
on 3 cases).

## Design

| Item | Value |
|---|---|
| Cases | case006: round 18's planted spec (24 conflicts, core 445); case010: round 19's (15 conflicts, core 173) |
| Arm | **Compiler export**: the round's measured compile (`work/compile-full` of round 17 for case006, round 19 for case010), the round's own verdicts on the non-planted contradictions recorded (`false` rows; `open` rows left open), **nothing injected** — round 21's compiler arm |
| Store script | `notes/compiler_store.py` = step 1 of round 19's `oracle_store.py`, step 2 (injection) left out. Verdicts copied to `notes/<case>/oracle_verdicts.tsv` |
| Export | `sddc --root work/compile-compiler-<case> export --allow-open --out work/export-compiler-<case>` |
| Tasks | copies of round 18's `case006-planted24-export-oracle` and round 19's `case010-planted15-export-oracle` with `environment/spec/` replaced by the compiler export and `task.toml` name/description changed. Instruction, Dockerfile, tests (incl. case010's model files for the verifier) unchanged |
| Models, n | Haiku 3, Sonnet 3 per case (the n of these cases' other arms) |
| Conditions | rounds 18/19/25's: Claude Code 2.1.316, no dollar ceiling, early-stop rerun. Threshold half the tests: case010 99, case006 238. Two phases as round 25, run by `notes/phases.sh` (phase 1 case010 rows; then threshold 238 written to `trial.env`, case006 rows released from hold, phase 2) |
| Order | per case: Sonnet 1 (first), Haiku 1, Haiku 2, Sonnet 2, Haiku 3, Sonnet 3 |
| Comparison | rounds 18/19 (Markdown, oracle export) and 25 (review list), same tasks otherwise; not interleaved (a week apart) |
| Measures | as round 25: set 1 core; set 2a named under the strict rule, on flagged and unflagged items; side B built; cost |
| Scorer | rounds 18/19's `score.py`, `probe.sh`, `footprint.json`, `plant.py` (to be copied unchanged except run paths); readings by reader 1, then reader 2 (round 26's script) |

## Build checks (2026-11-10, no model call)

| Check | Result |
|---|---|
| Verdicts recorded | case006 51 false, 4 open; case010 33 false, 4 open |
| Export | case006: 33 packs, 1 044 nodes, **18 unsettled** (14 found planted + 4 open); case010: 29 packs, 517 nodes, **13 unsettled** (9 found + 4 open) |
| `diff -r` against the rounds' oracle exports | only `export.meta.json`, `MAP.md` and the packs holding injected conflicts differ (case006 13 packs, case010 6); every removed line is an injected conflict, its rationale, or a count/size; all other packs byte-identical, so today's `sddc` reproduces round 17/19's export |
| `diff -r` task vs oracle task | `environment/spec/` and `task.toml` (name, description) only |
| Leak check (`planted\|oracle\|answer key\|r1x/r2x\|Cnn\|sk-ant`) | 0 matches in both exports |
| Do-nothing (`notes/check_nop.sh`) | 0 passed on both (judge reports 0 total, as rounds 18/19's checks) |

## Runs

| Step | What | Result |
|---|---|---|
| Launch | `nohup setsid bash notes/phases.sh >> run_queue.log` at 2026-11-10 18:03 (-05:00); 7-day window 0.24 at 09:53 (resets 16 Nov 16:00) 12 of 12 done 18:18–21:31; none retried, rerun or stopped early; driver ended 00:47 after a 5-hour-window pause (0.93) with no row left; token string in no saved file. Tests passed: case010 Sonnet 183, 177, 178, Haiku 177, 177, 163 (of 197); case006 Sonnet 465, 455, 453, Haiku 466, 465, 457 (of 476). **Cost $18.89 est.** (12 runs). 7-day window 0.44 after the last run (0.24 at 09:53, which includes other use in between) |
| Scores | `python3 score/<case>/notes/score.py runs/r27-*<case>*` (rounds 18/19's scorers as copied in round 25, unchanged) → `score/<case>/notes/scores.json` | tests, core, sides for all 12; one "neither" reading (`r27-haiku-case006-3` C26) |
| Readings | reader 1 (Claude Code, Opus 5.5), every `NOTES.md` → `notes/readings.txt`; `python3 notes/detection.py` → `notes/detection.tsv` | 6 × 24 + 6 × 15 items, 2026-11-11 |
| Tables | `python3 notes/tables.py` → `notes/tables.json` (rounds 18/19/25's arms recomputed from their files reproduce round 25's table) | below |
| Stats | `harness/trials/stats/power_plan.py` now also reads this round's compiler rows | Table 1a of the final report draft |

## Results

**Flags.** The compiler export flags **case006 15 of 24** (the 14 found by round 17's compile, plus C10 through
CF-000151: C10's side B against the original PRD sentence that carries side A, counted as flagged by round 21's
C13 rule) and **case010 9 of 15** (C18 with the wrong rationale, emoticon case, as in round 19).

| Case | Model | Arm | Named, all items | On the 15 / 9 flagged | On the 9 / 6 unflagged | Side B built | Built B unnamed | Core | $ est. mean |
|---|---|---|---|---|---|---|---|---|---|
| case006 (24) | Haiku | Markdown (r18) | 36.1 % | 13 / 45 (28.9 %) | 13 / 27 (48.1 %) | 11 / 72 | 7 | 87.6 % | 0.46 |
| | | **compiler export** | **88.9 %** | **45 / 45 (100 %)** | **19 / 27 (70.4 %)** | 6 / 72 | 1 | **97.3 %** | 1.44 |
| | | oracle export (r18) | 100 % | 45 / 45 | 27 / 27 | 7 / 72 | 0 | 91.8 % | 1.22 |
| | | review list (r25) | 94.4 % | 41 / 45 | 27 / 27 | 2 / 72 | 0 | 91.2 % | 0.89 |
| | Sonnet | Markdown (r18) | 73.6 % | 27 / 45 (60.0 %) | 26 / 27 (96.3 %) | 4 / 72 | 1 | 98.6 % | 2.12 |
| | | **compiler export** | **97.2 %** | **45 / 45 (100 %)** | **25 / 27 (92.6 %)** | 30 / 72 | 0 | **98.2 %** | 2.28 |
| | | oracle export (r18) | 100 % | 45 / 45 | 27 / 27 | 28 / 72 | 0 | 98.4 % | 2.22 |
| | | review list (r25) | 90.3 % | 41 / 45 | 24 / 27 | 4 / 72 | 1 | 98.6 % | 2.02 |
| case010 (15) | Haiku | Markdown (r19) | 51.1 % | 13 / 27 (48.1 %) | 10 / 18 (55.6 %) | 15 / 45 | 9 | 89.8 % | 0.52 |
| | | **compiler export** | **82.2 %** | **26 / 27 (96.3 %)** | **11 / 18 (61.1 %)** | 18 / 45 | 1 | **92.3 %** | 0.88 |
| | | oracle export (r19) | 95.6 % | 25 / 27 | 18 / 18 | 18 / 45 | 0 | 91.9 % | 0.98 |
| | | review list (r25) | 86.7 % | 21 / 27 | 18 / 18 | 16 / 45 | 6 | 92.5 % | 0.62 |
| | Sonnet | Markdown (r19) | 66.7 % | 18 / 27 (66.7 %) | 12 / 18 (66.7 %) | 10 / 45 | 6 | 97.1 % | 1.44 |
| | | **compiler export** | **84.4 %** | **24 / 27 (88.9 %)** | **14 / 18 (77.8 %)** | 25 / 45 | 1 | **97.5 %** | 1.68 |
| | | oracle export (r19) | 93.3 % | 24 / 27 | 18 / 18 | 11 / 45 | 0 | 96.9 % | 1.57 |
| | | review list (r25) | 86.7 % | 21 / 27 | 18 / 18 | 6 / 45 | 6 | 96.3 % | 1.34 |

n = 3 per cell. "Flagged" / "unflagged" = the compiler export's flags, applied to every arm. Named per run:
case006 Haiku 22 · 22 · 20, Sonnet 24 · 23 · 23 (of 24); case010 Haiku 12 · 13 · 12, Sonnet 12 · 13 · 13 (of
15). Core per run: case006 Haiku 436, 435, 428, Sonnet 436, 438, 437 (of 445); case010 Haiku 163, 162, 154,
Sonnet 171, 166, 169 (of 173). Turns: case006 Haiku 50–96, Sonnet 25–29; case010 Haiku 46–54, Sonnet 19–30.
**Cost $18.89 est.** for 12 runs.

## Findings

1. **The compiler export raises naming where it flags, on all three cases.** On the flagged items naming
   went from 28.9 / 48.1 % to 100 / 96.3 % (Haiku, case006 / case010) and from 60.0 / 66.7 % to 100 /
   88.9 % (Sonnet); case016 (round 21): 72 → 100 %, 70 → 87 %. Over all items the compiler export sits
   between the Markdown and the oracle export in all 4 cells (82.2–97.2 %).
2. **On the unflagged items the change is small and mixed:** Haiku +22.3 (case006) and +5.5 points
   (case010), Sonnet −3.7 and +11.1; case016 −6 and 0. The flagged-item gains are +48 to +71 (Haiku)
   and +22 to +40 points (Sonnet). Sonnet named case006's unflagged items at 96 % already from the Markdown.
3. **A flag with the wrong rationale still does not help Sonnet.** case010's C18 (flagged as emoticon
   case) was named in 0 of 3 Sonnet runs; 2 of 3 Haiku runs named it by stating the default ("on by
   default") inside or beside the flag. The Sonnet flagged-item rate (88.9 %) is those 3 misses.
4. **No flagged conflict was built on side B unnamed** (0 of 144 flagged readings: 90 case006, 54 case010); the 3 unnamed
   side-B builds are unflagged items (case010 C05, C13; case006 C06). Sonnet case006 built side B on
   30 of 72 readings, all named (rule "the Interface Contract wins"), as its oracle-export runs did (28).
5. **Core: no harm; Haiku case006 is high.** Sonnet within 0.4 points of the Markdown in both cases. Haiku
   97.3 % on case006 is above every other case006 Haiku arm (Markdown 87.6, oracle 91.8, review list
   91.2 %), with runs 96.2–98.0 % against the Markdown's 86.1–90.1 %. This round ran a week after round 18
   and alone (round 25 ran beside round 24); time is a confound and n = 3. Not read as a format effect.

**What this does not show.** n = 3 per cell; one non-blind reader (reader 2 not yet run on these runs); the
other arms ran in rounds 18, 19 and 25, not interleaved with this round.

## Files

| Path | Tracked | What |
|---|---|---|
| `TRIAL.md`, `trial.env`, `queue.tsv`, `run_queue.log` | yes | Description, conditions, queue, driver log |
| `notes/compiler_store.py`, `notes/phases.sh`, `notes/check_nop.sh`, `notes/<case>/` | yes | Store script, launcher, do-nothing check, copied verdicts/recall/plant |
| `runs/<run_id>/` | yes | Run files |
| `work/` | **no** | Compiler stores, exports, tasks (hidden tests), Harbor jobs |

**Reader 2** (2026-11-16, `r26-second-reader-detection/notes/reader2.py read r27`, blind): 234 conflict readings,
agreement 0.991, κ 0.954 (reader 1 yes 209, reader 2 yes 211). The 2 disagreements
(case010 C18 in two runs) were re-read: only the emoticon clash is stated, never side A (preservation on by
default), so reader 1 holds. Round 27b (`r27b-zero2repo-haiku-topup-case{006,010}/`) added 2 Haiku runs per
arm on 2026-11-16/17.
