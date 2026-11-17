# NOTES

Package: `pathsel/` (exceptions, parser = lexer + Pratt parser, interpreter, functions). No build step.

## Spec conflicts and what was built (ids from spec/CONFLICTS.md)
- C-01 bare expref: Terminology says "evaluates to null"; FP-05 and Interface Contract say non-null. Built: non-null `Expref` object.
- C-02 `not_null`: Terminology says empty string/array count as null; FP-07 says they are not null. Built: only `None` is null (empty values are returned).
- C-03 object wildcard on non-object: Terminology says empty array; FP-04 says null. Built: null.
- C-04 filter on non-array: FP-04 says null; FP-06 says empty array. Built: null.
- C-05 slice on non-array: FP-03 normal says null, boundary says empty array. Built: null.
- C-06 slice step 0: normal behavior says empty array; boundary + Interface Contract say refusal. Built: refusal (`ZeroSliceStepError`, raised at compile time, so both entries refuse).
- C-07 lone `=`: Terminology says grammar-level; FP-06 says token-level. Built: token-level (`LexerError`, subclass of `PathSelSyntaxError`).
- C-08 `join([])`: general paragraph says null, definition says "". Built: "".
- C-09 `to_number("5")`: Terminology says always float, FP-07 says integer numeral -> integer. Built: integer numerals give int, others float.
- C-10 string length: Terminology says UTF-8 bytes, FP-07 says characters. Built: characters (`len(str)`).
- C-11 multiselect list on null current value: one bullet says builds elements, next says yields null. Built: null (for hash too).
- C-12 `length` arity: listed with two slots but described as one value. Built: exactly one argument.
- C-13 `[ ]`: whitespace allowed between tokens vs flatten "nothing between". Built: `[ ]` is flatten (whitespace allowed; also `[ ?`).
- C-14 text ending after a dot (`foo.`): incomplete vs syntax. Built: syntax (explicitly stated in FP-01/FP-02), position = text length.

## Unstated / assumptions
- Arrays are `list` only (tuples/sets are non-JSON host values); objects are any `collections.abc.Mapping` (also accepted as function "object" args, including hashes of any dict_cls). `merge` returns a plain dict.
- Decimal counts as a number in comparisons only; function number args reject it (invalid-type).
- Ordering comparison (`<` etc.) on incompatible types yields null (so filters drop it); booleans are never ordered.
- Function check order: name, arity (from the argument count), then arguments evaluated, then types. Type name `any` rejects expression references.
- Custom functions: extra type names accepted in `signature`: `any`, `boolean`, `expref`, `array-number`, `array-string`; `{"variadic": True}` on last spec allowed. A provider lacking a `_func_` name is unknown-function even if built-in is defined elsewhere.
- Exception types: `EmptyExpressionError`, `IncompleteExpressionError`, `PathSelSyntaxError`, `LexerError`(token-level subclass), `ZeroSliceStepError`, `UnknownFunctionError`, `ArityError`, `InvalidTypeError`, all `ValueError`s in `pathsel.exceptions`. EOF in a place needing an operand/closer is incomplete; position = offset of offending token (text length at EOF).
- `\uXXXX` in raw strings is decoded; other backslashes kept; `\'` is a quote.
- Literal that is invalid JSON falls back to JSON-string content after stripping leading whitespace.
- Slice directly after index/slice starts a projection (implementer's choice).
