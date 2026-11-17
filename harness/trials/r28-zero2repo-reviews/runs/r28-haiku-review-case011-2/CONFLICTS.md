# Specification conflicts

Files: `spec/Full_PRD.md` (PRD), `spec/Interface_Contract.md` (Contract), `spec/Hardware_Requirements.md` (Hardware). Line numbers refer to `Full_PRD.md`.

## 1. Slice of a non-array: null or empty array

- **Side A:** PRD, FP-03, Normal behavior (line 138): "A slice on a value that is not an array yields null."
- **Side B:** PRD, FP-03, Normal behavior (line 148): "A slice of a value that is not an array is the empty array."
- **Why they cannot both hold:** the same slice on the same non-array value must return either null or the empty array, not both.

## 2. Filter on a non-array: null or empty array

- **Side A:** PRD, FP-04, Normal behavior (line 161): "Its left-hand value must be an array; otherwise the result is null." Also FP-04, Boundary (line 175): "A filter on a non-array yields null, not an empty array and not a failure."
- **Side B:** PRD, FP-06, Normal behavior (line 215): "A filter applied to anything but an array yields the empty array."
- **Why they cannot both hold:** a filter applied to a non-array value is required to produce either null or the empty array, and the two sections name different results.

## 3. Slice with step 0: empty array or refusal

- **Side A:** PRD, FP-03, Normal behavior (line 133): "A step of 0 selects nothing: the result is the empty array."
- **Side B:** PRD, FP-03, Boundary (line 146): "A slice whose step is 0 does not succeed on either entry ... That failure is the zero-slice-step kind: a kind of value error, not a successful empty array."
- **Why they cannot both hold:** a step-0 slice either succeeds with the empty array or fails with the zero-slice-step kind, and the spec says both.

## 4. Object wildcard on a non-object: null or empty array

- **Side A:** PRD, Terminology, row "Projection" (line 32): "An object wildcard applied to a non-object is the empty array."
- **Side B:** PRD, FP-04, Normal behavior (line 159): "An object wildcard on a value that is not an object yields null."
- **Why they cannot both hold:** the same object wildcard on a non-object value cannot yield both the empty array and null.

## 5. Dot at the end of the text: incomplete or syntax

- **Side A:** PRD, FP-01, Boundary (line 94): text that ends "at a place where an operand expression must still begin ... is the incomplete-expression kind." A trailing dot leaves an operand required at the end of the text.
- **Side B:** PRD, FP-01, Boundary (line 95): a dot "whatever follows it, including ... the end of the text" is "the syntax kind." Also FP-02, Boundary (line 118): "A dot at the start, at the end, or doubled is a grammar-level syntax failure."
- **Why they cannot both hold:** a trailing dot is one failing input, and the spec assigns it both the incomplete-expression kind and the syntax kind, which are distinct kinds.

## 6. A lone `=`: grammar-level or token-level syntax failure

- **Side A:** PRD, Terminology, row "Grammar-level syntax failure" (line 37): "A single `=` is a grammar-level failure of this kind."
- **Side B:** PRD, FP-06, Boundary (line 219): "A lone `=` is a token-level syntax failure."
- **Why they cannot both hold:** the Contract requires the two syntax forms to raise different types (grammar-level `<Syntax>`, token-level a subclass of `<Syntax>`), so a lone `=` cannot be both.

## 7. Multiselect list on a null current value: one null per element or null

- **Side A:** PRD, FP-05, Normal behavior (line 187): "On a null current value it still builds one element per expression."
- **Side B:** PRD, FP-05, Normal behavior (line 188): "A multiselect list or hash whose current value is null yields null."
- **Why they cannot both hold:** a multiselect list on a null current value is either an array of nulls, one per expression, or the single null, and the spec says both.

## 8. Escapes in raw string literals

- **Side A:** PRD, FP-05, Normal behavior (line 192): "A raw string literal ... No JSON escapes are processed."
- **Side B:** PRD, FP-05, Boundary (line 198): "A `\uXXXX` escape inside a raw string literal is decoded to its character."
- **Why they cannot both hold:** `\uXXXX` inside a raw string is either left as six literal characters (no escapes processed) or decoded to one character, and the spec requires both.

## 9. Bare expression reference: null or non-null

- **Side A:** PRD, Terminology, row "Expression reference" (line 29): "Outside a function argument it evaluates to null."
- **Side B:** PRD, FP-05, Normal behavior (line 193): "Searching an expression reference on its own succeeds and yields a non-null value." The Contract, section "Expression reference value," says the same: "returns a non-`None` value."
- **Why they cannot both hold:** searching a bare expression reference (outside any function argument) must yield either null or a non-null value.

## 10. `join` of an empty array

- **Side A:** PRD, FP-07, Normal behavior / preamble (line 230): "`join` of an empty array yields null."
- **Side B:** PRD, FP-07, Normal behavior (line 242): "`join(string, array of strings)` — ... the empty array yields the empty string."
- **Why they cannot both hold:** `join` of the empty array is either null or the empty string, and the spec names both.

## 11. `to_number` of an integer numeral: integer or float

- **Side A:** PRD, Terminology, row "Number" (line 26): "A number made from a string by `to_number` is always a floating-point value."
- **Side B:** PRD, FP-07, Normal behavior (line 247): "a string that is an integer numeral becomes that integer."
- **Why they cannot both hold:** a string such as `"5"` converted by `to_number` is either a float or an integer, and the spec says both.

## 12. Empty string and empty array under `not_null`

- **Side A:** PRD, Terminology, row "Null" (line 23): "An empty string or an empty array counts as null for `not_null`."
- **Side B:** PRD, FP-07, Normal behavior (line 252): "`not_null(any, any, …)` ... (an empty array or empty string is not null)."
- **Why they cannot both hold:** `not_null` of an empty string or array is either the null result (counted as null) or the value itself (not null), and the spec states both.

## 13. String length: bytes or characters

- **Side A:** PRD, Terminology, row "String" (line 27): "its length is its number of UTF-8 bytes."
- **Side B:** PRD, FP-07, Normal behavior (line 240): "`length(string, …)` — the number of Unicode characters (not bytes) of a string."
- **Why they cannot both hold:** for a non-ASCII string, the UTF-8 byte count and the Unicode character count differ, so `length` cannot return both.

## 14. Dependency order: FP-01 depends on a later feature point

- **Side A:** PRD, Product overview (line 11): "a later feature point may depend on an earlier one, never the reverse."
- **Side B:** PRD, FP-01, Public entry (line 81): "The search entry also supplies a document and may supply evaluation options (FP-08)."
- **Why they cannot both hold:** FP-01 (earlier) depends on FP-08 (later) for evaluation options, which is the reverse of the stated ordering rule.

## 15. Dependency order: FP-04 depends on a later feature point

- **Side A:** PRD, Product overview (line 11): "a later feature point may depend on an earlier one, never the reverse."
- **Side B:** PRD, FP-04, Public entry (line 154): "Filter predicates use the comparators and truthiness of FP-06."
- **Why they cannot both hold:** FP-04 (earlier) relies on the comparators and truthiness defined in FP-06 (later), which is the reverse of the stated ordering rule.
