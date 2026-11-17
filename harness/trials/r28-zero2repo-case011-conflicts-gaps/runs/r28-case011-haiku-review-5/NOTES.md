# NOTES

Implementation notes for the `pathsel` library. The specification is in `spec/` and was not modified.
Line numbers refer to `spec/Full_PRD.md` unless another file is named.

## What is here

- `pathsel/` is the importable package (flat layout at the project root).
  - `__init__.py`: `search`, `compile`, `ParsedExpression`, `Options`, and the refusal types.
  - `lexer.py`: lazy tokenizer. Token-level failures are raised when the parser reaches them.
  - `parser.py`: Pratt parser. Binding powers follow the projection ranking in FP-04: flatten 9, wildcard 20, filter 21, dot 40, `!` 45, multiselect hash 50, bracket 55.
  - `nodes.py`: expression tree and evaluation. Nothing mutates the input.
  - `functions.py`: `Functions` (the built-in set and the provider base class), `signature`, and built-in dispatch.
  - `runtime.py`: value-model helpers (truthiness, JSON equality, type names), `Options`, `Context`.
  - `exceptions.py`: refusal types.
- `tests/test_pathsel_spec.py`: behavioral tests (104 cases). Run with `python3 -m pytest`.
- `conftest.py` (empty except for a docstring): makes pytest put the project root on `sys.path`, so `import pathsel` works from any working directory.
- `pyproject.toml`: setuptools metadata for the flat layout, zero runtime dependencies, `requires-python >= 3.9`.

Refusal kinds and their carriers (Interface Contract, "Failure carriers"):

| Kind | Type | Carries `lex_position` |
| --- | --- | --- |
| empty expression | `EmptyExpressionError` | no |
| incomplete expression | `IncompleteExpressionError` | yes |
| grammar-level syntax | `SyntaxFailure` | yes |
| token-level syntax | `TokenSyntaxFailure(SyntaxFailure)` | yes |
| zero slice step | `ZeroSliceStepError` | no |
| unknown function | `UnknownFunctionError` | no |
| invalid arity | `InvalidArityError` | no |
| invalid type | `InvalidTypeError` | no |

All of them subclass `PathSelError(ValueError)`.

## Conflicts between the spec files

For each conflict: the two sides, then what was built. Where one side is a more specific rule (a function's own definition, or an explicit "does not succeed" rule), that side was chosen.

### C-01: Bare expression reference (null or non-null)

- Side A: Terminology table, "Expression reference" (line 29): "Outside a function argument it evaluates to null."
- Side B: FP-05 (line 193): "Searching an expression reference on its own succeeds and yields a non-null value..."; Interface Contract, "Expression reference value": "returns a non-`None` value".
- **Built:** non-null. `&expr` evaluates to an `ExpressionReference` object (two of three statements agree). It is not null, so it cannot be mistaken for a missing path.

### C-02: `not_null` on an empty string or array

- Side A: Terminology, "Null" (line 23): "An empty string or an empty array counts as null for `not_null`."
- Side B: FP-07, `not_null` (line 252): "(an empty array or empty string is not null)."
- **Built:** not null. The function's own definition is more specific.

### C-03: Object wildcard on a non-object

- Side A: Terminology, "Projection" (line 32): "An object wildcard applied to a non-object is the empty array."
- Side B: FP-04 (line 159): "An object wildcard on a value that is not an object yields null."
- **Built:** null. It matches the list wildcard and the detailed FP-04 rule.

### C-04: Filter on a non-array

- Side A: FP-04 (lines 161 and 175): "Its left-hand value must be an array; otherwise the result is null." and "A filter on a non-array yields null, not an empty array".
- Side B: FP-06 (line 215): "A filter applied to anything but an array yields the empty array."
- **Built:** null. FP-04 states it twice and FP-06 is a summary.

### C-05: Slice on a non-array

- Side A: FP-03 normal behavior (line 138): "A slice on a value that is not an array yields null."
- Side B: FP-03 boundary behavior (line 148): "A slice of a value that is not an array is the empty array."
- **Built:** null. The boundary line refers back to "as specified above", which is the normal-behavior rule.

### C-06: Slice with step 0

- Side A: FP-03 normal behavior (line 133): "A step of 0 selects nothing: the result is the empty array."
- Side B: FP-03 boundary behavior (line 146): "does not succeed on either entry ... the zero-slice-step kind"; Interface Contract "Failure carriers" lists zero slice step as a refusal.
- **Built:** refusal (`ZeroSliceStepError`), raised at compile time. Because the step is always an integer literal, compile-time refusal means both entries refuse the same texts.

### C-07: Lone `=`

- Side A: Terminology, "Grammar-level syntax failure" (line 37): "A single `=` is a grammar-level failure of this kind."
- Side B: FP-06 (line 219): "A lone `=` is a token-level syntax failure."
- **Built:** token-level (`TokenSyntaxFailure`). `=` begins no token, and FP-06 is the specific rule.

### C-08: `join` of an empty array

- Side A: FP-07 `join` definition (line 242): "the empty array yields the empty string."
- Side B: FP-07 paragraph (line 230): "`join` of an empty array yields null."
- **Built:** empty string, per the function's own definition. The paragraph at line 230 is a general rule about functions with nothing to compute, and it says that such a function "returns the result its definition states".

### C-09: Type of `to_number` output

- Side A: Terminology, "Number" (line 26): "A number made from a string by `to_number` is always a floating-point value."
- Side B: FP-07 `to_number` (line 247): "a string that is an integer numeral becomes that integer".
- **Built:** an integer numeral (`-?[0-9]+`) gives an `int`. Decimal and exponent numerals give a `float`. The function definition is more specific.

### C-10: Unit of string length

- Side A: Terminology, "String" (line 27): "its length is its number of UTF-8 bytes."
- Side B: FP-07 `length` (line 240): "the number of Unicode characters (not bytes)".
- **Built:** Unicode characters (code points, Python `len`). The function definition says so explicitly.

### C-11: Multiselect on a null current value

- Side A: FP-05 (line 187): "On a null current value it still builds one element per expression."
- Side B: FP-05 (line 188): "A multiselect list or hash whose current value is null yields null."
- **Built:** a multiselect list on null builds one element per expression (each element evaluated against null, so usually nulls). A multiselect hash on null yields null. Line 187 is specific to lists, and line 188 covers hashes.

### C-12: Arity of `length`

- Side A: FP-07 built-in list (line 240): `length(string, array or object)` uses two comma-separated slots, the same notation as `contains(array or string, any)`.
- Side B: FP-07 meaning (line 240): "the number of ... of a string, elements of an array, or keys of an object", one value. Line 260: "every other built-in takes exactly the number of arguments listed above".
- **Built:** one argument. The meaning and the usage (`length(@)`, `length(foo)`) both need one, and the two slots are the accepted types of that one argument.

### C-13: Whitespace inside the flatten operator

- Side A: FP-02 (line 110): "Spaces, tabs, line feeds, and carriage returns may appear between any two tokens and do not change meaning."
- Side B: FP-03 (line 140): "The flatten operator is empty square brackets `[]`, written with nothing between them."
- **Built:** `[ ]` is flatten, the same as `[]`. The general whitespace rule applies between the brackets too, because the two brackets are separate tokens.

### C-14: Text ending after a dot

- Side A: FP-01 incomplete expression (line 94): text ending "at a place where an operand expression must still begin" is the incomplete-expression kind.
- Side B: FP-01 syntax (line 95), and FP-02 (line 118): a dot followed by "the end of the text" is a grammar-level syntax failure.
- **Built:** syntax (`SyntaxFailure`). The rule for a dot names the end of the text explicitly. Other places where an operand is missing at the end (after a pipe, comparator, `!`, `&`, or an opening bracket or paren) are incomplete.

## Points the spec does not state (assumptions)

- **Whitespace:** only space, tab, line feed, and carriage return (FP-01). Any other character, including other Unicode whitespace, begins no token (token-level failure).
- **Identifiers:** only ASCII letters, `_`, and digits after the first character.
- **Numbers in the grammar:** `-?[0-9]+` only. A bare number is not an operand, so a top-level `1` is a syntax failure. A lone `-` is a token-level failure.
- **Quoted identifiers:** decoded by `json.loads`, so raw control characters are refused (token-level).
- **Raw strings:** `\'` is a quote. A `\uXXXX` escape is decoded (with surrogate pairs joined). Any other backslash is kept as written.
- **JSON literals:** inside backticks, `` \` `` stands for a backtick. If the text is not JSON, it is read as JSON string content after the leading whitespace is removed. An empty literal gives `""`.
- **Lazy lexing:** tokens are produced as the parser needs them, so when two failures are present the one further left is reported.
- **Expression-level errors:** `foo()` with no arguments parses and fails at search time with invalid-arity. A parenthesized expression is accepted wherever an operand is.
- **Incomplete vs syntax:** end of text where an operand or a closer is still needed is incomplete. Missing operands in the middle of the text are syntax.
- **Zero slice step:** detected while parsing, so compile refuses it and so does search.
- **Comparisons:** `==` and `!=` use JSON equality for every type. The ordering operators give null for any pair that is not two numbers or two strings (the spec does not say what other pairs yield).
- **Host values:** host values that are not JSON types can be selected and returned. A function argument that requires a JSON type refuses them. `type()` gives `object` for them.
- **Type names in `signature`:** the Interface Contract lists five. I also accept `boolean`, `reference` (an expression reference), and `any` (any value). `variadic=True` is a keyword argument that lets the last declared parameter repeat.
- **Built-in precedence:** a provider cannot override a built-in name, so every FP-07 function keeps its behavior.
- **Options:** `dict_cls` applies to constructed multiselect hashes only. `merge` returns a plain `dict`. Object-type checks accept any `collections.abc.Mapping`.
- **Numbers:** `avg` returns a float (true division). `sum([])` is `0`. `ceil` and `floor` return `int`. Host decimals are widened to float only when they meet floats in `avg` and `sum`. Non-finite floats are not special-cased (`ceil(inf)` raises `OverflowError`, which is not a refusal).
- **`to_number`:** no leading `+` and no surrounding whitespace. An integer numeral too large for Python's int conversion gives null.
- **`contains`:** on a string, the second argument must be a string, otherwise invalid-type.
- **`to_string`:** strings are returned unchanged. Other values are compact JSON. Non-ASCII is escaped as `\uXXXX`. Floats use `json.dumps` (the same repr as the host). Decimals use `str`.
- **`max_by` / `min_by`:** the first element wins ties. `sort_by` is stable.
- **Duplicate keys in a multiselect hash:** the later value wins.
- **Limits:** very deep parenthesis or bracket nesting can reach Python's recursion limit and raise `RecursionError`. This is not a `ValueError`. Long dot chains do not recurse (they evaluate as a flat `Chain`).
- **Input is never mutated.** JSON literals are deep-copied on each evaluation, so callers cannot change a parsed expression through a returned value.
