# NOTES

Implementation of the PathSel specification in `spec/` (not modified).

## Layout and how to check it

- `pathsel/` is the importable package (flat layout at the project root, `# spec: N-000369`).
  - `__init__.py`: public names `search`, `compile`, `Parsed`, `EvaluationOptions`, `Functions`, `signature`, the refusal types.
  - `lexer.py`, `parser.py`, `nodes.py`: tokens, Pratt parser, AST.
  - `interpreter.py`: evaluation of the AST against Python data.
  - `functions.py`: `signature`, the built-in provider `Functions`, name resolution.
  - `values.py`: JSON-type helpers, truthiness, equality, ordering, `RefValue`.
  - `errors.py`: refusal kinds. `options.py`: optional options holder.
- `pyproject.toml`: setuptools metadata for the `pathsel` distribution. Runtime dependencies: none.
- `tests/test_pathsel.py`: 105 tests. Each test is named after the checklist id(s) it covers.

Run from `/app`: `python3 -m pytest -q tests/`. Last run: 105 passed on Python 3.13.
Only Python 3.13 was used here. The code uses only the standard library and avoids 3.10+ syntax, but it has not been run on 3.9.

## Spec conflicts and what was built

The export lists 11 unsettled contradictions (`spec/MAP.md`, `spec/export.meta.json`). Each is an open question; this is what was built for each.

1. **CF-000005, filter on a non-array.** Pack 09 FP-04 (N-000202): "A filter on a non-array yields null, not an empty array and not a failure." Pack 11 FP-06 (N-000259): "A filter applied to anything but an array yields the empty array." **Built: null.** The FP-04 rule is the one stated in the filter's own feature point.
2. **CF-000007, slice on a non-array.** Pack 08 FP-03 (N-000142): "A slice on a value that is not an array yields null." Pack 08 FP-03 boundary (N-000157): "A slice of a value that is not an array is the empty array." **Built: null.**
3. **CF-000011, multiselect on a null current value.** Pack 10 FP-05 (N-000212): "On a null current value it still builds one element per expression." Pack 10 FP-05 (N-000218): "A multiselect list or hash whose current value is null yields null." **Built: null** (applies to both list and hash).
4. **CF-000015, `not_null` and empty values.** Pack 02 Terminology, Null (N-000022): "An empty string or an empty array counts as null for `not_null`." Pack 12 FP-07 (N-000300): "an empty array or empty string is not null". **Built: not null.** `not_null("", x)` returns `""`, and `not_null([], x)` returns `[]`. The FP-07 definition is the function's own rule.
5. **CF-000027, object wildcard on a non-object.** Pack 02 Terminology, Projection (N-000031): "An object wildcard applied to a non-object is the empty array." Pack 09 FP-04 (N-000165): "An object wildcard on a value that is not an object yields null." **Built: null.** Same reasoning as item 1.
6. **CF-000035, string length.** Pack 02 Terminology, String (N-000026): "its length is its number of UTF-8 bytes." Pack 12 FP-07 `length` (N-000277): "the number of Unicode characters (not bytes) of a string". **Built: code points** (`len` of the Python string). `length('é😀')` is 2.
7. **CF-000049, `\uXXXX` in a raw string.** Pack 10 FP-05 raw string (N-000227): "No JSON escapes are processed." Pack 10 FP-05 boundary (N-000239): "A `\uXXXX` escape inside a raw string literal is decoded to its character." **Built: no escapes are processed.** Only backslash-quote is special. `'A'` is the 6 characters `A`.
8. **CF-000054, `join` of an empty array.** Pack 12 FP-07 call rules (N-000268): "`join` of an empty array yields null." Pack 12 FP-07 `join` (N-000280): "the empty array yields the empty string". **Built: empty string.**
9. **CF-000055, slice with step 0.** Pack 08 FP-03 (N-000133): "A step of 0 selects nothing: the result is the empty array." Pack 08 FP-03 boundary (N-000152): "A slice whose step is 0 does not succeed on either entry." **Built: refusal** of the zero-slice-step kind, raised when the expression is compiled (so `compile` and `search` both refuse).
10. **CF-000056, bare expression reference.** Pack 02 Terminology (N-000028): "Outside a function argument it evaluates to null." Pack 10 FP-05 (N-000234): "yields a non-null value"; Pack 25 Interface Contract (N-000423): "returns a non-`None` value". **Built: a non-null `RefValue` object** (`pathsel.RefValue`), which is the value the two later statements require.
11. **CF-000057, `to_number` result type.** Pack 02 Terminology, Number (N-000023): "A number made from a string by `to_number` is always a floating-point value." Pack 12 FP-07 `to_number` (N-000287): "a string that is an integer numeral becomes that integer". **Built: integer numerals give `int`** (`to_number('42')` is `42`); decimal and exponent numerals give `float`.

## Other gaps and choices (the spec does not say)

Grammar and parsing:
- **No number literal.** Numbers appear only inside index and slice brackets. `abs(-3)` is a syntax failure; write `` abs(`-3`) ``. This follows from the spec's list of expression forms (N-000218, N-000155).
- **`a.` at the end of the text** is a syntax failure at the end position, not incomplete. The spec lists "the end of the text" after a dot under syntax (N-000094) and also describes incomplete as "text that ends where an operand must still begin" (N-000090). The explicit syntax rule was taken.
- **Dot followed by `@`, a literal, `(`, or `[*]`** is a syntax failure. Only identifiers, quoted identifiers, `*`, `[...]` multiselect lists, `{...}` multiselect hashes and function calls may follow a dot.
- **A function call after a dot** (`a.abs(@)`) is allowed, matching how JMESPath-style languages treat it. Not stated by the spec.
- **Slice after an index** (`a[0][1:2]`) starts a projection, since a slice is always a projection (N-000198 choice).
- **A dot-led multiselect** (`a[*].[x, y]`): later steps join the right-hand side under the projection's binding power (N-000199 choice).
- **Object wildcard after a dot** (`a.*`) ranks as a dot step, so a following dot step applies to the collected array (`a.*.b.c` is `null` for `{"a": {"x": {"b": {"c": 1}}}}`). An operand-initial `*` (rank 2) lets following dot steps join (`*.b.c` yields `[1]`). Both follow the ranking in N-000185 to N-000192.
- **Quoted identifier after a dot followed by `(`** is a syntax failure, as is a quoted identifier used as a function name.
- **Parsing order**: tokens are read lazily, so the first failure from left to right is the one reported.
- **JSON literal** ends at the first unescaped backtick (a backslash skips the next character). If the text is not valid JSON, it is read as JSON string content after stripping leading whitespace (N-000225).
- **Non-string expression** (`search(None, ...)`) raises `TypeError`, not a refusal. The spec only covers text input.

Evaluation:
- **Comparators** (`<`, `<=`, `>`, `>=`) with operands that are not both numbers or both strings yield null. The spec does not say what happens for mixed types.
- **`==` and `!=`** are JSON equality: `1 == true` is false, `0 == false` is false, and `1 == 1.0` is true.
- **Unknown-function refusals happen when the call is evaluated** (N-000264). `false && nosuch()` succeeds with `false`, because the call is never reached.
- **Built-in names take precedence** over a provider's function with the same name, so FP-07 behavior cannot be changed by a provider (N-000340).
- **Provider functions** are looked up only on the attached provider, so a name declared on another provider is unknown (N-000344).
- **Arrays** are `list` and `tuple`. **Objects** are any `collections.abc.Mapping`, including `dict_cls` instances and `OrderedDict`.
- **Host decimals**: they are numbers for comparisons and for `type()` (which returns `"number"`). They are not JSON numbers for function arguments, so `abs(d)` with a `Decimal` is an invalid-type refusal, following N-000057 and N-000058.
- **`type()` of a value that is not one of the six JSON types** is an invalid-type refusal, because the spec requires one of six names.
- **`to_string`** uses compact JSON with `ensure_ascii=True`. Host values JSON cannot encode fall back to `str()`. `Decimal` is written as a float.
- **`to_number`** strips surrounding ASCII whitespace. `+5`, `1_0`, `nan` and `inf` yield null.
- **`avg`** returns `sum / count` (a float). `ceil` and `floor` of `inf` or `nan` return the argument unchanged.
- **`contains(string, non-string)`** returns false, not a refusal.
- **`max`, `min`, `sort`, `sort_by`, `max_by`, `min_by`** refuse mixed-type or null keys with invalid-type. `sort_by` of an empty array is `[]`. `max_by` of an empty array is null.
- **`merge`** returns a plain `dict`, not the `dict_cls` type.
- **`merge`, `not_null`** have one-or-more arity; **`abs`** and similar have exact arity.
- **Projections** drop nulls even with no right-hand side. A projection applied to a null base is null.
- **Results may share objects with the input document**; the library never writes to the input. Literal values are deep-copied on each evaluation.
- **Expression reference inside a non-reference position** (`to_string(&a)`) is converted with `str()`, not refused.
- **Evaluation options**: any object with `dict_cls` and `custom_functions` attributes is accepted. `EvaluationOptions` is an optional holder.
- **Null-current multiselect hash** yields null (see CF-000011 above).

Tests and environment:
- Tests were written from the spec, not from any existing implementation. Several expectations were derived from the ranking rules (for example, `*.b.c` and `a.*.b.c`).
- Only the features listed above were exercised. A random-expression fuzz run (60,000 expressions, not checked in) found no exception other than a PathSel refusal.

## Checklist status

Every id in `spec/CHECKLIST.md` is listed below as implemented, tested, or not done. "Implemented" means a `# spec:` comment in `pathsel/` names it. "Tested" means a test in `tests/test_pathsel.py` names it, either in its function name or in a comment. An id can be both (the table then says "implemented" and gives the test as well). Seven ids are not done, each with a reason.

| Id | Status | Where |
|---|---|---|
| N-000001 | tested | `tests/test_pathsel.py` `test_N_000001_evaluates_against_python_data` |
| N-000002 | tested | `tests/test_pathsel.py` `test_N_000002_dotted_path_returns_nested_value` |
| N-000003 | tested | `tests/test_pathsel.py` `test_N_000003_missing_path_yields_null` |
| N-000004 | implemented | `pathsel/__init__.py:92` |
| N-000005 | implemented | `pathsel/__init__.py:68` |
| N-000006 | implemented | `pathsel/__init__.py:87` |
| N-000007 | implemented | `pathsel/__init__.py:92` |
| N-000008 | implemented | `pathsel/__init__.py:82` |
| N-000009 | implemented | `pathsel/__init__.py:82` |
| N-000010 | implemented | `pathsel/__init__.py:9` |
| N-000011 | implemented | `pathsel/__init__.py:9` |
| N-000012 | implemented | `pathsel/__init__.py:15` |
| N-000013 | not done | PRD ordering statement (feature points ordered by dependency). It is documentation; the library has no runtime behavior for it. |
| N-000014 | implemented | `pathsel/parser.py:353` |
| N-000015 | implemented | `pathsel/interpreter.py:29` |
| N-000016 | implemented | `pathsel/__init__.py:92` (also tested: test_N_000016_search_entry_takes_expression_and_document) |
| N-000017 | implemented | `pathsel/__init__.py:87` (also tested: test_N_000017_compile_entry_returns_reusable_parsed_expression) |
| N-000018 | implemented | `pathsel/__init__.py:68` |
| N-000019 | implemented | `pathsel/nodes.py:14` |
| N-000020 | implemented | `pathsel/nodes.py:14` |
| N-000021 | implemented | `pathsel/interpreter.py:30` |
| N-000022 | implemented | `pathsel/functions.py:267` |
| N-000023 | not done | Conflicts with N-000287 (CF-000057). Built: integer numerals become int; see NOTES.md. |
| N-000024 | implemented | `pathsel/values.py:44` (also tested: test_N_000024_decimal_values_participate_in_comparisons) |
| N-000025 | implemented | `pathsel/values.py:39` |
| N-000026 | not done | Conflicts with N-000277 (CF-000035). Built: length counts code points; see NOTES.md. |
| N-000027 | implemented | `pathsel/values.py:39` |
| N-000028 | not done | Conflicts with N-000234 and N-000423 (CF-000056). Built: a bare expression reference returns a non-null RefValue; see NOTES.md. |
| N-000029 | implemented | `pathsel/values.py:59` |
| N-000030 | implemented | `pathsel/interpreter.py:98` |
| N-000031 | not done | Conflicts with N-000165 (CF-000027). Built: an object wildcard on a non-object is null; see NOTES.md. |
| N-000032 | implemented | `pathsel/options.py:1` |
| N-000033 | implemented | `pathsel/functions.py:112` |
| N-000034 | implemented | `pathsel/errors.py:18` |
| N-000035 | implemented | `pathsel/errors.py:18` |
| N-000036 | implemented | `pathsel/errors.py:18` |
| N-000037 | implemented | `pathsel/errors.py:21` |
| N-000038 | implemented | `pathsel/__init__.py:9` |
| N-000039 | implemented | `pathsel/__init__.py:16` |
| N-000040 | implemented | `pathsel/__init__.py:9` |
| N-000041 | implemented | `pathsel/interpreter.py:36` |
| N-000042 | implemented | `pathsel/parser.py:353` |
| N-000043 | implemented | `pathsel/__init__.py:9` |
| N-000044 | implemented | `pathsel/__init__.py:11` |
| N-000045 | implemented | `pathsel/__init__.py:12` |
| N-000046 | implemented | `pathsel/__init__.py:12` |
| N-000047 | implemented | `pathsel/__init__.py:13` |
| N-000048 | implemented | `pathsel/__init__.py:13` |
| N-000049 | implemented | `pathsel/__init__.py:9` |
| N-000050 | tested | `tests/test_pathsel.py` `test_N_000050_pure_python_package_has_no_runtime_dependencies` |
| N-000051 | tested | `tests/test_pathsel.py` `test_N_000050_pure_python_package_has_no_runtime_dependencies` |
| N-000052 | tested | `tests/test_pathsel.py` `test_N_000050_pure_python_package_has_no_runtime_dependencies` |
| N-000053 | tested | `tests/test_pathsel.py` `test_N_000050_pure_python_package_has_no_runtime_dependencies` |
| N-000054 | tested | `tests/test_pathsel.py` `test_N_000050_pure_python_package_has_no_runtime_dependencies` |
| N-000055 | tested | `tests/test_pathsel.py` `test_N_000050_pure_python_package_has_no_runtime_dependencies` |
| N-000056 | implemented | `pathsel/values.py:44` (also tested: test_N_000024_decimal_values_participate_in_comparisons) |
| N-000057 | implemented | `pathsel/functions.py:58` |
| N-000058 | implemented | `pathsel/functions.py:58` |
| N-000059 | implemented | `pathsel/interpreter.py:36` (also tested: test_N_000003_missing_path_yields_null) |
| N-000060 | tested | `tests/test_pathsel.py` `test_N_000003_missing_path_yields_null` |
| N-000061 | implemented | `pathsel/errors.py:21` |
| N-000062 | implemented | `pathsel/errors.py:21` |
| N-000063 | tested | `tests/test_pathsel.py` `test_N_000105_refusals_are_value_errors_not_null` |
| N-000064 | implemented | `pathsel/errors.py:18` |
| N-000065 | implemented | `pathsel/parser.py:71` |
| N-000066 | implemented | `pathsel/interpreter.py:29` |
| N-000067 | tested | `tests/test_pathsel.py` `test_N_000067_no_json_decoding_of_document_text` |
| N-000068 | tested | `tests/test_pathsel.py` `test_N_000067_no_json_decoding_of_document_text` |
| N-000069 | implemented | `pathsel/interpreter.py:3` (also tested: test_N_000069_evaluation_does_not_mutate_input) |
| N-000070 | implemented | `pathsel/interpreter.py:3` (also tested: test_N_000069_evaluation_does_not_mutate_input) |
| N-000071 | not done | Non-goal: development tooling, packaging scripts, internal caching. Nothing to build. |
| N-000072 | not done | Non-goal: a later official language revision. Nothing to build. |
| N-000073 | implemented | `pathsel/__init__.py:92` |
| N-000074 | implemented | `pathsel/__init__.py:87` |
| N-000075 | implemented | `pathsel/__init__.py:87` |
| N-000076 | implemented | `pathsel/__init__.py:87` |
| N-000077 | tested | `tests/test_pathsel.py` `test_N_000002_dotted_path_returns_nested_value` |
| N-000078 | implemented | `pathsel/__init__.py:68` (also tested: test_N_000017_compile_entry_returns_reusable_parsed_expression) |
| N-000079 | implemented | `pathsel/__init__.py:82` (also tested: test_N_000017_compile_entry_returns_reusable_parsed_expression) |
| N-000080 | implemented | `pathsel/__init__.py:97` (also tested: tests/test_pathsel.py:47) |
| N-000081 | implemented | `pathsel/__init__.py:97` |
| N-000082 | implemented | `pathsel/__init__.py:92` |
| N-000083 | implemented | `pathsel/interpreter.py:36` (also tested: test_N_000003_missing_path_yields_null) |
| N-000084 | implemented | `pathsel/interpreter.py:36` (also tested: test_N_000003_missing_path_yields_null) |
| N-000085 | implemented | `pathsel/interpreter.py:36` |
| N-000086 | implemented | `pathsel/__init__.py:87` (also tested: test_N_000086_compiling_well_formed_expression_succeeds_even_if_search_is_null) |
| N-000087 | implemented | `pathsel/errors.py:26` (also tested: test_N_000087_empty_text_is_empty_expression_refusal) |
| N-000088 | implemented | `pathsel/parser.py:361` (also tested: test_N_000087_empty_text_is_empty_expression_refusal) |
| N-000089 | tested | `tests/test_pathsel.py` `test_N_000087_empty_text_is_empty_expression_refusal` |
| N-000090 | implemented | `pathsel/parser.py:68` (also tested: test_N_000090_incomplete_expressions_refuse) |
| N-000091 | tested | `tests/test_pathsel.py` `test_N_000091_whitespace_only_is_incomplete_not_empty` |
| N-000092 | implemented | `pathsel/parser.py:68` (also tested: test_N_000090_incomplete_expressions_refuse) |
| N-000093 | tested | `tests/test_pathsel.py` `test_N_000090_incomplete_expressions_refuse` |
| N-000094 | implemented | `pathsel/parser.py:71` (also tested: test_N_000094_syntax_failures_refuse) |
| N-000095 | implemented | `pathsel/parser.py:367` (also tested: test_N_000094_syntax_failures_refuse) |
| N-000096 | implemented | `pathsel/errors.py:46` (also tested: test_N_000096_token_level_failures_are_specific_syntax_kind) |
| N-000097 | tested | `tests/test_pathsel.py` `test_N_000096_token_level_failures_are_specific_syntax_kind` |
| N-000098 | tested | `tests/test_pathsel.py` `test_N_000096_token_level_failures_are_specific_syntax_kind` |
| N-000099 | tested | `tests/test_pathsel.py` `test_N_000096_token_level_failures_are_specific_syntax_kind` |
| N-000100 | tested | `tests/test_pathsel.py` `test_N_000096_token_level_failures_are_specific_syntax_kind` |
| N-000101 | tested | `tests/test_pathsel.py` `test_N_000096_token_level_failures_are_specific_syntax_kind` |
| N-000102 | implemented | `pathsel/lexer.py:5` (also tested: test_N_000102_position_reports_offset_of_failing_token) |
| N-000103 | implemented | `pathsel/lexer.py:5` (also tested: test_N_000102_position_reports_offset_of_failing_token) |
| N-000104 | tested | `tests/test_pathsel.py` `test_N_000102_position_reports_offset_of_failing_token` |
| N-000105 | implemented | `pathsel/errors.py:18` (also tested: test_N_000105_refusals_are_value_errors_not_null) |
| N-000106 | tested | `tests/test_pathsel.py` `test_N_000105_refusals_are_value_errors_not_null` |
| N-000107 | implemented | `pathsel/lexer.py:14` (also tested: test_N_000107_unquoted_identifier_selects_key) |
| N-000108 | implemented | `pathsel/interpreter.py:53` (also tested: test_N_000107_unquoted_identifier_selects_key) |
| N-000109 | implemented | `pathsel/lexer.py:13` (also tested: test_N_000107_unquoted_identifier_selects_key) |
| N-000110 | implemented | `pathsel/lexer.py:126` (also tested: test_N_000110_quoted_identifier_names_any_key) |
| N-000111 | tested | `tests/test_pathsel.py` `test_N_000110_quoted_identifier_names_any_key` |
| N-000112 | tested | `tests/test_pathsel.py` `test_N_000110_quoted_identifier_names_any_key` |
| N-000113 | tested | `tests/test_pathsel.py` `test_N_000110_quoted_identifier_names_any_key` |
| N-000114 | implemented | `pathsel/lexer.py:126` (also tested: test_N_000110_quoted_identifier_names_any_key) |
| N-000115 | implemented | `pathsel/interpreter.py:36` (also tested: test_N_000115_identifier_on_non_object_is_null) |
| N-000116 | implemented | `pathsel/interpreter.py:36` (also tested: test_N_000115_identifier_on_non_object_is_null) |
| N-000117 | implemented | `pathsel/lexer.py:17` (also tested: test_N_000117_number_cannot_be_identifier) |
| N-000118 | tested | `tests/test_pathsel.py` `test_N_000117_number_cannot_be_identifier` |
| N-000119 | implemented | `pathsel/lexer.py:75` (also tested: test_N_000119_hyphen_is_token_error) |
| N-000120 | tested | `tests/test_pathsel.py` `test_N_000119_hyphen_is_token_error` |
| N-000121 | implemented | `pathsel/lexer.py:75` (also tested: test_N_000119_hyphen_is_token_error) |
| N-000122 | implemented | `pathsel/lexer.py:75` (also tested: test_N_000119_hyphen_is_token_error) |
| N-000123 | implemented | `pathsel/parser.py:149` (also tested: test_N_000123_dot_at_start_end_or_doubled_refuses) |
| N-000124 | implemented | `pathsel/lexer.py:126` (also tested: test_N_000124_unterminated_or_illegal_quoted_identifier_refuses) |
| N-000125 | implemented | `pathsel/interpreter.py:36` (also tested: test_N_000115_identifier_on_non_object_is_null) |
| N-000126 | implemented | `pathsel/interpreter.py:50` (also tested: test_N_000126_index_is_zero_based_and_negative_from_end) |
| N-000127 | implemented | `pathsel/interpreter.py:50` (also tested: test_N_000126_index_is_zero_based_and_negative_from_end) |
| N-000128 | implemented | `pathsel/interpreter.py:50` (also tested: test_N_000126_index_is_zero_based_and_negative_from_end) |
| N-000129 | implemented | `pathsel/interpreter.py:45` (also tested: test_N_000126_index_is_zero_based_and_negative_from_end) |
| N-000130 | implemented | `pathsel/interpreter.py:120` (also tested: test_N_000130_slice_selects_new_array_with_default_step) |
| N-000131 | implemented | `pathsel/interpreter.py:142` (also tested: test_N_000130_slice_selects_new_array_with_default_step) |
| N-000132 | tested | `tests/test_pathsel.py` `test_N_000132_step_may_be_negative_and_selects_from_end` |
| N-000133 | tested | `tests/test_pathsel.py` `test_N_000133_negative_start_and_stop_add_length` |
| N-000134 | implemented | `pathsel/interpreter.py:149` (also tested: test_N_000133_negative_start_and_stop_add_length) |
| N-000135 | implemented | `pathsel/interpreter.py:149` (also tested: test_N_000130_slice_selects_new_array_with_default_step) |
| N-000136 | implemented | `pathsel/interpreter.py:151` (also tested: test_N_000130_slice_selects_new_array_with_default_step) |
| N-000137 | implemented | `pathsel/interpreter.py:155` (also tested: test_N_000130_slice_selects_new_array_with_default_step) |
| N-000138 | implemented | `pathsel/interpreter.py:159` (also tested: test_N_000132_step_may_be_negative_and_selects_from_end) |
| N-000139 | implemented | `pathsel/interpreter.py:160` (also tested: test_N_000132_step_may_be_negative_and_selects_from_end) |
| N-000140 | implemented | `pathsel/interpreter.py:161` (also tested: test_N_000132_step_may_be_negative_and_selects_from_end) |
| N-000141 | implemented | `pathsel/interpreter.py:120` (also tested: test_N_000141_slice_selecting_nothing_is_empty_array) |
| N-000142 | implemented | `pathsel/interpreter.py:119` (also tested: test_N_000142_slice_on_non_array_is_null) |
| N-000143 | implemented | `pathsel/interpreter.py:137` (also tested: test_N_000143_slice_is_projection_dropping_nulls) |
| N-000144 | implemented | `pathsel/interpreter.py:137` (also tested: test_N_000143_slice_is_projection_dropping_nulls) |
| N-000145 | implemented | `pathsel/parser.py:77` (also tested: test_N_000145_flatten_splices_one_level) |
| N-000146 | implemented | `pathsel/interpreter.py:114` (also tested: test_N_000145_flatten_splices_one_level) |
| N-000147 | implemented | `pathsel/interpreter.py:110` (also tested: test_N_000145_flatten_splices_one_level) |
| N-000148 | implemented | `pathsel/parser.py:219` (also tested: test_N_000148_flatten_is_projection_over_flattened_array) |
| N-000149 | tested | `tests/test_pathsel.py` `test_N_000148_flatten_is_projection_over_flattened_array` |
| N-000150 | tested | `tests/test_pathsel.py` `test_N_000148_flatten_is_projection_over_flattened_array` |
| N-000151 | tested | `tests/test_pathsel.py` `test_N_000151_index_slice_flatten_can_start_expression` |
| N-000152 | implemented | `pathsel/errors.py:50` (also tested: test_N_000152_zero_slice_step_refuses) |
| N-000153 | tested | `tests/test_pathsel.py` `test_N_000152_zero_slice_step_refuses` |
| N-000154 | implemented | `pathsel/parser.py:292` (also tested: test_N_000152_zero_slice_step_refuses) |
| N-000155 | implemented | `pathsel/lexer.py:17` (also tested: test_N_000155_slice_with_too_many_parts_is_syntax_failure) |
| N-000156 | implemented | `pathsel/interpreter.py:50` |
| N-000157 | tested | `tests/test_pathsel.py` `test_N_000141_slice_selecting_nothing_is_empty_array` |
| N-000158 | implemented | `pathsel/interpreter.py:98` |
| N-000159 | implemented | `pathsel/interpreter.py:98` (also tested: test_N_000159_list_wildcard_projects_and_drops_nulls) |
| N-000160 | implemented | `pathsel/parser.py:216` (also tested: test_N_000159_list_wildcard_projects_and_drops_nulls) |
| N-000161 | implemented | `pathsel/interpreter.py:102` (also tested: test_N_000159_list_wildcard_projects_and_drops_nulls) |
| N-000162 | implemented | `pathsel/interpreter.py:102` (also tested: test_N_000159_list_wildcard_projects_and_drops_nulls) |
| N-000163 | implemented | `pathsel/parser.py:110` (also tested: test_N_000163_object_wildcard_projects_values_in_order) |
| N-000164 | implemented | `pathsel/interpreter.py:107` (also tested: test_N_000163_object_wildcard_projects_values_in_order) |
| N-000165 | implemented | `pathsel/interpreter.py:106` (also tested: test_N_000165_object_wildcard_on_non_object_is_null) |
| N-000166 | implemented | `pathsel/interpreter.py:98` (also tested: test_N_000166_nested_projection_yields_inner_arrays) |
| N-000167 | implemented | `pathsel/interpreter.py:98` (also tested: test_N_000166_nested_projection_yields_inner_arrays) |
| N-000168 | implemented | `pathsel/interpreter.py:124` (also tested: test_N_000168_filter_keeps_true_elements_in_order) |
| N-000169 | tested | `tests/test_pathsel.py` `test_N_000168_filter_keeps_true_elements_in_order` |
| N-000170 | tested | `tests/test_pathsel.py` `test_N_000168_filter_keeps_true_elements_in_order` |
| N-000171 | tested | `tests/test_pathsel.py` `test_N_000168_filter_keeps_true_elements_in_order` |
| N-000172 | implemented | `pathsel/interpreter.py:124` (also tested: test_N_000168_filter_keeps_true_elements_in_order) |
| N-000173 | implemented | `pathsel/parser.py:251` (also tested: test_N_000168_filter_keeps_true_elements_in_order) |
| N-000174 | tested | `tests/test_pathsel.py` `test_N_000174_predicate_truthiness_and_zero` |
| N-000175 | tested | `tests/test_pathsel.py` `test_N_000174_predicate_truthiness_and_zero` |
| N-000176 | tested | `tests/test_pathsel.py` `test_N_000174_predicate_truthiness_and_zero` |
| N-000177 | tested | `tests/test_pathsel.py` `test_N_000174_predicate_truthiness_and_zero` |
| N-000178 | tested | `tests/test_pathsel.py` `test_N_000174_predicate_truthiness_and_zero` |
| N-000179 | tested | `tests/test_pathsel.py` `test_N_000174_predicate_truthiness_and_zero` |
| N-000180 | implemented | `pathsel/values.py:78` (also tested: test_N_000180_equality_in_predicate_is_json_equality) |
| N-000181 | implemented | `pathsel/values.py:78` (also tested: test_N_000180_equality_in_predicate_is_json_equality) |
| N-000182 | tested | `tests/test_pathsel.py` `test_N_000182_projection_reach_comparison_compares_whole_array` |
| N-000183 | implemented | `pathsel/parser.py:193` (also tested: test_N_000182_projection_reach_comparison_compares_whole_array) |
| N-000184 | implemented | `pathsel/parser.py:193` (also tested: test_N_000182_projection_reach_comparison_compares_whole_array) |
| N-000185 | implemented | `pathsel/parser.py:3` (also tested: test_N_000182_projection_reach_comparison_compares_whole_array) |
| N-000186 | tested | `tests/test_pathsel.py` `test_N_000182_projection_reach_comparison_compares_whole_array` |
| N-000187 | implemented | `pathsel/parser.py:177` (also tested: test_N_000182_projection_reach_comparison_compares_whole_array) |
| N-000188 | tested | `tests/test_pathsel.py` `test_N_000182_projection_reach_comparison_compares_whole_array` |
| N-000189 | tested | `tests/test_pathsel.py` `test_N_000182_projection_reach_comparison_compares_whole_array` |
| N-000190 | implemented | `pathsel/parser.py:3` (also tested: test_N_000182_projection_reach_comparison_compares_whole_array) |
| N-000191 | implemented | `pathsel/parser.py:9` (also tested: test_N_000182_projection_reach_comparison_compares_whole_array) |
| N-000192 | implemented | `pathsel/parser.py:193` (also tested: test_N_000182_projection_reach_comparison_compares_whole_array) |
| N-000193 | tested | `tests/test_pathsel.py` `test_N_000193_nested_projection_right_hand_side_rule` |
| N-000194 | implemented | `pathsel/parser.py:9` (also tested: test_N_000193_nested_projection_right_hand_side_rule) |
| N-000195 | implemented | `pathsel/parser.py:10` (also tested: test_N_000182_projection_reach_comparison_compares_whole_array) |
| N-000196 | tested | `tests/test_pathsel.py` `test_N_000182_projection_reach_comparison_compares_whole_array` |
| N-000197 | implemented | `pathsel/parser.py:10` (also tested: test_N_000182_projection_reach_comparison_compares_whole_array) |
| N-000198 | tested | `tests/test_pathsel.py` `test_N_000198_projection_placement_choices_are_documented` |
| N-000199 | tested | `tests/test_pathsel.py` `test_N_000198_projection_placement_choices_are_documented` |
| N-000200 | implemented | `pathsel/parser.py:202` (also tested: test_N_000200_wildcard_followed_by_identifier_refuses) |
| N-000201 | implemented | `pathsel/parser.py:202` (also tested: test_N_000200_wildcard_followed_by_identifier_refuses) |
| N-000202 | implemented | `pathsel/interpreter.py:123` (also tested: test_N_000202_filter_on_non_array_is_null) |
| N-000203 | tested | `tests/test_pathsel.py` `test_N_000202_filter_on_non_array_is_null` |
| N-000204 | implemented | `pathsel/interpreter.py:4` (also tested: test_N_000143_slice_is_projection_dropping_nulls) |
| N-000205 | implemented | `pathsel/interpreter.py:4` |
| N-000206 | implemented | `pathsel/interpreter.py:66` (also tested: test_N_000206_multiselect_hash_builds_object_and_stores_nulls) |
| N-000207 | implemented | `pathsel/interpreter.py:66` (also tested: test_N_000206_multiselect_hash_builds_object_and_stores_nulls) |
| N-000208 | implemented | `pathsel/interpreter.py:66` (also tested: test_N_000206_multiselect_hash_builds_object_and_stores_nulls) |
| N-000209 | tested | `tests/test_pathsel.py` `test_N_000206_multiselect_hash_builds_object_and_stores_nulls` |
| N-000210 | tested | `tests/test_pathsel.py` `test_N_000206_multiselect_hash_builds_object_and_stores_nulls` |
| N-000211 | implemented | `pathsel/interpreter.py:59` (also tested: test_N_000211_multiselect_list_builds_array_in_order) |
| N-000212 | implemented | `pathsel/interpreter.py:59` (also tested: test_N_000211_multiselect_list_builds_array_in_order) |
| N-000213 | implemented | `pathsel/parser.py:223` (also tested: test_N_000213_multiselect_placement_and_null_current_value) |
| N-000214 | tested | `tests/test_pathsel.py` `test_N_000213_multiselect_placement_and_null_current_value` |
| N-000215 | implemented | `pathsel/parser.py:169` (also tested: test_N_000213_multiselect_placement_and_null_current_value) |
| N-000216 | tested | `tests/test_pathsel.py` `test_N_000213_multiselect_placement_and_null_current_value` |
| N-000217 | tested | `tests/test_pathsel.py` `test_N_000213_multiselect_placement_and_null_current_value` |
| N-000218 | implemented | `pathsel/interpreter.py:59` (also tested: test_N_000213_multiselect_placement_and_null_current_value) |
| N-000219 | implemented | `pathsel/interpreter.py:53` (also tested: test_N_000219_pipe_passes_whole_result_and_binds_loosest) |
| N-000220 | tested | `tests/test_pathsel.py` `test_N_000219_pipe_passes_whole_result_and_binds_loosest` |
| N-000221 | tested | `tests/test_pathsel.py` `test_N_000219_pipe_passes_whole_result_and_binds_loosest` |
| N-000222 | implemented | `pathsel/parser.py:133` (also tested: test_N_000219_pipe_passes_whole_result_and_binds_loosest) |
| N-000223 | implemented | `pathsel/interpreter.py:42` (also tested: test_N_000223_json_literal_is_value_regardless_of_document) |
| N-000224 | tested | `tests/test_pathsel.py` `test_N_000223_json_literal_is_value_regardless_of_document` |
| N-000225 | tested | `tests/test_pathsel.py` `test_N_000223_json_literal_is_value_regardless_of_document` |
| N-000226 | implemented | `pathsel/lexer.py:169` (also tested: test_N_000223_json_literal_is_value_regardless_of_document) |
| N-000227 | implemented | `pathsel/lexer.py:148` (also tested: test_N_000227_raw_string_is_string_without_json_escapes) |
| N-000228 | tested | `tests/test_pathsel.py` `test_N_000227_raw_string_is_string_without_json_escapes` |
| N-000229 | tested | `tests/test_pathsel.py` `test_N_000227_raw_string_is_string_without_json_escapes` |
| N-000230 | implemented | `pathsel/lexer.py:148` (also tested: test_N_000227_raw_string_is_string_without_json_escapes) |
| N-000231 | implemented | `pathsel/interpreter.py:82` (also tested: test_N_000231_expression_reference_is_non_null_value) |
| N-000232 | implemented | `pathsel/parser.py:126` (also tested: test_N_000231_expression_reference_is_non_null_value) |
| N-000233 | tested | `tests/test_pathsel.py` `test_N_000231_expression_reference_is_non_null_value` |
| N-000234 | implemented | `pathsel/interpreter.py:82` (also tested: test_N_000231_expression_reference_is_non_null_value) |
| N-000235 | tested | `tests/test_pathsel.py` `test_N_000231_expression_reference_is_non_null_value` |
| N-000236 | tested | `tests/test_pathsel.py` `test_N_000231_expression_reference_is_non_null_value` |
| N-000237 | implemented | `pathsel/lexer.py:169` (also tested: test_N_000237_bad_literal_or_raw_string_refuses) |
| N-000238 | implemented | `pathsel/parser.py:149` (also tested: test_N_000238_literal_after_dot_refuses) |
| N-000239 | tested | `tests/test_pathsel.py` `test_N_000238_literal_after_dot_refuses` |
| N-000240 | implemented | `pathsel/parser.py:308` (also tested: test_N_000240_multiselect_missing_closer_or_trailing_comma_refuses) |
| N-000241 | tested | `tests/test_pathsel.py` `test_N_000240_multiselect_missing_closer_or_trailing_comma_refuses` |
| N-000242 | implemented | `pathsel/interpreter.py:91` (also tested: test_N_000242_equality_is_deep_json_equality) |
| N-000243 | implemented | `pathsel/values.py:78` (also tested: test_N_000242_equality_is_deep_json_equality) |
| N-000244 | implemented | `pathsel/values.py:78` (also tested: test_N_000242_equality_is_deep_json_equality) |
| N-000245 | implemented | `pathsel/interpreter.py:94` (also tested: test_N_000245_ordering_numbers_and_strings) |
| N-000246 | implemented | `pathsel/interpreter.py:94` (also tested: test_N_000245_ordering_numbers_and_strings) |
| N-000247 | implemented | `pathsel/interpreter.py:72` (also tested: test_N_000247_or_and_return_operands) |
| N-000248 | implemented | `pathsel/interpreter.py:75` (also tested: test_N_000247_or_and_return_operands) |
| N-000249 | implemented | `pathsel/interpreter.py:72` (also tested: test_N_000247_or_and_return_operands) |
| N-000250 | implemented | `pathsel/interpreter.py:75` (also tested: test_N_000247_or_and_return_operands) |
| N-000251 | implemented | `pathsel/interpreter.py:69` (also tested: test_N_000251_not_returns_boolean_and_zero_is_true) |
| N-000252 | implemented | `pathsel/interpreter.py:69` (also tested: test_N_000251_not_returns_boolean_and_zero_is_true) |
| N-000253 | implemented | `pathsel/parser.py:124` (also tested: test_N_000253_binding_order_and_grouping) |
| N-000254 | tested | `tests/test_pathsel.py` `test_N_000253_binding_order_and_grouping` |
| N-000255 | tested | `tests/test_pathsel.py` `test_N_000253_binding_order_and_grouping` |
| N-000256 | tested | `tests/test_pathsel.py` `test_N_000253_binding_order_and_grouping` |
| N-000257 | tested | `tests/test_pathsel.py` `test_N_000253_binding_order_and_grouping` |
| N-000258 | tested | `tests/test_pathsel.py` `test_N_000258_filter_uses_same_operators` |
| N-000259 | tested | `tests/test_pathsel.py` `test_N_000258_filter_uses_same_operators` |
| N-000260 | implemented | `pathsel/lexer.py:109` (also tested: test_N_000260_lone_equals_refuses) |
| N-000261 | tested | `tests/test_pathsel.py` `test_N_000261_lone_ampersand_or_missing_side_refuses` |
| N-000262 | implemented | `pathsel/interpreter.py:79` (also tested: test_N_000262_function_calls_by_name) |
| N-000263 | implemented | `pathsel/functions.py:112` (also tested: test_N_000262_function_calls_by_name) |
| N-000264 | implemented | `pathsel/functions.py:326` (also tested: test_N_000262_function_calls_by_name) |
| N-000265 | tested | `tests/test_pathsel.py` `test_N_000264_unknown_function_refuses_on_evaluation` |
| N-000266 | tested | `tests/test_pathsel.py` `test_N_000264_unknown_function_refuses_on_evaluation` |
| N-000267 | tested | `tests/test_pathsel.py` `test_N_000264_unknown_function_refuses_on_evaluation` |
| N-000268 | tested | `tests/test_pathsel.py` `test_N_000264_unknown_function_refuses_on_evaluation` |
| N-000269 | implemented | `pathsel/functions.py:121` (also tested: test_N_000262_function_calls_by_name) |
| N-000270 | implemented | `pathsel/functions.py:125` (also tested: test_N_000270_avg_of_numbers_and_empty_is_null) |
| N-000271 | implemented | `pathsel/functions.py:125` (also tested: test_N_000270_avg_of_numbers_and_empty_is_null) |
| N-000272 | implemented | `pathsel/functions.py:132` (also tested: test_N_000272_ceil_and_floor_are_integers) |
| N-000273 | implemented | `pathsel/functions.py:139` (also tested: test_N_000272_ceil_and_floor_are_integers) |
| N-000274 | implemented | `pathsel/functions.py:167` (also tested: test_N_000274_contains_array_and_string) |
| N-000275 | implemented | `pathsel/functions.py:167` (also tested: test_N_000274_contains_array_and_string) |
| N-000276 | implemented | `pathsel/functions.py:175` (also tested: test_N_000276_starts_and_ends_with) |
| N-000277 | implemented | `pathsel/functions.py:183` (also tested: test_N_000277_length_counts_code_points) |
| N-000278 | implemented | `pathsel/functions.py:188` (also tested: test_N_000278_reverse_array_and_string) |
| N-000279 | implemented | `pathsel/functions.py:194` (also tested: test_N_000279_join_strings_and_empty_array) |
| N-000280 | implemented | `pathsel/functions.py:194` (also tested: test_N_000279_join_strings_and_empty_array) |
| N-000281 | implemented | `pathsel/functions.py:201` (also tested: test_N_000281_keys_and_values_in_iteration_order) |
| N-000282 | implemented | `pathsel/functions.py:216` (also tested: test_N_000282_type_names) |
| N-000283 | implemented | `pathsel/functions.py:232` (also tested: test_N_000283_to_array_wraps_non_arrays) |
| N-000284 | implemented | `pathsel/functions.py:240` (also tested: test_N_000284_to_string_compact_json_and_unicode_escapes) |
| N-000285 | implemented | `pathsel/functions.py:240` (also tested: test_N_000284_to_string_compact_json_and_unicode_escapes) |
| N-000286 | implemented | `pathsel/functions.py:246` (also tested: test_N_000286_to_number_conversions) |
| N-000287 | implemented | `pathsel/functions.py:246` (also tested: test_N_000286_to_number_conversions) |
| N-000288 | implemented | `pathsel/functions.py:23` (also tested: test_N_000286_to_number_conversions) |
| N-000289 | implemented | `pathsel/functions.py:24` (also tested: test_N_000286_to_number_conversions) |
| N-000290 | implemented | `pathsel/functions.py:146` (also tested: test_N_000290_max_min_of_numbers_or_strings) |
| N-000291 | tested | `tests/test_pathsel.py` `test_N_000290_max_min_of_numbers_or_strings` |
| N-000292 | implemented | `pathsel/functions.py:146` (also tested: test_N_000290_max_min_of_numbers_or_strings) |
| N-000293 | implemented | `pathsel/functions.py:209` (also tested: test_N_000293_sort_numbers_or_strings) |
| N-000294 | implemented | `pathsel/functions.py:160` (also tested: test_N_000294_sum_of_numbers) |
| N-000295 | implemented | `pathsel/functions.py:260` (also tested: test_N_000295_merge_objects_later_wins) |
| N-000296 | implemented | `pathsel/functions.py:260` (also tested: test_N_000295_merge_objects_later_wins) |
| N-000297 | implemented | `pathsel/functions.py:260` (also tested: test_N_000295_merge_objects_later_wins) |
| N-000298 | implemented | `pathsel/functions.py:267` (also tested: test_N_000298_not_null_first_non_null_and_empty_is_not_null) |
| N-000299 | implemented | `pathsel/functions.py:267` (also tested: test_N_000298_not_null_first_non_null_and_empty_is_not_null) |
| N-000300 | implemented | `pathsel/functions.py:267` (also tested: test_N_000298_not_null_first_non_null_and_empty_is_not_null) |
| N-000301 | implemented | `pathsel/functions.py:277` (also tested: test_N_000301_map_includes_nulls) |
| N-000302 | implemented | `pathsel/functions.py:277` (also tested: test_N_000301_map_includes_nulls) |
| N-000303 | implemented | `pathsel/functions.py:281` (also tested: test_N_000303_sort_by_stable_ascending) |
| N-000304 | implemented | `pathsel/functions.py:281` (also tested: test_N_000303_sort_by_stable_ascending) |
| N-000305 | implemented | `pathsel/functions.py:88` (also tested: test_N_000303_sort_by_stable_ascending) |
| N-000306 | implemented | `pathsel/functions.py:290` (also tested: test_N_000306_max_by_min_by_first_on_ties) |
| N-000307 | tested | `tests/test_pathsel.py` `test_N_000306_max_by_min_by_first_on_ties` |
| N-000308 | implemented | `pathsel/functions.py:290` (also tested: test_N_000306_max_by_min_by_first_on_ties) |
| N-000309 | implemented | `pathsel/parser.py:334` (also tested: test_N_000309_function_can_be_projection_rhs) |
| N-000310 | tested | `tests/test_pathsel.py` `test_N_000309_function_can_be_projection_rhs` |
| N-000311 | implemented | `pathsel/errors.py:58` (also tested: test_N_000311_arity_refusals) |
| N-000312 | implemented | `pathsel/interpreter.py:179` (also tested: test_N_000311_arity_refusals) |
| N-000313 | implemented | `pathsel/interpreter.py:177` (also tested: test_N_000311_arity_refusals) |
| N-000314 | implemented | `pathsel/errors.py:62` (also tested: test_N_000314_type_refusals) |
| N-000315 | tested | `tests/test_pathsel.py` `test_N_000314_type_refusals` |
| N-000316 | implemented | `pathsel/functions.py:84` (also tested: test_N_000314_type_refusals) |
| N-000317 | implemented | `pathsel/functions.py:197` (also tested: test_N_000314_type_refusals) |
| N-000318 | tested | `tests/test_pathsel.py` `test_N_000314_type_refusals` |
| N-000319 | tested | `tests/test_pathsel.py` `test_N_000314_type_refusals` |
| N-000320 | implemented | `pathsel/interpreter.py:187` (also tested: test_N_000314_type_refusals) |
| N-000321 | implemented | `pathsel/parser.py:102` (also tested: test_N_000321_quoted_identifier_cannot_name_function) |
| N-000322 | implemented | `pathsel/parser.py:102` (also tested: test_N_000321_quoted_identifier_cannot_name_function) |
| N-000323 | tested | `tests/test_pathsel.py` `test_N_000323_options_mapping_type_for_constructed_hashes` |
| N-000324 | tested | `tests/test_pathsel.py` `test_N_000323_options_mapping_type_for_constructed_hashes` |
| N-000325 | implemented | `pathsel/__init__.py:58` |
| N-000326 | implemented | `pathsel/__init__.py:58` |
| N-000327 | implemented | `pathsel/__init__.py:58` |
| N-000328 | implemented | `pathsel/interpreter.py:16` (also tested: test_N_000323_options_mapping_type_for_constructed_hashes) |
| N-000329 | implemented | `pathsel/interpreter.py:63` (also tested: test_N_000323_options_mapping_type_for_constructed_hashes) |
| N-000330 | tested | `tests/test_pathsel.py` `test_N_000323_options_mapping_type_for_constructed_hashes` |
| N-000331 | tested | `tests/test_pathsel.py` `test_N_000323_options_mapping_type_for_constructed_hashes` |
| N-000332 | implemented | `pathsel/interpreter.py:63` |
| N-000333 | implemented | `pathsel/interpreter.py:63` |
| N-000334 | implemented | `pathsel/interpreter.py:63` |
| N-000335 | implemented | `pathsel/interpreter.py:16` (also tested: test_N_000335_custom_function_provider) |
| N-000336 | tested | `tests/test_pathsel.py` `test_N_000335_custom_function_provider` |
| N-000337 | tested | `tests/test_pathsel.py` `test_N_000335_custom_function_provider` |
| N-000338 | tested | `tests/test_pathsel.py` `test_N_000335_custom_function_provider` |
| N-000339 | tested | `tests/test_pathsel.py` `test_N_000335_custom_function_provider` |
| N-000340 | tested | `tests/test_pathsel.py` `test_N_000335_custom_function_provider` |
| N-000341 | implemented | `pathsel/interpreter.py:16` (also tested: test_N_000341_options_carry_mapping_and_provider_together) |
| N-000342 | implemented | `pathsel/__init__.py:82` (also tested: test_N_000342_one_shot_and_compiled_options_agree) |
| N-000343 | tested | `tests/test_pathsel.py` `test_N_000342_one_shot_and_compiled_options_agree` |
| N-000344 | implemented | `pathsel/errors.py:54` (also tested: test_N_000344_name_declared_on_other_provider_is_unknown) |
| N-000345 | implemented | `pathsel/errors.py:58` (also tested: test_N_000311_arity_refusals) |
| N-000346 | implemented | `pathsel/errors.py:62` (also tested: test_N_000345_custom_function_arity_and_type_refusals) |
| N-000347 | tested | `tests/test_pathsel.py` `test_N_000345_custom_function_arity_and_type_refusals` |
| N-000348 | tested | `tests/test_pathsel.py` `test_N_000345_custom_function_arity_and_type_refusals` |
| N-000349 | tested | `tests/test_pathsel.py` `test_N_000345_custom_function_arity_and_type_refusals` |
| N-000350 | implemented | `pathsel/functions.py:58` (also tested: test_N_000345_custom_function_arity_and_type_refusals) |
| N-000351 | tested | `tests/test_pathsel.py` `test_N_000050_pure_python_package_has_no_runtime_dependencies` |
| N-000352 | tested | `tests/test_pathsel.py` `test_N_000050_pure_python_package_has_no_runtime_dependencies` |
| N-000353 | tested | `tests/test_pathsel.py` `test_N_000050_pure_python_package_has_no_runtime_dependencies` |
| N-000354 | tested | `tests/test_pathsel.py` `test_N_000050_pure_python_package_has_no_runtime_dependencies` |
| N-000355 | tested | `tests/test_pathsel.py` `test_N_000050_pure_python_package_has_no_runtime_dependencies` |
| N-000356 | tested | `tests/test_pathsel.py` `test_N_000050_pure_python_package_has_no_runtime_dependencies` |
| N-000357 | tested | `tests/test_pathsel.py` `test_N_000050_pure_python_package_has_no_runtime_dependencies` |
| N-000358 | tested | `tests/test_pathsel.py` `test_N_000050_pure_python_package_has_no_runtime_dependencies` |
| N-000359 | tested | `tests/test_pathsel.py` `test_N_000050_pure_python_package_has_no_runtime_dependencies` |
| N-000360 | tested | `tests/test_pathsel.py` `test_N_000050_pure_python_package_has_no_runtime_dependencies` |
| N-000361 | tested | `tests/test_pathsel.py` `test_N_000050_pure_python_package_has_no_runtime_dependencies` |
| N-000362 | tested | `tests/test_pathsel.py` `test_N_000050_pure_python_package_has_no_runtime_dependencies` |
| N-000363 | tested | `tests/test_pathsel.py` `test_N_000050_pure_python_package_has_no_runtime_dependencies` |
| N-000364 | tested | `tests/test_pathsel.py` `test_N_000050_pure_python_package_has_no_runtime_dependencies` |
| N-000365 | tested | `tests/test_pathsel.py` `test_N_000050_pure_python_package_has_no_runtime_dependencies` |
| N-000366 | implemented | `pathsel/__init__.py:7` |
| N-000367 | implemented | `pathsel/__init__.py:17` |
| N-000368 | implemented | `pathsel/__init__.py:7` |
| N-000369 | tested | `tests/test_pathsel.py` `test_N_000050_pure_python_package_has_no_runtime_dependencies` |
| N-000370 | tested | `tests/test_pathsel.py` `test_N_000050_pure_python_package_has_no_runtime_dependencies` |
| N-000371 | implemented | `pathsel/__init__.py:7` (also tested: test_N_000371_import_has_no_side_effects) |
| N-000372 | implemented | `pathsel/__init__.py:3` (also tested: test_N_000372_root_names_search_and_compile) |
| N-000373 | implemented | `pathsel/__init__.py:3` (also tested: test_N_000372_root_names_search_and_compile) |
| N-000374 | implemented | `pathsel/__init__.py:4` (also tested: test_N_000372_root_names_search_and_compile) |
| N-000375 | implemented | `pathsel/__init__.py:92` (also tested: test_N_000016_search_entry_takes_expression_and_document) |
| N-000376 | tested | `tests/test_pathsel.py` `test_N_000016_search_entry_takes_expression_and_document` |
| N-000377 | implemented | `pathsel/__init__.py:58` |
| N-000378 | tested | `tests/test_pathsel.py` `test_N_000016_search_entry_takes_expression_and_document` |
| N-000379 | implemented | `pathsel/__init__.py:82` |
| N-000380 | implemented | `pathsel/__init__.py:82` |
| N-000381 | implemented | `pathsel/__init__.py:82` |
| N-000382 | implemented | `pathsel/__init__.py:92` |
| N-000383 | implemented | `pathsel/__init__.py:87` (also tested: test_N_000017_compile_entry_returns_reusable_parsed_expression) |
| N-000384 | implemented | `pathsel/__init__.py:68` (also tested: test_N_000017_compile_entry_returns_reusable_parsed_expression) |
| N-000385 | implemented | `pathsel/__init__.py:68` |
| N-000386 | implemented | `pathsel/__init__.py:58` |
| N-000387 | implemented | `pathsel/__init__.py:58` |
| N-000388 | implemented | `pathsel/__init__.py:82` (also tested: test_N_000017_compile_entry_returns_reusable_parsed_expression) |
| N-000389 | implemented | `pathsel/options.py:1` |
| N-000390 | implemented | `pathsel/options.py:1` |
| N-000391 | implemented | `pathsel/options.py:1` |
| N-000392 | implemented | `pathsel/options.py:1` |
| N-000393 | implemented | `pathsel/functions.py:112` (also tested: test_N_000393_provider_signature_declaration_and_return_value_kept) |
| N-000394 | implemented | `pathsel/functions.py:115` (also tested: test_N_000393_provider_signature_declaration_and_return_value_kept) |
| N-000395 | implemented | `pathsel/functions.py:112` (also tested: test_N_000393_provider_signature_declaration_and_return_value_kept) |
| N-000396 | implemented | `pathsel/functions.py:112` (also tested: test_N_000393_provider_signature_declaration_and_return_value_kept) |
| N-000397 | implemented | `pathsel/functions.py:115` (also tested: test_N_000335_custom_function_provider) |
| N-000398 | implemented | `pathsel/functions.py:326` (also tested: test_N_000335_custom_function_provider) |
| N-000399 | implemented | `pathsel/functions.py:326` (also tested: test_N_000335_custom_function_provider) |
| N-000400 | implemented | `pathsel/functions.py:326` (also tested: test_N_000335_custom_function_provider) |
| N-000401 | implemented | `pathsel/functions.py:28` (also tested: test_N_000393_provider_signature_declaration_and_return_value_kept) |
| N-000402 | implemented | `pathsel/functions.py:22` (also tested: test_N_000393_provider_signature_declaration_and_return_value_kept) |
| N-000403 | implemented | `pathsel/functions.py:28` (also tested: test_N_000393_provider_signature_declaration_and_return_value_kept) |
| N-000404 | implemented | `pathsel/functions.py:28` (also tested: test_N_000393_provider_signature_declaration_and_return_value_kept) |
| N-000405 | implemented | `pathsel/errors.py:3` (also tested: test_N_000105_refusals_are_value_errors_not_null) |
| N-000406 | implemented | `pathsel/errors.py:4` |
| N-000407 | implemented | `pathsel/errors.py:4` |
| N-000408 | implemented | `pathsel/errors.py:4` |
| N-000409 | implemented | `pathsel/errors.py:26` (also tested: test_N_000087_empty_text_is_empty_expression_refusal) |
| N-000410 | implemented | `pathsel/errors.py:38` (also tested: test_N_000090_incomplete_expressions_refuse) |
| N-000411 | implemented | `pathsel/errors.py:42` (also tested: test_N_000094_syntax_failures_refuse) |
| N-000412 | implemented | `pathsel/errors.py:10` (also tested: test_N_000096_token_level_failures_are_specific_syntax_kind) |
| N-000413 | implemented | `pathsel/errors.py:8` (also tested: test_N_000096_token_level_failures_are_specific_syntax_kind) |
| N-000414 | implemented | `pathsel/errors.py:8` (also tested: test_N_000096_token_level_failures_are_specific_syntax_kind) |
| N-000415 | implemented | `pathsel/errors.py:11` (also tested: test_N_000152_zero_slice_step_refuses) |
| N-000416 | implemented | `pathsel/errors.py:13` (also tested: test_N_000264_unknown_function_refuses_on_evaluation) |
| N-000417 | implemented | `pathsel/errors.py:58` |
| N-000418 | implemented | `pathsel/errors.py:62` |
| N-000419 | implemented | `pathsel/errors.py:62` |
| N-000420 | implemented | `pathsel/errors.py:13` |
| N-000421 | implemented | `pathsel/errors.py:30` (also tested: test_N_000102_position_reports_offset_of_failing_token) |
| N-000422 | implemented | `pathsel/errors.py:30` (also tested: test_N_000102_position_reports_offset_of_failing_token) |
| N-000423 | implemented | `pathsel/values.py:15` (also tested: test_N_000231_expression_reference_is_non_null_value) |
