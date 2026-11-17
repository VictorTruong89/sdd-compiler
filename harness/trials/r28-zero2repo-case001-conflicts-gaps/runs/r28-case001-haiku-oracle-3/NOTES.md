# NOTES — Tomlparse build

## Layout and how to run

- `src/tomlparse/__init__.py` — public names: `loads`, `load`, `TOMLDecodeError` (and `__version__`).
- `src/tomlparse/_parser.py` — the TOML v1.1.0 parser and the two entries.
- `src/tomlparse/_errors.py` — `TOMLDecodeError(msg, doc, pos)`.
- `tests/test_tomlparse.py` — tests, named after the spec ids they cover (`test_N_000113_…`).
- `pyproject.toml` — src-layout metadata (PEP 517, setuptools). Nothing is built by the judge.

Run: `cd /app && PYTHONPATH=src python3 -m pytest tests -q` (77 tests pass on Python 3.13.18).
The parser does not import `tomllib` or any other TOML library (checked by a test).

Environment limits: only Python 3.13 and Linux were available. The code avoids 3.9+ syntax and
library calls, but it has not been run on 3.8, PyPy, macOS, or Windows.

## Spec conflicts (all 20 are UNSETTLED in `spec/MAP.md`; the export used `--allow-open`)

Rule used for every conflict: the pack-01 text says what each entry does is specified in the PRD
("What each entry does with a document is specified in the PRD; this Contract states the shell
only", pack 01), so PRD feature-point wording wins over the Interface Contract where they differ.
Within the PRD, the behaviour that matches TOML v1.1.0 wins, since the spec says that language is
the authority (N-000001–N-000006, pack 06). Each entry below gives both sides and the choice.

1. **CF-000001** (quote before a multiline closing delimiter).
   A: N-000135, pack 12 FP-02 — "Both multiline forms may contain one or two of their own quote
   characters … including directly before the closing delimiter".
   B: N-000178, pack 12 FP-02 boundary — "a quote character directly before the closing delimiter of a
   multiline basic string" is refused.
   **Built:** A. Both multiline forms accept 1–2 quotes before the closing delimiter (3–5 in a row
   at the end; 6 or more is refused).

2. **CF-000008** (CRLF inside multiline strings).
   A: N-000112, pack 12 FP-01 — a CRLF is "a single line feed everywhere, including inside string
   values … holds line feeds only". B: N-000133, pack 12 FP-02 — line endings "carriage returns
   included" are kept exactly as written.
   **Built:** A. CRLF becomes LF inside every multiline string. A lone CR is refused.

3. **CF-000009** (first line feed of a multiline literal string).
   A: N-000130, pack 12 FP-02 — a multiline literal "keeps every character after its opening
   delimiter, including a first line feed". B: N-000131, pack 12 FP-02 — "a line feed immediately
   after the opening delimiter is discarded" in both multiline forms.
   **Built:** B. The first newline is trimmed in both multiline forms.

4. **CF-000012** (a header under a dotted-key table).
   A: N-000021, pack 07 Terminology (Dotted key) — "A table created by dotted keys cannot receive a
   sub-table through a header." B: N-000098, pack 12 FP-01 — a not-yet-defined sub-table "may still be
   declared by a header, as TOML v1.1.0 allows".
   **Built:** B. `[fruit.apple.texture]` is accepted after `fruit.apple.color = …`. A header that names a
   table already defined by dotted keys or by a header is refused (`[fruit.apple]` after dotted keys).

5. **CF-000015** (whitespace after a line-ending backslash).
   A: N-000134, pack 12 FP-02 — the backslash "removes the line ending and all whitespace … up to the
   next non-whitespace character". B: N-000136, pack 12 FP-02 — "the next line's leading spaces and
   tabs are kept".
   **Built:** A (TOML behaviour). Leading whitespace on the next line is removed. Whitespace before the
   backslash is kept.

6. **CF-000023, CF-000032, CF-000073** (which float-converter results are refused).
   A: N-000029, pack 07 Terminology (Float converter) — "Only a result whose type is exactly `dict` or
   exactly `list` is refused." B: N-000296 (pack 03), N-000232/N-000233 (pack 12 FP-05), N-000038 (pack 08),
   N-000230 (pack 12) — dict or list results "or a subclass instance" are refused; "dictionaries and lists
   forbidden"; "(and not an instance of a subclass of either)".
   **Built:** B. The check is `isinstance(result, (dict, list))`, so subclasses are refused too. The
   refusal is `ValueError`, not `TOMLDecodeError`, and no mapping is returned.

7. **CF-000028** (a tab in a literal-string key) and **CF-000035** (a tab in a literal string value).
   A: N-000141 (pack 12 FP-02, escapes) and N-000129 (pack 12 FP-02) — literal strings get no escape
   processing. B: N-000143 (pack 12 FP-02) — "A tab in a one-line string must be written as backslash-t".
   **Built:** A, with a raw tab accepted in every string form (see item 14). `'\t'` is the two characters
   backslash and `t`. A tab is never converted into an escape there.

8. **CF-000037** (hex digit case in integers).
   A: N-000146 (pack 12 FP-02) — "hex digits may be either case". B: N-000285 (pack 03) — "hexadecimal
   digits written in lowercase".
   **Built:** A. `0xDEADbeef` is accepted and gives the int `0xDEADBEEF`. Rule B describes digits written in
   the document, and the result is a Python int, which has no case, so the two rules only clash on how the
   source is written.

9. **CF-000045** and **CF-000069** (fraction of a local time). A: N-000156 and N-000157 (pack 12 FP-02) —
   the first six digits are read as microseconds, and later digits are "dropped (truncated, not rounded)".
   B: N-000292 (pack 03 `loads` return shape) — "its fraction rounded to the nearest microsecond".
   **Built:** A (truncation). It is the PRD behaviour, and pack 01 says the PRD specifies what each entry
   does. `00:00:00.9999999` gives microsecond 999999.

10. **CF-000059** (trailing comma in an array).
    A: N-000106 (pack 12 FP-01) — arrays "end with a trailing comma". B: N-000282 (pack 03) — "an array
    whose last element is followed by a comma is refused".
    **Built:** A. TOML v1.1.0 allows it, and the PRD lists v1.1 features (N-000067–N-000071, pack 11).

11. **CF-000062** (seconds in a local time).
    A: N-000028 (pack 07, Local time) — "Its seconds are always written." B: N-000154 (pack 12 FP-02) —
    "seconds may be omitted, in which case the second is 0" in any value with a time part.
    **Built:** B. `07:32` gives `time(7, 32)`. The PRD's non-goals list omitted seconds as a v1.1 feature
    (N-000071, pack 11).

12. **CF-000065** (a signed zero).
    A: N-000144 (pack 12 FP-02) — "a signed zero is the integer 0". B: N-000168 (pack 12 FP-02 error list) —
    "a zero with a sign (`+0`, `-0`)" is refused.
    **Built:** A. `+0`, `-0`, and `0` all give the int 0. TOML allows signed zero.

13. **CF-000068** (separator between date and time).
    A: N-000024 (pack 07, Offset date-time) — "Its date and time are joined by `T` or `t`." B: N-000153
    (pack 12 FP-02) — "The separator between date and time may be `T`, `t`, or a space."
    **Built:** B. A space is accepted in every date-time form, including offset date-times. Example:
    `1979-05-27 07:32:00-07:00`.

14. **CF-000071** (a raw tab in a one-line string).
    A: N-000143 (pack 12 FP-02) — "A tab in a one-line string must be written as backslash-t." B: N-000178
    (pack 12 FP-02 error list) — raw control characters "other than tab" are refused.
    **Built:** B (plus TOML). A raw tab is accepted in every string form. Only the other control
    characters (and DEL, see assumptions) are refused.

15. **CF-000072** (uppercase hex digits in `\x`, `\u`, `\U` escapes).
    A: N-000139 (pack 12 FP-02) — "Hex digits are case-insensitive." B: N-000176 (pack 12 FP-02 error list)
    — "escape digits written as uppercase letters" are refused.
    **Built:** A. `\u00e9` (lowercase digits) and `\u00E9` (uppercase digits) are both accepted.

16. **CF-000074** (an empty quoted key).
    A: N-000090 (pack 12 FP-01) — "A quoted key may be empty". B: N-000279 (pack 03) — keys are "`str`,
    never empty".
    **Built:** A. `"" = 1` gives the key `""`. A bare key cannot be empty, because the bare-key grammar
    requires at least one character.

Items 1 to 16 cover all 20 unsettled ids. Items 6, 7 and 9 each cover several ids.

## Spec gaps: what is not stated, and what was assumed

- **Invalid UTF-8 in `load`.** Not stated. `load` raises `TOMLDecodeError("invalid UTF-8 in document", doc, pos)`
  with `doc` decoded using replacement characters, and `pos` at the first bad byte.
- **UTF-8 BOM.** Not stated. A leading U+FEFF is not whitespace in TOML, so it is refused at offset 0.
- **Control characters in comments.** The spec allows non-ASCII in comments but does not say about control
  characters. Control characters other than tab are refused in comments, following TOML. Likewise DEL (U+007F)
  is refused in strings and comments.
- **Bare CR** outside a string is a decode error. Inside a string it is refused too, unless it is part of a CRLF.
- **Converter exceptions.** A `parse_float` that raises is not caught. The exception propagates unchanged.
- **Converter input.** The converter receives the token exactly as written, including sign, underscores and
  exponent (e.g. `"1_0.5e+3"`, `"-nan"`). It is called for every float, including `inf` and `nan`.
- **Date and time limits.** Seconds must be 0–59 (second 60 is refused, per "second not 0–59"). Offset hours
  must be 0–23 and offset minutes 0–59. Offsets with seconds are not accepted. Fraction digits: one or more,
  first six used, truncated.
- **`load` on an object without `read`** (for example a path string) raises `TypeError`. The spec says only that
  a path is never taken (N-000300).
- **`load` consumes the stream.** It calls `fp.read()` once and leaves the position at the end.
- **`loads` extra positional arguments** raise Python's own `TypeError`, since `parse_float` is keyword-only.
- **Error positions.** A duplicate key or invalid header is reported at the start of its key. An unexpected
  character is reported at that character. Running out of input reports `len(doc)`, so the message says
  "end of document".
- **Whitespace and newlines.** Spaces and tabs may surround `=`, dots, and `[`/`]`. Newlines and comments
  are allowed inside arrays and inline tables (TOML v1.1.0), but not between a key and its `=` or between `=`
  and its value (this follows TOML's line rule).
- **Signed zero** `+0` and `-0` are accepted (see CF-000065).
- **Super-table converted to dotted.** When dotted keys walk into a table that was only created implicitly as
  the parent of a header, the table becomes a dotted-key table. This is my reading of TOML's rule; the spec is silent.
- **Nesting depth.** The spec sets no limit. Arrays and inline tables are parsed with an explicit stack, so
  depth is bounded by memory, not by Python's recursion limit (tested to 5000 nested arrays and 3000 inline tables).
- **Pickling** `TOMLDecodeError` works, because its three values are passed to `ValueError.__init__` as arguments.
- **Version.** `__version__ = "2.4.0"`, the earliest version the PRD names as compatible with TOML v1.1.0 (N-000004).
- **Python 3.8 and other platforms.** The spec requires them, but only Python 3.13 on Linux was available. Nothing was
  run on 3.8, PyPy, macOS, or Windows.

## Checklist accounting

Every id in `spec/CHECKLIST.md` is either implemented (in `src/tomlparse/`) or listed as not done below.
Ids named in code comments (`# spec: N-…`) are the ones that point to a specific line. Ids named in test
names are tested. The other implemented ids are covered by the feature-point tests listed in each row.

**Implemented and tested (by feature point):**
- Pack 01–02, product shell and public surface (N-000255–N-000273): `test_N_000260_no_writer_or_cli_surface`,
  `test_N_000039_public_names_only`, `test_N_000259_entries_do_not_print`, `test_N_000270_root_names`,
  `test_N_000060_does_not_delegate_to_stdlib_toml`, `test_N_000267_package_imports_from_source_tree`.
- Pack 03, `loads` (N-000274–N-000298): `test_N_000278_result_shape`, `ParseStructure`, `ParseScalars`, `FloatConverter`,
  `ErrorsAndLocation`.
- Pack 04, `load` (N-000299–N-000306): `ParseFiles`, `test_N_000300_load_rejects_path_and_non_file`.
- Pack 05, `TOMLDecodeError` (N-000307–N-000323): `Surface`, `ErrorsAndLocation`
  (`test_N_000210_caller_can_construct_error`, `test_N_000313_error_round_trips_through_pickle`).
- Pack 06–11, product overview, terminology, public surface, non-functional constraints, real parser, non-goals
  (N-000001–N-000076): implemented as the behaviour listed in the next bullets. Tested by `test_N_000257_…`,
  `test_N_000066_result_is_plain_python`, `test_N_000160_values_copy_and_compare`,
  `test_N_000260_no_writer_or_cli_surface`, `test_N_000060_…`.
- Pack 12, feature points FP-01 to FP-05 (N-000077–N-000233): implemented in `_parser.py` and `_errors.py`,
  tested by the classes `ParseStructure`, `ParseScalars`, `ParseFiles`, `ErrorsAndLocation`, `FloatConverter`,
  `DeepNesting`.
- Pack 13–15, hardware requirements (N-000234–N-000254): pure Python, no compiled code, no third-party dependencies,
  src layout (`pyproject.toml`, `src/tomlparse`), imported from the source tree (`PYTHONPATH=src`).

**Not done, with reasons:**
- N-000008, N-000011: statements about the PRD's own scope and the order of feature points. They are documentation
  rules, with nothing to build.
- N-000009: the rule that exact symbol names live in the Interface Contract, not the PRD. Nothing to build; the
  names are implemented as the Interface Contract gives them (N-000270–N-000272).
- N-000041: "optional compiled wheels" are a MAY. None are built, which the spec allows (N-000248 is an assumption).
- N-000073, N-000074: "guaranteeing a parse throughput" is explicitly not a requirement. No speed target is set.
- N-000075: the speed scripts, fuzzer, profiler and packaging scripts are not product capabilities. None are shipped.
- N-000241: profile id `cpu_baseline`, a label with no runtime behaviour.
- N-000248: assumption that optional compiled extensions exist. Nothing depends on it.
- N-000043, N-000044, N-000242, N-000264: Python 3.8+ and the three platforms. The code is written for them, but it was
  only run on Python 3.13 and Linux (see Environment limits above).

**Assumptions, recorded for review:** items under "Spec gaps" above.
