# Specification conflicts

Files: PRD = `spec/Full_PRD.md`, IC = `spec/Interface_Contract.md`.

## 1. Porter `to_lowercase` default
- PRD, FP-02 Porter default mode: "The word is lowercased first, unless the caller turns lowercasing off."
- IC, Stemmers: "`to_lowercase` defaults to `False`, so `stem` keeps the letter case it is given."
- Why they conflict: for a mixed-case word with no argument, the stemmer either lowercases it (PRD) or keeps its case (IC).

## 2. Porter stem of *ties*
- PRD, FP-02 Porter default mode: "In Step 1a, a four-letter word ending in *-ies* becomes *-ie* rather than *-i*." *ties* has four letters, so it becomes *tie*.
- IC, Stemmers: "`PorterStemmer` applies Step 1a as published, so *ties* stems to *ti*."
- Why they conflict: the default-mode stem of *ties* cannot be both *tie* and *ti*.

## 3. Regular-expression tokenizer `discard_empty` default
- PRD, FP-01 Regular-expression tokenizer: "Empty pieces are dropped unless the caller turns empty-discarding off (it is on by default)."
- IC, Tokenizers: "`discard_empty` is off unless the caller passes `discard_empty=True`."
- Why they conflict: with no argument, empty pieces are dropped (PRD) or kept (IC).

## 4. Tweet tokenizer case handling
- PRD, Non-functional constraints (Unicode): the tweet tokenizer "lowercases its tokens unless the caller asks to preserve case."
- PRD, FP-01 Tweet tokenizer: "With case preservation off (it is on by default), tokens are lowercased."
- Why they conflict: by default the tokens are either lowercased or case-preserved.

## 5. Chunk rule: touching matches
- PRD, FP-04 Chunk rule: "Two matches that touch are two separate chunks."
- PRD, FP-04 Chunk rule, same bullet: "Chunks that touch, with no token between them, are joined into one chunk."
- Why they conflict: two adjacent chunks from the same rule are either kept separate or merged into one.

## 6. Generator and the empty-string terminal
- PRD, FP-05 Generator: "A quoted empty string contributes an empty-string token."
- IC, Grammars and parsers, Generation: "A terminal that is the empty string adds no token to a sentence."
- Why they conflict: a sentence derived through an empty-string terminal either contains an empty-string token or does not.

## 7. Tree constructor given a string as children
- PRD, FP-05 Trees: "A string given in place of the child list is taken as a single leaf."
- PRD, FP-05 Boundary: "Building a tree from a label and a **string** as the child list ... is refused."
- IC, Trees: "A `str` given as `children` ... makes `Tree` raise."
- Why they conflict: `Tree(label, "abc")` is either accepted as a single leaf or refused. The PRD contradicts itself, and the first statement also contradicts the IC.

## 8. Accuracy on lists of different lengths
- PRD, FP-07 Accuracy: "For lists of different lengths, it is that fraction over the positions both lists have."
- PRD, FP-07 Boundary, and FP-06 Boundary: "Accuracy on two lists of different lengths does not succeed."
- IC, Metrics: "Lists of different lengths make it raise."
- Why they conflict: unequal-length lists either produce a score or fail. The PRD contradicts itself, and the first statement also contradicts the IC.

## 9. Precision and recall on lists or tuples
- PRD, FP-07 Precision, recall and f-measure: "A list or tuple given as either argument is read as the set of its elements."
- PRD, FP-07 Boundary: "Lists, tuples and other non-set collections are refused."
- IC, Metrics: "A non-set argument makes the call raise."
- Why they conflict: a list argument is either converted to a set and scored or refused. The PRD contradicts itself, and the first statement also contradicts the IC.

## 10. f-measure when precision or recall is 0
- PRD, FP-07 f-measure: "It is 0 when precision or recall is 0."
- PRD, FP-07 Boundary: f-measure "when the two sets share no element return no number ... distinguishable from the number 0."
- Why they conflict: when the sets share no element, precision and recall are 0, so the result is the number 0 by one statement and no number by the other.

## 11. Edit distance with transpositions
- PRD, FP-07 Edit distance: the distance is the unrestricted Damerau–Levenshtein distance, and "characters may also be inserted between, or deleted from between, the two transposed characters."
- IC, Metrics: "only two characters that stand next to each other in both strings may be transposed, and nothing may be inserted or deleted between them."
- Why they conflict: the unrestricted variant allows edits between the transposed characters and the IC's restricted variant forbids them. The two give different distances, for example *ca* → *abc*: 2 unrestricted, 3 restricted.

## 12. BLEU default weights
- PRD, FP-07 BLEU: "The default is equal weights on unigrams through 4-grams."
- IC, Metrics: "When `weights` is omitted, unigrams and bigrams are weighted equally and longer n-grams are not scored."
- Why they conflict: the default weighting is either four orders (PRD) or two orders (IC), and the two give different scores.
