"""Plant round 19's conflicts into a copy of case010's public spec. No model call.

    python3 notes/plant.py work/spec-planted C01 C03 ...       (from the trial folder)

Method of ../r17-zero2repo-case006-conflicts-24/notes/plant.py. Copies Zero2Repo case010's
`public/*.md` to the output folder and applies the side-B edit of each item named. Each edit adds
text in **one** place, in the spec's own voice and with no marker, so the other place still states
side A (`ANSWER_KEY.md`). Every anchor must occur exactly once, and after planting every exposure
phrase (PHRASES, used by notes/score.py) must occur exactly once. Zero2Repo has no licence file: the
output stays in git-ignored `work/`; this script holds only the short anchors and planted sentences.
"""
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PUBLIC = HERE.parents[2] / "benchmarks/zero2repo/download/Zero2Repo/benchmark/cases/case010/public"
PRD, IC = "Full_PRD.md", "Interface_Contract.md"

# item: (file, anchor, replacement)
EDITS = {
    "C01": (IC, "  - `transpositions` is a `bool`.",
            "  - `transpositions` is a `bool`. With `transpositions=True`, only two characters that stand next "
            "to each other in both strings may be transposed, and nothing may be inserted or deleted between them."),
    "C02": (IC, "  - When the PRD says no number results, the call returns `None`.",
            "  - `f_measure` also takes `alpha=…`, the weight of precision, which defaults to 0.25.\n"
            "  - When the PRD says no number results, the call returns `None`."),
    "C03": (PRD, "and f-measure when either set is empty return no number.",
            "and f-measure when either set is empty or when the two sets share no element return no number."),
    "C04": (PRD, "  - Precision is |reference ∩ test| / |test|. Recall is |reference ∩ test| / |reference|.",
            "  - Precision is |reference ∩ test| / |test|. Recall is |reference ∩ test| / |reference|. A list or "
            "tuple given as either argument is read as the set of its elements."),
    "C05": (IC, "  - `weights` is a sequence of numbers, one per n-gram order starting from unigrams.",
            "  - `weights` is a sequence of numbers, one per n-gram order starting from unigrams. When `weights` "
            "is omitted, unigrams and bigrams are weighted equally and longer n-grams are not scored."),
    "C08": (PRD, "a child is a token string (a leaf) or a tree.",
            "a child is a token string (a leaf) or a tree. A string given in place of the child list is taken "
            "as a single leaf."),
    "C09": (IC, "`gaps`, `discard_empty`, `preserve_line`, `preserve_case`, `reduce_len` and `strip_handles` are `bool`.",
            "`gaps`, `discard_empty`, `preserve_line`, `preserve_case`, `reduce_len` and `strip_handles` are "
            "`bool`. `discard_empty` is off unless the caller passes `discard_empty=True`."),
    "C10": (IC, "each a regular-expression string and a tag string.",
            "each a regular-expression string and a tag string. When several patterns match a token, the last "
            "matching pair gives the tag."),
    "C11": (PRD, "Tokens no rule chunks stay direct children of the root.",
            "Tokens no rule chunks stay direct children of the root. Chunks that touch, with no token between "
            "them, are joined into one chunk."),
    "C13": (IC, "  - Each sentence is a `list` of `str` tokens.",
            "  - Each sentence is a `list` of `str` tokens. A terminal that is the empty string adds no token to "
            "a sentence."),
    "C14": (PRD, "none for a token list the grammar does not derive, and several for an ambiguous one.",
            "none for a token list the grammar does not derive (including one holding a token that no "
            "production produces), and several for an ambiguous one."),
    "C15": (PRD, "it is the fraction of positions at which they hold equal values.",
            "it is the fraction of positions at which they hold equal values. For lists of different lengths, "
            "it is that fraction over the positions both lists have."),
    "C16": (IC, "- `word` is a `str` and is treated as one token.",
            "- `word` is a `str` and is treated as one token. `PorterStemmer` applies Step 1a as published, so "
            "*ties* stems to *ti*."),
    "C17": (IC, "`to_lowercase` and `ignore_stopwords` are `bool`.",
            "`to_lowercase` and `ignore_stopwords` are `bool`; `to_lowercase` defaults to `False`, so `stem` "
            "keeps the letter case it is given."),
    "C18": (PRD, "Accented letters in a tweet-style tokenizer remain intact inside their tokens.",
            "Accented letters in a tweet-style tokenizer remain intact inside their tokens, and that tokenizer "
            "lowercases its tokens unless the caller asks to preserve case."),
    "C21": (PRD, "  - A double hyphen is a token.\n",
            "  - A double hyphen is a token.\n  - *cannot* is kept as one token.\n"),
    "C22": (PRD, "  - Typographic quotation marks are split off as tokens of their own.",
            "  - Typographic quotation marks are split off as tokens of their own. A straight double quote at "
            "the very start of the text becomes the closing-quote token."),
    "C26": (IC, "or a segment string for `blankline_tokenize`.",
            "or a segment string for `blankline_tokenize`, in which each single newline is replaced by one space."),
}

# item: (side-A phrase, side-B phrase); each must occur exactly once in the planted spec
PHRASES = {
    "C01": ("the distance is the unrestricted Damerau–Levenshtein distance", "nothing may be inserted or deleted between them"),
    "C02": ("with α = 0.5 by default", "which defaults to 0.25"),
    "C03": ("It is 0 when precision or recall is 0", "or when the two sets share no element"),
    "C04": ("Lists, tuples and other non-set collections are refused", "is read as the set of its elements"),
    "C05": ("The default is equal weights on unigrams through 4-grams", "longer n-grams are not scored"),
    "C08": ("as the child list (instead of a list of children) is refused", "is taken as a single leaf"),
    "C09": ("unless the caller turns empty-discarding off (it is on by default)", "`discard_empty` is off unless the caller passes"),
    "C10": ("the tag of the first rule whose pattern matches", "the last matching pair gives the tag"),
    "C11": ("Two matches that touch are two separate chunks", "are joined into one chunk"),
    "C13": ("A quoted empty string contributes an empty-string token", "adds no token to a sentence"),
    "C14": ("contains a token no production of the grammar produces does **not** succeed",
            "including one holding a token that no production produces"),
    "C15": ("Accuracy on two lists of different lengths does not succeed", "over the positions both lists have"),
    "C16": ("a four-letter word ending in *-ies* becomes *-ie* rather than *-i*", "*ties* stems to *ti*"),
    "C17": ("The word is lowercased first, unless the caller turns lowercasing off", "`to_lowercase` defaults to `False`"),
    "C18": ("With case preservation off (it is on by default)", "lowercases its tokens unless the caller asks to preserve case"),
    "C21": ("are split into their two parts (*can* + *not*", "*cannot* is kept as one token"),
    "C22": ("becomes the opening-quote token made of two backticks", "at the very start of the text becomes the closing-quote token"),
    "C26": ("Single newlines inside a segment are kept", "each single newline is replaced by one space"),
}

# The 15 items kept after step 1 (ANSWER_KEY.md), for the scripts that score them.
KEPT = "C01 C03 C04 C05 C08 C09 C11 C13 C14 C15 C16 C17 C18 C21 C22".split()
# item: (A substring, B substring) where the atomizer cut a phrase (filled after the compile, if needed)
FIND: dict[str, tuple[str | None, str | None]] = {
    # the atomizer dropped the sentence's leading ` or * (work/compile-full nodes N-000407, N-000426, N-000110)
    # C01's planted sentence was cut in two at ", and" (N-000505 + N-000506); both halves are side B
    "C01": (None, "only two characters that stand next to each other in both strings may be transposed"),
    "C09": (None, "discard_empty` is off unless the caller passes"),
    "C17": (None, "to_lowercase` defaults to `False`"),
    "C21": (None, "cannot* is kept as one token"),
}


if __name__ == "__main__":
    out, items = Path(sys.argv[1]), sys.argv[2:]
    assert items and all(i in EDITS for i in items), items
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    for f in PUBLIC.glob("*.md"):
        shutil.copy(f, out / f.name)
    for item in items:
        name, old, new = EDITS[item]
        text = (out / name).read_text(encoding="utf-8")
        assert text.count(old) == 1, (item, text.count(old))
        (out / name).write_text(text.replace(old, new), encoding="utf-8")
        print(item, name, "planted")
    spec = "\n".join(f.read_text(encoding="utf-8") for f in sorted(out.glob("*.md")))
    for item in items:
        for side, phrase in zip("AB", PHRASES[item]):
            assert spec.count(phrase) == 1, (item, side, phrase, spec.count(phrase))
    print("phrases ok;", "words", sum(len(f.read_text(encoding="utf-8").split()) for f in out.glob("*.md")))
