# G3.3b — Agent export: a code-ready reading format for the spec graph

> **Status:** APPROVED 2026-09-25 (rel01 D34: rel01; Q2–Q7 as recommended) → [`F7_agent_export`](../../specs/F7_agent_export/spec.md) · **Tier:** design, non-authoritative ·
> **Drafted:** 2026-09-25
> **Refines:** [`G3-3-traversal.md`](G3-3-traversal.md). That note designs a budgeted traversal
> recipe; this one designs the files a coding agent reads when it builds a codebase from scratch. The
> recipe idea stays; its first concrete form is the unit pack (E4).
> **Spec id:** `F7` (rel01 D34). Where this note and F7 differ, F7 wins.
> **Explanation, evidence and references:** lecture
> [`docs/lectures/lecture-agent-reads-spec-graph.html`](../../../docs/lectures/lecture-agent-reads-spec-graph.html)
> (non-binding; this note wins where they differ).

---

## 1. Purpose and boundary

`sddc` stops at the artifact. Generating code from it is a **separate step**, run by any coding agent
(Claude Code on Haiku, Sonnet or Opus; others later), outside this repository's code.

```text
STEP 1: sdd-compiler                          STEP 2: any coding agent (separate)
Markdown specs ──compile──► .sdd/ ──export──► agent export ──► agent ──► code + tests
                                              (frozen, one per spec set)
```

The compiler cannot make the agent write good code. **It decides what the agent reads.** The agent
export is that reading material. The store (`.sdd/`) stays the compiler's database and is unchanged
by this note.

**Goal:** an agent given only the export does at least as well as the same agent given the Markdown
specs, and better where the specs are scattered, duplicated or contradictory.

## 2. Why the rel01 store is not a reading format (measured)

Counted on `trial_01/full-corpus/` (R18) on 2026-09-25.

| Measure | Value | Effect on an agent |
|---|---|---|
| Spec Markdown | 10 files, 164 581 bytes; 845 blocks, 153 925 characters of block text | The baseline |
| Store an agent would read (nodes + edges + terms + conflicts) | 3 553 487 bytes, ≈ 21.6× the Markdown | More text in the window: attention degrades with length |
| Blocks forming no node | 183 (93 paragraphs, 39 list items, 26 table rows, **25 code**), 23 580 characters | Contracts and context missing: the agent must invent formats |
| Node files | 375, of which 246 hold one node | No file name leads to a unit of work |
| Nodes allocated to a component | 0 of 950 | G3-3's `implement(component K)` has no starting point |
| `uses_term` among edges | 2 819 of 4 199 (67 %) | Bookkeeping noise for a reader |
| Nodes with no modality | 407 of 950 | MUST is not separable from explanation |
| Open conflicts | 381 unadjudicated; ≈ 1 in 10 real on an earlier sample | Distractors |
| Traceability nodes | 39 | Leak an earlier implementation |
| Level-2 sections holding nodes | 68 across 9 spec files | A natural unit of work (E2) |
| `depends_on` edges crossing spec files | 155 of 396 | Enough to order units (E2) |

## 3. Principles

1. **Never less than the Markdown.** Every live block's text reaches the export verbatim. Checked, not
   assumed.
2. **Structure, never new words.** The export holds spec text, ids, counts, labels and links. No text
   written by a model is presented as spec text. Model-derived fields (layer, modality, verdicts) are
   labelled as derived.
3. **Small entry point, detail on demand.** One map, then one pack per unit.
4. **One unit fits comfortably.** Sizes are measured in characters (G3-3 issue 2) and reported.
5. **Settled before served.** No unadjudicated contradiction reaches the agent as an open question.
6. **Every obligation has an id to account for.** The agent ends with a checklist, not a feeling.
7. **Deterministic.** Same store → byte-identical export. No model call.

## 4. The export

### 4.1 Layout

```text
<out>/                          default .sdd/export/; rewritten whole on every export
  MAP.md                        entry point (E3)
  CHECKLIST.md                  every obligation id, by unit (E6)
  packs/00-foundation.md        vision + constitution
  packs/<nn>-<spec>-<section>.md   one per work unit, nn = build order (E2, E4)
  export.meta.json              counts, sizes, coverage, graph hash, compiler version
```

Every node id and block id has exactly **one home pack**. Other packs may reference it by id only.
`grep -l "N-000412" <out>/packs/` finds its home in one call.

### 4.2 The six changes

#### E1 — Lossless content

- A pack renders its unit's live blocks **verbatim, in source order**, under their headings. That
  includes blocks that formed no node, code blocks among them (recommended form, Q2).
- Each block carries its node ids as a short tag line (`↳ N-000412 L3 MUST · N-000413 V AC-4.7`), so the
  structure sits on top of the text rather than replacing it.
- Nodes whose `source.heading_path` contains *Traceability* are omitted. Their blocks are dropped too,
  and the count is reported in `export.meta.json`.
- The one pending block (I-84) is included verbatim with a `no node` tag.
- **Coverage check:** every live block except the Traceability ones appears in exactly one pack. If it
  doesn't, the export fails with exit 4 and lists the missing blocks.
- Inputs: `blocks.jsonl` (already stores every block's text, `kind` and `heading_path`) and the node
  records. No new model output.

#### E2 — Work units and their order

- A unit is `(source file, heading_path[:2])`. That gives 68 units in R18, plus the foundation pack for
  `vision.md` and `constitution.md`. Families remain a secondary index and do not decide reading
  units.
- Order: node A in unit X `depends_on` node B in unit Y means X comes after Y. The order is
  topological, with ties broken by source file then line.
- A cycle does not fail the export. Its units are ordered by source position, and the cycle is listed
  in `MAP.md` under *Cycles*, so it is visible, not silent.

#### E3 — `MAP.md`

Computed. No model text. Contents:
- What to read first: the foundation pack.
- The units in build order, each with: pack path, source file and section, counts by layer and
  modality, AC labels, and the contract labels it holds.
- An index of every contract (`CT-…` labels and code blocks) to its home pack.
- The units it depends on.
- Settled decisions (`D…` labels) to their home packs.
- Cycles (E2).
- Export counts and coverage.

#### E4 — Unit packs

Markdown, one per unit. Header: unit, source, counts. Then, in order:
1. **Obligations.** Its nodes with modality MUST or MUST NOT, as `[id] MODALITY text`, plus
   `depends_on` targets as ids (with their home pack when elsewhere).
2. **Constraints in scope.** `C` nodes from other units whose `scope_selector` covers this unit, by id
   and text.
3. **Acceptance criteria.** `V` nodes with label, text and the requirement ids they verify, plus the
   test-name convention (E6).
4. **The unit's text.** Its blocks verbatim, with node tags (E1).
5. **Related from elsewhere.** Nodes in other units linked by `refines`, `subsumes` or `duplicates`, by
   id and text, marked *elsewhere*.
6. **Settled conflicts.** From E5.

`uses_term` links are omitted. Terms used in the unit are listed by canonical name and aliases only (no
definitions; principle 2).

#### E5 — Settle before export

- Export refuses (exit 3, the "conflicts open" code) while any open conflict of kind `contradiction`
  lacks an adjudication. `--allow-open` overrides; the override is written in `MAP.md` and
  `export.meta.json`.
- Adjudicated `false` → omitted.
- Adjudicated `real` → shown in both members' packs with the adjudication note, which is where the
  owner states the winning side.
- Open `duplication` and `subsumption` → shown once, as "same as / covered by N-…", never as
  questions.
- Inputs: `conflicts.jsonl` and `adjudications.jsonl` (F6 AC-6.20), which already exist.

#### E6 — Checklist and trace convention

- `CHECKLIST.md` lists every obligation and every `V` node, grouped by unit in build order, as
  `- [ ] N-000412 (L3 MUST) · pack 07`.
- Convention: code carries `# spec: N-…` beside what satisfies a node, and tests are named after the
  AC label (`test_AC_4_7_…`) or the node id.
- **Scoring the checklist against generated code is step 2 (the harness), not the compiler** (Q5).

### 4.3 Candidate acceptance criteria (for graduation; ids provisional)

| # | Criterion | Tier |
|---|---|---|
| E-1 | Every live non-Traceability block appears verbatim in exactly one pack; otherwise exit 4 naming each missing block | property |
| E-2 | Two exports of the same store are byte-identical | golden |
| E-3 | Units are ordered so no unit precedes a unit it depends on, except inside a reported cycle | property |
| E-4 | Every MUST / MUST NOT node and every `V` node appears in `CHECKLIST.md` exactly once | property |
| E-5 | An unadjudicated open contradiction stops the export with exit 3 unless `--allow-open` is given; the override is recorded | contract |
| E-6 | A conflict adjudicated `false` appears in no pack | unit |
| E-7 | No Traceability node or block appears in any pack; their count is in `export.meta.json` | unit |
| E-8 | `export.meta.json` reports characters per pack and in total, alongside the source Markdown's characters | unit |
| E-9 | Export makes zero model calls | contract |
| E-10 | On R18, the export completes, and E-1 and E-4 hold (integration) | integration |

### 4.4 Effort (estimate, calibrated only by rel01's pace)

| Change | Estimate |
|---|---|
| E1 lossless content + coverage check | 2–3 days |
| E2 units and order | 1 day |
| E3 `MAP.md` | 1 day |
| E4 packs | 2 days |
| E5 settle gate | 0.5 day + adjudication time (corpus-dependent) |
| E6 checklist | 0.5 day |
| **Total** | **≈ 7–8 days of code and tests** |

## 5. Not in scope

| Idea | Why not |
|---|---|
| A query server (MCP) | Files work with any agent now. A server can come later over the same export |
| Model-written summaries or term definitions | They break principle 2 and would become a hallucination source attributed to the graph |
| Budgeted traversal (G3-3 tiers and budgets) | Needed for editing large existing systems, which is out of scope |
| Fixing term proliferation | E2 routes around it by taking units from headings |
| Embeddings | Not needed when the map names everything; similarity misleads on negation |
| Scoring generated code | Step 2, the harness |

## 6. Checks before any code-generation study run

1. **Coverage** (E-1) holds.
2. **Size:** total pack characters and the largest pack are recorded against the Markdown's. A total
   above the Markdown's is a finding to explain before the run.
3. **Pilot:** one task, one model, Markdown versus export. If the export loses, fix the export first.
   The pilot task is excluded from reported results. Whatever the study finds is reported.

## 7. Relation to other documents

- **G3-3-traversal.md:** its manifest idea (§4) becomes `MAP.md` plus `CHECKLIST.md`. Its trace-back
  convention (§3 issue 4) becomes E6. Its fallback for thin graphs (§3 issue 1) is answered by E2:
  units come from headings, not from `allocated_to`.
- **README §2 "For AI agents":** its read list and prompt target the raw store. Once E1–E6 exist,
  they should point to the export instead.
- **G4-measurement.md:** the pilot (§6) and pack sizes are new measurement inputs.

## 8. Decisions needed from the owner

| # | Question | Options | Recommended |
|---|---|---|---|
| **Q1** | Which release builds this? | (a) rel01, before 2026-09-30; (b) rel02 | Recommended (b); **owner chose (a), rel01 D34** |
| **Q2** | Pack text: blocks or nodes first? | (a) **block-first**: verbatim blocks with node tags; lossless by construction; (b) node-first: node texts, with only blocks that formed no node verbatim | **(a)**: node spans cover only part of each block, so (b) loses text even with the leftover blocks added |
| **Q3** | How strict is E5? | (a) refuse on unadjudicated contradictions, with override; (b) warn only; (c) refuse on any open conflict | **(a)**: contradictions are what the agent would resolve silently; duplications can be shown safely |
| **Q4** | Unit granularity | (a) `heading_path[:2]` (68 in R18); (b) whole spec file (9); (c) adaptive: split a section above a size limit | **(a)** now; add (c) only if the size check (§6) shows oversized packs |
| **Q5** | Where does checklist scoring live? | (a) harness only; (b) also `sddc trace` in the compiler | **(a)**: keeps the boundary. `sddc trace` can come later |
| **Q6** | Spec id | (a) take the reserved `F7` as *Agent export*, with traversal budgets deferred inside it; (b) new F8 | **(a)** |
| **Q7** | Command | `sddc export [--out DIR] [--allow-open]` (a sixth rel01-style command) | Yes, unless the owner prefers a `compile --export` flag |
