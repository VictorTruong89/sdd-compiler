# NOTES: pathsel build

This file records how the specification in `spec/` was resolved. `spec/` itself is unchanged.
Each conflict from `spec/CONFLICTS.md` is listed with what each side says (file and line), and
what was built. Where the spec is silent, the assumption is listed in the second part.

Layout: `pathsel/` (flat package at the repo root, importable with the root on the path),
`pyproject.toml` (setuptools, zero runtime dependencies), `tests/test_pathsel.py` (behavioural
tests written from the spec; run `python3 -m pytest tests/`).

---

## Part 1: Conflicts and decisions

Line numbers refer to `spec/Full_PRD.md` unless another file is named.

### C-01: Bare expression reference (null vs non-null)
- Side A: Terminology row "Expression reference" (line 29): "Outside a function argument it evaluates to null."
- Side B: FP-05 (line 193): "Searching an expression reference on its own succeeds and yields a non-null value"; `Interface_Contract.md` "Expression reference value": "returns a non-`None` value."
- **Built:** non-null. A bare `&expr` returns an `ExpressionRef` object (`pathsel/values.py`). Side B appears in the normative feature point and the interface contract, so it was chosen over the glossary row.

### C-02: `not_null` and empty string / empty array
- Side A: Terminology row "Null" (line 23): "An empty string or an empty array counts as null for `not_null`."
- Side B: FP-07 `not_null` (line 252): "(an empty array or empty string is not null)."
- **Built:** only Python `None` is null for `not_null`. `not_null('', x)` returns `''`. The FP-07 definition of the function was taken as more specific than the glossary.

### C-03: Object wildcard on a non-object
- Side A: Terminology row "Projection" (line 32): "An object wildcard applied to a non-object is the empty array."
- Side B: FP-04 object-wildcard bullet (line 159): "yields null."
- **Built:** null. This matches the list wildcard rule (line 158) and the rest of FP-04.

### C-04: Filter on a non-array
- Side A: FP-04 (lines 161 and 175): "the result is null", "not an empty array".
- Side B: FP-06 (line 215): "A filter applied to anything but an array yields the empty array."
- **Built:** null. FP-04 states it twice and it is the feature point that defines filters.

### C-05: Slice on a non-array
- Side A: FP-03 normal behaviour (line 138): "A slice on a value that is not an array yields null."
- Side B: FP-03 boundary (line 148): "A slice of a value that is not an array is the empty array."
- **Built:** null. Index and flatten on non-arrays are also null.

### C-06: Slice with step 0
- Side A: FP-03 normal behaviour (line 133): "A step of 0 selects nothing: the result is the empty array."
- Side B: FP-03 boundary (line 146) and `Interface_Contract.md` "Failure carriers" (zero slice step kind): a refusal, a `ValueError` subclass that is not `SyntaxFailure`.
- **Built:** refusal, `ZeroSliceStepError`. The zero-slice-step kind exists in the interface contract, so it must be reachable. The check is made at compile time because it depends only on the text, so compile and one-shot search refuse identically (FP-01 line 87).

### C-07: Single `=`
- Side A: Terminology row "Grammar-level syntax failure" (line 37): "A single `=` is a grammar-level failure of this kind."
- Side B: FP-06 boundary (line 219): "A lone `=` is a token-level syntax failure."
- **Built:** token-level (`TokenSyntaxFailure`, a subclass of `SyntaxFailure`). A lone `=` begins no token in the lexer, and FP-06 is the specific rule.

### C-08: `join` of an empty array
- Side A: FP-07 `join` definition (line 242): "the empty array yields the empty string."
- Side B: FP-07 paragraph (line 230): "`join` of an empty array yields null."
- **Built:** `""`. Line 230 says a function returns "the result its definition states", and the definition at line 242 says the empty string.

### C-09: Type of a number made by `to_number`
- Side A: Terminology row "Number" (line 26): "always a floating-point value."
- Side B: FP-07 `to_number` (line 247): "a string that is an integer numeral becomes that integer."
- **Built:** integer numerals become `int` (`"5"` gives `5`); decimal and exponent numerals become `float` (`"1e3"` gives `1000.0`).

### C-10: Unit of string length
- Side A: Terminology row "String" (line 27): "its length is its number of UTF-8 bytes."
- Side B: FP-07 `length` (line 240): "the number of Unicode characters (not bytes) of a string."
- **Built:** Unicode characters (`len(str)`). The function definition explicitly contrasts with bytes.

### C-11: Multiselect list on a null current value
- Side A: FP-05 (line 187): "On a null current value it still builds one element per expression."
- Side B: FP-05 (line 188): "A multiselect list or hash whose current value is null yields null."
- **Built:** null, for both lists and hashes (`MultiList` / `MultiHash` in `pathsel/nodes.py`). Line 188 is the more general rule and covers hashes too.

### C-12: Arity of `length`
- Side A: FP-07 built-in list (line 240): `length(string, array or object)` written with two parameter slots.
- Side B: FP-07 meaning (line 240) and the arity rule (line 260): one value, "every other built-in takes exactly the number of arguments listed above."
- **Built:** one argument. The slashes in `array or object` are a type union (as for `contains(array or string, any)`), not a second parameter. `length('abc', x)` is invalid-arity.

### C-13: Whitespace inside the flatten operator
- Side A: FP-02 (line 110): whitespace "may appear between any two tokens and do not change meaning."
- Side B: FP-03 (line 140): flatten is "empty square brackets `[]`, written with nothing between them."
- **Built:** `[ ]` is flatten, because whitespace between tokens does not change meaning (the lexer skips whitespace, so `[` followed by `]` is flatten).

### C-14: Text ending after a dot
- Side A: FP-01 incomplete-expression rule (line 94): text ending where an operand must still begin is incomplete.
- Side B: FP-01 syntax rule (line 95) and FP-02 (line 118): a dot followed by "the end of the text" is a syntax failure.
- **Built:** incomplete (`IncompleteExpressionError`). An operand must begin after the dot, and the incomplete rule is the more specific statement about where text stops. Position is the end of the text.

---

## Part 2: Items the spec does not state (assumptions)

### Parsing and projections
- **Projection right-hand side rank.** FP-04 gives an object wildcard rank 2 or 4 depending on its position. I gave `.*` rank 40 when it is a step in an enclosing projection, and rank 20 (like `[*]`) for its own right-hand side. Otherwise `foo.*.a.b` would stop after `.a`.
- **Slice after an index or slice.** `a[0][1:2]` starts a projection (slices are always projections, per FP-03 line 139). This is one of the two placements the spec leaves to the implementer.
- **Dot then multiselect.** `a[*].[x, y][0]` lets later steps join the right-hand side (the same rank rule applies). The second implementer-choice placement in FP-04 line 170.
- **Function call after a dot.** `a.length(@)` and `people[*].name.length(@)` are allowed; the call's current value is the left-hand result. Needed for "a function call may be the right-hand side of a projection" (line 256). `"abs"(...)` (quoted) is a grammar-level syntax failure (line 262).
- **Multiselect after an operand.** `[a, b]` is accepted only at the start of an operand, or as the first step of a projection's right-hand side. `foo[a, b]` is a syntax failure (FP-05 line 188).
- **Bracket content.** `[` followed by `*`, `?`, a number, or `:` is a wildcard, filter, index or slice. Anything else inside brackets is a multiselect list if allowed, otherwise a syntax failure. Number-only elements such as `[0, 1]` are syntax failures because numbers are not operands (use backtick JSON literals, e.g. `` abs(`-1`) ``).
- **Literal as an operand.** A literal can start any operand (for example `` `1` | @ ``, `` abs(`-1`) `` or `` foo[?a == `1`] ``). After a dot it is a syntax failure (FP-05 line 198): `` foo.`x` ``.
- **Expression reference extent.** `&expr` extends as far as an operand expression allows: to the next `,`, `)`, `]`, `}`, or the end of the text. Pipes inside a reference are included.

### Lexing
- **Hyphen.** A `-` that does not begin a number (for example `a-b`) is a token-level failure at the hyphen.
- **Number tokens.** Only `-?[0-9]+` is a number token. `1.5` lexes as `1`, `.`, `5`.
- **Unknown characters.** Characters that begin no token, including `#`, `$`, `;` and non-ASCII letters, are token-level failures. `?` outside brackets is lexed as a token and gives a grammar-level failure.
- **Lazy failure.** The first token-level failure in text order wins over a later grammar error; the lexer stops at the first failure.
- **Quoted identifiers** decode with `json.loads`, so `NaN` and `Infinity` are rejected. Raw control characters are rejected.
- **Raw strings.** Only `\'` and `\uXXXX` are escapes (surrogate pairs are combined). Other backslashes are kept, so `'a\\'` is unterminated.
- **JSON literals.** `` `…` `` is parsed with `json.loads` (NaN and Infinity rejected). An escaped backtick `` \` `` is accepted inside a literal and means a backtick. If the text is not JSON, it is read as JSON string content after removing leading whitespace; trailing whitespace is kept. Empty text `` `` `` is the empty string. Literal containers are deep-copied on each evaluation.

### Refusal kinds and checks
- **Position for failures at end of text.** Position equals the text length (FP-01 line 97).
- **Failure ordering.** A call is checked as: name, then argument count, then each argument's evaluation, then each argument's type, then the function runs (FP-07 line 230). Element-type requirements (for example "array of numbers") are checked inside the function body, and still raise the invalid-type kind.
- **Non-string expression.** `search(123, ...)` or `compile(None)` raises `TypeError`. It is misuse, not one of the refusal kinds.
- **Custom signature type names.** In addition to the five names listed in the interface contract (`number`, `string`, `array`, `object`, `null`), `boolean`, `any` and `expression` are accepted. A boolean passed to a custom function declared only with the listed names is invalid-type.
- **Built-in names win.** A provider's `_func_<name>` for a built-in name is ignored, so built-ins keep their behaviour (FP-08 line 274). A provider only adds new names.

### Values and built-ins
- **Arrays and objects.** Arrays are `list` and `tuple` (not `str`). Objects are any `collections.abc.Mapping`, so `OrderedDict` and other mappings are accepted wherever an object is required.
- **Numbers.** `int`, `float` and `decimal.Decimal` are numbers; `bool` is not. Mixed `Decimal` and `float` arithmetic in `sum` and `avg` converts the decimals to float.
- **Ordering comparators** (`<`, `<=`, `>`, `>=`) return null for anything other than two numbers or two strings. The spec does not say; null matches the "does not fail" rule.
- **`type()`** returns `"null"` for host values outside the six JSON types and for expression references.
- **`to_string`** writes compact JSON with `ensure_ascii`. Mappings and tuples are normalised first; `Decimal` is written as a JSON number (via `float`).
- **`to_number`** accepts an optional leading `+` or `-`, digits with an optional fraction and exponent, and no surrounding whitespace. Non-numeric strings give null. Booleans give null.
- **`contains` on a string** with a non-string second argument is invalid-type.
- **`max`, `min`, `sort`, `sort_by`, `max_by`, `min_by`** on an empty array: `max`, `min`, `max_by`, `min_by` return null; `sort` and `sort_by` return `[]`. Mixed or non-string/number keys are invalid-type. `max_by` and `min_by` return the first element on ties; `sort_by` is stable.
- **`merge`** returns a plain `dict`. It does not use `dict_cls` (the built-in does not receive the options context).
- **`avg`** returns a float (`sum / len`).
- **`ceil` and `floor`** on infinity or NaN raise the Python exception (`OverflowError` / `ValueError`); the spec does not say what should happen.
- **`keys`, `values`** return lists in the mapping's iteration order.
- **Duplicate keys in a multiselect hash.** The last one wins.

### Evaluation options and the package
- **Options object.** Any object with `dict_cls` and `custom_functions` attributes works (missing attributes are treated as `None`). `pathsel.Options` is a small convenience class.
- **Custom function results** are returned as they are, including `0`, `[]` and `{}` (FP-08 line 273).
- **Expression references in custom functions.** Custom signatures have no type for references, so custom functions cannot take them. The built-in `map`, `sort_by`, `max_by` and `min_by` take them.
- **Packaging.** `pyproject.toml` declares a setuptools build with the flat `pathsel` package and no runtime dependencies. Nothing needs to be installed to import from the repo root.
- **Document is not mutated.** Results can share sub-objects with the document; callers should not expect copies.
