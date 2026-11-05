# NOTES

The spec export flagged 19 unsettled contradictions (`spec/MAP.md`, `--allow-open`). This file
lists each one: where each side says it, and what was built. Pack names refer to the files in
`spec/packs/`; "Contract" means the Interface Contract packs (01–15) and "PRD" the Full PRD packs
(16–29).

## How conflicts were resolved

- The PRD (pack 16) says exact call signatures and output forms "belong in the Interface Contract",
  so **parameter defaults and parameter meanings are taken from the Contract**.
- **Algorithm behaviour is taken from the PRD**, unless the Contract states the same entry's
  behaviour more specifically.
- Where two different tokenizers are each described (Penn Treebank vs. LINGORA's recommended word
  tokenizer), each keeps its own rule. Those are not really contradictions, but they are listed below.

## Unsettled contradictions

### CF-000001 — straight double quote at the start of the text

- **A (PRD, pack 22, claim N-000094)**: "A straight double quote at the start of the text, or after a
  space or an opening bracket, becomes the opening-quote token made of two backticks."
- **B (PRD, pack 22, claim N-000106)**: "A straight double quote at the very start of the text becomes
  the closing-quote token."
- **Built**: the Penn Treebank tokenizer (`TreebankWordTokenizer`) follows A, so `"` at the start
  gives ``` `` ```. The recommended word tokenizer (`word_tokenize`) follows B, so it gives `''`. B is
  an explicit "improvement" listed only for the recommended tokenizer.

### CF-000008, CF-000039, CF-000072 — accuracy on lists of different lengths

- **A (PRD, pack 28, claim N-000331)**: "For lists of different lengths, it is that fraction over the
  positions both lists have."
- **B (PRD, pack 28, N-000343; also PRD pack 27, N-000318)**: "Accuracy on two lists of different
  lengths does not succeed."
- **C (Contract, pack 15, claim N-000502)**: "Lists of different lengths make it raise."
- **Built**: `metrics.accuracy` raises `ValueError`. Three sources agree on refusal; only one says
  the fraction.

### CF-000016, CF-000055, CF-000070 — edit distance with transpositions

- **A (PRD, pack 28, N-000325)**: "the distance is the unrestricted Damerau–Levenshtein distance."
- **B (PRD, pack 28, N-000327)**: "characters may also be inserted between, or deleted from between,
  the two transposed characters."
- **C (Contract, pack 15, N-000505)**: "only two characters that stand next to each other in both
  strings may be transposed."
- **D (Contract, pack 15, N-000506)**: "nothing may be inserted or deleted between them."
- **Built**: the restricted form (optimal string alignment). Transpositions are adjacent-only and
  nothing is inserted between them. This is the Contract's specific description of the parameter. It
  also matches how NLTK implements this option. For example, `edit_distance('ca', 'abc', transpositions=True) == 3`.
  The unrestricted variant (PRD A/B) is not built.

### CF-000028 — touching chunk matches

- **A (PRD, pack 25, N-000240)**: "Two matches that touch are two separate chunks."
- **B (PRD, pack 25, N-000242)**: "Chunks that touch, with no token between them, are joined into one chunk."
- **Built**: A. Each non-overlapping match is its own chunk; touching matches are not joined.

### CF-000038 — f-measure when precision or recall is 0

- **A (PRD, pack 28, N-000334)**: "It is 0 when precision or recall is 0."
- **B (PRD, pack 28, N-000346/N-000347)**: "...when the two sets share no element return no number. That absence is distinguishable from the number 0."
- **Built**: B. For non-empty sets, precision and recall are both 0 exactly when the sets are disjoint,
  so A could only apply to a case B says returns no number. B's explicit "distinguishable from 0"
  wins. `f_measure` returns `None` for disjoint or empty sets.

### CF-000054 — tweet tokenizer lowercasing of emoticons

- **A (PRD, pack 19, N-000067)**: "that tokenizer lowercases its tokens unless the caller asks to preserve case."
- **B (PRD, pack 22, N-000125)**: "With case preservation off (it is on by default), tokens are lowercased, except emoticons."
- **Built**: B. Emoticons are never lowercased. Everything else is lowercased when `preserve_case=False`.

### CF-000073 — Porter Step 1a on "ties"

- **A (PRD, pack 23, N-000158)**: "In Step 1a, a four-letter word ending in *-ies* becomes *-ie* rather than *-i*."
- **B (Contract, pack 09, N-000424)**: "`PorterStemmer` applies Step 1a as published, so *ties* stems to *ti*."
- **Built**: the default mode (`NLTK_EXTENSIONS`, the LINGORA extensions) follows A, so `ties → tie`.
  `PorterStemmer(ORIGINAL_ALGORITHM)` gives `ti`, which is B's "as published" result. The PRD says the
  default mode is the LINGORA extensions. B's "as published" wording describes the original mode.

### CF-000077 — `discard_empty` default in the regexp tokenizer

- **A (PRD, pack 22, N-000118)**: "Empty pieces are dropped unless the caller turns empty-discarding off (it is on by default)."
- **B (Contract, pack 07, N-000407)**: "`discard_empty` is off unless the caller passes `discard_empty=True`."
- **Built**: B, the signature default, under the rule above. `RegexpTokenizer(..., discard_empty=False)`.
  Callers who want the PRD's behaviour pass `discard_empty=True`. This is the one place where the
  build's default differs from the PRD.

### CF-000083 — "cannot"

- **A (PRD, pack 22, N-000102)**: the fused forms "*cannot*, *d'ye*, … are split into their two parts (*can* + *not*…)".
- **B (PRD, pack 22, N-000110)**: "*cannot* is kept as one token."
- **Built**: each rule applies to its own tokenizer. Penn Treebank (A) splits `cannot` into `can not`.
  The recommended tokenizer (B) keeps `cannot` as one token. This follows the same Penn/recommended
  split as CF-000001.

### CF-000086 — precision and recall with lists

- **A (PRD, pack 28, N-000332)**: "A list or tuple given as either argument is read as the set of its elements."
- **B (PRD, pack 28, N-000345; Contract, pack 15, N-000509)**: "Lists, tuples and other non-set collections are refused." / "A non-set argument makes the call raise."
- **Built**: B. Non-set arguments raise `TypeError`.

### CF-000087 — BLEU default weights

- **A (PRD, pack 28, N-000338)**: "The default is equal weights on unigrams through 4-grams."
- **B (Contract, pack 15, N-000514/N-000515)**: "When `weights` is omitted, unigrams and bigrams are weighted equally and longer n-grams are not scored."
- **Built**: B, the Contract's signature default, so `weights=(0.5, 0.5)`. The 1–4-gram default is
  not built. Passing `weights=(0.25, 0.25, 0.25, 0.25)` gives the PRD's behaviour.

### CF-000088 — a string given as a tree's child list

- **A (PRD, pack 26, N-000282)**: "A string given in place of the child list is taken as a single leaf."
- **B (PRD, pack 26, N-000288; Contract, pack 13, N-000486)**: "Building a tree from a label and a string as the child list ... is refused." / "A `str` given as `children` ... makes `Tree` raise."
- **Built**: B. `Tree('S', 'ab')` raises `TypeError`.

### CF-000089 — quoted empty string in generation

- **A (PRD, pack 26, N-000279)**: "A quoted empty string contributes an empty-string token."
- **B (Contract, pack 12, N-000480)**: "A terminal that is the empty string adds no token to a sentence."
- **Built**: A, because the PRD governs algorithm behaviour. `generate` yields `['']` for a `""`
  terminal. Empty productions add nothing.

### CF-000090 — a token no production produces

- **A (PRD, pack 26, N-000267)**: the chart parser "returns none for a token list the grammar does not derive (including one holding a token that no production produces)".
- **B (PRD, pack 26, N-000292; Contract, pack 12, N-000475)**: "A parser given a token list that contains a token no production of the grammar produces does **not** succeed." / "A token that no production produces makes `parse` raise."
- **Built**: B. `parse` raises `ValueError`. An ordinary underivable list of known tokens returns an
  empty iterator.

### CF-000091 — Porter `to_lowercase` default

- **A (PRD, pack 23, N-000154)**: "The word is lowercased first, unless the caller turns lowercasing off."
- **B (Contract, pack 09, N-000426)**: "`to_lowercase` defaults to `False`."
- **Built**: B, the Contract's signature default. `stem` keeps the case it is given. `to_lowercase=True`
  lowercases first.

## Other disagreements found while reading (not on the unsettled list)

### Chunk patterns can match earlier chunks (a reading of the PRD)

- **A (PRD, pack 25, N-000236)**: "Every match of the pattern among tokens not yet in a chunk becomes one chunk."
- **B (PRD, pack 25, N-000246–N-000249)**: "A later clause sees every chunk built by an earlier clause as a single unit whose tag is that chunk's label, so it can chunk the remaining tokens…"
- **Built**: an earlier chunk counts as one unit with its label as its tag. A later pattern can match
  that unit, and the new chunk nests it. B's wording only makes sense if units are matchable. A
  strict reading of A would forbid the nesting, so this is a judgement call.

### Named-entity chunker and Snowball/other families (not built)

These are not contradictions. Their results are outside the spec (PRD pack 25 N-000231, pack 23
N-000143–N-000146, pack 26 N-000258–N-000261), or the spec gives no file format. See
`SPEC_COVERAGE.md`.
