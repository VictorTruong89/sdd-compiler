# NOTES

Package: `lingora/` (flat layout at `/app`; no build step; run with `/app` on the import path or `python -m lingora tokenize`).
Resources are located through `lingora.data.path` (a mutable list; default entries are `~/lingora_data`, `/usr/share/lingora_data`, `/usr/local/share/lingora_data`, `/app/lingora_data`).

## Conflicts in the specification and what I built

Each item: what each side says, then my choice.

- **Porter default lowercasing (C-01).** PRD FP-02: "The word is lowercased first, unless the caller turns lowercasing off." Contract (Stemmers): "`to_lowercase` defaults to `False`, so `stem` keeps the letter case it is given." Built: PRD behaviour; `to_lowercase` defaults to `True`.
- **Porter Step 1a on "ties" (C-02).** PRD: a four-letter word ending in *-ies* becomes *-ie*. Contract: "`PorterStemmer` applies Step 1a as published, so *ties* stems to *ti*." Built: PRD, `ties` -> `tie`.
- **Touching chunks (C-03).** PRD FP-04 "Chunk rule": "Two matches that touch are two separate chunks." and "Chunks that touch, with no token between them, are joined into one chunk." Built: the first statement; touching matches stay separate chunks (the behaviour of the brace-string chunker).
- **`Tree(label, "x")` (C-04).** PRD FP-05 Trees: "A string given in place of the child list is taken as a single leaf." PRD boundary and Contract: a `str` as children "makes `Tree` raise". Built: raises `TypeError` (also when `children` is omitted).
- **Token no production produces (C-05, C-06).** PRD Chart parser / Contract line "A token list the grammar does not derive gives an empty iterator" say an empty result; PRD boundary and Contract say such a token "makes `parse` raise". Built: `parse` raises `ValueError` at call time for a token no production produces; an uncovered-but-known token list gives an empty iterator. Applies to both Chart and Shift-reduce parsers.
- **Empty terminal in generator (C-07).** PRD: "A quoted empty string contributes an empty-string token." Contract: "A terminal that is the empty string adds no token to a sentence." Built: PRD; `''` appears as a token in the sentence. An empty production adds nothing. (Parse trees contain no leaf for an empty terminal.)
- **Accuracy with different lengths (C-08).** PRD FP-07 normal text: fraction over common positions; PRD boundary and Contract: raise. Built: raises `ValueError`.
- **Precision/recall with lists (C-09).** PRD normal text: a list or tuple is read as a set; PRD boundary and Contract: non-set raises. Built: raises `TypeError` for non-`set`/`frozenset`.
- **f-measure with no overlap (C-10).** PRD: "It is 0 when precision or recall is 0." PRD boundary: f-measure "when the two sets share no element return no number". Built: returns `0.0` for non-empty sets with no overlap; `None` only when either set is empty.
- **Edit distance with transpositions (C-11).** PRD: unrestricted Damerau–Levenshtein (insertions/deletions between the transposed pair allowed). Contract: only adjacent transposition, nothing in between. Built: PRD (unrestricted, Lowrance–Wagner); `edit_distance('ca','abc',transpositions=True) == 2`.
- **BLEU default weights (C-12).** PRD: equal weights for 1- to 4-grams. Contract: "unigrams and bigrams are weighted equally". Built: PRD, `(0.25,)*4`. Smoothing is via `smoothing_function=` (see `SmoothingFunction`).
- **RegexpTokenizer `discard_empty` (C-13).** PRD: on by default. Contract: "`discard_empty` is off unless the caller passes `discard_empty=True`." Built: default `True` (PRD).
- **TweetTokenizer case (C-14).** PRD Unicode paragraph: lowercases unless asked to preserve case; PRD FP-01: case preservation is on by default. Built: `preserve_case=True` by default (no lowercasing by default).
- **Nonterminal symbol type (C-15).** Contract: symbol may be `str`, but `rhs()` nonterminals must not be `str`. Built: a `Nonterminal` object (its `str()` is the name); terminals in `rhs()` are plain `str`.

## Other decisions / limitations

- Treebank tokenizer does not split `--`; the recommended `word_tokenize` does (as the PRD lists it as an improvement). Recommended tokenizer keeps `cannot` whole; the Treebank tokenizer splits it into `can` + `not`.
- Edge cases: `metrics.accuracy([], [])`, `jaccard_distance(set(), set())` return `0.0`.
- Snowball: English (Porter2), `porter` (original Porter), German, Dutch, Swedish, Norwegian and Danish are written out from the Snowball algorithms. The remaining languages (arabic, finnish, french, hungarian, italian, portuguese, romanian, russian, spanish) are accepted but use an approximate suffix stripper, not the full Snowball algorithm. ARLSTem/ARLSTem2, Cistem, RSLP, ISRI are outside the spec; ARLSTem/ARLSTem2 are light approximations. `WordNetLemmatizer` raises when WordNet is absent (lookup itself is not implemented).
- Lancaster uses the Paice/Husk rule table reconstructed from memory; a few rules may differ from the published table.
- `ne_chunk` checks for the model and wordlist and raises when they are missing; with them present it raises `NotImplementedError` (results outside the spec).
- Punkt: algorithm implemented from the paper using the packaged parameter files (`abbrev_types.txt`, `sent_starters.txt`, `collocations.tab`, `ortho_context.tab`); the model is read on each call so changes to `data.path` take effect.
- CLI: `cli.main(args=['tokenize'])`; options `-l/--language`, `-d/--delimiter`, `-e/--encoding`. All lines are tokenized before anything is written, so a missing Punkt model gives exit status 1 and no output.
