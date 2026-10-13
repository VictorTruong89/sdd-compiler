# Trial record — Inspect AI (with Inspect SWE)

> **Kind:** platform only (no tasks of its own) · **State:** TRIED 2026-10-12 in part, no model call —
> installed and its code read; **no task was run** ·
> **Verdict:** none yet — the owner decides at milestone 2.
> **Recommendation: do not adopt; Harbor already does the job.** Inspect runs Claude Code with its
> model calls re-routed through Inspect's own model client, so the run is not Claude Code on the
> subscription as the study defines it, and cost is not Claude Code's own figure (§2).
> Milestone 1 of `sdd/design/rel-02/rel02_brainstorm.md`. This file is the record for the final
> report: what was tried, what happened, and why the candidate was chosen or rejected.
> Rules: no number that was not printed by a command here; no claim about the paper that was not read
> on the page; failures are written down, not removed.

## 0. What we knew before the trial (not verified by us)

From the survey §3 and §4 (docs pages read 2026-09-29): an evaluation framework from the UK AI
Security Institute; datasets from CSV/JSON/JSONL; samples can carry files copied into a sandbox;
several scorers per task; built-in accuracy, standard error and confidence intervals; Claude Code and
Codex CLI available through the Inspect SWE package. **Not confirmed:** whether they run on the
subscription login. Added by the owner 2026-10-12 (rel02 Q7).

## 1. Source

| | |
|---|---|
| Paper | None. Docs: `inspect.aisi.org.uk` (pages read 2026-09-29); Inspect SWE docs at `meridianlabs-ai.github.io/inspect_swe` (address from a search result; **not opened**) |
| Code / data URL | PyPI packages `inspect-ai` and `inspect-swe` |
| Version or commit tried | `inspect_ai` 0.3.278, `inspect_swe` 0.2.71, from PyPI on 2026-10-12 |
| Licence (read where) | MIT for both — the `License` field of `pip show` (the licence files were not opened) |
| Download size | 306 MB for the virtualenv (82 packages, `inspect-venv.freeze.txt`) |
| Downloaded to | `download/.venv/` in this folder (ignored by git) |

## 2. The five questions

All from **reading the installed code**; nothing was executed beyond `pip`.

| # | Question | Answer | Evidence (file in `site-packages`) |
|---|---|---|---|
| 1 | How is one of OUR tasks packaged? | *Not tried.* By the docs read earlier: a Python task file with a dataset of samples, a solver (the agent) and scorers | — |
| 2 | Does its `claude_code` agent run on the subscription login, without an API key? | **Not in the sense our study needs.** The agent starts Claude Code in the sandbox behind a **bridge**: Claude Code's model requests go to a local proxy and are answered by whatever model Inspect itself is serving. Claude Code is given a placeholder key (`"dummy-key-for-bridge"`). Inspect's own Anthropic client needs `ANTHROPIC_API_KEY`, or accepts a bearer token in `ANTHROPIC_AUTH_TOKEN`. Whether a subscription token works there, and whether using it from a client that is not Claude Code is permitted, was **not tried and not established** | `inspect_swe/_claude_code/claude_code.py` (lines 342–357, 434–445); `inspect_ai/model/_providers/anthropic.py` (lines 537–555) |
| 3 | What does it record that Harbor or `harness/` do not? | By the docs: standard error and confidence intervals built in; a log viewer. Token usage is Inspect's own count, since the calls pass through it. *Not seen in a run* | — |
| 4 | What does it need to run? | Python, Docker (or Kubernetes) for the sandbox, and model credentials for Inspect's provider | Search result on the package page; code |
| 5 | Which of our metrics does it give? | Whatever our scorers compute; time and tokens from its logs. **Cost would not be Claude Code's `total_cost_usd`**, which is the only cost figure this project reports | Reasoning from row 2 |

## 3. The one number

**None.** No task was run. Running one needs either an API key (ruled out by the project) or a test
of the subscription token through a different client (not done without the owner's say).

## 4. Log

| Date | What was done | Result |
|---|---|---|
| 2026-10-12 | Web search for Inspect SWE and subscription tokens | Package pages only; nothing on subscription login |
| 2026-10-12 | Virtualenv; `pip install inspect-ai inspect-swe` | 0.3.278 and 0.2.71, MIT, 306 MB |
| 2026-10-12 | Searched `inspect_swe` for `OAUTH`, `ANTHROPIC_API_KEY`, `subscription`, `setup-token`; read the bridge and environment code of the `claude_code` agent | No `CLAUDE_CODE_OAUTH_TOKEN` anywhere. Bridge design as in §2 row 2. A code comment says an earlier Claude Code version "enters an OAuth flow that silently fails" behind the bridge |
| 2026-10-12 | Searched `inspect_ai`'s Anthropic provider for token support | `ANTHROPIC_AUTH_TOKEN` accepted as a bearer token, with an OAuth header |

## 5. Verdict

**Chosen / rejected / kept as backup:** *the owner decides at milestone 2.* Recommendation: **do not
adopt.**

**Reasons:**
1. *Harbor already works* on this machine with Claude Code on the subscription, measured, and reports
   Claude Code's own cost figure.
2. *Inspect changes the thing being measured:* the model calls no longer go from Claude Code to
   Anthropic but through Inspect's proxy and client. Cost and token numbers would be Inspect's.
3. *The subscription route is unproven and of unclear standing.* It would mean giving the subscription
   token to a client other than Claude Code.

**What speaks for it:** built-in standard errors and confidence intervals; mature logging; MIT; a
government-backed project that is widely cited.

**What we lose by this choice:** the ready-made statistics. They are a few lines of code to compute
ourselves from Harbor's result files.

**To reopen:** only if Harbor fails later. First step would be one sample with the mock model
provider (`mockllm`), which costs nothing, to see the mechanics.

## 6. Revisit guide

Tracked here: `TRIAL.md`, `inspect-venv.freeze.txt`. Ignored: `download/.venv/`.

```bash
cd harness/platforms/inspect-ai/download
python3 -m venv .venv && .venv/bin/pip install inspect-ai==0.3.278 inspect-swe==0.2.71
grep -n "sandbox_agent_bridge\|dummy-key-for-bridge" .venv/lib/python3.*/site-packages/inspect_swe/_claude_code/claude_code.py
grep -n "ANTHROPIC_AUTH_TOKEN" .venv/lib/python3.*/site-packages/inspect_ai/model/_providers/anthropic.py
```
