# LINGORA build notes

The package is `/app/lingora/` (flat layout, pure Python, no dependencies). Import it from `/app`
(the judge runs with `/app` as the working directory). `pyproject.toml` is included for packaging; I did not run an install. `spec/` is unchanged.

Spec files are cited as `PRD` (`spec/Full_PRD.md`) and `IC` (`spec/Interface_Contract.md`).
Line numbers refer to those files.

## Conflicts between the specifications and what was built

Rule used: where the PRD defines what an entry computes, the PRD wins. The Interface Contract
wins for signatures and types. Where a conflict falls inside a single file, the choice is named.

### 1. Porter lowercasing default
- PRD FP-02, line 155: "The word is lowercased first, unless the caller turns lowercasing off."
  This makes lowercasing the default.
- IC line 99: "`to_lowercase` defaults to `False`, so `stem` keeps the letter case it is given."
- **Built:** `PorterStemmer().stem(word, to_lowercase=True)`. Lowercasing is the default, as in the PRD.
  `to_lowercase=False` keeps the case.

### 2. Porter Step 1a on "ties"
- PRD FP-02, line 158: "a four-letter word ending in *-ies* becomes *-ie* rather than *-i*".
- IC line 99: "`PorterStemmer` applies Step 1a as published, so *ties* stems to *ti*."
- **Built:** `ties` → `tie` (the PRD's LINGORA extension, which is also the default mode per PRD line 148).
  The original mode (`PorterStemmer("original")`) gives `ti`, which matches the IC example.

### 3. Edit distance with transpositions
- PRD FP-07, line 303: the distance is "the unrestricted Damerau–Levenshtein distance (Lowrance and Wagner, 1975)".
- IC line 235: only adjacent characters may be transposed, "and nothing may be inserted or deleted between them"
  (the restricted, optimal-string-alignment form).
- **Built:** the unrestricted form, as the PRD defines it. Example: `edit_distance("ca", "abc", transpositions=True)` is 2,
  where the restricted form gives 3.

### 4. BLEU default weights
- PRD FP-07, line 312: "The default is equal weights on unigrams through 4-grams."
- IC line 242: "When `weights` is omitted, unigrams and bigrams are weighted equally and longer n-grams are not scored."
- **Built:** 0.25 on each of unigrams through 4-grams (the PRD default).

### 5. Accuracy on lists of different lengths
- PRD FP-07, line 306: "For lists of different lengths, it is that fraction over the positions both lists have."
- PRD FP-07, line 319 and FP-06, line 288: lists of different lengths "does not succeed".
- IC line 231: "Lists of different lengths make it raise."
- **Built:** `ValueError`. The boundary text and the Interface agree, so the normal-behaviour sentence was not followed.

### 6. Touching chunks from one chunk rule
- PRD FP-04, line 222, one paragraph, two sentences: "Two matches that touch are two separate chunks."
  and "Chunks that touch, with no token between them, are joined into one chunk."
- **Built:** touching matches from one rule stay separate chunks (the first sentence). The "joined" sentence was not
  implemented, because the two cannot both hold.

### 7. Cascaded clauses and earlier chunks
- PRD FP-04, line 222: "Every match of the pattern among tokens not yet in a chunk."
- PRD FP-04, line 224: a later clause "sees every chunk built by an earlier clause as a single unit whose tag is that
  chunk's label, so it can chunk the remaining tokens but cannot chink inside an earlier clause's chunks."
- **Built:** a chunk from an earlier clause is a unit whose tag is its label, so a later pattern can include it
  (`VP: {<VBD><NP>}` after `NP: ...` works). Chunks from the same clause are barriers for that clause's chunk rules.
  Chinking is limited to chunks from the same clause.

### 8. Other points the specifications leave open (implementer's choice, recorded here)
- `word_tokenize(..., preserve_line=...)` has no stated default. Built: `preserve_line=False` (split sentences first),
  as PRD FP-01 line 114 describes.
- `accuracy([], [])` and classifier `accuracy` on an empty gold list return `0.0`. Not specified.
- `jaccard_distance(set(), set())` returns `0.0`. Not specified.
- The default `data.path` is the `LINGORA_DATA` environment variable (`os.pathsep` separated), and is empty when unset.
- The Russian universal mapping is a table I wrote (PRD FP-03 line 202 leaves it to the implementer).
- `RegexpParser` accepts a grammar string, or a list of `ChunkRule`/`ChinRule` objects.
- Shift-reduce parsing reduces an empty production at most once per input position, and has a step budget. Without these
  limits, empty productions could loop forever.

## Not complete

These are in the specification and are either missing or partial in this build:

- **Snowball:** only `english` (Porter2) and `porter` (original Porter) are implemented. The other listed languages raise
  `NotImplementedError` that names the language. Unknown names raise `ValueError` that names the language.
- **Lancaster (Paice/Husk):** the engine is complete, but the rule table holds only a few rules
  (`_LANCASTER_RULES` in `lingora/stem.py`). I could not reproduce the full published table from memory. Stems of most words
  will differ from the published algorithm until the table is completed.
- **Punkt sentence splitting:** implements the decision structure (abbreviations, collocations, sentence starters,
  orthographic context) in simplified form. It is not verified against the published Punkt output.
- **Averaged perceptron tagger:** implements the greedy averaged perceptron with NLTK-style features. It reads the packaged
  weights, tag dictionary and classes. Its output depends entirely on the packaged model, which I could only test with a
  tiny fake model.
- **WordNet lemmatizer, named-entity chunker (`ne_chunk`), ARLSTem, ARLSTem2:** these are outside the feature points and
  are not implemented. `ne_chunk` and `WordNetLemmatizer` raise `LookupError` when their resources are missing, as the
  spec requires. When the resources are present, they raise `NotImplementedError`.
- **Recommended tokenizer and `tokenize` command:** these need the Punkt model for English. Nothing was tested against a real
  Punkt model; the tests used a small fixture I wrote myself.
- **Other tagger families** (bigram, trigram, affix) are included as extras and are lightly tested.

## Verified in this environment

Checked with ad-hoc scripts outside `/app` (not included in the repository):
word/punctuation, Penn Treebank, recommended, whitespace, blank-line, regexp and tweet tokenizers; spans; empty input;
Porter (three modes), Porter2, regexp stemmer; Levenshtein, Damerau–Levenshtein, Jaccard, accuracy, precision, recall,
f-measure, BLEU; CFG reading, chart and shift-reduce parsing, generation; tree construction, equality, leaves, pformat,
bracketed-text reading; chunk grammars (chunk, chink, cascading); the default, unigram and regexp taggers; perceptron
tagging with a fixture model; Naive Bayes and decision tree classifiers; the CLI (`python -m lingora tokenize`), including the
failure when the Punkt model is missing.
