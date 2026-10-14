# Checklist

Every id below must end implemented, tested, or listed as not done with a reason.

## Pack 01 — 01-prd--introduction.md

None.

## Pack 02 — 02-prd--goals.md

- [ ] N-000001 · requirement · MUST · L2 · — · The goal of this project is to develop a Python package
- [ ] N-000002 · requirement · MUST · L0 · — · simplifies the task of converting CSV files to structured JSON
- [ ] N-000003 · requirement · SHOULD · L1 · — · accommodate custom delimiters
- [ ] N-000004 · requirement · SHOULD · L1 · — · and schema structures
- [ ] N-000005 · requirement · SHOULD · L1 · — · ensuring that users can tailor the output to their specific requirements

## Pack 03 — 03-prd--features-and-functionalities.md

- [ ] N-000006 · requirement · MUST · L1 · — · Ability to read CSV files and extract column names and data rows.
- [ ] N-000007 · requirement · MUST · L1 · — · Support for custom delimiters within CSV files
- [ ] N-000008 · requirement · MUST · L1 · — · Conversion of flat CSV data into a nested JSON structure using a custom or autom…
- [ ] N-000009 · requirement · MUST · L1 · — · Output JSON files with proper indentation and sorted keys
- [ ] N-000010 · requirement · MUST · L2 · — · Helper methods to open and manage CSV and JSON files
- [ ] N-000011 · requirement · MUST · L1 · — · writing JSON to standard output
- [ ] N-000012 · requirement · MUST · L2 · — · Context managers for file operations
- [ ] N-000013 · requirement · MUST · L1 · — · Argument parsing for specifying delimiters, schema, CSV input filepath, and JSON…
- [ ] N-000014 · requirement · MUST · L1 · — · CLI support for easy execution of the conversion process from the command line.

## Pack 04 — 04-prd--supporting-data-description.md

- [ ] N-000015 · assumption · — · — · — · utilizes datasets stored in three folders: `data_file/comma_test`, `./data_file/…
- [ ] N-000016 · assumption · — · L1 · — · Contains files such as `column_names.csv`, `data_rows.csv`, `dataset.csv`, and `…
- [ ] N-000017 · requirement · — · L1 · — · Tests the parsing of column names within a CSV file.
- [ ] N-000018 · requirement · — · L1 · — · Includes similar files: `column_names.csv`, `data_rows.csv`, `dataset.csv`, and …
- [ ] N-000019 · requirement · — · L4 · — · [ { "some 'quoted\"' field\"": "no quotes", "adopted_since": "2012", "adopted": …
- [ ] N-000020 · requirement · — · L2 · — · Houses `column_names.csv`, `data_rows.csv`, `dataset.csv`, `nested_dataset.json`…
- [ ] N-000021 · requirement · — · L4 · — · [ { "adopted": "TRUE", "adopted_since": "2012", "age (years)": "5", "birth": { "…
- [ ] N-000022 · requirement · MUST · L4 · — · Specifies the expected mapping of CSV columns to JSON fields.
- [ ] N-000023 · requirement · — · L4 · — · { "adopted_since": "adopted_since", "adopted": "adopted", "birth": { "year": "bi…

## Pack 05 — 05-prd--technical-constraints.md

- [ ] N-000024 · constraint · MUST · C · — · The solution must be implemented in Python
- [ ] N-000025 · constraint · MUST · C · — · utilize built-in libraries for CSV and JSON processing.
- [ ] N-000026 · constraint · SHOULD · C · — · The package should be OS-independent
- [ ] N-000027 · constraint · SHOULD · C · — · capable of running on any standard Python environment.

## Pack 06 — 06-prd--dependencies.md

- [ ] N-000028 · requirement · MUST · L2 · — · Standard Python libraries: `csv`, `json`, `argparse`, `contextlib
- [ ] N-000029 · requirement · MUST NOT · L1 · — · No external dependencies are required for the core functionality.

## Pack 07 — 07-prd--usage.md

- [ ] N-000030 · requirement · SHOULD · — · — · #! /bin/bash # Run the demo python examples/demo.py

## Pack 08 — 08-prd--command-line-configuration-arguments.md

- [ ] N-000031 · requirement · MAY · L1 · — · --delimiters` (list, optional) - List of string delimiters for parsing CSV files…
- [ ] N-000032 · requirement · MAY · L1 · — · --schema` (JSON object as string, optional) - JSON schema structure for the outp…
- [ ] N-000033 · requirement · MUST · L1 · — · csv_filepath` (string, required) - Path to the input CSV file.
- [ ] N-000034 · requirement · MUST · L1 · — · json_filepath` (string, required) - Path to the output JSON file.

## Pack 09 — 09-prd--acceptance-criteria.md

- [ ] N-000035 · requirement · SHOULD · L1 · — · The package should be capable of converting any valid CSV file to a structured J…
- [ ] N-000036 · requirement · SHOULD · L1 · — · The output JSON should accurately reflect the structure defined by the schema or…
- [ ] N-000037 · requirement · MUST · L1 · — · For a CSV input, the conversion must produce a valid JSON object that matches th…
- [ ] N-000038 · requirement · MUST · L1 · — · The CLI must handle the specified arguments correctly
- [ ] N-000039 · requirement · MUST · L1 · — · output the result to the appropriate location, whether it be a file or standard …

## Pack 10 — 10-prd--terms-concepts-explanation.md

None.

## Pack 11 — 11-uml-class--root.md

- [ ] N-000040 · requirement · MUST · L2 · — · classDiagram class Global_functions { <<fake class, to host global functions>> o…

## Pack 12 — 12-uml-sequence--root.md

- [ ] N-000041 · requirement · MUST · L2 · — · sequenceDiagram participant main participant ArgParse participant Hone participa…

## Pack 13 — 13-architecture-design--architecture-design.md

- [ ] N-000042 · requirement · MUST · L1 · — · ├── examples │ ├── demo.py │ ├── demo.sh │ ├── example_a.csv │ ├── example_a.jso…

## Pack 14 — 14-architecture-design--outputs.md

- [ ] N-000043 · assumption · — · L1 · — · example_a/b/c.csv`: CSV files used as input for conversion.
- [ ] N-000044 · assumption · — · L1 · — · example_a/b/c.json`: JSON files produced by the conversion process.

## Pack 15 — 15-architecture-design--hone.md

- [ ] N-000045 · requirement · MUST · L2 · — · This is the main package of the project, containing the Hone class and utility f…
- [ ] N-000046 · requirement · MUST · L2 · — · __init__.py`: Import statement file to make the Hone class available as part of …
- [ ] N-000047 · requirement · MUST · L2 · — · hone.py`: Contains the Hone class with methods to convert CSV files to a nested …
- [ ] N-000048 · requirement · MUST · L2 · — · test`: Directory containing test scripts to validate the functionality of the Ho…
- [ ] N-000049 · requirement · MUST · L2 · — · utils`: Directory containing utility scripts for CSV and JSON processing.
- [ ] N-000050 · requirement · MUST · L2 · — · Hone`: The central class responsible for CSV to JSON conversion.
- [ ] N-000051 · requirement · MUST · L2 · — · convert()`: Converts CSV files to JSON based on specified or generated schema.
- [ ] N-000052 · requirement · MUST · L2 · — · get_schema()`: Retrieves a generated JSON schema based on the structure of the C…
- [ ] N-000053 · requirement · MUST · L2 · — · Utility scripts to assist with file operations and provide helper functions.
- [ ] N-000054 · requirement · MUST · L2 · — · csv_utils.py`: Contains methods for reading and processing CSV files.
- [ ] N-000055 · requirement · MUST · L2 · — · json_utils.py`: Contains methods for writing JSON structures to files or stdout.
- [ ] N-000056 · requirement · MUST · L2 · — · test_utils.py`: Contains methods for parsing and testing JSON and CSV files with…
- [ ] N-000057 · constraint · SHOULD · L2 · — · The utils directory should contain standalone scripts that provide functionality…
- [ ] N-000058 · decision · — · L2 · — · The outputs folder is not included in this structure
- [ ] N-000059 · requirement · MUST · L2 · — · #! /bin/bash # Run the demo python examples/demo.py

## Pack 16 — 16-architecture-design--license-and-readme.md

- [ ] N-000060 · requirement · MUST · L2 · — · LICENSE`: Contains the licensing information for the Hone project.
- [ ] N-000061 · requirement · MUST · — · — · README.md`: Provides an overview and documentation for the Hone project.
