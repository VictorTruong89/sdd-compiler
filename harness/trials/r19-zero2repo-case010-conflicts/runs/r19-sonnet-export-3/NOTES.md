# Implementation notes

Layout: flat package `lingora/` at `/app` (no build step; put `/app` on the import path).
No runtime dependencies. The CLI (`lingora.cli.cli`, `cli.main(args=[...], standalone_mode=...)`) is a small
click-compatible group written in-repo because no third-party package is available.

Packaged models (Punkt, perceptron taggers, universal tagset, NE chunker, stopwords, WordNet) are never
shipped (spec non-goal); they are read from the directories in `lingora.data.path` (mutable list; initial
contents: `$LINGORA_DATA` entries, `~/lingora_data`, `/usr/share/lingora_data`, `/usr/local/share/lingora_data`).
A missing resource raises `LookupError` (or `TypeError`/`ValueError` for bad arguments).

## Conflicts between spec parts, and what was built
Rule used: the Interface Contract (pack 05-15) is the testable surface, so it wins over the PRD where they differ.

* CF-000001 PRD N-000094 "straight double quote at the start of the text" -> opening quote (``), vs N-000106 recommended tokenizer
  "straight double quote at the very start becomes the closing-quote token". Built: `TreebankWordTokenizer` gives ``;
  `word_tokenize`/`NLTKWordTokenizer` gives the closing `''`.
* CF-000054 N-000067 "tweet tokenizer lowercases its tokens unless preserve case" vs N-000125 "lowercased, except emoticons".
  Built: emoticons keep their case.
* CF-000077 N-000118 "empty-discarding is on by default" vs Contract N-000407 "`discard_empty` is off unless True".
  Built: `RegexpTokenizer(discard_empty=False)` default. Whitespace/blank-line tokenizers always discard empty pieces.
* CF-000083 N-000102 "*cannot* is split into two parts" vs N-000110 "*cannot* is kept as one token (recommended tokenizer)".
  Built: Treebank tokenizer splits (`can` `not`); recommended `word_tokenize` keeps `cannot`.
* CF-000073 N-000158 "four-letter word ending in -ies becomes -ie" vs Contract N-000424 "Step 1a as published, *ties* -> *ti*".
  Built: `ties` -> `ti` (published Step 1a). The *-ied* rule of Step 1b (four letters -> -ie, else -i) is kept.
* CF-000091 N-000154 "word is lowercased first unless caller turns it off" vs Contract N-000426 "`to_lowercase` defaults to False".
  Built: `PorterStemmer.stem(word, to_lowercase=False)`; with True the word is lowercased first.
* CF-000028 N-000240 "two touching matches are two separate chunks" vs N-000242 "chunks that touch are joined into one".
  Built: touching matches stay separate chunks (regex chunk-string semantics).
* CF-000088 N-000282 "a string in place of the child list is a single leaf" vs N-000288 "a string as child list is refused".
  Built: `Tree('S', 'abc')` raises `TypeError`; omitting children raises `TypeError`.
* CF-000089 N-000279 "quoted empty string contributes an empty-string token" vs Contract N-000480 "adds no token".
  Built: `generate` adds no token for an empty-string terminal.
* CF-000090 N-000267 "token no production produces -> no trees" vs N-000292 / Contract N-000475 "raises".
  Built: parsers raise `ValueError` for such a token (at the `parse` call); underivable-but-covered lists give an empty iterator.
* CF-000008, CF-000039, CF-000072 PRD "accuracy over shared positions for different lengths" vs N-000318/N-000343/N-000502 "raises".
  Built: `metrics.accuracy` raises `ValueError` on different lengths.
* CF-000016, CF-000055, CF-000070 PRD "unrestricted Damerau-Levenshtein" vs Contract N-000505/N-000506 "only adjacent transposition,
  nothing inserted/deleted between". Built: restricted (optimal-string-alignment) transposition; `edit_distance('ca','abc',transpositions=True)==3`.
* CF-000038 N-000334 "f-measure is 0 when precision or recall is 0" vs N-000346 "no number when sets share no element".
  Built: `f_measure` returns `None` for disjoint sets (and when either set is empty).
* CF-000086 N-000332 "list or tuple is read as a set" vs N-000345/N-000509 "non-set collections refused".
  Built: `precision`/`recall`/`f_measure` raise `TypeError` for non-set arguments.
* CF-000087 N-000338 "default BLEU weights are 1..4-grams equal" vs Contract N-000515 "unigrams and bigrams only".
  Built: default `weights=(0.5, 0.5)`. Smoothing argument: `smoothing_function=` (callable `(p_n, references=, hypothesis=, hyp_len=)`; see `SmoothingFunction`).

## Known limits (results declared outside the specification, or not recoverable without the data)
* Snowball: English (Porter2), `porter`, German, Dutch, Swedish, Danish, Norwegian are implemented. The other listed languages
  (arabic, finnish, french, hungarian, italian, portuguese, romanian, russian, spanish) are accepted but only lowercase the word
  (stemming algorithms not implemented). Stopword skipping works for all names.
* ARLSTem/ARLSTem2 are light approximations; ISRI/Cistem/RSLP are not provided (results outside the spec).
* Porter's other two modes, bigram/trigram/affix taggers, recursive-descent parser exist or are omitted as noted; not specified.
* `ne_chunk` checks the NE model directory and wordlist (raising `LookupError` if absent) and then groups proper-noun runs;
  the maxent model itself is not evaluated (results outside spec). `WordNetLemmatizer` does a light morphy over `index.*`/`*.exc`.
* Russian universal tagset mapping uses an implementer-chosen table (N-000218).
* Unigram tie-break: most frequent tag, ties to the one seen first (N-000200).

## Checklist accounting
All claim ids in `spec/CHECKLIST.md` are covered by the modules above: data (N-000385..402), tokenize (N-000081..139, 403..413),
cli (414..420), stem (140..186, 421..432), tag (187..227, 433..445), chunk (228..257, 446..460), grammar/parse (258..294, 461..480),
tree (281..291, 481..491), classify (295..318, 492..497), metrics/translate (319..348, 498..517), constraints (pure Python, no deps,
Python >= 3.10, nothing downloaded on import: 1..80, 353..384). Non-goals (N-000072..80, 349..352) are deliberately not built.
