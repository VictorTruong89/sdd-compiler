# NOTES — PathSel (`pathsel` package)

Implementation of the library described in `spec/`. Layout: flat package `pathsel/` at the
repository root, packaged by `pyproject.toml` (setuptools, zero runtime dependencies,
Python ≥ 3.9). Tests: `tests/test_pathsel.py` (`python3 -m pytest tests/`, 45 passing).

Line numbers below refer to the spec files as shipped. Where two spec statements disagree, I
kept one and dropped the other as listed here. My rule when a feature-specific statement
conflicted with a general one: I followed the feature-specific one (FP-xx normal or boundary
bullet over the Terminology table), and where both were explicit about the same case I
preferred the one that names the function or feature directly.

## Spec conflicts and what was built

1. **Empty array/string and `not_null`.**
   - `Full_PRD.md` line 23 (Terminology, *Null*): "An empty string or an empty array counts as null for `not_null`."
   - `Full_PRD.md` line 252 (FP-07, `not_null`): "(an empty array or empty string is not null)".
   - **Built:** not null. `not_null` returns the first argument that is not `null`.

2. **`to_number` of an integer numeral.**
   - Line 26 (Terminology, *Number*): "A number made from a string by `to_number` is always a floating-point value."
   - Line 247 (FP-07, `to_number`): "a string that is an integer numeral becomes that integer".
   - **Built:** integer numerals become `int`; decimal/exponent numerals become `float`.

3. **Object wildcard on a non-object.**
   - Line 32 (Terminology, *Projection*): "An object wildcard applied to a non-object is the empty array."
   - Line 159 (FP-04): "An object wildcard on a value that is not an object yields null."
   - **Built:** `null`, the same as list wildcards and filters.

4. **Expression reference outside a function argument.**
   - Line 29 (Terminology, *Expression reference*): "Outside a function argument it evaluates to null."
   - Line 193 (FP-05): searching a bare reference "succeeds and yields a non-null value"; Interface Contract line 113 repeats this.
   - **Built:** a bare `&expr` returns a non-null `pathsel.values.Ref` object. Inside a function argument it is passed to the function as a reference.

5. **Zero slice step.**
   - Line 133 (FP-03, normal): "A step of 0 selects nothing: the result is the empty array."
   - Line 146 (FP-03, boundary): a zero step "does not succeed ... That failure is the zero-slice-step kind ... not a successful empty array".
   - **Built:** refusal (`ZeroSliceStep`). The check runs at compile time, so `compile` and `search` both refuse. Interface Contract line 106 names it as a separate kind.

6. **Slice of a non-array.**
   - Line 138 (FP-03, normal): "A slice on a value that is not an array yields null."
   - Line 148 (FP-03, boundary): "A slice of a value that is not an array is the empty array."
   - **Built:** `null`.

7. **Filter on a non-array.**
   - Line 175 (FP-04): "A filter on a non-array yields null, not an empty array and not a failure."
   - Line 215 (FP-06): "A filter applied to anything but an array yields the empty array."
   - **Built:** `null`.

8. **Multiselect list/hash on a null current value.**
   - Line 187 (FP-05): "On a null current value it still builds one element per expression."
   - Line 188 (FP-05): "A multiselect list or hash whose current value is null yields null."
   - **Built:** `null` for both list and hash. Line 188 covers both forms and the hash, and it matches the JMESPath behavior this language is modeled on.

9. **`join` of an empty array.**
   - Line 242 (FP-07, `join`): "the empty array yields the empty string."
   - Line 230 (FP-07, boundary): "`join` of an empty array yields null."
   - **Built:** `null`. The boundary sentence names this exact case.

10. **Lone `=`: token-level or grammar-level.**
    - Line 37 (Terminology): "A single `=` is a grammar-level failure of this kind."
    - Line 219 (FP-06): "A lone `=` is a token-level syntax failure".
    - **Built:** token-level (`TokenSyntaxFailure`, which is a subclass of `SyntaxFailure`). Both kinds are syntax refusals, so a caller that handles the syntax kind still handles it.

11. **Dot at the end of the text: syntax or incomplete.**
    - Line 94 (FP-01): text ending where an operand must begin is incomplete.
    - Line 95 (FP-01): a dot followed by "the end of the text" is a syntax failure.
    - **Built:** syntax. The dot rule is the more specific one. Every other end-of-text case where an operand or a closer is missing is incomplete.

## Gaps the spec does not state, and what I assumed

- **Bare number literals are not operands.** `5`, `-1` as an expression, or `abs(1)`, are syntax failures. Numbers appear only inside brackets. Literal values use backticks, for example `` `1` ``.
- **Ordering comparison of non-comparable values** (`<`, `<=`, `>`, `>=` where the two sides are not both numbers or both strings) yields `null`, as in JMESPath. `==`/`!=` and `!` always yield `true`/`false`.
- **`type()` of a host value outside the six JSON types** returns `"object"`.
- **Custom-function argument types.** `signature` accepts the five listed type names. I also accept `"boolean"` (booleans cannot be declared otherwise) and `"any"`. Unknown names raise `ValueError` when the decorator is applied.
- **Function resolution order.** Built-in names are checked first, so a provider cannot change a built-in (FP-08 says built-ins keep "unchanged behavior"). Otherwise the provider's `_func_<name>` must carry the `signature` marker, or the name is unknown.
- **Check order on a call.** Name first, then argument count (both before any argument is evaluated), then the arguments are evaluated, then their types are checked, then the function runs. A call that is never reached (for example the right side of `||` after a true left side) is never checked.
- **Null short-circuit on the left of a dot.** When the left side of `a.b` is `null`, the right side is not evaluated. So `missing.length(@)` yields `null`, not an invalid-type refusal. Projections and filters on null also yield `null`.
- **Slice placement.** Every slice (`[a:b]`, `[a:b:c]`, `[:]`) starts a projection, including right after an index or another slice. An index never starts a projection.
- **Projection reach.** The step written directly after a projection form always begins its right-hand side (dot, index, slice, list wildcard, filter, multiselect). A flatten `[]` directly after a projection does not begin the right-hand side, so it applies to the collected array. Later steps join the right-hand side only if they bind tighter than the projection (flatten 9 < wildcard 20 < filter 21 < dot 40 < bracket 55). `a[*].[b, c].d` lets `.d` join the outer projection.
- **Object wildcard binding.** `*` and `.*` use the list-wildcard rank for their own right-hand side. A dot step after a `.*` therefore joins it.
- **Whole-text lexing first.** All token-level failures in the text are found before any grammar-level failure, so a token error anywhere wins over a grammar error earlier in the text.
- **Incomplete vs syntax.** End of text where an operand, a closing `)`, `]` or `}`, or a missing right side of a binary operator is required gives `IncompleteExpression` at the end offset. A dot at the end is syntax (see conflict 11). Anything else that is wrong is `SyntaxFailure` at the first offending token.
- **Function call with whitespace.** `a (b)` is a function call, since whitespace between tokens does not change meaning. `a.f(x)` calls `f` with the value of `a` as the current value.
- **Expression reference extent.** `&` extends to the end of the enclosing argument, element, parenthesis or expression, and includes pipes and comparisons.
- **Empty multiselect hash** `{}` is a syntax failure. `[]` is flatten (an empty list with no elements is not a valid multiselect list).
- **Duplicate hash keys:** the last pair wins.
- **Quoted identifiers:** the content must be a legal JSON string with no raw control characters (use `\u` escapes). Illegal content is a token-level failure.
- **Raw strings** `'...'`: the only backslash-escape is `\'`. A valid `\uXXXX` is decoded (surrogate pairs combined). Any other backslash is kept as written. A `\u` without four hex digits is kept as written.
- **Backtick literals:** the text is read as JSON. If that fails it is read as JSON string content after stripping leading whitespace (so `` `abc` `` is `"abc"`). `` \` `` inside the literal means a backtick. A literal that fails both readings is a token-level failure.
- **Literal values** are copied on each evaluation, so a caller mutating a result cannot change the expression.
- **Results may share structure with the input document.** Evaluation never writes to the input. A result may return the same list or mapping object that the document holds.
- **Array and object types.** Python `list` and `tuple` are arrays. Any `collections.abc.Mapping` is an object (including `OrderedDict`). `bool` is never a number.
- **`dict_cls`** applies only to multiselect hashes. `merge` returns a plain `dict`.
- **Host `Decimal`** counts as a number for comparisons, arithmetic and sorting. In JSON output (`to_string`) it is written as a float. Mixed `Decimal`/`float` sums are computed as floats.
- **`to_number`:** accepts an optional leading `+` or `-`. Input that is not an ASCII numeral (for example `"NaN"`, `"inf"`, `" 12 "`) yields `null`.
- **`to_string`** of a non-JSON host value uses `str()` for that value.
- **`sum([])`** is `0`. **`avg([])`**, **`max([])`**, **`min([])`**, **`max_by([])`**, **`min_by([])`** are `null`. **`sort([])`** and **`sort_by([], ...)`** are `[]`.
- **`sort_by` / `max_by` / `min_by` key checks:** every key must be a number, or every key must be a string, and null is neither. A mixed or null key is `InvalidType`. Ties in `max_by`/`min_by` keep the first element. `sort_by` is stable.
- **`contains` on a string** requires a string second argument. Otherwise it is `InvalidType`.
- **`length`** counts Unicode code points (Python `len`), not UTF-8 bytes.
- **Exception types.** `ValueError` is the base of every refusal (`PathSelError`). The kind is the exception type: `EmptyExpression`, `IncompleteExpression`, `SyntaxFailure`, `TokenSyntaxFailure(SyntaxFailure)`, `ZeroSliceStep`, `UnknownFunction`, `InvalidArity`, `InvalidType`. `IncompleteExpression` and `SyntaxFailure` carry `lex_position`.
- **Packaging.** `pyproject.toml` names the distribution `pathsel` and lists the `pathsel` package. The project root on `sys.path` (or an editable install) is enough to import it. Nothing is installed or built by the judge.
