# Specification conflicts

Paths are relative to `spec/`. "PRD" = `Full_PRD.md`.

## 1. String length: UTF-8 bytes vs Unicode characters
- PRD, Terminology, "String": "its length is its number of UTF-8 bytes."
- PRD, FP-07, `length`: "the number of Unicode characters (not bytes) of a string".
- Why: for a string such as `"é"`, the length is either 2 (bytes) or 1 (characters), not both.

## 2. Empty string / empty array and null for `not_null`
- PRD, Terminology, "Null": "An empty string or an empty array counts as null for `not_null`."
- PRD, FP-07, `not_null`: "(an empty array or empty string is not null)".
- Why: `not_null('', 'x')` returns `'x'` under the first and `''` under the second.

## 3. `to_number` result type
- PRD, Terminology, "Number": "A number made from a string by `to_number` is always a floating-point value."
- PRD, FP-07, `to_number`: "a string that is an integer numeral becomes that integer".
- Why: `to_number('5')` is either a float or an int, not both.

## 4. Object wildcard on a non-object
- PRD, Terminology, "Projection": "An object wildcard applied to a non-object is the empty array."
- PRD, FP-04, Normal behavior: "An object wildcard on a value that is not an object yields null."
- Why: the result for a non-object is either `[]` or null.

## 5. Slice on a non-array
- PRD, FP-03, Normal behavior: "A slice on a value that is not an array yields null."
- PRD, FP-03, Boundary / error behavior: "A slice of a value that is not an array is the empty array."
- Why: the same input gives null in one place and `[]` in the other.

## 6. Filter on a non-array
- PRD, FP-04 (Normal and Boundary): "Its left-hand value must be an array; otherwise the result is null", and "A filter on a non-array yields null, not an empty array".
- PRD, FP-06, Normal behavior: "A filter applied to anything but an array yields the empty array."
- Why: the result is null in one place and `[]` in the other.

## 7. Zero slice step: empty array vs failure
- PRD, FP-03, Normal behavior: "A step of 0 selects nothing: the result is the empty array."
- PRD, FP-03, Boundary; FP-01 failure kinds; Interface Contract, Failure carriers: a slice with step 0 "does not succeed", is the zero-slice-step kind, and "not a successful empty array".
- Why: a step-0 slice either returns `[]` or raises.

## 8. Lone `=`: grammar-level vs token-level
- PRD, Terminology, "Grammar-level syntax failure": "A single `=` is a grammar-level failure of this kind."
- PRD, FP-06, Boundary: "A lone `=` is a token-level syntax failure".
- Why: the exception type differs by level (plain Syntax vs a strict subclass of it, per Interface Contract, Failure carriers), so it cannot be both.

## 9. Expression reference evaluated on its own
- PRD, Terminology, "Expression reference": "Outside a function argument it evaluates to null."
- PRD, FP-05: "Searching an expression reference on its own succeeds and yields a non-null value". Interface Contract, "Expression reference value": "returns a non-`None` value".
- Why: a bare `&expr` search returns null in one place and non-null in the others.

## 10. Multiselect list on a null current value
- PRD, FP-05, first list rule: "On a null current value it still builds one element per expression."
- PRD, FP-05, later rule: "A multiselect list or hash whose current value is null yields null."
- Why: for a null current value, `[a, b]` is either `[null, null]` or null.

## 11. Raw string escapes
- PRD, FP-05, Normal behavior: "No JSON escapes are processed."
- PRD, FP-05, Boundary: "A `\uXXXX` escape inside a raw string literal is decoded to its character."
- Why: `\uXXXX` in a raw string is either left as literal text or decoded.

## 12. `join` of an empty array
- PRD, FP-07, intro paragraph: "`join` of an empty array yields null."
- PRD, FP-07, `join`: "the empty array yields the empty string."
- Why: `join(',', [])` returns either null or `''`.
