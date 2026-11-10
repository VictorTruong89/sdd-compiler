# r22-llm-review-baseline

> Opened 2026-11-08. State: **closed** 2026-11-09 (18 of 18 runs scored). Approved by the owner 2026-11-08: "do your #1 suggested task
> above" (the plain-LLM review baseline proposed that day). Update this file at every step; it is the
> description a later session starts from.

## Question

Does a plain LLM review, asked only to list the contradictions in a spec, find the planted conflicts
as well as `sddc` does, and at what precision and cost?

*Why:* the compiler's value to the report rests on finding conflicts. The obvious objection is that a
coding model asked directly ("list every contradiction") might do as well for less. Rounds 17, 19 and 21
already have answer keys and the compiler's recall and precision on the same planted text, so the
comparison costs only the review runs.

## Design

| Item | Value |
|---|---|
| Benchmark / case | Zero2Repo case006 (24 planted conflicts, round 17/18 key), case010 (15, round 19 key), case016 (17 conflicts + 16 removed facts, round 21 key; gaps not scored) |
| Input | The planted Markdown exactly as the coding agents' Markdown arm read it (`diff -r` identical, step 1) |
| Formats | Markdown only. The task is review, not coding |
| Models | Haiku 5.5 (the compiler's model) and Sonnet 5.5 |
| Runs per cell (n) | 3 → 18 runs |
| Agent | Claude Code 2.1.316, Harbor, the same disallowed tools as rounds 18–21, network allow-list `api.anthropic.com` only, no dollar ceiling, no thinking cap |
| Instruction | `work/tasks/review-<case>/instruction.md` (in `notes/build_review_task.py`): list every disagreement in `CONFLICTS.md`, each with what both sides say and where; no code; no missing information or style |
| Scorer | Reading `CONFLICTS.md` against the answer key (rule below). One reader (Claude, not blind to the key) |

### Scoring rule (written before any run)

1. **Recall (found).** A planted item is *found* when `CONFLICTS.md`, in one entry or in entries that
   refer to each other, states the content of side A and of side B (quoted or paraphrased so each is
   identifiable) and presents them as disagreeing. This is the strict *named* rule of rounds 17–21's
   set 2a. A borderline reading counts as **not** found and is named in the notes.
2. **Entries.** Each disagreement the file lists (a numbered or bulleted entry, or a table row) is one
   entry. An entry that bundles several disagreements counts once per distinct pair of statements.
3. **Precision.** Each entry is read as one of: *planted* (matches an item), *real-other* (a
   disagreement that holds in the planted text — e.g. a planted side against a second original
   sentence, or a genuine contradiction in the original spec), *false* (a rule and its stated exception,
   two cases, two modes, two senses of a word), *not a conflict* (a gap, unclear wording, style).
   Precision = (planted + real-other) / entries. Several entries matching one planted item count once
   for recall and each as planted for precision.
4. **Comparison.** The compiler's numbers on the same text (`TRIAL.md` of rounds 17, 19, 21): recall
   14 / 24, 9 / 15, 9 / 17; contradictions judged real 18 / 69, 13 / 46, 16 / 67 (verdicts "on the
   owner's behalf", same kind of reader as here); compile $2.89, $1.49, $3.58 est. (Haiku). The coding
   agents' naming from the same Markdown while building (set 2a, Markdown arm) is a second comparison.
5. Cost and time are Claude Code's `total_cost_usd` and Harbor's agent time, as in every round.

## Inputs (how each was made; commands)

| Step | Command | Result |
|---|---|---|
| 1. Tasks | `python3 notes/build_review_task.py` | `work/tasks/review-case006`, `-case010`, `-case016`; each `spec/` `diff -r` identical to r18 `case006-planted24-markdown`, r19 `case010-planted15-markdown`, r21 `case016-r21-markdown`; Dockerfile copied from the same tasks; 41 890 words in the three specs together |
| 2. Queue | `queue.tsv` | 18 rows; `r22-sonnet-case016-1` first as the gate run |
| 3. Leak check | `grep -r -i -E "planted\|oracle\|answer key\|r1[0-9]\|r2[0-9]\|\bC[0-9][0-9]\b"` over the tasks' instructions and `spec/` | nothing found |

## Checks before model runs (no model)

- Spec copies identical to the agents' Markdown arms (step 1).
- No answer-key text, "planted", "oracle", round id or item id in any task's `spec/` or instruction
  (step 3).

## Runs

Queue in `queue.tsv`; log in `run_queue.log`; files per run in `runs/<run_id>/` (`CONFLICTS.md`
saved by the verifier); `python3 ../summarize.py .` builds `results.json`.

| Step | What | Result |
|---|---|---|
| Gate run | `run_queue.sh … --one`: `r22-sonnet-case016-1`, 2026-11-08 23:00 (-05:00) | 148 s, 9 turns, $0.36 est.; `CONFLICTS.md` saved (16 entries); token string in no file under `runs/` or `work/jobs/`. Read at once: 16 / 17 found, 16 / 16 entries correct |
| Queue | `run_queue.sh` (the other 17), 23:02 – 00:25 | 17 done, 0 retried, 0 limited, 0 failed; token string in no file; subscription 7-day window 0.84 → 0.86 |
| Readings | one reader, every `CONFLICTS.md` in full; `notes/readings.md`; data in `notes/score.py` | 18 runs, 319 entries |
| Scores | `python3 notes/score.py` → `notes/scores.json` | tables below |

## Results

| Case | Model | Found per run | Mean recall | Correct entries / entries | Precision | $ est. per run | s per run |
|---|---|---|---|---|---|---|---|
| case006 (24) | Haiku | 22 · 20 · 23 | 90.3 % | 65 / 72 | 90.3 % | 0.02–0.04 | 154–225 |
| | Sonnet | 20 · 20 · 21 | 84.7 % | 61 / 62 | 98.4 % | 0.22–0.23 | 116–122 |
| | **compiler** (Haiku, round 17) | 14 (1 compile) | 58.3 % | 18 / 69 contradictions | 26.1 % | 2.89 (757 calls) | — |
| case010 (15) | Haiku | 13 · 13 · 13 | 86.7 % | 40 / 42 | 95.2 % | 0.02–0.03 | 134–184 |
| | Sonnet | 13 · 13 · 12 | 84.4 % | 39 / 39 | 100 % | 0.16–0.18 | 105–115 |
| | **compiler** (round 19) | 9 | 60.0 % | 13 / 46 | 28.3 % | 1.49 (386 calls) | — |
| case016 (17) | Haiku | 15 · 16 · 15 | 90.2 % | 49 / 57 | 86.0 % | 0.08–0.12 | 287–347 |
| | Sonnet | 16 · 15 · 16 | 92.2 % | 47 / 47 | 100 % | 0.32–0.36 | 141–148 |
| | **compiler** (round 21) | 9 | 52.9 % | 16 / 67 | 23.9 % | 3.58 (860 calls) | — |

**All three cases:** Haiku review recall 150 / 168 (89.3 %), precision 154 / 171 (90.1 %); Sonnet
review recall 146 / 168 (86.9 %), precision 147 / 148 (99.3 %); the compiler recall 32 / 56 (57.1 %),
contradictions judged real 47 / 182 (25.8 %). Total cost of the 18 review runs: **$2.67 est.**

**Per item** (`notes/scores.json`, `items`):
- **Found by the compiler, by no review run: C21 and C22 of case010** (two exceptions stated in the
  "recommended tokenizer's improvements" bullet list, each contradicting a rule a few lines earlier: PRD 112 vs 105, PRD 108 vs 100). The
  coding agents never named them from the Markdown either (round 19, 0 of 6).
- Found by every review run, missed by the compiler: case006 C01 C10 C12 C20 C23 C25 C29; case010
  C04 C05 C08 C13 C17; case016 C17 C19 C20 C22 C25 (17 items).
- Every other item was found by at least one review run. Sonnet missed case006 C03 and C17 in all
  three runs; Haiku found both in two and three runs. C17 (case006) is one the coding agents never
  named from the Markdown (0 of 11), and the compiler found it.
- Real disagreements of the **original** spec that the reviewers found and the key does not hold: 3
  (case010: nonterminal symbol type; case016: "at most one file operand", the `.pdf` row message).

## Findings

1. **A plain review finds more planted conflicts than the compiler, at higher precision, for less.**
   On all three cases and both models, recall 84–92 % per cell against the compiler's 53–60 %;
   precision 86–100 % against 24–28 %; $0.02–0.36 est. per review against $1.49–3.58 est. per compile.
2. **Sonnet is the cleaner reviewer, Haiku the wider one.** Sonnet made 1 false entry in 148; Haiku
   17 in 171 (mostly a rule read against its own stated exception), and found slightly more items.
3. **The compiler is not dominated on every item.** C21 and C22 of case010 were found only by the
   compiler. Its pairwise checks reach two sentences that a whole-document read passes over.
4. **A dedicated review beats naming while coding.** The same models, reading the same Markdown while
   building, named 36.1 % (Haiku) and 73.6 % (Sonnet) of case006's 24 in round 18, and about 65–71 % of
   case016's 17 in round 21. Asked only to review, they found 85–92 %.

**What this does not show.** One reader, not blind to the key, read both the review entries and (in
rounds 17–21) the compiler's verdicts; the compiler's precision counts contradictions only (it also
raises duplications and subsumptions), the review's counts every entry. One compile per case against
three reviews per cell. The planted conflicts were written to be findable by a careful reader in the
spec's voice; on a spec larger than one model context (these are 8 000–19 000 words) a single review
pass is not possible as run here, which is the case the compiler's incremental design is for — *not
measured*. The instruction named the task exactly; the compiler is a general tool that also builds the
graph and the export.

## Open items

- A **review-list arm**: hand the coding agent the Markdown plus a review's `CONFLICTS.md`, the cheap
  counterpart of the compiler export's flags. Not run.
- A spec larger than one context, where a single review pass cannot read everything at once.

## Files

| Path | Tracked | What |
|---|---|---|
| `TRIAL.md` | yes | This description |
| `trial.env` | yes | Run conditions read by `../run_queue.sh` |
| `queue.tsv`, `run_queue.log` | yes | Queue state, driver log |
| `runs/<run_id>/` | yes | `result.json`, `reward.json`, `CONFLICTS.md`, `agent.tgz` (transcript) |
| `results.json` | yes | Built by `../summarize.py` |
| `notes/` | yes | Task builder, readings, scores |
| `work/` | **no** | Tasks (with the planted spec), Harbor jobs |
