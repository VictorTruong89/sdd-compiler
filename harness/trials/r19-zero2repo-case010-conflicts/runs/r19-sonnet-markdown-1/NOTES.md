# Implementation notes

Pure-Python package `lingora` at the repo root (no install step; put `/app` on the import path).
Packaged models are read from the directories in `lingora.data.path` (initial contents: `$LINGORA_DATA`,
`~/lingora_data`, `/usr/share/lingora_data`, plus the usual `nltk_data` locations). No third-party dependencies;
the CLI is a small built-in click-like group (`lingora.cli.cli.main(args=..., standalone_mode=...)`).

## Spec disagreements and what was built

1. **Porter `ties`.** Interface Contract (Stemmers): "`PorterStemmer` applies Step 1a as published, so *ties* stems to *ti*".
   PRD FP-02: "In Step 1a, a four-letter word ending in *-ies* becomes *-ie* rather than *-i*". Built: the PRD rule (`ties` -> `tie`).
2. **Porter `to_lowercase` default.** Contract: "`to_lowercase` defaults to `False`, so `stem` keeps the letter case". PRD FP-02:
   "The word is lowercased first, unless the caller turns lowercasing off". Built: default `True`.
3. **`edit_distance` with transpositions.** PRD FP-07: unrestricted Damerau-Levenshtein (characters may be inserted between the
   transposed pair). Contract: only adjacent characters in both strings, nothing inserted/deleted between them. Built: the contract's
   restricted (optimal string alignment) variant.
4. **`accuracy` with different lengths.** PRD FP-07 says "for lists of different lengths, it is that fraction over the positions both lists
   have", but the same PRD (FP-06/FP-07 boundary sections) and the Contract say it raises. Built: raises `ValueError`.
5. **`f_measure` for non-empty disjoint sets.** PRD boundary: "f-measure ... when the two sets share no element return no number";
   PRD normal behavior: "It is 0 when precision or recall is 0". Built: `None` if either set is empty, `0.0` for disjoint non-empty sets.
6. **BLEU default weights.** PRD: equal weights on unigrams through 4-grams. Contract: when omitted, unigrams and bigrams equally,
   no longer n-grams. Built: PRD (0.25 x 4). Smoothing: `bleu(..., smoothing_function=callable)`; `lingora.translate.bleu_score.SmoothingFunction` provides methods.
7. **`RegexpTokenizer` `discard_empty` default.** PRD FP-01: empty pieces dropped unless the caller turns it off (on by default).
   Contract: "`discard_empty` is off unless the caller passes `discard_empty=True`". Built: default `True` (PRD).
8. **`TweetTokenizer` `preserve_case` default.** PRD FP-01: case preservation "is on by default"; PRD Unicode constraint: it "lowercases
   its tokens unless the caller asks to preserve case". Built: default `True` (no lowercasing).
9. **`generate` with an empty-string terminal.** PRD FP-05: "a quoted empty string contributes an empty-string token". Contract:
   "A terminal that is the empty string adds no token to a sentence". Built: the contract (the empty string is dropped from the sentence);
   an empty production also adds no token.
10. **`Tree(label, "str")`.** PRD FP-05 says "A string given in place of the child list is taken as a single leaf" but also (boundary) that
    it is refused; Contract says it raises. Built: raises `TypeError`; omitting `children` also raises.
11. **Touching chunks.** PRD FP-04 says "Two matches that touch are two separate chunks" and also "Chunks that touch ... are joined into one
    chunk". Built: touching matches stay separate chunks.
12. **Recursive-descent parser** exists only as an alias of the exhaustive chart parser (results unspecified).

## Known limits
- Snowball: English, Porter (original algorithm), German, Dutch, Swedish, Danish, Norwegian, Spanish, French, Italian, Portuguese and
  Russian are real implementations of the published rules but only English/Porter were checked carefully; Finnish, Hungarian,
  Romanian and Arabic are simplified suffix strippers.
- `ne_chunk` checks the model/wordlist are visible (raises `LookupError` otherwise) and then groups runs of proper nouns; no maxent model.
- `ARLSTem`/`ARLSTem2` are light approximations (results unspecified by the PRD). `WordNetLemmatizer` needs `corpora/wordnet`.
