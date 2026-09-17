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
  | List item | Block per item, kind `list_item`; nested items are separate blocks with `parent_block` |
  | Table | Block per **body row**, kind `table_row`, carrying the header row as `table_header` |
  | Content inside a blockquote | Keeps its own kind, with `in_blockquote: true` |
  | Fenced code | Block, kind `code`; pending only if `profile.include_code_blocks` is true |
  | HTML comment, front matter, horizontal rule, blank lines | Skipped |

- **Hashing:** `text_hash` = SHA-256 of the block text after normalizing line endings to `\n`,
  trimming trailing whitespace per line, and collapsing runs of blank lines. Case, punctuation and
  inner whitespace are preserved.
- **Identity on re-ingest of a file** (P-6), applied in order:
  1. same `text_hash` and same `heading_path` as an unmatched old block → keep id, `unchanged`;
  2. same `heading_path` and same ordinal position among blocks under that heading as an unmatched old
     block → keep id, `changed`;
  3. remaining new blocks → new id, `new`; remaining old blocks → `removed` (kept, never deleted).
- **Pending set:** blocks with status `new` or `changed`, excluding `code` blocks unless opted in.
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
  "table_header": "string | null",
  "in_blockquote": false,
  "status": "new | changed | unchanged | removed",
  "first_seen_run": "R-0007",
  "last_changed_run": "R-0009"
}
```
Rules:
- `id` has the form `B-` plus 6 or more zero-padded digits, is assigned once, and is never reused.
- `lines` are 1-based and inclusive.
- `text` is the verbatim source slice of those lines.
- `parent_block` is non-null only for nested list items.

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
- **AC-1.7** *(skipped constructs)* — **Given** front matter, an HTML comment and a horizontal rule,
  **when** ingested, **then** none of them produces a block. → *unit.*

**Identity and change**
- **AC-1.8** *(idempotent)* — **Given** an unchanged file ingested twice, **when** the second run
  completes, **then** it reports 0 new, 0 changed, 0 removed, and `blocks.jsonl` and `sources.jsonl`
  are byte-identical to the first run's. → *property.*
- **AC-1.9** *(insertion keeps ids)* — **Given** a paragraph inserted above existing blocks, **when**
  re-ingested, **then** every pre-existing block keeps its id with status `unchanged`, and only the
  inserted block is `new`. → *unit.*
- **AC-1.10** *(edit keeps id)* — **Given** one word changed in a list item, **when** re-ingested,
  **then** that item keeps its id with status `changed`, and no other block changes status. → *unit.*
- **AC-1.11** *(removal is recorded)* — **Given** a paragraph deleted from a file, **when** re-ingested,
  **then** its record remains with status `removed`, and its id is never reused. → *unit.*
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
- **D10 — rel01 is batch-only** (rel01 D26). Withdrawn from this spec and **deferred, not deleted**:
  `sddc add` with `--to`, `--under`, `--text`, stdin and interactive input (old D2, D6, D7 and
  AC-1.13…AC-1.16, AC-1.27…AC-1.29); the `sddc hook post-edit` adapter (old D3 and AC-1.17…AC-1.19);
  the `--actor` flag (AC-1.20). They return with live editing, together with rel01 D13, D16, D18 and
  D25. The inbox, marker format and heading rules are recorded in
  [`../../design/rel01_design/G1-ingest.md`](../../design/rel01_design/G1-ingest.md) **Appendix A**.

## 8. Open questions

*None. Q1–Q4 were resolved 2026-09-15 as D6–D9; D26 withdrew the features Q1–Q3 concerned (D10).*

## 9. Traceability

| AC | Test (file::test) | Code |
|---|---|---|
| AC-1.1 … AC-1.7 | *(to be written)* | `src/sdd_compiler/ingest/segment.py` |
| AC-1.8 … AC-1.12 | *(to be written)* | `src/sdd_compiler/ingest/identity.py` |
| AC-1.21 … AC-1.26 | *(to be written)* | `src/sdd_compiler/ingest/pipeline.py` · `src/sdd_compiler/store/` · `src/sdd_compiler/profile.py` |
