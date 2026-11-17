# NOTES

Pure-Python package `lingora` (flat layout, no build step, no third-party runtime deps).
Run `python -m pytest tests` for the smoke tests. `# spec: N-…` comments in `lingora/` mark satisfying code.

## Checklist accounting (all 517 ids)
Every id is implemented, except those listed under "Not done / approximated" below. By pack:
- 01–05 (hardware, public surface): pure-Python flat package, no downloads on import, Python ≥3.10, exceptions for refusals (never empty returns) — `lingora/__init__.py`, whole package.
- 06 (`lingora.data`): `data.path` mutable list, `data.find`, file readers; model readers in `tokenize/punkt.py`, `tag/perceptron.py`, `tag/__init__.py` (universal map), `stem/__init__.py` (stopwords, WordNet).
- 07/22 tokenizers: `lingora/tokenize/`. 08 CLI: `lingora/cli.py` (own minimal command group; `click` is not installed, so `cli.main(args, standalone_mode)` is hand-written).
- 09/23 stemmers: `lingora/stem/`. 10/24 taggers: `lingora/tag/`. 11/25 chunking: `lingora/chunk/`.
- 12/26 grammar/parse/generate: `grammar.py`, `parse/`. 13 trees: `tree.py`. 14/27 classifiers: `classify.py`. 15/28 metrics+BLEU: `metrics.py`, `translate/`.
- 16–21, 29 (overview, terminology, non-goals, out-of-scope): descriptive; nothing to build (non-goals deliberately not built).

## Conflicts between spec parts and what was built
1. CF-000001 — N-000094 (Treebank: "A straight double quote at the start of the text" becomes the opening token ``) vs N-000106 (recommended tokenizer: a straight double quote at the very start becomes the closing token ''). Built both as stated: `TreebankWordTokenizer` gives ``; `word_tokenize` (improved tokenizer) gives ''.
2. CF-000008 / CF-000039 / CF-000072 — N-000331 (PRD: accuracy on different-length lists is the fraction over the common positions) vs N-000343, N-000318, N-000502 (different lengths raise). Built: `metrics.accuracy` raises `ValueError`.
3. CF-000016 / CF-000055 / CF-000070 — N-000325/N-000327 (PRD: unrestricted Damerau–Levenshtein, characters may be inserted between transposed ones) vs N-000505/N-000506 (contract: only adjacent characters, nothing inserted/deleted between). Built the contract's restricted (optimal-string-alignment) form: `edit_distance("ca","abc",transpositions=True)==3`.
4. CF-000028 — N-000240 (two touching matches are two chunks) vs N-000242 (touching chunks are joined). Built N-000240: touching matches of a rule stay separate chunks.
5. CF-000038 — N-000334 (f-measure is 0 when precision or recall is 0) vs N-000346 (no number when the sets share no element). Built: `None` when either set is empty; `0` when both non-empty but disjoint.
6. CF-000054 — N-000067 vs N-000125 (tweet lowercasing "except emoticons"): built the latter (emoticons keep their case); not a real clash.
7. CF-000073 — N-000158 (PRD: four-letter "-ies" becomes "-ie") vs N-000424 (contract: Step 1a as published, "ties" → "ti"). Built the contract: "ties" → "ti". Other extensions (-ied, *o, step 1c, step 2) are as in the PRD. Also the contract's `to_lowercase=False` default is used (PRD N-000154 says lowercase first): `stem` keeps case unless `to_lowercase=True`; irregular-table lookup is case-insensitive.
8. CF-000077 — N-000118 (PRD: discarding empty pieces is on by default) vs N-000407 (contract: off unless `discard_empty=True`). Built the contract for `RegexpTokenizer`. `WhitespaceTokenizer`/`blankline_tokenize` drop empty pieces as the PRD describes for them.
9. CF-000083 — N-000102 (fused forms incl. *cannot* split) vs N-000110 (*cannot* kept whole): different tokenizers; `TreebankWordTokenizer` splits, `word_tokenize` keeps it.
10. Unlisted: PRD N-000283 says a `str` given as the child list is "taken as a single leaf", but N-000288/N-000486 refuse it. Built: `Tree(label, "abc")` raises `TypeError`.
11. Unlisted: PRD N-000332 says a list/tuple given to precision/recall is read as a set, but N-000344–N-000347/N-000508 refuse non-sets. Built: raises `TypeError`.
12. Unlisted: PRD N-000279 ("a quoted empty string contributes an empty-string token") vs contract N-000480 ("adds no token"). Built the contract: no token.

## Not done / approximated
- No models/corpora ship (spec forbids); everything reading Punkt/tagger/stopwords/WordNet/NE models raises `lingora.data.ResourceNotFound` (a `LookupError`) when absent. Default `data.path` = `$LINGORA_DATA` entries, `~/lingora_data`, `<repo>/lingora_data`.
- Snowball: english, porter, german, dutch, swedish, norwegian, danish, spanish, french, italian, portuguese, russian were written from the published algorithms but not verified against reference vocabularies. **arabic, finnish, hungarian, romanian are simplified approximations** (main suffix steps only) — stems may differ from Snowball 2.2.
- ARLSTem/ARLSTem2 share one simplified Arabic light stemmer (results out of spec).
- `ne_chunk`: checks the model dir and wordlist exist (raises otherwise); with them present it returns a flat tree with no entities (results out of spec).
- `WordNetLemmatizer`: minimal morphy over `index.*`/`*.exc` files; raises when `corpora/wordnet` is absent.
- Chunk grammar supports chunk `{}` and chink `}{` rules only (no split/merge). `RecursiveDescentParser` is an alias of the exhaustive chart parser.
- Tweet tokenizer does not unescape HTML entities.
