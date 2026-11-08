# 7. Changes and new specs — how the graph follows the text

Specs change every day. The compiler is built so that an edit costs in proportion to the edit, not
to the spec set, and so that nothing already known is thrown away because one word changed.

*Layman:* a well-run filing office re-files only the pages you changed. The index cards for untouched
pages stay where they are, with every note already written on them.

## What happens on the next `sddc compile`

```text
 1. ingest       every file re-split into blocks; each block matched to its old id
 2. pending      blocks whose text hash ≠ the hash they were last atomized at
 3. atomize      only the pending blocks; old answers replayed from the lock where the input is identical
 4. align        the new atoms matched to the block's old nodes, so a claim keeps its id
 5. stale        judged neighbours of an edited node marked stale
 6. check        only nodes that need it (new, stale, conflict, unchecked); the rest replay free
 7. write        one all-or-nothing transaction; views regenerated
```

### 1. Block identity (F1, `ingest/identity.py`)

Three passes per file:

1. **exact** — same normalized text, same heading path → same id, `unchanged` (even if it moved);
2. **positional** — same heading, same position under it → same id, `changed`;
3. **the rest** — new blocks get new ids; old blocks become `removed`.

An id is never reused: re-adding deleted text gives a **new** id, so "this existed, then was removed"
stays a fact.

### 2–3. Only the pending work is paid for

A block is pending when `atomized_hash ≠ text_hash`. The **judgment lock** (`.sdd/lock/*.jsonl`) keys
every accepted answer by the question's kind, schema, instructions and the item's **content** — not its
id. So a moved paragraph, or an untouched one next to an edit, replays for free. A prompt change in the
code changes the key, and those items are asked again.

### 4. Node alignment (F3 §4.6, `atomize/align.py`)

When an edited block is re-atomized, its new atoms are matched one-to-one to its old nodes, by text
overlap (`difflib` ratio ≥ 0.5), then by equal subject and response:

| Outcome | Meaning | The node… |
|---|---|---|
| `unchanged` | Same text up to whitespace (case counts) | keeps id **and** its whole record, verdicts included — except its `source` and its annotations, which are refreshed from the block (F3 D42: in rel02 round 14 a planted example beside an unchanged claim was lost) |
| `edited` | Overlapping, different | keeps its **id**, gets new content, is re-checked |
| `split` | A new atom overlapping an old node another atom kept | gets a new id |
| `new` | Nothing to match | new id |
| `merged` / `removed` | An old node no atom kept | deleted, with the cascade below |

### 5. The cascade

Deleting a node closes open conflicts it was in (`member_deleted`) and marks its judged neighbours
**stale**. Editing a node marks its judged neighbours **stale**: the verdict was about the old text.
Stale nodes are re-checked on this run's check phase.

### 6. Check — from both ends

Only new, edited, stale and conflict nodes are checked, but a pair is now proposed from **either
end** (F5 D14, chapter 6): an old, validated node that ranks the new claim within its own top 6 gets
the pair judged, even when the new claim ranks the old one far down its own list. Before this, an
incremental compile could miss a conflict that a full compile of the same text would have found.

## Adding a new spec: where will it land?

The compiler decides placement by rule, so you can predict it — and steer it.

**Worked example.** You add to `policy.md`:

```markdown
Share links expire after 7 days.
```

1. **Block:** new → new id, pending.
2. **Atom:** one requirement.
3. **Layer:** Q3 (an outsider can see it) → **L1**.
4. **Terms:** the model tags `share link`. The registry already has `term:share_link`, so it resolves
   there — *no Q-TERM question*. Had you written "sharing URL", there would be no exact match, and
   `share link` shares no word with it and is under 0.8 similar (checked: `similar_terms` returns
   nothing), so a new term `sharing_url` would be created **without any question**, and your claim
   would sit in a new family of its own.
5. **Family:** subject is an entity → **`term:share_link`** (rule 1). It joins the 30-day claim.
6. **Check:** it is `unchecked`, so it is checked; S1 + S2 + S4 + S5 + S6 score its pair with the
   30-day claim at 10.0 (chapter 6); Q-PAIR is asked; a `contradicts` verdict opens a contradiction.

**The lesson for authors:** *use the graph's existing names.* Look up the family you mean in
`.sdd/views/map.md` or `.sdd/terms.jsonl` and write that name as the subject. Computed with the real
functions (re-run with the current code on 2026-11-08, same result): "Sharing URLs expire after 7
days." against the 30-day claim scores **3.5** (S5 keywords 1.0 + S6 time 2.5) instead of **10.0** —
still above the 1.0 bar, but now it competes for one of only six candidate slots per node against
every same-family pair. On a large spec set such pairs are the ones that fall off the list; the M4 gate
measured exactly this (5 of 6 planted conflicts ranked below the cut because each side used its own
name), and so did rel02 round 17 (all 10 planted conflicts the compiler missed were pairs never put to
the judge).

The rel02 sources soften this only a little. S10 would add 2.0 if the new sentence said "share link"
anywhere (the family's two-word name in its text) — it does not. S9 would add 1.0 per rare shared
keyword in a large graph. Neither replaces writing the existing name.

## Tracing a claim after the compile

From a place in the source to its nodes:

```python
# PYTHONPATH=<repo>/src python - ; run in the directory holding .sdd/
from pathlib import Path
from sdd_compiler.store.graph import load_graph
g = load_graph(Path(".sdd"))
file, line = "sdd/specs/F1_ingest/spec.md", 28
for n in sorted(g.nodes.values(), key=lambda n: n["id"]):
    s = n["source"]
    if s["file"] == file and s["lines"][0] <= line <= s["lines"][1]:
        print(n["id"], n["layer"], n["family"], n["status"], n["conflict_ids"])
```

On R18 that prints `N-000007 L3 term:pending_block conflict ['CF-000315']` and `N-000008 L5
term:model_call conflict ['CF-000043', 'CF-000072', 'CF-000085']` — two claims live on that line
(re-run with the current code on 2026-11-08). Then `sddc family model_call`
shows the neighbourhood, and `sddc conflicts` the records.

From a node back to its words: `source.file` + `source.lines` for a person;
`source.block_id` + `source.spans` for exact character offsets in the block's stored text.

## What an edit does *not* do

- It does not close a conflict. Only a re-judgment (the pair is asked again because a member changed)
  or a deletion does. Fix the text, compile, and the re-judged pair closes the record with
  `resolved_reason: fixed`.
- It does not rewrite history. Conflict records, adjudications and lock records are appended; an
  earlier verdict stays visible.
