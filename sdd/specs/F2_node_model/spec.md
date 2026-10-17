# F2 — Node & layer model: nodes, layers, families, terms, links, status

> **Spec-ID:** F2 · **Status:** 🟢 approved · **Drafted:** 2026-09-15 · **Approved:** 2026-09-15 (rel01 D23)
> ⛔ **Coding gated (rel01 D20):** no implementation until G3 and G4 are reviewed and the build plan exists.
> **Source:** rel01 sub-goal G2.1 · approved proposals P-3, P-4, P-7, P-8, P-9, P-12 in
> [`../../archive/rel-01/design/rel01_design/core-working-principle.md`](../../archive/rel-01/design/rel01_design/core-working-principle.md)
> §2–§5, §13 · rel01 decisions D8 (hardcoded layers, abundant properties), D9, D14, D15, D17 (status
> and conflicts), D11 (families belong to placement).
> **Governs:** `constitution.md` §1 (id families).
> **⚑ Drafting choices:** where this spec had to fill a detail that no reviewed decision covered, the
> decision in §7 is marked ⚑. Review those first.
> **Amended:** 2026-10-16 (rel02 D26): D22, an example becomes a verification node (§4.1, AC-2.30).

---

## 1. Goal & why

**Define the one data contract every other part of the compiler reads and writes:** what a node is,
which properties it carries, how it is placed into exactly one layer and one family, how terms and
links are represented, and how status and conflicts are recorded.

Nodes carry **abundant properties** (D8) for two jobs:
- **placement** — layer and family, decided by code from recorded answers;
- **retrieval** — finding related nodes (F5) without re-reading prose.

Placement is deterministic code over answers produced by the atomizer (F3). This spec is testable
without any model call.

## 2. Scope / non-goals

**In scope:** node, term, link and conflict-record schemas · the hardcoded layer set · the placement
mapping rule · the family rule · component allocation · status derivation and precedence · id rules.

**Non-goals**
- ✗ Producing the answers placement consumes (atomization, Q-ATOM, Q-DESC) → F3.
- ✗ Where records are stored, views and queries → F4.
- ✗ Finding candidate related nodes → F5. Judging pairs and creating conflict records → F6, which in
  rel01 runs over the whole set and reports at the end (rel01 D26).
- ✗ Per-project layer meanings (P-7: meanings are fixed).

## 3. Users & triggers

| ID | Trigger | Entry point (code) |
|---|---|---|
| T1 | F3 has validated Q-DESC answers for an atom and asks for placement | `sdd_compiler.model.placement::place` |
| T2 | F3 or F6 changes a node's facts and needs its status | `sdd_compiler.model.status::derive_status` |
| T3 | Any module validates a record before writing | `sdd_compiler.model.schema::validate` |

## 4. Behaviour

### 4.1 Node kinds (P-3)

`requirement` · `constraint` · `assumption` · `verification` · `decision`.
Definitions become term-registry entries: a `definition` sentence is attached to the registered term it
opens with, as that term's `definition` and `defined_by` (F3 §4.5 step 9, F3 D38). Rationale and
examples become annotations. Neither is a node. **Amended by D22:** an example becomes a `verification`
node of the claim it illustrates (F3 D41), so it is compared with that claim like any other node; an
example in a block with no claim stays an annotation. Rationale stays an annotation.

### 4.2 Layers — hardcoded (D8, P-7)

| Layer | The claim is about |
|---|---|
| `L0` Intent | Why the system exists; the outcome it serves |
| `L1` Behavior | What an outside party observes, without naming protocol artefacts |
| `L2` Structure | Which components exist, what each owns, where they run |
| `L3` Contract | An agreement between two named parties: path, method, status code, field, event, file format |
| `L4` Data | Shape, type, identity or lifecycle of stored or transferred data |
| `L5` Logic | An internal rule or algorithm of one component |
| `C` Constraints | A restriction over many nodes: budgets, invariants, policies |
| `V` Verification | A test or check of other nodes |

The set and meanings are constants in code. The profile may supply display names and section hints.
Hints are recorded as priors and never override an answer (P-7, P-12).

### 4.3 Placement into exactly one layer (P-8)

Input: seven answers `Q1…Q7`, each `{answer: yes|no, quote: string|null}`, plus the node kind.

1. `kind = verification` → `V`. The answers are ignored.
2. Otherwise the layer is that of the **first `yes`** in order `Q1→C, Q2→L0, Q3→L1, Q4→L2, Q5→L3,
   Q6→L4, Q7→L5`.
3. A later `yes` whose quote **overlaps** (shares at least one character offset with) an earlier `yes`
   quote is recorded and does not affect the layer.
4. A later `yes` whose quote overlaps **no** earlier `yes` quote and maps to a **different** layer is a
   **T3 violation**. Placement returns `split_required` with both quotes, and no node is written.
5. All `no` → layer `null`, ambiguity kind `unplaceable`.

Quote overlap is computed on character offsets that code resolves in the source (F3 guard G2), never
on offsets supplied by the model.

### 4.4 Family — exactly one (P-9)

The primary term is chosen by the first rule that applies. ⚑ For a `V` node whose `verifies` resolved,
rule 3 is tried first (D18):

1. **Subject rule** — `canonical.subject` resolves to a term of kind `entity`, `data` or `event`.
2. **Response rule** — the subject is an `actor`, a `component`, an `external_system` or "the system";
   the first `entity`/`data`/`event` term in `canonical.response`.
3. **Verification rule** — a `V` node takes the family of the node(s) it verifies. If those differ, the
   node takes the first verified node's family and gets flag `family_disputed`.
4. **Constraint rule** — a `C` node whose scope selects exactly one family belongs to it; otherwise to
   `(global)`.
5. **Mention** (D17) — the first `entity`/`data`/`event` term the node uses in any role.
6. **Component** (D19) — the subject is a `component` term: that term.
7. **Fallback** — nothing resolves → family `null`, ambiguity kind `unresolved_term`.

**Where `scope_selector` and `verifies` come from (D13).** Both are filled by code, never written by
the model directly:
- `scope_selector` (a `C` node): `terms` = its resolved terms with role `scope`; `families` = those of
  kind `entity`, `data` or `event`; `categories` = those of kind `category`; `layers` = Q-DESC's closed
  answer `scope_layers` (any of `L0`…`L5`). An empty selector means the constraint is global.
- `verifies` (a `V` node): after every node of the run is formed, each node id or `AC-`/`CT-` label
  cited in the node's quotes or in Q-DESC's `verifies_text` resolves to the node(s) with that id or
  `label`, and each cited local label (`S4`, D20) to the nodes of the **same file** carrying it, when
  one block there carries it; each creates a `verifies` link with provenance `code`. Nothing cited → `verifies: []`, and the
  family falls to the subject rule or `unresolved_term`. The verification rule is then re-applied.

`actor` and `category` terms never seed a family, and a `component` only by rule 6. A pin overrides the rule, and the node
gets flag `pinned_family`. Mentioning a term never makes a node a member of that term's family; it
creates a `uses_term` link.

### 4.5 Components (§4.5 of the proposals)

- A node's `components` come from `allocated_to` links.
- An `L2` node stating ownership establishes the allocation for its family.
- Other nodes of that family are **proposed** for that component (flag `allocation_proposed`) until
  confirmed.
- `C` nodes are never allocated.

### 4.6 Status — derived, never set by hand (D9, D15, D17)

Values: `unchecked` · `validated` · `conflict` · `ambiguous` · `stale`. `derive_status(node)` applies
precedence **conflict > ambiguous > stale > unchecked > validated**:

| Status | Holds when |
|---|---|
| `conflict` | `conflict_ids` is non-empty |
| `ambiguous` | `ambiguity` is non-empty |
| `stale` | `stale_reasons` is non-empty |
| `unchecked` | `last_checked_run` is null |
| `validated` | none of the above |

The facts stay in their own fields. The status is recomputed whenever a fact changes, so it cannot
disagree with them.

### 4.7 Conflicts on nodes (D9, D14)

- `conflict_ids`: ids of graph-level conflict records (CT-2.4) this node belongs to.
- `related_conflict_nodes`: sorted union of all other members of those records.

The two fields are consistent by construction: `related_conflict_nodes` is computed from the records,
never written independently.

### 4.8 Ids

| Record | Form | Rule |
|---|---|---|
| Node | `N-000001`… · or an adopted human id (e.g. `AC-1.4`, `CT-1.1`) | Assigned once, never reused. A human id found in the source is adopted if unique (P-12). A duplicate human id is a build error. A contract block (F3 D39) adopts the `CT-` id of its title paragraph (D21) |
| Term | `term:<snake_case>` | Derived from the canonical name when created. Never renamed; renames become aliases |
| Conflict | `CF-000001` | Assigned once |
| Link | Key `(from, type, to)` | Unique per key |

Ids never embed family, layer or status (P-13 rule 3).

### 4.9 Deleting a node (rel01 D24)

A node is deleted when its source atom is gone: the block was removed, or re-atomization aligned it to
nothing. In one transaction:

1. delete the node record;
2. delete every link whose `from` or `to` is that node;
3. remove it from every conflict record's `members`; a record left with fewer than two members is
   `resolved` with reason `member_deleted`;
4. add a `stale_reasons` entry to every node that had a judged link to it;
5. recompute statuses, the registry and the counts.

Id counters are never rewound.

## 5. Contracts

**CT-2.1 — Node record**
```json
{
  "id": "N-000042",
  "kind": "requirement | constraint | assumption | verification | decision",
  "source": {"file": "…", "block_id": "B-000123", "heading_path": ["…"], "lines": [42, 44],
             "spans": [[12, 97]]},                       // offsets in the block's text (F3 D15)
  "text": "verbatim text of the spans",
  "canonical": {
    "state": "string | null", "trigger": "string | null", "scope": "string | null",
    "subject": "string", "modality": "MUST | MUST NOT | SHOULD | SHOULD NOT | MAY | null",
    "response": "string",
    "quantities": [{"value": 30, "unit": "day", "normalized": {"value": 2592000, "unit": "s"},
                    "quote": "30 days"}]
  },
  "terms": [{"term": "term:share_link", "role": "subject | response | trigger | state | scope",
             "quote": "share link"}],
  "label": "AC-1.8 | S1 | null",
  "primary_term": "term:share_link | null",
  "layer": "L0 | L1 | L2 | L3 | L4 | L5 | C | V | null",
  "layer_answers": {"Q1": {"answer": "no", "quote": null}, "Q3": {"answer": "yes", "quote": "…"}},
  "layer_hint": "string | null",
  "family": "term:share_link | (global) | null",
  "family_rule": "subject | response | verification | constraint | mention | component | pinned | fallback",
  "components": ["term:LinkService"],
  "scope_selector": {"families": [], "layers": [], "terms": [], "categories": []},
  "verifies": ["N-000010"],
  "decision": {"chosen": "string", "rejected": [{"option": "string", "reason": "string"}],
               "affects": ["N-000011"]},
  "annotations": [{"role": "rationale | example", "text": "…", "spans": [[0, 0]]}],
  "keywords": ["expire", "share", "link"],
  "ambiguity": [{"kind": "vague_term | unbounded_quantity | missing_actor | missing_modality | mixed_layers | referential | scope | unresolved_term | unplaceable | inferred | pending_review",
                 "quote": "string | null", "detail": "string"}],
  "conflict_ids": ["CF-000003"],
  "related_conflict_nodes": ["N-000017"],
  "stale_reasons": [{"link": ["N-000042", "refines", "N-000009"], "since_run": "R-0012"}],
  "last_checked_run": "R-0011 | null",
  "flags": ["inferred", "pinned_family", "allocation_proposed", "family_disputed"],
  "status": "unchecked | validated | conflict | ambiguous | stale",
  "judgments": ["J-000321"]
}
```
Rules:
- `scope_selector` is present only for `C` nodes, `verifies` only for `V` nodes, and `decision` only
  for `decision` nodes. Each is `null` otherwise.
- `keywords` are computed by code from `text` (lower-cased word tokens minus a fixed stop-word list,
  sorted, unique). They serve retrieval (F5) and are never model output.
- `status` always equals `derive_status` of the other fields (AC-2.14).
- `label` is the human id (`AC-<n>.<k>`, `CT-<n>.<k>`) of the block the node was formed from, on
  **every** node of that block, whether or not the id was adopted (D12). Null otherwise.
- `canonical.modality` is null only for an assumption, a decision or a verification stating no
  obligation, or together with ambiguity `missing_modality` (F3 D14).

**CT-2.2 — Term record**
```json
{ "id": "term:share_link", "canonical": "share link", "aliases": ["shared link"],
  "kind": "entity | data | event | actor | component | external_system | category | external_reference",
  "definition": "A block is a structural unit found by code … | null",
  "defined_by": "N-000005 | B-000030 | null", "status": "confirmed | proposed",
  "broader": "term:item | null" }
```
`definition` is the verbatim source slice of the sentence that defines the term, and `defined_by` the
block it came from; both are null, or both are set (F3 D38). A store whose terms predate `definition`
is refused by the schema check (F4) and must be rebuilt. ⚠ A rebuild is not free: on a copy of R18,
re-atomizing replays most answers from the lock but still needs live questions (the first one missing
was a split re-ask, F3 AC-3.12); its full cost is *to be measured*.
Attributes (for example `expires_at`) resolve to their parent entity term in rel01. `broader` names the
term this one is a kind of, as judged by Q-TERM's `narrower` verdict (D16); the terms keep separate
families.

**CT-2.3 — Link record**
```json
{ "from": "N-000042", "type": "uses_term | refines | allocated_to | constrains | verifies | depends_on | duplicates | subsumes | conflicts_with | decides",
  "to": "N-000009 | term:… | scope", "provenance": "code | judgment",
  "judgment": "J-000400 | null", "rationale": "string | null", "quotes": ["…"] }
```
`provenance: judgment` requires a non-null `judgment` and `rationale`.

**CT-2.4 — Conflict record** (D14)
```json
{ "id": "CF-000003", "kind": "contradiction | duplication | subsumption | ambiguity",
  "members": ["N-000017", "N-000042"], "rationale": "string", "quotes": {"N-000017": "…"},
  "state": "open | resolved", "resolved_reason": "fixed | member_deleted | null",
  "detected_run": "R-0011", "resolved_run": "R-0014 | null",
  "judgment": "J-000400" }
```
Rules: `members` has at least 2 entries, sorted. Every member lists this id in `conflict_ids` while the
record is `open`.

## 6. Acceptance criteria

> Test tiers are provisional names pending constitution §4.

**Placement**
- **AC-2.1** *(first yes wins)* — **Given** answers Q1 no, Q2 no, Q3 yes, Q6 yes with overlapping
  quotes, **when** placed, **then** layer is `L1`. → *unit.*
- **AC-2.2** *(T3 violation)* — **Given** Q4 yes and Q5 yes with non-overlapping quotes, **when**
  placed, **then** the result is `split_required` carrying both quotes, and no node record is
  produced. → *unit.*
- **AC-2.3** *(all no)* — **Given** seven `no` answers for a requirement, **when** placed, **then** layer
  is `null` and `ambiguity` contains `unplaceable`. → *unit.*
- **AC-2.4** *(verification bypass)* — **Given** kind `verification` with arbitrary answers, **when**
  placed, **then** layer is `V`. → *unit.*
- **AC-2.5** *(order is fixed)* — **Given** every combination of yes/no over Q1–Q7 with mutually
  overlapping quotes, **when** placed, **then** the layer always equals the first yes in Q1→Q7 order.
  → *property.*

**Family**
- **AC-2.6** *(subject rule)* — **Given** subject resolving to an `entity` term, **when** the family is
  derived, **then** family is that term and `family_rule` is `subject`. → *unit.*
- **AC-2.7** *(response rule; actors never seed)* — **Given** subject "the system" and a response whose
  first entity term is `term:file`, with actor `term:owner` also present, **then** family is
  `term:file`. → *unit.*
- **AC-2.8** *(verification rule)* — **Given** a `V` node verifying nodes in two different families,
  **then** it takes the first verified node's family and has flag `family_disputed`. → *unit.*
- **AC-2.9** *(constraint rule)* — **Given** a `C` node whose scope selects one family, **then** it
  belongs to that family; **given** a scope spanning two families or a layer, **then** `(global)`. →
  *unit.*
- **AC-2.10** *(fallback and pin)* — **Given** no resolvable term, **then** family `null` with ambiguity
  `unresolved_term`; **given** a pin, **then** the pinned family, rule `pinned`, flag `pinned_family`.
  → *unit.*
- **AC-2.11** *(mention is not membership)* — **Given** a node with family `term:share_link` whose terms
  include `term:file`, **then** a `uses_term` link to `term:file` exists and the family stays
  `term:share_link`. → *unit.*

**Status and conflicts**
- **AC-2.12** *(precedence)* — **Given** a node with non-empty `conflict_ids` and non-empty `ambiguity`,
  **then** status is `conflict`; for every combination of the four facts, status follows
  conflict > ambiguous > stale > unchecked > validated. → *property.*
- **AC-2.13** *(unchecked)* — **Given** a freshly placed node with `last_checked_run` null and no other
  facts, **then** status is `unchecked`, never `validated`. → *unit.*
- **AC-2.14** *(status consistent)* — **Given** any node record, **when** validated against CT-2.1,
  **then** a stored `status` different from `derive_status` is rejected. → *contract.*
- **AC-2.15** *(conflict membership consistent)* — **Given** open conflict records, **when**
  `related_conflict_nodes` is computed for a member, **then** it equals the sorted union of the other
  members of all its open records; a node in two records lists both `conflict_ids` (D14). → *property.*
- **AC-2.23** *(deletion cascades)* — **Given** node A in an open conflict with B and linked to C,
  **when** A is deleted, **then** A's record and all links touching it are gone, the record is
  `resolved` with reason `member_deleted`, B is no longer `conflict`, and C has a `stale_reasons`
  entry. → *integration.*
- **AC-2.16** *(resolution clears)* — **Given** a node whose only open conflict record becomes
  `resolved`, **when** facts are recomputed, **then** `conflict_ids` and `related_conflict_nodes` are
  empty and status is no longer `conflict`. → *unit.*

- **AC-2.24** *(scope selector derived; D13)* — **Given** a `C` node whose scope-role terms are
  `term:upload` (entity) and `term:api` (category) and whose `scope_layers` is `[L3]`, **then**
  `scope_selector` is `{families: [term:upload], layers: [L3], terms: [term:api, term:upload],
  categories: [term:api]}` and its family is `term:upload` by the constraint rule. → *unit.*
- **AC-2.25** *(verifies resolved by citation; D13)* — **Given** a `V` node whose quote cites `AC-1.4`
  and two nodes labelled `AC-1.4` in family `term:table`, **then** `verifies` lists both, two
  `verifies` links with provenance `code` exist, and the family is `term:table` by the verification
  rule; **given** a `V` node citing nothing, **then** `verifies` is `[]`. → *unit.*

- **AC-2.26** *(a criterion joins what it tests; D18)* — **Given** a `V` node whose subject term is the
  entity `term:node` and whose `verifies` resolves to a node in `term:candidate`, **then** its family is
  `term:candidate` by rule `verification`; **given** nothing resolved, **then** `term:node` by
  `subject`. → *unit.*
- **AC-2.27** *(component as last resort; D19)* — **Given** a subject tagged `component`
  (`term:exhaustive_mode`) and no entity, data or event term anywhere, **then** the family is
  `term:exhaustive_mode`, rule `component`; **given** an entity in the response, **then** the response
  rule applies as before. → *unit.*
- **AC-2.28** *(local labels; D20)* — **Given** a table row `| **S4 adjacent layer** | … |` in
  `f5.md`, a row labelled `S4` in `f9.md`, and a criterion in `f5.md` citing "S4", **then** the row's
  node carries `label: "S4"`, the criterion verifies only the `f5.md` node and joins its family; a local
  label carried by two blocks of one file resolves to nothing. → *unit.*

**Records and ids**
- **AC-2.17** *(schema validation)* — **Given** records missing required fields, with unknown enum
  values, or with a `judgment`-provenance link lacking a judgment id, **when** validated, **then** each
  is rejected naming the field. → *contract.*
- **AC-2.18** *(kind-specific fields)* — **Given** a `requirement` with a non-null `scope_selector` or
  `decision`, **then** it is rejected; **given** a `decision` without `chosen`, **then** it is rejected.
  → *contract.*
- **AC-2.19** *(human id adoption)* — **Given** an atom whose source carries a unique human id
  `AC-1.4`, **then** the node id is `AC-1.4`; **given** two sources carrying `AC-1.4`, **then** the
  build fails naming both locations. → *unit.*
- **AC-2.29** *(a contract takes its title's id; D21)* — **Given** a title paragraph
  `**CT-1.1 — Block record** (one JSON object per line):` that forms one node, followed by a fenced
  `json` block, **when** compiled, **then** the contract node's id is `CT-1.1`, the title's node has an
  `N-` id and `label: "CT-1.1"`, and the build does not fail on a duplicate id. → *integration.*
- **AC-2.20** *(deleted ids never reused)* — **Given** node `N-000007` is deleted, **when** later nodes
  are created, **then** the id counter continues past the highest id ever issued and `N-000007` is never
  issued again. → *property.*
- **AC-2.21** *(keywords deterministic)* — **Given** the same text, **then** `keywords` are identical
  across runs and contain no stop words. → *unit.*
- **AC-2.22** *(layers are constants)* — **Given** a profile that tries to add or redefine a layer,
  **then** loading fails; display names and hints load. → *unit.*

## 7. Decisions

- **AC-2.30** *(an example is a verification node; D22)* — **Given** a block whose claim "the default
  metavar is the type name in uppercase" is followed by the example "an integer option `--count`
  appears as `--count COUNT`", **when** it is formed, **then** the example is a node of kind
  `verification`, layer `V`, whose `verifies` holds the claim's id and whose family is the claim's
  (D18); **given** a block whose only sentences are an example and context, **then** the example is an
  annotation and no node is formed. → *unit.*
- **D1 — Status is derived from facts, never stored independently** (implements D9/D15/D17).
  *Rejected:* setting status directly — status and facts would drift apart.
- **D2 — ⚑ One `status` field replaces the proposals' `draft_status` × `check_status`.** rel01 has a
  single writer and no drafting workflow. *Rejected for rel01:* two status axes.
- **D3 — Removed nodes are deleted, not kept** (owner decision, rel01 D24). When a node's source text
  is gone, its record, its links and its membership in conflict records are deleted in the same
  transaction. *Why deletion is safe:* `.sdd/` is committed to git, so history lives in git rather than
  in a graveyard of `removed` records, and every query, count and view stops having to filter them out.
  *What deletion costs, and how it is covered:*
  - **Id reuse.** Ids must still never be reused, so `graph.meta.json` keeps monotonic **id counters**
    (F4 CT-4.1). A deleted id is never issued again (AC-2.20).
  - **Dangling references.** Deleting a node deletes every link touching it, drops it from every
    conflict record, and closes a record that falls below two members (§4.9).
  - **Neighbours.** Every node that had a judged link to the deleted node gains a `stale_reasons` entry,
    so it is re-checked rather than silently keeping a verdict about something gone.
  - ⚠ **Asymmetry with F1:** F1 keeps *blocks* with `removed_run` set (F1 D13), because block identity drives
    change detection across runs. Only *nodes* are deleted. Say so if this should change too.
- **D4 — ⚑ `keywords` computed by code** as a cheap retrieval signal for F5. *Rejected:* model-generated
  keywords — non-deterministic and unverifiable.
- **D5 — ⚑ Conflict kinds** `contradiction · duplication · subsumption · ambiguity` (from the pre-rel01
  design). Orphans are structural checks in F4, not conflicts.
- **D6 — ⚑ A `V` node verifying nodes in several families** takes the first verified node's family and
  is flagged. *Rejected:* failing placement — tests often span families.
- **D7 — ⚑ New link type `decides`** from a decision node to the nodes it changed (P-12 "links to the
  nodes it changed").
- **D8 — ⚑ Modality set** adds `SHOULD NOT` to the proposals' list.
- **D9 — ⚑ The family rules apply literally in order** (found while building T9). §4.4 says "the first
  rule that applies", so a `C` or `V` node whose subject is an entity takes that entity's family by the
  subject rule before the constraint or verification rule is reached. *Why:* it is what the text says,
  and it keeps "uploaded files must never exceed 5 GB" in the `file` family, where a reader looks for it.
- **D10 — ⚑ Which human ids are adopted** (found while building T9). Only `AC-<n>.<k>` and `CT-<n>.<k>`,
  which are unique across the repository by construction; only as the **label** at the start of a
  paragraph or list item (a mention or a table row is not the claim); and only when the block forms
  exactly one node. *Why:* `D<n>`, `Q<n>` and `T<n>` are unique only inside one spec (constitution §1),
  so adopting them would fail every multi-spec build on the duplicate rule. See Q4 for the multi-atom
  case.
- **D12 — Every node formed from a labelled block carries the label** (closes Q4, option c). A block
  that forms exactly one node still adopts its human id (AC-2.19); a block that forms several gives
  them `N-` ids, and all of them carry `label: "AC-1.8"`. *Why:* in two live runs, 13–14 of 18 F1
  acceptance criteria formed several nodes, so without the field the id survived only inside the
  text. *Rejected:* (a) text only — "which nodes came from AC-1.8" would need a text search; (b)
  suffixed ids (`AC-1.8.1`) — a new id form and a constitution change for what a field does.
- **D21 — ⚑ A contract block takes its title's `CT-` id** (I-92 a, owner 2026-09-27). A fenced
  contract block (F3 D39) has no id of its own: the id is in the paragraph directly before it —
  `**CT-1.1 — Block record** (…)`. The block adopts that id, so the node is `CT-1.1`, and it is the
  id's one carrier for the duplicate rule. The title paragraph's own nodes, if it forms any, carry
  `label: "CT-1.1"` with `N-` ids. *Why:* the contract *is* what `CT-1.1` names, and a criterion that
  cites `CT-1.4` then resolves `verifies` to it (D13). On R18 the 22 titled contract blocks each sit
  directly after their title, and none of the 23 `CT-` titles formed a node. *Rejected:* `N-` ids with
  the title as `label` only — "show me CT-2.1" would need a label lookup for the one id family made to
  be adopted.
- **D13 — Code fills `scope_selector` and `verifies` from answers already given** (closes Q3, option b;
  §4.4). *Why:* both fields feed placement (family rules 3, 4) and retrieval (F5 S3), and nothing
  produced them; the atomizer already tags scope terms, and the `label` field (D12) makes a cited
  criterion resolvable by lookup. One closed Q-DESC field (`scope_layers`) is the only new model output.
  *Rejected for rel01:* (a) leaving them empty — S3 and rule 4 would be dead code in production.
  *Deferred past rel01 (rel01 D31):* (c) `verifies` and `constrains` as Q-PAIR relations, which would
  find targets that are described but not named, at the cost of model calls and an ordering loop
  (family → retrieval → judgment → family).
- **D14 — ⚑ A conflict record resolved by a deletion keeps its members** (found while building T11).
  §4.9 step 3 says to remove the deleted node from `members`, but CT-2.4 requires at least two. A record
  falling below two is resolved (`member_deleted`) and keeps its member list as history; an **open**
  record never lists a deleted node, and the store checks only open records' members.
- **D15 — Ambiguity kind `mixed_layers`** (F3 D23): a node whose layer answers still point at two
  layers after the split re-ask is placed by the first yes and carries this ambiguity, quoting the
  second yes.
- **D16 — A term may record the term it is a kind of (`broader`)** (rel01 D33 R1, F3 D25). "Review
  item" is narrower than "item": both stay terms with their own families, and the relation is kept for
  later views rather than lost in a merge.
- **D17 — A mentioned entity names the family before null** (rel01 D32 R4). Rule 5 takes the first
  `entity`/`data`/`event` term the node uses in any role. *Why:* 20 of 84 gate nodes had no family,
  10 of them because no subject term was tagged. *Narrows* the principle "mentioning a term never makes
  a node a member" to: never while any earlier rule applies. AC-2.11 still holds.
- **D18 — ⚑ A verification that resolved `verifies` takes that family first** (M3 gate review, I-56;
  owner approved the direction 2026-09-19). *Amends D9 for `V` nodes.* On R12, nine of F5's criteria
  sat in `term:node` because "Given two nodes…" gave the subject; the Given clause names a criterion's
  fixture, not what it tests. D9's reason (a `C` node about files stays in `file`) does not transfer,
  because a criterion's subject is its setup.
- **D19 — ⚑ A `component` subject names the family as a last resort**, after mention and before null
  (M3 gate review, I-56). "Exhaustive mode" had about five claims and no family, because components never
  seeded one. Placed last, it takes only nodes that would otherwise be null. Actors and categories
  still never seed a family.
- **D22 — ⚑ An example is a verification node of the claim it illustrates** (rel02 round 14,
  2026-10-16; amends §4.1). As an annotation an example was never compared with anything, so an example
  that contradicts its own rule could not be found: planted in case006 (round 14, P7, `--count COUNT`
  against "the type name in uppercase") and missed. (`lend`'s P10 is a worked example written as a
  table in its own block; its rows are claims already, F3 D34, so its miss has another cause.) An
  example states an observable outcome in one case, which is what a check of the claim states, so it
  becomes a `V` node verifying that claim, and F5's same-block and same-family sources pair them.
  *Rejected:* keeping examples as annotations and judging them in F6 (a conflict's members are nodes;
  F6 and F7 would need a second member shape); making examples requirements (an example does not add an
  obligation, it instances one).
- **D20 — ⚑ Local labels** (M3 gate review, I-56). A table row that opens with an id (`S1`, `T1`, bold
  or not), or a list item that opens with a bold one (`**D1 — …**`), gives its nodes that `label`. A
  local label is **never adopted** as a node id and never fails a build as a duplicate (D10 still
  holds). It resolves only inside its file, and only when one block there carries it. *Why:* F5's
  criteria cite "S1" … "S7", ids unique only inside F5. *Rejected:* adopting them as ids, which fails
  every multi-spec build (D10).
- **D11 — Ambiguity kind `missing_modality`** (F3 D14): a requirement or constraint that states no modal
  verb is formed with `modality: null` and this ambiguity.

## 8. Open questions

- **Q1 — Decision nodes: is a rejected option a field (as here) or its own node?** Proposals §13.3.
  Field chosen for rel01; revisit if rejected options need their own links.
*Q2 closed 2026-09-18 by F5 D8: one fixed, versioned stop-word list in code (`keywords.py`, `en-1`). Q4
closed 2026-09-18 as D12. Q3 closed 2026-09-18 as D13.*

## 9. Traceability

| AC | Test (file::test) | Code |
|---|---|---|
| AC-2.1 … AC-2.5 | `tests/test_model_placement.py` (133) | `src/sdd_compiler/model/placement.py` · `layers.py` |
| AC-2.6 … AC-2.11 · D9 · AC-2.26, AC-2.27 · D18, D19 | `tests/test_model_family.py` (14) | `src/sdd_compiler/model/family.py` |
| AC-2.12 … AC-2.16 | `tests/test_model_status.py` (20) | `src/sdd_compiler/model/status.py` |
| AC-2.14, AC-2.17 … AC-2.21 · D10 … D12 | `tests/test_model_records.py` (29) | `src/sdd_compiler/model/schema.py` · `ids.py` · `keywords.py` |
| AC-2.22 | `tests/test_profile.py` (3) | `src/sdd_compiler/profile.py` · `model/layers.py` |
| AC-2.24, AC-2.25 · D13 | `tests/test_atomize_pipeline.py` | `src/sdd_compiler/atomize/forming.py` · `pipeline.py` |
| AC-2.28 · D20 | `tests/test_model_records.py::test_f2_d20_…` (8 cases) · `tests/test_atomize_pipeline.py::test_f2_d20_…` (3) | `src/sdd_compiler/model/ids.py` · `schema.py` · `atomize/forming.py` · `pipeline.py` |
| AC-2.23 · D14 | `tests/test_store_graph.py::test_f2_ac_2_23_deleting_a_node_cascades` | `src/sdd_compiler/store/graph.py` |
| AC-2.29 *(tier gap: specified integration, tested at unit level — added at the rel01 close)* | `tests/test_atomize_contracts.py::test_ac_2_29_the_contract_carries_the_id_and_the_title_only_the_label` | `src/sdd_compiler/atomize/contracts.py` |
| AC-2.30 · D22 | `tests/test_atomize_pipeline.py::test_ac_3_40_ac_2_30_*`, `::test_ac_2_30_an_example_in_a_block_with_no_claim_forms_no_node` | `src/sdd_compiler/atomize/forming.py::example_pieces` · `pipeline.py` |
