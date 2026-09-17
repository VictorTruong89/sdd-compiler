# Project Vision — SDD Compiler

> **Status:** Living · **Adopted:** 2026-09-17 · **Tier:** authoritative, release-independent.
> **Read this first.** [`constitution.md`](constitution.md) says *how* to build; this says *what* is
> being built and *why*.
> **Audience:** the owner, and any AI agent proposing, designing or reviewing work here.
> **Previous vision:** scrapped 2026-09-14, frozen at
> [`../archive/2026-09-13_vision_pre-rel01.md`](../archive/2026-09-13_vision_pre-rel01.md). Nothing in
> it binds unless re-adopted here.

---

# 1. What this project is

**A compiler for specifications: it turns a set of Markdown spec files into a checked graph of
atomic specs, and reports where those specs contradict, duplicate or under-specify each other.**

Spec-driven development lets people describe a system in ordinary language, which is its whole
advantage and the source of its problem: English has no type checker. Two specs written weeks apart
can contradict each other and nothing notices. The larger the spec set, the less likely a human — or
an AI agent reading it — will notice either.

The SDD Compiler reads the prose, breaks it into atomic claims, places each one in a layered graph,
and checks the claims against each other. **The prose stays the source of truth; the graph is a build
artifact**, the way object files are downstream of source code.

# 2. Purposes, in order

| # | Purpose | Measured by |
|---|---|---|
| **1** | **Make a spec set checkable.** Find the contradictions, duplicates and ambiguities a human reading cannot reliably find. | Conflicts found in a real spec set that a human review had missed, and the false ones it raises |
| **2** | **Make a spec set usable by an AI coding agent.** Give an agent the few specs that govern the change it is making, instead of a folder to read. | Whether an agent's output honours the specs it was given — designed later (rel01 G4) |

Purpose 1 comes first: an agent cannot be helped by a spec set nobody has checked.

# 3. Operating principles

- **O1 · The prose is the source of truth.** The graph is compiled from Markdown files and can always
  be rebuilt from them. Nobody edits the graph by hand.
- **O2 · The compiler's code is deterministic.** Structure, identity, placement, storage, comparison
  and status bookkeeping are plain code. Given the same inputs and the same recorded judgments, a
  build produces identical bytes.
- **O3 · Language judgment belongs to a model, in small closed questions.** The model answers narrow,
  schema-bound questions — "what claims are in this paragraph?", "do these two contradict?" — never
  open ones. Every answer is checked by code before it is accepted, and recorded so a rebuild replays
  it instead of asking again.
- **O4 · Fail loud, and never invent.** A model answer that cannot be anchored in the source is
  refused or flagged, never silently kept. Every conflict carries its quotes and its reasoning.
- **O5 · Two forms of one graph.** A collapsed form for humans and a full-detail form for AI agents,
  both derived from the same records, so they cannot disagree.

# 4. Scope by release

| Topic | **rel01** (target 2026-09-30) | Later |
|---|---|---|
| Input | **Several static Markdown spec files**, compiled in one batch run. Hardest shape supported: a spec tree like this repository's own `sdd/` | Live specs typed at the CLI; specs written during an AI session |
| Trigger | One command, run by a person | Editor and agent hooks; compile on save |
| Conflicts | Detected across the whole set, **recorded and reported together at the end of the run** | Immediate feedback while specs are being written; an agent that fixes its own conflict before continuing |
| Model | Haiku through headless Claude Code (default) or the Anthropic API | Local models as assistants |
| Output | The graph, a conflict report, and generated human views | Context packs for code generation; an interactive viewer |
| Code generation | Designed, not built | Built |
| Versioning, multi-author, design-vs-as-built comparison | Out | In |

**rel01 in one sentence:** *point it at a folder of spec files, and get back a graph plus a list of
every conflict in it.*

# 5. Durable non-goals

- **No new specification language.** Authors keep writing ordinary Markdown. Structure is inferred,
  never demanded.
- **No editing of specs by the compiler.** It reports; people and their agents decide and rewrite.
- **No arithmetic or bookkeeping inside a model prompt.** Offsets, quantities, counts and statuses
  are computed by code.
- **No hidden model output.** Nothing enters the graph without a quote from the source.
- **No graph as source of truth.** If the graph and the prose disagree, the prose wins and the graph
  is rebuilt.

# 6. Document conventions

| Kind | Format | Binding? |
|---|---|---|
| Lecture — explanation, alternatives, background | HTML in `docs/lectures/` | Never |
| Working design, specs, decisions | Markdown | Specs: yes · design: once adopted |

If a lecture and a Markdown file disagree, **the Markdown wins**.

# 7. How to use this file

- **Proposing or designing?** Start here, then `../design/rel01_brainstorm.md`. Work that serves no
  purpose in §2, or contradicts §3 or §5, is out of scope — say so rather than building it.
- **Implementing?** This file binds nothing directly. Go to [`constitution.md`](constitution.md) and
  the governing spec.
- **Amending?** The purposes (§2), principles (§3) and non-goals (§5) change only when the owner says
  so, and the change lands here first. The release scope (§4) is expected to churn.
