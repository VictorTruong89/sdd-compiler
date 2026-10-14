# rel02 — methodology notes for the report

> Opened 2026-10-12. A running record of **how the study is done**, kept so the report's method
> section can be written from it without reconstructing anything. Non-authoritative design note.
> Rules: every figure is measured and names its source, or is marked *to be measured*; every `$` is
> Claude Code's `total_cost_usd`, an estimated API-equivalent on the subscription, never spend; a
> setting that changed is kept with its date, not overwritten.
> Decisions referred to as D*n* are in [`rel02_brainstorm.md`](rel02_brainstorm.md); progress is in
> [`rel02_build_progress.md`](rel02_build_progress.md).

## 1. Question and design

- **Question.** Does an AI coding agent build better code from a compiled specification graph than
  from the same specification as plain Markdown files?
- **Independent variable.** The format the specification is handed over in. Built so far: flat
  Markdown files, and the graph export (`MAP.md`, `CHECKLIST.md`, `packs/`). The tiered format named
  in the proposal is not built.
- **Held fixed in a comparison.** Task text, hidden tests, agent and its version, model, tools,
  network, cost ceiling, compiler commit.
- **Way of working.** Quick iterations: decide, run a small trial, refine (D14). One run per
  condition is an observation; repetitions come only when the design is frozen (working map, stage E).
- **Working pass line for "the graph is ready for code generation"** (D15, initial): on the messy
  task, the agent given the export meets at least as many requirements as the one given the Markdown,
  with no more inventions, and no further export defect is found.

## 2. Choice of platform and benchmark

- **Method of choice.** Nine candidates were each tried on this machine and recorded, fit or unfit
  (D7): six benchmarks named in or added to the proposal, two platforms, and SWE-Dev. Each record is
  a `TRIAL.md` under `harness/benchmarks/` or `harness/platforms/` with source, licence, five fixed
  questions, one measured number, a dated log and a verdict.
- **Decision (D13).** Platform: Harbor. Public benchmark: DevEval. Messy-specification tasks: our own.
- **Statement for the report.** No public benchmark tried has scattered, duplicated or contradictory
  specifications, so the tasks that test the product's claim are our own.
- **Rejected, with the reason:** ProjectEval (inputs of median 14 or 179.5 words); Doc2Feat-Bench and
  SWE-Dev (the task edits an existing codebase); RealBench (not obtainable); RepoGenesis (an empty
  folder scored 1.0 on the task tried); ProgramBench (the real specification is a binary); Inspect AI
  (routes Claude Code's model calls through its own client). Comparison and popularity indicators:
  [`rel02_platform_comparison.md`](rel02_platform_comparison.md).

## 3. Materials

| Task | Kind | Specification | Tests | Reference check | Where |
|---|---|---|---|---|---|
| `lend` | Ours, messy by design | 7 Markdown files, 2 120 words, 85 blocks; 12 planted problems (5 contradictions, 1 superseded rule, 2 duplicates, 1 scattered refinement, 1 buried rule, 1 modality difference, 1 vague statement) with an answer key | 24 black-box tests through the command, mapped to requirements R1–R24; they never depend on how a contradiction is resolved | Reference 24 / 24, do-nothing 0 / 24 | `harness/tasks/lend-messy/` |
| `python-hone` | DevEval, clean, repackaged | 4 documents (PRD, 2 UML, architecture), 1 697 words | 12 tests from the benchmark | Reference 12 / 12, do-nothing 0 / 12 | `harness/benchmarks/devbench-2024/` |
| `f1-ingest` | Ours, clean (rel01 pilot) | 9 spec files of this repository | 26 tests | 26 / 26, 0 / 26 | `harness/tasks/f1-ingest/` |

- **Why DevEval is repackaged.** As distributed for Harbor, the agent's container holds the reference
  implementation, the tests and most of the source. Our build gives the agent only the specification
  and the data files (`build_clean_task.py`). Scores are therefore not comparable with published ones.
- **Contradictions in `lend` are left unsettled for both formats** (owner, 2026-10-01): the export is
  made with `--allow-open`, so it shows each detected contradiction as unsettled with both quotes;
  the Markdown agent has to find them itself.

## 4. Producing the graph format

- **Tool.** `sddc` 0.1.0.dev0, this repository. `sddc init`, `sddc compile`, then
  `sddc export --allow-open`. Atomizing and pair judging are model calls made through Claude Code
  headless on the subscription; `ANTHROPIC_API_KEY` is never set.
- **Compile model.** Haiku (profile `atomizer.model: haiku`), Claude Code 2.1.296.
- **Profile.** Defaults, except where the table says otherwise. The profile is the only hand-edited
  file in the store and is kept with each run.

| Compile | Compiler commit | Profile changes | Calls | Cost (est.) | Time | Result | Store |
|---|---|---|---|---|---|---|---|
| `python-hone`, 2026-10-12 | *not recorded at the time* (rel01 close commit `6a17a80` was `HEAD`) | `contract_languages` + `mermaid`, `bash` | 56 | $0.2685 | 18 min 1 s | 121 blocks → 61 nodes, 26 families; 3 duplications, 0 contradictions; export 9 388 words | `~/sddc-runs/deveval-hone/` |
| `lend`, 2026-10-12 | `03b44e6` | `max_calls_per_run` 200 → 300 (owner); not reached | 98 | $0.5031 | 37 min 34 s | 85 blocks → 124 nodes, 32 families; 26 blocks formed no node; 477 pairs judged; 12 conflicts opened (4 contradictions, 7 duplications, 1 subsumption); export 25 packs, 13 516 words (6.4 times the Markdown's 2 120), 4 contradictions shown unsettled | `~/sddc-runs/lend/`, export `~/sddc-runs/lend-export/` with manifest `lend-export.sha256` |

**Compiler recall on the `lend` answer key** (a by-product; `sddc conflicts`, read against
`ANSWER_KEY.md` by the assistant, not audited by a second person). Of the 9 planted items the compiler
could report as conflicts, it reported **5**: P2 (overdue boundary), P3 (email in the report), P6 and
P7 (duplicates), P11 (MUST against SHOULD). It **missed 4**: P1 (fee cap $10 against $15), P4 (the
"patron" alias), P5 (limit 5 superseded by 3), P10 (worked example against its rule). Both statements
of each missed item are in the export, in different packs, with nothing linking them. Of the 12
conflicts opened, 9 belong to planted items, 2 are duplications outside the key that read as real
(power tools 7 days; the three categories), and 1 reads as false (CF-000004: an email in each row
against the header row).

**DevEval compiles (round 7, 2026-10-13).** One store per project under `~/sddc-runs/deveval-<project>/`,
holding the project's four documents as `sdd/specs/*.md` (byte-identical to the Markdown task's
`spec/`). One profile for every DevEval project, the one of the hone pilot: `contract_languages`
= `json, yaml, text, mermaid, bash`, so each UML diagram and shell block stays one node; backend
`claude-code`, model `haiku`, no thinking, call cap 300. Fences with no language or with
`plaintext` (one in `lice`) are stored but form no node. Command: `sddc compile --json`, rerun if
the cap stops it. Export: `sddc export --allow-open --out export`. Compiler commit `03b44e6`.
Results per project: §8 and `harness/benchmarks/devbench-2024/TRIAL.md` §9.

## 5. Running the agent

| Setting | Value | Since | Note |
|---|---|---|---|
| Platform | Harbor 0.24.0 (PyPI, Apache-2.0), Docker Engine 29.9.0 | 2026-10-12 | Telemetry off (`HARBOR_TELEMETRY=0`) |
| Machine | Ubuntu 24.04.5, Linux 7.0.0-38, 20 CPU threads, 31 GB RAM | | One trial at a time |
| Agent | Claude Code, headless, started by Harbor's `claude-code` agent | | Permission mode `bypassPermissions` inside the container |
| Agent version | 2.1.296, installed in the task image and requested with `--ak version=2.1.296` | round 1 | Before round 1 Harbor installed the current release at each run (it was 2.1.296) |
| Credential | Subscription token in `CLAUDE_CODE_OAUTH_TOKEN`, `CLAUDE_FORCE_OAUTH=1`, no API key | | Start event reports `apiKeySource: "none"`. The token is never written into the repository |
| Agent model | `claude-sonnet-5-5` so far | | Haiku planned for round 3 |
| Tools | `Bash`, `Edit`, `Read`, `Write` only: 19 others disallowed | round 1 | First `lend` run: all 22 default tools. `hone` pilot runs: web tools removed only |
| Network, agent phase | Allow-list: `api.anthropic.com`, `pypi.org`, `files.pythonhosted.org` | round 1 | Public before round 1 |
| Cost ceiling | `--max-budget-usd 10` per run | | Not yet shown to stop a run |
| Container | `python:3.12-slim`; working directory `/app` holding only `spec/` (and data files for `hone`) | | Tests and scorer are uploaded only after the agent stops |
| Task text | Same for every format except one line saying where the specification starts | | `harness/tasks/lend-messy/task.md` |

Each format is its own Harbor task, generated by script from the same task folder, so nothing but
the specification folder and that one line differs.

## 6. Measures

| Measure | Definition | Computed by | Status |
|---|---|---|---|
| Tests passed | Hidden tests passed / total | `test.sh`, pytest | In use |
| Requirements met, omissions | A requirement is met when every hidden test named for it passes; omissions = 24 − met | `lend_score.py` | `lend` only, since round 1 |
| Contradiction side | For each of 5 planted contradictions, a probe through the command: statement A, statement B, or neither | `lend_score.py` | `lend` only. Recorded, never judged |
| Inventions, automatic part | Contradictions answered "neither" + commands beyond the eight specified | `lend_score.py` | Partial by design |
| Inventions and audit items A1–A6 | Human reading of the agent's code and notes, scale 0 / 1 / 2 per item, blind to format where possible | Owner | Not yet done on any run |
| Audit triage | Keyword match of A1–A6 in the agent's notes | `lend_score.py` | A triage. First compared with a reading of real notes in round 2: one false positive found and fixed (a bare "15" counted as the fee-cap item); A6 ("fast") still matches a mention that is not a listed open question |
| Cost | Claude Code's `total_cost_usd` (Harbor field `cost_usd`) | Harbor result file | Harbor's per-model cost figure differs and is not used |
| Tokens | Claude Code's input, cache-write, cache-read and output counts | Harbor result file | Harbor's "input" is the sum of the first three |
| Time, turns | Agent execution time and number of turns | Harbor result file | Setup and verifier time reported separately |

**Checks on the measuring itself.** Before any model run on a task, the reference agent must score
full marks and the do-nothing agent zero. `lend_score.py` is checked against three variants of the
reference whose behaviour is known (`check_scoring.py`).

## 7. Threats to validity noted so far

- **Ceiling.** Sonnet scored full marks on all three pilot runs; tests passed cannot separate formats
  on these tasks with this model.
- **n = 1** per condition in every run so far.
- **Conditions changed between rounds** (tools, network, pinned version). Runs before and after
  round 1 are not compared with each other.
- **Prior knowledge.** `python-hone` is a public package; the Markdown run finished in 4 turns.
- **The task author also wrote the scorer and the answer key**; the key was not audited by a second
  person.
- **The export adds instructions** (for example, to account for every checklist id), so a difference
  may come from the instructions as well as from the structure.
- **The compiler is the thing under test.** Runs compared together must use one compiler commit.
- **Compile cost is part of the graph format's cost** and is reported beside the run cost.

- **Round 2 added:** the triage keyword defect above; and both round 2 runs resolved all five
  contradictions the same way, so "which side" did not vary with format in this pair.
- **The audit so far is the assistant's reading, not the owner's blind audit.**
- **Round 3 added — the task cannot show the graph's main contribution.** Hidden tests avoid every
  contradicted value and the contradictions are unsettled in both formats, so flagged conflicts
  cannot move any scored number. Both models reached full marks in both formats.
- **Round 3 added — planted item P1 is not a real contradiction** (a $10 cap satisfies "no more than
  $15"). Compiler recall on the key is 5 of 9 as written, 5 of 8 with P1 set aside.
- **Scorer defects found on real runs and fixed:** the fee-cap keyword (round 2); the help-text
  parser (round 3). Stored score files keep the pre-fix values.
- **Round 4 added — the verdict comparison is not format against format.** The settled export
  carries two decisions of the owner; the Markdown input carries none. "2 of 2" against "0 of 2"
  therefore measures the workflow (compile, a person settles, the agent builds), not the graph as a
  format. A control (Markdown plus the same decisions in a plain file) has not been run.
- **Round 4 — the verdicts were chosen opposite to the unaided choice,** so that following them is
  visible. This is a design choice of the test, to be stated with the result.
- **Round 4 — the Markdown and unsettled-export rows are earlier builds rescored offline** with the
  new measure, not fresh runs.
- **Round 5 — the control was run.** Markdown plus the same two decisions in a plain file also
  follows 2 of 2, on both models. So the round 4 difference is explained by the decisions, not by
  the graph format. The decisions file was written by us in the adjudication's words; it is 92
  words in a 2 212-word spec, where it is hard to miss. A large spec may behave differently
  (*to be measured*).
- **Round 6 — DevEval subset.** Only the Python projects are repackaged (9 of 21), and one of
  those is left out because its reference fails under current NumPy: 8 projects, 123 tests. All
  eight specifications are smaller than `lend`. The repackaging (what is seed, what is hidden, how
  dependencies are installed, tests in two processes) is ours and is a change from the benchmark as
  published; `harness/benchmarks/devbench-2024/TRIAL.md` §8.
- **Round 7 — tests-passed is brittle on DevEval.** A test file that imports one missing name fails
  as a whole (`lice`: 25 of 31 tests lost to one name, in both formats). A count of tests passed
  therefore mixes "one omission" with "many". A finer measure (which specified names exist) is
  *to be designed*.
- **Round 7 — runs can be lost to the machine.** Two runs were stopped by the system for low memory.
  Runs were two at a time, after three parallel compiles. Interrupted runs are reported as not
  finished, never replaced silently.
- **Round 7 — `arxiv-digest` needs the live arXiv service** in the verifier, and the agent phase
  cannot reach it. Results on it can change with the service's content on the day.
- **Round 8 — the DevEval scorer counted tests the agent wrote.** On `stocktrends` both agents
  wrote tests into the folder the hidden tests are copied to, and the first reward files said 8 / 9
  and 7 / 9 where the hidden tests give 3 / 9 and 3 / 9. Found because the number of tests collected
  (14, 13) exceeded the number of hidden tests (9). Fixed in the task builder; both builds rescored
  from their saved workspace. Rule from now on: a reward is accepted only when tests collected is at
  most the number of hidden tests. Round 7 and the `hone` pilot pass that check.
- **Round 8 — some DevEval hidden tests ask for what the specification does not state** (a default
  argument, a constant's name on `stocktrends`). Such tests measure agreement with the reference,
  not with the specification, and put a ceiling below 100 % on any input format. How many tests per
  project are of this kind is *to be measured*.
- **Round 8 — the verifier depends on PyPI at scoring time;** one check hung there for 10 minutes.
- **Round 9 — most DevEval hidden tests cannot be passed from the specification.** By reading, 33
  of the 82 tests of three projects are stated in the specification; 33 need a name, default, key or
  exact string it does not give, 1 contradicts it, 15 are open to a fair reading. No run passed any
  of the 34. A raw tests-passed score on DevEval therefore mostly measures distance to the
  reference. From now on DevEval results are reported by class, with the stated tests as the main
  figure.
- **Round 9 — the classification is one reader's judgement,** made by the assistant that also
  built the task, before the runs were split but after seeing the round 7 and 8 totals. Not checked
  by a second reader. The boundary between S and U moved the result on two tests.
- **Round 9 — run-to-run variation is as large as the first difference seen.** The same Markdown
  task gave 22, 27 and 28 of 42. A single pair of runs cannot support a format claim; n = 3 is the
  least used from now on where a difference is to be reported.

## 8. Register of model runs

Every run that called a model, in order. Result files are in the folder named.

| # | Date | What | Model | Conditions | Result | Cost (est.) | Source |
|---|---|---|---|---|---|---|---|
| 1 | 2026-09-30 | `f1-ingest`, Markdown, own harness | Sonnet | 4 tools, bubblewrap | 26 / 26, 12 turns, 182 s | $0.52 | `docs/MIA5150-Project/pilot-F1-results.md` |
| 2 | 2026-09-30 | `f1-ingest`, export, own harness | Sonnet | same | 26 / 26, 15 turns, 186 s | $0.70 | same |
| 3 | 2026-10-12 | `lend`, Markdown, Harbor | Sonnet | 22 tools, public network | 24 / 24, 6 turns, 65.8 s | $0.1814 | `harness/platforms/harbor/lend-claude-sonnet-markdown.result.json` |
| 4 | 2026-10-12 | Compile `python-hone` | Haiku | — | 61 nodes, 56 calls, 18 min 1 s | $0.2685 | `~/sddc-runs/deveval-hone/` |
| 5 | 2026-10-12 | `hone`, Markdown, Harbor | Sonnet | web tools removed, public network | 12 / 12, 4 turns, 32.5 s | $0.1171 | `harness/benchmarks/devbench-2024/pilot-hone-markdown-sonnet-1.result.json` |
| 6 | 2026-10-12 | `hone`, export, Harbor | Sonnet | same | 12 / 12, 11 turns, 56.4 s | $0.1874 | `…/pilot-hone-export-sonnet-1.result.json` |
| 7 | 2026-10-12 | Compile `lend` | Haiku | cap 300 calls, not reached | 124 nodes, 12 conflicts, 98 calls, 37 min 34 s | $0.5031 | `harness/platforms/harbor/round2/lend-compile-1.json` |
| 8 | 2026-10-13 | `lend`, Markdown, Harbor | Sonnet | round 1 conditions: 4 tools, allow-list, 2.1.296 | 24 / 24, 0 omissions, 5 turns, 56.6 s; sides A A A A except P2 = B; 0 extra commands | $0.1451 | `…/round2/lend-markdown-sonnet-1.*` |
| 9 | 2026-10-13 | `lend`, export, Harbor | Sonnet | same | 24 / 24, 0 omissions, 6 turns, 71.9 s; same sides; 0 extra commands | $0.2351 | `…/round2/lend-export-sonnet-1.*` |

Tokens for runs 8 and 9 (Harbor fields; "input" includes cache): Markdown 56 374 input of which
41 571 cache read, 8 172 output; export 139 791 input of which 107 246 cache read, 9 419 output.
| 10 | 2026-10-13 | `lend`, Markdown, Harbor | Haiku (`claude-haiku-5-5`) | as runs 8–9 | 24 / 24, 0 omissions, 35 turns, 246.4 s; sides A B A A A | $0.0539 | `harness/platforms/harbor/round3/lend-markdown-haiku-1.*` |
| 11 | 2026-10-13 | `lend`, export, Harbor | Haiku | same | 24 / 24, 0 omissions, 43 turns, 296.4 s; same sides | $0.1118 | `…/round3/lend-export-haiku-1.*` |
| 12 | 2026-10-13 | `lend`, export with 2 owner verdicts, Harbor | Sonnet (`claude-sonnet-5-5`) | as runs 8–9 | 24 / 24, 0 omissions, 7 turns, 69.7 s; sides A A B A A; settled followed 2 of 2 | $0.2515 | `harness/platforms/harbor/round4/lend-export-settled-sonnet-1.*` |
| 13 | 2026-10-13 | same | Haiku (`claude-haiku-5-5`) | same | 24 / 24, 0 omissions, 53 turns, 304.1 s; same sides; settled followed 2 of 2 | $0.1227 | `…/round4/lend-export-settled-haiku-1.*` |
| 14 | 2026-10-13 | `lend`, Markdown + `DECISIONS.md`, Harbor | Sonnet (`claude-sonnet-5-5`) | as runs 8–9 | 24 / 24, 0 omissions, 5 turns, 69.1 s; sides A A B A A; settled followed 2 of 2 | $0.1461 | `harness/platforms/harbor/round5/lend-markdown-decisions-sonnet-1.*` |
| 15 | 2026-10-13 | same | Haiku (`claude-haiku-5-5`) | same | 24 / 24, 0 omissions, 35 turns, 185.2 s; same sides; settled followed 2 of 2 | $0.0381 | `…/round5/lend-markdown-decisions-haiku-1.*` |
| 16 | 2026-10-13 | Compile `python-lice` | Haiku | — | 58 nodes, 2 conflicts (0 contradictions), 43 calls, 15 min 43 s | $0.2158 | `harness/benchmarks/devbench-2024/round7/lice-compile-1.json` |
| 17 | 2026-10-13 | Compile `python-arxiv-digest` | Haiku | — | 55 nodes, 8 conflicts (2 contradictions), 46 calls, 16 min 31 s | $0.2286 | `…/round7/arxiv-digest-compile-1.json` |
| 18 | 2026-10-13 | Compile `python-stocktrends` | Haiku | — | 66 nodes, 10 conflicts (0 contradictions), 55 calls, 17 min 44 s | $0.2623 | `…/round7/stocktrends-compile-1.json` |
| 19 | 2026-10-13 | DevEval `lice`, Markdown, Harbor | Haiku (`claude-haiku-5-5`) | as runs 8–9 | 3 / 31, 10 turns, 100.4 s | $0.0197 | `harness/benchmarks/devbench-2024/round7/lice-markdown-haiku-1.*` |
| 20 | 2026-10-13 | DevEval `lice`, export | Haiku | same | 3 / 31, 45 turns, 178.7 s | $0.0425 | `…/round7/lice-export-haiku-1.*` |
| 21 | 2026-10-13 | DevEval `arxiv-digest`, Markdown | Haiku | same | 22 / 42, 6 turns, 39.3 s | $0.0079 | `…/round7/arxiv-digest-markdown-haiku-1.*` |
| 22 | 2026-10-13 | DevEval `arxiv-digest`, export | Haiku | same | 30 / 42, 19 turns, 127.7 s | $0.0312 | `…/round7/arxiv-digest-export-haiku-1.*` |
| — | 2026-10-13 | DevEval `stocktrends`, both formats (rerun as 23 and 24) | Haiku | same | **not finished**: stopped by the system for low memory during the agent phase; any model calls made before the stop are not recorded | not recorded | — |
| 23 | 2026-10-13 | DevEval `stocktrends`, Markdown (round 8) | Haiku | same, one run at a time | 3 / 9 after rescoring (first reported 8 / 9: scorer fault), 22 turns, 250.7 s | $0.0522 | `harness/benchmarks/devbench-2024/round8/stocktrends-markdown-haiku-1.*` |
| 24 | 2026-10-13 | DevEval `stocktrends`, export (round 8) | Haiku | same | 3 / 9 after rescoring (first reported 7 / 9), 27 turns, 370.9 s | $0.1150 | `…/round8/stocktrends-export-haiku-1.*` |
| 25 | 2026-10-13 | DevEval `arxiv-digest`, Markdown, run 2 (round 9) | Haiku | same, one run at a time | 27 / 42 (S 25 / 28), 8 turns, 104.1 s | $0.0111 | `harness/benchmarks/devbench-2024/round9/arxiv-digest-markdown-haiku-2.*` |
| 26 | 2026-10-13 | same, export, run 2 | Haiku | same | 30 / 42 (S 27 / 28), 13 turns, 100.3 s | $0.0237 | `…/round9/arxiv-digest-export-haiku-2.*` |
| 27 | 2026-10-13 | same, Markdown, run 3 | Haiku | same | 28 / 42 (S 25 / 28), 7 turns, 50.6 s | $0.0100 | `…/round9/arxiv-digest-markdown-haiku-3.*` |
| 28 | 2026-10-13 | same, export, run 3 | Haiku | same | 29 / 42 (S 27 / 28), 14 turns, 102.1 s | $0.0237 | `…/round9/arxiv-digest-export-haiku-3.*` |

Tokens for runs 10 and 11: Markdown 897 440 input incl. cache (821 287 cache read), 60 939 output of
which 35 866 thinking; export 1 627 993 (1 525 588 cache read), 71 744 output of which 42 069 thinking.

Tokens for runs 12 and 13 (Harbor `result.json`): Sonnet 178 132 input incl. cache (142 010 cache
read), 9 288 output; Haiku 1 916 433 (1 805 050 cache read), 72 327 output.

**Settling the contradictions (round 4, no model call).** Store copied to `~/sddc-runs/lend-r4/`;
four `sddc conflicts judge` commands with `--verdict real` and the owner's decision as `--note`;
`sddc export` without `--allow-open` to `~/sddc-runs/lend-r4-export/` (25 packs, 13 731 words, 0
unsettled). Verdicts: `harness/tasks/lend-messy/ANSWER_KEY.md`; records:
`harness/platforms/harbor/round4/lend-adjudications.jsonl`. Measure `settled_followed`:
`lend_score.py --settled P2=A,P3=B`.

Tokens for runs 14 and 15 (Harbor `result.json`): Sonnet 57 675 input incl. cache (43 554 cache
read), 8 529 output; Haiku 643 055 (590 697 cache read), 43 419 output.

Tokens for runs 23 and 24 (Harbor `result.json`): Markdown 1 007 042 input incl. cache (930 164 cache
read), 55 036 output; export 1 496 784 (1 394 040 cache read), 80 494 output.

**Rescoring a DevEval build offline (round 8, no model call).** `docker build` on the task's
`environment/`; extract `app.tgz` to a folder mounted at `/app`; mount the task's `tests/` at `/tests`
and an empty folder at `/logs/verifier`; run `bash /tests/test.sh`.

Tokens for runs 25 to 28 (Harbor `result.json`; input incl. cache, cache read, output): 91 304,
73 345, 13 468 · 354 983, 311 114, 23 669 · 107 250, 91 038, 11 632 · 399 111, 355 664, 22 987.

**Classifying hidden tests (round 9, no model call).** Each test read against the four documents and
the seed files; class S, U, R or C with a one-line reason in
`harness/benchmarks/devbench-2024/test-classification.json`; absent names confirmed with `grep` on
both the Markdown and the export; ids checked against the reference run with
`score_by_class.py --check`; a run is split with `score_by_class.py <project> <verifier folder>`.

**Round 10 (no model call).** Report draft sections R2 and R3 written from this register and the two
TRIAL files. Cost ratios are the recorded export cost over the recorded Markdown cost; for
`arxiv-digest` the mean of three runs per format. No new measurement.
