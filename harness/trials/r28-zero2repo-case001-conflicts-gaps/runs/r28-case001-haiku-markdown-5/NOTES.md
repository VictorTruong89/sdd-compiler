# Implementation notes

Tomlparse 2.4.0 — pure-Python TOML v1.1.0 parser.

Layout:

- `src/tomlparse/__init__.py` — public `loads`, `load`, `TOMLDecodeError` (plus type checks and UTF-8 decoding for `load`).
- `src/tomlparse/_parser.py` — the recursive-descent parser (no use of the standard `tomllib`).
- `src/tomlparse/_errors.py` — `TOMLDecodeError(msg, doc, pos)`, a `ValueError` subclass with `lineno` / `colno`.
- `tests/test_tomlparse.py` — unittest suite (`PYTHONPATH=src python3 -m unittest discover -s tests`).
- `pyproject.toml` — src-layout package, setuptools backend, no runtime dependencies.

Spec references below are `file → section/feature point (line in the file)`.

## Conflicts between the specification files

Where two places disagree, the choice is listed with what each side says.

1. **Empty keys.**
   - `spec/Full_PRD.md` FP-01, Normal behavior (line 84): "A quoted key may be empty".
   - `spec/Interface_Contract.md` `tomlparse.loads`, Return shape (line 37): "keys: `str`, never empty".
   - **Built:** empty quoted keys (`"" = 1`, `'' = 1`) are accepted. Bare keys are never empty by grammar.

2. **Trailing comma in arrays.**
   - `spec/Full_PRD.md` FP-01, Normal behavior (line 89): arrays "end with a trailing comma".
   - `spec/Interface_Contract.md` `tomlparse.loads`, Return shape (line 40): "an array whose last element is followed by a comma is refused".
   - **Built:** trailing commas in arrays are accepted, as the PRD and TOML v1.1.0 say. Inline tables also accept a trailing comma (PRD FP-01, line 88).

3. **Sub-table headers under dotted keys.**
   - `spec/Full_PRD.md` terminology, "Dotted key" row (line 23): "A table created by dotted keys cannot receive a sub-table through a header".
   - `spec/Full_PRD.md` FP-01, Normal behavior (line 86): a sub-table "may still be declared by a header, as TOML v1.1.0 allows".
   - **Built:** the FP-01 rule. A header may create a sub-table under a dotted-key table. A header may not name a table that dotted keys defined (refused, per FP-01 boundary).

4. **Signed zero.**
   - `spec/Full_PRD.md` FP-02, Normal behavior (line 113): "optionally signed; a signed zero is the integer 0".
   - `spec/Full_PRD.md` FP-02, Boundary (line 124): "a zero with a sign (`+0`, `-0`)" is refused.
   - **Built:** `+0` and `-0` are accepted as the integer 0 (the normal-behavior rule and the TOML grammar). A signed float zero such as `-0.0` was already valid.

5. **Quote characters before a multiline closing delimiter.**
   - `spec/Full_PRD.md` FP-02, Normal behavior (line 111): one or two quote characters may appear "including directly before the closing delimiter".
   - `spec/Full_PRD.md` FP-02, Boundary (line 127): "a quote character directly before the closing delimiter of a multiline basic string" is refused.
   - **Built:** the normal-behavior rule. One or two extra quotes before the closing `"""` or `'''` are content. A run of six or more quotes is refused.

6. **Case of hex digits in escapes.**
   - `spec/Full_PRD.md` FP-02, Normal behavior (line 112): "Hex digits are case-insensitive".
   - `spec/Full_PRD.md` FP-02, Boundary (line 126): "escape digits written as uppercase letters" are refused.
   - **Built:** the normal-behavior rule. `\u00e9` and `\u00E9` are both accepted. Escape letters (`\X`, `\N`, …) must be lowercase.

7. **Carriage returns inside multiline strings.**
   - `spec/Full_PRD.md` FP-01, Normal behavior (line 92): CRLF is "treated as a single line feed everywhere, including inside string values".
   - `spec/Full_PRD.md` FP-02, Normal behavior (line 109): line endings in a multiline basic string "are kept exactly as written, carriage returns included".
   - **Built:** the FP-01 rule. Every CRLF becomes LF, including inside strings. A bare CR (not followed by LF) is an error everywhere. The document is not pre-normalised, so error offsets still refer to the original text.

8. **Rounding of fractional seconds.**
   - `spec/Full_PRD.md` FP-02, Normal behavior (line 116): digits after the sixth are "dropped (truncated, not rounded)".
   - `spec/Interface_Contract.md` `tomlparse.loads`, Return shape (line 46): local time's "fraction rounded to the nearest microsecond".
   - **Built:** truncation, for every time value (local time, local date-time and offset date-time). This follows the PRD, which states the rule explicitly for all fractions.

9. **Omitted seconds in local times.**
   - `spec/Full_PRD.md` terminology, "Local time" row (line 28): "Its seconds are always written".
   - `spec/Full_PRD.md` FP-02, Normal behavior (line 116): "In any value with a time part, seconds may be omitted".
   - **Built:** seconds may be omitted in every time value, so `07:32` is a local time with second 0. This is what TOML v1.1.0 allows.

10. **Float converter refusals.**
    - `spec/Full_PRD.md` terminology, "Float converter" row (line 29): only a result whose type is "exactly `dict` or exactly `list`" is refused.
    - `spec/Full_PRD.md` FP-05, Normal behavior (line 179) and Boundary (line 183), and `spec/Interface_Contract.md` `tomlparse.loads` Failures (line 56): subclass instances are refused as well.
    - **Built:** `isinstance` checks, so subclasses of `dict` and `list` are refused too. This raises a plain `ValueError`, not a `TOMLDecodeError`.

11. **Hex-digit case in integer return shape (not a behavioural conflict).**
    - `spec/Interface_Contract.md` `tomlparse.loads`, Return shape (line 41): "integers: `int` (never `bool`), hexadecimal digits written in lowercase".
    - An `int` has no digit case, so this line has no effect on the values returned. The parser returns the numeric value of `0xDEADbeef` as the same integer regardless of case.

## Points the specification does not state (my assumptions)

- **Invalid UTF-8 in `load`.** The spec gives no failure for undecodable bytes. I raise `TOMLDecodeError` with `doc` = the bytes decoded with `errors="replace"` and `pos` = the character index of the first bad byte. A UTF-8 byte-order mark is not stripped. It is not whitespace, so a leading BOM is an error.
- **Offset ranges.** A numeric UTC offset is refused if its hours are above 23 or its minutes above 59. `Z` and `z` both give `datetime.timezone.utc`.
- **Seconds range.** Seconds 60 (leap seconds) are refused. The PRD requires 0–59.
- **Fraction digits.** Digits beyond six are truncated, and seconds may carry any number of fraction digits.
- **Control characters.** TOML forbids U+0000–U+0008, U+000A–U+001F and U+007F in strings and comments (tab is allowed). The PRD only says "raw control characters other than tab". DEL (U+007F) is treated as a control character.
- **`[[` and `]]`.** The brackets of an array-of-tables header must be adjacent (`[[a]]`, not `[[a] ]`). Spaces are allowed elsewhere inside headers and around dots.
- **Newlines in inline tables.** Newlines and comments are allowed around the commas and braces of an inline table, and before its first key or after its last value. They are not allowed around `=`, or inside a scalar value.
- **Dotted-key state rules.** A dotted-key walk through a table that a header created implicitly marks that table as "defined by dotted keys". A later header that names it is then refused. The PRD says a table defined by dotted keys cannot be reopened by a header, and I read "defined" to include this case.
- **Error positions.** For duplicate keys and key/table conflicts, `pos` is the start of the key or header. For other errors, `pos` is the offending character, or the end of the document for an unexpected end.
- **Deep nesting.** Recursion is used for arrays and inline tables. Extremely deep nesting (hundreds of levels) exceeds Python's recursion limit. That `RecursionError` is converted to `TOMLDecodeError` ("nested too deeply"), so the parse fails cleanly rather than with a recursion error. This is a practical limit; the spec states none.
- **`parse_float`.** Called once per float token, in document order, with the token exactly as written (sign, underscores and exponent included). Exceptions from the callable propagate unchanged. Its argument is not validated: a non-callable value fails with the usual `TypeError` from calling it.
- **Python versions.** The code avoids features newer than Python 3.8. Only Python 3.13 was available for testing.
- **Non-ASCII text.** Allowed in quoted keys, strings and comments. Bare keys remain ASCII-only, as the PRD requires.
