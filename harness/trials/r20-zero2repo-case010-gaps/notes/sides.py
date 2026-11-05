"""Make one alternative copy of a built lingora per gap candidate, for the footprint runs and the probe check.

    python3 notes/sides.py work/base-app work/sides            (from the trial folder)

Round 20: round 19's script (../r19-zero2repo-case010-conflicts/notes/sides.py) with its method kept and
its patches replaced. Each candidate is a stated fact that may be removed from the spec (a gap,
`../TRIAL.md` step 1); the base build takes the **upstream** value on every candidate, and each patch
is the smallest change that moves that one behaviour to a plausible **alternative**. Every anchor must
occur exactly once, so a patch never applies silently to the wrong place. Writes work/sides/<id>/ (a
full copy) and work/sides/<id>.tgz, plus work/sides/BASE.tgz. No candidate touches punkt, a tagger,
the named-entity chunker, stopwords, a wordlist, WordNet or the command line, and none is one of
round 19's 18 items (C01–C26).
"""
import shutil
import sys
import tarfile
from pathlib import Path

MET, BLEU, TREE, CHUNK, GRAM = ("lingora/metrics.py", "lingora/translate/bleu_score.py", "lingora/tree.py",
                                "lingora/chunk/regexp.py", "lingora/grammar.py")
PORTER, LANC, SNOW, RSTEM = ("lingora/stem/porter.py", "lingora/stem/lancaster.py", "lingora/stem/snowball.py",
                             "lingora/stem/regexp.py")
RTOK, TB, NB = "lingora/tokenize/regexp.py", "lingora/tokenize/treebank.py", "lingora/classify/naivebayes.py"

# Whole-string stemming -> each whitespace-separated word stemmed (G07): appended wrappers.
_SPLIT_PORTER = '''

_one_token_stem = PorterStemmer.stem


def _stem_each_word(self, word, to_lowercase=True):
    if len(word.split()) > 1:
        return " ".join(_one_token_stem(self, w, to_lowercase) for w in word.split())
    return _one_token_stem(self, word, to_lowercase)


PorterStemmer.stem = _stem_each_word
'''
_SPLIT_LANC = '''

_one_token_lstem = LancasterStemmer.stem


def _lstem_each_word(self, word):
    if len(word.split()) > 1:
        return " ".join(_one_token_lstem(self, w) for w in word.split())
    return _one_token_lstem(self, word)


LancasterStemmer.stem = _lstem_each_word
'''

PATCHES = {
    # G01 edit distance, default substitution cost: 1 (upstream) -> 2 (alternative)
    "G01": [(MET, "def edit_distance(s1, s2, substitution_cost=1, transpositions=False):",
             "def edit_distance(s1, s2, substitution_cost=2, transpositions=False):")],
    # G02 Jaccard distance: |symmetric difference| / |union| (upstream) -> |intersection| / |union| (similarity)
    "G02": [(MET, "    return (union - len(label1 & label2)) / union", "    return len(label1 & label2) / union")],
    # G03 recall with an empty reference set: no number (upstream) -> 0 (alternative)
    "G03": [(MET, "    if len(reference) == 0:\n        return None\n    return len(reference & test) / len(reference)",
             "    if len(reference) == 0:\n        return 0.0\n    return len(reference & test) / len(reference)")],
    # G04 BLEU brevity penalty: applied (upstream) -> none (alternative)
    "G04": [(BLEU, "    bp = _brevity_penalty(_closest_ref_len(references, hyp_len), hyp_len)", "    bp = 1.0")],
    # G05 BLEU closest reference length, tie: the shorter (upstream) -> the longer (alternative)
    "G05": [(BLEU, "    return min(lens, key=lambda l: (abs(l - hyp_len), l))",
             "    return min(lens, key=lambda l: (abs(l - hyp_len), -l))")],
    # G06 BLEU modified precision: counts clipped by the max reference count (upstream) -> not clipped
    "G06": [(BLEU, "        num = sum(min(c, mx[g]) for g, c in hc.items())",
             "        num = sum(c for g, c in hc.items() if mx[g])")],
    # G07 stemmers, a string with spaces: one token (upstream) -> each word stemmed, joined by a space
    "G07": [],   # appended wrappers only (APPEND below)
    # G08 Snowball, unsupported language: message names it (upstream) -> generic message
    "G08": [(SNOW, "raise ValueError(\"The language '%s' is not supported.\" % (language,))",
             "raise ValueError(\"The requested language is not supported.\")")],
    # G09 Snowball "porter": the original Porter algorithm (upstream) -> an alias of "english" (alternative)
    "G09": [(SNOW, '        if language == "porter":', '        if language == "porter-original":'),
            (SNOW, "            self._fn = _LANGS[language]", "            self._fn = _LANGS.get(language, snowball_en.stem)")],
    # G10 Porter, a stem reduced to one letter: returned (upstream) -> the word is returned unstemmed
    "G10": [(PORTER, "        stem = self._step5b(stem)\n        return stem",
             "        stem = self._step5b(stem)\n        if len(stem) == 1 and len(word) > 2:\n"
             "            return word.lower() if to_lowercase else word\n        return stem")],
    # G11 Lancaster prefixes: never stripped (upstream) -> stripped by default (alternative)
    "G11": [(LANC, "def __init__(self, rule_tuple=None, strip_prefix_flag=False):",
             "def __init__(self, rule_tuple=None, strip_prefix_flag=True):")],
    # G12 regexp stemmer: every match removed (upstream) -> the first match only
    "G12": [(RSTEM, '        return self._regexp.sub("", word)', '        return self._regexp.sub("", word, count=1)')],
    # G13 spans: (start, end) with end exclusive, slicing gives the token (upstream) -> end inclusive
    "G13": [(RTOK, "            yield (s, e)", "            yield (s, e - 1)")],
    # G14 Treebank comma or colon: kept when a digit follows (upstream) -> always split off
    "G14": [(TB, '        (re.compile(r"([:,])([^\\d])"), r" \\1 \\2"),\n        (re.compile(r"([:,])$"), r" \\1 "),\n'
                 '        (re.compile(r"\\.\\.\\."), r" ... "),',
             '        (re.compile(r"([:,])"), r" \\1 "),\n        (re.compile(r"([:,])$"), r" \\1 "),\n'
             '        (re.compile(r"\\.\\.\\."), r" ... "),'),
            (TB, '        (re.compile(r"([:,])([^\\d])"), r" \\1 \\2"),\n        (re.compile(r"([:,])$"), r" \\1 "),\n'
                 '        (re.compile(r"\\.{2,}"), r" \\g<0> "),',
             '        (re.compile(r"([:,])"), r" \\1 "),\n        (re.compile(r"([:,])$"), r" \\1 "),\n'
             '        (re.compile(r"\\.{2,}"), r" \\g<0> "),')],
    # G15 Treebank point: split off only at the end of the text (upstream) -> every single point split off
    "G15": [(TB, '        (re.compile(r"[?!]"), r" \\g<0> "),\n        (re.compile(r"([^\'])\' "), r"\\1 \' "),\n    ]',
             '        (re.compile(r"[?!]"), r" \\g<0> "),\n        (re.compile(r"([^\'])\' "), r"\\1 \' "),\n'
             '        (re.compile(r"(?<!\\.)\\.(?!\\.)"), r" . "),\n    ]'),
            (TB, '        (re.compile("[‒-―]"), r" \\g<0> "),\n    ]',
             '        (re.compile("[‒-―]"), r" \\g<0> "),\n        (re.compile(r"(?<!\\.)\\.(?!\\.)"), r" . "),\n    ]')],
    # G16 chunk tag pattern, whitespace: ignored (upstream) -> significant
    "G16": [(CHUNK, '    tag_pattern = re.sub(r"\\s", "", tag_pattern)\n', "")],
    # G17 chunking an empty tagged list: a root with no children (upstream) -> refused
    "G17": [(CHUNK, "        chunk_struct = list(chunk_struct) if not isinstance(chunk_struct, Tree) else chunk_struct\n",
             "        chunk_struct = list(chunk_struct) if not isinstance(chunk_struct, Tree) else chunk_struct\n"
             "        if len(chunk_struct) == 0:\n            raise ValueError(\"nothing to chunk\")\n")],
    # G18 a chunk grammar that is not text nor a list of stages: refused (upstream) -> taken as an empty grammar
    "G18": [(CHUNK, '            raise TypeError("the grammar must be a string or a list of chunk parsers")',
             "            self._stages = []")],
    # G19 tree length: immediate children (upstream) -> number of leaves
    "G19": [(TREE, "    __hash__ = None\n", "    __hash__ = None\n\n    def __len__(self):\n        return len(self.leaves())\n")],
    # G20 tree equality: labels and children (upstream) -> children only
    "G20": [(TREE, "        return isinstance(other, Tree) and self._label == other._label and list.__eq__(self, other)",
             "        return isinstance(other, Tree) and list.__eq__(self, other)")],
    # G21 grammar start symbol: left-hand side of the first production (upstream) -> S when S has a production
    "G21": [(GRAM, "            raise ValueError(\"No productions found\")\n        return cls(start, productions)",
             "            raise ValueError(\"No productions found\")\n"
             "        if any(str(p.lhs()) == \"S\" for p in productions):\n            start = Nonterminal(\"S\")\n"
             "        return cls(start, productions)")],
    # G22 Naive Bayes estimates: smoothed (upstream) -> raw relative frequencies (a value unseen with a label ~ 0)
    "G22": [(NB, "                logprob[label] += math.log((c + 0.5) / (n + 0.5 * bins))",
             "                logprob[label] += math.log(max(c / n, 1e-300))")],
    # G23 Naive Bayes, a feature name never seen in training: ignored (upstream) -> refused
    "G23": [(NB, "        featureset = {f: v for f, v in featureset.items()\n"
                 "                      if any((l, f) in self._feature_probdist for l in self._labels)}",
             "        featureset = dict(featureset)")],
    # G24 Naive Bayes, a featureset sharing no feature with training: a trained label (upstream) -> refused
    "G24": [(NB, "        logprob = {}\n",
             "        if not featureset:\n            raise ValueError(\"the featureset shares no feature with the training data\")\n"
             "        logprob = {}\n")],
}
# G07: the wrappers are appended to the end of each file (no anchor).
APPEND = {"G07": [(PORTER, _SPLIT_PORTER), (LANC, _SPLIT_LANC)]}


def make(base, out, item):
    d = out / item
    if d.exists():
        shutil.rmtree(d)
    shutil.copytree(base, d, ignore=shutil.ignore_patterns("__pycache__"))
    for rel, old, new in PATCHES[item]:
        p = d / rel
        s = p.read_text(encoding="utf-8")
        n = s.count(old)
        assert n == 1, f"{item}: anchor found {n} times in {rel}: {old!r}"
        p.write_text(s.replace(old, new), encoding="utf-8")
    for rel, tail in APPEND.get(item, []):
        p = d / rel
        p.write_text(p.read_text(encoding="utf-8") + tail, encoding="utf-8")
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
    print("made", len(items), "alternative copies and BASE.tgz in", out)
