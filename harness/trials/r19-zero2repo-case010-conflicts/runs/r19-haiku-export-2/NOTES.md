# NOTES

Implementation of the LINGORA specification in `spec/` (exported with `--allow-open`;
19 contradictions had no human verdict). Layout: flat package `lingora/` at the
repository root; no build step; the modules import from `/app` as the working
directory. Tests: `python3 -m pytest -q` (54 passing).

Spec references: each module carries `# spec: N-xxxxxx` comments for the claims it
serves. Pack numbers below refer to `spec/packs/NN-*.md`.

## Conflicts and how they were resolved

The export lists 19 unsettled contradictions (`spec/MAP.md`, `CF-…`). For each: side A
and side B with their location, then what was built. Rule used when a PRD claim and an
Interface Contract claim collide: the Contract wins for call shape, defaults and
failure behaviour (it says what each entry takes and returns); the PRD wins for what is
computed unless the Contract states the value explicitly.

1. **CF-000001: straight `"` at the start of text.** A: pack 22 (Full PRD, FP-01 Penn
   Treebank bullet), N-000094, the opening-quote token ``` `` ```. B: pack 22
   (recommended word tokenizer bullet), N-000106, the closing-quote token `''`.
   Built: the Penn Treebank tokenizer gives ``` `` ```; the recommended word tokenizer
   (which the PRD lists as an improvement) gives `''`. Both can hold because they are
   different tokenizers.

2. **CF-000008, CF-000039, CF-000072: accuracy on lists of different lengths.** A:
   pack 28 N-000331 (FP-07): a fraction over the shared positions. B: pack 28 N-000343 and
   pack 27 N-000318 (FP-07 and FP-06): does not succeed; pack 15 N-000502 (Contract): raises. Built: `lingora.metrics.accuracy` raises `ValueError`. Two of the three
   claims that name the case say it fails, and the Contract is explicit.

3. **CF-000016, CF-000055, CF-000070: transposition in edit distance.** A: pack 28
   N-000325 (unrestricted Damerau–Levenshtein) and N-000327 (characters may be inserted or
   deleted between the transposed pair). B: pack 15 N-000505 (only characters adjacent in
   both strings may be transposed) and N-000506 (nothing inserted or deleted between
   them). Built: restricted (optimal string alignment) distance: transpositions only of
   adjacent characters, nothing between them. Both sides are MUST and the Contract gives
   the exact rule. For `ca`→`abc` this gives 3 (unrestricted gives 2).

4. **CF-000028: touching matches in a chunk rule.** A: pack 25 N-000240, "two matches that
   touch are two separate chunks." B: pack 25 N-000242, "chunks that touch, with no token
   between them, are joined into one chunk." Built: A. Matches of one rule that touch are
   separate chunks, as the NLTK-style chunk parser does.

5. **CF-000038: f-measure with disjoint sets.** A: pack 28 N-000334, "0 when precision or
   recall is 0". B: pack 28 N-000346, "no number when the two sets share no element."
   Built: `f_measure` returns `None` for an empty set or disjoint sets. The "0" case
   cannot arise otherwise, since precision and recall are both positive when the sets
   intersect.

6. **CF-000054: tweet tokenizer lowercasing.** A: pack 19 N-000067 (lowercases its tokens
   unless case is kept). B: pack 22 N-000125 (tokens are lowercased, except emoticons).
   Built: B, emoticons keep their case when case preservation is off. B is the more
   specific claim.

7. **CF-000073: Porter Step 1a, `ties`.** A: pack 23 N-000158, the LINGORA default mode
   maps a four-letter `-ies` word to `-ie`. B: pack 09 N-000424 (Contract), "Step 1a as
   published, so `ties` stems to `ti`." Built: B, `PorterStemmer().stem("ties") == "ti"`.
   The `-ies`→`-ie` extension is therefore not applied in the default mode. The other
   LINGORA extensions are applied.

8. **CF-000077: `discard_empty` default.** A: pack 22 N-000118, "on by default." B: pack 07
   N-000407 (Contract), "off unless the caller passes `discard_empty=True`." Built: B, off
   by default.

9. **CF-000083: `cannot`.** A: pack 22 N-000102, the fused form `cannot` is split into
   `can` + `not` (Treebank list). B: pack 22 N-000110, the recommended tokenizer keeps
   `cannot` as one token. Built: both. Treebank splits `cannot`; the recommended word
   tokenizer keeps it whole.

10. **CF-000086: precision and recall argument types.** A: pack 28 N-000332, a list or tuple
    is read as the set of its elements. B: pack 28 N-000345 and pack 15 N-000509 (Contract),
    lists, tuples and other non-sets are refused. Built: B, `TypeError` for non-sets.

11. **CF-000087: BLEU default weights.** A: pack 28 N-000338, equal weights on unigrams
    through 4-grams. B: pack 15 N-000515 (Contract), unigrams and bigrams only, longer
    n-grams not scored. Built: B, default weights `(0.5, 0.5)`.

12. **CF-000088: `Tree` given a string as its child list.** A: pack 26 N-000282 (FP-05), a
    string is taken as one leaf. B: pack 26 N-000288 (FP-05) and pack 13 N-000486 (Contract),
    the call is refused. Built: B,
    `TypeError`. A missing child list is also `TypeError`.

13. **CF-000089: quoted empty string in generation.** A: pack 26 N-000279, a quoted empty
    string contributes an empty-string token. B: pack 12 N-000480 (Contract), an
    empty-string terminal adds no token. Built: B.

14. **CF-000090: token no production produces.** A: pack 26 N-000267, such a token list
    gives no trees. B: pack 26 N-000292 and pack 12 N-000475, parsing does not succeed
    (raises). Built: B, `ValueError` raised by `parse(...)` at the call.

15. **CF-000091: Porter lowercasing default.** A: pack 23 N-000154, the word is lowercased
    first unless the caller turns lowercasing off. B: pack 09 N-000426 (Contract),
    `to_lowercase` defaults to `False`. Built: B, `stem(word)` keeps the case given; pass
    `to_lowercase=True` to lowercase.

Disagreements the export did not flag, and what was built:

16. **Chunk root label.** Pack 25 requires a root label that is the same for every parser
    and differs from clause labels; the spelling is the implementer's choice. Built:
    constant `"SENT"`.

17. **Parser result for ambiguity with empty productions.** Packs 26 and 12 do not say
    how a cyclic or empty-production grammar should behave. Built: the chart parser cuts
    cycles (a symbol cannot derive its own span while it is being derived). The shift-reduce
    parser ignores empty productions and gives up after a bounded number of reductions.

18. **`lingora.data.path` initial contents.** Pack 06 leaves them to the implementer. Built:
    taken from the `LINGORA_DATA` environment variable (`os.pathsep`-separated), empty when
    unset. Importing the package downloads nothing.

## Choices the spec left open

- Command-line options: `--language/-l` (default `english`), `--delimiter/-d` (default one space).
- Failure: exit status 1 with a message on standard error. The Punkt model is checked before
  any input is read, so a missing model writes no token line.
- `cli.main(args=None, standalone_mode=True)` falls back to `sys.argv[1:]` when `args` is `None`.
- Tree `pformat()` layout: a node stays on one line when it fits in 70 columns.
- Unigram tagger ties: the first tag seen in training wins.
- Averaged perceptron tagger: textblob-style features with NLTK-style normalisation; weights
  are cached per directory and reloaded when the file changes.
- Russian RNC tags map to universal tags by the part of speech before the first comma (table in `lingora/tag.py`).
- English universal mapping with the tables absent raises `LookupError` (the spec allows failing or unmapped tags).
- `ne_chunk` raises `LookupError` when either its wordlist or its model is missing, as specified.
- Edit distance / BLEU / metrics: `TypeError` for wrong argument types, `ValueError` for empty
  or mismatched inputs where the spec gives no value.

## Not done (with reasons)

These are the claims that are not implemented, or are only partly implemented.

- **Snowball languages other than `english` and `porter`** (arabic, danish, dutch, finnish,
  french, german, hungarian, italian, norwegian, portuguese, romanian, russian, spanish,
  swedish). The constructor accepts the names and raises `NotImplementedError` that names the
  language. Claims N-000172 (partly), N-000147/N-000428 (names listed; only two algorithms exist).
- **ISRI, Cistem, RSLP, ARLSTem, ARLSTem2.** PRD FP-02 says their results are outside the
  specification (N-000143–N-000146). `ARLSTem` and `ARLSTem2` exist as placeholders that return the
  word unchanged. ISRI, Cistem and RSLP are not implemented.
- **Bigram, trigram and affix taggers** (N-000187–N-000189, N-000035). PRD says their results are
  outside the specification. Not implemented.
- **Recursive-descent parser** (N-000258–N-000261). PRD says its results are outside the
  specification. Not implemented.
- **Named-entity chunker model** (N-000231, N-000038). The model format is not in the spec and its
  results are outside it. `ne_chunk` checks its resources (N-000452, N-000257) and raises
  `NotImplementedError` when they are present.
- **Lancaster rule table** (N-000170, N-000171). Implemented as the Paice/Husk engine, but the rule
  table was reconstructed from memory and may differ from the published one in some rules. Treat
  Lancaster output as unverified against the published table.
- **WordNet lemmatizer** (N-000432, N-000185, N-000186). It raises when `corpora/wordnet` is absent
  (as specified). When present it only checks the index files and applies simple noun detachment
  rules. Full WordNet morphy is outside the specification.
- **Production lines appended to a grammar text** (N-000265). The Contract gives no append API. Not built.
- **Punkt training.** Only the decision phase is implemented; the packaged parameters are read and
  applied. Training is not part of the surface.
- **Porter `MARTIN_EXTENSIONS` and `ORIGINAL_ALGORITHM` modes.** Their results are outside the
  specification. They are approximations, not verified against the published variants.
- **Packaged data.** No models, wordlists or WordNet are shipped (non-goal, N-000073). Tests create
  small fixture resources in a temporary directory.

Everything else in `spec/CHECKLIST.md` is implemented. The main behaviours are covered by
`tests/` (54 tests); finer claims were checked by reading the code and by ad hoc runs, and carry
a `# spec:` marker in the code, not a dedicated test.
