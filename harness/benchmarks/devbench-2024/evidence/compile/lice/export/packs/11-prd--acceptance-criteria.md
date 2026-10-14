# Pack 11 — sdd/specs/PRD.md · Acceptance Criteria
blocks 7 · nodes 6 (requirement 6) · AC labels: none

## Text
# Acceptance Criteria

To validate the correct implementation of the command-line interface:
↳ no node

- All commands must execute without errors when the correct syntax is used.
↳ N-000031 requirement · MUST · L1

- The tool must correctly generate the license text for each specified license type.
↳ N-000032 requirement · MUST · L1

- Custom organization and project names must be accurately reflected in the generated license file.
↳ N-000033 requirement · MUST · L1

- When a custom template path is provided, the license generated must match the custom template.
↳ N-000034 requirement · MUST · L1

- The tool must accurately format licenses according to the specified programming language syntax.
↳ N-000035 requirement · MUST · L1

- The `--vars` option must list all the correct template variables for the specified license type.
↳ N-000036 requirement · MUST · L1

## Claims to implement
- [N-000031] requirement · MUST · L1 — All commands must execute without errors when the correct syntax is used.
  needs: none
- [N-000032] requirement · MUST · L1 — The tool must correctly generate the license text for each specified license type.
  needs: none
- [N-000033] requirement · MUST · L1 — Custom organization and project names must be accurately reflected in the generated license file.
  needs: N-000008 (pack 03)
- [N-000034] requirement · MUST · L1 — When a custom template path is provided, the license generated must match the custom template.
  needs: none
- [N-000035] requirement · MUST · L1 — The tool must accurately format licenses according to the specified programming language syntax.
  needs: none
- [N-000036] requirement · MUST · L1 — The `--vars` option must list all the correct template variables for the specified license type.
  needs: none

## Acceptance criteria
None.

## Constraints in scope
plus the broad constraints in pack 01

## Related elsewhere
- N-000029 refines N-000032 (pack 09)
- N-000033 refines N-000051 (pack 16)
- N-000036 refines N-000030 (pack 10)
- N-000052 refines N-000035 (pack 16)

## Conflicts
None.

## Terms
- license — defined: "`license`: The type of license to generate."
- template variable — defined: "**Template Variable**: A placeholder in the license template that is replaced with actual data when generating the license file."
