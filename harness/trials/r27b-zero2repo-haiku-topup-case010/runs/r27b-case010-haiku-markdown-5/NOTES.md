# LINGORA build notes

Implementation: `/app/lingora` (flat package, pure Python, no third-party dependencies).
Spec files in `spec/` are unchanged. Locations below use `PRD` = `spec/Full_PRD.md` and
`IC` = `spec/Interface_Contract.md` (line numbers from those files).

## 1. Conflicts between the specification documents

For each conflict: what each side says, and what was built.

**C1. Porter `to_lowercase` default**
- PRD FP-02, "Porter, default mode", line 155: "The word is lowercased first, unless the caller turns lowercasing off."
  (default: lowercase).
- IC "Stemmers", line 99: "`to_lowercase` defaults to `False`, so `stem` keeps the letter case it is given."
- **Built:** default `to_lowercase=False` (the Interface signature default governs the call signature).

**C2. Porter stemming of *ties***
- IC line 99: "`PorterStemmer` applies Step 1a as published, so *ties* stems to *ti*."
- PRD FP-02 line 158: LINGORA extension, "In Step 1a, a four-letter word ending in *-ies* becomes *-ie* rather than *-i*."
- **Built:** the default (LINGORA) mode follows the PRD extension, so `ties → tie`. The `original` mode gives `ties → ti`.
  The IC example would hold only in `original` mode.

**C3. Edit-distance transpositions**
- PRD FP-07 line 303: unrestricted Damerau–Levenshtein; insertion/deletion between the transposed characters is allowed.
- IC line 235: only adjacent characters may be transposed, and nothing may be inserted or deleted between them.
- **Built:** the PRD definition (unrestricted, Lowrance–Wagner). `edit_distance("ca", "abc", transpositions=True) == 2`.

**C4. BLEU default weights**
- PRD FP-07 line 312: "The default is equal weights on unigrams through 4-grams."
- IC line 242: when `weights` is omitted, "unigrams and bigrams are weighted equally and longer n-grams are not scored."
- **Built:** the IC default, `weights=(0.5, 0.5)`.

**C5. `RegexpTokenizer` empty-piece discarding default**
- PRD FP-01 line 120: "Empty pieces are dropped unless the caller turns empty-discarding off (it is on by default)."
- IC line 66: "`discard_empty` is off unless the caller passes `discard_empty=True`."
- **Built:** off by default (IC).

**C6. Accuracy on lists of unequal length**
- PRD FP-07 line 306: "For lists of different lengths, it is that fraction over the positions both lists have."
- PRD FP-07 line 319 and FP-06 line 288, and IC line 231: lists of different lengths make it fail (raise).
- **Built:** raises `ValueError` (two of the three statements, including the boundary section and the IC, agree).

**C7. Chunk joining**
- PRD FP-04 line 222: "Every match ... Two matches that touch are two separate chunks. ... Chunks that touch, with no token between them, are joined into one chunk."
- **Built (interpretation):** matches produced by one chunk rule stay separate. A new chunk that touches an existing chunk of the same clause (from an earlier rule of that clause) is joined to it. Chunks of different clauses are never joined.

## 2. Choices where the spec leaves room

- **Packaged data path:** `lingora.data.path` starts with the directories in `LINGORA_DATA` (os.pathsep separated), then `~/lingora_data`. No data is shipped.
- **Punkt:** only the sentence-annotation half of Kiss & Strunk is implemented, using the packaged parameters (`abbrev_types.txt`, `sent_starters.txt`, `collocations.tab`, `ortho_context.tab`). Missing individual files count as empty; a missing model directory raises `ResourceNotFoundError`.
- **Averaged perceptron (`eng`, `rus`):** feature templates, normalisation and START/END context follow the textblob-aptagger/NLTK formulation. Universal mapping for English uses `en-ptb.map`. The Russian RNC→universal table is my own choice; the part before `=` and before the first comma gives the POS.
- **Naive Bayes:** expected-likelihood smoothing (add 1/2 per value, bins = values seen for that feature); MLE label priors; unseen feature names ignored.
- **Decision tree:** ID3 (information gain). Ties broken by feature name (sorted by `repr`) and first-seen label. Absent features are the `None` branch. Unseen values fall back to the node's majority label.
- **Accuracy on empty lists** (`metrics.accuracy`, `classify.accuracy`): returns `0.0`.
- **Chunk root label:** `S`.
- **Tree formatting:** `pformat()` writes a single-line bracketed form; tuple leaves print as `token/tag`.
- **CLI:** no `click` available, so `cli` is a small command group with `main(args=..., standalone_mode=...)`. Options: `-l/--language` (default `english`), `-d/--delimiter` (default one space), `-e/--encoding` (default utf-8). A missing Punkt model fails with status 1 before any output.
- **Chart parser:** Earley-style memoized span parser; a re-entry on the same (symbol, span) is cut. This can miss trees only for cyclic grammars.
- **Shift-reduce parser:** single greedy pass, reduce-before-shift, empty productions not used for reduction.
- **Generator:** derivations are enumerated in increasing tree depth (iterative deepening), in written production order. A `depth` bound and `n` bound are honoured. With neither bound, an infinite language is enumerated forever.

## 3. Known gaps (not implemented, or approximate)

- **Snowball:** `english` (Porter2) and `porter` (original Porter) are implemented. The other listed languages (arabic, danish, dutch, finnish, french, german, hungarian, italian, norwegian, portuguese, romanian, russian, spanish, swedish) raise `NotImplementedError` naming the language. Stopword-list checks still apply first.
- **Lancaster:** the Paice/Husk engine is implemented, but the rule table is a partial reconstruction (11 rules), not the published table. Results will differ from the published stemmer for many words.
- **ARLSTem / ARLSTem2:** approximate light stemmers, not the published algorithms.
- **Named-entity chunker (`ne_chunk`):** checks that the NE model and English wordlist are visible (raises otherwise), but does not load the MaxEnt model. It chunks runs of NNP/NNPS as `NE`.
- **WordNet lemmatizer:** suffix rules checked against the packaged `index.*` files; not full morphy.
- **Porter2 (english):** implemented from the Snowball region definitions (R1/R2 fixed before step 0, `commun`/`gener`/`arsen` special prefixes). Examples: `communism → communism`, `happiness → happiness`, `hopefulness → hopeful`, `happily → happili`. These follow the algorithm as written; they were not checked against a reference output.
- **Not implemented, outside the stated feature points:** RSLP, ISRI, Cistem, the WordNet-based corpora, the data downloader, the s-expression tokenizer.

## 4. Verification done

Checked with ad-hoc scripts (not committed):
- Porter (`original` mode): all 70 example words match the outputs I recall from Porter's published examples (checked from memory, not from a reference file).
- Snowball `english`: sample words (running→run, generalization→general, generously→generous, cries→cri, ties→tie, skies→sky, dying→die, succeed unchanged, etc.) match.
- Penn/recommended word tokenizers, Punkt splitting (with a small hand-written model in `/tmp`), Tweet and regex tokenizers, perceptron tagging (with a tiny fake model), chunking (including chink and cascading clauses), CFG reading, chart/shift-reduce parsing, generation, trees, Naive Bayes, decision tree, metrics (Levenshtein, Damerau, Jaccard, P/R/F), BLEU, and the CLI (stdin, delimiter, missing-model failure).
- Not verified against real packaged Punkt, perceptron, or WordNet resources (none are installed in this environment).
