# Pack 09 — sdd/specs/PRD.md · Usage
blocks 1 · nodes 1 (requirement 1) · AC labels: none

## Text
# Usage

```bash
#!/bin/bash

# Generate a BSD3 license using default options
python lice/core.py bsd3

# Generate an MIT license using default options
python lice/core.py mit

# Generate a GPL3 license for the year 2021 and organization 'ExampleOrg'
python lice/core.py gpl3 --year 2021 --org 'ExampleOrg'

# Generate an Apache license with a header formatted for a Python source file
python lice/core.py apache --header --language py

# Generate a BSD2 license and save it to a file named 'LICENSE'
python lice/core.py bsd2 --file LICENSE

```
↳ N-000029 requirement · MUST

## Claims to implement
- [N-000029] requirement · MUST · — — #!/bin/bash
    
    # Generate a BSD3 license using default options
    python lice/core.py bsd3
    
    # Generate an MIT license using default options
    python lice/core.py mit
    
    # Generate a GPL3 license for the year 2021 and organization 'ExampleOrg'
    python lice/core.py gpl3 --year 2021 --org 'ExampleOrg'
    
    # Generate an Apache license with a header formatted for a Python source file
    python lice/core.py apache --header --language py
    
    # Generate a BSD2 license and save it to a file named 'LICENSE'
    python lice/core.py bsd2 --file LICENSE
  needs: none

## Acceptance criteria
None.

## Constraints in scope
plus the broad constraints in pack 01

## Related elsewhere
- N-000029 refines N-000006 (pack 03)
- N-000029 refines N-000032 (pack 11)

## Conflicts
None.

## Terms
- license — defined: "`license`: The type of license to generate."
