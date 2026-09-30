# Notes beside the proposal (owner only, not part of the submission)

Written 2026-09-29. Companion to `project-proposal.md`.

## 1. Decisions needed from the owner (updated after your comments)

1. **Team and category** — Only 1 member: Victor Truong (student number 300264088). Approve category *Benchmark and empirical study*.
2. **Which benchmark.** Your claim says "popular AI-coding benchmarks". HumanEval and SWE-bench give one fixed task text, not a specification that exists in flat, tiered and graph form. The only setting I have opened that is spec-like is Doc2Feat-Bench (abstract only; licence, size, how to run: unchecked). Two-day trial needed before committing.
3. **Cost of the graph spec format.** Each task's spec must be compiled into a graph. The one full compile measured (845 blocks) took 2 673 calls; cost on benchmark-sized specs is to be measured.
4. **Scale.** Design values 5 tasks × 3 spec formats × 3 models × 2 reps = 90 runs, with per-run cost to be measured (Opus unknown). The backup cuts to 36 runs.
5. **Trial run** — see §2. Needs your approval.
6. **Audit load** — 20 sampled claims per run by one member; second member on an overlap.

## 2. Proposed Haiku trial (SUPERSEDED 2026-09-29: the proposal now uses the compiled graph of our own specs as its trial-run number; kept for reference, not planned)

- **What:** one Claude Haiku run through headless Claude Code on the subscription (no API key), flat spec format, one benchmark task, empty output directory.
- **One number:** share of the task's tests passed.
- **What it takes:** calls and time unknown, to be measured; a call cap is needed. TODO(owner): pick the cap.
- **Approval needed to spend** estimated API-equivalent dollars.
- Until it is run, part 6 of the proposal says "trial pending — see Risks".

## 3. Citations — what was actually opened (2026-09-29)

Each row: the arXiv abstract page (the authors' own text) was opened with WebFetch. **No full text was read.** The brief says to check every reference and to cite only what you can explain; before submission, open the PDF of each and confirm the sentence it supports.

| # | Paper | Read | Claim used in the draft |
|---|---|---|---|
| 1 | Chen et al. 2021, arXiv:2107.03374 | abstract page | HumanEval, functional correctness, pass@k |
| 2 | Jimenez et al., ICLR 2024, arXiv:2310.06770 | abstract page | 2 294 real GitHub issues, 12 repos, hidden tests |
| 3 | Liu et al., NeurIPS 2023, arXiv:2305.01210 | abstract page | ≈ 80× more tests; pass@k drops 19.3–28.9 % |
| 4 | Jiang et al., arXiv:2507.18130 (v4 retitled Doc2Feat-Bench) | abstract page | doc change + implementation + tests; agents struggle with cross-file edits. Not used: the best rate, since the number changed between versions (37.72 % in v4; the lecture had 28.07 % from an earlier version) |
| 5 | Zhang et al., ISSTA 2025, arXiv:2409.20550 | abstract page | taxonomy from six LLMs; retrieval-based mitigation |
| 6 | Liu et al., TACL 2023, arXiv:2307.03172 | abstract page | best at start/end of context, worse in the middle |
| 7 | Zheng et al., NeurIPS 2023, arXiv:2306.05685 | abstract page | position/verbosity/self-enhancement biases; > 80 % agreement |
| 8 | Miller 2024, arXiv:2411.00640 | abstract page | error bars, paired comparisons, planning an experiment. ⚠ The abstract itself does not list "paired, clustered, power"; the fetch summary only inferred them. The draft's sentence leans on the lecture's account of the paper. **Open the paper before submission.** |

Details to fix: venue and year of #6 (TACL 2023 arXiv; journal issue 2024 per the lecture) and #3's venue (page shows arXiv only; NeurIPS 2023 is from the lecture) — check the proceedings pages.

**Not counted, [UNVERIFIED — open before citing]:** Sclar et al. ICLR 2024; He et al. 2024 (arXiv:2411.10541); Hey et al. IEEE RE 2024 (only surveyed in the lecture); Cemri et al. NeurIPS 2025.

## 4. Length check (estimate until the LaTeX build)

About **2 150 words** excluding comments and references, including two tables and a code block. A NeurIPS 2026 page in 10 pt single-column holds roughly 500–600 words of prose (my estimate; not measured), so this draft is probably **3.5–4 pages: over the 2–3 limit**. Cuts, in order: the facts table (keep 3 rows), the week table into 5 lines, related work to 2–3 sentences per paper, secondary metrics.

## 5. Numbers in the draft and their sources

All from the handover's table (M4-gate §8; build-plan I-92, I-94, §9). Two counts come from my own read of the frozen pilot graph on 2026-09-29: F5 has 80 nodes, 23 of layer `V`, 3 `CT-` nodes; vision + constitution have 38 + 39 = 77 nodes. Design values (not measured): 12 runs, 3 repetitions, 20 audited nodes per run, 240 checks. Not measured and marked so: the pilot graph's span coverage, cost per agent run, calls per run.
