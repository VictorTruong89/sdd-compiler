# Round 12: Claude Opus on the nine Python DevEval projects (Markdown only)

> Opened 2026-10-14 at commit `657b510` (uncommitted work on top). Asked by the owner; scope and the
> three awkward projects decided by the owner the same day (handover
> `sdd/design/rel-02/rel02_handover_round12.md`). Filled in as runs land.

## Purpose

1. Which projects have hidden tests the specification states (class S), and does the strongest model
   pass them? Per project: S tests stated, S tests passed.
2. A benchmark: Opus's score per project and in total on DevEval as repackaged here (n = 1 per project;
   say so in every reading).

## Conditions

| Item | Value |
|---|---|
| Model | `anthropic/claude-opus-5-5`, through Claude Code 2.1.296 in Harbor, owner's subscription (no API key) |
| Tools | `Bash`, `Edit`, `Read`, `Write` (the round-11 disallow list) |
| Network | agent phase: model API and PyPI only (`allowlist`); verifier: public |
| Ceiling | `max_budget_usd=10` per run |
| Input | the four original DevEval Markdown documents in `spec/`, plus seed files. No compile, no export |
| Tasks | `download/clean/<project>-markdown/`, built by `build_clean_task.py … markdown … --claude-version 2.1.296 --agent-network allowlist`. Six rebuilt 2026-10-14 (round-8 scorer); `lice`, `arxiv-digest`, `stocktrends` are the round 8–11 tasks, a fresh build of each is identical (`diff -r`) |
| Scorer | `tests/test.sh`: workspace saved as `app.tgz`, agent's own test folders set aside, hidden tests run per folder with `--confcutdir`; reward accepted only when tests collected ≤ hidden tests |
| Test classes | `../test-classification.json`, all 143 tests classified **before** any Opus run (`classification/README.md`) |
| `$` | Claude Code's `total_cost_usd`: an estimated API-equivalent on the subscription, never spend |

## Hidden tests and reference checks (no model)

Rebuilt tasks checked with Harbor's `oracle` (reference) and `nop` (do-nothing) agents, jobs
`download/jobs/r12-{oracle,nop}-<project>`.

| Project | Hidden tests | S | U | R | C | Reference | Do-nothing |
|---|---|---|---|---|---|---|---|
| readtime | 12 | 2 | 0 | 10 | 0 | 12 / 12 | 0 |
| chakin | 2 | 0 | 0 | 2 | 0 | 2 / 2 | 0 |
| particle-swarm-optimization | 6 | 6 | 0 | 0 | 0 | 6 / 6 | 0 |
| geotext | 9 | 5 | 3 | 1 | 0 | 9 / 9 | 0 |
| stocktrends | 9 | 2 | 5 | 2 | 0 | 9 / 9 (round 8) | 0 (round 8) |
| hybrid-images | **20** | 3 | 14 | 1 | 2 | **12 / 20** (same 8 fail as round 6) | 0 |
| hone | 12 | 11 | 1 | 0 | 0 | 12 / 12 | 0 |
| lice | 31 | 3 | 3 | 25 | 0 | 31 / 31 (round 11) | 0 (round 11) |
| arxiv-digest | 42 | 28 | 7 | 6 | 1 | 42 / 42 (round 9) | 0 (round 9) |
| **all** | **143** | **60** | **33** | **47** | **3** | | |

`hybrid-images` has 20 hidden tests, not 19: the builder's count missed the acceptance test named
`test` (fixed in `build_clean_task.py`). The reference fails 8 of them, listed in
`classification/README.md`; it is scored on all 20 and on the 12 the reference passes.

## Files

| Path | What |
|---|---|
| `queue.tsv` | One row per project: status `pending / running / done / limited / failed`, job, attempts, last limit or failure message |
| `run_queue.sh` | The unattended driver (plain bash, no Claude session). See "Running" |
| `run_queue.log` | The driver's log, one line per event (written when the owner starts it) |
| `runs/<project>/` | `result.json` (Harbor trial), `reward.json`, `pytest.out`, `junit-*.xml`, `app.tgz` (the agent's code), `agent.tgz` (the job folder with `claude-code.txt`, `trajectory.json`, session transcript, `verifier/`; without `.claude.json`, settings, shell snapshots, backups, setup) |
| `make_results.py` → `results.json` | One record per project, built from `runs/` only: passed by class, accepted flag, turns, agent time, cost; `hybrid-images` on both bases |
| `classification/` | Method notes and doubtful calls; per-project class inputs and `add_classes.py` |

## Running (only with the owner's go-ahead: model calls)

```bash
cd harness/benchmarks/devbench-2024/round12-opus
nohup bash run_queue.sh --one > run_queue.log 2>&1 &    # pilot: the first pending row (readtime)
nohup bash run_queue.sh      >> run_queue.log 2>&1 &    # the rest, one at a time
touch STOP                                               # stop cleanly between runs
```

The driver takes the next `pending` or `limited` row, runs Harbor inside `timeout`, stops the whole
queue if `sk-ant-oat01` appears in the job folder, copies the run files, and marks the row. A run that
does not finish cleanly is checked for a usage-limit message (agent result, Harbor exception, the
tails of `claude-code.txt` and Harbor's output); the exact message goes into `queue.tsv` and the log,
the partial job is kept as `<job>.limited-<time>`, and the driver sleeps until the reset time in the
message, or probes with a one-turn Haiku call every 30 minutes when no time is given. Other failures
are retried twice, then marked `failed`. Between runs: a 2-minute gap and removal of Harbor's stopped
containers and networks (names `<task>__<id>__…` only).

**On resume in a new session:** read `queue.tsv`, `run_queue.log` and this file first; never rerun a
`done` row.

## Results (8 of 9 run; round wrapped up temporarily 2026-10-14)

One Opus run per project (**n = 1**), Markdown only, 2026-10-14 08:11–08:47 local time, through
`run_queue.sh` with no limit hit and no failure. `readtime` (the proposed pilot) was **held**: the owner
approved "the remaining 8". Figures from `results.json` (built by `make_results.py`); pairs are passed /
tests in class.

| Project | All | S | U | R | C | Turns | Agent time | Cost, est. |
|---|---|---|---|---|---|---|---|---|
| chakin | 2 / 2 | – | – | 2 / 2 | – | 8 | 54.2 s | $0.2046 |
| particle-swarm-optimization | 6 / 6 | 6 / 6 | – | – | – | 4 | 35.1 s | $0.1199 |
| geotext | 9 / 9 | 5 / 5 | 3 / 3 | 1 / 1 | – | 8 | 49.9 s | $0.1984 |
| stocktrends | 7 / 9 | 2 / 2 | 3 / 5 | 2 / 2 | – | 9 | 127.6 s | $0.4641 |
| hybrid-images | 17 / 20 | 3 / 3 | 14 / 14 | 0 / 1 | 0 / 2 | 8 | 424.2 s | $0.1757 |
| hone | 12 / 12 | 11 / 11 | 1 / 1 | – | – | 7 | 87.8 s | $0.3384 |
| lice | 6 / 31 | 3 / 3 | 3 / 3 | 0 / 25 | – | 7 | 105.6 s | $0.3863 |
| arxiv-digest | 32 / 42 | 27 / 28 | 5 / 7 | 0 / 6 | 0 / 1 | 7 | 69.5 s | $0.2547 |
| **8 projects** | **91 / 131** | **57 / 58** | **29 / 33** | **5 / 37** | **0 / 3** | | | **$2.1420** |

`hybrid-images` on the 12 tests the reference passes: 9 / 12 (S 1 / 1, U 8 / 8, R 0 / 1, C 0 / 2). Opus
passes all 8 tests the reference fails. `lice`: the unit-test file could not be collected
(`ImportError`, `valid_year`), recorded as a collection error, not a test; 6 tests collected.

Markdown runs of the same tasks by other models (TRIAL §9–§11, register): `lice` Haiku 3, Sonnet 6;
`arxiv-digest` Haiku 22, 27, 28, Sonnet 29; `stocktrends` Haiku 3, Sonnet 4; `hone` Sonnet 12 (pilot, old
scorer).

## Findings (one reader, from `results.json`, junit files and the saved code)

1. **Stated tests are solved:** S 57 / 58. The miss is one `arxiv-digest` S test (not yet read).
2. **R passes come from recall of the public packages, not from the specification.** All 5 R passes
   are in projects published as packages, and Opus wrote names the specification never gives, exactly
   as upstream has them: `chakin` imports `urlretrieve` from `six.moves.urllib.request`; `geotext` has
   `Index = namedtuple('Index', 'nationalities cities countries')` and `self.index`; `stocktrends` has
   `UPTREND_CONTINUAL` and `roundit(self, x, base=5)`. Haiku and Sonnet passed no R test in any round.
   So on DevEval a high Opus score partly measures memory of the original repositories (TRIAL §6.3);
   the transcripts do not say so explicitly (searched for "original", "upstream", "I recall": none).
3. **Where the package is not known or the test is unreachable, R stays at 0:** `lice` 0 / 25 (the
   missing `valid_year` stops the whole unit file), `arxiv-digest` 0 / 6, `hybrid-images` 0 / 1.
4. **C tests: 0 / 3.** Opus followed the specification where a test contradicts it (`hybrid-images`
   width/height, `arxiv-digest` `max_results`).
5. **Cost:** $0.12 to $0.46 est. per project; 4 to 9 turns.

## Open items (round 12 is paused, not closed)

- `readtime`: held; run it only with the owner's go-ahead.
- `arxiv-digest`: 10 failures; the live-service check (rerun the saved code from the host against arXiv,
  as in round 11) is not done, so network versus code is not separated yet.
- Read the one missed S test and the U misses (`stocktrends` 2, `arxiv-digest` 2).
- Write-up into TRIAL §12, register, brainstorm and report §R2: a short §12 stub exists; the rest is open.

## Archive (everything needed to revisit, in this folder)

| Path | What |
|---|---|
| `runs/<project>/` | The run: Harbor trial `result.json`, `reward.json`, `pytest.out`, `junit-*.xml`, `app.tgz` (agent's code), `agent.tgz` (job folder with transcript and trajectory) |
| `runs/.harbor-<project>.out` | Harbor's console output for the run |
| `tasks/<project>-markdown.tgz` | The nine clean tasks as run (spec, seed, hidden tests, `test.sh`; reference left out — rebuild with `build_clean_task.py`) |
| `checks/r12-{oracle,nop}-<project>.tgz` | The reference and do-nothing jobs of step 2 (six projects) |
| `queue.tsv`, `run_queue.log` | Queue state and the driver's log |
| `results.json`, `make_results.py` | Results, rebuilt from `runs/` |
| `classification/` | Class notes and inputs; classes in `../test-classification.json` |

Every file and archive member was searched for the token string after copying: none found.
DevEval material inside (`tasks/`, `checks/`) has unchecked redistribution terms (`../evidence/README.md` §4).
