# NOTES

Implementation: `src/tomlparse/_parser.py` (pure Python, hand-written parser). No tests were written beyond manual checks.
All checklist ids are treated as implemented via the behaviour below, except as noted.

## Spec disagreements (all 16 UNSETTLED conflicts) and what I built
- CF-000001 (pack 12: multiline "may contain one or two quotes ... directly before the closing delimiter" N-000135 vs FP-02 error list "a quote character directly before the closing delimiter of a multiline basic string" N-000178): built TOML 1.1 behaviour: `"""a""""` is accepted (value `a"`); six or more quotes in a row are refused.
- CF-000008 (N-000112 CRLF "holds line feeds only" vs N-000133 "carriage returns included"): CRLF is normalised to LF everywhere (N-000112 wins; also FP-01 "everywhere").  A lone CR is a control character and refused.
- CF-000009 (N-000130 literal keeps first LF vs N-000131 discards it): first LF after the opening delimiter is discarded in both multiline forms (TOML).
- CF-000012 (N-000021 dotted-key table cannot get sub-table via header vs N-000098): a header may define a not-yet-defined sub-table below a dotted-key table (`[a.b.c]` after `a.b.x=1` in `[a]`), but a header naming the dotted-key table itself is refused.
- CF-000015 (N-000134 line-ending backslash strips following whitespace vs N-000136 next line's leading whitespace kept): backslash strips all whitespace/newlines up to the next non-whitespace char (TOML); N-000136 not followed.
- CF-000023 / CF-000032 (N-000029 only exact dict/list vs N-000296, N-000038, contract table): subclass instances of dict/list are also refused with ValueError (Interface Contract wins).
- CF-000028 / CF-000035 (tab in a one-line string must be written `\t` vs literal strings having no escapes): literal strings take a raw tab as written, and basic strings also accept a raw tab (TOML allows it; other control characters are refused).
- CF-000037 (hex digits either case vs lowercase): input hex digits of either case accepted; ints are Python ints so "lowercase" has no observable effect.
- CF-000045 / CF-000069 (fraction truncated to 6 digits vs rounded): truncated (FP-02, explicit "not rounded").
- CF-000059 (trailing comma in arrays allowed vs refused): allowed (TOML 1.x, FP-01).
- CF-000062 (local time seconds always written vs may be omitted): seconds optional (TOML 1.1).
- CF-000065 (`+0`/`-0` accepted vs refused): accepted as integer 0 (TOML).
- CF-000068 (offset date-time joined by T/t vs space allowed): space, `T`, `t` all accepted.

## Unstated items / assumptions
- FP-02 says "escape digits written as uppercase letters" are refused while also saying hex digits are case-insensitive: I accept both cases.
- Invalid UTF-8 bytes in `load`: raises `TOMLDecodeError` with doc `""` and pos 0 (not stated).
- Excessively nested documents (RecursionError) become `TOMLDecodeError` at pos 0 (decode error must not be a recursion error).
- Error offsets are mapped back to the original text when CRLF was normalised.
- Control chars: DEL (0x7f) and C0 chars other than tab are refused in strings and comments.
- `load` reads `fp.read()`; a str result means text mode -> TypeError.
- Python 3.8 syntax only; `parse_float` result is checked for dict/list only when `parse_float` is not the builtin `float`.
