# Specification conflicts

All entries are in `spec/Full_PRD.md` unless noted.

1. **Slice of a non-array: null vs empty array**
   - FP-03 Normal behavior: "A slice on a value that is not an array yields null."
   - FP-03 Boundary / error behavior: "A slice of a value that is not an array is the empty array."
   - Why: the same input (a slice applied to a non-array) cannot return both null and the empty array.

2. **Zero slice step: empty array vs failure**
   - FP-03 Normal behavior: "A step of 0 selects nothing: the result is the empty array."
   - FP-03 Boundary: a step of 0 "does not succeed ... zero-slice-step kind ... not a successful empty array". Terminology (Failure kind) and Interface_Contract (Failure carriers) also list zero slice step as a refusal.
   - Why: a slice with step 0 cannot both succeed with `[]` and be refused.

3. **Filter on a non-array: null vs empty array**
   - FP-04 Normal and Boundary: a filter on a non-array "yields null, not an empty array".
   - FP-06 Normal behavior: "A filter applied to anything but an array yields the empty array."
   - Why: the same filter on a non-array cannot return both null and `[]`.

4. **Object wildcard on a non-object: empty array vs null**
   - Terminology (Projection): "An object wildcard applied to a non-object is the empty array."
   - FP-04 Normal behavior: "An object wildcard on a value that is not an object yields null."
   - Why: the same input cannot give both `[]` and null.

5. **Lone `=`: grammar-level vs token-level syntax failure**
   - Terminology (Grammar-level syntax failure): "A single `=` is a grammar-level failure of this kind."
   - FP-06 Boundary: "A lone `=` is a token-level syntax failure."
   - Why: a lone `=` cannot be both grammar-level (the plain syntax type) and token-level (a strict subclass of it, per Interface_Contract). The two are distinguishable by exception type.

6. **String length: UTF-8 bytes vs characters**
   - Terminology (String): "its length is its number of UTF-8 bytes."
   - FP-07 `length`: "the number of Unicode characters (not bytes) of a string".
   - Why: the length of a non-ASCII string cannot be both its byte count and its character count.

7. **Empty string/array and `not_null`: counted as null vs not null**
   - Terminology (Null): "An empty string or an empty array counts as null for `not_null`."
   - FP-07 `not_null`: "(an empty array or empty string is not null)."
   - Why: `not_null` cannot both skip and return an empty string or array.

8. **`join` of an empty array: null vs empty string**
   - FP-07 intro: "`join` of an empty array yields null."
   - FP-07 `join` bullet: "the empty array yields the empty string."
   - Why: the same call cannot return both null and `""`.

9. **`to_number` result type: always float vs integer for integer numerals**
   - Terminology (Number): "A number made from a string by `to_number` is always a floating-point value."
   - FP-07 `to_number`: "a string that is an integer numeral becomes that integer".
   - Why: `to_number("5")` cannot be both a float and an integer.

10. **Expression reference outside a function argument: null vs non-null**
    - Terminology (Expression reference): "Outside a function argument it evaluates to null."
    - FP-05: searching an expression reference on its own "yields a non-null value". Interface_Contract (Expression reference value) agrees: "returns a non-`None` value".
    - Why: a bare `&expr` cannot evaluate to both null and a non-null value.

11. **Multiselect list on a null current value: builds elements vs yields null**
    - FP-05, multiselect list: "On a null current value it still builds one element per expression."
    - FP-05, same section: "A multiselect list or hash whose current value is null yields null."
    - Why: a multiselect list on a null current value cannot both build an array and yield null.

12. **Raw strings and `\uXXXX` escapes**
    - FP-05 Normal behavior: a raw string literal has "No JSON escapes processed".
    - FP-05 Boundary: "A `\uXXXX` escape inside a raw string literal is decoded to its character."
    - Why: `\uXXXX` is a JSON escape, so it cannot be both left undecoded and decoded.
