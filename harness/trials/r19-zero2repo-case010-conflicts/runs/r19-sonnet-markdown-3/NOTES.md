# Lingora build notes

Pure-Python package `lingora/` at the repo root (no build step; import from `/app`).
Resources are searched in `lingora.data.path` (initial: `$LINGORA_DATA`, `~/lingora_data`, `/usr/share/lingora_data`, ...).

## Spec disagreements and what was built

1. **`RegexpTokenizer` `discard_empty` default.** PRD (FP-01): empty-discarding "is on by default". Interface_Contract (Tokenizers): "`discard_empty` is off unless the caller passes `discard_empty=True`". Built: **on by default** (PRD).
2. **`PorterStemmer.stem` lowercasing.** PRD (FP-02): the word is lowercased first unless the caller turns it off. Contract (Stemmers): "`to_lowercase` defaults to `False`". Built: **`to_lowercase=True` default** (PRD).
3. **Porter Step 1a "ties".** PRD: a four-letter word ending in *-ies* becomes *-ie*. Contract: "Step 1a as published, so *ties* stems to *ti*". Built: **ties -> tie** (PRD).
4. **BLEU default weights.** PRD (FP-07): equal weights on unigrams through 4-grams. Contract: omitted `weights` means unigrams and bigrams equally. Built: **four equal weights (0.25 each)** (PRD).
5. **Edit distance with transpositions.** PRD: unrestricted Damerau-Levenshtein (insertions/deletions allowed between the swapped characters). Contract: only adjacent characters, nothing inserted or deleted between. Built: **adjacent-only transposition (optimal string alignment)** (Contract).
6. **Generator and the empty-string terminal.** PRD (FP-05): a quoted empty string contributes an empty-string token. Contract (Generation): such a terminal adds no token. Built: **an empty-string token `''` is emitted** (PRD).
7. **`accuracy` on unequal lengths.** PRD FP-07 normal behavior says the fraction is taken over the positions both lists have; the same PRD's boundary section, FP-06 and the Contract say it does not succeed/raises. Built: **raises `ValueError`**.
8. **`f_measure` for non-overlapping sets.** PRD normal behavior: "0 when precision or recall is 0"; PRD boundary section: sets sharing no element "return no number". Built: **returns `None`** (boundary section; Contract says `None` where the PRD says no number).

## Known limitations
- Snowball: `english` (Porter2) and `porter` are real implementations. The other listed languages are accepted by the constructor but use a light suffix stripper, not the full Snowball algorithm.
- Lancaster rule table was reconstructed from memory of the published Paice/Husk table.
- ARLSTem/ARLSTem2 are light approximations (outside spec). `ne_chunk` checks resources (raises `LookupError` when missing) but does not implement the model.
- Tweet tokenizer is a compact reimplementation of the usual casual-tokenizer regexes.
