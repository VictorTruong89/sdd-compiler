# 6. Relations and conflicts — how nodes get connected

950 nodes make 450 775 possible pairs. Asking the model about each would cost a fortune and drown the
real conflicts. So the check phase works in two steps:

1. **Retrieval (F5, code only):** find the few pairs worth asking about, and rank them.
2. **Judgment (F6, the model + code):** ask Q-PAIR about those pairs; code turns each verdict into
   links and, where warranted, a conflict record.

*Layman:* a school has 950 pupils and wants to find the ones who are fighting. It does not interview
every possible pair. It asks who sits together, who shares a class, who were seen arguing — and
interviews those pairs.

## Which nodes are checked in a run

A node is checked when its status is `unchecked`, `stale` or `conflict` (a conflict is re-judged every
run), or when it is `ambiguous` and **its pairs have never been judged** (`last_checked_run` is null).
A `validated` node is skipped: its verdicts replay from the lock for free. Order is
`(file, first line, id)`, so a run is reproducible.

## Retrieval: eight evidence sources and a score

For each checked node, every other node is scored by the sources that fire
(`retrieval/sources.py`, `retrieval/score.py`):

| Source | Fires when | Points |
|---|---|---|
| **S1** same family | Same `family` (not `(global)`, not null) | 3.0 |
| **S2** shared subject term | A shared entity/data/event term — or one is a *kind of* the other | 2.0 each, max 4.0 |
| **S3** constraint scope | One is a `C` node that covers the other (chapter 5) | 2.0 |
| **S4** adjacent layer | Same family, layers at most one apart in L0–L5 | 1.0 |
| **S5** shared keywords | At least `min_shared_keywords` (2) keywords in common | 0.5 each, max 2.0 |
| **S6** same measured property | A quantity of the same dimension (time, size, count, %) on both, and a shared term or keyword | 2.5 |
| **S7** same block | Both came from one block | 1.5 |
| **S8** siblings | Two terms that are kinds of the same thing ("export archive", "workspace export" → "export") | 1.0 |

A pair below `min_score` (1.0) is dropped; each node keeps its **top `max_pairs_per_node` (6)**; a pair
proposed from both ends is asked once. Every candidate carries the evidence its points came from, so a
score can always be explained. No model is involved anywhere in retrieval.

### The toy example, scored by the real code

Node A: "A share link must expire 30 days after it is created." · Node B: "Share links expire after
7 days." — both in family `term:share_link`, layer L1. Run through `evidence_for` and `score_of`:

| Source | Evidence | Points |
|---|---|---|
| S1 | family `term:share_link` | 3.0 |
| S2 | shared term `term:share_link` | 2.0 |
| S4 | both L1 | 1.0 |
| S5 | keywords `days`, `expire`, `share` | 1.5 |
| S6 | dimension `time`: 30 day vs 7 day | 2.5 |
| **score** | | **10.0** — far above the 1.0 bar |

(Notice `link` ≠ `links` as keywords: keywords are not folded to the singular; terms are.)

## Judgment: Q-PAIR and what a verdict becomes

The model returns one relation per pair (chapter 3). Code then applies `conflicts/records.py`:

| Relation | Link written | Conflict record? |
|---|---|---|
| `none` | — | — |
| `refines` | `refines` (directed) | no |
| `depends_on` | `depends_on` (directed) | no |
| `duplicates` | `duplicates` | **duplication** |
| `subsumes` | `subsumes` (directed) | **subsumption** — *only if* the two differ in modality or amount (profile default) |
| `contradicts` | `conflicts_with` | **contradiction** |

Before any of that, code **suppresses** verdicts the document's own form explains (F6 D16, D19):

- a `duplicates`/`subsumes` between an acceptance criterion and the requirement it `verifies` — a test
  restating its rule is design;
- the same between a criterion and any claim of **its own spec file**;
- the same between two claims of **one block**.

Contradictions are never suppressed — a test that contradicts its own rule is a real defect.

A `low` confidence verdict adds `low_confidence_verdict` ambiguity to both nodes. A verdict touching an
`ambiguous` node is kept but marked **provisional**.

### A conflict record (`.sdd/conflicts.jsonl`)

A real one from R18:

```json
{"id": "CF-000043", "kind": "contradiction", "members": ["N-000008", "N-000233"],
 "rationale": "A states F1 makes no model calls, while B requires recording telemetry for model calls (backend, model, tokens); these cannot both be true for the same F1 component at the same time.",
 "quotes": {"N-000008": "F1 makes **no model calls",
            "N-000233": "Every call records: backend, model as reported, CLI version, input and output tokens, cache tokens"},
 "state": "open", "resolved_reason": null, "detected_run": "R-000007", "resolved_run": null,
 "judgment": "J-003179"}
```

`judgment` points at the Q-PAIR answer in `.sdd/lock/q-pair.jsonl`, so every conflict can be traced to
the exact question, model, CLI version and cost that produced it.

Its members get the id in `conflict_ids`, and their status becomes `conflict`.

### The lifecycle of a conflict

| Event | Effect |
|---|---|
| The pair is judged again and the answer is not a conflict | Record closes, `resolved_reason: fixed` |
| The pair is judged again and still conflicts | Same record, same id, new quotes |
| A member node is deleted | Record closes, `member_deleted`; members kept as history |
| **An edit alone** | **Never closes a conflict** — only a re-judgment or a deletion does |
| A human records a verdict | Appended to `adjudications.jsonl`; the record itself is unchanged |

## Status: derived, in precedence order

```text
conflict      ← it is a member of an open conflict record
ambiguous     ← it has any ambiguity entry
stale         ← it has a stale reason (a judged neighbour was edited or deleted)
unchecked     ← its pairs have never been judged
validated     ← none of the above
```

The first that applies wins, and it is recomputed on every write — a stored status that disagrees
with its facts is rejected by the schema.

## R18, measured

| | |
|---|---|
| Verdicts | 4 251 — none 2 854 · subsumes 425 · depends_on 396 · refines 306 · contradicts 167 · duplicates 103 |
| Conflicts open | **381** — 167 contradiction · 157 subsumption · 57 duplication, in 95 groups |
| Distinct links | 4 199 — uses_term 2 819 · depends_on 396 · refines 306 · subsumes 286 · conflicts_with 167 · verifies 168 · duplicates 57 |

Reading the gap between rows: 103 `duplicates` verdicts became 57 duplication records and 425
`subsumes` became 157 subsumption records — the rest were suppressed by the rules above or were
subsumptions with no difference in modality or amount (a link, not a conflict).

⚠ **How many of the 381 are real is not yet known.** On a 181-block sample of the same specs, about
1 in 10 was (M4-gate §7). The main false-positive class still open: two criteria describing
*different situations* (exit `0` when clean, exit `5` when capped) read as contradicting each other.
The full adjudication (a seeded sample of 100) is the next step of R18.
