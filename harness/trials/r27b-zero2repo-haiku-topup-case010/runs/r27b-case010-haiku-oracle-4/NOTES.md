# NOTES

Implementation of the LINGORA specification in `spec/` (517 checklist ids, 29 packs).
Code lives in `/app/lingora` (flat layout), tests in `/app/tests`.

## How to run

- No build step. Import from `/app` (project root on `sys.path`), or `pip install -e .`.
- Tests: `python -m pytest -q tests` (68 tests pass in this environment).
- Packaged models (Punkt, the perceptron tagger, the universal tagset map, stopwords, WordNet,
  the named-entity model) are not shipped. They are searched in `lingora.data.path`, which starts
  from `$LINGORA_DATA` (os.pathsep-separated), `~/lingora_data` and `<sys.prefix>/share/lingora`.
  A path that needs a missing model raises `lingora.data.ResourceNotFound`.
- The tests build synthetic model directories in a temp dir; the real packaged parameters were not
  available here, so the model-dependent paths (Punkt, perceptron tagger, universal map) are verified
  only against those synthetic models.

## Spec disagreements and what was built

The export was made with `--allow-open`; 19 contradictions are unsettled (`spec/MAP.md`). For each,
the choice below is the one the code implements. "Contract" means `spec/packs/04..15`
(Interface Contract), "PRD" means `spec/packs/16..29` (Full PRD).

| Id | Topic | Side A (pack, claim) | Side B (pack, claim) | Built |
|---|---|---|---|---|
| CF-000001 | Penn/recommended quote at text start | pack 22, N-000094: "A straight double quote at the start of the text, or after a space or an opening bracket, becomes the opening-quote token" | pack 22, N-000106: "A straight double quote at the very start of the text becomes the closing-quote token" | Penn tokenizer: opening ``. Recommended tokenizer: closing '' (its own rule overrides the Penn convention). |
| CF-000008, CF-000039, CF-000072 | `accuracy` on lists of different lengths | pack 28 N-000331 (FP-07) and pack 15 N-000331-side text: "For lists of different lengths, it is that fraction over the positions both lists have" | pack 28 N-000343 and pack 27 N-000318 ("does not succeed"); pack 15 N-000502 (Contract): "Lists of different lengths make it raise" | Raises `ValueError`. Three sections agree on this. |
| CF-000016, CF-000055, CF-000070 | Transposition in edit distance | pack 28, N-000325/N-000327: unrestricted Damerau-Levenshtein; characters may be inserted/deleted between the transposed pair | pack 15, N-000505/N-000506 (Contract): only characters adjacent in both strings may be swapped; nothing may be inserted or deleted between them | The restricted (optimal-string-alignment) form, per the Contract's explicit rule. `edit_distance("ca","abc",transpositions=True) == 3`. |
| CF-000028 | Touching matches in chunk rules | pack 25, N-000240: "Two matches that touch are two separate chunks" | pack 25, N-000242: "Chunks that touch, with no token between them, are joined into one chunk" | Touching matches stay separate chunks. |
| CF-000038 | f-measure with no shared element | pack 28, N-000334: "It is 0 when precision or recall is 0" | pack 28, N-000346: "the two sets share no element return no number" | Disjoint sets (no shared element), an empty set, or an undefined precision/recall give `None`. The "0" branch is kept but is unreachable when a shared element exists. |
| CF-000054 | Tweet tokenizer case of emoticons | pack 22, N-000125: "tokens are lowercased, except emoticons" | pack 19, N-000067: "lowercases its tokens unless the caller asks to preserve case" | Emoticons keep their case (N-000125 is the more specific statement). |
| CF-000073 | Porter Step 1a `ies` | pack 23, N-000158 (LINGORA extension): "a four-letter word ending in -ies becomes -ie rather than -i" | pack 9, N-000424 (Contract): "PorterStemmer applies Step 1a as published, so ties stems to ti" | `ties -> ti` (the Contract's concrete example). The `-ies -> -ie` extension is not applied to Step 1a. The Step 1b `-ied` extension is applied as specified. |
| CF-000077 | `discard_empty` default | pack 22, N-000118: "Empty pieces ... dropped unless the caller turns empty-discarding off (it is on by default)" | pack 7, N-000407 (Contract): "`discard_empty` is off unless the caller passes `discard_empty=True`" | Off by default (Contract, interface-level). |
| CF-000083 | `cannot` | pack 22, N-000102 (Penn fused forms): "*cannot* ... split into their two parts" | pack 22, N-000110 (recommended): "*cannot* is kept as one token" | Penn tokenizer splits `can` + `not`; the recommended word tokenizer keeps `cannot`. |
| CF-000086 | Sets in precision/recall | pack 28, N-000332: a list or tuple argument "is read as the set of its elements" | pack 28, N-000345 (and Contract N-000508/N-000509): "Lists, tuples and other non-set collections are refused" | Refused (`TypeError`). |
| CF-000087 | BLEU default weights | pack 28, N-000338: "The default is equal weights on unigrams through 4-grams" | pack 15, N-000515 (Contract): "longer n-grams are not scored"; N-000513/514: unigrams and bigrams | Default weights `(0.5, 0.5)` (unigrams and bigrams). |
| CF-000088 | `Tree` given a string as children | pack 26, N-000282: "A string given in place of the child list is taken as a single leaf" | pack 26, N-000288 and Contract N-000486: refused | Refused (`TypeError`). |
| CF-000089 | Empty quoted terminal in generation | pack 26, N-000279: "A quoted empty string contributes an empty-string token" | pack 12, N-000480 (Contract): "A terminal that is the empty string adds no token" | Adds no token (Contract). |
| CF-000090 | Token no production produces | pack 26, N-000267: "none for a token list ... (including one holding a token that no production produces)" | pack 26, N-000292 and Contract N-000475: "does **not** succeed" | Raises `ValueError` (the failure is distinguishable from an empty set of parses). |
| CF-000091 | Porter lowercasing default | pack 23, N-000154: "The word is lowercased first, unless the caller turns lowercasing off" | pack 9, N-000426 (Contract): "`to_lowercase` defaults to `False`" | Default `False`: the case of the given letters is kept (opt in with `to_lowercase=True`). |

Other choices where the spec leaves the implementer free or is silent:

- Porter modes: `PorterStemmer(mode=...)` accepts `LINGORA` (default, all extensions),
  `MARTIN` and `ORIGINAL`. The non-default modes are approximations (results are outside the spec).
- Lancaster: the rule table is reconstructed from memory of the Paice/Husk rule set and is incomplete.
  Some words may differ from the published output.
- Snowball: `english` is Porter2 and `porter` is the original Porter algorithm (see not-done below).
- Punkt: decision rules follow the Punkt paper (collocations, abbreviations, initials/ordinals,
  sentence starters, orthographic heuristic). The orthographic heuristic is simplified.
- Chunk root label is `S` (implementer's choice). A list of chunk stages is accepted as the
  alternative grammar form; each stage is its own clause.
- Chunk-grammar continuation lines are indented, or start with `{`/`}`.
- Decision tree: ID3 with information gain; a feature absent from a featureset is value `None`.
- Naive Bayes: add-one smoothing per feature name; unseen feature names are ignored.
- BLEU smoothing: `bleu(..., smoothing_function=f)`, where `f(numerators, denominators)` returns
  a list of precisions (name and form are implementer's choice).
- CLI: options `--language/-l`, `--delimiter/-d` (default one space), `--encoding/-e`. Failure exit
  status is 1. Standard-error text is a one-line message.
- `pos_tag` with `tagset='universal'`: English uses the packaged `en-ptb.map`. Russian uses a built-in
  table keyed on the part before `=`. Unmapped English tags are returned unchanged.
- `ne_chunk`: checks its resources (raises when missing). When both are visible it raises
  `NotImplementedError`, because the packaged model format is not documented in the spec.

## Not done (with reasons)

- **Bigram, trigram and affix taggers** (N-000187, N-000188, N-000189). They are named as public
  entries in FP-03, and their results are outside the spec. Not implemented.
- **Snowball languages other than `english` and `porter`** (N-000172, and Dutch under N-000173). The constructor accepts all 16 names and validates them, and stopword skipping
  works for all. `stem()` raises `NotImplementedError` for the 14 other languages.
- **ISRI, Cistem and RSLP stemmers** (N-000140..N-000146). Named in FP-02, with results outside the
  spec. Not implemented. `ARLSTem` and `ARLSTem2` exist (the Contract imports them) but their
  `stem()` raises `NotImplementedError`.
- **Recursive-descent parser** (N-000258, N-000259). Named in FP-05 with results outside the spec.
  Not implemented.
- **Named-entity chunker output** (N-000231, N-000452 model path). Resource checks are implemented;
  the model itself is not (see above).
- **Penn tokenizer `span_tokenize`**: not required by the spec and not implemented.
- **Non-goals and out-of-scope surfaces** (N-000072..N-000080, N-000349..N-000352): graphical
  tools, chat and Twitter helpers, external-binary wrappers, CCG and inference, N-gram models,
  packaged corpora and the downloader. Not implemented, by design.
- **WordNet lemmatizer** (N-000185, N-000186, N-000432): implemented against the WordNet 3.0 index
  and exception-file layout. Untested against real WordNet data (none is shipped).

## Coverage by checklist id

Each id is implemented unless listed above. Tests in `tests/test_lingora.py` exercise the behaviour
listed in the Module column; the packs marked (model) are verified only with synthetic models.

| Pack | Ids | Module(s) | Status |
|---|---|---|---|
| 02, 03 | N-000353..N-000370 | `pyproject.toml`, package layout; `test_wordpunct_tokenize_runs_without_models` | implemented |
| 05 | N-000371..N-000384 | `lingora/__init__.py`, all modules (callables, exceptions, numbers) | implemented |
| 06 | N-000385..N-000402 | `lingora/data.py`, `lingora/_punkt.py`, `lingora/tag.py` (resource names, file formats) | implemented |
| 07 | N-000403..N-000413 | `lingora/tokenize.py` | implemented (sent tokenizer: model) |
| 08 | N-000414..N-000420 | `lingora/cli.py` | implemented |
| 09 | N-000421..N-000432 | `lingora/stem.py` | implemented; Snowball languages and ARLSTem*: see not done |
| 10 | N-000433..N-000445 | `lingora/tag.py` | implemented |
| 11 | N-000446..N-000460 | `lingora/chunk.py` | implemented; NE model: see not done |
| 12 | N-000461..N-000480 | `lingora/grammar.py`, `lingora/parse/__init__.py`, `lingora/parse/generate.py` | implemented |
| 13 | N-000481..N-000491 | `lingora/tree.py` | implemented |
| 14 | N-000492..N-000497 | `lingora/classify.py` | implemented |
| 15 | N-000498..N-000517 | `lingora/metrics.py`, `lingora/translate.py` | implemented |
| 16, 17, 18, 19, 20 | N-000001..N-000071, N-000016..N-000069 | product, vocabulary, surface and non-functional constraints | implemented (see `NOTES.md` spec-choice rows) |
| 21, 29 | N-000072..N-000080, N-000349..N-000352 | out of scope | not done (by design) |
| 22 | N-000081..N-000139 | `lingora/tokenize.py`, `lingora/_punkt.py`, `lingora/cli.py` | implemented (sentence splitting: model) |
| 23 | N-000140..N-000186 | `lingora/stem.py` | implemented for `english`/`porter`; see not done |
| 24 | N-000187..N-000227 | `lingora/tag.py` | implemented; bigram/trigram/affix not done |
| 25 | N-000228..N-000257 | `lingora/chunk.py` | implemented; NE model not done |
| 26 | N-000258..N-000294 | `lingora/grammar.py`, `lingora/parse/`, `lingora/tree.py` | implemented; recursive descent not done |
| 27 | N-000295..N-000318 | `lingora/classify.py` | implemented |
| 28 | N-000319..N-000348 | `lingora/metrics.py`, `lingora/translate.py` | implemented |

The checklist itself (`spec/CHECKLIST.md`) was not edited, as required.
