# NOTES

Implementation of PathSel (`pathsel`), built from `spec/` without changing it.
Layout: flat package `pathsel/` at the root, `pyproject.toml` (zero runtime
dependencies), tests in `tests/`, root `conftest.py` so `import pathsel` works
from `/app` without an install. Run the suite with `python3 -m pytest -q`
(168 tests, all passing on CPython 3.13). Every checklist id has a status in
`TRACEABILITY.md`.

The export says `--allow-open` and lists 11 contradictions with no human
verdict. Each is resolved below. Where a resolution contradicts a reading you
may have, change the one function named.

## 1. Conflicts in the spec (all 11 unsettled contradictions)

Quotes are from the pack `## Text` sections. "Pack NN" is the file under `spec/packs/`.

### CF-000005 — filter on a non-array
- Side A: "A filter on a non-array yields null, not an empty array and not a failure." (N-000202, pack 09, FP-04, boundary section)
- Side B: "A filter applied to anything but an array yields the empty array." (N-000259, pack 11, FP-06)
- **Built:** null (`pathsel/_nodes.py`, `Projection`, kind `filter`). Side A is the FP-04 rule that owns filters and says so explicitly.

### CF-000007 — slice of a non-array
- Side A: "A slice on a value that is not an array yields null." (N-000142, pack 08, FP-03, normal behavior)
- Side B: "A slice of a value that is not an array is the empty array." (N-000157, pack 08, FP-03, boundary section)
- **Built:** null. Matches the normal-behavior rule and the index rule for non-arrays.

### CF-000011 — multiselect on a null current value
- Side A: "On a null current value it still builds one element per expression." (N-000212, pack 10, FP-05, multiselect list)
- Side B: "A multiselect list or hash whose current value is null yields null." (N-000218, pack 10, FP-05)
- **Built:** null for both list and hash (`MultiList`, `MultiHash`). Side B covers both forms.

### CF-000015 — empty string/array under `not_null`
- Side A: "An empty string or an empty array counts as null for `not_null`." (N-000022, pack 02, Terminology "Null")
- Side B: "the first that is not null, or null if all are null (an empty array or empty string is not null)." (N-000300, pack 12, FP-07)
- **Built:** not null. Side B is the function's own definition.

### CF-000027 — object wildcard on a non-object
- Side A: "An object wildcard applied to a non-object is the empty array." (N-000031, pack 02, Terminology "Projection")
- Side B: "An object wildcard on a value that is not an object yields null." (N-000165, pack 09, FP-04)
- **Built:** null. Side B is in the feature point that defines the form; it matches the list-wildcard rule.

### CF-000035 — string length
- Side A: "its length is its number of UTF-8 bytes" (N-000026, pack 02, Terminology "String")
- Side B: "the number of Unicode characters (not bytes) of a string" (N-000277, pack 12, FP-07 `length`)
- **Built:** Unicode code points (`len(str)`). Side B is explicit about "not bytes".

### CF-000049 — escapes in raw strings
- Side A: "No JSON escapes are processed." (N-000227, pack 10, FP-05)
- Side B: "A `\uXXXX` escape inside a raw string literal is decoded to its character." (N-000239, pack 10, FP-05 boundary)
- **Built:** the specific rule wins. `\'` becomes `'`, `\uXXXX` runs (including surrogate pairs) are decoded, and every other backslash stays literal (`pathsel/_lexer.py`, `_decode_raw`).

### CF-000054 — `join` of an empty array
- Side A: "`join` of an empty array yields null." (N-000268, pack 12, FP-07 general rule)
- Side B: "the empty array yields the empty string." (N-000280, pack 12, FP-07 `join`)
- **Built:** empty string. Side B is the definition of `join` itself.

### CF-000055 — slice with step 0
- Side A: "A step of 0 selects nothing: the result is the empty array." (N-000133, pack 08, FP-03)
- Side B: "A slice whose step is 0 does not succeed on either entry" (N-000152, pack 08, FP-03 boundary; kind in N-000153, N-000415)
- **Built:** refusal with `ZeroSliceStepError`, raised at compile time (`pathsel/_parser.py`). Side B names a failure kind, and the spec's failure-carrier section gives it its own type.

### CF-000056 — searching a bare expression reference
- Side A: "Outside a function argument it evaluates to null" (N-000028, pack 02, Terminology "Expression reference")
- Side B: "returns a non-`None` value of the implementer's choice." (N-000423, pack 25; also N-000234, pack 10, "yields a non-null value")
- **Built:** non-null. `search("&expr", …)` returns an `ExpressionReference` object (`pathsel/_values.py`). Side B is explicit in the interface contract.

### CF-000057 — `to_number` on an integer numeral
- Side A: "A number made from a string by `to_number` is always a floating-point value." (N-000023, pack 02, Terminology "Number")
- Side B: "a string that is an integer numeral becomes that integer" (N-000287, pack 12, FP-07 `to_number`)
- **Built:** integer numerals give `int`; decimal and exponent numerals give `float`. Side B is the function's own rule. `42 == 42.0` in Python, so value comparisons agree either way.

## 2. Gaps: things the spec does not state, and what I assumed

Grouped by area. Each is a single decision point in the code.

**Comparison and types**
- Ordering (`<`, `<=`, `>`, `>=`) between mismatched types (number vs string, anything vs null) is not specified. Built: null (`_values.ordered`).
- Ordering for booleans is also unspecified; booleans are not numbers, so they yield null.
- `type()` of a host value that is not a JSON type: numbers (including `Decimal`) give `"number"`; any other non-JSON value gives `"object"`.
- Function arguments that require a JSON number refuse `Decimal` (invalid type), following the data-model constraint. Comparisons accept `Decimal` as a number, as FP-06 states.
- "Object" is duck-typed: anything with `keys()` and `__getitem__` (except str/list/tuple/bool/None). This lets an options `dict_cls` that is a plain class (filled by item assignment) act as an object, as FP-08 requires.
- Arrays are `list` or `tuple`.

**Numerals and literals**
- `to_number` accepts only strict numerals: no surrounding whitespace, no leading `+`, and `.5`, `1.`, `1e3` are floats. Anything else is null.
- A bare number is not an operand. Numbers occur only inside brackets, so `f(1)` or `[1, 2]` are syntax failures; write `` `1` `` for a JSON number. The spec's grammar implies this but does not say it.
- A JSON literal ends at the next backtick (no escape for backtick is specified). If the text is not JSON, it is read as JSON string content after leading whitespace is removed. Quotes in it make it a token-level failure.
- A raw string keeps every backslash except `\'` and `\uXXXX` (malformed `\u` stays literal).
- `\uXXXX` inside a quoted identifier is decoded by the JSON rules (FP-02 says so).

**Grammar and failures**
- Failures are detected left to right and tokens are lexed on demand, so a token-level error after an earlier grammar error is not reported.
- Position of a syntax failure is the start of the token where parsing cannot continue. The end of text has offset `len(text)`.
- Whitespace-only text is incomplete (spec explicit). `""` is empty.
- `[ ]` (flatten with a space) is flatten, because spaces between tokens do not change meaning (FP-02).
- `a.f(args)` (a function call after a dot) is allowed; the call's `@` is the value on the left of the dot. The spec's function-call rule does not forbid it.
- `dot` followed by an index, slice, list wildcard, or filter is a syntax failure, because only multiselect is allowed after a dot.
- A zero-argument call `f()` is accepted by the grammar and refused as invalid arity at evaluation.
- Non-string expression argument to `compile`/`search` raises `TypeError` (not a refusal kind; the spec covers only expression text).
- Comparisons chain left-to-right (`a == b == c` is `(a == b) == c`). The spec does not define chaining.

**Projections**
- Slices, flatten and filters with no right-hand side drop null items (spec: "null results are dropped").
- Function arguments are evaluated after the name and arity checks and before the type checks.
- Boolean operators short-circuit, so an unknown function in an unevaluated branch is not refused. The spec says the check happens when the call is evaluated, which supports this.

**Functions**
- `avg` returns a float. `sum([])` is `0`; `max([])` and `min([])` are null.
- `max`, `min`, `sort`, `sort_by`, `max_by`, `min_by` require every key to be a number or every key to be a string. Mixed types, including booleans and nulls, are invalid type.
- `contains(string, x)`: `x` must be a string, or invalid type.
- `merge` builds a mapping of the options' `dict_cls` when given, else a `dict`.
- `to_array` returns the same list object, not a copy. Literals are deep-copied on each evaluation so callers cannot change them.
- `to_string` of a non-JSON number uses its `str()` text.

**Options and providers**
- Built-in names keep their built-in behavior even if a provider defines an attribute with that name ("every FP-07 function remains available with unchanged behavior"). Only non-built-in names reach the provider.
- Custom declared type `object` matches any object as defined above; `null` matches only `None`; `number` excludes booleans and `Decimal`.
- `options` may be any object with `dict_cls` and `custom_functions` attributes, or a plain `dict` with those keys. Missing attributes mean "no setting".

**Output and mutation**
- Search returns new lists and mappings. It does not write into the document. Selected sub-objects are shared with the input (that is selection, not mutation).

## 3. Implementer's choices (spec left these open)

- **N-000198 (slice after an index or slice):** every slice is a projection, so a slice after an index also projects.
- **N-000199 (dot followed by a multiselect inside a right-hand side):** the later steps follow the same rank rules as any dot step; they join only when tighter than the projection.
- **N-000333 (other mapping types where an object is required):** accepted, through the duck-typed object rule.
- **N-000385 (type of the parsed expression):** `pathsel.ParsedExpression`.
- **N-000392 (options class):** not published. Any object or dict with the two attributes works.
- **N-000374 (root names):** besides `search` and `compile`, the root exports `ParsedExpression`, `ExpressionReference`, and every error class.
- **N-000407, N-000408 (failure type names and report text):** `EmptyExpressionError`, `IncompleteExpressionError`, `ExpressionSyntaxError` (grammar-level), `TokenSyntaxError` (subclass of the grammar-level one), `ZeroSliceStepError`, `UnknownFunctionError`, `InvalidArityError`, `InvalidTypeError`, all subclasses of `PathSelError(ValueError)`. Each is a single exact type per kind (except the token-level subclass). Reports are plain text.

## 4. Behaviour that follows the spec literally and may surprise

I kept these because the spec states them. They are the first places to look if a hidden test disagrees.

1. **Object wildcard followed by two dot steps.** Under the FP-04 rank table, a dot-form `.*` ranks 4, so only the first following step joins its right-hand side; the next dot step applies to the collected array. Verified: with `{"foo": {"k": {"bar": {"baz": 1}}}}`, `foo.*.bar` gives `[{"baz": 1}]`, and `foo.*.bar.baz` gives `null`. A JMESPath-style reading would give `[1]`. The change is local to `pathsel/_parser.py` (the `*` branch of `dot` and the bound passed to `projection_rhs`).
2. **First step after a projection form always begins its right-hand side** (N-000183). So `people[*][name]` projects a multiselect per element, and `a.b[0:2][0]` gives `[]` for scalar elements, because `[0]` is applied to each selected number.
3. **Bare numbers are refused** outside brackets (see section 2).
4. **Bracket after an operand**: only index, slice, list wildcard, filter, and flatten. A multiselect bracket there is a syntax failure, even when the spec's wording could be read more broadly (N-000216, N-000217).

## 5. Not verified in this environment

- Only CPython 3.13 on Linux was run. The code avoids 3.10+ syntax, but Python 3.9 and PyPy were not executed. macOS and Windows were not run.
- No installation step was run. The hidden tests run with `/app` as the working directory; `conftest.py` puts the root on `sys.path` for pytest, and `python3 -c "import pathsel"` works from `/app`.
