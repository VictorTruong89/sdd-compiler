# r19-zero2repo-case010-conflicts

> Opened 2026-11-02 by Claude Code. State: **round complete; 12 of 12 runs scored 2026-11-03** (gate run failed on set 1; the owner chose to continue).
> Asked by the owner 2026-11-02: "r19 should be similar to r18, but based on case010. same rule that
> planted conflicts quantity equal at least 5% of the test-case-number. all conflicts are covered by
> at least 1 test case. if using sdd-compiler/ cannot generate and export that highlight all
> conflicts, claude opus to appended all missing conflicts to the spec-graph export. follow same
> strict test rules. schedule for 3x haiku and 3x sonnet run (both markdown and export)." Added the
> same day: "add fixing the 20 test cases in the temporary prompt too. generate the conflicts
> unrelated to these 20 test cases." That request is the go-ahead for this round's model calls: one
> full compile of the planted spec and 12 agent runs (plus the one automatic early-stop rerun and any
> rerun of a run cut off by a usage limit). Update this file at every step.

## Question

Round 18 (`../r18-zero2repo-case006-notes-both-sides/TRIAL.md`) met the owner's target on case006:
with every planted conflict flagged in the export and the notes line asking for both sides, Sonnet
named 24 of 24 in every export run. Does that hold on a second case?

With at least 10 conflicts planted in **case010** (the `nltk` library under the name `lingora`),
each covered by 1 to 3 hidden tests outside the 20 tests that need the model files, and the model
files installed for scoring:

1. **Compiler recall:** how many of the planted conflicts does the current compiler report? (no agent)
2. **Set 1, build quality:** does the oracle export make the generated code worse than the planted
   Markdown, on the hidden tests no planted conflict touches (the core)?
3. **Set 2, detection:** does the agent name both sides of each planted conflict, from the Markdown
   and from the oracle export, under round 17's strict rule?

## The two validation sets (stated in every results table of this round)

| Set | What it validates | Unit | Score |
|---|---|---|---|
| **1. Benchmark** | the export does not make the generated code worse | one hidden test | passed / core tests (197 minus the footprint union; `ANSWER_KEY.md`) |
| **2. Detection** | the agent saw both sides of each conflict | one planted conflict | named / N kept (strict rule) |

As rounds 17 and 18: each set is reported on its own, as a percentage; inside a set every unit has
the same weight; the two sets weigh the same, and where one figure is wanted it is the plain mean of
the two percentages, reported next to both. The footprint tests belong to neither set. **The 20
model-file tests are in the core** (no planted conflict touches them; step 1 checks it).

## Detection rule (strict; written before any run)

A conflict counts as **named** in a run only if the run's `NOTES.md`, in one place or in lines that
refer to each other:

1. states the **content of side A** (the rule itself, not just a heading or a file name), and
2. states the **content of side B**, and
3. presents them as **disagreeing**, or as a choice between them.

Not enough on its own: a conflict id (`CF-…`) without both contents; stating only the side that was
built; a line that matches the topic but not the disagreement. Which side was built does not matter
for set 2. Each item is recorded as `named` (yes/no), `stated` (A, B or `-`), `built` (from the probe),
and whether the export **flagged** it (listed in its conflicts).

| Scenario | Named | Counted as |
|---|---|---|
| Missed it, whatever the side built (lucky A included) | no | a miss in set 2 |
| Saw both sides, built A | yes | detected |
| Saw both sides, built B (fails its footprint tests) | yes | detected; set 1 is unaffected |

**Three detection counts** in every results table, so a compiler miss is not read as an agent miss:

1. compiler recall: conflicts the export flags, out of 24;
2. named when flagged (export runs, flagged items);
3. named when not flagged (export runs, unflagged items; and every item in the Markdown runs).

Readings are made by Claude Code into `notes/detection.tsv`, then audited by the owner on a sheet
built from the notes (as rounds 14–16). Not blind to format: export notes cite `CF-` ids.

In this round "out of 24" in count 1 reads as "out of N", the number of kept items (`ANSWER_KEY.md`).

## Rerun rule (written before any run)

As round 18, with the threshold set for case010: `EARLYSTOP_RERUN=1`, `EARLYSTOP_MIN_PASSED=99` in
`trial.env` (half of 197, rounded up), implemented in `../run_queue.sh`. A finished run is an
**early stop** when both hold:

1. it passed fewer than 99 of the 197 hidden tests, and
2. its session log shows an output-limit cut (`stop_reason: max_tokens`), **or** its last message
   mentions a budget, token limit or output limit.

An early stop is set aside (job folder and `runs/` copy renamed `<run_id>.earlystop-<time>`, reason in
`work/earlystop-<run_id>`) and the row is queued **once** more; the rerun counts whatever it scores.
Every set-aside attempt is reported with its cost, never scored. A run that is poor for any other
reason is scored as it is.

## What changes from round 18, and what does not

| Item | Round 18 | Round 19 |
|---|---|---|
| Case | case006 (`click` as `optlyn`), 476 hidden tests | **case010** (`nltk` as `lingora`), **197** hidden tests |
| Model files for the hidden tests | none needed | **installed for the verifier phase only** (step 0b); before this, 20 of 197 could not pass |
| Planted conflicts | 24 (5 % of 476 = 23.8) | **at least 10** (5 % of 197 = 9.85); **none touches any of the 20 model-file tests** |
| Core (set 1) | 445 = 476 − 31 | 197 − footprint union (the 20 are in the core) |
| Oracle export | round 17's, copied | built in this round from this round's compile (step 3) |
| Compile | none (round 17's reused) | one full compile with the **current** compiler, no compiler change (step 2) |
| Base build, probes, footprint | round 17's | made for case010 (step 1), same method |
| Notes line of the instruction | below | **unchanged**, word for word |
| Claude Code 2.1.316, no `--max-budget-usd`, no thinking cap, rerun rule, strict rule, three counts, models, order, n | as round 18 | the same (rerun threshold 99 of 197) |
| Gate run | `r18-sonnet-export-1` first; ≥ 22 of 24 named, ≥ 458 of 476 tests | `r19-sonnet-export-1` first; **named ≥ kept − 2**, **core passed ≥ the lowest core of round 13c's four Sonnet case010 builds re-scored on the fixed task** |

Notes line (round 18's, word for word, in both tasks):

```
- If parts of the specification disagree, choose one and list each disagreement in `NOTES.md`:
  quote or state what each side says and where it is, then what you built. A conflict id or topic
  alone is not enough.
```

## Step 0b: the model files, for the verifier only (2026-11-02, no model call)

**What Zero2Repo does** (read in `benchmark/cbrun/`): `recipe_image.py` builds the case's env image by
running `fetch_resources.py` (download, size and sha256 check, zip extraction into `/opt/models`), then
the recipe's install command, which also writes a site-packages hook (`cb_models.pth` →
`cb_models_bootstrap.py`) that puts `/opt/models` first on the `path` list of any `<pkg>.data`
module. ⚠ **The prompt's premise does not hold as read:** that env image is committed and the
deliverable and **agent** images are built `FROM` it (`images.py`, `_build_dockerfile`:
`FROM {deliverable_image}`), so in Zero2Repo's own runner the agent's container does have
`/opt/models`. This round follows the owner's stricter rule instead: the files reach the verifier
only.

**How** (`notes/build_task.py`, docstring): the builder copies the manifest and the 7 archives into the
task's `tests/resources/`, plus the hook script decoded verbatim from the recipe (`cb_boot.py`);
`tests/test.sh` installs them (`tests/install_resources.py`: Zero2Repo's size, sha256 and zip checks,
no download) and runs the hook script before the judge. Harbor uploads `tests/` only in the verifier
phase, after the agent has finished (`harbor/verifier/verifier.py`, `verify`), as it does for the
hidden tests themselves.

| Check | Result | Source |
|---|---|---|
| Download, 7 archives (the manifest lists 7, not 4: the 4 models plus `stopwords`, `universal_tagset`, `words`) | 18 119 191 bytes; **every size and sha256 matches** `resources.json` | `work/resources/` |
| Task with against without the fix (`diff -r`) | only `tests/install_resources.py`, `tests/resources/`, and one hook line in `tests/test.sh` differ; `environment/`, `instruction.md`, `task.toml` identical | `work/tasks/case010-markdown-fixed`, `…-nofix` |
| Agent phase sees nothing new | an oracle `solve.sh` listing the container: no `/opt/models`, no `/tests`, no file named `*perceptron*`, no `cb_models*` | `work/jobs/check-agentview` |
| Verifier installs the files | "installed verified resource: …" for all 7 | `install_resources.log` in each job |
| Do-nothing agent on the fixed task | 0 tests, official 0 | `work/jobs/check-nop-case010-markdown-fixed` |
| Oracle with the reference solution | **not possible**: Zero2Repo ships no ground-truth project (`solution/solve.sh` copies `/solution/gt`, which is not in the repository). Replaced by the re-scores below | |
| Control: Sonnet md-2 on the task **without** the fix | 176 / 197, as round 13c | `work/jobs/rescore-NOFIX-S-md-2` |

**Round 13c's 8 saved case010 builds re-scored on the fixed task** (`bash notes/rescore.sh`, the
oracle-agent method of `footprint.sh`; no model):

| Build (round 13c) | Round 13c (no files) | Fixed task | Of the 20 model-file tests failed | Other failures |
|---|---|---|---|---|
| sonnet-case010-markdown-1 | 175 | **195** | 0 | Snowball arabic, ten languages |
| sonnet-case010-markdown-2 | 176 | **196** | 0 | Snowball arabic |
| sonnet-case010-export-1 | 176 | **196** | 0 | Snowball ten languages |
| sonnet-case010-export-2 | 175 | **195** | 0 | Snowball arabic, ten languages |
| haiku-case010-markdown-1 | 162 | 182 | 0 | 15 (classifier accuracy, naive Bayes, Lancaster, Snowball, …) |
| haiku-case010-markdown-2 | 169 | 189 | 0 | 8 |
| haiku-case010-export-1 | 168 | 188 | 0 | 9 |
| haiku-case010-export-2 | 166 | 183 | 3 | 11 |

Sources: `work/rescore.log`, `work/jobs/rescore-<label>/*/verifier/reward_detail.json`. **The fix
works:** every Sonnet build passes all 20; the only test left failing in Sonnet's builds is one or two
Snowball stem lists (as round 13c found). One Haiku build fails 3 of the 20 on its own code, a real
result now that the files are present. The Sonnet comparison for this round is **195, 196, 196, 195**
(replacing 175, 176, 176, 175).

**The hook** (control, `MODELS_HOOK=0`): Sonnet md-2 with the files but without the hook also scores
196 / 197, the same single failure (`work/jobs/rescore-NOHOOK-S-md-2`), so the hook does not change
that build's score. It is kept, so that scoring matches Zero2Repo's scoring image.

## Step 1: the planted conflicts (2026-11-02, no model call)

Same method as round 17 step 0 (`../r17-…/TRIAL.md`, "Method"), on case010.

| Step | Command (from this folder) | Result |
|---|---|---|
| Test names | `pytest --collect-only -q` on the hidden `tests/F0*_acceptance.py`, in a container with a Sonnet build | 197 names (list kept in the session scratchpad, not in the repo); no test body opened |
| The 20 model-file tests, by name | failure messages in round 13c's `final_tests.log` ("HarnessError: host resource is missing or empty: /opt/models/…"), all 8 runs | 19 by that message, plus `F03 russian_universal_succeeds_without_universal_tables_english_does_not`, failed in all 8 runs (a tagger-table test); 20, as round 13c. Left out of the candidates, with every test naming punkt, a tagger, the named-entity chunker, stopwords, a wordlist, WordNet or the command line |
| Base build | `work/base-app` = round 13c's `sonnet-case010-markdown-2` | 196 / 197 on the fixed task (step 0b); fails only `F02 snowball_arabic_named_pairs` |
| Side-B builds | `python3 notes/sides.py work/base-app work/sides` | 18 candidates, every anchor once |
| Probes | `bash notes/probe.sh <dir>` on the base and each copy | base A on all 18; each copy B on its own item, A on the other 17 (`work/probe_check.log`) |
| Footprint | `bash notes/footprint.sh BASE C01 … C26` (three streams), `python3 notes/footprint.py` | base 196 / 197 again; per item in `notes/footprint.json` |
| Selection | footprint 1–3, none among the 20, no shared test | **15 kept**: C01, C03, C04, C05, C08, C09, C11, C13, C14, C15, C16, C17, C18, C21, C22. Dropped: C02, C10, C26 (footprint 0) |
| Plant | `python3 notes/plant.py work/spec-planted <15 ids>` | 8 610 words (8 412 before); every anchor and exposure phrase once; `work/spec-planted.sha256` |

**15 of 197 = 7.6 %** (at least 10 needed). All 15 survivors are kept, as round 17 kept all its
survivors. **Footprint union 24 tests; core (set 1) = 173 tests**, the 20 model-file tests included.
Distances: same bullet 1, same file 8, across files 6 (`ANSWER_KEY.md`). Past fails: every footprint
test was passed by all 8 of round 13c's case010 builds re-scored on the fixed task.

**Gate threshold, set 1 (written before the gate run):** round 13c's four Sonnet case010 builds,
re-scored on the fixed task, fail only Snowball tests outside the union, so on round 19's core they
score 171, 172, 172, 171 of 173 (sonnet md-1, md-2, export-1, export-2). **The gate needs core ≥ 171
of 173** and **named ≥ 13 of 15** (kept − 2).

## Step 2: full compile, current compiler (2026-11-02 23:22 to 2026-11-03 00:58)

`nohup setsid bash notes/compile_full.sh` (round 17's driver, adapted: new store `work/compile-full`
by `sddc init`, round 13c's case010 profile, the planted spec, round 13c's case010 lock copied in so
questions already answered word for word replay). Compiler: this repository's `src/` at commit
`0fed585`, unchanged (no compiler change in this round).

| Pass | Calls | $ est. | Replayed answers | Pairs judged | Pairs replayed | Conflicts opened | Stop |
|---|---|---|---|---|---|---|---|
| 1 | 300 | 1.1661 | 922 | 1 536 | 0 | 66 | call cap (300); 615 pairs left |
| 2 | 86 | 0.3286 | 0 | 615 | 1 372 | 19 | none, complete |
| **Total** | **386** | **1.4947 est.** | | | | 85 | |

Source: `work/compile-full/compile-1.json`, `compile-2.json` (`model_calls`, `cost_usd`, `conflicts`).
517 nodes; the store holds 46 contradictions, 34 duplications and 5 subsumptions, all open.

**Recall: 9 of 15** (`python3 notes/recall.py work/compile-full` → `notes/recall.json`, copied to
`work/recall-full.json`). Three B sentences lost their leading `` ` `` or `*` in atomizing (C09, C17,
C21), and C01's B sentence was cut in two at ", and" (N-000505 + N-000506), so `FIND` in
`notes/plant.py` names a B substring for those four, as round 17 allowed. C01 is found through the
first half (CF-000055).

| Item | Found | Where it was lost |
|---|---|---|
| C01 | **yes** (CF-000055, A against the first half of B) | — |
| C03, C09, C11, C15, C16, C18, C21, C22 | **yes** | — |
| C04 | no | never proposed (no Q-PAIR answer quotes both sides) |
| C05 | no | proposed and judged `none` (J-005342): B's node is the fragment "longer n-grams are not scored", cut from its sentence, and the judge read it as "without saying longer than what"; the other half (N-000514) was judged `subsumes` (J-003712) |
| C08 | no | never proposed |
| C13 | no | never proposed |
| C14 | no | proposed and judged `subsumes` (J-003684, opened as subsumption CF-000035): the judge read "returns none" and "does not succeed" as the same outcome |
| C17 | no | never proposed |

Of the misses, 4 were never proposed and 2 were judged and rejected (round 17: every miss was never
proposed).

**A compiler behaviour to report (not fixed):** the atomizer cut two planted sentences at ", and" into
pieces whose second half has no subject ("nothing may be inserted or deleted between them";
"longer n-grams are not scored"). The pair judge sees each node alone, so C05's half was judged on a
fragment that does not say what it is about. **Not a code defect:** F3 D44
(`sdd/specs/F3_atomizer/spec.md`) carries a sentence's opening to its other atoms only when no atom
covers that opening, or when an atom opens with a pronoun. Here the first atom covers the opening
("When `weights` is omitted, …"; "With `transpositions=True`, …") and the second opens with "longer"
or "nothing", so the compiler did what its spec says. It is a gap in D44: a condition held by the
first atom is not carried to the second. Reported to the owner; not changed (no compiler change in
this round).

## Step 3: the oracle export (2026-11-03, no model call)

On a copy, `work/compile-oracle` (the measured store `work/compile-full` is untouched).

| Step | Command | Result |
|---|---|---|
| Verdicts | `notes/oracle_verdicts.tsv`, recorded by `notes/oracle_store.py` with `record_adjudication` | 37 contradictions that are not a found planted pair: **33 judged false** (8 reuse round 13c's verdict where the two texts are identical), **4 left open** as real second contradictions of a planted sentence (CF-000016 and CF-000070, C01 against PRD 303's second sentence; CF-000039 and CF-000072, C15 against Contract 231 and PRD 288) |
| Injection | `python3 notes/oracle_store.py work/compile-oracle` | 6 contradictions added through `write_graph`: C04 CF-000086, C05 CF-000087, C08 CF-000088, C13 CF-000089, C14 CF-000090, C17 CF-000091; judgment records kind/backend `answer-key`, model `none`, in `.sdd/lock/answer-key.jsonl`; each rationale written for its item (`RATIONALE` in the script) |
| Export | `sddc --root work/compile-oracle export --allow-open --out work/export-oracle` | 29 packs, 517 nodes, **19 unsettled contradictions** (9 found + 6 added + 4 left open) |
| Leak check | `grep -ril` for "planted", "answer key", "answer-key", "oracle", "added by hand", "round 19" | **0 files** (also none for "13c" or the token prefix; "round" only in "around") |
| Recall | `python3 notes/recall.py work/compile-oracle` | **15 of 15** (`work/recall-oracle.json`) |

C14's wrong subsumption (CF-000035) is left in the store as the compiler wrote it, beside the added
contradiction: only contradictions were judged, as the prompt asks. Called the **oracle export** in
every table.

## Step 4: tasks and checks (2026-11-03, no model call)

| Check | Result |
|---|---|
| Tasks | `work/tasks/case010-planted15-markdown` and `work/tasks/case010-planted15-export-oracle` (`notes/build_task.py`) |
| `diff -r` | only the spec folder, the instruction's spec line and the task name/description differ |
| Do-nothing (`notes/check_nop.sh`) | 0 on both |
| `notes/score.py` dry run | round 13c `sonnet-case010-markdown-2` (`work/dryrun`): 196 / 197, core 172 / 173 |
| Queue | `queue.tsv`, 12 rows: Sonnet export 1 (the gate), Haiku Markdown and export alternated ×3, Sonnet Markdown 1, 2, export 2, Markdown 3, export 3 |

## Step 5: gate run `r19-sonnet-export-1` (2026-11-03 01:04–01:13; read before any other run)

| Check | Result | Source |
|---|---|---|
| Tests passed, all 197 | 189 / 197 (reference only) | `run_queue.log`, `runs/r19-sonnet-export-1/reward.json` |
| **Core, set 1** | **168 / 173 (gate ≥ 171): FAIL** | `python3 notes/score.py runs/r19-sonnet-export-1/` |
| Named, strict rule, set 2 | **14 / 15 (gate ≥ 13): pass**. 15 conflict entries in `NOTES.md`, each with both sides and the side built, except C18: its entry gives side B ("lowercased unless preserve_case") against the emoticon exception, never side A (case preservation on by default), so it is not named | `NOTES.md` in `runs/r19-sonnet-export-1/app.tgz`, read against `ANSWER_KEY.md` |
| Sides built (probe) | A on 13; **B on C09 and C13** (the Contract side; these fail their 3 footprint tests, outside the core) | `notes/score.py` |
| Claude Code version | 2.1.316 | `agent/claude-code.txt` |
| `max_budget_usd` in job `config.json` | absent | both `config.json` files |
| `budget_usd` reminder in session log | absent | job folder |
| `stop_reason: max_tokens` | absent | job folder |
| Token string | absent | grep over run, job, `agent.tgz`, `app.tgz` and the log |
| Model files in the verifier | all 7 installed | `runs/r19-sonnet-export-1/install_resources.log` |
| Turns, time, cost | 21 turns, 548 s, $1.31 est. | `run_queue.log` |

**The 5 core failures are all F02 stemmers**, by failure message only: `lancaster_named_pairs`,
`snowball_arabic_named_pairs` (also failed by every round 13c Sonnet build), `snowball_german_…`,
`snowball_spanish_visionado`, `snowball_ten_languages_named_pairs` (wrong stems, e.g. Danish
"indflydels" for "indflyd"). The run's own `NOTES.md` says why: the 14 Snowball languages other than
English and Porter "are stemmed by a crude approximate suffix stripper", and Lancaster's "rule table
was reconstructed from memory". None is a planted item, a model-file test, or a verifier fault; it is
how much of the Snowball family this run chose to write (21 turns and 548 s; round 13c's four Sonnet
case010 runs took 21–29 turns and 704–912 s, register rows 62, 68, 74, 76).

**Gate failed; stopped as the prompt says.** The other 11 rows stay `pending` in `queue.tsv`; nothing
else was started. Decision for the owner (report, 2026-11-03).

**Owner, 2026-11-03: "continue the other 11 runs, then score them".** The gate's set-1 miss is
recorded as it is; the other 11 rows started detached at 06:17 (`../run_queue.sh "$PWD"`, no `--one`).

## Step 6: results (scored 2026-11-03, as rounds 17 and 18)

**Runs.** 12 of 12 done: the gate run 01:04–01:13, the other 11 at 06:17–11:42. At 08:41 the driver
paused for the 5-hour usage window (usage 0.99) and resumed at 11:17; no run was cut off, so no
attempt was set aside. No early stop. **$13.52 est.** for the 12 runs (`results.json`,
`notes/scores.json`). Sources: `run_queue.log`, `results.json`, `notes/scores.json`,
`notes/detection.tsv`.

**Two sets** (set 1 = core tests passed / 173; set 2 = named under the strict rule / 15; n = 3 each):

| Arm | Core passed | Set 1 | Named | Set 2 | Mean | All 197 | Turns | $ est. |
|---|---|---|---|---|---|---|---|---|
| Haiku Markdown | 151, 151, 164 | 89.8 % | 11, 6, 6 | 51.1 % | 70.4 | 164, 165, 177 | 37, 40, 41 | 0.49, 0.50, 0.57 |
| Haiku export | 157, 158, 162 | 91.9 % | 14, 14, 15 | **95.6 %** | 93.7 | 176, 167, 174 | 56, 59, 64 | 0.85, 1.02, 1.07 |
| Sonnet Markdown | 171, 165, 168 | 97.1 % | 11, 11, 8 | 66.7 % | 81.9 | 190, 184, 184 | 17, 15, 13 | 1.79, 1.34, 1.20 |
| Sonnet export | 168, 171, 164 | 96.9 % | 14, 14, 14 | **93.3 %** | **95.1** | 189, 195, 173 | 21, 25, 21 | 1.31, 1.71, 1.69 |

**Three counts.**

1. Compiler recall: **9 of 15** (step 2); the oracle export flags 15 of 15.
2. Named when flagged (export runs): **85 of 90**. The 6 added conflicts: **36 of 36**. The 9 the
   compiler found: 49 of 54. All 5 misses are C18.
3. Named when not flagged (Markdown runs): Haiku **23 of 45**, Sonnet **30 of 45**.

**Per item** (named, out of 3 runs):

| Item | Flagged by | Haiku Markdown | Sonnet Markdown | Haiku export | Sonnet export |
|---|---|---|---|---|---|
| C01 | compiler | 2 | 3 | 3 | 3 |
| C03 | compiler | 1 | 3 | 3 | 3 |
| C04 | added | 1 | 1 | 3 | 3 |
| C05 | added | 3 | 3 | 3 | 3 |
| C08 | added | 1 | 2 | 3 | 3 |
| C09 | compiler | 1 | 3 | 3 | 3 |
| C11 | compiler | 3 | 2 | 3 | 3 |
| C13 | added | 2 | 3 | 3 | 3 |
| C14 | added | 0 | 0 | 3 | 3 |
| C15 | compiler | 3 | 3 | 3 | 3 |
| C16 | compiler | 3 | 3 | 3 | 3 |
| C17 | added | 3 | 3 | 3 | 3 |
| C18 | compiler | 0 | 1 | 1 (borderline) | 0 |
| C21 | compiler | 0 | 0 | 3 | 3 |
| C22 | compiler | 0 | 0 | 3 | 3 |

**Why C18 is missed with the flag on.** The compiler flagged the right pair (CF-000054, N-000067
against N-000125), but its rationale names a different disagreement: "emoticon tokens are not
lowercased". Its quote of N-000125 also leaves out "(it is on by default)". Five of the six export
notes copy that framing and never state side A (case preservation on by default). Haiku export 3
quotes N-000125 in full, so it is counted, as borderline, for the owner's audit. A flag whose
rationale names the wrong disagreement counts as found for recall, yet it steers the agent away
from the planted difference.

**Named against built** (probe; 180 item readings):

| | Built A | Built B |
|---|---|---|
| Export, named | 56 | 29 |
| Export, not named | 5 | 0 |
| Markdown, named | 43 | 10 |
| Markdown, not named | 22 | **15** |

In the Markdown runs, 15 items were built on the planted side without the notes naming the conflict.
These are silent wrong builds: all six Markdown runs built C21 and C22 on side B unnamed (the
"recommended tokenizer" improvements). Sonnet export 3 stated the rule "the Interface Contract wins"
and built side B on 9 items; this cost its all-197 total (173), not set 2.

**Core failures** (failure names only; footprint tests excluded): mostly F02 stemmers. Sonnet: 2–8 per
run, all F02 (Snowball languages, Lancaster), except Sonnet export 3 (+5 F04 chunker). Haiku: 9–22
per run, F02 9–14 per run, plus F04, F05 or F06 in four runs. Every run's `NOTES.md` lists its
Snowball stemmers as a gap (languages other than English and Porter approximate, missing or raising);
7 of 12 also flag the Lancaster rule table (from memory, incomplete or untested).
**None of the 12 runs failed any of the 20 model-file tests.**

**Run conditions** (all 12 job folders): `claude_code_version` 2.1.316 in every `claude-code.txt`;
`max_budget_usd` in no job `config.json`; `budget_usd` in no session log; `"stop_reason":"max_tokens"`
in no session log (round 18: 4 of 6 Haiku runs); the token string in no file under `runs/`,
`work/jobs/`, `notes/` or the logs, nor inside any `agent.tgz` or `app.tgz`.

**Against round 18** (same design: oracle export, strict rule, `NOTES.md` line, CC 2.1.316, no budget
flag; different case, so only set 2 is compared). Set 2, export: Sonnet 93.3 % (round 18 100 %),
Haiku 95.6 % (100 %). The whole gap is C18. Markdown: Sonnet 66.7 % (73.6 %), Haiku 51.1 % (36.1 %).
Set 1 is not compared, because the tests differ.

## Findings

1. **When the export flags a conflict with a correct rationale, both models name it: 36 of 36 for
   the 6 added conflicts, and 49 of 54 for the 9 the compiler found.** Set 2 is 93–96 % for export
   against 51–67 % for Markdown.
2. **A flag with the wrong rationale does not help.** C18 was flagged in all 6 export runs and
   named in at most 1. Recall 9 of 15 overstates what the compiler gives the agent: one of its 9 hits
   describes a different disagreement. Recall should be read with the rationale, not just the pair.
3. **Without flags, the agents build the planted side silently.** 15 of 90 Markdown readings built B
   unnamed; C21 and C22 in all six runs. In the export runs the agent named every conflict built on
   B (0 unnamed B).
4. **The model-file fix holds**: 0 of the 20 model-file tests failed in 12 runs, and the agent never
   saw the files.
5. **Set 1 is capped by the stemmers, not by the spec format.** Sonnet core 96.9–97.1 % in both
   arms; the gate run's 168 was ordinary spread (Sonnet runs scored 164–171). The gate threshold (≥ 171),
   taken from round 13c's best builds, was set too high for n = 1.
6. **Compiler (step 2):** recall 9 of 15. 4 misses were never proposed and 2 were judged and rejected.
   C05 was judged on an atom cut away from its condition: a gap in F3 D44, reported and not changed.

## Next steps

- Owner: audit `notes/detection_audit.md` and `notes/detection.tsv` (C18 in Haiku export 3 is the
  borderline call).
- Owner decision: whether F3 D44 should carry a sentence's condition to every atom of the sentence
  (finding 6), and whether the pair judge's rationale should be checked against both quotes (finding 2).

## Files

| Path | Tracked | What |
|---|---|---|
| `TRIAL.md`, `ANSWER_KEY.md` | yes | This description; the 15 items |
| `trial.env`, `queue.tsv`, `run_queue.log`, `results.json` | yes | Run conditions, queue, driver log, `../summarize.py` output |
| `runs/<run_id>/` | yes | Per-run files, as round 18 (with `install_resources.log`) |
| `notes/build_task.py` | yes | Round 18's, plus the model files for the verifier |
| `notes/rescore.sh` | yes | Re-scores a saved build with Harbor's oracle agent (step 0b) |
| `notes/sides.py`, `probe.py`, `probe.sh`, `footprint.sh`, `footprint.py`, `footprint.json` | yes | Step 1 (round 17's method, case010) |
| `notes/plant.py` | yes | Edits, exposure phrases, `KEPT`, `FIND` |
| `notes/compile_full.sh`, `recall.py`, `recall.json` | yes | Step 2 (recall on `work/compile-full`) |
| `notes/oracle_store.py`, `oracle_verdicts.tsv` | yes | Step 3 |
| `notes/check_nop.sh`, `score.py`, `scores.json` | yes | Step 4 and step 6 |
| `notes/detection.tsv`, `detection_audit.md`, `audit_sheet.py` | yes | The strict-rule reading and the owner's audit sheet |
| `work/` | **no** | Model archives, tasks (with hidden tests), planted spec, stores, oracle export, Harbor jobs, `recall-full.json`, `recall-oracle.json` |
