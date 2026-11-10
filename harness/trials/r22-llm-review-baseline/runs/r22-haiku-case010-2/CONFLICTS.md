# Specification conflicts

Each entry names the statements that disagree, where they are, and why both cannot hold for the same case.
Files: `Full_PRD.md` (PRD), `Interface_Contract.md` (IC), `Hardware_Requirements.md` (HW).

## C-01: Tree child given as a string

- PRD, FP-05 "Trees" (normal behavior): "A string given in place of the child list is taken as a single leaf."
- PRD, FP-05 "Boundary / error behavior": "Building a tree from a label and a **string** as the child list (instead of a list of children) is refused."
- IC, "Trees — `lingora.tree`": "A `str` given as `children`, or omitting `children`, makes `Tree` raise."

A `Tree(label, "x")` call either returns a tree with one leaf or raises, and the PRD states both outcomes.

## C-02: Porter stemmer lowercases by default

- PRD, FP-02 "Porter, default mode": "The word is lowercased first, unless the caller turns lowercasing off."
- IC, "Stemmers — `lingora.stem`": "`to_lowercase` defaults to `False`, so `stem` keeps the letter case it is given."

With no argument, `PorterStemmer().stem("Running")` must return either a lowercased stem or a stem that keeps the capital letter; it cannot do both.

## C-03: Porter Step 1a result for "ties"

- PRD, FP-02 "Porter, default mode": "In Step 1a, a four-letter word ending in *-ies* becomes *-ie* rather than *-i*." The PRD says the default mode is the LINGORA extensions (FP-02 "Porter" intro).
- IC, "Stemmers — `lingora.stem`": "`PorterStemmer` applies Step 1a as published, so *ties* stems to *ti*."

The default mode is required to map "ties" to "tie" by the PRD and to "ti" by the IC; the stem of a single word under the default mode cannot be both.

## C-04: Tweet tokenizer case preservation default

- PRD, FP-01 "Tweet tokenizer": "With case preservation off (it is on by default), tokens are lowercased, except emoticons."
- PRD, "Non-functional constraints" (Unicode): "that tokenizer lowercases its tokens unless the caller asks to preserve case."

The first says lowercasing does not happen by default; the second says it happens unless the caller asks, which means by default. The same call with no options cannot both lowercase and not lowercase.

## C-05: Regular-expression tokenizer discards empty pieces by default

- PRD, FP-01 "Regular-expression tokenizer": "Empty pieces are dropped unless the caller turns empty-discarding off (it is on by default)."
- IC, "Tokenizers — `lingora.tokenize`": "`discard_empty` is off unless the caller passes `discard_empty=True`."

For `RegexpTokenizer(r",").tokenize("a,,b")` the result either contains an empty string or does not, and the two documents give opposite answers.

## C-06: Accuracy on lists of different lengths

- PRD, FP-07 "Accuracy" (normal behavior): "For lists of different lengths, it is that fraction over the positions both lists have."
- PRD, FP-07 "Boundary / error behavior": "Accuracy on two lists of different lengths does not succeed."
- PRD, FP-06 "Boundary / error behavior": "Two-list accuracy (FP-07) on lists of different lengths does not succeed."
- IC, "Metrics": "Lists of different lengths make it raise."

The normal-behavior rule returns a fraction for different-length lists, while the boundary rules and the IC require a failure for the same input.

## C-07: Precision, recall and f-measure accept lists

- PRD, FP-07 "Precision, recall and f-measure" (normal behavior): "A list or tuple given as either argument is read as the set of its elements."
- PRD, FP-07 "Boundary / error behavior": "Precision and recall require sets. Lists, tuples and other non-set collections are refused."
- IC, "Metrics": "A non-set argument makes the call raise."

`precision([1, 2], {1})` must either return a number (normal behavior) or raise (boundary behavior and IC).

## C-08: F-measure when the sets share no element

- PRD, FP-07 "Precision, recall and f-measure" (normal behavior): "It is 0 when precision or recall is 0."
- PRD, FP-07 "Boundary / error behavior": "f-measure when either set is empty or when the two sets share no element return no number."

For non-empty sets with no common element, precision and recall are both 0, so the normal rule requires 0 and the boundary rule requires no number (`None`).

## C-09: Transposition rule in edit distance

- PRD, FP-07 "Edit distance" (normal behavior): "the distance is the unrestricted Damerau–Levenshtein distance ... characters may also be inserted between, or deleted from between, the two transposed characters."
- IC, "Metrics", `edit_distance`: "only two characters that stand next to each other in both strings may be transposed, and nothing may be inserted or deleted between them."

For `edit_distance("ca", "abc", transpositions=True)`, unrestricted Damerau–Levenshtein gives 2 and the restricted (optimal string alignment) form gives 3, so the two documents assign different values to the same call.

## C-10: BLEU default weights

- PRD, FP-07 "BLEU" (normal behavior): "The default is equal weights on unigrams through 4-grams."
- IC, "Metrics", `bleu`: "When `weights` is omitted, unigrams and bigrams are weighted equally and longer n-grams are not scored."

With `weights` omitted, the PRD scores 4-grams and the IC does not, so the same call returns different scores under the two documents.

## C-11: Empty-string terminal in generation

- PRD, FP-05 "Generator" (normal behavior): "A quoted empty string contributes an empty-string token. An empty production contributes no token."
- IC, "Grammars and parsers", "Generation": "A terminal that is the empty string adds no token to a sentence."

For the production `S -> ""`, the PRD yields a sentence `['']` and the IC yields `[]`.

## C-12: Chart parser result for a token no production produces

- PRD, FP-05 "Chart parser" (normal behavior): "none for a token list the grammar does not derive (including one holding a token that no production produces)".
- PRD, FP-05 "Boundary / error behavior": "A parser given a token list that contains a token no production of the grammar produces does **not** succeed. That failure is distinguishable from a successful empty set of parses, which is the outcome for a list of covered tokens that the grammar does not derive."
- IC, "Grammars and parsers", "Parsing": "A token that no production produces makes `parse` raise."

The normal rule says the chart parser returns no parses for such a list and the boundary rule says the call fails. The same input cannot both return an empty set of parses and fail.

## C-13: Adjacent matches of one chunk rule

- PRD, FP-04 "Chunk rule" (normal behavior), same bullet: "Two matches that touch are two separate chunks." and "Chunks that touch, with no token between them, are joined into one chunk."

For a rule such as `<DT><NN>` applied to `the dog the cat`, two adjacent matches that touch must be two chunks (first statement) and one joined chunk (second statement). The bullet gives both outcomes for the same case.
