# NOTES

Implementation of PathSel (`pathsel` package) from `spec/`. Layout follows
Interface Contract "Layout": flat package `pathsel/` at the repository root,
no runtime dependencies (`pyproject.toml`, setuptools). No build step.

Run the tests with `python -m pytest -q tests` (94 tests, all passing on
CPython 3.13 here; code avoids 3.10+ syntax, but only 3.13 was run).

## Modules

| File | Role |
|---|---|
| `pathsel/__init__.py` | Public names: `search`, `compile`, the error classes. |
| `pathsel/core.py` | `compile` (parse once, `ParsedExpression.search`) and one-shot `search`. |
| `pathsel/lexer.py` | Tokenizer, on demand, so token-level failures appear in text order. |
| `pathsel/parser.py` | Pratt parser; binding powers implement the FP-04 projection ranking and FP-06 binding of `!`. |
| `pathsel/nodes.py` | Expression tree and evaluation; projections, filters, slices, function dispatch. |
| `pathsel/values.py` | JSON type predicates, truthiness, deep equality, the expression-reference value. |
| `pathsel/functions.py` | Built-ins (FP-07), `Functions` provider class, `signature` decorator. |
| `pathsel/errors.py` | Failure carriers (all `ValueError`). |
| `tests/test_pathsel.py` | Tests written from the spec. |

Code carries `# spec: N-...` comments beside the code that satisfies each
paragraph; ids come from the `↳` lines in `spec/packs/*.md`.

## Conflicts in the specification

### The seven unsettled contradictions (MAP.md: CF-000005, 007, 011, 015, 027, 035, 049)

MAP.md says these have no human verdict. I chose one side for each.

1. **CF-000005, filter on a non-array.** `spec/packs/09-…` (FP-04, N-000202): "A filter on a non-array yields null, not an empty array and not a failure." vs `spec/packs/11-…` (FP-06, N-000259): "A filter applied to anything but an array yields the empty array." **Built: null.** The FP-04 text names this case directly and rules out the empty array.
2. **CF-000007, slice on a non-array.** `spec/packs/08-…` (FP-03, N-000142): "A slice on a value that is not an array yields null." vs N-000157: "A slice of a value that is not an array is the empty array." **Built: null**, matching index and flatten on non-arrays.
3. **CF-000011, multiselect list or hash with a null current value.** `spec/packs/10-…` (FP-05, N-000212): "On a null current value it still builds one element per expression." vs N-000218: "A multiselect list or hash whose current value is null yields null." **Built: null.**
4. **CF-000015, `not_null` and empty values.** `spec/packs/02-…` (Terminology, N-000022): an empty string or empty array "counts as null for `not_null`" vs `spec/packs/12-…` (FP-07, N-000300): "an empty array or empty string is not null". **Built: not null**, the operative FP-07 definition of `not_null`.
5. **CF-000027, object wildcard on a non-object.** `spec/packs/02-…` (Terminology, N-000031): "An object wildcard applied to a non-object is the empty array." vs `spec/packs/09-…` (FP-04, N-000165): "An object wildcard on a value that is not an object yields null." **Built: null.**
6. **CF-000035, string length.** `spec/packs/02-…` (Terminology, N-000026): length "is its number of UTF-8 bytes" vs `spec/packs/12-…` (FP-07, N-000277): "the number of Unicode characters (not bytes)". **Built: Unicode code points** (Python `len`), since the FP-07 definition is explicit about it.
7. **CF-000049, escapes in raw string literals.** `spec/packs/10-…` (FP-05, N-000227): "No JSON escapes are processed." vs N-000239: a `\uXXXX` escape in a raw string "is decoded to its character". **Built:** `\'` gives a quote, `\uXXXX` gives its character, and any other backslash is literal.

### Conflicts not listed in MAP.md

8. **`join` of an empty array.** `spec/packs/12-…` FP-07 bullet (N-000279, N-000280): "the empty array yields the empty string." vs the FP-07 paragraph before the bullets (N-000264–N-000268): "`join` of an empty array yields null." **Built: `""`** (the definition bullet). Reversing this is a one-line change in `_b_join` (`functions.py`).
9. **Expression reference outside a function argument.** `spec/packs/02-…` (Terminology, "Expression reference"): "Outside a function argument it evaluates to null." vs `spec/packs/10-…` (FP-05, N-000231–N-000236): searching a bare reference "yields a non-null value", and `spec/packs/25-…` (Interface, N-000423): "returns a non-`None` value of the implementer's choice". **Built: a non-null `Reference` object** (two statements agree on this).
10. **Step 0 in a slice.** `spec/packs/08-…` (FP-03, N-000131–N-000133): "A step of 0 selects nothing: the result is the empty array." vs N-000152–N-000154 (FP-03 boundary): a zero step "does not succeed … the zero-slice-step kind", and `spec/packs/24-…` (N-000415) lists the zero-slice-step refusal. **Built: refusal** (`ZeroSliceStepError`), raised at compile time, which the spec allows ("either the compile or the later search refuses").
11. **Hash directly after a projection, `[*]{…}`.** `spec/packs/10-…` (FP-05) says a multiselect "may appear … as the right-hand side of a projection". `spec/packs/06-…` (FP-01 boundary) and `spec/packs/07-…` say a projection followed directly by anything other than a dot, bracket, filter, flatten, pipe, binary operator, comma, closer or end is a syntax failure. **Built: syntax failure.** The form that works is `[*].{…}` (after a dot).

## Choices the spec leaves open (implementer's choice or unstated)

- **Projection placements (FP-04):** a slice written directly after an index or slice starts a projection; a dot followed by a multiselect list does let later steps join its right-hand side. (In `nodes.py`/`parser.py`: every slice projects.)
- **Parsed-expression type** is `pathsel.ParsedExpression` (Interface, `pathsel.compile`). **Options** are read by attribute name from any object, and no options class is published (N-000392).
- **Failure type names** are `EmptyExpressionError`, `IncompleteExpressionError`, `PathSelSyntaxError`, `PathSelTokenSyntaxError` (subclass of the syntax error), `ZeroSliceStepError`, `UnknownFunctionError`, `InvalidArityError`, `InvalidTypeError`, all under `PathSelError(ValueError)`. Syntax and incomplete errors carry `lex_position` (int).
- **Failure messages** are free text (N-000408).
- **Non-string expression to `compile`:** raises `TypeError`. Not stated in the spec.
- **Zero slice step** is detected at compile time (see conflict 10).
- **Nesting deeper than the interpreter recursion limit** is refused with `PathSelError` (the base of all refusals) at compile time. Not stated in the spec.
- **`conftest.py` at the root** only exists so that `import pathsel` resolves under plain `pytest` from `/app`.
- **Comparison between incomparable values** (for example `<` on a number and a string, or on booleans): yields null. The spec defines only number-number and string-string ordering.
- **Host decimals (`decimal.Decimal`):** numbers for comparison (`==`, `<`, …) only. Function arguments that need a JSON number refuse them (invalid-type), per Non-functional constraints. `to_number` of a Decimal gives a float.
- **`type()` on a non-JSON host value** raises invalid-type. The spec says "any" accepts every value but names only six result strings.
- **Numerals for `to_number`:** optional `+`/`-`; integers become `int`; decimal or exponent forms become `float`. Surrounding whitespace is not accepted.
- **`avg`** returns a float. **`sum` of an empty array** is `0`. **`merge`** returns a plain `dict`.
- **Key rules for `sort_by`, `max_by`, `min_by`:** every key must be a number or every key a string; a null key is invalid-type.
- **`contains` on a string** requires a string second argument (else invalid-type).
- **Custom signatures** accept the five JSON type names from Interface Contract, plus `"boolean"`. A host value that is not a JSON type fails them (invalid-type).
- **Built-ins take precedence over a provider function of the same name.** A subclass of `Functions` cannot override a built-in. (Pack 13, N-000339: "every FP-07 function remains available with unchanged behavior.")
- **Function call order:** name, then argument count (before any argument is evaluated), then the arguments are evaluated, then each argument's type is checked in order.
- **Lexical:** whitespace is space, tab, LF, CR. Identifiers are ASCII. Numbers are `-?[0-9]+` (no `+`, no fraction). A `-` not followed by a digit is a token-level failure.
- **Backtick literal:** tried as JSON; if that fails, read as the content of a JSON string after removing leading whitespace; if that also fails, token-level syntax failure.
- **Filter on an object** is null (same as non-array).
- **Object wildcard on an array, list wildcard on an object, index on an object:** null.
- **`[*]` and `[]` at the start of an expression** project or flatten the document itself. `[a, b]` at the start is a multiselect list.
- **Input mutation:** none. Results may share sub-objects with the input (selection returns the stored value itself).
- **Mapping type:** `is_object` accepts any `collections.abc.Mapping` and any instance of the options' `dict_cls`. Objects of other mapping types are accepted by built-ins too.

## Coverage of `spec/CHECKLIST.md` (423 ids)

Status words: **implemented** = code in the module named; **tested** = at least one test in `tests/test_pathsel.py` exercises it. Every id below is implemented, and the feature packs are tested. The ranges are the ones in CHECKLIST.md.

| Pack | Ids | Status | Where |
|---|---|---|---|
| 01 product overview | N-000001–013 | implemented, tested (001–009); 010–013 are document framing with no runtime behaviour, no code obligation | `core.py`, `__init__.py`; tests `test_dotted_path…`, `test_compile_then_search…` |
| 02 terminology | N-000014–037 | implemented, tested (definitions realised by the behaviour below; 037 failure wording is free text) | `values.py`, `errors.py`, `nodes.py` |
| 03 public surface | N-000038–049 | implemented, tested (038–039: library only, no CLI; 042: ill-formed text refuses) | `__init__.py`, `core.py` |
| 04 non-functional | N-000050–066 | implemented: pure Python, `dependencies = []` in `pyproject.toml`, no compiled code; platforms are portable but only Linux was run here; failures are `ValueError` subclasses (`test_refusals_are_value_errors`) | `errors.py`, `pyproject.toml` |
| 05 non-goals | N-000067–072 | implemented by scope: no CLI, no JSON encoder/decoder API, no mutation (`test_input_is_not_mutated`), no tooling in the package | — |
| 06 FP-01 search/compile | N-000073–106 | implemented, tested | `core.py`, `parser.py`, `errors.py`; tests `test_compile_then_search_matches_one_shot`, `test_empty_expression_kind`, `test_whitespace_only_is_incomplete_not_empty`, `test_incomplete_ends`, `test_dot_at_end_is_syntax_not_incomplete`, `test_syntax_kinds_and_positions`, `test_token_level_is_subclass_of_syntax_but_not_syntax` |
| 07 FP-02 identifiers | N-000107–125 | implemented, tested | `lexer.py`, `nodes.py`; tests `test_quoted_identifiers_name_any_key`, `test_hyphen_rules`, `test_bad_quoted_identifier_token_error` |
| 08 FP-03 index/slice/flatten | N-000126–157 | implemented, tested | `nodes.py` (`slice_indices`, `Index`, `SliceProjection`, `FlattenProjection`), `parser.py`; tests `test_slices`, `test_zero_slice_step_refuses`, `test_flatten_one_level` |
| 09 FP-04 projections | N-000158–205 | implemented, tested; implementer's choices at N-000198/199 as stated above | `nodes.py`, `parser.py` (binding powers, `_bp`); tests `test_projection_rules_dot_chains_join_rhs`, `test_flatten_is_loosest_step_after_filter`, `test_bracket_after_*` |
| 10 FP-05 constructors/pipe/literals | N-000206–241 | implemented, tested | `nodes.py` (`MultiList`, `MultiHash`, `Chain`, `Ref`), `lexer.py`; tests `test_multiselect_*`, `test_pipe_*`, `test_json_literals`, `test_raw_string_literal` |
| 11 FP-06 comparison/logic | N-000242–261 | implemented, tested | `nodes.py` (`Compare`, `And`, `Or`, `Not`), `values.py`; tests `test_equality_is_json_equality`, `test_ordering`, `test_or_and_return_operands`, `test_not_truthiness` |
| 12 FP-07 built-in functions | N-000262–322 | implemented, tested; `join` empty-array choice at conflict 8 | `functions.py`, `nodes.py` (`FunctionCall`); tests `test_builtin_scalars`, `test_avg_sum_max_min_sort`, `test_length_counts_characters`, `test_to_array_to_string_to_number`, `test_max_by_min_by_sort_by_map_not_null_merge`, `test_unknown_function_at_search_not_compile`, `test_arity_and_type_checked_at_search` |
| 13 FP-08 options | N-000323–350 | implemented, tested | `nodes.py` (`Context`), `core.py`, `functions.py`; tests `test_dict_cls_*`, `test_custom_provider_functions`, `test_builtins_remain_with_provider`, `test_options_may_carry_both` |
| 14 hardware (overview) | (no ids) | no ids | — |
| 15 hardware summary | N-000351–354 | implemented: no compiled code, zero dependencies, Python ≥3.9 syntax | `pyproject.toml` |
| 16 execution profiles | N-000355–365 | implemented: runs from the source tree with the repo root on the path; no native build | root layout, `pyproject.toml` |
| 17 product form | N-000366–368 | implemented: library only; no `__main__`, no config file, no service | `pathsel/` |
| 18 layout | N-000369–371 | implemented: single top-level `pathsel` package; import performs no I/O | `pathsel/` |
| 19 `pathsel` names | N-000372–374 | implemented, tested | `__init__.py`; `test_package_surface` |
| 20 `pathsel.search` | N-000375–382 | implemented, tested | `core.py` |
| 21 `pathsel.compile` | N-000383–388 | implemented, tested | `core.py` (`ParsedExpression`) |
| 22 evaluation options | N-000389–392 | implemented, tested; no options class published (N-000392 choice) | `nodes.py` (`Context`) |
| 23 `pathsel.functions` | N-000393–404 | implemented, tested | `functions.py` (`Functions`, `signature`); tests `test_custom_provider_functions` |
| 24 failure carriers | N-000405–422 | implemented, tested | `errors.py`; tests `test_token_level_is_subclass…`, `test_refusals_are_value_errors`, `test_arity_and_type…`, `test_whitespace_only…` |
| 25 expression reference value | N-000423 | implemented, tested | `nodes.py` (`Ref`); test `test_expression_reference_top_level_is_non_null` |

**Not done:** none of the 423 ids is left without a status. N-000012 and N-000013 are
document-structure statements ("feature points are ordered…") with no runtime
behaviour to implement; they are satisfied by the layout of `spec/`, not by code.

## Known limits

- Only CPython 3.13 was executed here. Python 3.9 compatibility is by syntax review only.
- Platforms other than Linux were not run.
- `Functions` exposes built-ins as `_func_<name>` methods for subclassing; the evaluator calls the built-in table, not those methods (see the precedence choice above).
