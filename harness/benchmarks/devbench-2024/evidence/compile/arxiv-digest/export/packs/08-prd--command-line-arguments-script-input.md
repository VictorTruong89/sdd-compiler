# Pack 08 — sdd/specs/PRD.md · Requirements › Command Line Arguments (Script input)
blocks 7 · nodes 4 (requirement 4) · AC labels: none

## Text
# Requirements

## Command Line Arguments (Script input)

- category (str, optional): Category of the paper.
↳ no node

- title (str, optional): Keyword for the title.
↳ no node

- author (str, optional): Keyword for the author.
↳ no node

- abstract (str, optional): Keyword in the abstract.
↳ N-000029 requirement · MAY · L1

- recent_days (int, required): Filter papers from the most recent k days.
↳ N-000030 requirement · MUST · L1

- to_file (str, optional): Path to save the results in CSV format.
↳ N-000031 requirement · MAY · L1

- verbose (Boolean, optional): Flag to print results to the console.
↳ N-000032 requirement · MAY · L1

## Claims to implement
- [N-000029] requirement · MAY · L1 — abstract (str, optional): Keyword in the abstract.
  needs: none
- [N-000030] requirement · MUST · L1 — recent_days (int, required): Filter papers from the most recent k days.
  needs: none
- [N-000031] requirement · MAY · L1 — to_file (str, optional): Path to save the results in CSV format.
  needs: none
- [N-000032] requirement · MAY · L1 — verbose (Boolean, optional): Flag to print results to the console.
  needs: none

## Acceptance criteria
None.

## Constraints in scope
- [N-000019] (pack 05) The tool will be developed in Python, utilizing necessary libraries for API interaction, XML data parsing, and command-line argument parsing.
- [N-000027] (pack 07) All arguments should be constructed with only characters from `"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+:."

## Related elsewhere
- N-000010 duplicates N-000030 (pack 04) The `check_date` function is written to filter the results based on the recent_days parameter, ensuring only papers from the specified recent period are included.
- N-000011 duplicates N-000032 (pack 04) Console Output for immediate viewing, controlled by --verbose.
- N-000012 duplicates N-000031 (pack 04) CSV Export option controlled by --to_file.
- N-000013 subsumes N-000032 (pack 04)
- N-000030 refines N-000001 (pack 02)
- N-000030 refines N-000006 (pack 04)
- N-000030 same as N-000010 (pack 04) The `check_date` function is written to filter the results based on the recent_days parameter, ensuring only papers from the specified recent period are included.
- N-000031 refines N-000002 (pack 03)
- N-000031 same as N-000012 (pack 04) CSV Export option controlled by --to_file.
- N-000032 covered by N-000013 (pack 04) If both specified, print to console and save to csv; else if only --to_file, only save to csv; otherwise (either only --verbose or neither specified), print to console
- N-000032 refines N-000002 (pack 03)
- N-000032 same as N-000011 (pack 04) Console Output for immediate viewing, controlled by --verbose.
- N-000051 refines N-000030 (pack 12)

## Conflicts
None.

## Terms
None.
