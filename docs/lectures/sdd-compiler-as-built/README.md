# The SDD Compiler, as built — a beginner's lecture

> **Tier:** lecture — explanation for understanding, **never binding** (CLAUDE.md). If this lecture and
> a spec in `sdd/specs/` disagree, the spec wins; if it and the code disagree, one of them is a bug.
> **First written:** 2026-09-24, from the code at 628 passing tests and the R18 store.
> **Updated:** 2026-11-08, from the code at **779 passing tests** (`src/` last changed 2026-11-01,
> commit `0fed585`), the specs as amended in rel02, and a store compiled with that code (below).
> **Format:** Markdown, at the owner's request (the house default for lectures is HTML).

This lecture describes what the SDD Compiler **actually does today**, read from `src/`, not what the
design documents hoped it would do. Where the two differ, it says so.

## The real runs it quotes

Every number from a real run names its store. Three stores are used:

| Name in this lecture | What was compiled | Code | Where |
|---|---|---|---|
| **R18** | This repository's own `sdd/specs/` (9 files), 2026-09-23 | rel01, before contracts, examples-as-nodes and the export | `~/sddc-runs/full-corpus/.sdd/` |
| **Pilot graph** (R-000023) | The same specs, re-compiled with contracts and the Traceability skip, 2026-09-30 | rel01 at close | `~/sddc-runs/pilot-graph-R000023/`, export in `~/sddc-runs/pilot-export-R000023/` |
| **R21 store** | Zero2Repo case016 (`prosecheck`, 3 files) **with 17 planted conflicts and 16 removed facts**, rel02 round 21, 2026-11-05 | **current** (`0fed585`) | `harness/trials/r21-zero2repo-case016-conflicts-gaps/work/compile-full/.sdd/` |

R18 shows what a large compile of this repository's specs looked like and cost. The R21 store shows
the **current** code's behaviour, on a product spec that was damaged on purpose for a trial. Read its
conflict counts with that in mind.

## What changed since the first edition (2026-09-24)

| Change | Spec | Chapter |
|---|---|---|
| **`sddc export`**: map, packs and checklist for a coding agent, with a conflict gate | F7 (approved 2026-09-30; amended D15–D17 in rel02) | 1, 2, 8, **9** |
| Sections a person names (`skip_headings`, default Traceability) are stored but never atomized | F1 D14 | 2, 4 |
| Fenced blocks in a contract language (`json`, `yaml`, `text`) form one node, whole, with the title's `CT-` id | F1 D15, F2 D21, F3 D39–D40, F6 D23–D24 | 3, 4, 6 |
| A definition sentence is attached to the term it defines | F3 D38 | 5 |
| A re-judged pair keeps only its latest verdict's links (the old I-91 defect) | F6 D20 | 6, 8 |
| The run records why each unjudged pair failed | F6 D22 | 6 |
| **An example sentence becomes a `V` node** of the claim it illustrates, flagged `example` | F2 D22, F3 D41 | 3, 4, 5 |
| An unchanged node takes its block's current annotations | F3 D42 | 7 |
| A table cell holding several sentences gives one claim per sentence | F3 D43 | 3, 4 |
| An atom keeps the words that say what it is about (subject or condition) | F3 D44 | 3, 4 |
| A pair is proposed from either end in an incremental compile | F5 D14 | 6, 7 |
| S1 follows `broader`; new sources **S9** (rare keyword) and **S10** (topic named) | F5 D15–D17 | 6 |
| Precision on R18 measured: **1 of 381** conflicts real | rel01 close-out, I-93 | 6, 10 |
| Compiler recall on planted conflicts, three product specs | rel02 rounds 17, 19, 21 | 10 |

## Reading order

| # | Chapter | Answers |
|---|---|---|
| 1 | [The big picture](01-the-big-picture.md) | What is a spec graph, and why build one? The whole pipeline on one page |
| 2 | [Quick start](02-quick-start.md) | Install, `init`, `compile`, read the report, judge a conflict, `export`. Exit codes and cost |
| 3 | [Who does what: the AI model and the code](03-who-does-what.md) | Which model breaks specs down, which builds the graph, and where code — not the model — decides |
| 4 | [From Markdown to nodes](04-from-markdown-to-nodes.md) | Blocks, atoms, descriptions, examples, contracts; every field of a node record, on a real node |
| 5 | [Layers, terms and families](05-layers-terms-families.md) | How a node is classified, and why each rule is the way it is |
| 6 | [Relations and conflicts](06-relations-and-conflicts.md) | How pairs are found (ten sources), judged, turned into links and conflict records |
| 7 | [Changes and new specs](07-changes-and-new-specs.md) | What happens when you edit or add a spec; how to trace where a new claim lands |
| 8 | [Where the graph lives, and how to look at it](08-storage-and-visualization.md) | The `.sdd/` store, where the real stores are, the generated views, diagrams |
| 9 | [Handing the graph to an AI agent](09-reading-the-graph-as-an-agent.md) | `sddc export`: what it writes, how an agent reads it, what the trials found; reading the store by hand |
| 10 | [Trust, limits and cost](10-trust-limits-and-cost.md) | What is measured, what is not, known defects, what a compile and an export cost |
| 11 | [Glossary](11-glossary.md) | Every term in one place |

`scripts/` holds the helpers used in chapters 8 and 9: `context_pack.py` (one family's claims by
tier), `family_mermaid.py` (a diagram of one family), `build_viewer.py` + `viewer_template.html` (an
interactive HTML explorer of a whole store) and `review_queue.py` (a CSV of open conflicts for
adjudicating by hand). All four were run on the R18 store when written and **re-run on the R21 store on
2026-11-08 with the current code: all exit 0.**

## One running example

Every chapter uses the same toy spec, a **photo-sharing app**, because it needs no knowledge of this
repository:

```markdown
## Sharing

A share link must expire 30 days after it is created.

A share link must be revocable by its owner.
```

…and, later, a second author's paragraph in another file:

```markdown
Share links expire after 7 days.
```

A human skimming two files may miss that 30 days and 7 days cannot both be true. Finding that is the
compiler's job. By the end of chapter 6 you will have followed those three sentences all the way to a
conflict record, with the real scores the code computes (recomputed with the current code on
2026-11-08: unchanged).
