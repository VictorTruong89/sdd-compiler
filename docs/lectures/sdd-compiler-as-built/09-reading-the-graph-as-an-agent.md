# 9. Handing the graph to an AI agent

## What exists today

The graph was built so that a coding agent could build from the spec set with more help than a folder
of documents gives. The built hand-off is **`sddc export`** (spec F7, approved 2026-09-30, amended in
rel02 by D15–D17). It writes, from a compiled store, with **no model call**:

```text
.sdd/export/                       (or --out DIR)
  MAP.md                           the entry point: read first, build order, contracts, decisions, how to use
  CHECKLIST.md                     every claim id, once, grouped by pack
  export.meta.json                 counts, exclusions, backward needs, sizes, store hash
  packs/00-foundation.md           vision.md + constitution.md (export.foundation_globs), if present
  packs/NN-<spec>--<section>.md    one per unit of the specs, in build order
```

F7 §1 states the promise: **everything the Markdown gave, plus four things the Markdown cannot** — a
map, a build order, a checklist of ids, and conflicts settled before reading. The `.sdd/` store itself
is not a reading format: on R18 it was ≈ 21.6× the Markdown's bytes, with 375 family files, 246 of them
holding one node (F7 §1).

A `query` command — "what must I read to change X?" — is still specified, not built (F4 AC-4.9 …
4.13). For that question there is the by-hand recipe at the end of this chapter.

*Layman:* the library now hands the builder a bound copy of every notebook, cut into chapters in the
order the work needs them, each chapter's disputed instructions marked, and a tick-list at the back.

## The recipe for a person

```bash
sddc compile                       # until pending is 0 (chapter 2)
sddc conflicts                     # read the open contradictions
sddc conflicts judge CF-… --verdict real  --note "<which side holds, in your words>"
sddc conflicts judge CF-… --verdict false --note "<why it is not a conflict>"
sddc export                        # exit 0 → .sdd/export/
```

Then hand the agent the export folder and one line. The rel02 trials used exactly this instruction
line, the only line that differs from the Markdown arm's task text:

> The specification is the compiled export in `spec/`. Start with `spec/MAP.md`; account for every id
> in `spec/CHECKLIST.md`.

### What stops the export (F7 §4.2), in order

1. The store fails its checks → exit 4.
2. A spec file changed, appeared or disappeared since the last compile → exit 2, `run sddc compile
   first`. An export of a stale graph would look authoritative.
3. **The conflict gate:** an open contradiction has no current human verdict → exit 3, listing them
   (the first 20, then a count). `--allow-open` writes the export anyway and marks them.

Pending blocks do not stop it: their text is still printed, tagged `no node (pending)`, and `MAP.md`
opens with a count.

## What is in a pack

**Units.** A unit is one spec file's text under one second-level heading: `(source,
heading_path[:2])`. A unit whose block text passes 20 000 characters splits one heading level deeper
(F7 D16; below Claude Code's ≈ 30 000-character inline read). Units come from **headings, not
families**, so term proliferation (chapter 5) cannot scatter one section across files.

**Order.** Spec files are ordered to minimise `depends_on` links that point to a later file; sections
keep their order inside a file. Links that still point forward are listed in `MAP.md` under *Needs
against the order*, never an error.

**Sections of every pack**, always in this order (an empty one prints `None.`):

| Section | Holds |
|---|---|
| header | Source and heading; counts of blocks, nodes by kind, AC labels |
| `## Text` | **The unit's spec text, verbatim**, in source order, headings re-emitted. After each block, one `↳` line with its node ids (`↳ N-000866–N-000869`), or `↳ no node` |
| `## Claims to implement` | Each requirement, constraint, decision, assumption as `[id] kind · modality · layer`, plus `· needs <ids> (pack NN)` — **ids only, no text** (F7 D15): the text is in Text. An example node is `[id] example of <ids>` (D17). A contract points at its fence |
| `## Acceptance criteria` | Each `V` node (not examples) with its text, what it verifies, and a test name `test_AC_4_7_…` |
| `## Constraints in scope` | `C` nodes homed elsewhere whose scope covers a node here, with their text; broad ones once, in pack 00 |
| `## Related elsewhere` | `refines`/`subsumes` links to other packs as ids; `same as` / `covered by` with the other text |
| `## Conflicts` | `Settled:` (a `real` verdict: both quotes, the rationale, your note) or, under `--allow-open`, `UNSETTLED:` |
| `## Terms` | Terms used here that have aliases or a definition, the definition verbatim |

Nothing in a pack is written by a model: it is verbatim text, ids, labels, counts, headings, term
names, the author's own definitions, recorded rationales and your adjudication notes, or fixed words
(F7 §4.1 rule 2). Model-derived labels (layer, modality, kind) are named *derived* in `MAP.md`, and
"the verbatim text of a block wins over them". Before writing anything the export checks that **every
live block's text occurs verbatim in its home pack**; a miss is exit 4, nothing written (F7 §4.9).

### A real pack (R21 store, current code, exported 2026-11-08 with `--allow-open`)

```markdown
# Pack 30 — sdd/specs/Interface_Contract.md · Interface Contract › `tool_name`
blocks 3 · nodes 6 (constraint 2, requirement 4) · AC labels: none

## Text
# Interface Contract

## `tool_name`

Request field on the post-tool-use hook (`prosecheck-guard.js`). Host JSON on standard input names
the file-edit tool as `tool_name`. When the host supplies a session, the same object names it as
`session_id`.
↳ N-000864, N-000865

### Signature

    { "tool_name": "Write", "tool_input": { ... }, "session_id": string, "cwd": string }
↳ no node

`tool_name` is a string at the top level of that object, beside `tool_input`, `session_id`, and
`cwd`. … The ledger written for that attempt is the one `/prosecheck show` reads when the same
`session_id` is supplied beside `prompt`.
↳ N-000866–N-000869

## Claims to implement
- [N-000864] requirement · MUST · L3
- [N-000865] requirement · MUST · L3
- [N-000866] constraint · MUST · L3
…

## Acceptance criteria
None.

## Constraints in scope
plus the broad constraints in pack 01

## Related elsewhere
- N-000865 same as N-000848 (pack 28) When the host supplies a session, the same object names it as `session_id`.
- N-000869 refines N-000518 (pack 15)
…

## Conflicts
None.

## Terms
- session — defined: "The session is the `session_id` on the same prompt-submit object."
```

(Abridged here: the six-line fence is shown on one indented line, one paragraph is shortened, and some
list lines are cut; the real file prints them all verbatim, the fence included.) Two things to notice. The fence has no language, so it is not a contract and
formed no node — but its text is still in the pack, because the pack is the spec. And "beside the
claims" is literal: an agent reads the sentence, then the ids it carries.

An unsettled contradiction, from pack 12 of the same export:

```text
- UNSETTLED: CF-000080 — N-000037 "Every no-break space becomes an ordinary space." vs N-000307 "except a
  no-break space (U+00A0) or narrow no-break space (U+202F) that holds something together"
  rationale: A says every no-break space becomes an ordinary space, while B says a no-break space that
  holds digits or punctuation together must not become U+0020; … (low confidence, since B may be read
  as a clarification of what is normalized).
```

Its counts (`export.meta.json`): 40 packs, 450 blocks of which 73 formed no node, 1 126 nodes and
checklist items, 67 unsettled contradictions, no foundation (case016 has no `vision.md`), 14 backward
needs, 354 686 characters against 118 277 in the Markdown — **3.0×**. The pilot graph's frozen export
(`~/sddc-runs/pilot-export-R000023/`) is 2.94× (473 150 against 160 721), with 59 packs and 0
unsettled contradictions. The first export of that graph, before its lists were cut, was 4.57×
(build-plan I-95).

### `MAP.md` and `CHECKLIST.md`

`MAP.md` opens with banners (unsettled contradictions, pending blocks, no foundation), then *Read
first*, a table of *Units in build order* (pack, file, source and heading, blocks, claims by kind, AC
count, the packs it needs, its size in words), *Needs against the order*, *Contracts*, *Decisions*,
the fixed *How to use* text, and *Counts*. `CHECKLIST.md` lists every live node once under its home
pack as `- [ ] N-000412` (and its label when it has one): "Every id below must end implemented,
tested, or listed as not done with a reason." Every kind is listed, not only MUST claims (F7 D8).

## What the trials found

rel02 hands the export (or the plain Markdown) to Claude Code with Sonnet or Haiku in a sandbox and
scores the code with hidden tests (interim report §3). Two kinds of export are used: the **compiler
export** (what `sddc export --allow-open` writes) and an **oracle export** made by the harness, which
injects every planted conflict as flagged. The oracle is not a compiler feature; it measures what an
agent does with flags when none are missing.

| Finding | Evidence |
|---|---|
| **Flagged conflicts get named.** Round 18 (24 planted, oracle export): both models named all 24 in every export run (144 of 144), against 36.1 % (Haiku) and 73.6 % (Sonnet) of the 24 from the Markdown | interim report §4.6 |
| **The compiler export helps exactly where it flags.** Round 21: on the 10 conflicts the compiler flagged, naming rose 70 → 87 % (Sonnet) and 72 → 100 % (Haiku); on the 6 only the oracle flagged, no better than the Markdown | interim report §4.9 |
| **No measured gain in code quality.** Core tests from the oracle export against the Markdown: Sonnet −0.2, −0.2, −0.4 points (rounds 18, 19, 21); Haiku +4.2, +2.1, +4.1, permutation p = 0.060 over the three rounds — not significant | interim report §4.9 |
| **No effect on silent invention.** Where a fact was removed, agents filled the gap without saying so from either format | interim report §4.8, §4.9 |
| **It costs more to read.** Round 18, per run, building from the export instead of the Markdown: Sonnet +$0.10 (+4.7 %), Haiku +$0.76 (×2.66), almost all of it context re-sent over more turns | methodology notes §6.1 |

So, as built and as measured so far: the export is a reliable way to make an agent **surface** the
contradictions the compiler found. It does not make the code better, and it does not stop an agent
inventing what the spec left out.

## Reading the store by hand: one family's context pack

For a single change ("add a retry when the model call times out"), a whole export is more than you
need. The store is plain JSON Lines and the compiler's loader and indexes are importable, so the older
recipe — from the traversal design note (`sdd/archive/rel-01/design/rel01_design/G3-3-traversal.md`) —
still works, with a helper script, `scripts/context_pack.py`.

### Step 1 — find the target family

```python
# PYTHONPATH=<repo>/src ; run in the directory holding .sdd/
from collections import Counter
from pathlib import Path
from sdd_compiler.store.graph import load_graph
from sdd_compiler.store.index import GraphIndex
from sdd_compiler.atomize.terms import normalize_name

g = load_graph(Path(".sdd")); ix = GraphIndex.build(g)
task = "add a retry when the model call times out"
print(ix.names.get("model call"))                      # by name  → term:model_call
hits = Counter(g.nodes[n]["family"] for w in normalize_name(task).split()
               for n in ix.by_keyword.get(w, []))
print(hits.most_common(3))                              # by keyword
```

On R18 this prints `term:model_call`, then `[('term:model_call', 7), ('term:node', 6), ('term:block',
6)]` (re-run with the current code on 2026-11-08: the same). A task that points at a spec section can
go by place instead: `file:line` to nodes, chapter 7.

### Step 2 — gather the pack, in tiers

| Tier | Take | Why |
|---|---|---|
| 1 core | Every node in the family, ordered L0 → L5, C, V | What the code must do |
| 2 constraints | `C` nodes elsewhere whose scope **covers** a core node (`model/scope.py::covers`) | Rules the code must not break |
| 3 verification | `V` nodes whose `verifies` names a core node | How the change will be tested |
| 4 conflicts | Open conflict records with a core node as member | What is **not** settled |

```bash
PYTHONPATH=/path/to/sdd-compiler/src \
  python /path/to/sdd-compiler/docs/lectures/sdd-compiler-as-built/scripts/context_pack.py .sdd "model call"
```

Its output on R18 (abridged):

```text
# context pack: term:model_call

## core (5)
✗ N-000766   L2  sdd/specs/constitution.md:70  'Model calls go through **one interface with two backends'
✗ N-000008   L5  sdd/specs/F1_ingest/spec.md:28  'F1 makes **no model calls'
✗ N-000233   C   sdd/specs/F3_atomizer/spec.md:72  'Every call records:** backend, model as reported, …'
…
## constraints in scope (10)
✗ N-000521   C   sdd/specs/F5_retrieval/spec.md:135  'F5 makes no model calls at all.'
…
## open conflicts touching it (6)
CF-000043 contradiction: N-000008 vs N-000233 — A states F1 makes no model calls, while B requires …
```

An unknown family name fails loudly and suggests close ones. On the R21 store, `context_pack.py .sdd
"file path"` lists 29 core nodes (re-run 2026-11-08).

### Step 3 — read the marks before the text

| Mark | Status | The agent should |
|---|---|---|
| `✗` | conflict | **Not** pick a side silently. Name the conflict (`CF-…`) and ask, or implement only what both sides allow |
| `?` | ambiguous | Read the ambiguity kind; ask, or state the assumption it makes |
| `~` / `·` | stale / unchecked | The graph is behind the text — recompile first |
| `✓` | validated | Use as written |

### Step 4 — read the source, not only the node

A node's `text` is its quoted words and its `canonical` form is the model's rewrite; both are for
**finding**. For **implementing**, open `source.file` at `source.lines`. The export does this for you:
its packs are the source text.

### Step 5 — leave a trail, and say what you left out

Mark code with `# spec: <id>` and name tests after AC ids (the export's *How to use* says the same).
End with a manifest: families read, conflicts left open, assumptions made.

⚠ **The limit of the by-hand pack:** it is only as good as the graph's naming. A claim filed under a
synonym lands in another family and the pack misses it. The export does not have this limit, because
it is cut by headings — another reason to prefer it when building, not just changing, code.
