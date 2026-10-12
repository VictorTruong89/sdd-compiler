# G3 — Algorithms: retrieval, conflict detection, traversal

> **Status:** GRADUATED (rel01 D27) · rel01 G3 · **Tier:** design, non-authoritative
> **Split confirmed** (rel01 D11): G3.1 → G3.2; G3.3 after G2.3.
> **Graduated 2026-09-17:** G3.1 → [`../../specs/F5_retrieval/spec.md`](../../specs/F5_retrieval/spec.md);
> G3.2 → [`../../specs/F6_conflicts/spec.md`](../../specs/F6_conflicts/spec.md); G3.3 stays design only,
> [`G3-3-traversal.md`](G3-3-traversal.md). The specs win where they differ.
> **Simplified by rel01 D26 (2026-09-17):** batch only. No notification channel, no stop-and-fix loop;
> every conflict is recorded and reported at the end of the run.
> **Grouping** moved to G2.1 (placement).

---

## G3.1 — Related-node retrieval (future F5)

When a new node forms, find the existing nodes it may relate to, using node properties (rel01 D8) and
graph indexes (G2.3), deterministically.
**To design:** candidate sources · ranking and cut-off · how candidate completeness is measured.
**Inputs:** pre-rel01 `core-working-principle.md` §5; worked example §9.

## G3.2 — Conflict detection & notification (future F6)

Judge candidate pairs with Haiku; set node `status`, `conflict_ids` and related ids; create or update
graph-level conflict records and the conflicted-node registry (rel01 D9, D14); notify.

### Reporting (rel01 D26)

One behaviour, whoever ran the command: compile everything, then report **all** conflicts, including
interlinked ones, in the command output, in `sddc conflicts`, and in the generated views (F4 §4.6).
The run exits `3` when open conflicts exist, so a script or CI can react.

**Deferred with live editing** (rel01 D13, D18, D25): stopping at the first conflict, delivering it to
an AI agent through a `PostToolUse` hook as `{"decision": "block"}`, the attempt counter, and
`sddc review dispute`. The mechanism was checked against the hooks documentation on 2026-09-14 and is
kept in the decision log for that release.

**Still to design:** relation kinds · pair question schema · when a conflict counts as resolved and how
records close · the shape of the end-of-run report · how many pairs are judged per node and the run
budget shared with atomization.

## G3.3 — Traversal for code generation (future F7)

How an AI agent walks the full-detail form of the graph to assemble coding context. Read-only.
Designed in rel01; built if time allows.
**Inputs:** pre-rel01 P-10 (zoom levels, context recipes, manifest); worked example §9.5–§9.6.
