# Metrics, benchmarks and test platforms for the spec-representation study

Researched 2026-09-29 for the MIA 5150 project. Companion to `some-test-benchmarks.md` (owner's first pass) and `project-proposal.md`.

**Question.** Which metrics measure *code quality*, *hallucination* and *spec omission*; which popular benchmarks and platforms can run our three spec formats (flat Markdown, tiered SDD Markdown, compiled spec graph) as custom specs and report those metrics; and what is not supported anywhere?

## 0. How far to trust this

- **Opened** = I fetched the paper's arXiv abstract page or the project's README or docs page on 2026-09-29. **No paper's full text was read.** Fetched pages were summarised by a small model, so a detail that matters must be re-checked on the page.
- **Snippet only** = seen in a web-search result and not opened. Not to be cited.
- **From owner's file** = taken from `some-test-benchmarks.md` and not re-opened by me.
- Numbers are quoted as the authors report them, never recomputed. Papers dated mid-2026 are recent; I could not cross-check them against a second source.
- Nothing here is a measurement of our own. No new numbers are invented.

## 1. Metrics

### 1.1 Code quality

| Metric | What it measures / how | Source (opened) | Automatic? | Limits for us |
|---|---|---|---|---|
| pass@k | Share of tasks with ≥ 1 of k samples passing all tests | Chen et al. 2021 (arXiv 2107.03374) | Yes | Needs tests that cover the spec; says nothing about omitted requirements no test checks |
| Resolved rate | Share of tasks whose patch makes the designated failing tests pass without breaking others | Jimenez et al., ICLR 2024 (arXiv 2310.06770) | Yes | Same |
| Test-suite strength | Stronger tests lower measured pass rates: HumanEval+ has about 80× more tests, pass@k falls 19.3–28.9 % | Liu et al., NeurIPS 2023 (arXiv 2305.01210) | Yes | Warns that a weak hidden-test suite over-reports quality |
| Efficiency | Speed of generated code (EvalPerf) | EvalPlus README | Yes | Only within EvalPlus' own tasks |
| Non-functional quality: security, maintainability, performance efficiency, guided by ISO/IEC 25010 | Sun et al. (arXiv 2511.10271) report a gap between what research measures and what practitioners value (maintainability, readability), and that prompting alone did not reliably improve them | Sun et al. 2025/26 | Partly | Abstract does not name a tool set |
| Static-analysis maintainability (complexity, smells, lint) | SonarQube, CodeQL, PMD and similar tools | **Snippet only** (search result summarising a survey); not opened | Yes | Snippet says static metrics capture only part of maintainability |
| Similarity to a reference (BLEU-like, AST similarity, Token F1) | ProjectEval uses it beside execution; the portability study reports Token F1, AST similarity and syntax validity | Liu et al. ProjectEval (2503.07010); Grynets et al. (2608.21208) | Yes | Weak alignment with human judgement is claimed by Ponnusamy (2502.07835) for BLEU/ROUGE; needs a reference solution |
| LLM-as-judge quality | An LLM scores correctness or usefulness | Zheng et al. NeurIPS 2023; Crupi et al., TSE 2025 (arXiv 2507.16587); DevBench 2026 uses "LLM-judge assessments" | Yes | Crupi et al. report that even the best judge (GPT-4-turbo) "frequently misjudges the correctness of the code"; use for triage only |

### 1.2 Hallucination

| Metric / taxonomy | What it counts | Source (opened) | Automatic? | Limits for us |
|---|---|---|---|---|
| HalluCode taxonomy | 3 primary and 12 specific hallucination categories in generated code, plus a benchmark | Liu et al., TSE (arXiv 2404.00971) | Mostly manual labelling | Categories are about code vs intent and world knowledge, not "requirement not in the spec" |
| Practical-generation taxonomy | Taxonomy from six LLMs, repository-level dependency context; retrieval mitigation | Zhang et al., ISSTA 2025 (arXiv 2409.20550) | Manual | Same |
| CodeHalu | Four types (mapping, naming, resource, logic), detected by **execution-based verification**; 8 883 samples from 699 tasks | Tian et al., AAAI 2025 (arXiv 2405.00253) | Yes, needs runnable tasks with tests | Built on function-level tasks |
| Package hallucination rate | Share of suggested packages that do not exist in the official registry; 576 000 samples, 16 LLMs; commercial ≈ 5.2 %, open-source ≈ 21.7 % as reported | Spracklen et al., USENIX Security 2025 (arXiv 2406.10279) | **Yes**, registry lookup | Easy to reuse as one hallucination counter. Code and data on GitHub per the authors |
| Groundedness under unsatisfiable prompts | Whether the model fabricates or refuses when the task cannot be done; 270 prompts, 6 languages; Cohen's κ 0.73 against human judgement | Dasu, Kundu, Tan (arXiv 2609.03267) | Partly | Not spec-conditioned |
| Survey with taxonomy, benchmarks, metrics | Reviews taxonomies, benchmarks and mitigation | Lee et al. (arXiv 2504.20799) | — | Abstract lists no metric groups. A four-category taxonomy in a search snippet was **not** confirmed by the page; do not cite it |
| SBC score | "Reconstructs system requirements from AI-generated code and compares them with the original specifications"; combines semantic similarity, BLEU and a completeness check; flags missing features and hallucinations | Ponnusamy (arXiv 2502.07835) | Yes (LLM-based) | **Closest to our need** for both omission and invented behaviour. Single-author preprint; validity untested by us |

### 1.3 Spec omission (requirement coverage)

| Metric | What it measures | Source (opened) | Limits for us |
|---|---|---|---|
| SBC completeness | Missing features found by reverse-generating requirements from code and comparing to the spec | Ponnusamy (2502.07835) | See above |
| Prompt Coverage Adequacy | How well a **test suite** satisfies the requirements in a prompt, via LLM attention; reported to find over 30 % more faults than code coverage when guiding test generation | Tambon et al. (arXiv 2607.02057) | Measures the tests' coverage of the prompt, not the code's; needs model attention access, so probably not for hosted Claude |
| API coverage | Share of specified endpoints the generated repository implements (RepoGenesis, reported up to 73.91 %) | Repo-level benchmark (arXiv 2601.13943) | Specific to web microservices |
| Functionality coverage | Share of required functionality covered, reported beside pass rate | Repo0 (arXiv 2608.19854) | Method paper with six repositories |
| Requirement success rate with a traceability graph | Success rate on 125 use cases; the Validator agent builds a graph linking requirements, design and code | TraceDev (arXiv 2607.18886) | A method, not a shared metric |
| Trace-link precision / recall | Standard traceability-recovery measures | **Not opened** (surveyed only in the lecture) | Needs a primary source |
| Omission as a spec defect | WiseSpec names Conflict, Omission and Ambiguity as *requirement* deficiencies, not code omissions | WiseSpec (arXiv 2609.00568) | Different thing; do not confuse |

**Finding.** There is no shared, benchmark-native "requirement omission rate". The nearest are SBC completeness (single paper) and per-benchmark coverage numbers (API coverage, functionality coverage). The obvious build is what our proposal already plans: number the requirements before the run, have a script and a blind audit map each to code, and report the share not implemented.

## 2. Benchmarks

"Spec form" = what the agent is given. "Custom" = can we add our own task or spec.

| Benchmark | Spec form | Reported measures | Custom tasks? | Fit for three-spec-format study |
|---|---|---|---|---|
| Doc2Feat-Bench (was NoCode-bench), arXiv 2507.18130 | A documentation change; 634 tasks, 10 projects | Task success against developer tests | Not stated on the abstract page | Nearest to "spec in, feature out"; abstract only opened; licence and runner unchecked |
| FEA-Bench, ACL 2025 (2503.06680) | Feature description from pull requests, 83 repositories | Unit-test pass | Not stated | Feature implementation; spec is prose, not a structured spec |
| FeatureBench (2602.10975) | Tasks derived by tracing tests along dependency graphs; 200 tasks, 3 825 environments | Execution-based resolution (reported 11.0 % for the best model) | The authors ship an automatic task-collection toolkit | Can make more tasks, but the task text is not a structured spec |
| ProjectEval (2503.07010) | **Three input levels: natural language or code skeleton** | Execution by simulated user interaction, plus code similarity | Not stated | Its levels of input detail are a spec-format variable, close to our idea; check whether inputs can be replaced |
| RealBench (2604.22659) | Text requirements **plus UML diagrams** as system specification | Pass and analysis of failures | Not stated | Already treats spec *format* as a factor |
| RepoGenesis (2601.13943) | README → whole microservice repository; 106 repos | Pass@1, API coverage, deployment success | Public | Has a coverage metric; web-services only |
| ProgramBench (2605.03546) | A program's documentation; rebuild to match a reference executable | Agent-fuzzed behavioural tests; 200 tasks | Not stated | From-scratch like ours; behaviour, not spec-coverage |
| DevBench 2026 (2601.11895) | Telemetry-driven completion instances, 1 800 | Functional correctness, similarity, LLM judge | — | **Not spec-driven.** A search snippet said "PRDs and UML"; the abstract page does not, and that snippet probably described the older 2024 DevBench, which I did not open |
| ClassEval (2308.01861) | 100 class-level tasks | Test-based | Open source | Small, class-level |
| BigCodeBench | 1 140 tasks; *Complete* (docstring) vs *Instruct* (natural-language instruction) splits | pass@1, calibrated pass@k; Apache-2.0 | Not documented | Its two instruction forms are a small spec-format comparison; function-level |
| HumanEval / MBPP / EvalPlus | Docstring or short prompt | pass@k; EvalPlus adds 80× / 35× tests, Apache-2.0 | EvalPlus: not documented | Function-level; no repository or spec structure |
| LiveCodeBench | Contest problems | pass@1, pass@5; four scenarios; MIT | Only evaluates custom-format *outputs* via `custom_evaluator.py`, not new tasks | Not spec-driven |
| SWE-bench (Verified) | Issue text | Resolved rate | **Task collection paused by maintainers**; pipeline targets PyPI packages | Issue-to-patch, not spec |
| SWE-bench Pro V2 | 642 tasks, 11 repos, `instruction.md` per Harbor task | Verifier on a pristine image; 50-minute budget | Fixed public split | Hard; tasks fixed |
| Commit0 | Library with implementations erased | Unit tests | Via OpenHands list only | Not opened directly |
| SpecBench (2605.30314) | Design proposals from RFC processes | Accuracy of spotting spec defects; best agent reported 44.4 % | — | Measures *reviewing* specs, not implementing them; note for future |
| From owner's file, not re-opened: Aider Polyglot, AgentBench, SWE-bench guides, SWE-bench evaluation guide | | | | See `some-test-benchmarks.md` |

## 3. Platforms (harnesses that can run custom specs)

| Platform | What it is | Custom specs / tasks | Runs Claude Code as the agent? | Metrics you get natively | Notes (source opened) |
|---|---|---|---|---|---|
| **Inspect AI** (UK AISI) | Eval framework | **Yes.** Datasets from CSV/JSON/JSONL; each sample can carry `files` copied into a sandbox and a `setup` script | **Yes, per docs:** "Claude Code and Codex CLI via the Inspect SWE package" and an Agent Bridge. Sandbox behaviour of those agents not confirmed on the page | Built-ins: text matching, `model_graded_qa`, `model_graded_fact`; several scorers per task; metrics such as accuracy, standard error, confidence intervals | Best fit for custom, controlled comparisons of spec formats and for error bars. Requirement coverage and hallucination scorers would be ours |
| **Harbor** | Task packaging: `instruction.md`, `task.toml`, `environment/`, `tests/test.sh` | **Yes** | Claude Code named as an example consumer; agent compatibility not detailed on the page | `reward.txt`, or `reward.json` with **several labelled metrics** | A verifier script can emit *coverage* and *hallucination* counts as separate rewards |
| **Terminal-Bench** (Harbor org) | Continuous benchmark of agent tasks; Apache-2.0 | Contributions via CONTRIBUTING and a proposal rubric (aimed at the public benchmark, not private studies) | **Yes**, example command uses `--agent claude-code` | Task verifier | Use Harbor's format directly for private tasks |
| **OpenHands Benchmarks** | Runner for SWE-bench, SWE-bench Pro, GAIA, Commit0, OpenAgentSafety, ProgramBench | Adding a benchmark is not documented on the page | Claude models via LiteLLM proxy | Per-benchmark grading | Repository is mid-migration (V0 → V1) |
| **SWE-bench harness** | Docker-based test runner | Task creation paused | — | Resolved/unresolved counts | Not for us |
| **lm-evaluation-harness** (EleutherAI, MIT) | 60+ academic benchmarks, YAML custom tasks; HumanEval, MBPP | Yes (YAML) | No agentic loop mentioned | Task-defined | Wrong shape: prompt → text, not repository agents |
| **DeepEval** (Apache-2.0) | LLM-app evaluation | Yes, custom metrics | Not a coding-agent runner | **G-Eval** and DAG LLM-judge builders; a **Hallucination metric** ("factually correct against provided context"); agent metrics (task completion, tool correctness, plan adherence) | Could score "is each claim in the generated summary supported by the spec", i.e. a spec-grounded hallucination check, on text |
| **promptfoo** | Prompt/model test CLI | Yes, custom assertions and LLM rubrics (page is thin) | Coding-agent support not documented on the page | Assertion pass/fail | Optional |

## 4. Coverage matrix: which platform can report which of our metrics?

Legend: **N** native; **S** scorer or verifier we write (platform supports it); **—** not supported or not confirmed.

| Metric | Inspect | Harbor / Terminal-Bench | OpenHands | SWE-bench | DeepEval | lm-eval-harness |
|---|---|---|---|---|---|---|
| Tests passed / resolved rate | S | S (verifier `test.sh`) | N (for its benchmarks) | N | — | N (HumanEval, MBPP only) |
| Confidence intervals over runs | N | S (aggregation is configurable, per owner's file) | — | — | — | — |
| Requirement omission rate | S | S | — | — | S (custom G-Eval) | — |
| Invented requirement / spec-grounded hallucination | S | S | — | — | S (Hallucination metric or G-Eval; text only) | — |
| Non-existent package / API | S | S | — | — | — | — |
| Static-analysis quality (lint, complexity, smells) | S | S | — | — | — | — |
| LLM-judge quality | N (`model_graded_*`) | S | — | — | N (G-Eval) | — |
| Cost and token logging | N (limits; per owner's file) | — | Contribution guide asks for it (owner's file) | — | — | — |
| Runs Claude Code | via Inspect SWE | supported agent in Terminal-Bench | via LiteLLM proxy (Claude models) | — | — | — |

**No platform I opened natively reports requirement omission or spec-grounded hallucination for generated code.** Every route is "write a scorer or verifier".

## 5. Not supported anywhere: keep for the future

1. **Requirement-level omission rate as a shared metric.** Only SBC completeness (one preprint) and benchmark-specific coverage numbers exist.
2. **Spec-grounded hallucination** (behaviour the spec never asks for). Existing hallucination work targets world facts (packages, APIs), execution behaviour (CodeHalu) or intent mismatch (HalluCode), not "not in the spec".
3. **Representation as a controlled variable in a standard benchmark.** I found no benchmark that renders the same requirements as flat, tiered and graph forms. ProjectEval (input levels), RealBench (text + UML) and BigCodeBench (docstring vs instruction) come nearest.
4. **Trace-link quality for generated code** (which node each code unit satisfies): only method papers (TraceDev). Primary source for standard traceability metrics not yet opened.
5. **Judge reliability on requirement-to-code matching.** Crupi et al. and Zheng et al. cover correctness and preferences, not this.

## 6. Popular, but they do not fit our custom specs and metrics: revisit later

| Platform / benchmark | Why it is out now | When to revisit |
|---|---|---|
| SWE-bench Verified | Issue text, not spec; task collection paused by maintainers | If task collection reopens, or as an external baseline for the agents |
| SWE-bench Pro V2 | Fixed 642 public tasks | If we later want a hard external baseline; its Harbor format could hold custom tasks |
| HumanEval, MBPP, EvalPlus, BigCodeBench, ClassEval | Function or class level; no repository or spec structure | As a sanity check of the harness (do known models score as published) |
| LiveCodeBench | Contest problems; only custom-format *outputs* | Contamination-free baselines |
| DevBench 2026 | Not spec-driven | Check the 2024 DevBench, which may use PRDs and UML (unopened) |
| lm-evaluation-harness | Prompt-in, text-out; no agent loop | Only if we add a single-shot condition |
| SpecBench | Reviews specs, not implements them | A different study: does the graph help find spec defects? |
| Aider Polyglot, AgentBench | From owner's file: fixed exercises; heavier custom environments | Not re-opened |

## 7. What this means for the proposal (owner chose: both, 2026-09-29)

**Decision:** the main study uses the owner's own tasks; a public benchmark adds outside validity. Platform candidates, undecided: ProjectEval, RealBench, Harbor (see §8).


- **Harness.** Inspect AI (custom datasets, model-graded and custom scorers, confidence intervals, Claude Code via Inspect SWE) or Harbor tasks with a multi-metric `reward.json` are the two workable routes. Both need our own coverage and hallucination scorers.
- **Benchmarks.** "Popular benchmarks" alone cannot test our spec formats. Options: (a) a spec-like benchmark (Doc2Feat-Bench, ProjectEval, RealBench, RepoGenesis) whose task text we re-render as flat, tiered and graph, after checking each one's licence, size and whether tasks can be swapped; (b) our own small task set packaged as Harbor or Inspect tasks; (c) both: (b) as the main study, (a) as external validity.
- **Metrics that can be reproduced without a model:** tests passed (hidden), package existence (registry lookup, per Spracklen et al.), static checks. **Metrics that need a model or a person:** omission audit, invented-requirement counting; use blind human labels with κ and LLM judges only for triage.
- **Before citing any of the papers above in the proposal:** open the full text of the ones you use.

## 8. Efficiency metrics: which platform reports them? (added 2026-09-29)

Asked: agent completion time, model cost, input/output tokens, files read/edited, failed commands, number of tries. Candidates kept **undecided, one to be picked later**: ProjectEval, RealBench, Harbor.

**What I opened:** the ProjectEval paper's full text (the PDF, read locally with `pdftotext`) and README; RealBench's arXiv HTML full text; Harbor's docs pages (overview, metrics, tasks, ATIF, job results, pre-integrated agents, run-a-job); Claude Code's docs pages on headless mode, OpenTelemetry monitoring and Agent SDK cost tracking.

| Metric | ProjectEval | RealBench | Harbor | Claude Code itself (any harness) |
|---|---|---|---|---|
| Completion time | **Not reported per run.** The paper marks tasks an agent "did not finish" (OpenHands: 6 `AgentStuckInLoopError`, 2 "Not Complete") | Not reported | **Yes:** each trial's result file holds "agent duration and timing" | `duration_api_ms` appears in the SDK docs; OpenTelemetry `claude_code.active_time.total`. `duration_ms` and turn count were **not** confirmed on the pages I opened |
| Model cost | Only **benchmark-side** costs: $2.95 to construct with GPT-4o; $28.02 to evaluate Pass@5 with GPT-4o (≈ $5.60 per round). Not a per-agent-run cost | Not reported | **Yes:** cost per trial; ATIF `cost_usd` | `total_cost_usd`, per-model `modelUsage`. **Client-side estimates**, not billing. Includes subagents |
| Input / output tokens | **No.** The `#Tokens` column is the average length of the canonical answer, a dataset statistic | Not reported (the paper mentions truncating retrieved files to fit context) | **Yes:** token counts per trial; ATIF prompt / completion / cached tokens | `usage` and `modelUsage`: input, output, cache read, cache creation. Docs warn: per-step `output_tokens` is a placeholder (read it from the result); `usage` **undercounts subagents**, use `modelUsage` |
| Files read / edited | No | No | **Not a native counter.** ATIF records every tool call (`function_name`, `arguments`) and observation, so it can be **derived** | Derivable from `tool_use` blocks in `stream-json`; OpenTelemetry `claude_code.tool_result` events, with `OTEL_LOG_TOOL_DETAILS=1` to include tool inputs; `claude_code.lines_of_code.count` |
| Failed commands | No | No | Exceptions are recorded per trial; failed commands are **derivable** from ATIF observations, not counted | `tool_result` events; `permission_denials` in the final result; `api_retry` events with `attempt` and `error` (these are **API** retries, not agent retries) |
| Number of tries | Pass@k over k regenerations (5 in the paper) | Pass@k, Completion@k, Execution@k | **Yes:** `-k` attempts per task and `-r` retries in `harbor run`; retry attempts stored per trial | One `claude -p` call is one try; we count our own repeated runs |

**Findings.**
1. **ProjectEval and RealBench are correctness benchmarks, not efficiency instruments.** Neither reports per-run time, tokens, files or failed commands. ProjectEval's only cost figures are the cost of building and judging the benchmark. RealBench evaluates plain LLM API generation strategies (holistic, incremental, retrieval-augmented), not coding agents with tools.
2. **Harbor records the most natively:** time, cost, tokens, retries and attempts, and a full trajectory (ATIF) from which files read/edited and failed commands can be counted by our own script. It lists `claude-code` among 40+ pre-integrated agents (with ATIF trajectory generation). Its docs pages did not say whether every agent reports tokens and cost; check with a first run.
3. **Every efficiency metric on your list can be taken from Claude Code's own logs,** whatever platform scores correctness: `--output-format json` and `stream-json` (cost, per-model tokens including cache tokens, tool calls, permission denials, API retries) and OpenTelemetry (token, cost, active time, lines of code, `tool_result` events). So the choice of platform mostly changes **how correctness is scored**, not whether efficiency can be measured.
4. **Not measured by anything I found:** "number of failed commands" and "files read/edited" as named, ready-made metrics. They need a small script over the tool-call log. Also uncomfortable: cost is a client-side estimate, and subagent tokens are excluded from `usage`.
5. **⚠ Subscription vs API key.** Claude Code's headless docs recommend `--bare` for scripted runs, but say bare mode does **not** use the subscription login and needs `ANTHROPIC_API_KEY`. This project's rule is never to use an API key, so studies must not use `--bare` and need another way to keep the agent's ambient configuration (CLAUDE.md, hooks, memory) out of the runs. The earlier lecture's harness sketch used `--bare`; do not copy it.

**ProjectEval extras (from the README and paper):** three input levels (natural-language prompt, checklist, code skeleton); execution judged by simulated user interaction (needs a browser driver); README licence GPL-3.0; Windows or Linux; an LLM runtime (Ollama suggested); judging is run on a named experiment folder (`run_judge.py -r`), which suggests outputs made elsewhere could be scored, **not confirmed**. GPT-4o reached Pass@5 of about 15 % in the paper.
**RealBench extras (from the arXiv HTML):** 61 Python repositories created after Dec 2024; requirements and UML given as input; Requirement@k and Architecture@k (0–4 scores using DeepWiki plus human checking, so a requirement-level score exists, but by comparing to ground-truth labels, not per-requirement omission), Completion@k, Execution@k, Pass@k; best average Pass@1 reported 19.39 %. I found no repository link or licence in the paper text ("detailed instructions are available on our website").

**Open checks before picking one:** can ProjectEval or RealBench score a project made by Claude Code in a folder, without regenerating through their own pipeline; RealBench's release and licence; Harbor's `claude-code` agent on the subscription login and the token/cost fields it writes.

## 9. Sources

Opened (arXiv abstract page unless noted), 2026-09-29: Chen et al. 2107.03374 · Jimenez et al. 2310.06770 · Liu et al. 2305.01210 · Jiang et al. 2507.18130 · Zhang et al. 2409.20550 · Zheng et al. 2306.05685 · Liu et al. 2404.00971 · Tian et al. 2405.00253 · Spracklen et al. 2406.10279 · Dasu et al. 2609.03267 · Lee et al. 2504.20799 · Ponnusamy 2502.07835 · Tambon et al. 2607.02057 · Sun et al. 2511.10271 · Crupi et al. 2507.16587 · Liu et al. 2503.07010 · Li et al. 2503.06680 · Zhou et al. 2602.10975 · Yang et al. 2605.03546 · Kumarappan et al. 2601.11895 · Li et al. 2604.22659 · RepoGenesis 2601.13943 · Repo0 2608.19854 · TraceDev 2607.18886 · WiseSpec 2609.00568 · SpecBench 2605.30314 · Sartori 2603.24284 · Grynets et al. 2608.21208 · Du et al. ClassEval 2308.01861. Docs and READMEs: Inspect (scorers, datasets, agents pages) · Harbor task overview · Terminal-Bench, EvalPlus, SWE-bench collection guide, OpenHands Benchmarks, DeepEval, BigCodeBench, lm-evaluation-harness, LiveCodeBench, SWE-bench Pro V2 README · promptfoo intro.

Snippet only, not to cite: the SonarQube/CodeQL/PMD survey result; the four-category hallucination taxonomy attributed to Lee et al.; the "DevBench uses PRDs and UML" line; TDAD SpecSuite-Core.

Not opened: HumanEval and MBPP repositories, AgentBench, Aider Polyglot, SWE-bench evaluation guide (owner's file only); the 2024 DevBench; Commit0 primary paper; Hey et al. traceability.
