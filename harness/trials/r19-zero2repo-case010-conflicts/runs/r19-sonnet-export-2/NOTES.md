# NOTES

Package: `/app/lingora` (flat layout, pure Python, no dependencies; `python -m lingora tokenize` or `lingora.cli.cli.main`).
No packaged models are shipped; resources are looked up on `lingora.data.path` (initial contents: `$LINGORA_DATA` entries, `~/lingora_data`, `/usr/share/lingora_data`).

## Spec conflicts and what was built
Rule of thumb: where the two sides disagree I followed the behaviour of the well-known reference algorithm (the PRD side), except where the Contract was the only side that spoke to error behaviour.

- CF-000001 (Pack 22, PRD): Treebank "straight double quote at the start of the text" -> opening-quote (N-000094) vs recommended tokenizer "becomes the closing-quote token" (N-000106). Built: opening quote ``` `` ``` for both tokenizers.
- CF-000083: fused forms "are split into their two parts" incl. *cannot* (N-000102) vs "*cannot* is kept as one token" (N-000110). Built: *cannot* -> `can`, `not` in both tokenizers.
- CF-000077: RegexpTokenizer empty-discarding "on by default" (N-000118, PRD) vs "off unless discard_empty=True" (N-000407, Contract). Built: default `discard_empty=True`.
- CF-000054: tweet tokenizer lowercases all tokens (N-000067) vs "except emoticons" (N-000125). Built: emoticons keep case.
- CF-000073 / CF-000091: Porter Step 1a *ties*->*tie* (N-000158) vs Contract "*ties* stems to *ti*" (N-000424); lowercasing default on (N-000154) vs `to_lowercase` default False (N-000426). Built: *ties*->*tie*, `to_lowercase=True` default.
- CF-000028: chunk rule "two matches that touch are two separate chunks" (N-000240) vs "touching chunks are joined" (N-000242). Built: separate chunks (matches the regex-on-chunkstring mechanism).
- CF-000088: Tree "string given in place of child list is taken as a single leaf" (N-000282) vs refused (N-000288, N-000486). Built: refused (TypeError).
- CF-000089: generator quoted empty string contributes an empty-string token (N-000279) vs adds no token (N-000480). Built: contributes `''`.
- CF-000090: parser given token no production produces returns no trees (N-000267) vs must not succeed (N-000292, N-000475). Built: raises ValueError.
- CF-000008 / 000039 / 000072: accuracy on different lengths computed over shared positions (N-000331) vs raises (N-000343, N-000318, N-000502). Built: raises ValueError.
- CF-000016 / 000055 / 000070: edit distance transpositions: unrestricted Damerau–Levenshtein (N-000325/327) vs adjacent-only (N-000505/506). Built: unrestricted (Lowrance–Wagner).
- CF-000038: f-measure 0 when precision or recall 0 (N-000334) vs None when sets share no element (N-000346). Built: 0.0 for disjoint non-empty sets; None if either set empty.
- CF-000086: precision/recall accept list/tuple (N-000332) vs refuse non-sets (N-000345, N-000508/509). Built: refuse (TypeError).
- CF-000087: BLEU default weights 1..4-grams equal (N-000338) vs unigrams+bigrams only (N-000515). Built: (0.25,)*4.

## Not done / partial
- Snowball: English (Porter2) and `porter` are faithful. German, Dutch, Swedish, Danish, Norwegian, Spanish, Russian are close ports from the published algorithms; French, Italian, Portuguese are condensed; Finnish, Hungarian, Romanian, Arabic are light suffix strippers only (not the full Snowball algorithm).
- `ne_chunk`: checks that the model and wordlist are visible (raises LookupError otherwise) but the model format is not specified, so it then raises NotImplementedError.
- WordNetLemmatizer: simplified morphy over `index.*` / `*.exc` files; raises LookupError when WordNet not visible.
- ARLSTem/ARLSTem2: placeholder light stemmer (results outside spec). ISRI, Cistem, RSLP, bigram/affix taggers beyond Unigram/Bigram/Trigram, s-expression tokenizer, recursive-descent specific behaviour (aliased to the chart parser): not implemented / aliased.
- Hardware/packaging ids (packs 01–03, 05, 19): satisfied by a pure-Python flat package with no dependencies and no import-time downloads.
- Tests: `tests/test_basic.py` is a small smoke suite only.
