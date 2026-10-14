# Map

> ⚠ No foundation pack: no file matches `export.foundation_globs`.

## Read first

None.

## Units in build order

| Pack | File | Source · heading | Blocks | Claims | AC | Needs |
|---|---|---|---|---|---|---|
| 01 | `01-prd--introduction.md` | sdd/specs/PRD.md · Introduction | 1 | — | 0 | — |
| 02 | `02-prd--goals.md` | sdd/specs/PRD.md · Goals | 1 | requirement 5 | 0 | — |
| 03 | `03-prd--features-and-functionalities.md` | sdd/specs/PRD.md · Features and Functionalities | 13 | requirement 9 | 0 | — |
| 04 | `04-prd--supporting-data-description.md` | sdd/specs/PRD.md · Supporting Data Description | 62 | assumption 2, requirement 7 | 0 | 03 |
| 05 | `05-prd--technical-constraints.md` | sdd/specs/PRD.md · Technical Constraints | 2 | constraint 4 | 0 | 06 |
| 06 | `06-prd--dependencies.md` | sdd/specs/PRD.md · Requirements › Dependencies | 2 | requirement 2 | 0 | — |
| 07 | `07-prd--usage.md` | sdd/specs/PRD.md · Usage | 2 | requirement 1 | 0 | — |
| 08 | `08-prd--command-line-configuration-arguments.md` | sdd/specs/PRD.md · Usage › Command Line Configuration Arguments | 4 | requirement 4 | 0 | — |
| 09 | `09-prd--acceptance-criteria.md` | sdd/specs/PRD.md · Acceptance Criteria | 3 | requirement 5 | 0 | 08 |
| 10 | `10-prd--terms-concepts-explanation.md` | sdd/specs/PRD.md · Terms/Concepts Explanation | 3 | — | 0 | — |
| 11 | `11-uml-class--root.md` | sdd/specs/UML_class.md · (root) | 1 | requirement 1 | 0 | — |
| 12 | `12-uml-sequence--root.md` | sdd/specs/UML_sequence.md · (root) | 1 | requirement 1 | 0 | 03 |
| 13 | `13-architecture-design--architecture-design.md` | sdd/specs/architecture_design.md · Architecture Design | 2 | requirement 1 | 0 | — |
| 14 | `14-architecture-design--outputs.md` | sdd/specs/architecture_design.md · Architecture Design › Outputs: | 4 | assumption 2 | 0 | — |
| 15 | `15-architecture-design--hone.md` | sdd/specs/architecture_design.md · Architecture Design › Hone: | 17 | constraint 1, decision 1, requirement 13 | 0 | — |
| 16 | `16-architecture-design--license-and-readme.md` | sdd/specs/architecture_design.md · Architecture Design › License and Readme: | 3 | requirement 2 | 0 | 13 |

## Needs against the order

None.

## Contracts

- code block B-000051 (sdd/specs/PRD.md:63-80) → pack 04
- code block B-000073 (sdd/specs/PRD.md:106-122) → pack 04
- code block B-000077 (sdd/specs/PRD.md:127-140) → pack 04
- code block B-000083 (sdd/specs/PRD.md:153-158) → pack 07
- code block B-000094 (sdd/specs/UML_class.md:1-41) → pack 11
- code block B-000095 (sdd/specs/UML_sequence.md:1-23) → pack 12
- code block B-000097 (sdd/specs/architecture_design.md:5-26) → pack 13
- code block B-000118 (sdd/specs/architecture_design.md:62-67) → pack 15

## Decisions

- N-000058 (N-000058) → pack 15

## How to use

1. Read pack 00 (the foundation) first, if there is one, then each pack in the order of the table above.
2. Every id in `CHECKLIST.md` must end in one of three states: implemented, tested, or listed as
   not done with a reason.
3. Mark code with `# spec: <id>` beside what satisfies an id. Name a test after the acceptance
   criterion's label (`test_AC_4_7_…`) or the node id.
4. Fields named *derived* (layer, modality, kind, relation) were assigned by the compiler. The
   verbatim text of a block wins over them.
5. A block tagged `no node` carries spec text that formed no claim; read it, it is still the spec.

## Counts

- packs: 16
- blocks: 121
- blocks omitted: 0
- blocks excluded: 0
- blocks no node: 69
- blocks pending: 0
- nodes: 61
- nodes omitted: 0
- contracts: 0
- checklist items: 61
- unsettled contradictions: 0
