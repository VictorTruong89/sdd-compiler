# LINGORA build notes

This file records where the specification disagrees with itself, which side I built,
and the parts that are not complete. Sources: `spec/Full_PRD.md` (PRD),
`spec/Interface_Contract.md` (Interface), `spec/Hardware_Requirements.md` (HW).

Rule used to resolve conflicts: the Interface Contract says that it owns signatures,
parameter defaults and output shapes, and that the PRD owns what each entry computes.
Where two places in the PRD contradict each other, the boundary/error statement and the
Interface agreed in each case below, so that side was built.

## Spec disagreements and what was built

1. **Porter `to_lowercase` default.**
   - PRD FP-02: "The word is lowercased first, unless the caller turns lowercasing off" (implies on by default).
   - Interface: `PorterStemmer().stem(word, to_lowercase=…)`, "`to_lowercase` defaults to `False`".
   - Built: default `False` (signature default, Interface).

2. **Porter `ties` example.**
   - Interface: "`PorterStemmer` applies Step 1a as published, so *ties* stems to *ti*".
   - PRD FP-02 (LINGORA extension): a four-letter word ending in *-ies* becomes *-ie*, so *ties* → *tie*.
   - Built: PRD behaviour, `ties` → `tie`. The Interface example is original-Porter behaviour.

3. **Edit distance with transpositions.**
   - PRD FP-07: unrestricted Damerau–Levenshtein (Lowrance and Wagner, 1975), where characters may be inserted between transposed characters.
   - Interface: only adjacent characters may be transposed, with nothing inserted or deleted between them.
   - Built: PRD (unrestricted). Example: `edit_distance("ca", "abc", transpositions=True) == 2`.

4. **BLEU default weights.**
   - PRD FP-07: default is equal weights on unigrams through 4-grams.
   - Interface: when `weights` is omitted, unigrams and bigrams are weighted equally.
   - Built: Interface default `(0.5, 0.5)`, since it is a signature default. A `smoothing_function` keyword was added (the Interface leaves its form open).

5. **Precision, recall and f-measure with list arguments.**
   - PRD FP-07 normal behaviour: "A list or tuple given as either argument is read as the set of its elements".
   - PRD FP-07 boundary behaviour and Interface: lists, tuples and other non-sets are refused.
   - Built: refusal (`TypeError`).

6. **Accuracy on lists of different length.**
   - PRD FP-07 normal behaviour: the fraction over the positions both lists have.
   - PRD FP-07 boundary behaviour and Interface: the call raises.
   - Built: raises `ValueError`. Two empty lists return `0.0`, which the spec does not define.

7. **Tree built with a string as the child list.**
   - PRD FP-05 normal behaviour: "A string given in place of the child list is taken as a single leaf".
   - PRD FP-05 boundary behaviour and Interface: refused.
   - Built: refused (`TypeError`). A string child list and a missing child list both raise.

8. **Quoted empty-string terminal in generation.**
   - PRD FP-05: "A quoted empty string contributes an empty-string token".
   - Interface: "A terminal that is the empty string adds no token to a sentence".
   - Built: PRD. `generate` yields `''` for it. The chart and shift-reduce parsers match a `''` terminal against a `''` token. An empty production contributes nothing.

9. **`RegexpTokenizer` empty-piece default.**
   - PRD FP-01: empty pieces are dropped by default ("it is on by default").
   - Interface: `discard_empty` is off unless the caller passes `True`.
   - Built: off, the Interface default. `discard_empty=True` drops empty pieces.

10. **Touching chunk matches.**
    - PRD FP-04: "Two matches that touch are two separate chunks."
    - PRD FP-04, same rule: "Chunks that touch, with no token between them, are joined into one chunk."
    - Built: separate chunks, which is the statement about chunk-rule matches. The joining statement is not implemented, so the two statements are not both satisfied.

11. **f-measure when precision or recall is 0.**
    - PRD FP-07 normal behaviour: "It is 0 when precision or recall is 0".
    - PRD FP-07 boundary behaviour: no number when the two sets share no element.
    - Built: where the two sets share no element (the only way precision or recall is 0 for non-empty sets), `f_measure` returns `None`, never `0`. `alpha` is an optional keyword, default 0.5.

12. **Cascading chunk rules.**
    - PRD FP-04: "A later clause sees every chunk built by an earlier clause as a single unit whose tag is that chunk's label, so it can chunk the remaining tokens but cannot chink inside an earlier clause's chunks."
    - Built: a later clause's chunk rule may match an earlier clause's chunk by its label and nest it. Chinking is restricted to the current clause's chunks.

13. **Other choices (not contradictions).**
    - `word_tokenize` default `preserve_line=False`, since the PRD says it splits sentences unless told the input is one line.
    - The recommended word tokenizer applies per sentence, so a straight quote that begins a sentence is treated as a closing quote.
    - `Tree.pformat()` layout is my choice (Interface: implementer's choice).
    - Named-entity chunker is unsupported (see below).

## Known gaps in this build

- **Snowball:** only `english` (Porter2) and `porter` (original Porter) are implemented. The other listed languages (arabic, danish, dutch, finnish, french, german, hungarian, italian, norwegian, portuguese, romanian, russian, spanish, swedish) can be named, but their constructor raises `NotImplementedError` naming the language. Stopword skipping checks the file `corpora/stopwords/<language>` first, as specified.
- **Lancaster:** the rule table in `lingora/stem.py` is reconstructed from memory, not copied from the published Paice/Husk table. Some results differ from the published algorithm (for example *presumably* → *presumy*, *nationally* → *naty*).
- **Punkt sentence splitting:** a simplified decision procedure over the packaged parameters (abbreviation types, sentence starters, collocations, orthographic context). It is not a line-by-line port of Punkt's training or heuristics. Its results depend on the model files, which were not available here. I tested it only with small fabricated model files.
- **Averaged perceptron tagger:** implements textblob-aptagger feature templates and normalisation as I recall them. I did not verify compatibility with a real packaged model, which is not present in this environment. The Russian universal mapping uses my own table (PRD allows any table).
- **Named-entity chunker:** `ne_chunk` checks that the model and wordlist are visible (raising `LookupError` if not), then raises `NotImplementedError` even when they are present.
- **Not implemented:** `ARLSTem`/`ARLSTem2` and `WordNetLemmatizer` can be constructed (the WordNet one checks for the resource) but do not stem or lemmatize. The `WordNetLemmatizer` raises when WordNet is not visible, as specified. The Treebank tokenizer does not support spans.
- **Generation:** `generate` is depth-first. It does not terminate on a left-recursive grammar unless `depth` or `n` bounds it.
- **Decision tree:** ID3-style information gain with no pruning. It stops when no feature gives positive gain, so inseparable training examples may stay misclassified.
- **Naive Bayes:** add-one smoothing per feature value. Denominator = examples with the label that have the feature, plus the number of distinct values seen for that feature.

## Layout

- `lingora/` is the flat package. `data.py` is the resource finder (`data.path`, initially `$LINGORA_DATA` entries and `~/lingora_data`). `tokenize.py`, `stem.py`, `tag.py` (with `_perceptron.py`), `chunk.py`, `grammar.py`, `parse/` (with `parse/generate.py`), `tree.py`, `classify.py`, `metrics.py`, `translate.py`, `cli.py` (with `__main__.py`), and `_punkt.py`.
- The command-line group has no third-party dependencies. `lingora.cli.cli.main(args=[...], standalone_mode=...)` mirrors the Interface. Exit status is 0 on success, 1 when a sentence-splitting model is missing or tokenization fails, and 2 for usage errors.
- `pyproject.toml` declares a setuptools package with no runtime dependencies. Editable install: `pip install -e .`. Importing from `/app` also works with no install.
- `tests/test_lingora.py` contains 34 pytest tests. They fabricate Punkt and tagger resources in temporary directories, so no real packaged data is needed. Run with `python3 -m pytest -q tests`.
