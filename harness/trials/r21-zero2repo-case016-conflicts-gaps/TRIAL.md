# r21-zero2repo-case016-conflicts-gaps

> Opened 2026-11-05 by Claude Code. State: **done (steps 0–8); nothing staged**.
> Update this file at every step.

## Owner's request and decisions (2026-11-05, verbatim)

Request: "round 21 run tests on case016, including the conflicts tests (similar to r18 r19) and
hallucination test (r20). Design the conflicts, add tests, generate the graph-specs export and
hallucination testing. schedule the plan to run automatically. notify me if there is anything
interrupting."

Answers to three questions asked the same day (cost estimates scaled from round 13c's case016 runs,
not measured for these specs):

| Question | Owner's answer |
|---|---|
| Conflicts and gaps in one spec or two? | "One spec (Recommended)" |
| Which export arm(s)? | "Md + compiler + oracle" (three arms: Markdown, compiler-only export, oracle export) |
| Runs per format? | "3 Sonnet, 5 Haiku" |

That request is the go-ahead for this round's model calls: **one full compile** of the planted spec
(Haiku, `sddc`) and **24 agent runs** (3 arms × (3 Sonnet + 5 Haiku)), plus the run driver's own
automatic reruns under its written rules (early-stop rerun once; rerun of a run cut off by a usage
limit), as in rounds 18–20. Any other model call needs the owner's go-ahead. No change to `src/`
(the compiler), the export format, Harbor or Zero2Repo. Contradictions that are not planted items are
judged on the owner's behalf, as in rounds 19–20.

## Question

Round 19 (case010) found that an export flagging every planted conflict helps agents name them;
round 20 (case010) found no format effect on silent invention of planted gaps. On a third, larger
case — Zero2Repo **case016** (`prosecheck`, a Python detector plus Node.js agent-plugin hooks;
18 964 words; **388** hidden tests; upstream `sloptrim`, which is not on PyPI, so agents cannot
recall it) — with conflicts and gaps planted in **one** spec:

1. **Compiler recall:** how many planted conflicts does the current compiler report? (no agent)
2. **Set 1, build quality:** does either export make the generated code worse than the Markdown, on
   the hidden tests no planted item touches (the core)?
3. **Set 2a, conflicts named** (round 19's strict rule), in each arm.
4. **Set 2b, silent inventions** on the gaps (round 20's strict rule), in each arm; lower is better.

## Arms

| Arm | Spec given | Conflicts flagged | Gaps flagged |
|---|---|---|---|
| **Markdown** | the planted Markdown | none | none |
| **Compiler export** | `sddc export` of the planted spec; contradictions that are not planted items judged false; **nothing injected** | only those the compiler found | none |
| **Oracle export** | the compiler export plus the planted conflicts the compiler missed, injected from the answer key (round 19's `oracle_store.py`) | all | none |

The compiler export answers "does `sddc` as it is help"; the oracle export is an upper bound for a
better compiler (interim report §7.1, condition 1). Neither export flags a gap, so set 2b compares
formats with no extra information.

## Design (written 2026-11-05, before any model call)

**Candidates, from test names only** (`pytest --collect-only` of the 388 hidden tests; the list stays
in the session scratchpad; no test body opened). Each candidate:

1. points at one stated fact, named by a hidden test;
2. is stated in at most 2 places (PRD and/or Interface Contract), so a gap can be removed cleanly or a
   conflict planted against it;
3. has a plausible other value (side B of a conflict; the alternative of a gap);
4. a black-box probe (`scripts/detect.py` or a hook under `hooks/`, the paths the Contract fixes) tells
   the upstream value from the other one;
5. **footprint 1–3 tests**, none shared with any other kept item (conflicts and gaps together).

**Kept:** at least 20 conflicts and at least 20 gaps (5 % of 388 = 19.4 each). If more survive, all
are kept, as rounds 17–20 kept all survivors.

**Two sets, three measures** (each reported on its own, per arm and model):

| Set | What it validates | Unit | Score |
|---|---|---|---|
| **1. Core** | the format does not make the code worse | one hidden test | passed / (388 − footprint union) |
| **2a. Conflicts named** | the agent saw both sides | one planted conflict | named / conflicts kept (strict rule of rounds 17–19) |
| **2b. Silent inventions** | the agent says when the spec is silent | one gap | silent / gaps kept (strict rule of round 20; lower is better); flagged beside it |

**Strict rules** (written before any run; as rounds 19 and 20):

- *Named* (2a): `NOTES.md`, in one place or in lines that refer to each other, states the content of
  side A, the content of side B, and presents them as disagreeing or as a choice. A conflict id or
  topic alone is not enough. Which side was built does not matter.
- *Flagged* (2b): `NOTES.md` names this point as not stated in the specification (in words) and gives
  the value assumed. Otherwise, if the code takes a value, the gap is *invented silently*. *Not built*
  (probe reads neither value) is counted apart.

**Three detection counts for conflicts** (as round 19): compiler recall; named when flagged (export
arms); named when not flagged (Markdown arm, and unflagged items of the compiler export).

**Instruction:** round 20's two notes lines, word for word, identical in all three arms
(`notes/build_task.py`).

**Rerun rule** (`trial.env`): `EARLYSTOP_RERUN=1`, `EARLYSTOP_MIN_PASSED=194` (half of 388). A run
that passed fewer than 194 **and** shows an output-limit cut or a budget/limit last message is set
aside and queued once more; a run cut off by a usage limit is rerun by the driver. Every set-aside
attempt is reported with its cost, never scored.

**Unchanged from rounds 18–20:** Harbor 0.24.0; Claude Code 2.1.316; no `--max-budget-usd`; no
thinking cap; `RUN_TIMEOUT=9000`; tools `Bash Edit Read Write`; network allow-list; models
`anthropic/claude-haiku-5-5`, `anthropic/claude-sonnet-5-5`.

**Readers.** One reader (Claude Code), not blind to format (export notes cite `CF-` ids); borderline
readings are marked; the owner audits a sheet built from the notes.

## Steps

| Step | What | Model calls |
|---|---|---|
| 0 | Set up: folder, `trial.env`, scripts, `work/base-app` (round 13c `sonnet-case016-export-2`, 388 / 388 on round 13c's task) | none |
| 1 | Test names, candidates, alternative builds, probes, probe check, footprint, selection | none |
| 2 | Plant and remove (`notes/plant.py`), checks, `ANSWER_KEY.md` | none |
| 3 | Compile the planted spec (Haiku, `sddc`), recall, verdicts, compiler export, oracle export, leak checks | one compile |
| 4 | Three tasks, `diff -r`, do-nothing check, scorer dry run, queue | none |
| 5 | Check run, then the other 23 runs, unattended (driver + watchdog cron) | 24 runs (+ driver reruns) |
| 6 | Score, read `NOTES.md` per item, audit sheet, tables | none |
| 7 | Secondary measures (`notes/hallu_static.py`) | none |
| 8 | Findings; records (register, build progress, interim report) | none |

## Step 0: set up (2026-11-05, no model call)

| Item | Done |
|---|---|
| Folder | `bash new_trial.sh r21-zero2repo-case016-conflicts-gaps "…"` |
| `trial.env` | round 20's, header changed; `EARLYSTOP_MIN_PASSED=194`; other values unchanged (`CLAUDE_VERSION=2.1.316`, `BUDGET_USD=` empty, `RUN_TIMEOUT=9000`, `EARLYSTOP_RERUN=1`) |
| Scripts copied | from round 20: `build_task.py`, `check_nop.sh`, `rescore.sh`, `footprint.sh`, `footprint.py`, `compile_full.sh`, `score.py`, `audit_sheet.py`, `probe.sh`, `hallu_static.py`, `verdicts.py`; from round 19: `oracle_store.py`, `recall.py`. Each header says what changed for round 21 |
| `work/base-app` | round 13c `sonnet-case016-export-2` `app.tgz` unpacked (the only full pass of round 13c, 388 / 388, official 1.0) |
| `work/probe-image` | `r21-probe`: `python:3.13-slim-bookworm` plus Debian's Node.js 18, so the probes can fire the hooks with no network |

## Step 1: candidates, alternative builds, probes, footprint (2026-11-05, no model call)

| Step | Command (from this folder) | Result |
|---|---|---|
| Test names | `pytest --collect-only -q tests/F0*_acceptance.py` in `python:3.13-slim` with `pytest==8.4.1`, the base build mounted | **388** names (F01–F06), kept in the session scratchpad; no test body opened |
| Candidates | from the test names, each matched to the sentences that state the fact | **25 conflict candidates** (C01–C23, C25, C26) and **22 gap candidates** (G01–G14, G19, G21, G24, G25, G30, G33, G60, G67) |
| Alternative builds | `python3 notes/sides.py work/base-app work/sides` | 47 copies, every anchor once |
| Probes | `bash notes/probe.sh <dir>` (`notes/probe.py`, black-box, image `r21-probe`, no network) | — |
| Probe check | `bash work/probe_check.sh` → `work/probe_check.log` | **base upstream on all 47; each copy alternative on its own item, upstream on the other 46: 0 mismatches** (first pass: the G24 copy's zero-count members made 6 key-presence probes read alternative; the probes now count only members with a positive count) |
| Footprint | `bash notes/footprint.sh BASE …` (three streams; Harbor oracle agent, no model), `python3 notes/footprint.py` → `notes/footprint.json` | BASE **388 / 388**. Footprint 0: C04, C05, C14, C26, G14. Over 3: C02 (4), C07 (6), G19 (7), G25 (52), G24 (205). Shared tests among the rest: C01–C03, C03–G13, C10–G05, G04–G67, C19–G60 |
| Overlap rerun | C03, G67, G60 rerun alone (first jobs kept as `work/jobs/footprint1-*`) | same footprint, same shared tests: the overlaps are real, not flaky |
| Selection | footprint 1–3, none shared; overlap rule as round 20 (G15): drop the larger footprint, on a tie drop from the kind with more survivors | **17 conflicts kept** (C01, C06, C08, C09, C11, C12, C13, C15–C23, C25; `ANSWER_KEY.md`); **16 gaps kept** (G01–G13, G21, G30, G33). Dropped for overlap: C03, C10, G60, G67. Footprint union **50**, **core 338** |

G24 ("catalogue numbers that did not fire are omitted") is stated in 3 places (PRD 87, Contract 84 and
148), more than criterion 2 allows; it has a copy and a probe but no removal in `notes/plant.py`, and
is not kept whatever its footprint.

**Shortfall against the design.** The design asked for at least 20 of each kind; criteria 1–5 leave
**17 conflicts and 16 gaps**. Decision (Claude Code, 2026-11-05, before any model call): keep the
written criteria and run with 17 + 16, rather than relax the no-shared-test rule after seeing the
footprints (that would have given 19 + 18, still under 20) or design new candidates (another
footprint pass). Set 2a is reported over 17 conflicts and set 2b over 16 gaps; each is still above
rounds 19 (15) and 20 (14). The owner was notified.

## Step 2: plant and remove (2026-11-05, no model call)

| Step | Command | Result |
|---|---|---|
| Plant | `python3 notes/plant.py work/spec-planted <33 kept items>` | **41 edits for 33 items**; every side-A and side-B phrase once, every gap key phrase absent; words 18 964 → 18 845 |
| sha256 | `work/spec-planted/` | `Full_PRD.md` 05da27a5…, `Interface_Contract.md` 546980cb…, `Hardware_Requirements.md` 11bb8c7d… (unchanged) |
| Answer key | `ANSWER_KEY.md` | kept conflicts (side A, side B, place, footprint), kept gaps (removed fact, alternative, places, footprint), the 14 dropped with reasons |

## Step 3: compile, verdicts, exports (2026-11-05)

| Step | Command | Result |
|---|---|---|
| Compile | `nohup setsid bash notes/compile_full.sh &` (store `work/compile-full`, round 13c case016 profile and lock) | **done** 2026-11-06 00:13 (-05:00), 3 passes (first two stopped at the 300-call cap and resumed): **860 calls, $3.58 est.** (sum of the three passes' `cost_usd`, `work/compile-full/compile.log`); 1 126 nodes; conflicts: 141 duplication, **67 contradiction**, 25 subsumption |
| Recall | `python3 notes/recall.py work/compile-full` → `notes/recall.json` | **9 of 17** planted conflicts found (C06, C08, C09, C11, C15, C16, C18, C21, C23). Missed: C01, C12, C13, C17, C19, C20, C22, C25. `FIND` set for C08 and C20 (their side A was cut across two nodes) |
| Atomizer omission (compiler defect, recorded, not fixed) | — | **C12's side A is in no node**: block B-000074 (PRD line 110, the false-range rule) is atomized with no node carrying the rule; round 13c's case016 store (same text hash) shows the same. The export packs still print the block's source text (and a term definition), so the agent sees side A; the conflict check cannot reach it, and the oracle cannot inject it. C12 is therefore **unflagged in both export arms** and stays in set 2a |
| Verdicts | `python3 notes/verdicts.py list work/compile-full`, then `notes/verdicts.tsv` | 67 contradictions: 10 planted pairs (left open); 21 match a round 13c pair (judged false there, reason reused); 36 read one by one against the original spec: **6 left open** (a planted side B against a second sentence stating side A: CF-000081, CF-000082 C09; CF-000086 C06; CF-000179 C23; CF-000195 C16; CF-000210 C13), **30 false**. In all **51 false, 16 open** |
| Compiler export | copy to `work/compile-compiler`, `verdicts.py apply`, `sddc --root work/compile-compiler export --allow-open --out work/export-compiler` | 40 packs, 1 126 nodes, **16 unsettled contradictions**. Planted items flagged: the 9 found, plus **C13** through CF-000210 (its side B against the domain-list sentence) = **10 of 17 flagged** |
| Oracle export | copy to `work/compile-oracle`, `python3 notes/oracle_store.py work/compile-oracle` (`RATIONALE` for the 7 injectable misses), export to `work/export-oracle` | 51 judged false; **7 injected** (C01, C13, C17, C19, C20, C22, C25 → CF-000234…CF-000240); C12 not injectable; **23 unsettled contradictions**; **16 of 17 flagged** |
| Leak checks | both exports | no `planted`, `answer key`, `oracle`, `gap`, `r21`, token prefix; no gap key phrase (`KEY`) left; both sides of every kept conflict present. Words: compiler 60 152, oracle 60 852 (all files) |

## Step 4: tasks and checks (2026-11-06, no model call)

| Step | Command | Result |
|---|---|---|
| Tasks | `notes/build_task.py` (commands in its header) | `case016-r21-markdown` (spec words 18 845), `case016-r21-export-compiler` (59 879), `case016-r21-export-oracle` (60 572) |
| `diff -r` | Markdown vs. compiler export; compiler vs. oracle export | Markdown vs. export: the spec folder, the instruction's one spec line, `task.toml` name/description. Compiler vs. oracle: `export.meta.json`, `MAP.md` and 9 packs (the injected conflicts) only. The instruction is round 20's word for word apart from that one line |
| Do-nothing check | `bash notes/check_nop.sh <task>` (nop agent) | markdown, compiler export, oracle export: **0 / 388** each |
| Scorer dry run | `notes/score.py`'s `score()` on the base build (`work/sides/BASE.tgz`, BASE footprint reward) | 388 / 388, core 338 / 338, all 33 items read `upstream` |
| Queue | `queue.tsv` | 24 rows, `hold`; first row `r21-sonnet-compiler-1` (check run), then Haiku and Sonnet interleaved across the three arms |
| Token check | `grep -rl` for the subscription token prefix over the trial folder | 0 files |

## Step 5: check run, then the queue (2026-11-06)

| Step | Result |
|---|---|
| Check run | `run_queue.sh … --one`: **r21-sonnet-compiler-1**, 1 420 s, 39 turns, **$2.18 est.**, **368 / 388**, core **334 / 338**; `NOTES.md` 45 lines (a disagreements table and an assumptions list); exposure: both sides of all 17 conflicts in tool results; token prefix in `runs/` and `work/jobs/`: 0 files |
| Scorer fix | `notes/score.py` read the transcript with `str.splitlines()`, which also splits on U+2028 / U+0085; case016's prose puts those inside JSON strings, so a line failed to parse. Now split on `\n` only. Method unchanged |
| G01 not a gap | the check run's notes cite G01's fact from FP-04; the planted spec still states it (PRD 236, "needs two hits"): the removal missed a second sentence in other words. G01 stays planted and scored but is **reported apart** (`STATED_G`); set 2b is over **15 gaps**. A term search of the planted spec for the other 15 found no other statement; G21 can be derived from two definitions and is marked *derivable* (`ANSWER_KEY.md`, last section) |
| Queue | the other 23 rows set `pending`; `nohup bash run_queue.sh r21-… >> run_queue.log &`; watchdog cron line installed (`*/10 * * * *`) |
| Usage limit (2026-11-06 02:39) | `r21-sonnet-oracle-1` was cut off by the 5-hour limit after 34 turns (**$1.81 est.**, `last message: You've hit your 5-hour limit`); the driver kept it as `work/jobs/…-r21-sonnet-oracle-1.limited-20261106T023941`, slept until 04:05 and reran it (done, 370 / 388). The cut-off attempt is not scored |
| Progress (2026-11-06 06:17) | 10 of 24 done and scored (`notes/scores.json`), 1 running, 13 pending; token prefix in `runs/`, `work/jobs/`: 0 files |
| Queue end (2026-11-06 16:52) | **24 of 24 done**; 0 early stops; **2 usage-limit cut-offs** (`r21-sonnet-oracle-1` above; `r21-sonnet-oracle-3` at 11:19 after 24 turns, **$1.56 est.**, kept as `…-r21-sonnet-oracle-3.limited-20261106T111949`, rerun after the 14:00 reset); 1 usage-guard pause (06:43–09:05, no run lost). Watchdog cron line removed after the queue ended |

## Step 6: scores and readings (2026-11-06, no model call)

| Step | Command | Result |
|---|---|---|
| Scores | `python3 notes/score.py runs/*` → `notes/scores.json` | 24 runs; token prefix in `runs/`, `work/jobs/`: 0 files |
| Scorer fix 2 | `r21-haiku-compiler-5`'s `claude-code.txt` has **two** result lines: the agent finished (63 turns), then a background command it had started timed out and woke it for one more turn. The driver and the scorer read the last line only (1 turn). Turns are now summed over the result lines; the cost is cumulative, so the last line's is kept. Only this run has two result lines |
| Readings | the one reader read every `NOTES.md` in full; one line per run in `notes/readings.txt` (named conflicts, flagged gaps, borderline remarks); `python3 notes/detection.py` → `notes/detection.tsv` (792 rows) | borderline readings are counted as **not** named / **not** flagged and named in the remarks |
| Tables | `python3 notes/tables.py` → `notes/tables.json` | below |
| Audit sheet | `python3 notes/audit_sheet.py` → `notes/detection_audit.md` | one table per item, the lines of each run's notes that match its keywords, the reading, a blank **Owner** column |

**Per arm** (core = 338 tests no planted item touches; named over 17 conflicts; silent and flagged over the 15 gaps, G01 apart; *alt* = gaps whose built value is the alternative):

| Model | Arm | Runs | Core (each) | Core mean | Named / 17 (each) | Named when flagged | Named when not flagged | Silent / 15 (each) | Flagged / 15 (each) | $ est. |
|---|---|---|---|---|---|---|---|---|---|---|
| Sonnet | Markdown | 3 | 331, 335, 333 | 333.0 | 11, 11, 14 | — | 36 / 51 | 14, 15, 12 | 1, 0, 2 | 6.38 |
| Sonnet | Compiler export | 3 | 334, 332, 336 | 334.0 | 15, 11, 15 | 26 / 30 | 15 / 21 | 14, 14, 14 | 1, 1, 1 | 5.67 |
| Sonnet | Oracle export | 3 | 334, 332, 329 | 331.7 | 13, 16, 15 | 44 / 48 | 0 / 3 | 14, 13, 13 | 1, 1, 1 | 5.33 |
| Haiku | Markdown | 5 | 316, 331, 281, 306, 330 | 312.8 | 10, 10, 11, 12, 12 | — | 55 / 85 | 11, 14, 12, 13, 12 | 4, 1, 3, 1, 3 | 3.96 |
| Haiku | Compiler export | 5 | 334, 330, 329, 327, 329 | 329.8 | 13, 14, 13, 14, 13 | 50 / 50 | 17 / 35 | 12, 13, 11, 13, 13 | 3, 2, 3, 2, 2 | 6.26 |
| Haiku | Oracle export | 5 | 323, 328, 332, 327, 324 | 326.8 | 16, 16, 16, 16, 16 | 80 / 80 | 0 / 5 | 12, 14, 13, 12, 15 | 3, 1, 2, 3, 0 | 6.82 |

The "not flagged" column of the oracle arm is C12 alone (never named by any run).

**Same items, three arms** (conflicts named, runs × items):

| Items | Model | Markdown | Compiler export | Oracle export |
|---|---|---|---|---|
| the 10 the compiler flagged | Sonnet | 21 / 30 (70 %) | 26 / 30 (87 %) | 28 / 30 (93 %) |
| | Haiku | 36 / 50 (72 %) | **50 / 50 (100 %)** | 50 / 50 (100 %) |
| the 6 only the oracle flagged | Sonnet | 15 / 18 (83 %) | 15 / 18 (83 %) | 16 / 18 (89 %) |
| | Haiku | 19 / 30 (63 %) | 17 / 30 (57 %) | **30 / 30 (100 %)** |
| C12 (no flag anywhere) | both | 0 / 8 | 0 / 8 | 0 / 8 |

**Per gap** (24 runs): flagged in G13 20 runs (assistant rows counted once per message id), G08 9, G07 6,
G10 4, G06 3; **never flagged** by any run: G02, G03, G04, G05, G09, G11, G12, G21, G30, G33. The
alternative was built in all 24 runs for G03, G04, G05, G11, G12 (and 23 / 22 / 21 for G09 / G02 /
G33): no agent thought of those points, and the value it took without a word is the one the hidden
tests reject. G10, G13, G21 and G30 were built with the upstream value in all 24 runs (the agents'
default agrees with upstream). G07 was not built (probe reads neither value) in 6 runs.

## Step 7: secondary measures (2026-11-06, no model call)

`python3 notes/hallu_static.py` → `notes/hallu_static.json` (all saved builds of rounds 13c–21).
**Fix:** round 20's rule took only top-level names as the agent's own, so case016 builds that import
sibling modules beside `scripts/detect.py` (`import extract`, `pc_chars`, `families`) were read as
third-party imports, 4 of them "not on PyPI". Every module file's own name now counts as the agent's
own. Round 20's published counts are unchanged by the fix (re-checked: all zero but one undeclared,
as before).

| Measure | Round 21 result |
|---|---|
| Imports of packages that do not exist on PyPI | **0** in every arm (after the fix) |
| Failure classes of failed hidden tests | mostly `AssertionError` (wrong value): Haiku Markdown 172, compiler 112, oracle 125; Sonnet 50 / 53 / 50. Others: `HarnessError` 27, all in one run (`r21-haiku-markdown-3`, core 281), and 1 in `r21-haiku-compiler-5`; `TimeoutExpired` 0–7 per arm |
| Upstream leakage | not measurable: `sloptrim` is not on PyPI (as the design said) |

## Step 8: findings (2026-11-06)

1. **Compiler recall 9 of 17** (53 %); with C13 caught through another sentence, the compiler export
   flags **10 of 17**. One miss is not a judging miss: the atomizer left C12's side A in no node
   (also in round 13c's store), so no conflict check could reach it. *Compiler defect, recorded, not fixed.*
2. **Set 1, build quality: no sign that either export makes the code worse.** Sonnet core means 333.0 /
   334.0 / 331.7 (Markdown / compiler / oracle); Haiku 312.8 / 329.8 / 326.8, the Markdown mean pulled
   down by two runs (281, 306). Three to five runs per cell; descriptive, no test of significance.
3. **Set 2a, conflicts named: a flag helps; the compiler export helps only where it flags.** On the 10
   conflicts the compiler flagged, naming rose from 70 % to 87 % (Sonnet) and from 72 % to 100 % (Haiku);
   on the 6 it missed, the compiler export did no better than the Markdown (83 % vs 83 %; 57 % vs 63 %),
   and the oracle's flags lifted them to 89 % and 100 %. C12, flagged nowhere, was named by no run.
   Same direction as round 19 (case010), on a third and larger case.
4. **Set 2b, silent inventions: no format effect.** Mean silent inventions out of 15: Sonnet 13.7 / 14.0
   / 13.3, Haiku 12.4 / 12.4 / 13.2. Agents flagged at most 4 of 15 gaps, mostly the same three points
   (G13, G08, G07); ten gaps were never flagged by any run in any format. Same as round 20 (case010):
   **hallucination on unstated facts is not reduced by either export**, because neither export flags a
   gap and the agents rarely say when the spec is silent.
5. **Cost:** compile **$3.58 est.**; 24 scored runs **$34.42 est.**; 2 usage-limit cut-offs **$3.37 est.**;
   total **$41.37 est.** (Claude Code's `total_cost_usd` and the compiler's `cost_usd`; subscription use,
   not billed per call).

**Limits.** One reader, not blind to format (export notes cite `CF-` ids); borderline readings are
counted against the item and listed in `notes/readings.txt`; the owner's audit sheet is
`notes/detection_audit.md`. 17 conflicts and 15 gaps (under the 20-each target, step 1); G01 reported
apart; G21 derivable. 3 Sonnet and 5 Haiku runs per arm.

## Records (2026-11-06)

- Run register (`sdd/design/rel-02/rel02_methodology_notes.md` §8): rows **174** (compile) to **200**
  (24 runs and the 2 usage-limit cut-offs, in run order).
- Build progress and interim report: see their round 21 entries.

## Files

| File | What |
|---|---|
| `ANSWER_KEY.md` | kept items, dropped candidates, G01 / G21 notes; never given to an agent |
| `notes/plant.py`, `notes/sides.py`, `notes/probe.py` | planting, alternative builds, probes |
| `notes/footprint.json`, `notes/recall.json`, `notes/verdicts.tsv` | footprint, compiler recall, verdicts |
| `notes/scores.json`, `notes/readings.txt`, `notes/detection.tsv`, `notes/tables.json` | scores, readings, per-item table, aggregates |
| `notes/detection_audit.md` | the owner's audit sheet |
| `notes/hallu_static.json` | secondary measures |
| `runs/<run>/` | each run's saved code, transcript, judge's report, `NOTES.md` |
| `run_queue.log`, `queue.tsv` | the driver's log and queue |
