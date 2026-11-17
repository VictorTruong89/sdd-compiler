# NOTES

Layout: package `pathsel/` (flat, repo root): `__init__.py` (search, compile, Options),
`parser.py` (lexer + Pratt parser), `interpreter.py`, `functions.py` (Functions, signature), `exceptions.py`.
Exceptions: all `ValueError`; `EmptyExpressionError`, `IncompleteExpressionError`, `ParseError` (grammar syntax),
`LexerError(ParseError)` (token-level), `ZeroSliceStepError`, `UnknownFunctionError`, `ArityError`, `InvalidTypeError`.
Syntax/incomplete carry `lex_position`.

## Conflicts (spec/CONFLICTS.md) and what I built
- C-01 bare expref: Terminology says null; FP-05 and Interface Contract say non-null. Built: non-null `ExpRef` object.
- C-02 not_null: Terminology says empty string/array count as null; FP-07 says they are not null. Built: not null (only None is skipped).
- C-03 object wildcard on non-object: Terminology says empty array; FP-04 says null. Built: null.
- C-04 filter on non-array: FP-04 says null; FP-06 says empty array. Built: null.
- C-05 slice on non-array: FP-03 line 138 says null; line 148 says empty array. Built: null.
- C-06 slice step 0: FP-03 normal says empty array; boundary + contract say refusal. Built: `ZeroSliceStepError` raised at search time (not Syntax subclass), before the array-type check.
- C-07 lone `=`: Terminology says grammar-level; FP-06 says token-level. Built: token-level (`LexerError`).
- C-08 join of empty array: "yields null" (line 230) vs "empty string" (line 242). Built: empty string.
- C-09 to_number: Terminology says always float; FP-07 says integer numeral -> integer. Built: integer numeral -> int, other numerals -> float.
- C-10 string length: bytes (Terminology) vs characters (`length`). Built: characters.
- C-11 multiselect list/hash on null current value: line 187 builds elements; line 188 yields null. Built: null for both.
- C-12 `length` arity: two slots in notation vs one value. Built: exactly one argument (string, array or object).
- C-13 `[ ]`: Built: whitespace inside the brackets is allowed and it is flatten (same for `[ ?`).
- C-14 trailing dot (`foo.`): incomplete vs syntax. Built: syntax (`ParseError`) at position = text length, as FP-01/FP-02 state explicitly.

## Unstated items (assumptions)
- Comparators `< <= > >=` on non-number/non-string or mixed operands: yields null (not stated).
- `contains(string, non-string)`: false.
- `to_number` numerals: regex `[+-]?digits[.digits][e[+-]digits]` (no whitespace, no nan/inf).
- `type()` of a non-JSON host value: "object". An expression reference passed to an "any" parameter: invalid-type.
- `sum([])` = 0; `avg` is true division.
- Object arguments accept any `collections.abc.Mapping`; arrays are `list`/`tuple`; Decimal counts as number.
- Custom signature types: the five contract names, plus internal `any`, `boolean`, `expref`, `array-number`, `array-string`, and optional `"variadic": True` on the last spec.
- Check order of a call: name, arity (before evaluating arguments), then argument types.
- Quoted identifier / literal decoding via `json`; raw control characters inside a quoted identifier are a token-level failure.
- Unquoted number token followed by identifier characters (e.g. `0abc`) is lexed as number then identifier (grammar failure).
- Missing commas in function arguments, and trailing commas, are syntax failures.
- A lone slice index/part given twice (`[1 2:3]`) is a syntax failure.
- Slice directly after an index/slice starts a projection (implementer's choice allowed by spec).
