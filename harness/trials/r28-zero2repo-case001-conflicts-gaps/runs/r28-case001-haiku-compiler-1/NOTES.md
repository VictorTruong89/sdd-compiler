# Tomlparse — implementation notes

Layout (src layout, pure Python, stdlib only):

- `src/tomlparse/__init__.py` — public names: `loads`, `load`, `TOMLDecodeError`.
- `src/tomlparse/_api.py` — the two parse entries (`loads` for text, `load` for binary files).
- `src/tomlparse/_parser.py` — hand-written TOML v1.1.0 parser. It does not delegate to any other TOML parser.
- `src/tomlparse/_error.py` — `TOMLDecodeError(msg, doc, pos)`, a subclass of `ValueError`.
- `pyproject.toml` — setuptools PEP 517 metadata, `requires-python >= 3.8`, no dependencies.
- `tests/test_tomlparse.py` — 64 unit tests, grouped by feature point. Run with `PYTHONPATH=src python -m pytest tests`.

`spec/` is untouched.

## Contradictions (the 16 UNSETTLED ids in `spec/MAP.md`)

For each one: what each side says, where, and what was built. "Adopted" means the side that was implemented.

1. **CF-000001** — quote before the closing delimiter of a multi-line basic string.
   - A: FP-02, "Both multiline forms may contain one or two of their own quote characters … including directly before the closing delimiter" (`spec/packs/12`, N-000135).
   - B: FP-02 error list, "a quote character directly before the closing delimiter of a multiline basic string" is refused (N-000178).
   - Built: A. One or two quotes before `"""` are content (`"""x""""` is `x"`). Six or more quotes in a row are refused. This matches TOML.

2. **CF-000008** — line endings inside a CRLF multi-line string.
   - A: FP-01, a CRLF "is treated as a single line feed everywhere, including inside string values … holds line feeds only" (N-000111, N-000112).
   - B: FP-02, "line endings inside a multiline basic string are kept exactly as written, carriage returns included" (N-000133).
   - Built: A. CRLF becomes LF in multi-line strings. A lone CR is refused.

3. **CF-000009** — first line feed of a multi-line literal string.
   - A: FP-02, "a multiline literal string keeps every character after its opening delimiter, including a first line feed" (N-000130).
   - B: FP-02, "in both multiline forms a line feed immediately after the opening delimiter is discarded" (N-000131).
   - Built: B. The first line feed is dropped in both multi-line forms, as TOML requires.

4. **CF-000012** — a header declaring a sub-table of a table created by dotted keys.
   - A: FP-01, "A table created by dotted keys cannot receive a sub-table through a header" (glossary, N-000021).
   - B: FP-01, "a sub-table of it that has not itself been defined may still be declared by a header, as TOML v1.1.0 allows" (N-000098).
   - Built: B, for sub-tables that are not yet defined. `[fruit.apple.texture]` after `apple.color = …` is accepted. Redefining a table the header or dotted keys already defined (`[fruit.apple]`) is refused.

5. **CF-000015** — whitespace after a line-ending backslash in a multi-line basic string.
   - A: FP-02, the backslash "removes the line ending and all whitespace … up to the next non-whitespace character" (N-000134).
   - B: FP-02, "After a line-ending backslash, the next line's leading spaces and tabs are kept" (N-000136).
   - Built: A (the TOML rule). The next line's leading whitespace is removed.

6. **CF-000023** — converter results that are subclasses of dict or list.
   - A: FP-02 glossary, "Only a result whose type is exactly `dict` or exactly `list` is refused" (N-000029).
   - B: FP-05 error row and FP-03/04 tables, "(or an instance of a subclass of either)" (N-000296, N-000232).
   - Built: B. `isinstance` is used, so subclass instances are refused with `ValueError`.

7. **CF-000032** — same as CF-000023, against the public-surface wording "dictionaries and lists forbidden as conversion results" (N-000038). Built the same way: subclasses are refused.

8. **CF-000028** and **CF-000035** — a raw tab in a literal string.
   - A: FP-02, escapes "never in literal or multiline literal strings" (N-000129).
   - B: FP-02, "A tab in a one-line string must be written as backslash-t" (N-000143).
   - C (FP-02 error list): "raw control characters other than tab" are refused (N-000178), so a raw tab is legal in every string form.
   - Built: a raw tab is accepted in all string forms. `\t` is still an escape in basic strings. The N-000143 requirement to write a tab as `\t` is not applied, because it would contradict N-000178 and TOML.

9. **CF-000037** — hex digit case.
   - A: FP-02, "hex digits may be either case" (N-000146).
   - B: FP-02, "hexadecimal digits written in lowercase" (N-000285, return shape).
   - Built: A. Either case is accepted in input (`0xDEAD_beef`). A parsed integer has no case, so B has nothing to apply to.

10. **CF-000045** and **CF-000069** — fractional seconds: truncate or round.
    - A: FP-02 seconds and fractions, the first six digits are used and "any digits after the sixth are dropped (truncated, not rounded)" (N-000157).
    - B: FP-03 return shape, "its fraction rounded to the nearest microsecond" (N-000292).
    - Built: A (truncation). `07:32:00.9999999` gives microsecond 999999.

11. **CF-000059** — trailing comma in an array.
    - A: FP-02 "Arrays … end with a trailing comma" (N-000106).
    - B: return shape, "an array whose last element is followed by a comma is refused" (N-000282).
    - Built: A. Trailing commas are accepted in arrays, as TOML 1.1 allows. Trailing commas in inline tables are also accepted.

12. **CF-000062** — omitted seconds in a local time.
    - A: Terms, "Local time … Its seconds are always written" (N-000028).
    - B: FP-02, "In any value with a time part, seconds may be omitted" (N-000154). Non-goals also lists omitted seconds as a v1.1 feature.
    - Built: B. `07:32` is a local time with second 0.

13. **CF-000065** — signed zero.
    - A: FP-02 integers, "a signed zero is the integer 0" (N-000144).
    - B: FP-02 error list, "a zero with a sign (`+0`, `-0`)" is refused (N-000168).
    - Built: A. `+0` and `-0` are integer 0, as TOML allows.

14. **CF-000068** — date/time separator.
    - A: Terms, "Its date and time are joined by `T` or `t`" (N-000024, offset date-time).
    - B: FP-02, "The separator between date and time may be `T`, `t`, or a space" (N-000153).
    - Built: B for all date-time kinds. A space separator is accepted only when a digit follows it, so `1979-05-27 # c` is still a date.

## Assumptions (not stated in the spec)

- **Invalid UTF-8 in `load`**: the spec only says bytes are UTF-8. There is no decoded text to report, so `UnicodeDecodeError` (a `ValueError`, not a `TOMLDecodeError`) propagates.
- **Byte-order mark**: a leading U+FEFF is refused as an invalid character. The spec does not mention it.
- **Surrogates and control characters**: lone surrogate code points in the input are refused in strings and comments. Control characters other than tab are refused in comments, as TOML 1.1 requires; the PRD only says non-ASCII is allowed in comments.
- **UTC offsets**: hours 00–23 and minutes 00–59. A date or time component out of range is refused.
- **Dates**: year 0000 is refused (not a real calendar date); Python's `datetime` range (years 1–9999) applies.
- **Leap seconds**: second 60 is refused (seconds 0–59).
- **Fractions**: a fraction needs at least one digit; underscores are not allowed in date-time fractions.
- **Floats**: `1e5` (integer part with an exponent) is a float. Exponent digits may have leading zeros, as TOML allows. The default converter strips underscores before `float()`, but a user converter receives the text with underscores.
- **Integers**: unbounded. Literals longer than 4300 digits are converted in chunks, so CPython's digit limit does not reject them.
- **Dotted keys**: dotted keys may extend a table created by dotted keys, or an implicit table created by a header; the spec does not say so explicitly. Dotted keys may not extend a header-defined table or an inline table.
- **Duplicate key vs. table**: `a = {}` followed by `[a]`, and `[a]` followed by `a = 1`, are both refused as duplicates.
- **Key `""`**: an empty quoted key is allowed; an empty bare key is refused.
- **Inline tables**: TOML 1.1 newlines and comments are allowed inside inline tables (N-000104).
- **Nesting depth**: not limited by the parser. Very deep nesting raises Python's `RecursionError`. The spec does not give a limit.
- **Converter exceptions**: an exception raised by `parse_float` propagates unchanged.
- **`parse_float` validation**: the spec does not require the argument to be callable; a non-callable fails with the Python `TypeError` when first called.
- **Version**: the spec says 2.4.0 and later are TOML 1.1 compatible, but names no version attribute. `pyproject.toml` says `2.4.0`; the package has no `__version__`.
- **`load` reads the whole file** with `read()` and does not seek.
- **Lone carriage return** outside strings is refused. Only `\n` and `\r\n` are line endings.
- **Comments after a value without a space**: `a = 1#c` is accepted, as the PRD says the `#` may follow with or without whitespace.
- **Result types**: tables are plain `dict`, arrays are plain `list`, scalars are builtin or standard-library values. Keys keep document order.

## Coverage of `spec/CHECKLIST.md` ids

Every id is either implemented (code), tested (test), or listed as not done with a reason. Code refers to `# spec:` comments in `src/tomlparse/`. "Tested" refers to `tests/test_tomlparse.py`.

| Ids | Unit / topic | Where | Status |
| --- | --- | --- | --- |
| N-000001–N-000011 | Product overview (parser only, TOML 1.1, plain values, feature points are real) | whole package; `pyproject.toml` version | implemented |
| N-000012–N-000030 | Terminology (TOML document, mapping, table, array, bare/dotted/inline key, date-time kinds, float converter, decode error) | `_parser.py`, `_error.py` | implemented; tested |
| N-000031–N-000039 | Public surface inventory; no extra product surfaces | `__init__.py`, `_api.py`; test `test_no_writer_or_cli` | implemented; tested |
| N-000040–N-000042 | Pure Python, zero runtime dependencies, no compiled extensions | `_api.py`, `_parser.py` import only stdlib | implemented (no `tomllib`, no extensions) |
| N-000043–N-000045 | Python 3.8+, Linux/macOS/Windows; Linux is the reference | `pyproject.toml` (`requires-python`); code checked for 3.8 syntax with `ast` | implemented; run tested on Linux only (N-000045 is informational) |
| N-000046–N-000048 | CPU only; imported from source tree | no GPU code; `src/` layout | implemented |
| N-000049–N-000050 | TOML v1.1.0 only; no v1.0-only behaviour | `_parser.py`; tests in `FP02Scalars` and `FP01Structure` | implemented; tested |
| N-000051–N-000052 | Plain Python result types | `_api.py`, `_parser.py` | implemented; tested |
| N-000053–N-000056 | Error text free; exception kind and location fixed | `_error.py` | implemented; tested |
| N-000057–N-000062 | Real parser, no delegation (not even `tomllib`), CPU baseline | `_parser.py`; no `tomllib` import (checked by grep) | implemented |
| N-000063–N-000076 | Non-goals: no writer, no round-trip, v1.1 accepted, no CLI, no throughput promise, no fallback to `tomllib` | absence in code; v1.1 accepted in `_parser.py` | implemented (by absence) |
| N-000074 | "Speed is a design goal, not a requirement" | no throughput guarantee made | not done: informational only, no code required |
| N-000077–N-000079 | FP-01 entry point; text entry; binary entry gives same mapping | `_api.loads`, `_api.load` | implemented; tested |
| N-000080–N-000081 | FP-01 structure per TOML v1.1.0 | `_parser.parse`, `_header`, `_assign` | implemented; tested |
| N-000082 | Empty / whitespace / comment-only text | `_parser.parse` | tested (`test_empty_documents`) |
| N-000083–N-000084 | Root pairs, pairs after a header | `_parser.parse`, `_keyval` | tested |
| N-000085–N-000088 | Keys are strings; bare keys; case sensitivity | `_simple_key` | tested (`test_keys_are_strings`) |
| N-000089–N-000092 | Quoted keys: empty, any character, dots inside | `_simple_key`, `_basic_string`, `_literal_string` | tested (`test_quoted_keys`) |
| N-000093–N-000095 | Dotted keys and dotted headers | `_assign`, `_header` | tested |
| N-000096–N-000098 | Header creates missing parents; sub-table of dotted table (CF-000012) | `_header_table`, `_descend` | tested |
| N-000099–N-000102 | Array-of-tables headers; attach to last element; implicit parents | `_header_aot`, `_descend` | tested |
| N-000103–N-000104 | Inline tables (empty, dotted, multi-line, trailing comma) | `_inline_table` | tested |
| N-000105–N-000106 | Arrays (empty, mixed, nested, trailing comma) (CF-000059) | `_array` | tested |
| N-000107–N-000109 | Comments, non-ASCII in comments | `_comment`, `_skip_blank` | tested |
| N-000110 | Indentation insignificant | `_skip_ws`, `_skip_blank` | tested |
| N-000111–N-000112 | CRLF is one line feed (CF-000008) | `_ml_basic_string`, `_ml_literal_string` | tested |
| N-000113–N-000122 | Forbidden structures (duplicates, redefinitions, malformed headers and pairs) | `_header_table`, `_header_aot`, `_assign`, `_expect_eol` | tested (`test_forbidden_structures`) |
| N-000123 | FP-02 entry | `_value` | implemented |
| N-000124–N-000126 | Booleans lowercase only | `_value` | tested |
| N-000127–N-000136 | Four string forms, multi-line rules (CF-000001, 009, 015) | `_basic_string`, `_literal_string`, `_ml_basic_string`, `_ml_literal_string` | tested |
| N-000137–N-000143 | Basic-string escapes; `\xHH`, `\uHHHH`, `\UHHHHHHHH`, `\e`; key escapes; literal key unchanged (CF-000028, 035) | `_escape`, `_SIMPLE_ESCAPES` | tested |
| N-000144–N-000147 | Integers in four bases; underscores; signed zero (CF-000037, 065) | `_number`, `_decimal_int` | tested |
| N-000148–N-000150 | Floats; `inf` and `nan` spellings | `_number`, `_make_float` | tested |
| N-000151–N-000153 | Date-time values; separator (CF-000068) | `_datetime`, `_DATETIME_RE` | tested |
| N-000154–N-000158 | Seconds optional (CF-000062); fraction to microseconds, truncated (CF-000045, 069) | `_datetime`, `_local_time`, `_micro` | tested |
| N-000159 | Valid calendar dates including leap days | `_datetime` (`datetime.date`) | tested |
| N-000160–N-000161 | Values copy and compare as standard-library values | `datetime` objects | tested (`test_date_time_copy_and_compare`) |
| N-000162–N-000180 | Scalar refusals (booleans, numbers, floats, escapes, strings, date/time ranges) | `_number`, `_escape`, `_basic_string` etc. | tested (`test_bad_*`) |
| N-000181–N-000189 | FP-03 binary file: UTF-8, binary mode, same result as text, no bytes → `{}` | `_api.load` | tested |
| N-000190–N-000192 | Text-mode file refused with `TypeError` | `_api.load` (`io.TextIOBase` check; `str` read result) | tested |
| N-000193–N-000196 | Decode error location for binary entry; string entry refuses bytes/file | `_api.load`, `loads` | tested |
| N-000197–N-000202 | FP-04 failures: decode error is a `ValueError`; no partial mapping | `TOMLDecodeError` inheritance; `_parser` raises before returning | tested |
| N-000203–N-000207 | Error location: line, column, 0-based offset, interior vs end (MUST, L4) | `_error.py` | tested (`test_attributes_and_location`, `test_end_of_document_location`) |
| N-000208–N-000209 | Formatted report includes the location | `_error.py` | tested |
| N-000210–N-000212 | Caller can construct the error with three arguments | `_error.py` | tested (`test_constructed_by_caller`) |
| N-000213–N-000217 | Wrong Python type is `TypeError`, not decode error | `loads`, `load` | tested |
| N-000218 | Wording of the report is free (MAY) | `_error.py` wording | implemented (informational) |
| N-000219 | Exception kind and location rules fixed | `_error.py` | implemented |
| N-000220–N-000222 | FP-05 converter scope; no change to other types | `_make_float` | tested |
| N-000223–N-000227 | Converter called for every float with text as written; result stored unchanged | `_make_float` | tested (`test_converter_gets_text_as_written`) |
| N-000228–N-000229 | Converter never called for other types | `_value`, `_number` | tested |
| N-000230–N-000231 | Any non-dict/list return is bound as returned | `_make_float` | tested |
| N-000232–N-000233 | dict/list result → `ValueError`, not decode error (CF-000023, 032) | `_make_float` | tested |
| N-000234–N-000235 | Hardware: mandatory CPU profile; no substitute for it | pure Python, no accelerator path | implemented |
| N-000236–N-000239 | Summary: pure Python, no compiled extensions, 3.8+, source install | `pyproject.toml` | implemented |
| N-000240–N-000245 | CPU baseline profile: import from source, parse in-memory document | `_api.loads` | implemented; tested |
| N-000246–N-000247 | Setup: Python 3.8+; zero runtime dependencies | `pyproject.toml` | implemented |
| N-000248 | Assumption: optional compiled wheels exist on some platforms | none built | not done: optional, not required by the spec |
| N-000249–N-000250 | Compiled extensions not required; none built | no native code | implemented |
| N-000251–N-000254 | Build: no native compile step; src layout; PEP 517; editable install or source on path | `pyproject.toml`, `src/` | implemented; `PYTHONPATH=src` import tested. `pip install -e` was not run (it would create build artifacts in the repo) |
| N-000255–N-000265 | Interface contract overview (parser only; no writer, CLI, I/O of its own; pure Python; 3.8+; cross-platform; CPU-only) | whole package | implemented |
| N-000266–N-000273 | Public surface: package `tomlparse` under `src`; `loads`, `load`, `TOMLDecodeError` importable from root; import has no I/O; internal layout is the implementer's choice | `__init__.py`, `_api.py`, `_parser.py`, `_error.py` | implemented; tested (`Interface`, `Surface`) |
| N-000274–N-000298 | `loads(s, *, parse_float=float)`; return shape; failure table; message wording free | `_api.loads`, `_parser.py` | implemented; tested |
| N-000299–N-000306 | `load(fp, *, parse_float=float)`; text-mode refused; decode error with decoded text as `doc` | `_api.load` | implemented; tested |
| N-000307–N-000323 | `TOMLDecodeError`: subclass of `ValueError`; `msg`, `doc`, `pos`, `lineno`, `colno`; formatted report; wording free | `_error.py` | implemented; tested |

Not done, with reasons: N-000041 and N-000248 (optional compiled wheels: none built; the spec says they are optional), N-000074 (throughput is a design goal, not a requirement, so no code is needed), N-000045 and N-000218 (informational or free wording, see above).

## Verification

- `PYTHONPATH=src python -m pytest tests` — 64 tests pass.
- Structured fuzzing against the stdlib `tomllib` as a local oracle (outside the product; the product does not import it). Across over 200,000 generated and mutated documents (several seeds): no crashes (every bad input raised `TOMLDecodeError`), and no case where `tomllib` accepted a document with a different value. The only differences are documents we accept that TOML 1.0 rejects, and each uses a TOML 1.1 feature the spec requires: `\e` or `\x` escapes, a local time without seconds, a space date/time separator, a newline or trailing comma in an inline table, or a comment directly after a value.
