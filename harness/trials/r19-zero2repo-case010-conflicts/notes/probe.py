"""Side probes for round 19's candidate conflicts: which side of each item a built lingora takes. No model call.

    bash notes/probe.sh <app-dir>          (runs this file in a container with no network)

Method of ../r17-zero2repo-case006-conflicts-24/notes/probe.py. Written from the answer key
(`../ANSWER_KEY.md`) and the Interface Contract's API only, never from the hidden tests. Each probe
runs a tiny program against `<app>` (flat layout: the `lingora` package at its root) in a fresh
interpreter and reads only the returned value or the exception. It prints one JSON object:
{item: {"side": "A" | "B" | "neither" | "error", "evidence": ...}}. A side is never read as
detection; detection is scored from NOTES.md (`TRIAL.md`, "Detection rule").
"""
import json
import os
import subprocess
import sys
import tempfile
import textwrap

APP = sys.argv[1] if len(sys.argv) > 1 else "/app"
HEAD = f"import sys\nsys.path.insert(0, {APP!r})\n"

# item -> (program printing repr(value) or "RAISES", value meaning A, value meaning B)
PROBES = {
    "C01": ("from lingora.metrics import edit_distance\nprint(edit_distance('abc', 'ca', transpositions=True))",
            lambda o: o == "2", lambda o: o == "3"),
    "C02": ("from lingora.metrics import f_measure\nprint(round(f_measure({1, 2, 3}, {1}), 4))",
            lambda o: o == "0.5", lambda o: o == "0.4"),
    "C03": ("from lingora.metrics import f_measure\nprint(repr(f_measure({1}, {2})))",
            lambda o: o in ("0", "0.0"), lambda o: o == "None"),
    "C04": ("from lingora.metrics import precision\ntry:\n    print(precision([1, 2], [1]))\nexcept Exception:\n    print('RAISES')",
            lambda o: o == "RAISES", lambda o: o == "1.0"),
    "C05": ("from lingora.translate import bleu\nprint(round(bleu([['a', 'b']], ['a', 'b']), 4))",
            lambda o: o in ("0", "0.0"), lambda o: o == "1.0"),
    "C08": ("from lingora.tree import Tree\ntry:\n    t = Tree('S', 'abc')\n    print(t.leaves())\nexcept Exception:\n    print('RAISES')",
            lambda o: o == "RAISES", lambda o: o == "['abc']"),
    "C09": ("from lingora.tokenize import RegexpTokenizer\nprint(RegexpTokenizer(r'\\s+', gaps=True).tokenize(' a b '))",
            lambda o: o == "['a', 'b']", lambda o: o == "['', 'a', 'b', '']"),
    "C10": ("from lingora.tag import RegexpTagger\nprint(RegexpTagger([(r'\\d+', 'CD'), (r'.*', 'NN')]).tag(['3'])[0][1])",
            lambda o: o == "CD", lambda o: o == "NN"),
    "C11": ("from lingora.chunk import RegexpParser\nfrom lingora.tree import Tree\n"
            "t = RegexpParser('NP: {<DT><NN>}').parse([('the', 'DT'), ('dog', 'NN'), ('a', 'DT'), ('cat', 'NN')])\n"
            "print(sum(1 for c in t if isinstance(c, Tree)))",
            lambda o: o == "2", lambda o: o == "1"),
    "C13": ("from lingora.grammar import CFG\nfrom lingora.parse.generate import generate\n"
            "print(list(generate(CFG.fromstring(\"S -> 'a' ''\"))))",
            lambda o: o == "[['a', '']]", lambda o: o == "[['a']]"),
    "C14": ("from lingora.grammar import CFG\nfrom lingora.parse import ChartParser\n"
            "try:\n    print(list(ChartParser(CFG.fromstring(\"S -> 'a'\")).parse(['b'])))\nexcept Exception:\n    print('RAISES')",
            lambda o: o == "RAISES", lambda o: o == "[]"),
    "C15": ("from lingora.metrics import accuracy\ntry:\n    print(accuracy([1, 2, 3], [1, 2]))\nexcept Exception:\n    print('RAISES')",
            lambda o: o == "RAISES", lambda o: o == "1.0"),
    "C16": ("from lingora.stem import PorterStemmer\nprint(PorterStemmer().stem('ties'))",
            lambda o: o == "tie", lambda o: o == "ti"),
    "C17": ("from lingora.stem import PorterStemmer\nprint(PorterStemmer().stem('Running'))",
            lambda o: o == o.lower() and o != "", lambda o: o != o.lower()),
    "C18": ("from lingora.tokenize import TweetTokenizer\nprint(TweetTokenizer().tokenize('Hello World'))",
            lambda o: o == "['Hello', 'World']", lambda o: o == "['hello', 'world']"),
    "C21": ("from lingora.tokenize import word_tokenize\nprint(word_tokenize('I cannot go', preserve_line=True))",
            lambda o: o == "['I', 'can', 'not', 'go']", lambda o: o == "['I', 'cannot', 'go']"),
    "C22": ("from lingora.tokenize import word_tokenize\nprint(word_tokenize('\"Hi\" he said', preserve_line=True)[0])",
            lambda o: o == "``", lambda o: o == "''"),
    "C26": ("from lingora.tokenize import blankline_tokenize\nprint(blankline_tokenize('a\\nb\\n\\nc'))",
            lambda o: o == "['a\\nb', 'c']", lambda o: o == "['a b', 'c']"),
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


out = {}
for item, (body, is_a, is_b) in PROBES.items():
    rc, o, e = run(body)
    if rc != 0:
        out[item] = {"side": "error", "evidence": (o + " " + e)[-300:]}
    else:
        side = "A" if is_a(o) else "B" if is_b(o) else "neither"
        out[item] = {"side": side, "evidence": o[-200:]}
print(json.dumps(out))
