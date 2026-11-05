# Gap reading audit (round 20) — for the owner

One table per kept gap. **Lines** are every line of the run's `NOTES.md` that matches the gap's
keywords, cut at 300 characters, with their line numbers. **Reading** is the assistant's
(`detection.tsv`): flagged · built (probe) · note. **Flagged** needs the notes to name *this* point
as not stated in the specification, in words, and give the value assumed (TRIAL.md, "Strict
rule"). Fill **Owner** with `agree` or your reading. A line about something else that happens to
match the keywords is not a flag.

## G02 — Jaccard distance "is the size of the symmetric difference … divided by the size of their union" · upstream: identical sets 0, disjoint 1 · alternative: Jaccard similarity (identical 1)

| Run | Lines from NOTES.md | Reading | Owner |
|---|---|---|---|
| r20-haiku-markdown-1 | 27: \| Edit distance (with transpositions), Jaccard, accuracy, precision, recall, f-measure \| `lingora/metrics.py` \| Done \|<br>43: - **Jaccard distance of two empty sets** is `0.0`. | no · upstream · notes give jaccard of two empty sets only (not the definition) | |
| r20-haiku-markdown-2 | 123: - `jaccard_distance` of two empty sets is `0.0`. | no · upstream · notes give jaccard of two empty sets only (not the definition) | |
| r20-haiku-markdown-3 | 144: - **Jaccard distance.** Both sets empty gives `0.0`. Non-set arguments raise `TypeError`. | no · upstream · notes give jaccard of two empty sets only (not the definition) | |
| r20-sonnet-markdown-1 | 13: - `accuracy` (metrics and classify) on empty lists raises `ZeroDivisionError` (spec silent). `jaccard_distance` of two empty sets returns 0.0 (spec silent). | no · upstream · notes give jaccard of two empty sets only (not the definition) | |
| r20-sonnet-markdown-2 | 22: - `accuracy`/`jaccard_distance` on empty input raise `ZeroDivisionError` (undefined, not 0). | no · upstream · notes give jaccard of two empty sets only (not the definition) | |
| r20-sonnet-markdown-3 | 23: - `accuracy([], [])` raises `ZeroDivisionError`; `jaccard_distance(set(), set())` returns `0.0` (nothing stated). | no · upstream · notes give jaccard of two empty sets only (not the definition) | |
| r20-haiku-export-1 | 22: \| `lingora/metrics.py`, `lingora/translate.py` \| edit distance (incl. unrestricted Damerau–Levenshtein), Jaccard, accuracy, precision, recall, f-measure, BLEU \|<br>90: - **Jaccard of two empty sets**: 0.0 (spec silent). | no · upstream · notes give jaccard of two empty sets only (not the definition) | |
| r20-haiku-export-2 | 68: - `jaccard_distance` of two empty sets is `0.0`. | no · upstream · notes give jaccard of two empty sets only (not the definition) | |
| r20-haiku-export-3 | 29: \| `lingora/metrics.py`, `lingora/translate.py` \| FP-07 edit distance, Jaccard, accuracy, precision/recall/f, BLEU \|<br>130: - **Jaccard of two empty sets.** Returns `0.0` (the spec does not say). | no · upstream · notes give jaccard of two empty sets only (not the definition) | |
| r20-sonnet-export-1 | 20: - `accuracy` / `classify.accuracy` of empty lists: return 0.0. `jaccard_distance` of two empty | no · upstream · notes give jaccard of two empty sets only (not the definition) | |
| r20-sonnet-export-2 | 29: `jaccard_distance(set(), set())` returns `0.0`. | no · upstream · notes give jaccard of two empty sets only (not the definition) | |
| r20-sonnet-export-3 | *(none)* | no · upstream ·  | |

## G03 — "recall with an empty reference set" returns no number · upstream: `None` · alternative: 0

| Run | Lines from NOTES.md | Reading | Owner |
|---|---|---|---|
| r20-haiku-markdown-1 | 27: \| Edit distance (with transpositions), Jaccard, accuracy, precision, recall, f-measure \| `lingora/metrics.py` \| Done \|<br>44: - **Precision/recall of an empty set** returns `None` (per the spec); f-measure returns `None` when either set is empty and `0.0` when precision or recall is 0. | no · upstream ·  | |
| r20-haiku-markdown-2 | 124: - `f_measure` returns `None` when either set is empty, and `0.0` when precision or recall is 0. | no · upstream ·  | |
| r20-haiku-markdown-3 | 49: 4. **Recall with an empty reference set.** `spec/Full_PRD.md:310` says nothing about<br>50: recall. Precision with an empty test set and f-measure with an empty set return<br>51: "no number" (`None`). **Built:** recall with an empty reference returns `None`, so<br>112: textblob-aptagger / NLTK `PerceptronTagger` design as I recall it. This is<br>145: - **Metrics refusals.** Non-set arguments to precision, recall and f-measure raise | yes · upstream · NOTES.md:49-52: 'says nothing about recall… Built: recall with an empty reference returns None' | |
| r20-sonnet-markdown-1 | *(none)* | no · upstream ·  | |
| r20-sonnet-markdown-2 | *(none)* | no · upstream ·  | |
| r20-sonnet-markdown-3 | *(none)* | no · upstream ·  | |
| r20-haiku-export-1 | 22: \| `lingora/metrics.py`, `lingora/translate.py` \| edit distance (incl. unrestricted Damerau–Levenshtein), Jaccard, accuracy, precision, recall, f-measure, BLEU \|<br>91: - **Recall with an empty reference**: `None`. Spec gives `None` for precision | yes · upstream · NOTES.md:91-92 under 'Gaps': 'Recall with an empty reference: None' | |
| r20-haiku-export-2 | 30: **C5 — `recall` with an empty reference set.**<br>31: - Pack 28 (FP-07) says precision with an empty test set, and f-measure when either set is empty, return "no number". It does not say what `recall` does with an empty reference set.<br>32: - **Built:** `recall` returns `None` when the reference set is empty (no number), matching `precision`.<br>71: - **G26 — BLEU.** Empty hypothesis → `0.0`; empty reference list → `ValueError`. Without smoothing: `0.0` when there is no unigram match or any weighted order has no match. The smoothing function is a callable taking `[(numerator, denominator), …]` and returning precisions; `SmoothingFunction().meth | yes · upstream · NOTES.md:30-32: 'It does not say what recall does with an empty reference set. Built: None' | |
| r20-haiku-export-3 | 29: \| `lingora/metrics.py`, `lingora/translate.py` \| FP-07 edit distance, Jaccard, accuracy, precision/recall/f, BLEU \| | no · upstream ·  | |
| r20-sonnet-export-1 | *(none)* | no · upstream ·  | |
| r20-sonnet-export-2 | *(none)* | no · upstream ·  | |
| r20-sonnet-export-3 | *(none)* | no · upstream ·  | |

## G07 — "Every stemmer treats its whole input string as one token"; `word` "is treated as one token" · upstream: a string with a space is stemmed as one token · alternative: each word stemmed, joined by a space

| Run | Lines from NOTES.md | Reading | Owner |
|---|---|---|---|
| r20-haiku-markdown-1 | 12: \| Word/punct, Treebank, recommended word, whitespace, blank-line, regexp, tweet tokenizers \| `lingora/tokenize.py` \| Done \|<br>33: 1. **Treebank comma and colon splitting.** PRD FP-01 says the Penn Treebank word tokenizer "follows the Penn Treebank tokenization conventions", but its explicit list of split punctuation (`; @ # $ % & ? !` and brackets) does not mention commas or colons. Penn Treebank splits them, so I follow the c<br>34: 2. **Ellipsis in the tweet tokenizer.** PRD FP-01 says "other punctuation marks are tokens of their own", but a run of two or more points is a token in the recommended tokenizer. For the tweet tokenizer I kept a run of two or more points (`...`) as one token; single punctuation marks are one token e<br>60: - **Punkt sentence splitting** is an approximation of Kiss and Strunk's algorithm using the packaged parameters: `?` and `!` always end a sentence; a period after a token that is a known abbreviation, a single letter (initial) or a number is not a break unless the next word is a known sentence start<br>64: - **Blank-line tokenizer.** A separator is `\s*\n\s*\n\s*`. Trailing spaces on the last segment are kept.<br>65: - **Command-line tokenize** loads the Punkt model before reading input; when it is missing the command prints an error to stderr, exits with status 1 and writes nothing to stdout. Options: `--language` (default `english`), `--delimiter` (default one space), `--encoding` (default UTF-8). Each input l | no · upstream ·  | |
| r20-haiku-markdown-2 | 31: not only before whitespace.<br>42: - **Blank-line tokenizer.** The separator is a newline, optional whitespace, a newline, plus the<br>43: whitespace on either side. Segments keep internal single newlines.<br>135: input line. Options: `--language` (default `english`), `--delimiter` (default one space). | no · upstream ·  | |
| r20-haiku-markdown-3 | 88: patterns are my choices. Runs of two or more dots are one token. Other punctuation<br>89: is one token per character. A handle is `@` not preceded by a word character plus<br>91: - **Blank-line tokenizer.** Pieces are not stripped of surrounding spaces. Only empty<br>119: - **Grammar text.** Unquoted symbols are runs of non-space characters other than quotes<br>140: shape. Options: `--language` (default `english`), `--delimiter` (default one space), | no · upstream ·  | |
| r20-sonnet-markdown-1 | *(none)* | no · upstream ·  | |
| r20-sonnet-markdown-2 | *(none)* | no · upstream ·  | |
| r20-sonnet-markdown-3 | *(none)* | no · upstream ·  | |
| r20-haiku-export-1 | 15: \| `lingora/tokenize.py`, `lingora/_punkt.py` \| word/punct, Treebank, recommended word tokenizer, whitespace, blank-line, regexp, tweet, spans; Punkt sentence splitter \|<br>114: words. Runs of the same punctuation character form one token. Length<br>135: (default `english`), `--delimiter/-d` (default one space). An empty input | no · upstream ·  | |
| r20-haiku-export-2 | 38: - **G3 — Punkt algorithm details.** The spec names Kiss and Strunk (2006) and the parameter files, but not the decision rules. I implemented the standard token-annotation, collocation, orthographic and sentence-starter heuristics from the paper, written from memory and not checked against a referenc<br>40: - **G5 — Span tokenizers.** `span_tokenize` is provided for `WordPunctTokenizer`, `WhitespaceTokenizer` and `RegexpTokenizer` only. Treebank and Tweet tokenizers have no span method.<br>44: - **G9 — Penn "apostrophe" rules.** Clitics `'s 'm 'd 'll 're 've n't` split case-insensitively; `can't` → `ca n't`, `won't` → `wo n't` (regex consequence). A bare apostrophe that ends a word is split. Fused forms `cannot gimme gonna gotta lemme wanna more'n d'ye 'tis 'twas` split into `can not gim <br>73: - **G28 — CLI.** Options `--language` (default `english`), `--delimiter` (default one space), `--encoding` (default `utf-8`). Exit status: `0` success; `1` a failure (for example a missing Punkt model, checked before any output is written); `2` a usage error. With `standalone_mode=False`, `main` ret<br>75: - **G30 — Blank-line tokenizer.** Pieces that are empty or whitespace-only are dropped; other pieces are kept verbatim. | no · upstream ·  | |
| r20-haiku-export-3 | 66: procedure. My rules (`lingora/_punkt.py`): tokens are whitespace runs; a token ends a sentence<br>74: inter-sentence whitespace removed. Not validated against real Punkt output.<br>76: split off as their own tokens. Typographic single quotes `‘ ’` are split only at word<br>142: input line. Options: `--language/-l` (default `english`), `--delimiter/-d` (default one space), | no · upstream ·  | |
| r20-sonnet-export-1 | *(none)* | no · upstream ·  | |
| r20-sonnet-export-2 | 31: honours `discard_empty`. `blankline_tokenize` of whitespace-only text returns `[]`.<br>41: - CLI options: `-l/--language` (default english), `-d/--delimiter` (default space), | no · upstream ·  | |
| r20-sonnet-export-3 | 45: - `blankline_tokenize` of a whitespace-only string returns `[]` (N-000129); other gap tokenizers keep PRD semantics<br>46: (a whitespace-only text with a custom gap pattern returns the piece).<br>53: - Pack 22 (FP-01) says the PTB tokenizer "splits at whitespace, then punctuation" and lists only some punctuation | no · upstream ·  | |

## G08 — Snowball, unsupported language: "The failure names the requested language"; message "contains the requested name" · upstream: message names the language · alternative: generic message

| Run | Lines from NOTES.md | Reading | Owner |
|---|---|---|---|
| r20-haiku-markdown-1 | *(none)* | no · upstream ·  | |
| r20-haiku-markdown-2 | 61: Unsupported language names raise `ValueError`. | no · upstream ·  | |
| r20-haiku-markdown-3 | 15: are implemented. Constructing the others raises `NotImplementedError`. Unsupported | no · upstream ·  | |
| r20-sonnet-markdown-1 | 24: - Snowball: English (Porter2), porter, German, Dutch, Spanish, French, Swedish, Norwegian, Danish and Russian are implemented from the published algorithm descriptions (compact versions, only spot-checked). **Arabic, Finnish, Hungarian, Italian, Portuguese and Romanian are accepted as language names | no · upstream ·  | |
| r20-sonnet-markdown-2 | *(none)* | no · upstream ·  | |
| r20-sonnet-markdown-3 | 18: Contract says the file name is the Snowball language name.<br>40: **French, Italian, Portuguese, Romanian, Finnish, Hungarian, Arabic** are accepted as language names but currently | no · upstream ·  | |
| r20-haiku-export-1 | 218: language names raise `NotImplementedError` at construction, and unknown names | no · upstream ·  | |
| r20-haiku-export-2 | *(none)* | no · upstream ·  | |
| r20-haiku-export-3 | 144: written for that line, a message goes to standard error, and the status is 1. Usage errors exit 2. | no · upstream ·  | |
| r20-sonnet-export-1 | *(none)* | no · upstream ·  | |
| r20-sonnet-export-2 | 25: `LookupError`; `SnowballStemmer(ignore_stopwords=True)` and unsupported languages raise `ValueError`. | no · upstream ·  | |
| r20-sonnet-export-3 | 56: - Pack 05 says exception classes/messages are free; I used `LookupError` (missing resource), `TypeError`<br>57: (wrong argument types), `ValueError` (bad values/coverage), `NotImplementedError` (unsupported pos_tag lang). | no · upstream ·  | |

## G09 — Snowball *porter* "is Snowball's rendering of the original Porter algorithm, so the two can give different stems" · upstream: *porter* = original Porter (generously → gener) · alternative: *porter* = alias of *english* (generous)

| Run | Lines from NOTES.md | Reading | Owner |
|---|---|---|---|
| r20-haiku-markdown-1 | 16: \| Snowball `english` (Porter2), `porter` \| `lingora/stem.py` \| Done \|<br>73: - Hand-checked outputs: tokenizers on sample sentences and clitics; Porter and Snowball English on a set of common words; Lancaster on known words (`maximum`→`maxim`, `presumably`→`presum`, `provision`→`provid`, `saying`→`say`); chunker cascade, chink and quantifiers; chart parser ambiguity (`S -> S | no · upstream ·  | |
| r20-haiku-markdown-2 | 55: - **Snowball, implemented.** `english` (Porter2) and `porter` (the original Porter algorithm). | yes · upstream · BORDERLINE: NOTES.md:55 under 'Assumptions for points the spec does not state': 'Snowball, implemented: english (Porter2) and porter (the original Porter algorithm)'; a status line, not said to be unstated | |
| r20-haiku-markdown-3 | 14: russian, spanish, swedish). Only `english` (Porter2) and `porter` (original Porter)<br>54: 5. **Snowball `porter`.** `spec/Full_PRD.md:144` lists `porter` as a Snowball language,<br>56: `SnowballStemmer('porter')` is the original 1980 Porter algorithm.<br>97: - **Porter2 (English Snowball).** Standard Snowball algorithm. R1 and R2 are computed | yes · upstream · NOTES.md:54-56 under '…ambiguities': Snowball porter listed separately; built: the original 1980 Porter | |
| r20-sonnet-markdown-1 | 24: - Snowball: English (Porter2), porter, German, Dutch, Spanish, French, Swedish, Norwegian, Danish and Russian are implemented from the published algorithm descriptions (compact versions, only spot-checked). **Arabic, Finnish, Hungarian, Italian, Portuguese and Romanian are accepted as language names | no · upstream ·  | |
| r20-sonnet-markdown-2 | 9: ARLSTem, ARLSTem2, Lancaster, Porter, Regexp, Snowball, WordNetLemmatizer. I built the Contract's list only.<br>36: - Snowball: full ports exist for english, porter, german, dutch, swedish, norwegian, danish, spanish, russian | no · upstream ·  | |
| r20-sonnet-markdown-3 | 16: - **Snowball `porter`**: PRD lists `porter` as a Snowball language without defining it; I used the original<br>39: - Snowball: English, Porter, German, Dutch (original), Swedish, Norwegian, Danish, Spanish, Russian are implemented. | yes · upstream · NOTES.md:16-17: 'lists porter as a Snowball language without defining it; I used the original (unextended) Porter' | |
| r20-haiku-export-1 | 16: \| `lingora/stem.py` \| Porter (3 modes), Lancaster (partial table), Snowball English (Porter2), Snowball `porter`, regexp stemmer, WordNet lemmatizer (resource gate), ARLSTem/ARLSTem2 (stubs) \|<br>141: - **Snowball English.** Standard Porter2 (Snowball's `english`). Exceptions | no · upstream ·  | |
| r20-haiku-export-2 | 16: **C2 — Snowball `porter` language vs. the Porter stemmer modes.**<br>17: - Pack 09 lists `porter` among the Snowball languages. Pack 23 (FP-02) describes Porter as its own family with a LINGORA default mode.<br>18: - **Built:** `SnowballStemmer("porter")` applies the *original* published Porter rules (Snowball's `porter` is the original algorithm), not the LINGORA extensions.<br>26: - Pack 23 (FP-02) says the built-in families are "exactly" Porter, Lancaster, Snowball, regular-expression, ISRI, ARLSTem, ARLSTem2, Cistem and RSLP, plus the WordNet lemmatizer.<br>27: - Pack 09 (Interface) lists `ARLSTem`, `ARLSTem2`, `LancasterStemmer`, `PorterStemmer`, `RegexpStemmer`, `SnowballStemmer`, `WordNetLemmatizer`. ISRI, Cistem and RSLP are not in the Interface at all.<br>48: - **G13 — Snowball languages other than `english` and `porter`.** Constructor accepts the 16 names from Pack 09; `stem` raises `NotImplementedError`. Not implemented in this release. | yes · upstream · BORDERLINE: NOTES.md:16-18 under 'Conflicts': Snowball porter vs Porter modes; built original Porter; not said to be unstated | |
| r20-haiku-export-3 | 23: \| `lingora/stem.py` \| FP-02 Porter, Lancaster, Snowball (english, porter), regexp stemmer; stubs \|<br>48: 3. **Porter "default mode" and Snowball `porter`.** FP-02 defines the default Porter mode as the<br>49: LINGORA extensions. `SnowballStemmer('porter')` (named in the Interface Contract, pack 09) is<br>51: LINGORA extensions; `SnowballStemmer('porter')` uses the original algorithm (its results are<br>88: - **Porter2 (`SnowballStemmer('english')`).** Standard Porter2 (R1/R2, exceptions, Y marking,<br>151: - Snowball stemmers for the 14 languages other than `english` and `porter` (arabic, danish, dutch,<br>318: \| N-000140 \| 23 \| partial \| lingora/stem.py \| SnowballStemmer accepts all 16 names, but only english (Porter2) and porter are implemented; the other 14 raise NotImplementedError at construction \|<br>319: \| N-000141 \| 23 \| partial \| lingora/stem.py \| SnowballStemmer accepts all 16 names, but only english (Porter2) and porter are implemented; the other 14 raise NotImplementedError at construction \|<br>341: \| N-000163 \| 23 \| partial \| lingora/stem.py \| SnowballStemmer accepts all 16 names, but only english (Porter2) and porter are implemented; the other 14 raise NotImplementedError at construction \|<br>571: \| N-000393 \| 09 \| partial \| lingora/stem.py \| SnowballStemmer accepts all 16 names, but only english (Porter2) and porter are implemented; the other 14 raise NotImplementedError at construction \| | yes · upstream · NOTES.md:48-52 under '…ambiguities': Snowball porter = original algorithm, 'its results are not specified anywhere else' | |
| r20-sonnet-export-1 | 32: - Snowball: only `english` (Porter2) and `porter` (original Porter) are faithful ports. The other | no · upstream ·  | |
| r20-sonnet-export-2 | 45: - Snowball: `english` (Porter2) and `porter` are full algorithms. The other 14 languages are | no · upstream ·  | |
| r20-sonnet-export-3 | 14: - **Snowball**: english (Porter2), porter, german, dutch, swedish, norwegian, danish, spanish, italian, | no · upstream ·  | |

## G10 — Porter: "Every word is stemmed without refusal, including a word whose stem reduces to a single letter" · upstream: `stem('oed')` = "o" · alternative: a one-letter stem is not returned: the word comes back unstemmed ("oed")

| Run | Lines from NOTES.md | Reading | Owner |
|---|---|---|---|
| r20-haiku-markdown-1 | 36: 4. **Spelling of the root label of chunk trees.** Interface §Chunking says the default root label is "the same for every parser and differs from clause labels", but the spelling is the implementer's choice. I use `SENT`, and `RegexpParser` refuses a grammar that defines a clause labelled `SENT`.<br>60: - **Punkt sentence splitting** is an approximation of Kiss and Strunk's algorithm using the packaged parameters: `?` and `!` always end a sentence; a period after a token that is a known abbreviation, a single letter (initial) or a number is not a break unless the next word is a known sentence start | no · upstream ·  | |
| r20-haiku-markdown-2 | 38: evidence, paragraph starts and a missing next word force it. Single letters count as initials. | no · upstream ·  | |
| r20-haiku-markdown-3 | 63: 7. **Refusal of a two-list `accuracy` on empty lists.** The spec states only the<br>145: - **Metrics refusals.** Non-set arguments to precision, recall and f-measure raise | no · upstream ·  | |
| r20-sonnet-markdown-1 | *(none)* | no · upstream ·  | |
| r20-sonnet-markdown-2 | *(none)* | no · upstream ·  | |
| r20-sonnet-markdown-3 | *(none)* | no · upstream ·  | |
| r20-haiku-export-1 | 165: - **Pack 05** (N-000338–N-000352): done. Every entry is a callable; refusals | no · upstream ·  | |
| r20-haiku-export-2 | *(none)* | no · upstream ·  | |
| r20-haiku-export-3 | 69: `##number##`, single-letter initials, and `...`) end a sentence only when the next word starts | no · upstream ·  | |
| r20-sonnet-export-1 | *(none)* | no · upstream ·  | |
| r20-sonnet-export-2 | *(none)* | no · upstream ·  | |
| r20-sonnet-export-3 | *(none)* | no · upstream ·  | |

## G13 — spans: "Slicing the original string at a span must recover the corresponding token"; "Slicing the input at each pair gives the corresponding token" · upstream: end offset exclusive (Python slice) · alternative: end offset inclusive

| Run | Lines from NOTES.md | Reading | Owner |
|---|---|---|---|
| r20-haiku-markdown-1 | 17: \| Snowball `arabic`, `danish`, `dutch`, `finnish`, `french`, `german`, `hungarian`, `italian`, `norwegian`, `portuguese`, `romanian`, `russian`, `spanish`, `swedish` \| `lingora/stem.py` \| **Not implemented** (constructor raises `NotImplementedError`) \|<br>57: - **Chart parser.** Exhaustive. A derivation that revisits the same symbol over the same span (a cycle of unit productions) is cut off, so the number of trees is always finite. | no · upstream ·  | |
| r20-haiku-markdown-2 | 57: `german`, `hungarian`, `italian`, `norwegian`, `portuguese`, `romanian`, `russian`, `spanish`,<br>95: - The chart parser is exhaustive. Memoised over spans, with cycle cutting, so unit and epsilon<br>155: - Checks passed: tokenizers (Treebank, recommended, tweet, regex, blank-line, span), Punkt on | no · upstream ·  | |
| r20-haiku-markdown-3 | 14: russian, spanish, swedish). Only `english` (Porter2) and `porter` (original Porter)<br>85: brackets. `e.g.` is not split mid-text. Penn Treebank spans are recovered by<br>122: - **Chart parser.** Returns every derivation tree over each span. A cycle guard stops | no · upstream ·  | |
| r20-sonnet-markdown-1 | 24: - Snowball: English (Porter2), porter, German, Dutch, Spanish, French, Swedish, Norwegian, Danish and Russian are implemented from the published algorithm descriptions (compact versions, only spot-checked). **Arabic, Finnish, Hungarian, Italian, Portuguese and Romanian are accepted as language names | no · upstream ·  | |
| r20-sonnet-markdown-2 | 24: - A quoted empty terminal `""` matches an empty span in parsers and adds no leaf; shift-reduce ignores<br>36: - Snowball: full ports exist for english, porter, german, dutch, swedish, norwegian, danish, spanish, russian | no · upstream ·  | |
| r20-sonnet-markdown-3 | 39: - Snowball: English, Porter, German, Dutch (original), Swedish, Norwegian, Danish, Spanish, Russian are implemented. | no · upstream ·  | |
| r20-haiku-export-1 | 15: \| `lingora/tokenize.py`, `lingora/_punkt.py` \| word/punct, Treebank, recommended word tokenizer, whitespace, blank-line, regexp, tweet, spans; Punkt sentence splitter \|<br>109: order. Trees are finite under cycles (a `(symbol, span)` already on the path | no · upstream ·  | |
| r20-haiku-export-2 | 40: - **G5 — Span tokenizers.** `span_tokenize` is provided for `WordPunctTokenizer`, `WhitespaceTokenizer` and `RegexpTokenizer` only. Treebank and Tweet tokenizers have no span method.<br>61: - **G20 — Chart parser.** Exhaustive, memoised over spans. A derivation that cycles back on the same span (for example unit cycles) is omitted, since such derivations are infinitely ambiguous. | no · upstream ·  | |
| r20-haiku-export-3 | 111: - **Chart parser.** Exhaustive (memoised over spans). Derivations that cycle back through the same<br>112: (symbol, span) are cut, so cyclic grammars give finitely many trees.<br>152: finnish, french, german, hungarian, italian, norwegian, portuguese, romanian, russian, spanish,<br>162: - `span_tokenize` for the Treebank and tweet tokenizers (not listed in the Interface Contract). | no · upstream ·  | |
| r20-sonnet-export-1 | *(none)* | no · upstream ·  | |
| r20-sonnet-export-2 | *(none)* | no · upstream ·  | |
| r20-sonnet-export-3 | 14: - **Snowball**: english (Porter2), porter, german, dutch, swedish, norwegian, danish, spanish, italian, | no · upstream ·  | |

## G14 — Penn Treebank: "A comma or colon is split off unless a digit follows it" · upstream: "1,000" kept whole · alternative: comma always split off

| Run | Lines from NOTES.md | Reading | Owner |
|---|---|---|---|
| r20-haiku-markdown-1 | 29: \| `tokenize` command line \| `lingora/cli.py`, `lingora/__main__.py` \| Done (no click dependency; `cli.main(args=..., standalone_mode=...)`) \|<br>33: 1. **Treebank comma and colon splitting.** PRD FP-01 says the Penn Treebank word tokenizer "follows the Penn Treebank tokenization conventions", but its explicit list of split punctuation (`; @ # $ % & ? !` and brackets) does not mention commas or colons. Penn Treebank splits them, so I follow the c<br>65: - **Command-line tokenize** loads the Punkt model before reading input; when it is missing the command prints an error to stderr, exits with status 1 and writes nothing to stdout. Options: `--language` (default `english`), `--delimiter` (default one space), `--encoding` (default UTF-8). Each input l<br>74: - Missing-model failures were checked: `sent_tokenize`, `word_tokenize(preserve_line=False)`, `pos_tag` (English and Russian), `ne_chunk`, `SnowballStemmer(..., ignore_stopwords=True)` and `WordNetLemmatizer` all raise; the `tokenize` command exits 1 with no output. | yes · upstream · NOTES.md:33 under 'Spec disagreements': list 'does not mention commas or colons'; split, except before a digit | |
| r20-haiku-markdown-2 | 12: 1. **Penn Treebank comma and colon.** `spec/Full_PRD.md` FP-01 says the Penn Treebank tokenizer<br>15: Commas and colons are not in that list. Built: the explicit list wins, so `Hello, world`<br>16: gives `Hello,` and `world`. Conventional PTB/NLTK tokenizers split commas and colons; if<br>133: ### Command line (`lingora/cli.py`, `lingora/__main__.py`)<br>138: - An empty input line produces an empty output line. The command reads all of stdin before writing; | yes · upstream · NOTES.md:12-18 under 'Conflicts': commas and colons not in the list; built: not split at all ('the explicit list wins'); probe item 1,000 reads upstream, see note in TRIAL.md | |
| r20-haiku-markdown-3 | 31: 1. **Commas and colons in the Penn Treebank tokenizer.** `spec/Full_PRD.md:101`<br>34: commas and colons. **Built:** `,` and `:` are split unless followed by a digit<br>35: (so `1,000` stays whole). This follows the standard Treebank rule.<br>59: written "for the failed input", and `spec/Full_PRD.md:134` says the command writes | yes · upstream · NOTES.md:31-34 under 'Spec disagreements and ambiguities': lists not , or :; split unless followed by a digit | |
| r20-sonnet-markdown-1 | *(none)* | yes · upstream · NOTES.md:8 under 'Disagreements': list 'does not mention : and ,'; followed PTB (split unless between digits) | |
| r20-sonnet-markdown-2 | 4: Command line: `python -m lingora tokenize` or `lingora.cli.cli.main(args=[...])`. `click` is not | no · upstream ·  | |
| r20-sonnet-markdown-3 | 35: - CLI: `lingora tokenize [-l LANG] [-d DELIM] [-e ENC]`, built without third-party deps (a minimal command group | no · upstream ·  | |
| r20-haiku-export-1 | 23: \| `lingora/cli.py` \| `cli.main(args, standalone_mode)`; `tokenize` command \|<br>57: - **Treebank commas and colons.** `pack 22` (N-000089–N-000098) lists which<br>133: failure stops the command, and no token line is written for that input); | yes · upstream · NOTES.md:57-60 under 'Gaps': does not mention , or :; split unless between digits | |
| r20-haiku-export-2 | 20: **C3 — Penn Treebank comma and colon.**<br>21: - Pack 22 (FP-01) lists the characters that are split off as tokens of their own (`; @ # $ % & ? !`, brackets, ellipsis, final point, clitics). Commas and colons are not in that list.<br>22: - The spec says the tokenizer follows "the Penn Treebank tokenization conventions", which split commas and colons; the list above does not mention them, and no example in the spec settles it.<br>23: - **Built:** comma and colon are split off unless followed by a digit (so `1,000` stays whole). This is an assumption on my part; the spec does not state it. | yes · upstream · NOTES.md:20-23: 'This is an assumption on my part; the spec does not state it'; split unless followed by a digit | |
| r20-haiku-export-3 | 30: \| `lingora/cli.py`, `lingora/__main__.py` \| command line (`tokenize`), `python -m lingora` \|<br>37: 1. **Penn Treebank commas and colons.** FP-01 (pack 22, N-000089–N-000094) lists the characters<br>38: that are split off (`; @ # $ % & ? !`, brackets, the ellipsis) and does not mention commas or<br>39: colons, while the same section and the Interface Contract (pack 07) describe the tokenizer as<br>40: following the Penn Treebank conventions. **Built:** commas and colons are split off, except a<br>41: colon or comma before a digit, as in the Treebank convention. | yes · upstream · NOTES.md:37-41 under 'conflicts and ambiguities': does not mention commas or colons; split except before a digit | |
| r20-sonnet-export-1 | 12: - Interface Contract says command options (language, delimiter, encoding) are the implementer's | no · upstream ·  | |
| r20-sonnet-export-2 | *(none)* | no · upstream ·  | |
| r20-sonnet-export-3 | 49: - `word_tokenize` PTB variant: commas/colons are split like the reference Treebank tokenizer even though the PRD | yes · upstream · BORDERLINE: NOTES.md:49-50 under 'Spec gaps / assumptions': commas/colons split 'like the reference Treebank tokenizer even though the PRD lists only some punctuation'; digit exception not written | |

## G16 — "Whitespace in a tag pattern is ignored" / "Whitespace in a pattern is ignored" · upstream: `{<DT> <NN>}` matches "the dog" · alternative: whitespace significant (no match)

| Run | Lines from NOTES.md | Reading | Owner |
|---|---|---|---|
| r20-haiku-markdown-1 | *(none)* | no · upstream ·  | |
| r20-haiku-markdown-2 | *(none)* | no · upstream ·  | |
| r20-haiku-markdown-3 | *(none)* | no · upstream ·  | |
| r20-sonnet-markdown-1 | *(none)* | no · upstream ·  | |
| r20-sonnet-markdown-2 | *(none)* | no · upstream ·  | |
| r20-sonnet-markdown-3 | *(none)* | no · upstream ·  | |
| r20-haiku-export-1 | *(none)* | no · upstream ·  | |
| r20-haiku-export-2 | *(none)* | no · upstream ·  | |
| r20-haiku-export-3 | *(none)* | no · upstream ·  | |
| r20-sonnet-export-1 | *(none)* | no · upstream ·  | |
| r20-sonnet-export-2 | *(none)* | no · upstream ·  | |
| r20-sonnet-export-3 | 46: (a whitespace-only text with a custom gap pattern returns the piece). | no · upstream ·  | |

## G17 — "An empty tagged-token list yields a chunk structure with a sentence root and no children" · upstream: root, no children · alternative: refused (raises)

| Run | Lines from NOTES.md | Reading | Owner |
|---|---|---|---|
| r20-haiku-markdown-1 | 41: - **Packaged-resource search path.** `data.path` starts as the entries of the `LINGORA_DATA` environment variable (separated by `os.pathsep`), or as an empty list. No packaged data is searched by default, so every model-dependent path fails until a caller adds a directory.<br>42: - **Accuracy of empty lists.** `metrics.accuracy([], [])` and `classify.accuracy(c, [])` raise `ValueError`. The spec does not say what an empty comparison returns. | no · upstream ·  | |
| r20-haiku-markdown-2 | 115: an empty list raises `ValueError`.<br>122: - `accuracy` on two empty lists raises `ValueError`.<br>138: - An empty input line produces an empty output line. The command reads all of stdin before writing; | no · upstream ·  | |
| r20-haiku-markdown-3 | 63: 7. **Refusal of a two-list `accuracy` on empty lists.** The spec states only the<br>64: different-length case (`spec/Full_PRD.md:279`). **Built:** empty lists raise | no · upstream ·  | |
| r20-sonnet-markdown-1 | 13: - `accuracy` (metrics and classify) on empty lists raises `ZeroDivisionError` (spec silent). `jaccard_distance` of two empty sets returns 0.0 (spec silent). | no · upstream ·  | |
| r20-sonnet-markdown-2 | 22: - `accuracy`/`jaccard_distance` on empty input raise `ZeroDivisionError` (undefined, not 0). | no · upstream ·  | |
| r20-sonnet-markdown-3 | *(none)* | no · upstream ·  | |
| r20-haiku-export-1 | 135: (default `english`), `--delimiter/-d` (default one space). An empty input | no · upstream ·  | |
| r20-haiku-export-2 | *(none)* | no · upstream ·  | |
| r20-haiku-export-3 | 128: - **Accuracy on empty lists.** `metrics.accuracy` and `classify.accuracy` raise `ValueError` for<br>129: empty input (the spec does not say; the ratio is undefined). | no · upstream ·  | |
| r20-sonnet-export-1 | 20: - `accuracy` / `classify.accuracy` of empty lists: return 0.0. `jaccard_distance` of two empty | no · upstream ·  | |
| r20-sonnet-export-2 | *(none)* | no · upstream ·  | |
| r20-sonnet-export-3 | 33: - `accuracy` on two empty lists raises `ValueError` (spec only defines different lengths). | no · upstream ·  | |

## G18 — a chunk grammar "that is not text and not a list of chunk-parser stages is refused"; "Any other value makes the constructor raise" · upstream: `RegexpParser(42)` raises · alternative: taken as an empty grammar

| Run | Lines from NOTES.md | Reading | Owner |
|---|---|---|---|
| r20-haiku-markdown-1 | 59: - **Tree children** may be strings, `Tree`s, or `(token, tag)` tuples (the last is used by the chunk parser). `Tree(label, [])` is valid; a `str` or a missing argument raises `TypeError`.<br>68: - **Exceptions.** `lingora.data.ResourceNotFoundError` (a `LookupError`) is raised for any missing packaged resource. `TypeError` is raised for wrong argument types (for example a `str` passed where a token list is required), and `ValueError` for bad values. | no · upstream ·  | |
| r20-haiku-markdown-2 | 109: - `Tree` equality compares labels and children. `Tree(label)` and string children raise `TypeError`. | no · upstream ·  | |
| r20-haiku-markdown-3 | 118: objects is not supported (`TypeError`).<br>144: - **Jaccard distance.** Both sets empty gives `0.0`. Non-set arguments raise `TypeError`.<br>146: `TypeError`. Accuracy on lists of different lengths raises `ValueError`. | no · upstream ·  | |
| r20-sonnet-markdown-1 | *(none)* | no · upstream ·  | |
| r20-sonnet-markdown-2 | 20: raise `TypeError`; unknown `tagset` raises `ValueError`. | no · upstream ·  | |
| r20-sonnet-markdown-3 | *(none)* | no · upstream ·  | |
| r20-haiku-export-1 | *(none)* | no · upstream ·  | |
| r20-haiku-export-2 | 74: - **G29 — `Tree` constructor.** `label` is stored as `str(label)`. `children` must be a `list` (a `str`, or omitting it, raises `TypeError`). | no · upstream ·  | |
| r20-haiku-export-3 | 145: - **Errors.** Exception classes are `TypeError` for wrong argument types, `ValueError` for bad | no · upstream ·  | |
| r20-sonnet-export-1 | 23: - Resource-missing errors raise `LookupError`; bad types raise `TypeError`; bad values `ValueError`. | no · upstream ·  | |
| r20-sonnet-export-2 | 26: `pos_tag` raises `TypeError` for a str, `ValueError` for bad `lang`/`tagset`. | no · upstream ·  | |
| r20-sonnet-export-3 | 56: - Pack 05 says exception classes/messages are free; I used `LookupError` (missing resource), `TypeError` | no · upstream ·  | |

## G20 — "Two trees are equal exactly when their labels are equal and their children are equal pairwise, recursively" · upstream: equality compares labels and children · alternative: labels ignored (children only)

| Run | Lines from NOTES.md | Reading | Owner |
|---|---|---|---|
| r20-haiku-markdown-1 | 35: 3. **BLEU weights.** PRD FP-07 says the precisions are "combined as a geometric mean weighted by the caller's weights" and also says "standard sentence-level BLEU (Papineni et al., 2002)". I compute `BP * exp(sum_n w_n * log p_n)` without renormalising the weights, which equals the standard formula  | no · upstream ·  | |
| r20-haiku-markdown-2 | 109: - `Tree` equality compares labels and children. `Tree(label)` and string children raise `TypeError`. | yes · upstream · NOTES.md:109 under 'Assumptions for points the spec does not state': 'Tree equality compares labels and children' | |
| r20-haiku-markdown-3 | *(none)* | no · upstream ·  | |
| r20-sonnet-markdown-1 | *(none)* | no · upstream ·  | |
| r20-sonnet-markdown-2 | *(none)* | no · upstream ·  | |
| r20-sonnet-markdown-3 | *(none)* | no · upstream ·  | |
| r20-haiku-export-1 | 20: \| `lingora/tree.py` \| `Tree`: construct, `fromstring`, `label`, `leaves`, `pformat`, `==`, iteration \| | no · upstream ·  | |
| r20-haiku-export-2 | *(none)* | no · upstream ·  | |
| r20-haiku-export-3 | 103: - **Sequential taggers.** Unigram ties: the first-seen tag wins among equal counts (N-000189). | no · upstream ·  | |
| r20-sonnet-export-1 | 25: `Nonterminal` objects (not `str`, `str()` = name, `==` also accepts a `str`). | no · upstream ·  | |
| r20-sonnet-export-2 | 28: - Empty equal-length lists: `metrics.accuracy` and `classify.accuracy` return `0.0`. | no · upstream ·  | |
| r20-sonnet-export-3 | *(none)* | no · upstream ·  | |

## G23 — Naive Bayes: "uses only the features … that occurred in training. A feature name never seen in training is ignored" · upstream: unseen feature ignored · alternative: refused (raises)

| Run | Lines from NOTES.md | Reading | Owner |
|---|---|---|---|
| r20-haiku-markdown-1 | 47: - **Naive Bayes smoothing.** Add-one smoothing per label over the distinct values seen for each feature in training. A `(feature, value)` pair never seen in training is ignored; a feature absent from a featureset contributes nothing. Labels are listed in order of first appearance in training. | yes · upstream · BORDERLINE: NOTES.md:47 under 'Gaps filled by assumption': 'A (feature, value) pair never seen in training is ignored' (a pair, not a feature name) | |
| r20-haiku-markdown-2 | 113: frequencies, with `\|V\|+1` bins. A feature value never seen in training is ignored at<br>117: branch for an absent feature. An unseen value falls back to the node's majority label. No | yes · upstream · BORDERLINE: NOTES.md:113-114 under 'Assumptions…': 'A feature value never seen in training is ignored at classify time' (a value, not a feature name) | |
| r20-haiku-markdown-3 | 130: Features absent from a featureset, and features never seen in training, are ignored.<br>133: A feature missing from a featureset counts as `None`. Unseen values fall back to the | yes · upstream · NOTES.md:130 under 'Details the spec does not state': 'features never seen in training, are ignored' | |
| r20-sonnet-markdown-1 | *(none)* | no · upstream ·  | |
| r20-sonnet-markdown-2 | *(none)* | no · upstream ·  | |
| r20-sonnet-markdown-3 | *(none)* | no · upstream ·  | |
| r20-haiku-export-1 | 83: from a featureset counts as value `None`. Unseen values fall back to the | yes · upstream · NOTES.md:85-87 under 'Gaps': 'Features not seen in training are ignored' | |
| r20-haiku-export-2 | 64: - **G23 — Decision tree.** Chooses at each node the feature whose single-level test (majority label per value; absent feature = its own value `None`) has the fewest training errors, and stops when that does not beat the node's majority leaf. Ties: first feature in order of first appearance. Unseen v | yes · upstream · NOTES.md:65 under 'Gaps': 'Features absent from training are ignored at classification time' | |
| r20-haiku-export-3 | *(none)* | no · upstream ·  | |
| r20-sonnet-export-1 | *(none)* | no · upstream ·  | |
| r20-sonnet-export-2 | *(none)* | no · upstream ·  | |
| r20-sonnet-export-3 | 36: example count as value `None`; features never seen in training are ignored at classification time.<br>38: and recurses until pure; unseen feature values fall back to the node's majority label. | yes · upstream · NOTES.md:35-36 under 'Spec gaps / assumptions': 'features never seen in training are ignored at classification time' | |

## G24 — "A featureset that shares no feature with the training data still receives one of the trained labels … never refused" · upstream: a trained label · alternative: refused (raises)

| Run | Lines from NOTES.md | Reading | Owner |
|---|---|---|---|
| r20-haiku-markdown-1 | *(none)* | no · upstream ·  | |
| r20-haiku-markdown-2 | 112: - **Naive Bayes.** Smoothing is ELE-style (`+0.5`) for priors and for per-label value | no · upstream ·  | |
| r20-haiku-markdown-3 | *(none)* | no · upstream ·  | |
| r20-sonnet-markdown-1 | *(none)* | no · upstream ·  | |
| r20-sonnet-markdown-2 | *(none)* | no · upstream ·  | |
| r20-sonnet-markdown-3 | *(none)* | no · upstream ·  | |
| r20-haiku-export-1 | *(none)* | no · upstream ·  | |
| r20-haiku-export-2 | *(none)* | no · upstream ·  | |
| r20-haiku-export-3 | 120: - **Naive Bayes (N-000277–N-000281).** Label priors are maximum likelihood. Feature values use the | no · upstream ·  | |
| r20-sonnet-export-1 | *(none)* | no · upstream ·  | |
| r20-sonnet-export-2 | *(none)* | no · upstream ·  | |
| r20-sonnet-export-3 | 35: - Naive Bayes smoothing: Lidstone (+0.5) on label priors and per-label feature-value counts, features absent from an | no · upstream ·  | |

