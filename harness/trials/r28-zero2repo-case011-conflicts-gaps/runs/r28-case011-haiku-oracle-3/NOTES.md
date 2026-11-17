# NOTES

Implementation notes for `pathsel` (built from `spec/`). Spec files are under `spec/packs/`;
pack file names are given as `pack NN`. Ids are the `N-…` claim ids from `spec/CHECKLIST.md`.
Status of every checklist id is in `TRACEABILITY.md`.

## 1. Spec conflicts and what was built

Eleven contradictions are marked UNSETTLED in `spec/MAP.md` (no human verdict). Four more
disagreements were found while reading the packs; they are listed after them. For each one I
chose the side the spec states most specifically for the behaviour in question, and the other
side is not implemented.

### 1.1 UNSETTLED contradictions (CF-…)

**CF-000005 — filter on a non-array.**
- pack 09 (FP-04, Boundary), N-000202: "A filter on a non-array yields null, not an empty array and not a failure."
- pack 11 (FP-06, Normal), N-000259: "A filter applied to anything but an array yields the empty array."
- **Built:** null (FP-04 is the feature point that owns filters and names the rule explicitly).

**CF-000007 — slice on a value that is not an array.**
- pack 08 (FP-03, Normal), N-000142: "A slice on a value that is not an array yields null."
- pack 08 (FP-03, Boundary), N-000157: "A slice of a value that is not an array is the empty array."
- **Built:** null (matches the normal-behaviour rule and the rule for indexing a non-array).

**CF-000011 — multiselect list/hash with a null current value.**
- pack 10 (FP-05, Normal), N-000212: "On a null current value it still builds one element per expression."
- pack 10 (FP-05, Normal), N-000218: "A multiselect list or hash whose current value is null yields null."
- **Built:** null for both list and hash (N-000218). A null current value therefore never reaches the element expressions.

**CF-000015 — `not_null` and empty values.**
- pack 02 (Terminology, Null row), N-000022: "An empty string or an empty array counts as null for `not_null`."
- pack 12 (FP-07, `not_null`), N-000300: "(an empty array or empty string is not null)".
- **Built:** empty string and empty array are *not* null for `not_null` (the function's own definition, N-000300).

**CF-000027 — object wildcard on a non-object.**
- pack 02 (Terminology, Projection row), N-000031: "An object wildcard applied to a non-object is the empty array."
- pack 09 (FP-04, Normal), N-000165: "An object wildcard on a value that is not an object yields null."
- **Built:** null (N-000165).

**CF-000035 — length of a string.**
- pack 02 (Terminology, String row), N-000026: "its length is its number of UTF-8 bytes".
- pack 12 (FP-07, `length`), N-000277: "the number of Unicode characters (not bytes) of a string".
- **Built:** number of Unicode code points (Python `len`), per N-000277. `length('héllo')` is 5.

**CF-000049 — escapes in raw string literals.**
- pack 10 (FP-05, Normal), N-000227: "No JSON escapes are processed."
- pack 10 (FP-05, Boundary), N-000239: "A `\uXXXX` escape inside a raw string literal is decoded to its character."
- **Built:** only `\uXXXX` (exactly four hex digits) is decoded, and backslash-quote is a single quote (both explicit in the spec). Every other backslash stays as written, so `'a\nb'` is the four characters `a`, `\`, `n`, `b`.

**CF-000054 — `join` of an empty array.**
- pack 12 (FP-07, preamble), N-000268: "`join` of an empty array yields null."
- pack 12 (FP-07, `join` bullet), N-000280: "the empty array yields the empty string."
- **Built:** null (the preamble names `join` explicitly as the example).

**CF-000055 — slice with step 0.**
- pack 08 (FP-03, Normal), N-000133: "A step of 0 selects nothing: the result is the empty array."
- pack 08 (FP-03, Boundary), N-000152: "A slice whose step is 0 does not succeed on either entry … zero-slice-step kind."
- **Built:** refusal (zero-slice-step kind). It is raised when the expression is compiled, so it is refused by both entries.

**CF-000056 — bare expression reference.**
- pack 02 (Terminology, Expression reference row), N-000028: "Outside a function argument it evaluates to null."
- pack 10 (FP-05, Normal), N-000234 and pack 25 (Interface), N-000423: a non-null value is returned.
- **Built:** a non-null value: an `ExpressionReference` object wrapping the referenced expression. The interface contract (N-000423) also requires a non-`None` result, so that side is kept.

**CF-000057 — `to_number`.**
- pack 02 (Terminology, Number row), N-000023: "A number made from a string by `to_number` is always a floating-point value."
- pack 12 (FP-07, `to_number`), N-000287: "a string that is an integer numeral becomes that integer".
- **Built:** an integer numeral (`-?[0-9]+`) gives an `int`; a decimal or exponent numeral gives a `float`. So `to_number('42')` is `42`.

### 1.2 Disagreements not in the UNSETTLED list

**Lone `=`.**
- pack 11 (FP-06, Boundary), N-000260: "A lone `=` is a token-level syntax failure."
- pack 02 (Terminology, "Grammar-level syntax failure" row, no id): "A single `=` is a grammar-level failure of this kind."
- **Built:** token-level (`TokenSyntaxFailure`, a subclass of `SyntaxFailure`). Both are the syntax kind; only the subclass differs.

**Function call as a projection right-hand side vs. identifiers after a projection.**
- pack 12 (FP-07, Normal), N-000309: "A function call may be the right-hand side of a projection (applied to each element, dropping nulls)."
- pack 09 (FP-04, Boundary), N-000200: "A wildcard followed directly by an identifier … is a grammar-level syntax failure."
- **Built:** `ident(` directly after a projection form is a function-call right-hand side (`xs[*]length(@)`). A plain identifier directly after a projection form is still a syntax failure (`items[*]n`).

**Filter-step and flatten-step ranking.**
- pack 09 (FP-04, Reach of a projection), N-000185–N-000190: the ranking (flatten loosest, then wildcard/slice, filter, dot, index-like bracket).
- The spec ranks flatten and filter; it does not say how a bracket that *begins* a flatten or filter step is ranked after a projection.
- **Built:** `[]` after a projection is a flatten step (rank 1, does not join the right-hand side); `[?` is a filter step (rank 3); other brackets are rank 5. This is what the ranking gives.

## 2. Choices the spec left open

These are the implementer's choices named in the spec, and the choice made.

- **Slice starts a projection** (N-000198): a slice is always a projection, including directly after an index.
- **Dot followed by multiselect list or hash** (N-000199): later steps join the right-hand side (`items[*].{a: n}[0]` applies `[0]` to each constructed hash).
- **Type names** (N-000407) and **failure report text** (N-000408): exception types are `EmptyExpressionError`, `IncompleteExpressionError`, `SyntaxFailure`, `TokenSyntaxFailure`, `ZeroSliceStepError`, `UnknownFunctionError`, `InvalidArityError`, `InvalidTypeError`, all subclasses of `PathSelError(ValueError)`.
- **Options class** (N-000392): no options class is published; any object with `dict_cls` and `custom_functions` attributes is accepted.
- **Parsed-expression type** (N-000384): `pathsel.ParsedExpression`.
- **Mapping types accepted as objects** (N-000330 / pack 13): any `collections.abc.Mapping`, including `OrderedDict`.
- **Built-in names win over provider names.** A provider that declares a function with a built-in name does not change that built-in (N-000340).

## 3. Things the spec does not state (what I assumed)

Where I looked: all 25 packs, including the "Related elsewhere" and "Conflicts" sections.

**Lexing and grammar**
- Whitespace is space, tab, LF and CR only (N-000109). Any other character that begins no token is a token-level failure.
- Numbers are integers only, with an optional leading `-` and no `+`. A number is valid only inside brackets, as an index or slice part. A number elsewhere (for example a function argument such as `abs(1)`) is a grammar-level failure.
- Identifiers are ASCII (`[A-Za-z_][A-Za-z0-9_]*`). Any non-ASCII character outside a quoted identifier, literal or raw string is a token-level failure.
- Inside a JSON literal, `` \` `` is read as a backtick (the spec does not say how to write a backtick there).
- `:` and `?` are tokens. `?` only has meaning after `[`.
- `foo.[*]`, `foo.[0]` and `foo.(…)` are syntax failures (a dot may be followed only by an identifier, a quoted identifier, `*`, a multiselect list, or a multiselect hash).
- A function call after a dot (`a.length(@)`) is a syntax failure: a function call is an operand, not a field step.
- An empty argument list is allowed syntactically (`abs()`); it is an invalid-arity refusal when evaluated.
- A multiselect hash directly after a projection form (`items[*]{a: n}`) is a syntax failure; it needs a dot (`items[*].{a: n}`), per N-000213–N-000218.
- `(` after a projection form is a syntax failure.
- A lone `&` at end of text is an incomplete expression; `&` followed by a non-expression token is a syntax failure.
- A pipe with no left operand (`| a`) is a syntax failure; a pipe with no right operand (`a |`) is an incomplete expression.

**Positions**
- `lex_position` is the zero-based character offset of the token where the failure was detected (N-000102). For end of text it is the length of the text, including trailing whitespace.
- Failures reported by the lexer use the offset of the bad token's first character.

**Evaluation**
- Built-in functions are checked when the call is evaluated, not when compiled. A call that is never evaluated (for example after a short-circuit `&&` or `||`, or inside a projection over an empty array) is never refused.
- Name, then argument count, then argument types. Arguments are evaluated before the type check. A nested refusal inside an argument wins over this call's type check.
- Comparisons `<`, `<=`, `>`, `>=` on mismatched kinds (for example number and string, or boolean) yield null. The spec only defines numbers and strings.
- `==`/`!=` between two expression references compare by identity.
- `&&` and `||` evaluate the right-hand side only when needed.
- Literal values are deep-copied on each evaluation, so mutating a result cannot change a later result.
- Selected values are returned as the same Python objects as the input (no copy). The library never writes to the input.
- Returning an `ExpressionReference` as a top-level result is allowed (CF-000056).

**Built-in function details**
- `sum([])` is `0`. `avg([])` is null (N-000270).
- `ceil` and `floor` return `int`; `abs` returns the same numeric type as its argument.
- `avg` returns a `float` (true division).
- `to_number`: integer numerals are `-?[0-9]+`; decimal numerals are `-?(digits.digits* | .digits | digits)(e[+-]?digits)?`, with no surrounding whitespace.
- `to_string`: compact JSON, `ensure_ascii` escapes; floats use `json.dumps` (host `repr`); a `Decimal` uses its `str()`; a non-JSON host value is written as a JSON string of `str(value)`.
- `type` returns `null` for host values that are neither a number, string, boolean, array, object nor null (the spec lists only six type names).
- `to_array(null)` is `[null]`.
- `merge` returns a plain `dict`; `dict_cls` applies only to multiselect hashes.
- `max`, `min`, `sort` and `sort_by`/`max_by`/`min_by` accept numbers mixed with `Decimal`/`float`.
- `max_by`/`min_by` keep the first element among equal keys; `sort_by` is stable.
- `contains(string, x)` with a non-string `x` is invalid-type.
- A `Decimal` is a number everywhere (N-000056). A `bool` is never a number.
- Tuples are treated as arrays and any `collections.abc.Mapping` as an object.

**Custom functions (FP-08, pack 23)**
- `signature` takes mappings `{"types": [...]}`; each mapping is a union of type names. Type names used by the built-ins (`any`, `expref`, `array_of_numbers`, `array_of_strings`, `array_of_numbers_or_strings`) are internal; custom providers may use `number`, `string`, `array`, `object`, `null` (and `any`).
- A `signature` with no arguments declares a zero-argument function.
- A provider is instantiated by the caller; `Functions()` itself has no constructor arguments.
- `custom_functions` is read with `getattr`, so a provider that is not a `Functions` subclass but defines `_func_*` methods decorated with `signature` also works.

**Packaging and layout**
- The flat package is `/app/pathsel` (pack 18). `pyproject.toml` declares distribution name `pathsel`, setuptools build backend, no runtime dependencies (packs 16 and 18).
- No command-line entry, no `python -m` entry, no configuration file (pack 17).
- Python 3.9 is the floor (pack 04). The sources parse under the 3.9 grammar (`ast.parse(..., feature_version=(3, 9))`). No Python 3.9 interpreter is installed here, so the suite was run on 3.13 (pytest) and on 3.11 (the test functions called directly, because pytest is not installed for 3.11).

**Tests**
- No acceptance-criteria labels exist (`AC labels: none` in every pack), so tests are named after the behaviour and carry spec ids in their names where the id is the closest match.
- Tests live in `tests/test_pathsel.py` and run with `python3 -m pytest tests`.
