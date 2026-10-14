# rel02 — draft report sections

> **Status:** draft, opened 2026-10-13 (round 6 of the working map). Non-authoritative. Every figure
> comes from a file named in `rel02_methodology_notes.md` §8 or in
> `harness/platforms/harbor/TRIAL.md` §5b–5e, or in `harness/benchmarks/devbench-2024/TRIAL.md` §7–10.
> Method detail is in the methodology notes; this file holds the wording of results. R1 written in
> round 6, R2 and R3 in round 10 (2026-10-13). Sections not listed here are *to be written*.

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

1. **On specifications of 1 200 to 2 100 words, the format made no difference to the tests passed
   in five of six settings,** and a two-test difference in the sixth, on a point the specification
   leaves open.
2. **The export cost more to use in every setting,** 1.6 to 2.7 times the agent's run cost, on top
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
