# Pack 03 — sdd/specs/PRD.md · Features and Functionalities
blocks 8 · nodes 8 (requirement 8) · AC labels: none

## Text
# Features and Functionalities

`lice` offers the following features and functionalities:
↳ no node

- License Generation: Users can generate various licenses such as BSD-3, MIT, GPL, etc., with simple commands.
↳ N-000006 requirement · MAY · L1

- Customization: Allows specification of the year and organization for the generated license.
↳ N-000007 requirement · MAY · L1 ; N-000008 requirement · MAY · L1

- Integration: Tries to use `git config` or the `$USER` environment variable if the organization is not specified.
↳ N-000009 requirement · SHOULD · L1

- Formatting: Supports the creation of license headers for source files in different programming languages.
↳ N-000010 requirement · MUST · L1

- File Creation: Can generate a new source file with the license commented in the header.
↳ N-000011 requirement · MAY · L1

- Language Detection: Automatically detects the language for file formatting based on the file extension provided.
↳ N-000012 requirement · MUST · L1

- Extensibility: Users can contribute by adding support for additional licenses or programming languages.
↳ N-000013 requirement · MAY

## Claims to implement
- [N-000006] requirement · MAY · L1 — Users can generate various licenses such as BSD-3, MIT, GPL, etc., with simple commands.
  needs: none
- [N-000007] requirement · MAY · L1 — Allows specification of the year
  needs: none
- [N-000008] requirement · MAY · L1 — and organization for the generated license
  needs: none
- [N-000009] requirement · SHOULD · L1 — Tries to use `git config` or the `$USER` environment variable if the organization is not specified.
  needs: N-000008
- [N-000010] requirement · MUST · L1 — Supports the creation of license headers for source files in different programming languages.
  needs: none
- [N-000011] requirement · MAY · L1 — Can generate a new source file with the license commented in the header.
  needs: none
- [N-000012] requirement · MUST · L1 — Automatically detects the language for file formatting based on the file extension provided.
  needs: none
- [N-000013] requirement · MAY · — — Users can contribute by adding support for additional licenses or programming languages.
  needs: none

## Acceptance criteria
None.

## Constraints in scope
plus the broad constraints in pack 01

## Related elsewhere
- N-000009 duplicates N-000050 (pack 16) guess_organization()`: Attempts to determine the user's organization from git config or the USER environment variable.
- N-000009 refines N-000038 (pack 12)
- N-000009 same as N-000050 (pack 16) guess_organization()`: Attempts to determine the user's organization from git config or the USER environment variable.
- N-000029 refines N-000006 (pack 09)
- N-000043 refines N-000006 (pack 16)
- N-000055 refines N-000007 (pack 16)
- N-000056 refines N-000006 (pack 16)

## Conflicts
None.

## Terms
- license — defined: "`license`: The type of license to generate."
