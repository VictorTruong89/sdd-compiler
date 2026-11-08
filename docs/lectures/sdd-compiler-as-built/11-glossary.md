# 11. Glossary

| Term | Meaning | Chapter |
|---|---|---|
| **Adjudication** | A person's verdict (`real` / `false`) on a conflict record, kept in `.sdd/adjudications.jsonl`; a `real` one's note is shown in the export as `Settled:` | 2, 6, 9 |
| **Alias** | Another name for a term, created by a Q-TERM `same` verdict | 5 |
| **`--allow-open`** | Export flag: write the export although contradictions have no current verdict; they are marked `UNSETTLED:` | 2, 9 |
| **Ambiguity** | A recorded reason a claim is vague: `vague_term`, `referential`, `missing_actor`, `scope`, `missing_modality`, `unbounded_quantity`, `inferred`, `unplaceable`, `unresolved_term`, `mixed_layers`, `pending_review`, `low_confidence_verdict` | 4 |
| **Annotation** | A rationale sentence kept with a node, not a claim itself. Examples were annotations until rel02; now they become example nodes, unless their block has no claim | 4 |
| **Atom** | One claim found in a block by Q-ATOM (or formed by code from its answer), as verbatim quotes, before it is described | 4 |
| **Attention item** | A line in `.sdd/review.jsonl` asking a person to look: failed block, term merge, inferred fact | 3, 8 |
| **Backend** | How questions reach the model: `claude-code` (default, headless Claude Code) or `anthropic-api` | 3 |
| **Backward need** | A `depends_on` link from a pack to a later pack, which the build order could not avoid; listed in `MAP.md` | 9 |
| **Block** | A structural unit of a spec file: paragraph, list item, table row, code block | 4 |
| **Broader** | A term's parent in the kind-of hierarchy (`review item` → `item`); S1, S2 and S8 follow it | 5, 6 |
| **Call cap** | `max_calls_per_run`; reaching it ends a run cleanly with exit `5` | 2 |
| **Candidate pair** | Two nodes retrieval judged worth asking the model about | 6 |
| **Canonical form** | The claim rewritten as state / trigger / scope / subject / modality / response | 3, 4 |
| **Check phase** | Retrieval + judgment, after atomization, inside `compile` | 6 |
| **Checklist** | `CHECKLIST.md`: every live node id once, grouped by home pack; each must end implemented, tested or listed as not done | 9 |
| **Compiler export / oracle export** | In rel02 trials: what `sddc export` writes, against a harness-made export with every planted conflict flagged. The oracle is not a compiler feature | 9 |
| **Conflict gate** | The export refuses (exit 3) while an open contradiction has no current human verdict | 2, 9 |
| **Conflict record** | An open or resolved `contradiction`, `duplication` or `subsumption` between two nodes | 6 |
| **Context pack** | The claims governing one change, gathered by tiers from one family by hand (`scripts/context_pack.py`); the export is the built hand-off for a whole build | 9 |
| **Contract** | A fenced block in a `contract_languages` language (`json`, `yaml`, `text`): one node, formed whole by code, with its title's `CT-` id | 4 |
| **Coverage (guard G3)** | Every normative sentence must be inside an atom or have a non-claim role | 3 |
| **Coverage (constraint)** | Whether a `C` node's scope selector applies to a node | 5 |
| **Coverage check (export)** | Every live block's text must occur verbatim in its home pack, or nothing is written | 9 |
| **Definition** | The author's sentence defining a term, attached by code to the term it opens with; shown in the export's Terms | 5, 9 |
| **Example node** | A `V` node formed by code from an `example` sentence, verifying the claim before it, flagged `example`; listed in the export as `example of`, not as an acceptance criterion | 4 |
| **Export** | The output of `sddc export`: `MAP.md`, `packs/`, `CHECKLIST.md`, `export.meta.json` — the spec text verbatim, cut into units, with ids, order and settled conflicts; no model call | 9 |
| **Family** | The one term a node is primarily about; decided by a fixed rule | 5 |
| **Foundation** | Pack `00`: every block of the files matching `export.foundation_globs` (vision, constitution), read first | 9 |
| **`(global)`** | The pseudo-family of constraints scoped to no single family | 5 |
| **Guard** | A deterministic check on a model answer (G2 anchoring, G3 coverage, G4 injection, G5 schema, G6 weak words) | 3 |
| **Home** | The unit (pack) a node's block belongs to | 9 |
| **Judgment** | One accepted model answer, recorded in the lock with its cost (`J-000123`) | 3, 7 |
| **Judgment lock** | `.sdd/lock/`: every accepted answer, keyed by content, replayed instead of re-asked | 1, 7 |
| **Keywords** | A node's lower-cased words minus stop words, computed by code | 4, 6 |
| **Layer** | What kind of statement a node is: L0 intent … L5 logic, C constraint, V verification | 5 |
| **Link** | A typed edge: `uses_term`, `verifies` (code); `refines`, `depends_on`, `subsumes`, `duplicates`, `conflicts_with` (judged) | 6 |
| **Local label** | An id unique only inside one file (`S1`, `**D1 — …**`): labels the nodes, never becomes an id | 4 |
| **Map** | `MAP.md`, the export's entry point; not to be confused with `.sdd/views/map.md`, the families × layers view | 8, 9 |
| **Node** | One atomic claim with its classification, links and status | 4 |
| **Pack** | One Markdown file of the export, holding one unit: Text verbatim, then Claims, Acceptance criteria, Constraints in scope, Related elsewhere, Conflicts, Terms | 9 |
| **Pending** | A block whose `atomized_hash` differs from its `text_hash` (code blocks, skipped headings excepted) | 4 |
| **Provisional** | A verdict involving an ambiguous node: kept, but marked | 6 |
| **Q-ATOM / Q-DESC / Q-TERM / Q-PAIR** | The four questions the model is asked | 3 |
| **Retrieval sources S1–S10** | The evidence rules that propose candidate pairs, each worth fixed points; S9 rare keyword and S10 topic named were added in rel02 | 6 |
| **Round** | One `sddc compile` of a multi-run compile; ends at the cap, a session limit, or completion. (In rel02 also a numbered trial, r14 … r21) | 2 |
| **Scope selector** | A constraint's families, terms, categories and layers | 5 |
| **`skip_headings`** | Headings whose blocks are stored but never atomized nor exported (default Traceability) | 2, 4 |
| **Stale** | Needs re-checking because a judged neighbour was edited or deleted | 6, 7 |
| **Status** | `conflict` > `ambiguous` > `stale` > `unchecked` > `validated`, derived, never set | 6 |
| **Suppressed** | A duplication/subsumption verdict the document's form explains, not recorded as a conflict | 6 |
| **Term** | A named thing the specs talk about, in `.sdd/terms.jsonl` (`term:share_link`) | 5 |
| **Unit** | A spec file's text under one second-level heading; split one level deeper above 20 000 characters | 9 |
| **Unsettled** | A contradiction with no current human verdict; blocks the export unless `--allow-open` | 9 |
| **Views** | Generated Markdown in `.sdd/views/`: the map, family cards, the conflicts list | 8 |
