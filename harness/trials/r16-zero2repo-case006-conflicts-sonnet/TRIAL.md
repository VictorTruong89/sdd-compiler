# r16-zero2repo-case006-conflicts-sonnet (interim-report trial T2)

> Opened 2026-10-28 by Claude Code. State: **closed** 2026-10-28 (planned / running / paused / closed). Approved
> by the owner on 2026-10-28: "Do T0, then T1, then T2 as suggested" (plan: 2 + 2 Sonnet runs,
> ≈ $8.7–11.1 est. from Sonnet case006 runs 64, 70, 78, 82). Update this file at every step.

## Question

On the planted case006 with conflicts left open, Haiku named the two cross-document conflicts far more
often from the export (P3 7 / 7, R1 7 / 7) than from the Markdown (P3 0 / 7, R1 3 / 7)
(`../r15-zero2repo-case006-conflicts-v2/batch-2/TRIAL.md`). **Does a stronger model, Sonnet, show the
same gap?** Secondary: P7 side built, core score, cost and turns.

## Design

| Item | Value |
|---|---|
| Benchmark / case | Zero2Repo case006 (Optlyn = click renamed), 476 hidden tests; the 7 planted conflicts of rounds 14–15 (`../r15-zero2repo-case006-conflicts-v2/ANSWER_KEY.md`) |
| Formats | planted Markdown (the task of rounds 14–15, unchanged) · export v3 (6 of 7 conflicts open, F7 D17), the task of batch 3 (`../r15-zero2repo-case006-conflicts-v2/batch-3/TRIAL.md`) |
| Models | Sonnet (`anthropic/claude-sonnet-5-5`) |
| Runs per cell (n) | 2, interleaved Markdown, export, Markdown, export |
| Agent | Claude Code 2.1.296 (`trial.env`), Harbor 0.24.0, tools `Bash Edit Read Write`, network allow-list |
| Ceiling | `BUDGET_USD=10` per run, `RUN_TIMEOUT=9000` |
| Scorer | unchanged, copied from round 15 batch 2: judge (tests / 476); core (469); probes (`notes/probe.py`); exposure; `NOTES.md` read by Claude Code into `notes/detection.tsv` |

**Why export v3 and not v2.** v2 listed P7's example as an acceptance criterion, a known bias (batch 2,
finding 3). v3 differs from v2 only in that listing (batch 3, "Inputs"), so P3 and R1 are shown the
same way as in the Haiku runs.

**Comparison.** Sonnet Markdown vs Sonnet export, item by item (named, side built). Against Haiku's 7
+ 7 for the direction only: different model, n = 2. Earlier Sonnet case006 runs on the unplanted
spec (13c: 470, 469 Markdown; 473, 470 settled export, reg. 64, 70, 78, 82) give the unplanted level.

## Inputs (how each was made; commands)

No new input: both tasks are under `../r15-zero2repo-case006-conflicts-v2/work/tasks/`
(`case006-planted-markdown`, `case006-planted-export-v3`); scorers copied from batch 2 into `notes/`.

## Checks before model runs (no model)

Both tasks passed the do-nothing check in their own trial (Markdown: round 15 batch 1; export v3:
batch 3).

## Runs

Queue in `queue.tsv`; log in `run_queue.log`; files per run in `runs/<run_id>/`; table built by
`python3 ../summarize.py .` into `results.json`. Run after batch 3 in the same unattended chain.

Driver log, in order (`run_queue.log`): markdown-1 done 11:07; **export-1 attempt stopped by the
subscription session limit** at 11:19 (429, "resets 4pm (UTC)"; 12 turns, $1.3048 est.; job folder
kept as `work/jobs/…-r16-sonnet-export-1.limited-20261028T111900`); the driver slept to the reset and
reran export-1 from the start at 12:05; markdown-2 and export-2 followed; end 12:57. No early stop.
Token string absent from `runs/` and `work/` (`grep -rl`, 0 files).

**markdown-1: judge error.** The agent finished (21 turns, `NOTES.md` and code saved), but the hidden
test run did not complete: `runs/r16-sonnet-markdown-1/final_tests.log` stops inside
`F08_acceptance.py` (every test shown before that point is a pass), and `reward_detail.json` reads
"acceptance did not produce a parseable executed-test summary". The verifier ran 14:43:25–15:07:14
UTC (`result.json`). **Cause (debugged 2026-10-28, no model):** one test,
`test_password_option_accepts_matching_hidden_lines`, sends the agent's code into an endless loop:
at end of input its `CliRunner` returns an empty line instead of raising `EOFError`, and its
confirmation prompt (`termui.py` line 78) re-asks until it gets a non-empty answer, writing the
prompt into the captured output every time. The test process grows until the kernel kills it
(reproduced: `OOMKilled=true`, exit 137, after 92 s under a 2 GB cap); pytest dies mid-line and the
judge finds no summary. Not an early stop, so no
replacement was queued; probes and notes are read as usual, tests and core are *not measured*.

## Results

| Run | Tests | Core | Sides P1 P2 P3 P4 P6 P7 R1 | Named (of 7) | Turns | $ est. | Time (s) |
|---|---|---|---|---|---|---|---|
| r16 markdown-1 | judge error | — | A A A A A A A | 6 (all but P3) | 21 | 2.4639 | 2 341 |
| r16 export-1 | 472 | 465 | A A A A A A A | 7 | 26 | 2.2644 | 834 |
| r16 markdown-2 | 466 | 460 | A A A A A A A | 7 | 22 | 2.2431 | 962 |
| r16 export-2 | 472 | 465 | A A A A A A A | 6 (all but P4) | 27 | 2.5421 | 962 |

Sources: as batch 3 (`results.json`, `notes/scores.json`, `notes/detection.tsv`, `run_queue.log`).
**$9.5135 est.** for the four completed runs (`results.json`), plus **$1.3048 est.** for the
limit-stopped attempt (`run_queue.log`). Every transcript contains both sides' phrases of all 7 items.
In every row of `detection.tsv` the built side matches the probe.

| | Markdown (2 runs) | Export v3 (2 runs) |
|---|---|---|
| Named P1 / P2 / P3 / P4 / P6 / P7 / R1 | 2 / 2 / **1** / 2 / 2 / 2 / 2 | 2 / 2 / 2 / **1** / 2 / 2 / 2 |
| Named, all | 13 of 14 | 13 of 14 |
| Built side B | none | none |
| Core | 460 (markdown-1 not measured) | 465, 465 |

## Findings

1. **No format gap for Sonnet on these runs.** Sonnet named 13 of 14 planted conflicts from either
   format. The Markdown runs named the cross-document pair too: R1 in 2 of 2, P3 in 1 of 2. Haiku's
   gap (P3 0 / 7, R1 3 / 7 from Markdown) did not appear. n = 2 per format.
2. **Sonnet built the original side (A) on all 7 items in all 4 runs**, including P7 on export v3.
3. **Core**: export 465, 465; Markdown 460 (one run not measured). The unplanted Sonnet case006 level
   (13c: Markdown 470, 469; settled export 473, 470) is total tests, not core, and is given only for
   scale.
4. **Cost and turns**: $2.2431–2.5421 est. and 21–27 turns per Sonnet run, against $0.6927–1.1175
   est. and 58–84 turns for batch 3's Haiku runs (`run_queue.log` of each).
5. **Two operational events**: one session-limit stop (handled by the driver, rerun from scratch)
   and one judge error: the agent's code looped on one hidden test until the test process ran out of
   memory (no test score for that run).

## Open items

- markdown-1's test score: the loop repeats on every run (reproduced), so a rerun of the judge would
  fail the same way. A score without that one test would need a changed scorer; not done.
- Whether the Haiku gap is a Haiku effect needs more Sonnet runs; n = 2 does not separate them.

## Files

| Path | Tracked | What |
|---|---|---|
| `TRIAL.md` | yes | This description |
| `trial.env` | yes | Run conditions read by `../run_queue.sh` |
| `queue.tsv`, `run_queue.log` | yes | Queue state, driver log |
| `runs/<run_id>/` | yes | `result.json`, reward and report files, junit, `app.tgz` (agent's code), `agent.tgz` (transcript, trajectory), `NOTES.md` |
| `results.json` | yes | Built by `../summarize.py` |
| `notes/` | yes | `score.py`, `probe.py`, `probe.sh`, `footprint.json`, `scores.json`, `detection.tsv` |
| `work/` | **no** | Harbor jobs |
