# NOTES

Package: `src/tomlparse` (`loads`, `load`, `TOMLDecodeError`). Spec ids are marked `# spec:` in code where
convenient; every id is covered by the single parser (`_parser.py`) and error class (`_errors.py`).
No tests were written beyond ad-hoc checks. Not done: nothing intentionally omitted.

## Spec disagreements (all 16 UNSETTLED conflicts) and what I built
I followed the TOML v1.1.0 language where the two sides disagree.
- CF-000001 (pack 12 N-000135 "quote directly before closing delimiter" allowed vs N-000178 refused for multiline basic): built TOML behaviour: 1–2 quotes directly before the closing `"""` are accepted in both multiline forms (3+ extra quotes, i.e. a run over 5, is refused).
- CF-000008 (N-000112 CRLF holds line feeds only vs N-000133 CRs kept): built CRLF -> LF inside strings (N-000111 is a constraint "everywhere"). A lone CR is refused.
- CF-000009 (N-000130 multiline literal keeps first LF vs N-000131 discarded in both): first newline discarded in both.
- CF-000012 (N-000021 dotted-key table can't get sub-table by header vs N-000098 may): a header may declare an undefined sub-table beneath a dotted-key table; the dotted table itself cannot be redefined by header.
- CF-000015 (N-000134 trims all whitespace after line-ending backslash vs N-000136 next line's leading whitespace kept): trimmed (TOML).
- CF-000023 / CF-000032 (N-000029 only exact dict/list refused vs N-000296 / N-000038 / N-000233 subclasses too): subclasses refused with ValueError.
- CF-000028 / CF-000035 (N-000143 "tab must be written \t" vs literal strings having no escapes; and TOML allows raw tab): raw tabs are accepted in every string form.
- CF-000037 (N-000146 hex digits either case vs N-000285 lowercase): either case accepted on input; the result is a Python int so case is moot.
- CF-000045 / CF-000069 (N-000156/N-000157 truncate vs N-000292 round): truncation to 6 digits.
- CF-000059 (N-000106 trailing comma in arrays allowed vs N-000282 refused): allowed (TOML 1.1, FP-01).
- CF-000062 (N-000028 seconds always written vs N-000154 optional): optional (TOML 1.1).
- CF-000065 (N-000144 signed zero ok vs N-000168 refused): accepted (`+0`, `-0` are 0), as TOML.
- CF-000068 (N-000024 `T`/`t` only vs N-000153 space allowed): space allowed too.

## Unstated items I assumed
- Invalid UTF-8 in `load`: raises TOMLDecodeError (doc = lossy-decoded text, pos = bad byte index capped to length). A UTF-8 BOM is not stripped.
- Excessive nesting (RecursionError) is converted to TOMLDecodeError.
- DEL (0x7f) and control chars (except tab) are refused in strings and comments.
- Leap second (`:60`) refused, per the PRD (second 0–59). Offsets must have hour <= 23, minute <= 59.
- `parse_float` receives the token as written, but the default `float` gets underscores stripped.
- Dotted keys may not extend a table created via a header (even implicitly via `[a.b.c]` then `[a]` `b.x=1`).
- `load` accepts any object whose `read()` returns bytes; a `str` result gives TypeError.
