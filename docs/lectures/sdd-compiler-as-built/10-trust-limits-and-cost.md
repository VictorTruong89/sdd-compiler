# 10. Trust, limits and cost

A tool that reports 381 conflicts is only useful if you know how far to believe it. This chapter
collects what has been **measured**, what has **not**, and what a run costs. Every number carries its
corpus and sample size; nothing here is extrapolated unless it says so.

## What has been measured

| Measure | Corpus | Result | Source |
|---|---|---|---|
| **Recall** — planted conflicts found | Fixture, 28 blocks, 6 planted pairs | **2 of 6** (after fixes; 1 of 6 before) | M4-gate §5 (R17) |
| **Precision** — reported conflicts judged real | Same fixture | **5 of 7 (71 %)** | M4-gate §5 |
| **Precision** | This repo's F5 + F6 specs, 181 blocks | **4 of 39 sampled (≈ 10 %)** — before the I-86 fix | M4-gate §7 |
| **Precision** | This repo's full `sdd/specs/`, 845 blocks (R18) | **not yet measured** — a seeded sample of 100 of the 381 is drawn, unadjudicated | M4-gate §8 |
| **Determinism** | Tests | A rebuild from sources + lock makes zero model calls and byte-identical files | F3 AC-3.19 |
| **Store integrity** | R18 | `check_store` clean at the end | M4-gate §8 |

**How to read this:** on plain prose the judge is decent; on a spec set dense with acceptance criteria
and decision entries it raises many false alarms, because the document's own structure (a criterion
restating its rule, a decision heading summarising its body, two criteria for two situations) reads
like contradiction and duplication. Some of that is now suppressed in code (chapter 6); the
"different situations" class is not. **Treat every conflict as a question for a person, not a
finding.** The compiler's value is in the few real ones — in the 181-block run it found a defect its
author had introduced the same day (build-plan I-80).

## Known weaknesses of the as-built graph

| Weakness | Effect | Where recorded |
|---|---|---|
| **Term proliferation** — a new name per phrasing | Related claims land in different families and may never be paired; R18 has 1 031 terms for 950 nodes | build-plan I-65, I-76 |
| **Criteria for different situations read as contradictions** | The main remaining false-positive class | I-81 |
| **High ambiguity** | 628 of 950 R18 nodes (66 %) carry at least one ambiguity entry; 304 show status `ambiguous`, the other 324 are outranked by `conflict` | M4-gate §8 |
| **A small residue of blocks that never atomize** | R18 ended with 1 block pending, retried every run | I-84 |
| **Duplicate judged links** in the store | Link counts inflated until de-duplicated | I-89 (open) |
| **`jsonschema` not declared** in `pyproject.toml` | A clean install fails on import | I-90 (open) |
| **No traversal/query command** | Agents read the store by hand (chapter 9) | F7 design only |

Three defects that would each have made R18's numbers wrong were found by R18 itself and fixed before
the run finished (I-83 id counter, I-85 dropped pairs on a stopped run, I-86 ambiguous nodes never
checked). The lesson: **a run on real data is also a test run** — read its numbers against each other
(does this run's work add up with the last one's?), not only against themselves.

## What a compile costs

Every model call on the default backend goes through Claude Code on a **subscription**, so no money
is billed per call. What the compiler records is Claude Code's own `total_cost_usd` — an estimate of
what the same calls would cost at API list price. Quote it as **estimated API-equivalent**, never as
spend (build-plan I-82).

| Corpus | Blocks | Calls | Estimated API-equivalent | Compile time |
|---|---|---|---|---|
| Fixture (R17) | 28 | 177 | $2.35 | — |
| F5 + F6 dogfood | 181 | 271 | $6.32 | — |
| **Full `sdd/specs/` (R18)** | **845** | **2 673** | **≈ $54.94** | **9.05 h, 16 runs** |

Where it goes (R18): judging pairs ≈ $25.67; describing atoms ≈ $9.05; atomizing blocks ≈ $5.50;
term questions ≈ $1.48; the remaining ≈ $13.24 went to calls whose answers were rejected and re-asked.
**The call count is the cost**: each headless call carries ≈ 22 000 tokens of Claude Code's own
harness prompt, whatever it asks.

On a subscription the practical limit is not money but the **session window**: R18 hit the limit five
times and waited for resets. Budget for a large first compile over a day; after that, edits cost only
the changed blocks and their re-checked pairs.

⚠ **Estimates made on small corpora have always been low** — 3× on the dogfood, 2× on R18 — because
real specs form more pairs per block than a fixture does. Measure on a slice of your own specs before
promising a number.

## Troubleshooting

| Symptom | Likely cause | Do |
|---|---|---|
| `exit 5` every run, pending falling | A big corpus; the cap is doing its job | Keep compiling (chapter 2 loop) |
| `exit 6 … session limit · resets 5pm` | The subscription's usage window | Wait for the reset; run again — nothing is lost |
| `exit 6 … claude is not on PATH` | Claude Code missing | Install and log in to Claude Code |
| `exit 4` naming checks | A store or profile problem | Read every named problem; do not hand-edit `.sdd/` |
| The same blocks in "failed" every run | The model keeps paraphrasing a quote | See `.sdd/review.jsonl` → `atomize_failed`; rephrasing the sentence may help (unmeasured) |
| A conflict you know is false | Judge limitations (above) | `sddc conflicts judge CF-… --verdict false --note "…"` |
| A claim "in the wrong family" | It named the thing differently | Use the existing term name in the spec text (chapter 7) |
| A `ModuleNotFoundError: jsonschema` | I-90 | `pip install jsonschema` |
