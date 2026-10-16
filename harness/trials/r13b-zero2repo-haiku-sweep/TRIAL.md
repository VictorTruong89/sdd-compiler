# r13b-zero2repo-haiku-sweep

> Opened 2026-10-14. State: **closed 2026-10-14** (8 runs done). Approved by the owner 2026-10-14: "in round 13, I want to
> test Haiku testing the original markdown of each project inside Zero2Repo, and determine which
> project that Haiku fail test. Then we can try testing our spec-graph export with this project
> further". Update this file at every step; it is the description a later session starts from.

## Question

Which Zero2Repo cases does Haiku fail from the plain Markdown specification? Purpose: case004 was at
the ceiling (Haiku 258 / 258 from Markdown, `../r13-zero2repo-case004/TRIAL.md`), so a format
comparison there can only show a loss. A case Haiku fails leaves room for the export to show a gain.

## Design

| Item | Value |
|---|---|
| Benchmark | Zero2Repo, commit `0ecc523` (`../../benchmarks/zero2repo/TRIAL.md`, 17 cases) |
| Cases in this batch | the 8 that run on a Python + Node image: case001, 002, 005, 006, 007, 010, 011 (Python), case016 (Python + Node, no npm packages). case004 already done (round 13) |
| Left out for now | case003, 012 (TypeScript: need npm packages, and the npm registry is not on the agent allow-list); case008 (C++20, cmake), 014 (C11), 015 (C99); case009, 013 (Go); case017 (Zig). Each needs its toolchain in the image (and for TypeScript, the npm registry on the allow-list) |
| Format | Markdown only (the case's `public/` files, unchanged) |
| Model | Haiku (`anthropic/claude-haiku-5-5`) |
| Runs per case (n) | 1: a screen. A failing case is followed up with more runs before export runs |
| Agent | Claude Code 2.1.296, Harbor 0.24.0, tools `Bash Edit Read Write`, allow-list (model API, PyPI), $10 ceiling, 7 200 s agent timeout |
| Scorer | Zero2Repo's own judge unchanged: `official_reward` (1 only if every test passes); per-test counts from the judge's own report (`final_report.json`) into `reward.json` (`tests_passed / tests_total`) |
| Order | smallest specification first: 001, 007, 011, 002, 005, 010, 006, 016 |

## Inputs (how each was made; commands)

1. Adapter output for all 17 cases (no model):
   `../../benchmarks/zero2repo/download/.venv/bin/zero2repo-harbor --case-id caseNNN --force`. All 17
   get the same image (Python 3.13 + Node 22 + Claude Code/opencode/codex `@latest`); no Go, Zig, C or
   C++ compiler, so the non-Python cases expect the agent to install toolchains over an open network.
2. Tasks: `python3 notes/build_task.py caseNNN work/tasks/caseNNN-markdown`. Generalised from round
   13's builder: same conditions and the same two adapter fixes (test folder and manifest from the case);
   Node 22 added to the image; the per-test score is read from the judge's report instead of a second
   pytest pass, so each case's own test command and `PYTHONPATH` are used unchanged.

| Case | Upstream (`../../benchmarks/zero2repo/TRIAL.md`) | Spec words (all public files) | Tests (judge total) |
|---|---|---|---|
| case001 | hukkin/tomli | 4 860 | 302 |
| case007 | pyauth/pyotp | 5 122 | 80 |
| case011 | jmespath/jmespath.py | 7 002 | 321 |
| case002 | envfilehq/python-envfile | 7 202 | 281 |
| case005 | python-hyper/h11 | 7 915 | 395 |
| case010 | nltk/nltk | 8 412 | 197 |
| case006 | pallets/click | 14 138 | 476 |
| case016 | seyedehsanhadi/sloptrim | 18 964 | 388 |

Totals are filled from the first run that collects all tests; with no code most cases fail collection
(import error), so the judge reports 0.

## Checks before model runs (no model)

| Check | Job (`work/jobs/`) | Result |
|---|---|---|
| Positive control: round 13's `sonnet-markdown-1` code (258 / 258) through this builder (case004, oracle agent extracts the saved `app.tgz`) | `control-case004-oracle` | **258 / 258, official 1.0**: the report-based per-test score matches. (First attempt: Harbor raised `VerifierOutputParseError` on the null `judge_error`, unnoticed until case001; rerun after the fix with no exception, `control-case004-oracle`; the first kept as `.reward-null-bug`) |
| Do-nothing, each of the 8 tasks | `check-nop-caseNNN-markdown` (`work/check_nop.log`) | **all 0**, official 0. case005: 0 / 395, case016: 0 / 388; the other 6 fail collection ("pytest execution was incomplete") |

## Runs

Queue in `queue.tsv`; log in `run_queue.log`; files per run in `runs/<run_id>/`; table built by
`python3 ../summarize.py .` into `results.json`.

## Results

One Haiku run per case, Markdown. Tests: judge's passed / total (`runs/<run_id>/reward.json`);
official: Zero2Repo's binary reward; `$`: Claude Code's `total_cost_usd`, an API-equivalent estimate;
time: Harbor's whole run (`run_queue.log`). Table also in `results.json`.

| Case | Upstream | Spec words | Tests | Official | Turns | $ est. | Time |
|---|---|---|---|---|---|---|---|
| case001 | tomli | 4 860 | 302 / 302 | 1.0 | 14 | 0.0498 | 280 s |
| case007 | pyotp | 5 122 | 80 / 80 | 1.0 | 16 | 0.0253 | 145 s |
| case011 | jmespath | 7 002 | 321 / 321 | 1.0 | 20 | 0.2693 | 466 s |
| case002 | python-envfile | 7 202 | 281 / 281 | 1.0 | 24 | 0.0726 | 351 s |
| case005 | h11 | 7 915 | 395 / 395 | 1.0 | 22 | 0.3708 | 833 s |
| **case010** | nltk | 8 412 | **166 / 197** | **0** | 33 | 0.4539 | 736 s |
| **case006** | click | 14 138 | **464 / 476** | **0** | 81 | 1.2422 | 1 002 s |
| **case016** | sloptrim | 18 964 | **370 / 388** | **0** | 53 | 0.5550 | 1 368 s |

Total $3.0389 est. With case004 (round 13: 258 / 258 twice), Haiku passes 6 of the 9 Python cases
in full from the Markdown and fails 3: the three largest specifications (8 412 to 18 964 words; the passes are 4 860 to 7 915).
n = 1 per case: a screen, not a rate.

### What the failures are

- **case010 (nltk), 31 misses: parts left out.** Haiku's code raises `NotImplementedError` for
  required parts: "no Snowball algorithm for 'german' is built in; install the snowballstemmer
  package", "ARLSTem stemming is outside this specification". Snowball for the listed languages is
  required (`Full_PRD.md` 141, 143). For ARLSTem the specification says the families exist but
  "their stemming results are outside this specification" (`Full_PRD.md` 143); Haiku echoed that and
  raised, while the hidden tests only check that `ARLSTem()` constructs and `stem()` returns a string
  (corrected 2026-10-15; first written as "the specification requires them").
  Misses by feature: F03 13 (taggers), F02 11 (stemmers), F01 6 (sentence tokenizer, CLI), F04 1.
  **Correction 2026-10-16 (found in round 13c):** 20 of these 31 misses cannot pass in our task: they
  need NLTK model files in `/opt/models` that Zero2Repo's own runner downloads and its Harbor adapter
  does not (`../r13c-zero2repo-3cases/TRIAL.md`, Results). On the 177 scorable tests this run is
  146 / 177: Haiku's own misses are the Snowball and Lancaster stemmers and ARLSTem (11).
- **case006 (click), 12 misses: edge cases spread over 8 features** (e.g. env-var lists split on
  `os.pathsep`, UUID type never inferred, choice uniqueness after normalisation, prompt on a bare
  flag). Zero2Repo issue #4 reports another agent at 447 / 476 on the same case.
- **case016 (sloptrim), 18 misses: detection rules and limits** (catalogue rules firing or not,
  zero-width splitting, the archive size cap, five distinguishable failure reasons, help text).

## Findings

- **Haiku fails 3 of 9 Python cases from the Markdown** (case010, case006, case016; case010 with 11 of its own misses on 177 scorable tests, see the correction above); the specification
  appears to state what was missed in case010 (checked); case006 and case016 misses not yet read
  against the specification.
- **Two harness bugs, found on the first run (case001), fixed before the second.**
  (1) The builder wrote `judge_error: null` into `reward.json`; Harbor reads every value there as a
  number and rejected the run (`VerifierOutputParseError`). Now `reward.json` holds numbers only and
  the rest goes to `reward_detail.json`; tasks rebuilt. (2) The driver then looked for a usage limit
  and matched Claude Code's routine `rate_limit_event` line (`"status":"allowed"`, 8 % used), so it
  marked the run `limited` and began 30-minute probes. `../run_queue.sh` now drops lines with
  `"status":"allowed"` before matching. The driver was stopped, case001 was saved by hand from its
  job (agent ended normally, verifier ran: 302 / 302, official 1.0) and marked `done` with a note,
  and the driver restarted.

## Open items

- Choose the case for the export comparison (owner). Before export runs, repeat Haiku Markdown on it
  (n = 2 more) to confirm the failure is stable.
- The 9 cases left out (toolchains).

## Files

| Path | Tracked | What |
|---|---|---|
| `TRIAL.md` | yes | This description |
| `trial.env` | yes | Run conditions read by `../run_queue.sh` |
| `queue.tsv`, `run_queue.log` | yes | Queue state, driver log |
| `runs/<run_id>/` | yes | `result.json`, `reward.json`, `official_reward.json`, `final_report.json`, `final_tests.log`, `app.tgz` (agent's code), `agent.tgz` (transcript, trajectory) |
| `results.json` | yes | Built by `../summarize.py` |
| `notes/build_task.py`, `notes/check_nop.sh` | yes | Task builder for any case; do-nothing checks |
| `work/` | **no** | Tasks (with hidden tests; Zero2Repo has no licence file), Harbor jobs, checks |
