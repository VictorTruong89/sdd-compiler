# Implementation notes

Scope: the Tomlparse library under `src/tomlparse/` (entries `loads`, `load`, `TOMLDecodeError`).
Tests: `tests/test_tomlparse.py` (run with `PYTHONPATH=src python3 -m unittest discover -s tests`).
Verified on Python 3.13 and 3.11. Python 3.8 is the declared floor; no 3.8 interpreter was available,
so 3.8 compatibility was checked by reading only (no f-strings, no `match`, no builtin generics).

## Conflicts between spec documents

Each entry gives what each side says, then what was built.

1. **Trailing comma in arrays.**
   - `Interface_Contract.md`, `loads` return shape: "an array whose last element is followed by a comma is refused".
   - `Full_PRD.md`, FP-01 normal behavior: arrays "end with a trailing comma"; Non-goals say the product accepts TOML v1.1.0 documents.
   - Built: **accepted** (TOML v1.1.0 allows it, and the PRD is explicit).

2. **First line feed of a multiline literal string.**
   - `Full_PRD.md`, FP-02, the bullet on escapes: "A multiline literal string keeps every character after its opening delimiter, including a first line feed."
   - Same section, next bullet: "In both multiline forms a line feed immediately after the opening delimiter is discarded."
   - Built: **discarded** for both multiline forms (TOML v1.1.0).

3. **Carriage returns inside multiline basic strings.**
   - `Full_PRD.md`, FP-02: "Line endings inside a multiline basic string are kept exactly as written, carriage returns included."
   - `Full_PRD.md`, FP-01 normal behavior and FP-03: a CRLF pair "is treated as a single line feed everywhere, including inside string values".
   - Built: **CRLF becomes one line feed** everywhere, including inside strings. A bare CR (not part of CRLF) is refused.

4. **Raw tab in one-line strings.**
   - `Full_PRD.md`, FP-02 basic-string escapes: "A tab in a one-line string must be written as backslash-t."
   - Same section's boundary list: raw control characters "other than tab" are refused, so a raw tab is implied to be allowed. TOML v1.1.0 also allows a literal tab.
   - Built: **raw tab allowed** in basic and literal strings; the `\t` escape also works.

5. **Signed zero.**
   - `Full_PRD.md`, FP-02 normal: "optionally signed; a signed zero is the integer 0".
   - Same section's boundary list: "a zero with a sign (`+0`, `-0`)" is refused.
   - Built: **`+0` and `-0` accepted as `0`** (the normal behavior and TOML v1.1.0).

6. **Quote characters before the closing delimiter of a multiline string.**
   - `Full_PRD.md`, FP-02 normal: both multiline forms may contain one or two quote characters "including directly before the closing delimiter".
   - Same section's boundary list: "a quote character directly before the closing delimiter of a multiline basic string" is refused.
   - Built: **1 or 2 quotes before the closing delimiter are content** (for example `"""x""""` gives `x"`); a run of 6 or more quotes is refused. This follows TOML v1.1.0 and applies to both multiline forms.

7. **Case of hex digits in `\x`, `\u`, `\U` escapes.**
   - `Full_PRD.md`, FP-02 normal: "Hex digits are case-insensitive."
   - Same section's boundary list: "escape digits written as uppercase letters" are refused.
   - Built: **case-insensitive** (the normal behavior). The `\X` prefix is still lowercase only.

8. **Seconds in local times.**
   - `Full_PRD.md`, Terminology: a local time's "seconds are always written".
   - `Full_PRD.md`, FP-02 normal: "In any value with a time part, seconds may be omitted". Non-goals also mention date-times with omitted seconds.
   - Built: **seconds may be omitted** for local times as well as date-times and offset date-times.

9. **Rounding of fractional seconds.**
   - `Interface_Contract.md`, `loads` return shape: a local time's "fraction rounded to the nearest microsecond".
   - `Full_PRD.md`, FP-02: fractional digits beyond six "are dropped (truncated, not rounded)".
   - Built: **truncation**, as the PRD states it for every time value (including local times). Example: `07:32:00.1234567` gives microsecond `123456`.

10. **Converter results that are subclasses of dict or list.**
    - `Full_PRD.md`, Terminology: "Only a result whose type is exactly `dict` or exactly `list` is refused."
    - `Full_PRD.md`, FP-05 and `Interface_Contract.md`: dict or list "or an instance of a subclass of either" is refused.
    - Built: **`isinstance` check**, so subclass instances are refused with `ValueError`.

11. **Hex digit case in integer return shape.**
    - `Interface_Contract.md`: "integers: `int` (never `bool`), hexadecimal digits written in lowercase".
    - Integers are Python `int` values and have no written form, so this has no observable effect. Nothing was built for it.

## Points the specification does not state

- **Invalid UTF-8 in `load()`.** Not specified. Built: `TOMLDecodeError` with `doc` set to the bytes decoded with `errors="replace"` and `pos` at the first invalid byte. The decode is strict UTF-8, so a UTF-8 byte-order mark is not stripped. A leading U+FEFF is therefore an error.
- **Text-mode detection in `load()`.** A `io.TextIOBase` instance is refused before reading. Any other object whose `read()` returns `str` is refused after reading. An object without `read`, or whose `read()` returns something other than bytes, raises `TypeError`.
- **Control characters.** Raw control characters are refused in strings and comments, except tab, following TOML v1.1.0. DEL (U+007F) is treated as a control character and refused in strings, comments, and keys.
- **Comments.** Non-ASCII text is allowed. Control characters other than tab are refused (TOML v1.1.0).
- **Year 0000.** The TOML grammar allows four-digit years including `0000`. Python's `date` cannot represent year 0, so `0000-…` values are refused as invalid calendar dates.
- **Leap second.** `second = 60` is refused, following the PRD's 0–59 rule.
- **Offset range.** Offset hours must be 0–23 and offset minutes 0–59.
- **Dotted keys and implicit tables.** A table created implicitly by a header (a super-table such as `a` in `[a.b]`) may receive dotted keys later. After that it counts as created by dotted keys, so a header can no longer define it. This follows the TOML rules that the PRD cites.
- **Array-of-tables parents.** A parent created implicitly by `[[x.y]]` is a plain table. A later `[x]` header may define it, and it may then receive keys.
- **Inline tables.** Each inline table is frozen as soon as it is closed. Any later header or dotted key that reaches it, directly or through a sub-table, is refused.
- **Deep nesting.** A `RecursionError` during parsing is converted to `TOMLDecodeError`. The spec forbids the decode error from being a recursion error, but says nothing about deep documents. This conversion is the chosen behavior.
- **Converter timing.** `parse_float` is called as each float is parsed, before the rest of the document is checked. If the document is later found invalid, the converter has already been called for earlier floats; its results are discarded.
- **Converter for float-like tokens.** The converter is called with the exact source token, including underscores, sign, and exponent. The special spellings `inf`, `+inf`, `-inf`, `nan`, `+nan`, `-nan` go to the converter as text too.
- **Error positions.** Offsets count characters (code points), not bytes. Line and column follow the PRD rules. For a `\r\n` line ending the line counts the LF only.
- **Error position at end of input.** When the parser reaches the end of the document while still expecting something, the offset is the document length, and the report says "end of document".
- **`loads` subclass input.** Instances of `str` subclasses are accepted.
- **Package version.** `tomlparse.__version__` is `"2.4.0"`, matching the PRD's compatibility statement. `pyproject.toml` declares the same version.
