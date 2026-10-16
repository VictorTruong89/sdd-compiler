# r13c-zero2repo-3cases

> Opened 2026-10-14. State: **closed 2026-10-16** (24 runs done; crontab line removed). Approved by the owner 2026-10-14: "run haiku and sonnet on all
> 3 cases (case010, case006, case016) for both plain markdown and spec-graph export. Each combination
> (haiku/sonnet + case010/006/016 + markdown/export) run twice. add periodical check for each run
> finishes and daily claude credit limit, and resume in case of interruption or claude forget to
> conclude the ongoing run. Check if there is any differences in failed/passed test between markdown
> and export, and why fail. finally note down all about this run for future report writing."
> Update this file at every step; it is the description a later session starts from.

## Question

On the three Zero2Repo cases Haiku failed from the Markdown in the sweep (`../r13b-zero2repo-haiku-sweep/`),
does the spec-graph export change which hidden tests pass, for Haiku and for Sonnet? For every test that
differs between the formats, and every test that fails, why?

## Design

| Item | Value |
|---|---|
| Benchmark / cases | Zero2Repo `0ecc523`: **case010** (nltk, 8 412 words, 197 tests), **case006** (click, 14 138 words, 476 tests), **case016** (sloptrim, Python + Node, 18 964 words, 388 tests) |
| Formats | Markdown (the case's `public/` files) and the spec-graph export of the same files |
| Models | Haiku (`anthropic/claude-haiku-5-5`), Sonnet (`anthropic/claude-sonnet-5-5`) |
| Runs per cell (n) | 2 → 3 cases × 2 models × 2 formats × 2 = **24 runs**. The sweep's single Haiku Markdown run per case is kept separately (not counted in n) |
| Agent | Claude Code 2.1.296, Harbor 0.24.0, tools `Bash Edit Read Write`, allow-list (model API, PyPI), $10 ceiling, 7 200 s agent timeout (`trial.env`) |
| Scorer | Zero2Repo's own judge unchanged (`official_reward`, binary); per-test counts and the failed-test list from the judge's report (`reward.json`, `reward_detail.json`) |
| Compile | `sddc` with the round-13 profile (Haiku via Claude Code, 300 calls per pass), resumed pass after pass until the graph and the conflict judging are complete |
| Contradictions | judged by the agent on the owner's behalf against the specification, as in round 13's follow-up (`sddc conflicts judge`, one-line reason each, `notes/verdicts-<case>.tsv`); export **without** `--allow-open`. Round 13 showed unsettled false contradictions led Haiku astray |
| Order | the 12 Markdown runs first (while the compiles run), then the 12 export runs as each case's export is ready; models alternate. A time-of-day difference between formats cannot be excluded |

## Unattended operation

| Part | What it does |
|---|---|
| `../run_queue.sh` | one run at a time; waits out a usage limit (reset time or 30-min probe); **new**: after each run logs the subscription's usage from Claude Code's `rate_limit_event` (5-hour and 7-day windows) and pauses new runs at ≥ 0.90 of the 5-hour or ≥ 0.95 of the 7-day window until that window resets |
| `../watchdog.sh` (cron, every 10 min) | restarts a dead driver; sets a row left `running` back to `pending`; runs `notes/watchdog_hook.sh`, which restarts any unfinished compile; writes `work/watchdog.status`; logs actions to `watchdog.log`. `touch STOP` makes it idle |
| `notes/compile_case.sh <case>` | init + ingest + compile passes until complete (`DONE`); after 6 failed passes or 20 passes, `FAILED` and no restart |
| Claude session check-ins | a scheduled check-in in the Claude session reads the logs, builds exports when compiles finish, releases export rows and writes results. **If the session is gone**, a new session starts from this file: see "Resume" |

### Resume (for a new session)

1. Read this file, `queue.tsv`, `run_queue.log`, `watchdog.log`, `work/watchdog.status`,
   `work/compile-<case>/compile.log`.
2. For each case with `work/compile-<case>/DONE` and export rows still `hold`: `sddc conflicts` in
   the store, judge each contradiction against the specification (`notes/verdicts-<case>.tsv`), export
   without `--allow-open` to `work/compile-<case>/export`, build the task
   (`python3 notes/build_task.py <case> work/tasks/<case>-export work/compile-<case>/export`), run the
   nop check, then set that case's export rows to `pending`. The watchdog starts the driver.
3. When every row is `done`/`failed`: `python3 ../summarize.py .`, token check
   (`grep -rl "sk-ant-oat01" work/jobs runs` must be empty), compare failed tests between formats
   (`notes/compare.py`), remove the crontab line, write Results and Findings here and in
   `sdd/design/rel-02/rel02_report_draft.md` R4.

## Inputs (how each was made; commands)

1. Adapter output for the cases (made in round 13b): `zero2repo-harbor --case-id caseNNN --force`.
2. Markdown tasks: `python3 notes/build_task.py caseNNN work/tasks/caseNNN-markdown` (builder copied
   from round 13b with the export mode added; case010's task is identical to 13b's apart from the
   description line).
3. Compiles: `work/compile-<case>/` by `notes/compile_case.sh`; results below.

| Case | Compile complete | Passes | Calls | `cost_usd` est. | Contradictions (all judged false) | Export words (× Markdown) | Export sha256 (of `export.sha256`) |
|---|---|---|---|---|---|---|---|
| case010 | 2026-10-15 07:32 | 12 (most stalled on usage limits and the PATH bug) | 386 | 2.0344 | 15 (`notes/verdicts-case010.tsv`) | 42 230 (5.0), 23 packs | `661014fdc6aae947…` |
| case006 | 2026-10-15 17:53 | 16 (same stalls; passes 13–16 judged conflict pairs) | 853 | 4.2647 | 68 (`notes/verdicts-case006.tsv`) | 75 090 (5.3), 20 packs, 1 012 nodes | `4be62edf857541cb…` |
| case016 | 2026-10-15 18:41 | 16 (same stalls; passes 12–16 judged conflict pairs) | 939 | 4.8569 | 62 (`notes/verdicts-case016.tsv`) | 100 089 (5.3), 35 packs, 1 097 nodes | `5cc761f53f5dde9a…` |

Export task do-nothing checks: case010 0, case006 0, case016 0 / 388; official 0, no Harbor exception.

case006's 68 contradictions (judged 2026-10-15): every one is a rule paired with an exception or
condition the same text states (e.g. options on the help page unless hidden), two different
components or settings (File versus Path type; option versus context `show_default`), or a word read
in two senses ("sequence": a default-map value versus an ANSI escape). One judgement is a reading
the text leaves partly open: CF-000085 / CF-000099, whether the runner's echo-stdin mode echoes hidden
input; kept as "hidden input is never echoed" (PRD 280 and 404 give no mode exception).


case016's 62 contradictions (judged 2026-10-15): the same kinds, plus many that pair two different
components with similar outputs (the detector command, the saved-file hook, the `check` command, the
session-start hook) or replies scoped by level (`lite` / `full` / `strict`, `off`). One reading the
text leaves partly open: CF-000151, whether an invisible character inside a code block is a finding;
kept as "no" (PRD 98 excludes code blocks from findings; PRD 130 does not override it).

## Checks before model runs (no model)

- Markdown tasks: the builder's Markdown mode is unchanged from round 13b, whose do-nothing checks
  scored 0 on these three cases and whose positive control scored 258 / 258 (`../r13b-zero2repo-haiku-sweep/TRIAL.md`).
- Driver usage guard tested on a saved transcript: logs `five_hour 0.37 … seven_day 0.23`; with the
  threshold set below the reading, it pauses until the window's reset.
- Watchdog: a second pass right after the first started nothing twice. Found and fixed on the way:
  the first version's children inherited its pass lock, so every later pass exited at once.
- Export tasks: a do-nothing check each, when built.
- 2026-10-15 00:27, usage at 0.78 of the 5-hour window: `notes/compile_case.sh` changed so that a
  pass with no model call or with failed blocks (most likely a usage limit) waits 30 min and counts
  as a failure, instead of starting the next pass at once and using up the 20 passes. The file was
  replaced (not edited in place), the three old wrappers stopped; their first `sddc compile` passes
  kept running and the watchdog starts the new script when each ends.
- 2026-10-15 01:10–02:25, **compile passes 2–4 did nothing**: the first passes stopped at the
  5-hour usage limit (75–79 calls each, `compile-1.json`: "You've hit your session limit"); the
  watchdog restarted the compiles from cron, where `claude` (in `~/.local/bin`) is not on PATH, so every
  later pass stopped with "`claude` is not on PATH" and counted as a failure (3 of 6 used).
  `~/.local/bin` added to PATH in `notes/compile_case.sh` and `../watchdog.sh` (the driver's limit probe
  also calls `claude`). Stopping the old wrappers was not enough: their `sleep 1800` children kept the
  compile locks and had to be stopped too. Verified by a watchdog pass with an empty environment
  (`env -i`); passes 5 started 02:25 and ran.
- 2026-10-15 03:44–07:24, **compiles stopped as FAILED before the usage reset**: passes 5 hit the
  5-hour limit at 03:44 (reset 07:10); every 30-min retry stalled and counted as a failure, so all
  three reached 6 failures at 06:14 and wrote `FAILED`. `notes/compile_case.sh` now recognises a
  usage-limit stop ("hit your … limit", 429) and waits until the reset time in the message + 5 min,
  not counted as a failure. `FAILED` removed, restarted 07:24 (passes 12, 12, 11). State then:
  case010 graph complete (0 pending), 282 conflict pairs unjudged, 15 contradictions so far; case006
  177 blocks pending; case016 124 pending. The driver, meanwhile, waited out the same limit as
  designed (`sonnet-case010-markdown-2` limited at 03:44, rerun 07:15).

- 2026-10-15 19:07, **watchdog blind while the driver ran**: the subshell that launches the driver
  inherited the watchdog's pass lock (fd 7; `7>&-` was on the driver command only, not the subshell),
  and stayed alive as the driver's parent, so every watchdog pass from 18:40 exited at once (no status,
  no compile hook). Runs and compiles were not affected. `../watchdog.sh` now closes fd 7 on the whole
  subshell (file replaced, not edited in place); the lingering subshell was stopped (the driver, in its
  own session, kept running) and a pass in an empty environment wrote the status again.

## Runs

Queue in `queue.tsv`; log in `run_queue.log`; files per run in `runs/<run_id>/`; table built by
`python3 ../summarize.py .` into `results.json`.

## Results

All 24 runs `done` (closed 2026-10-16 00:38). Tests: judge's passed / total (`runs/<run_id>/reward.json`);
official: Zero2Repo's binary reward; `$`: Claude Code's `total_cost_usd`, an API-equivalent estimate,
of the counted attempt; time: Harbor's whole run (`run_queue.log`). Also in `results.json`.

| Run | Tests | Official | Turns | $ est. | Time (s) |
|---|---|---|---|---|---|
| haiku-case010-markdown-1 | 162 / 197 | 0 | 44 | 0.5506 | 707 |
| haiku-case010-markdown-2 | 169 / 197 | 0 | 47 | 0.7151 | 811 |
| haiku-case010-export-1 | 168 / 197 | 0 | 67 | 1.3220 | 1 112 |
| haiku-case010-export-2 | 166 / 197 | 0 | 78 | 1.0555 | 817 |
| sonnet-case010-markdown-1 | 175 / 197 | 0 | 22 | 2.1815 | 890 |
| sonnet-case010-markdown-2 ¹ | 176 / 197 | 0 | 21 | 2.1427 | 912 |
| sonnet-case010-export-1 ¹ | 176 / 197 | 0 | 29 | 2.3617 | 902 |
| sonnet-case010-export-2 | 175 / 197 | 0 | 24 | 1.6977 | 704 |
| haiku-case006-markdown-1 | 452 / 476 | 0 | 42 | 0.9022 | 895 |
| haiku-case006-markdown-2 | 0 (tests did not load) | 0 | 26 | 0.1145 | 725 |
| haiku-case006-export-1 | 425 / 476 | 0 | 77 | 1.0045 | 1 263 |
| haiku-case006-export-2 | 467 / 476 | 0 | 63 | 1.4731 | 1 203 |
| sonnet-case006-markdown-1 | 470 / 476 | 0 | 26 | 2.4009 | 927 |
| sonnet-case006-markdown-2 | 469 / 476 | 0 | 24 | 2.3553 | 926 |
| sonnet-case006-export-1 | 473 / 476 | 0 | 30 | 2.1689 | 753 |
| sonnet-case006-export-2 | 470 / 476 | 0 | 31 | 2.7664 | 1 017 |
| haiku-case016-markdown-1 | 381 / 388 | 0 | 33 | 0.8529 | 1 130 |
| haiku-case016-markdown-2 | 378 / 388 | 0 | 47 | 0.9487 | 1 462 |
| haiku-case016-export-1 | 364 / 388 | 0 | 80 | 1.1296 | 2 117 |
| haiku-case016-export-2 | 379 / 388 | 0 | 87 | 1.3504 | 1 246 |
| sonnet-case016-markdown-1 | 385 / 388 | 0 | 25 | 2.3885 | 1 186 |
| sonnet-case016-markdown-2 ¹ | 387 / 388 | 0 | 38 | 2.3986 | 1 426 |
| sonnet-case016-export-1 | 387 / 388 | 0 | 37 | 2.1847 | 1 186 |
| sonnet-case016-export-2 | **388 / 388** | **1** | 27 | 2.1454 | 952 |

¹ A first attempt stopped at the 5-hour usage limit and was rerun after the reset (the driver keeps
the stopped job as `.attemptN`); those attempts cost $4.3673 est. together and are not counted.

**Cost (est.):** counted runs $38.6116, stopped attempts $4.3673, compiles $11.1560 (case010 2.0344,
case006 4.2647, case016 4.8569): **$54.1349**. Seven-day usage went from 0.23 (2026-10-14) to 0.67.

**Tests that cannot pass in our tasks (case010, 20 tests).** 20 case010 tests need NLTK model files in
`/opt/models` (an English and a Russian perceptron tagger, the punkt sentence model, the NE chunker:
`Zero2Repo/benchmark/cases/case010/source/env/resources.json`). Zero2Repo's own runner (`cbrun`,
`fetch_resources.py`) downloads them before scoring; its Harbor adapter output (`output/case010/`) and
so our builder do not. Each of these tests stops with `HarnessError: host resource is missing or
empty: /opt/models/...` in every run, the 13b sweep's included, whatever the code. Read on the 177 scorable tests, case010 is:

| case010, 177 scorable | Markdown | Export |
|---|---|---|
| Haiku | 142, 149 (13b: 146) | 148, 146 |
| Sonnet | 155, 156 | 156, 155 |

case006 and case016 declare no such resources (no `source/env/`).

### Markdown versus export, test by test (`notes/compare.md`, `notes/compare.json`)

"Gain": failed in every Markdown run and in no export run; "loss": the reverse. For Haiku, the 13b
sweep's Markdown run (same task, only the description line differs) is counted as a further Markdown
run; `haiku-case006-markdown-2` (no tests loaded) is left out of the test sets.

| Case | Model | Gain | Loss | Failed in every run | Failed in some runs |
|---|---|---|---|---|---|
| case010 | Haiku (3 Markdown runs) | 0 | 0 | 26 (20 unscorable) | 13 |
| case010 | Sonnet | 0 | 0 | 20 (all unscorable) | 2 |
| case006 | Haiku (2 Markdown runs with tests) | 2 | 3 | 3 | — |
| case006 | Sonnet | 0 | 0 | 1 | 9 |
| case016 | Haiku (3 Markdown runs) | 0 | 0 | 2 | — |
| case016 | Sonnet | 0 | 0 | 0 | 5 |

Without the sweep run, Haiku case006 shows 12 gains (one Markdown run only) and case016 1 gain and 3
losses; the sweep run fails or passes those tests the other way, so they are run-to-run variation.

### Why tests fail (read from `final_tests.log` against the specification)

- **case010.** Besides the 20 unscorable tests: Haiku leaves the Snowball stemmers out (`NotImplementedError: Snowball algorithm for 'german' is not implemented in this build`), in both
  formats, and its Lancaster stemmer differs on single words (`multiply` → `multipl`/`multip`, expected
  `multiply`); some runs miss classifier details (naive Bayes ties at 0.5). Sonnet implements Snowball
  but its Arabic and Finnish stems differ from the reference (`lapset` → `lapse`, expected `laps`). The
  specification names the algorithms (Snowball, Lancaster) and does not give their rules; the tests
  check named word–stem pairs from the reference implementation. Neither format can supply them.
- **case006, Haiku gains (2):** `test_required_prompt_asks_on_omit_and_on_bare_flag`: both Markdown
  runs exit 2 with "Missing option" where the specification says "A required prompting option that is
  omitted prompts rather than failing as missing" (PRD 269). This is the rule behind contradiction
  CF-000034, judged false (the export shows it as a settled rule with its exception); a plausible link,
  not shown. `test_uuid_type_converts_text_and_is_never_inferred`: the UUID type is inferred from a
  default, which PRD 193 forbids ("never inferred automatically from a default").
- **case006, Haiku losses (3):** two completion tests: both export runs print the completion item
  objects (`<F12_acceptance._Suggest object at 0x…>`) instead of their `value`; IC §8 says a completer
  returns `str` or objects exposing `value`, `help`, `type`, and that each value appears verbatim. One
  help test: a subcommand's short help is not ellipsized to one line (PRD 104). The export carries both
  rules word for word (packs 12 and 19), so the text was there; why both export runs made the same
  mistake is not known.
- **case006, Haiku in every run (3):** completion for a custom type (same object-printing fault in the export runs); on/off pair with a
  non-dash prefix (`/k`) refused as "No such option" (PRD 136 "either prefix style", IC 123 "another declared prefix"); the
  pager test finds ANSI escapes on standard output where it expects none (reason not traced).
- **case006, Sonnet in every run (1):** `test_feature_switch_last_declared_wins_when_tied`: PRD 144
  states the tie rule ("If still tied, the last declared option wins"); Sonnet's code delivers the first
  declared flag's value, in all four runs.
- **case016, Haiku in every run (2):** the check command's five failure reasons collapse into fewer
  (IC 530–537 lists five distinct replies); TAG characters after an emoji flag's terminator are not
  reported as invisible characters (PRD 130, FP-03's keep rules). Sonnet's misses (0–3 per run, all
  different tests) are character-cleanup details: Unicode variation-selector and tag sequences that
  must be kept byte for byte, the over-cap guard, instruction-file stems.

## Findings

1. **The export did not change which tests pass.** With the settled export (every contradiction judged
   false), no test fails in every run of one format and in no run of the other, for either model, on
   case010 and case016; on case006 Haiku shows 2 such tests each way (above). Sonnet's totals overlap
   between formats on all three cases, and Haiku's on case010. On case006 and case016 one Haiku export
   run is the lowest of all Haiku runs (425; 364) and the other is at or above the Markdown runs (467;
   379, against 381, 378 and 13b's 370). n = 2 per cell.
2. **Sonnet is near the ceiling on all three cases in both formats** (case010 155–156 of 177 scorable,
   case006 469–473 of 476, case016 385–388 of 388), and passed a case in full once
   (`sonnet-case016-export-2`, official 1.0, the only full pass in this round).
3. **Haiku works longer on the export:** 63–87 turns against 33–47 on the Markdown runs that finished,
   in all three cases, at 1.4–1.9× the mean estimated cost per case; its scores do not rise with it. Sonnet's turns barely move (21–38
   both formats). Round 13 saw the same on case004 with the unsettled export; there the settled export
   brought Haiku's turns down to 20–35 (Markdown 24–26). Here the export is 5.0–5.3× the Markdown's
   words (42 230 to 100 089), against 6.1× on case004.
4. **What Haiku misses is mostly not a reading problem.** case010: algorithms the specification names
   without rules (Snowball, Lancaster); Haiku skips them, Sonnet approximates them. case006 and case016:
   single stated rules among hundreds (tie rule, five distinct replies, character classes), missed in
   both formats. In the two places the format seems to matter on case006, the rule is present in both
   formats; one (required prompting option) is the rule behind a contradiction the compiler raised and
   we settled.
5. **Benchmark fault found: case010 cannot be passed in full in our tasks.** 20 of 197 tests need model
   files that Zero2Repo's runner fetches and its Harbor adapter does not (Results). This changes round
   13b's reading of case010: Haiku's 31 misses there are 11 on the 177 scorable tests (146 / 177).
   case010 still separates the models (Haiku 142–149, Sonnet 155–156 of 177).
6. **Compiler on larger specifications:** 386, 853 and 939 Haiku calls ($2.03, $4.26, $4.86 est.); most
   of the calls on case006 and case016 went to judging conflict pairs (3 107 and 4 232 unjudged at one
   point). Contradictions found: 15, 68, 62; **all 145 judged false** on reading (a rule and its stated
   exception or condition, two different components, a word in two senses), as were the 18 of
   case004. Two judgements are readings the text leaves partly open (CF-000085/099 of case006,
   CF-000151 of case016).
7. **`haiku-case006-markdown-2` stopped early (valid run, scored 0).** After 26 turns ($0.11 est.)
   Haiku ended with "Much of the spec is still unimplemented, so this is a partial build, not the
   finished product". Its package lacks names the tests import (`File`, `Path`, `prompt`, …), so 12 of
   13 test files fail to import and the judge reports 0 tests (`final_tests.log`). Counted as 0.
8. **Unattended operation held over two days** (2026-10-14 to 16): the driver waited out the 5-hour
   limit 4 times (3 runs stopped and rerun), the compiles resumed after each reset. Faults found and
   fixed on the way: cron's PATH lacked `claude`; compiles counted usage-limit stops as failures; the
   watchdog's launching subshell held its lock while the driver ran (Checks section); `notes/compare.py`
   read a run with no tests loaded as "failed nothing" (fixed 2026-10-15; such runs are now shown and
   left out of the test sets).

## Open items

- case010 with the model files installed in the test image (Zero2Repo's `fetch_resources.py`, pinned
  URLs and sha256 in `resources.json`; the download goes to the image build, not the agent's network):
  rescoring the saved `app.tgz` of all 8 runs needs no model call.
- Whether to tell Zero2Repo its Harbor adapter leaves out the resource download (outward-facing; owner).
- Haiku case006: the 2 gains and 3 losses rest on 2 Markdown and 2 export runs; more runs would
  show whether they hold.

## Files

| Path | Tracked | What |
|---|---|---|
| `TRIAL.md` | yes | This description |
| `trial.env` | yes | Run conditions read by `../run_queue.sh` |
| `queue.tsv`, `run_queue.log`, `watchdog.log` | yes | Queue state, driver log, watchdog actions |
| `runs/<run_id>/` | yes | `result.json`, `reward.json`, `reward_detail.json`, `official_reward.json`, `final_report.json`, `final_tests.log`, `app.tgz`, `agent.tgz` |
| `results.json` | yes | Built by `../summarize.py` |
| `notes/` | yes | Builder, compile script, watchdog hook, verdicts, comparison |
| `work/` | **no** | Tasks (hidden tests), compile stores and exports, Harbor jobs, status |
