# 11. Glossary

| Term | Meaning | Chapter |
|---|---|---|
| **Adjudication** | A person's verdict (`real` / `false`) on a conflict record, kept in `.sdd/adjudications.jsonl` | 2, 6 |
| **Alias** | Another name for a term, created by a Q-TERM `same` verdict | 5 |
| **Ambiguity** | A recorded reason a claim is vague: `vague_term`, `referential`, `missing_actor`, `scope`, `missing_modality`, `unbounded_quantity`, `inferred`, `unplaceable`, `unresolved_term`, `mixed_layers`, `pending_review`, `low_confidence_verdict` | 4 |
| **Annotation** | A rationale or example sentence kept with a node, not a claim itself | 4 |
| **Atom** | One claim found in a block by Q-ATOM, as verbatim quotes, before it is described | 4 |
| **Attention item** | A line in `.sdd/review.jsonl` asking a person to look: failed block, term merge, inferred fact | 3, 8 |
| **Backend** | How questions reach the model: `claude-code` (default, headless Claude Code) or `anthropic-api` | 3 |
| **Block** | A structural unit of a spec file: paragraph, list item, table row, code block | 4 |
| **Broader** | A term's parent in the kind-of hierarchy (`review item` → `item`) | 5 |
| **Call cap** | `max_calls_per_run`; reaching it ends a run cleanly with exit `5` | 2 |
| **Candidate pair** | Two nodes retrieval judged worth asking the model about | 6 |
| **Canonical form** | The claim rewritten as state / trigger / scope / subject / modality / response | 3, 4 |
| **Check phase** | Retrieval + judgment, after atomization, inside `compile` | 6 |
| **Conflict record** | An open or resolved `contradiction`, `duplication` or `subsumption` between two nodes | 6 |
| **Context pack** | The claims an agent needs for one task, gathered by tiers (designed as F7; by hand today) | 9 |
| **Coverage (guard G3)** | Every normative sentence must be inside an atom or have a non-claim role | 3 |
| **Coverage (constraint)** | Whether a `C` node's scope selector applies to a node | 5 |
| **Family** | The one term a node is primarily about; decided by a fixed rule | 5 |
| **`(global)`** | The pseudo-family of constraints scoped to no single family | 5 |
| **Guard** | A deterministic check on a model answer (G2 anchoring, G3 coverage, G4 injection, G5 schema, G6 weak words) | 3 |
| **Judgment** | One accepted model answer, recorded in the lock with its cost (`J-000123`) | 3, 7 |
| **Judgment lock** | `.sdd/lock/`: every accepted answer, keyed by content, replayed instead of re-asked | 1, 7 |
| **Keywords** | A node's lower-cased words minus stop words, computed by code | 4, 6 |
| **Layer** | What kind of statement a node is: L0 intent … L5 logic, C constraint, V verification | 5 |
| **Link** | A typed edge: `uses_term`, `verifies` (code); `refines`, `depends_on`, `subsumes`, `duplicates`, `conflicts_with` (judged) | 6 |
| **Node** | One atomic claim with its classification, links and status | 4 |
| **Pending** | A block whose `atomized_hash` differs from its `text_hash` | 4 |
| **Provisional** | A verdict involving an ambiguous node: kept, but marked | 6 |
| **Q-ATOM / Q-DESC / Q-TERM / Q-PAIR** | The four questions the model is asked | 3 |
| **Retrieval sources S1–S8** | The evidence rules that propose candidate pairs, each worth fixed points | 6 |
| **Round** | One `sddc compile` of a multi-run compile; ends at the cap, a session limit, or completion | 2 |
| **Scope selector** | A constraint's families, terms, categories and layers | 5 |
| **Stale** | Needs re-checking because a judged neighbour was edited or deleted | 6, 7 |
| **Status** | `conflict` > `ambiguous` > `stale` > `unchecked` > `validated`, derived, never set | 6 |
| **Suppressed** | A duplication/subsumption verdict the document's form explains, not recorded as a conflict | 6 |
| **Term** | A named thing the specs talk about, in `.sdd/terms.jsonl` (`term:share_link`) | 5 |
| **Views** | Generated Markdown in `.sdd/views/`: the map, family cards, the conflicts list | 8 |
