# r15-zero2repo-case006-conflicts-v2 · batch 3 (interim-report trial T1)

> Opened 2026-10-28 by Claude Code. State: **closed** (2026-10-28). Approved by the owner on 2026-10-28: "Do T0,
> then T1, then T2 as suggested" (plan in `sdd/design/rel-02/rel02_handover_interim_report.md` §3 and
> the session's plan table: 3 Haiku export runs plus a lock-replay compile, ≈ $2.5–5.2 est.).

## Question

Round 15's export listed P7's example node under *Acceptance criteria*, and all 4 runs on it built the
example's side (B), 3 of them calling it "the acceptance criterion" (`../batch-2/TRIAL.md`, finding 3).
F7 D17 (2026-10-18) now lists such a node in Claims as `example of N-…`. **With the D17 export, do
Haiku runs still build P7's example side?** Secondary: does the rest of round 15's result (named
conflicts, core score) hold on the new export?

## Design

| Item | Value |
|---|---|
| Case | Zero2Repo case006 (Optlyn = click renamed), 476 hidden tests, the same 7 planted conflicts (`../ANSWER_KEY.md`) |
| Condition | **export v3**: the 6-of-7 export remade by the current compiler (F7 D17), conflicts open (`--allow-open`) |
| Compared with | round 15's 4 runs on export v2 (P7 B in 4 of 4) and the 7 planted-Markdown runs (P7 B in 1 of 7). No new Markdown runs |
| n | 3 (at most 2 replacements for early stops, as batch 2) |
| Model / agent | Haiku (`anthropic/claude-haiku-5-5`), Claude Code 2.1.296 in Harbor 0.24.0, tools `Bash Edit Read Write`, allow-list; `trial.env` as batches 1–2 ($10 ceiling, 9 000 s) |
| Scorers | unchanged, copied from batch 2: judge (tests / 476); core (469); probes (`notes/probe.py`); exposure; `NOTES.md` read by Claude Code into `notes/detection.tsv` |

**How export v3 is made** (as round 14's v2 replay, `../../r14-zero2repo-case006-conflicts/notes/compile_planted_v2.sh`):
copy round 13c's finished case006 store; copy the planted Markdown (`../work/spec-planted`, identical
to round 14's) over `sdd/specs/`; `sddc ingest`; copy in the lock of round 14's v2 compile so the same
atomizer and judge answers replay; `sddc compile`; judge the same 3 false alarms false with batch 1's
notes; `sddc export --allow-open`. Expected: the same 6 open contradictions as v2; the only intended
difference is the example's listing. **Calls of the compile: to be measured.** Check after export: the
diff against v2 is confined to the example's listing (and ids/dates); MAP reports 6 unsettled.

**Reading P7.** Side from the probe; whether the notes call the example an acceptance criterion, read
from `NOTES.md`. One run per format of round 15 built B without that wording, so a B here is read with
its notes.

## Inputs (commands and results)

Compiler: working tree at `674dc2f` (no `src/` change since `a5599ff`, 2026-10-18, which holds F7 D17);
`sddc 0.1.0.dev0`; suite **767 passed** (2026-10-28).

| Step | Command (from the trial root `..`) | Result |
|---|---|---|
| Store | `.sdd/`, `sdd/` of `../r13c-zero2repo-3cases/work/compile-case006` → `work/compile-v3`; `work/spec-planted/*.md` over `sdd/specs/` | base store unchanged since 2026-10-15 (mtimes); planted spec identical to round 14's (`diff -rq`) |
| Ingest | `sddc --json ingest` | 7 changed, 458 unchanged (same as round 14's v2) |
| Lock | `.sdd/lock` replaced by round 14's `work/compile-planted-v2/.sdd/lock` | |
| Compile | `bash batch-3/notes/compile_v3.sh` (one pass) | **0 calls, $0.00**: 1 690 candidates, 0 judged, 1 690 replayed; 10 opened. Store conflicts: 155, members identical to v2's |
| Example flag | N-001013 (P7's example) in `.sdd/nodes/metavar.jsonl` | v2 `flags: []`, v3 `flags: ['example']`; nothing else differs on the node |
| False alarms | `bash batch-3/notes/judge_false_alarms.sh` (CF-000148, 149, 154 false, batch 1's exact notes) | ADJ-000069–71 |
| Export | `sddc --root work/compile-v3 --json export --allow-open --out work/export-v3` | exit 0; MAP "unsettled contradictions: 6"; **40 197 words** (v2 40 212); `work/export-v3.sha256` |
| Diff v2 → v3 | `diff -r work/export-v2 work/export-v3` | only `export.meta.json` (hash, sizes), MAP row 20 (word count), and pack 20: `- [N-001013] example of N-000326` added under the claims, and *Acceptance criteria* now "None." (was the example, "verifies: N-000326") |
| Task | `SPEC_DIR=work/spec-planted python3 notes/build_task.py case006 work/tasks/case006-planted-export-v3 work/export-v3` | 40 197 words; `diff -rq` against the v2 task: only 3 files under `environment/spec/` differ |

## Checks before model runs (no model)

```text
bash notes/check_nop.sh case006-planted-export-v3
-> case006-planted-export-v3 exit 0 {"reward": 0.0, "tests_passed": 0, "tests_total": 0, ...}  (same as v2)
```

## Runs

Unattended chain started 2026-10-28 09:28 (`../../run_queue.sh batch-3`, then round 16); driver log
`run_queue.log`; queue `queue.tsv`. 3 of 3 runs completed on the first attempt; no early stop, no
replacement, no limit pause (5-hour usage 0.55 after the last run). Token string absent from
`runs/` and `work/jobs/` (`grep -rl`, 0 files).

## Results

| Run | Tests | Core | Sides P1 P2 P3 P4 P6 P7 R1 | Named (of 7) | Turns | $ est. | Time (s) |
|---|---|---|---|---|---|---|---|
| r15c export-1 | 436 | 433 | **B** A A **B** A A A | 6 (all but P4) | 84 | 0.6927 | 1 314 |
| r15c export-2 | 459 | 452 | A A A A A A A | 7 | 58 | 1.1175 | 924 |
| r15c export-3 | 460 | 453 | A A A A A A A | 7 | 66 | 1.0431 | 985 |

Sources: tests and $ from `results.json` / `run_queue.log`; core and sides from `notes/scores.json`;
named from `notes/detection.tsv`; time is Harbor's wall time in `run_queue.log`. Total **$2.8534 est.**
(`results.json`). Every transcript contains both sides' phrases of all 7 items (exposure). In every
row of `detection.tsv` the built side matches the probe.

**P7.** Built A (`INTEGER`) in **3 of 3** runs. Each run's notes list CF-000152 and choose "the type
name" / "the stated rule" / "the general rule"; none calls the example an acceptance criterion. On
export v2 the same item was built B in 4 of 4 runs, 3 calling it the acceptance criterion
(`../batch-2/TRIAL.md`).

**Other B sides (export-1 only).** P1: the notes name CF-000153 and choose "always left in place,
following the later, explicit claim". P4: the notes state the planted rule as a choice "where the
spec was silent or underspecified" and do not mention FP-03's opposite sentence; read as *not named*
(borderline, left for the owner's audit).

## Findings

1. **Listing the example as `example of N-…` (F7 D17) removed the P7 bias in these runs.** P7 side B:
   0 of 3 on export v3, against 4 of 4 on export v2. The only difference between the two tasks is
   that listing (3 spec files; "Inputs"). n = 3 against 4, Haiku, one case: consistent with the
   acceptance-criterion reading of batch 2, not proof of it.
2. **Detection holds on the new export.** Named 20 of 21 (P4 is the one miss, in export-1). Round 15
   on export v2: 27 of 28.
3. **Core on export v3**: 433, 452, 453. Round 15's export v2 runs: 454, 454, 435, 428; Markdown:
   430, 423, 456, 446 (`../notes/scores.json`, `../batch-2/notes/scores.json`). Inside the earlier
   spread; no claim of a difference.
4. **Recompile cost nothing.** Lock replay: 0 calls, $0.00; the same 155 store conflicts.

## Files

| Path | Tracked | What |
|---|---|---|
| `TRIAL.md` | yes | This description |
| `trial.env`, `queue.tsv`, `run_queue.log` | yes | Conditions, queue, driver log |
| `results.json` | yes | `../../summarize.py` |
| `runs/<run_id>/` | yes | Judge's files, `app.tgz`, `agent.tgz`, `NOTES.md` |
| `notes/` | yes | `score.py`, `probe.py`, `probe.sh`, `footprint.json` (copied from batch 2), `compile_v3.sh`, `judge_false_alarms.sh`, `scores.json`, `detection.tsv` |
| `../work/compile-v3`, `../work/export-v3`, `../work/tasks/case006-planted-export-v3` | **no** | Store, export, task (with hidden tests) |
| `work/jobs/` | **no** | Harbor jobs |
