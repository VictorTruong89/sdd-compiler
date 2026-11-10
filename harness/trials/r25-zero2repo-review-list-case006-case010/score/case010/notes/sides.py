"""Make one side-B copy of a built lingora per candidate item, for the footprint runs and the probe check.

    python3 notes/sides.py work/base-app work/sides            (from the trial folder)

Round 19 (method of ../r17-zero2repo-case006-conflicts-24/notes/sides.py, adapted to case010).
The base is round 13c's `sonnet-case010-markdown-2` build, 196 / 197 on the task with the model files
(TRIAL.md, step 0b), the best of the four Sonnet case010 builds; it takes side A on every item. Each
patch is the smallest change that moves that one behaviour to side B. Every anchor must occur exactly
once, so a patch never applies silently to the wrong place. Writes work/sides/<item>/ (a full copy)
and work/sides/<item>.tgz. No candidate touches a packaged model (punkt, tagger, chunker, stopwords,
wordlist, WordNet) or the command line, so none is near the 20 tests that needed the model files.
"""
import shutil
import sys
import tarfile
from pathlib import Path

MET, BLEU, TREE, RTOK, TAG = ("lingora/metrics.py", "lingora/translate/bleu_score.py", "lingora/tree.py",
                              "lingora/tokenize/regexp.py", "lingora/tag/sequential.py")
CHUNK, GEN, CHART, PORTER, TB, TWEET = ("lingora/chunk/regexp.py", "lingora/parse/generate.py",
                                        "lingora/parse/chart.py", "lingora/stem/porter.py",
                                        "lingora/tokenize/treebank.py", "lingora/tokenize/tweet.py")
PATCHES = {
    # C01 edit distance with transpositions: unrestricted Damerau-Levenshtein (A) -> adjacent only, OSA (B)
    "C01": [(MET, "                d[i1][j1] + (i - i1 - 1) + 1 + (j - j1 - 1),",
             "                (d[i1][j1] + 1) if (i1 == i - 1 and j1 == j - 1) else INF,")],
    # C02 f-measure alpha default: 0.5 (A) -> 0.25 (B)
    "C02": [(MET, "def f_measure(reference, test, alpha=0.5):", "def f_measure(reference, test, alpha=0.25):")],
    # C03 f-measure when precision or recall is 0: 0 (A) -> no number (B)
    "C03": [(MET, "    if p == 0 or r == 0:\n        return 0.0", "    if p == 0 or r == 0:\n        return None")],
    # C04 precision and recall on a list: refused (A) -> read as the set of its elements (B)
    "C04": [(MET, "def precision(reference, test):\n    _check_sets(reference, test)",
             "def precision(reference, test):\n    reference, test = set(reference), set(test)"),
            (MET, "def recall(reference, test):\n    _check_sets(reference, test)",
             "def recall(reference, test):\n    reference, test = set(reference), set(test)")],
    # C05 BLEU default weights: equal on 1- to 4-grams (A) -> equal on 1- and 2-grams (B)
    "C05": [(BLEU, "def bleu(references, hypothesis, weights=(0.25, 0.25, 0.25, 0.25),",
             "def bleu(references, hypothesis, weights=(0.5, 0.5),")],
    # C08 tree with a string as its child list: refused (A) -> the string is one leaf (B)
    "C08": [(TREE, "        if children is None or isinstance(children, str):",
             "        if isinstance(children, str):\n            children = [children]\n        if children is None:")],
    # C09 regexp tokenizer empty-discarding: on by default (A) -> off by default (B); built-in tokenizers unchanged
    "C09": [(RTOK, "def __init__(self, pattern, gaps=False, discard_empty=True, flags=_FLAGS):",
             "def __init__(self, pattern, gaps=False, discard_empty=False, flags=_FLAGS):"),
            (RTOK, 'RegexpTokenizer.__init__(self, r"\\s+", gaps=True)',
             'RegexpTokenizer.__init__(self, r"\\s+", gaps=True, discard_empty=True)'),
            (RTOK, 'RegexpTokenizer.__init__(self, r"\\s*\\n\\s*\\n\\s*", gaps=True)',
             'RegexpTokenizer.__init__(self, r"\\s*\\n\\s*\\n\\s*", gaps=True, discard_empty=True)'),
            (RTOK, 'RegexpTokenizer.__init__(self, r"\\w+|[^\\w\\s]+")',
             'RegexpTokenizer.__init__(self, r"\\w+|[^\\w\\s]+", discard_empty=True)')],
    # C10 regexp tagger: first matching rule wins (A) -> last matching rule wins (B)
    "C10": [(TAG, "        for rx, tag in self._regexps:\n            if rx.match(tokens[index]):",
             "        for rx, tag in reversed(self._regexps):\n            if rx.match(tokens[index]):")],
    # C11 chunk rule, two matches that touch: two chunks (A) -> one chunk (B)
    "C11": [(CHUNK, "        for rule in self._rules:\n            s = rule.apply(s)\n",
             "        for rule in self._rules:\n            s = rule.apply(s)\n        s = s.replace(\"}{\", \"\")\n")],
    # C13 generator, quoted empty string: an empty-string token (A) -> no token (B)
    "C13": [(GEN, "        else:\n            yield [lhs]", "        else:\n            yield [] if lhs == \"\" else [lhs]")],
    # C14 chart parser, a token no production produces: refused (A) -> no parse tree (B)
    "C14": [(CHART, "        check_tokens(self._grammar, tokens)\n",
             "        try:\n            check_tokens(self._grammar, tokens)\n        except ValueError:\n            return iter([])\n")],
    # C15 metrics accuracy on lists of different lengths: refused (A) -> over the positions both have (B)
    "C15": [(MET, "    if len(reference) != len(test):\n        raise ValueError(\"Lists must have the same length.\")",
             "    if len(reference) != len(test):\n        n = min(len(reference), len(test))\n"
             "        reference, test = list(reference)[:n], list(test)[:n]")],
    # C16 Porter step 1a, four-letter word in -ies: -ie (A) -> -i (B)
    "C16": [(PORTER, "            if word.endswith(\"ies\") and len(word) == 4:", "            if False:")],
    # C17 Porter lowercasing: on by default (A) -> off by default (B)
    "C17": [(PORTER, "    def stem(self, word, to_lowercase=True):", "    def stem(self, word, to_lowercase=False):")],
    # C18 tweet tokenizer case preservation: on by default (A) -> off by default (B)
    "C18": [(TWEET, "def __init__(self, preserve_case=True,", "def __init__(self, preserve_case=False,")],
    # C21 recommended and Treebank tokenizers, "cannot": can + not (A) -> one token (B)
    "C21": [(TB, "        r\"(?i)\\b(can)(?#X)(not)\\b\", ", "        ")],
    # C22 recommended tokenizer, straight double quote at the start of the text: `` (A) -> '' (B)
    "C22": [(TB, "        (re.compile(\"([«“‘„]|[`]+)\"), r\" \\1 \"),\n        (re.compile(r\"^\\\"\"), r\"``\"),\n",
             "        (re.compile(\"([«“‘„]|[`]+)\"), r\" \\1 \"),\n")],
    # C26 blank-line tokenizer, a single newline inside a segment: kept (A) -> one space (B)
    "C26": [(RTOK, "def blankline_tokenize(text):\n    return BlanklineTokenizer().tokenize(text)",
             "def blankline_tokenize(text):\n    return [t.replace(\"\\n\", \" \") for t in BlanklineTokenizer().tokenize(text)]")],
}


def make(base, out, item):
    d = out / item
    if d.exists():
        shutil.rmtree(d)
    shutil.copytree(base, d)
    for rel, old, new in PATCHES[item]:
        p = d / rel
        s = p.read_text(encoding="utf-8")
        n = s.count(old)
        assert n == 1, f"{item}: anchor found {n} times in {rel}: {old!r}"
        p.write_text(s.replace(old, new), encoding="utf-8")
    with tarfile.open(out / f"{item}.tgz", "w:gz") as t:
        for f in sorted(d.rglob("*")):
            if "__pycache__" not in f.parts:
                t.add(f, arcname="./" + str(f.relative_to(d)), recursive=False)


if __name__ == "__main__":
    base, out = Path(sys.argv[1]), Path(sys.argv[2])
    out.mkdir(parents=True, exist_ok=True)
    items = sys.argv[3:] or list(PATCHES)
    for it in items:
        make(base, out, it)
    with tarfile.open(out / "BASE.tgz", "w:gz") as t:
        for f in sorted(base.rglob("*")):
            if "__pycache__" not in f.parts:
                t.add(f, arcname="./" + str(f.relative_to(base)), recursive=False)
    print("made", len(items), "side-B copies and BASE.tgz in", out)
