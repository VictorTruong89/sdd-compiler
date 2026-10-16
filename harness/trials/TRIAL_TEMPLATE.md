# {{ID}}

> Opened {{DATE}}. State: **planned** (planned / running / paused / closed). Approved by the owner: *(quote
> and date)*. Update this file at every step; it is the description a later session starts from.

## Question

{{QUESTION}}

## Design

| Item | Value |
|---|---|
| Benchmark / case | |
| Formats | |
| Models | |
| Runs per cell (n) | |
| Agent | Claude Code (version in `trial.env`), Harbor, tools `Bash Edit Read Write`, network allow-list |
| Ceiling | `BUDGET_USD` in `trial.env` per run |
| Scorer | |

## Inputs (how each was made; commands)

## Checks before model runs (no model)

## Runs

Queue in `queue.tsv`; log in `run_queue.log`; files per run in `runs/<run_id>/`; table built by
`python3 ../summarize.py .` into `results.json`.

## Results

## Findings

## Open items

## Files

| Path | Tracked | What |
|---|---|---|
| `TRIAL.md` | yes | This description |
| `trial.env` | yes | Run conditions read by `../run_queue.sh` |
| `queue.tsv`, `run_queue.log` | yes | Queue state, driver log |
| `runs/<run_id>/` | yes | `result.json`, reward and report files, junit, `app.tgz` (agent's code), `agent.tgz` (transcript, trajectory) |
| `results.json` | yes | Built by `../summarize.py` |
| `notes/` | yes | Working notes, classifications, scripts specific to this trial |
| `work/` | **no** | Tasks (with hidden tests), Harbor jobs, compile store, third-party copies |
