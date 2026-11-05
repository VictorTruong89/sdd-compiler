# NOTES

Build of LINGORA from `spec/` (export with `--allow-open`; 19 contradictions have no human verdict).
Code is in `lingora/`; tests in `tests/` (`python3 -m pytest` from `/app`, 49 passing).
Every checklist id is accounted for in the traceability section below; `# spec: N-…` markers sit beside the code.

## 1. Disagreements in the spec and what was built

Rule used throughout: where the spec's own text says the PRD governs a default or an algorithm
(`spec/packs/05`, N-000382: "The PRD states the default's behaviour wherever it matters"), the PRD wins.
Where the Interface Contract states a call refusal (raise), the Contract wins. Each entry below says which rule applied.

1. **CF-000001: straight double quote at the start of the text.**
   - PTB word tokenizer, `spec/packs/22` (N-000094): "A straight double quote at the start of the text, or after a space or an opening bracket, becomes the opening-quote token made of two backticks."
   - Recommended word tokenizer, `spec/packs/22` (N-000106): "A straight double quote at the very start of the text becomes the closing-quote token."
   - **Built:** each tokenizer follows its own sentence. PTB gives ``` `` ```; the recommended tokenizer gives `''`.

2. **CF-000008, CF-000039, CF-000072: accuracy on lists of different lengths.**
   - FP-07 normal behaviour, `spec/packs/28` (N-000331): fraction over the positions both lists have.
   - FP-07 boundary, `spec/packs/28` (N-000343), FP-06 (`spec/packs/27`, N-000318), and Contract `spec/packs/15` (N-000502): "does not succeed" / "make it raise".
   - **Built:** raise `ValueError` (three statements against one).

3. **CF-000016, CF-000055, CF-000070: edit distance with transpositions.**
   - FP-07 (`spec/packs/28` N-000325, N-000327): unrestricted Damerau–Levenshtein (Lowrance and Wagner, 1975); insertions/deletions allowed between the transposed characters.
   - Contract (`spec/packs/15` N-000505, N-000506): only adjacent characters transposed; nothing inserted or deleted between them.
   - **Built:** the PRD algorithm (unrestricted). `edit_distance('ca', 'abc', transpositions=True) == 2`, which the Contract's rule would give as 3.

4. **CF-000028: two touching chunk matches.**
   - FP-04 (`spec/packs/25` N-000240): "Two matches that touch are two separate chunks."
   - FP-04 (`spec/packs/25` N-000242): "Chunks that touch, with no token between them, are joined into one chunk."
   - **Built:** matches stay separate (the rule-level statement wins over the general chunk statement).

5. **CF-000038: f-measure when precision or recall is 0.**
   - FP-07 (`spec/packs/28` N-000334): "It is 0 when precision or recall is 0."
   - FP-07 (`spec/packs/28` N-000346): no number when the two sets share no element.
   - **Built:** return `None` whenever the sets share no element, or precision or recall has no value. Otherwise the weighted harmonic mean with α = 0.5. A disjoint pair therefore gives `None`, not `0`.

6. **CF-000054: tweet tokenizer lowercasing and emoticons.**
   - `spec/packs/19` N-000067: the tweet tokenizer "lowercases its tokens unless the caller asks to preserve case".
   - `spec/packs/22` N-000125: "tokens are lowercased, except emoticons".
   - **Built:** the more specific rule (emoticons keep their case when case preservation is off).

7. **CF-000073: `ties` in PorterStemmer.**
   - FP-02 (`spec/packs/23` N-000158): LINGORA Step 1a turns a four-letter `-ies` word into `-ie`.
   - Contract (`spec/packs/09` N-000424): "applies Step 1a as published, so *ties* stems to *ti*".
   - **Built:** the PRD. Default-mode `PorterStemmer().stem("ties") == "tie"`. `PorterStemmer(mode="ORIGINAL")` gives `"ti"`, which is the published-algorithm result.

8. **CF-000077: `discard_empty` default in the regexp tokenizer.**
   - FP-01 (`spec/packs/22` N-000118): empty pieces are dropped "unless the caller turns empty-discarding off (it is on by default)".
   - Contract (`spec/packs/07` N-000407): "`discard_empty` is off unless the caller passes `discard_empty=True`".
   - **Built:** default ON (PRD governs defaults). `discard_empty=False` keeps empties.

9. **CF-000083: the fused form *cannot*.**
   - PTB (`spec/packs/22` N-000102): fused forms "are split into their two parts (*can* + *not*…)".
   - Recommended (`spec/packs/22` N-000110): "*cannot* is kept as one token."
   - **Built:** split under the PTB tokenizer, kept whole under the recommended tokenizer (the two tokenizers are separate entries).

10. **CF-000086: precision/recall arguments that are lists.**
    - FP-07 (`spec/packs/28` N-000332): a list or tuple "is read as the set of its elements".
    - FP-07 (`spec/packs/28` N-000345), Contract (`spec/packs/15` N-000508–N-000509): lists, tuples and non-sets are refused.
    - **Built:** refuse with `TypeError` (the call-refusal rule).

11. **CF-000087: BLEU default weights.**
    - FP-07 (`spec/packs/28` N-000338): default is equal weights on unigrams through 4-grams.
    - Contract (`spec/packs/15` N-000515): omitted weights cover unigrams and bigrams, and longer n-grams are not scored.
    - **Built:** the PRD (four equal weights, the standard sentence BLEU of Papineni et al.).

12. **CF-000088: `Tree` built from a string child list.**
    - FP-05 (`spec/packs/26` N-000282): a string given in place of the child list "is taken as a single leaf".
    - Contract (`spec/packs/13` N-000486–N-000488) and FP-05 boundary (`spec/packs/26` N-000288): refused.
    - **Built:** `Tree("S", "ab")` raises `TypeError`. Omitting the children also raises. `Tree("S", [])` is valid.

13. **CF-000089: a quoted empty string in the generator.**
    - FP-05 (`spec/packs/26` N-000279): "A quoted empty string contributes an empty-string token."
    - Contract (`spec/packs/12` N-000480): an empty-string terminal "adds no token to a sentence".
    - **Built:** the PRD. A quoted `''` terminal yields the token `""`. An empty production (nothing after `->`) yields no token.

14. **CF-000090: a token list containing a token no production produces.**
    - FP-05 chart parser (`spec/packs/26` N-000267): "none for a token list the grammar does not derive (including one holding a token that no production produces)".
    - FP-05 boundary (`spec/packs/26` N-000292), Contract (`spec/packs/12` N-000475): "does not succeed" / raises.
    - **Built:** raise `ValueError` at the call. A list of known tokens the grammar does not derive gives an empty iterator.

15. **CF-000091: `to_lowercase` default of `PorterStemmer.stem`.**
    - FP-02 (`spec/packs/23` N-000154): the word "is lowercased first, unless the caller turns lowercasing off".
    - Contract (`spec/packs/09` N-000426): "`to_lowercase` defaults to `False`".
    - **Built:** the PRD. The default is `True`, so `stem("Running") == "run"`. Pass `to_lowercase=False` to keep case; the suffix is still stripped (`"Run"`).

Other gaps and choices that are not spec conflicts:

- **Sentence splitting:** `word_tokenize(preserve_line=False)` requires the Punkt model (as specified). Sentence splitting is a decision procedure over the packaged parameters (abbreviations, collocations, sentence starters, orthographic context). There is no training, and the heuristics approximate the Punkt paper (Kiss and Strunk, 2006); they are not a byte-for-byte port.
- **Initial `data.path`:** empty, unless the `LINGORA_DATA` environment variable names directories (`os.pathsep`-separated). The spec leaves the initial contents to the implementer.
- **Lancaster rule table (highest-risk item):** reconstructed from memory of the Paice/Husk table as commonly published. Only `maximum→maxim`, `presumably→presum`, `provision→provid`, `multiply→multiply`, `running→run` were checked. Other words may differ from the published table.
- **Porter irregular-form table:** empty (its entries are outside the spec).
- **Russian universal tagset mapping:** my own table (the spec leaves it to the implementer); unknown tags map to `X`.
- **`jaccard_distance(∅, ∅)`:** returns `0.0` (undefined in the spec; identical sets).
- **`accuracy` on empty lists** (both `metrics` and `classify`): `ValueError`. **`bleu` with empty hypothesis:** `0.0`; with no references: `ValueError`.
- **Chunk grammar:** root label `"S"`; an empty grammar (no clauses) raises `ValueError`; a list of stages may hold grammar strings or `RegexpParser` objects.
- **`ChartParser` / `ShiftReduceParser` results:** trees are returned as a list-backed iterator. Cycles (unit or empty productions) are cut at the span where they recur. The shift-reduce pass is greedy with no backtracking, as specified, so it can return no parse for a sentence the chart parser accepts.
- **CLI:** `lingora tokenize [--language L] [--delimiter D] [--encoding E]`. Exit status 1 on failure (including a missing Punkt model, checked before any output), 2 on usage errors, 0 on success. Standard error text is free-form.

## 2. Not done (with reasons)

- **Snowball stemmers for arabic, danish, dutch, finnish, french, german, hungarian, italian, norwegian, portuguese, romanian, russian, spanish, swedish.** The names are accepted and the stopword-skipping check works, but `stem()` raises `NotImplementedError`. Porter2 (`english`) and the Snowball rendering of the original Porter (`porter`) are implemented. The other algorithms were not written in this build. (N-000172, N-000173, N-000147/148 partly.)
- **ISRI, ARLSTem, ARLSTem2, Cistem, RSLP.** Named in the contract surface; ARLSTem and ARLSTem2 are importable stubs that raise `NotImplementedError`. Their results are outside the spec (N-000143–N-000146).
- **WordNet lemmatizer.** Constructor checks the WordNet resource; `lemmatize` raises `NotImplementedError` (N-000185/186 partly).
- **Bigram, trigram and affix taggers.** Outside the specified results (N-000187–N-000189).
- **Recursive-descent parser.** Outside the specified results (N-000258–N-000261).
- **Named-entity chunker (`ne_chunk`).** Raises `LookupError` when its model or the English wordlist is not visible (as specified). When they are visible it raises `NotImplementedError`, because the packaged model format is not described in the spec (N-000231, N-000257 partly).
- **Non-goals and out-of-scope surfaces** (N-000072–N-000080, N-000349–N-000352): corpora, the downloader, graphical tools, chat and Twitter helpers, external-binary wrappers, semantic inference, n-gram models, sentiment lexicons, optional ML extras. None are built.
- **Throughput** (N-000080): not promised.
- **Threading and process model** (N-000068): not a concern of the spec. The library is in-process and has no shared state beyond `data.path`.
- **Terminology** (N-000022–N-000028): definitions are honoured by the code; they are not separate code units.

## 3. Traceability (every checklist id)

Status key: **I** implemented (code carries `# spec:` marker); **T** implemented and covered by tests; **N** not done, reason in section 2; **P** partly implemented, the gap is in section 2.

| Pack | Ids | Status | Where |
|---|---|---|---|
| 01 | (none) | — | — |
| 02 | N-000353–000356 | I (pure-Python layout, pyproject) | `pyproject.toml`, `lingora/__init__.py` |
| 03 | N-000357–000370 | I (flat layout, editable install, Python 3.10+) | `pyproject.toml`; `T` tokenizer test without model (`tests/test_tokenize.py`) |
| 04 | (none) | — | — |
| 05 | N-000371–000384 | I/T (importable package, raise on refusal, int/float scores) | `lingora/__init__.py`, `tests/test_cli_data.py` |
| 06 | N-000385–000402 | I/T (`data.path`, finder, Punkt/tagger/stopword/WordNet names, file formats) | `lingora/data.py`, `lingora/_punkt.py`, `lingora/tag.py`; `tests/conftest.py` fixtures |
| 07 | N-000403–000413 | I/T | `lingora/tokenize.py`; `tests/test_tokenize.py` |
| 08 | N-000414–000420 | I/T (`cli.main(args, standalone_mode)`) | `lingora/cli.py`; `tests/test_tokenize.py` (CLI tests) |
| 09 | N-000421–000432 | I/T (stemmers; P for the other Snowball languages, see §2) | `lingora/stem.py`; `tests/test_stem.py` |
| 10 | N-000433–000445 | I/T | `lingora/tag.py`; `tests/test_tag.py` |
| 11 | N-000446–000460 | I/T | `lingora/chunk.py`; `tests/test_chunk_parse.py` |
| 12 | N-000461–000480 | I/T (P for ne_chunk, N for recursive descent in 26 — see §2) | `lingora/grammar.py`, `lingora/parse/`; `tests/test_chunk_parse.py` |
| 13 | N-000481–000491 | I/T | `lingora/tree.py`; `tests/test_chunk_parse.py` |
| 14 | N-000492–000497 | I/T | `lingora/classify.py`; `tests/test_classify_metrics.py` |
| 15 | N-000498–000517 | I/T | `lingora/metrics.py`, `lingora/translate.py`; `tests/test_classify_metrics.py` |
| 16 | N-000001–000021 | I (library; feature ordering N-000017 reflected in module order) | `lingora/__init__.py` |
| 17 | N-000022–000028 | I (terminology honoured; no separate code) | — |
| 18 | N-000029–000047 | I/P (surface implemented; families in §2 are P or N) | `lingora/*` |
| 19 | N-000048–000068 | I (pure-Python, Unicode, packaged-data finder); N-000080 and N-000068 as in §2 | `pyproject.toml`, `lingora/data.py`, `lingora/tokenize.py` |
| 20 | N-000069–000071 | I/T (package imports; entries unusable without it) | `lingora/__init__.py` |
| 21 | N-000072–000080 | N (non-goals, §2) | — |
| 22 | N-000081–000139 | I/T (FP-01) | `lingora/tokenize.py`, `lingora/_punkt.py`, `lingora/cli.py`; `tests/test_tokenize.py` |
| 23 | N-000140–000186 | I/T for Porter, Porter2 (`english`), `porter`, Lancaster, regexp, stopword skipping; P/N for other Snowball languages, ISRI/ARLSTem/Cistem/RSLP, WordNet lookup (§2) | `lingora/stem.py`; `tests/test_stem.py` |
| 24 | N-000187–000227 | I/T for default, unigram, regexp, backoff, recommended English/Russian tagger, universal mapping; N for bigram/trigram/affix (outside spec) | `lingora/tag.py`; `tests/test_tag.py` |
| 25 | N-000228–000257 | I/T for chunk grammar, chunk and chink rules, cascade; P for ne_chunk (§2) | `lingora/chunk.py`; `tests/test_chunk_parse.py` |
| 26 | N-000258–000294 | I/T for chart and shift-reduce parsers, generator, trees and refusals; N for recursive descent (§2) | `lingora/parse/`, `lingora/grammar.py`, `lingora/tree.py`; `tests/test_chunk_parse.py` |
| 27 | N-000295–000318 | I/T (FP-06 classifiers; FP-07 accuracy refusals) | `lingora/classify.py`, `lingora/metrics.py`; `tests/test_classify_metrics.py` |
| 28 | N-000319–000348 | I/T (edit distance, Jaccard, precision/recall/f, BLEU) | `lingora/metrics.py`, `lingora/translate.py`; `tests/test_classify_metrics.py` |
| 29 | N-000349–000352 | N (outside this specification, §2) | — |

Ids that are only partly done (P) are also listed in §2 with the reason.

## 4. Verification

- `python3 -m pytest` from `/app`: 49 passed (the suite builds its own Punkt, tagger, universal-tagset and stopword fixtures under a temporary directory; no real corpus is needed).
- Spot checks made by hand against the spec: Treebank clitics and fused forms; `Dr. Smith` not split; `ties→tie` (default Porter); `generously→generous` and `ties→tie` (Porter2); chart parse tree counts (`S -> S S | "a"` gives 2 trees for `a a a`); unrestricted Damerau–Levenshtein; BLEU zero-match and identity cases; CLI exit codes 0, 1 (missing model, no output) and 2 (usage).
- Not verified: the hidden acceptance tests, the published Lancaster table, and Snowball languages other than English.
