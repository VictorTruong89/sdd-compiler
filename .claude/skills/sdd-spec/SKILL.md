---
name: sdd-spec
description: >
  PLACEHOLDER — not yet written. Graduate a decided idea from sdd/design/rel01_brainstorm.md into a
  feature spec under sdd/specs/F<n>_<slug>/spec.md, with acceptance criteria, contracts, decisions
  and a traceability table. Use when a brainstorm decision is ready to become a spec, or when a spec
  must be amended before implementation.
---

# Writing or amending a spec — PLACEHOLDER

> TODO (rel01): write this skill after the spec template has been used once for real.

Until then:

1. Confirm the decision is recorded in `sdd/design/rel01_brainstorm.md` with rejected options.
2. Claim the next free `F<n>` in `sdd/specs/README.md`. Never renumber.
3. Copy `sdd/specs/_templates/spec.md`; fill every section. Every behaviour gets an `AC-<n>.<k>`.
4. Add code globs to `sdd/specs/ownership.yaml` in the same change.
5. Record open questions in the spec §8 and in `sdd/questions.md`.
