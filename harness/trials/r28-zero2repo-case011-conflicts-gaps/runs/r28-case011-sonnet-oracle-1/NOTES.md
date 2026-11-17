# NOTES

Layout: `pathsel/` package (flat, repo root). `pathsel.search`, `pathsel.compile`, `pathsel.functions.{Functions,signature}`.
Exceptions in `pathsel/exceptions.py` (all `ValueError`): `EmptyExpressionError`, `IncompleteExpressionError`, `SyntaxFailure` (grammar-level), `TokenSyntaxFailure` (subclass, token-level), `ZeroSliceStepError`, `UnknownFunctionError`, `InvalidArityError`, `InvalidTypeError`. Syntax/incomplete carry `lex_position`.
Design follows the JMESPath grammar (Pratt parser); every checklist id is covered by that behaviour except where listed below.

## Spec conflicts (all 11 open ones) and what I built
- CF-000015 not_null: pack 02 says empty string/array count as null; FP-07 (N-000300) says they are not null. Built: not null (only `None` is skipped).
- CF-000027 object wildcard on non-object: pack 02 "empty array" vs FP-04 "null". Built: null.
- CF-000035 length: pack 02 "UTF-8 bytes" vs FP-07 "Unicode characters". Built: characters (`len(str)`).
- CF-000056 bare expression reference: pack 02 "evaluates to null" vs FP-05/Interface Contract "non-null". Built: non-null `Expref` object.
- CF-000057 to_number: pack 02 "always floating-point" vs FP-07 integer numeral becomes int. Built: `'42'` -> `42` (int); decimal/exponent numerals -> float.
- CF-000007 slice of non-array: FP-03 says null in one place, "empty array" in another. Built: null.
- CF-000055 slice step 0: "selects nothing, empty array" vs "does not succeed, zero-slice-step kind". Built: refusal with `ZeroSliceStepError`, raised at compile time (so `compile` itself refuses).
- CF-000005 filter on non-array: null vs empty array (FP-04 vs FP-06 text). Built: null.
- CF-000011 multiselect list on null current value: "one element per expression" vs "yields null". Built: null (both list and hash).
- CF-000049 raw string `\uXXXX`: "no JSON escapes processed" vs "decoded". Built: no escapes except `\'`; `\uXXXX` stays literal text.
- CF-000054 join of empty array: null vs empty string. Built: empty string.

## Other disagreements (not marked as conflicts)
- Lone `=`: terminology says grammar-level syntax failure, FP-06 says token-level. Built: token-level (`TokenSyntaxFailure`, a Syntax subclass).
- Dot at end of text (`a.`): "incomplete" rule (operand required at end) vs FP-01/FP-02 explicitly listing it as syntax. Built: syntax kind, position = text length.

## Unstated, assumed
- Bare numbers (e.g. `foo(1)`) are not expressions; syntax error (numbers only via backtick literals, indices, slices).
- `type()` of a non-JSON host value or expref returns `"null"`; `any` accepts every value.
- `object` argument types accept any `collections.abc.Mapping`; `merge` returns a plain `dict`. Tuples are treated as arrays.
- Function checks: name, then arity (before arguments are evaluated), then types (after).
- Ordering comparisons of unlike types yield null (JMESPath convention).
- Custom signature type names additionally accept `"any"`, `"boolean"`, `"expref"`; `{"variadic": True}` on the last spec is supported.
- Slice after an index starts a projection (implementer choice allowed); a multiselect after a dot joins later tight steps per the Pratt rules.
- `to_string` of host Decimal writes it as a float.
- No tests were added to the repo.
