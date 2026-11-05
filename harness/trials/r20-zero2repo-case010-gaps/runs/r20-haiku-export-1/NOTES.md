# NOTES — LINGORA build

Scope: the spec under `spec/` (29 packs, 477 checklist ids). The library is in
`/app/lingora/`, tests in `/app/tests/` (57 passing, `python3 -m pytest -q tests`).
No network was used. No hidden tests were looked for. The packaged models
(Punkt, averaged perceptron tagger, WordNet, stopwords) are not in this
repository, so every code path that reads them was exercised against small
fixture files written by `tests/conftest.py`, not against the real models.

## Layout

| Module | Covers |
|---|---|
| `lingora/data.py` | `data.path`, resource lookup (`find`, `is_visible`) |
| `lingora/tokenize.py`, `lingora/_punkt.py` | word/punct, Treebank, recommended word tokenizer, whitespace, blank-line, regexp, tweet, spans; Punkt sentence splitter |
| `lingora/stem.py` | Porter (3 modes), Lancaster (partial table), Snowball English (Porter2), Snowball `porter`, regexp stemmer, WordNet lemmatizer (resource gate), ARLSTem/ARLSTem2 (stubs) |
| `lingora/tag.py` | default / unigram / regexp taggers with backoff; averaged-perceptron `pos_tag` (eng, rus; universal tagset) |
| `lingora/chunk.py` | `RegexpParser` (chunk and chink rules, cascading), `ne_chunk` (resource gate only) |
| `lingora/grammar.py`, `lingora/parse/` | CFG reader; `ChartParser` (all trees); `ShiftReduceParser`; `generate` |
| `lingora/tree.py` | `Tree`: construct, `fromstring`, `label`, `leaves`, `pformat`, `==`, iteration |
| `lingora/classify.py` | Naive Bayes (+ `prob_classify`), decision tree, `accuracy` |
| `lingora/metrics.py`, `lingora/translate.py` | edit distance (incl. unrestricted Damerau–Levenshtein), Jaccard, accuracy, precision, recall, f-measure, BLEU |
| `lingora/cli.py` | `cli.main(args, standalone_mode)`; `tokenize` command |

## Spec disagreements (and what I built)

1. **Leaf type of a tree.** `pack 13` (N-000257, N-000447): "a child is a token
   string (a leaf) or a tree", `leaves() -> list[str]`. `pack 11` (N-000421,
   N-000422): chunk children are "the input `(token, tag)` pairs". Built:
   `Tree` accepts any leaf object. Chunk trees from `RegexpParser` carry
   `(token, tag)` tuples as leaves, so `leaves()` returns tuples for them.
   `Tree.fromstring` gives `str` leaves.

2. **Which tokens a chunk rule may match.** `pack 25` (N-000223): "every match
   of the pattern among tokens not yet in a chunk becomes one chunk". Also
   `pack 25` (N-000230–N-000233) and `pack 17` ("Chunk grammar ... later
   clauses may cascade"): "a later clause sees every chunk built by an earlier
   clause as a single unit whose tag is that chunk's label". Built: an earlier
   clause's chunk is a unit with tag = its label, and later chunk rules may
   match it (cascade, as in the classic NP/PP/VP example). Chunks built by the
   *same* clause are never matched by that clause's chunk rules. Chink rules
   act only on the same clause's chunks, as the spec says.

3. **Root label of chunk output.** `pack 11` (N-000420): spelling is the
   implementer's choice. `pack 25` (N-000217): the root label "is the same for
   every parser and differs from clause labels". Built: `SENT`
   (`lingora/chunk.py`, `ROOT_LABEL`), chosen so it cannot collide with an
   ordinary clause label such as `S`.

4. **Alternatives on one grammar line.** `pack 12` (N-000427): "one production
   per line". `pack 26` (N-000240): "each alternative separated by `|` is a
   production of its own". Built: a line may hold several alternatives; each
   becomes its own `Production`.

## Gaps: what the spec does not state, and my assumption

- **Treebank commas and colons.** `pack 22` (N-000089–N-000098) lists which
  characters split off, and does not mention `,` or `:`. It also says the
  tokenizer follows Penn Treebank conventions, which split them. Built: `,`
  and `:` split off unless between digits. The recommended tokenizer adds the
  extras listed in N-000099–N-000103.
- **Punkt decision details** (N-000122–N-000126). Built from Kiss & Strunk and
  the usual implementation: chunks ending in `.` are abbreviations when the
  type is in `abbrev_types`; second-pass evidence comes from collocations,
  the orthographic heuristic (`ortho_context` bits, capitalised word seen in
  lower case and never capitalised mid-sentence = sentence starter), and
  `sent_starters`; initials and numbers followed by a non-starter are not
  breaks; closing quotes or brackets at the start of the next chunk move to the
  previous sentence. Real models were not available to check this.
- **Perceptron feature templates** (N-000196–N-000201). Built from the usual
  greedy averaged-perceptron templates (bias, suffix-3, prefix-1, previous tags,
  word windows of ±2, the hyphen/year/digit normalisation). Not checked
  against the packaged weights.
- **Russian tag mapping** (N-000205–N-000207). Built as a table in
  `lingora/tag.py` (`_RUS_TO_UNIVERSAL`), keyed on the part before `=`. Unknown
  categories map to `X`.
- **English universal mapping missing table.** Raises `LookupError` (allowed by
  N-000215).
- **Unigram tie-break** (N-000189). Most frequent tag; ties by tag string order.
- **Decision tree.** Chooses, at each node, the feature whose one-level split
  classifies the most training examples correctly (feature names in sorted
  order for ties). Stops when no split beats the majority. A feature absent
  from a featureset counts as value `None`. Unseen values fall back to the
  node's majority label.
- **Naive Bayes smoothing.** Laplace-style: `(count+1)/(n+K+1)`, with `K` the
  number of distinct values of that feature in training. Features not seen in
  training are ignored.
- **Accuracy over no positions** (`metrics.accuracy`, `classify.accuracy`):
  raises `ValueError`. Spec is silent.
- **Jaccard of two empty sets**: 0.0 (spec silent).
- **Recall with an empty reference**: `None`. Spec gives `None` for precision
  with an empty test set, and for f-measure when either set is empty.
- **Edit distance**: the Lowrance–Wagner algorithm for `transpositions=True`,
  with the given substitution cost.
- **BLEU** (N-000302–N-000309): sentence BLEU with clipped counts, closest
  reference length (shorter on ties), brevity penalty. Without smoothing, any
  zero precision among the weighted orders gives 0.0. `smoothing_function` is
  a callable taking the list of `(numerator, denominator)` pairs and returning
  adjusted precisions; `translate.method1` is provided.
- **Shift-reduce.** Reduces with the longest matching right-hand side, then
  grammar order. Empty productions are never used to reduce, since they would
  reduce forever. A state-based guard stops loops from unit productions.
- **Generator order and depth.** Breadth-first by number of expansion steps,
  productions tried in written order, so recursive grammars yield lazily.
  `depth` stops expanding a nonterminal at that level.
- **Nonterminal representation.** A `Nonterminal` object whose `str()` is its
  name (N-000431 leaves the choice open). Terminals are `str`.
- **Chart parser tree order.** Not specified; the order is the enumeration
  order. Trees are finite under cycles (a `(symbol, span)` already on the path
  is not expanded again).
- **Tweet tokenizer.** Emoticons, URLs (`http(s)://` and `www.`), `@handles`,
  `#hashtags`, decimal numbers with `.`/`,` separators, words with internal
  apostrophes (`\w+('\w+)*`) are single tokens. Hyphens are not joined into
  words. Runs of the same punctuation character form one token. Length
  reduction collapses 3+ identical characters to three.
- **Porter modes.** `ORIGINAL_ALGORITHM` (no extensions) and
  `MARTIN_EXTENSIONS` (same LINGORA steps, documented as approximate) are
  provided; N-000142–N-000144 say their results are outside the spec.
- **Data finder defaults** (N-000353). Initial `data.path`: `LINGORA_DATA`
  (os.pathsep-separated), `~/lingora_data`, `<sys.prefix>/share/lingora`,
  `/usr/local/share/lingora`, `/usr/share/lingora`. Resources are looked up
  per call, so in-place changes to `data.path` take effect immediately.
- **Resource presence.** A resource counts as visible when its file or
  directory exists under a listed directory. Unreadable or malformed model
  files raise.
- **WordNet layout.** Assumed `corpora/wordnet/index.{noun,verb,adj,adv}`.
  The lemmatizer's result is outside the spec, so it is a minimal morphy-style
  lookup.
- **Stopwords.** `corpora/stopwords/<language>`, one word per line, UTF-8.
- **Punkt files.** Read as UTF-8; `collocations.tab` and `ortho_context.tab`
  are tab-separated; a missing file raises `LookupError`.
- **CLI.** Exit status 0 on success; 1 when tokenizing a line fails (the first
  failure stops the command, and no token line is written for that input);
  2 for usage errors. Stderr text is free-form. Options: `--language/-l`
  (default `english`), `--delimiter/-d` (default one space). An empty input
  line gives an empty output line.
- **Porter (LINGORA mode) specifics.** Irregular-forms table: a small built-in
  dict (N-000147; its contents are outside the spec). `logi`→`log` is
  conditioned on the measure of the part before `-ogi`. `bli`→`ble` is
  conditioned on the measure of the part before `-bli`.
- **Snowball English.** Standard Porter2 (Snowball's `english`). Exceptions
  lists and R1/R2 regions as in the Snowball algorithm. Verified on about forty
  words; not checked against the official test vocabulary.
- **Lancaster.** The rule engine follows Paice/Husk (rules written with the
  suffix reversed; `*` intact-only; `.` stop; `>` continue; acceptability:
  stem of length ≥2, or ≥3 when it starts with a consonant). The rule table is
  **partial** (see not-done list below).
- **Porter default mode `*o`** (N-000153): the two-letter stem case is
  vowel-then-consonant, with no w/x/y exclusion.
- **Short syllable in Porter2** (step 1b and step 5). The short-word rule uses
  R1 as defined in the Snowball algorithm.

## Checklist accounting (477 ids)

Status key: **done** = implemented (and where a test is named after the id,
tested). **Constraint** = satisfied by design. Ids marked *not done* are listed
below with their reasons.

- **Pack 02** (N-000320–N-000323): done (constraint). No compiled code,
  runtime dependencies none, `requires-python >=3.10`
  (`pyproject.toml`). Tests: none beyond import.
- **Pack 03** (N-000324–N-000337): done. CPU baseline: import from source tree,
  word/punct tokenization with no model (`test_N_000325_*`). Flat layout;
  `pyproject.toml` for editable install.
- **Pack 05** (N-000338–N-000352): done. Every entry is a callable; refusals
  raise; numbers are `int`/`float`, never `bool` (`metrics._as_number`).
- **Pack 06** (N-000353–N-000370): done. `data.path`, resource names, Punkt,
  perceptron, universal, WordNet, stopwords. Resource table rows N-000357–N-000364
  are read by the modules that need them.
- **Pack 07** (N-000371–N-000381): done (`test_N_000122_*`, `test_N_000381_*`).
- **Pack 08** (N-000382–N-000388): done (`test_N_000382_*`, `test_N_000387_*`).
- **Pack 09** (N-000389–N-000396): done (`test_N_000171_*`, `test_N_000174_*`).
- **Pack 10** (N-000397–N-000409): done (`test_N_000397_*`, `test_N_000211_*`,
  `test_N_000215_*`).
- **Pack 11** (N-000410–N-000423): done (`test_N_000410_*`, `test_N_000416_*`,
  `test_N_000422_*`, `test_N_000230_*`).
- **Pack 12** (N-000424–N-000443): done (`test_N_000424_*`, `test_N_000251_*`).
- **Pack 13** (N-000444–N-000454): done (`test_N_000444_*`).
- **Pack 14** (N-000455–N-000460): done (`test_N_000277_*`, `test_N_000274_*`).
- **Pack 15** (N-000461–N-000477): done (`test_N_000464_*`, `test_N_000302_*`).
- **Pack 16** (N-000001–N-000020): done (constraint/requirement; packaged corpora
  and downloader out of scope; see not-done).
- **Pack 17** (N-000021–N-000025): done (terminology; Punkt and token behaviour).
- **Pack 18** (N-000026–N-000044): done, except N-000028 (see not-done).
- **Pack 19** (N-000045–N-000064): done (constraints; data finder without
  downloader).
- **Pack 20** (N-000065–N-000067): done.
- **Pack 21** (N-000068–N-000076): satisfied by omission (non-goals).
- **Pack 22** (N-000077–N-000132): done, except N-000078 (see not-done).
  Tests: `test_N_000088_*`, `test_N_000096_*`, `test_N_000099_*`,
  `test_N_000106_*`, `test_N_000109_*`, `test_N_000112_*`, `test_N_000122_*`,
  `test_N_000129_*`, `test_N_000131_*`.
- **Pack 23** (N-000133–N-000175): done for English and `porter`; see not-done
  for other Snowball languages, ISRI, Cistem, RSLP.
- **Pack 24** (N-000176–N-000216): done for default/unigram/regexp taggers and
  the recommended tagger; see not-done for bigram/trigram/affix.
- **Pack 25** (N-000217–N-000236): done, except N-000219 (see not-done).
- **Pack 18 N-000036** (NE chunker is not the primary chunking path):
  satisfied; chunking is the regexp chunker, and the NE chunker is gated and
  not built (N-000219).
- **Pack 26** (N-000237–N-000268): done, except N-000237 (see not-done).
  Tests: `test_N_000242_*`, `test_N_000247_*`, `test_N_000268_*`, `test_N_000266_*`.
- **Pack 27** (N-000269–N-000288): done (`test_N_000277_*`, `test_N_000283_*`,
  `test_N_000274_*`).
- **Pack 28** (N-000289–N-000315): done (`test_N_000292_*`, `test_N_000300_*`,
  `test_N_000302_*`).
- **Pack 29** (N-000316–N-000319): outside the spec. Not built (see not-done).

## Not done (with reasons)

- **N-000028**, **N-000078**: the s-expression tokenizer. The spec says it is
  outside this specification.
- **N-000136–N-000139** (ISRI, ARLSTem, ARLSTem2, Cistem, RSLP exist; their
  results are outside the spec). `ARLSTem`/`ARLSTem2` are importable and
  `stem()` raises `NotImplementedError`. ISRI, Cistem, RSLP are not built.
- **N-000133**, **N-000140**, **N-000163**, **N-000164** (Snowball). Only
  `english` (Porter2) and `porter` are implemented. The other 14 supported
  language names raise `NotImplementedError` at construction, and unknown names
  raise `ValueError`. Dutch (N-000164) is not built. Reason: Snowball algorithms
  for the other languages were not implemented in this build.
- **N-000161** (Lancaster). The rule table is partial: `lingora/stem.py` has
  25 rules. The engine is complete. Full published table not reproduced, so
  Lancaster results will differ on many words.
- **N-000176**, **N-000177**, **N-000178** (bigram, trigram and affix taggers).
  Not built. The spec says their results are outside the specification.
- **N-000219** (named-entity chunker). `ne_chunk` checks that the model and
  the English wordlist are visible (N-000415, N-000236), then raises
  `NotImplementedError`. The model file format is not in the spec.
- **N-000237** (recursive-descent parser). Not built. The spec says its results
  are outside the specification.
- **N-000316–N-000319** (packaged corpora, WordNet, downloader, graphical
  tools, external wrappers, CCG, inference, n-gram models, sentiment, CRF/sklearn
  extras). Outside the specification.

## Checks I ran

- `python3 -m pytest -q tests`: 57 passed.
- Stemmers: Porter default and original modes checked against published
  examples (`caresses`, `ponies`, `relational`, `generalizations`, ...). Porter2
  checked on forty words (`consign`, `generously`, `exceed`, ...). Lancaster
  checked on `maximum`→`maxim` and `owed`→`ow` only.
- Parsers: chart parser counts two PP-attachment trees for the classic
  ambiguous sentence; generator order checked by hand; epsilon and unit cycles
  terminate.
- Punkt: checked on a fixture model (abbreviations, sentence starters,
  collocations, orthographic context).
- Chunker: checked cascading (`NP` inside `VP`), quantifiers, chink splitting,
  and root label.
