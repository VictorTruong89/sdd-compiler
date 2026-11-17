# Specification conflicts

1. **Trailing comma in arrays**
   - `spec/Full_PRD.md`, FP-01 Normal behavior: arrays "may ... end with a trailing comma".
   - `spec/Interface_Contract.md`, `loads` Return shape: "an array whose last element is followed by a comma is refused".
   - Why: the same array text cannot both be parsed into a list and be refused.

2. **Fraction of local time: truncate vs round**
   - `spec/Full_PRD.md`, FP-02 "Seconds and fractions": digits after the sixth are dropped, "truncated, not rounded".
   - `spec/Interface_Contract.md`, `loads` Return shape: local time has "its fraction rounded to the nearest microsecond".
   - Why: a fraction such as `.1234567` cannot give microsecond 123456 (truncated) and 123457 (rounded) at once.

3. **Empty keys**
   - `spec/Full_PRD.md`, FP-01: "A quoted key may be empty".
   - `spec/Interface_Contract.md`, `loads` Return shape: keys are `str`, "never empty".
   - Why: a document with `"" = 1` either yields an empty-string key or it cannot.

4. **Hex integers: case of digits**
   - `spec/Full_PRD.md`, FP-02 Integers: "hex digits may be either case".
   - `spec/Interface_Contract.md`, `loads` Return shape: integers have "hexadecimal digits written in lowercase".
   - Why: the PRD accepts uppercase hex digits, while the Contract limits the form to lowercase digits. Both cannot hold for `0xDEAD`.

5. **CRLF inside multiline basic strings**
   - `spec/Full_PRD.md`, FP-01 (last Normal bullet): CRLF is "a single line feed everywhere, including inside string values", so a multiline string holds line feeds only.
   - `spec/Full_PRD.md`, FP-02 Strings: "Line endings inside a multiline basic string are kept exactly as written, carriage returns included."
   - Why: a CRLF in a multiline basic string cannot be both reduced to LF and kept as CR+LF.

6. **First newline of a multiline literal string**
   - `spec/Full_PRD.md`, FP-02 Strings: a multiline literal string "keeps every character after its opening delimiter, including a first line feed".
   - Same section, next bullet: "In both multiline forms a line feed immediately after the opening delimiter is discarded".
   - Why: the first line feed of a multiline literal is both kept and discarded.

7. **Tab in a one-line string**
   - `spec/Full_PRD.md`, FP-02 Basic-string escapes: "A tab in a one-line string must be written as backslash-t."
   - Same file, FP-02 error list: only "raw control characters other than tab" are refused, so a raw tab is allowed in a string.
   - Why: a raw tab in a one-line string is either refused or allowed.

8. **Whitespace after a line-ending backslash**
   - `spec/Full_PRD.md`, FP-02 Strings: a line-ending backslash removes "all whitespace (spaces, tabs, line feeds) up to the next non-whitespace character".
   - Same section: "After a line-ending backslash, the next line's leading spaces and tabs are kept."
   - Why: the next line's leading spaces and tabs are both removed and kept.

9. **Quote before the closing delimiter of a multiline basic string**
   - `spec/Full_PRD.md`, FP-02 Strings: both multiline forms may contain one or two quote characters "directly before the closing delimiter, so that the value ends in one or two quote characters".
   - Same file, FP-02 error list: refused is "a quote character directly before the closing delimiter of a multiline basic string".
   - Why: for multiline basic strings, a quote before the closing delimiter is both valid and an error.

10. **Signed zero**
    - `spec/Full_PRD.md`, FP-02 Integers: "a signed zero is the integer 0".
    - Same file, FP-02 error list: "a zero with a sign (`+0`, `-0`)" is refused.
    - Why: `+0` is both accepted as 0 and refused.

11. **Sub-table of a dotted-key table via header**
    - `spec/Full_PRD.md`, Terminology (Dotted key): "A table created by dotted keys cannot receive a sub-table through a header."
    - Same file, FP-01 Normal behavior: after dotted keys have created a nested table, an undefined sub-table "may still be declared by a header".
    - Why: a header for a sub-table of a dotted-key table is both forbidden and permitted.

12. **Local time seconds**
    - `spec/Full_PRD.md`, Terminology (Local time): "Its seconds are always written".
    - Same file, FP-02 Seconds and fractions, and Non-goals: seconds may be omitted in any value with a time part.
    - Why: a local time without seconds is either invalid or valid.

13. **Date/time separator**
    - `spec/Full_PRD.md`, Terminology (Offset date-time): date and time "are joined by `T` or `t`".
    - Same file, FP-02 Date-time values: the separator "may be `T`, `t`, or a space".
    - Why: an offset date-time with a space separator is either accepted or not.

14. **Which float-converter results are refused**
    - `spec/Full_PRD.md`, Terminology (Float converter): "Only a result whose type is exactly `dict` or exactly `list` is refused."
    - Same file, FP-05 (and `spec/Interface_Contract.md`, `loads` Failures): subclass instances of dict or list are also refused.
    - Why: a `dict` subclass instance is both allowed and refused.
