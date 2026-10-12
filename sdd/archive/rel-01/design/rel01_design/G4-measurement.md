# G4 — Effectiveness measurement: the rel01 outline

> **Status:** ✅ OUTLINE APPROVED 2026-09-18 (rel01 D29), satisfying rel01 D22 · **Tier:** design, non-authoritative
> **Drafted:** 2026-09-18 · **Scope:** rel01 D26 (batch compiler over static Markdown).
> **D22 in one line:** this outline is reviewed *before* coding so the code emits what measurement
> needs; the detailed experiment is designed *after* a graph exists, against real output.

---

## 1. What "effective" means for rel01

rel01 is effective if, pointed at a real spec set, it produces a graph a person can trust and act on.
That splits into five questions, in the order they matter:

| # | Question | Why it comes first |
|---|---|---|
| **E1** | Does it **find real conflicts**? | This is the product's purpose (vision §2, purpose 1) |
| **E2** | Does it **avoid inventing** conflicts and requirements? | A tool that cries wolf is worse than none: it trains you to ignore it |
| **E3** | Is the graph **stable** — same input, same graph; small edit, small diff? | Nothing above can be trusted if the graph churns |
| **E4** | Is a compile **affordable** in time and tokens? | It decides whether it gets run at all |
| **E5** | Is the output **legible** — can a person act on the report without opening the graph? | An unread report finds nothing |

⚠ **Not in scope for rel01.** Whether a *coding agent* writes better code from a graph than from
Markdown files — the comparison in `docs/lectures/lecture-tiered-md-vs-graph.html` Parts 6–10 — needs
F7 traversal and an agent harness. rel01 only has to make that study *possible* later.

## 2. The measurements, and what each needs

| Metric | Definition | Needs |
|---|---|---|
| **M1 Conflict recall** | Of the conflicts known to exist in a corpus, how many the compiler reports | A corpus with known conflicts (§3) |
| **M2 Conflict precision** | Of the conflicts reported, how many a human agrees are real | Human adjudication of every reported conflict, recorded |
| **M3 Candidate completeness** | Of true conflict pairs, how many F5's ranked mode proposed at all | F5's exhaustive mode (`sddc pairs --exhaustive`) as the denominator |
| **M4 Atomizer stability** | Agreement between two atomization runs of the same block, lock disabled | `--no-replay` and a run-to-run diff |
| **M5 Build determinism** | Same sources + same lock ⇒ byte-identical records | Already an acceptance criterion (F3 AC-3.19, F4 AC-4.3) |
| **M6 Edit locality** | One edited paragraph changes how many nodes and how many verdicts | Run records before and after one edit |
| **M7 Cost** | Model calls, tokens and wall time per compile, and per node | F3 CT-3.2, F5 CT-5.3, F6 CT-6.2. ⚠ **Every `$` figure in this repository is Claude Code's own `total_cost_usd`, summed per call: an *estimate of the equivalent API list price*, not money billed.** These runs go through the `claude` CLI on the owner's subscription, so nothing is deducted from organization API credits and nothing appears in the Usage & Cost Admin API, which reports API traffic only. Anthropic's own docs call the Claude Code figures "estimated" (Claude Code Analytics API). Quote them as **estimated API-equivalent cost**, never as spend |
| **M8 Injection rate** | Share of nodes flagged `inferred` — content the model added | The `inferred` flag, already specified |
| **M9 Report legibility** | Can a reader, given only the report, locate and judge each conflict? | A small human trial; no instrumentation |

**Reported with each number:** the corpus, its size, the model, and the date. A metric without its
sample size is not publishable (a rule the owner's other repository learned the hard way).

## 3. Corpora

1. **This repository's own `sdd/specs/`** — 6 specs, 118 acceptance criteria, real prose written by a
   human and an AI. It is the honest first target: the compiler should find its own spec set's
   conflicts. Dogfooding also means every defect is felt immediately.
2. **A small fixture with planted conflicts** — a handful of files carrying known contradictions,
   duplications, a subsumption with differing modality, an alias pair, a unit boundary (`5 GB` vs
   `5 GiB`), and a negative constraint. It gives M1 a denominator that does not depend on anyone's
   judgement, and it doubles as the integration-test fixture.

⚠ **Planted conflicts must not look planted.** Write them in the same voice as their neighbours, or the
model will spot the seams and the numbers will flatter the tool.

## 4. Instrumentation — what the code must already emit

All of this is specified; the outline's job is to confirm it is enough before coding starts.

| Source | Carries | Serves |
|---|---|---|
| Run record (F1 CT-1.3) | run id, command, files, block counts, CLI version | M5, M6 |
| Judgment record (F3 CT-3.2) | question kind, schema version, input hash, backend, model, attempts, **usage and cost**, duration | M4, M7 |
| Retrieval counts (F5 CT-5.3) | candidates proposed, capped, dropped, replayed | M3, M7 |
| Conflict counts (F6 CT-6.2) | pairs judged and replayed, verdicts by kind, conflicts opened and closed, calls | M1, M2, M7 |
| Node flags (F2) | `inferred`, ambiguity kinds, `low_confidence_verdict` | M8, M2 |
| `--json` on every command | machine-readable everything | all |

**Two gaps, and the decision for each:**

- **Adjudication is not recorded anywhere.** M2 needs a human verdict per reported conflict, kept
  across runs. *Proposal:* a tiny `sddc conflicts judge CF-000003 --verdict real|false --note "…"`
  writing `.sdd/adjudications.jsonl`. Roughly one acceptance criterion; it is the only new code G4 asks
  for, and without it precision can never be measured. **Decide this now** — retrofitting it after the
  first compiles means re-judging everything.
- **Agent-side reading logs do not exist** (rel01 has no hooks). Any later study of how an agent uses
  the graph must take them from the agent's own transcript or telemetry, not from this compiler.

## 5. When each measurement happens

> **First M7 data point, 2026-09-18** (see rel01 S19): a headless Claude Code call carries ~22k tokens of
> harness prompt, so a one-block question costs ≈ $0.012 and ≈ 5 s in steady state. Per-call overhead,
> not question size, sets the cost of a compile.

| When | Measurement |
|---|---|
| As acceptance criteria, during the build | M5 determinism, and M6 locality on the fixture |
| First real compile of `sdd/specs/` | M7 cost, M8 injection rate, M4 stability |
| After the first compile, with the fixture | M1 recall, M3 candidate completeness |
| After a human reads one real report | M2 precision, M9 legibility |

**The one number for the 30 September close:** *conflicts reported on this repository's own spec set,
and how many of them a human judged real.* Everything else is supporting evidence.

## 6. What this outline deliberately does not fix

Thresholds and weights (F5 D6 calls them starting values), how many conflicts count as "good", and any
comparison against another tool or another representation. Those need the detailed design, written
once real output exists — which is exactly what D22 says.
