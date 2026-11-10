# r24-zero2repo-case016-settled-list

> Opened 2026-11-09. State: **closed** 2026-11-10 (8 of 8 runs scored). Approved by the owner 2026-11-09: "do all A-B-C-D by yourself and
> report the results to me" (A = the filtered and settled list proposed after round 23). Update this file at every step.

## Question

Given the review list **filtered** (false entries struck) and **settled** (a ruling on each entry), does a
coding agent build the side each ruling names — including the planted side B — and does the misleading
build of round 23 (probe G01) disappear?

*Why:* round 23 showed that an unfiltered review list carries the naming gain but also its errors (one
false entry changed what 5 of 8 runs built). The proposed pipeline is review → a person strikes false
entries and rules → the agent builds from the settled list. This round tests the last step.

## Design

A fifth arm for round 21's case016, under round 21's conditions (as round 23).

| Item | Value |
|---|---|
| Case | Zero2Repo case016, round 21's planted spec (17 conflicts, 15 scored gaps; G01 reported apart) |
| Arm | **Settled list**: round 21's Markdown task, `spec/` unchanged, plus `spec/RULINGS.md` |
| The list | Round 23's list (`r22-haiku-case016-1`'s `CONFLICTS.md`, kept as `work/review-list-r22-haiku-case016-1.md`), with entries 7 (zero-width), 19 (model-dialect two hits) and 20 (welcome) **struck** — the three false entries of round 22's reading — and a `**Ruling:**` line added to each of the other 17; renumbered 1–17, entry text otherwise verbatim. Rulings recorded **on the owner's behalf** by Claude (the owner delegated this step) |
| Rulings, fixed before any run | The 15 planted entries in list order alternate side A, side B, A, ...: **side B ruled** for C06, C25, C16, C21, C08, C18, C23 (7); **side A ruled** for C09, C01, C15, C13, C20, C17, C19, C22 (8). The two real original disagreements (pdf rows; number of file operands) are ruled as the original spec reads. C11 and C12 are not in the list |
| Instruction | Round 23's, with its list sentence replaced by: "`spec/RULINGS.md` lists places where those files disagree, each with the project owner's ruling; where it rules, build what the ruling says." (`diff -r` against round 23's task: that line, the list file, `task.toml`'s name) |
| Models, n | Haiku 5, Sonnet 3 |
| Conditions | `trial.env`: round 21's (Claude Code 2.1.316, no dollar ceiling, early-stop rerun at 194 of 388) |
| Measures | (1) **Ruled side built**: probe reading = the ruled side, per item, split side-A rulings / side-B rulings; against round 23 (unruled list), where side B was built 1 / 85 and 1 / 51. (2) **G01**: one hit (alternative) vs two hits; round 23 5 / 8 alternative, round 21 0 / 24. (3) Set 1 core / 338 (footprint tests of side-B rulings fail by design and are outside the core). (4) Set 2a named and 2b silent, as round 21, descriptive. (5) Cost |
| Scorer | Round 23's `notes/score.py`, `probe.sh`, `footprint.json`, `plant.py`, unchanged; `notes/detection.py` with the run prefix `r24-`; readings by the same one reader |

A ruling for side B makes the agent build what the hidden tests reject on that item's footprint tests;
those tests are outside the core by construction, so set 1 is not penalised by obeying a ruling.

## Inputs

| Step | Result |
|---|---|
| 1. Task | copied from round 23's; list → `RULINGS.md` by the script in this session (entries struck, rulings added); `diff -r` shows only the three expected differences |
| 2. Leak check | `grep -i -E "planted\|oracle\|answer key\|r2[0-9]\|\bC[0-9]{2}\b\|\bG[0-9]{2}\b"` on `RULINGS.md`: 0 matches |
| 3. Queue | 8 rows, Sonnet first as a check run, interleaved as round 23 |

## Runs

| Step | What | Result |
|---|---|---|
| Check run | `run_queue.sh … --one`: `r24-sonnet-settled-1`, 23:27–23:53 (-05:00), in parallel with round 25's check run | 363 / 388, core 333, 34 turns, $2.21 est.; 15 / 15 rulings built; G01 two hits; token in no file |
| Queue | the other 7, 23:54 (9 Nov) – 09:53 (10 Nov), in parallel with round 25 | 7 done, none retried, rerun or stopped early; paused 00:36–04:25 and 06:09–09:25 for the 5-hour window; token string in no saved file |
| Scores | `python3 notes/score.py runs/r24-*` → `notes/scores.json` | tests, core, probes for all 8 |
| Readings | one reader (Claude Code), every `NOTES.md` → `notes/readings.txt`; `python3 notes/detection.py` → `notes/detection.tsv` | 8 runs × 32 items |
| C25 check | the two Haiku runs whose probe read C25 upstream (settled-2, -4): their `app.tgz` run on the probe's two inputs, and on a hedge-stacking input | text + tailing negation: score 0 → 12 and 0 → 3, the only finding `17_tailing_negation`; hedge stacking (54) stays 0: the C25 ruling was stated in the notes but not built |
| Tables | `python3 notes/tables.py` (reads rounds 21, 23 and 24) → `notes/tables.json` | below; round 21's and 23's figures reproduce their `TRIAL.md` |

## Results

"Side-B items" are the 7 items whose ruling is side B (C06 C25 C16 C21 C08 C18 C23); "side-A items" the 8 ruled side A. For rounds 21 and 23, which had no rulings, the same columns count how often each side was built anyway.

| Model | Arm | Runs | Side B built on the 7 side-B items | Side A built on the 8 side-A items | Rulings built per run | G01 one hit | Silent / 15 | Core / 338, per run | Core mean | $ est. mean |
|---|---|---|---|---|---|---|---|---|---|---|
| Haiku | Markdown (r21) | 5 | 2 / 35 | 28 / 40 | — | 0 / 5 | 12.4 | | 312.8 | 0.79 |
| | compiler export (r21) | 5 | 1 / 35 | 27 / 40 | — | 0 / 5 | 12.4 | | 329.8 | 1.25 |
| | oracle export (r21) | 5 | 2 / 35 | 32 / 40 | — | 0 / 5 | 13.2 | | 326.8 | 1.36 |
| | review list (r23) | 5 | 0 / 35 | 39 / 40 | — | 2 / 5 | 12.8 | | 327.6 | 0.98 |
| | **settled list** | 5 | **33 / 35** | **40 / 40** | 15 · 14 · 15 · 14 · 15 | **0 / 5** | 12.8 | 321 · 325 · 330 · 315 · 313 | 320.8 | 0.80 |
| Sonnet | Markdown (r21) | 3 | 1 / 21 | 20 / 24 | — | 0 / 3 | 13.7 | | 333.0 | 2.13 |
| | compiler export (r21) | 3 | 2 / 21 | 17 / 24 | — | 0 / 3 | 14.0 | | 334.0 | 1.89 |
| | oracle export (r21) | 3 | 2 / 21 | 23 / 24 | — | 0 / 3 | 13.3 | | 331.7 | 1.78 |
| | review list (r23) | 3 | 0 / 21 | 23 / 24 | — | 3 / 3 | 13.3 | | 334.0 | 1.87 |
| | **settled list** | 3 | **21 / 21** | **24 / 24** | 15 · 15 · 15 | **0 / 3** | 12.3 | 333 · 332 · 327 | 330.7 | 1.97 |

**Rulings built: 118 of 120** (Haiku 73 / 75, Sonnet 45 / 45). The 2 misses are C25 in Haiku runs 2 and 4. Both runs' notes state the ruling and say it was built ("both forms weight zero"); their code still scores the tailing-negation form (C25 check above). So the miss is a coding slip against the agent's own notes, not a refusal of the ruling. All 7 side-B rulings were built in every other run.

**Named (set 2a), descriptive:** Haiku 16 · 15 · 14 · 14 · 15, Sonnet 16 · 2 · 16 of 17. With a ruling in hand, the strict rule partly measures note style: `r24-sonnet-settled-2` listed the 17 rulings by the ruled side only (not named under the strict rule) and built all 15; it is also the first run in any arm to name C12 (both sides). C11 was named in 3 of 8 runs (it is not in the list). Per run (tests / 388): Haiku 349, 352, 361, 344, 340; Sonnet 363, 360, 355. Turns: Haiku 27–42, Sonnet 22–34. **Cost: $9.91 est.** for 8 runs.

## Findings

1. **A settled list carries the owner's rulings into the code.** 118 of 120 rulings were built, including 54 of 56 rulings for the planted side B, which agents without a ruling built 0–2 times out of 21–35 per arm (rounds 21, 23). The 2 misses are one item (C25) in two Haiku runs, stated in the notes but not implemented.
2. **Striking a false entry removes the build it caused.** With the review list's three false entries struck, no run built G01's one-hit rule (0 / 8), against 5 / 8 with the unfiltered list (round 23) and 0 / 24 with no list (round 21).
3. **No cost on gaps; a small, uncertain cost on Haiku's core.** Silent inventions 12.8 and 12.3 of 15, as every arm. Sonnet's core 330.7 is inside round 21's arms (331.7–334.0); Haiku's 320.8 is below the export and review-list arms (326.8–329.8) and above the Markdown (312.8), with run ranges overlapping (313–330 vs 323–334). Following a side-B ruling makes those items' footprint tests fail, but the footprint is outside the core by construction.
4. **"Named" is the wrong measure once rulings are given.** One Sonnet run restated each ruling with one side only; what matters for a settled list is the build, which the probes read.

**What this does not show.** One case, one list, 8 runs; the rulings were recorded by Claude on the owner's behalf by a fixed alternation, not by a person weighing each conflict; the person's filtering step (striking 3 false entries) was done with knowledge of round 22's reading, so its accuracy for a person reading the list cold is not measured; one non-blind reader for the notes (the build reading is the probe's).

## Files

| Path | Tracked | What |
|---|---|---|
| `TRIAL.md`, `trial.env`, `queue.tsv`, `run_queue.log` | yes | Description, conditions, queue, driver log |
| `runs/<run_id>/` | yes | Run files, `NOTES.md`, `app.tgz`, `agent.tgz` |
| `notes/` | yes | Copied scorers (unchanged), readings, scores, tables |
| `work/` | **no** | The task (hidden tests, planted spec), the source list, Harbor jobs |
