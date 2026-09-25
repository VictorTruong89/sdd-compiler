# 8. Where the graph lives, and how to look at it

## The store: `.sdd/`

Everything the compiler knows is plain text in one folder, next to the specs. There is no database:
JSON Lines files, one record per line, with a fixed key order and sorted, so two builds from the same
input are byte-identical and a `git diff` of the store is readable.

```text
.sdd/
├── profile.yaml            ← the only file you edit
├── sources.jsonl           one line per spec file: path and hash
├── blocks.jsonl            every block (chapter 4), including removed ones
├── runs.jsonl              one line per run: command, files, counts
├── terms.jsonl             the term registry (chapter 5)
├── nodes/<family>.jsonl    nodes, one file ("shard") per family
│   ├── _global.jsonl       constraints scoped to no single family
│   └── _unplaced.jsonl     nodes with no family
├── edges/<family>.jsonl    links, stored with their families
├── conflicts.jsonl         every conflict record, open and resolved
├── conflicted_nodes.json   derived: the nodes currently in a conflict
├── review.jsonl            attention items for a person (failed blocks, term merges, inferred facts)
├── adjudications.jsonl     human verdicts on conflicts (created by `conflicts judge`)
├── graph.meta.json         schema versions, counts, id counters
├── lock/                   the judgment lock: q-atom, q-desc, q-term, q-pair .jsonl
├── views/                  GENERATED Markdown — never edit
│   ├── map.md
│   ├── conflicts.md
│   └── families/<family>.md
└── run.lock                present only while a compile is writing
```

**Writing is all or nothing.** Every compile derives what is derived (status, conflict fields, the
registry, counts), validates every record against its schema, runs the store's consistency checks
(unique ids, links resolve, status derived, conflict membership, registry derived, shard placement,
judgment references, counters monotonic), stages every file, then renames them together. A violation
aborts with exit `4`, names every problem, and leaves the old store untouched.

## Where the R18 graph is

| What | Where |
|---|---|
| **The full store** (950 nodes, 381 conflicts) | **`~/sddc-runs/full-corpus/.sdd/`**, and a copy of the whole run directory in the repository at **`build/full-corpus/`** |
| The spec text it was compiled from, frozen | `~/sddc-runs/full-corpus/sdd/specs/` and its hashes in `corpus.sha256` |
| Backups taken before the I-85 repair and the I-89 heal | `~/sddc-runs/full-corpus/.sdd.bak-before-I85-reset/`, `.sdd.bak-before-I89-heal/` |
| **An interactive explorer** of this store | `~/sddc-runs/full-corpus/graph.html` (section 5 below) |
| Per-round output, the report, the conflict list, the M2 sample | `sdd/design/rel01_design/measurements/R18_*` — in the repository |
| The write-up | `sdd/design/rel01_design/M4-gate.md` §8 |

Point any command at it with `--root`:

```bash
sddc --root ~/sddc-runs/full-corpus status
sddc --root ~/sddc-runs/full-corpus family "model call"
```

*Fixed 2026-09-24 (build-plan I-89):* judged links used to be stored again each time their verdict
was replayed — R18 held 9 682 link lines for 4 199 distinct links. The store has been healed and a
duplicate link key now fails the store checks. ⚠ Still open (I-91): when a re-judged pair's verdict
changes, its old judged link stays beside the new one.

## How a person should look at it — from the top down

A graph of 950 nodes and 4 199 links drawn all at once is a hairball; nobody learns anything from it.
Read it the way you read an atlas: the world map first, then one country, then one street.

### 1. The map — `.sdd/views/map.md`

Families as rows, layers as columns. Each cell is `count mark`, where the mark is the **worst status**
among those nodes: `✗` conflict · `?` ambiguous · `~` stale · `·` unchecked · `✓` validated. Rows are
sorted by open conflicts, most first. From R18:

```text
| family          | L0 | L1  | L2   | L3  | L4   | L5  | C   | V    | —   |
| node            |    | 5 ✗ | 11 ✗ | 1 ✓ | 21 ✗ | 8 ✗ | 9 ✗ | 20 ✗ | 1 ? |
| block           |    | 5 ✗ | 4 ✗  |     | 14 ✗ | 4 ✗ | 8 ✗ | 11 ✗ |     |
| conflict_record |    | 2 ✗ | 4 ✗  |     | 3 ✗  | 1 ? | 1 ? | 6 ✗  |     |
```

Read it as: "the `node` family has 76 claims spread over every layer, and conflicts in most of them".

### 2. A family card — `.sdd/views/families/<name>.md` or `sddc family NAME`

One family's nodes grouped by layer, each line linked to the exact source line; then **"In scope from
elsewhere"** (constraints that cover this family) and **"Related families"**. R18's `model_call`:

```text
## Family: model_call
**Also called:** call
### L2 (1)
- N-000766 ✗ Model calls go through one interface with two backends
### L5 (1)
- N-000008 ✗ F1 makes no model calls
### C (2)
- N-000233 ✗ Every call records: backend, model as reported, CLI version, …
- N-000565 ✗ Ask the model one question about one pair at a time, …
### V (1)
- AC-3.19 ✗ Given a completed compile, when compile runs again with no source change …
### In scope from elsewhere (10)
…
**Related families:** backend, cli_version, link, pair_key, spec_set, status
```

The links open the spec at the line in any Markdown viewer that follows relative links (VS Code,
GitHub).

### 3. The conflicts — `.sdd/views/conflicts.md` or `sddc conflicts`

Records grouped by shared members (R18: 95 groups), contradictions first, each with both files and
lines and the judge's rationale. This is the work list.

### 4. A diagram of one family — `scripts/family_mermaid.py`

For a picture of how one family's claims relate, export it as a Mermaid diagram (any viewer that
renders Mermaid — GitHub, VS Code with a Mermaid extension — draws it):

```bash
cd ~/sddc-runs/full-corpus
PYTHONPATH=/path/to/sdd-compiler/src \
  python /path/to/sdd-compiler/docs/lectures/sdd-compiler-as-built/scripts/family_mermaid.py .sdd model_call > model_call.mmd
```

What it produced on R18 (abridged):

```mermaid
graph LR
  N_000008["N-000008 [L5]<br/>F1 makes no model calls"]
  N_000233["N-000233 [C]<br/>Every call records: backend, model as "]
  N_000766["N-000766 [L2]<br/>Model calls go through one interface w"]
  N_000220["N-000220 [L2]<br/>Model interface with two backends."]
  N_000767["N-000767 [L4]<br/>headless Claude Code (default) and the A"]
  AC_3_19["AC-3.19 [V]<br/>Given a completed compile, when co"]
  AC_3_19 -- refines --> N_000008
  N_000008 -. contradicts .-> N_000233
  N_000008 -. contradicts .-> N_000766
  N_000220 -. duplicates .-> N_000766
  N_000767 -- depends on --> N_000766
  style N_000008 stroke:#c00,stroke-width:2px
```

Dotted arrows are conflicts; solid arrows are ordinary relations. The script draws the family's nodes
plus every node one judged link away.

### 5. The interactive explorer — `scripts/build_viewer.py`

For browsing the whole graph, build a single self-contained HTML page from any store:

```bash
cd ~/sddc-runs/full-corpus
PYTHONPATH=/path/to/sdd-compiler/src \
  python /path/to/sdd-compiler/docs/lectures/sdd-compiler-as-built/scripts/build_viewer.py \
  .sdd graph.html --label "R18 · sdd/specs · 2026-09-23"
xdg-open graph.html        # or open it in any browser; it needs no server
```

It reads the store with the compiler's own loader and fills `viewer_template.html`. You get:

- **Families** on the left, sorted by open conflicts, by size, or A–Z, with a filter that matches
  aliases too;
- **Graph**: the selected family's nodes, drawn with their layer inside each circle and their status
  as its ring (✗ red conflict, ? amber ambiguous, ✓ green validated), plus nodes one judged relation
  outside the family. Contradictions are dashed red. Each relation type can be switched off. Drag to
  move, scroll to zoom, hover for the text;
- **Map**: families × layers, each cell showing the count and the worst status. Click a row to open it;
- **Conflicts**: all 381, filtered by kind or by the current family. Click a member to open it;
- **Details**: the full node record (text, `file:line` with a copy button, canonical form, family and
  the rule that chose it, terms, ambiguity, conflicts with rationale, every relation);
- **Find**: any node by id or words. `graph.html#N-000008` opens straight on a node.

The R18 build is at `~/sddc-runs/full-corpus/graph.html` (≈ 1.1 MB).

### 6. Ask questions of the files directly

The store is JSON Lines, so any tool reads it. Two useful one-liners:

```bash
# every open contradiction, one line each
jq -r 'select(.state=="open" and .kind=="contradiction") | "\(.id)  \(.members|join(" vs "))"' .sdd/conflicts.jsonl

# how many nodes per layer
cat .sdd/nodes/*.jsonl | jq -r '.layer // "none"' | sort | uniq -c | sort -rn
```

Or load it in Python with the compiler's own reader, which also runs the checks:
`from sdd_compiler.store.graph import load_graph; g = load_graph(Path(".sdd"))`.

## What not to do

- **Do not edit anything in `.sdd/` except `profile.yaml`.** The next compile would either overwrite
  it or refuse to write (exit `4`). To change the graph, change the spec text and compile.
- **Do not trust a view you did not regenerate.** Views are rewritten by every compile; a copy pasted
  elsewhere goes stale.
