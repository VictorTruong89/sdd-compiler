# Release 01 — Brainstorm & Decisions

> **SDD role:** `design/` tier — NON-AUTHORITATIVE. Brainstorm, rationale and decision log. **Do not
> code from this file.** Ideas graduate into `../specs/F<n>_<slug>/spec.md` once their acceptance
> criteria can be written. If this file and a spec disagree, the spec wins.
>
> **Status:** OPEN · **Opened:** 2026-09-14 · **Target close:** 2026-09-30 · **Previous release:** none
> A living document: each session appends.

---

## Release goal

**A quick, workable first release that shows how effective the SDD Compiler really is.**

> ★ **Simplified use case (rel01 D26, 2026-09-17).** rel01 builds a spec graph from **several static
> Markdown spec files** in one batch run. The hardest input it must handle is a spec set shaped like
> this repository's own `sdd/` tree. There is **no hook integration, no live input, no AI-driven
> editing loop**, and the compiler **does not stop at a conflicted node**: it compiles everything and
> reports **all** conflicts at the end.

Four goals, in dependency order (rel01 D2):

| # | Goal | Nature | Design document |
|---|---|---|---|
| **G1** | **Workable platform:** read static Markdown spec files (batch) | Build | [`rel01_design/G1-ingest.md`](rel01_design/G1-ingest.md) — approved (D19) → [`../specs/F1_ingest/spec.md`](../specs/F1_ingest/spec.md) 🟢, coding gated (D20) |
| **G2** | **Atomize specs** with Claude (Haiku); design node properties, graph layers and the spec-graph architecture | Build + design | [`rel01_design/G2-atomize-and-graph.md`](rel01_design/G2-atomize-and-graph.md) — approved (D23) → [`F2`](../specs/F2_node_model/spec.md) · [`F3`](../specs/F3_atomizer/spec.md) · [`F4`](../specs/F4_graph_store/spec.md) 🟢, coding gated (D20) |
| **G3** | **Design the algorithms:** related-node retrieval when a new node is formed; conflict detection with an end-of-run report; how an AI agent traverses the graph when generating code (design only) | Design (+ build where time allows) | [`rel01_design/G3-algorithms.md`](rel01_design/G3-algorithms.md) — placeholder · split G3.1–G3.3 (D11) |
| **G4** | **Effectiveness measurement**, designed only after the compiler can ingest specs and produce a graph | Design, after G1–G2 run | [`rel01_design/G4-measurement.md`](rel01_design/G4-measurement.md) — placeholder |

**Stack (rel01 D3, D7, simplified by D26):** a **Python CLI**. Model calls go through one interface
with two backends: headless Claude Code on Haiku (default) and the Anthropic API (optional).
**Claude Code hooks are not used in rel01** — see "Stack interpretation" below for what they would
have given, kept for when live editing returns.

### Breakdown of G2 and G3 (confirmed — rel01 D11)

The goals stay G1–G4. G2 and G3 are split into sub-goals along **contract boundaries**, so each
becomes one spec with its own acceptance criteria:

| Sub-goal | Content | Why separate | Depends on | Future spec |
|---|---|---|---|---|
| **G2.1 Node & layer model** | Node properties, hardcoded layers, **family grouping (placement)**, conflict status fields | The **central contract** every other part reads and writes. Deterministic; testable without a model | G1 | F2 |
| **G2.2 Atomizer** | Haiku produces nodes conforming to G2.1: question schemas, guards, re-ask, judgment lock | The only **non-deterministic** component. Isolating it keeps every other test model-free | G2.1 | F3 |
| **G2.3 Graph architecture & views** | Storage, indexes, conflicted-node registry, **collapsed (human) and full (AI) views** | Consumes G2.1 records; independent of how atoms were produced | G2.1 | F4 |
| **G3.1 Related-node retrieval** | Candidate generation when a new node forms; indexes it queries | **Prerequisite** for conflict detection: pairs are judged only on retrieved candidates | G2.1, G2.3 | F5 |
| **G3.2 Conflict detection & report** | Pair judgment (Haiku), status updates, conflict records, registry, one end-of-run report (D26) | Has its own failure modes | G3.1, G2.2 | F6 |
| **G3.3 Traversal for code generation** | How an AI agent walks the graph to build coding context | A **read-only consumer**, lowest dependency pressure; design in rel01, build if time allows | G2.3, G3.1 | F7 |

**Grouping moves from G3 to G2.1.** Family assignment is part of *placement*: it is decided when a
node is formed, from node properties, and every later algorithm depends on it being settled.

## Progress board — updated 2026-09-17

| Goal | Artefact | State |
|---|---|---|
| G1 ingest | [`F1_ingest`](../specs/F1_ingest/spec.md) 18 ACs | 🟢 approved · revised for D26 |
| G2.1 node & layer model | [`F2_node_model`](../specs/F2_node_model/spec.md) 23 ACs | 🟢 approved |
| G2.2 atomizer | [`F3_atomizer`](../specs/F3_atomizer/spec.md) 24 ACs | 🟢 approved · revised for D26 |
| G2.3 graph store & views | [`F4_graph_store`](../specs/F4_graph_store/spec.md) 18 ACs | 🟢 approved |
| G3.1 retrieval | [`F5_retrieval`](../specs/F5_retrieval/spec.md) 16 ACs | 🟡 draft — awaiting owner review |
| G3.2 conflicts & report | [`F6_conflicts`](../specs/F6_conflicts/spec.md) 19 ACs | 🟡 draft — awaiting owner review |
| G3.3 traversal | [`rel01_design/G3-3-traversal.md`](rel01_design/G3-3-traversal.md) | design only · spec id `F7` reserved |
| G4 measurement | [`rel01_design/G4-measurement.md`](rel01_design/G4-measurement.md) | ⬜ outline not written (D22) |
| — | [`rel01_design/build-plan.md`](rel01_design/build-plan.md) | ⬜ not written (D20 gate) |
| — | `src/`, `tests/` | ⬜ **no code yet** (gated) |

**Totals:** 6 specs · **118 acceptance criteria** · 0 tests · 0 lines of product code.
**Decisions:** rel01 D1–D27. **Question register:** 11 entries, all answered or closed.
**Vision:** adopted 2026-09-17. **Constitution:** §1 and §6 written; §2–§5 still `TODO`.

⚠ **Schedule.** Target close is 2026-09-30, thirteen days away, and nothing is built. The gate (D20) has
two items left: the G4 outline and the build plan. See "What ships by 30 September" below.

### The rel01 command surface, as currently specified

`sddc init · ingest · status · blocks · show` (F1) · `compile · atomize · review` (F3) ·
`map · family · conflicts · query · check` (F4) · `pairs` (F5) · `check-conflicts` (F6).

⚠ **Fifteen commands is a large surface for a first release.** Most are read-only views of one store,
so they are cheap, but each needs help text, `--json` output and tests. The build plan should decide
which are rel01 and which wait — a defensible minimum is `init · compile · status · conflicts · family`,
with the rest following once the graph proves useful.

## What ships by 30 September — the honest cut

The specs describe more than can be built in the remaining days. The build plan must order them so
that an incomplete release is still a working one. Suggested order, smallest useful thing first:

| Step | Gives | Without it |
|---|---|---|
| 1 · F1 + the F4 store | `sddc ingest` produces a block inventory that survives edits | Nothing else can run |
| 2 · F3 atomize (Q-ATOM, Q-DESC, guards) + F2 placement | Nodes in layers and families: **the spec graph exists** | No graph |
| 3 · F4 views | `sddc map`, `sddc family`, generated Markdown: a human can read the graph | The graph is invisible |
| 4 · F5 + F6 | Conflicts found and reported: **the purpose of the tool** | A graph nobody can act on |
| 5 · F3 attention list, F4 `check`, exhaustive mode | Hygiene and measurability | Usable, but harder to trust |

Steps 1–4 are the release. Step 5 is what makes the G4 study possible later.

## Stack interpretation — what "Python CLI + Claude Code Haiku hooks" can and cannot do

Checked against the Claude Code hooks and headless documentation on 2026-09-14.

| Mechanism | What it is | Can it atomize (return structured JSON to the CLI)? | Role in rel01 |
|---|---|---|---|
| *(not used in rel01 — D26)* **Command hook** (`type: "command"`) | Claude Code runs a shell command on an event and passes JSON on stdin | It runs code; it does not call a model by itself | **Trigger:** e.g. after `Edit`/`Write` of a spec file, run `sddc ingest <file>` |
| *(not used in rel01 — D26)* **Prompt hook** (`type: "prompt"`) | Claude Code sends the hook input plus a prompt to a model, **Haiku by default**. The model must answer only `{"ok", "reason", "impossible"}` | **No.** The answer is a gate decision, not arbitrary structured output | **Gate or notifier:** e.g. a `PreToolUse` check "does this edit touch a conflicted node?" (G3) |
| **Headless Claude Code** (`claude -p --model haiku --output-format json --json-schema …`) | The Python CLI starts a non-interactive Claude Code run as a subprocess; the answer arrives in `structured_output` | **Yes.** Schema-bound JSON, with usage and estimated cost | **The atomizer and the pair judge (G2, G3)**, invoked by the CLI, which is invoked by a command hook |

**Consequence under D26:** atomization runs as *CLI command → headless Claude Code on Haiku → JSON back
to the CLI → deterministic checks*. The hook rows above are kept because they are what live editing will
use in a later release; rel01 wires none of them.

**Three hazards to design against (G1/G2):**

1. **Hook recursion.** A headless `claude -p` started from inside a project loads that project's
   hooks unless run with `--bare`, and `--bare` does not use the subscription login — it needs
   `ANTHROPIC_API_KEY`. A hook that calls the CLI, which calls `claude -p`, which fires the same hook,
   loops. **Guard:** the CLI sets an environment marker (e.g. `SDD_COMPILER_CHILD=1`) on the child
   process, and every project hook script exits immediately when it sees the marker.
2. **Version-dependent flags.** Several headless behaviours are documented as version-dependent.
   The CLI checks `claude --version` at startup and records it with every judgment.
3. **API key leaking into Claude Code.** `.env` holds API keys for the optional Anthropic API backend.
   If the CLI loads them into its environment, a child `claude -p` inherits `ANTHROPIC_API_KEY` and may
   authenticate with the key instead of the Claude Code login, which changes who is billed.
   **Guard:** load `.env` only inside the API backend, and strip `ANTHROPIC_API_KEY` from the child
   environment of the headless backend unless the profile explicitly asks for it.

## Inputs carried into rel01 (reference, not decisions)

| Input | What it offers | Status |
|---|---|---|
| [`rel01_design/core-working-principle.md`](rel01_design/core-working-principle.md) | Proposals P-0…P-14: atomize → place → link → retrieve, storage, visualization, worked example | Pre-rel01; each proposal must be re-adopted or rejected here |
| [`../../docs/lectures/core-working-principle.html`](../../docs/lectures/core-working-principle.html) | Lecture on the same principle | Reference |
| [`../../docs/lectures/lecture-tiered-md-vs-graph.html`](../../docs/lectures/lecture-tiered-md-vs-graph.html) | Graph vs tiered/flat Markdown; storage; visualization; study design (Parts 6–10) — input to G4 | Reference |
| [`../archive/2026-09-13_vision_pre-rel01.md`](../archive/2026-09-13_vision_pre-rel01.md) | Scrapped vision (U1–U7, O1–O3) | Frozen |
| [`../archive/chat_history/`](../archive/chat_history/) | Two earlier AI discussions + course brief | Raw reference |

**Which pre-rel01 proposals feed which goal:**

| Goal | Candidate proposals to re-adopt, amend or reject |
|---|---|
| G1 | P-0 (prose is the source), P-6 (stable ids, block-level change detection), P-13 (`.sdd/` storage) |
| G2 | P-1 (question kinds, judgment lock), P-2…P-5 (atom tests, roles, canonical form, guards), P-7…P-9 (layers, placement, families), P-12 (decision nodes) |
| G3 | §5 links and candidate generation, P-10 (indexes, disclosure, context recipes), P-11 (as-built comparison — likely out of rel01) |
| G4 | Lecture Parts 6–10 (arms, metrics, Claude Code instrumentation, failure catalogue) |

## Scope

| In rel01 | Out of rel01 (unless decided otherwise) |
|---|---|
| G1–G4 as above | As-built vs design comparison (P-11): approved, deferred |
| Collapsed human form of the graph (P-14, D10); a viewer is built only if time allows | |
| Python CLI, Claude Code (Haiku) via hooks and headless runs | VS Code extension, MCP server, local ML models |
| Single writer | Multi-author editing |
| Ambiguity recorded as a node status | Clarifying-question dialogue |

## Risks

| Risk | Mitigation |
|---|---|
| Haiku atomization quality is too low for reliable nodes | Deterministic guards (quotes found verbatim, coverage, schema); measure stability early; the model is a setting, not hard-coded |
| Hook recursion or runaway cost from nested headless runs | Child-process marker; per-run budget cap in the CLI; log usage from every headless result |
| G3 algorithm design consumes the release | G3 is design-first; build only what G2's graph needs to show one conflict end to end |
| Claude Code CLI flags change | Version check and recorded version per judgment |

---

## Sessions

### S1 — 2026-09-14 — Workspace initialized

- Scrapped the previous vision; archived it.
- Initialized git, Claude configuration placeholders, and this `sdd/` workspace.

### S2 — 2026-09-14 — Release goals and stack

- Owner set the four release goals G1–G4 and the stack.
- Checked Claude Code hook types: prompt hooks (Haiku by default) return only a gate decision, so
  atomization must run through headless Claude Code started by the CLI.
- G1 design proposed: [`rel01_design/G1-ingest.md`](rel01_design/G1-ingest.md).
- **Next:** owner review of the G1 design; then G2 (node properties, layers, architecture).

### S3 — 2026-09-14 — Grouping of G2/G3; answers to QR-1, QR-3, QR-4

- Proposed splitting G2 into G2.1–G2.3 and G3 into G3.1–G3.3; grouping moves to G2.1. Awaiting
  owner confirmation.
- Owner requirement: the graph architecture serves **humans in collapsed form** and **AI agents in
  full detail** (D10). Design deferred to G2.3.
- QR-1 answered (D7), QR-3 answered (D8), QR-4 storage answered (D9). Notification channel split
  out as QR-5. Two gaps in D9 raised as QR-6 and QR-7.
- `.env` confirmed git-ignored and never committed.

### S4 — 2026-09-14 — Split confirmed; proposals approved; notification and status decided

- D11 split confirmed. D12 all pre-rel01 proposals approved, with amendments.
- D13 notification: humans see all conflicts; an AI agent is stopped at the first. Checked the
  documented hook outputs that make this possible (see G3.2).
- D14 conflict records; D15 `unchecked` and `stale` statuses.
- New questions: QR-8 (how the CLI knows whether a human or an AI agent is writing), QR-9 (status
  precedence).

### S5 — 2026-09-15 — QR-8, QR-9 answered; notification mechanism chosen; F1 drafted

- D16 `--actor` flag; D17 status precedence; D18 post-edit hook `decision: "block"` only.
- D19 G1 approved and written as `specs/F1_ingest/spec.md`: 26 acceptance criteria, 5 decisions,
  4 open questions with defaults.
- Consequence of D18 recorded in F1: AI agents add specs by editing the inbox file, not by running
  `sdd add`.
- **Next:** owner review of F1; then G2.1 node & layer model (F2).

### S6 — 2026-09-15 — F1 open questions resolved; F1 approved; coding gated

- F1 Q1–Q4 resolved as F1 D6–D9: one inbox; `sddc add --under HEADING`; command `sddc`; 15 s lock wait.
  Three ACs added for `--under` (AC-1.27…1.29).
- D20: F1 approved (🟢) but coding waits for G2–G4 review, a build plan and a task list.
- D21: command renamed `sddc`.
- New question QR-10: how D20's G4 review before coding fits D2.
- Build plan placeholder: [`rel01_design/build-plan.md`](rel01_design/build-plan.md).
- **Next:** G2.1 node & layer model.

### S7 — 2026-09-15 — QR-10 answered; F2, F3, F4 written

- D22: G4 outline before coding, detailed experiment after a graph exists.
- D23: G2.1–G2.3 approved and written as F2 (22 ACs), F3 (25 ACs), F4 (18 ACs). Details the approved
  proposals did not fix are marked ⚑ in each spec's §7: 7 in F2, 5 in F3, 5 in F4.
- Constitution §1 now declares the id families in use.
- **Next:** G3 review (G3.1 retrieval, G3.2 conflict detection, G3.3 traversal) → F5–F7; then the G4
  outline.

### S8 — 2026-09-16 — ⚑ review of F2, F3, F4

- Owner accepted every ⚑ drafting choice except **F2 D3**: removed nodes are **deleted** (D24).
- Owner replaced **F3 D4** with an AI-first fix loop, keeping D3 (automatic alignment) and D5
  (block-level writes) (D25).
- F2 gained AC-2.23 (deletion cascades); F3 gained AC-3.26…AC-3.30 (attempts, self-closing items,
  dispute, new-signature items, human mode does not loop); F4 gained id counters in `graph.meta.json`,
  a counters check, and AC-4.13 rewritten for deletion.
- **Next:** G3 review → F5 retrieval, F6 conflict detection, F7 traversal; then the G4 outline; then the
  build plan.

### S9 — 2026-09-17 — rel01 simplified to a batch compiler (D26)

- Owner simplified the release: static Markdown in, spec graph plus one conflict report out.
- Revised in place: `specs/vision.md` (now filled), `specs/F1_ingest` (live input, `--under`, hook
  adapter and `--actor` withdrawn), `specs/F3_atomizer` (hook trigger, actor stop and the AI fix loop
  withdrawn; the review queue becomes an end-of-run attention list), `design/rel01_design/G1-ingest.md`
  and `G3-algorithms.md`.
- Closed as no longer applicable: QR-5 (notification channel) and QR-8 (actor detection).
- The F5/F6/F7 conflict list shrinks: 6.1, 6.2, 6.6 and 5.3's bootstrap mode disappear with the
  interactive loop; 5.4 (`checked_against`) is deferred, since every run checks the whole graph.
- **Next:** write F5 and F6 for the batch case, F7 as design-only, then the G4 outline and the build
  plan.

### S10 — 2026-09-17 — F5 and F6 written; F7 kept as design

- F5 adds two candidate sources beyond the pre-rel01 rule (shared keywords, same measured property),
  fixed additive scoring with a per-node cap, a `pair_key` that re-opens exactly the pairs an edit
  touches, and an exhaustive mode that exists only to measure what ranking misses.
- F6 fixes the closed list of relation kinds, when a relation becomes a conflict record, that ambiguous
  nodes are judged provisionally, that a conflict closes only on re-judgement or member deletion, and
  the end-of-run report.
- Conflict-list items now settled: 5.1, 5.2, 5.3 (cap + shared budget), 6.3, 6.4, 6.5, 6.7, X.1.
  Deferred: 5.4 (`checked_against`). F7 items 7.1–7.4 are recorded in the design note.
- **Next:** the G4 outline (rel01 D22), then the build plan (rel01 D20).

---

## Decisions log

> Append-only. `rel01 D<n> — YYYY-MM-DD — decision. Rationale. Rejected: option — reason.`

- **rel01 D1 — 2026-09-14 — Scrap the pre-rel01 vision; rewrite `specs/vision.md` from scratch for
  a quick first release.** Rationale: ship a workable product by end of September and learn from use.
  The old vision is archived, not deleted.
- **rel01 D2 — 2026-09-14 — Release goals are G1 (ingest file or live CLI specs), G2 (atomize with
  Claude; node properties, layers, architecture), G3 (grouping, conflict detection with notification,
  retrieval for new nodes, traversal for code generation), G4 (effectiveness measurement, designed
  after G1–G2 work).** Rationale: owner decision; measurement is designed against a working graph
  rather than in advance.
- **rel01 D3 — 2026-09-14 — Stack: Python CLI plus Claude Code (Haiku) through hooks.** Rationale:
  owner decision. Interpretation recorded above; direct Anthropic API use is open (QR-1).
- **rel01 D4 — 2026-09-14 — `chat_history/` moved to `sdd/archive/chat_history/` and tracked in
  git.** Rationale: owner decision; keeps the pre-rel01 reasoning with the project history.
- **rel01 D5 — 2026-09-14 — No day-by-day plan for rel01.** Rationale: owner decision. Goals and
  their dependency order are the plan.
- **rel01 D6 — 2026-09-14 — Code is never committed automatically.** Rationale: owner decision; the
  owner commits after review.

- **rel01 D7 — 2026-09-14 — Model access through one interface with two backends: headless Claude
  Code (`claude -p --model haiku --json-schema`, default) and the Anthropic API (optional, keys in
  `.env`).** Resolves QR-1. Rejected: headless only — gives up sampling control, caching and batch;
  API only — needs keys for every user and bypasses the Claude Code login.
- **rel01 D8 — 2026-09-14 — Haiku atomizes specs and forms the nodes. Layers are hardcoded. Nodes
  carry abundant properties to support placement into layers and families, and retrieval of related
  nodes.** Resolves QR-3's design question. Whether Haiku's output quality is sufficient remains a
  measurement for G4.
- **rel01 D9 — 2026-09-14 — Conflict state is stored on the node: a status enum
  (`validated` · `conflict` · `ambiguous`) and a list of related node ids that share the same
  conflict. The graph also records a registry listing all conflicted nodes, so an AI agent finds them
  in one read.** Resolves QR-4's storage question. Open follow-ups: QR-5 (notification channel), QR-6
  (a node in several conflicts), QR-7 (status before checking).
- **rel01 D10 — 2026-09-14 — The graph architecture must serve two forms: collapsed for humans, full
  detail for AI agents.** Design in G2.3.

- **rel01 D11 — 2026-09-14 — Split confirmed: G2.1 node & layer model (incl. family grouping), G2.2
  atomizer, G2.3 graph architecture & views; G3.1 related-node retrieval, G3.2 conflict detection &
  notification, G3.3 traversal for code generation.** Rationale: one contract per spec; the
  non-deterministic atomizer isolated; retrieval before conflict detection.
- **rel01 D12 — 2026-09-14 — Pre-rel01 proposals P-0…P-14 approved** (`rel01_design/core-working-principle.md`),
  with these amendments from later rel01 decisions, which win where they differ:
  - status names and values follow D9 + D15, replacing the pre-rel01 `clean` / `conflicted` names;
  - conflict storage follows D9 + D14;
  - P-11 (as-built comparison) is approved but deferred beyond rel01;
  - P-14 (visualization) is realized first as the collapsed human form (D10); a viewer is built if
    time allows.
- **rel01 D13 — 2026-09-14 — Conflict notification differs by who is writing** (resolves QR-5):
  - **Human** (CLI in a terminal): process everything, then report **all** conflicts, including
    interlinked ones, in the command output and in `sdd status`.
  - **AI agent** (inside Claude Code): **stop at the first conflicted node** so the agent fixes it
    before adding more. Rationale: conflicts that pile up are costly to resolve. Mechanism in
    `rel01_design/G3-algorithms.md` G3.2; caller detection is QR-8.
- **rel01 D14 — 2026-09-14 — Conflict records at graph level** (resolves QR-6, option B):
  `{conflict_id, kind, members, rationale, …}`. Each node stores `conflict_ids` alongside the flat
  list of related conflicted node ids (D9).
- **rel01 D15 — 2026-09-14 — Status enum adds `unchecked` and `stale`** (resolves QR-7, option A):
  `unchecked` · `validated` · `conflict` · `ambiguous` · `stale`. Precedence when several apply is QR-9.

- **rel01 D16 — 2026-09-15 — Every command that ingests takes an explicit `--actor ai|human` flag,
  default `human`; hooks and skills always pass `ai`** (resolves QR-8). Rejected: entry point only —
  misses Claude running the CLI through Bash; environment marker — unverified and fragile.
- **rel01 D17 — 2026-09-15 — Status precedence `conflict` > `ambiguous` > `stale` > `unchecked` >
  `validated`; the underlying facts stay in their own fields** (`conflict_ids`, ambiguity list)
  (resolves QR-9). Rejected: separate boolean flags with a derived summary — more states to test for
  the same information.
- **rel01 D18 — 2026-09-15 — AI-agent conflict notification uses only the `PostToolUse` command hook
  after a spec edit, returning `{"decision": "block", "reason": …}`.** Rejected for rel01: a
  `PreToolUse` gate that denies further spec edits; strict mode (`continue: false`); a dedicated exit
  code for `sdd add` run through Bash. Consequence: an AI agent must write specs with Edit/Write (not
  `sdd add` in Bash), so the hook always fires (F1 D3).
- **rel01 D19 — 2026-09-15 — G1 design approved; graduated to `specs/F1_ingest/spec.md` (🟡 draft).**

- **rel01 D20 — 2026-09-15 — F1 approved, but no coding starts until G2, G3 and G4 are reviewed and a
  rel01 build plan and task list exist.** Sequence: review G2 (G2.1–G2.3) → G3 (G3.1–G3.3) → G4 → build
  plan + task list → code. ⚠ This moves G4's review **before** coding, whereas D2 said measurement is
  designed only after the compiler produces a graph. Open as QR-10.
- **rel01 D21 — 2026-09-15 — The command is `sddc`** (F1 D8). Package `sdd_compiler`; store `.sdd/`.
  Earlier log entries that say `sdd …` refer to the same command.

- **rel01 D22 — 2026-09-15 — G4 in two steps** (resolves QR-10, option A): a G4 **outline** — goals,
  metrics, and the instrumentation the code must emit — is reviewed before coding; the detailed
  experiment is designed after a graph exists. D2 stands for the detailed design; D20's gate covers the
  outline.
- **rel01 D23 — 2026-09-15 — G2.1, G2.2, G2.3 approved and written as `specs/F2_node_model`,
  `specs/F3_atomizer`, `specs/F4_graph_store` (🟢, coding gated by D20).** Each spec marks its own
  drafting choices with ⚑ for review.

- **rel01 D24 — 2026-09-16 — Removed nodes are deleted, not kept.** The owner asked what a `removed`
  node would be for; the answers (history, undo, later as-built comparison) are all covered by git,
  because `.sdd/` is committed. Consequences specified in F2 §4.9 and D3: monotonic id counters so an id
  is never reused, cascade deletion of links, conflict records closed with reason `member_deleted`, and
  `stale_reasons` on every neighbour. ⚠ F1 still keeps *blocks* with status `removed`, because block
  identity drives change detection; only nodes are deleted.
- **rel01 D25 — 2026-09-16 — When a blocking item stops an AI-driven run, the AI agent fixes it
  immediately; the human is the last resort.** Repeats of the same item count attempts; at
  `ai_fix.max_attempts` (3), or when the agent disputes the item (`sddc review dispute`), the item is
  escalated and the agent must stop and ask the human. Rationale (owner): *better to write specs slowly
  than to resolve many conflicted specs at the end.* Rejected: queueing every blocking item for the
  human — the agent idles and conflicts pile up; unlimited retries — an agent that cannot fix an item
  loops and burns tokens.

- **rel01 D26 — 2026-09-17 — rel01 is a batch compiler over static Markdown spec files.** One command
  reads the spec files, atomizes them, builds the graph, checks every candidate pair, and **reports all
  conflicts at the end**. Rationale (owner): the interactive use case had grown more complicated than a
  first release can carry, and a batch compiler is enough to see whether the idea works.
  **This decision supersedes, in whole or in part:**

  | Superseded | Status under D26 |
  |---|---|
  | **D13** — humans see all conflicts, an AI agent is stopped at the first | The "stop at the first" half is withdrawn. Every run reports all conflicts |
  | **D16** — `--actor ai\|human` | Withdrawn for rel01. There is one behaviour, so no actor distinction is needed |
  | **D18** — the `PostToolUse` hook is the AI notification channel | Withdrawn for rel01. No hooks. The channel is the CLI report |
  | **D25** — AI fixes blocking items, 3 attempts, then escalate | Withdrawn for rel01. Items that need a human are listed in the report |
  | **D21** — command `sddc` | Stands |
  | **D24** — deleted nodes, id counters | Stands |
  | **D9, D14, D15, D17** — status values, precedence, conflict records, registry | Stand. They describe the graph, not the interaction |
  | **D7** — two model backends | Stands |
  | **D20** — coding gated until G3, G4 and the build plan | Stands |

  Everything withdrawn is **deferred, not deleted**: it returns when live editing does.

- **rel01 D27 — 2026-09-17 — G3 graduated: F5 (related-node retrieval, 16 ACs) and F6 (conflict
  detection and report, 19 ACs) written as specs; G3.3 stays design only** in
  `rel01_design/G3-3-traversal.md`, with spec id `F7` reserved. Rationale: F7's acceptance criteria
  would have to be invented before any real graph exists; F5 and F6 can be specified now because the
  graph model (F2) and the store (F4) are fixed.

## Rejected alternatives

- **Prompt hooks as the atomizer** — rejected by the documented response schema: a prompt hook
  returns only `ok` / `reason` / `impossible`, not structured node data.

## Open questions

*Tracked in [`../questions.md`](../questions.md): QR-1…QR-10 answered. Spec-level questions live in each spec §8.*
