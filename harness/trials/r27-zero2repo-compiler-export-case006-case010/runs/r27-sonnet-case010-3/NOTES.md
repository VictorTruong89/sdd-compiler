# Implementation notes

Package `lingora` (flat layout, pure Python, stdlib only) lives in `/app/lingora`; no build step.
Resources are read through `lingora.data.path` (mutable list; initial contents: `$LINGORA_DATA`, `~/lingora_data`,
`/usr/share/lingora_data`, `/usr/local/share/lingora_data`). Nothing is shipped or downloaded.

Checklist accounting: every N-id in `spec/CHECKLIST.md` belongs to a behaviour implemented in the module for its
pack (tokenize, stem, tag, chunk, parse/grammar/tree, classify, metrics/translate, cli, data). Not implemented
or only approximated (results declared outside the specification, or not feasible from the spec text):
- Snowball stemmers for arabic, finnish, french, hungarian, italian, portuguese, romanian, russian, spanish:
  names are accepted but `stem` only returns the lowercased word. english, porter, german, dutch, swedish,
  norwegian, danish are implemented.
- ARLSTem/ARLSTem2: light approximation (results outside spec). WordNetLemmatizer: simple morphy over the
  WordNet `index.*`/`*.exc` files; raises LookupError when `corpora/wordnet` is not visible.
- `ne_chunk`: checks the model and wordlist are visible (raises LookupError otherwise) but marks no entities.
- Porter modes other than the default exist but are lightly exercised.

## Contradictions and what was built (the Interface Contract wins when the two documents disagree)
- CF-000001: PRD N-000094 "A straight double quote at the start of the text ... opening-quote token" vs N-000106
  "A straight double quote at the very start of the text becomes the closing-quote token" (Recommended tokenizer).
  Built: Treebank tokenizer -> opening ``; `word_tokenize` -> closing ''.
- CF-000054: N-000067 tweet tokenizer "lowercases its tokens unless the caller asks to preserve case" vs N-000125
  "tokens are lowercased, except emoticons". Built: emoticons keep their case.
- CF-000077: PRD N-000118 "(it is on by default)" for empty-discarding vs Interface N-000407 "`discard_empty` is off
  unless the caller passes `discard_empty=True`". Built: default off for `RegexpTokenizer`; the whitespace and
  blank-line tokenizers always drop empty pieces.
- CF-000083: N-000102 fused forms incl. *cannot* "are split" vs N-000110 "*cannot* is kept as one token".
  Built: Treebank tokenizer splits cannot (can + not); recommended `word_tokenize` keeps it.
- CF-000073: PRD N-000158 four-letter *-ies* -> *-ie* vs Interface N-000424 "Step 1a as published, so *ties* stems
  to *ti*". Built: ties -> ti (Interface). Also Interface `to_lowercase=False` default (PRD N-000154 says
  lowercase first): built default False; the rest of the PRD extensions (ied, y->i, alli, bli, fulli, logi, irregular
  table, short words) are implemented.
- CF-000028: N-000240 "Two matches that touch are two separate chunks" vs N-000242 "Chunks that touch ... are joined
  into one chunk". Built: touching matches stay separate chunks.
- CF-000072 / CF-000008 / CF-000039 (N-000318, N-000343, N-000502 raise vs N-000331 fraction over shared positions):
  built raising ValueError on different lengths.
- CF-000016 / CF-000055 / CF-000070 (N-000325/327 unrestricted Damerau-Levenshtein vs N-000505/506 adjacent-only
  transposition): built the adjacent-only transposition (Interface).
- CF-000038: N-000334 "f-measure is 0 when precision or recall is 0" vs N-000346 "share no element -> no number".
  Built: `None` for disjoint sets.
- Not in the conflict list but contradictory: precision/recall given a list or tuple: PRD N-000332 "read as the set of
  its elements" vs Interface N-000508/509 "A non-set argument makes the call raise" -> raises TypeError.
- BLEU default weights: PRD N-000338 "equal weights on unigrams through 4-grams" vs Interface N-000514/515
  "unigrams and bigrams equally, longer n-grams not scored" -> built (0.5, 0.5).
- Generator empty-string terminal: PRD N-000279 "contributes an empty-string token" vs Interface N-000480 "adds no
  token" -> adds no token.
- Tree with a string child list: PRD N-000283 "taken as a single leaf" vs N-000288/Interface N-000486 refused -> raises
  TypeError.
