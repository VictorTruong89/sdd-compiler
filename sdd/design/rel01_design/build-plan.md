# rel01 build plan and task list

> **Status:** ✅ APPROVED 2026-09-18 (rel01 D29); B1–B3 decided as recommended. **Progress and the
> issue log for the retrospective: §7 and §8.** Earlier: DRAFT for review · **Drafted:** 2026-09-18 · **Tier:** design, non-authoritative.
> Written to satisfy the last item of the rel01 D20 coding gate. **Coding starts when the owner
> approves this file and the [G4 outline](G4-measurement.md).**
> **Specs:** F1–F6, 118 acceptance criteria, all 🟢. F7 is design only.

---

## 1. Three decisions this plan needs from the owner

| # | Decision | Recommendation |
|---|---|---|
| **B1** | **Who owns `sddc compile`?** It spans F1, F3, F5 and F6, and no spec owns the orchestration | Put it in `src/sdd_compiler/pipeline.py`, **governed by F3**, which already defines `compile`, its phases and its exit codes. Add the path to `ownership.yaml` under F3. *Rejected:* a new F8 spec — a spec whose content is three lines of sequencing is bureaucracy |
| **B2** | **Which commands ship in rel01?** Fifteen are specified | Ship five: **`init · compile · status · conflicts · family`** — ⚑ amended in T11 to **six**, adding `ingest` (F1 CT-1.6; see I-38). Defer `blocks`, `show`, `atomize`, `ingest` (as a separate command), `map`, `query`, `check`, `pairs`, `check-conflicts`, `review`. Every deferred command is a view on a store that already exists, so adding one later is cheap. ⚠ Their acceptance criteria stay in the specs, unbuilt and marked in §5 |
| **B3** | **Constitution §4 test tiers** — all 118 ACs say "provisional" | Adopt the five names the specs already use: **unit · contract · property · golden · integration** (§4 below). One small edit to `constitution.md`, then no AC wording changes |

## 2. Build order — four milestones

Each milestone is releasable on its own: if the clock runs out, the last finished milestone is rel01.

| M | Name | Delivers | Specs | Model calls? |
|---|---|---|---|---|
| **M1** | **Block inventory** | `sddc init`, and ingest inside `compile`: Markdown → stable blocks in `.sdd/`, change detection across edits | F1, F4 (store primitives) | **No** |
| **M2** | **The graph exists** | Atomization with Haiku, placement into layers and families, terms, nodes and links written and validated | F3, F2, F4 | Yes |
| **M3** | **The graph is readable** | `sddc status`, `family`, generated Markdown views | F4 | No |
| **M4** | **Conflicts reported** | Retrieval, pair judgment, conflict records, registry, the end-of-run report, `sddc conflicts` | F5, F6 | Yes |

**M4 is the release.** M1–M3 without it produce a graph nobody can act on; M4 is the purpose.

## 3. Task list

One task ≈ one coherent group of acceptance criteria. "AC" columns are the criteria a task must make
pass. Tasks inside a milestone are ordered by dependency.

**Gate protocol** (adopted 2026-09-19 after the M3 gate review, I-54; applies to every gate from M3 on):

1. **Pass line first.** The owner writes the pass line before anyone reads the evidence. A line drawn
   after reading bends to the result.
2. **All the outputs, or a sample drawn blind.** The gate file holds every output, or a sample chosen
   before the outputs are seen (every n-th, or seeded random). It never holds the builder's pick.
3. **A first-time reader** where the question is about understanding. This is someone who has not read
   the specs under test, for example a fresh agent given only the gate file. The author of the specs is
   the second reader, not the first.
4. **One recorded verdict per item**, with the reason, on a fixed scale (✅ / ⚠️ / ❌). The owner
   confirms or overrides each row.
5. **Durable.** The evidence and the raw outputs are written under `rel01_design/measurements/` the
   moment they exist (I-50).

### M1 — Block inventory

| # | Task | ACs | Code |
|---|---|---|---|
| T1 | Package skeleton, `pyproject`, the `sddc` entry point, profile load/validate | F1 CT-1.4 | `profile.py`, `cli.py` |
| T2 | Store primitives: JSONL read/write with fixed key order and sorting, temp-file + rename transaction, `.sdd/` lock with a 15 s wait | F1 AC-1.24, AC-1.26 · F4 AC-4.3, AC-4.4 | `store/jsonl.py`, `store/graph.py` |
| T3 | Segmentation: headings, paragraphs, list items (with nesting), table rows with header, blockquotes, code fences, skipped constructs | F1 AC-1.1 … AC-1.7 | `ingest/segment.py` |
| T4 | Normalization and hashing; identity and diff: exact match, positional match, new/removed | F1 AC-1.8 … AC-1.12 | `ingest/identity.py` |
| T5 | `init`; ingest pipeline; `status --json`; failure paths and exit codes | F1 AC-1.21 … AC-1.25 | `cli.py`, `ingest/pipeline.py` |
| **G** | **Gate:** run it on this repository's own `sdd/specs/`; edit one paragraph; confirm only that block changes | — | — |

### M2 — The graph exists

| # | Task | ACs | Code |
|---|---|---|---|
| T6 | Model interface: headless backend, child environment (`SDD_COMPILER_CHILD`, no `ANTHROPIC_API_KEY`), version capture, usage recording, call cap, **fake backend for tests** | F3 AC-3.1 … AC-3.5 | `llm/` |
| T7 | Q-ATOM + guards G2 span anchoring, G3 coverage, G5 schema; re-ask once | F3 AC-3.6 … AC-3.8, AC-3.10 | `atomize/questions.py`, `atomize/guards.py` |
| T8 | Q-DESC: canonical fields, layer answers, term tags; G4 injection, G6 weak words; quantity parsing and normalization | F3 AC-3.9, AC-3.11, AC-3.13 | `atomize/describe.py`, `atomize/quantities.py` |
| T9 | F2 model: schemas, ids and counters, layer placement (incl. `split_required`), family rule, status derivation and precedence | F2 AC-2.1 … AC-2.14, AC-2.17 … AC-2.22 | `model/` |
| T10 | Node forming: term resolution and Q-TERM, block-atomic writes, `uses_term` links; T3 split re-ask | F3 AC-3.12, AC-3.14 … AC-3.16 | `atomize/pipeline.py` |
| T11 | Graph store: family shards, `graph.meta.json` with counters, deletion cascade, the seven consistency checks | F4 AC-4.1 … AC-4.8 · F2 AC-2.23 | `store/graph.py`, `store/check.py` |
| T12 | Alignment across edits; judgment lock and replay; `--no-replay` | F3 AC-3.17 … AC-3.20 | `atomize/align.py`, `atomize/lock.py` |
| **G** | **Gate:** compile this repository's specs; inspect the nodes by hand; record cost (G4 M7) and the `inferred` rate (M8) | — | — |

### M3 — The graph is readable

| # | Task | ACs | Code |
|---|---|---|---|
| T13 | Indexes in memory; `status` extended with node counts | F4 §4.4 | `store/index.py` |
| T14 | `sddc family`, and generated `views/map.md` and `views/families/*.md` with the do-not-edit header | F4 AC-4.14, AC-4.15, AC-4.17, AC-4.18 | `views/` |
| **G** | **Gate:** a person who has not read the graph can describe what a family contains from the view alone. Run by the gate protocol above. **Pass line** (proposed — owner confirms before the reading): the largest family reads ✅, and ✅ cards hold at least half the nodes | — | — |

### M4 — Conflicts reported

| # | Task | ACs | Code |
|---|---|---|---|
| T15 | Retrieval sources S1–S7, scoring, cap, `pair_key`, which nodes are checked | F5 AC-5.1 … AC-5.14 | `retrieval/` |
| T16 | Q-PAIR judgment; links and conflict records; direction and confidence rules | F6 AC-6.1 … AC-6.8 | `conflicts/judge.py` |
| T17 | Check phase: never stops, shared budget, incomplete reporting; conflict lifecycle (re-judge, close, member deleted) | F6 AC-6.9, AC-6.12 … AC-6.19 | `conflicts/pipeline.py`, `conflicts/lifecycle.py` |
| T18 | The end-of-run report and `sddc conflicts`, grouped and sorted with contradictions first; exit codes 0/3/5 | F6 AC-6.10, AC-6.11 · F4 AC-4.16 | `report.py` |
| T19 | **Adjudication record** (G4 §4): `sddc conflicts judge …` → `.sdd/adjudications.jsonl` | *new AC in F6* | `conflicts/adjudicate.py` |
| **G** | **Gate:** compile the planted-conflict fixture; measure recall (G4 M1); compile this repository and judge every reported conflict (M2). Protocol §3 above; write-up [`M4-gate.md`](M4-gate.md) | — | — |

### M5 — Only if time remains

Exhaustive mode and candidate completeness (F5 AC-5.15, AC-5.16) · `sddc check` · the attention list
and `review` (F3 AC-3.24, AC-3.25) · `query` · `map` · `blocks` / `show` / `pairs` /
`check-conflicts`.

### M6 — Agent export (rel01 D34, added 2026-09-25)

Spec [`F7_agent_export`](../../specs/F7_agent_export/spec.md). Coding starts when F7 is approved 🟢 (approved 2026-09-30).
Code under `src/sdd_compiler/export/`. No model calls, so every test runs on stores built with the
fake backend.

| Task | Content | ACs |
|---|---|---|
| T20 | Profile keys (CT-7.2, an F1 CT-1.4 addition); stale-source check; units, foundation, omitted headings; order and cycles | AC-7.5 … AC-7.8, AC-7.18 |
| T21 | Pack rendering: text with tags, tables, code; claims, criteria, constraints in scope, related, terms; coverage check | AC-7.1, AC-7.2, AC-7.14, AC-7.15 |
| T22 | Conflict gate and rendering (F6 adjudications, D14 staleness); real-duplicate exclusion | AC-7.10 … AC-7.13, AC-7.23 |
| T23 | `MAP.md`, `CHECKLIST.md`, `export.meta.json`; `sddc export` in the CLI; whole-directory write; goldens and end to end on the planted fixture | AC-7.3, AC-7.4, AC-7.9, AC-7.16, AC-7.17, AC-7.19, AC-7.20 |

Estimate ≈ 7–8 days (design note §4.4), not measured.

## 4. Test tiers — proposed for constitution §4 (decision B3)

| Tier | Shape | Example from these specs |
|---|---|---|
| **unit** | One function, fixed input | Layer placement from seven answers (F2 AC-2.1) |
| **contract** | A record or CLI output validated against its schema | `status --json` (F1 AC-1.21) |
| **property** | Holds over many generated inputs | Status precedence over every fact combination (F2 AC-2.12) |
| **golden** | Text output compared with a stored expectation | `sddc map` (F4 AC-4.14) |
| **integration** | Several components over a fixture repository | Compile the fixture and report its conflicts (F6 AC-6.10) |

⚠ **Getting the tier wrong is the quiet failure:** a property AC given one example test looks green and
proves almost nothing.

## 5. Definition of done for rel01

- Every AC in the shipped scope has a passing test in its tier, and a filled traceability row.
- `sddc compile` runs clean on this repository's own `sdd/specs/` and on the fixture.
- The close-out (`design/releases/rel01_closeout.md`) records: conflicts reported, how many a human
  judged real, cost per compile, and which ACs were **not** built (B2 deferrals, M5).
- Unbuilt ACs are listed as deferred in the spec index — never quietly dropped.

## 6. Risks

| Risk | Mitigation |
|---|---|
| Time: 12 days, 118 ACs, 0 lines written | Milestones are releasable; M4 is the release; M5 is optional |
| Haiku's atomization is too weak to place nodes usefully | Measured at the M2 gate (G4 M4, M8) before M4 is built. The backend and model are profile settings |
| Cost per compile is unpleasant | Measured at the M2 gate (M7); the call cap already bounds a run |
| Retrieval misses real conflicts | Exhaustive mode (M5) measures it; until then the report states how many pairs were judged, never implying completeness |
| Scope creep back into live editing | It is deferred in writing (rel01 D26): appendices in G1, F1 D10, F3 D8 |

## 7. Build progress — updated 2026-09-30

| Task | State | Tests | Note |
|---|---|---|---|
| T1 skeleton, profile | ✅ | 21 | |
| T2 store primitives | ✅ | 18 | |
| T3 segmentation | ✅ | 16 | I-3, I-4 |
| T4 identity and change | ✅ | 18 | I-5; reworked for I-6 |
| T5 init, ingest, status | ✅ | 15 | I-6 |
| **M1 gate** | ✅ | — | 733 blocks from this repo; a second run is byte-identical; one edit → 1 changed |
| T6 model interface | ✅ | 16 | I-8 |
| T7 Q-ATOM, G2/G3/G5 | ✅ | 20 | I-9, I-10, I-11 · live: 20 blocks, 2 calls, 0 failures |
| T8 Q-DESC, G4/G6, quantities | ✅ | 47 | I-13 … I-20 · live: 21 atoms, 1 failure, 1 real `inferred` |
| T9 F2 model | ✅ | 195 | I-21 … I-24 · also AC-2.15, AC-2.16, which no task listed (I-25) |
| T10 node forming | ✅ code · ⚠ quality | 41 (+4 backend) | I-27 … I-32 · all 49 live nodes valid; families weak (I-28); F3 D20 |
| T11 graph store + `compile` wiring | ✅ | 21 | I-33 … I-38 · live smoke: `sddc compile` twice on `vision.md`, store checks clean |
| T12 alignment, lock, replay | ✅ | 23 | I-39 … I-42 · live: rebuild from lock replays every accepted answer; an edit keeps its id |
| **M2 gate** | ✅ measured and reviewed | — | [`M2-gate.md`](M2-gate.md): 63-block stratified sample, two runs, $3.21; findings G-1 … G-14, recommendations R1 … R11 (Part C: every block reviewed) |
| Gate fixes R1 … R11 | ✅ | +14 | Q-TERM `narrower` + `broader`; Q-DESC vocabulary; Q1/Q3 reworded; family `mention` rule; backticks and first-letter case as layout; non-empty canonical; AC = one `V` atom; non-claim examples |
| R6 re-measure | ✅ | — | [`M2-gate.md`](M2-gate.md) §B7: 60–61 of 63 completed, family null 0–7.5 %, criteria one `V` node each, 40–57 % cheaper, runs agree on node count 75 %; family targets unmet on a scattered sample (R12) |
| T13 indexes, `status` graph counts | ✅ | 3 | §4.4 indexes in memory; `status` adds nodes, families, open conflicts, attention items |
| T14 map, family cards, `.sdd/views/`, `sddc family` | ✅ | 15 (2 goldens) | F4 D10 … D16 · AC-4.14, AC-4.17, AC-4.18 partial: `sddc map` and `query map` are deferred (B2) |
| **M3 gate** | ✅ **closed 2026-09-21**: views pass; content fails, with a named cause for each part | — | [`measurements/R12_views_on.md`](measurements/R12_views_on.md): all 19 real cards; **owner approved the reading 2026-09-19**. Review fixes: 3 defects (I-51 … I-53), 4 card changes (F4 D13 … D16). Content: 3 of 19 cards (12 of 43 nodes) coherent (I-56) |
| Gate follow-ups: I-56, I-57, F4 Q2, protocol, I-59 | ✅ code · ✅ measured (R15) | +21 | I-56: F2 D18 … D20, F3 D32, AC-2.26 … AC-2.28. I-57: F5 D9, AC-5.3 amended — S3 pairs on R12 ≈ 60 → 16. Q2 → F4 D17 (full text in Markdown). Gate protocol in §3. Also **F3 D33**: the report counts blocks that completed and formed no node |
| **R15** re-measure — F5 recompiled, 64 nodes, $1.20 | ✅ measured and read | +3 | [`M3-gate.md`](M3-gate.md): criteria in the `node` grab-bag **9 → 4**; `verifies` resolved for **5 of 18** criteria (was 0); family null 3 → 1; S3 pairs on the same store **178 → 42** under F5 D9. Two new defects found and fixed: I-63, I-64 (**F3 D34**). Families still thin: 20 of 32 hold one node. **Blind reading** (a fresh agent, cards only): ✅ 10 of 34 cards, **30 of 64 nodes (47 %)**, against 12 of 43 (28 %) at R12; ❌ 15 nodes (23 %), was 42 %. Against the proposed pass line — largest family ✅, half the nodes in ✅ cards — R15 **fails both**, and 3 of the 6 ❌ cards are artefacts of I-63 and I-64, fixed after the run |
| T15 retrieval S1 … S7, scoring, cap, `pair_key`, which nodes are checked | ✅ | 22 | F5 AC-5.1 … AC-5.14, CT-5.1 … CT-5.3 · **F5 D10** (the counts count proposals). AC-5.15 stays deferred (M5). No model call anywhere in F5 |
| T16 Q-PAIR judgment; links and conflict records; direction and confidence | ✅ | 18 | F6 AC-6.2 … AC-6.8, AC-6.1 partial · CT-6.1, CT-6.3 · **F6 D11** (the direction rule lives in the schema). Writing them through a transaction is T17 |
| T17 check phase inside `compile`; budget; conflict lifecycle | ✅ | 19 | F6 AC-6.9, AC-6.12 … AC-6.19, and AC-6.1, AC-6.11 end to end · **F6 D12, D13** · exit codes 3 and 5 wired. `compile` = ingest → atomize → **check** → write |
| T18 end-of-run report; `sddc conflicts`; exit 3 | ✅ | 12 (2 goldens) | F6 AC-6.10, AC-6.11 · F4 AC-4.16 · **`compile` now prints the report**: what failed, what formed no node, what was dropped, every conflict grouped with contradictions first |
| Planted-conflict fixture (G4 §3 corpus 2) | ✅ | 1 | `tests/fixtures/planted/` — 3 files, 28 blocks, six pairs P1 … P6 in [`EXPECTED.md`](../../../tests/fixtures/planted/EXPECTED.md); written in ordinary spec voice. A suite test keeps it from rotting |
| **M4 gate** pass line | ✅ written **before** the run finished — [`M4-gate.md`](M4-gate.md) §1 | — | G1 ≥ 4 of 6 planted pairs including P1 · G2 ≥ half of what is reported judged real · G3 the run finishes, the store checks pass, the report names every conflict. Owner confirms |
| **M4 gate** | ❌ **failed, usefully** — [`M4-gate.md`](M4-gate.md) | +1 | First end-to-end run: 28 blocks → 34 nodes → 123 pairs → 72 judged → **11 conflicts**, store clean, $1.30. **M1 recall 1 of 6** planted pairs; **M2 precision 3 of 11 (27 %)**. Every planted pair *was* proposed — five ranked 81st–130th because each side got its own term (the measured cost of I-65). One real duplication found that nobody planted. Follow-ups R15 … R18 in the gate file |
| **R15, R16** gate fixes | ✅ | +3 | **F5 D11** (S2 follows `broader`; S6 takes a shared keyword) · **F6 D15** (when two numbers are *not* a contradiction). Effect measured offline before spending: the 5 GB/5 GiB pair rank 123 → 50, the alias pair 81 → 43 |
| **R17** gate re-run, identical corpus | ✅ $2.35 — [`M4-gate.md`](M4-gate.md) §5 | — | All **159 pairs judged**, exit 3, store clean. **Precision 27 % → 71 %**; **recall 1 → 2 of 6** (P4 found). G2 and G3 now pass, **G1 still fails** |
| **R19** I-77 and I-76 fixed in code | ✅ | +4 | **F6 D16**: a criterion never duplicates or subsumes what it `verifies` — checked against the graph, not asked of the model. **F5 D12** (S8, two kinds of one thing) and **F6 D17** (the judge is shown the terms and how they relate). Measured offline on R17's store: the 5 GB/5 GiB pair rank 63 → **43**, and the judge is now told the fact whose absence made it refuse |
| **R20 (B), R21 (A)** cost, measured not guessed | ✅ | +5 | **F5 D13**: the cap is 6, not 10 — 36 % fewer pairs on R17's store with every known-real pair kept. **F6 D18**: Q-PAIR is batched 8 per call, as Q-ATOM and Q-DESC already are, with each answer still checked alone and a failure re-asking that pair. Together: the gate corpus needs **15 judge calls instead of 159**; this repository ≈ **$12**, not $55–70 |
| **C — the dogfood** (F5 + F6, 181 real blocks) | ✅ $6.32 — [`M4-gate.md`](M4-gate.md) §7 | +1 | **192 nodes, 562 pairs judged, 70 conflicts, exit 3, store clean.** M2 on a sample of 39: **4 real (≈ 10 %)** — three of them one defect **introduced that day** (F5 D13 changed the cap; D6, §4.3 and AC-5.10 kept the old number), and one genuine under-specification in §4.1. **65 of 70 involve an acceptance criterion or a decision entry** |
| **I-82** every `$` relabelled: estimated API-equivalent, not spend | ✅ docs | — | The owner checked the Console and saw no credit movement. These runs are on the **subscription**; the figure is Claude Code's own per-call `total_cost_usd`. G4 §2 and M4-gate §7 corrected; the Usage & Cost Admin API (`/v1/organizations/cost_report`, Admin key, curl-only) would show nothing, because it reports API traffic |
| **The full-corpus test session (R18)** | ✅ **compile complete** 2026-09-23 23:46 · ⬜ **M2 adjudication next** (sample of 100 drawn, seed 20260922) · pass line fixed before the run (M4-gate §8) | +5 (**628**) | [`HANDOVER_full_compile.md`](HANDOVER_full_compile.md), write-up [`M4-gate.md`](M4-gate.md) §8. Corpus pinned in `~/sddc-runs/full-corpus/corpus.sha256`, unchanged at the end: **845 blocks** (not 733 — the specs grew, I-69). **16 rounds**, 2026-09-22 19:47 → 2026-09-23 23:46: 10 × call cap, 5 × session limit, 1 × complete; **9.05 h** of compile, **2 673 model calls, ≈ $54.94 estimated API-equivalent** (twice the handover's $26, I-87). **950 nodes, 4 251 pair verdicts, 381 conflicts open** (167 contradiction, 157 subsumption, 57 duplication) in 95 groups; `check_store` clean; 1 block still pending (I-84). **Three real defects found and fixed mid-run, test-first** — I-83 (id counter behind the lock; crash), I-85 (a stopped phase dropped its unjudged pairs; a false "complete"), I-86 (44 % of nodes never checked) — each would have made the close-out number wrong. Raw output: `measurements/R18_round1 … 16.json`, `R18_report.txt`, `R18_conflicts.txt`, `R18_sample.txt` |
| T19 adjudication record (G4 §4) | ✅ | 9 | **F6 AC-6.20, D14** · `sddc conflicts judge CF-… --verdict real\|false --note "…"` → `.sdd/adjudications.jsonl`. M2 (precision) is now recordable — the one number the 30 September close is about |
| *(2026-09-25 … 29: I-92 contract nodes, definitions, Traceability skip; I-94 live runs; pilot graph frozen — see §8)* | ✅ | 684 at `a51477f` | |
| **F7 brought up to date, approved 🟢** (Phase A) | ✅ 2026-09-30 | — | rel01 D36 … D39: definitions shown verbatim, one omit key (`skip_headings`), contract fence printed once (D12), real duplicates excluded (D13) |
| T20 profile key, stale sources, units, order | ✅ | 24 | `export/units.py`, `sources.py` · AC-7.5 … 7.8, 7.18 |
| T21 packs, coverage check | ✅ | 11 | `export/packs.py`, `pipeline.py` · AC-7.1, 7.2, 7.14, 7.15, 7.21, 7.22, 7.24 |
| T22 conflict gate, real-duplicate exclusion | ✅ | 15 | `export/gate.py`, `model.py` · AC-7.10 … 7.13, 7.23 |
| T23 `MAP.md`, `CHECKLIST.md`, meta, `sddc export`, golden, end to end | ✅ | 18 (1 golden) | `export/files.py` · AC-7.3, 7.4, 7.9, 7.16, 7.17, 7.19, 7.20 · end to end on the planted fixture with a scripted fake (`tests/smart_fake.py`) |
| **M6 — first export of the pilot graph** (copy `~/sddc-runs/export-trial-01`) | ✅ | — | 59 packs, 1.1 s. Found I-95 (4.57× the Markdown), I-96 (one 35-pack cycle), I-97 (run record) |
| I-95, I-96, I-97 fixes (rel01 D40) | ✅ | +6 | F7 D14 lists cut, D3 order by spec; run record carries `conflicts` · re-export 3.03× |
| **21 contradictions settled** (rel01 D41) | ✅ owner | — | 2 real, 19 false, recorded on the copy; export passes the gate without `--allow-open`: 2.94×, largest pack 41.7 k. Frozen as `~/sddc-runs/pilot-export-R000023` (+ sha256) |
| **Phase D prepared** — F1 task, hidden tests, harness (study side, `docs/MIA5150-Project/`) | ✅ built · ⛔ **blocked** | 26 hidden | Hidden tests 26/26 on our implementation, 26/26 fail on a no-op. The bubblewrap sandbox cannot start (Ubuntu 24.04 AppArmor userns restriction): owner action, `harness/README.md` |

Counts are tests per task's test files (T1's include 3 profile tests added in T6). Suite total: **628** (2026-09-24); **754** (2026-09-30, after M6 and I-95 … I-97). (T9's count is mostly the 128-case exhaustive placement test.)

## 8. Issues found while building — log for the retrospective

Each entry: what happened, how it was found, what was decided, and what it teaches. Numbered in the
order found. Owner decisions are cited by their spec decision id.

> **Where the retrospective material lives** (asked 2026-09-21). There is no single retrospective
> document yet; it is written at release close from these seven places:
>
> | Where | What it holds |
> |---|---|
> | **§8 of this file** (I-1 … I-68) | Every defect and surprise found while building: what happened, how it was found, what was decided |
> | **The patterns list**, end of §8 | The lessons drawn from those issues — the part a retrospective actually quotes |
> | **§7 of this file** | Build progress: what each task cost in tests and where each gate landed |
> | [`M2-gate.md`](M2-gate.md), [`M3-gate.md`](M3-gate.md) | The two gates in full: what was measured, every reading, the owner's verdict, and (M3 §4) where the gate broke its own protocol |
> | [`measurements/`](measurements/) | Raw output and rendered cards from every measured run (R12, R15, R16) — durable, because a scratch store is one restart from gone (I-50) |
> | [`../rel01_brainstorm.md`](../rel01_brainstorm.md) | Sessions S1 … S32, one entry per working session, and the owner's decision log (rel01 D1 … D33) |
> | Each spec's §7 | The decisions that changed the product, with what was rejected and why (F1 D1 … F6 D13) |
>
> **At release close** they are summarised into `sdd/design/releases/rel01_closeout.md`, from
> [`releases/_template_closeout.md`](../releases/_template_closeout.md): what shipped, what did not,
> and "measured, not asserted" — every number with its sample size. Build-plan §5 lists what that file
> must record. The template keeps it to one page: **these seven places stay the detailed record.**

| # | Task | Issue | Found by | Resolution |
|---|---|---|---|---|
| I-1 | T1 | `argparse` exits `2` on a usage error; F1 CT-1.6 reserves `2` for input errors | Contract test | Parser subclass maps usage errors to `1`. Owner agreed "the spec beats the library" |
| I-2 | T1 | Unknown profile keys: ignore or reject? The spec was silent | Writing the loader | Rejected with exit `4`; a typo in a key must not silently fall back to a default. Owner agreed |
| I-3 | T3 | A second paragraph inside a list item lost its link to the item, so it would be atomized as a free-standing, system-wide claim | Segmenting real specs; 3 of 649 list items affected | F1 Q5 → **F1 D11** (`parent_relation`: `nested` / `continuation`) |
| I-4 | T3 | markdown-it reports 0-based, end-exclusive line ranges; YAML front matter shifted every line number | Line-number tests | Converted to 1-based inclusive; front matter blanked, not removed, so lines stay true |
| I-5 | T4 | Re-adding deleted prose could resurrect the removed block's id | Writing the identity tests | **F1 D12**: a removed record never matches again |
| I-6 | T5 | AC-1.8 ("second run byte-identical") could not pass: the stored `status` flipped `new` → `unchanged`. **Underneath: pending was defined from that flag, so blocks left unprocessed by a call-cap exit, a double guard failure or a crash would silently never be atomized** | Failing AC test; the silent drop found only when analysing the options | F1 Q6 → **F1 D13**: the record stores facts; the run's delta is reported, not stored; pending is derived from `atomized_hash` (F3 §4.5 step 8). AC-1.31 added. Also fixed along the way: `status` had listed code blocks as pending despite `include_code_blocks: false` |
| I-7 | T1–T5 | Three defects in my own tests, not the code: tuple vs list comparison, a subprocess missing `PYTHONPATH`, a wrong line expectation in AC-1.9 | Red tests that should have been green | Tests fixed. A red test may be the test's fault; check before changing code |
| I-8 | T6 | Every headless Claude Code call carries ≈ 22k tokens of harness prompt: ≈ $0.012 and ≈ 5 s per call, almost none of it ours. One call per block ≈ $13.60 for this repo's Q-ATOM alone | First three live calls (measured, rel01 S19) | **rel01 D30**: batch Q-ATOM now; the `anthropic-api` backend for bulk work later |
| I-9 | T7 | Guard G2 ("quote verbatim") rejected **correct** quotes: sources are hard-wrapped (`\n` where the model writes a space) and blockquotes repeat `> ` on every line. 5 of 20 blocks failed; the re-asks made batching dearer ($0.0147/block) than no batching | First live batch | **F3 D9**: match up to layout only. Same 20 blocks: 2 calls, 0 failures, $0.0071/block. Words, case, punctuation still exact |
| I-10 | T7 | The G2 error message cut quotes at 60 characters, hiding I-9's cause (the difference was past character 60) | Diagnosing I-9 | Excerpt widened to 160 |
| I-11 | T7 | A usage-limit 429 from Claude Code surfaced as a raw JSON dump | Live run interrupted by the session limit | Exit code was correct (backend failure). A readable message is due with the end-of-run report (T18) |
| I-12 | T7 | F3 cited "rel01 D31" for batching, but no such decision had been logged | Scripted doc edit whose exact-match assertion failed | Logged as **rel01 D30**; F3 corrected |

| I-13 | T8 | A Q-DESC batch of ~25 atoms, then of 8, exceeded the 120 s call timeout | First live Q-DESC run | Batches capped at 8 atoms; each block's text sent once, not once per atom. The real cause was I-14 |
| I-14 | T8 | **Claude Code runs Haiku with extended thinking on by default.** One Q-DESC call: 2,896 of 3,588 output tokens were thinking; 25–35 s instead of ≈ 5 s | Timing one call, then reading `modelUsage.thinkingTokens` | **F3 D10** ⚑: `atomizer.thinking: false` by default (`MAX_THINKING_TOKENS=0` in the child). ⚠ Every earlier cost figure (I-8, I-9) was measured with thinking on; Q-ATOM for 20 blocks fell from $0.10–0.14 to ≈ $0.02 |
| I-15 | T8 | The model quoted the **section heading** we gave as context; G2 rejected it. 4 of 6 failures in one run | Live run | Prompt: "the section line is context only: never quote it". Next run: 0 such failures |
| I-16 | T8 | G4 as written (atom's own quotes) flagged 8 of 17 real atoms `inferred`, all context resolution ("here" → "F1" from the heading) | Live run, reading every flag | Implemented the wider source (block + headings): 1 of 20, and that one real. **F3 D13** (Q5 option a, owner) |
| I-17 | T8 | Model-proposed `vague_term` on 17 of 20 atoms ("Storage", "matches") | Live run | **F3 D11** ⚑: `vague_term` comes from G6 (the owner's weak-word list) only |
| I-18 | T8 | Inline Markdown (`` `PostToolUse` ``) made a real term look injected | Live run | G4 compares ignoring backticks and `*` |
| I-19 | T8 | A requirement with no modal verb (scope bullets) gets `modality: null`, which fails the atom and, by block all-or-nothing, the whole block | Live runs: 1–3 of ~22 atoms per run | **F3 D14** (Q6 option b, owner): formed and flagged `missing_modality` |
| I-20 | T8 | **Run-to-run variance.** The same 20 blocks gave 23, 23, 21 atoms, and 6, 3, 1 describe failures across three runs with different fixes; not every difference is the fix | Comparing runs | A single live run is an anecdote. G4 measurement (M7, M8) must repeat runs and report spread |

| I-21 | T9 | Q-ATOM failed **14 of 20** acceptance-criterion blocks: the source writes `**Given** … **when** … **then**`, Haiku quotes the words without the `**` | First live run on AC blocks (earlier runs used header and scope blocks) | F3 D9 extended ⚑: `*` emphasis marks are layout. Next run: 0 failures |
| I-22 | T9 | Given/When/Then criteria answer several layer questions with **non-overlapping** quotes ("Given a file…" → data; "then it exits 2" → behaviour): `split_required` for 5–11 of 33–45 atoms | Live placement run | Behaves as specified (T3 split, F3 AC-3.12). ⚠ Watch at the M2 gate: re-asks may cycle on criteria that are inherently setup + outcome |
| I-23 | T9 | Most AC blocks form several nodes, so their `AC-` id is not adopted: 3–5 of 18 kept | Live run | **F2 D12** (Q4 option c, owner): every node of a labelled block carries `label` |
| I-24 | T9 | The test-tier marker `→ *unit.*` became a stray `V` atom (≈ 8 in one run, ≈ 1 in the next); family fallback 9–19 of 33–45 | Live run | Not fixed yet. Candidate: tell Q-ATOM that a trailing tier tag is context. Measure at the M2 gate |
| I-25 | T9 | F2 AC-2.15 and AC-2.16 were in no task of this plan | Writing T9's tests | Built in T9 (pure functions over records) |
| I-26 | T9 | **Spec gap found only by building:** two fields read by approved rules — `scope_selector` (F2 family rule 4, F5 source S3) and `verifies` (F2 family rule 3) — were produced by nothing. Q-DESC returned a scope *description* and a verification *text*; no spec turned them into a selector or node ids. Q-PAIR has no `verifies`/`constrains` relation, so no judged path existed either. Unbuilt, S3 and rule 4 would have passed their unit tests (F5 AC-5.3, F2 AC-2.9) while never firing on real data | Writing the family rule, then tracing every reader of the two fields across F2, F4, F5, F6, F7 | **F2 D13** (Q3 option b, owner): code derives `scope_selector` from scope-role terms plus one closed Q-DESC field `scope_layers`, and resolves `verifies` from cited ids and `label`s (D12); AC-2.24, AC-2.25. Option c — `verifies`/`constrains` as Q-PAIR relations — deferred past rel01 (**rel01 D31**), to be decided from G4's count of unresolved `C`/`V` nodes |

| I-27 | T10 | Every headless call waited 3 s for stdin, and a failure showed only the stdin warning — the real reason (a 429 usage limit) was in the JSON on stdout | Live run died with "no stdin data received in 3s" | Child stdin is `/dev/null`; the error message reads Claude Code's `result` and API status. Closes I-11 |
| I-28 | T10 | **Terms, and so families, are poor.** 32 mixed blocks: 142 terms for 49 nodes, 119 used once (ids, values, clauses, plurals). With term hygiene (F3 D19): 91 terms, 76 used once — but family fallback rose from 16 to 22 of 49, 17 of them with no subject term at all. 19 families for 49 nodes, 22 nodes with none | Two live runs of the full pipeline, reading every term | F3 D19 ⚑ (drop ids/values/clauses, fold plurals, define "term" in the prompt). ⚠ **Main M2-gate risk**: families are the backbone of F5 retrieval and the views |
| I-29 | T10 | 7 of 8 Q-TERM verdicts were `same` and plausible, yet each made its nodes `ambiguous` under F3 D16: 16 of 49 nodes `pending_review` | Live run | **F3 D20** (Q7 option b, owner): `same` merges at once as an alias; a `term_same` item can undo it; `unsure` keeps `pending_review` |
| I-30 | T10 | The split re-ask (AC-3.12) failed permanently for 2, then 3 of 32 blocks — scope bullets ("Storage under `.sdd/`: profile, sources, blocks, runs") and Given/When/Then criteria | Live run (I-22 predicted it) | As specified: `atomize_failed`, block stays pending. ⚠ M2 gate |
| I-31 | T10 | The model seldom tags a constraint's scope terms with role `scope`: selector families for 0 of 12, then 1 of 7 `C` nodes. `scope_layers` is answered | Live run | ⚠ M2 gate: prompt, or derive scope from the Q1 quote |
| I-32 | T10 | Measurement hygiene: twice a run's summary line was lost by piping output through `tail` | Reading results | Run reports go to files in full; G4 must keep raw outputs |

| I-33 | T11 | The run lock file `.sdd/lock` collided with F4's judgment-lock folder `.sdd/lock/` | Writing the store layout against F4 §4.1 | Renamed `.sdd/run.lock` (**F4 D8** ⚑) |
| I-34 | T11 | F4 AC-4.8 said "all **seven**" checks; §4.3 lists eight since rel01 D24 added counters | Writing AC-4.8's test | AC text corrected to eight |
| I-35 | T11 | Two approved rules contradict: F2 §4.9 removes a deleted member from its conflict record; CT-2.4 requires ≥ 2 members | Writing the deletion cascade | **F2 D14** ⚑: a record resolved by deletion keeps its members as history; open records never list a deleted node |
| I-36 | T11 | Attention items piled up: a re-failing block opened a second item; a block completed on retry left its item open (F3 §4.9 says they close themselves) | Live smoke run, reading `review.jsonl` (6 open items, 1 real) | Compile closes items whose block completed, was removed, or whose node was deleted; a repeat failure updates the open item |
| I-37 | T11 | The run report had no model calls or cost, which F3 §4.8 requires — the smoke run's cost went unrecorded | Live smoke run | Calls and cost are metered per run and printed |
| I-38 | T11 | Once `compile` atomizes, the M1 CLI tests (`sddc compile` in a subprocess) would call the live model | Wiring compile | `sddc ingest` (already in F1 CT-1.6) shipped as a sixth command, B2 amended ⚑; M1 tests use it; compile is tested in-process with the fake backend |

| I-39 | T12 | F3 §4.7 keys the lock by question input; with batching (rel01 D30) a per-call key would re-ask a whole 20-block batch when one block changes | Designing the lock against batching | **F3 D21** ⚑: one lock record per item, keyed by content, call usage stored once (`batch_of`, CT-3.2); instructions in the key so a prompt change re-asks |
| I-40 | T12 | Alignment called a case-only edit (`by` → `BY`) `unchanged` and kept the node's **old text**: the comparison lowercased, though F1 treats case as meaning | Live edit test | Equality is case-sensitive (only whitespace ignored); scoring still ignores case. Live re-check: `edited`, id kept, text current |
| I-41 | T12 | A rebuild from sources + lock is byte-identical **only from a compile without failures**: failed items are never locked, so a rebuild asks them afresh, may succeed, and the node ids after them shift | Live rebuild of `vision.md`: 127 replayed, 11 calls — all for the 5 blocks that failed in the original; content of every completed block identical | As specified (AC-3.19 presumes a completed compile). ⚠ On a real corpus with some failures, node ids depend on the history of retries — judge at the M2 gate whether that matters |
| I-42 | T12 | 4 of 31 `vision.md` blocks fail **every** run, all one shape: a list item with a **bold lead-in title** plus its explanation. Title and body answer layer questions with non-overlapping quotes → `split_required`; the model rightly keeps one claim → failed twice. Each compile re-pays for them (≈ $0.08–0.11 per run here) | Live runs; reading every `atomize_failed` item | **Fixed — F3 D23, F2 D15** (owner): after the split re-ask, the node is formed with the first yes's layer and ambiguity `mixed_layers` |

| I-43 | — | **A backend failure mid-run loses the whole run.** Only the call cap (exit 5) keeps finished chunks; a backend error (exit 6) — e.g. the 429 usage limit, hit twice live — propagates before the write, so every finished chunk *and its lock records* are discarded and must be paid for again | Reviewing the pipeline before a large compile, with the owner's session usage at 86 % | **Fixed — F3 D24** (owner): exit 6 behaves like exit 5; finished chunks and lock records are written |
| I-44 | — | Sessions S19 … S25 and their decisions were stamped 2026-09-19; they happened on 2026-09-18 | Owner's usage report showed today's date | Corrected in every file |

| I-45 | M2 gate | Q-TERM crashed (`KeyError`) when B was judged the same as A after A had merged away in the same batch — a path F3 D20 opened and no test covered | Gate run 2 | Merges follow the chain to the surviving term; test added |
| I-46 | M2 gate | Q-TERM calls hyponyms "same": ≈ 10 of 16 merges in run 1 ("term id", "judgment id" → `id`). The T10 sample (7 of 8 plausible) was too small to show it | Reading every `term_same` item | Gate finding G-3; recommendation R1 (owner) |
| I-47 | M2 gate | Two fresh runs of the same 63 blocks agree on node count for 49 % of blocks; for single-node blocks, on layer and family 10 of 16 | Comparing the runs | Gate finding G-6: reproducibility comes only from the judgment lock |
| I-48 | M2 gate | The usage limit hit mid-gate (429): the I-43 fix, written an hour earlier, kept 18 finished blocks and the resume replayed 54 answers | Live | Validates F3 D24 |

| I-49 | R6 | The family targets set for R6 (terms used once ≤ 50 %, one-node families ≤ half) cannot be judged on a sample scattered across nine files: after the fixes it yields 43–53 claims, as few as 2 per file. Earlier runs looked better partly because fragments of one criterion shared a family | Reading the R6 numbers against the sample's design | Target design error, owned; proposal R12 (a dense sample) |

| I-50 | R12 | The session restarted (a re-login) and the operating system's temporary scratch area was cleared: the stores of the gate and R6 runs, and the finished-but-unread R12 result, were lost. Findings survived only because they had already been written into `M2-gate.md` | Reading R12's result after the restart | R12 re-run; its summary report is now written into the repo, `sdd/design/rel01_design/measurements/`. G4 must keep raw measurement output in a durable place (I-32 again) |

| I-51 | M3 gate | `sddc family "(no family)"` exited 2, while the error message itself listed `(no family)` as a known family: the drill-down map → card broke on the row most worth reading. "Not found" and "the unplaced family" were both `None` | Reviewing the gate: trying every map row | `family_of` raises `KeyError` when unknown; `(no family)`, `_unplaced`, `global` resolve. Test added |
| I-52 | M3 gate | AC-4.18's property test checked `map_counts`, a helper that `map_table` did not call. The rendered map could have shown any count and the test stayed green: the §4 "quiet failure" | Reading the test against the code | The map now takes its counts from `map_counts`, and the test parses the **rendered** table back on 50 random graphs |
| I-53 | M3 gate | Every card of a store with unplaced nodes said "Kind of: (no family)": `broader: null` matched the unplaced family's key, `None` | The first render of the real R12 cards, after D15 was written; the fixture has no unplaced node | Guarded; the unplaced test now asserts it. Second time a real card found what the golden could not (after D12) |
| I-54 | M3 gate | The gate evidence held the two best cards, `candidate` and `pair_key`. The largest family, `node` (12 of 43 nodes), fails the gate question | Rendering every card from the surviving R12 store | `R12_views_on.md` now holds all 19 cards and a reading of each, for the owner to confirm |
| I-55 | M3 gate | Cards were hard to read cold: ids sorted as strings (`AC-5.13` before `AC-5.2`); constraints in scope were bare ids, a dead end with `show` deferred; `?` gave no reason; `broader` was invisible, so `checked_node` and `other_node` stood unconnected beside `node` | Reading the real cards | **F4 D13 … D16** ⚑: source order, constraints as lines, "Kind of / Narrower families", `? (referential)`. Map unchanged. Text width stays open (F4 Q2) |
| I-56 | M3 gate | **Families rarely read as a group:** 3 of 19 cards (12 of 43 nodes) coherent. Nine S1 … S7 criteria sit in `node` because "Given two nodes…" gives the subject. Exhaustive mode (≈ 5 claims) has no family. Fragments ("deterministically") form their own family | Card-by-card reading | **Fixed in code (owner: "fix as suggested")**, three causes found in the data (see I-59, I-60): **F2 D18**, a criterion that resolved `verifies` takes that family before its Given-clause subject; **F2 D20**, local labels (`S1`, `D3`) resolve inside their file; **F2 D19**, a `component` subject names the family as a last resort. With F3 D32 (I-59). ⚠ Fragments not addressed. **Unmeasured until R15** |
| I-57 | M3 gate | **Constraint scope floods retrieval.** 13 of 19 cards list in-scope constraints, mostly three constraints scoped only by layer. By the card's rule, S3 would propose ≈ 60 pairs among 43 nodes. At weight 2.0 over `min_score` 1.0, S3 alone makes a candidate and outranks S7 (same block, 1.5) | Seeing the same three ids on most cards; counted on the R12 store with the card's coverage rule (F5 code does not exist yet) | **Fixed — F5 D9** (owner): a layer-only scope needs a shared term or keyword, the bar F5 D7 set for `(global)`; layers narrow a named scope. One function, `model/scope.py`, serves the card and S3. Same R12 store: ≈ 60 → **16** S3 pairs; cards with in-scope constraints 13 → 10 of 19. AC-5.3 amended |
| I-58 | M3 | F4's traceability claimed AC-4.14, AC-4.17 and AC-4.18 as built, but each names `sddc map` or `query map`, both deferred (B2) | Gate review | Rows marked *partial* and saying what is built |

| I-59 | I-56 fix | **F5's core rules were not in the graph.** Q-ATOM labelled all seven S1 … S7 table rows `definition` and formed no node, and each block still counted as completed. F2 §4.1 says definitions become term-registry entries, but no code writes them (`defined_by` is always null). A `definition` sentence is dropped without a trace | Checking whether the rows a criterion cites exist, before writing the fix | **F3 D32** ⚑: `definition` only for "what a word means"; a row stating behaviour is a claim. ⚠ **Open:** a producer for definitions, or a run-report count of blocks that formed no node. The I-26 pattern again: readers, no writer |
| I-60 | I-56 fix | My I-56 suggestion ("let `verifies` resolve `S1`") assumed the S1 … S7 nodes existed. They did not (I-59). Resolving citations alone would have changed nothing | Reading the R12 store before coding | Fixed the cause first (F3 D32), then the resolution (F2 D20). A suggestion made from reading a view must be checked against the records before it is built |
| I-61 | I-56 fix | F2 D9 ("rules literally in order") was argued from a `C` example (files stay in `file`) and applied to `V` unexamined. For a criterion, the subject is the fixture | Tracing why nine criteria sat in `node` | **F2 D18** amends D9 for `V` nodes only |
| I-62 | M3 gate | The gate's question ("describe a family from the view alone") had no pass line and was answered by the specs' author | Gate review | **Gate protocol** (§3): pass line first, every output or a blind sample, a first-time reader, one verdict per item, durable |

| I-63 | R15 | 4 of 66 blocks failed, all one shape: the model quoted the `section` heading or the `table header` that the prompt gives as context. Three were the `S1`, `S2` and `S6` rows, so the criteria testing them stayed in the `node` grab-bag | R15's failure list | **F3 D34**: Q-ATOM is told never to quote the context lines — the rule Q-DESC has had since I-15. ⚠ The same fix was needed twice, in two prompts, 3 days apart |
| I-64 | R15 | With rows atomized (D32), F5's `S3` row came back as **one atom per cell**: one rule became three fragment nodes in three families (`scope_selector`, `scope_selector_coverage`, `selector`) | Reading the nodes formed from lines 57–63 | **F3 D34**: a table row folds into one atom in code, as `AC-` blocks already did (D28). A prompt line says the same |
| I-65 | R15 | Fixing the loss made the graph **wider, not denser**: 97 terms for 64 nodes (R12: 45 for 43), 58 % used once, and only 42 % of nodes in a family of three or more (was 56 %). 15 of 64 nodes are `C`, 13 scoped by layer alone | Comparing R15 with R12 | ⚠ **Open.** More content captured, spread over more names. F5 D9 contains the scope consequence, not its cause (Q-DESC's generous `scope_layers`). Judge at the M4 gate, against retrieval, not in isolation |

| I-66 | R15 reading | The blind reader called the card's "In scope from elsewhere" list **boilerplate**: the same six constraints repeat on more than ten cards. F5 D9 cut the pairs from 178 to 42, and what survives is still noise on a card | The first-time reader's own observation | ⚠ **Open, small.** Options: list only constraints whose selector *names* the family (not a keyword match); or show a count with the ids behind a drill-down. Decide with the owner; it is a view change, not a graph one |

| I-67 | R16 | **The run crashed after every model call was paid for.** Q-ATOM merged two of F5's sentences into one `rationale` quote; `block_annotations` located annotation quotes with the guard that *raises*, outside the re-ask path, at node-forming time. $1.20 and 25 minutes lost, and no lock record written, so nothing was replayable | R16's first attempt died with an uncaught `GuardFailure` | **F3 D35**: an annotation carries no claim, so an unlocatable one is dropped and reported (`annotations_dropped`). R16 re-run |
| I-68 | R16 | **I-43's guarantee is narrower than it reads.** "A stop keeps finished work" covers the two expected stops, exit `5` (cap) and `6` (backend, F3 D24). Any *unexpected* exception — I-67's, or the next one — still discards every finished chunk **and its lock records**, because both are written in one transaction at the end | Tracing why I-67 cost the whole run | ⚠ **Open, owner.** Options: (a) write lock records per chunk, so a crash costs one chunk; (b) catch any exception in the chunk loop, write what finished, and exit with a new internal-error code — CT-1.6 has none, so it needs the owner. (a) is the cheaper half and helps every long compile |

| I-69 | R16 | **The measurement has no still control.** R16 was launched as "same source, changed code" and was not: the copy of F5 was taken after T15 had added F5 D10 and filled its traceability table — 16 lines, ≈ 5 blocks. The corpus *is* this repository, and it is edited while it is measured | Diffing the two runs' sources after reading the numbers | ⚠ **Open, cheap.** Copy the corpus **and record its hash** in the measurement file before a run, and compare hashes before comparing numbers. Until then, every A/B on our own specs is a direction, not a controlled comparison |

| I-70 | R16 reading | **The split re-ask undid F3 D34.** A table row's atoms are folded into one claim on the first pass, and then AC-3.12's re-ask asked the model to separate the row's rule from its evidence cell — and it did. All seven of F5's source rows became two nodes, one a bare fragment ("the term ids", "the block id"), which spawned five one-node families the blind reader called unintelligible | The R16 blind reading named the fragments; the store confirmed two nodes per row | **F3 D36**: a block that is one claim by its own form (a table row, an `AC-` block) is placed by its first yes and flagged `mixed_layers`, never asked to split. Decided in the first pass, so it also saves a call |

| I-71 | M4 gate | The gate's first compile died on its **first** model call: the account's session limit (429). Exit `6`, nothing atomized, nothing lost | Reading the run's summary | No defect — **F3 D24 working as designed on a real 429**. Worth recording as the first live proof of I-43's fix |
| I-72 | M4 gate | The check phase stopped after 72 of 123 pairs with **93 of 200 calls used**, and the report said *"the call cap stopped the run"*, exiting `5`. It was a backend 429. A report that names the wrong cause sends the reader to the wrong fix — raise the cap, which would have changed nothing | Comparing the calls used against the cap in the run summary | **Fixed:** the check phase records which limit stopped it (`stopped`, `stop_reason`), the report names it, and a backend stop exits `6` |
| I-73 | M4 gate | **The misses are in ranking, not judging.** All six planted pairs were proposed as candidates; five ranked 81st–130th of 137 and were never reached, because each side of each pair carries a different term (`export_archive` vs `workspace_export`), so S1 (3.0) and S2 (2.0) are dead and only S5's keyword overlap fires, at exactly `min_score` | The M4 gate's per-pair diagnosis | ⚠ **Open, owner — R15.** Options: Q-TERM merges phrasings of one thing; or a source that fires on the same quantity dimension *without* a shared term. This is I-65 (term proliferation) with a price on it |
| I-74 | M4 gate | **8 of 11 reported conflicts are false**, and 5 of them are one mistake repeated: the judge reads two different numbers about related objects as a contradiction — a 24-hour link inside a 30-day archive, a 13-day restore inside a 14-day window — and once invented arithmetic ("day 30 versus day 31") | Adjudicating every record with `sddc conflicts judge` (T19) | ⚠ **Open, owner — R16.** One prompt rule: two numbers conflict only when both must hold for the same object at the same time |
| I-75 | M4 gate | **The cost model does not reach this repository.** 28 blocks cost $1.30 and 93 calls with a third of the pairs unjudged; `sdd/specs/` is 733 blocks. G4's "one number for the close" — conflicts on our own specs — is not affordable on the `claude-code` backend at ≈ $0.014 per call | Extrapolating the gate's cost | ⚠ **Open, owner — R18.** Either the `anthropic-api` backend (rel01 D30's plan), or close rel01 with the fixture as the measured corpus and say so plainly |

| I-78 | R19 | Fixing I-76 raised a fair question about **P6**: Q-TERM judged "download link" **different** from "share link", so no relation reaches either retrieval or the judge. The fixture means them as one thing — the link you download the archive with | Measuring the I-76 fix offline: P6 gained nothing | ⚠ **Open, owner.** Not a code defect: the model made a defensible call on two names that a human reads as one. It is the same lesson as I-76 from the other side — **the term layer decides what the rest of the pipeline can see** |
| I-76 | R17 | **The naming problem moved from retrieval into the judge.** R15 delivered the two quantity pairs to the judge (rank 123 → 63, 81 → 42) and it refused them in those very words: *"the two claims govern different export types ('export archive' vs 'workspace export')"*. The model reads two objects where the spec means one | R17's per-pair verdicts, read against the answer key | ⚠ **Open, owner.** No retrieval tuning reaches this: a pair the judge is *told* about is still refused. Term hygiene at atomization (I-65) is the one lever left, and it is now the release's biggest quality item |
| I-77 | R17 | **R16's rule did not fully take.** The prompt says in as many words that an acceptance criterion restating its requirement is design, not duplication — and the judge still opened CF-000002 for exactly that | Adjudicating R17 | ⚠ **Open, small.** Either the rule needs to be a code check (a `V` node against the requirement it `verifies` is never a duplication) or the prompt needs the rule closer to the answer format. Code is the surer of the two |

| I-79 | C (dogfood) | The first compile of **real specs** (F5 + F6, 173 blocks) ended after **19**: one Q-ATOM call over 20 dense blocks returned no `structured_output`, which the backend raised as "backend unavailable", exit `6`. The $0.39 of finished work was kept (D24), but the run was over | The dogfood run's stop reason | **F3 D37**: `AnswerRejected` — one unusable answer is re-asked per item by the batch layer, as a guard failure already is. A dead backend, a missing binary and a 429 stay exit `6` |

| I-80 | C (dogfood) | **The compiler found a defect its author had made hours earlier.** F5 D13 changed `max_pairs_per_node` to 6; D6, §4.3 and AC-5.10 kept 10. Three of the four real finds are that one defect, in three places | The dogfood's own output, adjudicated | Fixed in F5 the same hour. **This is the product's purpose demonstrated on its own specification** — and evidence for the close that a spec set drifts within a single working day |
| I-81 | C (dogfood) | **Precision on our own specs is ≈ 10 %, against 71 % on the fixture**, and the reason is structural: **65 of 70 conflicts involve an acceptance criterion or a decision entry**. A criterion restating its requirement, a decision heading summarising its body, two criteria about different situations — the document's own form, read as defects | Counting the members of all 70 records | **F6 D19** (partly): a `duplicates`/`subsumes` verdict between a criterion and a claim of its own spec file, or between two claims of one block, is suppressed in code — 27 of the 70 on the dogfood store, none of the four real. ⚠ **Still open:** contradictions between criteria describing different situations (18 of 70, one real) — the judge needs the *Given/When*, not a layout rule |

| I-82 | — | **Every `$` in this repository was labelled "cost" and is not spend.** The figure is Claude Code's own `total_cost_usd` per call, which we sum — an estimate of the equivalent **API list price**. These runs go through the `claude` CLI on the owner's **subscription**: no organization credits move (the owner checked the Console and saw none), and the Usage & Cost Admin API would show nothing, because it reports API traffic. The 429s we hit say "session limit", which is the subscription's, not an API rate limit | The owner asking why the Console showed no deduction | Relabelled in G4 §2 and M4-gate §7 as **estimated API-equivalent cost**. ⚠ Every earlier figure (R12 … R21, both gates) carries the same caveat. Real API spend, if the `anthropic-api` backend is ever used, is readable from `GET /v1/organizations/cost_report` with an Admin key |

| I-83 | R18 round 7 | **The second round of judging crashed, and the store had been silently inconsistent since the first.** `compile` folded the lock's counter into `id_counters.judgment` *before* the check phase and never after, so round 6's 532 Q-PAIR records (J-002777 … J-003308) left the counter at 2776. Round 7 re-issued J-002777 for a new record, which overwrote a stored Q-PAIR answer in memory; the replay index, rebuilt only when the record count changes, then served that Q-ATOM/Q-DESC answer to a Q-PAIR question → `KeyError: 'relation'`, exit 1, after 2 minutes. Had it not crashed, the write would have replaced 532 pair verdicts with whatever reused their ids. **`check_store` reported the store clean throughout**: F4 §4.3's counters check stood `judgment` in with an empty id list, so it could never fail | An unhandled traceback (handover §4: stop, fix test-first); the stored counter compared with the highest id in `.sdd/lock/` | **Fixed, 3 tests** (suite 626): the counter is folded in again after the check phase (`pipeline.py`); the counters check reads judgment ids from the lock (`store/graph.py`); a lock never issues an id it already holds, whatever the stored counter says (`atomize/lock.py`) — which also heals the R18 store on its next write. No spec change: F4 §4.3 already required it. Round 7 restarted. ⚠ **The I-26 pattern again, in a check**: a rule with a reader that was handed nothing to read |
| I-84 | R18 rounds 1 … 6 | **Seven blocks fail on every retry**, so `pending` sticks at 7 and pass-line F1 (`pending` 0) cannot be met by rounds alone. Five are G2 rejections of real paraphrases — the model drops a word ("null *only …* or together with"), drops `with exit 5`, drops quotation marks around "span overlap", or rewrites a table row's cells as a sentence (vision.md:62); two are G3 coverage failures on decision-entry sentences (`*Rejected:*`, `*Narrows*`). Meanwhile 33 earlier failures resolved on a later round | Reading every open `atomize_failed` item after round 6 | The guards are right; the answers are wrong. Not hand-fixed mid-run (it would change the pinned corpus's behaviour). **By the end, retries had cleared six of the seven**: one block remains, B-000243 (F2 D12's `*Rejected:*` sentence, G3 coverage), so the run finished with `pending` 1. ⚠ **Open, owner:** re-ask with the G2 diff shown (the quote vs the nearest source span), or accept a small residue of unatomizable blocks and restate pass-line F1 |
| I-85 | R18 round 7 | **A stopped check phase silently dropped the pairs it had not reached.** Round 6 hit the cap with **1 866 of 2 418 pairs unjudged**, said so (`incomplete`, exit 5) — and marked **every** node it had proposed as checked (`last_checked_run`), so round 7 proposed only 506 pairs and reported the compile **complete**: `unjudged` 0, `incomplete` false, exit 3, store clean. Every number true, the conclusion false. F6 §4.7 and **AC-6.12** say in words that "unjudged nodes keep `unchecked` or `stale`"; none of the three AC-6.12 tests asserted that clause | Round 7's candidates (506) against round 6's unjudged (1 866); then `status` after round 6 showed 0 `unchecked` nodes | **Fixed, 1 test** (`conflicts/pipeline.py`): on a stop, a node that is an end of any unreached pair is not discharged. **Store recovered** (backup `.sdd.bak-before-I85-reset`): `last_checked_run` cleared on the 406 nodes round 6 stamped, through `write_graph` (checks clean); their judged pairs replay from the lock. ⚠ **The I-6 pattern exactly**: a stored "this run looked at it" flag standing in for "nothing is left to do". And I-52's: a test green on the AC's easy half |
| I-86 | R18 round 7 | **An `ambiguous` node never started a check of its own.** F5 §4.1: an ambiguous node is checked "when it was never judged". The code read "never judged" as `judgments` empty — but `judgments` lists the Q-ATOM/Q-DESC answers that *formed* the node, so it is never empty on a real graph. **416 of 937 nodes (44 %)** were reached only when some other node happened to propose them. The unit test encoded the misreading (`judgments: ["J-000001"]` → skip); fake nodes are built with `judgments: []`, so nothing in the suite formed a real one | Tallying nodes by `(status, last_checked_run, judgments)` while diagnosing I-85 | **Fixed** (`retrieval/select.py`): "never judged" is `last_checked_run` null. AC-5.14's test corrected, 1 test added (suite 628). ⚠ It also bore on the dogfood (M4-gate §7): its ambiguous nodes were under-checked too, so its pair and conflict counts are a floor |

| I-87 | R18 | **The full compile cost twice its estimate: ≈ $54.94 estimated API-equivalent, 2 673 calls, 16 rounds, 9 h** — against the handover's ≈ $26, ≈ 850 calls, 4–6 rounds. Three causes, measured: (1) **I-86's fix nearly doubled the work** — candidate pairs 2 418 → 4 268 once ambiguous nodes proposed their own, so the handover's figure, extrapolated from a dogfood that had the same defect, was a floor; (2) **Q-PAIR is the cost**: 4 251 verdicts, ≈ $25.67 of the total, Q-DESC ≈ $9.05, Q-ATOM ≈ $5.50, Q-TERM ≈ $1.48 (per-call usage in the lock); (3) **30 % of calls kept nothing**: 1 860 of 2 673 calls produced an accepted answer; the other 813 (≈ $13.24) went to answers the guards rejected, with or without a successful re-ask — failed atomize retries each round, and pairs whose batch answer failed a check and were re-asked alone (up to 56 pairs failed twice per round) | Summing every round's JSON, then the lock's per-call usage by question kind | Recorded, not fixed. ⚠ **Open, owner.** Levers, in order of size: fewer pairs (min_score / cap, F5 D13 measured on a fixture); a re-ask that shows the G2 diff (I-84) so retries stop paying twice; the `anthropic-api` backend removes the ≈ 22k-token harness prompt per call (I-8). **Every estimate this project has made from a smaller corpus has been low** (C: 3×, this: 2×) |
| I-88 | R18 (operations) | My watcher for the round driver waited on `pgrep -f "bash ./driver.sh"` — and its own command line contains that string, so it matched itself and never exited. The compile finished at 23:46 and nothing said so until the owner asked, seven hours later | The owner: "has R18 run complete?" | Killed by hand. No product code. Lesson for the next long run: wait on a PID or a done-file, never on a pattern the waiting command itself contains |
| I-89 | R18, found writing the as-built lecture | **Judged links are stored again every time their verdict is replayed.** `conflict` nodes are re-checked every run (F5 AC-5.14), their pairs replay from the lock, and `_apply_check` appends the verdict's link to `graph.links` without looking for the one already there. The R18 store holds **9 682 link lines for 4 199 distinct links** (1 086 keys repeated; `AC-3.19 refines N-000008` nine times, one judgment, J-003397). Conflict records are keyed by id and are **not** affected — the 381 stand. `check_store` has no link-uniqueness check, so the store reads clean | Exporting a family to Mermaid for the lecture: every arrow drawn several times | **Fixed 2026-09-24, 4 tests** (suite 632): the check phase keeps one link per `(from, type, to)`, and every write de-duplicates before it checks, so a store written before the fix heals even on a run the cap stops mid-atomization; F4 §4.3's "unique ids" row now names link keys (it was already F2 §4.8's rule). **R18 store healed** without model calls through `write_graph` (backup `.sdd.bak-before-I89-heal`): 9 682 → 4 199 links, checks clean. **The I-83 lesson again: a check only catches what it was written to look for** |
| I-90 | found writing the as-built lecture | **`jsonschema` is imported but not declared.** `model/schema.py` and `atomize/guards.py` import it; `pyproject.toml` lists only `PyYAML` and `markdown-it-py`. A clean `pip install -e .` installs, then every command fails on import. Invisible here because the development environment already had it | Listing third-party imports against `[project] dependencies` | **Fixed 2026-09-24:** `jsonschema>=4.18` added to `dependencies`; verified with `pip install -e .` into a clean virtual environment, then `sddc status` on the R18 store. `anthropic` stays an undeclared optional import (the API backend imports it lazily) |
| I-91 | found fixing I-89 | **A re-judged pair keeps its old link.** When a pair is judged again and the verdict changes — `contradicts` → `none`, or `refines` → `depends_on` — the conflict record closes correctly (`fixed`), but the old judged link (`conflicts_with`, with its old judgment id) stays in the graph beside the new one. Reproduced with the AC-6.16 scenario: record `resolved/fixed`, link `N-000001 conflicts_with N-000002` still present | A scripted re-judgment while testing the I-89 fix | **Fixed 2026-09-24, as recommended (owner).** Spec first: **F6 D20**, a §4.5 rule and **AC-6.24** — a pair that receives a verdict (asked or replayed) keeps only that verdict's judged links, in either direction; a pair that failed twice keeps its old ones. Code: `check` records `judged_pairs`, `_apply_check` replaces their links. 3 tests (suite 635). The R18 store needed no repair: none of its 381 records was ever re-judged |
| I-92 | preparing trial_01 (code generation from the graph alone) | **The graph does not carry everything code generation needs.** Measured on the R18 store: node spans cover **54 %** of the spec text; **183 of 845** blocks form no node, among them **all 25 fenced code blocks**, which are every JSON contract in the specs' "Contracts" sections (the default profile does not atomize code); **0 of 1 031** terms carry a definition (I-59's open half); and **39 nodes** come from Traceability tables, naming the existing `src/` and `tests/` files, so a "from scratch" agent is handed the old implementation's layout | Evaluating whether an agent can generate code without reading `sdd/specs/` (owner's rule for trial_01) | **(a), (b) and (c) built 2026-09-27; (a)'s conflict noise still to be measured live.** Both in code, not in a prompt, so the lock still replays (F3 D21). **(c) F1 D14:** profile key `skip_headings` (default `["Traceability"]`) takes those sections out of the pending set, like code blocks; a newly skipped block's nodes are deleted and its `atomized_hash` cleared (F3 §4.6, AC-1.32, AC-3.34). On a copy of R18: 39 nodes deleted with no model call, **43 new pairs** for Q-PAIR from the freed retrieval slots. The lever first written here — a Q-ATOM prompt rule — was rejected: it re-asks every block. **(b) F3 D38:** Q-ATOM's `definition` sentences are attached by code to the term the sentence opens with, followed by a definitional boundary; CT-2.2 gains `definition` (the verbatim sentence), since an agent cannot follow `defined_by` into `blocks.jsonl` (AC-3.31 … AC-3.33). On R18's data: **15 terms defined, all read and correct**; 48 sentences match no term and 2 repeat one, all listed in the report. A looser match attached 38, many wrongly. ⚠ Small yield: few terms are defined in "X is Y" form. ⚠ A store compiled before this refuses to write until rebuilt (terms lack `definition`), and a rebuild is not free: re-atomizing a copy of R18 still needed live questions (a split re-ask missing from the lock); cost *to be measured*. The 15-term figure is the shipped matcher run over R18's lock answers and terms, not a rebuilt store. 20 tests (suite 657). **(a) built 2026-09-27 (owner: node design, `text` blocks included, `CT-` ids).** F1 D15: profile key `contract_languages` (default `json`, `yaml`, `text`) makes those fenced blocks pending. F3 D39, §4.5a: code forms each as one `requirement` atom (no Q-ATOM); Q-DESC reads it with its lead paragraph, so a subject named only in the title passes G2/G4; the lead enters the lock key only for contracts (AC-3.37). F2 D21: the contract adopts its title's `CT-` id, the title's nodes keep it as `label`. 13 tests (suite 670). *Estimated* on a copy of R18 with a stand-in Q-DESC: 25 nodes, 22 `CT-` ids, 0 `inferred`, 4 Q-DESC calls, **191 new pairs touching a contract** (+ 37 from the Traceability deletion). ⚠ **Open:** a live run to see how many become conflicts, before any suppression rule |
| I-93 | full human adjudication of R18's 381 open conflicts (M4-gate §8) | **F6's precision on this repository's own specs is far below the M4 pass line.** All 381 records adjudicated (not just the drawn 100): **1 real (0.26 %)**, against a pass line of ≥25 %. The dogfood (§7 of M4-gate, 70 records) had already measured ≈10 %; the full corpus, at four times the sample size, measured 26× worse. Every false verdict falls into one of nine recurring shapes, all traced back to the atomizer or F6 not knowing a spec document's own structure: (1) an acceptance criterion's different Given/branches read as simultaneous — by far the largest class; (2) the same English word naming two unrelated things ("status", "family", "flag", "allocated"); (3) a scope-overview or "In scope" bullet read as a normative claim; (4) one compound sentence split into atoms, then compared against its own siblings; (5) deliberate repeated boilerplate (the coding-gated banner, a status summary table); (6) a mechanism and its own decision-log entry or rationale, often already cross-referenced by a citation the compiler doesn't resolve; (7) a correct general-rule/specific-instance pair, not a defect at all; (8) a traceability-table row (pure `AC-id \| test file \| code file` bookkeeping) compared as a behavioral claim; (9) sequential lifecycle states (set, then later cleared or superseded) read as holding at once | R18 M2 adjudication, all 381 records, 2026-09-27 | ⚠ **Open, owner.** §7's finding named two of these levers (`verifies` resolution for AC-vs-rule, decision-heading-to-body linkage); this run adds seven more shapes and turns the estimate into a full-corpus count. Candidate fixes, cheapest first: (a) D16-style suppression for shapes 6 and 7 wherever a citation already names the link (F2 §4.9, F3 §4.7 style refs) — no model change, a linking pass over existing citation text; (b) exclude Traceability-table rows and "In scope"/goal-overview list items from atomization or from F6 candidate generation (shapes 3 and 8 — pure bookkeeping, no behavioral content by construction); (c) teach Q-PAIR to recognise a term/word collision by checking whether the two claims' families or documents are unrelated before judging (shape 2); (d) shape 1 (different-situations-as-simultaneous) is the largest and the hardest — needs Q-PAIR to read a `Given`/condition clause as scoping the claim, not just its consequent, which may be a prompt change rather than a suppression rule |
| I-94 | I-92 (a) live run, `~/sddc-runs/i92a-live` (copy of R18, 2026-09-28) | **Contract blocks are hard for the model to quote, and my call estimate was 5× low.** Option 1 (contracts + the Traceability skip on R18, lock replay for the rest) hit the **200-call cap**: 198 calls, ≈ $3.88 estimated API-equivalent, exit `5`, finished work written. Q-DESC failed G2 twice on **7 of 25** contracts: the "quotes" were key lists pulled out of the JSON, summaries ("has fields: …"), the model's own commentary, and once my per-item hint text ("shape, format or output") — a whitespace-insensitive match would rescue only 1 of 7. Q-PAIR failed twice on **67 of 149** pairs it asked (reason not recorded: Q-PAIR does not keep why an answer failed). 619 pairs counted `unjudged` are mostly replayable: every `conflict` node (445) is re-checked each compile by design (F5 §4.1), and the cap stops replay too. **8 conflicts opened, 2 real:** CF-000384 — CT-5.1's example has score 5.5 but evidence points 2.0 + 2.5 = 4.5, against AC-5.9; CF-000387 — F6 counts `suppressed` "(CT-6.2)" but CT-6.2 has no such field (the judge named CT-4.1). Dry run for option 2 (re-atomize all, stand-in backend, no calls): **139 first asks** — 39 Q-ATOM (38 split re-asks, never replayed by design, + B-000243), 15 Q-DESC, 2 Q-TERM, 83 Q-PAIR for 218 pairs; 911 nodes align `unchanged`, so ids and adjudications survive; 14 definitions attach. Re-asks come on top | Running option 1 and the option-2 dry run | **Built 2026-09-28 (owner: 1, 2c, 3).** (1) the per-item hint is gone; (2c) **F3 D40**: the contract atom asks for the title or one whole line, and code replaces a contract quote it cannot find (layer → the whole contract, term → where its name is written or dropped, ambiguity → null), each listed in the report (AC-3.39); (3) **F6 D22**: `failed` keeps each unjudged pair and why (AC-6.25). 6 tests (suite 676). Option 1 resumed with cap 300; a dry run sized it at ≈ 80 first asks (7 contracts, B-000243, 200 pairs). **Round 2 (R-000020):** complete, exit `3`, 238 calls, ≈ $4.55 estimated API-equivalent (option 1 total 436 calls, ≈ $8.43); all 25 contracts formed (the per-item rule alone was enough: 0 quotes replaced); B-000243 failed again (I-84); `check_store` clean. **Q-PAIR failed twice on 110 pairs, 109 of them "quote not verbatim", 102 touching a contract** — the same JSON-quoting problem, and a failed pair is never locked, so it is re-asked on every compile. 11 conflicts opened, 0 real. Across both rounds: 19 conflicts from contracts, **2 real (CF-000384, 387), both contradictions; all 12 duplication/subsumption records pairing a contract with a claim of its own spec are false** (contract vs a rule restating part of it). **Built 2026-09-28 (owner):** **F6 D23** — a contract's unfound Q-PAIR quote becomes its whole text, counted as `quotes_replaced` (AC-6.26); **F6 D24** — a contract never duplicates or subsumes a node of its own file, contradictions still reported (AC-6.27); `compile` passes the contract node ids to the check phase. 8 tests (suite 684). Option 2 started on the option-1 store (every `atomized_hash` cleared; backup `.sdd.before-option2`); dry run: 39 Q-ATOM (38 split re-asks + B-000243) and 44 Q-PAIR calls for 85 pairs, 936 nodes `unchanged`, 14 definitions. **Option 2 live (R-000021):** stopped at the cap — 299 calls, ≈ $4.89 estimated API-equivalent, exit `5`, `check_store` clean. ⚠ The dry run's premise failed: live split re-asks did not answer as R18 did (24 nodes `edited`, 10 `removed`, 9 `new`, 1 `merged`, 1 `split`; 11 deleted), and edited nodes send their neighbours back to the judge — 275 pairs judged live, not ≈ 85. 779 of 791 blocks completed; 11 prose blocks failed their split re-ask on paraphrased quotes (they keep their R18 nodes and stay pending) plus B-000243. D23 replaced 55 contract quotes; 119 verdicts suppressed; **12 records closed on re-judging**: 8 of the 12 false contract-vs-own-spec records (D24; the other 4 are among the 130 pairs not yet reached) and CF-000033, 067, 247, 272 (edited nodes). 17 opened, 386 open. 11 definitions attached so far. **I-92/I-94 runs so far: 735 calls, ≈ $13.32 estimated API-equivalent** (option 1: 436, ≈ $8.43; option 2: 299, ≈ $4.89). Not finished: 12 pending blocks, 130 unjudged pairs. R-000022 hit the session limit on its first call (0 calls, exit `6`, nothing written but its run record). **Finishing round R-000023:** complete, exit `3`, 99 calls, ≈ $1.80 estimated API-equivalent; every pair judged (10 failed on quotes), 4 of 12 blocks completed. **Final store:** 933 nodes (25 contracts, no Traceability nodes), **11 terms defined**, `check_store` clean; **8 blocks still fail** every retry — B-000243 and 7 prose blocks whose split re-ask paraphrases (the I-84 class); they keep their 21 older nodes. Conflicts: 349 of R18's 381 still open (23 closed `member_deleted`, 9 `fixed`; none of them one judged real), 41 new (31 open: 20 contradiction, 10 subsumption, 1 duplication; CF-000384 and 387 among them); D24 closed 10 of the 12 false contract-vs-own-spec records — CF-000390 and 397 stay open because their pairs were not proposed again (D24 acts only on a re-judged pair). **I-92 runs total: 834 calls, ≈ $15.12 estimated API-equivalent** |
| I-95 | M6 built; `sddc export --allow-open` on a copy of the pilot graph (`~/sddc-runs/export-trial-01`, 2026-09-30) | **The export is 4.57× the Markdown.** `chars.export_total` 735 170 against 160 721 source characters (derived: 735 170 / 160 721). Measured by section over all 59 packs: block text ≈ 170 k; the lists after it ≈ 530 k — Related elsewhere 159 k, Constraints in scope 151 k, Claims 121 k, Terms 46 k, Acceptance criteria 37 k, Conflicts 18 k; the checklist and map are extra (112 k + 21 k). Largest packs: F3 Behaviour 64 k, F3 Decisions 60 k, F2 Behaviour 40 k, foundation 39 k. Cause (read from the output): each list repeats full node text, and 175 layer-`C` nodes are each listed in every pack whose nodes their selector covers | G3-3 §6 check 2: a total above the Markdown's is a finding to explain *before* any study run; it cuts against the goal that the agent reads no more than the Markdown gave it | **Fixed 2026-09-30 (owner, F7 D14).** Constraints in scope list only selectors that name a family, term or category; broad ones (empty or layers only, 132 nodes) are listed once in pack 00; `refines`/`subsumes` links are ids only; terms only with a definition or aliases. G3-3 §6 check 2 now records the largest pack and the list-to-text ratio; the total is reported, not gated. **Re-measured on the same copy:** total 487 666 characters, **3.03×** the Markdown (was 4.57×; my estimate beforehand, 2.8×, was low); lists ÷ text 1.47; Related 52 k (was 159 k), Constraints 32 k (151 k), Terms 22 k (46 k); Claims unchanged at 120 k. Largest pack now the foundation, 42.7 k (it gained the broad constraints), then F3 Decisions 41.5 k (was 64 k for F3 Behaviour). 3 tests changed, 1 new (AC-7.24) |
| I-96 | same run | **The build order collapses into one cycle of 35 packs (20–54).** Cross-spec `depends_on` links form a single strongly connected group; F7 D3 makes that non-fatal, so the export works, but inside it the order is only source order — the map's "build order" says nothing for 35 of 59 packs. Not measured: how many `depends_on` links sit in the cycle, or whether dropping judged links would break it | The order is one of the four things F7 promises beyond the Markdown | **Fixed 2026-09-30 (owner, F7 D3 revised).** Specs are ordered, not sections: the file order with the least weight of `depends_on` links pointing to a later file (exact for ≤ 8 files, a deterministic greedy pass above), sections in source order inside a file. Measured first: whole files also formed one cycle (all 6 specs + README), and the minimum order breaks 42 of 151 cross-file links. Re-export: order F2 → F1 → README → F3 → F5 → F4 → F6; `MAP.md` *Needs against the order* lists 33 pack pairs, 42 links; `export.meta.json` `backward_needs` replaces `cycles`. AC-7.6 and AC-7.7 rewritten (a property against brute force) |
| I-97 | Phase C1, then checked against the code | **The run record never carried the check phase's counts — a code defect, not a wording gap.** First logged as a spec wording gap; corrected the same day. F5 CT-5.3 and F6 CT-6.2 extend the run record, but all 22 `compile` records in the pilot's `runs.jsonl` hold only F1's four ingest counts: the counts were computed and printed in the report, never written. AC-5.16 looked covered because its tests check `retrieval/select.py`, not the record. The spec also disagreed with itself on where `retrieval` goes (top level in CT-5.3, inside `conflicts` in CT-6.2), and CT-6.2 lacked `suppressed` (the real half of CF-000387). Separately, `sdd/specs/README.md` listed `check` as deferred while the check *phase* runs in `compile` (CF-000407) | The study measures the compiler from its run records (G4); a missing count is a silent gap | **Fixed 2026-09-30 (owner).** Failing tests first (`test_compile.py::test_ac_5_16_ct_6_2_…`, `::test_an_ingest_only_run_records_no_check_counts`), then: the run record gains `conflicts` (CT-6.2, `retrieval` inside it), `null` when no check phase ran; older records read as `null`. Specs: F1 CT-1.3, F5 CT-5.3 and §4.x, F6 CT-6.2 (`suppressed`, `stopped`), README wording. ⚠ The pilot's records stay without counts (frozen); the next compile writes them |

**Patterns so far** (for the retrospective):
- **Check the store before calling it a wording gap** (I-97, 2026-09-30). Three false conflicts looked
  like a spec inconsistency about the run record; opening `runs.jsonl` showed the code had never written
  the counts at all, and the AC looked covered because its test checked a helper, not the record. A
  finding about a contract is verified against the data the contract describes.
- **Size lives in entry counts, not entry lengths** (I-95). The obvious lever, shortening each line,
  saved ≈ 5 %; counting entries showed 999 of 1 123 constraint lines came from one loose matching rule
  borrowed from retrieval. Measure what multiplies before trimming what is long.
- **A rule built for recall is wrong for reading** (I-95). F5 D9's loose selector match is right where
  a judge filters afterwards; reused in the export, nothing filtered it.
- **Model-judged links are votes, not edges** (I-96). A topological order over them collapsed into one
  35-pack cycle; even whole specs formed one cycle. Ordering by the fewest broken links gave the order
  a person would choose. Treat any graph built from model verdicts as weighted evidence.
- **Measure before recommending** (I-96). The first idea — "order whole files instead" — would not
  have worked; a five-line measurement showed it before it was proposed.
- **An estimate scaled from counts is still an estimate** (I-95): 2.8× predicted, 3.03× measured.
  Report both.
- **A scorer that cannot run must not report a score** (Phase D). The first scoring attempt printed
  "install ok, 0 / 0 tests" when the sandbox never started. Every measuring tool fails loud on its
  own failure, not only on the thing it measures.
- **Hidden tests for a from-scratch agent must be black-box** (Phase D). This repository's own tests
  call internals by name; an agent names them differently and would fail for the wrong reason. Test
  through the command and the files it writes, and check the tests both pass on a reference and fail
  on a no-op.
- **The run that measures the product tests the product** (R18). Three defects (I-83, I-85, I-86)
  surfaced only on the first multi-round judge of a real corpus: the id counter, the stop, and which
  nodes get checked. 623 green tests had never resumed a check phase across rounds with more than one
  batch, nor formed an ambiguous node the way the atomizer does.
- **A report can be true in every number and false in its conclusion** (I-85). "Complete, 0 unjudged,
  store clean, exit 3" — each field correct, the whole wrong, because the question it answered ("did
  this run judge what it proposed?") was not the question asked ("is anything left to judge?").
  Cross-check a finish against the previous round's remaining work, not only against itself.
- **A check that can never fail is not a check** (I-83). The counters rule was specified, implemented
  and listed as passing — with an empty list standing in for the one family that lives outside the
  graph. Test each check with a store that violates it, per family.
- **Test fixtures built by hand hide the fields real data always fills** (I-86). Every fake node had
  `judgments: []`; every real one has two. The defect lived exactly in that gap.
- **Estimates extrapolated from a run that had a defect inherit it** (I-87). The $26 came from the
  dogfood, which under-checked ambiguous nodes too; fixing the defect doubled the real figure.
- **A fixed pass line survives a surprise** (R18). The line was written before the run; when the run
  doubled in size and cost and three defects were found, nothing about what "pass" meant moved.
- **Real data finds what specs miss.** I-3, I-6, I-8, I-9 all came from running on this repository's own
  specs or the live model, not from reading the spec. Run on the real corpus at every task, not only at
  gates.
- **A stored flag that describes "the last run" is a trap** (I-6). Store facts; derive states.
- **Guards need a false-alarm budget, not only a miss budget** (I-9). A strict guard that rejects good
  answers costs money and hides real failures among noise.
- **Error messages are part of the diagnosis path** (I-10, I-11).
- **The harness's defaults are part of the system under test** (I-8, I-14). Claude Code's harness prompt
  and its default thinking each changed cost or time several-fold, and neither shows in our code.
- **Give the model context, and it will quote the context** (I-15, I-16). Every piece of context in a
  prompt needs a rule: quotable or not, grounding or not.
- **A field needs a producer, not just readers** (I-26). Approved specs defined `scope_selector` and
  `verifies`, and rules consumed them, and unit tests passed on hand-built inputs — yet nothing in the
  pipeline wrote them. Review check for every contract field: *who writes it, and in which step?*
- **Contradictions hide between specs, and surface when two rules meet in one function** (I-33,
  I-34, I-35): each rule was reviewed alone and was fine.
- **Normalization is a decision per comparison** (I-40, and F1's own rule). The same text needs
  case-blind matching to *find* a counterpart and case-exact matching to *judge* it unchanged.
- **Temporary means temporary** (I-32, I-50). A measurement that exists only in a scratch folder is
  one restart from gone; write the summary somewhere durable the moment it exists.
- **Match the sample to the question** (I-49). A stratified, scattered sample tests *shapes* of
  prose well and *grouping* badly; a dense sample does the opposite.
- **A small sample flatters** (I-46): 7 of 8 plausible merges on 32 blocks became ≈ 6 of 16 on 63.
  Decisions taken on a pilot run should be re-checked at the gate before they harden.
- **Fixing one metric moves another** (I-28). Tightening terms cut noise and raised the family
  fallback. Every calibration must be judged on the whole metric set (G4), never one number.
- **Gate evidence chosen by the builder flatters** (I-54). Show every output, or a sample drawn before
  looking. The two cards picked for the gate were the two that passed.
- **A property test must test the output, not a helper beside it** (I-52). Parse what the user sees.
- **`None` as both "absent" and a real key is a trap** (I-51, I-53). The unplaced family's key is
  `None`, and two separate bugs came from it in one milestone.
- **Fixing the cheap stage shows you the expensive one** (I-76). Retrieval was tuned in an afternoon
  and delivered the pairs; the judge then failed on the same naming confusion. A pipeline hides its
  worst stage behind its weakest one.
- **A number with a unit can still be the wrong number** (I-82). "$6.32" was measured, reproducible
  and correctly summed — and it is not money. The evidence rule this repository already has ("no
  invented numbers") does not catch a real number under a wrong name; **state what a figure *is*, not
  only where it came from.**
- **A corpus of specifications is not prose** (I-81). The fixture was plain paragraphs and scored
  71 %; our own specs are dense with criteria and decision entries and scored 10 %. A tool measured
  only on prose will surprise you on documents.
- **Estimates made on a fixture underestimate the real corpus** (C). $2 predicted, $6.32 spent: our
  specs form more pairs per block, and a quarter of the first answers needed a re-ask.
- **Severity is a design decision, and the default was wrong** (I-79). "No structured output" was
  filed under *the backend is gone* when it meant *this answer is unusable*. The first class ends a
  run; the second costs one re-ask. Every raised error picks one of those, and on a long run the
  choice is the difference between finishing and not.
- **A prompt rule is not a fix, it is a request** (I-77). The instruction naming the exact false
  positive did not stop it. What can be checked in code should be.
- **A gate that fails is worth more than one that passes** (M4). It located the failure precisely —
  ranking, not judging — and that distinction decides which of five candidate fixes is worth building.
- **A weakness measured in one gate becomes a number in the next** (I-65 → I-73). "Families group
  badly" was a readability complaint at M3; at M4 it is five missed conflicts out of six.
- **The fixture found a defect its own author missed** (M4 §3). Prose written to be consistent, by
  someone who had just written the answer key, still held a real duplication. That is the product
  working — and why "I read it carefully" is not a substitute for a check.
- **Two rules that never meet in one test can still contradict each other** (I-70). "A row is one
  claim" and "a mixed-layer atom is re-asked to split" were each correct and tested; the second
  silently undid the first on the only blocks where both applied.
- **The mechanics can improve while the reading gets worse** (R16). Fixing what was dropped made the
  graph wider before it made it denser. A metric set (build-plan G4) must include a human reading, or
  the numbers will report progress the reader does not see.
- **Measuring a moving corpus** (I-69). This project's test corpus is its own specs, which change
  every session. A run is only comparable to another if the source is pinned and hashed; otherwise
  "the code improved" and "the spec grew" are indistinguishable.
- **One fix can unblock another's evidence** (I-63 → R16). Three source rows failing to atomize kept
  three criteria in the grab-bag, which made the family fix look weaker than it was. A metric can be
  held down by a defect that has nothing to do with it.
- **A guard that raises must sit where a failure is handled** (I-67). The same check is a re-ask in
  one place and a crash in another; what differs is not the check but where it runs.
- **"Finished work is kept" is only true for the failures you predicted** (I-68). The guarantee held
  for the cap and the backend, and not for the defect nobody had thought of.
- **A first-time reader finds what a metric cannot** (I-66, R15 §3). Dangling pronouns, boilerplate
  and a concept owned by two families were all invisible in the numbers and obvious in one reading.
- **A prompt rule learned once must be applied to every prompt** (I-63). "Never quote the context
  lines" was learned for Q-DESC in I-15 and missing from Q-ATOM three days later. Prompts are code:
  a fix belongs wherever the same input shape appears.
- **Unblocking content creates work downstream** (I-64, I-65). Seven rows became claims, and at once
  they needed a splitting rule, a display rule and more terms than the graph could group.
- **Check the records before building a fix read off a view** (I-60). The view showed where the
  criteria were; only the store showed that what they cite was never formed.
- **A silent zero is a failure** (I-59). A block that forms no node counts as "completed". Seven rules
  vanished and no count moved. Every "nothing" needs a reason on record.
- **A decision's reason has a scope** (I-61). D9 was right for constraints and wrong for criteria. When
  a rule is justified by one kind of node, check it for the others before applying it to all.
- **A shared rule belongs in one function** (I-57). The card and S3 now call the same `covers`, so the
  view shows what retrieval will do.
- **Test on every kind of block, not the first twenty** (I-21). The same guard that passed 20 header
  blocks failed 14 of 20 acceptance criteria. The M2 gate sample must be stratified by block shape.

## 9. What remains — updated 2026-09-30

> **2026-09-30 — M6 built; Phase D blocked on the sandbox.** `sddc export` exists (F7 🟢, AC-7.1 …
> AC-7.24, suite 754) and the pilot graph's export passes the gate (2.94× the Markdown; frozen as
> `~/sddc-runs/pilot-export-R000023`). The one-task pilot (F1, Sonnet, ≤ $10 estimated API-equivalent
> per run) is ready to run once the owner lets `bwrap` create namespaces
> (`docs/MIA5150-Project/harness/README.md`). **rel01 closes (D35)** when the owner agrees the export is
> usable — the pilot is the evidence. Still open: I-93 (conflict precision), I-94 (8 blocks that always
> fail; CF-000390, 397).

> **2026-09-29 — pilot graph frozen; rel01 slips (D35).** `~/sddc-runs/pilot-graph-R000023/`
> (read-only, manifest sha256 `21376ada2faf8539…`, commit `acdada8`) is the graph every study run reads
> until a new one is frozen deliberately. rel01 closes when the first graph is usable for generating
> code — M6 (F7, the agent export) **was built 2026-09-30** (T20–T23, AC-7.1 … AC-7.23; suite 748; first export of a copy of the pilot graph: I-95, I-96). Open: I-93 (precision), I-94 (8 blocks that always
> fail; CF-000390, 397), and the two real spec defects CF-000384 (CT-5.1's example) and CF-000387
> (CT-6.2 lacks `suppressed`).

**Built: all four milestones.** M1 (T1–T5), M2 (T6–T12), M3 (T13, T14), M4 (T15–T19) — **628 tests** (617, then 6 from the M4 follow-ups and 5 from R18's I-83, I-85, I-86).
`sddc init · ingest · compile · status · family · conflicts`, and `compile` = ingest → atomize →
**check** → report. Both gates are run: M3 closed (views pass, content short of the line); M4 measured
on the planted fixture and on 181 blocks of our own specs.

**What is left is a decision and a measurement, not a feature.** The deferred surface (B2, M5) is
`review`, `query`, `pairs --exhaustive`, `check`, `map`, `blocks`, `show` — every one a view on a store
that already exists. F3 AC-3.21 and AC-3.22 are satisfied by T17/T18 and need only their tests.

| Item | Kind | Size | Blocks |
|---|---|---|---|
| ~~I-43~~ backend failure keeps finished work | ✅ F3 D24 | — | — |
| ~~I-42~~ bold-title items fail every run | ✅ F3 D23 | — | — |
| ~~M2 gate~~ | ✅ measured and reviewed — [`M2-gate.md`](M2-gate.md) | — | owner decisions R1 … R11 |
| ~~R1 … R11~~ gate fixes (rel01 D32, D33) | ✅ built — F2 D16, D17; F3 D9 ext., D25 … D29; 14 new tests | — | — |
| ~~R6~~ re-measure | ✅ $1.64, two runs — [`M2-gate.md`](M2-gate.md) §B7 | — | — |
| R13, R14 | ✅ built — F3 D30, D31; 3 new tests | — | — |
| ~~R12~~ dense A/B (families) | ✅ $1.55 — R2 cuts one-use terms 67 % → 42 %; one-node families unchanged at ≈ 67 % — [`M2-gate.md`](M2-gate.md) §B8 | — | — |
| ~~T13~~ indexes; `status` with node counts | ✅ | — | — |
| ~~T14~~ `sddc family`; generated `views/` | ✅ + gate fixes I-51 … I-55 (F4 D13 … D16) | — | — |
| ~~M3 gate~~ — owner verdict | ✅ approved 2026-09-19 | — | — |
| ~~I-56~~ code · ~~I-57~~ · ~~F4 Q2~~ · ~~gate protocol~~ | ✅ built, 517 tests | — | — |
| ~~R15~~ re-compile F5 and re-read every card | ✅ done 2026-09-21, $1.20 — [`M3-gate.md`](M3-gate.md) | — | — |
| **The full-corpus test session** — compile this repository's own `sdd/specs/` end to end on the subscription. ✅ **Compiled** (16 rounds, 381 conflicts, store clean; §7). ⬜ **Left:** adjudicate the seeded sample of 100 (`sddc conflicts judge`), owner confirms, write M2 into [`M4-gate.md`](M4-gate.md) §8, fix what is real in the specs | measurement | ≈ ½ session | **the close-out number** (G4 §5) |
| ~~I-77~~ a criterion never duplicates what it verifies | ✅ F6 D16, in code | — | — |
| ~~I-76~~ term hygiene: S8 siblings, and the judge is shown the terms | ✅ F5 D12, F6 D17 | — | — |
| ~~B, A~~ cap 6 (F5 D13) and batched Q-PAIR (F6 D18) | ✅ 15 judge calls where 159 were needed | — | — |
| ~~C~~ the dogfood on F5 + F6 | ✅ [`M4-gate.md`](M4-gate.md) §7 — 70 conflicts, 4 real in a sample of 39, one of them a defect made that day | — | — |
| ~~I-81 (a, b)~~ criterion vs its own spec, and one block vs itself | ✅ F6 D19, 6 tests — 27 of 70 dogfood records suppressed, 0 real lost | — | — |
| **I-81 (rest)** criteria describing different situations read as contradictions (18 of 70) — show the judge the *Given/When*, or a required "same situation?" field | decision + code, re-judges pairs | medium | precision on real specs |
| **I-78** Q-TERM called "download link" different from "share link" | decision | small | the P6 class |
| ~~R18 pricing decision~~ — superseded by B and A: the full corpus is now ≈ $26 estimated, not $55–70. Options priced in [`M4-gate.md`](M4-gate.md) §6: batch Q-PAIR (≈ 8× fewer calls), tune thresholds (free, halves pairs), a sampled dogfood (≈ $6–8), the `anthropic-api` backend, or the full run (≈ $55–70, 7–11 h) | owner | — | the 30 September close |
| Owner: confirm the M3 pass line, and the verdict on [`M3-gate.md`](M3-gate.md) §3 | decision | small | closing M3 |
| I-66 the in-scope list reads as boilerplate | decision + small view change | small | nothing |
| ~~I-59, the report half~~ blocks that formed no node are counted (F3 D33) | ✅ built, 2 tests | — | — |
| ~~I-59 open half~~ a producer for `definition` sentences — ✅ built as F3 D38 (I-92 b), 2026-09-27 | — | — | — |
| ~~T15~~ retrieval S1–S7, scoring, `pair_key` (F5) | ✅ built — 22 tests | — | — |
| ~~T16~~ Q-PAIR judgment; links and conflict records (F6) | ✅ built — 18 tests | — | — |
| ~~T17~~ check phase, shared budget, conflict lifecycle | ✅ built — 19 tests | — | — |
| ~~T18~~ report, `sddc conflicts`, exit 3 | ✅ built — 12 tests, 2 goldens | — | — |
| ~~R16~~ re-measure after the I-63, I-64, I-67 fixes | ✅ $1.31 (+ $1.20 lost to the crash) — [`M3-gate.md`](M3-gate.md) §5 | — | — |
| ~~T19~~ adjudication record (G4) | ✅ built — 9 tests | — | — |
| M5 (optional) | exhaustive mode, `check`, `review`, `query`, `map`, `blocks`, `show`, `pairs`, `check-conflicts` | — | nothing in rel01 |

**On compiling:** see the brainstorm, rel01 S26 — one small stratified gate run now, one full compile at
the M4 gate; never a full compile before I-43 is fixed.

