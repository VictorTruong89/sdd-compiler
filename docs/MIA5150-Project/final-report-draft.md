# Flags, not graphs: what helps an AI coding agent with a self-contradicting specification

> **Final report draft** (MIA 5150, due 4 Dec 2026; 6 pages max in NeurIPS LaTeX, not counting references
> and the contributions appendix). Opened 2026-11-09 by Claude Code for the owner, from the interim
> report (`interim-report.md`, its §4 tables are the figures' source) and the trial records under
> `harness/trials/`. Working Markdown, to be moved into the proposal's LaTeX template
> (`project-proposal/latex/`, same `references.bib`). **Every number is copied from a named trial
> record; none is new here.** Citations use the keys of `references.bib` (checked 2026-09-29);
> `[cite: …]` marks a source that is not yet in the `.bib` and must be opened before it is cited.
> Rounds 24–26 (9–10 November) are filled in from their `TRIAL.md` files (2026-11-10). Round 27 (compiler
> export on case006 and case010, 10–11 November) filled in 2026-11-11 from its `TRIAL.md`; §3.6 recomputed with it.
> **2026-11-17: round 28 (three new cases, case005 / case011 / case001, 96 runs) and round 27b (16 Haiku
> top-up runs on case006 and case010) filled in**, from each case's `notes/tables.json`, round 28's reviews
> `TRIAL.md`, `stats/power_plan.py` (K = 6; `power_plan.json`, and `power_plan_topup.json` with round 27b)
> and round 26's `reader2.py table` (rounds 18–28). Main tables keep n = 3 on case006 and case010; the n = 5
> figures with round 27b are given beside them in the text. Length target: about 3 300 words of text, 3 tables, 1 figure.

## Abstract

Spec-driven development gives an AI coding agent a written specification instead of a chat. Real
specifications drift: two documents, or two paragraphs, say different things. We built a compiler,
`sddc`, that turns a folder of Markdown specifications into a graph of quoted requirements and reports
each pair it judges contradictory, and asked whether an agent builds better software from the
compiled form. In controlled runs of Claude Code (Claude Haiku and Sonnet) on six public Zero2Repo
cases (4 800–19 000 words, 197–476 hidden tests) with 12–24 contradictions planted from an answer key
written before any run, **the compiled form did not raise hidden-test scores**: over the six cases no
arm's core score differed from the Markdown's by a margin we could detect, and every arm passed a
non-inferiority bound (2 points for Sonnet, 5 for Haiku). What changed was **whether the agent noticed and
reported the contradictions**: with every planted conflict flagged, naming rose in all six cases for both
models (by 13–64 points; t-test over cases p ≤ 0.007, sign test p = 0.031). The gain followed the flags item
by item, and **a one-pass LLM review supplied better flags than the compiler** (recall 90–91 % against
57 % of 100 planted conflicts, precision 93–99 % against 28 %, for cents instead of dollars). Handing that
review list to the agent beside the plain Markdown raised naming in all six cases (t-test p ≤ 0.012), and
nearly every listed conflict was named (518 of 530 readings on the five cases with a listed-item count). With its false entries struck and a ruling on each entry, the
list carried the rulings into the code (118 of 120 built). No format changed silent invention of facts we
removed from the specification (every arm within ±2 gaps per run of the Markdown, equivalence shown on 4–5
cases with gaps). We conclude that for specifications that fit one context, the useful artefact is a short,
checked list of conflicts with rulings, not a graph.

## 1 Introduction

*(≈ 0.6 page.)* Coding agents now build whole repositories from documents [cite: Zero2Repo]
\citep{chen2026repo0,peng2026repogenesis}. Spec-driven development makes the documents the source
of truth; but a product requirements document (PRD) and an interface contract written by different
people, or revised at different times, contradict each other, and an agent that does not notice
builds one side silently. Our proposal claimed that *an agent produces code of higher quality from a
structured, graph-based specification than from the same specification as flat files*. We built the
graph (§3.2), and tested the claim under tight controls.

The claim as proposed is **not supported**, and the experiments say what to do instead. Our
contributions:

1. A controlled benchmark design for specification conflicts and gaps: contradictions and removed facts
   planted into public Zero2Repo specifications, each chosen so that a black-box probe tells which
   side was built and at most three hidden tests depend on it, with the answer key written before any
   model call (§3.3).
2. Evidence on six cases and two models that a compiled graph does not change hidden-test scores,
   while **flagged** conflicts are named far more often, and only the flagged ones (§4.1–4.2).
3. A baseline the literature and our proposal lacked: a plain LLM review is a better and cheaper
   conflict detector than the compiler on these specifications, and its list carries the same help to
   the coding agent (§4.3–4.4).
4. A negative result on hallucination: no format makes an agent say that the specification is silent
   (§4.5).

*(Draft note, owner 2026-11-10: the four claims are agreed. Each is tested at the case level with the
sample size of §3.6. 2026-11-17, with all 6 cases: claims 2 and 3 pass the t-test over cases and the
oracle export and review list also pass the sign test (all 6 cases positive, p = 0.031); the compiler
export's naming gain passes the t-test but not the sign test (case005 −1.2 / −3.9). The nuance on Haiku's
core seen on the first 3 cases (+2.1–4.4 points with any flag source) **did not repeat**: on the 3 new
cases Haiku's core was 99.6–100 % in every arm, so the gain over 6 cases is not significant (p = 0.10–0.47).
Round 27b's top-up Markdown runs on case006 scored higher than round 18's (§4.1), which also points to time
or chance for the old case006 gap. Reader 2 has read every run of rounds 18–28.)*

## 2 Related work

*(≈ 0.5 page. Keep 6–8 citations; all below are in `references.bib`.)*

**Repository-level generation from documents.** SWE-bench \citep{jimenez2024swebench} and SWE-agent
\citep{yang2024sweagent} evaluate edits to existing code; ProjectEval \citep{liu2025projecteval},
DevBench \citep{kumarappan2026devbench}, RepoGenesis \citep{peng2026repogenesis} and Repo0
\citep{chen2026repo0} build projects from descriptions. Zero2Repo [cite: Zero2Repo] gives a PRD and an
interface contract per case and scores the build with hidden tests; we use it because its tests are
written against a stated contract. None of these plants contradictions in the specification.
**Requirements to code.** TraceDev \citep{chen2026tracedev} and WiseSpec \citep{tian2026wisespec} use
requirements traceability inside multi-agent pipelines; we instead test whether a compiled
specification helps an off-the-shelf agent. **Hallucination in code.** Taxonomies
\citep{liu2024halucode,zhang2025hallucination,lee2025hallucination} include code that contradicts or
goes beyond the requirements; we measure the second kind as *silent invention* of facts removed from
the specification. **Context and format.** Long inputs degrade reasoning \citep{liu2024lost,levy2024moretokens},
and prompt format alone moves scores \citep{he2024format,sclar2024format}; our export is 3–6× the
Markdown's length, so format effects are a live confound (§6). GraphRAG \citep{edge2024graphrag}
motivated the graph. **Evaluation.** We test each claim over cases (t-test, sign test, non-inferiority and equivalence bounds) and report counts and ranges, following
\citet{miller2024errorbars} on small-n evals, and use an LLM second reader with agreement reported, as
LLM-as-judge work advises \citep{zheng2023judge,crupi2025judge}.

## 3 Method

### 3.1 Platform

*(≈ 0.3 page.)* Claude Code 2.1.316, run headless by Harbor 0.24.0 \citep{harbor_docs} in a Docker
container with tools `Bash`, `Edit`, `Read`, `Write`, no dollar ceiling, and a 7 200 s agent limit.
The agent's container holds only the specification; hidden tests are copied in after it stops. Coding
agents: `claude-haiku-5-5` and `claude-sonnet-5-5`. Each condition is one frozen Harbor task, and the
arms of a round differ only in the specification folder and one instruction sentence (`diff -r`
checked). A driver runs each round's queue unattended in a fixed interleaved order and reruns, once,
a run cut off by a usage limit or stopped early by an output-limit cut (a rule written before any
run). One instruction line, identical in all arms, asks the agent to list each disagreement it finds
in `NOTES.md`, stating both sides, and each point the specification does not state.

### 3.2 The compiler and its export

*(≈ 0.3 page; Figure 1 = the pipeline.)* `sddc` splits each Markdown file into blocks, asks Claude
Haiku which claims each block makes (every quote is checked word for word against the source), picks
candidate pairs by fixed rules, and asks Haiku, 8 pairs per call, whether two claims duplicate or
contradict. A person then marks false alarms and may record rulings. `sddc export` writes a map, a
checklist of every claim id and one *pack* per area: the original text, its claims, and each open
conflict with both sides quoted. The compiler uses Haiku only.

### 3.2.1 Why a compiler and not retrieval (RAG)

*(Proposed 2026-11-17, owner to review. ≈ 0.3 page. A design argument from the rel01 design notes
(`sdd/archive/rel-01/design/rel01_design/core-working-principle.md` §4.3, §10–11) and the vision (O1, O2);
no RAG baseline was run, §6 item 11.)* A retrieval-augmented system [cite: Lewis et al. 2020, RAG] splits
the documents into chunks, embeds them, and gives the model the k chunks most similar to a query. GraphRAG
\citep{edge2024graphrag} adds an entity graph and community summaries for questions about a whole corpus. We
built a compiler instead, for four reasons.

1. **Conflict detection has no query.** Retrieval ranks chunks against a question and returns the best few.
   A contradiction check must compare every claim with every other claim on the same subject, and a pair
   it never compares fails silently. The compiler extracts every claim with a quote checked word for word,
   picks candidate pairs by fixed rules over all claims. So which pairs were compared is set by rules a
   person can read, and a miss can be traced to a rule.
2. **Similarity is the wrong signal.** Embeddings measure whether two passages read alike. A conflict is
   two statements about the same subject that disagree, and they need not read alike. The design notes'
   example: similarity groups an *upload size limit* with a *download rate limit*, but separates a
   *share-link expiry* rule from the *expiry timestamp* field. In our cases side B is written in the
   specification's own voice, often in another file (30 of 71 planted pairs on case006, case010, case005
   and case001); what ties it to side A is its subject, not its wording.
3. **Building code needs the whole specification, with proof of completeness.** An agent that builds a
   repository must implement every requirement, not the k most relevant to some question; a chunk left
   out becomes a missing feature. The export hands over all the text plus a checklist of every claim id
   and each open conflict with both quotes, so what the agent was given can be audited. A retriever adds
   a ranking step that the author cannot audit.
4. **Rulings need a stable home.** Each claim keeps its source quote and id, and a person's ruling is
   attached to a conflict id and survives a rebuild. The compiler's code is deterministic, and the model
   only answers narrow, schema-bound questions (vision O2). A RAG index stores chunks, not claims or
   verdicts.

The results narrow this argument. Our specifications fit one context (4 800–19 000 words), so no
selection step was needed at all: a plain one-pass review read everything and found more conflicts than
the compiler (§4.3). Retrieval and the compiler's incremental design both aim at specifications larger
than one context, and that case is untested (§6 item 7).

### 3.3 Planted conflicts and gaps

*(≈ 0.5 page; Table 1 = the cases.)* No public benchmark ships self-contradicting specifications, so
we planted them. For each case an answer key was written before any compile or run. A **conflict**
keeps the original sentence (side A, what the hidden tests check) and adds one sentence elsewhere in
the specification's own voice that says otherwise (side B). Each item must (i) be built in earlier
unplanted runs, (ii) be readable by a black-box probe on the saved code, and (iii) change at most
three hidden tests between sides, measured with no model by patching a reference build to each side.
A **gap** removes every statement of a fact the tests still check, with no marker. The tests touched
by any item (the *footprint*) are left out of the **core score**, because they reward side A whether
or not the agent noticed; the specification does not say A is right.

| Case (library) | Words | Tests | Conflicts | Gaps | Core | Rounds |
|---|---|---|---|---|---|---|
| case006 (`click`) | 14 435 | 476 | 24 | — | 445 | 18, 25, 27 |
| case010 (`nltk`) | 8 412 | 197 | 15 | 14 (round 20) | 173 / 175 | 19, 20, 25, 27 |
| case016 (`sloptrim`) | 18 845 | 388 | 17 | 15 | 338 | 21, 23, 24 |
| case005 (`h11`) | 7 916 | 395 | 17 | 11 | 335 | 28 |
| case011 (`jmespath`) | 6 909 | 321 | 12 | 12 | 271 | 28 |
| case001 (`tomli`) | 4 801 | 302 | 15 | 4 | 265 | 28 |

Round 28 planted the three new cases with the same rules and wrote each answer key on 11 November, before
any compile, review or agent run; all four arms ran on each, interleaved, 5 Haiku and 3 Sonnet runs per arm.

### 3.4 Arms

- **Markdown:** the planted specification as given.
- **Compiler export:** `sddc export` of the planted specification, false contradictions removed by
  verdicts, nothing added.
- **Oracle export:** the compiler export plus the planted conflicts it missed, injected from the
  answer key: an upper bound for a perfect compiler.
- **Review list:** the Markdown plus `CONFLICTS.md` from one plain LLM review of the same Markdown
  (§4.3), unfiltered, chosen by a fixed rule (the first Haiku review of the case).
- **Settled list** (case016): the review list with its false entries struck and a ruling added to each
  entry; the planted side B is ruled on alternate entries so that following the ruling can be told
  from default behaviour.

### 3.5 Measures and readers

**Set 1, core:** hidden tests passed outside the footprint. **Set 2a, named:** under a strict rule
fixed before the runs, `NOTES.md` states the content of both sides and presents them as a choice; an
id or topic alone does not count. **Set 2b, silent inventions:** gaps whose value the code takes while
the notes do not name it as unstated. **Built side:** the probe's reading. Cost is Claude Code's
`total_cost_usd`, an API-price estimate (the runs used a subscription). Reader 1 (the assistant in Claude Code)
read every `NOTES.md` item by item, not blind to arm. **Reader 2** (Claude Sonnet, no tools, a
fresh context per run) read the same files under the same rule, blind to run, arm, model and reader
1, and we report Cohen's κ.

### 3.6 Sample size: how many cases and runs are enough

*(≈ 0.4 page; Table 1a. Planned 2026-11-10 by `harness/trials/stats/power_plan.py` from rounds 18–25;
the tests recomputed 2026-11-17 on all 6 cases, rounds 18–28; no model call.)* The claims are about specifications in general, so the **unit of
analysis is the case**; runs inside a case only make that case's mean more precise. Each model is
analysed on its own. For each case we take the arm's mean minus the Markdown's mean, then test the
case differences:

- **Naming (claim 2, superiority):** two-sided one-sample t-test over cases, α = 0.05; as a check that
  does not assume normality, a sign test, which needs all K cases in one direction and **K ≥ 6**
  (two-sided p = 2 · 0.5^K = 0.031; one-sided, K ≥ 5).
- **Code quality (claim 2, non-inferiority):** "no significant difference" does not show "no harm". The
  claim holds if the one-sided 95 % lower bound of the mean case difference in core % lies above −δ,
  with **δ = 2 points for Sonnet and 5 for Haiku** (about 1.5× each model's run-to-run spread, fixed in
  the interim report before rounds 21–25).
- **Silent invention (claim 4, equivalence):** the same bound on both sides with δ = 2 gaps per run.

**Table 1a.** The claims tested over the 6 cases (case differences, arm − Markdown, points of %; cases in
the order case006 · case010 · case016 · case005 · case011 · case001; n = 3 per cell on case006 and case010,
Haiku n = 5 elsewhere).

| Claim | Model | Six case differences | Test over cases | Status |
|---|---|---|---|---|
| Flags raise naming (oracle) | Haiku | +63.9 · +44.4 · +29.4 · +12.9 · +18.3 · +33.3 | t p = 0.007; sign p = 0.031 | **holds** |
| | Sonnet | +26.4 · +26.7 · +15.7 · +17.6 · +47.2 · +51.1 | t p = 0.004; sign p = 0.031 | **holds** |
| Review list raises naming | Haiku | +58.3 · +35.6 · +24.7 · +5.9 · +16.7 · +28.0 | t p = 0.012; sign p = 0.031 | **holds** |
| | Sonnet | +16.7 · +20.0 · +25.5 · +9.8 · +38.9 · +33.3 | t p = 0.003; sign p = 0.031 | **holds** |
| Compiler export raises naming | Haiku | +52.8 · +31.1 · +14.1 · −1.2 · +6.7 · +26.7 | t p = 0.041; 5 of 6 positive | t passes, sign test does not |
| | Sonnet | +23.6 · +17.8 · +9.8 · −3.9 · +30.6 · +20.0 | t p = 0.021; 5 of 6 positive | t passes, sign test does not |
| Oracle export does not harm core | Haiku (δ 5) | +4.2 · +2.1 · +4.1 · 0.0 · 0.0 · −0.1 | lower bound +0.03 | **non-inferior** |
| | Sonnet (δ 2) | −0.2 · −0.2 · −0.4 · 0.0 · +7.1 · 0.0 | lower bound −1.40 | **non-inferior** |
| Review list does not harm core | Haiku (δ 5) | +3.6 · +2.7 · +4.4 · −0.4 · −4.1 · 0.0 | lower bound −1.59 | **non-inferior** |
| | Sonnet (δ 2) | 0.0 · −0.8 · +0.3 · 0.0 · +6.6 · 0.0 | lower bound −1.25 | **non-inferior** |
| Compiler export does not harm core | Haiku (δ 5) | +9.7 · +2.5 · +5.0 · 0.0 · +0.3 · 0.0 | lower bound −0.25 | **non-inferior** |
| | Sonnet (δ 2) | −0.4 · +0.4 · +0.3 · 0.0 · +7.1 · −0.5 | lower bound −1.27 | **non-inferior** |
| No format changes silent invention | both (δ 2 gaps) | cases with gaps: case010, case016, case005, case011, case001 | 90 % CI inside ±2 for all 6 arm × model rows (K = 4–5) | **equivalent** |

The silent-invention intervals are, arm − Markdown in gaps per run: Haiku compiler +0.47 [−0.52, +1.46],
oracle +0.80 [+0.03, +1.57], review +0.15 [−0.30, +0.60]; Sonnet compiler +0.33 [−0.17, +0.84], oracle +0.17
[−0.51, +0.85], review −0.58 [−1.45, +0.29]. Without case001 (only 4 gaps, so little room to invent), two of
the six rows (Haiku oracle, Sonnet review) no longer fit inside ±2 at K = 3. Case011's +7.1 / +6.6 for Sonnet
comes from one Markdown run (§4.1).

**Measured spreads on all 6 cases.** Run-to-run SD within a cell: core Sonnet 2.53, Haiku 3.02 points; named
Sonnet 12.1, Haiku 6.7 points; silent inventions 0.97 gaps. Case-to-case spread (τ) of the oracle's naming
gain: Haiku 17.4, Sonnet 14.1 points. Sonnet's spreads grew from the plan's (core 1.12, named 7.0) because of
single runs: one case011 Markdown run that lost 56 core tests, and two case001 runs that named 2 and 6 of
15 conflicts (compiler export, review list).

**Power, as planned** (2026-11-10, from the first 3 cases; simulated, 4 000 studies per cell, true effects set
to the smallest observed naming gain and to zero for core and silent invention, spreads as then measured):

| Test, model | Runs per arm per case | K = 3 | K = 4 | K = 5 | K = 6 | K = 8 |
|---|---|---|---|---|---|---|
| Naming, Haiku (gain 39.5, case spread 16) | 3 / 5 | 0.58 / 0.60 | 0.88 / 0.88 | 0.97 / 0.97 | 1.00 / 1.00 | — |
| Naming, Sonnet (gain 20.7) | 3 / 5 | 0.84 / 0.94 | 0.99 / 1.00 | 1.00 / 1.00 | 1.00 / 1.00 | — |
| Core non-inferiority, Haiku, δ 5 | 3 / 5 | 0.62 / 0.78 | 0.84 / 0.94 | 0.93 / 0.99 | 0.98 / 1.00 | 1.00 / 1.00 |
| Core non-inferiority, Sonnet, δ 2 | 3 / 5 | 0.69 / 0.81 | 0.89 / 0.95 | 0.96 / 0.99 | 0.99 / 1.00 | 1.00 / 1.00 |
| Silent invention, δ 2 gaps (one side) | 3 / 5 | 0.73 / 0.83 | 0.92 / 0.97 | — | 1.00 / 1.00 | — |

**Decision.** More cases raise power far more than more runs per case. The target is power ≥ 0.80 in
every row and a sign test that can reach 0.05: **6 cases with planted conflicts** (case006, case010,
case016 and 3 new), **at least 4 with planted gaps** (case010, case016 and the new ones), **5 Haiku runs
and 3 Sonnet runs per arm per case** (Haiku's larger spread; 5 runs lift Haiku's core power at K = 5–6
from 0.93–0.98 to 0.99–1.00). Every case gets the same four arms, so Table 2 has no empty cell. The extra
rounds were planned in `extra-trials-plan.md` and run as rounds 27, 27b and 28. Re-estimated with the
six-case spreads, the power at K = 6 is 0.97–0.99 for Haiku's core bound (n 3–5), 0.76–0.87 for naming and
1.00 for silent invention, but 0.59 (n 3) for Sonnet's 2-point core bound, because of the single case011
run above; all three Sonnet lower bounds still lie above −2.

## 4 Results

### 4.1 Code quality does not move

*(≈ 0.4 page; Table 1b.)* **Table 1b.** Set 1: core tests passed, % of the core (Table 1), mean over runs,
with the run range. Haiku n = 5 per cell on case016 and the new cases, n = 3 on case006 and case010
(n = 5 with round 27b in the text); Sonnet n = 3.

| Case | Model | Markdown | Compiler export | Oracle export | Review list |
|---|---|---|---|---|---|
| case006 | Haiku | 87.6 (86.1–90.1) | 97.3 (96.2–98.0) | 91.8 (84.5–96.9) | 91.2 (86.1–96.4) |
| | Sonnet | 98.6 (98.4–98.7) | 98.2 (98.0–98.4) | 98.4 (98.2–98.7) | 98.6 (98.4–98.7) |
| case010 | Haiku | 89.8 (87.3–94.8) | 92.3 (89.0–94.2) | 91.9 (90.8–93.6) | 92.5 (90.2–93.6) |
| | Sonnet | 97.1 (95.4–98.8) | 97.5 (96.0–98.8) | 96.9 (94.8–98.8) | 96.3 (95.4–98.3) |
| case016 | Haiku | 92.5 (83.1–97.9) | 97.6 (96.7–98.8) | 96.7 (95.6–98.2) | 96.9 (93.2–98.8) |
| | Sonnet | 98.5 (97.9–99.1) | 98.8 (98.2–99.4) | 98.1 (97.3–98.8) | 98.8 (97.3–99.7) |
| case005 | Haiku | 100 (100–100) | 100 (100–100) | 100 (100–100) | 99.6 (97.9–100) |
| | Sonnet | 100 (100–100) | 100 (100–100) | 100 (100–100) | 100 (100–100) |
| case011 | Haiku | 99.7 (98.5–100) | 100 (100–100) | 99.7 (98.5–100) | 95.6 (79.3–100) |
| | Sonnet | 92.9 (79.3–100) | 100 (100–100) | 100 (100–100) | 99.5 (99.3–100) |
| case001 | Haiku | 100 (100–100) | 100 (100–100) | 99.9 (99.6–100) | 100 (100–100) |
| | Sonnet | 100 (100–100) | 99.5 (98.5–100) | 100 (100–100) | 100 (100–100) |

All three export and list arms pass the non-inferiority bound for both models over the six cases (Table 1a).
On the three new cases the core was at or near the ceiling in every arm: 85 of 96 runs passed every core
test. The two low cells come from two runs, a case011 Markdown run (Sonnet) and a case011 review-list run
(Haiku), each at 215 of 271. Both failed the same 56 tests for the same reason: they gave the error for an
unfinished expression (`foo.`) a different kind from the one the tests expect. That is one of the
disagreements already present in Zero2Repo's own text, found by four of the six reviews of case011, so it
is not an arm effect. On the first three cases Haiku's core was higher with every flag source (oracle +4.2,
+2.1, +4.1; review list +3.6, +2.7, +4.4; compiler export +9.7, +2.5, +5.0 points). That pattern did not
repeat on the new cases (−4.1 to +0.3), and over six cases no arm's gain is significant (p = 0.10–0.47).
Round 27b's two extra Haiku runs per arm on case006 also scored the Markdown higher than round 18 did two weeks
earlier (97.5 and 91.2 % against 86.1–90.1 %). With n = 5 the case006 Markdown mean rises from 87.6 to
90.3 % and the compiler export's gain there falls from +9.7 to +6.2. So we read the old case006 gap as time
or chance. On the conflict-related footprint tests the export did not help either. The rules the tests check
are stated in both formats; the failures we read are unspecified algorithms, single edge rules missed in both
formats, and coding slips.

### 4.2 Flags drive naming, item by item

*(≈ 0.6 page; Table 2.)* **Table 2.** Conflicts named (set 2a), % of items × runs; Haiku n = 5 on case016
and the new cases, n = 3 elsewhere. Core score in brackets (% of the core; tests of 338 for case016).

| Case | Model | Markdown | Compiler export | Oracle export | Review list |
|---|---|---|---|---|---|
| case006 (24) | Haiku | 36.1 (87.6 %) | 88.9 (97.3 %) | 100 (91.8 %) | 94.4 (91.2 %) |
| | Sonnet | 73.6 (98.6 %) | 97.2 (98.2 %) | 100 (98.4 %) | 90.3 (98.6 %) |
| case010 (15) | Haiku | 51.1 (89.8 %) | 82.2 (92.3 %) | 95.6 (91.9 %) | 86.7 (92.5 %) |
| | Sonnet | 66.7 (97.1 %) | 84.4 (97.5 %) | 93.3 (96.9 %) | 86.7 (96.3 %) |
| case016 (17) | Haiku | 64.7 (312.8) | 78.8 (329.8) | 94.1 (326.8) | 89.4 (327.6) |
| | Sonnet | 70.6 (333.0) | 80.4 (334.0) | 86.3 (331.7) | 96.1 (334.0) |
| case005 (17) | Haiku | 87.1 (100 %) | 85.9 (100 %) | 100 (100 %) | 92.9 (99.6 %) |
| | Sonnet | 82.4 (100 %) | 78.4 (100 %) | 100 (100 %) | 92.2 (100 %) |
| case011 (12) | Haiku | 75.0 (99.7 %) | 81.7 (100 %) | 93.3 (99.7 %) | 91.7 (95.6 %) |
| | Sonnet | 52.8 (92.9 %) | 83.3 (100 %) | 100 (100 %) | 91.7 (99.5 %) |
| case001 (15) | Haiku | 66.7 (100 %) | 93.3 (100 %) | 100 (99.9 %) | 94.7 (100 %) |
| | Sonnet | 42.2 (100 %) | 62.2 (99.5 %) | 93.3 (100 %) | 75.6 (100 %) |

With every conflict flagged, both models named 86–100 % against 36–87 % from the Markdown, a gain in all
twelve case × model cells (Table 1a). The new cases start higher from the Markdown (Haiku 67–87 %), so
the gain there is smaller (+13 to +33 points for Haiku), but it stays in the same direction. The compiler
export shows where the gain comes from. It flags 15 of 24, 9 of 15, 10 of 17, 8 of 17, 7 of 12 and 12 of 15
planted conflicts (case006, case010, case016, case005, case011, case001). On the flagged ones, Haiku's
naming went from 29, 48, 72, 95, 74 and 68 % in the Markdown to 100, 96, 100, 100, 100 and 100 %. Sonnet's
went from 60, 67, 70, 96, 52 and 42 % to 100, 89, 87, 100, 100 and 72 %; the 72 % includes one case001 run
that named 2 of 15. On the unflagged ones, whose both sides sit in the same packs, the change was small
and mixed: Haiku +22, +6, −6, −7, −20 and +7 points, Sonnet −4, +11, 0, −11, +7 and −22. So over all
items the compiler export sits between the Markdown and the oracle export in ten of twelve cells. The two
exceptions are case005, where it flags fewer than half the conflicts and named slightly fewer than the
Markdown (85.9 against 87.1 %, 78.4 against 82.4 %). A flag with a wrong
rationale did not help: case010's C18, flagged by the compiler as a different clash, was named in 0 of 3
Sonnet runs, as with the oracle export in round 19. The review list repeats this. On the new cases its
runs named 311 of 320 listed-conflict readings (8 of the 9 misses are in one case001 Sonnet run that named 6), and the unlisted
ones gained nothing over the Markdown (8 of 32 readings against 8 of 32). Case011's unlisted C19 was built
on side B in all 8 review-list runs, as in all 8 Markdown runs. Naming also changed what was built
unnoticed: across rounds 18, 19, 21, 27 and 28 no flagged conflict was ever built on side B without being
named, while Markdown runs did so 35 times.

**With round 27b (n = 5 for Haiku on case006 and case010).** The two extra runs per arm leave the
flagged arms where they were: case006 oracle 100 %, review list 94.2 %, compiler export 91.7 %; case010
94.7, 86.7 and 82.7 %. The two extra case006 Markdown runs named 70.8 and 54.2 %, against 29–42 % in round
18, so that cell's mean rises from 36.1 to 46.7 %. Every naming test over cases still passes (Haiku
oracle, review list and compiler export: t p = 0.004, 0.007 and 0.033; `power_plan_topup.json`), and the
second reader agreed with every one of the 312 top-up readings.

### 4.3 A plain review is the better detector

*(≈ 0.4 page; Table 3.)* Asked only to list contradictions in the same planted Markdown, with no
code, the same models found far more planted conflicts than the compiler, with far fewer false
entries:

| Detector | Found (of 100, 6 cases) | Precision | $ est. per spec |
|---|---|---|---|
| `sddc` compile (Haiku) | 57.0 % | 28.0 % of contradictions (79 of 282) | 1.45–3.58 |
| Haiku review (3 runs per case) | 90.3 % (271 of 300) | 93.4 % of entries | 0.02–0.12 |
| Sonnet review (3 runs per case) | 91.0 % (273 of 300) | 98.9 % of entries | 0.16–0.47 |

Rounds 22 (case006, case010, case016) and 28 (the new cases) used the same prompt, rule and reading. The new
cases repeat the first three: per case the reviews found 87–100 % of the planted conflicts against 41–73 %
for the compiler (7 of 17, 7 of 12, 11 of 15). The compiler is not dominated item by item: two case010
conflicts (exceptions in a list, each against a rule a few lines earlier) were found only by its pairwise
check. Case005's C12 was found by no detector: neither the compiler nor any of its six reviews. The reviews
also found real disagreements present in the original Zero2Repo text: three on the first three cases and
three more on the new ones.

### 4.4 The review list replaces the export's flags, and a settled list carries rulings

*(≈ 0.4 page.)* On case016, the Markdown plus one review list (15 of 17 flagged, 3 false entries)
gave 89.4 % (Haiku) and 96.1 % (Sonnet) naming, against 78.8 and 80.4 % from the compiler export,
with the same core (327.6, 334.0) and the fewest planted sides built of any arm (1 of 85, 1 of 51).
The list's errors travel: its false entry (a two-hit condition said to be missing that the PRD states)
made 5 of 8 runs build one hit, against 0 of 24 runs in round 21. On case006 and case010 (round 25)
the result repeats: 207 of 210 listed-conflict readings were named, 86.7–94.4 % over all items, with
core unchanged; the unlisted conflicts gained little or nothing (case010: 0 of 12, built on side B as
from the Markdown), and the lists' 4 false entries misled no run. On the three new cases (round 28; lists
flag 15 of 17, 11 of 12 and 14 of 15) the review list again named more than the compiler export in all
six cells (91.7–94.7 %, except Sonnet on case001 at 75.6 %, against 62.2–93.3 %), with core unchanged
(Table 1b).
**Settled list** (round 24, case016):
with the 3 false entries struck and a ruling on each entry (side B ruled on 7 of 15), agents built 118
of 120 rulings, including 54 of 56 side-B rulings that unruled agents built 0–2 times per arm; the
misleading one-hit build disappeared (0 of 8). The 2 misses are one item in two Haiku runs whose notes
state the ruling but whose code does not implement it.

### 4.5 No format reduces silent invention

*(≈ 0.4 page; Table 4.)* **Table 4.** Set 2b: silent inventions per run (gaps whose value the code
takes while the notes do not name it as unstated; lower is better), mean and per run. case010: 14 gaps
(round 20; its "export" is the plain compiler export, which flags no gap); case016: 15 gaps (round 21,
and rounds 23–24 on the same planted spec); case005, case011, case001: 11, 12 and 4 gaps (round 28). No arm
flags any gap.

| Case (gaps) | Model | Markdown | Compiler export | Oracle export | Review list | Settled list |
|---|---|---|---|---|---|---|
| case010 (14) | Haiku | 10.67 (12 · 10 · 10) | 11.00 (11 · 10 · 12) | — | — | — |
| | Sonnet | 13.33 (13 · 14 · 13) | 13.33 (14 · 14 · 12) | — | — | — |
| case016 (15) | Haiku | 12.4 (11 · 14 · 12 · 13 · 12) | 12.4 (12 · 13 · 11 · 13 · 13) | 13.2 (12 · 14 · 13 · 12 · 15) | 12.8 | 12.8 |
| | Sonnet | 13.67 (14 · 15 · 12) | 14.0 (14 · 14 · 14) | 13.33 (14 · 13 · 13) | 13.3 | 12.3 |
| case005 (11) | Haiku | 9.2 (9 · 8 · 10 · 9 · 10) | 8.4 (8 · 9 · 9 · 8 · 8) | 9.2 (10 · 9 · 9 · 9 · 9) | 8.8 (8 · 10 · 10 · 8 · 8) | — |
| | Sonnet | 9.33 (9 · 9 · 10) | 10.33 (10 · 11 · 10) | 10.33 (10 · 11 · 10) | 9.33 (11 · 9 · 8) | — |
| case011 (12) | Haiku | 4.8 (5 · 3 · 7 · 5 · 4) | 6.8 (7 · 8 · 8 · 7 · 4) | 6.4 (6 · 6 · 6 · 7 · 7) | 5.2 (5 · 6 · 3 · 5 · 7) | — |
| | Sonnet | 10.0 (9 · 11 · 10) | 10.67 (11 · 11 · 10) | 10.0 (10 · 11 · 9) | 8.33 (8 · 8 · 9) | — |
| case001 (4) | Haiku | 1.0 (1 · 2 · 0 · 2 · 0) | 1.8 (2 · 2 · 2 · 1 · 2) | 1.8 (2 · 1 · 0 · 3 · 3) | 1.2 (1 · 1 · 1 · 2 · 1) | — |
| | Sonnet | 3.0 (3 · 3 · 3) | 2.67 (3 · 2 · 3) | 3.0 (3 · 3 · 3) | 2.67 (3 · 2 · 3) | — |

Every arm's mean is within 2.0 gaps of its case's Markdown mean (run SD 0.97 gaps), and over the five cases
with gaps every arm is equivalent to the Markdown within ±2 gaps per run (Table 1a; K = 4–5). Agents filled
most gaps without saying so in every arm and case: 10.7–14.0 of 14–15 on case010 and case016, 8.4–10.3 of 11
on case005. Sonnet flagged 4 of 84 gap readings on case010. The exception is Haiku on case011, which named
5–9 of 12 gaps as unstated in each run (Sonnet 1–4). That is a model difference within one case, and it
holds in every arm. The gaps that were flagged were mostly those a neighbouring sentence still exposed. On
`nltk` every gap was filled with the real library's value (168 of 168), so the hidden tests reward the
invention; on `sloptrim`, which is not on PyPI, five gaps were filled in every run with a value the tests
reject.

## 5 Analysis

*(≈ 0.5 page.)* **Why tests do not move but naming does.** Every run read both sides of every
planted item; the difference is connecting them. A flag puts both quotes under one heading, which
removes the search step; the agent then names the conflict but mostly builds the original side, so
the tests — which check side A — see little change. **What carried the gain was the flag, not the
graph.** Unflagged conflicts in the compiler export gained nothing consistent over the Markdown (−22 to +22
points, six cases × two models), although they sat in the same packs. Flagged ones rose to 87–100 % in
eleven of twelve cells (72 % in the twelfth). And a flat list from a review gave the same gain. **Where the
compiler still has a place.** Its pairwise check reaches items a whole-document read passes over, and
its rulings and checklist are structure a person can audit. Its incremental design targets
specifications too large for one context, which our cases are not; that case is untested. **Cost.**
An export run costs Haiku 1.6–1.9× a Markdown run (1.7–3.1× for round 27's compiler exports), plus a compile of $1.45–3.58 est. and a verdict on
each false contradiction (203 of the 282 raised over the six cases); a review costs $0.02–0.47 est. and its coding run costs
about as much as an export run. **What the settled list adds** is control: a person's rulings,
not the agent's default, decide what is built, and striking a false entry removes the build it caused.
**The measure holds:** an arm-blind second reader read all 3 336 item readings of rounds 18–28. There were
21 disagreements. On re-reading, reader 2 was right in 3, and reader 1's table was corrected; reader 1 held
in the other 18. After the corrections the two readers agree on 99.5 % (κ 0.980), and no arm comparison
changes.

## 6 Limitations

*(≈ 0.4 page.)* (1) **One model family and one agent** (Claude in Claude Code). (2) **Small n:** 3–5
runs per cell; exact permutation tests cannot reach p < 0.10 within one case, so every claim rests on the
test over cases. (3) **Six cases**, five ported from well-known libraries the models may remember (`click`,
`nltk`, `h11`, `jmespath`, `tomli`); side A is what the tests check, so rulings go to side B and the core
excludes the footprints. On the three new cases the core was at the ceiling, so set 1 there can show harm
but hardly help. (4) **The planted items were designed by
the same assistant that built the compiler and reads the notes**, with the answer key written before
any run; one removal (G01) was missed by its key-phrase check and is reported apart. (5) **Reading
`NOTES.md` is a judgement:** reader 1 was not blind to arm; reader 2 is blind to arm by label (not by
content) and a model from the same family (κ 0.980); 3 of 21 disagreements corrected reader 1. Round 24's
rulings followed a fixed alternation, not a person's judgement, and a person's cold filtering of a list
is not measured. (6) **The export changes more than structure:** it is 3–6× longer and its map states
how many conflicts are open. (7) **Specifications fit one context**, so the large-spec case is not
tested. (8) **Costs are API-price estimates**, not money billed. (9) Rounds 17 and 18 changed three
conditions at once; only within-round comparisons are used. (10) On case006 and case010 the four arms
come from three rounds a week apart (rounds 18/19, 25 and 27) under the same tasks and conditions, not
interleaved, so time is a confound for those cells. Round 27b shows it matters: two Markdown runs on
case006 two weeks after round 18 named 54–71 % instead of 29–42 % and scored higher core. On the new cases
(round 28) all four arms were interleaved in one queue. (11) **No retrieval (RAG) baseline was run**; §3.2.1
argues from the design, not from measurement.

## 7 What we learned: a retrospective

*(Proposed 2026-11-17, owner to review. ≈ 0.4 page. This is a course project, so the process is reported
too; every fact below is from a named trial record or design log.)*

1. **A test must be able to fail.** Our first pilot gave the Markdown and the export the same score (26 of
   26 hidden tests, rel01 phase D): a clean specification leaves nothing for a format to fix. Planting
   conflicts and gaps, and leaving out of the core the tests they touch, made the benchmark able to tell
   formats apart. Even so, the core was at its ceiling on the three new cases (85 of 96 runs), so a ceiling
   needs checking in every case, not once.
2. **Build the plainest baseline first.** We built the graph and compared formats for 21 rounds before
   asking a model, with no tools, to list the contradictions (round 22). That review was the better
   detector. Run first, it would have set the research question weeks earlier.
3. **Change one thing at a time, and run arms side by side.** Rounds 17 and 18 changed three conditions at
   once, so only comparisons within a round count (§6). On the old cases the arms ran weeks apart, and
   round 27b showed that drift moves the Markdown baseline. Round 28 ran all four arms in one interleaved
   queue.
4. **Fix the answer and the reading rule before the runs.** Each answer key and the strict reading rule
   were written before any model output, and a blind second reader checked every reading. That reader
   corrected three of our readings and confirmed the rest (κ 0.980).
5. **Read the logs before calling something a model result.** Early Haiku stops in rounds 14–17 came from
   an output-limit cut and a misread budget reminder (13 of 31 Haiku runs hit the cut, 4 misread the
   budget), not from the model's ability. Harness faults, such as a Docker socket failure that stopped the
   run drivers for four days, also had to be told apart from results.
6. **Size the study on the unit of the claim.** The claims are about specifications, so the case is the
   unit. Going from 3 to 6 cases added far more power than more runs per case (§3.6). Planning this before
   the extra rounds decided their shape.
7. **Test the expectation, and keep the negative result.** We expected the graph to help, and we expected
   the agents to miss the same conflicts as the compiler (rel02 D34). The data showed neither. Asking why
   the graph did not help is what led to the real finding: the flags did the work.
8. **Working with an AI assistant.** Claude Code wrote most of the code, planted the items and read the
   notes (Appendix B). That speed made 28 rounds possible, but the same assistant designed the items and
   read the results (§6 item 4). The safeguards were the answer key written first, black-box probes, fixed
   rules, the blind second reader, and the owner reviewing every decision and commit.

## 8 Conclusion

*(≈ 0.2 page.)* A compiled specification graph did not make an AI coding agent's code better on
six public cases with planted contradictions. What helped was telling the agent where the
contradictions are: flagged conflicts were named, and built knowingly, while unflagged ones were not.
A one-pass LLM review supplied those flags better and more cheaply than our compiler, and its list
carried the help to the agent. The list's errors travel too, so the practical pipeline is: review,
let a person strike false entries and rule, and hand the agent the short settled list beside the
specification. Agents still fill silent gaps without saying so, whatever the format.

## References

From `project-proposal/latex/references.bib` (keys cited above), plus to add after opening the
primary source: Zero2Repo (benchmark paper or repository, commit `0ecc523`); DevEval / DevBench 2024 if
the small-spec results are kept.

## Appendix A. Contributions *(owner to fill)*

## Appendix B. Use of AI tools

We used **Claude Code** (Anthropic) to write the compiler (`sddc`) and its tests from our
specifications, the Harbor task builders, the run driver and the scorers; to design and plant the
conflicts and gaps and build the oracle exports; to run and monitor the trials; to read the agents'
`NOTES.md` into detection tables (reader 1); to debug runs; and to draft the trial records and this
report. A second Claude model (Sonnet) is reader 2. We used **GitHub Copilot CLI** to operate one
round's run queue from a written procedure. Claude models are also part of the method itself: Claude
Haiku splits and compares requirements inside the compiler, Claude Haiku and Sonnet are the coding
agents and reviewers under test (§3). *[Owner: state what you checked yourself — figures, citations,
code — before submission.]*

## Appendix C. Reproduction

Code: the `sdd-compiler` repository (link to add). Main tables: `harness/trials/r21-…/notes/tables.py`,
`r23-…/notes/tables.py`, `r24-…/notes/tables.py`, `r25-…/notes/tables.py`, `r27-…/notes/tables.py`, `r28-…-case{005,011,001}-…/notes/tables.py`, `r27b-…/notes/detection.py`, `stats/power_plan.py` (`TOPUP=1` for the n = 5 figures), `r22-…/notes/score.py`, `r28-zero2repo-reviews/notes/score.py`, `r26-…/notes/reader2.py table`;
each reads the saved runs and needs no model call. Seeds: model runs are not seeded (Claude Code exposes
no seed); the second reader's run codes use `random.Random(2611 + n)`.

## Mapping to the marking scheme (remove before submission)

| Criterion (weight) | Where the draft answers it |
|---|---|
| Technical quality (30 %) | §3 controls: frozen tasks, footprint-free core, answer key first, probes, two readers |
| Evaluation and rigour (25 %) | Tables 1a–4, case-level tests (t, sign, non-inferiority, equivalence), κ, limitations; a null result reported as such |
| Original contribution (25 %) | Planted-conflict design; review-vs-compiler baseline; settled-list pipeline |
| Communication (20 %) | One claim per subsection; every number traceable to a `TRIAL.md` |
