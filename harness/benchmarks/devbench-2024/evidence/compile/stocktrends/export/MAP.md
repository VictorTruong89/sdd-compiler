# Map

> ⚠ No foundation pack: no file matches `export.foundation_globs`.

## Read first

None.

## Units in build order

| Pack | File | Source · heading | Blocks | Claims | AC | Needs |
|---|---|---|---|---|---|---|
| 01 | `01-prd--introduction.md` | sdd/specs/PRD.md · Introduction | 1 | requirement 1 | 0 | — |
| 02 | `02-prd--goals.md` | sdd/specs/PRD.md · Goals | 1 | requirement 2 | 0 | — |
| 03 | `03-prd--features-and-functionalities.md` | sdd/specs/PRD.md · Features and Functionalities | 22 | requirement 14 | 0 | — |
| 04 | `04-prd--supporting-data-description.md` | sdd/specs/PRD.md · Supporting Data Description | 33 | assumption 15, requirement 1 | 0 | — |
| 05 | `05-prd--technical-constraints.md` | sdd/specs/PRD.md · Technical Constraints | 2 | constraint 2 | 0 | — |
| 06 | `06-prd--dependencies.md` | sdd/specs/PRD.md · Requirements › Dependencies | 4 | requirement 4 | 0 | — |
| 07 | `07-prd--usage.md` | sdd/specs/PRD.md · Usage | 2 | — | 0 | — |
| 08 | `08-prd--acceptance-criteria.md` | sdd/specs/PRD.md · Acceptance Criteria | 3 | requirement 3 | 2 | 03 |
| 09 | `09-prd--terms-concepts-explanation.md` | sdd/specs/PRD.md · Terms/Concepts Explanation | 4 | — | 0 | — |
| 10 | `10-uml-class--uml-class.md` | sdd/specs/UML_class.md · UML class | 1 | requirement 1 | 0 | — |
| 11 | `11-uml-sequence--uml-sequence.md` | sdd/specs/UML_sequence.md · UML sequence | 1 | requirement 1 | 0 | — |
| 12 | `12-architecture-design--architecture-design.md` | sdd/specs/architecture_design.md · Architecture Design | 22 | requirement 20 | 0 | — |

## Needs against the order

None.

## Contracts

- code block B-000065 (sdd/specs/PRD.md:89-91) → pack 07
- code block B-000073 (sdd/specs/UML_class.md:3-44) → pack 10
- code block B-000074 (sdd/specs/UML_sequence.md:3-50) → pack 11
- code block B-000076 (sdd/specs/architecture_design.md:3-23) → pack 12
- code block B-000079 (sdd/specs/architecture_design.md:28-33) → pack 12

## Decisions

None.

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

- packs: 12
- blocks: 96
- blocks omitted: 0
- blocks excluded: 0
- blocks no node: 36
- blocks pending: 0
- nodes: 66
- nodes omitted: 0
- contracts: 0
- checklist items: 66
- unsettled contradictions: 0
