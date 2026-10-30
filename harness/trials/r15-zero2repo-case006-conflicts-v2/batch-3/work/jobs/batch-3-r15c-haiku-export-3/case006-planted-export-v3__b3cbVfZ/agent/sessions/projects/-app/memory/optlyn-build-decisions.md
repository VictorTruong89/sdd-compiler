---
name: optlyn-build-decisions
description: "Status and spec-conflict decisions for the Optlyn (Click-like CLI library) build in /app; read before changing deprecation output, confirm, env/default-map precedence, or runner cleanup."
metadata:
  node_type: memory
  type: project
  originSessionId: f4d17488-8ccf-4be3-9f39-6f9186950e8f
  modified: 2026-10-28T14:25:58.222Z
---

Optlyn is built in /app/src/optlyn (tests: /app/tests/test_optlyn.py, 112 passing; run with PYTHONPATH=src). The full spec is in /app/spec and must not be edited. The six unsettled spec contradictions (CF-000146/150/151/152/153/155) were resolved and recorded in /app/NOTES.md, with the checklist status by pack range.

**Why:** the spec was exported with `--allow-open` and has conflicting claims; the hidden tests will decide, so the choices need to be easy to find and change.

**How to apply:** if asked to revisit a conflict, edit the module named in NOTES.md's table rather than the spec. Keep the NOTES.md conflict table in step with any change. Known gap: Windows argv expansion is not implemented (Linux target).
