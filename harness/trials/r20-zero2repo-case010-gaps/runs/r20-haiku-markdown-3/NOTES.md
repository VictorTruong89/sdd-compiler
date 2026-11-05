# LINGORA build notes

Build: pure-Python package `lingora/` at the repository root (flat layout, no
third-party dependencies, no build step). `spec/` is unchanged.
Run tests: `pytest -q` (smoke tests in `tests/`).

## Not implemented (read this first)

These parts are named by the spec but are **not** delivered as working algorithms.
Each fails visibly rather than returning wrong output.

- **Snowball stemmers for 14 of the 16 listed languages** (arabic, danish, dutch,
  finnish, french, german, hungarian, italian, norwegian, portuguese, romanian,
  russian, spanish, swedish). Only `english` (Porter2) and `porter` (original Porter)
  are implemented. Constructing the others raises `NotImplementedError`. Unsupported
  names raise `ValueError`. The spec gives no algorithm text for these languages
  (`spec/Full_PRD.md:144`), and I did not reproduce them from memory.
- **ARLSTem / ARLSTem2** (exist; `stem()` raises `NotImplementedError`). Their results
  are outside the spec (`spec/Full_PRD.md:142`).
- **WordNetLemmatizer**: raises `LookupError` when WordNet is not visible; otherwise
  `lemmatize()` raises `NotImplementedError`.
- **`ne_chunk`**: raises `LookupError` when the NE model or `corpora/words` is missing.
  With both present it raises `NotImplementedError`, because the packaged model format
  is not described in the spec.
- Bigram, trigram and affix taggers, and the recursive-descent parser: not included.
  The spec says their results are outside the specification
  (`spec/Full_PRD.md:183`, `:233`).

## Spec disagreements and ambiguities, and what was built

1. **Commas and colons in the Penn Treebank tokenizer.** `spec/Full_PRD.md:101`
   lists `; @ # $ % & ? !` and brackets as split characters, but not `,` or `:`. The
   same bullet list is described as "the Penn Treebank conventions", which split
   commas and colons. **Built:** `,` and `:` are split unless followed by a digit
   (so `1,000` stays whole). This follows the standard Treebank rule.

2. **Chunk-rule scope across clauses.** `spec/Full_PRD.md:218` says a chunk rule
   matches "tokens not yet in a chunk". `spec/Full_PRD.md:220` says a later clause
   sees earlier chunks as single units "so it can chunk the remaining tokens".
   **Built:** a later clause's chunk rule can match an earlier clause's chunk as one
   unit (its tag is the label), which is the cascade behaviour. A rule never matches
   tokens inside a chunk built earlier in the same clause, and chink rules only act on
   the current clause's chunks (`spec/Full_PRD.md:219`).

3. **`discard_empty` in token mode.** `spec/Full_PRD.md:118` sits under the
   regexp-tokenizer bullet, and `spec/Interface_Contract.md:62` gives `discard_empty`
   without a mode. **Built:** empty pieces are dropped in both token and gap modes.

4. **Recall with an empty reference set.** `spec/Full_PRD.md:310` says nothing about
   recall. Precision with an empty test set and f-measure with an empty set return
   "no number" (`None`). **Built:** recall with an empty reference returns `None`, so
   the same rule holds.

5. **Snowball `porter`.** `spec/Full_PRD.md:144` lists `porter` as a Snowball language,
   separately from the Porter stemmer modes in `spec/Full_PRD.md:146`. **Built:**
   `SnowballStemmer('porter')` is the original 1980 Porter algorithm.

6. **Failure of the CLI.** `spec/Interface_Contract.md:82` says no token line is
   written "for the failed input", and `spec/Full_PRD.md:134` says the command writes
   no token line. **Built:** the Punkt model is checked before any input is read, so a
   missing model produces no output lines and exit status 1.

7. **Refusal of a two-list `accuracy` on empty lists.** The spec states only the
   different-length case (`spec/Full_PRD.md:279`). **Built:** empty lists raise
   `ValueError` in both `metrics.accuracy` and `classify.accuracy`. A fraction is
   undefined there.

## Details the spec does not state (assumptions)

- **Packaged data finder.** Initial `data.path` is `$LINGORA_DATA` (os.pathsep
  separated) followed by `~/lingora_data`. Punkt model directories are looked up by
  name only; missing individual model files count as empty, but a missing directory
  is an error.
- **Punkt.** The spec gives the parameters, not the decision rules. I implemented
  Kiss & Strunk style rules: `?` and `!` always end a sentence; an ordinary period
  ends a sentence unless the next word is lowercase and the orthographic heuristic does
  not say "sentence starter"; abbreviation, initial and number periods end a sentence
  only when the next word is a known sentence starter that is capitalised, or the
  heuristic says it is one; collocations (`(type, next type)`) suppress a break. The
  orthographic heuristic follows the bit semantics given in the Interface Contract.
  Only tested against a small hand-made model (not a real Punkt model).
- **Treebank / recommended word tokenizer.** Typographic quotes are U+2018–U+201F.
  Dashes are U+2012–U+2015 plus `*`. Guillemets are not split. `''` and `` `` `` are
  produced for straight quotes. A final period is split before closing quotes or
  brackets. `e.g.` is not split mid-text. Penn Treebank spans are recovered by
  searching the original text.
- **Tweet tokenizer.** Emoticon, URL (`https?://` or `www.`) and hashtag/handle
  patterns are my choices. Runs of two or more dots are one token. Other punctuation
  is one token per character. A handle is `@` not preceded by a word character plus
  1–15 ASCII name characters, not followed by another name character.
- **Blank-line tokenizer.** Pieces are not stripped of surrounding spaces. Only empty
  pieces are dropped.
- **Porter (default LINGORA mode).** The irregular-form table is my own list
  (NLTK-style irregulars), since the spec defers it. The two other modes are named
  `ORIGINAL_ALGORITHM` and `MARTIN_EXTENSIONS`. `MARTIN_EXTENSIONS` (adds `bli`→`ble`,
  `fulli`, `logi`) is my assumption about those modes.
- **Porter2 (English Snowball).** Standard Snowball algorithm. R1 and R2 are computed
  once, from the word after the initial-y marking. Exceptional forms are handled as in
  Snowball.
- **Lancaster.** The spec refers to "the standard rule table published with it" but
  does not include it. The 96 rules in `lingora/stem.py` are reconstructed from memory
  and may differ from the published table. Some outputs I checked (`maximum`→`maxim`,
  `presumably`→`presum`, `nation`→`nat`, `friendship`→`friend`) are plausible, but this
  is unverified.
- **Snowball stopwords.** A stopword list is a UTF-8 file, one word per line, lowercased
  for comparison.
- **Unigram tagger.** Ties go to the lexicographically smaller tag. `train=None` gives
  an untrained tagger. The backoff tagger is consulted only for the tokens left untagged.
- **Regexp tagger.** Rules use `re.match` at the start of each token.
- **Averaged perceptron tagger.** Weights, tag dictionary and classes are read from the
  packaged JSON files as specified. The feature templates and normalisation follow the
  textblob-aptagger / NLTK `PerceptronTagger` design as I recall it. This is
  unverified against the real model.
- **Russian universal mapping.** The table in `lingora/tag.py` is my choice. Unknown
  tags map to `X`. English uses `taggers/universal_tagset/en-ptb.map`.
- **Chunk trees.** The root label is `S`. Chunk leaves are `(token, tag)` tuples.
  `pformat()` shows tagged leaves as `token/tag`. A grammar given as a list of stage
  objects is not supported (`TypeError`).
- **Grammar text.** Unquoted symbols are runs of non-space characters other than quotes
  and `|`. Lines starting with `#` are comments (not in the spec). A quoted `''` is the
  empty-string terminal.
- **Chart parser.** Returns every derivation tree over each span. A cycle guard stops
  unit or epsilon cycles from producing infinitely many trees.
- **Shift-reduce parser.** Reductions are tried in written order. Empty productions are
  never reduced in this pass (they cannot match a stack top; the chart parser handles
  epsilon derivations). A step budget guards against unit-production loops.
- **Generator.** `depth` bounds the derivation depth. Terminals at depth 0 are dropped,
  as in NLTK. Productions are expanded in written order.
- **Naive Bayes.** Laplace-smoothed: `P(v|l) = (count(f=v, l) + 1) / (examples of l with f + distinct values of f + 1)`.
  Features absent from a featureset, and features never seen in training, are ignored.
  Ties go to the first label seen in training.
- **Decision tree.** ID3 with information gain. Features are considered in name order.
  A feature missing from a featureset counts as `None`. Unseen values fall back to the
  node's majority label.
- **BLEU.** `smoothing_function` is an optional callable over `(numerator, denominator)`
  pairs (`SmoothingFunction.method0/1/2` provided). A hypothesis shorter than an order
  has no n-grams at that order and scores 0 even with smoothing.
- **CLI.** `click` is not installed in this environment and cannot be installed, so
  `lingora.cli.cli` is a small group object with the same `main(args=..., standalone_mode=...)`
  shape. Options: `--language` (default `english`), `--delimiter` (default one space),
  `--encoding` (default `utf-8`). Exit status 1 for a missing model; 2 for usage errors.
- **Edit distance.** Unrestricted Damerau–Levenshtein (Lowrance–Wagner) with
  transpositions. A transposition costs 1, and the substitution cost is the caller's.
- **Jaccard distance.** Both sets empty gives `0.0`. Non-set arguments raise `TypeError`.
- **Metrics refusals.** Non-set arguments to precision, recall and f-measure raise
  `TypeError`. Accuracy on lists of different lengths raises `ValueError`.

## Verification status

- Verified by my own checks: tokenizer rules, Punkt on a hand-made model, Porter and
  Porter2 on standard words, Lancaster on a few standard words, chunk cascades, chart
  and shift-reduce parsing, the generator, trees, classifiers, metrics and BLEU values.
- Not verified against reference outputs: the Lancaster table, the perceptron tagger
  (fake model only), real Punkt models, and the Porter modes other than the default.
- No packaged corpora or models are present in this environment, so the model-gated paths
  were exercised only with hand-made files outside `/app`.
