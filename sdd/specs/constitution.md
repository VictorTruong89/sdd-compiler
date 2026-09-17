# Constitution — how the SDD Compiler is built

> **Status:** PLACEHOLDER · opened 2026-09-14 · authoritative once adopted.
> A spec may add constraints; it may never contradict this file. Change it first, in its own change.

## 1. ID families

> Every id family in use is declared here **before** it is used. An undeclared family is a defect.
> Declared 2026-09-15 (rel01 S7).

| Family | Meaning | Scope | Defined in |
|---|---|---|---|
| `F<n>` | Feature spec | Repository | `specs/README.md` |
| `AC-<n>.<k>` | Acceptance criterion of spec F<n> | Spec | Spec §6 |
| `CT-<n>.<k>` | Contract of spec F<n> | Spec | Spec §5 |
| `D<n>` | Decision inside one spec | Spec | Spec §7 |
| `Q<n>` | Open question inside one spec | Spec | Spec §8 |
| `T<n>` | Trigger inside one spec | Spec | Spec §3 |
| `rel<NN> D<n>` · `rel<NN> S<n>` | Release decision · release session | Release | `design/rel<NN>_brainstorm.md` |
| `QR-<n>` | Question register entry | Repository | `questions.md` |
| `G<n>` · `G<n>.<k>` | Release goal · sub-goal | Release | `design/rel<NN>_brainstorm.md` |
| `P-<n>` | Pre-rel01 design proposal | Historical | `design/rel01_design/core-working-principle.md` |
| `B-<digits>` · `R-<digits>` | Block · run (runtime records) | `.sdd/` store | F1 |
| `N-<digits>` · `term:<name>` · `CF-<digits>` | Node · term · conflict record | `.sdd/` store | F2 |
| `J-<digits>` · `RV-<digits>` | Judgment · review item | `.sdd/` store | F3 |

**Collision rule:** within one scope, two things may never share an id. Store ids are assigned once and
never reused.

## 2. Principles

*TODO.*

## 3. Invariants

*TODO — rules checked by tests or tooling, each with an id.*

## 4. Test tiers

*TODO — every AC maps to exactly one tier (for example unit · contract · property · golden ·
integration · end-to-end).*

## 5. Change process

*TODO — how a spec is amended, how an AC is added, what "done" means.*

## 6. Stack and environment

> **Adopted:** rel01 D3 (2026-09-14). Details marked TODO are decided when F1 is specified.

- **Language:** Python, packaged as a command-line tool named **`sddc`** (package `sdd_compiler`, store `.sdd/`; rel01 D21). *(TODO: minimum Python version, packaging
  tool, test runner.)*
- **Model access:** Claude Code with **Haiku**:
  - **command hooks** trigger the CLI;
  - **headless Claude Code** (`claude -p`) runs structured judgments;
  - **prompt hooks** are used only for yes/no gates.
  
  Model calls go through **one interface with two backends** (rel01 D7): headless Claude Code
  (default) and the Anthropic API (optional; keys only in the git-ignored `.env`, never in the child
  environment of the headless backend).
- **Not in rel01:** VS Code extension, MCP server, local ML models, graph database.
- **Commits:** never made automatically by an agent; the owner commits after review (rel01 D6).
