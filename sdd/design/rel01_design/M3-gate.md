# M3 gate — can a reader describe a family from its card alone?

> **Status:** ✅ **APPROVED by the owner 2026-09-21** — §3's reading and §4's verdict as written:
> **M3's views pass; M3's content fails the pass line, and improved from 28 % to 47 % of nodes.**
> **Tier:** design, non-authoritative · **Opened** 2026-09-19 (review of R12's cards) ·
> **R15 measured** 2026-09-21. Run under the gate protocol in
> [`build-plan.md`](build-plan.md) §3. The first reading, with the owner's approved verdicts, is in
> [`measurements/R12_views_on.md`](measurements/R12_views_on.md); this file carries the re-measure.

## 1. Where the gate stood after the first reading (R12, 43 nodes)

The view code passed. The graph content did not: 3 of 19 cards (12 of 43 nodes) read as a coherent
group. Owner approved that reading on 2026-09-19. Four causes were fixed the same day (I-56, I-57):
Q-ATOM dropped table rows as `definition` (F3 D32); criteria were filed by their Given clause
(F2 D18); ids such as `S4` could not be cited (F2 D20); components never seeded a family (F2 D19).
A layer-only constraint scope no longer covers a whole layer (F5 D9).

## 2. R15 — the same spec, compiled again (2026-09-21)

`sddc compile` over **F5 alone**, fresh store, `claude-code` + Haiku, thinking off, vocabulary shown.
Raw output: [`measurements/R15_compile.json`](measurements/R15_compile.json),
[`measurements/R15_graph.json`](measurements/R15_graph.json), cards in
[`measurements/R15_views.md`](measurements/R15_views.md).

⚠ **Not a clean A/B.** F5 itself grew by today's amendments (AC-5.3, D9): 70 blocks against R12's 65.
Read the table as a direction, not a controlled comparison.

| | R12 "on" (2026-09-19) | R15 (2026-09-21) |
|---|---|---|
| Blocks pending · completed · failed | 65 · 64 · 1 | 66 · 62 · **4** |
| Blocks that formed no node | not reported | **15**, every one `context` (F3 D33) |
| Nodes · terms | 43 · 45 | **64** · 97 |
| Families · one-node families | 18 · 12 (67 %) | 32 · 20 (63 %) |
| Nodes in families of three or more | 24 of 43 (56 %) | 27 of 64 (42 %) |
| Family null · `(global)` | 3 · 0 | **1** · 4 |
| Terms used by one node | 19 of 45 (42 %) | 56 of 97 (58 %) |
| Criteria (`V`) in the `node` grab-bag | **9** | **4** |
| Criteria whose `verifies` resolved | 0 of 16 | **5 of 18** |
| S3 constraint-scope pairs, old rule → F5 D9 | ≈ 60 → 16 (43 nodes) | **178 → 42** (64 nodes) |
| Model calls · cost | 21 · $0.69 | 57 · **$1.20** |

**What the fixes did.** F5's seven candidate-source rows are claims now, not silent drops: `S3`, `S4`,
`S5` and `S7` formed nodes carrying their local label, and five criteria resolved `verifies` and moved
to the family of the rule they test. The grab-bag shrank from nine criteria to four. Family null fell
to one node. The constraint-scope flood is confirmed and contained on fresh data: the same store gives
178 pairs under the old rule and 42 under F5 D9.

**What got worse or stayed bad.**
- **Four blocks failed** (R12: one), all on one shape (I-63): the model quoted the `section` heading or
  the `table header` given as context. Three of them are the `S1`, `S2` and `S6` rows — which is why
  AC-5.1, AC-5.2 and AC-5.6 are still in `node`. Fixed after the run (F3 D34).
- **A row split per cell** (I-64): `S3` became three fragment nodes in three families
  (`scope_selector`, `scope_selector_coverage`, `selector`). Fixed after the run (F3 D34).
- **More terms, thinner families.** 97 terms for 64 nodes, 58 % used once, and only 42 % of nodes in a
  family of three or more. More content is captured, and it is spread over more names.
- **15 C nodes of 64**, 13 of them scoped by layer alone. Q-DESC still answers `scope_layers`
  generously; F5 D9 contains the consequence rather than the cause.
- **Cost per node** $0.019 against R12's $0.016, and 57 calls against 21 — re-asks after the four
  failures, and more Q-TERM work for 97 terms.

## 3. Reading of every card

Run under protocol step 3: the reader had only [`measurements/R15_views.md`](measurements/R15_views.md)
and no access to F5 or to the repository.

**Reader:** a fresh Claude agent, 2026-09-21, given the cards file and nothing else — no F5, no
repository. Its words, lightly trimmed. **Owner:** confirm or override the verdict column.

| Card | Nodes | Reader's one-sentence reading | Verdict | Why |
|---|---|---|---|---|
| **node** | **7** | Nodes are skipped when unchanged and checked when unchecked or stale — and separately, a selector constraint plus three unrelated tests about S1, S6 and pair duplication | ❌ | The largest card, and a dumping ground: four of seven lines are there only because they mention two nodes |
| candidate | 6 | Candidates are filtered by `min_score`, ranked and capped per node, carry evidence, and come from extra sources beyond the pre-rel01 rule | ✅ | |
| pair | 5 | `sddc pairs --exhaustive` lists all pairs with scores; a pair's key changes when a node's text changes; two tests | ✅ | Duplicates `pair_key`'s own definition |
| (global) | 4 | No embeddings, measurement belongs to G4, no model calls, D6's defaults | ❌ | Four unrelated topics united by "did not fit anywhere else" |
| evidence | 3 | Evidence is recorded per source, never empty, and its points sum exactly to the score | ✅ | |
| pair_key | 3 | `pair_key` hashes both texts, changes when either changes, and is symmetric, with a test | ✅ | Overlaps `pair` |
| shared_keyword | 3 | S5 proposes candidates on ≥ 2 shared keywords, with an example and an edge case | ✅ | |
| atom | 2 | Two nodes from one source block are related (S7), with a test | ✅ | |
| family | 2 | S4 matches nodes of one family within a layer of each other, with a test | ✅ | |
| run_record | 2 | The run record carries per-run counts, and they add up | ✅ | |
| scope_selector | 2 | A `C` node whose selector covers another node makes a candidate pair, with a test | ✅ | |
| stop_word_list | 2 | The keyword stop-word list is fixed, versioned and in code | ✅ | |
| selector | 2 | A selector names a family, term or category, narrowed by layer | ⚠️ | Its second line, "the selector that matched", is a fragment |
| checked_against · checking_order · compilation · contradiction · function · judged_pair · last_checked_run · measurement · node_filter · project · ranked_set · relation · run · score · sddc_compile · verdict · wording_overlap | 1 each | (17 single-claim cards, each readable on its own) | ⚠️ | A family of one groups nothing; `verdict` and `judged_pair` also dangle a pronoun |
| nodes_checked | 1 | "These" go into the run record | ❌ | No antecedent anywhere on the card |
| number | 1 | "Both numbers" live in the profile | ❌ | No antecedent |
| scope_selector_coverage | 1 | "by the rule of D9" | ❌ | Not a sentence: the I-64 row split |
| (no family) | 1 | `sdd_compiler.retrieval::candidates_for` | ❌ | A bare code path, not a claim |

**Tally:** ✅ **10 cards, 30 of 64 nodes** · ⚠️ 18 cards, 19 nodes · ❌ 6 cards, 15 nodes.

**Against the first reading** (R12, owner-approved): ✅ went from 3 of 19 cards and **28 % of nodes**
to 10 of 34 cards and **47 % of nodes**. The ❌ share fell from 18 of 43 nodes (42 %) to 15 of 64 (23 %).

**What the reader found that the numbers did not:**
1. **Dangling pronouns**: "These go into the run record", "Both numbers live in the profile", "their
   verdicts are replayed". Unresolvable from the card. These are the `referential` flags (21 of 64
   nodes), seen from the reader's side.
2. **The in-scope list is boilerplate**: the same six constraint nodes repeat on more than ten cards,
   padding them without saying anything about that family (**I-66**). F5 D9 cut the pairs from 178 to
   42; what is left is still noise on a card.
3. **The same concept in two families** (`pair` and `pair_key`), with nothing saying which owns it.
4. **Layer mis-tagging** on the fragments from the split row (fixed by F3 D34).
5. **The two non-family buckets** hold 5 of 64 nodes, which is the tool naming its own gaps.

## 4. Verdict

**Against the proposed pass line** — the largest family reads ✅, and ✅ cards hold at least half the
nodes — R15 **fails on both**: `node` is ❌, and ✅ cards hold 47 % of nodes. ⚠ The pass line was
proposed by Claude and is **not yet confirmed by the owner** (protocol step 1 was not satisfied for
this run: the line was written before the reading, but never approved).

**Claude's reading of the result.** The direction is right and the remaining distance is known:

- Of the four stray lines on the `node` card, **two** (AC-5.1, AC-5.6) are there because the `S1` and
  `S6` rows failed to atomize in this very run — the defect fixed afterwards as I-63. A run without
  that defect would very likely put them with their rules, leaving `node` with five lines, three of
  them coherent.
- One ❌ card (`scope_selector_coverage`) is the I-64 row split, also fixed afterwards.
- So **three of the six ❌ cards are artefacts of two defects that no longer exist in the code.**

### Owner's decision, 2026-09-21

**Approved as written.** M3 closes with its views passing and its content short of the line, and
**R16 is authorised** to get the first fair reading.

**⚠ For the retrospective — this gate broke its own protocol, twice, and both are worth keeping:**

1. **Step 1 was not satisfied for R15.** The pass line (largest family ✅, half the nodes in ✅ cards)
   was written before the reading but approved only after it, together with the result. That is
   exactly the bend the protocol exists to prevent, and it happened on the protocol's first run,
   written by the person who wrote the protocol. **From R16 on, the line is fixed and approved before
   the compile starts** — and it is: unchanged, the same two conditions.
2. **The evidence and the fixes were entangled.** Two defects (I-63, I-64) were found *by* R15 and
   fixed *before* its reading was finished, so the reading describes a store the code can no longer
   produce. Three of six ❌ cards are artefacts of them. **Rule for later gates: freeze the code at the
   moment the measured store is written; fixes found during a gate wait for the next run.**

**Also on record for the retrospective:**

- **The gate found what the test suite could not.** 522 unit, contract, property, golden and
  integration tests were green through every one of I-51 … I-66. Each was found by reading real output:
  the cards, the store, or a blind reader's sentences. A green suite says the code does what it was
  told; only real data says whether being told that was right.
- **The first reading was chosen by the builder** and held the two best cards (I-54). The blind
  all-cards reading gave a number three times worse on the same question. **Any self-selected sample of
  one's own work should be assumed flattering until drawn blind.**
- **Cost of the M3 gate:** R12 $1.55 (two arms), R15 $1.20, R16 ≈ $1.20 — roughly **$4 to learn that the
  atomizer's grouping is the weak part of the product**, against the M2 gate's $3.21. Cheap, and it
  arrived before M4 was built on top of it.
- **What M3 leaves for M4 to watch:** families are wide and thin (I-65), constraint scope is contained
  but its cause is not (Q-DESC's generous `scope_layers`), and F5's S1 (same family, weight 3.0) is the
  strongest retrieval source in a graph whose families group weakly. If M4's recall is poor, this is the
  first place to look.

**Recommended:** run **R16** — the same compile with I-63 and I-64 fixed (≈ $1.20, ~10 minutes) — and
read it under the protocol with the owner's pass line fixed first. Judge M3's content on that. If R16
is not worth the money, the honest record is: **M3's views pass; M3's content is better than at R12 and
still short of the line**, and the remaining gap (fragments, dangling pronouns, one-node families) is
an atomizer question for the retrospective, not a view question.


---

## 5. R16 — the same spec again, with I-63, I-64 and I-67 fixed (2026-09-21)

Raw output: [`measurements/R16_compile.json`](measurements/R16_compile.json),
[`measurements/R16_graph.json`](measurements/R16_graph.json), cards in
[`measurements/R16_views.md`](measurements/R16_views.md).

⚠ **Not the controlled A/B it was meant to be.** R16 was launched as "same source, changed code", and
it is not: the copy of F5 was taken after T15 had added **F5 D10** and filled the spec's traceability
table — 16 lines, about 5 extra blocks. *The corpus is the repository, and the repository is being
worked on while it is measured.* A measurement on one's own specs has no still control (build-plan
I-69). What follows is still a direction, and the qualitative changes are unambiguous.

⚠ **The first attempt at R16 crashed** and cost $1.20 for nothing (I-67). These numbers are the re-run.

| | R15 (2026-09-21) | R16 (2026-09-21, fixed) |
|---|---|---|
| Blocks pending · completed · **failed** | 66 · 62 · **4** | 71 · 70 · **1** |
| Blocks that formed no node | 15, all `context` | 20, `context` and `rationale` |
| Annotations dropped (F3 D35) | *(would have crashed)* | **1, and the run finished** |
| Nodes · terms | 64 · 97 | **73** · 88 |
| Terms used by one node | 56 of 97 (58 %) | 46 of 88 (**52 %**) |
| Families · one-node families | 32 · 20 (63 %) | 33 · 19 (**58 %**) |
| Nodes in families of three or more | 27 of 64 (42 %) | 35 of 73 (**48 %**) |
| Family null · `(global)` | 1 · 4 | 1 · 4 |
| **Criteria whose `verifies` resolved** | 5 of 18 | **10 of 23** |
| **Criteria left in the `node` grab-bag** | 4 | **3** |
| Source rows carrying a local label | `S3` `S4` `S5` `S7` (4 of 7) | **`S1` … `S7` (7 of 7)**, `D1` … `D10`, `T2` |
| S3 constraint-scope pairs | 42 (64 nodes) | **19** (73 nodes) |
| Model calls · cost | 57 · $1.20 | 65 · $1.31 |

**What the two fixes bought.** I-63 (never quote the context lines) took failures from 4 to 1, and with
the `S1`, `S2` and `S6` rows now atomized, every one of F5's seven candidate sources exists as a node
with its own label. I-64 (a row is one claim) removed the fragment families. Together they doubled the
criteria that resolve what they test, 5 of 18 → 10 of 23, and the chain the M3 gate cared about now
works end to end: **a criterion cites `S4`, the citation resolves to the `S4` row inside F5, and the
criterion joins that row's family** (AC-5.1 … AC-5.6 all do).

**What is still not fixed.** `node` is still the largest family. More than half the terms are still used
by one node, and 35 of 73 nodes are `ambiguous` — 27 of them `referential`, the dangling pronouns the
first reader tripped over. Cost per node is flat ($0.019 → $0.018).

**F3 D35 proved itself live:** the same merged rationale quote that killed the first attempt was dropped,
reported, and the run finished.


## 6. The blind reading of R16 — and why it got worse

Same protocol, a fresh reader with the cards and nothing else.

| | R15 | R16 |
|---|---|---|
| Cards | 34 | 35 |
| ✅ coherent | **10** | **4** (atom, candidate, evidence, shared_keyword) |
| ⚠️ thin or one stray line | 18 | 19 |
| ❌ misleading or incoherent | 6 | **12** |
| Largest card reads as a group? | no (`node`, 7) | no (`node`, 12) |

⚠ The two readings' **node** tallies are not comparable: R16's reader counted the "In scope from
elsewhere" lines into each card's total (92 against 73 real nodes), R15's did not. The **card** counts
above are comparable; the node buckets from the two readings are not.

**The mechanics improved and the reading got worse.** Both are true, and the second is the one that
matters for M3's question. Three causes, all now understood:

1. **I-70 — the split re-ask undid F3 D34.** A row's atoms are folded into one claim on the first
   pass, and then the split re-ask (AC-3.12) asked the model to separate the row's rule from its
   evidence column, and it obliged. **Every one of F5's seven source rows became two nodes**, one of
   them a bare fragment: "the term ids", "the block id", "family id", "both layers", "the selector that
   matched". The reader called five of these out by name. Fixed as **F3 D36**: a block that holds one
   claim by its own form — a table row (D34) or an `AC-` block (D28) — is placed by its first yes and
   flagged `mixed_layers`, and is never asked to split. It also saves a model call per such block.
2. **I-66 got worse, and is now the top complaint.** One recycled constraint line appears, via "In
   scope from elsewhere", on **8 unrelated cards**, padding their counts and explaining nothing about
   the family named at the top.
3. **More content, thinner topics.** 73 nodes over 35 cards. Capturing what R12 dropped (I-59) made the
   graph wider before it made it denser.

**Verdict against the pass line** (largest family ✅, half the nodes in ✅ cards): **R16 fails**, as R15
did, and by the card measure it is further away. With I-70 fixed, fourteen of R16's nodes — the seven
row fragments and the families they created (`block_id`, `term_ids`, `layer_distance`, `value`,
`selector`) — would not exist, and five ❌ cards would go with them. **That is a prediction, not a
measurement: no run has been made since the fix.**

**M3 closes here regardless.** M3's deliverable is the views, and they pass: every row opens, every
card shows what the store holds, and three successive readings have each found real defects in the
graph the views were showing. The content is an atomizer question, and its remaining distance is now
written down with a named cause for each part.
