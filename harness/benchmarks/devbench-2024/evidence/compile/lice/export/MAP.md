# Map

> ⚠ No foundation pack: no file matches `export.foundation_globs`.

## Read first

None.

## Units in build order

| Pack | File | Source · heading | Blocks | Claims | AC | Needs |
|---|---|---|---|---|---|---|
| 01 | `01-prd--introduction.md` | sdd/specs/PRD.md · Introduction | 1 | — | 0 | — |
| 02 | `02-prd--goals.md` | sdd/specs/PRD.md · Goals | 1 | requirement 5 | 0 | — |
| 03 | `03-prd--features-and-functionalities.md` | sdd/specs/PRD.md · Features and Functionalities | 8 | requirement 8 | 0 | — |
| 04 | `04-prd--supporting-data-description.md` | sdd/specs/PRD.md · Supporting Data Description | 9 | requirement 8 | 0 | — |
| 05 | `05-prd--constraints.md` | sdd/specs/PRD.md · Constraints | 2 | constraint 1, requirement 1 | 0 | — |
| 06 | `06-prd--technical-constraints.md` | sdd/specs/PRD.md · Technical Constraints | 2 | assumption 1, requirement 2 | 0 | — |
| 07 | `07-prd--use-cases.md` | sdd/specs/PRD.md · Use Cases | 2 | — | 0 | — |
| 08 | `08-prd--dependencies.md` | sdd/specs/PRD.md · Requirements › Dependencies | 2 | requirement 2 | 0 | — |
| 09 | `09-prd--usage.md` | sdd/specs/PRD.md · Usage | 1 | requirement 1 | 0 | — |
| 10 | `10-prd--command-line-configuration-arguments.md` | sdd/specs/PRD.md · Usage › Command Line Configuration Arguments | 9 | requirement 1 | 0 | — |
| 11 | `11-prd--acceptance-criteria.md` | sdd/specs/PRD.md · Acceptance Criteria | 7 | requirement 6 | 0 | 03 |
| 12 | `12-prd--dependencies.md` | sdd/specs/PRD.md · Dependencies | 4 | constraint 3 | 0 | — |
| 13 | `13-prd--terms-concepts-explanation.md` | sdd/specs/PRD.md · Terms/Concepts Explanation | 2 | — | 0 | — |
| 14 | `14-uml-class--uml-class.md` | sdd/specs/UML_class.md · UML class | 1 | requirement 1 | 0 | — |
| 15 | `15-uml-sequence--uml-sequence.md` | sdd/specs/UML_sequence.md · UML sequence | 1 | requirement 1 | 0 | — |
| 16 | `16-architecture-design--architecture-design.md` | sdd/specs/architecture_design.md · Architecture Design | 24 | assumption 1, decision 7, requirement 9 | 0 | — |

## Needs against the order

None.

## Contracts

- code block B-000028 (sdd/specs/PRD.md:50-68) → pack 09
- code block B-000051 (sdd/specs/UML_class.md:3-54) → pack 14
- code block B-000052 (sdd/specs/UML_sequence.md:3-35) → pack 15
- code block B-000055 (sdd/specs/architecture_design.md:7-14) → pack 16
- code block B-000059 (sdd/specs/architecture_design.md:21-38) → pack 16
- code block B-000071 (sdd/specs/architecture_design.md:54-56) → pack 16
- code block B-000073 (sdd/specs/architecture_design.md:59-61) → pack 16
- code block B-000075 (sdd/specs/architecture_design.md:64-66) → pack 16

## Decisions

- N-000048 (N-000048) → pack 16
- N-000049 (N-000049) → pack 16
- N-000050 (N-000050) → pack 16
- N-000051 (N-000051) → pack 16
- N-000052 (N-000052) → pack 16
- N-000053 (N-000053) → pack 16
- N-000058 (N-000058) → pack 16

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
- blocks: 76
- blocks omitted: 0
- blocks excluded: 0
- blocks no node: 28
- blocks pending: 0
- nodes: 58
- nodes omitted: 0
- contracts: 0
- checklist items: 58
- unsettled contradictions: 0
