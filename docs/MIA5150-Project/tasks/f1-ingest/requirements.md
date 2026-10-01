# F1 (Ingest) — numbered requirement list for scoring

> Source: the **frozen** F1 spec the pilot graph was compiled from
> (`~/sddc-runs/pilot-graph-R000023-specs/specs/F1_ingest/spec.md`), not the current repository copy.
> Scoring is against this list, never the graph's node list (proposal: "Known confound").
> **Test** names the hidden test in `hidden_tests/test_f1_hidden.py`; **audit** means no black-box test
> can decide it, so it is judged by reading the code. In scope: `init`, `ingest`, `status` (task.md).

| # | Requirement | Source | Scored by |
|---|---|---|---|
| R1 | Paragraphs, list items, table body rows and fenced code are blocks with those kinds, correct `lines` and `heading_path` | §4, AC-1.1 | test `test_ac_1_1_*` |
| R2 | Headings produce no block; they set `heading_path` | §4, AC-1.2 | test `test_ac_1_2_*` |
| R3 | A nested list item is its own block, `parent_block` = the outer item, `parent_relation: nested` | AC-1.3, D11 | test `test_ac_1_3_*` |
| R4 | Table body rows carry the header row as `table_header`; no block for header or delimiter | AC-1.4, D4 | test `test_ac_1_4_*` |
| R5 | Content in a blockquote keeps its kind with `in_blockquote: true` | AC-1.5 | test `test_ac_1_5_*` |
| R6 | Code blocks are stored as `code`, pending only when `include_code_blocks` is true | AC-1.6 | test `test_ac_1_6_*` |
| R7 | A further paragraph inside a list item: `parent_relation: continuation`; top-level blocks have both fields null | AC-1.30, D11 | test `test_ac_1_30_*` |
| R8 | Front matter, HTML comments and horizontal rules produce no block | AC-1.7 | test `test_ac_1_7_*` |
| R9 | Re-ingesting an unchanged file reports 0 new/changed/removed; `blocks.jsonl`, `sources.jsonl` byte-identical | AC-1.8 | test `test_ac_1_8_*` |
| R10 | An inserted paragraph is `new`; existing blocks keep ids and are `unchanged` | AC-1.9, P-6 | test `test_ac_1_9_*` |
| R11 | A one-word edit keeps the id and is `changed`; nothing else changes | AC-1.10 | test `test_ac_1_10_*` |
| R12 | A removed block keeps its record with `removed_run`; its id is never reused | AC-1.11, D12 | test `test_ac_1_11_*` |
| R13 | Pending is derived from `atomized_hash` vs `text_hash`, `new` / `changed`, never stored | AC-1.31, D13 | test `test_ac_1_31_*` |
| R14 | Trailing whitespace and CRLF do not change a block; a case change does | AC-1.12, §4 hashing | test `test_ac_1_12_*` |
| R15 | `status --json` prints one JSON object with `run`, `counts` (sources, blocks, pending) and `pending` items | AC-1.21, CT-1.5 | test `test_ac_1_21_*` |
| R16 | A non-UTF-8 file fails the whole ingest with exit 2 naming it; no store file changes | AC-1.22 | test `test_ac_1_22_*` |
| R17 | A path outside the repository root exits 2 | AC-1.23 | test `test_ac_1_23_*` |
| R18 | Any command but `init` without `.sdd/` exits 4 naming `sddc init` | AC-1.24 | test `test_ac_1_24_*` |
| R19 | `init` never overwrites an existing profile | AC-1.25 | test `test_ac_1_25_*` |
| R20 | A second run waits up to 15 s for the lock, then exits 4 without writing | AC-1.26, D9 | **audit** (the lock file's name is not specified) |
| R21 | Block record fields and rules: `B-` + ≥ 6 digits, sorted by id, 1-based inclusive `lines`, verbatim `text`, `sha256:` hash | CT-1.1 | test `test_ct_1_1_*` |
| R22 | Source records `path`, `file_hash`, `last_ingest_run`, sorted by path | CT-1.2 | test `test_ct_1_2_*` |
| R23 | One run record appended per successful run, with the CT-1.3 fields | CT-1.3, §4 | test `test_ct_1_3_*` |
| R24 | `init` writes a profile with `spec_globs`, `exclude_globs`, `include_code_blocks` | CT-1.4 | test `test_ct_1_4_*` |
| R25 | Exit codes: 1 usage, 2 input, 4 store | CT-1.6 | test `test_ct_1_6_*` |
| R26 | Only files matching `spec_globs` and no `exclude_globs` are sources; a named non-source exits 2 | §4 source selection | test `test_source_selection_*` |
| R27 | Identical sources give byte-identical `blocks.jsonl` and `sources.jsonl` | §4 determinism | test `test_determinism_*` |
| R28 | No model call, no network use by the tool | §1 | **audit** |

**Deliberately not scored by test:** `status`'s `graph` object (CT-1.5) — it holds counts from features
out of this task's scope; `blocks` and `show` (CT-1.6) — the task names only `init`, `ingest`, `status`.
Both are stated the same way to both formats.
