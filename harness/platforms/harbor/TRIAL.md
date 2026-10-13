# Trial record — Harbor

> **Kind:** platform only (no tasks of its own) · **State:** TRIED 2026-10-12, in three sessions — the
> no-model checks and **one model run (Claude Code on the subscription, Sonnet) are done** ·
> **Verdict:** none yet — the owner decides at milestone 2.
> **Recommendation: Harbor fits as a platform; adopt it.** The subscription run it was waiting for
> succeeded (§3, §5). Three things are still to settle before the main runs (§5).
> Milestone 1 of `sdd/design/rel-02/rel02_brainstorm.md`. This file is the record for the final
> report: what was tried, what happened, and why the candidate was chosen or rejected.
> Rules: no number that was not printed by a command here; no claim about the documentation that was not
> read on the page or in the installed code; failures are written down, not removed.

## 0. What we knew before the trial (not verified by us)

From `docs/MIA5150-Project/metrics-and-platforms-survey.md` §3 and §8 (docs pages read 2026-09-29): a
task is `instruction.md`, `task.toml`, `environment/`, `tests/test.sh`; a verifier writes `reward.txt` or
a `reward.json` with several labelled metrics; each trial records duration, cost, tokens and retries;
`claude-code` is listed among its pre-integrated agents. **Not confirmed:** whether its Claude Code agent
works on the subscription login (this project never uses an API key), and which token and cost fields it
really writes.

## 1. Source

| | |
|---|---|
| Paper | None. Documentation: `https://docs.harborframework.com` (index, quick start and "run a job" pages fetched 2026-10-12 through a summarising fetch) |
| Code / data URL | PyPI package `harbor`. Repository: `github.com/laude-institute/harbor` — found on 2026-10-12 in the installed code (`constants.py`: `DEFAULT_REGISTRY_URL` points at that repository's `registry.json`) and its `adapters/deveval` page was opened. The commit for 0.24.0 is still not identified |
| Version or commit tried | `harbor` 0.24.0 from PyPI (the newest of the versions `pip index versions harbor` listed on 2026-10-12) |
| Licence (read where) | Apache-2.0 — `License-Expression: Apache-2.0` in the installed `METADATA`, and the `LICENSE` file in the wheel (201 lines, Apache License 2.0 heading read) |
| Download size | 378 MB for the virtualenv with Harbor and its 91 packages (`du -sh .venv`) |
| Downloaded to | `download/.venv/` in this folder (ignored by git) |
| Container runtime | Docker Engine 29.9.0, installed by the owner on 2026-10-12 after the first session was blocked |

Everything below marked "code" was read in the installed package,
`download/.venv/lib/python3.12/site-packages/harbor/`.

## 2. The five questions

| # | Question | Answer | Evidence (command or file) |
|---|---|---|---|
| 1 | How is one of OUR tasks packaged as a Harbor task? | **Done for `lend-messy` (Markdown format), by a script.** A Harbor task is a folder: `instruction.md` (the task text), `task.toml` (timeouts, network mode, environment variables), `environment/Dockerfile` (the machine the agent works in), `tests/test.sh` (+ test files; it writes the reward), `solution/solve.sh` (a reference solution). Ours maps as: `task.md` with its spec line → `instruction.md`; `spec/` → copied into the image at `/app/spec` by a three-line Dockerfile on `python:3.12-slim`; `hidden_tests/` → `tests/`; `reference/` → `solution/reference/`, installed by `solve.sh`. Because the specification is inside the image, **each spec format is its own task variant** (three per task). The conversion took one 92-line script and no change to the task | `build_lend_task.py`; runs in §3 |
| 2 | Does its `claude-code` agent run on the subscription login, without an API key? | **Yes according to the code; still not run** (it needs a model call and a token: owner's approval). The agent passes `CLAUDE_CODE_OAUTH_TOKEN` into the sandbox. By default an `ANTHROPIC_API_KEY`, if present, wins; setting `CLAUDE_FORCE_OAUTH=1` drops the key and uses the token, and raises if the token is missing ("Run `claude setup-token` to get one"). So it needs a long-lived token made by `claude setup-token`; it does **not** reuse the interactive login in `~/.claude`. Claude Code itself is installed **inside the container** (`npm install -g @anthropic-ai/claude-code` or the bootstrap script), so the container needs network and that install adds time to every trial (*not measured*) | code: `agents/installed/claude_code.py`, `_should_force_oauth`, `_resolve_auth_env` (lines 1770–1850), install commands near lines 483 and 566 |
| 3 | What does it record that `harness/run_task.py` does not, and the reverse? | **Harbor has, we do not:** timing split by phase (seen in a run: environment setup, agent setup, agent execution, verifier); per-model token usage; a standard trajectory format (ATIF) and a web viewer (`harbor view`); attempts per task (`-k`), retries (`-r`) and parallel trials (`-n`); a no-model reference agent (`-a oracle`) and a do-nothing agent (`-a nop`) to prove a task is passable and that its tests discriminate; a summary table of every named reward. **We have, Harbor does not (as far as read):** a sandbox that needs no container runtime (bubblewrap); the contamination audit of every tool call; the requirement-by-requirement mapping in `score.py`. **Both:** a cost ceiling (`--max-budget-usd` is an option of its Claude Code agent), a tool allow-list, a turn cap, Claude Code's own `total_cost_usd` (Harbor reads it from the `stream-json` result line and falls back to pricing each step with LiteLLM) | code: `models/trial/result.py`, `models/agent/context.py`, `agents/installed/claude_code.py` lines 54–101, 1001–1030, 1625–1636; `lend-oracle.result.json` |
| 4 | What does it need to run (OS, Docker, browser, a model for judging, a paid key)? | Python ≥ 3.12 and **a container runtime or a cloud sandbox account**. Default is Docker; the 31 environment types in the code include Podman, Singularity, Kata, Apple container and cloud or cluster services, but **no "run on this host" type**. With Docker installed it worked at the first try. No model and no key are needed to run or verify a task; only a model-driven agent needs credentials. It pulled the base image, built the task image and removed it afterwards (`docker images` showed only `hello-world` after the runs). **Telemetry:** usage events go to PostHog unless `HARBOR_TELEMETRY` is `0`/`false`/`no`/`off`/`disabled`. **Network:** a task's `network_mode` defaults to `public`; an `allowlist` mode with `allowed_hosts` exists in the code (*not tried*) | code: `models/environment_type.py`, `telemetry.py` lines 40–46 and 479, `models/task/config.py`; the runs in §3 |
| 5 | Which of our metrics does it give (tests passed, omission, hallucination, time, cost, tokens)? | **Time: yes, seen. Cost and tokens: fields exist; they were `None` for the no-model agent, so not yet seen filled. Tests passed and any other number: whatever our `test.sh` writes — seen working with four named rewards** (`reward`, `tests_passed`, `tests_total`, `installable`), each shown as a column in Harbor's summary. Omission and hallucination counts could be reported the same way, but **we** compute them; Harbor stores and aggregates. Files read or edited and failed commands: derivable from the trajectory, not counted | `lend-oracle.result.json`; `download/jobs/*/result.json` |

## 2a. Does Harbor also bring a benchmark? (checked 2026-10-12, no model)

**No benchmark that fits the study. Harbor stays a platform; the tasks must come from us or from a
benchmark we package ourselves.**

- Command: `harbor datasets list --legacy` (the plain command only prints a link to
  `hub.harborframework.com/datasets`; **that website was not opened**, so newer entries may be missing).
- The default registry lists **80 entries, 75 distinct names** (`registry-datasets.txt`).
- **None of our six candidate benchmarks is in it by name** (search for `projecteval`, `realbench`,
  `doc2feat`, `repogenesis`, `programbench`, `devbench`: 0 matches).
- Most entries are bug fixing or issue resolution in an existing repository (SWE-bench family,
  `swe-gen-js`, `vmax-tasks`), terminal tasks (`terminal-bench`), single-function or contest coding
  (`aider-polyglot`, `usaco`, `livecodebench`, `ds-1000`), or not coding at all (`gaia`, `aime`,
  `simpleqa`, `lawbench`). Judged from the one-line descriptions, not from the tasks.
- **One near match: `deveval`** — 63 tasks from 21 repositories; the adapter's page says each
  repository provides "Product Requirements Documents (PRD), UML diagrams, architecture designs, and
  test suites", and that DevEval was "originally named DevBench" (arXiv:2403.08604,
  `github.com/open-compass/DevEval`). Read on the adapter page through a summarising fetch; **the
  paper itself is not opened**. This is very probably our candidate 8, "DevBench (2024)", already
  packaged for Harbor. It is the first thing to try in trial 8: `harbor download deveval`.
- Others that take a feature description as input, for the record: `featurebench` (200
  feature-implementation tasks in 24 Python repositories) and `researchcodebench` (implement an
  algorithm from a paper). Both work inside an existing codebase; neither was opened.

**What this means:** "Harbor alone" cannot run the proposal's experiment. Harbor plus our own tasks
can (shown with `lend`), and Harbor plus DevEval may, if DevEval's specifications turn out large
enough to compile — to be found in trial 8.

## 3. The one number

**Our `lend` task, packaged as a Harbor task and solved by Harbor's no-model `oracle` agent with our
reference implementation: 24 of 24 hidden tests, reward 1.0, 31 s wall time.** The same task with the
do-nothing `nop` agent: 0 of 24, `installable` 0. So the packaged task is passable and its tests
discriminate, as they do under our own harness (24 / 24 on the reference, 24 / 24 failing on a no-op,
`harness/tasks/lend-messy/DESIGN.md`).

| Run | Command | Result |
|---|---|---|
| First session, no Docker | `harbor run -p scaffold/hello -a oracle -o jobs --job-name oracle-no-docker` | Stopped: "Docker is not installed or not on PATH. Please install Docker and try again." |
| Scaffold task | `harbor run -p ../example-task -a oracle -o jobs --job-name oracle-hello` | Reward 1.0, 38 s (includes the first pull of `ubuntu:24.04`). The scaffold's test is an empty `pass`, so this proves only that the machinery runs |
| `lend`, reference | `harbor run -p lend-task -a oracle -o jobs --job-name oracle-lend` | `{"reward": 1.0, "tests_passed": 24, "tests_total": 24, "installable": 1}`, 31 s |
| `lend`, reference, repeated | `… --job-name oracle-lend-2` | Same rewards. Phases: environment setup 2.1 s, agent setup 0.0 s, agent execution 0.2 s, verifier 13.0 s, total 25.9 s (`lend-oracle.result.json`) |
| `lend`, do-nothing | `harbor run -p lend-task -a nop -o jobs --job-name nop-lend-2` | `{"reward": 0, "tests_passed": 0, "tests_total": 24, "installable": 0}` |
| `lend` Markdown, **Claude Code on the subscription** (third session; the first model call) | `env -u ANTHROPIC_API_KEY harbor run -p lend-task -a claude-code -m anthropic/claude-sonnet-5-5 --ak max_budget_usd=10 -o jobs --job-name claude-lend-markdown` | `{"reward": 1.0, "tests_passed": 24, "tests_total": 24, "installable": 1}`, 3 min 5 s, no exception (`lend-claude-sonnet-markdown.result.json`) |

**The model run in detail** (one run, so every figure is n = 1; source: the trial's `result.json` and
the `result` event in `agent/claude-code.txt`, job `claude-lend-markdown`, trial `lend-task__rZvkD7h`):

| What | Value |
|---|---|
| Credential used | Subscription token. Claude Code's start event reports `apiKeySource: "none"`; `ANTHROPIC_API_KEY` was unset |
| Claude Code version / model reported | 2.1.296 / `claude-sonnet-5-5` |
| Tests passed | 24 / 24, package installable |
| Cost, est. API-equivalent (Claude Code's `total_cost_usd`) | $0.1813725. Harbor's `agent_result.cost_usd` holds the same figure |
| Harbor's own per-model figure (`model_usage.….cost_usd`) | $0.152025 — **differs** from the line above; Harbor computes it itself. Use `cost_usd`, not this one. Cause of the gap not investigated |
| Tokens, Claude Code | input 12, cache write 19 565, cache read 118 485, output 9 124 (of which thinking 1 019) |
| Tokens, Harbor | `n_input_tokens` 138 062, `n_cache_tokens` 118 485, `n_output_tokens` 9 124. **Harbor's "input" is the sum** of input, cache write and cache read (12 + 19 565 + 118 485); it is not comparable with our harness's input count without splitting |
| Turns / agent time | 6 turns; 65.8 s (57.99 s in the API) |
| Phases | environment setup 2.4 s, **agent setup 95.2 s** (installing Claude Code in the container), agent execution 66.5 s, verifier 8.4 s |
| Budget option | `--ak max_budget_usd=10` was accepted and recorded in `config.json`. Not tested: that it stops a run that reaches it |
| Tools offered to the agent | Harbor's default: everything, including `WebSearch` and `WebFetch`, permission mode `bypassPermissions`. Web requests made: 0. **We did not restrict the tool list** in this run |
| What the agent inherited from the host | Working directory `/app`, no MCP servers, memory path inside the trial's own log folder. The transcript contains neither `CLAUDE.md` nor `sdd-compiler` (0 matches) |
| Token in the job files | `grep -rl "sk-ant-oat01" jobs/claude-lend-markdown` returned nothing |
| Images left behind | None (`docker images` shows only `hello-world`) |

**What this run does not show.** It is one run of one format on one model. It says nothing about the
export (graph) format, and it is **not** a result of the study. Note for milestone 3: Sonnet reached
24 / 24 from the Markdown specs in 6 turns, so the hidden tests alone may be too easy to separate the
formats on this task; the planted items and audit items A1–A6 are not scored by this `test.sh` yet.

**Hidden tests stay hidden.** The reference solution's script printed what it could see while the agent
phase ran: `ls: cannot access '/tests': No such file or directory`. Harbor uploads `tests/` only for the
verifier phase. (Seen for the `oracle` agent; the same environment is used for any agent, but it was not
re-checked with a model-driven one.)

## 4. Log

| Date | What was done | Result |
|---|---|---|
| 2026-10-12 | Fetched the docs index, quick start and "run a job" pages | Task and command shapes; Docker is the default sandbox, Modal and Daytona named as cloud options. No install command, repository URL, licence or credential handling on those pages |
| 2026-10-12 | `which docker podman uv pipx` | None installed |
| 2026-10-12 | `pip index versions harbor`; `python3.12 -m venv download/.venv`; `pip install harbor` | 0.24.0 installed, 378 MB, 91 packages (`harbor-venv.freeze.txt`) |
| 2026-10-12 | `pip show harbor`; read `METADATA` and `LICENSE` | Apache-2.0; Python ≥ 3.12; no project URL in the metadata |
| 2026-10-12 | Read `agents/installed/claude_code.py` for authentication, install, cost and tokens | Answers 2 and 3 |
| 2026-10-12 | Read `models/environment_type.py`, `models/trial/result.py`, `models/agent/context.py`, `verifier/verifier.py`, `telemetry.py` | Answers 3, 4, 5 |
| 2026-10-12 | `harbor --help`, `harbor run --help`, `harbor init --help` | Command list |
| 2026-10-12 | `harbor init --task trial/hello -o scaffold` | Six files scaffolded (copied to `example-task/`) |
| 2026-10-12 | `harbor run -p scaffold/hello -a oracle …` | **Stopped: Docker is not installed** |
| 2026-10-12 | Owner installed Docker Engine 29.9.0 from Docker's apt repository, added the user to the `docker` group, rebooted | `docker run --rm hello-world` works without `sudo` |
| 2026-10-12 | `harbor run -p ../example-task -a oracle` | Reward 1.0 in 38 s; `result.json` read: timing per phase filled, token and cost fields `None` for this agent |
| 2026-10-12 | Read `models/trial/paths.py`, `agents/oracle.py`, `verifier/verifier.py` | Container paths: `/tests`, `/solution`, `/logs/verifier/reward.json`; a reward file may hold any number of finite numeric values |
| 2026-10-12 | Wrote `build_lend_task.py`; generated `download/lend-task/` | 16 files |
| 2026-10-12 | `harbor run -p lend-task -a oracle` (twice) and `-a nop` | 24 / 24 and 0 / 24; tests not visible in the agent phase |
| 2026-10-12 | `docker images`, `docker system df` after the runs | Only `hello-world` left: Harbor removed the images it built |

**Telemetry incident (kept, not hidden).** The first Harbor command, `harbor --version`, ran **before**
`HARBOR_TELEMETRY=0` was set, because telemetry was only found afterwards while reading the code. Harbor
may have sent one "command finished" event to PostHog for it. Every later command ran with
`HARBOR_TELEMETRY=0`. What such an event contains was not checked beyond the code comment that only
fixed labels are recorded, never environment values.

**A mistake of ours, fixed.** The first version of the generated `test.sh` counted passed tests with a
convoluted expression. It gave the right count (24) but was rewritten as a plain check and the run
repeated (`oracle-lend-2`), with the same result.

Third session (2026-10-12): the owner created a token with `claude setup-token` and saved it in
`~/.config/sdd-compiler/claude-oauth.env` (outside the repository, read by `source`, never printed).
One model run, approved by the owner, under a $10 ceiling; details in §3. Incident: the owner pasted
the token into the chat with the assistant, so it is in that session's transcript on this machine;
the owner was advised to replace it.

Not done: a second model run or another model; a comparison with `harness/run_task.py` on the same
task; a restricted tool list; a run that hits the budget ceiling; the export (graph) format of `lend` (the task is not
compiled yet); `f1-ingest`; the `allowlist` network mode; parallel trials; a cloud sandbox; the viewer;
finding the source repository.

## 5. Verdict

**Chosen / rejected / kept as backup:** *the owner decides at milestone 2.* Recommendation: **Harbor
fits; adopt it as the platform.** The condition set after the second session (one subscription run,
§6.4 step 1) is met: the run succeeded on 2026-10-12 (§3). `harness/` stays as the fallback and as the
cross-check in §6.4 step 3.

**Reasons it fits:**

1. *It runs our task unchanged.* A script turned `lend-messy` into a Harbor task; the reference scored
   24 / 24 and a do-nothing agent 0 / 24, the same as under our own harness.
2. *Hidden tests are hidden by construction*, and the agent works in a container that cannot see this
   repository or the host at all.
3. *It reports several named numbers per trial*, so tests passed, requirements met, omissions and
   inventions can sit side by side in one result file and one summary table.
4. *Time is recorded per phase; cost and token fields exist* and, by the code, are filled from Claude
   Code's own `total_cost_usd`.
5. *It has a no-model reference agent and a do-nothing agent*, which give every task a free sanity
   check before any paid run.
6. *It supports the subscription by design* (a token, no API key) — on paper.
7. Apache-2.0; overhead about 26–31 s per trial on this machine for a small task.

**Answered by the model run (§3):** Claude Code runs on the subscription token inside the container;
cost and tokens are filled, the cost from Claude Code's own `total_cost_usd`; the budget option is
accepted.

**Still to settle before the main runs:**

- *Install time.* 95 s of each trial went to installing Claude Code (n = 1). Over many runs that is
  the largest fixed cost. Whether it can be cached (in the task's Dockerfile, or a Harbor option) is
  not checked.
- *Tool list.* Harbor's default gives the agent every tool, web included. **Partly settled
  2026-10-12:** `--ak disable_web_search=true` was used in the two DevEval pilot runs and the start
  event listed no `WebSearch` or `WebFetch` tool. The container still has open network through the
  shell (`pip`, `curl`); `allowed_tools` and the `allowlist` network mode remain untried.
- *Same numbers as our harness?* Not compared yet (§6.4 step 3). Harbor's "input tokens" already
  differ in definition (§3).
- *The token's version of Claude Code.* Harbor installs the current release each time (2.1.296 here);
  a study should pin it. The agent has a version option in the code (`self._version`); not tried.

**What adopting it costs:**

- A long-lived subscription token (`claude setup-token`) handed to containers, kept out of git.
- Three task variants per task, one per spec format, generated by script.
- `score.py`'s logic re-housed in each task's `test.sh`; the contamination audit rebuilt on Harbor's
  trajectory, or dropped with the argument that a container cannot reach the host.
- The container has public network by default; our harness had the same exposure and handled it with
  the tool list. The `allowlist` mode would be stricter (*not tried*).
- Usage telemetry must be switched off in every shell that runs it.

**What we lose if we do not adopt it:** the public task format (our tasks would be reusable by others
and the report could name a known platform); parallel trials, attempts and retries; the free sanity
agents; the trajectory viewer.

**What we lose if we do adopt it:** the no-Docker sandbox; a harness we fully understand and have
already used for a pilot; some days of porting.

**A finding that goes beyond Harbor:** Docker is now installed, so the Docker routes of other candidates
are open as well (ProjectEval's supported Linux route, and any benchmark that runs repositories).

## 6. Revisit guide — how to repeat or continue this trial

Written 2026-10-12 so that a later session can pick this up without the conversation it came from.

### 6.1 What is in this folder

| File | Tracked in git? | What |
|---|---|---|
| `TRIAL.md` | yes | This record |
| `build_lend_task.py` | yes | Generates a Harbor task from `harness/tasks/lend-messy/` (Markdown format) |
| `lend-oracle.result.json` | yes | Harbor's `result.json` for the reference run of `lend` (rewards and phase timings) |
| `lend-claude-sonnet-markdown.result.json` | yes | Harbor's `result.json` for the one model run (rewards, cost, tokens, phase timings). Checked: holds no token |
| `example-task/` | yes | The task that `harbor init` scaffolds (Harbor's template, Apache-2.0), with our one-line instruction and solution |
| `registry-datasets.txt` | yes | Name, version and task count of every dataset in Harbor's default registry on 2026-10-12 (§2a) |
| `harbor-venv.freeze.txt` | yes | `pip freeze` of the virtualenv (91 packages, Python 3.12.3) |
| `download/.venv/` | **no** | The virtualenv with Harbor 0.24.0 |
| `download/lend-task/` | **no** | The generated Harbor task (it holds a copy of the hidden tests and the reference) |
| `download/jobs/` | **no** | Job folders: `oracle-hello`, `oracle-lend`, `oracle-lend-2`, `nop-lend-2`, `claude-lend-markdown` (with the agent's full transcript and trajectory) |

### 6.2 Rebuild from nothing

```bash
docker run --rm hello-world                  # Docker must work without sudo
cd harness/platforms/harbor
mkdir -p download && cd download
/usr/bin/python3.12 -m venv .venv            # Harbor needs Python >= 3.12
. .venv/bin/activate
export HARBOR_TELEMETRY=0                    # BEFORE the first harbor command, in every shell
pip install harbor==0.24.0
harbor --version                             # 0.24.0
```

### 6.3 Repeat the no-model runs

```bash
# from harness/platforms/harbor/download, virtualenv active, HARBOR_TELEMETRY=0
python3 ../build_lend_task.py lend-task                       # regenerate the Harbor task
harbor run -p ../example-task -a oracle -o jobs --job-name oracle-hello   # machinery: reward 1.0
harbor run -p lend-task       -a oracle -o jobs --job-name oracle-lend    # expect 24 / 24
harbor run -p lend-task       -a nop    -o jobs --job-name nop-lend       # expect 0 / 24
cat jobs/oracle-lend/lend-task__*/verifier/reward.json
cat jobs/oracle-lend/lend-task__*/agent/oracle.txt            # the "PROBE" lines: /tests is absent
harbor view jobs                                              # web viewer (not tried)
```

Useful `harbor run` options (from `--help`): `-p` task or dataset path, `-a` agent, `-m` model, `-e`
environment type, `-k` attempts per trial, `-n` concurrent trials, `-r` retries, `-o` output folder,
`--job-name`, `--ak key=value` for agent options, `--env-file`.

Where things are in a job folder: `jobs/<job>/result.json` (summary), and per trial
`<task>__<id>/result.json` (rewards, timings, tokens, cost), `agent/` (the agent's log),
`verifier/` (`reward.json`, and whatever `test.sh` wrote under `/logs/verifier/`: here `junit.xml`,
`pytest.out`, `pip.log`), `trial.log`.

### 6.4 To continue (in this order; each step answers one open question)

1. **Subscription run — DONE 2026-10-12 (§3).** Every model run needs the owner's approval. The token
   is in `~/.config/sdd-compiler/claude-oauth.env` (owner's file, outside the repository; valid one
   year from 2026-10-12 by `claude setup-token`'s own message). To repeat:
   ```bash
   source ~/.config/sdd-compiler/claude-oauth.env
   export CLAUDE_FORCE_OAUTH=1 HARBOR_TELEMETRY=0
   env -u ANTHROPIC_API_KEY .venv/bin/harbor run -p lend-task -a claude-code \
       -m anthropic/claude-sonnet-5-5 --ak max_budget_usd=10 -o jobs --job-name <new-name>
   grep -rl "sk-ant-oat01" jobs/<new-name>     # must print nothing
   ```
   The `--ak` names are the field names in `agents/installed/claude_code.py` lines 54–101 (`max_turns`,
   `allowed_tools`, `disallowed_tools`, `permission_mode`, `max_budget_usd`). *Not checked:* the form
   `-m` expects for a Claude model, and whether `--ak` takes these names as written. Read
   `harbor run --help` and `harbor agent --help` first.
2. Read that trial's `result.json`: are `cost_usd`, `n_input_tokens`, `n_cache_tokens`,
   `n_output_tokens` filled? How long was `agent_setup` (the Claude Code install)?
3. Run the same task and model through `harness/run_task.py` and compare cost, tokens and tests passed.
4. Add the export (graph) variant once `lend` is compiled: same script, `spec/` replaced by the export
   and the export's spec line.
5. Decide on the contamination audit: rebuild it on the trajectory, or drop it and say why.

### 6.5 Questions left open

| Question | How to answer it |
|---|---|
| ~~Does Claude Code run on the subscription token in the container?~~ | Yes (§3) |
| Cost and token fields are filled (§3). Do they match our harness? | §6.4 step 3 |
| Why does Harbor's per-model cost ($0.152025) differ from Claude Code's ($0.1813725)? | Read how `model_usage` is priced in `agents/installed/claude_code.py` |
| Can the Claude Code version be pinned, and the install cached? | The agent's version option; or install in the task's Dockerfile |
| Do `allowed_tools` / `disallowed_tools` take effect? | One run with a restricted list; read the start event's `tools` |
| ~~Where is the source repository~~ (`github.com/laude-institute/harbor`), and what is its commit for 0.24.0? | The repository's tags or releases page |
| Does the Hub website list datasets the legacy registry does not? | Open `hub.harborframework.com/datasets` |
| Are DevEval's specifications large enough to compile, and does its Harbor adapter run here? | Trial 8: `harbor download deveval`, then the `oracle` agent on one task |
| What exactly does a telemetry event contain? | Read `telemetry.py` (`posthog_properties`, the two event models) |
| Can the container's network be limited to what Claude Code needs? | `task.toml` `network_mode = "allowlist"` with `allowed_hosts` (`models/task/config.py`) |
| ~~Does the agent's container inherit anything from our host configuration (CLAUDE.md, memory, hooks)?~~ | No sign of it in the model run: no MCP servers, memory path inside the trial folder, no mention of `CLAUDE.md` or the repository in the transcript (§3) |
| Can the Claude Code install be cached between trials? | Put it in the task's Dockerfile, or look for a Harbor option |
