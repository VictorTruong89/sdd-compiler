# Conflicts in the LINGORA specification

Sources: `spec/Full_PRD.md` (PRD, line numbers as in the file), `spec/Interface_Contract.md` (IC, by section), `spec/Hardware_Requirements.md` (HW).

## C-01: Porter default mode and Step 1a (`ties`)

- **PRD FP-02, line 148 and 158:** the default mode is "the LINGORA extensions", and "In Step 1a, a four-letter word ending in *-ies* becomes *-ie* rather than *-i*."
- **IC, "Stemmers", bullet under the code block:** "`PorterStemmer` applies Step 1a as published, so *ties* stems to *ti*." The code block gives `PorterStemmer().stem(word, to_lowercase=…)  # default mode`.

Why they cannot both hold: under the default mode, *ties* (four letters ending in *-ies*) must stem to *tie* per PRD, but IC says the default applies the published Step 1a and gives *ti*.

## C-02: Porter `to_lowercase` default

- **PRD FP-02, line 155:** "The word is lowercased first, unless the caller turns lowercasing off."
- **IC, "Stemmers", bullet under the code block:** "`to_lowercase` defaults to `False`, so `stem` keeps the letter case it is given."

Why they cannot both hold: a call that omits the flag must both lowercase the word (PRD) and keep its case (IC).

## C-03: Tweet tokenizer case handling by default

- **PRD Non-functional constraints, line 65:** the tweet tokenizer "lowercases its tokens unless the caller asks to preserve case."
- **PRD FP-01, line 127:** "With case preservation off (it is on by default), tokens are lowercased, except emoticons."

Why they cannot both hold: the first says the default lowercases tokens, while the second says the default preserves case, so a default call cannot both lowercase and keep case.

## C-04: Penn Treebank treatment of a trailing apostrophe

- **PRD FP-01, line 104:** "a bare apostrophe ending a word, are split from the word they follow and become tokens of their own."
- **PRD FP-01, line 106:** "An apostrophe that does not begin one of those clitics stays inside its word."

Why they cannot both hold: a word-final apostrophe (e.g. *boys'*) does not begin a clitic, so line 106 keeps it in the word, while line 104 splits it off as its own token.

## C-05: Regex tokenizer `discard_empty` default

- **PRD FP-01, line 120:** "Empty pieces are dropped unless the caller turns empty-discarding off (it is on by default)."
- **IC, "Tokenizers":** "`discard_empty` is off unless the caller passes `discard_empty=True`."

Why they cannot both hold: the PRD makes the default drop empty pieces and the IC makes the default keep them, so the same call with no flag gives different token lists.

## C-06: Chunk matches that touch

- **PRD FP-04, line 222:** "Two matches that touch are two separate chunks." and, in the same paragraph, "Chunks that touch, with no token between them, are joined into one chunk."

Why they cannot both hold: two adjacent matches with no token between them are either two chunks or one joined chunk, and the same paragraph states both.

## C-07: Tree built with a string as the child list

- **PRD FP-05, Normal behavior "Trees", line 255:** "A string given in place of the child list is taken as a single leaf."
- **PRD FP-05, Boundary behavior, line 263:** "Building a tree from a label and a **string** as the child list (instead of a list of children) is refused."
- **IC, "Trees":** "A `str` given as `children`, or omitting `children`, makes `Tree` raise."

Why they cannot both hold: `Tree(label, "x")` either returns a tree whose single child is the leaf `"x"` or raises an exception, and the spec says both.

## C-08: Generator output for an empty-string terminal

- **PRD FP-05, Normal behavior "Generator", line 253:** "A quoted empty string contributes an empty-string token."
- **IC, "Grammars and parsers" (Generation):** "A terminal that is the empty string adds no token to a sentence."

Why they cannot both hold: a quoted empty terminal either adds an empty-string token to each sentence or adds no token, not both.

## C-09: Chart parser given a token no production produces

- **PRD FP-05, Normal behavior "Chart parser", line 251:** "none for a token list the grammar does not derive (including one holding a token that no production produces)".
- **PRD FP-05, Boundary behavior, line 264:** "A parser given a token list that contains a token no production of the grammar produces does **not** succeed. That failure is distinguishable from a successful empty set of parses, which is the outcome for a list of covered tokens that the grammar does not derive."
- **IC, "Grammars and parsers" (Parsing):** "A token that no production produces makes `parse` raise."

Why they cannot both hold: for such a token list the parser must either return no parses (line 251) or fail with an error, distinct from the empty result (lines 264 and IC).

## C-10: Edit distance with transpositions

- **PRD FP-07, Normal behavior "Edit distance", line 303:** "the distance is the unrestricted Damerau–Levenshtein distance... characters may also be inserted between, or deleted from between, the two transposed characters."
- **IC, "Metrics", `edit_distance`:** "With `transpositions=True`, only two characters that stand next to each other in both strings may be transposed, and nothing may be inserted or deleted between them."

Why they cannot both hold: the unrestricted Damerau–Levenshtein distance allows insertions between transposed characters, which the IC forbids, so the two give different distances for the same pair of strings (e.g. *ca* → *abc*: 2 vs 3).

## C-11: Accuracy on lists of different lengths

- **PRD FP-07, Normal behavior "Accuracy", line 306:** "For lists of different lengths, it is that fraction over the positions both lists have."
- **PRD FP-07, Boundary behavior, line 319:** "Accuracy on two lists of different lengths does not succeed." (also PRD FP-06, line 288)
- **IC, "Metrics", `lingora.metrics.accuracy`:** "Lists of different lengths make it raise."

Why they cannot both hold: for two lists of different lengths the call must either return a fraction over the shared positions or fail.

## C-12: Precision, recall and f-measure given lists

- **PRD FP-07, Normal behavior, line 308:** "A list or tuple given as either argument is read as the set of its elements."
- **PRD FP-07, Boundary behavior, line 320:** "Precision and recall require sets. Lists, tuples and other non-set collections are refused."
- **IC, "Metrics":** "`precision`, `recall` and `f_measure`: `reference` and `test` are `set`s (or `frozenset`s). A non-set argument makes the call raise."

Why they cannot both hold: a list argument is either converted to a set and scored or refused with an error.

## C-13: F-measure when precision or recall is 0 versus when the sets share no element

- **PRD FP-07, Normal behavior, line 309:** "It is 0 when precision or recall is 0."
- **PRD FP-07, Boundary behavior, line 320:** "f-measure when either set is empty or when the two sets share no element return no number."

Why they cannot both hold: disjoint non-empty sets have precision 0 and recall 0, so the normal rule requires the number 0 while the boundary rule requires no number.

## C-14: BLEU default n-gram weights

- **PRD FP-07, Normal behavior "BLEU", line 312:** "The default is equal weights on unigrams through 4-grams."
- **IC, "Metrics", `bleu`:** "When `weights` is omitted, unigrams and bigrams are weighted equally and longer n-grams are not scored."

Why they cannot both hold: the omitted-weights call must score the 1–4-gram orders (PRD) or only the 1- and 2-gram orders (IC), which gives different scores for the same input.
