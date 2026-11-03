# r17-zero2repo-case006-conflicts-24

> Opened 2026-10-30 by Claude Code. State: **compiler work** (step 0 done; step 1a pair ranking done; step 1b fix 1, F3 D43; step 1c fix 2, F5 D15–D16; step 1d fix 3, F3 D44; step 1e fix 4, F5 D17; step 2 full compile 2026-10-31: recall 14 of 24; step 3 baseline 11 of 24; step 4 options 1–2 offline, not built; step 5 oracle export, 24 of 24 flagged, tasks built; step 6 agent runs 2026-11-01 19:44 to 11-02 02:24; step 7 results scored 2026-11-02, owner's audit pending). Asked by the owner
> 2026-10-30: "I want stricter rules and redesign of conflicts. start new round with the same case006
> as base for redesign conflicts. first, all planted conflicts should be covered by existing tests.
> second, increase number of conflicts to at least 5% of test-quantity, so 476 x 5% = 23.8 = 24
> conflicts [...] third, explicitly state in test output report that 2 sets of validation". Owner's
> choices the same day: pick from **test names only** (hidden test bodies stay unopened); set 1 scored
> **per test**, set 2 **per conflict**; **at most 3 tests per conflict**; report **three detection
> counts**. Compile and agent runs each need the owner's go-ahead. Update this file at every step.

## Question

With 24 conflicts planted in case006, each one checked by at least one existing hidden test:

1. **Compiler recall:** how many of the 24 does the compiler report? (no agent)
2. **Set 1, build quality:** does the export make the generated code worse than the Markdown does, on
   the hidden tests that no planted conflict touches (the core)?
3. **Set 2, detection:** does the agent see both sides of each conflict, from the Markdown and from
   the export, under the strict rule below?

## The two validation sets (stated in every results table of this round)

| Set | What it validates | Unit | Score |
|---|---|---|---|
| **1. Benchmark** | the export does not make the generated code worse | one hidden test | passed / core tests (476 minus the footprint union; ANSWER_KEY.md) |
| **2. Detection** | the agent saw both sides of each conflict | one planted conflict | named / 24 (strict rule) |

Each set is reported on its own, as a percentage. Inside a set every unit has the same weight: one
test in set 1, one conflict in set 2. The two sets also weigh the same as each other: where one
figure is wanted, it is the plain mean of the two percentages, reported next to both of them, never
instead of them. The footprint tests (the tests a conflict's side changes) belong to neither set:
they reward side A whatever the agent noticed, so they would reward a lucky miss and punish a
noticed choice of B.

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

## Method: how the conflicts were built (step 0, no model call)

Same method as round 14 (`../r14-zero2repo-case006-conflicts/TRIAL.md`, "Method"), with the owner's
new rules:

1. **Candidates from test names.** The 476 hidden test names were listed with
   `pytest --collect-only -q` (names only; no test body opened; the list stays out of the repository).
   For each name that points at one behaviour with a sentence in the public spec, a candidate.
2. **Side-B builds** (`notes/sides.py`). Base: the same build as round 14, round 13c's
   `sonnet-case006-export-1` (473 / 476), which takes A on every item. One smallest patch per
   candidate; each anchor occurs exactly once.
3. **Probes** (`notes/probe.py`, `notes/probe.sh`), black box, from the answer key and the Contract's
   API only, run in a container with no network. Check: the base reads A on every item; each side-B
   copy reads B on its own item and A on the others.
4. **Footprint** (`notes/footprint.sh`, `notes/footprint.py`): the hidden tests run through Harbor's
   oracle agent (no model) on the base and on each side-B copy; the tests whose result differs from
   the base are that item's footprint. **Kept only if 1 to 3 tests**, and if no two kept items share
   a test.
5. **Plant** (`notes/plant.py`): the side-B sentence of each kept item, one place, in the spec's own
   voice, no marker; every anchor and every exposure phrase occurs exactly once.

Results of step 0: below, and the key in `ANSWER_KEY.md`.

## Step 0 results (2026-10-30, no model call)

| Step | Command (from this folder) | Result |
|---|---|---|
| Test names | `pytest --collect-only -q` on the hidden `tests/F*_acceptance.py` | 476 names (F01 27 … F14 20); list kept in the session scratchpad, not in the repo |
| Side-B builds | `python3 notes/sides.py work/base-app work/sides` | 30 candidates (28 + 2 reserves), every anchor once |
| Probes | `bash notes/probe.sh <dir>` on the base and each copy | base A on all; each copy B on its own item, A on the others, except C28, which also moved C04's probe to "neither" (`work/probe_check.log`; there R4 = C29) |
| Footprint | `bash notes/footprint.sh BASE C01 … C28 R3 R4`, `python3 notes/footprint.py` | base 473 / 476 as in round 14; per item in `notes/footprint.json` |
| Selection | footprint 1–3, no shared test | **24 kept**: C01–C10, C12–C15, C17, C18, C20–C23, C25–C27, C29. Dropped: C11 (6), C16 (4), C19 (6), C24 (394), C28 (shares C04's test), R3 (0) |
| Plant | `python3 notes/plant.py work/spec-planted <24 ids>` | 14 435 words (14 138 before); every anchor and exposure phrase once; `work/spec-planted.sha256` |

**Footprint union 31 tests; core (set 1) = 445 tests.** Distances: same bullet 2, far in one file 8,
across files 14 (`ANSWER_KEY.md`). 24 of 476 is 5.04 %.

**A check the owner did not ask for:** how often the 36 earlier case006 runs (rounds 13b–16) failed
each footprint test. Most new items' tests were failed by 0–2 of them; C29's by 10 and C02's
`feature_switch_more_explicit_source_wins` by 17 (`ANSWER_KEY.md`, "Past fails"). A miss there is
harder to tell from "not built"; the probe still reads the side.

## Step 1a: compile up to pair-picking (2026-10-30, approved: "go ahead, compile up to pair-picking and rank the 24")

| Step | Command | Result |
|---|---|---|
| Store | `.sdd/` and `sdd/` of `../r13c-zero2repo-3cases/work/compile-case006` → `work/compile-planted`; planted Markdown over `sdd/specs/`; `.sdd/lock` = round 14's v2 lock (so C01–C05's blocks replay) | |
| Ingest | `sddc --json ingest` | 23 changed, 442 unchanged |
| Atomize, pairs | `python3 notes/compile_to_pairs.py work/compile-planted` (the compiler unchanged; stops at the first judge call with its own call-cap error) | **15 calls, $0.1092 est.**, 29 replayed; 55 nodes formed, 10 deleted; 250 nodes checked, **1 842 pairs proposed, 0 judged** (`work/compile-planted/pairs-proposed.json`) |
| Rank | `python3 notes/rank_pairs.py work/compile-planted` → `notes/pair_ranks.json` | below |

A pair reaches the judge only if each side ranks the other within its top 6 (`max_pairs_per_node`),
from either end (F5 D14). Ranks are "rank / candidates" with the compiler's own scoring.

| Item | Proposed | Score (sources) | Rank from B | Rank from A | Why not, read in the store |
|---|---|---|---|---|---|
| C01 | yes | 3.5 (S2 S7) | 3 / 15 | 10 / 40 | |
| C02 | yes | 6.0 (S2 S5) | 5 / 206 | 42 / 301 | |
| C03 | **no** | 5.0 (S2 S5) | 7 / 160 | 32 / 131 | as round 14's P4: families `callback` / `parameter_callback`, one place outside the cap |
| C04 | yes | 2.0 (S5) | 55 / 81 | 5 / 9 | |
| C05 | yes | 4.5 (S1 S7) | 2 / 48 | 10 / 211 | |
| C06 | **no** | 2.0 (S5) | 7 / 115 | 47 / 57 | B sits in one node merging the whole `command` keyword list (family `attrs_keyword`) |
| C07 | yes | 6.5 (S1 S2 S5) | 1 / 116 | 1 / 118 | |
| C08 | yes | 9.0 (S1 S2 S5) | 1 / 272 | 1 / 169 | |
| C09 | yes | 4.0 (S2 S5) | 3 / 68 | 51 / 160 | |
| C10 | **no** | 2.0 (S2) | 27 / 76 | 112 / 208 | families `environment_value` / `boolean_flag` |
| C12 | **no** | 0 (none) | — | — | B merged into the `DateTime` row node (family `format`); no shared term or keyword |
| C13 | **no** | 1.5 (S5) | 31 / 57 | 7 / 11 | families `format_string_list` / `date_time_format_list`; one place outside the cap from A |
| C14 | yes | 3.0 (S2 S5) | 6 / 33 | 41 / 150 | |
| C15 | yes | 2.0 (S2) | 8 / 20 | 6 / 10 | |
| C17 | **no** | — | — | — | **no node holds B**: the atomizer kept only the effects of PRD 381's abort sentence and dropped its list of causes |
| C18 | **no** | 1.5 (S5) | 49 / 147 | 147 / 156 | B is inside FP-13's long usage-error list (family `exit_status`) |
| C20 | **no** | 1.0 (S5) | 57 / 77 | 27 / 27 | B merged into the `Path` row node |
| C21 | **no** | 1.5 (S5) | 134 / 239 | 33 / 47 | B merged into the `get_app_dir` row node (family `function`) |
| C22 | **no** | 0 (none) | — | — | B's node is "it still prints its message there": the subject (pause) was cut off |
| C23 | **no** | 2.0 (S2) | 227 / 277 | 119 / 124 | families `option` / `suggestion`; crowded rankings |
| C25 | **no** | 4.0 (S2 S5) | 46 / 265 | 22 / 257 | crowded: both sides share "default" and "option" with hundreds of nodes |
| C26 | yes | 7.0 (S1 S2 S4 S5) | 1 / 23 | 3 / 171 | |
| C27 | yes | 3.5 (S2 S5) | 4 / 115 | 6 / 46 | |
| C29 | **no** | 0 (none) | — | — | B merged into the `Choice` row node; families `choice_matching` / `choice` |

**Pairs proposed: 11 of 24** (C01, C02, C04, C05, C07, C08, C09, C14, C15, C26, C27); the judge's
answer on them is not yet asked. Missed 13, three causes: **an atomizer loss** (C17); **B in a node
with no usable link to A** — a Contract row merged into one node, or a clause cut from its subject
(C06, C12, C20, C21, C22, C29); **ranking** — A and B in different families and a crowded top 6
(C03, C10, C13, C18, C23, C25). The store is left with every node unchecked, so a later
`sddc compile` would judge the 1 842 pairs (calls *to be measured*; most replay from the lock).

**Correction to the cause count above** (found in step 1b, reading the lock): of the six "no usable
link" items, three are table rows whose `form` cell holds several sentences joined into one node
(C12, C20, C21; C15 is the same shape but was proposed anyway). C06 is a list item: one long
sentence, not a merged row. C29 is a one-sentence row, not merged. C22 is a clause cut from its
subject.

## Step 1b: compiler fix 1, table rows (F3 D43; rel02 D28; 2026-10-30)

Owner: "go ahead, start with the table-row merging fix".

**What the lock showed.** Haiku's Q-ATOM answer for each of those rows lists every sentence separately
(`sentences`) and then gives them as **one** atom, as the prompt asks ("A table row is ONE claim").
F3 D34 (rel01) also folds a row's atoms into one in code. So the merge is by design, made for tables
whose cells are parts of one rule; the Contract's `form` cells instead hold independent sentences.

**Change, spec first** (suite **770 passed**, 767 + 3 new):

| Where | What |
|---|---|
| `sdd/specs/F3_atomizer/spec.md` | §4.5 step 0, **D43**, **AC-3.42**, traceability row, header note |
| `sdd/design/rel-02/rel02_brainstorm.md` | decisions log **rel02 D28** |
| `tests/test_atomize_pipeline.py` | `test_ac_3_42_*` (3): a cell of several sentences splits; a key cell with no quote still leads; D34's one-fragment-per-cell row stays one claim |
| `src/sdd_compiler/atomize/pipeline.py` | `row_sentences` (new), called from `one_criterion` for every table row; no model call, no prompt change |

**Re-measured** (`work/compile-d43`: the same store recipe as step 1a, step 1a's lock copied in so
Q-ATOM replays; `python3 notes/compile_to_pairs.py work/compile-d43`): **5 calls, $0.031 est.**, 83
replayed; 64 nodes formed (55 in step 1a); 258 nodes checked, **1 884 pairs proposed** (1 842).
`python3 notes/rank_pairs.py work/compile-d43` (step 1a's ranks kept in `work/pair_ranks-step1a.json`).

| Item | Step 1a | After D43 | B node now |
|---|---|---|---|
| C12 | no evidence | no evidence (rank from B: none of 190) | "`DateTime(formats=None)` … When several formats match a value, the last matching format is used." |
| C15 | proposed (8 / 20 from B) | proposed (129 / 227 from B; 6 / 10 from A) | "`FloatRange(…)` … With `clamp=True` and an open bound, …" |
| C20 | 57 / 77 from B | 131 / 149 from B | "`Path(…)` … With `resolve_path=True`, a leading `~` is first expanded …" |
| C21 | 134 / 239 from B | 46 / 56 from B | "get_app_dir(…) -> str … On Unix the directory is always under `~/.config`" |
| all 24 | 11 proposed | **11 proposed** (the same 11) | |

**Finding: D43 does what it says, but recovers no pair.** Each planted sentence is now its own node,
so a judge shown the pair would see that sentence and not the whole row. Retrieval still does not
propose it, because the two sides carry **different terms**: C12's A side is tagged
`date_time_format` only, its B side `parameter_type`, `format`, `value` (no `broader` link between
`format` and `date_time_format`); C20's A side `leading_tilde`, B `path`, `parameter`; C21's A side
`application_directory` and three more, B `path`. Shared keywords are few ("formats"; "leading",
"expanded"). ⚠ **Leading each piece with the first cell has a cost:** the signature's words become
keywords of every piece, so a piece now ranks against all the entry's other nodes: C20's rank from
B fell from 57 to 131, C15's from 8 to 129 (C15 is still proposed from its A side). The cause of all
remaining misses in this group is therefore the ranking (cause 3), which also covers C03, C10, C13,
C18, C23, C25. Whether D43 helps once ranking is fixed is *to be measured* then; if it does not,
D43 is reverted.

## Step 1c: compiler fix 2, ranking (F5 D15, D16; rel02 D29; 2026-10-30)

Owner: "go ahead with your suggested ranking fix".

**Tried offline first** (no model call; the compiler's ranking with each change patched in, on
`work/compile-d43` and, as a hold-out, round 14's `work/compile-planted-v2`; script kept in the
session scratchpad as `variants.py`, not in the repo):

| Variant | Round 17 (of 24) | Pairs | Round 14 (of 7) | Pairs |
|---|---|---|---|---|
| current (after D43) | 11 | 1 893 | 6 | 1 761 |
| S1 follows `broader` ("kin") | 12 | 1 889 | 7 | 1 740 |
| kin + term names by last word | 12 | 1 881 | 7 | 1 738 |
| rare shared keyword (≤ 1 % of nodes) | 13 | 1 906 | 6 | 1 763 |
| rare (≤ 0.5 %) | 11 | 1 890 | 6 | 1 762 |
| kin + rare 1 % | 14 | 1 900 | 7 | 1 741 |

Kept: kin (**F5 D15**) and rare keyword at 1 % (**F5 D16**, new source **S9**); dropped: term names
by last word (no pair gained).

**Change, spec first** (suite **775 passed**):

| Where | What |
|---|---|
| `sdd/specs/F5_retrieval/spec.md` | S1 row, new S9 row, score formula, CT-5.2 `rare_keyword_share`, **AC-5.19**, **AC-5.20**, **D15**, **D16**, traceability, header note |
| `sdd/design/rel-02/rel02_brainstorm.md` | decisions log **rel02 D29** |
| `tests/test_retrieval_sources.py` | `test_ac_5_19_*` (1), `test_ac_5_20_*` (3), weights test updated |
| `tests/test_profile.py` | `test_d16_rare_keyword_share_defaults_and_is_validated` |
| `src/sdd_compiler/retrieval/sources.py` · `score.py` · `select.py`, `src/sdd_compiler/profile.py` | `_same_family` follows `broader`; `keyword_counts`, `_rare_keywords` (S9, weight 1.0, cap 2.0); counts made once per `propose`; profile key with validation |
| `tests/golden/export/export.meta.json` | regenerated: only `store_hash` changed (the default profile has one more line) |

A defect found by the existing suite on the way: in a 2-node graph every shared word was "rare".
S9 is now off when 1 % of the graph is under 2 nodes (spec and AC-5.20 say so).

**Re-measured with the real code** (`work/compile-d16`, the same store recipe, step 1b's lock: **0
calls, $0.00**, 100 replayed; 1 896 pairs; `python3 notes/rank_pairs.py work/compile-d16`; step 1b's
ranks kept in `work/pair_ranks-step1b.json`):

| Item | Step 1b | Step 1c | What moved it |
|---|---|---|---|
| C03 | 9 | **proposed** (4 from A) | S1 now fires: `parameter_callback` is a kind of `callback` (8.0) |
| C13 | 7 | **proposed** (3 from A) | S9: a rare shared keyword |
| C20 | 27 | **proposed** (1 from A) | S9: "tilde" |
| C14 | 6 | 7 (lost) | S9 lifted other candidates above it |
| C15 | 6 | 7 (lost) | the same |
| all | 11 of 24 | **12 of 24** | |

Round 14's store with the real code: **7 of 7** within the cap (P3 6th, P4 3rd).

**Findings.** (1) D15 is a clean gain: round 14's P4 / round 17's C03, missed in every compile since
round 14, is now proposed, and nothing was lost by it in either store. (2) D16 helps where a rare word
is shared (C13, C20) but, as built, also pushes two borderline pairs (6th) out of the cap: net +1. The
offline sketch scored the rare word inside S5 (14 of 24); the difference is recorded, not tuned to
the key. (3) **The cap of 6 is the binding constraint**: C14, C15 and C06 sit at 7th to 11th. (4)
Still out of reach of any ranking change: C12, C22, C29 score nothing or almost nothing; C10, C18,
C23, C25 rank 38th to 228th. Their two sides share neither a term nor a rare word: these need the
term tags themselves to meet (atomizer), or a different signal.

## Step 1d: compiler fix 3, an atom keeps what it is about (F3 D44; rel02 D30; 2026-10-30)

Owner: "go ahead with option 2 as you suggested first. then highlight when we can move on to option-3
fix".

**Traced in the lock** (`work/compile-d16/.sdd/lock/q-atom.jsonl`, answers J-006373 and J-006371):

| Item | Block | What Haiku's answer did |
|---|---|---|
| C17 | PRD 381, "Abort — user declined …, two different values typed into a confirmation prompt, … — yields …, writes …, and does not run …" | labelled the whole sentence a requirement, then gave three atoms quoting only the three predicates; the subject, with the planted cause, was in no atom. G3 passed: it only checks that an atom touches the sentence |
| C22 | PRD 346, "Pause must not block in non-interactive runs; it still prints its message there." | two atoms; the second, "it still prints its message there", names no subject. Q-DESC had resolved it (`canonical.subject` = "Pause"), but keywords come from the text only (F2 D4), so retrieval could not see "pause" |

**How common** (same lock, no model call): 21 of 761 claim sentences leave an opening of three or
more words uncovered, often a condition or scope ("For subcommands listed on a group help page,",
"In the in-process runner (FP-14),"); 40 of 1 029 nodes open with a pronoun.

**Change, spec first** (suite **778 passed**, 775 + 3):

| Where | What |
|---|---|
| `sdd/specs/F3_atomizer/spec.md` | §4.5 step 0, **D44**, **AC-3.43**, traceability, header note |
| `sdd/design/rel-02/rel02_brainstorm.md` | decisions log **rel02 D30** |
| `tests/test_atomize_pipeline.py` | `test_ac_3_43_*` (3): an uncovered opening leads every atom of its sentence; a pronoun atom is led by its sentence's first atom; atoms that keep their subject are unchanged |
| `src/sdd_compiler/atomize/pipeline.py` · `qatom.py` | `keep_subjects` (new), applied to every block that is not one claim by its form, also after an AC-3.12 re-ask; Q-ATOM's claim sentences kept on the outcome. Verbatim spans only, no model call |

**Re-measured** (`work/compile-d44`, the same recipe, step 1c's lock): **5 calls, $0.0232 est.**
(Q-DESC for the re-led atoms), 96 replayed; 1 899 pairs. `python3 notes/rank_pairs.py work/compile-d44`
(step 1c's ranks kept in `work/pair_ranks-step1c.json`):

| Item | Step 1c | Step 1d | B node now |
|---|---|---|---|
| C17 | no node held B | node exists, **not proposed** (31st from A, 35th from B; score 1.0) | "Abort — user declined …, two different values typed into a confirmation prompt, … — … yields a non-zero abort-class exit (**1**)" (family `abort`) |
| C22 | score 0 | **proposed** (2nd from A) | "Pause must not block in non-interactive runs … it still prints its message there" |
| all | 12 of 24 | **13 of 24** | |

**Finding.** Both atomizer defects are fixed: every planted sentence is now in a node. C22 is
gained. C17 is now a ranking case: its A side ("A confirmation prompt … rejects a mismatch by asking
the pair again", family `confirmation_prompt`) and its B node (family `abort`) share only the common
words "confirmation" and "prompt".

**Where the 11 misses stand now** (all ranking or terms; none is an atomizer loss any more):

| Group | Items | Best rank | Why |
|---|---|---|---|
| Just outside the cap | C14, C15, C06 | 7, 7, 11 | crowded top 6 |
| Weak link, different families | C17, C21, C10 | 31, 36, 38 | share only common words |
| No shared term or rare word | C12, C18, C23, C25, C29 | 21 to 228, or none | A and B tagged with unrelated terms |

## Step 1e: compiler fix 4, a node's topic named by the other (F5 D17; rel02 D31; 2026-10-30)

Owner: "go ahead with option 3 as you suggested".

**Read first** (the 8 pairs left after step 1d, tags from `work/compile-d44`, no model call): in
most of them one side's topic (`family`) is tagged on the other side in another role, or written out
in its text without a tag:

| Pair | A's topic | Found on the other side |
|---|---|---|
| C10 | `environment_value` (B's topic `boolean_flag`) | A carries `boolean_flag` as a scope term |
| C17 | `confirmation_prompt` | B's text says "confirmation prompt" (not tagged) |
| C18 | `conversion_failure` | B's text says "conversion failure" (not tagged) |
| C23 | `option` | B carries `option` as a response term |
| C21 | `application_directory` (a kind of `directory`) | B's text says "the directory" |
| C12, C25, C29 | `date_time_format`, `default_value`, `choice_matching` | only loosely ("formats", "the default", "matched") |

So the change was made **in retrieval, from tags already stored**, instead of re-tagging terms with a
new Q-DESC rule (model calls for every node; a prompt change re-asks every block, F3 D21).

**Variants tried offline** (scratchpad `variants3.py`; on top of D15, D16, D43, D44):

| Variant (new source S10) | Points | Round 17 | Pairs | Round 14 | Lost |
|---|---|---|---|---|---|
| current | — | 13 | 1 910 | 7 | |
| topic among the other's terms | 2.0 | 15 | 1 954 | 7 | |
| topic among the other's terms | 3.0 | 14 | 1 980 | 7 | C03 |
| topic's multi-word name in the other's text | 2.0 | 14 | 1 909 | 7 | |
| topic's multi-word name in the other's text | 3.0 | 15 | 1 907 | 7 | |
| **terms or multi-word name in text** | **2.0** | **16** | **1 949** | **7** | **none** |
| terms or multi-word name in text | 3.0 | 15 | 1 968 | 7 | C03 |
| terms or any name in text (one word too) | 2.0 | 14 | 1 941 | 7 | |

Kept: the bold row as **F5 D17**. One-word names are left out of the text match: "option" is in 137
of the store's 1 028 node texts, "value" in 132, "command" in 136.

**Change, spec first** (suite **779 passed**):

| Where | What |
|---|---|
| `sdd/specs/F5_retrieval/spec.md` | S10 row, score formula, **AC-5.21**, **D17**, traceability, header note |
| `sdd/design/rel-02/rel02_brainstorm.md` | decisions log **rel02 D31** |
| `tests/test_retrieval_sources.py` | `test_ac_5_21_*`; weights test; AC-5.9's order check now sorts sources by number (S10 after S9) |
| `src/sdd_compiler/retrieval/sources.py` · `score.py` | `_topic_named`, `_names` (whole words, case ignored, space / `_` / `-` alike, a final `s` allowed); weight 2.0 |

**Re-measured with the real code** (`work/compile-d17`, step 1d's lock: **0 calls, $0.00**; 1 936
pairs; step 1d's ranks in `work/pair_ranks-step1d.json`): **16 of 24** proposed (C14, C15, C17
gained; none lost), the same as offline. Round 14's store: **7 of 7** (P3 now 2nd, was 6th).

**The 8 still not proposed:**

| Item | Best rank | What is left |
|---|---|---|
| C18 | 13 | S10 fires (3.5), still a crowded top 6 |
| C06 | 16 | B is the whole `command` keyword list as one sentence |
| C12 | 21 | `date_time_format` against `DateTime`: no shared term, word, or name |
| C10 | 27 | S2 + S10 (4.0), crowded |
| C21 | 36 | `application_directory` against `path`; "directory" is one word |
| C25 | 81 | `default_value` against `parameter` (the row's key `show_default` is not in the node's text) |
| C23 | 95 | `option` against `suggestion`; `option` is a crowded topic |
| C29 | none | `choice_matching` against `choice`: no shared term or word ("match" vs "matched") |

## Step 2: full compile from a new store, with judging (2026-10-30/31)

Owner: "run the full from-scratch compile with judging".

**Run.** `bash notes/compile_full.sh` (round 13c's driver, copied; new store `work/compile-full` by
`sddc init`, round 13c's case006 profile, the planted spec, the compiler of steps 1b–1e, and the step
1e lock copied in so questions already answered word for word replay). 3 passes, 22:34 → 01:31
(`work/compile-full/compile.log`); no usage-limit wait.

| Pass | Calls | $ est. | Pairs judged | Pairs replayed | Conflicts opened |
|---|---|---|---|---|---|
| 1 | 300 | 1.2087 | 1 376 | 0 | 60 |
| 2 | 300 | 1.102 | 2 124 | 1 372 | 56 |
| 3 | 157 | 0.5828 | 1 102 | 3 002 | 37 |
| **total** | **757** | **2.8935** | | | |

(`work/compile-full/compile-<n>.json`; pass 1 also atomized: 1 044 nodes, 1 619 atomizer answers
replayed.) The store holds 69 contradictions, 71 duplications, 13 subsumptions, all open
(`notes/recall.json`).

**Compiler recall: 14 of 24** (`python3 notes/recall.py work/compile-full` → `notes/recall.json`;
found = a `contradiction` between a side-A and a side-B node):

| Item | Step 1e (incremental): proposed | Full compile | Conflict |
|---|---|---|---|
| C01 | proposed | missed | — |
| C02 | proposed | **found** | CF-000034 |
| C03 | proposed | missed | — |
| C04 | proposed | **found** | CF-000087 |
| C05 | proposed | **found** | CF-000115 |
| C06 | — | missed | — |
| C07 | proposed | **found** | CF-000048 |
| C08 | proposed | **found** | CF-000010 |
| C09 | proposed | **found** | CF-000088 |
| C10 | — | missed | — |
| C12 | — | missed | — |
| C13 | proposed | **found** | CF-000136 |
| C14 | proposed | **found** | CF-000092 |
| C15 | proposed | **found** | CF-000107 |
| C17 | proposed | **found** | CF-000134 |
| C18 | — | missed | — |
| C20 | proposed | missed | — |
| C21 | — | **found** | CF-000129 |
| C22 | proposed | **found** | CF-000128 |
| C23 | — | missed | — |
| C25 | — | missed | — |
| C26 | proposed | **found** | CF-000063 |
| C27 | proposed | **found** | CF-000047 |
| C29 | — | missed | — |

**Every miss is a pair that was never proposed; none was judged and rejected.** Each of the 10 missed
pairs was ranked with the compiler's own scoring on the full store, and the lock searched for a
Q-PAIR answer quoting both sides: none exists. Of the planted pairs that were proposed, the judge
called every one a contradiction (14 of 14).

**Why the full compile differs from step 1e** (16 proposed there, 14 here; C21 gained, C01, C03, C20
lost). Step 1e's store was incremental: only the 23 planted blocks were re-formed, the rest kept round
13c's nodes. Here every block is re-formed under D43 and D44, so many atoms reach Q-DESC with a new
input and get new answers, and **the topic (`family`) Haiku gives a node can change**:

| Item | Node | Step 1e store | Full store | Rank now (from A / from B) |
|---|---|---|---|---|
| C01 | A, "When no parent is given, the runner removes that directory on exit" | family `directory` | `isolated_filesystem` | 42 / 11 |
| C03 | B, the glossary row "**Callback** … not called for a parameter that was omitted" | `parameter_callback` (a kind of `callback`: D15 fired) | `value` (same terms) | 75 / 147 |
| C20 | A, "a leading tilde is not expanded" | not re-formed; `leading_tilde` | led by its sentence's opening (D44), "Optional checks, each independently selectable: … a leading tilde is not expanded"; `path_type` | 12 / 26 |

**Findings.** (1) Recall on a full compile is **14 of 24 (58 %)**, all losses in pair-picking, none in
judging. (2) The incremental measurements of steps 1a–1e were a **guide, not a measure**: they mixed
re-formed planted blocks with round 13c's old nodes, and Haiku's topic tags vary between runs; the
step 1e figure of 16 overstated the full-compile result by 2. (3) Retrieval now leans on `family`
(S1 with D15, S10), so **a change in one Q-DESC answer can drop a pair** (C03). (4) D44 can also
move a node's topic by adding its sentence's opening (C20). (5) **Not measured: the recall of the
compiler before the fixes on a full compile**; steps 1a–1e compared incremental stores only, so the
gain the four fixes give on a full compile is *to be measured* (a full compile with the code before
rel02 D28, about the same cost as this one). (6) The 55 contradictions that are not planted items
are for the owner to judge as real or false; round 13c's unplanted full compile ended with 68
contradictions (`../r13c-zero2repo-3cases/work/compile-case006/compile.log`).

## Step 3: baseline, the compiler before the fixes, on the same full compile (2026-11-01)

Owner: "go ahead with the baseline full compile first". `bash notes/compile_baseline.sh`: the
compiler as committed before rel02 D28 (`6c40e75`, exported with `git archive HEAD src` into
git-ignored `work/baseline-src`; the working tree untouched), otherwise exactly step 2's run (new
store `work/compile-baseline`, planted spec, round 13c's profile, the same step 1e lock). 3 passes,
15:39 → 18:07: 300 + 300 + 48 = **648 calls, $2.4576 est.** (`work/compile-baseline/compile-<n>.json`).
Store: 70 contradictions, 71 duplications, 9 subsumptions. Scored with the same `notes/recall.py`
(result kept in `work/recall-baseline.json`; step 2's in `work/recall-full.json` and `notes/recall.json`).

| Item | Baseline (before D28–D31) | Step 2 (with D43, D44, D15, D16, D17) |
|---|---|---|
| C01 | missed | missed |
| C02 | **found** | **found** |
| C03 | missed | missed |
| C04 | **found** | **found** |
| C05 | missed | **found** |
| C06 | **found** | missed |
| C07 | **found** | **found** |
| C08 | **found** | **found** |
| C09 | **found** | **found** |
| C10 | missed | missed |
| C12 | missed | missed |
| C13 | **found** | **found** |
| C14 | **found** | **found** |
| C15 | **found** | **found** |
| C17 | missed | **found** |
| C18 | missed | missed |
| C20 | missed | missed |
| C21 | missed | **found** |
| C22 | missed | **found** |
| C23 | missed | missed |
| C25 | missed | missed |
| C26 | **found** | **found** |
| C27 | **found** | **found** |
| C29 | missed | missed |
| **recall** | **11 of 24** | **14 of 24** |
| calls, $ est. | 648, 2.4576 | 757, 2.8935 |

**Gained by the fixes:** C05, C17, C21, C22 (C17, C22: the atomizer fix D44, which gave their planted sentences a node — the baseline has no node for C17's; C05, C21: cause not traced).
**Lost:** C06 (found by the baseline; in step 2 its pair ranked 13th).

**Finding.** On one full compile each, the fixes raise recall from 11 to 14 of 24 (+3: 4 gained, 1
lost) for 109 more calls (+17 %). ⚠ One run per arm: between step 1e and step 2, three items changed
outcome from Haiku's tag variance alone, so a difference of 3 is **not shown to exceed run-to-run
variation**. Repeat full compiles per arm would be needed to state it (≈ $2.5–2.9 est. each).

## Step 4: options 1 and 2 tested offline on the full store (2026-11-01, no model call)

Owner: "Then do 1 and 2, which are cheap and general." Tested on `work/compile-full` with the
compiler's own ranking (scratchpad `variants4.py`); pair counts = `propose()` with every node
unchecked, as in a first compile.

| Change | Planted pairs within the cap | Pairs to judge |
|---|---|---|
| current (cap 6) | 14 of 24 | 4 609 |
| **1.** S10 also through `broader` (a node's topic is a parent of one of the other's terms) | 14 (C03 72nd → 62nd) | 4 622 |
| **2.** cap 7 / 8 / 10 | 14 / 14 / 14 | 5 344 / 6 099 / 7 572 |
| **2.** cap 12 | 16 (C01 11th, C20 12th) | 9 058 |
| **2, narrow.** every same-block pair judged, outside the cap | 15 (C01) | 4 609 + 1 247 |

**Finding: neither option is worth building.** Option 1 gains nothing. Option 2 gains 2 pairs only at a
cap of 12, for 97 % more pairs to judge (judge calls scale with pairs: 8 per call); the same-block
rule gains 1 for 27 % more. Nothing changed in the code. The misses left rank 11th to 99th
(C29 has no score at all), so they are not near the cap: they need the two sides' tags to meet.

## Step 5: the oracle export, every planted conflict flagged (2026-11-01, no model call)

Owner: "the course project focuses more on the code-generation quality and benchmark testing [...]
should we hack through and try to force all 24 conflicts into the spec-graph export [...] use the
24-conflict export to verify the code generation [...] find a way to hack forced 24-conflicts to
graph export".

**What it is, for the report:** an **oracle export**: the compiler's own graph and export from step 2,
with the 10 planted conflicts the compiler missed **added from the answer key**. It isolates the
agent's use of flagged conflicts from the compiler's recall (14 of 24, step 2). It is not a compiler
result and must not be reported as one. Opus was not used: every miss was in pair-picking (code),
so a stronger model in the model steps would not have forced them in.

**How** (`python3 notes/oracle_store.py work/compile-oracle`, on a copy of `work/compile-full`; the
measured step 2 store is untouched):

1. **False alarms judged false on the owner's behalf**, as round 13c did for case006
   (`../r13c-zero2repo-3cases/notes/verdicts-case006.tsv`, 68 contradictions, all false): of the 55
   contradictions that are not planted items, 20 have the same two texts as a round-13c conflict and
   take its verdict and reason; the other 35 were read one by one: **31 false** (a rule and its stated
   exception, two modes, two cases, two senses of a word), **4 left open** because a planted sentence
   really contradicts a second original sentence (CF-000016 and CF-000100: C15 against PRD 196 and
   PRD 208; CF-000072: C02 against PRD 143; CF-000151: C10 against PRD 192, its own bullet). All 55
   with reasons in `notes/oracle_verdicts.tsv`; recorded with the compiler's `record_adjudication`.
2. **10 contradictions added** (C01 CF-000154; C03 CF-000155; C06 CF-000156; C10 CF-000157; C12 CF-000158; C18 CF-000159; C20 CF-000160; C23 CF-000161; C25 CF-000162; C29 CF-000163), each between the item's side-A and side-B node, quoting the
   answer key's phrases, through the compiler's `write_graph` (derived fields and store checks run).
   Each cites a judgment record of kind `answer-key`, backend `answer-key`, model `none`, in its own
   file `.sdd/lock/answer-key.jsonl`: it cannot be replayed as a model answer. ⚠ A first build wrote
   "Planted conflict … added by hand" as the rationale, and **the packs print the rationale**: found by
   grepping the export, the store rebuilt with a rationale worded like a judge's ("One claim says …,
   while the other says …; both cannot hold."). The rebuilt export contains none of "planted",
   "answer key", "oracle", "added by hand", "round 17" (`grep -ril`, 0 files). ⚠ Residual tell: the 10
   added rationales share one wording; the judge's 18 others vary.

**Result.** `python3 notes/recall.py work/compile-oracle`: **24 of 24** (kept in
`work/recall-oracle.json`). `sddc --root work/compile-oracle export --allow-open --out
work/export-oracle`: exit 0; MAP "**UNSETTLED: 28** contradiction(s)" (the 24 planted items and the 4
second pairs); 44 506 words (export v3 of rounds 15–16: 40 197); hashes in `work/export-oracle.sha256`.

**Tasks** (`notes/build_task.py`, `notes/check_nop.sh`, copied from round 15):

| Task | Spec | Words | Do-nothing check |
|---|---|---|---|
| `work/tasks/case006-planted24-markdown` | the planted Markdown (`SPEC_DIR=work/spec-planted`) | 14 435 | 0 tests, official 0 (as round 15) |
| `work/tasks/case006-planted24-export-oracle` | `work/export-oracle` (identical by `diff -rq`) | 44 506 | 0 tests, official 0 |

Instructions identical to round 15's (Markdown: byte for byte; export: apart from the word count).

## Step 6: agent runs, Haiku 3 + 3 then Sonnet 3 + 3 (started 2026-11-01 19:44)

Owner: "schedule to run Haiku 3 + 3 runs, then run Sonnet 3 + 3 runs, then score them. remember to
avoid daily credit limit and resume works after the credit limit reset."

| Item | Value |
|---|---|
| Formats | planted Markdown (`work/tasks/case006-planted24-markdown`) · oracle export, 24 of 24 flagged (`work/tasks/case006-planted24-export-oracle`; step 5) |
| Order | Haiku: Markdown, export × 3, interleaved; then Sonnet the same (`queue.tsv`, 12 rows) |
| Agent | Claude Code 2.1.296 in Harbor, tools `Bash Edit Read Write`, allow-list; `trial.env` as round 16 ($10 ceiling, 9 000 s) |
| Driver | `../run_queue.sh` started detached (`nohup setsid`), log `run_queue.log`. It pauses new runs at 0.90 of the 5-hour window or 0.95 of the 7-day window, and a run stopped by a limit is renamed `.limited-<ts>` and rerun from the start after the reset |
| Scoring | `notes/score.py` (round 15's, adapted: the 24 items, footprint union 31, **core 445**, `PHRASES` from `notes/plant.py`, keyword triage per item); dry run on round 16's `r16-sonnet-export-1` passed (472 / 476, core 441 / 445, all A); then `NOTES.md` read into `notes/detection.tsv` under the strict rule above, the three detection counts, and the owner's audit sheet |

## Step 7: results (scored 2026-11-02)

**Runs.** All 12 finished, 2026-11-01 19:44 to 2026-11-02 02:24 (`run_queue.log`). One limit
pause before `r17-haiku-markdown-2` (17 min); one run cut off by the 5-hour limit
(`r17-sonnet-export-2`, 15 turns, $1.50 est.; kept as
`work/jobs/…-r17-sonnet-export-2.limited-20261101T225101`, not scored) and rerun after the reset.
Scored runs cost **$18.95 est.** (`results.json`); with the cut-off attempt, $20.46 est. The
subscription token is in none of the 12 agent archives (`grep` for its prefix: 0 hits each).

⚠ **`r17-haiku-markdown-2` stopped early**: 15 turns, $0.09 est., one 13 kB file. Its last message:
"I stopped here because the remaining budget is small", which is wrong ($10 ceiling). The hidden
tests failed at import (`cannot import name 'INT'`), so 0 / 476. Like round 15's stopped run, it is
**left out of the means** below and shown in the per-run columns. The Haiku Markdown arm is n = 2.

**Sources.** Tests and sides: `notes/score.py runs/*/` → `notes/scores.json`. Named: Claude Code's
reading of each `NOTES.md` under the strict rule → `notes/detection.tsv`, to be audited by the owner
on `notes/detection_audit.md` (`notes/audit_sheet.py`). Percentages and means are computed from
those two files.

### The two validation sets

| Model | Format | Set 1: core passed / 445, per run | Set 1 mean | Set 2: named / 24, per run | Set 2 mean | Mean of the two |
|---|---|---|---|---|---|---|
| Haiku | Markdown | 433 · *(stopped)* · 414 | 95.2 % | 15 · *(0)* · 7 | 45.8 % | 70.5 % |
| Haiku | oracle export | 436 · 420 · 433 | 96.6 % | 22 · 23 · 24 | 95.8 % | 96.2 % |
| Sonnet | Markdown | 431 · 439 · 442 | 98.3 % | 16 · 15 · 20 | 70.8 % | 84.6 % |
| Sonnet | oracle export | 439 · 429 · 439 | 97.9 % | 12 · 1 · 13 | 36.1 % | 67.0 % |

All 476 tests, for reference only (they include the footprint tests, which reward side A): Haiku
Markdown 462 · 0 · 440; Haiku export 465 · 449 · 461; Sonnet Markdown 452 · 462 · 472; Sonnet export
470 · 458 · 465.

**Set 1.** The export did not make the code worse on the core: Haiku 96.6 % vs 95.2 %, Sonnet 97.9 %
vs 98.3 %. Both differences are smaller than the spread between runs of one arm (Sonnet Markdown
431–442, Sonnet export 429–439); with n = 3 (Haiku Markdown n = 2) no difference is shown either way.

**Set 2, strict rule.** Haiku named far more with the export (95.8 % vs 45.8 %). Sonnet named
fewer with the export (36.1 % vs 70.8 %), and one Sonnet export run named 1 of 24.

⚠ **Why Sonnet's export score is low: its notes cite the export's conflict ids with a topic, not the
two sides.** Every one of the 6 export runs lists **all 24** items in a table keyed by `CF-` id, each
with the side it built (checked by id against `NOTES.md`). Haiku wrote both sides in each row
("first set wins (FP-03) vs last set wins (Interface)"); Sonnet often wrote only a topic ("| 088 |
envvar list | first name that is set wins |"). The rule, written before the runs, says a conflict id
without both contents is not enough, so those rows count as misses. Under a looser reading
(**listed with a choice**: the id plus the side built, the two sides being stated in the export's
pack beside that id), every export run would score 24 / 24. That looser reading is not used for the
headline; whether to adopt it is the owner's call (see Next steps).

### The three detection counts

| Count | Haiku | Sonnet |
|---|---|---|
| 1. Compiler recall: conflicts the export flags | oracle export **24 / 24** (forced, step 5); the compiler alone: 14 / 24 (step 2) | same |
| 2. Named when flagged (export runs) | 22 · 23 · 24 of 24 | 12 · 1 · 13 of 24 |
| 3. Named when not flagged (Markdown runs; the oracle export leaves no item unflagged) | 15 · *(stopped)* · 7 of 24 | 16 · 15 · 20 of 24 |

### Named, and the side built (per run, from `detection.tsv`)

| Run | Named, built A | Named, built B (scenario 3, acceptable) | Missed, built A (lucky) | Missed, built B |
|---|---|---|---|---|
| r17-haiku-markdown-1 | 13 | 2 | 9 | 0 |
| r17-haiku-markdown-3 | 6 | 1 | 14 | 3 |
| r17-sonnet-markdown-1 | 7 | 9 | 8 | 0 |
| r17-sonnet-markdown-2 | 8 | 7 | 8 | 1 |
| r17-sonnet-markdown-3 | 19 | 1 | 4 | 0 |
| r17-haiku-export-1 | 19 | 3 | 2 | 0 |
| r17-haiku-export-2 | 21 | 2 | 1 | 0 |
| r17-haiku-export-3 | 23 | 1 | 0 | 0 |
| r17-sonnet-export-1 | 12 | 0 | 12 | 0 |
| r17-sonnet-export-2 | 1 | 0 | 21 | 2 |
| r17-sonnet-export-3 | 11 | 2 | 8 | 3 |

(`r17-haiku-markdown-2`: nothing named; its probes read A 3, B 2, the rest not built or errors.)
Sonnet Markdown runs 1–2 built B on 9 and 8 items they named: their notes say "the Contract wins"
(run 1) or follow the Contract item by item (run 2). That is scenario 3: it costs footprint tests
(452, 462 of 476), not set 1 or set 2.

### Per item: runs that named it

| Item | Haiku Markdown (of 2) | Sonnet Markdown (of 3) | Haiku export (of 3) | Sonnet export (of 3) |
|---|---|---|---|---|
| C01 | 1 | 3 | 3 | 1 |
| C02 | 0 | 0 | 2 | 0 |
| C03 | 2 | 3 | 3 | 0 |
| C04 | 2 | 3 | 3 | 2 |
| C05 | 1 | 3 | 3 | 2 |
| C06 | 1 | 3 | 3 | 0 |
| C07 | 1 | 3 | 3 | 1 |
| C08 | 0 | 0 | 3 | 3 |
| C09 | 1 | 3 | 3 | 2 |
| C10 | 0 | 3 | 3 | 2 |
| C12 | 1 | 3 | 3 | 2 |
| C13 | 0 | 1 | 3 | 2 |
| C14 | 1 | 1 | 3 | 1 |
| C15 | 1 | 1 | 3 | 1 |
| C17 | 0 | 0 | 3 | 1 |
| C18 | 0 | 1 | 3 | 1 |
| C20 | 2 | 3 | 3 | 0 |
| C21 | 1 | 3 | 3 | 2 |
| C22 | 1 | 2 | 3 | 1 |
| C23 | 2 | 3 | 3 | 1 |
| C25 | 1 | 3 | 1 | 0 |
| C26 | 1 | 1 | 3 | 1 |
| C27 | 1 | 3 | 3 | 0 |
| C29 | 1 | 2 | 3 | 0 |

No Markdown run named C02, C08 or C17; every Haiku export run named C08 and C17, and two named C02.

### Findings

1. **Set 1: the export does not make the code worse** on the 445 core tests, for either model
   (differences within run-to-run spread; n = 3, Haiku Markdown n = 2).
2. **Haiku: the flagged export raised strict detection from 45.8 % to 95.8 %** (22–24 of 24 per run,
   against 15 and 7 from the Markdown).
3. **Sonnet: strict detection fell with the export (70.8 % → 36.1 %)**, but every Sonnet export run
   listed all 24 by id with a choice. The drop is in how the notes are written (a pointer to the
   export's conflict instead of restating it), which the strict rule counts as a miss. The rule does
   not measure "noticed" alone when the input names the conflict for the agent.
4. **One Haiku Markdown run quit after 15 turns** on a false belief that the budget was nearly used up.
   Traced 2026-11-02 (below, "Why `r17-haiku-markdown-2` stopped").
5. These figures use the **oracle export** (a labelled condition: 10 of the 24 flags were added from
   the answer key). They show what the agent does with flagged conflicts, not what the compiler
   finds (14 / 24, step 2).

### Why `r17-haiku-markdown-2` stopped (traced 2026-11-02, no model call)

Owner: "before starting r18, debug why the Haiku Markdown run 2 stopped early". Read from the run's
Claude Code session log (`runs/r17-haiku-markdown-2/agent.tgz`, `sessions/projects/-app/*.jsonl`),
then the same check on every saved run of rounds 14–17 (41 runs: 31 Haiku, 10 Sonnet).

1. **The cut.** After reading the three spec files, Haiku's next response spent the whole output
   limit thinking: 128 000 output tokens, `stop_reason: max_tokens`, no text and no tool call. The
   thinking is not kept in the log.
2. **The resume message.** Claude Code 2.1.296 then sent its stock message: "Output token limit hit.
   Resume directly — no apology, no recap of what you were doing. Pick up mid-thought if that is
   where the cut happened. Break remaining work into smaller pieces."
3. **The misread budget.** Its next text: "Budget is nearly spent, so I'll write a minimal core
   package". The last budget reminder before the cut said used **$0.000214**, remaining $9.9998 of
   $10. Claude Code renders it as "USD budget: $used/$total; $remaining remaining". Haiku took the
   *used* figure as what was left. Later reminders said $9.92 remaining; it did not correct itself.

**Across rounds 14–17** (`grep` on each run's session log):

| What | Runs |
|---|---|
| Hit the output limit once, while thinking, early in the run | 13 of 31 Haiku runs; 0 of 10 Sonnet runs |
| …then read the budget as nearly spent | 4 of the 13. Each quoted the *used* figure as the amount left: $0.0002 (`r2-haiku-markdown-3`, round 14), $0.0004 (`r3-haiku-markdown-decisions-1`, round 14), $0.0008 (`r15-haiku-markdown-1`), "nearly spent" ($0.0002 used; `r17-haiku-markdown-2`) |
| …and stopped with almost nothing built | 2: `r15-haiku-markdown-1` (no code), `r17-haiku-markdown-2` (0 / 476) |
| …recovered at the next reminder | 2: `r2-haiku-markdown-3` ("The budget has been reset to about $9.92"; still 0 / 476, a partial build), `r3-haiku-markdown-decisions-1` ("The budget line I was reading earlier was stale"; 428 / 476) |
| …continued normally | 9 of the 13 |

So it is a fault of the harness and model together, not of the task or the spec format: 3 of 31
Haiku runs (2 stopped, 1 recovered too late) lost their build to it, all in the Markdown arm so far.
That the misreading is caused by the `used` figure is inferred from the quoted numbers matching it
exactly in all 4 cases; the thinking that led there is not in the log. Newer Claude Code (2.1.316,
installed on this laptop) sends a different message for a cut during thinking ("That reasoning was
not kept [...] reason much more briefly"); whether that prevents the misreading is *to be measured*.

## Next steps (each needs the owner's go-ahead)

1. **Audit** `notes/detection_audit.md` (24 tables, 11 runs): agree or correct each reading.
2. **Decide the export reading** for set 2: keep the strict rule as written (headline above), or add
   a second, labelled count, "listed with a choice", for runs whose notes cite the export's conflict
   id plus the side built. Changing the rule after the results must be reported as such.
3. Optional: **rerun `r17-haiku-markdown-2`** (about $0.7–1.0 est., from the other two Haiku
   Markdown runs) to bring that arm to n = 3.
4. Optional, cheaper than more runs: add one line to the task instruction asking the notes to state
   both sides of each disagreement. This changes the instruction from rounds 14–16, so it would be a
   new round, not a rerun.

## Files

| Path | Tracked | What |
|---|---|---|
| `TRIAL.md`, `ANSWER_KEY.md` | yes | This description; planted items, sides, footprints, probes, phrases |
| `notes/sides.py`, `notes/probe.py`, `notes/probe.sh`, `notes/footprint.sh`, `notes/footprint.py`, `notes/plant.py` | yes | Step 0 tools |
| `notes/footprint.json` | yes | Footprint per candidate (test names only) |
| `notes/compile_full.sh`, `notes/compile_baseline.sh`, `notes/recall.py`, `notes/recall.json` | yes | Steps 2–3: full compile drivers (fixed, baseline), recall scorer, step 2's result |
| `trial.env`, `queue.tsv`, `run_queue.log`, `runs/<run_id>/`, `notes/score.py` | yes | Step 6: run conditions, queue, driver log, per-run files, scorer |
| `results.json`, `notes/scores.json`, `notes/detection.tsv`, `notes/audit_sheet.py`, `notes/detection_audit.md` | yes | Step 7: summary per run, scores and sides, detection readings, the owner's audit sheet and its builder |
| `notes/oracle_store.py`, `notes/oracle_verdicts.tsv`, `notes/build_task.py`, `notes/check_nop.sh` | yes | Step 5: oracle store and its verdicts; task builder and do-nothing check |
| `notes/compile_to_pairs.py`, `notes/rank_pairs.py`, `notes/pair_ranks.json` | yes | Steps 1a, 1b: compile to pair-picking, and each pair's rank (the json holds the latest run, now step 1e) |
| `work/` | **no** | Base build, side-B copies, oracle tasks and jobs, planted spec (Zero2Repo has no licence file) |
