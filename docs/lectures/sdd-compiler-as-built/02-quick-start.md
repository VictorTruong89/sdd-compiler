# 2. Quick start

## What you need

- **Python ≥ 3.11** (dependencies `PyYAML`, `markdown-it-py`, `jsonschema` — installed with the package).
- **Claude Code** installed and logged in (`claude` on your `PATH`). The default backend runs every
  model question through it, on your Claude subscription. No API key is needed or wanted: the child
  process has `ANTHROPIC_API_KEY` removed unless the profile says `pass_api_key: true`.

```bash
cd /path/to/sdd-compiler
pip install -e .            # installs the `sddc` command and its dependencies
# or, without installing:  PYTHONPATH=src python -m sdd_compiler <command>
```

## The seven commands that ship

| Command | Does | Calls the model? |
|---|---|---|
| `sddc init` | Creates `.sdd/` and a default `.sdd/profile.yaml` | no |
| `sddc ingest` | Splits the spec files into blocks only | no |
| `sddc compile [PATH…]` | Ingest → atomize → check → write → print the report | **yes** |
| `sddc status` | Sources, blocks, pending work, node counts by status | no |
| `sddc family NAME` | One family's card: its nodes by layer, constraints in scope, related families | no |
| `sddc conflicts` | Every open conflict, grouped | no |
| `sddc conflicts judge CF-000123 --verdict real\|false --note "…"` | Records a human verdict in `.sdd/adjudications.jsonl` | no |
| `sddc export [--out DIR] [--allow-open]` | Writes the agent export: `MAP.md`, one pack per unit, `CHECKLIST.md` (chapter 9) | no |

Global flags: `--json` (machine-readable output, before or after the command), `--root DIR`
(defaults to the nearest parent containing `.sdd/`). `compile --no-replay` asks the model again even
where the lock holds an answer — you rarely want it.

Specified but not built (rel01 close-out, "What did not ship"): `review`, `query`, `map`, `check`,
`blocks`, `show`, `atomize`, `check-conflicts`, `pairs --exhaustive`.

## A first compile, step by step

```bash
mkdir demo && cd demo && mkdir -p sdd/specs
cat > sdd/specs/sharing.md <<'EOF'
## Sharing

A share link must expire 30 days after it is created.

A share link must be revocable by its owner.
EOF
cat > sdd/specs/policy.md <<'EOF'
## Retention

Share links expire after 7 days.
EOF

sddc init          # → .sdd/ and .sdd/profile.yaml
sddc compile       # a few model calls; prints the report; exit 3 if conflicts are open
sddc conflicts     # the conflicts again, any time, without calling the model
sddc family "share link"
```

The expected shape of the outcome — **not a recorded run**; the model's exact wording varies — is one
`contradiction` between the 30-day and the 7-day claim, exit `3`.

## Then hand it to an agent

```bash
sddc export                      # exit 3: the contradiction has no human verdict yet
sddc conflicts judge CF-000001 --verdict real --note "7 days holds; fix sharing.md"
sddc export                      # → .sdd/export/MAP.md, packs/, CHECKLIST.md, export.meta.json
```

The export refuses to run while any contradiction has no current human verdict (the **conflict
gate**, F7 §4.6), because an agent handed an unsettled contradiction must guess. `--allow-open` writes
it anyway and marks each one `UNSETTLED:` in the packs. A `real` verdict is shown as `Settled:` with
your note, which is where you say which side holds. Chapter 9 explains the files.

## The profile (`.sdd/profile.yaml`) — the only file you edit in `.sdd/`

| Key | Default | Meaning |
|---|---|---|
| `spec_globs` / `exclude_globs` | `sdd/specs/**/*.md` / `sdd/specs/_templates/**` | Which files are specs |
| `include_code_blocks` | `false` | Other fenced code is stored, not atomized |
| `skip_headings` | `["Traceability"]` | Blocks under these headings are stored, never atomized, and left out of the export (F1 D14). `9. Traceability` matches: the section number is ignored |
| `contract_languages` | `json`, `yaml`, `text` | Fences in these languages are contracts: each forms one node, whole (F1 D15, F3 D39) |
| `atomizer.backend` | `claude-code` | Or `anthropic-api` (exists, barely tested) |
| `atomizer.model` | `haiku` | The model for **all four** questions |
| `atomizer.pass_api_key` | `false` | Keep `ANTHROPIC_API_KEY` out of the child |
| `atomizer.max_calls_per_run` | `200` | One budget shared by atomizing and judging |
| `atomizer.timeout_s` | `120` | Per call |
| `atomizer.thinking` | `false` | Extended thinking off: it tripled cost on small questions (F3 D10) |
| `retrieval.max_pairs_per_node` | `6` | How many candidate pairs one node may propose (F5 D13: 10 cost 58 % more pairs and found nothing more) |
| `retrieval.min_score` | `1.0` | A pair below this score is dropped |
| `retrieval.min_shared_keywords` | `2` | For source S5 |
| `retrieval.rare_keyword_share` | `0.01` | A keyword in at most this share of nodes is rare, for source S9 (F5 D16) |
| `conflicts.judge_ambiguous` | `true` | Judge vague nodes too (verdicts marked provisional) |
| `conflicts.subsumption_conflict_only_when_differing` | `true` | "All requests logged" ⊇ "logins logged" is design, not a conflict — unless modality or amount differ |
| `export.foundation_globs` | `**/vision.md`, `**/constitution.md` | Files whose blocks form pack `00`, read first. `[]` = none |
| `weak_words` | fast, quickly, appropriate, … | Words that flag a claim `vague_term` |
| `layers` | `{}` | Display names and heading hints only — the layers themselves are fixed |

An unknown key is rejected (exit `4`) rather than ignored: a typo must not fall back to a default.
Source: `src/sdd_compiler/profile.py` (`DEFAULT_PROFILE` and its template).

## Exit codes — read them as a state, not a verdict

| Exit | `compile` and the others | `export` (F7 CT-7.6) |
|---|---|---|
| `0` | Finished, no conflicts open | Export written |
| `1` | Usage error (bad flag) | `--out` is a non-empty folder that is not an export: nothing touched |
| `2` | Input error (a spec file, a path) | Sources changed since the last compile: run `sddc compile` first |
| `3` | Finished, conflicts open — **the normal outcome on real specs** | Unsettled contradictions and no `--allow-open`: the message lists them |
| `4` | Store or profile error; the store was not changed | Store check or coverage check failed: nothing written |
| `5` | The call cap stopped the run. **Expected on a big corpus.** Everything finished is written; run `compile` again | — |
| `6` | The backend stopped it (e.g. the subscription's session limit, a 429). Wait for the reset; run again | — |

## Big spec sets: compile in rounds

A compile of 845 blocks needed 2 673 model calls (R18); the 450-block R21 store needed 860. With
`max_calls_per_run: 200` that is many runs, and **that is by design**: each run stops cleanly at the
cap, writes what it finished, and the next run replays every finished answer from the lock for free.
A loop is enough:

```bash
until sddc compile --json > last.json; code=$?; [ $code -eq 0 ] || [ $code -eq 3 ]; do
  [ $code -eq 5 ] || [ $code -eq 6 ] || { echo "stop: exit $code"; break; }
  [ $code -eq 6 ] && sleep 3600       # a session limit: wait for the reset
done
```

The rel02 trials raise the cap instead (300 calls per pass for R21; methodology notes, row 174). The
run is complete when `pending` is 0, `conflicts.unjudged` is 0 and `conflicts.incomplete` is false in
the `--json` summary.

## Recording what a human thinks of a conflict

The compiler proposes; a person decides.

```bash
sddc conflicts judge CF-000043 --verdict false \
  --note "F1 is one component; the telemetry rule is about the components that do call the model"
```

Each verdict is appended to `.sdd/adjudications.jsonl`, never overwritten, and tied to the judgment it
answered. If the pair is judged again later, the old human verdict is marked stale, not carried
forward — and a stale verdict no longer satisfies the export's gate. Precision ("how many reported
conflicts are real") is counted from this file. `scripts/review_queue.py` writes every open conflict
to a CSV, sorted for adjudicating by hand (chapter 8).
