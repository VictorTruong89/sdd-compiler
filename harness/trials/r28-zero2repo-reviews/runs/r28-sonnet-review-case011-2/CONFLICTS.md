# Specification conflicts

Files: PRD = spec/Full_PRD.md, IC = spec/Interface_Contract.md.

## 1. Slice of a non-array: null vs empty array
- PRD, FP-03 Normal behavior: "A slice on a value that is not an array yields null."
- PRD, FP-03 Boundary / error behavior: "A slice of a value that is not an array is the empty array."
- Why: the same slice applied to the same non-array value cannot be both null and the empty array.

## 2. Filter on a non-array: null vs empty array
- PRD, FP-04 Normal and Boundary: "Its left-hand value must be an array; otherwise the result is null" and "A filter on a non-array yields null, not an empty array".
- PRD, FP-06 Normal behavior: "A filter applied to anything but an array yields the empty array."
- Why: a filter on a non-array cannot yield both null and the empty array.

## 3. Object wildcard on a non-object: empty array vs null
- PRD, Terminology, "Projection": "An object wildcard applied to a non-object is the empty array."
- PRD, FP-04 Normal behavior: "An object wildcard on a value that is not an object yields null."
- Why: the result for the same input cannot be both the empty array and null.

## 4. Zero slice step: empty array vs failure
- PRD, FP-03 Normal behavior: "A step of 0 selects nothing: the result is the empty array."
- PRD, FP-03 Boundary / error behavior (also FP-01, IC "Failure carriers"): a slice with step 0 "does not succeed ... the zero-slice-step kind ... not a successful empty array".
- Why: a step-0 slice cannot both succeed with an empty array and be refused.

## 5. Lone `=`: grammar-level vs token-level syntax failure
- PRD, Terminology, "Grammar-level syntax failure": "A single `=` is a grammar-level failure of this kind."
- PRD, FP-06 Boundary: "A lone `=` is a token-level syntax failure".
- Why: each failure is exactly one of the two forms (plain syntax type vs its subclass, per IC "Failure carriers"), so a lone `=` cannot be both.

## 6. Length of a string: UTF-8 bytes vs Unicode characters
- PRD, Terminology, "String": "its length is its number of UTF-8 bytes."
- PRD, FP-07 `length`: "the number of Unicode characters (not bytes) of a string".
- Why: for any non-ASCII string the two counts differ.

## 7. Expression reference on its own: null vs non-null
- PRD, Terminology, "Expression reference": "Outside a function argument it evaluates to null."
- PRD, FP-05: searching an expression reference on its own "yields a non-null value". IC "Expression reference value": returns "a non-`None` value".
- Why: a bare expression reference cannot evaluate to both null and a non-null value.

## 8. Multiselect list/hash on a null current value
- PRD, FP-05 Normal, multiselect list: "On a null current value it still builds one element per expression." The hash entry stores null for null values and builds an object.
- PRD, FP-05 Normal, third bullet: "A multiselect list or hash whose current value is null yields null."
- Why: with a null current value the result cannot be both a constructed array or object and null.

## 9. Raw strings and `\uXXXX`
- PRD, FP-05 Normal: for a raw string "No JSON escapes are processed."
- PRD, FP-05 Boundary: "A `\uXXXX` escape inside a raw string literal is decoded to its character."
- Why: `\uXXXX` is a JSON escape, so it cannot be both left unprocessed and decoded.

## 10. Empty string / empty array and `not_null`
- PRD, Terminology, "Null": "An empty string or an empty array counts as null for `not_null`."
- PRD, FP-07 `not_null`: "(an empty array or empty string is not null)".
- Why: for `not_null`, an empty string or array cannot both count as null and not count as null.

## 11. `join` of an empty array: null vs empty string
- PRD, FP-07 intro: "`join` of an empty array yields null."
- PRD, FP-07 `join`: "the empty array yields the empty string."
- Why: the same call cannot return both null and the empty string.

## 12. `to_number` of an integer string: float vs integer
- PRD, Terminology, "Number": "A number made from a string by `to_number` is always a floating-point value."
- PRD, FP-07 `to_number`: "a string that is an integer numeral becomes that integer".
- Why: an integer numeral string cannot become both a float and an integer.
