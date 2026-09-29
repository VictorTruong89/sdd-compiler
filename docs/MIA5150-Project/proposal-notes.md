# Notes beside the proposal (owner only, not part of the submission)

Written 2026-09-29. Companion to `project-proposal.md`.

## 1. Decisions needed from the owner

1. **Team and category** — names, student numbers, 2–3 members (or instructor approval to work alone). Category drafted as *Benchmark and empirical study*.
2. **Framing** — drafted as framing B: graph (G) vs the same unit as Markdown (M), Haiku and Sonnet, 3 repetitions. Say if you prefer a single-arm study (the backup) or a third arm.
3. **Which artifact the agents read** — drafted as the raw `.sdd/` files of the frozen pilot graph (F7 `sddc export` is not built). ⚠ The pilot graph directory has `nodes/`, `terms.jsonl` … at its top level, not under `.sdd/`; the README prompt says `<BUILD>/.sdd/…`. The prompt paths need adapting, or the graph must be copied into a `.sdd/` folder. Not done, since the graph is read-only.
4. **The unit** — drafted as F5 (80 nodes: 23 `V`, 3 `CT-`) + vision + constitution (77 nodes). Alternative: F4 (114 nodes) or F1 (108). F5 is the smallest spec.
5. **Trial run** — see §2. Needs your approval.
6. **Scoring** — human audit of a seeded sample of 20 nodes per run; B second-audits. Confirm you accept the audit load (240 checks for A).

## 2. Proposed trial (not run)

- **What:** one Claude Haiku run through headless Claude Code on the owner's subscription (no API key), arm G, unit F5 + vision + constitution, README "For AI agents" prompt, empty output directory outside the repo.
- **One number:** of the unit's non-verification nodes, how many the generated code implements, judged against the node list (claimed coverage from the agent's `TRACEABILITY.md`, plus a hand audit of a seeded sample).
- **What it takes:** number of model calls and time — *unknown, to be measured by this trial*; a call cap is needed. TODO(owner): pick the cap and the session-limit tolerance (compile rounds hit the limit 5 times in 16; M4-gate §8). Roughly 1 run, one sitting, plus about 1–2 h of your reading time for the audit (estimate, not measured).
- **Approval needed to spend** estimated API-equivalent dollars; the per-run figure is to be measured.
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
