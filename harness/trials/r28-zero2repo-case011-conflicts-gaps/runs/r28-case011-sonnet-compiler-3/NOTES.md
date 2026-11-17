# NOTES

Layout: package `pathsel/` (flat, no build step): `lexer.py`, `parser.py` (Pratt parser, jmespath-style binding powers),
`interpreter.py`, `functions.py` (`Functions`, `signature`), `exceptions.py`. Tests: `tests/test_basic.py`.
Every claim id in the checklist is treated as implemented (behaviour in the packs) except where a conflict below picks one side.
Failure types (all `ValueError`): `EmptyExpressionError`, `IncompleteExpressionError`, `ParseError` (grammar syntax),
`LexerError(ParseError)` (token-level), `SliceStepError`, `UnknownFunctionError`, `ArityError`, `PathselTypeError`.
`lex_position` is on syntax/incomplete errors.

## Conflicts (spec disagrees with itself) and what I built
- CF-000005 filter on non-array: FP-04 N-000202 says null; FP-06 N-000259 says empty array. Built: **null**.
- CF-000007 slice on non-array: FP-03 N-000142 "yields null" vs N-000157 "is the empty array". Built: **null**.
- CF-000011 multiselect list on null current value: FP-05 N-000212 "still builds one element per expression" vs N-000218 "yields null". Built: **null** (for lists and hashes).
- CF-000015 not_null: Terminology N-000022 "empty string/array counts as null for not_null" vs FP-07 N-000300 "an empty array or empty string is not null". Built: **not null** (function definition wins).
- CF-000027 object wildcard on non-object: Terminology N-000031 "empty array" vs FP-04 N-000165 "yields null". Built: **null**.
- CF-000035 string length: Terminology N-000026 "number of UTF-8 bytes" vs FP-07 N-000277 "Unicode characters (not bytes)". Built: **characters**.
- CF-000049 raw strings: FP-05 N-000227 "No JSON escapes are processed" vs N-000239 "`\uXXXX` ... decoded". Built: only `\'` and `\uXXXX` (with surrogate pairs) are decoded; every other backslash sequence is kept literally.
- Unflagged: FP-03 normal bullet says slice step 0 "selects nothing: empty array"; boundary section says step 0 is refused as the zero-slice-step kind. Built: **refused** (raised at compile time, so both entries refuse).
- Unflagged: FP-07 preamble says `join` of an empty array yields null; the `join` bullet says the empty string. Built: **empty string**.
- Unflagged: FP-03 boundary last sentence "A slice of a value that is not an array is the empty array" is the CF-000007 conflict; resolved as above.

## Not stated, assumed
- Trailing comma in a function argument list (`f(a,)`): accepted (jmespath behaviour); spec only forbids it in multiselects.
- Arrays are `list` only (tuples/sets are "other host values": selectable, but invalid-type for functions needing a type).
- Objects: any `Mapping`, or any object with `keys` and `__getitem__` (so custom `dict_cls` types work).
- `type()` of an unrecognised host value returns "object"; `to_string` falls back to `str()` for non-JSON host values.
- `to_number` accepts only ASCII numerals without surrounding whitespace.
- `merge` returns a plain `dict`; custom `dict_cls` instances are accepted wherever an object is required.
- A slice written directly after an index/slice starts a projection (jmespath behaviour); a dot followed by multiselect on a RHS lets later steps join it per binding powers.
- Function name is checked before arguments are evaluated; arity before argument evaluation; types after.
- Quoted identifiers use strict JSON string decoding (raw control characters rejected; escapes allowed).
- A bare expression reference returns an `Expref` object.
