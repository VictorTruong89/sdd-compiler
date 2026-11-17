# LINGORA build notes

This file records how the specification's disagreements were resolved and what
was built. Sources: `spec/Full_PRD.md` (PRD), `spec/Interface_Contract.md`
(Contract), `spec/Hardware_Requirements.md` (Hardware). Each conflict below
quotes both sides with their location, then states the choice.

**Rule used.** The Contract says it defines shapes and signatures, and that
"the PRD states the default's behaviour wherever it matters" (Contract line 13)
and that computed results come from the PRD (Contract line 5). So where the
two disagree on a default or a computed result, the PRD wins. Where one side
refuses an input and the other returns a value, the refusal wins whenever the
PRD's own error section says "does not succeed" for that input.

## Conflicts and decisions

### C-01: Porter default lowercasing
- PRD, FP-02 "Porter, default mode", line 155: "The word is lowercased first, unless the caller turns lowercasing off."
- Contract, "Stemmers", line 99: "`to_lowercase` defaults to `False`, so `stem` keeps the letter case it is given."
- **Built:** `PorterStemmer().stem(word, to_lowercase=True)`. Default-call results are lowercased, as the PRD states. Passing `to_lowercase=False` keeps case.

### C-02: Porter Step 1a on "ties"
- PRD, FP-02, line 158: "In Step 1a, a four-letter word ending in *-ies* becomes *-ie* rather than *-i*." Default mode is LINGORA extensions (line 148).
- Contract, "Stemmers", line 99: "`PorterStemmer` applies Step 1a as published, so *ties* stems to *ti*."
- **Built:** the default mode gives `ties` → `tie`. `ti` is what the published algorithm gives, and it is available as `PorterStemmer(mode="ORIGINAL_ALGORITHM")`.

### C-03: Chunk rule on touching matches
- PRD, FP-04 "Chunk rule", line 222: "Two matches that touch are two separate chunks." and, in the same bullet, "Chunks that touch, with no token between them, are joined into one chunk."
- **Built:** matches are found left to right, and touching matches of one clause end up as one chunk. The later sentence (the join) is applied after each rule. A chunk from an earlier clause is not joined with a chunk from a later clause, because earlier chunks are opaque units there.

### C-04: Tree built from a string child list
- PRD, FP-05 "Trees", line 255: "A string given in place of the child list is taken as a single leaf."
- PRD, FP-05 "Boundary", line 263, and Contract, "Trees", line 195: refused / "makes `Tree` raise."
- **Built:** `Tree(label, "x")` raises `TypeError`. Omitting the child list also raises. `Tree(label, [])` is valid.

### C-05 / C-06: Chart parser on a token no production produces
- PRD, FP-05 "Chart parser", line 251: returns none for an underived list "including one holding a token that no production produces".
- PRD, FP-05 "Boundary", line 264: that case "does **not** succeed", distinguishable from an empty result. Contract, "Grammars and parsers", line 175: "makes `parse` raise." Contract line 174 also says an underived list "gives an empty iterator."
- **Built:** a token no production produces raises `ValueError` (raised by the call, before iteration). A list of covered tokens that the grammar does not derive gives an empty iterator.

### C-07: Empty terminal in the generator
- PRD, FP-05 "Generator", line 253: "A quoted empty string contributes an empty-string token."
- Contract, "Grammars and parsers", line 180: "A terminal that is the empty string adds no token to a sentence."
- **Built:** the PRD's rule (a quoted `''` contributes a `''` token). An empty production contributes nothing.

### C-08: Accuracy on lists of different lengths
- PRD, FP-07 "Accuracy", line 306: a fraction over the common positions. PRD, line 319: "does not succeed." Contract, "Metrics", line 231: "make it raise."
- **Built:** raises `ValueError`. Empty equal-length lists also raise `ValueError`, because the fraction is undefined.

### C-09: Precision and recall on lists or tuples
- PRD, FP-07, line 308: "A list or tuple given as either argument is read as the set of its elements." PRD, line 320: "Lists, tuples and other non-set collections are refused." Contract, line 238: "A non-set argument makes the call raise."
- **Built:** raises `TypeError` (the refusal, which is stated twice).

### C-10: F-measure when precision or recall is 0
- PRD, FP-07, line 309: "It is 0 when precision or recall is 0." PRD, line 320: "f-measure ... when the two sets share no element return no number."
- **Built:** `None` when the sets share no element (or either is empty). With a shared element both precision and recall are positive, so the `0` branch is not reachable.

### C-11: Edit distance with transpositions
- PRD, FP-07, line 303: the unrestricted Damerau–Levenshtein distance, with insertions allowed between transposed characters. Contract, "Metrics", line 235: only adjacent transpositions, nothing inserted between them.
- **Built:** the PRD's unrestricted distance (Lowrance–Wagner). For `("ca", "abc")` it gives 2.

### C-12: BLEU default weights
- PRD, FP-07 "BLEU", line 312: "equal weights on unigrams through 4-grams." Contract, "Metrics", line 242: "unigrams and bigrams are weighted equally."
- **Built:** the PRD's default, 0.25 for each of 1- to 4-grams.

### C-13: Regular-expression tokenizer, empty pieces
- PRD, FP-01, line 120: empty pieces are dropped "(it is on by default)." Contract, "Tokenizers", line 66: "`discard_empty` is off unless the caller passes `discard_empty=True`."
- **Built:** `discard_empty=True` by default, as the PRD states.

### C-14: Tweet tokenizer case default
- PRD, Non-functional "Unicode", line 65: lowercases "unless the caller asks to preserve case." PRD, FP-01, line 127: "With case preservation off (it is on by default)".
- **Built:** `preserve_case=True` by default, so tokens keep their case unless the caller passes `preserve_case=False`.

### C-15: Symbol type for nonterminals
- Contract, "Grammars and parsers", line 169: a nonterminal is "a `str`, or an object whose `str()` is the nonterminal's name. Which of the two is the implementer's choice." Line 170: in `rhs()`, "A nonterminal appears as a symbol that is not a `str`."
- **Built:** `Nonterminal`, a non-`str` object whose `str()` is its name. Terminals in `rhs()` are plain `str`s.

## Other choices (not conflicts)

- **Recommended word tokenizer, start quote.** The PRD (FP-01, line 108) says a straight double quote at the very start becomes the closing-quote token. That is an explicit override of the Penn rule, and it is implemented.
- **Resources.** `data.path` starts from the `LINGORA_DATA` environment variable (`os.pathsep`-separated), and is empty otherwise. No default directory is searched.
- **Punkt.** Implemented from the packaged files (`abbrev_types`, `sent_starters`, `collocations`, `ortho_context`). The decision rules are a simplified Kiss–Strunk pass, not a line-for-line port. A period after an abbreviation breaks only before a capitalised sentence starter. An ordinary period breaks unless the next word starts lowercase. A collocation never breaks.
- **Averaged perceptron.** Feature templates, normalisation and the tag dictionary follow textblob-aptagger as described in the PRD. The universal map for English reads `en-ptb.map`. For Russian, the category is the part before `=`, mapped by a fixed table.
- **Decision tree.** ID3-style splitting on information gain. Absent features count as the `None` value. An unseen value falls back to the node's majority label.
- **Naive Bayes.** Add-one smoothing per feature value. Feature names never seen in training are ignored.
- **CLI.** Implemented without a third-party framework, so the runtime has no dependencies. `cli.main(args, standalone_mode)` returns the status code and calls `sys.exit` when `standalone_mode=True`. The command checks the Punkt model before reading stdin, so a missing model writes no token line and exits 1.
- **`accuracy` of an empty gold list** (classifier) raises `ValueError`. It is undefined.

## Known gaps (not built)

- **Snowball:** only `english` (Porter2) and `porter` (original Porter) are implemented. The other 14 supported language names are accepted by the name check, but constructing them raises `NotImplementedError`.
- **ISRI, Cistem, RSLP, ARLSTem/ARLSTem2:** `ARLSTem` and `ARLSTem2` are present as stubs that raise `NotImplementedError`. ISRI, Cistem and RSLP are not provided, since the Contract's import list does not name them.
- **WordNet lemmatizer:** raises `LookupError` when WordNet is not visible; when it is visible it raises `NotImplementedError`.
- **`ne_chunk`:** checks the model and wordlist (raises `LookupError` when missing). When both are visible it raises `NotImplementedError`, because the published model layout is not implemented.
- **Lancaster:** the rule table is reproduced from memory of the published Paice/Husk rules. Results for unusual words may differ from the published stemmer.
- **Porter LINGORA extensions:** implemented from the PRD's list. The irregular-form table is a small internal set (its contents are outside the spec).
