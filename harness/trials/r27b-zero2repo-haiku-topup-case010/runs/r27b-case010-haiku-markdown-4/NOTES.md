# LINGORA build notes

This file records how the three specification documents were read, where they
disagree and what was built in each case, and what is not implemented.

Layout: `lingora/` is the flat import package at the repository root
(`__init__`, `data`, `tokenize`, `tag`, `stem`, `chunk`, `grammar`, `tree`,
`classify`, `metrics`, `translate`, `cli`, `__main__`, and `parse/` with
`chart`, `shiftreduce`, `generate`). `pyproject.toml` describes a setuptools
flat-layout install; `conftest.py` at the root makes the package importable
when pytest runs from `/app`. Tests are in `tests/test_lingora.py`.

Reading rule used throughout: the Interface Contract is authoritative for
signatures, parameter defaults and output forms; the PRD is authoritative for
what an entry computes. Where both sides speak to the same point, the choice
below is listed.

## Disagreements between the specification files

1. **Porter default lowercasing.**
   - PRD, FP-02 (Porter, default mode): "The word is lowercased first, unless the caller turns lowercasing off."
   - Interface, Stemmers: "`to_lowercase` defaults to `False`, so `stem` keeps the letter case it is given."
   - Built: the Interface default (`to_lowercase=False`). Lowercasing happens only when the caller asks for it. This follows the signature rule.

2. **Porter Step 1a on *ties*.**
   - PRD, FP-02: "In Step 1a, a four-letter word ending in *-ies* becomes *-ie* rather than *-i*."
   - Interface, Stemmers: "`PorterStemmer` applies Step 1a as published, so *ties* stems to *ti*."
   - Built: the PRD rule, so `PorterStemmer().stem("ties") == "tie"`. The `"original"` mode gives `"ti"`, which is the published result.

3. **A string as a tree's child list.**
   - PRD, FP-05 (normal behaviour): "A string given in place of the child list is taken as a single leaf."
   - PRD, FP-05 (boundary) and Interface, Trees: building a tree from a string child list "is refused" / "makes `Tree` raise."
   - Built: refused (`TypeError`).

4. **Precision, recall and f-measure arguments.**
   - PRD, FP-07 (normal): "A list or tuple given as either argument is read as the set of its elements."
   - PRD, FP-07 (boundary): "Lists, tuples and other non-set collections are refused." Interface, Metrics: "A non-set argument makes the call raise."
   - Built: refused (`TypeError`).

5. **Accuracy on lists of different lengths.**
   - PRD, FP-07 (normal): "For lists of different lengths, it is that fraction over the positions both lists have."
   - PRD, FP-07 (boundary): "Accuracy on two lists of different lengths does not succeed." Interface, Metrics: "Lists of different lengths make it raise."
   - Built: raises `ValueError`.

6. **Edit distance with transpositions.**
   - PRD, FP-07: "characters may also be inserted between, or deleted from between, the two transposed characters" (unrestricted Damerau–Levenshtein).
   - Interface, Metrics: "only two characters that stand next to each other in both strings may be transposed, and nothing may be inserted or deleted between them" (restricted, optimal-string-alignment form).
   - Built: the PRD's unrestricted form (Lowrance–Wagner). `edit_distance("abc", "bca", transpositions=True) == 2`.

7. **BLEU default weights.**
   - PRD, FP-07: "The default is equal weights on unigrams through 4-grams."
   - Interface, Metrics: "When `weights` is omitted, unigrams and bigrams are weighted equally and longer n-grams are not scored."
   - Built: the Interface default, `weights=(0.5, 0.5)`.

8. **Empty-string terminal in generated sentences.**
   - PRD, FP-05 (generator): "A quoted empty string contributes an empty-string token."
   - Interface, Grammars: "A terminal that is the empty string adds no token to a sentence."
   - Built: the PRD behaviour (`""` is emitted as a token). An empty production contributes nothing in both.

9. **Leaves of a tree.**
   - Interface, Trees: children "are `str` leaves or trees."
   - Interface, Chunking: a chunk's children "are its `(token, tag)` pairs."
   - Built: `Tree` accepts `str`, `(token, tag)` tuples, and `Tree` children. Chunk output uses tuples.

10. **Touching chunks.**
    - PRD, FP-04 (chunk rule): "Two matches that touch are two separate chunks."
    - PRD, FP-04 (same bullet list): "Chunks that touch, with no token between them, are joined into one chunk."
    - Built: matches from a single rule stay separate. A new match that touches an existing chunk of the same clause is joined into that chunk. A later clause treats earlier chunks as units, so cascades nest.

11. **Recommended word tokenizer, leading straight double quote.**
    - PRD, FP-01: "A straight double quote at the very start of the text becomes the closing-quote token."
    - Built: implemented literally (the leading `"` becomes `''`). This is a literal reading, not a resolved conflict; it is kept because it is what the text says.

## Choices where the spec is silent or open

- Packaged-data finder: `data.path` starts from the `LINGORA_DATA` environment variable (os.pathsep separated) and is empty otherwise. Nothing is downloaded.
- Punkt: the sentence splitter follows Kiss & Strunk with the packaged parameters. The annotation rules were reconstructed from the paper and from the algorithm as I know it, not copied from any source. No Punkt model was available, so it was tested only with a small fixture written under `/tmp` (outside `/app`).
- Averaged perceptron tagger: the feature templates and the tagdict/classes handling follow the textblob-aptagger design named in the PRD. No packaged weights were available, so only the missing-resource path was exercised.
- Universal mapping: English uses the packaged `en-ptb.map`; unknown tags map to `X`. Russian uses a built-in table keyed by the part before `=` (`S`→NOUN, `V`→VERB, and so on); unknown categories map to `X`.
- Naive Bayes: expected-likelihood smoothing (add 0.5 per bin, bins = distinct values of that feature in training). Classes listed in first-seen order.
- Decision tree: ID3 with multiway splits on value (absent feature = `None` branch); stops when a node is pure, when no features remain, or when no feature has positive information gain; leaves take the majority label.
- `accuracy` on an empty gold list returns `0.0` (classify) and `0.0` (metrics); the spec does not say.
- `jaccard_distance` of two empty sets returns `0.0`.
- `f_measure` takes an optional `alpha` (default 0.5).
- BLEU: an optional `smoothing_function` takes a list of `(numerator, denominator)` pairs and returns precisions; `add_one_smoothing` is provided. Empty hypothesis scores `0.0`.
- Chart parser: exhaustive, memoised per (symbol, span), with cycles through the same (symbol, span) cut. Unknown tokens raise at call time.
- Shift-reduce parser: a single pass; it does not use empty productions for reduction. Reduction is by production order.
- Generator: depth-first in written order. `depth=None` is unbounded and, for a recursive grammar, may recurse without reaching `n`; a `depth` bound is needed in that case (as in NLTK).
- CLI: `lingora tokenize [--language L] [--delimiter D] [--encoding E]`. It checks for the Punkt model before reading any input, so a missing model writes nothing and exits 1. Success exits 0. Errors go to stderr.
- `Group.main(args, standalone_mode)` is a small stand-in for a click group (click is not a dependency).

## Not implemented (gaps)

- **Snowball stemmers for 14 of the 16 listed languages.** Only `english` (Porter2) and `porter` (the original Porter algorithm) are implemented. For arabic, danish, dutch, finnish, french, german, hungarian, italian, norwegian, portuguese, romanian, russian, spanish and swedish, the name is validated and the stopword check runs, then construction raises `NotImplementedError` naming the language. This is a real gap in FP-02, not a design choice.
- **Lancaster rule table.** The Paice/Husk table was written from memory of the standard list and may differ from the published table in some entries. The algorithm (intact-only rules, stop/continue, minimum stem length 2) follows the published description. Spot checks: `maximum`→`maxim`, `nationality`→`nat`, `running`→`run`.
- **Porter `"martin"` mode** is treated as the original algorithm. Its results are outside the spec.
- **ARLSTem, ARLSTem2, WordNetLemmatizer**: exist, but their stemming/lemmatising raises `NotImplementedError`. `WordNetLemmatizer()` raises `LookupError` when WordNet is not visible, as specified.
- **Named-entity chunker** (`ne_chunk`): raises `LookupError` when its model or the wordlist is missing, as specified. When both are present it raises `NotImplementedError` (its results are outside the spec).
- **Affix tagger**: a simple prefix/suffix version is provided; its results are outside the spec.

## Verification

- `python3 -m pytest -q tests` in `/app`: 19 tests pass. They cover tokenizers (word/punct, Treebank, recommended, tweet, regexp, whitespace, blank-line, spans), Punkt sentence splitting (with a fixture), stemmers (Porter, Porter2, Lancaster, regexp, stopword gating), sequential taggers, chunking (cascades and chinks), chart and shift-reduce parsing, the generator, trees, both classifiers, metrics, BLEU, and the CLI success and failure paths.
- Packaged models (Punkt, perceptron tagger, universal tables, stopwords) are not available in this environment, so the recommended English and Russian tagging and the Punkt splitter on real models are not verified here.
