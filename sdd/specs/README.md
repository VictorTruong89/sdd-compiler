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

## Spec index

> IDs are claimed here and **never renumbered**.

| Spec-ID | Feature | Status | Acceptance criteria | Tests exist? |
|---|---|---|---|---|
| **F1** | [Ingest: static spec files into blocks](F1_ingest/spec.md) | 🟢 approved · revised 2026-09-17 (rel01 D26) — 18 ACs, 0 open questions · ⛔ coding gated (rel01 D20) | AC-1.1 … AC-1.12, AC-1.21 … AC-1.26 | ⛔ none |
| **F2** | [Node & layer model](F2_node_model/spec.md) | 🟢 approved 2026-09-15 — 23 ACs, ⚑ reviewed 2026-09-16 (D3 reversed by rel01 D24), 2 open questions · ⛔ coding gated | AC-2.1 … AC-2.23 | ⛔ none |
| **F3** | [Atomizer (Haiku + guards)](F3_atomizer/spec.md) | 🟢 approved · revised 2026-09-17 (rel01 D26) — 24 ACs, 3 open questions · ⛔ coding gated | AC-3.1 … AC-3.22, AC-3.24, AC-3.25 | ⛔ none |
| **F5** | [Related-node retrieval](F5_retrieval/spec.md) | 🟡 draft 2026-09-17 — 16 ACs, 4 ⚑, 3 open questions · ⛔ coding gated | AC-5.1 … AC-5.16 | ⛔ none |
| **F6** | [Conflict detection & report](F6_conflicts/spec.md) | 🟡 draft 2026-09-17 — 19 ACs, 6 ⚑, 3 open questions · ⛔ coding gated | AC-6.1 … AC-6.19 | ⛔ none |
| **F7** | *Traversal for code generation* — **id reserved, design only**: [`../design/rel01_design/G3-3-traversal.md`](../design/rel01_design/G3-3-traversal.md) | — not a spec yet | — | — |
| **F4** | [Graph store & views](F4_graph_store/spec.md) | 🟢 approved 2026-09-15 — 18 ACs, ⚑ reviewed 2026-09-16 (all accepted), 2 open questions · ⛔ coding gated | AC-4.1 … AC-4.18 | ⛔ none |
