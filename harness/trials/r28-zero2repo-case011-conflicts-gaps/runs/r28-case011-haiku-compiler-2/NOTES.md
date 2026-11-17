# pathsel: implementation notes

The library is in `pathsel/` at the repository root (flat layout, spec N-000369/N-000370).
Tests are in `tests/`, named after spec ids. No build step is needed.

Run the suite with either:

    python3 -m pytest tests
    python3 -m unittest discover -s tests

Verified here on Python 3.13 and 3.11. The 3.9 floor is checked by
`ast.parse(..., feature_version=(3, 9))` over the package, not by running 3.9.

## Layout

| file | role |
|---|---|
| `pathsel/__init__.py` | `search`, `compile`, error types, public re-exports |
| `pathsel/errors.py` | failure kinds (all `ValueError`s) |
| `pathsel/lexer.py` | tokens, lazily produced so token errors report the first failing position |
| `pathsel/parser.py` | Pratt parser; binding powers encode the projection ranks |
| `pathsel/nodes.py` | AST nodes and their evaluation (projections, filters, slices, calls) |
| `pathsel/values.py` | value model: type predicates, truthiness, JSON equality, references |
| `pathsel/functions.py` | `Functions` provider, `signature`, the 26 built-ins |
| `pathsel/evaluator.py` | evaluation context (options) and the `Parsed` object |
| `pyproject.toml` | setuptools metadata; no runtime dependencies |

## Spec conflicts and how each was resolved

Each entry quotes both sides with their pack file. The seven entries the export marks
`UNSETTLED` are listed first; the others were found while reading the packs.

1. **CF-000005, filter on a non-array.** `spec/packs/09-...fp-04...md` line 62
   (N-000202): "A filter on a non-array yields null, not an empty array and not a failure."
   versus `spec/packs/11-...fp-06...md` line 32 (N-000259): "A filter applied to anything
   but an array yields the empty array." **Built: null.**

2. **CF-000007, slice of a non-array.** `spec/packs/08-...fp-03...md` line 41 (N-000142):
   "A slice on a value that is not an array yields null." versus line 65 (N-000157): "A slice
   of a value that is not an array is the empty array." **Built: null.**

3. **CF-000011, multiselect on a null current value.** `spec/packs/10-...fp-05...md` line 20
   (N-000212): "On a null current value it still builds one element per expression." versus line 23
   (N-000218): "A multiselect list or hash whose current value is null yields null." **Built: null**
   (the more general rule, and the one JMESPath-style languages use).

4. **CF-000015, `not_null` and empty values.** `spec/packs/02-...terminology.md` line 17
   (N-000022): "An empty string or an empty array counts as null for `not_null`." versus
   `spec/packs/12-...fp-07...md` line 77 (N-000300): "an empty array or empty string is not null."
   **Built: not null** (the FP-07 definition of the function). N-000022 is not done.

5. **CF-000027, object wildcard on a non-object.** `spec/packs/02-...terminology.md` line 26
   (N-000031): "An object wildcard applied to a non-object is the empty array." versus
   `spec/packs/09-...fp-04...md` line 21 (N-000165): "An object wildcard on a value that is not an
   object yields null." **Built: null.** N-000031 is not done.

6. **CF-000035, string length.** `spec/packs/02-...terminology.md` line 21 (N-000026): "its length
   is its number of UTF-8 bytes" versus `spec/packs/12-...fp-07...md` line 41 (N-000277): "the
   number of Unicode characters (not bytes) of a string". **Built: code points** (`len(str)`).

7. **CF-000049, escapes in raw strings.** `spec/packs/10-...fp-05...md` line 35 (N-000227): "No
   JSON escapes are processed." versus line 47 (N-000239): "A `\uXXXX` escape inside a raw string
   literal is decoded to its character." **Built:** `\uXXXX` (four hex digits) is decoded, `\'` is
   a quote, and every other backslash stays literal.

Conflicts found while reading, not flagged by the export:

8. **`join` of an empty array.** `spec/packs/12-...fp-07...md` line 17 says "`join` of an empty
   array yields null." Line 47 (N-000280) says the empty array yields the empty string. **Built: "".**
   The definition line was preferred.

9. **Bare expression reference.** `spec/packs/02-...terminology.md` line 23: a reference "outside a
   function argument ... evaluates to null." versus `spec/packs/10-...fp-05...md` line 38 (N-000235)
   and `spec/packs/25-...expression-reference-value.md` line 9 (N-000423): searching a bare reference
   returns a non-null value. **Built: non-null**, an `ExpressionReference` object. The Terminology
   sentence (N-000028) is not done.

10. **Hash directly after a projection form.** `spec/packs/10-...fp-05...md` line 23 allows "a
    multiselect list or hash ... as the right-hand side of a projection". The reach rule in
    `spec/packs/09-...fp-04...md` line 38 lists only a dot step, a bracket step (index, slice, list
    wildcard, multiselect list) or a filter as the first step. **Built:** `foo[*].{...}` (through a
    dot) is allowed; `foo[*]{...}` is a syntax error. A multiselect *list* is allowed directly.

11. **Host decimals.** `spec/packs/04-...non-functional-constraints.md` line 21: host decimals are
    numbers "for comparison", and built-in arguments that require a JSON type refuse host values
    that are not JSON types. **Built:** decimals order and compare as numbers (`d > \`2\`` works),
    but a function argument typed `number` refuses them as invalid-type.

## Assumptions (not stated in the spec)

- **Bare numbers are not expressions.** `abs(-3)` is a syntax error; write `abs(\`-3\`)`. The spec
  writes numbers as JSON literals (backticks), and a number cannot begin an operand.
- **Mismatched ordering** (`<`, `<=`, `>`, `>=` on a number and a string, or on a boolean) yields
  null, not false. The spec defines ordering only for two numbers or two strings.
- **`length`** takes one argument whose accepted types are string, array or object. The spec writes
  `length(string, array or object)` and I read the second part as the type of the single argument.
- **Arithmetic:** `sum([])` is `0`; `avg` returns a float; `ceil`/`floor` return int.
- **`to_number`:** integer numerals are `[+-]?digits`; decimal and exponent numerals become floats.
  No surrounding whitespace is accepted.
- **`to_string`:** compact JSON with `ensure_ascii`. Decimals become floats. Host values that are not
  JSON are written as a JSON string of `str(value)`.
- **`type`** returns null for host values that are not JSON types.
- **Arrays and objects.** Lists and tuples are arrays. Any `Mapping`, and any object with `keys()`
  and item access (such as a constructed hash of a custom `dict_cls`), is an object.
- **JSON literals:** text is parsed as JSON; if that fails, it is read as JSON string content after
  stripping leading whitespace. A backtick cannot appear inside a literal (no escape is defined).
- **Quoted identifiers and literals** use strict JSON decoding; control characters are refused.
- **Zero slice step** is refused when the expression is compiled, so both entries refuse it, whatever
  the document.
- **Check order for calls:** name, then argument count, then argument types; arguments are evaluated
  after the count check and before the type check.
- **Function calls after a dot** are allowed (`a.length(@)`, `people[*].type(@)`). That is how a
  call becomes the right-hand side of a projection.
- **Built-in names take precedence** over a provider's methods of the same name, so every FP-07
  function keeps its behaviour (FP-08). A provider adds only new names.
- **Custom argument types** are `number`, `string`, `array`, `object`, `null`. The internal names
  (`any`, `boolean`, `ref`, and the array-of-type forms) are accepted too.
- **Non-string expression** passed to `compile`/`search` raises `TypeError`. It is not one of the
  refusal kinds, which apply to expression text.
- **Placement choices** (spec N-000198/N-000199): a slice written directly after an index or slice
  starts a projection; after a dot-led multiselect, later steps join its right-hand side. A filter
  directly after a filter starts the right-hand side of the first (the literal reading of N-000184).
- **Ranking of object wildcards:** `a.*.b.c` is `(a.*.b).c`, because the rank of an object wildcard
  after a dot is 4 and only tighter steps join its right-hand side. That is the spec's rule and matches
  the binding-power model; it looks odd but is what the rule says.
- **Binary operators** are left-associative (`a | b | c`, `a == b == c`); the spec does not say.
- **`!` operand:** the operand is the nud plus index, slice and list-wildcard brackets (binding 45).
  `!a.b` is `(!a).b`.
- **Results** are plain Python: `dict` for objects (or `dict_cls` instances), `list` for arrays.
  Literal containers are copied on each evaluation.
- **Options** are read by attribute (`dict_cls`, `custom_functions`) with `getattr`, so any object
  works; `None` means defaults.
- **Errors:** position is the offset of the token where the expression stopped being well formed;
  end of text is `len(text)`. Empty expressions carry no `lex_position`, since the spec asks for
  positions only on syntax and incomplete refusals.

## Not done, with reasons

Each id below has a reason in the traceability table. The short list:

- N-000010 to N-000013: descriptive statements in the PRD overview; they have no separate behaviour.
- N-000022, N-000031: superseded by the conflict resolutions above (items 4 and 5).
- N-000028: superseded by item 9.
- N-000037, N-000061: failure-message wording is informational.
- N-000053, N-000354, N-000356: platform claims (Linux, macOS, Windows, x86_64/arm64). The code uses
  only the standard library, but only Linux was run here.
- N-000072: a non-goal about future language revisions; nothing to build.

## Verification

- `python3 -m pytest tests` (or `unittest`): 178 tests pass on Python 3.13; the suite also passes on
  Python 3.11.
- Syntax compatibility with 3.9 is checked with `ast.parse(..., feature_version=(3, 9))`.
- The traceability table below was generated from `# spec: N-...` comments in `pathsel/` and from
  the ids in test names in `tests/`.

## Traceability (generated)

Status per checklist id. "code" = a `# spec:` comment in `pathsel/`; "test" = a test name in `tests/`. "not done" ids are listed with the reason.


### Pack 01 — 01-full-prd--product-overview.md

| id | status | where |
|---|---|---|
| N-000001 | tested | tests/test_pathsel.py |
| N-000002 | tested | tests/test_pathsel.py |
| N-000003 | tested | tests/test_pathsel.py |
| N-000004 | tested | tests/test_spec_ids.py |
| N-000005 | tested | tests/test_spec_ids.py |
| N-000006 | tested | tests/test_pathsel.py |
| N-000007 | tested | tests/test_spec_ids.py |
| N-000008 | tested | tests/test_spec_ids.py |
| N-000009 | tested | tests/test_spec_ids.py |
| N-000010 | not done | scope statement of the PRD overview; no separate behaviour |
| N-000011 | not done | feature-point ordering statement; no separate behaviour |
| N-000012 | not done | feature-point dependency statement; no separate behaviour |
| N-000013 | not done | descriptive statement about the document; no separate behaviour |

### Pack 02 — 02-full-prd--terminology.md

| id | status | where |
|---|---|---|
| N-000014 | tested | tests/test_spec_ids.py |
| N-000015 | tested | tests/test_spec_ids.py |
| N-000016 | tested | tests/test_spec_ids.py |
| N-000017 | tested | tests/test_spec_ids.py |
| N-000018 | tested | tests/test_spec_ids.py |
| N-000019 | tested | tests/test_pathsel.py |
| N-000020 | tested | tests/test_pathsel.py |
| N-000021 | tested | tests/test_spec_ids.py |
| N-000022 | not done | conflict CF-000015: empty string/array as null for not_null; built the FP-07 rule (N-000300), not null |
| N-000023 | implemented | values.py |
| N-000024 | tested | tests/test_spec_ids.py |
| N-000025 | tested | tests/test_spec_ids.py |
| N-000026 | implemented | values.py |
| N-000027 | tested | tests/test_spec_ids.py |
| N-000028 | not done | conflict with N-000235/N-000423: bare reference is non-null; built non-null (see NOTES) |
| N-000029 | tested | tests/test_spec_ids.py |
| N-000030 | tested | tests/test_spec_ids.py |
| N-000031 | not done | conflict CF-000027: object wildcard on non-object is empty array; built null (N-000165) |
| N-000032 | tested | tests/test_spec_ids.py |
| N-000033 | tested | tests/test_pathsel.py |
| N-000034 | tested | tests/test_spec_ids.py |
| N-000035 | tested | tests/test_spec_ids.py |
| N-000036 | tested | tests/test_spec_ids.py |
| N-000037 | not done | failure report wording is the implementer choice (N-000408); not behaviour |

### Pack 03 — 03-full-prd--public-surface-inventory.md

| id | status | where |
|---|---|---|
| N-000038 | implemented | values.py |
| N-000039 | tested | tests/test_spec_ids.py |
| N-000040 | tested | tests/test_spec_ids.py |
| N-000041 | tested | tests/test_spec_ids.py |
| N-000042 | tested | tests/test_spec_ids.py |
| N-000043 | tested | tests/test_spec_ids.py |
| N-000044 | tested | tests/test_spec_ids.py |
| N-000045 | tested | tests/test_spec_ids.py |
| N-000046 | tested | tests/test_spec_ids.py |
| N-000047 | tested | tests/test_spec_ids.py |
| N-000048 | tested | tests/test_spec_ids.py |
| N-000049 | tested | tests/test_spec_ids.py |

### Pack 04 — 04-full-prd--non-functional-constraints.md

| id | status | where |
|---|---|---|
| N-000050 | tested | tests/test_pathsel.py |
| N-000051 | tested | tests/test_pathsel.py |
| N-000052 | tested | tests/test_spec_ids.py |
| N-000053 | not done | platform list (Linux, macOS, Windows); code is stdlib-only, but only Linux was run here |
| N-000054 | tested | tests/test_spec_ids.py |
| N-000055 | tested | tests/test_pathsel.py |
| N-000056 | implemented, tested | tests/test_pathsel.py, values.py |
| N-000057 | implemented | values.py |
| N-000058 | implemented | values.py |
| N-000059 | tested | tests/test_pathsel.py |
| N-000060 | tested | tests/test_pathsel.py |
| N-000061 | not done | wording of failure messages is informational |
| N-000062 | tested | tests/test_spec_ids.py |
| N-000063 | tested | tests/test_spec_ids.py |
| N-000064 | tested | tests/test_spec_ids.py |
| N-000065 | tested | tests/test_spec_ids.py |
| N-000066 | tested | tests/test_pathsel.py |

### Pack 05 — 05-full-prd--non-goals.md

| id | status | where |
|---|---|---|
| N-000067 | tested | tests/test_spec_ids.py |
| N-000068 | tested | tests/test_spec_ids.py |
| N-000069 | tested | tests/test_pathsel.py |
| N-000070 | tested | tests/test_pathsel.py |
| N-000071 | decision (nothing built) | chosen: development tooling is outside the product |
| N-000072 | not done | non-goal (what is not built); no code |

### Pack 06 — 06-full-prd--fp-01-search-an-expression-and-compile-i.md

| id | status | where |
|---|---|---|
| N-000073 | tested | tests/test_spec_ids.py |
| N-000074 | tested | tests/test_spec_ids.py |
| N-000075 | tested | tests/test_spec_ids.py |
| N-000076 | tested | tests/test_spec_ids.py |
| N-000077 | tested | tests/test_spec_ids.py |
| N-000078 | tested | tests/test_pathsel.py |
| N-000079 | tested | tests/test_spec_ids.py |
| N-000080 | tested | tests/test_pathsel.py |
| N-000081 | tested | tests/test_pathsel.py |
| N-000082 | tested | tests/test_pathsel.py |
| N-000083 | implemented, tested | nodes.py, tests/test_pathsel.py |
| N-000084 | tested | tests/test_spec_ids.py |
| N-000085 | tested | tests/test_pathsel.py |
| N-000086 | tested | tests/test_pathsel.py |
| N-000087 | implemented, tested | errors.py, parser.py, tests/test_pathsel.py |
| N-000088 | implemented | parser.py |
| N-000089 | implemented, tested | errors.py, parser.py, tests/test_pathsel.py |
| N-000090 | implemented, tested | errors.py, parser.py, tests/test_pathsel.py |
| N-000091 | implemented | errors.py |
| N-000092 | implemented | errors.py |
| N-000093 | implemented, tested | errors.py, parser.py, tests/test_pathsel.py |
| N-000094 | implemented, tested | errors.py, parser.py, tests/test_pathsel.py |
| N-000095 | implemented, tested | errors.py, tests/test_pathsel.py |
| N-000096 | implemented, tested | errors.py, tests/test_pathsel.py |
| N-000097 | implemented | errors.py |
| N-000098 | implemented | errors.py |
| N-000099 | implemented | errors.py |
| N-000100 | implemented | errors.py |
| N-000101 | implemented, tested | errors.py, tests/test_pathsel.py |
| N-000102 | tested | tests/test_pathsel.py |
| N-000103 | tested | tests/test_spec_ids.py |
| N-000104 | tested | tests/test_pathsel.py |
| N-000105 | tested | tests/test_pathsel.py |
| N-000106 | tested | tests/test_pathsel.py |

### Pack 07 — 07-full-prd--fp-02-select-fields-with-identifiers-and.md

| id | status | where |
|---|---|---|
| N-000107 | implemented, tested | lexer.py, parser.py, tests/test_pathsel.py |
| N-000108 | implemented | parser.py |
| N-000109 | implemented, tested | lexer.py, tests/test_pathsel.py, tests/test_spec_ids.py |
| N-000110 | implemented, tested | lexer.py, parser.py, tests/test_pathsel.py |
| N-000111 | implemented | lexer.py, parser.py |
| N-000112 | implemented, tested | lexer.py, parser.py, tests/test_pathsel.py |
| N-000113 | implemented | lexer.py, parser.py |
| N-000114 | implemented, tested | lexer.py, parser.py, tests/test_pathsel.py |
| N-000115 | implemented | nodes.py |
| N-000116 | implemented, tested | nodes.py, tests/test_pathsel.py |
| N-000117 | implemented, tested | parser.py, tests/test_pathsel.py |
| N-000118 | implemented | parser.py |
| N-000119 | implemented, tested | lexer.py, tests/test_pathsel.py |
| N-000120 | implemented, tested | lexer.py, tests/test_pathsel.py |
| N-000121 | implemented | lexer.py |
| N-000122 | tested | tests/test_pathsel.py |
| N-000123 | implemented, tested | parser.py, tests/test_pathsel.py |
| N-000124 | implemented, tested | lexer.py, tests/test_pathsel.py |
| N-000125 | implemented | nodes.py |

### Pack 08 — 08-full-prd--fp-03-index-slice-and-flatten-arrays.md

| id | status | where |
|---|---|---|
| N-000126 | implemented, tested | parser.py, tests/test_pathsel.py |
| N-000127 | implemented | parser.py |
| N-000128 | implemented, tested | parser.py, tests/test_pathsel.py |
| N-000129 | implemented, tested | parser.py, tests/test_pathsel.py |
| N-000130 | implemented | parser.py |
| N-000131 | implemented, tested | parser.py, tests/test_pathsel.py |
| N-000132 | implemented | parser.py |
| N-000133 | implemented, tested | parser.py, tests/test_pathsel.py |
| N-000134 | implemented, tested | parser.py, tests/test_pathsel.py |
| N-000135 | implemented, tested | parser.py, tests/test_pathsel.py |
| N-000136 | implemented | parser.py |
| N-000137 | implemented, tested | parser.py, tests/test_pathsel.py |
| N-000138 | implemented, tested | parser.py, tests/test_pathsel.py |
| N-000139 | implemented | parser.py |
| N-000140 | implemented, tested | parser.py, tests/test_pathsel.py |
| N-000141 | implemented, tested | parser.py, tests/test_pathsel.py |
| N-000142 | implemented, tested | nodes.py, parser.py, tests/test_pathsel.py |
| N-000143 | implemented | parser.py |
| N-000144 | implemented | parser.py |
| N-000145 | implemented, tested | parser.py, tests/test_pathsel.py |
| N-000146 | implemented | parser.py |
| N-000147 | implemented, tested | parser.py, tests/test_pathsel.py |
| N-000148 | implemented, tested | parser.py, tests/test_pathsel.py |
| N-000149 | implemented | parser.py |
| N-000150 | implemented, tested | parser.py, tests/test_pathsel.py |
| N-000151 | implemented, tested | parser.py, tests/test_pathsel.py |
| N-000152 | implemented | errors.py, parser.py |
| N-000153 | implemented | errors.py, parser.py |
| N-000154 | implemented | errors.py, parser.py |
| N-000155 | implemented, tested | parser.py, tests/test_pathsel.py |
| N-000156 | implemented, tested | parser.py, tests/test_pathsel.py |
| N-000157 | implemented, tested | parser.py, tests/test_pathsel.py |

### Pack 09 — 09-full-prd--fp-04-wildcard-and-filter-projections.md

| id | status | where |
|---|---|---|
| N-000158 | implemented | parser.py |
| N-000159 | implemented, tested | parser.py, tests/test_pathsel.py |
| N-000160 | implemented | parser.py |
| N-000161 | implemented | parser.py |
| N-000162 | implemented, tested | parser.py, tests/test_pathsel.py |
| N-000163 | implemented, tested | parser.py, tests/test_pathsel.py |
| N-000164 | tested | tests/test_spec_ids.py |
| N-000165 | implemented, tested | nodes.py, tests/test_pathsel.py |
| N-000166 | tested | tests/test_pathsel.py |
| N-000167 | tested | tests/test_pathsel.py |
| N-000168 | implemented, tested | parser.py, tests/test_pathsel.py |
| N-000169 | implemented | parser.py |
| N-000170 | implemented | parser.py |
| N-000171 | implemented | parser.py |
| N-000172 | implemented | parser.py |
| N-000173 | implemented, tested | parser.py, tests/test_pathsel.py |
| N-000174 | tested | tests/test_pathsel.py |
| N-000175 | tested | tests/test_spec_ids.py |
| N-000176 | tested | tests/test_spec_ids.py |
| N-000177 | tested | tests/test_spec_ids.py |
| N-000178 | tested | tests/test_spec_ids.py |
| N-000179 | tested | tests/test_pathsel.py |
| N-000180 | tested | tests/test_pathsel.py |
| N-000181 | tested | tests/test_pathsel.py |
| N-000182 | tested | tests/test_spec_ids.py |
| N-000183 | implemented | parser.py |
| N-000184 | implemented | parser.py |
| N-000185 | implemented, tested | parser.py, tests/test_pathsel.py |
| N-000186 | implemented | parser.py |
| N-000187 | implemented | parser.py |
| N-000188 | implemented | parser.py |
| N-000189 | implemented | parser.py |
| N-000190 | implemented, tested | parser.py, tests/test_pathsel.py |
| N-000191 | tested | tests/test_spec_ids.py |
| N-000192 | implemented | parser.py |
| N-000193 | implemented | parser.py |
| N-000194 | implemented | parser.py |
| N-000195 | tested | tests/test_pathsel.py |
| N-000196 | tested | tests/test_spec_ids.py |
| N-000197 | tested | tests/test_pathsel.py |
| N-000198 | implemented | parser.py |
| N-000199 | implemented | parser.py |
| N-000200 | implemented, tested | parser.py, tests/test_pathsel.py |
| N-000201 | implemented, tested | parser.py, tests/test_pathsel.py |
| N-000202 | implemented, tested | nodes.py, tests/test_pathsel.py, tests/test_spec_ids.py |
| N-000203 | tested | tests/test_spec_ids.py |
| N-000204 | tested | tests/test_pathsel.py, tests/test_spec_ids.py |
| N-000205 | tested | tests/test_pathsel.py |

### Pack 10 — 10-full-prd--fp-05-construct-results-pipe-current-val.md

| id | status | where |
|---|---|---|
| N-000206 | implemented, tested | parser.py, tests/test_pathsel.py |
| N-000207 | implemented | parser.py |
| N-000208 | implemented | parser.py |
| N-000209 | implemented | parser.py |
| N-000210 | implemented, tested | parser.py, tests/test_pathsel.py |
| N-000211 | tested | tests/test_pathsel.py |
| N-000212 | tested | tests/test_pathsel.py |
| N-000213 | implemented, tested | parser.py, tests/test_pathsel.py |
| N-000214 | implemented | parser.py |
| N-000215 | implemented | parser.py |
| N-000216 | implemented | parser.py |
| N-000217 | implemented | parser.py |
| N-000218 | implemented, tested | nodes.py, parser.py, tests/test_pathsel.py |
| N-000219 | implemented, tested | lexer.py, parser.py, tests/test_pathsel.py |
| N-000220 | implemented | parser.py |
| N-000221 | implemented | parser.py |
| N-000222 | implemented, tested | parser.py, tests/test_pathsel.py |
| N-000223 | implemented, tested | lexer.py, parser.py, tests/test_pathsel.py, tests/test_spec_ids.py |
| N-000224 | implemented | lexer.py |
| N-000225 | implemented, tested | lexer.py, nodes.py, tests/test_spec_ids.py |
| N-000226 | implemented, tested | lexer.py, nodes.py, tests/test_pathsel.py, tests/test_spec_ids.py |
| N-000227 | implemented, tested | lexer.py, nodes.py, parser.py, tests/test_pathsel.py |
| N-000228 | implemented | lexer.py |
| N-000229 | implemented | lexer.py |
| N-000230 | implemented, tested | lexer.py, tests/test_pathsel.py |
| N-000231 | implemented, tested | lexer.py, parser.py, tests/test_pathsel.py |
| N-000232 | implemented | parser.py |
| N-000233 | implemented | parser.py |
| N-000234 | implemented | parser.py |
| N-000235 | implemented | parser.py |
| N-000236 | implemented, tested | parser.py, tests/test_pathsel.py |
| N-000237 | implemented, tested | lexer.py, tests/test_pathsel.py |
| N-000238 | implemented, tested | parser.py, tests/test_pathsel.py |
| N-000239 | implemented, tested | lexer.py, tests/test_pathsel.py |
| N-000240 | implemented, tested | parser.py, tests/test_pathsel.py |
| N-000241 | tested | tests/test_pathsel.py |

### Pack 11 — 11-full-prd--fp-06-compare-values-and-combine-them-wi.md

| id | status | where |
|---|---|---|
| N-000242 | implemented, tested | nodes.py, parser.py, tests/test_pathsel.py, values.py |
| N-000243 | implemented | nodes.py, parser.py, values.py |
| N-000244 | implemented, tested | parser.py, tests/test_pathsel.py, values.py |
| N-000245 | implemented, tested | lexer.py, nodes.py, parser.py, tests/test_pathsel.py |
| N-000246 | implemented, tested | nodes.py, tests/test_pathsel.py |
| N-000247 | implemented, tested | lexer.py, nodes.py, parser.py, tests/test_pathsel.py |
| N-000248 | implemented | nodes.py, parser.py |
| N-000249 | implemented | nodes.py, parser.py |
| N-000250 | implemented, tested | nodes.py, parser.py, tests/test_pathsel.py |
| N-000251 | implemented, tested | lexer.py, nodes.py, tests/test_pathsel.py, values.py |
| N-000252 | implemented, tested | nodes.py, tests/test_pathsel.py, values.py |
| N-000253 | implemented, tested | parser.py, tests/test_pathsel.py |
| N-000254 | implemented | parser.py, values.py |
| N-000255 | implemented | parser.py, values.py |
| N-000256 | implemented | parser.py, values.py |
| N-000257 | implemented, tested | parser.py, tests/test_pathsel.py, values.py |
| N-000258 | implemented, tested | nodes.py, tests/test_pathsel.py |
| N-000259 | implemented, tested | nodes.py, tests/test_pathsel.py |
| N-000260 | implemented, tested | lexer.py, tests/test_pathsel.py |
| N-000261 | tested | tests/test_pathsel.py |

### Pack 12 — 12-full-prd--fp-07-call-built-in-functions.md

| id | status | where |
|---|---|---|
| N-000262 | implemented, tested | evaluator.py, functions.py, parser.py, tests/test_pathsel.py |
| N-000263 | tested | tests/test_pathsel.py |
| N-000264 | implemented, tested | errors.py, parser.py, tests/test_pathsel.py |
| N-000265 | implemented | errors.py |
| N-000266 | implemented, tested | errors.py, tests/test_pathsel.py |
| N-000267 | tested | tests/test_pathsel.py |
| N-000268 | tested | tests/test_pathsel.py |
| N-000269 | implemented, tested | functions.py, tests/test_pathsel.py |
| N-000270 | implemented, tested | functions.py, tests/test_pathsel.py |
| N-000271 | implemented, tested | functions.py, tests/test_pathsel.py |
| N-000272 | implemented, tested | functions.py, tests/test_pathsel.py |
| N-000273 | implemented | functions.py |
| N-000274 | implemented, tested | functions.py, tests/test_pathsel.py |
| N-000275 | implemented, tested | functions.py, tests/test_pathsel.py |
| N-000276 | implemented, tested | functions.py, tests/test_pathsel.py |
| N-000277 | implemented, tested | functions.py, tests/test_pathsel.py |
| N-000278 | implemented, tested | functions.py, tests/test_pathsel.py |
| N-000279 | implemented, tested | functions.py, tests/test_pathsel.py |
| N-000280 | implemented, tested | functions.py, tests/test_pathsel.py |
| N-000281 | implemented, tested | functions.py, tests/test_pathsel.py |
| N-000282 | implemented, tested | functions.py, tests/test_pathsel.py |
| N-000283 | implemented, tested | functions.py, tests/test_pathsel.py |
| N-000284 | implemented, tested | functions.py, tests/test_pathsel.py |
| N-000285 | implemented, tested | functions.py, tests/test_pathsel.py |
| N-000286 | implemented, tested | functions.py, tests/test_pathsel.py |
| N-000287 | implemented | functions.py |
| N-000288 | implemented | functions.py |
| N-000289 | implemented, tested | functions.py, tests/test_pathsel.py |
| N-000290 | implemented, tested | functions.py, tests/test_pathsel.py |
| N-000291 | implemented | functions.py |
| N-000292 | implemented, tested | functions.py, tests/test_pathsel.py |
| N-000293 | implemented, tested | functions.py, tests/test_pathsel.py |
| N-000294 | implemented, tested | functions.py, tests/test_pathsel.py |
| N-000295 | implemented, tested | functions.py, tests/test_pathsel.py |
| N-000296 | implemented | functions.py |
| N-000297 | implemented, tested | functions.py, tests/test_pathsel.py |
| N-000298 | implemented, tested | functions.py, tests/test_pathsel.py |
| N-000299 | implemented | functions.py |
| N-000300 | implemented, tested | functions.py, tests/test_pathsel.py |
| N-000301 | implemented, tested | functions.py, tests/test_pathsel.py |
| N-000302 | implemented, tested | functions.py, tests/test_pathsel.py |
| N-000303 | implemented, tested | functions.py, tests/test_pathsel.py |
| N-000304 | implemented | functions.py |
| N-000305 | implemented, tested | functions.py, tests/test_pathsel.py |
| N-000306 | implemented, tested | functions.py, tests/test_pathsel.py |
| N-000307 | implemented | functions.py |
| N-000308 | implemented, tested | functions.py, tests/test_pathsel.py |
| N-000309 | implemented, tested | parser.py, tests/test_pathsel.py |
| N-000310 | tested | tests/test_pathsel.py |
| N-000311 | implemented, tested | errors.py, functions.py, tests/test_pathsel.py |
| N-000312 | implemented | errors.py, functions.py |
| N-000313 | implemented, tested | errors.py, functions.py, tests/test_pathsel.py |
| N-000314 | implemented, tested | errors.py, functions.py, tests/test_pathsel.py |
| N-000315 | implemented | errors.py, functions.py |
| N-000316 | implemented | errors.py, functions.py |
| N-000317 | implemented, tested | errors.py, functions.py, tests/test_pathsel.py |
| N-000318 | implemented | errors.py, functions.py, values.py |
| N-000319 | implemented | errors.py, functions.py, values.py |
| N-000320 | implemented, tested | errors.py, functions.py, tests/test_pathsel.py, values.py |
| N-000321 | implemented, tested | parser.py, tests/test_pathsel.py |
| N-000322 | implemented, tested | parser.py, tests/test_pathsel.py |

### Pack 13 — 13-full-prd--fp-08-evaluation-options-for-constructed.md

| id | status | where |
|---|---|---|
| N-000323 | tested | tests/test_pathsel.py |
| N-000324 | tested | tests/test_spec_ids.py |
| N-000325 | tested | tests/test_spec_ids.py |
| N-000326 | tested | tests/test_spec_ids.py |
| N-000327 | tested | tests/test_pathsel.py |
| N-000328 | implemented, tested | evaluator.py, tests/test_pathsel.py |
| N-000329 | implemented | evaluator.py |
| N-000330 | implemented | evaluator.py |
| N-000331 | implemented | evaluator.py |
| N-000332 | implemented | evaluator.py |
| N-000333 | implemented | evaluator.py |
| N-000334 | implemented, tested | evaluator.py, tests/test_pathsel.py |
| N-000335 | tested | tests/test_pathsel.py |
| N-000336 | implemented | functions.py |
| N-000337 | implemented | functions.py |
| N-000338 | implemented, tested | tests/test_pathsel.py, values.py |
| N-000339 | tested | tests/test_pathsel.py, tests/test_spec_ids.py |
| N-000340 | tested | tests/test_pathsel.py, tests/test_spec_ids.py |
| N-000341 | tested | tests/test_pathsel.py |
| N-000342 | tested | tests/test_pathsel.py |
| N-000343 | tested | tests/test_pathsel.py |
| N-000344 | implemented, tested | errors.py, evaluator.py, tests/test_pathsel.py |
| N-000345 | tested | tests/test_pathsel.py |
| N-000346 | tested | tests/test_spec_ids.py |
| N-000347 | tested | tests/test_spec_ids.py |
| N-000348 | tested | tests/test_spec_ids.py |
| N-000349 | tested | tests/test_pathsel.py |
| N-000350 | tested | tests/test_pathsel.py |

### Pack 14 — 14-hardware-requirements--hardware-requirements.md

No nodes (informational block).

### Pack 15 — 15-hardware-requirements--summary.md

| id | status | where |
|---|---|---|
| N-000351 | tested | tests/test_spec_ids.py |
| N-000352 | tested | tests/test_spec_ids.py |
| N-000353 | tested | tests/test_spec_ids.py |
| N-000354 | not done | host statement (x86_64/arm64 Linux, macOS, Windows); no code effect; arm64 not run here |

### Pack 16 — 16-hardware-requirements--execution-profiles.md

| id | status | where |
|---|---|---|
| N-000355 | tested | tests/test_spec_ids.py |
| N-000356 | not done | platform list as N-000053; only Linux was run here |
| N-000357 | tested | tests/test_spec_ids.py |
| N-000358 | tested | tests/test_spec_ids.py |
| N-000359 | tested | tests/test_spec_ids.py |
| N-000360 | tested | tests/test_spec_ids.py |
| N-000361 | tested | tests/test_spec_ids.py |
| N-000362 | tested | tests/test_spec_ids.py |
| N-000363 | tested | tests/test_spec_ids.py |
| N-000364 | tested | tests/test_spec_ids.py |
| N-000365 | implemented (not exercised) | pyproject.toml supports an editable install from the root |

### Pack 17 — 17-interface-contract--product-form.md

| id | status | where |
|---|---|---|
| N-000366 | tested | tests/test_spec_ids.py |
| N-000367 | tested | tests/test_spec_ids.py |
| N-000368 | tested | tests/test_spec_ids.py |

### Pack 18 — 18-interface-contract--layout.md

| id | status | where |
|---|---|---|
| N-000369 | tested | tests/test_pathsel.py |
| N-000370 | tested | tests/test_spec_ids.py |
| N-000371 | tested | tests/test_pathsel.py, tests/test_spec_ids.py |

### Pack 19 — 19-interface-contract--pathsel.md

| id | status | where |
|---|---|---|
| N-000372 | implemented | __init__.py |
| N-000373 | implemented | __init__.py |
| N-000374 | implemented (choice) | extra root names: errors, Functions, signature, ExpressionReference, Parsed |

### Pack 20 — 20-interface-contract--pathsel-search.md

| id | status | where |
|---|---|---|
| N-000375 | implemented | __init__.py |
| N-000376 | implemented | __init__.py |
| N-000377 | implemented | __init__.py |
| N-000378 | implemented | __init__.py |
| N-000379 | implemented | __init__.py |
| N-000380 | implemented | __init__.py |
| N-000381 | implemented | __init__.py |
| N-000382 | implemented | __init__.py |

### Pack 21 — 21-interface-contract--pathsel-compile.md

| id | status | where |
|---|---|---|
| N-000383 | implemented | __init__.py |
| N-000384 | implemented | __init__.py |
| N-000385 | implemented | __init__.py |
| N-000386 | implemented | evaluator.py |
| N-000387 | implemented | evaluator.py |
| N-000388 | implemented | evaluator.py |

### Pack 22 — 22-interface-contract--evaluation-options.md

| id | status | where |
|---|---|---|
| N-000389 | implemented, tested | evaluator.py, tests/test_pathsel.py |
| N-000390 | implemented | evaluator.py |
| N-000391 | implemented | evaluator.py |
| N-000392 | implemented, tested | evaluator.py, tests/test_pathsel.py |

### Pack 23 — 23-interface-contract--pathsel-functions.md

| id | status | where |
|---|---|---|
| N-000393 | implemented | functions.py |
| N-000394 | implemented | functions.py |
| N-000395 | implemented | functions.py |
| N-000396 | implemented | functions.py |
| N-000397 | implemented | functions.py |
| N-000398 | implemented | functions.py |
| N-000399 | implemented | functions.py |
| N-000400 | implemented | functions.py |
| N-000401 | implemented | functions.py, values.py |
| N-000402 | implemented | functions.py, values.py |
| N-000403 | implemented, tested | functions.py, tests/test_pathsel.py |
| N-000404 | implemented | functions.py |

### Pack 24 — 24-interface-contract--failure-carriers.md

| id | status | where |
|---|---|---|
| N-000405 | tested | tests/test_pathsel.py |
| N-000406 | tested | tests/test_spec_ids.py |
| N-000407 | decision (implemented) | type names: EmptyExpressionError, IncompleteExpressionError, PathSelSyntaxError, PathSelTokenSyntaxError, ZeroSliceStepError, UnknownFunctionError, InvalidArityError, InvalidTypeError |
| N-000408 | decision (implemented) | report text is free; messages are informational |
| N-000409 | implemented, tested | errors.py, tests/test_pathsel.py |
| N-000410 | implemented, tested | errors.py, tests/test_pathsel.py |
| N-000411 | implemented | errors.py |
| N-000412 | implemented | errors.py |
| N-000413 | implemented | errors.py |
| N-000414 | implemented | errors.py |
| N-000415 | implemented, tested | errors.py, tests/test_pathsel.py |
| N-000416 | implemented | errors.py |
| N-000417 | implemented | errors.py, functions.py |
| N-000418 | implemented | errors.py, functions.py |
| N-000419 | implemented | errors.py, functions.py |
| N-000420 | tested | tests/test_spec_ids.py |
| N-000421 | implemented, tested | errors.py, tests/test_pathsel.py |
| N-000422 | implemented, tested | errors.py, tests/test_pathsel.py |

### Pack 25 — 25-interface-contract--expression-reference-value.md

| id | status | where |
|---|---|---|
| N-000423 | tested | tests/test_spec_ids.py |

