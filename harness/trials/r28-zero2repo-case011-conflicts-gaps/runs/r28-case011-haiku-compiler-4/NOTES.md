# NOTES — pathsel build

Scope: the `pathsel` library (flat layout at `/app/pathsel`), tests in `/app/tests`,
packaging in `/app/pyproject.toml`. `spec/` is untouched. No CLI, no network, no
configuration file (Interface Contract, N-000366..N-000368).

Verification: `python3 -m pytest -q tests` → 184 passed on Python 3.13. The package
also imports and runs on Python 3.11 (smoke check only). A Python 3.9 interpreter is
not available here, so the stated 3.9 floor is not run; the code uses only 3.9-compatible
syntax (`from __future__ import annotations`, no `match`, no `X | Y` hints).

---

## 1. Conflicts in the specification

The export lists seven UNSETTLED contradictions (CF-000005, 007, 011, 015, 027, 035, 049).
The rows below give both sides, where they are, and what was built. Where a conflict
was not in the export, that is marked "not flagged".

### Flagged by the export

**CF-000005 — filter on a non-array.**
- Side A: FP-04 Boundary, "A filter on a non-array yields null, not an empty array and not a failure." (N-000202)
- Side B: FP-06 Boundary, "A filter applied to anything but an array yields the empty array." (N-000259)
- **Built:** null. FP-04 is the feature point that defines filters.

**CF-000007 — slice of a non-array.**
- Side A: FP-03 Normal, "A slice on a value that is not an array yields null." (N-000142)
- Side B: FP-03 Boundary, "A slice of a value that is not an array is the empty array." (N-000157)
- **Built:** null. The normal-behaviour bullet is the primary rule; it also matches the list wildcard and filter.

**CF-000011 — multiselect list on a null current value.**
- Side A: FP-05 Normal, "On a null current value it still builds one element per expression." (N-000212)
- Side B: FP-05 Normal, "A multiselect list or hash whose current value is null yields null." (N-000218)
- **Built:** null for both the list and the hash. N-000218 covers both forms; N-000212 names only the list.

**CF-000015 — `not_null` and empty values.**
- Side A: Terminology, "An empty string or an empty array counts as null for `not_null`." (N-000022)
- Side B: FP-07 `not_null`, "(an empty array or empty string is not null)." (N-000300)
- **Built:** B. `not_null` returns the first argument that is not null, so `""` and `[]` count as values. The function's own definition wins over the general term.

**CF-000027 — object wildcard on a non-object.**
- Side A: Terminology Projection/Object-wildcard, "An object wildcard applied to a non-object is the empty array." (N-000031)
- Side B: FP-04 Normal, "An object wildcard on a value that is not an object yields null." (N-000165)
- **Built:** null. This matches the feature-point rule and the list wildcard.

**CF-000035 — string length.**
- Side A: Terminology String, "its length is its number of UTF-8 bytes." (N-000026)
- Side B: FP-07 `length`, "the number of Unicode characters (not bytes) of a string" (N-000277)
- **Built:** code points (`len(str)`). The function's explicit wording wins; the byte rule is not applied anywhere.

**CF-000049 — escapes in raw strings.**
- Side A: FP-05 Normal, "No JSON escapes are processed." (N-000227)
- Side B: FP-05 Boundary, "A `\uXXXX` escape inside a raw string literal is decoded to its character." (N-000239)
- **Built:** `\uXXXX` is decoded, the pair `\'` gives `'`, and every other backslash is kept literally. B is the more specific rule.

### Not flagged by the export

**`join` of an empty array.**
- FP-07 paragraph, "`join` of an empty array yields null." (N-000268)
- FP-07 definition, "the empty array yields the empty string." (N-000280)
- **Built:** null. The explicit sentence was written for this case.

**Expression reference evaluated on its own.**
- Terminology "Expression reference": "Outside a function argument it evaluates to null."
- FP-05 (N-000231..N-000236): "Searching an expression reference on its own succeeds and yields a non-null value"; Interface Contract (N-000423): "returns a non-`None` value".
- **Built:** a non-null `ExpressionReference` object. Two normative places say non-null; the terminology row is descriptive.

---

## 2. Gaps: things the spec does not state, and what was assumed

Each item names where I looked and what I chose.

**Expression grammar and tokens**
- *Numbers are not operands.* Numbers appear only inside brackets (index and slice parts), so `foo(1)` or a bare `5` is a syntax failure. JSON literals (`` `1` ``) are the way to write numbers as values. The spec says a dot followed by a number is syntax (N-000117) but says nothing about a bare number.
- *Function call as a step after a dot.* FP-07 (N-000309) says a function call may be a projection's right-hand side, which the step rules in FP-04 can only reach through a dot. So `people[*].length(@)` and `a.length(@)` are accepted; the call gets the value before the dot as its current value.
- *Slice after an index or slice.* FP-04 leaves this to the implementer. A slice here always starts a projection.
- *Dot then multiselect as a projection RHS.* FP-04 leaves whether later steps join this RHS to the implementer. They do join: `people[*].{f: first}.f` gives `['J', 'K']` (`.f` applies per element). A multiselect list (`[first, age]`) builds an array, so `.x` after it is null.
- *Multiselect list as the first step of a projection RHS.* Allowed, as FP-05 says: `people[*][first, age]`.
- *Whitespace.* Only space, tab, LF and CR. Other characters (vertical tab, NBSP) begin no token and are token-level failures.
- *Identifiers.* ASCII letters, underscore, then ASCII letters, digits, underscore.
- *Lone `?`.* It is a grammar token (only meaningful after `[`); a lone `?` is a grammar-level failure, not token-level.
- *`[ ]` with a space inside.* Same as `[]` (flatten), since spaces are allowed between tokens.
- *Empty text vs whitespace.* Zero-length text is the empty kind (no `lex_position`). Whitespace-only text is the incomplete kind, with `lex_position` equal to the text length.
- *Incomplete vs syntax at end of text.* End of text where an operand or a closing token is still needed is incomplete. A dot followed by the end of text is a syntax failure (FP-01 says so explicitly).
- *Which failure is reported first.* Errors are reported in text order. A token-level failure is raised only when the parser reaches it, so an earlier grammar failure wins.
- *Backtick literal end.* The literal ends at the first unescaped backtick; `\`` inside the literal stands for a backtick. A literal that is not JSON is read as JSON string content after stripping leading whitespace (FP-05). NaN and Infinity are not JSON here, so they fall back to strings.
- *Raw string end.* Ends at the first unescaped `'`; `\'` is a quote.
- *Quoted identifier.* Decoded with Python's strict `json.loads`, so a raw control character inside is a token-level failure.
- *Zero slice step.* Refused at compile time (both entries). FP-03 allows either.
- *Logic binding.* Comparisons are left-associative. `!` nests (`!!a`).
- *Expression reference extent.* `&` takes an operand up to the end of the enclosing argument, element, parenthesis or expression, including pipes.

**Evaluation**
- *Ordering across unlike types* (`` `1` < `"b"` ``). The spec gives numbers and strings only; I return null, the way the null-as-no-result rule works elsewhere.
- *Projection results.* Each projection returns a fresh list. Nulls are dropped.
- *Object wildcard and filter on the document itself* (`*.x`, `[?x]`) follow the same rules as any other value.
- *Input document.* Never mutated; results can share sub-objects with the input.
- *Literals.* Deep-copied on each evaluation, so a caller cannot change a literal through its result.

**Built-in functions**
- `avg` returns a float (true division). `avg([])` is null (FP-07). `sum([])` is 0 (not stated).
- `ceil` and `floor` return `int`.
- `type(v)` for a host value outside the six JSON types returns null (not stated).
- `to_string` of a non-string uses compact JSON (`,` and `:` with no spaces, `\uXXXX` for non-ASCII, `ensure_ascii`). Host values that are not JSON use `str()`; `Decimal` becomes a float.
- `to_number`: an integer numeral is `-?[0-9]+`; a float numeral is `-?` digits with a decimal point and/or exponent (`1.`, `.5`, `1e3`). No leading `+`, no whitespace. `true`, `null`, arrays and objects give null.
- `to_array` returns a list unchanged; a tuple becomes a list; anything else is wrapped.
- `merge` returns a plain `dict`, whatever the mapping type option.
- `contains` on a string needs a string second argument; otherwise it is invalid-type.
- `length` takes a string, an array or an object; anything else is invalid-type.
- Built-in argument types are checked before the function runs; `null` from a missing field counts as a wrong type for an array argument.

**Options and custom functions**
- `dict_cls` is used for multiselect hashes only. It must be constructible with no arguments and accept item assignment. Field access, wildcards, filters, comparisons and truthiness treat its instances as objects (FP-08 N-000330).
- `custom_functions` may be None.
- Built-in names always resolve to the built-in implementation; a provider method with a built-in name is ignored. (FP-08 requires built-ins to keep unchanged behaviour.)
- `signature(...)` raises `TypeError` for a malformed specification or an unknown type name. The spec does not say what happens there.
- Custom function arity and type checks follow the same order and error kinds as built-ins.

**Errors**
- Message text is free-form (N-000061).
- `lex_position` appears only on syntax and incomplete failures (N-000421, N-000422).

---

## 3. Public names beyond the required ones

`pathsel` exports, besides `search` and `compile` (N-000372, N-000373): `ParsedExpression`, `Functions`, `signature` and every refusal class. Interface Contract N-000374 leaves other root names to the implementer; the refusal classes are there so callers can catch the kind by type.

Refusal classes (all `ValueError` subclasses; each in `pathsel/errors.py`):
`EmptyExpressionError`, `IncompleteExpressionError`, `PathSelSyntaxError`, `TokenSyntaxError` (subclass of `PathSelSyntaxError`), `ZeroSliceStepError`, `UnknownFunctionError`, `InvalidArityError`, `InvalidTypeError`. All share the base `PathSelError`.

---

## 4. Traceability (every id in `spec/CHECKLIST.md`)

The checklist has 423 ids (N-000001..N-000423). Each pack claims a contiguous range (pack 14 claims none), so statuses are given per range. Code carries a `# spec: <range>` marker beside the code that satisfies it. "Tested" means a test in `tests/test_pathsel.py` checks the behaviour (test names are prefixed with the feature point, e.g. `test_FP03_…`).

| Pack | Source | Ids | Status | Where / test |
|---|---|---|---|---|
| 01 | Product overview | N-000001..013 | implemented, tested | `__init__.py` (`search`, `compile`); `test_FP01_*` |
| 02 | Terminology | N-000014..037 | implemented, tested | `values.py`, `builtins.py`, `nodes.py`; `test_FP0x_*` |
| 03 | Public surface | N-000038..049 | implemented, tested | `__init__.py`; `test_FP01_*`, `test_pathsel_root_exposes_entries` |
| 04 | Non-functional constraints | N-000050..066 | implemented, tested | zero deps (`pyproject.toml`); `test_NFR_*`, `test_FP24_*` |
| 05 | Non-goals | N-000067..072 | implemented (N-000071 is a decision; no code needed) | no JSON reader, no CLI, no mutation (`test_NFR_input_document_not_mutated`) |
| 06 | FP-01 search and compile | N-000073..106 | implemented, tested | `parser.py`, `__init__.py`; `test_FP01_*` |
| 07 | FP-02 identifiers | N-000107..125 | implemented, tested | `lexer.py`, `parser.py` (`dot_step`), `nodes.Field`; `test_FP02_*` |
| 08 | FP-03 index, slice, flatten | N-000126..157 | implemented, tested | `parser.py` (`index_body`), `nodes.py` (`Index`, `SliceProj`, `FlattenProj`, `slice_indices`); `test_FP03_*` |
| 09 | FP-04 wildcards, filters, projection reach | N-000158..205 | implemented, tested | `nodes.py` (`_Projection`, `ListProj`, `ObjProj`, `FilterProj`), `parser.py` (`rhs`); `test_FP04_*` |
| 10 | FP-05 constructs, pipe, literals | N-000206..241 | implemented, tested | `nodes.py` (`MultiList`, `MultiHash`, `Pipe`, `ExprRef`), `lexer.py` (literals); `test_FP05_*` |
| 11 | FP-06 comparisons and logic | N-000242..261 | implemented, tested | `nodes.py` (`Compare`, `And`, `Or`, `Not`), `values.py`; `test_FP06_*` |
| 12 | FP-07 built-in functions | N-000262..322 | implemented, tested | `builtins.py`, `nodes.FuncCall`; `test_FP07_*` |
| 13 | FP-08 options and custom functions | N-000323..350 | implemented, tested | `values.Context`, `nodes.MultiHash`, `builtins._custom_function`; `test_FP08_*` |
| 14 | Hardware requirements (intro) | none | no claims | — |
| 15 | Hardware summary | N-000351..354 | implemented | pure Python, no deps (`pyproject.toml`) |
| 16 | Execution profile `cpu_baseline` | N-000355..365 | implemented | flat layout at `/app/pathsel`; setuptools `pyproject.toml`, no native step |
| 17 | Product form | N-000366..368 | implemented | no `__main__`, no CLI, no service |
| 18 | Layout | N-000369..371 | implemented | package `pathsel` at repository root; import does no I/O |
| 19 | `pathsel` names | N-000372..374 | implemented, tested | `pathsel/__init__.py`; `test_pathsel_root_exposes_entries` |
| 20 | `pathsel.search` | N-000375..382 | implemented, tested | `__init__.search`; `test_FP01_*`, `test_FP08_*` |
| 21 | `pathsel.compile` and parsed `.search` | N-000383..388 | implemented, tested | `__init__.compile`, `ParsedExpression`; `test_FP01_parsed_expression_reused_on_many_documents` |
| 22 | Evaluation options attributes | N-000389..392 | implemented, tested | `values.context_from_options`; `test_FP08_mapping_type_applies_to_constructed_hash` |
| 23 | `pathsel.functions` | N-000393..404 | implemented, tested | `pathsel/functions.py` (`Functions`, `signature`), `builtins._custom_function`; `test_FP08_custom_*`, `test_FP08_signature_*` |
| 24 | Failure carriers | N-000405..422 | implemented, tested | `pathsel/errors.py`; `test_FP24_*`, plus the `test_FP01_*` kind tests |
| 25 | Expression reference value | N-000423 | implemented, tested | `nodes.ExprRef`; `test_FP25_expression_reference_value_is_not_none` |

**Not done:** nothing in the checklist is left undone. The explicit non-goals (CLI, JSON reader, throughput target, later language revision) are out of scope by the spec itself.

---

## 5. Files

- `pathsel/__init__.py` — `search`, `compile`, `ParsedExpression`, public names.
- `pathsel/errors.py` — refusal classes.
- `pathsel/values.py` — type tests, truthiness, JSON equality, ordering, evaluation context.
- `pathsel/lexer.py` — tokenizer (token-level failures).
- `pathsel/parser.py` — Pratt parser with the spec's binding powers and projection right-hand-side rule.
- `pathsel/nodes.py` — expression tree and evaluation.
- `pathsel/builtins.py` — the 26 built-in functions, their argument checks, and provider lookup.
- `pathsel/functions.py` — `Functions` base class and `signature`.
- `tests/test_pathsel.py` — feature-point tests (184 cases with parametrization).
- `pyproject.toml` — setuptools packaging, zero runtime dependencies.
