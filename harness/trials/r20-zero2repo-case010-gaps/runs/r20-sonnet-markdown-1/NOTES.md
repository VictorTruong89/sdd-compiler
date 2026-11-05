# NOTES

Pure-Python package `lingora` at `/app/lingora` (no install step; run from `/app`). No third-party dependencies.

## Disagreements between spec parts
- **CLI framework**: Interface_Contract describes `cli.main(args=..., standalone_mode=True)` (click-style); `click` is not installed and no installs are allowed. I built a small dependency-free `cli` object with the same `main(args, standalone_mode)` behaviour (SystemExit 0 on success, 1 on failure; with `standalone_mode=False` errors are raised).
- **Runtime dependencies**: PRD says "small set of pure-Python packages"; Hardware_Requirements says the same; I used none.
- **Treebank punctuation**: PRD lists `; @ # $ % & ? !` as split characters but does not mention `:` and `,`; I followed the Penn Treebank convention (split `:`/`,` unless between digits), as the PRD says it "follows the Penn Treebank conventions".

## Not stated in the spec (my assumptions)
- Default `data.path` (initial contents): `$LINGORA_DATA` entries, `~/lingora_data`, `/usr/share/lingora_data`, `/usr/local/share/lingora_data`, `/app/lingora_data`. Contract leaves this to me.
- `generate(..., n=0)` yields nothing (n is a maximum); `n=None` = unlimited. Default depth unbounded; infinitely recursive grammars raise `RuntimeError` on recursion exhaustion.
- `accuracy` (metrics and classify) on empty lists raises `ZeroDivisionError` (spec silent). `jaccard_distance` of two empty sets returns 0.0 (spec silent).
- `ne_chunk`: raises when the model or wordlist is not visible; when they are present it raises `NotImplementedError` (results explicitly outside the spec).
- Naive Bayes uses expected-likelihood (+0.5) smoothing; ties between labels go to the first label seen in training. Decision tree uses a best-stump-per-node (lowest training error) with entropy cutoff 0.05, support cutoff 10, depth cutoff 100; a feature absent counts as value `None`.
- Unigram tagger ties: first-seen most frequent tag.
- Chunk grammar: only chunk `{}` and chink `}{` rules are implemented; root label is `S`. Comments (`#`) are stripped.
- Chart parser given an empty-string terminal (`''`) matches zero tokens and adds no leaf. Parsing with unary cycles ignores cyclic derivations. Coverage failure raises `ValueError` from the `parse` call itself.
- BLEU smoothing argument is `smoothing_function` (callable `(p_n, references, hypothesis, hyp_len) -> p_n`; `SmoothingFunction` class provided).
- Universal tag mapping for Russian: my own table by RNC part-of-speech (S→NOUN, V→VERB, A→ADJ, ADV→ADV, NUM→NUM, ANUM→ADJ, SPRO→PRON, APRO→DET, ADVPRO→ADV, PR→ADP, CONJ→CONJ, PART→PRT, others→X). English tags not in `en-ptb.map` become `X`.
- Punkt model is re-read when its files change (cache keyed on mtimes); paragraph/line-start flags of the original Punkt tokenizer are not used (only matter for training).

## Known limitations
- Snowball: English (Porter2), porter, German, Dutch, Spanish, French, Swedish, Norwegian, Danish and Russian are implemented from the published algorithm descriptions (compact versions, only spot-checked). **Arabic, Finnish, Hungarian, Italian, Portuguese and Romanian are accepted as language names but only lowercase the word** (no stemming) — not implemented.
- ISRI, ARLSTem, ARLSTem2, Cistem, RSLP and WordNetLemmatizer are placeholders (outside the spec); the lemmatizer/RSLP raise when their resource is not visible.
- Bigram/trigram/affix taggers are simple implementations of the train-then-tag protocol.
