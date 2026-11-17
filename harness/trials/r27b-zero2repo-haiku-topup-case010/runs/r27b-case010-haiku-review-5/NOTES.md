# LINGORA build notes

This file records where the specification disagrees with itself, which side I
built, and what is not implemented. Line numbers refer to the files in `spec/`.
Rule used throughout: where the Interface Contract defers to the PRD for a
default's behaviour (Contract, "Parameters": "The PRD states the default's
behaviour wherever it matters"), the PRD wins. Otherwise the more specific
statement wins.

## Conflicts

### C-01 Porter default lowercasing
- PRD, FP-02 "Porter, default mode" (line 155): "The word is lowercased first, unless the caller turns lowercasing off."
- Contract, "Stemmers" (line 99): "`to_lowercase` defaults to `False`, so `stem` keeps the letter case it is given."
- **Built:** `PorterStemmer().stem(word, to_lowercase=True)`. The PRD's default behaviour is used, so the default lowercases. Passing `to_lowercase=False` keeps case.

### C-02 Porter Step 1a on "ties"
- PRD, FP-02 (line 158): "In Step 1a, a four-letter word ending in *-ies* becomes *-ie* rather than *-i*." Default mode is the LINGORA extensions (line 148).
- Contract, "Stemmers" (line 99): "`PorterStemmer` applies Step 1a as published, so *ties* stems to *ti*."
- **Built:** default mode gives `ties` → `tie` (PRD extension). The published rule (`ties` → `ti`) is used only in `PorterStemmer(mode="original")`.

### C-03 Chunk rule on touching matches
- PRD, FP-04 "Chunk rule" (line 222): "Two matches that touch are two separate chunks." and later in the same bullet: "Chunks that touch, with no token between them, are joined into one chunk."
- **Built:** the second sentence wins. Adjacent matches of one chunk rule are merged into one chunk, so `NP: {<NN>}` over `dog dog` gives one `NP` with two tokens. The first sentence is not implemented. Chunks from different rules are not merged.

### C-04 Tree built from a string child list
- PRD, FP-05 "Trees" (line 255): "A string given in place of the child list is taken as a single leaf."
- PRD, FP-05 "Boundary" (line 263) and Contract, "Trees" (line 195): refused / "makes `Tree` raise."
- **Built:** `Tree(label, "x")` raises `TypeError`, and so does `Tree(label)`. A string *inside* a children list is a leaf, as usual.

### C-05 / C-06 Chart parser on a token no production produces
- PRD, FP-05 "Chart parser" (line 251): "none for a token list the grammar does not derive (including one holding a token that no production produces)."
- PRD, FP-05 "Boundary" (line 264): such a token "does **not** succeed", distinguishable from "a successful empty set of parses".
- Contract, "Grammars and parsers" (line 174): "A token list the grammar does not derive gives an empty iterator." and (line 175): "A token that no production produces makes `parse` raise."
- **Built:** `parse` raises `ValueError` eagerly, at the call. A token list the grammar does derive not-at-all (all tokens known) gives an empty iterator.

### C-07 Empty terminal in the generator
- PRD, FP-05 "Generator" (line 253): "A quoted empty string contributes an empty-string token. An empty production contributes no token."
- Contract, "Grammars and parsers" (line 180): "A terminal that is the empty string adds no token to a sentence."
- **Built:** the PRD. `S -> ""` generates `[""]`. An empty production adds nothing.

### C-08 Accuracy on lists of different lengths
- PRD, FP-07 "Accuracy" (line 306): "For lists of different lengths, it is that fraction over the positions both lists have."
- PRD, FP-07 "Boundary" (line 319) and Contract, "Metrics" (line 231): does not succeed / "Lists of different lengths make it raise."
- **Built:** `lingora.metrics.accuracy` raises `ValueError`. Empty lists also raise, since the fraction is undefined. (`classify.accuracy` is a different function.)

### C-09 Precision and recall on lists or tuples
- PRD, FP-07 (line 308): "A list or tuple given as either argument is read as the set of its elements."
- PRD, FP-07 "Boundary" (line 320) and Contract, "Metrics" (line 238): refused / "A non-set argument makes the call raise."
- **Built:** `precision`, `recall`, `f_measure` raise `TypeError` for anything that is not a `set` or `frozenset`.

### C-10 F-measure when precision or recall is 0
- PRD, FP-07 (line 309): "It is 0 when precision or recall is 0."
- PRD, FP-07 "Boundary" (line 320): f-measure returns no number "when the two sets share no element".
- **Built:** `f_measure` returns `None` for disjoint sets and for empty sets. Precision and recall on non-empty but disjoint sets return `0.0`. Precision on an empty test set and recall on an empty reference set return `None`.

### C-11 Edit distance with transpositions
- PRD, FP-07 (line 303): "the unrestricted Damerau–Levenshtein distance … characters may also be inserted between, or deleted from between, the two transposed characters."
- Contract, "Metrics" (line 235): "only two characters that stand next to each other in both strings may be transposed, and nothing may be inserted or deleted between them."
- **Built:** the PRD's unrestricted Lowrance–Wagner distance. `edit_distance("ca", "abc", transpositions=True) == 2`. The restricted variant is not built.

### C-12 BLEU default weights
- PRD, FP-07 (line 312): "The default is equal weights on unigrams through 4-grams."
- Contract, "Metrics" (line 242): "When `weights` is omitted, unigrams and bigrams are weighted equally and longer n-grams are not scored."
- **Built:** the PRD. Default weights are 0.25 for each of unigrams through 4-grams.

### C-13 Regular-expression tokenizer, empty-piece default
- PRD, FP-01 (line 120): "Empty pieces are dropped unless the caller turns empty-discarding off (it is on by default)."
- Contract, "Tokenizers" (line 66): "`discard_empty` is off unless the caller passes `discard_empty=True`."
- **Built:** the PRD. `RegexpTokenizer(pattern)` drops empty pieces by default.

### C-14 Tweet tokenizer case default
- PRD, Non-functional "Unicode" (line 65): the tweet-style tokenizer "lowercases its tokens unless the caller asks to preserve case."
- PRD, FP-01 "Tweet tokenizer" (line 127): "With case preservation off (it is on by default), tokens are lowercased, except emoticons."
- **Built:** FP-01 (the more specific statement). `TweetTokenizer()` preserves case by default. `preserve_case=False` lowercases everything except emoticons.

### C-15 Symbol type returned for a nonterminal
- Contract, "Grammars and parsers" (line 169): "A nonterminal is returned as a symbol: a `str`, or an object whose `str()` is the nonterminal's name. Which of the two is the implementer's choice."
- Contract (line 170): "A nonterminal appears as a symbol that is not a `str`."
- **Built:** a `Nonterminal` object (not a `str` subclass) whose `str()` is its name. `rhs()` therefore never gives a `str` for a nonterminal.

## Choices where the spec is silent or only implicit

- **Treebank "can't":** split as `ca` + `n't`, following the Penn Treebank convention the spec says it follows. The spec's wording ("split from the word they follow") read literally would give `can` + `n't`.
- **Treebank "cannot":** the Treebank tokenizer splits it to `can not`. The recommended tokenizer keeps `cannot` as one token (per FP-01).
- **Recommended tokenizer and single quotes:** typographic single quotation marks (‘ ’ ‚ ‛) are split off as tokens too, as the spec says for "typographic quotation marks". This also splits the apostrophe in `don’t`.
- **Punkt sentence splitter:** a simplified implementation of the Kiss & Strunk heuristics, driven by the four packaged Punkt files. Rules: `?`/`!` always end a sentence; a lower-case next word does not end one; an abbreviation or initial ends one only when the next word is a sentence starter or has upper-case sentence-start evidence in `ortho_context`; collocations never break. This is not the full NLTK/Punkt algorithm.
- **Averaged perceptron tagger:** the feature templates, normalisation and decoding follow textblob-aptagger as described in FP-03. The resource file layout is taken from the Contract. Only the fake resources in `tests/` were exercised, because no packaged models are installed here.
- **Universal mapping:** English uses the packaged `en-ptb.map`. Russian uses a built-in RNC-part-of-speech → universal table, as FP-03 permits. Mapping English without `en-ptb.map` raises `LookupError`.
- **Unigram ties:** the tag seen first in training wins.
- **Chunk parser:** a later clause can match earlier clause chunks as units (cascading). Chink rules touch only chunks built in their own clause. Chunk rules do not match inside chunks of the same clause.
- **Decision tree:** ID3 with information gain. A feature absent from a featureset is a separate `None` branch. A value without a branch falls back to the node's majority label.
- **Naive Bayes:** expected-likelihood smoothing with 0.5 per value and one extra bin for unseen values. Features whose name never occurred in training are ignored.
- **Parse trees:** `ChartParser` memoises per (symbol, span). A cycle through the same (symbol, span) is cut, so grammars with unit or epsilon cycles yield only their finite trees.
- **ShiftReduceParser:** one left-to-right pass. Reduce is attempted before every shift, and the first matching production (in written order) is used. There is no backtracking.
- **CLI:** `cli` is a small built-in group (click is not installed here, and the spec does not require it). Exit status is 0 on success, 1 when the Punkt model is missing or a line fails, 2 for usage errors. Missing Punkt is detected before any output is written. `-l/--language` and `-d/--delimiter` are supported.
- **`data.path`:** initially holds the directories in the `LINGORA_DATA` environment variable (os.pathsep separated), followed by `~/lingora_data`.

## Not implemented (spec says they exist; this build does not provide them)

- **Snowball:** only `english` (Porter2) and `porter` (original Porter) are implemented. The other 14 language names are accepted by the constructor and then raise `NotImplementedError`. `ignore_stopwords` is checked against the packaged list. Snowball's own published algorithms for those languages were not reproduced.
- **Lancaster:** the Paice/Husk engine is implemented, but the rule table is a small partial reconstruction, not the standard published table. The output is therefore not expected to match Lancaster's published results (for example `maximum` is not reduced to `maxim`). Treat Lancaster as incomplete.
- **ARLSTem, ARLSTem2, WordNetLemmatizer:** exist as names. `ARLSTem`/`ARLSTem2` raise `NotImplementedError`. `WordNetLemmatizer` raises `LookupError` when WordNet is not visible and `NotImplementedError` otherwise.
- **Named-entity chunker (`ne_chunk`):** checks the model and wordlist, raising `LookupError` when either is absent, and raises `NotImplementedError` when both are present.
- **Packaged data:** no corpora, Punkt models or perceptron models are installed, so the resource-dependent paths were tested only against fake files in a temporary directory.

## Tests

`tests/test_lingora.py` contains 30 behavioural tests. Run them from `/app` with `python3 -m pytest`. The packaged-resource tests create fake Punkt and tagger files in a temporary directory.
