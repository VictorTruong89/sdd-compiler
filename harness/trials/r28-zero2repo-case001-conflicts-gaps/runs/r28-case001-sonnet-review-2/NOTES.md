# Notes

Code: `src/tomlparse/` (`loads`, `load`, `TOMLDecodeError`). Hand-written parser; no build step.
In every conflict below I followed the TOML v1.1.0 specification, which the PRD names as the authority.

## Spec conflicts (spec/CONFLICTS.md C-01..C-14) and what I built
- C-01 Local time seconds: Terminology says "seconds are always written"; FP-02 says seconds may be omitted. Built: `07:32` is accepted, with second 0.
- C-02 Fraction rounding: PRD FP-02 says truncate; Contract `loads` return shape says "rounded to the nearest microsecond". Built: truncate to 6 digits, for times and datetimes.
- C-03 Trailing comma in arrays: PRD FP-01 accepts it; Contract says it is refused. Built: accepted.
- C-04 Float converter results: Terminology says only exact `dict`/`list` are refused; FP-05 and Contract say subclasses are refused too. Built: `isinstance` check, so subclasses raise `ValueError`.
- C-05 Sub-table under a dotted-key table: Terminology says a header is forbidden; FP-01 says an undefined sub-table may be declared by a header. Built: `a.b.c=1` then `[a.b.d]` is accepted. `[a.b]` itself is refused (a.b was defined by dotted keys). `a.b=1` then `[a.b.c]` is refused because a.b is a value.
- C-06 Empty keys: Contract says keys are "never empty"; PRD says a quoted key may be empty. Built: `"" = 1` is accepted.
- C-07 Quote before closing `"""`: FP-02 says valid, and the boundary list says refused. Built: valid, with up to two quotes at the end of the value. Six or more quotes in a row are refused.
- C-08 First line feed in a multiline literal string: one bullet says kept, the next says discarded. Built: discarded (TOML).
- C-09 Raw tab in a one-line string: one bullet says it must be written `\t`; the boundary list allows a raw tab. Built: raw tab accepted (TOML).
- C-10 Hex digit case in `\x`/`\u`/`\U`: one bullet says case-insensitive; the boundary list refuses uppercase. Built: both cases accepted.
- C-11 Whitespace after a line-ending backslash: one bullet says all whitespace is removed; another says the next line's leading whitespace is kept. Built: all whitespace and newlines are removed (TOML).
- C-12 CRLF in multiline basic strings: FP-01 says CRLF becomes LF; FP-02 says carriage returns are kept. Built: CRLF becomes LF in all multiline strings. A bare CR is refused. Error offsets index the original, un-normalized text.
- C-13 `+0` / `-0`: FP-02 says a signed zero is the integer 0 in one place and refused in another. Built: accepted as 0 (TOML). `01` is refused.
- C-14 Offset date-time separator: Terminology says `T`/`t`; FP-02 also allows a space. Built: `T`, `t` or a space for all date-times.

## Unstated items and my assumptions
- `load` with invalid UTF-8 bytes: the spec does not say what to raise. I raise `TOMLDecodeError` (a `ValueError`) with an empty `doc`.
- `load` detects text mode by `fp.read()` returning `str`, and then raises `TypeError`.
- Nesting deep enough to hit `RecursionError` is reported as `TOMLDecodeError`, since the PRD says a decode error is not a recursion error.
- Offset hours above 23 or minutes above 59 are refused.
- Bare `\r` (not followed by `\n`) is refused everywhere, including comments.
- DEL (0x7f) is treated as a control character, so it is refused in strings and comments.
- A `.pos` for an error is the offending character, or the start of the construct for unterminated or duplicate cases.
