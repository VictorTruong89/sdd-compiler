# NOTES

Implementation: `src/tomlparse/` (hand-written TOML v1.1.0 parser; `loads`, `load`, `TOMLDecodeError`).
Where spec files disagree, TOML v1.1.0 (declared the authority in the PRD) decided.

## Conflicts and choices
- C-01 local time seconds: PRD Terminology says seconds "always written"; FP-02 and Non-goals allow omission. Built: seconds optional (`07:32` -> 07:32:00).
- C-02 fraction: PRD says truncate to 6 digits; Contract says rounded for local time. Built: truncate (all time values).
- C-03 trailing comma in arrays: PRD accepts, Contract refuses. Built: accepted (TOML 1.1).
- C-04 converter result: Terminology says only exact dict/list refused; FP-05 and Contract also refuse subclasses. Built: subclasses refused (ValueError, not TOMLDecodeError).
- C-05 sub-table under dotted-key table: Terminology forbids; FP-01 allows. Built: allowed for tables not themselves defined (`a.b.c=1` then `[a.b.d]` ok; `[a.b]` rejected; `a.b=1` then `[a.b.c]` rejected as b is an integer).
- C-06 empty keys: Contract "never empty" vs PRD allows `"" = 1`. Built: allowed.
- C-07 quotes before closing `"""`: built: one or two allowed (TOML).
- C-08 first newline in `'''`: built: discarded (TOML).
- C-09 raw tab in one-line strings: built: allowed (TOML).
- C-10 uppercase hex in escapes: built: accepted.
- C-11 whitespace after line-ending backslash: built: all whitespace/newlines skipped, including next line's indentation (TOML).
- C-12 CRLF in multiline basic: built: CRLF normalized to LF before parsing (so `doc` in errors is the normalized text); a lone CR is an error.
- C-13 `+0`/`-0`: built: accepted as 0 (TOML).
- C-14 space separator: built: allowed for offset date-times too.

## Unstated items (assumed)
- Invalid UTF-8 bytes in `load`: raise `TOMLDecodeError` with empty doc, pos 0.
- `load` decides text vs binary by checking `fp.read()` returns bytes; otherwise TypeError.
- DEL (0x7f) and control chars other than tab are rejected in strings and comments.
- Offset hours must be <=23, minutes <=59.
- No recursion limit handling for deeply nested arrays (very deep nesting may hit RecursionError).
