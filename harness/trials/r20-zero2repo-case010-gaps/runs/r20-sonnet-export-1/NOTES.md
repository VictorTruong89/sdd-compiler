# NOTES

Layout: flat package `/app/lingora` (no build step; put `/app` on the import path).
Modules: data, tokenize, stem, tag, chunk, grammar, parse (+ parse.generate), tree,
classify, metrics, translate, cli. Code is marked with `# spec: N-…` ids. Tests: `tests/`.

## Spec disagreements
No unsettled contradictions are listed in `MAP.md`. Minor tensions I resolved:
- PRD FP-01 describes the Treebank tokenizer without typographic quotes/`*`/dashes, and the
  "recommended" tokenizer with them (pack 22). I built two separate tokenizer classes
  (`TreebankWordTokenizer`, internal `NLTKWordTokenizer` used by `word_tokenize`).
- Interface Contract says command options (language, delimiter, encoding) are the implementer's
  choice (N-000388); I provide `-l/--language`, `-d/--delimiter`, `-e/--encoding`.
- Pack 19 says "runtime dependencies are pure-Python packages"; the CLI is self-contained
  (the contract's `cli.main(args=…, standalone_mode=True)` mimics click but click is not required).

## Not stated in the spec (assumed)
- Initial `data.path`: `$LINGORA_DATA` entries (os.pathsep separated) plus `~/lingora_data`.
  No data ships in the tree, so Punkt/tagger/etc. need `data.path` set by the caller.
- `accuracy` / `classify.accuracy` of empty lists: return 0.0. `jaccard_distance` of two empty
  sets: 0.0. `bleu` with empty hypothesis: 0. `bleu` smoothing argument: `smoothing_function`,
  a callable `(list_of_Fractions, references=, hypothesis=, hyp_len=) -> list of numbers`.
- Resource-missing errors raise `LookupError`; bad types raise `TypeError`; bad values `ValueError`.
- Root chunk label is `"S"`. Parse/chunk trees use `str` labels; grammar nonterminals are
  `Nonterminal` objects (not `str`, `str()` = name, `==` also accepts a `str`).
- Quoted empty terminal `''` consumes no token in the parsers (it yields `''` only in `generate`).
- Unigram tie-break: first-seen tag. Russian→universal table: my own (`tag._RNC_TO_UNIVERSAL`).
- Missing universal tables for English with `tagset='universal'`: the call raises.
- NLTK-style options not in the spec (Porter modes, Lancaster prefix stripping etc.) exist but are lightly tested.

## Known limits / not done
- Snowball: only `english` (Porter2) and `porter` (original Porter) are faithful ports. The other
  languages in the allowed list construct fine but use a crude suffix-stripper; real Snowball
  algorithms for them were not ported (spec N-000163 is only partly met).
- Lancaster rule table and Porter irregular table were written from memory of the published
  algorithm; not verified against a reference.
- `ne_chunk`: checks that the model directory and `corpora/words` are visible (raises otherwise);
  the model format is unspecified, so with resources present it returns a flat tree without entities.
- ARLSTem/ARLSTem2 are simple light stemmers (results out of spec). `WordNetLemmatizer` raises
  `LookupError` when `corpora/wordnet` is missing; with data it uses a small morphy approximation.
- Tweet tokenizer regexes are a close but not exact reproduction of the usual ones.
- Items in the checklist about non-goals / outside-spec surfaces (GUIs, corpora, downloaders,
  wrappers, CCG, etc.) are intentionally not implemented.
