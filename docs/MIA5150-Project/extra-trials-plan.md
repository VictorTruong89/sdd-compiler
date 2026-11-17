# Extra trials for the final report: plan

> Written 2026-11-10 by Claude Code for the owner, after the owner's comments on
> `final-report-draft.md` ("explicitly state … how many trial cases … how many runs in each case, for
> each format … make a plan for extra trials"). **Not approved; no model run is started by this file.**
> The sample-size reasoning is in the draft's §3.6, computed by `harness/trials/stats/power_plan.py`
> from every scored run of rounds 18–25. Every `$` is Claude Code's `total_cost_usd` estimate; costs below
> are *estimates scaled from measured runs*, not measurements.

## 1. What the report needs, and the gap

| Claim (draft §1) | Test (draft §3.6) | Needs | Have | Gap |
|---|---|---|---|---|
| 2a. Flags raise naming (oracle export, review list) | t-test over cases; sign test as check | **6 cases** (sign test two-sided p = 0.031), power ≥ 0.97 at 5 | 3 cases | **3 cases** |
| 2b. The compiler's own export raises naming where it flags | same | the compiler-export arm in every case | 1 case (case016) | compiler-export arm on case006, case010 and every new case |
| 2c. No harm to code (core non-inferiority, δ Sonnet 2, Haiku 5 points) | one-sided 95 % bound over cases | 5–6 cases, Haiku 5 runs per arm (power 0.98–1.00) | 3 cases, Haiku 3 runs on two of them | the same 3 cases; Haiku top-up optional |
| 3. A review is the better detector | per case recall and precision (round 22) | the 3 new cases reviewed (3 Haiku + 3 Sonnet reviews each) | 3 cases | 3 cases, cheap |
| 4. No format reduces silent invention (equivalence, δ 2 gaps) | bound on both sides over cases | **≥ 4 cases with gaps** (power 0.92–0.97) | 2 cases (case010, case016) | gaps planted in the new cases |

**Runs per case, per model, per arm: Haiku 5, Sonnet 3.** More cases raise power far more than more
runs: going from 3 to 5 runs per arm adds 0.02–0.17 power, going from 3 to 6 cases adds 0.2–0.4. More
than 5 runs per arm is not worth its cost for any claim (draft §3.6, Power table). Haiku gets 5 because
its run-to-run spread is three times Sonnet's on the core (3.64 vs 1.14 points).

> **Status 2026-11-11:** round 27a approved 2026-11-10 and **done**
> (`harness/trials/r27-zero2repo-compiler-export-case006-case010/`): 12 of 12 runs, $18.89 est. (plan
> ≈ $15); scored and read by reader 1; Tables 1a, 1b and 2 of the draft filled. Reader 2 on its 12 runs
> still to run. The 7-day window was at 0.44 after it (resets 16 Nov 16:00). Round 27b not run (see §5).
> **Round 28 approved 2026-11-11** ("Agree on your suggestion and 3 questions. Go ahead with round 28"):
> three new cases; margins of §3.6 confirmed (core δ Sonnet 2, Haiku 5; silent invention δ 2 gaps). All three
> planted 2026-11-11, answer keys written before any model output: case005 17 conflicts / 11 gaps (core 335
> of 395), case011 12 / 12 (core 271 of 321), case001 15 / 4 (core 265 of 302; few gaps because the spec
> makes TOML v1.1.0 the authority for the grammar). Compiles and the 18 reviews (`r28-zero2repo-reviews/`)
> running.
>
> **Status 2026-11-17: all planned runs done; analysis done; draft updated.**
> - **Round 28 done.** 96 of 96 coding runs (`r28-zero2repo-case{005,011,001}-conflicts-gaps/`), $47.63 est.
>   for the runs that count, not counting compiles, reviews or early-stop attempts. The drivers stopped on
>   12 Nov (Docker EOF) and were restarted on 16 Nov; the failed rows reran and succeeded. All 96 runs are
>   scored and read by reader 1. The 18 reviews are scored (`r28-zero2repo-reviews/TRIAL.md`).
> - **Round 27b run** (the optional Haiku top-up of §5, because the 7-day window was at 0.07 after the
>   reset). 16 of 16 runs (`r27b-zero2repo-haiku-topup-case{006,010}/`), $15.55 est. Scored with round
>   27's copies of the round 18/19 scorers, and read by reader 1.
> - **Reader 2** has read every run of rounds 18–28, including 27, 27b and 28: 3 336 item readings, 21
>   disagreements. Reader 2 was right in 3 of them (case001 C16 twice; round 26's one), and reader 1's
>   table was corrected; reader 1 held in the other 18. After the corrections, agreement is 99.5 %
>   (κ 0.980; `r26-…/notes/agreement.json`).
> - **Tests over 6 cases** (`stats/power_plan.py`; `TOPUP=1` adds 27b):
>   - Naming, oracle export and review list: t p ≤ 0.012 and sign test p = 0.031 for both models.
>   - Naming, compiler export: t p = 0.041 (Haiku) and 0.021 (Sonnet), but 5 of 6 cases positive, so the
>     sign test fails (case005).
>   - Core: non-inferior for all 3 arms × 2 models.
>   - Silent invention: equivalent within ±2 gaps for all 6 rows (K = 4–5).
>   - The n = 5 top-up changes no conclusion. But the case006 Markdown runs from two weeks later named
>     more (54–71 % against 29–42 %), so time is a confound in the old cases.
> - **Draft:** `final-report-draft.md` Abstract, Tables 1, 1a, 1b, 2, 3, 4, §§4–7 and Appendix C rewritten
>   on 6 cases. Owner review pending.
>
> Nothing more is planned. Weekly usage after the runs was 0.24 (the window resets 23 Nov 16:00).

## 2. Round 27: complete the two old cases (no new compile)

**Goal:** fill Table 2's empty compiler-export cells for case006 and case010.

| Item | Plan |
|---|---|
| Compiler export, case006 | round 17's `work/compile-full` (the fixed compiler, 14 of 24 planted conflicts flagged); round 17/18's verdicts on the non-planted contradictions (51 false, 4 real); `sddc export --allow-open`; **nothing injected** (as round 21's compiler arm) |
| Compiler export, case010 | round 19's `work/compile-full` (9 of 15 flagged); round 19's verdicts; same steps |
| Tasks | round 18 / round 19 task builders, differing from the Markdown task only in the spec folder (`diff -r` check); instruction unchanged |
| Runs | **27a (needed):** compiler-export arm, Haiku 3 + Sonnet 3 per case = **12 runs**, matching the n of those cases' other arms. **27b (optional):** Haiku top-up to 5 runs in all four arms of both cases = 2 × 4 × 2 = **16 runs**, interleaved across arms so that no arm is a week apart from the others |
| Scoring | round 18/19 scorers and probes unchanged; readings by reader 1, then reader 2 (round 26's script) |
| Cost | 27a ≈ **$15** (round 18/19 export runs: Haiku $0.6–1.9, Sonnet $1.3–2.4); 27b ≈ **$13** |
| Time | 1 day (task build ½ day, runs overnight) |

## 3. Round 28: three new cases, four arms each

**Cases** (from the interim report's §7.1 list; Python; earlier Haiku Markdown builds at full score in
round 13b, so a base build for footprint measurement exists):

| Case | Upstream | Spec words | Hidden tests | Target conflicts / gaps (≈ 5 % of tests each, footprint 1–3) | Reserve |
|---|---|---|---|---|---|
| case005 | h11 | 7 915 | 395 | ~16 / ~12 | |
| case011 | jmespath | 7 002 | 321 | ~15 / ~12 | |
| case001 | tomli | 4 860 | 302 | ~14 / ~12 | case002 (python-envfile, 7 202 words, 281 tests) if a case yields too few candidates |

**Design per case:** round 21's (conflicts and gaps planted in one spec, answer key written before any
compile or run, candidates chosen from hidden-test *names* only, footprint measured with no model,
probes checked on the base build and every alternative copy). Four arms, so Table 2 has no empty cell:

| Arm | What the agent gets |
|---|---|
| Markdown | the planted spec |
| Compiler export | `sddc export` of the planted spec, false contradictions judged false (on the owner's behalf), nothing injected |
| Oracle export | the compiler export plus the planted conflicts it missed, injected from the key |
| Review list | the planted spec plus the first Haiku review's `CONFLICTS.md` (rule of rounds 23 and 25), unfiltered |

| Step | Model cost per case (estimate) |
|---|---|
| Plant, footprint, probes (Harbor's no-model oracle agent) | $0 |
| Compile (Haiku), one pass | $1.5–3.6 (rounds 19, 21: $1.49, $3.58 for 8 412 and 18 845 words) |
| Reviews: Haiku 3 + Sonnet 3 (detector comparison, claim 3; the first Haiku review becomes the list) | $0.5–1.5 |
| Coding runs: 4 arms × (Haiku 5 + Sonnet 3) = **32 runs** | ≈ $40 (Haiku ≈ $0.9, Sonnet ≈ $1.8 per run, rounds 21–25) |
| **Per case** | **≈ $45** |

**Round 28 total: 96 coding runs, ≈ $135** for three cases (smaller specs than case016 may cost less;
not measured). Each new case's own `TRIAL.md` and gate run, as rounds 18–21.

## 4. Totals, budget and calendar

| Round | Runs | Cost (est.) | Needed for |
|---|---|---|---|
| 27a compiler-export arm, case006 + case010 | 12 | ≈ $15 | Table 2 complete; claim 2b on 3 cases |
| 27b Haiku top-up, case006 + case010 (optional) | 16 | ≈ $13 | Haiku n = 5 everywhere |
| 28 three new cases | 96 + 18 reviews | ≈ $135 | claims 2a, 2c, 3 on 6 cases; claim 4 on 5 |
| Second reader on all new runs | ~110 calls | ≈ $5 | κ for the new readings |
| **Total** | **124–140 runs** | **≈ $155–170** | |

**Usage limit.** Over rounds 24–26 the subscription's 7-day share rose from 0.02 to 0.26 for about $30
est. of runs plus this session's own use, so one 7-day window holds roughly $100–120 est. of runs (a
rough reading, not measured). The plan therefore spans the reset of **16 Nov 16:00**.

| Dates | Work |
|---|---|
| 11 Nov | Round 27a: build the two compiler exports and tasks; runs overnight (27b with them if approved) |
| 11–13 Nov | Round 28: plant case005, case011, case001 (answer keys, footprints, probes); compiles; reviews |
| 13–16 Nov | Round 28 coding runs until the 7-day limit pauses the driver |
| 16–19 Nov | Rest of round 28 after the reset; scoring, readings, second reader |
| 16–20 Nov | Final report written in LaTeX in parallel (the draft's tables fill in as rounds close) |
| 20–21 Nov | Final numbers: draft §3.6 recomputed with K = 6, Tables 1b, 2, 4 complete |
| 27 Nov | Presentation |

**If time or budget runs short:** two new cases instead of three (K = 5) still give a one-sided sign
test at p = 0.031 and power ≥ 0.91 in every row of the draft's power table; drop 27b first, then the
third new case. Claim 4 then rests on 4 cases (power 0.92–0.97).

## 5. Decisions for the owner

1. Approve round 27a (12 runs, ≈ $15) — fills Table 2's empty cells. **Recommended.**
2. Approve or skip round 27b (Haiku top-up, 16 runs, ≈ $13). *Recommendation: skip unless budget
   remains after round 28; the case-level analysis gains little from it.*
3. Approve round 28 with three new cases (≈ $135) or two (≈ $90). *Recommendation: three.*
4. Confirm the margins fixed before these runs: core δ = 2 points (Sonnet), 5 (Haiku); silent
   invention δ = 2 gaps. They are stated in the draft's §3.6 and must not change after the runs.
5. The rulings arm (settled list) is **not** in this plan; it stays a one-case result (round 24).
