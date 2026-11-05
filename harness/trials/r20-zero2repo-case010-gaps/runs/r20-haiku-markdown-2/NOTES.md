# LINGORA build notes

Scope: the core processing path in `spec/Full_PRD.md` (FP-01 to FP-07), with the public
surface in `spec/Interface_Contract.md`. Pure Python 3.10+, no third-party dependencies
(`click` is not used; the CLI group is hand-written). Packaged models are read from
`lingora.data.path`; none ship in the tree, so every model-dependent path is verified
only against synthetic model files, not against the real Punkt, perceptron or universal
resources.

## Conflicts between spec documents, and what was built

1. **Penn Treebank comma and colon.** `spec/Full_PRD.md` FP-01 says the Penn Treebank tokenizer
   "follows the Penn Treebank tokenization conventions", but its explicit list of split
   characters is `;`, `@`, `#`, `$`, `%`, `&`, `?`, `!`, brackets, ellipsis and final points.
   Commas and colons are not in that list. Built: the explicit list wins, so `Hello, world`
   gives `Hello,` and `world`. Conventional PTB/NLTK tokenizers split commas and colons; if
   that is wanted, add `,` and `:` to `_PUNCT_RE` / a `([:,])(?!\d)` rule in
   `lingora/tokenize/treebank.py`.
2. **Tree leaves.** `spec/Interface_Contract.md` "Trees" says children are `str` leaves or
   trees; its "Chunking" section says a chunk's children are its `(token, tag)` pairs. Built:
   `Tree` accepts any leaf value. Chunk trees hold `(token, tag)` tuples; `fromstring` builds
   `str` leaves. `pformat` shows a tuple leaf as `token/tag`.

No other contradictions were found between the three documents.

## Assumptions for points the spec does not state

### Tokenization (`lingora/tokenize`)
- **Treebank clitics.** `can't` becomes `ca` + `n't` (NLTK style); `cannot` becomes `can` + `not`.
  `d'ye` becomes `d` + `'ye`. `'tis` and `'twas` become `'t` + `is` / `was`. `wanna` splits anywhere,
  not only before whitespace.
- **Typographic quotes** (recommended only): `“ ” „ ‘ ’ « »` are each their own token.
- **Dashes** U+2012 to U+2015 and `*` are split off in the recommended tokenizer only.
- **Punkt second pass.** The spec names the parameters but not the decision rules. Built, after
  Kiss and Strunk: `?` and `!` always end a sentence; a period after a non-abbreviation always
  ends one; for abbreviations and ellipses, a following lowercase word, a collocation pair, or a
  mid-sentence-only capitalised type blocks the break; sentence starters, upper-case-at-start
  evidence, paragraph starts and a missing next word force it. Single letters count as initials.
  A model directory that exists but lacks an individual file is treated as empty for that file.
- **Tweet tokenizer.** The emoticon, arrow, hashtag and word patterns are a simplified version
  of the usual rules. `@`-handles are stripped only when they are not preceded by a word character.
- **Blank-line tokenizer.** The separator is a newline, optional whitespace, a newline, plus the
  whitespace on either side. Segments keep internal single newlines.
- **Regular-expression tokenizer.** The `flags` argument is an extra, optional parameter.

### Stemming (`lingora/stem.py`)
- **Porter.** Default mode is the LINGORA extensions, including an irregular-forms table
  modelled on NLTK's (`sky`, `skis`, `dying`, `ugly`, ...). The table is not in the spec.
  `ORIGINAL_ALGORITHM` and `MARTIN_EXTENSIONS` modes exist and are approximate.
- **Lancaster.** The Paice/Husk rule table was reconstructed from memory, not copied from the
  published table. It reproduces the usual examples (`maximum`→`maxim`, `presumably`→`presum`,
  `owed`→`ow`, `saying`→`say`, `crying`→`cry`, `string`, `meant`, `cement`→`cem`, `running`→`run`).
  Other words may differ from the published stemmer. The acceptability rule used is: the stem left
  after removal has at least 2 letters and contains a vowel (`aeiouy`).
- **Snowball, implemented.** `english` (Porter2) and `porter` (the original Porter algorithm).
  **Not implemented:** the other 14 languages (`arabic`, `danish`, `dutch`, `finnish`, `french`,
  `german`, `hungarian`, `italian`, `norwegian`, `portuguese`, `romanian`, `russian`, `spanish`,
  `swedish`). Constructing one raises `NotImplementedError`, not a usable stemmer. The spec's
  Dutch note is therefore unmet.
- **Snowball stopwords.** Checked at construction (`LookupError` when the list is missing).
  Unsupported language names raise `ValueError`.
- **Regex stemmer.** Uses `re.sub` with the empty string, so every match is removed.
- **Not implemented, names only.** `ISRIStemmer`, `ARLSTem`, `ARLSTem2`, `Cistem`, `RSLPStemmer`
  and `WordNetLemmatizer` exist as names. Using them raises. `WordNetLemmatizer` raises
  `LookupError` when WordNet is not visible.

### Tagging (`lingora/tag.py`)
- Unigram ties go to the lexicographically smallest tag. A `RegexpTagger` pattern is matched
  with `re.match`, so it anchors at the first character.
- Backoff applies to the whole list and takes effect only for tokens the primary left untagged.
- Bigram, trigram and affix taggers are not implemented. The spec places their results out of scope.
- The perceptron follows the textblob-aptagger / NLTK-style feature set. The resource directory
  must hold the three JSON files; otherwise `LookupError`.
- **Universal mapping.** English uses `en-ptb.map`; unknown Penn tags map to `X`. Russian maps the
  part before `=` through a table I chose (`S`→`NOUN`, `V`→`VERB`, `A`→`ADJ`, `PR`→`ADP`, and so
  on); unknown parts map to `X`.
- `pos_tag(..., tagset='universal')` with `lang='eng'` raises `LookupError` when the universal
  table is missing (the spec allows either failing or returning unmapped tags).

### Chunking (`lingora/chunk.py`)
- Root label is `S`. Chunk labels are the clause labels.
- A chunk rule matches runs of tokens and of earlier-clause chunks. Earlier-clause chunks match by
  label, so cascading works. Chunks made by the same clause block chunk rules.
- A chink rule operates only on the children of this clause's chunks. Chunk interiors built by
  earlier clauses are never chinked.
- Zero-length matches are ignored. Tag elements accept `?`, `*`, `+`, `{m}`, `{m,n}`, `{m,}`,
  `{,n}`. `.` in an element matches any single character of a tag.
- `#` starts a comment outside angle brackets. `RegexpParser` accepts only a `str` grammar; a
  list of stages is not supported.
- `ne_chunk` raises `LookupError` when the model or wordlist is absent. When both are present it
  raises `NotImplementedError`, because the packaged model format is not implemented.

### Grammars and parsers (`lingora/grammar.py`, `lingora/parse`)
- Nonterminals are `Nonterminal` objects whose `str()` is the name. Terminals are `str`.
- The chart parser is exhaustive. Memoised over spans, with cycle cutting, so unit and epsilon
  cycles yield finite trees only. Tokens the grammar never produces raise `ValueError` at the
  call. A covered token list the grammar does not derive gives an empty iterator.
- The shift-reduce parser reduces with the first production in written order whose right-hand
  side matches the stack top. Empty productions never reduce, which avoids an infinite loop.
- **Generator.** Depth-first in written order, using NLTK's convention: each production expansion
  uses one level, and a terminal is yielded only at depth above 0. `depth=1` on `S -> "b"` gives
  nothing; `depth=2` gives `["b"]`. A left-recursive first production with no depth bound does not
  terminate (RecursionError), as with NLTK's generator. Pass `depth` for recursive grammars.
- Quoted empty string yields `""` as a token. Empty production yields nothing.

### Trees (`lingora/tree.py`)
- `pformat(margin=70)` prints one line if it fits, otherwise an indented layout. The layout is
  my choice.
- `Tree` equality compares labels and children. `Tree(label)` and string children raise `TypeError`.

### Classification (`lingora/classify.py`)
- **Naive Bayes.** Smoothing is ELE-style (`+0.5`) for priors and for per-label value
  frequencies, with `|V|+1` bins. A feature value never seen in training is ignored at
  classify time. Labels are listed in first-seen order. Ties go to the earlier label. Training on
  an empty list raises `ValueError`.
- **Decision tree.** ID3: information gain, multiway split on each value, with `None` as the
  branch for an absent feature. An unseen value falls back to the node's majority label. No
  pruning. A leaf is the majority label, with ties to the first-seen label.
- **Accuracy (classifier).** An empty gold list raises `ValueError`, since the fraction is undefined.

### Metrics (`lingora/metrics.py`, `lingora/translate.py`)
- `accuracy` on two empty lists raises `ValueError`.
- `jaccard_distance` of two empty sets is `0.0`.
- `f_measure` returns `None` when either set is empty, and `0.0` when precision or recall is 0.
- `edit_distance` with transpositions is the unrestricted Damerau-Levenshtein distance
  (Lowrance and Wagner). A transposition costs 1. `substitution_cost` must be a number, not a bool.
- `bleu(references, hypothesis, weights=..., smoothing_function=None)`. Weights are used as given
  (not normalised). Zero-weight orders are skipped. An empty hypothesis scores 0. Unsmoothed, any
  weighted order with zero precision gives 0. `smoothing_function` is a callable taking the list of
  `(numerator, denominator)` pairs per order and returning smoothed precisions.
  `SmoothingFunction` provides `method0`, `method1` (epsilon 0.1) and `method2` (add one).

### Command line (`lingora/cli.py`, `lingora/__main__.py`)
- `cli.main(args=['tokenize'], standalone_mode=True)` reads all of stdin, then writes one line per
  input line. Options: `--language` (default `english`), `--delimiter` (default one space).
- Exit status: 0 on success, 1 when a line fails (for example, the Punkt model is missing; nothing
  is written for that line), 2 on a usage error. With `standalone_mode=False` the status is returned.
- An empty input line produces an empty output line. The command reads all of stdin before writing;
  it is not streaming.
- `python -m lingora tokenize` is equivalent.

### Data finder (`lingora/data.py`)
- `data.path` starts with the directories in `LINGORA_DATA` (os.pathsep separated), then
  `~/lingora_data`, `~/.lingora/data`, `/usr/local/share/lingora` and `/usr/share/lingora`.
  The list is re-read on every lookup, so in-place edits take effect immediately.
- `find(resource)` returns the first match and raises `LookupError` otherwise.

## Packaging
- `pyproject.toml` declares a flat layout (`lingora`, `lingora.tokenize`, `lingora.parse`). Nothing
  is built or installed by the judge; the package imports from `/app` directly.

## Verification done
- Synthetic model files (a tiny Punkt model, perceptron weights, universal map, stopwords) were
  placed under `/tmp` and used by ad-hoc pytest checks. Those checks are not in the repo.
- Checks passed: tokenizers (Treebank, recommended, tweet, regex, blank-line, span), Punkt on
  synthetic parameters, pos_tag English and universal, unigram, regexp and backoff taggers,
  chunk / chink / cascade, tree construction and comparison, CFG reading, chart and shift-reduce
  parsing, generator depth and count, Naive Bayes, decision tree, metrics, BLEU, Porter / Porter2 /
  Lancaster examples, and the CLI (success, missing model, delimiter).
- Not verified: real Punkt or averaged-perceptron resources, the universal tagset tables, and the
  output of the Lancaster table against the published rules.
