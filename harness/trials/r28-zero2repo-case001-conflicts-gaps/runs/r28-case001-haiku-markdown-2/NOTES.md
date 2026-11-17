# Implementation notes

Tomlparse 2.4.0, a pure-Python TOML v1.1.0 parser. Layout:

- `src/tomlparse/__init__.py` — public entries `loads`, `load`, `__version__`.
- `src/tomlparse/_errors.py` — `TOMLDecodeError(msg, doc, pos)`.
- `src/tomlparse/_parser.py` — the parser (no delegation to any TOML library).
- `tests/test_tomlparse.py` — unit tests (`PYTHONPATH=src python3 -m unittest discover -s tests`).
- `pyproject.toml` — src-layout, setuptools PEP 517 backend, no runtime dependencies.

Status: all 54 tests in `tests/` pass on Python 3.13. Python 3.8 was not available
in this environment, so compatibility with 3.8 is by inspection only (no `match`,
no walrus, no `str.removeprefix`, no PEP 585/604 annotations).

## Conflicts in the specification

Each item quotes both sides, names where they are, and states what was built.
Line numbers refer to the files as delivered.

1. **Local time fraction: rounded or truncated.**
   - `spec/Interface_Contract.md` line 46 (`loads` return shape): local time has
     "its fraction rounded to the nearest microsecond".
   - `spec/Full_PRD.md` line 116 (FP-02, "Seconds and fractions"): fractions are
     "truncated, not rounded", for any value with a time part.
   - **Built:** truncation (the PRD rule, applied to all time-bearing values).

2. **Empty keys.**
   - `spec/Interface_Contract.md` line 38: keys are "`str`, never empty".
   - `spec/Full_PRD.md` line 84 (FP-01): "A quoted key may be empty".
   - **Built:** `""` is a valid key (TOML allows it). Bare keys cannot be empty.

3. **Trailing comma in arrays.**
   - `spec/Interface_Contract.md` line 40: "an array whose last element is followed by a comma is refused".
   - `spec/Full_PRD.md` line 89 (FP-01): arrays "end with a trailing comma"; TOML v1.1.0 allows it.
   - **Built:** accepted, as the PRD and TOML say. The interface line is treated as the error.

4. **Float converter: which results are refused.**
   - `spec/Full_PRD.md` line 29 (Terminology): only a result whose type is "exactly `dict` or exactly `list`" is refused.
   - `spec/Full_PRD.md` lines 179 and 183 (FP-05) and `spec/Interface_Contract.md` line 56: `dict`/`list` "(or a subclass instance)" is refused.
   - **Built:** `isinstance` check, so subclasses are refused too. Those two sources agree; the terminology entry is the outlier.

5. **Dotted keys followed by a header.**
   - `spec/Full_PRD.md` line 23 (Terminology, "Dotted key"): "A table created by dotted keys cannot receive a sub-table through a header."
   - `spec/Full_PRD.md` line 86 (FP-01): a sub-table not itself defined "may still be declared by a header, as TOML v1.1.0 allows."
   - **Built:** FP-01 and TOML. `[fruit.apple.texture]` is accepted after `apple.color = ...`. Re-defining the dotted-key table itself with `[fruit.apple]` is refused, as FP-01 requires.

6. **Seconds in local times.**
   - `spec/Full_PRD.md` line 28 (Terminology, "Local time"): "Its seconds are always written."
   - `spec/Full_PRD.md` line 116 (FP-02): "In any value with a time part, seconds may be omitted."
   - **Built:** seconds may be omitted in input. The constructed value always has a second field (0 when omitted).

7. **Date-time separator in offset date-times.**
   - `spec/Full_PRD.md` line 25 (Terminology, "Offset date-time"): date and time "joined by `T` or `t`".
   - `spec/Full_PRD.md` line 115 (FP-02): the separator "may be `T`, `t`, or a space".
   - **Built:** all three separators for every date-time kind. A space is only taken as a separator when a time (`HH:MM`) follows it, so `1979-05-27 # c` is a local date.

8. **Signed zero integers.**
   - `spec/Full_PRD.md` line 113 (FP-02, normal behaviour): "a signed zero is the integer 0".
   - `spec/Full_PRD.md` line 124 (FP-02, refusals): "a zero with a sign (`+0`, `-0`)" is refused.
   - **Built:** `+0` and `-0` are accepted as `0`. This matches the normal-behaviour bullet and TOML.

9. **Case of hex digits in escapes.**
   - `spec/Full_PRD.md` line 112 (FP-02, escapes) and line 113 (integers): hex digits are "case-insensitive" / "may be either case".
   - `spec/Full_PRD.md` line 126 (FP-02, refusals): "escape digits written as uppercase letters" are refused.
   - **Built:** case-insensitive hex in `\x`, `\u`, `\U` and in integer literals. The refusal line contradicts two normal-behaviour lines.

10. **Quotes next to a multiline closing delimiter.**
    - `spec/Full_PRD.md` line 111 (FP-02): multiline forms may contain one or two quote characters "including directly before the closing delimiter".
    - `spec/Full_PRD.md` line 127 (FP-02, refusals): "a quote character directly before the closing delimiter of a multiline basic string" is refused.
    - **Built:** the normal-behaviour rule. Runs of 1–2 quotes (3–5 in total before the delimiter) are content, and a run of 6 or more is refused. Same rule for multiline literal strings.

11. **Integer spelling in the return shape.**
    - `spec/Interface_Contract.md` line 41: "integers: `int` (never `bool`), hexadecimal digits written in lowercase".
    - A Python `int` has no spelling, so there is nothing to lower-case. **Built:** ordinary `int` values; no action.

## Gaps the specification does not state (assumptions)

- **Nesting depth.** No limit is stated. Recursion is used for arrays and inline tables. When Python's recursion limit is hit, the parse raises `TOMLDecodeError` ("document is nested too deeply") instead of `RecursionError`. With Python 3.13's default recursion limit, nesting of about 490 or more array levels is refused (measured).
- **Byte-order mark.** Not mentioned. A UTF-8 BOM (U+FEFF) at the start of the text is not whitespace and is refused. The binary entry does not strip it.
- **Invalid UTF-8 in `load`.** Not specified. Raised as `TOMLDecodeError` with `doc` set to the text decoded with `errors="replace"`, and `pos` at the first byte that is not valid UTF-8.
- **Text-mode detection in `load`.** A file object is refused with `TypeError` if it is an `io.TextIOBase`, if `read()` returns `str`, or if it has no `read` method at all. Values other than bytes-like objects are refused the same way.
- **Carriage returns.** A CR that is not part of a CR/LF pair is refused everywhere (it is a control character). Error offsets refer to the caller's original text, so a CR/LF pair counts as two characters.
- **Control characters.** DEL (U+007F) is refused in strings and comments, as TOML forbids it. Tab is allowed in comments and strings.
- **Whitespace.** Only space and tab are whitespace in the grammar. Other Unicode spaces are not.
- **Years.** Year `0000` is refused: Python `date` and `datetime` start at year 1. TOML permits 0000–9999; this is the only date range that is narrower.
- **UTC offsets.** Accepted range is `00:00`–`23:59`, the range `datetime.timezone` can represent. Hour above 23 or minute above 59 is refused.
- **Leap seconds.** Second `60` is refused (the PRD says seconds are 0–59).
- **Exponents.** Leading zeros are allowed in exponents (`1e05`), as TOML allows; leading zeros in the integer part are refused.
- **Dotted keys into an implicit table.** A super-table created implicitly by a header (for example `[a.b.c]` creates `a` and `a.b`) can receive dotted keys later (`[a]` then `b.x = 1`). It then becomes a dotted-key table, so a later `[a.b]` is refused. Dotted keys into a table defined by a header are refused.
- **Array of tables over an implicit table.** `[a.b.c]` followed by `[[a]]` is refused: a table cannot be replaced by an array of tables.
- **Error text.** Message wording is free (per the PRD). `str(err)` gives the message, line, column and character offset; when the offset is at or past the end, the report says "at end of document".
- **`parse_float`.** Called with the float's characters as written, after CR/LF normalisation (there are no CRs inside a float token). Exceptions raised by the converter propagate unchanged. The converter may be called for floats that appear before a later syntax error, since parsing is single-pass.
- **Default float.** `float` is detected by identity (`parse_float is float`), so passing `float` explicitly takes the same fast path.
- **Strings passed to `loads` as `str` subclasses** are accepted.
- **Fractions beyond six digits** are truncated, as the PRD specifies.
