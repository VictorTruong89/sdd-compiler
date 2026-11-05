# NOTES

Pure-Python package `lingora` at `/app/lingora` (no build step; put `/app` on the import path).

## Spec disagreements / choices
- **Punkt files vs. "packaged" naming**: the PRD speaks of Punkt "models"; the Interface Contract defines the
  on-disk layout (`tokenizers/punkt_tab/<lang>/` with four text files). I implemented the Punkt algorithm
  (Kiss & Strunk, as in the usual reference implementation) reading exactly those files. A missing directory or
  missing file raises (`LookupError` / `FileNotFoundError`).
- **Edit distance with transpositions**: PRD says unrestricted Damerau–Levenshtein (Lowrance–Wagner); I implemented
  that (not the restricted/optimal-string-alignment variant).
- **`ChartParser` vs. token coverage**: PRD says an uncovered token "does not succeed", Contract says "raised by the
  call or by first iteration". I raise `ValueError` eagerly from `parse()`.
- **`CFG` symbols**: the Contract allows `str` or a symbol object; nonterminals are `lingora.grammar.Nonterminal`
  objects (not `str`), terminals are `str`.
- **Snowball `porter`**: PRD lists `porter` as a Snowball language without defining it; I used the original
  (unextended) Porter algorithm. Stopword file for `porter` is read from `corpora/stopwords/porter`, as the
  Contract says the file name is the Snowball language name.

## Unstated details I assumed
- Default `data.path`: `$LINGORA_DATA`, `~/lingora_data`, `/usr/share/lingora_data`, `/usr/local/share/lingora_data`,
  and nltk_data-style dirs. Callers replace it in place.
- `accuracy([], [])` raises `ZeroDivisionError`; `jaccard_distance(set(), set())` returns `0.0` (nothing stated).
- `bleu` default weights (0.25,)*4; smoothing via `smoothing_function=` keyword (callable
  `(p_n, references, hypothesis, hyp_len)`; `lingora.translate.SmoothingFunction` has `method0..method3`).
  `p_n` is a list of `(numerator, denominator)` pairs.
- Quoted empty string `''` in a parsed grammar consumes no token and produces no child; in `generate` it yields `''`.
- Shift-reduce ignores empty productions when reducing.
- Decision tree defaults: entropy cutoff 0.05, depth cutoff 100, support cutoff 10; ties in majority label go to the
  first label seen. Naive Bayes uses expected-likelihood (+0.5) smoothing.
- Tweet tokenizer's URL/phone/emoticon patterns are my own approximation of the common patterns.
- Chunk grammar supports only chunk `{}` and chink `}{` rules (as the spec); root label is `S`.
- Tag `None` for untagged tokens; `pos_tag(tagset='universal')` for English raises `LookupError` if the tables are
  missing; unknown PTB tags map to `X`.
- CLI: `lingora tokenize [-l LANG] [-d DELIM] [-e ENC]`, built without third-party deps (a minimal command group
  with `main(args=…, standalone_mode=…)`). The Punkt model is checked before anything is read/written; failure exits 1.

## Not (fully) implemented
- Snowball: English, Porter, German, Dutch (original), Swedish, Norwegian, Danish, Spanish, Russian are implemented.
  **French, Italian, Portuguese, Romanian, Finnish, Hungarian, Arabic** are accepted as language names but currently
  return the lowercased word unchanged (not implemented).
- ISRI/ARLSTem/ARLSTem2/Cistem/RSLP: stubs (outside the specified behaviour). `WordNetLemmatizer` only checks for
  the resource and returns the word unchanged.
- `ne_chunk` checks for its resources (raises if missing) and otherwise raises `NotImplementedError`.
- Lancaster rule table and the tweet regexes were written from memory; small deviations are possible.
