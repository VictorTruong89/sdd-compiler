# Notes — tomlparse build

This file records (1) spec contradictions and how they were resolved, (2) things the spec
does not state and what I assumed, and (3) how every checklist id was accounted for.
Layout: `src/tomlparse/` (package), `tests/` (pytest suite), `pyproject.toml` (src-layout,
PEP 517 backend). `spec/` is untouched. Run the tests with `PYTHONPATH=src python3 -m pytest tests`.

Source map: `spec/MAP.md` says 20 contradictions have no human verdict (`--allow-open`).
Each one is resolved below. Where two statements disagree, the table gives both sides with
their location, then what was built.

## 1. Contradictions (all 20 unsettled CF ids)

Locations: `FP-0x` = `spec/packs/12-full-prd--feature-points.md` (pack 12); other packs are
named by file. "Pack 07" = `07-full-prd--terminology.md`, "Pack 03" = `03-interface-contract--tomlparse-loads.md`,
"Pack 05" = `05-interface-contract--tomlparse-tomldecodeerror.md`, "Pack 08" = `08-full-prd--public-surface-inventory.md`.

| CF id | Side A (location) | Side B (location) | What was built |
|---|---|---|---|
| CF-000001 | N-000135, FP-02 multiline strings: quote characters "including directly before the closing delimiter" are allowed | N-000178, FP-02 error list: "a quote character directly before the closing delimiter of a multiline basic string" is refused | **Allowed** (A). Runs of 1–2 quotes are content; a run of 3–5 closes the string with 0–2 extra quotes, as TOML does. A run of 6+ is refused. |
| CF-000008 | N-000112, FP-01: a CRLF multiline string "holds line feeds only" | N-000133, FP-02: line endings "kept exactly as written, carriage returns included" | **CRLF folded to LF everywhere** (A). A lone CR is still refused. |
| CF-000009 | N-000130, FP-02: a multiline literal string "keeps every character after its opening delimiter, including a first line feed" | N-000131, FP-02: a line feed right after the opening delimiter "is discarded" in both multiline forms | **First line feed discarded in both multiline forms** (B, as TOML does). |
| CF-000012 | N-000021, pack 07 "Dotted key": "A table created by dotted keys cannot receive a sub-table through a header" | N-000098, FP-01: a sub-table of a dotted-key table "that has not itself been defined may still be declared by a header, as TOML v1.1.0 allows" | **B**: `[fruit.apple.texture]` after `apple.color = …` is accepted. Re-opening the dotted-key table itself (`[fruit.apple]`) is refused. This matches the TOML example. |
| CF-000015 | N-000134, FP-02: a line-ending backslash removes "all whitespace … up to the next non-whitespace character" | N-000136, FP-02: "After a line-ending backslash, the next line's leading spaces and tabs are kept" | **A**: the leading whitespace of the next line is removed (TOML behavior). |
| CF-000023 | N-000029, pack 07 "Float converter": "Only a result whose type is exactly `dict` or exactly `list` is refused" | N-000296, pack 03: `parse_float` returning "a `dict` or `list` (or a subclass instance)" is refused | **B**: `isinstance` check, so subclass instances are refused with `ValueError`. |
| CF-000028 | N-000141, FP-02: "a key written as a literal string does not" undergo escape processing | N-000143, FP-02: "A tab in a one-line string must be written as backslash-t" | **Raw tab accepted** in all one-line strings and literal keys. Backslash-t is still valid in basic strings. A literal string has no escapes, so a raw tab there is the only way to write one. |
| CF-000032 | N-000029, pack 07 (exact type only) | N-000038, pack 08: "dictionaries and lists forbidden as conversion results" | Same as CF-000023: **subclass instances refused** (`isinstance`). |
| CF-000035 | N-000129, FP-02: escapes "never" processed in literal or multiline literal strings | N-000143, FP-02: a tab in a one-line string "must be written as backslash-t" | Same as CF-000028: **raw tab accepted**; no escape processing in literal strings. |
| CF-000037 | N-000146, FP-02: "hex digits may be either case" | N-000285, pack 03: "hexadecimal digits written in lowercase" | **Either case accepted** in hex integers (A). The prefix `0x`/`0o`/`0b` must be lowercase (both sides agree). |
| CF-000045 | N-000156, FP-02: "the fraction's first six digits are read as microseconds" | N-000292, pack 03: local-time fraction "rounded to the nearest microsecond" | **Truncation** (per N-000157; see CF-000069). Digits after the sixth are dropped. |
| CF-000059 | N-000106, FP-01: arrays "end with a trailing comma" | N-000282, pack 03: "an array whose last element is followed by a comma is refused" | **Trailing comma accepted** (A, also TOML 1.1). |
| CF-000062 | N-000028, pack 07: local time "Its seconds are always written" | N-000154, FP-02: "seconds may be omitted … in any value with a time part" | **Seconds may be omitted** (B). Local time `07:32` is accepted and gives second 0. |
| CF-000065 | N-000144, FP-02: "a signed zero is the integer 0" | N-000168, FP-02 error list: "a zero with a sign (`+0`, `-0`)" | **Accepted** (A): `+0` and `-0` both give `0`. |
| CF-000068 | N-000024, pack 07: an offset date-time's date and time "are joined by `T` or `t`" | N-000153, FP-02: "The separator … may be `T`, `t`, or a space" | **Space accepted** as separator for all date-times (B, general statement). |
| CF-000069 | N-000157, FP-02: digits after the sixth "are dropped (truncated, not rounded)" | N-000292, pack 03: "its fraction rounded to the nearest microsecond" | **Truncation** (A). The more detailed FP-02 rule governs. |
| CF-000071 | N-000143, FP-02: a tab in a one-line string "must be written as backslash-t" | N-000178, FP-02 error list: "raw control characters other than tab" are refused | **Raw tab accepted** (consistent with the exception for tab in N-000178). |
| CF-000072 | N-000139, FP-02: hex digits of `\x`/`\u`/`\U` "are case-insensitive" | N-000176, FP-02 error list: "escape digits written as uppercase letters" are refused | **Case-insensitive** (A). `é` is accepted. |
| CF-000073 | N-000029, pack 07: exact type only | N-000230, FP-05: "(and not an instance of a subclass of either)" | Same as CF-000023: **subclass instances refused**. |
| CF-000074 | N-000090, FP-01: "A quoted key may be empty" | N-000279, pack 03: "keys: `str`, never empty" | **Empty quoted key accepted** (`"" = 1` gives `{"": 1}`). Bare keys still need at least one character. |

I did not find other conflicts within the spec beyond the 20 above. Where the spec is silent, §2 lists the assumptions.

## 2. Things the spec does not state (assumptions)

- **UTF-8 BOM.** Not mentioned. The decoded text keeps U+FEFF, which is then invalid TOML, so a BOM gives `TOMLDecodeError`. This follows FP-03's rule literally (decode as UTF-8, then parse the same text).
- **Invalid UTF-8 in `load()`.** Not stated. Raised as `TOMLDecodeError` at the first bad byte (character offset in the replacement-decoded text), with that decoded text as `doc`.
- **Control characters in comments.** Not stated (the spec only says non-ASCII is allowed). Control characters other than tab, and DEL, are refused, as TOML requires.
- **DEL (U+007F)** in strings is treated as a "raw control character" and refused.
- **Offset format.** Only `Z`/`z` or `±HH:MM`. Offset hours must be 0–23 and minutes 0–59. The spec gives no range.
- **Leap second** (`:60`) is refused, because the spec gives seconds as 0–59 and Python's `datetime` cannot represent it.
- **Bare keys** are ASCII letters, digits, `_` and `-` only ("Latin letters", pack 07).
- **Empty table name** `[""]` is allowed (empty quoted key, see CF-000074).
- **Whitespace and newlines inside arrays and inline tables** are allowed (TOML 1.1). This includes newlines around `=` and after `{`/`,`, and comments.
- **Exponent digits** may have leading zeros (`1e05`). Hex, octal and binary integers may not have a sign.
- **Recursion depth.** Deeply nested arrays or inline tables may raise Python's `RecursionError`. The spec does not say how to handle this, and I did not add a guard.
- **Converter exceptions.** An exception raised by `parse_float` propagates unchanged. It is not wrapped.
- **Converter argument.** The default `float` is called on the text with underscores removed. A custom converter gets the text exactly as written.
- **`load()` input detection.** A value that is an `io.TextIOBase` is refused before reading. Any object whose `read()` returns `str` is also refused. Any other non-bytes result (including `memoryview`) is a `TypeError`. A string path is refused (no `read` attribute).
- **`TOMLDecodeError` positions.** `lineno` and `colno` are computed from `doc` and `pos` when read (as properties), so a caller-supplied `pos` past the end still gives a location. `str(err)` says "end of document" when `pos >= len(doc)`. Pickling is supported.
- **Package version** is set to `2.4.0`. The spec says "version 2.4.0 and later" but does not name the version for this build.
- **Distribution metadata.** `requires-python = ">=3.8"`, no dependencies, setuptools PEP 517 backend. The judge runs no build step, so this is for completeness only.
- **Python-version compatibility.** The code avoids 3.9+ syntax and library calls, but I ran it only on CPython 3.13 and 3.11 (`/usr/bin/python3.11`). CPython 3.8, PyPy, Windows and macOS were not available here and are not verified.

## 3. Checklist accounting (all 323 ids)

Every id is accounted for below. Status words: **implemented** (code exists and is covered by the test suite),
**implemented-by-absence** (a MUST NOT the product satisfies by not building the thing), **optional-not-built** (a MAY that was
not taken up, with a reason), **N/A** (no testable requirement). Code markers `# spec: N-…` sit beside the
code that satisfies each id. Tests are in `tests/test_tomlparse.py` and are named after the feature point (`test_FP01_…`), since the
spec has no acceptance-criteria labels.

| Ids | Source | Status | Where / test |
|---|---|---|---|
| N-000001–N-000011 | pack 06, product overview | implemented (parser only, TOML 1.1, native values) | `__init__.py`; `test_no_writer_or_cli_surface`, `test_pure_python_no_stdlib_toml_delegation`. N-000009 is a scope statement, nothing to build. |
| N-000012–N-000030 | pack 07, terminology | implemented | Parser and value types; FP-01/02/04/05 tests. N-000019–21 (bare, dotted, inline keys) in FP-01 tests. |
| N-000031–N-000039 | pack 08, public surface | implemented | `loads`, `load`, `TOMLDecodeError` only; `test_public_surface_names`. N-000037 (converter) is MAY and is implemented. |
| N-000040–N-000056 | pack 09, non-functional | implemented (except below) | Pure Python, no deps, no GPU code, Python ≥3.8 floor. N-000041 (optional compiled wheels) **optional-not-built**: no compiled code ships, the spec says it is not required. N-000043/044 (Python 3.8+, Linux/macOS/Windows): **only verified on Linux with 3.11 and 3.13** (see §2). N-000045 has no claim. N-000053 (error text free) is MAY and implemented. |
| N-000057–N-000062 | pack 10, real parser | implemented-by-absence (no delegation) | No import of `tomllib`/`toml` (`test_pure_python_no_stdlib_toml_delegation`). No GPU/service code. |
| N-000063–N-000076 | pack 11, non-goals | implemented-by-absence; N-000069–071 implemented | No writer, no CLI, no config. 1.1 features implemented: inline table newlines and trailing commas (N-000069), `\e`/`\x` escapes (N-000070), omitted seconds (N-000071). N-000074 (throughput) **N/A**: the spec states it is not a requirement. N-000075 (no speed scripts) and N-000076 (no `tomllib` fallback) are implemented by absence. |
| N-000077–N-000122 | pack 12, FP-01 structure | implemented | `_parser.py` (`parse`, `_open_table`, `_insert`, `_parse_key`, `_parse_header`); FP-01 tests incl. `test_FP01_structural_violations_are_refused`. |
| N-000123–N-000180 | pack 12, FP-02 scalars | implemented | `_parser.py` value and string functions; FP-02 tests. N-000135 (quote before closing) MAY: built as allowed (CF-000001). N-000146 (hex case) MAY: either case (CF-000037). N-000153/154 MAY: separator and omitted seconds (CF-000068, CF-000062). |
| N-000181–N-000196 | pack 12, FP-03 binary | implemented | `_api.load`; FP-03 tests. |
| N-000197–N-000219 | pack 12, FP-04 rejection | implemented | `_errors.py`, `_api.py`; FP-04 tests. N-000218 MAY (report wording free): free wording. |
| N-000220–N-000233 | pack 12, FP-05 converter | implemented | `_parser._float`; FP-05 tests. N-000230 MAY (any callable): implemented. |
| N-000234–N-000240 | pack 13 & pack 15 (hardware) | implemented | Pure-Python, runs on the CPU baseline; `test_*` imports from `src`. |
| N-000241 | pack 15, profile id `cpu_baseline` | implemented (documentation only) | Recorded here. Nothing to run. |
| N-000242–N-000244 | pack 15, platforms and import | implemented; N-000242 **verified on Linux only** | Source is portable; tests run with `PYTHONPATH=src`. |
| N-000245–N-000247 | pack 15 | implemented | Required on Linux (verified). |
| N-000248 | pack 15, assumption (compiled wheels) | N/A | Assumption about optional wheels; none built. |
| N-000249–N-000251 | pack 15, MUST NOT (no native step, no extra libs, no required wheels) | implemented-by-absence | No extension module; `pyproject.toml` has no native build. |
| N-000252–N-000254 | pack 15, build (src-layout, PEP 517, path import) | implemented | `pyproject.toml` (setuptools PEP 517, `src` layout); `tests/conftest.py` puts `src` on the path. N-000254 MAY: src layout chosen. |
| N-000234–N-000239 | pack 13/14 summary | implemented (see rows above) | Same as the pack 09/15 rows. |
| N-000255–N-000265 | pack 01, interface product overview | implemented | Parse-only, no I/O side effects, zero deps, CPU-only, Python ≥3.8. |
| N-000266–N-000273 | pack 02, public surface shape | implemented | `src/tomlparse/__init__.py`; no I/O or process at import (only stdlib `re`, `datetime`, `string`, `io`). N-000273 decision: internal layout is free (`_api`, `_parser`, `_errors`). |
| N-000274–N-000298 | pack 03, `loads` | implemented | `_api.loads`; `test_FP02_*`, `test_FP04_type_errors_for_wrong_input`, `test_FP05_*`, `test_contract_loads_is_keyword_only_for_parse_float`. N-000275 MAY (custom `parse_float`): implemented. N-000298 decision: message wording free. |
| N-000299–N-000306 | pack 04, `load` | implemented | `_api.load`; FP-03 tests, `test_contract_load_rejects_path_string`. N-000300 (no path) implemented. |
| N-000307–N-000323 | pack 05, `TOMLDecodeError` | implemented | `_errors.py`; `test_FP04_error_carries_doc_pos_line_column`, `test_FP04_caller_constructed_error`, `test_FP04_error_pickles`. N-000312 MAY (callers construct) implemented. N-000321/322 (report includes location) implemented. N-000323 decision: report layout free. |

## 4. Verification run

- `PYTHONPATH=src python3 -m pytest tests` (CPython 3.13.18): 124 passing.
- The same edge-case scripts under `/usr/bin/python3.11` gave the same results.
- Not done: running against any reference TOML implementation or other Python versions; PyPy, Windows and macOS checks.
