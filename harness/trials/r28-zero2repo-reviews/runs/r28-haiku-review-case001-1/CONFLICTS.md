# Specification conflicts

Files reviewed: `spec/Full_PRD.md` (PRD), `spec/Interface_Contract.md` (Contract), `spec/Hardware_Requirements.md` (Hardware). Line numbers refer to the files as they currently stand.

## C-01: Local time seconds

- **Side A:** PRD, Terminology table, "Local time" row (line 28): "Its seconds are always written."
- **Side B:** PRD, FP-02 "Seconds and fractions" (line 116): "In any value with a time part, seconds may be omitted, in which case the second is 0." PRD Non-goals (line 64) also accepts "date-times whose seconds are omitted."
- **Why they conflict:** A local time written as `07:32` either must have its seconds written (A) or may omit them (B), and both cannot hold for that input.

## C-02: Rounding of fractional seconds in local times

- **Side A:** PRD, FP-02 "Seconds and fractions" (line 116): the fraction is read as microseconds and "any digits after the sixth are dropped (truncated, not rounded)."
- **Side B:** Contract, `tomlparse.loads` "Return shape" (line 46): local time is "`datetime.time` with `tzinfo` `None`, its fraction rounded to the nearest microsecond."
- **Why they conflict:** For a fraction such as `.1234567`, truncation gives microsecond 123456 while rounding gives 123457, so the two cannot both be the value returned.

## C-03: Trailing comma in arrays

- **Side A:** PRD, FP-01 "Normal behavior" (line 89): arrays "may be empty, mix value types, nest, span lines, contain comments between elements, and end with a trailing comma."
- **Side B:** Contract, `tomlparse.loads` "Return shape" (line 40): "an array whose last element is followed by a comma is refused."
- **Why they conflict:** An array `[1, 2,]` is either accepted as a sequence (A) or refused (B), and both cannot hold.

## C-04: Which float-converter results are refused

- **Side A:** PRD, Terminology, "Float converter" (line 29): "Only a result whose type is exactly `dict` or exactly `list` is refused."
- **Side B:** PRD, FP-05 "Boundary / error behavior" (line 183) and Contract, `loads` Failures table (line 56) and `load` Failures table (line 81): a result that is a `dict` or `list` "(or an instance of a subclass of either)" is refused.
- **Why they conflict:** A `dict` subclass returned by the converter must either raise the value error (B) or be bound as returned (A), and both cannot hold.

## C-05: Sub-tables under a table created by dotted keys

- **Side A:** PRD, Terminology, "Dotted key" (line 23): "A table created by dotted keys cannot receive a sub-table through a header."
- **Side B:** PRD, FP-01 "Normal behavior" (line 86): "After dotted keys have created a nested table, a sub-table of it that has not itself been defined may still be declared by a header, as TOML v1.1.0 allows."
- **Why they conflict:** For `a.b = 1` followed by `[a.b.c]`, one statement forbids the header and the other requires it to be accepted.

## C-06: Keys may be empty

- **Side A:** Contract, `tomlparse.loads` "Return shape" (line 38): keys are `str`, "never empty."
- **Side B:** PRD, FP-01 "Normal behavior" (line 84): "A quoted key may be empty."
- **Why they conflict:** A document with key `"" = 1` must either produce an empty-string key, which the Contract forbids, or be accepted as the PRD requires, and both cannot hold.

## C-07: Quote characters directly before the closing delimiter of a multiline basic string

- **Side A:** PRD, FP-02 "Strings — four forms" (line 111): both multiline forms "may contain one or two of their own quote characters next to each other, including directly before the closing delimiter."
- **Side B:** PRD, FP-02 "Boundary / error behavior" (line 127): refused: "a quote character directly before the closing delimiter of a multiline basic string."
- **Why they conflict:** A value such as `"""a""""` (a quote directly before the closing delimiter) is declared valid by A and refused by B.

## C-08: Leading line feed in multiline literal strings

- **Side A:** PRD, FP-02 "Strings — four forms" (line 108): "A multiline literal string keeps every character after its opening delimiter, including a first line feed."
- **Side B:** PRD, FP-02 "Strings — four forms" (line 109): "In both multiline forms a line feed immediately after the opening delimiter is discarded."
- **Why they conflict:** For `'''` followed by a newline and text, A keeps the first line feed and B discards it, and the value cannot be both.

## C-09: Raw tab characters in one-line strings

- **Side A:** PRD, FP-02 "Basic-string escapes" (line 112): "A tab in a one-line string must be written as backslash-t."
- **Side B:** PRD, FP-02 "Boundary / error behavior" (line 126): the refused raw control characters are those "other than tab inside any string form."
- **Why they conflict:** A raw tab inside a basic string is invalid under A but is not refused under B, so the two disagree on whether such a document fails.

## C-10: Case of hex digits in `\x`, `\u`, `\U` escapes

- **Side A:** PRD, FP-02 "Basic-string escapes" (line 112): "Hex digits are case-insensitive."
- **Side B:** PRD, FP-02 "Boundary / error behavior" (line 126): refused: "escape digits written as uppercase letters."
- **Why they conflict:** A document containing `"é"` is accepted by A and refused by B.

## C-11: Whitespace kept or removed after a line-ending backslash

- **Side A:** PRD, FP-02 "Strings — four forms" (line 110): a line-ending backslash "removes the line ending and all whitespace (spaces, tabs, line feeds) up to the next non-whitespace character or the closing delimiter."
- **Side B:** PRD, FP-02 "Strings — four forms" (line 111): "After a line-ending backslash, the next line's leading spaces and tabs are kept."
- **Why they conflict:** For a continuation line that begins with spaces, A says those spaces are removed and B says they are kept, and the value cannot be both.

## C-12: Carriage returns in multiline basic strings

- **Side A:** PRD, FP-01 "Normal behavior" (line 92): a CRLF pair is "treated as a single line feed everywhere, including inside string values: a multiline string written with carriage-return/line-feed line endings holds line feeds only."
- **Side B:** PRD, FP-02 "Strings — four forms" (line 109): "Line endings inside a multiline basic string are kept exactly as written, carriage returns included."
- **Why they conflict:** A multiline basic string written with CRLF line endings either contains only line feeds (A) or contains carriage returns (B).

## C-13: Signed zero integers

- **Side A:** PRD, FP-02 "Integers" (line 113): "Decimal integers (optionally signed; a signed zero is the integer 0)."
- **Side B:** PRD, FP-02 "Boundary / error behavior" (line 124): refused: "a zero with a sign (`+0`, `-0`)."
- **Why they conflict:** The token `-0` is accepted as the integer 0 by A and refused by B.

## C-14: Separator in offset date-times

- **Side A:** PRD, Terminology, "Offset date-time" (line 25): "Its date and time are joined by `T` or `t`."
- **Side B:** PRD, FP-02 "Date-time values" (line 115): "The separator between date and time may be `T`, `t`, or a space."
- **Why they conflict:** A defines an offset date-time as one joined by `T` or `t`, so `1979-05-27 07:32:00Z` is not one under A, while B's rule that any date-time may use a space separator, together with its `Z` suffix, makes it one, so the two classify the same value differently.
