# Implementation notes

The package is `lingora/` at the repository root (flat layout, pure Python,
no third-party dependencies). `spec/` is unchanged.

## Spec conflicts and the choice made

1. **Porter `to_lowercase` default.**
   - PRD `spec/Full_PRD.md`, FP-02 "Porter, default mode": the word is
     lowercased first "unless the caller turns lowercasing off" (implies on by default).
   - Interface `spec/Interface_Contract.md`, "Stemmers": `to_lowercase` "defaults to `False`".
   - **Built:** default `False` (the signature is the concrete contract).

2. **Porter `ties`.**
   - Interface, "Stemmers": "`PorterStemmer` applies Step 1a as published, so *ties* stems to *ti*".
   - PRD FP-02, default-mode extensions: a four-letter word ending in *-ies* becomes *-ie*.
   - **Built:** the PRD extension, so `ties` → `tie`. The published Step 1a alone
     (`ties` → `ti`) is used only for the `porter` Snowball name.

3. **BLEU default weights.**
   - PRD FP-07: equal weights on unigrams through 4-grams.
   - Interface, "Metrics": when `weights` is omitted, "unigrams and bigrams are weighted equally".
   - **Built:** the PRD default, `(0.25, 0.25, 0.25, 0.25)`.

4. **Accuracy on lists of different lengths.**
   - PRD FP-07 normal behaviour: "for lists of different lengths, it is that fraction over the positions both lists have".
   - PRD FP-07 boundary and Interface, "Metrics": such a call must raise.
   - **Built:** raises `ValueError`.

5. **Quoted empty string in generation.**
   - PRD FP-05 generator: a quoted empty string "contributes an empty-string token".
   - Interface, "Grammars and parsers": "A terminal that is the empty string adds no token to a sentence".
   - **Built:** no token (Interface). The chart and shift-reduce parsers also treat `""` as matching no input.

6. **Chunk joining.**
   - PRD FP-04 says "Two matches that touch are two separate chunks" and also "Chunks that touch, with no token between them, are joined into one chunk".
   - **Built:** matches of one chunk rule stay separate. Chunks are not joined across rules or clauses.
     Later clauses see earlier chunks as single units tagged with their label.

7. **Chunk root label.** The spec leaves the sentence-root label to the implementer.
   **Built:** `SENT`. It is distinct from clause labels.

## Implementation choices (not conflicts)

- `lingora.data.path` starts with the directories in `LINGORA_DATA` (os.pathsep-separated) and `~/.lingora/data`. Packaged resources are found by directory (or file for stopwords) existence.
- Punkt: the sentence splitter follows Kiss and Strunk (2006), using the packaged abbreviation, collocation, sentence-starter and orthographic-context files. Missing individual parameter files count as empty; a missing language directory raises.
- Averaged perceptron: a faithful port of the textblob-aptagger feature templates and normalisation. Universal mapping for English uses `en-ptb.map`. For Russian, the table is the implementer's choice, keyed by the first comma/`=`-separated part of the tag.
- Tree children may be strings or tuples (`(token, tag)` leaves from chunking).
- The command line is built on `argparse` (no `click` dependency). `cli.main(args=..., standalone_mode=True)` exits 0 on success and 1 on failure. On failure no token line is written for that input.
- `ARLSTem`/`ARLSTem2` are approximate light stemmers and are outside the spec.
- Named-entity chunking: `ne_chunk` raises when resources are missing. When they are present it raises `NotImplementedError`, because the maxent decoder is not implemented.

## Known gaps

- **Snowball:** only `english` (Porter2) and `porter` (original Porter) are implemented. The other listed languages raise `NotImplementedError` naming the language. Those stemmers are not implemented.
- **Lancaster:** the rule table was reconstructed from memory of the published Paice/Husk table and is incomplete. For example, `presumably` is not reduced to `presum`. Treat its results as approximate.
- **Shift-reduce parser:** a single greedy pass with no backtracking, as the spec says. It can return no tree for sentences that a chart parser accepts.
- **Not exported by the interface:** the bigram, trigram and affix taggers, ISRI, Cistem and RSLP are not provided.
- **WordNet lemmatizer:** noun-index suffix rules only.
- **Recommended-tokenizer `cannot`:** kept as one token. The Treebank tokenizer splits it into `can` `not`.
