"""Make the gapped case010 spec: copy Zero2Repo case010's `public/` and remove each kept fact. No model call.

    python3 notes/remove.py work/spec-gapped G01 G02 ...        (from the trial folder)

Round 20 (new; the counterpart of round 19's notes/plant.py). For each gap id, every place that states
the fact is edited once: the smallest span that removes the fact and keeps the sentence readable. No
marker and no "unspecified" wording is added. Every `old` string must occur exactly once in the file,
so an edit never applies silently to the wrong place. `KEY` is each gap's key phrase or value, used by
the checks (step 2: nothing left states it; step 3: no export node quotes it).
"""
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PUBLIC = HERE.parents[2] / "benchmarks/zero2repo/download/Zero2Repo/benchmark/cases/case010/public"
PRD, IC = "Full_PRD.md", "Interface_Contract.md"

# gap -> list of (file, old, new)
REMOVALS = {
    "G01": [(PRD, "costs the caller's substitution cost, which defaults to 1.", "costs the caller's substitution cost.")],
    "G02": [(PRD, "- **Jaccard distance.** It is the size of the symmetric difference of the two sets divided by the size of their union.\n", "")],
    "G03": [(PRD, "Precision with an empty test set, recall with an empty reference set, and f-measure when either set is empty",
             "Precision with an empty test set and f-measure when either set is empty")],
    "G04": [(PRD, "  - The result is multiplied by the brevity penalty, computed from the reference length closest to the candidate length (the shorter one when two are equally close).\n", "")],
    "G05": [(PRD, " (the shorter one when two are equally close)", "")],
    "G06": [(PRD, "  - Each n-gram order has a modified precision: candidate n-gram counts are clipped by the maximum count of that n-gram in any one reference.",
             "  - Each n-gram order has a precision.")],
    "G07": [(PRD, "Every stemmer treats its whole input string as one token. A string containing spaces is not split into words.\n\n", ""),
            (IC, "- `word` is a `str` and is treated as one token.", "- `word` is a `str`.")],
    "G08": [(PRD, " does not produce a usable stemmer. The failure names the requested language.", " does not produce a usable stemmer."),
            (IC, " makes the `SnowballStemmer` constructor raise, and the exception message contains the requested name.",
             " makes the `SnowballStemmer` constructor raise.")],
    "G09": [(PRD, " The language named *porter* is Snowball's rendering of the original Porter algorithm, so the two can give different stems.", "")],
    "G10": [(PRD, " Every word is stemmed without refusal, including a word whose stem reduces to a single letter.", "")],
    "G11": [(PRD, "The word is lowercased first, and no prefix is stripped.", "The word is lowercased first.")],
    "G12": [(PRD, "It removes every match of the caller's pattern from the word", "It removes the caller's pattern from the word")],
    "G13": [(PRD, " Slicing the original string at a span must recover the corresponding token.", ""),
            (PRD, " Slicing the input at each pair gives the corresponding token.", "")],
    "G14": [(PRD, "  - A comma or colon is split off unless a digit follows it.\n", "")],
    "G15": [(PRD, "  - A point is split off only when it ends the text, optionally followed by closing quotes or brackets.\n", "")],
    "G16": [(PRD, " Whitespace in a tag pattern is ignored.", ""), (PRD, " Whitespace in a pattern is ignored.", "")],
    "G17": [(PRD, "- An empty tagged-token list yields a chunk structure with a sentence root and no children.\n", "")],
    "G18": [(PRD, "- A chunk grammar that is not text and not a list of chunk-parser stages is refused. The operation does not succeed and does not return a chunk structure.\n", ""),
            (IC, " Any other value makes the constructor raise.", "")],
    "G19": [(PRD, " Its length is the number of immediate children, and its children can be read by position.", " Its children can be read by position."),
            (IC, "- Iterating a tree, `len(tree)` and `tree[i]` give", "- Iterating a tree and `tree[i]` give")],
    "G20": [(PRD, "  - Two trees are equal exactly when their labels are equal and their children are equal pairwise, recursively.\n", "")],
    "G21": [(PRD, "  - The start symbol is the left-hand side of the first production.\n", "")],
    "G22": [(PRD, " The estimates are smoothed so that no feature value seen with some label gets probability zero under another label.", "")],
    "G23": [(PRD, "  - Classifying uses only the features of the queried featureset that occurred in training. A feature name never seen in training is ignored.\n", "")],
    "G24": [(PRD, "- A featureset that shares no feature with the training data still receives one of the trained labels, from either classifier. It is never refused, and it never receives a label that did not occur in training.\n", "")],
}

# gap -> key phrases or values that must not remain anywhere in the gapped spec, nor in the export
KEY = {
    "G01": ["defaults to 1"], "G02": ["symmetric difference"], "G03": ["empty reference"],
    "G04": ["brevity penalty"], "G05": ["equally close"], "G06": ["clipped", "modified precision"],
    "G07": ["one token", "not split into words"], "G08": ["names the requested", "contains the requested"],
    "G09": ["rendering of the original"], "G10": ["single letter", "without refusal"],
    "G11": ["prefix"], "G12": ["every match of the caller"], "G13": ["Slicing"],
    "G14": ["comma or colon"], "G15": ["point is split off"], "G16": ["Whitespace in a"],
    "G17": ["empty tagged-token list"], "G18": ["not text and not a list", "Any other value"],
    "G19": ["Its length is", "len(tree)"], "G20": ["equal exactly when"], "G21": ["left-hand side of the first"],
    "G22": ["smoothed"], "G23": ["never seen in training is ignored", "occurred in training"],
    "G24": ["shares no feature"],
}


# Kept after step 1 (footprint 1-3, none shared, none among the 20 model-file tests; TRIAL.md step 1).
KEPT = ["G02", "G03", "G07", "G08", "G09", "G10", "G13", "G14", "G16", "G17", "G18", "G20", "G23", "G24"]


def make(out: Path, gaps):
    if out.exists():
        shutil.rmtree(out)
    shutil.copytree(PUBLIC, out)
    for g in gaps:
        for name, old, new in REMOVALS[g]:
            p = out / name
            s = p.read_text(encoding="utf-8")
            n = s.count(old)
            assert n == 1, f"{g}: text found {n} times in {name}: {old!r}"
            p.write_text(s.replace(old, new), encoding="utf-8")


if __name__ == "__main__":
    out, gaps = Path(sys.argv[1]), sys.argv[2:]
    assert gaps and all(g in REMOVALS for g in gaps), gaps
    make(out, gaps)
    print("removed", len(gaps), "facts into", out)
