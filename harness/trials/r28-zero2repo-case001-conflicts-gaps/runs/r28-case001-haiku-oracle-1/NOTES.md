# Tomlparse — implementation notes

This file records where the specification in `spec/` disagrees with itself, what
the specification leaves unstated, and how every checklist id is accounted for.
Spec references are `N-` ids from `spec/CHECKLIST.md` and the pack file name
under `spec/packs/`. "Pack 12" is `12-full-prd--feature-points.md`, and so on.

The export was made with `--allow-open`, so all 20 contradictions below are
unsettled (no human verdict). Each one was resolved in the code as stated here.

## Layout

- `src/tomlparse/__init__.py` — public names `loads`, `load`, `TOMLDecodeError`.
- `src/tomlparse/errors.py` — `TOMLDecodeError(msg, doc, pos)`.
- `src/tomlparse/parser.py` — the TOML v1.1.0 parser (pure Python, character-level
  recursive descent). It does not use the standard library's TOML module or any
  other TOML implementation.
- `pyproject.toml` — src-layout metadata, no runtime dependencies, `requires-python >=3.8`.
- `tests/test_tomlparse.py` — 85 tests, one or more per feature point and per
  contradiction decision below.

Run: `cd /app && PYTHONPATH=src python3 -m pytest tests`.

## Contradictions and the choice made

Each entry quotes both sides, says where they are, and states what was built.

### CF-000001 — quote directly before the closing delimiter of a multiline basic string
- A: pack 12, N-000135 (FP-02): "Both multiline forms may contain one or two of their own quote characters next to each other, including directly before the closing delimiter…"
- B: pack 12, N-000178 (FP-02, boundary): "…a quote character directly before the closing delimiter of a multiline basic string".
- **Built:** allowed in both multiline forms (up to two quotes directly before the closing delimiter; `"""x""""` is `x"`). Runs of six or more quotes are refused.

### CF-000008 — line endings inside multiline strings
- A: pack 12, N-000112 (FP-01): a CR LF multiline string "holds line feeds only".
- B: pack 12, N-000133 (FP-02): "Line endings inside a multiline basic string are kept exactly as written, carriage returns included."
- **Built:** A. Every CR LF pair is treated as one LF before parsing (FP-01 and FP-03 both say so), so no CR appears in a value. A bare CR (not part of CR LF) is refused inside multiline basic strings, per FP-02's refusal list.

### CF-000009 — line feed right after the opening delimiter of a multiline literal string
- A: pack 12, N-000130 (FP-02): a multiline literal string "keeps every character after its opening delimiter, including a first line feed".
- B: pack 12, N-000131 (FP-02): "In both multiline forms a line feed immediately after the opening delimiter is discarded".
- **Built:** B, in both multiline forms. `'''\nx'''` is `x`.

### CF-000012 — a header declaring a sub-table of a dotted-key table
- A: pack 07, N-000021 (Terminology, dotted key): "A table created by dotted keys cannot receive a sub-table through a header."
- B: pack 12, N-000098 (FP-01): "a sub-table of it that has not itself been defined may still be declared by a header, as TOML v1.1.0 allows."
- **Built:** B, with A's restriction on the dotted table itself. `[fruit]` / `apple.color = 1` / `[fruit.apple.texture]` is accepted; `[fruit.apple]` after the dotted keys is refused. This matches the TOML specification's own example.

### CF-000015 — whitespace after a line-ending backslash
- A: pack 12, N-000134 (FP-02): the backslash removes "the line ending and all whitespace (spaces, tabs, line feeds) up to the next non-whitespace character".
- B: pack 12, N-000136 (FP-02): "After a line-ending backslash, the next line's leading spaces and tabs are kept."
- **Built:** A (the whitespace is removed). This is the TOML rule.

### CF-000023, CF-000032, CF-000073 — float converter returning a subclass of dict or list
- A: pack 07, N-000029 (Terminology, float converter): "Only a result whose type is exactly `dict` or exactly `list` is refused."
- B: pack 03, N-000296 / pack 08, N-000038 / pack 12, N-000230 and N-000232 (FP-05): refused results include "an instance of a subclass of either", and "dictionaries and lists [are] forbidden as conversion results".
- **Built:** B. The check is `isinstance(result, (dict, list))`, so subclass instances raise `ValueError` (not `TOMLDecodeError`).

### CF-000028, CF-000035, CF-000071 — tab characters in strings
- A: pack 12, N-000141 (FP-02): escapes are never processed in literal keys ("a key written as a literal string does not").
- B: pack 12, N-000143 (FP-02): "A tab in a one-line string must be written as backslash-t."
- C: pack 12, N-000129 (literal strings take no escapes) and N-000178 (refuse "raw control characters other than tab").
- **Built:** a raw tab is allowed in every string form, including literal and multiline strings. Backslash-t remains a valid escape in basic strings. Literal keys are never escape-processed, so `'\t'` is the two characters backslash and t. The "must be written as backslash-t" rule (B) is not applied, because C says tab is not refused and the TOML specification permits raw tabs.

### CF-000037 — hex digits in integers
- A: pack 12, N-000146 (FP-02): "hex digits may be either case".
- B: pack 03, N-000285 (FP-02 return shape): "hexadecimal digits written in lowercase".
- **Built:** A. Input hex digits may be either case. The prefix letter (`0x`, `0o`, `0b`) is lowercase only, as N-000144–N-000147 say. The resulting Python int has no case.

### CF-000072 — case of hex digits in `\x`, `\u`, `\U` escapes
- A: pack 12, N-000139 and N-000146 (FP-02): "Hex digits are case-insensitive."
- B: pack 12, N-000176 (FP-02 boundary): refuses "escape digits written as uppercase letters".
- **Built:** A. `"é"` and `"é"` are both accepted.

### CF-000045, CF-000069 — rounding of fractional seconds
- A: pack 12, N-000156 / N-000157 (FP-02): "the fraction's first six digits are read as microseconds… any digits after the sixth are dropped (truncated, not rounded)".
- B: pack 12, N-000292 (FP-02 return shape): "its fraction rounded to the nearest microsecond".
- **Built:** A (truncation). The rule in N-000157 is the more specific one and states "not rounded" explicitly. `07:32:00.1234569` gives microsecond 123456.

### CF-000059 — trailing comma in arrays
- A: pack 12, N-000106 (FP-01): arrays "end with a trailing comma".
- B: pack 03, N-000282 (return shape): "an array whose last element is followed by a comma is refused".
- **Built:** A. Trailing commas are accepted in arrays, as TOML v1.1.0 allows, and as the non-goals section (pack 11) describes for v1.1.0.

### CF-000062 — omitted seconds in a local time
- A: pack 07, N-000028 (Terminology, local time): "Its seconds are always written."
- B: pack 12, N-000154 (FP-02): "In any value with a time part, seconds may be omitted, in which case the second is 0."
- **Built:** B. `07:32` is a local time of 07:32:00. Pack 11, N-000067 (v1.1.0 accepts "date-times whose seconds are omitted") supports this.

### CF-000065 — signed zero
- A: pack 12, N-000144 (FP-02): "a signed zero is the integer 0".
- B: pack 12, N-000168 (FP-02 refusal list): "a zero with a sign (`+0`, `-0`)".
- **Built:** A. `+0`, `-0` and `0` all give the integer 0.

### CF-000068 — separator between date and time
- A: pack 07, N-000024 (Terminology, offset date-time): "Its date and time are joined by `T` or `t`."
- B: pack 12, N-000153 (FP-02): "The separator between date and time may be `T`, `t`, or a space."
- **Built:** B, applied to every date-time kind. `1979-05-27 07:32:00Z` is accepted. A space is treated as the separator only when a time of digits follows the date, so `d = 1979-05-27 # c` is a plain local date.

### CF-000074 — empty quoted key
- A: pack 12, N-000090 (FP-01): "A quoted key may be empty".
- B: pack 03, N-000279 (return shape): "keys: `str`, never empty".
- **Built:** A. `"" = 1` gives `{"": 1}`. Bare keys still cannot be empty.

## Items the specification does not state (assumptions)

- **Invalid UTF-8 in `load`.** Not specified. The bytes are decoded with `bytes.decode("utf-8")`, so an invalid byte raises `UnicodeDecodeError`, a `ValueError` subclass, not `TOMLDecodeError`. (FP-03 defines the decode error only for valid UTF-8 whose text is not TOML.)
- **Byte-order mark.** A leading U+FEFF is not TOML. It is refused as an invalid character (`TOMLDecodeError`).
- **Control characters in comments.** FP-02 refuses them in strings only. The implementation also refuses U+0000–U+0008, U+000A–U+001F (except LF) and U+007F in comments, as the TOML grammar does. Tab is allowed.
- **Deep nesting.** Recursion is used for nested arrays and inline tables. Very deep input exhausts Python's recursion limit; `RecursionError` is caught and reported as `TOMLDecodeError("document is nested too deeply")`. This is a limit of this implementation (roughly a few hundred levels), not a TOML rule. The spec says every document TOML allows must be accepted, so this is a known gap.
- **Integers beyond Python's decimal-string digit limit.** `int()` refuses very long decimal strings in newer Pythons; the failure is reported as `TOMLDecodeError`. Hex, octal and binary have no such limit.
- **Calendar and time ranges.** Dates use Python's `datetime.date` (years 1–9999; `0000-…` is refused). Hours must be 0–23, minutes and seconds 0–59 (leap second 60 refused, following FP-02). Offsets must have hours ≤ 23 and minutes ≤ 59.
- **Float range.** Values too large for a float (for example `1e400`) become `inf` through `float()`. The default converter does not refuse them.
- **Converter call details.** The converter is called once per float, in document order, with the token text (including underscores, sign and exponent). Its exceptions propagate unchanged. A `None` or other non-dict/list result is stored as returned.
- **Error text.** Wording is free (FP-04, N-000218). Format used: `"<msg> (line L, column C)"`, or `"<msg> at end of document (line L, column C)"` when `pos >= len(doc)`. Line and column count code points, not bytes. For CR LF input, `pos` indexes the original text, so it points at the right character in `err.doc`.
- **Pickling.** `TOMLDecodeError` defines `__reduce__`, so copy and pickle rebuild it from `(msg, doc, pos)`.
- **Table rules that the spec describes only in prose.**
  - Dotted keys may extend only tables that dotted keys created, and never implicit super-tables created by a header (FP-01: "provided that such tables were not previously created").
  - A header may define an implicit super-table once, and may not define a table already defined by a header, dotted keys, or an inline table.
  - Static arrays and inline tables cannot be extended by a header or by dotted keys.
- **Input types.** `loads` accepts any `str` (including subclasses) and refuses everything else with `TypeError`. `load` refuses an object that is a `io.TextIOBase`, or whose `read()` returns `str`, with `TypeError` before any decoding. It accepts `bytes`, `bytearray` and `memoryview` results from `read()`. `load` calls `read()` once and does not seek.
- **Keyword-only `parse_float`.** Both entries take it keyword-only, as in the signature (pack 03).
- **Python versions and platforms.** Written to Python 3.8+ syntax (no `match`, no `str.removeprefix`, no PEP 604 hints). Tested here only on CPython 3.13 (Linux). macOS, Windows and Python 3.8–3.12 were not run.
- **Packaging build.** `pyproject.toml` declares a setuptools PEP 517 backend. No wheel was built here because `setuptools` is not installed in this environment and there is no network access. The package imports directly from `src/` with `PYTHONPATH=src`, which is what the judge uses.
- **Lone surrogates in a Python `str` input.** Not refused. The spec is about TOML text, and a `str` can carry surrogates without going through UTF-8 decoding. This is unspecified.
- **Empty document after `load`.** A zero-byte stream yields `{}` (pack 04, N-000303).

## Checklist accounting

`spec/` is left untouched, as required. The checklist is accounted for here, not by
ticking boxes in `spec/CHECKLIST.md`. Every id from `N-000001` to `N-000323` falls
into one of three states:

- **implemented** — the behaviour is in `src/tomlparse/`;
- **tested** — there is a test in `tests/test_tomlparse.py` for the behaviour;
- **by absence / by design** — a MUST NOT or a platform/packaging statement met by what the code does not contain.

The per-id code locations are in the `# spec:` comments in `errors.py`, `parser.py`
(entry points and `_open_table`), and in the test names. Ranges map to these sections:

| Ids | Pack / section | Where it is met | Tested by |
|---|---|---|---|
| N-000001–N-000005 | 06 product overview (parser only; TOML v1.1.0) | `parser.py` (whole module); no writer or dump API in `__init__.py` | `test_public_names_importable_from_root`; spec-style example test |
| N-000006–N-000011 | 06 (feature scope; integrator gets native values; doc scope) | `parser.py` returns plain `dict`/`list`/scalars | all `test_*` structure tests |
| N-000012–N-000030 | 07 terminology (bare/dotted/inline keys, table kinds, date kinds, float converter, decode error) | `parser.py` `_key`, `_insert`, `_open_table`, `_datetime`, `_local_time`, `errors.py` | `test_dotted_*`, `test_inline_*`, `test_offset_*`, `test_local_*`, `test_converter_*` |
| N-000031–N-000039 | 08 public surface (library only; loads, load, decode error; no extra surfaces) | `__init__.py` `__all__` | `test_public_names_importable_from_root`, `test_load_*` |
| N-000040–N-000056 | 09 non-functional (zero deps, Python 3.8+, Linux/macOS/Windows, CPU-only, v1.1.0, result types, error text) | `pyproject.toml` (`dependencies = []`, `requires-python >=3.8`); no OS-specific code | Python 3.13/Linux only (see Assumptions) |
| N-000057–N-000062 | 10 real parser (no delegation to stdlib tomllib; CPU-only) | `parser.py` is the whole parser; no `tomllib` import | cross-checked against `tomllib` in scratch only, not shipped |
| N-000063–N-000076 | 11 non-goals (no writer; not v1.0.0-only; no CLI/service/config; no fallback import) | absence of writer/CLI/config code; v1.1.0 features accepted (trailing commas, `\e`, `\x`, omitted seconds, newlines in inline tables) | `test_inline_table_multiline_comments_trailing_comma`, `test_seconds_may_be_omitted`, `test_basic_string_escapes_all_forms` |
| N-000077–N-000122 | 12 FP-01 document structure | `parser.py` `parse`, `_keyval`, `_insert`, `_open_table`, `_header`, `_array`, `_inline_table`, `_wcn`, `_comment` | `test_root_and_table_pairs`, `test_dotted_*`, `test_super_*`, `test_array_of_tables_*`, `test_inline_*`, `test_duplicate_keys_refused`, `test_header_unclosed_*` |
| N-000123–N-000161 | 12 FP-02 scalars (booleans, strings, escapes, integers, floats, date-times, fractions, valid calendar dates, copy/compare) | `parser.py` `_value`, `_scalar`, `_multiline`, `_escape`, `_int`, `_float`, `_datetime`, `_local_time` | `test_booleans_*`, `test_*escape*`, `test_multiline_*`, `test_integers_*`, `test_floats_*`, `test_*datetime*`, `test_fraction_*`, `test_leap_day_accepted`, `test_datetime_values_copy_and_compare` |
| N-000162–N-000180 | 12 FP-02 refusals (invalid booleans, integers, floats, escapes, control characters, unclosed strings, invalid calendar/time values) | `parser.py` (error branches of the above) | `test_integer_leading_zero_and_bad_underscores_refused`, `test_floats_without_digits_on_both_sides_refused`, `test_bad_escapes_refused`, `test_raw_control_characters_refused_in_strings`, `test_unclosed_strings_refused`, `test_invalid_calendar_and_time_values_refused` |
| N-000181–N-000196 | 12 FP-03 binary file entry | `parser.load` | `test_load_*`, `test_binary_error_doc_is_decoded_text`, `test_invalid_utf8_in_load_is_not_silently_accepted` |
| N-000197–N-000219 | 12 FP-04 reject invalid TOML (decode error, location, type errors, message free) | `errors.py`, `parser._error` (CR LF mapping) | `test_decode_error_is_value_error_not_type_or_recursion`, `test_error_location_*`, `test_constructed_error_*`, `test_error_offsets_map_back_to_crlf_text`, `test_loads_refuses_non_str_with_type_error` |
| N-000220–N-000233 | 12 FP-05 float converter (called for every float with text as written; no dict/list results) | `parser._float` | `test_converter_*` |
| N-000234–N-000235 | 13 hardware (CPU baseline, no fallback substitute) | pure Python; no native code | by design |
| N-000236–N-000239 | 14 summary (default path has no compiled extensions or deps; interpreter floor 3.8) | pure Python; `pyproject.toml` | by design; not run on 3.8 |
| N-000240–N-000254 | 15 execution profile (cpu_baseline; src-layout; PEP 517; import from source tree) | `src/tomlparse/`, `pyproject.toml` | `PYTHONPATH=src` test runs; wheel build not run (see Assumptions) |
| N-000255–N-000265 | 01 product overview (library, not CLI/service; no dump/write; pure Python, zero deps, CPU-only, Python 3.8+, Linux/macOS/Windows) | as for N-000001–N-000056 | as above |
| N-000266–N-000273 | 02 public surface shape (package `tomlparse` under `src`; import does no I/O; names from package root; layout is implementer's choice) | `src/tomlparse/__init__.py` | `test_public_names_importable_from_root` |
| N-000274–N-000298 | 03 `loads` (signature; return shape; failures; message wording free) | `parser.loads` | `test_loads_*`, `test_*` shape tests, `test_converter_*` |
| N-000299–N-000306 | 04 `load` (binary file; no path; empty file; text mode TypeError; decode error doc is text) | `parser.load` | `test_load_*`, `test_binary_error_doc_is_decoded_text` |
| N-000307–N-000323 | 05 `TOMLDecodeError` (ValueError subclass; msg/doc/pos; lineno/colno; report text) | `errors.py` | `test_decode_error_*`, `test_constructed_error_*`, `test_error_*` |

Ids with no direct test: N-000041 and N-000248 (optional compiled wheels, `MAY`; not built, which the spec allows), N-000045 and N-000242 (platform list; not run outside Linux here), N-000253 (build backend; not run here), and N-000321–N-000322 (report text; covered by `test_error_at_end_of_document_mentions_end` and `test_error_location_attributes_for_interior_offset`). None of these is a missing feature.

## Decisions (ids N-000273, N-000298, N-000323)

- **N-000273 (module layout):** `tomlparse/errors.py`, `tomlparse/parser.py`, `tomlparse/__init__.py`.
- **N-000298 (TypeError/ValueError wording):** free text, as stated in the message strings in `parser.py`.
- **N-000323 (decode-error report wording):** `"<msg> (line L, column C)"`, or `"... at end of document (...)"`. Attribute names follow the spec exactly.
