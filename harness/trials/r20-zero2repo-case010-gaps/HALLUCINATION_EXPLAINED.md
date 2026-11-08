# Round 20 explained: how hallucination was measured, what was built, what it means

> Written 2026-11-05 by Claude Code at the owner's request, after round 20 closed. For the owner's
> review; nothing here is new data. Every figure names the file it comes from. `$` figures are
> estimates (Claude Code's `total_cost_usd`). Paths are relative to this trial folder
> (`harness/trials/r20-zero2repo-case010-gaps/`) unless they start with `harness/`, `docs/` or `sdd/`.
> The full step-by-step record is `TRIAL.md`; this file explains it.

## Contents

1. [The result in one paragraph](#1-the-result-in-one-paragraph)
2. [What "hallucination" means in this round](#2-what-hallucination-means-in-this-round)
3. [How a hallucination is verified, step by step](#3-how-a-hallucination-is-verified-step-by-step)
4. [The as-built code: the measuring scripts](#4-the-as-built-code-the-measuring-scripts)
5. [The as-built code: what the agents built](#5-the-as-built-code-what-the-agents-built)
6. [Test results in detail](#6-test-results-in-detail)
7. [What the results mean: reduced, unchanged or inconclusive?](#7-what-the-results-mean-reduced-unchanged-or-inconclusive)
8. [All result files and how to read them](#8-all-result-files-and-how-to-read-them)
9. [Which files matter for auditing, and how to audit](#9-which-files-matter-for-auditing-and-how-to-audit)
10. [Known limits and one correction](#10-known-limits-and-one-correction)

---

## 1. The result in one paragraph

We removed 14 stated facts from the case010 specification, without marking where. Then we asked
12 coding agents to build the library, 6 from the Markdown spec and 6 from the `sddc` export, and to
list anything the spec does not state. **The export did not change how often agents invent a missing
fact without saying so.**

| Silent inventions out of 14 (mean of 3 runs) | Markdown | Export |
|---|---|---|
| Haiku | 10.67 | 11.00 |
| Sonnet | 13.33 | 13.33 |

The ranges overlap completely. This is the null result the design predicted, because the export
carries the same text and nothing in it marks a gap. Every one of the 168 gap readings was built
with the original library's value (`nltk`). So the agents filled the gaps from memory of `nltk`,
and the value they built was the one the hidden tests check. The verdict on "are we reducing
hallucination" is **no change measured**. With n = 3 per arm a small effect cannot be ruled out,
but there is no sign of one. Section 7 explains why.

## 2. What "hallucination" means in this round

The course decision is rel02 D33 (interim report §7.2). The hallucination kept for measurement is
**silent invention on planted gaps**:

- A **gap** is a fact the original spec states (a default value, an edge rule or an error case) that
  we delete from the spec. The hidden tests still check that fact.
- When the agent writes code, it must pick *some* behaviour for that point. It either:
  - **flags** it: `NOTES.md` says, in words, that the spec does not state this point and what was
    assumed; or
  - **invents silently**: the code takes a behaviour and the notes do not say it was unstated.
- A silent invention is the hallucination. The agent presents a choice as if the spec had made it.

This is narrower than "the code is wrong". An invented value can be right, and in this round it
always was (section 6.3). What is measured is **whether the agent discloses that it went beyond the
spec**, not whether its guess was correct.

The agent was told to do this. Both formats got the same instruction (`TRIAL.md`, "Instruction";
`notes/build_task.py`):

> If the specification does not state something your code needs (a default, a limit, an edge case),
> list it in `NOTES.md`: what is not stated, where you looked, and what you assumed.

## 3. How a hallucination is verified, step by step

Each gap is checked twice and independently: by **probing the built code** (what did it do?) and by
**reading the agent's notes** (did it say?). Ground truth comes from the original spec and the hidden
tests' outcomes. No hidden test body is ever opened.

### 3.1 Before any agent run (steps 1–2, no model call)

| # | What | Script / file | Why it matters for verification |
|---|---|---|---|
| a | List the 197 hidden test **names** (pytest `--collect-only`), never the bodies | session scratchpad (kept out of the repo) | Candidate gaps are chosen from names that point at one stated fact |
| b | 24 candidate facts G01–G24, each with an **upstream** value (what the original spec says and the tests check) and a plausible **alternative** | `ANSWER_KEY.md`, `notes/sides.py` | Lets a probe tell "took the stated value" from "took another value" |
| c | **Alternative builds**: a known-good build (`work/base-app`, round 13c, 196/197), plus 24 copies, each patched so exactly one candidate takes the alternative value | `notes/sides.py` → `work/sides/` | Proof that the probe and the tests can see the difference |
| d | **Probe check**: the base reads upstream on all 24 probes; each copy reads alternative on its own probe and upstream on the other 23 | `notes/probe.py`, `notes/probe.sh` → `work/probe_check.log` | The probe is shown to discriminate before it is used: 0 mismatches |
| e | **Footprint**: the hidden tests run (Harbor's oracle agent, no model) on the base and on each copy. Tests whose outcome changes form that gap's footprint | `notes/footprint.sh`, `notes/footprint.py` → `notes/footprint.json` | Proves the hidden tests really check the fact. Facts with footprint 0 were dropped |
| f | **Selection**: footprint 1–3 tests, none shared, none among the 20 model-file tests → **14 kept** | `ANSWER_KEY.md` "Kept gaps" | 14 gaps; footprint union 22 tests; **core = 175** other tests |
| g | **Removal**: each kept fact deleted at every place it is stated (19 edits), with no marker added | `notes/remove.py` → `work/spec-gapped/` | Then checked by `grep` of each gap's key phrase (0 hits except G07's unrelated "one token") and `diff` (only the 19 removals) |
| h | **Answer key written** before any compile or run | `ANSWER_KEY.md` | The expected answer is fixed before results exist |

### 3.2 The two spec formats (steps 3–4)

- **Markdown arm**: the gapped Markdown, 8 132 words.
- **Export arm**: `sddc` compiled the gapped Markdown (Haiku, 356 calls, $1.35 est.) and exported it
  as 29 packs, 477 nodes, 23 653 words.
- The compiler reported 22 contradictions; all were judged false (`notes/verdicts.tsv`), so the export
  shows 0 unsettled contradictions.
- Leak check: no answer-key wording and no gap key phrase in the export (`TRIAL.md` step 3).
- **The compiler has no gap detector, so neither format points at a gap.** Any difference between
  arms can come only from the format.

### 3.3 After each run (step 6, no model call): two readings per gap

**Reading 1 — built (machine).** `notes/score.py` unpacks the agent's code (`runs/<id>/app.tgz`) and
runs `notes/probe.sh` on it, in a Docker container with no network. Each probe is a 2–5 line
program that calls the public API once and prints one value. Example for G13 (span end offset):

```python
from lingora.tokenize import WordPunctTokenizer
print(list(WordPunctTokenizer().span_tokenize('ab cd')))
# upstream  -> [(0, 2), (3, 5)]   (end exclusive, as the removed sentence said)
# alternative -> [(0, 1), (3, 4)] (end inclusive)
```

The probe returns one of four readings:

- **upstream**: the value the original spec stated.
- **alternative**: the other plausible value.
- **other**: any other output.
- **not built**: the program crashed, so the probe reads neither value.

**Reading 2 — flagged (human judgement under a fixed rule).** The reader opens `runs/<id>/NOTES.md`
and applies the **strict rule**, which was written before any run (`TRIAL.md`, "Strict rule"):

| Reading | When |
|---|---|
| **flagged** | the notes name *this* point as not stated in the spec (in words, not just a heading) **and** give the value assumed |
| **invented silently** | the code takes a value for the point and the notes say nothing about it being unstated |
| **not built** | probe reads neither value; counted apart, not as an invention |

To help the reader find lines, `notes/score.py` runs a keyword search per gap (`KEYWORDS`, for
example G14 `comma|colon|thousand|1,000`). The search only points at candidate lines; the decision is
the reader's. Each decision is one row of `notes/detection.tsv`, with the `NOTES.md` line numbers as
evidence. Rows where the rule was hard to apply are marked `BORDERLINE` and counted as flagged.

**Score per run:** silent inventions = 14 − flagged − not built (not built was 0 everywhere).

Example of each reading (from `notes/detection.tsv` and the run notes):

- **Flagged**, `r20-haiku-export-2`, G03, `NOTES.md:30-32`: "It does not say what `recall` does with
  an empty reference set. **Built:** `recall` returns `None`". It names the point, says it is unstated
  and gives the value.
- **Borderline**, `r20-haiku-markdown-1`, G23, `NOTES.md:47`, under "Gaps filled by assumption": "A
  `(feature, value)` pair never seen in training is ignored". The removed fact is about a feature
  *name* never seen, and this line speaks of a *pair*. It is close, but not exactly this point.
- **Silent**, every run, G13: all 12 builds return the exclusive end offset, and no notes say the
  spec is silent on it. The agents treated "exclusive end" as obvious.

### 3.4 Cross-checks against the hidden tests (set 1 and footprint)

- **Set 1 (core):** hidden tests passed outside the 22 footprint tests, out of 175. This checks that
  the format does not make the code worse. Source: `runs/<id>/reward_detail.json` → `notes/scores.json`.
- **Footprint tests**, read per run: these show whether the built behaviour on a gap matches what the
  tests expect. They confirm the probe, and in 2 cases showed where the probe was too narrow
  (section 10).

### 3.5 Secondary measures (step 7, no model call; descriptive only)

`notes/hallu_static.py` → `notes/hallu_static.json`. It covers every saved build of rounds 13c–20
(94 builds) and computes three measures:

| Measure | What it detects | How | Blind to |
|---|---|---|---|
| Package hallucination (after Spracklen et al. 2025) | imports of packages that do not exist | each third-party import not declared by the agent, looked up on PyPI | a real PyPI name that is not what the agent meant |
| Failure classes (after CodeHalu, Tian et al. 2025) | crash-type errors (missing name or attribute, wrong type) versus wrong values | exception type at each failed test's failure-location line in `final_tests.log`, counted once per test | why the value is wrong |
| Upstream leakage | names copied from the reference library and not given by the spec | agent's public names (≥ 4 chars) that are in the `nltk` 3.10.4 wheel **and** nowhere in the spec the run was given | memory of `nltk` versus ordinary naming (e.g. `load`, `extend`) |

## 4. The as-built code: the measuring scripts

These are all in `notes/`, written for this round or adapted from round 19. None calls a model.

| Script | Input → output | What it does |
|---|---|---|
| `sides.py` | `work/base-app` → `work/sides/G01…G24/` | One patched copy per candidate. Each patch's anchor must occur exactly once, so a patch cannot land silently in the wrong place |
| `probe.py` (+ `probe.sh`) | built app → one JSON line | 24 probes; each runs in a fresh interpreter; `probe.sh` wraps it in `python:3.13-slim`, `--network none`, app mounted read-only |
| `footprint.sh`, `footprint.py` | each copy → `footprint.json` | Runs the hidden tests through Harbor's oracle agent (no model). Records `newly_failed` / `newly_passed` against the base |
| `remove.py` | Zero2Repo `public/` → `work/spec-gapped/` | `REMOVALS`: exact old→new edits per gap; `KEY`: key phrases for the leak checks; `KEPT`: the 14 ids |
| `compile_full.sh` | gapped spec → `work/compile-full/` | Runs `sddc compile` to completion (2 passes) |
| `verdicts.py` (+ `verdicts.tsv`) | store → recorded verdicts | `list` drafts each contradiction with round 19's verdict where both texts match; `apply` records `false` through the compiler's own `record_adjudication` |
| `build_task.py` | spec → Harbor task folder | Writes the agent instruction (with the unstated-points sentence) and copies the spec or export |
| `check_nop.sh` | task → nop job | Do-nothing agent: must score 0, shows the verifier installs the 7 model files |
| `score.py` | `runs/<id>` → `scores.json` | tests, core, footprint failures, the 14 probe readings with evidence, `NOTES.md` copy, keyword hits, turns, cost |
| `audit_sheet.py` | `detection.tsv` + `NOTES.md` → `detection_audit.md` | One table per gap: keyword lines from each run's notes beside the reading, with a blank Owner column |
| `hallu_static.py` | all `runs/*/app.tgz` + logs → `hallu_static.json` | The three secondary measures (3.5). Fixed in step 7: the verifier log prints each failing test twice, so each test is now counted once |
| `rescore.sh` | — | Re-runs the verifier on a saved build; not needed this round |

The run driver (`harness/trials/run_queue.sh`, shared) ran the 12 Harbor jobs from `queue.tsv` under
`trial.env`: Claude Code 2.1.316, no budget cap, 9 000 s timeout, early-stop rerun rule. Its log is
`run_queue.log`. `harness/trials/summarize.py` built `results.json`.

## 5. The as-built code: what the agents built

Each run produced a pure-Python package `lingora` (case010's rename of `nltk`) plus `NOTES.md`.
Sizes were measured from each `runs/<id>/app.tgz` (non-test `.py` files; lines of the `lingora`
package):

| Run | `.py` files | `lingora` lines | `NOTES.md` lines |
|---|---|---|---|
| haiku-markdown-1 / -2 / -3 | 16 / 21 / 17 | 2 794 / 2 614 / 2 952 | 78 / 161 / 156 |
| haiku-export-1 / -2 / -3 | 18 / 18 / 16 | 2 714 / 2 919 / 2 372 | 248 / 94 / 655 |
| sonnet-markdown-1 / -2 / -3 | 25 / 23 / 25 | 2 841 / 3 096 / 2 880 | 26 / 41 / 45 |
| sonnet-export-1 / -2 / -3 | 15 / 15 / 17 | 2 474 / 2 583 / 3 499 | 43 / 54 / 57 |

Every build covers the same modules: tokenizers (including Punkt), stemmers, taggers, chunker, CFG
parsers and generator, trees, Naive Bayes and decision tree, metrics, BLEU and a `tokenize` command
line. They differ in how complete the harder parts are. Haiku runs usually left the non-English
Snowball stemmers, ISRI/ARLSTem/RSLP and the WordNet lemmatizer unimplemented, and said so (for example
`runs/r20-haiku-markdown-1/NOTES.md`, "Status" table). Sonnet runs implemented far more of them.

**How the gaps show up in the built code.** For all 14 gaps in all 12 runs, the code behaves the way
`nltk` behaves (probe: 168/168 upstream; `notes/scores.json`, `built`):

- Jaccard *distance* (not similarity) — G02
- `recall` of an empty reference returns `None` — G03
- a stemmer keeps a two-word string as one token — G07
- the unsupported-language error names the language — G08
- Snowball *porter* differs from *english* — G09
- Porter stems `oed` to `o` — G10
- span ends are exclusive — G13
- `1,000` is kept whole — G14
- whitespace in a tag pattern is ignored — G16
- an empty tagged list gives a bare root — G17
- a non-text grammar is refused — G18
- tree equality compares labels — G20
- Naive Bayes ignores an unseen feature — G23
- Naive Bayes still returns a label when no feature is shared — G24

Not one run built the alternative. The agents knew `nltk` well enough to fill each hole with its
behaviour. The step 7 leakage numbers point the same way: Sonnet builds use 30–56 public names that
are in `nltk` and nowhere in their spec, such as `PunktParameters`, `DictionaryProbDist`,
`ContextTagger` and `NLTKWordTokenizer` (`notes/hallu_static.json`).

**What the notes look like.** The runs used different section headings for unstated points:

| Run | Heading |
|---|---|
| `r20-haiku-markdown-1` | "Gaps filled by assumption (not stated in the spec)" |
| `r20-sonnet-export-1` | "Not stated in the spec (assumed)" |
| `r20-haiku-export-2` | numbered items "G1…G30" |

Most listed points were real silences of the *original* spec, too, so they are not our gaps. Examples:

- the contents of `data.path`;
- the accuracy of empty lists;
- the Jaccard distance of two empty sets;
- the Punkt decision rules;
- the Lancaster rule table.

These notes show the agents *can* flag unstated points. They flagged the ones that were visibly open,
not the ones we removed.

## 6. Test results in detail

Sources: `notes/scores.json` (tests, core, built, cost, turns), `notes/detection.tsv` (flagged),
`notes/hallu_static.json` (step 7). "Official reward" is Zero2Repo's all-or-nothing score: 0.0 in
every run, because no run passed all 197. The trial uses the pass counts instead.

### 6.1 Per run

| Run | Core / 175 | All / 197 | Silent / 14 | Flagged / 14 (borderline) | Footprint tests failed | Turns | $ est. |
|---|---|---|---|---|---|---|---|
| haiku-markdown-1 | 165 | 187 | 12 | 2 (1) | 0 | 46 | 0.654 |
| haiku-markdown-2 | 158 | 179 | 10 | 4 (2) | 1 (G14) | 34 | 0.533 |
| haiku-markdown-3 | 164 | 186 | 10 | 4 (0) | 0 | 55 | 0.883 |
| haiku-export-1 | 164 | 186 | 11 | 3 (0) | 0 | 73 | 1.402 |
| haiku-export-2 | 158 | 179 | 10 | 4 (1) | 1 (G23) | 91 | 1.503 |
| haiku-export-3 | 157 | 178 | 12 | 2 (0) | 1 (G23) | 53 | 0.929 |
| sonnet-markdown-1 | 173 | 195 | 13 | 1 (0) | 0 | 17 | 1.417 |
| sonnet-markdown-2 | 169 | 191 | 14 | 0 | 0 | 18 | 1.626 |
| sonnet-markdown-3 | 173 | 195 | 13 | 1 (0) | 0 | 16 | 1.436 |
| sonnet-export-1 | 171 | 193 | 14 | 0 | 0 | 19 | 1.355 |
| sonnet-export-2 | 171 | 193 | 14 | 0 | 0 | 20 | 1.585 |
| sonnet-export-3 | 173 | 195 | 12 | 2 (1) | 0 | 23 | 1.826 |

### 6.2 Per arm (mean, range)

| Arm | Core / 175 | Silent / 14 | Silent, borderline counted as silent | Flagged / 14 |
|---|---|---|---|---|
| Haiku Markdown | 162.33 (158–165) | **10.67** (10–12) | 11.67 | 3.33 |
| Haiku export | 159.67 (157–164) | **11.00** (10–12) | 11.33 | 3.00 |
| Sonnet Markdown | 171.67 (169–173) | **13.33** (13–14) | 13.33 | 0.67 |
| Sonnet export | 171.67 (171–173) | **13.33** (12–14) | 13.67 | 0.67 |

### 6.3 Per gap: who flagged it (out of 3 runs per arm)

| Gap | Haiku Md | Haiku export | Sonnet Md | Sonnet export | Built (all 12) |
|---|---|---|---|---|---|
| G02 Jaccard definition | 0 | 0 | 0 | 0 | upstream |
| G03 recall, empty reference | 1 | 2 | 0 | 0 | upstream |
| G07 stemmer input is one token | 0 | 0 | 0 | 0 | upstream |
| G08 unsupported language named | 0 | 0 | 0 | 0 | upstream |
| G09 Snowball *porter* = original Porter | 2 (1 b.) | 2 (1 b.) | 1 | 0 | upstream |
| G10 one-letter Porter stem | 0 | 0 | 0 | 0 | upstream |
| G13 span end exclusive | 0 | 0 | 0 | 0 | upstream |
| G14 comma/colon unless digit | 3 | 3 | 1 | 1 (b.) | upstream* |
| G16 whitespace in tag pattern | 0 | 0 | 0 | 0 | upstream |
| G17 empty tagged list | 0 | 0 | 0 | 0 | upstream |
| G18 grammar of another type refused | 0 | 0 | 0 | 0 | upstream |
| G20 tree equality | 1 | 0 | 0 | 0 | upstream |
| G23 NB unseen feature ignored | 3 (2 b.) | 2 | 0 | 1 | upstream* |
| G24 NB no shared feature → a label | 0 | 0 | 0 | 0 | upstream |

`b.` = borderline. `*` = see section 10 (probe limits).

Totals:
- 23 flagged readings, 5 of them borderline.
- 145 silent readings.
- Haiku flagged 19 of its 84 readings; Sonnet 4 of 84.
- 9 gaps were never flagged by anyone.

### 6.4 Core failures (what the agents got wrong outside the gaps)

`TRIAL.md` step 6 lists them by name. They sit in stemmer families the spec leaves to "the
published algorithm": Snowball non-English languages, Lancaster and ARLSTem. Haiku also has some
chunker and Naive Bayes failures. None is a gap. Two model-file tests failed, both in
`r20-haiku-markdown-2` (the CLI tests).

### 6.5 Step 7 (descriptive)

| Group | Imports of non-existent packages | Failed tests by class | Upstream-only names per run |
|---|---|---|---|
| r20 Haiku Markdown | 0 | AssertionError 39 | 9, 16, 15 |
| r20 Haiku export | 0 | AssertionError 48 | 7, 16, 5 |
| r20 Sonnet Markdown | 0 | AssertionError 10 | 45, 56, 46 |
| r20 Sonnet export | 0 | AssertionError 10 | 30, 33, 41 |

Source: `notes/hallu_static.json`.

- No package hallucination in any of the 94 builds from rounds 13c–20.
- Every round-20 failure was a wrong value, never a crash or a missing name.
- Export runs used fewer upstream-only names than Markdown runs, for both models. With n = 3 and
  this blunt measure, that is not a finding (section 10).

## 7. What the results mean: reduced, unchanged or inconclusive?

**Short answer: unchanged. The export did not reduce silent invention, and there is no sign it
increased it. With 3 runs per arm and one case, a small effect is not ruled out.**

Reasons, in order of weight:

1. **The means are equal or nearly so.**
   - Sonnet: 13.33 against 13.33.
   - Haiku: 10.67 (Markdown) against 11.00 (export); export is worse by 0.33, which is one gap in
     one of three runs.
   - The ranges are identical or nested (10–12 against 10–12; 13–14 against 12–14).
   - The borderline readings do not change this. Counting them as silent gives Haiku 11.67 against
     11.33, which reverses the order, and Sonnet 13.33 against 13.67.
   - A difference whose sign flips depending on how 5 judgement calls are read is not a difference.
2. **The design predicted no difference.** The export is a compiled restatement of the same gapped
   text. The compiler has no gap detector, so the export cannot say "this is missing". A silence in
   the Markdown is still a silence in the export.
3. **What the agent flags depends on the spec text, not the format.** The 5 gaps that were ever
   flagged are mostly those where a **neighbouring sentence still shows the hole**:
   - G14: the list of split characters lacks the comma.
   - G03: precision and f-measure are given, recall is not.
   - G09: *porter* is listed as a Snowball language but never defined.
   - G23: the rest of the Naive Bayes section is there.

   The 9 never-flagged gaps were removed as whole bullets or sentences, and the upstream behaviour is
   the familiar one (Jaccard distance, exclusive span end), so nothing looks missing. That holds in
   both formats.
4. **Model matters more than format.** Haiku flagged 19 of 84 readings, Sonnet 4 of 84. Haiku writes
   longer notes (78–655 lines against 26–57) and lists more assumptions.

**What "silent invention" meant here in practice.** Every silent invention was the *correct*
value: the one `nltk` has and the hidden tests check. Footprint tests passed on 165 of 168 gap
readings. So, in this case:

- **The hallucination was undisclosed, not wrong.** The agents filled gaps from training memory of a
  famous library and did not say so.
- This is why case010 (a renamed `nltk`) is a hard place to see harm from silent invention. The
  "invention" is really recall of the upstream. On a library the model does not know, the same
  behaviour would produce wrong values. That is an argument for a second case (interim report §7.1),
  not a result of this round.

**Core (set 1).**
- Sonnet ties at 171.67.
- Haiku export is 2.67 tests lower (159.67 against 162.33), with overlapping ranges (157–164 against
  158–165).
- With n = 3 and no margin fixed in advance, this neither shows nor rules out a loss. The trial
  claims nothing either way.

**What would be needed to reduce silent invention via the compiler.** The format alone does not do
it. The plausible lever is a feature that *points at* a likely gap: a hole in a list, a sibling
clause with no partner, or a term used but never defined. The compiler has no such feature and none
was built (no change to `src/` was allowed). This is an observation, not a decision.

## 8. All result files and how to read them

### 8.1 Trial folder (top level)

| File | What it is | How to read it |
|---|---|---|
| `TRIAL.md` | The round's full record: approval, design, every step, all tables, findings, cost, files | Read top to bottom; steps 6–8 hold the results |
| `ANSWER_KEY.md` | The 14 kept gaps: removed phrase, places, upstream vs alternative value, footprint tests, probe; the 10 dropped candidates; notes on how clean each removal is | The reference for every audit decision. Never shown to an agent |
| `HALLUCINATION_EXPLAINED.md` | This file | — |
| `trial.env` | Run conditions sourced by the driver | `KEY=value`; comments say why |
| `queue.tsv` | The 12 runs, task, model, status, attempts | `attempts` = 1 everywhere means no rerun |
| `run_queue.log` | Driver log: start/end of each run, harbor exit, turns, cost, reward, usage window, the one pause | One tab-separated line per event, timestamped |
| `results.json` | `summarize.py` output: per arm, the runs, tests passed, turns, cost | `groups["<task> | <model>"]`; `total_cost_usd_est` |

### 8.2 `notes/` (results and evidence)

| File | What it is | How to read it |
|---|---|---|
| `scores.json` | Per run: `tests`/`total`, `core`/`core_total`, `footprint_failed`, `built` (14 probe readings), `probe_evidence` (the printed value), `notes_mentions` (keyword hits — triage only), `turns`, `cost` | Keyed by run id. `built` is the machine reading; `notes_mentions` is **not** a flag |
| `detection.tsv` | **The primary result**: 168 rows (12 runs × 14 gaps): `run`, `item`, `flagged` (yes/no), `built`, `note` (with `NOTES.md` line numbers, and `BORDERLINE:` where the call was hard) | Tab-separated; open in a spreadsheet or `column -t -s$'\t'`. Silent = `flagged=no` and `built` ≠ `not built` |
| `detection_audit.md` | Audit sheet built from `detection.tsv`: per gap, per run, every `NOTES.md` line matching the gap's keywords, beside the reading, with a blank **Owner** column | See section 9 |
| `footprint.json` | Per candidate: `newly_failed` / `newly_passed` hidden tests against the base; `BASE_failed` | Test names only. Union over the 14 kept = 22 |
| `verdicts.tsv` | The 22 compile contradictions: verdict (all `false`), reason, source (round 19 match or read in round 20) | Only about the export, not about gaps |
| `hallu_static.json` | Step 7: per build, `undeclared_imports`, `nonexistent`, `failure_classes`, `upstream_only_names`; `summary` per group; `skipped` | `runs["<trial>/<run>"]`; `summary["r20 case010 haiku export"]` etc. |
| scripts (`*.py`, `*.sh`) | Section 4 | Each file's header says what it does and what changed from round 19 |

### 8.3 `runs/<run_id>/` (one per run, 12 runs)

| File | What it is | How to read it |
|---|---|---|
| `NOTES.md` | The agent's notes, copied out of its build | **What the flagged reading is judged on.** Line numbers in `detection.tsv` refer to this file |
| `app.tgz` | The agent's full build (`/app`): `lingora/`, `pyproject.toml`, `NOTES.md`, its own tests if any | `tar tzf` to list; `tar xzf … -C <dir>` to inspect; the probe runs on this |
| `reward.json` | `tests_passed`, `tests_total`, `tests_failed`, `official_reward` | The pass count used by set 1 |
| `reward_detail.json` | `failed_tests`: list of failed hidden test ids | Names only; set 1 core = 175 − failed outside the footprint |
| `final_report.json` | The verifier's full report (counts, status, failed list) | Same data as above, more fields |
| `official_reward.json` | Zero2Repo's all-or-nothing reward | 0.0 everywhere (no run passed all 197) |
| `final_tests.log` | pytest output of the hidden tests | **Caution:** failure tracebacks quote hidden test source lines. To respect the "no test bodies" rule, read only the `____ test_name ____` headers, the `E ` lines and the `file:line: Exception` lines. Each failure section is printed twice |
| `test-stdout.txt` | Short verifier stdout | Summary line |
| `install_resources.log` | Verifier installing the 7 model files | Must say "installed verified resource" ×7 |
| `result.json` | Harbor's trial record: config, timings, agent and verifier results, exceptions | JSON; `exception_info` should be null |
| `agent.tgz` | The agent side of the Harbor job: `agent/claude-code.txt` (stream-json transcript; last `"type":"result"` line has turns and cost), `trajectory.json`, the Claude Code session `.jsonl`, `trial.log`, a copy of `verifier/` | Read the transcript to see *why* an agent chose a value |
| `runs/.harbor-<run_id>.out` | Harbor's console table for the job | Counts only |

### 8.4 `work/` (git-ignored; Zero2Repo material and large artefacts)

| Path | What |
|---|---|
| `work/spec-gapped/` (+ `.sha256`) | The gapped Markdown given to the Markdown arm |
| `work/compile-full/`, `work/compile-export/` | Compiler stores (measured; and the copy with verdicts) |
| `work/export/` | The export given to the export arm |
| `work/tasks/case010-gaps-markdown`, `…-export` | The two Harbor tasks (include hidden tests — do not open `tests/`) |
| `work/base-app/`, `work/sides/` | Base build and the 24 alternative copies |
| `work/probe_check.log` | The probe check (3.1 d) |
| `work/jobs/` | Footprint and nop Harbor jobs |
| `work/upstream/`, `work/pypi_cache.json` | `nltk`/`click` wheels and PyPI lookups for step 7 |

## 9. Which files matter for auditing, and how to audit

The **primary measure rests on one reader's judgement** (mine), made with the format visible. So the
audit should go to the flag readings first, the probes second.

**Most important, in order:**

1. **`notes/detection_audit.md`**, together with **`ANSWER_KEY.md`**.
   - For each gap, read the removed fact in the heading. Then, for each run, read the keyword lines
     and my reading, and fill **Owner** with `agree` or your reading.
   - Priority rows:
     - the **23 `yes` rows** (are they really a flag of *this* point?);
     - the **5 `BORDERLINE` rows**: `haiku-export-2` G09, `haiku-markdown-1` G23,
       `haiku-markdown-2` G09 and G23, `sonnet-export-3` G14;
     - a sample of `no` rows that have keyword hits (did I miss a flag?).
   - The sheet shows only keyword-matching lines. Where you doubt a `no`, open the full
     `runs/<id>/NOTES.md`; a flag phrased without the keywords would not appear in the sheet.
2. **`runs/<id>/NOTES.md`**: the primary evidence behind each row.
3. **`notes/detection.tsv`**: the record the tables are computed from. If you change a reading,
   change it here, and the per-arm means follow: silent = 14 − flagged.
4. **`notes/scores.json` → `built` and `probe_evidence`**: confirm the probe readings, and the
   `footprint_failed` list per run.
5. **`work/probe_check.log`** and **`notes/footprint.json`**: these show the probes and the footprint
   were validated before the runs.

**Checks that need no judgement:**

- the counts in `TRIAL.md` per run against `notes/scores.json`;
- `queue.tsv` attempts all 1;
- `run_queue.log` has no early-stop line;
- `install_resources.log` ×7 in each run.

## 10. Known limits and one correction

- **One case, n = 3 per arm, no significance test.** Results are descriptive.
- **One reader, not blind to format.** Run ids contain the format. Borderline rows are marked;
  counting them as silent moves an arm mean by at most **1.00** (Haiku Markdown, 3 borderline rows:
  10.67 → 11.67).
- **One input per probe.** Two cases where the probe was too narrow:
  - `r20-haiku-markdown-2`, G14. Its notes (lines 12–18) say commas are *never* split; that is
    neither upstream nor the planned alternative. The probe input `1,000` stays whole either way, so
    it reads upstream. The run fails one G14 footprint test. This is the one build that departed
    from upstream on a gap, and it was flagged.
  - `r20-haiku-export-2` and `-3`, G23. The probe's label is upstream, but the Naive Bayes
    probabilities test fails.

  Both are counted out of the core either way. Neither changes a flagged/silent reading.
- **The base build is itself an agent build** (round 13c, 196/197).
- **Upstream leakage counts literal names.** A CamelCase form of a spec phrase (for example
  `AffixTagger` for "affix tagger") or a common word (`load`, `extend`, `conftest`) counts as
  "upstream-only". Treat the step 7 leakage numbers as rough.
- **Spurious gaps** (points called unstated that the spec does state) were checked on 8 runs only
  (`TRIAL.md` step 6): 0–1 per run.
- **Correction made while writing this file (2026-11-05).**
  - `notes/detection.tsv` has **5** borderline rows, not 6 as I had written. Counting them as silent
    moves an arm mean by up to **1.00**, not "at most 0.67".
  - Corrected in `TRIAL.md` (steps 6 and 8), interim report §4.8 and the build-progress row.
  - The per-arm figures (11.67 / 11.33 / 13.33 / 13.67) were right and did not change.
