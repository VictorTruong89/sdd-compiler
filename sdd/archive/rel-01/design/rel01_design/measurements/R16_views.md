# R16 — every family card from the F5 compile of 2026-09-21 (after the I-63, I-64, I-67 fixes)

> Rendered from the R16 store (73 nodes, 33 families). Gate write-up: [`../M3-gate.md`](../M3-gate.md).
> Statuses: `·` unchecked, `?` ambiguous (reasons in brackets); the check phase arrives with M4.

## Map

| family | L0 | L1 | L2 | L3 | L4 | L5 | C | V | — |
|---|---|---|---|---|---|---|---|---|---|
| atom |  |  |  |  | 1 ? |  |  | 1 · |  |
| block_id |  |  |  |  |  |  |  | 1 ? |  |
| candidate |  | 2 · |  |  |  |  | 1 · | 1 · |  |
| comparison_set |  | 1 ? |  |  |  |  |  |  |  |
| compilation |  |  |  |  |  |  | 1 · |  |  |
| count |  |  |  |  | 1 ? |  |  |  |  |
| count_proposal |  |  |  |  | 1 ? |  |  |  |  |
| evidence |  |  |  |  | 2 ? |  |  | 1 · |  |
| family |  |  |  |  | 1 ? |  |  | 3 ? |  |
| graph |  |  |  |  |  |  |  | 1 · |  |
| identity |  |  |  |  | 1 ? |  |  |  |  |
| judgment |  | 1 ? |  |  |  |  |  |  |  |
| key |  |  | 1 ? |  |  |  |  |  |  |
| last_checked_run |  |  |  |  | 1 · |  |  |  |  |
| layer_distance |  |  |  |  |  |  | 1 · |  |  |
| max_pairs_per_node |  |  |  |  | 1 · |  |  |  |  |
| measurement | 1 ? |  |  |  |  |  | 1 ? |  |  |
| min_score |  |  |  |  | 1 ? |  | 1 ? |  |  |
| node |  | 2 ? |  |  | 1 · | 2 ? | 1 ? | 3 ? |  |
| other_node |  |  | 1 ? |  |  |  |  | 1 · |  |
| pair_key |  | 1 · |  |  | 3 ? |  |  | 2 · |  |
| related_node_pair |  | 2 · |  |  |  |  |  | 2 · |  |
| run_record |  |  |  |  |  |  |  | 1 · |  |
| score |  |  |  |  |  |  | 1 · |  |  |
| selector |  |  |  |  | 1 ? | 1 ? |  |  |  |
| shared_keyword |  | 1 ? |  |  |  |  | 1 · | 3 · |  |
| source_file |  |  | 1 ? |  |  |  |  |  |  |
| stop_word_list |  |  |  |  |  | 1 · |  |  |  |
| term |  |  |  |  | 1 ? |  |  | 1 ? |  |
| term_ids |  |  |  |  |  |  |  | 1 ? |  |
| value |  |  |  |  |  |  | 1 ? | 1 · |  |
| verdict |  |  |  |  | 1 ? |  |  |  |  |
| weight |  |  |  |  |  | 1 · |  |  |  |
| (global) |  |  |  |  |  |  | 4 ? |  |  |
| (no family) |  |  |  |  |  | 1 ? |  |  |  |

73 nodes · 33 families · 0 open conflicts
Marks: ✗ conflict · ? ambiguous · ~ stale · · unchecked · ✓ validated · column — no layer

### Card: atom

#### L4 (1)
- N-000025 ? (missing_modality) Both atomized from the same block

#### V (1)
- AC-5.7 · Given two nodes atomized from one block, then S7 contributes.

**In scope from elsewhere:** none
**Related families:** node

### Card: block_id

#### V (1)
- N-000026 ? (referential) the block id

**In scope from elsewhere:** none
**Related families:** none

### Card: candidate

#### L1 (2)
- N-000027 · Candidates below min_score (default 1.0) are dropped.
- N-000028 · The rest are ranked by score, then by node id, and the top max_pairs_per_node (default 10) are returned.

#### C (1)
- N-000003 · So every candidate carries why it was proposed, the counts are recorded, and an exhaustive mode exists to measure what the ranked mode misses.

#### V (1)
- AC-5.10 · Given 25 scoring candidates with max_pairs_per_node: 10, then exactly 10 are returned, they are the 10 highest, ties break by node id, and the run counts record 15 dropped by the cap.

**In scope from elsewhere:** none
**Related families:** count, max_pairs_per_node, min_score, run_record, score

### Card: comparison_set

#### L1 (1)
- N-000001 ? (referential) For every node that needs checking, produce a small, ranked, explained set of other nodes worth comparing it against

**In scope from elsewhere:** none
**Related families:** node

### Card: compilation

#### C (1)
- N-000035 · Compilation never uses exhaustive mode: it is an offline measurement tool.

**In scope from elsewhere:** none
**Related families:** none

### Card: count

#### L4 (1)
- N-000037 ? (referential, missing_modality) These go into the run record (F1 CT-1.3, extended by CT-5.3).

#### In scope from elsewhere (1)
- N-000046 ? (referential, scope, mixed_layers) They are starting values, not findings: the run counts (CT-5.3) and the exhaustive mode exist so G4 can replace them with measured ones.

**Related families:** run_record

### Card: count_proposal

#### L4 (1)
- N-000054 ? (pending_review) The CT-5.3 counts count proposals, not distinct pairs

#### In scope from elsewhere (1)
- N-000046 ? (referential, scope, mixed_layers) They are starting values, not findings: the run counts (CT-5.3) and the exhaustive mode exist so G4 can replace them with measured ones.

**Related families:** none

### Card: evidence

#### L4 (2)
- N-000010 ? (referential) Each source records the evidence it used.
- N-000038 · evidence is never empty, and its points sum to score.

#### V (1)
- AC-5.9 · Given any candidate, then evidence is non-empty and its points sum exactly to score.

**In scope from elsewhere:** none
**Related families:** candidate, score

### Card: family

#### L4 (1)
- N-000017 ? (referential) Same family

#### V (3)
- N-000012 · family id
- N-000019 ? (referential) both layers
- AC-5.4 · Given two nodes of one family in L1 and L2, then S4 contributes; given L1 and L4, then S4 does not.

#### In scope from elsewhere (1)
- N-000018 · layer distance ≤ 1 in the order L0…L5

**Related families:** node

### Card: graph

#### V (1)
- AC-5.11 · Given the same graph, when candidates are computed twice in different insertion orders, then the results are identical, including rank order.

**In scope from elsewhere:** none
**Related families:** candidate

### Card: identity

#### L4 (1)
- N-000055 ? (mixed_layers) AC-5.16's identity (proposed = capped + dropped_below_min_score + dropped_by_cap) only holds if every number counts proposals

#### In scope from elsewhere (1)
- N-000046 ? (referential, scope, mixed_layers) They are starting values, not findings: the run counts (CT-5.3) and the exhaustive mode exist so G4 can replace them with measured ones.

**Related families:** pair_key

### Card: judgment

#### L1 (1)
- N-000005 ? (referential) A person inspects what would be judged, or measures coverage

**In scope from elsewhere:** none
**Related families:** none

### Card: key

#### L2 (1)
- N-000033 ? (referential) F6 uses it for the judgment lock, and F5 uses it to drop pairs already judged in this run.

**In scope from elsewhere:** none
**Related families:** related_node_pair

### Card: last_checked_run

#### L4 (1)
- N-000057 · A batch run checks the whole graph, so the cheaper last_checked_run plus stale_reasons is enough for rel01.

#### In scope from elsewhere (1)
- N-000046 ? (referential, scope, mixed_layers) They are starting values, not findings: the run counts (CT-5.3) and the exhaustive mode exist so G4 can replace them with measured ones.

**Related families:** none

### Card: layer_distance

#### C (1)
- N-000018 · layer distance ≤ 1 in the order L0…L5

**In scope from elsewhere:** none
**Related families:** none

### Card: max_pairs_per_node

#### L4 (1)
- N-000045 · D6 — Starting values adopted (resolves Q1): max_pairs_per_node: 10, min_score: 1.0, min_shared_keywords: 2, and the §4.3 weights.

#### In scope from elsewhere (2)
- N-000036 ? (referential) Per run, for later measurement (G4): nodes checked, candidates proposed, pairs after the cap, pairs dropped by min_score, pairs dropped by the cap, pairs replayed from the lock.
- N-000046 ? (referential, scope, mixed_layers) They are starting values, not findings: the run counts (CT-5.3) and the exhaustive mode exist so G4 can replace them with measured ones.

**Related families:** min_score, weight

### Card: measurement

#### L0 (1)
- N-000043 ? (referential, missing_modality) this is the only honest way to measure it.

#### C (1)
- N-000042 ? (mixed_layers) An exhaustive mode for measurement only.

**In scope from elsewhere:** none
**Related families:** pair_key

### Card: min_score

#### L4 (1)
- N-000029 ? (referential, missing_modality) Both numbers live in the profile (CT-5.2).

#### C (1)
- N-000030 ? (referential) They are starting values to tune with measurement, not findings.

#### In scope from elsewhere (2)
- N-000036 ? (referential) Per run, for later measurement (G4): nodes checked, candidates proposed, pairs after the cap, pairs dropped by min_score, pairs dropped by the cap, pairs replayed from the lock.
- N-000046 ? (referential, scope, mixed_layers) They are starting values, not findings: the run counts (CT-5.3) and the exhaustive mode exist so G4 can replace them with measured ones.

**Related families:** max_pairs_per_node, measurement

### Card: node

#### L1 (2)
- N-000007 ? (referential) Nodes whose text and whose candidates are unchanged since their last_checked_run are skipped
- N-000011 ? (referential) Same family (not (global))

#### L4 (1)
- N-000006 · A node needs checking when its status is unchecked, or stale, or when it is ambiguous and was never judged.

#### L5 (2)
- N-000048 · (global) constraints are proposed only against nodes sharing a term or a keyword with them
- N-000052 ? (referential) the node must also share a term or keyword

#### C (1)
- N-000036 ? (referential) Per run, for later measurement (G4): nodes checked, candidates proposed, pairs after the cap, pairs dropped by min_score, pairs dropped by the cap, pairs replayed from the lock.

#### V (3)
- AC-5.1 · Given two nodes in family term:share_link, then each is a candidate for the other with S1 evidence.
- AC-5.13 ? (referential) Given any node, then it is never its own candidate, and a pair appears at most once per run.
- AC-5.14 ? (referential) Given nodes with statuses unchecked, stale, validated (unchanged) and conflict, then the first two are checked, the validated one is skipped, and the conflict one is checked again.

#### In scope from elsewhere (3)
- N-000003 · So every candidate carries why it was proposed, the counts are recorded, and an exhaustive mode exists to measure what the ranked mode misses.
- N-000009 · Checking order is (source file, first line, node id), so a run is reproducible.
- N-000041 · Fixed additive scoring with a per-node cap.

**Related families:** candidate, count, family, last_checked_run, min_score, related_node_pair, term
**Narrower families:** other_node (2)

### Card: other_node

#### L2 (1)
- N-000015 ? (referential, missing_modality, mixed_layers) A C node whose scope_selector covers the other node, in either direction

#### V (1)
- AC-5.3 · Given a C node scoped to category term:endpoint in layer L3 and an L3 node using term:endpoint, then the pair is proposed with S3 evidence naming the selector; given a C node scoped to L3 only and an L3 node sharing no term or keyword with it, then S3 does not contribute.

**In scope from elsewhere:** none
**Related families:** pair_key, selector
**Kind of:** node

### Card: pair_key

**Also called:** pair

#### L1 (1)
- N-000034 · sddc pairs --exhaustive returns all pairs among the checked nodes, with their scores, without judging anything.

#### L4 (3)
- N-000031 ? (referential, missing_modality) Its key is pair_key = sha256(min(id_a, id_b) + "|" + max(id_a, id_b) + "|" + text_hash of each, in the same order).
- N-000032 ? (mixed_layers) The key changes when either node's text changes, which is exactly when the pair must be judged again.
- N-000044 · pair_key includes both text hashes, so an edit re-opens exactly the pairs it touches.

#### V (2)
- AC-5.12 · Given nodes A and B, then pair_key(A,B) == pair_key(B,A); when either node's text changes, then the key changes.
- N-000056 · The pairs handed to F6 hold each pair_key once

#### In scope from elsewhere (1)
- N-000018 · layer distance ≤ 1 in the order L0…L5

**Related families:** judgment, node, related_node_pair, score

### Card: related_node_pair

#### L1 (2)
- N-000022 · Shares a term
- N-000023 · both carry a quantity of the same dimension (time, size, count, percent)

#### V (2)
- AC-5.6 · Given two nodes sharing term:share_link, one with "30 days" and one with "1 hour", then S6 contributes with dimension time and both values.
- AC-5.15 · Given 6 checked nodes, when sddc pairs --exhaustive runs, then it returns all 15 pairs with scores, judges nothing, and makes no model call.

**In scope from elsewhere:** none
**Related families:** node, term

### Card: run_record

#### V (1)
- AC-5.16 · Given a compile run, then the run record carries the CT-5.3 counts and they add up: proposed = capped + dropped_below_min_score + dropped_by_cap.

**In scope from elsewhere:** none
**Related families:** compilation, count

### Card: score

#### C (1)
- N-000041 · Fixed additive scoring with a per-node cap.

**In scope from elsewhere:** none
**Related families:** max_pairs_per_node

### Card: selector

#### L4 (1)
- N-000016 ? (referential, scope, missing_modality) the selector that matched

#### L5 (1)
- N-000050 ? (referential) A selector that names a family, term or category covers the nodes matching it, narrowed by its layers if it has any.

#### In scope from elsewhere (1)
- N-000051 ? (referential, missing_modality, mixed_layers) A layer-only selector is a global constraint within those layers

**Related families:** family, node, term

### Card: shared_keyword

#### L1 (1)
- N-000020 ? (missing_actor) At least min_shared_keywords (default 2) common keywords

#### C (1)
- N-000040 · Two extra candidate sources, S5 keywords and S6 same measured property, beyond the pre-rel01 rule.

#### V (3)
- N-000021 · the shared keywords
- AC-5.5 · Given two nodes sharing 2 keywords and min_shared_keywords: 2, then S5 contributes and names the shared keywords; given one shared keyword, then S5 does not.
- AC-5.8 · Given a graph where a node's family, terms and block are unique to it, when candidates are gathered, then any candidate comes from S5 or S6, and the result may legitimately be empty.

**In scope from elsewhere:** none
**Related families:** candidate, family, node, term

### Card: source_file

#### L2 (1)
- N-000053 ? (referential) One function serves S3 and F4's card (model/scope.py).

**In scope from elsewhere:** none
**Related families:** none

### Card: stop_word_list

#### L5 (1)
- N-000049 · One fixed, versioned stop-word list in code for keywords

#### In scope from elsewhere (2)
- N-000040 · Two extra candidate sources, S5 keywords and S6 same measured property, beyond the pre-rel01 rule.
- N-000041 · Fixed additive scoring with a per-node cap.

**Related families:** none

### Card: term

#### L4 (1)
- N-000013 ? (missing_modality) Shares a term of kind entity, data or event

#### V (1)
- AC-5.2 ? (referential) Given two nodes sharing term:file (an entity) and two others sharing only term:owner (an actor), then the first pair is proposed with S2 evidence and the second is not proposed by S2.

#### In scope from elsewhere (1)
- N-000018 · layer distance ≤ 1 in the order L0…L5

**Related families:** node, pair_key
**Narrower families:** term_ids (1)

### Card: term_ids

#### V (1)
- N-000014 ? (referential) the term ids

**In scope from elsewhere:** none
**Related families:** none
**Kind of:** term

### Card: value

**Also called:** starting value

#### C (1)
- N-000046 ? (referential, scope, mixed_layers) They are starting values, not findings: the run counts (CT-5.3) and the exhaustive mode exist so G4 can replace them with measured ones.

#### V (1)
- N-000024 · the dimension and both values

**In scope from elsewhere:** none
**Related families:** none

### Card: verdict

#### L4 (1)
- N-000008 ? (referential, mixed_layers) their verdicts are replayed from the judgment lock (F3 §4.7)

**In scope from elsewhere:** none
**Related families:** node

### Card: weight

#### L5 (1)
- N-000047 · Changing a weight or a threshold is a profile change, never a code change.

#### In scope from elsewhere (1)
- N-000046 ? (referential, scope, mixed_layers) They are starting values, not findings: the run counts (CT-5.3) and the exhaustive mode exist so G4 can replace them with measured ones.

**Related families:** none

### Card: (global)

#### C (4)
- N-000002 · deterministically, with no model call
- N-000009 · Checking order is (source file, first line, node id), so a run is reproducible.
- N-000039 · No test calls a model: F5 makes no model calls at all.
- N-000051 ? (referential, missing_modality, mixed_layers) A layer-only selector is a global constraint within those layers

**In scope from elsewhere:** none
**Related families:** source_file

### Card: (no family)

#### L5 (1)
- N-000004 ? (unresolved_term) ✗ Embeddings or any learned similarity (rel01: deterministic only; vision O2).

#### In scope from elsewhere (1)
- N-000040 · Two extra candidate sources, S5 keywords and S6 same measured property, beyond the pre-rel01 rule.

**Related families:** none
