# 9. Reading the graph as an AI agent

## What exists today, honestly

The graph was built so that a coding agent could be handed **the few claims that govern a change**
instead of a folder of documents. That hand-off — traversal into a *context pack* — is designed
(`sdd/archive/rel-01/design/rel01_design/G3-3-traversal.md`, spec id **F7 reserved, not built**), and the `sddc query`
command is deferred. So in rel01 **there is no built-in command that answers "what must I read to
change X?"**

What does exist is enough to follow the design's recipe by hand, because the store is plain JSON Lines
and the compiler's own loader and indexes are importable. This chapter is that recipe, with a helper
script (`scripts/context_pack.py`) tested on the R18 store.

*Layman:* the library has a perfect card catalogue but no librarian yet. This chapter teaches you to
use the catalogue yourself.

## The recipe

### Step 0 — make sure the graph is current

```bash
sddc status --json      # pending must be 0; if not, compile first
```

A graph older than the specs is worse than none: it looks authoritative. If any spec changed since
the last compile, compile again (it is cheap: only the changed blocks are paid for).

### Step 1 — find the target family

From the words of the task to the family most about them. Three ways, cheapest first:

1. **By name** — the task names a thing that is a term: look it up among canonical names *and
   aliases* (`GraphIndex.names`, after `normalize_name`, which lower-cases and folds plurals).
2. **By keyword** — count which families the task's keywords land in (below).
3. **By place** — the task points at a spec section: map `file:line` to nodes (chapter 7).

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

On R18 this prints `term:model_call`, then
`[('term:model_call', 7), ('term:node', 6), ('term:block', 6)]` — the name lookup and the keyword vote
agree.

### Step 2 — gather the context pack, in tiers

Follow the design's tier order (G3-3 §2), reduced to what the as-built graph can answer:

| Tier | Take | Why |
|---|---|---|
| 1 core | Every node in the family, ordered L0 → L5, C, V | What the code must do |
| 2 constraints | `C` nodes elsewhere whose scope **covers** a core node (`model/scope.py::covers`) | Rules the code must not break |
| 3 verification | `V` nodes whose `verifies` names a core node | How the change will be tested |
| 4 conflicts | Open conflict records with a core node as member | What is **not** settled |
| 5 neighbours (titles only) | Nodes one `depends_on` / `refines` link away | Context, not instructions |

`scripts/context_pack.py` does tiers 1–4:

```bash
cd ~/sddc-runs/full-corpus
PYTHONPATH=/path/to/sdd-compiler/src \
  python /path/to/sdd-compiler/docs/lectures/sdd-compiler-as-built/scripts/context_pack.py .sdd "model call"
```

Its real output on R18 (abridged):

```text
# context pack: term:model_call

## core (5)
✗ N-000766   L2  sdd/specs/constitution.md:70  'Model calls go through **one interface with two backends'
✗ N-000008   L5  sdd/specs/F1_ingest/spec.md:28  'F1 makes **no model calls'
✗ N-000233   C   sdd/specs/F3_atomizer/spec.md:72  'Every call records:** backend, model as reported, …'
✗ N-000565   C   sdd/specs/F6_conflicts/spec.md:16  'Ask the model one question about one pair at a time, …'
✗ AC-3.19    V   sdd/specs/F3_atomizer/spec.md:327  'Given** a completed compile, **when** compile runs again …'

## constraints in scope (10)
✗ N-000521   C   sdd/specs/F5_retrieval/spec.md:135  'F5 makes no model calls at all.'
✗ N-000781   C   sdd/specs/vision.md:43  'The model answers narrow, schema-bound questions — …'
…

## verifications (0)

## open conflicts touching it (6)
CF-000043 contradiction: N-000008 vs N-000233 — A states F1 makes no model calls, while B requires …
…
```

An unknown family name fails loudly and suggests close ones — it never returns an empty pack that
looks complete.

### Step 3 — read the flags before the text

Each line starts with the node's status mark. Treat them as instructions to the agent:

| Mark | Status | The agent should |
|---|---|---|
| `✗` | conflict | **Not** pick a side silently. Name the conflict (`CF-…`) and ask a person, or implement only what both sides allow |
| `?` | ambiguous | Read the ambiguity kind (`vague_term`, `referential`, `missing_modality`, `inferred`…); ask, or state the assumption it makes |
| `~` / `·` | stale / unchecked | The graph is behind the text — recompile first |
| `✓` | validated | Use as written |

A node flagged `inferred` contains a value or name the model added that the source does not say —
check the source line before relying on it.

### Step 4 — read the source, not only the node

A node's `text` is the claim's quoted words; its `canonical` form is the model's rewrite. Both are for
**finding**. For **implementing**, open `source.file` at `source.lines`: the surrounding rationale and
the exact wording are there. The node tells you *where to read*; the spec is still the authority
(CLAUDE.md: the specs are the source of truth).

### Step 5 — leave a trail

Name the nodes you implemented in the code and tests you write — the convention the design proposes
(G3-3 §3.4), e.g. a `# spec: N-000233` comment, or `AC-3.19` in a test name. Nothing in rel01 reads it
yet; every later feature (impact analysis, design-versus-as-built) needs it, and it costs nothing now.

### Step 6 — say what the pack left out

A manifest, even a short one: which families were included, which constraints were cut for length,
which conflicts are unresolved. An agent that knows its context is partial asks for more; one that
believes it is complete guesses (G3-3 §4).

## A prompt a person can hand an agent

```text
Before changing code for <task>:
1. Run `sddc status --json`; if pending > 0, run `sddc compile` and wait for exit 0 or 3.
2. Find the family: context_pack.py .sdd "<the main thing the task is about>".
3. Read every core, constraint and verification line; open each source file at its line.
4. For every ✗ line: list the CF id and stop to ask before implementing either side.
   For every ? line: state the assumption you make.
5. Implement; put `spec: <node id>` beside the code that satisfies each node; name tests after
   the AC ids they cover.
6. End with a manifest: families read, conflicts left open, assumptions made.
```

## Why a graph instead of just grepping the Markdown

- **Grep finds words; the graph finds rules that govern you without using your words.** On R18, the
  `model_call` pack pulls in "F5 makes no model calls at all" (a constraint from another spec) because
  its scope covers the family — a search for "retry" would never show it.
- **Grep cannot tell you a sentence is disputed.** The pack marks six open conflicts on this family;
  the Markdown files look equally confident everywhere.
- **Grep cannot tell you a sentence is not a rule.** Rationale, examples and "*Rejected:*" options are
  kept out of the nodes (they become annotations), so an agent is not steered by an option the authors
  rejected.

⚠ **The limit, stated plainly:** the pack is only as good as the graph's naming. If the atomizer filed
a claim under a synonym, it lands in another family and the pack misses it (chapter 7). Until
retrieval of synonyms improves, run step 1 with both the name and the keyword vote, and read the
top two or three families when they are close.
