# Implementation notes

Tomlparse is a pure-Python TOML v1.1.0 parser. Layout: `src/tomlparse/` (the
package; `loads`, `load`, `TOMLDecodeError`), `tests/test_tomlparse.py`
(unit tests, run with `PYTHONPATH=src python -m pytest tests`), and
`pyproject.toml` (src layout, PEP 517 backend, no runtime dependencies).

Where the specification disagrees with itself, I followed the side that matches
TOML v1.1.0 and the more specific statement. Each entry below quotes both sides
and gives the choice. `spec/CONFLICTS.md` lists the same fourteen items.

## Conflicts between the specification files

### C-01: Local time seconds
- **PRD Terminology, "Local time" row:** "Its seconds are always written."
- **PRD FP-02, "Seconds and fractions":** "In any value with a time part, seconds may be omitted, in which case the second is 0." PRD Non-goals also lists "date-times whose seconds are omitted" as accepted.
- **Built:** seconds may be omitted (`07:32` and `1979-05-27T07:32Z` are accepted; the second is 0). This is what TOML v1.1.0 allows, and it is the explicit normative rule.

### C-02: Rounding of fractional seconds in local times
- **PRD FP-02, "Seconds and fractions":** the fraction's first six digits are microseconds, "any digits after the sixth are dropped (truncated, not rounded)."
- **Contract, `loads` return shape:** local time has "its fraction rounded to the nearest microsecond."
- **Built:** truncation, for every value with a time part, including local times. `07:32:00.1234569` gives microsecond 123456. The PRD is the behavioral source, and it states truncation explicitly and emphatically.

### C-03: Trailing comma in arrays
- **PRD FP-01, "Normal behavior":** arrays "end with a trailing comma."
- **Contract, `loads` return shape:** "an array whose last element is followed by a comma is refused."
- **Built:** trailing commas are accepted in arrays (`[1, 2,]` is `[1, 2]`). TOML v1.0 and v1.1 both allow this, and the PRD says so explicitly.

### C-04: Which float-converter results are refused
- **PRD Terminology, "Float converter":** "Only a result whose type is exactly `dict` or exactly `list` is refused."
- **PRD FP-05, Boundary; Contract, `loads` and `load` Failures tables:** a `dict` or `list`, "or an instance of a subclass of either," is refused.
- **Built:** `isinstance` checks, so subclass instances are refused with `ValueError`. The FP-05 boundary rule and both Contract tables agree on this, and only the glossary disagrees.

### C-05: Sub-tables under a table created by dotted keys
- **PRD Terminology, "Dotted key":** "A table created by dotted keys cannot receive a sub-table through a header."
- **PRD FP-01, "Normal behavior":** "After dotted keys have created a nested table, a sub-table of it that has not itself been defined may still be declared by a header, as TOML v1.1.0 allows."
- **Built:** the FP-01 rule. For `[fruit]` `apple.color = "red"` followed by `[fruit.apple.texture]`, the header is accepted. The header `[fruit.apple]` is refused, because `apple` was itself created by dotted keys. TOML's own example uses this pattern.

### C-06: Keys may be empty
- **Contract, `loads` return shape:** keys are `str`, "never empty."
- **PRD FP-01, "Normal behavior":** "A quoted key may be empty."
- **Built:** `"" = 1` is accepted with the key `""`. TOML allows it and the PRD names it explicitly. Bare keys still need at least one character.

### C-07: Quote characters before the closing delimiter of a multiline basic string
- **PRD FP-02, "Strings — four forms":** both multiline forms "may contain one or two of their own quote characters next to each other, including directly before the closing delimiter."
- **PRD FP-02, Boundary:** "a quote character directly before the closing delimiter of a multiline basic string" is refused.
- **Built:** accepted. `"""x""""` is `x"` and `"""x"""""` is `x""`. This follows TOML's own examples, and the rule that permits up to two quotes at the end is stated positively. Runs of six or more quotes are refused, as the spec implies.

### C-08: Leading line feed in multiline literal strings
- **PRD FP-02, "Strings — four forms":** "A multiline literal string keeps every character after its opening delimiter, including a first line feed."
- **PRD FP-02, same section:** "In both multiline forms a line feed immediately after the opening delimiter is discarded."
- **Built:** the first line feed is discarded for both multiline forms, as TOML requires. The second statement is the more specific one, and it covers both forms.

### C-09: Raw tab characters in one-line strings
- **PRD FP-02, "Basic-string escapes":** "A tab in a one-line string must be written as backslash-t."
- **PRD FP-02, Boundary:** the refused raw control characters are those "other than tab inside any string form."
- **Built:** a raw tab is accepted in basic and literal strings. TOML allows it, and the boundary rule treats tab as permitted.

### C-10: Case of hex digits in `\x`, `\u`, `\U` escapes
- **PRD FP-02, "Basic-string escapes":** "Hex digits are case-insensitive."
- **PRD FP-02, Boundary:** "escape digits written as uppercase letters" are refused.
- **Built:** case-insensitive. The positive statement is explicit, and TOML's ABNF matches it. Uppercase digits are accepted (`"é"` is `é`).

### C-11: Whitespace after a line-ending backslash
- **PRD FP-02, "Strings — four forms" (first bullet group):** the line-ending backslash "removes the line ending and all whitespace (spaces, tabs, line feeds) up to the next non-whitespace character or the closing delimiter."
- **PRD FP-02, same section, later bullet:** "After a line-ending backslash, the next line's leading spaces and tabs are kept."
- **Built:** all whitespace up to the next non-whitespace character is removed. That matches TOML and the earlier, more precise rule.

### C-12: Carriage returns in multiline basic strings
- **PRD FP-01, "Normal behavior":** a CRLF pair is "treated as a single line feed everywhere, including inside string values."
- **PRD FP-02, "Strings — four forms":** "Line endings inside a multiline basic string are kept exactly as written, carriage returns included."
- **Built:** CRLF is one line feed everywhere, including inside multiline strings (FP-01 and FP-03 agree). A lone carriage return that is not followed by a line feed is refused. The parser does not pre-rewrite the text, so error offsets refer to the caller's original string.

### C-13: Signed zero integers
- **PRD FP-02, "Integers":** "a signed zero is the integer 0."
- **PRD FP-02, Boundary:** "a zero with a sign (`+0`, `-0`)" is refused.
- **Built:** `+0` and `-0` are the integer 0. The positive rule is in the normal-behavior section, and TOML allows it.

### C-14: Separator in offset date-times
- **PRD Terminology, "Offset date-time":** "Its date and time are joined by `T` or `t`."
- **PRD FP-02, "Date-time values":** "The separator between date and time may be `T`, `t`, or a space."
- **Built:** a space separator is accepted for every date-time kind, including offset date-times (`1979-05-27 07:32Z`). The FP-02 rule applies to all date-time values and is the more specific statement. TOML 1.1 allows the space.

## Points the specification does not state

- **Nesting depth.** No limit is stated. Nested arrays and inline tables use the Python call stack. Nesting beyond about 300 levels (the exact limit depends on the interpreter's recursion limit) is refused with `TOMLDecodeError` ("value is nested too deeply") at the innermost value. A bare `RecursionError` is never raised. I did not change the recursion limit, because that is a process-wide side effect.
- **Invalid UTF-8.** `load` raises `UnicodeDecodeError` for bytes that are not valid UTF-8. That is a `ValueError` subclass but not a `TOMLDecodeError`, because there is no decoded text to report. The spec only covers valid UTF-8.
- **Byte-order mark.** A leading UTF-8 byte-order mark (U+FEFF) is not stripped. It is not valid TOML whitespace, so the document is refused.
- **Text-mode detection.** `load` refuses any `io.TextIOBase` before reading. For other objects it reads, and refuses if `read()` returns `str` rather than bytes or bytearray. `load` reads the whole file; it never takes a path.
- **Year 0000.** Years 0000–9999 are in the date grammar. Year 0000 cannot be represented by `datetime.date`, so it is refused as an invalid date.
- **Leap seconds.** The PRD says seconds must be 0–59, so `60` is refused.
- **UTC offset range.** Hours 0–23 and minutes 0–59. `-00:00` is accepted as zero offset.
- **Exponent case.** Floats accept `e` and `E` in the exponent. Other prefixes (`0x`, `0o`, `0b`) are lowercase only, as the PRD says.
- **Control characters in comments.** TOML forbids control characters other than tab in comments, so they are refused. Non-ASCII text is allowed.
- **DEL (U+007F).** Refused as a raw control character in strings and comments.
- **Error offsets.** The offset is the character at which parsing failed. At the end of the document it is `len(doc)`, which the report shows as "at end of document".
- **Contract wording: "hexadecimal digits written in lowercase."** This sentence is listed under integers. Integer values carry no digit case, so nothing is observable and nothing is done about it.
- **`parse_float` input for special spellings.** It receives the text as written (`+inf`, `-nan`). The default `float` is applied to the text with underscores removed. A custom converter receives the text unchanged, underscores included.
- **Converter errors.** Exceptions raised by `parse_float` itself propagate unchanged.
- **Duplicate-key detection through inline tables.** An inline table is frozen once it is written, as the PRD requires. A table defined with dotted keys inside an inline table cannot be extended from outside it.
- **Implicit super-tables.** A dotted key cannot walk through a table that was created implicitly by a header, because TOML says dotted keys only create tables that did not previously exist. A header can still define such a table later.
- **Tab in comments.** Allowed, as TOML permits.
