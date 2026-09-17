# F5 — Related-node retrieval: which pairs are worth judging

> **Spec-ID:** F5 · **Status:** 🟡 draft · **Drafted:** 2026-09-17
> ⛔ **Coding gated (rel01 D20).**
> **Source:** rel01 sub-goal G3.1 · approved proposal P-10 and the candidate rule in
> [`../../design/rel01_design/core-working-principle.md`](../../design/rel01_design/core-working-principle.md)
> §5–§6 · rel01 D26 (batch) · the F5 conflict list of 2026-09-16 (items 5.1–5.5).
> **Depends on:** F2 (node properties) · F4 (indexes). **Feeds:** F6 (pair judgment).
> **⚑ Drafting choices** are marked in §7.

---

## 1. Goal & why

**For every node that needs checking, produce a small, ranked, explained set of other nodes worth
comparing it against — deterministically, with no model call.**

Judging every pair is quadratic and unaffordable: 500 nodes is 124,750 pairs, one Haiku call each.
Retrieval is what makes checking affordable, and it is also the **main risk in the whole design**: a
pair never proposed is a relation never found. So every candidate carries *why* it was proposed, the
counts are recorded, and an exhaustive mode exists to measure what the ranked mode misses.

## 2. Scope / non-goals

**In scope:** candidate sources · deterministic scoring and capping · the pair key that makes a pair
identifiable across runs · which nodes need checking in a run · the exhaustive mode used for
measurement · `sddc pairs`.

**Non-goals**
- ✗ Judging a pair, or deciding what a relation means → F6.
- ✗ Embeddings or any learned similarity (rel01: deterministic only; vision O2).
- ✗ Context packs for code generation → F7 design note.

## 3. Users & triggers

| ID | Trigger | Entry point (code) |
|---|---|---|
| T1 | `sddc compile` reaches the check phase | `sdd_compiler.retrieval::candidates_for` |
| T2 | A person inspects what would be judged, or measures coverage | `sddc pairs [--node ID] [--exhaustive] [--json]` |

## 4. Behaviour

### 4.1 Which nodes are checked in a run

A node needs checking when its `status` is `unchecked`, or `stale`, or when it is `ambiguous` and was
never judged. Nodes whose text and whose candidates are unchanged since their `last_checked_run` are
skipped: their verdicts are replayed from the judgment lock (F3 §4.7).

Checking order is `(source file, first line, node id)`, so a run is reproducible.

### 4.2 Candidate sources

For node **A**, candidates are gathered from these sources. Each source records the evidence it used.

| Source | Rule | Evidence recorded |
|---|---|---|
| **S1 same family** | Same `family` (not `(global)`) | family id |
| **S2 shared subject term** | Shares a term of kind `entity`, `data` or `event` | the term ids |
| **S3 constraint scope** | A `C` node whose `scope_selector` covers the other node, in either direction | the selector that matched |
| **S4 adjacent layer** | Same family and layer distance ≤ 1 in the order L0…L5 | both layers |
| **S5 shared keywords** | At least `min_shared_keywords` (default 2) common `keywords` | the shared keywords |
| **S6 same measured property** | Shares a term **and** both carry a quantity of the same dimension (time, size, count, percent) | the dimension and both values |
| **S7 same source block** | Both atomized from the same block | the block id |

**Why S5 and S6 exist (⚑ D1).** The pre-rel01 rule was family, shared term, constraint scope and
adjacent layer only. That never proposes the first node of a family, and it misses conflicts whose
nodes share no term — the "SQLite versus 100 concurrent writes" shape. S5 catches wording overlap
without embeddings; S6 catches two numbers about the same thing, which is the most common real
contradiction.

### 4.3 Scoring and capping (⚑ D2)

```text
score = 3.0 · S1 + 2.0 · S2(per shared term, max 4.0) + 2.0 · S3 + 1.0 · S4
      + 0.5 · S5(per shared keyword, max 2.0) + 2.5 · S6 + 1.5 · S7
```

- Candidates below `min_score` (default 1.0) are dropped.
- The rest are ranked by score, then by node id, and the top `max_pairs_per_node` (default 10) are
  returned.
- Both numbers live in the profile (CT-5.2). They are **starting values to tune with measurement**, not
  findings.

### 4.4 Pair identity

A pair is unordered. Its key is
`pair_key = sha256(min(id_a, id_b) + "|" + max(id_a, id_b) + "|" + text_hash of each, in the same order)`.

The key changes when either node's text changes, which is exactly when the pair must be judged again.
F6 uses it for the judgment lock, and F5 uses it to drop pairs already judged in this run.

### 4.5 Exhaustive mode (⚑ D3)

`sddc pairs --exhaustive` returns **all** pairs among the checked nodes, with their scores, without
judging anything. It exists so the ranked mode can be measured against it on a labelled corpus: of the
true relations found exhaustively, how many did ranking propose? That measurement belongs to G4; this
spec only guarantees the mode exists and is deterministic.

Compilation never uses exhaustive mode: it is an offline measurement tool.

### 4.6 Counts a run records

Per run, for later measurement (G4): nodes checked, candidates proposed, pairs after the cap, pairs
dropped by `min_score`, pairs dropped by the cap, pairs replayed from the lock. These go into the run
record (F1 CT-1.3, extended by CT-5.3).

## 5. Contracts

**CT-5.1 — Candidate**
```json
{ "pair_key": "sha256:<hex>", "a": "N-000042", "b": "N-000017", "score": 5.5,
  "evidence": [ {"source": "S2", "detail": {"terms": ["term:share_link"]}, "points": 2.0 },
                {"source": "S6", "detail": {"dimension": "time", "values": ["30 d", "1 h"]}, "points": 2.5 } ],
  "rank": 1 }
```
`evidence` is never empty, and its `points` sum to `score`.

**CT-5.2 — Profile additions**
```yaml
retrieval:
  max_pairs_per_node: 10
  min_score: 1.0
  min_shared_keywords: 2
```

**CT-5.3 — Run record additions** (F1 CT-1.3)
```json
{ "retrieval": {"nodes_checked": 0, "candidates_proposed": 0, "pairs_capped": 0,
                "dropped_below_min_score": 0, "dropped_by_cap": 0, "replayed": 0} }
```

## 6. Acceptance criteria

> Tiers are provisional. No test calls a model: F5 makes no model calls at all.

**Sources**
- **AC-5.1** *(same family)* — **Given** two nodes in family `term:share_link`, **then** each is a
  candidate for the other with S1 evidence. → *unit.*
- **AC-5.2** *(shared subject term, actors excluded)* — **Given** two nodes sharing `term:file` (an
  entity) and two others sharing only `term:owner` (an actor), **then** the first pair is proposed with
  S2 evidence and the second is not proposed by S2. → *unit.*
- **AC-5.3** *(constraint scope)* — **Given** a `C` node scoped to layer `L3` and a node in `L3`,
  **then** the pair is proposed with S3 evidence naming the selector. → *unit.*
- **AC-5.4** *(adjacent layer)* — **Given** two nodes of one family in `L1` and `L2`, **then** S4
  contributes; **given** `L1` and `L4`, **then** S4 does not. → *unit.*
- **AC-5.5** *(shared keywords)* — **Given** two nodes sharing 2 keywords and `min_shared_keywords: 2`,
  **then** S5 contributes and names the shared keywords; **given** one shared keyword, **then** S5 does
  not. → *unit.*
- **AC-5.6** *(same measured property)* — **Given** two nodes sharing `term:share_link`, one with
  "30 days" and one with "1 hour", **then** S6 contributes with dimension `time` and both values. →
  *unit.*
- **AC-5.7** *(same block)* — **Given** two nodes atomized from one block, **then** S7 contributes. →
  *unit.*
- **AC-5.8** *(first node of a family)* — **Given** a graph where a node's family, terms and block are
  unique to it, **when** candidates are gathered, **then** any candidate comes from S5 or S6, and the
  result may legitimately be empty. → *unit.*

**Ranking and capping**
- **AC-5.9** *(evidence explains the score)* — **Given** any candidate, **then** `evidence` is
  non-empty and its points sum exactly to `score`. → *property.*
- **AC-5.10** *(cap and threshold)* — **Given** 25 scoring candidates with `max_pairs_per_node: 10`,
  **then** exactly 10 are returned, they are the 10 highest, ties break by node id, and the run counts
  record 15 dropped by the cap. → *unit.*
- **AC-5.11** *(determinism)* — **Given** the same graph, **when** candidates are computed twice in
  different insertion orders, **then** the results are identical, including rank order. → *property.*

**Pairs and selection**
- **AC-5.12** *(pair key symmetry and sensitivity)* — **Given** nodes A and B, **then**
  `pair_key(A,B) == pair_key(B,A)`; **when** either node's text changes, **then** the key changes. →
  *property.*
- **AC-5.13** *(no self pair, no duplicates)* — **Given** any node, **then** it is never its own
  candidate, and a pair appears at most once per run. → *unit.*
- **AC-5.14** *(which nodes are checked)* — **Given** nodes with statuses `unchecked`, `stale`,
  `validated` (unchanged) and `conflict`, **then** the first two are checked, the `validated` one is
  skipped, and the `conflict` one is checked again. → *unit.*
- **AC-5.15** *(exhaustive mode)* — **Given** 6 checked nodes, **when** `sddc pairs --exhaustive` runs,
  **then** it returns all 15 pairs with scores, judges nothing, and makes no model call. →
  *integration.*
- **AC-5.16** *(counts recorded)* — **Given** a compile run, **then** the run record carries the CT-5.3
  counts and they add up: proposed = capped + dropped_below_min_score + dropped_by_cap. → *contract.*

## 7. Decisions

- **D1 — ⚑ Two extra candidate sources, S5 keywords and S6 same measured property**, beyond the
  pre-rel01 rule. *Why:* the old rule cannot propose the first node of a family and misses
  no-shared-term conflicts. *Rejected:* embeddings — non-deterministic, and they answer "reads alike"
  rather than "about the same thing".
- **D2 — ⚑ Fixed additive scoring with a per-node cap.** *Rejected:* judging every candidate — the cost
  is unbounded; a learned ranker — no training data and no determinism.
- **D3 — ⚑ An exhaustive mode for measurement only.** *Why:* the design's biggest risk is a missed
  pair, and this is the only honest way to measure it.
- **D4 — ⚑ `pair_key` includes both text hashes**, so an edit re-opens exactly the pairs it touches.
- **D5 — Deferred: `checked_against` per node** (conflict-list item 5.4). A batch run checks the whole
  graph, so the cheaper `last_checked_run` plus `stale_reasons` is enough for rel01. It returns with
  incremental checking.

## 8. Open questions

- **Q1 — Defaults** (`max_pairs_per_node` 10, `min_score` 1.0, `min_shared_keywords` 2) and the weights
  in §4.3: set from the first measurement, not by taste.
- **Q2 — Should S3 also propose the reverse direction for `(global)` constraints?** Every node is in
  their scope, which would flood the candidate set. Current answer: `(global)` constraints are proposed
  only against nodes sharing a term or keyword with them.
- **Q3 — Keyword stop-word list** is shared with F2 Q2.

## 9. Traceability

| AC | Test (file::test) | Code |
|---|---|---|
| AC-5.1 … AC-5.8 | *(to be written)* | `src/sdd_compiler/retrieval/sources.py` |
| AC-5.9 … AC-5.11 | *(to be written)* | `src/sdd_compiler/retrieval/score.py` |
| AC-5.12 … AC-5.16 | *(to be written)* | `src/sdd_compiler/retrieval/select.py` · `src/sdd_compiler/cli.py` |
