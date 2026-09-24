# 2. Quick start

## What you need

- **Python ≥ 3.11** with `PyYAML`, `markdown-it-py` and **`jsonschema`**. ⚠ `pyproject.toml` declares
  only the first two, but the code imports `jsonschema` (build-plan I-90), so install it yourself.
- **Claude Code** installed and logged in (`claude` on your `PATH`). The default backend runs every
  model question through it, on your Claude subscription. No API key is needed or wanted: the child
  process has `ANTHROPIC_API_KEY` removed unless the profile says `pass_api_key: true`.

```bash
cd /path/to/sdd-compiler
pip install -e . jsonschema # installs the `sddc` command (jsonschema: see I-90)
# or, without installing:  PYTHONPATH=src python -m sdd_compiler <command>
```

## The six commands rel01 ships

| Command | Does | Calls the model? |
|---|---|---|
| `sddc init` | Creates `.sdd/` and a default `.sdd/profile.yaml` | no |
| `sddc ingest` | Splits the spec files into blocks only | no |
| `sddc compile [PATH…]` | Ingest → atomize → check → write → print the report | **yes** |
| `sddc status` | Sources, blocks, pending work, node counts by status | no |
| `sddc family NAME` | One family's card: its nodes by layer, constraints in scope, related families | no |
| `sddc conflicts` | Every open conflict, grouped | no |
| `sddc conflicts judge CF-000123 --verdict real\|false --note "…"` | Records a human verdict in `.sdd/adjudications.jsonl` | no |

Global flags: `--json` (machine-readable output, before or after the command), `--root DIR`
(defaults to the nearest parent containing `.sdd/`). `compile --no-replay` asks the model again even
where the lock holds an answer — you rarely want it.

Deferred to a later release (they are specified, not built): `review`, `query`, `map`, `check`,
`blocks`, `show`, `pairs`, `check-conflicts`, exhaustive retrieval.

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

## The profile (`.sdd/profile.yaml`) — the only file you edit in `.sdd/`

| Key | Default | Meaning |
|---|---|---|
| `spec_globs` / `exclude_globs` | `sdd/specs/**/*.md` / `_templates/**` | Which files are specs |
| `include_code_blocks` | `false` | Fenced code is stored, not atomized |
| `atomizer.backend` | `claude-code` | Or `anthropic-api` (exists, barely tested) |
| `atomizer.model` | `haiku` | The model for **all four** questions |
| `atomizer.pass_api_key` | `false` | Keep `ANTHROPIC_API_KEY` out of the child |
| `atomizer.max_calls_per_run` | `200` | One budget shared by atomizing and judging |
| `atomizer.timeout_s` | `120` | Per call |
| `atomizer.thinking` | `false` | Extended thinking off: it tripled cost on small questions (F3 D10) |
| `retrieval.max_pairs_per_node` | `6` | How many candidate pairs one node may propose |
| `retrieval.min_score` | `1.0` | A pair below this score is dropped |
| `retrieval.min_shared_keywords` | `2` | For source S5 |
| `conflicts.judge_ambiguous` | `true` | Judge vague nodes too (verdicts marked provisional) |
| `conflicts.subsumption_conflict_only_when_differing` | `true` | "All requests logged" ⊇ "logins logged" is design, not a conflict — unless modality or amount differ |
| `weak_words` | fast, quickly, appropriate, … | Words that flag a claim `vague_term` |
| `layers` | `{}` | Display names and heading hints only — the layers themselves are fixed |

An unknown key is rejected (exit `4`) rather than ignored: a typo must not fall back to a default.

## Exit codes — read them as a state, not a verdict

| Exit | Means | What to do |
|---|---|---|
| `0` | Finished, no conflicts open | Nothing |
| `1` | Usage error (bad flag) | Fix the command |
| `2` | Input error (a spec file, a path) | The message names the file |
| `3` | Finished, conflicts open | Read the report — this is the normal outcome on real specs |
| `4` | Store or profile error | The message names every problem; the store was not changed |
| `5` | The call cap stopped the run | **Expected on a big corpus.** Everything finished is written; run `compile` again |
| `6` | The backend stopped it (e.g. the subscription's session limit, a 429) | Wait for the reset the message names; run again |

## Big spec sets: compile in rounds

A compile of 845 blocks needed 2 673 model calls (R18). With `max_calls_per_run: 200` that is many
runs, and **that is by design**: each run stops cleanly at the cap, writes what it finished, and the
next run replays every finished answer from the lock for free. A loop is enough:

```bash
until sddc compile --json > last.json; code=$?; [ $code -eq 0 ] || [ $code -eq 3 ]; do
  [ $code -eq 5 ] || [ $code -eq 6 ] || { echo "stop: exit $code"; break; }
  [ $code -eq 6 ] && sleep 3600       # a session limit: wait for the reset
done
```

The run is complete when `pending` is 0, `conflicts.unjudged` is 0 and `conflicts.incomplete` is
false in the `--json` summary.

## Recording what a human thinks of a conflict

The compiler proposes; a person decides.

```bash
sddc conflicts judge CF-000043 --verdict false \
  --note "F1 is one component; the telemetry rule is about the components that do call the model"
```

Each verdict is appended to `.sdd/adjudications.jsonl`, never overwritten, and tied to the judgment it
answered. If the pair is judged again later, the old human verdict is marked stale, not carried
forward. Precision ("how many reported conflicts are real") is counted from this file.
