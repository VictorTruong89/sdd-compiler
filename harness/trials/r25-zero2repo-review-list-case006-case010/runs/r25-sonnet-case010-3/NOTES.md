# NOTES

Pure-Python package `lingora` at the repo root (no dependencies, no build step). `conftest.py` and
`pyproject.toml` put the root on `sys.path` for pytest. Resources are searched on `lingora.data.path`
(initial contents: `$LINGORA_DATA`, `~/lingora_data`, `/usr/share/lingora_data`, nltk_data-style dirs).
The CLI is a small click-compatible group (`cli.main(args=[...], standalone_mode=...)`), with no click dependency.

## Spec conflicts and what I built

- **C-01 Porter lowercasing.** PRD FP-02 (line 155): word is lowercased unless the caller turns it off. Contract "Stemmers" (line 99): `to_lowercase` defaults to `False`. Built: PRD. `to_lowercase` defaults to `True`.
- **C-02 "ties".** PRD FP-02 (line 158): four-letter *-ies* becomes *-ie*. Contract (line 99): Step 1a "as published", so *ties* gives *ti*. Built: PRD, so `ties` gives `tie`.
- **C-03 Touching chunk matches.** PRD FP-04 (line 222) says two touching matches are two chunks and also that touching chunks are joined. Built: touching matches stay separate chunks (`{<NN>}` on NN NN gives two chunks). A single match is as long as possible, so `<NN>+` gives one.
- **C-04 `Tree(label, "x")`.** PRD FP-05 line 255 says a string child list is a single leaf. PRD line 263 and Contract line 195 say it is refused. Built: refused with `TypeError`. A missing child list is also refused. `Tree(label, [])` is valid.
- **C-05 / C-06 Token no production produces.** PRD line 251 says an empty result. PRD line 264 and Contract lines 174-175 say it raises. Built: `parse` raises `ValueError` from the call itself. A covered but underivable token list gives an empty iterator.
- **C-07 Empty-string terminal in `generate`.** PRD line 253 says it adds an empty-string token. Contract line 180 says it adds no token. Built: PRD, so a quoted `""` yields `''` in the sentence. An empty production adds nothing.
- **C-08 Accuracy on unequal lengths.** PRD line 306 gives a fraction over common positions. PRD line 319 and Contract line 231 say it raises. Built: `ValueError`.
- **C-09 Precision/recall on lists.** PRD line 308 reads lists as sets. PRD line 320 and Contract line 238 refuse them. Built: `TypeError` for non-set arguments.
- **C-10 F-measure with disjoint non-empty sets.** PRD line 309 gives 0. PRD line 320 gives no number. Built: `0.0`. `None` only when precision or recall is `None` (an empty set).
- **C-11 Edit distance transpositions.** PRD line 303 is unrestricted Damerau-Levenshtein (`ca` to `abc` is 2). Contract line 235 is the restricted version (3). Built: PRD (unrestricted).
- **C-12 BLEU default weights.** PRD line 312 is equal weights on 1- to 4-grams. Contract line 242 is 1- and 2-grams only. Built: PRD (0.25 x 4).
- **C-13 `RegexpTokenizer` `discard_empty` default.** PRD line 120 says on. Contract line 66 says off. Built: on (`True`).
- **C-14 Tweet tokenizer case.** PRD line 65 says lowercases by default. PRD line 127 says case preservation is on by default. Built: `preserve_case=True`, so no lowercasing by default.
- **C-15 Nonterminal symbol type.** Contract line 169 allows `str` symbols. Line 170 requires `rhs()` nonterminals to be non-`str`. Built: `Nonterminal` objects (not `str`); `str()` gives the name, terminals are plain `str`. Tree labels are `str`.

## Known gaps (outside the stated specification or not feasible here)

- Snowball: `english` (Porter2) and `porter` are implemented. The other listed languages construct fine (unsupported names and missing stopwords still raise as specified), but `stem()` raises `NotImplementedError`.
- ISRI, ARLSTem, ARLSTem2, Cistem, RSLP and the WordNet lemmatizer are simplified placeholders. The PRD marks their results out of scope.
- `ne_chunk` raises `LookupError` when the model or wordlist is missing. When both are present it raises `NotImplementedError`.
- Porter's original and Martin modes are approximations (results out of scope).
