# 10. Trust, limits and cost

A tool that reports hundreds of conflicts is only useful if you know how far to believe it. This
chapter collects what has been **measured**, what has **not**, and what a run costs. Every number
carries its corpus and sample size; nothing here is extrapolated unless it says so.

## What has been measured

**Recall — how many planted conflicts the compiler reports**

| Corpus | Planted | Found | Code | Source |
|---|---|---|---|---|
| Fixture, 28 blocks | 6 pairs | **2 of 6** (1 of 6 before fixes) | rel01 | M4-gate §5 |
| Zero2Repo case006, round 17 | 24 | **14 of 24** with F3 D43–D44 and F5 D15–D17; **11 of 24** with the compiler before them, on the same full compile | current | interim report §3.6 |
| Zero2Repo case010, round 19 | 15 | **9 of 15** | current | interim report §3.7 |
| Zero2Repo case016, round 21 | 17 | **9 of 17** (its export flags 10, through a second sentence) | current | interim report §4.9 |

Where the misses come from: in round 17 **all 10 misses were pairs never proposed** to the judge, and
every planted pair that was proposed was called a contradiction. In round 19, 4 misses were never
proposed and 2 were judged and rejected (one read as a subsumption; one side reached the judge as a
fragment cut from its condition). In round 21, one side of one planted conflict was **in no node** —
the atomizer omitted a list item. One compile per arm: in round 17 Haiku's topic tags varied enough
between compiles to change 3 items, so the gain of 3 is not shown to exceed run-to-run variation.

**Precision — how many reported conflicts a person judged real**

| Corpus | Result | Source |
|---|---|---|
| Fixture (same as above) | **5 of 7 (71 %)** | M4-gate §5 |
| This repo's F5 + F6 specs, 181 blocks | **4 of 39 sampled (≈ 10 %)**, before the I-86 fix | M4-gate §7 |
| **This repo's full `sdd/specs/` (R18), 845 blocks** | **1 of 381 (0.26 %)**, all adjudicated, against a pass line of ≥ 25 % | build-plan I-93; rel01 close-out |
| Pilot graph's open contradictions | **2 of 21** — both spec defects, both fixed | rel01 close-out |
| case010 with 14 facts removed, round 20 | **0 of 22** contradictions | interim report §3.8 |
| case016 with 17 planted conflicts, round 21 (R21 store) | **16 of 67** contradictions (10 planted, 6 more left open as real; 51 judged false "on the owner's behalf") | interim report §3.9 |

**Other properties**

| Measure | Result | Source |
|---|---|---|
| **Determinism** | A rebuild from sources + lock makes zero model calls and byte-identical files | F3 AC-3.19 (test) |
| **Store integrity** | `check_store` clean at the end of R18 | M4-gate §8 |
| **Export is lossless** | Every live block's text occurs verbatim in its home pack, or nothing is written | F7 §4.9 (checked on every export, tested) |
| **Test suite** | **779 passing** on 2026-11-08 (754 at rel01 close, 628 when this lecture was first written) | `pytest` |

**How to read this:** the judge is decent on plain prose and on product specs, and it raises many false
alarms on a spec set dense with acceptance criteria and decision entries. There, the document's own
structure — a criterion restating its rule, a decision heading summarising its body, two criteria for
two situations — reads like contradiction and duplication. Some of that is suppressed in code (chapter
6); the "different situations" class is not. Recall is limited mostly by **which pairs are proposed**,
not by the judge. **Treat every conflict as a question for a person, not a finding** — which is
exactly what the export's gate makes you do.

## Known weaknesses of the as-built compiler

| Weakness | Effect | Where recorded |
|---|---|---|
| **Pairs never proposed** | The main source of missed conflicts (all 10 misses in round 17) | interim report §3.6; F5 D15–D17 narrowed it |
| **Term proliferation** — a new name per phrasing | Related claims land in different families and may never be paired; R18 has 1 031 terms for 950 nodes | build-plan I-65, I-76 |
| **False positives on criteria-dense specs** | R18: 1 real of 381. Nine shapes named; fixes need prompt or suppression decisions | I-93 (carried to rel02) |
| **High ambiguity** | 628 of 950 R18 nodes (66 %) and 650 of 1 126 R21 nodes (58 %) carry at least one ambiguity entry | M4-gate §8; R21 store |
| **Blocks that never atomize** | 8 blocks fail on every retry at rel01 close; the model paraphrases a quote | I-84, I-94 |
| **The atomizer can omit a claim or cut it from its condition** | A planted side in no node (round 21); a fragment that loses its meaning (round 19). F3 D44 covers two shapes only | interim report §3.7, §4.9 |
| **An example is linked to the claim before it** | An example illustrating a later claim is linked to the wrong one (still paired by S7) | F3 D41 ⚠ |
| **No `query` command** | Agents read the store by hand for one change (chapter 9), or use the export | F4 AC-4.9 … 4.13 |

Three defects that would each have made R18's numbers wrong were found by R18 itself and fixed before
the run finished (I-83 id counter, I-85 dropped pairs on a stopped run, I-86 ambiguous nodes never
checked). The lesson: **a run on real data is also a test run** — read its numbers against each other
(does this run's work add up with the last one's?), not only against themselves.

## What a compile costs

Every model call on the default backend goes through Claude Code on a **subscription**, so no money
is billed per call. What the compiler records is Claude Code's own `total_cost_usd` — an estimate of
what the same calls would cost at API list price. Quote it as **estimated API-equivalent**, never as
spend (build-plan I-82).

| Corpus | Blocks | Calls | Estimated API-equivalent | Source |
|---|---|---|---|---|
| Fixture (R17) | 28 | 177 | $2.35 | M4-gate |
| F5 + F6 dogfood | 181 | 271 | $6.32 | M4-gate |
| **Full `sdd/specs/` (R18)** | **845** | **2 673** | **≈ $54.94**, 9.05 h, 16 runs | rel01 close-out |
| Later rel01 fix runs on it (I-92, I-94) | — | 834 | ≈ $15.12 | rel01 close-out |
| case006, 24 planted, full compile (round 17) | — | 757 | $2.89 | interim report §3.6 |
| case010, 15 planted (round 19) | — | 386 | $1.49 (517 nodes) | interim report §3.7 |
| case010, 14 facts removed (round 20) | — | 356 | $1.35 | interim report §3.8 |
| **case016, planted (round 21, R21 store)** | **450** | **860** | **$3.58** (1 126 nodes) | interim report §3.9 |

Where R18's went: judging pairs ≈ $25.67; describing atoms ≈ $9.05; atomizing blocks ≈ $5.50;
term questions ≈ $1.48; the remaining ≈ $13.24 went to calls whose answers were rejected and re-asked.
**The call count is the cost**: each headless call carries ≈ 22 000 tokens of Claude Code's own
harness prompt, whatever it asks (build-plan I-8).

On a subscription the practical limit is not money but the **session window**: R18 hit the limit five
times and waited for resets. Budget for a large first compile over a day; after that, edits cost only
the changed blocks and their re-checked pairs.

⚠ **Estimates made on small corpora have always been low** — 3× on the dogfood, 2× on R18, 5× on the
contract run (I-94) — because real specs form more pairs per block than a fixture does. Measure on a
slice of your own specs before promising a number.

## What an export costs

`sddc export` makes no model call, so producing it costs nothing but seconds. **Reading** it costs the
agent more than reading the Markdown: the export is about 3× the Markdown's characters (chapter 9). In
round 18, building from the export instead of the Markdown cost per run, as measured from the agents'
own logs: Sonnet **+$0.10 (+4.7 %)**, Haiku **+$0.76 (×2.66)**, n = 3 each. The agents' output
tokens barely changed (Sonnet ≈ equal, Haiku ×1.07); the extra cost was context re-sent over more
turns (Haiku: 57–77 turns against 48–54; peak context up to 404 k tokens against 138–176 k). How this was measured, and checked against
the logs, is in `sdd/design/rel-02/rel02_methodology_notes.md` §6.1.

## Troubleshooting

| Symptom | Likely cause | Do |
|---|---|---|
| `exit 5` every run, pending falling | A big corpus; the cap is doing its job | Keep compiling (chapter 2 loop) |
| `exit 6 … session limit · resets 5pm` | The subscription's usage window | Wait for the reset; run again — nothing is lost |
| `exit 6 … claude is not on PATH` | Claude Code missing | Install and log in to Claude Code |
| `exit 4` naming checks | A store or profile problem | Read every named problem; do not hand-edit `.sdd/` |
| The same blocks in "failed" every run | The model keeps paraphrasing a quote | See `.sdd/review.jsonl` → `atomize_failed`; rephrasing the sentence may help (unmeasured) |
| A conflict you know is false | Judge limitations (above) | `sddc conflicts judge CF-… --verdict false --note "…"` |
| A claim "in the wrong family" | It named the thing differently | Use the existing term name in the spec text (chapter 7) |
| `sddc export` exits 3 | Contradictions without a current verdict | Judge them, or `--allow-open` and tell the agent they are open |
| `sddc export` exits 2 | A spec changed since the compile | `sddc compile`, then export |
| `sddc export` exits 1 | `--out` points at a folder that is not an export | Choose an empty folder, or the old export's folder |
| An old store shows many pending blocks after an upgrade | New rules made blocks pending (e.g. contract fences, F1 D15) | `sddc compile` — only those blocks are paid for |
