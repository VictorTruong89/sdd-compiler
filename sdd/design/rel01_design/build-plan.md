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
| **G** | **Gate:** a person who has not read the graph can describe what a family contains from the view alone | — | — |

### M4 — Conflicts reported

| # | Task | ACs | Code |
|---|---|---|---|
| T15 | Retrieval sources S1–S7, scoring, cap, `pair_key`, which nodes are checked | F5 AC-5.1 … AC-5.14 | `retrieval/` |
| T16 | Q-PAIR judgment; links and conflict records; direction and confidence rules | F6 AC-6.1 … AC-6.8 | `conflicts/judge.py` |
| T17 | Check phase: never stops, shared budget, incomplete reporting; conflict lifecycle (re-judge, close, member deleted) | F6 AC-6.9, AC-6.12 … AC-6.19 | `conflicts/pipeline.py`, `conflicts/lifecycle.py` |
| T18 | The end-of-run report and `sddc conflicts`, grouped and sorted with contradictions first; exit codes 0/3/5 | F6 AC-6.10, AC-6.11 · F4 AC-4.16 | `report.py` |
| T19 | **Adjudication record** (G4 §4): `sddc conflicts judge …` → `.sdd/adjudications.jsonl` | *new AC in F6* | `conflicts/adjudicate.py` |
| **G** | **Gate:** compile the planted-conflict fixture; measure recall (G4 M1); compile this repository and judge every reported conflict (M2) | — | — |

### M5 — Only if time remains

Exhaustive mode and candidate completeness (F5 AC-5.15, AC-5.16) · `sddc check` · the attention list
and `review` (F3 AC-3.24, AC-3.25) · `query` · `map` · `blocks` / `show` / `pairs` /
`check-conflicts`.

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

## 7. Build progress — updated 2026-09-18

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
| **M2 gate** | ✅ measured · owner review pending | — | [`M2-gate.md`](M2-gate.md): 63-block stratified sample, two runs, $3.21; findings G-1 … G-14, recommendations R1 … R11 (Part C: every block reviewed) |
| M3, M4 | ⬜ | | |

Counts are tests per task's test files (T1's include 3 profile tests added in T6). Suite total: **463**. (T9's count is mostly the 128-case exhaustive placement test.)

## 8. Issues found while building — log for the retrospective

Each entry: what happened, how it was found, what was decided, and what it teaches. Numbered in the
order found. Owner decisions are cited by their spec decision id.

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

**Patterns so far** (for the retrospective):
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
- **A small sample flatters** (I-46): 7 of 8 plausible merges on 32 blocks became ≈ 6 of 16 on 63.
  Decisions taken on a pilot run should be re-checked at the gate before they harden.
- **Fixing one metric moves another** (I-28). Tightening terms cut noise and raised the family
  fallback. Every calibration must be judged on the whole metric set (G4), never one number.
- **Test on every kind of block, not the first twenty** (I-21). The same guard that passed 20 header
  blocks failed 14 of 20 acceptance criteria. The M2 gate sample must be stratified by block shape.

## 9. What remains — updated 2026-09-18

**Built:** M1 (T1–T5) and M2's tasks (T6–T12): `sddc init · ingest · compile · status`, 461 tests.
`compile` today = ingest → atomize → write the graph. It does not yet check for conflicts.

| Item | Kind | Size | Blocks |
|---|---|---|---|
| ~~I-43~~ backend failure keeps finished work | ✅ F3 D24 | — | — |
| ~~I-42~~ bold-title items fail every run | ✅ F3 D23 | — | — |
| ~~M2 gate~~ | ✅ measured and reviewed — [`M2-gate.md`](M2-gate.md) | — | owner decisions R1 … R11 |
| R1 … R11 (gate recommendations, if approved) | prompt, schema and rule changes | small each (R8 medium) | the M4 gate |
| T13 indexes; `status` with node counts | code (M3) | small | T14, T15 |
| T14 `sddc family`; generated `views/` | code (M3) | medium | M3 gate |
| T15 retrieval S1–S7, scoring, `pair_key` (F5) | code (M4) | medium | T16 |
| T16 Q-PAIR judgment; links and conflict records (F6) | code (M4) | medium | T17 |
| T17 check phase: never stops, shared budget, conflict lifecycle | code (M4) | medium | T18 |
| T18 end-of-run report; `sddc conflicts`; exit 3 | code (M4) | medium | **the release** |
| T19 adjudication record (G4) | code (M4) | small | G4 measurements M1–M2 |
| M5 (optional) | exhaustive mode, `check`, `review`, `query`, `map`, `blocks`, `show`, `pairs`, `check-conflicts` | — | nothing in rel01 |

**On compiling:** see the brainstorm, rel01 S26 — one small stratified gate run now, one full compile at
the M4 gate; never a full compile before I-43 is fixed.

