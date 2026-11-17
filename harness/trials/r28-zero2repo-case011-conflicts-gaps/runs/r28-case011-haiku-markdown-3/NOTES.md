# NOTES: PathSel (`pathsel` package)

Build: pure Python, no dependencies, importable from `/app` (flat layout, `pathsel/` at the root).
`pyproject.toml` is provided for setuptools packaging. `conftest.py` at the root lets pytest import
`pathsel` when tests live in `tests/`. Regression tests: `python3 -m pytest -q` (94 pass on CPython 3.13).

Not verified here: Python 3.9–3.12 and PyPy, Windows and macOS, and an actual `pip install`
of `pyproject.toml`. Only CPython 3.13 was available.

## Part 1: Conflicts between spec files

Each item quotes both sides, then states what was built.

1. **Filter on a non-array.**
   - Full_PRD.md FP-04: "Its left-hand value must be an array; otherwise the result is null" and "A filter on a non-array yields null, not an empty array".
   - Full_PRD.md FP-06: "A filter applied to anything but an array yields the empty array."
   - **Built:** null. FP-04 is the feature point that defines filters and is explicit about it.

2. **Object wildcard on a non-object.**
   - Full_PRD.md, Terminology, "Projection": "An object wildcard applied to a non-object is the empty array."
   - Full_PRD.md FP-04: "An object wildcard on a value that is not an object yields null."
   - **Built:** null (FP-04).

3. **Slice with step 0.**
   - Full_PRD.md FP-03 normal behavior: "A step of 0 selects nothing: the result is the empty array."
   - Full_PRD.md FP-03 boundary: "A slice whose step is 0 does not succeed on either entry ... zero-slice-step kind", and the failure-kind list in Terminology.
   - **Built:** refused as `ZeroSliceStepError`, at compile time, so both entries refuse the same text.

4. **Multiselect on a null current value.**
   - Full_PRD.md FP-05: "On a null current value it still builds one element per expression."
   - The same FP-05 section: "A multiselect list or hash whose current value is null yields null."
   - **Built:** null, from the closing rule. Each element is not built.

5. **`join` of an empty array.**
   - Full_PRD.md FP-07 definition: "the empty array yields the empty string."
   - Full_PRD.md FP-07 closing note: "`join` of an empty array yields null."
   - **Built:** null (the specific note).

6. **Expression reference used on its own.**
   - Full_PRD.md, Terminology "Expression reference": "Outside a function argument it evaluates to null."
   - Full_PRD.md FP-05 and Interface_Contract.md "Expression reference value": a bare reference "yields a non-null value" / "returns a non-`None` value of the implementer's choice."
   - **Built:** a non-null `pathsel.values.ExpressionReference` object. It carries the node and the evaluation context, so `map` and `sort_by` can apply it.

7. **Host decimal numbers.**
   - Full_PRD.md Terminology "Number": "Host decimal values participate as numbers in comparisons."
   - Full_PRD.md Non-functional "Data model": a function argument that requires a JSON type "refuses" host values that are not JSON types.
   - **Built:** `Decimal` is a number for `==` and ordering only. Function arguments reject it as `InvalidTypeError`. `type()` reports it as `"number"`.

## Part 2: Things the spec does not state (assumptions)

**Values and types**
- Object = any `collections.abc.Mapping`. Array = `list` or `tuple`. A string is never an array.
- Ordering (`<`, `<=`, `>`, `>=`) of values that are not both numbers, or both strings, yields null. The spec is silent here.
- `type()` returns `"null"` for host values that are not JSON types, other than `Decimal`. The spec lists only six names.
- `to_number` numeral grammar: an integer numeral is `-?[0-9]+`. A float numeral is `-?(digits.digits* | .digits | digits)([eE][+-]?digits)?`. No surrounding whitespace and no leading `+`.
- Function results built from a host mapping (`merge`) are plain `dict`s. Only multiselect hashes use `dict_cls`.

**Lexing and syntax**
- The whole text is tokenized before parsing. A token-level failure anywhere in the text wins over a grammar failure.
- A bare number outside brackets (for example `length(1)`) is an operand the grammar does not define, so it is a syntax failure. JSON numbers come from backtick literals.
- `[]` is flatten only when the two brackets are adjacent. `[ ]` is a syntax failure.
- Incomplete-expression position is the end of the text (`len(text)`). A dot followed by end of text is a syntax failure, as FP-01 says, not an incomplete one.
- A function call may follow a dot (`foo.length(@)`). The call's `@` is the value of `foo`.
- A dot followed by `[` must start a multiselect list. `.[0]`, `.[*]`, `.[]`, `.[?…]` and `.[a:b]` are syntax failures.
- A projection's right-hand side ends at a flatten token, so `foo[*][]` flattens the projection result.
- Placement choices (FP-04 allows the implementer to pick): a slice or index written directly after an operand is an ordinary step. A slice written directly after a projection starts a projection. A dot step followed by a multiselect list applies later steps to the multiselect result, not inside the right-hand side.
- Raw strings: backslash-quote gives a quote, `\uXXXX` (four hex digits) is decoded, and any other backslash is kept as written. Inside backtick literals, backslash-backtick gives a backtick.
- A JSON literal that is not valid JSON falls back to a JSON string body with leading whitespace removed (the legacy rule the spec describes).

**Evaluation**
- Type checks on function arguments run even when the current value is null. For example `length(missing)` is `InvalidTypeError`.
- Builtin names always resolve to the built-in implementation. A provider subclass that overrides a built-in method name does not change the built-in.
- A custom signature with an empty `types` list accepts any value. `boolean` and `any` are accepted as type names in `signature`, in addition to the five the spec lists.
- Custom functions are looked up on the provider with `getattr(provider, "_func_" + name)`. Only callables carrying the `signature` mark count as functions.
- `sort_by`, `max_by` and `min_by` check every key before comparing, so a single null key is an invalid-type failure even when it is the only element.
- `max_by` and `min_by` return the first element on a tie. `sort_by` is stable.
- `sum` of an empty array is `0`. `avg` of an empty array is null. `max` and `min` of an empty array are null.
- `ceil` and `floor` return `int`. Infinite or NaN floats are not handled specially.
- `to_string` uses compact JSON with `ensure_ascii=True`. Numbers use Python's float and int formatting.
- `not_null` tests `is not None`, so `""` and `[]` count as non-null.
- Output is never shared with the input: literals are deep-copied, and projections and slices build new lists.

**Errors**
- Exception type names are chosen by this implementation. Every refusal is a `pathsel.errors.PathSelError`, which is a `ValueError`. The names are `EmptyExpressionError`, `IncompleteExpressionError`, `ExpressionSyntaxError`, `TokenSyntaxError` (a subclass of `ExpressionSyntaxError`), `ZeroSliceStepError`, `UnknownFunctionError`, `InvalidArityError` and `InvalidTypeError`. All are exported from `pathsel`.
- `lex_position` is an `int` on incomplete and syntax refusals.
- `compile(non_str)` raises `TypeError`. This is not a refusal kind in the spec.

**Limits**
- Expression nesting and data nesting are limited by Python's recursion limit. No other limit is set.

## Part 3: Layout

- `pathsel/__init__.py`: `search`, `compile`, `ParsedExpression`, and error re-exports.
- `pathsel/errors.py`: refusal kinds.
- `pathsel/values.py`: truthiness, JSON equality, ordering, `ExpressionReference`.
- `pathsel/functions.py`: `signature`, `Functions`, and the built-in specs and implementations.
- `pathsel/lexer.py`: tokenizer.
- `pathsel/parser.py`: Pratt parser with the FP-04 projection rules.
- `pathsel/nodes.py`: AST node classes and their evaluation.
- `tests/test_pathsel.py`: regression tests keyed to the PRD feature points.
