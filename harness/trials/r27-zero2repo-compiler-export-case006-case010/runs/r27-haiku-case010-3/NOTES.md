# NOTES

Implementation of the LINGORA specification in `spec/` (read from `spec/MAP.md`; checklist in `spec/CHECKLIST.md`).
`spec/` is unchanged.

## Layout and how to check

- Package: `/app/lingora/` (flat layout). Submodules: `data`, `tokenize`, `stem`, `tag`, `chunk`, `grammar`,
  `parse` (`chart`, `shift_reduce`, `generate`), `tree`, `classify`, `metrics`, `translate`, `cli`, `_punkt`.
- Packaging metadata: `/app/pyproject.toml` (pure Python, no runtime dependencies, Python >= 3.10). No build step is needed;
  `/app` on the import path is enough.
- Tests: `/app/tests/` (30 tests, all passing with `python3 -m pytest -q tests`). Test names carry the spec ids.
- Each implemented id is marked in code with a `# spec: N-...` comment (the table below lists the files).
- Environment note: no third-party packages were available (no `click`, `nltk`, `snowballstemmer`). The CLI uses `argparse`.

## No packaged data is shipped

The packaged resources (Punkt models, the perceptron taggers, the universal tagset tables, the NE chunker, the English wordlist,
stopwords, WordNet) are not in this repository and were not downloaded. Every path that needs them raises
(`lingora.data.ResourceNotFoundError`, a `LookupError`) unless the caller points `lingora.data.path` at a directory that has them.
The data-dependent tests use small synthetic Punkt fixtures written to a temporary directory. The file formats follow the
spec's tables; the real models have not been exercised.

`lingora.data.path` starts as `$LINGORA_DATA` (os.pathsep separated) plus `~/lingora_data`. Lookups read the list at call time.

## Resolved conflicts

The export was made with `--allow-open`, so 13 contradictions have no human verdict. Each is listed with the choice made.
Where two non-contradiction claims disagree, the choice follows the rule in the PRD's *Public surface* preface: the Interface Contract
owns signatures and defaults; the PRD owns what an entry computes.

### Unsettled contradictions (CF ids from `spec/MAP.md`)

- **CF-000001** (`Full_PRD` FP-01, N-000094 vs N-000106). Treebank: a straight `"` at the start of the text opens (as two backticks).
  Recommended tokenizer: a straight `"` at the very start closes (`''`), because N-000106 is the recommended-specific improvement.
- **CF-000008, CF-000039, CF-000072** (accuracy on lists of different lengths: PRD N-000331 says "a fraction over the shared positions";
  PRD N-000343, interface N-000502 and N-000318 say "does not succeed"). Chose: `metrics.accuracy` raises `ValueError`;
  `classify.accuracy` is only over gold pairs, so it has no length problem.
- **CF-000016, CF-000055, CF-000070** (edit distance with transpositions: PRD N-000325/N-000327 say unrestricted Damerau–Levenshtein with
  insertions allowed between the transposed characters; interface N-000505/N-000506 say only adjacent characters, nothing between).
  Chose the interface's rule (optimal string alignment): a transposition needs the two characters adjacent in both strings.
  Example: `edit_distance("ca", "abc", transpositions=True)` is 3 under this rule, not 2.
- **CF-000028** (touching matches in a chunk rule: N-000240 says two separate chunks; N-000242 says touching chunks are joined).
  Chose N-000242 (joined). This matches the usual NLTK behavior.
- **CF-000038** (f-measure: N-000334 says 0 when precision or recall is 0; N-000346 says no number when the sets share nothing).
  Chose N-000346: `f_measure` returns `None` when the sets are empty or share no element. With a shared element, precision and recall
  are both positive, so the "0" case cannot arise.
- **CF-000054** (tweet tokenizer lowercasing: PRD N-000067 says it lowercases unless the caller asks for case; N-000125 says emoticons
  keep their case). Chose: emoticons are never lowercased. Case preservation defaults to **on** (`preserve_case=True`), following
  N-000125's "(it is on by default)"; N-000067 contradicts that default, so I went with the explicit default.
- **CF-000073** (Porter step 1a: N-000158 says a four-letter word ending in `-ies` becomes `-ie`; interface N-000424 says `ties` stems to `ti`).
  Chose N-000158 (`ties` → `tie`), since the interface defers computed behavior to the PRD. The default `PorterStemmer` is the
  LINGORA-extensions mode.
- **CF-000077** (`discard_empty` default: PRD N-000118 says on by default; interface N-000407 says off unless `discard_empty=True`).
  Chose the interface (off by default). So gap-mode tokenization keeps empty pieces unless the caller passes `discard_empty=True`.
- **CF-000083** (`cannot`: PRD N-000102 splits the Treebank fused forms, including `cannot`; N-000110 keeps `cannot` as one token in the
  recommended tokenizer). Chose: Treebank splits `cannot` → `can not`; the recommended tokenizer keeps `cannot`.

### Other cross-pack conflicts (not in the unsettled list)

- **Porter `to_lowercase` default.** Interface N-000426 says it defaults to `False`; PRD N-000154 says the word is lowercased first unless the
  caller turns it off. Chose `False` (the interface owns signature defaults), so `stem` keeps the case it is given.
- **BLEU default weights.** PRD N-000338 says equal weights over unigrams through 4-grams; interface N-000515 says unigrams and bigrams,
  with longer n-grams not scored. Chose the interface: default `weights=(0.5, 0.5)`.
- **Generator and empty terminals.** PRD N-000279 says a quoted empty string contributes an empty-string token; interface N-000480 says a
  terminal that is the empty string adds no token. Chose the interface (no token).
- **Generator ordering and depth.** With `n` and no `depth`, I run an unbounded depth-first search under an expansion budget (20000);
  if the budget is exhausted, I fall back to deepening the derivation bound. `depth` counts productions applied along a derivation.
- **Lancaster rule table.** The spec points to the published table, which I could not reproduce in full. The engine is the
  Paice/Husk one; the rule set is a 42-rule subset (partial, see the table). Results for words the subset does not cover are not
  guaranteed.
- **Chart parser cycles.** Derivations that revisit the same (symbol, span) on one path are cut. Grammars with cycles therefore give finitely many trees.
- **Shift-reduce parser.** Empty productions are not used, and unit-production cycles are cut after a bounded number of reductions.
- **Decision tree.** "Classifies the training examples reaching that node best" is implemented as the number of training examples
  correctly classified by a per-branch majority label.
- **Classifier accuracy and metrics on empty input.** `accuracy([], [])` and `classify.accuracy` on an empty gold list return `0.0`
  (the spec does not define these).
- **`ne_chunk`.** Raises when the model or wordlist is absent (the spec's requirement). When they are present, it raises NotImplementedError (see not done).
- **Punkt.** The sentence splitter applies the Kiss–Strunk decision rules to the packaged parameters. It is a re-implementation written from the spec, not a
  reproduction of any particular library. Paragraph breaks (blank lines) always end a sentence.

## Not done, and why

Statuses below are the ones in the table. "Satisfied by omission" means a MUST NOT (non-goal or out-of-scope item) that the build
meets by not implementing the surface. The per-id table at the end gives every id a status.

- Named-entity chunker (N-000038, N-000231): not done. The resource check is done; the model format is not specified.
- Snowball algorithms for 14 of 16 languages (N-000172): not done. `SnowballStemmer` validates the language name and raises
  NotImplementedError naming it; `english` (Porter2) and `porter` are implemented.
- ISRI, Cistem, RSLP stemmers (N-000140): not provided. ARLSTem and ARLSTem2 exist but raise NotImplementedError.
- WordNet lemmatizer (N-000142, N-000185, N-000432): the constructor and `lemmatize` check the WordNet resource; lemmatization raises NotImplementedError.
- Recursive-descent parser (N-000259): outside this specification; not provided.
- S-expression tokenizer (N-000031): outside this specification.
- Non-goals and out-of-scope surfaces (N-000072–N-000080, N-000349–N-000352): satisfied by omission.
- Threading (N-000068): an assumption with no work item.

## Known gaps to check first

1. Real Punkt, perceptron, stopword, universal-tagset and WordNet data were not available, so the data-dependent paths
   (`sent_tokenize`, `word_tokenize` with sentence splitting, `pos_tag`, `SnowballStemmer(ignore_stopwords=True)`) are tested only against synthetic fixtures.
2. Lancaster uses a partial rule table.
3. Non-English Snowball stemmers and the WordNet lemmatizer are not implemented.

## Per-id accounting

Every id in `spec/CHECKLIST.md` (517 total) appears below with its status. "implemented" means a `# spec:` marker in the listed
file (the marker is a claim that the code addresses the id; the tests in `tests/` exercise the main entries).

| id | status |
| --- | --- |
| N-000353 | implemented: `lingora/__init__.py`, `tests/test_cpu_profile.py` |
| N-000354 | implemented: `lingora/__init__.py`, `tests/test_cpu_profile.py` |
| N-000355 | implemented: `lingora/__init__.py`, `tests/test_cpu_profile.py` |
| N-000356 | implemented: `lingora/__init__.py`, `tests/test_cpu_profile.py` |
| N-000357 | implemented: `tests/test_cpu_profile.py` |
| N-000358 | implemented: `tests/test_cpu_profile.py` |
| N-000359 | implemented: `tests/test_cpu_profile.py` |
| N-000360 | implemented: `tests/test_cpu_profile.py` |
| N-000361 | implemented: `tests/test_cpu_profile.py` |
| N-000362 | implemented: `tests/test_cpu_profile.py` |
| N-000363 | implemented: `tests/test_cpu_profile.py` |
| N-000364 | implemented: `tests/test_cpu_profile.py` |
| N-000365 | implemented: `tests/test_cpu_profile.py` |
| N-000366 | implemented: `tests/test_cpu_profile.py` |
| N-000367 | implemented: `tests/test_cpu_profile.py` |
| N-000368 | implemented: `tests/test_cpu_profile.py` |
| N-000369 | implemented: `tests/test_cpu_profile.py` |
| N-000370 | implemented: `tests/test_cpu_profile.py` |
| N-000371 | implemented: `lingora/__init__.py` |
| N-000372 | implemented: `lingora/__init__.py` |
| N-000373 | implemented: `lingora/__init__.py` |
| N-000374 | implemented: `lingora/__init__.py` |
| N-000375 | implemented: `lingora/__init__.py` |
| N-000376 | implemented: `lingora/__init__.py` |
| N-000377 | implemented: `lingora/__init__.py` |
| N-000378 | implemented: `lingora/__init__.py` |
| N-000379 | implemented: `lingora/__init__.py` |
| N-000380 | implemented: `lingora/__init__.py` |
| N-000381 | implemented: `lingora/__init__.py` |
| N-000382 | implemented: `lingora/__init__.py` |
| N-000383 | implemented: `lingora/__init__.py` |
| N-000384 | implemented: `lingora/__init__.py` |
| N-000385 | implemented: `lingora/__init__.py`, `lingora/data.py`, `tests/test_cli_and_data.py` |
| N-000386 | implemented: `lingora/_punkt.py`, `lingora/data.py`, `tests/test_cli_and_data.py` |
| N-000387 | implemented: `lingora/data.py`, `tests/test_cli_and_data.py` |
| N-000388 | implemented: `lingora/data.py` |
| N-000389 | implemented: `lingora/_punkt.py` |
| N-000390 | implemented: `lingora/tag.py` |
| N-000391 | implemented: `lingora/tag.py` |
| N-000392 | implemented: `lingora/tag.py` |
| N-000393 | implemented: `lingora/chunk.py` |
| N-000394 | implemented: `lingora/chunk.py` |
| N-000395 | implemented: `lingora/stem.py` |
| N-000396 | implemented: `lingora/stem.py` |
| N-000397 | implemented: `lingora/data.py` |
| N-000398 | implemented: `lingora/data.py` |
| N-000399 | implemented: `lingora/_punkt.py` |
| N-000400 | implemented: `lingora/tag.py` |
| N-000401 | implemented: `lingora/tag.py` |
| N-000402 | implemented: `lingora/_punkt.py`, `lingora/data.py` |
| N-000403 | implemented: `lingora/tokenize.py` |
| N-000404 | implemented: `lingora/tokenize.py` |
| N-000405 | implemented: `lingora/tokenize.py` |
| N-000406 | implemented: `lingora/tokenize.py` |
| N-000407 | implemented: `lingora/tokenize.py` |
| N-000408 | implemented: `lingora/tokenize.py` |
| N-000409 | implemented: `lingora/tokenize.py` |
| N-000410 | implemented: `lingora/tokenize.py` |
| N-000411 | implemented: `lingora/tokenize.py` |
| N-000412 | implemented: `lingora/tokenize.py` |
| N-000413 | implemented: `lingora/_punkt.py`, `lingora/tokenize.py`, `tests/test_tokenize.py` |
| N-000414 | implemented: `lingora/cli.py`, `tests/test_cli_and_data.py` |
| N-000415 | implemented: `lingora/cli.py`, `tests/test_cli_and_data.py` |
| N-000416 | implemented: `lingora/cli.py`, `tests/test_cli_and_data.py` |
| N-000417 | implemented: `lingora/cli.py`, `tests/test_cli_and_data.py` |
| N-000418 | implemented: `lingora/cli.py`, `tests/test_cli_and_data.py` |
| N-000419 | implemented: `lingora/cli.py` |
| N-000420 | implemented: `lingora/cli.py` |
| N-000421 | implemented: `lingora/stem.py` |
| N-000422 | implemented: `lingora/stem.py` |
| N-000423 | implemented: `lingora/stem.py` |
| N-000424 | implemented: `lingora/stem.py` |
| N-000425 | implemented: `lingora/stem.py` |
| N-000426 | implemented: `lingora/stem.py` |
| N-000427 | implemented: `lingora/stem.py` |
| N-000428 | implemented: `lingora/stem.py` |
| N-000429 | implemented: `lingora/stem.py` |
| N-000430 | implemented: `lingora/stem.py` |
| N-000431 | implemented: `lingora/stem.py` |
| N-000432 | not done: WordNet lemmatization (constructor and lemmatize check the WordNet resource; result not implemented). |
| N-000433 | implemented: `lingora/tag.py` |
| N-000434 | implemented: `lingora/tag.py` |
| N-000435 | implemented: `lingora/tag.py` |
| N-000436 | implemented: `lingora/tag.py` |
| N-000437 | implemented: `lingora/tag.py` |
| N-000438 | implemented: `lingora/tag.py` |
| N-000439 | implemented: `lingora/tag.py` |
| N-000440 | implemented: `lingora/tag.py` |
| N-000441 | implemented: `lingora/tag.py` |
| N-000442 | implemented: `lingora/tag.py` |
| N-000443 | implemented: `lingora/tag.py` |
| N-000444 | implemented: `lingora/tag.py` |
| N-000445 | implemented: `lingora/tag.py` |
| N-000446 | implemented: `lingora/chunk.py` |
| N-000447 | implemented: `lingora/chunk.py` |
| N-000448 | implemented: `lingora/chunk.py` |
| N-000449 | implemented: `lingora/chunk.py` |
| N-000450 | implemented: `lingora/chunk.py` |
| N-000451 | implemented: `lingora/chunk.py` |
| N-000452 | implemented: `lingora/chunk.py` |
| N-000453 | implemented: `lingora/chunk.py` |
| N-000454 | implemented: `lingora/chunk.py` |
| N-000455 | implemented: `lingora/chunk.py` |
| N-000456 | implemented: `lingora/chunk.py` |
| N-000457 | implemented: `lingora/chunk.py` |
| N-000458 | implemented: `lingora/chunk.py` |
| N-000459 | implemented: `lingora/chunk.py` |
| N-000460 | implemented: `lingora/chunk.py` |
| N-000461 | implemented: `lingora/grammar.py`, `lingora/parse/__init__.py` |
| N-000462 | implemented: `lingora/parse/__init__.py` |
| N-000463 | implemented: `lingora/parse/__init__.py` |
| N-000464 | implemented: `lingora/grammar.py` |
| N-000465 | implemented: `lingora/grammar.py` |
| N-000466 | implemented: `lingora/grammar.py`, `tests/test_tree_grammar.py` |
| N-000467 | implemented: `lingora/grammar.py` |
| N-000468 | implemented: `lingora/grammar.py` |
| N-000469 | implemented: `lingora/grammar.py`, `tests/test_tree_grammar.py` |
| N-000470 | implemented: `lingora/grammar.py` |
| N-000471 | implemented: `lingora/grammar.py`, `tests/test_tree_grammar.py` |
| N-000472 | implemented: `lingora/parse/_common.py` |
| N-000473 | implemented: `lingora/parse/chart.py` |
| N-000474 | implemented: `lingora/parse/chart.py` |
| N-000475 | implemented: `lingora/parse/_common.py`, `lingora/parse/chart.py` |
| N-000476 | implemented: `lingora/parse/_common.py`, `lingora/parse/chart.py` |
| N-000477 | implemented: `lingora/parse/generate.py`, `tests/test_tree_grammar.py` |
| N-000478 | implemented: `lingora/parse/generate.py`, `tests/test_tree_grammar.py` |
| N-000479 | implemented: `lingora/grammar.py`, `lingora/parse/generate.py` |
| N-000480 | implemented: `lingora/grammar.py`, `lingora/parse/generate.py`, `tests/test_tree_grammar.py` |
| N-000481 | implemented: `lingora/tree.py`, `tests/test_tree_grammar.py` |
| N-000482 | implemented: `lingora/tree.py` |
| N-000483 | implemented: `lingora/tree.py`, `tests/test_tree_grammar.py` |
| N-000484 | implemented: `lingora/tree.py`, `tests/test_tree_grammar.py` |
| N-000485 | implemented: `lingora/tree.py`, `tests/test_tree_grammar.py` |
| N-000486 | implemented: `lingora/tree.py`, `tests/test_tree_grammar.py` |
| N-000487 | implemented: `lingora/tree.py`, `tests/test_tree_grammar.py` |
| N-000488 | implemented: `lingora/tree.py`, `tests/test_tree_grammar.py` |
| N-000489 | implemented: `lingora/tree.py`, `tests/test_tree_grammar.py` |
| N-000490 | implemented: `lingora/tree.py` |
| N-000491 | implemented: `lingora/tree.py` |
| N-000492 | implemented: `lingora/classify.py`, `tests/test_tag_chunk_classify_metrics.py` |
| N-000493 | implemented: `lingora/classify.py`, `tests/test_tag_chunk_classify_metrics.py` |
| N-000494 | implemented: `lingora/classify.py`, `tests/test_tag_chunk_classify_metrics.py` |
| N-000495 | implemented: `lingora/classify.py` |
| N-000496 | implemented: `lingora/classify.py`, `tests/test_tag_chunk_classify_metrics.py` |
| N-000497 | implemented: `lingora/classify.py` |
| N-000498 | implemented: `lingora/metrics.py` |
| N-000499 | implemented: `lingora/metrics.py` |
| N-000500 | implemented: `lingora/metrics.py` |
| N-000501 | implemented: `lingora/metrics.py`, `tests/test_tag_chunk_classify_metrics.py` |
| N-000502 | implemented: `lingora/metrics.py`, `tests/test_tag_chunk_classify_metrics.py` |
| N-000503 | implemented: `lingora/metrics.py`, `tests/test_tag_chunk_classify_metrics.py` |
| N-000504 | implemented: `lingora/metrics.py` |
| N-000505 | implemented: `lingora/metrics.py`, `tests/test_tag_chunk_classify_metrics.py` |
| N-000506 | implemented: `lingora/metrics.py` |
| N-000507 | implemented: `lingora/metrics.py`, `tests/test_tag_chunk_classify_metrics.py` |
| N-000508 | implemented: `lingora/metrics.py` |
| N-000509 | implemented: `lingora/metrics.py`, `tests/test_tag_chunk_classify_metrics.py` |
| N-000510 | implemented: `lingora/metrics.py`, `tests/test_tag_chunk_classify_metrics.py` |
| N-000511 | implemented: `lingora/translate.py`, `tests/test_tag_chunk_classify_metrics.py` |
| N-000512 | implemented: `lingora/translate.py`, `tests/test_tag_chunk_classify_metrics.py` |
| N-000513 | implemented: `lingora/translate.py`, `tests/test_tag_chunk_classify_metrics.py` |
| N-000514 | implemented: `lingora/translate.py` |
| N-000515 | implemented: `lingora/translate.py` |
| N-000516 | implemented: `lingora/translate.py`, `tests/test_tag_chunk_classify_metrics.py` |
| N-000517 | implemented: `lingora/translate.py` |
| N-000001 | implemented: `lingora/__init__.py` |
| N-000002 | implemented: `lingora/__init__.py` |
| N-000003 | implemented: `lingora/__init__.py` |
| N-000004 | implemented: `lingora/__init__.py` |
| N-000005 | implemented: `lingora/__init__.py` |
| N-000006 | implemented: `lingora/__init__.py` |
| N-000007 | implemented: `lingora/__init__.py` |
| N-000008 | implemented: `lingora/__init__.py` |
| N-000009 | implemented: `lingora/__init__.py` |
| N-000010 | implemented: `lingora/__init__.py` |
| N-000011 | implemented: `lingora/__init__.py` |
| N-000012 | implemented: `lingora/__init__.py` |
| N-000013 | implemented: `lingora/__init__.py` |
| N-000014 | implemented: `lingora/__init__.py` |
| N-000015 | implemented: `lingora/__init__.py` |
| N-000016 | implemented: `lingora/__init__.py` |
| N-000017 | implemented: `lingora/__init__.py` |
| N-000018 | implemented: `lingora/__init__.py` |
| N-000019 | implemented: `lingora/__init__.py` |
| N-000020 | implemented: `lingora/__init__.py` |
| N-000021 | implemented: `lingora/__init__.py` |
| N-000022 | implemented: `lingora/tokenize.py` |
| N-000023 | implemented: `lingora/stem.py` |
| N-000024 | implemented: `lingora/stem.py`, `lingora/tag.py` |
| N-000025 | implemented: `lingora/chunk.py`, `lingora/tag.py` |
| N-000026 | implemented: `lingora/chunk.py` |
| N-000027 | implemented: `lingora/chunk.py` |
| N-000028 | implemented: `lingora/_punkt.py` |
| N-000029 | implemented: `lingora/__init__.py` |
| N-000030 | implemented: `lingora/tokenize.py` |
| N-000031 | not done: s-expression tokenizer is outside this specification (PRD FP-01 says so). |
| N-000032 | implemented: `lingora/cli.py` |
| N-000033 | implemented: `lingora/tokenize.py` |
| N-000034 | implemented: `lingora/stem.py` |
| N-000035 | implemented: `lingora/tag.py` |
| N-000036 | implemented: `lingora/tag.py` |
| N-000037 | implemented: `lingora/chunk.py` |
| N-000038 | not done: named-entity chunker. `ne_chunk` checks the packaged model and wordlist, then raises NotImplementedError; the model's file format is not specified. |
| N-000039 | implemented: `lingora/chunk.py` |
| N-000040 | implemented: `lingora/grammar.py`, `lingora/tree.py` |
| N-000041 | implemented: `lingora/grammar.py`, `lingora/tree.py` |
| N-000042 | implemented: `lingora/tree.py` |
| N-000043 | implemented: `lingora/tree.py` |
| N-000044 | implemented: `lingora/classify.py` |
| N-000045 | implemented: `lingora/classify.py` |
| N-000046 | implemented: `lingora/metrics.py` |
| N-000047 | implemented: `lingora/__init__.py` |
| N-000048 | implemented: `lingora/__init__.py` |
| N-000049 | implemented: `lingora/__init__.py` |
| N-000050 | implemented: `lingora/__init__.py` |
| N-000051 | implemented: `lingora/__init__.py` |
| N-000052 | implemented: `lingora/__init__.py` |
| N-000053 | implemented: `lingora/__init__.py` |
| N-000054 | implemented: `lingora/__init__.py` |
| N-000055 | implemented: `lingora/__init__.py` |
| N-000056 | implemented: `lingora/__init__.py` |
| N-000057 | implemented: `lingora/__init__.py` |
| N-000058 | implemented: `lingora/__init__.py` |
| N-000059 | implemented: `lingora/__init__.py` |
| N-000060 | implemented: `lingora/__init__.py` |
| N-000061 | implemented: `lingora/__init__.py` |
| N-000062 | implemented: `lingora/__init__.py` |
| N-000063 | implemented: `lingora/__init__.py` |
| N-000064 | implemented: `lingora/__init__.py` |
| N-000065 | implemented: `lingora/__init__.py` |
| N-000066 | implemented: `lingora/tokenize.py` |
| N-000067 | implemented: `lingora/tokenize.py` |
| N-000068 | assumption (threading and process model): not a concern of this specification; nothing to build. |
| N-000069 | implemented: `lingora/__init__.py` |
| N-000070 | implemented: `lingora/__init__.py` |
| N-000071 | implemented: `lingora/__init__.py` |
| N-000072 | satisfied by omission: non-goal. |
| N-000073 | satisfied by omission: non-goal (corpora are not shipped). |
| N-000074 | satisfied by omission: non-goal. |
| N-000075 | satisfied by omission: non-goal. |
| N-000076 | satisfied by omission: non-goal. |
| N-000077 | satisfied by omission: non-goal. |
| N-000078 | satisfied by omission: non-goal. |
| N-000079 | satisfied by omission: non-goal. |
| N-000080 | satisfied by omission: non-goal (no throughput guarantee is made). |
| N-000081 | implemented: `lingora/tokenize.py` |
| N-000082 | implemented: `lingora/tokenize.py` |
| N-000083 | implemented: `lingora/cli.py` |
| N-000084 | implemented: `lingora/cli.py`, `lingora/tokenize.py` |
| N-000085 | implemented: `tests/test_tokenize.py` |
| N-000086 | implemented: `lingora/tokenize.py` |
| N-000087 | implemented: `lingora/tokenize.py` |
| N-000088 | implemented: `lingora/tokenize.py` |
| N-000089 | implemented: `lingora/tokenize.py`, `tests/test_tokenize.py` |
| N-000090 | implemented: `lingora/tokenize.py`, `tests/test_tokenize.py` |
| N-000091 | implemented: `lingora/tokenize.py`, `tests/test_tokenize.py` |
| N-000092 | implemented: `lingora/tokenize.py` |
| N-000093 | implemented: `lingora/tokenize.py`, `tests/test_tokenize.py` |
| N-000094 | implemented: `lingora/tokenize.py`, `tests/test_tokenize.py` |
| N-000095 | implemented: `lingora/tokenize.py` |
| N-000096 | implemented: `lingora/tokenize.py`, `tests/test_tokenize.py` |
| N-000097 | implemented: `lingora/tokenize.py`, `tests/test_tokenize.py` |
| N-000098 | implemented: `lingora/tokenize.py` |
| N-000099 | implemented: `lingora/tokenize.py`, `tests/test_tokenize.py` |
| N-000100 | implemented: `lingora/tokenize.py`, `tests/test_tokenize.py` |
| N-000101 | implemented: `lingora/tokenize.py`, `tests/test_tokenize.py` |
| N-000102 | implemented: `lingora/tokenize.py`, `tests/test_tokenize.py` |
| N-000103 | implemented: `lingora/tokenize.py`, `tests/test_tokenize.py` |
| N-000104 | implemented: `lingora/tokenize.py` |
| N-000105 | implemented: `lingora/tokenize.py` |
| N-000106 | implemented: `lingora/tokenize.py`, `tests/test_tokenize.py` |
| N-000107 | implemented: `lingora/tokenize.py`, `tests/test_tokenize.py` |
| N-000108 | implemented: `lingora/tokenize.py`, `tests/test_tokenize.py` |
| N-000109 | implemented: `lingora/tokenize.py`, `tests/test_tokenize.py` |
| N-000110 | implemented: `lingora/tokenize.py`, `tests/test_tokenize.py` |
| N-000111 | implemented: `lingora/tokenize.py`, `tests/test_tokenize.py` |
| N-000112 | implemented: `lingora/tokenize.py`, `tests/test_tokenize.py` |
| N-000113 | implemented: `lingora/tokenize.py`, `tests/test_tokenize.py` |
| N-000114 | implemented: `lingora/tokenize.py`, `tests/test_tokenize.py` |
| N-000115 | implemented: `lingora/tokenize.py`, `tests/test_tokenize.py` |
| N-000116 | implemented: `lingora/tokenize.py`, `tests/test_tokenize.py` |
| N-000117 | implemented: `lingora/tokenize.py`, `tests/test_tokenize.py` |
| N-000118 | implemented: `lingora/tokenize.py`, `tests/test_tokenize.py` |
| N-000119 | implemented: `lingora/tokenize.py`, `tests/test_tokenize.py` |
| N-000120 | implemented: `lingora/tokenize.py`, `tests/test_tokenize.py` |
| N-000121 | implemented: `lingora/tokenize.py`, `tests/test_tokenize.py` |
| N-000122 | implemented: `lingora/tokenize.py`, `tests/test_tokenize.py` |
| N-000123 | implemented: `lingora/tokenize.py`, `tests/test_tokenize.py` |
| N-000124 | implemented: `lingora/tokenize.py`, `tests/test_tokenize.py` |
| N-000125 | implemented: `lingora/tokenize.py`, `tests/test_tokenize.py` |
| N-000126 | implemented: `lingora/tokenize.py`, `tests/test_tokenize.py` |
| N-000127 | implemented: `lingora/tokenize.py`, `tests/test_tokenize.py` |
| N-000128 | implemented: `lingora/tokenize.py`, `tests/test_tokenize.py` |
| N-000129 | implemented: `lingora/_punkt.py`, `lingora/tokenize.py`, `tests/test_tokenize.py` |
| N-000130 | implemented: `lingora/_punkt.py`, `tests/test_tokenize.py` |
| N-000131 | implemented: `lingora/_punkt.py`, `tests/test_tokenize.py` |
| N-000132 | implemented: `lingora/_punkt.py`, `tests/test_tokenize.py` |
| N-000133 | implemented: `lingora/_punkt.py`, `lingora/tokenize.py`, `tests/test_tokenize.py` |
| N-000134 | implemented: `lingora/cli.py` |
| N-000135 | implemented: `lingora/cli.py` |
| N-000136 | implemented: `lingora/tokenize.py`, `tests/test_tokenize.py` |
| N-000137 | implemented: `lingora/tokenize.py`, `tests/test_tokenize.py` |
| N-000138 | implemented: `lingora/tokenize.py`, `tests/test_tokenize.py` |
| N-000139 | implemented: `lingora/cli.py`, `tests/test_cli_and_data.py` |
| N-000140 | partial: Porter, Lancaster, Snowball, regexp are implemented; ISRI, Cistem and RSLP are not provided at all. |
| N-000141 | implemented: `lingora/stem.py` |
| N-000142 | partial: the WordNet lemmatizer exists and checks the WordNet resource, but `lemmatize` raises NotImplementedError (not done). |
| N-000143 | partial: ARLSTem and ARLSTem2 exist as classes that raise NotImplementedError when stemming; their results are outside this specification. |
| N-000144 | implemented: `lingora/stem.py` |
| N-000145 | implemented: `lingora/stem.py` |
| N-000146 | satisfied by omission: the stemmer families not listed in FP-02 are absent or outside this specification. |
| N-000147 | implemented: `lingora/stem.py` |
| N-000148 | implemented: `lingora/stem.py` |
| N-000149 | partial: the three Porter modes are accepted; 'original' and 'martin' both use the published algorithm without LINGORA's changes (their results are outside this specification). |
| N-000150 | implemented: `lingora/stem.py` |
| N-000151 | implemented: `lingora/stem.py` |
| N-000152 | implemented: `lingora/stem.py` |
| N-000153 | implemented: `lingora/stem.py` |
| N-000154 | implemented: `lingora/stem.py` |
| N-000155 | implemented: `lingora/stem.py` |
| N-000156 | implemented: `lingora/stem.py` |
| N-000157 | implemented: `lingora/stem.py` |
| N-000158 | implemented: `lingora/stem.py` |
| N-000159 | implemented: `lingora/stem.py` |
| N-000160 | implemented: `lingora/stem.py` |
| N-000161 | implemented: `lingora/stem.py` |
| N-000162 | implemented: `lingora/stem.py` |
| N-000163 | implemented: `lingora/stem.py` |
| N-000164 | implemented: `lingora/stem.py` |
| N-000165 | implemented: `lingora/stem.py` |
| N-000166 | implemented: `lingora/stem.py` |
| N-000167 | implemented: `lingora/stem.py` |
| N-000168 | implemented: `lingora/stem.py` |
| N-000169 | implemented: `lingora/stem.py` |
| N-000170 | partial: Paice/Husk engine is implemented with a 42-rule subset of the published table (see Lancaster notes); not a full transcription. |
| N-000171 | implemented: `lingora/stem.py` |
| N-000172 | partial: Snowball algorithms are implemented for `english` (Porter2) and `porter`; the other 14 languages raise NotImplementedError naming the language. |
| N-000173 | implemented: `lingora/stem.py` |
| N-000174 | implemented: `lingora/stem.py` |
| N-000175 | implemented: `lingora/stem.py` |
| N-000176 | implemented: `lingora/stem.py` |
| N-000177 | implemented: `lingora/stem.py` |
| N-000178 | implemented: `lingora/stem.py` |
| N-000179 | implemented: `lingora/stem.py` |
| N-000180 | implemented: `lingora/stem.py` |
| N-000181 | implemented: `lingora/stem.py` |
| N-000182 | implemented: `lingora/stem.py` |
| N-000183 | implemented: `lingora/stem.py` |
| N-000184 | implemented: `lingora/stem.py` |
| N-000185 | not done: WordNet lemmatization (WordNet resource is checked; lemmatize raises NotImplementedError). |
| N-000186 | implemented: `lingora/stem.py` |
| N-000187 | implemented: `lingora/tag.py` |
| N-000188 | implemented: `lingora/tag.py` |
| N-000189 | partial: bigram, trigram and affix taggers are implemented simply; their results are outside this specification. |
| N-000190 | implemented: `lingora/tag.py` |
| N-000191 | implemented: `lingora/tag.py` |
| N-000192 | implemented: `lingora/tag.py` |
| N-000193 | implemented: `lingora/tag.py` |
| N-000194 | implemented: `lingora/tag.py` |
| N-000195 | implemented: `lingora/tag.py` |
| N-000196 | implemented: `lingora/tag.py` |
| N-000197 | implemented: `lingora/tag.py` |
| N-000198 | implemented: `lingora/tag.py`, `tests/test_tag_chunk_classify_metrics.py` |
| N-000199 | implemented: `lingora/tag.py`, `tests/test_tag_chunk_classify_metrics.py` |
| N-000200 | implemented: `lingora/tag.py`, `tests/test_tag_chunk_classify_metrics.py` |
| N-000201 | implemented: `lingora/tag.py`, `tests/test_tag_chunk_classify_metrics.py` |
| N-000202 | implemented: `lingora/tag.py`, `tests/test_tag_chunk_classify_metrics.py` |
| N-000203 | implemented: `lingora/tag.py`, `tests/test_tag_chunk_classify_metrics.py` |
| N-000204 | implemented: `lingora/tag.py` |
| N-000205 | implemented: `lingora/tag.py`, `tests/test_tag_chunk_classify_metrics.py` |
| N-000206 | implemented: `lingora/tag.py` |
| N-000207 | implemented: `lingora/tag.py` |
| N-000208 | implemented: `lingora/tag.py` |
| N-000209 | implemented: `lingora/tag.py` |
| N-000210 | implemented: `lingora/tag.py` |
| N-000211 | implemented: `lingora/tag.py` |
| N-000212 | implemented: `lingora/tag.py` |
| N-000213 | implemented: `lingora/tag.py` |
| N-000214 | implemented: `lingora/tag.py` |
| N-000215 | implemented: `lingora/tag.py` |
| N-000216 | implemented: `lingora/tag.py` |
| N-000217 | implemented: `lingora/tag.py` |
| N-000218 | implemented: `lingora/tag.py` |
| N-000219 | implemented: `lingora/tag.py` |
| N-000220 | implemented: `lingora/tag.py` |
| N-000221 | implemented: `lingora/tag.py` |
| N-000222 | implemented: `lingora/tag.py` |
| N-000223 | implemented: `lingora/tag.py` |
| N-000224 | implemented: `lingora/tag.py` |
| N-000225 | implemented: `lingora/tag.py` |
| N-000226 | implemented: `lingora/tag.py` |
| N-000227 | implemented: `lingora/tag.py` |
| N-000228 | implemented: `lingora/chunk.py`, `tests/test_tag_chunk_classify_metrics.py` |
| N-000229 | implemented: `lingora/chunk.py` |
| N-000230 | implemented: `lingora/chunk.py` |
| N-000231 | not done: named-entity chunker (see N-000038). |
| N-000232 | implemented: `lingora/chunk.py` |
| N-000233 | implemented: `lingora/chunk.py` |
| N-000234 | implemented: `lingora/chunk.py` |
| N-000235 | implemented: `lingora/chunk.py` |
| N-000236 | implemented: `lingora/chunk.py`, `tests/test_tag_chunk_classify_metrics.py` |
| N-000237 | implemented: `lingora/chunk.py` |
| N-000238 | implemented: `lingora/chunk.py` |
| N-000239 | implemented: `lingora/chunk.py`, `tests/test_tag_chunk_classify_metrics.py` |
| N-000240 | implemented: `lingora/chunk.py` |
| N-000241 | implemented: `lingora/chunk.py` |
| N-000242 | implemented: `lingora/chunk.py` |
| N-000243 | implemented: `lingora/chunk.py`, `tests/test_tag_chunk_classify_metrics.py` |
| N-000244 | implemented: `lingora/chunk.py` |
| N-000245 | implemented: `lingora/chunk.py` |
| N-000246 | implemented: `lingora/chunk.py`, `tests/test_tag_chunk_classify_metrics.py` |
| N-000247 | implemented: `lingora/chunk.py` |
| N-000248 | implemented: `lingora/chunk.py` |
| N-000249 | implemented: `lingora/chunk.py` |
| N-000250 | implemented: `lingora/chunk.py` |
| N-000251 | implemented: `lingora/chunk.py` |
| N-000252 | implemented: `lingora/chunk.py`, `tests/test_tag_chunk_classify_metrics.py` |
| N-000253 | implemented: `lingora/chunk.py`, `tests/test_tag_chunk_classify_metrics.py` |
| N-000254 | implemented: `lingora/chunk.py`, `tests/test_tag_chunk_classify_metrics.py` |
| N-000255 | implemented: `lingora/chunk.py` |
| N-000256 | implemented: `lingora/chunk.py`, `tests/test_tag_chunk_classify_metrics.py` |
| N-000257 | implemented: `lingora/chunk.py` |
| N-000258 | implemented: `lingora/parse/__init__.py` |
| N-000259 | not done: recursive-descent parser is outside this specification (PRD FP-05). |
| N-000260 | implemented: `lingora/parse/__init__.py` |
| N-000261 | implemented: `lingora/parse/__init__.py` |
| N-000262 | implemented: `lingora/parse/__init__.py` |
| N-000263 | implemented: `lingora/parse/__init__.py` |
| N-000264 | implemented: `lingora/grammar.py`, `tests/test_tree_grammar.py` |
| N-000265 | implemented: `lingora/grammar.py`, `tests/test_tree_grammar.py` |
| N-000266 | implemented: `lingora/parse/chart.py`, `tests/test_tree_grammar.py` |
| N-000267 | implemented: `lingora/parse/chart.py`, `tests/test_tree_grammar.py` |
| N-000268 | implemented: `lingora/grammar.py`, `lingora/parse/chart.py`, `tests/test_tree_grammar.py` |
| N-000269 | implemented: `lingora/parse/chart.py`, `tests/test_tree_grammar.py` |
| N-000270 | implemented: `lingora/grammar.py`, `lingora/parse/chart.py`, `tests/test_tree_grammar.py` |
| N-000271 | implemented: `lingora/parse/chart.py`, `tests/test_tree_grammar.py` |
| N-000272 | implemented: `lingora/parse/shift_reduce.py`, `tests/test_tree_grammar.py` |
| N-000273 | implemented: `lingora/parse/shift_reduce.py`, `tests/test_tree_grammar.py` |
| N-000274 | implemented: `lingora/parse/shift_reduce.py`, `tests/test_tree_grammar.py` |
| N-000275 | implemented: `lingora/parse/shift_reduce.py`, `tests/test_tree_grammar.py` |
| N-000276 | implemented: `lingora/parse/generate.py`, `tests/test_tree_grammar.py` |
| N-000277 | implemented: `lingora/parse/generate.py`, `tests/test_tree_grammar.py` |
| N-000278 | implemented: `lingora/parse/generate.py`, `tests/test_tree_grammar.py` |
| N-000279 | implemented: `lingora/parse/generate.py`, `tests/test_tree_grammar.py` |
| N-000280 | implemented: `lingora/parse/generate.py` |
| N-000281 | implemented: `lingora/tree.py` |
| N-000282 | implemented: `lingora/tree.py` |
| N-000283 | implemented: `lingora/tree.py` |
| N-000284 | implemented: `lingora/tree.py` |
| N-000285 | implemented: `lingora/tree.py` |
| N-000286 | implemented: `lingora/tree.py`, `tests/test_tree_grammar.py` |
| N-000287 | implemented: `lingora/tree.py`, `tests/test_tree_grammar.py` |
| N-000288 | implemented: `lingora/tree.py` |
| N-000289 | implemented: `lingora/tree.py`, `tests/test_tree_grammar.py` |
| N-000290 | implemented: `lingora/tree.py` |
| N-000291 | implemented: `lingora/tree.py` |
| N-000292 | implemented: `lingora/parse/_common.py`, `lingora/parse/chart.py` |
| N-000293 | implemented: `lingora/parse/chart.py` |
| N-000294 | implemented: `lingora/parse/_common.py`, `lingora/parse/chart.py` |
| N-000295 | implemented: `lingora/classify.py` |
| N-000296 | implemented: `lingora/classify.py` |
| N-000297 | implemented: `lingora/classify.py` |
| N-000298 | implemented: `lingora/classify.py` |
| N-000299 | implemented: `lingora/classify.py` |
| N-000300 | implemented: `lingora/classify.py` |
| N-000301 | implemented: `lingora/classify.py` |
| N-000302 | implemented: `lingora/classify.py` |
| N-000303 | implemented: `lingora/classify.py` |
| N-000304 | implemented: `lingora/classify.py` |
| N-000305 | implemented: `lingora/classify.py` |
| N-000306 | implemented: `lingora/classify.py` |
| N-000307 | implemented: `lingora/classify.py`, `tests/test_tag_chunk_classify_metrics.py` |
| N-000308 | implemented: `lingora/classify.py`, `tests/test_tag_chunk_classify_metrics.py` |
| N-000309 | implemented: `lingora/classify.py`, `tests/test_tag_chunk_classify_metrics.py` |
| N-000310 | implemented: `lingora/classify.py` |
| N-000311 | implemented: `lingora/classify.py` |
| N-000312 | implemented: `lingora/classify.py` |
| N-000313 | implemented: `lingora/classify.py` |
| N-000314 | implemented: `lingora/classify.py` |
| N-000315 | implemented: `lingora/classify.py`, `tests/test_tag_chunk_classify_metrics.py` |
| N-000316 | implemented: `lingora/classify.py` |
| N-000317 | implemented: `lingora/classify.py` |
| N-000318 | implemented: `lingora/classify.py` |
| N-000319 | implemented: `lingora/metrics.py` |
| N-000320 | implemented: `lingora/metrics.py` |
| N-000321 | implemented: `lingora/metrics.py` |
| N-000322 | implemented: `lingora/metrics.py` |
| N-000323 | implemented: `lingora/metrics.py` |
| N-000324 | implemented: `lingora/metrics.py` |
| N-000325 | implemented: `lingora/metrics.py` |
| N-000326 | implemented: `lingora/metrics.py` |
| N-000327 | implemented: `lingora/metrics.py` |
| N-000328 | implemented: `lingora/metrics.py` |
| N-000329 | implemented: `lingora/metrics.py` |
| N-000330 | implemented: `lingora/metrics.py` |
| N-000331 | implemented: `lingora/metrics.py` |
| N-000332 | implemented: `lingora/metrics.py` |
| N-000333 | implemented: `lingora/metrics.py` |
| N-000334 | implemented: `lingora/metrics.py` |
| N-000335 | implemented: `lingora/translate.py`, `tests/test_tag_chunk_classify_metrics.py` |
| N-000336 | implemented: `lingora/translate.py` |
| N-000337 | implemented: `lingora/translate.py` |
| N-000338 | implemented: `lingora/translate.py` |
| N-000339 | implemented: `lingora/translate.py`, `tests/test_tag_chunk_classify_metrics.py` |
| N-000340 | implemented: `lingora/translate.py` |
| N-000341 | implemented: `lingora/translate.py` |
| N-000342 | implemented: `lingora/translate.py` |
| N-000343 | implemented: `lingora/metrics.py` |
| N-000344 | implemented: `lingora/metrics.py` |
| N-000345 | implemented: `lingora/metrics.py` |
| N-000346 | implemented: `lingora/metrics.py` |
| N-000347 | implemented: `lingora/metrics.py` |
| N-000348 | implemented: `lingora/metrics.py` |
| N-000349 | satisfied by omission: outside this specification (no corpus, downloader or data finder beyond `lingora.data`). |
| N-000350 | satisfied by omission: outside this specification. |
| N-000351 | satisfied by omission: outside this specification. |
| N-000352 | satisfied by omission: outside this specification. |