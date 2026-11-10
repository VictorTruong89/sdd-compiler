# Conflicts in the LINGORA specification

Sources: `spec/Full_PRD.md` (PRD), `spec/Interface_Contract.md` (Contract), `spec/Hardware_Requirements.md` (Hardware). Line numbers refer to those files.

---

### C-01: Porter default lowercasing
- **PRD**, FP-02 "Porter, default mode" (line 155): "The word is lowercased first, unless the caller turns lowercasing off."
- **Contract**, "Stemmers — `lingora.stem`" (line 99): "`to_lowercase` defaults to `False`, so `stem` keeps the letter case it is given."
- **Why:** `PorterStemmer().stem(word)` with default arguments must both lowercase the word (PRD) and keep its case (Contract).

### C-02: Porter Step 1a on "ties"
- **PRD**, FP-02 "Porter, default mode" (line 158): "In Step 1a, a four-letter word ending in *-ies* becomes *-ie* rather than *-i*." Default mode is the LINGORA extensions (line 148).
- **Contract**, "Stemmers — `lingora.stem`" (line 99): "`PorterStemmer` applies Step 1a as published, so *ties* stems to *ti*."
- **Why:** "ties" is four letters ending in *-ies*, so the default-mode rule must give *tie*, while the Contract says the default-mode result is *ti* from the unextended Step 1a.

### C-03: Chunk rule on touching matches
- **PRD**, FP-04 "Chunk rule" (line 222), same bullet: "Two matches that touch are two separate chunks." and later in the same bullet: "Chunks that touch, with no token between them, are joined into one chunk."
- **Why:** Two touching matches of one rule become two chunks by the first sentence, and those two touching chunks must be joined into one by the second.

### C-04: Recursive tree built from a string child list
- **PRD**, FP-05 "Trees" (line 255): "A string given in place of the child list is taken as a single leaf."
- **PRD**, FP-05 "Boundary / error behavior" (line 263): "Building a tree from a label and a **string** as the child list (instead of a list of children) is refused."
- **Contract**, "Trees — `lingora.tree`" (line 195): "A `str` given as `children` … makes `Tree` raise."
- **Why:** The same call `Tree(label, "x")` must either return a tree with one leaf or raise, and the PRD states both.

### C-05: Chart parser on a token no production produces
- **PRD**, FP-05 "Chart parser" (line 251): the parser returns "none for a token list the grammar does not derive (including one holding a token that no production produces)."
- **PRD**, FP-05 "Boundary / error behavior" (line 264): a token no production produces means the parser "does **not** succeed", and this is "distinguishable from a successful empty set of parses, which is the outcome for a list of covered tokens that the grammar does not derive."
- **Contract**, "Grammars and parsers" (line 175): "A token that no production produces makes `parse` raise."
- **Why:** The same input must give an empty result (PRD line 251) and must raise (PRD line 264 and Contract line 175).

### C-06: Contract's own statement on empty-result parsing
- **Contract**, "Grammars and parsers" (line 174): "A token list the grammar does not derive gives an empty iterator."
- **Contract**, "Grammars and parsers" (line 175): "A token that no production produces makes `parse` raise."
- **Why:** A token list that contains a token no production produces is a token list the grammar does not derive, so line 174 requires an empty iterator and line 175 requires an exception for the same input.

### C-07: Empty terminal in the generator
- **PRD**, FP-05 "Generator" (line 253): "A quoted empty string contributes an empty-string token. An empty production contributes no token."
- **Contract**, "Grammars and parsers" (line 180): "A terminal that is the empty string adds no token to a sentence."
- **Why:** A quoted empty string either adds an empty-string token to the sentence (PRD) or adds no token (Contract).

### C-08: Accuracy on lists of different lengths
- **PRD**, FP-07 "Accuracy" (line 306): "For lists of different lengths, it is that fraction over the positions both lists have."
- **PRD**, FP-07 "Boundary / error behavior" (line 319): "Accuracy on two lists of different lengths does not succeed."
- **Contract**, "Metrics" (line 231): "Lists of different lengths make it raise."
- **Why:** The same call `accuracy(a, b)` with lists of unequal length must either return a fraction over the common positions or fail.

### C-09: Precision and recall on lists or tuples
- **PRD**, FP-07 "Precision, recall and f-measure" (line 308): "A list or tuple given as either argument is read as the set of its elements."
- **PRD**, FP-07 "Boundary / error behavior" (line 320): "Precision and recall require sets. Lists, tuples and other non-set collections are refused."
- **Contract**, "Metrics" (line 238): "A non-set argument makes the call raise."
- **Why:** A list argument to `precision` must either be converted to a set and scored (line 308) or be refused (lines 320 and 238).

### C-10: F-measure when precision or recall is 0
- **PRD**, FP-07 "Precision, recall and f-measure" (line 309): "It is 0 when precision or recall is 0."
- **PRD**, FP-07 "Boundary / error behavior" (line 320): "f-measure when either set is empty or when the two sets share no element return no number."
- **Why:** Two non-empty sets with no shared element have precision 0 and recall 0, so line 309 requires the number 0 and line 320 requires no number.

### C-11: Edit distance with transpositions
- **PRD**, FP-07 "Edit distance" (line 303): "With transpositions on … the distance is the unrestricted Damerau–Levenshtein distance … characters may also be inserted between, or deleted from between, the two transposed characters."
- **Contract**, "Metrics" (line 235): "With `transpositions=True`, only two characters that stand next to each other in both strings may be transposed, and nothing may be inserted or deleted between them."
- **Why:** For a pair such as "ca" and "abc", the unrestricted distance (PRD) is 2 while the restricted distance (Contract) is 3, so the two definitions give different numbers for the same call.

### C-12: BLEU default weights
- **PRD**, FP-07 "BLEU" (line 312): "The default is equal weights on unigrams through 4-grams."
- **Contract**, "Metrics" (line 242): "When `weights` is omitted, unigrams and bigrams are weighted equally and longer n-grams are not scored."
- **Why:** The same call `bleu(refs, hyp)` cannot both weight 1- to 4-grams and weight only 1- and 2-grams.

### C-13: Regular-expression tokenizer, empty-piece default
- **PRD**, FP-01 "Regular-expression tokenizer" (line 120): "Empty pieces are dropped unless the caller turns empty-discarding off (it is on by default)."
- **Contract**, "Tokenizers" (line 66): "`discard_empty` is off unless the caller passes `discard_empty=True`."
- **Why:** The default `RegexpTokenizer(pattern)` either drops empty pieces (PRD) or keeps them (Contract).

### C-14: Tweet tokenizer lowercasing default
- **PRD**, Non-functional constraints, "Unicode" (line 65): the tweet-style tokenizer "lowercases its tokens unless the caller asks to preserve case."
- **PRD**, FP-01 "Tweet tokenizer" (line 127): "With case preservation off (it is on by default), tokens are lowercased, except emoticons."
- **Why:** Under default arguments the tweet tokenizer must lowercase its tokens (line 65) and must preserve case (line 127), since the PRD says case preservation is on by default.

### C-15: Symbol type returned for a nonterminal
- **Contract**, "Grammars and parsers" (line 169): "A nonterminal is returned as a symbol: a `str`, or an object whose `str()` is the nonterminal's name. Which of the two is the implementer's choice."
- **Contract**, "Grammars and parsers" (line 170): "In `rhs()` … A nonterminal appears as a symbol that is not a `str`."
- **Why:** If the implementer chooses `str` for symbols, as line 169 allows, then `rhs()` returns a `str` for a nonterminal, which line 170 forbids.
