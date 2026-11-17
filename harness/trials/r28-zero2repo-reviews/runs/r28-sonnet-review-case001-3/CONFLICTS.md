# Specification conflicts

1. **Trailing comma in arrays**
   - `spec/Full_PRD.md`, FP-01: arrays "may ... end with a trailing comma".
   - `spec/Interface_Contract.md`, `loads` Return shape: "an array whose last element is followed by a comma is refused".
   - The same array with a trailing comma cannot both parse and be refused.

2. **Fraction of a local time: truncated or rounded**
   - `spec/Full_PRD.md`, FP-02 Seconds and fractions: digits after the sixth are dropped, "truncated, not rounded".
   - `spec/Interface_Contract.md`, `loads` Return shape: local time has "its fraction rounded to the nearest microsecond".
   - A fraction with 7 or more digits (e.g. `.1234567`) cannot be both truncated and rounded.

3. **Empty keys**
   - `spec/Full_PRD.md`, FP-01: "A quoted key may be empty".
   - `spec/Interface_Contract.md`, `loads` Return shape: keys are "`str`, never empty".
   - A document containing `"" = 1` cannot both produce an empty key and never produce one.

4. **Case of hexadecimal digits**
   - `spec/Full_PRD.md`, FP-02 Integers: "hex digits may be either case"; Basic-string escapes: "Hex digits are case-insensitive".
   - `spec/Interface_Contract.md`, `loads` Return shape: "hexadecimal digits written in lowercase".
   - The Contract restricts the written hex digits to lowercase, while the PRD accepts both cases.

5. **Uppercase hex digits in escapes**
   - `spec/Full_PRD.md`, FP-02 Basic-string escapes: "Hex digits are case-insensitive" for `\x`, `\u`, `\U`.
   - `spec/Full_PRD.md`, FP-02 Boundary: refused are "escape digits written as uppercase letters".
   - `\u00E9` cannot be both accepted and refused.

6. **Signed zero**
   - `spec/Full_PRD.md`, FP-02 Integers: "a signed zero is the integer 0".
   - `spec/Full_PRD.md`, FP-02 Boundary: refused is "a zero with a sign (`+0`, `-0`)".
   - `+0` cannot be both the integer 0 and an error.

7. **Carriage returns inside multiline basic strings**
   - `spec/Full_PRD.md`, FP-01: CRLF "is treated as a single line feed everywhere, including inside string values ... holds line feeds only".
   - `spec/Full_PRD.md`, FP-02 Strings: "Line endings inside a multiline basic string are kept exactly as written, carriage returns included."
   - A CRLF inside a multiline basic string cannot both become LF and stay CRLF.

8. **First line feed of a multiline literal string**
   - `spec/Full_PRD.md`, FP-02 Strings: a multiline literal string "keeps every character after its opening delimiter, including a first line feed".
   - `spec/Full_PRD.md`, FP-02 Strings: "In both multiline forms a line feed immediately after the opening delimiter is discarded".
   - The first line feed of a multiline literal string cannot be both kept and discarded.

9. **Whitespace after a line-ending backslash**
   - `spec/Full_PRD.md`, FP-02 Strings: a line-ending backslash removes the line ending "and all whitespace (spaces, tabs, line feeds) up to the next non-whitespace character".
   - `spec/Full_PRD.md`, FP-02 Strings: "After a line-ending backslash, the next line's leading spaces and tabs are kept."
   - The next line's leading spaces and tabs cannot be both removed and kept.

10. **Quote directly before the closing delimiter of a multiline basic string**
    - `spec/Full_PRD.md`, FP-02 Strings: both multiline forms may contain one or two quote characters "directly before the closing delimiter, so that the value ends in one or two quote characters".
    - `spec/Full_PRD.md`, FP-02 Boundary: refused is "a quote character directly before the closing delimiter of a multiline basic string".
    - `"""a""""` cannot be both accepted and refused.

11. **Tab in a one-line string**
    - `spec/Full_PRD.md`, FP-02 Basic-string escapes: "A tab in a one-line string must be written as backslash-t".
    - `spec/Full_PRD.md`, FP-02 Boundary: refused are "raw control characters other than tab inside any string form", so a raw tab is allowed.
    - A raw tab in a one-line string cannot be both forbidden and allowed.

12. **Sub-tables of tables created by dotted keys**
    - `spec/Full_PRD.md`, Terminology (Dotted key): "A table created by dotted keys cannot receive a sub-table through a header."
    - `spec/Full_PRD.md`, FP-01: "After dotted keys have created a nested table, a sub-table of it that has not itself been defined may still be declared by a header".
    - A header declaring a sub-table of a dotted-key table cannot be both refused and accepted.

13. **Further dotted keys under a dotted-key table**
    - `spec/Full_PRD.md`, FP-01 Normal: "A table created implicitly by dotted keys may receive further dotted keys under the same prefix."
    - `spec/Full_PRD.md`, FP-01 Boundary: refused is "reopening a table already defined ... by dotted keys, through a later header or later dotted keys".
    - Later dotted keys into a dotted-key table cannot be both allowed and a refused reopening.

14. **Seconds in local times**
    - `spec/Full_PRD.md`, Terminology (Local time): "Its seconds are always written."
    - `spec/Full_PRD.md`, FP-02 Seconds and fractions: "In any value with a time part, seconds may be omitted"; Non-goals also say v1.1.0 allows omitted seconds.
    - A local time such as `07:32` cannot both be invalid and be valid.

15. **Date/time separator**
    - `spec/Full_PRD.md`, Terminology (Offset date-time): date and time "are joined by `T` or `t`".
    - `spec/Full_PRD.md`, FP-02 Date-time values: "The separator between date and time may be `T`, `t`, or a space."
    - An offset date-time with a space separator cannot both be accepted and not.

16. **Which converter results are refused**
    - `spec/Full_PRD.md`, Terminology (Float converter): "Only a result whose type is exactly `dict` or exactly `list` is refused."
    - `spec/Full_PRD.md`, FP-05 (and `spec/Interface_Contract.md`, Failures tables): results that are dict/list subclass instances are also refused.
    - A `dict` subclass instance returned by the converter cannot be both allowed and refused.
