# Trial record — RepoGenesis

> **Kind:** benchmark with its own evaluator · **State:** TRIED 2026-10-12, no model call ·
> **Verdict:** none yet — the owner decides at milestone 2.
> **Recommendation: reject.** The specification is one README per task (median 634.5 words), and the
> scoring is unsafe: on the one task run, **an empty folder passed every test**, and another task's
> tests import module names its README never gives (§3).
> Milestone 1 of `sdd/design/rel-02/rel02_brainstorm.md`. This file is the record for the final
> report: what was tried, what happened, and why the candidate was chosen or rejected.
> Rules: no number that was not printed by a command here; no claim about the paper that was not read
> on the page; failures are written down, not removed.

## 0. What we knew before the trial (not verified by us)

From the survey §1.3 and §2 (abstract page only, 2026-09-29): README → a whole microservice
repository; 106 repositories; reports Pass@1, API coverage and deployment success. Web services only.
Not in the proposal's candidate lists; added by the owner 2026-10-12 (rel02 Q7).

## 1. Source

| | |
|---|---|
| Paper | Peng, Yin, Zhao, Yang, Wang, Jia, Chen, Lin, Rajmohan, Zhang, *RepoGenesis: Benchmarking End-to-End Microservice Generation from Readme to Repository*, arXiv:2601.13943 (v3). First 100 000 characters of the HTML read through a summarising fetch; the appendices were not read |
| Code / data URL | `https://github.com/microsoft/DKI_LLM/tree/main/RepoGenesis` (named in the paper) |
| Version or commit tried | `microsoft/DKI_LLM` commit `c090b7d57e3996c8900e86fecd16085b27e07f29` (20 May 2026), folder `RepoGenesis` only (sparse checkout) |
| Licence (read where) | MIT — `LICENSE` at the root of `DKI_LLM`, heading read. No separate licence in the `RepoGenesis` folder |
| Download size | 5.6 MB for the folder |
| Downloaded to | `download/DKI_LLM/` in this folder (ignored by git) |

## 2. The five questions

| # | Question | Answer | Evidence (command or file) |
|---|---|---|---|
| 1 | What does one task's specification look like (form, length, files)? | **One `README.md` per task**: a description, the port, and each API endpoint with input, output and status codes. Over the 30 tasks in the repository: **median 634.5 words** (min 231, mean 636.0, max 1 460). Java tasks add a `pom.xml`. One file, one kind of document | `wc -w` over `repo/*/README.md`, §4 |
| 2 | Can that specification be replaced by our three formats? | Hardly. A single API contract of about 600 words has little to arrange; the three formats would be near-identical | §3 |
| 3 | Can it score a project that Claude Code built **outside** its own pipeline? | **Yes**: the evaluator takes a folder with one sub-folder per generated repository. But see the scoring problems in §3 | `eval_harness/run_evaluation.py --help` |
| 4 | What does it need to run? | Python and Docker; no model for the Docker evaluator. (Their generation scripts need an OpenAI-style key; not used.) **The evaluator's default folders do not exist in the repository** — it runs zero tests unless `--golden_test_dir_python repo --readme_dir_python repo` is given | §4 |
| 5 | Which of our metrics does it give? | Pass@1 (all tests pass), deployment success, **API coverage** (share of the README's endpoints found in the code — the nearest thing to an omission measure among all candidates). No invention, time or cost | Evaluator output |

**The tests are public:** they sit beside each README in the repository. There is **no reference
implementation**, so no "reference solution" run is possible.

## 3. The one number

Smallest task, `flask` (231-word README, three endpoints), evaluated in Docker, no model:

| Submission | Deployed | Tests passed | API coverage | Pass@1 |
|---|---|---|---|---|
| A 30-line service written by hand in this session (not a study run) | yes | 7 / 7 | 3 / 3 | 1.0 |
| **A folder holding only a text note** | **no** | **7 / 7** | 0 / 3 | **1.0** |

Reports: `flask-hand.report.json`, `flask-empty.report.json`. About 20 s each.

**Why the empty folder passes:** the task's test file builds its own small Flask application inside
the test (`create_minimal_app`) and tests that, not the submission. By a search of the test files this
is the only task of the 30 that does so.

**A second problem, seen in one other task by reading (not run):** the `Blog` tests import
`app.main`, `app.core.database`, `app.core.auth.create_user_access_token`,
`app.core.security.get_password_hash` — internal module and function names. A search of `Blog`'s
README for those names found none. A correct service with a different internal layout would fail.
Whether other tasks do the same was not checked.

## 4. Log

| Date | What was done | Result |
|---|---|---|
| 2026-10-12 | arXiv HTML (first part), summarising fetch | Repository URL; 106 repositories (60 Python, 46 Java), 30 of them the verified evaluation set; agents evaluated do not include Claude Code |
| 2026-10-12 | Sparse clone of `microsoft/DKI_LLM`, folder `RepoGenesis`; read its README | 30 task folders in `repo/`, each a README and tests |
| 2026-10-12 | `wc -w` on every task README | §2 row 1 |
| 2026-10-12 | Virtualenv, `pip install -r eval_harness/requirements.txt` (one package) | — |
| 2026-10-12 | Evaluator on the hand-written `flask` service and on an empty folder, default options | Both: **0 tests found**; deployment 1 and 0. Cause: the default test folder `repo_readme_verified` is not in the repository |
| 2026-10-12 | The same two with `--golden_test_dir_python repo --readme_dir_python repo` | §3 |
| 2026-10-12 | Searched the test files for tests that build their own app, and for imports of internal modules | `flask` only; `Blog` imports internals |

No model was called. The hand-written service was typed by the assistant from the README; it is a
check of the evaluator, not a measurement of anything.

## 5. Verdict

**Chosen / rejected / kept as backup:** *the owner decides at milestone 2.* Recommendation: **reject.**

**Reasons:**
1. *One document per task, about 600 words.* Nothing for the compiler to consolidate.
2. *Scoring cannot be trusted as shipped:* Pass@1 = 1.0 for an empty folder on one task; tests tied to
   unstated internal names on another; default paths that silently run no tests.
3. *Web microservices only,* in Python and Java, which narrows what the study could claim.
4. *Tests are public and there is no reference implementation.*

**What speaks for it:** real build-from-nothing tasks; MIT; a Docker evaluator that takes any folder;
and **API coverage**, a ready-made idea for our omission metric (count the specified endpoints that
exist in the code). Worth citing for that idea even if rejected.

**What we lose by rejecting it:** a from-scratch public benchmark with a leaderboard; nothing we could
not rebuild.

## 6. Revisit guide

Tracked here: `TRIAL.md`, `flask-hand.report.json`, `flask-empty.report.json`. Ignored:
`download/DKI_LLM/`, `download/.venv/`, `download/preds-hand/`, `download/preds-empty/`,
`download/eval-*`.

```bash
cd harness/benchmarks/repogenesis/download
git clone --depth 1 --filter=blob:none --sparse https://github.com/microsoft/DKI_LLM
git -C DKI_LLM sparse-checkout set RepoGenesis
python3 -m venv .venv && .venv/bin/pip install rich
mkdir -p preds-empty/flask && echo note > preds-empty/flask/NOTE.txt
cd DKI_LLM/RepoGenesis
../../.venv/bin/python -m eval_harness.run_evaluation --predictions_dir ../../preds-empty \
    --output_dir ../../eval-empty2 --repo_names flask --golden_test_dir_python repo --readme_dir_python repo
```

Open: do the other 28 tasks' tests depend on internal names; do the Java tasks run here; where are the
other 76 repositories of the paper's 106.
