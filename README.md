# SDD Compiler

> **Status:** rel01 in progress (opened 2026-09-14, target 2026-09-30). All four milestones are
> built (635 tests); the first full compile of this repository's own specs (R18) is done.

A compiler for specifications. It turns a folder of Markdown spec files into a **spec graph**: every
atomic claim as a node, classified by layer and family, linked to the claims it relates to, with every
contradiction, duplication and overlap reported as a conflict record.

**rel01 in one sentence:** point `sddc compile` at a folder of static Markdown specs and get back a
spec graph plus a report of every conflict in it. **The rel01 use case for the graph is generating a
whole codebase from scratch** from that graph. Adding code to an existing codebase is out of scope
for now.

A beginner's guide to how it works, written from the as-built code, is in
[`docs/lectures/sdd-compiler-as-built/`](docs/lectures/sdd-compiler-as-built/README.md).

---

## 1. For people: generate a spec graph and look at it

### Install

Python ≥ 3.11 and [Claude Code](https://claude.com/claude-code), installed and logged in. Every model
question runs through headless Claude Code on your subscription; no API key is needed.

```bash
pip install -e .              # gives you the `sddc` command
```

### Compile

```bash
cd <your project>             # specs under sdd/specs/ by default (see .sdd/profile.yaml)
sddc init                     # creates .sdd/ and a default profile
sddc compile                  # ingest → atomize → check → write; prints the conflict report
```

Read the exit code as a state:

| Exit | Meaning | Do |
|---|---|---|
| `0` / `3` | Finished; `3` means conflicts are open | Read the report |
| `5` | The per-run call cap stopped it; finished work is saved | Run `sddc compile` again |
| `6` | The subscription's session limit (or another backend stop) | Wait for the reset it names, run again |
| `1` / `2` / `4` | Usage, input, or store error | Read the message; it names the problem |

A large spec set takes several runs. R18 needed 16 runs over about 9 hours of compile time for 845
blocks. Each run resumes where the last stopped, and answers already paid for replay free from
`.sdd/lock/`.

### Look at it

| To see | Use |
|---|---|
| Counts and what is pending | `sddc status` |
| All open conflicts, grouped | `sddc conflicts` · `.sdd/views/conflicts.md` |
| Families × layers at a glance | `.sdd/views/map.md` |
| One family's claims by layer | `sddc family "share link"` · `.sdd/views/families/<name>.md` |
| **The whole graph, interactively** | `graph.html` — build it as below |

**The interactive explorer** is a single HTML file that needs no server:

```bash
PYTHONPATH=src python docs/lectures/sdd-compiler-as-built/scripts/build_viewer.py \
    <path/to/.sdd> graph.html --label "my specs · 2026-09-24"
xdg-open graph.html           # or open it in any browser
```

- **Families** (left): sorted by open conflicts, by size or A–Z. The filter also matches alternative
  names (aliases).
- **Graph**: the selected family's claims. The text inside each circle is its layer (L1 behaviour, L4
  data, C constraint, V verification …). Its ring is its status: ✗ red conflict, ? amber ambiguous, ✓
  green validated. Claims one relation outside the family are drawn smaller. Contradictions are
  dashed red, and each relation type can be switched off. Drag to move, scroll to zoom, hover for the
  text.
- **Map**: families × layers; each cell shows the count and the worst status. Click a row to open it.
- **Conflicts**: every open conflict, filtered by kind or by the current family.
- **Details**: the full record of a claim: its text, `file:line` with a copy button, canonical form,
  family and the rule that chose it, terms, ambiguity, conflicts with the judge's rationale, and
  every relation.
- **Find**: any claim by id or words. `graph.html#N-000008` opens straight on a claim.

**The R18 graph of this repository's own specs** is in `build/full-corpus/`: open
`build/full-corpus/graph.html` directly, or run `sddc --root build/full-corpus status`.

### Record what you think of a conflict

```bash
sddc conflicts judge CF-000043 --verdict false --note "different components, no conflict"
```

Verdicts go to `.sdd/adjudications.jsonl`, and that is where precision is counted from. On this
repository's specs most reported conflicts have been false alarms (about 1 in 10 real on an earlier
sample), so treat each one as a question, not a finding.

---

## 2. For AI agents: generate code from a compiled spec graph

This section is generic: it applies to any spec set compiled by `sddc`, fed to any LLM coding agent.
The rel01 use case is **a new codebase from scratch**.

### What the agent reads

A compiled build directory (for example `build/full-corpus/`) holds the spec text and its graph:

| Path | What it is | Use it to |
|---|---|---|
| `sdd/specs/**/*.md` | **The specifications — the source of truth** | Read `vision.md` and `constitution.md` in full first (purpose, stack, non-negotiable rules), then each feature spec |
| `.sdd/nodes/*.jsonl` | Every atomic claim, one JSON record per line, one file per family | Your checklist: every non-`V` node must be satisfied by code, every `V` node by a test |
| `.sdd/terms.jsonl` | The vocabulary: canonical names, aliases, `broader` (kind-of) | Name modules, classes and fields consistently; treat an alias as the same thing |
| `.sdd/edges/*.jsonl` | Links: `depends_on`, `refines`, `subsumes`, `duplicates`, `conflicts_with` (judged), `verifies` (code) | Build order (`depends_on`), which test covers which rule (`verifies`) |
| `.sdd/conflicts.jsonl` | Open contradictions, duplications and subsumptions, with rationale and quotes | Questions to settle before implementing either side |
| `.sdd/graph.meta.json` | Counts and versions | Check you loaded everything (the node count must match) |
| `.sdd/blocks.jsonl` | Every source paragraph with file, lines and text | Find the exact source of a claim; find **pending** blocks (below) |
| `.sdd/review.jsonl` | Attention items; an **open** `atomize_failed` item = a paragraph that is in **no** node | Read those paragraphs straight from the spec. They are requirements the graph missed |
| `.sdd/adjudications.jsonl` *(if present)* | Human verdicts on conflicts | A conflict judged `false` is settled: ignore it |

**The fields of a node that matter for code:**

- `layer` says what to build. `L0` intent tells you why; `L1` behaviour becomes a feature seen from
  outside; `L2` structure becomes a component or module; `L3` contract becomes an interface, CLI or
  file format; `L4` data becomes a schema or type; `L5` logic becomes an algorithm; `C` becomes a
  cross-cutting rule to enforce; `V` becomes a test.
- `family` is the thing the claim is about. Group your design by family.
- `canonical` gives state / trigger / scope / subject / **modality** / response. `MUST` and
  `MUST NOT` are hard; `SHOULD` and `MAY` are softer.
- `text` + `source.file` + `source.lines` are the claim's own words and where they are. Read the
  source line, not only the node.
- `status`: `conflict` means unsettled, `ambiguous` means vague (see `ambiguity`), `validated` means
  clean.
- `label` (`AC-1.4`, `CT-2.1`) is the spec's own id for an acceptance criterion or contract. Use it
  in test names.
- `flags` containing `inferred` means the description holds something the source does not say. Trust
  the source.

### What the agent ignores (for people only)

| Path | Why ignore it |
|---|---|
| `graph.html`, `.sdd/views/` | Human visualizations of the same data |
| `.sdd/lock/` | Raw model answers and their cost: provenance, not requirements |
| `.sdd/runs.jsonl`, `.sdd/profile.yaml`, `.sdd/conflicted_nodes.json`, `.sdd/sources.jsonl` | Compiler bookkeeping, or derived from files above |
| `.sdd.bak-*/` | Backups taken during repairs |
| `round-*`, `driver.*`, `summary.py`, `ingest.json`, `corpus.sha256` | Logs and scripts of the compile runs (`corpus.sha256` only proves which spec text was compiled) |
| `sdd/specs/_templates/`, `sdd/specs/README.md` | A blank template and an index |

### The procedure

1. **Read the foundation.** `vision.md` and `constitution.md` in full. The constitution fixes the
   stack and the rules every file must follow.
2. **Load the graph.** All nodes, terms, links and open conflicts. Confirm the node count against
   `graph.meta.json`.
3. **Collect what the graph missed.** Every open `atomize_failed` item in `review.jsonl` names a source
   paragraph with no node. Read it from the spec and add it to your checklist by hand.
4. **Design from the layers.** `L2` gives the components, `L3` the interfaces, `L4` the data, `L1`
   the features, `L5` the algorithms, `C` the rules that cut across all of them. Name things with
   the canonical term names.
5. **Settle conflicts you touch, never silently.** For each open conflict involving a node you
   implement, read both source lines. If they only look contradictory (different situations,
   different components), note it and continue. If they are really contradictory, choose, and write
   the choice and its reason in `OPEN_QUESTIONS.md`. Do the same for every `ambiguous` node: state
   the assumption you made.
6. **Implement test-first.** Each `V` node becomes a test named after its `label` (or its id). Write
   the test, then the code that passes it.
7. **Leave a trail.** Put `# spec: <node id>` beside the code that satisfies a node. Write
   `TRACEABILITY.md`: every non-`V` node → the code that satisfies it, every `V` node → its test, and
   a list of the nodes you did **not** implement, with the reason.

### A prompt to hand an agent

Replace `<BUILD>` with the build directory (for this repository's own specs: `build/full-corpus`)
and `<OUT>` with an empty directory for the new code.

```text
You are generating a complete codebase from scratch, from a compiled spec graph.

Inputs (read only these):
  <BUILD>/sdd/specs/**/*.md      the specifications — the source of truth
  <BUILD>/.sdd/nodes/*.jsonl     every atomic claim (one JSON per line)
  <BUILD>/.sdd/terms.jsonl       vocabulary: canonical names and aliases
  <BUILD>/.sdd/edges/*.jsonl     relations between claims
  <BUILD>/.sdd/conflicts.jsonl   open conflicts between claims
  <BUILD>/.sdd/review.jsonl      atomize_failed items = paragraphs with no node
  <BUILD>/.sdd/graph.meta.json   counts, to check you loaded everything
Ignore graph.html, .sdd/views/, .sdd/lock/, .sdd.bak-*/, round-*, driver.*, and anything else
in <BUILD>. Do not read any existing implementation of these specs; write everything in <OUT>.

Steps:
1. Read vision.md and constitution.md in full; follow the constitution's stack and rules.
2. Load all nodes; confirm their count matches graph.meta.json. Read the source paragraph of
   every open atomize_failed item and treat it as a requirement too.
3. Plan components from L2 nodes, interfaces from L3, data from L4, features from L1,
   algorithms from L5; enforce every C node everywhere its scope covers. Use term names.
4. Before implementing a node with status "conflict", read both source lines of each conflict
   it is in. Only an apparent contradiction: note it and go on. A real one: choose, and record
   the choice and reason in OPEN_QUESTIONS.md. Do the same for "ambiguous" nodes (state the
   assumption).
5. Test-first: each V node becomes a test named after its label (e.g. test_AC_1_4_...).
6. Mark code with "# spec: <node id>". Write TRACEABILITY.md mapping every node to code or test,
   and list every node not implemented, with the reason.
Finish with: the test suite passing, TRACEABILITY.md, OPEN_QUESTIONS.md.
```

---

## Repository map

| Path | What |
|---|---|
| `CLAUDE.md` | Working agreement for AI agents working **on** the compiler |
| `sdd/specs/` | The compiler's own specs (vision, constitution, F1–F6) — [map](sdd/README.md) |
| `sdd/design/` | Release design, gates, measurements, the build plan and issue log |
| `src/sdd_compiler/` · `tests/` | The Python CLI and its tests |
| `docs/lectures/` | Lectures explaining the design, including the as-built beginner's guide |
| `build/full-corpus/` | The R18 compile of this repository's own `sdd/specs/`: spec copy, graph, explorer |
| `sdd/archive/` | Superseded documents and pre-rel01 brainstorm exports |
