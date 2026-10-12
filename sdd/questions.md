# Question register

> **Status:** live · opened 2026-09-14 · 11 entries, all answered or closed
> **Role:** every design question, open or answered, with its context, the options considered
> **including the rejected ones and why**, and a pointer to where the answer binds (a spec, the
> constitution, or the vision). It records reasoning, never rules.

## Format

```markdown
### QR-<n> — <question>
- **Origin:** <rel01 S<k> / spec / finding>
- **Status:** open | answered <YYYY-MM-DD>
- **Context:** <why it matters>
- **Options:** <A — …> · <B — …> · <C — …>
- **Answer:** <chosen option> · **Rejected:** <option — reason>
- **Binds in:** <path §section>
```

## Open

*None at rel01 level. Spec-level open questions live in each spec §8.*

## Answered

### QR-1 — Model access: headless Claude Code, the Anthropic API, or both?
- **Status:** answered 2026-09-14
- **Answer:** C — one interface, two backends; headless Claude Code on Haiku by default, Anthropic API
  optional (keys in git-ignored `.env`). · **Rejected:** A headless only — no sampling control, caching
  or batch; B API only — requires keys for every user and bypasses the Claude Code login.
- **Binds in:** `specs/constitution.md` §6; rel01 D7

### QR-2 — Which pre-rel01 proposals are re-adopted, amended or rejected for rel01?
- **Origin:** rel01 S2 · **Status:** answered 2026-09-14 — **all approved** (rel01 D12), with amendments listed in D12
- **Context:** Before rel01, `archive/rel-01/design/rel01_design/core-working-principle.md` recorded proposals P-0…P-14
  for a broader vision. None is binding. Each needs an explicit keep, amend or reject so rel01 does
  not silently inherit or silently lose them:

  | Id | Proposal, in one line | Feeds |
  |---|---|---|
  | P-0 | Markdown files are the source of truth; the graph is compiled from them | G1 |
  | P-1 | The agent answers only small, closed, schema-checked questions; every accepted answer is recorded ("judgment lock") so rebuilds replay instead of re-asking | G2.2 |
  | P-2 | Four tests for "what is one atom": single verdict, independent change, single layer, stands alone | G2.2 |
  | P-3 | Sentence roles: requirement, constraint, assumption, decision become nodes; rationale and examples become annotations | G2.1–G2.2 |
  | P-4 | Canonical form (condition, trigger, subject, MUST/SHOULD/MAY, response); quantities normalized by code | G2.1–G2.2 |
  | P-5 | Guards: quotes found verbatim, coverage, no injected content, schema, weak-word flags | G2.2 |
  | P-6 | Stable ids; only changed blocks are re-atomized | G1, G2.2 |
  | P-7 | Layer set L0–L5 plus constraints and verification | G2.1 |
  | P-8 | Layer placement by a fixed yes/no questionnaire mapped by code | G2.1 |
  | P-9 | Family = the node's primary term, chosen by a fixed rule | G2.1 |
  | P-10 | Indexes, zoom levels, context recipes with a manifest | G2.3, G3.3 |
  | P-11 | Comparing design and as-built graphs | out of rel01 |
  | P-12 | Decisions (with rejected options) are nodes | G2.1 |
  | P-13 | `.sdd/` storage as JSON Lines | G1, G2.3 |
  | P-14 | Human visualization views | G2.3 (collapsed form) |
- **Binds in:** each sub-goal's design file, then its spec

### QR-3 — What does Haiku do, and what carries placement and retrieval?
- **Status:** answered 2026-09-14 (design role); output quality still to be measured in G4
- **Answer:** Haiku atomizes specs and forms nodes. Layers are hardcoded. Nodes carry abundant
  properties that support placement into layer and family, and retrieval of related nodes.
- **Binds in:** rel01 D8; G2.1, G2.2

### QR-4 — Where is conflict state recorded?
- **Status:** answered 2026-09-14 (storage); notification split into QR-5
- **Answer:** On each node: a status enum `validated` · `conflict` · `ambiguous`, and a list of related
  node ids sharing the same conflict. At graph level: a registry of all conflicted nodes, for fast
  lookup by AI agents. Follow-ups: QR-6, QR-7.
- **Binds in:** rel01 D9; G2.1, G2.3

### QR-5 — How is a conflict *notified* to a human or an AI agent inside Claude Code?
- ⛔ **CLOSED 2026-09-17 — not applicable to rel01** (D26: batch run, one end-of-run report). The
  answer below is kept for the release that adds live editing.
- **Origin:** split from QR-4 in rel01 S3 · **Status:** answered 2026-09-14 (rel01 D13) — A for AI agents (hook output after a spec edit, stopping at the first conflict) and D for humans (`sdd status` and command output showing all conflicts)
- **Options:** A — command hook output shown to Claude after a spec edit · B — prompt hook (Haiku)
  gating code edits that touch conflicted nodes · C — a skill Claude calls to list conflicts ·
  D — `sdd status` report for humans
- **Binds in:** `archive/rel-01/design/rel01_design/G3-algorithms.md` G3.2

### QR-6 — A node in more than one conflict
- **Origin:** gap in rel01 D9 · **Status:** answered 2026-09-14 — option B (rel01 D14)
- **Context:** D9 stores one list of related node ids per node. Node A may conflict with B about
  expiry and with C about size. A flat list `[B, C]` loses that these are two separate conflicts, so
  resolving one cannot clear only its part.
- **Options:** A — keep the flat list (simplest; resolution re-checks all) · B — add conflict records
  `{conflict_id, kind, members, rationale}` at graph level, and store `conflict_ids` on the node next to
  the flat related-id list
- **Binds in:** G2.1 node schema; G2.3 registry

### QR-7 — The status of a node before it has been checked, or after its neighbours changed
- **Origin:** gap in rel01 D9 · **Status:** answered 2026-09-14 — option A: add `unchecked` and `stale` (rel01 D15)
- **Context:** D9's enum is `validated` · `conflict` · `ambiguous`. A freshly formed node that has not
  yet been compared, or a validated node whose related node was just edited, is none of these. Marking
  it `validated` would claim a check that never happened.
- **Options:** A — add `unchecked` (and possibly `stale`) · B — keep three values plus a separate
  `checked_at` / `checked_against` field
- **Binds in:** G2.1 node schema

### QR-8 — How does the CLI know whether a human or an AI agent is writing specs?
- ⛔ **CLOSED 2026-09-17 — not applicable to rel01** (D26: one behaviour, no actor distinction). The
  answer below returns with live editing.
- **Origin:** rel01 D13 · **Status:** answered 2026-09-15 — option C, explicit `--actor ai|human`, default `human` (rel01 D16)
- **Context:** D13 treats the two differently (report all vs stop at the first conflict). Entry
  points: `sdd add`/`sdd ingest` typed in a terminal; `sdd hook post-edit` fired by Claude Code after
  an `Edit`/`Write`; `sdd add` run by Claude through its Bash tool (e.g. from the `/spec-add` skill).
- **Options:** A — by entry point only: `sdd hook …` = AI, everything else = human (misses Claude
  running `sdd add` via Bash) · B — entry point, plus an environment marker Claude Code sets in the
  shells it spawns (to verify: whether such a variable exists and is stable) · C — explicit flag
  `--actor ai|human`, which the skill and hooks always pass, defaulting to human
- **Binds in:** G3.2; F1 CLI contract

### QR-9 — Status precedence when several apply
- **Origin:** rel01 D15 · **Status:** answered 2026-09-15 — option A, precedence `conflict` > `ambiguous` > `stale` > `unchecked` > `validated` (rel01 D17)
- **Context:** A node can be ambiguous *and* in conflict, or stale *and* ambiguous. One enum value
  must win, or the status splits into flags.
- **Options:** A — precedence `conflict` > `ambiguous` > `stale` > `unchecked` > `validated`, with the
  underlying facts kept in other fields (`conflict_ids`, ambiguity list) · B — separate boolean flags
  plus a derived summary status
- **Binds in:** G2.1 node schema

### QR-10 — When is G4 (effectiveness measurement) designed: before coding, or after a graph exists?
- **Origin:** rel01 D20 vs D2 · **Status:** answered 2026-09-15 — option A (rel01 D22)
- **Context:** D2 says measurement is designed only after the compiler can ingest specs and produce a
  graph, so it is designed against real output. D20 says coding starts only after G4 is reviewed.
  Both cannot hold literally: no graph exists before coding.
- **Options:** A — review a G4 **outline** before coding (goals, metrics, what instrumentation the
  code must emit, such as run logs and read logs), and design the detailed experiment after a graph
  exists · B — design G4 fully before coding, amending D2 · C — keep D2; G4 is not part of the coding
  gate
- **Binds in:** rel01 D2, D20; `archive/rel-01/design/rel01_design/G4-measurement.md`
