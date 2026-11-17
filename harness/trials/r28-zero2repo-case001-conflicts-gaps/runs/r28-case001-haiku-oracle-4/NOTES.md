# Notes

Implementation of `tomlparse` (TOML v1.1.0 parser) from `spec/`.

- Package: `src/tomlparse/` (`__init__.py`, `_api.py` for `loads`/`load`, `_parser.py` for the grammar and document builder, `_errors.py` for `TOMLDecodeError`).
- Tests: `tests/test_tomlparse.py` (53 tests). Run from `/app`: `PYTHONPATH=src python3 -m pytest -q tests` (or `python3 -m unittest discover -s tests`).
- Packaging: `pyproject.toml`, setuptools, src layout. Nothing needs to be built for the judge.
- Verified here on CPython 3.13 only. Source passes an `ast` parse with `feature_version=(3,8)`. Python 3.8, PyPy, macOS and Windows were not run.

## Conflicts

The export was made with `--allow-open`, and 20 contradictions are unsettled (CF ids below). For each one I chose a side. "Chosen" is the claim I built to. "Rejected" is the claim I did not build to. Locations are the pack file and claim id.

1. **CF-000001: quote directly before a multiline closing delimiter.**
   - Chosen: N-000135 (`pack 12`, FP-02 "Both multiline forms may contain one or two of their own quote characters ... including directly before the closing delimiter"). `"""a""""` is `a"`. Runs of 3 to 5 closing quotes are accepted; 6 or more are refused.
   - Rejected: N-000178 (`pack 12`, FP-02 refusal list: "a quote character directly before the closing delimiter of a multiline basic string").

2. **CF-000008: CRLF inside multiline strings.**
   - Chosen: N-000111/N-000112 (`pack 12`, FP-01: a CRLF pair is one line feed everywhere, "holds line feeds only"). Every CRLF in a multiline string becomes `\n`.
   - Rejected: N-000133 (`pack 12`, FP-02: "carriage returns included" kept as written).

3. **CF-000009: newline right after the opening delimiter of a multiline literal string.**
   - Chosen: N-000131 (`pack 12`, FP-02: "In both multiline forms a line feed immediately after the opening delimiter is discarded"). This matches the TOML grammar.
   - Rejected: N-000130 (`pack 12`, FP-02: multiline literal "keeps ... including a first line feed").

4. **CF-000012 (also N-000021 vs N-000098): header below a dotted-key table.**
   - Chosen: N-000098 (`pack 12`, FP-01: a sub-table of a dotted-key table that has not been defined may be declared by a header, "as TOML v1.1.0 allows"). `[fruit.apple.texture]` after `fruit.apple.color = ...` is valid. A header naming a table that dotted keys already defined, such as `[fruit.apple]`, is refused.
   - Rejected: N-000021 (`pack 07`, "cannot receive a sub-table through a header").

5. **CF-000015: whitespace at the start of the line after a line-ending backslash.**
   - Chosen: N-000134 (`pack 12`, FP-02: the backslash removes the line ending and all whitespace up to the next non-whitespace character). This matches the TOML grammar.
   - Rejected: N-000136 (`pack 12`, FP-02: "the next line's leading spaces and tabs are kept").

6. **CF-000023, CF-000032, CF-000073 (also N-000029, N-000038, N-000230, N-000296): converter results that are dict or list subclasses.**
   - Chosen: refuse any result that is an instance of `dict` or `list`, subclasses included (N-000230, N-000296; the FP-05 body "not an instance of a subclass of either").
   - Rejected: N-000029 (`pack 07` and `pack 12` terminology, "only a result whose type is exactly dict or exactly list is refused").

7. **CF-000028 and CF-000035 (also N-000141, N-000129 vs N-000143): tabs in literal keys and strings.**
   - Chosen: a raw tab is allowed in every string form and in literal keys. Escapes are not processed in literal strings or literal keys. N-000178 (refuse control characters other than tab) and the TOML grammar are consistent with this.
   - Rejected: N-000143 ("A tab in a one-line string must be written as backslash-t").

8. **CF-000037 and CF-000072 (also N-000146, N-000139, N-000176 vs N-000285): hex digits.**
   - Chosen: integer hex digits may be upper or lower case (N-000146). `\x`, `\u` and `\U` escape digits are case-insensitive (N-000139). The "lowercase" rule (N-000285) is read as applying to the prefix letters only (`0x`, `0o`, `0b`), which N-000144 also states.
   - Rejected: N-000285 applied to hex digits; N-000176 (refuse uppercase escape digits).

9. **CF-000045 and CF-000069 (also N-000156/N-000157 vs N-000292): fractional seconds.**
   - Chosen: N-000156/N-000157 (`pack 12`, FP-02: first six digits are microseconds, padded on the right, and anything after the sixth is dropped, "truncated, not rounded"). The FP-02 rule is more detailed than the Interface Contract's one-line "rounded" rule.
   - Rejected: N-000292 (`pack 03`, "its fraction rounded to the nearest microsecond").

10. **CF-000059 (also N-000106 vs N-000282): trailing comma in arrays.**
    - Chosen: N-000106 (`pack 12`, FP-01: arrays "end with a trailing comma"). TOML v1.1.0 allows it. `[1, 2,]` parses to `[1, 2]`.
    - Rejected: N-000282 (`pack 03`, "an array whose last element is followed by a comma is refused").

11. **CF-000062 (also N-000154 vs N-000028): seconds in local time.**
    - Chosen: N-000154 (`pack 12`, FP-02: "in any value with a time part, seconds may be omitted"). `07:32` is a valid local time with second 0.
    - Rejected: N-000028 (`pack 07`, local time "Its seconds are always written").

12. **CF-000065 (also N-000144 vs N-000168): signed zero.**
    - Chosen: N-000144 (`pack 12`, FP-02: "a signed zero is the integer 0"). `+0` and `-0` both parse to `0`.
    - Rejected: N-000168 (`pack 12`, refuse "a zero with a sign").

13. **CF-000068 (also N-000024 vs N-000153): separator in date-times.**
    - Chosen: N-000153 (`pack 12`, FP-02: the separator "may be `T`, `t`, or a space"). The rule applies to every date-time kind, offset and local, with `T`, `t` or a space.
    - Rejected: N-000024 (`pack 07`, "joined by `T` or `t`").

14. **CF-000074 (also N-000090 vs N-000279): empty quoted key.**
    - Chosen: N-000090 (`pack 12`, FP-01: "a quoted key may be empty"). `"" = 1` parses to `{"": 1}`, and `[""]` is a valid table name.
    - Rejected: N-000279 (`pack 03`, "keys: `str`, never empty"). Keys are still always `str`.

## Assumptions (not stated in the spec)

- **Invalid UTF-8 in `load`:** the spec defines only the valid-UTF-8 path. Invalid bytes raise `TOMLDecodeError`. Its `doc` is the input decoded with `errors="replace"`, and `pos` is the character offset of the first bad byte.
- **Byte order mark:** a leading U+FEFF is not stripped. It is an invalid character and raises `TOMLDecodeError`.
- **`load` with a non-file:** an object with no `read` method raises `TypeError`.
- **`load` and text mode:** the text-mode check is done after `read()`. A text-mode file object is read once and refused.
- **Error text:** `str(err)` is `"<msg> (at line L, column C)"`, or `"<msg> (at end of document, line L, column C)"` when `pos >= len(doc)`. The attributes `msg`, `doc`, `pos`, `lineno`, `colno` are set on every instance, raised or constructed.
- **`TOMLDecodeError` positions:** `pos` is a character index into the original text, so CRLF input reports the same offsets the caller sees. `doc` is always the text as given (CRLF not normalized).
- **Lone carriage return:** refused everywhere except as the first half of a CRLF pair.
- **Control characters in comments:** refused, except tab. Non-ASCII text is allowed.
- **Datetime details:** lowercase `t` and `z` are accepted. Offset hours must be 0 to 23 and minutes 0 to 59. Seconds 60 (leap second) is refused, since the spec gives second range 0 to 59. Time-only values take no offset.
- **Basic-key escapes:** basic quoted keys process escapes. Literal quoted keys do not.
- **Nesting depth:** the parser is recursive. Very deep nesting raises `RecursionError`, which is not a `TOMLDecodeError`. The spec does not say what to do.
- **Surrogates in input text:** a raw surrogate code point in a Python `str` is not checked. Surrogate escapes (`\uD800`) are refused.
- **Converter called on floats only:** the converter gets only float tokens, including the special spellings. Its exceptions propagate unchanged.
- **Converter text:** the converter receives the float token exactly as written, including the sign, underscores and exponent.
- **`__version__`:** `"2.4.0"`, from the PRD ("Version 2.4.0 and later ... compatible with TOML v1.1.0").
- **Module layout:** `_errors.py`, `_parser.py`, `_api.py`. The spec allows any internal layout (N-000273, N-000298, N-000323).
- **Dict key order:** dict insertion order follows document order.

## Coverage of `spec/CHECKLIST.md`

Every id ends as **implemented** (code and, for behavior, a test in `tests/test_tomlparse.py`) or as **not done** with a reason. Ids are grouped by pack. The `# spec:` comments in the source name the ids each code block satisfies.

Pack 01 (N-000255 to N-000265), product overview: **implemented.** Parser-only. No writer, no CLI, no `__main__`, no configuration. Pure Python, no runtime dependencies, CPU-only. Platform (N-000264) and Python 3.8+ (N-000263) are implemented in the code but only verified on CPython 3.13 Linux.

Pack 02 (N-000266 to N-000273), public surface: **implemented.** Src layout (`src/tomlparse`). Importing does no I/O. `loads`, `load`, `TOMLDecodeError` exported from the package root. N-000273 is a decision left to the implementer; the layout is recorded above.

Pack 03 (N-000274 to N-000298), `loads`: **implemented.** Positional `s`, keyword-only `parse_float`, return shape, failures. Trailing-comma and float-converter conflicts are resolved as in the conflicts list. N-000275 (`parse_float` optional, MAY) is implemented.

Pack 04 (N-000299 to N-000306), `load`: **implemented.** Binary file read, UTF-8, text-mode refusal (`TypeError`), converter, empty file gives `{}`.

Pack 05 (N-000307 to N-000323), `TOMLDecodeError`: **implemented.** `ValueError` subclass, not `TypeError` or `RecursionError`. Constructor `(msg, doc, pos)`, attributes, formatted report. N-000321 is a MUST with no layer assigned; it is covered by the report format and a test.

Pack 06 (N-000001 to N-000011), product overview: **implemented.** Parser only, TOML v1.1.0.

Pack 07 (N-000012 to N-000030), terminology: **implemented.** Bare keys, dotted keys (dots inside quotes are not separators), inline-table freezing, date-time kinds, float converter, decode error as a `ValueError`. N-000021 (`pack 07`, dotted-table sub-table rule) follows conflict item 4.

Pack 08 (N-000031 to N-000039), public surface inventory: **implemented.** Library only. The four surface groups (parse text, scalars, binary file, errors, converter) are implemented. N-000038 (converter results cannot be dict or list) is implemented per conflict item 6.

Pack 09 (N-000040 to N-000056), non-functional constraints: **implemented, with two items not done.**
- N-000041 (MAY, optional compiled wheels for speed): **not done**, MAY, and the spec says the pure-Python parser is the product.
- N-000053 (MAY, error wording free): implemented by choice. The message text is ours, and the tests check only exception kind and location.
- Otherwise implemented: zero dependencies, Python 3.8+ intended, Linux/macOS/Windows intended (only Linux verified), CPU-only, TOML v1.1.0.

Pack 10 (N-000057 to N-000062), real parser: **implemented.** The parser is ours and does not call `tomllib` or any other TOML parser. No GPU, accelerator or extra service.

Pack 11 (N-000063 to N-000076), non-goals: **implemented** as non-goals. No dump/write/encode, no round-trip, no v1.0.0-only behavior (v1.1.0 features accepted: newlines and trailing commas in inline tables, `\e` and `\xHH`, omitted seconds), no CLI, no throughput guarantee (N-000074, no requirement), no speed scripts or fuzzer shipped (N-000075), no fallback to `tomllib` (N-000076). N-000066 (a successful parse is plain builtin and standard-library values) is implemented.

Pack 12 (N-000077 to N-000233), feature points FP-01 to FP-05: **implemented**, with the conflicts above resolved as stated. Tests cover structure (FP-01), scalars (FP-02), binary file (FP-03), errors and location (FP-04), converter (FP-05). The fuzzer used during development was not kept; it found no unexpected exception type across 200,000 random short inputs.

Pack 13 (N-000234 to N-000235), hardware requirements: **implemented.** CPU-only, pure Python, no mandatory fallback.

Pack 14 (N-000236 to N-000239), hardware summary: **implemented.** Pure Python, no compiled extensions, no runtime third-party dependencies, Python 3.8+ intended. N-000239 (optional compiled wheels not required) is satisfied by having none.

Pack 15 (N-000240 to N-000254), execution profiles: **implemented, with one label not done at runtime.**
- N-000241 (profile id `cpu_baseline`): recorded here as a label. There is no runtime profile identifier in the package, because the spec does not ask for one in the public surface.
- N-000242 and N-000243 (platforms, required on Linux): Linux is the verified platform. macOS and Windows are not run here.
- N-000244, N-000245, N-000246 to N-000254 (import from source tree, Python 3.8+, no compile step, src layout, PEP 517 backend in `pyproject.toml`, editable install or path import): implemented.

## Not run here

- Python 3.8 and PyPy: source is checked for 3.8 syntax with `ast`, but no interpreter other than CPython 3.13 was used.
- macOS and Windows.
- No judge-side build or install step is needed; the tests import from `src/` with `PYTHONPATH=src`.
