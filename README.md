# SDD Compiler

> **Status:** rel01 **closed 2026-10-01** ([close-out](sdd/design/releases/rel01_closeout.md); opened
> 2026-09-14). Seven feature specs built, 754 tests at the close. Its design record is frozen in
> [`sdd/archive/rel-01/`](sdd/archive/rel-01/README.md). No release is open.

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

**The R18 graph of this repository's own specs** is in `sdd/archive/rel-01/trial_01/full-corpus/`: open
`sdd/archive/rel-01/trial_01/full-corpus/graph.html` directly, or run `sddc --root sdd/archive/rel-01/trial_01/full-corpus status`.

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

### Start here: read the export (F7)

Run `sddc export` after a compile (`--out DIR`, default `.sdd/export/`; `--allow-open` only when you
accept contradictions with no human verdict — the export is refused otherwise, exit 3). It writes the
files an agent reads; it makes no model call and is byte-identical for the same store.

| File | Read it to |
|---|---|
| `MAP.md` | Start here: banners, the units in build order, cycles, where each contract and decision lives, how to use the rest |
| `packs/00-foundation.md` … | One pack per unit, in build order. **Text** (every block verbatim, tagged with its nodes) first; then the claims, acceptance criteria, constraints in scope, related claims elsewhere, settled conflicts and terms |
| `CHECKLIST.md` | Every claim id. Each must end **implemented, tested, or listed as not done with a reason** |
| `export.meta.json` | Counts, sizes, the excluded blocks and why, the store hash |

The agent **never reads** `sdd/specs/**`, `.sdd/` (the store is the compiler's database, not a reading
format), or any existing implementation. Mark code with `# spec: <id>`; name tests after the `AC-…`
label or the node id. A contradiction the owner judged `real` appears as *Settled* with the owner's
note; one judged `false` does not appear; with `--allow-open` an undecided one appears as `UNSETTLED`
— state your choice in `OPEN_QUESTIONS.md`. A block the owner judged a real duplicate of an earlier one
is left out (F7 D13). Scoring the code against the checklist is the harness's job, not the compiler's.

*Everything below describes reading the raw `.sdd/` store. It predates the export (R18, `trial_01`) and
remains as a fallback and as the record of what the graph carries.*

### The rule: the agent reads the graph, never the specs

The point of the compiler is that its graph can stand in for the Markdown. So the agent **must not
read the spec files**, **nor `.sdd/blocks.jsonl`** (it stores every paragraph's verbatim text, so it
is the specs in another format), **nor any existing implementation**. It works from the compiled
graph alone. Whatever the graph does not carry, the agent has to design itself and say so. That list
of gaps is one of the results the experiment is for.

### Is that enough to build from? Measured on `sdd/archive/rel-01/trial_01/full-corpus/` (R18)

**Yes for behaviour, not for exact formats.** The graph holds 950 claims:

- behaviour, structure, data rules and constraints;
- 191 acceptance criteria that become tests;
- 127 decisions with the options they rejected;
- 421 rationale and example annotations;
- the stack itself, because the constitution's claims are nodes ("Language: Python ≥ 3.11",
  "tests with pytest").

What it does **not** carry:

| Gap | Measured | Consequence for the agent |
|---|---|---|
| **Contract formats** | In `trial_01`, compiled before F3 D39, all 25 fenced blocks — every record shape and file format in the specs' "Contracts" sections — form no node. A store compiled now forms each as one node: id `CT-n.k` from its title (22 of them), `text` the JSON or YAML verbatim | Build to a `CT-` node's `text` exactly. Where none exists, design the format from the `L3`/`L4` claims about it and record it as invented |
| **Definitions** | 0 of 1 031 terms in `trial_01`, compiled before F3 D38. A store compiled now gives a term the spec's own "X is Y" sentence as `definition` — measured on this corpus, 15 of 1 031 terms | Use `definition` where present; otherwise infer meanings from how terms are used |
| **Everything that is not a claim** | 183 of 845 paragraphs form no node; node spans cover 54 % of the spec text (rationale is partly kept as annotations) | Expect gaps in context, not in obligations |
| **Fragments** | 82 nodes have text under 30 characters (`keep id, "unchanged"`) | Read `canonical`, `heading_path` and the node's annotations alongside `text` |
| **Leakage** | 39 nodes in `trial_01` come from the specs' *Traceability* tables and name the existing `src/` and `tests/` files. A store compiled now does not atomize those sections (`skip_headings`, F1 D14) | Skip any that remain: they describe an earlier implementation, not a requirement |
| **One missing paragraph** | 1 block never atomized (an open `atomize_failed` item in `review.jsonl`) | Its content is unavailable; note it as a known gap |
| **Unsettled conflicts** | 381 open, unadjudicated; on an earlier sample about 1 in 10 was real | Treat each as a question (below) |

### What the agent reads

| Path | What it is | Use it to |
|---|---|---|
| `.sdd/nodes/*.jsonl` | Every atomic claim, one JSON record per line, one file per family | Your checklist: every non-`V` node must be satisfied by code, every `V` node by a test |
| `.sdd/terms.jsonl` | The vocabulary: canonical names, aliases, `broader` (kind-of) | Name modules, classes and fields consistently; an alias is the same thing |
| `.sdd/edges/*.jsonl` | Links: `depends_on`, `refines`, `subsumes`, `duplicates`, `conflicts_with` (judged), `verifies` (code) | Build order (`depends_on`), and which test covers which rule (`verifies`) |
| `.sdd/conflicts.jsonl` | Open conflicts, each with the judge's rationale and a quote from both claims | Questions to settle before implementing either side |
| `.sdd/graph.meta.json` | Counts and versions | Check you loaded everything: 950 nodes and 4 199 links in `trial_01` |
| `.sdd/review.jsonl` | Attention items for people | Only to learn what is missing: an open `atomize_failed` item is a paragraph with no node |
| `.sdd/adjudications.jsonl` *(if present)* | Human verdicts on conflicts | A conflict judged `false` is settled: ignore it |

**The fields of a node that matter for code:**

- `layer` says what to build. `L0` intent tells you why; `L1` behaviour becomes a feature seen from
  outside; `L2` structure becomes a component or module; `L3` contract becomes an interface, CLI or
  file format; `L4` data becomes a schema or type; `L5` logic becomes an algorithm; `C` becomes a
  cross-cutting rule to enforce; `V` becomes a test.
- `canonical` gives the claim in a fixed shape: state / trigger / scope / subject / **modality** /
  response. `MUST` and `MUST NOT` are hard; `SHOULD` and `MAY` are softer. It is the easiest field
  to build from.
- `text` is the claim's own words, quoted from the spec. `annotations` holds the rationale and
  examples written beside it. `decision` holds a decision's chosen and rejected options.
- `family` is the thing the claim is about. `source.file` tells you which spec it came from (one
  feature per spec). `source.heading_path` tells you its section. Use both to group your design.
  **Never open `source.file`.**
- `label` (`AC-1.4`, `CT-2.1`) is the spec's own id for an acceptance criterion or contract. Use it
  in test names.
- `status`: `conflict` means unsettled; `ambiguous` means vague (the `ambiguity` field says why);
  `validated` means clean. `flags` containing `inferred` means the description added something the
  spec did not say: trust `text` over `canonical` there.

### What the agent never reads

| Path | Why |
|---|---|
| `sdd/specs/**` | The specifications themselves. Reading them defeats the experiment |
| `.sdd/blocks.jsonl` | The verbatim text of every spec paragraph: the specs in another format |
| Any existing implementation (`src/`, `tests/` of this repository) | "From scratch" means from the graph |
| `graph.html`, `.sdd/views/` | Human visualizations of the same data |
| `.sdd/lock/` | Raw model answers and their cost: provenance, not requirements |
| `.sdd/runs.jsonl`, `.sdd/sources.jsonl`, `.sdd/profile.yaml`, `.sdd/conflicted_nodes.json` | Compiler bookkeeping, or derived from the files above |
| `.sdd.bak-*/`, `round-*`, `driver.*`, `summary.py`, `ingest.json`, `corpus.sha256` | Backups, logs and scripts of the compile runs |

### The procedure

1. **Load the graph.** All nodes, terms, links and open conflicts. Confirm the counts against
   `graph.meta.json`.
2. **Read the foundation first.** The nodes whose `source.file` is `vision.md` or `constitution.md`
   state the purpose, the stack and the rules every file must follow (74 nodes in `trial_01`).
3. **Drop what is not a requirement.** Skip nodes whose `source.heading_path` contains
   *Traceability*: they list an earlier implementation's files.
4. **Design from the layers, feature by feature.** Group nodes by the spec they came from, then by
   family. `L2` gives the components, `L3` the interfaces, `L4` the data, `L1` the features, `L5` the
   algorithms; `C` nodes are rules that cut across all of them. Name things with the canonical term
   names.
5. **Fill the gaps openly.** Where a format, a schema or a meaning is not in the graph — above all
   the `CT-` contracts — design it from the claims that mention it, and list it under *Invented* in
   `OPEN_QUESTIONS.md` with the node ids it rests on.
6. **Settle conflicts you touch, never silently.** For each open conflict involving a node you
   implement, compare the two claims (the record quotes both). If they only look contradictory
   (different situations, different components), note it and continue. If they really contradict,
   choose, and write the choice and its reason in `OPEN_QUESTIONS.md`. Do the same for every
   `ambiguous` node: state the assumption you made.
7. **Implement test-first.** Each `V` node becomes a test named after its `label` (or its id). Write
   the test, then the code that passes it.
8. **Leave a trail.** Put `# spec: <node id>` beside the code that satisfies a node. Write
   `TRACEABILITY.md`: every non-`V` node → the code that satisfies it, every `V` node → its test, and
   every node you did **not** implement, with the reason.

### A prompt to hand an agent

Replace `<BUILD>` with the compiled directory (for this repository's own specs:
`sdd/archive/rel-01/trial_01/full-corpus`) and `<OUT>` with an empty directory for the new code.

```text
You are generating a complete codebase from scratch, using ONLY a compiled spec graph.

Read only these files:
  <BUILD>/.sdd/nodes/*.jsonl     every atomic claim (one JSON record per line)
  <BUILD>/.sdd/terms.jsonl       vocabulary: canonical names, aliases, kind-of links
  <BUILD>/.sdd/edges/*.jsonl     relations between claims
  <BUILD>/.sdd/conflicts.jsonl   open conflicts, with both claims quoted
  <BUILD>/.sdd/graph.meta.json   counts, to check you loaded everything
  <BUILD>/.sdd/review.jsonl      only to see which paragraphs never became claims
Never read: <BUILD>/sdd/specs/ or any other Markdown spec, <BUILD>/.sdd/blocks.jsonl,
the file named in a node's source.file, or any existing implementation. Ignore everything
else in <BUILD>. Write everything in <OUT>.

Steps:
1. Load all nodes, terms, links and conflicts; check the counts against graph.meta.json.
2. Read first the nodes whose source.file is vision.md or constitution.md: purpose, stack,
   rules. Follow them everywhere.
3. Skip nodes whose source.heading_path contains "Traceability".
4. Design per source spec and family: L2 components, L3 interfaces, L4 data, L1 features,
   L5 algorithms; enforce every C node where its scope applies. Use canonical term names.
   Build from "canonical", "text", "annotations" and "decision".
5. Nodes whose id starts with "CT-" are contracts: their "text" is the exact record shape
   or file format, verbatim. Implement them exactly. Terms have few definitions (a term's
   "definition", when present, is the spec's own sentence). Design what is missing from the
   claims that mention it, and list each one under "Invented" in
   OPEN_QUESTIONS.md with the node ids it rests on.
6. For a node with status "conflict", compare the two claims each of its conflicts quotes.
   Only apparent: note it and go on. Real: choose, and record choice and reason in
   OPEN_QUESTIONS.md. For "ambiguous" nodes, record the assumption you made.
7. Test-first: each V node becomes a test named after its label (e.g. test_AC_1_4_...).
8. Mark code with "# spec: <node id>". Write TRACEABILITY.md mapping every node to code or a
   test, and list every node not implemented, with the reason.
Finish with: the test suite passing, TRACEABILITY.md, OPEN_QUESTIONS.md.
```

### Judging the result

Compare the generated code with the specs **afterwards, as a person**. Useful measures:

- how many `V` nodes became passing tests;
- how many nodes `TRACEABILITY.md` leaves unimplemented;
- how many *Invented* formats match the real contracts;
- how many conflicts the agent settled correctly.

Each gap you find is either a gap in the graph (a compiler finding) or a gap in the agent.

---

## Repository map

| Path | What |
|---|---|
| `CLAUDE.md` | Working agreement for AI agents working **on** the compiler |
| `sdd/specs/` | The compiler's own specs (vision, constitution, F1–F7) — [map](sdd/README.md) |
| `sdd/design/` | The open release's brainstorm and design notes (none open); `releases/` holds the one-page close-outs |
| `src/sdd_compiler/` · `tests/` | The Python CLI and its tests |
| `harness/` | Runs a coding agent on a task in a sandbox and scores the result with hidden tests. Outside the compiler (F7 D9); `sddc` never reads it |
| `docs/lectures/` | Lectures explaining the design, including the as-built beginner's guide |
| `sdd/archive/rel-01/trial_01/full-corpus/` | The R18 compile of this repository's own `sdd/specs/`: spec copy, graph, explorer — the input to the first code-generation trial |
| `sdd/archive/rel-01/` | Release 01, frozen: brainstorm and decisions, design notes, gates, measurements, the build plan and issue log, a snapshot of the specs at the close |
| `sdd/archive/` | Other superseded documents and pre-rel01 brainstorm exports |
| `docs/MIA5150-Project/` | The course study: the submitted proposal (`project-proposal/`), the pilot tasks the harness runs (`tasks/`), the F1 pilot result, the metrics survey |
