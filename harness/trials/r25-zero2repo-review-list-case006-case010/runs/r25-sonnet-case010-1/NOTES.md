# NOTES

Code lives in the `lingora/` package at the repo root (no build step; put `/app` on the import path).
`lingora.data.path` is the resource search list; resources are read exactly as in the Interface Contract.

## Conflicts in the specification and what was built

For each conflict I followed the PRD (the behavioural document) unless the Contract's statement
is the only one that makes a failure observable, as noted.

1. **Porter default lowercasing.** PRD FP-02: "The word is lowercased first, unless the caller turns lowercasing off."
   Contract (Stemmers): "`to_lowercase` defaults to `False`, so `stem` keeps the letter case it is given."
   Built: `to_lowercase=True` by default (PRD).
2. **Porter Step 1a on "ties".** PRD: four-letter word ending in *-ies* becomes *-ie*. Contract: "applies Step 1a as published, so *ties* stems to *ti*."
   Built: `ties` -> `tie` (PRD, default mode = LINGORA extensions).
3. **Chunk rule touching matches.** PRD FP-04: "Two matches that touch are two separate chunks" vs "Chunks that touch, with no token between them, are joined into one chunk."
   Built: touching matches stay separate chunks (the first statement); chunks are never merged.
4. **Tree built from a string child list.** PRD FP-05 Trees: "A string given in place of the child list is taken as a single leaf" vs PRD boundary and Contract: a `str` as `children` raises.
   Built: `Tree(label, "x")` raises `TypeError`; omitting children raises; `Tree(label, [])` is valid.
5. **Chart parser, token no production produces.** PRD Chart parser: "none for ... one holding a token that no production produces" vs PRD boundary + Contract: `parse` raises.
   Built: `parse` raises `ValueError` for uncovered tokens; a covered but underivable list gives an empty iterator.
6. **Contract's own empty-iterator vs raise (lines "gives an empty iterator" / "makes parse raise").** Resolved as in 5. Same for `ShiftReduceParser`.
7. **Empty terminal in the generator.** PRD: a quoted empty string contributes an empty-string token; Contract: adds no token.
   Built: PRD — it contributes `''`; an empty production contributes nothing.
8. **Accuracy on different lengths.** PRD Accuracy: "fraction over the positions both lists have" vs PRD boundary/Contract: raise.
   Built: `metrics.accuracy` raises `ValueError`.
9. **Precision/recall on lists/tuples.** PRD: "A list or tuple ... is read as the set of its elements" vs PRD boundary/Contract: refused.
   Built: non-set arguments raise `TypeError`.
10. **F-measure when precision or recall is 0.** PRD: "It is 0 when precision or recall is 0" vs PRD boundary: disjoint sets return no number.
    Built: `None` when either set is empty (precision/recall undefined); `0` for non-empty disjoint sets.
11. **Edit distance with transpositions.** PRD: unrestricted Damerau-Levenshtein (Lowrance-Wagner) vs Contract: only adjacent characters, nothing inserted between.
    Built: unrestricted (PRD); `edit_distance('ca','abc',transpositions=True) == 2`.
12. **BLEU default weights.** PRD: equal weights on 1- to 4-grams vs Contract: unigrams and bigrams only.
    Built: `(0.25, 0.25, 0.25, 0.25)` (PRD).
13. **RegexpTokenizer `discard_empty` default.** PRD: on by default vs Contract: off unless passed.
    Built: default `True` (PRD).
14. **Tweet tokenizer case.** PRD Unicode constraint: lowercases unless asked to preserve case vs PRD FP-01: case preservation on by default.
    Built: `preserve_case=True` default (FP-01); `preserve_case=False` lowercases except emoticons.
15. **Nonterminal symbol type.** Contract: symbol may be `str` vs `rhs()` nonterminals must not be `str`.
    Built: nonterminals are `Nonterminal` objects (`str()` = name, not a `str` subclass); terminals are plain `str`. Tree labels are plain `str`.

## Known limitations

* Snowball: only `english` (Porter2) and `porter` are implemented; the other listed languages are accepted
  by the constructor but `stem()` raises `NotImplementedError`. ISRI/ARLSTem/Cistem/RSLP, the WordNet
  lemmatizer (raises when WordNet is missing, else NotImplementedError), and the named-entity chunker
  (raises when its model/wordlist are missing, else NotImplementedError) are outside the specified results.
* Tweet tokenizer URL/phone patterns are simplified.
* Contract inconsistency left as is: `word_tokenize` default `language='english'`, `preserve_line=False`.
