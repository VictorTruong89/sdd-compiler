# NOTES

Implementation: `src/tomlparse/` (`loads`, `load`, `TOMLDecodeError`). Where the spec files disagree I followed TOML v1.1.0 (the PRD names it as the authority).

## Spec conflicts and what I built
- C-01 local time seconds: PRD Terminology says seconds are always written; FP-02 (line 116) and Non-goals say they may be omitted. Built: omitted seconds accepted (`07:32` -> second 0).
- C-02 fraction rounding: PRD FP-02 says truncate to 6 digits; Contract says round to nearest microsecond. Built: truncate (applies to all time kinds).
- C-03 array trailing comma: PRD allows it; Contract "Return shape" says refused. Built: accepted (`[1,2,]`), as TOML 1.1.0.
- C-04 converter results: Terminology says only exact dict/list refused; FP-05 and Contract say subclasses too. Built: `isinstance(r,(dict,list))` raises `ValueError`.
- C-05 header under dotted-key table: Terminology forbids; FP-01 allows undefined sub-table via header. Built: `a.b.c=1` then `[a.b.d]` is accepted; `[a.b]` itself (the dotted-defined table) is refused.
- C-06 empty keys: Contract "never empty" vs PRD "quoted key may be empty". Built: `"" = 1` accepted.
- C-07 quotes before closing `"""`: FP-02 line 111 allows; line 127 refuses. Built: up to two quotes before the closing delimiter are accepted in both multiline forms.
- C-08 first newline in multiline literal: line 108 says kept, line 109 says discarded. Built: discarded in both forms.
- C-09 raw tab in one-line strings: line 112 says must be `\t`; line 126 says raw tab is not refused. Built: raw tab accepted (TOML).
- C-10 hex escape case: line 112 case-insensitive; line 126 refuses uppercase. Built: both cases accepted.
- C-11 line-ending backslash: line 110 trims all following whitespace; line 111 keeps leading spaces. Built: trims (TOML).
- C-12 CR in multiline basic strings: FP-01 says CRLF becomes LF; FP-02 line 109 keeps CR. Built: CRLF normalized to LF up front; a lone CR is refused as a control character. The error `doc` is the normalized text.
- C-13 `+0`/`-0`: line 113 accepts; line 124 refuses. Built: accepted as 0.
- C-14 date-time separator: Terminology says `T`/`t`; FP-02 also allows space. Built: `T`, `t` and space all accepted.

## Unstated details (assumptions)
- `load` with invalid UTF-8: not specified; raises `TOMLDecodeError` with `doc=""`, `pos=0`.
- `load` text-mode detection: `fp.read()` returning `str` raises `TypeError`.
- A non-callable `parse_float` raises `TypeError` (not specified).
- Control characters (other than tab) and DEL in comments are refused, as TOML says.
- `\x7f` (DEL) raw in strings is refused.
- `TOMLDecodeError` end-of-document reports "end of document" when `pos >= len(doc)`.
- Offset date-times with offsets (`+HH:MM`) require HH 00-23, MM 00-59.
- Heavily nested input may hit Python's recursion limit; that RecursionError is not converted.
