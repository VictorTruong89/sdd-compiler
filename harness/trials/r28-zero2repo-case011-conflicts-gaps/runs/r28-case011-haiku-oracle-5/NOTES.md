# pathsel — implementation notes

Built from `spec/` (compiled export, `spec/MAP.md`, `spec/CHECKLIST.md`). `spec/` is unchanged.

## Layout

- `pathsel/` — the importable package (flat layout at the repository root).
  - `__init__.py` — `search(expression, data, options=None)`, `compile(expression)`, exports.
  - `lexer.py` — lazy tokenizer; token-level failures are raised only when the parser reaches them.
  - `parser.py` — Pratt parser; binding powers match the spec's step ranking (flatten 9, `*`/slice 20, filter 21, dot 40, bracket 55).
  - `nodes.py` — expression tree and evaluation, projections, comparisons, logic, multiselects.
  - `builtins.py` — the 26 FP-07 built-in functions.
  - `calls.py` — call dispatch: name check, then argument count, then argument types.
  - `functions.py` — public provider API: `Functions`, `signature`.
  - `context.py` — reads `dict_cls` and `custom_functions` from the options object.
  - `values.py` — truthiness, JSON equality, number/type predicates, `ExpressionReference`.
  - `errors.py` — failure kinds (all subclasses of `ValueError`).
- `pyproject.toml` — setuptools metadata; zero runtime dependencies.
- `conftest.py` — empty root conftest; it puts `/app` on `sys.path` so plain `pytest` can import `pathsel`.
- `tests/` — `test_pathsel.py` and `test_spec_remaining.py`; each test cites its spec ids.

Run: `python3 -m pytest -q tests/` (166 tests, all passing on Python 3.13).

## Coverage of the checklist

All 423 ids are cited by a `# spec: N-…` marker in `pathsel/` and by at least one test in `tests/`.
Nothing is listed as not done. Ids that are non-goals or packaging statements (for example N-000067–N-000072, N-000050–N-000055, N-000351–N-000365) are satisfied by the absence of the feature or by the layout, and `test_spec_remaining.py` checks that (stdlib-only imports, no CLI entry, no I/O on import, no mutation of input).

## Conflicts in the spec and what was built

The export lists 11 unsettled contradictions (`CF-…`). Each is decided below. The quotes are from the pack named in brackets.

1. **CF-000005 — filter on a non-array.**
   - "A filter on a non-array yields null, not an empty array" [pack 09, FP-04, N-000202].
   - "A filter applied to anything but an array yields the empty array" [pack 11, FP-06, N-000259].
   - **Built:** null. FP-04 is the feature that defines filters.
2. **CF-000007 — slice of a non-array.**
   - "A slice on a value that is not an array yields null" [pack 08, FP-03, N-000142].
   - "A slice of a value that is not an array is the empty array" [pack 08, FP-03, N-000157].
   - **Built:** null (the normal-behaviour statement).
3. **CF-000011 — multiselect on a null current value.**
   - "On a null current value it still builds one element per expression" [pack 10, FP-05, N-000212].
   - "A multiselect list or hash whose current value is null yields null" [pack 10, FP-05, N-000218].
   - **Built:** null for both lists and hashes (N-000218 names both forms explicitly).
4. **CF-000015 — `not_null` and empty values.**
   - "an empty string or an empty array counts as null for `not_null`" [pack 02, Terminology, N-000022].
   - "an empty array or empty string is not null" [pack 12, FP-07, N-000300].
   - **Built:** not null (N-000300 is the function's own definition).
5. **CF-000027 — object wildcard on a non-object.**
   - "An object wildcard applied to a non-object is the empty array" [pack 02, Terminology "Projection", N-000031].
   - "An object wildcard on a value that is not an object yields null" [pack 09, FP-04, N-000165].
   - **Built:** null (the FP-04 rule, matching the list wildcard).
6. **CF-000035 — string length.**
   - "its length is its number of UTF-8 bytes" [pack 02, Terminology "String", N-000026].
   - "the number of Unicode characters (not bytes) of a string" [pack 12, FP-07 `length`, N-000277].
   - **Built:** `length()` counts Unicode code points. Strings are otherwise not measured anywhere in the language.
7. **CF-000049 — escapes in raw strings.**
   - "No JSON escapes are processed" [pack 10, FP-05, N-000227].
   - "A `\uXXXX` escape inside a raw string literal is decoded to its character" [pack 10, FP-05, N-000239].
   - **Built:** `\'` is a quote, `\uXXXX` is decoded (surrogate pairs combined), and every other backslash is literal. The `\uXXXX` rule is the specific exception to the general one.
8. **CF-000054 — `join` of an empty array.**
   - "`join` of an empty array yields null" [pack 12, FP-07, N-000268, general rule].
   - "the empty array yields the empty string" [pack 12, FP-07, N-000280, the `join` definition].
   - **Built:** the empty string (the function's own definition).
9. **CF-000055 — slice with step 0.**
   - "A step of 0 selects nothing: the result is the empty array" [pack 08, FP-03, N-000133].
   - "A slice whose step is 0 does not succeed on either entry" [pack 08, FP-03, N-000152].
   - **Built:** refused with the zero-slice-step kind, at compile time, so both entries refuse. The spec has a separate failure kind for this, which the refusal uses.
10. **CF-000056 — bare expression reference.**
    - "Outside a function argument it evaluates to null" [pack 02, Terminology "Expression reference", N-000028].
    - "yields a non-null value" [pack 10, N-000234] and "returns a non-`None` value of the implementer's choice" [pack 25, N-000423].
    - **Built:** a non-None `ExpressionReference` object. Two statements and the interface contract agree on non-null.
11. **CF-000057 — `to_number` of an integer numeral.**
    - "a number made from a string by `to_number` is always a floating-point value" [pack 02, Terminology "Number", N-000023].
    - "a string that is an integer numeral becomes that integer" [pack 12, FP-07, N-000287].
    - **Built:** `to_number("42")` is the int `42`; decimal and exponent numerals become floats.

Other points where the spec is ambiguous, read as follows (not in the export's conflict list):

- **Host decimals.** Comparisons treat `Decimal` as a number (N-000024, N-000056). The data model says non-JSON host values are refused by functions that require a JSON type (N-000056–N-000058, FP-07). I read it strictly: `abs`, `sum`, and similar functions refuse `Decimal` with invalid-type. `to_number(Decimal)` is null (its "anything else" rule). `type(Decimal)` is `"number"`.
- **Built-in name versus provider name.** The spec says built-ins stay "unchanged" when a provider is attached (N-000340). A provider method with a built-in name does not replace the built-in.

## Choices where the spec leaves the implementer free

- N-000198: a slice written directly after an index starts a projection (`a[0][0:1]` projects). This follows the binding-power rule.
- N-000199: later steps join a right-hand side that begins with a dot and a multiselect hash/list (`a[*].{n: n}.n`).
- N-000333: any `collections.abc.Mapping` is accepted where a function requires an object.
- N-000385 / N-000392: the parsed-expression type is `pathsel.ParsedExpression`. The library does not publish its own options class; options are read by attribute.
- N-000407 / N-000408: exception types are `PathSelEmptyError`, `PathSelIncompleteError`, `PathSelSyntaxError` (with `PathSelTokenError` as a subclass), `PathSelZeroStepError`, `PathSelUnknownFunctionError`, `PathSelArityError`, `PathSelTypeError`. All derive from `PathSelError(ValueError)`. Messages are free text.

## Things the spec does not state (and what I assumed)

Parsing:

- The kind for `&` followed by nothing, and for a missing `:` in a multiselect hash, is not stated. `&` at end of text is incomplete. A missing `:` is syntax, except at end of text, which is incomplete.
- A number is not an expression, so `1`, `foo(1)`, and `{a: 1}` are syntax errors. Numbers appear only inside brackets.
- A multiselect list directly after an operand (`a[0,1]`, `a[0][b]`) is syntax. The reported position is the `[`.
- Unquoted identifiers are ASCII-only (`[A-Za-z_][A-Za-z0-9_]*`, per FP-02). Any other character that begins no token (including a lone `?` outside a filter, `#`, `$`, `;`, or non-ASCII letters) is a token-level syntax error.
- Whitespace is space, tab, LF and CR only.
- `[` followed by whitespace and `]` is the flatten operator. `[` followed by whitespace and `?` is a filter.
- A JSON literal ends at the first backtick (there is no escape for backticks). Content that is not JSON is read as JSON string content after stripping leading whitespace. `NaN` and `Infinity` are not JSON and are not accepted as JSON.
- A quoted identifier is decoded with strict JSON, so raw control characters are rejected.
- `lex_position` is the character offset (Python `str` index) of the failing token. End of text counts as offset `len(text)`.

Evaluation:

- Function calls are checked when evaluated, so an uncalled branch (for example the right side of a true `||`, or a projection over an empty array) never refuses.
- Order of checks inside a call: name, then argument count, then each argument's type, left to right. Arguments are evaluated before types are checked. An expression reference argument is passed unevaluated.
- Ordering comparisons (`<`, `<=`, `>`, `>=`) between values that are not both numbers or both strings yield null. The spec does not say.
- `==` on an `ExpressionReference` compares identity.
- `contains(string, x)` requires `x` to be a string.
- `max`/`min`/`sort` accept an array of all numbers or all strings, never mixed; empty arrays are fine.
- `sort_by`, `max_by` and `min_by` key checks run only over elements that exist, so an empty array never refuses.
- `avg` returns a float. `sum` of an empty array is `0`. `ceil`/`floor` return ints; non-finite floats are refused with invalid-type (no integer result exists).
- `type()` of a host value that is not a JSON type and not a Decimal is null.
- `to_string` of a value JSON cannot encode uses `str()`; NaN serialises as `NaN`.
- `to_number` accepts an optional leading `+` or `-`. Surrounding whitespace is not allowed. `"1."` is a decimal numeral. `NaN` and `Infinity` are not numerals.
- `merge` builds its result with the supplied mapping type (`dict_cls`) when one is given.
- A Python `tuple` counts as an array; any `Mapping` counts as an object. Output is not normalised: tuples selected from the document come back as tuples.
- A multiselect hash with a repeated key keeps the last value (ordinary mapping assignment).
- Result objects may share structure with the input document. Evaluation never writes to the input.

Providers:

- Only the five type names in `signature` are allowed. `"boolean"` is not declarable, so `signature` raises `ValueError` for it at decoration time, and a custom function therefore never accepts a boolean argument.
- Custom `number` arguments exclude booleans and `Decimal`.
- Any `_func_<name>` attribute with a `signature` marker is a provider function. Its name is the text after `_func_`.

## Not verified

- Python 3.9 runtime: the code uses only 3.9-compatible syntax (`ast.parse(..., feature_version=(3, 9))` passes in the test suite) and standard-library calls available on 3.9. The tests were run only on Python 3.13.
- The packaging metadata was not built: setuptools is not installed in this environment, so `pyproject.toml` is written but not exercised.
- The hidden acceptance tests were not seen or used, as the task required.
