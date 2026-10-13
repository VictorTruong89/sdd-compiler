# SDD Compiler — working agreement

> **Status:** opened 2026-09-14 · release **rel01 CLOSED 2026-10-01**
> ([close-out](sdd/design/releases/rel01_closeout.md)); its brainstorm, design notes and first compile
> are frozen in [`sdd/archive/rel-01/`](sdd/archive/rel-01/README.md). **rel02 is open** (2026-10-11):
> [`sdd/design/rel-02/rel02_brainstorm.md`](sdd/design/rel-02/rel02_brainstorm.md). Sections marked `TODO` are still open.
>
> ★ **rel01 in one sentence (rel01 D26):** point `sddc compile` at a folder of static Markdown spec
> files and get back a spec graph plus a report of every conflict in it. No hooks, no live input, no
> stopping mid-run.

This repo builds the **SDD Compiler**: a tool that consolidates spec-driven-development specs
into a graph an AI agent can check and query. The repo is itself built **spec-first**. The specs
are the source of truth and the code is downstream of them. If code and spec disagree, one of them
is a bug — say so rather than quietly picking a side.

## Read before you write

- `sdd/specs/vision.md` — what is being built and why. **Adopted 2026-09-17.**
- `sdd/specs/constitution.md` — non-negotiable rules.
- The spec that governs the path you touch — mapping in `sdd/specs/ownership.yaml`.
- The open release's brainstorm: `sdd/design/rel-02/rel02_brainstorm.md` (objectives, decisions, open questions).
- Why something was built the way it was in rel01: `sdd/archive/rel-01/` (brainstorm with decisions
  rel01 D1–D42, design notes, build plan and issue log). Frozen; never edit, never build from it.

## Layout

| Path | Role | Authority |
|---|---|---|
| `sdd/specs/` | Vision, constitution, one spec per feature | **Authoritative** |
| `sdd/design/` | Release brainstorm and design notes | Non-authoritative, release-scoped |
| `sdd/blueprints/` | What the built code does and why | Permanent, per module |
| `sdd/archive/` | Superseded documents, frozen | Historical |
| `sdd/archive/rel-01/` | Release 01: brainstorm, design notes, measurements, spec snapshot, `trial_01/` | Historical |
| `sdd/questions.md` | Question register: decisions and rejected options | Reasoning, never rules |
| `docs/lectures/` | **HTML lectures** for the owner's understanding | Never binding |
| `src/`, `tests/` | Python CLI code and tests (stack: constitution §6) | Downstream of specs |
| `harness/` | Runs a coding agent on a task in a sandbox and scores it; outside the compiler (F7 D9) | No governing spec yet |
| `sdd/archive/chat_history/` | Raw brainstorm exports and course brief from before rel01 | Historical |

## Document conventions

- **Lectures** (explanation, alternatives, background) are **HTML** in `docs/lectures/`.
- **Working design, specs, decisions** — anything humans and AI build from — are **Markdown**.
- If a lecture and a Markdown file disagree, **the Markdown wins**.

## The loop

1. **Diverge** — brainstorm in `sdd/design/rel-02/rel02_brainstorm.md`.
2. **Converge** — record the decision in that file's decisions log.
3. **Graduate** — copy `sdd/specs/_templates/spec.md` → `sdd/specs/F<n>_<slug>/spec.md` once its
   acceptance criteria can be written.
4. **Wire** — add the spec's code globs to `sdd/specs/ownership.yaml`.
5. **Implement** — failing test per `AC-<n>.<k>` first, then the smallest code that passes. Fill the
   spec's traceability table. Skill: `sdd-implement`.
6. **Verify** — run the whole test suite.

## Evidence rules

- No invented numbers. Quantitative claims are measured or marked *to be measured*.
- No unverified citations. A reference is cited only after its primary source has been opened.

## House rules

- **Never run `git commit` or `git push`.** The owner reviews and commits. Staging is also left to the owner.
- Never hardcode a credential; read from the environment.
- Fail loud, never silent.

## Enforcement

*(TODO — a spec-read gate hook like the one in `collective-investment-ai-assistant` may be added.
None is active yet; see `.claude/settings.json`.)*
