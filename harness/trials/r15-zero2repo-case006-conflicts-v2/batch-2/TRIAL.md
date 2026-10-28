# r15-zero2repo-case006-conflicts-v2 · batch 2

> Opened 2026-10-18. State: **closed 2026-10-19**. Approved by the owner through the Copilot handover
> (`sdd/design/rel-02/rel02_handover_copilot_r15.md`, batch 2 version): 5 runs, at most 2
> replacements. Operated by GitHub Copilot CLI (setup, queue, driver); the driver paused for usage
> from 2026-10-18 01:24 to 2026-10-19 17:05. **Scored and written up by Claude Code on 2026-10-19**
> (the owner kept the earlier prompt, so Copilot did not do steps 7–9). Copilot's first version of
> this file (state *planned*, prechecks) is replaced by this one; its prechecks are kept below.

## Question

With the same planted Markdown and the same 6-of-7 unsettled export as batch 1, do more Haiku runs
change round 15's comparison of which planted conflicts the agent names and builds?

## Design

| Item | Value |
|---|---|
| Case | Zero2Repo case006 (Optlyn = click renamed), 476 hidden tests; 7 planted conflicts (`../ANSWER_KEY.md`) |
| Conditions | planted Markdown (3 runs) · 6-of-7 export, conflicts open (2 runs) |
| Tasks | batch 1's, **unchanged**: `../work/tasks/case006-planted-markdown`, `../work/tasks/case006-planted-export-v2`; the export checked against `../work/export-v2.sha256` (`export-unchanged`, `task-holds-the-same-export`) |
| Note | this export predates F7 D17: P7's example is listed under *Acceptance criteria* (kept so batch 2 adds to batch 1) |
| Model / agent | Haiku (`anthropic/claude-haiku-5-5`), Claude Code 2.1.296 in Harbor, tools `Bash Edit Read Write`, allow-list; `trial.env` as batch 1 ($10 ceiling, 9 000 s) |
| Scorers | judge (tests / 476); core (469 outside the planted footprints); probes (`notes/probe.py`); exposure; `NOTES.md` read by Claude Code (`notes/detection.tsv`) |

## Inputs and prechecks (Copilot, 2026-10-18)

Docker, token-file presence, both task instruction files, `export-unchanged`,
`task-holds-the-same-export` passed. The handover's `pgrep -f run_queue.sh` check matched its own
shell (a prompt fault, fixed in the revised handover); `pgrep -af '[r]un_queue\.sh'` found no
driver. Folder made with `trial.env`, `notes/` (`score.py`, `probe.py`, `probe.sh`,
`footprint.json`, `issues.md`). Queue of 5, driver started 2026-10-18 01:06.

## Runs

Queue `queue.tsv`; log `run_queue.log`; files `runs/<run_id>/`; `python3 ../../summarize.py .` →
`results.json`; `python3 notes/score.py runs/r15b-*/` → `notes/scores.json`. No early stop, no
replacement. Token check clean. Usage: 7-day 0.95 after run 1 (paused until the reset), then 0.01 →
0.03; 5-hour 0.10 → 0.32 (`run_queue.log`).

## Results

| Run | Tests | Core | Sides P1 P2 P3 P4 P6 P7 R1 | Named (of 7) | Turns | $ est. | Time (s) |
|---|---|---|---|---|---|---|---|
| r15b markdown-1 | 429 | 423 | A A A A A A A | 4 (P1 P2 P4 P6) | 66 | 0.4683 | 1 056 |
| r15b export-1 | 441 | 435 | A A A A A **B** A | 7 | 64 | 1.2666 | 1 129 |
| r15b markdown-2 | 463 | 456 | A A A A A A A | 6 (all but P3) | 41 | 0.7842 | 856 |
| r15b export-2 | 431 | 428 | A A A **B** A **B B** | 6 (all but P4) | 60 | 0.8178 | 1 115 |
| r15b markdown-3 | 452 | 446 | A A A A A A A | 5 (P1 P2 P4 P6 R1) | 53 | 1.0257 | 1 040 |

Total **$4.3626 est.** Every run's transcript contains both sides' phrases of all 7 items (exposure).
In every row of `notes/detection.tsv`, the side a run's notes say it built is the side the probe
found. `r15b export-2` built P4's planted side without naming the conflict (its code skips the
callback for an omitted parameter): a build choice, not a detection.

## Round 15 so far (batch 1 + batch 2; batch 1's stopped Markdown run left out)

| | Markdown (4 runs) | Export 6 of 7 (4 runs) |
|---|---|---|
| Core | 430, 423, 456, 446 · mean 438.8 (423–456) | 454, 454, 435, 428 · mean 442.8 (428–454) |
| Named P1 / P2 / P3 / P4 / P6 / P7 / R1 | 4 / 4 / **0** / 4 / 4 / 2 / **2** | 4 / 4 / **4** / 3 / 4 / 4 / **4** |
| Named, all | 20 of 28 | 27 of 28 |
| Built side B | P7 once | P7 **4**, P1 1, P4 1, R1 1 |

## Comparison with round 14 (same planted Markdown; round 14's export listed 4 of 7)

Both rounds, conflicts open: **Markdown 7 runs**, core mean 440.6 (423–457), named 33 of 49; **export
7 runs** (3 with 4 listed, 4 with 6 listed), core mean 437.7 (400–462), named 46 of 49.
- P3 (environment vs default map, across files): named in **0 of 7** Markdown runs and **7 of 7**
  export runs. R1 (confirm, across files): **3 of 7** and **7 of 7**.
- The core scores are not separable: the means differ by 2.9 of 469 and the ranges overlap.
- Unruled, both formats built the original side (A) on almost every item.
- P7: built side B in **4 of 4** 6-of-7 export runs, against 1 of 7 Markdown runs and 0 of 3 runs of
  round 14's export (where the example was not a node). Three of the four export runs call the example
  the "acceptance criterion" in their notes.

## How to read the tables (added 2026-10-20)

- **Sides P1 … R1.** For each planted conflict, which of the two sentences the run's code follows,
  measured by running a small black-box check on the built code (`notes/probe.py`). **A** = the
  case's original sentence; **B** = the planted one. Bold marks a B.
- **Named (of 7).** How many of the 7 planted conflicts the run *said* it noticed. A conflict counts
  as named when the run's `NOTES.md` mentions both sentences as a contradiction (or the choice made
  between them), read by Claude Code into `notes/detection.tsv`. It measures noticing, not which
  side was built: a run can name a conflict and still pick A. The list in brackets is which ones.
- **Named P1 / P2 / P3 / P4 / P6 / P7 / R1** in the round 15 table. Each number is "in how many of
  the 4 runs of that format was this conflict named". Markdown `4 / 4 / 0 / 4 / 4 / 2 / 2` reads: P1,
  P2, P4 and P6 were named by all 4 Markdown runs; P3 by none; P7 and R1 by 2 of 4. Export
  `4 / 4 / 4 / 3 / 4 / 4 / 4`: every conflict was named by all 4 export runs except P4 (3 of 4; the
  one miss is `r15b export-2`). Summed, 20 of 28 and 27 of 28 (4 runs × 7 conflicts = 28).
- **Built side B.** How many runs built the planted sentence instead of the original, per item.

## The 7 planted conflicts, their sides, and the tests they move

Source: `../../r14-zero2repo-case006-conflicts/ANSWER_KEY.md` (written before any run). Side **A**
is what case006 already said: click's real behaviour, so it is what the 476 hidden tests check.
Side **B** is one sentence planted elsewhere in the spec that says the opposite. Neither side is
marked; nothing in the spec says which one is right.

**Which side passes the tests:** always side A. Building side B fails that conflict's *footprint*
tests (measured in round 14 by patching a near-complete build to side B and running the hidden tests:
`notes/footprint.json`). P2 and R1 have no footprint: the hidden tests do not check them, so either
side passes. The 7 footprint tests are kept out of the **core** score (469 tests) so that a run is not
rewarded or punished for the side it chose.

| Item | Where the two sentences are | Side A (original; passes the tests) | Side B (planted; fails the tests) | Footprint tests (fail on B) |
|---|---|---|---|---|
| P1 | same paragraph of PRD FP-14 | a temporary folder made by the test runner with no parent given is **removed** on exit | the folder is **always left** in place | 1 (`F14 …new_empty_dir_removed_when_no_parent`) |
| P2 | Contract table vs PRD FP-01 | a deprecated command's warning goes to **standard error** | it goes to **standard output** | 0 |
| P3 | PRD FP-03 vs Contract `default_map` row | value order: command line, then **environment**, then the default map | default-map values **beat** environment variables | 3 (`F03 …feature_switch_more_explicit_source_wins`, `F03 …fill_order_command_line_env_map_declared`, `F07 …default_map_string_splits_like_environment`) |
| P4 | PRD FP-03 vs PRD Terminology "Callback" | a missing parameter **still runs** its callback | the callback is **not called** for an omitted parameter | 1 (`F03 …missing_parameter_still_runs_its_callback`) |
| P6 | PRD FP-02 vs PRD FP-11 | help text maximum width defaults to **80** columns | help pages use **100** columns | 1 (`F02 …help_rewrapped_to_width_capped_at_default_80`) |
| P7 | one bullet of PRD FP-02: rule vs its example | default metavar is the **type name** in upper case: `--count INTEGER` | the example shows `--count COUNT` (the **parameter name**) | 1 (`F02 …value_option_metavar_is_type_name_not_parameter_name`) |
| R1 | PRD FP-08 vs Contract `confirm` row | for a yes/no question, any other answer **asks again** | any other answer **counts as no** | 0 |

**Expected footprint result for a run:** start from 7, subtract the footprint of each item built on B.
A run that built A everywhere *can* pass all 7, but only if the rest of that feature also works: an A
build can still fail a footprint test for an unrelated reason (see P3 and P6 in `r15b export-2`
below). Total score = core + footprint passed.

## Why `r15b export-2` scored lowest (431 tests, core 428), debugged 2026-10-20

Read from the run's transcript, `NOTES.md` and code (`runs/r15b-haiku-export-2/`), plus small
black-box checks in a no-network container. The hidden tests were not opened; only the names of the
failed tests (`reward_detail.json`) and the exception lines of `final_tests.log` were used.

**Score breakdown.** 45 tests failed: 4 footprint, 41 core (469 − 41 = 428; 428 + 3 footprint passed
= 431). Almost all are wrong-behaviour assertions; `final_tests.log` shows only 3 exception lines
other than assertions (2 `RuntimeError`, 1 `FileNotFoundError`). 23 of the 45 fail in no other batch 2
run.

**1. Planted conflicts: 4 of 7 footprint tests lost.**
- P4 built on **B** without naming the conflict: `parser.py` runs a callback only
  `if p.callback is not None and source is not None`, so an omitted parameter's callback is skipped.
  Cost: 1 test.
- P7 built on **B** (`--count COUNT`), choosing it because it matches "the criterion" (its `NOTES.md` calls
  the example an acceptance criterion, as the pre-D17 export lists it). Cost: 1 test.
- R1 built on **B** (counts as no). Cost: 0 (no footprint).
- P3 (A) and P6 (A, width 80) each lost a footprint test for an unrelated reason. P3's
  `feature_switch…` test needs feature-switch groups, which the run lists as not implemented. P6's
  test needs the help rewrapping, which the run did with plain `textwrap` (its own "Known gaps").

**2. Core: 41 failures, spread over 11 feature files.** From most to least clearly explained:
- **A coding slip against a sentence it read.** `core.py` makes every argument without a default
  *required*, including variadic ones (`nargs=-1`). An omitted variadic argument then stops with
  "Missing parameter" instead of delivering `()`. Pack 22 says the opposite in plain words ("A
  variadic argument omitted yields an empty sequence unless it was marked required"), and the run read
  that text. `r15b export-1` gets it right. Checked directly; it plausibly also breaks other tests that
  leave a variadic argument empty.
- **Gaps the run itself listed in `NOTES.md`:** feature-switch groups (F03), group-level option
  mixing as a keyword (F03 `group_mixing…`, `leaf_mixing…`), descriptor capture `capture="fd"` (F14
  `descriptor_capture…`), short-help ellipsis and `textwrap` wrapping (F02 `long_short_help…`,
  `single_newlines…`, `backspace_paragraph…`).
- **Scattered misses** with no single cause found from the names: chaining and result callbacks (F10,
  5), completion (F12, 5; 4 of 5 also fail in other runs), files (F09, 3), terminal helpers (F11, 3),
  version detection (F02, 2), group help (F06, 2).

**3. Not the cause: how it read the spec.** For packs 22–33 (PRD FP-04 to FP-14) the run filtered out
the sections from *Claims to implement* through *Related elsewhere* with `awk`. That looks like
skipping requirements, but in this export those sections hold only node-id lists and cross-links; the
full prose (`## Text`) was kept and read. Packs 01–21 were read whole.

**4. A smaller, less-tested build.** 3 050 source lines (export-1: 3 894) and 10 self-written tests
(export-1: about 1 300 test lines); 60 turns, $0.8178 est. Whether size or self-testing predicts the
score is not shown: `r15b markdown-2` wrote no tests and scored highest (463).

**Reading.** Most of the low score is ordinary Haiku build-to-build variation: one clear coding slip,
several features left out on purpose, and scattered edge cases. The export did not cause it: the run
named 6 of 7 conflicts, read the whole spec, and the planted sides cost it 2 tests. Core across the
4 export runs ranges 428–454 and across the 4 Markdown runs 423–456, so a run-to-run spread of about
30 tests is normal on this case.

## Findings

1. **More runs keep the detection result.** Round 15's export runs named 27 of 28 planted conflicts,
   the Markdown runs 20 of 28. The gap is the conflicts that span the two documents (P3, R1); the
   others were named from either format (`notes/detection.tsv`).
2. **No test-score difference** (core means 442.8 and 438.8, overlapping ranges); consistent with
   rounds 13c–14.
3. **Listing the example as an acceptance criterion is associated with building it.** All four
   6-of-7 export runs built P7's example side; 3 of 4 named it an acceptance criterion. Association on
   4 runs, not shown as cause; it supports F7 D17 (2026-10-18), which lists such a node as
   `example of N-…`. An export with D17 has not been run.
4. **No early stop in batch 2** (0 of 5). Haiku Markdown runs on case006 that stopped early on the
   misread budget: 3 of 15 so far; export runs: 0 of 14.

## Open items

- An export built with F7 D17 (needs a fresh compile; then the same Haiku runs) would test finding 3.
- Detection read by one reader (Claude Code); the owner's audit sheet covers round 14 only.

## Files

| Path | Tracked | What |
|---|---|---|
| `TRIAL.md` | yes | This description |
| `trial.env`, `queue.tsv`, `run_queue.log` | yes | Conditions, queue, driver log |
| `runs/<run_id>/` | yes | Judge's files, `app.tgz`, `agent.tgz`, `NOTES.md` |
| `results.json` | yes | `../../summarize.py` |
| `notes/` | yes | `score.py`, `probe.py`, `probe.sh`, `footprint.json` (copied from batch 1), `scores.json`, `detection.tsv`, `issues.md` |
| `work/` | **no** | Harbor jobs |

## For the report

Batch 2 brings round 15 to four valid runs per condition. With round 14, seven Haiku runs per format
on the same planted case006: the export runs named 46 of 49 planted conflicts, the Markdown runs 33 of
49, and the gap is entirely in the conflicts that span the specification's two documents (P3 0 of 7
against 7 of 7; R1 3 of 7 against 7 of 7). Test scores did not differ (core means 437.7 and 440.6),
and unruled conflicts were built on the original side in both formats. Limits: Haiku only, one case,
one reader of the notes, 7 runs per format.
