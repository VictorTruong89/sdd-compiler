# Specification conflicts

Abbreviations: PRD = spec/Full_PRD.md, IC = spec/Interface_Contract.md.

## 1. Trailing comma in arrays
- PRD, FP-01 Normal behavior: arrays "may ... end with a trailing comma".
- IC, `loads` Return shape: "an array whose last element is followed by a comma is refused".
- The same array text cannot be both accepted and refused.

## 2. Fractional seconds: truncate vs. round
- PRD, FP-02 "Seconds and fractions": digits after the sixth are "dropped (truncated, not rounded)".
- IC, `loads` Return shape (local time): "its fraction rounded to the nearest microsecond".
- A fraction such as `.1234567` gives microsecond 123456 if truncated and 123457 if rounded.

## 3. Empty keys
- PRD, FP-01 Normal behavior: "A quoted key may be empty".
- IC, `loads` Return shape: keys are "`str`, never empty".
- `"" = 1` either yields an empty-string key or it cannot.

## 4. Hexadecimal digit case
- PRD, FP-02 Integers: "hex digits may be either case".
- IC, `loads` Return shape: integers are "hexadecimal digits written in lowercase".
- Hex integers are either accepted in both cases or only in lowercase.

## 5. Line endings inside multiline basic strings
- PRD, FP-01 Normal behavior: CRLF is "treated as a single line feed everywhere, including inside string values: a multiline string written with CRLF line endings holds line feeds only".
- PRD, FP-02 Strings: "Line endings inside a multiline basic string are kept exactly as written, carriage returns included".
- A CRLF inside a multiline basic string cannot both become a bare LF and be kept as CR+LF.

## 6. First line feed of a multiline literal string
- PRD, FP-02 Strings: a multiline literal string "keeps every character after its opening delimiter, including a first line feed".
- PRD, FP-02 Strings (next bullet): "In both multiline forms a line feed immediately after the opening delimiter is discarded".
- The first line feed after `'''` is either kept or discarded.

## 7. Whitespace after a line-ending backslash
- PRD, FP-02 Strings: a line-ending backslash removes the line ending and "all whitespace (spaces, tabs, line feeds) up to the next non-whitespace character".
- PRD, FP-02 Strings: "After a line-ending backslash, the next line's leading spaces and tabs are kept."
- The next line's leading spaces and tabs are either removed or kept.

## 8. Quote directly before the closing delimiter of a multiline basic string
- PRD, FP-02 Strings: both multiline forms may contain one or two quote characters "including directly before the closing delimiter, so that the value ends in one or two quote characters".
- PRD, FP-02 Boundary: refused is "a quote character directly before the closing delimiter of a multiline basic string".
- A multiline basic string ending in `""""` + `"""` is either valid or refused.

## 9. Raw tab in a one-line string
- PRD, FP-02 Basic-string escapes: "A tab in a one-line string must be written as backslash-t".
- PRD, FP-02 Boundary: refused are "raw control characters other than tab inside any string form", so a raw tab is allowed.
- A raw tab in a one-line string is either refused or accepted.

## 10. Uppercase hex digits in escapes
- PRD, FP-02 Basic-string escapes: "Hex digits are case-insensitive" for `\x`, `\u`, `\U`.
- PRD, FP-02 Boundary: refused are "escape digits written as uppercase letters".
- `"é"` is either valid or refused.

## 11. Signed zero
- PRD, FP-02 Integers: "a signed zero is the integer 0".
- PRD, FP-02 Boundary: refused is "a zero with a sign (`+0`, `-0`)".
- `+0` is either accepted as 0 or refused.

## 12. Date/time separator for offset date-times
- PRD, Terminology (Offset date-time): "Its date and time are joined by `T` or `t`".
- PRD, FP-02 Date-time values: "The separator between date and time may be `T`, `t`, or a space".
- An offset date-time with a space separator is either valid or invalid.

## 13. Seconds in local times
- PRD, Terminology (Local time): "Its seconds are always written".
- PRD, FP-02 Seconds and fractions: "In any value with a time part, seconds may be omitted"; Non-goals also accept date-times with seconds omitted.
- A local time like `07:32` is either valid or invalid.

## 14. Sub-tables of a table created by dotted keys
- PRD, Terminology (Dotted key): "A table created by dotted keys cannot receive a sub-table through a header."
- PRD, FP-01 Normal behavior: "After dotted keys have created a nested table, a sub-table of it that has not itself been defined may still be declared by a header".
- A header such as `[a.b.c]` after `a.b.x = 1` is either refused or accepted.

## 15. Extending a table made by dotted keys
- PRD, FP-01 Normal behavior: "A table created implicitly by dotted keys may receive further dotted keys under the same prefix".
- PRD, FP-01 Boundary: refused is "reopening a table already defined ... by dotted keys, through ... later dotted keys".
- A later dotted key into a table already created by dotted keys is either allowed or refused.

## 16. Which converter results are refused
- PRD, Terminology (Float converter): "Only a result whose type is exactly `dict` or exactly `list` is refused."
- PRD, FP-05 and IC (`loads`/`load` Failures): a `dict` or `list` "or a subclass instance" is refused.
- A converter returning a `dict` subclass instance is either accepted or refused.
