# NOTES

Implementation of the LINGORA specification in `spec/` (read-only). Layout follows
`spec/MAP.md`: package `lingora/` at the repository root, tests in `tests/`.

Run the tests from `/app`: `python3 -m pytest -q` (61 tests, all passing on Python 3.13.18).
The package has no runtime dependencies and needs no install step: put `/app` on the import
path (the working directory is enough). `pyproject.toml` describes a flat-layout build.

**Important limitation.** The packaged resources (Punkt models, averaged perceptron taggers,
universal tagset tables, WordNet, stopword lists, NE chunker model) are not in this repository,
and the spec says they live outside the source tree. The tests therefore use small synthetic
resource directories (`tests/conftest.py`) that follow the file layout the spec names. Code that
depends on the published model files is implemented from the spec's format description, but its
output has **not** been checked against the real models.

## Files

| Module | Covers |
|---|---|
| `lingora/__init__.py`, `lingora/data.py` | package, `lingora.data` (`path`, resource finder) |
| `lingora/tokenize.py`, `lingora/_punkt.py` | FP-01 tokenizers, Punkt sentence splitting |
| `lingora/stem.py` | FP-02 Porter, Lancaster, Snowball (english, porter), regexp stemmer; stubs |
| `lingora/tag.py` | FP-03 default/unigram/regexp taggers, averaged-perceptron `pos_tag`, universal tagset |
| `lingora/chunk.py` | FP-04 chunk grammar parser, `ne_chunk` gate |
| `lingora/grammar.py`, `lingora/parse/` | FP-05 CFG reader, chart and shift-reduce parsers, `generate` |
| `lingora/tree.py` | FP-05 trees |
| `lingora/classify.py` | FP-06 Naive Bayes, decision tree, accuracy |
| `lingora/metrics.py`, `lingora/translate.py` | FP-07 edit distance, Jaccard, accuracy, precision/recall/f, BLEU |
| `lingora/cli.py`, `lingora/__main__.py` | command line (`tokenize`), `python -m lingora` |

Spec ids are marked in code comments (`# spec: N-000xxx`). Tests are named after node ids
(`test_N_000085_...`), since the spec has no acceptance-criteria labels.

## Spec conflicts and ambiguities (what I built)

1. **Penn Treebank commas and colons.** FP-01 (pack 22, N-000089–N-000094) lists the characters
   that are split off (`; @ # $ % & ? !`, brackets, the ellipsis) and does not mention commas or
   colons, while the same section and the Interface Contract (pack 07) describe the tokenizer as
   following the Penn Treebank conventions. **Built:** commas and colons are split off, except a
   colon or comma before a digit, as in the Treebank convention.
2. **Chunk rule scope.** FP-04 says a chunk rule's matches are "among tokens not yet in a chunk"
   (pack 25, N-000223–N-000226), but also that a later clause "sees every chunk built by an earlier
   clause as a single unit whose tag is that chunk's label" (N-000230–N-000233). **Built:** a chunk
   from an earlier clause is one unit tagged with its label, and later chunk rules may match it
   (the usual cascade, e.g. `VP: {<VB.*><NP>*}`). Chunks built by the same clause are opaque to that
   clause's chunk rules. A chink rule only splits chunks built earlier in the same clause.
3. **Porter "default mode" and Snowball `porter`.** FP-02 defines the default Porter mode as the
   LINGORA extensions. `SnowballStemmer('porter')` (named in the Interface Contract, pack 09) is
   the original published algorithm, without the extensions. **Built:** `PorterStemmer()` uses the
   LINGORA extensions; `SnowballStemmer('porter')` uses the original algorithm (its results are
   not specified anywhere else).
4. **Chunk stages.** The Interface Contract (pack 11) allows a grammar given as a list of stages.
   **Built:** a list is read as a sequence of grammar strings, each applied to the result of the
   previous one.
5. **Interface shape of the CLI.** The Interface Contract (pack 08) describes a Click-style group.
   Click is not installed here and runtime dependencies must be pure Python, so **built:** a
   small `argparse`-free group object with the same `main(args=..., standalone_mode=...)` shape.

## Gaps the spec does not state, and what I assumed

- **Data finder initial path (N-000353–N-000356).** `lingora.data.path` starts with the entries of
  the `LINGORA_DATA` environment variable (path-separator separated), then `<repo>/lingora_data`
  and `~/lingora_data`. Only existing directories are searched; the list is read at every lookup.
- **Punkt decision rules (N-000122–N-000126).** The spec names the parameters but not the decision
  procedure. My rules (`lingora/_punkt.py`): tokens are whitespace runs; a token ends a sentence
  candidate if it ends in `.`, `?` or `!` after closing quotes/brackets are removed.
  `?` and `!` always end a sentence. For `.`, abbreviations (`abbrev_types`, numbers as
  `##number##`, single-letter initials, and `...`) end a sentence only when the next word starts
  with a capital and is a sentence starter or the orthographic context says it starts a sentence
  (an upper-case word seen lower-case inside sentences, with no upper-case-inside observations).
  An ordinary period ends a sentence unless the next word starts lower-case. A collocation pair
  (`collocations.tab`) suppresses the break. Sentences are original text slices with the
  inter-sentence whitespace removed. Not validated against real Punkt output.
- **Recommended word tokenizer (N-000099–N-000105).** Typographic double quotes `“ ” „ ‟` are
  split off as their own tokens. Typographic single quotes `‘ ’` are split only at word
  boundaries, so `don’t` stays one word. Dashes U+2012–U+2015, asterisks, runs of two or more
  points, and `--` are tokens. `word_tokenize` defaults to `preserve_line=False`.
- **Tweet tokenizer (N-000112–N-000118).** The emoticon, URL and hashtag patterns are my own.
  Handles match `@` not preceded by a word character, followed by 1–15 ASCII letters, digits or
  underscores, and not continued by another such character. Dots in runs of two or more are one
  token. Unicode `\w` keeps accented letters whole.
- **Blank-line tokenizer.** Pieces are stripped and empty pieces dropped.
- **Porter (LINGORA mode).** The irregular-forms table is a small built-in table (N-000147);
  the spec leaves its entries to me. `to_lowercase=False` leaves upper-case letters unchanged
  (the rules are lower-case only). The `-logi` rule applies when the part before `-ogi` has
  positive measure, read literally from FP-02 (N-000158–N-000159).
- **Porter2 (`SnowballStemmer('english')`).** Standard Porter2 (R1/R2, exceptions, Y marking,
  short syllables) written from the algorithm description; the 2.2-release wording is not
  checked against the reference implementation.
- **Lancaster (N-000161).** The spec says "the standard rule table published with it" but does not
  give the table. I reconstructed a subset (about 30 rules, from memory) and assumed the
  acceptability condition "remaining stem of at least two letters with a vowel". Stems will differ
  from the published algorithm on many words.
- **Averaged perceptron (N-000196–N-000203).** Feature templates, word normalisation and the
  sentence-boundary (START/END) context follow the textblob-aptagger / NLTK perceptron design as I
  understand it. Ties are broken by label order. The weights, tag dictionary and classes are read
  from the packaged JSON files, as the spec describes.
- **Russian universal mapping (N-000207).** Implementer's table (`_RUSSIAN_TO_UNIVERSAL` in
  `tag.py`); unknown categories map to `X`.
- **English universal mapping (N-000183, N-000215).** Uses `en-ptb.map`. If the table is missing,
  the call raises `LookupError` (not an unmapped result).
- **Sequential taggers.** Unigram ties: the first-seen tag wins among equal counts (N-000189).
  Regexp rules match at the start of the token (`re.match`).
- **Chunk grammar.** `#` lines are comments; a clause label is any token before `:`. The root label
  is `S` (N-000420). A `{m,n}` quantifier is recognised only directly after an element, so a
  brace that is not a quantifier closes the rule.
- **CFG reader.** `#` lines are comments. Nonterminals are returned as `Nonterminal` objects
  whose `str()` is the name (N-000431). Terminal `''` is a `str` terminal that matches no token
  when parsing (no leaf), and is emitted as an empty-string token when generating.
- **Chart parser.** Exhaustive (memoised over spans). Derivations that cycle back through the same
  (symbol, span) are cut, so cyclic grammars give finitely many trees.
- **Shift-reduce parser.** Reduces greedily in written production order and never backtracks.
  Empty productions and empty terminals are never reduced (this avoids infinite reduction loops).
- **Generator.** Leftmost expansion in written order. `depth` counts nonterminal expansions; at
  depth 0 a nonterminal yields nothing, while terminals are always emitted. `depth=None` is
  unbounded, so use `n` with recursive grammars.
- **Trees.** `Tree` accepts leaves of any type (chunk structures use `(token, tag)` tuples).
  `pformat()` is one line in pre-order (N-000454); `(token/tag)` is shown for pair leaves.
- **Naive Bayes (N-000277–N-000281).** Label priors are maximum likelihood. Feature values use the
  expected-likelihood estimate `(count + 0.5) / (total + 0.5 * bins)`, where `bins` is the number of
  distinct values of that feature in training. Features absent from a featureset are ignored.
  Ties in `classify` go to the first label seen.
- **Decision tree (N-000283–N-000287).** Multi-way splits on a feature's value, with an absent
  feature as its own branch, chosen by information gain (ties: first feature in sorted name order).
  A leaf returns its majority label (ties: first seen). A value with no branch returns the node's
  majority label.
- **Accuracy on empty lists.** `metrics.accuracy` and `classify.accuracy` raise `ValueError` for
  empty input (the spec does not say; the ratio is undefined).
- **Jaccard of two empty sets.** Returns `0.0` (the spec does not say).
- **Edit distance.** Substitution cost is a number (int or float). With `transpositions=True` it is
  the unrestricted Damerau–Levenshtein distance (Lowrance and Wagner).
- **BLEU (N-000302–N-000309).** Weights are used as given (not normalised). Brevity penalty uses the
  closest reference length, ties to the shorter. Without smoothing, any zero clipped count gives
  `0.0`. The optional `smoothing_function` (N-000477, implementer's choice of form) is a callable
  that takes the list of `(clipped, total)` pairs per order and returns the precisions; the
  library's `translate.epsilon_smoothing` is a ready-made one.
- **Named-entity chunker (N-000415, N-000236).** `ne_chunk` raises `LookupError` when the model or
  wordlist is not visible. When both are visible it raises `NotImplementedError`, because the
  model format is not described in the spec.
- **CLI (N-000385–N-000388).** `tokenize` reads UTF-8 from standard input and writes one line per
  input line. Options: `--language/-l` (default `english`), `--delimiter/-d` (default one space),
  `--encoding/-e` (default `utf-8`). Processing stops at the first line that fails: nothing is
  written for that line, a message goes to standard error, and the status is 1. Usage errors exit 2.
- **Errors.** Exception classes are `TypeError` for wrong argument types, `ValueError` for bad
  values, `LookupError` for a missing packaged resource, and `NotImplementedError` for the
  unfinished parts listed below.

## Not done

- Snowball stemmers for the 14 languages other than `english` and `porter` (arabic, danish, dutch,
  finnish, french, german, hungarian, italian, norwegian, portuguese, romanian, russian, spanish,
  swedish). The constructor accepts the names (N-000393) and then raises `NotImplementedError`.
- Porter's original and Martin Porter's extension modes (N-000142–N-000144). Only the default mode.
- ISRI, Cistem and RSLP stemmers (N-000136, N-000138). Named in the interface, not built.
  `ARLSTem` and `ARLSTem2` are importable and raise `NotImplementedError` (N-000389).
- WordNet lemmatizer lookup (N-000135, N-000174–N-000175, N-000396). The visibility check is done.
- Bigram, trigram and affix taggers (N-000177–N-000178). Outside this specification's results.
- Named-entity chunk model (N-000219, N-000415). See above.
- Recursive-descent parser (N-000237). Outside this specification.
- The s-expression tokenizer (N-000028, N-000078). Named as outside this specification.
- `span_tokenize` for the Treebank and tweet tokenizers (not listed in the Interface Contract).
- Non-goals and the outside-the-spec surfaces (N-000068–N-000076, N-000316–N-000319) are not built.
- Verification on Python 3.10–3.12 and 3.14 (only 3.13 was run). The code avoids 3.11+-only syntax
  as far as I know, but this is untested.
- Verification against the published packaged resources (not in this repository).

## Traceability (every checklist id)

Each id in `spec/CHECKLIST.md` is listed below with a status: `implemented` (code and tests in
this repository; see the `# spec:` comments and `tests/`), `partial` (a stated part is missing,
see the note), `not done` (with a reason), or `satisfied` (a descriptive, constraint or
non-goal statement met by the build layout or by not building the excluded feature).
Status is my own assessment, not the spec's; the implementation of the `implemented` rows
against real packaged data is unverified (see the limitation above).

| Id | Pack | Status | Where | Note |
|---|---|---|---|---|
| N-000001 | 16 | satisfied | lingora/cli.py, lingora/tokenize.py, all feature modules | descriptive product statement; library plus a CLI convenience |
| N-000002 | 16 | satisfied | lingora/cli.py, lingora/tokenize.py, all feature modules | descriptive product statement; library plus a CLI convenience |
| N-000003 | 16 | satisfied | lingora/cli.py, lingora/tokenize.py, all feature modules | descriptive product statement; library plus a CLI convenience |
| N-000004 | 16 | satisfied | lingora/cli.py, lingora/tokenize.py, all feature modules | descriptive product statement; library plus a CLI convenience |
| N-000005 | 16 | satisfied | lingora/cli.py, lingora/tokenize.py, all feature modules |  |
| N-000006 | 16 | satisfied | lingora/cli.py, lingora/tokenize.py, all feature modules |  |
| N-000007 | 16 | satisfied | lingora/cli.py, lingora/tokenize.py, all feature modules |  |
| N-000008 | 16 | satisfied | lingora/cli.py, lingora/tokenize.py, all feature modules |  |
| N-000009 | 16 | satisfied | lingora/cli.py, lingora/tokenize.py, all feature modules |  |
| N-000010 | 16 | satisfied | lingora/cli.py, lingora/tokenize.py, all feature modules |  |
| N-000011 | 16 | satisfied | lingora/cli.py, lingora/tokenize.py, all feature modules |  |
| N-000012 | 16 | satisfied | lingora/cli.py, lingora/tokenize.py, all feature modules |  |
| N-000013 | 16 | satisfied | lingora/cli.py, lingora/tokenize.py, all feature modules |  |
| N-000014 | 16 | satisfied | lingora/cli.py, lingora/tokenize.py, all feature modules |  |
| N-000015 | 16 | satisfied | lingora/cli.py, lingora/tokenize.py, all feature modules |  |
| N-000016 | 16 | satisfied | lingora/cli.py, lingora/tokenize.py, all feature modules | decision on feature-point order: the build followed it |
| N-000017 | 16 | satisfied | lingora/cli.py, lingora/tokenize.py, all feature modules | ordering constraint (feature points depend only backwards); the code layout follows it |
| N-000018 | 16 | satisfied | lingora/cli.py, lingora/tokenize.py, all feature modules | packaged corpora, WordNet, data finder and downloader are not built beyond locating packaged models (see lingora/data.py) |
| N-000019 | 16 | satisfied | lingora/cli.py, lingora/tokenize.py, all feature modules | packaged corpora, WordNet, data finder and downloader are not built beyond locating packaged models (see lingora/data.py) |
| N-000020 | 16 | satisfied | lingora/cli.py, lingora/tokenize.py, all feature modules |  |
| N-000021 | 17 | satisfied | lingora/tokenize.py, lingora/tag.py, lingora/chunk.py |  |
| N-000022 | 17 | satisfied | lingora/tokenize.py, lingora/tag.py, lingora/chunk.py |  |
| N-000023 | 17 | satisfied | lingora/tokenize.py, lingora/tag.py, lingora/chunk.py |  |
| N-000024 | 17 | satisfied | lingora/tokenize.py, lingora/tag.py, lingora/chunk.py |  |
| N-000025 | 17 | satisfied | lingora/tokenize.py, lingora/tag.py, lingora/chunk.py |  |
| N-000026 | 18 | implemented | lingora/* (public surface) |  |
| N-000027 | 18 | implemented | lingora/* (public surface) |  |
| N-000028 | 18 | not done | lingora/* (public surface) | the s-expression tokenizer is named as outside this specification (pack 29 / FP-01) |
| N-000029 | 18 | implemented | lingora/* (public surface) |  |
| N-000030 | 18 | implemented | lingora/* (public surface) |  |
| N-000031 | 18 | implemented | lingora/* (public surface) |  |
| N-000032 | 18 | implemented | lingora/* (public surface) |  |
| N-000033 | 18 | implemented | lingora/* (public surface) |  |
| N-000034 | 18 | implemented | lingora/* (public surface) |  |
| N-000035 | 18 | implemented | lingora/* (public surface) |  |
| N-000036 | 18 | implemented | lingora/* (public surface) |  |
| N-000037 | 18 | implemented | lingora/* (public surface) |  |
| N-000038 | 18 | implemented | lingora/* (public surface) |  |
| N-000039 | 18 | implemented | lingora/* (public surface) |  |
| N-000040 | 18 | implemented | lingora/* (public surface) |  |
| N-000041 | 18 | implemented | lingora/* (public surface) |  |
| N-000042 | 18 | implemented | lingora/* (public surface) |  |
| N-000043 | 18 | implemented | lingora/* (public surface) |  |
| N-000044 | 18 | implemented | lingora/* (public surface) |  |
| N-000045 | 19 | implemented | pyproject.toml, lingora/data.py |  |
| N-000046 | 19 | implemented | pyproject.toml, lingora/data.py |  |
| N-000047 | 19 | implemented | pyproject.toml, lingora/data.py |  |
| N-000048 | 19 | implemented | pyproject.toml, lingora/data.py |  |
| N-000049 | 19 | implemented | pyproject.toml, lingora/data.py |  |
| N-000050 | 19 | implemented | pyproject.toml, lingora/data.py |  |
| N-000051 | 19 | implemented | pyproject.toml, lingora/data.py |  |
| N-000052 | 19 | implemented | pyproject.toml, lingora/data.py |  |
| N-000053 | 19 | implemented | pyproject.toml, lingora/data.py |  |
| N-000054 | 19 | implemented | pyproject.toml, lingora/data.py |  |
| N-000055 | 19 | implemented | pyproject.toml, lingora/data.py |  |
| N-000056 | 19 | implemented | pyproject.toml, lingora/data.py |  |
| N-000057 | 19 | implemented | pyproject.toml, lingora/data.py |  |
| N-000058 | 19 | implemented | pyproject.toml, lingora/data.py |  |
| N-000059 | 19 | implemented | pyproject.toml, lingora/data.py |  |
| N-000060 | 19 | implemented | pyproject.toml, lingora/data.py |  |
| N-000061 | 19 | implemented | pyproject.toml, lingora/data.py |  |
| N-000062 | 19 | implemented | pyproject.toml, lingora/data.py |  |
| N-000063 | 19 | implemented | pyproject.toml, lingora/data.py |  |
| N-000064 | 19 | satisfied | pyproject.toml, lingora/data.py | assumption: not a concern of this specification |
| N-000065 | 20 | implemented | lingora/__init__.py |  |
| N-000066 | 20 | implemented | lingora/__init__.py |  |
| N-000067 | 20 | implemented | lingora/__init__.py |  |
| N-000068 | 21 | satisfied | (nothing built) | non-goal; not built |
| N-000069 | 21 | satisfied | (nothing built) | non-goal; not built |
| N-000070 | 21 | satisfied | (nothing built) | non-goal; not built |
| N-000071 | 21 | satisfied | (nothing built) | non-goal; not built |
| N-000072 | 21 | satisfied | (nothing built) | non-goal; not built |
| N-000073 | 21 | satisfied | (nothing built) | non-goal; not built |
| N-000074 | 21 | satisfied | (nothing built) | non-goal; not built |
| N-000075 | 21 | satisfied | (nothing built) | non-goal; not built |
| N-000076 | 21 | satisfied | (nothing built) | non-goal; not built |
| N-000077 | 22 | implemented | lingora/tokenize.py, lingora/_punkt.py |  |
| N-000078 | 22 | not done | lingora/tokenize.py, lingora/_punkt.py | the s-expression tokenizer is named as outside this specification (pack 29 / FP-01) |
| N-000079 | 22 | implemented | lingora/tokenize.py, lingora/_punkt.py |  |
| N-000080 | 22 | implemented | lingora/tokenize.py, lingora/_punkt.py |  |
| N-000081 | 22 | implemented | lingora/tokenize.py, lingora/_punkt.py |  |
| N-000082 | 22 | implemented | lingora/tokenize.py, lingora/_punkt.py |  |
| N-000083 | 22 | implemented | lingora/tokenize.py, lingora/_punkt.py |  |
| N-000084 | 22 | implemented | lingora/tokenize.py, lingora/_punkt.py |  |
| N-000085 | 22 | implemented | lingora/tokenize.py, lingora/_punkt.py |  |
| N-000086 | 22 | implemented | lingora/tokenize.py, lingora/_punkt.py |  |
| N-000087 | 22 | implemented | lingora/tokenize.py, lingora/_punkt.py |  |
| N-000088 | 22 | implemented | lingora/tokenize.py, lingora/_punkt.py |  |
| N-000089 | 22 | implemented | lingora/tokenize.py, lingora/_punkt.py |  |
| N-000090 | 22 | implemented | lingora/tokenize.py, lingora/_punkt.py |  |
| N-000091 | 22 | implemented | lingora/tokenize.py, lingora/_punkt.py |  |
| N-000092 | 22 | implemented | lingora/tokenize.py, lingora/_punkt.py |  |
| N-000093 | 22 | implemented | lingora/tokenize.py, lingora/_punkt.py |  |
| N-000094 | 22 | implemented | lingora/tokenize.py, lingora/_punkt.py |  |
| N-000095 | 22 | implemented | lingora/tokenize.py, lingora/_punkt.py |  |
| N-000096 | 22 | implemented | lingora/tokenize.py, lingora/_punkt.py |  |
| N-000097 | 22 | implemented | lingora/tokenize.py, lingora/_punkt.py |  |
| N-000098 | 22 | implemented | lingora/tokenize.py, lingora/_punkt.py |  |
| N-000099 | 22 | implemented | lingora/tokenize.py, lingora/_punkt.py |  |
| N-000100 | 22 | implemented | lingora/tokenize.py, lingora/_punkt.py |  |
| N-000101 | 22 | implemented | lingora/tokenize.py, lingora/_punkt.py |  |
| N-000102 | 22 | implemented | lingora/tokenize.py, lingora/_punkt.py |  |
| N-000103 | 22 | implemented | lingora/tokenize.py, lingora/_punkt.py |  |
| N-000104 | 22 | implemented | lingora/tokenize.py, lingora/_punkt.py |  |
| N-000105 | 22 | implemented | lingora/tokenize.py, lingora/_punkt.py |  |
| N-000106 | 22 | implemented | lingora/tokenize.py, lingora/_punkt.py |  |
| N-000107 | 22 | implemented | lingora/tokenize.py, lingora/_punkt.py |  |
| N-000108 | 22 | implemented | lingora/tokenize.py, lingora/_punkt.py |  |
| N-000109 | 22 | implemented | lingora/tokenize.py, lingora/_punkt.py |  |
| N-000110 | 22 | implemented | lingora/tokenize.py, lingora/_punkt.py |  |
| N-000111 | 22 | implemented | lingora/tokenize.py, lingora/_punkt.py |  |
| N-000112 | 22 | implemented | lingora/tokenize.py, lingora/_punkt.py |  |
| N-000113 | 22 | implemented | lingora/tokenize.py, lingora/_punkt.py |  |
| N-000114 | 22 | implemented | lingora/tokenize.py, lingora/_punkt.py |  |
| N-000115 | 22 | implemented | lingora/tokenize.py, lingora/_punkt.py |  |
| N-000116 | 22 | implemented | lingora/tokenize.py, lingora/_punkt.py |  |
| N-000117 | 22 | implemented | lingora/tokenize.py, lingora/_punkt.py |  |
| N-000118 | 22 | implemented | lingora/tokenize.py, lingora/_punkt.py |  |
| N-000119 | 22 | implemented | lingora/tokenize.py, lingora/_punkt.py |  |
| N-000120 | 22 | implemented | lingora/tokenize.py, lingora/_punkt.py |  |
| N-000121 | 22 | implemented | lingora/tokenize.py, lingora/_punkt.py |  |
| N-000122 | 22 | implemented | lingora/tokenize.py, lingora/_punkt.py | Punkt-style decision rules written from the Punkt paper and the parameter files; not validated against the published Punkt models (none are in this repository) |
| N-000123 | 22 | implemented | lingora/tokenize.py, lingora/_punkt.py | Punkt-style decision rules written from the Punkt paper and the parameter files; not validated against the published Punkt models (none are in this repository) |
| N-000124 | 22 | implemented | lingora/tokenize.py, lingora/_punkt.py | Punkt-style decision rules written from the Punkt paper and the parameter files; not validated against the published Punkt models (none are in this repository) |
| N-000125 | 22 | implemented | lingora/tokenize.py, lingora/_punkt.py | Punkt-style decision rules written from the Punkt paper and the parameter files; not validated against the published Punkt models (none are in this repository) |
| N-000126 | 22 | implemented | lingora/tokenize.py, lingora/_punkt.py | Punkt-style decision rules written from the Punkt paper and the parameter files; not validated against the published Punkt models (none are in this repository) |
| N-000127 | 22 | implemented | lingora/tokenize.py, lingora/_punkt.py |  |
| N-000128 | 22 | implemented | lingora/tokenize.py, lingora/_punkt.py |  |
| N-000129 | 22 | implemented | lingora/tokenize.py, lingora/_punkt.py |  |
| N-000130 | 22 | implemented | lingora/tokenize.py, lingora/_punkt.py |  |
| N-000131 | 22 | implemented | lingora/tokenize.py, lingora/_punkt.py |  |
| N-000132 | 22 | implemented | lingora/tokenize.py, lingora/_punkt.py |  |
| N-000133 | 23 | implemented | lingora/stem.py |  |
| N-000134 | 23 | implemented | lingora/stem.py |  |
| N-000135 | 23 | partial | lingora/stem.py | WordNet lemmatizer raises LookupError when WordNet is not visible; with WordNet visible it raises NotImplementedError (lookup not built) |
| N-000136 | 23 | partial | lingora/stem.py | ARLSTem and ARLSTem2 are importable and raise NotImplementedError; ISRI, Cistem and RSLP are not built (results outside this specification) |
| N-000137 | 23 | partial | lingora/stem.py | ARLSTem and ARLSTem2 are importable and raise NotImplementedError; ISRI, Cistem and RSLP are not built (results outside this specification) |
| N-000138 | 23 | partial | lingora/stem.py | RSLP not built; WordNet lemmatizer only checks that WordNet is visible (see N-000174) |
| N-000139 | 23 | implemented | lingora/stem.py |  |
| N-000140 | 23 | partial | lingora/stem.py | SnowballStemmer accepts all 16 names, but only english (Porter2) and porter are implemented; the other 14 raise NotImplementedError at construction |
| N-000141 | 23 | partial | lingora/stem.py | SnowballStemmer accepts all 16 names, but only english (Porter2) and porter are implemented; the other 14 raise NotImplementedError at construction |
| N-000142 | 23 | partial | lingora/stem.py | PorterStemmer implements only the default LINGORA-extensions mode; the two other modes are outside this specification and not built |
| N-000143 | 23 | partial | lingora/stem.py | PorterStemmer implements only the default LINGORA-extensions mode; the two other modes are outside this specification and not built |
| N-000144 | 23 | partial | lingora/stem.py | PorterStemmer implements only the default LINGORA-extensions mode; the two other modes are outside this specification and not built |
| N-000145 | 23 | implemented | lingora/stem.py |  |
| N-000146 | 23 | implemented | lingora/stem.py |  |
| N-000147 | 23 | implemented | lingora/stem.py |  |
| N-000148 | 23 | implemented | lingora/stem.py |  |
| N-000149 | 23 | implemented | lingora/stem.py |  |
| N-000150 | 23 | implemented | lingora/stem.py |  |
| N-000151 | 23 | implemented | lingora/stem.py |  |
| N-000152 | 23 | implemented | lingora/stem.py |  |
| N-000153 | 23 | implemented | lingora/stem.py |  |
| N-000154 | 23 | implemented | lingora/stem.py |  |
| N-000155 | 23 | implemented | lingora/stem.py |  |
| N-000156 | 23 | implemented | lingora/stem.py |  |
| N-000157 | 23 | implemented | lingora/stem.py |  |
| N-000158 | 23 | implemented | lingora/stem.py |  |
| N-000159 | 23 | implemented | lingora/stem.py |  |
| N-000160 | 23 | implemented | lingora/stem.py |  |
| N-000161 | 23 | partial | lingora/stem.py | Paice/Husk rule engine implemented, but the rule table is a reconstructed subset (about 30 of the published rules); see NOTES.md |
| N-000162 | 23 | partial | lingora/stem.py | Paice/Husk rule engine implemented, but the rule table is a reconstructed subset (about 30 of the published rules); see NOTES.md |
| N-000163 | 23 | partial | lingora/stem.py | SnowballStemmer accepts all 16 names, but only english (Porter2) and porter are implemented; the other 14 raise NotImplementedError at construction |
| N-000164 | 23 | not done | lingora/stem.py | the Snowball Dutch algorithm is not implemented |
| N-000165 | 23 | implemented | lingora/stem.py |  |
| N-000166 | 23 | implemented | lingora/stem.py |  |
| N-000167 | 23 | implemented | lingora/stem.py |  |
| N-000168 | 23 | implemented | lingora/stem.py |  |
| N-000169 | 23 | implemented | lingora/stem.py |  |
| N-000170 | 23 | implemented | lingora/stem.py |  |
| N-000171 | 23 | implemented | lingora/stem.py |  |
| N-000172 | 23 | implemented | lingora/stem.py |  |
| N-000173 | 23 | implemented | lingora/stem.py |  |
| N-000174 | 23 | partial | lingora/stem.py | WordNet lemmatizer raises LookupError when WordNet is not visible; with WordNet visible it raises NotImplementedError (lookup not built) |
| N-000175 | 23 | partial | lingora/stem.py | WordNet lemmatizer raises LookupError when WordNet is not visible; with WordNet visible it raises NotImplementedError (lookup not built) |
| N-000176 | 24 | implemented | lingora/tag.py |  |
| N-000177 | 24 | partial | lingora/tag.py | default, unigram and regular-expression taggers are implemented; bigram, trigram and affix taggers are not built (their results are outside this specification) |
| N-000178 | 24 | partial | lingora/tag.py | default, unigram and regular-expression taggers are implemented; bigram, trigram and affix taggers are not built (their results are outside this specification) |
| N-000179 | 24 | implemented | lingora/tag.py |  |
| N-000180 | 24 | implemented | lingora/tag.py |  |
| N-000181 | 24 | implemented | lingora/tag.py |  |
| N-000182 | 24 | implemented | lingora/tag.py | English universal mapping needs en-ptb.map; the Russian mapping is an implementer-chosen table (N-000207) |
| N-000183 | 24 | implemented | lingora/tag.py | English universal mapping needs en-ptb.map; the Russian mapping is an implementer-chosen table (N-000207) |
| N-000184 | 24 | implemented | lingora/tag.py |  |
| N-000185 | 24 | implemented | lingora/tag.py |  |
| N-000186 | 24 | implemented | lingora/tag.py |  |
| N-000187 | 24 | implemented | lingora/tag.py |  |
| N-000188 | 24 | implemented | lingora/tag.py |  |
| N-000189 | 24 | implemented | lingora/tag.py |  |
| N-000190 | 24 | implemented | lingora/tag.py |  |
| N-000191 | 24 | implemented | lingora/tag.py |  |
| N-000192 | 24 | implemented | lingora/tag.py |  |
| N-000193 | 24 | implemented | lingora/tag.py |  |
| N-000194 | 24 | implemented | lingora/tag.py |  |
| N-000195 | 24 | implemented | lingora/tag.py |  |
| N-000196 | 24 | implemented | lingora/tag.py | averaged perceptron with textblob-aptagger style features, written from the spec; not validated against the published weights (none are in this repository) |
| N-000197 | 24 | implemented | lingora/tag.py | averaged perceptron with textblob-aptagger style features, written from the spec; not validated against the published weights (none are in this repository) |
| N-000198 | 24 | implemented | lingora/tag.py | averaged perceptron with textblob-aptagger style features, written from the spec; not validated against the published weights (none are in this repository) |
| N-000199 | 24 | implemented | lingora/tag.py | averaged perceptron with textblob-aptagger style features, written from the spec; not validated against the published weights (none are in this repository) |
| N-000200 | 24 | implemented | lingora/tag.py | averaged perceptron with textblob-aptagger style features, written from the spec; not validated against the published weights (none are in this repository) |
| N-000201 | 24 | implemented | lingora/tag.py | averaged perceptron with textblob-aptagger style features, written from the spec; not validated against the published weights (none are in this repository) |
| N-000202 | 24 | implemented | lingora/tag.py |  |
| N-000203 | 24 | implemented | lingora/tag.py |  |
| N-000204 | 24 | implemented | lingora/tag.py |  |
| N-000205 | 24 | implemented | lingora/tag.py |  |
| N-000206 | 24 | implemented | lingora/tag.py |  |
| N-000207 | 24 | implemented | lingora/tag.py |  |
| N-000208 | 24 | implemented | lingora/tag.py |  |
| N-000209 | 24 | implemented | lingora/tag.py |  |
| N-000210 | 24 | implemented | lingora/tag.py |  |
| N-000211 | 24 | implemented | lingora/tag.py |  |
| N-000212 | 24 | implemented | lingora/tag.py |  |
| N-000213 | 24 | implemented | lingora/tag.py |  |
| N-000214 | 24 | implemented | lingora/tag.py |  |
| N-000215 | 24 | implemented | lingora/tag.py | English universal mapping needs en-ptb.map; the Russian mapping is an implementer-chosen table (N-000207) |
| N-000216 | 24 | implemented | lingora/tag.py | English universal mapping needs en-ptb.map; the Russian mapping is an implementer-chosen table (N-000207) |
| N-000217 | 25 | implemented | lingora/chunk.py |  |
| N-000218 | 25 | implemented | lingora/chunk.py |  |
| N-000219 | 25 | partial | lingora/chunk.py | the named-entity chunker checks its model and wordlist and raises LookupError if either is missing; the model itself is not implemented (NotImplementedError) |
| N-000220 | 25 | implemented | lingora/chunk.py |  |
| N-000221 | 25 | implemented | lingora/chunk.py |  |
| N-000222 | 25 | implemented | lingora/chunk.py |  |
| N-000223 | 25 | implemented | lingora/chunk.py | chunk rules apply left to right; earlier-clause chunks are units; see NOTES.md (scope ambiguity) |
| N-000224 | 25 | implemented | lingora/chunk.py | chunk rules apply left to right; earlier-clause chunks are units; see NOTES.md (scope ambiguity) |
| N-000225 | 25 | implemented | lingora/chunk.py | chunk rules apply left to right; earlier-clause chunks are units; see NOTES.md (scope ambiguity) |
| N-000226 | 25 | implemented | lingora/chunk.py | chunk rules apply left to right; earlier-clause chunks are units; see NOTES.md (scope ambiguity) |
| N-000227 | 25 | implemented | lingora/chunk.py | chunk rules apply left to right; earlier-clause chunks are units; see NOTES.md (scope ambiguity) |
| N-000228 | 25 | implemented | lingora/chunk.py | chunk rules apply left to right; earlier-clause chunks are units; see NOTES.md (scope ambiguity) |
| N-000229 | 25 | implemented | lingora/chunk.py | chunk rules apply left to right; earlier-clause chunks are units; see NOTES.md (scope ambiguity) |
| N-000230 | 25 | implemented | lingora/chunk.py | chunk rules apply left to right; earlier-clause chunks are units; see NOTES.md (scope ambiguity) |
| N-000231 | 25 | implemented | lingora/chunk.py | chunk rules apply left to right; earlier-clause chunks are units; see NOTES.md (scope ambiguity) |
| N-000232 | 25 | implemented | lingora/chunk.py | chunk rules apply left to right; earlier-clause chunks are units; see NOTES.md (scope ambiguity) |
| N-000233 | 25 | implemented | lingora/chunk.py | chunk rules apply left to right; earlier-clause chunks are units; see NOTES.md (scope ambiguity) |
| N-000234 | 25 | implemented | lingora/chunk.py |  |
| N-000235 | 25 | implemented | lingora/chunk.py |  |
| N-000236 | 25 | implemented | lingora/chunk.py |  |
| N-000237 | 26 | not done | lingora/grammar.py, lingora/parse/ | the recursive-descent parser is outside this specification (its results are outside it) |
| N-000238 | 26 | implemented | lingora/grammar.py, lingora/parse/ |  |
| N-000239 | 26 | implemented | lingora/grammar.py, lingora/parse/ |  |
| N-000240 | 26 | implemented | lingora/grammar.py, lingora/parse/ |  |
| N-000241 | 26 | implemented | lingora/grammar.py, lingora/parse/ |  |
| N-000242 | 26 | implemented | lingora/grammar.py, lingora/parse/ |  |
| N-000243 | 26 | implemented | lingora/grammar.py, lingora/parse/ |  |
| N-000244 | 26 | implemented | lingora/grammar.py, lingora/parse/ |  |
| N-000245 | 26 | implemented | lingora/grammar.py, lingora/parse/ |  |
| N-000246 | 26 | implemented | lingora/grammar.py, lingora/parse/ |  |
| N-000247 | 26 | implemented | lingora/grammar.py, lingora/parse/ |  |
| N-000248 | 26 | implemented | lingora/grammar.py, lingora/parse/ |  |
| N-000249 | 26 | implemented | lingora/grammar.py, lingora/parse/ |  |
| N-000250 | 26 | implemented | lingora/grammar.py, lingora/parse/ |  |
| N-000251 | 26 | implemented | lingora/grammar.py, lingora/parse/ |  |
| N-000252 | 26 | implemented | lingora/grammar.py, lingora/parse/ |  |
| N-000253 | 26 | implemented | lingora/grammar.py, lingora/parse/ |  |
| N-000254 | 26 | implemented | lingora/grammar.py, lingora/parse/ |  |
| N-000255 | 26 | implemented | lingora/grammar.py, lingora/parse/ |  |
| N-000256 | 26 | implemented | lingora/grammar.py, lingora/parse/ |  |
| N-000257 | 26 | implemented | lingora/grammar.py, lingora/parse/ |  |
| N-000258 | 26 | implemented | lingora/grammar.py, lingora/parse/ |  |
| N-000259 | 26 | implemented | lingora/grammar.py, lingora/parse/ |  |
| N-000260 | 26 | implemented | lingora/grammar.py, lingora/parse/ |  |
| N-000261 | 26 | implemented | lingora/grammar.py, lingora/parse/ |  |
| N-000262 | 26 | implemented | lingora/grammar.py, lingora/parse/ |  |
| N-000263 | 26 | implemented | lingora/grammar.py, lingora/parse/ |  |
| N-000264 | 26 | implemented | lingora/grammar.py, lingora/parse/ |  |
| N-000265 | 26 | implemented | lingora/grammar.py, lingora/parse/ |  |
| N-000266 | 26 | implemented | lingora/grammar.py, lingora/parse/ | failure raised at call for uncovered tokens; empty iterator otherwise |
| N-000267 | 26 | implemented | lingora/grammar.py, lingora/parse/ | failure raised at call for uncovered tokens; empty iterator otherwise |
| N-000268 | 26 | implemented | lingora/grammar.py, lingora/parse/ | failure raised at call for uncovered tokens; empty iterator otherwise |
| N-000269 | 27 | implemented | lingora/classify.py |  |
| N-000270 | 27 | implemented | lingora/classify.py |  |
| N-000271 | 27 | implemented | lingora/classify.py |  |
| N-000272 | 27 | implemented | lingora/classify.py |  |
| N-000273 | 27 | implemented | lingora/classify.py |  |
| N-000274 | 27 | implemented | lingora/classify.py |  |
| N-000275 | 27 | implemented | lingora/classify.py |  |
| N-000276 | 27 | implemented | lingora/classify.py |  |
| N-000277 | 27 | implemented | lingora/classify.py |  |
| N-000278 | 27 | implemented | lingora/classify.py |  |
| N-000279 | 27 | implemented | lingora/classify.py |  |
| N-000280 | 27 | implemented | lingora/classify.py |  |
| N-000281 | 27 | implemented | lingora/classify.py |  |
| N-000282 | 27 | implemented | lingora/classify.py |  |
| N-000283 | 27 | implemented | lingora/classify.py |  |
| N-000284 | 27 | implemented | lingora/classify.py |  |
| N-000285 | 27 | implemented | lingora/classify.py |  |
| N-000286 | 27 | implemented | lingora/classify.py |  |
| N-000287 | 27 | implemented | lingora/classify.py |  |
| N-000288 | 27 | implemented | lingora/classify.py |  |
| N-000289 | 28 | implemented | lingora/metrics.py, lingora/translate.py |  |
| N-000290 | 28 | implemented | lingora/metrics.py, lingora/translate.py |  |
| N-000291 | 28 | implemented | lingora/metrics.py, lingora/translate.py |  |
| N-000292 | 28 | implemented | lingora/metrics.py, lingora/translate.py |  |
| N-000293 | 28 | implemented | lingora/metrics.py, lingora/translate.py |  |
| N-000294 | 28 | implemented | lingora/metrics.py, lingora/translate.py |  |
| N-000295 | 28 | implemented | lingora/metrics.py, lingora/translate.py |  |
| N-000296 | 28 | implemented | lingora/metrics.py, lingora/translate.py |  |
| N-000297 | 28 | implemented | lingora/metrics.py, lingora/translate.py | transpositions use the unrestricted Damerau-Levenshtein algorithm |
| N-000298 | 28 | implemented | lingora/metrics.py, lingora/translate.py |  |
| N-000299 | 28 | implemented | lingora/metrics.py, lingora/translate.py |  |
| N-000300 | 28 | implemented | lingora/metrics.py, lingora/translate.py |  |
| N-000301 | 28 | implemented | lingora/metrics.py, lingora/translate.py |  |
| N-000302 | 28 | implemented | lingora/metrics.py, lingora/translate.py |  |
| N-000303 | 28 | implemented | lingora/metrics.py, lingora/translate.py |  |
| N-000304 | 28 | implemented | lingora/metrics.py, lingora/translate.py |  |
| N-000305 | 28 | implemented | lingora/metrics.py, lingora/translate.py |  |
| N-000306 | 28 | implemented | lingora/metrics.py, lingora/translate.py |  |
| N-000307 | 28 | implemented | lingora/metrics.py, lingora/translate.py |  |
| N-000308 | 28 | implemented | lingora/metrics.py, lingora/translate.py |  |
| N-000309 | 28 | implemented | lingora/metrics.py, lingora/translate.py | no smoothing: a zero order gives 0.0; with a smoothing function the caller decides |
| N-000310 | 28 | implemented | lingora/metrics.py, lingora/translate.py |  |
| N-000311 | 28 | implemented | lingora/metrics.py, lingora/translate.py |  |
| N-000312 | 28 | implemented | lingora/metrics.py, lingora/translate.py |  |
| N-000313 | 28 | implemented | lingora/metrics.py, lingora/translate.py |  |
| N-000314 | 28 | implemented | lingora/metrics.py, lingora/translate.py |  |
| N-000315 | 28 | implemented | lingora/metrics.py, lingora/translate.py |  |
| N-000316 | 29 | satisfied | (nothing built) | outside this specification; not built |
| N-000317 | 29 | satisfied | (nothing built) | outside this specification; not built |
| N-000318 | 29 | satisfied | (nothing built) | outside this specification; not built |
| N-000319 | 29 | satisfied | (nothing built) | outside this specification; not built |
| N-000320 | 02 | satisfied | pyproject.toml; no compiled code | hardware and packaging: pure Python, flat layout, no downloads at import (tested on Python 3.13 only; see NOTES.md) |
| N-000321 | 02 | satisfied | pyproject.toml; no compiled code | hardware and packaging: pure Python, flat layout, no downloads at import (tested on Python 3.13 only; see NOTES.md) |
| N-000322 | 02 | satisfied | pyproject.toml; no compiled code | hardware and packaging: pure Python, flat layout, no downloads at import (tested on Python 3.13 only; see NOTES.md) |
| N-000323 | 02 | satisfied | pyproject.toml; no compiled code | hardware and packaging: pure Python, flat layout, no downloads at import (tested on Python 3.13 only; see NOTES.md) |
| N-000324 | 03 | satisfied | pyproject.toml; lingora/data.py | hardware and packaging: pure Python, flat layout, no downloads at import (tested on Python 3.13 only; see NOTES.md) |
| N-000325 | 03 | satisfied | pyproject.toml; lingora/data.py | hardware and packaging: pure Python, flat layout, no downloads at import (tested on Python 3.13 only; see NOTES.md) |
| N-000326 | 03 | satisfied | pyproject.toml; lingora/data.py | hardware and packaging: pure Python, flat layout, no downloads at import (tested on Python 3.13 only; see NOTES.md) |
| N-000327 | 03 | satisfied | pyproject.toml; lingora/data.py | hardware and packaging: pure Python, flat layout, no downloads at import (tested on Python 3.13 only; see NOTES.md) |
| N-000328 | 03 | satisfied | pyproject.toml; lingora/data.py | hardware and packaging: pure Python, flat layout, no downloads at import (tested on Python 3.13 only; see NOTES.md) |
| N-000329 | 03 | satisfied | pyproject.toml; lingora/data.py | hardware and packaging: pure Python, flat layout, no downloads at import (tested on Python 3.13 only; see NOTES.md) |
| N-000330 | 03 | satisfied | pyproject.toml; lingora/data.py | hardware and packaging: pure Python, flat layout, no downloads at import (tested on Python 3.13 only; see NOTES.md) |
| N-000331 | 03 | satisfied | pyproject.toml; lingora/data.py | hardware and packaging: pure Python, flat layout, no downloads at import (tested on Python 3.13 only; see NOTES.md) |
| N-000332 | 03 | satisfied | pyproject.toml; lingora/data.py | hardware and packaging: pure Python, flat layout, no downloads at import (tested on Python 3.13 only; see NOTES.md) |
| N-000333 | 03 | satisfied | pyproject.toml; lingora/data.py | hardware and packaging: pure Python, flat layout, no downloads at import (tested on Python 3.13 only; see NOTES.md) |
| N-000334 | 03 | satisfied | pyproject.toml; lingora/data.py | hardware and packaging: pure Python, flat layout, no downloads at import (tested on Python 3.13 only; see NOTES.md) |
| N-000335 | 03 | satisfied | pyproject.toml; lingora/data.py | hardware and packaging: pure Python, flat layout, no downloads at import (tested on Python 3.13 only; see NOTES.md) |
| N-000336 | 03 | satisfied | pyproject.toml; lingora/data.py | hardware and packaging: pure Python, flat layout, no downloads at import (tested on Python 3.13 only; see NOTES.md) |
| N-000337 | 03 | satisfied | pyproject.toml; lingora/data.py | hardware and packaging: pure Python, flat layout, no downloads at import (tested on Python 3.13 only; see NOTES.md) |
| N-000338 | 05 | implemented | lingora/* |  |
| N-000339 | 05 | implemented | lingora/* |  |
| N-000340 | 05 | implemented | lingora/* |  |
| N-000341 | 05 | implemented | lingora/* |  |
| N-000342 | 05 | implemented | lingora/* |  |
| N-000343 | 05 | implemented | lingora/* |  |
| N-000344 | 05 | implemented | lingora/* |  |
| N-000345 | 05 | implemented | lingora/* |  |
| N-000346 | 05 | implemented | lingora/* |  |
| N-000347 | 05 | implemented | lingora/* |  |
| N-000348 | 05 | implemented | lingora/* |  |
| N-000349 | 05 | implemented | lingora/* |  |
| N-000350 | 05 | implemented | lingora/* |  |
| N-000351 | 05 | implemented | lingora/* |  |
| N-000352 | 05 | implemented | lingora/* |  |
| N-000353 | 06 | implemented | lingora/data.py, lingora/_punkt.py, lingora/tag.py |  |
| N-000354 | 06 | implemented | lingora/data.py, lingora/_punkt.py, lingora/tag.py |  |
| N-000355 | 06 | implemented | lingora/data.py, lingora/_punkt.py, lingora/tag.py |  |
| N-000356 | 06 | implemented | lingora/data.py, lingora/_punkt.py, lingora/tag.py |  |
| N-000357 | 06 | implemented | lingora/data.py, lingora/_punkt.py, lingora/tag.py |  |
| N-000358 | 06 | implemented | lingora/data.py, lingora/_punkt.py, lingora/tag.py |  |
| N-000359 | 06 | implemented | lingora/data.py, lingora/_punkt.py, lingora/tag.py |  |
| N-000360 | 06 | implemented | lingora/data.py, lingora/_punkt.py, lingora/tag.py |  |
| N-000361 | 06 | implemented | lingora/data.py, lingora/_punkt.py, lingora/tag.py |  |
| N-000362 | 06 | implemented | lingora/data.py, lingora/_punkt.py, lingora/tag.py |  |
| N-000363 | 06 | implemented | lingora/data.py, lingora/_punkt.py, lingora/tag.py |  |
| N-000364 | 06 | implemented | lingora/data.py, lingora/_punkt.py, lingora/tag.py |  |
| N-000365 | 06 | implemented | lingora/data.py, lingora/_punkt.py, lingora/tag.py |  |
| N-000366 | 06 | implemented | lingora/data.py, lingora/_punkt.py, lingora/tag.py |  |
| N-000367 | 06 | implemented | lingora/data.py, lingora/_punkt.py, lingora/tag.py |  |
| N-000368 | 06 | implemented | lingora/data.py, lingora/_punkt.py, lingora/tag.py |  |
| N-000369 | 06 | implemented | lingora/data.py, lingora/_punkt.py, lingora/tag.py |  |
| N-000370 | 06 | implemented | lingora/data.py, lingora/_punkt.py, lingora/tag.py |  |
| N-000371 | 07 | implemented | lingora/tokenize.py |  |
| N-000372 | 07 | implemented | lingora/tokenize.py |  |
| N-000373 | 07 | implemented | lingora/tokenize.py |  |
| N-000374 | 07 | implemented | lingora/tokenize.py |  |
| N-000375 | 07 | implemented | lingora/tokenize.py |  |
| N-000376 | 07 | implemented | lingora/tokenize.py |  |
| N-000377 | 07 | implemented | lingora/tokenize.py |  |
| N-000378 | 07 | implemented | lingora/tokenize.py |  |
| N-000379 | 07 | implemented | lingora/tokenize.py |  |
| N-000380 | 07 | implemented | lingora/tokenize.py |  |
| N-000381 | 07 | implemented | lingora/tokenize.py |  |
| N-000382 | 08 | implemented | lingora/cli.py, lingora/__main__.py |  |
| N-000383 | 08 | implemented | lingora/cli.py, lingora/__main__.py |  |
| N-000384 | 08 | implemented | lingora/cli.py, lingora/__main__.py |  |
| N-000385 | 08 | implemented | lingora/cli.py, lingora/__main__.py | exit status 1 on failure, 2 for usage errors; options --language/--delimiter/--encoding |
| N-000386 | 08 | implemented | lingora/cli.py, lingora/__main__.py | exit status 1 on failure, 2 for usage errors; options --language/--delimiter/--encoding |
| N-000387 | 08 | implemented | lingora/cli.py, lingora/__main__.py | exit status 1 on failure, 2 for usage errors; options --language/--delimiter/--encoding |
| N-000388 | 08 | implemented | lingora/cli.py, lingora/__main__.py | exit status 1 on failure, 2 for usage errors; options --language/--delimiter/--encoding |
| N-000389 | 09 | partial | lingora/stem.py | the interface names ARLSTem and ARLSTem2 and they are importable; their stemming is not implemented |
| N-000390 | 09 | implemented | lingora/stem.py |  |
| N-000391 | 09 | implemented | lingora/stem.py |  |
| N-000392 | 09 | implemented | lingora/stem.py |  |
| N-000393 | 09 | partial | lingora/stem.py | SnowballStemmer accepts all 16 names, but only english (Porter2) and porter are implemented; the other 14 raise NotImplementedError at construction |
| N-000394 | 09 | implemented | lingora/stem.py |  |
| N-000395 | 09 | implemented | lingora/stem.py |  |
| N-000396 | 09 | partial | lingora/stem.py | WordNet lemmatizer raises LookupError when WordNet is not visible; with WordNet visible it raises NotImplementedError (lookup not built) |
| N-000397 | 10 | implemented | lingora/tag.py |  |
| N-000398 | 10 | implemented | lingora/tag.py |  |
| N-000399 | 10 | implemented | lingora/tag.py |  |
| N-000400 | 10 | implemented | lingora/tag.py |  |
| N-000401 | 10 | implemented | lingora/tag.py |  |
| N-000402 | 10 | implemented | lingora/tag.py |  |
| N-000403 | 10 | implemented | lingora/tag.py |  |
| N-000404 | 10 | implemented | lingora/tag.py |  |
| N-000405 | 10 | implemented | lingora/tag.py |  |
| N-000406 | 10 | implemented | lingora/tag.py |  |
| N-000407 | 10 | implemented | lingora/tag.py |  |
| N-000408 | 10 | implemented | lingora/tag.py |  |
| N-000409 | 10 | implemented | lingora/tag.py |  |
| N-000410 | 11 | implemented | lingora/chunk.py |  |
| N-000411 | 11 | implemented | lingora/chunk.py |  |
| N-000412 | 11 | implemented | lingora/chunk.py |  |
| N-000413 | 11 | implemented | lingora/chunk.py |  |
| N-000414 | 11 | implemented | lingora/chunk.py | a grammar may be a list of grammar strings applied as sequential stages |
| N-000415 | 11 | partial | lingora/chunk.py | the named-entity chunker checks its model and wordlist and raises LookupError if either is missing; the model itself is not implemented (NotImplementedError) |
| N-000416 | 11 | implemented | lingora/chunk.py |  |
| N-000417 | 11 | implemented | lingora/chunk.py |  |
| N-000418 | 11 | implemented | lingora/chunk.py |  |
| N-000419 | 11 | implemented | lingora/chunk.py |  |
| N-000420 | 11 | implemented | lingora/chunk.py | decision recorded in NOTES.md |
| N-000421 | 11 | implemented | lingora/chunk.py |  |
| N-000422 | 11 | implemented | lingora/chunk.py |  |
| N-000423 | 11 | implemented | lingora/chunk.py |  |
| N-000424 | 12 | implemented | lingora/grammar.py, lingora/parse/__init__.py, lingora/parse/generate.py |  |
| N-000425 | 12 | implemented | lingora/grammar.py, lingora/parse/__init__.py, lingora/parse/generate.py |  |
| N-000426 | 12 | implemented | lingora/grammar.py, lingora/parse/__init__.py, lingora/parse/generate.py |  |
| N-000427 | 12 | implemented | lingora/grammar.py, lingora/parse/__init__.py, lingora/parse/generate.py |  |
| N-000428 | 12 | implemented | lingora/grammar.py, lingora/parse/__init__.py, lingora/parse/generate.py |  |
| N-000429 | 12 | implemented | lingora/grammar.py, lingora/parse/__init__.py, lingora/parse/generate.py |  |
| N-000430 | 12 | implemented | lingora/grammar.py, lingora/parse/__init__.py, lingora/parse/generate.py |  |
| N-000431 | 12 | implemented | lingora/grammar.py, lingora/parse/__init__.py, lingora/parse/generate.py | decision recorded in NOTES.md |
| N-000432 | 12 | implemented | lingora/grammar.py, lingora/parse/__init__.py, lingora/parse/generate.py |  |
| N-000433 | 12 | implemented | lingora/grammar.py, lingora/parse/__init__.py, lingora/parse/generate.py |  |
| N-000434 | 12 | implemented | lingora/grammar.py, lingora/parse/__init__.py, lingora/parse/generate.py |  |
| N-000435 | 12 | implemented | lingora/grammar.py, lingora/parse/__init__.py, lingora/parse/generate.py |  |
| N-000436 | 12 | implemented | lingora/grammar.py, lingora/parse/__init__.py, lingora/parse/generate.py |  |
| N-000437 | 12 | implemented | lingora/grammar.py, lingora/parse/__init__.py, lingora/parse/generate.py |  |
| N-000438 | 12 | implemented | lingora/grammar.py, lingora/parse/__init__.py, lingora/parse/generate.py |  |
| N-000439 | 12 | implemented | lingora/grammar.py, lingora/parse/__init__.py, lingora/parse/generate.py |  |
| N-000440 | 12 | implemented | lingora/grammar.py, lingora/parse/__init__.py, lingora/parse/generate.py |  |
| N-000441 | 12 | implemented | lingora/grammar.py, lingora/parse/__init__.py, lingora/parse/generate.py |  |
| N-000442 | 12 | implemented | lingora/grammar.py, lingora/parse/__init__.py, lingora/parse/generate.py |  |
| N-000443 | 12 | implemented | lingora/grammar.py, lingora/parse/__init__.py, lingora/parse/generate.py |  |
| N-000444 | 13 | implemented | lingora/tree.py |  |
| N-000445 | 13 | implemented | lingora/tree.py |  |
| N-000446 | 13 | implemented | lingora/tree.py |  |
| N-000447 | 13 | implemented | lingora/tree.py |  |
| N-000448 | 13 | implemented | lingora/tree.py |  |
| N-000449 | 13 | implemented | lingora/tree.py |  |
| N-000450 | 13 | implemented | lingora/tree.py |  |
| N-000451 | 13 | implemented | lingora/tree.py |  |
| N-000452 | 13 | implemented | lingora/tree.py |  |
| N-000453 | 13 | implemented | lingora/tree.py |  |
| N-000454 | 13 | implemented | lingora/tree.py | decision recorded in NOTES.md |
| N-000455 | 14 | implemented | lingora/classify.py |  |
| N-000456 | 14 | implemented | lingora/classify.py |  |
| N-000457 | 14 | implemented | lingora/classify.py |  |
| N-000458 | 14 | implemented | lingora/classify.py |  |
| N-000459 | 14 | implemented | lingora/classify.py |  |
| N-000460 | 14 | implemented | lingora/classify.py |  |
| N-000461 | 15 | implemented | lingora/metrics.py, lingora/translate.py |  |
| N-000462 | 15 | implemented | lingora/metrics.py, lingora/translate.py |  |
| N-000463 | 15 | implemented | lingora/metrics.py, lingora/translate.py |  |
| N-000464 | 15 | implemented | lingora/metrics.py, lingora/translate.py |  |
| N-000465 | 15 | implemented | lingora/metrics.py, lingora/translate.py |  |
| N-000466 | 15 | implemented | lingora/metrics.py, lingora/translate.py |  |
| N-000467 | 15 | implemented | lingora/metrics.py, lingora/translate.py |  |
| N-000468 | 15 | implemented | lingora/metrics.py, lingora/translate.py |  |
| N-000469 | 15 | implemented | lingora/metrics.py, lingora/translate.py |  |
| N-000470 | 15 | implemented | lingora/metrics.py, lingora/translate.py |  |
| N-000471 | 15 | implemented | lingora/metrics.py, lingora/translate.py |  |
| N-000472 | 15 | implemented | lingora/metrics.py, lingora/translate.py |  |
| N-000473 | 15 | implemented | lingora/metrics.py, lingora/translate.py |  |
| N-000474 | 15 | implemented | lingora/metrics.py, lingora/translate.py |  |
| N-000475 | 15 | implemented | lingora/metrics.py, lingora/translate.py |  |
| N-000476 | 15 | implemented | lingora/metrics.py, lingora/translate.py |  |
| N-000477 | 15 | implemented | lingora/metrics.py, lingora/translate.py | decision recorded in NOTES.md |
