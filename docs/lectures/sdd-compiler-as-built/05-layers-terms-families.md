# 5. Layers, terms and families — how a node is classified

Every node gets **exactly one layer** (what *kind of statement* it is) and **exactly one family** (what
*thing* it is about). Think of a library: the layer is the shelf type (history, cookery, law), the
family is the subject index card (steak, sauces, desserts). A book lives on one shelf and under one
subject heading, but it may *mention* many subjects.

## Layers: eight fixed shelves

The set and meaning of the layers are constants in code (`model/layers.py`); a profile may only rename
them for display.

| Layer | Name | It is… | Restaurant example |
|---|---|---|---|
| **L0** | Intent | Why the system exists; judged only by a business outcome | "Guests come back within a month" |
| **L1** | Behaviour | What an outsider can check by using the product, without naming internal artefacts | "A steak arrives within 20 minutes of ordering" |
| **L2** | Structure | Which component exists, owns or runs something | "The grill station cooks all meat" |
| **L3** | Contract | An agreement between two named parties (API, event, file format) | "Order tickets list table, dish, doneness" |
| **L4** | Data | Shape, type, identity or lifecycle of data | "Each order has a unique ticket number" |
| **L5** | Logic | An internal rule or algorithm, checkable only white-box | "Rest the steak 5 minutes before slicing" |
| **C** | Constraint | A restriction over many parts at once: budget, invariant, policy | "No nuts in any dish" |
| **V** | Verification | A test or check of other claims | "Taste-test: a medium steak is pink at the centre" |

**R18 distribution** (950 nodes): L4 201 · V 191 · C 168 · L1 137 · L5 122 · L2 79 · L3 16 · L0 3 ·
no layer 33. A spec *about a compiler* is heavy on data and verification, light on intent — expect a
different shape on a product spec.

### How the layer is chosen

The model answers seven yes/no questions, each *yes* with a quote (`atomize/describe.py`):

| Q | Asks | A *yes* means |
|---|---|---|
| Q1 | Does it restrict many parts at once — a budget, invariant, cross-feature policy? | **C** |
| Q2 | Can it only be judged by a business outcome? | **L0** |
| Q3 | Can an outsider check it just by using the system, without naming a path, field, status code…? | **L1** |
| Q4 | Is it about which component exists, owns or runs something? | **L2** |
| Q5 | Is it about an agreement between two named parties? | **L3** |
| Q6 | Is it about the shape, type, identity or lifecycle of data? | **L4** |
| Q7 | Is it an internal rule or algorithm, verifiable only white-box? | **L5** |

Then **code** decides (`model/placement.py`), in this order:

1. A `verification` atom goes to **V**, whatever it answered.
2. Otherwise the **first yes** in Q1 → Q7 order wins.
3. A later *yes* whose quote **overlaps** an earlier yes quote is the same words seen from another
   angle: recorded, ignored.
4. A later *yes* on **different words** means the atom holds two claims on two layers: it must be split
   (re-asked once). Table rows and `AC-` blocks are exempt — placed by the first yes, flagged
   `mixed_layers`.
5. Seven *no*s: no layer, ambiguity `unplaceable`.

*Why the model answers questions instead of naming a layer:* "is this L1 or L5?" is a judgment people
disagree on; "can an outsider check this by using the product?" is a question with a quotable answer.
The questions are answered; the mapping is fixed.

*Note:* `kind` and `layer` are different axes. `N-000008` in chapter 4 is a **constraint** by kind
(it says *must not*) but placed in **L5** (Q7 was its first yes). Kind is what the sentence does;
layer is what it is about.

## Terms: the vocabulary

A **term** is a named thing the specs talk about — `share link`, `block`, `profile`. The registry
(`.sdd/terms.jsonl`) holds one record per term:

```json
{"id": "term:agent", "canonical": "agent", "aliases": ["ai agent"], "kind": "actor",
 "defined_by": null, "status": "proposed", "broader": null}
```

- `aliases` come from Q-TERM `same` verdicts (chapter 3);
- `broader` from `narrower` verdicts — a **kind-of** hierarchy (`review item` → `item`);
- `kind` is `entity`, `data`, `event`, `actor`, `component`, `external_system`, `category` or
  `external_reference`.

Each node links to every term it uses with a `uses_term` link — **mentioning a term never makes a node
a member of that term's family**. Membership is decided by the family rule below.

**R18:** 1 031 terms for 950 nodes; 452 have a `broader`, 53 have aliases. More terms than nodes is
the known weakness called *term proliferation*: the atomizer tends to coin a new name per phrasing
(build-plan I-65, I-76). It is the single biggest quality lever left.

## Families: one subject heading per node

A family **is a term**: `term:share_link` is both the term and the family of the claims whose main
subject is a share link. The rule (`model/family.py`) tries these in order, and the first that applies
wins:

| # | Rule | Applies when | Example |
|---|---|---|---|
| — | **pin** | A person pinned the family | — |
| 3′ | **verification first** | A `V` node whose `verifies` resolved | A test of `AC-1.4` joins AC-1.4's family — not the family of its "Given two nodes…" fixture |
| 1 | **subject** | The subject term is an entity, data or event | "A **share link** must expire…" → `share_link` |
| 2 | **response** | The subject is an actor, component, external system or "the system" | "**The system** must delete the **archive**" → `archive` |
| 4 | **constraint** | A `C` node | Scoped to exactly one family → that family; otherwise **`(global)`** |
| 5 | **mention** | Any entity/data/event term it uses | `N-000008` "F1 makes no **model calls**" → `model_call` |
| 6 | **component** | The subject is a component | "The **atomizer** re-asks…" → `atomizer` |
| 7 | **fallback** | Nothing above | family `null`, ambiguity `unresolved_term` |

Actors and categories never seed a family — otherwise "user" or "the service" would swallow half the
graph.

**R18:** rules used — subject 534 · mention 146 · response 88 · constraint 58 · verification 48 ·
component 48 · fallback 28. There are **375 families**. The largest are `node` (76 nodes),
`(global)` (51), `block` (46), `pair_key` (21) — natural for specs about a graph compiler — and 28
nodes have no family.

## Constraints and their scope

A `C` node restricts *other* nodes. Its `scope_selector` is built by code from the terms Q-DESC tagged
with role `scope` and the layers it named:

```json
{"families": ["term:confidence"], "layers": ["L5"], "terms": ["term:confidence"], "categories": []}
```

A constraint **covers** a node (`model/scope.py`) when the node is in a named family or uses a named
term — narrowed by the layers, if any. A selector with *layers only* covers a node only if they also
share a term or keyword; without that bar, three layer-wide constraints paired with most of the graph
(F5 D9). Coverage is how a family card lists "in scope from elsewhere" and how retrieval source S3
proposes a constraint against the nodes it governs.

## Why these rules matter to you

- **Families are the backbone of retrieval.** Two claims in the same family are paired first (S1,
  chapter 6). If the atomizer names one thing two ways, the two claims land in two families and the
  conflict between them may never be judged — this was measured: 5 of 6 planted conflicts were missed
  for exactly that reason (M4 gate).
- **Layers make impact readable.** A change to an L4 data rule touches the L1 behaviours in the same
  family; the map (chapter 8) shows families × layers at a glance.
