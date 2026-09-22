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

## Progress board — updated 2026-09-19

| Goal | Artefact | State |
|---|---|---|
| G1 ingest | [`F1_ingest`](../specs/F1_ingest/spec.md) 20 ACs | 🟢 approved · revised for D26, D13 (F1) |
| G2.1 node & layer model | [`F2_node_model`](../specs/F2_node_model/spec.md) 28 ACs | 🟢 approved · open: Q1 · D18 … D20 added (M3 gate) |
| G2.2 atomizer | [`F3_atomizer`](../specs/F3_atomizer/spec.md) 24 ACs | 🟢 approved · revised for D26 · open: Q1, Q3 |
| G2.3 graph store & views | [`F4_graph_store`](../specs/F4_graph_store/spec.md) 18 ACs | 🟢 approved |
| G3.1 retrieval | [`F5_retrieval`](../specs/F5_retrieval/spec.md) 16 ACs | 🟢 approved (D28) |
| G3.2 conflicts & report | [`F6_conflicts`](../specs/F6_conflicts/spec.md) 19 ACs | 🟢 approved (D28) |
| G3.3 traversal | [`rel01_design/G3-3-traversal.md`](rel01_design/G3-3-traversal.md) | design only · spec id `F7` reserved |
| G4 measurement | [`rel01_design/G4-measurement.md`](rel01_design/G4-measurement.md) | ✅ outline approved (D29) |
| — | [`rel01_design/build-plan.md`](rel01_design/build-plan.md) | ✅ approved (D29); B1–B3 decided |
| — | `src/`, `tests/` | ✅ M1, M2, M3 (gated) · 🔨 **M4** — T15 … T18 built; `compile` = ingest → atomize → **check** → report · 617 tests · **M4 gate done; dogfood run on our own specs** (M4-gate.md §7) · next: the close |

**Totals:** 6 specs · **128 acceptance criteria** (AC-5.17, AC-6.21 added by R19) · 617 tests · M1, M2 built and gated; M3 built and gated (content re-measured in R15); remaining work: build-plan §9.
**Decisions:** rel01 D1–D33. **Question register:** 11 entries, all answered or closed.
**Vision:** adopted 2026-09-17. **Constitution:** §1 and §6 written; §2–§5 still `TODO`.

⚠ **Schedule.** Target close is 2026-09-30. The D20 gate is satisfied (D29); M1 is built; M2's tasks are built. Next: the I-43 fix, a
sampled M2 gate, then M3 and M4 (build-plan §9; when to compile: S26). See "What ships by 30 September" below.

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

### S13 — 2026-09-18 — gate satisfied (D29); M1 T1 built

- D29: G4 outline and build plan approved; B1 `pipeline.py` under F3, B2 five commands, B3 test tiers
  adopted into constitution §4 (plus §6: Python ≥ 3.11, `src/` layout, setuptools, pytest).
- **T1 built, test-first:** `pyproject.toml`, `errors.py` (the seven exit codes), `profile.py`
  (CT-1.4 with strict validation), `cli.py` (CT-1.6 skeleton, five commands registered), `__main__.py`.
  **15 tests green.**
- ⚠ **Spec-versus-library conflict found and resolved in favour of the spec:** argparse exits `2` on a
  usage error, but CT-1.6 reserves `2` for input errors and `1` for usage. The parser is subclassed so
  a usage error exits `1`.
- Deliberate: a registered but unimplemented command prints what it is and exits `1`, rather than
  pretending to work.
- **Next:** T2 store primitives, then T3 segmentation.

### S38 — 2026-09-22 — I-82: the money was never money; handover for the full-corpus run

- **I-82, found by the owner:** the Console showed no credit deduction, and it never would. Every `$`
  in this repository is Claude Code's own `total_cost_usd` summed per call — **an estimate of the
  equivalent API list price**, on the owner's **subscription**. No organization credits move, and the
  Usage & Cost Admin API (`/v1/organizations/cost_report`, Admin key, curl-only) reports API traffic
  only, so these runs are absent from it by design. Anthropic's own docs call the Claude Code figures
  "estimated". G4 §2 and M4-gate §7 relabelled; every earlier figure carries the caveat.
  **The lesson:** a number can be measured, reproducible, correctly summed — and still be the wrong
  number, because it was given the wrong name.
- **Token shape from the dogfood's 238 calls:** 992 uncached input tokens against **5.78 M cache
  reads** and 394 K output — the harness prompt, re-read once per call. I-8's finding, still true
  after every optimisation: the call count is the cost.
- **Handover written** for a fresh session to run the close-out measurement:
  [`rel01_design/HANDOVER_full_compile.md`](rel01_design/HANDOVER_full_compile.md) — `sdd/specs/` end
  to end, subscription only, in resumable rounds with the store as the checkpoint.
- **617 tests.** All four milestones built; what remains is a decision (I-81) and this measurement.

### S37 — 2026-09-22 — B, A, C: the compiler read our own specs and found a defect we had just made

- **B (F5 D13):** `max_pairs_per_node` 10 → 6. 36 % fewer pairs on R17's store, every known-real pair
  kept. Rejected `min_score: 2.5`, which would delete the keyword-only class S5 exists for.
- **A (F6 D18):** Q-PAIR is batched, 8 pairs per call — rel01 D30's lever applied to the phase that
  now dominates. Each answer still checked alone, a failure re-asking that pair alone. The gate corpus
  needs **15 judge calls instead of 159**.
- **I-79 (F3 D37), found by C:** one Q-ATOM call over 20 dense blocks returned no `structured_output`,
  which the backend called "backend unavailable" — ending a 173-block compile after 19. One unusable
  answer is now re-asked per item; a dead backend, a missing binary and a 429 stay exit 6.
- **C — the dogfood.** F5 + F6, 181 real blocks, $6.32: **192 nodes, 562 pairs judged, 70 conflicts**,
  exit 3, store clean. Write-up: `rel01_design/M4-gate.md` §7.
  - **It found a defect introduced that day** (I-80): D13 changed the cap to 6 and D6, §4.3 and
    AC-5.10 still said 10. Fixed. Plus a real under-specification in §4.1.
  - **M2 on a sample of 39: 4 real, ≈ 10 %** — against 71 % on the fixture.
  - **Why (I-81): 65 of the 70 involve an acceptance criterion or a decision entry.** Our specs'
    own structure — a criterion restating its rule, a heading summarising its body — reads as
    duplication. F6 D16 suppresses that only when `verifies` resolved.
  - **Cost, measured:** $0.035 per block. The whole repository ≈ **$26**, not the $12 the fixture
    suggested.
- **617 tests.** **Next:** the owner's call — extend "the form says so" to decision headings, and
  whether to spend ≈ $26 on the full repository for the close.

### S36 — 2026-09-21 — R15, R16 built; R17 re-run: precision 27 % → 71 %

- **R15 (F5 D11):** S2 follows `broader` (F2 D16 recorded it since the M2 gate; nothing read it), and
  S6 takes a shared **keyword** instead of a shared term. Measured offline first: 5 GB/5 GiB pair
  rank 123 → 50, alias pair 81 → 43, at 19 extra candidates.
- **R16 (F6 D15):** the judge is told when two numbers are *not* a contradiction — a limit inside a
  longer one, a window and what follows it, a rule and its clarification — and forbidden to calculate.
- **R17**, same three files byte-identical, cap raised so nothing was skipped: **159 of 159 pairs
  judged**, 7 conflicts, exit 3, store clean, $2.35.
  - **Precision 3 of 11 (27 %) → 5 of 7 (71 %)** · **recall 1 → 2 of 6** (P4 found).
  - **G2 and G3 now pass; G1 still fails.**
  - **I-76, the finding:** the naming problem moved into the judge. R15 delivered the two quantity
    pairs and the model refused them — *"different export types (export archive vs workspace
    export)"*. Term hygiene at atomization is the one lever left.
  - **I-77:** R16's "an AC restating its requirement is not a duplication" rule did not take; that one
    belongs in code.
- **Cost, now measured:** $0.076 per block complete → this repo's 733 blocks ≈ **$55** (R18).
- **607 tests.** **Next:** R18 (the close-out number) and the owner's call on term hygiene.

### S35 — 2026-09-21 — T19 built; **the M4 gate ran, and failed usefully**

- **T19** (9 tests): `sddc conflicts judge CF-… --verdict real|false` → `.sdd/adjudications.jsonl`
  (**F6 AC-6.20, D14**). M2 is now recordable — the number the close is about.
- **Planted fixture written** (`tests/fixtures/planted/`, G4 §3 corpus 2): 3 files, 28 blocks, six
  pairs in `EXPECTED.md`, in ordinary spec voice. A suite test keeps it alive.
- **Pass line written before the run finished** — the protocol step M3 failed.
- **The M4 gate: the whole product ran end to end for the first time.** 28 blocks → 34 nodes → 123
  pairs → 72 judged → 11 conflicts, store clean, $1.30. Write-up: `rel01_design/M4-gate.md`.
  - **M1 recall 1 of 6** planted pairs · **M2 precision 3 of 11 (27 %)** → **the gate fails**.
  - **Where it fails matters:** every planted pair *was* proposed. Five ranked 81st–130th of 137
    because each side carries its own term, so S1 and S2 are dead and only keyword overlap fires
    (I-73). The misses are in ranking, not judging.
  - 5 of the 8 false positives are one repeated mistake: two different numbers read as a contradiction
    (I-74).
  - **It found a real duplication nobody planted** — an accident in the fixture's own prose.
  - **Cost does not reach this repo** (I-75): 733 blocks against the fixture's 28.
- Also I-71 (a 429 on the first call, handled exactly as F3 D24 designed) and I-72 (a backend stop
  reported as the call cap — fixed).
- **604 tests.** **Next:** the owner's calls on R15 … R18 in the gate file.

### S34 — 2026-09-21 — R16 read; M3 gate closed; I-70 found and fixed

- **R16** ($1.31, after $1.20 lost to I-67's crash): failures 4 → 1, all seven `S` rows labelled,
  criteria resolving what they test **5 of 18 → 10 of 23**, S3 pairs 42 → 19. `M3-gate.md` §5.
- ⚠ **I-69:** R16 was not the controlled A/B it was launched as — F5 had gained D10 and its
  traceability rows between the two runs. The corpus is this repository, and it moves while it is
  measured. Pin and hash the corpus before a measured run.
- **The blind reading got worse, not better:** ✅ 10 of 34 cards → **4 of 35**, ❌ 6 → 12.
- **I-70, the cause:** the split re-ask undid F3 D34. Every `S` row was split into its rule and its
  evidence cell, making bare fragments ("the term ids", "the block id") and five unreadable one-node
  families. **F3 D36**: a block that is one claim by its own form is never asked to split.
- **M3 gate closed** (`M3-gate.md`): the views pass; the content fails with a named cause for each
  part. Three readings, three real defects — each found by a person reading output, not by the suite.
- **594 tests.** **Next:** T19, then the M4 gate.

### S33 — 2026-09-21 — M4 built: T15 … T18. `compile` now reports conflicts

- **T15 retrieval** (22 tests): S1 … S7 with their evidence, additive scoring with per-source caps,
  ranking, the per-node cap, `pair_key`, and which nodes are checked. **F5 D10**: the CT-5.3 counts
  count proposals, not distinct pairs, or AC-5.16's identity cannot hold.
- **T16 the pair judge** (18 tests): Q-PAIR, its two guards, and what each verdict records.
  **F6 D11**: the direction rule lives in the JSON Schema, so a symmetric relation carrying a
  direction is rejected before anything reads it.
- **T17 the check phase** (19 tests): `compile` = ingest → atomize → **check** → write. One budget for
  the run (F6 D5), never stops at a conflict, exit 3 and 5 wired. **F6 D12** (the counts also record
  what was *not* judged) and **F6 D13** (a node the phase looked at loses the stale reasons that
  scheduled it).
- **T18 the report** (12 tests, 2 goldens): `sddc compile` now prints what failed, what formed no node,
  what was dropped, and every open conflict — grouped so interlinked records read together (F4 AC-4.16)
  and contradictions first (F6 D9). `sddc conflicts` ships as the sixth command; exit 3 while any is open.
- **R16 crashed and was re-run** (I-67, I-68): see S32's entry and `M3-gate.md`.
- **593 tests.** **Next:** T19 (the adjudication record), then the M4 gate — the release.

### S32 — 2026-09-21 — R15: the I-56 fixes measured; two more defects

- **F3 D33 built first:** the run report now counts blocks that completed and formed **no** node, with
  their lines and sentence roles. R15 found 15, every one `context` (headings, legends) — and none of
  the seven rules that vanished silently in R12.
- **R15** — F5 recompiled in a fresh store, $1.20, 64 nodes (R12: 43). Write-up:
  [`rel01_design/M3-gate.md`](rel01_design/M3-gate.md); cards and raw output in
  `rel01_design/measurements/`.
  - **The I-56 fixes work.** The `node` grab-bag holds 4 criteria, not 9. Five criteria resolved
    `verifies` and joined the family of the rule they test. `S3` … `S7` carry their local labels.
    Family null 3 → 1.
  - **The I-57 fix is confirmed on fresh data:** the same store gives 178 constraint-scope pairs under
    the old rule and **42** under F5 D9.
  - **Two new defects, both from rows becoming claims** (**F3 D34**): the model quoted the section and
    table-header context lines, failing 4 blocks — the S1, S2 and S6 rows, which is why their criteria
    stayed in `node` (I-63); and a row came back as one atom per cell, so one rule became three
    fragments (I-64).
  - **Open (I-65):** the graph is wider, not denser — 97 terms for 64 nodes, 58 % used once, 42 % of
    nodes in families of three or more (was 56 %).
- **The blind reading** (a fresh agent with the cards and nothing else): ✅ **10 of 34 cards, 30 of 64
  nodes (47 %)**, against 3 of 19 cards and 28 % of nodes at R12; ❌ down from 42 % of nodes to 23 %.
  Against the proposed pass line (largest family ✅, half the nodes in ✅ cards) R15 **fails both** —
  but three of the six ❌ cards are artefacts of I-63 and I-64, fixed after the run. The reader also
  found what the metrics missed: dangling pronouns, and the in-scope list reading as boilerplate (I-66).
- **522 tests.** **Next:** the owner confirms the pass line and the §3 verdict; optionally R16 (a fair
  reading, ≈ $1.20); then T15 — M4 is the release and has not started.

### S31 — 2026-09-19 — M3 gate closed; I-56, I-57, F4 Q2, gate protocol

- **Owner approved** the card-by-card reading in `R12_views_on.md`. **M3 gate:** the view code passes;
  the graph content fails.
- **I-56 fixed in code.** The data showed three causes, one of which my suggestion had missed:
  - Q-ATOM labelled F5's S1 … S7 rows `definition`, so they formed no node (I-59, **F3 D32**). The
    suggestion to resolve `S1` assumed nodes that did not exist (I-60).
  - The subject rule ran before the verification rule for criteria (I-61, **F2 D18**).
  - Ids such as `S4` could not be cited (**F2 D20**, local labels, resolved within their file).
  - Components never seeded a family, so exhaustive mode had none (**F2 D19**, as a last resort).
  - New acceptance criteria: AC-2.26 … AC-2.28.
- **I-57 fixed:** a layer-only scope needs a shared term or keyword (**F5 D9**, the same bar as D7). One
  `covers` function serves the card and S3. On R12, S3 pairs fall from ≈ 60 to 16. AC-5.3 amended.
- **F4 Q2 closed as D17:** the Markdown card keeps full text; the terminal cuts at 80.
- **Gate protocol adopted** (build-plan §3): pass line first; every output or a blind sample; a
  first-time reader; a verdict per item; durable evidence (I-62).
- **517 tests, 125 ACs** (recount; the board said 121 before, actually 122). **Next:** R15, re-compile F5 and re-read every card; then T15.

### S30 — 2026-09-19 — M3 gate reviewed

- **Evidence widened:** the R12 "on" store had survived in an earlier session's scratch folder. All 19
  real cards were rendered, not the two chosen before (I-54). They are in
  `rel01_design/measurements/R12_views_on.md`, with a one-sentence reading of each card for the owner
  to confirm.
- **Three defects fixed, test first:**
  - `sddc family "(no family)"` was refused (I-51).
  - AC-4.18's property test checked a helper the map did not use (I-52).
  - Every card showed "Kind of: (no family)" when any node was unplaced (I-53, found only on real data).
- **Four card changes, F4 D13 … D16 ⚑:**
  - lines follow the source;
  - constraints in scope are shown as lines, not ids;
  - "Kind of" and "Narrower families" come from `broader`;
  - an ambiguous line names its kinds.
- F4 traceability for AC-4.14, AC-4.17 and AC-4.18 is marked partial, because `sddc map` and
  `query map` are deferred (I-58). **498 tests.**
- **Claude's reading: the view code passes; the graph content does not.** Only 3 of 19 cards (12 of 43
  nodes) read as a coherent group. The largest, `node`, holds nine S1 … S7 criteria filed by their Given
  clause (I-56).
- **Open for the owner before T15:**
  - **I-56:** the family subject for criteria.
  - **I-57:** layer-only constraint scope. By the card's rule, S3 alone proposes about 60 pairs among 43
    nodes, above `min_score`.
  - **F4 Q2:** text width.

### S29 — 2026-09-19 — R12 … R14 done; M3 built

- **R13, R14 built** (F3 D30, D31): resolve references before flagging `referential`; `narrower`
  points specific → general, reversed verdicts refused by code.
- **R12, re-run** after a re-login cleared the scratch area and lost the first result (I-50). One whole
  spec (F5, 65 blocks), R2 off against R2 on: terms used once **67 % → 42 %**, nodes in families of three
  or more 42 % → 56 %, cheaper; one-node families unchanged at about two thirds. Reports now kept in
  `rel01_design/measurements/`. Write-up: `rel01_design/M2-gate.md` §B8.
- **M3 built:** T13 indexes and `status` graph counts (F1 CT-1.5 extended); T14 the map, family cards,
  generated `.sdd/views/`, `sddc family NAME` (F4 D10 … D12), two reviewed golden files. The first golden
  review caught a missing in-scope constraint and a row-order oddity; the first real card caught stray
  Markdown marks. **494 tests.** M3 gate: the owner reads the real cards in
  `measurements/R12_views_on.md`.

### S28 — 2026-09-18 — R1 … R11 built; R6 re-measured

- **rel01 D33** (owner): R1 and R2, option (a) each. **All eleven gate fixes built** test-first (F2 D16,
  D17; F3 D9 extended, D25 … D29). **477 tests.**
- **R6** (same 63 blocks, two fresh runs, $1.64): 60 and 61 blocks completed (was 60, 51); no node
  without a family beyond 7.5 %; every acceptance criterion one `V` node; wrong merges down from ≈ 27 to
  5; 40–57 % cheaper; runs agree on node count for 75 % of blocks (was 49 %). **Not met:** the family
  targets — which this scattered sample cannot measure (I-49, my target-setting error). Proposed R12 (a
  dense sample), R13 (`referential` resolution), R14 (`narrower` direction). Details:
  [`rel01_design/M2-gate.md`](rel01_design/M2-gate.md) §B7.

### S27 — 2026-09-18 — I-42, I-43 fixed; the M2 gate measured

- **F3 D23** (owner): a split refused twice is formed with the first yes's layer, flagged
  `mixed_layers` (F2 D15). **F3 D24** (owner): a backend failure mid-run keeps finished work.
- **M2 gate, run on a stratified sample** (63 blocks, 9 per shape, two independent runs, $3.21 in
  total): results, findings G-1 … G-14 and recommendations R1 … R11 in
  [`rel01_design/M2-gate.md`](rel01_design/M2-gate.md) — Part A a plain-language lecture, Part B the record,
  Part C a verdict and reason for every sampled block (run 1: 23 ✅ · 25 ⚠️ · 15 ❌; run 2: 12 ✅ · 27 ⚠️ ·
  24 ❌), adding findings G-9 … G-14 and recommendations R7 … R11. Headline: the pipeline is robust
  (all checks clean, the usage limit hit and was survived); **families do not group** (G-1), **Q-TERM
  merges hyponyms** (G-3), **fresh runs disagree** (G-6). A crash found and fixed (I-45). **463 tests.**

### S26 — 2026-09-18 — Progress review; when to compile

- **Remaining code** (build-plan §9): I-43 fix; M3 (T13, T14); M4 (T15–T19), which is the release.
  Seven tasks, eight working days to 2026-09-30.
- **Owner question: compile once all code is finished?** Answer recorded: **no, and not a full one
  now.**
  1. **Now — no full compile.** A full compile (≈ 733 blocks, ≈ 1,000+ headless calls, extrapolated
     ≈ $19 and ≈ 3 h) runs on the owner's Claude Code subscription, whose session was at 86 %; under
     I-43 a usage-limit stop mid-run would throw the whole run away.
  2. **After I-43 (and ideally I-42): one small, stratified M2-gate run** — ≈ 60 blocks across every
     block shape (header/scope, criteria, decisions, tables, bold-title items), repeated twice for
     spread. Families (I-28), `C` over-assignment, split failures (I-30, I-42) and cost decide how F5
     retrieval and the M3 views should lean. Found after M4 is coded, they would mean rework.
  3. **One full compile at the M4 gate**, which the build plan already requires (compile the fixture
     and this repository, judge every reported conflict). The judgment lock replays everything the
     gate run already paid for.
  Consider the `anthropic-api` backend (rel01 D30, "later") before that full run: no 22k-token
  harness prompt per call, and it does not draw on the subscription's limits.

### S25 — 2026-09-18 — M2 T12: judgment lock, replay, identity across edits — M2's tasks complete

- **T12 built:** `atomize/lock.py` (per-item judgment lock, replay through the guards, `--no-replay`),
  `atomize/align.py` (unchanged / edited / split / merged / new / removed), wired into `compile`: an
  edited node keeps its id and its judged neighbours go stale; code links are regenerated; nodes cite
  the judgments that formed them. **461 tests green.** ⚑ F3 D21, D22.
- **Live, on a copy of `vision.md` (31 blocks):**

| Run | Calls | Cost | Replayed | Result |
|---|---|---|---|---|
| A1 first compile | 37 | $0.76 | 8 (within the run) | 25 completed, 6 failed, 42 nodes |
| A2 same sources | 10 | $0.12 | 28 | retried the 6 failed; 1 completed |
| B rebuild: A's sources + lock, fresh store | 11 | $0.19 | 127 | every block completed in A rebuilt with identical content; calls only for A's failed blocks (I-41) |
| B + one-word edit | 7 | $0.08 | 23 | aligned — first as `unchanged` with stale text (bug I-40), fixed |
| B + second edit | 9 | $0.11 | 22 | `edited`, id kept, text current; store checks clean |

  ⚠ 4 blocks fail on every run, all "bold title + explanation" list items (I-42) — an M2-gate decision.
- **M2's build tasks are complete (T6 … T12).** Next: the M2 gate.

### S24 — 2026-09-18 — F3 D20 decided; M2 T11: the graph store, and `sddc compile` end to end

- **F3 Q7 → D20** (owner, option b): a Q-TERM `same` merges at once as an alias, undoable by review.
- **T11 built:** `store/graph.py` — family shards (`nodes/`, `edges/`), `terms.jsonl`,
  `conflicts.jsonl`, the derived registry, `review.jsonl`, `graph.meta.json` with id counters, the F2
  §4.9 deletion cascade, the eight consistency checks (`check_store`), one transaction; and
  `pipeline.py` — `sddc compile` = ingest → atomize pending → delete, merge, write, in one
  transaction under the lock. Items close themselves (F3 §4.9); calls and cost are reported.
  `sddc ingest` shipped (B2 amended). **438 tests green.** ⚑ F2 D14, F4 D8, D9.
- **Live smoke run** (`sddc init`, then `sddc compile` twice, on a copy of `vision.md`): run 1 — 31 blocks,
  7 min 11 s, 26 atomized, 5 failed, 43 nodes; run 2 — re-tried exactly the 5 failed blocks (F1 D13 at
  work), 4 completed, 10 more nodes. Final store: 53 nodes, 99 terms, 20 families, **all eight checks
  clean**. Cost not recorded (I-37, now fixed).

### S23 — 2026-09-18 — F2 D12, D13 decided; M2 T10: node forming

- **F2 Q4 → D12** (`label` on every node of a labelled block) and **F2 Q3 → D13** (code fills
  `scope_selector` and `verifies`; AC-2.24, AC-2.25); Q-PAIR relations deferred as **rel01 D31**.
  Retrospective entry I-26: a contract field with readers but no producer.
- **T10 built:** `atomize/pipeline.py` (chunks of 20, every model step per chunk, block all-or-nothing,
  the split re-ask, call cap keeps finished chunks), `forming.py` (CT-2.1 records, scope selector,
  `verifies` by citation, layer hints), `terms.py` (registry, Q-TERM only for similar names, term
  hygiene). Backend: no stdin wait, readable 429s. ⚑ F3 D15 … D19. **F3 Q7 → D20** (owner, option b):
  a Q-TERM `same` merges at once as an alias, undoable by review. **417 tests green.**
- **Live, full pipeline on 32 mixed blocks** (10 F1 header/scope, 12 F1 criteria, 10 F3 decisions):

| Run | Calls (atom / desc / term) | Cost | Time | Completed | Nodes | Terms (used once) | Family null | Status ambiguous |
|---|---|---|---|---|---|---|---|---|
| 1 | 7 / 14 / 2 | $0.82 | 452 s | 30 of 32 | 49 | 142 (119) | 16 | 31 |
| 2, term hygiene | *(summary lost, I-32)* | — | — | 25 of 32 | 49 | 91 (76) | 22 | 33 |

  Every record passed its contract in both runs. *Extrapolation, to be measured:* ≈ $0.026 and ≈ 14 s
  per block → this repository (733 blocks) ≈ $19 and ≈ 3 hours per full compile.
  ⚠ **For the M2 gate:** families (I-28) are the main risk; then `ambiguous` at ≈ 2/3 of nodes
  (pending_review, unresolved_term, unplaceable), permanent split failures (I-30), and cost.

### S22 — 2026-09-18 — F3 D13, D14 decided; M2 T9: the F2 model

- **F3 Q5 → D13** (G4 grounds against block and headings) and **F3 Q6 → D14** (a requirement without
  modality is formed and flagged `missing_modality`, a new F2 ambiguity kind).
- **T9 built** — `src/sdd_compiler/model/`: fixed layers and the profile's display names and hints
  (AC-2.22), placement with the T3 split (AC-2.1 … 2.5, exhaustive over 128 answer patterns), the family
  rule (AC-2.6 … 2.11), status and conflict fields (AC-2.12 … 2.16), record schemas with the rules a
  schema cannot express (AC-2.14, 2.17, 2.18), ids, human-id adoption and keywords (AC-2.19 … 2.21).
  **371 tests green.** Decisions ⚑ F2 D9 (family rules literally in order), D10 (which human ids are
  adopted); open F2 Q3 (who fills `scope_selector` / `verifies`); Q4 closed as F2 D12 (`label` field).
- ⚠ **Live, on 20 acceptance-criterion blocks of F1** (build-plan §8, I-21 … I-24):

| Run | Q-ATOM calls / cost | Q-DESC calls / cost | Atoms | Q-ATOM fails | `split_required` | family fallback | AC ids kept |
|---|---|---|---|---|---|---|---|
| before the `*` fix | 19 / $0.389 | 2 / $0.064 | 8 | **14 of 20** | 0 of 8 | 1 of 8 | 1 of 18 |
| after, run 1 | — | — | 45 | 0 | 11 | 19 | 3 of 18 |
| after, run 2 | 2 / $0.044 | 11 / $0.307 | 35 | 0 | 5 | 9 | 5 of 18 |

  (Run 1's call counts were cut from the captured output.) Layers in run 2: L1 21, C 5, L4 1, V 1.
  ⚠ For the M2 gate: split rate on Given/When/Then criteria, stray `V` atoms from `→ *unit.*`, and the
  family fallback rate all need a stratified sample and repeated runs before they mean anything.

### S21 — 2026-09-18 — F1 D13 (derived pending), and M2 T8: Q-DESC, G4, G6, quantities

- **F1 Q6 closed as F1 D13 (option c).** The block record stores facts (`removed_run`,
  `atomized_hash`); the run's delta is reported, not stored; pending is derived. This fixes a silent
  drop: blocks left unprocessed by a call-cap exit or a failure would have been marked `unchanged` by
  the next ingest and never atomized. AC-1.31 added. M1 gate re-run: 733 blocks, run 2 byte-identical.
- **F3 Q4 closed as F3 D9** (G2 up to layout).
- **T8 built:** `quantities.py` (AC-3.13), `describe.py` (Q-DESC, G2/G4/G5/G6, AC-3.9 up to the
  description, AC-3.11), `batch.py` (the shared batch-and-re-ask loop, now also used by Q-ATOM),
  `atomizer.thinking`. **174 tests green.**
- ⚠ **Live runs changed the design four times** (build-plan §8, I-13 … I-20): thinking off by default
  (F3 D10), `vague_term` from G6 only (D11), the model told not to quote the section line, and G4's
  source widened (F3 D13). Null modality is flagged, not failed (F3 D14).

| Live run, same 20 blocks of `F1_ingest/spec.md` | Q-ATOM calls / cost | Q-DESC calls / cost | Atoms | Describe failures | `inferred` |
|---|---|---|---|---|---|
| thinking on, Q-DESC batch ≈ 25, then 8 | — | timed out at 120 s | — | — | — |
| thinking off, batch 8, G4 narrow | 4 / $0.106 | 14 / $0.479 | 23 | 6 | 8 of 17 (all context) |
| + "never quote the section", G4 wide | 1 / $0.021 | 9 / $0.259 | 23 | 3 (null modality) | 1 of 20 (false: backticks) |
| + `vague_term` G6-only, inline marks ignored | 1 / $0.023 | 10 / $0.347 | 21 | 1 (correct G2 rejection) | 1 of 20 (**real**: "post-rel01") |

  ⚠ One run per row, and runs vary (I-20). *Extrapolation, to be measured:* this repository's 733
  blocks ≈ 800 atoms → Q-ATOM ≈ $1, **Q-DESC ≈ $12–14 and ≈ 40 minutes**. Q-DESC now dominates cost,
  which strengthens the case for the `anthropic-api` backend (rel01 D30, "later"): no harness prompt
  per call.
  ⚠ Also for the M2 gate: the first `yes` was Q1 (→ `C`) for 9 of 20 atoms. `C` may be over-assigned;
  judge by hand at the gate.

### S20 — 2026-09-18 — M2 T7: batched Q-ATOM and guards G2, G3, G5

- `atomize/qatom.py` and `atomize/guards.py` built test-first against F3 AC-3.6 … AC-3.8, AC-3.10:
  batched question, G5 schema check on the whole answer, G2 anchoring and G3 coverage per block,
  one single-block re-ask naming the failed check. **119 tests green.**
- ⚠ **The first live batch exposed a false alarm in G2.** 20 blocks of `F1_ingest/spec.md`: 7 calls,
  **$0.0147 per block — dearer than one call per block**, 5 blocks failed. Every rejected quote was
  correct prose: the source wraps lines (`\n`) and, in blockquotes, repeats `> ` on each line, where
  the model writes a space. The error message cut quotes at 60 characters, which hid the cause; it now
  shows 160.
- **Fix, approved as F3 D9 (Q4 option a):** G2 matches *up to layout* — whitespace runs and continuation `>`
  markers — and still maps to true source offsets. Changed words, case, punctuation and paraphrase
  are still rejected (pinned by tests).

| Live run, same 20 blocks | Calls | Cost per block | Atoms | Failed |
|---|---|---|---|---|
| strict G2 | 7 | $0.0147 | 14 | 5 |
| whitespace-tolerant | 2 | $0.0052 | 19 | 1 (blockquote) |
| layout-tolerant | 2 | $0.0071 | 23 | 0 |

  ⚠ One run each. Model output varies between runs (atom counts differ), so these are single data
  points, not averages. Extrapolated to 723 blocks: ≈ $4–5 for Q-ATOM, *to be measured*.

### S19 — 2026-09-18 — M2 T6: the model interface, and the first cost measurement

- `llm/` built test-first against F3 AC-3.1 … AC-3.5: the question and answer envelope, the headless
  Claude Code backend (child marker, key stripped, no `--bare`, version captured once, usage and cost
  recorded), the optional API backend's key handling, the shared `CallBudget`, and the **fake backend**
  every later test uses. The profile now carries F3 CT-3.4's settings. **99 tests green.**
- ✅ **One real Haiku call, to prove the wiring:** Claude Code 2.1.275 split a two-sentence block into
  two atoms with verbatim quotes; usage, cost and duration were all captured.

#### ⚠ Measured: the per-call overhead dominates, and it changes the plan

Three consecutive real calls, each asking about one short block:

| Call | Cost | In | Out | Cache read | Cache write | Time |
|---|---|---|---|---|---|---|
| 1 | $0.0315 | 10 | 443 | 0 | 22,603 | 6.7 s |
| 2 | $0.0113 | 10 | 166 | 16,293 | 6,310 | 3.8 s |
| 3 | $0.0137 | 10 | 643 | 16,293 | 6,314 | 7.0 s |

**Every headless call carries ~22k tokens of Claude Code's own harness prompt**, against a question of
ten tokens. Steady state is ≈ $0.012 and ≈ 5 s per call, almost none of it ours.

Extrapolated to this repository (723 blocks): **≈ $13.60 and ≈ 1 hour for Q-ATOM alone**, before
Q-DESC (one call per atom) or Q-PAIR (one per candidate pair). A full compile would be tens of dollars
and several hours — which would make "run it often" false.

**Three ways out, for the owner to choose (none taken yet):**
1. **Batch** several blocks per call. F3 §4.3 rule 4 already allows it, provided each answer is
   validated separately and a failure re-asks only the failed item. 20 blocks per call turns 723 calls
   into ~36: roughly $0.50 and minutes instead of dollars and hours.
2. **Prefer the `anthropic-api` backend** for bulk work: no harness prompt, so a call costs what the
   question costs. Needs the key and the unbuilt code path.
3. **Both**, with the profile choosing.

⚑ This is exactly the number the G4 outline asked for at the M2 gate (metric M7), arriving earlier than
planned because the backend could be measured before the pipeline exists.

### S18 — 2026-09-18 — M1 T5, and M1 closed

- `ingest/pipeline.py`, `commands.py` and the CLI wiring: `sddc init`, `sddc compile [PATH…]` and
  `sddc status`, under the store lock, in one transaction. **77 tests green.**
- ✅ **M1 gate run on a copy of this repository's `sdd/`:**
  - `compile` → 9 files, **723 blocks**, all new;
  - `compile` again → **0 new, 0 changed, 723 unchanged**;
  - one word edited in F2 → **1 changed, 722 unchanged**, and `status` reports exactly that block
    (`B-000104`, lines 17–19);
  - the whole store is 480 KB for 723 blocks.
- ⚠ **A defect in an approved AC, found by its own test — F1 Q6.** AC-1.8 asks for `blocks.jsonl` to be
  byte-identical between run 1 and run 2, which cannot hold: run 1 marks blocks `new`, run 2 marks them
  `unchanged`. The property it means — the store reaches a **fixed point** — is built and tested. Two
  ways out are written up in F1 §8; (a) rewording needs no code change. **Owner decision needed.**
- ⚑ While raising it: `sources.last_ingest_run` is now stamped only when a file's content changed, so a
  compile that finds nothing leaves the store untouched.
- `--json` is accepted before or after the command, because people reach for it in both places.
- **Next:** M2 T6 — the model interface with the fake backend, the first code that talks to Haiku.

### S17 — 2026-09-18 — M1 T4: identity and change detection

- `ingest/identity.py` built test-first against F1 AC-1.8 … AC-1.12: normalization, hashing, the three
  matching passes (exact → positional → the rest), id allocation, and the record shape of CT-1.1.
  **63 tests green.**
- ✅ **Verified on the real corpus, which is the point of the whole design:**
  - first run over `sdd/specs/`: **732 blocks**, all `new`;
  - second run, nothing edited: **732 unchanged, 0 changed** — the store is stable;
  - one word edited inside F2: **1 changed, 125 unchanged**, and the pending set is that single block.
  Incremental atomization only pays off if an edit stays local, and now it demonstrably does.
- ⚑ **F1 D12 added:** a `removed` record never matches again, so re-adding deleted prose gets a new id.
  Resurrecting an id would make the history ambiguous and silently re-attach old judgments.
- **Next:** T5 — wire `init`, the ingest pipeline and `status` together, with the store transaction and
  lock, closing M1.

### S16 — 2026-09-18 — F1 Q5 closed as D11 (option B)

- Measured first: **3 of 649 list items** in this repository hold a continuation paragraph (0.5%).
- Owner chose option B: record the structural fact. `parent_relation` is now `nested` or
  `continuation`, CT-1.1 gained the field, **AC-1.30** covers it, and the segmenter links continuation
  paragraphs and fences to their item. **49 tests green.**
- Rejected: merging an item with its continuations into one block — their lines are not contiguous when
  a sub-list sits between them, which would break the verbatim-slice property that all 729 blocks
  currently satisfy and that F3's span guard depends on.
- Deliberately deferred: whether the atomizer *uses* the link as context. That is an F3 decision and a
  measurable one (G4 M4), so it is not being guessed now.

### S15 — 2026-09-18 — M1 T3: segmentation

- `ingest/segment.py` built test-first against F1 AC-1.1 … AC-1.7. **46 tests green.**
- ✅ **Verified the "to verify" assumption:** `markdown-it-py` 2.2 reports `token.map` as a 0-based
  half-open line range; the conversion to the spec's 1-based inclusive lines happens in one function.
  The dependency is now in `pyproject.toml`.
- ✅ **Run against this repository's own specs:** 729 blocks (168 paragraphs, 373 list items, 162 table
  rows, 26 code blocks), and every block's `text` was found verbatim in its source file — the property
  F3's span-anchoring guard will rest on.
- ⚠ **Gap found and recorded as F1 Q5, not silently accepted:** a continuation paragraph inside one
  list item becomes a plain paragraph with no parent, because CT-1.1 allows `parent_block` only for
  nested items. A test pins today's behaviour so a change has to be deliberate.
- Front matter is blanked out before parsing, which keeps every line number honest.
- **Next:** T4 identity and diff (AC-1.8 … AC-1.12) — hashing, exact and positional matching, and
  `removed`.

### S14 — 2026-09-18 — M1 T2: store primitives

- Built test-first: `store/jsonl.py` (caller-supplied key order, sorted lines, UTF-8 kept verbatim,
  corrupt lines named with their line number), `store/transaction.py` (stage to `.sddc-tmp` neighbours,
  `os.replace` them together on success, discard on any exception), `store/lock.py` (one writer, 15 s
  wait, exit `4`). **33 tests green.**
- ⚑ **A lock whose holder process is gone is reclaimed**, not honoured. Otherwise one crashed run
  wedges the repository until someone deletes a file by hand — which would teach users to delete locks,
  the one habit that makes the lock useless.
- Determinism is enforced where it is cheapest: the writer refuses a record with an unexpected or a
  missing field, so no field is ever written that nobody validated.
- **Next:** T3 segmentation (F1 AC-1.1 … AC-1.7) — the first real Markdown work, still no model.

### S12 — 2026-09-18 — G4 outline and build plan drafted

- **G4 outline:** five effectiveness questions (finds real conflicts · does not invent · stable ·
  affordable · legible), nine metrics, two corpora (this repo's own specs, plus a planted-conflict
  fixture), and a check that the instrumentation already specified covers them. Two gaps named: no
  record of human adjudication (needs one small command, decide before the first compile) and no
  agent-side read logs (rel01 has no hooks).
- **Build plan:** four releasable milestones — block inventory → the graph exists → the graph is
  readable → conflicts reported — with 19 tasks mapped to acceptance criteria and code paths, a gate
  after each milestone, the definition of done, and the risks. It asks for three decisions: B1 who owns
  `sddc compile`, B2 which five commands ship, B3 the constitution §4 test tier names.
- **Next:** owner approves both → rel01 D20's gate is satisfied → coding starts at M1 T1.

### S11 — 2026-09-18 — F5 and F6 approved; git remote set up

- D28: all suggested answers in F5 and F6 adopted; both specs 🟢. The rel01 spec set is complete:
  F1–F6, 118 acceptance criteria, F7 design only.
- The repository now has a remote; the release branch is pushed. `main` stays empty until rel01 closes.
- **Remaining gate items (D20):** the G4 outline (D22), then the build plan. Then code.

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

- **rel01 D28 — 2026-09-18 — F5 and F6 approved, with every suggested answer adopted.** F5: starting
  values for the thresholds and weights (F5 D6), `(global)` constraints proposed only against nodes
  sharing a term or keyword (D7), one fixed versioned stop-word list (D8, which also settles F2 Q2 for
  `keywords`). F6: the pair question carries only the two nodes plus their layer and family labels (F6
  D8), one conflict list with contradictions first (D9), `confidence` recorded and flagged but never
  acted on (D10). ⚠ The F5 numbers are **starting values, not measurements**; G4 replaces them.
  Still open elsewhere: F2 Q1, F3 Q1–Q3, F4 Q1–Q2.

- **rel01 D29 — 2026-09-18 — The G4 outline and the build plan are approved; the D20 coding gate is
  satisfied; coding starts at M1 T1.** Build-plan decisions taken as recommended:
  **B1** `sddc compile` orchestration lives in `src/sdd_compiler/pipeline.py`, governed by F3
  (no F8 spec). **B2** rel01 ships five commands — `init · compile · status · conflicts · family`;
  the other ten stay specified but unbuilt, and the close-out must list them. **B3** constitution §4
  adopts the tiers `unit · contract · property · golden · integration`, which the ACs already use.
  Also settled in the constitution §6: Python ≥ 3.11, `src/` layout, setuptools, pytest.

- **rel01 D30 — 2026-09-18 — Cut the per-call overhead by batching now; add the `anthropic-api`
  backend for bulk work later** (S19 option 1 now, option 2 later). Q-ATOM carries a batch of blocks
  per call; each block is validated alone and only a failed block is re-asked, alone, once (F3 §4.3
  rule 4). Measured in S20 on 20 real blocks: 2 calls, $0.0071 per block, against ≈ $0.012 per block
  one call at a time.

- **rel01 D31 — 2026-09-18 — `verifies` and `constrains` as Q-PAIR relations are deferred past rel01**
  (F2 Q3 option c). rel01 fills `scope_selector` and `verifies` by code (F2 D13, option b). After rel01,
  G4 counts how many `C` and `V` nodes that leaves unresolved, and that number decides whether Q-PAIR
  (F6 CT-6.1) gains the two relations.

- **rel01 D32 — 2026-09-18 — M2 gate recommendations R3 … R11 accepted as recommended**
  (`rel01_design/M2-gate.md` §B5): reword Q1 and Q3 without trigger words (R3, R11); the family
  fallback takes the first entity/data/event term anywhere before null (R4, an F2 §4.4 change);
  backticks and a quote's first-letter case are layout (R5, R10, extending F3 D9); non-empty canonical
  subject and response (R7); **an acceptance criterion becomes one `V` node verifying the requirement it
  tests** (R8, an F3 change); Q-ATOM prompt examples for non-claim roles (R9). R1 and R2 pending. The
  spec amendments are written when each is implemented; R6 re-measures the sample afterwards.

- **rel01 D33 — 2026-09-18 — R1 and R2 approved, option (a) each** (`rel01_design/M2-gate.md` §B6,
  which keeps the options and reasons). **R1:** Q-TERM gains the verdict `narrower`; the terms stay
  separate and the new one records `broader`; `same` means synonyms, spellings and plurals only.
  *Rejected:* back to D16 (the ambiguity flood), stricter wording alone (already ignored 9 of 16
  times), a spelling-only code rule (blocks real synonyms). **R2:** each Q-DESC call is shown up to
  ~100 existing term names and asked to reuse one when it names the same thing, with R1's rule (*a kind
  of X is not X*); the list is not part of the lock key. *Rejected for now:* a separate vocabulary pass
  (kept in reserve), code-side clustering (merges distinct things). Success targets for R6: terms used
  once ≤ 50 %, one-node families ≤ half, family null ≤ 10 %, no hyponym merges.

## Rejected alternatives

- **Prompt hooks as the atomizer** — rejected by the documented response schema: a prompt hook
  returns only `ok` / `reason` / `impossible`, not structured node data.

## Open questions

*Tracked in [`../questions.md`](../questions.md): QR-1…QR-10 answered. Spec-level questions live in each spec §8.*
