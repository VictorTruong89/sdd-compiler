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

Then it prints the notebooks again for the cook who will do the work: one booklet per section, in a
sensible cooking order, with the disputed instructions marked and a tick-list of every instruction.
That is the **export**.

## What the compiler does, in two sentences

> `sddc compile` turns a folder of static Markdown specs into a checked spec graph with a report of
> every conflict, and `sddc export` turns that graph into files a coding agent builds from.
> (rel01 close-out, D26 and D34)

No hooks, no live editing, no code generation — generating code from the export is done by any coding
agent outside this repository (F7 §2). rel02 is not adding features to the compiler. It tests whether
the export helps an agent, and it fixes the compiler where those trials showed it missing planted
conflicts.

## The pipeline

```text
 Markdown files
      │  F1 ingest            code only — split into blocks, give each a stable id
      ▼
 blocks (.sdd/blocks.jsonl)
      │  F3 atomize           AI model: Q-ATOM, Q-DESC, Q-TERM  ─┐ every answer checked
      │                       code: guards, layer, family, ids,  │ by code before it is kept
      │                       examples, contracts, definitions ──┘
      ▼
 nodes + terms (.sdd/nodes/, terms.jsonl)
      │  F5 retrieve          code only — which pairs of nodes are worth comparing (S1–S10)
      ▼
 candidate pairs (in memory)
      │  F6 judge             AI model: Q-PAIR — how do these two relate?
      │                       code: links, conflict records, suppressions
      ▼
 links + conflicts (.sdd/edges/, conflicts.jsonl)
      │  F4 store + report    code only — one all-or-nothing write, checks, views, report
      ▼
 the spec graph  +  the end-of-run report  +  .sdd/views/*.md
      │  a person judges the open contradictions (sddc conflicts judge)
      │  F7 export            code only, no model call — `sddc export`
      ▼
 MAP.md  +  packs/NN-*.md  +  CHECKLIST.md  +  export.meta.json   →  a coding agent
```

The spec that governs each stage is named on the left: `sdd/specs/F1_ingest` … `F7_agent_export`.

## Five principles you will see everywhere

1. **The model answers small, closed questions; code decides.** The model never "builds the graph".
   It answers four kinds of multiple-choice-with-quotes question, and deterministic code turns the
   answers into records. (Vision §3; chapter 3.)
2. **Every answer is anchored in the source.** Whatever the model says, it must quote the spec
   verbatim, and code checks the quote is really there (guard G2). A claim with no quote is not
   believed.
3. **Nothing is silently dropped.** A block the model could not handle stays *pending* and is listed
   in the report; a run stopped early says so and exits `5`; an unusable answer is re-asked. The export
   checks that every live block's text is in some pack before it writes anything. "Fail loud, never
   silent" is a house rule.
4. **Same input, same graph.** Every accepted model answer is recorded in a *judgment lock*
   (`.sdd/lock/`). The next compile replays it instead of asking again, so a rebuild is free and
   byte-identical, and a stopped run resumes where it stopped. The export, which calls no model, is
   byte-identical for the same store.
5. **Status is derived, never set.** Whether a node is `conflict`, `ambiguous`, `stale`, `unchecked`
   or `validated` is computed from facts on the record every time it is written (F2 §4.6).

## What you get at the end

| Artefact | What it is | Where |
|---|---|---|
| The report | Every conflict, grouped, contradictions first, with file and line | printed by `sddc compile`; `.sdd/views/conflicts.md` |
| The graph | Nodes, terms, links, conflict records | `.sdd/` (chapter 8) |
| The views | A map of families × layers, one card per family | `.sdd/views/` |
| The lock | Every model answer, with its cost | `.sdd/lock/` |
| **The export** | A map, one pack per section of the specs, a checklist of every claim id | `.sdd/export/` by default (chapter 9) |

**For scale, two real compiles:**

- **R18** (rel01 code, this repository's specs): 9 files → 845 blocks → **950 nodes**, 1 031 terms,
  **4 199 distinct links**, **381 open conflicts**, in 16 resumable runs.
- **R21 store** (current code, case016 with planted defects): 3 files → 450 blocks → **1 126 nodes**,
  636 terms, **3 595 links**, **233 open conflicts** (67 contradictions), in 3 runs and 860 model calls
  (`graph.meta.json`; register row 174 of the methodology notes). Exported for this lecture on
  2026-11-08 with `--allow-open`: 40 packs, 1 126 checklist items, 3.0× the Markdown's characters
  (354 686 against 118 277, `export.meta.json`).
