# Pack 08 — sdd/specs/PRD.md · Usage › Command Line Configuration Arguments
blocks 4 · nodes 4 (requirement 4) · AC labels: none

## Text
# Usage

## Command Line Configuration Arguments

 - `--delimiters` (list, optional) - List of string delimiters for parsing CSV files.
↳ N-000031 requirement · MAY · L1

 - `--schema` (JSON object as string, optional) - JSON schema structure for the output JSON.
↳ N-000032 requirement · MAY · L1

 - `csv_filepath` (string, required) - Path to the input CSV file.
↳ N-000033 requirement · MUST · L1

 - `json_filepath` (string, required) - Path to the output JSON file.
↳ N-000034 requirement · MUST · L1

## Claims to implement
- [N-000031] requirement · MAY · L1 — --delimiters` (list, optional) - List of string delimiters for parsing CSV files.
  needs: none
- [N-000032] requirement · MAY · L1 — --schema` (JSON object as string, optional) - JSON schema structure for the output JSON.
  needs: none
- [N-000033] requirement · MUST · L1 — csv_filepath` (string, required) - Path to the input CSV file.
  needs: none
- [N-000034] requirement · MUST · L1 — json_filepath` (string, required) - Path to the output JSON file.
  needs: none

## Acceptance criteria
None.

## Constraints in scope
- [N-000025] (pack 05) utilize built-in libraries for CSV and JSON processing.
plus the broad constraints in pack 01

## Related elsewhere
- N-000031 refines N-000007 (pack 03)
- N-000031 refines N-000013 (pack 03)
- N-000032 refines N-000004 (pack 02)
- N-000033 refines N-000013 (pack 03)
- N-000034 refines N-000013 (pack 03)

## Conflicts
None.

## Terms
None.
