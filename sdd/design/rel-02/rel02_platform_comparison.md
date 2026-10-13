# rel02 — platform comparison: trials, findings, recommendation, plan

> Written 2026-10-12, after milestone 1. Non-authoritative design note.
> **Decided by the owner 2026-10-12 (brainstorm D13): Harbor is the platform, DevEval the public
> benchmark, the messy-specification tasks are our own.** The plan in §5 is worked in quick
> iterations (D14), so its order may change. Every figure below was measured in a trial and names its source file.
> Every `$` is Claude Code's `total_cost_usd`: an estimated API-equivalent on the subscription.
> A **platform** runs an agent on a task and records what happened; it has no tasks of its own.

## 1. Have all candidate platforms been tried?

**Every platform on the trial queue has a record, but only two have run a model, and one never ran
anything.** Six more tools named in the survey were ruled out from their documentation and never tried.

| Platform | Where it came from | How far the trial went | Record |
|---|---|---|---|
| **Harbor** 0.24.0 | Proposal | **Full.** Our `lend` task and one DevEval project run with the reference, the do-nothing agent, and Claude Code on the subscription (3 model runs) | `harness/platforms/harbor/TRIAL.md` |
| **`harness/`** (ours) | Built for the F1 pilot, 2026-09-30 | **Full on one task.** Two model runs on `f1-ingest`. On `lend` only the dry run | `harness/README.md`, `docs/MIA5150-Project/pilot-F1-results.md` |
| **ProjectEval's judge** | Proposal (benchmark and platform) | **Run without a model.** Scored its own reference answer | `harness/benchmarks/projecteval/TRIAL.md` |
| **Inspect AI** 0.3.278 + Inspect SWE 0.2.71 | Added by the owner (D8) | **Installed, code read, nothing run** | `harness/platforms/inspect-ai/TRIAL.md` |
| **RealBench's pipeline** | Proposal (benchmark and platform) | **Not obtainable.** No code, data or address in the paper or in two searches | `harness/benchmarks/realbench/TRIAL.md` |

**Named in the survey, not tried** (`docs/MIA5150-Project/metrics-and-platforms-survey.md` §3, §6). These
judgements rest on documentation pages, not on trials:

| Tool | Why it was not queued |
|---|---|
| Terminal-Bench | A public benchmark in Harbor's task format, not a separate runner; Harbor's registry lists it (`registry-datasets.txt`). Using Harbor covers it |
| OpenHands Benchmarks | Adding a custom benchmark was not documented; Claude models go through a proxy, not Claude Code |
| SWE-bench harness | Runs SWE-bench's fixed tasks only |
| lm-evaluation-harness | Prompt in, text out; no agent loop |
| DeepEval | Scores text with a model as judge; does not run a coding agent |
| promptfoo | Coding-agent support not documented on the page read |

**Gaps to state in the report:**

- Inspect AI's verdict rests on reading its code, not on a run.
- Harbor and `harness/` have not run the same task, so their numbers are not yet cross-checked.
- Harbor has been run with one agent and one model only, with n = 1 per condition.

## 2. Findings per platform

**Harbor.** Fits.
- Our task converted by one script, unchanged in content. `lend`: reference 24 / 24, do-nothing 0 / 24
  (`lend-oracle.result.json`). Hidden tests are uploaded only after the agent stops.
- Claude Code ran on the subscription token with no API key (`apiKeySource: "none"`): 24 / 24,
  $0.1813725, 6 turns, 3 min 5 s (`lend-claude-sonnet-markdown.result.json`).
- Its `cost_usd` is Claude Code's own figure. Its per-model cost figure differs ($0.152025) and its
  "input tokens" include cache tokens: use neither without care.
- 95.2 s of that run was installing Claude Code in the container (n = 1).
- It brings no fitting benchmark by itself: 80 registry entries, none of our candidates by name; `deveval`
  is the near match, and its packaging leaks the reference and the tests
  (`harness/benchmarks/devbench-2024/TRIAL.md`).
- Needs Docker, a long-lived token, and `HARBOR_TELEMETRY=0` in every shell.

**`harness/` (ours).** Works, narrower.
- F1 pilot, Sonnet: Markdown 26 / 26, $0.52, 182 s; export 26 / 26, $0.70, 186 s
  (`pilot-F1-results.md`).
- Sandbox is bubblewrap, no container runtime; tools limited to `Bash, Read, Write, Edit`.
- It has two things Harbor lacks: the contamination audit of every tool call, and the
  requirement-by-requirement mapping in `score.py`.
- It lacks parallel trials, attempts and retries, the no-model sanity agents, and a public task format.

**ProjectEval's judge.** Not a general platform.
- It scores only ProjectEval's 20 projects, and needs per-project parameter answers from the agent.
- It needed 5 fixes on Linux; its own reference answer then scored 202 / 284
  (`canonical-run.result.json`), cause not investigated.
- It runs generated code on the host with no sandbox, and records no time, cost or tokens.

**Inspect AI.** Does not match the study's definition of a run.
- Its `claude_code` agent puts Claude Code behind a bridge: model calls are answered by Inspect's own
  client, and Claude Code gets a placeholder key. Cost would not be `total_cost_usd`.
- No `CLAUDE_CODE_OAUTH_TOKEN` anywhere in Inspect SWE; whether a subscription token may be used
  through Inspect's client was not tried and not established.
- In its favour, by its docs only: standard errors and confidence intervals built in.

**RealBench's pipeline.** Nothing to evaluate.

## 3. Comparison

"Seen" means observed in a run here; "code" means read in the installed code; "docs" means read on a
documentation page only.

| Criterion | Harbor | `harness/` (ours) | Inspect AI | ProjectEval's judge |
|---|---|---|---|---|
| Runs our own tasks | Yes, seen | Yes, seen | Not tried (docs: yes) | No: its 20 projects only |
| Claude Code on the subscription, no API key | **Yes, seen** | **Yes, seen** | No route proven (code) | Does not run an agent |
| Cost is Claude Code's `total_cost_usd` | Yes, seen | Yes, seen | No (code) | No cost recorded |
| Time and tokens recorded | Yes, per phase, seen | Yes, seen | Its own count (docs) | No |
| Hidden tests kept from the agent | Yes, seen | Yes, seen | Not tried | Agent is told what is tested |
| Isolation | Docker container | bubblewrap | Docker (docs) | None, runs on the host |
| Several named scores per trial | Yes, seen (4 rewards) | Yes (`score.json`) | Yes (docs) | Tests passed only |
| Omission and invention scoring | Ours to write in `test.sh` | Partly built in `score.py` | Ours to write | None |
| Free no-model sanity agents | Yes, seen | No (manual check) | Mock model (docs) | Reference answer run |
| Parallel trials, attempts, retries | Yes (code) | No | Yes (docs) | Pass@k (paper) |
| Error bars built in | No | No | Yes (docs) | No |
| Public task format a reader can rerun | Yes | No | Yes | Its own |
| Contamination audit of tool calls | No (trajectory kept) | Yes | Not tried | No |
| Licence | Apache-2.0 | Ours | MIT | GPL-3.0 |
| Fixed overhead per trial | 95.2 s install + about 26–31 s (n = 1) | *Not measured* | *Not measured* | 2 min 22 s for 20 projects |
| Model runs done here | 3 | 2 | 0 | 0 |

## 4. Recommendation

1. **Adopt Harbor as the study's platform.** It is the only outside candidate that ran Claude Code on
   the subscription and reported Claude Code's own cost figure, and it adds what `harness/` lacks.
2. **Keep `harness/` as the cross-check and the fallback,** and as the source of the scoring logic.
3. **Do not adopt Inspect AI, ProjectEval's judge, or RealBench's pipeline.**
4. **No further platform trial is needed for the choice.** One optional, free step would let the report
   say Inspect AI was run, not only read: one sample with its mock model. It would not change the
   recommendation, because the bridge is in the code.

**What this choice drops:**

- Built-in error bars (Inspect). We compute them ourselves from Harbor's result files.
- The sandbox that needs no Docker, and a harness already used and fully understood.
- The contamination audit, unless it is rebuilt on Harbor's trajectory files.
- ProjectEval's and RealBench's own judges, named as platforms in the proposal. The report must say
  they were tried and why they were rejected.

SWE-Dev (candidate 9, added later) ships its own inference and scoring scripts; they are not a
general platform either (`harness/benchmarks/swe-dev/TRIAL.md`).

## 5. Plan

Steps 1–4 cost no model calls. Steps 5–7 need the owner's approval each time.

| # | Step | Done when | Model calls? |
|---|---|---|---|
| 1 | Owner decides the platform and the tasks (Q6), and Q11 | Decision in the brainstorm log | No |
| 2 | Pin the Claude Code version and cut the 95 s install (bake it into the task image, or Harbor's version option) | Two reference-agent runs show the same version and a shorter setup phase | No |
| 3 | Restrict the agent: tool allow-list as in `harness/` (`Bash, Read, Write, Edit`), and try the `allowlist` network mode | Start event lists only those tools; a `curl` to an outside host fails | No |
| 4 | Port the scoring into each task's `test.sh`: requirements met, omissions, inventions, audit items as named rewards | Reference agent scores full marks and do-nothing scores zero on every reward, for `lend` | No |
| 5 | Cross-check the two platforms: `lend` Markdown on Sonnet through `harness/`, against the Harbor run already made | Tests passed agree; cost, turns and tokens compared, with the token definitions reconciled | **Yes, 1 run** |
| 6 | Test the budget ceiling stops a run (a deliberately low `max_budget_usd`) | Run ends at the ceiling with a recorded reason | **Yes, 1 short run** |
| 7 | Ceiling check on Haiku (Q10): `lend` Markdown, `hone` Markdown, `hone` export | Three result files; says whether a weaker model leaves room between formats | **Yes, 3 runs** |
| 8 | Write the script that reads Harbor result files into one table with means and confidence intervals | Reproduces the pilot table from the stored result files | No |

Costs of steps 5–7 are *to be measured*. The only measured figures are the three Sonnet runs through
Harbor: $0.18, $0.12 and $0.19.

## 6. How well known is each candidate? (added 2026-10-12, owner's question)

**How it was determined.** No single number measures "well known", so several public indicators were
read on 2026-10-12 and reported side by side. None of them measures quality.

| Indicator | Read from | What it shows | Its weakness |
|---|---|---|---|
| Venue and peer review | The venue's own page, Semantic Scholar | Whether reviewers accepted it, and where | A workshop or a preprint is weaker than a main conference |
| Citations | Semantic Scholar API | Use by other researchers | Grows with age; a 2026 paper cannot match a 2023 one |
| GitHub stars, forks, last push | GitHub API | Interest and whether it is maintained | Stars are cheap; they show attention, not use |
| Downloads | pypistats, Hugging Face, Docker Hub | Actual installs | Includes automated installs and mirrors |
| Adoption by others | Registries and README claims | Whether third parties build on it | Hard to count; claims must be opened |

**Platforms**

| | Harbor | Inspect AI | SWE-bench runner | Terminal-Bench (first version) |
|---|---|---|---|---|
| GitHub repository | `harbor-framework/harbor` | `UKGovernmentBEIS/inspect_ai` | `SWE-bench/SWE-bench` | `harbor-framework/terminal-bench-1` |
| Stars / forks | 6 049 / 1 990 | 2 990 / 805 | 6 013 / 1 009 | 2 600 / 571 |
| Created / last push | 2025-08-04 / 2026-10-13 | 2023-11-14 / 2026-10-13 | 2023-10-04 / 2026-09-18 | 2025-01-17 / 2026-07-11 |
| PyPI downloads, last month | 4 778 308 (`harbor`) | 2 896 739 (`inspect-ai`) | 22 102 583 (`swebench`) | 23 475 (`terminal-bench`) |
| A paper to cite | None found | None found | Yes (arXiv:2310.06770) | Not looked for |

Harbor was opened earlier in this trial under `laude-institute/harbor`; GitHub now answers that name
with `harbor-framework/harbor`.

**Benchmarks** (citations and venue from Semantic Scholar; Doc2Feat-Bench was not looked up)

| | Citations | Venue | GitHub stars | Last push |
|---|---|---|---|---|
| SWE-bench *(for scale; not a candidate)* | 4 283 | ICLR | 6 013 | 2026-09-18 |
| ProgramBench | 51 | arXiv 2026 | 952 | 2026-10-12 |
| **DevEval** | 49 | COLING 2024 | 139 | 2024-05-30 |
| ProjectEval | 31 | ACL 2025 | 29 | 2026-07-03 |
| RepoGenesis | 13 | ACL 2026 | 41 (a shared Microsoft repository) | 2026-05-20 |
| SWE-Dev | 12 | arXiv; workshop poster per the NeurIPS 2025 site | 62 | 2025-10-24 |
| RealBench | 6 | Proc. ACM Softw. Eng. 2026 | no repository found | — |

**What the indicators say:**

1. **The platform recommendation is also the well-known choice.** Harbor is about level with the
   SWE-bench repository in stars and far ahead of the other candidates in downloads. Its weakness for
   a report is that there is no paper to cite: cite the repository, the version (0.24.0) and the
   documentation.
2. **No benchmark that starts from a specification is well known.** All six candidates have between
   6 and 51 citations; SWE-bench has 4 283. The well-known benchmarks do not fit the question
   (survey §6), and the fitting ones are not well known.
3. **Among the fitting ones DevEval is the most established:** peer-reviewed at a main conference,
   49 citations, and included in Harbor's registry. Its repository has not been pushed to since
   2024-05-30.
4. **SWE-Dev is the least known of the candidates that could be downloaded,** and it shares its name
   with another paper, which a reader may confuse it with.

**Recommendation on credibility.** Name Harbor as the platform and DevEval as the public benchmark,
and say plainly that the messy-specification tasks are our own because no public benchmark has them.
The report gains more from that statement, with the nine trial records behind it, than from a famous
name that does not fit. *What this drops:* a headline comparison on a benchmark every reader knows.
If one is wanted, the survey's option stands: SWE-bench as an outside baseline for the agents only,
not as a test of the formats.
