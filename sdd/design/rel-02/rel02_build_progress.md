# Release 02 — Build progress

> **SDD role:** `design/` tier — NON-AUTHORITATIVE. What has been done, in order, with its evidence.
> The plan, the decisions and the open questions are in [`rel02_brainstorm.md`](rel02_brainstorm.md);
> this file only records progress against it. Opened 2026-10-12.
>
> Rules: a step is "done" only when its "done when" in the brainstorm holds. Every number names the
> command or file it came from. Anything not measured is written *to be measured*.

## Board — the ten milestones (rel02 D6)

| # | Milestone | State | Evidence / where |
|---|---|---|---|
| 1 | Try the candidate benchmarks | **DONE 2026-10-12** — **9 of 9 tried** (SWE-Dev added and tried after the first eight) (two of them only in part: ProgramBench, Inspect AI; one not obtainable: RealBench) | §"Milestone 1" below |
| 2 | Choose benchmark, platform, metrics | **Part, 2026-10-12:** platform = Harbor, public benchmark = DevEval (repackaged), messy-specification tasks = our own (D13). Metrics still open | brainstorm D13, Q1, Q4 |
| 3 | Fix the measuring | Not started | brainstorm Q4 |
| 4 | Prepare the tasks | Part: `f1-ingest`, `lend-messy` exist | `harness/tasks/` |
| 5 | Render three formats | Part: tiered and graph for `f1-ingest` only | `~/sddc-runs/pilot-graph-R000023-specs`, `~/sddc-runs/pilot-export-R000023` |
| 6 | Pilot | Part: F1, Sonnet, two formats, both 26 / 26 | `docs/MIA5150-Project/pilot-F1-results.md` |
| 7 | Decide and freeze | Not started | |
| 8 | Main runs | Not started | |
| 9 | Score and audit | Not started | |
| 10 | Analyse | Not started | |

## Milestone 1 — trial queue

One candidate at a time, in this order. Each trial fills the `TRIAL.md` in its folder: source and
licence, the five questions, the one number, a dated log, and the verdict with its reason. A rejected
candidate keeps its record: the report needs the reasons.

| Order | Candidate | Kind | Folder | In the submitted proposal? | State | Verdict |
|---|---|---|---|---|---|---|
| 1 | ProjectEval | benchmark + own judge | `harness/benchmarks/projecteval/` | Yes (benchmark and platform) | **Tried 2026-10-12** | Recommended: reject as main benchmark (specs too small; judge needed 5 fixes on Linux; canonical answer scores 202 / 284). Owner decides at milestone 2 |
| 2 | Harbor | platform | `harness/platforms/harbor/` | Yes (platform) | **Tried 2026-10-12** (no-model checks and one subscription run done) | Recommended: **fits, adopt**. One Sonnet run on the subscription: 24 / 24, $0.18 est., 3 min 5 s. Our `lend` task ran through it: reference 24 / 24, do-nothing 0 / 24, hidden tests not visible to the agent |
| 3 | Doc2Feat-Bench | benchmark | `harness/benchmarks/doc2feat-bench/` | Yes (benchmark) | **Tried 2026-10-12** (no model) | Recommended: reject as main benchmark. Input is a documentation diff, median 132 words in 1 file; the task edits a large existing codebase. Its evaluator works: reference patch 1 / 1 in 36 s |
| 4 | RealBench | benchmark + own pipeline | `harness/benchmarks/realbench/` | Yes (benchmark and platform) | **Tried 2026-10-12 — could not be downloaded** | Recommended: reject, not obtainable. No code, data or website address in the paper or in two searches |
| 5 | RepoGenesis | benchmark | `harness/benchmarks/repogenesis/` | No — added by the owner (rel02 D8) | **Tried 2026-10-12** (no model) | Recommended: reject. One README per task, median 634.5 words. On the one task run, an empty folder scored Pass@1 = 1.0. Its *API coverage* metric is worth borrowing |
| 6 | Inspect AI | platform | `harness/platforms/inspect-ai/` | No — added (D8) | **Tried 2026-10-12 in part** (installed, code read, nothing run) | Recommended: do not adopt. It re-routes Claude Code's model calls through its own client; no subscription route proven; Harbor already works |
| 7 | ProgramBench | benchmark | `harness/benchmarks/programbench/` | No — added (D8) | **Tried 2026-10-12 in part** (data and one task image inspected; evaluator not run) | Recommended: reject. The real specification is a runnable binary; the text is a README and a manual page; 4.19 GB per task image |
| 8 (moved up by the owner, tried 4th) | DevEval, first published as DevBench (2024) | benchmark, a Harbor dataset | `harness/benchmarks/devbench-2024/` | No — added (D8) | **Tried 2026-10-12** (no model) | Recommended: **keep as leading public candidate, with our own repackaging**. Input is 4 spec documents per project, median 1 274 words; 21 projects. The Harbor packaging leaks (reference, tests and most source visible to the agent) and fails without `--ve TEST_DIR=/tests` **Pilot on one repackaged project (Sonnet, n = 1 per format): Markdown 12 / 12, export 12 / 12 — no separation; export cost 1.6 times more** |
| 9 | SWE-Dev (arXiv:2505.16975) | benchmark + own scripts | `harness/benchmarks/swe-dev/` | No — added by the owner (rel02 D12) | **Tried 2026-10-12** (no model) | Recommended: reject as main benchmark. Fills in removed functions inside an existing package, from one document of docstrings written with GPT-4o (median 875 / 1 109.5 words). Its test step works: reference 9 / 9, untouched 0 / 9; one of three images tried made it fail silently. Not well known: 12 citations, 62 stars |

Why this order: ProjectEval first, because its README suggests its judge can run on an existing output
folder (not confirmed) and its three input levels are closest to our format variable. Harbor second,
because it answers the platform question for every benchmark. RealBench last, because no repository
link or licence was found in its paper text, so it may not be downloadable.

### Candidates not in the proposal — all four added to the queue (rel02 D8)

Found by re-reading the proposal and `docs/MIA5150-Project/metrics-and-platforms-survey.md` on
2026-10-12. Order 5–8 above is the assistant's suggestion: the one with a coverage metric first, the
unverified one last.

| Candidate | Kind | Why it could fit | Why it may not | Known from |
|---|---|---|---|---|
| RepoGenesis (arXiv:2601.13943) | benchmark | README → whole repository, built from scratch like our tasks; reports **API coverage**, the nearest thing to our omission metric; already cited in the proposal's Table 3 | Web microservices only | Abstract page only |
| ProgramBench (arXiv:2605.03546) | benchmark | A program's documentation → rebuild the program from scratch; 200 tasks | Scores behaviour against a reference executable, not requirements | Abstract page only |
| Inspect AI (UK AISI) | platform | Custom datasets with files per sample, several scorers per task, confidence intervals built in; the survey called it the best fit for a controlled comparison | Its Claude Code support goes through a separate package; sandbox behaviour not confirmed | Docs pages |
| DevBench (2024, not the 2026 paper) | benchmark | A search snippet said it uses PRDs and UML as input | **Never opened**: the snippet is unverified and may be wrong | Snippet only |

Looked at and not proposed, with the reason (survey §2, §6): HumanEval, MBPP, EvalPlus, BigCodeBench,
ClassEval, LiveCodeBench (function, class or contest level: no specification to render three ways);
SWE-bench Verified and SWE-bench Pro (an issue text, not a specification; fixed task sets); FEA-Bench
and FeatureBench (feature descriptions in prose, added to existing repositories); SpecBench (reviews
specifications, does not implement them); DevBench 2026 (not spec-driven); OpenHands Benchmarks,
lm-evaluation-harness, DeepEval, promptfoo (not runners for a repository-building agent, or no way to
add a benchmark documented). These judgements rest on abstracts and READMEs, not on trials.

## Blockers for the owner

| # | Blocker | Affects | What unblocks it |
|---|---|---|---|
| ~~B1~~ | **Resolved 2026-10-12:** the owner installed Docker Engine 29.9.0. ~~No container runtime~~ | Harbor cannot run at all; ProjectEval's supported Linux route is Docker; later candidates that run repositories or deploy services probably need it too (*not yet checked per candidate*) | Owner installs Docker (administrator rights), or decides the study uses no container and every candidate that needs one is rejected for that reason |

| ~~B2~~ | **Resolved 2026-10-12:** the owner made the token and the run succeeded. ~~Harbor's last check needs a model call and a token~~ | Whether Harbor can be adopted | Owner runs `claude setup-token` and approves one run of `lend` (Markdown) through Harbor; steps in `harness/platforms/harbor/TRIAL.md` §6.4 |

## Log

| Date | What | Result |
|---|---|---|
| 2026-10-11 | rel02 opened; harness and tasks moved to `harness/` | 754 tests pass; `run_task.py --dry-run` on `lend-messy`: every sandbox probe `ok` |
| 2026-10-12 | Milestones accepted (D6); trial folders and `TRIAL.md` templates made; `download/` folders ignored by git | Four candidates queued; four more listed for the owner |
| 2026-10-12 | Owner added the four extras (D8); folders made | Eight candidates queued |
| 2026-10-12 | **Trial 1, ProjectEval** — cloned (commit `34f838c`, GPL-3.0, 116 MB), data counted, judge read and run without a model | 20 projects, 264 tests, specs of median 14 words (prompt) or 179.5 words (checklist). Judge failed on Linux until 5 defects were worked around; then its own canonical answer scored **202 / 284 (0.711)** in 2 min 22 s. Record: `harness/benchmarks/projecteval/TRIAL.md` |
| 2026-10-12 | ProjectEval record extended with a revisit guide (§6): files, rebuild and run commands, how the judge works, how to score a Claude Code project, open questions | `spec_stats.py`, `judge-venv.freeze.txt` added |
| 2026-10-12 | **Trial 2, Harbor** — installed 0.24.0 from PyPI (Apache-2.0), read its Claude Code agent, result models, environment types and telemetry; scaffolded a task; ran the no-model `oracle` agent | Run stopped: "Docker is not installed or not on PATH". No number. Findings from the code: subscription supported through `CLAUDE_CODE_OAUTH_TOKEN` + `CLAUDE_FORCE_OAUTH=1`; time, cost, tokens recorded; no host mode among 31 environment types; telemetry on by default (one event may have been sent before it was switched off). Record: `harness/platforms/harbor/TRIAL.md` |
| 2026-10-12 | Owner installed Docker Engine 29.9.0 and rebooted (answers Q8) | `docker run --rm hello-world` works without `sudo` |
| 2026-10-12 | **Trial 2, Harbor, second session** — scaffold task with the `oracle` agent; `lend-messy` packaged as a Harbor task by `build_lend_task.py`; run with `oracle` (twice) and `nop` | Scaffold: reward 1.0. `lend`: **24 / 24** with the reference in 31 s, **0 / 24** with the do-nothing agent; four named rewards reported; `/tests` absent during the agent phase; phase timings recorded; cost and token fields empty for a no-model agent |
| 2026-10-12 | **Trial 2, Harbor, third session — first model call of rel02.** Owner made a subscription token and approved one run: `lend` Markdown, Claude Code 2.1.296, `claude-sonnet-5-5`, $10 ceiling | **24 / 24**, no exception, 3 min 5 s (95 s of it installing Claude Code). Cost $0.1813725 est. API-equivalent (`total_cost_usd`), 6 turns. `apiKeySource: "none"`, no API key. Token not found in the job files. Harbor's "input tokens" include cache tokens; its per-model cost figure differs from Claude Code's. Tool list was not restricted. n = 1, not a study result. Record: `harness/platforms/harbor/TRIAL.md` §3 |
| 2026-10-12 | **Harbor: does it bring a benchmark?** `harbor datasets list --legacy` | 80 entries, 75 names; none of our six candidates by name. One near match, `deveval` (63 tasks, 21 repositories, PRD + UML + architecture inputs; "originally named DevBench" per its adapter page). Harbor alone cannot run the study; Harbor + our tasks can. Record: `harness/platforms/harbor/TRIAL.md` §2a, `registry-datasets.txt` |
| 2026-10-12 | **Trial 3, Doc2Feat-Bench** — cloned the repository (MIT), downloaded both datasets, measured the input, ran its evaluator on one reference patch | Input: documentation diff, median 132 words / 30 lines / 1 file (Verified, 114 tasks). Evaluator: Success 1 / 1 in 36 s, first attempt, no model. Recommended: reject as main benchmark (nothing to compile; task is editing a large codebase). Record: `harness/benchmarks/doc2feat-bench/TRIAL.md` |
| 2026-10-12 | **Trial 8 moved up by the owner: DevEval (DevBench 2024)** — downloaded as Harbor dataset `deveval@1.0` (63 tasks, 21 projects), measured the specifications, ran one task with `oracle` and `nop`, inspected the task image | Specification: PRD + 2 UML diagrams + architecture design, median 1 274 words (`lend`: 2 120). As downloaded the task fails (`TEST_DIR` unset); with `--ve TEST_DIR=/tests`: reference 1.0, do-nothing 0.0. **Leak:** the image holds the full reference, the tests and the rest of the source, and the agent is `root`. Recommended: keep as leading public candidate, repackaged by us. Record: `harness/benchmarks/devbench-2024/TRIAL.md` |
| 2026-10-12 | **Trials 4–7, no model** — RealBench (paper read in full, two searches), RepoGenesis (cloned, READMEs measured, evaluator run on a hand-written and an empty `flask` submission), ProgramBench (cloned, 201 task definitions counted, one task image inspected), Inspect AI (installed, agent and provider code read) | RealBench: nothing to download. RepoGenesis: README median 634.5 words; empty folder passes 7 / 7 tests on `flask`. ProgramBench: input is README + manual page + runnable binary; median 974 tests per task; 4.19 GB image. Inspect AI: Claude Code runs behind a model bridge, not on its own login. All four: recommended reject / do not adopt. Records: each folder's `TRIAL.md` |
| 2026-10-12 | **DevEval pilot (owner approved; model calls)** — `python-hone` repackaged clean; its four documents compiled on Haiku; one Sonnet run per format through Harbor | Clean task: reference 12 / 12, do-nothing 0 / 12. Compile: 61 nodes, 3 duplications, 0 contradictions, 56 calls, $0.2685 est., 18 min. Runs: **Markdown 12 / 12** (4 turns, $0.1171 est.), **export 12 / 12** (11 turns, $0.1874 est.). Ceiling effect: the formats do not separate on tests passed. Total model cost of the pilot ≈ $0.57 est. API-equivalent (sum of the three figures). Record: `harness/benchmarks/devbench-2024/TRIAL.md` §7 |
| 2026-10-12 | **Milestone 1 finished: all 8 candidates have a record.** | Summary and recommendation for milestone 2: brainstorm, session S3 |
| 2026-10-12 | **Platform comparison written** — which platforms were tried and how far, findings, comparison table, recommendation, plan | 5 platforms have a record (Harbor and `harness/` ran models; ProjectEval judge ran without one; Inspect AI read only; RealBench not obtainable); 6 survey tools never tried. Recommendation unchanged: adopt Harbor, keep `harness/` as cross-check. Record: `sdd/design/rel-02/rel02_platform_comparison.md` |
| 2026-10-12 | **Trial 9, SWE-Dev (owner added, D12)** — paper read on arXiv (the owner's OpenReview link is behind a browser challenge), repository and test split downloaded, input measured, its test step run on two samples; popularity indicators read for all candidates | Input: one PRD of per-function docstrings, median 875 words (easy) / 1 109.5 (hard), plus the package's source with those functions removed. Reference 9 / 9, untouched 0 / 9 on `idna`; on `advertools` the evaluator reported 0 for everything (plugin missing in the image). Record: `harness/benchmarks/swe-dev/TRIAL.md`; popularity table and method: `rel02_platform_comparison.md` §6 |
| 2026-10-12 | **Owner's decisions D13 and D14** | D13: Harbor is the platform, DevEval the public benchmark, the messy-specification tasks are our own because no public benchmark has them. D14: rel02 works in quick iterations (decide, small trial, refine); the milestone list is a map, not a fixed sequence |
