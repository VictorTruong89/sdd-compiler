# NOTES

Layout: flat package `lingora/` at the repo root (`data`, `tokenize`, `stem`, `tag`, `chunk`,
`grammar`, `parse` (+`parse.generate`), `tree`, `classify`, `metrics`, `translate`, `cli`).
Pure Python, no runtime dependencies, no build step. Tests: `tests/`. Code carries the
behaviour of every id in `spec/CHECKLIST.md` (marked in places with `# spec: N-…`);
ids in FP-xx / Interface packs were implemented as stated in their pack text.

## Spec disagreements
- Interface_Contract (pack 12) lists only `ChartParser` and `ShiftReduceParser`; the PRD
  (pack 26, N-000237) says a recursive-descent parser also exists with results outside the spec.
  Built: `lingora.parse.RecursiveDescentParser`, a thin subclass of `ChartParser`.
- Interface_Contract (pack 08) says the CLI is `cli.main(args=…, standalone_mode=True)`, which
  is the `click` API, while the Hardware/PRD packs allow only pure-Python dependencies and
  `click` is not installed. Built: a small own `Group` class with the same `main(args,
  standalone_mode)` behaviour (exit via `SystemExit`: 0 success, 1 runtime failure, 2 usage).
- PRD pack 24 says the Russian→universal table is the implementer's choice; Interface pack 10
  says only `tagset` is `None`/`'universal'`. Built: a fixed RNC→universal table in `tag.py`.
- Interface pack 14 says `accuracy(classifier, gold)` exists in `classify`; PRD FP-06 says the
  list/list `accuracy` (FP-07) is separate. Both exist (`classify.accuracy`, `metrics.accuracy`).

## Not stated by the spec (assumptions)
- `data.path` initial contents: `$LINGORA_DATA` (os.pathsep-separated), `/app/lingora_data`
  (repo-root `lingora_data`), `~/lingora_data`, `/usr/share/lingora_data`. Missing resources raise
  `LookupError`; `SnowballStemmer(ignore_stopwords=True)` and unsupported languages raise `ValueError`.
  `pos_tag` raises `TypeError` for a str, `ValueError` for bad `lang`/`tagset`.
  English `tagset='universal'` without `en-ptb.map` raises `LookupError`; unmapped tags map to `X`.
- Empty equal-length lists: `metrics.accuracy` and `classify.accuracy` return `0.0`.
  `jaccard_distance(set(), set())` returns `0.0`.
- `RegexpTokenizer` token mode returns all matches (empty matches are not discarded); gap mode
  honours `discard_empty`. `blankline_tokenize` of whitespace-only text returns `[]`.
- Tweet tokenizer also converts HTML entities (as the reference library does) and accepts
  `match_phone_numbers`.
- `generate(..., n=0)` yields nothing; `depth=None` means unbounded (RecursionError -> RuntimeError).
- Chunk grammar: clause label line `LABEL: {…}`/`}…{`; `#` comments and blank lines ignored; other
  rule syntax (merge/split) raises `ValueError`. Root label is `"S"`. A list grammar may hold
  grammar strings, `ChunkStage` objects or `RegexpParser`s.
- Tie-breaks: unigram tagger / decision tree majority use first-seen order.
- Naive Bayes uses +0.5 (ELE) smoothing; Decision tree uses entropy_cutoff=0.05,
  support_cutoff=10, depth_cutoff=100 (so tiny training sets yield a stump).
- CLI options: `-l/--language` (default english), `-d/--delimiter` (default space),
  `-e/--encoding` (default utf-8). The Punkt model is checked before any output is written.

## Not done / approximations (results outside the spec or too large)
- Snowball: `english` (Porter2) and `porter` are full algorithms. The other 14 languages are
  accepted but use a light suffix stripper (`_GenericSnowball`), not the real Snowball rules.
- `ARLSTem`/`ARLSTem2`: simplified light Arabic stemmer (results outside the spec).
- `ne_chunk`: checks that the model directory and `corpora/words` are visible (raises
  `LookupError` otherwise); with both present it returns the tagged tokens unchunked, because the
  maxent model file format is not described in the spec.
- Cistem, ISRI, RSLP stemmers are not implemented (not importable from `lingora.stem`). Bigram/trigram/affix tagger details and Porter's
  original/Martin modes: present or approximate; outside the spec.
- Lancaster rule table and the Porter irregular-forms table were written from memory of the
  published algorithms; rare words may differ.
