# Pack 10 — sdd/specs/PRD.md · Usage › Command Line Configuration Arguments
blocks 9 · nodes 1 (requirement 1) · AC labels: none

## Text
# Usage

## Command Line Configuration Arguments

The following are the command line arguments that users can specify with `lice`:
↳ no node

- `license`: The type of license to generate.
↳ no node

- `-o`, `--org ORGANIZATION`: The organization under which the license is registered.
↳ no node

- `-p`, `--proj PROJECT`: The project name for which the license is generated.
↳ no node

- `-t`, `--template TEMPLATE_PATH`: The path to a custom license template file.
↳ no node

- `-y`, `--year YEAR`: The copyright year to be listed in the license.
↳ no node

- `-l`, `--language LANGUAGE`: The language for which the license header should be formatted.
↳ no node

- `-f`, `--file OFILE`: The output file name where the license should be saved.
↳ no node

- `--vars`: Option to list all template variables for the specified license.
↳ N-000030 requirement · MUST · L1

## Claims to implement
- [N-000030] requirement · MUST · L1 — Option to list all template variables for the specified license.
  needs: none

## Acceptance criteria
None.

## Constraints in scope
plus the broad constraints in pack 01

## Related elsewhere
- N-000036 refines N-000030 (pack 11)

## Conflicts
None.

## Terms
- license — defined: "`license`: The type of license to generate."
- template variable — defined: "**Template Variable**: A placeholder in the license template that is replaced with actual data when generating the license file."
