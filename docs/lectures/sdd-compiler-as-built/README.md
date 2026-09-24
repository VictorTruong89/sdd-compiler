# The SDD Compiler, as built — a beginner's lecture

> **Tier:** lecture — explanation for understanding, **never binding** (CLAUDE.md). If this lecture and
> a spec in `sdd/specs/` disagree, the spec wins; if it and the code disagree, one of them is a bug.
> **Written:** 2026-09-24, from the code at 628 passing tests and the R18 full-corpus store.
> **Format:** Markdown, at the owner's request (the house default for lectures is HTML).

This lecture describes what the SDD Compiler **actually does today**, read from `src/`, not what the
design documents hoped it would do. Where the two differ, it says so. Every number quoted from a real
run is from **R18** — the compile of this repository's own `sdd/specs/` finished on 2026-09-23 — and
is labelled as such.

## Reading order

| # | Chapter | Answers |
|---|---|---|
| 1 | [The big picture](01-the-big-picture.md) | What is a spec graph, and why build one? The whole pipeline on one page |
| 2 | [Quick start](02-quick-start.md) | Install, `init`, `compile`, read the report, record a verdict. Exit codes and cost |
| 3 | [Who does what: the AI model and the code](03-who-does-what.md) | Which model breaks specs down, which builds the graph, and where code — not the model — decides |
| 4 | [From Markdown to nodes](04-from-markdown-to-nodes.md) | Blocks, atoms, descriptions; every field of a node record, on a real node |
| 5 | [Layers, terms and families](05-layers-terms-families.md) | How a node is classified, and why each rule is the way it is |
| 6 | [Relations and conflicts](06-relations-and-conflicts.md) | How pairs are found, judged, turned into links and conflict records |
| 7 | [Changes and new specs](07-changes-and-new-specs.md) | What happens when you edit or add a spec; how to trace where a new claim lands |
| 8 | [Where the graph lives, and how to look at it](08-storage-and-visualization.md) | The `.sdd/` store, the R18 store's location, the generated views, diagrams |
| 9 | [Reading the graph as an AI agent](09-reading-the-graph-as-an-agent.md) | A recipe an agent can follow today to gather the specs for a coding task |
| 10 | [Trust, limits and cost](10-trust-limits-and-cost.md) | What is measured, what is not, known defects, what a run costs |
| 11 | [Glossary](11-glossary.md) | Every term in one place |

`scripts/` holds two small helpers used in chapters 8 and 9, both tested on the R18 store:
`context_pack.py` (the agent recipe) and `family_mermaid.py` (a diagram of one family).

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
conflict record, with the real scores the code computes.
