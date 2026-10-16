# Handover prompt: round 12 (Opus on the 9 Python DevEval projects, Markdown only)

> Temporary. Written 2026-10-14 for a new Claude Code session; scope narrowed the same day by the
> owner from 21 projects to the 9 Python projects that can run now. Paste everything below the line as
> the first message. Delete this file once round 12 is recorded.

---

You are continuing rel02 of the SDD Compiler in `~/Workspace/sdd-compiler`, branch
`rel-02-graph-for-code-gen-test`. The owner (Victor Truong) works alone, runs work in quick rounds, and
wants progress, decisions, options and methodology recorded at every step. Read `CLAUDE.md` first.

## Binding rules (verbatim, no exceptions)

- **Never run `git commit` or `git push`.** The owner reviews and commits. Staging is also left to the owner. Never `git add`.
- **Never set or use `ANTHROPIC_API_KEY`.** Model runs use the owner's Claude Code subscription, and only after the owner approves the spend. Do not use Claude Code's `--bare` (it needs an API key).
- Anything that spends model calls, deletes, or is outward-facing needs the owner's explicit go-ahead.
- **No invented numbers.** A figure is measured (with its source file) or marked *to be measured*. Every `$` is Claude Code's `total_cost_usd`: an estimated API-equivalent on the subscription, never "spend".
- **No unverified citations.** Open the primary source before citing.
- Never hardcode a credential; read from the environment.
- The subscription token lives in `~/.config/sdd-compiler/claude-oauth.env`. Use it only via `source`; never print, copy or put it in a tracked file. After each run, `grep -rl "sk-ant-oat01" <job>` must be empty.
- Never mention the course in `sdd/specs/vision.md`. Lectures are HTML in `docs/lectures/`; working design and specs are Markdown.
- Third-party downloads stay in git-ignored `download/` folders. Run Harbor only with `HARBOR_TELEMETRY=0`.
- SWE-Dev's `infer/single/run.sh` carries someone else's API key: never run it, never copy it.
- Be concise; recommend and name what a choice drops. Work in quick iterations.

## Read before acting

- `harness/benchmarks/devbench-2024/PROJECTS.md`: all 22 DevEval projects (21 in Harbor), sizes, which work here.
- `harness/benchmarks/devbench-2024/TRIAL.md`: §8 (round 6, repackaging and checks), §9–§11 (rounds 7–11), §6 (files).
- `harness/benchmarks/devbench-2024/evidence/README.md`: how past runs are stored.
- `sdd/design/rel-02/rel02_report_draft.md` §R2–§R3, `rel02_methodology_notes.md` (threats, run register 1–34), `rel02_build_progress.md`, `rel02_brainstorm.md` (S14, D23).
- `sdd/design/rel-02/rel02_investigation_arxiv_digest.md`: how tests were triaged against the spec.

## Round 12: the owner's request

Run **Claude Opus** (`anthropic/claude-opus-5-5`) on the **9 Python projects** in the local Harbor
copy, implementation phase, with the **original Markdown documents only**. No sddc compile, no export.

| Project | Hidden tests | Task state (`download/clean/<project>-markdown/`) | Tests classified |
|---|---|---|---|
| arxiv-digest | 42 | current scorer | yes |
| lice | 31 | current scorer | yes |
| stocktrends | 9 | current scorer | yes |
| chakin | 2 | **old scorer: rebuild** | no |
| geotext | 9 | **old scorer: rebuild** | no |
| hone | 12 | **old scorer: rebuild** | no |
| hybrid-images | 19 | **old scorer: rebuild** | no |
| particle-swarm-optimization | 6 | **old scorer: rebuild** | no |
| readtime | 12 | **old scorer: rebuild** | no |

Hidden-test counts: `clean-tasks-check.json` (round 6); 142 in all. "Old scorer" means its
`tests/test.sh` lacks the round-8 fix (agent's own tests set aside, `--confcutdir`, workspace saved as
`app.tgz`); checked 2026-10-14 by grepping for `confcutdir`.

Two purposes:

1. **Which projects have tests that the spec covers, and does the best model pass them?** Per project:
   how many hidden tests the spec states (class S), and how many of those Opus passes.
2. **A benchmark:** Opus's score per project and in total, on DevEval as repackaged here.

**The owner's decisions on the awkward projects (2026-10-14): keep all three.**
- **`hybrid-images`:** keep. The reference passes only 12 of 19 tests (round 6). Report two scores:
  all 19, and the 12 the reference passes. List the 7 the reference fails by name.
- **`arxiv-digest`:** keep. Its acceptance tests call the live arXiv service (TRIAL §11). When an
  acceptance test fails, rerun the agent's saved code from the host against arXiv, as in round 11, and
  record whether the failure is the network or the code.
- **`actor-relationship-game`:** kept for the later non-Python round. It is Java, so it is not in
  these 9. It needs a TMDB key at test time.

## What is already true (checked 2026-10-14)

- `build_clean_task.py` builds Python projects only. Rebuild a task with
  `python3 build_clean_task.py python-<project> markdown download/clean/<project>-markdown --claude-version 2.1.296 --agent-network allowlist`.
  Check the options against how the round-11 tasks were built (TRIAL §11, build-progress log) before
  rebuilding.
- Test classes: S stated / U names stated, value not / R needs a detail the spec lacks / C contradicts
  the spec. They exist for `lice`, `arxiv-digest`, `stocktrends` in `test-classification.json` (keys
  `_about` plus one per project); `score_by_class.py <project> <verifier dir>` splits a run by class.
- A reward is accepted only when tests collected is at most the hidden-test count.
- Earlier results to compare against: Haiku and Sonnet on `lice`, `arxiv-digest`, `stocktrends`
  (rounds 7–11), Sonnet on `hone` (pilot, TRIAL §7). The `hone` pilot used the old scorer.
- The run command (from `harness/benchmarks/devbench-2024/download/`, one run at a time, inside
  `timeout`):

  ```bash
  source ~/.config/sdd-compiler/claude-oauth.env; export CLAUDE_FORCE_OAUTH=1 HARBOR_TELEMETRY=0
  H=../../../platforms/harbor/download/.venv/bin/harbor
  DISALLOW=Task,CronCreate,CronDelete,CronList,DesignSync,EnterWorktree,ExitWorktree,ListAgents,NotebookEdit,RemoteTrigger,ReportFindings,ScheduleWakeup,SendMessage,Skill,TaskStop,ToolSearch,WebFetch,WebSearch,Workflow
  env -u ANTHROPIC_API_KEY $H run -p clean/<project>-markdown -a claude-code -m anthropic/claude-opus-5-5 \
    --ak version=2.1.296 --ak max_budget_usd=10 --ak disallowed_tools=$DISALLOW -o jobs --job-name r12-<project>-markdown-opus-1
  ```

## Plan (stop for the owner where marked)

**Step 0 — folder (no model).** Create `harness/benchmarks/devbench-2024/round12-opus/` with:
- `README.md`: purpose, conditions (model, Claude Code version, task builds, date), index; filled in as
  runs land.
- `queue.tsv`: one row per project (project, task path, status `pending|running|done|limited|failed`,
  job name, attempts, last limit message).
- `runs/<project>/`: `result.json`, `reward.json`, `pytest.out`, the junit files, `app.tgz`, and
  `agent.tgz` (the job folder with `claude-code.txt`, `trajectory.json`, the session transcript and
  `verifier/`; leave out `.claude.json`, settings, shell snapshots, backups and setup, as in
  `evidence/`).
- `classification/`: method notes and doubtful calls (the classes themselves go into
  `test-classification.json`).
- `results.json`: one record per project, built by a script from `runs/`, never by hand.

**Step 1 — classify the 60 unclassified tests before any run (no model call; reading only).** Six
projects: `chakin` 2, `geotext` 9, `hone` 12, `hybrid-images` 19, `particle-swarm-optimization` 6,
`readtime` 12. Sort each test into S/U/R/C against the four documents and extend
`test-classification.json`. Do it **before** seeing any Opus result, so the classes are not shaped by
what passed. Check each project with `score_by_class.py --check` against its reference run. Save after
each project.

**Step 2 — rebuild and check the six old tasks (no model).** Rebuild with the current builder; rerun
reference (`-a oracle`) and do-nothing (`-a nop`) on each. Expect reference 100 % except
`hybrid-images` (12 of 19), do-nothing 0. Clean up containers after.

**Step 3 — one Opus pilot run (needs the owner's go-ahead).** `readtime` or
`particle-swarm-optimization` (small, usable). Measure turns, wall time, `total_cost_usd`, and the share
of the plan's usage it took: ask the owner to read `/usage` in their own Claude Code before and after.
Do not guess plan limits. Use this to size the queue.

**Step 4 — the queue (needs the owner's go-ahead for the batch).** The remaining 8 projects, one at a
time, through the unattended driver below. Smallest first: `chakin`, `particle-swarm-optimization`
(or `readtime`, whichever was not the pilot), `geotext`, `stocktrends`, `hybrid-images`, `hone`,
`lice`, `arxiv-digest`. One run per project (n = 1); say so in every reading.

**Step 5 — read and record.** Per project: tests passed, S passed / S total, U, R, C, cost, turns;
`hybrid-images` on both bases; `arxiv-digest` network check. Compare with Haiku and Sonnet where they
exist. Write TRIAL §12, register rows from 35, build-progress rows, a brainstorm session and
decision, and a §R2 subsection in the report draft.

## Credit-limit plan (daily / rolling subscription limits)

The plan's exact limits are not known here: **do not invent them.** Measure from the pilot (step 3) and
the owner's `/usage` readings. Design for interruption:

1. **The driver must not depend on a Claude session.** This chat session draws on the same
   subscription, so it stops at the limit too. Write `round12-opus/run_queue.sh`, a plain bash script.
   The owner starts it with `nohup bash run_queue.sh > run_queue.log 2>&1 &` (or in `tmux`). It:
   - takes the next `pending` or `limited` row of `queue.tsv`, runs it with the command above inside
     `timeout`, copies the run files into `runs/<project>/`, checks for the token (stops the queue if
     one is found), and marks the row `done`;
   - after each run, checks whether it ended on a usage limit: Harbor's `exception_info` in
     `result.json`, a zero-turn or error result, or a limit message in `agent/claude-code.txt`. On the
     first such case it records the exact message in `queue.tsv` and the log, so the pattern comes from
     real output, not assumption. It marks the row `limited` so it is retried, and keeps the partial job
     under a renamed folder rather than overwriting it;
   - when limited, waits: it parses the reset time from the message if one is given. Otherwise it
     probes every 30 minutes with
     `env -u ANTHROPIC_API_KEY claude -p "reply ok" --model haiku --max-turns 1 --output-format json`
     (after `source`-ing the token file) and resumes when that succeeds. Each probe uses a little usage;
     the owner approves this with the batch;
   - leaves a gap between runs (for example 2 minutes) and logs one line per event (time, project,
     result, cost);
   - stops cleanly between runs when a `STOP` file exists in the folder;
   - retries a non-limit failure at most twice, then marks it `failed` with the reason;
   - removes stopped containers and networks between runs; `docker ps -a` after any interruption.
2. **Keep the owner's daytime usage free:** once the pilot shows the cost, propose a start time (for
   example evening) and a cap on runs per window. The owner decides.
3. **On resume in a new chat session:** read `queue.tsv`, `run_queue.log` and `round12-opus/README.md`
   first; never rerun a `done` row.

## Open points to raise with the owner

- DevEval projects are public, some as real packages (`lice`, `readtime`, `hone`, `geotext`, `chakin`);
  Opus may know them, so a pass is not proof the spec was enough. TRIAL §6.3 lists a test (ask for the
  code from the project name alone).
- The 12 C/C++, Java and JavaScript projects are a later round: they need repackaging (Harbor's tasks
  leave the tests readable in `/app`, TRIAL §3) and a per-test scorer (Harbor scores each suite as one
  pass or fail).
- The licence for redistributing DevEval material in the repository is unchecked (`evidence/README.md` §4).
