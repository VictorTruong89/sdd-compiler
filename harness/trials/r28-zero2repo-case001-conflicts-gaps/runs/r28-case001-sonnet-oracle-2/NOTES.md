# Notes

Implementation: `src/tomlparse/` (`_parser.py`, hand-written recursive-descent parser). Spec ids are covered by the
package as a whole (`# spec:` marks only on the public surface). No separate tests were written.

## Spec disagreements and what was built
In every case the real TOML v1.1.0 behaviour (which the PRD names as authority) was chosen.
- CF-000001: N-000135 (pack 12) multiline strings may end in 1-2 quote chars vs N-000178 refusing a quote before the closing delimiter of a multiline basic string. Built: allowed (up to two quotes before closing `"""`).
- CF-000008: N-000112 "holds line feeds only" vs N-000133 "carriage returns included". Built: CRLF -> LF everywhere (input normalised up-front; `TOMLDecodeError.doc` is the normalised text). A lone CR is a control-character error.
- CF-000009: N-000130 literal keeps first line feed vs N-000131 discarded in both. Built: first newline after opening delimiter dropped in both.
- CF-000012: N-000021 (dotted-key table cannot receive sub-table via header) vs N-000098. Built: `[a.b.c]` allowed when `a.b` came from dotted keys and `c` is undefined; `[a.b]` itself is refused.
- CF-000015: N-000134 line-ending backslash trims next line's whitespace vs N-000136 keeps it. Built: trimmed (TOML).
- CF-000028/35/71: N-000143 "tab must be written as \t" vs raw tabs allowed (N-000178) / no escapes in literals. Built: raw tab allowed in all strings.
- CF-000037: hex digits either case (N-000146) vs "lowercase" (N-000285). Built: either case accepted; result is an int.
- CF-000045/69: round (N-000292) vs truncate (N-000156/157). Built: truncate to 6 digits.
- CF-000059: trailing comma in arrays allowed (N-000106) vs refused (N-000282). Built: allowed.
- CF-000062: local-time seconds optional (N-000154) vs always written (N-000028). Built: optional.
- CF-000065: `+0`/`-0` accepted as 0 (N-000144) vs refused (N-000168). Built: accepted.
- CF-000068: space separator allowed (N-000153) vs T/t only for offset date-time (N-000024). Built: T, t, space for all.
- CF-000072: hex escape digits case-insensitive (N-000139) vs uppercase refused (N-000176). Built: both cases accepted.
- CF-000074: empty quoted key allowed (N-000090) vs never empty (N-000279). Built: allowed.
- CF-000023/32/73: parse_float returning dict/list subclass: refused (N-000296, N-000038) vs only exact types (N-000029). Built: `isinstance` check, subclasses refused with ValueError.

## Unstated, assumed
- Invalid UTF-8 in `load`: not specified; raises `TOMLDecodeError("Invalid UTF-8", ...)` with replacement-decoded doc.
- Excess nesting (RecursionError) is converted to `TOMLDecodeError`.
- `parse_float` receives the raw token (underscores kept); default `float` accepts them.
- Seconds of 60 (leap second) refused, per PRD (0-59).
- Tables from implicit header paths may later be defined once by their own header; dotted-key extension of a header-created table is refused.
