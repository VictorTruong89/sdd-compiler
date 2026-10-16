# r13-zero2repo-case004

> Opened 2026-10-14. State: **closed 2026-10-14** (8 runs, then 2 follow-up runs on a settled export, owner's go-ahead "go ahead with option 1"). Approved by the owner 2026-10-14: "move on a new round to try
> setting up Zero2Repo and test 1 prominent, suitable case. Use haiku and sonnet, test both plain
> markdown and spec-graph 2 times each." Update this file at every step; it is the description a later
> session starts from.

## Question

On a benchmark whose hidden tests are written against the stated interface (Zero2Repo), does the
spec-graph export change what Haiku and Sonnet build compared with the plain Markdown specification?
Secondary: does Zero2Repo avoid DevEval's fault (tests that need details the specification does not
give, round 12)?

## Design

| Item | Value |
|---|---|
| Benchmark / case | Zero2Repo (`../../benchmarks/zero2repo/TRIAL.md`), commit `0ecc523`, **case004 "Signtoken"**: built from `pallets/itsdangerous` at `672971d`, names neutralised |
| Why this case | prominent upstream (Pallets); Python, like all earlier rounds; mid-size spec (PRD 3 665 + contract 1 483 + hardware 222 = 5 370 words, 2.5 times `lend`); 258 hidden tests in 4 feature files; Zero2Repo's own review file says passed |
| Formats | Markdown (the three public files) and the spec-graph export of the same three files |
| Models | Haiku (`anthropic/claude-haiku-5-5`) and Sonnet (`anthropic/claude-sonnet-5-5`) |
| Runs per cell (n) | 2 → 8 runs |
| Agent | Claude Code 2.1.296, Harbor 0.24.0, tools `Bash Edit Read Write`, agent network allow-list (model API, PyPI), $10 ceiling, 7 200 s agent timeout |
| Scorer | Zero2Repo's own judge unchanged (binary: all 258 or 0) as `official_reward`, plus the same test files run once more with junit for a per-test count (`reward.json`: `tests_passed / 258`) |
| Order | the four Markdown runs first, the four export runs after the compile (to save time); within each, Haiku and Sonnet alternate. A time-of-day difference between formats cannot be excluded |

## Inputs (how each was made; commands)

1. Zero2Repo cloned (`../../benchmarks/zero2repo/download/Zero2Repo`, shallow, `0ecc523`); its harness
   installed in `../../benchmarks/zero2repo/download/.venv`; `zero2repo-harbor --case-id case004 --force`
   wrote its own Harbor task to `.../benchmark/output/case004/`.
2. **Our task** (`notes/build_task.py`): spec files in `/app/spec/` instead of pasted into the
   instruction; Claude Code pinned instead of `@latest`; allow-list network; workspace saved as
   `app.tgz`; Zero2Repo's judge kept and a junit pass added. Tests are taken from the case source
   because **the adapter's task lacks `_harness.py` and `conftest.py`, which every test file imports**
   (found by the first check below).
   `python3 notes/build_task.py markdown work/tasks/case004-markdown`
   `python3 notes/build_task.py export work/tasks/case004-export work/compile/export` (after the compile)
3. **Compile** (`work/compile/`): `sddc init`; profile copied from `~/sddc-runs/deveval-lice` (Haiku via
   Claude Code, cap 300 calls, `mermaid`/`bash`/`json`/`yaml`/`text` fences are contracts); the three
   public files in `sdd/specs/`; ingest R-000001: 3 files, 192 blocks. Compile started 2026-10-14
   16:27 with `work/compile/run_compile.sh` (token sourced, no API key). Compiler `sddc 0.1.0.dev0` at
   repository commit `657b510` (uncommitted work on top).
   - Pass 1 (`compile-1.json`, 16:27–18:26): all 187 pending blocks formed, **381 nodes**, 19 empty
     blocks, 0 failed; stopped at the **300-call cap** with conflict judging incomplete (1 432 pairs
     judged, 55 unjudged); `cost_usd` 1.5676 (estimate).
   - Pass 2, resume (`N=2 bash run_compile.sh` → `compile-2.json`, 18:26–18:28): 8 calls, `cost_usd`
     0.0308; conflict judging complete, 0 unjudged. **18 contradictions**, 59 open conflict items in all.
   - Total: 308 calls, `cost_usd` 1.5984 (estimate), about 2 h.
4. **Export**: `sddc --json export --allow-open --out export` (as in the DevEval rounds: the 18
   contradictions have no human verdict and appear as UNSETTLED in `MAP.md`). 20 packs + `MAP.md` +
   `CHECKLIST.md` + `export.meta.json`: **32 759 words, 6.1 times** the 5 370 words of the Markdown.
   Checksums: `work/compile/export.sha256` (its sha256 `4cb69d7a…a939c2`).

5. **Settled export (follow-up)**: the store copied to `work/compile-settled/`; the 18 contradictions
   judged **false** with `sddc conflicts judge <id> --verdict false --note ...` (no model call; one
   line each in `notes/verdicts.tsv`, all "a rule and its stated exception/condition"). Verdicts by the
   agent on the owner's behalf after reading each pair against the specification. Export **without**
   `--allow-open`: same 20 packs, no UNSETTLED banner and no `CF-` id anywhere, **30 875 words**
   (`work/compile-settled/export.sha256`, its sha256 `9590e38e…45cff`). Task
   `work/tasks/case004-export-settled`.

## Checks before model runs (no model)

| Check | Job (`work/jobs/`) | Result |
|---|---|---|
| Do-nothing, adapter's test folder | `check-nop-markdown.adapter-tests` | 0 / 258; 8 collection errors |
| Upstream code, adapter's test folder | `check-upstream.adapter-tests` | 0 / 258: `ModuleNotFoundError: _harness` → adapter fault found |
| Do-nothing, fixed task | `check-nop-markdown` | **0 / 258**, official 0 |
| Upstream code (itsdangerous `672971d`, package renamed `signtoken`) | `check-upstream` | **246 / 258**, all 258 collected, official 0 |
| Do-nothing, export task | `check-nop-export` | **0 / 258**, official 0 |
| Do-nothing, settled export task | `check-nop-export-settled` | **0 / 258**, official 0 |

The 12 tests upstream fails all assert the `reason` attribute ("missing" / "malformed") that the
Interface Contract adds to `BadTimeSignature` and upstream does not have. So the hidden tests follow the
stated contract, not the original code, and a build from the specification can reach 258. No reference
solution ships with Zero2Repo; this upstream check stands in for one.

## Runs

Queue in `queue.tsv`; log in `run_queue.log`; files per run in `runs/<run_id>/`; table built by
`python3 ../summarize.py .` into `results.json`.

## Results

All per-test figures are passed of 258 hidden tests; `official` is Zero2Repo's binary judge; `$` is
Claude Code's `total_cost_usd`, an API-equivalent estimate on the subscription; time is Harbor's whole
run (`run_queue.log`). Source: `runs/<run_id>/reward.json`, `result.json`; table in `results.json`.

| Run | Tests | Official | Turns | $ est. | Time |
|---|---|---|---|---|---|
| haiku-markdown-1 | 258 | 1.0 (after rescore) | 26 | 0.0507 | 250 s |
| haiku-markdown-2 | 258 | 1.0 | 24 | 0.0494 | 249 s |
| haiku-export-1 | 258 | 1.0 | 75 | 0.5144 | 492 s |
| haiku-export-2 | **256** | **0** | 46 | 0.3863 | 376 s |
| sonnet-markdown-1 | 258 | 1.0 | 5 | 0.2331 | 96 s |
| sonnet-markdown-2 | 258 | 1.0 | 6 | 0.2136 | 93 s |
| sonnet-export-1 | 258 | 1.0 | 7 | 0.2240 | 92 s |
| sonnet-export-2 | 258 | 1.0 | 6 | 0.2466 | 103 s |
| haiku-settled-1 | 258 | 1.0 | 35 | 0.1670 | 313 s |
| haiku-settled-2 | 258 | 1.0 | 20 | 0.0726 | 261 s |

Runs total $1.9181 est.; the compile adds $1.5984 est. (308 Haiku calls, about 2 h) once per
specification.

In short: Markdown 4 / 4 at 258; export 3 / 4 at 258. With Haiku the export cost about 8 to 10 times
the Markdown and 2 to 3 times the turns; with Sonnet the two formats are the same within noise.
n = 2 per cell, one case.

Follow-up (settled export, Haiku): 2 / 2 at 258; 20–35 turns, $0.07–0.17 est. Settling the false
contradictions removed the failure and cut Haiku's cost by about 2.3 to 7 times against the
unsettled export; it remains above Markdown (1.4 to 3.4 times the estimate, 20–35 turns against
24–26). Follow-up total $0.2396 est.

## Findings

- **The one failure was caused by a false-positive contradiction.** `haiku-export-2` failed
  `test_replaced_out_of_range_time_field_is_malformed_not_expiry` and
  `test_runtime_replaced_out_of_range_time_field_is_malformed` (got time-signature failure, expected
  malformed timestamp). The specification is unambiguous (`Full_PRD.md` line 153: a time-signature
  failure whose time field cannot be represented "is a malformed timestamp instead"). The compiler
  split that sentence into a rule (N-000221 / N-000220) and its exception (N-000223), judged them
  contradictory (CF-000034, CF-000044), and the export showed both as UNSETTLED. The agent wrote its
  own resolution, "A verified token whose time is unrepresentable is refused as malformed. An
  unverified token keeps its time-signature failure", which is the wrong side. Both Haiku export
  runs read these ids (24 and 28 mentions in their transcripts); run 1 resolved them correctly.
  The Markdown runs, which saw the sentence whole, never failed it.
- **Settling the contradictions fixed it.** With the 18 judged false and the export made without
  `--allow-open`, both Haiku runs passed 258 / 258 and cost far less (table above). So the unsettled
  conflict list itself, not the size of the export, drove most of Haiku's extra turns and the failure.
  n = 2; not shown on other cases.
- **Export cost with Haiku.** The 32 759-word export (6.1 times the Markdown) plus the
  checklist ("account for every id") took Haiku 46–75 turns against 24–26, and about 8–10 times the
  estimated cost. Sonnet was not affected (6–7 turns either way).
- **Zero2Repo does avoid DevEval's fault on this case**: upstream code misses only contract-added
  behaviour (246 / 258), and every model in both formats reached 256–258 from the specification
  alone. But the case is too easy to separate formats (ceiling).

- Zero2Repo's Harbor adapter (commit `0ecc523`) leaves out the test support files for case004; its
  own judge would score every submission 0 ("pytest execution was incomplete"). Worth reporting
  upstream (outward-facing: owner's decision).
- **Second adapter fault**: the adapter rewrites the manifest's `test_command` to absolute
  `/tests/final/...` paths, and the judge then appends the same files again, so every test is collected
  twice (516 items), the judge's collection audit fails, and `official_reward` is 0 for any build. Found
  on `haiku-markdown-1` (258/258 per test, official 0). Fixed in `notes/build_task.py` (the case's own
  manifest, relative paths); `haiku-markdown-1` rescored from its saved `app.tgz` with
  `notes/rescore.sh` (oracle agent, no model) → official **1.0** (`runs/haiku-markdown-1/rescore/`).
  The later runs used the fixed task.
- **Ceiling on Markdown**: all four Markdown runs pass 258/258. The format comparison can only show a
  difference if the export runs fall below that; it cannot show an export gain on this case.
- **Possible recall**: no transcript names `itsdangerous`, but the agents chose upstream's module names
  (`exc.py`, `url_safe.py`, `signer.py`, `serializer.py`, `encoding.py`), none of which the
  specification gives. Zero2Repo neutralises names but cannot hide a well-known library's shape.
- **Compiler on a clean specification**: 18 contradictions detected in a benchmark spec that its own
  review marks consistent and that a build satisfies in full. Report saved in `notes/conflicts.txt`
  (`sddc conflicts`). On a first reading, most pair a general rule with an exception the specification
  states (e.g. "the signature length follows the digest size" against "NoneAlgorithm's signature is
  empty"; "unsafe load returns a pair" against "it raises on a payload-decode failure"). A
  per-conflict verdict is *to be done*; until then these are likely false positives, and the export
  shows all 18 to the agent as UNSETTLED.

## Open items

- The 18 verdicts were given by the agent; the owner may review `notes/verdicts.tsv`.
- Compiler: a rule and its stated exception in one sentence (or adjacent bullets) should not be judged
  a contradiction. A candidate for the rel02 brainstorm.
- A harder Zero2Repo case (larger contract, less famous upstream) to get below the ceiling.
- Report the two adapter faults to Zero2Repo (outward-facing: owner's decision).

## Files

| Path | Tracked | What |
|---|---|---|
| `TRIAL.md` | yes | This description |
| `trial.env` | yes | Run conditions read by `../run_queue.sh` |
| `queue.tsv`, `run_queue.log` | yes | Queue state, driver log |
| `runs/<run_id>/` | yes | `result.json`, `reward.json`, `official_reward.json`, `final_report.json`, `junit-final.xml`, `pytest.out`, `app.tgz` (agent's code), `agent.tgz` (transcript, trajectory) |
| `results.json` | yes | Built by `../summarize.py` |
| `notes/build_task.py` | yes | Our task builder for this case |
| `notes/rescore.sh` | yes | Rescore a saved `app.tgz` with the fixed task (oracle agent, no model) |
| `notes/conflicts.txt` | yes | `sddc conflicts` report of the compile (18 contradictions) |
| `notes/verdicts.tsv` | yes | The 18 verdicts (all false) and their one-line reasons |
| `work/` | **no** | Tasks (with hidden tests; Zero2Repo has no licence file), Harbor jobs and checks, compile store and export, upstream clone |
