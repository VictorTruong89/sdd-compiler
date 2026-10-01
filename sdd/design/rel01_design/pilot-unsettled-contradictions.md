# Pilot graph — the 21 contradictions the export gate blocks on

> Written 2026-09-30 · design tier, non-authoritative · Phase C1 of `HANDOVER_code_ready_graph.md`.
> **These are Claude's readings — all 21 confirmed by the owner on 2026-09-30** and recorded on the copy
> (`ADJ-000382` … `ADJ-000402` in `~/sddc-runs/export-trial-01/.sdd/adjudications.jsonl`). CF-000384's
> fix is applied: F5 CT-5.1's example now reads `"score": 4.5`.
> Source: `sddc export` (no `--allow-open`) on a copy of the frozen pilot graph,
> `~/sddc-runs/export-trial-01` — 21 open contradictions have no current human verdict: the 20 with none
> (handover) plus CF-000044, whose R18 verdict is stale (its pair was judged again, J-003200 → J-007532).
> How the verdict is used: `real` → shown in both members' packs as *Settled*, with the note stating
> which side holds (F7 §4.6); `false` → shown nowhere.
> To record: `sddc --root ~/sddc-runs/export-trial-01 conflicts judge CF-… --verdict false --note "…"`.
> Line numbers below are the nodes' own `source.lines`; two are in `sdd/specs/README.md`.

**Summary of my readings: 2 real (CF-000384, CF-000387), 19 false.** I looked at the spec text around
most of the false ones; the five marked *not re-read in context* (CF-000400, 402, 408, 410, 422) rest on
the two quotes and the model's rationale only, so weigh those least. CF-000382 and 386 I reasoned from
the structure of CT-1.3 and did not re-read either.

| CF | Members (quote A · quote B) | Reading | Recommend | Note for the export |
|---|---|---|---|---|
| 000044 | N-000098 "The answers are ignored" · N-000782 "Every answer is checked by code…" | placement ignores the Q1–Q7 sub-answers for a `verification` atom; the whole answer is still checked. Earlier verdict (false, scope mismatch) still stands | **false** | re-confirm the stale verdict |
| 000382 | AC-5.16 "run record carries the CT-5.3 counts…" · CT-1.3 `counts` {new, changed, unchanged, removed} | F5's retrieval counts and F1's ingest counts are different objects; CT-1.3 does not say the run record is extended | **false** | ⚠ a wording gap in F1 CT-1.3 (not extendable as written); same for 386 and 408 |
| 000383 | AC-5.8 "any candidate comes from S5 or S6" · CT-5.1 `"source": "S2"` | AC-5.8 is scoped to a graph whose first node shares nothing; CT-5.1 is an example elsewhere | **false** | |
| **000384** | AC-5.9 "points sum exactly to `score`" · CT-5.1 `score: 5.5`, points 2.0 + 2.5 | the example breaks the rule it illustrates (known, I-94) | **real** | winner: AC-5.9; fix CT-5.1's example (4.5 or add a third point) |
| 000386 | AC-5.10 "run counts record 15 dropped by the cap" · CT-1.3 `counts` | as 382 | **false** | |
| **000387** | AC-6.22 "the run counts one `suppressed`" · CT-4.1 `counts` | a true defect — CT-6.2 has no `suppressed` field (I-94) — but this record names CT-4.1, the wrong member | **real** | winner: AC-6.22; CT-6.2 should add `suppressed`. The pack shows the record with CT-4.1, so the note must name CT-6.2 |
| 000400 | N-000030 "Case… preserved" (F1) · N-000249 "the case of a quote's first letter (D9)" (F3) | F1 stores block text exactly; F3's quote match may relax first-letter case. Different things | **false** | *(not re-read in context)* |
| 000401 | N-000177 "`label` is the human id…" · N-000178 "Null otherwise." | a rule and its own complement (F2 CT-2.1 text) | **false** | |
| 000402 | N-000266 "set `atomized_hash` to its current `text_hash`" · N-000268 "a block that failed … keeps its old value" | success case vs failure case | **false** | *(not re-read in context)* |
| 000403 | AC-1.9 "every pre-existing block … `unchanged`" · N-000036 "remaining old blocks → `removed`" | AC-1.9 is the no-change case; the rule is the matching order — the remaining-unmatched case | **false** | |
| 000407 | N-000571 "`sddc compile` runs … check (F6)" · N-000705 "deferred out of rel01: … `check`…" | the `check` *phase* runs inside compile; the standalone `check` *command* is deferred | **false** | ⚠ README wording invites this; worth rewording |
| 000408 | CT-1.3 run record · N-000613 "Pairs judged … usage" (F6 report) | F1's record is the ingest run; F6 describes the report's counts | **false** | *(not re-read in context)*; same gap as 382 |
| 000409 | CT-6.1 pair answer · N-000517 "`pairs --exhaustive` … without judging anything" | retrieval's exhaustive mode judges nothing; F6's check does | **false** | |
| 000410 | N-000098 "answers are ignored" · N-000248 "never discards another block's accepted answer" | different answers, different scopes (as 044) | **false** | *(not re-read in context)* |
| 000413 | AC-5.15 "6 nodes … all 15 pairs" · N-000546 "6 gave 117" | two unrelated numbers: 6 nodes → 15 pairs; a *cap of 6* on R17 → 117 pairs | **false** | |
| 000414 | N-000067 "no sentence splitting in F1" · N-000382 "every sentence after *Why:* or *Rejected:*" | F1 does no splitting; F3 names non-claim sentences | **false** | |
| 000417 | N-000521 "F5 makes no model calls" · N-000781 "The model answers narrow questions" | F5 is the retrieval stage; the model is used by F3 and F6 | **false** | |
| 000418 | N-000180 "its record… deleted in the same transaction" · N-000272 "Same id; record untouched except `source.lines`" | deletion when the text is gone vs the `unchanged` case | **false** | |
| 000419 | N-000368 "No node becomes `ambiguous`" · N-000590 "A node with status `ambiguous`" | the first is scoped to a term-merge review item ("…for it", F3 line 498) | **false** | |
| 000420 | AC-2.1 "layer is `L1`" · N-000256 "formed with the first yes's layer" | AC-2.1 is the one-quote placement; the other is the split case | **false** | |
| 000422 | N-000830 "in small closed questions" · N-000831 "never open ones" | complements; the model's own rationale says so | **false** | *(not re-read in context)* |

## What these records surfaced (fixed 2026-09-30, build-plan I-97)

1. **The run record never stored the check counts** (CF-382, 386, 408): a code defect, now fixed; the
   records themselves stay false — CT-1.3's ingest counts and F5/F6's counts are different keys.
2. **`sdd/specs/README.md` "deferred … `check`"** (CF-407): reworded to name the standalone command.
3. **CF-387's real half** — CT-6.2 lacked `suppressed` — is fixed in the spec. If you judge CF-387
   `real`, its note can now say the defect is fixed; the record itself names CT-4.1, the wrong member.
