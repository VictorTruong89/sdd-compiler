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

## 5a. Round 1 of the working map: scoring, pinned agent, limited tools and network (2026-10-12, no model call)

Stage A of the working map (brainstorm D15). Everything here was checked with the free agents or with
Claude Code started without credentials; **the first model run must confirm the three items marked
"to confirm"**.

| What | How it is done | Checked how | Result |
|---|---|---|---|
| Omissions | `harness/tasks/lend-messy/scoring/lend_score.py`, run by `tests/test.sh`: a requirement R1–R24 is met when every hidden test named for it passes | Reference and do-nothing agents | Reference: 24 met, 0 omissions. Do-nothing: 0 met, 24 omissions (`lend-oracle-pinned.score.json`, `lend-nop.score.json`) |
| Inventions, automatic part | Five probes through the command, one per planted contradiction: the build took statement A, statement B, or **neither**. Plus commands in `lend --help` beyond the eight specified | `scoring/check_scoring.py`: three variants of the reference with known behaviour | All pass: A-variant 5 × A; B-variant 5 × B and 1 extra command; third variant "neither" on the four items where a probe can show it |
| Audit triage | Keywords for A1–A6 in the agent's `OPEN_QUESTIONS.md` and `IMPLEMENTATION_NOTES.md` (`noticed_auto`). **A triage, not the audit** | A sample note naming three items | 3 of 6 found, as written |
| Files for the human audit | `test.sh` copies the two notes, `pyproject.toml` and an archive of `/app` to `verifier/agent_files/` | Reference agent | Present in the job folder |
| Agent version | `--claude-version 2.1.296` puts that release in the task image | `claude --version` in the agent phase | `2.1.296 (Claude Code)`; agent setup phase 0 s with the reference agent. **To confirm:** that Harbor skips its own install when run with `--ak version=2.1.296` |
| Tools | `--ak disallowed_tools=…` (19 names, §6.4) | Claude Code started in the image with no credentials and no network; its start event read | Tools offered: `Bash`, `Edit`, `Read`, `Write`. Cost 0, "Not logged in". **To confirm** in a logged-in run: the list can differ |
| Network in the agent phase | `[agent] network_mode = "allowlist"`, hosts `api.anthropic.com`, `pypi.org`, `files.pythonhosted.org` | Probes in the reference agent's script | `pypi.org` and `api.anthropic.com` reached; `example.com` and `github.com` blocked. **To confirm:** that Claude Code works with only these hosts |

Fourteen named rewards per trial now, in `reward.json`; the detail behind them is in `score.json`.
The pinned image is 570 MB and took about 55 s to build the first time; Harbor removes it after each
job, so that time recurs unless Docker's build cache holds.

**Limits, stated plainly:**

- The invention count is partial. It catches behaviour no statement supports on five planted items,
  and extra commands. Inventions elsewhere in the code still need the human audit.
- `noticed_auto` is a keyword match. It has not been compared with a human reading of a real run.
- The earlier Sonnet run of `lend` (§3) cannot be rescored: that task version did not keep the
  agent's files.
- Restricting the network and the tools changes the conditions compared with the three pilot runs.

## 5b. Round 2: the messy task in both formats, Sonnet, n = 1 each (2026-10-13)

Owner approved the compile and both runs. Files: `round2/`. Conditions as set in round 1, the same
for both runs; the two task folders differ only in `spec/` and one line of the task text (checked
with `diff`). Free checks on the export task first: reference 24 / 24, do-nothing 0 / 24.

**The three items round 1 left to confirm: all confirmed.** Agent setup took 0–1 s (Harbor skipped
its install); the start event lists `Bash`, `Edit`, `Read`, `Write` and version 2.1.296,
`apiKeySource: "none"`; Claude Code ran to completion behind the three-host allow-list. No token in
the job files.

| | Markdown (7 files, 2 120 words) | Graph export (25 packs, 13 516 words) |
|---|---|---|
| Hidden tests | 24 / 24 | 24 / 24 |
| Requirements met / omissions | 24 / 0 | 24 / 0 |
| Contradiction sides P1, P2, P3, P4, P10 | A, B, A, A, A | A, B, A, A, A |
| Answers matching neither statement | 0 | 0 |
| Extra commands | 0 | 0 |
| Turns / agent time | 5 / 56.6 s | 6 / 71.9 s |
| Cost, est. API-equivalent | $0.1451 | $0.2351 |
| Input tokens incl. cache / output | 56 374 / 8 172 | 139 791 / 9 419 |
| Audit items named in its notes (assistant's reading) | A1, A2, A3, A4 | A2, A3, A4, A5 |
| Not named | A5 worked example, A6 vague "fast" | A1 fee cap $15, A6 only in passing |

Compile for the export: 98 calls, $0.5031, 37 min 34 s (`round2/lend-compile-1.json`).

**What it shows, as observations (n = 1):**

1. **No difference on anything the scorer measures.** Same tests, same omissions, the same side on
   every contradiction, no invented behaviour in either.
2. **The export cost 1.6 times more to run** ($0.2351 against $0.1451), plus the compile.
3. **Each agent missed a different planted contradiction in its notes.** The export agent did not
   name the fee cap ($10 against $15), which is also one the compiler missed: the two statements sit
   in packs 00 and 06 with no link. The Markdown agent did not name the worked example. Both named
   the superseded limit and chose 3.
4. **Where the compiler flagged a contradiction, the export agent cited it** (CF ids and node ids in
   its notes) — the flag reached the agent.

**Defect found in our own scorer:** the keyword triage counted the export run's "pack 15" and
"15 June" as the fee-cap item. Fixed in `lend_score.py` (a dollar sign or "1500 cents" is now
needed) and covered in `check_scoring.py`. The stored `score.json` files hold the values from before
the fix (`noticed_auto` 4 and 6); after it they are 4 and 5, the fifth being a passing mention of
"fast". The triage stays a triage.

## 5c. Round 3: the same two runs on Haiku, n = 1 each (2026-10-13)

Owner approved. Files: `round3/`. Same task folders, export (checksum verified) and conditions as
round 2; only the model changed (`anthropic/claude-haiku-5-5`, reported as `claude-haiku-5-5`). The
task's scorer carried the triage fix from round 2.

| | Markdown | Graph export |
|---|---|---|
| Hidden tests | 24 / 24 | 24 / 24 |
| Requirements met / omissions | 24 / 0 | 24 / 0 |
| Contradiction sides P1, P2, P3, P4, P10 | A, B, A, A, A | A, B, A, A, A |
| Answers matching neither statement | 0 | 0 |
| Commands beyond the eight (read in the code; the scorer could not parse the help text) | 0 | 0 |
| Turns / agent time | 35 / 246.4 s | 43 / 296.4 s |
| Cost, est. API-equivalent | $0.0539 | $0.1118 |
| Input tokens incl. cache / output | 897 440 / 60 939 | 1 627 993 / 71 744 |
| Lines of Python written (source and its own tests) | 948 | 1 049 |
| Words in its two notes files | 1 970 | 2 205 |
| Audit items treated as contradictions in its notes (assistant's reading) | A2, A3, A4, A5 | A2, A3, A4, A5 |
| Fee cap, A1 | Looked at and judged **not a conflict**: a $10 cap satisfies "nobody should owe more than $15" | Not mentioned |

**What it shows, as observations (n = 1):**

1. **Haiku is at the ceiling too.** Four runs on `lend` now (two models, two formats): every one
   24 / 24, 0 omissions, and the same side on all five contradictions. The task does not separate
   the formats on any scored measure with either model.
2. **The export cost about twice as much to run on Haiku** ($0.1118 against $0.0539); 1.6 times on
   Sonnet.
3. **The export agent said what the graph did not flag.** Its notes mark the borrowing limit, the
   renewal example and the fees-over-$5 rule as "not flagged by the MAP": it found three of the
   compiler's four misses by reading the packs.
4. **The fee cap is not named by the export agent in either round;** the Markdown agent addressed it
   in both.

**Two defects found in our own materials:**

- **Planted item P1 is not a real contradiction.** "Nobody should owe more than $15" and "capped at
  $10.00" can both hold; the Haiku Markdown agent said so. So the compiler's "miss" of P1 may be
  correct, and its recall on the key is 5 of 8 if P1 is set aside. The answer key and audit item A1
  need rewording or removal before `lend` is used again.
- **The scorer could not parse `--help`** when the command list had a metavar (`extra_commands` −1 in
  both runs). Fixed in `lend_score.py` and covered in `check_scoring.py`; the stored `score.json`
  files hold the −1.

**A limit of the task design, seen after three rounds.** The hidden tests were written never to
depend on how a contradiction is resolved, and the contradictions are left unsettled in both
formats. So what the graph adds — flagging conflicts — cannot change any scored number by design.
Only the agents' notes can show it, and those need the human audit.

## 5d. Round 4: the export with the owner's verdicts, Sonnet and Haiku, n = 1 each (2026-10-13)

**Question:** when the owner settles the contradictions the compiler reported, does an agent given
the export build the settled behaviour?

**What changed against rounds 2 and 3.** Only the export. On a copy of the store (`~/sddc-runs/lend-r4/`)
the owner's verdict was recorded on the four reported contradictions with
`sddc conflicts judge CF-… --verdict real --note "…"` (no model call), and `sddc export` then ran
without `--allow-open` (0 unsettled). Each settled conflict appears in the packs of its nodes as
`Settled: CF-… / rationale / adjudication: <the owner's note>`. Six files differ from the round 2
export (`MAP.md`, `export.meta.json`, packs 09, 16, 22, 24); 13 731 words against 13 516. Task,
instruction, hidden tests, agent version, tools and network are those of round 1.

| Planted item | Conflicts | Owner's verdict (2026-10-13) | Side |
|---|---|---|---|
| P2 | CF-000001, CF-000010 | `loans/spec.md` wins: overdue only from the day after the due date, in the report too | A |
| P3 | CF-000004, CF-000009 | `ops/notes.md` wins: each report row carries the contact email, sixth column `email` | B |

Both verdicts are the opposite of what every build of rounds 2 and 3 chose unaided. This was chosen on
purpose and must be stated in the report: a verdict that agrees with the unaided choice cannot show an
effect. P4 and P10 have no verdict because the compiler did not report them.

**New measure.** `lend_score.py --settled P2=A,P3=B` adds `settled_followed` / `settled_total`, using the
existing probes. Checked by `check_scoring.py` (five checks pass) and by the reference solution through
Harbor (`r4-oracle-settled`: 24 / 24, settled 1 of 2, as the reference takes side A on P3).

**Runs.** Markdown side: not rerun (owner's choice); the round 2 and 3 builds were rescored offline from
their stored `app.tgz`. The unsettled-export builds were rescored the same way.

| Build | Model | Tests | Sides P1 P2 P3 P4 P10 | Settled followed | Turns | Agent time | Cost (est.) |
|---|---|---|---|---|---|---|---|
| Markdown (round 2, rescored) | Sonnet | 24 / 24 | A B A A A | 0 of 2 | 5 | 56.6 s | $0.1451 |
| Export, unsettled (round 2, rescored) | Sonnet | 24 / 24 | A B A A A | 0 of 2 | 6 | 71.9 s | $0.2351 |
| **Export, settled (round 4)** | Sonnet | 24 / 24 | A **A B** A A | **2 of 2** | 7 | 69.7 s | $0.2515 |
| Markdown (round 3, rescored) | Haiku | 24 / 24 | A B A A A | 0 of 2 | 35 | 246.4 s | $0.0539 |
| Export, unsettled (round 3, rescored) | Haiku | 24 / 24 | A B A A A | 0 of 2 | 43 | 296.4 s | $0.1118 |
| **Export, settled (round 4)** | Haiku | 24 / 24 | A **A B** A A | **2 of 2** | 53 | 304.1 s | $0.1227 |

0 omissions and 0 extra commands in both new builds. Both agents cite the verdict in `OPEN_QUESTIONS.md`
(Sonnet: "Settled conflict verdict: loans wins"; Haiku quotes the adjudication and its conflict ids).
`grep -rl "sk-ant-oat01"` on both job folders: empty.

**What this shows, and what it does not.**
- It shows that the chain works end to end: compile, the owner judges, export, the agent builds the
  settled behaviour. Both models followed both verdicts.
- It does **not** show that the graph is needed for this. The Markdown agent was given no decision at
  all, so "0 of 2" for Markdown says only that an agent cannot guess a decision it was not told. The
  missing control is Markdown plus the same two decisions in a plain file (not run; owner chose 2 runs).
- n = 1 per cell.

**Findings for the compiler (stage "fix compiler" of the working map).**
1. `MAP.md` of a settled export says nothing about settled conflicts and prints "unsettled
   contradictions: 0". The Haiku agent noted that the P4 pair is "not in the export's conflict list"
   although the MAP reports 0. A reader can take 0 to mean "no contradictions"; it means "none that
   the compiler found is unjudged".
2. The verdict is `real` or `false` plus a free-text note. Which side wins lives only in the note. The
   losing claim stays in its pack and in `CHECKLIST.md` as an ordinary item, so an agent told to
   "account for every id" must work out from prose that the id is dropped. Both agents did.
3. One contradiction can be several conflict records (P2 and P3 are two each), so the owner judged
   four records for two decisions and the same note is printed several times in a pack.

Files: `round4/` (result, score and notes of both runs; `rescore.*.score.json` for the four earlier
builds; `lend-adjudications.jsonl`; `lend-export-settled.sha256`).

## 5e. Round 5: the control — Markdown plus the decisions in a plain file, n = 1 each (2026-10-13)

**Question:** is the graph needed to carry the owner's decisions, or does a plain file do the same?

**What changed against the Markdown runs of rounds 2 and 3.** One file added to the spec folder:
`spec/DECISIONS.md` (`harness/tasks/lend-messy/decisions/DECISIONS.md`, 92 words; spec folder 2 212
words). It states the two verdicts of round 4 in the same words as the adjudication notes, naming files
instead of conflict and node ids. The instruction is unchanged and does not mention the file. Built
with `build_lend_task.py … --decisions FILE --settled P2=A,P3=B`. Reference solution through Harbor
(`r5-oracle-decisions`): 24 / 24, settled 1 of 2, as expected.

| Input | Model | Tests | Sides P1 P2 P3 P4 P10 | Settled followed | Turns | Agent time | Cost (est.) |
|---|---|---|---|---|---|---|---|
| Markdown (round 2) | Sonnet | 24 / 24 | A B A A A | 0 of 2 | 5 | 56.6 s | $0.1451 |
| **Markdown + decisions file (round 5)** | Sonnet | 24 / 24 | A A B A A | **2 of 2** | 5 | 69.1 s | $0.1461 |
| Export with verdicts (round 4) | Sonnet | 24 / 24 | A A B A A | 2 of 2 | 7 | 69.7 s | $0.2515 |
| Markdown (round 3) | Haiku | 24 / 24 | A B A A A | 0 of 2 | 35 | 246.4 s | $0.0539 |
| **Markdown + decisions file (round 5)** | Haiku | 24 / 24 | A A B A A | **2 of 2** | 35 | 185.2 s | $0.0381 |
| Export with verdicts (round 4) | Haiku | 24 / 24 | A A B A A | 2 of 2 | 53 | 304.1 s | $0.1227 |

0 omissions and 0 extra commands in both new builds; both agents cite `DECISIONS.md` in
`OPEN_QUESTIONS.md`, and both list the fees-over-$5 pair as a contradiction no decision covers.
`grep -rl "sk-ant-oat01"` on both job folders: empty.

**Reading.** On `lend`, a plain decisions file gives the same scored result as the settled export,
at 0.58 times (Sonnet) and 0.31 times (Haiku) the run cost, and without the compile. Across five
rounds no scored measure favours the graph export on this task. What the compiler did contribute
is upstream of the agent: it reported the two contradictions the owner then settled (and missed
P4 and P10; by keyword triage of the notes, the Markdown agents named P4 on both models and P10 on Haiku only). n = 1 per cell.

Files: `round5/`.

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

### 6.5 Round 1 commands (2026-10-12): build, free checks, and the model run that comes next

```bash
cd harness/tasks/lend-messy/scoring && python3 check_scoring.py        # scorer against known variants
cd ../../../platforms/harbor
python3 build_lend_task.py download/lend-markdown-pinned --claude-version 2.1.296 --agent-network allowlist
cd download && export HARBOR_TELEMETRY=0
.venv/bin/harbor run -p lend-markdown-pinned -a oracle -o jobs --job-name r1-oracle-pinned   # 24 / 24, 0 omissions
.venv/bin/harbor run -p lend-markdown-pinned -a nop    -o jobs --job-name r1-nop-pinned      # 0 / 24, 24 omissions

# NEXT, model call, needs the owner's go-ahead (round 2). Not run yet.
DISALLOW=Task,CronCreate,CronDelete,CronList,DesignSync,EnterWorktree,ExitWorktree,ListAgents,NotebookEdit,RemoteTrigger,ReportFindings,ScheduleWakeup,SendMessage,Skill,TaskStop,ToolSearch,WebFetch,WebSearch,Workflow
source ~/.config/sdd-compiler/claude-oauth.env; export CLAUDE_FORCE_OAUTH=1
env -u ANTHROPIC_API_KEY .venv/bin/harbor run -p lend-markdown-pinned -a claude-code \
  -m anthropic/claude-sonnet-5-5 --ak version=2.1.296 --ak max_budget_usd=10 \
  --ak disallowed_tools=$DISALLOW -o jobs --job-name <name>
```
