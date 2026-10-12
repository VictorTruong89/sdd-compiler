# G2 — Atomize with Claude (Haiku); node model, layers, graph architecture

> **Status:** APPROVED (rel01 D23) — graduated to [`../../specs/F2_node_model/spec.md`](../../specs/F2_node_model/spec.md), [`../../specs/F3_atomizer/spec.md`](../../specs/F3_atomizer/spec.md), [`../../specs/F4_graph_store/spec.md`](../../specs/F4_graph_store/spec.md); the specs win · **Tier:** design, non-authoritative
> **Split confirmed** (rel01 D11): G2.1 first → G2.2 and G2.3 in parallel. Pre-rel01 proposals
> approved (D12). **Scoped by rel01 D26 (2026-09-17):** one batch run — atomize every pending block,
> then check, then report. No hook trigger, no actor distinction, no stopping mid-run.
> **Depends on:** G1 pending-block output ([`G1-ingest.md`](G1-ingest.md) §7)

---

## G2.1 — Node & layer model (future F2)

**Decided requirements**
- Layers are **hardcoded** (rel01 D8).
- Nodes carry **abundant properties** to support (a) placement into a layer and a family and
  (b) retrieval of related nodes (rel01 D8).
- Status enum: `unchecked` · `validated` · `conflict` · `ambiguous` · `stale` (rel01 D9, D15).
- Conflict fields on the node: `conflict_ids` (references to graph-level conflict records) and a flat
  list of related node ids sharing a conflict (rel01 D9, D14).
- Family grouping is part of placement (rel01 D11).

**To design:** the property list and what each property enables · layer set · placement rule · family
rule · status precedence (rel01 D17: `conflict` > `ambiguous` > `stale` > `unchecked` > `validated`).
**Inputs:** pre-rel01 P-3, P-4, P-7, P-8, P-9, P-12 (`../../questions.md` QR-2).

## G2.2 — Atomizer (future F3)

**Decided requirements**
- **Haiku** atomizes specs and forms nodes (rel01 D8).
- Model calls use one interface with two backends: headless Claude Code (default) and the Anthropic
  API (optional) (rel01 D7).
- Runs as one phase over all pending blocks; the run never stops at a conflict (rel01 D26).
- Hazards that still apply: version-dependent `claude` flags, and an API key leaking into the child
  environment of a headless call. (Hook recursion was a third hazard; with no hooks in rel01 the child
  marker stays only as a guard for any nested `claude` call.)

**To design:** question schemas · batching · check-immediately and re-ask rule · guards · judgment
lock · usage and cost logging · the attention list of items a person must decide, reported at the end
of the run.
**Inputs:** pre-rel01 P-1, P-2, P-5, P-6.

## G2.3 — Graph architecture & views (future F4)

**Decided requirements**
- **Two forms of the same graph** (rel01 D10):
  - **collapsed** for humans — aggregated by family and layer, drill down on demand;
  - **full detail** for AI agents — complete node records and links.
- A **graph-level registry of all conflicted nodes**, so the end-of-run report and any agent find them
  in one read (rel01 D9, D26).
- **Conflict records** at graph level: `{conflict_id, kind, members, rationale, …}` (rel01 D14).

**To design** (when the spec is refined — not yet):
- one record of truth with both forms derived from it, so they cannot drift apart;
- storage layout, indexes, and how the conflict registry stays consistent with node statuses;
- what the collapsed form shows at each zoom level, and what the full form returns to an agent.

**Inputs:** pre-rel01 P-10, P-13, P-14; lecture `tiered-md-vs-graph` Parts 4–5.
