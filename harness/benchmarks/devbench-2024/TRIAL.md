# Trial record — DevEval (first published as DevBench, 2024)

> **Kind:** benchmark, available as a Harbor dataset · **State:** TRIED 2026-10-12; **pilot run on one
> repackaged project (§7): Markdown 12 / 12, graph export 12 / 12 — the formats did not separate** ·
> **Verdict:** none yet — the owner decides at milestone 2.
> **Recommendation: keep as the leading public candidate, but not as packaged.** It is the first
> candidate whose input is a set of specification documents (a PRD, two UML diagrams and an
> architecture design per project). The Harbor packaging cannot be used for our study as it stands:
> it leaves most of the code, the tests and the full reference answer where the agent can read them
> (§3). A repackaging of our own would be needed (§5).
> Milestone 1 of `sdd/design/rel-02/rel02_brainstorm.md`. This file is the record for the final
> report: what was tried, what happened, and why the candidate was chosen or rejected.
> Rules: no number that was not printed by a command here; no claim about the paper that was not read
> on the page; failures are written down, not removed.

## 0. What we knew before the trial (not verified by us)

**Nothing verified.** A web-search snippet seen 2026-09-29 said a benchmark called DevBench uses PRDs
and UML as input; the survey marks that snippet as not to be cited. Added by the owner 2026-10-12
(rel02 Q7). On 2026-10-12, during the Harbor trial, the dataset `deveval` was found in Harbor's
registry, and its adapter page said DevEval was "originally named DevBench". The owner moved this
trial up the queue on that lead.

## 1. Source

| | |
|---|---|
| Paper | Li, Wu, Tang, Shi, Yang, Li, Yao, Qian, Hui, Zhang, Yu, Du, Yang, Lin, Peng, Chen, arXiv:2403.08604 (v1 13 Mar 2024, v3 14 Dec 2024). **Current title on arXiv:** *Prompting Large Language Models to Tackle the Full Software Development Lifecycle: A Case Study*; the benchmark is called DevEval in the abstract. Abstract page read through a summarising fetch; **the paper body is not read** — do that before citing it |
| Is it "DevBench"? | Yes, by two secondary sources: the repository's README is headed "DevBench: Towards LLMs based Automated Software Development" while the repository is named DevEval, and Harbor's adapter page says "originally named DevBench". The arXiv page shown to us does not use the name. **Not the same** as the 2026 DevBench paper (Kumarappan et al., arXiv:2601.11895) |
| Code / data URL | Original: `https://github.com/open-compass/DevEval` (README read through a summarising fetch; **not cloned**). Tried here: Harbor dataset `deveval@1.0`, adapter at `github.com/laude-institute/harbor/tree/main/adapters/deveval` |
| Version or commit tried | Harbor dataset `deveval` version `1.0`, downloaded 2026-10-12 with Harbor 0.24.0. The upstream commit it was built from is not recorded in the tasks |
| Licence (read where) | Per the original README (summarised fetch): code Apache-2.0, data CC BY 4.0. **Not read word for word.** Each bundled project also carries its own licence file |
| Download size | 43 MB for 63 tasks, 11 s. Base image `ghcr.io/laude-institute/t-bench/deveval:latest` pulled on first run (size not recorded; Harbor removed it afterwards) |
| Downloaded to | `download/deveval/` in this folder (ignored by git) |

## 2. The five questions

| # | Question | Answer | Evidence (command or file) |
|---|---|---|---|
| 1 | What does one task's specification look like (form, length, files)? | **Four Markdown documents per project:** `PRD.md`, `UML_class.md` and `UML_sequence.md` (Mermaid diagrams), `architecture_design.md` (file tree plus a line per function). Over 21 projects: **median 1 274 words in total** (min 524, max 3 005); the PRD is the largest (median 718). For scale, our `lend` task is 2 120 words in 7 files. The documents are clean and agree with each other; nothing in the sample read looked like a planted or accidental conflict | `spec_stats.py`; §3 |
| 2 | Can that specification be replaced by our three formats (flat, tiered, graph)? | **Yes in principle.** The four files are a small folder of specifications of different kinds (requirements, structure, behaviour, layout), which is what the compiler takes. Flat = the four files joined (this is what the Harbor task already does in `instruction.md`); tiered and graph = our renderings. **Not tried:** compiling one (needs model calls) | `instruction.md` of any `*-implementation` task |
| 3 | Can it score a project that Claude Code built **outside** its own pipeline? | **Yes.** Scoring is the project's own unit and acceptance tests run by a shell script; any agent Harbor supports can produce the code | `tests/test.sh`; §3 |
| 4 | What does it need to run (OS, Docker, browser, a model for judging, a paid key)? | Harbor and Docker; **no model for judging** the implementation, unit-testing and acceptance-testing tasks. One project (`java-actor-relationship-game`) needs a TMDB key per the original README. The original benchmark's *software design* task is judged by a model, but the Harbor dataset does not include that task. **As downloaded the task fails** under Harbor 0.24.0 until `--ve TEST_DIR=/tests` is added (§4) | §3, §4 |
| 5 | Which of our metrics does it give (tests passed, omission, hallucination, time, cost, tokens)? | **One number, all-or-nothing:** reward 1 if both the unit tests and the acceptance tests pass completely, else 0. The script does write per-test JSON reports and coverage inside the container, so a finer score could be taken from them. Time, cost and tokens come from Harbor. Omission and invention: no | `tests/test.sh`, `tests/test_outputs.py` |

## 3. The one number

**Shape of the specifications** (no model; `python3 -I spec_stats.py download/deveval`, 21 projects):

| | min | median | mean | max |
|---|---|---|---|---|
| `PRD.md`, words | 295 | 718 | 745.2 | 1 706 |
| `UML_class.md`, words | 33 | 120 | 113.4 | 238 |
| `UML_sequence.md`, words | 44 | 71 | 100.0 | 331 |
| `architecture_design.md`, words | 123 | 319 | 374.0 | 1 005 |
| All four together, words | 524 | 1 274 | 1 332.5 | 3 005 |
| Instruction the agent receives, words | 561 | 1 331 | 1 379.4 | 3 071 |
| Source files the task removes | 1 | 2 | 3.5 | 10 |
| Source files named in the project's file graph | 1 | 4 | 4.6 | 11 |
| Lines in those source files (the reference) | 61 | 368 | — | 840 |

Languages: 9 Python, 5 C++, 5 Java, 2 JavaScript. Each project gives three tasks (implementation,
unit testing, acceptance testing): 63 tasks. Only the implementation task matches our study.

**The task in Harbor, with the two no-model agents** (`python-readtime-implementation`):

| Run | Result |
|---|---|
| Reference solution, as downloaded | **Failed**: `RewardFileNotFoundError`. `test.sh` line 36 calls `$TEST_DIR/setup-uv-pytest.sh` and `TEST_DIR` is not set |
| Do-nothing agent, as downloaded | Same failure |
| Reference solution, with `--ve TEST_DIR=/tests` | **Reward 1.0** (2 of 2 checks; `readtime-oracle.result.json`). Environment 12.7 s, verifier 36.0 s, 1 min in all |
| Do-nothing agent, with `--ve TEST_DIR=/tests` | **Reward 0.0** |

**What the agent can see inside the task image** (built from the task's own Dockerfile and listed;
the container runs as `root`):

| Item | Present | Why it matters |
|---|---|---|
| `/deveval_source_repo/readtime/result.py` — the file the agent is asked to write | **Yes** | The whole reference project is copied into the image; the task's own `solve.sh` just copies the file back from there |
| `/app/unit_tests/`, `/app/acceptance_tests/` — the scoring tests | **Yes** (`chmod 700`, which does not stop `root`) | The tests are not hidden |
| `/app/readtime/api.py`, `utils.py` — the rest of the source | **Yes** | For this project the agent writes 1 file of 3; over all projects a median of 2 of 4 |

So, as packaged, the task is "fill in the missing files of an existing project, with the tests and
the answer on disk". That is not a test of building from specifications, and a result from it could
not be defended. No other project's image was inspected; the same three lines are in every
implementation task's Dockerfile (read with `grep`).

## 4. Log

| Date | What was done | Result |
|---|---|---|
| 2026-10-12 | Opened arXiv:2403.08604 (abstract page) and `github.com/open-compass/DevEval` (README), both through a summarising fetch | Title, authors, dates; "22 curated repositories", 4 languages; five tasks in the original (software design, environment setup, implementation, acceptance testing, unit testing); software design judged by a model |
| 2026-10-12 | `harbor download deveval@1.0 -o download` | 63 tasks, 43 MB, 11 s |
| 2026-10-12 | Read one task in full (`python-readtime-implementation`: instruction, `task.toml`, Dockerfile, `test.sh`, `test_outputs.py`, `solve.sh`, `repo_config.json`) | §2, §3 |
| 2026-10-12 | First version of `spec_stats.py` | **Wrong for 6 projects** (it reported 0 words): those keep the four documents at the project root, not in `docs/`. Fixed to read the paths from `repo_config.json`; rerun, all 21 non-zero |
| 2026-10-12 | `harbor run -p deveval/python-readtime-implementation -a oracle` and `-a nop` | Both failed: no reward file; cause `TEST_DIR` unset |
| 2026-10-12 | The same two runs with `--ve TEST_DIR=/tests` (their files unchanged) | 1.0 and 0.0 |
| 2026-10-12 | `docker build` of the task's `environment/`, listed `/deveval_source_repo`, `/app`, user | Reference, tests and remaining source all readable; user `root`. Probe image removed |

No model was called.

## 5. Verdict

**Chosen / rejected / kept as backup:** *the owner decides at milestone 2.* Recommendation:
**keep as the leading public-benchmark candidate, conditional on our own repackaging; reject the
Harbor packaging as it stands.**

**Reasons to keep it:**

1. *Its input is a specification, in several documents of different kinds.* PRD, class diagram,
   sequence diagram, architecture design. Neither ProjectEval (one sentence or a checklist) nor
   Doc2Feat-Bench (a 30-line diff) has that.
2. *The size is in the range of our own task:* median 1 274 words against `lend`'s 2 120.
3. *It is scored by tests, with no model as judge,* and it already runs on Harbor with the free
   sanity agents.
4. *It is published and named,* which our home-made task is not.
5. *21 projects in four languages,* small enough (reference median 368 lines) for one agent run each.

**Reasons for caution:**

1. *The specifications are clean.* They read as written to describe finished code: the architecture
   design lists the file tree and every function. There are no contradictions to find, so the part of
   the compiler that detects conflicts has nothing to show, and at about 1 300 words a flat file may
   already be easy to read. **The formats might not differ on it** — the same worry as `lend`'s
   24 / 24, and it can only be settled by a pilot.
2. *The packaging leaks,* as shown in §3. Our repackaging must: start from an empty source tree,
   keep the tests out of the agent's container, and not ship the reference.
3. *All-or-nothing reward.* A finer score has to be taken from the per-test reports.
4. *Public since March 2024,* and several projects are real open-source packages (`readtime`, `lice`,
   `geotext` …), so a model may know the code. *Our reasoning, not measured.*
5. *Six of 21 projects in C++ or Java* need their toolchains; only one Python task was run.

**What repackaging would take** (*estimate, not done*): a script like
`harness/platforms/harbor/build_lend_task.py`, reading each project's four documents and
`repo_config.json`, writing an instruction with the specification in one of our three formats, an
image without the source or tests, and a `test.sh` that copies the tests in and reports the per-test
counts. The data licence (CC BY 4.0 per the README) appears to allow it; read the licence text first.

**What we lose if we reject it:** the only public benchmark found so far with multi-document
specifications; the report would rest on home-made tasks alone.

**What we lose if we choose it:** the "messy specifications" premise of the product is not exercised,
since these documents do not conflict; and we take on a repackaging whose result is no longer
comparable with numbers published for DevEval.

## 7. Pilot on one cleanly repackaged project (2026-10-12, approved by the owner)

**Question:** on a DevEval project with no leak, does the specification's format change what Claude
Code builds? **Answer from one run per format: no difference in tests passed; the graph export cost
more.** This is a pilot (n = 1 per arm), not a result of the study.

### 7.1 What was done

| Step | Command or file | Result |
|---|---|---|
| Repackage `python-hone` clean | `build_clean_task.py python-hone markdown download/clean/hone-markdown` | Agent's container holds only `spec/` (the four documents, 1 697 words), `data_file/` and one test helper. 12 hidden tests (7 unit, 5 acceptance) uploaded only for scoring; reference only for the `oracle` agent |
| Check the task, no model | Harbor `oracle` and `nop` agents | **12 / 12** and **0 / 12**; `/tests` absent during the agent phase |
| Compile the four documents | `~/sddc-runs/deveval-hone/`: `sddc init`, profile `contract_languages` extended with `mermaid` and `bash` so each UML diagram and the file tree stay whole, `sddc compile` (Haiku, subscription) | 121 blocks → **61 nodes**, 26 families; 69 blocks formed no node; 233 pairs judged; **3 conflicts, all duplications, 0 contradictions**; 56 model calls, **$0.2685 est. API-equivalent** (the compiler's own figure; the lock files sum to $0.2653 over 55 recorded calls); 18 min 1 s |
| Export | `sddc export --out export --allow-open` | 16 packs + `MAP.md` + `CHECKLIST.md`: **9 388 words**, 5.5 times the 1 697 words of the Markdown |
| Build the export task | `build_clean_task.py python-hone export download/clean/hone-export ~/sddc-runs/deveval-hone/export` | Same task, tests and seed files; only `spec/` and one sentence of the instruction differ |
| Run each once | Harbor, `claude-code`, `anthropic/claude-sonnet-5-5`, `--ak max_budget_usd=10 --ak disable_web_search=true`, subscription token | Below |

### 7.2 The two runs

Source: each trial's `result.json` (copied here as `pilot-hone-<format>-sonnet-1.result.json`) and the
`result` event of `agent/claude-code.txt`. Claude Code 2.1.296, model reported `claude-sonnet-5-5`,
`apiKeySource: "none"`, no web tools in the tool list.

| | Markdown (4 files) | Graph export |
|---|---|---|
| Hidden tests passed | **12 / 12** | **12 / 12** |
| Turns | 4 | 11 |
| Agent time | 32.5 s | 56.4 s |
| Cost, est. API-equivalent (`total_cost_usd`) | $0.1171 | $0.1874 |
| Output tokens | 4 723 | 7 068 |
| Cache-read tokens | 67 714 | 238 542 |
| Cache-write tokens | 15 760 | 23 214 |
| Claude Code install (Harbor `agent_setup`) | 105.9 s | 97.4 s |
| Mentions of `CHECKLIST` in the transcript | 0 | 8 |
| `pip install hone`, `pypi`, `curl`, `/tests` in the transcript | 0 | 0 |

One-off cost on the export side, not in the table: the compile, $0.2685 est. and 18 minutes.

### 7.3 What it shows, and what it does not

- **Ceiling effect.** Both arms pass every test, so tests-passed cannot rank the formats here. The
  same happened on `lend` with Markdown (24 / 24). With one run per arm, even a real difference in
  cost (1.6 times) or turns (2.75 times) is an observation, not a finding.
- **The export was the more expensive input on a small, clean specification.** It is 5.5 times longer,
  and the transcript shows the agent paging through the packs with `cut` and `sed` before writing.
- **The compiler found nothing wrong with the specification:** three duplications, no contradiction.
  That fits the caution in §5: these documents are clean, so conflict detection has no work to do.
- **Speed suggests familiarity, not proven.** The Markdown run wrote a project that passes 12 hidden
  tests in 4 turns and 32 s. `hone` is a public package. Whether the model already knew it was not
  tested (§6.3). The code the runs wrote was not compared with the reference (they wrote through shell
  commands, and Harbor did not keep the workspace).
- **Not shown:** anything about omission or invention (not scored); other projects; other models
  (Haiku might not be at the ceiling); the tiered format (not built yet).

### 7.4 Conclusion for milestone 2

DevEval is usable on Harbor once repackaged, and the repackaging is small (one 130-line script, one
project done). But **as a test of specification format it is too easy and too clean** for Sonnet:
the pilot gives no sign that the formats separate. To be useful it would need at least one of: a
weaker model, larger projects (the C++ ones have up to 3 005 words), or a finer measure than
tests-passed.

## 8. Round 6: all nine Python projects repackaged clean and checked (2026-10-13, no model call)

**Question:** how many DevEval projects can be used as clean tasks on Harbor, under the same agent
conditions as `lend`?

`build_clean_task.py` now handles any Python project and takes `--claude-version` and
`--agent-network allowlist` (the round 1 conditions of `lend`). Seed files are the project's
`required_files` plus data files inside the package; every `.py` file outside tests, examples and docs
is the reference. Each task was run with Harbor's `oracle` (reference) and `nop` (do-nothing) agents.
Result file: `clean-tasks-check.json`.

| Project | Spec words (4 documents) | Hidden tests | Reference | Do-nothing | Usable |
|---|---|---|---|---|---|
| arxiv-digest | 1 198 | 42 | 42 / 42 | 0 | yes |
| chakin | 982 | 2 | 2 / 2 | 0 | yes, but 2 tests only |
| geotext | 895 | 9 | 9 / 9 | 0 | yes |
| hone | 1 699 | 12 | 12 / 12 | 0 | yes |
| hybrid-images | 760 | 20 collected | **12 / 20** | 0 | **no** |
| lice | 1 376 | 31 | 31 / 31 | 0 | yes |
| particle-swarm-optimization | 524 | 6 | 6 / 6 | 0 | yes |
| readtime | 827 | 12 | 12 / 12 | 0 | yes |
| stocktrends | 1 556 | 9 | 9 / 9 | 0 | yes |

**8 of 9 usable, 123 hidden tests in all.** Three packaging problems were found on the first pass and
two fixed:
- `arxiv-digest`: its dependency list names standard-library modules (`os`, `csv`, …), so
  `pip install -r` fails as a whole. Fixed: requirements are installed one at a time.
- `readtime`: the reference fails one acceptance test when unit and acceptance tests share a
  process (it adds methods to a class at run time). Fixed: the two folders run in separate processes,
  as DevEval runs them.
- `hybrid-images`: needs system libraries for OpenCV (added to its image), and then the reference
  still fails 8 unit tests with `ValueError: setting an array element with a sequence` under the
  NumPy that an unpinned `numpy` installs today. Not fixed; the project is left out.

**Limits to state.** Every one of these specifications is smaller than `lend` (524 to 1 699 words
against 2 120), so DevEval cannot answer the scale question. The hone pilot (§7) showed a ceiling on
Sonnet. `hone`'s instruction text changed slightly against the pilot (the list of files present). The
12 C++, Java and JavaScript projects are not repackaged. The compile of the seven other
specifications and any agent run need the owner's approval (model calls).

## 9. Round 7: three projects, both formats, Haiku (2026-10-13)

**Question:** on clean public specifications and a weaker model, do the formats differ?

### 9.1 Compiles (Haiku, subscription; one attempt each, cap of 300 calls not reached)

Stores `~/sddc-runs/deveval-<project>/`, profile of the hone pilot, compiler commit `03b44e6`. The
three ran in parallel. Source: `round7/<project>-compile-1.json`; times from the start and finish
stamps beside it in the store.

| Project | Words | Blocks | Nodes | Blocks with no node | Pairs judged | Conflicts opened | of which contradictions | Model calls | Cost (est.) | Time |
|---|---|---|---|---|---|---|---|---|---|---|
| lice | 1 374 | 76 | 58 | 27 | 180 | 2 | 0 | 43 | $0.2158 | 15 min 43 s |
| arxiv-digest | 1 196 | 79 | 55 | 26 | 194 | 8 | 2 | 46 | $0.2286 | 16 min 31 s |
| stocktrends | 1 555 | 96 | 66 | 35 | 220 | 10 | 0 | 55 | $0.2623 | 17 min 44 s |

Three compiles: 144 calls, $0.7067 est. API-equivalent.

**The compiler reported two contradictions in `arxiv-digest`,** a specification we took to be clean:
- CF-000003: `PRD.md` line 23 says that with only `--to_file` the program saves without printing;
  the sequence diagram has `main` always calling `print_results`.
- CF-000006: `PRD.md` line 21 says console output is controlled by `--verbose`; line 23 says results
  are printed when neither flag is given.
Neither was checked against the reference or the tests yet (*to be read*). They are left unsettled.

### 9.2 Exports and tasks (no model)

`sddc export --allow-open --out export`; checksums in `round7/<project>-export.sha256`.

| Project | Packs | Export words | Times the Markdown | Unsettled |
|---|---|---|---|---|
| lice | 16 | 6 823 | 5.0 | 0 |
| arxiv-digest | 12 | 6 569 | 5.5 | 2 |
| stocktrends | 12 | 7 284 | 4.7 | 0 |

Export tasks built with `build_clean_task.py python-<project> export … --claude-version 2.1.296
--agent-network allowlist`. For each project the Markdown and export tasks have the same seed files,
tests and reference; the instruction differs in one sentence (checked with `diff`).

### 9.3 Runs (Haiku, n = 1 each) — 4 of 6 finished

Harbor, `claude-code` 2.1.296, `anthropic/claude-haiku-5-5`, tools `Bash`, `Edit`, `Read`, `Write`, agent
network limited to the model API and PyPI, two runs at a time. **The `stocktrends` pair did not finish:**
the session's background command was stopped by the system for low memory while both runs were in
their agent phase. Their two containers were removed. They were not restarted (to be decided by the
owner). Files: `round7/<project>-<format>-haiku-1.{result.json,reward.json,pytest.out}`.

| Project | Format | Hidden tests passed | Turns | Agent time | Cost (est.) |
|---|---|---|---|---|---|
| lice | Markdown | 3 / 31 | 10 | 100.4 s | $0.0197 |
| lice | Export | 3 / 31 | 45 | 178.7 s | $0.0425 |
| arxiv-digest | Markdown | 22 / 42 | 6 | 39.3 s | $0.0079 |
| arxiv-digest | Export | 30 / 42 | 19 | 127.7 s | $0.0312 |
| stocktrends | Markdown | not finished in round 7; run in round 8, §9.4 | | | |
| stocktrends | Export | not finished in round 7; run in round 8, §9.4 | | | |

**Haiku is well below the ceiling on both projects,** unlike Sonnet on `hone` and both models on `lend`.

**Reading, from `pytest.out` (not a full audit):**
- `lice`, both formats, the same failure: the unit-test file imports the name `LICENSES` from
  `lice.core`; neither build defines it, so the whole file (25 tests) fails to load and only the 6
  acceptance tests run (3 pass, 3 fail in both). `LICENSES` is in the specification: a class box in
  `UML_class.md` (2 mentions), and in export pack 14 (4 mentions). So both builds omitted the same
  specified name. One missing name removes 25 of 31 tests: tests-passed is a brittle measure here.
- `arxiv-digest`: the export build passes 8 more tests (30 against 22). The Markdown build fails 4
  tests because no CSV file is written and 3 because no `ValueError` is raised; both builds share
  failures on CSV field names and on XML namespace handling. Test by test (from the two junit files): the 8 tests
  only the export build passes are the 4 acceptance tests (the Markdown build wrote no CSV file when
  run as a script), 3 of `construct_query_url` (no `ValueError` raised) and 1 of `get_args`; no test
  is passed by the Markdown build only; 20 pass in both and 12 fail in both. The specification
  statements behind each were not traced, and Harbor did not keep the builds' code (*to be added to
  the task: save the workspace, as the `lend` task does*). One run per format: this is an
  observation, not a result.
- The agent phase cannot reach the arXiv service (network allow-list), so neither build could try
  its code against the live service; the verifier can. Same for both formats.

**The two contradictions reported in `arxiv-digest`, checked by reading** (PRD lines 19–23, the
sequence diagram, the reference): both are real tensions in the text. Line 21 says console output is
"controlled by --verbose", line 23 says results are printed when neither flag is given, and the
diagram shows `print_results` always called. The reference follows line 23 (`query_arxiv.py` lines
187–191). The hidden tests always pass both flags, so they do not depend on this.

**Cost so far in round 7:** compiles $0.7067 est.; four runs $0.1013 est.

### 9.4 Round 8: the `stocktrends` pair, and a scoring fault found and fixed (2026-10-13)

**Question:** what does the third project show, and can the builds' code be kept?

**Step 1, no model: keep the agent's workspace.** `build_clean_task.py` now writes
`/logs/verifier/agent_files/app.tgz` (everything under `/app` except `spec/`) before the hidden tests
are copied in. Both `stocktrends` tasks rebuilt; against the round 7 tasks only `tests/test.sh`
differs (`diff -r`), and the export files match `round7/stocktrends-export.sha256`. Reference 9 / 9,
do-nothing 0 / 9 (`r8-oracle-stocktrends-export`, `r8-nop-stocktrends-export`).

**Step 2: two Haiku runs, one at a time** (same conditions as §9.3). Both finished. No token in
either job folder (`grep -rl "sk-ant-oat01"`: empty).

**Step 3: the reward files of these two runs were wrong, and why.** They said 8 / 9 (Markdown) and
7 / 9 (export), with 14 and 13 tests collected against 9 hidden tests. Both agents had written their
own tests into `unit_tests/` (5 and 4 tests, all passing). `test.sh` copied the hidden tests into
the same folder, ran the folder, and counted every passing test. Read test by test from the junit
files, both builds pass the same 3 of the 9 hidden tests.

Fix in `build_clean_task.py`: the agent's `unit_tests/` and `acceptance_tests/` folders are removed
before the hidden ones are copied (they stay in `app.tgz`), and pytest runs with
`--confcutdir=<folder>` so a `conftest.py` the agent put at the top level is not loaded. Checked:
reference 9 / 9, do-nothing 0 / 9 (`r8c-…`). Both builds were then rescored from their saved
`app.tgz` in a container built from the task's Dockerfile, with the fixed `test.sh`: 3 / 9 and 3 / 9,
9 collected in each. Still open: an agent's `pytest.ini` or `pyproject.toml` is still read by pytest.

**Are the round 7 numbers affected?** No, by the counts: `arxiv-digest` collected 42 of 42 in both
runs, `lice` 7 (one file that failed to load, plus the 6 acceptance tests). The `hone` pilot
collected 12 of 12. A count above the number of hidden tests is the sign of this fault; none shows it.
The other tasks in `download/clean/` still carry the old `test.sh` and must be rebuilt before reuse.

| Project | Format | Hidden tests passed | As first reported (wrong) | Turns | Agent time | Cost (est.) |
|---|---|---|---|---|---|---|
| stocktrends | Markdown | 3 / 9 | 8 / 9 | 22 | 250.7 s | $0.0522 |
| stocktrends | Export | 3 / 9 | 7 / 9 | 27 | 370.9 s | $0.1150 |

**Reading (from the saved code, the tests, the specification and the reference; n = 1).**
- Both builds pass the 2 acceptance tests and `test_validate_df`, and fail the same 6: five of
  `test_pnf.py` and one of `test_renko.py`.
- At least two of the six ask for things the specification does not state. `test_roundit` calls
  `roundit(7)`: the specification gives `roundit(x: float, base: int)` with no default, the
  reference has `base=5`. `test_get_state` reads `pnf.UPTREND_CONTINUAL`: that name is in neither the
  Markdown nor the export (`grep`: 0). The other four compare row counts of the output with the
  reference's; whether the specification fixes those counts was not traced.
- So on this project the hidden tests partly measure agreement with the reference's unstated
  choices, which no input format can supply.
- The export run cost 2.2 times the Markdown run.

**Hazard seen once:** a reference check hung for 10 minutes in `pip install pandas` inside the
verifier (PyPI answered from the host). Stopped by hand, containers removed, rerun with a 4-minute
limit: passed. No model call was involved.

**Three projects, Haiku, n = 1 per cell (rounds 7 and 8 together):**

| Project | Markdown | Export | Export cost / Markdown cost |
|---|---|---|---|
| lice | 3 / 31 | 3 / 31 | 2.2 |
| arxiv-digest | 22 / 42 | 30 / 42 | 3.9 |
| stocktrends | 3 / 9 | 3 / 9 | 2.2 |

Files: `round8/stocktrends-<format>-haiku-1.{result.json, reward.json, pytest.out, app.tgz}` (rescored)
and `.reward-as-run.json`, `.pytest-as-run.out` (as first produced, kept for the record).
**Cost of round 8:** two runs $0.1672 est.

## 10. Round 9: `arxiv-digest` three times per format, and the hidden tests classified (2026-10-13)

**Questions:** does the 8-test difference of round 7 hold when repeated? How much of a DevEval score
can the specification support at all?

### 10.1 Hidden tests classified by reading (no model call)

Each of the 82 hidden tests of `lice`, `arxiv-digest` and `stocktrends` was read against the four
specification documents and the seed files, and put in one class. This was done **before** the new
runs were scored, by one reader (the assistant), and not checked by a second reader.

| Class | Meaning | lice | arxiv-digest | stocktrends | Total |
|---|---|---|---|---|---|
| S | names and expected behaviour stated in the specification or seed data | 3 | 28 | 2 | 33 |
| U | names stated; the expected value or behaviour is not | 3 | 7 | 5 | 15 |
| R | needs a name, default, key or exact string the specification does not give | 25 | 6 | 2 | 33 |
| C | expects a value that contradicts the specification | 0 | 1 | 0 | 1 |
| | all | 31 | 42 | 9 | 82 |

Files: `test-classification.json` (class and one-line reason per test), `score_by_class.py` (splits a
run's junit results by class; `--check` confirms the ids match the reference run: 31, 42, 9, none
missing, none extra).

**Finds while reading.**
- **`lice`: the unit-test file imports `valid_year`,** which is in neither the Markdown nor the
  export (`grep`: 0). All 25 unit tests are therefore out of reach of any build made from the
  specification, whatever its format. This corrects §9.3, which named only `LICENSES` (the first
  missing name in the error). Read one by one without the import, the 25 would be 6 S, 8 U, 11 R.
- **`arxiv-digest`: one test contradicts the specification.** `test_construct_query_default_max_results`
  expects `max_results=100`; the class diagram and the PRD give 10. The reference has 100 in
  `construct_query_url` and 10 on the command line.
- **`arxiv-digest`: the 4 acceptance tests compare the build with itself.** Each runs the build twice
  and opens the same output file as "reference" and as "test"; they pass when the script runs and
  writes a readable CSV twice alike.
- **`arxiv-digest`: test dictionaries use the key `authors`;** the specification says `author` and
  gives no dictionary keys.

**Limits of the classification.** One reader, who also built the compiler. S against U is a
judgement: two S tests turned out to depend on *where* a stated check lives (§10.3), and one S test
(`test_all_required_arguments_present`) expects `get_args` to accept a command line with no search
field although the specification requires one. The classes were not changed after the results.

### 10.2 Runs (Haiku, one at a time; with the round 7 pair, n = 3 per format)

Tasks rebuilt with the fixed scorer and workspace saving (§9.4): only `tests/test.sh` differs from the
round 7 tasks; the export files match `round7/arxiv-digest-export.sha256`; reference 42 / 42,
do-nothing 0 / 42. Each run collected 42 tests (the check of §9.4). No token in the job folders.

| Run | Format | All 42 | S (28) | U (7) | R (6) | C (1) | Turns | Agent time | Cost (est.) |
|---|---|---|---|---|---|---|---|---|---|
| round 7, 1 | Markdown | 22 | 20 | 2 | 0 | 0 | 6 | 39.3 s | $0.0079 |
| round 9, 2 | Markdown | 27 | 25 | 2 | 0 | 0 | 8 | 104.1 s | $0.0111 |
| round 9, 3 | Markdown | 28 | 25 | 3 | 0 | 0 | 7 | 50.6 s | $0.0100 |
| round 7, 1 | Export | 30 | 27 | 3 | 0 | 0 | 19 | 127.7 s | $0.0312 |
| round 9, 2 | Export | 30 | 27 | 3 | 0 | 0 | 13 | 100.3 s | $0.0237 |
| round 9, 3 | Export | 29 | 27 | 2 | 0 | 0 | 14 | 102.1 s | $0.0237 |

Cost of the four new runs: $0.0685 est.

### 10.3 Reading (from the junit files and the saved code)

- **The 8-test difference of round 7 did not hold; a smaller one did.** Markdown 22, 27, 28;
  export 30, 30, 29. The four acceptance failures and one `get_args` failure of the first Markdown
  run did not repeat.
- **Two tests separate the formats in 3 of 3 runs each:** `test_construct_query_special_characters_in_title`
  and `test_construct_query_non_ascii_characters_in_title`. Every export build checks the allowed
  characters inside `construct_query_url`; every Markdown build with saved code (2 of 3) checks them
  where the command line is validated, so a direct call does not raise. The specification states
  the rule and the `ValueError` but not which function applies it (PRD, Usage). The export carries
  "otherwise, a `ValueError` will be raised" as its own checklist item (N-000028, MUST); whether
  that is why the export builds apply it more widely is a guess, not a finding.
- **Apart from those two tests the formats do not differ** beyond what one format shows between
  its own runs. On S tests: export 27, 27, 27; Markdown 20, 25, 25.
- **No R or C test was passed by any of the 10 DevEval runs** of rounds 7 to 9 (0 of 25, 0 of 6,
  0 of 2, 0 of 1 in every run). The classification was made before these were split, so this is
  some support for it.
- **So the usable ceiling is far below the test count:** 33 of 82 tests are S. On `lice` 3 of 31.

All ten Haiku runs by class (passed / in class):

| Project | Format | Runs | S | U | R + C |
|---|---|---|---|---|---|
| lice | Markdown | 1 | 3 / 3 | 0 / 3 | 0 / 25 |
| lice | Export | 1 | 3 / 3 | 0 / 3 | 0 / 25 |
| arxiv-digest | Markdown | 3 | 20, 25, 25 / 28 | 2, 2, 3 / 7 | 0 / 7 |
| arxiv-digest | Export | 3 | 27, 27, 27 / 28 | 3, 3, 2 / 7 | 0 / 7 |
| stocktrends | Markdown | 1 | 2 / 2 | 1 / 5 | 0 / 2 |
| stocktrends | Export | 1 | 2 / 2 | 1 / 5 | 0 / 2 |

Files: `round9/arxiv-digest-<format>-haiku-<n>.{result.json, reward.json, pytest.out, app.tgz}` and
`.junit/`.

## 11. Round 11: Sonnet on the same three projects, both formats (2026-10-14)

**Question (owner):** run Claude Sonnet 5.5 on `lice`, `arxiv-digest` and `stocktrends` in both
formats exactly as Haiku ran, and compare.

**Conditions.** Identical to the Haiku runs except the model (`anthropic/claude-sonnet-5-5`):
Harbor, Claude Code 2.1.296, tools `Bash`, `Edit`, `Read`, `Write`, agent network limited to the
model API and PyPI, same tasks, one run per format, one run at a time. The `lice` tasks were first
rebuilt with the fixed scorer and workspace saving (only `tests/test.sh` differs from round 7;
export unchanged by hash; reference 31 / 31, do-nothing 0 / 31). Every run collected no more tests
than the hidden set. No token in the job folders.

| Project | Format | All tests | Stated (S) | Names only (U) | Not in spec or against it (R + C) | Turns | Agent time | Cost, est. |
|---|---|---|---|---|---|---|---|---|
| lice | Markdown | 6 / 31 | 3 / 3 | 3 / 3 | 0 / 25 | 4 | 36.8 s | $0.1039 |
| lice | Export | 6 / 31 | 3 / 3 | 3 / 3 | 0 / 25 | 7 | 44.8 s | $0.1347 |
| arxiv-digest | Markdown | 29 / 42 | 25 / 28 | 4 / 7 | 0 / 7 | 4 | 23.7 s | $0.0692 |
| arxiv-digest | Export | 30 / 42 | 27 / 28 | 3 / 7 | 0 / 7 | 8 | 31.7 s | $0.1288 |
| stocktrends | Markdown | 4 / 9 | 2 / 2 | 2 / 5 | 0 / 2 | 9 | 103.1 s | $0.2167 |
| stocktrends | Export | 3 / 9 | 2 / 2 | 1 / 5 | 0 / 2 | 10 | 107.0 s | $0.2778 |

Total for the six runs: $0.9311 est. Classes from `test-classification.json` (fixed in round 9).

**Reading (from junit files and saved code; n = 1 per cell).**
- **Same picture as Haiku: no R or C test passed,** in either format, on any project. All six
  builds kept `max_results = 10` (F1 of the investigation note). Both `lice` builds define
  `LICENSES` and fail on the next missing name, `valid_year` (`ImportError`), as the investigation
  predicted.
- **`lice`:** identical results. Sonnet passes all 3 U acceptance tests that Haiku failed (it made
  BSD3 the default licence), so 6 / 31 against Haiku's 3 / 31.
- **`arxiv-digest`:** export 30, Markdown 29. The two tests only the export passed are acceptance
  tests (`category`, `title`) where the Markdown build wrote no CSV file at scoring time; the same
  build, rerun from the host against the live arXiv service at 2026-10-14 ~04:20 UTC, wrote the CSV
  for both queries. So that difference is most likely the live service at the moment of scoring, not
  the build. The test only the Markdown build passed is `test_directory_created` (U). **The
  character-rule difference seen in all six Haiku runs does not appear:** the Sonnet Markdown build
  checks the allowed characters inside `construct_query_url` and passes both tests.
- **`stocktrends`:** Markdown 4, export 3. The one difference is `test_validate_df` (U): the export
  build also requires a `date` column (the specification asks for OHLC columns only); the test frame
  has none.
- **Cost:** the export run cost 1.30 (`lice`), 1.86 (`arxiv-digest`) and 1.28 (`stocktrends`) times
  the Markdown run; Sonnet runs cost 2.4 to 7.2 times the Haiku runs of the same task
  (against the mean of Haiku's three runs on `arxiv-digest`).

Files: `round11/<project>-<format>-sonnet-1.{result.json, reward.json, pytest.out, app.tgz}` and
`.junit/`.

## 6. Revisit guide

### 6.1 What is in this folder

| Path | Tracked by git | What |
|---|---|---|
| `TRIAL.md` | yes | This record |
| `spec_stats.py` | yes | Our script: words per specification document and files removed, per project |
| `readtime-oracle.result.json` | yes | Harbor's result for the reference run with `TEST_DIR` set |
| `build_clean_task.py` | yes | Our script: one DevEval project as a clean Harbor task, in Markdown or export format (§7) |
| `pilot-hone-markdown-sonnet-1.result.json`, `pilot-hone-export-sonnet-1.result.json` | yes | Harbor's results for the two pilot runs. Checked: no token inside |
| `PROJECTS.md` | yes | All 22 DevEval projects (21 in Harbor): language, domain, size, tests, spec words, usable here; how to pick one (2026-10-14) |
| `evidence/` | yes | Saved 2026-10-14: the compile stores and exports the agents read, the clean tasks (without reference), and every model run's Harbor job with the agent transcript. Index: `evidence/README.md` |
| `download/deveval/` | **no** | The 63 Harbor tasks |
| `download/clean/` | **no** | The two generated clean tasks (they hold the hidden tests and the reference) |
| `~/sddc-runs/deveval-hone/` | outside the repository | The compile store (`.sdd/`), the four documents, the export |
| `download/jobs/` | **no** | `oracle-readtime`, `nop-readtime` (failed), `oracle-readtime-testdir`, `nop-readtime-testdir` |

### 6.2 Repeat

```bash
cd harness/benchmarks/devbench-2024
export HARBOR_TELEMETRY=0 H=../../platforms/harbor/download/.venv/bin/harbor
$H download deveval@1.0 -o download
python3 -I spec_stats.py download/deveval
cd download
$H run -p deveval/python-readtime-implementation -a oracle --ve TEST_DIR=/tests -o jobs --job-name oracle-readtime-testdir
$H run -p deveval/python-readtime-implementation -a nop    --ve TEST_DIR=/tests -o jobs --job-name nop-readtime-testdir
docker build -q -t deveval-probe deveval/python-readtime-implementation/environment
docker run --rm deveval-probe bash -c 'id -un; ls /deveval_source_repo/readtime /app/readtime /app/unit_tests'
docker rmi -f deveval-probe
```

### 6.3 Questions left open

| Question | How to answer it |
|---|---|
| How were the PRD and design documents written (by hand, from the code, by a model)? | The paper's benchmark-construction section |
| Does the original benchmark's implementation task also keep existing files and tests visible? | Clone `open-compass/DevEval`; read its implementation runner |
| Do the C++, Java and JavaScript tasks run here? | The `oracle` agent on one task of each language |
| Do the three formats differ on it at all? | Repackage one project cleanly, compile its four documents, one pilot run per format (model calls; needs approval) |
| Exact licence terms for redistributing a repackaged task | The licence files in the original repository |
| Does the model already know these projects? | Ask for the reference file from the project name alone, without the specification (model call) |
