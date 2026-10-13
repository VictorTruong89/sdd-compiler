# Release 01 — Close-out

> **SDD role:** `design/` tier — NON-AUTHORITATIVE, historical. One page.
> **Status:** CLOSED · **Opened:** 2026-09-14 · **Closed:** 2026-10-01 (owner; target 2026-09-30,
> slipped by rel01 D35 until a graph was usable for generating code)

★ **rel01 in one sentence (D26, D34):** `sddc compile` turns a folder of static Markdown specs into a
checked spec graph with a report of every conflict, and `sddc export` turns that graph into files a
coding agent builds from.

## What shipped

Counts are each spec's §6 criteria; "with a test" means a passing test named in that spec's §9
traceability table. Exceptions are listed in the next table, never folded into the totals.

| Spec | Feature | ACs with a test / total | Code |
|---|---|---|---|
| F1 | Ingest: static spec files into blocks | 22 / 22 (AC-1.26 partial: the lock, not the whole run) | `src/sdd_compiler/ingest/`, `store/lock.py`, `profile.py`, `cli.py` |
| F2 | Node & layer model | 29 / 29 (AC-2.29 tested at unit level, not the integration tier it names; its row was missing from §9 and added at close) | `src/sdd_compiler/model/` |
| F3 | Atomizer | 29 / 33 | `src/sdd_compiler/atomize/`, `llm/`, `pipeline.py` |
| F4 | Graph store & views | 13 / 18 (3 of them partial) | `src/sdd_compiler/store/`, `views/` |
| F5 | Related-node retrieval | 16 / 17 | `src/sdd_compiler/retrieval/` |
| F6 | Conflict detection & report | 27 / 27 | `src/sdd_compiler/conflicts/`, `report.py` |
| F7 | Agent export | 24 / 24 | `src/sdd_compiler/export/` |
| **Total** | | **160 / 170** | |

Commands: `sddc init · ingest · compile · status · conflicts [judge] · family · export`.
**Test suite at close: 754 passing** (2026-09-30).

## What did not ship, and where it went

| Item | Why deferred | Now tracked in |
|---|---|---|
| F3 AC-3.21, AC-3.22 (never stops at a conflict; one report) | Behaviour built in T17/T18; the tests named for them were never written | F3 §9 *(to be written)* · rel02 |
| F3 AC-3.24, AC-3.25 (`sddc review accept / reject`) | `review` command deferred (build-plan B2) | F3 §9 · rel02 |
| F4 AC-4.9 … AC-4.13 (`query`); AC-4.14, 4.17, 4.18 partial (`map`); AC-4.7/4.8 via `check_store` only | `query`, `map`, `check` commands deferred (B2, M5) | F4 §9 · rel02 |
| F5 AC-5.15 (`pairs --exhaustive`) | M5 | F5 §9 · rel02 |
| Commands `blocks`, `show`, `atomize`, `check-conflicts` | B2: views on a store that exists | `sdd/specs/README.md` rel01 scope |
| **I-93: conflict precision far below its pass line** | Nine false-positive shapes named; fixes need prompt or suppression decisions | build-plan §8 I-93 · rel02 |
| I-94: 8 blocks fail atomization on every retry; CF-000390, 397 | Split re-ask paraphrases (I-84 class) | build-plan §8 I-94 · rel02 |
| Term proliferation (I-65, I-76); one-node families ≈ 67 % | Export routes around it (units from headings) | build-plan §8 · rel02 |
| F7 follow-up: the *Claims* list (120 k on the pilot) is now the largest list | Measured after D14; no decision yet | build-plan I-95 · rel02 |

## Measured, not asserted

- **Compile of this repository's own specs (R18, 2026-09-23):** 9 files, 845 blocks → 950 nodes, 381
  open conflicts; **2 673 model calls, ≈ $54.94 estimated API-equivalent** (≈ $0.065 per block,
  derived 54.94 / 845); later fix runs (I-92, I-94) 834 calls, ≈ $15.12. Every `$` here is Claude
  Code's `total_cost_usd` on the subscription, not spend (I-82).
- **Conflicts judged real by a human: 1 of 381 (0.26 %)** on R18, all adjudicated (I-93), against a
  pass line of ≥ 25 %. On the frozen pilot graph (R-000023), the 21 open contradictions without a
  current verdict were settled 2026-09-30: **2 real, 19 false** (D41) — both real ones are spec defects
  (CF-000384, now fixed; CF-000387, fixed with I-97).
- **Planted fixture (M4 gate):** 28 blocks, six planted pairs — see `M4-gate.md` for recall.
- **Export of the pilot graph (2026-09-30):** 59 packs, 932 checklist items, passes the gate without
  override; **2.94× the Markdown's characters**, largest pack 41.7 k; the build order breaks 42 of 151
  cross-spec `depends_on` links, all listed (I-95, I-96).
- **First code generated from a graph (Phase D pilot, F1, Sonnet, one run per format):** Markdown
  **26 / 26** hidden tests, $0.52 est.; export **26 / 26**, $0.70 est. The task hit the ceiling for
  both, so it cannot rank the formats; it shows the export is usable — rel01's close condition (D35).
  `docs/MIA5150-Project/pilot-F1-results.md`.

## Close checklist

- [x] Every approved spec's traceability table is current (F7 filled 2026-09-30; deferred rows say so)
- [x] `specs/README.md` index matches reality (updated at close)
- [x] Open questions moved: rel01-level ones answered in `questions.md`; carried work is the table above
- [x] `rel01_brainstorm.md` marked FROZEN

## After the close

- **2026-10-11 — archived (owner).** The brainstorm, `rel01_design/` (with `measurements/`) and
  `trial_01/` moved to [`sdd/archive/rel-01/`](../../archive/rel-01/README.md), with a snapshot of
  `sdd/specs/` as it stood. Paths written as text above are the paths of the time; "build-plan" is now
  `sdd/archive/rel-01/design/rel01_design/build-plan.md`. The specs stay live in `sdd/specs/`.
- The messy pilot task `lend` (`harness/tasks/lend-messy/`), built 2026-10-01 and not
  compiled, is carried to the next release.
