# Implementation notes

Pure-Python package `lingora` at the repo root (no build step; put `/app` on the import path).
`lingora.data.path` is the mutable resource search list; `lingora.data.find()` resolves resources.
The CLI (`lingora.cli.cli.main`) is a small built-in group object (no `click` dependency).

## Spec disagreements and what was built

1. **Porter `ties`.** Interface_Contract (Stemmers): "Step 1a as published, so *ties* stems to *ti*". Full_PRD FP-02: "a four-letter word ending in *-ies* becomes *-ie*". Built the PRD rule (`ties` -> `tie`, default mode).
2. **Porter `to_lowercase` default.** Contract: "`to_lowercase` defaults to `False`, so `stem` keeps the letter case". PRD FP-02: the word "is lowercased first, unless the caller turns lowercasing off". Built: default `True` (lowercases).
3. **`RegexpTokenizer` `discard_empty` default.** Contract: "`discard_empty` is off unless the caller passes `discard_empty=True`". PRD FP-01: "dropped unless the caller turns empty-discarding off (it is on by default)". Built: default `True`.
4. **Tree built from a string child list.** PRD FP-05 Normal behavior: "A string given in place of the child list is taken as a single leaf"; PRD boundary section and Contract: such a call is refused. Built: `Tree('A', 'b')` raises `TypeError`.
5. **Generator and empty-string terminal.** Contract: "A terminal that is the empty string adds no token". PRD FP-05: "A quoted empty string contributes an empty-string token". Built: PRD behaviour (the `''` token is emitted; empty productions add nothing).
6. **Edit distance with transpositions.** PRD FP-07: unrestricted Damerau–Levenshtein (characters may be inserted between the transposed pair). Contract: only adjacent characters in both strings, nothing inserted between. Built: the Contract's restricted (adjacent-only) variant.
7. **`accuracy` with lists of different length.** PRD FP-07 normal behavior: fraction over the positions both lists have; PRD boundary section and Contract: raises. Built: raises `ValueError`.
8. **`precision`/`recall` with list/tuple arguments.** PRD FP-07: a list or tuple "is read as the set of its elements"; PRD boundary + Contract: non-set arguments are refused. Built: `TypeError`.
9. **`f_measure` for disjoint non-empty sets.** PRD normal behavior: "0 when precision or recall is 0"; PRD boundary: no number when the sets share no element. Built: returns `0` (precision/recall 0); `None` only if either set is empty.
10. **BLEU default weights.** PRD FP-07: default equal weights on unigrams..4-grams; Contract: omitted `weights` means unigrams and bigrams equally weighted. Built: 4-gram equal weights `(0.25,)*4`. A `smoothing_function=` keyword (callable on the list of `Fraction` precisions, with `references`, `hypothesis`, `hyp_len` keywords) is accepted.
11. **Chunk rules whose matches touch.** PRD says both "two matches that touch are two separate chunks" and "chunks that touch ... are joined into one chunk". Built: separate chunks.

## Known limitations

* `SnowballStemmer` implements only `english` (Porter2) and `porter`. The other listed languages construct successfully (name validation, stopword checking) but `stem()` raises `NotImplementedError`.
* `ARLSTem`/`ARLSTem2` are light approximations; their results are outside the spec.
* `ne_chunk` checks that the NE model dir and `corpora/words` are visible (raises otherwise) but does not interpret the maxent model; it returns the input tokens unchunked under an `S` root.
* `WordNetLemmatizer` reads `index.<pos>` and `<pos>.exc` files with simple morphy rules.
* Without a Punkt model on `data.path`, `sent_tokenize`, `word_tokenize(preserve_line=False)` and the CLI raise / exit non-zero.
