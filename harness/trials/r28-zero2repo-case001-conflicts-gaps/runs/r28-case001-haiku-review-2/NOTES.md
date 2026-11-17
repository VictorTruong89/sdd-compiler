# Implementation notes

Tomlparse is a pure-Python TOML v1.1.0 parser. Layout:

- `src/tomlparse/__init__.py` — exports `loads`, `load`, `TOMLDecodeError`, `__version__`.
- `src/tomlparse/_parser.py` — the parser (hand-written; no stdlib `tomllib`).
- `src/tomlparse/_errors.py` — `TOMLDecodeError(msg, doc, pos)`.
- `tests/test_tomlparse.py` — unit tests (`PYTHONPATH=src python3 -m unittest tests.test_tomlparse`).
- `pyproject.toml` — src-layout metadata for an optional install; nothing needs building to import.

## Conflicts between the specification files

Where the sources disagree I chose one side as listed. The spec files are unchanged.

### C-01 Local time seconds
- **PRD Terminology, "Local time"** (`spec/Full_PRD.md`, line 28): "Its seconds are always written."
- **PRD FP-02 "Seconds and fractions"** (line 116) and **Non-goals** (line 64): seconds may be omitted, and date-times whose seconds are omitted are accepted.
- **Built:** seconds may be omitted (`07:32` → `time(7, 32)`), as TOML v1.1.0 allows.

### C-02 Rounding of fractional seconds
- **PRD FP-02** (line 116): digits after the sixth are "dropped (truncated, not rounded)".
- **Contract, `loads` return shape** (`spec/Interface_Contract.md`, line 46): local time's "fraction rounded to the nearest microsecond".
- **Built:** truncation, for all time values (`07:00:00.1234567` → microsecond 123456). The PRD's wording is explicit and covers every time value; the Contract mentions only local times.

### C-03 Trailing comma in arrays
- **PRD FP-01** (line 89): arrays may "end with a trailing comma".
- **Contract, return shape** (line 40): an array whose last element is followed by a comma "is refused".
- **Built:** accepted (`[1, 2,]` → `[1, 2]`). TOML v1.1.0 allows it, and the Contract's rule contradicts it.

### C-04 Which float-converter results are refused
- **PRD Terminology, "Float converter"** (line 29): only an exact `dict` or exact `list` is refused.
- **PRD FP-05** (line 183) and **Contract** failure tables (lines 56, 81): subclasses of `dict`/`list` are refused too.
- **Built:** `isinstance` check, so subclasses are refused as well. Two sources say so and the Terminology line is the outlier.

### C-05 Sub-tables under a table created by dotted keys
- **PRD Terminology, "Dotted key"** (line 23): a table created by dotted keys "cannot receive a sub-table through a header".
- **PRD FP-01** (line 86): a sub-table of such a table that has not itself been defined may still be declared by a header.
- **Built:** the FP-01 rule. `a.b.c = 1` followed by `[a.b.d]` is accepted. `[a.b]` after `a.b.c = 1` is refused, because `a.b` was defined by dotted keys. This matches the TOML v1.1.0 example for dotted keys.

### C-06 Empty keys
- **Contract, return shape** (line 38): keys are `str`, "never empty".
- **PRD FP-01** (line 84): "A quoted key may be empty."
- **Built:** `"" = 1` is accepted and yields the key `""`. TOML permits it and the PRD states it explicitly. Bare keys still need at least one character.

### C-07 Quote characters before the closing delimiter of a multiline basic string
- **PRD FP-02, "Strings"** (line 111): may end with one or two quotes next to the closing delimiter.
- **PRD FP-02, "Boundary"** (line 127): refused.
- **Built:** accepted, as TOML specifies. `"""a""""` → `a"`, `"""a"""""` → `a""`. Runs of six or more quotes are refused.

### C-08 Leading line feed in multiline literal strings
- **PRD FP-02** (line 108): a multiline literal string keeps its first line feed.
- **PRD FP-02** (line 109): both multiline forms discard a line feed right after the opening delimiter.
- **Built:** both multiline forms discard it (TOML). A CRLF right after the opening delimiter is discarded too.

### C-09 Raw tab in one-line strings
- **PRD FP-02, "Basic-string escapes"** (line 112): a tab in a one-line string "must be written as backslash-t".
- **PRD FP-02, "Boundary"** (line 126): control characters are refused "other than tab".
- **Built:** a raw tab is accepted in every string form, as TOML allows. The Boundary rule is the one consistent with the TOML grammar.

### C-10 Case of hex digits in `\x`, `\u`, `\U`
- **PRD FP-02** (line 112): "Hex digits are case-insensitive."
- **PRD FP-02, "Boundary"** (line 126): uppercase escape digits are refused.
- **Built:** case-insensitive (`"é"` and `"é"` are both `é`).

### C-11 Whitespace after a line-ending backslash
- **PRD FP-02** (line 110): the backslash removes the line ending and all whitespace, including line feeds, up to the next non-whitespace character.
- **PRD FP-02** (line 111): "the next line's leading spaces and tabs are kept."
- **Built:** the first form (TOML). Spaces, tabs and line feeds are removed up to the next non-whitespace character or the closing delimiter.

### C-12 Carriage returns in multiline basic strings
- **PRD FP-01** (line 92): a CRLF is a single line feed everywhere, including inside string values.
- **PRD FP-02** (line 109): line endings inside a multiline basic string are kept "carriage returns included".
- **Built:** the FP-01 rule. CRLF becomes LF everywhere, including in multiline strings. A bare CR outside a CRLF pair is refused. Error offsets still refer to the original text.

### C-13 Signed zero integers
- **PRD FP-02, "Integers"** (line 113): a signed zero is the integer 0.
- **PRD FP-02, "Boundary"** (line 124): `+0` and `-0` are refused.
- **Built:** accepted (`+0`, `-0` → `0`). This matches the TOML grammar, where a decimal integer may carry a sign.

### C-14 Separator in date-times
- **PRD Terminology, "Offset date-time"** (line 25): the date and time are joined by `T` or `t`.
- **PRD FP-02, "Date-time values"** (line 115): the separator may be `T`, `t` or a space.
- **Built:** a space is accepted for every date-time kind, offset or local (`1979-05-27 07:32:00-07:00`). The RFC 3339 form that TOML uses allows it, and the FP-02 rule is the more specific of the two.

## Choices and assumptions the specification does not settle

- **Invalid UTF-8 in `load`.** Not specified. The bytes are decoded strictly; the result is a `UnicodeDecodeError` (a `ValueError` subclass), not a `TOMLDecodeError`, because there is no decoded text to put in `doc`.
- **Byte-order mark.** A UTF-8 BOM decodes to U+FEFF, which is not valid at the start of a document, so it is refused with a `TOMLDecodeError` at offset 0.
- **Text-mode detection in `load`.** `io.TextIOBase` instances are refused before reading. Any other object is read, and a `str` result is refused. An object without `read` (for example a path string) is refused with `TypeError`.
- **Non-`str` input to `loads`.** Refused with `TypeError`, including `bytes`, `bool`, `None` and file objects.
- **Control characters in comments.** Refused, except tab and CRLF. TOML forbids them; the PRD does not mention comments.
- **Surrogate code points** in the text, and escapes that produce them, are refused.
- **Escape code points** above U+10FFFF are refused.
- **Year 0000** is refused, because Python's `date` starts at year 1.
- **Seconds 60** (leap seconds) are refused, as the PRD's 0–59 rule requires.
- **Hour and minute offsets** in date-times must have hours 0–23 and minutes 0–59. Otherwise they are refused.
- **Contract wording "hexadecimal digits written in lowercase"** (return shape, `loads`). The PRD says prefixes are lowercase and digits may be either case. The value is what gets returned, so the digit case in the source does not matter and nothing was changed.
- **Table-definition rules.** Tables created implicitly by a header parent (`[a.b.c]` creates `a` and `a.b`) can be defined later by a header, or extended by dotted keys. Tables created or extended by dotted keys cannot be defined by a header. Tables defined by a header cannot be extended by dotted keys. Inline tables are frozen once written. Static arrays cannot be extended by headers or dotted keys. Arrays of tables cannot be extended by dotted keys, and a header cannot redefine them as a plain table.
- **Error positions.** `pos` is the offset of the offending character. Where a rule is broken at a key or header (duplicate key, redefined table), `pos` is the start of that key or header. A premature end of input reports `pos == len(doc)`, which `str(err)` describes as "end of document".
- **`TOMLDecodeError` report wording** is `"<msg> (at line L, column C)"`, or `"<msg> (at end of document)"`.
- **Float converter.** It receives the float's text exactly as written, including underscores, sign and exponent. It is not called for integers, strings, booleans or date-times. Exceptions raised by the converter propagate unchanged. The default `float` path strips underscores before converting.
- **Speed** is not a requirement, and the parser is a straightforward recursive-descent implementation with regex-assisted scanning of string runs.
