# Pack 12 — sdd/specs/PRD.md · Dependencies
blocks 4 · nodes 3 (constraint 3) · AC labels: none

## Text
# Dependencies

The `lice` tool relies on the following environment settings and external resources:
↳ no node

- Python runtime environment.
↳ N-000037 constraint · MUST · L2

- Access to system environment variables or `git config` for default values.
↳ N-000038 constraint · MUST

- Access to file system for reading custom templates and writing license files.
↳ N-000039 constraint · MUST

## Claims to implement
- [N-000037] constraint · MUST · L2 — Python runtime environment.
  needs: none
- [N-000038] constraint · MUST · — — Access to system environment variables or `git config` for default values.
  needs: none
- [N-000039] constraint · MUST · — — Access to file system for reading custom templates and writing license files.
  needs: none

## Acceptance criteria
None.

## Constraints in scope
plus the broad constraints in pack 01

## Related elsewhere
- N-000009 refines N-000038 (pack 03)
- N-000050 refines N-000038 (pack 16)

## Conflicts
None.

## Terms
None.
