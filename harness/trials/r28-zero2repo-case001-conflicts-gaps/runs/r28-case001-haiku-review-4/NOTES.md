# Implementation notes

Tomlparse 2.4.0, a pure-Python TOML v1.1.0 parser. Layout:

- `src/tomlparse/__init__.py` — public names `loads`, `load`, `TOMLDecodeError`.
- `src/tomlparse/_core.py` — the hand-written parser (no `tomllib` or other TOML library is used).
- `src/tomlparse/_errors.py` — `TOMLDecodeError(msg, doc, pos)`.
- `tests/test_tomlparse.py` — unit tests written from the spec; run with `PYTHONPATH=src python3 -m unittest tests.test_tomlparse`.
- `pyproject.toml` — src-layout setuptools metadata (no runtime dependencies).

## Spec conflicts and what was built

Each entry gives the two sides (file and line as the files now stand) and the choice made.
"PRD" is `spec/Full_PRD.md`, "Contract" is `spec/Interface_Contract.md`.

### C-01 Local time seconds
- Side A: PRD Terminology, "Local time" row (line 28): "Its seconds are always written."
- Side B: PRD FP-02 "Seconds and fractions" (line 116): "seconds may be omitted, in which case the second is 0"; PRD Non-goals (line 64) also accepts omitted seconds.
- **Built:** seconds may be omitted in the document (`07:32` is valid, second = 0). Every constructed `datetime.time` has a seconds value, so the "always written" wording still holds for the result.

### C-02 Rounding of fractional seconds in local times
- Side A: PRD FP-02 (line 116): digits after the sixth are "dropped (truncated, not rounded)."
- Side B: Contract `loads` "Return shape" (line 46): local time fraction "rounded to the nearest microsecond."
- **Built:** truncation (`.1234567` gives microsecond 123456). The PRD is more specific and states the rule for every value with a time part.

### C-03 Trailing comma in arrays
- Side A: PRD FP-01 "Normal behavior" (line 89): arrays "end with a trailing comma."
- Side B: Contract `loads` "Return shape" (line 40): "an array whose last element is followed by a comma is refused."
- **Built:** accepted (`[1, 2,]` is `[1, 2]`). TOML v1.1.0 allows the trailing comma, and the PRD is the behavioural authority.

### C-04 Which float-converter results are refused
- Side A: PRD Terminology "Float converter" (line 29): "Only a result whose type is exactly `dict` or exactly `list` is refused."
- Side B: PRD FP-05 (line 183) and Contract `loads` (line 56) and `load` (line 81) Failures tables: a `dict` or `list` "(or an instance of a subclass of either)" is refused.
- **Built:** `isinstance` check, so subclasses are refused too. Three spec locations agree on this; the Terminology row is the outlier.

### C-05 Sub-tables under a table created by dotted keys
- Side A: PRD Terminology "Dotted key" (line 23): "A table created by dotted keys cannot receive a sub-table through a header."
- Side B: PRD FP-01 "Normal behavior" (line 86): "a sub-table of it that has not itself been defined may still be declared by a header, as TOML v1.1.0 allows."
- **Built:** side B. `[fruit]` / `apple.color = "red"` / `[fruit.apple.texture]` is valid. Declaring a table that dotted keys already defined (`[fruit.apple]` after `apple.color = ...`) is refused. A dotted key whose path runs through a value is refused, so `a.b = 1` followed by `[a.b.c]` is refused because `a.b` is an integer.

### C-06 Keys may be empty
- Side A: Contract `loads` "Return shape" (line 38): keys are `str`, "never empty."
- Side B: PRD FP-01 "Normal behavior" (line 84): "A quoted key may be empty."
- **Built:** quoted keys may be empty (`"" = 1` gives key `""`). Bare keys must be non-empty by grammar. The PRD is the TOML rule.

### C-07 Quote characters before the closing delimiter of a multiline basic string
- Side A: PRD FP-02 (line 111): both multiline forms "may contain one or two of their own quote characters ... including directly before the closing delimiter."
- Side B: PRD FP-02 Boundary (line 127): refused: "a quote character directly before the closing delimiter of a multiline basic string."
- **Built:** side A. A run of 3 to 5 quotes closes the string, and the extra one or two are content (`"""a""""` is `a"`). A run of six or more is refused. This matches TOML.

### C-08 Leading line feed in multiline literal strings
- Side A: PRD FP-02 (line 108): a multiline literal "keeps every character after its opening delimiter, including a first line feed."
- Side B: PRD FP-02 (line 109): "In both multiline forms a line feed immediately after the opening delimiter is discarded."
- **Built:** side B. The first line feed is discarded in both multiline forms, as TOML specifies.

### C-09 Raw tab characters in one-line strings
- Side A: PRD FP-02 (line 112): "A tab in a one-line string must be written as backslash-t."
- Side B: PRD FP-02 Boundary (line 126): refused raw control characters are those "other than tab."
- **Built:** side B. A raw tab is accepted in every string form (TOML allows it).

### C-10 Case of hex digits in `\x`, `\u`, `\U` escapes
- Side A: PRD FP-02 (line 112): "Hex digits are case-insensitive."
- Side B: PRD FP-02 Boundary (line 126): refused "escape digits written as uppercase letters."
- **Built:** side A. `"é"` is accepted.

### C-11 Whitespace after a line-ending backslash
- Side A: PRD FP-02 (line 110): the line-ending backslash "removes the line ending and all whitespace ... up to the next non-whitespace character or the closing delimiter."
- Side B: PRD FP-02 (line 111): "After a line-ending backslash, the next line's leading spaces and tabs are kept."
- **Built:** side A. The continuation line's leading whitespace is removed, as TOML specifies.

### C-12 Carriage returns in multiline basic strings
- Side A: PRD FP-01 (line 92): a CR LF pair is "a single line feed everywhere, including inside string values."
- Side B: PRD FP-02 (line 109): "Line endings inside a multiline basic string are kept exactly as written, carriage returns included."
- **Built:** side A. CR LF is normalised to LF before parsing, so multiline strings contain only LF. A bare CR (not followed by LF) is refused everywhere. Error locations are still reported against the caller's original text.

### C-13 Signed zero integers
- Side A: PRD FP-02 Integers (line 113): "a signed zero is the integer 0."
- Side B: PRD FP-02 Boundary (line 124): refused "a zero with a sign (`+0`, `-0`)."
- **Built:** side A. `+0` and `-0` are the integer 0.

### C-14 Separator in offset date-times
- Side A: PRD Terminology "Offset date-time" (line 25): date and time "joined by `T` or `t`."
- Side B: PRD FP-02 "Date-time values" (line 115): "The separator between date and time may be `T`, `t`, or a space."
- **Built:** side B. `1979-05-27 07:32:00Z` is an offset date-time. A space separator is allowed for every date-time kind.

## Points the spec does not state (my assumptions)

- **Invalid UTF-8 in `load`.** Not specified. Raised as `TOMLDecodeError` with `doc` set to the text decoded with `errors="replace"` and `pos` set to the character index of the first bad byte.
- **UTF-8 byte-order mark.** Not specified. Refused (the BOM is not valid TOML whitespace, so the parse fails at offset 0).
- **Control characters in comments.** The spec only lists control characters for strings. TOML forbids them in comments (tab is allowed), so they are refused.
- **Years and leap seconds.** Year 0000 is refused, because `datetime.date` cannot represent it. Second 60 is refused because the PRD says seconds must be 0–59.
- **Nesting depth.** Parsing is recursive, so the limit is Python's recursion limit (a few hundred levels of nested arrays or inline tables). Hitting it raises `TOMLDecodeError` ("nested too deeply"), not `RecursionError`, as the spec requires. A valid but extremely deep document is therefore rejected.
- **Dotted keys and implicit tables.** TOML says dotted keys define only tables "not previously created". A dotted key that would extend a table created by a header (even an implicit super-table) is refused.
- **Inline tables.** Newlines and comments inside inline tables are accepted (TOML v1.1.0).
- **Fractions beyond six digits.** Truncated to microseconds, as in C-02.
- **Converter details.** The builtin `float` (or the default) strips underscores before converting. Any other callable receives the token exactly as written (underscores, sign, exponent). A `dict` or `list` result raises `ValueError` as soon as it is seen, which can come before a later syntax error. Exceptions raised by the converter propagate unchanged.
- **Integer spelling.** Python `int` values have no spelling, so the "hexadecimal digits written in lowercase" phrase in the Contract has no effect on results.
- **Error messages.** Wording is free. `str(err)` includes the reason and `line N, column M` (or "at end of document") and the character offset. `TOMLDecodeError` pickles and copies correctly.
- **Input types.** `loads` accepts any `str` subclass. `load` accepts any object with a `read()` method that returns `bytes` or `bytearray`. `io.TextIOBase` instances are refused before reading. A `read()` that returns `str` also raises `TypeError`.
