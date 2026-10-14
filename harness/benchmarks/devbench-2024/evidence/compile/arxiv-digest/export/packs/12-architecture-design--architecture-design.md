# Pack 12 — sdd/specs/architecture_design.md · Architecture Design
blocks 22 · nodes 17 (constraint 2, requirement 15) · AC labels: none

## Text
# Architecture Design

Below is a text-based representation of the file tree.
↳ no node

```bash
├── .gitignore
├── examples
│   ├── run_query_all.sh
│   ├── run_query_only_csv.sh
│   └── run_query_only_verbose.sh
├── query_arxiv.py
├── outputs
│   ├── query_results.txt
│   └── query_results.csv
```
↳ N-000039 requirement · MUST · L2

Output:
↳ no node

- query_results.txt: results printed to console, including titles, authors, links, and truncated abstracts.
↳ N-000040 requirement · MUST

- query_results.csv: complete query results saved in a csv file, whose columns should include title, author, publication date, abstract, and link.
The outputs folder should be ignored in git.
↳ N-000041 requirement · SHOULD · L3 ; N-000042 constraint · SHOULD · L1

Examples:
↳ no node

- To make a complete query request, run `sh ./examples/run_query_all.sh`. An example of the script `run_query_all.sh` is shown as follows.
↳ N-000043 requirement · MUST

```
python query_arxiv.py \
--category cs.CL \
--title LLM \
--author Smith \
--abstract Deep+Learning \
--recent_days 10 \
--to_file output/query_all_results.csv \
--verbose \
>> output/query_all_results.txt
```
↳ no node

- To make a query request that only save results to csv while not print result to console, run `sh ./examples/run_query_only_csv.sh`. An example of the script `run_query_only_csv.sh` is shown as follows.
↳ N-000044 requirement · MUST

```
python query_arxiv.py \
--category cs.CL \
--title LLM \
--author Smith \
--abstract Deep+Learning \
--recent_days 10 \
--to_file output/query_only_csv_results.csv
```
↳ no node

- To make a query request that only print result to cosole and save that to txt file without storing csv, run `sh ./examples/run_query_only_verbose.sh`. An example of the script `run_query_only_verbose.sh` is shown as follows.
↳ N-000045 requirement · MUST

```
python query_arxiv.py \
--category cs.CL \
--title LLM \
--author Smith \
--abstract Deep+Learning \
--recent_days 10 \
--verbose \
>> output/query_only_verbose_results.txt
```
↳ no node

`query_arxiv.py`:
↳ no node

- get_args(): parse arguments from command line.
↳ N-000046 requirement · MUST · L2

- main(): the body of implementing querying, filtering, saving, and showing results.
↳ N-000047 requirement · MUST · L2

    - construct_query_url(): construct query url that is going to be send to ArXiv API according to arguments.
↳ N-000048 requirement · MUST · L2

    - fetch_data(): get response from ArXiv API through a get request.
↳ N-000049 requirement · MUST · L2

    - process_entries(): process response from ArXiv and return a list of dictionaries to store paper information
↳ N-000050 requirement · MUST · L2

    - check_date(): check if the publication date of the a certain paper is within k days from current date (k specified by arguments)
↳ N-000051 requirement · MUST · L5

    - save_to_csv(): save valid papers to csv file whose path/fileName is specified by arguments
↳ N-000052 requirement · MUST · L5

    - print_results(): print search results to console (abstract being truncated)
↳ N-000053 requirement · MUST · L1 ; N-000054 requirement · MUST · L1

The standalone functions are all placed in the `query_arxiv.py` file.
↳ N-000055 constraint · MUST · C

## Claims to implement
- [N-000039] requirement · MUST · L2 — ├── .gitignore
    ├── examples
    │   ├── run_query_all.sh
    │   ├── run_query_only_csv.sh
    │   └── run_query_only_verbose.sh
    ├── query_arxiv.py
    ├── outputs
    │   ├── query_results.txt
    │   └── query_results.csv
  needs: none
- [N-000040] requirement · MUST · — — query_results.txt: results printed to console, including titles, authors, links, and truncated abstracts.
  needs: none
- [N-000041] requirement · SHOULD · L3 — query_results.csv: complete query results saved in a csv file, whose columns should include title, author, publication date, abstract, and link.
  needs: none
- [N-000042] constraint · SHOULD · L1 — The outputs folder should be ignored in git.
  needs: none
- [N-000043] requirement · MUST · — — To make a complete query request, run `sh ./examples/run_query_all.sh`.
  needs: none
- [N-000044] requirement · MUST · — — To make a query request that only save results to csv while not print result to console, run `sh ./examples/run_query_only_csv.sh`.
  needs: none
- [N-000045] requirement · MUST · — — To make a query request that only print result to cosole and save that to txt file without storing csv, run `sh ./examples/run_query_only_verbose.sh`.
  needs: none
- [N-000046] requirement · MUST · L2 — get_args(): parse arguments from command line.
  needs: none
- [N-000047] requirement · MUST · L2 — main(): the body of implementing querying, filtering, saving, and showing results.
  needs: none
- [N-000048] requirement · MUST · L2 — construct_query_url(): construct query url that is going to be send to ArXiv API according to arguments.
  needs: none
- [N-000049] requirement · MUST · L2 — fetch_data(): get response from ArXiv API through a get request.
  needs: none
- [N-000050] requirement · MUST · L2 — process_entries(): process response from ArXiv and return a list of dictionaries to store paper information
  needs: none
- [N-000051] requirement · MUST · L5 — check_date(): check if the publication date of the a certain paper is within k days from current date (k specified by arguments)
  needs: none
- [N-000052] requirement · MUST · L5 — save_to_csv(): save valid papers to csv file whose path/fileName is specified by arguments
  needs: none
- [N-000053] requirement · MUST · L1 — print_results(): print search results to console
  needs: none
- [N-000054] requirement · MUST · L1 — abstract being truncated
  needs: none
- [N-000055] constraint · MUST · C — The standalone functions are all placed in the `query_arxiv.py` file.
  needs: none

## Acceptance criteria
None.

## Constraints in scope
- [N-000019] (pack 05) The tool will be developed in Python, utilizing necessary libraries for API interaction, XML data parsing, and command-line argument parsing.
- [N-000020] (pack 05) Compliance with ArXiv API usage guidelines and rate limits is required.

## Related elsewhere
- N-000040 refines N-000002 (pack 03)
- N-000044 refines N-000002 (pack 03)
- N-000044 refines N-000024 (pack 07)
- N-000051 refines N-000010 (pack 04)
- N-000051 refines N-000016 (pack 04)
- N-000051 refines N-000030 (pack 08)
- N-000052 refines N-000002 (pack 03)

## Conflicts
None.

## Terms
- arxiv — defined: "ArXiv: An open-access archive and distribution service for scholarly articles in various scientific fields."
- global function — defined: "`Global_functions` is a fake class to host global functions"
- query arxiv — defined: "Query ArXiv is a tool designed to streamline the process of fetching research papers from the ArXiv database."
