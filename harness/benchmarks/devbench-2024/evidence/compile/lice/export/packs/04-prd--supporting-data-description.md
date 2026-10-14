# Pack 04 — sdd/specs/PRD.md · Supporting Data Description
blocks 9 · nodes 8 (requirement 8) · AC labels: none

## Text
# Supporting Data Description

The `lice` project, aimed at automating the creation of license files for software projects, uses a set of 35 templates stored in the `templates` folder. This collection is essential for testing and validating the software's functionality in generating a variety of open-source licenses:
↳ N-000014 requirement · MUST · L2

**`./templates` Folder:**
↳ no node

- **License Templates:**
↳ no node

  - Includes a wide range of license templates, such as `template-afl3.txt`, `template-agpl3.txt`, `template-apache.txt`, `template-bsd2.txt`, `template-cc_by.txt`, and many others.
↳ N-000015 requirement · MUST · L2

  - Each template corresponds to a different type of open-source license, covering common licenses like Apache, GPL, MIT, BSD, and Creative Commons variants.
↳ N-000016 requirement · MUST · L4 ; N-000017 requirement · MUST · L4

- **Header Templates:**
↳ no node

  - Contains header templates like `template-agpl3-header.txt`, `template-apache-header.txt`, `template-cc_by-header.txt`, and more.
↳ N-000018 requirement · MUST · L2

  - These templates are designed to insert license information into the headers of source files, catering to different programming languages and file types.
↳ N-000019 requirement · MUST · L1 ; N-000020 requirement · MUST · L1

The comprehensive range of templates in the `./templates` folder allows the `lice` tool to generate license files tailored to a variety of licensing requirements, ensuring legal compliance and facilitating open-source sharing. This functionality aligns with the project's goals of simplifying license file creation and integrating seamlessly into software development workflows.
↳ N-000021 requirement · MUST · L1

## Claims to implement
- [N-000014] requirement · MUST · L2 — uses a set of 35 templates stored in the `templates` folder
  needs: none
- [N-000015] requirement · MUST · L2 — Includes a wide range of license templates, such as `template-afl3.txt`, `template-agpl3.txt`, `template-apache.txt`, `template-bsd2.txt`, `template-cc_by.txt`, and many others.
  needs: none
- [N-000016] requirement · MUST · L4 — Each template corresponds to a different type of open-source license
  needs: none
- [N-000017] requirement · MUST · L4 — covering common licenses like Apache, GPL, MIT, BSD, and Creative Commons variants
  needs: none
- [N-000018] requirement · MUST · L2 — Contains header templates like `template-agpl3-header.txt`, `template-apache-header.txt`, `template-cc_by-header.txt`, and more.
  needs: none
- [N-000019] requirement · MUST · L1 — These templates are designed to insert license information into the headers of source files
  needs: none
- [N-000020] requirement · MUST · L1 — catering to different programming languages and file types
  needs: none
- [N-000021] requirement · MUST · L1 — allows the `lice` tool to generate license files tailored to a variety of licensing requirements
  needs: none

## Acceptance criteria
None.

## Constraints in scope
- [N-000025] (pack 06) it should be maintainable and follow Pythonic conventions
plus the broad constraints in pack 01

## Related elsewhere
- N-000014 refines N-000053 (pack 16)
- N-000015 duplicates N-000053 (pack 16) The `templates` directory contains the text templates for various licenses.
- N-000015 refines N-000003 (pack 02)
- N-000015 same as N-000053 (pack 16) The `templates` directory contains the text templates for various licenses.
- N-000018 refines N-000053 (pack 16)

## Conflicts
None.

## Terms
- license — defined: "`license`: The type of license to generate."
