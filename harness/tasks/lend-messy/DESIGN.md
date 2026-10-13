# Pilot task 2 — `lend`, a tool-library loan CLI, specified messily across files

> **Status:** BUILT 2026-10-01, awaiting the owner's approval for the compile · **carried to rel-02**
> (owner, 2026-10-11: worth exploring for the study; nothing run in rel01) · study side (outside the
> compiler). Purpose: a pilot task that **can** tell the formats apart. The F1 pilot could not: one
> clean spec file, both formats 26 / 26 (`docs/MIA5150-Project/pilot-F1-results.md`). The proposal's hypothesis is that
> the graph helps on "messy, multi-file specs (duplicates, scattered refinements, contradictions)"; this
> task plants exactly those, with an answer key.

## Owner decisions (2026-10-01)

1. **Contradictions are not settled for either format.** The export is made with `--allow-open`, so it
   shows each detected contradiction as `UNSETTLED` with both quotes; the Markdown agent must find them
   itself. Hidden tests skip every contradicted value; the audit scores whether the agent noticed each
   one (0 / 1 / 2, `requirements.md`). The compiler's false conflicts (I-93) will show in the export
   too — a real effect, measured.
2. **Size as drafted:** 7 files, 12 planted items. Measured: **2 120 words, 85 blocks** (`sddc ingest`,
   no model) — under the ≈ 2 500-word target.
3. **Domain unrelated to this repository.** The first draft (`wex`, workspace exports) reused the M4
   fixture's world, whose conflict shapes the compiler was tuned on; replaced by `lend`.

## The product

`lend` — a CLI a volunteer runs on the counter laptop of a community tool library: `init`, `member add`,
`item add`, `checkout`, `renew`, `return`, `status --json`, `report --out FILE`. Dates come from
`LEND_NOW` when set, so the hidden tests move the clock. Black-box testable through the command, like
F1.

## Files

| Path | What |
|---|---|
| `spec/` | The 7 spec files the agent gets in the Markdown format: `vision.md`, `glossary.md`, `loans/spec.md`, `loans/fees.md`, `reports/spec.md`, `ops/notes.md`, `CHANGELOG.md` |
| `ANSWER_KEY.md` | The 12 planted items P1–P12, with both statements and files. Never shown to an agent |
| `requirements.md` | R1–R24 (hidden tests) and A1–A6 (audit of the contradictions and the vague item) |
| `hidden_tests/` | 24 black-box tests. **Checked:** 24 / 24 on the reference, 24 / 24 fail on a no-op, 24 / 24 through `score.py` in the sandbox |
| `reference/` | A minimal implementation that takes one side of each contradiction, only to prove the tests are passable |
| `task.md`, `inputs.json` | The task text and what each format gets; the export comes from `~/sddc-runs/lend-export` once compiled |

## Still to do, in order

1. **Compile and export (owner approval: model calls).** Copy `spec/` to a durable run directory under
   `~/sddc-runs/` as `sdd/specs/`, `sddc compile` on Haiku through the subscription, then
   `sddc export --allow-open --out ~/sddc-runs/lend-export`, frozen with a sha256 manifest.
   **Estimate, not measured:** R18's ≈ $0.065 per block (derived: $54.94 / 845) and ≈ 3.2 calls per
   block (2 673 / 845) give ≈ $5.5 and ≈ 270 calls for 85 blocks. R18's per-block figures include
   judging pairs against a 950-node graph, so this small corpus may cost less per block. The profile's
   default cap is 200 calls per run, so the compile may stop at the cap and need a second run (or a
   higher cap) to finish.
2. Two Sonnet runs, Markdown and export, same harness and ceiling ($10 estimated API-equivalent each).
3. Scoring: hidden tests by `score.py`; A1–A6 audited by the owner, blind to format where possible.
4. Compiler recall on the answer key (which planted items the compile reported) — a by-product, recorded.
