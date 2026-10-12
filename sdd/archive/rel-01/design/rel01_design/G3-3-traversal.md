# G3.3 — Traversal for code generation (design only)

> **Status:** DESIGN ONLY (rel01) · **Tier:** design, non-authoritative · **Drafted:** 2026-09-17
> **Spec id reserved:** `F7`. It becomes a spec when rel01 D20's build plan decides to build it, and
> not before: this is the one sub-goal the owner scoped as "design now, build if time allows".
> **Depends on:** F2 (node records) · F4 (queries, indexes) · F5 (candidates) · F6 (conflict records).
> **Source:** approved proposal P-10 §6 of
> [`core-working-principle.md`](core-working-principle.md) · rel01 D10 (two forms) · D26 (batch).

---

## 1. What it is for

An AI agent about to write code needs **the few specs that govern the change**, not a folder. Traversal
turns a target — a component, a node, a family — into an ordered **context pack** with a **manifest**
saying what was included, what was cut, and what was flagged.

This is purpose 2 of the vision, and it is what the rel01 G4 study would measure. rel01 builds the
graph that makes it possible; whether the pack itself is built is a build-plan decision.

## 2. The recipe idea

A recipe is a fixed traversal, so the same graph, target and budget always produce the same pack.

**`implement(component K)`** — tiers, in order:

| Tier | Include | Resolution |
|---|---|---|
| 0 header | `L2` nodes establishing K's ownership | full |
| 1 core | `L1` and `L5` nodes allocated to K | full |
| 2 contracts | `L3` nodes allocated to K | full |
| 3 constraints | `C` nodes whose scope covers any tier 1–2 node | full |
| 4 data | `L4` nodes in the families of tiers 1–2 | full |
| 5 verification | `V` nodes verifying tiers 1–2 | full |
| 6 orientation | `refines` ancestors up to `L0` | title |
| 7 boundary | Nodes in other components reached by `depends_on` | title |

Other recipes, same mechanics: `change(node N)` (N plus its impact), `review_conflict(A, B)` (both
nodes, their sources, their ancestors, the constraints covering either).

## 3. The four issues to settle before it becomes a spec

1. **Thin graphs.** The recipe leans on `allocated_to`, which needs `L2` ownership nodes. Many spec sets
   have few. *Proposed fallback:* when a component has no allocation, fall back to family plus shared
   keywords, and **say so in the manifest** — a pack assembled loosely must not look authoritative.
2. **Budget unit.** Token counts for a third-party model cannot be computed locally. *Proposed:* budget
   in **characters**, state the unit, and never convert with an invented ratio.
3. **Both forms (D10).** The pack is for an agent, but a person needs to see what the agent saw.
   *Proposed:* JSON pack plus an optional Markdown rendering of the same pack.
4. **Trace-back convention.** Generated code and tests should name the nodes they implement, for example
   a `spec: N-000042` comment or a test name. Nothing in rel01 consumes it, but defining it costs
   nothing and every later feature — measurement, design-versus-as-built comparison, impact analysis —
   needs it.

## 4. The manifest, which is the point

Every node the recipe reached is listed as `included full`, `included title`, `cut` (with the reason:
budget, or tier order) or `flagged` (conflicted, ambiguous, stale). The manifest also lists **family
members the recipe did not reach**, so a missing link shows up as a visible gap rather than as silence.

An agent that knows its context is partial asks for more. An agent that believes it is complete guesses.

## 5. Why it is not a spec yet

Its acceptance criteria would be written against pack contents, and pack contents depend on link types
that F6 has not yet produced on a real corpus. Writing them now would fix numbers and shapes chosen
from imagination. The honest order is: compile a real spec set (F1–F6), look at what the graph actually
contains, then specify the traversal.
