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
| **Q-ATOM** | A **batch** of pending blocks (rel01 D30), each with text, kind, heading path, table header | Sentence roles; atoms, each `{kind, quotes[]}` with **verbatim quotes**; non-normative sentences labelled with their role |
| **Q-DESC** | A **batch** of atoms (rel01 D30; at most 8 per call, rel01 S21), each with its quotes; each block's text and heading path sent once; up to 100 existing term names to reuse (D26) | Canonical fields (F2 CT-2.1 `canonical`, without normalized quantities); layer answers Q1–Q7 with quotes; term tags `{name, kind, role, quote}`; ambiguity candidates `{kind, quote}`; for `C` a scope description and `scope_layers` (closed list of `L0`…`L5`, F2 D13); for `V` the text of what it verifies; for `decision` chosen, rejected with reasons |
| **Q-TERM** | One proposed term plus up to N existing terms with similar names | `same` (synonym, spelling, plural) · `narrower` (a kind of a candidate) · `different` · `unsure`, with a `target` for the first two and a reason (`q-term/2`, D25) |

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
4. **Batching (rel01 D30).** Q-ATOM may carry several blocks in one call. Each block's answer is
   validated on its own; a failure re-asks **only that block**, alone, once. One block failing never
   discards another block's accepted answer.

### 4.4 Guards (P-5)

| Guard | Applied to | Check | On failure |
|---|---|---|---|
| **G2** Span anchoring | Q-ATOM, Q-DESC quotes | Every quote occurs verbatim in the block text — ⚑ *up to layout*: runs of whitespace, and the `>` markers Markdown repeats on each wrapped line of a blockquote, and `*` emphasis marks may differ, as may backticks and the case of a quote's **first** letter (D9). Words, order, case and
punctuation must otherwise match. Code computes the offsets. A quote occurring more than once anchors to the first occurrence not already claimed by another atom in the same block | Re-ask |
| **G3** Coverage | Q-ATOM | Every sentence of the block containing a normative word (`must, shall, should, may, never, only, required, not allowed`) is covered by an atom quote or labelled non-normative | Re-ask |
| **G4** No injection | Q-DESC | Every term name and every quantity in the canonical fields appears in the atom's quotes, directly or as a registered alias — **source = the atom's block and its heading path** (D13); values are compared ignoring inline Markdown marks (`` ` ``, `*`) | Node gets flag `inferred` and ambiguity `inferred`, plus a review-queue item |
| **G5** Schema | All | The answer validates against its schema version | Re-ask |
| **G6** Weak words | Atom quotes | Words from `profile.weak_words` add ambiguity `vague_term` with the matched quote. G6 is the **only** source of `vague_term`; the model may not propose it (D11) | — (fact, not failure) |

- **Placement T3** (F2 AC-2.2) returning `split_required` counts as a Q-ATOM failure for that block:
  re-ask Q-ATOM once with both quotes. If the re-asked atoms still require a split, the node is formed
  with the first yes's layer and ambiguity `mixed_layers` (D23) — the block does not fail.
- **Quantities** are parsed from the quotes by code into a value and unit. They are normalized for
  time (to seconds), size (to bytes; KB = 1000, KiB = 1024) and count/percent (unchanged). A quantity
  the parser cannot read adds ambiguity `unbounded_quantity`.
  ⚑ Months and years are recorded with `normalized: null` (D12). A count is recognized only after a
  bounding word ("at most 3 times"); numbers inside identifiers, dates and versions are not
  quantities.

### 4.5 Forming a node

For each validated atom:
1. Resolve term tags against the registry. Exact names and aliases resolve directly.
2. Otherwise ask Q-TERM:
   - `different` → create a `proposed` term;
   - `same` → the name becomes an alias of that existing term, and a `term_same` review item lets a
     person reject the merge (D20);
   - `narrower` → a `proposed` term of its own, recording `broader` (D25); no review item;
   - `unsure` → a `proposed` term, a `term_unsure` review item, and ambiguity `pending_review` on the
     node until reviewed (D16).
3. Compute quantities, `keywords`, spans and lines.
4. Call F2 placement (layer, family, components).
5. Create `uses_term` links (provenance `code`).
6. Set `last_checked_run: null`. Status derives to `unchecked` or `ambiguous` (F2).
7. Write through F4 atomically per block: either all nodes from a block are written, or none.
8. In the same write, set the block's `atomized_hash` to its current `text_hash` (F1 D13). This is
   what takes a block out of the pending set, so it is set **only** when the block completed: a block
   that failed its checks, hit the call cap, or was interrupted keeps its old value and stays pending.
   A block yielding zero atoms (all sentences non-normative) still completes.
9. **Definitions** (D38), after every chunk, in the same write: a term whose `defined_by` block was
   re-atomized, removed or skipped in this run loses its `definition`. Then each `definition` sentence
   from this run's completed blocks — its quote located in the block (G2, layout-tolerant), stored as
   the block's own text — is attached, in `(source, line)` order, to the registered term whose name or
   alias the sentence **opens with**, followed by a definitional boundary (`is`, `are`, `means`, `=`,
   `:`, `—`, `(`, or the end). A leading `a`/`an`/`the` and inline Markdown are ignored; a sentence
   that is a table row is not matched. A term that already has a `definition` keeps it. A sentence
   that matches no term, or whose term is already defined, is **reported, never dropped silently**
   (§4.8).

### 4.5a Contract blocks (D39)

A fenced block pending by F1 D15 is a **contract**: one record shape, file format or output, stated by
its form. It is formed whole:
1. **No Q-ATOM.** Code forms one `requirement` atom whose quote is the block's text between its fence
   lines. It is one claim by its form, so it is never re-asked to split (D36).
2. **Its lead** is the paragraph directly before it in the same file and section, if any: normally its
   title, `**CT-1.1 — Block record** (…)`. The lead's `CT-` id becomes the node's id (F2 D21).
3. **Q-DESC** describes the atom with the lead shown before the block's text; G2 and G4 read lead and
   block together, so a subject named only in the title is quoted and grounded. The node's `text`,
   `spans` and `lines` are still the block's own. The lead enters the lock key only for a contract, so
   no other item's key changes (AC-3.37).
4. **Quotes from a contract** (D40). The atom tells the model to quote only the title or one whole
   line of the block, copied exactly. A quote that is still not found does not fail the answer:
   a `yes` layer answer's quote becomes the whole contract, a term's quote becomes the first place
   its name appears in lead or block (the tag is dropped if the name appears nowhere), and an
   ambiguity's quote becomes null. Every replaced quote is listed in the run report (§4.8).

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
- So does a block that is no longer pending by F1 D14 or `include_code_blocks: false` but still has
  nodes (the profile changed after it was atomized): its nodes are deleted (F2 §4.9) and its
  `atomized_hash` is cleared, so that naming the section again makes the block pending again.
- Alignments are applied automatically, recorded with `confirmed: auto`, and listed in the run report
  (⚑ D3).

### 4.7 Judgment lock (P-1)

- Every accepted answer is appended to the lock as CT-3.2.
- Before asking, the atomizer computes `input_hash = sha256(question kind + schema version + the
  question's instructions + canonical JSON input)` per item (D21). A lock hit **replays** the stored
  answer through the same guards, with no model call; if a guard now rejects it, the item is asked.
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
- The run ends with one report (§4.10): blocks processed, nodes formed, **blocks that completed and
  formed no node, with the roles their sentences were given** (D33), **definitions attached and
  definitions not attached, each with file and line** (D38), **every contract quote replaced**
  (D40), model calls and usage, every conflict
  found, and every attention item opened.

### 4.9 Attention list — items a person must decide

Some findings cannot be settled by code and, in a batch run, are not settled by anyone mid-run. They
are recorded as items (CT-3.3) and listed at the end of the run:

| Type | Raised when | Effect on the node |
|---|---|---|
| `inferred_node` | G4 found canonical content that is not in the source | flag `inferred`, ambiguity `inferred` |
| `term_same` | Q-TERM judged a new name the same as an existing term; merged as an alias (D20) | none; rejecting the item splits the name back out |
| `term_unsure` | Q-TERM could not tell | ambiguity `pending_review` |
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
| `6` | Model backend unavailable (e.g. `claude` not found, authentication failure, a usage limit). If it happens mid-run, finished chunks are written and the rest stays pending, as for `5` (D24) |

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
  "usage": {"input_tokens": 0, "output_tokens": 0, "cache_read_tokens": 0, "cost_usd": null} | null,
  "batch_of": "J-000320 | null",
  "duration_ms": 0, "confirmed": "auto | author", "run": "R-0011" }
```
One record per **item** — a block (Q-ATOM), an atom (Q-DESC), a term (Q-TERM) — not per call (D21).
`answer` is the item's entry from the call's answer, without its id. The first record of a call carries
the call's `usage` and `duration_ms`; the others have `usage: null` and `batch_of` naming it.

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
  thinking: false              # extended thinking for the claude-code backend (D10)
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
  is re-asked once for that block with both quotes; **given** the re-asked answer still requires a
  split, **then** the node is formed with the first yes's layer and ambiguity `mixed_layers` (D23). →
  *unit.*
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

**Contract blocks** (I-92 a, D39)
- **AC-3.35** *(formed whole, without Q-ATOM)* — **Given** `**CT-1.1 — Block record**` followed by a
  fenced `json` block, **when** compiled with a fake backend scripted for Q-DESC only, **then** no
  Q-ATOM is asked for the block, one node `CT-1.1` of kind `requirement` is formed whose `text` is the
  JSON between the fences, verbatim, and whose `spans` address the block. → *integration.*
- **AC-3.36** *(the lead grounds the description)* — **Given** AC-3.35, with a Q-DESC answer whose
  subject term `block record` is quoted from the title, **then** the answer passes G2, the node is not
  flagged `inferred`, and its family is `term:block_record`. → *integration.*
- **AC-3.37** *(other lock keys are unchanged)* — **Given** an ordinary atom, **then** its Q-DESC lock
  input has no lead, and equals the input computed before D39; **given** a contract atom, **then** the
  lead is part of its input. → *unit.*
- **AC-3.38** *(a text block without a title)* — **Given** a fenced `text` block that opens its section,
  **when** compiled, **then** it forms one node with an `N-` id and no label, described with its
  heading path as its only context. → *integration.*

- **AC-3.39** *(a contract's unfound quote is replaced; D40)* — **Given** a contract whose Q-DESC
  answer quotes `"id", "kind", "members"` (not contiguous in the block) for a `yes` layer answer, and a
  term `block record` quoted as `the block record type`, **then** the answer is accepted without a
  re-ask, the layer answer's span is the whole contract, the term's quote is `Block record` as the
  title writes it, and both replaced quotes are listed; **given** the same bad quote on an ordinary
  atom, **then** it is re-asked (G2). **And** no contract hint text appears in the question.
  → *unit.*

**Definitions and skipped sections** (I-92)
- **AC-3.31** *(a definition is attached; D38)* — **Given** a block whose fake Q-ATOM answer labels
  "A **block** is a structural unit found by code." `definition`, and a registered term `block`,
  **when** compiled, **then** `term:block` has that sentence, as it appears in the block, as its
  `definition` and the block's id as its `defined_by`, and the run report counts 1 definition attached.
  → *integration.*
- **AC-3.32** *(unmatched and repeated definitions are reported; D38)* — **Given** definition sentences
  "Both cannot hold.", "A block is not an atomic spec." (after the one in AC-3.31) and "A requirement
  or constraint that states no modal verb has this ambiguity.", with terms `block` and `requirement`
  registered, **when** compiled, **then** `term:block` keeps its first definition, `term:requirement`
  gets none (the name is not followed by a definitional boundary), and all three sentences are listed
  in the report as not attached, with file and line. → *unit.*
- **AC-3.33** *(a re-atomized block re-derives its definitions; D38)* — **Given** AC-3.31's store,
  **when** the defining block is edited so that its answer holds no definition, **then** `term:block`
  has `definition` and `defined_by` null. → *integration.*
- **AC-3.34** *(a newly skipped section loses its nodes; §4.6, F1 D14)* — **Given** a compiled store
  with a node formed from a row under `## 9. Traceability` and `skip_headings: []`, **when** the
  profile is changed to the default and compile runs, **then** the node is deleted with the F2 §4.9
  cascade, the block's `atomized_hash` is null, no model call is made, and `check_store` is clean.
  → *integration.*

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
- **D9 — G2 matches quotes *up to layout*** (closes Q4, 2026-09-18, option a). Runs of whitespace, and
  the `>` markers Markdown repeats on wrapped blockquote lines, may differ between a quote and the
  source; words, order, case and punctuation may not, and anchors stay true source offsets.
  *Why:* strict matching rejected 5 of 20 real blocks whose quotes were correct prose, and the re-asks
  made batching dearer than one call per block; with D9 the same blocks gave 0 failures (rel01 S20).
  *Rejected:* (b) strict matching after re-wrapping quotes in code — the same rule, stated less
  directly.
  *Extended 2026-09-18 (T9, ⚑ under the same principle):* `*` emphasis marks are also layout. Haiku
  quotes `**Given** a file` as `Given a file`; strict matching failed **14 of 20** acceptance-criterion
  blocks, and ignoring `*` brought that to 0 (rel01 S22).
- **D10 — ⚑ Extended thinking is off by default** (found while building T8; profile
  `atomizer.thinking`). Claude Code thinks by default. On one Q-DESC call, thinking was 2,896 of 3,588
  output tokens and took the call from ≈ 5 s to 25–35 s; batches of 8 atoms exceeded the 120 s timeout.
  The questions are small and closed. On the one atom compared, the answer without thinking placed the
  claim correctly (L1) and the thinking answer did not (C). One sample; the M2 gate measures quality.
  *Mechanism:* `MAX_THINKING_TOKENS=0` in the child environment. ⚠ Every cost figure before rel01
  S21 was measured with thinking on.
- **D11 — ⚑ `vague_term` comes from G6 only** (found while building T8). Offered `vague_term`, Haiku
  flagged 17 of 20 real atoms, on words such as "Storage" and "matches". The model still proposes
  `missing_actor`, `referential` and `scope`.
- **D12 — ⚑ Months and years are not normalized.** Neither has a fixed length; converting one would
  invent a number. The raw value and unit are kept.
- **D13 — G4 grounds against the atom's block and its heading path** (closes Q5, option a).
  `inferred` means "not in the source at all". *Why:* read narrowly (the atom's own quotes), G4 flagged
  8 of 17 real atoms, all context resolution ("here" → "F1" from the heading); read widely, 1 of 20, and
  that one real (rel01 S21). *Rejected:* (b) narrow — ≈ 8 false review items per 17 atoms.
  *Accepted cost:* borrowing a value from a neighbouring claim in the same block is not flagged.
- **D14 — A requirement or constraint without a modality is formed and flagged** (closes Q6, option b).
  `canonical.modality` is null and the node carries ambiguity `missing_modality` (F2 CT-2.1), so its
  status derives to `ambiguous`. *Why:* failing it removed its whole block (AC-3.16) for a claim that is
  merely under-specified; defaulting to `MUST` (option c) would invent an obligation strength the
  author did not write.
- **D15 — ⚑ `source.spans` are offsets into the block's text** (found while building T10). The block's
  verbatim text is stored with the block (F1 CT-1.1), so block id plus span is a complete address and
  no node needs the file to be located. Multi-span text is joined with ` … `.
- **D16 — ⚑ A `same`/`unsure` Q-TERM verdict keeps the new term separate until reviewed** (T10): the
  node links the new `proposed` term and carries `pending_review`; accepting the review item merges it
  as an alias. *Why:* merging on the model's word alone would move nodes between families unreviewed.
  *Narrowed by D20:* applies to `unsure` only.
- **D17 — ⚑ Q-TERM is asked only when similar names exist** (T10). "Similar" = a shared word (plural
  folded) or a `difflib` ratio ≥ 0.8, at most 10 candidates (Q3's default). With no candidate the
  answer could only be `different`, so no call is made; on a first run most terms need none.
- **D18 — ⚑ Pending blocks are processed in chunks of 20** (T10). One chunk runs every model step
  (Q-ATOM, Q-DESC, the split re-ask, Q-TERM) before any of it is kept, so a call-cap stop keeps the
  finished chunks and leaves the interrupted one pending, whole (AC-3.5).
- **D19 — ⚑ Term hygiene** (T10). A family is a term, so a term must name a thing. On 32 live blocks
  Haiku tagged 142 terms for 49 nodes, 119 used once — ids (`AC-1.9`, `D9`), values (`120 s timeout`),
  settings with values, clauses — making families near one per node (rel01 S23). Code drops a tag with
  a digit, a `:`/`=`, or more than four words, and folds names to the singular before matching; the
  Q-DESC prompt defines a term as a short singular noun phrase naming a thing.
- **D20 — A Q-TERM `same` verdict merges at once, and a person may undo it** (closes Q7, option b).
  The new name becomes an alias of the existing term, all its tags resolve there, and a `term_same`
  item records the merge; rejecting it splits the name back out. No node becomes `ambiguous` for it.
  *Why:* on 32 live blocks 7 of 8 verdicts were `same` and all plausible, yet under D16 they made 16 of
  49 nodes `ambiguous` (rel01 S23). *Rejected:* (a) D16 for every verdict — a flood of ambiguity over
  merges that were right. `unsure` keeps D16.
- **D21 — ⚑ The judgment lock is per item, and its key includes the instructions** (T12). Q-ATOM,
  Q-DESC and Q-TERM are batched (rel01 D30); keyed per call, editing one block would change its
  20-block batch and re-ask all twenty. Keyed per item — by the item's content, not its id — only the
  changed item is asked, and a moved block keeps its answer. A call's usage is stored once
  (`batch_of`, CT-3.2) so costs are never counted twice. The instructions are in the key so that a
  prompt change re-asks instead of replaying answers to a different prompt. A re-ask carrying a note
  (the T3 split, AC-3.12) is never answered from the lock; the latest record for a key wins.
- **D22 — ⚑ Alignment measures text overlap, and an aligned id beats an adopted one** (T12). §4.6's
  "span overlap" is computed as a `difflib` ratio (≥ 0.5) between the old node's `text` and the new
  atom's text, because the old block's text is gone once ingest replaces it. Ties break by old id,
  then atom order. When a labelled block's atom aligns to an old `N-` node, the old id is kept (the
  `label` still names the criterion): identity across edits outranks adoption (F2 AC-2.19). An
  `unchanged` node keeps its whole record — check state included — except its `source`.
- **D23 — A split the model refuses twice is formed, flagged `mixed_layers`** (owner, 2026-09-18,
  closing I-42). *Why:* on `vision.md`, 4 of 31 blocks failed every run, all a bold title plus its
  explanation: title and body answered different layer questions with non-overlapping quotes, and the
  model rightly kept one claim. Failing them cost a re-ask on every compile and left them out of the
  graph. Two refusals are evidence of one claim, so the node takes the first yes's layer and the
  ambiguity names the second (F2 D15). *Rejected:* special-casing bold lead-ins — narrower, and the same
  refusal appears on Given/When/Then criteria (I-22, I-30).
- **D24 — A backend failure mid-run keeps finished work** (owner, 2026-09-18, closing I-43). Exit `6`
  now behaves like exit `5`: finished chunks and their judgment-lock records are written; the
  interrupted chunk stays pending. *Why:* a usage limit (hit twice in live runs) would otherwise
  discard every paid-for answer of the run.
- **D9 extended (rel01 D32 R5, R10):** backticks are layout, like `*`; a case difference in a quote's
  first letter only is tolerated ("a Q-TERM…" for "A Q-TERM…" failed a block in both gate runs).
- **D25 — Q-TERM `narrower`** (rel01 D33 R1). A kind of a candidate keeps its own term and family and
  records `broader` (F2 D16). `same` is defined as synonyms, spellings and plurals, with examples.
  *Why:* at the M2 gate 9 of 16 `same` verdicts explained themselves as "a specialized form of".
- **D26 — Q-DESC is shown the vocabulary** (rel01 D33 R2): up to 100 existing term names — the chunk's
  own files' terms first, then the most used — to reuse when they name the same thing, with the rule "a
  kind of X is not X". The list is rendered outside the instructions, so it is **not** in the lock key
  (D21). *Why:* 72–79 % of gate terms were used once, so families held one node each.
- **D27 — Prompt corrections from the M2 gate** (rel01 D32 R3, R9, R11). Q1 asks about meaning, not
  words such as "every" or "never"; Q3 asks whether an outsider can check the claim without looking
  inside the system; Q-ATOM lists what is *not* a claim (titles, status and process notes, open
  questions, pointers, legends, tier tags, and every sentence after *Why:* or *Rejected:*).
- **D28 — An acceptance criterion is one verification atom** (rel01 D32 R8). A block labelled `AC-…` is
  folded by code into a single `verification` atom holding all its quotes; the prompt says the same for
  Given/When/Then text. *Why:* at the gate, criteria became Given/When/Then fragments plus a stray atom
  from the tier tag. A side effect: such blocks form one node, so they adopt their `AC-` id (F2
  AC-2.19).
- **D29 — Canonical subject and response must say something** (rel01 D32 R7): an empty or blank one fails
  G5 and is re-asked. *Why:* two gate nodes were formed with both empty.
- **D30 — Resolve a reference before flagging it** (owner, after R6: R13). Q-DESC is told to resolve
  "it", "this", "they" from the same block or its section and to write the resolved thing as the
  subject; `referential` is flagged only when neither names it. *Why:* after R1 … R11, `referential` was
  still on about a third of nodes and the main cause of `ambiguous`.
- **D31 — `narrower` points from the specific to the general** (owner, after R6: R14). The Q-TERM prompt
  says so, with a reversed example, and code refuses a `narrower` verdict whose candidate already
  contains every word of the new term ("backend" against "claude code backend"): the new term is the
  broader one, so the answer is re-asked. *Why:* about 1 in 4 `narrower` verdicts in R6 were reversed.

- **D32 — ⚑ `definition` is only for what a word means** (M3 gate review, I-56). Q-ATOM labelled all
  seven of F5's candidate-source table rows `definition` and formed no node, so F5's core rules were
  absent from the graph with no warning. The prompt now says that a row or item stating how something
  behaves, is decided or is checked is a claim, with F5's S1 row as the example. ⚠ **Still open:** F2 §4.1
  says "definitions become term-registry entries", but nothing writes them (`defined_by` is always
  null). A sentence labelled `definition` is dropped silently. This is the I-26 pattern again: a field
  with readers and no producer (build-plan I-59).

- **D33 — ⚑ The report counts blocks that formed no node** (M3 gate review, I-59). A block whose
  sentences are all `definition`, `context` or `rationale` is completed, correctly, and forms nothing;
  until now the run said "65 of 65 completed" while seven of F5's rules vanished. The summary carries
  `empty_blocks` and, per block, its file, lines and sentence roles. *Not* an attention item (§4.9):
  most empty blocks are headings and legends, and a queue of them would bury the real items. ⚠ The
  other half of I-59 — a producer for `definition` sentences (F2 §4.1) — is still open.

- **D34 — ⚑ A table row is one claim, enforced in code** (R15, I-64). With D32 the rows became
  claims, and F5's `S3` row came back as one atom per cell: "A `C` node whose `scope_selector` covers
  the other node", "by the rule of D9", "the selector that matched" — one rule as three fragment nodes
  in three families. A row's cells are the parts of one rule, so `one_criterion` now folds a row's
  atoms into one, keeping every quote in row order, as it already did for `AC-` blocks (D28). The
  prompt says the same, and adds the rule Q-DESC has had since I-15: **the "section" and "table header"
  lines are context and are never quoted** (R15, I-63: 4 of 66 blocks failed on exactly that).

- **D35 — ⚑ An annotation that cannot be located is dropped and reported, never raised** (R16, I-67).
  Rationale and example sentences become annotations (F2 §4.1), and their quotes were located by the
  same guard that anchors atoms — which *raises*. Q-ATOM merged two source sentences into one
  `rationale` quote, and the exception escaped at node-forming time, **after every model call of the
  run had been paid for**, losing the whole compile. An annotation carries no claim, so an unlocatable
  one is dropped and listed in the run report (`annotations_dropped`), beside D33's empty blocks.
  ⚠ **Open (build-plan I-68):** F3 D24 keeps finished work only for the two *expected* stops, exit `5`
  and `6`. An unexpected exception anywhere after the first call still discards the run and its lock
  records. The exit code for an internal error is not specified (CT-1.6 has none), so this is the
  owner's call.

- **D36 — ⚑ A block that is one claim by its own form is never asked to split** (R16, I-70). D34 folds
  a table row's atoms into one, and D28 does the same for an `AC-` block — and then AC-3.12's split
  re-ask asked the model to separate the row's rule from its evidence cell, and it obliged: all seven
  of F5's source rows became two nodes, one of them a bare fragment. Such a block now takes D23's
  path directly — placed by its first yes, flagged `mixed_layers` — decided in the first pass, so it
  also saves a model call. AC-3.12 still governs every other block.

- **D40 — ⚑ A contract's unfound quote is replaced, not re-asked** (I-94, owner 2026-09-28, option
  c). On the live run, Q-DESC failed G2 twice on 7 of 25 contracts: asked to quote JSON, Haiku gave key
  lists pulled out of it, summaries, its own commentary, and once the hint this spec had added to the
  atom's kind line — so the hint is gone. Two layers: the atom asks for the title or one whole line
  (a request, which the model may ignore), and code no longer fails the answer when it does. *Why a
  replacement is safe here:* a layer quote only lets placement compare spans (F2 §4.3), and a contract
  is one claim that is never split (D36), so its whole span is the right one; a term keeps its tag
  only where its name is really in the source, so G4 still holds. Nothing the node stores is model
  text. *Rejected:* a whitespace-insensitive G2 alone — it would have rescued 1 of the 7; relaxing G2
  for every atom — prose quotes fail rarely and a re-ask fixes them.

- **D39 — ⚑ A contract block is one node, formed whole** (I-92 a, owner 2026-09-27: node design,
  `text` blocks included, `CT-` ids). §4.5a. *Why:* the 25 fenced blocks are every contract the specs
  define and formed no node (F1 D15). Q-ATOM cannot usefully split JSON into claims, so code forms the
  one atom and saves the call; Q-DESC still places it, because code cannot tell an `L3` file format from
  an `L4` data shape (F2 §4.2), and still tags its subject term, which puts `CT-1.1` in the family of the
  rules written about it. The title is where the subject is named, so Q-DESC sees it; without it G2
  would reject every subject quote. A contract states no modal verb, so a model answering modality null
  flags `missing_modality` as for any requirement (D14) — code never supplies MUST. ⚠ Retrieval will
  pair a contract with every claim sharing its field names (F5 S5) and may read its own rules as
  duplicates (the I-93 pattern). *Measured on a copy of R18, with a stand-in Q-DESC answer (subject =
  the title's name), so an estimate:* 25 contract nodes, 22 with their `CT-` id, none `inferred`;
  4 Q-DESC calls; **191 new candidate pairs touch a contract** (≈ 8 each; S5 fired in 170, S3 in 76 —
  criteria citing `CT-n.k` now resolve `verifies` to it, and D16 already suppresses those as
  duplicates). What the judge makes of them is **to be measured** by a live run before any suppression
  rule is added.

- **D38 — ⚑ A definition is attached by code, to the term it opens with** (I-92, closing I-59's open
  half, 2026-09-27). Q-ATOM has always labelled `definition` sentences and F2 §4.1 always said they
  become term entries, but nothing wrote them: on R18, 68 definition sentences were labelled and **0 of
  1 031** terms had a definition. An agent building from the graph alone (the trial_01 README rule)
  therefore saw no definitions at all, and `defined_by` alone would not help it — a block id points into
  `blocks.jsonl`, the verbatim source it may not read — so the term carries the sentence itself.
  *The match is by code, and strict on purpose.* Measured on R18's 68 sentences: matching a term name
  anywhere at the start attaches 38, and reading them, many are wrong ("A requirement or constraint that
  states no modal verb…" defines `missing_modality`, not `requirement`). Requiring the definitional
  boundary, the shipped code attaches **15 sentences to 15 terms, all read and correct**; 2 more repeat
  a term already defined, and 48 define things the registry does not hold (`inferred`, "Similar"), are
  ID-family table rows, or gloss relations ("Both cannot hold") — reported, not guessed (67 distinct
  sentences, 65 located in a block still atomized). ⚠ A small yield: the specs define few of their terms
  in "X is Y" form, and the registry only holds names Q-DESC tagged on nodes. A wrong definition misleads a reader more than a missing one.
  *Rejected:* (a) asking Q-ATOM to name the defined term — a schema change re-asks every block (D21);
  (b) creating a term from an unmatched definition — its `kind` would have to be invented; (c) keeping
  every definition of a term — the contract is one sentence, the first in reading order.

- **D37 — ⚑ An unusable answer is rejected, not fatal** (C, the dogfood run: I-79). A Q-ATOM call
  over 20 dense spec blocks returned no `structured_output`, and the backend raised it as "the model
  backend is unavailable" (exit `6`), ending a 173-block compile after 19 blocks. One call producing
  nothing usable is the same event as an answer failing a guard: `AnswerRejected` now travels to the
  batch layer, which re-asks **each item alone** — a far smaller prompt, and usually enough. A dead
  backend, a missing binary and a 429 stay exit `6`. *Why it matters at scale:* on 733 blocks, one
  unlucky call in fifty would otherwise stop every long compile.

## 8. Open questions

- **Q1 — Default `max_calls_per_run`** (200 here) and `timeout_s` (120 here): set from the first real
  measurements.
*Q2 closed 2026-09-18 by measurement: `--model haiku` resolves to `claude-haiku-4-5-20251001` on Claude
Code 2.1.275 (reported in every call's usage). The model actually used is recorded on every call, so a
change of alias is visible.*
- **Q3 — Q-TERM candidate count N** (similar existing names shown to the model). Default 10.

*Q5 and Q6 were closed 2026-09-18 as D13 and D14.*

*Q7 was closed 2026-09-18 as D20.*

## 9. Traceability

| AC | Test (file::test) | Code |
|---|---|---|
| AC-3.1 … AC-3.4, AC-3.5 *(budget; the pending-blocks half lands with T10)* | `tests/test_llm_backend.py` (16) · `tests/test_profile.py` (3) | `src/sdd_compiler/llm/` · `profile.py` |
| AC-3.6 … AC-3.8, AC-3.10 · D9 | `tests/test_atomize_qatom.py` (20) | `src/sdd_compiler/atomize/qatom.py` · `guards.py` |
| AC-3.9 *(flag and ambiguity; node status and review item with T10)*, AC-3.11, AC-3.13 · D10–D14 | `tests/test_atomize_qdesc.py` (22) · `tests/test_quantities.py` (25) · `tests/test_llm_backend.py` (+2) | `src/sdd_compiler/atomize/describe.py` · `quantities.py` · `batch.py` · `llm/claude_code.py` |
| AC-3.5 *(pending half)*, AC-3.9 *(node and review item)*, AC-3.12, AC-3.14 … AC-3.16 · D15 … D20, D25 … D31 | `tests/test_atomize_pipeline.py` (52) | `src/sdd_compiler/atomize/pipeline.py` · `forming.py` · `terms.py` · `batch.py` |
| D37 *(an unusable answer is re-asked)* | `tests/test_llm_backend.py::test_i79_…`, `::test_a_missing_structured_output_rejects_…` | `src/sdd_compiler/llm/base.py` · `claude_code.py` · `atomize/batch.py` |
| D36 *(a one-claim block is never split)* | `tests/test_atomize_pipeline.py::test_r16_a_table_row_is_never_split_into_its_cells` | `src/sdd_compiler/atomize/pipeline.py::one_claim_block` · `_describe_and_place` |
| D34 *(a row is one claim)* | `tests/test_atomize_pipeline.py::test_r15_a_table_row_becomes_one_claim` · `tests/test_atomize_qatom.py::test_the_prompt_forbids_quoting_the_context_lines` | `src/sdd_compiler/atomize/pipeline.py::one_criterion` · `qatom.py` |
| D35 *(a dropped annotation never stops a run)* | `tests/test_atomize_pipeline.py::test_r16_a_rationale_quote_…` | `src/sdd_compiler/atomize/forming.py::block_annotations` |
| §4.8 run report (calls, cost, empty blocks) · D33 · §4.9 items closing themselves | `tests/test_compile.py` · `tests/test_atomize_pipeline.py::test_f3_d33_…` | `src/sdd_compiler/pipeline.py` · `atomize/pipeline.py` · `atomize/qatom.py` |
| AC-3.17 … AC-3.20 · D21, D22 | `tests/test_atomize_align.py` (9) · `tests/test_atomize_lock.py` (8) · `tests/test_compile.py` (+6) | `src/sdd_compiler/atomize/align.py` · `lock.py` · `batch.py` · `src/sdd_compiler/pipeline.py` |
| AC-3.21 … AC-3.22 | *(to be written)* | `src/sdd_compiler/atomize/pipeline.py` · `src/sdd_compiler/report.py` |
| AC-3.24 … AC-3.25 | *(to be written)* | `src/sdd_compiler/atomize/review.py` |
| AC-3.39 · D40 | `tests/test_atomize_contracts.py::test_ac_3_39_*` | `src/sdd_compiler/atomize/describe.py` · `pipeline.py` · `src/sdd_compiler/report.py` |
| AC-3.35 … AC-3.38 · D39 · §4.5a · F2 AC-2.29, D21 | `tests/test_atomize_contracts.py` · `tests/test_compile.py::test_ac_3_35_*`, `::test_ac_3_38_*`, `::test_ac_2_29_*` | `src/sdd_compiler/atomize/contracts.py` · `describe.py` · `pipeline.py` · `src/sdd_compiler/model/ids.py` |
| AC-3.31 … AC-3.34 · D38 · §4.6 skipped sections | `tests/test_atomize_definitions.py` · `tests/test_compile.py::test_ac_3_31_*`, `::test_ac_3_33_*`, `::test_ac_3_34_*` | `src/sdd_compiler/atomize/definitions.py` · `qatom.py` · `src/sdd_compiler/pipeline.py` · `report.py` |
