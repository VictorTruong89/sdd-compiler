# Trials: one folder per trial, everything needed to continue it

> Made 2026-10-14 (owner's request after round 12): run different trials in different folders, keep all
> intermediate files there, and keep a Markdown file that describes the test. Round 12 predates this
> kit and lives in `../benchmarks/devbench-2024/round12-opus/` with the same layout.

## Layout

```
harness/trials/
  README.md            this file
  TRIAL_TEMPLATE.md    the description template
  new_trial.sh         make a trial folder:  bash new_trial.sh <id> "<question>"
  run_queue.sh         unattended driver:    nohup bash run_queue.sh <id> >> <id>/run_queue.log 2>&1 &
  summarize.py         results:              python3 summarize.py <id>
  watchdog.sh          cron keeper:          */10 * * * * bash watchdog.sh <abs trial dir>  (restarts a dead
                       driver, resets an interrupted `running` row, runs <id>/notes/watchdog_hook.sh)
  <id>/
    TRIAL.md           question, design, inputs, checks, runs, results, findings, open items
    trial.env          run conditions (Claude Code version, $ ceiling, timeout)
    queue.tsv          run_id, task, model, status, job, attempts, last_message
    run_queue.log      one line per event
    runs/<run_id>/     saved files of each run
    results.json       built from runs/
    notes/             trial-specific notes and scripts (task builders, classifications)
    work/              NOT tracked: tasks with hidden tests, Harbor jobs, compile store, third-party copies
```

## Rules

- **Model runs need the owner's go-ahead.** The driver uses the subscription token from
  `~/.config/sdd-compiler/claude-oauth.env` (sourced, never printed); `ANTHROPIC_API_KEY` is unset.
- **Never rerun a `done` row.** To repeat, add a new row with a new `run_id`.
- The driver stops the queue if the token string appears in a job folder; it waits out usage limits
  (reset time from the message, or a one-turn Haiku probe every 30 minutes); `touch <id>/STOP` stops it
  between runs.
- The driver logs the subscription's usage after each run (5-hour and 7-day windows, from Claude
  Code's `rate_limit_event`) and pauses new runs at 0.90 / 0.95 of them until the window resets.
- On resume in a new session: read `<id>/TRIAL.md`, `queue.tsv` and `run_queue.log` first.
- `work/` holds third-party material whose licence may not allow redistribution; it stays out of git.
  What is needed to rebuild it is written in `TRIAL.md` ("Inputs").

## Trials

| Id | Question | State |
|---|---|---|
| `r13-zero2repo-case004` | Zero2Repo case004: Haiku and Sonnet, Markdown and spec-graph export, 2 runs each | closed 2026-10-14: 7 / 8 at 258 / 258; the miss is a false-positive contradiction in the export; with the 18 settled, Haiku 2 / 2 at 258 |
| `r13b-zero2repo-haiku-sweep` | Which Zero2Repo cases does Haiku fail from the Markdown? (8 Python/Node cases, n = 1) | closed 2026-10-14: fails case010 (166 / 197; 146 / 177 scorable, corrected 2026-10-16), case006 (464 / 476), case016 (370 / 388); passes the other 5 |
| `r13c-zero2repo-3cases` | case010, 006, 016: Haiku and Sonnet, Markdown and export, 2 runs each (24); watchdog in cron | closed 2026-10-16: no test-level gain from the settled export (Haiku case006: 2 gains, 3 losses); Haiku 63–87 turns on export against 33–47; 20 case010 tests unscorable (model files missing from Zero2Repo's Harbor output) |
