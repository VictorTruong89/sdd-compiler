# rel02 — draft report sections

> **Status:** draft, opened 2026-10-13 (round 6 of the working map). Non-authoritative. Every figure
> comes from a file named in `rel02_methodology_notes.md` §8 or in
> `harness/platforms/harbor/TRIAL.md` §5b–5e, or in `harness/benchmarks/devbench-2024/TRIAL.md` §7–10.
> Method detail is in the methodology notes; this file holds the wording of results. R1 written in
> round 6, R2 and R3 in round 10 (2026-10-13); Sonnet results added to R2 and R3 in round 11 (2026-10-14). Sections not listed here are *to be written*.

## R1. Result on a small messy specification (`lend`)

### What was tested

One specification, written by us with planted defects: a command-line tool for a tool library,
7 Markdown files, 2 120 words, 24 testable requirements, 4 real contradictions. A coding agent
(Claude Code 2.1.296 in a Harbor container, tools limited to `Bash`, `Edit`, `Read`, `Write`, network
limited to the model API and PyPI) built the tool from one of four inputs:

| Input | What the agent reads | Words |
|---|---|---|
| Markdown | the 7 files as written | 2 120 |
| Graph export | the compiler's export of the same files; the 4 contradictions it reported are flagged as unsettled | 13 516 |
| Graph export with verdicts | the same, after the owner settled the 2 contradictions those 4 reports describe | 13 731 |
| Markdown with decisions | the 7 files plus a 92-word file stating the same 2 decisions | 2 212 |

Each input was run once on Claude Sonnet 5.5 and once on Claude Haiku 5.5: 8 runs. The build was
scored by 24 hidden tests, by the number of requirements with no passing test (omissions), by
probes that show which side of each contradiction the build takes, and by whether it follows the
owner's two decisions.

### What was measured

| Input | Model | Tests passed | Omissions | Decisions followed | Turns | Cost, est. API-equivalent |
|---|---|---|---|---|---|---|
| Markdown | Sonnet | 24 / 24 | 0 | 0 of 2 | 5 | $0.1451 |
| Graph export | Sonnet | 24 / 24 | 0 | 0 of 2 | 6 | $0.2351 |
| Graph export with verdicts | Sonnet | 24 / 24 | 0 | 2 of 2 | 7 | $0.2515 |
| Markdown with decisions | Sonnet | 24 / 24 | 0 | 2 of 2 | 5 | $0.1461 |
| Markdown | Haiku | 24 / 24 | 0 | 0 of 2 | 35 | $0.0539 |
| Graph export | Haiku | 24 / 24 | 0 | 0 of 2 | 43 | $0.1118 |
| Graph export with verdicts | Haiku | 24 / 24 | 0 | 2 of 2 | 53 | $0.1227 |
| Markdown with decisions | Haiku | 24 / 24 | 0 | 2 of 2 | 35 | $0.0381 |

Cost is Claude Code's `total_cost_usd`, an estimated API-equivalent on a subscription, not money
spent. Producing the graph cost a further $0.5031 (est.) and 37 min 34 s, once (98 model calls on
Haiku).

### Findings

1. **The format of the specification did not change what was built.** All eight builds passed all
   24 tests with no omission and no extra command. Where the inputs carried no decision, every build
   took the same side of every contradiction.
2. **What changed the build was the owner's decision, not its carrier.** With the two decisions,
   both models built the decided behaviour, whether the decisions arrived inside the graph export
   or in a plain file.
3. **The graph export cost more to use.** It is 6.4 times the length of the Markdown. The agent's
   run cost 1.6 times (Sonnet) and 2.1 times (Haiku) the Markdown run without decisions, and 1.7
   times and 3.2 times with them.
4. **The compiler reported 2 of the 4 real contradictions** (as 4 conflict records, all about those
   two). It missed the other two. The agents, reading the Markdown unaided, named 3 or 4 of the 4
   in their notes (keyword triage of the notes, not a human audit: *audit to be done*).

### What this result does not cover

- **One run per cell.** No variance was measured; small differences in turns or cost are observations.
- **One small specification.** At 2 120 words an agent can hold every file at once. Whether the graph
  helps when a specification is too large for that is *to be measured*.
- **The tests were written to avoid every contradicted value,** so they could not register a
  difference in how contradictions were handled; only the probes and the decision measure could.
- **The two decisions were chosen opposite to what agents did unaided,** so that following them
  would be visible.
- **The specification, the planted defects, the answer key and the scorer are ours,** written by the
  same person who built the compiler. One planted item (a fee ceiling of $15 beside a cap of $10)
  turned out not to be a contradiction and was removed from the count.
- **One agent product and one model family.**

### Three defects found in the export while running this

1. The export's map says nothing about settled conflicts and prints "unsettled contradictions: 0",
   which a reader can take for "no contradictions".
2. Which side of a settled conflict wins is written only in a free-text note; the losing claim stays
   in the checklist as an ordinary item.
3. One decision had to be recorded on several conflict records, and its note is repeated in each.

## R2. Result on a public benchmark (DevEval)

### What was tested

DevEval (first published as DevBench, 2024) gives, for each project, four specification documents
(a requirements document, a class diagram, a sequence diagram, an architecture note) and hidden unit
and acceptance tests with a reference implementation. We repackaged projects so that the agent's
container holds only the specification and the seed data; tests and reference are added only for
scoring. Of the nine Python projects, eight are usable this way (the reference passes every test,
a do-nothing agent passes none); one is excluded because its own reference fails under current
libraries.

Four projects were compiled and run in both formats, under the same agent conditions as R1:

| Project | Specification, words | Graph export, words | Hidden tests | Compile cost, est. |
|---|---|---|---|---|
| hone | 1 697 | 9 388 | 12 | $0.2685 |
| lice | 1 374 | 6 823 | 31 | $0.2158 |
| arxiv-digest | 1 196 | 6 569 | 42 | $0.2286 |
| stocktrends | 1 555 | 7 284 | 9 | $0.2623 |

### What was measured

On Claude Sonnet 5.5, `hone`, one run per format: 12 / 12 in both (Markdown 4 turns, $0.1171;
export 11 turns, $0.1874). The model is at the ceiling, so nothing can show.

On Claude Haiku 5.5 the model is below the ceiling:

| Project | Format | Runs | Tests passed | Of the tests stated in the specification | Cost per run, est. |
|---|---|---|---|---|---|
| lice | Markdown | 1 | 3 / 31 | 3 / 3 | $0.0197 |
| lice | Export | 1 | 3 / 31 | 3 / 3 | $0.0425 |
| arxiv-digest | Markdown | 3 | 22, 27, 28 / 42 | 20, 25, 25 / 28 | $0.0079 to $0.0111 |
| arxiv-digest | Export | 3 | 30, 30, 29 / 42 | 27, 27, 27 / 28 | $0.0237 to $0.0312 |
| stocktrends | Markdown | 1 | 3 / 9 | 2 / 2 | $0.0522 |
| stocktrends | Export | 1 | 3 / 9 | 2 / 2 | $0.1150 |

### The same three projects on Sonnet (added 2026-10-14)

Claude Sonnet 5.5 was run on `lice`, `arxiv-digest` and `stocktrends` exactly as Haiku was: same
tasks, same agent and tools, same network limits, one run per format.

| Project | Format | All tests | Stated (S) | Names only (U) | Not in spec or against it (R + C) | Turns | Agent time | Cost, est. |
|---|---|---|---|---|---|---|---|---|
| lice | Markdown | 6 / 31 | 3 / 3 | 3 / 3 | 0 / 25 | 4 | 36.8 s | $0.1039 |
| lice | Export | 6 / 31 | 3 / 3 | 3 / 3 | 0 / 25 | 7 | 44.8 s | $0.1347 |
| arxiv-digest | Markdown | 29 / 42 | 25 / 28 | 4 / 7 | 0 / 7 | 4 | 23.7 s | $0.0692 |
| arxiv-digest | Export | 30 / 42 | 27 / 28 | 3 / 7 | 0 / 7 | 8 | 31.7 s | $0.1288 |
| stocktrends | Markdown | 4 / 9 | 2 / 2 | 2 / 5 | 0 / 2 | 9 | 103.1 s | $0.2167 |
| stocktrends | Export | 3 / 9 | 2 / 2 | 1 / 5 | 0 / 2 | 10 | 107.0 s | $0.2778 |

- **No format difference that survives a reading.** `lice`: identical. `arxiv-digest`: the export
  build passed two more acceptance tests, but the Markdown build lost them because no CSV was
  written at scoring time; the same code, rerun against the live arXiv service minutes later, wrote
  it. Most likely a passing failure of the service, not of the build. `stocktrends`: the export build
  failed one test by also requiring a `date` column, which the specification does not ask for.
- **The two-test difference seen in every Haiku run on `arxiv-digest` does not appear on Sonnet.**
  The Sonnet Markdown build applies the allowed-characters rule inside the function the tests call,
  as the export builds did. It was a habit of one model reading the Markdown, not an effect of the
  format.
- **Sonnet is ahead of Haiku only on tests open to reading** (on `lice` it took BSD3 as the default
  licence, which the tests expect; 6 / 31 against 3 / 31). On tests stated in the specification the
  models are level: `lice` 3 / 3 and `stocktrends` 2 / 2 everywhere; `arxiv-digest` export 27 / 28 for
  both; Markdown 25 / 28 for Sonnet and 20, 25, 25 for Haiku, lost on different tests.
- **No build of either model in either format passed any test that needs a detail absent from the
  specification or contradicts it.** All twelve `arxiv-digest` builds kept the specified default of
  10 results where the benchmark's test expects 100; the 100 is in the benchmark's reference code
  only.
- **The export run cost more again:** 1.3 to 1.9 times the Markdown run. Sonnet runs cost 2.4 to 7.2
  times Haiku runs on the same task (against the mean of Haiku's three runs on `arxiv-digest`).

### Findings

1. **Two of three projects show no difference between formats.** On `lice` and `stocktrends` both
   builds pass and fail the same tests.
2. **One project shows a small, steady difference for the export.** On `arxiv-digest` two tests
   are passed by all three export builds and by no Markdown build. Both test one rule (only certain
   characters are allowed in a query, otherwise an error). The specification states the rule but
   not which function applies it. The export builds apply it inside the function the tests call;
   the Markdown builds whose code was kept apply it where the command line is read. The export
   lists the rule as a separate must-do item, which may be why; this was not tested.
3. **A single pair of runs misleads.** The first pair on `arxiv-digest` differed by 8 tests; over
   three runs per format the same Markdown task gave 22, 27 and 28. Most of the first difference was
   variation between runs.
4. **The export run cost more every time:** 2.2 times the Markdown run on `lice` and `stocktrends`,
   about 2.7 times on `arxiv-digest` (means of three), 1.6 times on `hone`.
5. **The compiler reported two contradictions in a public specification** (`arxiv-digest`: whether
   results are printed without the `--verbose` flag). Both are real on reading. The hidden tests do
   not depend on them.

### A finding about the benchmark itself

We read each of the 82 hidden tests of the three Haiku projects against the specification and the
seed data.

| | lice | arxiv-digest | stocktrends | Total |
|---|---|---|---|---|
| Stated in the specification | 3 | 28 | 2 | 33 |
| Names stated, expected value or behaviour not | 3 | 7 | 5 | 15 |
| Needs a name, default, key or exact text the specification does not give | 25 | 6 | 2 | 33 |
| Contradicts the specification | 0 | 1 | 0 | 1 |

No test of the last two rows was passed by any of the ten Haiku runs. Examples: the unit tests of
`lice` import a function the specification never names, so all 25 fail to load; one `arxiv-digest`
test expects a default of 100 results where the specification says 10. A raw count of tests passed
on DevEval therefore mostly measures how close a build is to the reference implementation, not how
well it follows the specification. For a comparison of specification formats, only the first row
is a fair measure, and it is small: 33 tests, of which 28 are in one project.

### What this result does not cover

- **One run per format on three of four projects;** three on one. No statistics are claimed.
- **The classification of tests is one reader's judgement,** made by the assistant that also built
  the tasks, not checked by a second reader. The line between the first two rows is soft, and the
  two tests of finding 2 sit on it.
- **Small specifications again** (1 196 to 1 697 words). An agent can read all of each.
- **Public projects.** The models may have seen them; `hone` on Sonnet finished in 4 turns.
- **`arxiv-digest` calls the live arXiv service during scoring,** so its acceptance results can
  change with the day.
- **Four of eight usable projects; Python only; one agent product; one model family.**
- **A scoring fault was found and fixed during this work:** the scorer counted tests the agent had
  written. Two results were first recorded as 8 / 9 and 7 / 9 and are 3 / 9 and 3 / 9. Every result
  above passes the check added afterwards (tests collected is at most the number of hidden tests).

## R3. Overall result so far

### The question

Does a coding agent build better software from the compiler's graph export of a specification than
from the specification's own Markdown files?

### What the evidence says

| Setting | Model | Runs per format | Difference in tests passed | Export run cost / Markdown run cost |
|---|---|---|---|---|
| `lend`, our messy specification, 2 120 words | Sonnet | 1 | none (24 / 24 both) | 1.6 |
| `lend` | Haiku | 1 | none (24 / 24 both) | 2.1 |
| `hone`, DevEval | Sonnet | 1 | none (12 / 12 both) | 1.6 |
| `lice`, DevEval | Haiku | 1 | none (3 / 31 both) | 2.2 |
| `stocktrends`, DevEval | Haiku | 1 | none (3 / 9 both) | 2.2 |
| `arxiv-digest`, DevEval | Haiku | 3 | 2 tests for the export in every run | 2.7 |
| `lice`, DevEval | Sonnet | 1 | none (6 / 31 both) | 1.3 |
| `arxiv-digest`, DevEval | Sonnet | 1 | 1 test (30 against 29), most likely the live service | 1.9 |
| `stocktrends`, DevEval | Sonnet | 1 | 1 test for the Markdown (4 against 3), on an unstated point | 1.3 |

1. **On specifications of 1 200 to 2 100 words, the format made no difference to the tests passed
   in any of nine settings that survives a reading.** The one steady difference (two tests, Haiku,
   `arxiv-digest`) is on a point the specification leaves open and does not appear on Sonnet.
2. **The export cost more to use in every setting,** 1.3 to 2.7 times the agent's run cost, on top
   of a one-time compile of $0.22 to $0.50 (est.) and 16 to 38 minutes per specification.
3. **The owner's decisions changed what was built; the carrier did not.** On `lend`, both models
   built the two decided behaviours when told them, whether through the export or through a plain
   92-word file, and neither did when not told.
4. **The compiler's conflict report has value apart from code generation.** It reported 2 of the 4
   real contradictions planted in `lend` and 2 real ones in a public specification. It also missed
   2 of the 4.

### What has not been tested

- **A specification too large to read at once.** Every specification here fits in the agent's
  working memory several times over. The case for a graph is strongest where an agent must select
  what to read; that case is *to be measured*.
- **Whether the agent uses the conflict report to ask** rather than to guess. Agents wrote notes
  about contradictions in both formats; the notes were sorted by keyword, not audited by a person:
  *audit to be done*.
- **Repeated runs on `lend`** and on three of the DevEval projects.
- **Other agents, other model families, other languages.**

### Reading

With the evidence so far, the honest statement is: at this size of specification the graph export
does not improve the code an agent writes, and it costs more. What the work does support is
narrower: the compiler finds some real contradictions before any code is written, and a decision
recorded once reaches the code. Whether the graph earns its cost on large specifications is the
open question that decides the claim.

## R4. Result on a second benchmark (Zero2Repo) — draft, rounds 13, 13b and 13c (2026-10-14 to 16)

> Sources: `harness/trials/r13-zero2repo-case004/TRIAL.md` (round 13),
> `harness/trials/r13b-zero2repo-haiku-sweep/TRIAL.md` (round 13b),
> `harness/trials/r13c-zero2repo-3cases/TRIAL.md` (round 13c), register runs 43–84 in
> `rel02_methodology_notes.md`. R3 does not yet include this section.

### Why a second benchmark

DevEval's hidden tests check details its documents do not state (R2, "A finding about the benchmark
itself"), so a format difference there could not be read as a specification effect. Zero2Repo
(commit `0ecc523`, 17 cases, no licence file, kept out of git) writes its hidden tests against a stated
Interface Contract. On case004 (`pallets/itsdangerous`, names neutralised) the original upstream code
fails only the 12 tests on behaviour the contract adds (246 / 258), which supports the claim.

### Round 13: case004, both models, both formats, two runs each

Every Markdown run passed all 258 tests (Haiku 2, Sonnet 2). Export runs: Sonnet 2 / 2 full; Haiku 1
full, 1 at 256 / 258. The two misses were caused by the compiler: one sentence of the specification
states a rule and its exception, the compiler judged them contradictory, the export showed the
contradiction as unsettled, and Haiku resolved it the wrong way. With the 18 detected contradictions
judged false (all were a rule and its stated exception or condition) and the export remade, Haiku
passed 258 / 258 twice, at 20–35 turns against 46–75 with the unsettled export and 24–26 with the
Markdown. Sonnet's turns and cost did not change with the format.

### Round 13b: which cases does Haiku fail from the Markdown?

**Intention.** case004 sat at the ceiling: a format can only lose there. The sweep looks for cases
where Haiku, given the plain Markdown, does not pass every test, so the export has room to show a gain.
One Haiku run per case (a screen, not a rate), on the 8 Python cases that run on a Python + Node image;
the 9 TypeScript, C/C++, Go and Zig cases need their toolchains in the image and are not run.

| Case | Upstream | Spec words | Tests passed | Turns | $ est. |
|---|---|---|---|---|---|
| case001 | tomli | 4 860 | 302 / 302 | 14 | 0.05 |
| case007 | pyotp | 5 122 | 80 / 80 | 16 | 0.03 |
| case011 | jmespath | 7 002 | 321 / 321 | 20 | 0.27 |
| case002 | python-envfile | 7 202 | 281 / 281 | 24 | 0.07 |
| case005 | h11 | 7 915 | 395 / 395 | 22 | 0.37 |
| case010 | nltk | 8 412 | **166 / 197** | 33 | 0.45 |
| case006 | click | 14 138 | **464 / 476** | 81 | 1.24 |
| case016 | sloptrim | 18 964 | **370 / 388** | 53 | 0.55 |

**Findings.** With case004, Haiku passes 6 of the 9 Python cases in full from the Markdown. The three
it fails are the three largest specifications (8 412 to 18 964 words; the passes are 4 860 to 7 915).
On case010 Haiku left out the Snowball stemmers the specification requires, and made ARLSTem raise
because the specification calls its results "outside this specification" (the tests only check that
it constructs and returns a string); on case006 and case016 the misses are edge cases and rules spread over many features
(read in round 13c, below). **Correction (2026-10-16):** 20 of case010's 197 tests cannot pass in our
tasks (model files missing, see 13c); on the 177 scorable tests this run is 146 / 177, all 11 misses
in the stemmers.

**What this does not cover.** One run per case; famous upstreams (recall: in round 13 the agents
chose upstream's own module names, which the specification does not give); Python only.

### Round 13c: three cases Haiku fails, both models, both formats, two runs each

**Intention.** Take the three cases Haiku failed from the Markdown in 13b (case010 nltk, case006
click, case016 sloptrim: 8 412, 14 138 and 18 964 words) and ask whether the spec-graph export
changes which hidden tests pass, for Haiku and for Sonnet, and why the failing tests fail. Each case was
compiled with `sddc` (Haiku), every contradiction the compiler raised was judged against the
specification (145 in all, every one false: a rule and its stated exception, two different
components, or a word in two senses), and the export was made with none left unsettled. 24 runs:
3 cases × 2 models × 2 formats × n = 2.

**A benchmark fault first.** 20 of case010's 197 tests need NLTK model files that Zero2Repo's own
runner downloads before scoring and its Harbor adapter output does not. In our tasks these 20 fail in
every run whatever the code, so case010 is read on the 177 scorable tests below.

| Case (tests) | Haiku Markdown | Haiku export | Sonnet Markdown | Sonnet export |
|---|---|---|---|---|
| case010 (177 scorable) | 142, 149 (13b: 146) | 148, 146 | 155, 156 | 156, 155 |
| case006 (476) | 452, 0 ¹ (13b: 464) | 425, 467 | 470, 469 | 473, 470 |
| case016 (388) | 381, 378 (13b: 370) | 364, 379 | 385, 387 | 387, **388** ² |

¹ Haiku stopped early calling its code "a partial build"; the tests could not import it.
² Official 1.0, the only full pass of the round.

Turns, Haiku: Markdown 33–47 (runs that finished), export 63–87. Sonnet: 21–38 in both formats.
Estimated cost (Claude Code's `total_cost_usd`): runs $38.61, three runs stopped at the usage limit
and rerun $4.37, compiles $11.16 (386, 853 and 939 Haiku calls).

**Findings.**

- **The settled export did not change which tests pass.** Test by test, no test fails in every run of
  one format and in no run of the other, for either model, on case010 and case016 (for Haiku the 13b
  run counted as a third Markdown run). On case006 Haiku shows 2 such tests each way, on 2 runs per
  format. Sonnet's totals overlap between formats on every case.
- **Haiku works about twice as long on the export without scoring higher** (63–87 turns against
  33–47; 1.4–1.9× the estimated cost). On case004 (round 13) the settled export had brought Haiku's
  turns down to about the Markdown's; on these larger specifications (export 5.0–5.3× the Markdown's
  words) it does not.
- **The failures are mostly not about reading the specification.** case010: algorithms the
  specification names without giving their rules (Snowball, Lancaster stemmers); Haiku leaves them
  out, Sonnet approximates them and misses exact stems. case006 and case016: single stated rules among
  hundreds (a tie rule, five distinct failure replies, Unicode character classes), missed in both
  formats. Where a format difference shows on case006, the rule is present word for word in both
  formats.
- **The compiler's contradictions were all false again** (145 here, 18 in round 13): on specifications
  written carefully, every one it raised was a rule with its own stated exception or condition, or two
  different things with similar wording. Two judgements were readings the text leaves partly open.

**What this does not cover.** n = 2 per cell; a time-of-day difference between formats cannot be
excluded (the Markdown runs went first); case010's 20 unscorable tests are not rescored with the model
files installed (possible without a model call, from the saved code); famous upstreams; Python only.

## R5. Planted conflicts in a large specification (Zero2Repo case006) — draft, round 14 (2026-10-16)

### Why this round

Rounds 13–13d showed no test-level effect of the export on carefully written specifications, where
every contradiction the compiler raised was false. The product's claim is about specifications that
disagree with themselves. No public benchmark has such specifications (rel02 D13), so this round plants
conflicts, by design and with an answer key, into one large public case: Zero2Repo case006 (14 138
words, 476 hidden tests; the `click` library renamed Optlyn). Record:
`harness/trials/r14-zero2repo-case006-conflicts/` (`TRIAL.md`, `ANSWER_KEY.md`); design in
`rel02_brainstorm.md` S17.

### How the conflicts were built

**Designed, not random.** A random edit can fall where no agent builds working code, so a miss cannot be
told from an unbuilt feature; it can change any number of hidden tests; it is usually a plain value
swap, so the kinds a compiler finds hard are missing; and it cannot be balanced over distance and kind.
Each planted item was therefore chosen by five rules and written down, with both sides, before any
compile or agent run:

1. **Built in every past run.** The hidden tests closest to the behaviour passed in all, or all but one,
   of the 9 earlier case006 runs, so every agent writes the code the conflict touches.
2. **Both sides observable.** Each side gives a different result seen from outside the code (a stream,
   a value, a file, a help line), so a probe can say which side a build took.
3. **Narrow footprint, measured.** At most 3 hidden tests may change result between the two sides.
   Measured without opening the tests: one good earlier build (473 / 476) was patched to each side and
   the hidden tests run on every copy through Harbor's oracle agent (no model). The tests that flip are
   the item's footprint. Two candidates failed this rule and were dropped (7 tests; 238 tests).
4. **Side A is the original library's behaviour**, which the hidden tests check and the model may
   remember. A build on side A is therefore never taken as evidence that the agent noticed anything,
   and every ruling goes to side B.
5. **Real drift.** One sentence or table row in one place, in the specification's own voice, with no
   marker; the other place keeps side A.

Seven items were kept, spread over distance and kind: two in the same paragraph or bullet (a direct
control, and an example that contradicts its rule), three across the two documents (prose against a
table, and a precedence order), and two far apart in one document (a rule inside a glossary
definition, and a numeric default). Footprints: 0–3 tests each, 7 tests in all.

### How the builds were tested

- **The benchmark's tests and judge are unchanged.** A build that follows a ruling to side B fails that
  item's footprint tests by design, so builds are compared on the **core score**: the 469 tests
  outside the footprints. Earlier rounds were rescored on the same 469 from their saved reports.
- **New tests outside the reward:** one black-box probe per item, written from the answer key and the
  interface document only, run afterwards on each build's saved code in a container with no network.
  Checked before use: the base build reads side A on every item, and each patched copy reads side B on
  its own item only.
- **Exposure:** one phrase per side, unique in the specification; a run is exposed to a side when a
  tool result in its transcript contains the phrase. This separates "never read" from "read, not
  noticed", the risk that a planted conflict is missed by chance.
- **Stated detection:** one instruction line, the same in every cell, asks the agent to list each
  disagreement it finds and the choice it made in `NOTES.md`. The notes are read item by item.
- **Compiler recall:** which planted items the compile reports, against the answer key.

### Design of the runs

The compile reused the finished store of the earlier round: the 7 changed blocks were re-ingested and
compiled (35 calls, $0.124 est.). Haiku, Claude Code 2.1.296 in Harbor, n = 3 per cell. Round 2
(unsettled): Markdown against the export with the reported planted conflicts left open (`UNSETTLED`,
both quotes in both packs). Round 3 (settled): the owner's rulings, all to side B, given for the 4
reported conflicts; the settled export against the Markdown with the same rulings as a plain
`DECISIONS.md`. One Markdown run stopped early on a misread budget message and was replaced.

### Results

| Cell | Core of 469, mean (range) | Noticed: the 4 reported | Noticed: the 3 not reported | Rulings built |
|---|---|---|---|---|
| Markdown | 443.0 (424–457) | 7 / 12 | 6 / 9 | — |
| Export, unsettled | 431.0 (400–462) | 12 / 12 | 7 / 9 | — |
| Markdown + `DECISIONS.md` | 428.3 (410–452) | ruled | 5 / 9 | 11 / 12 |
| Export, settled | 455.7 (450–460) | ruled | 9 / 9 | 12 / 12 |

Compiler recall: 4 of 7 (missed the glossary rule, the far-apart default and the example). Every run
read both sides of every item. Cost: $11.64 est. (13 runs and the compile).

### Findings

- **The export made Haiku report more of the conflicts it lists** (12 of 12 against 7 of 12 from the
  Markdown); a precedence conflict across the two documents was reported by no Markdown run and by
  every export run. On conflicts the compiler did not list, the formats were close when unsettled.
- **Reporting a conflict did not change the build.** Unsettled, 40 of 42 item-runs took the original
  library's side in both formats, with reasons such as "the more specific rule".
- **Rulings reached the code from both carriers** (12 of 12, 11 of 12); the one miss was a ruling
  stated in the notes and not built, caught by the probes only.
- **No effect on the rest of the build** can be claimed: core means overlap and sit inside the earlier
  Haiku spread on the unplanted specification (409–460).

### The compiler's misses, traced and changed (after the runs)

P6 was lost to the incremental compile itself (only the new end of the pair was ranked; the old end
ranked it inside its cap), P7 because examples were annotations that nothing compared, and P4 to
ranking (7th, one past the cap). The compiler was changed so that an incremental run proposes a pair
from either end, and an example becomes a verification node of the claim it follows (rel02 D26). The
same compile, with the same model answers replayed, then found 6 of 7 (29 calls, $0.0732 est.), with
one more false alarm (3). P4 was left as is: widening the cap to catch it would fit the answer key.
The agent runs above used the 4-of-7 export and were not repeated.

### Round 15: the 6-of-7 export, and both rounds together (2026-10-16 to 18)

Round 15 repeated round 2's question with the improved compiler's export, which lists 6 of the 7
planted conflicts as open (`harness/trials/r15-zero2repo-case006-conflicts-v2/`). Haiku, Markdown
against export, 2 runs each. The runs were operated by GitHub Copilot CLI from a written procedure
(`rel02_handover_copilot_r15.md`); its write-up was checked against the run data and corrected in four
places (the trial's "Review" section). One Markdown run stopped early (below), leaving 1 valid Markdown
run and 2 export runs.

**Both rounds, conflicts left open** (round 14's 3 + 3 runs and round 15's 1 + 2; detection from each
run's `NOTES.md`):

| Planted conflict | Named, Markdown (4 runs) | Named, export (5 runs) |
|---|---|---|
| P1 isolated folder, same paragraph | 4 | 5 |
| P2 warning channel, prose vs table | 4 | 5 |
| **P3 environment vs default map, across files** | **0** | **5** |
| P4 glossary rule, far apart (never listed) | 4 | 5 |
| P6 80 vs 100 columns, far apart | 3 | 5 |
| P7 example against its rule | 2 | 3 |
| **R1 confirm, across files** | **1** | **5** |
| All | 18 of 28 | 33 of 35 |
| Core score, mean (range) | 439.8 (424–457) | 440.2 (400–462) |

- **The export makes the agent report the conflicts it lists, and the difference is in the
  conflicts that span the two documents** (P3 and R1). Conflicts inside one paragraph, or the glossary
  rule against its section, were named from either format.
- **It does not change the tests passed:** the core means differ by 0.4 tests out of 469, and the
  ranges overlap. Nor does naming a conflict change what is built: unruled, both formats built the
  original library's side on almost every item.
- **A rendering fault, found and fixed:** the improved compiler formed the P7 example as a
  verification node, and the export listed it under *Acceptance criteria*. Both round 15 export runs
  built the example's side, one calling it "the acceptance criterion" (the Markdown run did too, so the
  heading is not shown to be the cause). The export now lists such a node beside the claims, as
  `example of N-…` (F7 D17, rel02 D27). Round 15's export runs predate the fix.

### A Haiku failure that costs runs (observed, not a format finding)

On case006, Haiku sometimes spends its whole first answer planning: it thinks until it reaches the
128 000-token output limit. Claude Code then cuts the answer and tells it to continue in smaller
pieces. In some runs Haiku next reads Claude Code's budget reminder as money left ("The run is out of
budget: $0.0008 of the $10 remains"), writes no code and stops, having used about $0.08 of its $10
ceiling. The judge then finds nothing to test. This happened in **3 of 12 Haiku Markdown runs** on
case006 (13c, round 14, round 15) and in **none of 12 Haiku export runs**. That difference may be
chance at this size and is not claimed as an effect. The stopped runs are recorded and left out of the
scores, and a stopped run is simply run again. The study does not cap Haiku's thinking, so the runs
keep the same conditions throughout (owner, 2026-10-18).

### What this does not cover

n = 3; one reader of the notes, not blind to format (the export's conflict ids would defeat
blinding); rounds run in sequence; Haiku only; one case, from a library the model knows; 7 items.
