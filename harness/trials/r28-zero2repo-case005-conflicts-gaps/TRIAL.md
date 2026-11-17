# r28-zero2repo-case005-conflicts-gaps

> Opened 2026-11-11 by Claude Code. State: **closed 2026-11-17** (32 of 32 runs scored, read by reader 1 and reader 2; Steps 5–6).
> Round 28 of `docs/MIA5150-Project/extra-trials-plan.md`, first of its three new cases.
> Owner, 2026-11-11: "should we start the rest of round r27? if yes, run r27. if not, start planting
> round 28" — round 27b was not run (7-day window at 0.44; the plan recommends skipping it), so planting
> started. **Go-ahead for the model calls, 2026-11-11:** "Agree on your suggestion and 3 questions. Go
> ahead with round 28. Update final report and notify me when r28 done" — three new cases (case005,
> case011, case001); margins confirmed (core δ Sonnet 2, Haiku 5 points; silent invention δ 2 gaps);
> the compile, the reviews and the 32 coding runs approved.

## Question

As round 21 (case016), on a fourth case — Zero2Repo **case005** (`httpwire`, upstream `h11`; 7 915
words; **395** hidden tests) — with conflicts and gaps planted in one spec, in four arms (Markdown,
compiler export, oracle export, review list):

1. compiler recall and review recall on the planted conflicts (no agent);
2. set 1, core: does any arm make the code worse than the Markdown;
3. set 2a, conflicts named (strict rule of rounds 17–21);
4. set 2b, silent inventions on the gaps (round 20's strict rule; lower is better).

## Design

Round 21's, unchanged (its TRIAL.md, "Design"): candidates from hidden-test **names** only (no test body
opened); one alternative copy and one black-box probe per candidate; footprint measured with Harbor's
no-model oracle agent; kept = footprint 1–3, no test shared by two kept items; answer key written before
any compile or run. Plan §3: four arms, Haiku 5 and Sonnet 3 runs per arm (32 coding runs), reviews
Haiku 3 + Sonnet 3, the first Haiku review becomes the review list.

## Step 0: set up (2026-11-11, no model call)

| Item | Done |
|---|---|
| Folder | `bash new_trial.sh r28-zero2repo-case005-conflicts-gaps "…"` |
| Scripts | from round 21: `build_task.py` (unchanged), `check_nop.sh`, `footprint.sh` (case005 task name), `footprint.py`; new for case005: `sides.py`, `probe.py`, `probe.sh`, `plant.py` |
| `work/base-app` | round 13b `haiku-case005-1` `app.tgz` (395 / 395, official 1.0) |
| Original task | `python3 notes/build_task.py case005 ../work/tasks/case005-markdown-orig` (spec words 7 915) |

## Step 1: candidates, alternative builds, probes, footprint (2026-11-11, no model call)

| Step | Result |
|---|---|
| Test names | `pytest --collect-only` (pytest 8.4.1, `python:3.13-slim-bookworm`, base build mounted): **395** names (F01–F07), kept in the session scratchpad |
| Candidates | **21 conflicts** (C01–C21) and **17 gaps** (G01, G03, G05–G09, G14, G16, G21, G22, G31, G33, G34, G47–G49), each matched to the sentences that state the fact |
| Alternative builds | `python3 notes/sides.py work/base-app work/sides` → 38 copies, every anchor once |
| Probe check | `bash work/probe_check.sh` → `work/probe_check.log`: **base A on all 38; each copy B on its own item, A on the other 37: 0 mismatches** (first pass: 3 probe faults, fixed in the probes — C07's probe was case-sensitive; C11's copy drops `Content-Length: 0`, which made two other probes' empty responses close-delimited, so those probes now send a 2-byte body) |
| Footprint | `bash notes/footprint.sh BASE …` (two streams, about 22 s per run), `python3 notes/footprint.py` → `notes/footprint.json`. BASE **395 / 395** on this round's task. Over 3: C17 (11), C19 (9), G01 (27), G05 (5); 0: G31. Shared test: C07, C08 and G47 (`host_is_written_before_foo_even_when_not_first`) |
| Still stated after removal (read in the spec) | G03, G07, G08 (`ANSWER_KEY.md`) |
| **Kept** | **17 conflicts** (C01–C06, C09–C16, C18, C20, C21) and **11 gaps** (G06, G09, G14, G16, G21, G22, G33, G34, G47, G48, G49); footprint union **60**, none shared; **core 335** |

## Step 2: plant and remove (2026-11-11, no model call)

| Item | Result |
|---|---|
| Plant | `python3 notes/plant.py work/spec-planted <28 ids>`: 33 edits; every A and B phrase once; no gap key phrase left; 7 915 → 7 916 words |
| sha256 | `work/spec-planted.sha256` (in `ANSWER_KEY.md`) |
| Answer key | `ANSWER_KEY.md`, written before any compile, review or run |

## Step 3: compile, verdicts, exports (2026-11-11)

| Step | Result |
|---|---|
| Compile | `nohup setsid bash notes/compile_full.sh &` started 16:10 -> **done** 2026-11-11 21:34 (-05:00), 4 passes (pass 1 stopped at the 300-call cap; pass 3 waited out the 5-hour usage limit until 21:05): **425 calls, $2.36 est.** (sum of the passes' `cost_usd`); 522 nodes; conflicts: 40 duplication, **48 contradiction**, 9 subsumption |
| Recall | `python3 notes/recall.py work/compile-full` → `notes/recall.json`: **7 of 17** (C03, C05, C06, C10, C13, C20, C21). Missed: C01, C02, C04, C09, C11, C12, C14, C15, C16, C18. `FIND` set for C11 (side B reworded in its node) |
| Verdicts | `python3 notes/verdicts.py list work/compile-full`, then `notes/verdicts.tsv`: 48 contradictions: 7 planted pairs (left open); 41 read one by one against the original spec (no earlier case005 compile): **2 left open** (CF-000075, CF-000076: planted C04 side B against two other sentences stating side A), **39 false**. Rule for a real clash a planted sentence makes with an original sentence that is not side A: left open (true contradiction), but it does not count as flagging the item (round 21's rule: a flag counts only when the other sentence states side A) |
| Compiler export | copy to `work/compile-compiler`, `verdicts.py apply`, `sddc --root work/compile-compiler export --allow-open --out work/export-compiler`: 20 packs, 522 nodes, **9 unsettled**; flagged: the 7 found plus **C04** (CF-000075/076) = **8 of 17** |
| Oracle export | copy to `work/compile-oracle`, `python3 notes/oracle_store.py work/compile-oracle` (`RATIONALE` for the misses, judge's voice), export to `work/export-oracle`: **10 injected** (C01, C02, C04, C09, C11, C12, C14, C15, C16, C18 → CF-000098…CF-000107); 19 unsettled; **17 of 17 flagged** |
| Leak checks | both exports: no `planted`, `answer key`, `oracle`, `gap`, `r28`, token prefix; no gap key phrase; both sides of every kept conflict present |

## Step 4: tasks and checks

| Step | Result |
|---|---|
| Export tasks | `build_task.py case005 ../work/tasks/case005-r28-export-compiler ../work/export-compiler` and `…-export-oracle` (spec words compiler 23 189, oracle 23 945 (spec words of the tasks)) |
| Review-list task | `python3 notes/review_list_task.py`: the Markdown task plus `spec/CONFLICTS.md` = `../r28-zero2repo-reviews/runs/r28-haiku-review-case005-1/CONFLICTS.md` verbatim, and round 23's sentence; leak check (`planted|oracle|answer key|Cnn|Gnn|CF-`): 0 |
| `diff -r` | Markdown vs. compiler export: the spec folder, the instruction's one spec line, `task.toml` name/description. Compiler vs. oracle export: `export.meta.json`, `MAP.md` and packs only (the injected conflicts). Markdown vs. review list: the list file, the one added sentence, `task.toml` |
| Do-nothing checks (all four tasks) | reward 0 each |
| Scorer dry run | `score()` on the base build: full score, full core, every item `upstream` |
| Markdown task | `SPEC_DIR=../work/spec-planted python3 build_task.py case005 ../work/tasks/case005-r28-markdown` (spec words 7 916) |
| Do-nothing check | `bash notes/check_nop.sh case005-r28-markdown`: **0 / 395** |
| Reviews | Haiku 3 + Sonnet 3 in `../r28-zero2repo-reviews/` (round 22's task builder and instruction) |
| `trial.env` | Claude Code 2.1.316, no budget cap, `RUN_TIMEOUT=9000`, `EARLYSTOP_RERUN=1`, `EARLYSTOP_MIN_PASSED=198` |
| Scorer | `notes/score.py` (round 21's, for 395 tests; maps this round's probe output A / B to upstream / alternative) |

## Step 5: coding runs (2026-11-11 to 2026-11-16)

32 of 32 runs done (`queue.tsv`, `run_queue.log`). The drivers stopped on 12 Nov (Docker EOF) and were
restarted on 16 Nov 18:07; the rows that had failed reran as attempt 2 and succeeded.

## Step 6: scores, readings and results (2026-11-16 to 2026-11-17, no model call except reader 2)

Scored by `notes/score.py` (tests, core, built sides by probe), read by reader 1 into `notes/readings.txt`
(strict rule; gaps flagged only when named as unstated with the value), `notes/detection.py` →
`notes/detection.tsv`, `notes/tables.py` → `notes/tables.json`. Core of 335; 17 conflicts;
11 gaps. Silent = gaps whose value the code takes while the notes do not name it as unstated.

| Model | Arm | n | Core mean (range) | Named (per run) | Silent mean (per run) | Gaps flagged per run | $ est. per run |
|---|---|---|---|---|---|---|---|
| haiku | markdown | 5 | 335.0 (335–335) | 87.1 % (15 · 14 · 16 · 15 · 14) | 9.20 (9 · 8 · 10 · 9 · 10) | 2 · 3 · 1 · 2 · 1 | 0.41–0.57 |
| haiku | compiler | 5 | 335.0 (335–335) | 85.9 % (14 · 15 · 16 · 16 · 12) | 8.40 (8 · 9 · 9 · 8 · 8) | 3 · 2 · 2 · 3 · 3 | 0.51–0.91 |
| haiku | oracle | 5 | 335.0 (335–335) | 100.0 % (17 · 17 · 17 · 17 · 17) | 9.20 (10 · 9 · 9 · 9 · 9) | 1 · 2 · 2 · 2 · 2 | 0.69–1.03 |
| haiku | review | 5 | 333.6 (328–335) | 92.9 % (16 · 16 · 16 · 16 · 15) | 8.80 (8 · 10 · 10 · 8 · 8) | 3 · 1 · 1 · 3 · 3 | 0.45–0.64 |
| sonnet | markdown | 3 | 335.0 (335–335) | 82.4 % (14 · 13 · 15) | 9.33 (9 · 9 · 10) | 2 · 2 · 1 | 0.62–0.63 |
| sonnet | compiler | 3 | 335.0 (335–335) | 78.4 % (14 · 13 · 13) | 10.33 (10 · 11 · 10) | 1 · 0 · 1 | 0.65–0.75 |
| sonnet | oracle | 3 | 335.0 (335–335) | 100.0 % (17 · 17 · 17) | 10.33 (10 · 11 · 10) | 1 · 0 · 1 | 0.68–0.76 |
| sonnet | review | 3 | 335.0 (335–335) | 92.2 % (15 · 16 · 16) | 9.33 (11 · 9 · 8) | 0 · 1 · 3 | 0.59–0.72 |

31 of 32 runs passed the whole core. Core 335 of 335 in 31 of 32 runs (one Haiku review-list run 328). The compiler export flags only 8 of 17 and named no more than the Markdown (Haiku 85.9 against 87.1 %, Sonnet 78.4 against 82.4 %); on its 8 flagged items naming was 100 % in both models, on the 9 unflagged it fell (Haiku 80 to 73 %, Sonnet 70 to 59 %). The review list's unlisted C12 and C18 gained nothing (Haiku 4 of 10 readings in both arms). Reader 2 disagreed on one reading (`haiku-compiler-5` C04: the notes state CF-000075/076, joined against refused): reader 1 holds.

**Reader 2** (`r26-second-reader-detection/notes/reader2.py`, round key `r28a`): 544 conflict
readings, agreement 0.998, κ 0.990 (reader 1 yes 491, reader 2 yes 490).

## Files

| Path | Tracked | What |
|---|---|---|
| `TRIAL.md`, `ANSWER_KEY.md`, `trial.env`, `queue.tsv` | yes | Description, answer key, conditions, queue |
| `notes/` | yes | Scripts, `footprint.json` |
| `work/` | **no** | Base build, alternative copies, tasks (hidden tests), planted spec, Harbor jobs, probe outputs |
