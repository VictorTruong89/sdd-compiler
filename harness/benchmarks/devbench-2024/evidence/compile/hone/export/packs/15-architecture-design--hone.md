# Pack 15 — sdd/specs/architecture_design.md · Architecture Design › Hone:
blocks 17 · nodes 15 (constraint 1, decision 1, requirement 13) · AC labels: none

## Text
# Architecture Design

## Hone:

This is the main package of the project, containing the Hone class and utility functions for conversion between CSV and JSON.
↳ N-000045 requirement · MUST · L2

- `__init__.py`: Import statement file to make the Hone class available as part of the package.
↳ N-000046 requirement · MUST · L2

- `hone.py`: Contains the Hone class with methods to convert CSV files to a nested JSON structure.
↳ N-000047 requirement · MUST · L2

- `test`: Directory containing test scripts to validate the functionality of the Hone class and its methods.
↳ N-000048 requirement · MUST · L2

- `utils`: Directory containing utility scripts for CSV and JSON processing.
↳ N-000049 requirement · MUST · L2

### Hone Class (hone.py):

- `Hone`: The central class responsible for CSV to JSON conversion.
↳ N-000050 requirement · MUST · L2

  - `convert()`: Converts CSV files to JSON based on specified or generated schema.
↳ N-000051 requirement · MUST · L2

  - `get_schema()`: Retrieves a generated JSON schema based on the structure of the CSV file.
↳ N-000052 requirement · MUST · L2

### Utils:

Utility scripts to assist with file operations and provide helper functions.
↳ N-000053 requirement · MUST · L2

- `csv_utils.py`: Contains methods for reading and processing CSV files.
↳ N-000054 requirement · MUST · L2

- `json_utils.py`: Contains methods for writing JSON structures to files or stdout.
↳ N-000055 requirement · MUST · L2

- `test_utils.py`: Contains methods for parsing and testing JSON and CSV files within the test scripts.
↳ N-000056 requirement · MUST · L2

The utils directory should contain standalone scripts that provide functionality used by the hone.py script, such as reading, parsing, and writing files.
↳ N-000057 constraint · SHOULD · L2

The outputs folder is not included in this structure, as the Hone tool outputs JSON either to a specified file or standard output.
↳ N-000058 decision · — · L2

### Examples:

- To convert a CSV to a nested JSON, you would invoke the Hone class with the desired CSV file path.
↳ no node

- Example CSV and JSON files are provided to demonstrate the conversion process.
↳ no node

```bash
#! /bin/bash

# Run the demo
python examples/demo.py 
```
↳ N-000059 requirement · MUST · L2

## Claims to implement
- [N-000045] requirement · MUST · L2 — This is the main package of the project, containing the Hone class and utility functions for conversion between CSV and JSON.
  needs: none
- [N-000046] requirement · MUST · L2 — __init__.py`: Import statement file to make the Hone class available as part of the package.
  needs: N-000047
- [N-000047] requirement · MUST · L2 — hone.py`: Contains the Hone class with methods to convert CSV files to a nested JSON structure.
  needs: none
- [N-000048] requirement · MUST · L2 — test`: Directory containing test scripts to validate the functionality of the Hone class and its methods.
  needs: none
- [N-000049] requirement · MUST · L2 — utils`: Directory containing utility scripts for CSV and JSON processing.
  needs: none
- [N-000050] requirement · MUST · L2 — Hone`: The central class responsible for CSV to JSON conversion.
  needs: none
- [N-000051] requirement · MUST · L2 — convert()`: Converts CSV files to JSON based on specified or generated schema.
  needs: none
- [N-000052] requirement · MUST · L2 — get_schema()`: Retrieves a generated JSON schema based on the structure of the CSV file.
  needs: none
- [N-000053] requirement · MUST · L2 — Utility scripts to assist with file operations and provide helper functions.
  needs: none
- [N-000054] requirement · MUST · L2 — csv_utils.py`: Contains methods for reading and processing CSV files.
  needs: none
- [N-000055] requirement · MUST · L2 — json_utils.py`: Contains methods for writing JSON structures to files or stdout.
  needs: none
- [N-000056] requirement · MUST · L2 — test_utils.py`: Contains methods for parsing and testing JSON and CSV files within the test scripts.
  needs: none
- [N-000057] constraint · SHOULD · L2 — The utils directory should contain standalone scripts that provide functionality used by the hone.py script, such as reading, parsing, and writing files.
  needs: none
- [N-000058] decision · — · L2 — The outputs folder is not included in this structure
  needs: none
  chosen: Leave the outputs folder out of this structure
  rejected: Include an outputs folder in this structure — the Hone tool outputs JSON either to a specified file or standard output.
- [N-000059] requirement · MUST · L2 — #! /bin/bash
    
    # Run the demo
    python examples/demo.py
  needs: none

## Acceptance criteria
None.

## Constraints in scope
- [N-000025] (pack 05) utilize built-in libraries for CSV and JSON processing.
plus the broad constraints in pack 01

## Related elsewhere
- N-000008 refines N-000051 (pack 03)
- N-000030 duplicates N-000059 (pack 07) #! /bin/bash
    
    # Run the demo
    python examples/demo.py
- N-000037 duplicates N-000051 (pack 09) For a CSV input, the conversion must produce a valid JSON object that matches the schema provided or generated.
- N-000045 refines N-000001 (pack 02)
- N-000051 refines N-000035 (pack 09)
- N-000051 same as N-000037 (pack 09) For a CSV input, the conversion must produce a valid JSON object that matches the schema provided or generated.
- N-000059 same as N-000030 (pack 07) #! /bin/bash
    
    # Run the demo
    python examples/demo.py

## Conflicts
None.

## Terms
None.
