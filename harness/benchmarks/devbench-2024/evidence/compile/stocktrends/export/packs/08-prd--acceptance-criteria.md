# Pack 08 — sdd/specs/PRD.md · Acceptance Criteria
blocks 3 · nodes 5 (requirement 3, verification 2) · AC labels: none

## Text
# Acceptance Criteria

The repository should include acceptance testing for both the renko and line break indicator calculation models.
↳ N-000040 requirement · SHOULD · L1

- For the Renko indicator calculation model, the program is required to precisely compute the Renko indicator. This will be evaluated by comparing the closing prices of the Renko chart generated from the input data with the anticipated closing prices. The acceptance test will validate that the absolute difference between the closing prices of the generated Renko chart and the expected closing prices falls within a tolerance threshold of 1e-12.
↳ N-000041 requirement · MUST · L1 ; N-000042 verification · — · V

- For the line break indicator calculation model, the program should correctly calculate the Line Break indicator. This will involve comparing the close prices of the Line Break chart generated from the input data with the expected close prices. The acceptance test will validate that the absolute difference between the close prices of the generated Line Break chart and the expected close prices is less than or equal to 1e-12.
↳ N-000043 requirement · SHOULD · L1 ; N-000044 verification · — · V

## Claims to implement
- [N-000040] requirement · SHOULD · L1 — The repository should include acceptance testing for both the renko and line break indicator calculation models.
  needs: none
- [N-000041] requirement · MUST · L1 — For the Renko indicator calculation model, the program is required to precisely compute the Renko indicator.
  needs: none
- [N-000043] requirement · SHOULD · L1 — For the line break indicator calculation model, the program should correctly calculate the Line Break indicator.
  needs: none

## Acceptance criteria
- [N-000042] This will be evaluated by comparing the closing prices of the Renko chart generated from the input data with the anticipated closing prices. … The acceptance test will validate that the absolute difference between the closing prices of the generated Renko chart and the expected closing prices falls within a tolerance threshold of 1e-12.
  verifies: none
  test name: test_N_000042_…
- [N-000044] This will involve comparing the close prices of the Line Break chart generated from the input data with the expected close prices. … The acceptance test will validate that the absolute difference between the close prices of the generated Line Break chart and the expected close prices is less than or equal to 1e-12.
  verifies: none
  test name: test_N_000044_…

## Constraints in scope
plus the broad constraints in pack 01

## Related elsewhere
- N-000021 refines N-000040 (pack 04)
- N-000042 refines N-000021 (pack 04)
- N-000042 refines N-000031 (pack 04)
- N-000044 refines N-000010 (pack 03)
- N-000044 refines N-000021 (pack 04)
- N-000044 refines N-000031 (pack 04)

## Conflicts
None.

## Terms
None.
