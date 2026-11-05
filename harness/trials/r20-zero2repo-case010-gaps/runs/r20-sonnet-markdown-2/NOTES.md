# NOTES

Layout: package `lingora/` at the repo root (flat layout, pure Python, no dependencies, no build step).
Command line: `python -m lingora tokenize` or `lingora.cli.cli.main(args=[...])`. `click` is not
installed, so `lingora.cli.cli` is a small click-compatible shim (`main(args, standalone_mode)`).

## Disagreements / choices between spec parts
- PRD FP-02 lists ISRI, Cistem, RSLP stemmers as existing; the Interface Contract exports only
  ARLSTem, ARLSTem2, Lancaster, Porter, Regexp, Snowball, WordNetLemmatizer. I built the Contract's list only.
- PRD says recursive-descent parser "exists"; the Contract lists only ChartParser and ShiftReduceParser.
  I added `RecursiveDescentParser` in `lingora.parse` as an extra.
- PRD FP-06 says "Two-list accuracy (FP-07)" in the classifier section; both `lingora.classify.accuracy`
  (classifier, gold) and `lingora.metrics.accuracy` (two lists) exist, as the Contract says.
- Hardware doc says "editable install ... or project root on import path": I provide `pyproject.toml`
  but nothing needs installing.

## Not stated by the spec (assumptions)
- Initial contents of `data.path`: `$LINGORA_DATA` entries, `<repo>/lingora_data`, `~/lingora_data`.
- Missing resources raise `LookupError`; wrong `lang` raises `NotImplementedError`; str tokens to `pos_tag`
  raise `TypeError`; unknown `tagset` raises `ValueError`.
- Unigram tag ties: the tag seen first in training wins.
- `accuracy`/`jaccard_distance` on empty input raise `ZeroDivisionError` (undefined, not 0).
- `generate(n=0)` yields nothing (n is a maximum); `n=None` is unlimited. Default depth is 100000.
- A quoted empty terminal `""` matches an empty span in parsers and adds no leaf; shift-reduce ignores
  empty productions.
- Tweet tokenizer: URL/emoticon/phone regexes are my own simplified versions; HTML entities are not unescaped.
- Russian universal tag mapping table is my own (part of speech before `=`; unknown -> `X`).
- The CLI options are `--language/-l`, `--delimiter/-d`, `--encoding/-e`. The Punkt model is loaded before any
  output, so a missing model gives exit status 1 and no token lines. Usage errors exit with 2.
- `RegexpTokenizer` token mode uses the whole match (group 0) even when the pattern has groups.
- `ne_chunk`: raises if the model dir or `corpora/words` is not visible; when both are present the model
  format is not interpreted (spec says results are out of scope) and a flat tree of the input is returned.
- Sentence tokenizer treats `?`/`!` per Punkt reference behaviour; `NonWord` punctuation set follows the original Punkt.

## Known limitations
- Snowball: full ports exist for english, porter, german, dutch, swedish, norwegian, danish, spanish, russian
  (from memory of the Snowball definitions; not verified against reference output). french, italian,
  portuguese, finnish, hungarian, romanian use a light generic suffix stripper (NOT the real Snowball
  algorithms), and arabic uses the ARLSTem-like light stemmer.
- ARLSTem/ARLSTem2 are simplified light stemmers (spec leaves their results out of scope).
- Lancaster rules and Porter extensions were written from memory of the published algorithms.
