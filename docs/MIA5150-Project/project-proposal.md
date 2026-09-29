# MIA 5150 Project Proposal

<!-- DRAFT 2026-09-29 for owner review. Markdown first; LaTeX (NeurIPS 2026) only after approval.
     Source comments (src: …) are for the owner and are stripped at the LaTeX build.
     Every "$" figure is Claude Code's own total_cost_usd, an estimated API-equivalent, not money billed. -->

**Title (working):** Does a compiled spec graph help a coding agent implement a spec? A controlled test on a graph built from the SDD Compiler's own specs

## Team Members and Project Category

TODO(owner): member names and student numbers (not in the repo). Teams are 2–3; working alone needs the instructor's approval.
Members below are written **A** and **B** until filled in.

**Category:** Benchmark and empirical study (a controlled comparison on one task).
TODO(owner): confirm the category.

## One-Sentence Testable Claim

We claim that **a coding agent given a compiled spec graph implements more of a spec unit's requirements than the same agent given the same specs as plain Markdown**, and we will show it by measuring **requirement-node coverage** (the share of the unit's nodes that the generated code implements, audited by hand on a seeded sample) **against the same specs as plain Markdown (identical task, agent and settings)** on **one unit of the SDD Compiler's own specs (the F5 retrieval spec plus the vision and constitution), built from scratch by Claude Haiku and Claude Sonnet through Claude Code**.

<!-- All four blanks filled (claim, measuring, against, on). Owner: shorten if the LaTeX page is tight. -->

## Problem and Motivation

Spec-driven development treats specifications as the source of truth and code as downstream. The SDD Compiler (this project's artifact) turns a folder of Markdown specs into a graph of atomic requirement nodes, terms and links, so that an AI agent can check and query the specs. Its rel01 goal is that the graph is *usable for generating code*.

Nobody has yet measured that. Every number so far describes the artifact, not an agent that uses it. The compiler's own gaps are measured (see Baseline): node spans covered 54 % of the spec text, all 25 fenced contract blocks formed no node, and 0 of 1 031 terms carried a definition <!-- src: build-plan.md I-92 -->. Three fixes were built (I-92 a–c), but whether an agent builds *more of the spec* from the fixed graph than from the Markdown it replaces is unknown. If the graph does not beat plain Markdown, the compiler's central claim is not supported; a null result is still a finding, and an agent's own list of what it had to invent tells the compiler what to add.

## Related Work

<!-- Each paper was opened at its arXiv abstract page (the authors' own text) on 2026-09-29. Full text was NOT read for any of them, so every claim below is limited to what the abstract states. Details: proposal-notes.md §3. -->

**Code-generation scoring.** Chen et al. (2021) introduce HumanEval and the *pass@k* metric for functional correctness on short function-writing tasks. Jimenez et al. (ICLR 2024) score whole-repository edits by hidden tests on 2 294 real GitHub issues (SWE-bench). Both score *does the code pass tests*. Neither asks *how much of a written specification was implemented*; we score coverage per requirement node, and use tests only as a secondary check.

**Weak tests hide errors.** Liu et al. (NeurIPS 2023, EvalPlus) add about 80× more tests to HumanEval and report pass@k falling by 19.3–28.9 %. This is why we do not trust the agent's own tests as our primary score and audit coverage independently.

**Nearest setting to ours.** Doc2Feat-Bench (Jiang et al., arXiv 2025; earlier titled NoCode-bench) pairs a *documentation change* with the implementation and developer tests, and reports that agents struggle with cross-file edits and with "interpreting documentation semantics". It fixes the documentation format and varies the agent; we fix the agent and vary how the specification is represented (Markdown vs compiled graph).

**Hallucination in generated code.** Zhang et al. (ISSTA 2025) build a hallucination taxonomy from six LLMs and propose retrieval-based mitigation. We do not re-derive a taxonomy; we count one narrow kind, *invented requirements*, that the agent itself lists where the graph is silent.

**Context position.** Liu et al. (TACL 2023, *Lost in the Middle*) show that models use information at the start and end of a long input better than the middle. This motivates giving an agent a graph it can read node by node instead of a long file, and is why arm M fixes the order of the Markdown files.

**Judging and statistics.** Zheng et al. (NeurIPS 2023) document position, verbosity and self-preference biases of LLM judges, with over 80 % agreement with human preferences for strong judges; so LLM judging is used only for triage, calibrated against human labels. Miller (2024) argues evals should report error bars, paired comparisons and planned power; we use paired comparisons over the same requirement nodes.

## Proposed Approach

### Models

Claude Haiku and Claude Sonnet, driven headlessly by Claude Code on the owner's subscription (never an API key). Model id, effort and Claude Code version are recorded per run. No local or open-weights model, hence no GPU.

### Data and Tasks

**Study artifact.** The frozen pilot graph `~/sddc-runs/pilot-graph-R000023/`, read-only, built by commit `acdada8`, manifest sha256 `21376ada…19605e2c` <!-- src: build-plan.md §9 (2026-09-29 note) -->. It holds 933 nodes, 25 contract nodes, 11 defined terms and 380 open conflicts <!-- src: build-plan.md I-94 -->.

**Task.** *Build from scratch, in an empty directory, the code that the unit's specs require.* The **unit** is the F5 retrieval spec (80 nodes: 23 verification nodes, 3 contracts) plus the vision and constitution (77 nodes: purpose, stack, rules) <!-- src: node counts by source.file, computed on the frozen graph 2026-09-29 -->. One unit keeps a run small enough to repeat.

**Which artifact the agents read.** The raw `.sdd/` files the README's "For AI agents" section describes (nodes, terms, edges, conflicts), **not** the agent export `sddc export` (spec F7, milestone M6), which is not built <!-- src: build-plan.md §9 -->. The prompt is the README's, unchanged, and forbids reading the specs, `blocks.jsonl`, or any existing implementation.

### Experimental Variables

- **Varied — representation (arm):**
  **G** the compiled graph (the README prompt);
  **M** the same unit's Markdown spec files, in a fixed order, with a matching prompt.
- **Varied — agent:** Haiku, Sonnet.
- **Held fixed:** the task text (apart from one line naming where the specs are), the tool list and permission mode, an empty output directory, model id and effort, and the turn cap.
- **Repetitions:** 3 per (arm, agent) as the design value; the trial run and pilot variance may change it (Miller: choose from pilot variance).
- **Known confound:** the graph does not carry everything the Markdown does. In the earlier R18 graph, node spans covered 54 % of the spec text <!-- src: build-plan.md I-92 -->; the pilot graph's coverage is *to be measured*. We therefore measure coverage against **the node list** (what the compiler claims to hold), and report separately, as a second table, how much of the Markdown's own requirements have no node. Content parity between the arms is checked with a script before any run.

## Baseline and Trial-Run Result

**Trial pending — see Risks.** No agent has yet generated code from the graph, so there is no measured baseline for the study question. TODO(owner): approve the trial in `proposal-notes.md` §2 (one Haiku run, arm G, unit F5 + foundation, one number). The number will be the count of the unit's non-verification nodes that the generated code implements, out of the unit's node total, judged against the node list.

**What is measured about the artifact** (not about agents):

| Fact | Value | Source |
|---|---|---|
| Full compile of this repo's specs (R18) | 845 blocks → 950 nodes; 2 673 model calls; ≈ $54.94 est. API-equivalent; 9.05 h | M4-gate.md §8 |
| Per-call average | $54.94 / 2 673 ≈ $0.0206 (derived) | M4-gate.md §8 |
| Conflicts | 381 open; 1 judged real (Claude's reading, owner confirms) | M4-gate.md §8 |
| Gaps of the R18 graph for code generation | spans 54 %; 183 of 845 blocks form no node; 25 of 25 contract blocks absent; 0 of 1 031 terms defined; 39 nodes leaked from Traceability tables | build-plan.md I-92 |
| After the I-92 fixes (pilot graph) | 933 nodes; 25 contract nodes; 11 defined terms; 8 blocks still fail every retry | build-plan.md I-94, §9 |

The compile is not a cost of this study: the graph is already frozen and every run reads it.

## Evaluation Plan and Metrics

**Primary metric: requirement-node coverage** = (unit nodes whose requirement is implemented by the generated code) ÷ (unit nodes, minus verification nodes). Reproducible scoring:

1. **Automatic:** a script lists the agent's `# spec: <node id>` markers and `TRACEABILITY.md` claims, checks every id exists, and lists nodes with no claim. This gives the *claimed* coverage and the omissions.
2. **Audit:** a seeded random sample of 20 claimed nodes per run (seed recorded before drawing) is checked against the code by A, with a written rubric (*implemented / partial / absent*). B audits an overlapping subset; report Cohen's κ. Audits are blind to arm.
3. LLM judging, if used, is triage only, calibrated against the human labels.

**Secondary metrics:**
- **Contract conformance:** for each `CT-` node, does the code's output validate against the contract's verbatim JSON/YAML (automatic).
- **Own-test pass rate:** the agent's tests for the unit's verification nodes, run by us; reported with the caution that the same agent wrote them (EvalPlus).
- **Invented list:** items in `OPEN_QUESTIONS.md` under *Invented*, and items we find invented that the agent did not list.
- **Effort:** model calls, tokens, and estimated API-equivalent dollars per run, from the Claude Code JSON output.

**Statistics (fixed before running):** paired by requirement node across arms; per-node outcomes are clustered by run, so we report run-clustered bootstrap confidence intervals over all runs. Nothing is dropped after the fact; every run is reported, failures included.

## Compute Budget

**GPU: none.** All models are hosted; no local model runs, so the brief's 15 GB / 20 GPU-hour limits do not bind. We budget model calls and estimated API-equivalent dollars instead, and the subscription's session limit.

```
runs        = arms × agents × repetitions = 2 × 2 × 3 = 12          (design values)
model calls = runs × calls per run          calls per run: TO BE MEASURED in the trial
est. $      = runs × $ per run              $ per run:     TO BE MEASURED in the trial
```

Graph compiles: 0 (frozen). Audits: human time, 12 runs × 20 nodes = 240 node checks for A, about 60 for B (design values).
The compile's $0.0206 per call is **not** a usable per-run figure: a compile call answers one short question, an agent run makes many long calls. A per-agent cost for Sonnet is to be measured. The trial (one Haiku run) gives the first per-run figure; if 12 runs would exceed the session limit, the plan shrinks (see Risks).

## Week-by-Week Plan

Dates from the course schedule. Names **A** and **B** are placeholders. TODO(owner): assign real names and confirm the split.

| Week | Dates | Task | Who |
|---|---|---|---|
| 4 | to 2 Oct | Proposal; approve the trial | A, B |
| 5 | 5–9 Oct | Run the trial (1 Haiku run, arm G); read every output; fix harness | A |
| 5 | 5–9 Oct | Build arm M files and the content-parity script; write the audit rubric | B |
| 6 | 12–16 Oct | Pilot: 1 run per arm per agent; measure calls and $ per run; fix reps and cap | A, B |
| 7–8 | 19–30 Oct | Main runs, interleaved across days; run the scoring script after each | A |
| 7–8 | 19–30 Oct | Blind audits of the samples; κ on the overlap | B (A on the overlap) |
| 9 | 2–6 Nov | Analysis; **check-in 6 Nov** | A, B |
| 10 | 9–13 Nov | Gap list and invented list; second table (Markdown requirements without a node) | B |
| 11 | 16–20 Nov | Draft report; presentation slides | A, B |
| 12 | 23–27 Nov | Rehearse; **presentation 27 Nov** (or 4 Dec) | A, B |
| 13 | 30 Nov–4 Dec | Final report (6 pages), README with seeds and how to reproduce | A, B |

## Risks and Smaller Backup Project

- **Trial pending.** No baseline number exists; the trial is the first agent run on the graph. If it fails outright (for example the agent cannot read the graph layout), that is the finding and the plan drops to the backup.
- **Subscription limit.** Compile rounds hit the session limit 5 times in 16 rounds <!-- src: M4-gate.md §8 -->. Agent runs may too; the plan interleaves arms and keeps a call cap per run.
- **Graph gaps confound the comparison.** Handled by scoring against the node list and reporting the Markdown-only requirements separately.
- **Variance.** Runs are stochastic; 3 repetitions may be too few. Reported as intervals; a null result is valid.
- **Agent export not built (F7).** The study reads raw `.sdd/` files; the result says nothing about the future export.
- **Audit load.** 240 node checks is the design value; the sample size may drop to 10 per run.
- **Judge noise.** Audits are human first; κ reported.

**Smaller backup:** Haiku only, arm G only, F5 alone, 3 runs: a descriptive study of what the agent builds and what it invents from the graph, compared with the compiler's measured gap list. No comparison arm, no Sonnet.

## References

<!-- All eight: arXiv abstract page opened 2026-09-29; full text not read. Author lists as printed on the page. -->

1. M. Chen, J. Tworek, H. Jun, Q. Yuan, H. Ponde de Oliveira Pinto, J. Kaplan, et al. *Evaluating Large Language Models Trained on Code.* arXiv:2107.03374, 2021. https://arxiv.org/abs/2107.03374
2. C. E. Jimenez, J. Yang, A. Wettig, S. Yao, K. Pei, O. Press, K. Narasimhan. *SWE-bench: Can Language Models Resolve Real-World GitHub Issues?* ICLR 2024. https://arxiv.org/abs/2310.06770
3. J. Liu, C. S. Xia, Y. Wang, L. Zhang. *Is Your Code Generated by ChatGPT Really Correct? Rigorous Evaluation of Large Language Models for Code Generation.* NeurIPS 2023. https://arxiv.org/abs/2305.01210
4. Z. Jiang, L. Deng, J. Cao, M. Pradel, Z. Liu. *Doc2Feat-Bench: Evaluating Documentation-Driven Feature Addition* (earlier: NoCode-bench). arXiv:2507.18130, 2025. https://arxiv.org/abs/2507.18130
5. Z. Zhang, Y. Wang, C. Wang, J. Chen, Z. Zheng. *LLM Hallucinations in Practical Code Generation: Phenomena, Mechanism, and Mitigation.* ISSTA 2025. https://arxiv.org/abs/2409.20550
6. N. F. Liu, K. Lin, J. Hewitt, A. Paranjape, M. Bevilacqua, F. Petroni, P. Liang. *Lost in the Middle: How Language Models Use Long Contexts.* TACL, 2023. https://arxiv.org/abs/2307.03172
7. L. Zheng, W.-L. Chiang, Y. Sheng, S. Zhuang, Z. Wu, Y. Zhuang, Z. Lin, Z. Li, D. Li, E. P. Xing, H. Zhang, J. E. Gonzalez, I. Stoica. *Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena.* NeurIPS 2023 Datasets and Benchmarks. https://arxiv.org/abs/2306.05685
8. E. Miller. *Adding Error Bars to Evals: A Statistical Approach to Language Model Evaluations.* arXiv:2411.00640, 2024. https://arxiv.org/abs/2411.00640

<!-- Not counted, [UNVERIFIED — open before citing]: Sclar et al. ICLR 2024 (prompt-format sensitivity); He et al. 2024 (arXiv:2411.10541); Hey et al. IEEE RE 2024 (traceability link recovery, only surveyed); Cemri et al. NeurIPS 2025 (MAST). -->
