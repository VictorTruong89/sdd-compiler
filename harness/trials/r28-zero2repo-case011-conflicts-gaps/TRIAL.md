# r28-zero2repo-case011-conflicts-gaps

> Opened 2026-11-11 by Claude Code. State: **closed 2026-11-17** (32 of 32 runs scored, read by reader 1 and reader 2; Steps 5–6).
> Round 28 of `docs/MIA5150-Project/extra-trials-plan.md`, second of its three new cases. Owner's go-ahead,
> 2026-11-11: "Agree on your suggestion and 3 questions. Go ahead with round 28. Update final report and
> notify me when r28 done" — three new cases; margins confirmed (core δ Sonnet 2, Haiku 5 points;
> silent invention δ 2 gaps); the compile, the reviews and the 32 coding runs of each case approved.

## Question

As round 21 (case016) and round 28's case005, on Zero2Repo **case011** (`pathsel`, upstream `jmespath.py`; 7 002
words; **321** hidden tests), with conflicts and gaps planted in one spec, in four arms (Markdown,
compiler export, oracle export, review list): compiler and review recall on the planted conflicts; set 1
core (no arm worse than the Markdown); set 2a conflicts named (strict rule of rounds 17–21); set 2b silent
inventions on the gaps (round 20's strict rule).

## Design

Round 21's, unchanged (its TRIAL.md, "Design"); case005's TRIAL.md for this round. Plan §3: four arms,
Haiku 5 and Sonnet 3 runs per arm (32 coding runs; threshold half of 321 = 161); reviews Haiku 3 +
Sonnet 3 in `../r28-zero2repo-reviews/`, the first Haiku review becomes the review list.

## Step 0: set up (2026-11-11, no model call)

| Item | Done |
|---|---|
| Folder | `bash new_trial.sh r28-zero2repo-case011-conflicts-gaps "…"` |
| Scripts | from case005: `build_task.py` (unchanged), `check_nop.sh`, `footprint.sh`, `footprint.py`, `probe.sh`, `compile_full.sh`, `score.py` (case name, test total, keywords); new for case011: `sides.py`, `probe.py`, `plant.py` |
| `work/base-app` | round 13b `haiku-case011-1` `app.tgz` (321 / 321, official 1.0) |
| Original task | `python3 notes/build_task.py case011 ../work/tasks/case011-markdown-orig` (spec words 7 002) |

## Step 1: candidates, alternative builds, probes, footprint (2026-11-11, no model call)

| Step | Result |
|---|---|
| Test names | `pytest --collect-only` (pytest 8.4.1, `python:3.13-slim-bookworm`, base build mounted): **321** names, kept in the session scratchpad; no test body opened |
| Candidates | **27 conflicts** (C01–C27) and **14 gaps** (G03, G04, G07, G22, G25, G27, G28, G29, G34, G35, G54, G60, G61, G69), each matched to the sentences that state the fact; `python3 notes/sides.py work/base-app work/sides` → 41 copies, every anchor once |
| Probe check | `bash work/probe_check.sh` → `work/probe_check.log`: **0 mismatches** (first pass: 1 probe fault — G69's probe used a custom function, which the C23 copy refuses at compile time; it now uses a mapping type) |
| Footprint | `bash notes/footprint.sh BASE …` (Harbor oracle agent, no model; two streams), `python3 notes/footprint.py` → `notes/footprint.json`; BASE **321 / 321** |
| Selection | footprint 1–3, none shared; overlap rule of rounds 20–21 (drop the larger footprint; on a tie drop from the kind with more survivors) |
| **Kept** | **12 conflicts** (C02, C05, C08, C12, C14, C15, C17, C19, C20, C22, C24, C26) and **12 gaps** (G03, G22, G25, G27, G28, G29, G34, G35, G54, G60, G61, G69); footprint union **50**, none shared; **core 271** (`ANSWER_KEY.md`, dropped candidates with reasons) |

## Step 2: plant and remove (2026-11-11, no model call)

| Item | Result |
|---|---|
| Plant | `python3 notes/plant.py work/spec-planted <kept ids>`: 28 edits for 24 items; every A and B phrase once; no gap key phrase left; 7 002 → 6 909 words |
| sha256 | `work/spec-planted.sha256` (in `ANSWER_KEY.md`) |
| Answer key | `ANSWER_KEY.md`, written before any compile output, review or run was read |

## Step 3: compile, verdicts, exports (2026-11-11)

| Step | Result |
|---|---|
| Compile | `nohup setsid bash notes/compile_full.sh &` started 16:27 -> **done** 2026-11-11 21:06 (-05:00), 4 passes (pass 1 at the call cap; pass 3 waited out the usage limit): **340 calls, $1.80 est.** (sum of the passes' `cost_usd`); 423 nodes; conflicts: 28 duplication, **25 contradiction**, 0 subsumption |
| Recall | `python3 notes/recall.py work/compile-full` → `notes/recall.json`: **7 of 12** (C05, C08, C12, C14, C15, C17, C19). Missed: C02, C20, C22, C24, C26. `FIND` set for C02 and C22 |
| Atomizer omission (compiler defect, recorded, not fixed) | **C24's side B is in no node**: its Terminology table row (block B-000025, PRD 37) was atomized into no node, as round 21's C12. The packs still print the block's text, so the agent sees side B; the conflict check cannot reach it and the oracle cannot inject it. C24 is **unflagged in both export arms** and stays in set 2a |
| Verdicts | `python3 notes/verdicts.py list work/compile-full`, then `notes/verdicts.tsv`: 25 contradictions: 7 planted pairs (open); 18 read one by one: **18 false**, none open. Rule for a real clash a planted sentence makes with an original sentence that is not side A: left open (true contradiction), but it does not count as flagging the item (round 21's rule: a flag counts only when the other sentence states side A) |
| Compiler export | copy to `work/compile-compiler`, `verdicts.py apply`, `sddc --root work/compile-compiler export --allow-open --out work/export-compiler`: 25 packs, 423 nodes, **7 unsettled**; **7 of 12 flagged** |
| Oracle export | copy to `work/compile-oracle`, `python3 notes/oracle_store.py work/compile-oracle` (`RATIONALE` for the misses, judge's voice), export to `work/export-oracle`: **4 injected** (C02, C20, C22, C26 → CF-000054…CF-000057); **C24 not injectable**; 11 unsettled; **11 of 12 flagged** |
| Leak checks | both exports: no `planted`, `answer key`, `oracle`, `gap`, `r28`, token prefix; no gap key phrase; both sides of every kept conflict present |

## Step 4: tasks and checks

| Step | Result |
|---|---|
| Export tasks | `build_task.py case011 ../work/tasks/case011-r28-export-compiler ../work/export-compiler` and `…-export-oracle` (spec words compiler 21 297, oracle 21 627) |
| Review-list task | `python3 notes/review_list_task.py`: the Markdown task plus `spec/CONFLICTS.md` = `../r28-zero2repo-reviews/runs/r28-haiku-review-case011-1/CONFLICTS.md` verbatim, and round 23's sentence; leak check (`planted|oracle|answer key|Cnn|Gnn|CF-`): 0 |
| `diff -r` | Markdown vs. compiler export: the spec folder, the instruction's one spec line, `task.toml` name/description. Compiler vs. oracle export: `export.meta.json`, `MAP.md` and packs only. Markdown vs. review list: the list file, the one added sentence, `task.toml` |
| Do-nothing checks (all four tasks) | reward 0 each |
| Scorer dry run | `score()` on the base build: full score, full core, every item `upstream` |
| Markdown task | `SPEC_DIR=../work/spec-planted python3 build_task.py case011 ../work/tasks/case011-r28-markdown` (spec words 6 909) |
| Do-nothing check | `bash notes/check_nop.sh case011-r28-markdown`: reward 0 (the judge collects no test when the package is missing) |
| `trial.env` | Claude Code 2.1.316, no budget cap, `RUN_TIMEOUT=9000`, `EARLYSTOP_RERUN=1`, `EARLYSTOP_MIN_PASSED=161` |

## Step 5: coding runs (2026-11-11 to 2026-11-16)

32 of 32 runs done (`queue.tsv`, `run_queue.log`). The drivers stopped on 12 Nov (Docker EOF) and were
restarted on 16 Nov 18:07; the rows that had failed reran as attempt 2 and succeeded.

## Step 6: scores, readings and results (2026-11-16 to 2026-11-17, no model call except reader 2)

Scored by `notes/score.py` (tests, core, built sides by probe), read by reader 1 into `notes/readings.txt`
(strict rule; gaps flagged only when named as unstated with the value), `notes/detection.py` →
`notes/detection.tsv`, `notes/tables.py` → `notes/tables.json`. Core of 271; 12 conflicts;
12 gaps. Silent = gaps whose value the code takes while the notes do not name it as unstated.

| Model | Arm | n | Core mean (range) | Named (per run) | Silent mean (per run) | Gaps flagged per run | $ est. per run |
|---|---|---|---|---|---|---|---|
| haiku | markdown | 5 | 270.2 (267–271) | 75.0 % (11 · 10 · 6 · 8 · 10) | 4.80 (5 · 3 · 7 · 5 · 4) | 7 · 9 · 5 · 7 · 8 | 0.35–0.57 |
| haiku | compiler | 5 | 271.0 (271–271) | 81.7 % (11 · 9 · 10 · 9 · 10) | 6.80 (7 · 8 · 8 · 7 · 4) | 5 · 4 · 4 · 5 · 8 | 0.64–0.83 |
| haiku | oracle | 5 | 270.2 (267–271) | 93.3 % (11 · 11 · 12 · 11 · 11) | 6.40 (6 · 6 · 6 · 7 · 7) | 6 · 6 · 6 · 5 · 5 | 0.66–0.90 |
| haiku | review | 5 | 259.0 (215–271) | 91.7 % (11 · 11 · 11 · 11 · 11) | 5.20 (5 · 6 · 3 · 5 · 7) | 7 · 6 · 9 · 7 · 5 | 0.35–0.50 |
| sonnet | markdown | 3 | 251.7 (215–271) | 52.8 % (6 · 6 · 7) | 10.00 (9 · 11 · 10) | 3 · 1 · 2 | 0.45–0.56 |
| sonnet | compiler | 3 | 271.0 (271–271) | 83.3 % (10 · 11 · 9) | 10.67 (11 · 11 · 10) | 1 · 1 · 2 | 0.59–0.60 |
| sonnet | oracle | 3 | 271.0 (271–271) | 100.0 % (12 · 12 · 12) | 10.00 (10 · 11 · 9) | 2 · 1 · 3 | 0.50–0.60 |
| sonnet | review | 3 | 269.7 (269–271) | 91.7 % (11 · 11 · 11) | 8.33 (8 · 8 · 9) | 4 · 4 · 3 | 0.44–0.51 |

24 of 32 runs passed the whole core. Two runs scored 215 of 271 core (`sonnet-markdown-3`, `haiku-review-4`): both failed the same 56 tests by giving an unfinished expression (`foo.`) a different error kind, one of the disagreements in Zero2Repo's own text that 4 of the 6 reviews found; not an arm effect. Haiku named 5–9 of 12 gaps as unstated in each run (Sonnet 1–4), in every arm. The review list's unlisted C19 was built on side B in all 8 review-list runs, as in all 8 Markdown runs. Reader 2 agreed on every reading.

**Reader 2** (`r26-second-reader-detection/notes/reader2.py`, round key `r28b`): 384 conflict
readings, agreement 1.000, κ 1.000 (reader 1 yes 323, reader 2 yes 323).

## Files

| Path | Tracked | What |
|---|---|---|
| `TRIAL.md`, `ANSWER_KEY.md`, `trial.env`, `queue.tsv` | yes | Description, answer key, conditions, queue |
| `notes/` | yes | Scripts, `footprint.json` |
| `work/` | **no** | Base build, alternative copies, tasks (hidden tests), planted spec, compile stores, exports, Harbor jobs |
