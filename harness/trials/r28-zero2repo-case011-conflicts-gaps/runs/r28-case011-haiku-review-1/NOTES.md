# NOTES

Implementation notes for `pathsel` (the library in `/app/pathsel/`). Each
conflict from `spec/CONFLICTS.md` is listed below, with both sides, and then the
choice I built. Items the spec does not state follow the conflicts.

Layout: `pathsel/__init__.py` (exports), `api.py` (`search`, `compile`,
`ParsedExpression`, `Options`), `lexer.py`, `parser.py`, `nodes.py` (evaluation),
`values.py` (truthiness and JSON equality), `functions.py` (`Functions`,
`signature`, built-ins), `exceptions.py`. Tests: `tests/test_pathsel.py`
(run `python3 tests/test_pathsel.py`).

## Conflicts

Locations: `PRD` = `spec/Full_PRD.md`, `IC` = `spec/Interface_Contract.md`.

### C-01 Bare expression reference: null or non-null
- Side A, PRD Terminology "Expression reference": "Outside a function argument it evaluates to null."
- Side B, PRD FP-05 (line 193) and IC "Expression reference value": non-null value.
- **Built:** non-null. A bare `&expr` returns an `ExpressionReference` object (the referenced node and its context). It is neither the document nor the result of the expression. Two sources (FP-05 and IC) agree on this.

### C-02 `not_null` and empty string / array
- Side A, PRD Terminology "Null": an empty string or empty array counts as null for `not_null`.
- Side B, PRD FP-07 `not_null` (line 252): "an empty array or empty string is not null".
- **Built:** not null. `not_null("")` returns `""`. This is the definition of the function itself.

### C-03 Object wildcard on a non-object
- Side A, PRD Terminology "Projection": "An object wildcard applied to a non-object is the empty array."
- Side B, PRD FP-04 (line 159): "yields null".
- **Built:** null. FP-04 defines the object wildcard specifically.

### C-04 Filter on a non-array
- Side A, PRD FP-04 (lines 161, 175): null, "not an empty array and not a failure".
- Side B, PRD FP-06 (line 215): "yields the empty array".
- **Built:** null. FP-04 says so twice.

### C-05 Slice on a non-array
- Side A, PRD FP-03 normal behaviour (line 138): null.
- Side B, PRD FP-03 boundary (line 148): "the empty array".
- **Built:** null, consistent with C-03 and C-04.

### C-06 Slice with step 0
- Side A, PRD FP-03 (line 133): "A step of 0 selects nothing: the result is the empty array."
- Side B, PRD FP-03 (line 146) and IC failure carriers: refused with the zero-slice-step kind.
- **Built:** refused. `ZeroSliceStepError` is raised when the expression is compiled, so both `search` and `compile` refuse it.

### C-07 Single `=`
- Side A, PRD Terminology: "A single `=` is a grammar-level failure".
- Side B, PRD FP-06 (line 219): "A lone `=` is a token-level syntax failure".
- **Built:** token-level (`TokenSyntaxFailure`, a subclass of `SyntaxFailure`). The FP-06 rule is the more specific one. Both sides are the syntax family, so a caller that catches `SyntaxFailure` handles it.

### C-08 `join` of an empty array
- Side A, PRD FP-07 `join` definition (line 242): "the empty array yields the empty string."
- Side B, PRD FP-07 paragraph before the list (line 230): "`join` of an empty array yields null."
- **Built:** `""`. This is the definition of `join`.

### C-09 Type of a number from `to_number`
- Side A, PRD Terminology "Number" (line 26): always floating-point.
- Side B, PRD FP-07 `to_number` (line 247): "a string that is an integer numeral becomes that integer."
- **Built:** `to_number("5")` is `int` 5. Decimal and exponent numerals become `float`. The two sides only differ by type, and `5 == 5.0`.

### C-10 Length of a string
- Side A, PRD Terminology "String" (line 27): length is the number of UTF-8 bytes.
- Side B, PRD FP-07 `length` (line 240): "the number of Unicode characters (not bytes)".
- **Built:** characters (`len()` of the `str`). Side B is the function's definition.

### C-11 Multiselect list on a null current value
- Side A, PRD FP-05 (line 187): "On a null current value it still builds one element per expression."
- Side B, PRD FP-05 (line 188): "A multiselect list or hash whose current value is null yields null."
- **Built:** null, for lists and hashes alike. This is the general rule, and it matches the usual behaviour of this expression family.

### C-12 Arity of `length`
- Side A, PRD FP-07 list (line 240): `length(string, array or object)` written with two slots.
- Side B, PRD FP-07 meaning (line 240) and the arity rule (line 260): one value, "exactly the number of arguments listed".
- **Built:** one argument. `length("abc")` is valid; `length(a, b)` is `InvalidArityError`. Two-argument `length` is not offered.

### C-13 Whitespace inside `[ ]`
- Side A, PRD FP-02 (line 110): whitespace between any two tokens does not change meaning.
- Side B, PRD FP-03 (line 140): flatten is written "with nothing between them".
- **Built:** whitespace does not matter, so `[ ]` is flatten. The same holds for `[ * ]`, `[ ? ... ]` and `[ 0 ]`. The lexer produces separate tokens and the parser decides meaning from them.

### C-14 Text ending after a dot
- Side A, PRD FP-01 (line 94): text that ends where an operand must begin is incomplete.
- Side B, PRD FP-01 (line 95) and FP-02 (line 118): a dot followed by the end of the text is syntax.
- **Built:** syntax (`SyntaxFailure` at the end offset). Both explicit statements say so. Other cases where an operand is missing at the end, such as `a |`, `a ==`, `a &&`, `(a`, `a[`, are incomplete.

## Choices the specification leaves open (or that I resolved)

- **Projection thresholds.** The PRD ranks list wildcards, slices and object wildcards at 2 when they begin an operand, 4 for an object wildcard written after a dot, and 5 for a bracket written as a step. Using those values as a projection's threshold would end a projection too early. For example, `a.items[*].name.first` would become `(a.items[*].name).first`. I used threshold 2 for `[*]`, slices and `*`, 3 for filters, and 1 for flatten. A later step joins a projection's right-hand side when its rank is above that threshold. Ranks as written are used for the later steps. The consequence is `foo.*.bar.baz` evaluates as `foo.*` each value's `.bar.baz`.
- **Slices after an index** start a projection (a slice always projects, per FP-03). `foo[0][1:2]` is a projection.
- **Multiselect after a dot** (`.[a, b]`, `.{...}`) is allowed anywhere; later steps join its right-hand side like any other dot step.
- **Bare `*`** at the start of an operand is an object wildcard on the current value.
- **Dot followed by a function call** (`foo.abs(@)`) is allowed; the call is applied to the value selected before the dot.
- **Zero-argument calls** such as `keys()` parse and fail with `InvalidArityError` during search.
- **Function name check order.** Name is checked first (at search time, not compile time), then arity, then argument types. Arguments are evaluated before the type check. An unknown name inside a projection over an empty array is never reached.
- **Lookup order for functions.** The attached provider is consulted first, then the built-in `Functions`. A subclass can therefore override a built-in name. A provider that does not subclass `Functions` still gets all built-ins.
- **Custom function types.** Only the five public names are accepted by `signature`, plus internal refinements used by the built-ins (`expref`, `any`, `array_of_numbers`, and so on). `null` accepts only null; `array` accepts list and tuple; `object` accepts any `collections.abc.Mapping`.
- **Operators.** Comparators are left-associative (`a == b == c`). `<`, `<=`, `>`, `>=` between values that are not both numbers or both strings return null rather than refusing. `==` is deep JSON equality (booleans never equal numbers).
- **Literal grammar.** A backtick literal is read as JSON. `NaN` and `Infinity` are not JSON and fall back to string content. If that fails, the content is read as JSON string content (leading whitespace removed). `` \` `` inside a literal means a backtick. An unterminated literal, or content that is neither, is token-level.
- **Quoted identifiers** are JSON strings. Invalid escapes or raw control characters are token-level.
- **Raw strings.** Only `\'` and `\uXXXX` are special (surrogate pairs are combined). Other backslashes are kept. A malformed `\u` escape is kept as written.
- **Positions.** The `lex_position` of a syntax failure is the start offset of the offending token. For a token that cannot be read, it is the start of that token. The end of the text counts as the token at `len(text)`.
- **Incomplete vs syntax.** Text that ends where a closing bracket, brace, parenthesis or operand is still required is incomplete. A token that is wrong where it appears is syntax. A dot followed by the end is syntax (C-14).
- **Lazy tokenizing.** Tokens are read as the parser needs them, so the first failure in source order is the one reported.
- **Empty check** happens before anything else. Whitespace-only text is incomplete, not empty.
- **Expression references** in function arguments extend to the end of the argument (pipe level included). Outside a function they are values, not evaluated.
- **Projections** always return a new list. Input documents are never mutated. Literal lists and objects are deep-copied when returned, so a compiled expression cannot be changed through a result.
- **`type()`** returns `"boolean"` for booleans, `"number"`, `"string"`, `"array"` (list or tuple) and `"null"`. Other objects return `"object"`.
- **`avg`** is `sum / len` (a float for integers). `sum([])` is `0`. `max`/`min` of an empty array are null. `max_by`/`min_by` return the first element on ties. `sort_by` is stable.
- **`ceil` / `floor`** return `int`.
- **`to_string`** writes compact JSON with `\uXXXX` escapes for non-ASCII. Values that are not JSON types are written with `str()`. Mapping and tuple values are converted first.
- **`to_number`** accepts an optional sign and no surrounding whitespace.
- **`contains`** with a string subject requires a string needle. With an array subject, any needle is accepted and compared by JSON equality.
- **`merge`** returns a plain `dict`. Later keys overwrite earlier ones.
- **`keys` / `values`** accept objects only.
- **Host values.** Mappings are objects, lists and tuples are arrays, `Decimal` is a number. Other host values (dates, custom classes) can be selected and returned, are true values, and are refused by any function that needs a JSON type.
- **Evaluation options.** `dict_cls` is called with no arguments and filled by item assignment. If it returns a type that is not a `Mapping` subclass, the constructed hash is not treated as an object. Standard mappings (dict, OrderedDict, defaultdict) work.
- **Custom providers** receive the provider as `self` through the bound method, so `_func_<name>` methods can use provider state.
- **Expression reference value.** The wrapper class is `pathsel.ExpressionReference`. Its only public behaviour is `apply(value)`.

## Not verified

- Only CPython 3.13 was run here. The code avoids syntax newer than 3.9 but was not exercised on 3.9, PyPy, Windows, or macOS.
- The hidden tests were not consulted. The behaviour above follows the spec text and the choices listed here.
