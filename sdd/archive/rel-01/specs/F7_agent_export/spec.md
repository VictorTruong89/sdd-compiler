# F7 — Agent export: a code-ready reading format for the spec graph

> **Spec-ID:** F7 · **Status:** 🟢 approved 2026-09-30 · **Drafted:** 2026-09-25 (rel01 D34)
> **Source:** rel01 S40–S41 · design note
> [`../../design/rel01_design/G3-3-agent-export.md`](../../design/rel01_design/G3-3-agent-export.md)
> (E1–E6, owner answers Q1–Q7 in rel01 D34) · refines
> [`G3-3-traversal.md`](../../design/rel01_design/G3-3-traversal.md) · lecture
> [`docs/lectures/lecture-agent-reads-spec-graph.html`](../../../../../docs/lectures/lecture-agent-reads-spec-graph.html)
> (non-binding).
> **Revised:** 2026-09-30 (Phase A of `HANDOVER_code_ready_graph.md`; owner answers: definitions shown,
> one omit key; D12, D13, Q1–Q3) — **approved by the owner 2026-09-30**.
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
export reads (`export.foundation_globs`, and F1's `skip_headings`).

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

1. **Nothing spec-bearing is lost, and nothing is reworded** (relaxed by owner 2026-09-30, D13). The
   export may *exclude* a live block that carries no spec content: a duplicate of another block, or a
   non-spec item (document version or status line, a past reminder, trivial words). Every live block
   that is not excluded appears verbatim in exactly one pack. An exclusion has a recorded reason from
   a closed list (§4.3: `skip_heading`, `real_duplicate`), and is
   counted and listed by block id in `export.meta.json`; none is silent. Checked after rendering
   (§4.9).
2. **Structure, never new words.** Output text is one of: verbatim block text, verbatim node text or
   a verbatim prefix of it, ids, labels, counts, heading text, term names, a term's verbatim
   `definition` (F3 D38: the author's own sentence), a conflict's recorded
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
- **Omitted headings (D11).** The export reads the profile's `skip_headings` (F1 D14, default
  `["Traceability"]`) and its matching rule: equal after lower-casing and removing a leading section
  number, so `9. Traceability` matches. A block whose `heading_path` has a matching element, and any
  node under one, is left out of every file. Its counts go to `export.meta.json`. Ingest already
  deletes such nodes at compile (F1 D14), so on a current store the omitted items are blocks (54 on the
  pilot graph, 0 nodes); a node found under one is still omitted, not an error.
- **Real duplicates (D13, owner 2026-09-30: the agent reads a clean graph).** A block is **excluded**
  (reason `real_duplicate`) when it has at least one node and **every** node homed in it is the *later*
  member of a `duplication` conflict whose current human verdict is `real` (§4.6), the other member
  being homed in a different block. *Later* = the order (source path, then first line). The earlier
  member is kept, so a chain or a cycle of duplicates keeps exactly one. A block with a node that
  duplicates nothing, a subsumption, or a duplication not judged `real` is never excluded; a block
  with no node is never excluded. An excluded block's nodes leave every file; a reference to one (a
  `needs:`, `Related elsewhere` or a checklist link) is rewritten to its kept node. The owner cannot
  choose which side stays: a wrong side is fixed by editing the specs.
- A unit with no live, non-omitted, non-excluded block is not emitted.

### 4.4 Order

- Unit X **needs** unit Y when a node homed in X has a `depends_on` link to a node homed in Y, with
  X ≠ Y and neither the foundation.
- **Specs are ordered, not sections (⚑ D3, revised 2026-09-30, I-96).** The weight of *F needs G*,
  for two different source files, is the number of `depends_on` links from a node homed in F to a node
  homed in G (foundation excluded). The files are put in the order that minimises the total weight of
  links pointing to a *later* file (a "backward need"). Ties go to the order whose file paths compare
  smallest, position by position. With at most 8 files every order is tried; with more, a
  deterministic greedy pass places first the file with the lowest (needs on the remaining files −
  needed by them), ties by path, then adjacent swaps that lower the weight are applied until none does.
- Inside a file, units keep source order. A section that needs a later section of its own spec is not
  reported: sections of one spec cite each other by nature.
- **Backward needs** between files are listed in `MAP.md` under *Needs against the order* (packs and
  link count) and in `export.meta.json` (`backward_needs`). Nothing about the order ever fails the
  export.
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
   adds `chosen:` and `rejected:` from its `decision` field. **A contract node** (its id is a `CT-…`
   id and its block is `code`; F3 D39, F2 D21) is listed as `- [CT-5.1] contract · <layer> — <lead
   line> (fence in Text)`, where the lead line is the first line of the nearest preceding non-code block
   of the same source that starts with `**<id>` (verbatim), or absent. The fence itself is not repeated
   here; it stays once, verbatim, in Text (⚑ D12).
4. **Acceptance criteria.** Every `V` node homed here, as `- [<label or id>] <node text>`, then
   `verifies:` ids, then `test name: test_<label or id with non-alphanumerics as _>_…`.
5. **Constraints in scope (⚑ D14).** Every `C` node homed elsewhere whose selector **names** a
   family, term or category and `covers` (F2 D13, `model/scope.py`) at least one node homed here, as
   `- [N-…] (pack NN) <node text>`. **Broad** `C` nodes — an empty selector, or one that names only
   layers — are listed once, in the foundation pack's own section of this name, a layers-only one as
   `- [N-…] (pack NN) layers L1, L4 — <node text>`; every other pack ends this section with `plus the
   broad constraints in pack 00`. With no foundation, the first pack takes that role and the line names it.
   A contract node in this list shows its lead line, not its fence (D12).
6. **Related elsewhere (⚑ D14).** For each node homed here, its `refines` and `subsumes` links to
   nodes homed in other units, as ids only: `- N-a <relation> N-b (pack NN)`. `duplicates` links, and
   open duplications and subsumptions (§4.6), add the other node's text: `- N-a same as N-b (pack NN)
   <text>`.
7. **Conflicts.** Per §4.6.
8. **Terms (⚑ D14).** The terms used by nodes homed here that have a `definition` or aliases, sorted
   by canonical name, with aliases; a `definition` is shown verbatim as `— defined: "<definition>"`
   (D5). A term with neither is not listed: its name is already in the text.

The text comes first and the lists after it: long material ahead of the task-shaped part (⚑ D6).

### 4.6 The conflict gate and how conflicts render

A conflict's **human verdict** is the latest adjudication for it (F6 AC-6.20). It is **current**
unless F6 D14 marks it stale (`adjudicate.verdicts_for`).

| Open conflict | Verdict | Gate | Rendering (in both members' packs) |
|---|---|---|---|
| `contradiction` | current `real` | passes | Under **Conflicts**, as `Settled:` with both quotes, the model's rationale and the adjudication note. The note is where the owner states which side holds |
| `contradiction` | current `false` | passes | Nowhere |
| `contradiction` | none, or stale | **blocks** | With `--allow-open`: under **Conflicts**, as `UNSETTLED:` with both quotes and the rationale |
| `duplication` | current `real` | passes | The later member's block is excluded (§4.3); nothing is shown for it |
| `duplication` · `subsumption` | not `false`, not a `real` duplication | passes | Under **Related elsewhere** (or in the same pack) as `same as` / `covered by`, never as a question |
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
4. **Needs against the order:** each cross-file need that points to a later pack, as
   `- pack NN needs pack MM (k links)`, or `None.`
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
A contract node's text is its whole fence, so its item shows the lead line of §4.5 in place of the
prefix. Contracts are counted in `export.meta.json` (`counts.contracts`).
**Every kind is listed, not only MUST (⚑ D8).** On the pilot graph, 186 requirement and constraint
nodes carry no modality (166 + 20).

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
```

Headings to omit come from F1's `skip_headings` (D11); the export has no key of its own for them.

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
`## Units in build order` (a table), `## Needs against the order`, `## Contracts`, `## Decisions`, `## How to use`,
`## Counts`. The "How to use" wording is fixed in code and covered by the golden test.

**CT-7.5: `export.meta.json`**

```json
{
  "schema_version": "export/1",
  "compiler_version": "<sddc version>",
  "store_hash": "sha256:<hex over the store files read, in sorted path order>",
  "profile_export": {"foundation_globs": ["…"], "skip_headings": ["…"]},
  "allow_open": false,
  "counts": {
    "packs": 69, "blocks": 845, "blocks_omitted": 1, "blocks_excluded": 1, "blocks_no_node": 0, "blocks_pending": 0,
    "nodes": 950, "nodes_omitted": 0, "contracts": 22, "checklist_items": 949,
    "unsettled_contradictions": 0
  },
  "unsettled_ids": [],
  "excluded_blocks": [{"block": "B-000102", "reason": "skip_heading"},
                      {"block": "B-000212", "reason": "real_duplicate"}],
  "backward_needs": [{"from": "07", "to": "12", "links": 1}],
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
  runs, **then** every live block that is not excluded (F7 §4.1 rule 1) appears verbatim in exactly one pack, and every
  excluded block is listed with its reason in `export.meta.json`.
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
- **AC-7.6** *(order)*: **Given** random weighted *needs* between up to 6 files, **when** the order is
  computed, **then** no other order of the files has a smaller backward weight, ties go to the
  smallest paths, and every file's units stay together in source order; an acyclic relation therefore
  gives a topological order. → *property.* (§4.4)
- **AC-7.7** *(cycles are votes, not failures)*: **Given** file A needing file B by 3 links and B
  needing A by 1, **when** the export runs, **then** it succeeds, B's packs come before A's, and
  `MAP.md` and `export.meta.json` list the one backward need. → *unit.* (§4.4, D3)
- **AC-7.8** *(omitted headings)*: **Given** blocks and nodes under a heading `9. Traceability`
  and `skip_headings: ["Traceability"]`, **when** the export runs, **then** none appears in any
  file, and `export.meta.json` counts them; **and with** `skip_headings: []` they all appear.
  → *unit.* (§4.3, F1 D14)
- **AC-7.9** *(checklist complete)*: **Given** any fixture store, **when** the export runs, **then**
  every live node that is not omitted or in an excluded block appears in `CHECKLIST.md` exactly once, under its home pack, whatever
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
- **AC-7.14** *(constraints in scope)*: **Given** a `C` node whose selector names a family that
  covers a node in another unit, a `C` node with an empty selector, and a `C` node whose selector
  names only layers, **when** the export runs, **then** the first is listed in that unit's
  *Constraints in scope*, and the other two only in pack 00's, the third with its layers. → *unit.*
  (§4.5, D14)
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

- **AC-7.23** *(real duplicates excluded)*: **Given** a `duplication` adjudicated `real` between a
  block in `A.md` and a later block in `B.md` (each with one node), **when** the export runs, **then**
  `B.md`'s block and node appear in no pack or checklist, `A.md`'s appear once, `export.meta.json`
  lists the excluded block id with reason `real_duplicate` and counts it, and a `depends_on` to the
  excluded node is shown as a link to the kept one; **and given** the same duplication judged `false`,
  or stale, **then** both blocks appear. **And** a block with two nodes of which only one is a real
  duplicate is kept. → *unit.* (§4.3, §4.6, D13)
- **AC-7.21** *(contracts)*: **Given** a contract node `CT-1.1` whose block is a fenced `json` block
  under a lead paragraph `**CT-1.1 — Block record** (…)`, **when** the export runs, **then** the fence
  appears once, verbatim, in its home pack's Text; the Claims list has one `CT-1.1` line with the lead
  line and `(fence in Text)`; `CHECKLIST.md` lists it once with the lead line; and `MAP.md`'s Contracts
  index points to its pack. → *unit.* (§4.5, §4.8, §4.7 item 5, D12)
- **AC-7.22** *(definitions)*: **Given** three terms used by a unit — one with a `definition`, one
  with aliases only, one with neither — **when** the pack renders, **then** the first shows its
  definition verbatim, the second its name and aliases, and the third is not listed. → *unit.* (§4.5
  item 8, D5, D14)
- **AC-7.24** *(related, ids only)*: **Given** a `refines` link and a `duplicates` link to nodes in
  other units, **when** the pack renders, **then** the first is listed with ids and pack only, and the
  second with the other node's text. → *unit.* (§4.5 item 6, D14)

## 7. Decisions

- **D1 — Blocks first: packs render verbatim blocks with node tags** (rel01 D34, design note Q2 option
  a). *Why:* node spans cover only part of their blocks (54 % of the spec text in R18), so a
  node-first pack loses text even after adding the blocks that formed no node. *Rejected:* node-first
  (lossy), and nodes plus a link to the source file (the agent would read the prose and bypass the
  export).
- **D2 — Units are `(source, heading_path[:2])`** (rel01 D34, Q4 option a). Measured 2026-09-30 on the pilot graph (`R000023`), over blocks not under `skip_headings`: 73 distinct keys; 15 lie in `vision.md` / `constitution.md` and merge into the foundation, so **58 work units + 1 foundation = 59 packs**. (R18's "68" counted level-2 sections holding nodes, a different measure; it is not comparable.)
  *Rejected for now:* whole files (too large a reading unit) and adaptive splitting (added only if
  measured pack sizes call for it, §8 Q2). Families are not reading units: 246 of 375 hold one node.
- **D3 — ⚑ Order the specs by the fewest backward needs; report what points back** (revised
  2026-09-30, owner, I-96). *Why:* every `depends_on` link is a model verdict, so they are votes, not
  facts. On the pilot graph, ordering sections topologically made one cycle of 35 of 59 packs (the
  sections of one spec cite each other by nature), and even whole files form one cycle; the minimum
  order breaks 42 of 151 cross-file links and reads F2 → F1 → README → F3 → F5 → F4 → F6. *Rejected:*
  a cycle as one step (the drafted rule: the order says nothing for most packs), failing on a cycle,
  and breaking cycles silently.
- **D4 — Contradictions gate the export; duplications and subsumptions do not** (rel01 D34, Q3 option
  a). *Why:* a contradiction is what an agent resolves silently. A duplication can be shown safely as
  "same as". *Rejected:* warn only (the agent sees unsettled questions as spec), and refusing on any
  open conflict (R18 has 381, most false; the export would be unusable until all were reviewed).
- **D5 — No model-written text; a term's definition only when it is the author's** (§4.1 rule 2;
  owner 2026-09-30). *Why:* every model-written sentence would be a new hallucination source, and the
  study would attribute it to the graph. F3 D38 attaches definitions by code as the author's verbatim
  sentence, which meets that reason, so a pack shows it. A term with no such sentence shows none (a
  model never fills the gap). *Yield:* small, 11 of the pilot graph's terms.
- **D6 — ⚑ Text first, lists after.** *Why:* Anthropic's long-context guidance puts long material
  above the task-shaped part (lecture ref [1]). The lists are the part the agent acts on. *Rejected:*
  lists first (they read as the spec, and the text becomes an appendix that gets skimmed).
- **D7 — ⚑ A stale graph is refused.** If sources changed since the last compile, exit 2. *Why:* an
  export of an out-of-date graph looks authoritative and is not (O4). *Rejected:* exporting with a
  warning (a frozen study input could silently differ from its specs).
- **D8 — ⚑ The checklist lists every node, not only MUST / MUST NOT.** *Why:* measured on the pilot graph, 166
  requirement and 20 constraint nodes have no modality (186 in all). A MUST-only checklist would hide
  them. *Rejected:* modality filter (misses 186); requirements only (drops decisions, the chosen
  options the code must follow).
- **D9 — Scoring lives in the harness** (rel01 D34, Q5 option a). The compiler defines the checklist
  and the `# spec:` convention. It does not read generated code.
- **D10 — ⚑ The export never deletes a directory it did not write.** A non-empty `--out` without
  `export.meta.json` → exit 1. *Why:* the export replaces its output whole, and pointing it at a
  source tree by mistake must not cost files.
- **D11 — ⚑ Foundation files are a profile key; omitted headings are F1's `skip_headings`** (owner
  2026-09-30). `export.foundation_globs` defaults to `vision.md` / `constitution.md`. *Why:* other spec
  sets name these differently; and one key for omitted headings means ingest and export never
  disagree (this replaces the drafted `export.omit_headings`). *Cost:* one addition to F1 CT-1.4, the
  strict profile. *Consequence:* the export cannot omit a heading that ingest still atomizes.
- **D14 — ⚑ The lists after the text carry only what changes the build** (owner 2026-09-30, I-95).
  Measured on the first pilot export: the packs were 4.57× the Markdown, and the lists, not the text,
  made the difference — 999 of 1 123 *Constraints in scope* entries came from layers-only selectors
  matched by one shared keyword (F5 D9, a rule built for retrieval, where a judge filters afterwards),
  *Related elsewhere* printed 543 model-judged links with full text in both packs, and 1 608 of 1 968
  *Terms* entries were bare names. *Rejected:* a length cap or text prefix (measured: about 5 %), and
  dropping the lists (they hold the needs, the settled conflicts and the cross-pack rules).
- **D13 — ⚑ The export may exclude duplicate and non-spec blocks, never reword** (owner 2026-09-30,
  relaxes the drafted "never less than the Markdown"). *Why:* a version line, a past reminder or a
  restated duplicate costs reading and adds no claim. *Cost:* exclusion is a judgement; it is allowed
  only by a recorded, closed-list reason, so the coverage check still catches an accidental drop
  (AC-7.2). *Rejected:* exporting everything (keeps the noise); free exclusion (silent loss).
- **D12 — ⚑ A contract's fence is printed once, in Text.** Claims and the checklist show its lead line
  and point to Text. *Why:* repeating a fence in the same pack adds size without adding information
  (size is checked, G3-3 §6). *Rejected:* the fence in Claims too (the handover's first suggestion;
  owner to confirm).

## 8. Open questions

Answered by the owner 2026-09-30: **Q1** (global constraints) — once, in pack 00, as drafted (§4.5);
**Q2** (pack size limit) — none. Both kept below as the record; neither blocks anything.

- **Q1 — ✅ answered (once in pack 00). Global constraints: once in pack 00, or repeated in every pack?** Drafted as once (§4.5),
  because R18 has 32 global `C` nodes, and repeating them in 68 packs adds text an agent has already
  read. Revisit if the pilot shows global rules being missed. Blocks nothing.
- **Q2 — ✅ answered (no limit). A pack size limit.** None is set, because a number now would be invented. Measure pack sizes
  on the R18 export (CT-7.5 `chars`), then decide whether oversized units split (D2 "adaptive").
  Blocks nothing. Sizes are still reported (CT-7.5 `chars`).
- **Q3 — ✅ answered (option a).** Duplicates are excluded after a `real` adjudication (§4.3, D13); a
  profile pattern list (b) is not built.

## 9. Traceability

| AC | Test (file::test) | Code |
|---|---|---|
| AC-7.1 | `tests/test_export_pipeline.py::test_ac_7_1_*, ::test_ac_7_20_*` | `src/sdd_compiler/export/pipeline.py (`_check_coverage`) · packs.py` |
| AC-7.2 | `tests/test_export_pipeline.py::test_ac_7_2_*` | `src/sdd_compiler/export/pipeline.py` |
| AC-7.3 | `tests/test_export_pipeline.py::test_ac_7_3_* (golden: `tests/golden/export/`)` | `src/sdd_compiler/export/` |
| AC-7.4 | `tests/test_export_pipeline.py::test_ac_7_4_*` | `src/sdd_compiler/export/ (imports no backend)` |
| AC-7.5 | `tests/test_export_units.py::test_ac_7_5_*, ::test_foundation_*` | `src/sdd_compiler/export/units.py` |
| AC-7.6 | `tests/test_export_units.py::test_ac_7_6_*` | `src/sdd_compiler/export/units.py (`order_units`)` |
| AC-7.7 | `tests/test_export_units.py::test_ac_7_7_*` | `src/sdd_compiler/export/units.py` |
| AC-7.8 | `tests/test_export_units.py::test_ac_7_8_*, test_export_pipeline.py::test_ac_7_8_*, test_export_profile.py::test_ct_7_2_*` | `src/sdd_compiler/export/units.py · profile.py` |
| AC-7.9 | `tests/test_export_pipeline.py::test_ac_7_9_*, ::test_ac_7_20_*` | `src/sdd_compiler/export/files.py (`checklist`)` |
| AC-7.10 | `tests/test_export_gate.py::test_ac_7_10_*, test_export_pipeline.py::test_ac_7_10_*` | `src/sdd_compiler/export/gate.py · pipeline.py` |
| AC-7.11 | `tests/test_export_pipeline.py::test_ac_7_11_*` | `src/sdd_compiler/export/files.py · packs.py` |
| AC-7.12 | `tests/test_export_gate.py::test_ac_7_12_*, test_export_packs.py::test_ac_7_12_*` | `src/sdd_compiler/export/gate.py · packs.py` |
| AC-7.13 | `tests/test_export_gate.py::test_ac_7_13_*, test_export_packs.py::test_ac_7_13_*` | `src/sdd_compiler/export/gate.py · packs.py` |
| AC-7.14 | `tests/test_export_packs.py::test_ac_7_14_*` | `src/sdd_compiler/export/packs.py (`_scope`)` |
| AC-7.15 | `tests/test_export_packs.py::test_ac_7_15_*` | `src/sdd_compiler/export/packs.py (`_text`)` |
| AC-7.16 | `tests/test_export_pipeline.py::test_ac_7_16_*, ::test_ac_7_3_*` | `src/sdd_compiler/export/` |
| AC-7.17 | `tests/test_export_pipeline.py::test_ac_7_17_*` | `src/sdd_compiler/export/files.py (`META_SCHEMA`)` |
| AC-7.18 | `tests/test_export_sources.py, test_export_pipeline.py::test_ac_7_18_*` | `src/sdd_compiler/export/sources.py` |
| AC-7.19 | `tests/test_export_pipeline.py::test_ac_7_19_*` | `src/sdd_compiler/export/pipeline.py (`_check_out`, `_write_whole`)` |
| AC-7.20 | `tests/test_export_pipeline.py::test_ac_7_20_*` | `src/sdd_compiler/export/ + tests/smart_fake.py` |
| AC-7.21 | `tests/test_export_packs.py::test_ac_7_21_*` | `src/sdd_compiler/export/packs.py` |
| AC-7.22 | `tests/test_export_packs.py::test_ac_7_22_*` | `src/sdd_compiler/export/packs.py (`_terms`)` |
| AC-7.23 | `tests/test_export_gate.py::test_ac_7_23_*` | `src/sdd_compiler/export/model.py (`_real_duplicates`)` |
| AC-7.24 | `tests/test_export_packs.py::test_ac_7_24_*` | `src/sdd_compiler/export/packs.py (`_related`)` |
