# NOTES — pathsel implementation

Layout: the importable package is `/app/pathsel/` (flat layout, `pyproject.toml`
packages it with setuptools). Tests are in `/app/tests/test_pathsel.py`
(stdlib `unittest`; run `python -m pytest tests` from `/app`). Line numbers below
refer to `spec/Full_PRD.md` ("PRD") unless stated otherwise.

## Part 1 — Conflicts inside the specification

For each conflict: what each side says, and what was built.

### C1. A lone `=`: grammar-level or token-level?
- PRD line 37 (Terminology, "Grammar-level syntax failure"): "A single `=` is a grammar-level failure of this kind."
- PRD line 219 (FP-06): "A lone `=` is a token-level syntax failure; equality is the two-character token `==`."
- **Built:** token-level (`TokenSyntaxError`, a subclass of `ExpressionSyntaxError`). The FP-06 statement is the specific rule.

### C2. Object wildcard on a non-object: empty array or null?
- PRD line 32 (Terminology, "Projection"): "An object wildcard applied to a non-object is the empty array."
- PRD line 159 (FP-04): "An object wildcard on a value that is not an object yields null."
- **Built:** null. This matches the general rule at PRD line 23 ("a selector applied to the wrong kind of value all yield null") and the list wildcard rule at FP-04 line 158.

### C3. Filter on a non-array: empty array or null?
- PRD line 215 (FP-06): "A filter applied to anything but an array yields the empty array."
- PRD line 161 (FP-04): "Its left-hand value must be an array; otherwise the result is null." Line 175: "A filter on a non-array yields null, not an empty array and not a failure."
- **Built:** null (FP-04 states it explicitly, and says "not an empty array").

### C4. Slice on a non-array: null or empty array?
- PRD line 138 (FP-03, normal behaviour): "A slice on a value that is not an array yields null."
- PRD line 148 (FP-03, boundary): "A slice of a value that is not an array is the empty array."
- **Built:** null (the normal-behaviour rule, consistent with line 23).

### C5. Slice with step 0: empty array or refusal?
- PRD line 133 (FP-03, normal behaviour): "A step of 0 selects nothing: the result is the empty array."
- PRD line 146 (FP-03, boundary): "A slice whose step is 0 does not succeed on either entry ... zero-slice-step kind."
- The zero-slice-step kind exists only if line 146 holds (Interface Contract, failure carriers).
- **Built:** refusal (`ZeroSliceStepError`). It is raised when the slice is evaluated, so `compile` succeeds and the search refuses, which PRD line 146 allows. It is raised regardless of the value's type.

### C6. Multiselect list on a null current value
- PRD line 187 (FP-05): "On a null current value it still builds one element per expression."
- PRD line 188 (FP-05): "A multiselect list or hash whose current value is null yields null."
- **Built:** null for both list and hash (line 188 is the explicit rule for both forms).

### C7. `not_null` and empty values
- PRD line 23 (Terminology, "Null"): "An empty string or an empty array counts as null for `not_null`."
- PRD line 252 (FP-07): "the first that is not null, or null if all are null (an empty array or empty string is not null)."
- **Built:** an empty string or empty array is not null (the function definition).

### C8. Length of a string: bytes or characters?
- PRD line 27 (Terminology, "String"): "its length is its number of UTF-8 bytes."
- PRD line 240 (FP-07, `length`): "the number of Unicode characters (not bytes) of a string."
- **Built:** Unicode code points (`len(str)`), the FP-07 definition.

### C9. `to_number` result type
- PRD line 26 (Terminology, "Number"): "A number made from a string by `to_number` is always a floating-point value."
- PRD line 247 (FP-07, `to_number`): "a string that is an integer numeral becomes that integer, otherwise ... that floating-point number."
- **Built:** integer numerals give `int`, decimal or exponent numerals give `float` (the FP-07 algorithm).

### C10. `join` of an empty array
- PRD line 230 (FP-07, general rule): "`join` of an empty array yields null."
- PRD line 242 (FP-07, `join` definition): "the empty array yields the empty string."
- **Built:** the empty string (the function's own definition). To follow line 230 instead, make `_func_join` in `functions.py` return `None` when the array is empty.

### C11. Expression reference outside a function argument
- PRD line 29 (Terminology, "Expression reference"): "Outside a function argument it evaluates to null."
- PRD line 193 (FP-05): searching a bare expression reference "succeeds and yields a non-null value".
- `spec/Interface_Contract.md` ("Expression reference value"): a bare expression reference "returns a non-`None` value".
- **Built:** a non-null `ExpressionReference` object, both on its own and inside multiselect elements.

## Part 2 — Behaviour the specification does not state (assumptions)

- **Ordering across types:** `<`, `<=`, `>`, `>=` between values that are not both numbers or both strings yield null (the PRD does not say). Ordering a value with a `null` also yields null.
- **Host values:** `list` and `tuple` are arrays; any `collections.abc.Mapping` (and the `dict_cls` of a search) is an object; `Decimal` is a number. Other host values are truthy, are returned as selected, and `type()` reports them as `"null"`.
- **Equality:** deep JSON equality; a host value that is neither a JSON type nor a container compares with `==`, and an error during that comparison counts as not equal.
- **Built-in names win:** a provider's `_func_<name>` never replaces a built-in of the same name (FP-07 says built-ins keep unchanged behaviour). Custom names that collide are ignored.
- **Signature extensions (internal):** `signature()` accepts the five public type names plus `any` and `expref` (an expression reference), and an optional `"repeat": True` on the last parameter (one or more arguments). The built-ins `merge` and `not_null` use `repeat`. The `repeat` key is an addition beyond the Interface Contract; it is harmless to custom providers that do not use it.
- **Custom function arguments:** type names `number`, `string`, `array`, `object`, `null` are checked as the Interface Contract states. A reference, or any non-JSON host value, fails the type check. `array` also accepts tuples.
- **Check order:** name, then argument count (before argument evaluation), then argument evaluation left to right, then argument types left to right, then the call.
- **Token errors first:** the whole text is tokenized before parsing, so a token-level failure anywhere wins over an earlier grammar-level failure. Grammar errors are reported at the first offending token in parse order.
- **Incomplete vs syntax:** end of text where an operand or closing token is still required gives the incomplete kind. A dot followed by end of text is a syntax failure (FP-01 line 95). Whitespace-only text is incomplete at position `len(text)`. Empty text is the empty kind.
- **Numbers:** a number is valid only inside index or slice brackets. A bare number as an operand (for example `5`, `f(1)`, `a == 5`) is a grammar-level syntax failure. Use a JSON literal (`` `5` ``) instead. Numbers are signed integers only (`-?[0-9]+`).
- **Adjacency:** `[]` (flatten) and `[?` (filter) must be written without a space between the brackets. `[ ]` is a syntax failure.
- **Dots and functions:** `a.abs(@)` is accepted (the identifier after a dot is an operand, so a call is allowed).
- **Wildcard ranks:** a `.*` after a dot ranks as a dot step (binding power 40). A `*` that begins an operand, or is the first step of a projection's right-hand side, ranks as a list wildcard (binding power 20). This is the JMESPath-compatible reading of FP-04 lines 164–169.
- **Slices after an index or slice** start a projection (one of the two placements FP-04 line 170 leaves open).
- **Raw strings** (`'...'`): only `\'` and `\uXXXX` are processed. Other backslashes stay literal. A `\uXXXX` escape with surrogate pairs is combined.
- **JSON literals** (`` `...` ``): `` \` `` is an escaped backtick. Text that is not JSON is read as the body of a JSON string after leading whitespace is removed (FP-05 line 191). Literal values are deep-copied on every evaluation, so a caller mutating a result cannot change the compiled expression.
- **Quoted identifiers** are decoded strictly with `json.loads`. A raw control character inside the quotes is a token-level failure.
- **Projections** drop null results. A projection over a missing value is null; over an empty array it is the empty array.
- **Slices:** a zero step is refused when the slice node is evaluated. An omitted step is 1. Slice bounds follow FP-03 lines 135–136.
- **Numeric functions:** `sum([])` is `0`; `avg` returns a float; `avg`, `max`, `min`, `max_by`, `min_by` of an empty array are null; `ceil`/`floor` of a non-finite float are null; `sort_by` is stable.
- **`merge`** returns a plain `dict` (not the `dict_cls` of the options). Later keys overwrite earlier ones.
- **`to_string`:** `json.dumps` with compact separators and `ensure_ascii=True`. A `Decimal` is written as a float. A non-JSON host value is written with `str()`.
- **`to_number`:** accepts an optional leading `-` on an integer or decimal numeral with optional exponent. `+`, surrounding whitespace, underscores and `NaN`/`Infinity` are refused (null).
- **`contains` on a string** needs a string second argument, otherwise invalid type.
- **Options:** `dict_cls` and `custom_functions` are read with `getattr`, so any object with those attributes works. `options=None` means no mapping type and no provider. Constructed objects are created with `dict_cls()` and filled by item assignment. While a search runs, instances of `dict_cls` count as objects for field selection, wildcards, filters, comparisons, truthiness and built-in arguments.
- **Non-string expression text** raises `TypeError`, which is a programming error, not one of the refusal kinds.
- **Deep chains:** evaluation recurses once per step of a chain such as `a.a.a...`. Very long expressions (thousands of steps) can exceed Python's recursion limit. This is not covered by the PRD.
- **Error attributes:** every syntax and incomplete refusal sets `lex_position` (an `int`). Other refusals have no position.

## Part 3 — Files

- `pathsel/__init__.py` — public names: `search`, `compile`, `ParsedExpression`, `Functions`, `signature`, the refusal classes.
- `pathsel/api.py` — `search` and `compile` (the parsed expression's `.search`).
- `pathsel/lexer.py` — tokenizer (token-level failures).
- `pathsel/parser.py` — Pratt parser with the binding powers of the PRD.
- `pathsel/nodes.py` — AST node classes and their evaluation.
- `pathsel/values.py` — type tests, truthiness, JSON equality, ordering, expression reference.
- `pathsel/functions.py` — `Functions` (built-ins), `signature`, the function table.
- `pathsel/errors.py` — refusal classes (all subclasses of `ValueError`).
- `tests/test_pathsel.py` — behaviour checks.
- `pyproject.toml` — setuptools metadata (flat layout, no runtime dependencies).
