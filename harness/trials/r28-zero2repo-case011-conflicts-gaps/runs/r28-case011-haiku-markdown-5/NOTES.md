# NOTES — pathsel implementation

This file records where the specification disagrees with itself, what the
specification leaves unstated, and what the implementation does about each.
Section names refer to `spec/Full_PRD.md` (PRD) and `spec/Interface_Contract.md`
(IC). "Terminology" is the table at the top of the PRD.

Layout built: flat package `pathsel/` at the repository root (IC "Layout";
Hardware "cpu_baseline"), plus `pyproject.toml` (setuptools, zero
dependencies). Tests: `tests/test_pathsel.py` (stdlib `unittest`, run with
`python3 -m unittest discover -s tests` from `/app`).

---

## 1. Conflicts between parts of the specification

### 1.1 Filter applied to a non-array
- PRD FP-04, Normal behavior: "Its left-hand value must be an array; otherwise the result is null."
  and Boundary: "A filter on a non-array yields null, not an empty array and not a failure."
- PRD FP-06, Normal behavior, last bullet: "A filter applied to anything but an array yields the empty array."
- **Built:** `null`. FP-04 is the filter's own section and states the rule
  explicitly, including "not an empty array". Consistent with the general
  "wrong kind yields null" rule.

### 1.2 Slice applied to a non-array
- PRD FP-03, Normal behavior: "A slice on a value that is not an array yields null."
- PRD FP-03, Boundary: "A slice of a value that is not an array is the empty array."
- **Built:** `null`. This matches the Normal-behavior bullet and the "wrong kind yields null" rule in Terminology.

### 1.3 Object wildcard applied to a non-object
- PRD Terminology, "Projection": "An object wildcard applied to a non-object is the empty array."
- PRD FP-04, Normal behavior: "An object wildcard on a value that is not an object yields null."
- **Built:** `null` (the FP-04 rule). The list wildcard in FP-04 also yields null for a non-array.

### 1.4 Length of a string: bytes or characters
- PRD Terminology, "String": "its length is its number of UTF-8 bytes."
- PRD FP-07, `length`: "the number of Unicode characters (not bytes) of a string".
- **Built:** `length()` counts Unicode code points (`len(str)`). No other operation in the spec observes a string's length, so the byte statement has no other effect.

### 1.5 Expression reference searched on its own
- PRD Terminology, "Expression reference": "Outside a function argument it evaluates to null."
- PRD FP-05: "Searching an expression reference on its own succeeds and yields a non-null value that is neither the document nor the result of evaluating the referenced expression."
- IC `pathsel.search` / "Expression reference value": "Searching an expression that is a bare expression reference returns a non-`None` value of the implementer's choice."
- **Built:** a non-null object of the internal class `pathsel._ast.ExpressionReference` (not exported from the package root). Two of the three statements say non-null.

### 1.6 Multiselect on a null current value
- PRD FP-05, bullet 2 (multiselect list): "On a null current value it still builds one element per expression."
- PRD FP-05, bullet 3: "A multiselect list or hash whose current value is null yields null."
- **Built:** the two are split. A multiselect **list** on a null current value builds one element per expression (the list-specific sentence is the more specific rule). A multiselect **hash** on a null current value yields null. For example `n.[a, b]` gives `[null, null]` and `n.{a: a}` gives `null`.

### 1.7 `not_null` and empty values
- PRD Terminology, "Null": "An empty string or an empty array counts as null for `not_null`."
- PRD FP-07, `not_null`: "(an empty array or empty string is not null)".
- **Built:** an empty string or empty array is **not** null, so `not_null` returns it. FP-07 is the function's definition and the Terminology sentence contradicts it.

### 1.8 `join` of an empty array
- PRD FP-07, `join`: "the empty array yields the empty string."
- PRD FP-07, paragraph before the normal-behavior list: "`join` of an empty array yields null."
- **Built:** the empty string, from the function's own definition. The paragraph sentence is the one that disagrees with it. This is a judgment call; the other reading is a one-line change in `functions.py` (`_func_join`).

### 1.9 `to_number` on integer numerals
- PRD Terminology, "Number": "A number made from a string by `to_number` is always a floating-point value."
- PRD FP-07, `to_number`: "a string that is an integer numeral becomes that integer, otherwise ... becomes that floating-point number".
- **Built:** an integer numeral (for example `"42"`) gives a Python `int`; a decimal or exponent numeral (`"4.5"`, `"1e3"`) gives a `float`. `to_number("42") == 42` is true under either reading.

### 1.10 Raw string literals and escapes
- PRD FP-05, raw string literal: "No JSON escapes are processed. The pair backslash-quote stands for a single quote."
- PRD FP-05, boundary: "A `\uXXXX` escape inside a raw string literal is decoded to its character."
- **Built:** in a raw string, `\'` becomes `'`, `\uXXXX` (with surrogate pairs) becomes its character, and every other backslash is kept literally (so `'a\nb'` is the 4-character string `a\nb`).

### 1.11 Projection-reach placements that the spec leaves to the implementer
These are not conflicts; FP-04 says they are implementer's choice. Built as follows:
- A slice written directly after an index **starts a projection**: `arr[0][1:2]` is a projection of the slice over the index result.
- A right-hand side that starts with a dot followed by a multiselect list or hash **lets later steps join it**: `a[*].[x, y][0]` applies `[0]` to each constructed list.

---

## 2. Things the specification does not state (and what was assumed)

### 2.1 Lexing
- Whitespace (space, tab, LF, CR) is allowed between any two tokens, including between `[` and `]`. So `[ ]` is the flatten operator, the same as `[]`. The spec says "written with nothing between them" for flatten, but also says spaces "may appear between any two tokens and do not change meaning." The second rule was followed.
- Identifiers and digits are ASCII only. Any other character begins no token (token-level failure).
- A number token is an optional leading `-` directly followed by ASCII digits. `+` is not a number sign. Leading zeros are accepted (`007` is 7).
- A hyphen not followed by a digit begins no token (token-level failure), as FP-02 states.
- Quoted identifiers are JSON string literals; raw control characters inside them are a token-level failure because JSON rejects them.
- Backtick JSON literals: the only escape handled by the lexer is backslash-backtick, which yields a literal backtick. Otherwise the text is passed to `json.loads` as-is. If that fails, the text is read as JSON-string content after removing leading whitespace (`json.loads('"' + text.lstrip() + '"')`); if that also fails it is a token-level failure. An empty literal is the empty string.

### 2.2 Parsing
- Tokens are read lazily, one at a time, so the first failure in text order is the one reported. A token-level failure later in the text does not pre-empt an earlier grammar failure.
- `Empty` is returned only for the zero-length text. Whitespace-only text is `Incomplete` (FP-01 says so explicitly).
- End of text where an operand or a closer is still required is `Incomplete`. End of text directly after a dot is `Syntax` (FP-01 lists "the end of the text" among the dot failures).
- A function call is an unquoted identifier followed by `(`. `()` with no arguments parses; the arity is checked when the call is evaluated. A dot-step identifier is never a function call: `a.length(x)` is a grammar-level syntax failure.
- A number cannot be an operand on its own. `1`, `[1, 2]` and `{a: 1}` are grammar-level syntax failures, because only literals, identifiers and the other operands of FP-05 are expressions.
- Zero slice step (`[::0]`) is refused at compile time, which FP-03 allows ("either the compile or the later search refuses").
- `[` followed by a number or colon is always an index or slice. `[` followed by `*]` is a list wildcard. `[` followed by `]` is flatten. `[` followed by `?` is a filter. Any other `[` at an operand's start is a multiselect list. After an operand, a bracket with other content is a grammar-level syntax failure.
- The projection rule implemented: a projection's right-hand side takes a step when that step's binding power is greater than the projection's (flatten 9, wildcard 20, filter 21, dot 40, index/slice/`[*]` 55), with the first step always taken if it is a dot, index, slice, wildcard, multiselect or filter step.

### 2.3 Evaluation
- Comparing values that are not both numbers or both strings with `<`, `<=`, `>`, `>=` yields `null`. The spec does not say what a non-comparable ordering gives.
- `==` between host (non-JSON) values falls back to Python `==`. Two host values of different kinds are unequal.
- `decimal.Decimal` counts as a number for comparisons and for `to_number` (returned unchanged), but not as a JSON number for built-in arguments, which refuse it as invalid-type (FP-07 says built-ins refuse non-JSON host values).
- Arrays are `list` and `tuple`; objects are any `collections.abc.Mapping`; any other host value is "host": it can be selected and returned, is truthy, and is refused by built-in arguments.
- Booleans are checked before numbers everywhere, so `True` is never a number.
- Projections, slices, flatten and filters all drop null results, including the identity projection of a slice (so `arr[::-1]` drops the null in `arr`).
- Literal values are deep-copied on each evaluation so that a caller mutating a result cannot change the parsed expression.
- Search results may share objects with the input document (selection returns the stored value). Evaluation never writes to the input.
- `search` returns a Python value; a bare expression reference returns an `ExpressionReference` object.

### 2.4 Function calls
- Check order: name first, then argument count, then each argument's value is evaluated left to right, then each argument's type is checked. Element-type checks of array arguments happen inside the function body before it returns anything. Compile does not check names, counts or types.
- Name lookup: built-ins win over a provider's function with the same name, so every built-in keeps its behavior on a search that uses a provider.
- `type()` on a non-JSON host value reports `"object"` (a `Decimal` reports `"number"`).
- `to_string` writes compact JSON with `ensure_ascii` (so non-ASCII becomes `\uXXXX`), `default=str` for values JSON cannot encode, and a `Decimal` as its `str()`.
- `to_number` accepts only the exact numeral forms: an optional `-`, then digits, or a decimal or exponent form. No leading or trailing whitespace, no `+`.
- `merge` returns a plain `dict`. `dict_cls` (FP-08) applies only to multiselect hashes, as FP-08 specifies.
- `keys`/`values`/`length`/`contains` on a `Mapping` use its own iteration order.
- `avg` returns a float. `sum` of an empty array is `0`. `avg`, `max`, `min`, `max_by`, `min_by` of an empty array are `null` (`sort` and `sort_by` of an empty array are `[]`).
- `sort_by` is stable. `max_by` and `min_by` return the first element on ties.
- Mixed key types for `sort_by`/`max_by`/`min_by` (or a key that is neither a number nor a string) are invalid-type. An empty array has no keys, so it is never invalid-type.
- `ceil`/`floor` use Python `math`; an infinite float raises `OverflowError`, which is not one of the refusal kinds. JSON input cannot produce infinity, so this only happens with host values.
- Custom functions: an attribute named `_func_<name>` whose value went through `signature` defines `<name>`. Types `any` and `boolean` are accepted by `signature` in addition to the five listed in IC (the built-ins need `any` and `reference`). Providers are scanned with `dir()` on every search; nothing is cached across searches.

### 2.5 Options
- `options` may be `None` or any object. A missing `dict_cls` or `custom_functions` attribute is treated as `None`.
- `dict_cls` is called with no arguments and filled by item assignment (IC).

### 2.6 Failure carriers
- The failure types are `EmptyExpressionError`, `IncompleteExpressionError`, `SyntaxFailure`, `TokenSyntaxFailure(SyntaxFailure)`, `ZeroSliceStepError`, `UnknownFunctionError`, `InvalidArityError`, `InvalidTypeError`. All derive from `pathsel.errors.PathSelError`, which derives from `ValueError`. The names are the implementer's choice (IC).
- `lex_position` is an `int` on syntax and incomplete failures. It is the offset of the token where the expression went wrong; the end of text is `len(text)`.
- Messages are informational (PRD, Non-functional constraints).

### 2.7 Packaging
- The import name is `pathsel`; the distribution name is `pathsel`, version `1.0.0`, `requires-python >=3.9`, no dependencies. The package is found at the repository root.
- No command-line program, no `python -m` entry, no config file (IC).
- Importing `pathsel` or `pathsel.functions` does no I/O and starts nothing.

### 2.8 Verification
- `tests/test_pathsel.py` encodes the rules above (58 tests, all passing on the interpreter installed here, Python 3.13). The code is written to run on Python 3.9 too: it uses no `match`, no `X | Y` type unions, no walrus, and no newer library functions. I did not run it on 3.9 because no 3.9 interpreter is installed here.
