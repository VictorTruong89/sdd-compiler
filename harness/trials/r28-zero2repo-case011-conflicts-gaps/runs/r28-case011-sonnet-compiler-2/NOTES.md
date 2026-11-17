# NOTES

Implementation: package `pathsel/` (flat layout): `lexer.py`, `parser.py` (Pratt parser), `interp.py`, `functions.py` (`Functions`, `signature`), `exceptions.py`, `__init__.py` (`search`, `compile`). No build step. All N-ids in CHECKLIST.md are implemented as described below; the spec-text-only/non-behavioural ids (hardware, packaging, non-goals) are satisfied by the pure-Python, dependency-free layout. No test suite was written beyond ad-hoc manual checks.

## Contradictions (choice made)
Unsettled (CF-ids) — in each case I chose the more specific/JMESPath-conventional side:
- CF-000005 (pack 09/11): filter on a non-array — "yields null" (FP-04 N-000202) vs "yields the empty array" (FP-06 N-000259). Built: null.
- CF-000007 (pack 08): slice on a non-array — null (N-000142) vs empty array (N-000157). Built: null.
- CF-000011 (pack 10): multiselect list on null current value — "still builds one element per expression" (N-000212) vs "yields null" (N-000218). Built: null (lists and hashes).
- CF-000015 (pack 02/12): `not_null` with empty string/array — Terminology N-000022 says counts as null; FP-07 N-000300 says not null. Built: not null (only None is skipped).
- CF-000027 (pack 02/09): object wildcard on non-object — empty array (N-000031) vs null (N-000165). Built: null.
- CF-000035 (pack 02/12): string length — UTF-8 bytes (N-000026) vs Unicode characters (N-000277). Built: characters.
- CF-000049 (pack 10): raw string `\uXXXX` — "No JSON escapes are processed" (N-000227) vs "decoded to its character" (N-000239). Built: not decoded; only `\'` becomes `'`.

Other disagreements I found (not flagged in the export):
- Single `=`: Terminology says grammar-level syntax failure; FP-06 says token-level. Built: token-level (`LexerError`, subclass of `PathSyntaxError`).
- `join` of empty array: FP-07 intro says null; the function entry says the empty string. Built: empty string.
- Slice step 0: FP-03 normal behaviour says empty array; its boundary section says zero-step failure. Built: failure (`ZeroSliceStepError`), raised at search time, regardless of the value being sliced.
- Expression reference outside a function argument: Terminology says null; FP-05 and the Interface Contract say a non-null value. Built: non-null `Expref` object.
- Whole-text empty-expression only for zero-length; "foo." (dot then end of text) is syntax, not incomplete, as FP-01 says.

## Not stated, assumed
- Lexing happens fully before parsing (a token-level failure anywhere wins over an earlier grammar failure).
- `type()` of a non-JSON host value returns "object"; `length`, etc. refuse such values as invalid-type.
- Tuples are treated as arrays; any `Mapping` (or object with keys/items/__getitem__) is an object, so hashes of any `dict_cls` are accepted where functions need an object.
- `contains(string, non-string)` returns false. `to_number` accepts an optional leading sign; no whitespace; "nan"/"inf" give null.
- `merge` returns a plain `dict`. `to_string` of a Decimal writes it as a float.
- Custom function `signature` supports internal `"types"` names number/string/array/object/null (plus boolean/any); an extra `"variadic": true` key is used by built-ins.
- Exception types: `EmptyExpressionError`, `IncompleteExpressionError`, `PathSyntaxError`, `LexerError(PathSyntaxError)`, `ZeroSliceStepError`, `UnknownFunctionError`, `InvalidArityError`, `InvalidTypeError`, all under `PathSelError(ValueError)`, importable from `pathsel`.
- Implementer-choice placements (slice after index; later steps after dot+multiselect) follow jmespath.py-style binding powers.
