# F6 — Conflict detection: judge the pairs, record the conflicts, report them all

> **Spec-ID:** F6 · **Status:** 🟢 approved · **Drafted:** 2026-09-17 · **Approved:** 2026-09-18 (rel01 D28)
> ⛔ **Coding gated (rel01 D20).**
> **Source:** rel01 sub-goal G3.2 · approved proposals P-1 (Q-PAIR, judgment lock) and §5 of
> [`../../design/rel01_design/core-working-principle.md`](../../design/rel01_design/core-working-principle.md)
> · rel01 D9, D14 (conflict records and registry), D15, D17 (status), **D26 (batch: never stop, report
> everything at the end)** · the F6 conflict list of 2026-09-16 (items 6.3–6.5, 6.7).
> **Depends on:** F2 (records) · F3 (model interface, judgment lock, guards) · F4 (store, registry) ·
> F5 (candidate pairs). **⚑ Drafting choices** are marked in §7.

---

## 1. Goal & why

**Ask the model one question about one pair at a time, turn the answers into links and conflict
records, and end the run with a report of every conflict in the spec set.**

This is the purpose the whole compiler serves (vision §2): finding the contradictions, duplicates and
silent overlaps that a human reading a spec set cannot reliably find. Everything before it — blocks,
atoms, layers, families, candidates — exists so that this question can be asked narrowly enough to be
answerable and cheap enough to be asked often.

## 2. Scope / non-goals

**In scope:** the Q-PAIR question and its answer schema · which answers create links and which create
conflict records · statuses and the registry · when a conflict closes · re-judging after edits · the
end-of-run report · the run budget shared with atomization.

**Non-goals**
- ✗ Choosing which pairs to judge → F5.
- ✗ Fixing conflicts, suggesting fixes, or editing specs (vision §5).
- ✗ Notifying an agent mid-run, stopping at the first conflict, any fix loop — withdrawn by rel01 D26.
- ✗ Comparing a design graph with an as-built graph (P-11, deferred).

## 3. Users & triggers

| ID | Trigger | Entry point (code) |
|---|---|---|
| T1 | `sddc compile` reaches the check phase, after atomization | `sdd_compiler.conflicts.pipeline::check` |
| T2 | A person re-checks without re-atomizing | `sddc check-conflicts [--no-replay]` |
| T3 | A person reads the result | `sddc conflicts` (F4 §4.6), `.sdd/views/conflicts.md` |

## 4. Behaviour

### 4.1 Where the check phase sits (rel01 D26)

`sddc compile` runs: **ingest (F1) → atomize every pending block (F3) → check (F6) → report**. The check
phase starts only when atomization has finished, so every node that exists is visible to every pair.
The phase never stops early: a conflict is recorded and checking continues.

### 4.2 The question

One Q-PAIR call judges **one pair**. It receives both nodes' canonical form, verbatim text, layer,
family and source location, and it must answer with exactly one relation kind:

| Answer | Meaning | Effect |
|---|---|---|
| `none` | The two claims are independent | Nothing recorded except the judgment |
| `refines` | A is a more specific statement of B | `refines` link A → B |
| `depends_on` | A presupposes B | `depends_on` link A → B |
| `duplicates` | Both state the same claim | `duplicates` link **and** a conflict record, kind `duplication` |
| `subsumes` | A already implies B | `subsumes` link; a conflict record, kind `subsumption`, **only** when the two differ in modality or in a quantity (⚑ D2) |
| `contradicts` | Both cannot hold | Conflict record, kind `contradiction`, and a `conflicts_with` link |

Every answer carries a `rationale` and a quote from each node. A quote that is not found verbatim in
that node's text fails guard G2 and is re-asked once (F3 §4.3, §4.4).

### 4.3 What a conflict record holds

Conflict records are F2 CT-2.4: id, kind, sorted members, rationale, the quotes, `state`,
`detected_run`. Creating one sets `conflict_ids` on both members, which derives their status to
`conflict` (F2 §4.6), which puts them in the registry (F4 CT-4.2).

Two members are enough. A node in several conflicts carries several `conflict_ids` (rel01 D14), and
`sddc conflicts` groups records that share a member so interlinked conflicts are read together.

### 4.4 Ambiguous nodes are judged, provisionally (⚑ D3)

A node with status `ambiguous` still takes part: a vague spec can still contradict a precise one.
Verdicts involving an ambiguous node are recorded with `provisional: true`. When the ambiguity is
resolved, every provisional verdict touching that node is marked stale and re-judged.

### 4.5 Replay and re-judging

- A pair's judgment is stored in the lock under its `pair_key` (F5 §4.4) plus the Q-PAIR schema version.
  A lock hit is replayed; no model call is made (F3 §4.7).
- When a node's text changes, its `pair_key`s change, so every pair touching it is judged again, and
  the stale verdicts from the old text are discarded.
- `--no-replay` forces re-asking.

### 4.6 When a conflict closes (⚑ D4)

A record moves to `resolved` only when:
1. the pair is judged again and the answer is `none` or a non-conflicting relation; or
2. a member is deleted (F2 §4.9), with reason `member_deleted`.

**An edit alone never closes a conflict.** Changing the text makes the verdict stale and schedules a
re-judgement; the record closes when that re-judgement says so. A `resolved` record stays in
`conflicts.jsonl` as history, with its `resolved_run`.

### 4.7 Budget (⚑ D5)

Pair judging and atomization share `atomizer.max_calls_per_run` (F3 CT-3.4). The check phase reports
how many calls it used. If the budget runs out mid-phase:
- what has been judged is written;
- the remaining nodes keep status `unchecked` or `stale`;
- the run exits `5` and the report says checking is incomplete, naming how many pairs were left.

Checking order is F5's order, so a resumed run continues predictably.

### 4.8 The report

At the end of a run, `compile` prints, and writes through F4:

```text
compiled 4 files · 37 blocks · 52 nodes · 18 terms
checked 44 pairs (31 judged, 13 replayed) · 6 model calls · 12,480 tokens
CONFLICTS: 3 open (2 contradiction, 1 duplication) in 2 groups
  CF-000001 contradiction  N-000017 sharing.md:5  ↔  N-000042 sharing.md:22
    "expires 30 days after it is created" ↔ "valid for one hour"
    rationale: both set the lifetime of a share link, to different values
  …
ATTENTION: 2 items (1 inferred_node, 1 term_unsure) — run `sddc review list`
exit 3
```

- Exit `3` when open conflicts exist, `0` when none, `5` when the budget stopped the phase.
- `--json` emits the same content as one object, for scripts and for G4 measurement.

### 4.9 Counts a run records

Pairs judged, replayed, by answer kind, conflicts opened, conflicts closed and their reasons, calls and
usage. These extend the run record (CT-6.2) and are the raw material for measuring the compiler later.

## 5. Contracts

**CT-6.1 — Q-PAIR answer schema `q-pair/2`** (`/2` asks about a batch, D18)
```json
{ "pairs": [ {
  "pair_id": "N-000017|N-000042",
  "relation": "none | refines | depends_on | duplicates | subsumes | contradicts",
  "direction": "a_to_b | b_to_a | symmetric",
  "rationale": "one sentence",
  "quotes": {"a": "verbatim from A", "b": "verbatim from B"},
  "confidence": "high | low" } ] }
```
Rules: `direction` must be `symmetric` for `none`, `duplicates` and `contradicts`. `confidence: low`
adds ambiguity `low_confidence_verdict` to both nodes rather than suppressing the verdict.

**CT-6.2 — Run record additions**
```json
{ "conflicts": {"candidates": 0, "pairs_judged": 0, "pairs_replayed": 0, "unjudged_failed": 0,
                "provisional": 0, "retrieval": {},
                "by_relation": {"none": 0, "refines": 0, "depends_on": 0, "duplicates": 0,
                                "subsumes": 0, "contradicts": 0},
                "opened": 0, "closed": {"rejudged": 0, "member_deleted": 0},
                "calls": 0, "incomplete": false} }
```

**CT-6.3 — Profile additions**
```yaml
conflicts:
  judge_ambiguous: true          # §4.4
  subsumption_conflict_only_when_differing: true   # ⚑ D2
```

## 6. Acceptance criteria

> Tests use F3's recorded fake backend; no test calls a live model. Tiers are provisional.

**Judging and recording**
- **AC-6.1** *(contradiction opens a record)* — **Given** a candidate pair and a fake `contradicts`
  answer, **then** one conflict record exists with kind `contradiction`, both ids sorted in `members`,
  the rationale and both quotes; both nodes carry its `conflict_ids` and derive to status `conflict`;
  the registry lists both. → *integration.*
- **AC-6.2** *(none records nothing but the judgment)* — **Given** a fake `none` answer, **then** no
  link and no conflict record exist, and the judgment is in the lock. → *unit.*
- **AC-6.3** *(refines and depends_on make links only)* — **Given** fake `refines` and `depends_on`
  answers, **then** links of those types exist with `provenance: judgment`, a judgment id and a
  rationale, and no conflict record. → *unit.*
- **AC-6.4** *(duplication)* — **Given** a fake `duplicates` answer, **then** both a `duplicates` link
  and a conflict record of kind `duplication` exist. → *unit.*
- **AC-6.5** *(subsumption only conflicts when they differ)* — **Given** `subsumes` where both nodes
  have modality `MUST` and no differing quantity, **then** a link exists and no record; **given**
  `subsumes` where one is `MUST` and the other `SHOULD`, **then** a record of kind `subsumption` also
  exists. → *unit.*
- **AC-6.6** *(quote guard)* — **Given** an answer whose quote is not verbatim in the node, **then** the
  question is re-asked once; on a second failure no verdict is recorded and both nodes stay unchecked
  for that pair. → *unit.*
- **AC-6.7** *(direction rule)* — **Given** `contradicts` with `direction: a_to_b`, **then** the answer
  is rejected by the schema check. → *contract.*
- **AC-6.8** *(low confidence)* — **Given** a `contradicts` answer with `confidence: low`, **then** the
  record is created **and** both nodes gain ambiguity `low_confidence_verdict`. → *unit.*

- **AC-6.21** *(a criterion does not duplicate its requirement; D16)* — **Given** a `V` node whose
  `verifies` lists node B, **when** the judge answers `duplicates` or `subsumes`, **then** no conflict
  record and no link are made and the run counts one `suppressed`; **when** it answers `contradicts`,
  **then** the record is opened as usual. → *unit.*
- **AC-6.22** *(a criterion does not duplicate its own spec; D19)* — **Given** a `V` node and a
  non-`V` node from the **same file**, `verifies` empty, **when** the judge answers `duplicates` or
  `subsumes`, **then** no record and no link are made and the run counts one `suppressed`; **when** it
  answers `contradicts`, or the other node is in another file, or both are `V` nodes, **then** the
  record is opened as usual. → *unit.*
- **AC-6.23** *(one block does not duplicate itself; D19)* — **Given** two nodes with the same
  `source.block_id`, **when** the judge answers `duplicates` or `subsumes`, **then** no record and no
  link are made and the run counts one `suppressed`; **when** it answers `contradicts`, **then** the
  record is opened as usual. → *unit.*
- **AC-6.20** *(a human verdict is recorded; G4 §4, D14)* — **Given** an open conflict, **when**
  `sddc conflicts judge CF-000001 --verdict real --note "…"` runs, **then** `.sdd/adjudications.jsonl`
  gains a record naming the conflict, the verdict, the note, the members and the `judgment` it
  answered; **when** the pair is judged again, **then** that verdict reads `stale`; **given** an
  unknown conflict id, **then** exit `2`. → *unit.*

**Batch behaviour**
- **AC-6.9** *(never stops)* — **Given** five candidate pairs where the second and fourth contradict,
  **then** all five are judged, two records exist, and the run continues to the end (rel01 D26). →
  *integration.*
- **AC-6.10** *(report lists everything)* — **Given** that run, **then** the report names both
  conflicts with their members, files and lines, groups records sharing a member, states the counts,
  and exits `3`. → *golden.*
- **AC-6.11** *(clean run)* — **Given** a graph with no conflicts, **then** the report says so and the
  run exits `0`. → *integration.*
- **AC-6.12** *(budget exhausted)* — **Given** a call cap smaller than the pairs to judge, **then**
  judged verdicts are written, unjudged nodes keep `unchecked` or `stale`, the report says checking is
  incomplete with the number of remaining pairs, and the run exits `5`. → *integration.*

**Replay, staleness and closing**
- **AC-6.13** *(replay)* — **Given** a completed check and no source change, **when** the run repeats
  with a fake backend that fails on any call, **then** it succeeds with zero calls and identical
  records. → *property.*
- **AC-6.14** *(edit re-opens the pair)* — **Given** a judged pair, **when** one node's text changes,
  **then** its `pair_key` changes, the pair is judged again, and the previous verdict is not reused. →
  *integration.*
- **AC-6.15** *(an edit alone does not close a conflict)* — **Given** an open contradiction, **when** one
  member's text is edited but the re-judgement still answers `contradicts`, **then** the record stays
  open with the new quotes. → *integration.*
- **AC-6.16** *(re-judgement closes)* — **Given** an open contradiction, **when** a re-judgement answers
  `none`, **then** the record is `resolved`, `conflict_ids` are cleared on both nodes, their status is
  re-derived, and the registry no longer lists them. → *integration.*
- **AC-6.17** *(member deleted closes)* — **Given** an open contradiction, **when** one member is
  deleted, **then** the record is `resolved` with reason `member_deleted` (F2 AC-2.23). → *integration.*
- **AC-6.18** *(ambiguous nodes are judged provisionally)* — **Given** an `ambiguous` node in a pair,
  **then** the verdict is recorded with `provisional: true`; **when** the ambiguity is resolved, **then**
  that verdict is stale and re-judged. → *integration.*
- **AC-6.19** *(counts)* — **Given** any check phase, **then** CT-6.2 counts are recorded and
  `pairs_judged + pairs_replayed` equals the number of candidate pairs. → *contract.*

## 7. Decisions

- **D1 — One closed list of relation kinds, one per pair** (conflict-list item 6.3). *Rejected:* letting
  the model return several relations — the compiler could not act on a mixture, and it invites
  hedging.
- **D2 — ⚑ `subsumes` opens a conflict only when the two differ in modality or quantity.** Plain
  subsumption is useful structure, not a defect; a `MUST` subsumed by a `SHOULD` is a defect. Made
  configurable because this is a judgement call to revisit with real data.
- **D3 — ⚑ Ambiguous nodes are judged, with `provisional` verdicts** (item 6.5). *Rejected:* skipping
  them — vague specs are exactly where contradictions hide; accepting their verdicts as final — the
  claim may change when the ambiguity is cleared.
- **D4 — A conflict closes only on re-judgement or member deletion** (item 6.4). *Rejected:* closing on
  text change — it would report "fixed" for an edit that changed nothing relevant.
- **D5 — ⚑ One run budget shared with atomization**, and exit `5` with an explicit "incomplete" report
  rather than silently checking less (conflict-list item X.1).
- **D6 — ⚑ `confidence: low` records the verdict and flags the nodes**, rather than dropping it.
  *Rejected:* discarding low-confidence verdicts — a silent miss is worse than a flagged guess.
- **D7 — Deterministic checking order** (item 6.7). Which conflict is found first is then reproducible.
  Whether a *fixing* order changes the final graph is a property to measure in G4, not a claim here.

## 8. Open questions

*None. Q1–Q3 were resolved 2026-09-18 as D8–D10 (rel01 D28).*

- **D8 — The pair question carries the two nodes plus their layer and family labels, and nothing else**
  (resolves Q1). *Rejected for rel01:* including refinement ancestors or the constraints covering each
  node — it grows every prompt for a benefit nobody has measured. If verdicts look uninformed on a real
  corpus, this is the first thing to change, and the judgment lock makes the before/after comparable.
- **D9 — One conflict list, sorted with contradictions first**, then duplications, then subsumptions
  (resolves Q2). *Rejected:* a separate hygiene list — it splits the reader's attention and invites
  ignoring one of the two lists. Sorting solves the "40 duplicates bury 3 contradictions" problem
  without hiding anything. The counts per kind are in the report header, so a large duplication count is
  visible at a glance.
- **D16 — ⚑ A criterion never duplicates or subsumes what it verifies — checked in code** (R17,
  I-77). D15 says it in the prompt and the judge opened CF-000002 for exactly that case, so the graph
  settles it: when one node's `verifies` holds the other's id (resolved from the criterion's own
  citation, F2 D13), a `duplicates` or `subsumes` verdict records nothing and is counted as
  `suppressed` (CT-6.2). A **contradiction** between a test and its rule is still reported: a test that
  denies its requirement is a real defect. *Why in code:* a prompt rule is a request, and this one was
  refused; `verifies` is a fact the graph already holds.
- **D18 — ⚑ Q-PAIR is batched: 8 pairs per call** (R21; rel01 D30's lever, applied to the phase that
  now dominates a compile). §4.2 said "one Q-PAIR call judges one pair", and the M4 gate showed what
  that costs: 159 calls for 159 pairs, $2.35 on 28 blocks, and ≈ $55–70 extrapolated to this
  repository (I-75). A headless call carries ≈ 22k tokens of harness prompt whatever it asks, so the
  call count *is* the cost. **The condition F3 §4.3 rule 4 puts on batching holds here too:** each
  pair's answer is validated on its own, and a failure re-asks **that pair alone**. With D13's cap,
  the same corpus needs **15 calls instead of 159**. *Rejected:* a larger batch — Q-DESC settled on 8
  (rel01 S21) because a longer call risks the timeout, and a timeout costs the whole batch.
- **D19 — ⚑ The document's form settles two more non-conflicts, in code** (I-81, after the dogfood).
  D16 fires only when a criterion cites its rule, and on this repository's own specs most criteria
  cite nothing: precision there was ≈ 10 %, and 65 of 70 conflicts involved a criterion or a decision
  entry. Two facts the graph already holds now settle a `duplicates` or `subsumes` verdict the same
  way D16 does — nothing recorded, counted as `suppressed` (CT-6.2):
  (a) **a criterion and a claim of its own spec file** — exactly one of the two is a `V` node and both
  come from one file; a criterion restates its spec's rules by design;
  (b) **two claims of one block** — the same `source.block_id`, as a decision entry's heading and
  its body are.
  **A contradiction is never suppressed by either**: all four real finds of the dogfood were
  contradictions, one between a criterion and its own spec (CF-000038), one between two sentences of
  one paragraph (CF-000001). Measured on the dogfood store before building: (a) removes 22 of the 70
  records and (b) 5, none of them among the four real. *Given up:* a criterion that genuinely
  duplicates prose of its own file is no longer reported; duplication **across** files, and between
  two criteria, still is. *Rejected:* suppressing contradictions between criteria describing different
  situations by label — CF-000038 is in that class; that one needs the judge to see the situation,
  not a rule on the layout.
- **D17 — ⚑ The judge is shown the terms, and how they relate** (after R17: I-76). Retrieval delivered
  the 5 GB / 5 GiB pair and the judge answered `none` — *"the two claims govern different export types
  (export archive vs workspace export)"* — while the graph held both as kinds of `export`. Each claim
  now lists its terms, the question states how the two sets relate (same term, a kind of, or two kinds
  of one thing), and the instructions say a different name is not a different object. *Rejected:*
  renaming nodes' text to a canonical term — the verbatim span is the evidence a person checks.
- **D15 — ⚑ Q-PAIR is told when two numbers are *not* a contradiction** (R16, after the M4 gate:
  I-74). Eight of eleven reported conflicts were false, and five were one mistake: a 24-hour link
  inside a 30-day archive, a 13-day restore inside a 14-day window, read as contradictions — and once
  the judge computed "day 30 versus day 31", arithmetic the text does not do. The prompt now states
  that two claims contradict only if both must hold for the same thing at the same time, gives the
  three consistent shapes (a limit inside a longer one, a window and what follows it, a rule and its
  clarification), forbids calculating, and says that an acceptance criterion restating its requirement
  is design, not duplication. *Rejected:* a code-side numeric check — the relation between two
  quantities is exactly the judgement the model is asked for.
- **D14 — ⚑ An adjudication answers one model verdict, not a conflict id** (T19, G4 §4). The record
  keeps the `judgment` it answered and the members at the time, so a pair judged again marks the human
  verdict **stale** instead of carrying it forward — the person answered about the old text. Records
  are appended, never rewritten, so a change of mind stays visible and M2 can be recounted at any time.
  *Rejected:* a `human_verdict` field on the conflict record — it would be overwritten by the next
  re-judgement, which is exactly the history M2 needs.
- **D13 — ⚑ A node the check phase looked at loses the stale reasons that scheduled it** (T17), and
  records the run in `last_checked_run`. *Why:* `stale` means "needs re-checking" (F2 §4.6); keeping the
  reason after the re-check would leave the node stale for ever and re-judge it every run. The reason
  is still written by whatever caused it — a deleted neighbour, an edited counterpart — so a node is
  never silently dropped from the queue; it is discharged only by the phase that honours it.
  *Rejected:* clearing it when the graph is written, which would discharge reasons nobody acted on.
- **D12 — ⚑ CT-6.2 also counts what was *not* judged** (T17): `candidates` (how many pairs retrieval
  proposed), `unjudged_failed` (answers that failed their checks twice), `provisional` (§4.4), and F5's
  own `retrieval` counts. *Why:* AC-6.19's identity reads "judged + replayed = candidate pairs", and a
  pair that failed twice would otherwise break it silently — the I-59 lesson, that a zero with no
  reason is a failure the report must show.
- **D11 — ⚑ The direction rule is in the schema, not in a later check** (T16). CT-6.1 says `none`,
  `duplicates` and `contradicts` are symmetric; the JSON Schema now says so too (`if`/`then`), so
  AC-6.7's answer is rejected before anything reads it, and the re-ask carries the reason. *Rejected:*
  silently normalising the direction to `symmetric` — that would hide a judge that did not understand
  the question.
- **D10 — `confidence` is recorded and flagged, never acted on** (resolves Q3). rel01 stores it and
  raises ambiguity `low_confidence_verdict`; nothing filters or re-ranks by it until G4 has compared it
  with human labels.

## 9. Traceability

| AC | Test (file::test) | Code |
|---|---|---|
| AC-6.2 … AC-6.8 · CT-6.1, CT-6.3 · D15 (T16, R16) | `tests/test_conflicts_judge.py` (19) | `src/sdd_compiler/conflicts/judge.py` · `records.py` · `src/sdd_compiler/profile.py` |
| AC-6.1 *(partial: the record and links a contradiction produces; writing them through a transaction and deriving status is T17)* | `tests/test_conflicts_judge.py::test_ac_6_1_…` | `src/sdd_compiler/conflicts/records.py` |
| AC-6.9, AC-6.12 · CT-6.1, CT-6.2 · D5, D12, D18 (T17, R21) | `tests/test_conflicts_pipeline.py` (18) · `tests/test_compile.py::test_ac_6_12_…` | `src/sdd_compiler/conflicts/pipeline.py` · `src/sdd_compiler/pipeline.py` |
| AC-6.1, AC-6.11, AC-6.13, AC-6.16, AC-6.17 *(through `compile`)* | `tests/test_compile.py` (6) | `src/sdd_compiler/pipeline.py::compile_graph` · `_apply_check` |
| AC-6.14, AC-6.15, AC-6.18 · D4, D13 | `tests/test_conflicts_pipeline.py::test_ac_6_14_…`, `::test_ac_6_15_…`, `::test_ac_6_18_…` | `src/sdd_compiler/conflicts/pipeline.py` |
| AC-6.19 *(counts add up)* | `tests/test_conflicts_pipeline.py::test_ac_6_19_…` | `src/sdd_compiler/conflicts/pipeline.py` |
| AC-6.21 · D16, D17 (R19) | `tests/test_conflicts_judge.py::test_i77_…`, `::test_r19_…` · `tests/test_conflicts_pipeline.py::test_r19_…` | `src/sdd_compiler/conflicts/records.py` · `judge.py` · `pipeline.py` |
| AC-6.22, AC-6.23 · D19 (I-81) | `tests/test_conflicts_judge.py::test_ac_6_22_…` (3), `::test_ac_6_23_…` (3) | `src/sdd_compiler/conflicts/records.py::outcome_for` · `_criterion_in_its_own_spec` |
| AC-6.20 · D14 (T19) | `tests/test_adjudicate.py` (9) | `src/sdd_compiler/conflicts/adjudicate.py` · `commands.py` · `cli.py` |
| AC-6.10, AC-6.11 · D9 (T18) | `tests/test_report.py` (12), goldens `tests/golden/report_*.md` | `src/sdd_compiler/report.py` · `src/sdd_compiler/commands.py` |
