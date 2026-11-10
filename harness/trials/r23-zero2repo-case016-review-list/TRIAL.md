# r23-zero2repo-case016-review-list

> Opened 2026-11-09. State: **closed** 2026-11-09 (8 of 8 runs scored). Approved by the owner 2026-11-09: "do #5 task as recommended"
> (the review-list arm proposed after round 22). Update this file at every step.

## Question

Does a coding agent given the Markdown plus a plain review's conflict list name the planted conflicts
as well as one given the compiler export?

*Why:* round 21 showed that agents name what is flagged; round 22 showed that a one-pass review flags
more planted conflicts than the compiler (15 of 17 in the list used here, against the compiler's 9),
at a tenth of the cost. If the review list carries the same help as the export's flags, the cheap
pipeline (review → list beside the Markdown) replaces the compiler for this purpose on specs of this
size.

## Design

A fourth arm for round 21's case016, run under round 21's conditions so its other three arms
(Markdown, compiler export, oracle export) are the comparison. Nothing else changes.

| Item | Value |
|---|---|
| Case | Zero2Repo case016, round 21's planted spec (17 conflicts, 16 gaps removed, 15 scored) |
| Arm | **Review list**: round 21's Markdown task, `spec/` unchanged, plus `spec/CONFLICTS.md` |
| The list | `r22-haiku-case016-1`'s `CONFLICTS.md`, verbatim. **Chosen by rule before any run:** the first Haiku review of case016 (Haiku is the compiler's model; first by run order, not by score). It flags 15 of the 17 planted conflicts (not C11, C12) and holds 5 other entries: 2 real disagreements of the original spec, 3 false. It was not filtered — the compiler export's 51 false contradictions were removed by verdicts (on the owner's behalf) before export |
| Instruction | Round 21's Markdown instruction with one sentence added after the spec line: "`spec/CONFLICTS.md` is a reviewer's list of places where those files disagree; it is not part of the specification." (`diff -r` against round 21's Markdown task: that line, the list file and `task.toml`'s name only) |
| Models, n | Haiku 5, Sonnet 3 (round 21's numbers per arm) |
| Conditions | `trial.env`: round 21's (Claude Code 2.1.316, no dollar ceiling, early-stop rerun at 194 of 388) |
| Measures | Round 21's, unchanged: set 1 core / 338; set 2a named / 17 (strict rule); set 2b silent / 15 (strict rule); which side built (probes) |
| Scorer | Round 21's `notes/score.py`, `probe.sh`, `footprint.json`, `plant.py`, copied unchanged; readings by the same one reader (Claude, not blind), in `notes/readings.txt` |

**Comparisons, fixed before any run.** (1) Named on all 17: review list against round 21's Markdown,
compiler export and oracle export. (2) Named on the 15 the list flags and on the 2 it does not (C11,
C12), as round 21 split the compiler's flagged / unflagged items. (3) Set 1 and set 2b as descriptive
non-inferiority readings. (4) Cost and turns.

## Inputs

| Step | Command | Result |
|---|---|---|
| 1. Task | copy `../r21-…/work/tasks/case016-r21-markdown` → `work/tasks/case016-r23-review-list`; add the list; one instruction sentence; `task.toml` name | `diff -r` against round 21's Markdown task: only those three differences |
| 2. Leak check | `grep -i -E "planted\|oracle\|answer key\|r2[0-9]\|\bC[0-9]{2}\b\|\bG[0-9]{2}\b"` on the list | 0 matches |
| 3. Queue | `queue.tsv` | 8 rows, Sonnet first as a check run, then interleaved |

## Runs

| Step | What | Result |
|---|---|---|
| Check run | `run_queue.sh … --one`: `r23-sonnet-review-1`, 06:23–06:41 (-05:00) | 370 / 388, 16 turns, $1.83 est.; `NOTES.md` saved; token string in no file. Scorer (`notes/score.py`, unchanged from round 21) ran on it: core 336 / 338 |
| Queue | the other 7, 06:41–17:06 | 7 done, none retried or rerun; paused 08:26–16:05 for the subscription's 7-day window (0.91 after the check run), as the driver is built to do; token string in no file |
| Scores | `python3 notes/score.py runs/r23-*` → `notes/scores.json` | tests, core, probes for all 8 |
| Readings | one reader, every `NOTES.md` in full → `notes/readings.txt`; `python3 notes/detection.py` → `notes/detection.tsv` | 8 runs × 32 items |
| Tables | `python3 notes/tables.py` (reads round 21's and this round's files) → `notes/tables.json` | below; round 21's figures reproduce the interim report's §4.9 exactly |

## Results

| Model | Arm | Runs | Named / 17 per run | Named, all 17 | On the 15 the list flags | On C11, C12 | Side B built | Silent / 15, mean | Core / 338, mean | $ est., mean |
|---|---|---|---|---|---|---|---|---|---|---|
| Haiku | Markdown (r21) | 5 | 10 · 10 · 11 · 12 · 12 | 64.7 % | 70.7 % | 2 / 10 | 14 / 85 | 12.4 | 312.8 | 0.79 |
| | compiler export (r21) | 5 | 13 · 14 · 13 · 14 · 13 | 78.8 % | 82.7 % | 5 / 10 | 14 / 85 | 12.4 | 329.8 | 1.25 |
| | oracle export (r21) | 5 | 16 × 5 | 94.1 % | 100 % | 5 / 10 | 10 / 85 | 13.2 | 326.8 | 1.36 |
| | **review list** | 5 | 15 · 16 · 15 · 15 · 15 | **89.4 %** | **100 %** | 1 / 10 | **1 / 85** | 12.8 | 327.6 | 0.98 |
| Sonnet | Markdown (r21) | 3 | 11 · 11 · 14 | 70.6 % | 73.3 % | 3 / 6 | 5 / 51 | 13.7 | 333.0 | 2.13 |
| | compiler export (r21) | 3 | 15 · 11 · 15 | 80.4 % | 84.4 % | 3 / 6 | 9 / 51 | 14.0 | 334.0 | 1.89 |
| | oracle export (r21) | 3 | 13 · 16 · 15 | 86.3 % | 91.1 % | 3 / 6 | 3 / 51 | 13.3 | 331.7 | 1.78 |
| | **review list** | 3 | 16 · 17 · 16 | **96.1 %** | **100 %** | 4 / 6 | **1 / 51** | 13.3 | 334.0 | 1.87 |

Per run (tests / 388, core / 338): Haiku 367 / 329, 349 / 315, 369 / 334, 369 / 331, 363 / 329; Sonnet
370 / 336, 373 / 337, 365 / 329. Turns: Haiku 31–52, Sonnet 16–22. The two side-B builds are both C20
(environment level over the stored level: the list states both sides; these runs chose the IC).

**What the list's false entries did.** The list's entry "model-dialect needs two hits vs FP-01 states
no such condition" is false (PRD 102 says two hits too). **5 of 8** review-list runs built one hit
(probe G01 reads the alternative: Sonnet 3 of 3, Haiku 2 of 5); in round 21's three arms **0 of 24**
did. G01's tests are outside the core (G01 was reported apart in round 21), so the core does not show
it. The other two false entries (zero-width characters, the welcome) were resolved the spec's way.

## Findings

1. **The review list carried the flag effect at least as well as the oracle export.** Every run named
   all 15 listed conflicts (100 %, both models), as the oracle export did for Haiku and better than it
   did for Sonnet (91.1 %). Over all 17: 89.4 % and 96.1 %, against the compiler export's 78.8 % and
   80.4 % and the Markdown's 64.7 % and 70.6 %.
2. **The help is item by item, as in round 21.** On the 2 unlisted items, the list arm did no better
   than the Markdown (Haiku 1 / 10 vs 2 / 10; Sonnet 4 / 6 vs 3 / 6).
3. **Fewer planted sides built.** 1 / 85 (Haiku) and 1 / 51 (Sonnet) against 5–14 in round 21's arms.
   The list states both sides with their locations and every run argued its choice (often "two
   statements against one" or the IC deferring to the PRD).
4. **No cost on code or on gaps.** Core 327.6 and 334.0 (in the range of round 21's export arms);
   silent inventions 12.8 and 13.3 of 15 (as every arm: the list carries no gap flag).
5. **Cheaper than the compiler route.** One review ($0.08 est. for the list used) plus the coding run,
   against a compile ($3.58 est.) plus 51 verdicts recorded before export (on the owner's behalf) plus the coding run; the coding runs
   themselves cost about the same ($0.98 Haiku against $1.25 from the compiler export).
6. **An unfiltered list can mislead.** One false entry changed what 5 of 8 runs built. The compiler
   route had every contradiction judged before export; the review list was used as it came.

**What this does not show.** One case, one list (chosen by rule), 8 runs; one non-blind reader. The
list flagged 15 of 17 because round 22 found them; a list with lower recall would help less, by
finding 2. Filtering the list before use (as the compiler export was filtered by verdicts) was not tried.

## Files

| Path | Tracked | What |
|---|---|---|
| `TRIAL.md`, `trial.env`, `queue.tsv`, `run_queue.log` | yes | Description, conditions, queue, driver log |
| `runs/<run_id>/` | yes | Run files, `NOTES.md`, `app.tgz`, `agent.tgz` |
| `notes/` | yes | Copied scorers (unchanged), readings, scores |
| `work/` | **no** | The task (with hidden tests and the planted spec), Harbor jobs |
