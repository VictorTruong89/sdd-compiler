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
- **Round 11 — the live arXiv service can cost a build tests at scoring time.** Two acceptance tests
  of one Sonnet build failed with no CSV written; the same code, rerun from the host about ten
  minutes later, wrote it. The scorer keeps no stderr of those script runs, so the cause is
  inferred, not shown. `arxiv-digest` acceptance results are to be read with this in mind.

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
| 29 | 2026-10-14 | DevEval `lice`, Markdown (round 11) | Sonnet (`claude-sonnet-5-5`) | as the Haiku runs, one at a time | 6 / 31 (S 3 / 3, U 3 / 3), 4 turns, 36.8 s | $0.1039 | `harness/benchmarks/devbench-2024/round11/lice-markdown-sonnet-1.*` |
| 30 | 2026-10-14 | DevEval `lice`, export | Sonnet | same | 6 / 31 (S 3 / 3, U 3 / 3), 7 turns, 44.8 s | $0.1347 | `…/round11/lice-export-sonnet-1.*` |
| 31 | 2026-10-14 | DevEval `arxiv-digest`, Markdown | Sonnet | same | 29 / 42 (S 25 / 28), 4 turns, 23.7 s; 2 acceptance tests lost to the live service, most likely | $0.0692 | `…/round11/arxiv-digest-markdown-sonnet-1.*` |
| 32 | 2026-10-14 | DevEval `arxiv-digest`, export | Sonnet | same | 30 / 42 (S 27 / 28), 8 turns, 31.7 s | $0.1288 | `…/round11/arxiv-digest-export-sonnet-1.*` |
| 33 | 2026-10-14 | DevEval `stocktrends`, Markdown | Sonnet | same | 4 / 9 (S 2 / 2, U 2 / 5), 9 turns, 103.1 s | $0.2167 | `…/round11/stocktrends-markdown-sonnet-1.*` |
| 34 | 2026-10-14 | DevEval `stocktrends`, export | Sonnet | same | 3 / 9 (S 2 / 2, U 1 / 5), 10 turns, 107.0 s | $0.2778 | `…/round11/stocktrends-export-sonnet-1.*` |
| 35 | 2026-10-14 | DevEval `chakin`, Markdown | Opus | Harbor, CC 2.1.296, 4 tools, allow-list, round-8 scorer | 2 / 2 (R 2 / 2), 8 turns, 54.2 s | $0.2046 | `harness/benchmarks/devbench-2024/round12-opus/runs/chakin/` |
| 36 | 2026-10-14 | DevEval `particle-swarm-optimization`, Markdown | Opus | Harbor, CC 2.1.296, 4 tools, allow-list, round-8 scorer | 6 / 6 (S 6 / 6), 4 turns, 35.1 s | $0.1199 | `harness/benchmarks/devbench-2024/round12-opus/runs/particle-swarm-optimization/` |
| 37 | 2026-10-14 | DevEval `geotext`, Markdown | Opus | Harbor, CC 2.1.296, 4 tools, allow-list, round-8 scorer | 9 / 9 (S 5 / 5, U 3 / 3, R 1 / 1), 8 turns, 49.9 s | $0.1984 | `harness/benchmarks/devbench-2024/round12-opus/runs/geotext/` |
| 38 | 2026-10-14 | DevEval `stocktrends`, Markdown | Opus | Harbor, CC 2.1.296, 4 tools, allow-list, round-8 scorer | 7 / 9 (S 2 / 2, U 3 / 5, R 2 / 2), 9 turns, 127.6 s | $0.4641 | `harness/benchmarks/devbench-2024/round12-opus/runs/stocktrends/` |
| 39 | 2026-10-14 | DevEval `hybrid-images`, Markdown | Opus | Harbor, CC 2.1.296, 4 tools, allow-list, round-8 scorer | 17 / 20 (S 3 / 3, U 14 / 14, R 0 / 1, C 0 / 2), 8 turns, 424.2 s | $0.1757 | `harness/benchmarks/devbench-2024/round12-opus/runs/hybrid-images/` |
| 40 | 2026-10-14 | DevEval `hone`, Markdown | Opus | Harbor, CC 2.1.296, 4 tools, allow-list, round-8 scorer | 12 / 12 (S 11 / 11, U 1 / 1), 7 turns, 87.8 s | $0.3384 | `harness/benchmarks/devbench-2024/round12-opus/runs/hone/` |
| 41 | 2026-10-14 | DevEval `lice`, Markdown | Opus | Harbor, CC 2.1.296, 4 tools, allow-list, round-8 scorer | 6 / 31 (S 3 / 3, U 3 / 3, R 0 / 25), 7 turns, 105.6 s | $0.3863 | `harness/benchmarks/devbench-2024/round12-opus/runs/lice/` |
| 42 | 2026-10-14 | DevEval `arxiv-digest`, Markdown | Opus | Harbor, CC 2.1.296, 4 tools, allow-list, round-8 scorer | 32 / 42 (S 27 / 28, U 5 / 7, R 0 / 6, C 0 / 1), 7 turns, 69.5 s | $0.2547 | `harness/benchmarks/devbench-2024/round12-opus/runs/arxiv-digest/` |
| 43 | 2026-10-14 | Zero2Repo case004, Markdown | Haiku | Harbor, CC 2.1.296, 4 tools, allow-list, Zero2Repo judge + junit | 258 / 258 (official 1.0 after rescore; 0 at run time from adapter fault 2), 26 turns, 250 s | $0.0507 | `harness/trials/r13-zero2repo-case004/runs/haiku-markdown-1/` |
| 44 | 2026-10-14 | Zero2Repo case004, Markdown | Sonnet | Harbor, CC 2.1.296, 4 tools, allow-list, Zero2Repo judge + junit | 258 / 258, official 1.0, 5 turns, 96 s | $0.2331 | `harness/trials/r13-zero2repo-case004/runs/sonnet-markdown-1/` |
| 45 | 2026-10-14 | Zero2Repo case004, Markdown | Haiku | Harbor, CC 2.1.296, 4 tools, allow-list, Zero2Repo judge + junit | 258 / 258, official 1.0, 24 turns, 249 s | $0.0494 | `harness/trials/r13-zero2repo-case004/runs/haiku-markdown-2/` |
| 46 | 2026-10-14 | Zero2Repo case004, Markdown | Sonnet | Harbor, CC 2.1.296, 4 tools, allow-list, Zero2Repo judge + junit | 258 / 258, official 1.0, 6 turns, 93 s | $0.2136 | `harness/trials/r13-zero2repo-case004/runs/sonnet-markdown-2/` |
| 47 | 2026-10-14 | Zero2Repo case004, export (`--allow-open`, 18 unsettled) | Haiku | Harbor, CC 2.1.296, 4 tools, allow-list, Zero2Repo judge + junit | 258 / 258, official 1.0, 75 turns, 492 s | $0.5144 | `harness/trials/r13-zero2repo-case004/runs/haiku-export-1/` |
| 48 | 2026-10-14 | Zero2Repo case004, export (`--allow-open`, 18 unsettled) | Sonnet | Harbor, CC 2.1.296, 4 tools, allow-list, Zero2Repo judge + junit | 258 / 258, official 1.0, 7 turns, 92 s | $0.2240 | `harness/trials/r13-zero2repo-case004/runs/sonnet-export-1/` |
| 49 | 2026-10-14 | Zero2Repo case004, export (`--allow-open`, 18 unsettled) | Haiku | Harbor, CC 2.1.296, 4 tools, allow-list, Zero2Repo judge + junit | 256 / 258, official 0 (2 misses from false-positive CF-000034/44), 46 turns, 376 s | $0.3863 | `harness/trials/r13-zero2repo-case004/runs/haiku-export-2/` |
| 50 | 2026-10-14 | Zero2Repo case004, export (`--allow-open`, 18 unsettled) | Sonnet | Harbor, CC 2.1.296, 4 tools, allow-list, Zero2Repo judge + junit | 258 / 258, official 1.0, 6 turns, 103 s | $0.2466 | `harness/trials/r13-zero2repo-case004/runs/sonnet-export-2/` |
| 51 | 2026-10-14 | Zero2Repo case004, export settled (18 contradictions judged false, no `--allow-open`) | Haiku | Harbor, CC 2.1.296, 4 tools, allow-list, Zero2Repo judge + junit | 258 / 258, official 1.0, 35 turns, 313 s | $0.1670 | `harness/trials/r13-zero2repo-case004/runs/haiku-settled-1/` |
| 52 | 2026-10-14 | Zero2Repo case004, export settled (18 contradictions judged false, no `--allow-open`) | Haiku | Harbor, CC 2.1.296, 4 tools, allow-list, Zero2Repo judge + junit | 258 / 258, official 1.0, 20 turns, 261 s | $0.0726 | `harness/trials/r13-zero2repo-case004/runs/haiku-settled-2/` |
| 53 | 2026-10-14 | Zero2Repo case001, Markdown | Haiku | Harbor, CC 2.1.296, 4 tools, allow-list, Zero2Repo judge (report counts) | 302 / 302, official 1.0, 14 turns, 280 s | $0.0498 | `harness/trials/r13b-zero2repo-haiku-sweep/runs/haiku-case001-1/` |
| 54 | 2026-10-14 | Zero2Repo case007, Markdown | Haiku | Harbor, CC 2.1.296, 4 tools, allow-list, Zero2Repo judge (report counts) | 80 / 80, official 1.0, 16 turns, 145 s | $0.0253 | `harness/trials/r13b-zero2repo-haiku-sweep/runs/haiku-case007-1/` |
| 55 | 2026-10-14 | Zero2Repo case011, Markdown | Haiku | Harbor, CC 2.1.296, 4 tools, allow-list, Zero2Repo judge (report counts) | 321 / 321, official 1.0, 20 turns, 466 s | $0.2693 | `harness/trials/r13b-zero2repo-haiku-sweep/runs/haiku-case011-1/` |
| 56 | 2026-10-14 | Zero2Repo case002, Markdown | Haiku | Harbor, CC 2.1.296, 4 tools, allow-list, Zero2Repo judge (report counts) | 281 / 281, official 1.0, 24 turns, 351 s | $0.0726 | `harness/trials/r13b-zero2repo-haiku-sweep/runs/haiku-case002-1/` |
| 57 | 2026-10-14 | Zero2Repo case005, Markdown | Haiku | Harbor, CC 2.1.296, 4 tools, allow-list, Zero2Repo judge (report counts) | 395 / 395, official 1.0, 22 turns, 833 s | $0.3708 | `harness/trials/r13b-zero2repo-haiku-sweep/runs/haiku-case005-1/` |
| 58 | 2026-10-14 | Zero2Repo case010, Markdown | Haiku | Harbor, CC 2.1.296, 4 tools, allow-list, Zero2Repo judge (report counts) | 166 / 197 (146 / 177 scorable: 20 tests need model files our task lacks, found 2026-10-16), official 0, 33 turns, 736 s | $0.4539 | `harness/trials/r13b-zero2repo-haiku-sweep/runs/haiku-case010-1/` |
| 59 | 2026-10-14 | Zero2Repo case006, Markdown | Haiku | Harbor, CC 2.1.296, 4 tools, allow-list, Zero2Repo judge (report counts) | 464 / 476, official 0, 81 turns, 1002 s | $1.2422 | `harness/trials/r13b-zero2repo-haiku-sweep/runs/haiku-case006-1/` |
| 60 | 2026-10-14 | Zero2Repo case016, Markdown | Haiku | Harbor, CC 2.1.296, 4 tools, allow-list, Zero2Repo judge (report counts) | 370 / 388, official 0, 53 turns, 1368 s | $0.5550 | `harness/trials/r13b-zero2repo-haiku-sweep/runs/haiku-case016-1/` |
| 61 | 2026-10-15 | Zero2Repo case010, Markdown | Haiku | Harbor, CC 2.1.296, 4 tools, allow-list, Zero2Repo judge (report counts) | 162 / 197 (142 / 177 scorable), official 0, 44 turns, 707 s | $0.5506 | `harness/trials/r13c-zero2repo-3cases/runs/haiku-case010-markdown-1/` |
| 62 | 2026-10-15 | Zero2Repo case010, Markdown | Sonnet | Harbor, CC 2.1.296, 4 tools, allow-list, Zero2Repo judge (report counts) | 175 / 197 (155 / 177 scorable), official 0, 22 turns, 890 s | $2.1815 | `harness/trials/r13c-zero2repo-3cases/runs/sonnet-case010-markdown-1/` |
| 63 | 2026-10-15 | Zero2Repo case006, Markdown | Haiku | Harbor, CC 2.1.296, 4 tools, allow-list, Zero2Repo judge (report counts) | 452 / 476, official 0, 42 turns, 895 s | $0.9022 | `harness/trials/r13c-zero2repo-3cases/runs/haiku-case006-markdown-1/` |
| 64 | 2026-10-15 | Zero2Repo case006, Markdown | Sonnet | Harbor, CC 2.1.296, 4 tools, allow-list, Zero2Repo judge (report counts) | 470 / 476, official 0, 26 turns, 927 s | $2.4009 | `harness/trials/r13c-zero2repo-3cases/runs/sonnet-case006-markdown-1/` |
| 65 | 2026-10-15 | Zero2Repo case016, Markdown | Haiku | Harbor, CC 2.1.296, 4 tools, allow-list, Zero2Repo judge (report counts) | 381 / 388, official 0, 33 turns, 1130 s | $0.8529 | `harness/trials/r13c-zero2repo-3cases/runs/haiku-case016-markdown-1/` |
| 66 | 2026-10-15 | Zero2Repo case016, Markdown | Sonnet | Harbor, CC 2.1.296, 4 tools, allow-list, Zero2Repo judge (report counts) | 385 / 388, official 0, 25 turns, 1186 s | $2.3885 | `harness/trials/r13c-zero2repo-3cases/runs/sonnet-case016-markdown-1/` |
| 67 | 2026-10-15 | Zero2Repo case010, Markdown | Haiku | Harbor, CC 2.1.296, 4 tools, allow-list, Zero2Repo judge (report counts) | 169 / 197 (149 / 177 scorable), official 0, 47 turns, 811 s | $0.7151 | `harness/trials/r13c-zero2repo-3cases/runs/haiku-case010-markdown-2/` |
| 68 | 2026-10-15 | Zero2Repo case010, Markdown | Sonnet | Harbor, CC 2.1.296, 4 tools, allow-list, Zero2Repo judge (report counts) | 176 / 197 (156 / 177 scorable), official 0, 21 turns, 912 s (rerun after a usage-limit stop) | $2.1427 | `harness/trials/r13c-zero2repo-3cases/runs/sonnet-case010-markdown-2/` |
| 69 | 2026-10-15 | Zero2Repo case006, Markdown | Haiku | Harbor, CC 2.1.296, 4 tools, allow-list, Zero2Repo judge (report counts) | 0 (tests did not load), official 0, 26 turns, 725 s | $0.1145 | `harness/trials/r13c-zero2repo-3cases/runs/haiku-case006-markdown-2/` |
| 70 | 2026-10-15 | Zero2Repo case006, Markdown | Sonnet | Harbor, CC 2.1.296, 4 tools, allow-list, Zero2Repo judge (report counts) | 469 / 476, official 0, 24 turns, 926 s | $2.3553 | `harness/trials/r13c-zero2repo-3cases/runs/sonnet-case006-markdown-2/` |
| 71 | 2026-10-15 | Zero2Repo case016, Markdown | Haiku | Harbor, CC 2.1.296, 4 tools, allow-list, Zero2Repo judge (report counts) | 378 / 388, official 0, 47 turns, 1462 s | $0.9487 | `harness/trials/r13c-zero2repo-3cases/runs/haiku-case016-markdown-2/` |
| 72 | 2026-10-15 | Zero2Repo case016, Markdown | Sonnet | Harbor, CC 2.1.296, 4 tools, allow-list, Zero2Repo judge (report counts) | 387 / 388, official 0, 38 turns, 1426 s (rerun after a usage-limit stop) | $2.3986 | `harness/trials/r13c-zero2repo-3cases/runs/sonnet-case016-markdown-2/` |
| 73 | 2026-10-15 | Zero2Repo case010, export (settled, no `--allow-open`) | Haiku | Harbor, CC 2.1.296, 4 tools, allow-list, Zero2Repo judge (report counts) | 168 / 197 (148 / 177 scorable), official 0, 67 turns, 1112 s | $1.3220 | `harness/trials/r13c-zero2repo-3cases/runs/haiku-case010-export-1/` |
| 74 | 2026-10-15 | Zero2Repo case010, export (settled, no `--allow-open`) | Sonnet | Harbor, CC 2.1.296, 4 tools, allow-list, Zero2Repo judge (report counts) | 176 / 197 (156 / 177 scorable), official 0, 29 turns, 902 s (rerun after a usage-limit stop) | $2.3617 | `harness/trials/r13c-zero2repo-3cases/runs/sonnet-case010-export-1/` |
| 75 | 2026-10-15 | Zero2Repo case010, export (settled, no `--allow-open`) | Haiku | Harbor, CC 2.1.296, 4 tools, allow-list, Zero2Repo judge (report counts) | 166 / 197 (146 / 177 scorable), official 0, 78 turns, 817 s | $1.0555 | `harness/trials/r13c-zero2repo-3cases/runs/haiku-case010-export-2/` |
| 76 | 2026-10-15 | Zero2Repo case010, export (settled, no `--allow-open`) | Sonnet | Harbor, CC 2.1.296, 4 tools, allow-list, Zero2Repo judge (report counts) | 175 / 197 (155 / 177 scorable), official 0, 24 turns, 704 s | $1.6977 | `harness/trials/r13c-zero2repo-3cases/runs/sonnet-case010-export-2/` |
| 77 | 2026-10-15 | Zero2Repo case006, export (settled, no `--allow-open`) | Haiku | Harbor, CC 2.1.296, 4 tools, allow-list, Zero2Repo judge (report counts) | 425 / 476, official 0, 77 turns, 1263 s | $1.0045 | `harness/trials/r13c-zero2repo-3cases/runs/haiku-case006-export-1/` |
| 78 | 2026-10-15 | Zero2Repo case006, export (settled, no `--allow-open`) | Sonnet | Harbor, CC 2.1.296, 4 tools, allow-list, Zero2Repo judge (report counts) | 473 / 476, official 0, 30 turns, 753 s | $2.1689 | `harness/trials/r13c-zero2repo-3cases/runs/sonnet-case006-export-1/` |
| 79 | 2026-10-15 | Zero2Repo case016, export (settled, no `--allow-open`) | Haiku | Harbor, CC 2.1.296, 4 tools, allow-list, Zero2Repo judge (report counts) | 364 / 388, official 0, 80 turns, 2117 s | $1.1296 | `harness/trials/r13c-zero2repo-3cases/runs/haiku-case016-export-1/` |
| 80 | 2026-10-15 | Zero2Repo case016, export (settled, no `--allow-open`) | Sonnet | Harbor, CC 2.1.296, 4 tools, allow-list, Zero2Repo judge (report counts) | 387 / 388, official 0, 37 turns, 1186 s | $2.1847 | `harness/trials/r13c-zero2repo-3cases/runs/sonnet-case016-export-1/` |
| 81 | 2026-10-15 | Zero2Repo case006, export (settled, no `--allow-open`) | Haiku | Harbor, CC 2.1.296, 4 tools, allow-list, Zero2Repo judge (report counts) | 467 / 476, official 0, 63 turns, 1203 s | $1.4731 | `harness/trials/r13c-zero2repo-3cases/runs/haiku-case006-export-2/` |
| 82 | 2026-10-15 | Zero2Repo case006, export (settled, no `--allow-open`) | Sonnet | Harbor, CC 2.1.296, 4 tools, allow-list, Zero2Repo judge (report counts) | 470 / 476, official 0, 31 turns, 1017 s | $2.7664 | `harness/trials/r13c-zero2repo-3cases/runs/sonnet-case006-export-2/` |
| 83 | 2026-10-16 | Zero2Repo case016, export (settled, no `--allow-open`) | Haiku | Harbor, CC 2.1.296, 4 tools, allow-list, Zero2Repo judge (report counts) | 379 / 388, official 0, 87 turns, 1246 s | $1.3504 | `harness/trials/r13c-zero2repo-3cases/runs/haiku-case016-export-2/` |
| 84 | 2026-10-16 | Zero2Repo case016, export (settled, no `--allow-open`) | Sonnet | Harbor, CC 2.1.296, 4 tools, allow-list, Zero2Repo judge (report counts) | 388 / 388, official 1, 27 turns, 952 s | $2.1454 | `harness/trials/r13c-zero2repo-3cases/runs/sonnet-case016-export-2/` |
| 85 | 2026-10-16 | Zero2Repo case006, **lean export** (F7 D15, D16; settled) | Haiku | Harbor, CC 2.1.296, 4 tools, allow-list, Zero2Repo judge (report counts) | 447 / 476, official 0, 95 turns, 1418 s | $0.9954 | `harness/trials/r13d-zero2repo-case006-lean-export/runs/haiku-case006-export-1/` |
| 86 | 2026-10-16 | Zero2Repo case006, **lean export** (F7 D15, D16; settled) | Haiku | Harbor, CC 2.1.296, 4 tools, allow-list, Zero2Repo judge (report counts) | 415 / 476, official 0, 71 turns, 1038 s | $0.5920 | `harness/trials/r13d-zero2repo-case006-lean-export/runs/haiku-case006-export-2/` |
| 87 | 2026-10-16 | Zero2Repo case006, Markdown, **7 conflicts planted** | Haiku | Harbor, CC 2.1.296, 4 tools, allow-list, Zero2Repo judge (report counts); instruction + `NOTES.md` line | 429 / 476, core 424 / 469, official 0, 54 turns, 1165 s | $0.6249 | `harness/trials/r14-zero2repo-case006-conflicts/runs/r2-haiku-markdown-1/` |
| 88 | 2026-10-16 | Zero2Repo case006, export, planted, **unsettled** (`--allow-open`) | Haiku | Harbor, CC 2.1.296, 4 tools, allow-list, Zero2Repo judge (report counts); instruction + `NOTES.md` line | 434 / 476, core 431 / 469, official 0, 43 turns, 1286 s | $0.5272 | `harness/trials/r14-zero2repo-case006-conflicts/runs/r2-haiku-export-1/` |
| 89 | 2026-10-16 | Zero2Repo case006, Markdown, **7 conflicts planted** | Haiku | Harbor, CC 2.1.296, 4 tools, allow-list, Zero2Repo judge (report counts); instruction + `NOTES.md` line | 463 / 476, core 457 / 469, official 0, 57 turns, 1075 s | $1.3020 | `harness/trials/r14-zero2repo-case006-conflicts/runs/r2-haiku-markdown-2/` |
| 90 | 2026-10-16 | Zero2Repo case006, export, planted, **unsettled** (`--allow-open`) | Haiku | Harbor, CC 2.1.296, 4 tools, allow-list, Zero2Repo judge (report counts); instruction + `NOTES.md` line | 469 / 476, core 462 / 469, official 0, 60 turns, 1047 s | $1.2927 | `harness/trials/r14-zero2repo-case006-conflicts/runs/r2-haiku-export-2/` |
| 91 | 2026-10-16 | Zero2Repo case006, Markdown, **7 conflicts planted** | Haiku | Harbor, CC 2.1.296, 4 tools, allow-list, Zero2Repo judge (report counts); instruction + `NOTES.md` line | 0 (stopped early: misread budget; no tests loaded), 16 turns, 618 s | $0.0852 | `harness/trials/r14-zero2repo-case006-conflicts/runs/r2-haiku-markdown-3/` |
| 92 | 2026-10-16 | Zero2Repo case006, export, planted, **unsettled** (`--allow-open`) | Haiku | Harbor, CC 2.1.296, 4 tools, allow-list, Zero2Repo judge (report counts); instruction + `NOTES.md` line | 403 / 476, core 400 / 469, official 0, 90 turns, 1070 s | $1.0934 | `harness/trials/r14-zero2repo-case006-conflicts/runs/r2-haiku-export-3/` |
| 93 | 2026-10-16 | Zero2Repo case006, Markdown, planted, + `DECISIONS.md` (4 rulings) | Haiku | Harbor, CC 2.1.296, 4 tools, allow-list, Zero2Repo judge (report counts); instruction + `NOTES.md` line | 428 / 476, core 423 / 469, official 0, 48 turns, 1156 s | $0.5346 | `harness/trials/r14-zero2repo-case006-conflicts/runs/r3-haiku-markdown-decisions-1/` |
| 94 | 2026-10-16 | Zero2Repo case006, export, planted, **settled** (4 rulings) | Haiku | Harbor, CC 2.1.296, 4 tools, allow-list, Zero2Repo judge (report counts); instruction + `NOTES.md` line | 464 / 476, core 460 / 469, official 0, 39 turns, 978 s | $0.7982 | `harness/trials/r14-zero2repo-case006-conflicts/runs/r3-haiku-export-settled-1/` |
| 95 | 2026-10-16 | Zero2Repo case006, Markdown, planted, + `DECISIONS.md` (4 rulings) | Haiku | Harbor, CC 2.1.296, 4 tools, allow-list, Zero2Repo judge (report counts); instruction + `NOTES.md` line | 455 / 476, core 452 / 469, official 0, 56 turns, 986 s | $0.9534 | `harness/trials/r14-zero2repo-case006-conflicts/runs/r3-haiku-markdown-decisions-2/` |
| 96 | 2026-10-16 | Zero2Repo case006, export, planted, **settled** (4 rulings) | Haiku | Harbor, CC 2.1.296, 4 tools, allow-list, Zero2Repo judge (report counts); instruction + `NOTES.md` line | 461 / 476, core 457 / 469, official 0, 80 turns, 1275 s | $2.0239 | `harness/trials/r14-zero2repo-case006-conflicts/runs/r3-haiku-export-settled-2/` |
| 97 | 2026-10-16 | Zero2Repo case006, Markdown, planted, + `DECISIONS.md` (4 rulings) | Haiku | Harbor, CC 2.1.296, 4 tools, allow-list, Zero2Repo judge (report counts); instruction + `NOTES.md` line | 413 / 476, core 410 / 469, official 0, 58 turns, 1155 s | $0.5810 | `harness/trials/r14-zero2repo-case006-conflicts/runs/r3-haiku-markdown-decisions-3/` |
| 98 | 2026-10-16 | Zero2Repo case006, export, planted, **settled** (4 rulings) | Haiku | Harbor, CC 2.1.296, 4 tools, allow-list, Zero2Repo judge (report counts); instruction + `NOTES.md` line | 452 / 476, core 450 / 469, official 0, 44 turns, 1030 s | $1.0370 | `harness/trials/r14-zero2repo-case006-conflicts/runs/r3-haiku-export-settled-3/` |
| 99 | 2026-10-16 | Zero2Repo case006, Markdown, **7 conflicts planted** | Haiku | Harbor, CC 2.1.296, 4 tools, allow-list, Zero2Repo judge (report counts); instruction + `NOTES.md` line | 454 / 476, core 448 / 469, official 0, 73 turns, 1180 s | $0.6575 | `harness/trials/r14-zero2repo-case006-conflicts/runs/r2-haiku-markdown-4/` |
| 100 | 2026-10-16 | Zero2Repo case006, Markdown, **7 conflicts planted**, round 15 | Haiku | Harbor, CC 2.1.296, 4 tools, allow-list, six-of-seven export comparison; instruction + `NOTES.md` line | 0 (stopped early: output cap in planning, then misread budget "$0.0008 of the $10 remains"; no code, no tests loaded), 6 turns, 584 s | $0.0779 | `harness/trials/r15-zero2repo-case006-conflicts-v2/runs/r15-haiku-markdown-1/` |
| 101 | 2026-10-16 | Zero2Repo case006, export, planted, **6 unsettled conflicts**, round 15 | Haiku | Harbor, CC 2.1.296, 4 tools, allow-list, six-of-seven export comparison; instruction + `NOTES.md` line | 457 / 476, core 454 / 469, official 0, 91 turns, 1040 s | $1.4450 | `harness/trials/r15-zero2repo-case006-conflicts-v2/runs/r15-haiku-export-1/` |
| 102 | 2026-10-17 | Zero2Repo case006, Markdown, **7 conflicts planted**, round 15 | Haiku | Harbor, CC 2.1.296, 4 tools, allow-list, six-of-seven export comparison; instruction + `NOTES.md` line | 436 / 476, core 430 / 469, official 0, 38 turns, 887 s | $0.7853 | `harness/trials/r15-zero2repo-case006-conflicts-v2/runs/r15-haiku-markdown-2/` |
| 103 | 2026-10-17 | Zero2Repo case006, export, planted, **6 unsettled conflicts**, round 15 | Haiku | Harbor, CC 2.1.296, 4 tools, allow-list, six-of-seven export comparison; instruction + `NOTES.md` line | 460 / 476, core 454 / 469, official 0, 97 turns, 1128 s | $1.7415 | `harness/trials/r15-zero2repo-case006-conflicts-v2/runs/r15-haiku-export-2/` |
| 104 | 2026-10-18 | Zero2Repo case006, Markdown, **7 conflicts planted**, round 15 batch 2 | Haiku | Harbor, CC 2.1.296, 4 tools, allow-list, six-of-seven export comparison; instruction + `NOTES.md` line | 429 / 476, core 423 / 469, official 0, 66 turns, 1056 s | $0.4683 | `harness/trials/r15-zero2repo-case006-conflicts-v2/batch-2/runs/r15b-haiku-markdown-1/` |
| 105 | 2026-10-19 | Zero2Repo case006, export, planted, **6 unsettled conflicts**, round 15 batch 2 | Haiku | Harbor, CC 2.1.296, 4 tools, allow-list, six-of-seven export comparison; instruction + `NOTES.md` line | 441 / 476, core 435 / 469, official 0, 64 turns, 1129 s | $1.2666 | `harness/trials/r15-zero2repo-case006-conflicts-v2/batch-2/runs/r15b-haiku-export-1/` |
| 106 | 2026-10-19 | Zero2Repo case006, Markdown, **7 conflicts planted**, round 15 batch 2 | Haiku | Harbor, CC 2.1.296, 4 tools, allow-list, six-of-seven export comparison; instruction + `NOTES.md` line | 463 / 476, core 456 / 469, official 0, 41 turns, 856 s | $0.7842 | `harness/trials/r15-zero2repo-case006-conflicts-v2/batch-2/runs/r15b-haiku-markdown-2/` |
| 107 | 2026-10-19 | Zero2Repo case006, export, planted, **6 unsettled conflicts**, round 15 batch 2 | Haiku | Harbor, CC 2.1.296, 4 tools, allow-list, six-of-seven export comparison; instruction + `NOTES.md` line | 431 / 476, core 428 / 469, official 0, 60 turns, 1115 s | $0.8178 | `harness/trials/r15-zero2repo-case006-conflicts-v2/batch-2/runs/r15b-haiku-export-2/` |
| 108 | 2026-10-19 | Zero2Repo case006, Markdown, **7 conflicts planted**, round 15 batch 2 | Haiku | Harbor, CC 2.1.296, 4 tools, allow-list, six-of-seven export comparison; instruction + `NOTES.md` line | 452 / 476, core 446 / 469, official 0, 53 turns, 1040 s | $1.0257 | `harness/trials/r15-zero2repo-case006-conflicts-v2/batch-2/runs/r15b-haiku-markdown-3/` |
| 109 | 2026-10-28 | Zero2Repo case006, export v3 (F7 D17), planted, **6 unsettled conflicts**, round 15 batch 3 | Haiku | Harbor, CC 2.1.296, 4 tools, allow-list, six-of-seven export comparison; instruction + `NOTES.md` line | 436 / 476, core 433 / 469, official 0, 84 turns, 1314 s | $0.6927 | `harness/trials/r15-zero2repo-case006-conflicts-v2/batch-3/runs/r15c-haiku-export-1/` |
| 110 | 2026-10-28 | Zero2Repo case006, export v3 (F7 D17), planted, **6 unsettled conflicts**, round 15 batch 3 | Haiku | Harbor, CC 2.1.296, 4 tools, allow-list, six-of-seven export comparison; instruction + `NOTES.md` line | 459 / 476, core 452 / 469, official 0, 58 turns, 924 s | $1.1175 | `harness/trials/r15-zero2repo-case006-conflicts-v2/batch-3/runs/r15c-haiku-export-2/` |
| 111 | 2026-10-28 | Zero2Repo case006, export v3 (F7 D17), planted, **6 unsettled conflicts**, round 15 batch 3 | Haiku | Harbor, CC 2.1.296, 4 tools, allow-list, six-of-seven export comparison; instruction + `NOTES.md` line | 460 / 476, core 453 / 469, official 0, 66 turns, 985 s | $1.0431 | `harness/trials/r15-zero2repo-case006-conflicts-v2/batch-3/runs/r15c-haiku-export-3/` |
| 112 | 2026-10-28 | Zero2Repo case006, Markdown, **7 conflicts planted**, round 16 | Sonnet | Harbor, CC 2.1.296, 4 tools, allow-list, six-of-seven export comparison; instruction + `NOTES.md` line | 0 (judge error: the agent's code loops on one hidden test in `F08_acceptance.py` until the test process is killed for memory, reproduced 2026-10-28; the test log stops there; verifier 14:43:25–15:07:14 UTC in `result.json`; code and `NOTES.md` present), official 0, 21 turns, 2341 s | $2.4639 | `harness/trials/r16-zero2repo-case006-conflicts-sonnet/runs/r16-sonnet-markdown-1/` |
| 113 | 2026-10-28 | Zero2Repo case006, export v3 (F7 D17), planted, **6 unsettled conflicts**, round 16 | Sonnet | Harbor, CC 2.1.296, 4 tools, allow-list, six-of-seven export comparison; instruction + `NOTES.md` line | none: stopped by the subscription session limit (429) after 12 turns, 574 s; job kept as `work/jobs/…-r16-sonnet-export-1.limited-20261028T111900`; rerun as 114 | $1.3048 | `harness/trials/r16-zero2repo-case006-conflicts-sonnet/run_queue.log` |
| 114 | 2026-10-28 | Zero2Repo case006, export v3 (F7 D17), planted, **6 unsettled conflicts**, round 16 | Sonnet | Harbor, CC 2.1.296, 4 tools, allow-list, six-of-seven export comparison; instruction + `NOTES.md` line | 472 / 476, core 465 / 469, official 0, 26 turns, 834 s | $2.2644 | `harness/trials/r16-zero2repo-case006-conflicts-sonnet/runs/r16-sonnet-export-1/` |
| 115 | 2026-10-28 | Zero2Repo case006, Markdown, **7 conflicts planted**, round 16 | Sonnet | Harbor, CC 2.1.296, 4 tools, allow-list, six-of-seven export comparison; instruction + `NOTES.md` line | 466 / 476, core 460 / 469, official 0, 22 turns, 962 s | $2.2431 | `harness/trials/r16-zero2repo-case006-conflicts-sonnet/runs/r16-sonnet-markdown-2/` |
| 116 | 2026-10-28 | Zero2Repo case006, export v3 (F7 D17), planted, **6 unsettled conflicts**, round 16 | Sonnet | Harbor, CC 2.1.296, 4 tools, allow-list, six-of-seven export comparison; instruction + `NOTES.md` line | 472 / 476, core 465 / 469, official 0, 27 turns, 962 s | $2.5421 | `harness/trials/r16-zero2repo-case006-conflicts-sonnet/runs/r16-sonnet-export-2/` |
| 117 | 2026-10-30 | Compile, Zero2Repo case006 **24 planted**, round 17 step 1a: up to pair-picking (incremental store) | Haiku | compiler before rel02 D28; round 14 v2 lock replayed | 15 calls, 29 replayed; 1 842 pairs proposed, 0 judged; 11 of 24 planted pairs proposed | $0.1092 | `harness/trials/r17-zero2repo-case006-conflicts-24/TRIAL.md` step 1a |
| 118 | 2026-10-30 | Compile, case006 24 planted, round 17 step 1b (F3 D43, table rows) | Haiku | incremental store, step 1a lock | 5 calls, 83 replayed; 64 nodes formed; 1 884 pairs; no planted pair gained | $0.031 | `harness/trials/r17-zero2repo-case006-conflicts-24/TRIAL.md` step 1b |
| 119 | 2026-10-30 | Compile, case006 24 planted, round 17 step 1d (F3 D44, atom keeps its subject) | Haiku | incremental store, step 1c lock | 5 calls, 96 replayed; 1 899 pairs; every planted sentence in a node | $0.0232 | `harness/trials/r17-zero2repo-case006-conflicts-24/TRIAL.md` step 1d |
| 120 | 2026-10-30/31 | Compile, case006 24 planted, round 17 step 2: **full compile, new store, with judging** | Haiku | compiler with F3 D43–D44, F5 D15–D17; step 1e lock; 3 passes | 1 044 nodes; 757 calls; 69 contradictions; **recall 14 of 24** | $2.8935 | `harness/trials/r17-zero2repo-case006-conflicts-24/work/compile-full/compile-<n>.json`; `harness/trials/r17-zero2repo-case006-conflicts-24/notes/recall.json` |
| 121 | 2026-11-01 | Compile, case006 24 planted, round 17 step 3: **baseline full compile** | Haiku | compiler at `6c40e75` (before rel02 D28), otherwise as step 2 | 648 calls; 70 contradictions; **recall 11 of 24** | $2.4576 | `harness/trials/r17-zero2repo-case006-conflicts-24/work/compile-baseline/compile-<n>.json` (git-ignored); `harness/trials/r17-zero2repo-case006-conflicts-24/TRIAL.md` step 3 |
| 122 | 2026-11-01 | Zero2Repo case006, Markdown, **24 conflicts planted**, round 17 | Haiku | Harbor, CC 2.1.296, 4 tools, allow-list, Zero2Repo judge (report counts); $10 ceiling; instruction + `NOTES.md` line (round 15 wording) | 462 / 476, core 433 / 445, official 0, 45 turns, 983 s | $0.9842 | `harness/trials/r17-zero2repo-case006-conflicts-24/runs/r17-haiku-markdown-1/` |
| 123 | 2026-11-01 | Zero2Repo case006, **oracle export** (24 of 24 flagged, 28 unsettled), round 17 | Haiku | Harbor, CC 2.1.296, 4 tools, allow-list, Zero2Repo judge (report counts); $10 ceiling; instruction + `NOTES.md` line (round 15 wording) | 465 / 476, core 436 / 445, official 0, 59 turns, 1096 s | $1.2362 | `harness/trials/r17-zero2repo-case006-conflicts-24/runs/r17-haiku-export-1/` |
| 124 | 2026-11-01 | Zero2Repo case006, Markdown, **24 conflicts planted**, round 17 | Haiku | Harbor, CC 2.1.296, 4 tools, allow-list, Zero2Repo judge (report counts); $10 ceiling; instruction + `NOTES.md` line (round 15 wording) | 0 (stopped early: output cap while planning, then misread budget; tests failed at import), official 0, 15 turns, 588 s | $0.0863 | `harness/trials/r17-zero2repo-case006-conflicts-24/runs/r17-haiku-markdown-2/` |
| 125 | 2026-11-01 | Zero2Repo case006, **oracle export** (24 of 24 flagged, 28 unsettled), round 17 | Haiku | Harbor, CC 2.1.296, 4 tools, allow-list, Zero2Repo judge (report counts); $10 ceiling; instruction + `NOTES.md` line (round 15 wording) | 449 / 476, core 420 / 445, official 0, 48 turns, 1017 s | $0.9830 | `harness/trials/r17-zero2repo-case006-conflicts-24/runs/r17-haiku-export-2/` |
| 126 | 2026-11-01 | Zero2Repo case006, Markdown, **24 conflicts planted**, round 17 | Haiku | Harbor, CC 2.1.296, 4 tools, allow-list, Zero2Repo judge (report counts); $10 ceiling; instruction + `NOTES.md` line (round 15 wording) | 440 / 476, core 414 / 445, official 0, 59 turns, 1179 s | $0.7402 | `harness/trials/r17-zero2repo-case006-conflicts-24/runs/r17-haiku-markdown-3/` |
| 127 | 2026-11-01 | Zero2Repo case006, **oracle export** (24 of 24 flagged, 28 unsettled), round 17 | Haiku | Harbor, CC 2.1.296, 4 tools, allow-list, Zero2Repo judge (report counts); $10 ceiling; instruction + `NOTES.md` line (round 15 wording) | 461 / 476, core 433 / 445, official 0, 69 turns, 1003 s | $1.2344 | `harness/trials/r17-zero2repo-case006-conflicts-24/runs/r17-haiku-export-3/` |
| 128 | 2026-11-01 | Zero2Repo case006, Markdown, **24 conflicts planted**, round 17 | Sonnet | Harbor, CC 2.1.296, 4 tools, allow-list, Zero2Repo judge (report counts); $10 ceiling; instruction + `NOTES.md` line (round 15 wording) | 452 / 476, core 431 / 445, official 0, 21 turns, 915 s | $2.3417 | `harness/trials/r17-zero2repo-case006-conflicts-24/runs/r17-sonnet-markdown-1/` |
| 129 | 2026-11-01 | Zero2Repo case006, **oracle export** (24 of 24 flagged, 28 unsettled), round 17 | Sonnet | Harbor, CC 2.1.296, 4 tools, allow-list, Zero2Repo judge (report counts); $10 ceiling; instruction + `NOTES.md` line (round 15 wording) | 470 / 476, core 439 / 445, official 0, 29 turns, 892 s | $2.3804 | `harness/trials/r17-zero2repo-case006-conflicts-24/runs/r17-sonnet-export-1/` |
| 130 | 2026-11-01 | Zero2Repo case006, Markdown, **24 conflicts planted**, round 17 | Sonnet | Harbor, CC 2.1.296, 4 tools, allow-list, Zero2Repo judge (report counts); $10 ceiling; instruction + `NOTES.md` line (round 15 wording) | 462 / 476, core 439 / 445, official 0, 20 turns, 931 s | $2.4302 | `harness/trials/r17-zero2repo-case006-conflicts-24/runs/r17-sonnet-markdown-2/` |
| 131 | 2026-11-01 | Zero2Repo case006, **oracle export** (24 of 24 flagged, 28 unsettled), round 17 | Sonnet | Harbor, CC 2.1.296, 4 tools, allow-list, Zero2Repo judge (report counts); $10 ceiling; instruction + `NOTES.md` line (round 15 wording) | none: stopped by the subscription 5-hour limit (429) after 15 turns, 620 s; job kept as `work/jobs/…-r17-sonnet-export-2.limited-20261101T225101`; rerun as 132 | $1.5038 | `harness/trials/r17-zero2repo-case006-conflicts-24/run_queue.log` |
| 132 | 2026-11-02 | Zero2Repo case006, **oracle export** (24 of 24 flagged, 28 unsettled), round 17 | Sonnet | Harbor, CC 2.1.296, 4 tools, allow-list, Zero2Repo judge (report counts); $10 ceiling; instruction + `NOTES.md` line (round 15 wording) | 458 / 476, core 429 / 445, official 0, 23 turns, 801 s | $2.0340 | `harness/trials/r17-zero2repo-case006-conflicts-24/runs/r17-sonnet-export-2/` |
| 133 | 2026-11-02 | Zero2Repo case006, Markdown, **24 conflicts planted**, round 17 | Sonnet | Harbor, CC 2.1.296, 4 tools, allow-list, Zero2Repo judge (report counts); $10 ceiling; instruction + `NOTES.md` line (round 15 wording) | 472 / 476, core 442 / 445, official 0, 23 turns, 943 s | $2.3380 | `harness/trials/r17-zero2repo-case006-conflicts-24/runs/r17-sonnet-markdown-3/` |
| 134 | 2026-11-02 | Zero2Repo case006, **oracle export** (24 of 24 flagged, 28 unsettled), round 17 | Sonnet | Harbor, CC 2.1.296, 4 tools, allow-list, Zero2Repo judge (report counts); $10 ceiling; instruction + `NOTES.md` line (round 15 wording) | 465 / 476, core 439 / 445, official 0, 26 turns, 882 s | $2.1643 | `harness/trials/r17-zero2repo-case006-conflicts-24/runs/r17-sonnet-export-3/` |
| 135 | 2026-11-02 | Zero2Repo case006, **oracle export** (24 of 24 flagged, 28 unsettled), round 18 | Sonnet | Harbor, **CC 2.1.316**, 4 tools, allow-list, Zero2Repo judge (report counts); **no dollar ceiling**; early-stop rerun rule; `NOTES.md` line asks for both sides | gate run, read before the other 11 started: 467 / 476, core 437 / 445, official 0, 27 turns, 865 s | $2.1391 | `harness/trials/r18-zero2repo-case006-notes-both-sides/runs/r18-sonnet-export-1/` |
| 136 | 2026-11-02 | Zero2Repo case006, Markdown, **24 conflicts planted**, round 18 | Haiku | Harbor, **CC 2.1.316**, 4 tools, allow-list, Zero2Repo judge (report counts); **no dollar ceiling**; early-stop rerun rule; `NOTES.md` line asks for both sides | 411 / 476, core 386 / 445, official 0, 48 turns, 999 s | $0.3758 | `harness/trials/r18-zero2repo-case006-notes-both-sides/runs/r18-haiku-markdown-1/` |
| 137 | 2026-11-02 | Zero2Repo case006, **oracle export** (24 of 24 flagged, 28 unsettled), round 18 | Haiku | Harbor, **CC 2.1.316**, 4 tools, allow-list, Zero2Repo judge (report counts); **no dollar ceiling**; early-stop rerun rule; `NOTES.md` line asks for both sides | 400 / 476, core 376 / 445, official 0, 57 turns, 1072 s | $0.6062 | `harness/trials/r18-zero2repo-case006-notes-both-sides/runs/r18-haiku-export-1/` |
| 138 | 2026-11-02 | Zero2Repo case006, Markdown, **24 conflicts planted**, round 18 | Haiku | Harbor, **CC 2.1.316**, 4 tools, allow-list, Zero2Repo judge (report counts); **no dollar ceiling**; early-stop rerun rule; `NOTES.md` line asks for both sides | 406 / 476, core 383 / 445, official 0, 49 turns, 1127 s | $0.5329 | `harness/trials/r18-zero2repo-case006-notes-both-sides/runs/r18-haiku-markdown-2/` |
| 139 | 2026-11-02 | Zero2Repo case006, **oracle export** (24 of 24 flagged, 28 unsettled), round 18 | Haiku | Harbor, **CC 2.1.316**, 4 tools, allow-list, Zero2Repo judge (report counts); **no dollar ceiling**; early-stop rerun rule; `NOTES.md` line asks for both sides | 443 / 476, core 419 / 445, official 0, 74 turns, 1069 s | $1.1659 | `harness/trials/r18-zero2repo-case006-notes-both-sides/runs/r18-haiku-export-2/` |
| 140 | 2026-11-02 | Zero2Repo case006, Markdown, **24 conflicts planted**, round 18 | Haiku | Harbor, **CC 2.1.316**, 4 tools, allow-list, Zero2Repo judge (report counts); **no dollar ceiling**; early-stop rerun rule; `NOTES.md` line asks for both sides | 424 / 476, core 401 / 445, official 0, 54 turns, 1147 s | $0.4624 | `harness/trials/r18-zero2repo-case006-notes-both-sides/runs/r18-haiku-markdown-3/` |
| 141 | 2026-11-02 | Zero2Repo case006, **oracle export** (24 of 24 flagged, 28 unsettled), round 18 | Haiku | Harbor, **CC 2.1.316**, 4 tools, allow-list, Zero2Repo judge (report counts); **no dollar ceiling**; early-stop rerun rule; `NOTES.md` line asks for both sides | 461 / 476, core 431 / 445, official 0, 77 turns, 1348 s | $1.8793 | `harness/trials/r18-zero2repo-case006-notes-both-sides/runs/r18-haiku-export-3/` |
| 142 | 2026-11-02 | Zero2Repo case006, Markdown, **24 conflicts planted**, round 18 | Sonnet | Harbor, **CC 2.1.316**, 4 tools, allow-list, Zero2Repo judge (report counts); **no dollar ceiling**; early-stop rerun rule; `NOTES.md` line asks for both sides | 468 / 476, core 439 / 445, official 0, 17 turns, 857 s | $2.0411 | `harness/trials/r18-zero2repo-case006-notes-both-sides/runs/r18-sonnet-markdown-1/` |
| 143 | 2026-11-02 | Zero2Repo case006, Markdown, **24 conflicts planted**, round 18 | Sonnet | Harbor, **CC 2.1.316**, 4 tools, allow-list, Zero2Repo judge (report counts); **no dollar ceiling**; early-stop rerun rule; `NOTES.md` line asks for both sides | 469 / 476, core 438 / 445, official 0, 24 turns, 934 s | $2.1732 | `harness/trials/r18-zero2repo-case006-notes-both-sides/runs/r18-sonnet-markdown-2/` |
| 144 | 2026-11-02 | Zero2Repo case006, **oracle export** (24 of 24 flagged, 28 unsettled), round 18 | Sonnet | Harbor, **CC 2.1.316**, 4 tools, allow-list, Zero2Repo judge (report counts); **no dollar ceiling**; early-stop rerun rule; `NOTES.md` line asks for both sides | none: stopped by the subscription 5-hour limit (429) after 16 turns, 631 s; job kept as `work/jobs/…-r18-sonnet-export-2.limited-20261102T150230`; rerun as 145 | $1.3326 | `harness/trials/r18-zero2repo-case006-notes-both-sides/run_queue.log` |
| 145 | 2026-11-02 | Zero2Repo case006, **oracle export** (24 of 24 flagged, 28 unsettled), round 18 | Sonnet | Harbor, **CC 2.1.316**, 4 tools, allow-list, Zero2Repo judge (report counts); **no dollar ceiling**; early-stop rerun rule; `NOTES.md` line asks for both sides | 451 / 476, core 437 / 445, official 0, 25 turns, 910 s | $2.3808 | `harness/trials/r18-zero2repo-case006-notes-both-sides/runs/r18-sonnet-export-2/` |
| 146 | 2026-11-02 | Zero2Repo case006, Markdown, **24 conflicts planted**, round 18 | Sonnet | Harbor, **CC 2.1.316**, 4 tools, allow-list, Zero2Repo judge (report counts); **no dollar ceiling**; early-stop rerun rule; `NOTES.md` line asks for both sides | 469 / 476, core 439 / 445, official 0, 23 turns, 872 s | $2.1344 | `harness/trials/r18-zero2repo-case006-notes-both-sides/runs/r18-sonnet-markdown-3/` |
| 147 | 2026-11-02 | Zero2Repo case006, **oracle export** (24 of 24 flagged, 28 unsettled), round 18 | Sonnet | Harbor, **CC 2.1.316**, 4 tools, allow-list, Zero2Repo judge (report counts); **no dollar ceiling**; early-stop rerun rule; `NOTES.md` line asks for both sides | 455 / 476, core 439 / 445, official 0, 27 turns, 865 s | $2.1295 | `harness/trials/r18-zero2repo-case006-notes-both-sides/runs/r18-sonnet-export-3/` |
| 148 | 2026-11-02 | Compile, Zero2Repo case010 **15 planted**, round 19 step 2: full from-scratch compile with judging | Haiku | compiler at `0fed585`, unchanged; round 13c case010 profile and lock replayed; 2 passes (call cap 300 per pass) | 386 calls (300 + 86), 922 answers replayed; 517 nodes; 46 contradictions, 34 duplications, 5 subsumptions; **compiler recall 9 of 15** (4 misses never proposed, 2 judged and rejected) | $1.4947 | `harness/trials/r19-zero2repo-case010-conflicts/TRIAL.md` step 2 |
| 149 | 2026-11-03 | Zero2Repo case010, **oracle export** (15 of 15 flagged, 19 unsettled), model files in the verifier only, round 19 **gate run** | Sonnet | Harbor, **CC 2.1.316**, 4 tools, allow-list, Zero2Repo judge (report counts); **no dollar ceiling**; early-stop rerun rule; `NOTES.md` line asks for both sides | 189 / 197, core 168 / 173 (**gate ≥ 171: failed**), named 14 / 15, official 0, 21 turns, 548 s | $1.3077 | `harness/trials/r19-zero2repo-case010-conflicts/runs/r19-sonnet-export-1/` |
| 150 | 2026-11-03 | Zero2Repo case010, Markdown, **15 conflicts planted**, round 19 | Haiku | Harbor, **CC 2.1.316**, 4 tools, allow-list, Zero2Repo judge (report counts); **no dollar ceiling**; early-stop rerun rule; `NOTES.md` line asks for both sides; model files in the verifier only | 164 / 197, core 151 / 173, named 11 / 15, official 0, 37 turns, 739 s | $0.4853 | `harness/trials/r19-zero2repo-case010-conflicts/runs/r19-haiku-markdown-1/` |
| 151 | 2026-11-03 | Zero2Repo case010, **oracle export** (15 of 15 flagged, 19 unsettled), round 19 | Haiku | Harbor, **CC 2.1.316**, 4 tools, allow-list, Zero2Repo judge (report counts); **no dollar ceiling**; early-stop rerun rule; `NOTES.md` line asks for both sides; model files in the verifier only | 176 / 197, core 157 / 173, named 14 / 15, official 0, 56 turns, 1042 s | $0.8474 | `harness/trials/r19-zero2repo-case010-conflicts/runs/r19-haiku-export-1/` |
| 152 | 2026-11-03 | Zero2Repo case010, Markdown, **15 conflicts planted**, round 19 | Haiku | Harbor, **CC 2.1.316**, 4 tools, allow-list, Zero2Repo judge (report counts); **no dollar ceiling**; early-stop rerun rule; `NOTES.md` line asks for both sides; model files in the verifier only | 165 / 197, core 151 / 173, named 6 / 15, official 0, 40 turns, 697 s | $0.5013 | `harness/trials/r19-zero2repo-case010-conflicts/runs/r19-haiku-markdown-2/` |
| 153 | 2026-11-03 | Zero2Repo case010, **oracle export** (15 of 15 flagged, 19 unsettled), round 19 | Haiku | Harbor, **CC 2.1.316**, 4 tools, allow-list, Zero2Repo judge (report counts); **no dollar ceiling**; early-stop rerun rule; `NOTES.md` line asks for both sides; model files in the verifier only | 167 / 197, core 158 / 173, named 14 / 15, official 0, 59 turns, 1281 s | $1.0216 | `harness/trials/r19-zero2repo-case010-conflicts/runs/r19-haiku-export-2/` |
| 154 | 2026-11-03 | Zero2Repo case010, Markdown, **15 conflicts planted**, round 19 | Haiku | Harbor, **CC 2.1.316**, 4 tools, allow-list, Zero2Repo judge (report counts); **no dollar ceiling**; early-stop rerun rule; `NOTES.md` line asks for both sides; model files in the verifier only | 177 / 197, core 164 / 173, named 6 / 15, official 0, 41 turns, 763 s | $0.5651 | `harness/trials/r19-zero2repo-case010-conflicts/runs/r19-haiku-markdown-3/` |
| 155 | 2026-11-03 | Zero2Repo case010, **oracle export** (15 of 15 flagged, 19 unsettled), round 19 | Haiku | Harbor, **CC 2.1.316**, 4 tools, allow-list, Zero2Repo judge (report counts); **no dollar ceiling**; early-stop rerun rule; `NOTES.md` line asks for both sides; model files in the verifier only | 174 / 197, core 162 / 173, named 15 / 15, official 0, 64 turns, 897 s | $1.0657 | `harness/trials/r19-zero2repo-case010-conflicts/runs/r19-haiku-export-3/` |
| 156 | 2026-11-03 | Zero2Repo case010, Markdown, **15 conflicts planted**, round 19 | Sonnet | Harbor, **CC 2.1.316**, 4 tools, allow-list, Zero2Repo judge (report counts); **no dollar ceiling**; early-stop rerun rule; `NOTES.md` line asks for both sides; model files in the verifier only | 190 / 197, core 171 / 173, named 11 / 15, official 0, 17 turns, 844 s | $1.7889 | `harness/trials/r19-zero2repo-case010-conflicts/runs/r19-sonnet-markdown-1/` |
| 157 | 2026-11-03 | Zero2Repo case010, Markdown, **15 conflicts planted**, round 19 | Sonnet | Harbor, **CC 2.1.316**, 4 tools, allow-list, Zero2Repo judge (report counts); **no dollar ceiling**; early-stop rerun rule; `NOTES.md` line asks for both sides; model files in the verifier only | 184 / 197, core 165 / 173, named 11 / 15, official 0, 15 turns, 634 s | $1.3362 | `harness/trials/r19-zero2repo-case010-conflicts/runs/r19-sonnet-markdown-2/` |
| 158 | 2026-11-03 | Zero2Repo case010, **oracle export** (15 of 15 flagged, 19 unsettled), round 19 | Sonnet | Harbor, **CC 2.1.316**, 4 tools, allow-list, Zero2Repo judge (report counts); **no dollar ceiling**; early-stop rerun rule; `NOTES.md` line asks for both sides; model files in the verifier only | 195 / 197, core 171 / 173, named 14 / 15, official 0, 25 turns, 774 s | $1.7127 | `harness/trials/r19-zero2repo-case010-conflicts/runs/r19-sonnet-export-2/` |
| 159 | 2026-11-03 | Zero2Repo case010, Markdown, **15 conflicts planted**, round 19 | Sonnet | Harbor, **CC 2.1.316**, 4 tools, allow-list, Zero2Repo judge (report counts); **no dollar ceiling**; early-stop rerun rule; `NOTES.md` line asks for both sides; model files in the verifier only | 184 / 197, core 168 / 173, named 8 / 15, official 0, 13 turns, 556 s | $1.1996 | `harness/trials/r19-zero2repo-case010-conflicts/runs/r19-sonnet-markdown-3/` |
| 160 | 2026-11-03 | Zero2Repo case010, **oracle export** (15 of 15 flagged, 19 unsettled), round 19 | Sonnet | Harbor, **CC 2.1.316**, 4 tools, allow-list, Zero2Repo judge (report counts); **no dollar ceiling**; early-stop rerun rule; `NOTES.md` line asks for both sides; model files in the verifier only | 173 / 197, core 164 / 173, named 14 / 15, official 0, 21 turns, 704 s | $1.6897 | `harness/trials/r19-zero2repo-case010-conflicts/runs/r19-sonnet-export-3/` |
| 161 | 2026-11-04 | Compile, Zero2Repo case010 **14 gaps** (facts removed), round 20 step 3: full from-scratch compile with judging | Haiku | compiler at `0fed585`, unchanged; round 13c case010 profile and lock replayed; 2 passes (call cap 300 per pass) | 356 calls (300 + 56), 888 answers replayed; 477 nodes; 22 contradictions (all judged false on the owner's behalf, 14 as round 19, none injected), 35 duplications, 5 subsumptions | $1.3493 | `harness/trials/r20-zero2repo-case010-gaps/TRIAL.md` step 3 |
| 162 | 2026-11-05 | Zero2Repo case010, **plain export** of the gapped spec (0 unsettled, no gap flagged), round 20, **check run** | Sonnet | Harbor, **CC 2.1.316**, 4 tools, allow-list, Zero2Repo judge (report counts); **no dollar ceiling**; early-stop rerun rule; `NOTES.md` lines ask for both sides and for unstated points; model files in the verifier only | 193 / 197, core 171 / 175, silent inventions 14 / 14, flagged 0 / 14, official 0, 19 turns, 563 s | $1.3550 | `harness/trials/r20-zero2repo-case010-gaps/runs/r20-sonnet-export-1/` |
| 163 | 2026-11-05 | Zero2Repo case010, Markdown, **14 gaps** (facts removed), round 20 | Haiku | Harbor, **CC 2.1.316**, 4 tools, allow-list, Zero2Repo judge (report counts); **no dollar ceiling**; early-stop rerun rule; `NOTES.md` lines ask for both sides and for unstated points; model files in the verifier only | 187 / 197, core 165 / 175, silent inventions 12 / 14, flagged 2 / 14, official 0, 46 turns, 820 s | $0.6543 | `harness/trials/r20-zero2repo-case010-gaps/runs/r20-haiku-markdown-1/` |
| 164 | 2026-11-05 | Zero2Repo case010, **plain export** of the gapped spec (0 unsettled, no gap flagged), round 20 | Haiku | Harbor, **CC 2.1.316**, 4 tools, allow-list, Zero2Repo judge (report counts); **no dollar ceiling**; early-stop rerun rule; `NOTES.md` lines ask for both sides and for unstated points; model files in the verifier only | 186 / 197, core 164 / 175, silent inventions 11 / 14, flagged 3 / 14, official 0, 73 turns, 1113 s | $1.4018 | `harness/trials/r20-zero2repo-case010-gaps/runs/r20-haiku-export-1/` |
| 165 | 2026-11-05 | Zero2Repo case010, Markdown, **14 gaps** (facts removed), round 20 | Haiku | Harbor, **CC 2.1.316**, 4 tools, allow-list, Zero2Repo judge (report counts); **no dollar ceiling**; early-stop rerun rule; `NOTES.md` lines ask for both sides and for unstated points; model files in the verifier only | 179 / 197, core 158 / 175, silent inventions 10 / 14, flagged 4 / 14, official 0, 34 turns, 733 s | $0.5328 | `harness/trials/r20-zero2repo-case010-gaps/runs/r20-haiku-markdown-2/` |
| 166 | 2026-11-05 | Zero2Repo case010, **plain export** of the gapped spec (0 unsettled, no gap flagged), round 20 | Haiku | Harbor, **CC 2.1.316**, 4 tools, allow-list, Zero2Repo judge (report counts); **no dollar ceiling**; early-stop rerun rule; `NOTES.md` lines ask for both sides and for unstated points; model files in the verifier only | 179 / 197, core 158 / 175, silent inventions 10 / 14, flagged 4 / 14, official 0, 91 turns, 1162 s | $1.5028 | `harness/trials/r20-zero2repo-case010-gaps/runs/r20-haiku-export-2/` |
| 167 | 2026-11-05 | Zero2Repo case010, Markdown, **14 gaps** (facts removed), round 20 | Haiku | Harbor, **CC 2.1.316**, 4 tools, allow-list, Zero2Repo judge (report counts); **no dollar ceiling**; early-stop rerun rule; `NOTES.md` lines ask for both sides and for unstated points; model files in the verifier only | 186 / 197, core 164 / 175, silent inventions 10 / 14, flagged 4 / 14, official 0, 55 turns, 939 s | $0.8831 | `harness/trials/r20-zero2repo-case010-gaps/runs/r20-haiku-markdown-3/` |
| 168 | 2026-11-05 | Zero2Repo case010, **plain export** of the gapped spec (0 unsettled, no gap flagged), round 20 | Haiku | Harbor, **CC 2.1.316**, 4 tools, allow-list, Zero2Repo judge (report counts); **no dollar ceiling**; early-stop rerun rule; `NOTES.md` lines ask for both sides and for unstated points; model files in the verifier only | 178 / 197, core 157 / 175, silent inventions 12 / 14, flagged 2 / 14, official 0, 53 turns, 846 s | $0.9294 | `harness/trials/r20-zero2repo-case010-gaps/runs/r20-haiku-export-3/` |
| 169 | 2026-11-05 | Zero2Repo case010, Markdown, **14 gaps** (facts removed), round 20 | Sonnet | Harbor, **CC 2.1.316**, 4 tools, allow-list, Zero2Repo judge (report counts); **no dollar ceiling**; early-stop rerun rule; `NOTES.md` lines ask for both sides and for unstated points; model files in the verifier only | 195 / 197, core 173 / 175, silent inventions 13 / 14, flagged 1 / 14, official 0, 17 turns, 686 s | $1.4171 | `harness/trials/r20-zero2repo-case010-gaps/runs/r20-sonnet-markdown-1/` |
| 170 | 2026-11-05 | Zero2Repo case010, Markdown, **14 gaps** (facts removed), round 20 | Sonnet | Harbor, **CC 2.1.316**, 4 tools, allow-list, Zero2Repo judge (report counts); **no dollar ceiling**; early-stop rerun rule; `NOTES.md` lines ask for both sides and for unstated points; model files in the verifier only | 191 / 197, core 169 / 175, silent inventions 14 / 14, flagged 0 / 14, official 0, 18 turns, 787 s | $1.6261 | `harness/trials/r20-zero2repo-case010-gaps/runs/r20-sonnet-markdown-2/` |
| 171 | 2026-11-05 | Zero2Repo case010, **plain export** of the gapped spec (0 unsettled, no gap flagged), round 20 | Sonnet | Harbor, **CC 2.1.316**, 4 tools, allow-list, Zero2Repo judge (report counts); **no dollar ceiling**; early-stop rerun rule; `NOTES.md` lines ask for both sides and for unstated points; model files in the verifier only | 193 / 197, core 171 / 175, silent inventions 14 / 14, flagged 0 / 14, official 0, 20 turns, 745 s | $1.5853 | `harness/trials/r20-zero2repo-case010-gaps/runs/r20-sonnet-export-2/` |
| 172 | 2026-11-05 | Zero2Repo case010, Markdown, **14 gaps** (facts removed), round 20 | Sonnet | Harbor, **CC 2.1.316**, 4 tools, allow-list, Zero2Repo judge (report counts); **no dollar ceiling**; early-stop rerun rule; `NOTES.md` lines ask for both sides and for unstated points; model files in the verifier only | 195 / 197, core 173 / 175, silent inventions 13 / 14, flagged 1 / 14, official 0, 16 turns, 699 s | $1.4363 | `harness/trials/r20-zero2repo-case010-gaps/runs/r20-sonnet-markdown-3/` |
| 173 | 2026-11-05 | Zero2Repo case010, **plain export** of the gapped spec (0 unsettled, no gap flagged), round 20 | Sonnet | Harbor, **CC 2.1.316**, 4 tools, allow-list, Zero2Repo judge (report counts); **no dollar ceiling**; early-stop rerun rule; `NOTES.md` lines ask for both sides and for unstated points; model files in the verifier only | 195 / 197, core 173 / 175, silent inventions 12 / 14, flagged 2 / 14, official 0, 23 turns, 780 s | $1.8264 | `harness/trials/r20-zero2repo-case010-gaps/runs/r20-sonnet-export-3/` |

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

Tokens for runs 29 to 34 (Harbor `result.json`; input incl. cache, cache read, output): 38 745,
26 880, 5 378 · 81 117, 64 637, 6 233 · 34 220, 26 474, 3 555 · 118 469, 99 079, 4 134 ·
161 639, 140 108, 11 657 · 208 397, 175 110, 12 717.
