# NOTES

Build of the LINGORA library (`lingora`) from `spec/`. Pure Python 3.10+, flat layout,
no build step (import from `/app`). Tests: `python3 -m pytest -q tests` (56 passing).

Layout: `lingora/` (package), `lingora/parse/` (parsers and generator), `tests/`
(synthetic packaged-resource fixtures in `tests/conftest.py`, which the sentence
tokenizer, taggers and stemmers need). `pyproject.toml` describes the distribution.
`# spec: N-xxxxxx` markers sit beside the code that satisfies each checklist id.

## Spec disagreements and what was built

Where two parts of the spec disagree, the decision below wins. "UNSETTLED" marks
contradictions the export flagged (`spec/MAP.md`, 13 ids). Unflagged ones are listed
too. The rule used: the Interface Contract governs signatures and refusals; the PRD
governs default *behaviour* (the Interface says the PRD states defaults "wherever it
matters").

1. **Start-of-text straight double quote** (UNSETTLED CF-000001). Pack 22 (FP-01):
   N-000094 "A straight double quote at the start of the text … becomes the
   opening-quote token" vs N-000106 "A straight double quote at the very start of the
   text becomes the closing-quote token" (recommended word tokenizer).
   Built: Penn Treebank tokenizer gives `` ; recommended tokenizer gives ''.
2. **Accuracy on lists of different lengths** (UNSETTLED CF-000008, CF-000039,
   CF-000072). Pack 28 N-000331 "it is that fraction over the positions both lists
   have" vs N-000343 (FP-07 boundary), pack 27 N-000318 (FP-06), pack 15 N-000502
   (interface) "Lists of different lengths make it raise." Three say refuse.
   Built: `metrics.accuracy` raises `ValueError`; the fraction-over-shared-positions
   rule is not built.
3. **Edit-distance transpositions** (UNSETTLED CF-000016, CF-000055, CF-000070). Pack 28
   N-000325 "unrestricted Damerau–Levenshtein distance" and N-000327 "characters may
   also be inserted between … the two transposed characters" vs pack 15 N-000505
   "only two characters that stand next to each other in both strings may be
   transposed" and N-000506 "nothing may be inserted or deleted between them".
   Built: optimal-string-alignment rule (the interface's). `edit_distance('ca','abc',
   transpositions=True) == 3`.
4. **Touching chunks** (UNSETTLED CF-000028). Pack 25 N-000240 "Two matches that touch
   are two separate chunks" vs N-000242 "Chunks that touch, with no token between them,
   are joined into one chunk." Built: separate chunks; no joining.
5. **F-measure with no common element** (UNSETTLED CF-000038). Pack 28 N-000334 "It is
   0 when precision or recall is 0" vs N-000346 "the two sets share no element return
   no number." Built: `None` for empty sets or disjoint sets (where precision is 0
   too), so the "0" branch is effectively unreachable.
6. **Tweet tokenizer emoticon case** (UNSETTLED CF-000054). Pack 19 N-000067 "lowercases
   its tokens" vs pack 22 N-000125 "tokens are lowercased, except emoticons." Built:
   emoticons keep their case.
7. **Porter 1a `-ies`** (UNSETTLED CF-000073). Pack 23 N-000158 (`-ies`→`-ie` for
   four-letter words) vs pack 09 N-000424 "`PorterStemmer` applies Step 1a as
   published, so *ties* stems to *ti*." Built: the default mode is the LINGORA
   extensions, so `ties` → `tie` (FP-02 defines the default mode).
8. **Empty-discarding default** (UNSETTLED CF-000077). Pack 22 N-000118 "it is on by
   default" vs pack 07 N-000407 "`discard_empty` is off unless the caller passes
   `discard_empty=True`." Built: on by default (PRD behaviour).
9. **`cannot`** (UNSETTLED CF-000083). Pack 22 N-000102 (fused `cannot` split into
   *can* + *not*) vs N-000110 (recommended tokenizer keeps *cannot* whole). Built:
   Penn Treebank splits it; the recommended tokenizer keeps it.
10. **Porter `to_lowercase` default** (not flagged). Pack 23 N-000154 "lowercased first,
    unless the caller turns lowercasing off" vs pack 09 N-000427 "`to_lowercase`
    defaults to `False`, so `stem` keeps the letter case." Built: default True (PRD).
11. **BLEU default weights** (not flagged). Pack 28 N-000337/338 "default is equal
    weights on unigrams through 4-grams" vs pack 15 N-000513–515 "when `weights` is
    omitted, unigrams and bigrams are weighted equally." Built: 4-grams (PRD).
    `bleu(..., smoothing_function=…)` is a callable `(matches, totals) -> precisions`.
12. **Empty-string terminal in generation** (not flagged). Pack 26 N-000280 "A quoted
    empty string contributes an empty-string token" vs pack 12 N-000480 "A terminal
    that is the empty string adds no token to a sentence." Built: no token (interface).
    The chart parser likewise adds no leaf for `''`.
13. **Tree children given as a string** (not flagged). Pack 26 N-000281–284 "A string
    given in place of the child list is taken as a single leaf" vs pack 13 N-000486–488
    "A `str` given as `children` … makes `Tree` raise." Built: raises `TypeError`.
14. **Cascading chunk clauses** (not flagged). Pack 25 N-000232–249: "A later clause
    sees every chunk built by an earlier clause as a single unit whose tag is that
    chunk's label" versus "chunk the remaining tokens". Built: an earlier chunk is a
    unit matched by its label (so `VP: {<NP><VBD>}` works); its interior can't be
    chinked by later clauses.
15. **Sentence-tokenizer parameters** (not a conflict, decided). Punkt `ortho_context`
    heuristic and `ne_chunk` results are not fully specified. Built per the
    Kiss–Strunk heuristics (see `tokenize.PunktSentenceTokenizer._ortho_heuristic`).

## Implementation choices and limitations

- **Packaged resources.** `lingora.data.path` starts as the entries of `LINGORA_DATA`
  (empty otherwise). Nothing is downloaded. Tests supply a synthetic model directory.
  The Punkt parameters, perceptron tagger, universal map, stopwords and WordNet index
  are read in the shapes given in pack 06.
- **Porter stemmer.** The three modes exist. Default `NLTK_EXTENSIONS` has the
  LINGORA extensions. Mode results beyond the default are approximate.
- **Lancaster.** The rule table is a partial reconstruction of the published table
  (about 100 rules, not the full published list). Results on common words are right;
  rare suffixes may not be.
- **Snowball.** Implemented: `english` (Porter2, full algorithm) and `porter`
  (original Porter). Not implemented: arabic, danish, dutch, finnish, french, german,
  hungarian, italian, norwegian, portuguese, romanian, russian, spanish, swedish.
  They construct (name validated, stopword list checked) but `stem` raises
  `NotImplementedError`.
- **Taggers.** Default, unigram, regexp, bigram, trigram and affix taggers, with
  backoff. The recommended perceptron tagger (textblob-aptagger features and
  normalisation) reads the packaged weights, tagdict and classes JSON. Russian
  universal mapping is by the part before `=` with a table of my own.
- **ne_chunk.** Requires the NE model directory and `corpora/words` (raises if absent).
  The maximum-entropy model itself is not loaded (its format is not in the spec);
  the result groups runs of `NNP`/`NNPS` into `NE` chunks.
- **WordNet lemmatizer.** Requires `corpora/wordnet`. Lemma candidates come from the
  index files and simple morphological suffix rules; it is not the full WordNet
  morphy.
- **Naive Bayes** uses additive 0.5 smoothing over labels and feature values.
  **Decision tree** grows a full tree and chooses each split by the number of
  examples its per-value majority labels get right.
- **CLI.** `cli.main(args=[...], standalone_mode=True)`; `tokenize` reads stdin and
  writes one line per input line. Exit codes: 0 success, 1 failed tokenization (no token
  line for the failing input), 2 usage error. Options: `--language`, `--delimiter`,
  `--encoding`. `python -m lingora tokenize` also works.
- **Packaging.** `pyproject.toml` declares `lingora` (no dependencies), with the
  `lingora` and `lingora.parse` packages.

## Not done (checklist ids with a reason)

- N-000068 — threading and process model: "Not a concern of this specification."
- N-000072 to N-000080 — non-goals (general regex engine, corpora in the tree, GUI demos,
  chat/Twitter helpers, external-binary wrappers, CCG/DRT/inference, n-gram models,
  throughput). They are exclusions; nothing was built for them.
- N-000143 to N-000146 — ISRI, Cistem, RSLP and the other stemmer families named in
  FP-02 are not implemented. `ARLSTem` and `ARLSTem2` are importable stubs that raise
  `NotImplementedError`.
- N-000172 and N-000173 — "Snowball algorithm for that language, as published in 2.2"
  (including the Dutch rule): only `english` and `porter` are implemented; the other
  languages are listed under Implementation choices.
- N-000261 — recursive-descent parser: "exists; its results are outside this
  specification." Not implemented.
- N-000349 to N-000352 — the "outside this specification" block (corpora, WordNet data
  finder and downloader, graphical tools, external wrappers). Not implemented.
- N-000231 / N-000257 — the packaged named-entity model is not loaded; `ne_chunk` uses a
  proper-noun stand-in (see above).

Every other id in `CHECKLIST.md` is marked in code (`# spec: N-xxxxxx`) beside the code
that satisfies it. Most of the behaviour is exercised by `tests/`; the approximations
listed above are not fully tested against the published data.
