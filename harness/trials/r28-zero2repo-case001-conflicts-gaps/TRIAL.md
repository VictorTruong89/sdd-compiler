# r28-zero2repo-case001-conflicts-gaps

> Opened 2026-11-11 by Claude Code. State: **closed 2026-11-17** (32 of 32 runs scored, read by reader 1 and reader 2; Steps 5–6).
> Round 28 of `docs/MIA5150-Project/extra-trials-plan.md`, third of its three new cases. Owner's go-ahead,
> 2026-11-11: "Agree on your suggestion and 3 questions. Go ahead with round 28. Update final report and
> notify me when r28 done" — three new cases; margins confirmed (core δ Sonnet 2, Haiku 5 points;
> silent invention δ 2 gaps); the compile, the reviews and the 32 coding runs of each case approved.

## Question

As round 21 (case016) and round 28's case005, on Zero2Repo **case001** (`tomlparse`, upstream `tomli`; 4 860
words; **302** hidden tests), with conflicts and gaps planted in one spec, in four arms (Markdown,
compiler export, oracle export, review list): compiler and review recall on the planted conflicts; set 1
core (no arm worse than the Markdown); set 2a conflicts named (strict rule of rounds 17–21); set 2b silent
inventions on the gaps (round 20's strict rule).

## Design

Round 21's, unchanged (its TRIAL.md, "Design"); case005's TRIAL.md for this round. Plan §3: four arms,
Haiku 5 and Sonnet 3 runs per arm (32 coding runs; threshold half of 302 = 151); reviews Haiku 3 +
Sonnet 3 in `../r28-zero2repo-reviews/`, the first Haiku review becomes the review list.

## Step 0: set up (2026-11-11, no model call)

| Item | Done |
|---|---|
| Folder | `bash new_trial.sh r28-zero2repo-case001-conflicts-gaps "…"` |
| Scripts | from case005: `build_task.py` (unchanged), `check_nop.sh`, `footprint.sh`, `footprint.py`, `probe.sh`, `compile_full.sh`, `score.py` (case name, test total, keywords); new for case001: `sides.py`, `probe.py`, `plant.py` |
| `work/base-app` | round 13b `haiku-case001-1` `app.tgz` (302 / 302, official 1.0) |
| Original task | `python3 notes/build_task.py case001 ../work/tasks/case001-markdown-orig` (spec words 4 860) |

## Step 1: candidates, alternative builds, probes, footprint (2026-11-11, no model call)

| Step | Result |
|---|---|
| Test names | `pytest --collect-only` (pytest 8.4.1, `python:3.13-slim-bookworm`, base build mounted): **302** names, kept in the session scratchpad; no test body opened |
| Candidates | **27 conflicts** (C01–C19, C23, C25, C27–C29, C31, C35, C36) and **6 gaps** (G01, G03, G04, G05, G09, G13). Gap candidates are limited to product facts TOML v1.1.0 does not fix: the PRD makes TOML v1.1.0 the authority for the grammar, so a removed grammar fact stays stated by reference. `python3 notes/sides.py work/base-app work/sides`, every anchor once |
| Probe check | `bash work/probe_check.sh` → `work/probe_check.log`: **0 mismatches** (first pass: 4 mismatches from two pairs of candidates that were one fact — C23/G01 (C23 dropped) and C31/G09 (G09\'s first alternative, the default recursion limit, still parses depth 470; C31\'s nesting guard became G09\'s alternative); the C04 probe moved to a fraction that rounding and truncation tell apart. 30 final candidates) |
| Footprint | `bash notes/footprint.sh BASE …` (Harbor oracle agent, no model; two streams), `python3 notes/footprint.py` → `notes/footprint.json`; BASE **302 / 302** |
| Selection | footprint 1–3, none shared; overlap rule of rounds 20–21 (drop the larger footprint; on a tie drop from the kind with more survivors) |
| **Kept** | **15 conflicts** (C03, C04, C07, C08, C10, C11, C12, C13, C14, C16, C17, C18, C29, C35, C36) and **4 gaps** (G01, G03, G09, G13); footprint union **37**, none shared; **core 265** (`ANSWER_KEY.md`, dropped candidates with reasons) |

## Step 2: plant and remove (2026-11-11, no model call)

| Item | Result |
|---|---|
| Plant | `python3 notes/plant.py work/spec-planted <kept ids>`: 20 edits for 19 items; every A and B phrase once; no gap key phrase left; 4 860 → 4 801 words |
| sha256 | `work/spec-planted.sha256` (in `ANSWER_KEY.md`) |
| Answer key | `ANSWER_KEY.md`, written before any compile output, review or run was read |

**Shortfall.** Plan §3 targeted about 12 gaps per case; case001 yields 4 (TOML authority, above). Decision (Claude Code, 2026-11-11, before any model call): keep the written criteria and run with 15 + 4, as round 21 kept its 17 + 16; set 2b for case001 is reported over 4 gaps with that caveat, and the case-level equivalence test of claim 4 is computed with and without case001.

## Step 3: compile, verdicts, exports (2026-11-11)

| Step | Result |
|---|---|
| Compile | `nohup setsid bash notes/compile_full.sh &` started 16:27 -> **done** 2026-11-11 18:13 (-05:00), 1 pass: **279 calls, $1.45 est.** (sum of the passes' `cost_usd`); 323 nodes; conflicts: 31 duplication, **27 contradiction**, 12 subsumption |
| Recall | `python3 notes/recall.py work/compile-full` → `notes/recall.json`: **11 of 15** (C03, C04, C07, C08, C10, C11, C12, C13, C16, C18, C36). Missed: C14, C17, C29, C35. `FIND` set for C03 |
| Verdicts | `python3 notes/verdicts.py list work/compile-full`, then `notes/verdicts.tsv`: 27 contradictions: 11 planted pairs (open); 16 read one by one: **5 left open** (CF-000023: planted C29 side B against the Contract row stating side A; CF-000045: planted C04 side B against a second sentence stating side A; CF-000028, CF-000035, CF-000032: real clashes the planted C14 / C29 sentences make with other original sentences, not side A), **11 false**. Rule for a real clash a planted sentence makes with an original sentence that is not side A: left open (true contradiction), but it does not count as flagging the item (round 21's rule: a flag counts only when the other sentence states side A) |
| Compiler export | copy to `work/compile-compiler`, `verdicts.py apply`, `sddc --root work/compile-compiler export --allow-open --out work/export-compiler`: 15 packs, 323 nodes, **16 unsettled**; flagged: the 11 found plus **C29** (CF-000023) = **12 of 15** |
| Oracle export | copy to `work/compile-oracle`, `python3 notes/oracle_store.py work/compile-oracle` (`RATIONALE` for the misses, judge's voice), export to `work/export-oracle`: **4 injected** (C14, C17, C29, C35 → CF-000071…CF-000074); 20 unsettled; **15 of 15 flagged** |
| Leak checks | both exports: no `planted`, `answer key`, `oracle`, `gap`, `r28`, token prefix; no gap key phrase; both sides of every kept conflict present |

## Step 4: tasks and checks

| Step | Result |
|---|---|
| Export tasks | `build_task.py case001 ../work/tasks/case001-r28-export-compiler ../work/export-compiler` and `…-export-oracle` (spec words compiler 16 929, oracle 17 266) |
| Review-list task | `python3 notes/review_list_task.py`: the Markdown task plus `spec/CONFLICTS.md` = `../r28-zero2repo-reviews/runs/r28-haiku-review-case001-1/CONFLICTS.md` verbatim, and round 23's sentence; leak check (`planted|oracle|answer key|Cnn|Gnn|CF-`): 0 |
| `diff -r` | Markdown vs. compiler export: the spec folder, the instruction's one spec line, `task.toml` name/description. Compiler vs. oracle export: `export.meta.json`, `MAP.md` and packs only. Markdown vs. review list: the list file, the one added sentence, `task.toml` |
| Do-nothing checks (all four tasks) | reward 0 each |
| Scorer dry run | `score()` on the base build: full score, full core, every item `upstream` |
| Markdown task | `SPEC_DIR=../work/spec-planted python3 build_task.py case001 ../work/tasks/case001-r28-markdown` (spec words 4 801) |
| Do-nothing check | `bash notes/check_nop.sh case001-r28-markdown`: reward 0 (the judge collects no test when the package is missing) |
| `trial.env` | Claude Code 2.1.316, no budget cap, `RUN_TIMEOUT=9000`, `EARLYSTOP_RERUN=1`, `EARLYSTOP_MIN_PASSED=151` |

## Step 5: coding runs (2026-11-11 to 2026-11-16)

32 of 32 runs done (`queue.tsv`, `run_queue.log`). The drivers stopped on 12 Nov (Docker EOF) and were
restarted on 16 Nov 18:07; the rows that had failed reran as attempt 2 and succeeded.

## Step 6: scores, readings and results (2026-11-16 to 2026-11-17, no model call except reader 2)

Scored by `notes/score.py` (tests, core, built sides by probe), read by reader 1 into `notes/readings.txt`
(strict rule; gaps flagged only when named as unstated with the value), `notes/detection.py` →
`notes/detection.tsv`, `notes/tables.py` → `notes/tables.json`. Core of 265; 15 conflicts;
4 gaps. Silent = gaps whose value the code takes while the notes do not name it as unstated.

| Model | Arm | n | Core mean (range) | Named (per run) | Silent mean (per run) | Gaps flagged per run | $ est. per run |
|---|---|---|---|---|---|---|---|
| haiku | markdown | 5 | 265.0 (265–265) | 66.7 % (12 · 10 · 8 · 10 · 10) | 1.00 (1 · 2 · 0 · 2 · 0) | 3 · 2 · 4 · 2 · 4 | 0.06–0.10 |
| haiku | compiler | 5 | 265.0 (265–265) | 93.3 % (13 · 15 · 15 · 14 · 13) | 1.80 (2 · 2 · 2 · 1 · 2) | 2 · 2 · 2 · 3 · 2 | 0.17–0.56 |
| haiku | oracle | 5 | 264.8 (264–265) | 100.0 % (15 · 15 · 15 · 15 · 15) | 1.80 (2 · 1 · 0 · 3 · 3) | 2 · 3 · 4 · 1 · 1 | 0.23–0.63 |
| haiku | review | 5 | 265.0 (265–265) | 94.7 % (14 · 15 · 14 · 14 · 14) | 1.20 (1 · 1 · 1 · 2 · 1) | 3 · 3 · 3 · 2 · 3 | 0.05–0.09 |
| sonnet | markdown | 3 | 265.0 (265–265) | 42.2 % (7 · 6 · 6) | 3.00 (3 · 3 · 3) | 1 · 1 · 1 | 0.23–0.28 |
| sonnet | compiler | 3 | 263.7 (261–265) | 62.2 % (13 · 2 · 13) | 2.67 (3 · 2 · 3) | 1 · 2 · 1 | 0.23–0.35 |
| sonnet | oracle | 3 | 265.0 (265–265) | 93.3 % (13 · 14 · 15) | 3.00 (3 · 3 · 3) | 1 · 1 · 1 | 0.26–0.34 |
| sonnet | review | 3 | 265.0 (265–265) | 75.6 % (6 · 14 · 14) | 2.67 (3 · 2 · 3) | 1 · 2 · 1 | 0.23–0.31 |

30 of 32 runs passed the whole core. `sonnet-compiler-2` named only 2 of 15 and `sonnet-review-1` 6 of 15; they drive Sonnet's run spread on naming. Only 4 gaps, so little room for silent invention (1.0–3.0 per run). Reader 2 disagreed on 10 readings before adjudication; 2 were corrected (`haiku-markdown-1` and `haiku-review-2` C16, now named) and reader 1 holds the other 8.

**Reader 2** (`r26-second-reader-detection/notes/reader2.py`, round key `r28c`): 480 conflict
readings, agreement 0.983, κ 0.944 (reader 1 yes 389, reader 2 yes 395).

## Files

| Path | Tracked | What |
|---|---|---|
| `TRIAL.md`, `ANSWER_KEY.md`, `trial.env`, `queue.tsv` | yes | Description, answer key, conditions, queue |
| `notes/` | yes | Scripts, `footprint.json` |
| `work/` | **no** | Base build, alternative copies, tasks (hidden tests), planted spec, compile stores, exports, Harbor jobs |
