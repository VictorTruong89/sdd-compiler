# NOTES

Build of LINGORA (`lingora`) from `spec/` (export `store_hash` sha256:981ec6dc…; 517 checklist ids, 19 unsettled contradictions — the export was made with `--allow-open`, so each one below was decided here).

## What is here

- `lingora/` — the importable package (flat layout, pure Python, **standard library only**: no click, no NLTK, no snowball package; none of these are installed and nothing is installed at judge time).
- `pyproject.toml` — packaging metadata for an editable install (optional; `/app` on the import path is enough).
- `tests/` — pytest suite (`python3 -m pytest -q tests`): 89 tests, all passing. Tests build a small packaged-data tree in a temp directory, so they need no data outside the repo.
- `spec/` — untouched.

Packaged data (Punkt models, perceptron tagger, universal tagset map, stopword lists, WordNet) is **not shipped**. Point `lingora.data.path` (or the `LINGORA_DATA` environment variable, `os.pathsep`-separated) at a directory laid out as in pack 06. Without it, paths that need a model raise `ResourceNotFoundError`, as the spec requires.

## Disagreements in the spec and what was built

Each item quotes both sides (export claim id, pack, text) and says what the code does. Where a conflict is marked UNSETTLED in `spec/MAP.md`, the CF id is given. Rule used: the more specific statement for the case wins; for a default value the PRD's behaviour text wins over the Interface Contract's signature note, except where the Contract's shape/refusal rule is explicit.

1. **CF-000001 — straight `"` at start of text.** Pack 22 N-000094 (Treebank: a straight double quote at the start of the text becomes the opening-quote token ``) vs pack 22 N-000106 (recommended tokenizer: a straight double quote at the very start becomes the closing-quote token ''). **Built:** opening `` for both tokenizers (the Treebank rule; the common Penn Treebank output).
2. **CF-000008 / CF-000039 / CF-000072 — accuracy on lists of different length.** Pack 15 / 28 N-000331 ("for lists of different lengths it is the fraction over the positions both lists have") vs pack 15 N-000502 ("lists of different lengths make it raise"), pack 28 N-000343, pack 27 N-000318 (does not succeed). **Built:** `ValueError` (three of four statements say it does not succeed).
3. **CF-000016 / CF-000055 / CF-000070 — transposition in edit distance.** Pack 15/28 N-000325 (unrestricted Damerau–Levenshtein) and N-000327 (characters may be inserted or deleted between the two transposed characters) vs N-000505 (only adjacent characters in both strings may be transposed) and N-000506 (nothing may be inserted or deleted between them). **Built:** unrestricted Damerau–Levenshtein (Lowrance–Wagner); the adjacency restriction is not built. Without `transpositions=True` it is plain Levenshtein with `substitution_cost`.
4. **CF-000028 — touching chunk matches.** Pack 25 N-000240 ("two matches that touch are two separate chunks") vs N-000242 ("chunks that touch, with no token between them, are joined into one chunk"). **Built:** touching matches produced by the same chunk rule are joined (the N-000242 behaviour, which is how NLTK's `}{` join works).
5. **CF-000038 — f-measure with disjoint sets.** Pack 28 N-000334 ("0 when precision or recall is 0") vs N-000346 (no number when the sets share no element). **Built:** `None` when the sets share no element or either is empty (the boundary rule); the zero-precision formula is not reached for disjoint sets.
6. **CF-000054 — tweet lowercasing and emoticons.** Pack 19 N-000067 / pack 22 N-000125 ("lowercases its tokens"; "tokens are lowercased, except emoticons"). **Built:** emoticons keep their case when `preserve_case=False`; everything else is lowercased.
7. **CF-000073 — Porter Step 1a.** Pack 23 N-000158 (four-letter `-ies` → `-ie`, the LINGORA extension) vs Pack 09 N-000424 (`PorterStemmer` applies Step 1a "as published", so *ties* → *ti*). **Built:** default mode (LINGORA extensions, the PRD's definition of the default) gives `ties → tie`; `ORIGINAL_ALGORITHM` mode gives `ties → ti`.
8. **CF-000077 — `discard_empty` default.** Pack 22 N-000118 ("on by default") vs pack 07 N-000407 ("off unless the caller passes `discard_empty=True`"). **Built:** on by default (PRD); a caller can pass `discard_empty=False`.
9. **CF-000083 — *cannot*.** Pack 22 N-000102 (fused forms, including *cannot*, are split) vs N-000110 (recommended tokenizer keeps *cannot* as one token). **Built:** both hold, each in its own tokenizer: Penn Treebank `TreebankWordTokenizer` gives `can not`; `word_tokenize` (recommended) keeps `cannot`.
10. **CF-000086 — precision/recall argument types.** Pack 28 N-000332 (a list or tuple is read as the set of its elements) vs N-000345 (lists, tuples and other non-set collections are refused) and pack 15 N-000508–509 (sets required). **Built:** refused with `TypeError` (the Contract and the boundary rule agree).
11. **CF-000087 — BLEU default weights.** Pack 28 N-000338 (equal weights on unigrams through 4-grams) vs pack 15 N-000515 (omitted weights cover unigrams and bigrams; longer n-grams not scored). **Built:** `weights=(0.25, 0.25, 0.25, 0.25)` (the PRD).
12. **CF-000088 — string given as tree children.** Pack 26 N-000282 (a string in place of the child list is a single leaf) vs N-000288 (building a tree from a label and a string is refused) and pack 13 N-000486–487. **Built:** refused with `TypeError`.
13. **CF-000089 — quoted empty terminal in generation.** Pack 26 N-000279 (a quoted empty string contributes an empty-string token) vs pack 12 N-000480 (a terminal that is the empty string adds no token). **Built:** an empty-string token `""` (the PRD); an empty production contributes nothing.
14. **CF-000090 — token no production produces.** Pack 26 N-000267 (such a token list gives no parse, like any underivable list) vs N-000292 (parser does not succeed). **Built:** raises `UnsupportedError` (a `ValueError`) at the call; a covered-but-underivable token list gives an empty iterator.
15. **CF-000091 — `to_lowercase` default.** Pack 09 N-000426 / Interface Contract (`to_lowercase` defaults to `False`) vs pack 23 N-000154 (lowercased first unless the caller turns lowercasing off). **Built:** default `True` (PRD); `to_lowercase=False` keeps case.
16. **Not flagged by the export — PRD FP-07 contradicts itself on list arguments** (see 10) and **Porter default mode** described two ways (see 7 and 15); both resolved as above.
17. **Not flagged — Lancaster rule table.** The PRD requires "the standard rule table published with" Paice/Husk; the table was not available here and was reproduced from memory. Results are plausible but not verified (`maximum → maxim`, `provision → provid`, but `string → str`). Treat Lancaster as unverified.
18. **Not flagged — chink/chunk order inside one clause.** Pack 25 N-000246–249 describe cascaded clauses; they were built as NLTK-style cascades (a later clause may match earlier chunks as units; chinking only touches chunks of its own clause).

## Judgement calls not fixed by the spec

- Snowball: only `english` (Porter2) and `porter` (the original algorithm) are implemented. The other 14 listed names are validated and the constructor raises `NotImplementedError` with the name in the message. Stopword lists load for every listed name; the stemmer itself still raises for the unimplemented languages.
- Named-entity chunker: the resource gate raises when the model or wordlist is absent (N-000257, N-000452); with resources present it raises `NotImplementedError`.
- WordNet lemmatizer: construction raises when WordNet is absent; `lemmatize` raises `NotImplementedError` otherwise.
- ARLSTem / ARLSTem2 exist as classes but `stem` raises `NotImplementedError` (their results are outside the spec).
- Exceptions: `LingoraError` base; `ResourceNotFoundError` (a `LookupError`) for missing packaged data; `UnsupportedError` (a `ValueError`) for unsupported arguments and unknown tokens; `ParseError` for malformed grammar/tree text.
- `accuracy` (classifier) and `accuracy` (metrics) raise `ValueError` on an empty list (no number is defined).
- Shift-reduce: a production with an empty right-hand side is never reduced (it would loop); the pass is greedy with no backtracking, so `John saw the dog` with the test grammar yields no tree (it reduces `V` to `VP` too early), as the spec's description implies.
- Chunk root label: `S`.
- Data finder initial `data.path`: `$LINGORA_DATA` entries, then `~/lingora_data`, `/usr/share/lingora`, `/usr/local/share/lingora`.
- CLI: stdlib `argparse`; options `-l/--language` (default `english`), `-d/--delimiter` (default one space), `-e/--encoding`. Exit status 1 on failure, 2 on bad arguments; the Punkt model is checked before any output.
- Punkt: a reimplementation of the Punkt decision rules over the packaged parameters (abbreviation types, sentence starters, collocations, orthographic context), not a byte-for-byte port; it has not been run against the real English model.
- Averaged perceptron tagger: feature templates and greedy decoding follow the textblob-aptagger / NLTK perceptron design, reproduced from memory; not run against the real model. Russian universal mapping is a fixed RNC→universal table.
- Decision tree: ID3 with information gain; a featureset's absent feature is the value `None`.
- Naive Bayes: additive (0.5) smoothing per feature value; features never seen in training are ignored.

## Checklist accounting

Every id in `spec/CHECKLIST.md` (517) is listed below with one status:

- `tested` — a named test `test_N_xxxxxx…` in `tests/` covers it.
- `implemented` — the code path exists (the id is covered by a `# spec:` marker in the module); no dedicated test.
- `implemented (partial)` — part of what the id says is built; the stated remainder is named in the note.
- `implemented (unverified)` — built, but its numeric results were reproduced without the real packaged resource or the published table, so they are not checked against a reference.
- `not done` — with the reason in the note.

Module docstrings carry `# spec: N-…` markers for the ids they implement; the tests name the ids they check.

## Status summary

- tested: 84; implemented: 399; partial: 9; unverified: 8; not done: 17 (non-goals and out-of-scope items, Snowball languages other than english/porter, Dutch, the named-entity model, WordNet `lemmatize`, ISRI/Cistem/RSLP).

## Table

| Id | Pack | Status | Where | Test | Note |
|---|---|---|---|---|---|
| N-000353 | 02 | implemented | lingora/ (flat package, stdlib only) |  |  |
| N-000354 | 02 | implemented | lingora/ (flat package, stdlib only) |  |  |
| N-000355 | 02 | implemented | lingora/ (flat package, stdlib only) |  |  |
| N-000356 | 02 | implemented | lingora/ (flat package, stdlib only) |  |  |
| N-000357 | 03 | implemented | lingora/ (flat package, stdlib only); pyproject.toml |  |  |
| N-000358 | 03 | implemented | lingora/ (flat package, stdlib only); pyproject.toml |  |  |
| N-000359 | 03 | implemented | lingora/ (flat package, stdlib only); pyproject.toml |  |  |
| N-000360 | 03 | implemented | lingora/ (flat package, stdlib only); pyproject.toml |  |  |
| N-000361 | 03 | implemented | lingora/ (flat package, stdlib only); pyproject.toml |  |  |
| N-000362 | 03 | implemented | lingora/ (flat package, stdlib only); pyproject.toml |  |  |
| N-000363 | 03 | implemented | lingora/ (flat package, stdlib only); pyproject.toml |  |  |
| N-000364 | 03 | implemented | lingora/ (flat package, stdlib only); pyproject.toml |  |  |
| N-000365 | 03 | implemented | lingora/ (flat package, stdlib only); pyproject.toml |  |  |
| N-000366 | 03 | implemented | lingora/ (flat package, stdlib only); pyproject.toml |  |  |
| N-000367 | 03 | implemented | lingora/ (flat package, stdlib only); pyproject.toml |  |  |
| N-000368 | 03 | implemented | lingora/ (flat package, stdlib only); pyproject.toml |  |  |
| N-000369 | 03 | implemented | lingora/ (flat package, stdlib only); pyproject.toml |  |  |
| N-000370 | 03 | implemented | lingora/ (flat package, stdlib only); pyproject.toml |  |  |
| N-000371 | 05 | implemented | lingora/errors.py; all modules |  |  |
| N-000372 | 05 | implemented | lingora/errors.py; all modules |  |  |
| N-000373 | 05 | implemented | lingora/errors.py; all modules |  |  |
| N-000374 | 05 | implemented | lingora/errors.py; all modules |  |  |
| N-000375 | 05 | implemented | lingora/errors.py; all modules |  |  |
| N-000376 | 05 | implemented | lingora/errors.py; all modules |  |  |
| N-000377 | 05 | implemented | lingora/errors.py; all modules |  |  |
| N-000378 | 05 | implemented | lingora/errors.py; all modules |  |  |
| N-000379 | 05 | implemented | lingora/errors.py; all modules |  |  |
| N-000380 | 05 | implemented | lingora/errors.py; all modules |  |  |
| N-000381 | 05 | implemented | lingora/errors.py; all modules |  |  |
| N-000382 | 05 | implemented | lingora/errors.py; all modules |  |  |
| N-000383 | 05 | implemented | lingora/errors.py; all modules |  |  |
| N-000384 | 05 | implemented | lingora/errors.py; all modules |  |  |
| N-000385 | 06 | tested | lingora/data.py | test_data_cli.py |  |
| N-000386 | 06 | tested | lingora/data.py | test_data_cli.py |  |
| N-000387 | 06 | implemented | lingora/data.py |  |  |
| N-000388 | 06 | implemented | lingora/data.py |  |  |
| N-000389 | 06 | implemented | lingora/data.py |  |  |
| N-000390 | 06 | implemented | lingora/data.py |  |  |
| N-000391 | 06 | implemented | lingora/data.py |  |  |
| N-000392 | 06 | implemented | lingora/data.py |  |  |
| N-000393 | 06 | implemented | lingora/data.py |  |  |
| N-000394 | 06 | implemented | lingora/data.py |  |  |
| N-000395 | 06 | implemented | lingora/data.py |  |  |
| N-000396 | 06 | implemented | lingora/data.py |  |  |
| N-000397 | 06 | implemented | lingora/data.py |  |  |
| N-000398 | 06 | tested | lingora/data.py | test_data_cli.py |  |
| N-000399 | 06 | implemented | lingora/data.py |  |  |
| N-000400 | 06 | implemented | lingora/data.py |  |  |
| N-000401 | 06 | implemented | lingora/data.py |  |  |
| N-000402 | 06 | implemented | lingora/data.py |  |  |
| N-000403 | 07 | implemented | lingora/tokenize.py |  |  |
| N-000404 | 07 | implemented | lingora/tokenize.py |  |  |
| N-000405 | 07 | tested | lingora/tokenize.py | test_tokenize.py |  |
| N-000406 | 07 | implemented | lingora/tokenize.py |  |  |
| N-000407 | 07 | implemented | lingora/tokenize.py |  |  |
| N-000408 | 07 | implemented | lingora/tokenize.py |  |  |
| N-000409 | 07 | implemented | lingora/tokenize.py |  |  |
| N-000410 | 07 | implemented | lingora/tokenize.py |  |  |
| N-000411 | 07 | implemented | lingora/tokenize.py |  |  |
| N-000412 | 07 | implemented | lingora/tokenize.py |  |  |
| N-000413 | 07 | implemented | lingora/tokenize.py |  |  |
| N-000414 | 08 | tested | lingora/cli.py | test_data_cli.py |  |
| N-000415 | 08 | implemented | lingora/cli.py |  |  |
| N-000416 | 08 | implemented | lingora/cli.py |  |  |
| N-000417 | 08 | tested | lingora/cli.py | test_data_cli.py |  |
| N-000418 | 08 | implemented | lingora/cli.py |  |  |
| N-000419 | 08 | implemented | lingora/cli.py |  |  |
| N-000420 | 08 | tested | lingora/cli.py | test_data_cli.py |  |
| N-000421 | 09 | implemented | lingora/stem.py |  |  |
| N-000422 | 09 | implemented | lingora/stem.py |  |  |
| N-000423 | 09 | implemented | lingora/stem.py |  |  |
| N-000424 | 09 | implemented | lingora/stem.py |  |  |
| N-000425 | 09 | implemented | lingora/stem.py |  |  |
| N-000426 | 09 | implemented | lingora/stem.py |  |  |
| N-000427 | 09 | implemented | lingora/stem.py |  |  |
| N-000428 | 09 | implemented | lingora/stem.py |  |  |
| N-000429 | 09 | implemented | lingora/stem.py |  |  |
| N-000430 | 09 | implemented | lingora/stem.py |  |  |
| N-000431 | 09 | implemented | lingora/stem.py |  |  |
| N-000432 | 09 | implemented (partial) | lingora/stem.py |  | raises when WordNet is not visible; lemmatize() itself not implemented |
| N-000433 | 10 | implemented | lingora/tag.py |  |  |
| N-000434 | 10 | implemented | lingora/tag.py |  |  |
| N-000435 | 10 | implemented | lingora/tag.py |  |  |
| N-000436 | 10 | implemented | lingora/tag.py |  |  |
| N-000437 | 10 | implemented | lingora/tag.py |  |  |
| N-000438 | 10 | implemented | lingora/tag.py |  |  |
| N-000439 | 10 | implemented | lingora/tag.py |  |  |
| N-000440 | 10 | implemented | lingora/tag.py |  |  |
| N-000441 | 10 | implemented | lingora/tag.py |  |  |
| N-000442 | 10 | tested | lingora/tag.py | test_tag.py |  |
| N-000443 | 10 | tested | lingora/tag.py | test_tag.py |  |
| N-000444 | 10 | implemented | lingora/tag.py |  |  |
| N-000445 | 10 | implemented | lingora/tag.py |  |  |
| N-000446 | 11 | implemented | lingora/chunk.py |  |  |
| N-000447 | 11 | implemented | lingora/chunk.py |  |  |
| N-000448 | 11 | implemented | lingora/chunk.py |  |  |
| N-000449 | 11 | implemented | lingora/chunk.py |  |  |
| N-000450 | 11 | implemented | lingora/chunk.py |  |  |
| N-000451 | 11 | implemented | lingora/chunk.py |  |  |
| N-000452 | 11 | implemented | lingora/chunk.py |  |  |
| N-000453 | 11 | implemented | lingora/chunk.py |  |  |
| N-000454 | 11 | implemented | lingora/chunk.py |  |  |
| N-000455 | 11 | implemented | lingora/chunk.py |  | Tree result; root label is "S" |
| N-000456 | 11 | implemented | lingora/chunk.py |  |  |
| N-000457 | 11 | implemented | lingora/chunk.py |  |  |
| N-000458 | 11 | implemented | lingora/chunk.py |  |  |
| N-000459 | 11 | implemented | lingora/chunk.py |  |  |
| N-000460 | 11 | implemented | lingora/chunk.py |  |  |
| N-000461 | 12 | implemented | lingora/grammar.py; lingora/parse/ |  |  |
| N-000462 | 12 | implemented | lingora/grammar.py; lingora/parse/ |  |  |
| N-000463 | 12 | implemented | lingora/grammar.py; lingora/parse/ |  |  |
| N-000464 | 12 | implemented | lingora/grammar.py; lingora/parse/ |  |  |
| N-000465 | 12 | implemented | lingora/grammar.py; lingora/parse/ |  |  |
| N-000466 | 12 | implemented | lingora/grammar.py; lingora/parse/ |  |  |
| N-000467 | 12 | implemented | lingora/grammar.py; lingora/parse/ |  |  |
| N-000468 | 12 | implemented | lingora/grammar.py; lingora/parse/ |  |  |
| N-000469 | 12 | tested | lingora/grammar.py; lingora/parse/ | test_parse_tree.py |  |
| N-000470 | 12 | implemented | lingora/grammar.py; lingora/parse/ |  |  |
| N-000471 | 12 | implemented | lingora/grammar.py; lingora/parse/ |  |  |
| N-000472 | 12 | implemented | lingora/grammar.py; lingora/parse/ |  |  |
| N-000473 | 12 | implemented | lingora/grammar.py; lingora/parse/ |  |  |
| N-000474 | 12 | implemented | lingora/grammar.py; lingora/parse/ |  |  |
| N-000475 | 12 | implemented | lingora/grammar.py; lingora/parse/ |  |  |
| N-000476 | 12 | implemented | lingora/grammar.py; lingora/parse/ |  |  |
| N-000477 | 12 | implemented | lingora/grammar.py; lingora/parse/ |  |  |
| N-000478 | 12 | implemented | lingora/grammar.py; lingora/parse/ |  |  |
| N-000479 | 12 | implemented | lingora/grammar.py; lingora/parse/ |  |  |
| N-000480 | 12 | implemented | lingora/grammar.py; lingora/parse/ |  |  |
| N-000481 | 13 | implemented | lingora/tree.py |  |  |
| N-000482 | 13 | implemented | lingora/tree.py |  |  |
| N-000483 | 13 | implemented | lingora/tree.py |  |  |
| N-000484 | 13 | implemented | lingora/tree.py |  |  |
| N-000485 | 13 | implemented | lingora/tree.py |  |  |
| N-000486 | 13 | implemented | lingora/tree.py |  |  |
| N-000487 | 13 | tested | lingora/tree.py | test_parse_tree.py |  |
| N-000488 | 13 | implemented | lingora/tree.py |  |  |
| N-000489 | 13 | tested | lingora/tree.py | test_parse_tree.py |  |
| N-000490 | 13 | implemented | lingora/tree.py |  |  |
| N-000491 | 13 | implemented | lingora/tree.py |  |  |
| N-000492 | 14 | implemented | lingora/classify.py |  |  |
| N-000493 | 14 | implemented | lingora/classify.py |  |  |
| N-000494 | 14 | implemented | lingora/classify.py |  |  |
| N-000495 | 14 | implemented | lingora/classify.py |  |  |
| N-000496 | 14 | implemented | lingora/classify.py |  |  |
| N-000497 | 14 | implemented | lingora/classify.py |  |  |
| N-000498 | 15 | implemented | lingora/metrics.py; lingora/translate.py |  |  |
| N-000499 | 15 | implemented | lingora/metrics.py; lingora/translate.py |  |  |
| N-000500 | 15 | implemented | lingora/metrics.py; lingora/translate.py |  |  |
| N-000501 | 15 | implemented | lingora/metrics.py; lingora/translate.py |  |  |
| N-000502 | 15 | implemented | lingora/metrics.py; lingora/translate.py |  |  |
| N-000503 | 15 | implemented | lingora/metrics.py; lingora/translate.py |  |  |
| N-000504 | 15 | implemented | lingora/metrics.py; lingora/translate.py |  |  |
| N-000505 | 15 | implemented | lingora/metrics.py; lingora/translate.py |  |  |
| N-000506 | 15 | implemented | lingora/metrics.py; lingora/translate.py |  |  |
| N-000507 | 15 | implemented | lingora/metrics.py; lingora/translate.py |  |  |
| N-000508 | 15 | implemented | lingora/metrics.py; lingora/translate.py |  |  |
| N-000509 | 15 | implemented | lingora/metrics.py; lingora/translate.py |  |  |
| N-000510 | 15 | implemented | lingora/metrics.py; lingora/translate.py |  |  |
| N-000511 | 15 | implemented | lingora/metrics.py; lingora/translate.py |  |  |
| N-000512 | 15 | implemented | lingora/metrics.py; lingora/translate.py |  |  |
| N-000513 | 15 | implemented | lingora/metrics.py; lingora/translate.py |  |  |
| N-000514 | 15 | implemented | lingora/metrics.py; lingora/translate.py |  |  |
| N-000515 | 15 | implemented | lingora/metrics.py; lingora/translate.py |  |  |
| N-000516 | 15 | implemented | lingora/metrics.py; lingora/translate.py |  |  |
| N-000517 | 15 | implemented | lingora/metrics.py; lingora/translate.py |  |  |
| N-000001 | 16 | implemented | lingora/ (whole package) |  |  |
| N-000002 | 16 | implemented | lingora/ (whole package) |  |  |
| N-000003 | 16 | implemented | lingora/ (whole package) |  |  |
| N-000004 | 16 | implemented | lingora/ (whole package) |  |  |
| N-000005 | 16 | implemented | lingora/ (whole package) |  |  |
| N-000006 | 16 | implemented | lingora/ (whole package) |  |  |
| N-000007 | 16 | implemented | lingora/ (whole package) |  |  |
| N-000008 | 16 | implemented | lingora/ (whole package) |  |  |
| N-000009 | 16 | implemented | lingora/ (whole package) |  |  |
| N-000010 | 16 | implemented | lingora/ (whole package) |  |  |
| N-000011 | 16 | implemented | lingora/ (whole package) |  |  |
| N-000012 | 16 | implemented | lingora/ (whole package) |  |  |
| N-000013 | 16 | implemented | lingora/ (whole package) |  |  |
| N-000014 | 16 | implemented | lingora/ (whole package) |  |  |
| N-000015 | 16 | implemented | lingora/ (whole package) |  |  |
| N-000016 | 16 | implemented | lingora/ (whole package) |  |  |
| N-000017 | 16 | implemented | lingora/ (whole package) |  |  |
| N-000018 | 16 | implemented | lingora/ (whole package) |  |  |
| N-000019 | 16 | not done | lingora/ (whole package) |  | packaged corpora / data finder beyond locating models: outside this specification (not a feature point) |
| N-000020 | 16 | not done | lingora/ (whole package) |  | packaged corpora / data finder beyond locating models: outside this specification (not a feature point) |
| N-000021 | 16 | not done | lingora/ (whole package) |  | packaged corpora / data finder beyond locating models: outside this specification (not a feature point) |
| N-000022 | 17 | implemented | lingora/ (term meanings in the modules above) |  |  |
| N-000023 | 17 | implemented | lingora/ (term meanings in the modules above) |  |  |
| N-000024 | 17 | implemented | lingora/ (term meanings in the modules above) |  |  |
| N-000025 | 17 | implemented | lingora/ (term meanings in the modules above) |  |  |
| N-000026 | 17 | implemented | lingora/ (term meanings in the modules above) |  |  |
| N-000027 | 17 | implemented | lingora/ (term meanings in the modules above) |  |  |
| N-000028 | 17 | implemented | lingora/ (term meanings in the modules above) |  |  |
| N-000029 | 18 | implemented | lingora/ (public surface) |  |  |
| N-000030 | 18 | implemented | lingora/ (public surface) |  |  |
| N-000031 | 18 | implemented | lingora/ (public surface) |  |  |
| N-000032 | 18 | implemented | lingora/ (public surface) |  |  |
| N-000033 | 18 | implemented | lingora/ (public surface) |  |  |
| N-000034 | 18 | implemented | lingora/ (public surface) |  |  |
| N-000035 | 18 | implemented | lingora/ (public surface) |  |  |
| N-000036 | 18 | implemented | lingora/ (public surface) |  |  |
| N-000037 | 18 | implemented | lingora/ (public surface) |  |  |
| N-000038 | 18 | implemented | lingora/ (public surface) |  |  |
| N-000039 | 18 | implemented | lingora/ (public surface) |  |  |
| N-000040 | 18 | implemented | lingora/ (public surface) |  |  |
| N-000041 | 18 | implemented | lingora/ (public surface) |  |  |
| N-000042 | 18 | implemented | lingora/ (public surface) |  |  |
| N-000043 | 18 | implemented | lingora/ (public surface) |  |  |
| N-000044 | 18 | implemented | lingora/ (public surface) |  |  |
| N-000045 | 18 | implemented | lingora/ (public surface) |  |  |
| N-000046 | 18 | implemented | lingora/ (public surface) |  |  |
| N-000047 | 18 | implemented | lingora/ (public surface) |  |  |
| N-000048 | 19 | implemented | lingora/data.py; lingora/tokenize.py (Unicode) |  |  |
| N-000049 | 19 | implemented | lingora/data.py; lingora/tokenize.py (Unicode) |  |  |
| N-000050 | 19 | implemented | lingora/data.py; lingora/tokenize.py (Unicode) |  |  |
| N-000051 | 19 | implemented | lingora/data.py; lingora/tokenize.py (Unicode) |  |  |
| N-000052 | 19 | implemented | lingora/data.py; lingora/tokenize.py (Unicode) |  |  |
| N-000053 | 19 | implemented | lingora/data.py; lingora/tokenize.py (Unicode) |  |  |
| N-000054 | 19 | implemented | lingora/data.py; lingora/tokenize.py (Unicode) |  |  |
| N-000055 | 19 | implemented | lingora/data.py; lingora/tokenize.py (Unicode) |  |  |
| N-000056 | 19 | implemented | lingora/data.py; lingora/tokenize.py (Unicode) |  |  |
| N-000057 | 19 | implemented | lingora/data.py; lingora/tokenize.py (Unicode) |  |  |
| N-000058 | 19 | implemented | lingora/data.py; lingora/tokenize.py (Unicode) |  |  |
| N-000059 | 19 | implemented | lingora/data.py; lingora/tokenize.py (Unicode) |  |  |
| N-000060 | 19 | implemented | lingora/data.py; lingora/tokenize.py (Unicode) |  |  |
| N-000061 | 19 | implemented | lingora/data.py; lingora/tokenize.py (Unicode) |  |  |
| N-000062 | 19 | implemented | lingora/data.py; lingora/tokenize.py (Unicode) |  |  |
| N-000063 | 19 | implemented | lingora/data.py; lingora/tokenize.py (Unicode) |  |  |
| N-000064 | 19 | implemented | lingora/data.py; lingora/tokenize.py (Unicode) |  |  |
| N-000065 | 19 | implemented | lingora/data.py; lingora/tokenize.py (Unicode) |  |  |
| N-000066 | 19 | implemented | lingora/data.py; lingora/tokenize.py (Unicode) |  |  |
| N-000067 | 19 | implemented | lingora/data.py; lingora/tokenize.py (Unicode) |  |  |
| N-000068 | 19 | implemented | lingora/data.py; lingora/tokenize.py (Unicode) |  |  |
| N-000069 | 20 | implemented | lingora/__init__.py |  |  |
| N-000070 | 20 | implemented | lingora/__init__.py |  |  |
| N-000071 | 20 | implemented | lingora/__init__.py |  |  |
| N-000072 | 21 | not done | — |  | non-goal of the PRD |
| N-000073 | 21 | not done | — |  | non-goal of the PRD |
| N-000074 | 21 | not done | — |  | non-goal of the PRD |
| N-000075 | 21 | not done | — |  | non-goal of the PRD |
| N-000076 | 21 | not done | — |  | non-goal of the PRD |
| N-000077 | 21 | not done | — |  | non-goal of the PRD |
| N-000078 | 21 | not done | — |  | non-goal of the PRD |
| N-000079 | 21 | not done | — |  | non-goal of the PRD |
| N-000080 | 21 | not done | — |  | non-goal of the PRD |
| N-000081 | 22 | implemented | lingora/tokenize.py; lingora/punkt.py; lingora/cli.py |  |  |
| N-000082 | 22 | implemented | lingora/tokenize.py; lingora/punkt.py; lingora/cli.py |  |  |
| N-000083 | 22 | implemented | lingora/tokenize.py; lingora/punkt.py; lingora/cli.py |  |  |
| N-000084 | 22 | implemented | lingora/tokenize.py; lingora/punkt.py; lingora/cli.py |  |  |
| N-000085 | 22 | implemented | lingora/tokenize.py; lingora/punkt.py; lingora/cli.py |  |  |
| N-000086 | 22 | implemented | lingora/tokenize.py; lingora/punkt.py; lingora/cli.py |  |  |
| N-000087 | 22 | implemented | lingora/tokenize.py; lingora/punkt.py; lingora/cli.py |  |  |
| N-000088 | 22 | implemented | lingora/tokenize.py; lingora/punkt.py; lingora/cli.py |  |  |
| N-000089 | 22 | tested | lingora/tokenize.py; lingora/punkt.py; lingora/cli.py | test_tokenize.py |  |
| N-000090 | 22 | implemented | lingora/tokenize.py; lingora/punkt.py; lingora/cli.py |  |  |
| N-000091 | 22 | implemented | lingora/tokenize.py; lingora/punkt.py; lingora/cli.py |  |  |
| N-000092 | 22 | tested | lingora/tokenize.py; lingora/punkt.py; lingora/cli.py | test_tokenize.py |  |
| N-000093 | 22 | implemented | lingora/tokenize.py; lingora/punkt.py; lingora/cli.py |  |  |
| N-000094 | 22 | implemented | lingora/tokenize.py; lingora/punkt.py; lingora/cli.py |  |  |
| N-000095 | 22 | implemented | lingora/tokenize.py; lingora/punkt.py; lingora/cli.py |  |  |
| N-000096 | 22 | implemented | lingora/tokenize.py; lingora/punkt.py; lingora/cli.py |  |  |
| N-000097 | 22 | implemented | lingora/tokenize.py; lingora/punkt.py; lingora/cli.py |  |  |
| N-000098 | 22 | implemented | lingora/tokenize.py; lingora/punkt.py; lingora/cli.py |  |  |
| N-000099 | 22 | tested | lingora/tokenize.py; lingora/punkt.py; lingora/cli.py | test_tokenize.py |  |
| N-000100 | 22 | tested | lingora/tokenize.py; lingora/punkt.py; lingora/cli.py | test_tokenize.py |  |
| N-000101 | 22 | implemented | lingora/tokenize.py; lingora/punkt.py; lingora/cli.py |  |  |
| N-000102 | 22 | tested | lingora/tokenize.py; lingora/punkt.py; lingora/cli.py | test_tokenize.py |  |
| N-000103 | 22 | implemented | lingora/tokenize.py; lingora/punkt.py; lingora/cli.py |  |  |
| N-000104 | 22 | implemented | lingora/tokenize.py; lingora/punkt.py; lingora/cli.py |  |  |
| N-000105 | 22 | implemented | lingora/tokenize.py; lingora/punkt.py; lingora/cli.py |  |  |
| N-000106 | 22 | implemented | lingora/tokenize.py; lingora/punkt.py; lingora/cli.py |  |  |
| N-000107 | 22 | tested | lingora/tokenize.py; lingora/punkt.py; lingora/cli.py | test_tokenize.py |  |
| N-000108 | 22 | tested | lingora/tokenize.py; lingora/punkt.py; lingora/cli.py | test_tokenize.py |  |
| N-000109 | 22 | tested | lingora/tokenize.py; lingora/punkt.py; lingora/cli.py | test_tokenize.py |  |
| N-000110 | 22 | implemented | lingora/tokenize.py; lingora/punkt.py; lingora/cli.py |  |  |
| N-000111 | 22 | tested | lingora/tokenize.py; lingora/punkt.py; lingora/cli.py | test_tokenize.py |  |
| N-000112 | 22 | implemented | lingora/tokenize.py; lingora/punkt.py; lingora/cli.py |  |  |
| N-000113 | 22 | tested | lingora/tokenize.py; lingora/punkt.py; lingora/cli.py | test_tokenize.py |  |
| N-000114 | 22 | tested | lingora/tokenize.py; lingora/punkt.py; lingora/cli.py | test_tokenize.py |  |
| N-000115 | 22 | implemented | lingora/tokenize.py; lingora/punkt.py; lingora/cli.py |  |  |
| N-000116 | 22 | tested | lingora/tokenize.py; lingora/punkt.py; lingora/cli.py | test_tokenize.py |  |
| N-000117 | 22 | implemented | lingora/tokenize.py; lingora/punkt.py; lingora/cli.py |  |  |
| N-000118 | 22 | implemented | lingora/tokenize.py; lingora/punkt.py; lingora/cli.py |  |  |
| N-000119 | 22 | tested | lingora/tokenize.py; lingora/punkt.py; lingora/cli.py | test_tokenize.py |  |
| N-000120 | 22 | implemented | lingora/tokenize.py; lingora/punkt.py; lingora/cli.py |  |  |
| N-000121 | 22 | implemented | lingora/tokenize.py; lingora/punkt.py; lingora/cli.py |  |  |
| N-000122 | 22 | tested | lingora/tokenize.py; lingora/punkt.py; lingora/cli.py | test_tokenize.py |  |
| N-000123 | 22 | tested | lingora/tokenize.py; lingora/punkt.py; lingora/cli.py | test_tokenize.py |  |
| N-000124 | 22 | implemented | lingora/tokenize.py; lingora/punkt.py; lingora/cli.py |  |  |
| N-000125 | 22 | tested | lingora/tokenize.py; lingora/punkt.py; lingora/cli.py | test_tokenize.py |  |
| N-000126 | 22 | tested | lingora/tokenize.py; lingora/punkt.py; lingora/cli.py | test_tokenize.py |  |
| N-000127 | 22 | implemented | lingora/tokenize.py; lingora/punkt.py; lingora/cli.py |  |  |
| N-000128 | 22 | implemented | lingora/tokenize.py; lingora/punkt.py; lingora/cli.py |  |  |
| N-000129 | 22 | tested | lingora/tokenize.py; lingora/punkt.py; lingora/cli.py | test_tokenize.py |  |
| N-000130 | 22 | implemented | lingora/tokenize.py; lingora/punkt.py; lingora/cli.py |  |  |
| N-000131 | 22 | implemented | lingora/tokenize.py; lingora/punkt.py; lingora/cli.py |  |  |
| N-000132 | 22 | implemented | lingora/tokenize.py; lingora/punkt.py; lingora/cli.py |  |  |
| N-000133 | 22 | implemented | lingora/tokenize.py; lingora/punkt.py; lingora/cli.py |  |  |
| N-000134 | 22 | implemented | lingora/tokenize.py; lingora/punkt.py; lingora/cli.py |  |  |
| N-000135 | 22 | implemented | lingora/tokenize.py; lingora/punkt.py; lingora/cli.py |  |  |
| N-000136 | 22 | tested | lingora/tokenize.py; lingora/punkt.py; lingora/cli.py | test_tokenize.py |  |
| N-000137 | 22 | tested | lingora/tokenize.py; lingora/punkt.py; lingora/cli.py | test_tokenize.py |  |
| N-000138 | 22 | implemented | lingora/tokenize.py; lingora/punkt.py; lingora/cli.py |  |  |
| N-000139 | 22 | implemented | lingora/tokenize.py; lingora/punkt.py; lingora/cli.py |  |  |
| N-000140 | 23 | implemented | lingora/stem.py |  |  |
| N-000141 | 23 | implemented | lingora/stem.py |  |  |
| N-000142 | 23 | implemented | lingora/stem.py |  |  |
| N-000143 | 23 | implemented (partial) | lingora/stem.py |  | Porter, Lancaster, Snowball, regexp families built; ISRI, Cistem, RSLP not built (results outside this specification) |
| N-000144 | 23 | implemented | lingora/stem.py |  |  |
| N-000145 | 23 | implemented | lingora/stem.py |  |  |
| N-000146 | 23 | implemented | lingora/stem.py |  |  |
| N-000147 | 23 | implemented | lingora/stem.py |  |  |
| N-000148 | 23 | implemented | lingora/stem.py |  |  |
| N-000149 | 23 | implemented | lingora/stem.py |  |  |
| N-000150 | 23 | implemented | lingora/stem.py |  |  |
| N-000151 | 23 | implemented | lingora/stem.py |  |  |
| N-000152 | 23 | tested | lingora/stem.py | test_stem.py |  |
| N-000153 | 23 | tested | lingora/stem.py | test_stem.py |  |
| N-000154 | 23 | tested | lingora/stem.py | test_stem.py |  |
| N-000155 | 23 | tested | lingora/stem.py | test_stem.py |  |
| N-000156 | 23 | tested | lingora/stem.py | test_stem.py |  |
| N-000157 | 23 | implemented | lingora/stem.py |  |  |
| N-000158 | 23 | tested | lingora/stem.py | test_stem.py |  |
| N-000159 | 23 | tested | lingora/stem.py | test_stem.py |  |
| N-000160 | 23 | implemented | lingora/stem.py |  |  |
| N-000161 | 23 | implemented | lingora/stem.py |  |  |
| N-000162 | 23 | tested | lingora/stem.py | test_stem.py |  |
| N-000163 | 23 | implemented | lingora/stem.py |  |  |
| N-000164 | 23 | implemented | lingora/stem.py |  |  |
| N-000165 | 23 | implemented | lingora/stem.py |  |  |
| N-000166 | 23 | implemented | lingora/stem.py |  |  |
| N-000167 | 23 | implemented | lingora/stem.py |  |  |
| N-000168 | 23 | implemented | lingora/stem.py |  |  |
| N-000169 | 23 | implemented | lingora/stem.py |  |  |
| N-000170 | 23 | implemented (unverified) | lingora/stem.py | test_stem.py | Paice/Husk rule table reproduced from memory; not checked against the published table |
| N-000171 | 23 | implemented (unverified) | lingora/stem.py |  | Paice/Husk rule table reproduced from memory; not checked against the published table |
| N-000172 | 23 | implemented (partial) | lingora/stem.py | test_stem.py | Snowball for english and porter built; the other 14 listed languages raise NotImplementedError |
| N-000173 | 23 | not done | lingora/stem.py |  | Dutch Snowball stemmer not built (see N-000172) |
| N-000174 | 23 | implemented | lingora/stem.py |  |  |
| N-000175 | 23 | tested | lingora/stem.py | test_stem.py |  |
| N-000176 | 23 | tested | lingora/stem.py | test_stem.py |  |
| N-000177 | 23 | implemented | lingora/stem.py |  |  |
| N-000178 | 23 | tested | lingora/stem.py | test_stem.py |  |
| N-000179 | 23 | implemented | lingora/stem.py |  |  |
| N-000180 | 23 | implemented | lingora/stem.py |  |  |
| N-000181 | 23 | tested | lingora/stem.py | test_stem.py |  |
| N-000182 | 23 | implemented | lingora/stem.py |  |  |
| N-000183 | 23 | tested | lingora/stem.py | test_stem.py |  |
| N-000184 | 23 | implemented | lingora/stem.py |  |  |
| N-000185 | 23 | tested | lingora/stem.py | test_stem.py |  |
| N-000186 | 23 | implemented | lingora/stem.py |  |  |
| N-000187 | 24 | implemented | lingora/tag.py |  |  |
| N-000188 | 24 | implemented | lingora/tag.py |  |  |
| N-000189 | 24 | implemented (partial) | lingora/tag.py |  | default, unigram, regexp built and tested; bigram/trigram/affix exist as basic taggers, results outside this specification |
| N-000190 | 24 | implemented | lingora/tag.py |  |  |
| N-000191 | 24 | implemented | lingora/tag.py |  |  |
| N-000192 | 24 | implemented | lingora/tag.py |  |  |
| N-000193 | 24 | implemented | lingora/tag.py |  |  |
| N-000194 | 24 | implemented | lingora/tag.py |  |  |
| N-000195 | 24 | implemented | lingora/tag.py |  |  |
| N-000196 | 24 | tested | lingora/tag.py | test_tag.py |  |
| N-000197 | 24 | implemented | lingora/tag.py |  |  |
| N-000198 | 24 | tested | lingora/tag.py | test_tag.py |  |
| N-000199 | 24 | tested | lingora/tag.py | test_tag.py |  |
| N-000200 | 24 | implemented | lingora/tag.py |  |  |
| N-000201 | 24 | implemented | lingora/tag.py |  |  |
| N-000202 | 24 | tested | lingora/tag.py | test_tag.py |  |
| N-000203 | 24 | implemented | lingora/tag.py |  |  |
| N-000204 | 24 | implemented | lingora/tag.py |  |  |
| N-000205 | 24 | tested | lingora/tag.py | test_tag.py |  |
| N-000206 | 24 | implemented | lingora/tag.py |  |  |
| N-000207 | 24 | implemented (unverified) | lingora/tag.py | test_tag.py | algorithm and feature templates reproduced without access to the packaged model; not run against the real resource |
| N-000208 | 24 | implemented (unverified) | lingora/tag.py |  | algorithm and feature templates reproduced without access to the packaged model; not run against the real resource |
| N-000209 | 24 | implemented (unverified) | lingora/tag.py |  | algorithm and feature templates reproduced without access to the packaged model; not run against the real resource |
| N-000210 | 24 | implemented (unverified) | lingora/tag.py |  | algorithm and feature templates reproduced without access to the packaged model; not run against the real resource |
| N-000211 | 24 | implemented (unverified) | lingora/tag.py |  | algorithm and feature templates reproduced without access to the packaged model; not run against the real resource |
| N-000212 | 24 | implemented (unverified) | lingora/tag.py |  | algorithm and feature templates reproduced without access to the packaged model; not run against the real resource |
| N-000213 | 24 | implemented | lingora/tag.py |  |  |
| N-000214 | 24 | implemented | lingora/tag.py |  |  |
| N-000215 | 24 | tested | lingora/tag.py | test_tag.py |  |
| N-000216 | 24 | implemented | lingora/tag.py |  |  |
| N-000217 | 24 | implemented | lingora/tag.py |  |  |
| N-000218 | 24 | implemented | lingora/tag.py |  |  |
| N-000219 | 24 | implemented | lingora/tag.py |  |  |
| N-000220 | 24 | implemented | lingora/tag.py |  |  |
| N-000221 | 24 | implemented | lingora/tag.py |  |  |
| N-000222 | 24 | implemented | lingora/tag.py |  |  |
| N-000223 | 24 | implemented | lingora/tag.py |  |  |
| N-000224 | 24 | tested | lingora/tag.py | test_tag.py |  |
| N-000225 | 24 | implemented | lingora/tag.py |  |  |
| N-000226 | 24 | implemented | lingora/tag.py |  |  |
| N-000227 | 24 | implemented | lingora/tag.py |  |  |
| N-000228 | 25 | implemented | lingora/chunk.py |  |  |
| N-000229 | 25 | implemented | lingora/chunk.py |  |  |
| N-000230 | 25 | implemented | lingora/chunk.py |  |  |
| N-000231 | 25 | implemented (partial) | lingora/chunk.py |  | resource gate built; named-entity model results not built (outside this specification) |
| N-000232 | 25 | implemented | lingora/chunk.py |  |  |
| N-000233 | 25 | tested | lingora/chunk.py | test_tag.py |  |
| N-000234 | 25 | implemented | lingora/chunk.py |  |  |
| N-000235 | 25 | implemented | lingora/chunk.py |  |  |
| N-000236 | 25 | tested | lingora/chunk.py | test_chunk_classify_metrics.py |  |
| N-000237 | 25 | implemented | lingora/chunk.py |  |  |
| N-000238 | 25 | implemented | lingora/chunk.py |  |  |
| N-000239 | 25 | implemented | lingora/chunk.py |  |  |
| N-000240 | 25 | implemented | lingora/chunk.py |  |  |
| N-000241 | 25 | implemented | lingora/chunk.py |  |  |
| N-000242 | 25 | implemented | lingora/chunk.py |  |  |
| N-000243 | 25 | tested | lingora/chunk.py | test_chunk_classify_metrics.py |  |
| N-000244 | 25 | implemented | lingora/chunk.py |  |  |
| N-000245 | 25 | implemented | lingora/chunk.py |  |  |
| N-000246 | 25 | tested | lingora/chunk.py | test_chunk_classify_metrics.py |  |
| N-000247 | 25 | implemented | lingora/chunk.py |  |  |
| N-000248 | 25 | implemented | lingora/chunk.py |  |  |
| N-000249 | 25 | implemented | lingora/chunk.py |  |  |
| N-000250 | 25 | tested | lingora/chunk.py | test_chunk_classify_metrics.py |  |
| N-000251 | 25 | implemented | lingora/chunk.py |  |  |
| N-000252 | 25 | tested | lingora/chunk.py | test_chunk_classify_metrics.py |  |
| N-000253 | 25 | tested | lingora/chunk.py | test_chunk_classify_metrics.py |  |
| N-000254 | 25 | implemented | lingora/chunk.py |  |  |
| N-000255 | 25 | implemented | lingora/chunk.py |  |  |
| N-000256 | 25 | implemented | lingora/chunk.py |  |  |
| N-000257 | 25 | tested | lingora/chunk.py | test_chunk_classify_metrics.py |  |
| N-000258 | 26 | implemented (partial) | lingora/grammar.py; lingora/parse/; lingora/tree.py |  | chart and shift-reduce built; recursive-descent parser is a chart-based stand-in (results outside this specification) |
| N-000259 | 26 | implemented (partial) | lingora/grammar.py; lingora/parse/; lingora/tree.py |  | chart and shift-reduce built; recursive-descent parser is a chart-based stand-in (results outside this specification) |
| N-000260 | 26 | implemented (partial) | lingora/grammar.py; lingora/parse/; lingora/tree.py |  | chart and shift-reduce built; recursive-descent parser is a chart-based stand-in (results outside this specification) |
| N-000261 | 26 | implemented (partial) | lingora/grammar.py; lingora/parse/; lingora/tree.py |  | chart and shift-reduce built; recursive-descent parser is a chart-based stand-in (results outside this specification) |
| N-000262 | 26 | implemented | lingora/grammar.py; lingora/parse/; lingora/tree.py |  |  |
| N-000263 | 26 | implemented | lingora/grammar.py; lingora/parse/; lingora/tree.py |  |  |
| N-000264 | 26 | tested | lingora/grammar.py; lingora/parse/; lingora/tree.py | test_parse_tree.py |  |
| N-000265 | 26 | implemented | lingora/grammar.py; lingora/parse/; lingora/tree.py |  |  |
| N-000266 | 26 | tested | lingora/grammar.py; lingora/parse/; lingora/tree.py | test_parse_tree.py |  |
| N-000267 | 26 | implemented | lingora/grammar.py; lingora/parse/; lingora/tree.py |  |  |
| N-000268 | 26 | implemented | lingora/grammar.py; lingora/parse/; lingora/tree.py |  |  |
| N-000269 | 26 | implemented | lingora/grammar.py; lingora/parse/; lingora/tree.py |  |  |
| N-000270 | 26 | implemented | lingora/grammar.py; lingora/parse/; lingora/tree.py |  |  |
| N-000271 | 26 | implemented | lingora/grammar.py; lingora/parse/; lingora/tree.py |  |  |
| N-000272 | 26 | tested | lingora/grammar.py; lingora/parse/; lingora/tree.py | test_parse_tree.py |  |
| N-000273 | 26 | implemented | lingora/grammar.py; lingora/parse/; lingora/tree.py |  |  |
| N-000274 | 26 | tested | lingora/grammar.py; lingora/parse/; lingora/tree.py | test_parse_tree.py |  |
| N-000275 | 26 | implemented | lingora/grammar.py; lingora/parse/; lingora/tree.py |  |  |
| N-000276 | 26 | tested | lingora/grammar.py; lingora/parse/; lingora/tree.py | test_parse_tree.py |  |
| N-000277 | 26 | implemented | lingora/grammar.py; lingora/parse/; lingora/tree.py |  |  |
| N-000278 | 26 | implemented | lingora/grammar.py; lingora/parse/; lingora/tree.py |  |  |
| N-000279 | 26 | tested | lingora/grammar.py; lingora/parse/; lingora/tree.py | test_parse_tree.py |  |
| N-000280 | 26 | implemented | lingora/grammar.py; lingora/parse/; lingora/tree.py |  |  |
| N-000281 | 26 | tested | lingora/grammar.py; lingora/parse/; lingora/tree.py | test_parse_tree.py |  |
| N-000282 | 26 | implemented | lingora/grammar.py; lingora/parse/; lingora/tree.py |  |  |
| N-000283 | 26 | implemented | lingora/grammar.py; lingora/parse/; lingora/tree.py |  |  |
| N-000284 | 26 | implemented | lingora/grammar.py; lingora/parse/; lingora/tree.py |  |  |
| N-000285 | 26 | implemented | lingora/grammar.py; lingora/parse/; lingora/tree.py |  |  |
| N-000286 | 26 | implemented | lingora/grammar.py; lingora/parse/; lingora/tree.py |  |  |
| N-000287 | 26 | tested | lingora/grammar.py; lingora/parse/; lingora/tree.py | test_parse_tree.py |  |
| N-000288 | 26 | tested | lingora/grammar.py; lingora/parse/; lingora/tree.py | test_parse_tree.py |  |
| N-000289 | 26 | implemented | lingora/grammar.py; lingora/parse/; lingora/tree.py |  |  |
| N-000290 | 26 | implemented | lingora/grammar.py; lingora/parse/; lingora/tree.py |  |  |
| N-000291 | 26 | tested | lingora/grammar.py; lingora/parse/; lingora/tree.py | test_parse_tree.py |  |
| N-000292 | 26 | tested | lingora/grammar.py; lingora/parse/; lingora/tree.py | test_parse_tree.py |  |
| N-000293 | 26 | implemented | lingora/grammar.py; lingora/parse/; lingora/tree.py |  |  |
| N-000294 | 26 | implemented | lingora/grammar.py; lingora/parse/; lingora/tree.py |  |  |
| N-000295 | 27 | implemented | lingora/classify.py |  |  |
| N-000296 | 27 | implemented | lingora/classify.py |  |  |
| N-000297 | 27 | implemented | lingora/classify.py |  |  |
| N-000298 | 27 | implemented | lingora/classify.py |  |  |
| N-000299 | 27 | implemented | lingora/classify.py |  |  |
| N-000300 | 27 | implemented | lingora/classify.py |  |  |
| N-000301 | 27 | implemented | lingora/classify.py |  |  |
| N-000302 | 27 | tested | lingora/classify.py | test_chunk_classify_metrics.py |  |
| N-000303 | 27 | implemented | lingora/classify.py |  |  |
| N-000304 | 27 | implemented | lingora/classify.py |  |  |
| N-000305 | 27 | implemented | lingora/classify.py |  |  |
| N-000306 | 27 | implemented | lingora/classify.py |  |  |
| N-000307 | 27 | implemented | lingora/classify.py |  |  |
| N-000308 | 27 | implemented | lingora/classify.py |  |  |
| N-000309 | 27 | implemented | lingora/classify.py |  |  |
| N-000310 | 27 | tested | lingora/classify.py | test_chunk_classify_metrics.py |  |
| N-000311 | 27 | implemented | lingora/classify.py |  |  |
| N-000312 | 27 | implemented | lingora/classify.py |  |  |
| N-000313 | 27 | implemented | lingora/classify.py |  |  |
| N-000314 | 27 | implemented | lingora/classify.py |  |  |
| N-000315 | 27 | tested | lingora/classify.py | test_chunk_classify_metrics.py |  |
| N-000316 | 27 | implemented | lingora/classify.py |  |  |
| N-000317 | 27 | implemented | lingora/classify.py |  |  |
| N-000318 | 27 | tested | lingora/classify.py | test_chunk_classify_metrics.py |  |
| N-000319 | 28 | implemented | lingora/metrics.py; lingora/translate.py |  |  |
| N-000320 | 28 | implemented | lingora/metrics.py; lingora/translate.py |  |  |
| N-000321 | 28 | implemented | lingora/metrics.py; lingora/translate.py |  |  |
| N-000322 | 28 | tested | lingora/metrics.py; lingora/translate.py | test_chunk_classify_metrics.py |  |
| N-000323 | 28 | implemented | lingora/metrics.py; lingora/translate.py |  |  |
| N-000324 | 28 | implemented | lingora/metrics.py; lingora/translate.py |  |  |
| N-000325 | 28 | implemented | lingora/metrics.py; lingora/translate.py |  |  |
| N-000326 | 28 | implemented | lingora/metrics.py; lingora/translate.py |  |  |
| N-000327 | 28 | implemented | lingora/metrics.py; lingora/translate.py |  |  |
| N-000328 | 28 | tested | lingora/metrics.py; lingora/translate.py | test_chunk_classify_metrics.py |  |
| N-000329 | 28 | implemented | lingora/metrics.py; lingora/translate.py |  |  |
| N-000330 | 28 | tested | lingora/metrics.py; lingora/translate.py | test_chunk_classify_metrics.py |  |
| N-000331 | 28 | implemented | lingora/metrics.py; lingora/translate.py |  |  |
| N-000332 | 28 | tested | lingora/metrics.py; lingora/translate.py | test_chunk_classify_metrics.py |  |
| N-000333 | 28 | implemented | lingora/metrics.py; lingora/translate.py |  |  |
| N-000334 | 28 | implemented | lingora/metrics.py; lingora/translate.py |  |  |
| N-000335 | 28 | tested | lingora/metrics.py; lingora/translate.py | test_chunk_classify_metrics.py |  |
| N-000336 | 28 | implemented | lingora/metrics.py; lingora/translate.py |  |  |
| N-000337 | 28 | implemented | lingora/metrics.py; lingora/translate.py |  |  |
| N-000338 | 28 | implemented | lingora/metrics.py; lingora/translate.py |  |  |
| N-000339 | 28 | tested | lingora/metrics.py; lingora/translate.py | test_chunk_classify_metrics.py |  |
| N-000340 | 28 | implemented | lingora/metrics.py; lingora/translate.py |  |  |
| N-000341 | 28 | tested | lingora/metrics.py; lingora/translate.py | test_chunk_classify_metrics.py |  |
| N-000342 | 28 | implemented | lingora/metrics.py; lingora/translate.py |  |  |
| N-000343 | 28 | implemented | lingora/metrics.py; lingora/translate.py |  |  |
| N-000344 | 28 | tested | lingora/metrics.py; lingora/translate.py | test_chunk_classify_metrics.py |  |
| N-000345 | 28 | implemented | lingora/metrics.py; lingora/translate.py |  |  |
| N-000346 | 28 | implemented | lingora/metrics.py; lingora/translate.py |  |  |
| N-000347 | 28 | implemented | lingora/metrics.py; lingora/translate.py |  |  |
| N-000348 | 28 | implemented | lingora/metrics.py; lingora/translate.py |  |  |
| N-000349 | 29 | not done | — |  | outside this specification (pack 29) |
| N-000350 | 29 | not done | — |  | outside this specification (pack 29) |
| N-000351 | 29 | not done | — |  | outside this specification (pack 29) |
| N-000352 | 29 | not done | — |  | outside this specification (pack 29) |
