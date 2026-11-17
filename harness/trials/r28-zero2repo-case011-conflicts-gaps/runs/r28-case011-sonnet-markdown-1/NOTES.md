# NOTES

Layout: package `pathsel/` (flat), pure Python, no build step. Pratt parser modelled on JMESPath binding powers.

## Spec disagreements and what I built
1. **Slice / filter on a non-array.** FP-03 normal ("A slice on a value that is not an array yields null") vs FP-03 boundary ("A slice of a value that is not an array is the empty array"); FP-04 ("A filter on a non-array yields null") vs FP-06 ("A filter applied to anything but an array yields the empty array"). Built: null for both.
2. **Lone `=`.** Terminology says it is a grammar-level syntax failure; FP-06 and FP-01's token-level definition say token-level. Built: token-level (subclass of the syntax type).
3. **String length.** Terminology: "its length is its number of UTF-8 bytes"; FP-07 `length`: "number of Unicode characters (not bytes)". Built: characters.
4. **`join` of empty array.** FP-07 preamble: "`join` of an empty array yields null"; the `join` bullet: "the empty array yields the empty string". Built: empty string.
5. **Multiselect on null current value.** FP-05 list bullet: "On a null current value it still builds one element per expression"; same FP: "A multiselect list or hash whose current value is null yields null". Built: null for both.

## Unstated items / assumptions
- Zero slice step is refused at parse (compile) time, so both entries refuse; the spec allows either.
- Token errors are found eagerly (whole text tokenized before parsing), so a token-level failure anywhere wins over an earlier grammar-level one.
- A dot followed by end of text is a syntax failure (per FP-01), position = text length. Other EOF-where-more-is-required cases (including `a[`, `{a`, `f(`) are incomplete-expression.
- `type()` of a non-JSON host value raises invalid-type (spec says "any" accepts everything but `type` must return one of six names).
- `contains(string, non-string)` returns false. `merge` returns a plain dict even with `dict_cls`.
- Objects: any `collections.abc.Mapping` (or instance of `dict_cls`) is accepted as an object everywhere; arrays are `list`/`tuple`.
- `to_number` accepts `[+-]?digits` as int, and `[+-]?(d+.?d*|.d+)([eE][+-]?d+)?` as float; no whitespace/nan/inf.
- Custom `signature` accepts the five documented type names (plus internal extras: boolean, any, expref, array-number, array-string); a bool therefore never matches a custom `number`/etc. parameter.
- Comparators `< <= > >=` on non-comparable operand kinds yield null.
- Raw strings decode `\uXXXX` (surrogate pairs combined); other backslashes are kept, `\'` -> `'`.
- JSON literal rejects NaN/Infinity constants (falls back to string content, then token error).
- Expression reference value is an `Expref` object.
