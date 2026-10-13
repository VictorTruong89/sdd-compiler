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

## 6. Revisit guide

### 6.1 What is in this folder

| Path | Tracked by git | What |
|---|---|---|
| `TRIAL.md` | yes | This record |
| `spec_stats.py` | yes | Our script: words per specification document and files removed, per project |
| `readtime-oracle.result.json` | yes | Harbor's result for the reference run with `TEST_DIR` set |
| `build_clean_task.py` | yes | Our script: one DevEval project as a clean Harbor task, in Markdown or export format (§7) |
| `pilot-hone-markdown-sonnet-1.result.json`, `pilot-hone-export-sonnet-1.result.json` | yes | Harbor's results for the two pilot runs. Checked: no token inside |
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
