"""Make round 28's case011 spec: plant the kept conflicts and remove the kept gaps in a copy of case011's public spec.
No model call.

    python3 notes/plant.py work/spec-planted C02 ... G03 ...       (from the trial folder)

Round 28, case011 (copied from ../r28-zero2repo-case005-conflicts-gaps/notes/plant.py; method unchanged,
new anchors for case011):
  - **Conflict** C..: one edit adds side B in **one** place, in the spec's own voice and with no marker,
    so the other place still states side A. `PHRASES[item] = (A phrase, B phrase)`; after planting each
    must occur exactly once.
  - **Gap** G..: every place that states the fact is edited once, the smallest span that removes it and
    keeps the sentence readable; no marker and no "unspecified" wording is added. `KEY[item]` lists
    phrases that must occur nowhere after removal.
Every `old` string must occur exactly once in its file. A bullet left empty by removals is dropped.
Zero2Repo has no licence file: the output stays in git-ignored `work/`.
"""
import re
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PUBLIC = HERE.parents[2] / "benchmarks/zero2repo/download/Zero2Repo/benchmark/cases/case011/public"
PRD, IC = "Full_PRD.md", "Interface_Contract.md"

EDITS = {
    # ---------------- conflicts: side B added in one place
    "C02": [(PRD, "A function that has nothing to compute returns the result its definition states; that is not a failure.",
             "A function that has nothing to compute returns the result its definition states; that is not a failure. "
             "`join` of an empty array yields null.")],
    "C05": [(PRD, "A missing field, an out-of-range index, and a selector applied to the wrong kind of value all yield null; they do not fail.",
             "A missing field, an out-of-range index, and a selector applied to the wrong kind of value all yield null; they do not fail. "
             "An empty string or an empty array counts as null for `not_null`.")],
    "C08": [(PRD, "| **String** | A Unicode text value. |", "| **String** | A Unicode text value; its length is its number of UTF-8 bytes. |")],
    "C12": [(PRD, "It builds a new array with one element per expression, in order, storing nulls.",
             "It builds a new array with one element per expression, in order, storing nulls. "
             "On a null current value it still builds one element per expression.")],
    "C14": [(PRD, "- Out-of-range indices and slices do not fail: they yield null or a (possibly empty) array as specified above.",
             "- Out-of-range indices and slices do not fail: they yield null or a (possibly empty) array as specified above. "
             "A slice of a value that is not an array is the empty array.")],
    "C15": [(PRD, "- The same operators apply inside a filter predicate (FP-04).",
             "- The same operators apply inside a filter predicate (FP-04). A filter applied to anything but an array yields the empty array.")],
    "C17": [(PRD, "Null results are dropped, not stored. Which following steps",
             "Null results are dropped, not stored. An object wildcard applied to a non-object is the empty array. Which following steps")],
    "C19": [(PRD, "- A literal is not an identifier: a literal directly after a dot is a grammar-level syntax failure.",
             "- A literal is not an identifier: a literal directly after a dot is a grammar-level syntax failure. "
             "A `\\uXXXX` escape inside a raw string literal is decoded to its character.")],
    "C20": [(PRD, "  - The step defaults to 1. A step may be negative.",
             "  - The step defaults to 1. A step may be negative. A step of 0 selects nothing: the result is the empty array.")],
    "C22": [(PRD, "Specified in FP-05 and used in FP-07. |", "Specified in FP-05 and used in FP-07. Outside a function argument it evaluates to null. |")],
    "C24": [(PRD, "| **Grammar-level syntax failure** | A syntax failure on text that splits into valid tokens which do not form a well-formed expression. |",
             "| **Grammar-level syntax failure** | A syntax failure on text that splits into valid tokens which do not form a well-formed expression. "
             "A single `=` is a grammar-level failure of this kind. |")],
    "C26": [(PRD, "| **Number** | An integer or a floating-point value.",
             "| **Number** | An integer or a floating-point value. A number made from a string by `to_number` is always a floating-point value.")],
    # ---------------- gaps: every statement removed
    "G03": [(PRD, "strings by code point); the empty array yields the empty array.", "strings by code point).")],
    "G22": [(PRD, "- An ordering comparison in which either side is an array, an object, a boolean, or null yields null — not false and not a failure.\n", ""),
            (PRD, "- Ordering involving a boolean, an array, an object or null is null, not a failure.\n", "")],
    "G25": [(PRD, "A backslash and the character after it are read together: the pair backslash-quote stands for a single quote, "
                  "and every other pair is kept exactly as written (both characters).",
             "The pair backslash-quote stands for a single quote.")],
    "G27": [(PRD, " A host value that is not a JSON type is converted with the host's ordinary text conversion, and that text is returned as a JSON string encoding (in double quotes).", "")],
    "G28": [(PRD, "Host decimal numbers are numbers for comparison (FP-06), not for built-in functions: a function argument that requires a number refuses a host decimal as the invalid-type kind, on either entry.",
             "Host decimal numbers are numbers for comparison (FP-06)."),
            (PRD, "This includes a host decimal or boolean where a number is required,", "This includes a boolean where a number is required,")],
    "G29": [(PRD, "one or more objects; a new host ordinary mapping with each argument's entries", "one or more objects; a new mapping with each argument's entries"),
            (PRD, " Built-in functions that return a new object, including `merge`, still return the host’s ordinary mapping.", "")],
    "G34": [(PRD, "Every **multiselect hash** the evaluation constructs — at any nesting depth — is built", "A **multiselect hash** the evaluation constructs is built")],
    "G35": [(PRD, "It builds a new object with one entry per pair, in declaration order;", "It builds a new object with one entry per pair;"),
            (PRD, "is built as an instance of exactly that type, with its keys inserted in declaration order.", "is built as an instance of exactly that type.")],
    "G54": [(PRD, "A backtick inside the literal is written as a backslash then a backtick. The text, with those escapes replaced, is read as JSON",
             "The text is read as JSON")],
    "G60": [(PRD, "`sum(array of numbers)` — the sum; the empty array yields 0.", "`sum(array of numbers)` — the sum.")],
    "G61": [(PRD, "keep their input order. The empty array yields the empty array.", "keep their input order.")],
    "G69": [(PRD, "- Options apply to the search they are attached to and to nothing else: a later search without options, with options lacking a provider or mapping type, or with a different provider, sees only what its own options supply. One options object",
             "- One options object")],
}

PHRASES = {
    "C02": ("the empty array yields the empty string", "`join` of an empty array yields null"),
    "C05": ("an empty array or empty string is not null", "counts as null for `not_null`"),
    "C08": ("the number of Unicode characters (not bytes) of a string", "its length is its number of UTF-8 bytes"),
    "C12": ("A multiselect list or hash whose current value is null yields null", "On a null current value it still builds one element per expression"),
    "C14": ("A slice on a value that is not an array yields null", "A slice of a value that is not an array is the empty array"),
    "C15": ("A filter on a non-array yields null", "A filter applied to anything but an array yields the empty array"),
    "C17": ("An object wildcard on a value that is not an object yields null", "An object wildcard applied to a non-object is the empty array"),
    "C19": ("No JSON escapes are processed", "escape inside a raw string literal is decoded to its character"),
    "C20": ("A slice whose step is 0 does not succeed on either entry", "A step of 0 selects nothing: the result is the empty array"),
    "C22": ("Searching an expression reference on its own succeeds and yields a non-null value", "Outside a function argument it evaluates to null"),
    "C24": ("A lone `=` is a token-level syntax failure", "A single `=` is a grammar-level failure of this kind"),
    "C26": ("a string that is an integer numeral becomes that integer", "is always a floating-point value"),
}

KEY = {
    "G03": ["by code point); the empty array yields the empty array"],
    "G22": ["yields null — not false", "Ordering involving a boolean"],
    "G25": ["every other pair is kept exactly as written"],
    "G27": ["returned as a JSON string encoding"],
    "G28": ["not for built-in functions", "a host decimal or boolean where"],
    "G29": ["including `merge`, still return", "a new host ordinary mapping"],
    "G34": ["at any nesting depth"],
    "G35": ["declaration order"],
    "G54": ["written as a backslash then a backtick", "with those escapes replaced"],
    "G60": ["the empty array yields 0"],
    "G61": ["input order. The empty array yields the empty array"],
    "G69": ["and to nothing else"],
}

KEPT_C = ["C02", "C05", "C08", "C12", "C14", "C15", "C17", "C19", "C20", "C22", "C24", "C26"]
KEPT_G = ["G03", "G22", "G25", "G27", "G28", "G29", "G34", "G35", "G54", "G60", "G61", "G69"]
KEPT = KEPT_C + KEPT_G
FIND = {"C02": (None, "of an empty array yields null"), "C22": ("yields a non-null value", None)}   # node text where the atomizer reworded a side (step 3, recall)


def words(folder):
    return sum(len(f.read_text(encoding="utf-8").split()) for f in folder.glob("*.md"))


if __name__ == "__main__":
    out, items = Path(sys.argv[1]), sys.argv[2:]
    assert items and all(i in EDITS for i in items), items
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    for f in PUBLIC.glob("*.md"):
        shutil.copy(f, out / f.name)
    n_edits = 0
    for item in items:
        for name, old, new in EDITS[item]:
            text = (out / name).read_text(encoding="utf-8")
            assert text.count(old) == 1, (item, name, text.count(old), old[:60])
            (out / name).write_text(text.replace(old, new), encoding="utf-8")
            n_edits += 1
    for f in out.glob("*.md"):   # a bullet emptied by removals is dropped
        t = f.read_text(encoding="utf-8")
        f.write_text(re.sub(r"(?m)^- *\n", "", t), encoding="utf-8")
    spec = "\n".join(f.read_text(encoding="utf-8") for f in sorted(out.glob("*.md")))
    for item in items:
        if item in PHRASES:
            for side, phrase in zip("AB", PHRASES[item]):
                assert spec.count(phrase) == 1, (item, side, phrase, spec.count(phrase))
        for k in KEY.get(item, []):
            assert k not in spec, (item, "key phrase left", k)
    print(f"{n_edits} edits for {len(items)} items; phrases and keys ok; words {words(PUBLIC)} -> {words(out)}")
