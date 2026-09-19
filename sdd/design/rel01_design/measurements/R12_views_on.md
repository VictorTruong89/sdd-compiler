# R12: every family card from the dense F5 compile (vocabulary on), for the M3 gate

> **Store:** the R12 "on" store, F5 only (65 blocks → 43 nodes, 18 families). It survived in an earlier
> session's scratch folder. A copy was rendered on 2026-09-19 with the M3 code *after* the gate review
> fixes (F4 D13 … D16). The first version of this file held only the two best cards, `candidate` and
> `pair_key`. This one holds **every** card, in map order.
> Statuses show `·` (unchecked) and `?` (ambiguous) only, because the check phase arrives with M4.
> Kept in the repo because scratch stores are not durable (I-50).

## Gate question and protocol

**Build-plan M3 gate:** *a person who has not read the graph can describe what a family contains from
the view alone.*

For each card, the reader writes one sentence saying what the family is about, using the card and
nothing else. There are three verdicts:

| Verdict | Meaning |
|---|---|
| ✅ | A coherent group. The sentence covers every line, and a reader of F5 would agree with it |
| ⚠️ | Describable, but only as one claim (a singleton) or with a stray member |
| ❌ | Misleading or incoherent: the name does not say what the lines are about, or the lines are fragments |

## Reading of every card

**Reader:** Claude, 2026-09-19. I have not read `F5_retrieval/spec.md`; I have seen only the node
texts. **Owner:** confirm or override the last column. The owner wrote F5, so the owner is not a
first-time reader. See the gate note below.

| Card | Nodes | One-sentence reading | Verdict | Why | Owner |
|---|---|---|---|---|---|
| candidate | 6 | Which candidate pairs survive: those under `min_score` are dropped, the rest are ranked and capped, and three criteria test it | ✅ | The 80-character cut hides the cap's value (F4 Q2) || ✅ agreed |
| evidence | 3 | Each candidate carries evidence, which is never empty and whose points sum to the score | ✅ | || ✅ agreed |
| pair_key | 3 | The key of a pair is symmetric, includes both text hashes, and changes when either text changes | ✅ | || ✅ agreed |
| pair | 2 | Pairs are listed exhaustively and keyed by `pair_key` | ⚠️ | Coherent, but two unrelated facts; `pair_key` is shown as narrower || ✅ agreed |
| checking_order | 1 | Nodes are checked in source order, so a run is reproducible | ⚠️ | Singleton || ✅ agreed |
| constraint | 1 | `(global)` constraints are proposed only against nodes sharing a term or keyword | ⚠️ | Singleton; "constraint" is a generic name || ✅ agreed |
| count_record | 1 | Each run records counts for measurement | ⚠️ | Singleton || ✅ agreed |
| last_checked_run | 1 | A batch run checks the whole graph, so `last_checked_run` is cheaper | ⚠️ | Singleton; the line is cut before its point || ✅ agreed |
| other_node | 1 | Goal: produce a small ranked set of other nodes to compare with | ⚠️ | Singleton; a fragment of the goal sentence || ✅ agreed |
| run_record | 1 | A run record carries the retrieval counts | ⚠️ | Singleton || ✅ agreed |
| score | 1 | Scoring is additive and capped per node | ⚠️ | Singleton || ✅ agreed |
| stop_word_list | 1 | One fixed, versioned stop-word list for keywords | ⚠️ | Singleton || ✅ agreed |
| (no family) | 3 | Exhaustive mode exists, is deterministic, is never used by compile; S5 and S6 are extra sources | ⚠️ | Not a family, but the lines are clear || ✅ agreed |
| **node** | **12** | "Tests about nodes" | ❌ | **The largest family is a grab-bag.** Nine criteria that test the sources S1 … S7 are filed under `node` because the Given clause's subject is "two nodes". A reader cannot tell that they are about candidate sources || ✅ agreed |
| node_selection | 2 | — | ❌ | Two fragments: "deterministically", "with no model call" || ✅ agreed |
| checked_node | 1 | Exhaustive mode returns all pairs among checked nodes | ❌ | The line is about exhaustive mode. It is filed by the Given clause's subject || ✅ agreed |
| contradiction | 1 | S5 catches wording overlap, S6 two numbers about one thing | ❌ | The line is about sources S5 and S6, not contradictions || ✅ agreed |
| measurement | 1 | An exhaustive mode for measurement only | ❌ | Filed under the purpose, not the thing || ✅ agreed |
| min_score_threshold | 1 | "They are starting values to tune…" | ❌ | "They" means the weights *and* `min_score`, and is not flagged `referential` || ✅ agreed |

**Tally:** ✅ 3 cards (12 of 43 nodes) · ⚠️ 10 (13 nodes) · ❌ 6 (18 nodes).

**Owner verdict, 2026-09-19:** the reading is approved row by row. **M3 gate result:** the view code
passes; the graph content fails the gate question. The fixes built the same day (F2 D18 … D20, F3 D32
for I-56; F5 D9 for I-57; F4 D17 for text width) are **not** reflected in the cards below. The cards
were rendered from the R12 store with the rule as it stood. R15 re-compiles F5 and re-reads every card
by the gate protocol (build-plan §3).

**Also seen:** exhaustive mode has about five claims and **no family**. They are spread over
`checked_node`, `measurement`, `pair` and `(no family)`, so F5's S1 (same family) will never pair them.

## Gate note (Claude's recommendation, for the owner)

- **The view code passes.** Every card shows exactly what the store holds. Every map row, `(no family)`
  included, now opens as a card. Nothing a reader needs is hidden, except text past 80 characters
  (F4 Q2).
- **The graph content fails the gate question for most families:** only 3 of 19 cards, holding 12 of 43
  nodes, read as a coherent group. The causes are upstream in M2, not in M3:
  - criteria are filed by their Given clause;
  - atoms are fragments;
  - families are named after a purpose instead of a subject.

  They matter for M4, because F5's S1 (same family, weight 3.0) is the strongest candidate source.
- **The protocol is weak as written.** The owner wrote F5 and is not a first-time reader, and the gate
  has no pass line. Suggested: a reader who has not seen the specs, the sentence-per-card protocol
  above, and a pass line the owner sets before reading.

---

## Map

| family | L0 | L1 | L2 | L3 | L4 | L5 | C | V | — |
|---|---|---|---|---|---|---|---|---|---|
| candidate |  | 2 · |  |  |  |  | 1 ? | 3 ? |  |
| checked_node |  |  |  |  |  |  |  | 1 · |  |
| checking_order |  |  |  |  |  |  | 1 ? |  |  |
| constraint |  |  |  |  |  |  | 1 ? |  |  |
| contradiction |  |  |  |  |  |  |  |  | 1 ? |
| count_record |  |  |  |  |  |  | 1 ? |  |  |
| evidence |  | 1 ? |  |  | 1 · |  |  | 1 · |  |
| last_checked_run |  |  |  |  | 1 ? |  |  |  |  |
| measurement |  |  |  |  |  | 1 · |  |  |  |
| min_score_threshold | 1 · |  |  |  |  |  |  |  |  |
| node |  | 1 ? |  |  | 1 · |  | 1 · | 9 ? |  |
| node_selection |  | 1 · |  |  |  | 1 · |  |  |  |
| other_node | 1 ? |  |  |  |  |  |  |  |  |
| pair | 1 · |  |  |  | 1 ? |  |  |  |  |
| pair_key |  |  |  |  | 2 · |  |  | 1 · |  |
| run_record |  |  |  |  |  |  |  | 1 · |  |
| score |  |  |  |  |  | 1 · |  |  |  |
| stop_word_list |  |  |  |  | 1 · |  |  |  |  |
| (no family) |  | 2 ? |  |  |  | 1 ? |  |  |  |

43 nodes · 18 families · 0 open conflicts
Marks: ✗ conflict · ? ambiguous · ~ stale · · unchecked · ✓ validated · column — no layer

### Card: candidate

#### L1 (2)
- N-000011 · Candidates below min_score (default 1.0) are dropped.
- N-000012 · The rest are ranked by score, then by node id, and the top max_pairs_per_node (…

#### C (1)
- N-000005 ? (referential) So every candidate carries why it was proposed, the counts are recorded, and an…

#### V (3)
- AC-5.8 ? (scope) Given a graph where a node's family, terms and block are unique to it, when can…
- AC-5.10 · Given 25 scoring candidates with max_pairs_per_node: 10, then exactly 10 are re…
- AC-5.11 · Given the same graph, when candidates are computed twice in different insertion…

#### In scope from elsewhere (3)
- N-000007 · Nodes whose text and whose candidates are unchanged since their last_checked_ru…
- N-000008 ? (missing_modality) Checking order is (source file, first line, node id), so a run is reproducible.
- N-000025 ? (referential) (global) constraints are proposed only against nodes sharing a term or a keywor…

**Related families:** count_record, min_score_threshold, node, run_record

### Card: checked_node

#### V (1)
- AC-5.15 · Given 6 checked nodes, when sddc pairs --exhaustive runs, then it returns all 1…

**In scope from elsewhere:** none
**Related families:** pair
**Kind of:** node

### Card: checking_order

#### C (1)
- N-000008 ? (missing_modality) Checking order is (source file, first line, node id), so a run is reproducible.

**In scope from elsewhere:** none
**Related families:** none

### Card: constraint

#### C (1)
- N-000025 ? (referential) (global) constraints are proposed only against nodes sharing a term or a keywor…

**In scope from elsewhere:** none
**Related families:** node

### Card: contradiction

#### — (1)
- N-000010 ? (unplaceable) S5 catches wording overlap without embeddings; S6 catches two numbers about the…

**In scope from elsewhere:** none
**Related families:** none

### Card: count_record

#### C (1)
- N-000019 ? (missing_modality, mixed_layers) Per run, for later measurement (G4): nodes checked, candidates proposed, pairs …

**In scope from elsewhere:** none
**Related families:** run_record

### Card: evidence

#### L1 (1)
- N-000009 ? (referential) Each source records the evidence it used.

#### L4 (1)
- N-000020 · evidence is never empty, and its points sum to score.

#### V (1)
- AC-5.9 · Given any candidate, then evidence is non-empty and its points sum exactly to s…

#### In scope from elsewhere (4)
- N-000005 ? (referential) So every candidate carries why it was proposed, the counts are recorded, and an…
- N-000007 · Nodes whose text and whose candidates are unchanged since their last_checked_ru…
- N-000008 ? (missing_modality) Checking order is (source file, first line, node id), so a run is reproducible.
- N-000025 ? (referential) (global) constraints are proposed only against nodes sharing a term or a keywor…

**Related families:** candidate, node, score

### Card: last_checked_run

#### L4 (1)
- N-000027 ? (missing_actor) A batch run checks the whole graph, so the cheaper last_checked_run plus stale_…

#### In scope from elsewhere (3)
- N-000005 ? (referential) So every candidate carries why it was proposed, the counts are recorded, and an…
- N-000007 · Nodes whose text and whose candidates are unchanged since their last_checked_ru…
- N-000025 ? (referential) (global) constraints are proposed only against nodes sharing a term or a keywor…

**Related families:** node

### Card: measurement

#### L5 (1)
- N-000023 · An exhaustive mode for measurement only.

#### In scope from elsewhere (3)
- N-000007 · Nodes whose text and whose candidates are unchanged since their last_checked_ru…
- N-000008 ? (missing_modality) Checking order is (source file, first line, node id), so a run is reproducible.
- N-000025 ? (referential) (global) constraints are proposed only against nodes sharing a term or a keywor…

**Related families:** none

### Card: min_score_threshold

**Also called:** min_score

#### L0 (1)
- N-000013 · They are starting values to tune with measurement, not findings.

#### In scope from elsewhere (1)
- N-000019 ? (missing_modality, mixed_layers) Per run, for later measurement (G4): nodes checked, candidates proposed, pairs …

**Related families:** measurement

### Card: node

#### L1 (1)
- N-000001 ? (missing_actor) For every node that needs checking

#### L4 (1)
- N-000006 · A node needs checking when its status is unchecked, or stale, or when it is amb…

#### C (1)
- N-000007 · Nodes whose text and whose candidates are unchanged since their last_checked_ru…

#### V (9)
- AC-5.1 · Given two nodes in family term:share_link, then each is a candidate for the oth…
- AC-5.2 ? (referential) Given two nodes sharing term:file (an entity) and two others sharing only term:…
- AC-5.3 ? (referential) Given a C node scoped to layer L3 and a node in L3, then the pair is proposed w…
- AC-5.4 · Given two nodes of one family in L1 and L2, then S4 contributes; given L1 and L…
- AC-5.5 · Given two nodes sharing 2 keywords and min_shared_keywords: 2, then S5 contribu…
- AC-5.6 · Given two nodes sharing term:share_link, one with "30 days" and one with "1 hou…
- AC-5.7 ? (referential) Given two nodes atomized from one block, then S7 contributes.
- AC-5.13 ? (referential) Given any node, then it is never its own candidate, and a pair appears at most …
- AC-5.14 · Given nodes with statuses unchecked, stale, validated (unchanged) and conflict,…

#### In scope from elsewhere (3)
- N-000005 ? (referential) So every candidate carries why it was proposed, the counts are recorded, and an…
- N-000008 ? (missing_modality) Checking order is (source file, first line, node id), so a run is reproducible.
- N-000025 ? (referential) (global) constraints are proposed only against nodes sharing a term or a keywor…

**Related families:** candidate, checked_node, evidence, last_checked_run, other_node, pair, run_record
**Narrower families:** checked_node (1), other_node (1)

### Card: node_selection

#### L1 (1)
- N-000003 · deterministically

#### L5 (1)
- N-000004 · with no model call

#### In scope from elsewhere (3)
- N-000007 · Nodes whose text and whose candidates are unchanged since their last_checked_ru…
- N-000008 ? (missing_modality) Checking order is (source file, first line, node id), so a run is reproducible.
- N-000025 ? (referential) (global) constraints are proposed only against nodes sharing a term or a keywor…

**Related families:** none

### Card: other_node

#### L0 (1)
- N-000002 ? (missing_actor) produce a small, ranked, explained set of other nodes worth comparing it against

#### In scope from elsewhere (2)
- N-000019 ? (missing_modality, mixed_layers) Per run, for later measurement (G4): nodes checked, candidates proposed, pairs …
- N-000025 ? (referential) (global) constraints are proposed only against nodes sharing a term or a keywor…

**Related families:** node
**Kind of:** node

### Card: pair

#### L0 (1)
- N-000016 · sddc pairs --exhaustive returns all pairs among the checked nodes, with their s…

#### L4 (1)
- N-000014 ? (referential, missing_modality) Its key is pair_key = sha256(min(id_a, id_b) + "|" + max(id_a, id_b) + "|" + te…

#### In scope from elsewhere (3)
- N-000005 ? (referential) So every candidate carries why it was proposed, the counts are recorded, and an…
- N-000007 · Nodes whose text and whose candidates are unchanged since their last_checked_ru…
- N-000019 ? (missing_modality, mixed_layers) Per run, for later measurement (G4): nodes checked, candidates proposed, pairs …

**Related families:** checked_node, pair_key, score
**Narrower families:** pair_key (3)

### Card: pair_key

#### L4 (2)
- N-000015 · The key changes when either node's text changes, which is exactly when the pair…
- N-000024 · pair_key includes both text hashes

#### V (1)
- AC-5.12 · Given nodes A and B, then pair_key(A,B) == pair_key(B,A) … when either node's t…

#### In scope from elsewhere (3)
- N-000005 ? (referential) So every candidate carries why it was proposed, the counts are recorded, and an…
- N-000007 · Nodes whose text and whose candidates are unchanged since their last_checked_ru…
- N-000025 ? (referential) (global) constraints are proposed only against nodes sharing a term or a keywor…

**Related families:** node, pair
**Kind of:** pair

### Card: run_record

#### V (1)
- AC-5.16 · Given a compile run, then the run record carries the CT-5.3 counts and they add…

**In scope from elsewhere:** none
**Related families:** count_record

### Card: score

#### L5 (1)
- N-000022 · Fixed additive scoring with a per-node cap.

#### In scope from elsewhere (3)
- N-000007 · Nodes whose text and whose candidates are unchanged since their last_checked_ru…
- N-000008 ? (missing_modality) Checking order is (source file, first line, node id), so a run is reproducible.
- N-000025 ? (referential) (global) constraints are proposed only against nodes sharing a term or a keywor…

**Related families:** none

### Card: stop_word_list

#### L4 (1)
- N-000026 · One fixed, versioned stop-word list in code for keywords

#### In scope from elsewhere (2)
- N-000005 ? (referential) So every candidate carries why it was proposed, the counts are recorded, and an…
- N-000007 · Nodes whose text and whose candidates are unchanged since their last_checked_ru…

**Related families:** none

### Card: (no family)

#### L1 (2)
- N-000017 ? (unresolved_term) the mode exists and is deterministic
- N-000018 ? (unresolved_term) Compilation never uses exhaustive mode: it is an offline measurement tool.

#### L5 (1)
- N-000021 ? (unresolved_term) Two extra candidate sources, S5 keywords and S6 same measured property, beyond …

#### In scope from elsewhere (3)
- N-000007 · Nodes whose text and whose candidates are unchanged since their last_checked_ru…
- N-000008 ? (missing_modality) Checking order is (source file, first line, node id), so a run is reproducible.
- N-000025 ? (referential) (global) constraints are proposed only against nodes sharing a term or a keywor…

**Related families:** none

