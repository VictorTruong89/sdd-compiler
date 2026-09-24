# M4 gate — does the compiler find real conflicts, and do people believe them?

> **Tier:** design, non-authoritative · **Opened** 2026-09-21 · Run under the gate protocol in
> [`build-plan.md`](build-plan.md) §3. M4 is the release: M1–M3 without it produce a graph nobody can
> act on.

## 1. Pass line — written 2026-09-21, before the run finished

⚠ Written and committed to the file **while the compile was still running**, so it could not be bent
to the result. This is the protocol's step 1, which the M3 gate failed to satisfy (M3-gate §4).
**Owner: confirm or replace before reading §3.**

| # | Condition | Why this line |
|---|---|---|
| **G1** | The compiler reports **at least 4 of the 6 planted pairs**, and P1 is among them | P1 is a plain same-spec contradiction in two units of the same sentence pattern; missing it would mean the product does not do its one job |
| **G2** | Of everything reported, **at least half is judged real** by a human (M2) | Below half, the report trains you to ignore it — E2 in G4 §1 |
| **G3** | The run finishes, the store passes its own checks, and the report names every conflict with file and line | The report is the product's only surface (E5) |

**Not in this line, deliberately:** cost, run time, and the share of `ambiguous` nodes. They are
recorded in §3 as measurements, not as conditions — M3 already showed the atomizer's grouping is the
weak part, and re-litigating it here would stop a release for something M4 cannot fix.

## 2. Corpus, pinned

`tests/fixtures/planted/`, 3 files, ~725 words, 28 blocks. Written 2026-09-21 in the voice of ordinary
specs (G4 §3's warning: planted conflicts must not look planted). The answer key — six pairs, P1 … P6 —
is [`tests/fixtures/planted/EXPECTED.md`](../../../tests/fixtures/planted/EXPECTED.md).

Hashes of the compiled corpus (I-69: a measurement on a moving corpus is not a comparison):

```text
60a0dfc1dede84a4d6a01cb8ff754273ff6a7c9b37f12a1c61af06d1364d3baa  F1_exports/sharing.md
25749aab944aab3f7fd42fab29d6990b02e54f9dea8e55d925e83f074f858682  F1_exports/spec.md
94ef8764beabed3166f99407e781c1194879bc3c3e8be1e738c49035fbb7ae5c  F2_retention/spec.md
```

**Model:** `claude-code` + Haiku, thinking off. **Date:** 2026-09-21.

## 3. Results — 2026-09-21

Raw output: [`measurements/M4_fixture_compile.json`](measurements/M4_fixture_compile.json),
report [`measurements/M4_fixture_report.txt`](measurements/M4_fixture_report.txt), adjudications
[`measurements/M4_fixture_adjudications.jsonl`](measurements/M4_fixture_adjudications.jsonl).

**The whole product ran end to end for the first time:** ingest → atomize → retrieve → judge → write
→ report. 28 blocks → 34 nodes → 123 candidate pairs → 72 judged → 11 conflicts, store checks clean.

| | |
|---|---|
| Blocks · completed · failed · formed no node | 28 · 28 · 0 · 4 |
| Nodes · attention items | 34 · 3 |
| Candidate pairs · judged · failed twice · **left unjudged** | 123 · 72 · 1 · **50** |
| Verdicts | 45 none · 10 depends_on · 6 contradicts · 5 refines · 4 subsumes · 2 duplicates |
| Conflicts opened (3 groups) | **11** — 6 contradiction, 2 duplication, 3 subsumption |
| Model calls · cost · exit | 93 · **$1.30** · 5 (should have been 6, I-72) |

⚠ **The run stopped early.** A backend 429 (the account's session limit) ended the check phase after
72 of 123 pairs, and the phase reported it as the call cap — with 93 of 200 calls used. Fixed after the
run as **I-72**: the check phase now records which limit stopped it, the report names it, and a backend
stop exits `6`, not `5`.

### M1 — conflict recall: **1 of 6 planted pairs**

| Planted | Reported? | Rank among candidates | What fired |
|---|---|---|---|
| **P1** 30 days vs 7 days | ✅ **CF-000001**, and again via `AC-2.1` as CF-000005 | **1** of 137, score 10.5 | S1, S2, S4, S5, S6 |
| P6 shared link vs 7-day removal | ✗ | 81 | S5 only, 1.5 |
| P2/P5 5 GB vs 5 GiB | ✗ | 123 | S5 only, 1.0 |
| P4 every MUST vs nightly SHOULD | ✗ | 128 | S5 only, 1.0 |
| P3 never contain the owner's email vs the manifest lists it | ✗ | 130 | S5 only, 1.0 |

**Every planted pair was proposed as a candidate — none of the five misses was invisible to
retrieval.** They were ranked 81st to 130th of 137 and the run stopped at 72. And they ranked there for
one reason: **each side of those pairs uses a different term for the same thing**, so the two strongest
sources cannot fire.

| Pair | A's family / terms | B's family / terms |
|---|---|---|
| P2/P5 | `export_archive` | `null` · `workspace_export`, `size_limit` |
| P3 | `export` | `manifest_json` · `member_email`, … |
| P4 | `export` | `null` · `nightly_backup_export` |

S1 (same family, 3.0) and S2 (shared term, 2.0) are dead on all three; only S5's keyword overlap fires,
at exactly `min_score`. **This is the measured cost of M3's finding** (I-65: 97 terms for 64 nodes, a
name per phrasing). The M2 gate warned that families are the backbone of retrieval; M4 puts a number on
it: *of the conflicts this compiler missed, none was missed by the judge — all were missed by naming.*

### M2 — precision: **3 of 11 judged real (27 %)**

Adjudicated with `sddc conflicts judge` (T19), which is what that command exists for. **Reader: Claude;
owner confirms.**

| Verdict | Records | Why |
|---|---|---|
| **real** | CF-000001, CF-000005 | P1, reached directly and through its acceptance criterion |
| **real** | **CF-000003** | The one-year audit retention is stated twice, in §2.2 and §2.4. **Not planted** — an accident in the fixture's own prose that the answer key missed and the compiler found |
| false ×4 | CF-000004, CF-000007, CF-000006, CF-000010 | Two clocks that are consistent by design: a 24-hour link inside a 30-day archive; a 13-day restore inside a 14-day window. The judge reads "different numbers" as "conflict" |
| false ×3 | CF-000008, CF-000011, CF-000002 | A rule and its own consequence, or an acceptance criterion restating its requirement. Design, not defect |
| false ×1 | CF-000009 | "day 30 versus day 31" — arithmetic the judge invented; both claims describe a 30-day life |

**The one genuinely encouraging result:** CF-000003 is a real duplication that nobody planted and the
author of the fixture did not notice. The product did its job on prose written to be consistent.

**The pattern in the false positives** is one mistake, made five times: *two different numbers about
related objects are not a contradiction unless both must hold for the same object at the same time.*

## 4. Verdict — **the M4 gate fails**, against the pass line in §1

| | Condition | Result |
|---|---|---|
| **G1** | ≥ 4 of 6 planted pairs, P1 among them | ❌ **1 of 6** (P1 found) |
| **G2** | ≥ half of what is reported judged real | ❌ **3 of 11 (27 %)** |
| **G3** | The run finishes, the store checks pass, the report names every conflict with file and line | ⚠ **Partly.** The store is clean and the report is good; the run stopped early on a 429 and mislabelled why (I-72, fixed) |

**What this gate establishes, which is worth more than a pass would have been:**

1. **The machine works.** Every stage ran, on prose nobody wrote for it, and produced a clean store, a
   readable report and a real find the fixture's author had missed.
2. **The failure is in ranking, not in judging.** All six planted pairs were proposed. Five ranked
   below 80 because the atomizer gave each side its own name.
3. **The precision failure is one prompt-sized mistake**, repeated: different numbers ≠ contradiction.
4. **The cost model does not reach this repository.** 28 blocks cost $1.30 and 93 calls with a third of
   the pairs unjudged. `sdd/specs/` is 733 blocks — roughly 25–40× — so G4's "one number for the close"
   (conflicts on our own specs) is **not affordable on the `claude-code` backend** at ≈ $0.014 per call.

### Recommended next, for the owner to decide

| # | What | Size | Why now |
|---|---|---|---|
| **R15** | **Term hygiene for retrieval**: let Q-TERM merge phrasings of one thing (`export archive` / `workspace export`), or add a source that fires on *same quantity dimension without a shared term* | medium | It is the direct cause of 5 of 6 misses. The second option alone would have caught P2 and P4 |
| **R16** | **One prompt rule for Q-PAIR**: two numbers are a contradiction only when both must hold for the same object at the same time; otherwise `none` | small | Would have removed 5 of the 8 false positives |
| **R17** | Re-run this gate after R15 and R16, with the cap raised so all 123 pairs are judged | ≈ $2 | The current numbers are a floor: 50 pairs were never judged |
| **R18** | Decide the close-out number: either the `anthropic-api` backend (rel01 D30's plan) for the full-repo compile, or close rel01 with the fixture as the measured corpus and say so | owner | 9 days to 30 September |


---

## 5. R17 — the gate re-run with R15 and R16 (2026-09-21)

**A controlled comparison this time.** The three files are byte-identical to §2's hashes; only the code
changed (F5 D11, F6 D15) and the call cap was raised to 400 so every pair could be judged. Raw output:
[`measurements/R17_compile.json`](measurements/R17_compile.json),
[`measurements/R17_report.txt`](measurements/R17_report.txt),
[`measurements/R17_adjudications.jsonl`](measurements/R17_adjudications.jsonl).

| | M4 gate | **R17** |
|---|---|---|
| Nodes formed · blocks forming none | 34 · 4 | 31 · 6 |
| Candidate pairs · **judged** · unjudged | 123 · 72 · **50** | 159 · **159** · **0** |
| Conflicts reported | 11 | **7** |
| **M1 recall** (planted pairs found) | 1 of 6 | **2 of 6** (P1, **P4**) |
| **M2 precision** (judged real) | 3 of 11 (27 %) | **5 of 7 (71 %)** |
| Model calls · cost · exit | 93 · $1.30 · 5 | 177 · **$2.35** · **3** |
| Store checks | clean | clean |

**Precision more than doubled.** The false positives R16 targeted are gone: no more 24-hour link
against 30-day archive, no more 13-day restore against a 14-day window, no invented arithmetic. Two
remain — an acceptance criterion judged a duplication of its own requirement (the one R16's prompt
explicitly names, so the rule did not take), and a rule paired with its own instance.

**Recall moved 1 → 2 of 6, and the diagnosis is now complete.** Every planted pair's fate is known:

| Planted | Rank | Judged? | Outcome |
|---|---|---|---|
| **P1** 30 d vs 7 d | 1 | yes | ✅ found — and twice more from other angles (CF-000003, CF-000004), all real |
| **P4** MUST vs SHOULD | — | yes | ✅ **found** (CF-000007). R15 did not touch it; judging every pair did |
| P6 shared link vs 7 d | 42 | **yes** | ❌ `none`: *"A specifies the expiration of shared links, while B specifies the removal of export archives"* |
| P2/P5 5 GB vs 5 GiB | 63 | **yes** | ❌ `none`: *"the two claims govern different export types ('export archive' vs 'workspace export')"* |
| P3 email | 179 | no | Never reached: below `max_pairs_per_node` |

### The finding that matters

**The naming problem has moved from retrieval into the judge.** R15 did its job — P2/P5 went from rank
123 to 63 and P6 from 81 to 42, both were delivered to the judge, and the judge refused them *in those
words*: they "govern different export types". The two claims say `export archive` and `workspace
export`, and the model reads two objects where the spec means one.

So the same defect now costs at three stages, and it is the same defect M3's blind readings kept
finding: **the atomizer coins a name per phrasing** (I-65 → I-73 → this). It is the release's single
biggest quality lever, and no amount of retrieval tuning reaches it — a pair the judge is *told* about
is still refused.

**P3 remains the one true retrieval miss:** two claims with no shared quantity and no shared term, one
about "an export" and one about "manifest.json", sitting 179th. Only keyword overlap connects them.

### Against the pass line (§1)

| | Condition | M4 gate | R17 |
|---|---|---|---|
| **G1** | ≥ 4 of 6 planted, P1 among them | ❌ 1 | ❌ **2** |
| **G2** | ≥ half of what is reported judged real | ❌ 27 % | ✅ **71 %** |
| **G3** | Run finishes, store clean, every conflict located | ⚠ stopped early | ✅ **complete, exit 3** |

**Two of three.** G2 and G3 pass; **G1 still fails**, and it fails for one reason that is now measured
rather than suspected. ⚠ The adjudications are Claude's, as at M3 — **owner confirms**.

**Cost, for the close:** 28 blocks, complete, $2.35 and 177 calls — $0.076 per block. This repository's
`sdd/specs/` is 733 blocks, so a complete compile of our own specs is ≈ **$55 and some hours** on the
`claude-code` backend. That is R18's decision, and it is now a measured number rather than an estimate.


---

## 8. The full-corpus run — pass line, fixed 2026-09-22 before the run

> Recorded **before** any of this run's output exists — gate protocol step 1 (build-plan §3), the step
> the M3 gate failed (M3-gate §4). Procedure: [`HANDOVER_full_compile.md`](HANDOVER_full_compile.md).

**Owner's pass line, confirmed 2026-09-22:**

> *"The compile completes with a clean store, and at least a quarter of a sampled hundred conflicts
> are judged real."*

| # | Condition | Measured by |
|---|---|---|
| **F1** | The compile **completes**: `pending` 0, `conflicts.unjudged` 0, `incomplete` false | the last round's summary |
| **F2** | The store is **clean**: `check_store` reports nothing | `check_store(.sdd)` |
| **F3** | **≥ 25 of 100** sampled conflicts judged **real** (all of them, and a quarter of them, if fewer than 100 are reported) | `.sdd/adjudications.jsonl` (F6 AC-6.20) |

**Sampling:** a seeded random draw over every reported conflict, made **before** any record is read,
with the seed recorded. Claude adjudicates; the owner confirms; the verdict stands on the owner's
confirmation.

⚠ **This is a demanding bar on this corpus, knowingly set.** The same specs at 181 blocks scored
≈ 10 % (M4-gate §7, I-81), and the cause is known: 65 of 70 conflicts there involved an acceptance
criterion or a decision entry — the documents' own structure. Passing F3 without fixing I-81 would be
a surprise; failing it while the machine works is the expected outcome, and is worth recording as
precisely as a pass.

### Results — the compile (2026-09-22 19:47 → 2026-09-23 23:46)

**Corpus:** `sdd/specs/` copied to `~/sddc-runs/full-corpus/` and hashed before the run
(`corpus.sha256`), identical at the end: **9 files, 845 blocks** — not the 733 of the M1 gate; the
specs grew in between (I-69).

```text
360390f261dfcf48d72924ef2e4ec64dda27e06598f393d7ae9161f2ec53ed34  ./constitution.md
bb2f1596037e4559cc5f32c46aa35f0d7551c454adc748a30bc951398eb95132  ./F1_ingest/spec.md
dcbdfecbf508687609569a103347f6d11521654bc8d7ec6afb5064ac4e2ddf36  ./F2_node_model/spec.md
0bac0f9f019008e02049136547bceaf799c595d4e117548ed1d108f8eb9f7c51  ./F3_atomizer/spec.md
3913b4b6977ae194fbf09eda9bb63d168353897cfbf6b960b3478fe36205b3dc  ./F4_graph_store/spec.md
577b59979b9e958e403ae64d908dc8fb50643c0dbb77b060fca8df32b1c04a2b  ./F5_retrieval/spec.md
59c651d395a40c8b93c2426fb0dc5467e98b049e5e9526f06089ce378e0c148a  ./F6_conflicts/spec.md
738109e7ff65a0743a3f5c2790040c62c86305e927c4c6b33e32490b3fdc7a1c  ./README.md
0b49e91f42d6368f94662576c0c3c4c192e80c2a4ec5c97a101cd2ab9e8e02cd  ./vision.md
```

**Model:** `claude-code` + Haiku, thinking off, on the owner's subscription. No API key was set or
used at any point. Raw output in [`measurements/`](measurements/): `R18_round1 … 16.json`,
`R18_round7_crash.err`, `R18_report.txt`, `R18_conflicts.txt`, `R18_sample.txt`.

| | Handover expected (§6) | **Measured** |
|---|---|---|
| Blocks · nodes | 733 · ≈ 800 | **845 · 950** (304 `ambiguous`, 451 `conflict`, 195 `validated`) |
| Candidate pairs · verdicts | ≈ 3 000 · — | **4 268** at the widest round (R-000010) **· 4 251** (2 854 none · 425 subsumes · 396 depends_on · 306 refines · 167 contradicts · 103 duplicates) |
| Conflicts reported | ≈ 150–190 | **381 open** — 167 contradiction, 157 subsumption, 57 duplication, in 95 groups |
| Rounds | 4–6 | **16** — 10 call cap, 5 session limit, 1 complete |
| Model calls · estimated API-equivalent | ≈ 850 · ≈ $26 | **2 673 · ≈ $54.94** (I-87) |
| Compile wall time | — | **9.05 h** over 28 h elapsed |

⚠ **Every `$` is Claude Code's own `total_cost_usd`, summed per call — an estimate of the equivalent
API list price, not money billed** (G4 §2, I-82). The 2-minute run that crashed (I-83) wrote nothing,
its usage included.

**Three defects found by the run and fixed test-first mid-run** (build-plan I-83, I-85, I-86; suite
623 → 628). Each would have made the number below wrong:

- **I-83** — the judgment-id counter was saved before the check phase, so round 7 re-issued ids the
  lock already held and crashed; `check_store` had been blind to that counter.
- **I-85** — a check phase stopped by the cap marked every node checked, silently dropping its
  unjudged pairs; round 7 then reported the compile **complete** with 1 866 pairs never judged. The
  store was recovered (406 nodes' `last_checked_run` cleared through `write_graph`; backup kept) and
  every judged pair replayed from the lock at no cost.
- **I-86** — `ambiguous` nodes never proposed pairs of their own (44 % of the graph). Fixing it took
  the candidate pairs from 2 418 to 4 268, and is most of why the conflict count and the cost are
  twice the estimate.

⚠ **The dogfood (§7) had I-86 too**, so its 70 conflicts on 181 blocks were an undercount.

### Against the pass line

| # | Condition | Result |
|---|---|---|
| **F1** | `pending` 0, `conflicts.unjudged` 0, `incomplete` false | ⚠ **`unjudged` 0 and `incomplete` false; `pending` is 1** — one block, B-000243 (F2 D12's `*Rejected:*` sentence), fails G3 on every retry (I-84; six others cleared on retry). Strictly **not met**; owner to rule whether one unatomizable block of 845 fails the line |
| **F2** | `check_store` clean | ✅ **clean** — with the counters check that now covers `judgment` (I-83) |
| **F3** | ≥ 25 of 100 sampled conflicts judged real | ⬜ **pending adjudication.** Sample drawn 2026-09-24: `random.Random(20260922).sample(sorted open ids, 100)` — seed = the pass-line date, fixed before drawing; population 381; ids in `measurements/R18_sample.txt`. ⚠ Disclosure: the first ~19 records of group 1 were displayed while saving `R18_conflicts.txt`, before the draw; the draw is mechanical and the seed was chosen a priori, so this cannot steer which records are sampled |

*(M2 — adjudication of the 100, then the owner's confirmation.)*

---

## 6. R18 — what it is, what it costs, and the cheaper ways to the same number

### What R18 is

**One `sddc compile` over this repository's own `sdd/specs/`, with the check phase, start to finish.**
It is the last item in G4 §5: *"the one number for the 30 September close: conflicts reported on this
repository's own spec set, and how many of them a human judged real."* Everything measured so far —
R12, R15, R16, R17 — was either atomization only, or the 28-block planted fixture.

### What it is for

1. **The release's headline claim.** rel01's purpose (vision §2) is finding conflicts in a real spec
   set. Six specs, 126 acceptance criteria, written over two weeks by a human and an AI *is* the real
   spec set, and it is the one the owner can judge.
2. **It is the honest corpus.** The fixture's conflicts were planted by the person reading the results.
   Our own specs were not written to be found.
3. **Conflicts found are worth having.** Anything real it reports is a defect in this project's specs,
   today — not a metric.
4. **M7 and M8 at scale**: cost per node and injection rate on 733 blocks rather than 28.

### What it costs, extrapolated from R17 (28 blocks — state the sample, G4 §2)

| | R17 | `sdd/specs/` |
|---|---|---|
| Blocks · nodes | 28 · 31 | 733 · ≈ 800 |
| Judged pairs | 159 | ≈ 4 800 |
| Model calls | 177 | ≈ **5 000** |
| Cost at ≈ $0.0135 per call | $2.35 | ≈ **$55 – 70** |
| Wall time at 5–8 s per call | ≈ 25 min | ≈ **7 – 11 hours** |

**Why per-call, not per-token:** a headless Claude Code call carries ≈ 22k tokens of harness prompt
whatever it asks (I-8). Cost is set by *how many calls*, and the check phase makes one per pair.

⚠ A 7–11 hour run crosses several session-limit windows. It survives them (F3 D24, proven at I-71),
but it needs restarting each time.

### The case against spending it now

- **It buys a number, not an improvement.** The quality ceiling is already known and measured: the
  atomizer names one thing several ways, which costs at retrieval *and* at judging (I-76). A full
  compile would mostly re-measure that, 26× more expensively.
- **9 days remain.** $60 and a day of babysitting is a large share of what is left.
- **It is not needed to close.** A close-out may report a measured corpus and say which one it was.

### Four things that reach the same place for less — in the order they should be done

| | What | Effort | What it changes |
|---|---|---|---|
| **A** | **Batch Q-PAIR**, as rel01 D30 already did for Q-ATOM and Q-DESC: 8 pairs per call instead of 1 | ~1 day | Calls fall ≈ 8×. The full compile becomes ≈ **$8 and ~1 hour**. It is the same lever that made atomization affordable, applied to the phase that now dominates |
| **B** | **Tune `min_score` / `max_pairs_per_node`** — measured offline on R17's store, free: `min_score: 2.5` cuts 184 pairs → **97**, and `max_pairs_per_node: 4` cuts them to **86**, with all four known-real pairs kept in both | minutes | Roughly halves the cost of every future run. ⚠ Judged on 4 real pairs in one 31-node store: a direction, not a setting to adopt blind |
| **C** | **A sampled dogfood**: compile one real spec (F5, 71 blocks ≈ $6) or a stratified 100-block sample across all six (≈ $8), and report the number *with its sample size* | hours | Gives a real "conflicts in our own specs" figure, which is what the close needs, at a tenth of the price |
| **D** | **The `anthropic-api` backend** (rel01 D30's plan; `llm/anthropic_api.py` exists, 65 lines, barely tested) | ~½ day + an API key | Removes the harness overhead entirely — the per-call floor drops to real tokens |

**Recommended:** **B now** (free), then **A**, then **C** as the close-out number — with the full R18
run only if A lands and the money is then trivial. Recorded for the owner; not started.


---

## 7. C — the dogfood: two real specs of this repository (2026-09-22)

The first compile of **our own prose**. Corpus: `F5_retrieval/spec.md` + `F6_conflicts/spec.md`,
**181 blocks**, chosen because they cross-reference each other constantly, so a real conflict was
plausible. Hashes: `b91fcc5e…` (F5), `6d1e6c7f…` (F6). Raw output in
[`measurements/`](measurements/): `C_dogfood_compile.json`, `C_dogfood_report.txt`,
`C_dogfood_adjudications.jsonl`.

| | |
|---|---|
| Blocks pending · completed · failed · formed no node | 154 · **142** · 12 · 23 |
| Nodes · attention items | **192** · 22 |
| Candidate pairs · judged · failed twice · suppressed (D16) | 587 · **562** · 25 · 3 |
| Verdicts | 384 none · 50 depends_on · 40 refines · 37 subsumes · **29 contradicts** · 22 duplicates |
| **Conflicts opened** | **70** — 29 contradiction, 21 duplication, 20 subsumption |
| Model calls · cost · exit | 271 · **$5.93** (+ $0.39 for the run I-79 cut short) · 3 |
| Store checks | clean |

⚠ **Every `$` here is Claude Code's `total_cost_usd`, summed per call — an estimate of the equivalent
API list price, not money billed** (G4 §2, I-82). These runs ran on the owner's Claude subscription:
no organization credits were drawn, and nothing appears in the Usage & Cost Admin API.

⚠ **Cost was 3× my estimate** ($2). Two things I had not counted: the atomize side needs ≈ 0.8 calls
per block (Q-DESC batches of 8 *atoms*, plus Q-TERM), and **25 pairs failed their first answer**, each
costing a re-ask — 144 judge calls for 73 batches.

### M2 — precision on a **sample of 39 of the 70** (all 29 contradictions + 10 others drawn at random)

**4 real, 35 false — ≈ 10 %.** Reader: Claude; owner confirms. The four:

| | What it found |
|---|---|
| **CF-000013** | F5 **D6** says `max_pairs_per_node: 10`; **D13**, written the same day, says 6 |
| **CF-000047** | F5 **§4.3** still says "the top `max_pairs_per_node` (default 10)" |
| **CF-000038** | **AC-5.10**'s prose hardcodes `max_pairs_per_node: 10` |
| **CF-000001** | F5 **§4.1** says both "a `stale` node needs checking" and "nodes unchanged since their `last_checked_run` are skipped", without saying which wins — the implementation had to decide, and did (T15) |

**The first three are one real defect in three places, and I introduced it hours earlier**: D13 changed
the default and three other passages kept the old number. *The compiler found its author's own mistake
in its own specification, the same day it was made.* That is the product doing exactly what vision §2
promises, on prose nobody wrote for it. **CF-000001** is a genuine under-specification, found by
reading two sentences of one paragraph against each other.

### Why the other 35 are false — one dominant class

**65 of the 70 conflicts involve an acceptance criterion or a decision entry.** Spec documents have a
structure the compiler does not know:

- an **acceptance criterion restates the requirement it verifies** — design, not duplication. F6 D16
  suppresses exactly this, and did so 3 times; it only fires when `verifies` resolved, and on this
  corpus most criteria cite nothing;
- a **decision's heading summarises its own body** ("D11 — S2 follows `broader`…" against the sentence
  below it), which reads as duplication or subsumption;
- **two criteria describing different situations** (exit `0` when clean, exit `5` when the cap is hit)
  read as contradictory.

**The lever is the same one M3 and the M4 gate both pointed at, from a third side:** the compiler needs
what the document's own form already says. `verifies` when a criterion cites its rule (built, F2 D13),
and the same idea for a decision heading and its body.

### What this means for the close

- **The product works end to end on real specs**, and found a real defect its own author had just made.
- **Precision on our own corpus is ≈ 10 %** against 71 % on the fixture — because our specs are dense
  with criteria and decisions, and the fixture was plain prose. ⚠ *Both numbers are Claude's reading of
  a sample; the owner's confirmation is what G4 asks for.*
- **Cost, measured:** an estimated **$6.32 of API-equivalent usage** for 181 blocks with the check
  phase — **$0.035 per block**, after R20 and R21. The whole repository (733 blocks) is ≈ **$26** at
  this rate, not the $12 I projected from the fixture: our own specs form more pairs per block than
  plain prose does. The 238 lock records that carry usage sum to $5.61; the rest of the $6.32 is calls
  whose usage is recorded once per batch, plus the run I-79 cut short. **Token shape:** 992 uncached
  input tokens against **5.78 M cache reads** and 394 K output — the harness prompt, re-read once per
  call. That is I-8's finding, still true after every optimisation: the call count is the cost.
