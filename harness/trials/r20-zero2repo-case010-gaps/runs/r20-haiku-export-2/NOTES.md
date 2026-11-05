# NOTES — LINGORA build

Built from `spec/` (compiled export, 29 packs, 477 checklist ids). `spec/` is untouched.
Code: `/app/lingora/` (flat package, stdlib only). Tests: `/app/tests/` (100 passing, `python3 -m pytest -q tests`).
Id-by-id status: `/app/COVERAGE.md`. Pack numbers below are the spec's `packs/NN-…` numbers.

## 1. Conflicts between parts of the specification

**C1 — Children and leaves of trees (chunk trees).**
- Pack 26 (FP-05, N-000256/N-000257): "a child is a token string (a leaf) or a tree".
- Pack 13 (Interface, `Tree`): `<tree>.leaves() -> list[str]`.
- Pack 11 (chunking): "Its children are … the input `(token, tag)` pairs that are in no chunk" and "A chunk's … children are its `(token, tag)` pairs".
- Pack 25 (FP-04): "The chunk structure's leaves, in order, are exactly the input tagged tokens".
- **Built:** `Tree` accepts any child value. Plain trees hold `str` leaves. Chunk trees hold `(token, tag)` tuples as leaves, so `leaves()` returns those tuples for chunk output. `leaves()` returns children unchanged; it does not convert them to `str`.

**C2 — Snowball `porter` language vs. the Porter stemmer modes.**
- Pack 09 lists `porter` among the Snowball languages. Pack 23 (FP-02) describes Porter as its own family with a LINGORA default mode.
- **Built:** `SnowballStemmer("porter")` applies the *original* published Porter rules (Snowball's `porter` is the original algorithm), not the LINGORA extensions.

**C3 — Penn Treebank comma and colon.**
- Pack 22 (FP-01) lists the characters that are split off as tokens of their own (`; @ # $ % & ? !`, brackets, ellipsis, final point, clitics). Commas and colons are not in that list.
- The spec says the tokenizer follows "the Penn Treebank tokenization conventions", which split commas and colons; the list above does not mention them, and no example in the spec settles it.
- **Built:** comma and colon are split off unless followed by a digit (so `1,000` stays whole). This is an assumption on my part; the spec does not state it.

**C4 — Stemmer families named in the PRD but not in the Interface.**
- Pack 23 (FP-02) says the built-in families are "exactly" Porter, Lancaster, Snowball, regular-expression, ISRI, ARLSTem, ARLSTem2, Cistem and RSLP, plus the WordNet lemmatizer.
- Pack 09 (Interface) lists `ARLSTem`, `ARLSTem2`, `LancasterStemmer`, `PorterStemmer`, `RegexpStemmer`, `SnowballStemmer`, `WordNetLemmatizer`. ISRI, Cistem and RSLP are not in the Interface at all.
- **Built:** the Interface names only. `ARLSTem` and `ARLSTem2` import, and `stem` raises `NotImplementedError` (their results are outside the spec). ISRI, Cistem and RSLP are not implemented.

**C5 — `recall` with an empty reference set.**
- Pack 28 (FP-07) says precision with an empty test set, and f-measure when either set is empty, return "no number". It does not say what `recall` does with an empty reference set.
- **Built:** `recall` returns `None` when the reference set is empty (no number), matching `precision`.

## 2. Gaps: things the spec does not state, and what I assumed

- **G1 — `data.path` initial contents** (Pack 06 says "implementer's choice"). Built: entries of the environment variable `LINGORA_DATA` (split on `os.pathsep`), then `~/.lingora`.
- **G2 — Packaged-model file handling.** A Punkt language directory is required; its four files are read as UTF-8, one entry per line. A missing individual file is treated as empty (not an error). Tagger files are JSON, named `averaged_perceptron_tagger_<lang>.{weights,tagdict,classes}.json`.
- **G3 — Punkt algorithm details.** The spec names Kiss and Strunk (2006) and the parameter files, but not the decision rules. I implemented the standard token-annotation, collocation, orthographic and sentence-starter heuristics from the paper, written from memory and not checked against a reference implementation. Sentence strings are stripped of trailing whitespace.
- **G4 — `word_tokenize(…, preserve_line=…)` default.** Not in the Interface; the PRD says sentence splitting happens unless the caller says the input is one line, so the default is `False`.
- **G5 — Span tokenizers.** `span_tokenize` is provided for `WordPunctTokenizer`, `WhitespaceTokenizer` and `RegexpTokenizer` only. Treebank and Tweet tokenizers have no span method.
- **G6 — Regular-expression tokenizer, token mode.** Empty matches are dropped under the default `discard_empty=True` (same switch as gap mode).
- **G7 — Tweet tokenizer patterns.** Emoticon, URL, hashtag and word patterns are my own; the spec gives only the behaviours.
- **G8 — Typographic quotes and dashes (recommended tokenizer).** Split set: `“”„‟‘’‚‛«»‹›`; dashes U+2012–U+2015; asterisks; runs of 2+ points; `--`. Penn-only tokenizer does not split `--` (per spec).
- **G9 — Penn "apostrophe" rules.** Clitics `'s 'm 'd 'll 're 've n't` split case-insensitively; `can't` → `ca n't`, `won't` → `wo n't` (regex consequence). A bare apostrophe that ends a word is split. Fused forms `cannot gimme gonna gotta lemme wanna more'n d'ye 'tis 'twas` split into `can not gim me gon na got ta lem me more 'n d' ye 't is 't was`.
- **G10 — Unigram tagger ties.** Broken by first-seen tag order in training.
- **G11 — Russian universal mapping.** Table is built in: `S→NOUN, A→ADJ, ANUM→ADJ, NUM→NUM, V→VERB, ADV→ADV, PRAEDIC→ADV, PARENTH→ADV, A-PRO/S-PRO/PRAEDIC-PRO→PRON, PR→ADP, CONJ→CONJ, PART→PRT, INTJ→X`; unknown → `X`. English universal: unmapped tags become `X`.
- **G12 — `pos_tag` failures.** Unknown `tagset` → `ValueError`; `universal` without the English table → `ResourceNotFound`.
- **G13 — Snowball languages other than `english` and `porter`.** Constructor accepts the 16 names from Pack 09; `stem` raises `NotImplementedError`. Not implemented in this release.
- **G14 — Porter modes.** `PorterStemmer(mode=…)` accepts `lingora` (default), `original`, `martin`. `martin` uses the original rules (the separate Martin extensions are not implemented). Irregular-forms table entries are the implementer's choice (a small Porter-style list).
- **G15 — Lancaster rule table.** The spec says "the standard rule table published with it", which is not in the spec. I reconstructed the Paice/Husk table from memory and it is **incomplete and may differ from the published table** (for example, `maximum` is not reduced to `maxim`). Treat Lancaster output as unverified.
- **G16 — WordNet lemmatizer.** Only exception-list lookup (`noun.exc`, `verb.exc`, `adj.exc`, `adv.exc`); no morphy rules. Results beyond exception lookup are outside the spec.
- **G17 — Named-entity chunker.** `ne_chunk` raises `ResourceNotFound` when the model or wordlist is not visible. When visible it raises `NotImplementedError`: the model file format is not stated and is not implemented.
- **G18 — Chunk grammar details.**
  - Pattern lines must be indented; a clause line is `<LABEL>: <pattern>`; lines starting with `#` are comments (not stated in the spec).
  - Cascading: a later clause's rule matches earlier-clause chunks as single units (tag = chunk label); chunks from the same clause are not matchable by that clause's own rules.
  - Chink rules act only on leaves inside chunks of the same clause.
  - Matches are the longest possible at each position; empty matches are not made.
  - `grammar` argument: only a `str` is accepted (pack 11 allows "a list of chunk-parser stages", implementer's choice; not implemented, see N-000414 in COVERAGE).
  - Root label: `S`.
- **G19 — Grammar text.** Quoted terminals are `'…'` or `"…"`. An unquoted symbol is a nonterminal. Unmatched quotes are dropped silently by the tokenizer of the RHS. Nonterminal objects are `Nonterminal` (not `str`), which the RHS requires.
- **G20 — Chart parser.** Exhaustive, memoised over spans. A derivation that cycles back on the same span (for example unit cycles) is omitted, since such derivations are infinitely ambiguous.
- **G21 — Shift-reduce parser.** Reduces whenever any production (in grammar order) matches the top of the stack, otherwise shifts. Empty productions are not used for reduction. Reductions between two shifts are capped at the number of productions, so a cycle of unit productions terminates (and then usually yields no tree).
- **G22 — Generator.** `depth`: a nonterminal is expanded only while the remaining depth is positive; terminals are always emitted. `n=0` yields nothing.
- **G23 — Decision tree.** Chooses at each node the feature whose single-level test (majority label per value; absent feature = its own value `None`) has the fewest training errors, and stops when that does not beat the node's majority leaf. Ties: first feature in order of first appearance. Unseen values fall back to the node's majority label.
- **G24 — Naive Bayes smoothing.** Expected-likelihood estimation with γ = 0.5, bins = number of distinct values of that feature across training. Features absent from training are ignored at classification time. Probabilities are normalised with log-sum-exp.
- **G25 — Metric edge cases not stated.**
  - `accuracy([], [])` raises `ValueError` (undefined).
  - `jaccard_distance` of two empty sets is `0.0`.
  - `f_measure(..., alpha=…)` takes an optional `alpha` (default 0.5).
  - `edit_distance` with `transpositions=True` is the unrestricted Damerau–Levenshtein distance; `ca`→`abc` = 2 (not OSA's 3).
- **G26 — BLEU.** Empty hypothesis → `0.0`; empty reference list → `ValueError`. Without smoothing: `0.0` when there is no unigram match or any weighted order has no match. The smoothing function is a callable taking `[(numerator, denominator), …]` and returning precisions; `SmoothingFunction().method1` replaces zero numerators with ε = 0.1 (keyword `smoothing_function`).
- **G27 — Tree printing.** `pformat()` puts a subtree on one line when it fits in 70 columns, otherwise one child per line, indented by two.
- **G28 — CLI.** Options `--language` (default `english`), `--delimiter` (default one space), `--encoding` (default `utf-8`). Exit status: `0` success; `1` a failure (for example a missing Punkt model, checked before any output is written); `2` a usage error. With `standalone_mode=False`, `main` returns the status instead of exiting. Input is read in full and split on newlines (a trailing `\r` is removed).
- **G29 — `Tree` constructor.** `label` is stored as `str(label)`. `children` must be a `list` (a `str`, or omitting it, raises `TypeError`).
- **G30 — Blank-line tokenizer.** Pieces that are empty or whitespace-only are dropped; other pieces are kept verbatim.

## 3. Things deliberately not done

- Packaged corpora, the data finder, the downloader, WordNet beyond exception lookup, graphical applications, chat/Twitter/HF helpers, external-binary wrappers, CCG/DRT/inference, N-gram models, sentiment lexicons — all outside the spec (Pack 21 and Pack 29 non-goals).
- Snowball stemming for 14 languages (see G13); ISRI, Cistem, RSLP; ARLSTem/ARLSTem2 results.
- Bigram, trigram and affix taggers (Pack 24 says they exist with the same protocol; results outside the spec).
- Recursive-descent parser (Pack 26: exists; results outside the spec).
- The optional extra groups (Pack 19, N-000050): no optional dependencies are provided.
- The s-expression tokenizer (Pack 22 / Pack 18, outside this specification).
- Named-entity chunking results (G17).

## 4. Running

```
python3 -m pytest -q tests      # 100 tests; they build their own Punkt/tagger/WordNet fixtures in tmp dirs
python3 -m lingora tokenize     # reads stdin, uses lingora.data.path (set LINGORA_DATA to a directory with tokenizers/punkt_tab/english)
```

The judge runs against `/app` as the working directory. `conftest.py` at the root keeps `import lingora` working from pytest.
