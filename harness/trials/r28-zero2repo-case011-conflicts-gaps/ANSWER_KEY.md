# Answer key: 12 conflicts and 12 gaps planted in case011, round 28 (never shown to an agent)

> Written 2026-11-11, after the step-1 checks and before any compile output, review or agent run was read.
> The planted Markdown is made by `notes/plant.py work/spec-planted` with the 24 kept ids (`KEPT_C`,
> `KEPT_G` in the script) from Zero2Repo case011's `public/` (`pathsel`, upstream `jmespath.py`); it stays in
> git-ignored `work/` (Zero2Repo has no licence file). 6 909 words (7 002 before). sha256 of the planted
> files (`work/spec-planted.sha256`): `Full_PRD.md` `8deb86c2fee415fb…`, `Interface_Contract.md`
> `73ea1d6c770a09b6…`, `Hardware_Requirements.md` `9d43026e083a277e…` (unchanged). Only short phrases are
> quoted here.

Side **A** is the text the case already had: the reference library's behaviour and what the hidden
tests check. Side **B** is the planted sentence: one place edited, in the spec's voice, no marker. A
**gap** removes every statement of a fact the hidden tests still check. Lines are those of the planted
`Full_PRD.md` (all 12 conflicts are within the PRD).

## Conflicts (12)

| Item | Distance | A (kept) | B (planted) | Footprint |
|---|---|---|---|---|
| C02 | same file | 242: `join` — "the empty array yields the empty string" | 230 (FP-07 intro): "`join` of an empty array yields null" | 1 |
| C05 | same file, far | 252: `not_null` — "(an empty array or empty string is not null)" | 23 (Terminology, Null): "An empty string or an empty array counts as null for `not_null`" | 2 |
| C08 | same file, far | 240: `length` — "the number of Unicode characters (not bytes) of a string" | 27 (Terminology, String): "its length is its number of UTF-8 bytes" | 3 |
| C12 | same file | 188: "A multiselect list or hash whose current value is null yields null" | 187: "On a null current value it still builds one element per expression" (multiselect list) | 3 |
| C14 | same file | 138: "A slice on a value that is not an array yields null" | 148: "A slice of a value that is not an array is the empty array" | 2 |
| C15 | same file | 175: "A filter on a non-array yields null" (also 161, "otherwise the result is null") | 215 (FP-06): "A filter applied to anything but an array yields the empty array" | 2 |
| C17 | same file, far | 159: "An object wildcard on a value that is not an object yields null" | 32 (Terminology, Projection): "An object wildcard applied to a non-object is the empty array" | 3 |
| C19 | same file | 192: raw string — "No JSON escapes are processed" | 198: "A `\uXXXX` escape inside a raw string literal is decoded to its character" | 3 |
| C20 | same file | 146: "A slice whose step is 0 does not succeed on either entry" (the zero-slice-step kind; also Terminology and the Contract) | 133: "A step of 0 selects nothing: the result is the empty array" | 3 |
| C22 | same file, far (and Contract) | 193: "Searching an expression reference on its own succeeds and yields a non-null value" (also Contract, "Expression reference value") | 29 (Terminology): "Outside a function argument it evaluates to null" | 3 |
| C24 | same file, far | 219: "A lone `=` is a token-level syntax failure" | 37 (Terminology, grammar-level): "A single `=` is a grammar-level failure of this kind" | 1 |
| C26 | same file, far | 247: `to_number` — "a string that is an integer numeral becomes that integer" | 26 (Terminology, Number): "A number made from a string by `to_number` is always a floating-point value" | 2 |

## Gaps (12)

| Item | Fact removed (upstream value) | Removed from | Alternative probed | Footprint |
|---|---|---|---|---|
| G03 | `sort` of the empty array is the empty array | FP-07 (`sort` bullet) | null | 2 |
| G22 | an ordering comparison with an array, object, boolean or null side yields null | FP-06 (normal bullet and boundary bullet) | false | 3 |
| G25 | in a raw string, a backslash pair other than backslash-quote is kept as written (both characters) | FP-05 (raw string bullet) | `\\` stands for one backslash | 1 |
| G27 | `to_string` of a non-JSON host value: its host text as a JSON string encoding (quoted) | FP-07 (`to_string` bullet) | the plain host text | 2 |
| G28 | a host decimal is refused (invalid type) where a function needs a number | Non-functional constraints (data model); FP-07 boundary ("a host decimal or boolean where") | accepted | 1 |
| G29 | `merge` returns the host's ordinary mapping, whatever mapping type the options supply | FP-07 (`merge`: "host ordinary"); FP-08 (the "including `merge`" sentence) | the supplied mapping type | 2 |
| G34 | the supplied mapping type builds every multiselect hash at any nesting depth | FP-08 ("Every … — at any nesting depth —" → "A …") | only the outermost hash | 1 |
| G35 | multiselect hash keys are inserted in declaration order | FP-05 (hash bullet); FP-08 (mapping-type bullet) | sorted keys | 2 |
| G54 | a backslash-backtick inside a JSON literal stands for a backtick | FP-05 (JSON literal bullet: two spans) | no such escape | 2 |
| G60 | `sum` of the empty array is 0 | FP-07 (`sum` bullet) | null | 3 |
| G61 | `sort_by` of the empty array is the empty array | FP-07 (`sort_by` bullet) | null | 2 |
| G69 | options apply to their own search only (a later search without them sees none) | FP-08 (the "Options apply … and to nothing else" sentence) | a parsed expression keeps the last options it was given | 1 |

**Still implied, recorded before any run.** G28: Terminology still defines a number as "an integer or a
floating-point value" and says host decimals "participate as numbers in comparisons", which can be read
as excluding decimals elsewhere; kept. G34: "A multiselect hash the evaluation constructs is built as an
instance of exactly that type" can be read generically (every hash); kept. G69: FP-08's boundary still
says a name "declared only on some other provider" is unknown, which covers part of the fact (a
different provider), not a later search without options; kept. G22: FP-06 still says ordering compares
"two numbers numerically, or two strings", silent on other operands.

**Footprint union: 50 tests, none shared by two items; the base build fails none.** The **core** (set 1)
is the other **271** of 321 tests. Distances: all 12 conflicts within `Full_PRD.md`; far (Terminology
against a feature point) 6: C05, C08, C17, C22, C24, C26; the other 6 in the same or a neighbouring
feature point.

## Candidates tried and dropped (step 1, no model call)

| Item | Behaviour | Why dropped |
|---|---|---|
| C01 | `avg([])` 0 | footprint 5 |
| C03 | `merge`: first key kept | shares `runtime_merge_and_not_null` with C05 (larger footprint, 3 vs 2) |
| C04 | `max`/`min` of `[]` refused | footprint 4 |
| C06 | `map` drops nulls | footprint 4 |
| C07 | `max_by`/`min_by` last on ties | footprint 0 |
| C09 | strings not ordered | shares two ordering tests with C10 and G22 (all footprint 3; tie, conflicts had more survivors) |
| C10 | decimals not ordered | the same shared tests |
| C11 | hash omits null-valued keys | footprint 4 |
| C13 | empty slice → null | shares the zero-step tests with C20 (tie, same kind; the copy's footprint reached zero-step tests as a side effect) |
| C16 | list wildcard on non-array → `[]` | footprint 5 |
| C18 | index on a string selects a character | footprint 4 |
| C21 | quoted identifier calls a function | shares `compile_path_function_failures` with G27 (tie, conflicts had more survivors) |
| C23 | compile refuses unknown names | footprint 14 |
| C25 | hyphen grammar-level | footprint 5 |
| C27 | `to_string` non-ASCII unescaped | footprint 0 |
| G04 | `sort_by` ties reversed | shares `runtime_sort_by_max_by_min_by` with G61 (larger footprint) |
| G07 | `to_string` with spaces | shares two conversion tests with C26 (larger footprint) |

## How each side is read (`notes/probe.py`, black box, from this key and the Contract only)

One probe per item on the saved code, in a container with no network (`notes/probe.sh`). Check
(`work/probe_check.log`): the base reads A on all 41 candidates; each alternative copy reads B on its own
item and A on the other 40 (0 mismatches; first pass: the G69 probe used a custom function, which the C23
copy refuses at compile time; the probe now uses a mapping type).
