# r14-zero2repo-case006-conflicts

> Opened 2026-10-16. State: **closed 2026-10-16** (13 Haiku runs: 12 + 1 replacement). Approved by the owner 2026-10-16: "Run
> steps 0-4 as you recommend above. After conflicts builts, run trials as you suggested. After trials
> complete, note down all results finding and properly explain the conflict-building and testing
> methodology for future report writing." The recommendation is `sdd/design/rel-02/rel02_brainstorm.md`
> S17 (with the instruction line). Update this file at every step; a later session starts from it.

## Question

With conflicts planted in case006 by design (answer key written first):
1. Which planted conflicts does the compiler report? (recall; no agent)
2. Unsettled: does Haiku notice them, and which side does it build, from the Markdown vs from the export
   that lists them as `UNSETTLED`?
3. Settled: once the owner rules (all to the side that is not click's), does the ruling reach the code,
   from the settled export vs from the Markdown plus a plain `DECISIONS.md`?
4. Does planting change the rest of the build (core score)?

## Design

| Item | Value |
|---|---|
| Benchmark / case | Zero2Repo `0ecc523`, **case006** (click renamed Optlyn), 476 hidden tests; 7 conflicts planted (`ANSWER_KEY.md`); planted Markdown 14 237 words (14 138 before) |
| Cells (Haiku, n = 3 each) | round 2: **Markdown** (planted) · **export, unsettled** (`--allow-open`; the planted conflicts the compiler found are open) · round 3: **Markdown + `DECISIONS.md`** · **export, settled** (rulings as adjudications) |
| Model | Haiku (`anthropic/claude-haiku-5-5`) |
| Agent | Claude Code 2.1.296, Harbor 0.24.0, tools `Bash Edit Read Write`, allow-list (model API, PyPI); `trial.env` as 13c/13d ($10 ceiling, 9 000 s) |
| Instruction | 13d's, plus one line in every cell (owner's choice, S17): "If parts of the specification disagree, choose one and list each choice in `NOTES.md` (what disagrees, where, and what you built)." |
| Scorers | Zero2Repo's judge unchanged (official, per-test); **core score** = the 469 tests outside the footprint union; side probes; exposure; `NOTES.md` (`notes/score.py`) |
| Compile | incremental: round 13c's finished case006 store copied, the planted Markdown re-ingested (7 blocks changed, 458 unchanged), one `sddc compile` pass |
| Order | round 2 rows alternate Markdown / export, then round 3 rows alternate. Rounds are not interleaved: a time-of-day difference between rounds cannot be excluded |

## Method: how the conflicts were built

### Why designed, not random

A random edit can land where no test or probe looks, or in a feature some agents build badly (FP-09
tests failed in 7 of the 9 earlier case006 runs, FP-10 in 4), so "missed" cannot be told from "not
built"; it can break an unknown number of hidden tests; it is mostly a plain value swap, so the kinds
the compiler is known to miss (a rule inside a definition, an example against its rule; `lend`, rel02
S5) would be absent; and it cannot be balanced, so a result cannot be put down to distance or kind.
Each planted item is one cell of a small factor table (distance × kind), with the answer key written
before the compile and before any agent run, as for `lend` (`harness/tasks/lend-messy/ANSWER_KEY.md`).

### Selection rules (every kept item meets all)

1. **Built in every past run:** the tests nearest the touched behaviour (by name, in the judges'
   reports of the 9 earlier case006 runs) passed in all or all but one.
2. **Both sides observable:** each side gives a different black-box result, so a probe reads A, B,
   both, neither or error in every run.
3. **Narrow footprint, measured:** at most 3 hidden tests change result between side A and side B.
4. **Side A is click's behaviour:** what the hidden tests check and what the model may remember. An
   agent can land on A from memory without noticing anything, so a side is never read as detection,
   and every ruling picks B.
5. **Real drift:** one document edited, one sentence or row, in the spec's own voice, no marker.

### Steps (step 0 costs no model call)

1. **Side-B builds** (`notes/sides.py`). Base: round 13c's `sonnet-case006-export-1` (473 / 476),
   which takes A on every item. For each candidate, the smallest patch that moves that one behaviour
   to B; each anchor must occur exactly once.
2. **Probes** (`notes/probe.py`, `notes/probe.sh`), written from the answer key and the Contract's API
   only, run in a container with no network. Check: the base reads A on every item; each side-B copy
   reads B on its own item and A on the others. Passed for all kept items.
3. **Footprint without reading the tests** (`notes/footprint.sh`, `notes/footprint.py`): the hidden
   tests run through Harbor's oracle agent (a `solve.sh` that unpacks the build; no model) on the base
   and on each side-B copy. The tests whose result differs from the base are the item's footprint.
   The base reproduced its original 473 / 476.
4. **Plant** (`notes/plant.py`): the side-B sentence of each kept item into a copy of `public/`.
5. **Exposure phrases:** one phrase per side, each checked to occur exactly once in the planted
   Markdown (`ANSWER_KEY.md`).

### Candidates and footprints (step 0 result)

| Item | Distance | Kind | Footprint | Kept |
|---|---|---|---|---|
| P1 isolated filesystem kept or removed | same paragraph (control) | direct | 1 | yes |
| P2 deprecated command's warning: stderr or stdout | across files | prose vs table | 0 | yes |
| P3 environment vs default map | across files | precedence | 3 | yes |
| P4 callback for a missing parameter | far, same file | rule inside a definition (Terminology) | 1 | yes |
| P5 top-level name in the auto-prefix key | same bullet | example against its rule | **7** | no |
| P6 maximum content width 80 vs 100 | far, same file | direct value | 1 | yes |
| P7 integer option metavar `INTEGER` vs `COUNT` | same bullet | example against its rule (replaces P5) | 1 | yes |
| R1 confirm: other answer asks again vs counts as no | across files | prose vs table | 0 | yes |
| R2 a bare leaf shows help (Terminology row) | far | rule inside a definition | **238** | no |

Kept: 7 items. Footprint union: 7 tests; core = 469. Distances: same paragraph or bullet 2 (P1, P7),
across files 3 (P2, P3, R1), far in one file 2 (P4, P6).

## Method: how the builds are tested

- **Existing tests unchanged.** Zero2Repo's 476 tests and judge are untouched (no test was opened). A
  build that follows a ruling to B fails the footprint tests of that item by design, so the
  comparable number is the **core score** on the other 469. Earlier rounds are rescored on the same
  469 from their saved reports (`notes/baseline_scores.json`), at no cost.
- **New tests outside the reward:** the side probes, run after the fact on each run's saved code
  (`runs/<id>/app.tgz`), never inside Zero2Repo's verifier, so the official reward is unaffected.
- **Exposure** (against "missed by chance"): for each item and side, whether any tool result in the
  run's transcript contains that side's phrase. It separates "never read" from "read, did not notice".
- **Stated detection:** the agent's `NOTES.md` (saved to `runs/<id>/NOTES.md`); a keyword triage points
  the reader, and the reading per item and run is recorded in `notes/detection.tsv`.
- **Settled round:** a ruling is followed when the probe reads B on that item.

## Inputs (how each was made; commands)

| Input | Command / source | Result |
|---|---|---|
| Base build | `tar -xzf ../r13c-zero2repo-3cases/runs/sonnet-case006-export-1/app.tgz -C work/base-app` | 473 / 476 through the oracle |
| Side-B builds | `python3 notes/sides.py work/base-app work/sides` | 9 copies + `.tgz` |
| Footprints | `bash notes/footprint.sh BASE P1 … R2`, `python3 notes/footprint.py` | `notes/footprint.json` |
| Planted Markdown | `python3 notes/plant.py work/spec-planted P1 P2 P3 P4 P6 P7 R1` | 14 237 words |
| Compile store | `.sdd/` of `../r13c-zero2repo-3cases/work/compile-case006` copied to `work/compile-planted`; planted files over `sdd/specs/`; `sddc ingest` | 7 changed, 458 unchanged |
| Compile | `bash notes/compile_planted.sh` (one pass) | see below |
| False alarms judged | `sddc conflicts judge CF-000148/149 --verdict false` (owner's behalf, as in 13c) | |
| Unsettled export | `sddc export --allow-open --out work/export-unsettled` | 39 992 words; `work/export-unsettled.sha256` |
| Rulings | store copied to `work/compile-settled`; `sddc conflicts judge CF-000146/150/151/152 --verdict real --note "ruling: … (side B) …"` | |
| Settled export | `sddc export --out work/export-settled` (no `--allow-open`; 0 unsettled) | 40 169 words; `work/export-settled.sha256` |
| `DECISIONS.md` | `decisions/DECISIONS.md`: the same 4 rulings in plain words, no conflict ids | added to `spec/` in the control |
| Tasks | `SPEC_DIR=… python3 notes/build_task.py case006 <task> [<export>]` (builder from 13d + `SPEC_DIR` + the instruction line) | 4 tasks |

## Compile result (step 1)

One pass: **35 calls, $0.124 est.** (13c's full compile: 853 calls, $4.2647). 19 nodes formed, 1
deleted; 1 160 candidate pairs, 45 judged, 1 115 replayed; 7 conflicts opened.

| Item | Reported | Conflict | Note |
|---|---|---|---|
| P1 | **yes** | CF-000152 contradiction | |
| P2 | **yes** | CF-000146 contradiction | also CF-000148, CF-000149: the command's warning against the option and argument "warn only when supplied" rules: false alarms, judged false |
| P3 | **yes** | CF-000150 contradiction | |
| P4 | no | — | rule inside a definition (CF-000147 is a subsumption between the planted row and FP-03's wording "may replace … or refuse", not the conflict) |
| P6 | no | — | 80 vs 100, far apart in one file |
| P7 | no | — | example against its rule, same bullet |
| R1 | **yes** | CF-000151 contradiction | |

**Recall 4 of 7.** Missed: the definition, the far-apart value, the example. `lend` showed the same two
kinds missed (alias in a definition, worked example). Rulings were given only for the 4 reported
items, so P4, P6 and P7 stay unruled in every cell (pure agent detection).

### Why the compiler missed 3, and the change (rel02 D26, after the runs)

Traced in the store, no model call (`work/compile-planted`):

| Item | Cause |
|---|---|
| P6 | **Incremental compile, one end checked.** The old "defaults to 80 columns" node ranks the new "100 columns" node 5th of 9, inside its cap of 6, but old nodes are not checked in an incremental run; from the new node's side the pair ranks 54th of 80, behind six help-page claims sharing a term. A full compile would have proposed it. |
| P7 | **Examples are annotations, never judged** (F2 §4.1); and the example was lost even as an annotation, because an `unchanged` node kept its old record (F3 §4.6). |
| P4 | **Ranking.** The glossary row's best pair, "a missing parameter still runs its callback", ranks 7th of 171 from the row's side (score 5.0 against 5.5 for the 6th) and 32nd from the other. |

Changed spec-first (suite 766 passed): **F5 D14** a pair is proposed from either end, checked or not
(AC-5.18); **F2 D22 / F3 D41** an example becomes a `verification` node of the claim before it,
formed in code with no model call (AC-2.30, AC-3.40); **F3 D42** an `unchanged` node takes its
block's current annotations (AC-3.41). P4's cap was **not** tuned: a cap of 7 would catch it, but
that would be fitting the answer key.

**Re-measured** (`notes/compile_planted_v2.sh`, `work/compile-planted-v2`): the same incremental
compile from 13c's store, with round 14's lock copied in so the same atomizer and judge answers
replay; only the code differs. One pass, **29 calls, $0.0732 est.**; 1 690 candidate pairs (1 160
before), 51 judged, 1 639 replayed; `pairs_from_unchecked_end` 525.

| Item | Before | After |
|---|---|---|
| P1, P2, P3, R1 | found | found |
| P6 | missed | **found** (CF-000155: "one at 80 columns and the other at 100") |
| P7 | missed | **found** (CF-000152, the example node N-001013 against N-000326) |
| P4 | missed | missed (still 7th of 171) |
| False alarms | 2 (CF-000148, 149) | 3 (the same two, and CF-000154: the glossary row against "that callable is invoked when no earlier value source produced a value", a callable default, not a callback) |

**Recall 6 of 7** (was 4 of 7). The agent runs above used the first export; they were not rerun.

## Checks before model runs (no model)

| Check | Result |
|---|---|
| Probes on base and side-B copies | base all A; each copy B on its own item only (R2's copy also broke 3 other probes) |
| Do-nothing agent, all 4 tasks | 0 tests, official 0, no Harbor exception |
| Instructions | identical across the 4 tasks apart from the spec line |
| Baseline on the unplanted spec (9 earlier runs, rescored) | every completed build takes A on all 7 items (one P6 "neither"); Haiku core 446 (Markdown), 409–460 (export) of 469 |

## Runs

Queue in `queue.tsv`; log in `run_queue.log`; files per run in `runs/<run_id>/`; `python3 ../summarize.py .`
into `results.json`; `python3 notes/score.py runs/*/` into `notes/scores.json`. Driver started
2026-10-16 15:13; last run done 20:30.

### Resume (for a new session)

Read this file, `queue.tsv`, `run_queue.log`. If the driver is not running and rows are pending:
`cd .. && nohup bash run_queue.sh r14-zero2repo-case006-conflicts >> r14-zero2repo-case006-conflicts/run_queue.log 2>&1 &`.
When all rows are done: summarize, score, read each `NOTES.md` into `notes/detection.tsv`, token check
(`grep -rl "sk-ant-oat01" work/jobs runs` must be empty), write Results and Findings.

## Results

13 runs, all `done`. `r2-haiku-markdown-3` stopped after 16 turns with a partial package (no test
could load): after an output-cap cut it read Claude Code's budget reminder as "about $0.0002 left" and
stopped, the same behaviour as 13c's `haiku-case006-markdown-2`. It is kept on record, left out of the
tables, and replaced by `r2-haiku-markdown-4` (same task, queued after round 3), so every cell has 3
runs. One pause for the 5-hour window (0.93 at 18:28, resumed 19:25). Token check: no token string
in `work/jobs` or `runs`. Seven-day usage 0.72 before the round, 0.84 after.

Tests: the judge's passed / 476. Core: of the 469 outside the footprint union. Sides: the probes on
the saved code. Noticed: the run's `NOTES.md` names the disagreement (read by the assistant, item by
item, `notes/detection.tsv`; not blind to format, which the export's conflict ids would defeat
anyway). `$`: `total_cost_usd`, an API-equivalent estimate. Time: Harbor's job time.

| Run | Tests | Core | Sides P1 P2 P3 P4 P6 P7 R1 | Noticed (of 7) | Turns | $ est. | Time (s) |
|---|---|---|---|---|---|---|---|
| r2 markdown-1 | 429 | 424 | A A A A A A A | 3 (P1 P2 P4) | 54 | 0.6249 | 1 165 |
| r2 markdown-2 | 463 | 457 | A A A A A A A | 6 (all but P3) | 57 | 1.3020 | 1 075 |
| r2 markdown-4 | 454 | 448 | A A A A A A A | 4 (P1 P2 P4 P6) | 73 | 0.6575 | 1 180 |
| *r2 markdown-3 (stopped)* | *0 (no tests loaded)* | — | — | — | *16* | *0.0852* | *618* |
| r2 export-1 | 434 | 431 | **B** A A A A A A | 6 (all but P7) | 43 | 0.5272 | 1 286 |
| r2 export-2 | 469 | 462 | A A A A A A A | 7 | 60 | 1.2927 | 1 047 |
| r2 export-3 | 403 | 400 | **B** A A A A A A | 6 (all but P7) | 90 | 1.0934 | 1 070 |
| r3 markdown+decisions-1 | 428 | 423 | **B B** A A A A **B** | 5 (P1 P2 P3 P4 R1) | 48 | 0.5346 | 1 156 |
| r3 markdown+decisions-2 | 455 | 452 | **B B B B** A A **B** | 6 (all but P7) | 56 | 0.9534 | 986 |
| r3 markdown+decisions-3 | 413 | 410 | **B B B** A A A **B** | 6 (all but P7) | 58 | 0.5810 | 1 155 |
| r3 export-settled-1 | 464 | 460 | **B B B** A A A **B** | 7 | 39 | 0.7982 | 978 |
| r3 export-settled-2 | 461 | 457 | **B B B** A A A **B** | 7 | 80 | 2.0239 | 1 275 |
| r3 export-settled-3 | 452 | 450 | **B B B** A A **B B** | 7 | 44 | 1.0370 | 1 030 |

Cost: runs $11.5112 est. (13 runs, the stopped one included); compile $0.124 est.; **$11.64 in all**.

**Per cell** (3 runs each):

| Cell | Core, mean (range) | Noticed: 4 items the compiler reported | Noticed: 3 it missed | Rulings followed in code | Turns |
|---|---|---|---|---|---|
| r2 Markdown | 443.0 (424–457) | 7 / 12 (P1 3, P2 3, P3 **0**, R1 1) | 6 / 9 (P4 3, P6 2, P7 1) | — | 54–73 |
| r2 export, unsettled | 431.0 (400–462) | **12 / 12** | 7 / 9 (P4 3, P6 3, P7 1) | — | 43–90 |
| r3 Markdown + `DECISIONS.md` | 428.3 (410–452) | 12 / 12 (ruled) | 5 / 9 (P4 3, P6 2, P7 **0**) | **11 / 12** | 48–58 |
| r3 export, settled | 455.7 (450–460) | 12 / 12 (ruled) | **9 / 9** | **12 / 12** | 39–80 |

Baseline, same 469 tests, unplanted spec, earlier rounds (`notes/baseline_scores.json`): Haiku
Markdown 446 (13c); Haiku export 419 and 460 (13c), 442 and 409 (13d). Every completed earlier build
took A on all 7 items (one P6 "neither").

**Exposure:** in all 13 runs, the tool results contain both phrases of every item (`notes/scores.json`).
No planted sentence went unread; every miss above is "read, not noticed".

**Where notes and code differ (the probes caught both):**
- `r3 markdown+decisions-1`, P3: `NOTES.md` states the ruling (default map before environment); the
  code resolves the environment first (`command.py`, `_resolve_one`). A ruling stated, not built.
- `r3 markdown+decisions-2`, P4 (unruled): the agent built a split rule (callback runs when a default
  is declared, not otherwise); the probe's option has no default, so it reads B.

## Findings

1. **The compiler found 4 of the 7 planted conflicts**, from a 35-call incremental compile ($0.124
   est.): the same-paragraph control (P1) and the three across files (P2, P3, R1). It missed the rule
   inside a definition (P4), the far-apart value (P6) and the example against its rule (P7). It raised
   2 false alarms on the planted P2 sentence. *Traced afterwards:* P6 was lost to the incremental
   compile itself (only the new end was checked), P7 to examples never being judged, P4 to ranking.
   After the change of rel02 D26, the same compile finds **6 of 7** (see "Why the compiler missed 3").
2. **Unsettled, the export made Haiku name more of the planted conflicts: 19 of 21 against 13 of 21
   from the Markdown.** The difference is on the conflicts the export lists: 12 of 12 against 7 of 12.
   The across-file precedence conflict (P3) was noticed in no Markdown run and in every export run; the
   across-file confirm conflict (R1) in 1 of 3 against 3 of 3. On the 3 the compiler missed, the two
   formats are close (7 of 9 against 6 of 9). Every run read both sides of every item, so the
   Markdown runs' misses are not reading gaps.
3. **Noticing did not change what was built.** Unsettled, the builds took side A (click's behaviour)
   on 40 of 42 item-runs in both formats; the exceptions are P1 in 2 export runs. The agents' reasons:
   "the more specific rule", "the channel table is the normative form", "as the first sentence says".
   With unsettled conflicts the export changes what the agent reports, hardly what it builds.
4. **Rulings reached the code from both carriers**: 12 of 12 from the settled export, 11 of 12 from
   `DECISIONS.md`. The one miss is a build whose notes state the ruling while its code does not
   follow it: the probes, not the notes, caught it. With n = 3 this is one event, not a rate.
5. **In the settled round the export runs also noticed every unruled conflict (9 of 9) against 5 of 9
   from the Markdown with `DECISIONS.md`.** P7 (the example) was noticed by no Markdown-with-decisions
   run. One export run took the example's side on P7.
6. **No core-score effect can be claimed.** Means 443.0 and 431.0 (round 2), 428.3 and 455.7 (round
   3), with ranges overlapping (400–462 overall), inside the earlier Haiku spread on the unplanted
   spec (409–460). Planting 7 conflicts did not visibly lower the rest of the build.
7. **Turns did not separate the formats this time** (export 39–90, Markdown 48–73; 13c and 13d had
   the export higher). The task differs from 13d by the planted text and the instruction line, so
   nothing is put down to either.
8. **Methods that paid off:** the footprint rule dropped two candidates that would have dominated the
   score (P5: 7 tests; R2: 238, a single Terminology row); the exposure check showed misses were not
   reading gaps; the probes caught a stated-but-not-built ruling that the notes alone would have scored
   as followed; side alone would have shown nothing in round 2 (all A).

## Open items

- n = 3 per cell; the reading of `NOTES.md` is one reader's (an owner audit of `notes/detection.tsv`
  against `runs/*/NOTES.md` would give a second).
- Rounds ran in sequence (round 2 then round 3), so a time-of-day difference between rounds cannot be
  excluded; cells within a round alternated.
- Sonnet not run. Only 7 items, one case (click, which the model knows).
- P4 is still missed (rank 7, cap 6). Options: a larger cap for the nodes an incremental run checks,
  or splitting glossary rows; neither chosen, both need measuring beyond this key.
- The agent cells were not rerun with the 6-of-7 export.
- Owner audit of the detection readings: `notes/detection_audit.md` (built by `notes/audit_sheet.py`).

## Files

| Path | Tracked | What |
|---|---|---|
| `TRIAL.md` | yes | This description |
| `ANSWER_KEY.md` | yes | Planted items, sides, footprints, probes, exposure phrases |
| `decisions/DECISIONS.md` | yes | The 4 rulings in plain words (Markdown control) |
| `trial.env`, `queue.tsv`, `run_queue.log` | yes | Run conditions, queue, driver log |
| `runs/<run_id>/` | yes | Judge's files, `app.tgz`, `agent.tgz`, and `NOTES.md` copied out by the scorer |
| `results.json` | yes | `../summarize.py` |
| `notes/` | yes | `plant.py`, `sides.py`, `probe.py`, `probe.sh`, `footprint.sh`, `footprint.py`, `footprint.json`, `compile_planted.sh`, `build_task.py`, `check_nop.sh`, `score.py`, `scores.json`, `baseline_scores.json`, `detection.tsv` |
| `work/` | **no** | Planted spec, base and side-B builds, compile stores, exports, tasks (with hidden tests), Harbor jobs |
