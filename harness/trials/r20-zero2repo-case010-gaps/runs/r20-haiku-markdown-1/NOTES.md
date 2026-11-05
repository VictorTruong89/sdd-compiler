# LINGORA build notes

Implementation of the specification in `spec/` (PRD, Hardware Requirements, Interface Contract).
Package: `/app/lingora` (flat layout, pure Python, no third-party dependencies, Python 3.10+).
Packaging metadata: `/app/pyproject.toml`. Import from `/app` (or after an editable install).

## Status

| Area | Module | Status |
| --- | --- | --- |
| Packaged-resource finder | `lingora/data.py` | Done |
| Word/punct, Treebank, recommended word, whitespace, blank-line, regexp, tweet tokenizers | `lingora/tokenize.py` | Done |
| Punkt sentence splitter | `lingora/punkt.py`, `lingora/tokenize.py` | Done, algorithm approximated (see below); not run against real packaged models (none are installed here) |
| Porter (lingora / original / martin modes) | `lingora/stem.py` | Done for `lingora` and `original`; `martin` approximated |
| Lancaster (Paice/Husk) | `lingora/stem.py` | Done; rule table written from the published table, checked on a few known words |
| Snowball `english` (Porter2), `porter` | `lingora/stem.py` | Done |
| Snowball `arabic`, `danish`, `dutch`, `finnish`, `french`, `german`, `hungarian`, `italian`, `norwegian`, `portuguese`, `romanian`, `russian`, `spanish`, `swedish` | `lingora/stem.py` | **Not implemented** (constructor raises `NotImplementedError`) |
| Regular-expression stemmer | `lingora/stem.py` | Done |
| ISRI / ARLSTem / ARLSTem2 / Cistem / RSLP / WordNet lemmatizer | `lingora/stem.py` | **Not implemented**; `WordNetLemmatizer` checks for WordNet and raises when it is missing, and raises `NotImplementedError` when it is present |
| Default, unigram, bigram, trigram, affix, regexp taggers, with backoff | `lingora/tag.py` | Done |
| Averaged perceptron tagger (English, Russian), universal mapping | `lingora/tag.py` | Done; algorithm and features follow textblob-aptagger/NLTK from memory, not verified against the packaged weights |
| Regexp chunk parser (chunk, chink, cascade, quantifiers) | `lingora/chunk.py` | Done |
| Named-entity chunker `ne_chunk` | `lingora/chunk.py` | Checks both resources and raises when missing; **model loading not implemented** |
| CFG reader, chart parser, shift-reduce parser, generator | `lingora/grammar.py`, `lingora/parse/` | Done |
| Trees (build, bracketed text, compare, leaves, pformat) | `lingora/tree.py` | Done |
| Naive Bayes (with probability distribution), decision tree, accuracy | `lingora/classify.py` | Done |
| Edit distance (with transpositions), Jaccard, accuracy, precision, recall, f-measure | `lingora/metrics.py` | Done |
| BLEU | `lingora/translate.py` | Done |
| `tokenize` command line | `lingora/cli.py`, `lingora/__main__.py` | Done (no click dependency; `cli.main(args=..., standalone_mode=...)`) |

## Spec disagreements and how they were resolved

1. **Treebank comma and colon splitting.** PRD FP-01 says the Penn Treebank word tokenizer "follows the Penn Treebank tokenization conventions", but its explicit list of split punctuation (`; @ # $ % & ? !` and brackets) does not mention commas or colons. Penn Treebank splits them, so I follow the convention: `"a,b"` becomes `a , b` and `"x:y"` becomes `x : y`, except that a comma or colon directly before a digit is not split (`3,50` stays intact, as in the convention).
2. **Ellipsis in the tweet tokenizer.** PRD FP-01 says "other punctuation marks are tokens of their own", but a run of two or more points is a token in the recommended tokenizer. For the tweet tokenizer I kept a run of two or more points (`...`) as one token; single punctuation marks are one token each.
3. **BLEU weights.** PRD FP-07 says the precisions are "combined as a geometric mean weighted by the caller's weights" and also says "standard sentence-level BLEU (Papineni et al., 2002)". I compute `BP * exp(sum_n w_n * log p_n)` without renormalising the weights, which equals the standard formula when the weights sum to 1 (the default) and matches the NLTK convention. Weights that do not sum to 1 are not rescaled.
4. **Spelling of the root label of chunk trees.** Interface §Chunking says the default root label is "the same for every parser and differs from clause labels", but the spelling is the implementer's choice. I use `SENT`, and `RegexpParser` refuses a grammar that defines a clause labelled `SENT`.
5. **Interface §Chunking allows a list of stages as `grammar`.** Only the text form is accepted.

## Gaps filled by assumption (not stated in the spec)

- **Packaged-resource search path.** `data.path` starts as the entries of the `LINGORA_DATA` environment variable (separated by `os.pathsep`), or as an empty list. No packaged data is searched by default, so every model-dependent path fails until a caller adds a directory.
- **Accuracy of empty lists.** `metrics.accuracy([], [])` and `classify.accuracy(c, [])` raise `ValueError`. The spec does not say what an empty comparison returns.
- **Jaccard distance of two empty sets** is `0.0`.
- **Precision/recall of an empty set** returns `None` (per the spec); f-measure returns `None` when either set is empty and `0.0` when precision or recall is 0.
- **Edit distance** returns an `int` for integer costs and a `float` otherwise.
- **BLEU.** An empty hypothesis scores `0.0`. A zero numerator in any weighted order gives `0.0`. An optional `smoothing_function` may be passed; it receives and returns `(numerator, denominator)` pairs.
- **Naive Bayes smoothing.** Add-one smoothing per label over the distinct values seen for each feature in training. A `(feature, value)` pair never seen in training is ignored; a feature absent from a featureset contributes nothing. Labels are listed in order of first appearance in training.
- **Decision tree.** ID3 with information gain. A feature missing from an example is a separate branch (value `None`). Ties go to the feature name that sorts first. A value not seen at a node falls back to that node's majority label.
- **Unigram/bigram/trigram ties** are broken by the lexicographically smallest tag.
- **Regexp tagger** uses `re.match` at the token start, first matching rule wins.
- **Chunk parser semantics.**
  - A chunk rule matches over the root's units: leaf tokens, and chunks built by earlier clauses (treated as one unit labelled with the clause label). A match never includes a token inside a chunk built by the same clause.
  - A chink rule removes leaf tokens only from chunks built by the same clause; a chunk is split into the pieces on either side, and chinked tokens become root children.
  - Zero-length matches are ignored.
  - Matches are found by a regular expression over the encoded tag sequence, so a match always starts and ends on a unit boundary.
- **Shift-reduce parser.** Reductions are tried in written order and the first matching production wins. Productions with an empty right-hand side are never used for reduction (they would loop forever). A token the grammar cannot produce raises.
- **Chart parser.** Exhaustive. A derivation that revisits the same symbol over the same span (a cycle of unit productions) is cut off, so the number of trees is always finite.
- **Generator.** With `depth=None`, sentences are produced in increasing order of derivation height (so recursive grammars work with `n`). The generator stops when no derivation has been found for a height window of `(number of nonterminals + 1)` beyond the last height that produced sentences. A finite grammar therefore terminates; an infinite grammar produces sentences until `n` is reached. With `depth=d`, derivation height is bounded by `d` and sentences come out in the grammar's written production order.
- **Tree children** may be strings, `Tree`s, or `(token, tag)` tuples (the last is used by the chunk parser). `Tree(label, [])` is valid; a `str` or a missing argument raises `TypeError`.
- **Punkt sentence splitting** is an approximation of Kiss and Strunk's algorithm using the packaged parameters: `?` and `!` always end a sentence; a period after a token that is a known abbreviation, a single letter (initial) or a number is not a break unless the next word is a known sentence starter or the orthographic heuristic says it starts a sentence; ellipses break before a capitalised word; collocations suppress a break; an ordinary period is a break unless the orthographic heuristic says the next word is lower-case. Sentences are returned as the original text, stripped of the whitespace separating them.
- **Recommended word tokenizer** splits the text into sentences first (Punkt), then applies the Treebank rules to each sentence. Typographic quotes (U+2018–U+201F), dashes (U+2012–U+2015), asterisks, runs of two or more points, and `--` are split off as tokens before the Treebank rules run on the pieces in between.
- **Porter lingora mode** returns irregular forms from a small built-in table (for example `skies`→`sky`, `dying`→`die`); the spec leaves the table's content open. Words of one or two letters are returned after the lowercasing and table steps.
- **Snowball stopword skipping** reads `corpora/stopwords/<language>` (one word per line, UTF-8). It is checked on the lowercased word.
- **Blank-line tokenizer.** A separator is `\s*\n\s*\n\s*`. Trailing spaces on the last segment are kept.
- **Command-line tokenize** loads the Punkt model before reading input; when it is missing the command prints an error to stderr, exits with status 1 and writes nothing to stdout. Options: `--language` (default `english`), `--delimiter` (default one space), `--encoding` (default UTF-8). Each input line is one output line.
- **Named-entity chunking** raises `ResourceNotFoundError` when either the model or the wordlist is missing, and `NotImplementedError` when both are present (model loading is not implemented).
- **Averaged perceptron** `pos_tag(tokens, tagset='universal', lang='rus')` maps the part before `=` of a Russian National Corpus tag with a fixed table (noun→NOUN, verb→VERB, and so on); unknown categories map to `X`. For English, `universal` requires `taggers/universal_tagset/en-ptb.map`; without it the call raises.
- **Exceptions.** `lingora.data.ResourceNotFoundError` (a `LookupError`) is raised for any missing packaged resource. `TypeError` is raised for wrong argument types (for example a `str` passed where a token list is required), and `ValueError` for bad values.

## Verification done here

- No packaged data exists on this machine, so model-dependent paths (Punkt, perceptron tagger, universal map, stopwords) were exercised with small fabricated resources placed under `/tmp` and selected via `LINGORA_DATA` or `lingora.data.path`. The fabricated data is not part of the deliverable.
- Hand-checked outputs: tokenizers on sample sentences and clitics; Porter and Snowball English on a set of common words; Lancaster on known words (`maximum`→`maxim`, `presumably`→`presum`, `provision`→`provid`, `saying`→`say`); chunker cascade, chink and quantifiers; chart parser ambiguity (`S -> S S | 'a'` gives 2 trees for `a a a`); generator order; BLEU on simple examples; Naive Bayes and decision tree on tiny data; edit distance (`kitten`/`sitting`=3, `ca`/`abc` with transpositions=2).
- Missing-model failures were checked: `sent_tokenize`, `word_tokenize(preserve_line=False)`, `pos_tag` (English and Russian), `ne_chunk`, `SnowballStemmer(..., ignore_stopwords=True)` and `WordNetLemmatizer` all raise; the `tokenize` command exits 1 with no output.

## Not in the feature set (left out on purpose)

Packaged corpora and the downloader, WordNet itself, graphical demos, chat/Twitter/Hugging Face helpers, external-binary wrappers, CCG/DRT/inference, the s-expression tokenizer, n-gram language models, sentiment lexicons.
