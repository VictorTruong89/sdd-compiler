"""Make round 28's case001 spec: plant the kept conflicts and remove the kept gaps in a copy of case001's public spec.
No model call.

    python3 notes/plant.py work/spec-planted C03 ... G01 ...       (from the trial folder)

Round 28, case001 (copied from ../r28-zero2repo-case005-conflicts-gaps/notes/plant.py; method unchanged,
new anchors for case001):
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
PUBLIC = HERE.parents[2] / "benchmarks/zero2repo/download/Zero2Repo/benchmark/cases/case001/public"
PRD, IC = "Full_PRD.md", "Interface_Contract.md"

EDITS = {
    # ---------------- conflicts: side B added in one place
    "C03": [(PRD, "| **Local time** | A TOML clock time with no date. Constructed as a time. |",
             "| **Local time** | A TOML clock time with no date. Constructed as a time. Its seconds are always written. |")],
    "C04": [(IC, "- local time: `datetime.time` with `tzinfo` `None`.",
             "- local time: `datetime.time` with `tzinfo` `None`, its fraction rounded to the nearest microsecond.")],
    "C07": [(IC, "- arrays and arrays of tables: `list`, elements in document order;",
             "- arrays and arrays of tables: `list`, elements in document order; an array whose last element is followed by a comma is refused;")],
    "C08": [(PRD, "with a leading zero (other than a lone `0`);", "with a leading zero (other than a lone `0`); a zero with a sign (`+0`, `-0`);")],
    "C10": [(PRD, "a line feed immediately after the opening delimiter is discarded; later line feeds are kept.",
             "a line feed immediately after the opening delimiter is discarded; later line feeds are kept. "
             "Line endings inside a multiline basic string are kept exactly as written, carriage returns included.")],
    "C11": [(PRD, "whose interior is taken as written (backslashes included).",
             "whose interior is taken as written (backslashes included). A multiline literal string keeps every character after its "
             "opening delimiter, including a first line feed.")],
    "C12": [(PRD, "so that the value ends in one or two quote characters.",
             "so that the value ends in one or two quote characters. After a line-ending backslash, the next line's leading spaces and tabs are kept.")],
    "C13": [(PRD, "an unclosed string of any form;", "an unclosed string of any form; a quote character directly before the closing delimiter of a multiline basic string;")],
    "C14": [(PRD, "so the two spellings of the same characters can be different keys.",
             "so the two spellings of the same characters can be different keys. A tab in a one-line string must be written as backslash-t.")],
    "C16": [(IC, "integers: `int` (never `bool`);", "integers: `int` (never `bool`), hexadecimal digits written in lowercase;")],
    "C17": [(PRD, "incomplete or non-hex `\\x`, `\\u` or `\\U` runs,", "incomplete or non-hex `\\x`, `\\u` or `\\U` runs, escape digits written as uppercase letters,")],
    "C18": [(PRD, "| **Offset date-time** | A TOML date-time with a `Z` / `z` suffix or a numeric offset. Constructed as a timezone-aware datetime. |",
             "| **Offset date-time** | A TOML date-time with a `Z` / `z` suffix or a numeric offset. Constructed as a timezone-aware datetime. "
             "Its date and time are joined by `T` or `t`. |")],
    "C29": [(PRD, "Specified in FP-05. |\n| **Decode error**",
             "Specified in FP-05. Only a result whose type is exactly `dict` or exactly `list` is refused. |\n| **Decode error**")],
    "C35": [(IC, "- keys: `str`;", "- keys: `str`, never empty;")],
    "C36": [(PRD, "Dots inside a quoted part are part of that part’s name, not separators. |",
             "Dots inside a quoted part are part of that part’s name, not separators. A table created by dotted keys cannot receive a sub-table through a header. |")],
    # ---------------- gaps: every statement removed
    "G01": [(PRD, " When the document ends where more input is required (an unfinished pair, string, array, inline table or header), the offset is the document's length, which marks the end of the document rather than an interior line and column.", "")],
    "G03": [(PRD, "- A table header or array-of-tables header that conflicts with what the document already defines (it would overwrite a value, declare a table a second time, or open a table that may not be opened) fails at a character within that header. Its offset is therefore inside the document, even when that header is the last thing in the document and nothing follows it.\n", "")],
    "G09": [(PRD, "- Nesting depth: a document whose arrays are nested inline 470 levels deep parses successfully, as does a document whose inline tables are nested 310 levels deep and a document with a dotted key of 310 parts; every shallower nesting parses as well. Behaviour beyond those depths is unspecified.\n", "")],
    "G13": [(PRD, "- Bytes that are not valid UTF-8 do not yield a document mapping and the call does not succeed. They are never reinterpreted in another 8-bit encoding, even when that reading would be valid TOML.\n", ""),
            (IC, "| the bytes are not valid UTF-8 | an exception (its type is the implementer's choice); no mapping is returned |\n", "")],
}

PHRASES = {
    "C03": ("In any value with a time part, seconds may be omitted", "Its seconds are always written"),
    "C04": ("any digits after the sixth are dropped (truncated, not rounded)", "rounded to the nearest microsecond"),
    "C07": ("contain comments between elements, and end with a trailing comma", "an array whose last element is followed by a comma is refused"),
    "C08": ("a signed zero is the integer 0", "a zero with a sign"),
    "C10": ("holds line feeds only", "carriage returns included"),
    "C11": ("In both multiline forms a line feed immediately after the opening delimiter is discarded", "including a first line feed"),
    "C12": ("removes the line ending and all whitespace (spaces, tabs, line feeds)", "the next line's leading spaces and tabs are kept"),
    "C13": ("including directly before the closing delimiter", "a quote character directly before the closing delimiter of a multiline basic string"),
    "C14": ("raw control characters other than tab inside any string form", "A tab in a one-line string must be written as backslash-t"),
    "C16": ("hex digits may be either case", "hexadecimal digits written in lowercase"),
    "C17": ("Hex digits are case-insensitive", "escape digits written as uppercase letters"),
    "C18": ("The separator between date and time may be `T`, `t`, or a space", "Its date and time are joined by `T` or `t`"),
    "C29": ("(and not an instance of a subclass of either)", "exactly `dict` or exactly `list` is refused"),
    "C35": ("A quoted key may be empty", "keys: `str`, never empty"),
    "C36": ("may still be declared by a header", "cannot receive a sub-table through a header"),
}

KEY = {
    "G01": ["the offset is the document's length"],
    "G03": ["fails at a character within that header"],
    "G09": ["470", "310"],
    "G13": ["not valid UTF-8", "never reinterpreted"],
}

KEPT_C = ["C03", "C04", "C07", "C08", "C10", "C11", "C12", "C13", "C14", "C16", "C17", "C18", "C29", "C35", "C36"]
KEPT_G = ["G01", "G03", "G09", "G13"]
KEPT = KEPT_C + KEPT_G
FIND = {"C03": ("seconds may be omitted", None)}   # node text where the atomizer reworded a side (step 3, recall)


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
