# Core Working Principle — Working Design

> **Status:** In progress · **Opened:** 2026-09-13 · **Tier:** design — **proposals, not yet adopted**.
> **Serves:** first release **U1 · U2 · U5** ([`../vision.md`](../../archive/2026-09-13_vision_pre-rel01.md) §1). **Designs for, does
> not build:** U7.
> **Binds to:** vision O1 (deterministic core, relaxed in later releases), O2 (the agent makes
> language judgments), O3 (runs through the agent's hooks and API).
> **Lecture companions:** [`core-working-principle.html`](../../../docs/lectures/core-working-principle.html) explains the
> reasoning and alternatives; [`lecture-tiered-md-vs-graph.html`](../../../docs/lectures/lecture-tiered-md-vs-graph.html)
> compares against tiered Markdown specs, storage and visualization. **If the two disagree, this file wins** (vision §5).
> **Evidence rule:** this file states no accuracy, coverage or token figure. Every quantitative
> property is written as *to be measured*. Named methods are listed in §12 as *to verify*.

**How to read the ids.**

- **`P-n`** is a proposal waiting for the owner to accept or reject it.
- **`Q-*`** is a question kind the compiler sends to the agent.
- **`G-n`** is a deterministic guard (a check done in code).
- **`N-n`** is a node in the worked example (§9).

>
> ⚠ **Pre-rel01 document (moved 2026-09-14).** "vision O1–O3 / U1–U7" point to the archived vision.
> ★ **Scoped by rel01 D26 (2026-09-17):** rel01 is a **batch** compiler over static Markdown. Where this
> document assumes interactive authoring — "one button press", per-press checking, an author confirming
> at the commit point, hook-carried questions — read it as *one command over the whole spec set*. The
> graph model, guards, placement, family rule, retrieval and storage are unaffected.
> ✅ **Proposals P-0…P-14 approved in rel01 D12**, amended by later rel01 decisions that win where
> they differ: status names and values (D9, D15), conflict storage (D9, D14), P-11 deferred, P-14
> realized first as the collapsed human form (D10). See [`../rel01_brainstorm.md`](../rel01_brainstorm.md).
---

## 1. The frame

### 1.1 What is compiled

| Program compiler | SDD Compiler | Done by |
|---|---|---|
| Source files | Spec documents in prose (Markdown), one writer at a time | Author (human or AI) |
| Lexing / parsing | **Atomization**: prose → atomic nodes (§3) | Agent answers, compiler checks |
| Symbol table | **Term registry**: canonical names of actors, entities, components (§4.4) | Agent proposes, compiler resolves |
| Semantic analysis | **Placement** (§4) and **linking** (§5) | Agent answers small questions, compiler maps |
| Intermediate representation | **The spec graph** | Compiler |
| Back ends | Diff against the as-built graph (U5, §8) · context packs for code generation (U7, §6) | Compiler |

> **P-0 · Prose is the source of truth; the graph is compiled.**
>
> - **What:** the Markdown spec files are authoritative. The graph is a build artifact derived from them. It is stored as plain text next to the specs and versioned in git. Nobody edits the graph by hand.
> - **Why:**
>   - U1: every spec-driven project already has prose files.
>   - Single writer: there is no concurrent graph editing to reconcile.
>   - U5: an as-built spec set is also prose, so both sides enter the compiler the same way.
> - **Cost:** every change must round-trip through prose. There is no "just fix the edge" shortcut.

### 1.2 The boundary: small questions, checked at once

Release 1 splits the work in two:

- The compiler's **code is deterministic**.
- Every language judgment is a **small, closed question** sent to the user's AI agent.

The compiler never asks an open question such as "analyze this spec". It asks one narrowly scoped
question, validates the answer immediately, and does everything else itself.

```text
COMPILER (code)          AGENT (judgment)            COMPILER (code)
───────────────          ────────────────            ───────────────
1 segment blocks   ──►   2 Q-ATOM: roles, atoms,  ──► 3 guards G1–G6
                            verbatim quotes
                   ◄──────────────────────────────────┘
                         4 Q-DESC: canonical form, ──► 5 map layer, resolve terms,
                            7 layer answers, terms       derive family, candidates
                   ◄──────────────────────────────────┘
                         6 Q-PAIR: judge one        ──► 7 author confirms → commit
                            candidate pair               graph + judgment lock
```

#### Question kinds (release 1)

| Kind | Input (small, bounded) | Output (schema-bound) | Checked by |
|---|---|---|---|
| **Q-ATOM** | One source block (one paragraph or list item) + its heading path | Sentence roles; atoms, each with **verbatim quotes** | G2 quotes found verbatim · G3 coverage · G5 schema |
| **Q-DESC** | One atom + its source block | Canonical fields (§3.3); answers to layer questions Q1–Q7, each yes/no + quote (§4.2); term tags | G4 no injection · G5 schema · T3 consistency (§4.2) |
| **Q-TERM** | One proposed term + candidate existing terms | `same` · `different` · `unsure` + reason | G5 schema; any `same` or `unsure` goes to the author |
| **Q-PAIR** | Two nodes + the relation question | Relation kind + rationale + quotes (§5) | G2 · G5 · the kind must be allowed for the two nodes' layers |

#### The check-immediately rule

1. Every answer is validated **the moment it arrives**, before any other question depends on it.
2. **On failure,** re-ask **once**, with the specific failed check included in the question.
3. **On a second failure,** the item goes to the author with status `unchecked` and the failed check
   visible. It is **never accepted silently**.
4. **Batching** several independent small questions into one agent call is allowed only if each
   answer is validated separately, and a failure re-asks only the failed item.

> **P-1 · Judgment lock.** Every accepted answer is stored as a record:
>
> ```yaml
> judgment:
>   kind: Q-DESC
>   input_hash: sha256(input text + question schema version)
>   agent: claude-code
>   model: <as reported>
>   prompt_version: q-desc/1
>   answer: { ... }
>   confirmed: author | auto
> ```
>
> A rebuild **replays** the lock. The agent is asked again only when an input hash or a schema
> version changes. Same sources plus same lock gives an identical graph. Future local ML models
> (vision O1) record their outputs in the same lock, pinned by model version.

### 1.3 Four operations per node

| Question about a node | Operation | Section |
|---|---|---|
| What exactly does it claim? | Atomize | §3 |
| What kind of claim, about what, built where? | Place: layer · family · component | §4 |
| What does it refine, constrain, duplicate or contradict? | Link | §5 |
| How does an agent find it later? | Retrieve | §6 |

---

## 2. Node model (summary)

```yaml
node:
  id: N-0042                 # assigned once, never recomputed (P-6)
  kind: requirement | constraint | assumption | verification | decision   # decision: P-12
  source: { file, block_hash, spans: [[start, end], ...] }   # offsets computed by code
  text: <verbatim source text of the spans>
  canonical: { subject, modality, response, trigger, state, scope, quantities }   # §3.3
  layer: L0 | L1 | L2 | L3 | L4 | L5 | C | V     # exactly one (§4.2); V for kind=verification
  family: term:<id> | (global)                    # exactly one (§4.3)
  components: [term:<id>, ...]                    # zero or more (§4.5)
  terms: [term:<id>, ...]                         # every term referenced
  annotations: [{ role: rationale | example, span }]
  draft_status: drafting | ready
  check_status: unchecked | clean | conflicted | ambiguous | stale
  flags: [inferred, pinned_family, ...]
  ambiguity: [{ kind, span }]                     # when check_status = ambiguous
  judgments: [<lock record ids>]
```

**Membership rule, stated once:** a node has **exactly one layer**, **exactly one family**, **zero or
more components**, and **any number of term references**. Being *mentioned* in another family's
terms never makes a node a member of that family. It creates a `uses_term` link, which retrieval can
follow (§6).

---

## 3. Atomize

### 3.1 What an atom is

> **P-2 · Atom tests.** An atom is one claim that can be judged true or false on its own.
>
> | Test | Question | If it fails |
> |---|---|---|
> | **T1 Single verdict** | Could one observation or test decide the whole statement? | Split along the verdicts |
> | **T2 Independent change** | Could a stakeholder plausibly change or dispute one part and keep the other? | Split |
> | **T3 Single layer** | Does the statement answer exactly one layer question (§4.2)? | Split |
> | **T4 Stands alone** | After resolving pronouns and ellipsis, does each piece still mean something? | Do **not** split |
>
> **List rule:** split on distinct **obligations**, not distinct list members. Members that share
> the same obligation under the same condition stay one node with a set-valued field.

### 3.2 Sentence roles

> **P-3 · Roles decide what a sentence becomes.**
>
> | Role | Becomes |
> |---|---|
> | requirement | Node (`kind: requirement`) |
> | constraint | Node in C (`kind: constraint`) |
> | assumption | Node (`kind: assumption`). Assumptions can be contradicted later, so they must be in the graph. |
> | verification | Node (`kind: verification`, layer V) |
> | decision | Node (`kind: decision`): chosen option, rejected options with reasons, links to the nodes it changed (P-12, §13) |
> | definition | Term registry entry, not a node |
> | rationale · example | Annotation on the node they support |
> | context · heading | Document context only |
> | open question | Flag on the section; nodes it touches become `ambiguous` |

### 3.3 Canonical form

> **P-4 · EARS-style canonical fields, derived by the agent, confirmed by the author.**
>
> ```text
> [While <state>] [When <trigger> | If <unwanted condition>] [Where <scope>]
> the <subject> MUST | MUST NOT | SHOULD | MAY <response>
> ```
>
> - Stored as fields: `subject`, `modality`, `response`, `trigger`, `state`, `scope`, `quantities`.
> - The source text stays authoritative. If source and canonical form disagree, the canonical form
>   is re-derived.
> - **Quantities are parsed and normalized by code** ("5 GB", "5GB", "5120 MB"), never by the agent.

### 3.4 Guards

> **P-5 · Deterministic guards around the atomizer.**
>
> | Guard | Code checks | Catches |
> |---|---|---|
> | **G1** Pre-segmentation | Markdown headings, list items and sentences become block boundaries before Q-ATOM | Atoms spanning unrelated sections |
> | **G2** Span anchoring | Every quote must be found verbatim in the source; offsets are computed by code | Paraphrase or hallucinated text |
> | **G3** Coverage | Every sentence with a normative word (must, shall, should, may, never, only) is covered by an atom or labelled non-normative | Dropped requirements |
> | **G4** No injection | Every term and quantity in the canonical form appears in the atom's span, directly or as a registered alias. Otherwise the node gets flag `inferred` and needs author acceptance. | Requirements the author never wrote |
> | **G5** Schema | The answer validates against the versioned schema | Malformed output |
> | **G6** Weak words | A configurable lexicon (fast, appropriate, user-friendly, as needed, etc.) suggests ambiguity | Vagueness the agent missed |

### 3.5 Ambiguity (release 1: a status, not a conversation)

`check_status: ambiguous` with one or more kinds:

- `vague_term`
- `unbounded_quantity`
- `missing_actor`
- `referential`
- `scope`
- `unresolved_term`

The node is still placed and linked.

**Open (§10):** whether ambiguous nodes take part in Q-PAIR judgment.

### 3.6 Identity

> **P-6 · Stable ids, block-level re-atomization.**
>
> 1. An id is assigned once and never recomputed from content.
> 2. When a source block's hash changes, only that block is re-atomized.
> 3. New atoms are aligned to old ones by span overlap, then by canonical-field match. Each alignment
>    is one of `unchanged`, `edited`, `split`, `merged`, `new` or `removed`.
> 4. The author confirms the alignment.
>
> **Measure:** atomizer stability, meaning agreement between two runs on the same block without the
> lock.

---

## 4. Place

### 4.1 The layer set

> **P-7 · Layers L0–L5 plus C; V is a verification layer; Terms is a separate plane. Semantics
> fixed, surface configurable.**
>
> | Layer | The claim is about… | Verified by |
> |---|---|---|
> | **L0 Intent** | Why the system exists; the outcome it serves | A business outcome, not a software test |
> | **L1 Behavior** | What an outside party observes, described without protocol artefacts | Black-box test |
> | **L2 Structure** | Which components exist, what each owns, where they run | Inspecting structure or deployment |
> | **L3 Contract** | The agreement between two named parties: path, method, status code, field, event, file format | Contract test |
> | **L4 Data** | Shape, type, identity or lifecycle of stored or transferred data | Schema or data inspection |
> | **L5 Logic** | An internal rule or algorithm of one component | White-box test |
> | **C Constraints** | A restriction over **many** nodes: budgets, invariants, policies | A check applied to every node in scope |
> | **V Verification** | A test or check of other nodes (`kind: verification`) | — (V nodes verify; they are not verified) |
>
> **Project profile (U1):** a project may rename layers for display, leave layers empty, and supply
> hints ("sections titled *Acceptance criteria* are usually L1"). Hints are stored as priors. They
> never override an answer. Layer **meanings** are not configurable, because U5 comparison and the
> §6 recipes depend on them.

### 4.2 How a node gets exactly one layer

Q-DESC asks **all seven questions** for every atom. Each answer is yes or no. A yes must come with a
supporting quote.

```text
Q1  Does it restrict MANY nodes or the whole system (every / all / never / budgets),
    rather than describe one behaviour?                                        → C
Q2  Can it only be judged by a business outcome, not by testing software?       → L0
Q3  Can an outside observer verify it WITHOUT naming a protocol artefact
    (path, method, status code, field, event name)?                              → L1
Q4  Is it about which component exists, owns or runs something?                 → L2
Q5  Is it about an agreement between two named parties (API, event, message,
    file format)?                                                                → L3
Q6  Is it about the shape, type, identity or lifecycle of data?                  → L4
Q7  Is it an internal rule or algorithm, verifiable only white-box?              → L5
(kind = verification bypasses Q1–Q7                                             → V)
```

**Mapping rule (code):**

1. **Precedence:** the layer is the one belonging to the **first yes**, in the order Q1 → Q7.
2. **Same-claim yeses are not conflicts.** A later yes whose quote **overlaps** the first yes's quote
   is the same claim seen from another angle. It is recorded and ignored for mapping.
3. **T3 violation:** a later yes whose quote does **not overlap** any earlier yes quote, pointing to a
   **different** layer, means the atom holds two claims. The atom goes back to Q-ATOM for splitting.
4. **All no:** the node becomes `ambiguous`, kind `unplaceable`, and goes to the author.

**Why this order.** Each step's reason also explains why a node is *not* in the later layers.

- **C first.** A rule over a set filed as one behaviour would hide its reach.
- **L0 before L1.** An untestable goal must not pose as a requirement.
- **L1 before L2–L5.** If the outside world can observe it, the generated code must honour it at
  the boundary, whatever the internals.
- **L3 before L4.** Data at a boundary is a contract first.
- **L4 before L5.** A data shape is not an algorithm.

Worked examples of "in this layer, not the others" are in §9.3.

### 4.3 How a node gets exactly one family

A **family is a vertical slice**: everything about one subject, across all layers.

> **P-9 · Family = the node's primary term.** The primary term is chosen by a fixed rule, applied in
> order:
>
> 1. **Subject rule:** if `canonical.subject` resolves to an **entity, data or event** term, that term
>    is the primary term.
> 2. **Response rule:** if the subject is an **actor**, a **component**, "the system" or an external
>    system, the primary term is the **first entity, data or event term in `canonical.response`**.
> 3. **Verification rule:** a V node takes the family of the node it verifies. If it verifies nodes
>    in different families, that is flagged to the author.
> 4. **Constraint rule:** a C node whose scope selects exactly one family belongs to that family.
>    Otherwise it belongs to `(global)`.
> 5. **Fallback:** if nothing resolves, the node is `ambiguous` with kind `unresolved_term`.
>
> **Actor and component terms never seed a family.** Otherwise "user" or "the service" would absorb
> half the graph. Components have their own coordinate (§4.5).
>
> **Pins:** the author may pin a node to another family. The pin is stored as flag `pinned_family`
> and shown in every view.

**Why not embeddings or text similarity?** Similarity answers "do these read alike?". A family asks
"are these about the same thing?". Similarity would group *upload size limit* with *download rate
limit*, and would separate *share-link expiry* (L1) from *the expiry timestamp field* (L4). Future
local ML models (vision O1) may **suggest** alias merges or pins. They never assign a family.

### 4.4 Term registry

```yaml
term:
  id: term:share_link
  canonical: "share link"
  aliases: ["shared link", "public link"]
  kind: entity | data | event | actor | component | external_system | category
  defined_by: <definition span or node id, optional>
```

- The agent tags terms in Q-DESC. Code resolves exact names and aliases.
- Every **new term** and every **proposed alias merge** goes through Q-TERM and then to the author.
- **Asymmetry:**
  - A wrong **merge** fabricates conflicts, which is noisy.
  - A wrong **split** hides conflicts, which is silent.
  - When unsure, the compiler proposes a merge for review rather than keeping the terms apart.
- **Release-1 simplification:** attributes such as `token` or `expires_at` are not separate terms.
  They resolve to their parent entity.
- **Category terms** (e.g. `public_endpoint`) are tags used by constraint scopes. They never seed a
  family.

### 4.5 Component coordinate

A node's components come from `allocated_to` links (§5).

- An L2 node that states ownership ("LinkService owns share links") **establishes** the allocation.
- For the other nodes in the same family, allocation is **proposed** by code from that L2 ownership
  node, and confirmed by the author.
- A node may be allocated to several components (an L1 behaviour realized by two services). It may
  also have none, until architecture is written.
- **C nodes are not allocated.** They reach components through their scope.

---

## 5. Link (partially open)

| Link | From → to | Produced by |
|---|---|---|
| `uses_term` | node → term | Q-DESC tags, resolved by code |
| `refines` | more specific node → the node it details | Q-PAIR on candidates |
| `allocated_to` | node → component term | L2 ownership (§4.5) + author |
| `constrains` | C node → scope selector (family / layer / term / category) | Scope resolved by code |
| `verifies` | V node → node it checks | Q-PAIR on candidates |
| `depends_on` | node → node it presupposes | Q-PAIR on candidates |
| `duplicates` · `subsumes` · `conflicts_with` | node ↔ node | Q-PAIR on candidates, with kind and rationale |

**Candidate generation (code).** For a new node, the candidate pairs are the nodes that:

- share its family;
- share any non-actor term;
- are covered by the same constraint scope;
- are in an adjacent layer of the same family.

The agent judges **only** these candidates, **one pair per Q-PAIR**.

> ⚠ **The main measured risk.** A pair never proposed is a relation never found. **Candidate
> completeness** (the share of true relations whose pair was proposed) must be measured on a labelled
> corpus. The Q-PAIR schema and the complete list of relation kinds are open (§10).

---

## 6. Retrieve (designed in release 1, built later for U7)

> **P-10 · The agent queries the graph and never reads it whole.** It asks through a fixed set of
> deterministic queries, and receives context packs with a manifest.

### 6.1 Indexes

All indexes are rebuilt by code from the graph:

| Index | Key → value |
|---|---|
| `by_id` | node id → node |
| `by_term` | term id, and every alias → node ids that use it |
| `by_family` | family → member node ids |
| `by_layer` | layer → node ids |
| `by_component` | component term → node ids allocated to it |
| `by_status` | status → node ids |
| `by_source` | file and line → node ids |
| `edges_out` · `edges_in` | (node, link type) → node ids |

### 6.2 Queries

```text
node(id)                         → full node (level 2)
source(id)                       → exact source span and section (level 3)
map()                            → project map (level 0)
family(term)                     → family card (level 1)
neighbors(id, type, dir, depth)  → node ids
impact(id)                       → transitive refines⁻¹ ∪ verifies⁻¹ ∪ depends_on⁻¹ + their components
context_pack(recipe, target, budget) → ordered pack + manifest
```

### 6.3 Progressive disclosure

| Level | Returns | Size bounded by |
|---|---|---|
| 0 · map | Families × layers counts; open conflicts / ambiguous / stale counts | Number of families |
| 1 · family card | Member ids and titles by layer; components; constraints in scope; related families via `uses_term` | One family |
| 2 · node | Everything in §2 for one node, plus links | One node |
| 3 · source | The verbatim span and its section heading | One passage |

Family one-line summaries (if used) are agent judgments. They are stored in the lock, keyed by the
hash of the members, and marked stale when a member changes.

### 6.4 Context recipes

A recipe is a fixed traversal. The same graph, target and budget always produce the same pack.

**Recipe `implement(component K)`:**

| Tier | Include | Resolution |
|---|---|---|
| 0 header | L2 nodes that establish K's ownership | full |
| 1 core | L1 and L5 nodes `allocated_to` K | full |
| 2 contracts | L3 nodes `allocated_to` K | full |
| 3 constraints | C nodes whose scope covers any tier 1–2 node | full |
| 4 data | L4 nodes whose family is the family of any tier 1–2 node | full |
| 5 verification | V nodes that `verify` any tier 1–2 node | full |
| 6 orientation | `refines` ancestors not already included, up to L0 | title |
| 7 boundary | Nodes in other components reached by `depends_on` from tiers 1–2 | title |

**Other recipes, with the same mechanics:**

- `change(node N)`: N, `impact(N)`, and the affected components.
- `review_conflict(A, B)`: both nodes, their sources, their refinement ancestors, and constraints
  covering either.
- `compare_family(term)` (U5): one family on both graphs, aligned (§8).

**Budget rule (code):**

1. Fill tiers in order.
2. Within a tier, order by link distance from the target, then by id.
3. When the budget is reached, remaining nodes are **cut**. Titles are tried before a node is cut
   entirely.
4. A node's text is never truncated.

**Manifest:** every node the recipe reached is listed as `included full`, `included title`, `cut` or
`flagged` (conflicted, ambiguous or stale). The manifest also lists **family members the recipe did
not reach**, so gaps caused by missing links are visible.

---

## 7. Status and invalidation (summary; detail open)

- `draft_status` describes authoring. `check_status` describes verification. They are independent.
- When a node's text changes, every judged link touching it becomes `stale`. The nodes on the
  other end of those links become `stale` for that link only.
- Family summaries are stale when any member changes.
- A button press re-checks only stale items.

---

## 8. U5 — comparing pre-built and as-built graphs

> **P-11 · Same compiler, same registry, both sides.**
>
> - Both graphs record atomizer rules, question schema versions and the layer-mapping version in
>   their header. A comparison **refuses to run** if these differ, and reports the difference
>   instead.
> - Both sides resolve against the **same term registry**. Terms new on the as-built side enter as
>   Q-TERM proposals.
> - **Matching order:**
>   1. trace link (a node id cited in code or tests), if present;
>   2. address (family, layer, component);
>   3. canonical fields;
>   4. Q-PAIR on whatever remains.

| Outcome | Meaning |
|---|---|
| `matched_equal` | Built as specified |
| `matched_diverged` | Same claim, different value or condition |
| `matched_contradicted` | Built behaviour contradicts the design |
| `prebuilt_only` | Specified, not built |
| `asbuilt_only` | Built, never specified |

**Open:** specs written from code are usually finer-grained, so a match may be one-to-many. The
candidate model is "the as-built graph refines the pre-built graph".

---

## 9. Worked example

A small spec set, compiled end to end. It is intended to become a test fixture.

### 9.1 Source — `specs/sharing.md`

```text
 1  # Sharing
 2
 3  ## Share links
 4  Owners can create a share link for a file they own.
 5  A share link expires 30 days after it is created.
 6  Visitors who open an expired share link see a "link expired" page.
 7  Share links must never reveal the owner's email address.
 8  When a file is deleted, its share links must stop working.
 9
10  ## Files
11  Owners can delete a file they own.
12
13  ## Architecture
14  LinkService owns share links. FileService owns files.
15  GET /s/{token} returns 200 with the file stream when the token is valid, and 404 when it is expired or unknown.
16  A share link record stores token, file_id, created_at and expires_at.
17  expires_at is set to created_at plus 30 days when the link is created.
18
19  ## Tests
20  Test: a link created 31 days ago returns 404.
21
22  ## Cross-cutting
23  Every public endpoint must respond within 300 ms.
```

### 9.2 Atoms

G1 splits line 14 into two sentences. On line 15, T1 finds two verdicts (200 when valid, 404
otherwise), so Q-ATOM splits it into two atoms.

| Node | Line | Canonical (abridged) | Layer | Family | Components |
|---|---|---|---|---|---|
| N-1 | 4 | When an owner requests it, the system MUST create a share link for a file the owner owns | L1 | share_link | LinkService |
| N-2 | 5 | The share link MUST expire 30 days (quantity: 30 d) after creation | L1 | share_link | LinkService |
| N-3 | 6 | When a visitor opens an expired share link, the system MUST show a "link expired" page | L1 | share_link | LinkService |
| N-4 | 7 | Share links MUST NOT reveal the owner's email address | C | share_link | — |
| N-5 | 8 | When a file is deleted, its share links MUST stop working | L1 | share_link | LinkService |
| N-6 | 11 | When an owner requests it, the system MUST delete a file the owner owns | L1 | file | FileService |
| N-7 | 14a | LinkService owns share links | L2 | share_link | LinkService |
| N-8 | 14b | FileService owns files | L2 | file | FileService |
| N-9 | 15a | When the token is valid, GET /s/{token} MUST return 200 with the file stream | L3 | share_link | LinkService |
| N-10 | 15b | When the token is expired or unknown, GET /s/{token} MUST return 404 | L3 | share_link | LinkService |
| N-11 | 16 | A share link record MUST store token, file_id, created_at, expires_at | L4 | share_link | LinkService |
| N-12 | 17 | When a link is created, expires_at MUST be set to created_at + 30 days | L5 | share_link | LinkService |
| N-13 | 20 | A link created 31 days ago returns 404 | V | share_link | — |
| N-14 | 23 | Every public endpoint MUST respond within 300 ms | C | (global) | — |

**Terms**

| Kind | Terms |
|---|---|
| entity | `share_link`, `file` |
| actor | `owner`, `visitor` |
| component | `LinkService`, `FileService` |
| category | `public_endpoint` (tagged on N-9, N-10) |

**Links**

| Link | Edges |
|---|---|
| `refines` | N-10 → N-3, N-12 → N-2 |
| `verifies` | N-13 → N-10, N-13 → N-2 |
| `depends_on` | N-5 → N-6 |
| `constrains` | N-4 → family:share_link; N-14 → layer:L3 ∩ category:public_endpoint (resolves to N-9, N-10) |

### 9.3 Locating a node — in this layer and family, not in others

#### N-2 · "A share link expires 30 days after it is created." → **L1**, not L4 or L5

| Q | Answer | Quote | Effect |
|---|---|---|---|
| Q1 C | no | — | Concerns one entity's behaviour, not a restriction over many nodes |
| Q2 L0 | no | — | Testable |
| Q3 L1 | **yes** | "expires 30 days after it is created" | **First yes → L1.** An outside observer opens the link on day 31; no protocol artefact is named |
| Q4 L2 | no | — | No component named |
| Q5 L3 | no | — | No parties or artefact named |
| Q6 L4 | yes | "expires 30 days after it is created" | Overlaps the Q3 quote: same claim seen as data lifecycle → ignored (rule 2) |
| Q7 L5 | no | — | Describes an outcome, not an internal algorithm |

**Why not L5?** N-12 (line 17) is the algorithm, and it links to N-2 by `refines`. If line 5 had said
"…expires, computed as created_at + 30 days", Q7 would say yes with the non-overlapping quote
"computed as created_at + 30 days". That triggers rule 3: a T3 violation, and a split into N-2 plus
an L5 atom.

#### N-10 · "…404 when it is expired or unknown." → **L3**, not L1

| Q | Answer | Quote | Effect |
|---|---|---|---|
| Q3 L1 | **no** | — | The claim names a protocol artefact (status code 404, path) |
| Q5 L3 | **yes** | "GET /s/{token} … 404" | **First yes → L3** |

**Why not L1?** Q3 is worded to exclude protocol artefacts. The observable effect, the "link expired"
page, already exists as N-3 in L1. N-10 details it through the contract, hence `refines`
N-10 → N-3.

#### N-4 · "Share links must never reveal the owner's email address." → **C**, not L1

| Q | Answer | Quote | Effect |
|---|---|---|---|
| Q1 C | **yes** | "must never reveal" | **First yes → C.** Restricts every response and page involving share links |
| Q3 L1 | yes | "never reveal the owner's email address" | Overlaps the Q1 quote → ignored |

**Why not L1?** Filed as one L1 behaviour, it would sit beside N-1…N-5 as a peer, and a recipe would
include it only where it happened to be linked. As C, its **scope** `family:share_link` makes every
share-link recipe include it (§9.6, tier 3).

#### N-11 · "A share link record stores token, file_id, created_at and expires_at." → **L4**, not L1 or L2

| Q | Answer | Quote | Effect |
|---|---|---|---|
| Q3 L1 | no | — | An outside observer cannot see stored fields |
| Q4 L2 | no | — | "record" is data, not a component |
| Q6 L4 | **yes** | "stores token, file_id, created_at and expires_at" | **First yes → L4** |

#### Families

| Node | Terms referenced | Subject → rule | Family | Not in |
|---|---|---|---|---|
| N-1 | owner, share_link, file | "the system" → **response rule** → first entity in response: share_link | **share_link** | `file`: file is mentioned (`uses_term`), not the subject of the obligation |
| N-5 | file, share_link | subject "share links" → **subject rule** | **share_link** | `file`: the file deletion is the *trigger*; the obligation is on share links. The dependency is kept as `depends_on` N-5 → N-6 |
| N-6 | owner, file | "the system" → response rule → file | **file** | — |
| N-7 | LinkService, share_link | subject LinkService is a component → response rule → share_link | **share_link** | `LinkService` is never a family; it becomes N-7's component coordinate |
| N-13 | share_link | kind V → **verification rule** → family of N-10 and N-2 | **share_link** | — |
| N-4 | share_link, owner | kind C → **constraint rule**; scope is exactly one family | **share_link** | — |
| N-14 | public_endpoint | kind C; scope is layer ∩ category, not one family | **(global)** | — |

### 9.4 Indexes

```yaml
by_term:
  share_link:      [N-1, N-2, N-3, N-4, N-5, N-7, N-9, N-10, N-11, N-12, N-13]
  file:            [N-1, N-5, N-6, N-8, N-9]
  owner:           [N-1, N-4, N-6]
  visitor:         [N-3]
  LinkService:     [N-7]
  FileService:     [N-8]
  public_endpoint: [N-9, N-10, N-14]
by_family:
  share_link: [N-1, N-2, N-3, N-4, N-5, N-7, N-9, N-10, N-11, N-12, N-13]
  file:       [N-6, N-8]
  (global):   [N-14]
by_layer:
  L0: []
  L1: [N-1, N-2, N-3, N-5, N-6]
  L2: [N-7, N-8]
  L3: [N-9, N-10]
  L4: [N-11]
  L5: [N-12]
  C:  [N-4, N-14]
  V:  [N-13]
by_component:
  LinkService: [N-1, N-2, N-3, N-5, N-7, N-9, N-10, N-11, N-12]
  FileService: [N-6, N-8]
edges_in:
  N-2:  { refines: [N-12], verifies: [N-13] }
  N-3:  { refines: [N-10] }
  N-6:  { depends_on: [N-5] }
  N-10: { verifies: [N-13] }
```

Two lookups show why the indexes matter:

- **Which nodes are about files?** `by_family[file]` gives **N-6, N-8**, the members.
  `by_term[file]` gives five nodes that **mention** files. The difference between the two lists is
  exactly the cross-family context (N-1, N-5, N-9).
- **What else is affected if N-2 changes?** `edges_in[N-2]` gives N-12 (refines) and N-13 (verifies).
  The graph answers this in one lookup. Grep cannot.

### 9.5 Progressive disclosure

**Level 0 — `map()`**

```text
family        L0 L1 L2 L3 L4 L5  C  V   total
share_link     0  4  1  2  1  1  1  1    11
file           0  1  1  0  0  0  0  0     2
(global)       0  0  0  0  0  0  1  0     1
open: conflicted 0 · ambiguous 0 · stale 0
```

**Level 1 — `family(share_link)`**

```text
family share_link   (components: LinkService)
L1  N-1  create share link for own file
    N-2  expires 30 days after creation
    N-3  expired link → "link expired" page
    N-5  file deleted → links stop working        depends_on → N-6 (file)
L2  N-7  LinkService owns share links
L3  N-9  GET /s/{token} → 200 + stream (valid)
    N-10 GET /s/{token} → 404 (expired/unknown)  refines → N-3
L4  N-11 record: token, file_id, created_at, expires_at
L5  N-12 expires_at = created_at + 30 d           refines → N-2
V   N-13 31-day-old link → 404                    verifies → N-10, N-2
constraints in scope: N-4 (family), N-14 (global, covers N-9, N-10)
related families via uses_term: file (N-1, N-5, N-9)
```

**Level 2 — `node(N-10)`:** the full record from §2 with the links `refines → N-3` and
`verified_by ← N-13`.

**Level 3 — `source(N-10)`:** `specs/sharing.md` line 15, section *Architecture*, verbatim span
"and 404 when it is expired or unknown", with the full sentence for context.

**Reading path for an agent asked to change link expiry:**
`map()` → sees the share_link family → `family(share_link)` → `impact(N-2)` → reads N-2, N-12, N-13
at level 2. That is four nodes, not the whole document.

### 9.6 Context recipe — `implement(component LinkService)`

| Tier | Rule | Result |
|---|---|---|
| 0 header | L2 ownership of LinkService | N-7 |
| 1 core | L1 · L5 `allocated_to` LinkService | N-1, N-2, N-3, N-5, N-12 |
| 2 contracts | L3 `allocated_to` LinkService | N-9, N-10 |
| 3 constraints | C scope covers tiers 1–2 | N-4 (family share_link), N-14 (covers N-9, N-10) |
| 4 data | L4 in families of tiers 1–2 | N-11 |
| 5 verification | V verifying tiers 1–2 | N-13 |
| 6 orientation | `refines` ancestors not yet included | — (N-3 and N-2 already in core; no L0) |
| 7 boundary | `depends_on` into other components | N-6 (FileService), title only |

**Manifest, generous budget:**

```text
recipe: implement   target: component:LinkService   graph: <hash>   budget: <B1>
included full : N-7 N-1 N-2 N-3 N-5 N-12 N-9 N-10 N-4 N-14 N-11 N-13
included title: N-6
cut           : —
flagged       : —
family members not reached: —
```

**Manifest, tight budget (illustrative):**

```text
included full : N-7 N-1 N-2 N-3 N-5 N-12 N-9 N-10 N-4 N-14
included title: N-11 N-13
cut           : N-6
```

With the tight budget, the agent **knows** it has the data shape and the test only as titles, and
that the FileService dependency was cut. It can call `node(N-11)` if it needs the fields. Nothing is
missing without a record of it.

**Not included, and why:** N-8 (FileService ownership) is not allocated to LinkService and is not
reached by any link from tiers 1–2. N-6 is reached only as a boundary.

---

## 10. Proposals and open questions

### 10.1 Proposals

| Id | Proposal | § | Status |
|---|---|---|---|
| P-0 | Prose is the source; the graph is compiled | 1.1 | approved (rel01 D12) |
| P-1 | Question kinds, check-immediately rule, judgment lock | 1.2 | approved (rel01 D12) |
| P-2 | Atom tests T1–T4 and the list rule | 3.1 | approved (rel01 D12) |
| P-3 | Sentence roles | 3.2 | approved (rel01 D12) |
| P-4 | EARS-style canonical fields; quantities normalized by code | 3.3 | approved (rel01 D12) |
| P-5 | Guards G1–G6 | 3.4 | approved (rel01 D12) |
| P-6 | Stable ids; block-level re-atomization with alignment | 3.6 | approved (rel01 D12) |
| P-7 | Layers L0–L5 + C + V; fixed meanings; project profile | 4.1 | approved (rel01 D12) |
| P-8 | Seven-question placement with precedence and overlap rules | 4.2 | approved (rel01 D12) |
| P-9 | Family = primary term by fixed rule; actors and components never seed | 4.3 | approved (rel01 D12) |
| P-10 | Indexes, queries, disclosure levels, recipes with manifest | 6 | approved (rel01 D12) |
| P-11 | U5: same versions and registry; ordered matching; five outcomes | 8 | approved (rel01 D12) |
| P-12 | Compile tiered Markdown as-is; adopt existing ids; decisions are a node kind | 13 | approved (rel01 D12) |
| P-13 | Storage: `.sdd/` with JSONL sharded by family, generated views, SQLite cache | 14 | approved (rel01 D12) |
| P-14 | Visualization: aggregate-first views V1–V7, stable layout, generated static viewer | 15 | approved (rel01 D12) |

### 10.2 Open questions

1. Q-PAIR schema and the complete list of relation kinds. How is candidate completeness measured?
2. Do `ambiguous` nodes take part in Q-PAIR?
3. ~~Where are decisions and their rejected alternatives recorded?~~ Proposed in P-12: a `decision`
   node kind. Still open: the schema of a decision node and its link types (§13.3).
4. What must the single writer confirm at each press, and what may be auto-accepted?
5. Storage layout of the graph and the lock (file per node, family or source).
6. Which Claude Code mechanism carries each question kind: hook, MCP tool, or headless call (vision §4)?
7. U5 granularity mismatch: is "as-built refines pre-built" the right model?
8. Specs that reference external standards or third-party APIs: node kind or external term?
9. Tie cases beyond L1/L3 in the questionnaire. Collect them from a real corpus before fixing.

### 10.3 Rejected

- **Keyword rules as the layer classifier.** At most, project-profile hints.
- **Layer as the only filter for candidate pairs.** Misses cross-layer conflicts.
- **Embedding similarity assigning families or links.** In later releases, suggestions only.
- **LLM-named families.** The term is the name.
- **Per-project layer meanings.**
- **Offsets supplied by the model.**

---

## 11. Future — local ML models (not release 1)

Vision O1 allows later releases to deploy local models. Where they could help, always as
**suggestions** recorded in the lock with a pinned model version:

| Task | Possible local model | Still decided by |
|---|---|---|
| Candidate generation | Embedding similarity as an extra candidate source | Q-PAIR judgment |
| Alias proposals | Embedding nearest neighbours in the term registry | Q-TERM + author |
| Layer pre-check | Small classifier predicting Q1–Q7 answers, to flag disagreements with the agent | The agent's answers |
| Weak-word detection | Classifier extending G6 | Author |

## 12. References — named from working knowledge, not verified

| Topic | Starting point |
|---|---|
| Requirement characteristics (singular, verifiable) | ISO/IEC/IEEE 29148 |
| Structured requirement templates | EARS (Mavin et al., about 2009) |
| Modal keywords | RFC 2119, RFC 8174 |
| Requirements smells / weak words | Femmer et al., about 2017 |
| Traceability | Gotel & Finkelstein, about 1994 |
| Hierarchical retrieval summaries | GraphRAG, RAPTOR (2024) |
| Candidate-pair generation | Record linkage / blocking literature |
| Overview first, zoom and filter, details on demand | Shneiderman, about 1996 |
| Graph viewer libraries | Cytoscape.js, elkjs, Sigma.js + Graphology |

---

## 13. Relation to tiered Markdown specs

Lecture: [`lecture-tiered-md-vs-graph.html`](../../../docs/lectures/lecture-tiered-md-vs-graph.html). It was measured
against `collective-investment-ai-assistant/sdd/specs/` on 2026-09-13.

### 13.1 Findings that bind this design

| Finding (measured) | Consequence |
|---|---|
| A tiered spec set already *is* a hand-maintained graph: ids = nodes, citations = untyped edges, sections ≈ layers, feature folder ≈ family, `ownership.yaml` ≈ component index | The compiler **compiles that structure**; it does not replace it |
| In the 12 specs, the median share of bytes in acceptance criteria (§6) is 17%. Decisions and open questions (§7–§8) take **30%** | Decisions must be **nodes** that recipes carry, not annotations |
| Recorded defects: an id collision (`DX-44`); 39 undeclared id families; six traceability rows naming checks that did not exist (`DX-53`); rules defined twice | Uniqueness, a declared id registry, link resolution and one-definition checks are **compiler passes**, not per-project scripts |
| Whole-file reads keep nuance and rationale; atoms risk losing them | Verbatim source stays one hop from every node (level 3). Every judged link carries its quote and rationale |

### 13.2 Proposal

> **P-12 · Compile tiered Markdown as it is.**
>
> - Files remain the authoring and reading unit. Atoms are the checking and linking unit.
> - **Existing human ids** (`AC-F9.3`, `CT-9.1`, `D2`) are adopted as node ids when present and
>   unique. A collision is a build error, not a renaming.
> - **Project profile (U1)** maps a project's conventions to the compiler's:
>   - section numbers → layer hints (for example §5 → L3/L4, §6 → L1, §9 → V)
>   - id families → node kinds
>   - path → spec map (for example `ownership.yaml`) → component allocation hints
> - **New node kind `decision`**:
>   - the chosen option;
>   - the rejected options, each with its reason;
>   - links to the nodes it changed.
>
>   Recipes include decisions linked to any included node.
> - Unresolvable citations (for example ids defined in another repository) become
>   `external_reference` terms, flagged, never silently dropped.

### 13.3 Open

1. Schema of a `decision` node, and whether "rejected option" is a node or a field.
2. How profile hints are expressed for section-numbered specs without over-fitting to one project.
3. The comparison experiment: flat Markdown, tiered Markdown, graph views only, and graph with query
   tools, all run on the same agent, on tasks with known answer sets and planted traps. Study design
   (metrics, Claude Code instrumentation, failure catalogue, statistics):
   [`lecture-tiered-md-vs-graph.html`](../../../docs/lectures/lecture-tiered-md-vs-graph.html) Parts 6–10. Nothing in this
   file claims the graph is better until that experiment has run.
4. Design features the experiment needs from the compiler: hook-friendly query logging, and graph
   views generated only from spec content, so no answers leak into them.

---

## 14. Storage

> **P-13 · Plain-text record, derived index, generated views.**
>
> ```text
> .sdd/                              # beside the specs, committed
>   graph.meta.json                  # compiler, schema and question versions; source hashes; counts
>   profile.yaml                     # project profile (U1) — the only hand-edited file here
>   terms.jsonl                      # one term per line, sorted by id
>   nodes/<family>.jsonl             # one node per line, sorted by id
>   edges/<family>.jsonl             # edges stored with the family of their source node
>   lock/<question-kind>.jsonl       # judgment lock
>   views/map.md                     # GENERATED level-0 map
>   views/families/<family>.md       # GENERATED level-1 cards
>   cache/index.sqlite               # DERIVED, git-ignored, rebuilt on demand
> ```

**Rules**

1. **JSONL is the record of truth.** Each line is one complete record. Keys are in a fixed order,
   and lines are sorted by id. The same graph always gives the same bytes.
2. **Shard by family.** An agent without tools opens one family file, and git diffs stay local to
   the feature that changed.
3. **Ids never embed family or layer.** Those can change, and an id cannot.
4. **SQLite is a cache.** It may be deleted at any time. It is never committed and never
   authoritative.
5. **Views are generated Markdown**, carry a do-not-edit header, and are regenerated on every
   compile.
6. **Order of access for agents:** (1) queries through the agent integration (vision O3),
   (2) generated views, (3) grep on JSONL by id. All three return the same facts.

**Rejected:** one large JSON file (unreadable diffs); one file per node as the record (a thousand
files, slow scans); SQLite as the record (binary in git); a graph database server (not files; too
much for release 1).

**Size:** one node line is estimated at a few hundred bytes to a couple of kilobytes, so a thousand
nodes is on the order of a megabyte. This is an estimate from the schema. Measure it on the first
real corpus.

---

## 15. Human visualization (target: ~1,000 nodes in ~30 families)

> **P-14 · Aggregate first, drill down, never a hairball.**

| View | Content | Scale on screen |
|---|---|---|
| **V1 Health matrix** | Families × layers; cell = node count, coloured by worst status | 30 × 8 cells |
| **V2 Family map** | Family bubbles (size = members); aggregated cross-family links (thickness = count) | 30 nodes |
| **V3 Family lanes** | One family; layers as fixed horizontal lanes; `refines` vertical; other families as collapsed stubs | ~30 nodes + stubs |
| **V4 Node focus** | One node, 1–2 hop neighbourhood, all link types, verbatim source panel | < 20 nodes |
| V5 Component matrix | Components × families; cell = allocated nodes | small |
| V6 Issues list | Conflicts, ambiguities, stale items; filterable; linked to V3/V4 | list |
| V7 U5 diff | V1 coloured by comparison outcome (§8) | 30 × 8 cells |

**Rules**

1. The default entry is V1 or V2. A larger drawing is always a filter result.
2. Families are compound nodes that expand and collapse.
3. **Layout is stable across compiles.** Positions are computed deterministically and cached, so
   adding one node does not reshuffle the picture.
4. Within a family, layers are a **fixed axis** (layered layout), never a force layout.
5. **Colour encodes status only:** clean, ambiguous, stale, conflicted, empty. Layer and family are
   shown by position.
6. Link types are filterable. Cross-family links stay aggregated until expanded.
7. Every visual item links to its node view and verbatim source.

**Build approach (release 1):** `sddc view` generates one self-contained static HTML page from
`.sdd/`. It opens in a browser or a VS Code webview, with no server. Candidate libraries:

- Cytoscape.js for V2–V4
- elkjs layered layout for V3
- plain SVG for the V1, V5 and V7 matrices
- Sigma.js + Graphology only if a whole-graph view is ever needed

Library choice, licences and performance at 1,000 nodes are to verify when prototyping.
