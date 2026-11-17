# NOTES

Implementation of PathSel (`pathsel` package) from `spec/`. Layout: flat package
`pathsel/` at the repository root, `pyproject.toml` (setuptools, zero runtime
dependencies), tests in `tests/`. `spec/` is unchanged.

Modules: `pathsel/__init__.py` (search, compile, ParsedExpression),
`lexer.py`, `parser.py` (Pratt parser), `nodes.py` (expression tree and
evaluation), `values.py` (truthiness, equality, JSON text), `functions.py`
(built-ins, `Functions`, `signature`), `errors.py` (failure carriers).

Checklist coverage: every one of the 423 ids in `spec/CHECKLIST.md` has a
`# spec: <id>` marker in `pathsel/` or `tests/`. `tests/test_spec_coverage.py`
fails if one is missing. Behaviour is covered by `tests/test_pathsel.py`.
No acceptance-criteria labels exist in this export (every pack says "AC labels:
none"), so tests are named by feature, not `test_AC_*`. Nothing is listed as not
done. Ids that are non-goals (N-000067..072) or implementer's choice (N-000198,
N-000199, N-000333, N-000385, N-000392, N-000407, N-000408) are satisfied by
design, as described below.

Test status: `python3 -m pytest -q tests` gives 113 passed on Python 3.13.
Python 3.9 was not available to run the tests; the source parses with the 3.9
grammar (`ast.parse(..., feature_version=(3, 9))`) and the package imports under
3.11.

## Spec conflicts

### Listed as unsettled by the export (`spec/MAP.md`, CF ids)

Each has no human verdict. Built behaviour is in brackets.

1. **CF-000005, filter on a non-array.** N-000202 (FP-04): "A filter on a non-array
   yields null." vs N-000259 (FP-06): "A filter applied to anything but an array
   yields the empty array." [null]
2. **CF-000007, slice on a non-array.** N-000142 (FP-03, normal behaviour): "yields
   null." vs N-000157 (FP-03, boundary): "is the empty array." [null]
3. **CF-000011, multiselect on a null current value.** N-000212 (FP-05): "still builds
   one element per expression." vs N-000218 (FP-05): "whose current value is null
   yields null." [null, the later and more general rule]
4. **CF-000015, `not_null` and empty values.** N-000022 (Terminology, Null): "an empty
   string or an empty array counts as null for `not_null`." vs N-000300 (FP-07, the
   `not_null` definition): "an empty array or empty string is not null." [not null;
   the function's own definition governs]
5. **CF-000027, object wildcard on a non-object.** N-000031 (Terminology, Projection):
   "the empty array." vs N-000165 (FP-04): "yields null." [null]
6. **CF-000035, string length.** N-000026 (Terminology, String): "its length is its
   number of UTF-8 bytes." vs N-000277 (FP-07 `length`): "the number of Unicode
   characters (not bytes)." [Unicode code points, so `length("héllo")` is 5]
7. **CF-000049, escapes in raw strings.** N-000227 (FP-05): "No JSON escapes are
   processed." vs N-000239 (FP-05): "a `\uXXXX` escape inside a raw string literal is
   decoded to its character." [`\'` is a quote and `\uXXXX` (four hex digits) is
   decoded; every other backslash is literal]

### Not listed by the export (found while reading)

8. **`join` of an empty array.** FP-07 intro (N-000268): "`join` of an empty array
   yields null." vs the `join` definition (N-000280): "the empty array yields the empty
   string." [empty string, the function's definition]. Tested in
   `test_string_and_membership_functions`.
9. **Result type of `to_number`.** Terminology, Number: "a number made from a string by
   `to_number` is always a floating-point value." vs FP-07 `to_number` (N-000287): "a
   string that is an integer numeral becomes that integer." [integer numerals give
   `int`; decimal and exponent numerals give `float`. Equal by value either way.]
10. **Expression reference on its own.** Terminology: "Outside a function argument it
    evaluates to null." vs FP-05 (N-000235): "yields a non-null value", and the
    Interface Contract (N-000423): "returns a non-`None` value." [non-null: the search
    returns an `ExpressionReference` object]
11. **A lone `=`.** Terminology, Grammar-level: "A single `=` is a grammar-level failure
    of this kind." vs FP-06 (N-000260): "A lone `=` is a token-level syntax failure."
    [token-level, a subclass of the syntax kind. A test that checks only for
    `ValueError` or the syntax kind passes either way.]
12. **Signature type names.** Interface Contract (N-000402) lists five type names
    (`number`, `string`, `array`, `object`, `null`), but FP-07 and FP-08 accept
    booleans and "any" value. [Also accepted: `boolean`, `any`. Built-in parameters
    also use an internal `reference` name for expression references.]

## Choices the spec leaves open

- **Projection placement (N-000198, N-000199).** A slice after an index or after another
  slice always starts a projection (the JMESPath rule). When a right-hand side begins
  with a dot followed by a multiselect list or hash, later steps join it, because
  they rank tighter than the projection.
- **Accepted object arguments (N-000333).** Any `collections.abc.Mapping` is an object,
  so `dict` and `OrderedDict` are both accepted, as are host mappings.
- **Options (N-000392).** No options class is published. `search` and `compile` read
  `dict_cls` and `custom_functions` from any object with those attributes, with
  `None` as the default for each missing attribute. `options=None` is allowed.
- **Failure carrier names (N-000407, N-000408).** `PathSelError(ValueError)` is the base.
  Then `EmptyExpressionError`, `IncompleteExpressionError`, `PathSelSyntaxError` (the
  grammar-level syntax kind), `TokenSyntaxError(PathSelSyntaxError)`,
  `ZeroSliceStepError`, `UnknownFunctionError`, `InvalidArityError`, `InvalidTypeError`.
  The message text is informational. Empty, incomplete and syntax failures carry
  `lex_position`, an `int`.
- **Parsed-expression type (N-000385).** `pathsel.ParsedExpression`, with
  `.search(value, options=None)` and `.expression` (the source text).
- **Filter and slice on non-arrays**, resolved above as CF-000005 and CF-000007.

## Assumptions (not stated in the spec)

- **Bare numbers are not expressions.** Numbers appear only inside `[...]` (index and
  slice). `abs(-5)` is a syntax failure; write ``abs(`-5`)`` (a JSON literal).
- **Ordering across unlike kinds.** `<`, `<=`, `>`, `>=` between values that are not
  both numbers or both strings (including booleans and null) yield null.
- **`type()` of a host value outside the JSON model** (for example a set) is `"null"`.
  `to_string()` of such a value is its `str()` as a JSON string.
- **Host values.** A tuple is an array. `Decimal` is a number. A mixed `Decimal`/`float`
  `sum` falls back to floats.
- **Null is not short-circuited along a dot.** `missing.abs(@)` calls `abs(null)`, which
  is an invalid-type refusal. `missing.length(@)` behaves the same way.
- **Zero slice step** is refused when the expression is compiled, not later. FP-03 allows
  either the compile or the search to refuse.
- **`contains(string, x)`** with a non-string `x` is `false`.
- **`merge`** returns a plain `dict`, even when `dict_cls` is supplied. Only multiselect
  hashes use `dict_cls`.
- **`ceil` and `floor`** of infinity or NaN are invalid-type refusals (JSON has no such
  values; the spec is silent).
- **`avg`** returns a float. `sum([])` is `0`. `max([])`, `min([])`, `avg([])`,
  `max_by([])`, `min_by([])` are null. `sort_by` is stable. `max_by` and `min_by` keep
  the first element on ties.
- **Multiselect hash, duplicate keys:** the last value wins.
- **JSON literal that is not valid JSON** is read as JSON string content after the
  leading whitespace is removed (as the spec says). If that also fails, it is a token-level
  refusal.
- **Raw string `\uXXXX`** with fewer than four hex digits stays literal.
- **Whitespace before brackets.** `[ ]` (with a space) is not the flatten operator; it is
  an empty bracket and a syntax failure. `[ ?` (with a space) is a filter opener. Spaces are
  allowed everywhere else between tokens.
- **Order of failure detection.** The whole text is tokenized before parsing, so a
  token-level refusal later in the text is reported before an earlier grammar-level
  one. Positions are the offset of the offending token.
- **End of text.** Unexpected end of text is the incomplete kind, with position `len(text)`.
  The exception is a dot followed by end of text, which is a syntax failure (FP-02 and
  FP-01 list it under syntax). Empty text has position `0`.
- **Custom functions.** Built-in names cannot be overridden by a provider, which keeps
  FP-08's "every FP-07 function remains available with unchanged behavior". A custom
  function is an attribute `_func_<name>` decorated with `signature`; undecorated
  attributes are unknown functions. An invalid type name passed to `signature` raises
  `ValueError` when the decorator is applied. That is a programming error, not a refusal.
- **Returned values.** Literals are deep-copied on each evaluation, so callers cannot change
  a compiled expression by mutating a result. Inputs are never mutated.

## Known gaps

- Python 3.9 was not run; only the grammar and a 3.11 import were checked.
- The hardware and packaging ids (N-000351..365) are satisfied by reading: pure Python,
  no dependencies, flat layout, `pyproject.toml`. No platform matrix was run.
