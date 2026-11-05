# Interim report: does a compiled specification graph help an AI coding agent?

> MIA 5150, Fall 2026 · draft opened 2026-10-28 by Claude Code for the owner; updated 2026-11-02
> with rounds 17 and 18 (24 planted conflicts, §3.6 and §4.6); **updated 2026-11-03 with round 19**
> (15 planted conflicts in a second case, case010, §3.7 and §4.7); **updated 2026-11-05 with round 20**
> (14 planted gaps in case010, §4.8) · working Markdown, may move to LaTeX
> later. Every figure names its source: a trial's `TRIAL.md` (under `harness/trials/` or
> `harness/benchmarks/`), a run of the register in `sdd/design/rel-02/rel02_methodology_notes.md` §8
> ("reg. *n*"; rounds 17–18 are reg. 117–147, round 19 reg. 148–160, round 20 reg. 161–173), or the report draft `sdd/design/rel-02/rel02_report_draft.md`
> (R1–R5). Every `$`
> is Claude Code's `total_cost_usd`: an **estimated** API-equivalent, not money spent (the runs used a
> subscription). Trials T0–T2, run or prepared on 28 October, are in §4.5.

## Terms used in this report

| Term | Meaning |
|---|---|
| **Specification (spec)** | The documents that say what the software must do. In Zero2Repo: a PRD (product requirements) and an Interface Contract. |
| **Markdown (format)** | The specification files exactly as the benchmark gives them. One of the two formats an agent is given. |
| **Graph** | The compiler's internal record of a specification, in the `.sdd/` folder: one *node* per requirement (a quoted claim from the source), the links between nodes, defined terms, and a *conflict record* for each pair of nodes judged to contradict. The coding agent never reads the graph itself. |
| **Export** (also "graph export") | What the compiler writes *from* the graph for a coding agent to read: `MAP.md` (index and reading instructions), `CHECKLIST.md` (every node id) and one *pack* per area of the spec (the original text plus its claims and any conflicts, both sides quoted). It is the second format. "Export v2" and "export v3" are two exports of the same 7-conflict case006 (§4.5). |
| **Oracle export** | Rounds 17–19 only: the compiler's export with the planted conflicts it missed added by hand from the answer key, so that all are flagged (24 of 24 in rounds 17–18, §3.6; 15 of 15 in round 19, §3.7). It measures what an agent does with flagged conflicts, **not** what the compiler finds. |
| **Conflict / contradiction** | Two sentences of the specification that cannot both be built. *Planted* conflicts are ones we added on purpose (§3.4, §3.6). |
| **Side A / side B** | The two sentences of a planted conflict. **A** is the case's original sentence (case006, or case010 in round 19): the real library's behaviour, and what the hidden tests check. **B** is the sentence we planted elsewhere that says the opposite. Example (P6): A "maximum content width 80 columns", B "100 columns". Nothing in the spec says which side is right. |
| **Unsettled / settled** | Unsettled: the export shows both sides and leaves the choice to the agent (`--allow-open`). Settled: the owner has ruled, and the export carries only the ruling. `DECISIONS.md` is the same rulings as a short plain file beside the Markdown. |
| **Named (detection)** | Rounds 14–16: the agent's `NOTES.md` mentions both sides as a disagreement, or the choice it made between them. Rounds 17–18, **strict rule**: the notes state the *content* of both sides and present them as disagreeing; a conflict id or a topic alone does not count. Read by Claude Code, item by item. |
| **Built side / probe** | Which side the agent's code actually follows, found by a small black-box check (*probe*) run on the saved code. |
| **Footprint** | The hidden tests whose result changes when one planted conflict is built on side B instead of A, measured with no model. These are the tests *related to the conflicts*. |
| **Core score (set 1)** | Hidden tests passed among those no planted conflict touches, i.e. all hidden tests **minus** the footprint tests: 469 of 476 with 7 conflicts (rounds 14–16), 445 of 476 with 24 (rounds 17–18; footprint union 31), 173 of 197 with 15 (round 19, case010; footprint union 24). The footprint tests are left out because they reward side A whether or not the agent noticed the conflict, and the spec does not say A is right. |
| **Set 1, set 2** | Rounds 17–19 report two validation sets side by side: **set 1** = core passed / 445 (round 19: / 173) (build quality, one unit per test); **set 2** = named / 24 (round 19: / 15) under the strict rule (detection, one unit per conflict). Where one figure is wanted, it is the plain mean of the two percentages, shown next to both. |
| **Exposure** | Whether each side's wording appears in what the agent read (its tool results in the transcript). |
| **`lend`** | Our own small benchmark task: a command-line tool for a library that lends tools. 7 Markdown files, 2 120 words, 4 contradictions written in by design, 24 hidden tests (R1). |
| **Turns** | Claude Code's count of agent steps in a run (`num_turns` in its result line). Each turn is one model reply, usually with one or more tool calls (read a file, edit, run a command). More turns means more model calls and usually more cost. |
| **Run, round, batch, trial** | A *run* is one agent building one task once. A *round* or *trial* is a planned set of runs with its own `TRIAL.md`; a *batch* is a later addition to a round under the same conditions. "reg. *n*" is row *n* of the run register. |
| **$ est.** | Claude Code's `total_cost_usd`: an API-price estimate. The runs used a subscription, so no money was billed per run. |
| **Haiku, Sonnet, Opus** | Claude models, smallest to largest: `claude-haiku-5-5`, `claude-sonnet-5-5`, `claude-opus-5-5`. |

## 1. Progress check-in (half page, for Brightspace)

**What is working.** The full pipeline runs end to end: our compiler (`sddc`) turns a folder of
Markdown specifications into a graph and an export, and Claude Code builds the software inside the
Harbor platform from either form, scored by hidden tests. The run register holds 160 model runs (agent runs,
including cut-off attempts, and compiles). The one number: **with 24 conflicts
planted in a 14 435-word specification and all 24 flagged in the export, both Claude Haiku and Claude
Sonnet named every one, with both sides, in all 3 runs each (24 of 24); from the plain Markdown
Sonnet named 17–18 and Haiku 7–10.** Sonnet's build quality was the same from either format (core
tests 98.4 % vs 98.6 %). Our compiler on its own flags 14 of the 24 (11 before this round's fixes);
the other 10 flags were added from the answer key, so the 24 of 24 is an upper bound for the agent,
not a compiler result. **A second case (round 19, 15 conflicts in case010) repeats the pattern:**
named 93–96 % from the flagged export against 51–67 % from the Markdown, and the same core score from
either format for Sonnet (96.9 % vs 97.1 %); the compiler alone flags 9 of the 15.

**What is blocked.** Nothing is hard-blocked. Three things slow us. (1) The subscription's usage
limit: runs pause at the 5-hour and weekly windows (in each of rounds 16–18 one run was cut off and rerun).
(2) The check of how agents' notes were read is done by one reader so far; my own audit sheets for
rounds 14–18 are prepared but not yet filled in. (3) Haiku's build quality fell in round 18 for a
reason we cannot yet separate (three run conditions changed together, §4.6). Round 19 ran under
round 18's conditions and its audit sheet is ready too (`r19-…/notes/detection_audit.md`).

**What changed since the proposal.** Harbor is the platform; the public benchmarks are DevEval and
Zero2Repo instead of ProjectEval, RealBench and Doc2Feat-Bench, which did not fit (inputs too small,
not obtainable, or edits to an existing codebase). The flat single-prompt format was not built, and
Opus was tried on one benchmark only and then dropped. We added conflicts planted on purpose, because
no public benchmark has specifications that contradict themselves, and raised them from 7 to 24 (5 %
of the hidden tests). The claim has narrowed: **the graph does not raise test scores** in any setting
so far; what it does is make the agent **notice and report contradictions** in the specification.

**Plan or backup.** We are on a version of the **backup** (proposal §10): two formats (specification
as written vs graph), Haiku and Sonnet. It differs from the backup in its main measure (tests passed
and conflicts noticed, not omission rate) and has more tasks and runs than the backup's 36.

*(Sources: §4 below; `harness/trials/r17-zero2repo-case006-conflicts-24/TRIAL.md`,
`harness/trials/r18-zero2repo-case006-notes-both-sides/TRIAL.md`,
`harness/trials/r19-zero2repo-case010-conflicts/TRIAL.md`.)*

## 2. Claim and question

**Claim as proposed** (proposal §2): *an AI coding agent produces code of higher quality from a
structured, graph-based specification than from the same specification given as a single long flat
prompt or as tiered SDD files*, measured by code quality, hallucination and specification omission.

**What the evidence supports now.**
- **Not supported: better code.** In every setting tested (three benchmarks, two
  models, 1 196 to 18 964 words of specification) the export did not change the hidden tests passed
  by a margin that survives reading the failures (§4). With 24 planted conflicts, the export did not
  make Sonnet's code worse either (set 1, §4.6), nor with 15 on a second case (§4.7). Haiku's core
  was higher from the export in both rounds 18 and 19, by less than its own run spread (§5).
- **Supported: detection, when the conflicts are flagged.** With 7 planted conflicts, the export made
  Haiku report more of them (46 of 49 vs 33 of 49), all of the gain in conflicts whose sides sit in
  different documents; Sonnet named almost all from either format (4 runs). With 24, the gain shows
  for **both** models: 100 % from the flagged export against 73.6 % (Sonnet) and 36.1 % (Haiku) from the
  Markdown (round 18). On a second case (round 19, 15 conflicts): 93.3 % and 95.6 % against 66.7 % and
  51.1 %. Noticing did not by itself change which side was built.
- **A flag helps only if its rationale names the real difference.** In round 19 one conflict was
  flagged with the right pair but a rationale about another point; it was named in at most 1 of 6
  export runs (§4.7).
- **Limited by the compiler's recall.** The 24-of-24 and 15-of-15 results use oracle exports. The
  compiler alone flags 14 of 24 (every miss a pair never put to the judge, §4.6) and 9 of 15 (4 never
  put to the judge, 2 judged wrongly, §3.7).
- **Supported: decisions travel.** When the owner rules on a contradiction, the ruling reaches the
  code whether it travels inside the export or as a short plain `DECISIONS.md`.

The question for the rest of the term is therefore: *does a compiled graph help an agent find
contradictions in a specification, how much of that help survives the compiler's own recall, and is
it worth its cost?*

## 3. Method

### 3.1 Platform and controls

Claude Code 2.1.296, run headless by Harbor 0.24.0 in a Docker container (`python:3.12-slim`), on a
subscription token (no API key). Tools limited to `Bash`, `Edit`, `Read`, `Write`; network limited to
the model API and PyPI during the agent phase; $10 ceiling per run. **Round 18 changed two of these:**
Claude Code 2.1.316, and no dollar ceiling (`--max-budget-usd` not passed), so no budget reminder
reaches the agent; a run is then bounded by the task's 7 200 s agent limit. The agent's container
holds only the specification (and seed data); hidden tests are copied in after the agent stops. The
two formats are separate Harbor tasks generated by one script, differing only in the specification
folder and one line saying where it starts. Before any model run on a task, the reference solution
must score full marks and a do-nothing agent zero. Models: `claude-haiku-5-5` and `claude-sonnet-5-5`
(8 DevEval runs on Opus). *(Methodology notes §5–6; round 18 `TRIAL.md`, "What changes from round
17".)*

**Run driver** (`harness/trials/run_queue.sh`). Runs one trial's queue in a fixed, interleaved order
(Markdown and export alternate), pauses new runs at 0.90 of the 5-hour usage window or 0.95 of the
weekly one, and reruns from the start any run cut off by a usage limit (the cut-off attempt is kept,
reported with its cost, and not scored). Round 18 added an **early-stop rule, written before any run**:
a run that passed fewer than half the hidden tests *and* shows an output-limit cut or mentions a
budget or token limit in its last message is set aside and rerun once. It did not fire in round 18.

### 3.2 Benchmarks

| Benchmark | What | Specs | Why |
|---|---|---|---|
| `lend` (ours) | Tool-library command-line tool, 7 Markdown files, 4 real contradictions | 2 120 words, 24 tests | A messy spec by design (R1) |
| DevEval (DevBench 2024), repackaged | 4 documents per project (PRD, 2 UML, architecture); 4 projects run | 1 196–1 697 words, 9–42 tests | Public, spec-driven (R2) |
| Zero2Repo (commit `0ecc523`) | Real libraries rewritten as PRD + Interface Contract, names neutralised; 9 Python cases run (case004 + an 8-case sweep) | sweep: 4 860–18 964 words, 80–476 tests | Tests written against a stated contract (R4) |

DevEval as packaged for Harbor leaks the reference and tests to the agent, so we rebuilt each task
clean; scores are not comparable with published ones (methodology notes §3).

### 3.3 The two formats, and how the export is made

- **Markdown:** the specification files exactly as given.
- **Export:** made by our compiler `sddc` in the steps below. The model work is a few narrow,
  closed questions. Plain code checks every answer before it is kept (each quote must appear word for
  word in the source) and does all structure, ids, counting and layout. Each answer is recorded in a
  *lock* file, so a rebuild replays it instead of asking again.

| Step | Command | Done by | What it does |
|---|---|---|---|
| 1. Ingest | `sddc ingest` | code | Splits each Markdown file into blocks (paragraphs, list items, table rows) and records their source |
| 2. Atomize | `sddc compile` | **LLM** (Haiku) + code checks | Asks "which claims are in this block?", then a short description of each claim and how terms relate; code turns the checked answers into nodes |
| 3. Pick pairs | `sddc compile` | code | Chooses, for each node, a small ranked set of other nodes worth comparing it with, by fixed rules (no model) |
| 4. Judge pairs | `sddc compile` | **LLM** (Haiku) + code checks | Asks, 8 pairs per call, whether two nodes duplicate or contradict each other, with quotes; code records the conflicts |
| 5. Rule | `sddc conflicts judge` | **person** | Marks false alarms false and, when settling, records the owner's ruling |
| 6. Export | `sddc export` | code | Writes `MAP.md`, `CHECKLIST.md` and the packs from the graph; unsettled conflicts are shown with both quotes (`--allow-open`) |

The compiler's model is always **Claude Haiku**, called through headless Claude Code. Every recorded
answer in every compile store on the project machine is Haiku's (78 854 answers, counted 2026-10-28
from the stores' `lock` files). No Opus or Sonnet is used in the compiler. Opus and Sonnet appear
only as coding agents (§3.1). The export is 4.7–6.4 times the Markdown's length (R1, R2, R4); the
24-conflict oracle export is 3.1 times (44 506 vs 14 435 words, §3.6).

**One frozen task per condition.** Each condition is built once as a Harbor task, with its
specification folder fixed. Every run of that condition uses that same task. We checked this for the
Zero2Repo rounds 13c–16 from the task checksum Harbor records in each run's `result.json`: every run
of a condition carries the same checksum. On 28 October, for example, **one export v3** was frozen.
All 3 Haiku runs (T1) and both Sonnet export runs (T2) used it (checksum `8325cf29befa…`). The planted
Markdown task is one task for rounds 14, 15 and 16 (`39283f1a2447…`), and export v2 is one task for
all 4 of its runs in round 15. Exports are not rebuilt between runs. A new export (v2, then v3) is a
new condition with its own name. The earlier `lend` and DevEval rounds were not re-checked this way.
Rounds 17 and 18 each use one frozen Markdown task and one frozen oracle-export task; round 18's are
copies of round 17's that differ only in the instruction's notes line (`diff -r`, §3.6).

### 3.4 Planted-conflict design, 7 conflicts (Zero2Repo case006, rounds 14–16)

No public benchmark ships self-contradicting specifications, so we planted 7 conflicts into case006
(the `click` library renamed Optlyn; 14 138 words; 476 tests). The answer key was written before any
compile or run. Each item had to meet five rules (R5):

1. **Built in every past run:** the nearest hidden tests passed in all, or all but one, of 9 earlier
   case006 runs.
2. **Both sides observable** from outside the code, so a probe can tell which was built.
3. **Narrow footprint, measured:** at most 3 hidden tests change between sides, found by patching a
   473 / 476 build to each side and running the tests with Harbor's no-model oracle agent. Two
   candidates failed this rule and were dropped.
4. **Side A is the original library's behaviour** (what the tests check and the model may remember),
   so building A is never taken as evidence of noticing, and every ruling goes to side B.
5. **Real drift:** one sentence or table row, in the spec's own voice, no marker.

The seven: two in one paragraph (P1, and P7 an example contradicting its rule), three across the two
documents (P2, P3, R1), two far apart in one document (P4 a glossary rule, P6 a numeric default).
Footprints total 7 tests (`batch-2/TRIAL.md`, table of the 7 conflicts).

**Measures.** *Core score*: the 469 tests outside the footprints. *Probes*: one black-box check per
item on the saved code, no network, says A or B. *Exposure*: whether each side's unique phrase appears
in a tool result of the transcript. *Stated detection*: one instruction line, the same in both
formats, asks the agent to list disagreements in `NOTES.md`; the notes are read item by item into
`detection.tsv`. *Compiler recall*: planted items the compile reports.

### 3.5 Scorers

Hidden tests via each benchmark's own runner (pytest; Zero2Repo's judge), checked so that only hidden
tests are counted (a fault where agent-written tests were counted was found and fixed in round 8,
R2). On `lend`, `lend_score.py` adds omissions and contradiction sides. On DevEval, each hidden test
was classified by whether the specification states it (R2). On case006, `notes/score.py`,
`probe.py` and `probe.sh` give core, probes and exposure; rounds 17 and 18 use the same scorer
adapted to 24 items and core 445, unchanged between the two rounds.

### 3.6 Planted-conflict design, 24 conflicts (rounds 17–18)

The owner asked for stricter rules: every planted conflict covered by an existing hidden test, and
at least 5 % of the test count, so 24 conflicts for 476 tests. Method as §3.4, with these changes
(round 17 `TRIAL.md`, "Method" and "Step 0"):

1. **Candidates from test names only.** The 476 hidden test names were listed
   (`pytest --collect-only`); no hidden test body was opened. Each name pointing at one behaviour
   with a sentence in the public spec gave a candidate: 30 in all (28 + 2 reserves).
2. **Side-B builds, probes and footprint** as §3.4, on the same 473 / 476 base build. **Kept only if
   the footprint is 1 to 3 tests and no two items share a test.** 24 kept; 6 dropped (footprints of
   6, 4, 6 and 394 tests, one sharing another's test, one with none).
3. **Plant:** each side-B sentence in one place, in the spec's own voice, no marker. Planted spec
   14 435 words (14 138 before). Distances: 2 in the same bullet, 8 far apart in one file, 14 across
   the two files.
4. **Footprint union 31 tests, so core (set 1) = 445.** The footprint tests count in neither set: they
   reward side A whatever the agent noticed.

**Two validation sets** (Terms): set 1 core passed / 445, set 2 named / 24, each reported on its own,
plus their plain mean.

**Strict detection rule, written before any run.** A conflict counts as named only if `NOTES.md`
states the content of side A, states the content of side B, and presents them as disagreeing or as a
choice. A conflict id without both contents, only the side that was built, or a line on the topic
without the disagreement is a miss. Which side was built does not matter for set 2.

**Three detection counts**, so that a compiler miss is not read as an agent miss: (1) compiler recall,
the conflicts the export flags; (2) named when flagged (export runs); (3) named when not flagged
(Markdown runs).

**Compiler work on the 24 (round 17, steps 1–4).** A compile up to pair-picking showed the misses
fell into three kinds: claims lost by the atomizer, claims merged into one node with no usable link
to the other side, and pairs ranked outside each node's top 6. Four compiler fixes were made, spec
first with a failing test each (F3 D43–D44, F5 D15–D17; rel02 D28–D31). On a **full compile from a
new store** the fixed compiler flags **14 of 24** (757 Haiku calls, $2.89 est.); the compiler from
before the fixes, on the same full compile, **11 of 24** (648 calls, $2.46 est.). All 10 misses of the
fixed compiler are pairs never proposed; of the planted pairs proposed, the judge called all 14
contradictions. One full compile per arm, and Haiku's topic tags varied enough between compiles to
change 3 items, so the gain of 3 is not shown to exceed run-to-run variation. Two further changes
(wider pair caps, a broader topic link) were tested offline and not built: the best gained 2 pairs for
97 % more pairs to judge. Compiles in round 17 cost $5.51 est. in all.

**The oracle export (round 17, step 5).** To measure what an agent does with flagged conflicts apart
from the compiler's recall, the 10 missed conflicts were **added from the answer key** to a copy of the
full-compile store, through the compiler's own store writer, each tied to a record of kind
`answer-key` that cannot be replayed as a model answer. The 55 contradictions that are not planted
items were judged on the owner's behalf: 51 false (20 by round 13c's verdicts, 31 read one by one),
4 left open because a planted sentence really contradicts a second original sentence. The export
lists **28 unsettled** contradictions (the 24 and those 4), 44 506 words. A first build printed "added
by hand" in the packs; it was found by searching the export and rebuilt with judge-like wording, after
which no file mentions planting. The 10 added rationales still share one wording.

**The two rounds.**

| | Round 17 | Round 18 |
|---|---|---|
| Notes line of the instruction (both formats, identical) | "If parts of the specification disagree, choose one and list each choice in `NOTES.md` (what disagrees, where, and what you built)." | "…list each disagreement in `NOTES.md`: quote or state what each side says and where it is, then what you built. A conflict id or topic alone is not enough." |
| Claude Code; dollar ceiling | 2.1.296; $10 | 2.1.316; none |
| Early-stop rerun | none | once, by the rule in §3.1 |
| Runs | Haiku 3 + 3, then Sonnet 3 + 3, formats alternated | the same; one Sonnet export run first, as a gate (≥ 22 of 24 named and ≥ 458 of 476 tests), then the other 11 |
| Unchanged | planted spec, answer key, oracle export, footprint, core 445, scorer, strict rule, two sets, three counts | |

Round 18 was started because round 17's Sonnet export notes often gave a conflict id and a topic,
not both sides, which the strict rule counts as a miss (§4.6). Three conditions change together
between the rounds, so a difference between them cannot be put down to one; inside each round the two
formats share all conditions.

### 3.7 Planted-conflict design on a second case (round 19, case010)

The owner asked for round 18 repeated on a second case: Zero2Repo **case010** (the `nltk` library
renamed lingora; 8 412 words; **197** hidden tests), at least 5 % of the tests as planted conflicts,
each covered by a hidden test, and no conflict touching the 20 tests that need packaged model files.
Everything not listed here is as round 18: the notes line word for word, Claude Code 2.1.316, no
dollar ceiling, the early-stop rule (threshold 99 of 197), the strict rule, the two sets and three
counts, the models, n = 3, alternated order and a gate run first. *(Source:
`harness/trials/r19-zero2repo-case010-conflicts/TRIAL.md`, steps 0b–4, and its `ANSWER_KEY.md`.)*

1. **Model files fixed, for scoring only.** Harbor's Zero2Repo tasks never installed case010's 7
   model archives, so 20 of 197 tests could not pass in any earlier run (§6, item 8). The task
   builder now copies them, checked by size and sha256, into the hidden-test folder, which Harbor
   uploads only after the agent stops; a listing from inside the agent's container shows none of them.
   Round 13c's 8 saved case010 builds, re-scored: Sonnet 175–176 → 195–196 of 197, failing none of the
   20. (Zero2Repo's own runner does give its agent these files; we keep them from it.)
2. **Candidates, side-B builds, probes and footprint** as §3.6, from test names only, on a 196 / 197
   base build (round 13c's Sonnet Markdown run 2). 18 candidates; 3 dropped with a footprint of 0;
   **15 kept** (7.6 % of 197). Planted spec 8 610 words. Distances: 1 same bullet, 8 same file, 6
   across files. **Footprint union 24 tests, core (set 1) = 173**, the 20 model-file tests included.
   No footprint test had failed in any of the 8 earlier builds.
3. **Compile.** One full compile of the planted spec with the compiler unchanged since round 17
   (commit `0fed585`): 386 Haiku calls, $1.49 est., 517 nodes. **Recall 9 of 15.** Of the 6 misses, 4
   pairs were never proposed and 2 were judged and rejected: C14's two sides were judged a
   subsumption ("returns none" read as "does not succeed"), and C05's side B reached the judge as the
   fragment "longer n-grams are not scored", cut by the atomizer from the condition that gives it
   meaning. The cut follows the atomizer's own spec (F3 D44 carries a sentence's opening to its other
   claims only in two cases, neither met here), so it is a gap in the spec, not a code defect;
   reported, not changed.
4. **Oracle export.** The 6 misses were added from the answer key as in §3.6, **each with its own
   rationale** (round 17's 10 had shared one wording). Of the 37 other contradictions, 33 were judged
   false and 4 left open as real (a planted sentence that also contradicts a second original one). The
   export lists 19 unsettled contradictions; no file mentions planting.
5. **Gate** (written before it ran): named ≥ 13 of 15 and core ≥ 171 of 173 (the lowest of round 13c's
   four Sonnet builds re-scored). The gate run named 14 but scored 168 on the core, all 5 failures in
   word stemmers; it **failed**, the queue stopped, and the owner chose to run the other 11 ("continue
   the other 11 runs, then score them").

## 4. Results so far

### 4.1 Overview

| Setting | Model | Runs per format | Tests: export vs Markdown | Other result | Source |
|---|---|---|---|---|---|
| `lend`, 2 120 words | Sonnet, Haiku | 1 | 24 / 24 both | Rulings built 2 / 2 via export or `DECISIONS.md`; 0 / 2 when not given | R1; reg. 8–15 |
| DevEval, 4 projects | Haiku, Sonnet | 1 (3 on one) | No difference that survives reading | Only 33 of 82 hidden tests stated in the spec; no run passed an unstated one | R2, R3; reg. 5–6, 19–34 |
| Zero2Repo case004 | Haiku, Sonnet | 2 | Markdown 258 / 258; 2 Haiku export misses from false contradictions; settled export 258 / 258 | Compiler: 18 contradictions, all false | R4; reg. 43–52 |
| Zero2Repo case010, 006, 016 | Haiku, Sonnet | 2 | No test-level difference | Haiku ~2× turns on export; 145 contradictions, all false | R4; reg. 61–84 |
| case006 lean export | Haiku | 2 (export only) | 447, 415 / 476 | Turns did not fall | reg. 85–86 |
| case006, 7 planted, unsettled | Haiku | 7 | Core 437.7 vs 440.6 of 469 | Named 46 / 49 vs 33 / 49 | R5; `batch-2/TRIAL.md`; reg. 87–108 |
| case006, 7 planted, export v3 (F7 D17) | Haiku | 3 (export only) | Core 433, 452, 453 | P7 side B 0 / 3 (was 4 / 4); named 20 / 21 | §4.5; reg. 109–111 |
| case006, 7 planted, unsettled | Sonnet | 2 | Core 465, 465 vs 460 (one Markdown run unscored) | Named 13 / 14 vs 13 / 14 | §4.5; reg. 112–116 |
| case006, 7 planted, settled | Haiku | 3 | Core 455.7 (export) vs 428.3 (Markdown + `DECISIONS.md`) | Rulings built 12 / 12 vs 11 / 12 | R5; reg. 93–98 |
| case006, **24 planted**, oracle export, round 17 | Haiku, Sonnet | 3 (Haiku Markdown 2 scored) | Core 96.6 vs 95.2 % (Haiku), 97.9 vs 98.3 % (Sonnet) | Named, strict: 95.8 vs 45.8 % (Haiku), 36.1 vs 70.8 % (Sonnet) | §4.6; r17 `TRIAL.md`; reg. 122–134 |
| case006, **24 planted**, oracle export, round 18 | Haiku, Sonnet | 3 | Core 91.8 vs 87.6 % (Haiku), 98.4 vs 98.6 % (Sonnet) | Named, strict: **100 vs 36.1 %** (Haiku), **100 vs 73.6 %** (Sonnet) | §4.6; r18 `TRIAL.md`; reg. 135–147 |
| case006, 24 planted, compiler recall | (Haiku compiler) | 1 compile each | — | 14 / 24 fixed compiler; 11 / 24 before the fixes | §3.6; r17 `TRIAL.md` steps 2–3; reg. 120–121 |
| case010, **15 planted**, oracle export, round 19 | Haiku, Sonnet | 3 | Core 91.9 vs 89.8 % (Haiku), 96.9 vs 97.1 % (Sonnet) | Named, strict: **95.6 vs 51.1 %** (Haiku), **93.3 vs 66.7 %** (Sonnet) | §4.7; r19 `TRIAL.md`; reg. 149–160 |
| case010, 15 planted, compiler recall | (Haiku compiler) | 1 compile | — | 9 / 15 | §3.7; r19 `TRIAL.md` step 2; reg. 148 |
| case010, **14 gaps** (facts removed), plain export, round 20 | Haiku, Sonnet | 3 | Core 159.7 vs 162.3 / 175 (Haiku), 171.7 vs 171.7 (Sonnet) | Silent inventions / 14: **11.00 vs 10.67** (Haiku), **13.33 vs 13.33** (Sonnet); all 168 gap builds upstream | §4.8; r20 `TRIAL.md`; reg. 161–173 |

### 4.2 Small specifications (R3)

| Setting | Model | Runs per format | Difference in tests passed | Export run cost / Markdown |
|---|---|---|---|---|
| `lend`, ours, 2 120 words | Sonnet | 1 | none (24 / 24 both) | 1.6 |
| `lend` | Haiku | 1 | none (24 / 24 both) | 2.1 |
| `hone`, DevEval | Sonnet | 1 | none (12 / 12 both) | 1.6 |
| `lice`, DevEval | Haiku | 1 | none (3 / 31 both) | 2.2 |
| `stocktrends`, DevEval | Haiku | 1 | none (3 / 9 both) | 2.2 |
| `arxiv-digest`, DevEval | Haiku | 3 | 2 tests for the export in every run | 2.7 |
| `lice`, DevEval | Sonnet | 1 | none (6 / 31 both) | 1.3 |
| `arxiv-digest`, DevEval | Sonnet | 1 | 1 test (30 vs 29), most likely the live service | 1.9 |
| `stocktrends`, DevEval | Sonnet | 1 | 1 test for Markdown (4 vs 3), on an unstated point | 1.3 |

*Source: R3 table (`rel02_report_draft.md`), from reg. 5–34.* The one steady difference (Haiku,
`arxiv-digest`) concerns where a stated rule is applied, a point the spec leaves open, and does not
appear on Sonnet. A one-time compile cost $0.22–0.50 est. per spec (R3).

### 4.3 Large specifications (R4, round 13c)

Tests passed, two runs per cell; case010 on the 177 scorable tests.

| Case (tests) | Haiku Markdown | Haiku export | Sonnet Markdown | Sonnet export |
|---|---|---|---|---|
| case010 nltk, 8 412 words (177) | 142, 149 | 148, 146 | 155, 156 | 156, 155 |
| case006 click, 14 138 words (476) | 452, 0 ¹ | 425, 467 | 470, 469 | 473, 470 |
| case016 sloptrim, 18 964 words (388) | 381, 378 | 364, 379 | 385, 387 | 387, 388 |

¹ Haiku stopped early and wrote no importable code (see §6, item 10).
*Source: R4; `harness/trials/r13c-zero2repo-3cases/TRIAL.md`; reg. 61–84.* Test by test, no test
fails in every run of one format and none of the other on case010 or case016; on case006 Haiku shows
2 such tests each way. Haiku took 63–87 turns on the export against 33–47; Sonnet 21–38 in both. Runs
cost $38.61 est., compiles $11.16 est. (386, 853, 939 Haiku calls).

### 4.4 Planted conflicts (R5, rounds 14 and 15, conflicts left open)

| Planted conflict | Named, Markdown (7 runs) | Named, export (7 runs) |
|---|---|---|
| P1 isolated folder, same paragraph | 7 | 7 |
| P2 warning channel, prose vs table | 7 | 7 |
| **P3 environment vs default map, across files** | **0** | **7** |
| P4 glossary rule, far apart (never listed by the compiler) | 7 | 6 |
| P6 80 vs 100 columns, far apart | 6 | 7 |
| P7 example against its rule | 3 | 5 |
| **R1 confirm, across files** | **3** | **7** |
| All | 33 of 49 | 46 of 49 |
| Core score of 469, mean (range) | 440.6 (423–457) | 437.7 (400–462) |

*Source: R5; `r15-…-v2/batch-2/TRIAL.md` §"Comparison with round 14"; `notes/detection.tsv` and
`notes/scores.json` of rounds 14, 15 and batch 2 (recounted 2026-10-28: same figures).* The export
runs are 3 with round 14's export (compiler listed 4 of 7) and 4 with round 15's (6 of 7). Every run
read both sides of every item (exposure). Unruled, both formats built side A on almost every item;
the exception is P7, built on side B by all 4 round-15 export runs, 3 of which called the example
"the acceptance criterion" (the export listed it under that heading), against 1 of 7 Markdown runs
(T1 below tests the fix).
Per-run cost: Markdown $0.47–1.30 est., export $0.53–1.74 est.; turns 38–73 and 43–97 (reg. 87–108,
valid runs).

**Settled (round 14, n = 3):** rulings built 12 / 12 from the settled export, 11 / 12 from Markdown +
`DECISIONS.md` (the miss was stated in the notes but not built). Core 455.7 (450–460) vs 428.3
(410–452), inside the earlier Haiku spread on the unplanted spec (409–460) (R5).

**Compiler recall** on the 7 items: 4 of 7 in round 14; 6 of 7 after the D26 fixes, with one more
false alarm (3); P4 left unfixed so as not to fit the answer key (R5).

### 4.5 Trials added for this report (28 October)

**T1: the example fix (F7 D17), Haiku, 3 export runs.** The export was rebuilt with the current
compiler by replaying round 14's model answers (0 calls, $0.00); the only change from round 15's export
is that P7's example is listed as `example of N-000326` instead of under *Acceptance criteria*.

| Run | Core of 469 | Sides P1 P2 P3 P4 P6 P7 R1 | Named (of 7) | Turns | $ est. |
|---|---|---|---|---|---|
| export v3, 1 | 433 | B A A B A A A | 6 (all but P4) | 84 | 0.6927 |
| export v3, 2 | 452 | A A A A A A A | 7 | 58 | 1.1175 |
| export v3, 3 | 453 | A A A A A A A | 7 | 66 | 1.0431 |

P7 was built on side A in **3 of 3** runs, against B in 4 of 4 on the old export. All three runs name
the conflict and choose "the type name" or "the stated rule"; none calls the example an acceptance
criterion. This fits the reading that the old heading caused the B builds, on 3 runs against 4.
Detection held (20 of 21 named). The run that built two B sides named P1 and chose B ("the later,
explicit claim"); for P4 it stated the planted rule as a choice where "the spec was silent", which we
count as not named (marked for the audit). *Source:
`harness/trials/r15-zero2repo-case006-conflicts-v2/batch-3/TRIAL.md`; reg. 109–111.*

**T2: Sonnet, planted case006, Markdown vs export v3, 2 + 2 runs, interleaved.**

| | Markdown | Export v3 |
|---|---|---|
| Named P1 / P2 / P3 / P4 / P6 / P7 / R1 | 2 / 2 / 1 / 2 / 2 / 2 / 2 | 2 / 2 / 2 / 1 / 2 / 2 / 2 |
| Named, all | 13 of 14 | 13 of 14 |
| Built side B | none | none |
| Core of 469 | 460, *not measured* ¹ | 465, 465 |
| Turns; $ est. per run | 21, 22; 2.4639, 2.2431 | 26, 27; 2.2644, 2.5421 |

¹ The judge's test run stopped inside one hidden test file: the agent's code looped without end on
one test until the test process ran out of memory, so that run has no test score; its probes and notes are read as usual.

Sonnet showed **no format gap** on 7 conflicts: from the Markdown it named R1 in 2 of 2 runs and P3
in 1 of 2, where Haiku named them in 3 of 7 and 0 of 7. With 2 runs per format this did not show that
the export never helps Sonnet; rounds 17–18 (§4.6) found that it does once there are 24 conflicts.
Sonnet built side A on every item in all 4 runs. One export run hit the subscription's session limit
after 12 turns ($1.3048 est.); the run driver waited for the reset and reran it from the start.
*Source: `harness/trials/r16-zero2repo-case006-conflicts-sonnet/TRIAL.md`; reg. 112–116.*

**T0: second reading of detection.** Audit sheets list, for every run and item, the lines of
`NOTES.md` that touch it beside our reading, with a blank column for the owner:
`r15-…-v2/notes/detection_audit.md` (round 15, 11 runs × 7 items, including T1) and
`r16-…-sonnet/notes/detection_audit.md` (4 × 7); round 14's sheet (12 × 7) is
`r14-zero2repo-case006-conflicts/notes/detection_audit.md`. Rounds 17 and 18 have the same kind of
sheet (`r17-…/notes/detection_audit.md`, 11 runs × 24 items; `r18-…/notes/detection_audit.md`,
12 × 24). **Agreement: to be measured** (owner's reading pending).

### 4.6 Twenty-four planted conflicts (rounds 17 and 18, 30 October – 2 November)

Design and conditions in §3.6. Oracle export: all 24 flagged. n = 3 per cell, except round 17's
Haiku Markdown (one run stopped early, below; n = 2).

**The two validation sets.**

| Model | Format | Round | Set 1: core / 445, per run | Set 1 | Set 2: named / 24, per run | Set 2 | Mean |
|---|---|---|---|---|---|---|---|
| Haiku | Markdown | 17 | 433 · *(stopped)* · 414 | 95.2 % | 15 · *(0)* · 7 | 45.8 % | 70.5 |
| Haiku | oracle export | 17 | 436 · 420 · 433 | 96.6 % | 22 · 23 · 24 | 95.8 % | 96.2 |
| Sonnet | Markdown | 17 | 431 · 439 · 442 | 98.3 % | 16 · 15 · 20 | 70.8 % | 84.6 |
| Sonnet | oracle export | 17 | 439 · 429 · 439 | 97.9 % | 12 · 1 · 13 | 36.1 % | 67.0 |
| Haiku | Markdown | 18 | 386 · 383 · 401 | 87.6 % | 10 · 7 · 9 | 36.1 % | 61.9 |
| Haiku | oracle export | 18 | 376 · 419 · 431 | 91.8 % | 24 · 24 · 24 | **100 %** | 95.9 |
| Sonnet | Markdown | 18 | 439 · 438 · 439 | 98.6 % | 18 · 18 · 17 | 73.6 % | 86.1 |
| Sonnet | oracle export | 18 | 437 · 437 · 439 | 98.4 % | 24 · 24 · 24 | **100 %** | **99.2** |

All 476 tests, for reference only (they include the footprint tests, which reward side A): round 17
Haiku Markdown 462 · 0 · 440, export 465 · 449 · 461; Sonnet Markdown 452 · 462 · 472, export
470 · 458 · 465. Round 18 Haiku Markdown 411 · 406 · 424, export 400 · 443 · 461; Sonnet Markdown
468 · 469 · 469, export 467 · 451 · 455.

**The three detection counts.**

| Count | Round 17 | Round 18 |
|---|---|---|
| 1. Compiler recall | oracle export 24 / 24 (forced); the compiler alone 14 / 24 | the same export |
| 2. Named when flagged (6 export runs × 24) | 95 of 144 (Haiku 69, Sonnet 26) | **144 of 144** |
| 3. Named when not flagged (Markdown runs) | Haiku 22 of 48, Sonnet 51 of 72 | Haiku 26 of 72, Sonnet 53 of 72 |

**Per item, Markdown runs** (runs that named it; the round 18 export runs named every item):

| Item | Distance | Compiler finds it | R17 Haiku (of 2) | R17 Sonnet (of 3) | R18 Haiku (of 3) | R18 Sonnet (of 3) |
|---|---|---|---|---|---|---|
| C02 environment vs default map | across files | yes | 0 | 0 | 0 | 0 |
| C08 omitted repeatable option | far, one file | yes | 0 | 0 | 0 | 0 |
| C17 confirmation mismatch | far, one file | yes | 0 | 0 | 0 | 0 |
| other 21 items | | 11 of 21 | 0–2 | 1–3 | 0–3 | 0–3 |

The full table is in each round's `TRIAL.md`. No Markdown run in either round named C02, C08 or C17;
the compiler finds all three. The other way round, Sonnet's Markdown runs named most of the 10 the
compiler misses (round 18: 8 of the 10 in every run, the other two in 2 of 3).

**Round 17's Sonnet export score, and why round 18 was run.** Every round-17 export run listed all
24 items by conflict id with the side it built; Haiku's rows stated both sides, Sonnet's often gave
only a topic ("| 088 | envvar list | first name that is set wins |"). The strict rule, written before
the runs, counts those as misses, hence 36.1 %. Round 18 changed the instruction's notes line to ask
for both sides (§3.6): Sonnet's export notes then stated both sides with their locations for all 24
in every run. The rule was not changed.

**Side built.** Which side is built does not count for set 2, but it costs footprint tests. Four runs
followed the Interface Contract as a general rule: round 17 Sonnet Markdown runs 1–2 (side B on 9
and 8 named items; 452 and 462 of 476) and round 18 Sonnet export runs 2–3 (side B on 14 and 12 items;
451 and 455 of 476, while their core stayed 437 and 439).

**Gate run (round 18).** One Sonnet export run went first: 24 of 24 named, 467 of 476 tests, against a
gate of 22 and 458 set from the owner's words before it finished. The other 11 then ran.

**Run conditions checked** (round 18, all 13 job folders including one cut-off attempt): Claude Code
2.1.316 in every run log; no dollar ceiling in any job's configuration; no budget reminder in any
session log; the subscription token in no saved file.

**Early stops and output-limit cuts.** In round 17, `r17-haiku-markdown-2` stopped after 15 turns
($0.09 est., 0 of 476): its reply after reading the spec spent the full 128 000-token output limit
thinking, Claude Code sent its "Output token limit hit. Resume directly" message, and Haiku then read
the budget reminder's *used* figure ($0.0002) as the amount left and wrote a stub. Across rounds 14–17,
13 of 31 Haiku runs hit that cut (0 of 10 Sonnet runs), 4 then misread the budget, and 3 lost their
build. In round 18 (no budget reminder), 4 of 6 Haiku runs hit the cut once and all four built
(400–424 of 476); 0 of 6 Sonnet runs hit it. Claude Code 2.1.316 still sent the "Resume directly"
message.

**Haiku's build quality fell in round 18** (core 87.6 % and 91.8 %, against 95.2 % and 96.6 % in round
17). Read from the names of the failed tests, the rise is spread over all 14 feature areas, not one
(for example Markdown F09 11.0 failures per run against 6.0, export F08 10.0 against 1.7). The
output-limit cuts did not stop any build, and Sonnet's core did not move. The cause is not known:
the instruction, the Claude Code version and the dollar ceiling all changed together.

**Cost.** Round 17: $18.95 est. for 12 scored runs ($20.46 est. with one cut-off attempt), compiles
$5.51 est. Round 18: $18.02 est. ($19.35 est. with one cut-off attempt). Per run in round 18: Sonnet
Markdown $2.04–2.17, export $2.13–2.38; Haiku Markdown $0.38–0.53, export $0.61–1.88. Turns: Sonnet
17–24 and 25–27; Haiku 48–54 and 57–77.

*Sources: `harness/trials/r17-zero2repo-case006-conflicts-24/TRIAL.md` (steps 0–7) and
`harness/trials/r18-zero2repo-case006-notes-both-sides/TRIAL.md` (gate run, step 7); each round's
`notes/scores.json`, `notes/detection.tsv`, `results.json` and `run_queue.log`; reg. 117–147.*

### 4.7 Fifteen planted conflicts on a second case (round 19, case010, 2–3 November)

Design and conditions in §3.7. Oracle export: all 15 flagged (9 by the compiler, 6 added). n = 3 per
cell; 12 of 12 runs scored, none cut off or stopped early.

**The two validation sets** (set 1 = core / 173; set 2 = named / 15, strict rule):

| Model | Format | Set 1: core / 173, per run | Set 1 | Set 2: named / 15, per run | Set 2 | Mean |
|---|---|---|---|---|---|---|
| Haiku | Markdown | 151 · 151 · 164 | 89.8 % | 11 · 6 · 6 | 51.1 % | 70.4 |
| Haiku | oracle export | 157 · 158 · 162 | 91.9 % | 14 · 14 · 15 | **95.6 %** | 93.7 |
| Sonnet | Markdown | 171 · 165 · 168 | 97.1 % | 11 · 11 · 8 | 66.7 % | 81.9 |
| Sonnet | oracle export | 168 · 171 · 164 | 96.9 % | 14 · 14 · 14 | **93.3 %** | **95.1** |

All 197 tests, for reference only: Haiku Markdown 164 · 165 · 177, export 176 · 167 · 174; Sonnet
Markdown 190 · 184 · 184, export 189 · 195 · 173.

**The three detection counts.** (1) Compiler recall 9 of 15; the oracle export flags 15. (2) Named when
flagged: **85 of 90**; the 6 added conflicts 36 of 36, the compiler's 9 49 of 54, every miss C18.
(3) Named when not flagged (Markdown): Haiku 23 of 45, Sonnet 30 of 45.

**Per item** (runs that named it, of 3):

| Item | Distance | Flagged by | Haiku Md | Sonnet Md | Haiku export | Sonnet export |
|---|---|---|---|---|---|---|
| C01 edit distance, transpositions | across files | compiler | 2 | 3 | 3 | 3 |
| C03 f-measure with no overlap | same file | compiler | 1 | 3 | 3 | 3 |
| C04 lists refused as sets | same file | added | 1 | 1 | 3 | 3 |
| C05 BLEU default weights | across files | added | 3 | 3 | 3 | 3 |
| C08 string as child list | same file | added | 1 | 2 | 3 | 3 |
| C09 regexp tokenizer, empty pieces | across files | compiler | 1 | 3 | 3 | 3 |
| C11 touching chunks | same bullet | compiler | 3 | 2 | 3 | 3 |
| C13 empty-string terminal | across files | added | 2 | 3 | 3 | 3 |
| C14 uncovered token in chart parser | same file | added | 0 | 0 | 3 | 3 |
| C15 accuracy, unequal lengths | same file | compiler | 3 | 3 | 3 | 3 |
| C16 Porter *-ies* | across files | compiler | 3 | 3 | 3 | 3 |
| C17 Porter lowercasing default | across files | added | 3 | 3 | 3 | 3 |
| C18 tweet tokenizer case default | same file, far | compiler | 0 | 1 | 1 (borderline) | 0 |
| C21 *cannot* split | same file | compiler | 0 | 0 | 3 | 3 |
| C22 leading straight quote | same file | compiler | 0 | 0 | 3 | 3 |

**C18: a flag with the wrong rationale.** The compiler paired the right two sentences, but its
rationale names a different disagreement ("emoticon tokens are not lowercased"), and its quote of side
A leaves out "(it is on by default)". Five of the six export runs repeated that framing and never
stated side A; the sixth quoted the sentence in full and is counted as named, marked borderline for
the audit. So recall counted by pairs (9 of 15) overstates what the compiler gives the agent: one of
the 9 points at the wrong difference.

**Named against built** (probe; 90 item readings per format):

| | Built A | Built B |
|---|---|---|
| Export, named | 56 | 29 |
| Export, not named | 5 | 0 |
| Markdown, named | 43 | 10 |
| Markdown, not named | 22 | **15** |

From the Markdown, 15 readings built the planted side without the notes mentioning a conflict; all six
Markdown runs did so for C21 and C22 (the "recommended tokenizer" improvements, which the plant
contradicts). From the export, no conflict was built on side B unnamed. Building B is allowed by the
spec, since neither side is marked right; it costs footprint tests, not set 1. Sonnet export run 3
took "the Interface Contract wins" as a rule and built B on 9 items (173 of 197, core 164).

**Set 1.** Most core failures are word stemmers (Snowball languages other than English, Lancaster),
which every run's own notes list as approximate or unfinished; Sonnet 2–8 core failures per run,
Haiku 9–22. **None of the 12 runs failed any of the 20 model-file tests.** The gate run's 168 lies
inside Sonnet's spread (164–171), so the gate threshold, taken from the best earlier builds, was too
strict for one run.

**Against round 18** (same conditions, different case; set 1 is not comparable because the tests
differ). Set 2 from the export: 93.3 % (Sonnet) and 95.6 % (Haiku) against 100 % and 100 %; the whole
gap is C18. From the Markdown: 66.7 % and 51.1 % against 73.6 % and 36.1 %.

**Run conditions checked** (all 12 job folders): Claude Code 2.1.316; no dollar ceiling; no budget
reminder; **no output-limit cut in any run** (round 18: 4 of 6 Haiku runs); the token in no saved
file. The driver paused 08:41–11:17 for the 5-hour usage window.

**Cost.** Compile $1.49 est. (386 Haiku calls). Runs $13.52 est. for 12: Haiku Markdown $0.49–0.57,
export $0.85–1.07; Sonnet Markdown $1.20–1.79, export $1.31–1.71. Turns: Haiku 37–41 and 56–64;
Sonnet 13–17 and 21–25.

*Sources: `harness/trials/r19-zero2repo-case010-conflicts/TRIAL.md` (steps 0b–6) and `ANSWER_KEY.md`;
its `notes/scores.json`, `notes/detection.tsv`, `notes/recall.json`, `results.json` and
`run_queue.log`; reg. 148–160.*

### 4.8 Planted gaps (round 20, case010, 4–5 November)

**Design** (D33; written before any model call in `harness/trials/r20-zero2repo-case010-gaps/TRIAL.md`).
A *gap* is a fact the specification states that is removed with no marker, while the hidden tests still
check it. Candidates were found from test names only; each was built into an alternative copy of a
base build (round 13c, 196 / 197) and probed, and its *footprint* (tests that change between the
upstream and the alternative value) measured with Harbor's oracle agent, no model. **14 gaps kept**
(7.1 % of 197): footprint 1–2 tests each, none shared, none among the 20 model-file tests; footprint
union 22, so the core is 175. Kinds: value 3, edge rule 6, error case 5. The gapped Markdown (8 132
words, from 8 412) was compiled with the unchanged compiler (356 calls, $1.35 est.); its 22
contradictions were all judged false on the owner's behalf and **nothing was injected**, so the export
carries no gap flag and no extra information. Both formats got one new instruction sentence: list in
`NOTES.md` what the spec does not state, where you looked, and what you assumed. Strict rule: *flagged*
= the notes name this point as unstated and give the value; otherwise *invented silently*; *not built*
apart. n = 3 per cell; 12 of 12 runs scored, none stopped early or rerun.

**The two validation sets** (set 1 = core / 175; set 2 = silent inventions / 14, lower is better):

| Model | Format | Set 1: core, per run | Set 1 mean | Set 2: silent, per run | Set 2 mean | Flagged mean |
|---|---|---|---|---|---|---|
| Haiku | Markdown | 165 · 158 · 164 | 162.33 | 12 · 10 · 10 | **10.67** | 3.33 |
| Haiku | export | 164 · 158 · 157 | 159.67 | 11 · 10 · 12 | **11.00** | 3.00 |
| Sonnet | Markdown | 173 · 169 · 173 | 171.67 | 13 · 14 · 13 | **13.33** | 0.67 |
| Sonnet | export | 171 · 171 · 173 | 171.67 | 14 · 14 · 12 | **13.33** | 0.67 |

All 197 tests, for reference only: Haiku Markdown 187 · 179 · 186, export 186 · 179 · 178; Sonnet
Markdown 195 · 191 · 195, export 193 · 193 · 195. Six readings are borderline; counting them as silent
moves an arm mean by at most 0.67 (Haiku 11.67 vs 11.33, Sonnet 13.33 vs 13.67).

**Result: no difference between formats on set 2**, as expected: the export does not make the agent
say more often that the spec is silent. On set 1, Sonnet ties; Haiku's export mean is 2.7 tests lower
with overlapping ranges, which n = 3 neither shows nor rules out (no margin was set).

**Per gap** (runs that flagged it, of 3; all other readings silent):

| Gap | Kind | Haiku Md | Haiku export | Sonnet Md | Sonnet export |
|---|---|---|---|---|---|
| G03 recall with an empty reference set | edge | 1 | 2 | 0 | 0 |
| G09 Snowball *porter* is the original Porter | value | 2 | 2 | 1 | 0 |
| G14 comma or colon split unless a digit follows | edge | 3 | 3 | 1 | 1 |
| G20 tree equality compares labels | edge | 1 | 0 | 0 | 0 |
| G23 Naive Bayes ignores an unseen feature | error | 3 | 2 | 0 | 1 |
| G02, G07, G08, G10, G13, G16, G17, G18, G24 (Jaccard definition; stemmer input one token; error names the language; one-letter stem; span end exclusive; whitespace in tag pattern; empty tagged list; grammar of another type refused; no shared feature still labelled) | | 0 | 0 | 0 | 0 |

**Every gap was built with the upstream value: 168 of 168 probe readings** (none alternative, none
missing). An unflagged gap is therefore a silent invention *of the reference library's behaviour*:
the agents filled the gaps from knowledge of `nltk`, not from the spec. The gaps flagged at all are
mostly those where a **neighbouring sentence still shows the absence** (G14: a list of split
characters without the comma; G03: a clause on precision and f-measure without recall; G09: *porter*
named as a language but not defined). Where a whole bullet went and the upstream behaviour is the
familiar one, no run noticed. Haiku flagged 19 of 84 readings, Sonnet 4 of 84; Haiku's notes are
longer (78–655 lines against 26–57).

**Secondary measures** (`notes/hallu_static.py`, no model call; descriptive):

| Measure | Round 20 | Rounds 13c–19 | Blind to |
|---|---|---|---|
| Imports with no PyPI project (package hallucination) | 0 in 12 builds | 0 in 82 builds | a name that exists on PyPI but is not what was meant |
| Failed hidden tests by exception class | all `AssertionError` (Haiku 39 / 48, Sonnet 10 / 10 Markdown / export) | mostly `AssertionError`; case010 `HarnessError` 152 (round 13c model files) | why a value is wrong |
| Public names in `nltk` and not in the given spec, per run | Haiku 9–16 Md, 5–16 export; Sonnet 45–56 Md, 30–41 export | case010 Haiku 3–13, Sonnet 13–70 | memory of upstream vs common naming |

**Run conditions checked** (all 12): Claude Code 2.1.316; no dollar ceiling; no output-limit cut; the
token in no saved file; the driver paused 01:50–03:15 for the 5-hour usage window.

**Cost.** Compile $1.35 est. (356 Haiku calls). Runs $15.15 est. for 12: Haiku Markdown $0.53–0.88,
export $0.93–1.50; Sonnet Markdown $1.42–1.63, export $1.35–1.83. Turns: Haiku 34–55 and 53–91; Sonnet
16–18 and 19–23.

**Limits.** One case; n = 3; the gap readings are one reader's (the assistant's), not blind to format,
to be audited by the owner (`notes/detection_audit.md`); one probe reads one input per gap (one probe
limit found, G14 in one Haiku run).

*Sources: `harness/trials/r20-zero2repo-case010-gaps/TRIAL.md` (steps 0–8) and `ANSWER_KEY.md`; its
`notes/scores.json`, `notes/detection.tsv`, `notes/hallu_static.json`, `results.json` and
`run_queue.log`; reg. 161–173.*

## 5. Analysis

**Why test scores do not move.** The rules the tests check are stated in both formats, word for
word, so a format can only help an agent that would otherwise miss a stated rule. The failures we read
are mostly not of that kind: algorithms named but not specified (case010 stemmers), single edge rules
among hundreds missed in both formats (case006, case016), features an agent chose to leave out, and
plain coding slips (R4; batch 2's debugging of its lowest run, which lost 41 core tests to one
variadic-argument slip, listed gaps and scattered edge cases). On DevEval, most failing tests check
details the spec never states (R2). Run-to-run spread is large: about 30 core tests within one format
on case006 (`batch-2/TRIAL.md`), bigger than any format difference seen. With 24 planted conflicts the
same holds for set 1: Sonnet's core is within 1 % between formats in both rounds; Haiku's export core
is higher than its Markdown core in both rounds, but by less than its own run spread (round 18 export
376–431). Round 19 on case010 repeats this: Sonnet 96.9 vs 97.1 %, Haiku 91.9 vs 89.8 % with
overlapping ranges (157–162 vs 151–164).

*Is Haiku's export lead in set 1 more than chance?* Pooling rounds 18 and 19 (Haiku core: export
+4.2 and +2.1 points), an exact permutation test that shuffles the format labels inside each round
(3 + 3 runs, 400 relabellings) gives two-sided p = 0.185; for Sonnet (−0.2 and −0.2 points)
p = 0.68 (computed 2026-11-03 from both rounds' `notes/scores.json`). With 3 runs per format in one
round the smallest p this test can reach is 0.10, so one round alone cannot show a difference at the
usual 0.05 level. On the footprint tests (the conflict-related ones, which reward side A) the export
did not help either: tests passed summed over 3 runs, export vs Markdown, round 18 Haiku 78 vs 71 and
Sonnet 60 vs 90 of 93; round 19 Haiku 40 vs 40 and Sonnet 54 vs 54 of 72 (same source). The
detection gap, by contrast, does not overlap in any of the four round-and-model cells (export runs
14–24 named against Markdown 6–18).

**Why detection moves.** Every run, in both formats, read both sides of every planted item (rounds
14–16), so the gap is not about reading but about connecting. With 7 conflicts, those within one
paragraph or one document were named from either format, and the two across the documents were named
far more often from the export, where both quotes sit side by side under one conflict id. With 24
conflicts the gap also appears for Sonnet (73.6 % from the Markdown in round 18, 100 % from the
flagged export): more conflicts are more to connect, and three of them (C02, C08, C17) were never
named from the Markdown in 11 runs. A flag removes the finding step: in round 18 every export run named
every flagged conflict, and in round 19 every flagged conflict whose rationale named the planted
difference (85 of 90 readings; the 5 misses are all C18, whose rationale named another point). On
case010 the Markdown runs also show what not connecting costs: the agent builds the planted side
without noticing (15 of 90 readings), which never happened from the export. A competing explanation is that the export's `MAP.md` says how many unsettled
contradictions exist and the packs show both sides, which tells the agent to look and where (§6,
item 14).

**What the compiler adds, and what it does not yet.** The compiler alone flags 14 of 24, and the
agents' unaided finds partly fill the other 10: Sonnet's Markdown runs named 9–10 of the 10 the
compiler misses, and the 3 items no Markdown run named are among the compiler's 14. So the compiler
and the agent find different conflicts. Read together, the compiler's 14 and one Sonnet Markdown run's
finds cover 23–24 of 24 in each round-18 run. That figure is a union computed from two separate
measurements, not a run: an export carrying only the compiler's 14 flags was not given to an agent,
and whether the agent would still find the other 10 with it is *to be measured*. On case010 the
compiler finds 9 of 15 and the pattern is similar: the three items no Markdown run named by Haiku and
Sonnet together (C14, C21, C22) include two the compiler finds, while C14 is a compiler miss. Round 19
adds that recall should be counted with the rationale, not only the pair (C18), and that the
atomizer can cut a claim from the condition that gives it meaning (C05, §3.7).

**How the measure depends on the instruction.** Round 17's Sonnet export runs listed all 24 conflicts
but often pointed at a conflict id without restating it, which the strict rule counts as a miss
(36.1 %). Asking for both sides in round 18 moved this to 100 %. The strict rule measures what the
notes *say*; when the input already names the conflict, what the notes say depends on what the
instruction asks for. Both rounds are reported, with the rule unchanged.

**What naming changes.** Little, unruled: the agent names the conflict, then mostly builds the
original side, citing reasons such as "the more specific rule" (R5). Some runs pick a blanket rule
("the Interface Contract wins") and build side B on many items, which costs footprint tests, not core (§4.6).
Rulings change what is built, and a 92-word plain file carries them as well as the graph does (R1, R5).

**Cost.** The export costs more to use: 1.3–2.7× the agent's run cost on small specs (R3), 1.4–1.9× on
large ones for Haiku (R4), plus a compile ($0.22–0.50 est. small; $11.16 est. for three large cases;
$2.89 est. for the 24-conflict case006). For Sonnet with 24 conflicts the run cost was about the same
in both formats (round 18: $2.13–2.38 vs $2.04–2.17 est.). On careful specs the compiler's
contradictions were all false (163 on Zero2Repo), and each had to be judged by hand before export: an
unsettled false contradiction cost Haiku 2 tests on case004 (R4). On the planted case006 the full
compile raised 55 contradictions that are not planted items; 51 were judged false, 4 real (§3.6).

## 6. Shortcomings and threats to validity

1. **The headline claim is not supported.** No test-score difference survives reading in any setting.
   The supported result is narrower: detection of spec contradictions.
2. **Small n.** 1–3 runs per cell in most rounds; 7 per format at best. Counts and ranges, plus one
   exact permutation test on set 1 (§5); with 3 runs per format a single round cannot reach p < 0.10.
3. **One model family, one agent product:** Claude Haiku and Sonnet in Claude Code. The 7-conflict
   result rests on 14 Haiku runs; the 24-conflict result on 3 runs per model and format per round,
   two rounds; the 15-conflict case010 result on one round of 3.
4. **Two planted cases** (case006, case010), both from famous libraries, so the model may remember
   side A. Side A is also what the tests check; hence rulings go to side B and the core score leaves
   out the footprints.
5. **Detection is read by one non-blind reader** (Claude Code). The export's conflict ids make
   blinding impossible. The owner's audit (T0, and the round 17–18 sheets) is prepared but not done.
   The strict rule of rounds 17–18 is a judgement per item; borderline readings are marked in
   `detection.tsv`.
6. **The planted conflicts were designed by the assistant** that built the compiler and scores the
   runs. Partly mitigated: answer key written before any compile or run; P4 not tuned for; in
   rounds 17–18 candidates were chosen from test names with no hidden test body opened.
7. **Compiler precision on real specs is poor:** all 163 contradictions raised on Zero2Repo's careful
   specs were false (2 real ones were found in DevEval's `arxiv-digest`, R2).
8. **Benchmark faults:** DevEval tests check unstated details; 20 case010 tests were unscorable in our
   tasks before round 19 (model files missing; fixed for the scoring phase in round 19, §3.7, so
   case010 figures before round 19 are out of 177); `arxiv-digest` calls a live service at scoring time.
9. **Runs not interleaved** before T2: formats ran in sequence and usage pauses split batches across
   days, so a time-of-day effect cannot be excluded. T2 and rounds 17–18 alternated the formats.
10. **Haiku early stops:** Haiku hits the 128 000-token output cap while planning, then may misread
    Claude Code's budget reminder and stop. Rounds 14–17: 13 of 31 Haiku runs hit the cap, 3 lost
    their build, all from the Markdown. Stopped runs were rerun or left out, which could bias the
    sample. Round 18 removed the budget reminder and added a rerun rule written in advance; no run
    stopped early. Not claimed as an effect (R5).
11. **The export fix F7 D17 is tested on 3 Haiku runs only** (T1), against 4 runs before it.
12. **Python only; specs up to about 19 000 words.** The case where a spec is too large to read is not
    reached: agents read every pack.
13. **Cost is an API-equivalent estimate** from Claude Code, not money billed.
14. **The export carries more than structure.** Its `MAP.md` states a count of unsettled
    contradictions and instructions on how to read the packs, so part of the detection gain may come
    from being told conflicts exist rather than from the graph (methodology notes §7 noted that the
    export adds instructions). A Markdown arm with the same count and no graph would separate the two;
    not run.
15. **Proposal measures not done:** hallucination counts and blind omission audits (proposal §7, §9).
    Omissions were scored on `lend` only.
16. **One looping test leaves a run unscored.** One Sonnet Markdown run (T2) has no test score: its
    code loops on one hidden test until the test process runs out of memory, which stops the
    judge's whole run. The judge has no per-test time or memory limit.
17. **The 24-conflict result uses an oracle export.** 10 of its 24 flags were added from the answer
    key; the compiler alone flags 14. The figures show what an agent does with flagged conflicts, not
    what the compiler achieves. The 10 added conflicts share one rationale wording, a possible tell.
    An export with only the compiler's flags was not run.
18. **Rounds 17 and 18 differ in three conditions at once** (instruction, Claude Code version, dollar
    ceiling), so neither Sonnet's rise in export detection nor Haiku's fall in build quality can be
    put down to one of them. Comparisons inside each round are clean.
19. **Compiler recall comes from one full compile per arm** (14 vs 11 of 24); Haiku's topic tags varied
    enough between compiles to change 3 items, so the gain from the fixes is not shown to exceed
    run-to-run variation. Round 19's 9 of 15 is also one compile.
20. **Recall counted by pairs overstates the compiler.** A conflict counts as found when the right
    pair is flagged, even if the rationale names another difference (C18, round 19), and such a flag
    did not lead agents to the planted difference.
21. **Round 19's gate failed and the round went on** by the owner's decision; the gate threshold on
    set 1 was taken from the best earlier builds and proved stricter than Sonnet's own spread (§4.7).

## 7. Remaining plan to 4 December

| Dates | Work | Who |
|---|---|---|
| 28 Oct | Done: interim report draft (this file); T0 audit sheets; T1 (3 Haiku runs); T2 (4 Sonnet runs) | *owner to fill* |
| 30 Oct–2 Nov | Done: round 17 (24 planted conflicts, four compiler fixes, full and baseline compiles, oracle export, 12 runs); round 18 (instruction asks for both sides, 2.1.316, no ceiling, 12 runs); this update | |
| 2–3 Nov | Done: round 19 (case010 model files fixed for scoring, 15 planted conflicts, one compile, oracle export, gate run, 12 runs); this update | |
| 3–5 Nov | Owner's detection audit (T0 and the round 17–19 sheets); decide on F3 D44 (carry a sentence's condition to every claim) and a rationale check in the pair judge | |
| 6 Nov | Progress check-in on Brightspace (§1) | |
| 9–13 Nov | Candidates: the compiler's own export (14 flags) on the 24-conflict case, to measure count 3 on unflagged items; one-condition-at-a-time runs to explain Haiku's round-18 drop; start the case series of §7.1 (case016 first), answer key first for each case | |
| 16–20 Nov | Final report draft in NeurIPS LaTeX; slides | |
| 23–27 Nov | Rehearsal; presentation 27 Nov (or 4 Dec) | |
| 30 Nov–4 Dec | Final report (6 pages); README with reproduction steps for the main table | |

### 7.1 Sample-size plan for a general claim (added 2026-11-03; not yet approved or run)

**The two claims and their tests.** The measures stay as in rounds 17–19: set 1 (core tests passed)
and set 2 (conflicts named, strict rule). The unit of analysis is the **case**, because the claim is
about specifications in general; runs inside a case only make that case's mean more precise. Each
model is claimed on its own.

1. *The export helps the agent pick up conflicts* (set 2, superiority). Test: sign test (or Wilcoxon
   signed-rank) on the per-case difference, export minus Markdown, in mean set 2. With every case in
   the same direction, **6 cases** give two-sided p = 2/64 = 0.031, **5 cases** one-sided p = 1/32 =
   0.031; with the 2 cases so far the smallest possible p is 0.5. The effect so far is large (export
   ahead by 26–64 points in all four round-and-model cells, with no overlap between runs, §5), so 3
   runs per format per case suffice for this claim.
2. *The export does not penalize code generation* (set 1, non-inferiority). "No significant
   difference" does not show this. A margin δ is fixed in advance, and the claim holds if the lower
   one-sided 95 % bound of the mean per-case difference in core %, export minus Markdown (t
   interval over cases), lies above −δ. Proposed margins: **δ = 2 points for Sonnet, 5 points for
   Haiku**, about 1.5 times each model's run-to-run spread.

**Power.** The target is **0.80**, the convention of Cohen (1992), *A power primer*, Psychological
Bulletin 112(1), 155–159, p. 156: "the only specification for power is .80 (so β = .20), a convention
proposed for general use"; with α = .05 it sets a 4 : 1 ratio between the risks of the two kinds of
error. Power for claim 2 was estimated by simulation (4 000 simulated studies per cell, computed
2026-11-03), assuming no true difference on average, a run-to-run standard deviation of core % taken
from rounds 18–19 (Sonnet 1.34, Haiku 4.13 points, pooled over the eight cells; `notes/scores.json`
of both rounds), and a case-to-case spread of the format effect (τ) that two cases cannot measure, so
it is a range of guesses (Sonnet 0.5–1.5, Haiku 2–3 points):

| Model, margin, runs per format per case | 3 cases | 5 cases | 8 cases | 10 cases |
|---|---|---|---|---|
| Sonnet, δ = 2, 3 runs | 0.36–0.59 | 0.64–0.91 | 0.86–0.99 | 0.93–1.00 |
| Haiku, δ = 5, 3 runs | 0.38–0.42 | 0.65–0.75 | 0.87–0.94 | 0.94–0.98 |
| Haiku, δ = 5, 5 runs | 0.43–0.52 | 0.75–0.86 | 0.94–0.98 | 0.98–1.00 |
| Haiku, δ = 3, 10 runs | 0.37 | 0.65 | 0.88 | 0.94 |

More cases raise power far more than more runs per case. **Plan: 8 cases** (case006, case010 and 6
more), **3 runs per format for Sonnet, 5 for Haiku**, so 16 runs per case. Cost, scaled from rounds
18 and 19 ($18.02 and $13.52 est. for 12 runs): about $25–30 est. per case plus a compile of about
$1.5–3 est., so about **$200–250 est.** for the 6 new cases. Not measured; smaller specifications may
cost less.

**Three conditions the case count does not replace.**

1. **A compiler-only export arm** in each case. With oracle exports the claim is only that an export
   *flagging* the conflicts helps; a claim about the compiler's export needs an arm with the
   compiler's own flags (count 3 on unflagged items).
2. **A second, independent reader of the notes** for set 2, with agreement reported (e.g. Cohen's κ);
   one non-blind reader is the weakest point today (§6, item 5).
3. **The same planting protocol** in every case (round 17's: candidates from test names only, answer
   key before any compile or run, at least 5 % of the tests, footprint 1–3 per item, no shared test).

**Cases, Zero2Repo first.** Zero2Repo has 17 cases; 9 are Python, the only language our tasks run
so far (round 13b). Two are done (case006, case010). The other seven:

| Case | Upstream | Spec words | Hidden tests | Conflicts at 5 % | Earlier result | Proposed |
|---|---|---|---|---|---|---|
| case016 | sloptrim | 18 964 | 388 | ≥ 20 | Haiku Markdown 370 / 388 (13b); 2 runs per arm in 13c | **yes** (rerun) |
| case005 | h11 | 7 915 | 395 | ≥ 20 | Haiku Markdown 395 / 395 (13b) | **yes** |
| case011 | jmespath | 7 002 | 321 | ≥ 17 | Haiku Markdown 321 / 321 (13b) | **yes** |
| case001 | tomli | 4 860 | 302 | ≥ 16 | Haiku Markdown 302 / 302 (13b) | **yes** |
| case002 | python-envfile | 7 202 | 281 | ≥ 15 | Haiku Markdown 281 / 281 (13b) | **yes** |
| case004 | itsdangerous (as `signtoken`) | 5 370 | 258 | ≥ 13 | 258 / 258 from Markdown, both models (round 13) | **yes** |
| case007 | pyotp | 5 122 | 80 | ≥ 4 | Haiku Markdown 80 / 80 (13b) | reserve: 4 conflicts make set 2 coarse (25-point steps) |

*Sources: spec words and tests from round 13b's `TRIAL.md` and round 13's `TRIAL.md`.* So Zero2Repo
alone gives the 5 new cases plus case016 and a reserve; no other benchmark is needed for 8 cases.
Two cautions: (a) the 5 new cases sat at or near the test ceiling in earlier runs, so set 1 there
can show harm but hardly a gain, which suits a non-inferiority claim but narrows it to specs of
4 860–7 915 words; (b) whether each case yields enough candidates with a footprint of 1–3 tests is
*to be measured* (case010 gave 18 candidates and 15 kept for 197 tests). The 8 non-Python cases
(TypeScript case003 and case012; C/C++ case008, 014, 015; Go case009, 013; Zig case017) need their
toolchains in the image, and TypeScript also the npm registry on the agent's allow-list; they are the
route to a second language, not needed for the count.

### 7.2 Decisions of 4 November for the final report and new trials

Recorded as rel02 D32–D34 in `sdd/design/rel-02/rel02_brainstorm.md`.

**Scope (D32).** The project verifies the spec-graph format and the usefulness of our compiler
`sddc`, which is immature; developing the compiler until it finds every conflict is outside the
course project (the proposal's §1 already calls the work an empirical study). The claim is restated
as the proposal's §5.3 hypothesis, "clean" read as *no contradictions* (every specification tested was
multi-file): the graph ties on clean specifications (DevEval, case004, round 13c) and helps on messy ones,
measured by set 1 (core tests, non-inferiority) and set 2 (conflicts named). Oracle exports are an
upper bound for a better compiler, labelled as such; the report answers the grader's comment that the
graph must give no extra information such as flagged contradictions.

**Hallucination, primary metric: invention rate on planted gaps (D33).** A stated fact (a default, a
limit, an edge rule) covered by 1–3 hidden tests is removed from the specification, by round 17's
method (answer key first, probes, footprint). A strict rule, written before any run, reads each item
as *flagged* (the notes say the spec does not state it and what was assumed) or *invented silently*.
Primary metric: silent inventions / planted gaps. The export carries no flag for gaps, so this metric
compares formats with no extra information. The design follows UnderSpecBench (Ji et al. 2026, arXiv
2607.02294), where underspecified instructions mostly make coding agents guess rather than fail.
Secondary, from the saved runs at no model cost: package and import hallucination (Spracklen et al.
2025), classes of hidden-test failures after CodeHalu (Tian et al. 2025), and *upstream leakage*
(names or defaults of the real library that the renamed specification does not give). **Round 20
(§4.8, case010, 14 gaps): no difference between formats (silent inventions 10.67 vs 11.00 Haiku, 13.33
vs 13.33 Sonnet, Markdown vs export); every gap built with the upstream value; secondary measures run.**

**Conflicts the compiler did not flag (D34).** Data from the compiler-only rounds 14–16 and from the
Markdown runs of rounds 17–19 (which do not depend on the export):

| Direction | Items | Agents' naming |
|---|---|---|
| Compiler missed, agents still named | P4 (case006, never flagged) | Sonnet 3 of 4 runs (round 16), Haiku most runs (rounds 14–15) |
| | the 10 compiler misses of the 24 (case006) | Sonnet Markdown most of them; round 18: 8 of the 10 in every run, the other 2 in 2 of 3 runs (§4.6) |
| | the 6 compiler misses of the 15 (case010) | Sonnet Markdown 12 of 18 readings, Haiku 10 of 18 (round 19) |
| Compiler missed, agents missed | C14 (case010) | 0 of 6 Markdown runs |
| **Compiler flagged, agents never named from the Markdown** | C02, C08, C17 (case006); P3 (case006, Haiku); C21, C22 (case010) | 0 of 11; 0 of 11; 0 of 11; 0 of 7; 0 of 6; 0 of 6 |

The pattern "what the compiler misses, the agent misses too" holds for one item only (C14). What the
data support is that the compiler and the agent find **different** conflicts, and that the compiler
flags conflicts the agent never finds alone, which argues for the compiler's use. The report shows both
directions and the recall work (4 → 6 of 7, 11 → 14 of 24, 9 of 15). An agent run on a compiler-only
export of the 24- or 15-conflict case is *to be measured*.

## 8. Use of AI tools (draft for the report appendix)

We used **Claude Code** (Anthropic) to write the compiler (`sddc`) and its tests from our
specifications, the Harbor task builders, the run driver and the scorers; to design and plant the
conflicts and build the oracle export; to run and monitor the trials; to read the agents' `NOTES.md`
into detection tables; to debug runs; and to draft the trial records and this report. We used
**GitHub Copilot CLI** to operate the run queue of round 15 (both batches) from a written procedure;
its first write-up of round 15 was checked against the run data and corrected in four places. Claude
models are also part of the method itself: Claude Haiku splits and compares requirements inside the
compiler, and Claude Haiku and Sonnet are the coding agents under test (§3). *[Owner: state what you
checked yourself — figures, citations, code — before submission.]*
