# NOTES

Implementation notes for the pathsel library built from `spec/`. Section 1 lists every
conflict in the spec and what was built. Section 2 lists things the spec does not state
and the assumption made. Section 3 covers verification and what was not checked.

Rule used for conflicts: when two spec statements disagree, the one inside the feature
point that owns the behavior (the bullet that defines the function, filter, slice, and so
on) wins over a general statement in Terminology or the data model. Where both statements
sit in the same feature point, the choice is named below.

## 1. Conflicts (the 11 unsettled contradictions in `spec/MAP.md`)

Quotes are verbatim from the packs. Pack numbers refer to `spec/packs/`.

| Id | Side A (quoted) | Side B (quoted) | Built |
|---|---|---|---|
| CF-000005 | N-000202, pack 09 (FP-04): "A filter on a non-array yields null, not an empty array and not a failure." | N-000259, pack 11 (FP-06): "A filter applied to anything but an array yields the empty array." | **null.** FP-04 owns filters and is the more explicit statement. |
| CF-000007 | N-000142, pack 08 (FP-03): "A slice on a value that is not an array yields null." | N-000157, pack 08 (FP-03): "A slice of a value that is not an array is the empty array." | **null.** Both are in FP-03; the normal-behavior bullet is used. |
| CF-000011 | N-000212, pack 10 (FP-05): "On a null current value it still builds one element per expression." | N-000218, pack 10 (FP-05): "A multiselect list or hash whose current value is null yields null." | **null.** N-000218 covers lists and hashes together; N-000212 covers only lists. |
| CF-000015 | N-000022, pack 02 (Terminology): "An empty string or an empty array counts as null for `not_null`." | N-000300, pack 12 (FP-07): "an empty array or empty string is not null" | **Not null.** The `not_null` bullet in FP-07 defines the function. |
| CF-000027 | N-000031, pack 02 (Terminology): "An object wildcard applied to a non-object is the empty array." | N-000165, pack 09 (FP-04): "An object wildcard on a value that is not an object yields null." | **null.** FP-04 owns the object wildcard. |
| CF-000035 | N-000026, pack 02 (Terminology): "its length is its number of UTF-8 bytes" | N-000277, pack 12 (FP-07): "the number of Unicode characters (not bytes) of a string" | **Unicode characters** (Python code points). The `length` bullet defines the function. |
| CF-000049 | N-000227, pack 10 (FP-05): "No JSON escapes are processed." | N-000239, pack 10 (FP-05): "A `\uXXXX` escape inside a raw string literal is decoded to its character." | **`\uXXXX` is decoded; no other escape is.** The specific rule beats the general one. `\'` is a quote, `\\` stays two backslashes, and `\n` stays backslash-n. |
| CF-000054 | N-000268, pack 12 (FP-07): "`join` of an empty array yields null." | N-000280, pack 12 (FP-07): "the empty array yields the empty string." | **Empty string.** The `join` bullet defines the function. |
| CF-000055 | N-000133, pack 08 (FP-03): "A step of 0 selects nothing: the result is the empty array" | N-000152, pack 08 (FP-03): "A slice whose step is 0 does not succeed on either entry" | **Refused with the zero-slice-step kind** (`ZeroSliceStepError`). The kind is listed in Terminology and in N-000415, which requires its own type. The refusal is raised at compile time, which the spec allows ("either the compile or the later search refuses"). |
| CF-000056 | N-000028, pack 02 (Terminology): "Outside a function argument it evaluates to null" | N-000234, pack 10 (FP-05): "Searching an expression reference on its own succeeds and yields a non-null value" (also N-000423, pack 25) | **Non-null.** A bare `&expr` search returns an `ExprRef` object (not JSON data, not the document, not the referenced result). |
| CF-000057 | N-000023, pack 02 (Terminology): "a number made from a string by `to_number` is always a floating-point value" | N-000287, pack 12 (FP-07): "a string that is an integer numeral becomes that integer, otherwise ... floating-point" | **Integer numerals give `int`**; decimal and exponent numerals give `float`. So `to_number('42')` is `42`. |

Two of the decisions also settle non-conflicting placements:

- Projection and slice null-dropping: a slice with no right-hand side still drops null
  elements, because the spec says a slice is a projection and null results are dropped.
- Implementer's choices (N-000198, N-000199): a slice written directly after an index or
  slice starts a projection; and when a right-hand side begins with a dot followed by a
  multiselect list or hash, later steps that bind tighter than the projection still join it
  (the general rule in N-000191).

## 2. Things the spec does not state (assumptions)

- **Comparison of mismatched types** (`<`, `<=`, `>`, `>=`): the spec only defines numbers
  and strings. Mixed or other types give null. `==` and `!=` are always booleans.
- **Equality with host values** (non-JSON Python objects): falls back to Python `==`
  when neither side is a JSON type.
- **`type()` of a non-JSON host value**: the spec says `any` accepts every value, but the
  result set is fixed to six names. Non-JSON values give null.
- **`to_string()` of a non-JSON host value**: its `str()` is written as a JSON string.
  Host `Decimal` values are written as `str(d)`. Floats use `json.dumps` (which matches
  `repr`).
- **`sum([])`** is `0`. **`avg([])`** is null (stated).
- **`avg`** uses true division, so an integer mean comes back as a `float`.
- **`ceil` and `floor`** of a non-finite host float (NaN, infinity) refuse with
  invalid-type. Without this they would raise a non-PathSel `OverflowError`.
- **`contains(string, x)`**: `x` must be a string, else invalid-type.
- **`max`, `min`, `sort`**: an empty array gives null, `[]`, respectively. A mix of numbers
  and strings is invalid-type. Booleans are not numbers.
- **`merge`** returns a plain `dict`, not the configured `dict_cls`. Only multiselect hashes
  use `dict_cls` (the spec names only those).
- **Function call order**: name first, then argument count, then argument evaluation, then
  argument types, then the call. Argument evaluation happens before the types are checked,
  so a refusal inside an argument surfaces before the type refusal.
- **Function call after a dot** (`foo.length(@)`) is allowed. The spec does not forbid it, and
  JMESPath-style grammars allow it.
- **Dot before a bracket**: `a.[x, y]` is a multiselect list. `a.[0]`, `a.[]`, `a.[?...]`,
  `a.[*]` are grammar-level syntax failures. The spec says a dot must be followed by an
  identifier, a wildcard, a multiselect list, or a multiselect hash, and nothing else fits.
- **Backtick JSON literal**: `\`` inside the backticks is a literal backtick. Valid JSON is
  read as JSON. Otherwise the text, after removing leading whitespace, is read as JSON string
  content (trailing whitespace is kept). Unclosed or unreadable text is a token-level failure.
  `NaN` and `Infinity` are not JSON, so they take the string fallback.
- **Numbers in the grammar** are integers only (used in indices and slices). A bare number
  elsewhere, such as `length(1)`, is a syntax failure. `` `1` `` is the JSON literal form.
- **Wildcard, filter and flatten at expression start** apply to the document itself
  (`[*]`, `*`, `[?...]`, `[]`); this follows the spec's "may be the whole expression or the
  start of one".
- **Pipe, `&&`, `||`, `!` precedence** follows the spec's binding order: pipe < `||` < `&&` <
  comparators < `!`. Within a projection, the spec's rank order (flatten < list/slice/object
  wildcard < filter < dot < index) decides which later steps join the right-hand side.
- **`!` operand** takes index, slice and list-wildcard brackets written directly after it,
  but not a dot step, a filter, or a flatten (the spec's rule).
- **Zero-argument functions**: `f()` parses; the arity refusal happens at search time.
- **Slices with a step of 0 are refused at compile time.** The refusal is raised in the
  parser, not at search time (the spec allows either).
- **Options object**: attributes are read with `getattr`, so any object with `dict_cls` and/or
  `custom_functions` works, and a missing attribute means `None`. A `None` options argument is
  the same as no options.
- **Provider overrides**: a provider cannot replace a built-in. A `_func_<builtin>` method on a
  subclass is ignored, so every FP-07 function keeps its behavior (N-000340). Only `_func_`
  methods decorated with `signature` are custom functions.
- **`signature` extensions** (internal to the built-ins; the spec's type list is still the
  supported public form): `variadic=True` keyword (for `merge` and `not_null`), and two
  additional type names, `"any"` and `"reference"` (an `ExprRef` argument). Custom functions
  may use the five spec type names, and also these two.
- **Expression reference as a result**: an `ExprRef` object is returned from a bare `&expr`
  search (see CF-000056). It is the only non-JSON result the library produces.
- **Non-string expression text** raises `TypeError` (a programming error, not a refusal).
- **Positions**: `lex_position` is the character offset (UTF-16 offsets are not used). Tokens
  are split on the first failure in text order, so a grammar failure earlier in the text is
  reported before a later token-level failure.
- **Empty expression** has `lex_position == 0`. The spec only requires the position for syntax
  and incomplete kinds.
- **Raw strings** process `\'` and `\uXXXX` (see CF-000049). Unterminated raw strings are
  token-level failures.
- **Quoted identifiers and JSON strings**: the lexer uses `json.loads` in strict mode, so a raw
  control character inside the quotes is a token-level failure.
- **Mapping types**: any `collections.abc.Mapping` is accepted as an object, not only dicts and
  `OrderedDict`. The spec leaves other mapping types to the implementer (N-000333).
- **Packaging**: flat `pathsel/` at the root (N-000369). `pyproject.toml` declares the
  distribution name `pathsel` with no dependencies. No build step is required to import from
  `/app`.

## 3. Verification and gaps

- Tests: `tests/test_pathsel.py` (172 cases), run with Python 3.13 and pytest 8.4.1. All pass.
- Python 3.9 (the stated floor) is **not installed here**, so it has not been run. The code uses
  no syntax newer than 3.8 (no `match`, no `X | Y` types, no `str.removeprefix`), but this is
  unverified.
- PyPy, macOS and Windows were **not run**. The code is pure Python with no platform calls.
- No CLI, no `python -m` entry, and no network code exist, as the spec requires.
- `spec/` was not modified.
- `SPEC_COVERAGE.md` maps every checklist id to its implementation or to the reason it is
  satisfied another way.
