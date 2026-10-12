# 1. The big picture

## The problem, in kitchen terms

Imagine a restaurant whose recipes are written by ten cooks over two years, in forty notebooks. One
notebook says *"rest the steak 5 minutes"*, another *"never serve steak that rested under 10"*. No cook
reads all forty notebooks before cooking. Contradictions sit there until a customer finds them.

A folder of Markdown specifications is those notebooks. It is written for humans, one document at a
time, and nothing checks it as a whole.

The **SDD Compiler** reads every notebook, cuts it into single instructions ("rest the steak 5
minutes"), files each instruction on an index card, sorts the cards by what they are about ("steak")
and by what kind of instruction they are, and then lays likely-related cards side by side and asks:
*do these two agree?* The result is a **spec graph**: every claim in the spec set as a node, with its
relations to the others as links, and every disagreement as a conflict record.

## What rel01 does, in one sentence

> Point `sddc compile` at a folder of static Markdown spec files and get back a spec graph plus a
> report of every conflict in it. (rel01 D26)

No hooks, no live editing, no code generation — those are later releases. rel01 builds the graph and
checks it.

## The pipeline

```text
 Markdown files
      │  F1 ingest            code only — split into blocks, give each a stable id
      ▼
 blocks (.sdd/blocks.jsonl)
      │  F3 atomize           AI model: Q-ATOM, Q-DESC, Q-TERM  ─┐ every answer checked
      │                       code: guards, layer, family, ids ──┘ by code before it is kept
      ▼
 nodes + terms (.sdd/nodes/, terms.jsonl)
      │  F5 retrieve          code only — which pairs of nodes are worth comparing
      ▼
 candidate pairs (in memory)
      │  F6 judge             AI model: Q-PAIR — how do these two relate?
      │                       code: links, conflict records, suppressions
      ▼
 links + conflicts (.sdd/edges/, conflicts.jsonl)
      │  F4 store + report    code only — one all-or-nothing write, checks, views, report
      ▼
 the spec graph  +  the end-of-run report  +  .sdd/views/*.md
```

The spec that governs each stage is named on the left: `sdd/specs/F1_ingest` … `F6_conflicts`.

## Five principles you will see everywhere

1. **The model answers small, closed questions; code decides.** The model never "builds the graph".
   It answers four kinds of multiple-choice-with-quotes question, and deterministic code turns the
   answers into records. (Vision §3; chapter 3.)
2. **Every answer is anchored in the source.** Whatever the model says, it must quote the spec
   verbatim, and code checks the quote is really there (guard G2). A claim with no quote is not
   believed.
3. **Nothing is silently dropped.** A block the model could not handle stays *pending* and is listed
   in the report; a run stopped early says so and exits `5`; an unusable answer is re-asked. "Fail
   loud, never silent" is a house rule.
4. **Same input, same graph.** Every accepted model answer is recorded in a *judgment lock*
   (`.sdd/lock/`). The next compile replays it instead of asking again, so a rebuild is free and
   byte-identical, and a stopped run resumes where it stopped.
5. **Status is derived, never set.** Whether a node is `conflict`, `ambiguous`, `stale`, `unchecked`
   or `validated` is computed from facts on the record every time it is written (F2 §4.6).

## What you get at the end

| Artefact | What it is | Where |
|---|---|---|
| The report | Every conflict, grouped, contradictions first, with file and line | printed by `sddc compile`; `.sdd/views/conflicts.md` |
| The graph | Nodes, terms, links, conflict records | `.sdd/` (chapter 8) |
| The views | A map of families × layers, one card per family | `.sdd/views/` |
| The lock | Every model answer, with its cost | `.sdd/lock/` |

**R18, for scale:** this repository's 9 spec files → 845 blocks → **950 nodes**, 1 031 terms,
**4 199 distinct links**, **381 open conflicts**, in 16 resumable runs.
