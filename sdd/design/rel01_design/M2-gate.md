# M2 gate — lecture and results

> **Status:** measured 2026-09-18 · **Tier:** design, non-authoritative · **Owner review:** pending
> **Gate (build plan §3):** compile this repository's specs; inspect the nodes by hand; record cost (G4
> M7) and the `inferred` rate (M8). Per the owner's instruction (rel01 S26) the gate compiled a
> **stratified sample**, twice, not the whole repository. Hand review of every sampled block: Part C.
>
> **How to read this file.** Part A is a lecture: why the two runs were done, what happened, and what
> the numbers mean in plain words, with real examples. Part B is the technical record the lecture
> explains. Part C reviews every one of the 63 sampled blocks, with a verdict and a reason per run. Written as Markdown in this file at the owner's request (lectures normally live as HTML in
> `docs/lectures/`).

---

# Part A — Lecture

## A1. Where this sits in the build

rel01 is built in four milestones, each one usable on its own (build plan §2):

| Milestone | In one line | State on 2026-09-18 |
|---|---|---|
| M1 | Read spec files and cut them into **blocks** (paragraphs, list items, table rows) | built |
| **M2** | Turn blocks into a **graph**: the model splits each block into single claims (**nodes**), and code files each node into a **layer** and a **family** | **built — this gate checks it** |
| M3 | Let people read the graph (family views, a map) | next |
| M4 | Find **conflicts** between nodes and report them — the point of rel01 | after M3 |

Every milestone ends with a **gate**: a check, on real material, that the milestone is good enough to
build the next one on. The M2 gate asks a simple question:

> *If we point the compiler at our own specs, is the graph it builds good enough for M3 and M4 to work
> with — and what does it cost?*

### Why the tests were not enough

The code has 463 automated tests, and they all pass. But those tests use a **fake model**: we write
the model's answers ourselves, so the tests prove that *the code does what the specs say with the
answers it is given*. They cannot tell us whether the **real** model (Haiku) gives useful answers on
**real** prose. Only a live run can. Every live run so far has found something the tests could not
(the build log, build-plan §8, lists 48 such issues).

## A2. What the two runs were

### The sample, not the whole repository

Compiling all ~750 blocks of our specs would take about three hours and about $18 of model usage on
the owner's subscription, which was at 86 % of its session limit. So the gate took a **sample**.

A random sample would mostly pick the commonest kinds of block and miss rare ones — and earlier runs
showed that different *shapes* of prose break in different ways (the `**Given**` bug only appeared on
acceptance criteria, I-21). So the sample was **stratified**: the blocks were sorted into seven shapes
and 9 were drawn from each:

| Shape | What it looks like in our specs |
|---|---|
| header | the `> **Spec-ID:** … **Status:** …` blockquote at the top of each spec |
| paragraph | ordinary prose |
| list_item | a plain bullet |
| bold_title | a bullet that starts with a bold title: `- **Make a spec set checkable.** Find …` |
| criterion | an acceptance criterion: `- **AC-1.4** — **Given** … **when** … **then** …` |
| decision | a decision entry: `- **D9 — …**` |
| table_row | one row of a table (often a traceability row: AC → test → code) |

63 blocks in all. The draw uses a fixed seed, so anyone can reproduce exactly the same sample.

### Why two runs

The model is not deterministic: asked the same question twice, it may answer differently. One run
would tell us what happened *once*; it could not tell a real weakness from bad luck. So the same 63
blocks were compiled **twice, independently** — two fresh stores, no shared memory of answers — to see
how much of the result is stable and how much is chance. That comparison is called the **spread**.

## A3. What actually happened, in order

1. **Run 1 started** and, after 7½ minutes and 18 finished blocks, hit the **usage limit** of the
   owner's Claude Code session (an error 429: "you've hit your session limit").
   The fix written an hour earlier (I-43) did its job: the 18 finished blocks were **kept**, and the
   compiler stopped cleanly with exit code 6. Before that fix, all 18 would have been thrown away.
2. **Run 2 started straight after** and failed at once — same limit.
3. After the limit reset (6:40 pm), **run 1 was resumed**. Only its unfinished blocks were asked; the
   answers already paid for were **replayed** from the judgment lock (54 of them), costing nothing.
   Run 1 finished: 60 of 63 blocks done.
4. **Run 2 was restarted** — and **crashed** on a real bug (I-45): the model had said "term B is the
   same as term A" after A had itself just been merged into a third term, and the code looked for A.
   The bug was fixed, a test added, and run 2 was **started again from scratch**: 51 of 63 done.

Total cost of both runs: **$3.21**, about 33 minutes of model time.

## A4. How the compiler turns one block into nodes — a real example

Take this acceptance criterion from F1 (block `B-000085`):

> - **AC-1.21** *(pending output contract)* — **Given** a store with pending blocks, **when**
>   `sddc status --json` runs, **then** stdout is exactly one JSON object valid against CT-1.5. →
>   *contract.*

1. **Q-ATOM** — the model splits the block into **atoms**, single claims that are true or false on
   their own.
2. **Q-DESC** — for each atom, the model fills in a **canonical form** (subject · modality · response:
   *stdout · MUST · be exactly one JSON object…*), answers **seven yes/no layer questions**, and tags the
   **terms** it uses (*stdout*, *store*…).
3. **Code** does the rest: picks the **layer** from the first "yes", picks the **family** from the
   subject term, checks that every quote really is in the source, and writes the **node**.

What the two runs made of it:

| | Nodes | Layer · family · claim |
|---|---|---|
| **Run 1** | 2 | `L0` · *no family* · "pending output contract" (the title, as a claim) · `L1` · `stdout` · "stdout MUST be exactly one JSON object…" |
| **Run 2** | 3 | `L2` · *no family* · "the test context exists with pending blocks" · `L1` · *no family* · "the command runs" · `L1` · `stdout` · "stdout MUST be exactly one JSON object…" |

Both runs found the real requirement (the last row) and placed it identically. They disagreed on
everything around it: run 1 turned the *title* into a claim, run 2 turned the *Given* and *When* parts
into claims. That is what "fresh runs disagree" means in practice.

## A5. The results table, row by row, in plain words

(The table itself is in Part B, §B2.)

| Row | Plain meaning | Run 1 · Run 2 | Good or bad? |
|---|---|---|---|
| **Blocks completed** | How many of the 63 blocks the compiler fully processed. A block fails when the model's answer breaks a check twice — usually by "quoting" words that are not in the source | 60 · 51 | Run 1 good. Run 2's 12 failures were mostly the check **working**: the model paraphrased or trimmed quotes, and the compiler refused to invent. The difference between 3 and 12 failures on the *same* blocks is chance |
| **Nodes** | Single claims found | 84 · 74 | About 1.3 claims per block. Neither right nor wrong by itself |
| **Model calls · cost** | Questions sent to Haiku, and what they cost | 77 · $1.69 and 79 · $1.52 | About **2.4 cents per block**. For the whole repository: ≈ $18 and ≈ 3 hours from scratch. After that, the lock means a re-compile pays only for what changed |
| **`inferred` nodes** | Nodes whose description contains something **not in the source** (the model added a fact). The compiler flags each one for a person | 2.4 % · 2.7 % | **Good.** Rare, and each flag was a real addition |
| **Layers** | Which of the eight fixed layers each claim was filed under (see glossary). "none" = no layer question got a yes | L1 dominates in both; C ≈ 20 % | **Too many C.** C means "a rule over many things", but headers like "never renumbered" landed there because the question lists the words "every / all / never" and the model matches words, not meaning |
| **Family null** | Claims the compiler could not attach to any family | 24 % · 23 % | **Bad.** A quarter of the graph is homeless |
| **Families with one node** | Of ~42 families, how many hold a single claim | 28 · 36 | **Bad.** A family is meant to gather everything about one thing (all claims about *share links*). One-member families gather nothing |
| **Terms used once** | Terms (the "things" claims talk about) that only one claim uses | 79 % · 72 % | **Bad, and the cause of the two rows above.** Families are named after terms. When each claim names its thing slightly differently ("pending status", "changed status", "block"), every claim gets its own family |
| **Status ambiguous** | Claims flagged as "a person should look": vague word, unresolved "it", no modal verb, no family… | 62 % · 73 % | **Bad.** If two thirds of the graph is flagged, the flags stop meaning anything, and the M4 report will drown real conflicts |
| **Attention items** | The to-do list for a person: failed blocks, term merges to confirm, inferred content | `term_same` 16 · 11 | The `term_same` items revealed the finding below |
| **Store checks** | The eight consistency checks on the saved graph (ids unique, links resolve, …) | all clean · all clean | **Good.** The storage layer is sound |
| **Spread** | How often the two runs agree on the same block | node count 49 %; layer and family 10 of 16 | **Important.** Asking again gives a different graph about half the time. Stability comes only from **replaying** recorded answers (the lock), never from re-asking |

### The term-merging finding, by example

When the model tags a new term that looks like an existing one, the compiler asks (Q-TERM): *same
thing or different?* On "same", it now merges them at once (F3 D20). In run 1 it answered "same" 16
times — and about 10 were **"a kind of"**, not "the same":

- "review item", "attention item" → merged into `item`
- "term id", "judgment id" → merged into `id`
- "batch run" → `run`; "violation report" → `report`

So unrelated claims about *judgment ids* and *term ids* end up in one family, `id`. That is the
opposite of what families are for. The pilot run in T10 (7 of 8 merges looked right) was too small to
show this — a lesson recorded in the build log.

### A header, twice

The F2 header line "⛔ Coding gated: no implementation until G3 and G4 are reviewed and the build plan
exists" became, word for word, the same claim in both runs — but run 1 filed it under **C** (a rule
over many things) and run 2 under **no layer at all**. Same text, same model, different answer.

### Traceability rows

Rows such as `| AC-1.24 | tests/test_profile.py::… | src/…/profile.py |` became "verification" nodes
with no family in both runs. They are bookkeeping about the specs, not claims *in* them. Whether such
rows should become nodes at all is a question for the owner (G-8; Part C reviews every row).

## A6. What the gate concluded

- **The machinery works.** Storage, checks, recovery from a usage limit, resuming from the lock,
  refusing invented quotes — all held on real data.
- **The meaning layer is not good enough yet.** Families do not gather (terms are too scattered, and
  Q-TERM merges the wrong things), C is over-used, and most nodes are flagged ambiguous.
- **Re-asking is not reproducible.** The lock is not an optimisation; it is the only thing that makes
  one compile equal the next.
- **Cost is known:** ≈ 2.4 cents per block; ≈ $18 for the whole repository from scratch.

What to change is proposed in Part B §B5 (R1–R6) and waits for the owner. M3 can be built meanwhile;
the fixes should land before the M4 gate compiles the whole repository.

## A7. Glossary

| Word | Meaning |
|---|---|
| block | A structural piece of a Markdown file found by code: paragraph, list item, table row |
| atom · node | One claim that is true or false on its own. An atom is the model's split; a node is the atom once described, placed and saved |
| layer | Which of eight fixed kinds of statement a node is: **L0** intent (why), **L1** behaviour an outsider can see, **L2** structure (which component), **L3** contract between two parties (API, file format), **L4** data, **L5** internal logic, **C** a rule over many nodes, **V** a test or check |
| family | The group a node belongs to, named after the main *thing* it is about (a term). One node, one family |
| term | A named thing claims talk about ("share link", "block"). Families are terms |
| canonical form | The claim rewritten as *subject · MUST/SHOULD/MAY · response* |
| ambiguous | A node flagged for a person: an unresolved "it", a vague word, no modal verb, no family, mixed layers, an unconfirmed term |
| inferred | A node whose description contains something not in the source |
| `mixed_layers` | A node whose layer questions pointed at two layers, which the model twice declined to split (F3 D23) |
| attention item | An entry on the person's to-do list (`review.jsonl`) |
| judgment lock | The record of every accepted model answer; a later compile **replays** it instead of asking again |
| gate | A checkpoint at the end of a milestone, on real material |
| spread | How much two independent runs of the same input differ |
| G2 / G3 guards | Checks on the model's answers: G2 "every quote is really in the source"; G3 "every sentence with *must*, *never*… is covered" |

---

# Part B — Technical record

## B1. What was run

- **Sample:** 63 blocks of `sdd/specs/**` — 9 per shape, fixed seed 20260918: `header` (blockquote
  front matter), `paragraph`, `list_item`, `bold_title` (list item with a bold lead-in), `criterion`
  (`AC-`/`CT-`), `decision` (`D<n>`), `table_row`. Population: 19 · 151 · 166 · 46 · 122 · 75 · 168
  (code blocks, 25, are not atomized).
- **Two independent runs**, each a fresh store with no shared lock, so the spread is real. Code as of
  463 tests, with F3 D23 (refused split → `mixed_layers`) and D24 (backend failure keeps work).
- **Backend:** headless Claude Code, Haiku, thinking off (F3 D10).

## B2. Results

| | Run 1 | Run 2 |
|---|---|---|
| Blocks completed | **60 of 63** (95 %) | **51 of 63** (81 %) |
| Failures by guard | G2 ×2, G3 ×1 | G2 ×10, G3 ×2 |
| Nodes | 84 | 74 |
| Model calls · cost *(M7)* | 77 · $1.69 (in two parts, see §A3) | 79 · $1.52 |
| Time | 448 s + 561 s | 956 s |
| `inferred` nodes *(M8)* | 2 of 84 (2.4 %) | 2 of 74 (2.7 %) |
| Layers | L1 37 · C 17 · V 12 · L4 11 · L2 2 · L0 1 · none 4 | L1 27 · C 17 · L4 14 · V 6 · none 5 · L2 2 · L5 2 · L3 1 |
| Family null · `(global)` | 20 (24 %) · 1 | 17 (23 %) · 2 |
| Distinct families · with one node | 42 · 28 | 43 · 36 |
| Terms · used by one node only | 162 · 128 (79 %) | 126 · 91 (72 %) |
| Status `ambiguous` · `unchecked` | 52 (62 %) · 32 | 54 (73 %) · 20 |
| Top ambiguity kinds | referential 27 · unresolved_term 20 · missing_actor 11 · missing_modality 7 · mixed_layers 6 | referential 26 · missing_modality 20 · unresolved_term 17 · scope 8 · missing_actor 7 |
| Attention items | term_same 16 · atomize_failed 3 · inferred 2 · term_unsure 1 | term_same 11 · atomize_failed 12 · inferred 2 · term_unsure 2 |
| Store checks | all eight clean | all eight clean |

**Spread between the runs, same 63 blocks:** 31 blocks (49 %) got the same number of nodes. Of the 16
blocks that formed exactly one node in both runs, the layer agreed on 10 and the family on 10.

**Cost extrapolated to the whole repository** (747 non-code blocks, *to be measured*): ≈ $0.024 and
≈ 15 s per block → ≈ **$18 and ≈ 3 hours** per full compile from scratch; with the lock, a re-compile
pays only for changed and previously failed blocks.

## B3. What held

- **The pipeline is robust.** Both runs' stores passed all eight consistency checks.
- **I-43 worked live.** Run 1 hit the session usage limit (429) after 448 s: 18 finished blocks were
  written, exit 6. The resumed compile asked only for the unfinished blocks and replayed 54 recorded
  answers.
- **D23 removed the bold-title failures:** `bold_title` completed 9 of 9 in both runs (was 4 of 31
  `vision.md` blocks failing every run). 8 nodes carry `mixed_layers` across the two runs.
- **`inferred` is rare** (2.4–2.7 %) and each flag read as real.
- **One new bug, fixed:** run 2 first crashed when Q-TERM merged B into A after A had merged away in the
  same batch (I-45); merges now follow the chain. Test added.

## B4. What did not hold — findings

| # | Finding | Evidence | Consequence |
|---|---|---|---|
| **G-1** | **Families do not group.** A quarter of nodes have no family; 28–36 of ~42 families hold one node; 72–79 % of terms are used once | §2 | F5 retrieval (S1 same family, S4 adjacent layer) and the M3 family views have little to work with |
| G-2 | Family null causes (run 1): no subject term tagged 10, subject is a `component` with no entity in the response 6, subject is a `category` 4 | Run 1 store | Partly the prompt (subjects left untagged), partly F2 §4.4's rule |
| **G-3** | **Q-TERM merges *kinds of* as *same*.** Of 16 `same` verdicts in run 1, about 10 are hyponyms: "review item", "attention item" → `item`; "term id", "judgment id" → `id`; "batch run" → `run`; "violation report" → `report` | `review.jsonl` details | Under F3 D20 these merge at once, pooling unrelated nodes into generic families (`term:id`, `term:item`) — the opposite of what families are for. The T10 evidence for D20 (7 of 8 plausible) did not hold at gate scale |
| G-4 | **`C` is over-assigned**, especially for front matter: 8 of 11–13 header nodes are `C` in both runs; "never renumbered", "One feature = one spec" become constraints | Layer answers: Q1 quotes | Q1's wording lists trigger words ("every / all / never"), and the model matches on them |
| G-5 | **Two thirds of nodes are `ambiguous`.** `referential` alone is on about a third of nodes | §2 | The attention list and the report will be dominated by ambiguity; conflicts may be hard to see |
| **G-6** | **Fresh runs disagree.** Half the blocks change node count between runs; for single-node blocks, layer and family agree only 10 of 16 | §2 spread | A graph is reproducible only through the judgment lock (F3 D21), never by re-asking. Conflict results will depend on which run's answers were locked |
| G-7 | G2 rejections in run 2 are mostly genuine — paraphrase, elided quotes ("term of kind ... `data`"), a quoted section heading — but one is formatting: dropped backticks around `` `SDD_COMPILER_CHILD=1` `` | Failure details | Backticks are the same class as `*` (F3 D9) |
| G-9 … G-14 | From the block-by-block review: empty nodes pass the guards, acceptance criteria split into Given/When/Then fragments, titles and notes become claims, rationale fails coverage, a sentence-initial capital fails G2, internal rules land in `L1` | Part C §C3 | See R7 … R11 |
| G-8 | **Traceability rows become nodes.** Table rows such as `\| AC-1.24 \| tests/… \| src/… \|` became `V` nodes with no family in both runs; and the test-tier tag `→ *unit.*` still becomes a stray `V` atom sometimes (I-24; run 2, `AC-1.31`) | Hand-review sheet, `table_row` and `criterion` | Bookkeeping *about* the specs enters the graph as claims. Owner question: exclude traceability tables (e.g. by heading, via the profile) or keep them |

## B5. Recommendations — owner decisions before the M4 gate

| # | Change | Addresses | Size |
|---|---|---|---|
| **R1** | **Q-TERM gains a verdict `narrower`** ("a kind of"), which keeps the terms separate with no review item; only true synonyms and spelling variants are `same`. Revisits F3 D20's premise | G-3 | small (schema `q-term/2`, prompt) |
| **R2** | **Show Q-DESC the existing term names** (the registry, bounded — e.g. the 100 most used) and ask it to reuse a name where one fits | G-1, G-2 | small (prompt); likely the largest lever on families |
| R3 | **Reword Q1** without trigger words: "Does it restrict many parts of the system at once (a budget, an invariant, a policy), rather than state one behaviour?" | G-4 | small (prompt) |
| R4 | F2 §4.4: when no rule applies, take the **first entity/data/event term anywhere** in the node before falling back to null | G-2 | small (rule change, F2 decision) |
| R5 | Extend F3 D9: backticks are layout, like `*` | G-7 | tiny |
| R7 | Canonical `subject` and `response` must be non-empty; an empty answer is re-asked | G-9 | tiny |
| R8 | Owner question: an acceptance criterion becomes **one `V` node** verifying the requirement it tests, its Given/When kept as context | G-10, G-8 | medium (Q-ATOM prompt, perhaps F3) |
| R9 | Q-ATOM prompt: examples of each non-claim role (title, note, open question, rationale after *Why:* / *Rejected:*) from our own specs | G-11, G-12 | small |
| R10 | Extend F3 D9: a case difference in the **first letter** of a quote is tolerated | G-13 | tiny |
| R11 | Reword Q3 (`L1`) so internal rules stop landing in behaviour | G-14 | small |
| R6 | Re-measure after the approved changes on the same sample (the lock replays nothing, since the prompts change) | all | ≈ $3, 30 min |

**On sequencing:** M3 (views) can be built now — its code does not depend on these answers. M4's
retrieval leans on families and terms, so R1–R4 should land before the M4 gate compiles the repository.

---

# Part C — Hand review of every sampled block

> **Reviewer:** Claude, 2026-09-18, at the owner's request. **Owner:** confirm or override each row in
> the last column. This replaces the separate `M2-gate-review.md`, merged here for easier maintenance.

## C1. How the rows were judged

Each run's nodes for a block are judged against the block's text, on four questions:

1. **Atomization.** Is every claim in the block captured once, with nothing lost, duplicated or invented, and no title, note or bookkeeping turned into a claim?
2. **Canonical form.** Does *subject · modality · response* say what the source says, conditions included?
3. **Layer.** Is it the layer a careful reader would choose (see §A7)?
4. **Family.** Does the node sit with the thing it is about?

| Verdict | Meaning |
|---|---|
| ✅ accept | The claims are captured faithfully, and layer and family are defensible. Also used when the block correctly formed **no** node (a heading, legend, TODO, open question) |
| ⚠️ partly | The claims are there, but a person would have to fix a layer, a family, an extra node or a lost detail |
| ❌ reject | A claim is lost or distorted, noise nodes dominate, an empty node was formed, or the block failed and stayed pending |

Each cell shows the node as `layer · family · subject | modality | response · ambiguity`; "—" means no node.

## C2. The verdicts in numbers

| Shape | Run 1 | Run 2 |
|---|---|---|
| bold_title | 4 ✅ · 5 ⚠️ · 0 ❌ | 1 ✅ · 4 ⚠️ · 4 ❌ |
| criterion | 1 ✅ · 6 ⚠️ · 2 ❌ | 0 ✅ · 6 ⚠️ · 3 ❌ |
| decision | 0 ✅ · 6 ⚠️ · 3 ❌ | 2 ✅ · 4 ⚠️ · 3 ❌ |
| header | 5 ✅ · 1 ⚠️ · 3 ❌ | 1 ✅ · 5 ⚠️ · 3 ❌ |
| list_item | 4 ✅ · 5 ⚠️ · 0 ❌ | 2 ✅ · 3 ⚠️ · 4 ❌ |
| paragraph | 5 ✅ · 2 ⚠️ · 2 ❌ | 5 ✅ · 2 ⚠️ · 2 ❌ |
| table_row | 4 ✅ · 0 ⚠️ · 5 ❌ | 1 ✅ · 3 ⚠️ · 5 ❌ |
| **All 63** | **23 ✅ · 25 ⚠️ · 15 ❌** | **12 ✅ · 27 ⚠️ · 24 ❌** |

**In plain words:** in run 1, about 4 blocks in 10 came out right (23 of 63), 4 in 10 partly right (25) and
1 in 4 wrong (15). In run 2, only 1 in 5 came out right (12) and nearly 4 in 10 wrong (24), mostly because
run 2 **failed** 12 blocks, which stay pending and count here as wrong. The blocks that came out
**partly** right almost all have the same few problems, listed in C3. The best shapes are the plain
bullets and headers of rules (B-000708, B-000329); the worst are traceability rows and titles or notes
that became claims.

## C3. What the review adds to the findings (G-9 … G-14)

| # | Finding | Rows | Proposed fix |
|---|---|---|---|
| **G-9** | **Empty nodes pass the guards.** The model returned a canonical form with an empty subject or response, and the schema accepted it | B-000583 (run 1) | Schema: `subject` and `response` must be non-empty (`minLength: 1`); an empty answer is re-asked. Tiny |
| **G-10** | **Acceptance criteria are split into Given / When / Then fragments**, and the Given and When parts become claims of their own. The tier tag `→ *unit.*` adds a stray node (G-8) | B-000082, 085, 086, 500, 506 | Owner question: should an acceptance criterion be **one `V` node** that verifies the requirement it tests, with the Given/When as its context? That matches what a criterion is, and would remove most of the noise |
| **G-11** | **Titles, notes, open questions and process remarks become claims.** Q-ATOM has roles for them (`context`, `open_question`, `rationale`), but the model does not always use them | B-000194, 357, 415, 416, 731, 733 | Prompt: examples of each non-claim role, drawn from our own specs |
| **G-12** | **Coverage (G3) fails on rationale that uses normative words** ("would silently *never* be atomized"), losing whole decisions: F1 D13 failed in both runs | B-000096, 404 | Prompt: say explicitly that sentences after *Why:* or *Rejected:* are rationale. Or relax G3 for sentences labelled rationale |
| **G-13** | **A capital at the start of a sentence fails the quote guard.** The model wrote "a Q-TERM…" for "A Q-TERM…", so G2 rejected the block in both runs | B-000410 | Extend F3 D9: tolerate a case difference in the **first letter** of a quote only. Case elsewhere still counts |
| **G-14** | **Internal rules land in `L1`.** Hashing, id formats, field rules and fallback rules were filed as behaviour an outsider can see; `L4` and `L5` are under-used | B-000029, 044, 146, 190, 311 | Reword Q3 (the `L1` question) the way R3 rewords Q1: *an outsider can see it without looking inside the system* |
| — | *Confirms* G-1/G-2 (families missing, generic or split: 29 of 63 rows name a family problem), G-4 (`C` for notes and test expectations), G-7 (backticks: B-000363), G-8 (traceability rows: B-000106, 107, 249) | — | R1 … R5 |

## C4. Every row

### bold_title (9 blocks — run 1: 4 ✅ · 5 ⚠️ · 0 ❌; run 2: 1 ✅ · 4 ⚠️ · 4 ❌)

| Block | Text | Run 1 | Run 2 | R1 | R2 | Reason | Owner |
|---|---|---|---|---|---|---|---|
| B-000029 | - **Hashing:** `text_hash` = SHA-256 of the block text after normalizing line endings to `\n`,   trimming trailing whitespace per  | `L1` · `term:text_hash` · `text_hash` \| MUST \| equal SHA-256 of the normalized block text<br>`L1` · `None` · Case, punctuation and inner whitespace \| MUST \| be preserved in the text hash · _scope, unresolved_term_ | `L1` · `term:text_hash` · `text_hash` \| None \| equals SHA-256 of the block text · _missing_modality_<br>`L1` · `term:case` · Case, punctuation and inner whitespace \| MUST \| be preserved · _scope_ | ⚠️ | ⚠️ | Both split it correctly into the hash rule and the preservation rule. Wrong in both: layer `L1`, but hashing is an internal rule (`L5`). The second claim's family is missing (run 1) or `case` (run 2); it belongs to `text_hash`. | |
| B-000112 | - **placement** — layer and family, decided by code from recorded answers; | — | `L5` · `term:placement` · placement \| None \| is determined by layer and family, decided by code from · _missing_modality_ | ✅ | ⚠️ | A purpose line in F2's goal list. Run 1 treats it as context, which is fine. Run 2 turns it into an `L5` claim with no modality; defensible ("decided by code" is a real rule), but a person must confirm it. | |
| B-000113 | - **retrieval** — finding related nodes (F5) without re-reading prose. | — | — | ✅ | ✅ | A purpose line. Both runs correctly formed no node. | |
| B-000415 | - **Q1 — Default `max_calls_per_run`** (200 here) and `timeout_s` (120 here): set from the first real   measurements. *Q2 closed 2 | `V` · `term:model_alias_flag` · `--model haiku` flag \| None \| resolves to `claude-haiku-4-5-20251001`<br>`C` · `term:model` · model actually used \| MUST \| be recorded | `L4` · `term:max_calls_per_run` · Default max_calls_per_run and timeout_s \| None \| set from the first real measurements (200, 120)<br>`V` · `None` · --model haiku flag \| None \| resolves to claude-haiku-4-5-20251001 and change of ali · _unresolved_term_ | ⚠️ | ❌ | An open question (Q1) followed by a closed-question note. Run 1 kept only the closed note's facts; "model actually used MUST be recorded" is right, but its layer is `C` (it is a per-call rule, `L5`) and the alias fact became `V`. Run 2 made the **open question** a claim ("set from the first real measurements"): an open question is not a claim. | |
| B-000416 | - **Q3 — Q-TERM candidate count N** (similar existing names shown to the model). Default 10. | — | `L4` · `term:q_term_candidate_count` · Q-TERM candidate count N \| None \| default 10 (similar existing names shown to model) | ✅ | ❌ | An open question with a default. Run 1 correctly formed no node. Run 2 made it an `L4` claim. | |
| B-000430 | - **Collapsed form, for humans:** aggregated by family and layer, with drill-down, as CLI text and   generated Markdown views. | `L4` · `term:family` · views \| MUST \| be aggregated by family and layer, with drill-down, as  | `L4` · `term:collapsed_form` · data \| None \| aggregated by family and layer · _referential, missing_modality_<br>`L1` · `None` · view \| None \| with drill-down · _missing_modality, unresolved_term_<br>`L1` · `None` · view \| None \| as CLI text and generated Markdown views · _missing_modality, unresolved_term_ | ⚠️ | ❌ | Run 1 has one node, correctly: one obligation with several parts. But its layer is `L4` (what people *see* is `L1`) and its family is the generic `family`. Run 2 over-split it into three nodes ("with drill-down", "as CLI text"), breaking the list rule (one obligation, one node); two have no family. | |
| B-000735 | - **Model access:** Claude Code with **Haiku**: | `L2` · `None` · model access \| None \| is Claude Code with Haiku · _unresolved_term_ | `L2` · `None` · Model access \| None \| use Haiku · _missing_actor, missing_modality, unresolved_term_ | ⚠️ | ⚠️ | A lead-in to the stack list. Both chose `L2` (structure) correctly, but neither found a family: "Model access" was not tagged as a term. | |
| B-000762 | - **No new specification language.** Authors keep writing ordinary Markdown. Structure is inferred,   never demanded. | `L1` · `None` · new specification language \| MUST NOT \| be introduced · _unresolved_term_<br>`L1` · `term:markdown` · Authors \| MUST \| keep writing ordinary Markdown<br>`L1` · `term:structure` · Structure \| MUST \| be inferred, never demanded | `C` · `term:markdown` · Authors \| None \| write ordinary Markdown · _missing_modality_<br>`C` · `term:structure` · Structure \| MUST NOT \| be demanded · _referential_ | ⚠️ | ⚠️ | Three claims. Run 1 found all three, but at `L1`; these are product principles (`L0`/`C`), and the first has no family. Run 2 lost "no new specification language" and kept two at `C`. | |
| B-000763 | - **No editing of specs by the compiler.** It reports; people and their agents decide and rewrite. | `L1` · `term:spec` · compiler \| MUST NOT \| edit specs<br>`L1` · `term:spec` · people and their agents \| None \| decide and rewrite specs · _referential_ | `C` · `term:spec` · compiler \| MUST \| report; people and their agents decide and rewrite · _referential, pending_review_ | ✅ | ❌ | Run 1 is right: "compiler MUST NOT edit specs", plus the users' role. Run 2 **lost the prohibition**: its only node says "compiler MUST report", which inverts the emphasis of the source. | |

### criterion (9 blocks — run 1: 1 ✅ · 6 ⚠️ · 2 ❌; run 2: 0 ✅ · 6 ⚠️ · 3 ❌)

| Block | Text | Run 1 | Run 2 | R1 | R2 | Reason | Owner |
|---|---|---|---|---|---|---|---|
| B-000082 | - **AC-1.31** *(pending until processed; D13)* — **Given** three blocks ingested and none atomized,   **when** the unchanged file  | `C` · `term:pending_status` · all three blocks \| MUST \| be still pending · _referential_<br>`C` · `term:pending` · two blocks \| MUST \| be pending · _referential, mixed_layers_<br>`L4` · `term:changed_status` · that block \| MUST \| be pending again as `changed` · _referential_ | `L4` · `term:block` · all three blocks \| MUST \| be still pending (new)<br>`L4` · `term:block` · two blocks \| MUST \| be pending<br>`L4` · `term:block` · it \| MUST \| be pending again as `changed` · _referential_<br>`V` · `term:block` · AC-1.31 \| None \| unit test verification | ❌ | ⚠️ | AC-1.31 has three given/then checks. Run 1 filed two of them as `C` (they are test expectations, not rules over many nodes) and spread them across three families (`pending_status`, `pending`, `changed_status`). Run 2 kept all three in one family (`block`), which is the grouping families are for, at `L4`. But it adds a stray `V` node made from the `→ *unit.*` tag (G-8). | |
| B-000085 | - **AC-1.21** *(pending output contract)* — **Given** a store with pending blocks, **when**   `sddc status --json` runs, **then**  | `L0` · `None` · AC-1.21 \| None \| pending output contract · _missing_modality, unresolved_term_<br>`L1` · `term:stdout` · stdout \| MUST \| be exactly one JSON object valid against CT-1.5 | `L2` · `None` · the test context \| None \| exists with pending blocks · _missing_actor, missing_modality, unresolved_term_<br>`L1` · `None` · the command \| None \| runs · _missing_modality, unresolved_term_<br>`L1` · `term:stdout` · stdout \| MUST \| be exactly one JSON object valid against CT-1.5 | ⚠️ | ⚠️ | Both found the real claim (stdout MUST be exactly one JSON object…) and placed it identically. Both add noise: run 1 turned the *title* into an `L0` claim; run 2 turned the *Given* and *When* into claims with no family. | |
| B-000086 | - **AC-1.22** *(non-UTF-8 fails atomically)* — **Given** one valid file and one non-UTF-8 file in a   single `ingest`, **when** ru | `L1` · `None` · the command \| MUST \| exit with code `2` naming the bad file · _unresolved_term_<br>`L1` · `term:store_file` · the store file \| MUST NOT \| change<br>`V` · `term:store_file` · AC-1.22 \| None \| verified by integration test | `L1` · `term:exit_code` · exit code \| MUST \| be `2` naming the bad file · _referential, mixed_layers_<br>`L1` · `term:store_file` · store file \| MUST NOT \| change<br>`V` · `term:exit_code` · the system \| None \| exits with code 2 naming the bad file, and no store fil · _missing_actor, referential_ | ⚠️ | ⚠️ | Both found the two real claims (exit `2` naming the file; no store file changes). Both add a `V` node restating the criterion ("verified by integration test"), made from the tier tag. The exit-code claim has no family in run 1. | |
| B-000363 | - **AC-3.1** *(child environment)* — **Given** `ANTHROPIC_API_KEY` in the parent environment and   `pass_api_key: false`, **when** | `V` · `None` · child environment \| MUST \| have `SDD_COMPILER_CHILD=1` and no `ANTHROPIC_API_KEY` · _unresolved_term_<br>`V` · `term:command_line` · command line \| MUST \| contain `-p`, `--model haiku`, `--output-format json`,  | — | ⚠️ | ❌ | Run 1 found both checks (child environment; command line) as `V`, which suits an acceptance criterion; the first has no family. Run 2 **failed**: the model dropped the backticks around `` `SDD_COMPILER_CHILD=1` `` (R5 would fix this). | |
| B-000365 | - **AC-3.3** *(usage recorded)* — **Given** a fake response carrying usage and cost, **when** accepted,   **then** the judgment re | `V` · `term:judgment_record` · judgment record \| MUST \| contain usage, cost, backend, model and CLI version · _referential_ | — | ✅ | ❌ | Run 1 is right: the judgment record MUST contain usage, cost, backend, model and CLI version. Run 2 **failed**: it quoted "contain them", but the source says "contains them". | |
| B-000500 | - **AC-4.2** *(family move)* — **Given** a node whose family changes from `term:a` to `term:b`, **when**   the transaction commits | `L1` · `term:node` · it \| MUST \| appear only in `nodes/b.jsonl`, and its outgoing links  · _referential_<br>`V` · `term:node` · AC-4.2 \| None \| be verified by unit test | `L1` · `term:node` · the node \| MUST \| appear only in `nodes/b.jsonl`, and its outgoing links <br>`L1` · `None` · AC-4.2 \| None \| verified at unit level · _unresolved_term_ | ⚠️ | ⚠️ | Both found the real claim (the node appears only in `nodes/b.jsonl`; its links move). Both add a node made from the tier tag ("verified by unit test"). | |
| B-000506 | - **AC-4.7** *(membership enforced)* — **Given** a stored node missing a `conflict_ids` entry for an open   record that lists it,  | `L1` · `term:node` · the node \| None \| have a `conflict_ids` entry · _missing_actor, missing_modality_<br>`L1` · `None` · the check \| MUST \| report the violation and exit with code `4` · _referential, mixed_layers, unresolved_term_ | `L1` · `term:node` · stored node \| None \| missing a `conflict_ids` entry for an open record that  · _referential_<br>`L1` · `None` · sddc check \| MUST \| report the violation · _referential, unresolved_term_<br>`L1` · `None` · sddc check \| MUST \| exit with code 4 · _unresolved_term_ | ⚠️ | ⚠️ | Both found "`sddc check` MUST report and exit `4`" (run 2 splits it in two, which is acceptable). Both also turned the *Given* precondition into a claim, which it is not. The check claims have no family. | |
| B-000583 | - **AC-5.8** *(first node of a family)* — **Given** a graph where a node's family, terms and block are   unique to it, **when** ca | `L1` · `term:node` · assumption \| None \| <br>`V` · `None` · verification \| None \|  · _missing_actor, unresolved_term_<br>`C` · `term:candidate` · any candidate \| MUST \| comes from S5 or S6 · _referential_<br>`L1` · `term:result` · result \| MAY \| may be empty · _referential_ | `C` · `term:candidate` · any candidate \| MUST \| come from S5 or S6 · _referential_<br>`L4` · `term:result` · the result \| MAY \| be legitimately empty · _referential_ | ❌ | ⚠️ | Run 1 contains **two empty nodes** (subject "assumption" / "verification", empty response): the model returned blank fields and no guard caught it (G-9). Run 2 is clean: "any candidate MUST come from S5 or S6" and "the result MAY be empty". Its layer is `C`, where the retrieval rule should be `L5`. | |
| B-000658 | - **AC-6.3** *(refines and depends_on make links only)* — **Given** fake `refines` and `depends_on`   answers, **then** links of t | `L4` · `term:outgoing_link` · links of those types \| MUST \| exist with `provenance: judgment`, a judgment id and a  · _missing_actor_<br>`L1` · `term:outgoing_link` · links of those types \| MUST \| exist with `provenance: judgment`, a judgment id and a <br>`L1` · `term:conflict_record` · conflict record \| MUST NOT \| exist | `L4` · `term:refines_link` · links of refines and depends_on types \| None \| exist with `provenance: judgment`, a judgment id and a  · _referential, missing_modality_<br>`L1` · `term:judgment_provenance_link` · judgment-provenance links \| MUST \| exist with `provenance: judgment`, a judgment id and a  | ⚠️ | ❌ | Run 1 found "no conflict record exists", but states the links claim **twice** (`L4` and `L1`). Run 2 states the links claim twice and **misses** the no-conflict-record check. | |

### decision (9 blocks — run 1: 0 ✅ · 6 ⚠️ · 3 ❌; run 2: 2 ✅ · 4 ⚠️ · 3 ❌)

| Block | Text | Run 1 | Run 2 | R1 | R2 | Reason | Owner |
|---|---|---|---|---|---|---|---|
| B-000096 | - **D13 — The block record stores facts; the run's delta and the pending set are derived** (closes   Q6, option c, 2026-09-18). `s | — | — | ❌ | ❌ | **Failed in both runs**: a rationale sentence ("they would silently never be atomized") contains the normative word *never*, and the model did not label it as rationale, so coverage (G3) rejected the answer twice. The decision itself (F1 D13) is lost from the graph (G-12). | |
| B-000242 | - **D11 — Ambiguity kind `missing_modality`** (F3 D14): a requirement or constraint that states no modal   verb is formed with `mo | `L1` · `term:modal_verb` · a requirement or constraint that states no modal verb \| None \| formed with `modality: null` and this ambiguity · _referential_ | `L5` · `term:kind` · Ambiguity kind `missing_modality` \| None \| a requirement or constraint that states no modal verb i | ⚠️ | ⚠️ | Both captured the rule (a requirement without a modal verb is formed with `modality: null` and flagged). Families are poor (`modal_verb`, `kind`); they should be `missing_modality` or the ambiguity kind. | |
| B-000391 | - **D1 — Headless Claude Code is the default backend** (rel01 D7). *Rejected:* prompt hooks — they   return only `ok`/`reason`. | `L1` · `None` · default backend \| None \| is Headless Claude Code · _unresolved_term_ | `L1` · `None` · backend selection \| None \| Headless Claude Code is the default backend · _unresolved_term_ | ⚠️ | ⚠️ | Both captured "headless Claude Code is the default backend" as a decision, but at `L1`: a backend choice is structure (`L2`). Neither found a family ("backend" was not tagged as a term). | |
| B-000394 | - **D4 — One batch run, one report** (rel01 D26). Nothing stops mid-run; every conflict and every   attention item is reported at  | `None` · `term:run` · batch run \| None \| produces one report · _unplaceable_<br>`C` · `term:run` · batch run \| MUST NOT \| stop mid-run; all conflicts and attention items must be | `L1` · `term:batch_run` · the batch run \| MUST NOT \| stop mid-run · _missing_actor_<br>`C` · `term:conflict_record` · every conflict and every attention item \| MUST \| be reported at the end · _mixed_layers_<br>`None` · `None` · stopping at first conflict and AI fix loop with attempts and escalation \| None \| rejected because both require live editing · _referential, missing_modality, unplaceable, unresolved_term_ | ⚠️ | ⚠️ | Run 1 found both halves but merged "never stops" and "reports everything at the end" into one node; its other node is unplaced. Run 2 split the halves correctly, but made the **rejected alternative** a claim of its own (unplaced, no family). Rejected options belong in the decision's `rejected` field, not in a node. | |
| B-000397 | - **D7 — ⚑ Size units:** KB/MB/GB are decimal, KiB/MiB/GiB binary. | `L1` · `None` · KB/MB/GB \| None \| are decimal · _unresolved_term_ | `L1` · `None` · size unit representation \| None \| KB/MB/GB are decimal, KiB/MiB/GiB binary · _unresolved_term_ | ❌ | ⚠️ | Run 1 **lost half the claim** (the KiB/MiB/GiB part). Run 2 kept both halves, but has no family and sits at `L1` (data units are `L4`). | |
| B-000402 | - **D12 — ⚑ Months and years are not normalized.** Neither has a fixed length; converting one would   invent a number. The raw val | `L1` · `term:month` · months and years \| None \| are not normalized<br>`L1` · `term:raw_value` · raw value and unit \| MUST \| be kept | `L4` · `term:month` · Months and years \| None \| are not normalized<br>`L4` · `term:raw_value` · raw value and unit \| None \| are kept · _referential, pending_review_ | ⚠️ | ✅ | Both captured both claims. Run 1 used `L1`; run 2's `L4` fits a rule about stored values. Run 2's `pending_review` flag on `raw_value` comes from a Q-TERM "unsure", not from an error. | |
| B-000404 | - **D14 — A requirement or constraint without a modality is formed and flagged** (closes Q6, option b).   `canonical.modality` is  | `L1` · `None` · requirement or constraint without modality \| None \| is formed and flagged · _mixed_layers, unresolved_term_<br>`L4` · `term:node` · node with null canonical.modality \| None \| carries ambiguity `missing_modality`, status derives to · _mixed_layers_ | — | ⚠️ | ❌ | Run 1 captured the rule, flagged `mixed_layers`; the first node has no family. Run 2 **failed** coverage (G3): the rationale sentence containing `MUST` ("defaulting to MUST would invent…") was not labelled. | |
| B-000410 | - **D20 — A Q-TERM `same` verdict merges at once, and a person may undo it** (closes Q7, option b).   The new name becomes an alia | — | — | ❌ | ❌ | **Failed in both runs, for the same reason**: the model quoted "a Q-TERM `same` verdict merges", but the source starts the sentence with a capital "A". G2 treats case as meaning, so a sentence-initial capital fails the block (G-13). | |
| B-000600 | - **D8 — One fixed, versioned stop-word list in code** for `keywords` (resolves Q3, and F2 Q2 for the   same field). *Rejected:* a | `L4` · `None` · stop-word list \| None \| one fixed, versioned list in code · _unresolved_term_ | `L4` · `term:stop_word_list` · stop-word list \| MUST \| be one fixed, versioned list in code | ⚠️ | ✅ | Both captured "one fixed, versioned stop-word list in code". Run 1 found no family; run 2 filed it under `stop_word_list` with a MUST. | |

### header (9 blocks — run 1: 5 ✅ · 1 ⚠️ · 3 ❌; run 2: 1 ✅ · 5 ⚠️ · 3 ❌)

| Block | Text | Run 1 | Run 2 | R1 | R2 | Reason | Owner |
|---|---|---|---|---|---|---|---|
| B-000109 | > **Spec-ID:** F2 · **Status:** 🟢 approved · **Drafted:** 2026-09-15 · **Approved:** 2026-09-15 (rel01 D23) > ⛔ **Coding gated (re | `C` · `term:implementation` · implementation \| MUST NOT \| begin until G3 and G4 are reviewed and the build plan e | `None` · `term:implementation` · implementation work \| MUST NOT \| begin until G3 and G4 are reviewed and the build plan e · _referential, unplaceable_ | ✅ | ⚠️ | Both extracted the one real claim (no implementation until G3 and G4 are reviewed and the build plan exists) and correctly ignored the Spec-ID, status and dates. Run 1 placed it at `C`, which fits a rule over all coding; run 2 left it unplaced. Note: the claim is out of date, and the graph faithfully records what the spec says. | |
| B-000194 | > Test tiers are provisional names pending constitution §4. | `L1` · `term:test_tier` · Test tiers \| None \| are provisional names · _referential, missing_modality_<br>`L1` · `term:test_tier` · Test tiers \| None \| are provisional pending constitution §4 · _referential, missing_modality_ | `C` · `(global)` · Test tiers \| None \| are provisional names pending constitution §4 · _referential, scope, missing_modality_ | ❌ | ⚠️ | A status note about the specs, not a claim in them. Run 1 made **two near-identical** nodes from one sentence. Run 2 made one node, `C (global)`; still a note filed as a rule. Best: no node, or one flagged note. | |
| B-000497 | > Tiers are provisional. | — | `L1` · `term:tier` · Tiers \| None \| are provisional · _referential, missing_modality_ | ✅ | ⚠️ | "Tiers are provisional.": a status note. Run 1 correctly formed no node; run 2 made one (flagged). | |
| B-000537 | > **Spec-ID:** F5 · **Status:** 🟢 approved · **Drafted:** 2026-09-17 · **Approved:** 2026-09-18 (rel01 D28) > ⛔ **Coding gated (re | `C` · `term:coding` · coding \| MUST NOT \| proceed until release 01 decision point D20 is reached · _missing_actor, inferred_ | `C` · `term:coding` · Coding \| MUST NOT \| proceed until rel01 D20 · _scope_<br>`C` · `(global)` · F5 \| MUST \| depend on F2 (node properties) and F4 (indexes), and fe | ⚠️ | ❌ | Run 1 extracted the coding gate at `C`, correctly flagged `inferred` (the model expanded "D20" in its own words). Run 2 also made a claim from the "Depends on / feeds" metadata line (F5 MUST depend on F2 and F4): spec bookkeeping filed as a rule. | |
| B-000691 | > **Status:** live · opened 2026-09-14 · six specs written. This folder is authoritative once a spec is > approved; rel01 D20 gate | `C` · `term:implementation` · the spec folder \| MUST \| be authoritative; rel01 D20 gates implementation separa · _referential, inferred_ | `C` · `term:implementation` · this folder \| MUST \| be authoritative; rel01 D20 gates implementation separa · _referential, inferred_ | ❌ | ❌ | Both dropped the **condition**: the source says the folder is authoritative *once a spec is approved*; both canonical forms say it MUST be authoritative, full stop. G4 flagged both as `inferred`, so the error is visible, but the claim is distorted. | |
| B-000699 | > IDs are claimed here and **never renumbered**. | `None` · `term:id` · IDs \| MUST \| be claimed here · _missing_actor, unplaceable_<br>`C` · `term:id` · IDs \| MUST NOT \| be renumbered · _referential, mixed_layers_ | `C` · `term:id` · IDs \| MUST NOT \| be renumbered · _scope_ | ✅ | ⚠️ | "IDs are claimed here and never renumbered." Run 1 found both halves; the invariant at `C` is right. Run 2 kept only "never renumbered". | |
| B-000708 | > Every id family in use is declared here **before** it is used. An undeclared family is a defect. > Declared 2026-09-15 (rel01 S7 | `C` · `term:id_family` · every id family \| MUST \| be declared before it is used · _referential_<br>`C` · `term:id_family` · an undeclared family \| MUST NOT \| exist in the system | `C` · `term:id_family` · every id family \| MUST \| be declared before it is used · _scope_<br>`C` · `term:id_family` · an undeclared family \| MUST NOT \| exist (it is a defect) | ✅ | ✅ | Both identical and right: two constraints (every id family declared before use; an undeclared family is a defect) at `C`, family `id_family`. **The best row in the sample.** | |
| B-000725 | > **Adopted:** rel01 D29 (2026-09-18). Every acceptance criterion maps to **exactly one** tier. The > tier decides the *shape* of  | `C` · `term:tier` · every acceptance criterion \| MUST \| map to exactly one tier<br>`C` · `term:tier` · the tier \| None \| decides the shape of the test · _referential, missing_modality_ | `C` · `term:acceptance_criterion` · every acceptance criterion \| MUST \| map to exactly one tier; the tier decides the shape of  · _scope, inferred_ | ✅ | ⚠️ | Run 1 is right: each acceptance criterion maps to exactly one tier; the tier decides the shape of the test, at `C`, family `tier`. Run 2 merged both into one node, flagged `inferred`. | |
| B-000733 | > **Adopted:** rel01 D3 (2026-09-14). Details marked TODO are decided when F1 is specified. | `L2` · `None` · SDD Compiler build stack \| None \| is rel01 D3, adopted 2026-09-14 · _unresolved_term_<br>`None` · `term:todo_detail` · Details marked TODO \| MUST \| be decided · _missing_actor, referential, unplaceable_ | `None` · `term:todo_detail` · details marked TODO \| None \| are decided · _missing_actor, unplaceable_ | ❌ | ❌ | A process note ("Adopted: rel01 D3… details marked TODO are decided when F1 is specified"). Both made claims of it, unplaced or without a family. It should form no node (G-11). | |

### list_item (9 blocks — run 1: 4 ✅ · 5 ⚠️ · 0 ❌; run 2: 2 ✅ · 3 ⚠️ · 4 ❌)

| Block | Text | Run 1 | Run 2 | R1 | R2 | Reason | Owner |
|---|---|---|---|---|---|---|---|
| B-000044 | - `id` has the form `B-` plus 6 or more zero-padded digits, is assigned once, and is never reused. | `L1` · `term:id` · `id` \| MUST \| have the form `B-` plus 6 or more zero-padded digits · _mixed_layers_<br>`L1` · `term:id` · id \| MUST NOT \| be reused after assignment | `L1` · `term:id` · `id` \| MUST \| have the form `B-` plus 6 or more zero-padded digits<br>`L1` · `term:id` · `id` \| MUST \| be assigned once<br>`L1` · `term:id` · `id` \| MUST NOT \| be reused | ⚠️ | ✅ | Run 2 is right: three claims (the form, assigned once, never reused). Run 1 merged "assigned once" into the form. Both chose layer `L1` and family `id`, but an id format is data (`L4`), and the family would better be `block`. | |
| B-000119 | - ✗ Finding candidate related nodes → F5. Judging pairs and creating conflict records → F6, which in   rel01 runs over the whole s | — | `None` · `term:candidate_related_node` · finding candidate related nodes \| None \| is governed by F5, not by F2 · _referential, missing_modality, unplaceable_<br>`C` · `term:conflict_record` · conflict records \| None \| are created and judged by F6, which runs over the whole · _referential, missing_modality_ | ✅ | ❌ | A non-goal pointer ("Finding candidate related nodes → F5 …"). Run 1 treats it as context, which is right for a cross-reference. Run 2 made two claims from it (one unplaced). | |
| B-000146 | 5. **Fallback** — nothing resolves → family `null`, ambiguity kind `unresolved_term`. | `L1` · `term:family` · family \| MUST \| be assigned `null` and ambiguity kind be set to `unreso | `L4` · `term:family` · family \| None \| becomes null with ambiguity kind unresolved_term · _referential, missing_modality_ | ⚠️ | ⚠️ | Both captured the fallback rule (nothing resolves → family null, ambiguity `unresolved_term`). The layers are `L1` and `L4`; this is internal logic (`L5`). | |
| B-000261 | - Node alignment across block edits. | `L1` · `term:node` · node alignment across block edits \| MUST NOT \| be a goal | `C` · `term:node_alignment` · Node alignment across block edits \| MUST NOT \| be a goal · _missing_actor_ | ⚠️ | ⚠️ | A non-goal list item. Both read it as "MUST NOT be a goal", which is fair, but the families differ (`node`, `node_alignment`) and the layers differ (`L1`, `C`). | |
| B-000262 | - Term registry updates. | `L1` · `None` · term registry updates \| MUST NOT \| be a goal · _unresolved_term_ | `C` · `term:term_registry` · Term registry updates \| MUST NOT \| be a goal · _missing_actor_ | ⚠️ | ⚠️ | Same pattern as B-000261; run 1 has no family. | |
| B-000311 | 6. Set `last_checked_run: null`. Status derives to `unchecked` or `ambiguous` (F2). | `L4` · `term:last_checked_run` · `last_checked_run` \| MUST \| be set to null · _missing_actor, scope_<br>`L1` · `term:status` · status \| MUST \| derive to `unchecked` or `ambiguous` · _referential_ | — | ⚠️ | ❌ | Run 1 found both claims (set `last_checked_run: null`; status derives to unchecked or ambiguous), at `L4` and `L1`; internal steps are `L5`. Run 2 **failed**: it quoted the section heading "Forming a node". | |
| B-000329 | - Pending blocks are processed in `(source path, first line)` order, so a run is reproducible. | `C` · `term:pending_block` · pending blocks \| MUST \| be processed in `(source path, first line)` order | `C` · `term:pending_block` · Pending blocks \| MUST \| be processed in `(source path, first line)` order for r | ✅ | ✅ | Both identical: pending blocks MUST be processed in (source path, first line) order, family `pending_block`. `C` is defensible (it governs every run); `L5` would also do. | |
| B-000612 | - ✗ Fixing conflicts, suggesting fixes, or editing specs (vision §5). | `C` · `term:conflict` · the system \| MUST NOT \| fix conflicts, suggest fixes, or edit specs · _missing_actor_ | — | ✅ | ❌ | Run 1 is right: the system MUST NOT fix conflicts, suggest fixes or edit specs, at `C`. Run 2 **failed** on an invented quote ("record the conflicts, report them"). | |
| B-000645 | - `--json` emits the same content as one object, for scripts and for G4 measurement. | `L1` · `term:sddc_status_json` · `--json` flag \| MUST \| emit the same content · _referential_<br>`L1` · `term:output` · output \| MUST \| be one object · _referential_ | — | ✅ | ❌ | Run 1 is right: two claims (`--json` emits the same content; as one object). Run 2 **failed**: the quote "emits... for scripts" elides the middle of the sentence. | |

### paragraph (9 blocks — run 1: 5 ✅ · 2 ⚠️ · 2 ❌; run 2: 5 ✅ · 2 ⚠️ · 2 ❌)

| Block | Text | Run 1 | Run 2 | R1 | R2 | Reason | Owner |
|---|---|---|---|---|---|---|---|
| B-000054 | **CT-1.4 — Profile** (`.sdd/profile.yaml`, written by `sddc init`, then hand-edited): | — | — | ✅ | ❌ | A contract's title line. Run 1 correctly formed no node. Run 2 **failed** on an invented quote ("Profile is at `.sdd/profile.yaml`"). | |
| B-000190 | `provenance: judgment` requires a non-null `judgment` and `rationale`. | `L1` · `term:provenance_judgment` · `provenance: judgment` \| MUST \| have a non-null `judgment` and `rationale` | `L1` · `term:provenance_field` · `provenance: judgment` \| MUST \| have a non-null `judgment` and `rationale` · _scope_ | ⚠️ | ⚠️ | Both captured the rule correctly (`provenance: judgment` requires a judgment and a rationale). Layer `L1`, where a rule on a record's fields is `L4`. The families disagree (`provenance_judgment`, `provenance_field`). | |
| B-000344 | Accepting or rejecting updates the affected nodes' facts, and their status is re-derived. An item whose cause disappears on a late | `C` · `term:affected_node` · affected nodes' facts and status \| MUST \| be updated and re-derived · _referential_<br>`L4` · `term:item` · item \| MUST \| close automatically with `state: resolved` · _referential_ | `L1` · `term:affected_node` · affected nodes' facts and status \| MUST \| be updated and re-derived · _referential_<br>`L1` · `term:attention_list_item` · item \| MUST \| close automatically with `state: resolved` | ⚠️ | ✅ | Both found both claims (a review decision updates facts and status; a resolved item closes itself). Run 2's `L1` fits; run 1 put the first at `C`. | |
| B-000357 | **CT-3.3 — Review item** (`.sdd/review.jsonl`) | `V` · `term:item` · Review item \| None \| stored at `.sdd/review.jsonl` | — | ❌ | ❌ | A contract's title line ("CT-3.3 — Review item"). Run 1 made it a `V` claim; run 2 **failed** on an invented quote. It should form no node (G-11). | |
| B-000377 | **Forming, identity, lock** | — | — | ✅ | ✅ | A bold subheading. Both correctly formed no node. | |
| B-000649 | Rules: `direction` must be `symmetric` for `none`, `duplicates` and `contradicts`. `confidence: low` adds ambiguity `low_confidenc | `L4` · `term:direction_field` · `direction` field \| MUST \| be `symmetric` for `none`, `duplicates` and `contradict<br>`L4` · `None` · ambiguity field \| MUST \| add `low_confidence_verdict` to both nodes rather than  · _unresolved_term_ | `L3` · `term:direction` · `direction` \| MUST \| be `symmetric` for `none`, `duplicates` and `contradict · _referential_<br>`L1` · `None` · ambiguity `low_confidence_verdict` \| None \| is added to both nodes rather than suppressing the verd · _referential, missing_modality, unresolved_term_ | ✅ | ⚠️ | Two rules, both found. Run 1 put both at `L4`, which suits field rules; the second has no family. Run 2 used `L3` and `L1`, with the second unflagged but without a family. | |
| B-000697 | Status legend: 🔵 idea · 🟡 draft (has ACs) · 🟢 approved (coding may start, unless a release gate says otherwise — rel01 D20 gates a | — | — | ✅ | ✅ | A status legend. Both correctly formed no node. | |
| B-000723 | *TODO.* | — | — | ✅ | ✅ | "*TODO.*" Both correctly formed no node. | |
| B-000731 | ⚠ **Getting the tier wrong is the quiet failure:** a property criterion given one example test looks green and proves almost nothi | `None` · `term:tier` · Getting the tier wrong \| None \| is the quiet failure · _missing_actor, referential, missing_modality, unplaceable_<br>`V` · `None` · a property criterion given one example test \| None \| looks green and proves almost nothing · _missing_actor, unresolved_term, pending_review_ | — | ❌ | ✅ | A warning: rationale about testing, not a claim. Run 1 made two claims of it (one unplaced, one `V`). Run 2 correctly formed no node. | |

### table_row (9 blocks — run 1: 4 ✅ · 0 ⚠️ · 5 ❌; run 2: 1 ✅ · 3 ⚠️ · 5 ❌)

| Block | Text | Run 1 | Run 2 | R1 | R2 | Reason | Owner |
|---|---|---|---|---|---|---|---|
| B-000023 |   \| Paragraph \| Block, kind `paragraph` \| | `L1` · `term:paragraph` · Paragraph \| MUST \| be a Block with kind `paragraph` | — | ✅ | ❌ | A row of F1's segmentation table (paragraph → block of kind `paragraph`). Run 1 is right; `L4`/`L5` would fit better than `L1`. Run 2 **failed** on a paraphrased quote. | |
| B-000026 |   \| Content inside a blockquote \| Keeps its own kind, with `in_blockquote: true` \| | `L1` · `term:content` · Content \| MUST \| keep its own kind with `in_blockquote: true` | `L1` · `term:content` · Content \| MUST \| keep its own kind, with `in_blockquote: true` | ✅ | ✅ | Both identical and right: content in a blockquote keeps its kind, with `in_blockquote: true`. | |
| B-000106 | \| AC-1.24 *(partial: raised by `load_profile`)* \| `tests/test_profile.py::test_ac_1_24_missing_store_is_a_store_error` \| `src/s | `V` · `None` · AC-1.24 (partial: raised by `load_profile`) \| None \| is verified by test `test_ac_1_24_missing_store_is_a_st · _referential, unresolved_term_ | `V` · `None` · AC-1.24 \| None \| verified by `tests/test_profile.py::test_ac_1_24_missin · _referential, unresolved_term_ | ❌ | ❌ | A traceability row (criterion → test → code). Both made a `V` node with no family: bookkeeping about the specs, not a claim in them (G-8). | |
| B-000107 | \| AC-1.8, AC-1.31, AC-1.21 … AC-1.26 \| `tests/test_ingest_pipeline.py` (14) \| `src/sdd_compiler/ingest/pipeline.py` · `commands | `V` · `term:pending_status` · AC-1.8, AC-1.31, AC-1.21 through AC-1.26 \| None \| are verified by 14 tests in `tests/test_ingest_pipeline | `None` · `None` · Requirements AC-1.8, AC-1.31, AC-1.21 through AC-1.26 \| None \| are traceable to test and implementation files · _referential, missing_modality, unplaceable, unresolved_term_<br>`V` · `term:block` · tests and implementation files \| None \| `tests/test_ingest_pipeline.py` (14) verifies AC-1.8, A · _scope_<br>`L1` · `None` · Ingest pipeline implementation \| None \| is composed of pipeline.py, commands.py, and cli.py · _unresolved_term_ | ❌ | ❌ | A traceability row. Run 1 made one `V` node in the wrong family (`pending_status`); run 2 made **three** nodes of it (G-8). | |
| B-000156 | \| `conflict` \| `conflict_ids` is non-empty \| | — | `L4` · `term:status` · node status \| None \| becomes conflict · _missing_modality_ | ❌ | ⚠️ | A row of the status table (`conflict` holds when `conflict_ids` is non-empty). Run 1 **failed** on a paraphrased quote. Run 2 formed "node status becomes conflict" but lost the condition from the response. | |
| B-000167 | \| Conflict \| `CF-000001` \| Assigned once \| | `L1` · `term:conflict` · Conflict id \| MUST \| follow format `CF-000001` and be assigned once | `L4` · `term:conflict_id` · conflict ID \| None \| is assigned once · _missing_modality_ | ✅ | ⚠️ | A row of the id table (conflict ids `CF-000001`, assigned once). Run 1 captured both parts; run 2 dropped the format. | |
| B-000249 | \| AC-2.24, AC-2.25 · D13 \| `tests/test_atomize_pipeline.py` \| `src/sdd_compiler/atomize/forming.py` · `pipeline.py` \| | `V` · `None` · AC-2.24, AC-2.25 · D13 \| None \| verified by tests/test_atomize_pipeline.py and src/sdd_ · _referential, unresolved_term_ | `V` · `None` · AC-2.24, AC-2.25 · D13 \| None \| verified by `tests/test_atomize_pipeline.py` and `src/s · _referential, unresolved_term_ | ❌ | ❌ | A traceability row. Both made a `V` node with no family (G-8). | |
| B-000551 | \| **S2 shared subject term** \| Shares a term of kind `entity`, `data` or `event` \| the term ids \| | `L4` · `None` · S2 shared subject term \| None \| Shares a term of kind `entity`, `data` or `event` · _missing_actor, scope, missing_modality, unresolved_term_<br>`L4` · `None` · candidate source S2 \| MUST \| be retrieved and identified by term ids · _referential, unresolved_term_ | — | ❌ | ❌ | A row of F5's source table (S2 shared subject term: rule and evidence). Run 1 made two nodes without families, and the second **reinterprets** the evidence column as "MUST be retrieved and identified by term ids". Run 2 **failed** on an elided quote. | |
| B-000694 | \| `F<n>_<slug>/spec.md` \| One feature = one spec \| | `C` · `(global)` · one feature \| MUST \| map to one spec · _referential_ | — | ✅ | ⚠️ | A convention row (`F<n>_<slug>/spec.md` = one feature per spec). Run 1's "one feature MUST map to one spec" at `C (global)` is right. Run 2 formed no node: a missed rule. | |

