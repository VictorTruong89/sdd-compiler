# Map

> ⚠ UNSETTLED: 2 contradiction(s) have no current human verdict (CF-000003, CF-000006). The export was made with `--allow-open`; treat them as open questions, not as spec.

> ⚠ No foundation pack: no file matches `export.foundation_globs`.

## Read first

None.

## Units in build order

| Pack | File | Source · heading | Blocks | Claims | AC | Needs |
|---|---|---|---|---|---|---|
| 01 | `01-uml-class--uml-class.md` | sdd/specs/UML_class.md · UML class | 3 | requirement 1 | 0 | — |
| 02 | `02-prd--introduction.md` | sdd/specs/PRD.md · Introduction | 1 | requirement 1 | 0 | — |
| 03 | `03-prd--goals.md` | sdd/specs/PRD.md · Goals | 1 | requirement 1 | 0 | — |
| 04 | `04-prd--features-and-functionalities.md` | sdd/specs/PRD.md · Features and Functionalities | 27 | assumption 1, constraint 2, requirement 13 | 0 | 01, 03 |
| 05 | `05-prd--technical-constraints.md` | sdd/specs/PRD.md · Technical Constraints | 3 | constraint 2, requirement 1 | 0 | — |
| 06 | `06-prd--dependencies.md` | sdd/specs/PRD.md · Requirements › Dependencies | 3 | requirement 2 | 0 | — |
| 07 | `07-prd--usage.md` | sdd/specs/PRD.md · Requirements › Usage | 3 | constraint 1, requirement 4 | 0 | 08 |
| 08 | `08-prd--command-line-arguments-script-input.md` | sdd/specs/PRD.md · Requirements › Command Line Arguments (Script input) | 7 | requirement 4 | 0 | — |
| 09 | `09-prd--acceptance-criteria.md` | sdd/specs/PRD.md · Acceptance Criteria | 4 | — | 4 | 04 |
| 10 | `10-prd--terms-concepts-explanation.md` | sdd/specs/PRD.md · Terms/Concepts Explanation | 2 | — | 0 | — |
| 11 | `11-uml-sequence--uml-sequence.md` | sdd/specs/UML_sequence.md · UML sequence | 3 | requirement 1 | 0 | — |
| 12 | `12-architecture-design--architecture-design.md` | sdd/specs/architecture_design.md · Architecture Design | 22 | constraint 2, requirement 15 | 0 | — |

## Needs against the order

None.

## Contracts

- code block B-000010 (sdd/specs/PRD.md:15-17) → pack 04
- code block B-000037 (sdd/specs/PRD.md:55-64) → pack 07
- code block B-000053 (sdd/specs/UML_class.md:3-14) → pack 01
- code block B-000054 (sdd/specs/UML_class.md:16-27) → pack 01
- code block B-000056 (sdd/specs/UML_sequence.md:3-20) → pack 11
- code block B-000057 (sdd/specs/UML_sequence.md:22-39) → pack 11
- code block B-000059 (sdd/specs/architecture_design.md:3-13) → pack 12
- code block B-000065 (sdd/specs/architecture_design.md:22-32) → pack 12
- code block B-000067 (sdd/specs/architecture_design.md:35-43) → pack 12
- code block B-000069 (sdd/specs/architecture_design.md:45-54) → pack 12

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
- blocks: 79
- blocks omitted: 0
- blocks excluded: 0
- blocks no node: 32
- blocks pending: 0
- nodes: 55
- nodes omitted: 0
- contracts: 0
- checklist items: 55
- unsettled contradictions: 2
