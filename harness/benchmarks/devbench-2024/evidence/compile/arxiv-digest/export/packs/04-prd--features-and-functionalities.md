# Pack 04 — sdd/specs/PRD.md · Features and Functionalities
blocks 27 · nodes 16 (assumption 1, constraint 2, requirement 13) · AC labels: none

## Text
# Features and Functionalities

- Advanced Query Options:
↳ no node

    - Enables querying by any combinations of `category`, `author`, `title`, and `abstract`. But at least one of them should be specified
↳ N-000003 requirement · MAY · L1 ; N-000004 constraint · SHOULD · L1

    - `max_results` parameter to control the number of results, with a sensible default (recommanded: 10).
↳ N-000005 requirement · MUST · L1

- Time-based Filtering:
↳ no node

    - Integrates a mandatory `recent_days` parameter, not directly supported by ArXiv. This feature requires custom implementation:
↳ N-000006 requirement · MUST · L1 ; N-000007 assumption · — ; N-000008 constraint · MUST · L5

        - **Query URL Construction:** Queries are structured with sortBy=submittedDate and sortOrder=descending to fetch recent papers first.
↳ N-000009 requirement · MUST · L5

        - **Example Query URL:**
↳ no node

        ```
        http://export.arxiv.org/api/query?search_query=cat:cs.CL+AND+au:Smith+AND+ti:neural+AND+abs:learning&sortBy=submittedDate&sortOrder=descending&start=0&max_results=10
        ```
↳ no node

        - **Custom Date Check:** The `check_date` function is written to filter the results based on the recent_days parameter, ensuring only papers from the specified recent period are included.
↳ N-000010 requirement · MUST · L5

- Output Handling:
↳ no node

    - Console Output for immediate viewing, controlled by --verbose.
↳ N-000011 requirement · MUST · L1

    - CSV Export option controlled by --to_file.
↳ N-000012 requirement · MUST · L1

    - If both specified, print to console and save to csv; else if only --to_file, only save to csv; otherwise (either only --verbose or neither specified), print to console
↳ N-000013 requirement · MUST · L1

- User Input Processing:
↳ no node

    - Command-line arguments for search parameters and output preferences.
↳ N-000014 requirement · MUST · L1

- Data Retrieval and Processing:
↳ no node

    - Efficient API interactions and XML data parsing according to user criteria.
↳ N-000015 requirement · MUST · L1

- Result Filtering and Formatting:
↳ no node

    - Applies date filtering via check_date.
↳ N-000016 requirement · MUST · L5

    - Coherent presentation of key details in both console and CSV.
↳ N-000017 requirement · MUST · L1

        - Both console output and CSV columns should include at least the following inforamtion:
↳ N-000018 requirement · SHOULD · L1

            - `category`
↳ no node

            - `title`
↳ no node

            - `author`
↳ no node

            - `abstract`
↳ no node

            - `published`: publication date
↳ no node

            - `link`
↳ no node

## Claims to implement
- [N-000003] requirement · MAY · L1 — Enables querying by any combinations of `category`, `author`, `title`, and `abstract`.
  needs: none
- [N-000004] constraint · SHOULD · L1 — But at least one of them should be specified
  needs: none
- [N-000005] requirement · MUST · L1 — max_results` parameter to control the number of results, with a sensible default (recommanded: 10).
  needs: none
- [N-000006] requirement · MUST · L1 — Integrates a mandatory `recent_days` parameter,
  needs: none
- [N-000007] assumption · — · — — not directly supported by ArXiv.
  needs: none
- [N-000008] constraint · MUST · L5 — This feature requires custom implementation:
  needs: N-000007
- [N-000009] requirement · MUST · L5 — Queries are structured with sortBy=submittedDate and sortOrder=descending to fetch recent papers first.
  needs: none
- [N-000010] requirement · MUST · L5 — The `check_date` function is written to filter the results based on the recent_days parameter, ensuring only papers from the specified recent period are included.
  needs: none
- [N-000011] requirement · MUST · L1 — Console Output for immediate viewing, controlled by --verbose.
  needs: none
- [N-000012] requirement · MUST · L1 — CSV Export option controlled by --to_file.
  needs: none
- [N-000013] requirement · MUST · L1 — If both specified, print to console and save to csv; else if only --to_file, only save to csv; otherwise (either only --verbose or neither specified), print to console
  needs: none
- [N-000014] requirement · MUST · L1 — Command-line arguments for search parameters and output preferences.
  needs: none
- [N-000015] requirement · MUST · L1 — Efficient API interactions and XML data parsing according to user criteria.
  needs: none
- [N-000016] requirement · MUST · L5 — Applies date filtering via check_date.
  needs: N-000037 (pack 01)
- [N-000017] requirement · MUST · L1 — Coherent presentation of key details in both console and CSV.
  needs: N-000002 (pack 03)
- [N-000018] requirement · SHOULD · L1 — Both console output and CSV columns should include at least the following inforamtion:
  needs: N-000002 (pack 03)

## Acceptance criteria
None.

## Constraints in scope
- [N-000019] (pack 05) The tool will be developed in Python, utilizing necessary libraries for API interaction, XML data parsing, and command-line argument parsing.
- [N-000020] (pack 05) Compliance with ArXiv API usage guidelines and rate limits is required.
- [N-000027] (pack 07) All arguments should be constructed with only characters from `"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+:."

## Related elsewhere
- N-000003 refines N-000001 (pack 02)
- N-000004 duplicates N-000025 (pack 07) At least one of the query parameters `[category, title, author, abstract]` must be provided
- N-000004 same as N-000025 (pack 07) At least one of the query parameters `[category, title, author, abstract]` must be provided
- N-000006 duplicates N-000026 (pack 07) along with the mandatory `--recent_days` parameter
- N-000006 refines N-000001 (pack 02)
- N-000006 same as N-000026 (pack 07) along with the mandatory `--recent_days` parameter
- N-000010 duplicates N-000030 (pack 08) recent_days (int, required): Filter papers from the most recent k days.
- N-000010 same as N-000030 (pack 08) recent_days (int, required): Filter papers from the most recent k days.
- N-000011 duplicates N-000032 (pack 08) verbose (Boolean, optional): Flag to print results to the console.
- N-000011 same as N-000032 (pack 08) verbose (Boolean, optional): Flag to print results to the console.
- N-000012 duplicates N-000031 (pack 08) to_file (str, optional): Path to save the results in CSV format.
- N-000012 refines N-000002 (pack 03)
- N-000012 same as N-000031 (pack 08) to_file (str, optional): Path to save the results in CSV format.
- N-000013 covered by N-000032 (pack 08) verbose (Boolean, optional): Flag to print results to the console.
- N-000013 refines N-000002 (pack 03)
- N-000013 subsumes N-000032 (pack 08)
- N-000030 refines N-000006 (pack 08)
- N-000051 refines N-000010 (pack 12)
- N-000051 refines N-000016 (pack 12)

## Conflicts
- UNSETTLED: CF-000003 — N-000013 "else if only --to_file, only save to csv" vs N-000038 "main->>Global_functions: print_results()"
  rationale: A says that with only --to_file the program saves to CSV without printing, while B's diagram has main always calling print_results with no condition, so both cannot hold for a save-only run.
- UNSETTLED: CF-000006 — N-000011 "controlled by --verbose" vs N-000013 "otherwise (either only --verbose or neither specified), print to console"
  rationale: Claim A says console output is controlled by --verbose, so it should not appear without it, but Claim B prints to console when neither flag is specified.

## Terms
- arxiv — defined: "ArXiv: An open-access archive and distribution service for scholarly articles in various scientific fields."
