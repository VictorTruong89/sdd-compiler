# Pack 14 — sdd/specs/architecture_design.md · Architecture Design › Outputs:
blocks 4 · nodes 2 (assumption 2) · AC labels: none

## Text
# Architecture Design

## Outputs:

The examples directory contains CSV and JSON files which represent the input and output data for the CSV to JSON conversion process:
↳ no node

- `example_a/b/c.csv`: CSV files used as input for conversion.
↳ N-000043 assumption · — · L1

- `example_a/b/c.json`: JSON files produced by the conversion process.
↳ N-000044 assumption · — · L1

These example files are used to demonstrate the functionality of the Hone tool.
↳ no node

## Claims to implement
- [N-000043] assumption · — · L1 — example_a/b/c.csv`: CSV files used as input for conversion.
  needs: none
- [N-000044] assumption · — · L1 — example_a/b/c.json`: JSON files produced by the conversion process.
  needs: none

## Acceptance criteria
None.

## Constraints in scope
- [N-000025] (pack 05) utilize built-in libraries for CSV and JSON processing.
plus the broad constraints in pack 01

## Related elsewhere
None.

## Conflicts
None.

## Terms
None.
