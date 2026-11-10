# LINGORA build notes

Implementation of the LINGORA library described in `spec/`. The package is
`lingora/` at the repository root (flat layout). Run tests with `python3 -m pytest tests`.

Sources cited below: **PRD** = `spec/Full_PRD.md`, **Contract** = `spec/Interface_Contract.md`,
**HW** = `spec/Hardware_Requirements.md`. Line numbers are those files' lines.

## Resolution rule

The Contract says it does not restate what each entry computes; that is the PRD's job.
So where the two disagree on **computation or a default's behaviour**, the PRD wins. Where
they disagree on **what raises / is refused, or on the shape of a signature or result**, the
Contract wins, and where the PRD also says "refused", the refusal is kept.

## Conflicts and choices

Each entry gives both sides, then what was built. `CONFLICTS.md` lists these ids.

### C-01 Porter default lowercasing
- PRD FP-02 "Porter, default mode" (line 155): "The word is lowercased first, unless the caller turns lowercasing off."
- Contract "Stemmers" (line 99): "`to_lowercase` defaults to `False`, so `stem` keeps the letter case it is given."
- **Built:** `PorterStemmer().stem(word, to_lowercase=True)`, the PRD default. `stem("Running")` gives `run`.

### C-02 Porter Step 1a on "ties"
- PRD FP-02 (line 158): a four-letter word ending in *-ies* becomes *-ie* in default mode.
- Contract "Stemmers" (line 99): "`PorterStemmer` applies Step 1a as published, so *ties* stems to *ti*."
- **Built:** default (LINGORA) mode gives `ties` → `tie`. The `original` mode gives `ti`.

### C-03 Chunk rule on touching matches
- PRD FP-04 "Chunk rule" (line 222): "Two matches that touch are two separate chunks." and, in the same bullet, "Chunks that touch, with no token between them, are joined into one chunk."
- **Built:** chunks of the same clause and label that touch are joined, so `NP: {<DT>}` on `the the` gives one NP. The later sentence was taken as the rule that applies to the result.

### C-04 Tree built from a string child list
- PRD FP-05 "Trees" (line 255): "A string given in place of the child list is taken as a single leaf."
- PRD FP-05 boundary (line 263) and Contract "Trees" (line 195): a `str` given as children makes `Tree` raise.
- **Built:** `Tree(label, "x")` raises `TypeError`; `Tree(label)` raises `TypeError`. `Tree(label, [])` is valid.

### C-05 / C-06 Chart parser and an uncovered token
- PRD FP-05 "Chart parser" (line 251): "none" for a token list the grammar does not derive, "including one holding a token that no production produces".
- PRD boundary (line 264) and Contract "Grammars and parsers" (line 174-175): a token no production produces makes `parse` raise; "A token list the grammar does not derive gives an empty iterator."
- **Built:** a token no production produces raises `ValueError` (checked when `parse` is called). A covered token list the grammar does not derive gives an empty iterator.

### C-07 Empty terminal in the generator
- PRD FP-05 "Generator" (line 253): "A quoted empty string contributes an empty-string token."
- Contract "Grammars and parsers" (line 180): "A terminal that is the empty string adds no token to a sentence."
- **Built:** `generate` follows the PRD: `S -> ''` yields `['']`. An empty production contributes no token. In parsing, a quoted empty terminal consumes no token and adds no leaf, because leaves must be the input tokens.

### C-08 Accuracy on lists of different lengths
- PRD FP-07 "Accuracy" (line 306): a fraction over the common positions.
- PRD boundary (line 319) and Contract "Metrics" (line 231): the call does not succeed / raises.
- **Built:** `metrics.accuracy` raises `ValueError`. Empty lists also raise, because the fraction is undefined.

### C-09 Precision and recall on lists
- PRD FP-07 (line 308): a list or tuple is read as the set of its elements.
- PRD boundary (line 320) and Contract "Metrics" (line 238): lists are refused; a non-set makes the call raise.
- **Built:** `precision`, `recall` and `f_measure` raise `TypeError` for non-set arguments.

### C-10 F-measure when there is no shared element
- PRD FP-07 (line 309): 0 when precision or recall is 0.
- PRD boundary (line 320): f-measure with no shared element returns no number.
- **Built:** the boundary rule is the more specific one, so `f_measure` returns `None` when the sets share no element, and `0.0` only when they share elements but precision or recall is 0 (which cannot happen with a shared element, so in practice it is `None`).

### C-11 Edit distance with transpositions
- PRD FP-07 (line 303): the unrestricted Damerau–Levenshtein distance, where characters may be inserted between the transposed pair.
- Contract "Metrics" (line 235): only adjacent characters may be transposed, with nothing inserted or deleted between.
- **Built:** the PRD version, since the Contract defers computation to the PRD. `edit_distance("ca", "abc", transpositions=True)` is 2; the restricted version would give 3.

### C-12 BLEU default weights
- PRD FP-07 (line 312): equal weights on unigrams through 4-grams.
- Contract "Metrics" (line 242): when `weights` is omitted, unigrams and bigrams are weighted and longer n-grams are not scored.
- **Built:** the PRD default, `(0.25, 0.25, 0.25, 0.25)`.

### C-13 Regular-expression tokenizer, empty pieces
- PRD FP-01 (line 120): empty pieces are dropped unless the caller turns this off; it is on by default.
- Contract "Tokenizers" (line 66): `discard_empty` is off unless the caller passes `discard_empty=True`.
- **Built:** the PRD default (`discard_empty=True`).

### C-14 Tweet tokenizer case default
- PRD non-functional "Unicode" (line 65): the tweet tokenizer lowercases "unless the caller asks to preserve case".
- PRD FP-01 "Tweet tokenizer" (line 127): case preservation is on by default.
- **Built:** `preserve_case=True` by default, since the feature-level statement is the more specific one. `TweetTokenizer().tokenize("ÉCOLE")` keeps `ÉCOLE`.

### C-15 Type of a nonterminal symbol
- Contract "Grammars" (line 169): a nonterminal is a `str` or an object whose `str()` is the name.
- Contract (line 170): in `rhs()`, a nonterminal is a symbol that is not a `str`.
- **Built:** `Nonterminal` objects, which are never `str`, so both lines hold. `str(symbol)` is the name.

## Choices not fixed by the spec

- **Chunk root label** is `S`. A chunk grammar that uses the clause label `S` will therefore share its label with the root.
- **Chunk cascading.** A later clause may match an earlier clause's chunk as one unit (tag = its label). The earlier chunk's tokens are then carried into the new chunk as `(token, tag)` children, as the Contract describes chunk children. The earlier chunk's label is therefore not kept inside the new chunk.
- **Chink** removes matched tokens only from chunks built by the same clause, per the PRD.
- **Shift-reduce** never reduces an empty production (it would match forever). The first matching production in written order is used.
- **Chart parser** cuts cyclic derivations over the same span, so a unit-production cycle does not loop.
- **Packaged data directories.** `data.path` starts with the entries of `$LINGORA_DATA` (os.pathsep separated) and `~/lingora_data`. An empty list hides all packaged data.
- **Punkt.** Decisions follow Kiss and Strunk's rules: abbreviations, initials, numbers and ellipses are resolved by collocations, sentence starters and orthographic context; other period-final tokens end a sentence. This is a reimplementation of the decision rules, not a byte-for-byte port of any other library.
- **Averaged perceptron tagger** uses the feature templates and normalisation of the textblob-aptagger design. Output depends entirely on the packaged model files.
- **Russian universal mapping** uses my own table in `lingora/tag.py` (`_RUS_TO_UNIVERSAL`).
- **Extra taggers.** Bigram, trigram and affix taggers exist. They are outside the spec and only lightly checked.
- **CLI.** A tiny group object provides `cli.main(args=..., standalone_mode=...)`, since no CLI library is installed. Options: `--language` (default `english`), `--delimiter` (default one space), `--encoding` (accepted, not used; input is read as text).

## Known gaps

- **Snowball.** Only `english` (Porter2) and `porter` (original Porter) are implemented. The other listed languages pass name validation, but constructing them raises `NotImplementedError`. Stopword skipping works for any language whose list is installed.
- **Lancaster.** The rule table was reconstructed from memory and is incomplete. It stems `maximum` to `maxim`, `running` to `run` and `provision` to `provid`, but `presumably` is not stemmed to `presum`. It should be checked against the published table before relying on its output.
- **Porter `martin` mode** currently behaves the same as `original`.
- **ARLSTem, ARLSTem2** raise `NotImplementedError` on construction.
- **WordNetLemmatizer** raises `LookupError` when WordNet is not visible, and `NotImplementedError` otherwise.
- **ne_chunk** raises `LookupError` when its model or wordlist is not visible, and `NotImplementedError` otherwise.
- **Recursive-descent parser** is not provided. The spec lists it as outside its results.
- **Tests.** `tests/test_lingora.py` checks behaviour against small packaged-data fixtures built in a temporary directory. The real Punkt, perceptron and WordNet models were not available in this environment, so those paths were exercised only with the fixtures.
