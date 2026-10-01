# Map

> ⚠ UNSETTLED: 1 contradiction(s) have no current human verdict (CF-000003). The export was made with `--allow-open`; treat them as open questions, not as spec.

## Read first

`packs/00-foundation.md` — sdd/specs/vision.md (1 blocks).

## Units in build order

| Pack | File | Source · heading | Blocks | Claims | AC | Needs |
|---|---|---|---|---|---|---|
| 00 | `00-foundation.md` | foundation | 1 | requirement 1 | 0 | — |
| 01 | `01-f1-share--1-goal.md` | sdd/specs/F1_share/spec.md · F1 — Share › 1. Goal | 1 | requirement 1 | 0 | — |
| 02 | `02-f1-share--2-rules.md` | sdd/specs/F1_share/spec.md · F1 — Share › 2. Rules | 2 | requirement 1 | 0 | — |
| 03 | `03-f1-share--3-contracts.md` | sdd/specs/F1_share/spec.md · F1 — Share › 3. Contracts | 2 | requirement 1 | 0 | — |
| 04 | `04-f1-share--4-acceptance.md` | sdd/specs/F1_share/spec.md · F1 — Share › 4. Acceptance | 1 | — | 1 | — |
| 05 | `05-f2-keep--1-goal.md` | sdd/specs/F2_keep/spec.md · F2 — Keep › 1. Goal | 1 | requirement 1 | 0 | 01 |
| 06 | `06-f2-keep--2-rules.md` | sdd/specs/F2_keep/spec.md · F2 — Keep › 2. Rules | 2 | requirement 2 | 0 | — |

## Needs against the order

None.

## Contracts

- CT-1.1 → pack 03
- code block B-06 (sdd/specs/F1_share/spec.md:11-13) → pack 03

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

- packs: 7
- blocks: 12
- blocks omitted: 1
- blocks excluded: 1
- blocks no node: 2
- blocks pending: 0
- nodes: 9
- nodes omitted: 0
- contracts: 1
- checklist items: 8
- unsettled contradictions: 1
