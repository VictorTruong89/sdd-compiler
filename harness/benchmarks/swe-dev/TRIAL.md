# Trial record — SWE-Dev (feature-driven development benchmark)

> **Kind:** benchmark + own inference and evaluation scripts · **State:** TRIED 2026-10-12, no model
> call — paper read, repository and test split downloaded, input measured, its test step run on two
> samples · **Verdict:** none yet — the owner decides at milestone 2.
> **Recommendation: reject as the main benchmark.** The task fills in removed functions inside a large
> existing package, from one document that is mostly per-function docstrings written with GPT-4o. It
> is the same shape as Doc2Feat-Bench, which was rejected for that reason, and it is not a well-known
> benchmark by any indicator measured (§5a).
> Added by the owner on 2026-10-12 (rel02 D12) as the ninth candidate.
> Rules: no number that was not printed by a command here; no claim about the paper that was not read
> on the page; failures are written down, not removed.

## 0. What we knew before the trial (not verified by us)

Only the link the owner gave: `https://openreview.net/forum?id=vokqMIUEaz`.

**That page could not be opened.** OpenReview answered both the page and its API with a browser
challenge (`ChallengeRequiredError`, 403). The paper was identified by its title through a search and
read on arXiv instead. **Whether the OpenReview forum `vokqMIUEaz` is this paper, and which venue it
belongs to, is not verified.** The owner should open the link and confirm the title and venue.

**Two different papers are called SWE-Dev.** Do not mix them up:

| | This trial | The other one |
|---|---|---|
| Title | *SWE-Dev: Evaluating and Training Autonomous Feature-Driven Software Development* | *SWE-Dev: Building Software Engineering Agents with Training and Inference Scaling* |
| arXiv | 2505.16975 | 2506.07636 |
| What it is | A benchmark and training set | An agent, scored on SWE-bench Verified |
| Repository | `DorothyDUUU/SWE-Dev` | `THUDM/SWE-Dev` |

The first was assumed, because the owner asked for a benchmark candidate.

## 1. Source

| | |
|---|---|
| Paper | Du, Cai, Zhou, Wang, Qian, Pang, Liu, Hu, Chen. arXiv:2505.16975v2, read as HTML on 2026-10-12 through a summarising fetch (both halves of the page) |
| Venue | The NeurIPS 2025 site lists it as "Poster in Workshop: Deep Learning for Code in the Agentic Era" (`neurips.cc/virtual/2025/131677`, opened). Semantic Scholar gives the venue as arXiv. The README's citation is the arXiv preprint. **Not shown to be a main-conference paper** |
| Code | `github.com/DorothyDUUU/SWE-Dev`, commit `839148bf404838534c55d9a3e15ae86d01c4aeb1` (2025-10-24, the last push) |
| Data | Hugging Face dataset `Dorothydu/SWE-Dev`, revision `5b24a7f909b2aaa64e61c2123e359e008f6978ee`; test split only (500 files, 63 MB) |
| Test environments | Docker Hub `dorothyduuu/swe-dev:<package>-image`. 41 packages in the test list, all 41 tags exist, 10.16 GB compressed in total (Docker Hub API). The README says the training images need "at least 100GB" |
| Licence (read where) | **Apache-2.0 by statement only.** The README and the dataset card say Apache-2.0; the repository has **no `LICENSE` file** and GitHub reports no licence. The source packages keep their own licences |
| Downloaded to | `download/` in this folder (ignored by git), 128 MB, plus three Docker images |

## 2. The five questions

| # | Question | Answer | Evidence |
|---|---|---|---|
| 1 | What does one task's specification look like? | **One text field, `PRD`, per sample.** It holds a folder tree, a one-paragraph module description, then for every function to write: its name, signature and docstring. The paper says GPT-4o wrote the module description from the test file and refined the docstrings. Median 875 words (easy) and 1 109.5 words (hard). Beside it the model is shown the source files with those functions removed: median 2 files and 1 609.5 words (easy), 3 files and 2 703 words (hard) | `spec_stats.py`; one PRD read in full (`advertools-test_ad_create`); paper |
| 2 | Can that specification be replaced by our three formats? | **Technically yes, usefully no.** It is one clean document whose content is a list of docstrings. There is nothing scattered, duplicated or contradictory to consolidate, and no second file. Not compiled: that needs model calls | Judgement from row 1, not a measurement |
| 3 | Can it score code that Claude Code wrote outside its pipeline? | **Yes for the mechanism.** The test step writes the changed files into the package's container and runs one test file with pytest. Its own inference script is a single prompt to an OpenAI-style endpoint that must return whole files; it has no Claude Code route and no agent loop of the kind we study. To run Claude Code we would repackage each sample as a Harbor task, with a clean image: **the released image contains the reference source and the tests** | `infer/single/single_evaluation_passk.py`, `single_agent_infer.py` (read); `judge_one.py` (run); image inspected |
| 4 | What does it need to run? | Docker and about 10 GB of images for the test split; Python ≥ 3.12 for the evaluator (nested quotes in an f-string). No model and no key for scoring. **One defect found in three images:** `advertools-image` lacks the `pytest-json-report` plugin the evaluator calls, so the evaluator reports 0 passed for the reference and for anything else, without an error | §3 |
| 5 | Which of our metrics does it give? | **Tests passed only** (Pass@1, Pass@3; the denominator is what the reference passes). No omission count, no invention count, no time, cost or tokens | Evaluator code |

Other things seen:

- `infer/single/run.sh` in the public repository contains a **hard-coded API key and server address**.
  Not used, not copied here.
- The test split covers 39 packages (easy) and 34 (hard) in 250 + 250 samples; the reference changes
  a median of 2 and 3 files.
- The hidden tests are small: median 175 and 209.5 words of test code per sample.
- The paper's own figures disagree with each other in places (for example Claude 3.7 Sonnet on the
  hard split: 22.45 % in the abstract, 24.25 % in a table, as reported by the fetch). Not checked
  against the PDF.
- Claude Code was not among the systems the paper evaluated.

## 3. The one number

**SWE-Dev's own test step, unchanged, on sample `idna-test_idna_codec-level2`: reference 9 of 9,
untouched task files 0 of 9 (1 collection error).** No model call. `judge-idna.report.json`.

| Sample | Image as shipped | Reference written in | Untouched (masked) files | Note |
|---|---|---|---|---|
| `idna-test_idna_codec-level2` (1 297-word PRD, 2 files) | 9 passed | 9 passed | 0 passed, 1 error | Evaluator unchanged |
| `advertools-test_ad_create-level1` (the first sample) | 0 | 0 | 0 | **Evaluator fails silently:** pytest rejects `--json-report` in this image (`judge-advertools-ad_create.report.json`) |
| the same, run by hand with plain `pytest -q` | 4 passed | 4 passed | import error | Shows the task itself is sound; with `pip install pytest-json-report` at run time the evaluator's command also gives 4 passed |

**What this means:** the scoring works and separates a correct answer from no answer, when the image
is intact. One of three images tried was not. Before any use, every one of the 41 images would need
the same check.

## 4. Log

| Date | What was done | Result |
|---|---|---|
| 2026-10-12 | Fetched the owner's OpenReview link; then its API by forum and by note id | Browser challenge, 403, both times |
| 2026-10-12 | Web search for the title | arXiv:2505.16975, repository `DorothyDUUU/SWE-Dev`; a second, unrelated SWE-Dev paper found |
| 2026-10-12 | Read arXiv HTML v2, both halves | Task, sizes, evaluation, limits ("currently focuses on Python"); no dataset licence named in the licensing appendix |
| 2026-10-12 | Cloned the repository; read README, download scripts, inference and evaluation scripts | 21 MB; no `LICENSE` file; hard-coded key in `run.sh` |
| 2026-10-12 | Read the dataset's metadata on Hugging Face; downloaded the test split at a pinned revision | 500 files, 63 MB |
| 2026-10-12 | `spec_stats.py` | Figures in §2 row 1 |
| 2026-10-12 | Pulled `advertools-image` (65 s; 1.47 GB on disk); `judge_one.py` on the first sample | 0 / 0 / 0. Cause found by running pytest by hand: plugin missing |
| 2026-10-12 | Same sample by hand, plain pytest; then with the plugin installed at run time | 4 / 4 / import error; 4 passed |
| 2026-10-12 | Pulled `idna-image` and `typish-image` (about 720 MB each); `pip list` | Plugin present in both |
| 2026-10-12 | `judge_one.py` on an `idna` sample | 9 / 9 / 0 |
| 2026-10-12 | Popularity indicators read from GitHub, Semantic Scholar, Hugging Face, Docker Hub | §5a |

## 5. Verdict

**Chosen / rejected / kept as backup:** *the owner decides at milestone 2.* Recommendation: **reject as
the main benchmark.**

| Question the owner asked | Answer |
|---|---|
| Feasible? | **Yes, with work.** It downloads and its scoring ran here. Costs: about 10 GB of images, a check of all 41, and a clean repackaging per sample for Harbor |
| Capable? | **One metric.** Tests passed; nothing on omissions, inventions or cost |
| Suitable? | **No.** See the reasons |

**Reasons:**

1. *Wrong task shape.* The agent fills in removed functions inside an existing package. Most of the
   outcome depends on reading the surrounding code, not on how the specification is arranged. This is
   the reason Doc2Feat-Bench was rejected.
2. *The specification is one clean document of docstrings.* Median about 900–1 100 words, one file,
   one docstring per function to write. Our three formats would differ little on it, and the
   product's claim is about messy, multi-file specifications.
3. *The requirement text is machine-written.* GPT-4o produced the module description from the test
   file and refined the docstrings. A study about specification quality should say so if it uses them.
4. *It is not better known than what we already have* (§5a), so it does not add credibility.
5. *Smaller points:* no licence file; one silent evaluator failure in three images; the paper's venue
   is a workshop by the one listing opened.

**In its favour:** large (500 test samples, 14 000 for training); real packages with tests written by
their developers; every test maps to named functions; the scoring is simple and needs no model.

**What we lose by this choice:** a large ready-made task set. DevEval, already tried, gives whole
projects from four documents and fits the question better.

**To reopen:** if the study is ever widened to "add a feature to an existing codebase". First step:
check all 41 images, then repackage one sample cleanly and run the reference and do-nothing agents.

## 5a. Is it well known? (indicators read 2026-10-12)

Every figure is from the named service's public API on that day. None is a quality measure.

| | SWE-Dev (this) | DevEval | ProgramBench | ProjectEval | SWE-bench (for scale) |
|---|---|---|---|---|---|
| Citations (Semantic Scholar) | 12 | 49 | 51 | 31 | 4 283 |
| Venue (Semantic Scholar) | arXiv; workshop poster per the NeurIPS site | COLING 2024 | arXiv 2026 | ACL 2025 | ICLR |
| GitHub stars | 62 | 139 | 952 | 29 | 6 013 |
| Last push to the repository | 2025-10-24 | 2024-05-30 | 2026-10-12 | 2026-07-03 | 2026-09-18 |

Also for SWE-Dev: Hugging Face dataset 950 downloads and 1 like; Docker Hub 81 401 pulls in total.
The README says Kimi-K2 used the benchmark (a link to a post; not opened). It is **not** in Harbor's
registry (`../../platforms/harbor/registry-datasets.txt`).

Platforms, for the owner's question "is SWE-Dev more popular than Harbor": Harbor's repository
(`harbor-framework/harbor`) has 6 049 stars and 1 990 forks, pushed today; its PyPI package had
4 778 308 downloads in the last month (pypistats; includes automated installs). Inspect AI: 2 990
stars, 2 896 739 downloads. A benchmark and a platform are different kinds of thing, but on every
shared indicator Harbor is far ahead of SWE-Dev.

## 6. Revisit guide

Tracked here: `TRIAL.md`, `spec_stats.py`, `judge_one.py`, `judge-idna.report.json`,
`judge-advertools-ad_create.report.json`, `eval-venv.freeze.txt`. Ignored: `download/`.

```bash
cd harness/benchmarks/swe-dev
mkdir -p download && cd download
git clone https://github.com/DorothyDUUU/SWE-Dev repo && git -C repo checkout 839148bf404838534c55d9a3e15ae86d01c4aeb1
python3 -m venv .venv && .venv/bin/pip install huggingface_hub
mkdir data && HF_HUB_DISABLE_TELEMETRY=1 .venv/bin/python -I -c "
from huggingface_hub import snapshot_download
snapshot_download(repo_id='Dorothydu/SWE-Dev', repo_type='dataset',
    revision='5b24a7f909b2aaa64e61c2123e359e008f6978ee', local_dir='data',
    allow_patterns=['dataset/test/*', 'README.md'])"
cd ..
python3 -I spec_stats.py download/data/dataset/test
docker pull dorothyduuu/swe-dev:idna-image
python3 judge_one.py download/data/dataset/test/easy/idna-test_idna_codec-level2-metadata.json
```

Do not run `infer/single/run.sh`: it carries someone else's API key and server address.
Images left on this machine: `advertools-image` (1.47 GB), `idna-image`, `typish-image` (about 720 MB
each); remove with `docker rmi` when no longer needed.
