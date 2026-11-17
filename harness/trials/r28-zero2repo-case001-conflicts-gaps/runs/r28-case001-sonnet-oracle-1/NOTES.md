# NOTES

Code: `src/tomlparse/` (`_parser.py`, re-exported in `__init__.py`). All checklist ids are treated as implemented by that parser (loads/load/TOMLDecodeError, pure Python, no writer/CLI). No tests were written beyond manual smoke checks.

## Spec disagreements and what was built (all 20 are UNSETTLED in MAP.md; the real TOML v1.1.0 rule was chosen)
- CF-000023/032/073 (PRD terminology N-000029 "Only ... exactly `dict` or exactly `list` is refused" vs Contract N-000296 "(or a subclass instance)", FP-05 N-000230, N-000038): built refusal by `isinstance` (subclasses refused) -> `ValueError`.
- CF-000037 (N-000146 "hex digits may be either case" vs N-000285 "hexadecimal digits written in lowercase"): integers are ints, so case is irrelevant; uppercase hex digits accepted.
- CF-000072 (N-000139 escape hex digits case-insensitive vs N-000176 uppercase escape digits refused): accepted either case.
- CF-000045/069 (N-000156/N-000157 truncate to 6 digits vs N-000292 round): truncation (explicit "not rounded" in PRD).
- CF-000059 (N-000106 trailing comma allowed vs N-000282 refused): trailing comma allowed (TOML 1.1, FP-01).
- CF-000074 (N-000090 empty quoted key allowed vs N-000279 keys never empty): empty quoted key accepted.
- CF-000012 (N-000021 vs N-000098): dotted-key-created table cannot be re-declared by header itself, but undefined sub-tables of it may be declared by header.
- CF-000062 (N-000028 local-time seconds always written vs N-000154 seconds optional): seconds optional (1.1).
- CF-000068 (N-000024 T/t only vs N-000153 T/t/space): space accepted for all date-times.
- CF-000065 (N-000144 signed zero ok vs N-000168 refused): `+0`/`-0` accepted as 0.
- CF-000001 (N-000135 vs N-000178 quote before closing delimiter of multiline basic): allowed (up to two quotes).
- CF-000008 (N-000112 CRLF -> LF vs N-000133 CR kept): CRLF becomes LF in multiline strings; lone CR refused.
- CF-000009 (N-000130 literal keeps first LF vs N-000131 discards): first newline discarded in both multiline forms.
- CF-000015 (N-000134 line-ending backslash trims whitespace vs N-000136 leading whitespace kept): trimmed, per TOML.
- CF-000028/035/071 (N-000143 raw tab must be `\t` vs N-000141/N-000129/N-000178 tab allowed): raw tab allowed in all strings; no escapes in literal strings.

## Unstated details (assumed)
- Invalid UTF-8 in `load`: raises `TOMLDecodeError("Invalid UTF-8...", "", 0)`.
- `load` raises TypeError when `fp.read()` returns `str`.
- DEL (0x7f) is treated as a forbidden control character in strings and comments.
- Deeply nested arrays may raise `RecursionError` (not caught).
- Years must be 1-9999 (Python limits); offset hour 0-23 minute 0-59; leap second 60 refused.
- `TOMLDecodeError` with pos outside the doc: lineno/colno are clamped to the end; the report says "end of document".
