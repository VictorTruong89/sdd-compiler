# Trial record — Doc2Feat-Bench (earlier NoCode-bench)

> **Kind:** benchmark with its own evaluator · **State:** TRIED 2026-10-12, no model call ·
> **Verdict:** none yet — the owner decides at milestone 2.
> **Recommendation: reject as the main benchmark.** Its evaluator is the best-working one tried so
> far, but what a task gives the agent is a small documentation diff (median 132 words, one file), and
> the task is to edit a large existing codebase. There is nothing for a spec compiler to consolidate (§5).
> Milestone 1 of `sdd/design/rel-02/rel02_brainstorm.md`. This file is the record for the final
> report: what was tried, what happened, and why the candidate was chosen or rejected.
> Rules: no number that was not printed by a command here; no claim about the paper that was not read
> on the page; failures are written down, not removed.

## 0. What we knew before the trial (not verified by us)

From the survey §2 (abstract page only, 2026-09-29): 634 tasks over 10 projects; each task pairs a
documentation change with its implementation and developer tests; scored by task success against
those tests. Licence, runner and whether tasks can be swapped: **unchecked**. Note: its tasks add a
feature to an existing codebase, while our study so far builds from an empty directory.

## 1. Source

| | |
|---|---|
| Paper | Jiang, Deng, Cao, Pradel, Liu, *Doc2Feat-Bench: Evaluating Documentation-Driven Feature Addition*, arXiv:2507.18130 (v1 24 Jul 2025, v4 3 Aug 2026). Abstract page and the HTML of v4 were read on 2026-10-12 **through a summarising fetch**, not word for word — re-read the PDF before quoting it in the report. The repository README says "Accepted by ASE 2026" (not checked against the venue) |
| Earlier name | NoCode-bench. Seen in the repository itself: the Docker Hub namespace is `nocodebench/nocode-bench`. The arXiv v4 page no longer uses that name |
| Code / data URL | `https://github.com/Doc2Feat-bench/Doc2Feat-bench` (named in the paper's data-availability section). Data: Hugging Face `Doc2Feat-bench/Doc2Feat-bench_Full` and `…_Verified`. Leaderboard `doc2featbench.org` and Zenodo `10.5281/zenodo.21762257`: **not opened** |
| Version or commit tried | Repository commit `145e2603652521a2ca3ee9f484f2274dcacda2f3` (1 Aug 2026). Datasets as served on 2026-10-12 (revision not recorded) |
| Licence (read where) | Code: MIT — `LICENSE` in the repository, heading read. **Dataset licence: not read.** The tasks are taken from ten open-source projects with their own licences |
| Download size | Repository 2.7 MB; both datasets exported to JSON lines 50 MB; virtualenv 374 MB; Hugging Face cache 98 MB; one project image (`requests`) 3.75 GB on disk. The other nine images were not pulled |
| Downloaded to | `download/` in this folder (ignored by git) |

## 2. The five questions

| # | Question | Answer | Evidence (command or file) |
|---|---|---|---|
| 1 | What does one task's specification look like (form, length, files)? | **A unified diff of the project's documentation** (field `problem_statement`), mostly `.rst`. Verified subset (114 tasks): **median 132 words, 30 lines, 11 added lines, 1 documentation file**; 70 of 114 tasks touch one file, the most is 7. Full set (634): median 124 words, 29 lines, 8 added lines, 1 file; 5 tasks have no documentation file at all. Each task also carries `augmentations`: a list of suggested names for new entities. The codebase at `base_commit` is the rest of the input | `spec_stats.py` on `download/data/*.jsonl`; §3 |
| 2 | Can that specification be replaced by our three formats (flat, tiered, graph)? | **Not in a meaningful way.** The input is one small diff; compiling it would give a graph of a handful of nodes. The only large body of prose is the project's **whole** documentation (measured for one project, `requests`: 15 `.rst` files, 11 932 words), but that describes code which is already there, and giving the agent a graph of it would change what the benchmark measures | §3; `docker run … fb_requests:dev` |
| 3 | Can it score a project that Claude Code built **outside** its own pipeline? | **Yes, cleanly.** The evaluator takes a JSON-lines file of `{model_name_or_path, instance_id, model_patch}` and does not care what produced the patch. But the answer must be a **patch against the project at a fixed commit**, not a new project | `README.md` "Evaluation"; `evaluation/eval.py` |
| 4 | What does it need to run (OS, Docker, browser, a model for judging, a paid key)? | Linux, Docker, Python; **no model and no key for judging**. One prebuilt image per project from Docker Hub. It ran here on Python 3.13 **without** `tree-sitter-languages` (no wheel for 3.13; used only by the construction scripts) | §3; §4 |
| 5 | Which of our metrics does it give (tests passed, omission, hallucination, time, cost, tokens)? | **Tests passed only**, in five forms: Success %, Applied %, RT % (regression tests), FV-Micro and FV-Macro (the new feature's tests). No omission, no invention, no time, no cost. The paper's "#Token" comes from its own agent runs, not from the evaluator | Evaluator output, §3 |

## 3. The one number

**Shape of the input** (no model; `python3 -I spec_stats.py download/data/verified.jsonl download/data/full.jsonl`):

| | Verified (114) | Full (634) |
|---|---|---|
| Input diff, words: min / median / mean / max | 32 / 132 / 365.68 / 7 425 | 0 / 124 / 302.19 / 7 429 |
| Input diff, lines: median / max | 30 / 1 280 | 29 / 1 288 |
| Added documentation lines: min / median / max | 1 / 11 / 753 | 0 / 8 / 753 |
| Documentation files in the input: median / max | 1 / 7 | 1 / 92 |
| Reference code patch, words: median | 581 | 705.5 |
| Files in the reference code patch: median / max | 3 / 20 | 3 / 97 |
| Tests the feature must turn green (FAIL2PASS): median / max | 2 / 2 824 | 4 / 5 166 |
| Tests that must stay green (PASS2PASS): median / max | 46.5 / 2 587 | 63.5 / 3 505 |
| Largest project share | astropy 19, xarray 17, sphinx 17, matplotlib 16, scikit-learn 16 | scikit-learn 234, astropy 164, xarray 87 |

The paper reports an average input length of 739.06 (Full) and 820.65 (Verified); the unit was not
visible to us. Our means are 302.19 and 365.68 **words**, so the paper's unit is probably tokens
(*our guess, not checked*).

**The evaluator on its own reference answer** (no model). One task, `psf__requests-5856` (133-word
input, 1 new-feature test, 274 regression tests):

```
Applied%: 100.00% (1 / 1)   Success%: 100.00% (1 / 1)   Regression Test (RT%): 100.00% (1 / 1)
FV-Micro: 1.0000 (1 / 1)    FV-Macro: 1.0000
```

36 s wall time, after a 91 s image pull. Report saved as `gold-requests.report.json`. It worked on
the first attempt with no change to their code. *Not done:* a wrong or empty patch as a negative
control; any of the other nine projects; a full run of the 114.

## 4. Log

| Date | What was done | Result |
|---|---|---|
| 2026-10-12 | Opened the arXiv abstract page and the HTML of v4 (summarising fetch) | Title, authors, version dates, repository URL, metric names, "one base Docker image per project" |
| 2026-10-12 | `git clone --depth 1` of the repository; read `README.md`, `requirements.txt`, `evaluation/eval.sh`, `environment/pull_from_hub.sh`, the argument list of `evaluation/eval.py` | 2.7 MB, MIT. Ten projects: astropy, django, matplotlib, pylint, pytest, requests, scikit-learn, seaborn, sphinx, xarray |
| 2026-10-12 | Virtualenv; `pip install datasets`; loaded both datasets and exported them to `download/data/` | 114 and 634 rows; 13 fields |
| 2026-10-12 | `spec_stats.py` on both files; printed one median-sized task (`django__django-15248`) | §3. The median task adds one argument to two signals: 12 added lines in a reference page and a 3-line release note |
| 2026-10-12 | `pip install -r requirements.txt` | **Failed:** no `tree-sitter-languages==1.10.2` for Python 3.13. Installed the other packages by name; the evaluator does not import it |
| 2026-10-12 | `docker pull nocodebench/nocode-bench:requests`, tagged `fb_requests:dev` | 91 s, 3.75 GB |
| 2026-10-12 | `evaluation/eval.py --gold` on the one `requests` task | Success 1 / 1 in 36 s. Python printed `SyntaxWarning` lines from their `constants.py`; harmless |
| 2026-10-12 | Counted the `requests` project's own documentation inside the image | 15 `.rst` files, 11 932 words |

No model was called. Nothing here was sent anywhere except the downloads.

## 5. Verdict

**Chosen / rejected / kept as backup:** *the owner decides at milestone 2.* Recommendation:
**reject as the main benchmark.**

**Reasons:**

1. *The specification is too small to compile.* The agent's input is a documentation diff with a
   median of 132 words in one file. Our question is whether the **arrangement** of a large, messy set
   of specifications changes what the agent builds; a 30-line diff has no arrangement to vary.
2. *The hard part is the codebase, not the specification.* Each task edits a large existing project
   (scikit-learn, astropy, django …). The paper itself names "understanding existing modules" and
   cross-file edits as the main failure causes (abstract, summarised). A graph of the specification
   does not help with that; a graph of the code would, and that is a different tool.
3. *It is a different task from the proposal's.* The proposal builds a project from specifications in
   an empty directory. Here the output is a patch on top of somebody else's repository.
4. *It gives only tests-passed.* Omission and invention would still be ours to define, and a patch to
   a large project has no clean meaning of "invented feature".

**What speaks for it (and should be said in the report):** the evaluator ran on the first attempt, on
Linux, with no model and no key; it scores a patch from any source; prebuilt images; MIT code; 634
real tasks with developer-written tests; a human-checked subset of 114. As engineering it is far
ahead of ProjectEval.

**What we lose by rejecting it:** a published, real-world benchmark with a working evaluator and a
leaderboard to compare against; and the only candidate so far whose input is genuine project
documentation rather than text written for a benchmark.

**A use that would fit, if the owner wants it later** (*an idea, not tried*): a side experiment in
which the agent gets the project's whole documentation as flat files or as a compiled graph, plus the
diff. That tests the compiler on real documentation, but it is a second study, each project image is
several gigabytes, and compiling ten projects' documentation costs model calls not estimated here.

## 6. Revisit guide

### 6.1 What is in this folder

| Path | Tracked by git | What |
|---|---|---|
| `TRIAL.md` | yes | This record |
| `spec_stats.py` | yes | Our script: size and shape of the input, no model |
| `gold-requests.report.json` | yes | The evaluator's report for the one reference run |
| `eval-venv.freeze.txt` | yes | `pip freeze` of the virtualenv (46 lines, Python 3.13.9) |
| `download/Doc2Feat-bench/` | **no** | The repository at commit `145e260…` |
| `download/data/` | **no** | `verified.jsonl`, `full.jsonl`, `one-requests.jsonl` |
| `download/.venv/`, `download/hf-cache/`, `download/eval-logs/` | **no** | Virtualenv, Hugging Face cache, evaluator logs |

Docker image: `nocodebench/nocode-bench:requests` = `fb_requests:dev`, 3.75 GB, was pulled for the
run. It was no longer listed by `docker images` later the same day (not removed by us on purpose;
cause not investigated — possibly a later Harbor run's clean-up). Pull it again to repeat (§6.2).

### 6.2 Rebuild and repeat

```bash
cd harness/benchmarks/doc2feat-bench/download
git clone https://github.com/Doc2Feat-bench/Doc2Feat-bench && git -C Doc2Feat-bench checkout 145e2603652521a2ca3ee9f484f2274dcacda2f3
python3 -m venv .venv
.venv/bin/pip install datasets docker==7.1.0 unidiff tqdm lxml packaging requests openai
mkdir -p data
HF_HUB_DISABLE_TELEMETRY=1 HF_HOME=$PWD/hf-cache .venv/bin/python -I -c "
from datasets import load_dataset
for n in ('Verified','Full'):
    load_dataset(f'Doc2Feat-bench/Doc2Feat-bench_{n}', split='test').to_json(f'data/{n.lower()}.jsonl')"
python3 -I ../spec_stats.py data/verified.jsonl data/full.jsonl

# the evaluator on one reference patch
grep 'psf__requests-5856' data/verified.jsonl > data/one-requests.jsonl   # one line; the export writes "psf\/requests"
docker pull nocodebench/nocode-bench:requests && docker tag nocodebench/nocode-bench:requests fb_requests:dev
cd Doc2Feat-bench
PYTHONPATH=$PWD HF_HOME=$PWD/../hf-cache ../.venv/bin/python evaluation/eval.py --gold \
    --log_dir ../eval-logs/gold-requests --bench_tasks ../data/one-requests.jsonl \
    --max_workers 1 --image_level repo --timeout 600 --output_file ../eval-logs/gold-requests.txt
```

### 6.3 Questions left open

| Question | How to answer it |
|---|---|
| What is the dataset's licence? | The dataset card on Hugging Face |
| What unit is the paper's 739.06 / 820.65? | Read §3 of the PDF |
| Does the evaluator fail a wrong patch? | Run it with an empty and with a broken `model_patch` |
| How large is each project's own documentation? | The count in §4, repeated in the other nine images |
| How large are all ten images together? | `docker pull` each; expect tens of gigabytes (*not measured*) |
