# r13d-zero2repo-case006-lean-export

> Opened 2026-10-16. State: **closed 2026-10-16** (2 runs done). Approved by the owner
> 2026-10-16: "implement X1-X5 ; then run Haiku case006 export only 2 runs to compare with previous
> trial." Update this file at every step; it is the description a later session starts from.

## Question

Does the lean export (F7 D15, D16: rel02 S15 options X1–X5) bring Haiku's turns and context on case006
toward the Markdown's, without losing tests, compared with round 13c?

## Design

| Item | Value |
|---|---|
| Benchmark / case | Zero2Repo `0ecc523`, **case006** (click renamed Optlyn, 14 138 Markdown words, 476 tests) |
| Formats | the **lean export** only. Comparison: round 13c's 2 Haiku export runs (old export) and 2 Haiku Markdown runs (`../r13c-zero2repo-3cases/`) |
| Models | Haiku (`anthropic/claude-haiku-5-5`) |
| Runs per cell (n) | 2 |
| Agent | Claude Code 2.1.296, Harbor 0.24.0, tools `Bash Edit Read Write`, network allow-list; same `trial.env` and driver as 13c |
| Ceiling | $10 per run (`trial.env`) |
| Scorer | Zero2Repo's own judge unchanged (`official_reward`, binary); per-test counts from `reward.json` / `reward_detail.json` |
| Same as 13c | the store (`../r13c-zero2repo-3cases/work/compile-case006/`, 68 contradictions judged false), `instruction.md`, `task.toml`, Dockerfile, tests. **Only `spec/` differs** (`diff -rq`) |
| Measures | tests passed; turns (`num_turns`); requests; context after spec reading, peak context, Σ cache read, Σ output (session JSONL `usage`); `total_cost_usd`; which spec files were read and how |

## Inputs (how each was made; commands)

1. **Compiler change** (F7 amended 2026-10-16: D15, D16, AC-7.25–7.27; `src/sdd_compiler/export/`).
   Whole suite 759 passed.
   - X1: Claims list without node text (`- [N-…] kind · modality · layer[ · label][ · needs …]`).
   - X2: `CHECKLIST.md` ids only (with a label when it differs from the id).
   - X3: tag lines ids only (`↳ N-000677–N-000679`), ranges for 3+ consecutive ids.
   - X4: a unit over 20 000 characters of block text splits at its next heading (`MAX_UNIT_CHARS`).
   - X5: `MAP.md` units table gives each pack's words; "How to use" item 3 says Text is the spec.
2. **Export** (no model call): `sddc --root ../r13c-zero2repo-3cases/work/compile-case006 export --out
   $PWD/work/export-case006` → 33 packs, 1 012 nodes, 0 unsettled.
3. **Task:** `python3 notes/build_task.py case006 work/tasks/case006-export work/export-case006`
   (builder copied from 13c, unchanged).

| Measure (case006 export) | Round 13c | This round | Markdown |
|---|---|---|---|
| Words (`.md` files) | 75 090 | **39 162** (2.8×) | 14 138 |
| Files in `spec/` | 23 (20 packs) | 36 (33 packs) | 3 |
| Largest pack | 32 520 words · 188 025 chars (pack 19) | 3 280 words · 19 530 chars (pack 21, FP-03) | — |
| `CHECKLIST.md` | 23 151 | 4 241 | — |
| Claims to implement | 22 128 | 7 897 | — |
| `↳` tag lines | 7 585 | 1 302 | — |
| Related elsewhere | 5 233 | 6 760 (more cross-pack links after the split) | — |
| `MAP.md` | 882 | 1 473 (33 rows, words column) | — |

Source: `wc -w` and a section-splitting count, 2026-10-16. The Text sections are 14 394 words (13c:
14 238; more headings re-emitted by the split packs).

## Checks before model runs (no model)

| Check | Job | Result |
|---|---|---|
| Do-nothing, lean export task | `work/jobs/check-nop-case006-export` | 0 tests, official 0, no Harbor exception (13c's export task: 0, the same) |
| Task identical to 13c's except `spec/` | `diff -rq` | yes |

## Runs

Queue in `queue.tsv`; log in `run_queue.log`; files per run in `runs/<run_id>/`; table built by
`python3 ../summarize.py .` into `results.json`. Driver started 2026-10-16 07:41.

## Results

Tests: judge's passed / total (`runs/<run_id>/reward.json`). Turns: Claude Code's `num_turns`. Requests,
context and token sums: session JSONL `usage` via `notes/reading_trace.py` (same script on the 13c runs).
"Context into planning" is the context entering the run's largest-output request, which in every
run here is the one planning request after the spec was read. `$`: `total_cost_usd`, an
API-equivalent estimate.

| Run | Export | Tests | Turns | Requests | Context into planning | Planning output (stop) | Peak context | Σ cache read | Σ output | $ est. | Time (s) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **13d haiku-export-1** | lean | **447** | 95 | 73 | 65 582 | 128 000 (`max_tokens`) | 234 574 | 10 390 570 | 285 187 | 0.9954 | 1 418 |
| **13d haiku-export-2** | lean | **415** | 71 | 50 | 72 062 | 128 000 (`max_tokens`) | 180 004 | 5 761 875 | 229 924 | 0.5920 | 1 038 |
| 13c haiku-export-1 | old | 425 | 77 | 57 | 95 632 | 128 000 (`max_tokens`) | 247 411 | 9 164 878 | 270 645 | 1.0045 | 1 263 |
| 13c haiku-export-2 | old | 467 | 63 | 63 | 48 734 | 94 689 | 336 197 | 13 910 304 | 272 250 | 1.4731 | 1 203 |
| 13c haiku-markdown-1 | Markdown | 452 | 42 | 39 | 37 998 | 110 274 | 253 183 | 7 724 852 | 207 420 | 0.9022 | 895 |
| 13c haiku-markdown-2 | Markdown | 0 (stopped) | 26 | 19 | 37 294 | 128 000 (`max_tokens`) | 76 395 | 960 954 | 166 711 | 0.1145 | 725 |

13b sweep's Haiku Markdown run on the same task: 464 / 476. Cost of this round: $1.5874 est.;
seven-day usage 0.72 after the runs (`run_queue.log`). No token string in `work/jobs` or `runs`.

**How the spec was read** (`notes/reading_trace.py`):
- Both runs began at `MAP.md`, as instructed, then read every pack in order, in 13 and 14 shell
  calls, all before writing code. **No output was saved to a file** (13c: pack 19 overflowed in every
  export run).
- Both still stripped the lists. Run 1 read packs 01–18 whole, then only `## Text` without `↳` lines
  for packs 19–33. Run 2 piped packs 14–33 through `grep -v '^↳'` and `grep -v '^- \[N-'` and dropped
  section headings. The checklist was read at its head (60 and 300 lines), not ticked.
- Context entering the planning request: 65.6k and 72.1k tokens, against 95.6k and 48.7k on the old
  export and 37–38k on the Markdown.

**Where the turns went** (tool calls by kind, a keyword classification of each call's input):

| Run | Spec / notes | Write or edit code | Run or try code | Other | All |
|---|---|---|---|---|---|
| 13d export-1 | 14 | 71 | 6 | 2 | 93 |
| 13d export-2 | 14 | 45 | 8 | 2 | 69 |
| 13c export-1 | 22 | 31 | 18 | 4 | 75 |
| 13c export-2 | 9 | 40 | 9 | 4 | 62 |
| 13c markdown-1 | 4 | 27 | 6 | 4 | 41 |

**Tests, set by set** (`reward_detail.json`): 15 tests failed in both 13d runs. 6 of them failed in no
13c export run (among them `test_required_prompt_asks_on_omit_and_on_bare_flag`, 13c's export
"gain"). 4 tests that failed in both 13c export runs pass in both 13d runs: the two completion tests
(13c's export "losses"), the custom-type completion test and the pager-styles test.

## Findings

1. **The lean export did not reduce Haiku's turns.** 95 and 71 turns (73 and 50 requests), against 77
   and 63 (57 and 63) on the old export and 42 on the Markdown. Tests 447 and 415, within the spread of
   the 13c runs of both formats (425–467). n = 2: no test-level effect can be claimed either way.
2. **It did what it was built to do on the reading side.** Words 75 090 → 39 162; no pack over Claude
   Code's inline limit, so no output was saved to a file and no file was paged. Context entering the
   planning request fell for run 1's pattern (95.6k → 65.6k) but stays above the Markdown's 38k,
   because the agents still `cat` most packs whole before cutting.
3. **The extra turns are code-writing turns, and they follow the output cap.** Both 13d runs hit the
   128 000-token output cap in the planning request (`stop_reason: max_tokens`). Claude Code then
   injects "Output token limit hit. Resume directly … Break remaining work into smaller pieces", and
   Haiku answered "I'll write the package in modules" / "in small files". The two runs then made 71
   and 45 code write/edit calls, against 27 in the Markdown run that did not hit the cap. In 13c, the
   cap was hit by export-1 and markdown-2 (which then stopped on a misread budget). This is an
   association on 6 runs, **not shown to be the cause**.
4. **Haiku's planning thought is close to the cap in every case006 run, in both formats**: 94.7k–128k
   output tokens, 4 of 6 runs at the 128k cap. Whether a run crosses the cap may matter more for turns
   than the export format does. The export's size may raise the chance (a longer input to plan from),
   *to be measured*.
5. **Agents still strip the lists**, even when they are ids only: both runs filtered `↳` and claim
   lines with `grep -v`. The lists cost little now (Claims 7 897, checklist 4 241 words), and nothing
   shows they are used during reading.

## Open items

- Whether the output cap drives the turn count: compare runs that hit it and runs that do not, with
  more runs (both formats), or cap thinking (Harbor's `MAX_THINKING_TOKENS` env var exists in its
  Claude Code agent; not used so far). Needs the owner's go-ahead (model runs).
- Whether to drop the lists from the reading path entirely (a Text-only pack plus a separate index),
  since the agents remove them anyway.
- Markdown runs on the same day were not repeated; the comparison uses 13c's Markdown runs.

## Files

| Path | Tracked | What |
|---|---|---|
| `TRIAL.md` | yes | This description |
| `trial.env` | yes | Run conditions read by `../run_queue.sh` |
| `queue.tsv`, `run_queue.log` | yes | Queue state, driver log |
| `runs/<run_id>/` | yes | `result.json`, reward and report files, `app.tgz` (agent's code), `agent.tgz` (transcript, trajectory) |
| `results.json` | yes | Built by `../summarize.py` |
| `notes/` | yes | `build_task.py` (copied from 13c), `check_nop.sh` (copied from 13b), `reading_trace.py` (reads and tokens from transcripts) |
| `work/` | **no** | Lean export, task (with hidden tests), Harbor jobs |
