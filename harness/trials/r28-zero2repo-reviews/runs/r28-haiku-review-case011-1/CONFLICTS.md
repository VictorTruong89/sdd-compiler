# Specification conflicts

Each entry quotes or states both sides with their location, then gives one sentence on why both cannot hold. Locations use `Full_PRD.md` section and line numbers, or `Interface_Contract.md` section names.

## C-01: Bare expression reference evaluates to null vs. non-null

- **Side A:** `Full_PRD.md`, Terminology table, row "Expression reference" (line 29): "Outside a function argument it evaluates to null."
- **Side B:** `Full_PRD.md`, FP-05, expression reference bullet (line 193): "Searching an expression reference on its own succeeds and yields a non-null value." `Interface_Contract.md`, "Expression reference value" section: "Searching an expression that is a bare expression reference returns a non-`None` value."
- **Why:** A bare expression reference searched on its own cannot both yield null and yield a non-null value.

## C-02: `not_null` and empty string / empty array

- **Side A:** `Full_PRD.md`, Terminology table, row "Null" (line 23): "An empty string or an empty array counts as null for `not_null`."
- **Side B:** `Full_PRD.md`, FP-07, `not_null` (line 252): "(an empty array or empty string is not null)."
- **Why:** An empty string or empty array cannot both be null and be not null for the same `not_null` call.

## C-03: Object wildcard on a non-object

- **Side A:** `Full_PRD.md`, Terminology table, row "Projection" (line 32): "An object wildcard applied to a non-object is the empty array."
- **Side B:** `Full_PRD.md`, FP-04, object wildcard bullet (line 159): "An object wildcard on a value that is not an object yields null."
- **Why:** The same non-object input cannot produce both the empty array and null.

## C-04: Filter on a non-array

- **Side A:** `Full_PRD.md`, FP-04 (line 161 and line 175): "Its left-hand value must be an array; otherwise the result is null." and "A filter on a non-array yields null, not an empty array and not a failure."
- **Side B:** `Full_PRD.md`, FP-06, last normal-behavior bullet (line 215): "A filter applied to anything but an array yields the empty array."
- **Why:** A filter on a non-array cannot yield both null and the empty array.

## C-05: Slice on a non-array

- **Side A:** `Full_PRD.md`, FP-03, normal behavior (line 138): "A slice on a value that is not an array yields null."
- **Side B:** `Full_PRD.md`, FP-03, boundary behavior (line 148): "A slice of a value that is not an array is the empty array."
- **Why:** Both statements are about the same slice of a non-array, and they give null and the empty array respectively.

## C-06: Slice with step 0

- **Side A:** `Full_PRD.md`, FP-03, normal behavior (line 133): "A step of 0 selects nothing: the result is the empty array."
- **Side B:** `Full_PRD.md`, FP-03, boundary behavior (line 146): "A slice whose step is 0 does not succeed on either entry ... That failure is the zero-slice-step kind." `Interface_Contract.md`, Failure carriers, zero slice step: every such refusal raises a `ValueError` subclass.
- **Why:** A zero-step slice cannot both return the empty array as a success and be refused with an error.

## C-07: Single `=` is grammar-level or token-level

- **Side A:** `Full_PRD.md`, Terminology table, row "Grammar-level syntax failure" (line 37): "A single `=` is a grammar-level failure of this kind."
- **Side B:** `Full_PRD.md`, FP-06, boundary behavior (line 219): "A lone `=` is a token-level syntax failure; equality is the two-character token `==`."
- **Why:** A failure cannot be classified as both grammar-level and token-level, and the Interface Contract's distinct carriers for these kinds make the two classifications observably different.

## C-08: `join` of an empty array

- **Side A:** `Full_PRD.md`, FP-07, `join` definition (line 242): "the empty array yields the empty string."
- **Side B:** `Full_PRD.md`, FP-07, paragraph before the function list (line 230): "`join` of an empty array yields null."
- **Why:** The same call on an empty array cannot return both the empty string and null.

## C-09: Type of a number produced by `to_number`

- **Side A:** `Full_PRD.md`, Terminology table, row "Number" (line 26): "A number made from a string by `to_number` is always a floating-point value."
- **Side B:** `Full_PRD.md`, FP-07, `to_number` (line 247): "a string that is an integer numeral becomes that integer."
- **Why:** A string such as `"5"` converted by `to_number` cannot be both a floating-point value and an integer.

## C-10: Unit of string length

- **Side A:** `Full_PRD.md`, Terminology table, row "String" (line 27): "its length is its number of UTF-8 bytes."
- **Side B:** `Full_PRD.md`, FP-07, `length` (line 240): "the number of Unicode characters (not bytes) of a string."
- **Why:** A non-ASCII string has a different UTF-8 byte count and character count, so both cannot be its length.

## C-11: Multiselect list on a null current value

- **Side A:** `Full_PRD.md`, FP-05, normal behavior (line 187): "On a null current value it still builds one element per expression."
- **Side B:** `Full_PRD.md`, FP-05, normal behavior (line 188): "A multiselect list or hash whose current value is null yields null."
- **Why:** The same multiselect list on a null current value cannot both build an array of nulls and yield null.

## C-12: Arity of `length` (one parameter or two)

- **Side A:** `Full_PRD.md`, FP-07, built-in list (line 240): `length(string, array or object)` is written with two comma-separated parameter slots, following the notation used for `contains(array or string, any)` and `join(string, array of strings)`.
- **Side B:** `Full_PRD.md`, FP-07, line 240 meaning: `length` takes one value, "the number of Unicode characters ... of a string, elements of an array, or keys of an object." Line 260: "every other built-in takes exactly the number of arguments listed above."
- **Why:** Under the listed notation `length("abc")` has one argument where two are required, so it would be invalid-arity by line 260 yet valid by the meaning on line 240.

## C-13: Whitespace inside the flatten operator

- **Side A:** `Full_PRD.md`, FP-02, normal behavior (line 110): "Spaces, tabs, line feeds, and carriage returns may appear between any two tokens and do not change meaning."
- **Side B:** `Full_PRD.md`, FP-03, normal behavior (line 140): "The flatten operator is empty square brackets `[]`, written with nothing between them."
- **Why:** If whitespace between `[` and `]` does not change meaning, `[ ]` must be flatten, but line 140 defines flatten as the form with nothing between the brackets, which excludes `[ ]`.

## C-14: Text ending after a dot

- **Side A:** `Full_PRD.md`, FP-01, boundary behavior, incomplete expression (line 94): text that ends "at a place where an operand expression must still begin" is the incomplete-expression kind.
- **Side B:** `Full_PRD.md`, FP-01, boundary behavior, syntax (line 95), and FP-02 (line 118): a dot "whatever follows it, including ... the end of the text" or "a dot at the end" is a grammar-level syntax failure.
- **Why:** A trailing dot such as `foo.` must be either incomplete (because an operand must still begin after it) or syntax (as the spec explicitly says), and the spec gives no rule that picks one.
