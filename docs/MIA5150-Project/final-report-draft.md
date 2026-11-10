# Flags, not graphs: what helps an AI coding agent with a self-contradicting specification

> **Final report draft** (MIA 5150, due 4 Dec 2026; 6 pages max in NeurIPS LaTeX, not counting references
> and the contributions appendix). Opened 2026-11-09 by Claude Code for the owner, from the interim
> report (`interim-report.md`, its §4 tables are the figures' source) and the trial records under
> `harness/trials/`. Working Markdown, to be moved into the proposal's LaTeX template
> (`project-proposal/latex/`, same `references.bib`). **Every number is copied from a named trial
> record; none is new here.** Citations use the keys of `references.bib` (checked 2026-09-29);
> `[cite: …]` marks a source that is not yet in the `.bib` and must be opened before it is cited.
> Rounds 24–26 (9–10 November) are filled in from their `TRIAL.md` files (2026-11-10). Length target: about 3 300 words of text, 3 tables, 1 figure.

## Abstract

Spec-driven development gives an AI coding agent a written specification instead of a chat. Real
specifications drift: two documents, or two paragraphs, say different things. We built a compiler,
`sddc`, that turns a folder of Markdown specifications into a graph of quoted requirements and reports
each pair it judges contradictory, and asked whether an agent builds better software from the
compiled form. In controlled runs of Claude Code (Claude Haiku and Sonnet) on three public Zero2Repo
cases (8 000–19 000 words, 197–476 hidden tests) with 15–24 contradictions planted from an answer key
written before any run, **the compiled form did not raise hidden-test scores**: Sonnet's core score
moved by less than 1 % in every case, and Haiku's gains stayed inside its own run spread (pooled
permutation test p = 0.06). What changed was **whether the agent noticed and reported the
contradictions**: with every planted conflict flagged, naming rose from 36–74 % to 93–100 %. The gain
followed the flags item by item, and **a one-pass LLM review supplied better flags than the compiler**
(recall 87–89 % against 57 %, precision 90–99 % against 26 %, at a tenth of the cost). Handing that
review list to the agent beside the plain Markdown gave most of the oracle's naming gain on all three
cases (86.7–96.1 % of conflicts named, 95.5–100 % of those listed). With its false entries struck and a
ruling on each entry, the list carried the rulings into the code (118 of 120 built). Neither form reduced silent invention of facts we removed from the specification (10–14 of
14–15 per run in every arm). We conclude that for specifications that fit one context, the useful
artefact is a short, checked list of conflicts with rulings, not a graph.

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
2. Evidence on three cases and two models that a compiled graph does not change hidden-test scores,
   while **flagged** conflicts are named far more often, and only the flagged ones (§4.1–4.2).
3. A baseline the literature and our proposal lacked: a plain LLM review is a better and cheaper
   conflict detector than the compiler on these specifications, and its list carries the same help to
   the coding agent (§4.3–4.4).
4. A negative result on hallucination: no format makes an agent say that the specification is silent
   (§4.5).

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
motivated the graph. **Evaluation.** We report counts and ranges with exact permutation tests, following
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
| case006 (`click`) | 14 435 | 476 | 24 | — | 445 | 18, 25 |
| case010 (`nltk`) | 8 412 | 197 | 15 | 14 (round 20) | 173 / 175 | 19, 20, 25 |
| case016 (`sloptrim`) | 18 845 | 388 | 17 | 15 | 338 | 21, 23, 24 |

### 3.4 Arms

- **Markdown:** the planted specification as given.
- **Compiler export:** `sddc export` of the planted specification, false contradictions removed by
  verdicts, nothing added (case016 only).
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

## 4 Results

### 4.1 Code quality does not move

*(≈ 0.3 page; Table 2, set 1 column.)* Sonnet's core score was within 1 % between Markdown and
oracle export in every case (98.6 vs 98.4 % on case006, 97.1 vs 96.9 % on case010, 333.0 vs
331.7 of 338 on case016). Haiku's core was higher from the export on all three cases (+4.2, +2.1,
+4.1 points) but inside its own run spread; an exact permutation test that shuffles arm labels within
each case gives p = 0.060 (Sonnet p = 0.59). On the conflict-related footprint tests the export did
not help either. The rules the tests check are stated in both formats; the failures we read are
unspecified algorithms, single edge rules missed in both formats, and coding slips.

### 4.2 Flags drive naming, item by item

*(≈ 0.6 page; Table 2.)* **Table 2.** Conflicts named (set 2a), % of items × runs; n = 3 per cell
except case016 Haiku, n = 5. Core score in brackets.

| Case | Model | Markdown | Compiler export | Oracle export | Review list |
|---|---|---|---|---|---|
| case006 (24) | Haiku | 36.1 (87.6 %) | — | 100 (91.8 %) | 94.4 (91.2 %) |
| | Sonnet | 73.6 (98.6 %) | — | 100 (98.4 %) | 90.3 (98.6 %) |
| case010 (15) | Haiku | 51.1 (89.8 %) | — | 95.6 (91.9 %) | 86.7 (92.5 %) |
| | Sonnet | 66.7 (97.1 %) | — | 93.3 (96.9 %) | 86.7 (96.3 %) |
| case016 (17) | Haiku | 64.7 (312.8) | 78.8 (329.8) | 94.1 (326.8) | 89.4 (327.6) |
| | Sonnet | 70.6 (333.0) | 80.4 (334.0) | 86.3 (331.7) | 96.1 (334.0) |

With every conflict flagged, both models named 93–100 % against 36–74 % from the Markdown, and the
ranges do not overlap in five of six cells. The compiler export on case016 shows where the gain comes
from: on the 10 conflicts it flags, naming rose from 72 to 100 % (Haiku) and from 70 to 87 % (Sonnet);
on the 6 it misses, whose both sides sit in the same packs, it did no better than the Markdown (57 vs
63 %, 83 vs 83 %). The review list repeats this: every review-list run named all 15 listed conflicts,
and on the 2 unlisted ones it did no better than the Markdown. Naming also changed what was built
unnoticed: across rounds 18, 19 and 21 no flagged conflict was ever built on side B without being
named, while Markdown runs did so 26 times.

### 4.3 A plain review is the better detector

*(≈ 0.4 page; Table 3.)* Asked only to list contradictions in the same planted Markdown, with no
code, the same models found far more planted conflicts than the compiler, with far fewer false
entries:

| Detector | Found (of 56, 3 cases) | Precision | $ est. per spec |
|---|---|---|---|
| `sddc` compile (Haiku) | 57.1 % | 25.8 % of contradictions | 1.49–3.58 |
| Haiku review (3 runs per case) | 89.3 % | 90.1 % of entries | 0.02–0.12 |
| Sonnet review (3 runs per case) | 86.9 % | 99.3 % of entries | 0.16–0.36 |

The compiler is not dominated item by item: two case010 conflicts (exceptions in a list, each against
a rule a few lines earlier) were found only by its pairwise check, and every planted item was found
by some detector. The review also found three real disagreements present in the original Zero2Repo
text.

### 4.4 The review list replaces the export's flags, and a settled list carries rulings

*(≈ 0.4 page.)* On case016, the Markdown plus one review list (15 of 17 flagged, 3 false entries)
gave 89.4 % (Haiku) and 96.1 % (Sonnet) naming, against 78.8 and 80.4 % from the compiler export,
with the same core (327.6, 334.0) and the fewest planted sides built of any arm (1 of 85, 1 of 51).
The list's errors travel: its false entry (a two-hit condition said to be missing that the PRD states)
made 5 of 8 runs build one hit, against 0 of 24 runs in round 21. On case006 and case010 (round 25)
the result repeats: 207 of 210 listed-conflict readings were named, 86.7–94.4 % over all items, with
core unchanged; the unlisted conflicts gained little or nothing (case010: 0 of 12, built on side B as
from the Markdown), and the lists' 4 false entries misled no run. **Settled list** (round 24, case016):
with the 3 false entries struck and a ruling on each entry (side B ruled on 7 of 15), agents built 118
of 120 rulings, including 54 of 56 side-B rulings that unruled agents built 0–2 times per arm; the
misleading one-hit build disappeared (0 of 8). The 2 misses are one item in two Haiku runs whose notes
state the ruling but whose code does not implement it.

### 4.5 No format reduces silent invention

*(≈ 0.3 page.)* With 14 facts removed from case010 (round 20) and 15 from case016 (round 21), agents
filled most gaps without saying so in every arm (arm means 10.7–14.0 silent inventions; Sonnet
flagged 4 of 84 gap readings on case010). The gaps that were flagged were mostly those a neighbouring
sentence still exposed. On `nltk` every gap was filled with the real library's value (168 of 168), so
the hidden tests reward the invention; on `sloptrim`, which is not on PyPI, five gaps were filled in
every run with a value the tests reject.

## 5 Analysis

*(≈ 0.5 page.)* **Why tests do not move but naming does.** Every run read both sides of every
planted item; the difference is connecting them. A flag puts both quotes under one heading, which
removes the search step; the agent then names the conflict but mostly builds the original side, so
the tests — which check side A — see little change. **What carried the gain was the flag, not the
graph.** Unflagged conflicts in the compiler export were named no more often than in the Markdown,
although they sat in the same packs; and a flat list from a review gave the same gain. **Where the
compiler still has a place.** Its pairwise check reaches items a whole-document read passes over, and
its rulings and checklist are structure a person can audit. Its incremental design targets
specifications too large for one context, which our cases are not; that case is untested. **Cost.**
An export run costs Haiku 1.6–1.9× a Markdown run, plus a compile of $1.49–3.58 est. and a verdict on
each of 33–51 false contradictions per case (of 46–69 raised); a review costs $0.02–0.36 est. and its coding run costs
about as much as an export run. **What the settled list adds** is control: a person's rulings,
not the agent's default, decide what is built, and striking a false entry removes the build it caused.
**The measure holds:** an arm-blind second reader agreed with reader 1 on 99.5 % of 1 382 item readings
(κ 0.983), and no arm comparison changes.

## 6 Limitations

*(≈ 0.4 page.)* (1) **One model family and one agent** (Claude in Claude Code). (2) **Small n:** 3
runs per cell (5 for Haiku on case016); exact permutation tests cannot reach p < 0.10 within one case.
(3) **Three cases**, two from famous libraries the models may remember; side A is what the tests check,
so rulings go to side B and the core excludes the footprints. (4) **The planted items were designed by
the same assistant that built the compiler and reads the notes**, with the answer key written before
any run; one removal (G01) was missed by its key-phrase check and is reported apart. (5) **Reading
`NOTES.md` is a judgement:** reader 1 was not blind to arm; reader 2 is blind to arm by label (not by
content) and a model from the same family (κ 0.983); one disagreement corrected reader 1. Round 24's
rulings followed a fixed alternation, not a person's judgement, and a person's cold filtering of a list
is not measured. (6) **The export changes more than structure:** it is 3–6× longer and its map states
how many conflicts are open. (7) **Specifications fit one context**, so the large-spec case is not
tested. (8) **Costs are API-price estimates**, not money billed. (9) Rounds 17 and 18 changed three
conditions at once; only within-round comparisons are used.

## 7 Conclusion

*(≈ 0.2 page.)* A compiled specification graph did not make an AI coding agent's code better on
three public cases with planted contradictions. What helped was telling the agent where the
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
`r23-…/notes/tables.py`, `r24-…/notes/tables.py`, `r25-…/notes/tables.py`, `r22-…/notes/score.py`, `r26-…/notes/reader2.py table`;
each reads the saved runs and needs no model call. Seeds: model runs are not seeded (Claude Code exposes
no seed); the second reader's run codes use `random.Random(2611 + n)`.

## Mapping to the marking scheme (remove before submission)

| Criterion (weight) | Where the draft answers it |
|---|---|
| Technical quality (30 %) | §3 controls: frozen tasks, footprint-free core, answer key first, probes, two readers |
| Evaluation and rigour (25 %) | Tables 2–3, permutation tests, κ, limitations; a null result reported as such |
| Original contribution (25 %) | Planted-conflict design; review-vs-compiler baseline; settled-list pipeline |
| Communication (20 %) | One claim per subsection; every number traceable to a `TRIAL.md` |
