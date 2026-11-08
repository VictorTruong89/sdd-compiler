# 3. Who does what: the AI model and the code

## The short answer

| Job | Done by | Where in the code |
|---|---|---|
| Split Markdown into blocks | **code** (markdown-it parser) | `ingest/segment.py` |
| Give blocks stable ids, detect edits | **code** (hash, then position) | `ingest/identity.py` |
| Break a block into atomic claims | **AI model** — question **Q-ATOM** | `atomize/qatom.py` |
| Form a contract fence (`json`/`yaml`/`text`) as one atom, without asking Q-ATOM | **code** (F3 D39) | `atomize/contracts.py` |
| Split a table cell of several sentences into one claim each; give an atom the subject or condition its sentence opened with | **code**, from Q-ATOM's own sentence labels (F3 D43, D44) | `atomize/forming.py` |
| Turn an example sentence into a verification node of the claim before it | **code**, from Q-ATOM's `example` label (F3 D41) | `atomize/forming.py` (`example_pieces`) |
| Attach a definition sentence to the term it defines | **code**, from Q-ATOM's `definition` label (F3 D38) | `atomize/definitions.py` |
| Describe each claim: canonical form, seven layer answers, terms | **AI model** — question **Q-DESC** | `atomize/describe.py` |
| Decide whether a new term is a synonym of an old one | **AI model** — question **Q-TERM** | `atomize/terms.py` |
| Check every quote is really in the source | **code** (guards G2 … G6) | `atomize/guards.py` |
| Choose the node's layer | **code**, from the model's seven yes/no answers | `model/placement.py` |
| Choose the node's family | **code**, by a fixed rule list | `model/family.py` |
| Ids, keywords, quantities, `verifies`, `uses_term` links | **code** | `model/ids.py`, `model/keywords.py`, `atomize/quantities.py`, `atomize/forming.py` |
| Decide which pairs of nodes to compare | **code** (ten evidence sources, a score) | `retrieval/` |
| Judge how two claims relate | **AI model** — question **Q-PAIR** | `conflicts/judge.py` |
| Turn a verdict into links and conflict records | **code** | `conflicts/records.py` |
| Write the graph, check it, render the views | **code** | `store/`, `views/` |
| Write the agent export (map, packs, checklist) | **code**, no model call at all (F7 §4.1) | `export/` |

**Which model?** One model answers all four questions: whatever `atomizer.model` names in the
profile — **`haiku`** by default, i.e. Claude Haiku. By default it is reached through **headless
Claude Code**:

```text
claude -p "<prompt>" --model haiku --output-format json --json-schema '<schema>'
```

with `MAX_THINKING_TOKENS=0` (thinking off), `SDD_COMPILER_CHILD=1` (so nothing can recurse into the
compiler), and `ANTHROPIC_API_KEY` removed from the child's environment (`llm/claude_code.py`). The
answer is read from Claude Code's `structured_output`, which must match the JSON Schema sent with the
question. A second backend, `anthropic-api`, exists (`llm/anthropic_api.py`) but is barely tested.

So "which AI builds the graph?" has a precise answer: **none does.** The model answers four closed
questions; **deterministic code builds the graph** from the checked answers. The model never writes a
record, never picks an id, never decides a layer or a family directly.

## Why split it this way

Layman version: the model is a very well-read clerk who can read a sentence and tell you what it
says. You would not let a clerk run the filing system: they would file the same thing under three
names on three days. So you ask the clerk narrow questions — *"which sentences here are instructions?
quote them"* — and the filing rules are written down and applied the same way every time.

Concretely it buys three things:

- **Reproducibility.** The model will not answer the same way twice. Code will. With the answers
  locked (chapter 7), the whole graph rebuilds byte-identically.
- **Checkability.** A closed answer can be checked: is the quote in the text? is the relation one of
  six? is a symmetric relation marked symmetric? An open answer ("summarise the spec") cannot.
- **Cost.** A headless Claude Code call carries ≈ 22 000 tokens of harness prompt whatever it asks
  (build-plan I-8), so the questions are **batched**: 20 blocks per Q-ATOM call, 8 atoms per Q-DESC
  call, 8 pairs per Q-PAIR call. Each item's answer is still checked alone, and only a failed item is
  re-asked, alone, once.

## The four questions

### Q-ATOM — "what claims are in this block?"

Asked about a batch of blocks. For each block the model returns:

- every **sentence** with a **role**: `requirement`, `constraint`, `assumption`, `verification`,
  `decision` (these five become atoms) or `definition`, `rationale`, `example`, `context`,
  `open_question` (these do not become atoms in the answer);
- the **atoms**: each one claim, as verbatim quotes, with its kind.

The prompt gives the atom tests — one verdict decides it, parts could change independently, one layer,
stands alone — and rules learned from real failures: a heading line is `context`; everything after
"*Why:*" or "*Rejected:*" is `rationale`; an acceptance criterion (Given/When/Then) is **one**
verification atom; a table row is one claim.

**What code does with the answer, without asking again.** The prompt has not changed since rel01
(a prompt change is part of the lock key and would re-ask every block of every store, F3 D21), so
every rel02 fix reads the sentence labels the model already gives:

- an `example` sentence becomes a `verification` atom of the claim before it, flagged `example` (F3
  D41); it used to be an annotation and was never compared with anything — a planted example that
  contradicted its own rule was missed that way (rel02 round 14);
- a `definition` sentence is attached to the term it opens with (F3 D38);
- a table row is still one claim (F3 D34), **except** that a cell holding several sentences gives one
  claim per sentence, each led by the row's first cell so it keeps its subject (F3 D43);
- an atom that quotes only a sentence's predicate is given the sentence's uncovered opening — its
  subject or condition — or, when it opens with a pronoun, the sentence's first atom (F3 D44).

The last two came from rel02 round 17, where three planted conflicts sat inside multi-sentence table
cells and one planted cause was in no node at all (F3 D43, D44 record the cases).

*Toy example.* Block: "A share link must expire 30 days after it is created." → one sentence, role
`requirement`; one atom, kind `requirement`, quote = the whole sentence.

**Contracts skip Q-ATOM.** A fenced block in a `contract_languages` language is one claim by
construction: code forms the one atom (F3 D39), and Q-DESC still places it and tags its subject.

### Q-DESC — "describe this claim"

Asked about a batch of atoms (with their block's text). For each atom:

- the **canonical form**, in an EARS-like template:
  `[While state] [When trigger] [Where scope] the SUBJECT MUST|MUST NOT|SHOULD|SHOULD NOT|MAY RESPONSE`;
- **seven yes/no layer questions**, each yes with a supporting quote (chapter 5);
- **terms**: the things the claim is about, each with a kind (`entity`, `data`, `event`, `actor`,
  `component`, …) and a role (`subject`, `response`, `trigger`, `state`, `scope`);
- **ambiguity** the model noticed: only `missing_actor`, `referential` ("it", "this"), `scope`;
- for a constraint its scope; for a verification what it verifies; for a decision the chosen and
  rejected options.

*Toy example.* Subject `share link`, modality `MUST`, response `expire 30 days after it is created`;
Q3 = yes ("A share link must expire 30 days after it is created"), the other six no; term
`share link` — kind `entity`, role `subject`.

Code then adds what it can compute itself: **quantities** (`30 days` → 2 592 000 s) are parsed by code,
never taken from the model; **weak words** from your profile add `vague_term`; an obligation with no
modal verb adds `missing_modality`; a value or term in the canonical form that is **not in the
source** adds `inferred` (guard G4 — the model is not allowed to add facts).

### Q-TERM — "is this new name one we already know?"

Asked only when a new term has **look-alike** names in the registry (a shared word, or ≥ 0.8 string
similarity). Four verdicts:

| Verdict | Effect |
|---|---|
| `same` | Merged at once: the new name becomes an **alias** ("shared link" → `share link`); a review item lets a person undo it |
| `narrower` | Kept as its own term, recording `broader` ("review item" is a kind of "item") |
| `different` | Nothing |
| `unsure` | Kept separate; its nodes get `pending_review` until a person decides |

Before asking, code throws away tags that are not names of things — anything with a digit (`AC-1.4`,
`120 s`), a `:` or `=`, or more than four words — and folds plurals ("blocks" → "block").

### Q-PAIR — "how do these two claims relate?"

Asked about a batch of candidate pairs chosen by code (chapter 6). For each pair, exactly one relation
from a closed list:

`none` · `refines` · `depends_on` · `duplicates` · `subsumes` · `contradicts`

with a direction (`a_to_b`, `b_to_a`, or `symmetric` — required for `none`, `duplicates`,
`contradicts`), a one-sentence rationale, a verbatim quote from each claim, and a confidence
(`high`/`low`). The prompt carries rules learned the hard way: different numbers are **not**
automatically a contradiction (a 24-hour link inside a 30-day archive is fine); do not do arithmetic
the text does not do; an acceptance criterion restating its requirement is not a duplicate; a
different name is not a different object.

## Guards: how code keeps the model honest

| Guard | Checks | On failure |
|---|---|---|
| **G2** anchoring | Every quote appears in the source, up to layout (line wraps, `> `, `**`, backticks) | Re-ask the item once, naming the problem |
| **G3** coverage | Every sentence carrying a normative word (must, never…) is covered by an atom or explained by a role | Re-ask |
| **G4** no injection | Values and terms in the description exist in the block or its headings | Not a failure: node written, flagged `inferred` |
| **G5** schema | The answer matches the question's JSON Schema | Re-ask |
| **G6** weak words | Your profile's weak words in the quotes | Not a failure: ambiguity `vague_term` |

One exception, for contracts only: a quote from a JSON or YAML fence that is not found is **replaced
by the contract's whole text** instead of re-asked (F3 D40 in Q-DESC, F6 D23 in Q-PAIR). On the live
contract run the model kept quoting key lists and summaries instead of the fence. A contract is one
claim that is never split, so its whole span is the right quote. The replacement is counted in the
run's `contract_quotes_replaced` and `quotes_replaced`.

An item that fails twice is **not** guessed: its block stays pending, an `atomize_failed` attention
item is opened, and the next compile tries again. In R18, 69 blocks failed on one run and succeeded on a
later one; one block (a `*Rejected:*` sentence in F2) still fails every time (build-plan I-84). At rel01
close, 8 blocks failed on every retry (I-94, carried to rel02). For a pair that fails twice, the run's
JSON now lists the pair and the reason its last answer was rejected (F6 D22). R21's last run: 1 such
pair, a quote that was not verbatim (`compile-3.json`).

## R18, by question (rel01 code)

| Question | Accepted answers | Calls that produced one | Estimated API-equivalent |
|---|---|---|---|
| Q-ATOM | 922 blocks | 321 | ≈ $5.50 |
| Q-DESC | 1 094 atoms | 325 | ≈ $9.05 |
| Q-TERM | 795 terms | 77 | ≈ $1.48 |
| Q-PAIR | 4 251 pairs | 1 137 | ≈ $25.67 |
| *Subtotal* | | *1 860 calls* | *≈ $41.70* |
| **All calls**, including 813 whose answers were rejected | | **2 673** | **≈ $54.94** |

The dollar figures are Claude Code's own
`total_cost_usd` estimate, summed — an **API-equivalent estimate, not money spent**: the run was on a
subscription (build-plan I-82).

With the current code, the R21 store (450 blocks) took **860 calls, ≈ $3.58 est.** in three passes
(300 + 300 + 260; methodology notes, register row 174). The split by question was not tallied for it.
