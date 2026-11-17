# NOTES

Implementation: package `pathsel/` (flat layout). Parser is a Pratt parser (JMESPath-style binding powers) in `parser.py`; evaluation in `interpreter.py`; built-ins and `signature` in `functions.py`; failure types in `exceptions.py`. No tests were written beyond manual checks; all 423 checklist ids are covered by the implementation unless listed below as a conflict resolution.

## Spec disagreements (and what I built)
- CF-000015 not_null: Terminology (pack 02, N-000022) says empty string/array count as null for `not_null`; FP-07 (N-000300) says an empty array or string is not null. Built: empty string/array are NOT null (only `None` is skipped).
- CF-000027 object wildcard on non-object: pack 02 (N-000031) says empty array; FP-04 (N-000165) says null. Built: null.
- CF-000035 string length: Terminology (N-000026) says UTF-8 bytes; FP-07 `length` (N-000277) says Unicode characters. Built: characters (`len(str)`).
- CF-000056 bare expression reference: Terminology (N-000028) says null outside function argument; FP-05 (N-000234) and Interface Contract (N-000423) say non-null. Built: non-null `Expref` object.
- CF-000057 to_number: pack 02 (N-000023) says always float; FP-07 (N-000287) says integer numeral becomes int. Built: integer numeral -> int, decimal/exponent -> float.
- CF-000007 slice of non-array: FP-03 (N-000142) null vs boundary section (N-000157) empty array. Built: null.
- CF-000055 slice step 0: N-000133 says empty array; N-000152 says refused with its own kind. Built: refused (`SliceStepZeroError`, a ValueError, not a Syntax subclass), raised at compile/parse time so both entries refuse.
- CF-000005 filter on non-array: FP-04 (N-000202) null vs FP-06 (N-000259) empty array. Built: null.
- CF-000011 multiselect on null current value: N-000212 builds elements; N-000218 yields null. Built: null (both list and hash).
- CF-000049 raw string `\uXXXX`: N-000227 "no JSON escapes processed" vs N-000239 decoded. Built: not decoded (only `\'` -> `'`).
- CF-000054 join of empty array: N-000268 null vs N-000280 empty string. Built: empty string.
- Unlisted: a lone `=` — Terminology (pack 02) calls it a grammar-level failure; FP-06 (N-000260) says token-level. Built: token-level (`LexerError`, subclass of `ParseError`).

## Unstated items and assumptions
- Position of `lex_position` for errors raised from a failed token-level read: offset where that token starts; end-of-text = len(expression). Dot followed by end of text is a plain syntax error (as FP-01 states), not incomplete.
- Trailing comma in function arguments (`f(a,)`): not stated; treated as syntax error.
- `type()` of a host value that isn't a JSON type: unstated; returns "null". `any`-typed arguments reject expression references (invalid-type).
- Ordering comparators (`<` etc.) on non-number/non-string operand pairs yield null (unstated).
- `sum([])` = 0; `avg`/`max`/`min` empty -> null. `merge` returns a plain `dict`.
- Object arguments: any `collections.abc.Mapping` (or duck-typed mapping with `keys`/`__getitem__`) is accepted. Tuples are treated as arrays.
- `contains(array, x)` uses JSON equality (bool != number). `contains(string, non-string)` is false.
- Custom `signature` also internally accepts extra type names (`any`, `boolean`, `expref`, `array-number`, `array-string`) and `variadic`; the public five names are as contract.
- Whether a slice directly after an index/slice starts a projection: chose yes (projection).
