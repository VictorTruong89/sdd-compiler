# NOTES — LINGORA implementation

Build: no build step. The package is the flat `lingora/` directory at `/app`; import
it from `/app` (or `pip install -e .` with the included `pyproject.toml`). Tests:
`python3 -m pytest -q tests` (72 passing at the time of writing).

Packaged resources (Punkt models, averaged-perceptron taggers, universal tagset,
stopwords, WordNet, the named-entity chunker) are **not** in this repository and
are not downloaded. Lookups go through `lingora.data.path` (initially the
directories in `$LINGORA_DATA` and `~/lingora_data`). The tests build small
fabricated resource trees in the layout of pack 06; they are not real models.

## 1. Where the specification disagrees with itself

Format: **Sources** (pack and id), **what each says**, **built**.
The 13 unsettled contradictions in `spec/MAP.md` are CF-000001, -000008, -000016,
-000028, -000038, -000039, -000054, -000055, -000070, -000072, -000073, -000077,
-000083. All 13 are covered below.

Rule used where a conflict was not otherwise decided: the PRD (`Full_PRD.md`,
packs 16–29) states what each entry computes and the default behaviour; the
Interface Contract (packs 04–15) states signatures and types. Pack 05 says
this itself: "The PRD states the default's behaviour wherever it matters."

1. **Opening vs closing quote at the start of text (CF-000001).**
   Pack 22 N-000094 (Penn Treebank rules): a straight `"` at the start of text
   becomes the opening token ``` `` ```. Pack 22 N-000106 (recommended word tokenizer):
   at the very start it becomes the closing token `''`.
   *Built:* each tokenizer follows its own statement. Penn gives ``` `` ```;
   the recommended tokenizer gives `''`. The two statements describe different
   tokenizers, so this is a per-tokenizer choice, not a contradiction in code.

2. **`cannot` (CF-000083).** Pack 22 N-000102 (fused forms split, including
   *cannot*) vs N-000110 (recommended tokenizer keeps *cannot* as one token).
   *Built:* Penn splits it (`can` `not`); the recommended tokenizer keeps it whole.

3. **Emoticons and lowercasing (CF-000054).** Pack 19 N-000067 (tweet tokenizer
   lowercases "unless the caller asks to preserve case") vs pack 22 N-000125 (tokens
   are lowercased "except emoticons").
   *Built:* emoticons are never lowercased by the tweet tokenizer, following the more
   specific N-000125.

4. **Empty-token dropping default in `RegexpTokenizer` (CF-000077).** Pack 07
   N-000407 (`discard_empty` is off unless the caller passes `True`) vs pack 22
   N-000118 (empty pieces are dropped; "it is on by default").
   *Built:* on by default (PRD). `discard_empty=False` keeps empty pieces.

5. **Default of `to_lowercase` in `PorterStemmer.stem` (not an unsettled CF).**
   Pack 09 N-000422 ("`to_lowercase` defaults to `False`, so `stem` keeps the letter case")
   vs pack 23 N-000154 (the word "is lowercased first, unless the caller turns
   lowercasing off").
   *Built:* default `True` (PRD). With `to_lowercase=False` the algorithm runs on
   the lowercase form and the result is the original-case prefix of the input.

6. **`ties` under Porter (CF-000073).** Pack 09 N-000424 ("Step 1a as published, so
   *ties* stems to *ti*") vs pack 23 N-000158 (in the LINGORA mode a four-letter
   word ending in *-ies* becomes *-ie*).
   *Built:* the default LINGORA mode gives `tie`. `PorterStemmer(mode="ORIGINAL_ALGORITHM")`
   gives `ti`, matching the published algorithm.

7. **Transposition in `edit_distance` (CF-000016, -000055, -000070).** Pack 28 N-000325
   (unrestricted Damerau–Levenshtein; insertions/deletions between transposed
   characters allowed) and N-000327 (MAY allow them) vs pack 15 N-000505–N-000506
   (only adjacent characters, nothing inserted between).
   *Built:* unrestricted Damerau–Levenshtein (Lowrance–Wagner), so `edit_distance("ca","abc",transpositions=True) == 2`.

8. **Accuracy on lists of different lengths (CF-000008, -000039, -000072).**
   Pack 28 N-000331 (fraction over shared positions) vs N-000343, pack 27 N-000318,
   and pack 15 N-000502 (does not succeed / raises).
   *Built:* raises `ValueError`. Three of the four statements agree on this.

9. **f-measure when the sets share nothing (CF-000038).** Pack 28 N-000334 ("0 when
   precision or recall is 0") vs N-000346 (returns no number when the sets share no element).
   *Built:* `None` when either set is empty or the sets share no element (N-000346);
   otherwise the weighted harmonic mean.

10. **Touching matches in chunk rules (CF-000028).** Pack 25 N-000240 ("two matches
    that touch are two separate chunks") vs N-000242 ("chunks that touch are joined").
    *Built:* separate chunks (N-000240). The joining rule (N-000242) is not implemented.

11. **Chart parser on a token no production produces.** Pack 26 N-000267 (returns
    "none" for such a list) vs N-000292–N-000294 (does not succeed; distinguishable
    from an empty result) and pack 12 N-000475 (raises).
    *Built:* raises `ValueError` from the `parse` call. Empty iterator only for
    token lists that are all covered by the grammar but not derivable.

12. **Empty quoted terminal in the generator.** Pack 12 N-000480 ("a terminal that
    is the empty string adds no token") vs pack 26 N-000279 ("a quoted empty string
    contributes an empty-string token").
    *Built:* contributes `''` (PRD). An empty production contributes nothing.

13. **Default BLEU weights.** Pack 15 N-000513–N-000515 (when `weights` is omitted,
    unigrams and bigrams are weighted equally; longer n-grams not scored) vs pack 28
    N-000338 (equal weights on unigrams through 4-grams).
    *Built:* unigrams through 4-grams (PRD).

14. **Snowball `porter` vs `english`.** Not a contradiction. Pack 23 N-000174–N-000175
    says `english` is Porter2 and `porter` is Snowball's rendering of the original
    Porter algorithm. Built as stated; the two can differ.

15. **Porter/Snowball irregular-form table.** Pack 23 N-000155 says the built-in table
    of irregular forms is outside this specification. Built with no table.

## 2. Decisions the spec left to the implementer

- **Chunk grammar cascade (packs 11, 25).** A later clause may match a chunk built
  by an earlier clause as one unit labelled with that chunk's label. A match that
  includes such a unit absorbs its tokens, so the result stays shallow and every
  chunk's children are `(token, tag)` pairs. Within one clause, chunks built by
  that clause are barriers for chunk rules. A chink rule only affects chunks built
  earlier in the same clause. (Pack 25 N-000246–N-000249.)
- **Chunk root label** is `S` (N-000456–N-000457).
- **Tree layout** of `pformat()` is an indented bracketed form.
- **Grammar nonterminals** are `lingora.grammar.Nonterminal` objects whose `str()` is the name (N-000468).
- **Named-entity chunker.** `ne_chunk` checks that `corpora/words` and the chunker
  model are visible (raises `LookupError` otherwise). Results are not implemented (see §3).
- **CLI.** Options `--language` (default `english`), `--delimiter` (default one space),
  `--encoding` (default UTF-8). Failure exits with status 1 and a message on stderr.
  Usage errors exit with 2. Lines written before a failure are kept; the failed line writes nothing.
- **Penn Treebank and recommended tokenizers** are regex pipelines modelled on the
  published Penn conventions; the recommended tokenizer adds the PRD's improvements.
- **Punkt** is a simplified re-implementation of the decision rules (abbreviations,
  collocations, sentence starters and orthographic context). It is not a port of a
  reference implementation, and its boundary decisions may differ from the published
  Punkt on real models.
- **Averaged perceptron** (`pos_tag`) reproduces the feature template and
  normalisation of the textblob-aptagger algorithm described in pack 24. It has
  not been checked against a real model, since none is available here.
- **Universal tags for Russian** map the part before `=` of an RNC tag through a
  fixed table (`S→NOUN`, `V→VERB`, …). Unmapped categories become `X`.
- **Naive Bayes** uses add-one smoothing per feature name; decision tree splits on
  information gain over the feature's values (a missing feature is a `None` branch).
  `accuracy` on an empty list returns `0.0`.
- **BLEU** `smoothing=` is an optional callable taking `[(clipped, total), ...]` and
  returning the list of precisions; not part of the interface.
- **Lancaster** rule table was reproduced from memory of the published Paice/Husk
  table. Rules using a `+` marker are omitted. Treat outputs as likely but not
  certainly identical to the published table.
- **Edit distance** insertion, deletion, and transposition costs are fixed at 1. Only
  substitution cost is configurable.

## 3. Not done (with reasons)

- `ARLSTem`, `ARLSTem2`: importable; `stem()` raises `NotImplementedError`. Their results are outside the spec (pack 23 N-000143–N-000146).
- `ISRI`, `Cistem`, `RSLP` stemmers: not in the interface contract; not implemented (outside spec).
- `SnowballStemmer` for languages other than `english` and `porter`: the constructor
  validates the name (`ValueError` naming the language for names outside the list) and
  raises `NotImplementedError` for the other 14 listed languages. Their algorithms were not implemented. (Pack 23 N-000172.)
- `ne_chunk`: the packaged model format is not implemented, so even with resources
  visible it raises `NotImplementedError` (pack 25 N-000231, N-000257).
- Bigram, trigram, affix taggers (pack 24 N-000188–N-000189): exist in the PRD but results are outside the spec; not implemented.
- Recursive-descent parser (pack 26 N-000258–N-000261): outside the spec; not implemented.
- `WordNetLemmatizer`: requires WordNet files and checks their presence, but uses a
  reduced morphy (suffix rules plus index lookup). Its results are not specified.
- `CFG` incremental append of grammar lines (pack 26 N-000265): no API; the grammar is read whole with `CFG.fromstring`.
- Pack 29 items (corpora, WordNet beyond locating models, graphical tools, chat/Twitter helpers, external wrappers, CCG/DRT, n-gram models, CRF/sklearn extras) are outside the specification (N-000349–N-000352). Not implemented.
- The chunk-joining rule for touching chunks (N-000242): not implemented (see §1.10).

## 4. Checklist accounting

Every id in `spec/CHECKLIST.md` is listed below as implemented (I), tested (T), or
not done (N). Ids marked `# spec: N-xxxxx` in code or named in tests were checked
mechanically; the remainder were checked by reading the code path that realises them.

| Ids | Status | Where |
|---|---|---|
| N-000001–N-000085 | I | Package layout, public surface, PRD overview, terminology (`lingora/*.py`); FP-01 entries at `tokenize.py`; the CLI at `cli.py` |
| N-000086–N-000088 | I, T | `tokenize.py` (word/punct/Penn/whitespace/blank-line/regexp/tweet do not read resources); `tests/test_tokenize.py` |
| N-000089–N-000091 | I, T | `WordPunctTokenizer` |
| N-000092–N-000103 | I, T | `TreebankWordTokenizer` (`_ptb_tokenize`); `tests/test_tokenize.py` |
| N-000104–N-000112 | I, T | `word_tokenize` / `_ptb_tokenize(recommended=True)` |
| N-000113 | I, T | `WhitespaceTokenizer` |
| N-000114–N-000115 | I, T | `blankline_tokenize` |
| N-000116–N-000118 | I, T | `RegexpTokenizer` |
| N-000119–N-000125 | I, T | `TweetTokenizer` |
| N-000126–N-000128 | I, T | `span_tokenize` on Word/Whitespace/Regexp tokenizers |
| N-000129–N-000133 | I, T | `_punkt.py` (sentence splitting); `tests/test_tokenize.py` |
| N-000134–N-000135 | I | `cli.py` (`tokenize`) |
| N-000136 | I, T | empty/whitespace inputs |
| N-000137–N-000139 | I, T | `sent_tokenize` / `word_tokenize` / CLI raise without Punkt |
| N-000140–N-000148 | I (Porter, Lancaster, Snowball english/porter, regexp), N (ISRI, Cistem, RSLP, other Snowball languages, see §3) | `stem.py` |
| N-000149–N-000169 | I, T | Porter (`PorterStemmer`, Porter2 in `_porter2`) |
| N-000170–N-000171 | I, T | `LancasterStemmer` (table caveat in §2) |
| N-000172–N-000177 | I, T | `SnowballStemmer` |
| N-000178–N-000180 | I, T | `RegexpStemmer` |
| N-000181–N-000184 | I, T | `SnowballStemmer` constructor checks |
| N-000185–N-000186 | I, T | `WordNetLemmatizer` raises when WordNet absent |
| N-000187–N-000189 | I (taggers), N (bigram/trigram/affix) | `tag.py` |
| N-000190–N-000206 | I, T | `tag.py` (default, unigram, regexp, backoff, `pos_tag`) |
| N-000207–N-000218 | I, T | `tag.py` (`_Perceptron`, `_load_perceptron`, universal mapping) |
| N-000219–N-000227 | I, T | `pos_tag` argument and resource checks |
| N-000228–N-000257 | I, T | `chunk.py` (`RegexpParser`, `_apply_chunk`, `_apply_chink`) |
| N-000258–N-000265 | I (N-000258–N-000264), N (N-000258 recursive descent and N-000265 append, §3) | `grammar.py`, `parse/` |
| N-000266–N-000271 | I, T | `parse/chart.py` |
| N-000272–N-000275 | I, T | `parse/shiftreduce.py` |
| N-000276–N-000280 | I, T | `parse/generate.py` |
| N-000281–N-000291 | I, T | `tree.py` |
| N-000292–N-000294 | I, T | raise on unknown token (§1.11) |
| N-000295–N-000318 | I, T | `classify.py`, `accuracy` |
| N-000319–N-000348 | I, T | `metrics.py`, `translate.py` |
| N-000349–N-000352 | N | outside specification (pack 29) |
| N-000353–N-000370 | I | pure Python, flat layout, `pyproject.toml`; no compiled code |
| N-000371–N-000384 | I, T | call/failure/numeric conventions across modules |
| N-000385–N-000402 | I (resource finder, layouts, formats), T (Punkt/tagger/universal fixtures in `tests/conftest.py`) | `data.py`, `_punkt.py`, `tag.py` |
| N-000403–N-000413 | I, T | `tokenize.py` |
| N-000414–N-000420 | I, T | `cli.py`, `tests/test_cli.py` |
| N-000421–N-000432 | I, T (see §3 for gaps) | `stem.py` |
| N-000433–N-000445 | I, T | `tag.py` |
| N-000446–N-000460 | I, T | `chunk.py` |
| N-000461–N-000480 | I, T | `grammar.py`, `parse/` |
| N-000481–N-000491 | I, T | `tree.py` |
| N-000492–N-000497 | I, T | `classify.py` |
| N-000498–N-000517 | I, T | `metrics.py`, `translate.py` |

No id is left unaccounted for. The ids marked N are the gaps listed in §3.
