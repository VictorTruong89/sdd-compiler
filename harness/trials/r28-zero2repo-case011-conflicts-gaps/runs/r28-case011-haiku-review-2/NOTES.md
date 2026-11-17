# NOTES

Implementation of pathsel (PathSel) as the flat-layout package `pathsel/` at the repository root.
Entry points: `pathsel.search(expression, data, options=None)` and `pathsel.compile(expression)`
returning a parsed expression with `.search(value, options=None)`. Provider base class and
`signature` decorator are in `pathsel.functions`.

Files:

- `pathsel/errors.py` — refusal classes (all `ValueError`; syntax and incomplete carry `lex_position`).
- `pathsel/values.py` — JSON type tests, truthiness, JSON equality, `ExpressionReference`.
- `pathsel/functions.py` — `Functions` (built-ins as `_func_<name>`), `signature`, provider lookup.
- `pathsel/lexer.py` — tokenizer; token-level failures become error tokens, raised in text order.
- `pathsel/parser.py` — Pratt parser; binding powers encode the FP-04 projection ranks.
- `pathsel/nodes.py` — expression nodes and their evaluation.
- `tests/test_pathsel.py` — behavior tests (`python3 -m pytest tests`).
- `conftest.py` — empty; keeps the project root on `sys.path` for pytest.
- `pyproject.toml` — setuptools metadata, distribution name `pathsel`, zero dependencies.

## Conflicts between the specification files

Each entry gives both sides with their location, then what was built. Where a side was chosen,
the other side is the one that is not implemented.

**C-01 Bare expression reference.** `Full_PRD.md` Terminology, "Expression reference" row (line 29):
"Outside a function argument it evaluates to null." versus `Full_PRD.md` FP-05 (line 193):
"Searching an expression reference on its own succeeds and yields a non-null value", and
`Interface_Contract.md` "Expression reference value": "returns a non-`None` value".
*Built:* non-null. A bare `&expr` returns an `ExpressionReference` object.

**C-02 `not_null` and empty values.** `Full_PRD.md` Terminology, "Null" row (line 23):
"An empty string or an empty array counts as null for `not_null`." versus FP-07 `not_null`
(line 252): "(an empty array or empty string is not null)."
*Built:* the FP-07 rule. `not_null` returns the first argument that is not `null`; `""` and `[]` count as values.

**C-03 Object wildcard on a non-object.** Terminology, "Projection" row (line 32): "An object
wildcard applied to a non-object is the empty array." versus FP-04 object wildcard (line 159):
"yields null."
*Built:* null.

**C-04 Filter on a non-array.** FP-04 (lines 161 and 175): "otherwise the result is null" and
"not an empty array and not a failure", versus FP-06 (line 215): "A filter applied to anything but
an array yields the empty array."
*Built:* null.

**C-05 Slice on a non-array.** FP-03 normal behavior (line 138): "yields null." versus FP-03
boundary (line 148): "A slice of a value that is not an array is the empty array."
*Built:* null.

**C-06 Slice with step 0.** FP-03 normal behavior (line 133): "A step of 0 selects nothing: the result
is the empty array." versus FP-03 boundary (line 146): refused as the zero-slice-step kind, and
`Interface_Contract.md` Failure carriers.
*Built:* refusal (`ZeroSliceStepError`). The check runs at evaluation time, before the input is
type-tested, so a zero step is refused even when the input is not an array.

**C-07 Lone `=`.** Terminology, "Grammar-level syntax failure" row (line 37): "A single `=` is a
grammar-level failure of this kind." versus FP-06 boundary (line 219): "A lone `=` is a token-level
syntax failure."
*Built:* token-level (`TokenSyntaxError`), because the lexer is where the character is rejected.
Both are syntax kinds, so only the subclass differs.

**C-08 `join` of an empty array.** FP-07 `join` definition (line 242): "the empty array yields the
empty string." versus FP-07 paragraph (line 230): "`join` of an empty array yields null."
*Built:* the empty string (the per-function definition).

**C-09 Type of a number from `to_number`.** Terminology, "Number" row (line 26): "A number made from a
string by `to_number` is always a floating-point value." versus FP-07 `to_number` (line 247): "a
string that is an integer numeral becomes that integer."
*Built:* integer numerals become `int`; decimal and exponent numerals become `float`. (`5 == 5.0`
in Python, so only the type differs.)

**C-10 Unit of string length.** Terminology, "String" row (line 27): "its length is its number of
UTF-8 bytes." versus FP-07 `length` (line 240): "the number of Unicode characters (not bytes)."
*Built:* characters, per the function definition. The `length` built-in is the only place length is
computed.

**C-11 Multiselect list or hash on a null current value.** FP-05 normal behavior (line 187): "On a
null current value it still builds one element per expression." versus FP-05 (line 188): "whose
current value is null yields null."
*Built:* null (the second statement). The first is not implemented.

**C-12 Arity of `length`.** FP-07 list (line 240) writes `length(string, array or object)` with two
parameter slots, while the meaning says one value, and line 260 says every other built-in takes
exactly the listed number.
*Built:* one argument, of type string, array, or object.

**C-13 Whitespace inside the flatten operator.** FP-02 (line 110): whitespace "may appear between any
two tokens and do not change meaning." versus FP-03 (line 140): flatten is `[]` "with nothing between
them."
*Built:* `[ ]` (with whitespace) is flatten, because `[` and `]` are tokens and whitespace between tokens
does not change meaning. The same applies to `[ ?` as a filter.

**C-14 Text ending after a dot.** FP-01 (line 94): text ending "at a place where an operand expression
must still begin" is incomplete; FP-01 (line 95) and FP-02 (line 118): a dot followed by the end of
the text is grammar-level syntax.
*Built:* syntax (`PathSelSyntaxError`, position = end of text). Other places where input ends while an
operand or a closing bracket is still needed (`foo |`, `foo[0`, `foo ==`, `&`) are incomplete.

## Assumptions where the specification is silent

- **Comparison of incomparable values.** `<`, `<=`, `>`, `>=` between values that are not both numbers
  (booleans excluded) or both strings return null. Host `Decimal` values count as numbers.
- **Object, array, and number detection.** An object is any `Mapping`, or any value with `keys()` and
  item access (so a caller's `dict_cls` works). An array is a `list` or `tuple`. A number is `int` or
  `float` and never a boolean (strict for function arguments; `Decimal` only counts in comparisons).
- **Function lookup order.** Built-in names resolve to the built-in implementation before the provider.
  A provider cannot change built-in behavior. Provider attributes count only if decorated with `signature`.
- **Zero-argument calls.** `f()` is an invalid-arity refusal at search time, not a syntax refusal.
- **Calls after a dot.** `foo.length(@)` is accepted: the call's `@` is the subexpression's current value.
- **Variadic built-ins.** `merge` and `not_null` take one or more arguments.
- **`merge` result type.** Always a plain `dict`; `dict_cls` applies only to multiselect hashes.
- **`type()` of a host value that is not a JSON type.** Returns null.
- **`avg`** returns a float; **`sum([])`** is `0`; **`max`/`min`/`sort`** accept only all-number or
  all-string arrays (an empty array passes).
- **`to_number`** accepts no whitespace and no leading `+`. A leading `-` is allowed.
- **`to_string`** writes compact JSON with ASCII-only `\uXXXX` escapes; numbers use Python's repr form;
  a `Decimal` is written unquoted; a `str` is returned unchanged.
- **Raw string literals.** Only `\'` and `\uXXXX` are escapes; any other backslash is kept.
- **JSON literals.** `` \` `` inside a literal is a backtick. If the text is not JSON, it is wrapped as
  JSON string content after leading whitespace is removed.
- **Quoted identifiers.** Decoded with strict JSON, so a raw control character inside the quotes is a
  token-level refusal; a control character must be written as an escape.
- **Negative numbers.** `-` followed by digits is one number token; `-` with no digit after it is a
  token-level refusal.
- **Expression reference scope.** `&` extends to the end of the enclosing argument, element, parenthesis,
  or expression, including pipes.
- **Nested projections.** A slice written after an index starts a projection (the spec leaves this
  open). A multiselect list is allowed as the first step of a projection's right-hand side only.
- **Top-level forms.** `*`, `[*]`, `[]`, `[n]`, `[a:b]`, and `[?...]` at the start of an expression
  apply to the document itself.
- **Failure order.** The first failure in text order is reported. A token-level failure is raised when
  the parser reaches it.
- **Positions.** A syntax failure reports the start of the token where it was detected (for a token
  error, where the bad token begins). End of text is `len(text)`.
- **Non-string expression.** `compile` and `search` raise `TypeError`. This is not a refusal in the
  PathSel sense.
- **Non-finite numbers.** `ceil` and `floor` on `inf` or `NaN` raise Python's `OverflowError` or
  `ValueError`. The spec does not say how these should be refused; this is left as is.
- **Packaging.** No install step is required by the judge. `pyproject.toml` declares a setuptools
  build, and `conftest.py` makes the flat package importable under pytest.
