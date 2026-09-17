# Project Vision — SDD Compiler

> **Status:** Draft · being built step by step · **Opened:** 2026-09-13 · **Last revised:** 2026-09-13
> **Tier:** authoritative once adopted, **release-independent**.
> **Audience:** the human authors and the AI agents who propose, design or review work on the SDD
> Compiler, and any later reader who needs the goal without reading the brainstorm history.
> **Sources:** `sdd/archive/chat_history/Spec-Compiler-SDD-chat-export-1789156135574.json` (generic discussion)
> and `sdd/archive/chat_history/sdd-compiler-design.html` (design tied to one project).
> Neither is binding. This file supersedes them wherever they disagree.

---

# 1. Ultimate purposes

Recorded as decided. **Technical refinement comes later** (§4). A release marker is shown only where it
has been decided. "Not yet decided" means exactly that.

| # | Purpose | Clarification | Release |
|---|---|---|---|
| **U1** | **Generic.** Supports any spec-driven project, not only `collective-investment-ai-assistant/`. | Nothing about one repository's layout, vocabulary or governance is hard-coded. Project-specific conventions are configuration. | **First release** |
| **U2** | **Consolidate new spec creation.** | New specs are consolidated into the existing spec set, surfacing duplication, overlap, conflict and ambiguity. | **First release** |
| **U3** | **Consolidate agent-discovered spec conflicts and missing specs.** When an AI agent finds a spec conflict, or finds that a new spec is required, the SDD Compiler consolidates that too. | The SDD Compiler **reports and waits** for a response. The responder is either (a) a human, or (b) the AI agent that generates the specs, reached through that agent's API. Claude Code is the first agent supported; other agent APIs may follow. | **Future release**, not the first |
| **U4** | **Version the full spec set.** | The whole spec set is versioned. Identity and relationships of spec units survive across versions. | Not yet decided |
| **U5** | **Compare pre-built vs. as-built spec graphs.** | **Out of scope:** *producing* as-built specs. A separate AI agent or a human writes them, possibly using the pre-built spec graph as input. **In scope:** *comparing* the as-built spec graph against the pre-built spec graph. | **First release** |
| **U6** | **Future optimization of the spec graph.** | Deferred by design. Recorded now so early choices don't prevent it. | Future |
| **U7** | **Help AI agents generate code from the spec graph.** | The spec graph is the input an AI agent uses to write code. | Not in first release · the graph design must not preclude it |

---

# 2. Operating model

These are the decisions that shape how the purposes are met.

- **O1 · Deterministic wherever possible — relaxed over releases.**
  - **Release 1:** the SDD Compiler's own code is deterministic. Everything that can be computed
    deterministically is: graph structure, identity, comparison, status bookkeeping. Every language
    judgment is requested from the AI agent as a **small, closed question**. The answer is **checked
    immediately** (schema, verbatim quotes, internal consistency) and recorded.
  - **Future releases** may deploy **local ML models** (for example embedding or small classification
    models) to help build the graph or with other tasks. Their exact role is not yet decided. Any
    such model is pinned to a version, and its outputs are recorded the same way agent judgments are.
- **O2 · Language intelligence belongs to the user's own AI agent (release 1).** Three kinds of work
  are done by the AI agent the user already runs, not by a model embedded in or called by the SDD
  Compiler:
  - converting specs into nodes
  - any other judgment that needs understanding of language
  - rewriting specs
- **O3 · Runs through the agent's hooks and API.** The SDD Compiler integrates with that agent through
  the agent's own extension points. **Claude Code is the first supported agent**, because it is the
  current agent in use. Other agents may follow, so the agent-facing boundary is kept replaceable.

---

# 3. Scope by release

| Topic | First release | Future |
|---|---|---|
| Authorship | **One writer at a time**, human or AI | Several people editing one spec set |
| Ambiguous specs | A node **status value `ambiguous`**. No questions are asked. | Clarifying questions: an interactive loop that generates questions, processes answers and decides |
| Agent feedback loop (U3) | — | Report-and-wait to a human or to the spec-generating agent's API |
| Intelligence | The user's AI agent only, via small checked questions (O1, O2) | Local ML models may assist; role not yet decided |

---

# 4. Deliberately open

Not decided yet. Listed so nothing is silently assumed.

- Technical refinement of U1–U7: what each means mechanically, and how each is measured.
  In progress for the core working principle (atomize → place → link → retrieve):
  working design [`design/core-working-principle.md`](../design/rel01_design/core-working-principle.md), lecture
  [`design/core-working-principle.html`](../../docs/lectures/core-working-principle.html).
- U4 release timing. It is not in the first release, but U5 comparison needs some notion of "which
  graph version" — see the design file.
- Durable non-goals.
- Architecture principles beyond §2.
- Which Claude Code integration points realize O3. Candidates: hooks, MCP tools, headless / Agent
  SDK invocation.
- How O1 holds when a node originates from an agent's non-deterministic output. Proposed in the
  design file: immediate answer checks and a "judgment lock" that records every answer.

---

# 5. Document conventions

| Kind of document | Format | Audience | Binding? |
|---|---|---|---|
| **Lecture** — explains reasoning, alternatives and background for understanding | HTML | The human owner | Never |
| **Working design, specs, decisions** — what humans and AI agents build from | Markdown | Humans and AI agents | Design: proposals until adopted · Specs: yes |

A lecture and its working design may cover the same topic. If they disagree, **the Markdown file
wins** and the lecture is corrected.
