# SDD Compiler — working agreement

> **Status:** PLACEHOLDER skeleton · opened 2026-09-14 · release **rel01** (target: a workable
> product by **2026-09-30**). Sections marked `TODO` are filled as rel01 decisions land.

This repo builds the **SDD Compiler**: a tool that consolidates spec-driven-development specs
into a graph an AI agent can check and query. The repo is itself built **spec-first**. The specs
are the source of truth and the code is downstream of them. If code and spec disagree, one of them
is a bug — say so rather than quietly picking a side.

## Read before you write

- `sdd/specs/vision.md` — what is being built and why. *(TODO — being rewritten for rel01.)*
- `sdd/specs/constitution.md` — non-negotiable rules. *(TODO.)*
- The spec that governs the path you touch — mapping in `sdd/specs/ownership.yaml`. *(TODO.)*
- Working on rel01 scope? `sdd/design/rel01_brainstorm.md`.

## Layout

| Path | Role | Authority |
|---|---|---|
| `sdd/specs/` | Vision, constitution, one spec per feature | **Authoritative** |
| `sdd/design/` | Release brainstorm and design notes | Non-authoritative, release-scoped |
| `sdd/blueprints/` | What the built code does and why | Permanent, per module |
| `sdd/archive/` | Superseded documents, frozen | Historical |
| `sdd/questions.md` | Question register: decisions and rejected options | Reasoning, never rules |
| `docs/lectures/` | **HTML lectures** for the owner's understanding | Never binding |
| `src/`, `tests/` | Code and tests *(TODO — stack decided in rel01 S1)* | Downstream of specs |
| `chat_history/` | Raw brainstorm exports from before rel01 | Reference only |

## Document conventions

- **Lectures** (explanation, alternatives, background) are **HTML** in `docs/lectures/`.
- **Working design, specs, decisions** — anything humans and AI build from — are **Markdown**.
- If a lecture and a Markdown file disagree, **the Markdown wins**.

## The loop

1. **Diverge** — brainstorm in `sdd/design/rel01_brainstorm.md`.
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

- Never `git commit` or push without the owner's review.
- Never hardcode a credential; read from the environment.
- Fail loud, never silent.

## Enforcement

*(TODO — a spec-read gate hook like the one in `collective-investment-ai-assistant` may be added.
None is active yet; see `.claude/settings.json`.)*
