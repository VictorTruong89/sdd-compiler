# Checklist

Every id below must end implemented, tested, or listed as not done with a reason.

## Pack 01 — 01-prd--introduction.md

None.

## Pack 02 — 02-prd--goals.md

- [ ] N-000001 · requirement · MUST · L1 · — · to provide a tool
- [ ] N-000002 · requirement · MUST · L1 · — · quickly generates license files for software projects
- [ ] N-000003 · requirement · MUST · L1 · — · supporting a wide range of commonly used open-source licenses
- [ ] N-000004 · requirement · MUST · L0 · — · save time for developers
- [ ] N-000005 · requirement · MUST · L0 · — · help ensure that software licensing is handled correctly and efficiently

## Pack 03 — 03-prd--features-and-functionalities.md

- [ ] N-000006 · requirement · MAY · L1 · — · Users can generate various licenses such as BSD-3, MIT, GPL, etc., with simple c…
- [ ] N-000007 · requirement · MAY · L1 · — · Allows specification of the year
- [ ] N-000008 · requirement · MAY · L1 · — · and organization for the generated license
- [ ] N-000009 · requirement · SHOULD · L1 · — · Tries to use `git config` or the `$USER` environment variable if the organizatio…
- [ ] N-000010 · requirement · MUST · L1 · — · Supports the creation of license headers for source files in different programmi…
- [ ] N-000011 · requirement · MAY · L1 · — · Can generate a new source file with the license commented in the header.
- [ ] N-000012 · requirement · MUST · L1 · — · Automatically detects the language for file formatting based on the file extensi…
- [ ] N-000013 · requirement · MAY · — · — · Users can contribute by adding support for additional licenses or programming la…

## Pack 04 — 04-prd--supporting-data-description.md

- [ ] N-000014 · requirement · MUST · L2 · — · uses a set of 35 templates stored in the `templates` folder
- [ ] N-000015 · requirement · MUST · L2 · — · Includes a wide range of license templates, such as `template-afl3.txt`, `templa…
- [ ] N-000016 · requirement · MUST · L4 · — · Each template corresponds to a different type of open-source license
- [ ] N-000017 · requirement · MUST · L4 · — · covering common licenses like Apache, GPL, MIT, BSD, and Creative Commons varian…
- [ ] N-000018 · requirement · MUST · L2 · — · Contains header templates like `template-agpl3-header.txt`, `template-apache-hea…
- [ ] N-000019 · requirement · MUST · L1 · — · These templates are designed to insert license information into the headers of s…
- [ ] N-000020 · requirement · MUST · L1 · — · catering to different programming languages and file types
- [ ] N-000021 · requirement · MUST · L1 · — · allows the `lice` tool to generate license files tailored to a variety of licens…

## Pack 05 — 05-prd--constraints.md

- [ ] N-000022 · constraint · SHOULD · C · — · The project should be intuitive enough for developers who are not familiar with …
- [ ] N-000023 · requirement · SHOULD · L1 · — · It should be easily integrated into existing workflows or development environmen…

## Pack 06 — 06-prd--technical-constraints.md

- [ ] N-000024 · assumption · — · — · — · The project is implemented in Python
- [ ] N-000025 · requirement · SHOULD · C · — · it should be maintainable and follow Pythonic conventions
- [ ] N-000026 · requirement · SHOULD · C · — · It should support cross-platform compatibility across different operating system…

## Pack 07 — 07-prd--use-cases.md

None.

## Pack 08 — 08-prd--dependencies.md

- [ ] N-000027 · requirement · MUST · L2 · — · pytest library
- [ ] N-000028 · requirement · MUST · L2 · — · flake8 library

## Pack 09 — 09-prd--usage.md

- [ ] N-000029 · requirement · MUST · — · — · #!/bin/bash # Generate a BSD3 license using default options python lice/core.py …

## Pack 10 — 10-prd--command-line-configuration-arguments.md

- [ ] N-000030 · requirement · MUST · L1 · — · Option to list all template variables for the specified license.

## Pack 11 — 11-prd--acceptance-criteria.md

- [ ] N-000031 · requirement · MUST · L1 · — · All commands must execute without errors when the correct syntax is used.
- [ ] N-000032 · requirement · MUST · L1 · — · The tool must correctly generate the license text for each specified license typ…
- [ ] N-000033 · requirement · MUST · L1 · — · Custom organization and project names must be accurately reflected in the genera…
- [ ] N-000034 · requirement · MUST · L1 · — · When a custom template path is provided, the license generated must match the cu…
- [ ] N-000035 · requirement · MUST · L1 · — · The tool must accurately format licenses according to the specified programming …
- [ ] N-000036 · requirement · MUST · L1 · — · The `--vars` option must list all the correct template variables for the specifi…

## Pack 12 — 12-prd--dependencies.md

- [ ] N-000037 · constraint · MUST · L2 · — · Python runtime environment.
- [ ] N-000038 · constraint · MUST · — · — · Access to system environment variables or `git config` for default values.
- [ ] N-000039 · constraint · MUST · — · — · Access to file system for reading custom templates and writing license files.

## Pack 13 — 13-prd--terms-concepts-explanation.md

None.

## Pack 14 — 14-uml-class--uml-class.md

- [ ] N-000040 · requirement · — · L2 · — · classDiagram class Global_functions { +main() +clean_path(p String) String +get_…

## Pack 15 — 15-uml-sequence--uml-sequence.md

- [ ] N-000041 · requirement · MUST · L2 · — · sequenceDiagram participant User participant ArgumentParser participant Global_f…

## Pack 16 — 16-architecture-design--architecture-design.md

- [ ] N-000042 · assumption · — · — · — · The design is based on the functionality as specified in the `core.py` and `_ini…
- [ ] N-000043 · requirement · MUST · L1 · — · To generate a license, run `./examples.sh` which encapsulates the commands to in…
- [ ] N-000044 · requirement · MUST · L1 · — · To run tests, the `examples.sh` script includes a command for discovering and ru…
- [ ] N-000045 · requirement · MUST · L1 · — · #! /bin/bash set -e # source /path/to/your/venv/bin/activate pip install lice li…
- [ ] N-000046 · requirement · — · L1 · — · Defines the version of the Lice package
- [ ] N-000047 · requirement · — · L2 · — · the `main()` entry point for the CLI
- [ ] N-000048 · decision · — · L2 · — · Houses the main functionality of the Lice License Generator.
- [ ] N-000049 · decision · — · L1 · — · main()`: Parses command-line arguments and invokes the appropriate functions to …
- [ ] N-000050 · decision · — · L1 · — · guess_organization()`: Attempts to determine the user's organization from git co…
- [ ] N-000051 · decision · — · L1 · — · generate_license()`: Generates the license text based on the selected template a…
- [ ] N-000052 · decision · — · L1 · — · format_license()`: Formats the license text for a specific programming language …
- [ ] N-000053 · decision · — · L2 · — · The `templates` directory contains the text templates for various licenses.
- [ ] N-000054 · requirement · MAY · L1 · — · Each license template can be used to generate the corresponding license file.
- [ ] N-000055 · requirement · MUST · L1 · — · lice [license_type] -o "Your Organization Name" -y $(date +"%Y")
- [ ] N-000056 · requirement · MUST · L1 · — · lice -l py -f [filename]
- [ ] N-000057 · requirement · MUST · L1 · — · python -m unittest discover -s ./lice/tests -p 'test_*.py'
- [ ] N-000058 · decision · — · C · — · The architecture is designed to be modular and extensible
