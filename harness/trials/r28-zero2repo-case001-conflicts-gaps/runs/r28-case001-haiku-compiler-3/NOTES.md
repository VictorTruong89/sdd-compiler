# NOTES

Build of the Tomlparse library from `spec/` (TOML v1.1.0 parser, pure Python).

Layout: `src/tomlparse/` (`__init__.py`, `_api.py` for `loads`/`load`, `_errors.py` for
`TOMLDecodeError`, `_parser.py` for the parser). Tests: `tests/test_tomlparse.py`
(run with `PYTHONPATH=src python3 -m pytest tests`). Packaging: `pyproject.toml`
(setuptools, src layout, no dependencies). The hidden tests run with `PYTHONPATH=src`.

Target: Python 3.8+ syntax and standard library only. Verified here on Python 3.13.

## 1. Conflicts in the spec

The export was made with `--allow-open`; `spec/MAP.md` lists 16 unsettled contradictions.
For each, the choice below is what the code does. Where the spec gives two readings, I took
the reading that matches TOML v1.1.0 and the more specific PRD statement.

### Unsettled contradictions (listed in MAP.md)

- **CF-000001** (Full PRD, FP-02 multiline strings, claims N-000135 vs N-000178). N-000135: both
  multiline forms may contain quotes "including directly before the closing delimiter". N-000178
  (FP-02 boundary): a quote directly before the closing delimiter of a multiline basic string is
  refused. **Built:** allowed (TOML 1.1 behaviour; up to two quotes before `"""`, more than five in a row is refused).
- **CF-000008** (FP-01 CR LF, N-000112 vs N-000133). N-000112: CR LF is one line feed everywhere,
  multiline strings "hold line feeds only". N-000133: CR is kept in multiline basic strings. **Built:**
  N-000112. CR LF is normalized to LF before parsing. A lone CR is refused. Error offsets are mapped
  back to the original text, so `doc` is the caller's string.
- **CF-000009** (FP-02 multiline literal, N-000130 vs N-000131). N-000130 keeps a first line feed in
  multiline literal strings. N-000131 drops it in both multiline forms. **Built:** dropped in both
  (TOML 1.1 behaviour).
- **CF-000012** (FP-01 dotted keys and headers, N-000021 vs N-000098). N-000021: a table created by
  dotted keys cannot receive a sub-table through a header. N-000098: a not-yet-defined sub-table of it
  may be declared by a header. **Built:** N-000098. `[fruit.apple.texture]` is allowed after
  `apple.color = ...`. Re-defining `[fruit.apple]` or `[fruit.apple.taste]` (defined by dotted keys)
  is refused.
- **CF-000015** (FP-02 line-ending backslash, N-000134 vs N-000136). N-000134: all whitespace after
  the line-ending backslash, including the next line's indentation, is removed. N-000136: that
  indentation is kept. **Built:** N-000134 (TOML behaviour).
- **CF-000023** and **CF-000032** (`parse_float` result, Terms and FP-05 vs N-000029, N-000038,
  N-000296). N-000029: only results whose type is *exactly* dict or list are refused. N-000296 and
  FP-05: subclass instances are refused too. **Built:** `isinstance` (subclasses refused) because
  FP-05 and the Failures table say so explicitly. The error is `ValueError`, not `TOMLDecodeError`.
- **CF-000028** and **CF-000035** (tabs in literal strings, N-000141/N-000129 vs N-000143). N-000143:
  "a tab in a one-line string must be written as backslash-t". Literal strings are never escaped
  (N-000129, N-000141). FP-02 also excludes only control characters "other than tab" from strings.
  **Built:** a raw tab is allowed in every string form, including literal strings. Backslash-t
  still works in basic strings.
- **CF-000037** (hex digits, N-000146 vs N-000285). N-000146: either case. N-000285 (interface
  contract, integer return shape): "written in lowercase". Integer values have no written digits, so
  this affects nothing observable. **Built:** either case in input (`0xDEADbeef` is accepted).
- **CF-000045** and **CF-000069** (fraction handling, N-000156/N-000157 vs N-000292). N-000156 and
  N-000157 (FP-02): the first six digits are read, the rest dropped, "truncated, not rounded". N-000292
  (interface contract, local time): "rounded to the nearest microsecond". **Built:** truncation (the
  more specific PRD text, and it applies to all date-times).
- **CF-000059** (arrays, N-000106 vs N-000282). N-000106 (FP-01): arrays "end with a trailing comma".
  N-000282 (interface contract): an array whose last element is followed by a comma "is refused".
  **Built:** trailing commas are accepted (TOML 1.1). The interface sentence looks like an error.
- **CF-000062** (local time seconds, N-000028 vs N-000154). N-000028: local time seconds are always
  written. N-000154: seconds may be omitted in any value with a time part. **Built:** seconds may be
  omitted in local times as well (`07:32` is `datetime.time(7, 32)`).
- **CF-000065** (signed zero, N-000144 vs N-000168). N-000144: "a signed zero is the integer 0".
  N-000168: `+0` and `-0` are refused. **Built:** accepted, as the integer 0 (TOML behaviour).
  `+0x1` and `-0o7` are still refused.
- **CF-000068** (date/time separator, N-000024 vs N-000153). N-000024: an offset date-time's date and time
  are "joined by T or t". N-000153: the separator "may be T, t, or a space". **Built:** T, t or a space,
  for all date-times (TOML 1.1 behaviour).

### Gaps and contradictions not in MAP.md

- **Empty quoted keys.** Interface contract "keys: `str`, never empty" (N-000279) vs FP-01
  "A quoted key may be empty" (N-000089). **Built:** `"" = 1` is accepted with key `""`.
- **Uppercase hex escape digits.** FP-02 refuses "escape digits written as uppercase letters"
  (N-000176), but the same section says "Hex digits are case-insensitive" (N-000139, N-000146).
  **Built:** `é` and `\x4A` are accepted.
- **Dotted keys into an implicit table.** `[a.b.c]` followed by `[a]` then `b.d = 1` is allowed.
  The spec does not say. The resulting `b` is marked as dotted-key-defined, so a later `[a.b]` is refused.

## 2. Things the spec does not state (assumptions)

- **Leap second** `:60` is refused (FP-02 says seconds are 0-59).
- **Year 0000** is refused: `datetime.date` cannot represent year 0. TOML allows it.
- **UTC offsets** must satisfy hours 0-23 and minutes 0-59. `Z` and `z` both give `timezone.utc`.
- **Byte order mark.** A leading UTF-8 BOM (U+FEFF) is not whitespace in TOML, so it is refused.
- **Invalid UTF-8** in `load()` raises `TOMLDecodeError`. `doc` is the bytes decoded with
  `replace`, and `pos` is the character index of the first bad byte in that text. Not specified.
- **Recursion.** Deeply nested arrays or inline tables (about 1000 levels) raise `TOMLDecodeError`
  ("document is nested too deeply") instead of `RecursionError`. Not specified.
- **Error wording.** `str(err)` is `"<msg> (line L, column C)"`, or `"<msg> (end of document, line L,
  column C)"` at or past the end. Wording is free per the spec.
- **`TOMLDecodeError` args and pickling.** `args` is `(msg, doc, pos)`. Pickling and copying are
  supported through `__reduce__`.
- **`load()` text detection.** A `io.TextIOBase` is refused before reading. Any other object whose
  `read()` returns `str` is refused after reading. Passing a non-file object (no `read`) is a `TypeError`.
- **`parse_float` is called** once per float token, in document order, with the token text as
  written (sign, underscores, exponent included). The builtin `float` is used directly when it is the
  default. A converter result is checked immediately, so a dict/list return raises at that float.
- **Subclasses of `str`** passed to `loads` are accepted.
- **Bare keys** are ASCII only (`A-Za-z0-9_-`), per the Terms table.
- **Local times** have no time zone. Fractions of any length are accepted; only the first six digits count.
- **Comments** may contain any non-control character, including non-ASCII. Tab is allowed.
- **Non-decimal integers** and floats: `inf` and `nan` are accepted only in the exact spellings
  given (`inf`, `+inf`, `-inf`, `nan`, `+nan`, `-nan`).

## 3. Spec coverage

Every id from `spec/CHECKLIST.md` has an outcome. Ids marked "code" have a `# spec:` marker beside the
implementing code. "test" means `tests/test_tomlparse.py` covers the behaviour. Ids that have no
code of their own are listed with the reason.

- **Implemented in code and exercised by tests:** the document grammar and tables (FP-01), scalars
  (FP-02), binary entry (FP-03), decode error and location rules (FP-04), the float converter (FP-05),
  the public surface and the decode error class (interface contract packs 02-05).
- **Non-goals, not built (the spec says they are not part of the product):** N-000063 to N-000076 and
  N-000032. There is no writer, no dump/encode entry, no CLI, no `python -m`, no config file, no
  speed claim, no speed scripts, no fallback to the stdlib `tomllib` (the parser does not use it).
- **Design and environment constraints, satisfied by construction:** N-000040 to N-000048 and
  N-000234 to N-000254 (pure Python, zero runtime dependencies, CPU only, Python 3.8+, Linux/macOS/
  Windows, source-tree import, no compiled extension). N-000236 to N-000254 concern the default
  profile only. The package has no native code, and `pyproject.toml` declares no dependencies.
  Not run here: macOS and Windows (only Linux is available in this environment).
- **Result types and error text:** N-000051 to N-000056 (plain builtin results, free error text) are
  met as described in section 2.
- **Items the spec makes optional:** N-000041 (compiled wheels, MAY), N-000042, N-000074 (speed is a
  design goal, no requirement), N-000075 (speed scripts are not product capabilities), N-000218
  (wording of the decode-error report is free).

## 4. Not verified

- No run against the hidden tests (not visible, by design). Local tests and a differential check
  against the stdlib `tomllib` (1.0 only) on 18 documents agree, except for TOML 1.1 features
  (`\e`, `\x`) that `tomllib` refuses, as expected.
- macOS and Windows behaviour is untested. Nothing in the code is platform-specific.
