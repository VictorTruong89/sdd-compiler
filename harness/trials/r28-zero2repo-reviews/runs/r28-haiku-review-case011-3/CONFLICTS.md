# Specification conflicts

Each entry quotes both sides of a disagreement inside `spec/`, with file and section, followed by one sentence on why both cannot hold. Line numbers refer to the files as they currently are.

### 1. Result type of `to_number` on a numeral string

- **Side A:** `spec/Full_PRD.md`, Terminology, "Number" (line 26): "A number made from a string by `to_number` is always a floating-point value."
- **Side B:** `spec/Full_PRD.md`, FP-07, `to_number(any)` (line 247): "a string that is an integer numeral becomes that integer".
- **Why:** A string such as `"5"` passed to `to_number` cannot both become a floating-point value (A) and become an integer (B).

### 2. Length of a string

- **Side A:** `spec/Full_PRD.md`, Terminology, "String" (line 27): "its length is its number of UTF-8 bytes."
- **Side B:** `spec/Full_PRD.md`, FP-07, `length(string, array or object)` (line 240): "the number of Unicode characters (not bytes) of a string".
- **Why:** A non-ASCII string such as `"é"` has two UTF-8 bytes but one Unicode character, so the length cannot be both values.

### 3. Object wildcard on a non-object

- **Side A:** `spec/Full_PRD.md`, Terminology, "Projection" (line 32): "An object wildcard applied to a non-object is the empty array."
- **Side B:** `spec/Full_PRD.md`, FP-04, object wildcard (line 159): "An object wildcard on a value that is not an object yields null."
- **Why:** The same expression applied to a non-object cannot yield both an empty array and null.

### 4. `not_null` and empty string or empty array

- **Side A:** `spec/Full_PRD.md`, Terminology, "Null" (line 23): "An empty string or an empty array counts as null for `not_null`."
- **Side B:** `spec/Full_PRD.md`, FP-07, `not_null(any, any, …)` (line 252): "(an empty array or empty string is not null)".
- **Why:** `not_null("")` or `not_null([])` either counts as null (returning the next argument) or is not null (returning the empty value), and cannot be both.

### 5. Expression reference searched on its own

- **Side A:** `spec/Full_PRD.md`, Terminology, "Expression reference" (line 29): "Outside a function argument it evaluates to null."
- **Side B:** `spec/Full_PRD.md`, FP-05, expression reference (line 193): "Searching an expression reference on its own succeeds and yields a non-null value"; and `spec/Interface_Contract.md`, "Expression reference value" (line 113): "returns a non-`None` value of the implementer's choice."
- **Why:** A bare expression reference searched on its own must be either null (A) or non-null (B), not both.

### 6. Filter applied to a non-array

- **Side A:** `spec/Full_PRD.md`, FP-06, Normal behavior (line 215): "A filter applied to anything but an array yields the empty array."
- **Side B:** `spec/Full_PRD.md`, FP-04, filter (line 161): "Its left-hand value must be an array; otherwise the result is null."; and FP-04, Boundary (line 175): "A filter on a non-array yields null, not an empty array".
- **Why:** A filter on a non-array produces either the empty array (A) or null, and FP-04 explicitly rules out the empty array.

### 7. Slice applied to a non-array

- **Side A:** `spec/Full_PRD.md`, FP-03, Normal behavior (line 138): "A slice on a value that is not an array yields null."
- **Side B:** `spec/Full_PRD.md`, FP-03, Boundary (line 148): "A slice of a value that is not an array is the empty array."
- **Why:** The same slice on a non-array value cannot be both null and the empty array.

### 8. Slice with step 0

- **Side A:** `spec/Full_PRD.md`, FP-03, Normal behavior (line 133): "A step of 0 selects nothing: the result is the empty array."
- **Side B:** `spec/Full_PRD.md`, FP-03, Boundary (line 146): "A slice whose step is 0 does not succeed on either entry … That failure is the zero-slice-step kind"; also Terminology (line 35) and `spec/Interface_Contract.md` (line 106) treat it as a refusal.
- **Why:** A step-0 slice either succeeds with an empty array (A) or refuses with the zero-slice-step failure (B), not both.

### 9. `join` of an empty array

- **Side A:** `spec/Full_PRD.md`, FP-07, Normal behavior intro (line 230): "`join` of an empty array yields null."
- **Side B:** `spec/Full_PRD.md`, FP-07, `join(string, array of strings)` (line 242): "the empty array yields the empty string."
- **Why:** `join` of an empty array must return either null or the empty string, and cannot return both.

### 10. Multiselect list on a null current value

- **Side A:** `spec/Full_PRD.md`, FP-05, Normal behavior (line 187): "On a null current value it still builds one element per expression."
- **Side B:** `spec/Full_PRD.md`, FP-05, Normal behavior (line 188): "A multiselect list or hash whose current value is null yields null."
- **Why:** On a null current value a multiselect list must either build an array with one element per expression or yield null, not both.

### 11. Escapes in raw string literals

- **Side A:** `spec/Full_PRD.md`, FP-05, raw string literal (line 192): "No JSON escapes are processed."
- **Side B:** `spec/Full_PRD.md`, FP-05, Boundary (line 198): "A `\uXXXX` escape inside a raw string literal is decoded to its character."
- **Why:** A `\uXXXX` sequence inside a raw string is either left as literal backslash text (A) or decoded to a character (B).

### 12. Classification of a lone `=`

- **Side A:** `spec/Full_PRD.md`, Terminology, "Grammar-level syntax failure" (line 37): "A single `=` is a grammar-level failure of this kind."
- **Side B:** `spec/Full_PRD.md`, FP-06, Boundary (line 219): "A lone `=` is a token-level syntax failure".
- **Why:** A lone `=` is classified as either a grammar-level failure or a token-level failure, and the two are defined as distinct kinds.

### 13. Expression ending in a dot

- **Side A:** `spec/Full_PRD.md`, FP-01, Boundary (line 94): text that ends "at a place where an operand expression must still begin" is the incomplete-expression kind.
- **Side B:** `spec/Full_PRD.md`, FP-01, Boundary (line 95): a dot followed by "the end of the text" is a syntax failure; and FP-02, Boundary (line 118): "A dot at the start, at the end, or doubled is a grammar-level syntax failure."
- **Why:** For a trailing dot such as `a.`, the text ends where an operand must begin, so it cannot be both the incomplete-expression kind (A) and the syntax kind (B).
