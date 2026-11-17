# Tomlparse — implementation notes

Layout (src layout, zero runtime dependencies, pure Python):

- `src/tomlparse/__init__.py` — public names `loads`, `load`, `TOMLDecodeError`; `__version__ = "2.4.0"`.
- `src/tomlparse/_api.py` — `loads` (text entry) and `load` (binary file entry).
- `src/tomlparse/_parser.py` — hand-written TOML v1.1.0 parser. It does not use the standard library `tomllib` (N-000058, N-000076).
- `src/tomlparse/_errors.py` — `TOMLDecodeError(msg, doc, pos)`, a subclass of `ValueError`.
- `pyproject.toml` — PEP 517 (setuptools) metadata, src layout, `requires-python >=3.8`, no dependencies.
- `tests/test_tomlparse.py` — pytest suite, named after feature points (`test_FP_01_…`) and the interface contract (`test_IC_…`).

Run: `cd /app && PYTHONPATH=src python3 -m pytest -q tests` (116 passed on Python 3.13 / Linux).

Spec files were read in full: `spec/packs/01`–`15`. The `spec/` directory was not modified.

## 1. Conflicts between spec parts

The export was made with `--allow-open`, and `spec/MAP.md` lists 16 unsettled contradictions. Each one is listed below with both sides quoted, its location, and what was built. Where a conflict is about the same behaviour in two places, the choice follows the TOML v1.1.0 language and the more specific PRD statement.

**CF-000001 — quote directly before the closing `"""`.**
- A: N-000135 (`spec/packs/12`, FP-02 multiline strings): "Both multiline forms may contain one or two of their own quote characters next to each other, including directly before the closing delimiter…"
- B: N-000178 (FP-04): "a quote character directly before the closing delimiter of a multiline basic string" is refused.
- Built: A. `"""a""""` gives `a"`; up to two quotes may precede the closing delimiter (a run of 3–5 quotes closes the string).

**CF-000008 — carriage returns in multiline strings.**
- A: N-000112 (FP-01): a CRLF pair "is treated as a single line feed everywhere, including inside string values: a multiline string written with carriage-return/line-feed line endings holds line feeds only."
- B: N-000133 (FP-02): "Line endings inside a multiline basic string are kept exactly as written, carriage returns included."
- Built: A. CRLF inside a multiline string is read as `\n`. A lone CR (not followed by LF) is refused everywhere (N-000178).

**CF-000009 — first line feed of a multiline literal string.**
- A: N-000130 (FP-02): "A multiline literal string keeps every character after its opening delimiter, including a first line feed."
- B: N-000131 (FP-02): "In both multiline forms a line feed immediately after the opening delimiter is discarded."
- Built: B for both multiline forms (TOML behaviour).

**CF-000012 — sub-tables of a table created by dotted keys.**
- A: N-000021 (FP-01 terminology, pack 07 row "Dotted key"): "A table created by dotted keys cannot receive a sub-table through a header."
- B: N-000098 (FP-01): "After dotted keys have created a nested table, a sub-table of it that has not itself been defined may still be declared by a header, as TOML v1.1.0 allows."
- Built: B. A header may declare a sub-table that is not yet defined under a dotted-key table. Reopening a dotted-key table *itself* by a header is refused (N-000113–N-000122).

**CF-000015 — leading whitespace after a line-ending backslash.**
- A: N-000134 (FP-02): the backslash "removes the line ending and all whitespace (spaces, tabs, line feeds) up to the next non-whitespace character or the closing delimiter."
- B: N-000136 (FP-02): "After a line-ending backslash, the next line's leading spaces and tabs are kept."
- Built: A (whitespace removed), the TOML behaviour.

**CF-000023 / CF-000032 — dict or list subclasses returned by a float converter.**
- A: N-000029 (pack 07 Terminology, "Float converter"): "Only a result whose type is exactly `dict` or exactly `list` is refused." (The glossary and FP-05 differ on this; see B.)
- B: N-000296 (Interface Contract, `loads` failures table), N-000038 (PRD, FP-05 summary), N-000230–N-000233 (FP-05): a dict or list result, "or a subclass instance", raises `ValueError`; the FP-05 text says "not an instance of a subclass of either".
- Built: B. Any `dict`/`list` instance, including subclasses, raises a plain `ValueError` (not `TOMLDecodeError`).

**CF-000028 / CF-000035 — tab characters in literal strings.**
- A: N-000141 / N-000129: escapes (and therefore `\t`) are never processed in literal strings.
- B: N-000143 (FP-02): "A tab in a one-line string must be written as backslash-t." Also N-000178 excludes tab from the refused control characters.
- Built: a raw tab is accepted in every string form (basic, literal, multiline) and in comments. `\t` is still accepted in basic strings. Literal strings do not process escapes. N-000143 is therefore not enforced as a refusal.

**CF-000037 — case of hexadecimal digits.**
- A: N-000146 (FP-02): "hex digits may be either case" (also N-000139 for escapes, "Hex digits are case-insensitive").
- B: N-000285 (Interface Contract, `loads` return shape): "hexadecimal digits written in lowercase".
- Built: A. Both upper and lower hex digits are accepted in `0x` integers and in `\x`, `\u`, `\U` escapes. The prefix itself must be lowercase (`0x`, `0o`, `0b`, N-000145). The integer value does not depend on digit case.

**CF-000045 / CF-000069 — fractional seconds beyond six digits.**
- A: N-000156–N-000157 (FP-02): "the fraction's first six digits are read as microseconds … any digits after the sixth are dropped (truncated, not rounded)."
- B: N-000292 (Interface Contract, local time): "its fraction rounded to the nearest microsecond."
- Built: A (truncation). The PRD FP-02 text states the rule more precisely than the contract summary does.

**CF-000059 — trailing comma in arrays.**
- A: N-000106 (FP-01): arrays "end with a trailing comma" (MAY).
- B: N-000282 (Interface Contract): "an array whose last element is followed by a comma is refused."
- Built: A. Trailing commas are accepted in arrays and inline tables (TOML 1.1). Inline tables may also contain line breaks and comments (N-000104).

**CF-000062 — seconds in local times.**
- A: N-000028 (pack 07 Terminology, "Local time"): "Its seconds are always written."
- B: N-000154 (FP-02): "In any value with a time part, seconds may be omitted, in which case the second is 0."
- Built: B. `07:32` is a local time with second 0 (TOML 1.1, and the non-goals text in N-000071 names "date-times whose seconds are omitted").

**CF-000065 — signed zero.**
- A: N-000144 (FP-02): "a signed zero is the integer 0."
- B: N-000168 (FP-02 error list): "a zero with a sign (`+0`, `-0`)" must not be accepted.
- Built: A. `+0` and `-0` are integer 0. Leading zeros (`01`, `-01`) are still refused.

**CF-000068 — separator between date and time of an offset date-time.**
- A: N-000024 (pack 07 Terminology, "Offset date-time"): "Its date and time are joined by `T` or `t`."
- B: N-000153 (FP-02): "The separator between date and time may be `T`, `t`, or a space."
- Built: B. A space is accepted for offset and local date-times alike (`1979-05-27 07:32:00Z`).

**Other contradictions found but not listed in MAP.md.** None beyond the above, apart from the following two minor items:
- *Error-kind wording:* N-000053 (FP-02) says decode errors are "a kind of value error", and N-000217 (FP-04) says a decode error "is not a recursion error and not a type error." Both are honoured. Deep nesting is reported as a decode error (section 2).
- *Version scope:* N-000004 (PRD) says "Version 2.4.0 and later … compatible with TOML v1.1.0", so `__version__` is set to `2.4.0`.

## 2. Things the spec does not state (assumptions)

- **Invalid UTF-8 in `load`.** Not stated; FP-03 only covers valid UTF-8. Built: `TOMLDecodeError` (a document error), with `doc` = the bytes decoded with replacement characters and `pos` = the character index of the first bad byte.
- **Byte-order mark.** Not stated. A leading U+FEFF is not whitespace in TOML and is refused (it is read as the start of a key, so the error is "expected key").
- **Control characters.** TOML forbids all of U+0000–U+001F except tab, LF and CR-LF, plus DEL. The spec mentions only strings explicitly (N-000178). Built: these characters are refused everywhere (in strings, comments and between tokens); lone CR and surrogate code points in a `str` are refused too.
- **Nesting depth.** Not stated. The parser is recursive; deeper nesting than the interpreter's stack allows is reported as `TOMLDecodeError("document is nested too deeply")` rather than a `RecursionError` (N-000217). About 500 levels of nesting is the practical limit.
- **Year 0000.** TOML allows 0000–9999 but Python's `date` starts at year 1. Built: year 0000 is a calendar-date failure (decode error).
- **Time and offset ranges.** Hours 0–23, minutes and seconds 0–59 (N-000180); leap second `:60` is refused. Offsets: hours 0–23, minutes 0–59 (not stated; chosen to keep `timezone` constructible).
- **Empty keys.** Empty quoted keys are allowed (N-000089). An empty bare key is refused.
- **Dotted keys into implicit tables.** A table that exists only because a header declared a sub-table (for example `[a.b.c]` creates `a` and `a.b`) can later receive dotted keys (`b.x = 1` under `[a]`). The spec says dotted keys may extend implicitly created tables (N-000095) but does not name this case; the rule was applied.
- **Converter exceptions.** An exception raised by the caller's `parse_float` is propagated unchanged.
- **Non-callable `parse_float`.** Not checked; the call fails with the usual `TypeError`.
- **`load` input.** A path or any value without `read()` raises `TypeError`, since `load` never takes a path (N-000299). A text-mode file is detected with `io.TextIOBase`; a file whose `read()` returns `str` is refused the same way.
- **Text of `TOMLDecodeError.__str__`.** Interior offsets give `reason (at line L, column C)`; offsets at or past the end give `reason (at end of document)`. Wording is free (N-000218).
- **Pickling.** `TOMLDecodeError` pickles and unpickles with its three constructor arguments (not in the spec; added for convenience).

## 3. Checklist accounting (`spec/CHECKLIST.md`, 323 ids)

Every id is accounted for below by pack and range. "Implemented" means code carries a `# spec: <id>` marker (the markers are at function level in `_parser.py`, `_api.py`, `_errors.py` and `__init__.py`). "Tested" means the named test in `tests/test_tomlparse.py` exercises it.

| Ids | Pack | Status | Where / test |
| --- | --- | --- | --- |
| N-000001–N-000011 | 06 product overview | implemented | parser-only API; no writer (N-000032) |
| N-000012–N-000030 | 07 terminology | implemented | parser `_value`, `_simple_key`, `_make_datetime`, `_float`; tests `test_FP_01_*`, `test_FP_02_*` |
| N-000031–N-000039 | 08 public surface | implemented | `__init__.py`; `test_IC_public_names_importable_from_root` |
| N-000040–N-000044 | 09 constraints (packaging) | implemented | `pyproject.toml` (`dependencies = []`, `requires-python >=3.8`); Linux only tested |
| N-000045–N-000047 | 09 hardware | implemented | CPU-only pure Python; no claim made |
| N-000048–N-000056 | 09 non-functional | implemented | source tree import; result types are `dict`/`list`/`str`/`int`/`float`/`bool`/`datetime`; error text free |
| N-000057–N-000062 | 10 real parser | implemented | `_parser.py`; no tomllib (`test_IC_no_tomllib_dependency`) |
| N-000063–N-000076 | 11 non-goals | implemented (absence) | no writer, no CLI, no tomllib fallback. N-000074 (throughput) is a non-goal with no requirement, so nothing to build |
| N-000077–N-000079 | 12 FP-01 entry | implemented | `_api.loads`; `test_FP_01_*` |
| N-000080–N-000122 | 12 FP-01 structure and errors | implemented | `_parser.py` (`parse`, `_header`, `_walk_header`, `_walk_dotted`, `_keyval`, `_dotted_key`, `_simple_key`, `_inline_table`, `_array`); `test_FP_01_*`, `test_FP_01_structural_violations_are_decode_errors` |
| N-000123–N-000162 | 12 FP-02 scalars | implemented | `_value`, `_number_or_date`, `_make_datetime`, `_time_fields`, `_basic_string`, `_literal_string`, `_multiline_string`, `_escape`; `test_FP_02_*` |
| N-000163–N-000180 | 12 FP-02 refusals | implemented | `_parser.py`; `test_FP_02_bad_*` |
| N-000181–N-000196 | 12 FP-03 binary entry | implemented | `_api.load`; `test_FP_03_*` |
| N-000197–N-000219 | 12 FP-04 decode error | implemented | `_errors.py`, `_api.py`; `test_FP_04_*` |
| N-000220–N-000233 | 12 FP-05 converter | implemented | `_parser._float`, `_api`; `test_FP_05_*` |
| N-000234–N-000254 | 13–15 hardware and profiles | implemented, see below | `pyproject.toml`; source-tree import |
| N-000255–N-000265 | 01 product overview | implemented | `__init__.py`, `_api.py`; no I/O at import |
| N-000266–N-000273 | 02 public surface | implemented | `__init__.py`; `test_IC_*` |
| N-000274–N-000298 | 03 `loads` | implemented | `_api.loads`; `test_FP_01`, `test_FP_02`, `test_FP_05`, `test_FP_04_wrong_python_type_is_type_error` |
| N-000299–N-000306 | 04 `load` | implemented | `_api.load`; `test_FP_03_*` |
| N-000307–N-000323 | 05 `TOMLDecodeError` | implemented | `_errors.py`; `test_FP_04_constructed_error_carries_values_and_location`, `test_FP_04_location_fields_and_line_column_rule` |

**Not done, with reasons:**
- **N-000241** (`cpu_baseline` profile id, a label in the Hardware spec): recorded here and in the spec; there is no code element that uses it.
- **N-000242** (platforms linux, darwin, windows): the code is portable pure Python, but only Linux was run in this environment. macOS and Windows are not verified.
- **N-000248** (assumption that optional compiled wheels exist): not applicable. No compiled extension was built, so no wheel exists.
- **N-000074** (throughput guarantee): a non-goal with no requirement; nothing to build.
- **N-000045** (constraint without modality or layer): no testable content.

Not verified here: Python 3.8 and PyPy (only 3.13 is installed), macOS, Windows, and the PEP 517 build (the package was not built into a wheel).
