# NOTES

Build notes for the `lingora` library in `/app`. The specification is `spec/` (unchanged).
Code lives in `/app/lingora/` (flat layout, pure Python, Python 3.10+). Tests live in
`/app/tests/` and run with `python3 -m pytest` from `/app`.

## 1. Disagreements in the specification, and what was built

The export was made with `--allow-open` and lists 13 unsettled contradictions. Below, each
disagreement is quoted with its location, then what was built. Where the export did not flag a
disagreement, it is listed too, marked **(not flagged)**.

### 1.1 Unsettled contradictions (CF ids from `spec/MAP.md`)

| # | Where | Side A | Side B | Built |
|---|---|---|---|---|
| CF-000001 | `packs/22-…fp-01…` (N-000094, N-000106) | N-000094, Penn Treebank rules: "A straight double quote at the start of the text, or after a space or an opening bracket, becomes the opening-quote token made of two backticks." | N-000106, recommended word tokenizer: "A straight double quote at the very start of the text becomes the closing-quote token." | Penn Treebank tokenizer: opening quote (``). Recommended tokenizer (`word_tokenize`): the start-of-text quote becomes the closing-quote token (''), since N-000106 is the more specific rule for that tokenizer. |
| CF-000008 (also CF-000039, CF-000072) | `packs/28-…fp-07…` N-000331, `packs/15-…metrics…` N-000502, `packs/27-…fp-06…` N-000318, `packs/28` N-000343 | N-000331: "For lists of different lengths, it is that fraction over the positions both lists have." | N-000343 / N-000318: "Accuracy on two lists of different lengths does not succeed." N-000502: "Lists of different lengths make it raise." | Raise (`UnsupportedInput`) for lists of different lengths. Two of the three statements say it does not succeed. |
| CF-000016 (also CF-000055, CF-000070) | `packs/15` N-000325, N-000327, N-000505, N-000506; `packs/28` N-000325, N-000327 | N-000325: "the distance is the unrestricted Damerau–Levenshtein distance"; N-000327: "characters may also be inserted between, or deleted from between, the two transposed characters." | N-000505: "only two characters that stand next to each other in both strings may be transposed"; N-000506: "nothing may be inserted or deleted between them." | Optimal string alignment (adjacent transposition only, nothing inserted or deleted between the pair), which is the interface contract's statement (`packs/15`, N-000505/N-000506). `edit_distance("ca", "abc", transpositions=True)` is 3. |
| CF-000028 | `packs/25-…fp-04…` N-000240 vs N-000242 | N-000240: "Two matches that touch are two separate chunks." | N-000242: "Chunks that touch, with no token between them, are joined into one chunk." | Touching matches stay separate chunks (N-000240). The joining rule (N-000242) is not implemented. |
| CF-000038 | `packs/28` N-000334 vs N-000346 | N-000334: "It is 0 when precision or recall is 0." | N-000346: f-measure gives "no number" when the two sets share no element. | When the sets share no element, `f_measure` returns `None`. The 0 result applies only when precision or recall is 0 with a shared element, which cannot happen with a non-empty intersection, so the 0 branch is retained but unreachable in practice. |
| CF-000054 | `packs/19` N-000067 vs `packs/22` N-000125 | N-000067: the tweet tokenizer "lowercases its tokens unless the caller asks to preserve case." | N-000125: "tokens are lowercased, except emoticons." | Emoticons are not lowercased. |
| CF-000073 | `packs/23` N-000158 vs `packs/09` N-000424 | N-000158 (PRD): "a four-letter word ending in *-ies* becomes *-ie* rather than *-i*." | N-000424 (interface): "`PorterStemmer` applies Step 1a as published, so *ties* stems to *ti*." | `PorterStemmer()` (default mode, the LINGORA extensions) gives `ties` → `tie`. The interface sentence describes "Step 1a as published"; the PRD defines the default mode as the LINGORA extensions. |
| CF-000077 | `packs/22` N-000118 vs `packs/07` N-000407 | N-000118: empty-discarding "is on by default." | N-000407: "discard_empty is off unless the caller passes `discard_empty=True`." | Off by default (the interface contract's signature statement). |
| CF-000083 | `packs/22` N-000102 vs N-000110 | N-000102 (Penn Treebank): the fused form *cannot* "[is] split into their two parts (*can* + *not*)." | N-000110 (recommended tokenizer): "*cannot* is kept as one token." | Penn Treebank tokenizer splits `cannot` into `can not`; recommended tokenizer keeps `cannot`. |

### 1.2 Disagreements the export did not flag

- **Quoted empty string in generation (not flagged).** `packs/26` N-000280: "A quoted empty string contributes an empty-string token." vs `packs/12` N-000480: "A terminal that is the empty string adds no token to a sentence." **Built:** no token (N-000480, the interface contract).
- **List arguments to precision/recall/f-measure (not flagged).** `packs/28` N-000332: "A list or tuple given as either argument is read as the set of its elements." vs `packs/28` N-000345 and `packs/15` N-000509: "Lists, tuples and other non-set collections are refused." **Built:** refused (`UnsupportedInput`).
- **Default lowercasing in the Porter stemmer (not flagged).** `packs/23` N-000154: the word "is lowercased first, unless the caller turns lowercasing off" vs `packs/09`: "`to_lowercase` defaults to `False`, so `stem` keeps the letter case it is given." **Built:** the interface default (`to_lowercase=False`).
- **Default n-gram weights for BLEU (not flagged).** `packs/28` N-000337: "The default is equal weights on unigrams through 4-grams." vs `packs/15` N-000513–N-000515: "When `weights` is omitted, unigrams and bigrams are weighted equally and longer n-grams are not scored." **Built:** weights (0.5, 0.5), the interface contract's statement.
- **Default case preservation in the tweet tokenizer (not flagged).** `packs/22` N-000125: "case preservation off (it is on by default)" vs `packs/19` N-000067: lowercasing by default. **Built:** `preserve_case=True` by default (no lowercasing).

## 2. Not done

These checklist ids are not implemented. `tests/test_spec_coverage.py` checks that each one is listed here.

- **N-000038 — named-entity chunker.** `lingora.chunk.ne_chunk` checks that the NE model and the English wordlist are visible (raising `ResourceNotFound` otherwise), then raises `NotImplementedError`. The maximum-entropy model is not implemented.
- **N-000140, N-000141 — ISRI, Cistem and RSLP stemmers.** Not implemented. `ARLSTem` and `ARLSTem2` exist as light Arabic stemmers with unspecified results (the spec says their results are outside it); they are approximations.
- **N-000172 — Snowball for 14 of the 16 languages.** `SnowballStemmer` accepts all 16 names, but only `english` (Porter2) and `porter` (original Porter) stem. Other languages raise `NotImplementedError` at `stem()` time, naming the language.
- **N-000173 — Snowball Dutch.** Not implemented (part of the same gap as N-000172).
- **N-000258 — recursive-descent parser.** Not implemented. The spec says its results are outside it; the chart and shift-reduce parsers are implemented.

Also not built, deliberately, because the spec places them outside the feature points (the checklist ids for these are satisfied by omission, see the `# spec:` markers in `lingora/__init__.py`): graphical applications, chat/Twitter/Hugging Face/Toolbox helpers, external-binary wrappers, CCG/DRT/inference, n-gram language models, the s-expression tokenizer, the corpus downloader.

## 3. Choices made where the spec leaves room

- **Packaged resources.** No models are shipped; `data.path` starts with the entries of the `LINGORA_DATA` environment variable (os.pathsep separated), then `~/lingora_data` and `/usr/share/lingora`. Resource names follow the spec's table (`tokenizers/punkt_tab/<language>/`, `taggers/averaged_perceptron_tagger_<lang>/`, etc.).
- **Exceptions.** `LingoraError` base; `ResourceNotFound` (also `LookupError`) for a missing model; `UnsupportedInput` (also `TypeError`) for a wrong argument type or value; `ParseError` (also `ValueError`) for a token that no production produces.
- **Punkt sentence splitting** (`lingora/_punkt.py`) reads the four packaged parameter files as the spec describes. The decision rules are a simplified Punkt: abbreviation types, collocations, sentence starters, and orthographic context, with blank lines as hard breaks. It is not a port of the full Punkt algorithm and has not been checked against real Punkt models (none are on this machine).
- **Penn Treebank and recommended tokenizers** (`lingora/tokenize.py`) are regex pipelines following the spec's list of rules. The span of each token in `TreebankWordTokenizer.span_tokenize` is found by aligning tokens to the text.
- **Porter stemmer.** `PorterStemmer(mode="lingora")` is the default; `mode="original"` is the published algorithm (used for the `porter` Snowball language). The irregular-forms table is empty (the spec leaves its entries outside it).
- **Porter2 (English Snowball)** is implemented from the published description, including the exception lists in the usual form; it has not been checked against the Snowball reference outputs.
- **Lancaster** (`LancasterStemmer`). The rule table is reproduced from memory of the published Paice/Husk rules and may differ from the reference table in a few rules. The acceptability test is the usual "stem must keep at least two letters, or three with a vowel".
- **Chunk parser semantics.** Chunk rules match only tokens not yet in a chunk; a chunk built in an earlier clause is a single unit that later chunk rules cannot match into, and chink rules act only on chunks of the same clause (N-000243–N-000249). The root label is `S`.
- **Chart parser** is exhaustive: a fixed point over spans, keeping only trees in which no node repeats beneath itself on the same span (so the result is finite for cyclic grammars). **Shift-reduce parser**: one pass, reduce whenever a production's right-hand side matches the top of the stack, otherwise shift; no backtracking. It returns `[]` when the pass does not end in the start symbol (as the spec requires).
- **Generator**: lazily yields sentences by iterative deepening over derivation depth, deduplicated; stops after `n` sentences, or when the depth stops producing new sentences for a while (so finite grammars terminate).
- **Trees**: `Tree(label, children)`, children must be a list/tuple (a `str` or omission raises). `pformat()` shows one node per line with indentation; the leaves appear in pre-order.
- **Naive Bayes** uses expected-likelihood smoothing `(count + 0.5) / (N_label + 0.5·(|values|+1))`; features never seen in training are ignored. **Decision tree** splits on maximum information gain; absent features count as a `None` value; unseen values fall back to the node's majority label. Ties go to the label seen first in training.
- **Classifier and list accuracy** of an empty gold list return `0.0` (the spec does not define it).
- **Metrics.** `jaccard_distance` of two empty sets returns `0.0`. `f_measure` takes an optional `alpha=0.5`.
- **BLEU** (`lingora/translate.py`): `smoothing_function(counts)` receives `(matches, total)` pairs per order and returns precisions; `epsilon_smoothing` is provided.
- **Tweet tokenizer** uses a regex with emoticon, URL, hashtag, handle, number, word-with-apostrophe, ellipsis and punctuation alternatives.
- **Command line** (`lingora/cli.py`): `cli.main(args=[...], standalone_mode=True)`. Options: `--language` (default `english`), `--delimiter` (default one space), `--encoding` (default `utf-8`). Missing Punkt models are detected before any output, so the command fails with status 1 and writes nothing. Usage errors exit with the argparse status (2). `python -m lingora tokenize` is equivalent.
- **Averaged perceptron tagger** (`lingora/tag.py`) follows the feature templates and normalisation the PRD describes (textblob-aptagger style). Universal mapping: English via `en-ptb.map` (raises if the table is absent); Russian via a small table on the part before `=` (the spec leaves the table to the implementer).
- **Bigram, trigram and affix taggers** are implemented in a simple form (the spec says their results are outside it).
- **WordNet lemmatizer** (`lingora/stem.py`) checks the WordNet directory at construction and does a morphy-style lookup in the `index.*` files. This is an approximation; WordNet's results are outside the spec.

## 4. Verification

- `python3 -m pytest` runs 79 tests, all passing. Tests that need packaged data build tiny fake resources in a temporary directory (`tests/conftest.py`); the resources exist only for the tests.
- No real packaged model is present on this machine, so the Punkt, perceptron-tagger and Lancaster outputs were not checked against reference data.
- `tests/test_spec_coverage.py` checks that every id in `spec/CHECKLIST.md` is either referenced by a `# spec:` marker in `lingora/` or `tests/`, or listed in section 2 above. Result: 511 of 517 ids are referenced by code; the other 6 are exactly the section 2 list (N-000038, N-000140, N-000141, N-000172, N-000173, N-000258).
