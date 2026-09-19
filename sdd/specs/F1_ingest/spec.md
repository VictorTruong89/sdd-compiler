# F1 — Ingest: read static spec files into blocks

> **Spec-ID:** F1 · **Status:** 🟢 approved · **Drafted:** 2026-09-15 · **Approved:** 2026-09-15 ·
> **Revised:** 2026-09-17 (rel01 D26 — batch compiler over static Markdown)
> ⛔ **Coding gated (rel01 D20):** implementation does not start until G2, G3 and G4 are reviewed and
> the rel01 build plan and task list exist.
> **Source discussion:** `sdd/design/rel01_brainstorm.md` S2–S5 · design
> [`../../design/rel01_design/G1-ingest.md`](../../design/rel01_design/G1-ingest.md) (approved, rel01 D19)
> **Governs:** `constitution.md` §6 (stack). Constitution §1–§5 are still placeholders: the id families
> and test-tier names used here are provisional until the constitution adopts them.
> **Decisions applied:** rel01 D3 (Python CLI), D6 (no automatic commits), D12 (P-0, P-6, P-13),
> D21 (command name `sddc`), **D26 (batch over static files)**.
> **Withdrawn by D26, deferred to a later release:** live CLI input (`sddc add`, `--under`), the
> `PostToolUse` hook adapter, and the `--actor` flag. Their acceptance criteria are listed in D10.
> **Extended by:** F3 (`compile` and `atomize` commands, the attention list, exit codes 5–6) ·
> F4 (full `.sdd/` layout and store API) · F5/F6 (the check phase `compile` runs after atomization).

---

## 1. Goal & why

**Turn a set of static Markdown spec files into a stable, addressable inventory of blocks, and say
exactly which blocks are new or changed since the last run.**

A block is a structural unit found by code: a paragraph, a list item, a table body row, or a fenced
code block. A block is **not** an atomic spec. Splitting blocks into claims is a language judgment and
belongs to atomization (F3, rel01 G2.2). F1 hands atomization its exact input: the pending blocks, with
source file, line range, heading path and verbatim text. F1 makes **no model calls**.

Every spec is prose on disk before it is anything else (P-0: prose is the source of truth), so it is
always reviewable, diffable and versioned.

## 2. Scope / non-goals

**In scope**
- `sddc init`, `ingest`, `status`, `blocks`, `show`.
- Deterministic Markdown segmentation into blocks.
- Stable block identity and change detection across runs.
- Storage under `.sdd/`: profile, sources, blocks, runs.

**Non-goals (this spec)**
- ✗ Model calls, atomization, nodes, layers, families → F2, F3.
- ✗ Conflict detection and the conflict report → F6.
- ✗ **Live input, editor or agent hooks, file watching, an actor distinction** — withdrawn by rel01
  D26 and deferred to the release that adds live editing.
- ✗ Non-Markdown inputs; multi-writer merging.
- ✗ Committing anything to git (D6).

## 3. Users & triggers

| ID | Trigger | Input | Entry point (code) |
|---|---|---|---|
| T1 | A person initializes a repository | — | `sdd_compiler.cli::init` |
| T2 | A person compiles a set of spec files | paths, or all sources from the profile | `sdd_compiler.cli::ingest` |
| T3 | Anyone inspects the inventory | flags | `sdd_compiler.cli::status`, `blocks`, `show` |

## 4. Behaviour

- **Repository root:** the nearest parent directory containing `.sdd/`, or `--root DIR`. Every path is
  resolved and must lie inside the root.
- **Source selection:** a file is a spec source only if it matches `profile.spec_globs` and no
  `profile.exclude_globs`. A directory argument expands to its matching files, sorted by path.
- **Segmentation** (deterministic, CommonMark parsing with source line maps):

  | Construct | Result |
  |---|---|
  | Heading | Not a block; updates `heading_path` |
  | Paragraph | Block, kind `paragraph` |
  | List item | Block per item, kind `list_item`. A sub-item is its own block with `parent_relation: nested`; a further paragraph or fence inside the same item keeps its own kind and gets `parent_relation: continuation` (D11) |
  | Table | Block per **body row**, kind `table_row`, carrying the header row as `table_header` |
  | Content inside a blockquote | Keeps its own kind, with `in_blockquote: true` |
  | Fenced code | Block, kind `code`; pending only if `profile.include_code_blocks` is true |
  | HTML comment, front matter, horizontal rule, blank lines | Skipped |

- **Hashing:** `text_hash` = SHA-256 of the block text after normalizing line endings to `\n`,
  trimming trailing whitespace per line, and collapsing runs of blank lines. Case, punctuation and
  inner whitespace are preserved.
- **Identity on re-ingest of a file** (P-6), applied in order:
  1. same `text_hash` and same `heading_path` as an unmatched old live block → keep id, `unchanged`;
  2. same `heading_path` and same ordinal position among blocks under that heading as an unmatched old
     live block → keep id, `changed`;
  3. remaining new blocks → new id, `new`; remaining old blocks → `removed`: the record is kept with
     `removed_run` set, never deleted.
  `new · changed · unchanged · removed` is the **run's delta**. It is reported (CT-1.3 counts, the run
  output) and **not stored on the block** (D13): a stored per-run flag flips back on the next run.
- **Pending set (D13), derived, never stored:** a block is pending when it is live (`removed_run` is
  null), it is not a `code` block unless `include_code_blocks` is true, and its `text_hash` differs from
  its `atomized_hash` (including when `atomized_hash` is null). A block therefore stays pending until
  the atomizer has actually processed its current text, however many runs that takes.
- **Runs are atomic:**
  - every store file is written to a temporary file and renamed only after the whole run succeeds;
  - a lock file in `.sdd/` serializes runs, and a second run waits up to **15 seconds**, then fails
    (D9);
  - each successful run appends one line to `runs.jsonl`.
- **Determinism:** JSON Lines, UTF-8, fixed key order, records sorted by id. Timestamps appear only in
  `runs.jsonl`. Identical sources and identical prior store give byte-identical
  `sources.jsonl` and `blocks.jsonl`.
- **Failures are loud:** every error names the offending path or field and exits non-zero (CT-1.6). No
  store file changes on failure.

## 5. Contracts

**CT-1.1 — Block record** (`.sdd/blocks.jsonl`, one JSON object per line, sorted by `id`):
```json
{
  "id": "B-000123",
  "source": "sdd/specs/F1_ingest/spec.md",
  "kind": "paragraph | list_item | table_row | code",
  "heading_path": ["F1 — Ingest", "6. Acceptance criteria"],
  "lines": [42, 44],
  "text": "exact source text",
  "text_hash": "sha256:<hex>",
  "parent_block": "B-000120 | null",
  "parent_relation": "nested | continuation | null",
  "table_header": "string | null",
  "in_blockquote": false,
  "first_seen_run": "R-0007",
  "last_changed_run": "R-0009",
  "removed_run": "R-0011 | null",
  "atomized_hash": "sha256:<hex> | null"
}
```
Rules:
- `id` has the form `B-` plus 6 or more zero-padded digits, is assigned once, and is never reused.
- `lines` are 1-based and inclusive.
- `text` is the verbatim source slice of those lines.
- `parent_block` is non-null when a block belongs to a list item, and `parent_relation` says how
  (F1 D11): `nested` for a sub-item, `continuation` for a further paragraph or code fence inside the
  same item. Both are null otherwise, and they are always null or non-null together.
- `last_changed_run` is the run that first saw the current text. `removed_run` is set once, by the run
  that no longer found the block, and never cleared (D12).
- `atomized_hash` is written **only by the atomizer** (F3 §4.5): the `text_hash` it last processed to
  completion. Ingest copies it unchanged. It is how pending is derived (D13).

**CT-1.2 — Source record** (`.sdd/sources.jsonl`, sorted by `path`):
```json
{ "path": "sdd/specs/F1_ingest/spec.md", "file_hash": "sha256:<hex>", "last_ingest_run": "R-0009" }
```

**CT-1.3 — Run record** (`.sdd/runs.jsonl`, append-only):
```json
{ "id": "R-0009", "started_at": "ISO-8601 UTC", "command": "ingest | compile",
  "files": ["…"], "counts": {"new": 0, "changed": 0, "unchanged": 0, "removed": 0},
  "cli_version": "string" }
```

**CT-1.4 — Profile** (`.sdd/profile.yaml`, written by `sddc init`, then hand-edited):
```yaml
spec_globs: ["sdd/specs/**/*.md"]
exclude_globs: ["sdd/specs/_templates/**"]
include_code_blocks: false
atomizer: { backend: claude-code, model: haiku }   # read by F3, not by F1
```

**CT-1.5 — Pending output** (`sddc status --json`, stdout):
```json
{ "run": "R-0009",
  "counts": {"sources": 3, "blocks": 41, "pending": 2},
  "pending": [ {"id": "B-000123", "status": "changed", "source": "…", "lines": [42, 44],
                "heading_path": ["…"], "kind": "list_item", "text": "…"} ] }
```
`status` here is derived (D13): `new` when `atomized_hash` is null, `changed` when it is an older hash.

**CT-1.6 — CLI surface**
- `sddc [--root DIR] [--json] <command>`
- `init`
- `ingest [PATH…]` — with no path, every file matching the profile's spec globs
- `status`
- `blocks [--file F] [--pending]`
- `show BLOCK_ID`

Exit codes: `0` success · `1` usage error · `2` input error (missing, unreadable, non-UTF-8, outside
root, not a spec source) · `4` store error (missing `.sdd/`, lock timeout, write failure). Code `3` is
reserved for "conflict" (F6).

## 6. Acceptance criteria

> Test tiers are provisional names pending constitution §4.

**Segmentation**
- **AC-1.1** *(block kinds and positions)* — **Given** a file with 3 paragraphs, a 2-item list and a
  table with a header and 2 body rows, **when** ingested, **then** exactly 7 blocks exist with kinds 3 ×
  `paragraph`, 2 × `list_item`, 2 × `table_row`, and correct `lines` and `heading_path`. → *unit.*
- **AC-1.2** *(heading path)* — **Given** a paragraph under `## A` › `### B`, **when** ingested, **then**
  its `heading_path` is `["A", "B"]` and headings themselves produce no blocks. → *unit.*
- **AC-1.3** *(nested list)* — **Given** a list item containing a nested item, **when** ingested,
  **then** both are blocks and the nested one's `parent_block` is the outer one's id. → *unit.*
- **AC-1.4** *(table row carries header)* — **Given** a table, **when** ingested, **then** every body-row
  block has `table_header` equal to the header row text, and no block is created for the header or the
  delimiter row. → *unit.*
- **AC-1.5** *(blockquote)* — **Given** `> ⚠ Tokens must never be logged.`, **when** ingested, **then**
  one `paragraph` block exists with `in_blockquote: true`. → *unit.*
- **AC-1.6** *(code blocks)* — **Given** a fenced code block and `include_code_blocks: false`, **when**
  ingested, **then** it is stored with kind `code` and is not in the pending set; **and with**
  `include_code_blocks: true` it is pending. → *unit.*
- **AC-1.30** *(a block belongs to its list item)* — **Given** a list item holding a second paragraph
  and a nested sub-item, **when** segmented, **then** the second paragraph is a `paragraph` block with
  `parent_block` naming the item and `parent_relation: continuation`, the sub-item is a `list_item`
  block with `parent_relation: nested`, and a top-level block has both fields null. → *unit.*
- **AC-1.7** *(skipped constructs)* — **Given** front matter, an HTML comment and a horizontal rule,
  **when** ingested, **then** none of them produces a block. → *unit.*

**Identity and change**
- **AC-1.8** *(idempotent)* — **Given** an unchanged file ingested twice, **when** the second run
  completes, **then** it reports 0 new, 0 changed, 0 removed, and `blocks.jsonl` and `sources.jsonl`
  are byte-identical to the first run's. → *property.*
- **AC-1.9** *(insertion keeps ids)* — **Given** a paragraph inserted above existing blocks, **when**
  re-ingested, **then** every pre-existing block keeps its id and the run classifies it `unchanged`,
  and only the inserted block is `new`. → *unit.*
- **AC-1.10** *(edit keeps id)* — **Given** one word changed in a list item, **when** re-ingested,
  **then** that item keeps its id and the run classifies it `changed`, and no other block changes. → *unit.*
- **AC-1.11** *(removal is recorded)* — **Given** a paragraph deleted from a file, **when** re-ingested,
  **then** its record remains with `removed_run` set, and its id is never reused. → *unit.*
- **AC-1.31** *(pending until processed; D13)* — **Given** three blocks ingested and none atomized,
  **when** the unchanged file is ingested again, **then** all three are still pending (`new`); **given**
  the atomizer then records `atomized_hash` for one of them, **then** two are pending; **given** that
  block's text is then edited, **then** it is pending again as `changed`. → *unit.*
- **AC-1.12** *(normalization boundary)* — **Given** a block whose only change is trailing whitespace or
  CRLF line endings, **when** re-ingested, **then** it is `unchanged`; **given** a change of case
  ("must" → "MUST"), **then** it is `changed`. → *unit.*

**Storage and failures**
- **AC-1.21** *(pending output contract)* — **Given** a store with pending blocks, **when**
  `sddc status --json` runs, **then** stdout is exactly one JSON object valid against CT-1.5. →
  *contract.*
- **AC-1.22** *(non-UTF-8 fails atomically)* — **Given** one valid file and one non-UTF-8 file in a
  single `ingest`, **when** run, **then** it exits `2` naming the bad file, and no store file changes. →
  *integration.*
- **AC-1.23** *(outside root)* — **Given** a path outside the repository root, **when** ingested,
  **then** it exits `2`. → *unit.*
- **AC-1.24** *(not initialized)* — **Given** no `.sdd/`, **when** any command except `init` runs,
  **then** it exits `4` with a message naming `sddc init`. → *unit.*
- **AC-1.25** *(init does not overwrite)* — **Given** an existing `.sdd/profile.yaml`, **when**
  `sddc init` runs, **then** it exits non-zero and the profile is unchanged. → *unit.*
- **AC-1.26** *(serialized runs)* — **Given** a run holding the lock, **when** a second run starts,
  **then** it waits up to 15 seconds, and on timeout exits `4` without writing. → *integration.*

## 7. Decisions

- **D1 — Blocks, not sentences.** F1 never splits paragraphs into sentences or claims. *Rejected:*
  sentence splitting in F1 — it is a language judgment, and a code heuristic would pre-empt the
  atomizer's decisions.
- **D4 — Table body rows are blocks, carrying their header.** *Rejected:* whole table as one block —
  acceptance-criteria tables would become one unit, hiding which row changed.
- **D5 — Identity by hash then position, no model** (P-6). *Rejected:* content-hash ids — every edit
  would change the id and break history.
- **D8 — Command name `sddc`** (resolves Q3; rel01 D21). The Python package stays `sdd_compiler` and the
  store directory stays `.sdd/`. *Rejected:* `sdd` — may clash with other tools on PATH;
  `spec-compiler` — long to type.
- **D9 — Lock wait 15 seconds** (resolves Q4).
- **D13 — The block record stores facts; the run's delta and the pending set are derived** (closes
  Q6, option c, 2026-09-18). `status` is removed from CT-1.1; `removed_run` and `atomized_hash` are
  added. *Why:* `status` meant "what the last ingest saw", but pending needs "has the atomizer processed
  this text". They diverge whenever a run ends early: after a call-cap exit (F3 AC-3.5), a block that
  failed its checks twice, or a crash, the next ingest would mark the unprocessed blocks `unchanged` and
  they would **silently never be atomized**. Deriving pending from `atomized_hash` removes that failure
  and makes AC-1.8 hold exactly as written. *Rejected:* (a) rewording AC-1.8 to a fixed point — leaves
  the silent drop in place for T10 to discover; (b) dropping `status` without saying how pending is
  derived. *Cost:* one CT-1.1 change, one F3 sentence, about six tests.
- **D12 — ⚑ A `removed` record never matches again** (found while building T4). Re-adding deleted prose
  produces a **new** id. *Why:* "this id existed and was removed" should stay a fact; resurrecting an id
  would make the history ambiguous and would silently re-attach any later judgments made about the old
  block. *Cost:* re-adding a paragraph that was deleted by mistake costs its id, which is cheap —
  nothing downstream is lost, because a removed block has no nodes.
- **D11 — A block records which list item it belongs to, and how** (closes Q5). `parent_relation` is
  `nested` for a sub-item and `continuation` for a further paragraph or fence inside one item.
  *Why:* a continuation paragraph genuinely belongs to its item, and losing that is a **silent** loss —
  atomized alone, "Model calls go through one interface with two backends" reads as a system-wide
  requirement and can be placed in the wrong family with nothing marking it as suspect. Measured on this
  repository: 3 of 649 list items are affected, so the cost of the fix is small and so is the blast
  radius of getting it wrong. *Rejected:* leaving it (a rare but silent mis-placement); merging an item
  and its continuations into one block — the item's lines are not contiguous when a sub-list sits
  between them, which would break the verbatim-slice property F3's span guard depends on.
  ⚠ Whether the atomizer *uses* the link as context is a separate decision, deliberately deferred to F3
  and measurable (G4 M4).
- **D10 — rel01 is batch-only** (rel01 D26). Withdrawn from this spec and **deferred, not deleted**:
  `sddc add` with `--to`, `--under`, `--text`, stdin and interactive input (old D2, D6, D7 and
  AC-1.13…AC-1.16, AC-1.27…AC-1.29); the `sddc hook post-edit` adapter (old D3 and AC-1.17…AC-1.19);
  the `--actor` flag (AC-1.20). They return with live editing, together with rel01 D13, D16, D18 and
  D25. The inbox, marker format and heading rules are recorded in
  [`../../design/rel01_design/G1-ingest.md`](../../design/rel01_design/G1-ingest.md) **Appendix A**.

## 8. Open questions

*Q6 was closed 2026-09-18 as D13. Q5 was closed 2026-09-18 as D11.*

<!-- Q5, for the record — A continuation paragraph inside a list item (a loose list: one item holding two paragraphs)
  becomes a plain `paragraph` with no parent, because CT-1.1 allows `parent_block` only for nested list
  items. Found while building T3; pinned by a test. Options: leave it (the second paragraph is atomized
  on its own, which may be right); or widen `parent_block` to mean "the block this one continues".
  ⚠ Nothing blocks on it, but the first real spec set with loose lists will show whether atoms lose
  their context this way. -->

*Q1–Q4 were resolved 2026-09-15 as D6–D9; D26 withdrew the features Q1–Q3 concerned (D10).*

## 9. Traceability

| AC | Test (file::test) | Code |
|---|---|---|
| CT-1.4 profile · CT-1.6 CLI surface | `tests/test_profile.py::test_ct_1_4_*` (4) · `tests/test_cli_skeleton.py::test_ct_1_6_*` (4) | `src/sdd_compiler/profile.py` · `cli.py` · `errors.py` |
| AC-1.1 … AC-1.7, AC-1.30 | `tests/test_segment.py` (16) | `src/sdd_compiler/ingest/segment.py` |
| AC-1.8 … AC-1.12 | `tests/test_identity.py` (14) | `src/sdd_compiler/ingest/identity.py` |
| AC-1.26 *(partial: the lock itself)* | `tests/test_store_lock.py::test_ac_1_26_a_second_holder_waits_then_exits_4` (+3) | `src/sdd_compiler/store/lock.py` |
| AC-1.24 *(partial: raised by `load_profile`)* | `tests/test_profile.py::test_ac_1_24_missing_store_is_a_store_error` | `src/sdd_compiler/profile.py` |
| AC-1.8, AC-1.31, AC-1.21 … AC-1.26 | `tests/test_ingest_pipeline.py` (14) | `src/sdd_compiler/ingest/pipeline.py` · `commands.py` · `cli.py` |
| ~~AC-1.21 … AC-1.26~~ *(superseded row)* | `src/sdd_compiler/ingest/pipeline.py` · `src/sdd_compiler/store/` · `src/sdd_compiler/profile.py` |
