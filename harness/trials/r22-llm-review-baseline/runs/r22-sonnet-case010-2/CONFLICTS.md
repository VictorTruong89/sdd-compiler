# Specification conflicts

Abbreviations: PRD = spec/Full_PRD.md, IC = spec/Interface_Contract.md.

1. **Porter `to_lowercase` default.**
   - PRD, FP-02 Porter default mode: "The word is lowercased first, unless the caller turns lowercasing off."
   - IC, Stemmers: "`to_lowercase` defaults to `False`, so `stem` keeps the letter case it is given."
   - Both cannot hold: a call with no `to_lowercase` argument either lowercases the word or keeps its case.

2. **Porter stem of "ties".**
   - PRD, FP-02 Step 1a: "a four-letter word ending in *-ies* becomes *-ie* rather than *-i*", so *ties* becomes *tie*.
   - IC, Stemmers: "`PorterStemmer` applies Step 1a as published, so *ties* stems to *ti*."
   - Both cannot hold: the default-mode stem of *ties* cannot be both *tie* and *ti*.

3. **Regexp tokenizer empty-piece discarding.**
   - PRD, FP-01 Regular-expression tokenizer: empty pieces are dropped unless the caller turns empty-discarding off ("it is on by default").
   - IC, Tokenizers: "`discard_empty` is off unless the caller passes `discard_empty=True`."
   - Both cannot hold: the default is either on or off.

4. **Tweet tokenizer case default.**
   - PRD, Non-functional constraints (Unicode): the tweet tokenizer "lowercases its tokens unless the caller asks to preserve case", so the default lowercases.
   - PRD, FP-01 Tweet tokenizer: "With case preservation off (it is on by default), tokens are lowercased", so the default keeps case.
   - Both cannot hold: with no option given, tokens are either lowercased or not.

5. **Chunks that touch.**
   - PRD, FP-04 Chunk rule: "Two matches that touch are two separate chunks."
   - PRD, FP-04 Chunk rule (same bullet): "Chunks that touch, with no token between them, are joined into one chunk."
   - Both cannot hold: two adjacent chunks are either separate or merged.

6. **Edit distance with transpositions.**
   - PRD, FP-07 Edit distance: with transpositions on the distance is the unrestricted Damerau–Levenshtein distance, and "characters may also be inserted between, or deleted from between, the two transposed characters."
   - IC, Metrics: with `transpositions=True`, "only two characters that stand next to each other in both strings may be transposed, and nothing may be inserted or deleted between them."
   - Both cannot hold: for example, "ca" to "abc" has a different cost under the unrestricted and the restricted definition.

7. **Accuracy on lists of different lengths.**
   - PRD, FP-07 Accuracy (Normal behavior): "For lists of different lengths, it is that fraction over the positions both lists have."
   - PRD, FP-07 and FP-06 Boundary behavior, and IC (`lingora.metrics.accuracy`): lists of different lengths do not succeed / "make it raise".
   - Both cannot hold: unequal-length input either returns a fraction or fails.

8. **Precision and recall with list or tuple arguments.**
   - PRD, FP-07 Precision/recall: "A list or tuple given as either argument is read as the set of its elements."
   - PRD, FP-07 Boundary, and IC (`precision`, `recall`): "Lists, tuples and other non-set collections are refused" / "A non-set argument makes the call raise."
   - Both cannot hold: a list argument is either accepted or refused.

9. **F-measure when the sets share no element.**
   - PRD, FP-07 f-measure: "It is 0 when precision or recall is 0."
   - PRD, FP-07 Boundary: f-measure "when the two sets share no element return no number … distinguishable from the number 0."
   - Both cannot hold: disjoint non-empty sets have precision 0, so the result is either 0 or no number.

10. **BLEU default weights.**
    - PRD, FP-07 BLEU: "The default is equal weights on unigrams through 4-grams."
    - IC, Metrics (`bleu`): "When `weights` is omitted, unigrams and bigrams are weighted equally and longer n-grams are not scored."
    - Both cannot hold: the default weights are either four orders or two.

11. **Tree built from a string child list.**
    - PRD, FP-05 Trees: "A string given in place of the child list is taken as a single leaf."
    - PRD, FP-05 Boundary, and IC (Trees): "Building a tree from a label and a **string** as the child list … is refused" / "A `str` given as `children` … makes `Tree` raise."
    - Both cannot hold: that call either builds a one-leaf tree or is refused.

12. **Token that no production produces.**
    - PRD, FP-05 Chart parser: returns "none for a token list the grammar does not derive (including one holding a token that no production produces)", that is, an empty result.
    - PRD, FP-05 Boundary, and IC (Parsing): a token no production produces makes the parser not succeed, and this is "distinguishable from a successful empty set of parses" (IC: `parse` raises).
    - Both cannot hold: an uncovered token either gives an empty result or fails.

13. **Empty-string terminal in generation.**
    - PRD, FP-05 Generator: "A quoted empty string contributes an empty-string token."
    - IC, Generation: "A terminal that is the empty string adds no token to a sentence."
    - Both cannot hold: the sentence either contains an empty-string token or does not.

14. **Nonterminal symbol type in `rhs()`.**
    - IC, Grammars (Grammar objects), first bullet: a nonterminal is returned as a symbol that is "a `str`, or an object whose `str()` is the nonterminal's name", and which of the two is the implementer's choice.
    - IC, same section, second bullet: in `rhs()`, "a nonterminal appears as a symbol that is not a `str`."
    - Both cannot hold: if symbols may be plain `str`, `rhs()` cannot require that nonterminals are not `str`.
