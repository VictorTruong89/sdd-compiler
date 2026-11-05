# NOTES

Layout: flat package `lingora/` (tokenize, punkt, stem, tag, chunk, grammar, parse/, tree, classify, metrics, translate, cli, data). No dependencies, no build step. `lingora.data.path` defaults to `/app/lingora_data`, `~/lingora_data` and `$LINGORA_DATA`; resources are looked up on every call. No models/corpora are shipped.

## Conflicts: what the spec says on each side, and what I built
(Rule of thumb: where one side matches the well-known behaviour of the algorithm named in the spec, I followed it.)

- CF-000001 (Pack 22, N-000094 vs N-000106): straight `"` at the very start of the text is the *opening* quote (PRD Treebank bullet) vs "closing-quote token" (recommended tokenizer bullet). Built: opening ``` `` ```.
- CF-000054 (N-000067 vs N-000125): tweet tokens lowercased unless preserve_case vs "except emoticons". Built: emoticons keep case.
- CF-000077 (N-000118 vs N-000407): `discard_empty` "on by default" (PRD) vs "off unless True" (Contract, pack 07). Built: Contract (default False) for RegexpTokenizer; WhitespaceTokenizer and blankline_tokenize discard empties internally.
- CF-000083 (N-000102 vs N-000110): `cannot` split into two parts vs kept as one in the recommended tokenizer. Built: split into `can` + `not` in both tokenizers.
- CF-000073 (N-000158 vs N-000424): 4-letter `-ies` -> `-ie` (PRD) vs "Step 1a as published, ties -> ti" (Contract). Built: PRD (`ties` -> `tie`).
- CF-000091 (N-000154 vs N-000426): lowercase by default vs `to_lowercase` defaults False. Built: default `True` (PRD).
- CF-000028 (N-000240 vs N-000242): touching matches are separate chunks vs joined. Built: separate chunks (each rule match is its own chunk).
- CF-000088 (N-000282 vs N-000288): string child list "taken as a single leaf" vs refused. Built: refused (TypeError); missing children also TypeError; `[]` fine.
- CF-000089 (N-000279 vs N-000480): quoted empty string adds an empty-string token vs adds no token. Built: adds no token (Contract).
- CF-000090 (N-000267 vs N-000292): unknown token -> no trees vs failure. Built: ValueError (call raises).
- CF-000008/000039/000072 (accuracy on unequal lengths: fraction over shared positions vs raises). Built: `ValueError`.
- CF-000016/000055/000070 (edit distance transpositions: unrestricted Damerau-Levenshtein vs adjacent only). Built: unrestricted Lowrance-Wagner (PRD, N-000325/N-000327); `edit_distance('ca','abc',transpositions=True) == 2`.
- CF-000038 (N-000334 vs N-000346): f-measure for disjoint non-empty sets: 0 vs None. Built: 0.0; `None` only when precision or recall is None (empty sets).
- CF-000086 (N-000332 vs N-000345): precision/recall accept list/tuple vs refuse. Built: refuse non-set (TypeError), per Contract.
- CF-000087 (N-000338 vs N-000515): BLEU default weights 1..4-grams vs unigram+bigram. Built: four equal weights (PRD).

## Not done / approximations
- Snowball: `english` (Porter2) and `porter` are real implementations. The other 14 language names are accepted but stemmed by a crude approximate suffix stripper (not the Snowball algorithms).
- Lancaster: engine is faithful, rule table was reconstructed from memory and may be incomplete.
- ARLSTem/ARLSTem2 are simplified light stemmers; results are outside the spec.
- `ne_chunk` checks that the model dir and `corpora/words` exist (raises otherwise) but does not interpret the maxent model; returns tagged tokens under the root. Results with resource present are outside the spec.
- WordNetLemmatizer: simple morphy over `index.*`/`*.exc` files; raises at construction if `corpora/wordnet` is missing.
- Chink/chunk rules supported; split/merge rule forms of chunk grammars are not.
- Every checklist id (CHECKLIST.md) is either implemented by the above or listed here; no per-id `# spec:` marking was done beyond a few comments.
