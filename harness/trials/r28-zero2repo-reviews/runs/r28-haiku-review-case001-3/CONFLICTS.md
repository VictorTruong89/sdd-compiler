# Specification conflicts

Files: `PRD` = `spec/Full_PRD.md`, `IC` = `spec/Interface_Contract.md`, `HW` = `spec/Hardware_Requirements.md`.

## 1. Whether local time seconds may be omitted

- **Side A (PRD, Terminology, "Local time"):** "A TOML clock time with no date. Constructed as a time. Its seconds are always written."
- **Side B (PRD, FP-02, Normal behavior, "Seconds and fractions"):** "In any value with a time part, seconds may be omitted, in which case the second is 0."
- **Why they cannot both hold:** A local time written as `07:32` has a time part and omits its seconds, which Side A forbids and Side B permits.

## 2. Truncating or rounding the fractional second

- **Side A (PRD, FP-02, Normal behavior, "Seconds and fractions"):** "any digits after the sixth are dropped (truncated, not rounded)."
- **Side B (IC, `tomlparse.loads`, Return shape):** "local time: `datetime.time` with `tzinfo` `None`, its fraction rounded to the nearest microsecond."
- **Why they cannot both hold:** For a local time `07:32:00.1234567`, truncation gives microsecond 123456 and rounding gives 123457, so the two rules produce different values for the same input.

## 3. Trailing comma in arrays

- **Side A (PRD, FP-01, Normal behavior):** "Arrays are sequences in document order. They may be empty, mix value types, nest, span lines, contain comments between elements, and end with a trailing comma."
- **Side B (IC, `tomlparse.loads`, Return shape):** "arrays and arrays of tables: `list`, elements in document order; an array whose last element is followed by a comma is refused;"
- **Why they cannot both hold:** The document `a = [1,]` must be accepted under Side A and refused under Side B.

## 4. Which converter results are refused: exact types or subclasses

- **Side A (PRD, Terminology, "Float converter"):** "Only a result whose type is exactly `dict` or exactly `list` is refused."
- **Side B (PRD, FP-05, Normal behavior and Boundary):** a value "that is not a dictionary or a list (and not an instance of a subclass of either) is allowed"; "If the converter returns a dictionary or a list (or an instance of a subclass of either) ... the parse fails."
- **Why they cannot both hold:** A converter that returns a `dict` subclass instance is accepted under Side A's exact-type rule and refused under Side B's subclass rule.

## 5. Declaring a header-defined sub-table under a dotted-key table

- **Side A (PRD, Terminology, "Dotted key"):** "A table created by dotted keys cannot receive a sub-table through a header."
- **Side B (PRD, FP-01, Normal behavior, "A table header creates any missing parent tables" bullet):** "After dotted keys have created a nested table, a sub-table of it that has not itself been defined may still be declared by a header, as TOML v1.1.0 allows."
- **Why they cannot both hold:** For `a.b.c = 1` followed by `[a.b.d]`, Side A forbids the header and Side B permits it.

## 6. Adding further dotted keys to a table created by dotted keys

- **Side A (PRD, FP-01, Normal behavior, "Dotted keys and dotted table headers" bullet):** "A table created implicitly by dotted keys may receive further dotted keys under the same prefix."
- **Side B (PRD, FP-01, Boundary behavior):** refused: "reopening a table already defined by a header, or by dotted keys, through a later header or later dotted keys."
- **Why they cannot both hold:** For `a.b.x = 1` followed by `a.b.y = 2`, Side A requires acceptance and Side B, which refuses reopening a table defined by dotted keys through later dotted keys, requires refusal.

## 7. Whether a quoted key may be empty

- **Side A (PRD, FP-01, Normal behavior, "Keys" bullets):** "A quoted key may be empty and may contain any character TOML allows."
- **Side B (IC, `tomlparse.loads`, Return shape):** "keys: `str`, never empty;"
- **Why they cannot both hold:** The document `"" = 1` produces a key that Side A permits and Side B forbids.

## 8. Date and time separator in offset date-times

- **Side A (PRD, Terminology, "Offset date-time"):** "Its date and time are joined by `T` or `t`."
- **Side B (PRD, FP-02, Normal behavior, "Date-time values"):** "The separator between date and time may be `T`, `t`, or a space."
- **Why they cannot both hold:** The offset date-time `1979-05-27 07:32:00Z` is required to be refused by Side A and is permitted by Side B.

## 9. Signed zero integers

- **Side A (PRD, FP-02, Normal behavior, "Integers"):** "Decimal integers (optionally signed; a signed zero is the integer 0)".
- **Side B (PRD, FP-02, Boundary behavior):** refused: "a zero with a sign (`+0`, `-0`)".
- **Why they cannot both hold:** The token `-0` is required to produce the integer 0 by Side A and to be refused by Side B.

## 10. Raw tab characters in one-line strings

- **Side A (PRD, FP-02, Normal behavior, "Basic-string escapes"):** "A tab in a one-line string must be written as backslash-t."
- **Side B (PRD, FP-02, Boundary behavior):** refused: "raw control characters other than tab inside any string form", which implies a raw tab is not refused.
- **Why they cannot both hold:** A raw tab inside `"a<TAB>b"` must be refused under Side A and must not be refused under Side B's exception for tab.

## 11. Carriage returns inside multiline basic strings

- **Side A (PRD, FP-01, Normal behavior, last bullet):** "A carriage-return/line-feed pair in the input is treated as a single line feed everywhere, including inside string values: a multiline string written with carriage-return/line-feed line endings holds line feeds only."
- **Side B (PRD, FP-02, Normal behavior, second multiline bullet):** "Line endings inside a multiline basic string are kept exactly as written, carriage returns included."
- **Why they cannot both hold:** A multiline basic string written with CRLF line endings must contain only line feeds under Side A and must contain carriage returns under Side B.

## 12. Discarding the first line feed of multiline strings

- **Side A (PRD, FP-02, Normal behavior, second multiline bullet):** "In both multiline forms a line feed immediately after the opening delimiter is discarded; later line feeds are kept."
- **Side B (PRD, FP-02, Normal behavior, first bullet on strings):** "A multiline literal string keeps every character after its opening delimiter, including a first line feed."
- **Why they cannot both hold:** For `'''<LF>x'''` Side A yields `x` and Side B yields `\nx`, and both statements apply to multiline literal strings.

## 13. Whitespace after a line-ending backslash

- **Side A (PRD, FP-02, Normal behavior, multiline basic string bullet):** "a backslash that is the last non-whitespace character on a line removes the line ending and all whitespace (spaces, tabs, line feeds) up to the next non-whitespace character or the closing delimiter."
- **Side B (PRD, FP-02, Normal behavior, last multiline bullet):** "After a line-ending backslash, the next line's leading spaces and tabs are kept."
- **Why they cannot both hold:** For `"""a\<LF>   b"""` Side A yields `ab` with the leading spaces removed and Side B yields `a   b` with them kept.

## 14. Quote characters directly before the closing delimiter of multiline basic strings

- **Side A (PRD, FP-02, Normal behavior, last multiline bullet):** "Both multiline forms may contain one or two of their own quote characters next to each other, including directly before the closing delimiter, so that the value ends in one or two quote characters."
- **Side B (PRD, FP-02, Boundary behavior):** refused: "a quote character directly before the closing delimiter of a multiline basic string".
- **Why they cannot both hold:** The document `"""a""""` (a value ending in one quote) is accepted under Side A and refused under Side B.
