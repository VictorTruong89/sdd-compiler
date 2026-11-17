# NOTES

Implementation: package `pathsel/` (flat layout; no build step). Pratt parser + tree interpreter.

## Spec conflicts and what was built

1. **Slice of a non-array.** FP-03 Normal: "A slice on a value that is not an array yields null." FP-03 Boundary: "A slice of a value that is not an array is the empty array." Built: null.
2. **Slice step 0.** FP-03 Normal: "A step of 0 selects nothing: the result is the empty array." FP-03 Boundary: step 0 "does not succeed ... zero-slice-step kind". Built: raises `ZeroSliceStepError` (at search time).
3. **Filter on a non-array.** FP-04: "a filter on a non-array yields null". FP-06: "A filter applied to anything but an array yields the empty array." Built: null.
4. **Lone `=`.** Terminology and FP-01: grammar-level syntax failure. FP-06: "A lone `=` is a token-level syntax failure". Built: grammar-level (`ParseError`, not `LexerError`), position of the `=`.
5. **Multiselect list on null.** FP-05: list "on a null current value it still builds one element per expression" vs "A multiselect list or hash whose current value is null yields null." Built: null for both.
6. **`join` of empty array.** FP-07 intro: "`join` of an empty array yields null"; function list: "the empty array yields the empty string". Built: empty string.
7. **`to_number` of an integer string.** Terminology: "A number made from a string by `to_number` is always a floating-point value"; FP-07: integer numeral becomes that integer. Built: integer for integer numerals, float otherwise.

## Unstated items (assumptions)

- Trailing comma in a function argument list (`f(a,)`) is not specified; it is accepted (as in the JMESPath-style grammar).
- Order of checks when a call fails in several ways: name, then arity (from the written argument count), then argument evaluation and types.
- Arrays are Python `list` only; tuples and other host values are non-JSON values (selectable, but invalid-type for typed function arguments). Objects are any `collections.abc.Mapping`.
- `type()` of a non-JSON host value returns `"object"`. `to_string` of such values uses `str()`.
- `<`/`<=`/`>`/`>=` on incomparable types (e.g. string vs number, booleans) yield null.
- `to_number` strings: optional sign, digits, optional fraction/exponent, surrounding whitespace allowed; `nan`/`inf`/underscores yield null.
- Lexing is eager, so token-level failures anywhere are reported before grammar-level ones.
- Custom function signature types also support `any`, `boolean`, `expref`, `array-number`, `array-string`, an empty/missing `types` meaning any, and `"variadic": True` on the last spec.
- Exception types (in `pathsel.errors`): `EmptyExpressionError`, `ParseError` (syntax), `LexerError` (subclass of `ParseError`), `IncompleteExpressionError`, `ZeroSliceStepError`, `UnknownFunctionError`, `InvalidArityError`, `InvalidTypeError`; all `ValueError`. Syntax and incomplete errors carry `lex_position`.
