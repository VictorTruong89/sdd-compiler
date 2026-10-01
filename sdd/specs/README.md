# Specs — source of truth

> **Status:** live · opened 2026-09-14 · six specs written. This folder is authoritative once a spec is
> approved; rel01 D20 gates implementation separately.

## What lives where

| Path | Role |
|---|---|
| [`vision.md`](vision.md) | **What** is built and **why** |
| [`constitution.md`](constitution.md) | **How** to build: principles, invariants, test tiers, change process |
| `F<n>_<slug>/spec.md` | One feature = one spec |
| [`ownership.yaml`](ownership.yaml) | Spec → code globs |
| [`_templates/spec.md`](_templates/spec.md) | Skeleton for a new spec |

Status legend: 🔵 idea · 🟡 draft (has ACs) · 🟢 approved (coding may start, unless a release gate says otherwise — rel01 D20 gates all rel01 coding).

## rel01 command scope (build-plan B2, rel01 D29)

**Shipping:** `sddc init · compile · status · conflicts · family`, plus `export` (rel01 D34, F7).
**Specified but deferred out of rel01:** `ingest` (as its own command), `atomize`, `blocks`, `show`,
`review`, `map`, `query`, `check` (the standalone command — the check *phase* runs inside `compile`),
`pairs`, `check-conflicts`, and F5's exhaustive mode. Their
acceptance criteria stay in the specs, unbuilt; the release close-out lists them as deferred.

## Spec index

> IDs are claimed here and **never renumbered**.

| Spec-ID | Feature | Status | Acceptance criteria | Tests exist? |
|---|---|---|---|---|
| **F1** | [Ingest: static spec files into blocks](F1_ingest/spec.md) | 🟢 approved · revised 2026-09-18 (D13) — 20 ACs, 0 open questions · 🔨 built (M1) | AC-1.1 … AC-1.12, AC-1.21 … AC-1.26, AC-1.30, AC-1.31 | ⛔ none |
| **F2** | [Node & layer model](F2_node_model/spec.md) | 🟢 approved 2026-09-15 — 23 ACs, ⚑ reviewed 2026-09-16 (D3 reversed by rel01 D24), 2 open questions · ⛔ coding gated | AC-2.1 … AC-2.23 | ⛔ none |
| **F3** | [Atomizer (Haiku + guards)](F3_atomizer/spec.md) | 🟢 approved · revised 2026-09-17 (rel01 D26) — 24 ACs, 3 open questions · ⛔ coding gated | AC-3.1 … AC-3.22, AC-3.24, AC-3.25 | ⛔ none |
| **F5** | [Related-node retrieval](F5_retrieval/spec.md) | 🟢 approved 2026-09-18 — 16 ACs, 0 open questions · ⛔ coding gated | AC-5.1 … AC-5.16 | ⛔ none |
| **F6** | [Conflict detection & report](F6_conflicts/spec.md) | 🟢 approved 2026-09-18 — 19 ACs, 0 open questions · ⛔ coding gated | AC-6.1 … AC-6.19 | ⛔ none |
| **F7** | [Agent export: map, unit packs, checklist](F7_agent_export/spec.md) (rel01 D34; G3-3 budgeted traversal deferred) | 🟢 approved 2026-09-30, amended (D3, D14) — 24 ACs, built | AC-7.1 … AC-7.24 | ⛔ none |
| **F4** | [Graph store & views](F4_graph_store/spec.md) | 🟢 approved 2026-09-15 — 18 ACs, ⚑ reviewed 2026-09-16 (all accepted), 2 open questions · ⛔ coding gated | AC-4.1 … AC-4.18 | ⛔ none |
