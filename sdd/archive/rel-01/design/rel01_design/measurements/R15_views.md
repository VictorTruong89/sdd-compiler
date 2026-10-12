# R15 — every family card from the F5 compile of 2026-09-21

> Rendered from the R15 store (64 nodes, 32 families) with the M3 code of 2026-09-21.
> Kept here because scratch stores are not durable (I-50). Gate write-up: [`../M3-gate.md`](../M3-gate.md).
> Statuses: `·` unchecked, `?` ambiguous (reasons in brackets); the check phase arrives with M4.

## Map

| family | L0 | L1 | L2 | L3 | L4 | L5 | C | V | — |
|---|---|---|---|---|---|---|---|---|---|
| atom |  | 1 ? |  |  |  |  |  | 1 · |  |
| candidate |  |  |  |  |  | 2 · | 2 ? | 2 · |  |
| checked_against |  |  |  |  | 1 · |  |  |  |  |
| checking_order |  | 1 ? |  |  |  |  |  |  |  |
| compilation |  |  |  |  |  |  | 1 · |  |  |
| contradiction |  |  |  |  |  | 1 ? |  |  |  |
| evidence |  | 1 ? |  |  | 1 · |  |  | 1 · |  |
| family |  | 1 · |  |  |  |  |  | 1 · |  |
| function |  |  | 1 ? |  |  |  |  |  |  |
| judged_pair |  | 1 ? |  |  |  |  |  |  |  |
| last_checked_run |  |  |  |  |  |  | 1 · |  |  |
| measurement | 1 · |  |  |  |  |  |  |  |  |
| node |  | 1 · |  |  | 1 · |  | 1 ? | 4 ? |  |
| node_filter |  | 1 · |  |  |  |  |  |  |  |
| nodes_checked |  |  |  |  |  |  | 1 · |  |  |
| number |  | 1 ? |  |  |  |  |  |  |  |
| pair |  | 1 ? |  |  | 2 ? |  |  | 2 · |  |
| pair_key |  |  |  |  | 1 · |  | 1 · | 1 · |  |
| project |  |  |  |  |  |  | 1 · |  |  |
| ranked_set |  | 1 ? |  |  |  |  |  |  |  |
| relation |  |  |  |  |  |  | 1 ? |  |  |
| run |  |  |  |  |  |  |  | 1 · |  |
| run_record |  |  |  |  |  |  | 1 ? | 1 · |  |
| scope_selector |  |  |  |  | 1 ? |  |  | 1 ? |  |
| scope_selector_coverage |  |  |  |  |  | 1 ? |  |  |  |
| score |  |  |  |  |  |  | 1 · |  |  |
| sddc_compile |  | 1 ? |  |  |  |  |  |  |  |
| selector |  |  |  |  |  | 1 · |  | 1 ? |  |
| shared_keyword |  | 1 ? |  |  |  |  |  | 2 ? |  |
| stop_word_list | 1 ? |  | 1 · |  |  |  |  |  |  |
| verdict |  |  |  |  | 1 ? |  |  |  |  |
| wording_overlap |  |  |  |  |  | 1 · |  |  |  |
| (global) |  |  |  |  |  |  | 4 ? |  |  |
| (no family) |  |  | 1 ? |  |  |  |  |  |  |

64 nodes · 32 families · 0 open conflicts
Marks: ✗ conflict · ? ambiguous · ~ stale · · unchecked · ✓ validated · column — no layer

### Card: atom

#### L1 (1)
- N-000020 ? (referential) S7 same source block · Both atomized from the same block · the block id

#### V (1)
- AC-5.7 · AC-5.7 (same block) — Given two nodes atomized from one block, then S7 contributes.

**In scope from elsewhere:** none
**Related families:** node

### Card: candidate

**Also called:** candidates proposed

#### L5 (2)
- N-000023 · Candidates below min_score (default 1.0) are dropped.
- N-000024 · The rest are ranked by score, then by node id, and the top max_pairs_per_node (default 10) are returned.

#### C (2)
- N-000002 ? (referential) So every candidate carries why it was proposed, the counts are recorded, and an exhaustive mode exists to measure what the ranked mode misses.
- N-000035 ? (scope) D1 — ⚑ Two extra candidate sources, S5 keywords and S6 same measured property, beyond the pre-rel01 rule.

#### V (2)
- AC-5.10 · AC-5.10 (cap and threshold) — Given 25 scoring candidates with max_pairs_per_node: 10, then exactly 10 are returned, they are the 10 highest, ties break by node id, and the run counts record 15 dropped by the cap.
- AC-5.11 · AC-5.11 (determinism) — Given the same graph, when candidates are computed twice in different insertion orders, then the results are identical, including rank order.

#### In scope from elsewhere (3)
- N-000027 · The key changes when either node's text changes, which is exactly when the pair must be judged again.
- N-000031 ? (missing_modality, mixed_layers) Per run, for later measurement (G4): nodes checked, candidates proposed, pairs after the cap, pairs dropped by min_score, pairs dropped by the cap, pairs replayed from the lock.
- N-000036 · D2 — ⚑ Fixed additive scoring with a per-node cap.

**Related families:** run_record, score, shared_keyword

### Card: checked_against

#### L4 (1)
- N-000047 · Deferred: checked_against per node

#### In scope from elsewhere (4)
- N-000027 · The key changes when either node's text changes, which is exactly when the pair must be judged again.
- N-000031 ? (missing_modality, mixed_layers) Per run, for later measurement (G4): nodes checked, candidates proposed, pairs after the cap, pairs dropped by min_score, pairs dropped by the cap, pairs replayed from the lock.
- N-000040 ? (referential) D6 — Starting values adopted (resolves Q1): max_pairs_per_node: 10, min_score: 1.0, min_shared_keywords: 2, and the §4.3 weights.
- N-000048 · A batch run checks the whole graph, so the cheaper last_checked_run plus stale_reasons is enough for rel01.

**Related families:** node

### Card: checking_order

#### L1 (1)
- N-000012 ? (mixed_layers) Checking order is (source file, first line, node id)

**In scope from elsewhere:** none
**Related families:** none

### Card: compilation

#### C (1)
- N-000030 · Compilation never uses exhaustive mode: it is an offline measurement tool.

**In scope from elsewhere:** none
**Related families:** none

### Card: contradiction

#### L5 (1)
- N-000022 ? (referential) S6 catches two numbers about the same thing, which is the most common real contradiction

#### In scope from elsewhere (1)
- N-000035 ? (scope) D1 — ⚑ Two extra candidate sources, S5 keywords and S6 same measured property, beyond the pre-rel01 rule.

**Related families:** number

### Card: evidence

#### L1 (1)
- N-000014 ? (referential) Each source records the evidence it used.

#### L4 (1)
- N-000033 · evidence is never empty, and its points sum to score.

#### V (1)
- AC-5.9 · AC-5.9 (evidence explains the score) — Given any candidate, then evidence is non-empty and its points sum exactly to score.

#### In scope from elsewhere (2)
- N-000031 ? (missing_modality, mixed_layers) Per run, for later measurement (G4): nodes checked, candidates proposed, pairs after the cap, pairs dropped by min_score, pairs dropped by the cap, pairs replayed from the lock.
- N-000040 ? (referential) D6 — Starting values adopted (resolves Q1): max_pairs_per_node: 10, min_score: 1.0, min_shared_keywords: 2, and the §4.3 weights.

**Related families:** candidate, score

### Card: family

#### L1 (1)
- N-000018 · S4 adjacent layer · Same family and layer distance ≤ 1 in the order L0…L5 · both layers

#### V (1)
- AC-5.4 · Given two nodes of one family in L1 and L2, then S4 contributes; given L1 and L4, then S4 does not.

#### In scope from elsewhere (1)
- N-000045 ? (mixed_layers) A layer-only selector is a global constraint within those layers, so it takes D7's bar: the node must also share a term or keyword.

**Related families:** node

### Card: function

#### L2 (1)
- N-000046 ? (mixed_layers) One function serves S3 and F4's card (model/scope.py).

**In scope from elsewhere:** none
**Related families:** none

### Card: judged_pair

#### L1 (1)
- N-000007 ? (referential, missing_modality) A person inspects what would be judged, or measures coverage

**In scope from elsewhere:** none
**Related families:** none
**Kind of:** pair

### Card: last_checked_run

#### C (1)
- N-000048 · A batch run checks the whole graph, so the cheaper last_checked_run plus stale_reasons is enough for rel01.

**In scope from elsewhere:** none
**Related families:** none

### Card: measurement

#### L0 (1)
- N-000037 · D3 — ⚑ An exhaustive mode for measurement only.

#### In scope from elsewhere (1)
- N-000029 ? (referential) That measurement belongs to G4; this spec only guarantees the mode exists and is deterministic.

**Related families:** none

### Card: node

#### L1 (1)
- N-000010 · Nodes whose text and whose candidates are unchanged since their last_checked_run are skipped

#### L4 (1)
- N-000009 · A node needs checking when its status is unchecked, or stale, or when it is ambiguous and was never judged.

#### C (1)
- N-000045 ? (mixed_layers) A layer-only selector is a global constraint within those layers, so it takes D7's bar: the node must also share a term or keyword.

#### V (4)
- AC-5.1 · Given two nodes in family term:share_link, then each is a candidate for the other with S1 evidence.
- AC-5.6 ? (referential) AC-5.6 (same measured property) — Given two nodes sharing term:share_link, one with "30 days" and one with "1 hour", then S6 contributes with dimension time and both values.
- AC-5.13 · AC-5.13 (no self pair, no duplicates) — Given any node, then it is never its own candidate, and a pair appears at most once per run.
- AC-5.14 ? (referential) AC-5.14 (which nodes are checked) — Given nodes with statuses unchecked, stale, validated (unchanged) and conflict, then the first two are checked, the validated one is skipped, and the conflict one is checked again.

#### In scope from elsewhere (3)
- N-000027 · The key changes when either node's text changes, which is exactly when the pair must be judged again.
- N-000040 ? (referential) D6 — Starting values adopted (resolves Q1): max_pairs_per_node: 10, min_score: 1.0, min_shared_keywords: 2, and the §4.3 weights.
- N-000048 · A batch run checks the whole graph, so the cheaper last_checked_run plus stale_reasons is enough for rel01.

**Related families:** candidate, last_checked_run
**Narrower families:** node_filter (1), nodes_checked (1)

### Card: node_filter

#### L1 (1)
- N-000008 · sddc pairs [--node ID] [--exhaustive] [--json]

#### In scope from elsewhere (1)
- N-000002 ? (referential) So every candidate carries why it was proposed, the counts are recorded, and an exhaustive mode exists to measure what the ranked mode misses.

**Related families:** none
**Kind of:** node

### Card: nodes_checked

#### C (1)
- N-000032 · These go into the run record (F1 CT-1.3, extended by CT-5.3).

**In scope from elsewhere:** none
**Related families:** candidate, run, run_record
**Kind of:** node

### Card: number

#### L1 (1)
- N-000025 ? (referential, missing_modality) Both numbers live in the profile (CT-5.2).

**In scope from elsewhere:** none
**Related families:** none

### Card: pair

#### L1 (1)
- N-000028 ? (referential) sddc pairs --exhaustive returns all pairs among the checked nodes, with their scores, without judging anything.

#### L4 (2)
- N-000026 ? (referential) Its key is pair_key = sha256(min(id_a, id_b) + "|" + max(id_a, id_b) + "|" + text_hash of each, in the same order).
- N-000039 ? (referential) an edit re-opens exactly the pairs it touches

#### V (2)
- AC-5.2 · Given two nodes sharing term:file (an entity) and two others sharing only term:owner (an actor), then the first pair is proposed with S2 evidence and the second is not proposed by S2.
- AC-5.15 · AC-5.15 (exhaustive mode) — Given 6 checked nodes, when sddc pairs --exhaustive runs, then it returns all 15 pairs with scores, judges nothing, and makes no model call.

#### In scope from elsewhere (6)
- N-000003 ? (referential) a pair never proposed is a relation never found
- N-000002 ? (referential) So every candidate carries why it was proposed, the counts are recorded, and an exhaustive mode exists to measure what the ranked mode misses.
- N-000027 · The key changes when either node's text changes, which is exactly when the pair must be judged again.
- N-000031 ? (missing_modality, mixed_layers) Per run, for later measurement (G4): nodes checked, candidates proposed, pairs after the cap, pairs dropped by min_score, pairs dropped by the cap, pairs replayed from the lock.
- N-000040 ? (referential) D6 — Starting values adopted (resolves Q1): max_pairs_per_node: 10, min_score: 1.0, min_shared_keywords: 2, and the §4.3 weights.
- N-000048 · A batch run checks the whole graph, so the cheaper last_checked_run plus stale_reasons is enough for rel01.

**Related families:** node, pair_key, score
**Narrower families:** judged_pair (1), pair_key (3)

### Card: pair_key

#### L4 (1)
- N-000038 · pair_key includes both text hashes

#### C (1)
- N-000027 · The key changes when either node's text changes, which is exactly when the pair must be judged again.

#### V (1)
- AC-5.12 · AC-5.12 (pair key symmetry and sensitivity) — Given nodes A and B, then pair_key(A,B) == pair_key(B,A); … when either node's text changes, then the key changes.

**In scope from elsewhere:** none
**Related families:** node, pair
**Kind of:** pair

### Card: project

#### C (1)
- N-000042 · two projects with different lists could not be compared

**In scope from elsewhere:** none
**Related families:** stop_word_list

### Card: ranked_set

#### L1 (1)
- N-000001 ? (scope) For every node that needs checking, produce a small, ranked, explained set of other nodes worth comparing it against — deterministically, with no model call.

#### In scope from elsewhere (1)
- N-000002 ? (referential) So every candidate carries why it was proposed, the counts are recorded, and an exhaustive mode exists to measure what the ranked mode misses.

**Related families:** node

### Card: relation

#### C (1)
- N-000003 ? (referential) a pair never proposed is a relation never found

**In scope from elsewhere:** none
**Related families:** pair

### Card: run

#### V (1)
- N-000013 · a run is reproducible

**In scope from elsewhere:** none
**Related families:** none
**Narrower families:** run_record (2)

### Card: run_record

#### C (1)
- N-000031 ? (missing_modality, mixed_layers) Per run, for later measurement (G4): nodes checked, candidates proposed, pairs after the cap, pairs dropped by min_score, pairs dropped by the cap, pairs replayed from the lock.

#### V (1)
- AC-5.16 · AC-5.16 (counts recorded) — Given a compile run, then the run record carries the CT-5.3 counts and they add up: proposed = capped + dropped_below_min_score + dropped_by_cap.

**In scope from elsewhere:** none
**Related families:** candidate, compilation, nodes_checked, number
**Kind of:** run

### Card: scope_selector

#### L4 (1)
- N-000015 ? (referential) A C node whose scope_selector covers the other node, in either direction

#### V (1)
- AC-5.3 ? (missing_actor) Given a C node scoped to category term:endpoint in layer L3 and an L3 node using term:endpoint, then the pair is proposed with S3 evidence naming the selector; given a C node scoped to L3 only and an L3 node sharing no term or keyword with it, then S3 does not contribute.

#### In scope from elsewhere (2)
- N-000027 · The key changes when either node's text changes, which is exactly when the pair must be judged again.
- N-000040 ? (referential) D6 — Starting values adopted (resolves Q1): max_pairs_per_node: 10, min_score: 1.0, min_shared_keywords: 2, and the §4.3 weights.

**Related families:** pair, selector

### Card: scope_selector_coverage

#### L5 (1)
- N-000016 ? (referential, missing_modality) by the rule of D9

#### In scope from elsewhere (1)
- N-000035 ? (scope) D1 — ⚑ Two extra candidate sources, S5 keywords and S6 same measured property, beyond the pre-rel01 rule.

**Related families:** none

### Card: score

#### C (1)
- N-000036 · D2 — ⚑ Fixed additive scoring with a per-node cap.

**In scope from elsewhere:** none
**Related families:** none

### Card: sddc_compile

#### L1 (1)
- N-000005 ? (missing_actor, missing_modality) sddc compile reaches the check phase

**In scope from elsewhere:** none
**Related families:** none

### Card: selector

#### L5 (1)
- N-000044 · A selector that names a family, term or category covers the nodes matching it, narrowed by its layers if it has any.

#### V (1)
- N-000017 ? (referential) the selector that matched

#### In scope from elsewhere (2)
- N-000031 ? (missing_modality, mixed_layers) Per run, for later measurement (G4): nodes checked, candidates proposed, pairs after the cap, pairs dropped by min_score, pairs dropped by the cap, pairs replayed from the lock.
- N-000045 ? (mixed_layers) A layer-only selector is a global constraint within those layers, so it takes D7's bar: the node must also share a term or keyword.

**Related families:** family, node

### Card: shared_keyword

#### L1 (1)
- N-000019 ? (missing_actor, pending_review) S5 shared keywords · At least min_shared_keywords (default 2) common keywords · the shared keywords

#### V (2)
- AC-5.5 ? (referential, inferred) Given two nodes sharing 2 keywords and min_shared_keywords: 2, then S5 contributes and names the shared keywords; given one shared keyword, then S5 does not.
- AC-5.8 · AC-5.8 (first node of a family) — Given a graph where a node's family, terms and block are unique to it, when candidates are gathered, then any candidate comes from S5 or S6, and the result may legitimately be empty.

**In scope from elsewhere:** none
**Related families:** candidate, family, node

### Card: stop_word_list

#### L0 (1)
- N-000043 ? (mixed_layers) the list is not the kind of thing a user should have to tune

#### L2 (1)
- N-000041 · One fixed, versioned stop-word list in code for keywords

#### In scope from elsewhere (2)
- N-000035 ? (scope) D1 — ⚑ Two extra candidate sources, S5 keywords and S6 same measured property, beyond the pre-rel01 rule.
- N-000042 · two projects with different lists could not be compared

**Related families:** none

### Card: verdict

#### L4 (1)
- N-000011 ? (referential) their verdicts are replayed from the judgment lock (F3 §4.7).

#### In scope from elsewhere (2)
- N-000027 · The key changes when either node's text changes, which is exactly when the pair must be judged again.
- N-000031 ? (missing_modality, mixed_layers) Per run, for later measurement (G4): nodes checked, candidates proposed, pairs after the cap, pairs dropped by min_score, pairs dropped by the cap, pairs replayed from the lock.

**Related families:** node

### Card: wording_overlap

#### L5 (1)
- N-000021 · S5 catches wording overlap without embeddings

#### In scope from elsewhere (2)
- N-000004 · Embeddings or any learned similarity (rel01: deterministic only; vision O2).
- N-000035 ? (scope) D1 — ⚑ Two extra candidate sources, S5 keywords and S6 same measured property, beyond the pre-rel01 rule.

**Related families:** none

### Card: (global)

#### C (4)
- N-000004 · Embeddings or any learned similarity (rel01: deterministic only; vision O2).
- N-000029 ? (referential) That measurement belongs to G4; this spec only guarantees the mode exists and is deterministic.
- N-000034 · F5 makes no model calls at all.
- N-000040 ? (referential) D6 — Starting values adopted (resolves Q1): max_pairs_per_node: 10, min_score: 1.0, min_shared_keywords: 2, and the §4.3 weights.

**In scope from elsewhere:** none
**Related families:** measurement

### Card: (no family)

#### L2 (1)
- N-000006 ? (referential, unresolved_term) sdd_compiler.retrieval::candidates_for

**In scope from elsewhere:** none
**Related families:** none
