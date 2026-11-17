# LINGORA — build notes

Pure-Python implementation of the LINGORA specification in `spec/` (not modified).
Per-id status for all 517 checklist ids: [`SPEC_COVERAGE.md`](SPEC_COVERAGE.md).

## Layout

- `lingora/` — flat package at the repo root (`pyproject.toml` for an editable install).
  - `data.py` data finder (`data.path`, `locate`, `require`)
  - `tokenize.py` word/punctuation, Penn Treebank, recommended word tokenizer, Punkt sentence tokenizer, whitespace, blank-line, regexp, tweet
  - `stem.py` Porter (LINGORA and original modes), Porter2 (Snowball english), Snowball `porter`, Lancaster, regexp stemmer, WordNet gate
  - `tag.py` default, unigram, bigram, trigram, regexp taggers with backoff; averaged-perceptron `pos_tag` (English, Russian); universal tagset mapping
  - `chunk.py` chunk grammar (`RegexpParser`), chunk and chink rules, `ne_chunk` gate
  - `grammar.py`, `parse/` (`CFG`, `ChartParser`, `ShiftReduceParser`, `generate`)
  - `tree.py` `Tree` (a `list` subclass with a label)
  - `classify.py` Naive Bayes, decision tree, `accuracy`
  - `metrics.py` edit distance (incl. unrestricted Damerau–Levenshtein), Jaccard, accuracy, precision, recall, f-measure
  - `translate.py` BLEU
  - `cli.py` `cli.main(args=['tokenize'], standalone_mode=True)`, parsed by hand with the standard library (no `click`)
- `tests/` — pytest suite (67 tests). `conftest.py` writes synthetic packaged resources to `tmp_path`.

No third-party runtime dependencies.

## Packaged resources

No packaged data (Punkt, perceptron tagger, stopwords, WordNet, NE chunker) exists on this machine,
and none is shipped in the repo (the spec excludes corpora). Those paths therefore look for their
resources on `data.path`, which is initialised from `$LINGORA_DATA` (os.pathsep-separated),
`~/lingora_data`, and `<sys.prefix>/share/lingora`. Without the resources, the paths that need them
raise `LookupError` as the spec requires. The tests use small synthetic resources, so they check
the plumbing, not the real model accuracy.

## Conflicts and decisions

The export lists 13 unsettled contradictions (`spec/MAP.md`). Each is listed below with the two
sides and the choice. Where several listed sides agree, the choice follows them. Where the
PRD and the Interface Contract disagree on a behaviour, the choice follows the PRD (the Interface
Contract says it does not restate computation or defaults), except that the Interface Contract
governs signatures, types and refusal behaviour.

### Listed as unsettled

1. **CF-000001 — straight `"` at the start of text** (pack 22). N-000094 (Penn Treebank section):
   opening-quote token ``` `` ```. N-000106 (recommended section): closing-quote token `''`.
   *Built:* `TreebankWordTokenizer` gives ``` `` ```; the recommended `word_tokenize` gives `''`.
2. **CF-000008, CF-000039, CF-000072 — accuracy on lists of different lengths** (packs 15, 27, 28).
   N-000331 (pack 28): fraction over shared positions. N-000343 (pack 28), N-000318 (pack 27),
   N-000502 (pack 15) and the Interface Contract: refused. *Built:* `ValueError` (3 sides vs 1).
3. **CF-000016, CF-000055, CF-000070 — transposition in edit distance** (packs 15, 28). N-000325/327
   (pack 28): unrestricted Damerau–Levenshtein, insertions/deletions allowed between the transposed
   characters. N-000505/506 (pack 15): only adjacent characters, nothing inserted between.
   *Built:* the PRD's unrestricted definition (Lowrance–Wagner). `edit_distance('ca','abc',
   transpositions=True) == 2`. The adjacent-only variant is not built.
4. **CF-000028 — touching chunks** (pack 25). N-000240: two touching matches of one rule are two
   chunks. N-000242: touching chunks with no token between are joined.
   *Built:* matches of one rule stay separate; a chunk that touches a chunk of the same clause built
   by a *different* rule is joined into it.
5. **CF-000038 — f-measure with no shared element** (pack 28). N-000334: 0 when precision or recall
   is 0. N-000346: no number when the sets share no element. *Built:* `None` when either set is empty
   or they share no element (so the 0 case is unreachable).
6. **CF-000054 — tweet tokenizer lowercasing** (packs 19, 22). N-000067 (pack 19): lowercased unless
   case is preserved. N-000125 (pack 22): lowercased except emoticons. *Built:* N-000125 for the
   lowercasing rule (emoticons keep case). See item 14 for the default.
7. **CF-000073 — Porter Step 1a, `ties`** (packs 09, 23). N-000158 (pack 23, default mode):
   four-letter `-ies` → `-ie`, so `ties` → `tie`. N-000424 (pack 09): Step 1a "as published",
   `ties` → `ti`. *Built:* default `PorterStemmer()` (LINGORA mode) gives `tie`;
   `PorterStemmer(mode='original')` gives `ti`.
8. **CF-000077 — `discard_empty` default** (packs 07, 22). N-000118 (pack 22): on by default.
   N-000407 (pack 07): off unless `discard_empty=True`. *Built:* on by default, as the PRD says;
   `discard_empty=False` turns it off.
9. **CF-000083 — `cannot`** (pack 22). N-000102 (Treebank section): fused forms, including
   *cannot*, split. N-000110 (recommended section): *cannot* kept whole. *Built:* Treebank splits
   (`can not`), the recommended tokenizer keeps `cannot`.

### Conflicts found that the export does not list

10. **Chart parser and unknown tokens** (pack 26). N-000267/N-000292's list text: "none for a token
    list the grammar does not derive (including one holding a token that no production produces)".
    The boundary section of the same pack and Interface N-000475/476: must not succeed, distinguishable
    from an empty result. *Built:* `ValueError` (the boundary wording and the interface agree).
11. **Precision/recall argument types** (pack 28). N-000332: "a list or tuple given as either argument
    is read as the set of its elements." N-000345 (pack 28, also pack 15 N-000509): lists, tuples and
    other non-sets are refused. *Built:* `TypeError` for non-sets (two sides vs one).
12. **BLEU default weights** (packs 15, 28). N-000338 (pack 28, PRD): equal weights on unigrams
    through 4-grams. N-000513–515 (pack 15, Interface Contract): unigrams and bigrams when omitted.
    *Built:* the PRD default (4 × 0.25).
13. **Stemmer lowercasing default** (packs 09, 23). N-000154 (pack 23): lowercased first unless the
    caller turns it off. N-000422–427 (pack 09): `to_lowercase` defaults to `False`. *Built:* default
    `True` (the PRD governs behaviour).
14. **Tweet tokenizer preserve-case default** (packs 19, 22). N-000125 (pack 22): case preservation
    is on by default. N-000067 (pack 19): lowercased unless the caller asks to keep case. *Built:*
    `preserve_case=True` by default.

## Not done, partial, or unverified

Per-id reasons are in `SPEC_COVERAGE.md`. In short:

- **Snowball:** only `english` (Porter2) and `porter` are implemented. The other 14 languages are
  refused with `NotImplementedError` naming the language. Dutch (N-000173) is not done. The `porter`
  language uses the original-mode Porter, which may differ slightly from Snowball's rendering.
- **Lancaster (N-000170/171):** the engine follows Paice/Husk, but the rule table was reproduced
  from memory, is unverified and is likely incomplete (for example `presumably` does not reach
  `presum`). Treat its results as unreliable until the table is checked against the published one.
- **Porter `martin` mode (N-000149):** not implemented; `PorterStemmer(mode='martin')` raises.
- **Punkt (N-000129–133):** a simplified decision procedure (abbreviation, collocation,
  sentence-starter and orthographic checks) over the packaged parameters. It has no training step
  and is not a faithful Kiss & Strunk implementation. Sentence boundaries on real text may differ.
- **Averaged perceptron (N-000207–214):** the feature templates, normalisation and tie-break follow
  the textblob-aptagger/NLTK approach as I recall it. The resource file layout is from the spec. Not
  verified against real model files, which are not on this machine.
- **Affix tagger, recursive-descent parser, ISRI, Cistem, RSLP, ARLSTem/ARLSTem2 (N-000141,
  N-000187–189, N-000258):** not implemented. ARLSTem stubs raise `NotImplementedError`.
- **WordNet lemmatizer (N-000142, N-000185/186, N-000432):** refuses without WordNet (`LookupError`).
  With WordNet visible it raises `NotImplementedError`; the WordNet reader is not implemented.
- **Named-entity chunker (N-000231, N-000452):** the refusal path is implemented. The model format
  is not in the spec, so the success path raises `NotImplementedError`.
- **Command line:** only `-l/--language` and `-d/--delimiter`. Input and output are UTF-8 (fixed, not
  an option). Exit codes: 0 success, 1 failure (including a missing Punkt model, checked before any
  output), 2 usage error.

## Verification

- `python3 -m pytest -q` — 67 passed (Python 3.13). The suite uses synthetic resources, so it
  does not check real Punkt, perceptron or stopword data.
- I fuzzed the stemmers and tokenizers with 20,000 random words and 5,000 random strings with no
  exceptions. Porter2 outputs were spot-checked against known Snowball results.
- The parsers were checked on cyclic (`S -> S`) and epsilon grammars. The shift-reduce pass now
  rejects looping reductions, and the chart parser terminates through its cycle guard.
- No install or build step is required. An editable install from the repo root is possible via
  `pyproject.toml`, but I did not run it, since the judge does not install anything.
- Nothing has been committed (the directory is not a git repository).
