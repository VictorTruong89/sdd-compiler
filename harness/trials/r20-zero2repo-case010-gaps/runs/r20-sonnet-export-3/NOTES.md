# NOTES

Layout: flat package `lingora/` (no build step; put `/app` on the import path). No third-party dependencies
(the CLI is a tiny click-compatible `Group` in `lingora/cli.py` because `click` is not installed).
Code is marked with `# spec:` comments in places; modules map to packs (tokenize=07/22, stem=09/23, tag=10/24,
chunk=11/25, grammar+parse=12/26, tree=13, classify=14/27, metrics+translate=15/28, data=06, cli=08).

## Checklist accounting
Every id in `spec/CHECKLIST.md` is covered by the modules above, except the items listed under
"Not done / partial". Meta-requirements (platform, Python version, non-goals, "outside this specification")
are satisfied by construction (pure Python, no network, no GUI/wrappers/corpora shipped).

## Not done / partial (reasons)
- **Snowball**: english (Porter2), porter, german, dutch, swedish, norwegian, danish, spanish, italian,
  portuguese, french, russian are implemented from the published algorithm descriptions (from memory, not
  verified against the reference vocabularies). **finnish, hungarian, romanian, arabic are only simplified
  suffix strippers**, not the real Snowball algorithms (time/size); their output will differ from Snowball.
- ARLSTem / ARLSTem2 are simple light stemmers (results are declared outside the spec, N-000136..139).
- `ne_chunk` raises when the model dir or `corpora/words` is not visible; when both are present it returns the
  tagged tokens under the root without entity grouping (results are declared outside the spec, N-000219).
- WordNetLemmatizer is a minimal morphy implementation over `index.*` / `*.exc` files in `corpora/wordnet`.
- Porter's "irregular forms" table is my own small table (entries are outside the spec, N-000147).

## Spec gaps / assumptions
- `data.path` initial contents (implementer's choice): `$LINGORA_DATA` entries, then `~/lingora_data`,
  `~/nltk_data`, `/usr/share/nltk_data`, ... when they exist. Resources are looked up only in `data.path`
  at call time; model caches are keyed by file mtime.
- Packaged resources are not in the repo (spec: non-goal); Punkt / perceptron / stopwords / WordNet code paths were
  tested against small synthetic resource trees only.
- Root label of chunk trees is `"S"` (N-000419/420 implementer's choice). Chunk children are `(token, tag)` tuples.
- Nonterminals are `lingora.grammar.Nonterminal` objects (`str()` gives the name); `Tree` labels from parsers are `str`.
- `generate(..., n=0)` behaves like `n=None` (unlimited), as `n` is only applied when truthy. Not stated in spec.
- `accuracy` on two empty lists raises `ValueError` (spec only defines different lengths). 
  `classify.accuracy` with empty gold raises `ValueError`.
- Naive Bayes smoothing: Lidstone (+0.5) on label priors and per-label feature-value counts, features absent from an
  example count as value `None`; features never seen in training are ignored at classification time.
- Decision tree: picks the feature whose stump has the fewest training errors (ties: first feature by sorted name)
  and recurses until pure; unseen feature values fall back to the node's majority label.
- Smoothing argument of `bleu` is `smoothing_function=` (callable `(p_n, references=, hypothesis=, hyp_len=)`);
  `lingora.translate.SmoothingFunction` offers `method0/1/2`. Unsmoothed zero precisions use `sys.float_info.min`
  (score "negligibly close to 0", N-000309).
- Tie-break for UnigramTagger: first-seen most frequent tag (N-000189 implementer's choice).
- Russian→universal tag table is my own (N-000207); unmapped tags -> `X`. English universal mapping with
  missing `en-ptb.map` raises `LookupError`.
- `blankline_tokenize` of a whitespace-only string returns `[]` (N-000129); other gap tokenizers keep PRD semantics
  (a whitespace-only text with a custom gap pattern returns the piece).
- Tweet tokenizer follows the well-known HANG-run rule (runs of 4+ identical punctuation chars are cut to 3) in
  addition to the PRD's `reduce_len` option; not stated in the PRD.
- `word_tokenize` PTB variant: commas/colons are split like the reference Treebank tokenizer even though the PRD
  lists only some punctuation.

## Disagreements inside the spec
- Pack 22 (FP-01) says the PTB tokenizer "splits at whitespace, then punctuation" and lists only some punctuation
  characters; Interface Contract pack 07 only gives signatures. I built the conventional regex-cascade PTB tokenizer.
- Pack 23 says the Porter lookup uses "the lowercased word"; I look up the lowercased form (not the raw word).
- Pack 05 says exception classes/messages are free; I used `LookupError` (missing resource), `TypeError`
  (wrong argument types), `ValueError` (bad values/coverage), `NotImplementedError` (unsupported pos_tag lang).
