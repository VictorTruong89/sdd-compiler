# Handover — draft the MIA 5150 project proposal

> Written 2026-09-29 for a new Claude Code session. Paste the prompt below, or say
> "run the prompt inside `docs/MIA5150-Project/HANDOVER_proposal.md`".
> **Deadline: Friday 2 October 2026** (PDF, NeurIPS 2026 LaTeX template). Late work loses 5 % at once.

---

## Prompt

You are drafting the MIA 5150 (uOttawa, Fall 2026) course-project proposal for the owner of this
repository, `~/Workspace/sdd-compiler`. The proposal is a **Markdown draft for review**, converted to
LaTeX (NeurIPS 2026 template) only after the owner approves it. Write it at
**`docs/MIA5150-Project/project-proposal.md`**; overwrite that file (it holds only a heading skeleton).

### 1. Read first, in this order

1. `docs/MIA5150-Project/MIA5150_Project_Brief.pdf` — the rules (2 pages). Authoritative.
2. `docs/lectures/lecture-agent-reads-spec-graph.html` — design input for how an agent reads the graph.
3. `docs/lectures/lecture-tiered-md-vs-graph.html`, Parts 6–10 — an **earlier** study design.
4. `README.md`, section "For AI agents" — how an agent is told to build code from the graph alone,
   and the measured gaps of the graph.
5. `sdd/design/rel01_design/M4-gate.md` §3, §5, §7, §8 and `sdd/design/rel01_design/build-plan.md`
   §8 rows I-92, I-93, I-94 and §9 — where every number below comes from.
6. `CLAUDE.md` — house rules (below they are repeated where they bind this task).

### 2. What the proposal must contain (brief, page 2)

2–3 pages, references not counted. Keep the ten parts, in the brief's order, under the headings
already in `project-proposal.md`:

1. Team members, student numbers, category — **owner input**: names and numbers are not in the repo.
   Teams are 2–3; working alone needs the instructor's approval. Category: likely *Benchmark and
   empirical study* (framing B is a controlled comparison) — confirm with the owner.
2. One-sentence claim with **all four blanks**: *We claim that [claim], and we will show it by
   measuring [measurement] against [comparison] on [task/data].*
3. Problem and why it matters.
4. Related work: **5–8 papers, positioned** (what each does, and how this project differs).
5. Approach: models, data, what is varied.
6. **Baseline and trial-run number** — see §5 below: this number does not exist yet.
7. Evaluation plan: name the metrics, and how each is scored reproducibly.
8. Compute budget, **with the arithmetic**.
9. Week-by-week plan, with **names on tasks**.
10. Risks, and a smaller backup project.

Marked on: feasibility 30 %, question and framing 25 %, literature 20 %, evaluation plan 15 %,
writing 10 %. A proposal that cannot be finished with the compute and time is **returned for
revision** (resubmit within a week, capped at 80 %) — feasibility is the heaviest weight.

### 3. Measured facts you may use — every one has a source; use no other numbers

State the source file beside each number you use in the draft (a comment or footnote), so the owner
can check it. Every `$` figure is **"estimated API-equivalent"** — Claude Code's own `total_cost_usd`
summed per call on the owner's subscription, not money billed (build-plan I-82). Never write "cost"
or "spend" without that label.

| Fact | Value | Source |
|---|---|---|
| Full compile of this repo's specs (R18) | 845 blocks → 950 nodes; 381 open conflicts; 2 673 model calls; ≈ $54.94 est. API-equivalent; 9.05 h compile time | `M4-gate.md` §8 |
| Per-call average, R18 | $54.94 / 2 673 ≈ $0.0206 (derived — show the division) | `M4-gate.md` §8 |
| Conflict precision, full corpus (Claude's reading, owner confirms) | 1 of 381 judged real; 0 of a seeded 100-sample | `M4-gate.md` §8 |
| Conflict precision, dogfood (2 specs, 181 blocks) | 4 real of a 39-record sample (≈ 10 %) | `M4-gate.md` §7 |
| Planted fixture (28 blocks, 6 planted conflicts) | first gate: recall 1 of 6, precision 3 of 11; R17 re-run: recall 2 of 6, precision 5 of 7 | `M4-gate.md` §3–§5 |
| What the R18 graph lacked for code generation | node spans cover 54 % of spec text; 183 of 845 blocks form no node; all 25 fenced contract blocks absent; 0 of 1 031 terms defined; 39 nodes leaked from Traceability tables | `build-plan.md` I-92 |
| After the I-92 fixes (pilot graph, below) | 933 nodes, 25 contract nodes, 11 defined terms, 380 open conflicts; 8 blocks still fail every retry | `build-plan.md` I-94, §9 |
| Conflicts found once contracts became nodes | 2 of 19 judged real | `build-plan.md` I-94 |
| Cost of the I-92 runs | 834 calls, ≈ $15.12 est. API-equivalent | `build-plan.md` I-94 |

Not measured, and must be written as *to be measured* if used: node-span coverage of the pilot graph;
any quality of code generated from the graph; any per-agent cost other than Haiku's.

**The frozen pilot graph** (the study artifact for framing B): `~/sddc-runs/pilot-graph-R000023/`,
read-only, specs beside it in `pilot-graph-R000023-specs/`, file manifest
`~/sddc-runs/pilot-graph-R000023.sha256` (itself sha256 `21376ada2faf8539cbd6bea2842c8ace2922578208217363906818fc19605e2c`),
built by commit `acdada8`. Every study run reads this graph until a new one is frozen deliberately.

### 4. The trial-run number — the proposal's biggest gap

The brief says: before the proposal, run the simplest baseline and **put one number in the
proposal**. For framing B that number is an agent's output on the graph, and **no agent has yet
generated code from the graph**. The compiler numbers above are about the artifact, not about agents.

Do not invent one. Do this instead:
1. Propose to the owner the **smallest honest trial**: one agent (Claude Haiku through headless
   Claude Code, the owner's subscription — never an API key) given the README's "For AI agents"
   prompt on **one small unit** of the pilot graph (one spec's family or section), and **one number**
   out of it (for example, how many of the unit's requirement nodes the generated code implements,
   judged against the node list). Say what it would take: number of calls, time, and the owner's
   approval to spend.
2. Only after the owner approves, run it, and report exactly what came out — including failure.
3. Until then, the draft says **"trial pending — see Risks"** in part 6. Never a placeholder number.

### 5. Compute budget — frame it for this project

The brief budgets **GPU-hours** (≈ 15 GB per job, ≤ ≈ 20 GPU-hours total). This project runs hosted
models (Claude through Claude Code), so it needs **no GPU**: say so, and budget in **model calls and
estimated API-equivalent dollars** instead, with the arithmetic from the facts in §4 (calls per
graph compile, calls per agent run × runs × agents). A per-agent cost for Sonnet or Opus is **to be
measured**. If the design needs local models (to meet the brief's "generative/foundation models" or
to vary open models), check them against the brief's hardware limits.

### 6. Related work — the citation rule

The course treats **a made-up citation, an invented number, or a method you cannot explain as
academic fraud**, whatever produced it (brief page 2). So:

- Cite a paper **only after opening its primary source** (the paper itself, not a summary or a
  search snippet) — use WebSearch/WebFetch. Record title, authors, venue/year and URL as read.
- Anything not yet opened is marked **[UNVERIFIED — open before citing]** and never counted in the
  5–8.
- Directions to search (topics, not citations): LLM code-generation benchmarks and their scoring;
  hallucination in LLM-generated code; requirements coverage / traceability for generated code;
  spec-driven or specification-guided code generation; comparisons of coding agents; LLM-as-judge
  reliability (if outputs are judged by a model).
- Position each paper: what it measures, and what this project measures that it does not.

### 7. Plan dates you already know

Proposal 2 Oct (week 4) · progress check-in 6 Nov (week 9, no marks) · presentations 27 Nov / 4 Dec
(weeks 12–13) · final report 4 Dec (6 pages, NeurIPS template, code link with a reproducing README
and seeds). rel01 of the compiler **slipped** (rel01 D35): it closes when the first graph is usable for
generating code, and the agent export (spec F7, `sddc export`, build-plan M6) is **not built** — a
dependency and a risk for framing B if the agents are meant to read the export rather than the raw
`.sdd/` files the README describes. Say which the study uses.

### 8. House rules that bind this task

- Write only `docs/MIA5150-Project/project-proposal.md` (and, if useful, notes beside it in that
  folder). **Do not edit** `sdd/specs/**`, `src/`, `tests/`, or the frozen pilot graph.
- **Never mention the course in `sdd/specs/vision.md`** (owner's decision).
- **Never run `git add`, `commit` or `push`.** The owner commits.
- **Never set `ANTHROPIC_API_KEY`** or switch backends; any model run uses the owner's Claude Code
  subscription, and only with the owner's approval.
- No invented numbers: measured, or marked *to be measured*.

### 9. Finish with

1. The draft at `docs/MIA5150-Project/project-proposal.md`, all ten parts present, owner inputs
   marked `TODO(owner): …`, unverified citations marked as such.
2. A rough length check against 2–3 NeurIPS pages (state it is an estimate until the LaTeX build).
3. A short list for the owner: decisions needed (framing, team, category, trial run, which artifact
   the agents read), and citations still to verify.
