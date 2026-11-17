# NOTES

Implementation: package `pathsel/` (lexer, Pratt parser, tree interpreter, functions). Tests: `tests/`.
Failure types (all `ValueError`): `EmptyExpressionError`, `IncompleteExpressionError`, `ParseError` (syntax),
`LexerError` (subclass of `ParseError`, token-level), `SliceStepError`, `UnknownFunctionError`, `ArityError`,
`InvalidTypeError`; syntax/incomplete carry `lex_position`. A zero slice step is refused at compile time.
Checklist ids are all covered by the behaviour below; none is left undone.

## Unsettled conflicts (CF-…) — what I chose
- CF-000015 not_null: Terminology (N-000022) says empty string/array count as null; FP-07 (N-000300) says they are not null. Built: not null (only `None` is skipped).
- CF-000027 object wildcard on non-object: Terminology (N-000031) says empty array; FP-04 (N-000165) says null. Built: null.
- CF-000035 string length: Terminology (N-000026) says UTF-8 bytes; FP-07 (N-000277) says Unicode characters. Built: characters.
- CF-000005 filter on non-array: FP-04 (N-000202) null vs FP-06 (N-000259) empty array. Built: null.
- CF-000007 slice on non-array: FP-03 (N-000142) null vs the FP-03 boundary section (N-000157) empty array. Built: null.
- CF-000011 multiselect list on null current value: FP-05 (N-000212) one element per expression vs (N-000218) null. Built: null (hash and list).
- CF-000049 raw string: N-000227 "No JSON escapes are processed" vs N-000239 "`\uXXXX` is decoded". Built: no escapes processed (only `\'` → `'`).

## Other disagreements found (not flagged in the spec)
- Lone `=`: Terminology says grammar-level; FP-06 says token-level. Built: grammar-level (`ParseError` itself, position of `=`).
- Dot followed by end of text: FP-01/FP-02 say syntax kind, whereas the "incomplete" rule would say incomplete. Built: syntax kind (position = text length).
- `to_number`: Terminology says a number from a string is always float; FP-07 says an integer numeral becomes an integer. Built: integer numeral -> int, else float.
- `join` of empty array: FP-07 preamble says null; the function entry says empty string. Built: empty string.

## Unstated, assumed
- Arrays: `list` and `tuple`. Objects: any `collections.abc.Mapping` (also accepted for function "object" args).
- `type()` of a non-JSON host value returns "object". An expression reference passed where "any" is expected is invalid-type.
- Commas in function arguments are required between args; trailing comma is a syntax failure.
- Literal `NaN`/`Infinity` in backticks are not JSON (read as string content).
- `merge` builds its result with the options' `dict_cls` if given, else `dict`.
- Slice directly after an index/slice starts a projection (implementer's choice in FP-04).
- Custom `signature` also accepts extra type names (`any`, `boolean`, `expref`, `array-number`, `array-string`) and `"variadic": true`; empty `types` means any.
- Non-str expression raises `TypeError`.
