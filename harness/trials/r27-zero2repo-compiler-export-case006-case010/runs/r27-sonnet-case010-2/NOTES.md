# Lingora build notes

Pure-Python package `lingora` at `/app/lingora` (no dependencies, no build step; put `/app` on the path).
Modules: `data`, `tokenize` (incl. Punkt), `cli`, `stem`, `tag`, `chunk`, `grammar`, `parse` (+`parse.generate`),
`tree`, `classify`, `metrics`, `translate`. `python -m lingora tokenize` runs the CLI (own small
click-like `Group.main(args, standalone_mode)`, since click is not installed).
`data.path` defaults to `<repo>/lingora_data`, `~/lingora_data` and two `/usr/share` dirs; no corpora are shipped.

Every CHECKLIST id is implemented unless listed under "Not done / approximate" below.

## Disagreements in the spec and what I built
The Interface Contract (pack 05-15) was treated as more authoritative than the PRD where they clash.

1. CF-000001: N-000094 (PRD FP-01) "a straight double quote at the start of the text ... becomes the opening-quote token" vs
   N-000106 "A straight double quote at the very start of the text becomes the closing-quote token" (recommended tokenizer).
   Built: `TreebankWordTokenizer` gives the opening token ``` `` ```; `word_tokenize` gives closing `''` at text start.
2. CF-000054: N-000067 (non-functional) tweet tokenizer "lowercases its tokens unless the caller asks to preserve case" vs
   N-000125 "tokens are lowercased, except emoticons". Built: emoticons keep their case.
3. CF-000077: N-000118 (FP-01) discard_empty "is on by default" vs N-000407 (contract) "off unless the caller passes discard_empty=True".
   Built: off by default for `RegexpTokenizer`. (`WhitespaceTokenizer` / `blankline_tokenize` drop empty pieces as FP-01 states.)
4. CF-000083: N-000102 "fused forms cannot ... are split" vs N-000110 "cannot is kept as one token" (recommended tokenizer).
   Built: Treebank tokenizer splits `can` + `not`; `word_tokenize` keeps `cannot`.
5. CF-000073: N-000158 (FP-02) "four-letter word ending in -ies becomes -ie" vs N-000424 (contract) "Step 1a as published, so ties stems to ti".
   Built: `ties` -> `ti` (Step 1a as published); the other LINGORA extensions (ied, *o, 1c, step 2) stay.
6. Porter lowercasing: N-000154 (PRD) "The word is lowercased first, unless the caller turns lowercasing off" vs N-000425/426 (contract)
   `to_lowercase` defaults to False. Built: default False (case kept); `to_lowercase=True` lowercases.
7. CF-000028: N-000240 "Two matches that touch are two separate chunks" vs N-000242 "Chunks that touch ... are joined into one chunk".
   Built: separate chunks (one per match).
8. CF-000008 / CF-000039 / CF-000072: N-000331 accuracy over shared positions for different lengths vs N-000343 / N-000318 / N-000502 "does not succeed / raises".
   Built: `metrics.accuracy` raises `ValueError` on different lengths.
9. CF-000016 / CF-000055 / CF-000070: N-000325-327 unrestricted Damerau-Levenshtein (insertions between transposed chars) vs N-000505/506
   adjacent-only transposition with nothing between. Built: adjacent-only (optimal string alignment).
10. CF-000038: N-000334 "f-measure is 0 when precision or recall is 0" vs N-000346 "returns no number when the two sets share no element".
    Built: `None` for disjoint sets (and empty sets).
11. N-000332 "A list or tuple given as either argument is read as the set of its elements" vs N-000344/N-000508/509 (non-sets are refused).
    Built: `TypeError` for non-set arguments.
12. N-000338 (PRD) BLEU default "equal weights on unigrams through 4-grams" vs N-000514/515 (contract) default unigrams and bigrams equally.
    Built: default weights `(0.5, 0.5)`.
13. N-000280 (PRD) "A quoted empty string contributes an empty-string token" vs N-000480 (contract) "adds no token". Built: no token.
14. N-000284 (PRD) "A string given in place of the child list is taken as a single leaf" vs N-000486/N-000290 (refused). Built: `TypeError`.

## Not done / approximate
- Snowball: english (Porter2), porter, german, dutch, swedish, norwegian, danish, russian, spanish, french, italian, portuguese are
  written from the published algorithms from memory and unverified against the reference. finnish, hungarian, romanian and arabic
  are light suffix-stripping approximations only.
- ARLSTem / ARLSTem2: light approximations (results are outside the spec). Porter ORIGINAL/MARTIN modes exist but are lightly checked.
- `ne_chunk` checks that the NE model and wordlist are visible (raises otherwise) but does not run the maxent model (results outside spec).
- `RegexpParser` supports chunk and chink rules (no split/merge/expand rules). Recursive-descent parser not provided (outside spec).
- Bigram/trigram/affix taggers not provided (outside spec). Shift-reduce skips empty productions.
- Throughput, GUI, corpora, external wrappers: non-goals.
