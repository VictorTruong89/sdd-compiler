# r20-zero2repo-case010-gaps

> Opened 2026-11-04 by Claude Code, from the session prompt `harness/trials/r20_session_prompt.md`
> (written 2026-11-04). State: **round complete (2026-11-05)**.
> Update this file at every step.

## Owner's approval (2026-11-04, verbatim)

"approve all those steps above." For this round only, that approves:

1. the **new instruction sentence** below (a change from rounds 18–19), the same in both formats;
2. model calls: **one compile** of the gapped case010 spec (Haiku, `sddc`; ≈ $0.3–1.5 est., to be
   measured) and **12 agent runs** (≈ $13.5 est. at round 19's rate), plus the run driver's own
   automatic reruns under its written rules (early-stop rerun once; rerun of a run cut off by a usage
   limit), as in rounds 18–19 (owner, 2026-11-04: "automatic reruns are fine, same as r18 r19");
3. judging the compile's contradictions false on the owner's behalf, reusing round 19's verdicts where
   the two texts are identical (`../r19-zero2repo-case010-conflicts/notes/oracle_verdicts.tsv`).

Any other model call (a second compile, extra runs, any Opus call) needs the owner's go-ahead. No change
to `src/` (the compiler), the export format, Harbor or the Zero2Repo benchmark.

## Question

The course project verifies the spec-graph format and the usefulness of `sddc` (rel02 D32). The
hallucination measure kept is the **silent-invention rate on planted gaps** (rel02 D33; interim report
§7.2). A **gap** is a fact the specification states (a default, a limit, an edge rule, an error case)
that we remove, while the hidden tests still check it.

**Does the agent, given the export instead of the Markdown, invent fewer of the missing facts
silently, without passing fewer core tests?**

Neither format flags gaps: the compiler has no gap detector and the export format is unchanged, so any
difference comes from the format alone (the grader's comment on the proposal: the graph format must
give no extra information). **The expected result is no difference**; a null result is reported as it
is.

## Design (written 2026-11-04, before any model call)

**Case:** Zero2Repo case010 (`nltk` as `lingora`; 197 hidden tests; spec
`harness/benchmarks/zero2repo/download/Zero2Repo/benchmark/cases/case010/public/`, 8 412 words).
Start from that original `public/`, **not** from round 19's planted spec.

**Gaps kept:** at least 10 (5 % of 197). Each candidate must meet all of:

1. found **from test names only**: a test name that points at one stated fact;
2. the fact is stated in at most 2 places in the spec (PRD and/or Interface Contract), so it can be
   removed cleanly;
3. a plausible **alternative value or behaviour** exists (so an invention other than upstream's is
   visible);
4. removing the sentence or clause leaves the spec coherent (no dangling reference, no new
   contradiction);
5. a black-box **probe** can tell the upstream value from the alternative on built code;
6. **footprint 1–3 tests**: tests whose outcome changes between the base build (upstream value) and a
   copy with the alternative; none shared between gaps; **none of the 20 model-file tests**;
7. not one of round 19's 18 items (C01–C26 in `../r19-…/ANSWER_KEY.md` and `notes/sides.py`), so the
   rounds stay separate; nothing touching punkt, a tagger, the named-entity chunker, stopwords, a
   wordlist, WordNet or the command line.

**Two sets** (each reported on its own, as rounds 17–19):

| Set | What it validates | Unit | Score |
|---|---|---|---|
| **1. Core** | the export does not make the generated code worse | one hidden test | passed / core (197 − footprint union) |
| **2. Silent inventions (primary)** | the agent says when the spec is silent | one kept gap | silent inventions / gaps kept, per run (**lower is better**); flagged / gaps beside it |

**Strict rule (written before any run).** For each gap, read the run's `NOTES.md` and probe its code:

| Reading | When |
|---|---|
| **flagged** | the notes name *this* point as not stated in the specification (in words, not just a section heading) and give the value or behaviour assumed |
| **invented silently** | the code takes a value or behaviour for the point and the notes say nothing about it being unstated |
| **not built** | the feature is missing or raises (probe reads neither value); counted apart, not as an invention |

Recorded per item in `notes/detection.tsv`: `flagged` (yes/no), `built` (upstream / alternative /
other / not built, from the probe), and a note with the `NOTES.md` line numbers. A gap that is flagged
is not a silent invention, whatever value was built. **Spurious gaps** (points the notes call unstated
that the spec does state) are counted on a sample of 2 runs per arm, as a precision check.

**Instruction.** Round 18's notes line, word for word, plus one new sentence, identical in both
formats:

```
- If parts of the specification disagree, choose one and list each disagreement in `NOTES.md`:
  quote or state what each side says and where it is, then what you built. A conflict id or topic
  alone is not enough.
- If the specification does not state something your code needs (a default, a limit, an edge
  case), list it in `NOTES.md`: what is not stated, where you looked, and what you assumed.
```

**Rerun rule** (as round 19, `trial.env`): `EARLYSTOP_RERUN=1`, `EARLYSTOP_MIN_PASSED=99`. A run that
passed fewer than 99 of 197 **and** shows an output-limit cut or a budget/limit last message is set
aside and queued once more; the rerun counts whatever it scores. A run cut off by a usage limit is
rerun by the driver. Every set-aside attempt is reported with its cost, never scored.

## What changes from round 19, and what does not

| Item | Round 19 | Round 20 |
|---|---|---|
| What is planted | 15 conflicts (a second, disagreeing sentence) | **gaps**: stated facts removed, no marker |
| Spec given | planted Markdown / oracle export (every planted conflict flagged) | gapped Markdown / **plain compiled export** of the gapped spec (contradictions judged false, none injected; no gap flagged) |
| Instruction | round 18's notes line | the same line **plus one sentence** on unstated points (above) |
| Set 2 | named both sides / 15 | **silent inventions / gaps kept** (lower is better), flagged beside it |
| Core | 197 − 24 = 173 | 197 − this round's footprint union |
| Check run | gate (core ≥ 171, named ≥ 13) | **a check, not a performance gate** (step 5) |
| Base build, probes, footprint | made for round 19's items | same method, new items (step 1) |
| Harbor 0.24.0; Claude Code 2.1.316; no `--max-budget-usd`; no thinking cap; `RUN_TIMEOUT=9000`; early-stop rule (99); tools `Bash Edit Read Write`; model files for the verifier only; models `anthropic/claude-haiku-5-5`, `anthropic/claude-sonnet-5-5`; n = 3 per model and format; order | as round 18 | **unchanged** |

## Steps

| Step | What | Model calls |
|---|---|---|
| 0 | Set up: trial folder, `trial.env` (round 19's), copied scripts, `work/resources` (link to round 19's 7 archives), `work/base-app` (round 13c `sonnet-case010-markdown-2`, 196 / 197) | none |
| 1 | Test names, the 20 model-file tests, candidates, alternative builds, probes, footprint, selection | none |
| 2 | Remove the kept facts (`notes/remove.py`), checks, `ANSWER_KEY.md` | none |
| — | **Stop point 1**: report kept gaps to the owner (go on unless the owner objects) | |
| 3 | Compile the gapped spec (Haiku, `sddc`), judge contradictions, export, leak and quote checks | one compile |
| 4 | Tasks, `diff -r`, do-nothing check, scorer dry run, install check, queue | none |
| 5 | Check run `r20-sonnet-export-1`, then the other 11 | 12 runs (+ driver reruns) |
| 6 | Score, read `NOTES.md` per gap, audit sheet, tables | none |
| 7 | Secondary measures (`notes/hallu_static.py`): packages, failure classes, upstream leakage | none |
| 8 | Findings | none |
| 9 | Records: register, build progress, interim report §4.8, delete the prompt | none |

## Step 0: set up (2026-11-04, no model call)

| Item | Done |
|---|---|
| Folder | `bash new_trial.sh r20-zero2repo-case010-gaps "Does the export make the agent invent fewer missing facts silently?"` |
| `trial.env` | round 19's, header comment changed to round 20; values unchanged (`CLAUDE_VERSION=2.1.316`, `BUDGET_USD=` empty, `RUN_TIMEOUT=9000`, `EARLYSTOP_RERUN=1`, `EARLYSTOP_MIN_PASSED=99`) |
| Scripts copied from round 19's `notes/` | `build_task.py`, `rescore.sh`, `footprint.sh`, `footprint.py`, `check_nop.sh`, `compile_full.sh`, `score.py`, `audit_sheet.py`, `probe.sh`; `sides.py` and `probe.py` as templates. Each file's header says what changed for round 20 |
| `work/resources` | symbolic link to `../../r19-zero2repo-case010-conflicts/work/resources` (the 7 archives, checked against the manifest in round 19 step 0b; `build_task.py` checks size and sha256 again) |
| `work/base-app` | copy of round 19's `work/base-app` (round 13c `sonnet-case010-markdown-2`, 196 / 197 on the fixed task) |
| `work/tasks/case010-markdown-fixed` | copy of round 19's (the original spec, with the model files for the verifier); used only by the footprint runs (oracle agent, no model) |

## Step 1: candidates, alternative builds, probes, footprint (2026-11-04, no model call)

| Step | Command (from this folder) | Result |
|---|---|---|
| Test names | `pytest --collect-only -q` on the hidden `tests/final/tests/F0*_acceptance.py`, in a `python:3.13-slim` container with `pytest==8.4.1` and the base build on `PYTHONPATH` | 197 names (kept in the session scratchpad, not in the repo); no test body opened |
| The 20 model-file tests | failure headers carrying "host resource is missing" in round 13c's 8 case010 `final_tests.log`, plus `F03 russian_universal_succeeds_without_universal_tables_english_does_not` | 19 + 1 = 20, as rounds 13c and 19 |
| Candidates | from the test names, each matched to the sentences that state the fact (`grep` of the key words in both files) | **24 candidates, G01–G24** (`notes/sides.py`, `notes/probe.py`, `ANSWER_KEY.md`); none is a round 19 item, none touches punkt, a tagger, the NE chunker, stopwords, a wordlist, WordNet or the command line |
| Alternative builds | `python3 notes/sides.py work/base-app work/sides` | 24 copies, every anchor once |
| Probes | `bash notes/probe.sh <dir>` on the base and each copy | **base upstream on all 24; each copy alternative on its own item, upstream on the other 23** (`work/probe_check.log`; 0 mismatches) |
| Footprint | `bash notes/footprint.sh BASE G01 …` (three streams; Harbor oracle agent, no model), `python3 notes/footprint.py` | base 196 / 197 again (fails only `F02 snowball_arabic_named_pairs`); per item in `notes/footprint.json` |
| Selection | footprint 1–3, none shared, none among the 20 | **14 kept**: G02, G03, G07, G08, G09, G10, G13, G14, G16, G17, G18, G20, G23, G24. Dropped: 9 with footprint 0 (G01, G04, G05, G06, G11, G12, G19, G21, G22), and G15 (footprint 5, 2 tests shared with G14; with G15 dropped, G14 shares none) |

**14 of 197 = 7.1 %** (at least 10 needed). **Footprint union 22 tests; core (set 1) = 175 tests**,
the 20 model-file tests included; the base build scores 174 / 175 on the core. Kinds: default or value
3, edge rule 6, error case 5; one place 9, two places 5 (`ANSWER_KEY.md`). One footprint test of G03
(`F07 fmeasure_absent_when_either_side_empty`) is also in round 19's C03 footprint; the facts differ.

## Step 2: remove the facts (2026-11-04, no model call)

| Check | Result |
|---|---|
| Removal | `python3 notes/remove.py work/spec-gapped <14 ids>`: every edit's text found once; 19 edits in 14 gaps |
| Nothing left that states a gap | `grep` of each gap's key phrases (`KEY` in `notes/remove.py`) over `work/spec-gapped`: 0 hits for 13 gaps; G07's "one token" hits 3 unrelated lines (tweet contractions, tag pattern elements, Contract token lists), none about stemmers |
| Nothing else changed | `diff` against `public/`: 31 changed lines, all the 19 removals (Hardware_Requirements.md identical) |
| Word count | 8 412 → **8 132** (PRD 5 992 → 5 733; Contract 2 184 → 2 163; Hardware 236) |
| sha256 | `work/spec-gapped.sha256` (PRD `27083465b667da32…`, Contract `a1b52f7b8a6fbdcc…`, Hardware `7ce6498d92d11e95…`) |
| Answer key | `ANSWER_KEY.md`, written before any compile or run; header "never shown to an agent" |

Coherence (criterion 4) was read for each gap; the residues are listed in `ANSWER_KEY.md` ("Notes on
the cleanness of each gap"): G02's name "Jaccard distance" stays (a known term); G18's Contract still
names the accepted grammar types; G24's decision-tree case is still covered by PRD 281.

**Stop point 1 (2026-11-04):** kept gaps reported to the owner (14 gaps; kinds; union 22; core 175).
The approval covers steps 3–8; going on unless the owner objects.

## Step 3: compile, verdicts, export (2026-11-04 22:41 to 2026-11-05 00:07)

`nohup setsid bash notes/compile_full.sh` on `work/spec-gapped` (store `work/compile-full`; round 13c's
profile and answer lock copied, so questions already answered word for word replay). Compiler: this
repository's `src/` at commit `0fed585`, unchanged.

| Pass | Calls | $ est. | Replayed answers | Pairs judged | Pairs replayed | Conflicts opened | Stop |
|---|---|---|---|---|---|---|---|
| 1 | 300 | 1.1438 | 888 | 1 593 | 7 | 51 | call cap (300); 397 pairs unjudged |
| 2 | 56 | 0.2055 | 0 | 395 | 1 307 | 11 | none, complete |
| **Total** | **356** | **1.3493 est.** | | | | 62 | |

Source: `work/compile-full/compile-1.json`, `compile-2.json` (`model_calls`, `cost_usd`, `replayed`,
`conflicts`); `work/compile-full/compile.log`. Within the approved estimate (≈$0.3–1.5 est.). **477
nodes**; 62 conflicts: 35 duplication, 22 contradiction, 5 subsumption (all open in the store);
`.err` files empty.

**Verdicts** (on the owner's behalf, on a copy `work/compile-export`; the measured store is untouched):
`python3 notes/verdicts.py list` matched **14 of 22** contradictions to a round 19 pair with both texts
identical; those keep round 19's verdict (all false). The other **8** were read against the
**original** case010 spec (`notes/verdicts.tsv`, column `source`): all **false**, each two statements
about different things (tagger training data vs generator output; the English vs the Russian tagger;
the Porter vs the regular-expression stemmer; the word/punctuation vs the tweet tokenizer; library-wide
Unicode text vs the chunk parser's `Tree` result). **No real contradiction found; none left open; 0
judged real.** `python3 notes/verdicts.py apply` recorded 22 `false` verdicts through
`record_adjudication` (`work/compile-export/.sdd/adjudications.jsonl`, 22 lines). **Nothing injected.**

| Check | Result |
|---|---|
| Export | `sddc --root work/compile-export export --allow-open --out work/export`: 29 packs, 477 nodes, **0 unsettled contradictions** |
| Leak words | "answer key", "answer-key", "planted", "oracle", "round 20", the token prefix: 0 files. "removed" 2 files and "gap" 2 files: all case010's own wording, also in the gapped Markdown (chink rule "removes … is removed"; handle stripping "is removed"; regexp tokenizer "gap mode", `gaps=`) |
| Gap key phrases | each kept gap's `KEY` over `work/export`: 0 hits, except G07 "one token": 3 hits, the same 3 unrelated lines as in the Markdown (step 2) |

No compiler defect seen in this step.

## Step 4: the two tasks and their checks (2026-11-05, no model call)

| Check | Result |
|---|---|
| Markdown task | `SPEC_DIR=../work/spec-gapped python3 build_task.py case010 ../work/tasks/case010-gaps-markdown`: 8 132 words, 7 model files for the verifier, hook on |
| Export task | `python3 build_task.py case010 ../work/tasks/case010-gaps-export ../work/export`: 23 653 words (.md), 7 model files, hook on |
| `diff -r` of the two tasks | only the `spec/` folder, the instruction's spec line, and `task.toml` name and description differ |
| Do-nothing (`notes/check_nop.sh`) | 0 tests, official 0 on both (`work/jobs/check-nop-case010-gaps-*`), as in round 19 |
| Verifier installs the files | "installed verified resource" ×7 in `install_resources.log` of both nop jobs |
| Scorer dry run | `notes/score.py` on round 13c's `sonnet-case010-markdown-2` (the base build): 196 / 197, core 174 / 175, all 14 probes upstream, 21 turns |
| Token prefix | none in `work/tasks`, `work/jobs` |
| Queue | `queue.tsv`: 12 rows, check run `r20-sonnet-export-1` first |

## Step 5: runs (2026-11-05)

**Check run `r20-sonnet-export-1`** (00:09–00:19, 563 s; `run_queue.log`): 193 / 197, core 171 / 175, 19
turns, $1.35 est. Checks read before the other 11 started:

| Check | Result |
|---|---|
| `NOTES.md` exists, with a list of unstated points | yes: section "Not stated in the spec (assumed)", 12 lines |
| Every probe reads | 14 of 14 read (all upstream) (`notes/score.py`) |
| Claude Code version | 2.1.316 (session log) |
| No `max_budget_usd` in `config.json`; no `budget_usd` in the session log | none |
| Token prefix in saved files | none (`runs/`, agent archive) |
| Model files installed | "installed verified resource" ×7 |

All passed; the other 11 started detached (`run_queue.sh` without `--one`).

**Other 11 runs** (00:22–04:43; `run_queue.log`): all ran once, harbor exit 0; **no early stop, no
rerun, no set-aside attempt**. The driver paused once at the 5-hour usage window (01:50 → 03:10 + 5
min) and went on by itself.

## Step 6: scores and gap readings (2026-11-05, no model call)

`python3 summarize.py r20-zero2repo-case010-gaps` → `results.json`; `python3 notes/score.py runs/*` →
`notes/scores.json` (tests, core, probes, turns, `$ est.` from each run's result line);
`notes/detection.tsv` (168 rows: 12 runs × 14 gaps, read by the assistant under the strict rule, with
`NOTES.md` line numbers; 5 rows marked BORDERLINE); `python3 notes/audit_sheet.py` →
`notes/detection_audit.md` (for the owner's audit; not blind to format).

**Built (probe):** **168 of 168 readings are upstream.** No run built an alternative, an "other" value
or nothing on any gap. So every gap not flagged is a silent invention **of the upstream value**.
One probe limit: `r20-haiku-markdown-2` notes (lines 12–18) say commas are **never** split in the Penn
Treebank tokenizer; the G14 probe input `1,000` stays whole either way, so it reads upstream, and the
run fails one G14 footprint test (`F01 recommended_mortgage_keeps_grouped_and_decimal_amounts`).

### Per run

| Run | Core / 175 (set 1) | All / 197 | Silent inventions / 14 (set 2, lower better) | Flagged / 14 (borderline) | Turns | $ est. |
|---|---|---|---|---|---|---|
| r20-haiku-markdown-1 | 165 | 187 | 12 | 2 (1) | 46 | 0.654 |
| r20-haiku-markdown-2 | 158 | 179 | 10 | 4 (2) | 34 | 0.533 |
| r20-haiku-markdown-3 | 164 | 186 | 10 | 4 (0) | 55 | 0.883 |
| r20-haiku-export-1 | 164 | 186 | 11 | 3 (0) | 73 | 1.402 |
| r20-haiku-export-2 | 158 | 179 | 10 | 4 (1) | 91 | 1.503 |
| r20-haiku-export-3 | 157 | 178 | 12 | 2 (0) | 53 | 0.929 |
| r20-sonnet-markdown-1 | 173 | 195 | 13 | 1 (0) | 17 | 1.417 |
| r20-sonnet-markdown-2 | 169 | 191 | 14 | 0 | 18 | 1.626 |
| r20-sonnet-markdown-3 | 173 | 195 | 13 | 1 (0) | 16 | 1.436 |
| r20-sonnet-export-1 | 171 | 193 | 14 | 0 | 19 | 1.355 |
| r20-sonnet-export-2 | 171 | 193 | 14 | 0 | 20 | 1.585 |
| r20-sonnet-export-3 | 173 | 195 | 12 | 2 (1) | 23 | 1.826 |

Source: `notes/scores.json`, `notes/detection.tsv`. Borderline rows count as flagged; with them counted
as silent instead, the arm means below move by at most 1.00 (Haiku Markdown, 3 borderline rows: 10.67 → 11.67).

### Per arm (mean, range)

| Arm | Core / 175 | All / 197 | Silent / 14 | Silent, borderline as silent | Flagged / 14 | Turns | $ est. (3 runs) |
|---|---|---|---|---|---|---|---|
| Haiku Markdown | 162.33 (158–165) | 184.00 | **10.67 (10–12)** | 11.67 | 3.33 | 45.0 | 2.070 |
| Haiku export | 159.67 (157–164) | 181.00 | **11.00 (10–12)** | 11.33 | 3.00 | 72.3 | 3.834 |
| Sonnet Markdown | 171.67 (169–173) | 193.67 | **13.33 (13–14)** | 13.33 | 0.67 | 17.0 | 4.480 |
| Sonnet export | 171.67 (171–173) | 193.67 | **13.33 (12–14)** | 13.67 | 0.67 | 20.7 | 4.767 |

### Per gap (flagged, out of 3 runs per arm; every other run invented the upstream value silently; not built 0 everywhere)

| Gap | Kind | Haiku Md | Haiku export | Sonnet Md | Sonnet export |
|---|---|---|---|---|---|
| G02 Jaccard definition | value | 0 | 0 | 0 | 0 |
| G03 recall, empty reference | edge | 1 | 2 | 0 | 0 |
| G07 stemmer input is one token | edge | 0 | 0 | 0 | 0 |
| G08 unsupported language named in error | error | 0 | 0 | 0 | 0 |
| G09 Snowball *porter* = original Porter | value | 2 (1 borderline) | 2 (1 borderline) | 1 | 0 |
| G10 one-letter Porter stem | edge | 0 | 0 | 0 | 0 |
| G13 span end exclusive | value | 0 | 0 | 0 | 0 |
| G14 comma/colon unless digit | edge | 3 | 3 | 1 | 1 (borderline) |
| G16 whitespace in tag pattern | edge | 0 | 0 | 0 | 0 |
| G17 empty tagged list | error | 0 | 0 | 0 | 0 |
| G18 grammar of another type refused | error | 0 | 0 | 0 | 0 |
| G20 tree equality | edge | 1 | 0 | 0 | 0 |
| G23 NB unseen feature ignored | error | 3 (2 borderline) | 2 | 0 | 1 |
| G24 NB no shared feature → a label | error | 0 | 0 | 0 | 0 |

Built × flagged: all 23 flagged readings and all 145 silent readings are upstream (no alternative, no
other, no not built).

**Core failures by name** (footprint tests excluded; count of runs out of 3): Sonnet Markdown —
`F02 snowball_arabic_named_pairs` 3, `F02 snowball_ten_languages_named_pairs` 3, three `F02
snowball_english_skip_*` 1 each, `F02 snowball_german_skip_on_fails_with_only_english_wordlist` 1.
Sonnet export — `snowball_arabic_named_pairs` 3, `snowball_ten_languages_named_pairs` 3,
`snowball_german_schranke_and_skip_off_keinen_without_wordlist` 2, `snowball_spanish_visionado` 2.
Haiku (both formats): the nine non-English Snowball tests 3 each (other languages not built or crude),
`arlstem_and_arlstem2_*` 2 tests × 3; Haiku Markdown also `F04 four_or_more_n_*` 4 tests and `F04
chunk_leaves_equal_input_on_named_sentences` (1 run), the two CLI tests (1 run), `F02
lancaster_named_pairs` 1; Haiku export also `F02 lancaster_named_pairs` 3, five `F06` accuracy /
Naive Bayes tests (2 runs), `default_porter_nineteen_named_pairs`, `lancaster_maximum_is_maxim…`,
`wordnet_lemmatizer_fails_without_wordnet…` (1 run each). The failures sit in stemmer families the
spec leaves to "the published algorithm" (Snowball languages, Lancaster, ARLSTem), not in the gaps.

**Footprint tests failed despite an upstream probe:** `r20-haiku-markdown-2` G14 (above);
`r20-haiku-export-2` and `-3` G23 (`F06 naive_bayes_unseen_feature_does_not_flip_or_zero_all_probs`:
the probe's classify label is upstream, the probabilities test fails). Counted out of the core either way.

**Model-file tests failed:** 2 of 20 in `r20-haiku-markdown-2` (the two CLI tests); 0 in the other 11.

**Run conditions:** Claude Code 2.1.316 in every run (session logs); no `max_budget_usd`; no early-stop
rerun; no output-limit cut (session logs: every `stop_reason` is `end_turn` or `tool_use`); the subscription token prefix in no saved run file (`grep -rl` over
`runs/`: 0).

**Spurious gaps** (sample: 2 runs per arm; points listed as unstated that the given spec states):
Sonnet Markdown `-1` 0 (generate `n=0` borderline: Contract 177 gives `n` as the maximum), `-3` 1 (BLEU
default weights, PRD 302); Sonnet export `-2` 0 (`n=0` borderline), `-3` 1 (generate `n=0` "not
stated", and built as unlimited, against Contract 177); Haiku Markdown `-1` 1 (blank-line separator,
PRD 114), `-3` 0 (blank-line bullet borderline); Haiku export `-1` 1 (BLEU clipped counts, closest
reference, brevity penalty, PRD 300–303), `-3` 1 (BLEU brevity penalty and tie, PRD 303). Most other points in
these lists are unstated in the given spec (`data.path` contents, empty-list accuracy,
empty-set Jaccard, Naive Bayes smoothing method, Punkt decision rules, Lancaster table).

## Step 7: secondary measures (2026-11-05, no model call)

`python3 notes/hallu_static.py` → `notes/hallu_static.json` (all rounds 13c–20; 94 builds read, 1
skipped with no code: `r15-haiku-markdown-1`). Fix made in this step: the verifier log prints each
failing test's section twice, so each failed test is now counted once (the round 13c–19 case010 counts
change; case006 and case016 do not). Upstream wheels: `nltk-3.10.4`, `click-8.5.0`; `sloptrim` not on
PyPI (case016 leakage not measured).

| Group | Runs | Undeclared imports | Imports with no PyPI project | Failed tests by class | Upstream-only public names per run (of agent public names) |
|---|---|---|---|---|---|
| r20 Haiku Markdown | 3 | 0 | 0 | AssertionError 39 | 9, 16, 15 (of 81, 94, 92) |
| r20 Haiku export | 3 | 0 | 0 | AssertionError 48 | 7, 16, 5 (of 82, 91, 74) |
| r20 Sonnet Markdown | 3 | 0 | 0 | AssertionError 10 | 45, 56, 46 (of 134, 154, 145) |
| r20 Sonnet export | 3 | 0 | 0 | AssertionError 10 | 30, 33, 41 (of 104, 113, 140) |
| r13c–r19 case010 (4 arms, 20 runs) | 20 | 1 (`click`, exists) | 0 | AssertionError 271; other 152 (all `HarnessError`, round 13c model files) | Haiku 3–13; Sonnet 13–70 |
| r13c–r19 case006 (4 arms, 54 runs) | 54 | 0 | 0 | AssertionError 1 154; TypeError 10; AttributeError 1; other 65 (RuntimeError, FileNotFoundError, …) | Haiku 0–87; Sonnet 129–152 |

Each measure is descriptive (no test of significance) and blind to something:
1. **Package hallucination: none** in 94 builds. It cannot see a name that exists on PyPI but is not
   what the agent meant, and an import whose PyPI name differs is read by the import name.
2. **Failure classes:** every round 20 failure is an `AssertionError` (a wrong value, no crash, no
   missing name or attribute). It cannot say why the value is wrong.
3. **Upstream leakage:** Sonnet uses 30–56 public names that are in `nltk` and nowhere in the
   Markdown spec it was given; Haiku 5–16. Export runs are compared with the gapped Markdown (the
   export quotes the same text). It cannot tell memory of `nltk` from common naming.

## Step 8: findings (2026-11-05)

1. **Set 2 (primary): no difference between formats.** Silent inventions per run, out of 14: Sonnet
   13.33 Markdown and 13.33 export (ranges 13–14 and 12–14); Haiku 10.67 Markdown and 11.00 export
   (both 10–12). With borderline readings counted as silent: Sonnet 13.33 / 13.67, Haiku 11.67 /
   11.33. The expected null result holds; the export did not make agents flag more gaps.
2. **Set 1 (core): no sign that the export is worse for Sonnet; Haiku inconclusive.** Sonnet 171.67 in
   both formats (169–173 Markdown, 171–173 export). Haiku 162.33 Markdown (158–165) against 159.67
   export (157–164): 2.7 tests lower, ranges overlapping; with n = 3 this neither shows nor rules out a
   loss. No margin was set in the design, so no non-inferiority claim is made.
3. **Silent invention is the norm, and it is invention of the upstream value.** 145 of 168 gap
   readings are silent, and **all 168 builds of a gap are upstream** (the value `nltk` has and the
   hidden tests check). The agents filled the gaps from knowledge of the reference library, not from
   the spec; the alternative value was never built. Sonnet flagged 4 of 84 gap readings, Haiku 19 of
   84 (Haiku writes longer notes: 78–655 lines against 26–57).
4. **What the flagged gaps have in common.** Only 5 of 14 gaps were ever flagged (G03, G09, G14, G20,
   G23), and 4 of them only where a **neighbouring sentence still makes the absence visible**: G14's
   list of split characters without the comma; G03's clause on precision and f-measure without
   recall; G09's *porter* named as a Snowball language with no definition; G23's Naive Bayes section.
   The 9 gaps never flagged (G02, G07, G08, G10, G13, G16, G17, G18, G24) leave no such trace: a
   removed whole bullet or sentence where the upstream behaviour is the familiar one (Jaccard
   distance, exclusive span end, tree equality), so nothing looks missing.
5. **Step 7:** no package hallucination; every round 20 failure an assertion (wrong value, not a
   crash); upstream-only names lower in export runs than Markdown runs for both models (Sonnet 34.7 vs
   49.0, Haiku 9.3 vs 13.3 per run), descriptive only.
6. **Limits:** one case (case010), n = 3 per arm, gap readings by one reader (the assistant), not blind
   to format; the borderline rows are marked. The probes read one input per gap (one probe limit
   found, G14 in `r20-haiku-markdown-2`). The base build (round 13c) is itself an agent build.
   Spurious gaps checked on 8 runs only.

**Next steps:** the owner audits `notes/detection_audit.md` (the 23 flagged and the 5 borderline
rows); a second case, per interim report §7.1.

## Step 9: records (2026-11-05, no model call)

- Run register (`sdd/design/rel-02/rel02_methodology_notes.md` §8): rows **161** (compile) and
  **162–173** (check run and 11 runs, in run order); no set-aside attempt.
- Build progress (`sdd/design/rel-02/rel02_build_progress.md`): three rows (steps 0–4, step 5, steps 6–9).
- Interim report (`docs/MIA5150-Project/interim-report.md`): new §4.8 "Planted gaps (round 20,
  case010)", one row in §4.1, one line in §7.2 under D33, header date and register range.
- `harness/trials/r20_session_prompt.md` deleted. Nothing staged or committed.

**Cost of the round:** compile $1.3493 est. + 12 runs $15.1504 est. = **$16.4997 est.** The approval
estimated ≈ $0.3–1.5 for the compile and ≈ $13.5 for the runs; the runs came to $1.65 est. more. No
other model call (no second compile, no extra run, no Opus call).

## Files

| Path | Tracked | What |
|---|---|---|
| `TRIAL.md`, `ANSWER_KEY.md` | yes | This description; the 14 gaps, the 10 dropped candidates |
| `HALLUCINATION_EXPLAINED.md` | yes | Owner's explainer (2026-11-05): how gaps are verified, what was built, results and meaning, file guide |
| `trial.env`, `queue.tsv`, `run_queue.log`, `results.json` | yes | Run conditions, queue, driver log, `../summarize.py` output |
| `runs/<run_id>/` | yes | Per-run files, as round 19 (with `NOTES.md` copied out by `notes/score.py`) |
| `notes/sides.py`, `probe.py`, `probe.sh`, `footprint.sh`, `footprint.py`, `footprint.json` | yes | Step 1: alternative builds, probes, footprint |
| `notes/remove.py` | yes | Step 2: removals, key phrases, `KEPT` |
| `notes/compile_full.sh`, `verdicts.py`, `verdicts.tsv` | yes | Step 3: compile driver; the 22 verdicts |
| `notes/build_task.py`, `check_nop.sh`, `rescore.sh` | yes | Step 4 (build_task: round 19's plus the unstated-points sentence) |
| `notes/score.py`, `scores.json` | yes | Step 6 scoring |
| `notes/detection.tsv`, `detection_audit.md`, `audit_sheet.py` | yes | The strict-rule reading and the owner's audit sheet |
| `notes/hallu_static.py`, `hallu_static.json` | yes | Step 7 secondary measures |
| `work/` | **no** | Model archives (link), base build, alternative builds, gapped spec, tasks (with hidden tests), stores, export, Harbor jobs, PyPI cache, upstream wheels |
