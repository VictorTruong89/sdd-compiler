# LINGORA implementation notes

## Layout and how to run

- Package: `/app/lingora` (flat layout; `pyproject.toml` at the root for an editable install).
- No build step. `import lingora` works with `/app` on the path; nothing is downloaded on import.
- Packaged models are looked up in `lingora.data.path` (initially read from the `LINGORA_DATA`
  environment variable, `os.pathsep`-separated; empty when unset). Callers may change the list in place.
- Tests: `python -m pytest -q tests/` (fixture models are built in a temp directory).
- Pure standard library. No third-party dependency (`click`, `snowballstemmer` are not installed here,
  so the command line is a small built-in group and Snowball is implemented directly).

## Conflicts between the specification files

Rule used: where the PRD states behaviour and the Interface Contract states a name, type, signature or
default that disagrees, the **PRD governs the behaviour** and the **Contract governs names and types**
where the PRD is silent. Where two statements sit in the same file, the more specific one wins.

Quotations use the file names in `spec/`. "PRD" is `spec/Full_PRD.md`; "Contract" is `spec/Interface_Contract.md`.

### C-01 Porter default lowercasing
- PRD, FP-02 "Porter, default mode": "The word is lowercased first, unless the caller turns lowercasing off."
- Contract, "Stemmers": "`to_lowercase` defaults to `False`, so `stem` keeps the letter case it is given."
- **Built:** `PorterStemmer().stem(word)` lowercases by default (`to_lowercase=True`); the parameter still
  exists, so `to_lowercase=False` keeps case.

### C-02 Porter Step 1a on "ties"
- PRD, FP-02 "Porter, default mode": "In Step 1a, a four-letter word ending in *-ies* becomes *-ie* rather than *-i*."
- Contract, "Stemmers": "`PorterStemmer` applies Step 1a as published, so *ties* stems to *ti*."
- **Built:** the default mode gives `ties` → `tie` (PRD extension). Mode `'original'` (the published
  algorithm) gives `ti`, which is what the Contract's example describes.

### C-03 Touching chunks from one rule
- PRD, FP-04 "Chunk rule": "Two matches that touch are two separate chunks." and, in the same bullet,
  "Chunks that touch, with no token between them, are joined into one chunk."
- **Built:** each match is its own chunk, so touching matches of one rule stay separate. The
  joining sentence is not applied. The two sentences cannot both hold, and the first is the one that
  describes matches; it also matches the standard regular-expression chunking behaviour. A later clause
  that matches adjacent chunks can still group them as units.

### C-04 `Tree(label, "x")`
- PRD, FP-05 "Trees": "A string given in place of the child list is taken as a single leaf."
- PRD, FP-05 "Boundary": "Building a tree from a label and a **string** as the child list … is refused."
- Contract, "Trees": "A `str` given as `children` … makes `Tree` raise."
- **Built:** raises `TypeError`. The bracketed-text reader still produces leaves.

### C-05 Chart parser on a token no production produces
- PRD, FP-05 "Chart parser": a token list the grammar does not derive, "including one holding a token that
  no production produces", gives "none".
- PRD, FP-05 "Boundary": such a token "does **not** succeed", distinguishable from "a successful empty set of parses".
- Contract, "Grammars and parsers": "A token that no production produces makes `parse` raise."
- **Built:** raises `ValueError` (from the call, before any iteration).

### C-06 Contract's own empty-iterator and raise statements
- Contract, "Grammars and parsers": "A token list the grammar does not derive gives an empty iterator." and
  "A token that no production produces makes `parse` raise."
- **Built:** the same split as C-05. A token outside the grammar's terminals raises; a list of covered
  tokens that the grammar does not derive gives an empty iterator.

### C-07 Quoted empty string in the generator
- PRD, FP-05 "Generator": "A quoted empty string contributes an empty-string token."
- Contract, "Grammars and parsers": "A terminal that is the empty string adds no token to a sentence."
- **Built:** the PRD. `generate` yields `['']` for a `''` terminal. An empty production contributes nothing.
  The parsers treat `''` as matching zero tokens and add no leaf.

### C-08 Accuracy on lists of different lengths
- PRD, FP-07 "Accuracy": "For lists of different lengths, it is that fraction over the positions both lists have."
- PRD, FP-07 "Boundary": "Accuracy on two lists of different lengths does not succeed."
- Contract, "Metrics": "Lists of different lengths make it raise."
- **Built:** raises `ValueError`. Empty lists also raise, because the fraction is undefined.

### C-09 Precision and recall on lists or tuples
- PRD, FP-07 "Precision, recall and f-measure": "A list or tuple given as either argument is read as the set of its elements."
- PRD, FP-07 "Boundary": "Lists, tuples and other non-set collections are refused."
- Contract, "Metrics": "A non-set argument makes the call raise."
- **Built:** refused with `TypeError` (two sources say refuse, one says read as a set).

### C-10 F-measure when precision or recall is 0
- PRD, FP-07 "Precision, recall and f-measure": "It is 0 when precision or recall is 0."
- PRD, FP-07 "Boundary": "… f-measure when either set is empty or when the two sets share no element return no number."
- **Built:** for non-empty sets with no shared element, the result is `None` (the boundary rule, which
  is the more specific statement). The numeric 0 never occurs for non-empty sets.

### C-11 Edit distance with transpositions
- PRD, FP-07 "Edit distance": "the unrestricted Damerau–Levenshtein distance (Lowrance and Wagner, 1975) …
  characters may also be inserted between, or deleted from between, the two transposed characters."
- Contract, "Metrics": "With `transpositions=True`, only two characters that stand next to each other in both
  strings may be transposed, and nothing may be inserted or deleted between them."
- **Built:** the PRD's unrestricted Damerau–Levenshtein. `edit_distance("ca", "abc", transpositions=True)` is 2.

### C-12 BLEU default weights
- PRD, FP-07 "BLEU": "The default is equal weights on unigrams through 4-grams."
- Contract, "Metrics": "When `weights` is omitted, unigrams and bigrams are weighted equally and longer n-grams are not scored."
- **Built:** the PRD's default (1- to 4-grams, 0.25 each). Pass `weights=(0.5, 0.5)` for the Contract's behaviour.

### C-13 Regular-expression tokenizer, empty-piece default
- PRD, FP-01 "Regular-expression tokenizer": "Empty pieces are dropped unless the caller turns empty-discarding off (it is on by default)."
- Contract, "Tokenizers": "`discard_empty` is off unless the caller passes `discard_empty=True`."
- **Built:** the PRD. `discard_empty` defaults to `True`.

### C-14 Tweet tokenizer case default
- PRD, Non-functional "Unicode": the tweet-style tokenizer "lowercases its tokens unless the caller asks to preserve case."
- PRD, FP-01 "Tweet tokenizer": "With case preservation off (it is on by default), tokens are lowercased, except emoticons."
- **Built:** the FP-01 statement, which is the more specific one: `preserve_case=True` by default, so
  tokens keep their case unless the caller passes `preserve_case=False`.

### C-15 Symbol type returned for a nonterminal
- Contract, "Grammars and parsers": "A nonterminal is returned as a symbol: a `str`, or an object whose `str()` is the nonterminal's name. Which of the two is the implementer's choice." and, in `rhs()`, "A nonterminal appears as a symbol that is not a `str`."
- **Built:** a `Nonterminal` object that is not a `str` but compares equal to, and hashes like, its name. So
  `cfg.start() == "S"` holds, and `rhs()` never yields a `str` for a nonterminal.

## Limitations and deviations from the full specification

These are things the specification leaves open or places outside the feature points, and what I built
for them. Items marked **not implemented** raise rather than return a guess.

- **Punkt sentence splitting** uses the packaged parameters (abbreviations, collocations, sentence starters,
  orthographic context) with a rule-based decision: `?`/`!` always end a sentence; a period after a
  non-abbreviation ends one unless the pair is a collocation; after an abbreviation (or an ellipsis, or a
  single letter) it ends a sentence only when the next word is a sentence starter or is capitalised with
  orthographic evidence of sentence-initial capitalisation. It is not the full unsupervised log-likelihood
  Punkt training, because training is not part of the specified behaviour.
- **Snowball**: only `english` (Porter2) and `porter` (the original Porter algorithm, via the Porter engine
  in `original` mode) are implemented. The other 14 listed languages are **not implemented**: the
  constructor validates the name, loads the stopword list if requested, and then raises `NotImplementedError`.
  An unlisted name raises `ValueError` that contains the name.
- **Lancaster** follows the Paice/Husk algorithm with a rule table reconstructed from memory of the published
  list. A few rules may differ from the original table.
- **Porter** irregular-form table is a small built-in list (the specification leaves its entries open).
  Mode `'martin'` is an approximation (it adds the `bli`→`ble` and `logi`→`log` changes only).
- **Averaged perceptron tagger** (`pos_tag`) follows the greedy textblob/NLTK-style feature templates,
  word normalisation and start/end padding. It reads the weights, tag dictionary and classes files exactly as
  the specification's layout describes. The universal mapping of Russian tags is my own table.
  English tags are mapped with `en-ptb.map`; a tag missing from that table maps to `X`.
- **Named-entity chunker** (`ne_chunk`) checks its resources (model directory and English wordlist) and
  raises `LookupError` when either is absent. With both present it raises `NotImplementedError`, because
  its inference is outside the specification.
- **WordNet lemmatizer**, **ARLSTem**, **ARLSTem2**: their import and construction behave as the Contract says,
  but their results are **not implemented** (`NotImplementedError`). WordNet raises `LookupError` when absent.
- **Recursive-descent parser** and **ISRI/Cistem/RSLP** stemmers are outside the specified behaviour and are not included.
- **Shift-reduce parser** does not use empty productions (they would reduce forever), so an empty token list
  yields no parse. The chart parser memoises per span; a grammar with unit cycles (`A -> B`, `B -> A`)
  can give an incomplete result for the cyclic spans.
- **Decision tree** splits on the feature with the highest information gain, with ties broken by feature
  name. **Naive Bayes** uses add-one smoothing over the values of each feature seen in training.
- **Command line**: `lingora tokenize [--language LANG] [--delimiter TEXT]`, also `python -m lingora tokenize`.
  The Punkt model is checked before any input is read, so a missing model exits with status 1 and writes no token line.
- **Tokenizer spans**: `span_tokenize` is provided for the word/punctuation, whitespace and regular-expression
  tokenizers. The Penn Treebank tokenizers do not report spans.
