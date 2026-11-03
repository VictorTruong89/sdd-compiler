# r18-zero2repo-case006-notes-both-sides

> Opened 2026-11-02 by Claude Code. State: **scored 2026-11-02** (12 of 12 runs; Step 7 below;
> detection reading awaits the owner's audit in `notes/detection_audit.md`). Asked by the owner 2026-11-02, after round 17:
> "should we change the prompt to explicitly tell ai-agent to name both sides of the conflicts? still
> keep the strict rules", then "it's ok for a new round r18, and the proposed wording of new fixed
> prompt", then "go ahead, set up r18 with the rerun rule : Upgrade to Claude Code 2.1.316, Drop the
> budget flag, no cap thinking tokens". Update this file at every step.

## Question

Round 17 (`../r17-zero2repo-case006-conflicts-24/TRIAL.md`, step 7) left two problems:

1. The notes instruction asked for "what disagrees, where, and what you built", while the strict
   detection rule needs both sides' content. Sonnet's export notes often gave a conflict id and a topic
   only, so strict detection fell from 70.8 % (Markdown) to 36.1 % (export), although every export run
   listed all 24 conflicts.
2. A Haiku run stopped early after an output-limit cut and a misread budget reminder (round 17,
   "Why `r17-haiku-markdown-2` stopped").

With an instruction that asks for both sides, and with the run conditions below:

- **Set 1:** does the oracle export keep build quality on the 445 core tests, against the Markdown?
- **Set 2:** does the agent name both sides of each of the 24 planted conflicts, under round 17's
  strict rule unchanged?

## What changes from round 17, and what does not

| Item | Round 17 | Round 18 |
|---|---|---|
| Notes line of the instruction (both tasks, identical) | "If parts of the specification disagree, choose one and list each choice in `NOTES.md` (what disagrees, where, and what you built)." | "If parts of the specification disagree, choose one and list each disagreement in `NOTES.md`: quote or state what each side says and where it is, then what you built. A conflict id or topic alone is not enough." |
| Claude Code | 2.1.296 | **2.1.316** (npm `latest` on 2026-11-02, published 2026-10-31) |
| `--max-budget-usd` | 10 | **none** (`BUDGET_USD` empty): no budget reminder reaches the agent |
| Thinking cap | none | none (`MAX_THINKING_TOKENS` not set) |
| Early-stop rerun | none (the stopped run was left out of the means) | **automatic, once** (below) |
| Planted items, answer key, oracle export, footprint, core 445, scorer, strict rule, two sets, three counts | as round 17 | **unchanged** (copied; see Files) |
| Models, order, n | Haiku then Sonnet, Markdown and export interleaved, 3 + 3 each | the same (`queue.tsv`, 12 rows) |
| Time limits | agent 7 200 s (`task.toml`), driver 9 000 s | the same |

Three conditions change together (the instruction, the Claude Code version, the budget flag), so a
difference from round 17 cannot be put down to any one of them. Inside round 18, the Markdown and the
export arms share all of them, so the comparison between formats is still clean. Without a dollar
ceiling, a run is bounded by the agent's 7 200 s limit and the driver's usage pauses (0.90 of the
5-hour window, 0.95 of the 7-day window).

What 2.1.316 changes that matters here: after an output-limit cut *during thinking*, it sends
"Output token limit hit while you were still reasoning, before this response produced any text or tool
call. That reasoning was not kept and is not part of this conversation, so there is nothing to resume.
Continue from the conversation above: reason much more briefly and produce your answer or next tool
call well within the output limit." (2.1.296: "Output token limit hit. Resume directly [...]"). Read
from the installed 2.1.316 binary on this laptop; whether Haiku still hits the cut, and what it does
after, is *to be measured* (session logs, as round 17). Measured in step 7: Haiku still hit the cut,
and the message sent was the old "Resume directly" one.

## Rerun rule (written before any run)

`EARLYSTOP_RERUN=1`, `EARLYSTOP_MIN_PASSED=238` in `trial.env`; implemented in `../run_queue.sh`
(added 2026-11-02, off unless a trial sets it). A finished run is an **early stop** when both hold:

1. it passed fewer than 238 of the 476 hidden tests (half), and
2. its session log shows an output-limit cut (`stop_reason: max_tokens`), **or** its last message
   mentions a budget, token limit or output limit.

An early stop is set aside (job folder and `runs/` copy renamed `<run_id>.earlystop-<time>`, reason in
`work/earlystop-<run_id>`) and the row is queued **once** more; the rerun counts whatever it scores,
early stop or not. Every set-aside attempt is reported with its cost, never scored. A run that is
poor for any other reason (it built little but hit no limit and said nothing about one) is scored as
it is.

Checked offline on round 17's job folders: flags `r17-haiku-markdown-2` (0 passed; cut; "remaining
budget is small"); does not flag `r17-haiku-markdown-3` (cut, 440 passed) or `r17-sonnet-export-1`.

## Checks before model runs (no model, 2026-11-02)

| Check | Result |
|---|---|
| Tasks copied from round 17 (`work/tasks/case006-planted24-markdown`, `…-export-oracle`); `diff -r` against round 17 | only `instruction.md` lines 13–15 differ, in both tasks |
| Do-nothing run, both tasks (`notes/check_nop.sh`) | 0 tests, official 0, as round 17 |
| `run_queue.sh` after the change | `bash -n` passes; the early-stop detector tested on round 17's runs as above |
| Claude Code 2.1.316 on npm | present (`latest`; `stable` is 2.1.309) |
| Install of 2.1.316 inside Harbor's container | *not checked yet*: needs a model run. The first run is started with `--one` and read before the rest |

## Plan for the runs

Owner, 2026-11-02: "Rerun focus on sonnet that should highlight 24 conflicts with both sides. If not
all 24 conflicts, it should miss only 1 or 2 conflicts. 1) Better run 1 sonnet Export run first.
2) Check the log that expected conflicts are found. And good amount of test cases passed. 3) continue
the other 11 runs if step 2) ok. 4) score as in round 17". `r18-sonnet-export-1` moved to the top of
`queue.tsv`; started alone with `--one` at 2026-11-02 09:21.

**Gate after that run** (set by Claude Code from the owner's words, before the run finished):
continue only if (a) **at least 22 of 24 named** under the strict rule, and (b) **at least 458 of 476
tests passed** (the lowest of round 17's three Sonnet export runs: 470, 458, 465). Otherwise stop and
report to the owner.

1. `nohup setsid bash ../run_queue.sh r18-zero2repo-case006-notes-both-sides --one`: one Sonnet
   export run. Check also: `claude_code_version` 2.1.316 in `agent/claude-code.txt`; no
   `max_budget_usd` in the job's `config.json`; no `budget_usd` reminder in the session log; the
   token string absent.
2. Then the other 11 rows, detached, as round 17.
3. Scoring exactly as round 17 step 7: `python3 ../summarize.py .`, `python3 notes/score.py runs/*/`,
   `NOTES.md` read into `notes/detection.tsv` under the strict rule, three counts,
   `python3 notes/audit_sheet.py`, plus an output-limit scan of every session log.

Cost, scaled from round 17 only: $18.95 est. for the 12 scored runs there ($20.46 est. with its cut-off
attempt); round 18's is *to be measured*, and may be higher, because nothing stops a run on cost.

## Results

### Gate run `r18-sonnet-export-1` (read 2026-11-02, before the other 11 started)

| Check | Result | Source |
|---|---|---|
| Tests passed | **467 / 476** (gate ≥ 458): pass | `run_queue.log`, `runs/r18-sonnet-export-1/reward.json` |
| Named, strict rule | **24 / 24** (gate ≥ 22): pass. 22 numbered entries; #13 covers C17 + C18 and #14 covers C13 + C12, each stating both sides' content with N-ids. #13 is the tersest ("re-ask" vs "two different values abort / not asked again") but states both sides for both items | `NOTES.md` in `runs/r18-sonnet-export-1/app.tgz`, read against `ANSWER_KEY.md` |
| Claude Code version | 2.1.316 | `agent/claude-code.txt` |
| `max_budget_usd` in job `config.json` | absent | both `config.json` files |
| `budget_usd` reminder in session log | absent | `agent/sessions/` |
| `stop_reason: max_tokens` | absent | `agent/sessions/` |
| Token string | absent | grep over run, job and log |
| Turns, time, cost | 27 turns, 865 s, $2.14 est. | `run_queue.log` |

Gate passed; the other 11 rows started detached at 2026-11-02 12:13. (The run finished at 09:35; it
was read late because the assistant's wait loop matched the wrong log text, not because of the run.)

### Step 7: results (scored 2026-11-02, as round 17)

**Runs.** 12 of 12 done, 12:13–17:45 (gate run 09:21–09:35). No early stop: the rerun rule never
fired. One attempt cut off by the 5-hour usage limit, set aside and rerun by the driver:
`work/jobs/…-r18-sonnet-export-2.limited-20261102T150230` (16 turns, $1.33 est., not scored). Scored
runs $18.02 est. (`results.json`); with the cut-off attempt $19.35 est. Sources: `run_queue.log`,
`results.json`, `notes/scores.json`.

**Two sets** (set 1 = core tests passed / 445; set 2 = named under the strict rule / 24; n = 3 each):

| Arm | Core passed | Set 1 | Named | Set 2 | Mean | All 476 | Turns | $ est. |
|---|---|---|---|---|---|---|---|---|
| Haiku Markdown | 386, 383, 401 | 87.6 % | 10, 7, 9 | 36.1 % | 61.9 | 411, 406, 424 | 48, 49, 54 | 0.38, 0.53, 0.46 |
| Haiku export | 376, 419, 431 | 91.8 % | 24, 24, 24 | **100 %** | 95.9 | 400, 443, 461 | 57, 74, 77 | 0.61, 1.17, 1.88 |
| Sonnet Markdown | 439, 438, 439 | 98.6 % | 18, 18, 17 | 73.6 % | 86.1 | 468, 469, 469 | 17, 24, 23 | 2.04, 2.17, 2.13 |
| Sonnet export | 437, 437, 439 | 98.4 % | 24, 24, 24 | **100 %** | **99.2** | 467, 451, 455 | 27, 25, 27 | 2.14, 2.38, 2.13 |

Round 17 for comparison (its step 7): Haiku Markdown 95.2 % / 45.8 % (n = 2); Haiku export 96.6 % /
95.8 %; Sonnet Markdown 98.3 % / 70.8 %; Sonnet export 97.9 % / **36.1 %**.

**Three counts.**

1. Compiler recall: unchanged (oracle export flags 24/24; the compiler alone 14/24, round 17).
2. Named when flagged (export runs): **144 of 144** (6 runs × 24). Round 17: 95 of 144.
3. Named when not flagged (Markdown runs): Haiku 26 of 72, Sonnet 53 of 72 (round 17: Haiku 22 of 48,
   Sonnet 51 of 72).

**Per item, Markdown runs only** (named out of 3; the export runs named every item):

| Item | Haiku | Sonnet | | Item | Haiku | Sonnet |
|---|---|---|---|---|---|---|
| C01 | 2 | 3 | | C13 | 0 | 1 |
| C02 | 0 | 0 | | C14 | 1 | 1 |
| C03 | 2 | 3 | | C15 | 0 | 3 |
| C04 | 3 | 3 | | C17 | 0 | 0 |
| C05 | 2 | 3 | | C18 | 0 | 3 |
| C06 | 2 | 3 | | C20 | 1 | 3 |
| C07 | 3 | 3 | | C21 | 0 | 3 |
| C08 | 0 | 0 | | C22 | 0 | 2 |
| C09 | 0 | 3 | | C23 | 0 | 3 |
| C10 | 0 | 2 | | C25 | 2 | 3 |
| C12 | 2 | 3 | | C26 | 3 | 0 |
| | | | | C27 | 1 | 3 |
| | | | | C29 | 2 | 2 |

As in round 17, no Markdown run named C02, C08 or C17. Sonnet Markdown runs 2 and 3 gave a C26 entry
that states only the Contract's 45-character side (stated `B`, not named).

**Side built** (probe, `scores.json`): Sonnet export runs 2 and 3 stated the rule "the Interface
Contract wins" and built side B on 14 and 12 items; their core scores stayed 437 and 439, but their
all-476 totals fell to 451 and 455 because the footprint tests follow side A. Sonnet export run 1
and every Markdown run mostly built side A. Which side is built does not count for set 2.

**Run conditions** (all 13 job folders, including the cut-off attempt): `claude_code_version`
2.1.316 in every `claude-code.txt`; `max_budget_usd` in no job `config.json`; `budget_usd` in no
session log; token string in no file under `runs/`, `work/jobs/` or `run_queue.log`.

**Output-limit cuts** (`"stop_reason":"max_tokens"` in session logs): 4 of 6 Haiku runs, one each
(Haiku Markdown 1, 2, 3 at the 6th–8th assistant message, Haiku export 1 at the 33rd), each at
128 000 output tokens; 0 of 6 Sonnet runs. All four went on to build (406–424 and 400 tests passed).
After each cut, 2.1.316 sent "Output token limit hit. Resume directly — no apology, no recap of what
you were doing", the old message, **not** the "while you were still reasoning" message quoted above;
when 2.1.316 sends that one was not checked.

**Haiku failing tests by area** (failed per run, from `reward_detail.json` names; r18 / r17): the rise
is spread over every area rather than one feature, e.g. Markdown F03 9.0 / 4.5, F08 7.0 / 3.0,
F09 11.0 / 6.0, F12 6.3 / 1.0; export F08 10.0 / 1.7, F12 5.0 / 1.0.

## Findings

1. **The owner's target is met for Sonnet export: 24 of 24 named, with both sides, in all 3 runs**
   (round 17: 12, 1, 13). Haiku export also 24 of 24 in all 3. With the conflicts flagged and the
   instruction asking for both sides, the notes problem of round 17 is gone in this round.
2. **Without flags the instruction helps little.** Sonnet Markdown 73.6 % (round 17 70.8 %), Haiku
   Markdown 36.1 % (45.8 %). The same items stay unnamed (C02, C08, C17); the agent does not find them,
   so asking for both sides does not change them.
3. **Sonnet build quality held** (core 98.6 % Markdown, 98.4 % export; round 17 98.3 %, 97.9 %).
4. **Haiku build quality fell** (core 87.6 % Markdown, 91.8 % export; round 17 95.2 %, 96.6 %), across
   all feature areas. Three conditions changed at once (instruction, 2.1.316, no budget flag), so the
   cause cannot be named from this round; the output-limit cuts did not stop any build. Cause *to be
   measured* (for example: the same task on 2.1.296 with no budget flag, or on 2.1.316 with the
   round 17 instruction).
5. **For set 2 the format effect is now large for both models:** export 100 % against Markdown 73.6 %
   (Sonnet) and 36.1 % (Haiku). The best mean of the two sets is Sonnet export, 99.2.

## Next steps

- Owner: audit `notes/detection_audit.md` (24 item tables, 12 runs) and `notes/detection.tsv`.
- If the Haiku build drop matters: a run that changes one condition at a time (finding 4).

## Files

| Path | Tracked | What |
|---|---|---|
| `TRIAL.md` | yes | This description |
| `ANSWER_KEY.md` | yes | Copied unchanged from round 17 |
| `trial.env` | yes | Run conditions read by `../run_queue.sh` |
| `queue.tsv`, `run_queue.log` | yes | Queue state, driver log |
| `runs/<run_id>/` | yes | Per-run files, as round 17 |
| `results.json` | yes | Built by `../summarize.py` |
| `notes/plant.py`, `probe.py`, `probe.sh`, `footprint.json`, `score.py`, `check_nop.sh` | yes | Copied unchanged from round 17 |
| `notes/build_task.py` | yes | Round 17's, with the new instruction line |
| `notes/audit_sheet.py` | yes | Round 17's; title "round 18", no left-out run |
| `notes/scores.json` | yes | `python3 notes/score.py runs/r18-*/` |
| `notes/detection.tsv` | yes | The assistant's strict-rule reading of each `NOTES.md` (run, item, named, stated, flagged, built, note) |
| `notes/detection_audit.md` | yes | `python3 notes/audit_sheet.py`; for the owner's audit |
| `runs/<run_id>/NOTES.md` | yes | Extracted by `score.py` |
| `work/` | **no** | Tasks (with hidden tests), oracle export and planted spec (copies of round 17's), `recall-full.json` and `compile-oracle/oracle.json` for the audit sheet, Harbor jobs |
