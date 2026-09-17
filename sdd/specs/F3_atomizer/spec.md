# F3 — Atomizer: pending blocks → nodes, with Haiku and deterministic guards

> **Spec-ID:** F3 · **Status:** 🟢 approved · **Drafted:** 2026-09-15 · **Approved:** 2026-09-15 (rel01 D23) ·
> **Revised:** 2026-09-17 (rel01 D26 — batch compiler over static Markdown)
> ⛔ **Coding gated (rel01 D20).**
> **Source:** rel01 sub-goal G2.2 · approved proposals P-1, P-2, P-4, P-5, P-6 in
> [`../../design/rel01_design/core-working-principle.md`](../../design/rel01_design/core-working-principle.md)
> §1.2, §3 · rel01 D7 (two model backends), D8 (Haiku atomizes and forms nodes), **D26 (batch)**.
> **Withdrawn by D26, deferred:** the hook trigger, the `--actor` stop rule and the AI fix loop
> (old D4). See D8 below.
> **Depends on:** F1 (pending blocks, CT-1.5) · F2 (node, term, link contracts; placement).
> **⚑ Drafting choices** are marked in §7.

---

## 1. Goal & why

**Turn each pending block into atomic nodes that conform to F2.** Haiku answers small, closed,
schema-bound questions. Code checks every answer before accepting it, records it, and does
everything else: offsets, quantities, placement and identity.

The atomizer is the **only non-deterministic component**. Isolating it here keeps every other spec
testable without a model. The judgment lock makes rebuilds reproducible: accepted answers are
replayed, not re-asked.

## 2. Scope / non-goals

**In scope**
- Model interface with two backends.
- Question kinds `Q-ATOM`, `Q-DESC`, `Q-TERM`.
- Check-immediately and re-ask rule.
- Guards G2–G6 (G1 is F1 segmentation).
- Quantity normalization.
- Judgment lock.
- Node alignment across block edits.
- Term registry updates.
- An attention list of items a person must decide, and the review commands.
- The `sddc atomize` and `sddc compile` commands, and the per-node hand-off point used by F5/F6.
- Usage logging.

**Non-goals**
- ✗ `Q-PAIR` and conflict decisions → F6.
- ✗ Candidate retrieval → F5.
- ✗ Storage layout and views → F4. F3 writes through F4's store API.
- ✗ Clarifying questions to the author (rel01 scope: ambiguity is a status).
- ✗ **Hook triggers, an actor distinction, and any stop-and-fix loop** — withdrawn by rel01 D26 and
  deferred to the release that adds live editing.

## 3. Users & triggers

| ID | Trigger | Entry point (code) |
|---|---|---|
| T1 | A human runs `sddc atomize` or `sddc compile [PATH…]` | `sdd_compiler.cli::atomize`, `compile` |
| T2 | A person resolves items from the attention list | `sdd_compiler.cli::review` |

## 4. Behaviour

### 4.1 Model interface — one interface, two backends (D7)

| Backend | Invocation | Auth |
|---|---|---|
| `claude-code` (default) | Subprocess `claude -p --model <profile model> --output-format json --json-schema <schema>`; answer read from `structured_output` | Claude Code login |
| `anthropic-api` (optional) | Anthropic SDK call with the same schema and prompt | `ANTHROPIC_API_KEY`, loaded from `.env` **only inside this backend** |

**Child-process rules for `claude-code`:**
- set `SDD_COMPILER_CHILD=1`;
- **remove `ANTHROPIC_API_KEY`** from the child environment, unless the profile sets
  `atomizer.pass_api_key: true`;
- never pass `--bare`;
- run `claude --version` once per run and record it.

**Every call records:** backend, model as reported, CLI version, input and output tokens, cache tokens
(when reported), estimated cost (when reported), duration, exit status.

A per-run cap `atomizer.max_calls_per_run` stops the run with exit `5` when reached. Remaining blocks
stay pending.

### 4.2 Questions

| Kind | Input | Output (schema-bound) |
|---|---|---|
| **Q-ATOM** | One pending block: text, kind, heading path, table header | Sentence roles; atoms, each `{kind, quotes[]}` with **verbatim quotes**; non-normative sentences labelled with their role |
| **Q-DESC** | One atom: its quotes and its block text | Canonical fields (F2 CT-2.1 `canonical`, without normalized quantities); layer answers Q1–Q7 with quotes; term tags `{name, kind, role, quote}`; ambiguity candidates `{kind, quote}`; for `C` a scope description; for `V` the text of what it verifies; for `decision` chosen, rejected with reasons |
| **Q-TERM** | One proposed term plus up to N existing terms with similar names | `same: term id` · `different` · `unsure`, with a reason |

- The atom tests T1–T4 (P-2), the role list (P-3) and the canonical form (P-4) are stated in the
  question text.
- Each question has a versioned schema, e.g. `q-atom/1`.

### 4.3 Check-immediately rule (P-1)

1. Validate each answer as soon as it arrives, before any dependent question is asked.
2. On failure, re-ask **once**, including the specific failed check in the question.
3. On a second failure, **no node is created**:
   - the block is recorded as `atomize_failed` with the failed check;
   - the block stays pending;
   - an item is added to the review queue.

### 4.4 Guards (P-5)

| Guard | Applied to | Check | On failure |
|---|---|---|---|
| **G2** Span anchoring | Q-ATOM, Q-DESC quotes | Every quote occurs verbatim in the block text. Code computes the offsets. A quote occurring more than once anchors to the first occurrence not already claimed by another atom in the same block | Re-ask |
| **G3** Coverage | Q-ATOM | Every sentence of the block containing a normative word (`must, shall, should, may, never, only, required, not allowed`) is covered by an atom quote or labelled non-normative | Re-ask |
| **G4** No injection | Q-DESC | Every term name and every quantity in the canonical fields appears in the atom's quotes, directly or as a registered alias | Node gets flag `inferred` and ambiguity `inferred`, plus a review-queue item |
| **G5** Schema | All | The answer validates against its schema version | Re-ask |
| **G6** Weak words | Atom quotes | Words from `profile.weak_words` add ambiguity `vague_term` with the matched quote | — (fact, not failure) |

- **Placement T3** (F2 AC-2.2) returning `split_required` counts as a Q-ATOM failure for that block:
  re-ask Q-ATOM once with both quotes.
- **Quantities** are parsed from the quotes by code into a value and unit. They are normalized for
  time (to seconds), size (to bytes; KB = 1000, KiB = 1024) and count/percent (unchanged). A quantity
  the parser cannot read adds ambiguity `unbounded_quantity`.

### 4.5 Forming a node

For each validated atom:
1. Resolve term tags against the registry. Exact names and aliases resolve directly.
2. Otherwise ask Q-TERM:
   - `different` → create a `proposed` term;
   - `same` or `unsure` → review-queue item, and ambiguity `pending_review` on the node until reviewed.
3. Compute quantities, `keywords`, spans and lines.
4. Call F2 placement (layer, family, components).
5. Create `uses_term` links (provenance `code`).
6. Set `last_checked_run: null`. Status derives to `unchecked` or `ambiguous` (F2).
7. Write through F4 atomically per block: either all nodes from a block are written, or none.

### 4.6 Identity across edits (P-6)

When a `changed` block is re-atomized, new atoms are aligned to the block's existing active nodes:
1. by span overlap of quotes on the new block text with the old nodes' `text`;
2. then by equal `canonical.subject` and `canonical.response`.

| Alignment | Result |
|---|---|
| `unchanged` | Same id; record untouched except `source.lines` |
| `edited` | Same id; fields replaced; every judged link touching it gains a `stale_reasons` entry |
| `split` | Old id kept by the best-overlapping atom; others get new ids |
| `merged` | Best-overlapping old id kept; other old nodes deleted (F2 §4.9) |
| `new` | New id |
| `removed` | Old node deleted (F2 §4.9) |

- A `removed` block deletes all its nodes.
- Alignments are applied automatically, recorded with `confirmed: auto`, and listed in the run report
  (⚑ D3).

### 4.7 Judgment lock (P-1)

- Every accepted answer is appended to the lock as CT-3.2.
- Before asking, the atomizer computes `input_hash = sha256(question kind + schema version + canonical
  JSON input)`. A lock hit **replays** the stored answer through the same guards, with no model call.
- `sddc compile --no-replay` forces asking.
- With the same sources, lock and profile, `compile` produces byte-identical node, term and link records
  (F4).

### 4.8 Order of processing, and where the checks run

- Pending blocks are processed in `(source path, first line)` order, so a run is reproducible.
- In rel01 the checks (F5 retrieval, F6 judgment) run as a **separate phase after atomization**
  (F6 §4.1), not per node, so every node is visible to every pair.
- The pipeline keeps a per-node extension point `on_node_formed(node)`, unused in rel01. It is where
  live editing would hook checking back into atomization. ⚠ Not a Claude Code hook: rel01 has none.
- **The run never stops at a conflict** (rel01 D26). Every conflict found is recorded on the nodes and
  in the graph's conflict records, and the run continues to the last pending block.
- The run ends with one report (§4.10): blocks processed, nodes formed, model calls and usage, every
  conflict found, and every attention item opened.

### 4.9 Attention list — items a person must decide

Some findings cannot be settled by code and, in a batch run, are not settled by anyone mid-run. They
are recorded as items (CT-3.3) and listed at the end of the run:

| Type | Raised when | Effect on the node |
|---|---|---|
| `inferred_node` | G4 found canonical content that is not in the source | flag `inferred`, ambiguity `inferred` |
| `term_same` · `term_unsure` | Q-TERM proposed merging a term with an existing one | ambiguity `pending_review` |
| `atomize_failed` | A block failed its checks twice (§4.3) | no node; the block stays pending |

Conflicts are **not** attention items in rel01: they live on the nodes and in the conflict records
(F2, F4) and are reported by F6.

**Commands:**
- `sddc review list [--json]` · `sddc review show ITEM`;
- `sddc review accept ITEM` — confirm a term merge, a proposed term or an inferred node;
- `sddc review reject ITEM` — reject: the node is deleted, or the terms stay distinct.

Accepting or rejecting updates the affected nodes' facts, and their status is re-derived. An item whose
cause disappears on a later run closes automatically with `state: resolved`.

### 4.10 Commands and exit codes (extends F1 CT-1.6)

- `sddc atomize [--no-replay]` atomizes all pending blocks.
- `sddc compile [PATH…] [--no-replay]` — **the one command of rel01**: F1 ingest over the paths (or all
  spec sources), then atomize, then the F5/F6 checks, then the report.

| Code | Meaning |
|---|---|
| `0` | Success |
| `3` | The run completed and the graph holds open conflicts (F6). The graph is written; the report lists them |
| `5` | Call cap reached |
| `6` | Model backend unavailable (e.g. `claude` not found, authentication failure) |

F1 codes also apply.

## 5. Contracts

**CT-3.1 — Q-ATOM answer schema `q-atom/1`**
```json
{ "sentences": [{"quote": "…", "role": "requirement | constraint | assumption | verification | decision | definition | rationale | example | context | open_question"}],
  "atoms": [{"kind": "requirement | constraint | assumption | verification | decision", "quotes": ["…"]}] }
```

**CT-3.2 — Judgment record** (`.sdd/lock/<kind>.jsonl`)
```json
{ "id": "J-000321", "kind": "q-atom | q-desc | q-term", "schema_version": "q-desc/1",
  "input_hash": "sha256:<hex>", "backend": "claude-code | anthropic-api", "model": "string",
  "cli_version": "string | null", "answer": {}, "attempts": 1,
  "usage": {"input_tokens": 0, "output_tokens": 0, "cache_read_tokens": 0, "cost_usd": null},
  "duration_ms": 0, "confirmed": "auto | author", "run": "R-0011" }
```

**CT-3.3 — Review item** (`.sdd/review.jsonl`)
```json
{ "id": "RV-000007",
  "type": "inferred_node | term_same | term_unsure | atomize_failed",
  "subject": "N-000042 | term:… | B-000123",
  "detail": "…",
  "source": {"file": "…", "lines": [42, 44], "quotes": ["…"]},
  "state": "open | accepted | rejected | resolved",
  "opened_run": "R-0011", "closed_run": "R-0014 | null" }
```

**CT-3.4 — Profile additions** (F1 CT-1.4)
```yaml
atomizer:
  backend: claude-code         # claude-code | anthropic-api
  model: haiku
  pass_api_key: false
  max_calls_per_run: 200
  timeout_s: 120
weak_words: [fast, quickly, appropriate, user-friendly, as needed, etc, robust, simple]
```

## 6. Acceptance criteria

> Tests that need a model use a **recorded fake backend** that returns scripted answers. No test calls a
> live model. Tiers are provisional.

**Backend**
- **AC-3.1** *(child environment)* — **Given** `ANTHROPIC_API_KEY` in the parent environment and
  `pass_api_key: false`, **when** the `claude-code` backend spawns a call, **then** the child
  environment has `SDD_COMPILER_CHILD=1` and no `ANTHROPIC_API_KEY`, and the command line contains
  `-p`, `--model haiku`, `--output-format json`, `--json-schema`, and not `--bare`. → *unit.*
- **AC-3.2** *(.env confined)* — **Given** a `.env` with keys, **when** the `claude-code` backend runs,
  **then** `.env` is never read; **when** the `anthropic-api` backend runs, **then** the key is read from
  `.env`. → *unit.*
- **AC-3.3** *(usage recorded)* — **Given** a fake response carrying usage and cost, **when** accepted,
  **then** the judgment record contains them, plus the backend, model and CLI version. → *unit.*
- **AC-3.4** *(backend unavailable)* — **Given** `claude` not on PATH, **when** `atomize` runs, **then**
  it exits `6` and no store file changes. → *integration.*
- **AC-3.5** *(call cap)* — **Given** `max_calls_per_run: 2` and three pending blocks needing calls,
  **then** the run exits `5`, completed blocks are written, and the rest stay pending. → *integration.*

**Guards and re-ask**
- **AC-3.6** *(G2 re-ask then fail)* — **Given** a fake Q-ATOM answer quoting text absent from the
  block, twice, **then** the question is asked exactly twice, the second time including the failed
  check; no node is written; the block stays pending; an `atomize_failed` review item exists. →
  *unit.*
- **AC-3.7** *(G2 offsets by code)* — **Given** a quote occurring twice in the block and two atoms
  quoting it, **then** they anchor to the first and second occurrences respectively. → *unit.*
- **AC-3.8** *(G3 coverage)* — **Given** a block with two "must" sentences and an answer covering one,
  **then** a re-ask occurs naming the uncovered sentence. → *unit.*
- **AC-3.9** *(G4 injection)* — **Given** canonical fields containing "AES-256" absent from the quotes,
  **then** the node has flag `inferred`, ambiguity `inferred`, status `ambiguous`, and an
  `inferred_node` review item. → *unit.*
- **AC-3.10** *(G5 schema)* — **Given** an answer missing `atoms`, **then** a re-ask occurs. → *unit.*
- **AC-3.11** *(G6 weak words)* — **Given** "uploads must be fast" and `fast` in `weak_words`, **then**
  the node has ambiguity `vague_term` quoting "fast". → *unit.*
- **AC-3.12** *(T3 split re-ask)* — **Given** Q-DESC answers producing `split_required`, **then** Q-ATOM
  is re-asked once for that block with both quotes. → *unit.*
- **AC-3.13** *(quantities)* — **Given** quotes "30 days", "5 GB", "5 GiB" and "15%", **then** the
  normalized values are 2,592,000 s, 5,000,000,000 bytes, 5,368,709,120 bytes, and 15 percent;
  **given** "a few minutes", **then** ambiguity `unbounded_quantity`. → *unit.*

**Forming, identity, lock**
- **AC-3.14** *(node formed)* — **Given** valid fake answers for one requirement, **then** one node
  conforming to F2 CT-2.1 exists with layer, family, `uses_term` links, `last_checked_run` null and
  status `unchecked`. → *integration.*
- **AC-3.15** *(term resolution)* — **Given** a tag matching a registered alias, **then** no Q-TERM is
  asked; **given** Q-TERM answer `unsure`, **then** a `term_unsure` review item exists and the node has
  ambiguity `pending_review`. → *unit.*
- **AC-3.16** *(block all-or-nothing)* — **Given** a block yielding three atoms where the third fails
  twice, **then** none of the three nodes is written. → *integration.*
- **AC-3.17** *(edited keeps id, marks stale)* — **Given** a changed block whose single atom aligns by
  span overlap to an existing node that has a judged link, **then** the id is kept, alignment `edited`,
  and the link's other end gains a `stale_reasons` entry. → *integration.*
- **AC-3.18** *(split and removed)* — **Given** a block that previously produced one node and now
  produces two atoms, **then** one keeps the old id and one is new; **given** a removed block, **then**
  its nodes are deleted, together with their links, and each neighbour that had a judged link to them
  gains a `stale_reasons` entry. → *integration.*
- **AC-3.19** *(replay)* — **Given** a completed compile, **when** compile runs again with no source
  change and a fake backend that fails on any call, **then** it succeeds with zero model calls and
  byte-identical node, term and link files. → *property.*
- **AC-3.20** *(no-replay)* — **Given** `--no-replay`, **then** every question is asked even with lock
  hits. → *unit.*

**Hand-off and reporting**
- **AC-3.21** *(never stops at a conflict)* — **Given** three pending blocks and a check phase that
  reports a conflict involving a node from the first block, **when** `compile` runs, **then** all three
  blocks are atomized, the check phase runs over every node, and the report lists the conflict. →
  *integration.*
- **AC-3.22** *(one report)* — **Given** a run with two conflicts and one attention item, **then** the
  report names both conflicts, the item, the blocks processed, the nodes formed and the model usage;
  the exit code is `3`. → *integration.*

**Review**
- **AC-3.24** *(accept term merge)* — **Given** an open `term_same` item, **when** `sddc review accept`
  runs, **then** the proposed name becomes an alias of the existing term, affected nodes lose
  `pending_review`, and their status is re-derived. → *integration.*
- **AC-3.25** *(reject inferred)* — **Given** an open `inferred_node` item, **when** rejected, **then**
  the node is deleted (F2 §4.9). → *integration.*

## 7. Decisions

- **D1 — Headless Claude Code is the default backend** (rel01 D7). *Rejected:* prompt hooks — they
  return only `ok`/`reason`.
- **D2 — Fake backend for tests.** *Rejected:* live model calls in tests — cost, non-determinism.
- **D3 — ⚑ Alignment is applied automatically in rel01** (`confirmed: auto`) and reported. P-6's
  "author confirms the alignment" is deferred. *Rejected for rel01:* blocking every edit on
  confirmation — too slow for AI-driven editing.
- **D4 — One batch run, one report** (rel01 D26). Nothing stops mid-run; every conflict and every
  attention item is reported at the end. *Rejected for rel01:* stopping at the first conflict, and the
  AI fix loop with attempts and escalation (old D4, rel01 D25) — both need live editing, which rel01
  does not have.
- **D5 — ⚑ Block-level all-or-nothing writes.** *Rejected:* per-atom writes — partial blocks would
  misalign identity.
- **D6 — ⚑ Exit codes `5` (call cap) and `6` (backend unavailable)** added to F1's code set.
- **D7 — ⚑ Size units:** KB/MB/GB are decimal, KiB/MiB/GiB binary.
- **D8 — Withdrawn by rel01 D26, deferred, not deleted:** the post-edit hook trigger (old T2,
  AC-3.23), the `--actor` stop rule (the old AC-3.21–3.22), and the AI fix loop with
  `attempts`, escalation and `sddc review dispute` (AC-3.26…AC-3.30, profile `ai_fix`). They return with
  live editing, together with rel01 D13, D16, D18 and D25. The child-process marker and the
  API-key stripping in §4.1 stay: they guard any nested `claude` call, hooks or not.

## 8. Open questions

- **Q1 — Default `max_calls_per_run`** (200 here) and `timeout_s` (120 here): set from the first real
  measurements.
- **Q2 — Model alias:** confirm that `--model haiku` resolves on the installed Claude Code version;
  otherwise pin a full model id in the profile.
- **Q3 — Q-TERM candidate count N** (similar existing names shown to the model). Default 10.

## 9. Traceability

| AC | Test (file::test) | Code |
|---|---|---|
| AC-3.1 … AC-3.5 | *(to be written)* | `src/sdd_compiler/llm/` |
| AC-3.6 … AC-3.13 | *(to be written)* | `src/sdd_compiler/atomize/guards.py` · `src/sdd_compiler/atomize/quantities.py` |
| AC-3.14 … AC-3.20 | *(to be written)* | `src/sdd_compiler/atomize/pipeline.py` · `src/sdd_compiler/atomize/align.py` · `src/sdd_compiler/atomize/lock.py` |
| AC-3.21 … AC-3.22 | *(to be written)* | `src/sdd_compiler/atomize/pipeline.py` · `src/sdd_compiler/report.py` |
| AC-3.24 … AC-3.25 | *(to be written)* | `src/sdd_compiler/atomize/review.py` |
