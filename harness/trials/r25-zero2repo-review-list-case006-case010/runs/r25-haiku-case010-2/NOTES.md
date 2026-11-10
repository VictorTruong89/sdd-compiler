# LINGORA build notes

Scope: the library in `lingora/` (flat layout, pure Python 3.10+), built from
`spec/Full_PRD.md`, `spec/Interface_Contract.md` and `spec/Hardware_Requirements.md`.
`spec/` is unchanged. Packaged models (Punkt, the perceptron tagger, WordNet,
stopwords, the NE chunker) are not in the repository; they are found through
`lingora.data.path`, which starts empty unless `LINGORA_DATA` is set.

Where the specification disagrees with itself, the rule used is: where a
conflict is about a call's **signature default, error behaviour or return
shape**, the Interface Contract decides; where it is about **algorithm
internals** the Contract does not describe, the PRD decides. Each item below
names both sides, the location, and the choice.

## Spec conflicts and resolutions

Line numbers refer to the files named in each entry.

### C-01 Porter default lowercasing
- PRD, FP-02 "Porter, default mode" (`Full_PRD.md:155`): "The word is lowercased first, unless the caller turns lowercasing off."
- Contract, "Stemmers" (`Interface_Contract.md:99`): "`to_lowercase` defaults to `False`, so `stem` keeps the letter case it is given."
- **Built:** the Contract's signature default. `PorterStemmer().stem(word)` keeps case; `to_lowercase=True` lowercases. The stem is computed on the lowercased word, and the original case is restored on letters the stem still shares with the input (`Running` → `Run`).

### C-02 Porter Step 1a on "ties"
- PRD, FP-02 (`Full_PRD.md:158`): in default mode, "a four-letter word ending in -ies becomes -ie rather than -i" (so `ties` → `tie`).
- Contract (`Interface_Contract.md:99`): "`PorterStemmer` applies Step 1a as published, so *ties* stems to *ti*."
- **Built:** the PRD's default mode (`ties` → `tie`). The Contract's sentence describes the published algorithm, and the PRD defines the default mode as the LINGORA extensions. `PorterStemmer(mode="original")` gives `ti`.

### C-03 Chunk rule on touching matches
- PRD, FP-04 (`Full_PRD.md:222`): "Two matches that touch are two separate chunks." and, in the same bullet, "Chunks that touch, with no token between them, are joined into one chunk."
- **Built:** the later sentence. Touching matches of one rule are merged into a single chunk (so `{<NN>}` over `NN NN` gives one chunk). A later clause may still absorb an earlier clause's chunk as a unit.

### C-04 Recursive tree built from a string child list
- PRD, FP-05 "Trees" (`Full_PRD.md:255`): "A string given in place of the child list is taken as a single leaf."
- PRD, FP-05 "Boundary" (`Full_PRD.md:263`) and Contract (`Interface_Contract.md:195`): a string as the child list is refused / "makes `Tree` raise."
- **Built:** refused (`TypeError`). `Tree("X", [])` is valid.

### C-05 Chart parser on a token no production produces
- PRD, FP-05 "Chart parser" (`Full_PRD.md:251`): returns none for a list the grammar does not derive, "including one holding a token that no production produces".
- PRD, FP-05 "Boundary" (`Full_PRD.md:264`) and Contract (`Interface_Contract.md:175`): such a token makes the parser raise.
- **Built:** raise (`ValueError`), at the call (`parse` validates eagerly). A covered token list the grammar does not derive gives an empty iterator.

### C-06 Contract's own statement on empty-result parsing
- Contract, "Grammars and parsers" (`Interface_Contract.md:174`): "A token list the grammar does not derive gives an empty iterator."
- Contract (`Interface_Contract.md:175`): "A token that no production produces makes `parse` raise."
- **Built:** the same resolution as C-05. A token no production produces raises; a token list made only of produced tokens that the grammar does not derive gives an empty iterator.

### C-07 Empty terminal in the generator
- PRD, FP-05 "Generator" (`Full_PRD.md:253`): "A quoted empty string contributes an empty-string token."
- Contract (`Interface_Contract.md:180`): "A terminal that is the empty string adds no token to a sentence."
- **Built:** the Contract (no token). An empty production also contributes no token.

### C-08 Accuracy on lists of different lengths
- PRD, FP-07 (`Full_PRD.md:306`): "For lists of different lengths, it is that fraction over the positions both lists have."
- PRD, FP-07 "Boundary" (`Full_PRD.md:319`) and Contract (`Interface_Contract.md:231`): lists of different lengths make it raise.
- **Built:** raise (`ValueError`). Empty lists also raise, since the fraction is undefined.

### C-09 Precision and recall on lists or tuples
- PRD, FP-07 (`Full_PRD.md:308`): "A list or tuple given as either argument is read as the set of its elements."
- PRD, FP-07 "Boundary" (`Full_PRD.md:320`) and Contract (`Interface_Contract.md:238`): non-set arguments are refused.
- **Built:** refused (`TypeError`) for anything that is not a `set` or `frozenset`.

### C-10 F-measure when precision or recall is 0
- PRD, FP-07 (`Full_PRD.md:309`): "It is 0 when precision or recall is 0."
- PRD, FP-07 "Boundary" (`Full_PRD.md:320`): f-measure "when either set is empty or when the two sets share no element return no number."
- **Built:** the second. Precision 0 means no shared element, so f-measure returns `None` (no number) in that case. The formula is used otherwise.

### C-11 Edit distance with transpositions
- PRD, FP-07 (`Full_PRD.md:303`): the unrestricted Damerau–Levenshtein distance, where characters may be inserted or deleted between the two transposed characters.
- Contract, "Metrics" (`Interface_Contract.md:235`): only characters adjacent in both strings may be transposed, with nothing inserted or deleted between them.
- **Built:** the Contract's restricted form (optimal string alignment). `edit_distance("ca", "abc", transpositions=True)` is 3, as it is without transpositions.

### C-12 BLEU default weights
- PRD, FP-07 "BLEU" (`Full_PRD.md:312`): "The default is equal weights on unigrams through 4-grams."
- Contract, "Metrics" (`Interface_Contract.md:242`): "When `weights` is omitted, unigrams and bigrams are weighted equally and longer n-grams are not scored."
- **Built:** the Contract's default, equal weights `(0.5, 0.5)` on unigrams and bigrams. Passing four equal weights gives the PRD's standard BLEU-4.

### C-13 Regular-expression tokenizer, empty-piece default
- PRD, FP-01 (`Full_PRD.md:120`): "Empty pieces are dropped unless the caller turns empty-discarding off (it is on by default)."
- Contract, "Tokenizers" (`Interface_Contract.md:66`): "`discard_empty` is off unless the caller passes `discard_empty=True`."
- **Built:** the Contract (off by default; `discard_empty=True` drops empty pieces).

### C-14 Tweet tokenizer lowercasing default
- PRD, Non-functional "Unicode" (`Full_PRD.md:65`): the tokenizer "lowercases its tokens unless the caller asks to preserve case."
- PRD, FP-01 "Tweet tokenizer" (`Full_PRD.md:127`): "With case preservation off (it is on by default), tokens are lowercased, except emoticons."
- **Built:** the FP-01 statement (`preserve_case=True` by default). The Contract does not state a default. Emoticons are never lowercased.

### C-15 Symbol type returned for a nonterminal
- Contract, "Grammars and parsers" (`Interface_Contract.md:169`): a nonterminal is "a `str`, or an object whose `str()` is the nonterminal's name", the choice being the implementer's.
- Contract (`Interface_Contract.md:170`): in `rhs()`, "a nonterminal appears as a symbol that is not a `str`."
- **Built:** a `Nonterminal` object whose `str()` is its name (not a `str`). Terminals in `rhs()` are plain `str`.

## Other choices the spec left open

- **Sentence boundaries (Punkt):** `lingora/_punkt.py` implements a simplified Kiss–Strunk decision over the four packaged parameter files (abbreviations, collocations, sentence starters, orthographic context). It is not bit-for-bit the NLTK Punkt implementation.
- **Recommended word tokenizer:** the Penn Treebank rules, with the FP-01 changes. A straight double quote at the very start of the text is a closing quote. The typographic quotes split off are `“ ” „ ‟ « » ‘ ‚ ‛ ‹ ›`; the right single quote `’` is left as an apostrophe.
- **Chunk grammar:** the root label is `S`. Clause labels that are also `S` would be ambiguous with it. A later clause's rules may match earlier chunks by their label.
- **Shift-reduce parser:** reduces the first matching production in grammar order, ignores empty productions, and returns at most one tree (no backtracking).
- **Generator:** depth bounds the number of nested nonterminal expansions. With no bound, left-recursive grammars raise `RecursionError`.
- **Decision tree:** information gain, ties broken by feature name order. A feature absent from a featureset is its own branch.
- **Naive Bayes:** add-one smoothing over each feature's observed values.
- **Averaged perceptron tagger:** reads the packaged weights, tagdict and classes as specified, and uses the feature templates and normalization of the published greedy tagger (as I know them). The tie-break for equal scores is the first class in the classes file. I could not check these details against the packaged model, because no packaged model is present in this environment.
- **Russian universal mapping:** a fixed table on the part before `=`; unknown categories map to `X`.
- **Command line:** `lingora tokenize [--language L] [--delimiter D] [--encoding E]`, also `python -m lingora tokenize`. It checks the Punkt model before reading input, so a missing model exits 1 with no output. It has no third-party dependencies (`click` is not installed here).
- **Packaging:** `pyproject.toml` (setuptools, flat layout). `pytest.ini` and `conftest.py` put the project root on `sys.path` for tests.

## Not built, or only partly built

- **Snowball:** `english` (Porter2) and `porter` (original Porter) are implemented. The other supported names (arabic, danish, dutch, finnish, french, german, hungarian, italian, norwegian, portuguese, romanian, russian, spanish, swedish) are accepted by the name check, but constructing them raises `NotImplementedError`. Unsupported names raise `ValueError` naming the language, as the spec requires.
- **ARLSTem, ARLSTem2:** importable and constructible; `stem` raises `NotImplementedError`. The spec puts their results outside scope.
- **Named-entity chunker (`ne_chunk`):** raises `LookupError` when the model or the wordlist is missing, as specified. When both are present it raises `NotImplementedError`, because the packaged model format is not implemented.
- **Lancaster:** implements the Paice/Husk algorithm with a rule table I reconstructed from memory of the published table. Spot checks (`maximum`→`maxim`, `nation`→`nat`, `presumably`→`presum`) agree with the reference outputs I know. The table has not been verified against the published one, and a few entries I was unsure of were written in their most likely form.
- **Porter:** the `original` mode is Porter's 1980 algorithm. The "Martin Porter extensions" mode named in the PRD is not implemented as a separate mode.
- **Bigram, trigram and affix taggers:** basic implementations; their behaviour is outside the spec.
- **Recursive-descent parser:** not implemented (the PRD says its results are outside the spec, and the Contract does not list it).
- **WordNet lemmatizer:** reads `index.<pos>` and `<pos>.exc`, and applies the standard morphological suffix rules. It is not checked against a real WordNet installation.
- **RSLP, ISRI, Cistem:** not implemented (not in the Contract's import list, and outside the specified results).

## Tests

`tests/test_lingora.py` (33 tests) runs against synthetic packaged models in a temporary data directory. All pass with `python3 -m pytest -q` from `/app`. The tests cover many of the chosen behaviours above (not every conflict; C-14, the tweet lowercasing default, is untested), plus the missing-model failures. They do not check the output of any packaged model, because none is present.
