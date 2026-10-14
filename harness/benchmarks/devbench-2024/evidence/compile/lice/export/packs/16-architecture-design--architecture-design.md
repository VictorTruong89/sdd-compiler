# Pack 16 — sdd/specs/architecture_design.md · Architecture Design
blocks 24 · nodes 17 (assumption 1, decision 7, requirement 9) · AC labels: none

## Text
# Architecture Design

This document outlines the architecture design for the Lice License Generator project. The design is based on the functionality as specified in the `core.py` and `_init_.py` files, as well as the `examples.sh` script provided.
↳ N-000042 assumption · —

Below is a text-based representation of the file tree for the Lice License Generator project.
↳ no node

```plaintext
├── .github
├── lice
│   ├── __init__.py
│   └── core.py
└── examples
    └── examples.sh
```
↳ no node

Examples:
↳ no node

- To generate a license, run `./examples.sh` which encapsulates the commands to install Lice and generate various licenses.
↳ N-000043 requirement · MUST · L1

- To run tests, the `examples.sh` script includes a command for discovering and running unit tests.
↳ N-000044 requirement · MUST · L1

  ```bash
    #! /bin/bash
    set -e
    
    # source /path/to/your/venv/bin/activate
    pip install lice
    
    lice
    
    lice mit
    
    lice -y $(date +"%Y") -o "Your Organization Name"
    
    lice -l py > LICENSE.txt
    
    # Run tests
    python -m unittest discover -s ./lice/tests -p 'test_*.py'
  ```
↳ N-000045 requirement · MUST · L1

`__init__.py`:
↳ no node

- Defines the version of the Lice package and the `main()` entry point for the CLI.
↳ N-000046 requirement · — · L1 ; N-000047 requirement · — · L2

`core.py`:
↳ no node

- Houses the main functionality of the Lice License Generator.
↳ N-000048 decision · — · L2

    - `main()`: Parses command-line arguments and invokes the appropriate functions to generate licenses.
↳ N-000049 decision · — · L1

    - `guess_organization()`: Attempts to determine the user's organization from git config or the USER environment variable.
↳ N-000050 decision · — · L1

    - `generate_license()`: Generates the license text based on the selected template and context (year, organization, project).
↳ N-000051 decision · — · L1

    - `format_license()`: Formats the license text for a specific programming language comment style.
↳ N-000052 decision · — · L1

Templates:
↳ no node

- The `templates` directory contains the text templates for various licenses. Each license template can be used to generate the corresponding license file.
↳ N-000053 decision · — · L2 ; N-000054 requirement · MAY · L1

To generate a license:
↳ no node

```bash
lice [license_type] -o "Your Organization Name" -y $(date +"%Y")
```
↳ N-000055 requirement · MUST · L1

To format a license for a Python source file:
↳ no node

```bash
lice -l py -f [filename]
```
↳ N-000056 requirement · MUST · L1

To run tests:
↳ no node

```bash
python -m unittest discover -s ./lice/tests -p 'test_*.py'
```
↳ N-000057 requirement · MUST · L1

The architecture is designed to be modular and extensible, allowing for the addition of new license templates and language comment styles as needed.
↳ N-000058 decision · — · C

## Claims to implement
- [N-000042] assumption · — · — — The design is based on the functionality as specified in the `core.py` and `_init_.py` files, as well as the `examples.sh` script provided.
  needs: none
- [N-000043] requirement · MUST · L1 — To generate a license, run `./examples.sh` which encapsulates the commands to install Lice and generate various licenses.
  needs: none
- [N-000044] requirement · MUST · L1 — To run tests, the `examples.sh` script includes a command for discovering and running unit tests.
  needs: none
- [N-000045] requirement · MUST · L1 —     #! /bin/bash
        set -e
        
        # source /path/to/your/venv/bin/activate
        pip install lice
        
        lice
        
        lice mit
        
        lice -y $(date +"%Y") -o "Your Organization Name"
        
        lice -l py > LICENSE.txt
        
        # Run tests
        python -m unittest discover -s ./lice/tests -p 'test_*.py'
  needs: none
- [N-000046] requirement · — · L1 — Defines the version of the Lice package
  needs: none
- [N-000047] requirement · — · L2 — the `main()` entry point for the CLI
  needs: none
- [N-000048] decision · — · L2 — Houses the main functionality of the Lice License Generator.
  needs: none
  chosen: Houses the main functionality of the Lice License Generator.
  rejected: none
- [N-000049] decision · — · L1 — main()`: Parses command-line arguments and invokes the appropriate functions to generate licenses.
  needs: none
  chosen: `main()`: Parses command-line arguments and invokes the appropriate functions to generate licenses.
  rejected: none
- [N-000050] decision · — · L1 — guess_organization()`: Attempts to determine the user's organization from git config or the USER environment variable.
  needs: none
  chosen: `guess_organization()`: Attempts to determine the user's organization from git config or the USER environment variable.
  rejected: none
- [N-000051] decision · — · L1 — generate_license()`: Generates the license text based on the selected template and context (year, organization, project).
  needs: none
  chosen: `generate_license()`: Generates the license text based on the selected template and context (year, organization, project).
  rejected: none
- [N-000052] decision · — · L1 — format_license()`: Formats the license text for a specific programming language comment style.
  needs: none
  chosen: `format_license()`: Formats the license text for a specific programming language comment style.
  rejected: none
- [N-000053] decision · — · L2 — The `templates` directory contains the text templates for various licenses.
  needs: none
  chosen: The `templates` directory contains the text templates for various licenses.
  rejected: none
- [N-000054] requirement · MAY · L1 — Each license template can be used to generate the corresponding license file.
  needs: none
- [N-000055] requirement · MUST · L1 — lice [license_type] -o "Your Organization Name" -y $(date +"%Y")
  needs: none
- [N-000056] requirement · MUST · L1 — lice -l py -f [filename]
  needs: none
- [N-000057] requirement · MUST · L1 — python -m unittest discover -s ./lice/tests -p 'test_*.py'
  needs: none
- [N-000058] decision · — · C — The architecture is designed to be modular and extensible
  needs: none
  chosen: modular and extensible architecture
  rejected: none

## Acceptance criteria
None.

## Constraints in scope
- [N-000025] (pack 06) it should be maintainable and follow Pythonic conventions
plus the broad constraints in pack 01

## Related elsewhere
- N-000009 duplicates N-000050 (pack 03) Tries to use `git config` or the `$USER` environment variable if the organization is not specified.
- N-000014 refines N-000053 (pack 04)
- N-000015 duplicates N-000053 (pack 04) Includes a wide range of license templates, such as `template-afl3.txt`, `template-agpl3.txt`, `template-apache.txt`, `template-bsd2.txt`, `template-cc_by.txt`, and many others.
- N-000018 refines N-000053 (pack 04)
- N-000033 refines N-000051 (pack 11)
- N-000043 refines N-000006 (pack 03)
- N-000050 refines N-000038 (pack 12)
- N-000050 same as N-000009 (pack 03) Tries to use `git config` or the `$USER` environment variable if the organization is not specified.
- N-000052 refines N-000035 (pack 11)
- N-000053 same as N-000015 (pack 04) Includes a wide range of license templates, such as `template-afl3.txt`, `template-agpl3.txt`, `template-apache.txt`, `template-bsd2.txt`, `template-cc_by.txt`, and many others.
- N-000055 refines N-000007 (pack 03)
- N-000056 refines N-000006 (pack 03)

## Conflicts
None.

## Terms
- license — defined: "`license`: The type of license to generate."
