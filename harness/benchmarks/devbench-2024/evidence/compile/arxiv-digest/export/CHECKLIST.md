# Checklist

Every id below must end implemented, tested, or listed as not done with a reason.

## Pack 01 — 01-uml-class--uml-class.md

- [ ] N-000037 · requirement · MUST · L2 · — · classDiagram class Global_functions{ +get_args(argv=None) -> argparse.Namespace …

## Pack 02 — 02-prd--introduction.md

- [ ] N-000001 · requirement · MAY · L1 · — · It allows users to perform advanced searches based on parameters like category, …

## Pack 03 — 03-prd--goals.md

- [ ] N-000002 · requirement · SHOULD · L1 · — · It should also allow user to either print query results to console or save them …

## Pack 04 — 04-prd--features-and-functionalities.md

- [ ] N-000003 · requirement · MAY · L1 · — · Enables querying by any combinations of `category`, `author`, `title`, and `abst…
- [ ] N-000004 · constraint · SHOULD · L1 · — · But at least one of them should be specified
- [ ] N-000005 · requirement · MUST · L1 · — · max_results` parameter to control the number of results, with a sensible default…
- [ ] N-000006 · requirement · MUST · L1 · — · Integrates a mandatory `recent_days` parameter,
- [ ] N-000007 · assumption · — · — · — · not directly supported by ArXiv.
- [ ] N-000008 · constraint · MUST · L5 · — · This feature requires custom implementation:
- [ ] N-000009 · requirement · MUST · L5 · — · Queries are structured with sortBy=submittedDate and sortOrder=descending to fet…
- [ ] N-000010 · requirement · MUST · L5 · — · The `check_date` function is written to filter the results based on the recent_d…
- [ ] N-000011 · requirement · MUST · L1 · — · Console Output for immediate viewing, controlled by --verbose.
- [ ] N-000012 · requirement · MUST · L1 · — · CSV Export option controlled by --to_file.
- [ ] N-000013 · requirement · MUST · L1 · — · If both specified, print to console and save to csv; else if only --to_file, onl…
- [ ] N-000014 · requirement · MUST · L1 · — · Command-line arguments for search parameters and output preferences.
- [ ] N-000015 · requirement · MUST · L1 · — · Efficient API interactions and XML data parsing according to user criteria.
- [ ] N-000016 · requirement · MUST · L5 · — · Applies date filtering via check_date.
- [ ] N-000017 · requirement · MUST · L1 · — · Coherent presentation of key details in both console and CSV.
- [ ] N-000018 · requirement · SHOULD · L1 · — · Both console output and CSV columns should include at least the following infora…

## Pack 05 — 05-prd--technical-constraints.md

- [ ] N-000019 · constraint · MUST · C · — · The tool will be developed in Python, utilizing necessary libraries for API inte…
- [ ] N-000020 · constraint · MUST · C · — · Compliance with ArXiv API usage guidelines and rate limits is required.
- [ ] N-000021 · requirement · MUST · L1 · — · Accurate and reliable date handling for time-based filtering.

## Pack 06 — 06-prd--dependencies.md

- [ ] N-000022 · requirement · MUST · — · — · Python 3.x
- [ ] N-000023 · requirement · MUST · — · — · Libraries: os, datetime, urllib, xml.etree.ElementTree, csv, and argparse

## Pack 07 — 07-prd--usage.md

- [ ] N-000024 · requirement · MUST · L1 · — · python query_arxiv.py --category [category] --title [title] --author [author] --…
- [ ] N-000025 · requirement · MUST · L1 · — · At least one of the query parameters `[category, title, author, abstract]` must …
- [ ] N-000026 · requirement · MUST · L1 · — · along with the mandatory `--recent_days` parameter
- [ ] N-000027 · constraint · SHOULD · C · — · All arguments should be constructed with only characters from `"ABCDEFGHIJKLMNOP…
- [ ] N-000028 · requirement · MUST · L1 · — · otherwise, a `ValueError` will be raised.

## Pack 08 — 08-prd--command-line-arguments-script-input.md

- [ ] N-000029 · requirement · MAY · L1 · — · abstract (str, optional): Keyword in the abstract.
- [ ] N-000030 · requirement · MUST · L1 · — · recent_days (int, required): Filter papers from the most recent k days.
- [ ] N-000031 · requirement · MAY · L1 · — · to_file (str, optional): Path to save the results in CSV format.
- [ ] N-000032 · requirement · MAY · L1 · — · verbose (Boolean, optional): Flag to print results to the console.

## Pack 09 — 09-prd--acceptance-criteria.md

- [ ] N-000033 · verification · — · V · — · Successful execution of queries with various combinations of parameters.
- [ ] N-000034 · verification · — · V · — · Accurate filtering based on the recent_days parameter.
- [ ] N-000035 · verification · — · V · — · Correct formatting and data integrity in both console output and CSV file.
- [ ] N-000036 · verification · — · V · — · Compliance with performance and reliability standards, including efficient handl…

## Pack 10 — 10-prd--terms-concepts-explanation.md

None.

## Pack 11 — 11-uml-sequence--uml-sequence.md

- [ ] N-000038 · requirement · MUST · L2 · — · sequenceDiagram participant Global_functions participant main main->>Global_func…

## Pack 12 — 12-architecture-design--architecture-design.md

- [ ] N-000039 · requirement · MUST · L2 · — · ├── .gitignore ├── examples │ ├── run_query_all.sh │ ├── run_query_only_csv.sh │…
- [ ] N-000040 · requirement · MUST · — · — · query_results.txt: results printed to console, including titles, authors, links,…
- [ ] N-000041 · requirement · SHOULD · L3 · — · query_results.csv: complete query results saved in a csv file, whose columns sho…
- [ ] N-000042 · constraint · SHOULD · L1 · — · The outputs folder should be ignored in git.
- [ ] N-000043 · requirement · MUST · — · — · To make a complete query request, run `sh ./examples/run_query_all.sh`.
- [ ] N-000044 · requirement · MUST · — · — · To make a query request that only save results to csv while not print result to …
- [ ] N-000045 · requirement · MUST · — · — · To make a query request that only print result to cosole and save that to txt fi…
- [ ] N-000046 · requirement · MUST · L2 · — · get_args(): parse arguments from command line.
- [ ] N-000047 · requirement · MUST · L2 · — · main(): the body of implementing querying, filtering, saving, and showing result…
- [ ] N-000048 · requirement · MUST · L2 · — · construct_query_url(): construct query url that is going to be send to ArXiv API…
- [ ] N-000049 · requirement · MUST · L2 · — · fetch_data(): get response from ArXiv API through a get request.
- [ ] N-000050 · requirement · MUST · L2 · — · process_entries(): process response from ArXiv and return a list of dictionaries…
- [ ] N-000051 · requirement · MUST · L5 · — · check_date(): check if the publication date of the a certain paper is within k d…
- [ ] N-000052 · requirement · MUST · L5 · — · save_to_csv(): save valid papers to csv file whose path/fileName is specified by…
- [ ] N-000053 · requirement · MUST · L1 · — · print_results(): print search results to console
- [ ] N-000054 · requirement · MUST · L1 · — · abstract being truncated
- [ ] N-000055 · constraint · MUST · C · — · The standalone functions are all placed in the `query_arxiv.py` file.
