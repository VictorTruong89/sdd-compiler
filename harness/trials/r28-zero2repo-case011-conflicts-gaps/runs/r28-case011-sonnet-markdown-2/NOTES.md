# NOTES

Layout: package `pathsel/` (exceptions, lexer, parser, interpreter, functions). A Pratt parser; binding powers follow the ranks in FP-04/FP-06.

## Spec disagreements (what I built)
- **String length**: Terminology says a string's "length is its number of UTF-8 bytes"; FP-07 `length` says "number of Unicode characters (not bytes)". Built: characters.
- **`join` of empty array**: FP-07 intro says "`join` of an empty array yields null"; the `join` bullet says "the empty array yields the empty string". Built: empty string.
- **Multiselect list on null current value**: FP-05 bullet 2 says it "still builds one element per expression"; bullet 4 says a list or hash with null current value "yields null". Built: null for both.
- **Slice / filter on non-array**: FP-03 and FP-04 say null; the FP-03 boundary section ("is the empty array") and FP-06 ("A filter applied to anything but an array yields the empty array") say empty array. Built: null.
- **Trailing dot (`a.`)**: FP-01 incomplete-expression definition (ends where an operand must begin) vs. FP-01 syntax list (dot followed by end of text). Built: syntax kind at position = text length. Other EOF-in-the-middle cases are the incomplete kind.
- **`=` lone**: FP-01 calls it grammar-level, FP-06 token-level. Built: token-level (LexerError, subclass of syntax type).
- **Slice zero step**: raised when the expression is compiled (after the whole text parsed successfully), regardless of the data.

## Unspecified, assumed
- `to_number` accepts only strict numerals (`[+-]?digits`, decimal/exponent forms); whitespace, `nan`, `inf` give null.
- `any`-typed args (including custom provider `types`) reject expression references (invalid-type). Custom signature types are only number/string/array/object/null (plus optional `"variadic": true` on the last spec, and extra names `any`, `boolean`, `expref` are accepted).
- Any `collections.abc.Mapping` counts as an object; `list`/`tuple` count as arrays.
- `merge` returns a plain `dict`. `contains` on an array uses JSON equality (1 != true). String needle of a non-string for `contains(string, x)` → false.
- A literal in backticks that is invalid JSON becomes the string content (leading whitespace stripped); `NaN`/`Infinity` are not JSON.
- Slice after an index (`a[0][1:2]`) starts a projection; dot + multiselect right-hand side does not take later steps.
- Bare expression reference returns an `Expref` object.
