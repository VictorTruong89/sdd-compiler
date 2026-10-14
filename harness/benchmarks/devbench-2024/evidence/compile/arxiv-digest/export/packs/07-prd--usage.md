# Pack 07 — sdd/specs/PRD.md · Requirements › Usage
blocks 3 · nodes 5 (constraint 1, requirement 4) · AC labels: none

## Text
# Requirements

## Usage

To execute a query, run the following script:
↳ no node

```bash
python query_arxiv.py 
--category [category] 
--title [title] 
--author [author] 
--abstract [abstract]
--recent_days [number_of_days]
[--to_file path_to_csv_file]
[--verbose]
```
↳ N-000024 requirement · MUST · L1

At least one of the query parameters `[category, title, author, abstract]` must be provided, along with the mandatory `--recent_days` parameter. All arguments should be constructed with only characters from `"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+:."`; otherwise, a `ValueError` will be raised.
↳ N-000025 requirement · MUST · L1 ; N-000026 requirement · MUST · L1 ; N-000027 constraint · SHOULD · C ; N-000028 requirement · MUST · L1

## Claims to implement
- [N-000024] requirement · MUST · L1 — python query_arxiv.py 
    --category [category] 
    --title [title] 
    --author [author] 
    --abstract [abstract]
    --recent_days [number_of_days]
    [--to_file path_to_csv_file]
    [--verbose]
  needs: none
- [N-000025] requirement · MUST · L1 — At least one of the query parameters `[category, title, author, abstract]` must be provided
  needs: none
- [N-000026] requirement · MUST · L1 — along with the mandatory `--recent_days` parameter
  needs: N-000030 (pack 08)
- [N-000027] constraint · SHOULD · C — All arguments should be constructed with only characters from `"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+:."
  needs: none
- [N-000028] requirement · MUST · L1 — otherwise, a `ValueError` will be raised.
  needs: N-000025

## Acceptance criteria
None.

## Constraints in scope
- [N-000019] (pack 05) The tool will be developed in Python, utilizing necessary libraries for API interaction, XML data parsing, and command-line argument parsing.

## Related elsewhere
- N-000004 duplicates N-000025 (pack 04) But at least one of them should be specified
- N-000006 duplicates N-000026 (pack 04) Integrates a mandatory `recent_days` parameter,
- N-000025 same as N-000004 (pack 04) But at least one of them should be specified
- N-000026 refines N-000001 (pack 02)
- N-000026 same as N-000006 (pack 04) Integrates a mandatory `recent_days` parameter,
- N-000044 refines N-000024 (pack 12)

## Conflicts
None.

## Terms
- query arxiv — defined: "Query ArXiv is a tool designed to streamline the process of fetching research papers from the ArXiv database."
