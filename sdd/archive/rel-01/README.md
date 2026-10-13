# rel-01 archive — frozen at the close

> **SDD role:** `archive/` tier — read-only, binds nothing. Release 01 opened 2026-09-14 and closed
> 2026-10-01 (rel01 D42). Archived here 2026-10-11 by the owner's instruction, so that `sdd/design/`
> is empty for the next release.
> The one-page summary is the close-out: [`../../design/releases/rel01_closeout.md`](../../design/releases/rel01_closeout.md).

## What is here

| Path | What | Was at |
|---|---|---|
| [`design/rel01_brainstorm.md`](design/rel01_brainstorm.md) | The release brainstorm: goals G1–G4, sessions S1–S42, decisions rel01 D1–D42 | `sdd/design/rel01_brainstorm.md` |
| [`design/rel01_design/`](design/rel01_design/README.md) | Design notes G1–G4, the build plan (§7 progress, §8 issue log I-1 … I-97, §9 what remains), the gates M2–M4, the handover for the full compile, the 21 pilot contradictions | `sdd/design/rel01_design/` |
| `design/rel01_design/measurements/` | Raw records of the measured runs (R12, R15–R18, the M4 fixture) | `sdd/design/rel01_design/measurements/` |
| [`specs/`](specs/README.md) | **A copy** of `sdd/specs/` as it stood at the close: vision, constitution, F1–F7, ownership, template | copy of `sdd/specs/` |
| `trial_01/full-corpus/` | The first full compile of this repository's own specs (R18): spec copy, `.sdd/` store, two store backups, `graph.html`, the 16 round records | `trial_01/` at the repository root |

## Rules for reading it

- **The specs in `specs/` are a snapshot, not the specs.** The authoritative specs are in
  [`../../specs/`](../../specs/README.md) and go on being amended. If the two differ, `sdd/specs/` wins;
  the difference is what changed after rel01.
- **Paths written as text inside these files are the paths of the time.** `sdd/design/rel01_design/…`
  is now `sdd/archive/rel-01/design/rel01_design/…`; `trial_01/…` is now
  `sdd/archive/rel-01/trial_01/…`. Only clickable relative links were re-pointed when the files moved
  (20 links); no other text was changed.
- Links from the archived design notes to a spec lead to the snapshot in `specs/`, which is the text
  those notes were written against.
- `trial_01/` was compiled before F3 D38/D39 and F1 D14, so its store has no contract nodes and no term
  definitions (root `README.md` §2). The later frozen pilot graph and its export are outside the
  repository, in `~/sddc-runs/pilot-graph-R000023` and `~/sddc-runs/pilot-export-R000023`.

## What rel01 left open

Listed in the close-out ("What did not ship, and where it went") and in
`design/rel01_design/build-plan.md` §8–§9. Not copied here, so that there is one list.

Kept outside this archive because the next release continues them (owner, 2026-10-11):

- `sdd/specs/` — the live specs.
- `sdd/questions.md` — the permanent question register.
- `harness/tasks/lend-messy/` — the messy pilot task `lend`: built, not yet compiled.
