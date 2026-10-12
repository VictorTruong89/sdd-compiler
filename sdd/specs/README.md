# Specs — source of truth

> **Status:** live · opened 2026-09-14 · seven feature specs · rel01 closed 2026-10-01
> ([close-out](../design/releases/rel01_closeout.md)). This folder is authoritative once a spec is approved.

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

| Spec-ID | Feature | Status | Acceptance criteria | Tests (at the rel01 close, 2026-10-01) |
|---|---|---|---|---|
| **F1** | [Ingest: static spec files into blocks](F1_ingest/spec.md) | 🟢 approved · 🔨 built (M1) | AC-1.1 … AC-1.12, AC-1.21 … AC-1.26, AC-1.30 … AC-1.33 (22) | 22 / 22 (AC-1.26 partial) |
| **F2** | [Node & layer model](F2_node_model/spec.md) | 🟢 approved · 🔨 built | AC-2.1 … AC-2.29 (29) | 29 / 29 (AC-2.29 at unit tier) |
| **F3** | [Atomizer (Haiku + guards)](F3_atomizer/spec.md) | 🟢 approved · 🔨 built | 33 | 29 / 33 — AC-3.21, 3.22 tests unwritten; AC-3.24, 3.25 deferred (`review`) |
| **F4** | [Graph store & views](F4_graph_store/spec.md) | 🟢 approved · 🔨 built in part | AC-4.1 … AC-4.18 (18) | 13 / 18 — AC-4.9 … 4.13 deferred (`query`); 4.14, 4.17, 4.18 partial |
| **F5** | [Related-node retrieval](F5_retrieval/spec.md) | 🟢 approved · 🔨 built | AC-5.1 … AC-5.17 (17) | 16 / 17 — AC-5.15 deferred (`pairs`) |
| **F6** | [Conflict detection & report](F6_conflicts/spec.md) | 🟢 approved · 🔨 built | 27 | 27 / 27 |
| **F7** | [Agent export: map, unit packs, checklist](F7_agent_export/spec.md) | 🟢 approved 2026-09-30, amended (D3, D14) · 🔨 built (M6) | AC-7.1 … AC-7.24 (24) | 24 / 24 |
