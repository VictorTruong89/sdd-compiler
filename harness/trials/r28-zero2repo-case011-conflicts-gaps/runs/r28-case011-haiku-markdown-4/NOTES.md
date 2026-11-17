# NOTES — pathsel implementation

Layout (per `spec/Interface_Contract.md`): flat package `pathsel/` at the repo root.

- `pathsel/__init__.py` — `search`, `compile`, `Options`, `ParsedExpression`, error re-exports
- `pathsel/parser.py` — tokenizer and Pratt parser
- `pathsel/nodes.py` — expression tree and evaluation
- `pathsel/functions.py` — `Functions` provider, `signature`, built-in functions
- `pathsel/values.py` — truthiness, JSON equality, ordering, object helpers
- `pathsel/errors.py` — refusal types
- `pyproject.toml` — setuptools metadata (zero runtime dependencies)
- `conftest.py` — empty; puts the project root on `sys.path` for pytest
- `tests/test_pathsel.py` — behaviour tests for each feature point (`python3 -m pytest -q`)

## Conflicts inside the specification

Where two statements disagree, I followed the more specific one and list both here.

1. **Filter on a non-array.** `Full_PRD.md` line 175 (FP-04 boundary): "A filter on a non-array yields null, not an empty array". Line 215 (FP-06): "A filter applied to anything but an array yields the empty array." → **null**.
2. **Slice on a non-array.** Line 138 (FP-03 normal): "A slice on a value that is not an array yields null." Line 148 (FP-03 boundary): "A slice of a value that is not an array is the empty array." → **null**.
3. **Object wildcard on a non-object.** Line 32 (Terminology, "Projection"): "An object wildcard applied to a non-object is the empty array." Line 159 (FP-04): "An object wildcard on a value that is not an object yields null." → **null**.
4. **`not_null` and empty values.** Line 23 (Terminology, "Null"): "An empty string or an empty array counts as null for `not_null`." Line 252 (FP-07): "(an empty array or empty string is not null)". → **not null**; only a missing or JSON `null` value is skipped.
5. **`to_number` on integer numerals.** Line 26 (Terminology): "A number made from a string by `to_number` is always a floating-point value." Line 247 (FP-07): "a string that is an integer numeral becomes that integer". → **integer** for an integer numeral, float otherwise.
6. **`join` of an empty array.** Line 230 (FP-07 preamble): "`join` of an empty array yields null." Line 242 (FP-07 definition): "the empty array yields the empty string." → **empty string** (the definition).
7. **A bare expression reference.** Line 29 (Terminology): "Outside a function argument it evaluates to null." Line 193 (FP-05): "Searching an expression reference on its own ... yields a non-null value". → **non-null**: an `ExpressionReference` object (Interface: "non-None value of the implementer's choice").
8. **Multiselect on a null current value.** Line 187 (FP-05): "On a null current value it still builds one element per expression." Line 188 (same bullet, last sentence): "A multiselect list or hash whose current value is null yields null." → **multiselect list** still builds one element per expression (nulls stored); **multiselect hash** yields null.
9. **Projection extent for wildcards.** Line 166 ranks a list wildcard written as a step at 5, the tightest rank, but a dot step at 4. Read literally, `foo[*].bar.baz` would stop the projection before `.baz`, which contradicts the basic projection example. → The projection threshold for `[*]`, slices and `*` is the same wherever it starts (it joins steps that bind tighter than it), so `foo[*].bar.baz` projects both steps. Brackets (index, slice, `[*]`, multiselect) that follow an operand join a right-hand side. Filter and flatten follow the rank table.

## Interpretations where the specification is silent

- **Ordering of incomparable values.** `<`, `<=`, `>`, `>=` between values that are not two numbers or two strings yield null (JMESPath behaviour). Equality is always a boolean.
- **Token errors versus grammar errors.** The whole text is tokenized before parsing, so a token-level failure anywhere wins over an earlier grammar-level failure. Both are syntax kinds, and the token-level form is the more specific one.
- **Dot followed by end of text** is a syntax failure, as FP-01 says. Other missing operands at the end of the text (after `|`, `&&`, `==`, `(`, `[`, …) are incomplete failures. The position of an incomplete failure is the text's length.
- **Multiselect after an operand.** The error position is the offset of the `[`.
- **Zero slice step** is raised when the expression is compiled, so both entries refuse it.
- **Numbers.** Number tokens are integers, with an optional leading minus. A float such as `1.5` is not a token and is a grammar-level failure.
- **Identifiers** are ASCII letters, digits and underscores only. Any other character that begins no token is a token-level failure.
- **Quoted identifiers and JSON literals** are decoded with `json.loads(strict=False)`, so raw control characters are accepted (FP-02 says control characters are allowed in keys).
- **JSON literal fallback.** A literal that is not JSON is read as JSON string content after its leading whitespace is removed. The sequence `` \` `` inside a literal stands for a backtick.
- **Raw strings.** Only `\'` and `\uXXXX` are processed; every other backslash is kept.
- **Arrays and objects.** A `list` or `tuple` is an array. A `Mapping`, or an instance of the caller's `dict_cls`, is an object. A host `Decimal` is a number in comparisons and in `==`, but built-in functions that require a JSON number refuse it (FP-07 says built-in arguments need JSON types).
- **Truthiness.** The false values are false, null, `""`, `[]` and `{}`. `0` and `0.0` are true.
- **Equality.** Booleans never equal numbers. Arrays and objects compare deeply, with object key order ignored.
- **`type()`** returns `"null"` for a host value that is none of the JSON types. This is a guess.
- **`to_string`** writes compact JSON with `ensure_ascii=True`. A `Decimal` is written as a float, and any other non-JSON host value as its `str()`.
- **`to_number`** accepts an integer numeral (`-?[0-9]+`), or a decimal or exponent numeral that Python's `float()` accepts. It does not accept surrounding spaces or a leading `+`.
- **`sum([])`** is `0`. **`avg`** returns a float. **`sort` / `sort_by`** on mixed key types refuse as invalid-type.
- **`max_by` / `min_by`** keep the first element on ties. **`sort_by`** is stable.
- **`merge`** returns a plain `dict`, not the caller's `dict_cls`.
- **`contains`** on a string needs a string second argument. Otherwise it refuses as invalid-type.
- **`map`** keeps nulls, as FP-07 says.
- **Literals** are deep-copied on each evaluation, so a caller cannot mutate a compiled expression through a returned value.
- **Function-call checks** run in this order: name (unknown-function), argument count (invalid-arity), argument evaluation, then argument types (invalid-type).
- **Built-ins take precedence** over a provider. A provider can add functions but cannot change a built-in. A name that is neither is an unknown-function refusal.
- **Custom functions** are found on the provider instance (`_func_<name>` attribute carrying a `signature` declaration). Subclassing `Functions` is one way to get that, and any object with the attributes works.
- **Options** are read by duck typing (`dict_cls`, `custom_functions`). A library class `Options` is also provided.
- **Refusal types.** `EmptyExpressionError`, `IncompleteExpressionError`, `PathSelSyntaxError`, `TokenSyntaxError` (a subclass of `PathSelSyntaxError`), `ZeroSliceStepError`, `UnknownFunctionError`, `InvalidArityError` and `InvalidTypeError`. All derive from `PathSelError`, which derives from `ValueError`. Syntax and incomplete refusals carry `lex_position`.
- **Constructed hashes with a custom `dict_cls`** are read through `keys()` and `[]`, so a non-`Mapping` class also works.
- **Empty `[]` at the start of an expression** is a flatten of the current value, not an empty multiselect.
