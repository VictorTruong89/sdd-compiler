# Answer key: 15 conflicts planted in case010, round 19 (never shown to an agent)

> Written 2026-11-02, after the step-1 checks and before the compile and any agent run. The planted
> Markdown is made by `notes/plant.py work/spec-planted C01 C03 C04 C05 C08 C09 C11 C13 C14 C15 C16
> C17 C18 C21 C22` (the 15 kept ids) from Zero2Repo case010's `public/`; it stays in git-ignored
> `work/` (Zero2Repo has no licence file), 8 610 words (8 412 before). sha256 of the planted files
> (`work/spec-planted.sha256`): `Full_PRD.md` `f556b568f5dfc512…`, `Interface_Contract.md`
> `0496bd9aa6a1e095…`, `Hardware_Requirements.md` `7ce6498d92d11e95…` (unchanged). Only short
> phrases are quoted here.

Side **A** is the text the case already had: the reference library's behaviour and what the hidden
tests check. Side **B** is the planted sentence: one place edited, in the spec's voice, no marker.
Lines are those of the planted files (PRD = `Full_PRD.md`, Contract = `Interface_Contract.md`).
Where side A is stated in a second place too, that place is named; the B sentence contradicts both.

| Item | Distance | A (kept) | B (planted) | Footprint (hidden tests A→B) | Past fails |
|---|---|---|---|---|---|
| C01 | across files | PRD 303: with transpositions, "the distance is the unrestricted Damerau–Levenshtein distance" | Contract 235: only adjacent characters may be transposed and "nothing may be inserted or deleted between them" | `F07 edit_distance_abc_ca_transpositions_off_three_on_two` | 0 |
| C03 | same file | PRD 309: f-measure "is 0 when precision or recall is 0" | PRD 320: f-measure returns no number "when the two sets share no element" | `F07 empty_test_precision_is_absent_not_zero`, `F07 fmeasure_absent_when_either_side_empty`, `F07 fmeasure_nonempty_disjoint_is_zero` | 0, 0, 0 |
| C04 | same file | PRD 320: "Lists, tuples and other non-set collections are refused" (also Contract 238) | PRD 308: a list or tuple "is read as the set of its elements" | `F07 precision_recall_refuse_lists_and_other_non_sets` | 0 |
| C05 | across files | PRD 312: BLEU's "default is equal weights on unigrams through 4-grams" | Contract 242: with `weights` omitted, unigrams and bigrams equal, "longer n-grams are not scored" | `F07 default_four_weight_unsmoothed_two_token_identity_is_zero_to_four_decimals` | 0 |
| C08 | same file | PRD 263: a string "as the child list (instead of a list of children) is refused" (also Contract 195) | PRD 255: a string in place of the child list "is taken as a single leaf" | `F05 tree_empty_child_list_succeeds_and_differs_from_refusals`, `F05 tree_rejects_string_as_child_list` | 0, 0 |
| C09 | across files | PRD 120: regexp tokenizer drops empty pieces "unless the caller turns empty-discarding off (it is on by default)" | Contract 66: "`discard_empty` is off unless the caller passes `discard_empty=True`" | `F01 regexp_gap_mode_no_empty_tokens_at_whitespace_ends` | 0 |
| C11 | same bullet | PRD 222: "Two matches that touch are two separate chunks" | PRD 222: chunks that touch "are joined into one chunk" | `F04 np_grammar_adjacent_matches_are_two_chunks` | 0 |
| C13 | across files | PRD 253: generator, "A quoted empty string contributes an empty-string token" | Contract 180: "A terminal that is the empty string adds no token to a sentence" | `F05 generate_quoted_empty_string_is_a_then_empty_token`, `F05 generate_runtime_quoted_empty_vs_empty_production` | 0, 0 |
| C14 | same file | PRD 264: a token list with a token no production produces "does **not** succeed" (also Contract 175) | PRD 251: chart parser returns none for a list "including one holding a token that no production produces" | `F05 chart_runtime_uncovered_vs_covered_ungrammatical`, `F05 chart_uncovered_token_is_refused_not_empty_set` | 0, 0 |
| C15 | same file | PRD 319: "Accuracy on two lists of different lengths does not succeed" (also PRD 288, Contract 231) | PRD 306: for lists of different lengths, the fraction "over the positions both lists have" | `F06 accuracy_mismatched_lengths_does_not_succeed`, `F07 accuracy_mismatched_lengths_does_not_succeed` | 0, 0 |
| C16 | across files | PRD 158: Porter, "a four-letter word ending in *-ies* becomes *-ie* rather than *-i*" | Contract 99: Step 1a as published, "so *ties* stems to *ti*" | `F02 default_porter_nineteen_named_pairs` | 0 |
| C17 | across files | PRD 155: Porter, "The word is lowercased first, unless the caller turns lowercasing off" | Contract 99: "`to_lowercase` defaults to `False`", `stem` keeps the letter case | `F02 default_porter_running_case_matches`, `F02 default_porter_runtime_capitalized_named_word_matches` | 0, 0 |
| C18 | same file, far | PRD 127: tweet tokenizer, "With case preservation off (it is on by default)" | PRD 65: the tweet tokenizer "lowercases its tokens unless the caller asks to preserve case" | `F01 tweet_strips_myke_keeps_colon_lets_and_accents` | 0 |
| C21 | same file | PRD 105: *cannot* and the other fused forms "are split into their two parts (*can* + *not*" | PRD 112 (recommended tokenizer's improvements): "*cannot* is kept as one token" | `F01 recommended_cannot_splits_each_into_can_not`, `F01 recommended_runtime_cannot_splits` | 0, 0 |
| C22 | same file | PRD 100: a straight double quote at the start of the text "becomes the opening-quote token made of two backticks" | PRD 108 (recommended tokenizer's improvements): one "at the very start of the text becomes the closing-quote token" | `F01 recommended_leading_straight_quote_becomes_backticks`, `F01 recommended_runtime_leading_quote_rewritten` | 0, 0 |

**Footprint union: 24 tests, none shared by two items, none among the 20 model-file tests.** The
**core** (set 1) is the other **173** tests, the 20 model-file tests included. The base build fails 1
test, not in the union (`F02 snowball_arabic_named_pairs`; `notes/footprint.json`, `BASE_failed`), so
it scores 172 / 173 on the core. Distances: same bullet 1 (C11); same file 8 (C03, C04, C08, C14,
C15, C18, C21, C22; C18's two places are 62 lines apart, the others 7 to 13); across files 6 (C01,
C05, C09, C13, C16, C17). C16 and C17 are planted on the same Contract line, as two sentences.

**Past fails** = how many of round 13c's 8 case010 builds, re-scored on the fixed task (TRIAL.md,
step 0b), failed that test: 0 for every footprint test, so a failure there in this round is a side-B
build or a new fault, not a test the models already found hard.

## Candidates tried and dropped (step 1, no model call)

| Item | Behaviour | Why dropped |
|---|---|---|
| C02 | f-measure α defaults to 0.25 | footprint 0 (no hidden test reads the default α) |
| C10 | regexp tagger, last matching rule wins | footprint 0 |
| C26 | blank-line tokenizer, newline inside a segment becomes a space | footprint 0 |

No candidate touched a packaged-model path (punkt, tagger, chunker, stopwords, wordlist, WordNet) or
the command line; none of the 18 footprints contained a model-file test.

## How each side is read (`notes/probe.py`, black box, from this key and the Contract only)

| Item | Probe | A | B |
|---|---|---|---|
| C01 | `edit_distance('abc', 'ca', transpositions=True)` | 2 | 3 |
| C03 | `f_measure({1}, {2})` | 0 | `None` |
| C04 | `precision([1, 2], [1])` | raises | 1.0 |
| C05 | `bleu([['a', 'b']], ['a', 'b'])` | 0 | 1.0 |
| C08 | `Tree('S', 'abc')` | raises | leaves `['abc']` |
| C09 | `RegexpTokenizer(r'\s+', gaps=True).tokenize(' a b ')` | `['a', 'b']` | `['', 'a', 'b', '']` |
| C11 | `RegexpParser('NP: {<DT><NN>}')` on DT NN DT NN: chunks | 2 | 1 |
| C13 | `generate(CFG.fromstring("S -> 'a' ''"))` | `[['a', '']]` | `[['a']]` |
| C14 | `ChartParser(CFG.fromstring("S -> 'a'")).parse(['b'])` | raises | `[]` |
| C15 | `metrics.accuracy([1, 2, 3], [1, 2])` | raises | 1.0 |
| C16 | `PorterStemmer().stem('ties')` | `tie` | `ti` |
| C17 | `PorterStemmer().stem('Running')` | lower case | case kept |
| C18 | `TweetTokenizer().tokenize('Hello World')` | `['Hello', 'World']` | lower case |
| C21 | `word_tokenize('I cannot go', preserve_line=True)` | `can`, `not` | `cannot` |
| C22 | `word_tokenize('"Hi" he said', preserve_line=True)[0]` | ` `` ` | `''` |

Check (`work/probe_check.log`): the base reads A on all 18 candidates; each side-B copy reads B on its
own item and A on the other 17.
