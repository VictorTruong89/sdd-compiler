# Specification conflicts

Files: `PRD` = `spec/Full_PRD.md`, `IC` = `spec/Interface_Contract.md`, `HW` = `spec/Hardware_Requirements.md`.

## 1. Empty quoted keys vs. "keys never empty"

- **PRD, FP-01, Normal behavior (keys bullet):** "A quoted key may be empty."
- **IC, `tomlparse.loads`, Return shape:** "keys: `str`, never empty".
- **Why they cannot both hold:** a document containing `"" = 1` must either yield a key that is the empty string (violating "never empty") or be rejected/handled differently (violating "may be empty").

## 2. Sub-table under a dotted-key table: forbidden vs. allowed

- **PRD, Terminology, "Dotted key":** "A table created by dotted keys cannot receive a sub-table through a header."
- **PRD, FP-01, Normal behavior (table header bullet):** "After dotted keys have created a nested table, a sub-table of it that has not itself been defined may still be declared by a header, as TOML v1.1.0 allows."
- **Why they cannot both hold:** for `a.b.c = 1` followed by `[a.b.d]`, the first says the header is not allowed to add a sub-table of the dotted-key table `a.b`, and the second says it is allowed.

## 3. Offset date-time separator: only T/t vs. space also allowed

- **PRD, Terminology, "Offset date-time":** "Its date and time are joined by `T` or `t`."
- **PRD, FP-02, Date-time values:** "The separator between date and time may be `T`, `t`, or a space." (no exception for offset date-times)
- **Why they cannot both hold:** `1979-05-27 07:32:00Z` is either an offset date-time (which must use T/t only) or a valid value (space allowed), not both.

## 4. Local time: seconds always written vs. seconds may be omitted

- **PRD, Terminology, "Local time":** "Its seconds are always written."
- **PRD, FP-02, Seconds and fractions:** "In any value with a time part, seconds may be omitted, in which case the second is 0."
- **Why they cannot both hold:** a local time such as `07:32` has a time part, so the FP-02 rule permits omitting its seconds while the Terminology rule forbids it.

## 5. Fractional seconds: truncated vs. rounded

- **PRD, FP-02, Seconds and fractions:** digits after the sixth "are dropped (truncated, not rounded)."
- **IC, `tomlparse.loads`, Return shape (local time):** "its fraction rounded to the nearest microsecond."
- **Why they cannot both hold:** for `07:32:00.1234567`, truncation yields microsecond 123456 and rounding yields 123457.

## 6. Multiline literal string: leading line feed kept vs. discarded

- **PRD, FP-02, Strings, first bullet:** "A multiline literal string keeps every character after its opening delimiter, including a first line feed."
- **PRD, FP-02, Strings, second bullet:** "In both multiline forms a line feed immediately after the opening delimiter is discarded."
- **Why they cannot both hold:** for `'''\nabc'''` the first says the value starts with a line feed, the second says that line feed is removed.

## 7. CRLF inside multiline strings: kept vs. normalized to LF

- **PRD, FP-02, Strings, second bullet:** "Line endings inside a multiline basic string are kept exactly as written, carriage returns included."
- **PRD, FP-01, Normal behavior (last bullet):** a CRLF pair "is treated as a single line feed everywhere, including inside string values: a multiline string written with carriage-return/line-feed line endings holds line feeds only."
- **Why they cannot both hold:** a multiline basic string written with CRLF line endings must either contain `\r\n` (FP-02) or contain only `\n` (FP-01).

## 8. Raw tab in a one-line string: forbidden vs. allowed

- **PRD, FP-02, Strings:** "A tab in a one-line string must be written as backslash-t."
- **PRD, FP-02, Boundary/error behavior:** refused are "raw control characters **other than tab** inside any string form."
- **Why they cannot both hold:** the Strings rule requires a raw tab in a one-line string to be refused (it must be written as `\t`), while the Boundary rule exempts tab from refusal, so a raw tab in a one-line string is both required to fail and not required to fail.

## 9. Quote directly before the closing delimiter of a multiline basic string: allowed vs. refused

- **PRD, FP-02, Strings, fourth bullet:** "Both multiline forms may contain one or two of their own quote characters ... including directly before the closing delimiter, so that the value ends in one or two quote characters."
- **PRD, FP-02, Boundary/error behavior:** refused is "a quote character directly before the closing delimiter of a multiline basic string."
- **Why they cannot both hold:** `"""a""""` (quote directly before the closing delimiter in a multiline basic string) is either a valid string per the first statement or a refused document per the second.

## 10. Signed zero: valid integer vs. refused

- **PRD, FP-02, Integers:** "Decimal integers (optionally signed; a signed zero is the integer 0)."
- **PRD, FP-02, Boundary/error behavior:** refused is "a zero with a sign (`+0`, `-0`)."
- **Why they cannot both hold:** `+0` and `-0` are either accepted as the integer 0 or refused, not both.

## 11. Trailing comma in arrays: accepted vs. refused

- **PRD, FP-01, Normal behavior (arrays bullet):** arrays "may be empty, mix value types, nest, span lines, contain comments between elements, and end with a trailing comma."
- **IC, `tomlparse.loads`, Return shape:** "an array whose last element is followed by a comma is refused."
- **Why they cannot both hold:** `a = [1, 2,]` is accepted by the PRD and refused by the Interface Contract.

## 12. Float converter result: exact `dict`/`list` vs. subclasses also refused

- **PRD, Terminology, "Float converter":** "Only a result whose type is exactly `dict` or exactly `list` is refused."
- **PRD, FP-05, Normal behavior:** a result "that is not a dictionary or a list (and not an instance of a subclass of either) is allowed," i.e. subclass instances are not allowed.
- **IC, `tomlparse.loads` / `load`, Failures:** "`parse_float` returned a `dict` or `list` (or a subclass instance)" raises `ValueError`.
- **Why they cannot both hold:** a converter returning an instance of a `dict` subclass is accepted under the Terminology rule (not exactly `dict`) and refused under FP-05 and the Interface Contract.
