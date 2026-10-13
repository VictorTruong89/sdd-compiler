# Trial record — ProjectEval

> **Kind:** benchmark with its own runner and judge · **State:** TRIED 2026-10-12 ·
> **Verdict:** none yet — the owner decides at milestone 2. **Recommendation: not the main benchmark**
> (§5).
> Milestone 1 of `sdd/design/rel-02/rel02_brainstorm.md`. This file is the record for the final
> report: what was tried, what happened, and why the candidate was chosen or rejected.
> Rules: no number that was not printed by a command here; no claim about the paper that was not read
> on the page; failures are written down, not removed.

## 0. What we knew before the trial (not verified by us)

From `docs/MIA5150-Project/metrics-and-platforms-survey.md` §2 and §8 (paper PDF and README read 2026-09-29):
three input levels (natural-language prompt, checklist, code skeleton); judged by simulated user
interaction (needs a browser driver) plus code similarity; README licence GPL-3.0; Windows or Linux;
an LLM runtime is involved (Ollama suggested); judging runs on a named experiment folder
(`run_judge.py -r`), which *suggests* outside outputs could be scored — **not confirmed**.

## 1. Source

| | |
|---|---|
| Paper | Liu et al., arXiv:2503.07010. The repository URL is in the abstract's footnote of the arXiv HTML version (read 2026-10-12). The README says ACL 2025 Findings and gives `https://aclanthology.org/2025.findings-acl.1036/` (*that page not opened by us*) |
| Code / data URL | `https://github.com/RyanLoil/ProjectEval` |
| Version or commit tried | `34f838c3da58e816b63d1a6f2ab7956d62a19e09` (2026-07-03, message "ProjectEvalPlus"), shallow clone |
| Licence (read where) | GPL-3.0 — the `LICENSE` file in the checkout (first lines read) and the README badge |
| Download size | 116 MB working tree including 26 MB `.git` (`du -sh`); of it one data file of 49 MB (`data/material/19-Deathlist-Standard 1.csv`). The judge's virtualenv added 953 MB |
| Downloaded to | `download/ProjectEval/` in this folder (ignored by git) |

A successor, **ProjectEvalPlus**, is announced in the README (`https://github.com/RyanLoil/ProjectEvalPlus`,
accepted by ACM TOSEM per the README). *Not opened, not tried.*

## 2. The five questions

| # | Question | Answer | Evidence (command or file) |
|---|---|---|---|
| 1 | What does one task's specification look like (form, length, files)? | One JSON record per project in a single file, 20 projects: 16 websites (Django), 3 console programs, 1 batch program. Three alternative inputs per project: `nl_prompt` (one or a few sentences: 4 to 327 words, median 14), `nl_checklist` (a JSON list of pages and functions: 44 to 449 words, median 179.5; 219 functions in all), `skeleton` (the canonical code with bodies removed, 1 to 27 files). There is no multi-file specification, no rules file, no cross-references | `data/project_eval_project.json`, counted with a short Python script (whitespace-separated words of the JSON text) |
| 2 | Can that specification be replaced by our three formats (flat, tiered, graph)? | **Technically yes, usefully no.** Nothing stops us from handing the agent other text. But the source is too small to render: a median 180-word checklist has nothing to tier and little to link, and our hypothesis is about messy, multi-file specifications. Its three levels differ in *how much* is told (sentence → checklist → code skeleton), not in how the same content is arranged, so they are not our variable. To use it we would have to write our own longer specifications for its 20 projects | Same file; judgement, not a measurement |
| 3 | Can it score a project that Claude Code built **outside** its own pipeline? | **Yes for the mechanism, not yet shown end to end.** The judge reads an answer JSON (`{project_id: [{file, path, code}]}`); `tools/file_transform.py` turns a folder into that. It also needs, per project, **parameter values** (the element ids, URLs and inputs each test should use, answered about the agent's own code) and a start file. With those supplied the judge calls no model: shown by running it on the canonical answer with a model class that raises if called. Not shown: a project actually built by Claude Code (that needs a model run). Cost of this route: the agent must also answer the parameter questions, which shows it what will be tested | `run_judge.py`, `controller.py` lines 264–560 (read); `judge_canonical.py` in this folder (run) |
| 4 | What does it need to run (OS, Docker, browser, a model for judging, a paid key)? | Python ≥ 3.12 (nested f-string quotes in `run_judge.py`), Chrome or Firefox or Edge with Selenium, port 8000 free. **No model and no key for judging** when parameters and start files are given. It runs the generated code **directly on the host**: `pip install` and `python` from the `PATH`, no sandbox (a Docker route exists; Docker is not installed on this machine, so not tried). On Linux it did not work as downloaded — see §4, five defects | §4 |
| 5 | Which of our metrics does it give (tests passed, omission, hallucination, time, cost, tokens)? | **Tests passed only**: 264 test functions plus 1 point per project for "runs" = 284. Each test belongs to a named checklist function, so a per-requirement pass table could be built from its log (not built). "Objective indicators" (similarity to the canonical code) exist in `run_indicators.py`; they need torch and sentence-transformers and were *not tried*. No omission count, no hallucination count, no time, cost or tokens | `controller.py` scoring loop; `config.py` (`PROJECT_EVAL_DEFAULT_TEST_CASE = 284`) |

## 3. The one number

**ProjectEval's own judge, run on ProjectEval's own canonical answer, on this machine: 202 of 284
(0.711).** Wall time 2 min 22 s for the 20 projects. No model call.

- Command: `cd download/ProjectEval && . .venv/bin/activate && python ../../judge_canonical.py`
- Result kept in `canonical-run.result.json`; full log in `download/canonical-run.log` (not in git).
- Conditions: Ubuntu, Python 3.12 virtualenv, Chrome 155.0.8059.39 headless, Selenium 4.51.0,
  Django 5.1.15; the judge **patched** as in `linux-trial.patch` (two changes) and `config.ini` given
  one missing key.
- Per project (points / possible, possible = tests + 1): eight projects below 80 % — 7 (6/24), 13 (8/25),
  17 (2/6), 8 (9/18), 11 (4/8), 20 (18/26), 5 (10/13), 12 (14/18) — and project 19 scored 0 because the judge itself
  raised (`BasePythonManager.__init__() got an unexpected keyword argument 'start_file'`).

**What this number means:** the reference solution does not reach 100 % under the reference judge
here. Whether the cause is our Linux setup, our two patches, timing (the judge allows 3 s per page),
newer library versions, or the benchmark itself is **not established**: we did not investigate the 74
failures one by one, and we did not read what score the authors report for the canonical answer. Until
that is known, a score from this judge on this machine has an unknown ceiling.

## 4. Log

| Date | What was done | Result |
|---|---|---|
| 2026-10-12 | arXiv abstract page fetched for a repository link | None on the abstract page |
| 2026-10-12 | Web search for the repository | No URL found; `gh` is not installed |
| 2026-10-12 | arXiv HTML full text fetched (summarising fetch) | URL found in the abstract's footnote |
| 2026-10-12 | `git clone --depth 1` into `download/` | Commit `34f838c`, 116 MB |
| 2026-10-12 | Read `README.md`, `LICENSE` (head), `config.ini`, `requirements.txt`, `run_judge.py`, parts of `controller.py`, `openjudge.py`, `llm.py`, `tools/file_transform.py`, `docker/Dockerfile` | Answers 1–5 above |
| 2026-10-12 | Counted the data file | 20 projects; 264 tests; word counts in §2 |
| 2026-10-12 | Python 3.12 virtualenv; installed the judge's dependencies from `requirements.txt` except torch, sentence-transformers, codebleu, scipy | OK |
| 2026-10-12 | `import config` | **Defect 1:** `KeyError: 'DEEPSEEK_KEY'` — `config.py` reads a key that `config.ini` does not have. Added `DEEPSEEK_KEY = unused` to the downloaded `config.ini` |
| 2026-10-12 | Judge on canonical project 1 | **Defect 2:** `No module named 'sympy'`, then `No module named 'sklearn'` — imported by `llm.py` and `openjudge.py`, absent from `requirements.txt`. Installed both |
| 2026-10-12 | Judge on canonical project 1 | **Defect 3:** `ERR_CONNECTION_REFUSED` — the judge opens the home page straight after starting the Django server, without waiting. **Defect 4:** `module 'signal' has no attribute 'CTRL_BREAK_EVENT'` — stopping a project uses a Windows-only signal, so on Linux the stop fails and **the server is left running** (two `manage.py runserver` processes found and killed by hand) |
| 2026-10-12 | Patched `openjudge.py` in the download: wait up to 20 s for port 8000; terminate the process on non-Windows. Saved as `linux-trial.patch` (47 lines) | Canonical project 1: 11 / 11 in 8 s; no process left behind |
| 2026-10-12 | Judge on all 20 canonical projects | 202 / 284 (0.711), 2 min 22 s. **Defect 5:** project 19 (batch) cannot be judged: the judge raises on `start_file` |

Not done: the Docker route; `run_indicators.py`; any run of a model; judging a project built by Claude
Code; reading the paper beyond the footnote that holds the URL; opening ProjectEvalPlus.

## 5. Verdict

**Chosen / rejected / kept as backup:** *the owner decides at milestone 2.* Recommendation: **reject as
the main benchmark; keep as a possible source of ready-made tests** if we ever write our own
specifications for its projects.

**Reason:**

1. *The specifications are too small for our question.* A sentence or a 180-word checklist cannot be
   meaningfully rendered as flat, tiered and graph, and carries none of the mess (duplicates, scattered
   refinements, contradictions) our hypothesis is about.
2. *Its levels are a different variable.* They change how much the agent is told, not how the same
   requirements are arranged.
3. *The judge is not trustworthy here as downloaded.* Five defects on Linux, and its own reference
   solution scores 0.711 after our patches, cause unknown.
4. *It gives one of our four metric groups* (tests passed), and nothing on omission, hallucination or
   efficiency.

**In its favour:** it downloads and runs; the judge needs no model and no key; it can score an answer
made elsewhere; every test is tied to a named requirement; 20 whole projects with tests already written.

**What we lose by this choice:** a published benchmark whose input levels reviewers may see as close to
our format variable, and its leaderboard for outside comparison.

**Licence note:** GPL-3.0. Using it to score is unrestricted. `linux-trial.patch` in this folder is a
modification of GPL-3.0 code; if the repository is published with it, GPL-3.0 applies to that file.

## 6. Revisit guide — how to repeat or continue this trial

Written 2026-10-12 so that a later session can pick this up without the conversation it came from.

### 6.1 What is in this folder

| File | Tracked in git? | What |
|---|---|---|
| `TRIAL.md` | yes | This record |
| `spec_stats.py` | yes | Counts projects, words per input level, checklist functions, tests (the numbers in §2 row 1) |
| `judge_canonical.py` | yes | Runs ProjectEval's judge on its canonical answer with a stand-in model class that raises if called |
| `linux-trial.patch` | yes | Our changes to the checkout: one line in `config.ini`, two edits in `openjudge.py`. GPL-3.0 applies to it |
| `canonical-run.result.json` | yes | The judge's result for the 20 canonical projects (the one number) |
| `judge-venv.freeze.txt` | yes | `pip freeze` of the virtualenv the judge ran in (80 packages, Python 3.12.3) |
| `download/ProjectEval/` | **no** | The checkout at commit `34f838c`, with our patch applied, its `.venv/` (953 MB), `test/` (the projects the judge wrote out) and `log/` |
| `download/canonical-run.log` | **no** | Full console log of the 20-project run (2 423 lines) |

If `download/` is gone, everything below rebuilds it.

### 6.2 Rebuild from nothing

```bash
cd harness/benchmarks/projecteval
mkdir -p download && cd download
git clone https://github.com/RyanLoil/ProjectEval.git
cd ProjectEval
git checkout 34f838c3da58e816b63d1a6f2ab7956d62a19e09
git apply ../../linux-trial.patch            # defects 1, 3, 4

/usr/bin/python3.12 -m venv .venv            # 3.12 or newer: run_judge.py uses nested f-string quotes
. .venv/bin/activate                         # REQUIRED: the judge calls bare `python` and `pip` from PATH
pip install "Levenshtein~=0.26.1" "scikit-image~=0.24.0" "opencv-python~=4.10.0.84" \
    "selenium>=4.0.0" "func-timeout>=4.3.5" ollama openai google-genai \
    "Django~=5.1.1" "Markdown~=3.7" "matplotlib~=3.9.2" "pyperclip~=1.9.0" \
    "qrcode~=7.4.2" "openpyxl~=3.1.5" "pandas~=2.2.3"
pip install sympy scikit-learn               # defect 2: imported, not in requirements.txt
# (exact versions that were installed: ../../judge-venv.freeze.txt)
```

Left out on purpose: `torch`, `sentence-transformers`, `scipy`, `codebleu`, `tree-sitter-python`. Only
`run_indicators.py` (similarity to the canonical code) needs them.

Needs on the machine: Google Chrome (155.0.8059.39 was used; Selenium fetched the matching driver by
itself), port 8000 free, network for `pip`.

### 6.3 Run

```bash
# from download/ProjectEval, with the virtualenv active
python3 -I ../../spec_stats.py data/project_eval_project.json     # spec sizes; no venv needed
python ../../judge_canonical.py 1                                  # one project, about 8 s
python ../../judge_canonical.py > ../canonical-run.log 2>&1        # all 20, about 2 min 22 s
grep -E "scored|Finished|^RESULT" ../canonical-run.log
```

After any run, check that nothing was left behind, and kill it if so:

```bash
ps -eo pid,cmd | grep -E "manage\.py runserver|chromedriver" | grep -v grep
pkill -f "manage.py runserver"; pkill -f chromedriver
```

### 6.4 How the judge works (read from the code, commit `34f838c`)

- **Inputs.** `data/project_eval_project.json` (the 20 projects with their tests), an **answer** JSON
  `{project_id: [{"file", "path", "code"}, …]}`, a **parameter** JSON with the value of every test
  parameter, and for console and batch projects a **start file** per project.
- **Per project** (`controller.py`, `JudgeController.evaluate`): delete and rewrite `test/<date>/<id>/`
  from the answer JSON → `pip install` the project's requirements → for a website, run
  `manage.py makemigrations`, `migrate`, create the superuser `Admin` / `abc#12345`, start
  `manage.py runserver` on port 8000, open the home page in headless Chrome → run each test function
  with its parameter values → stop the server.
- **Score.** Per project `(passed + 1) / (tests + 1)`; the `+ 1` is a point for "the project runs".
  Overall `pass@1 = total passed points / 284`, and 284 = 264 tests + 20 projects
  (`config.py: PROJECT_EVAL_DEFAULT_TEST_CASE`). A project that fails to start gets 0, not 1.
- **When it calls a model.** Only to fill a gap: start commands and requirements for a website
  (`get_information`), the start file of a console or batch project (`get_start_file`), or parameter
  values (`get_parameters`) when the parameter file lacks that project. Supply all three and no model
  is used — that is what `judge_canonical.py` does.
- **Limits read from `config.ini`:** page-load and test timeout 3 s (`TIMEOUT_LIMIT`), string
  similarity threshold 0.65, image similarity threshold 0.2.
- **Naming rule for `run_judge.py`:** results must sit at
  `experiments/<folder>/<model>/<cascade|direct>/<model>_<timestamp>_level_<n>.json` with sibling
  `…_parameter.json` and optionally `…_startfile.json`. `experiments/example/` shows it.
  `run_judge.py` picks the model class from the folder name, so a folder not starting with `gpt`,
  `gemini` or `deepseek` is treated as an Ollama model.
- **"cascade" vs "direct"** (from the file names and README, not verified in the paper): in cascade the
  model first writes the next level itself (prompt → its own checklist → its own skeleton → code); in
  direct it goes from the given level straight to code.

### 6.5 To score a project built by Claude Code (not done — the next step if this is reopened)

1. Give the agent one project's `nl_prompt` or `nl_checklist` (or our own specification for it) and let
   it build the Django or console project in a folder.
2. `python tools/file_transform.py` on that folder → the answer JSON (function `get_files` skips
   `migrations/`, `*.sqlite3`, `*.log`). *Its command-line form was not read.*
3. Produce the parameter JSON. Either ask the agent to answer the parameter descriptions about its own
   code (they are in each test's `"parameter"` list, e.g. "the id of the introduction element"), or
   write them by hand. Shape: `experiments/example/gpt-4o/cascade/*_parameter.json`.
4. Produce the start-file JSON (`{"1": "myproject/manage.py", …}`).
5. Run a copy of `judge_canonical.py` with `answer_path`, `parameter_file_path` and `start_files`
   pointing at those three files.

Open design problem with step 3: the parameter descriptions tell the agent what is tested. In the
authors' pipeline the model answers them *after* writing the code; ours would have to do the same, as a
second, separate prompt.

### 6.6 Questions left open

| Question | Why it matters | How to answer it |
|---|---|---|
| Why does the canonical answer score 0.711 here, not 1.0? | Without it the judge's ceiling on this machine is unknown | Read `download/ProjectEval/log/<date>/*-Judge.log` for the 74 failures. Seen so far, uninvestigated: 25 × "Testcase failed", 17 × empty assertion error, three console failures on input files (`'Gamedata.xlsx' does not …`, "Feature matrix or target vector is empty", "Dataset contains missing or invalid value") — which suggests the data files in `data/material/` are not copied to where the console programs look. Then try a longer `TIMEOUT_LIMIT`, and the Docker route |
| What score do the authors report for the canonical answer? | To know whether 0.711 is our setup or the benchmark | Read the paper's results section (not read) |
| Does the Docker route work? | It is the authors' supported Linux path and it isolates generated code | Install Docker; `cd docker && sh build.sh && sh compose.sh`. Note the Dockerfile sets `docker=1` in lower case while the code tests `DOCKER` — check which path it really takes |
| Is defect 5 (project 19, `start_file`) ours or theirs? | One of 20 projects is unjudgeable | Checked in the code: theirs. Project 19's stack is `Matplotlib`, which `BatchJudge.BATCH_MANAGER` maps to `MatplotlibManager`; that class has no `start_file` parameter, while `controller.py` always passes one for console and batch projects. A fix would be a third patch (not made). Compare with ProjectEvalPlus |
| Is ProjectEvalPlus different in what matters to us (spec size, Linux support)? | It is the maintained successor | Open `https://github.com/RyanLoil/ProjectEvalPlus`; run `spec_stats.py` on its data first |
| Do the "objective indicators" add a metric we want? | Possible extra code-quality measure | Install the left-out packages; `python run_indicators.py -r '["example"]'` |

### 6.7 Things that were tried and did not work, in order

1. Looking for the repository on the arXiv **abstract** page: no link there. A web search also returned
   no URL. The link is only in the footnote of the full text (`https://arxiv.org/html/2503.07010`).
2. `gh search repos`: the GitHub CLI is not installed on this machine.
3. Running the judge as downloaded on Linux: stopped by defects 1 to 4 in turn (§4).
4. Running the judge unpatched leaves Django servers running: two had to be killed by hand.
