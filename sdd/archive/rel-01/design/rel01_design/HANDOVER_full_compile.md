# Handover — the full-corpus test session

> **Tier:** design, non-authoritative · **Written:** 2026-09-22 · **For:** a fresh Claude Code session.
> Paste §1 as the opening prompt. Everything the session needs is in this repository.

---

## 1. The prompt to paste

```text
You are continuing the SDD Compiler (rel01). Read these first, in order:

  CLAUDE.md                                    the working agreement and the house rules
  sdd/design/rel01_design/build-plan.md        §3 gate protocol · §7 progress · §8 issues · §9 what remains
  sdd/design/rel01_design/M4-gate.md           §6 the options, §7 the dogfood that preceded this run
  sdd/design/rel01_design/G4-measurement.md    §2 what M1, M2 and M7 mean — read the M7 caveat carefully
  sdd/design/rel01_design/HANDOVER_full_compile.md   this file, for the run procedure (§2 … §6)

YOUR TASK: compile this repository's own `sdd/specs/` end to end — ingest, atomize, retrieve, judge,
report — and produce the one number the 30 September close is about (G4 §5): how many conflicts the
compiler reports on our own specs, and how many a human judges real.

This is roughly 733 blocks, ~850 model calls and several hours. It will NOT finish in one run, and it
is not supposed to: run it in resumable slices, checkpointing after each (§3). A run that stops on a
session limit is a checkpoint, not a failure — the judgment lock means nothing is paid for twice.

HARD CONSTRAINTS — read these twice:

1. **Claude Code subscription only. Never consume Anthropic API tokens.** Keep the profile's
   `atomizer.backend: claude-code` and `pass_api_key: false`. Never set ANTHROPIC_API_KEY, never
   switch to the `anthropic-api` backend, never add an API key to a `.env`. If a step seems to need
   an API key, stop and ask the owner.
2. **Never run `git commit`, `git push`, or `git add`.** The owner reviews and commits (CLAUDE.md).
3. **Work in a durable directory, never /tmp.** A scratch store was cleared mid-measurement once and
   the results were lost (build-plan I-50). Use `~/sddc-runs/full-corpus/`.
4. **Every `$` figure is an estimate, not spend** (build-plan I-82, G4 §2): it is Claude Code's own
   `total_cost_usd` summed per call — the equivalent API list price. These runs are on the owner's
   subscription; no organization credits move. Write "estimated API-equivalent", never "cost".
5. **The pass line is already fixed — do not reinterpret it.** The owner confirmed it on
   2026-09-22, before the run, which is gate protocol step 1 (build-plan §3):

   > **"The compile completes with a clean store, and at least a quarter of a sampled hundred
   > conflicts are judged real."**

   Operationally, both must hold: (a) `pending` 0, `conflicts.unjudged` 0, `incomplete` false, and
   `check_store` clean; (b) **≥ 25 of 100** sampled conflicts judged real. If fewer than 100 are
   reported, judge them all and the bar is a quarter of that number. Draw the sample **before**
   reading any record, with a seeded random draw over every reported conflict, and write the seed
   into the write-up. You adjudicate; the owner confirms; the verdict stands on the owner's
   confirmation. ⚠ On 181 blocks of these same specs the rate was ≈ 10 % (I-81), so this bar is
   demanding on this corpus — report the number you get, never a reading that reaches it. Since
   then F6 D19 suppresses two of I-81's shapes in code (a criterion against its own spec, one block
   against itself); contradictions between criteria describing different situations are still
   reported, and are the known remaining false-positive class.

Start by confirming the suite is green (`python -m pytest -q` → 623 passed), then follow §2 of the
handover file. Report after each round; do not start a new round without saying what the last one did.
```

---

## 2. Setting the run up (once)

```bash
mkdir -p ~/sddc-runs/full-corpus && cd ~/sddc-runs/full-corpus
mkdir -p sdd && cp -r /home/victor/Workspace/sdd-compiler/sdd/specs sdd/specs
(cd sdd/specs && find . -name '*.md' | sort | xargs sha256sum) > corpus.sha256   # I-69: pin the corpus
export SDDC=/home/victor/Workspace/sdd-compiler/src
PYTHONPATH=$SDDC python -m sdd_compiler init
PYTHONPATH=$SDDC python -m sdd_compiler ingest --json | tee ingest.json
```

**Copy the corpus; do not compile the working tree in place.** The specs change while they are being
measured — that is I-69, and it is what made R16 not the controlled comparison it was launched as.
The hash file is what lets the write-up say which text produced these numbers.

Then set the round size in `.sdd/profile.yaml`:

```yaml
atomizer:
  max_calls_per_run: 200      # one round ≈ 200 calls; raise only if rounds finish easily
```

A cap is the checkpoint mechanism: the run stops cleanly at exit `5`, having written everything it
finished, and the next round replays it for free.

## 3. The round loop

```bash
N=1   # increment each round
PYTHONPATH=$SDDC timeout 7200 python -m sdd_compiler compile --json > round-$N.json 2> round-$N.err
echo "exit=$?"
```

After each round, record and report:

```bash
python - <<'PY'
import json, glob
d = json.load(open(sorted(glob.glob('round-*.json'))[-1]))
c = d.get('conflicts', {})
print({k: d[k] for k in ['run','pending','completed','failed','empty_blocks','nodes_formed',
                         'model_calls','cost_usd','replayed','stopped']})
print({k: c.get(k) for k in ['candidates','pairs_judged','pairs_replayed','unjudged','unjudged_failed',
                             'suppressed','opened','open','incomplete','stopped']})
print('stop reason:', (d.get('stop_reason') or c.get('stop_reason') or '')[:200])
PY
cp round-$N.json /home/victor/Workspace/sdd-compiler/sdd/design/rel01_design/measurements/R18_round$N.json
```

**Read the exit code as a state, not a verdict:**

| Exit | Meaning | Do |
|---|---|---|
| `0` | Finished, no conflicts open | Go to §5 |
| `3` | Finished, conflicts open | Go to §5 |
| `5` | The call cap ended the round — **expected, this is the checkpoint** | Start the next round |
| `6` | The backend stopped it. Read the message: "session limit" means the subscription's daily/weekly window | Wait for the reset it names, then start the next round |
| `2`/`4` | An input or store error — a real defect | Stop, diagnose, log it as an issue |

**The run is done when** `pending` is 0, `conflicts.unjudged` is 0 and `incomplete` is false.

**Why resuming is free** (verify it, do not take it on faith — `pairs_replayed` and `replayed` in the
round summary should climb while `model_calls` stays proportional to the *new* work):

- every accepted answer is in `.sdd/lock/` and replays by content hash (F3 §4.7, D21);
- a cap (`5`) or backend (`6`) stop writes finished chunks **and** their lock records (F3 D24, proven
  live at I-71 and I-79);
- one unusable answer is re-asked per item, never fatal (F3 D37).

## 4. Watch for these (all have history in build-plan §8)

| If you see | It is | Do |
|---|---|---|
| A round with many `unjudged_failed` | Pairs whose answer failed its checks twice | Record the count; it is a finding, not a bug to fix mid-run |
| `empty_blocks` rising | Blocks that formed no node — headings and legends are fine (F3 D33) | Check a few; if a *rule* formed nothing, that is a finding |
| `annotations_dropped` | F3 D35 working | Record the count |
| An unhandled traceback | A defect: severity was misjudged (I-67, I-72, I-79 were all this) | Stop, log it, fix test-first, restart the round |
| `suppressed` climbing | F6 D19 (and D16) working: a criterion against its own spec, or two claims of one block, judged `duplicates`/`subsumes` | Record the count; it is the size of what D19 removed |
| The same conflict shape repeating | Probably I-81's open half: two criteria (or a criterion and prose) describing **different situations** read as a contradiction — exit `0` vs exit `5` | Count it; do not hand-fix |

## 5. When the compile completes

1. **Store integrity:** `check_store` must be clean, and `sddc status` should agree with the report.
2. **The report:** save `sddc compile`'s printed report and `sddc conflicts` output into
   `measurements/R18_report.txt` and `R18_conflicts.txt`.
3. **M2 (precision) — the number the close is about.** Adjudicate with the real command, which is what
   T19 built it for:
   `sddc conflicts judge CF-000123 --verdict real|false --note "…"`.
   With hundreds of records, **adjudicate a stated sample**, not an impression: every contradiction,
   plus a seeded-random sample of the rest. Report "N real of M judged, sampled from K reported" —
   a metric without its sample size is not publishable (G4 §2).
4. **Fix what it finds.** The dogfood found a real defect in F5 made the same day (I-80). Anything real
   in our specs gets fixed in the working tree — that is the product doing its job.
5. **Write it up** in `M4-gate.md` §8, with: the corpus hash, blocks/nodes/pairs/conflicts, M1 if any
   planted pairs are involved, M2 with its sample, estimated API-equivalent usage, wall time, how many
   rounds it took, and every issue found (continue the numbering from I-82).
6. **Update the records:** build-plan §7 (progress), §8 (issues and patterns), §9 (what remains), and a
   new session entry in `rel01_brainstorm.md`. Leave the working tree uncommitted.

## 6. What to expect (extrapolated from the dogfood — 181 blocks, build-plan I-81, F6 D19)

| | Dogfood (measured) | Full corpus (expected) |
|---|---|---|
| Blocks · nodes | 181 · 192 | 733 · ≈ 800 |
| Candidate pairs · judge calls | 587 · 144 | ≈ 3 000 · ≈ 400 |
| Model calls total | 271 | ≈ 850 |
| Estimated API-equivalent | $6.32 | **≈ $26** |
| Conflicts reported | 70 → **43** with D19 (27 suppressed, re-applied to the stored run) | ≈ 150–190 — *extrapolated from one corpus* |
| Rounds at `max_calls_per_run: 200` | — | **4–6** |

⚠ These are extrapolations from one corpus. Report what actually happens, including where the
expectation was wrong — that is worth as much as the number itself.
