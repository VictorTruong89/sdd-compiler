# G1 — Ingest: read static spec files into blocks

> **Status:** APPROVED (rel01 D19) · **rewritten 2026-09-17 for rel01 D26** (batch compiler over static
> Markdown) · **Tier:** design, non-authoritative · **Goal:** rel01 G1
> ([`../rel01_brainstorm.md`](../rel01_brainstorm.md))
> **Graduated to:** [`../../specs/F1_ingest/spec.md`](../../specs/F1_ingest/spec.md) — **the spec wins**
> where the two differ.
> **Stack:** Python CLI. G1 makes **no model calls**; atomization is G2.
> The live-input and hook design that rel01 D26 removed is preserved in **Appendix A**, for the release
> that adds live editing.

---

## 1. What G1 delivers

A command-line tool, `sddc`, that:

1. **reads** a set of static Markdown spec files, or directories of them;
2. **splits** each source into stable, addressable **blocks** (paragraphs, list items, table rows),
   deterministically;
3. **detects change** between runs: which blocks are new, changed, unchanged or removed;
4. **records** everything under `.sdd/` so G2 atomizes only new or changed blocks.

**A block is not an atom.** A block is a structural unit found by code. An atom is a claim, found by
the model in G2. G1 produces G2's input: "these blocks changed; here is their exact text, file, line
range and heading path."

**One trigger:** a person runs the command. No hooks, no watching, no live typing (rel01 D26).

## 2. Design principle carried from pre-rel01

> **P-0 · Prose is the source of truth.** Specs are Markdown files on disk. The graph is compiled from
> them and can always be rebuilt from them.

Consequences that matter here: a spec is reviewable and diffable before it is anything else; one
ingestion pipeline means one set of tests and one set of guards; and the store is a build artifact,
never an input.

## 3. Entry points

```text
  sddc ingest sdd/specs/            sddc ingest sdd/specs/F1_ingest/spec.md
            │                                    │
            └──────────────┬─────────────────────┘
                           ▼
        read → segment → diff against the store → write
```

### 3.1 Commands

| Command | Does |
|---|---|
| `sddc init` | Creates `.sdd/` and `.sdd/profile.yaml` with defaults; refuses to overwrite an existing profile |
| `sddc ingest [PATH…]` | Reads the given files or directories, or every file matching the profile's spec globs; segments, diffs, stores |
| `sddc status` | Sources, block counts, and the pending (new/changed) set |
| `sddc blocks [--file F] [--pending]` | Lists blocks, for inspection and tests |
| `sddc show BLOCK_ID` | One block: exact text, file, lines, heading path |

**Global flags:** `--json` for machine-readable output (tests, scripts, later measurement).
`--root DIR` selects the repository; the default is the nearest parent containing `.sdd/`.

## 4. Segmentation — deterministic rules

**Parser:** a CommonMark-conformant Markdown parser that reports source line ranges per block.
Candidate: `markdown-it-py`, whose tokens carry line maps (to verify at implementation).

| Markdown construct | Becomes | Rule |
|---|---|---|
| Heading | **Not a block**; updates the heading path | `heading_path` = enclosing heading texts |
| Paragraph | One block, kind `paragraph` | |
| List item | One block per item, kind `list_item` | Nested items are separate blocks with `parent_block` |
| Table | One block per **body row**, kind `table_row` | The header row travels with each row as `table_header` |
| Blockquote | Blocks keep their own kind, plus `in_blockquote: true` | Callouts such as `> ⚠ …` are often normative |
| Fenced code | Kind `code`, stored but not atomized unless the profile opts in | JSON contracts inside specs matter |
| HTML comment, front matter, horizontal rule, blank lines | Skipped | |

**Sentence splitting is not done in G1.** Splitting a paragraph into claims is a language judgment and
belongs to G2's atomizer.

## 5. Data model

### 5.1 Block record

```yaml
block:
  id: B-000123                  # assigned once, never recomputed (§5.3)
  source: sdd/specs/F1_ingest/spec.md
  kind: paragraph | list_item | table_row | code
  heading_path: ["F1 — Ingest", "6. Acceptance criteria"]
  lines: [42, 44]               # 1-based, inclusive, computed by code
  text: "<exact source text>"
  text_hash: sha256:…           # of normalized text (§5.2)
  parent_block: B-000120 | null
  table_header: "| AC | Test | Code |" | null
  in_blockquote: false
  status: new | changed | unchanged | removed
  first_seen_run: R-0007
  last_changed_run: R-0009
```

### 5.2 Normalization for hashing

Normalize only what never changes meaning: line endings to `\n`, trailing whitespace trimmed per line,
runs of blank lines collapsed. **Case, punctuation and inner whitespace are preserved** — "MUST" versus
"must", or "5GB" versus "5 GB", are real edits.

### 5.3 Stable identity across edits

On re-ingest of a file, in order:

1. **Exact match:** same `text_hash` and `heading_path` → keep the id, `unchanged`, even if it moved.
2. **Positional match:** same heading path and ordinal position → keep the id, `changed`.
3. **Anything left:** new blocks get new ids (`new`); unmatched old blocks are `removed` (kept, so
   change detection stays honest across runs — unlike *nodes*, which are deleted; rel01 D24).

Deterministic, no model. A block split in two shows up as `changed` + `new`; a merge as `changed` +
`removed`.

### 5.4 Storage (subset of P-13)

```text
.sdd/
  profile.yaml        spec globs, code-fence opt-in, atomizer settings for G2
  sources.jsonl       one line per source file: path, file hash, last ingest run
  blocks.jsonl        one line per block, sorted by id
  runs.jsonl          one line per run: id, time, command, files, counts, CLI version
```

JSON Lines, fixed key order, sorted, UTF-8 — the same input gives byte-identical files. The full
`.sdd/` layout, once nodes exist, is G2.3's (F4).

### 5.5 Profile

```yaml
spec_globs: ["sdd/specs/**/*.md"]
exclude_globs: ["sdd/specs/_templates/**"]
include_code_blocks: false
atomizer:                 # used by G2; recorded here so runs are reproducible
  backend: claude-code    # claude-code (default) | anthropic-api  (rel01 D7)
  model: haiku
```

## 6. Guards and failure behaviour

| Situation | Behaviour |
|---|---|
| File not found, not UTF-8, or unreadable | Error naming the file; exit non-zero; nothing written |
| Path outside the repository root | Error |
| Path not matching `spec_globs` | Error, listing the globs |
| `.sdd/` missing | Error: "run `sddc init`" |
| Concurrent runs | A lock file in `.sdd/`; a second run waits 15 s, then errors |
| Partial failure mid-run | Write to temporary files, rename at the end: a run is all-or-nothing |

## 7. What G1 hands to G2

`sddc status --json` returns the pending set: for each new or changed block, its id, status, source,
line range, heading path and exact text. G2's atomizer consumes exactly this and never re-reads files
on its own.

## 8. Out of scope for G1

Model calls · atomization · layers and families · conflict detection · non-Markdown inputs ·
multi-writer merging · **live input, hooks and file watching** (rel01 D26 — Appendix A).

## 9. Acceptance criteria

Superseded by [`../../specs/F1_ingest/spec.md`](../../specs/F1_ingest/spec.md) §6 (18 criteria:
segmentation, identity and change, storage and failures).

## 10. Open questions

None. The four G1 questions were resolved in F1 D6–D9; two of them (the inbox, the target heading)
concerned features rel01 D26 deferred, and are recorded in Appendix A.

---

# Appendix A — Deferred: live input and editor/agent integration

> ⛔ **Not part of rel01** (D26). Kept because this is the design for the release that adds live
> editing, and because it was reviewed and approved before the simplification (rel01 D19).

**The principle that survives:** live input is **written to a Markdown file first**, then ingested
through the same pipeline as any file. A spec never exists only in the graph.

**Command:** `sddc add [--to FILE] [--under HEADING] [--text TEXT | -]`
- appends one entry: a blank line, `<!-- sddc:add <UTC timestamp> -->`, then the text verbatim;
- `--to` defaults to a single inbox file named in the profile, and must match a spec glob;
- `--under` places the entry at the end of a named heading's section: exact, case-sensitive match, a
  heading path (`A > B`) for disambiguation, and an error on no match or an ambiguous match;
- empty input is an error.

**Editor and agent integration:**
- a `PostToolUse` command hook on `Edit|Write` runs a hook adapter that re-ingests an edited spec file;
- the adapter exits 0 for non-spec files and prints nothing;
- an AI agent adds specs by editing the inbox file with Edit/Write, so the hook always fires;
- a child-process marker (`SDD_COMPILER_CHILD=1`) stops a hook → CLI → `claude -p` → hook loop.

**Companion decisions to revive with it:** rel01 D13 (stop at the first conflict for an agent), D16
(`--actor ai|human`), D18 (the hook is the agent's notification channel), D25 (the AI fix loop with
attempts and escalation), and F1's withdrawn criteria listed in F1 D10.
