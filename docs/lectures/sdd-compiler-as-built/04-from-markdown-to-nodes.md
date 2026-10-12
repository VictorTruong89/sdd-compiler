# 4. From Markdown to nodes

Three levels, from coarse to fine:

```text
 file  ──F1──►  block  ──Q-ATOM──►  atom  ──Q-DESC + code──►  node
 (a .md)        (a paragraph,       (one claim,              (one claim, classified,
                 list item,          as quotes)               linked, checked)
                 table row)
```

## Step 1 — blocks (F1, code only)

A **block** is a structural unit: a paragraph, a list item, a table body row, or a fenced code block.
Headings are not blocks; they become the block's `heading_path`. The parser is `markdown-it-py`, and
nothing at this step reads meaning.

A block record (`.sdd/blocks.jsonl`) holds:

| Field | Example / meaning |
|---|---|
| `id` | `B-000003` — stable across edits (chapter 7) |
| `source`, `lines` | `sdd/specs/F1_ingest/spec.md`, `[28, 28]` (1-based, inclusive) |
| `kind` | `paragraph` · `list_item` · `table_row` · `code` |
| `heading_path` | `["F1 — Ingest: …", "1. Goal & why"]` |
| `text`, `text_hash` | The verbatim slice of the file, and its hash |
| `parent_block`, `parent_relation` | A sub-item is `nested`; a second paragraph inside one list item is a `continuation` |
| `table_header` | For a table row, the header row — context for the model |
| `first_seen_run`, `last_changed_run`, `removed_run` | Facts about its history |
| `atomized_hash` | The text hash when it was last atomized. **A block is pending exactly when this differs from `text_hash`.** |

That last rule is why nothing is ever silently skipped: "pending" is computed from two hashes, not
remembered as a flag that a crashed run might leave wrong (build-plan I-6).

*Layman:* a block is one numbered paragraph of the notebook, photocopied, with a note of the page it
came from.

## Step 2 — atoms (Q-ATOM, the model)

Pending blocks are processed in `(file, first line)` order, in **chunks of 20**. One chunk goes
through every model step before anything from it is kept, so a run stopped mid-chunk loses only that
chunk (and even its paid-for answers stay in the lock).

For each block the model labels every sentence and lists the atoms as verbatim quotes (chapter 3).
Code then:

- **anchors** every quote in the block and computes its character offsets (`spans`) itself — the
  model's idea of where the quote is, is never used;
- checks **coverage**: a sentence with *must, shall, should, may, never, only, required, not allowed*
  must be inside an atom or have a non-claim role;
- keeps the block's `rationale` and `example` sentences as **annotations** for its nodes.

A block whose sentences are all `definition`/`context`/`rationale` **completes and forms no node**,
and the report counts it (R18: between 8 and 49 per run — headings, legends, pointers).

## Step 3 — descriptions (Q-DESC, the model; then code)

Each atom is described (canonical form, seven layer answers, terms, ambiguity — chapter 3). Then code
places it in a layer (chapter 5). If the atom answered *yes* on two layers with **non-overlapping**
quotes, it is really two claims: it is re-asked **once** to split. A block that is one claim by its own
form — a table row, an `AC-` criterion — is never asked to split; it is placed by its first *yes* and
flagged `mixed_layers` (F3 D36).

## Step 4 — terms (Q-TERM, only if needed; then code)

Every term tag is resolved against the **term registry** (`.sdd/terms.jsonl`): an existing name or
alias resolves directly; a new name with look-alikes goes to Q-TERM (chapter 3); a new name with none
becomes a new `proposed` term. Term ids are code: `share link` → `term:share_link`.

## Step 5 — the node (code only)

A **node** is one atomic claim with everything the graph knows about it. Ids:

- a block labelled `**AC-1.4** …` or `**CT-1.4** …` that forms exactly **one** node gives it that id
  (`AC-1.4`), so the author finds the id they wrote;
- otherwise nodes get `N-000001`, `N-000002`, … and every node of a labelled block carries the label
  in its `label` field (`"AC-1.8"`), so "which nodes came from AC-1.8" is a lookup.

A block is **all or nothing**: if any of its atoms fails its checks twice, none of its nodes is
written, and the block stays pending with an `atomize_failed` attention item.

## Anatomy of a real node (R18, `N-000008`)

From `sdd/specs/F1_ingest/spec.md` line 28, which says *"F1 makes **no model calls** …"*:

```json
{
 "id": "N-000008",
 "kind": "constraint",
 "source": {"file": "sdd/specs/F1_ingest/spec.md", "block_id": "B-000003",
            "heading_path": ["F1 — Ingest: read static spec files into blocks", "1. Goal & why"],
            "lines": [28, 28], "spans": [[364, 389]]},
 "text": "F1 makes **no model calls",
 "canonical": {"state": null, "trigger": null, "scope": "F1 ingest", "subject": "F1",
               "modality": "MUST NOT", "response": "make model calls", "quantities": []},
 "terms": [{"term": "term:model_call", "role": "response", "quote": "model calls"}],
 "label": null,
 "primary_term": "term:model_call",
 "layer": "L5",
 "layer_answers": {"Q1": {"answer": "no", "quote": null}, "…": "…",
                   "Q7": {"answer": "yes", "quote": "F1 makes no model calls"}},
 "layer_hint": null,
 "family": "term:model_call",
 "family_rule": "mention",
 "components": [], "scope_selector": null, "verifies": null, "decision": null,
 "annotations": [],
 "keywords": ["calls", "f1", "makes", "model"],
 "ambiguity": [],
 "conflict_ids": ["CF-000043", "CF-000072", "CF-000085"],
 "related_conflict_nodes": ["N-000233", "N-000565", "N-000766"],
 "stale_reasons": [],
 "last_checked_run": "R-000018",
 "flags": [],
 "status": "conflict",
 "judgments": ["J-000003", "J-000025"]
}
```

Field by field — **who filled it in**:

| Field | Meaning | Filled by |
|---|---|---|
| `id` | Node id | code |
| `kind` | requirement · constraint · assumption · verification · decision | model (Q-ATOM) |
| `source` | File, block, heading path, lines, character spans in the block | code (spans from G2) |
| `text` | The claim's own words: the quoted spans, joined with ` … ` | code, from the source |
| `canonical` | State / trigger / scope / subject / modality / response | model (Q-DESC), checked by G4 |
| `canonical.quantities` | Amounts with units, normalized (`30 days` → `2592000 s`) | code |
| `terms` | Resolved term ids with role and quote | model tags → code resolves (Q-TERM if needed) |
| `label` | The `AC-`/`CT-` label of its block, if any | code |
| `layer`, `layer_answers` | One of L0–L5, C, V; the seven answers that decided it | model answers → code decides |
| `layer_hint` | A layer your profile's heading hints suggested — recorded, never obeyed | code |
| `family`, `family_rule`, `primary_term` | The family and which rule chose it | code |
| `scope_selector` | For a `C` node: which families/terms/layers it restricts | code, from Q-DESC's scope terms |
| `verifies` | For a `V` node: the nodes it tests, resolved from ids it cites | code |
| `decision` | For a decision: chosen and rejected options | model (Q-DESC) |
| `annotations` | The block's rationale/example sentences | model roles → code anchors |
| `keywords` | Lower-cased words minus stop words | code |
| `ambiguity` | Why the claim is vague: `vague_term`, `referential`, `missing_modality`, `inferred`, `unplaceable`, `mixed_layers`, `low_confidence_verdict`, … | model (3 kinds) + code (the rest) |
| `conflict_ids`, `related_conflict_nodes` | Open conflict records it is in, and the other members | code, derived from records |
| `stale_reasons` | Why it must be re-checked (a neighbour was edited or deleted) | code |
| `last_checked_run` | The run whose check phase last judged its pairs | code |
| `flags` | `inferred`, `family_disputed`, `pinned_family`, … | code |
| `status` | `conflict` > `ambiguous` > `stale` > `unchecked` > `validated` — first that applies | **derived** from the fields above |
| `judgments` | The lock records (Q-ATOM, Q-DESC answers) that formed it | code |

Read this node as a story: *F1 must not make model calls* (canonical); it is an internal rule, only
checkable white-box (Q7 → `L5`); it is filed under **model call** because that is the only thing it
names (`mention` rule, chapter 5); and it is in **three open contradictions**, each pairing it with a
rule about components that *do* call the model. Whether those are real is exactly what a human
adjudication decides (chapter 2, `sddc conflicts judge`) — the compiler only proposes.

## The toy example, end to end

"A share link must expire 30 days after it is created." becomes, schematically:

| | |
|---|---|
| block | `B-000001`, `paragraph`, heading `Sharing` |
| atom | one `requirement`, quote = the sentence |
| canonical | subject `share link` · `MUST` · response `expire 30 days after it is created` |
| quantity | `30 day` → `2 592 000 s` (code) |
| layer | Q3 yes → **L1** Behaviour (an outsider can check it by using the product) |
| term | `term:share_link`, entity, role subject |
| family | **`term:share_link`** (rule 1, subject) |
| keywords | `created, days, expire, link, share` (computed with the real function) |
| status | `unchecked` until the check phase has judged its pairs |
