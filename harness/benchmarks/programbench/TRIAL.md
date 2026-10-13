# Trial record — ProgramBench

> **Kind:** benchmark with its own evaluator · **State:** TRIED 2026-10-12 in part, no model call —
> the data and one task image were inspected; **its evaluator was not run** ·
> **Verdict:** none yet — the owner decides at milestone 2.
> **Recommendation: reject.** The agent's real specification is a runnable copy of the program; the
> written documentation is a README and a manual page. Arranging that text differently is not what the
> benchmark tests. It is also heavy: one task image is 4.19 GB.
> Milestone 1 of `sdd/design/rel-02/rel02_brainstorm.md`. This file is the record for the final
> report: what was tried, what happened, and why the candidate was chosen or rejected.
> Rules: no number that was not printed by a command here; no claim about the paper that was not read
> on the page; failures are written down, not removed.

## 0. What we knew before the trial (not verified by us)

From the survey §2 (abstract page only, 2026-09-29): given a program's documentation, rebuild it to
match a reference executable; 200 tasks; scored by agent-fuzzed behavioural tests. Added by the owner
2026-10-12 (rel02 Q7).

## 1. Source

| | |
|---|---|
| Paper | Yang, Lieret, Ma, Thakkar, Pedchenko, Sootla, McMilin, Yin, Hou, Synnaeve, Yang, Press, *ProgramBench: Can Language Models Rebuild Programs From Scratch?*, arXiv:2605.03546 (v1, 5 May 2026). Abstract page only, through a summarising fetch |
| Code / data URL | `https://github.com/facebookresearch/ProgramBench` (found by web search, confirmed by cloning: its README cites the paper). Tests on Hugging Face `programbench/ProgramBench-Tests`; task images on Docker Hub under `programbench/`. Website `programbench.com`: not opened |
| Version or commit tried | Repository commit `27f02157c785f8da3647aa6dbbe6b9137f99f10e` (28 Sep 2026); image `programbench/abishekvashok_1776_cmatrix.5c082c6:task_cleanroom_v6` |
| Licence (read where) | MIT — `LICENSE` in the repository, heading read. Each rebuilt program has its own licence |
| Download size | Repository 43 MB (39 MB of it task definitions); **one task image 4.19 GB**, pulled in 88 s. The evaluation images and test archives were not pulled |
| Downloaded to | `download/ProgramBench/` (ignored by git). The image was removed after inspection |

## 2. The five questions

| # | Question | Answer | Evidence (command or file) |
|---|---|---|---|
| 1 | What does one task's specification look like (form, length, files)? | **The program's own documentation plus a compiled executable the agent may run.** For the one task inspected (`cmatrix`): `README.md` 472 words, manual page `cmatrix.1` 340 words, a licence file, two images, and `./executable` (execute-only). No source. **Only one task of 201 was inspected** | `docker run --network none … find/wc`, §4 |
| 2 | Can that specification be replaced by our three formats? | **Not usefully.** The behaviour the tests check comes from probing the executable, not from the text; a README and a manual page are two short documents with nothing to consolidate | §3 |
| 3 | Can it score a project that Claude Code built **outside** its own pipeline? | Yes by its guide: the submission is a `submission.tar.gz` of the codebase per task, from any agent. The guide requires that the agent has **no internet** during the run. *Not run* | `docs/README.md` |
| 4 | What does it need to run? | Linux x86-64, Docker, Python; a multi-gigabyte image per task for the agent and another for evaluation; test archives fetched from Hugging Face. No model for judging | `docs/README.md` |
| 5 | Which of our metrics does it give? | Tests passed, per test, per task. Nothing on omission, invention, time or cost | `docs/README.md` (output format) |

## 3. The one number

**The evaluator was not run**, so there is no score. Measured instead, from the repository's task
definitions (no model): **201 task folders** (the paper says 200); languages Rust 107, Go 46, C 33,
C++ 12, and one each of Bash, Java, Haskell; difficulty labels medium 120, easy 28, hard 18 (35
unlabelled); behavioural tests per task (not ignored): min 3, **median 974**, max 20 530.

## 4. Log

| Date | What was done | Result |
|---|---|---|
| 2026-10-12 | arXiv abstract page (summarising fetch); web search for the repository | Title, authors; `facebookresearch/ProgramBench` |
| 2026-10-12 | `git clone --depth 1`; read `README.md` and `docs/README.md` | Submission format, image naming, no-internet rule |
| 2026-10-12 | Counted `task.yaml` and `tests.json` over `src/programbench/data/tasks/` | §3 |
| 2026-10-12 | `docker pull` of the `cmatrix` agent image; listed `/workspace` with the network off | §2 row 1. User `agent`; the executable is mode `--x--x--x` |
| 2026-10-12 | `docker rmi` of that image | Removed |

Not done: `programbench eval` on any submission (needs a second image and the test archive); any
other task; the website and leaderboard.

## 5. Verdict

**Chosen / rejected / kept as backup:** *the owner decides at milestone 2.* Recommendation: **reject.**

**Reasons:**
1. *The specification is behaviour, not documents.* The agent learns what to build by running the
   reference program. Our variable is how written specifications are arranged; here the writing is a
   minor input.
2. *Mostly Rust, Go and C programs,* some very large (the paper names FFmpeg, SQLite and PHP). The
   paper's abstract says no model fully solves any task; a study that needs differences between three
   formats cannot use a benchmark where every arm scores near the floor.
3. *Cost in disk and time:* about 4 GB per task image, 201 tasks.

**What speaks for it:** the most carefully isolated set-up seen (no source, execute-only binary,
no network), thousands of behavioural tests per task, MIT, recent.

**What we lose by rejecting it:** nothing our question needs.

## 6. Revisit guide

Tracked here: `TRIAL.md` only. Ignored: `download/ProgramBench/`.

```bash
cd harness/benchmarks/programbench/download
git clone --depth 1 https://github.com/facebookresearch/ProgramBench
docker pull programbench/abishekvashok_1776_cmatrix.5c082c6:task_cleanroom_v6
docker run --rm --network none --entrypoint bash programbench/abishekvashok_1776_cmatrix.5c082c6:task_cleanroom_v6 \
    -c 'ls -la; wc -w README.md cmatrix.1'
```
