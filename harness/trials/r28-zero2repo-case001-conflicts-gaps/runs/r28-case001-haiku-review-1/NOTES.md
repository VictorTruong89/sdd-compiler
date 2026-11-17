# Implementation notes

Tomlparse 2.4.0: a pure-Python TOML v1.1.0 parser. Package: `src/tomlparse/`
(`__init__.py` exports `loads`, `load`, `TOMLDecodeError`; `_parser.py` is the parser;
`_errors.py` holds the exception). No runtime dependencies. Nothing under `spec/` was changed.

Scope: the spec sections read were `spec/Full_PRD.md`, `spec/Interface_Contract.md`,
`spec/Hardware_Requirements.md`, and `spec/CONFLICTS.md` (a reviewer list, used only as a
pointer; each conflict below was checked against the quoted spec text).

## Conflicts between the spec files

Each entry gives both sides (file and location), then the behaviour built.

### C-01 Local time seconds
- **PRD, Terminology, "Local time" row:** "Its seconds are always written."
- **PRD, FP-02 "Seconds and fractions":** "In any value with a time part, seconds may be omitted, in which case the second is 0." PRD Non-goals also accepts "date-times whose seconds are omitted."
- **Built:** seconds optional (`07:32` is a local time at 07:32:00). The FP-02 rule and the Non-goals text both state this; the Terminology row predates it.

### C-02 Rounding of fractional seconds
- **PRD, FP-02 "Seconds and fractions":** the first six fraction digits are microseconds; "any digits after the sixth are dropped (truncated, not rounded)."
- **Contract, `loads` Return shape:** local time's fraction is "rounded to the nearest microsecond."
- **Built:** truncation, everywhere (local time included). The PRD rule is the detailed one and says "any value with a time part"; it also matches TOML's own behaviour.

### C-03 Trailing comma in arrays
- **PRD, FP-01 "Normal behavior":** arrays "end with a trailing comma" (accepted).
- **Contract, `loads` Return shape:** "an array whose last element is followed by a comma is refused."
- **Built:** accepted, `[1, 2,]` == `[1, 2]`. TOML allows it, and the Contract line reads as a stray sentence contradicting its own table.

### C-04 Which float-converter results are refused
- **PRD Terminology:** "Only a result whose type is exactly `dict` or exactly `list` is refused."
- **PRD FP-05 Boundary, Contract `loads` and `load` Failures tables:** a `dict` or `list` "(or an instance of a subclass of either)" is refused.
- **Built:** `isinstance` check, so subclasses are refused with `ValueError` (not `TOMLDecodeError`). Three documents say this, so it wins over the Terminology row.

### C-05 Sub-tables under a table created by dotted keys
- **PRD Terminology, "Dotted key":** "A table created by dotted keys cannot receive a sub-table through a header."
- **PRD FP-01 "Normal behavior":** "After dotted keys have created a nested table, a sub-table of it that has not itself been defined may still be declared by a header."
- **Built:** the FP-01 rule. For `a.b = 1` then `[a.b.c]`, the header is refused (`a.b` is an integer). For `a.b.x = 1` then `[a.b.c]`, the header is accepted. A header naming a table already defined by dotted keys (e.g. `[a.b]` after `a.b.x = 1`) is refused, as FP-01 requires for reopening.

### C-06 Empty keys
- **Contract, `loads` Return shape:** keys are `str`, "never empty."
- **PRD FP-01 "Normal behavior":** "A quoted key may be empty."
- **Built:** `"" = 1` is accepted and produces the key `""`. Only quoted keys can be empty; a bare key needs at least one character.

### C-07 Quote characters before a multiline closing delimiter
- **PRD FP-02 "Strings — four forms":** both multiline forms may contain one or two quotes directly before the closing delimiter.
- **PRD FP-02 Boundary:** refused: "a quote character directly before the closing delimiter of a multiline basic string."
- **Built:** the first (accepted), as TOML does. A run of 3 to 5 quotes closes the string, and the first `run-3` quotes are content. A run of 6 or more is refused. The same rule applies to multiline literal strings.

### C-08 Leading line feed in multiline literal strings
- **PRD FP-02 "Strings — four forms", literal-string bullet:** "keeps every character after its opening delimiter, including a first line feed."
- **PRD FP-02 "Strings — four forms", next bullet:** "In both multiline forms a line feed immediately after the opening delimiter is discarded."
- **Built:** discarded, for both multiline forms (the second statement is the TOML rule).

### C-09 Raw tab in one-line strings
- **PRD FP-02 "Basic-string escapes":** "A tab in a one-line string must be written as backslash-t."
- **PRD FP-02 Boundary:** refused control characters are those "other than tab inside any string form."
- **Built:** a raw tab is accepted in every string form (TOML permits it, and only the Boundary text is a refusal rule). `\t` still works.

### C-10 Case of hex digits in `\x`, `\u`, `\U`
- **PRD FP-02 "Basic-string escapes":** "Hex digits are case-insensitive."
- **PRD FP-02 Boundary:** refused: "escape digits written as uppercase letters."
- **Built:** case-insensitive. `"é"` is `é`. TOML's ABNF is case-insensitive for hex digits.

### C-11 Whitespace after a line-ending backslash
- **PRD FP-02 "Strings — four forms", first multiline bullet:** the backslash "removes the line ending and all whitespace (spaces, tabs, line feeds) up to the next non-whitespace character or the closing delimiter."
- **PRD FP-02, following bullet:** "After a line-ending backslash, the next line's leading spaces and tabs are kept."
- **Built:** the first statement (whitespace removed), as TOML says. The second contradicts the first and the TOML rule.

### C-12 Carriage returns in multiline basic strings
- **PRD FP-01 "Normal behavior":** a CRLF pair is "treated as a single line feed everywhere, including inside string values."
- **PRD FP-02 "Strings — four forms":** "Line endings inside a multiline basic string are kept exactly as written, carriage returns included."
- **Built:** CRLF becomes LF in every string form, as FP-01 says globally (and FP-03 repeats). A bare CR is refused. Since the FP-01 rule is global, it wins over the FP-02 bullet.

### C-13 Signed zero integers
- **PRD FP-02 "Integers":** "a signed zero is the integer 0."
- **PRD FP-02 Boundary:** refused: "a zero with a sign (`+0`, `-0`)."
- **Built:** accepted; `+0` and `-0` are `0`.

### C-14 Separator in offset date-times
- **PRD Terminology, "Offset date-time":** "Its date and time are joined by `T` or `t`."
- **PRD FP-02 "Date-time values":** "The separator between date and time may be `T`, `t`, or a space."
- **Built:** the FP-02 rule for all date-times, offset ones included. A space counts as a separator only when a two-digit hour follows it, so `1979-05-27 # c` is a local date.

## Choices where the spec is silent

- **Byte-order mark:** not stripped. A leading U+FEFF is an invalid character and raises `TOMLDecodeError`. The spec does not mention a BOM.
- **Invalid UTF-8 in `load`:** raised as `TOMLDecodeError` (a `ValueError`, not a `UnicodeDecodeError`) with `doc` set to the text decoded with `errors="replace"`, and `pos` at the first bad byte in characters. The spec says only "decodes the bytes as UTF-8" and the decode error requires a text `doc`.
- **Control characters in comments:** refused, except tab (TOML forbids them there). The spec states only that non-ASCII text is allowed in comments.
- **Surrogate code points in the input string:** not specifically rejected outside escapes.
- **Error positions:** `pos` is the offending character where one exists (for example the start of an invalid value or key, or the newline that ends an unterminated single-line string). For unterminated strings and other failures at the end of input, `pos` is the length of the document. The wording of messages is free.
- **Leap second `:60`:** refused; seconds must be 0-59 (per FP-02).
- **Time zones:** only `Z`/`z` and `±HH:MM` (hours 0-23, minutes 0-59). `-00:00` is a zero offset. Offsets without a colon are refused.
- **Fractional seconds beyond six digits:** truncated, as C-02 says.
- **Exponent leading zeros:** accepted (`1e05`), since TOML's exponent takes zero-prefixable digits. Fraction digits may also have leading zeros (`1.05`).
- **Converter arguments:** `parse_float` is called with the float's exact token text (sign, underscores, exponent included). The default is `float`, which accepts the same underscore and sign forms.
- **Converter failures:** an exception raised by the caller's `parse_float` propagates unchanged.
- **Nesting depth:** arrays and inline tables are parsed with an explicit stack, so deep nesting does not raise `RecursionError`. Verified at 5000 levels.
- **Large integers:** `int()` is used, so on Python 3.11+ integers longer than 4300 decimal digits hit CPython's int string-conversion limit and raise `ValueError`. The spec gives no limit; the product does not change the process-wide setting.
- **`load` text-mode detection:** an `io.TextIOBase` instance is refused before reading. Other objects whose `read()` returns `str` are refused after the read.
- **Inline tables:** TOML 1.1 newlines, comments and trailing commas are accepted inside `{ }`.
- **Keys:** bare keys are ASCII `A-Za-z0-9_-` only; a quoted key can hold any character TOML allows.

## Verification performed

- Scratch checks (outside `/app`, a few hundred individual cases): scalar forms and boundaries, all string forms and escapes, date-times with and without offsets/fractions, table/array-of-table/inline-table rules, dotted-key rules, the float converter (including refused dict/list/subclass results), `load` with binary and text objects, the `TOMLDecodeError` attributes and formatting, and 5000-deep nesting. All pass.
- Differential check against the stdlib `tomllib` on sample documents within TOML 1.0: identical results. The one divergence found, a trailing comma in an inline table, is TOML 1.1 behaviour that the spec requires.
- `tomllib` is used only as a local oracle; the product does not delegate to it.
- Not tested: PyPy, Python 3.8 specifically (the code avoids newer syntax), Windows.
