# Optlyn — implementation notes

Layout: `src/optlyn/` (pure Python, no runtime dependencies, Python 3.10+).
Tests: `tests/test_optlyn.py` (`PYTHONPATH=src python3 -m pytest tests`).

Modules:

| module | role |
| --- | --- |
| `core.py` | `Command`, `Group`, `CommandCollection`; token scanning, dispatch, `main`, help |
| `params.py` | `Parameter`, `Option`, `Argument`; value sources and callbacks |
| `paramtypes.py` | built-in and custom parameter types (`Choice`, `File`, `Path`, ...) |
| `context.py` | `Context`, `ParameterSource`, `get_current_context` |
| `decorators.py` | `command`, `group`, `option`, `argument`, ready-made option decorators, pass decorators |
| `termui.py` | echo, styling, prompts, pager, progress bar, files |
| `completion.py` | completion items, registration scripts, `*_complete` suggestions |
| `formatting.py` | `wrap_text` and the help formatter |
| `testing.py` | `CliRunner` and `Result` |
| `exceptions.py` | exit-status classes (`UsageError` 2, `Abort`/general 1, `Exit`) |

`paramtypes.py` is named to avoid shadowing the standard `types` module.

## Choices where the specification disagrees or is silent

1. **Deprecation warning channel.** FP-01 says standard output; the Interface
   Contract channel table says standard error. Built: standard error (the contract
   table is the integrator-facing interface).
2. **Callback for an omitted parameter.** The PRD terminology says a parameter
   callback is not called when the parameter was omitted and had no value; FP-03
   says a missing parameter still runs its callback so it can default from an
   earlier value. Built: the callback always runs, with `None` (or `()` for
   variadic/repeatable values) when there is no value.
3. **Help width.** FP-02 says the maximum content width defaults to 80; FP-11 says
   help pages and wrapped text default to 100. Built: 80 for help pages
   (`max_content_width` setting) and 80 as the `wrap_text` default.
4. **`isolated_filesystem`.** The PRD says the directory is removed on exit when no
   parent is given, and also that it is always left in place. Built: removed when no
   parent is given; left in place when a parent path is given.
5. **No-arguments help for a leaf or group.** FP-02 places "no-args-is-help" paths in
   the usage-error class. Built: help goes to standard error and the exit status is 2
   (intentional `--help` is 0).
6. **Destination inference.** The spec order is "valid identifier, then first long
   name, then first short name". Built: first long name, then first short name, so
   `-c/--count` yields destination `count`.
7. **Empty variadic argument.** FP-04 says a variadic argument is optional unless
   marked required; the general "no default means required" rule is overridden for
   variadic arguments.
8. **Standalone-off help/version.** Printed on standard output, then the call returns
   `None` (no exception), matching a clean stop.

## Known gaps (not finished)

- **Group option mixing** (`allow mixing on a group`, FP-03/FP-06) is not implemented;
  group options must precede the subcommand name.
- **Lazy loading** works through overridable `list_commands`/`get_command`; no plugin
  folder format is shipped (not required).
- **Completion** is complete for Bash (4.4+). Zsh, Fish and PowerShell emit scripts
  and suggestions in the basic form; per-shell edge cases (path requests in zsh/fish,
  help display details) are minimal.
- **Progress bar** is a simple renderer: it visits every item and shows a remaining
  estimate, but `progressbar(**options)` ignores extra options.
- **Pager** uses `PAGER` only when both stdin and stdout are terminals; chunked output
  is written as it arrives.
- **Editor, launch, getchar** are minimal: `edit` uses the editor's exit and file
  modification time to detect a save; `launch` uses `open`/`xdg-open`/`startfile`;
  `getchar` reads raw input from `/dev/tty` when present.
- **Parameter-type coverage** is per the table, but `DateTime` and `Path` path-type
  checks are the simplest reading of the spec.
- Tests cover the main flows only (13 tests); the PRD has many more edge cases that
  are not individually tested.
