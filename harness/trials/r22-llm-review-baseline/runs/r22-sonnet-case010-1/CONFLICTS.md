# Specification conflicts

Files: PRD = `spec/Full_PRD.md`, IC = `spec/Interface_Contract.md`.

1. **Regexp tokenizer: discard_empty default**
   - PRD, FP-01 Regular-expression tokenizer: "Empty pieces are dropped unless the caller turns empty-discarding off (it is on by default)."
   - IC, Tokenizers: "`discard_empty` is off unless the caller passes `discard_empty=True`."
   - With no argument, empty pieces are either dropped (PRD) or kept (IC).

2. **Edit distance with transpositions**
   - PRD, FP-07 Edit distance: with transpositions on it is unrestricted Damerau–Levenshtein, and "characters may also be inserted between, or deleted from between, the two transposed characters."
   - IC, Metrics, `edit_distance`: "only two characters that stand next to each other in both strings may be transposed, and nothing may be inserted or deleted between them."
   - The unrestricted and the restricted (optimal string alignment) variants give different distances for inputs such as "ca" vs "abc".

3. **Accuracy on lists of different lengths**
   - PRD, FP-07 Accuracy (Normal behavior): "For lists of different lengths, it is that fraction over the positions both lists have." (a number is returned)
   - PRD, FP-07 Boundary, FP-06 Boundary, and IC (`lingora.metrics.accuracy`): lists of different lengths do not succeed / make it raise.
   - The same call either returns a fraction or raises.

4. **Precision/recall argument types**
   - PRD, FP-07 Precision, recall and f-measure: "A list or tuple given as either argument is read as the set of its elements."
   - PRD, FP-07 Boundary: "Lists, tuples and other non-set collections are refused." IC: "A non-set argument makes the call raise."
   - A list argument is either accepted as a set or refused.

5. **F-measure when precision or recall is 0**
   - PRD, FP-07 Normal behavior: f-measure "is 0 when precision or recall is 0."
   - PRD, FP-07 Boundary: f-measure "when the two sets share no element return[s] no number", which is distinguishable from 0.
   - With non-empty sets that share no element, precision and recall are 0, so the result is both 0 and no number.

6. **BLEU default weights**
   - PRD, FP-07 BLEU: "The default is equal weights on unigrams through 4-grams."
   - IC, Metrics, `bleu`: "When `weights` is omitted, unigrams and bigrams are weighted equally and longer n-grams are not scored."
   - The default is either four equally weighted orders or two.

7. **Porter stemmer: default lowercasing**
   - PRD, FP-02 Porter, default mode: "The word is lowercased first, unless the caller turns lowercasing off." Lowercasing is the default.
   - IC, Stemmers: "`to_lowercase` defaults to `False`, so `stem` keeps the letter case it is given."
   - A default call either lowercases the input or keeps its case.

8. **Porter stemmer: "ties"**
   - PRD, FP-02 Porter Step 1a: "a four-letter word ending in *-ies* becomes *-ie* rather than *-i*." *ties* has four letters, so it gives *tie*.
   - IC, Stemmers: "`PorterStemmer` applies Step 1a as published, so *ties* stems to *ti*."
   - The same default-mode call cannot give both *tie* and *ti*.

9. **Tweet tokenizer: case preservation default**
   - PRD, Non-functional constraints, Unicode: the tweet tokenizer "lowercases its tokens unless the caller asks to preserve case." Lowercasing is the default.
   - PRD, FP-01 Tweet tokenizer: "With case preservation off (it is on by default), tokens are lowercased." Preserving case is the default.
   - The default either lowercases or preserves case.

10. **Touching chunks**
    - PRD, FP-04 Chunk rule: "Two matches that touch are two separate chunks."
    - PRD, FP-04 Chunk rule (same bullet): "Chunks that touch, with no token between them, are joined into one chunk."
    - Two adjacent matches are either two chunks or one.

11. **Tree built from a string child list**
    - PRD, FP-05 Trees: "A string given in place of the child list is taken as a single leaf."
    - PRD, FP-05 Boundary: building a tree from a label and a string child list "is refused." IC, Trees: a `str` given as `children` makes `Tree` raise.
    - The same construction is either accepted or refused.

12. **Parser given a token no production produces**
    - PRD, FP-05 Chart parser: gives "none for a token list the grammar does not derive (including one holding a token that no production produces)", meaning an empty result.
    - PRD, FP-05 Boundary: a parser given such a token "does **not** succeed", distinguishable from an empty set of parses. IC, Parsing: such a token "makes `parse` raise."
    - The same input gives either an empty result or a failure.

13. **Generator and the empty-string terminal**
    - PRD, FP-05 Generator: "A quoted empty string contributes an empty-string token."
    - IC, Generation: "A terminal that is the empty string adds no token to a sentence."
    - The sentence either contains an empty-string token or does not.
