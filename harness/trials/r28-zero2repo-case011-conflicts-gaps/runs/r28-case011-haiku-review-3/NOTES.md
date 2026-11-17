# NOTES — pathsel implementation

Layout: flat package `pathsel/` at the repository root (as in `spec/Interface_Contract.md`, "Layout"),
with `pyproject.toml` for setuptools. Zero runtime dependencies. Python 3.9+ syntax only.

- `pathsel/__init__.py` — `search`, `compile`, error types, `Functions`, `signature`
- `pathsel/parser.py` — tokens → parse tree, projection-reach rules, `compile`, `search`
- `pathsel/lexer.py` — tokenizer (token-level failures)
- `pathsel/nodes.py` — evaluation of the parse tree
- `pathsel/functions.py` — built-in functions, `Functions`, `signature`, call-time lookup
- `pathsel/values.py` — JSON type tests, truthiness, deep equality, expression references, options
- `pathsel/errors.py` — refusal types
- `tests/test_pathsel.py` — behavioral tests (`python -m pytest tests`)

Spec file `spec/CONFLICTS.md` was used only as a checklist; the conflicts below are stated from the
primary spec files (`spec/Full_PRD.md`, `spec/Interface_Contract.md`, `spec/Hardware_Requirements.md`).

---

## Conflicts between the specification files

Each entry: what each side says and where, then what was built.

### C-01 Bare expression reference: null or non-null
- **Side A** — `spec/Full_PRD.md`, Terminology table, row "Expression reference" (line 29): "Outside a function argument it evaluates to null."
- **Side B** — `spec/Full_PRD.md`, FP-05, expression-reference bullet (line 193): "Searching an expression reference on its own succeeds and yields a non-null value…"; `spec/Interface_Contract.md`, "Expression reference value": "returns a non-`None` value".
- **Built:** side B. A bare `&expr` returns an `ExpressionReference` object (non-null). Built-in functions apply it to elements.

### C-02 `not_null` and empty string / empty array
- **Side A** — `Full_PRD.md`, Terminology, row "Null" (line 23): "An empty string or an empty array counts as null for `not_null`."
- **Side B** — `Full_PRD.md`, FP-07, `not_null` (line 252): "(an empty array or empty string is not null)."
- **Built:** side B, because it is the function's own definition. `not_null("", x)` returns `""`.

### C-03 Object wildcard on a non-object
- **Side A** — `Full_PRD.md`, Terminology, row "Projection" (line 32): "An object wildcard applied to a non-object is the empty array."
- **Side B** — `Full_PRD.md`, FP-04, object-wildcard bullet (line 159): "An object wildcard on a value that is not an object yields null."
- **Built:** side B (null), the more specific rule.

### C-04 Filter on a non-array
- **Side A** — `Full_PRD.md`, FP-04 (line 161 and line 175): "…otherwise the result is null." / "A filter on a non-array yields null, not an empty array and not a failure."
- **Side B** — `Full_PRD.md`, FP-06, last normal-behavior bullet (line 215): "A filter applied to anything but an array yields the empty array."
- **Built:** side A (null).

### C-05 Slice on a non-array
- **Side A** — `Full_PRD.md`, FP-03, normal behavior (line 138): "A slice on a value that is not an array yields null."
- **Side B** — `Full_PRD.md`, FP-03, boundary behavior (line 148): "A slice of a value that is not an array is the empty array."
- **Built:** side A (null). Line 148 says "as specified above", which points back to null.

### C-06 Slice with step 0
- **Side A** — `Full_PRD.md`, FP-03, normal behavior (line 133): "A step of 0 selects nothing: the result is the empty array."
- **Side B** — `Full_PRD.md`, FP-03, boundary behavior (line 146): the zero-slice-step kind; `Interface_Contract.md`, "Failure carriers": refused with a `ValueError` subclass.
- **Built:** side B. A zero step is refused when the expression is compiled (`ZeroSliceStepError`), so both entries refuse it regardless of the document.

### C-07 Single `=`
- **Side A** — `Full_PRD.md`, Terminology, row "Grammar-level syntax failure" (line 37): "A single `=` is a grammar-level failure of this kind."
- **Side B** — `Full_PRD.md`, FP-06, boundary behavior (line 219): "A lone `=` is a token-level syntax failure."
- **Built:** side B (token-level, `TokenSyntaxError`).

### C-08 `join` of an empty array
- **Side A** — `Full_PRD.md`, FP-07, `join` definition (line 242): "the empty array yields the empty string."
- **Side B** — `Full_PRD.md`, FP-07, paragraph before the function list (line 230): "`join` of an empty array yields null."
- **Built:** side B (null). It is the explicit statement about this exact call.

### C-09 Type of a number from `to_number`
- **Side A** — `Full_PRD.md`, Terminology, row "Number" (line 26): "A number made from a string by `to_number` is always a floating-point value."
- **Side B** — `Full_PRD.md`, FP-07, `to_number` (line 247): "a string that is an integer numeral becomes that integer".
- **Built:** side B. `"5"` → `int` 5. A decimal or exponent numeral (`"5.5"`, `"1e3"`) → `float`.

### C-10 Unit of string length
- **Side A** — `Full_PRD.md`, Terminology, row "String" (line 27): "its length is its number of UTF-8 bytes."
- **Side B** — `Full_PRD.md`, FP-07, `length` (line 240): "the number of Unicode characters (not bytes) of a string".
- **Built:** side B (code points). `length("héllo")` is 5.

### C-11 Multiselect on a null current value
- **Side A** — `Full_PRD.md`, FP-05, normal behavior (line 187): "On a null current value it still builds one element per expression."
- **Side B** — `Full_PRD.md`, FP-05, normal behavior (line 188): "A multiselect list or hash whose current value is null yields null."
- **Built:** side B for both lists and hashes: null.

### C-12 Arity of `length`
- **Side A** — `Full_PRD.md`, FP-07, built-in list (line 240): `length(string, array or object)` is written with two parameter slots, like `contains(array or string, any)`.
- **Side B** — `Full_PRD.md`, FP-07, line 240 meaning ("…of a string, elements of an array, or keys of an object"), and line 260: "every other built-in takes exactly the number of arguments listed above."
- **Built:** one argument. `string, array or object` is read as the alternatives for a single argument. Any other count is `InvalidArityError`.

### C-13 Whitespace inside `[ ]`
- **Side A** — `Full_PRD.md`, FP-02, normal behavior (line 110): "Spaces, tabs, line feeds, and carriage returns may appear between any two tokens and do not change meaning."
- **Side B** — `Full_PRD.md`, FP-03, normal behavior (line 140): flatten is "empty square brackets `[]`, written with nothing between them."
- **Built:** side A. `[ ]` is flatten, and `[ * ]` is a list wildcard. Whitespace never changes meaning.

### C-14 Text ending after a dot
- **Side A** — `Full_PRD.md`, FP-01, incomplete expression (line 94): text ending "at a place where an operand expression must still begin" is incomplete.
- **Side B** — `Full_PRD.md`, FP-01, syntax (line 95) and FP-02 (line 118): a dot followed by the end of the text, and "a dot at the end", are syntax failures.
- **Built:** side B. `a.` is `PathSelSyntaxError` with position `len(text)`. Other trailing operators (`a |`, `a ==`, `a[`, `foo(`) are incomplete.

---

## Points the specification does not state (assumptions)

**Lexing and parsing**
- All tokens are lexed before parsing. A token-level failure anywhere in the text is reported before a grammar failure earlier in the text.
- A JSON literal ends at the first backtick; there is no backtick escape. Text that is neither JSON nor a valid JSON-string body (after left-trimming) is a token-level failure.
- A raw string decodes `\uXXXX`, and a surrogate pair written as two escapes is combined. Other backslashes are kept literally.
- Bare numbers are valid only inside brackets. A number elsewhere (`abs(1)`) is a grammar-level failure. Use a JSON literal (`abs(\`1\`)`).
- `f()` with no arguments parses; the arity is checked at search time (`not_null()` and `merge()` then raise `InvalidArityError`).
- A function call is an identifier immediately followed by `(` at the start of an operand. After a dot, `a.f(x)` is a syntax failure.
- A comparator chain such as `a < b < c` is accepted and grouped left to right.
- `!` takes the operand plus index/slice/list-wildcard brackets (and the projection right-hand side they start). A following dot, filter or flatten applies to the `!` result. So `!a.b` is `(!a).b`, which is null.
- A `&` expression extends to the end of its enclosing argument, element, parenthesis or whole expression, including `|`.
- A filter predicate is a full expression, including `|`.
- Whitespace between `[` and `]` is insignificant (C-13).

**Projection reach (FP-04)**

These follow the ranks in the spec literally, which gives some results that differ from JMESPath:
- Join ranks of steps: flatten 1, filter 3, dot step (field, multiselect, or `.*`) 4, bracket step (index, slice, `[*]`, multiselect) 5.
- Projection ranks (the threshold its right-hand side must exceed): flatten 1, filter 3, `[*]` and slice 2, `*` at the start of an operand or of a right-hand side 2, `.*` written after a dot 4.
- Consequences: `a.*.b` is per-value `b` (the step directly after a projection always starts its right-hand side), but `a.*.b.c` is null, because `.c` (rank 4) does not outrank `.*` (rank 4). `a[?x].b[?y]` applies `[?y]` to the collected array, because `[?y]` (rank 3) does not outrank the filter (rank 3). `a[*].b[]` applies the flatten to the collected array.
- A slice directly after an index or another slice starts a projection (the implementer's choice allowed by FP-04).

**Evaluation**
- Comparators `<`, `<=`, `>`, `>=` on operands that are not both numbers or both strings yield null.
- `==` and `!=` are JSON equality. `!=` is the negation of `==`.
- Built-in names take precedence over a provider that declares the same name, so a built-in's behavior is unchanged (FP-08, "every FP-07 function remains available").
- The function check order is: name (`UnknownFunctionError`), argument count (`InvalidArityError`), argument evaluation, argument types (`InvalidTypeError`), then the call. The check happens at search time.
- Custom `signature` accepts `number`, `string`, `array`, `object`, `null`, plus `boolean` and `any`. A declared type list is a union.
- Host values: `list` and `tuple` are arrays; `collections.abc.Mapping` instances are objects; `int`, `float` and `decimal.Decimal` (not `bool`) are numbers. Values of `dict_cls` are treated as objects even when that class is not a `Mapping`.
- A host value that is not one of the six JSON types can be selected and returned. It is refused by `type()` and `to_string()` (invalid-type). `to_array()` wraps it in a one-element array, and `to_number()` yields null.
- `avg()` returns a float; `avg([])` and `max([])` / `min([])` / `max_by([])` / `min_by([])` / `join(_, [])` yield null. `sum([])` is 0; `sort([])` and `sort_by([], _)` yield `[]`.
- `ceil`/`floor` return `int`. `to_string` uses compact JSON with `\uXXXX` escapes for non-ASCII, and host number formatting (`Decimal` is written with `str`).
- `merge` returns a plain `dict`, not the `dict_cls` type.
- A multiselect hash uses `dict_cls()` when given, otherwise a `dict`.
- Ties in `max_by` / `min_by` take the first element; `sort_by` is stable.
- `contains(string, x)` requires `x` to be a string (invalid-type otherwise).
- Results from the same expression, document and options through `search` and `compile().search` are identical; both refuse the same texts with the same kinds.

**Errors**
- The kind of a refusal is the type of the raised exception: `EmptyExpressionError`, `IncompleteExpressionError`, `PathSelSyntaxError`, `TokenSyntaxError` (a subclass of `PathSelSyntaxError`), `ZeroSliceStepError`, `UnknownFunctionError`, `InvalidArityError`, `InvalidTypeError`. All subclass `PathSelError`, which subclasses `ValueError`.
- `IncompleteExpressionError` and `PathSelSyntaxError` carry `lex_position`. It is the zero-based offset of the token where the failure was detected. End of text counts as offset `len(text)`. Token-level failures report the start of the bad token.
- Compiling a well-formed expression with an unknown name, a wrong argument count or wrong types succeeds. The refusal happens at search time.

**Packaging**
- `pyproject.toml` declares the flat `pathsel` package for setuptools. No install step is required: running from the repository root puts `pathsel` on the import path.
