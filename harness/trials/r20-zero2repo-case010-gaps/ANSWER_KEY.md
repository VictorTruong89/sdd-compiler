# Answer key: 14 gaps made in case010, round 20 (never shown to an agent)

> Written 2026-11-04, after the step-1 checks and before the compile and any agent run. The gapped
> Markdown is made by `notes/remove.py work/spec-gapped G02 G03 G07 G08 G09 G10 G13 G14 G16 G17 G18
> G20 G23 G24` (`KEPT`) from Zero2Repo case010's `public/`; it stays in git-ignored `work/` (Zero2Repo
> has no licence file). 8 132 words (8 412 before). sha256 of the gapped files
> (`work/spec-gapped.sha256`): `Full_PRD.md` `27083465b667da32…`, `Interface_Contract.md`
> `a1b52f7b8a6fbdcc…`, `Hardware_Requirements.md` `7ce6498d92d11e95…` (unchanged). Only short phrases
> are quoted here.

A **gap** is a stated fact removed from the spec, with no marker and no "unspecified" wording. The
**upstream** value is what the original spec stated, what the reference library does and what the
hidden tests check; the **alternative** is a plausible other value, built into one copy of the base
build to measure the footprint (`notes/sides.py`). Places are the lines of the **original** files
(PRD = `Full_PRD.md`, Contract = `Interface_Contract.md`). Probe = `notes/probe.py`, on built code.

## Kept gaps

| Gap | Removed fact (short phrase) | Places (original) | Upstream | Alternative | Footprint (hidden tests upstream→alternative) | Probe |
|---|---|---|---|---|---|---|
| G02 | Jaccard distance "is the size of the symmetric difference … divided by the size of their union" | PRD 304 (whole bullet) | identical sets 0, disjoint 1 | Jaccard similarity (identical 1) | `F07 jaccard_disjoint_nonempty_sets_are_one`, `F07 jaccard_identical_sets_are_zero` | `jaccard_distance({1}, {1})` 0 / 1 |
| G03 | "recall with an empty reference set" returns no number | PRD 319 (clause) | `None` | 0 | `F07 empty_reference_recall_is_absent`, `F07 fmeasure_absent_when_either_side_empty` | `recall(set(), {1})` None / 0 |
| G07 | "Every stemmer treats its whole input string as one token"; `word` "is treated as one token" | PRD 149 (two sentences), Contract 99 (clause) | a string with a space is stemmed as one token | each word stemmed, joined by a space | `F02 default_porter_two_word_string_is_one_token`, `F02 lancaster_two_word_string_is_one_token` | Porter `stem('running dogs')` "running dog" / "run dog" |
| G08 | Snowball, unsupported language: "The failure names the requested language"; message "contains the requested name" | PRD 176 (sentence), Contract 101 (clause) | message names the language | generic message | `F02 snowball_klingon_fails_identifying_language_english_succeeds`, `F02 snowball_runtime_unsupported_language_is_identified` | `'klingon' in str(e)` True / False |
| G09 | Snowball *porter* "is Snowball's rendering of the original Porter algorithm, so the two can give different stems" | PRD 169 (sentence) | *porter* = original Porter (generously → gener) | *porter* = alias of *english* (generous) | `F02 snowball_porter_generously_differs_from_english` | porter vs english on "generously" differ / equal |
| G10 | Porter: "Every word is stemmed without refusal, including a word whose stem reduces to a single letter" | PRD 165 (sentence) | `stem('oed')` = "o" | a one-letter stem is not returned: the word comes back unstemmed ("oed") | `F02 default_porter_oed_succeeds_as_o` | `stem('oed')` "o" / "oed" |
| G13 | spans: "Slicing the original string at a span must recover the corresponding token"; "Slicing the input at each pair gives the corresponding token" | PRD 19 (Terminology), PRD 127 (sentence) | end offset exclusive (Python slice) | end offset inclusive | `F01 spans_on_muffin_recover_tokens_ordered_and_nonoverlapping`, `F01 spans_on_runtime_currency_recover_tokens` | spans of "ab cd" [(0,2),(3,5)] / [(0,1),(3,4)] |
| G14 | Penn Treebank: "A comma or colon is split off unless a digit follows it" | PRD 102 (whole bullet) | "1,000" kept whole | comma always split off | `F01 recommended_mortgage_keeps_grouped_and_decimal_amounts`, `F01 recommended_runtime_grouped_and_decimal_amounts` | `tokenize('pay 1,000 now')` ['1,000'] / ['1', ',', '000'] |
| G16 | "Whitespace in a tag pattern is ignored" / "Whitespace in a pattern is ignored" | PRD 28 (Terminology), PRD 220 (sentence) | `{<DT> <NN>}` matches "the dog" | whitespace significant (no match) | `F04 np_grammar_whitespace_in_tag_pattern_ignored` | chunks of `NP: {<DT> <NN>}` 1 / 0 |
| G17 | "An empty tagged-token list yields a chunk structure with a sentence root and no children" | PRD 228 (whole bullet) | root, no children | refused (raises) | `F04 empty_tagged_list_sentence_root_no_children` | `parse([])` root+0 / RAISES |
| G18 | a chunk grammar "that is not text and not a list of chunk-parser stages is refused"; "Any other value makes the constructor raise" | PRD 229 (whole bullet), Contract 139 (sentence) | `RegexpParser(42)` raises | taken as an empty grammar | `F04 non_text_non_stage_grammar_is_refused` | `RegexpParser(42)` RAISES / ACCEPTED |
| G20 | "Two trees are equal exactly when their labels are equal and their children are equal pairwise, recursively" | PRD 256 (whole bullet) | equality compares labels and children | labels ignored (children only) | `F05 changing_inner_np_label_to_x_breaks_equality_and_pretty_print`, `F05 runtime_bracketed_tree_equals_constructed` | `Tree('S',['a']) == Tree('X',['a'])` False / True |
| G23 | Naive Bayes: "uses only the features … that occurred in training. A feature name never seen in training is ignored" | PRD 277 (whole bullet) | unseen feature ignored | refused (raises) | `F06 naive_bayes_unseen_feature_does_not_flip_or_zero_all_probs` | `classify({'nice': True, 'zzz': True})` pos / RAISES |
| G24 | "A featureset that shares no feature with the training data still receives one of the trained labels … never refused" | PRD 282 (whole bullet) | a trained label | refused (raises) | `F06 empty_of_training_features_returns_a_trained_label`, `F06 naive_bayes_runtime_label_inventory_and_empty_query` | NB `classify({})` label / RAISES |

**Footprint union: 22 tests, none shared by two gaps, none among the 20 model-file tests**
(`notes/footprint.json`). The **core** (set 1) is the other **175** tests, the 20 model-file tests
included. The base build fails 1 test, not in the union (`F02 snowball_arabic_named_pairs`), so it
scores 174 / 175 on the core.

**Kinds:** default or value 3 (G02, G09, G13); edge rule 6 (G03, G07, G10, G14, G16, G20); error case
5 (G08, G17, G18, G23, G24). **Places:** one place 9, two places 5 (G07, G08, G13, G16, G18).

**Notes on the cleanness of each gap** (criterion 4, read before any run):

- G02: the name "Jaccard distance" stays (PRD 54, 293; Contract 217, 222). The definition is gone; the
  name is a known term, so an agent may fill it from general knowledge. That is still an unstated
  point under the strict rule.
- G03: the f-measure clause ("when either set is empty") stays; it says nothing about recall itself.
  One footprint test (`fmeasure_absent_when_either_side_empty`) is also in round 19's C03 footprint;
  the facts differ (round 19: f-measure on disjoint sets).
- G07: the phrase "one token" remains in three unrelated places (tweet contractions, PRD 121; tag
  pattern elements, PRD 220; token lists, Contract 69); none is about stemmers.
- G18: Contract 139 still gives the accepted types ("a `str`, or a list of chunk-parser stages"), and
  Contract 11 says a call that does not succeed raises; no sentence says what happens to another
  type.
- G24: PRD 281 still says that for the decision tree "a feature absent from a featureset counts as
  having no value"; the Naive Bayes case is unstated. The alternative build refuses in Naive Bayes
  only.

## Candidates tried and dropped (step 1, no model call)

| Gap | Fact | Why dropped |
|---|---|---|
| G01 | edit distance, default substitution cost 1 (PRD 301) | footprint 0 |
| G04 | BLEU brevity penalty applied (PRD 312) | footprint 0 |
| G05 | BLEU closest reference length, tie → the shorter (PRD 312) | footprint 0 |
| G06 | BLEU counts clipped (PRD 310) | footprint 0 |
| G11 | Lancaster strips no prefix (PRD 166) | footprint 0 |
| G12 | regexp stemmer removes every match (PRD 172) | footprint 0 |
| G15 | Penn Treebank point split off only at the end of the text (PRD 103) | footprint 5, and 2 of its tests are G14's |
| G19 | tree length = immediate children (PRD 254, Contract 194) | footprint 0 |
| G21 | grammar start symbol = first production's left-hand side (PRD 245) | footprint 0 |
| G22 | Naive Bayes estimates smoothed (PRD 276) | footprint 0 |

Every candidate passed the probe check (base upstream on all 24; each copy alternative on its own
item and upstream on the other 23; `work/probe_check.log`).
