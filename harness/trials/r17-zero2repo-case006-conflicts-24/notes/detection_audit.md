# Detection audit (round 17) — for the owner

One table per planted item. **Lines** are every line of the run's `NOTES.md` that matches the
item's keywords (or, in export runs, one of its conflict ids), cut at 300 characters. **Reading**
is the assistant's (`detection.tsv`): named · stated sides · side the probe found in the code.
**Named** needs both sides' content stated as disagreeing (TRIAL.md, "Detection rule"); a CF id
with a topic only is not enough. Fill **Owner** with `agree` or your reading. A line about
something else that happens to match the keywords is not a detection. `r17-haiku-markdown-2` stopped early
(partial build) and is left out, as round 15's stopped run was.

## C01 — A: PRD 403: runner "removes that directory on exit" · B: PRD 403: "always left in place after the block ends"

Conflict ids in the export: CF-000154

| Run | Lines from NOTES.md | Reading | Owner |
|---|---|---|---|
| r17-haiku-markdown-1 | \| `testing.py` \| `CliRunner`, `Result`, `isolated_filesystem` \|<br>14. **`CliRunner.isolated_filesystem` cleanup.** The spec says the runner "removes that directory<br>on exit" when no parent is given, and also that the directory is "always left in place after<br>the block ends". Built: left in place after the block; with no `temp_dir` it is removed at | yes · AB · B | |
| r17-haiku-markdown-3 | *(none)* | no · - · A | |
| r17-sonnet-markdown-1 | \| `isolated_filesystem`: directory removed vs "always left in place" \| Removed when no parent is given; kept when `temp_dir` is given. \| | yes · AB · A | |
| r17-sonnet-markdown-2 | \| `isolated_filesystem` cleanup \| PRD says both "removed when no parent" and "always left" \| Removed when no `temp_dir` is given; kept otherwise. \| | yes · AB · A | |
| r17-sonnet-markdown-3 | \| 19 \| `isolated_filesystem`: "removed when no parent" vs "always left in place". \| Removed when no `temp_dir`; kept when a parent is given. \| | yes · AB · A | |
| r17-haiku-export-1 | \| CF-000154 \| `isolated_filesystem` without a parent: removed on exit (FP-14 first sentence) vs always left in place (FP-14 last sentence) \| Always left in place. \| | yes · AB · B | |
| r17-haiku-export-2 | \| `testing.py` \| `CliRunner`, `Result`, `isolated_filesystem` \| 13, 32 \|<br>- **Pack 13 (N-001038–1044):** `CliRunner.invoke` (args, input, env with `None` unset, extra context settings), `Result` attributes, `isolated_filesystem`.<br>\| CF-000154 \| Isolated filesystem: removed on exit vs always left in place \| Always left in place (so files can be inspected) \| | yes · AB · B | |
| r17-haiku-export-3 | \| CF-000154 \| `isolated_filesystem`: removed on exit (no parent) vs always left in place \| removed when no `temp_dir` is given; left in place when one is (the clause about the parent case) \| | yes · AB · A | |
| r17-sonnet-export-1 | \| FP-14 (CF-154) \| isolated filesystem directory removed vs left in place \| removed on exit when no parent given; kept when `temp_dir` is given \| | yes · AB · A | |
| r17-sonnet-export-2 | \| 154 \| isolated_filesystem \| removed on exit when no `temp_dir`; kept when `temp_dir` given \| | no · - · A | |
| r17-sonnet-export-3 | \| 154 \| isolated_filesystem cleanup \| directory removed on exit when no `temp_dir` given; kept when a parent is supplied \| | no · - · A | |

## C02 — A: PRD 143: command line, "then environment, then the default map" · B: Contract 234: default-map values "take precedence over environment variables"

Conflict ids in the export: CF-000034

| Run | Lines from NOTES.md | Reading | Owner |
|---|---|---|---|
| r17-haiku-markdown-1 | *(none)* | no · - · A | |
| r17-haiku-markdown-3 | *(none)* | no · - · A | |
| r17-sonnet-markdown-1 | *(none)* | no · - · A | |
| r17-sonnet-markdown-2 | *(none)* | no · - · A | |
| r17-sonnet-markdown-3 | *(none)* | no · - · A | |
| r17-haiku-export-1 | \| CF-000034, CF-000072 \| Environment vs default map precedence \| Command line, then environment, then default map, then declared default (FP-03 ranking). \| | no · - · A | |
| r17-haiku-export-2 | \| CF-000034, CF-000072 \| Source precedence: environment above default map, or the reverse \| Command line > prompt > environment > default map > declared default (PRD FP-03) \| | yes · AB · A | |
| r17-haiku-export-3 | \| CF-000034, CF-000072 \| Environment vs default map precedence: Contract says default map beats env; FP-03 ranks env above default map \| environment wins over default map (FP-03 ranking) \| | yes · AB · A | |
| r17-sonnet-export-1 | \| FP-03 vs Contract s6 (CF-34, 72) \| env vs default map precedence \| prompt > command line > environment > default map > declared default \| | no · - · A | |
| r17-sonnet-export-2 | \| 034/072 \| env vs default map precedence \| command line > environment > default map > declared default \| | no · - · A | |
| r17-sonnet-export-3 | \| 34, 72 \| default map vs environment precedence \| command line > environment > default map > declared default (PRD) \| | no · - · A | |

## C03 — A: PRD 145: "A missing parameter still runs its callback" · B: PRD 28 (Terminology): callback "not called for a parameter that was omitted"

Conflict ids in the export: CF-000155

| Run | Lines from NOTES.md | Reading | Owner |
|---|---|---|---|
| r17-haiku-markdown-1 | 2. **Callback for an omitted parameter.** PRD glossary says a parameter callback is not called<br>its callback". Built: the callback runs for every parameter, receiving `None`, `()` or the | yes · AB · A | |
| r17-haiku-markdown-3 | \| 7 \| PRD terminology (callbacks) vs. PRD FP-03 \| Terminology: a parameter callback is not called for an omitted parameter with no value. FP-03: a missing parameter still runs its callback so it can default from an earlier value. \| FP-03. Callbacks run for every parameter, including omitted ones. \| | yes · AB · A | |
| r17-sonnet-markdown-1 | \| Parameter callback for an omitted parameter: Terminology "not called", FP-03 "still runs" \| Called (with `None`), so it can derive a default from earlier values. \|<br>\| Chaining group, `standalone_mode=False` \| Returns the list of child return values even when a result callback exists (the callback is still called). \| | yes · AB · A | |
| r17-sonnet-markdown-2 | \| Parameter callback on omitted value \| Terminology: not called; FP-03: called with `None` \| Called (with `None`/`()`). \|<br>\| Chaining group return with standalone off \| Contract: list of child returns even with a result callback \| Returns the list; the result callback still runs. \| | yes · AB · A | |
| r17-sonnet-markdown-3 | \| 17 \| Parameter callback on an omitted parameter: Terminology says not called; FP-03 says it still runs (value `None`). \| Called with `None`. \| | yes · AB · A | |
| r17-haiku-export-1 | \| CF-000155 \| Callback for an omitted parameter: not called (terminology) vs runs and may default from earlier values (FP-03) \| Runs for every parameter, including omitted ones. \|<br>whether or not a result callback is registered. The result callback still runs.<br>distribution that is not installed cannot be detected (`RuntimeError` at callback time). | yes · AB · A | |
| r17-haiku-export-2 | - **Pack 07 (N-000850–880):** `command`, `group`, `Group`, `CommandCollection`, `add_command`, `command()`/`group()` child helpers, `result_callback()`, `list_commands`/`get_command` override points, `main`/`__call__`.<br>\| CF-000155 \| Callback for a missing parameter: runs vs not called \| Runs (PRD FP-03: a missing parameter still runs its callback, so it can default from earlier values) \|<br>- Completion output: `@path:file:<token>` / `@path:dir:<token>` for path requests, `value\thelp` for zsh and fish; unknown instruction → message on stderr, exit 2, callback not run. | yes · AB · A | |
| r17-haiku-export-3 | \| CF-000155 \| Callback for an omitted parameter: runs (FP-03) vs not run (terminology) \| runs (FP-03) \|<br>- `Context.invoke(cmd, **values)` passes the caller's values and fills the target's omitted parameters with their defaults (so the callback signature still works); `forward` merges the current parameters first.<br>- A group's callback runs after the subcommand name is resolved and before the child's own arguments are parsed. In chain mode the children are parsed first, then the group callback runs. | yes · AB · A | |
| r17-sonnet-export-1 | \| Terminology vs FP-03 (CF-155) \| callback for omitted parameter \| callback runs (receives `None`/`()`) \| | no · - · A | |
| r17-sonnet-export-2 | \| 155 \| callback for omitted parameter \| callback still runs \| | no · - · A | |
| r17-sonnet-export-3 | \| 155 \| callback for omitted parameter \| callback is called with the absent value (so it can default from earlier params) \| | no · - · A | |

## C04 — A: PRD 107: max content width "defaults to 80 columns" · B: PRD 340: "maximum content width of 100 columns"

Conflict ids in the export: CF-000087

| Run | Lines from NOTES.md | Reading | Owner |
|---|---|---|---|
| r17-haiku-markdown-1 | 4. **Help width.** FP-02 says the maximum content width is 80; FP-11 says 100. Built: 80. | yes · AB · A | |
| r17-haiku-markdown-3 | \| 3 \| PRD FP-02 vs. PRD FP-11 (width) \| FP-02: help pages cap auto-detected width at 80 columns. FP-11: help pages and wrapped text use 100 columns. \| Help pages use the context's `max_content_width` (default 80). `formatting.wrap_text` defaults to 100, as FP-11 says for wrapped text. \| | yes · AB · A | |
| r17-sonnet-markdown-1 | \| Default `max_content_width`: PRD FP-02 80, FP-11 100 \| 80. Under `CliRunner` the width is forced to 80. \| | yes · AB · A | |
| r17-sonnet-markdown-2 | \| Max content width \| FP-02: 80; FP-11: 100 \| 80. \| | yes · AB · A | |
| r17-sonnet-markdown-3 | \| 11 \| Max content width: PRD FP-02 says 80, FP-11 says 100. \| 80 (`HelpFormatter`; `wrap_text` default width 78). Inside `CliRunner` the width is 80. \| | yes · AB · A | |
| r17-haiku-export-1 | \| CF-000087 \| Default maximum content width: 80 (FP-02) vs 100 (FP-11 / constraint) \| 80 for help pages. `wrap_text` has its own width argument (default 78). \| | yes · AB · A | |
| r17-haiku-export-2 | \| CF-000087 \| Default maximum content width: 80 vs 100 \| 80 for auto-detected width; an explicit terminal width is used as given \| | yes · AB · A | |
| r17-haiku-export-3 | \| CF-000087 \| Default maximum content width: 80 (FP-02) vs 100 (FP-11) \| help pages use 80 (`max_content_width`); `wrap_text` default width is 100 (FP-11) \| | yes · AB · A | |
| r17-sonnet-export-1 | \| FP-05 vs Contract s5 (CF-16, 92, 100, 107) \| clamp at open bound; FloatRange clamp \| IntRange open bound -> adjacent integer inside range; FloatRange with clamp and an open bound raises `TypeError` at construction \|<br>\| FP-02 vs FP-11 (CF-87) \| default max content width 80 vs 100 \| 80 (help layout and `wrap_text`'s formatter) \| | yes · AB · A | |
| r17-sonnet-export-2 | \| 016/092/100/107 \| clamp with open bounds \| IntRange: adjacent integer inside range; FloatRange: clamp with an open bound raises `DeclarationError` at construction \|<br>\| 087 \| default max content width \| 80 \| | no · - · A | |
| r17-sonnet-export-3 | \| 100, 107 \| FloatRange clamp with open bound: refused (PRD) vs clamps to the bound (contract) \| `TypeError` at construction (PRD) \|<br>\| 87 \| max content width 80 vs 100 \| 80 (the runner also forces an 80 column width unless `terminal_width` is given) \| | yes · AB · A | |

## C05 — A: PRD 108: option metavar "is the type name in uppercase" · B: PRD 108: example `--count COUNT`

Conflict ids in the export: CF-000115

| Run | Lines from NOTES.md | Reading | Owner |
|---|---|---|---|
| r17-haiku-markdown-1 | 3. **Default metavar for typed options.** PRD FP-02 gives `--count COUNT` as the example, but<br>`--count INTEGER`. | yes · AB · A | |
| r17-haiku-markdown-3 | - Default option metavars: `TEXT` for strings, `INTEGER` for ints, `FLOAT`, `BOOLEAN`, `UUID`, `DATETIME`; choices show `[a\|b]`. | no · - · A | |
| r17-sonnet-markdown-1 | \| Integer option metavar: PRD example `--count COUNT`, rule "type name upper-case" \| Type name: `--count INTEGER`. \| | yes · AB · A | |
| r17-sonnet-markdown-2 | \| Default option metavar \| PRD example shows `COUNT`; text says type name \| Type name upper-cased (`INTEGER`, `TEXT`, ...). \| | yes · AB · A | |
| r17-sonnet-markdown-3 | \| 21 \| Integer option metavar: PRD example `--count COUNT`, rule "type name uppercase". \| Type name: `--count INTEGER`. \| | yes · AB · A | |
| r17-haiku-export-1 | \| CF-000115 \| Option metavar: type name in uppercase (`INTEGER`) vs example `--count COUNT` \| Type name (`--count INTEGER`), following the general rule. The example was not followed. \|<br>Option entries list names, then metavar, then help, then bracketed extras (`[default: x]`, | yes · AB · A | |
| r17-haiku-export-2 | - **Pack 08 (N-000881–935):** `option` and `argument` keywords, on/off pairs, delivered-value table (scalar, tuple, `()`, `None`, flag, count), `BadParameter`, ready-made `help_option`, `version_option`, `custom_version_option`, `password_option`, `confirmation_option`.<br>\| CF-000115 \| Metavar of `--count` with an integer type: `INTEGER` vs `COUNT` \| The type name uppercased (`INTEGER`); the example in the PRD is not followed \| | yes · AB · A | |
| r17-haiku-export-3 | \| CF-000115 \| Default metavar of an integer option: `INTEGER` (rule) vs `COUNT` (example) \| `INTEGER` (the stated rule) \| | yes · AB · A | |
| r17-sonnet-export-1 | \| FP-02 (CF-115) \| default metavar: type name upper-case vs `--count COUNT` \| type name upper-case (`--count INTEGER`) \| | yes · AB · A | |
| r17-sonnet-export-2 | \| 048 \| omitted count option \| `0` \|<br>\| 115 \| default option metavar \| type name upper-cased (`--count INTEGER`) \| | no · - · A | |
| r17-sonnet-export-3 | \| 115 \| metavar "type name" vs `--count COUNT` \| built-in scalar types show the parameter's destination name upper-cased (`--count COUNT`); custom `ParamType` shows its `name` upper-cased; Choice shows `[a\|b]` \| | yes · AB · B | |

## C06 — A: PRD 102: form feed, "text after that character is omitted" · B: Contract 74: form feed "dropped and the text after it is kept"

Conflict ids in the export: CF-000156

| Run | Lines from NOTES.md | Reading | Owner |
|---|---|---|---|
| r17-haiku-markdown-1 | 10. **Docstring form feed.** PRD: text after `\f` is omitted from help. Interface: the `\f`<br>is dropped and the text kept. Built: truncate at `\f` (PRD). | yes · AB · A | |
| r17-haiku-markdown-3 | *(none)* | no · - · A | |
| r17-sonnet-markdown-1 | \| `help=` with a form feed: PRD (docstring) truncates, Contract (`help` keyword) drops the character and keeps the rest \| Docstrings are truncated at `\f`; an explicit `help=` only loses the `\f` character. \| | yes · AB · B | |
| r17-sonnet-markdown-2 | \| Form feed in help \| PRD: text after is omitted; Contract: dropped, text after kept \| Docstring-derived help is cut at the form feed; an explicit `help=` just drops the character. \| | yes · AB · B | |
| r17-sonnet-markdown-3 | \| 12 \| Form feed in `help`: contract "text after it is kept"; PRD "text after is omitted". \| Text after the form feed is omitted, the form feed itself is dropped. \| | yes · AB · A | |
| r17-haiku-export-1 | \| CF-000156 \| Form feed: docstring text after it is omitted (FP-02) vs kept (Interface, `help=` keyword) \| Docstring: truncated at the form feed. Explicit `help=` keyword: the form feed is dropped and the text after it is kept. \| | yes · AB · B | |
| r17-haiku-export-2 | \| CF-000156 \| Form feed in a docstring: text after it kept vs omitted \| Text after the form feed is omitted (PRD FP-02) \| | yes · AB · A | |
| r17-haiku-export-3 | \| CF-000156 \| Form feed in a docstring: text after it omitted (FP-02) vs kept (Contract) \| text after it omitted; the form feed itself removed \| | yes · AB · A | |
| r17-sonnet-export-1 | \| FP-02 vs Contract s3 (CF-156) \| form feed in help \| text after the form feed is dropped \| | no · - · A | |
| r17-sonnet-export-2 | \| 156 \| form feed in help \| text after it is dropped \| | no · - · A | |
| r17-sonnet-export-3 | \| 156 \| form feed in help \| text after the form feed is dropped \| | no · - · A | |

## C07 — A: PRD 137: counting option "(zero if omitted)" · B: Contract 177: "or `None` when the option was omitted"

Conflict ids in the export: CF-000048

| Run | Lines from NOTES.md | Reading | Owner |
|---|---|---|---|
| r17-haiku-markdown-1 | 1. **Omitted counting option.** PRD FP-03 says zero when omitted; Interface §2 says `None`.<br>3. **Default metavar for typed options.** PRD FP-02 gives `--count COUNT` as the example, but<br>`--count INTEGER`. | yes · AB · A | |
| r17-haiku-markdown-3 | *(none)* | no · - · B | |
| r17-sonnet-markdown-1 | \| Counting option omitted: PRD "zero", Contract "`None`" \| `None` (an explicit `default=` is honoured). \|<br>\| Integer option metavar: PRD example `--count COUNT`, rule "type name upper-case" \| Type name: `--count INTEGER`. \| | yes · AB · B | |
| r17-sonnet-markdown-2 | \| Counting option omitted \| PRD: `0`; Contract: `None` \| `None` when omitted (Contract). \|<br>\| Default option metavar \| PRD example shows `COUNT`; text says type name \| Type name upper-cased (`INTEGER`, `TEXT`, ...). \| | yes · AB · B | |
| r17-sonnet-markdown-3 | \| 4 \| Counting option omitted: contract `None`; PRD "zero if omitted". \| `0`. \|<br>\| 21 \| Integer option metavar: PRD example `--count COUNT`, rule "type name uppercase". \| Type name: `--count INTEGER`. \| | yes · AB · A | |
| r17-haiku-export-1 | \| CF-000048 \| Counting option when omitted: 0 (FP-03) vs `None` (Interface) \| 0 (or the declared default). \|<br>\| CF-000115 \| Option metavar: type name in uppercase (`INTEGER`) vs example `--count COUNT` \| Type name (`--count INTEGER`), following the general rule. The example was not followed. \|<br>\| CF-000157, CF-000151 \| Boolean flag from environment with an unrecognised non-empty value: usage error (FP-03, FP-05) vs turns the flag off (FP-05) \| Usage error for boolean flags. For a flag with a non-boolean flag value, an unrecognised value counts as unset. \| | yes · AB · A | |
| r17-haiku-export-2 | - **Pack 08 (N-000881–935):** `option` and `argument` keywords, on/off pairs, delivered-value table (scalar, tuple, `()`, `None`, flag, count), `BadParameter`, ready-made `help_option`, `version_option`, `custom_version_option`, `password_option`, `confirmation_option`.<br>\| CF-000048 \| Counting option omitted: `0` vs `None` \| `0` (PRD FP-03) \|<br>\| CF-000115 \| Metavar of `--count` with an integer type: `INTEGER` vs `COUNT` \| The type name uppercased (`INTEGER`); the example in the PRD is not followed \| | yes · AB · A | |
| r17-haiku-export-3 | \| CF-000048 \| Counting option omitted: `0` (FP-03) vs `None` (Contract) \| `0` \|<br>\| CF-000115 \| Default metavar of an integer option: `INTEGER` (rule) vs `COUNT` (example) \| `INTEGER` (the stated rule) \|<br>## Checklist accounting | yes · AB · A | |
| r17-sonnet-export-1 | ## Checklist accounting<br>\| FP-03 vs Contract s4 (CF-48) \| omitted counting option \| `0` \|<br>\| FP-02 (CF-115) \| default metavar: type name upper-case vs `--count COUNT` \| type name upper-case (`--count INTEGER`) \| | no · - · A | |
| r17-sonnet-export-2 | \| 048 \| omitted count option \| `0` \|<br>\| 115 \| default option metavar \| type name upper-cased (`--count INTEGER`) \| | no · - · A | |
| r17-sonnet-export-3 | \| 48 \| counting option omitted: 0 vs None \| `0` \|<br>\| 115 \| metavar "type name" vs `--count COUNT` \| built-in scalar types show the parameter's destination name upper-cased (`--count COUNT`); custom `ParamType` shows its `name` upper-cased; Choice shows `[a\|b]` \|<br>## Checklist accounting | yes · AB · A | |

## C08 — A: PRD 138: omitted repeatable "receives an empty tuple" (also Contract 174) · B: PRD 84: omitted repeatable "is passed as an absent value"

Conflict ids in the export: CF-000010

| Run | Lines from NOTES.md | Reading | Owner |
|---|---|---|---|
| r17-haiku-markdown-1 | *(none)* | no · - · A | |
| r17-haiku-markdown-3 | - Multi-value (`nargs`) options combined with `multiple=True` are supported; a variadic argument combined with a later fixed argument takes the tokens left after reserving the later ones. | no · - · A | |
| r17-sonnet-markdown-1 | *(none)* | no · - · A | |
| r17-sonnet-markdown-2 | *(none)* | no · - · A | |
| r17-sonnet-markdown-3 | *(none)* | no · - · A | |
| r17-haiku-export-1 | Build: pure Python package under `src/optlyn`, no runtime dependencies, Python 3.10+.<br>\| CF-000010 \| Omitted repeatable option (or variadic argument) with no default: "absent value" (FP-01) vs "empty tuple, not absent" (FP-03) \| Delivers `()`. \| | yes · AB · A | |
| r17-haiku-export-2 | - Package: `src/optlyn/` (src layout, Python 3.10+, standard library only).<br>\| `core.py` \| `Parameter`, `Option`, `Argument`, `Context`, `Command`, `Group`, `CommandCollection`; parsing pipeline; help page; `main` \| 07, 08, 10, 19–24, 31, 32 \|<br>\| `decorators.py` \| `command`, `group`, `option`, `argument`, ready-made options, `pass_*`, `make_pass_decorator` \| 07, 08, 10 \|<br>\| `_globals.py` \| thread-local current-context stack \| 10, 17 \|<br>- **Pack 10 (N-000950–980):** `Context` settings and members, `pass_context`, `pass_obj`, `make_pass_decorator`, `get_current_context(silent=…)`, per-thread stack.<br>\| CF-000010 \| Omitted repeatable option: absent value vs empty tuple \| Empty tuple `()` (PRD FP-03, contract table) \| | yes · AB · A | |
| r17-haiku-export-3 | - `pyproject.toml` — setuptools PEP 517 build, src layout, zero runtime dependencies, Python ≥ 3.10.<br>\| CF-000010 \| Omitted repeatable option with no default: "absent value" (FP-01) vs "empty tuple, not absent" (FP-03) \| `()` (empty tuple), per FP-03 \|<br>\| 03 \| Hardware requirements · Execution profiles \| N-000780–N-000789 (10) \| pyproject.toml (src layout, setuptools PEP 517) \| implemented; Linux only exercised; macOS/Windows branches (get_app_dir, launch, argv expansion) not run \|<br>\| 10 \| Contract §6 Invocation context \| N-000950–N-000980 (31) \| core.py Context; decorators.py pass_context/pass_obj/make_pass_decorator \| implemented \|<br>\| 15 \| PRD terminology \| N-000015–N-000024 (10) \| whole package \| satisfied \|<br>\| 28 \| FP-10 Chaining and pipelines \| N-000591–N-000617 (27) \| core.py Group._invoke_chain \| implemented \| | yes · AB · A | |
| r17-sonnet-export-1 | Package: `src/optlyn` (pure Python, no dependencies, Python 3.10+). Run with `PYTHONPATH=src`.<br>Ids that only restate packaging/hardware constraints (zero dependencies, src layout, Python 3.10+,<br>\| FP-03 vs Contract s4 (CF-10) \| omitted repeatable option: absent value vs `()` \| `()` \| | yes · AB · A | |
| r17-sonnet-export-2 | \| 010 \| omitted repeatable option: absent vs `()` \| `()` \| | yes · AB · A | |
| r17-sonnet-export-3 | \| 10 \| omitted repeatable option: absent value vs empty tuple \| empty tuple `()` \| | yes · AB · A | |

## C09 — A: PRD 141: env name list "(first one set wins)" (also PRD 169) · B: Contract 137: "the last name that is set wins"

Conflict ids in the export: CF-000088

| Run | Lines from NOTES.md | Reading | Owner |
|---|---|---|---|
| r17-haiku-markdown-1 | *(none)* | no · - · A | |
| r17-haiku-markdown-3 | \| 1 \| Interface Contract §4 (`envvar`) vs. PRD FP-03 \| Contract: a list of env names, "the last name that is set wins". PRD: "first one set wins". \| PRD (first set wins). The PRD is the behavioural authority; the contract only fixes shape. \| | yes · AB · A | |
| r17-sonnet-markdown-1 | \| `envvar` list: PRD "first set wins", Contract "last set wins" \| Last set wins (options and arguments share the code). \| | yes · AB · B | |
| r17-sonnet-markdown-2 | \| Env var list on an option \| PRD: first set wins; Contract: last set wins \| Options: last non-empty wins (Contract). Arguments: first wins (PRD). \| | yes · AB · B | |
| r17-sonnet-markdown-3 | \| 1 \| Env var list on an option: contract says "last name set wins"; PRD says "first one set wins". \| First set wins (options and arguments). \| | yes · AB · A | |
| r17-haiku-export-1 | \| CF-000088 \| Environment name list: first set wins (FP-03) vs last set wins (Interface) \| First set wins. \| | yes · AB · A | |
| r17-haiku-export-2 | \| CF-000088 \| Environment name list: first set wins vs last set wins \| First set wins (PRD FP-03); the automatic prefix name is tried last \| | yes · AB · A | |
| r17-haiku-export-3 | \| CF-000088 \| Environment name list: first set wins (FP-03) vs last set wins (Contract) \| first set wins \| | yes · AB · A | |
| r17-sonnet-export-1 | \| FP-03 vs Contract s4 (CF-88) \| envvar list: first set vs last set wins \| first set wins \| | yes · AB · A | |
| r17-sonnet-export-2 | \| 088 \| envvar list \| first name that is set wins \| | no · - · A | |
| r17-sonnet-export-3 | \| 88 \| env var list: first set vs last set \| first set wins \| | yes · AB · A | |

## C10 — A: PRD 142: other flag env value "is a conversion usage error" · B: PRD 192: "any other value turns the flag off"

Conflict ids in the export: CF-000157

| Run | Lines from NOTES.md | Reading | Owner |
|---|---|---|---|
| r17-haiku-markdown-1 | *(none)* | no · - · A | |
| r17-haiku-markdown-3 | *(none)* | no · - · A | |
| r17-sonnet-markdown-1 | \| Boolean flag env var with junk text: FP-03 usage error, FP-05 "turns flag off" \| Usage error. \| | yes · AB · A | |
| r17-sonnet-markdown-2 | *(none)* | yes · AB · A | |
| r17-sonnet-markdown-3 | \| 16 \| Bool flag env value: FP-03 says an unknown non-empty string is a usage error; FP-05 says it turns the flag off. \| Usage error (whitespace-only deactivates). \| | yes · AB · A | |
| r17-haiku-export-1 | \| CF-000157, CF-000151 \| Boolean flag from environment with an unrecognised non-empty value: usage error (FP-03, FP-05) vs turns the flag off (FP-05) \| Usage error for boolean flags. For a flag with a non-boolean flag value, an unrecognised value counts as unset. \| | yes · AB · A | |
| r17-haiku-export-2 | - **Pack 10 (N-000950–980):** `Context` settings and members, `pass_context`, `pass_obj`, `make_pass_decorator`, `get_current_context(silent=…)`, per-thread stack.<br>\| CF-000151, CF-000157 \| Boolean flag from an environment variable with an unrecognized value: usage error vs "turns the flag off" \| Usage error for an unrecognized non-empty value. A flag with a non-boolean flag value treats an unrecognized value as unset \| | yes · AB · A | |
| r17-haiku-export-3 | \| CF-000151, CF-000157 \| Boolean flag env value that is not recognised: usage error (FP-03) vs turns the flag off (FP-05) \| plain boolean flag: usage error; a flag with a non-boolean flag value: unrecognised text is treated as unset (FP-03) \| | yes · AB · A | |
| r17-sonnet-export-1 | \| FP-05 (CF-151, 157) \| env bool flag: other value is an error vs turns flag off \| other non-empty value is a usage error (whitespace-only deactivates) \| | yes · AB · A | |
| r17-sonnet-export-2 | \| 151/157 \| boolean env/text junk value \| usage error (blank env value deactivates a flag) \| | no · - · A | |
| r17-sonnet-export-3 | \| 151, 157 \| bool env value other than known tokens: error vs off \| usage error (whitespace-only value is off) \| | yes · AB · A | |

## C12 — A: PRD 195: date-time formats, "the first success wins" · B: Contract 211: "the last matching format is used"

Conflict ids in the export: CF-000158

| Run | Lines from NOTES.md | Reading | Owner |
|---|---|---|---|
| r17-haiku-markdown-1 | 8. **`DateTime` with several matching formats.** PRD: the first success wins. Interface: the last<br>matching format. Built: first match wins. | yes · AB · A | |
| r17-haiku-markdown-3 | - Default option metavars: `TEXT` for strings, `INTEGER` for ints, `FLOAT`, `BOOLEAN`, `UUID`, `DATETIME`; choices show `[a\|b]`. | no · - · B | |
| r17-sonnet-markdown-1 | \| `DateTime`: PRD "first success wins", Contract "last matching format" \| Last matching format. Custom formats replace the default list. \| | yes · AB · B | |
| r17-sonnet-markdown-2 | \| DateTime with several matching formats \| PRD: first wins; Contract: last wins \| Last matching format; custom list replaces the defaults. \| | yes · AB · B | |
| r17-sonnet-markdown-3 | \| 2 \| `DateTime` with several matching formats: contract "last matching"; PRD "first success wins". \| First success wins. \| | yes · AB · A | |
| r17-haiku-export-1 | \| CF-000158 \| Date-time formats: first success wins (FP-05) vs last matching format (Interface) \| First success wins. \| | yes · AB · A | |
| r17-haiku-export-2 | \| `paramtypes.py` \| `ParamType`, built-in types, `Choice`, `DateTime`, `IntRange`, `FloatRange`, `Tuple`, `File`, `Path` \| 09, 23, 27 \|<br>\| CF-000158 \| Date-time format match: first success vs last matching format \| First success wins (PRD FP-05) \| | yes · AB · A | |
| r17-haiku-export-3 | \| CF-000158 \| Date-time formats: first match wins (FP-05) vs last match (Contract) \| first match wins \| | yes · AB · A | |
| r17-sonnet-export-1 | \| FP-01 vs FP-05 (CF-136, 158) \| DateTime custom formats added vs replace; first vs last match \| custom list replaces the default list; first matching format wins \| | yes · AB · A | |
| r17-sonnet-export-2 | \| 136 \| DateTime custom formats \| replace the defaults \|<br>\| 158 \| DateTime several matches \| first matching format wins \| | no · - · A | |
| r17-sonnet-export-3 | \| 136 \| DateTime formats extend vs replace \| a supplied list replaces the defaults \|<br>\| 158 \| DateTime: first vs last matching format \| first matching format \| | yes · AB · A | |

## C13 — A: PRD 195: author list "replaces the default list (it does not extend it)" · B: PRD 40: author list "is added to the default formats"

Conflict ids in the export: CF-000136

| Run | Lines from NOTES.md | Reading | Owner |
|---|---|---|---|
| r17-haiku-markdown-1 | 8. **`DateTime` with several matching formats.** PRD: the first success wins. Interface: the last | no · - · A | |
| r17-haiku-markdown-3 | - Default option metavars: `TEXT` for strings, `INTEGER` for ints, `FLOAT`, `BOOLEAN`, `UUID`, `DATETIME`; choices show `[a\|b]`. | no · - · A | |
| r17-sonnet-markdown-1 | \| `DateTime`: PRD "first success wins", Contract "last matching format" \| Last matching format. Custom formats replace the default list. \| | no · A · A | |
| r17-sonnet-markdown-2 | \| DateTime with several matching formats \| PRD: first wins; Contract: last wins \| Last matching format; custom list replaces the defaults. \| | no · A · A | |
| r17-sonnet-markdown-3 | \| 2 \| `DateTime` with several matching formats: contract "last matching"; PRD "first success wins". \| First success wins. \| | yes · AB · A | |
| r17-haiku-export-1 | \| CF-000136 \| Custom date-time format list: added to defaults (FP-03 public surface) vs replaces defaults (FP-05, Interface) \| Replaces the defaults. \| | yes · AB · A | |
| r17-haiku-export-2 | \| `paramtypes.py` \| `ParamType`, built-in types, `Choice`, `DateTime`, `IntRange`, `FloatRange`, `Tuple`, `File`, `Path` \| 09, 23, 27 \|<br>\| CF-000136 \| Date-time formats: added to the defaults vs replace them \| Replace the defaults (PRD FP-05) \| | yes · AB · A | |
| r17-haiku-export-3 | \| CF-000136 \| Date-time format list: replaces the defaults (FP-05) vs added to them (FP-16) \| replaces the defaults \| | yes · AB · A | |
| r17-sonnet-export-1 | \| FP-01 vs FP-05 (CF-136, 158) \| DateTime custom formats added vs replace; first vs last match \| custom list replaces the default list; first matching format wins \| | yes · AB · A | |
| r17-sonnet-export-2 | \| 136 \| DateTime custom formats \| replace the defaults \|<br>\| 158 \| DateTime several matches \| first matching format wins \| | no · - · A | |
| r17-sonnet-export-3 | \| 136 \| DateTime formats extend vs replace \| a supplied list replaces the defaults \|<br>\| 158 \| DateTime: first vs last matching format \| first matching format \| | yes · AB · A | |

## C14 — A: PRD 196: open-bound clamp, "the adjacent integer inside the range" · B: Contract 212: the value "becomes that bound’s value"

Conflict ids in the export: CF-000092

| Run | Lines from NOTES.md | Reading | Owner |
|---|---|---|---|
| r17-haiku-markdown-1 | 6. **`IntRange` clamp on an open bound.** PRD: the adjacent integer inside the range.<br>Interface: the bound's value. Built: the PRD behaviour (e.g. `min_open` clamps `0` to `1`).<br>7. **`FloatRange` clamp with an open bound.** PRD: a declaration error. Interface: clamp to the | yes · AB · A | |
| r17-haiku-markdown-3 | *(none)* | no · - · A | |
| r17-sonnet-markdown-1 | Declaration errors (invalid keyword combinations, bad style colors, clamped open `FloatRange`) | no · - · A | |
| r17-sonnet-markdown-2 | *(none)* | no · - · A | |
| r17-sonnet-markdown-3 | \| 6 \| `FloatRange` clamp with an open bound: contract clamps to the bound; PRD says declaration error. \| `TypeError` at construction. \|<br>\| 7 \| `IntRange` clamp with open bound: contract "that bound's value"; PRD "adjacent integer inside". \| Adjacent integer inside the range. \| | yes · AB · A | |
| r17-haiku-export-1 | \| CF-000016, CF-000092 \| `IntRange` clamp beyond an open bound: "adjacent integer inside the range" vs "the bound itself" \| Adjacent integer inside the range (`min+1` / `max-1`). \|<br>\| CF-000100, CF-000107 \| `FloatRange` with an open bound and `clamp=True`: refused (FP-05) vs allowed (Interface) \| Refused at construction with `DeclarationError`. \| | yes · AB · A | |
| r17-haiku-export-2 | \| CF-000016, CF-000092 \| Clamp past an open integer bound: adjacent integer vs bound \| Adjacent integer inside the range (`IntRange`) \|<br>\| CF-000100, CF-000107 \| `FloatRange` clamp with an open bound: allowed vs refused \| Refused at construction (`ValueError`) \| | yes · AB · A | |
| r17-haiku-export-3 | \| CF-000016, CF-000092 \| `IntRange` clamp beyond an open bound: "nearest included value" vs "the bound itself" \| adjacent integer inside the range (FP-05) \|<br>\| CF-000100, CF-000107 \| `FloatRange` clamp with an open bound: refused (FP-05) vs allowed (Contract) \| refused with `TypeError` at construction \| | yes · AB · A | |
| r17-sonnet-export-1 | \| FP-05 vs Contract s5 (CF-16, 92, 100, 107) \| clamp at open bound; FloatRange clamp \| IntRange open bound -> adjacent integer inside range; FloatRange with clamp and an open bound raises `TypeError` at construction \| | no · - · A | |
| r17-sonnet-export-2 | \| 016/092/100/107 \| clamp with open bounds \| IntRange: adjacent integer inside range; FloatRange: clamp with an open bound raises `DeclarationError` at construction \| | no · - · A | |
| r17-sonnet-export-3 | \| 16, 92 \| IntRange clamp at an open bound: "adjacent integer" (PRD) vs "the bound" (contract) \| adjacent integer inside the range (PRD) \|<br>\| 100, 107 \| FloatRange clamp with open bound: refused (PRD) vs clamps to the bound (contract) \| `TypeError` at construction (PRD) \| | yes · AB · A | |

## C15 — A: PRD 197: float clamp "only allowed when both bounds are closed" (also PRD 208) · B: Contract 213: with an open bound the value "becomes the bound"

Conflict ids in the export: CF-000107

| Run | Lines from NOTES.md | Reading | Owner |
|---|---|---|---|
| r17-haiku-markdown-1 | 6. **`IntRange` clamp on an open bound.** PRD: the adjacent integer inside the range.<br>Interface: the bound's value. Built: the PRD behaviour (e.g. `min_open` clamps `0` to `1`).<br>7. **`FloatRange` clamp with an open bound.** PRD: a declaration error. Interface: clamp to the | yes · AB · A | |
| r17-haiku-markdown-3 | *(none)* | no · - · A | |
| r17-sonnet-markdown-1 | Declaration errors (invalid keyword combinations, bad style colors, clamped open `FloatRange`) | no · A · A | |
| r17-sonnet-markdown-2 | *(none)* | no · - · A | |
| r17-sonnet-markdown-3 | \| 6 \| `FloatRange` clamp with an open bound: contract clamps to the bound; PRD says declaration error. \| `TypeError` at construction. \|<br>\| 7 \| `IntRange` clamp with open bound: contract "that bound's value"; PRD "adjacent integer inside". \| Adjacent integer inside the range. \| | yes · AB · A | |
| r17-haiku-export-1 | \| CF-000016, CF-000092 \| `IntRange` clamp beyond an open bound: "adjacent integer inside the range" vs "the bound itself" \| Adjacent integer inside the range (`min+1` / `max-1`). \|<br>\| CF-000100, CF-000107 \| `FloatRange` with an open bound and `clamp=True`: refused (FP-05) vs allowed (Interface) \| Refused at construction with `DeclarationError`. \| | yes · AB · A | |
| r17-haiku-export-2 | \| `paramtypes.py` \| `ParamType`, built-in types, `Choice`, `DateTime`, `IntRange`, `FloatRange`, `Tuple`, `File`, `Path` \| 09, 23, 27 \|<br>\| CF-000016, CF-000092 \| Clamp past an open integer bound: adjacent integer vs bound \| Adjacent integer inside the range (`IntRange`) \|<br>\| CF-000100, CF-000107 \| `FloatRange` clamp with an open bound: allowed vs refused \| Refused at construction (`ValueError`) \| | yes · AB · A | |
| r17-haiku-export-3 | \| CF-000016, CF-000092 \| `IntRange` clamp beyond an open bound: "nearest included value" vs "the bound itself" \| adjacent integer inside the range (FP-05) \|<br>\| CF-000100, CF-000107 \| `FloatRange` clamp with an open bound: refused (FP-05) vs allowed (Contract) \| refused with `TypeError` at construction \|<br>\| 21 \| FP-03 Options \| N-000178–N-000284 (107) \| core.py Option, _OptionParser, Command._process \| implemented \| | yes · AB · A | |
| r17-sonnet-export-1 | \| FP-05 vs Contract s5 (CF-16, 92, 100, 107) \| clamp at open bound; FloatRange clamp \| IntRange open bound -> adjacent integer inside range; FloatRange with clamp and an open bound raises `TypeError` at construction \| | no · - · A | |
| r17-sonnet-export-2 | \| 016/092/100/107 \| clamp with open bounds \| IntRange: adjacent integer inside range; FloatRange: clamp with an open bound raises `DeclarationError` at construction \| | no · - · A | |
| r17-sonnet-export-3 | \| 16, 92 \| IntRange clamp at an open bound: "adjacent integer" (PRD) vs "the bound" (contract) \| adjacent integer inside the range (PRD) \|<br>\| 100, 107 \| FloatRange clamp with open bound: refused (PRD) vs clamps to the bound (contract) \| `TypeError` at construction (PRD) \| | yes · AB · A | |

## C17 — A: PRD 272: confirmation "rejects a mismatch by asking the pair again" · B: PRD 381: two different values in a confirmation prompt are an abort

Conflict ids in the export: CF-000134

| Run | Lines from NOTES.md | Reading | Owner |
|---|---|---|---|
| r17-haiku-markdown-1 | *(none)* | no · - · A | |
| r17-haiku-markdown-3 | *(none)* | no · - · A | |
| r17-sonnet-markdown-1 | *(none)* | no · - · A | |
| r17-sonnet-markdown-2 | *(none)* | no · - · A | |
| r17-sonnet-markdown-3 | *(none)* | no · - · A | |
| r17-haiku-export-1 | \| CF-000134 \| Confirmation mismatch: ask the pair again (FP-08) vs two different values abort (FP-13) \| Ask the pair again. End of input during the pair aborts. \| | yes · AB · A | |
| r17-haiku-export-2 | - **Pack 08 (N-000881–935):** `option` and `argument` keywords, on/off pairs, delivered-value table (scalar, tuple, `()`, `None`, flag, count), `BadParameter`, ready-made `help_option`, `version_option`, `custom_version_option`, `password_option`, `confirmation_option`.<br>\| CF-000134, CF-000159 \| Confirmation mismatch and conversion failure at a prompt: re-ask vs abort/not asked again \| Re-ask (PRD FP-08). Command-line conversion failures remain usage errors \| | yes · AB · A | |
| r17-haiku-export-3 | - `decorators.py` — `command`, `group`, `option`, `argument`, `help_option`, `version_option`, `custom_version_option`, `password_option`, `confirmation_option`, `pass_context`, `pass_obj`, `make_pass_decorator`.<br>\| CF-000134 \| Confirmation mismatch: re-ask the pair (FP-08) vs abort (FP-13) \| re-asks the pair (FP-08); the FP-13 abort case is not applied \|<br>- `prompt_required` defaults to `True`: an omitted prompting option asks. `password_option` therefore asks when omitted; `confirmation_option` asks when the flag is omitted (declined → `Abort`).<br>\| 26 \| FP-08 Prompts, confirmation, hidden input \| N-000484–N-000527 (44) \| termui.py prompt/confirm; core.py Option.resolve; decorators.py password/confirmation options \| implemented \| | yes · AB · A | |
| r17-sonnet-export-1 | \| FP-08 vs FP-13 (CF-134, 159) \| confirmation mismatch / bad prompt value: ask again vs abort/usage error \| ask again (a mismatch, an invalid typed value); EOF aborts \| | yes · AB · A | |
| r17-sonnet-export-2 | \| 134 \| confirmation mismatch \| ask the pair again (EOF aborts) \| | no · - · A | |
| r17-sonnet-export-3 | \| 134, 159 \| prompt confirmation / re-ask \| invalid prompt values re-ask; EOF and declined confirmation abort (exit 1) \| | no · - · A | |

## C18 — A: PRD 274: "Prompts re-ask on conversion failure" · B: PRD 380: a prompt value failing conversion is a usage error, "not asked again"

Conflict ids in the export: CF-000159

| Run | Lines from NOTES.md | Reading | Owner |
|---|---|---|---|
| r17-haiku-markdown-1 | *(none)* | no · - · A | |
| r17-haiku-markdown-3 | *(none)* | no · - · A | |
| r17-sonnet-markdown-1 | *(none)* | no · - · A | |
| r17-sonnet-markdown-2 | \| Prompt conversion failure \| FP-13: not asked again; FP-08: re-ask \| Re-asks until valid or EOF (EOF aborts). \| | yes · AB · A | |
| r17-sonnet-markdown-3 | *(none)* | no · - · A | |
| r17-haiku-export-1 | \| CF-000159 \| Conversion failure at a prompt: prompt re-asks (FP-08) vs not asked again (FP-13) \| Prompt re-asks. Conversion failures from other sources are usage errors (exit 2). \| | yes · AB · A | |
| r17-haiku-export-2 | \| CF-000134, CF-000159 \| Confirmation mismatch and conversion failure at a prompt: re-ask vs abort/not asked again \| Re-ask (PRD FP-08). Command-line conversion failures remain usage errors \| | yes · AB · A | |
| r17-haiku-export-3 | \| CF-000134 \| Confirmation mismatch: re-ask the pair (FP-08) vs abort (FP-13) \| re-asks the pair (FP-08); the FP-13 abort case is not applied \|<br>\| CF-000159 \| Prompt conversion failure: re-ask (FP-08) vs not asked again (FP-13) \| re-asks (FP-08) \| | yes · AB · A | |
| r17-sonnet-export-1 | \| FP-08 vs FP-13 (CF-134, 159) \| confirmation mismatch / bad prompt value: ask again vs abort/usage error \| ask again (a mismatch, an invalid typed value); EOF aborts \| | yes · AB · A | |
| r17-sonnet-export-2 | \| 159 \| prompt conversion failure \| re-ask until valid or EOF \| | no · - · A | |
| r17-sonnet-export-3 | \| 134, 159 \| prompt confirmation / re-ask \| invalid prompt values re-ask; EOF and declined confirmation abort (exit 1) \| | no · - · A | |

## C20 — A: PRD 292: resolved path, "a leading tilde is not expanded" · B: Contract 216: "a leading `~` is first expanded"

Conflict ids in the export: CF-000160

| Run | Lines from NOTES.md | Reading | Owner |
|---|---|---|---|
| r17-haiku-markdown-1 | `~/.config`. Built: `$XDG_CONFIG_HOME` when set, otherwise `~/.config`.<br>9. **`Path(resolve_path=True)` and `~`.** PRD: a leading tilde is not expanded. Interface: it is | yes · AB · A | |
| r17-haiku-markdown-3 | \| 2 \| Contract §5 (`Path`, `resolve_path`) vs. PRD FP-09 \| Contract: a leading `~` is expanded when `resolve_path=True`. PRD: "a leading tilde is not expanded". \| Contract (`~` is expanded before resolving). \|<br>- Windows-only argument expansion (glob / `~` / environment tokens in the argument list) is not implemented. | yes · AB · B | |
| r17-sonnet-markdown-1 | \| `Path(resolve_path=True)`: PRD "no tilde expansion", Contract "expand `~` first" \| Expand, then `realpath`. \|<br>\| `get_app_dir` on Unix: PRD honours `XDG_CONFIG_HOME`, Contract "always under `~/.config`" \| Always `~/.config`. \| | yes · AB · B | |
| r17-sonnet-markdown-2 | \| `Path(resolve_path=True)` and `~` \| PRD: not expanded; Contract: expanded \| Expanded, then `realpath`. \|<br>\| `get_app_dir` on Unix \| Contract: always `~/.config`; PRD: honours `XDG_CONFIG_HOME` \| Honours `XDG_CONFIG_HOME`, else `~/.config`. \| | yes · AB · B | |
| r17-sonnet-markdown-3 | \| 3 \| `Path(resolve_path=True)`: contract expands leading `~`; PRD says tilde is not expanded. \| No tilde expansion (symlinks resolved). \|<br>\| 14 \| `get_app_dir` on Unix: contract "always under ~/.config"; PRD honours `XDG_CONFIG_HOME`. \| `XDG_CONFIG_HOME` when set. \| | yes · AB · A | |
| r17-haiku-export-1 | \| CF-000129 \| Application directory: honour `XDG_CONFIG_HOME` (FP-11) vs always `~/.config` (Interface) \| Honour `XDG_CONFIG_HOME` when set. \|<br>\| CF-000160 \| `Path(resolve_path=True)` and a leading `~`: expanded (Interface) vs not expanded (FP-09) \| Not expanded (realpath only). \| | yes · AB · A | |
| r17-haiku-export-2 | \| CF-000129 \| Application directory on Unix: `$XDG_CONFIG_HOME` vs always `~/.config` \| `$XDG_CONFIG_HOME` when set, else `~/.config` (PRD) \|<br>\| CF-000160 \| `Path(resolve_path=True)` and a leading `~`: expanded vs not \| Not expanded (PRD FP-09) \| | yes · AB · A | |
| r17-haiku-export-3 | \| CF-000129 \| Application config dir on Unix: honour `XDG_CONFIG_HOME` (FP-11) vs always `~/.config` (Contract) \| honours `XDG_CONFIG_HOME` \|<br>\| CF-000160 \| `Path(resolve_path=True)` and `~`: not expanded (FP-09) vs expanded (Contract) \| not expanded \|<br>- Windows and macOS branches: `get_app_dir` (APPDATA, Library/Application Support), `launch` (`os.startfile`, `open -R`), argv glob/`~`/`%VAR%` expansion, and the `windows` profile in the hardware spec. | yes · AB · A | |
| r17-sonnet-export-1 | \| FP-11 vs Contract s7 (CF-129) \| app dir under XDG_CONFIG_HOME vs always `~/.config` \| `$XDG_CONFIG_HOME` when set, else `~/.config` \|<br>\| FP-09 vs Contract s5 (CF-160) \| `Path(resolve_path=True)` expands `~` \| no tilde expansion; symlinks resolved \| | no · B · A | |
| r17-sonnet-export-2 | \| 129 \| app dir \| `$XDG_CONFIG_HOME` honoured, else `~/.config` \|<br>\| 160 \| `~` in Path \| not expanded \| | no · - · A | |
| r17-sonnet-export-3 | \| 129 \| app dir: `XDG_CONFIG_HOME` vs always `~/.config` \| `XDG_CONFIG_HOME` honoured when set \|<br>\| 160 \| Path `resolve_path` and `~` \| leading `~` is expanded, then realpath (contract) \| | no · - · B | |

## C21 — A: PRD 339: Unix config home is `$XDG_CONFIG_HOME` when set · B: Contract 292: "always under `~/.config`"

Conflict ids in the export: CF-000129

| Run | Lines from NOTES.md | Reading | Owner |
|---|---|---|---|
| r17-haiku-markdown-1 | \| `utils.py` \| file helpers (`open_file`, lazy and atomic files, `-` streams), `get_app_dir`, `format_filename` \|<br>5. **App config directory on Unix.** FP-11 honours `$XDG_CONFIG_HOME`; Interface §7 says always<br>`~/.config`. Built: `$XDG_CONFIG_HOME` when set, otherwise `~/.config`. | yes · AB · A | |
| r17-haiku-markdown-3 | *(none)* | no · - · A | |
| r17-sonnet-markdown-1 | \| `get_app_dir` on Unix: PRD honours `XDG_CONFIG_HOME`, Contract "always under `~/.config`" \| Always `~/.config`. \| | yes · AB · B | |
| r17-sonnet-markdown-2 | \| `get_app_dir` on Unix \| Contract: always `~/.config`; PRD: honours `XDG_CONFIG_HOME` \| Honours `XDG_CONFIG_HOME`, else `~/.config`. \| | yes · AB · A | |
| r17-sonnet-markdown-3 | \| 14 \| `get_app_dir` on Unix: contract "always under ~/.config"; PRD honours `XDG_CONFIG_HOME`. \| `XDG_CONFIG_HOME` when set. \| | yes · AB · A | |
| r17-haiku-export-1 | \| CF-000129 \| Application directory: honour `XDG_CONFIG_HOME` (FP-11) vs always `~/.config` (Interface) \| Honour `XDG_CONFIG_HOME` when set. \| | yes · AB · A | |
| r17-haiku-export-2 | \| `utils.py` \| file opening (lazy/atomic/dash), `get_app_dir`, `format_filename`, stream accessors \| 11, 27, 29 \|<br>- **Pack 11 (N-000981–1012):** all terminal helpers; `echo` to stdout/stderr/file; styling; pager via `PAGER`; progress bar; `getchar`; `pause`; `edit`; `launch`; `clear`; `get_app_dir`; `format_filename`; `open_file`.<br>\| CF-000129 \| Application directory on Unix: `$XDG_CONFIG_HOME` vs always `~/.config` \| `$XDG_CONFIG_HOME` when set, else `~/.config` (PRD) \|<br>- **`launch`, `edit`, `get_app_dir`**: the macOS and Windows branches are written but untested; `launch` uses `xdg-open` on Linux. | yes · AB · A | |
| r17-haiku-export-3 | - `termui.py` — echo/style/prompts/pager/progress/editor/launch/app-dir helpers.<br>\| CF-000129 \| Application config dir on Unix: honour `XDG_CONFIG_HOME` (FP-11) vs always `~/.config` (Contract) \| honours `XDG_CONFIG_HOME` \|<br>\| 03 \| Hardware requirements · Execution profiles \| N-000780–N-000789 (10) \| pyproject.toml (src layout, setuptools PEP 517) \| implemented; Linux only exercised; macOS/Windows branches (get_app_dir, launch, argv expansion) not run \|<br>\| 29 \| FP-11 Terminal output and helpers \| N-000618–N-000688 (71) \| termui.py (echo, style, pager, progressbar, getchar, pause, edit, launch, clear, get_app_dir) \| implemented; partly exercised: interactive TTY paths (getchar via /dev/tty, pager, progress drawing, pause wait) are not run here \|<br>- Windows and macOS branches: `get_app_dir` (APPDATA, Library/Application Support), `launch` (`os.startfile`, `open -R`), argv glob/`~`/`%VAR%` expansion, and the `windows` profile in the hardware spec. | yes · AB · A | |
| r17-sonnet-export-1 | progressbar, getchar, pause, edit, launch, clear), `utils` (echo, style, files, get_app_dir),<br>\| FP-11 vs Contract s7 (CF-129) \| app dir under XDG_CONFIG_HOME vs always `~/.config` \| `$XDG_CONFIG_HOME` when set, else `~/.config` \| | yes · AB · A | |
| r17-sonnet-export-2 | \| 129 \| app dir \| `$XDG_CONFIG_HOME` honoured, else `~/.config` \| | no · - · A | |
| r17-sonnet-export-3 | \| 129 \| app dir: `XDG_CONFIG_HOME` vs always `~/.config` \| `XDG_CONFIG_HOME` honoured when set \| | yes · AB · A | |

## C22 — A: PRD 335: pause, not interactive, "does nothing" · B: PRD 346: "it still prints its message there"

Conflict ids in the export: CF-000128

| Run | Lines from NOTES.md | Reading | Owner |
|---|---|---|---|
| r17-haiku-markdown-1 | 15. **`pause` when not interactive.** PRD: does nothing. FP-11: prints its message and does not | yes · AB · B | |
| r17-haiku-markdown-3 | - `edit`, `launch`, `getchar` and `pause` are implemented with simple, platform-basic behaviour and are only smoke-tested (no TTY in this environment). | no · - · A | |
| r17-sonnet-markdown-1 | \| `pause` when not interactive: "does nothing" vs "still prints its message" \| Prints the message, never blocks. \| | yes · AB · B | |
| r17-sonnet-markdown-2 | *(none)* | no · - · B | |
| r17-sonnet-markdown-3 | \| 18 \| `pause()` when not interactive: FP-11 normal says does nothing; boundary says it still prints the message. \| Prints the message, does not wait. \| | yes · AB · B | |
| r17-haiku-export-1 | \| CF-000128 \| `pause` when not interactive: does nothing (FP-11) vs prints its message (FP-11 boundary) \| Prints the message and does not block. \| | yes · AB · B | |
| r17-haiku-export-2 | \| `termui.py` \| echo/styling/prompt/confirm/getchar/pause/edit/launch/clear/pager/progress \| 11, 29 \|<br>- **Pack 11 (N-000981–1012):** all terminal helpers; `echo` to stdout/stderr/file; styling; pager via `PAGER`; progress bar; `getchar`; `pause`; `edit`; `launch`; `clear`; `get_app_dir`; `format_filename`; `open_file`.<br>\| CF-000128 \| Non-interactive `pause`: does nothing vs prints its message \| Prints the message; does not block \| | yes · AB · B | |
| r17-haiku-export-3 | - `tests/` — `test_optlyn.py`, `test_optlyn_more.py` (128 tests; run `PYTHONPATH=src python3 -m pytest tests`).<br>\| CF-000128 \| Pause when not interactive: "does nothing" vs "still prints its message" \| prints the message, does not wait \|<br>\| 29 \| FP-11 Terminal output and helpers \| N-000618–N-000688 (71) \| termui.py (echo, style, pager, progressbar, getchar, pause, edit, launch, clear, get_app_dir) \| implemented; partly exercised: interactive TTY paths (getchar via /dev/tty, pager, progress drawing, pause wait) are not run here \|<br>- Interactive terminal paths: `getchar` via `/dev/tty`, pager through `PAGER`, progress-bar drawing, and the wait in `pause`; prompts that use `getpass` on a real TTY. | yes · AB · B | |
| r17-sonnet-export-1 | progressbar, getchar, pause, edit, launch, clear), `utils` (echo, style, files, get_app_dir),<br>\| FP-11 (CF-128) \| `pause` non-interactive: nothing vs prints message \| does nothing and does not block \| | yes · AB · A | |
| r17-sonnet-export-2 | \| 128 \| pause when not interactive \| does not block, prints its message \| | no · - · B | |
| r17-sonnet-export-3 | \| 128 \| pause when not interactive \| prints its message, does not block \| | no · - · B | |

## C23 — A: PRD 358: "Options are listed only once at least a dash has been typed" · B: Contract 306: an empty token lists "the subcommand names followed by the option names"

Conflict ids in the export: CF-000161

| Run | Lines from NOTES.md | Reading | Owner |
|---|---|---|---|
| r17-haiku-markdown-1 | \| `shell_completion.py` \| registration scripts (`<shell>_source`) and suggestion output (`<shell>_complete`) \|<br>13. **Completion of an empty token.** Interface §8 lists option names after subcommand names<br>for an empty token; PRD FP-12 lists options only after a dash has been typed. Built: PRD.<br>- The shell completion scripts are minimal and were not run in real bash, zsh, fish or PowerShell. | yes · AB · A | |
| r17-haiku-markdown-3 | \| 6 \| Contract §8 (completion, empty token) vs. PRD FP-12 \| Contract: for an empty token, subcommand names are followed by option names. PRD: options are listed only once at least a dash has been typed. \| PRD. An empty token lists subcommands only. \|<br>- Completion: an unrecognised `_<PROG>_COMPLETE` instruction exits with status 1 and prints nothing.<br>- The completion variable uses the program name with `-` replaced by `_`, upper-cased (`_MYTOOL_COMPLETE`). | yes · AB · A | |
| r17-sonnet-markdown-1 | \| Completion of an empty token: PRD "options only after a dash", Contract "subcommands then options" \| Subcommands then options. \| | yes · AB · B | |
| r17-sonnet-markdown-2 | \| Completion of empty token \| PRD: options only after a dash; Contract: subcommands then options \| Empty token: subcommands, then options. Non-empty alphanumeric token: subcommands only. \| | yes · AB · B | |
| r17-sonnet-markdown-3 | \| 13 \| Show options for an empty incomplete token: contract says subcommands then options; PRD says options only after a dash. \| Options only once a dash is typed. \| | yes · AB · A | |
| r17-haiku-export-1 | \| CF-000161 \| Completion of an empty token: subcommand names then option names (Interface) vs options only after a dash (FP-12) \| Subcommand names only for an empty token. Options are listed only once a dash has been typed. \|<br>- Completion protocol: suggestions are one per line. Zsh and fish add `<TAB>help`. Path requests are<br>`@@file:<token>` or `@@dir:<token>`. Unknown `_<PROG>_COMPLETE` instructions print an error to<br>- Shell completion scripts for zsh, fish and PowerShell were only checked for generation, not run in | yes · AB · A | |
| r17-haiku-export-2 | \| `utils.py` \| file opening (lazy/atomic/dash), `get_app_dir`, `format_filename`, stream accessors \| 11, 27, 29 \|<br>\| `shell_completion.py` \| `_<PROG>_COMPLETE` handling, `{shell}_source` / `{shell}_complete` for bash/zsh/fish/powershell \| 12, 30 \|<br>- **Pack 06 (N-000803–849):** exit statuses (0 / 1 / 2 / author status); standalone mode raises `SystemExit`, non-standalone raises or returns; stream channels (stdout for intentional help, stderr for usage/abort/errors/deprecation, completion on stdout); help-page order (usage, description, Positio<br>- **Pack 12 (N-001013–1037):** completion variable name, instructions, COMP_WORDS/COMP_CWORD handling, suggestion output, `shell_complete` on options and types, `CompletionItem` (`value`, `help`, `type`).<br>- **FP-01 … FP-14 (packs 19–32) and cross-cutting refinements (pack 33):** implemented in `core.py` (parsing, groups, chaining, help, eager flags, prompts, value sources, exit classes), `paramtypes.py`, `utils.py`, `termui.py`, `shell_completion.py`, `testing.py`.<br>\| CF-000161 \| Completion of an empty token: subcommands then options vs subcommands only \| Subcommands only; options appear once a dash is typed (PRD FP-12) \|<br>- Completion output: `@path:file:<token>` / `@path:dir:<token>` for path requests, `value\thelp` for zsh and fish; unknown instruction → message on stderr, exit 2, callback not run.<br>- **Shell completion scripts** for zsh, fish and PowerShell were not run in their shells. Bash's script is the most straightforward and was checked only by its text.<br>- **`ParamType` shell completion for `Path`/`File`** only asks the shell for a path (file or directory); it does not list entries. | yes · AB · A | |
| r17-haiku-export-3 | - `shell_completion.py` — completion mode (`_<PROG>_COMPLETE`).<br>\| CF-000161 \| Completion of an empty token: subcommands only, options once a dash is typed (FP-12) vs subcommands then options (Contract) \| FP-12 behaviour \|<br>\| 12 \| Contract §8 Shell completion \| N-001013–N-001037 (25) \| shell_completion.py \| implemented \|<br>\| 30 \| FP-12 Shell completion \| N-000689–N-000715 (27) \| shell_completion.py \| implemented; partly exercised: bash path tested; zsh/fish/PowerShell scripts are written but not run in a shell \|<br>- Shell scripts for zsh, fish and PowerShell are written from the contract but were not run in those shells; bash completion was exercised through the environment interface (`COMP_WORDS`, `COMP_CWORD`). | yes · AB · A | |
| r17-sonnet-export-1 | `shell_completion`, `testing` (CliRunner), `exceptions`, `globals`.<br>implementer (exception class names, source enum values, completion framing, help extras) use the<br>\| FP-12 (CF-161) \| options suggested for empty token \| options only when the incomplete token starts with a prefix char; empty token gives subcommands only \| | no · - · A | |
| r17-sonnet-export-2 | \| 161 \| completion options \| options listed for empty token and for `-` prefixes (after subcommands) \| | no · - · B | |
| r17-sonnet-export-3 | \| 161 \| options listed only after a dash vs after an empty token \| an empty token lists subcommands then options; a token starting with a dash lists matching options only \|<br>Completion output lines: `type,value` (bash/powershell/fish; fish adds `\thelp`), zsh uses three lines per item;<br>path requests have type `dir` or `file` carrying the incomplete token.<br>completion in `shell_completion.py`, runner in `testing.py`). | yes · AB · B | |

## C25 — A: PRD 110: off-flag default "remains hidden even if show-default is on" · B: Contract 150: shown for every option, "a flag whose default is `False` included"

Conflict ids in the export: CF-000162

| Run | Lines from NOTES.md | Reading | Owner |
|---|---|---|---|
| r17-haiku-markdown-1 | 11. **`show_default` on a flag whose default is off.** PRD: hidden. Interface: shown for every | yes · AB · A | |
| r17-haiku-markdown-3 | *(none)* | no · - · A | |
| r17-sonnet-markdown-1 | \| `show_default` on a flag with default `False`: PRD hides it, Contract shows it \| Shown. \| | yes · AB · B | |
| r17-sonnet-markdown-2 | \| Show default for a False flag \| PRD: hidden; Contract: shown \| Shown (`default: False`) when show-default is on (Contract). \| | yes · AB · B | |
| r17-sonnet-markdown-3 | \| 5 \| `show_default` on a single bool flag defaulting to false: contract shows it; PRD hides it. \| Hidden (a true default is shown). \| | yes · AB · A | |
| r17-haiku-export-1 | \| CF-000162 \| `show_default` on a boolean flag whose default is False \| Hidden (FP-02). \| | no · - · A | |
| r17-haiku-export-2 | \| CF-000162 \| Show-default on a `False` flag default \| Hidden (PRD FP-02) \| | no · - · A | |
| r17-haiku-export-3 | \| CF-000162 \| `show_default` on a `False` flag: hidden (FP-02) vs shown (Contract) \| hidden \| | yes · AB · A | |
| r17-sonnet-export-1 | \| FP-02 vs Contract s4 (CF-162) \| show_default on a flag defaulting to false \| hidden (single boolean flag with false default) \| | no · - · A | |
| r17-sonnet-export-2 | \| 162 \| show_default for False flag \| hidden \| | no · - · A | |
| r17-sonnet-export-3 | \| 162 \| show_default with a False flag \| the default is shown (`default: False`) when show_default is on (contract) \| | no · - · B | |

## C26 — A: PRD 104: short help "is the first sentence of the docstring" · B: Contract 55: "the start of the child’s first paragraph, cut … at 45 characters"

Conflict ids in the export: CF-000063

| Run | Lines from NOTES.md | Reading | Owner |
|---|---|---|---|
| r17-haiku-markdown-1 | 12. **Group listing short help.** PRD: the first sentence, ellipsized at the wrap width.<br>Interface: the first paragraph, cut with `...` at 45 characters. Built: the first sentence, | yes · AB · A | |
| r17-haiku-markdown-3 | *(none)* | no · - · B | |
| r17-sonnet-markdown-1 | \| Short help in group listings \| First sentence / first paragraph, cut with `...` at 45 characters. \| | no · - · A | |
| r17-sonnet-markdown-2 | *(none)* | no · - · A | |
| r17-sonnet-markdown-3 | \| 10 \| Group short help: contract "cut at 45 characters"; PRD "first sentence, ellipsized at the wrap width". \| First sentence, limit derived from the width (45 when `get_short_help_str()` is called with no limit). \| | yes · AB · A | |
| r17-haiku-export-1 | \| CF-000063 \| Subcommand short help: first sentence (FP-02) vs first paragraph cut at 45 chars (FP-02 / Interface) \| First sentence of the docstring; if longer than 45 characters, cut to 42 + `...`. An explicit `short_help` is used as given. \|<br>\| CF-000154 \| `isolated_filesystem` without a parent: removed on exit (FP-14 first sentence) vs always left in place (FP-14 last sentence) \| Always left in place. \| | yes · AB · A | |
| r17-haiku-export-2 | \| CF-000063 \| Subcommand short help: first sentence vs first paragraph cut at 45 \| First sentence; cut to 42 characters plus `...` when longer than 45 \| | yes · AB · A | |
| r17-haiku-export-3 | \| CF-000063 \| Default short help: first sentence (FP-02) vs first paragraph cut at 45 (Contract) \| first sentence, cut at 45 characters with `...` \|<br>\| 27 \| FP-09 File and path parameters \| N-000528–N-000590 (63) \| paramtypes.py File, Path, open_file \| implemented \| | yes · AB · A | |
| r17-sonnet-export-1 | \| FP-02 vs Contract s2 (CF-63) \| subcommand short help \| first paragraph up to its first sentence, cut with `...` at 45 characters (an explicit `short_help` replaces it) \| | no · - · A | |
| r17-sonnet-export-2 | \| 063 \| subcommand short help \| first sentence of first paragraph, cut with `...` at 45 characters \| | no · - · A | |
| r17-sonnet-export-3 | \| 63 \| short help of children: first sentence vs 45-char cut \| first sentence, cut with `...` at 45 characters (both rules applied) \| | yes · AB · A | |

## C27 — A: PRD 105: "The epilog is printed at the end of the help page" (also Contract 49–56) · B: Contract 74: epilog "printed right after the description, before the options"

Conflict ids in the export: CF-000047

| Run | Lines from NOTES.md | Reading | Owner |
|---|---|---|---|
| r17-haiku-markdown-1 | *(none)* | no · - · A | |
| r17-haiku-markdown-3 | \| 4 \| Contract §3 (`command` attrs `epilog`) vs. Contract §2 help layout and PRD FP-02 \| The `command` attrs text places the epilog right after the description, before the options. The help-page layout and FP-02 place it last. \| Epilog is printed last on the help page. \| | yes · AB · A | |
| r17-sonnet-markdown-1 | \| Epilog position: Contract `command` attrs "after description", help-page section "last" \| Last on the page (PRD). \| | yes · AB · A | |
| r17-sonnet-markdown-2 | \| Epilog position \| Contract (command attrs): before options; Contract (help page list) and PRD: last \| Printed last. \| | yes · AB · A | |
| r17-sonnet-markdown-3 | \| 9 \| Epilog position: contract (command attrs) says right after description; help-page list and PRD say last. \| Printed last. \| | yes · AB · A | |
| r17-haiku-export-1 | \| CF-000047 \| Epilog position: end of page (Interface section 2, FP-02) vs right after description (Interface attrs) \| End of the help page. \|<br>- Help layout: `Usage:` line, description, `Positional arguments:`, `Options:`, `Commands:`, epilog. | yes · AB · A | |
| r17-haiku-export-2 | - **Pack 06 (N-000803–849):** exit statuses (0 / 1 / 2 / author status); standalone mode raises `SystemExit`, non-standalone raises or returns; stream channels (stdout for intentional help, stderr for usage/abort/errors/deprecation, completion on stdout); help-page order (usage, description, Positio<br>\| CF-000047 \| Epilog position: end of page vs after description \| End of the help page (PRD FP-02) \| | yes · AB · A | |
| r17-haiku-export-3 | \| CF-000047 \| Epilog placement: "end of page" (FP-02) vs "right after description" (Contract) \| end of the help page (FP-02) \|<br>\| 06 \| Contract §2 Global output forms \| N-000803–N-000849 (47) \| core.py Command.format_help, Context exits; exceptions.py; decorators.py version options \| implemented \| | yes · AB · A | |
| r17-sonnet-export-1 | \| FP-02 vs Contract s3 (CF-47) \| epilog position \| printed last, after everything else \| | no · - · A | |
| r17-sonnet-export-2 | \| 047 \| epilog position \| printed last, after all other sections \| | no · - · A | |
| r17-sonnet-export-3 | \| 47 \| epilog position \| printed last on the help page (PRD item list, contract help-page order) \| | no · - · A | |

## C29 — A: PRD 194: choice "Matching is case-sensitive unless the author turns that off" (also the Contract 210 signature) · B: Contract 210: "by default the match ignores letter case"

Conflict ids in the export: CF-000163

| Run | Lines from NOTES.md | Reading | Owner |
|---|---|---|---|
| r17-haiku-markdown-1 | \| `param_types.py` \| parameter types (`STRING`, `INT`, `Choice`, `File`, `Path`, ...) \| | no · - · A | |
| r17-haiku-markdown-3 | \| 5 \| Contract §5 (`Choice`, `case_sensitive=True`) vs. the same entry's note on enums \| The signature defaults to case-sensitive, but the enum note says enum matching ignores case by default. \| `case_sensitive` defaults to `None`: enum choices match ignoring case, list choices match case-sensitivel<br>## Other choices (where the spec leaves the form to the implementer)<br>- Default option metavars: `TEXT` for strings, `INTEGER` for ints, `FLOAT`, `BOOLEAN`, `UUID`, `DATETIME`; choices show `[a\|b]`. | yes · AB · A | |
| r17-sonnet-markdown-1 | # Notes: specification conflicts and the choice made<br>\| Conflict \| Choice \|<br>\| Choice with an `Enum`: Contract "matched ignoring case by default", signature `case_sensitive=True` \| Exact name match first, then a case-insensitive fallback for enums; plain choices are case-sensitive unless `case_sensitive=False`. \| | yes · AB · A | |
| r17-sonnet-markdown-2 | ## Spec disagreements and the choice made<br>\| Enum `Choice` case \| Contract: enum match ignores case by default \| List choices are case-sensitive by default; enum choices ignore case unless `case_sensitive=` is passed. \| | no · B · A | |
| r17-sonnet-markdown-3 | ## Spec disagreements and the choice made<br>\| 8 \| `Choice` over an Enum: contract says case-insensitive by default; PRD says case-sensitive unless turned off. \| Case-sensitive unless `case_sensitive=False`. \| | yes · AB · A | |
| r17-haiku-export-1 | \| CF-000163 \| `Choice` matching: case-sensitive by default (signature, FP-05) vs ignores case by default (Interface note) \| Case-sensitive by default. \|<br>Other choices where the spec left the form to the implementer: | yes · AB · A | |
| r17-haiku-export-2 | \| `paramtypes.py` \| `ParamType`, built-in types, `Choice`, `DateTime`, `IntRange`, `FloatRange`, `Tuple`, `File`, `Path` \| 09, 23, 27 \|<br>- **Pack 04 (N-000790):** the form of anything the contract leaves open is my choice (listed below).<br>- **Pack 05 (N-000791–802):** package root exports, `optlyn.testing.CliRunner`, `optlyn.formatting.wrap_text`; additional exports are my choice.<br>## Conflicts and the choice I made<br>\| CF-000163 \| Choice matching: case-insensitive by default vs case-sensitive \| Case-sensitive unless `case_sensitive=False` (PRD FP-05) \|<br>Choices where the spec leaves the form open (contract and PRD "implementer's choice"): | yes · AB · A | |
| r17-haiku-export-3 | The export was made with `--allow-open`, so 28 contradictions have no human verdict (listed in `spec/MAP.md`). For each, the choice below was made. Where a PRD feature point and the Interface Contract disagree, the PRD's more specific feature statement was followed unless noted.<br>\| CF-000163 \| `Choice` matching case: sensitive by default (FP-05) vs insensitive (Contract, for enum names) \| case-sensitive by default; `case_sensitive=False` turns it off \|<br>Other choices where the spec leaves room or the statements interact:<br>- `token_normalize_func` applies to option names, choice values and command names. | yes · AB · A | |
| r17-sonnet-export-1 | \| Contract s5 vs FP-05 (CF-163) \| Choice case sensitivity default \| case-sensitive (`case_sensitive=True`) \|<br>Other choices: a single boolean flag delivers `True` when present even with default `True`; | no · - · A | |
| r17-sonnet-export-2 | as follows. Where the choice is not listed the spec was consistent.<br>\| 163 \| Choice case \| case-sensitive by default \|<br>Other choices: declaration errors raise `DeclarationError` (subclass of TypeError, ValueError, | no · - · A | |
| r17-sonnet-export-3 | ## Spec contradictions and the choice made for each<br>The spec has 28 unsettled contradictions (CF ids). Choices:<br>\| 115 \| metavar "type name" vs `--count COUNT` \| built-in scalar types show the parameter's destination name upper-cased (`--count COUNT`); custom `ParamType` shows its `name` upper-cased; Choice shows `[a\|b]` \|<br>\| 163 \| Choice case sensitivity default \| case-sensitive by default (signature `case_sensitive=True`); enum members matched by name \|<br>Other choices: a group invoked with no arguments (default policy) prints its help to stderr and exits 2 | no · - · A | |

