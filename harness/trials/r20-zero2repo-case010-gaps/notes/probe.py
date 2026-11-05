"""Gap probes for round 20: which value a built lingora takes on each gap candidate. No model call.

    bash notes/probe.sh <app-dir>          (runs this file in a container with no network)

Round 20: round 19's probe (../r19-zero2repo-case010-conflicts/notes/probe.py) with its method kept
and its probes replaced, and the reading renamed from sides A/B to the round's four readings. Written
from the answer key (`../ANSWER_KEY.md`) and the Interface Contract's API only, never from the hidden
tests. Each probe runs a tiny program against `<app>` (flat layout: the `lingora` package at its
root) in a fresh interpreter and reads only the printed value. Where a refusal is one of the values,
the program catches it and prints RAISES. Prints one JSON object:
{item: {"built": "upstream" | "alternative" | "other" | "not built", "evidence": ...}}.
"not built" = the program itself failed (import missing, entry missing, an unexpected exception):
the probe reads neither value. The reading is never detection; flagging is read from NOTES.md.
"""
import json
import os
import subprocess
import sys
import tempfile
import textwrap

APP = sys.argv[1] if len(sys.argv) > 1 else "/app"
HEAD = f"import sys\nsys.path.insert(0, {APP!r})\n"


def num(o):
    try:
        return float(o)
    except ValueError:
        return None


def near(x):
    return lambda o: num(o) is not None and abs(num(o) - x) < 1e-3


NB = ("from lingora.classify import NaiveBayesClassifier\n"
      "c = NaiveBayesClassifier.train([({'nice': True}, 'pos'), ({'bad': True}, 'neg')])\n")

# item -> (program printing a value, test for upstream, test for the alternative)
PROBES = {
    "G01": ("from lingora.metrics import edit_distance\nprint(edit_distance('a', 'b'))", near(1), near(2)),
    "G02": ("from lingora.metrics import jaccard_distance\nprint(jaccard_distance({1}, {1}))", near(0), near(1)),
    "G03": ("from lingora.metrics import recall\nprint(repr(recall(set(), {1})))", lambda o: o == "None", near(0)),
    "G04": ("from lingora.translate import bleu\nprint(bleu([['a', 'b', 'c', 'd']], ['a', 'b'], weights=(1,)))",
            near(0.36788), near(1)),
    "G05": ("from lingora.translate import bleu\nprint(bleu([['a'], ['a', 'b', 'c']], ['a', 'b'], weights=(1,)))",
            near(1), near(0.60653)),
    "G06": ("from lingora.translate import bleu\nprint(bleu([['the', 'cat']], ['the', 'the'], weights=(1,)))",
            near(0.5), near(1)),
    "G07": ("from lingora.stem import PorterStemmer\nprint(PorterStemmer().stem('running dogs'))",
            lambda o: o == "running dog", lambda o: o == "run dog"),
    "G08": ("from lingora.stem import SnowballStemmer\ntry:\n    SnowballStemmer('klingon')\n    print('NORAISE')\n"
            "except Exception as e:\n    print('klingon' in str(e))",
            lambda o: o == "True", lambda o: o == "False"),
    "G09": ("from lingora.stem import SnowballStemmer\n"
            "p, e = SnowballStemmer('porter').stem('generously'), SnowballStemmer('english').stem('generously')\n"
            "print(p, e, p == e)",
            lambda o: o.endswith("False"), lambda o: o.endswith("True")),
    "G10": ("from lingora.stem import PorterStemmer\nprint(PorterStemmer().stem('oed'))",
            lambda o: o == "o", lambda o: o == "oed"),
    "G11": ("from lingora.stem import LancasterStemmer\ns = LancasterStemmer()\n"
            "print(s.stem('kilogram'), s.stem('gram'), s.stem('kilogram') == s.stem('gram'))",
            lambda o: o.endswith("False"), lambda o: o.endswith("True")),
    "G12": ("from lingora.stem import RegexpStemmer\nprint(RegexpStemmer('a').stem('banana'))",
            lambda o: o == "bnn", lambda o: o == "bnana"),
    "G13": ("from lingora.tokenize import WordPunctTokenizer\nprint(list(WordPunctTokenizer().span_tokenize('ab cd')))",
            lambda o: o == "[(0, 2), (3, 5)]", lambda o: o == "[(0, 1), (3, 4)]"),
    "G14": ("from lingora.tokenize import TreebankWordTokenizer\nprint(TreebankWordTokenizer().tokenize('pay 1,000 now'))",
            lambda o: o == "['pay', '1,000', 'now']", lambda o: o == "['pay', '1', ',', '000', 'now']"),
    "G15": ("from lingora.tokenize import TreebankWordTokenizer\nprint(TreebankWordTokenizer().tokenize('costs 3.50 now'))",
            lambda o: o == "['costs', '3.50', 'now']", lambda o: o == "['costs', '3', '.', '50', 'now']"),
    "G16": ("from lingora.chunk import RegexpParser\nfrom lingora.tree import Tree\n"
            "try:\n    t = RegexpParser('NP: {<DT> <NN>}').parse([('the', 'DT'), ('dog', 'NN')])\n"
            "    print(sum(1 for c in t if isinstance(c, Tree)))\nexcept Exception:\n    print('RAISES')",
            lambda o: o == "1", lambda o: o in ("0", "RAISES")),
    "G17": ("from lingora.chunk import RegexpParser\n"
            "try:\n    t = RegexpParser('NP: {<NN>}').parse([])\n    print(t.label() is not None, sum(1 for _ in t))\n"
            "except Exception:\n    print('RAISES')",
            lambda o: o == "True 0", lambda o: o == "RAISES"),
    "G18": ("from lingora.chunk import RegexpParser\ntry:\n    RegexpParser(42)\n    print('ACCEPTED')\n"
            "except Exception:\n    print('RAISES')",
            lambda o: o == "RAISES", lambda o: o == "ACCEPTED"),
    "G19": ("from lingora.tree import Tree\nprint(len(Tree('S', [Tree('NP', ['a', 'b'])])))",
            lambda o: o == "1", lambda o: o == "2"),
    "G20": ("from lingora.tree import Tree\nprint(Tree('S', ['a']) == Tree('X', ['a']))",
            lambda o: o == "False", lambda o: o == "True"),
    "G21": ("from lingora.grammar import CFG\nprint(str(CFG.fromstring(\"NP -> 'a'\\nS -> NP\").start()))",
            lambda o: o == "NP", lambda o: o == "S"),
    "G22": (NB + "print(c.prob_classify({'nice': True}).prob('neg'))",
            lambda o: num(o) is not None and 0.01 < num(o) < 0.5, lambda o: num(o) is not None and num(o) < 1e-6),
    "G23": (NB + "try:\n    print(c.classify({'nice': True, 'zzz': True}))\nexcept Exception:\n    print('RAISES')",
            lambda o: o == "pos", lambda o: o == "RAISES"),
    "G24": (NB + "try:\n    print(c.classify({}))\nexcept Exception:\n    print('RAISES')",
            lambda o: o in ("pos", "neg"), lambda o: o == "RAISES"),
}


def run(body):
    with tempfile.TemporaryDirectory() as d:
        prog = os.path.join(d, "prog.py")
        with open(prog, "w") as f:
            f.write(HEAD + textwrap.dedent(body) + "\n")
        try:
            p = subprocess.run([sys.executable, prog], capture_output=True, text=True, cwd=d, timeout=30)
            return p.returncode, p.stdout.strip(), p.stderr
        except subprocess.TimeoutExpired:
            return None, "", "timeout"


if __name__ == "__main__":
    items = sys.argv[2:] or list(PROBES)
    out = {}
    for item in items:
        body, is_up, is_alt = PROBES[item]
        rc, o, e = run(body)
        if rc != 0:
            out[item] = {"built": "not built", "evidence": (o + " " + e)[-300:]}
        else:
            built = "upstream" if is_up(o) else "alternative" if is_alt(o) else "other"
            out[item] = {"built": built, "evidence": o[-200:]}
    print(json.dumps(out))
