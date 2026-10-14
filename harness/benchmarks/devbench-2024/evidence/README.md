# Evidence: everything behind the DevEval runs (rounds 5–11)

> Saved 2026-10-14 at commit `a4e7d94` (uncommitted work on top) so the runs can be debugged and
> revisited without `download/` or `~/sddc-runs/`, which are not tracked. No token: every file and
> every archive member was searched for `sk-ant-` after copying; none found.

## 1. What is here

| Path | What | Copied from |
|---|---|---|
| `compile/<project>/` | The whole compile store: `.sdd/` (blocks, nodes, edges, conflicts, terms, runs, profile, lock files with every model call), `sdd/specs/` (the four DevEval documents compiled), `export/` (**the spec-graph export the agent read**), `export.sha256`, `compile-1.json` (the compiler's summary; not for `hone`) | `~/sddc-runs/deveval-<project>/` |
| `tasks/<project>-<format>.tgz` | The clean Harbor task as it stands now: `instruction.md`, `task.toml`, `environment/` (Dockerfile, seed files, `spec/`), `tests/` (hidden tests, `test.sh`). The reference solution is left out (rebuild with `build_clean_task.py`) | `download/clean/<project>-<format>/` |
| `agent-logs/<job>.tgz` | One Harbor job: `result.json`, `config.json`, `job.log`, and the trial folder with `agent/claude-code.txt`, `agent/trajectory.json`, the agent's raw session transcript (`agent/sessions/projects/`), `trial.log` and `verifier/` (reward, junit, pytest output, pip log, `app.tgz` from round 8 on) | `download/jobs/<job>/` |

Left out of `agent-logs`, as not needed and possibly personal: the agent's `.claude.json`, settings,
shell snapshots, backups and setup logs. The run-level scores, rescored where the scorer changed, stay
in `../round7/` to `../round11/`; `agent-logs/` keeps them as they were at run time.

## 2. Which export each run read

The export inside each task is byte-identical to the one in `compile/` (checked 2026-10-14 by hashing
every file in both trees), and the three round-7 exports still match `../round7/<project>-export.sha256`.

| Project | Export tree hash (sha256 of the sorted file hashes, first 12) | Compile | Export size (`export.meta.json`) |
|---|---|---|---|
| lice | `efecf8d05c4c` | R-000002: 58 nodes, 27 empty blocks, 43 model calls, $0.2158 est. | 16 packs, 58 checklist items |
| arxiv-digest | `97ece82e75e5` | R-000002: 55 nodes, 26 empty blocks, 46 model calls, $0.2286 est. | 12 packs, 55 checklist items |
| stocktrends | `67c46d8e27cf` | R-000002: 66 nodes, 35 empty blocks, 55 model calls, $0.2623 est. | 12 packs, 66 checklist items |
| hone | `c92e404cd983` | see TRIAL §7: 61 nodes, $0.2685 est. | 16 packs, 61 checklist items |

## 3. Runs

Scores: hidden tests passed / total, from `../round*/<run>.reward.json` (the rescored figure for
round 8). `$` is Claude Code's `total_cost_usd`, an estimated API-equivalent on the subscription.

| Job (`agent-logs/`) | Model | Project, format | Passed | Run files |
|---|---|---|---|---|
| `pilot-hone-markdown-sonnet-1` | Sonnet | hone, Markdown | see TRIAL §7 | `../pilot-hone-markdown-sonnet-1.result.json` |
| `pilot-hone-export-sonnet-1` | Sonnet | hone, export | see TRIAL §7 | `../pilot-hone-export-sonnet-1.result.json` |
| `r7-lice-markdown-haiku-1` | Haiku | lice, Markdown | 3 / 31 | `../round7/` |
| `r7-lice-export-haiku-1` | Haiku | lice, export | 3 / 31 | `../round7/` |
| `r7-arxiv-digest-markdown-haiku-1` | Haiku | arxiv-digest, Markdown | 22 / 42 | `../round7/` |
| `r7-arxiv-digest-export-haiku-1` | Haiku | arxiv-digest, export | 30 / 42 | `../round7/` |
| `r7-stocktrends-markdown-haiku-1` | Haiku | stocktrends, Markdown | did not finish (TRIAL §9.3) | — |
| `r7-stocktrends-export-haiku-1` | Haiku | stocktrends, export | did not finish (TRIAL §9.3) | — |
| `r8-stocktrends-markdown-haiku-1` | Haiku | stocktrends, Markdown | 3 / 9 | `../round8/` |
| `r8-stocktrends-export-haiku-1` | Haiku | stocktrends, export | 3 / 9 | `../round8/` |
| `r9-arxiv-digest-markdown-haiku-2`, `-3` | Haiku | arxiv-digest, Markdown | 27, 28 / 42 | `../round9/` |
| `r9-arxiv-digest-export-haiku-2`, `-3` | Haiku | arxiv-digest, export | 30, 29 / 42 | `../round9/` |
| `r11-lice-markdown-sonnet-1` | Sonnet | lice, Markdown | 6 / 31 | `../round11/` |
| `r11-lice-export-sonnet-1` | Sonnet | lice, export | 6 / 31 | `../round11/` |
| `r11-arxiv-digest-markdown-sonnet-1` | Sonnet | arxiv-digest, Markdown | 29 / 42 | `../round11/` |
| `r11-arxiv-digest-export-sonnet-1` | Sonnet | arxiv-digest, export | 30 / 42 | `../round11/` |
| `r11-stocktrends-markdown-sonnet-1` | Sonnet | stocktrends, Markdown | 4 / 9 | `../round11/` |
| `r11-stocktrends-export-sonnet-1` | Sonnet | stocktrends, export | 3 / 9 | `../round11/` |

## 4. Caveats for revisiting

- **The task snapshots are the current builds, not the round-7 builds.** `test.sh` changed in round 8
  (workspace saved; agent-written tests set aside). The specification, seed files and hidden tests are
  copied unchanged from `download/deveval/` by the builder, and the exports match the round-7 checksums. The round-7 `test.sh` is inside each round-7 job's logs only as its output.
- **Round 7 kept no workspace** (`app.tgz` started in round 8). The code the round-7 agents wrote can
  be read from `agent/trajectory.json` (the `Write` and `Edit` calls).
- **Third-party material is inside:** `compile/*/sdd/specs/` and the task archives hold DevEval's
  documents and hidden tests. DevEval's licence terms for redistribution are not checked (TRIAL §6.3).
  Decide before pushing to a public remote.

## 5. Reading a run again

```bash
cd harness/benchmarks/devbench-2024/evidence
mkdir -p /tmp/look/app && tar -xzf agent-logs/r11-lice-export-sonnet-1.tgz -C /tmp/look
less /tmp/look/*__*/agent/claude-code.txt
tar -xzf /tmp/look/*__*/verifier/agent_files/app.tgz -C /tmp/look/app   # the agent's code
python3 ../score_by_class.py lice /tmp/look/*__*/verifier                # S/U/R/C split
```

To rescore offline, rebuild the task image from `tasks/<project>-<format>.tgz` and run `test.sh` as in
TRIAL §9.4 (method in `sdd/design/rel-02/rel02_methodology_notes.md`).
