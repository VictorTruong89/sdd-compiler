---
name: sdd-implement
description: >
  PLACEHOLDER — not yet written. Implement or change code in this repo under its spec-driven
  process: load the constitution and the governing spec, find the acceptance criterion, write a
  failing test, then the smallest code that passes, then fill the traceability table. Use before
  editing anything under src/ or tests/. Until this skill is written, follow CLAUDE.md "The loop"
  and sdd/agent-workflow.md.
---

# Implementing under SDD — PLACEHOLDER

> TODO (rel01): write this skill once `sdd/specs/constitution.md` and the first feature spec exist.

Until then:

1. Read `CLAUDE.md`, `sdd/specs/constitution.md` and the governing spec.
2. Quote the `AC-<n>.<k>` the change satisfies. **If no AC covers it, stop and propose a spec
   amendment instead.**
3. Write the failing test first; confirm it fails for the right reason.
4. Write the smallest code that passes; run the whole suite.
5. Add the traceability row: AC → test → code.
