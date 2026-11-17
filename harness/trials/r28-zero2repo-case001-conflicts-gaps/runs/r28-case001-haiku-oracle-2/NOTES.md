# Tomlparse — implementation notes

This file records (1) every disagreement inside `spec/` and what was built for it,
(2) what the spec leaves unstated and the assumption made, and (3) how the
checklist was covered. The spec itself is unchanged.

Pack files are cited as `spec/packs/NN-…md` with the node ids from `spec/CHECKLIST.md`.
The export's `spec/MAP.md` marks all 20 contradictions below as UNSETTLED (no human
verdict), so every one of them was resolved by choosing one side here.

## Layout

- `src/tomlparse/__init__.py` — public names: `loads`, `load`, `TOMLDecodeError` (and `__all__`).
- `src/tomlparse/_api.py` — `loads` (text entry) and `load` (binary-file entry).
- `src/tomlparse/_parser.py` — pure-Python TOML v1.1.0 parser (no `tomllib`, no other TOML library).
- `src/tomlparse/_errors.py` — `TOMLDecodeError(msg, doc, pos)`.
- `pyproject.toml` — src-layout, setuptools PEP 517 backend, no dependencies. The tests and the judge use `PYTHONPATH=src`; nothing needs installing.
- `tests/` — pytest suite; test names carry node ids (`test_N_000082_…`). `tests/test_spec_coverage.py` fails if any checklist id is referenced neither in `src/` nor `tests/`.

Run: `cd /app && python -m pytest tests` (conftest adds `src/` to `sys.path`; `PYTHONPATH=src` works too).

## 1. Conflicts inside the spec

Each entry gives side A and side B with their location, then what was built.

### CF-000001 — quote characters before a multi-line closing delimiter
- A: `N-000135` (pack 12, FP-02 strings): both multi-line forms "may contain one or two of their own quote characters … including directly before the closing delimiter".
- B: `N-000178` (pack 12, FP-02 boundary): refuse "a quote character directly before the closing delimiter of a multiline basic string".
- **Built:** A. Both multi-line forms accept one or two quotes before the closing delimiter (`"""a""""` → `a"`); six or more quotes in a row is an error.

### CF-000008 — carriage returns in CRLF multi-line strings
- A: `N-000112` (pack 12, FP-01): a CRLF multi-line string "holds line feeds only"; CRLF is one line feed "everywhere, including inside string values".
- B: `N-000133` (pack 12, FP-02): "Line endings inside a multiline basic string are kept exactly as written, carriage returns included."
- **Built:** A. The whole input is normalised CRLF → LF before parsing; no CR reaches a string value. A lone CR (not part of CRLF) is an error.

### CF-000009 — first line feed of a multi-line literal string
- A: `N-000130` (pack 12, FP-02): a multi-line literal string "keeps every character after its opening delimiter, including a first line feed".
- B: `N-000131` (pack 12, FP-02): "a line feed immediately after the opening delimiter is discarded" in both multi-line forms.
- **Built:** B, for both multi-line forms (the TOML rule).

### CF-000012 — header declaring a sub-table of a dotted-key table
- A: `N-000021` (pack 07, Terminology, "Dotted key"): "A table created by dotted keys cannot receive a sub-table through a header."
- B: `N-000098` (pack 12, FP-01): "a sub-table of it that has not itself been defined may still be declared by a header, as TOML v1.1.0 allows."
- **Built:** B for new sub-tables; A for the dotted table itself. A header cannot define a table that dotted keys created (`[a]` after `a.b = 1` is an error), but `[fruit.apple.texture]` after `apple.color = …` is accepted, as in the TOML spec. Read literally, A would also forbid that case; I did not apply it that far.

### CF-000015 — whitespace after a line-ending backslash
- A: `N-000134` (pack 12, FP-02): the backslash "removes the line ending and all whitespace (spaces, tabs, line feeds) up to the next non-whitespace character or the closing delimiter".
- B: `N-000136` (pack 12, FP-02): "After a line-ending backslash, the next line's leading spaces and tabs are kept."
- **Built:** A (TOML rule). Leading whitespace on the next line is removed.

### CF-000023, CF-000032, CF-000073 — what the float converter may return
- A: `N-000029` (pack 07, Terminology, "Float converter"): "Only a result whose type is exactly `dict` or exactly `list` is refused." (Also `N-000230`: a value "not an instance of a subclass of either" is the one allowed.)
- B: `N-000296` (pack 03, `loads` failures): "`parse_float` returned a `dict` or `list` (or a subclass instance)" → `ValueError`; `N-000038` (pack 08): "with dictionaries and lists forbidden as conversion results"; `N-000220` (pack 12, FP-05): "or an instance of a subclass of either".
- **Built:** B. An instance of a `dict` or `list` subclass is refused with `ValueError`, the same as the exact types. Other results are bound as returned, including `None`, `str` and `int`.

### CF-000028, CF-000035, CF-000071 — raw tab inside strings and keys
- A: `N-000141` (pack 12, FP-02): a literal-string key "does not" undergo escape processing; `N-000129`: escapes are "never" processed in literal strings.
- B: `N-000143` (pack 12): "A tab in a one-line string must be written as backslash-t."
- C: `N-000178` (pack 12): refuses "raw control characters other than tab".
- **Built:** tab is a legal raw character in every string form and key. `\t` is still a valid escape in basic strings. B cannot apply to literal strings, because they have no escapes.

### CF-000037 — case of hexadecimal digits in integers
- A: `N-000146` (pack 12, FP-02): "hex digits may be either case".
- B: `N-000285` (pack 03, return shape): "hexadecimal digits written in lowercase".
- **Built:** A. Input digits of any case are accepted. Case cannot be observed in the result (an `int`), so B has no visible effect and was not otherwise applied.

### CF-000045, CF-000069 — fractional seconds beyond six digits
- A: `N-000156`/`N-000157` (pack 12, FP-02): the first six digits are microseconds and "any digits after the sixth are dropped (truncated, not rounded)".
- B: `N-000292` (pack 03, `loads` return shape): "its fraction rounded to the nearest microsecond".
- **Built:** A (truncation). The PRD states the rule explicitly; rounding can also carry to 1 000 000 µs.

### CF-000059 — trailing comma in arrays
- A: `N-000106` (pack 12, FP-01): arrays "end with a trailing comma".
- B: `N-000282` (pack 03, return shape): "an array whose last element is followed by a comma is refused".
- **Built:** A. Trailing commas are accepted in arrays and inline tables (TOML v1.1.0).

### CF-000062 — omitted seconds in a local time
- A: `N-000028` (pack 07, Terminology, "Local time"): "Its seconds are always written."
- B: `N-000154` (pack 12, FP-02): "seconds may be omitted, in which case the second is 0" for "any value with a time part". The non-goals (pack 11, `N-000071`) also list omitted seconds as a v1.1 feature.
- **Built:** B. `07:32` is the local time 07:32:00 (and `1979-05-27T07:32` a local date-time).

### CF-000065 — signed zero
- A: `N-000144` (pack 12, FP-02): "a signed zero is the integer 0".
- B: `N-000168` (pack 12, FP-02 refusals): "a zero with a sign (`+0`, `-0`)".
- **Built:** A. `+0`, `-0` → `0`. This matches TOML.

### CF-000068 — separator between date and time
- A: `N-000024` (pack 07, Terminology, "Offset date-time"): "Its date and time are joined by `T` or `t`."
- B: `N-000153` (pack 12, FP-02): "The separator between date and time may be `T`, `t`, or a space."
- **Built:** B, for every date-time kind. A space is accepted (`1979-05-27 07:32:00Z`), as well as `T` and `t`.

### CF-000072 — uppercase digits in `\x`, `\u`, `\U` escapes
- A: `N-000139` / `N-000146` (pack 12): hex digits of escapes are "case-insensitive".
- B: `N-000176` (pack 12, FP-02 refusals): "escape digits written as uppercase letters".
- **Built:** A. `\u00E9` and `\u00e9` both decode to `é`.

### CF-000074 — empty quoted keys
- A: `N-000090` (pack 12, FP-01): "A quoted key may be empty".
- B: `N-000279` (pack 03, return shape): "keys: `str`, never empty".
- **Built:** A. `"" = 1` gives `{"": 1}`. A bare key still cannot be empty, because the grammar requires at least one character. B is read as a claim about key type (`str`).

## 2. Items the spec does not state (assumptions)

- **Byte-order mark.** A leading U+FEFF is not whitespace and is refused as an invalid key. `load` decodes with the plain `utf-8` codec, not `utf-8-sig`.
- **Invalid UTF-8 in `load`.** The spec only covers bytes that decode. Undecodable bytes raise `UnicodeDecodeError`, which is a `ValueError` but not a `TOMLDecodeError`.
- **Nesting depth.** The parser is recursive. Arrays and inline tables nested more than 250 levels deep raise `TOMLDecodeError` ("nesting too deep"). This is an implementation limit, not a TOML limit; it avoids a `RecursionError`.
- **Years.** `0000-…` is rejected because Python's `datetime` cannot represent year 0. TOML's grammar would allow it.
- **Offset range.** Offset hours must be 00–23 and minutes 00–59, as `datetime.timezone` requires |offset| < 24 h.
- **Times.** Seconds 00–59 only (`N-000180`); leap second `:60` is rejected.
- **Error positions.** `pos` and the reported `doc` use the caller's original text, including CRLF. `lineno`/`colno` come from `doc[:pos]`. An offset at or past the end reports "end of document". Errors at end-of-input (for example an unterminated array) use the end offset.
- **Stray carriage return.** A CR that is not part of CRLF is an error wherever it appears (it is not whitespace and is a control character in strings and comments).
- **Control characters.** Only tab is allowed among the ASCII control characters (U+0000–U+001F and U+007F) in strings and comments. Multi-line strings also allow LF.
- **Converter specifics.** `parse_float` receives the token exactly as written (sign, underscores, exponent), including `inf` and `nan`. Exceptions from the converter propagate unchanged. The default is the builtin `float`, which accepts underscores.
- **Top-level `load` checks.** A `io.TextIOBase` is refused before reading. An object whose `read()` returns `str` is refused after reading. An object with no `read` attribute, or one returning something other than `bytes`/`bytearray`, is refused with `TypeError`.
- **Table-rule corners.** A header may walk through (and extend) a table created by dotted keys, and a dotted key may walk through a table that an earlier header only implied as a parent. Neither is forbidden by the spec. A header may never define a table that was already defined, or that dotted keys created. Extending an inline table or an array of tables by dotted key or header is refused. The rules were cross-checked against the TOML 1.0 examples.
- **Type of values.** Results are exact builtin types (`dict`, `list`, `str`, `int`, `bool`, `float`) and standard-library `datetime` types.
- **Python versions.** Developed and run on CPython 3.13 here. The code is checked for Python 3.8 syntax (`ast.parse(..., feature_version=(3, 8))`) and uses no 3.9+ standard-library APIs, but it was not executed on 3.8 or PyPy. Linux only was exercised; macOS and Windows were not run (the code has no platform-specific paths).
- **Version.** `pyproject.toml` sets `version = "2.4.0"` to match the PRD's compatibility statement. No `__version__` attribute was added, because the spec says the product must not invent extra surfaces (`N-000039`).
- **Profile id.** `cpu_baseline` (`N-000241`) is a label in the hardware document. The product has no runtime profile selection, so it is not implemented as code.
- **Verification aid.** During development I compared outputs with the standard library's `tomllib` on TOML 1.0 samples, as a scratch check outside the repository. The product does not import or call it (`N-000057`, `N-000058`, `N-000076`), and the test suite does not depend on it.

## 3. Checklist coverage

- All 323 ids in `spec/CHECKLIST.md` are referenced: by `# spec:` comments in `src/` and by test names or comments in `tests/`. `tests/test_spec_coverage.py` enforces this.
- Two ids are recorded as not applicable with reasons in that test: `N-000073` and `N-000074` (speed is a non-goal, not a requirement).
- Acceptance criteria: none exist in this export (`AC` counts are 0 in `spec/MAP.md`), so tests are named by node id.
- Last run: `python -m pytest tests` → 190 passed (Python 3.13, Linux).
