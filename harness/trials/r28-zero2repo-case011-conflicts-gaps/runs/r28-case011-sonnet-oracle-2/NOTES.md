# NOTES

Implementation: package `pathsel/` (flat layout; `errors.py`, `lexer.py`, `parser.py` (Pratt parser),
`interpreter.py`, `functions.py`, `__init__.py`). No build step. Not done: no test suite was written;
checklist ids were verified only by manual smoke runs.

## Spec conflicts (all listed UNSETTLED in the spec) and what I built
- CF-000005 filter on non-array: N-000202 (FP-04) "yields null" vs N-000259 (FP-06) "yields the empty array". Built: null.
- CF-000007 slice on non-array: N-000142 "yields null" vs N-000157 "is the empty array" (FP-03). Built: null.
- CF-000011 multiselect on null current value: N-000212 "still builds one element per expression" vs N-000218 "yields null" (FP-05). Built: null (list and hash).
- CF-000015 not_null: Terminology N-000022 "empty string or array counts as null" vs N-000300 "an empty array or empty string is not null". Built: empty is NOT null (only None is skipped).
- CF-000027 object wildcard on non-object: N-000031 "is the empty array" vs N-000165 "yields null". Built: null.
- CF-000035 string length: N-000026 "UTF-8 bytes" vs N-000277 "Unicode characters (not bytes)". Built: characters (`len(str)`).
- CF-000049 raw string escapes: N-000227 "No JSON escapes are processed" vs N-000239 "\uXXXX ... is decoded". Built: only `\'` and `\uXXXX` processed; other backslashes kept literally.
- CF-000054 join of empty array: N-000268 "yields null" vs N-000280 "yields the empty string". Built: empty string.
- CF-000055 slice step 0: N-000133 "selects nothing: empty array" vs N-000152 "does not succeed" (own kind). Built: refusal (`SliceStepError`, a ValueError, not Syntax), raised at compile time, so both entries refuse identically.
- CF-000056 expression reference alone: N-000028 "Outside a function argument it evaluates to null" vs N-000234/N-000423 non-null. Built: returns an `ExpRef` object (non-None).
- CF-000057 to_number: N-000023 "always floating-point" vs N-000287 "integer numeral becomes that integer". Built: integer numeral -> int, decimal/exponent numeral -> float.
- Not in the conflict list: a lone `=` is "grammar-level" in Terminology but "token-level" in FP-06 (N-000260). Built: token-level (`LexerError`).
- Layout/FP-01: `a.` (dot followed by end of text) is listed under Syntax in FP-01, while end-of-text where an operand must begin is Incomplete. Built: Syntax for dot-without-rhs, Incomplete elsewhere at EOF.

## Unstated choices
- Non-`str` expression to search/compile: raises `TypeError` (spec only covers str).
- Trailing comma in function arguments is a syntax error. Function args are not expressions-from-numbers: `f(1)` is a syntax error (bare numbers are not expressions; use backticks).
- Slice after index/slice starts a projection (allowed by N-000198). After `.[...]`/`.{...}` rhs no later steps join (N-000199).
- Evaluation order for calls: name, arity checked before evaluating arguments, then types.
- `merge` returns a plain `dict`. Tuples are treated as arrays. Any `collections.abc.Mapping` (or instance of the supplied dict_cls) is an object, and is accepted by `object` arguments.
- `signature` also understands type names `any`, `boolean`, `expref`, `array-number`, `array-string` and `"variadic": True` on the last spec (needed internally); empty `types` means any.
- Failure types: `PathSelError(ValueError)` base; `EmptyExpressionError`, `IncompleteExpressionError`, `ParseError` (syntax), `LexerError(ParseError)`, `SliceStepError`, `UnknownFunctionError`, `ArityError`, `FunctionTypeError` in `pathsel.errors`. Position in `lex_position`.
- Evaluation options: `pathsel.Options(dict_cls, custom_functions)` is published; any object with those attributes works.
