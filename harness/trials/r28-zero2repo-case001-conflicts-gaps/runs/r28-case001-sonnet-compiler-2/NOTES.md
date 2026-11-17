# NOTES

Implementation: `src/tomlparse/` (`_parser.py`, re-exported in `__init__.py`). Pure Python, no build step.
All checklist ids are implemented in `_parser.py` (loads, load, TOMLDecodeError, TOML v1.1.0 grammar, parse_float).
Non-goal/constraint ids (no writer, no CLI, no deps, no I/O on import) are satisfied by absence.
No separate test suite was written; the parser was smoke-tested by hand only.

## Contradictions (all 16 were unsettled; each choice follows TOML v1.1.0)
- CF-000001 (N-000135 vs N-000178, multiline quote before closing delimiter): allowed 1–2 quotes before the closing `"""` in both forms; 3+ extra quotes refused (run > 5).
- CF-000008 (N-000112 "line feeds only" vs N-000133 "carriage returns included"): CRLF inside multiline strings becomes LF; a lone CR is refused.
- CF-000009 (N-000130 vs N-000131, first line feed of multiline literal): discarded in both multiline forms (TOML rule).
- CF-000012 (N-000021 vs N-000098): header may declare a not-yet-defined sub-table of a dotted-key table; defining the dotted table itself via header is refused.
- CF-000015 (N-000134 vs N-000136): line-ending backslash strips all whitespace and newlines up to the next non-whitespace character, so leading whitespace of the next line is removed.
- CF-000028 / CF-000035 (tab in literal string vs "must be backslash-t"): raw tab allowed in all string forms (TOML); literal strings get no escape processing.
- CF-000037 (N-000146 vs N-000285, hex case): hex digits accepted in either case; the result is an int, so case of digits is not observable.
- CF-000045 / CF-000069 (N-000156/N-000157 vs N-000292): fractional seconds truncated to six digits, not rounded.
- CF-000059 (N-000106 vs N-000282): trailing comma in arrays is accepted (TOML 1.1.0).
- CF-000062 (N-000028 vs N-000154): seconds may be omitted in local times too (TOML 1.1.0).
- CF-000065 (N-000144 vs N-000168): `+0`/`-0` accepted as 0 (TOML allows it).
- CF-000068 (N-000024 vs N-000153): space separator allowed for all date-times including offset ones.
- CF-000023 / CF-000032 (exact dict/list vs subclasses): parse_float returning a dict/list or subclass instance raises ValueError (isinstance check).

## Unstated details (assumptions)
- `TOMLDecodeError.pos` for a given failure: the start of the offending token/construct (key start for key conflicts, header start for header conflicts); exact positions are not specified.
- `load` with invalid UTF-8 bytes lets `UnicodeDecodeError` (a ValueError) propagate; no BOM handling.
- `load` accepts any object whose `read()` returns bytes; `str` result gives TypeError.
- DEL (0x7f) is treated as a control character in strings and comments (TOML rule).
- Offset hours > 23 or minutes > 59 are refused.
- Very deep nesting may raise RecursionError (not caught).
