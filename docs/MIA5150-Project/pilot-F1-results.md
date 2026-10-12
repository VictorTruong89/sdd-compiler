# Phase D pilot — F1 (Ingest), Sonnet, Markdown vs export

> Run 2026-09-30 by the harness in `harness/` at the repository root (sandboxed, tools `Bash, Read, Write, Edit`, ceiling
> $10 estimated API-equivalent per run). **The pilot task is excluded from reported study results**
> (G3-3 §6). One run per format: these are observations, not a comparison with any statistical weight.
> Every `$` is Claude Code's `total_cost_usd` — an estimated API-equivalent on the subscription.

| | Markdown | Export |
|---|---|---|
| Run directory (`~/sddc-runs/study-runs/`) | `f1-ingest--markdown--sonnet--20260930-235058` | `f1-ingest--export--sonnet--20260930-235415` |
| Model reported | `claude-sonnet-5-5` | `claude-sonnet-5-5` |
| Result | success | success |
| **Hidden tests** | **26 / 26** | **26 / 26** |
| Requirements by test (R1–R27 less R20) | 26 / 26 | 26 / 26 |
| Requirements left to audit | R20 (lock), R28 (no model call) | same |
| Turns | 12 | 15 |
| Time | 182 s | 186 s |
| **Est. API-equivalent $** | **0.52** | **0.70** (+36 %) |
| Input tokens: cache created / read | 44 420 / 300 178 | 71 737 / 670 674 (2.2× read) |
| Output tokens (of which thinking) | 27 737 (6 565) | 27 825 (5 414) |
| Code written (src + tests, lines of `.py`) | 1 038 | 1 063 |
| Spec it opened | `README.md`, `constitution.md`, `F1_ingest/spec.md` (not `vision.md`) | `MAP.md` and packs (read with `cat`; file-level list not recovered) |
| F1 `AC-`/`CT-` labels mentioned in its files | 10 of 26 | 14 of 26 |
| `# spec:` marks in code | 0 | 23 |
| F1 checklist ids mentioned | — | 45 of 108 |
| `OPEN_QUESTIONS.md` / `IMPLEMENTATION_NOTES.md` | 27 / 23 lines | 29 / 28 lines |
| Contamination audit (host paths) | none | none |

## What this says

1. **The export did not lose** on the hidden tests, which is G3-3 §6's condition for going on. It cost
   more to read: about 2.2× the cached input and +36 % est. API-equivalent $.
2. **The task cannot tell the formats apart: both hit the ceiling.** F1 is one clean, precise spec file
   — the case where the study's hypothesis already expects a tie. A pilot that should discriminate needs
   a messier task (scattered, duplicated, contradictory requirements across files) or finer measures
   than pass/fail tests (the R20/R28 audit, the content of `OPEN_QUESTIONS.md`).
3. **Traceability came with the export's instructions.** The export run put 23 `# spec:` marks in its
   code and mentioned 45 of the 108 F1 checklist ids; the Markdown run, whose input does not ask for
   them, put none. This is a difference in the task each format hands over, not in quality.
4. **Cost per run is far below the ceiling.** $0.52 and $0.70 against $10; the proposal's budget line
   "$ per run: to be measured" now has its first two figures for Sonnet on a one-feature task.

## Incidents (kept, not hidden)

- **First attempt aborted.** It offered every default tool, including web search, so the agent could
  have looked up this project's repository. Stopped after two spec reads (no web use), kept as
  `…--ABORTED-web-tools`; both runs restarted with the four-tool list.
- **Audit false positive.** The first audit flagged the package name `sdd-compiler`, which the spec itself
  names. Narrowed to host paths; both transcripts re-audited clean.
- **Harness crash after the export run.** The audit failed on a transcript event whose `message` was a
  string, so the export run's `run.json` was not written. Rebuilt from `transcript.jsonl` and marked
  `recovered`: exit code, stderr and wall time were lost (the transcript's own `duration_ms` is 186 346).
  Fixed in `run_task.py`.
