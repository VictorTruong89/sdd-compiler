# Optlyn — build notes

Implementation of the spec in `spec/` (33 packs, 1014 checklist ids). Code lives in
`src/optlyn/`, tests in `tests/`. Run tests with `PYTHONPATH=src python -m pytest tests`.
Pure Python 3.10+, no runtime dependencies. `spec/` is untouched.

## Layout

| Module | Covers |
|---|---|
| `core.py` | `Context`, `Parameter`/`Option`/`Argument`, `Command`, `Group`, `CommandCollection`, invocation, help |
| `parser.py` | token parsing: flags, stacks, `--`, nargs, variadic binding |
| `param_types.py` | built-in and custom types (`Choice`, `DateTime`, ranges, `Tuple`, `File`, `Path`) |
| `decorators.py` | `command`, `group`, `option`, `argument`, ready-made options, pass-context helpers |
| `termui.py` | `echo`, `style`, prompts, `confirm`, `getchar`, pager, progress bar, editor, launch, clear |
| `utils.py` | file opening (lazy/atomic/dash), `format_filename`, `get_app_dir` |
| `formatting.py` | `wrap_text`, help layout |
| `shell_completion.py` | `_<PROG>_COMPLETE` modes: registration scripts and suggestion output |
| `testing.py` | `CliRunner`, `Result` |

`# spec: <id>` comments sit beside the functions that implement each id.

## Conflicts in the spec and what was built

1. **Deprecated command warning channel.** The channel table says stderr; the PRD FP-01 says stdout, and the compiler ruling (CF-000146) picks FP-01. Built: command deprecation goes to stdout, ahead of the command's output. Option and argument deprecation warnings go to stderr.
2. **Default map vs environment.** FP-03 ranks environment above the default map; the Contract row says the default map wins (CF-000150). Built: command line, then default map, then environment, then declared default.
3. **Standalone `confirm` on an odd answer.** FP-08 says "asks again"; the Contract row says it counts as no (CF-000151). Built: only `y`/`yes` is yes; an empty answer takes the default; anything else is no and is not re-asked.
4. **Parameter callback for an omitted parameter.** The terminology says the callback is not called when nothing supplied a value; FP-03 says a missing parameter still runs its callback (so it can default from an earlier parameter). Built: FP-03 — the callback runs with `None` (or the default).
5. **Maximum content width.** FP-02 says 80 columns by default for help; pack 29 says 100 for help pages and wrapped text. Built: help pages use 80 (`max_content_width`); `wrap_text` defaults to 100.
6. **Option metavar.** The rule says "the type name in uppercase", but the example says `--count` shows `COUNT`, which the type name would not give (`INT`). Built: an option's metavar is its destination name in uppercase, unless it is a choice (`[a|b]`) or an author `metavar`. Flags have none.
7. **`isolated_filesystem` cleanup.** One sentence says the directory is removed when no parent is given; another says it is always left in place. Built: always left in place.
8. **Prompt semantics.** `prompt_required=True` (the default) prompts when the option is omitted; `prompt_required=False` prompts only when the flag is given without a value. A required prompting option prompts in both cases.
9. **Optional-value options.** The spec describes the form but names no keyword. Built: a non-flag option with `flag_value=` set takes an optional value.
10. **Variadic argument required by default.** A bare variadic argument is optional (empty tuple when omitted), per FP-04; it is required only when marked `required=True`.

## Behaviour choices the spec left open

- Group child contexts are created after the group callback runs, so a group can set `ctx.obj` for its children. An unknown subcommand name is still rejected before the group callback runs.
- Chaining groups parse all subcommand tokens before the group callback, because the leftover tokens decide which subcommand comes next.
- Usage errors print the usage line and `Try '<prog> --help' for help.` before `Error: ...` on stderr. Help shown for incorrect usage is printed on stderr.
- A clean stop with status `n` exits with `n`. With standalone mode off, a clean stop returns the status; failures raise.
- Completion output lines are `plain,<value>`, `file,<incomplete>`, `dir,<incomplete>`, with `\t<help>` appended for zsh and fish.
- Completion functions receive a best-effort `ctx.params` built from the tokens already on the line.
- The auto-env name is the prefix, then the subcommand names below the root, then the destination, upper-cased with `_` separators.
- Feature-switch options sharing one destination: the most explicit source wins, then an explicit default over an auto-derived one, then the last declared.
- `CliRunner.invoke` in `capture="fd"` mode returns stdout followed by stderr in `output`, not interleaved in write order.
- `default` and `required` combinations that the spec forbids raise `TypeError` when the decorator is applied (for example deprecated + prompt, deprecated + required, clamp with an open float bound, a second variadic argument on a command).
- `Option.metavar` / `Argument.metavar` store the author string as given (`None` when not set).

## Coverage and gaps

Every pack in `spec/` is implemented. The behaviours that the tests exercise are covered by `tests/test_optlyn.py` and `tests/test_optlyn_more.py` (126 tests, all passing); test names carry the node ids they exercise. Not every one of the 1014 ids has its own test, and I did not check each id line by line against the code. The `# spec:` markers point at the functions that carry most of the behaviour, not at every id.

Not done, with reasons:

- **N-000049 (assumption) and the Windows-only sentence in pack 17**: glob, home-directory and environment-variable expansion of the argument list on Windows is not implemented. The target is Linux, and the spec says Windows is only "intended to work". The Windows path is otherwise the same code.
- **Interleaved output in fd capture** (see above) is approximated, not write-ordered.
- **Packaging as a console script** is out of scope: the spec says it is not an Optlyn command.
