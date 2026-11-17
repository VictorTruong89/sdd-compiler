# Notes: Tomlparse build

Spec: `spec/` (exported with `--allow-open`, 16 contradictions unsettled). Code: `src/tomlparse/`. Tests: `tests/`.
Run: `cd /app && PYTHONPATH=src python3 -m pytest tests` (116 passing on Python 3.13; 3.8 syntax checked with `ast.parse(feature_version=(3, 8))`, not run on 3.8).

Layout:
- `src/tomlparse/__init__.py`: `loads`, `load`, `TOMLDecodeError` re-export, `__version__ = "2.4.0"`.
- `src/tomlparse/_errors.py`: `TOMLDecodeError(msg, doc, pos)`; derives `lineno`, `colno`.
- `src/tomlparse/_parser.py`: hand-written recursive-descent TOML v1.1.0 decoder. No `tomllib`.
- `pyproject.toml`: src-layout, setuptools PEP 517 backend, no runtime dependencies.

## Conflicts in the spec

Each conflict lists both sides (pack and claim id), then what was built. Where I chose one side, the other is not implemented.

1. **Quote before the closing delimiter of a multiline string (CF-000001).**
   A: N-000135, pack 12 FP-02, "Both multiline forms may contain one or two of their own quote characters ... including directly before the closing delimiter."
   B: N-000178, pack 12 FP-02 boundary list, "a quote character directly before the closing delimiter of a multiline basic string" is refused.
   Built: 1 or 2 quotes directly before the closing delimiter are accepted in both multiline forms; 3 to 5 extra quotes close the string with the excess kept; 6 or more is an error. This is the TOML grammar.

2. **CRLF inside multiline strings (CF-000008).**
   A: N-000112, pack 12 FP-01, "a multiline string written with carriage-return/line-feed line endings holds line feeds only."
   B: N-000133, pack 12 FP-02, "Line endings inside a multiline basic string are kept exactly as written, carriage returns included."
   Built: A. CRLF becomes LF in strings. A bare CR (not followed by LF) is an error inside strings and comments.

3. **Newline right after the opening delimiter of a multiline literal string (CF-000009).**
   A: N-000130, pack 12 FP-02, "A multiline literal string keeps every character after its opening delimiter, including a first line feed."
   B: N-000131, pack 12 FP-02, "In both multiline forms a line feed immediately after the opening delimiter is discarded."
   Built: B. The first newline is discarded in both multiline forms, as TOML requires.

4. **Header declaring a sub-table of a dotted-key table (CF-000012).**
   A: N-000021, pack 12 FP-01 (and pack 07 N-000021), "A table created by dotted keys cannot receive a sub-table through a header."
   B: N-000098, pack 12 FP-01, "a sub-table of it that has not itself been defined may still be declared by a header, as TOML v1.1.0 allows."
   Built: both readings. A dotted-key table cannot be defined by a header (`[a.b]` after `a.b.c = 1` is an error). Its undefined sub-tables can be declared by a header (`[fruit.apple.texture]` after `apple.color = ...`).

5. **Whitespace after a line-ending backslash (CF-000015).**
   A: N-000134, pack 12 FP-02, the backslash "removes the line ending and all whitespace ... up to the next non-whitespace character."
   B: N-000136, pack 12 FP-02, "After a line-ending backslash, the next line's leading spaces and tabs are kept."
   Built: A. In multiline basic strings the whitespace after a line-ending backslash is removed. B has no effect on literal strings, which have no line-ending backslash.

6. **Float converter returning a subclass of dict or list (CF-000023, CF-000032).**
   A: N-000029, pack 07 terms, "Only a result whose type is exactly `dict` or exactly `list` is refused."
   B: N-000296 (pack 03), N-000232/N-000199 (pack 12 FP-05), N-000038 (pack 08), "or an instance of a subclass of either" / "dictionaries and lists forbidden."
   Built: B. `isinstance(result, (dict, list))` is refused with `ValueError`. Three claims agree on this; N-000029 is the outlier.

7. **Raw tab in literal keys and in one-line strings (CF-000028, CF-000035).**
   A: N-000129 and N-000141, pack 12 FP-02, escapes are never processed in literal strings and literal keys are unchanged.
   B: N-000143, pack 12 FP-02, "A tab in a one-line string must be written as backslash-t."
   C: N-000178, pack 12 FP-02 boundary, "raw control characters other than tab" are refused, so a raw tab is legal inside strings.
   Built: a raw tab is accepted in all string forms, and in keys. `\t` also works in basic strings. Backslash-t is not required. C and TOML agree on the raw tab.

8. **Hex digit case (CF-000037).**
   A: N-000146, pack 12 FP-02, "hex digits may be either case" / "Hex digits are case-insensitive."
   B: N-000285, pack 03, "hexadecimal digits written in lowercase."
   Built: A. Hex digits in escapes and in integers may be either case. For integers this has no visible effect, since the value is an `int`. Prefixes (`0x`, `0o`, `0b`) are lowercase only, as N-000144 and N-000167 require.

9. **Uppercase escape digits (not in the export's unsettled list).**
   A: N-000139 and N-000146, pack 12 FP-02 (in the "Basic-string escapes" bullet), "Hex digits are case-insensitive."
   B: N-000174–N-000177, pack 12 FP-02 boundary list, "escape digits written as uppercase letters" are refused.
   Built: A. Uppercase escape digits are accepted. TOML's own grammar is case-insensitive for hex digits.

10. **Fractional seconds: truncate or round (CF-000045, CF-000069).**
    A: N-000157 and N-000158, pack 12 FP-02, "the fraction's first six digits are read as microseconds ... any digits after the sixth are dropped (truncated, not rounded)."
    B: N-000292, pack 03 (interface contract), "its fraction rounded to the nearest microsecond."
    Built: A (truncation). The feature point gives the full rule, and the contract's wording is a summary.

11. **Trailing comma in arrays (CF-000059).**
    A: N-000106, pack 12 FP-01, arrays "end with a trailing comma."
    B: N-000282, pack 03, "an array whose last element is followed by a comma is refused."
    Built: A. TOML arrays accept a trailing comma.

12. **Seconds in local times (CF-000062).**
    A: N-000028, pack 07 terms, local time: "Its seconds are always written."
    B: N-000154, pack 12 FP-02, "in any value with a time part, seconds may be omitted, in which case the second is 0."
    Built: B. Seconds are optional for local times and for date-times, as TOML 1.1 allows.

13. **Signed zero (CF-000065).**
    A: N-000144, pack 12 FP-02, "a signed zero is the integer 0."
    B: N-000168, pack 12 FP-02 boundary list, "a zero with a sign (`+0`, `-0`)" is refused.
    Built: A. `+0`, `-0` and `+0.0` are accepted.

14. **Date/time separator (CF-000068).**
    A: N-000024, pack 07 terms, the offset date-time's date and time "are joined by `T` or `t`."
    B: N-000153, pack 12 FP-02, "The separator between date and time may be `T`, `t`, or a space."
    Built: B. `T`, `t` or a single space. TOML 1.1 allows a space.

Export conflicts, all 16 (CF-000001, 008, 009, 012, 015, 023, 028, 032, 035, 037, 045, 059, 062, 065, 068, 069) are covered by items 1–14 above: 023 and 032 by item 6, 028 and 035 by item 7, 045 and 069 by item 10. Item 9 is extra.

## Assumptions (not stated in the spec)

- **Invalid UTF-8 in `load()`.** Not specified. Raised as `TOMLDecodeError("invalid UTF-8 in document", ...)`, with `doc` the text decoded with replacement characters and `pos` the character offset of the first bad byte. The spec only says a decode error is raised for invalid TOML.
- **UTF-8 byte-order mark.** Not specified. Rejected as an invalid character (`expected key`). TOML does not list a BOM as allowed.
- **`load()` reads only.** It calls `read()` once, does not seek or close the file, and accepts any object with a `read` method. A `read()` returning `str` gives `TypeError`, which is how text-mode files are detected. It does not inspect the object's mode.
- **Bytes-like returns.** `bytes`, `bytearray` and `memoryview` from `read()` are accepted for `load()`. `loads()` accepts only `str`; bytes passed to it is a `TypeError`.
- **Year 0000.** TOML allows it, but Python's `datetime.date` does not. Years 0000 are rejected as an invalid calendar date.
- **Date-time ranges.** Hours 0–23, minutes 0–59, seconds 0–59 (no leap second 60), and UTC offsets with hours 0–23 and minutes 0–59. Offsets accept `Z`, `z`, or `±HH:MM` only.
- **Fraction digits.** Any number of fraction digits is accepted. Only the first six are used.
- **Escape `\e` and `\xHH`.** Taken from TOML v1.1.0 (escape is U+001B, `\xHH` is a code point from U+0000 to U+00FF). `\x`, `\u` and `\U` code points must be Unicode scalar values (no surrogates, at most U+10FFFF).
- **Control characters.** Outside strings and comments, and inside strings and comments, control characters other than tab (U+0000–U+001F except tab, and U+007F) are refused, as TOML requires. Newlines are handled separately.
- **Error positions.** `pos` is the index of the offending character. For an error found at the end of input (for example an unterminated string or array), `pos` is `len(doc)`, which makes the report say "at end of document". Errors on a construct report the position where the construct starts or where it breaks.
- **`TOMLDecodeError` extras.** `__reduce__` is defined so the error pickles with its three arguments. The formatted message is `"<msg> (line L column C (char P))"` or `"<msg> (at end of document)"`.
- **Nesting depth.** Arrays and inline tables are parsed recursively. Python's recursion limit allows about 490 levels of nested arrays (fewer for nested inline tables). Deeper input raises `TOMLDecodeError("document is nested too deeply", ...)`, not `RecursionError`. The spec sets no limit, so this is a known gap.
- **Large integers.** Decimal integers of any length are accepted. CPython limits `int(str)` to 4300 digits, so longer ones are converted in 1000-digit chunks. Hex, octal and binary have no such limit.
- **Default float.** Underscores are removed and the text is passed to `float()`. A custom `parse_float` receives the text as written, underscores and sign included, and is called only for floats (decimal floats and `inf`/`nan` spellings), never for integers or strings.
- **`parse_float` exceptions.** Exceptions raised by the converter propagate unchanged. The `ValueError` for a dict or list result is a plain `ValueError`, not `TOMLDecodeError`.
- **Keys.** Bare keys are ASCII letters, digits, `_` and `-`. A quoted key may be empty. A multiline string as a key is an error.
- **Version string.** `__version__ = "2.4.0"`, the first version the PRD says is TOML v1.1.0 compatible.
- **Packaging.** `pyproject.toml` declares `requires-python >= 3.8`, `dependencies = []` and setuptools with src layout. The judge does not install anything; tests use `PYTHONPATH=src`.

## Spec ids not implemented as code

These ids are referenced by a marker or test, so the checklist is complete. The reason for each is listed here.

- **N-000041, N-000042** (optional compiled wheels, Level L2, MAY). No compiled extension exists; the pure-Python path is the product. Not done, because the spec says it is optional.
- **N-000073, N-000074, N-000075** (throughput is not a requirement; speed scripts are not product). No benchmark or speed code is in the product. Not done by design.
- **N-000002, N-000003, N-000032, N-000064, N-000065, N-000072** (no writer, no round-trip, no CLI). Verified by absence and tests in `tests/test_product_surface.py` and `tests/test_tomlparse.py`.
- **N-000076** (fallback import of `tomllib` is integrator guidance, not a product feature). Not done by design. The package never imports `tomllib`.
- **N-000008–N-000011, N-000031, N-000039, N-000053–N-000056** (documentation and scope statements about the spec). Implemented as described: no extra public surface, and error wording is free.

## Test coverage

`tests/test_tomlparse.py` covers feature points FP-01 to FP-05, the binary-file entry, the decode error, the float converter and the public surface. `tests/test_product_surface.py` covers layout, dependencies, the 3.8 syntax floor and the absence of out-of-scope surfaces. Each test carries `# spec:` markers. Every id in `spec/CHECKLIST.md` appears in a marker in `src/` or `tests/`, which was checked with grep.
