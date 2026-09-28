# F7 — Agent export: a code-ready reading format for the spec graph

> **Spec-ID:** F7 · **Status:** 🟡 draft · **Drafted:** 2026-09-25 (rel01 D34)
> **Source:** rel01 S40–S41 · design note
> [`../../design/rel01_design/G3-3-agent-export.md`](../../design/rel01_design/G3-3-agent-export.md)
> (E1–E6, owner answers Q1–Q7 in rel01 D34) · refines
> [`G3-3-traversal.md`](../../design/rel01_design/G3-3-traversal.md) · lecture
> [`docs/lectures/lecture-agent-reads-spec-graph.html`](../../../docs/lectures/lecture-agent-reads-spec-graph.html)
> (non-binding).
> **Depends on:** F1 (blocks, sources, profile) · F2 (node, term and conflict records; `covers`) · F4
> (store, `check_store`, transactions) · F6 (conflict records, adjudications).
> **Governs:** `constitution.md` (§1 id families — no new family; §4 test tiers). **⚑ Drafting
> choices** are marked in §7.

---

## 1. Goal & why

**Write, from a compiled store, the files a coding agent reads to build a codebase from scratch: a
map, one pack per unit of work, and a checklist of every claim. Deterministic, lossless, and with no
model call.**

The compiler stops at this artifact. Generating code from it is a separate step, run by any agent
outside this repository (vision §2 purpose 2). The `.sdd/` store is the compiler's database and is
not a reading format. On R18 it is ≈ 21.6× the Markdown's bytes, has 183 blocks with no node (25 of
them code), 375 family files (246 holding one node), and no node allocated to a component (design note
§2). An agent handed the store would read more text and less information than the Markdown gave it.
The export gives it **everything the Markdown gave, plus four things the Markdown cannot**: a map, a
build order, a checklist of ids, and conflicts settled before reading.

## 2. Scope / non-goals

**In scope:** the `sddc export` command · work units and their order · the unit packs, `MAP.md`,
`CHECKLIST.md` and `export.meta.json` · the conflict gate · the coverage check · the profile keys the
export reads.

**Non-goals**
- ✗ Generating, running or scoring code. That is step 2, the harness (rel01 D34, Q5). Scoring the
  checklist against generated code lives there.
- ✗ Any text written by a model: summaries, definitions, explanations (§4.1 rule 2).
- ✗ A query server (MCP), embeddings, budgeted traversal (the tiers and budgets of G3-3). These are
  later interfaces over the same records.
- ✗ Changing the store. The export only reads `.sdd/`.
- ✗ Fixing term proliferation (build-plan I-65, I-76). Units come from headings, so the export does
  not depend on it.

## 3. Users & triggers

| ID | Trigger | Input | Entry point (code) |
|---|---|---|---|
| T1 | A person runs `sddc export [--out DIR] [--allow-open]` after a compile | The store under `--root` | `sdd_compiler.export.pipeline::export` |
| T2 | A study harness runs the same command once per spec set, then freezes the output | Same | Same |

## 4. Behaviour

### 4.1 Rules that hold throughout

1. **Never less than the Markdown.** Every live block's text appears verbatim in exactly one pack,
   except blocks under an omitted heading (§4.3). This is checked after rendering (§4.9).
2. **Structure, never new words.** Output text is one of: verbatim block text, verbatim node text or
   a verbatim prefix of it, ids, labels, counts, heading text, term names, a conflict's recorded
   rationale and quotes, an adjudication note, or fixed words defined in §5. Model-derived fields
   (layer, modality, kind, relation) appear as labels and are named as derived in `MAP.md`.
3. **Deterministic.** The same store and profile always give byte-identical output: no dates, no
   clocks, no unordered iteration (O2).
4. **No model call.** The export never constructs a backend.

### 4.2 Preconditions

In order; the first failure stops the export, and nothing is written:
1. The store passes F4 `check_store`; otherwise exit 4 naming each problem.
2. **Sources match the graph (⚑ D7).** Every source in `sources.jsonl` still exists with its recorded
   `file_hash`, and no file matching `spec_globs` is missing from it. Otherwise exit 2, naming each
   changed, missing or new file, with the words `run sddc compile first`.
3. **The conflict gate** (§4.6) passes, or `--allow-open` is given.

Pending blocks (not yet atomized) do **not** stop the export. They render verbatim with the tag
`no node (pending)`, and `MAP.md` opens with a banner giving their count.

### 4.3 Units

- A block's **unit key** is `(source, heading_path[:2])`. A block with a shorter heading path uses
  what it has. A node belongs to its block's unit, which is the node's **home**. (rel01 D34, Q4.)
- **Foundation.** Every block whose source matches `export.foundation_globs` belongs to one unit, the
  foundation, whatever its headings. It is always first. If nothing matches, there is no foundation
  pack and `MAP.md` says so.
- **Omitted headings.** A block or node whose `heading_path` contains an element matching one of
  `export.omit_headings` (a case-insensitive substring) is left out of every file. Its counts go to
  `export.meta.json`. In R18 this removes the 39 Traceability nodes.
- A unit with no live, non-omitted block is not emitted.

### 4.4 Order

- Unit X **needs** unit Y when a node homed in X has a `depends_on` link to a node homed in Y, with
  X ≠ Y and neither the foundation.
- Units are ordered topologically over *needs*, Y before X. Ties break by source path, then by the
  unit's first block line.
- **Cycles (⚑ D3).** The strongly connected groups of *needs* are found. A group of two or more units
  is a cycle: it is placed as one step in the order, its units sorted by source position, and it is
  listed in `MAP.md` under *Cycles*. A cycle never fails the export.
- Packs are numbered `00` (foundation) then `01`, `02`, … in this order, zero-padded to the width of
  the largest number and at least two digits.

### 4.5 Pack content

One Markdown file per unit (CT-7.3). Sections always appear in this order, and an empty one prints
`None.`:

1. **Header.** The unit's source and heading, and counts: blocks, nodes by kind, AC labels.
2. **Text.** The unit's blocks, verbatim, in source order. Headings are re-emitted from
   `heading_path` when it changes, at their depth. After each block comes one tag line listing its
   nodes: `↳ N-000412 requirement · MUST · L3 · AC-4.7`, or `↳ no node`, or `↳ no node (pending)`.
   Consecutive `table_row` blocks with the same `table_header` render as one table: the header, the
   separator, then the rows, followed by one tag line per row, numbered. Code blocks render verbatim,
   fences included.
3. **Claims to implement.** Every node homed here of kind `requirement`, `constraint`, `decision` or
   `assumption`, as `- [N-…] <kind> · <modality or —> · <layer> — <node text>`. Each is followed by
   `needs:` with the ids of its `depends_on` targets and their pack number when elsewhere. A decision
   adds `chosen:` and `rejected:` from its `decision` field.
4. **Acceptance criteria.** Every `V` node homed here, as `- [<label or id>] <node text>`, then
   `verifies:` ids, then `test name: test_<label or id with non-alphanumerics as _>_…`.
5. **Constraints in scope.** Every `C` node homed elsewhere whose selector `covers` (F2 D13,
   `model/scope.py`) at least one node homed here, as `- [N-…] (pack NN) <node text>`. Global `C`
   nodes (empty selector) are listed once, in the foundation pack's own section of this name, and every
   other pack ends this section with `plus the global constraints in pack 00`.
6. **Related elsewhere.** For each node homed here, its `refines`, `subsumes` and `duplicates` links to
   nodes homed in other units, as `- N-a <relation> N-b (pack NN) <other node's text>`.
7. **Conflicts.** Per §4.6.
8. **Terms.** The canonical names of the terms used by nodes homed here, each with its aliases, sorted.
   No definitions (rule 2).

The text comes first and the lists after it: long material ahead of the task-shaped part (⚑ D6).

### 4.6 The conflict gate and how conflicts render

A conflict's **human verdict** is the latest adjudication for it (F6 AC-6.20). It is **current**
unless F6 D14 marks it stale (`adjudicate.verdicts_for`).

| Open conflict | Verdict | Gate | Rendering (in both members' packs) |
|---|---|---|---|
| `contradiction` | current `real` | passes | Under **Conflicts**, as `Settled:` with both quotes, the model's rationale and the adjudication note. The note is where the owner states which side holds |
| `contradiction` | current `false` | passes | Nowhere |
| `contradiction` | none, or stale | **blocks** | With `--allow-open`: under **Conflicts**, as `UNSETTLED:` with both quotes and the rationale |
| `duplication` · `subsumption` | not `false` | passes | Under **Related elsewhere** (or in the same pack) as `same as` / `covered by`, never as a question |
| `duplication` · `subsumption` | current `false` | passes | Nowhere |

When the gate blocks and `--allow-open` is absent: exit 3. The message lists each blocking conflict id
with its members (the first 20, then a count), and nothing is written. With `--allow-open`, the export
runs, `MAP.md` opens with a banner giving the count of unsettled contradictions, and
`export.meta.json` lists their ids.

### 4.7 `MAP.md`

The entry point (CT-7.4). In order:
1. Banners, only when they apply: unsettled contradictions (`--allow-open`), pending blocks, no
   foundation.
2. **Read first:** pack `00` and what it holds.
3. **Units in build order:** one row per pack, giving pack file, source and heading, block count,
   claims by kind, AC count, and the packs it needs.
4. **Cycles:** each cycle's packs, or `None.`
5. **Contracts:** every code block and every `CT-…` label → its home pack.
6. **Decisions:** every `decision` node's label (or id) → its home pack.
7. **How to use:** fixed text (CT-7.4). Read the foundation, then each pack in order. Every id in
   `CHECKLIST.md` must end implemented, tested or listed as not done with a reason. Mark code with
   `# spec: <id>`. Fields named *derived* were assigned by the compiler, and the verbatim text wins
   over them.
8. **Counts:** from `export.meta.json`.

### 4.8 `CHECKLIST.md`

Every live, non-omitted node exactly once, grouped under its home pack in build order, as
`- [ ] N-000412 · <kind> · <modality or —> · <layer> · <label or —> · <first 80 characters of its text>…`.
**Every kind is listed, not only MUST (⚑ D8).** In R18, 168 requirement and constraint nodes carry no
modality.

### 4.9 Writing and checking

1. **Output directory.** `--out` defaults to `.sdd/export/`. If it exists, is not empty, and holds no
   `export.meta.json`, the export stops with exit 1 and touches nothing (⚑ D10).
2. Everything is rendered in memory, then the **coverage check** runs: each rendered block's text must
   occur verbatim in its home pack, and every live, non-omitted block must have a home. A failure is
   a defect: exit 4, listing each missing block id, and nothing is written.
3. Files are written to a sibling temporary directory, which then replaces `--out` whole. A failure
   leaves the previous export intact.
4. stdout prints one summary line (pack count, nodes, unsettled contradictions, output path), or the
   CT-7.5 object under `--json`.

## 5. Contracts

**CT-7.1: output layout**

```text
<out>/
  MAP.md
  CHECKLIST.md
  export.meta.json
  packs/00-foundation.md
  packs/<NN>-<spec-slug>--<section-slug>.md
```

`spec-slug`: the spec's parent directory name when the file is `spec.md`, otherwise the file stem.
`section-slug`: `heading_path[1]` (or `[0]`, or `root`), lower-cased, non-alphanumerics collapsed to
`-`, at most 40 characters. Two units with the same slug get `-2`, `-3` in order.

**CT-7.2: profile keys** (an F1 CT-1.4 addition: strict, and unknown keys are errors)

```yaml
export:
  foundation_globs: ["**/vision.md", "**/constitution.md"]   # list of globs; [] = no foundation
  omit_headings: ["Traceability"]                            # case-insensitive substrings
```

**CT-7.3: pack skeleton**

```markdown
# Pack NN — <source> · <heading>
<counts line>

## Text
<blocks verbatim, headings re-emitted, ↳ tag lines>

## Claims to implement
## Acceptance criteria
## Constraints in scope
## Related elsewhere
## Conflicts
## Terms
```

**CT-7.4: `MAP.md` skeleton.** The headings are fixed: `# Map`, then any banners, `## Read first`,
`## Units in build order` (a table), `## Cycles`, `## Contracts`, `## Decisions`, `## How to use`,
`## Counts`. The "How to use" wording is fixed in code and covered by the golden test.

**CT-7.5: `export.meta.json`**

```json
{
  "schema_version": "export/1",
  "compiler_version": "<sddc version>",
  "store_hash": "sha256:<hex over the store files read, in sorted path order>",
  "profile_export": {"foundation_globs": ["…"], "omit_headings": ["…"]},
  "allow_open": false,
  "counts": {
    "packs": 69, "blocks": 845, "blocks_omitted": 0, "blocks_no_node": 0, "blocks_pending": 0,
    "nodes": 950, "nodes_omitted": 39, "checklist_items": 911,
    "unsettled_contradictions": 0
  },
  "unsettled_ids": [],
  "cycles": [["07", "08"]],
  "chars": {"source_markdown": 0, "export_total": 0,
            "packs": {"00-foundation.md": 0}}
}
```

The numbers are illustrative, except that the fields are fixed. `chars.source_markdown` is the
character count of the source files recorded in `sources.jsonl`.

**CT-7.6: exit codes** (F1 CT-1.6 meanings)

| Exit | When |
|---|---|
| 0 | Export written |
| 1 | `--out` is a non-empty directory that is not an export |
| 2 | Sources changed since the last compile |
| 3 | Unsettled contradictions and no `--allow-open` |
| 4 | Store check failed, or the coverage check failed |

## 6. Acceptance criteria

- **AC-7.1** *(lossless)*: **Given** any store built from the fixture specs, **when** the export
  runs, **then** every live block not under an omitted heading appears verbatim in exactly one pack.
  → *property.* (§4.1 rule 1, §4.9)
- **AC-7.2** *(coverage failure is loud)*: **Given** a renderer forced to drop one block, **when** the
  export runs, **then** it exits 4 naming that block id, and the output directory is unchanged.
  → *unit.* (§4.9)
- **AC-7.3** *(deterministic)*: **Given** the fixture store, **when** the export runs twice, **then**
  both outputs are byte-identical, and equal to the stored golden output. → *golden.* (§4.1 rule 3)
- **AC-7.4** *(no model)*: **Given** a profile whose backend would fail if called, **when** the
  export runs, **then** it succeeds and no backend is constructed. → *contract.* (§4.1 rule 4)
- **AC-7.5** *(units)*: **Given** blocks with heading paths of depth 1, 2 and 3, **when** units are
  formed, **then** each block's unit is `(source, heading_path[:2])`, and every block of a
  foundation-glob file is in the foundation. → *unit.* (§4.3)
- **AC-7.6** *(order)*: **Given** random acyclic *needs* relations over units, **when** the order is
  computed, **then** no unit precedes a unit it needs, and ties follow source order. → *property.*
  (§4.4)
- **AC-7.7** *(cycles reported, not fatal)*: **Given** two units that need each other, **when** the
  export runs, **then** it succeeds, the two are adjacent in source order, and `MAP.md` lists them
  under *Cycles*. → *unit.* (§4.4, D3)
- **AC-7.8** *(omitted headings)*: **Given** blocks and nodes under a heading containing
  `Traceability`, **when** the export runs, **then** none appears in any file, and
  `export.meta.json` counts them. → *unit.* (§4.3)
- **AC-7.9** *(checklist complete)*: **Given** any fixture store, **when** the export runs, **then**
  every live, non-omitted node appears in `CHECKLIST.md` exactly once, under its home pack, whatever
  its kind or modality. → *property.* (§4.8, D8)
- **AC-7.10** *(gate blocks)*: **Given** an open `contradiction` with no current human verdict,
  **when** the export runs without `--allow-open`, **then** it exits 3 listing the conflict id and
  members, and writes nothing. → *contract.* (§4.6)
- **AC-7.11** *(override is visible)*: **Given** the same store, **when** the export runs with
  `--allow-open`, **then** both members' packs show the conflict as `UNSETTLED:`, `MAP.md` opens with
  the banner, and `export.meta.json` lists the id. → *unit.* (§4.6)
- **AC-7.12** *(verdicts)*: **Given** contradictions adjudicated `false`, `real`, and `real` but
  stale, **when** the export runs with `--allow-open`, **then** the first appears nowhere, the second
  appears as `Settled:` with its note, and the third appears as `UNSETTLED:`. → *unit.* (§4.6, F6 D14)
- **AC-7.13** *(duplicates are not questions)*: **Given** an open `duplication` between nodes in two
  units, **when** the export runs, **then** it passes the gate and appears as `same as` under
  *Related elsewhere*, not under *Conflicts*. → *unit.* (§4.6)
- **AC-7.14** *(constraints in scope)*: **Given** a `C` node whose selector covers a node in another
  unit, and a `C` node with an empty selector, **when** the export runs, **then** the first is listed
  in that unit's *Constraints in scope*, and the second only in pack 00's. → *unit.* (§4.5)
- **AC-7.15** *(tables and code)*: **Given** a unit with a three-row table and a fenced code block,
  **when** its pack renders, **then** the table appears once with its header and three tag lines, and
  the code block appears verbatim with its fences. → *unit.* (§4.5)
- **AC-7.16** *(pack, map and checklist shapes)*: **Given** the fixture store, **when** the export
  runs, **then** every pack has the CT-7.3 sections in order, `MAP.md` has the CT-7.4 headings in
  order, and file names follow CT-7.1. → *golden.* (CT-7.1, CT-7.3, CT-7.4)
- **AC-7.17** *(meta)*: **Given** the fixture store, **when** the export runs with `--json`, **then**
  stdout and `export.meta.json` validate against CT-7.5, and `chars.export_total` equals the sum of
  the pack sizes. → *contract.* (CT-7.5)
- **AC-7.18** *(stale sources)*: **Given** a spec file edited after the last compile, **when** the
  export runs, **then** it exits 2 naming the file and `run sddc compile first`. → *contract.* (§4.2,
  D7)
- **AC-7.19** *(out directory safety)*: **Given** `--out` pointing at a non-empty directory with no
  `export.meta.json`, **when** the export runs, **then** it exits 1 and every file in that directory
  is unchanged. → *contract.* (§4.9, D10)
- **AC-7.20** *(end to end)*: **Given** the planted fixture repository compiled with the fake
  backend, and its contradictions adjudicated, **when** `sddc export` runs, **then** it exits 0, and
  AC-7.1 and AC-7.9 hold on the output. → *integration.*

## 7. Decisions

- **D1 — Blocks first: packs render verbatim blocks with node tags** (rel01 D34, design note Q2 option
  a). *Why:* node spans cover only part of their blocks (54 % of the spec text in R18), so a
  node-first pack loses text even after adding the blocks that formed no node. *Rejected:* node-first
  (lossy), and nodes plus a link to the source file (the agent would read the prose and bypass the
  export).
- **D2 — Units are `(source, heading_path[:2])`** (rel01 D34, Q4 option a). That gives 68 in R18.
  *Rejected for now:* whole files (too large a reading unit) and adaptive splitting (added only if
  measured pack sizes call for it, §8 Q2). Families are not reading units: 246 of 375 hold one node.
- **D3 — ⚑ A cycle is reported, not fatal.** Its units sit together in source order. *Why:* cross-spec
  `depends_on` links (155 of 396 in R18) come from model verdicts, so a cycle is plausible, and
  refusing the export over it would block the agent for a compiler-side artefact. *Rejected:*
  failing (blocks every export) and silently breaking the cycle (hides it).
- **D4 — Contradictions gate the export; duplications and subsumptions do not** (rel01 D34, Q3 option
  a). *Why:* a contradiction is what an agent resolves silently. A duplication can be shown safely as
  "same as". *Rejected:* warn only (the agent sees unsettled questions as spec), and refusing on any
  open conflict (R18 has 381, most false; the export would be unusable until all were reviewed).
- **D5 — No model-written text, and terms without definitions** (§4.1 rule 2). *Why:* every
  model-written sentence would be a new hallucination source, and the study would attribute it to the
  graph. Definitions stay in the verbatim text where the author wrote them.
- **D6 — ⚑ Text first, lists after.** *Why:* Anthropic's long-context guidance puts long material
  above the task-shaped part (lecture ref [1]). The lists are the part the agent acts on. *Rejected:*
  lists first (they read as the spec, and the text becomes an appendix that gets skimmed).
- **D7 — ⚑ A stale graph is refused.** If sources changed since the last compile, exit 2. *Why:* an
  export of an out-of-date graph looks authoritative and is not (O4). *Rejected:* exporting with a
  warning (a frozen study input could silently differ from its specs).
- **D8 — ⚑ The checklist lists every node, not only MUST / MUST NOT.** *Why:* measured on R18, 147
  requirement and 21 constraint nodes have no modality (168 in all). A MUST-only checklist would hide
  them. *Rejected:* modality filter (misses 168); requirements only (drops decisions, the chosen
  options the code must follow).
- **D9 — Scoring lives in the harness** (rel01 D34, Q5 option a). The compiler defines the checklist
  and the `# spec:` convention. It does not read generated code.
- **D10 — ⚑ The export never deletes a directory it did not write.** A non-empty `--out` without
  `export.meta.json` → exit 1. *Why:* the export replaces its output whole, and pointing it at a
  source tree by mistake must not cost files.
- **D11 — ⚑ Foundation files and omitted headings are profile keys, not hard-coded names.** Their
  defaults are `vision.md` / `constitution.md` and `Traceability`. *Why:* other spec sets name these
  differently. *Cost:* an addition to F1 CT-1.4, the strict profile.

## 8. Open questions

- **Q1 — Global constraints: once in pack 00, or repeated in every pack?** Drafted as once (§4.5),
  because R18 has 32 global `C` nodes, and repeating them in 68 packs adds text an agent has already
  read. Revisit if the pilot shows global rules being missed. Blocks nothing.
- **Q2 — A pack size limit.** None is set, because a number now would be invented. Measure pack sizes
  on the R18 export (CT-7.5 `chars`), then decide whether oversized units split (D2 "adaptive").
  Blocks nothing.

## 9. Traceability

| AC | Test (file::test) | Code |
|---|---|---|
| AC-7.1 | *(to be written)* | `src/sdd_compiler/export/` |
| AC-7.2 | *(to be written)* | |
| AC-7.3 | *(to be written)* | |
| AC-7.4 | *(to be written)* | |
| AC-7.5 | *(to be written)* | |
| AC-7.6 | *(to be written)* | |
| AC-7.7 | *(to be written)* | |
| AC-7.8 | *(to be written)* | |
| AC-7.9 | *(to be written)* | |
| AC-7.10 | *(to be written)* | |
| AC-7.11 | *(to be written)* | |
| AC-7.12 | *(to be written)* | |
| AC-7.13 | *(to be written)* | |
| AC-7.14 | *(to be written)* | |
| AC-7.15 | *(to be written)* | |
| AC-7.16 | *(to be written)* | |
| AC-7.17 | *(to be written)* | |
| AC-7.18 | *(to be written)* | |
| AC-7.19 | *(to be written)* | |
| AC-7.20 | *(to be written)* | |
