# Optlyn implementation notes

Package: `src/optlyn/` (importable as `optlyn` with `PYTHONPATH=src`). Pure Python 3.10+, no runtime dependencies.

| Module | Contents |
| --- | --- |
| `core.py` | `Command`, `Group`, `CommandCollection`, the option/argument scanner, eager processing, help rendering, dispatch |
| `parameters.py` | `Parameter`, `Option`, `Argument`: declaration, value sources, prompts, callbacks |
| `paramtypes.py` | `ParamType` and the built-in types (`STRING`, `INT`, `FLOAT`, `BOOL`, `UUID`, `UNPROCESSED`, `Choice`, `DateTime`, `IntRange`, `FloatRange`, `Tuple`, `File`, `Path`) |
| `context.py` | `Context`, `get_current_context` (thread-local) |
| `decorators.py` | `command`, `group`, `option`, `argument`, ready-made options, `pass_context`, `pass_obj`, `make_pass_decorator` |
| `termui.py` | echo, styling, prompt, confirm, getchar, pause, pager, progress bar, edit, launch, clear, app dir, filename, open_file |
| `formatting.py` | `wrap_text` and help-table layout |
| `shell_completion.py` | Bash, Zsh, Fish and PowerShell registration scripts and suggestion output |
| `testing.py` | `CliRunner` (`capture="sys"` or `"fd"`), `Result`, `isolated_filesystem` |
| `exceptions.py` | `OptlynError`, `UsageError` (exit 2), `BadParameter`, `Abort` and `FileError` (exit 1), `Exit` |

## Rule used when the specification disagrees with itself

The Contract says behaviour is defined by the PRD. So when a PRD statement and a Contract statement give different concrete behaviour, the PRD wins, except where the PRD itself has a more specific sentence on the same point (noted below). Each entry gives the two sides and what was built. IDs `C-xx` match `spec/CONFLICTS.md`; `X-xx` are disagreements the reviewer's list does not contain.

### C-01: form feed in a docstring
- PRD FP-02, Normal behavior (line 102): "A form-feed character in the docstring truncates the help: text after that character is omitted from the page."
- Contract §3 `command`, `attrs`: "a form-feed character in it is dropped and the text after it is kept."
- **Built:** truncation at the form feed (PRD), for docstrings and explicit `help=` text.

### C-02: short help for subcommands on a group page
- PRD FP-02 (line 104): "the short help is the first sentence of the docstring by default, ellipsized if it cannot fit on one line at the wrap width."
- Contract §2, Help page, item 5: "by default the start of the child's first paragraph, cut with `...` at 45 characters."
- **Built:** the first sentence (PRD), cut with `...` when it does not fit the wrap width. No fixed 45-character limit.

### C-03: epilog position
- PRD FP-02 (line 105): "The epilog is printed at the end of the help page, after everything else on it." Contract §2 item 6 also places it last.
- Contract §3 `command`, `attrs`: "`epilog` (printed right after the description, before the options)."
- **Built:** at the end of the page.

### C-04: default maximum content width
- PRD FP-02 (line 107): "a maximum content width that defaults to 80 columns and can be raised by the caller caps auto-detected width only."
- PRD FP-11 (line 340): "Help pages and wrapped text use a maximum content width of 100 columns unless the caller sets another."
- **Built:** help pages cap the auto-detected width at 80 (`max_content_width` raises the cap). `wrap_text()` defaults to 100. An explicit `terminal_width` is used as-is.

### C-05: default metavar and its example
- PRD FP-02 (line 108): the metavar is "the type name in uppercase"; the example says an integer `--count` appears as `--count COUNT`.
- **Built:** the rule. An integer option shows `--count INTEGER`. The example cannot hold, since the uppercased type name is never `COUNT`.

### C-06: showing a default of `False` on a boolean flag
- PRD FP-02 (line 110): "For a single-option boolean flag whose default is off (false), that default remains hidden even if show-default is on."
- Contract §4 `show_default`: "when on, the default is shown for every option, a flag whose default is `False` included."
- **Built:** hidden for a false flag default (PRD). A true default is shown.

### C-07: counting option when omitted
- PRD FP-03 (line 137): "A counting option yields how many times it occurred (zero if omitted)."
- Contract §6 delivered-values table: "an `int`, or `None` when the option was omitted."
- **Built:** `0`.

### C-08: several environment variable names
- PRD FP-03 (line 141): "an option may name one variable or a list of names (first one set wins)."
- Contract §4 `envvar`: "with a list, the last name that is set wins."
- **Built:** the first name that is set (PRD).

### C-09: unrecognised environment value for a boolean flag
- PRD FP-03 (line 142): "Any other non-empty string is a conversion usage error, not a silent deactivation."
- PRD FP-05 (line 192): "For a boolean flag read from an environment variable, any other value turns the flag off."
- **Built:** a usage error (the FP-03 rule is specific to flags). For a flag with a non-boolean `flag_value`, an unrecognised value counts as unset, as FP-03 says.

### C-10: prompting option that is omitted
- PRD FP-08 (line 268): "An option with prompting enabled, if not supplied on the command line, reads a line from the user."
- PRD FP-08 (line 269): "the option does not prompt when fully omitted; it prompts when the flag is present without a value."
- **Built:** `prompt_required` decides, and it defaults to `True`, which matches the name in Contract §4 and gives the line-268 rule. `prompt_required=False` gives the line-269 rule. A required prompting option always prompts when omitted. `password_option` keeps `prompt_required=True`.

### C-11: mismatched confirmation entries
- PRD FP-08 (line 272): the pair is asked again and "mismatched values are not delivered."
- PRD FP-13 (line 381): "two different values typed into a confirmation prompt" yields abort, exit 1.
- **Built:** ask the pair again (the prompt-specific rule). End of input during a prompt still aborts with exit 1.

### C-12: conversion failure at a prompt
- PRD FP-08 (line 274): "Prompts re-ask on conversion failure."
- PRD FP-13 (line 380): "conversion failure (including a value typed at a prompt, which is not asked again)."
- **Built:** the prompt re-asks. The usage-error exit applies to values given on the command line.

### C-13: date-time format precedence
- PRD FP-05 (line 195): "Formats are tried in order; the first success wins."
- Contract §5 `DateTime`: "When several formats match a value, the last matching format is used."
- **Built:** the first matching format.

### C-14: author format list
- PRD "Public surface inventory" (line 40): "an author's date-time format list is added to the default formats."
- PRD FP-05 (line 195): "which replaces the default list (it does not extend it)."
- **Built:** the author list replaces the defaults.

### C-15: case sensitivity of `Choice`
- Contract §5 `Choice`: "`case_sensitive=True` ... (members are matched by name; by default the match ignores letter case)."
- PRD FP-05 (line 194): "Matching is case-sensitive unless the author turns that off."
- **Built:** case-sensitive by default for lists and enumerations alike. `case_sensitive=False` ignores case.

### C-16: clamping an integer range at an open bound
- PRD FP-05 (line 196): the value is replaced by "the adjacent integer inside the range for an open bound."
- Contract §5 `IntRange`: "a value beyond an open bound becomes that bound's value."
- **Built:** the adjacent integer (PRD). `IntRange(min=0, min_open=True, clamp=True)` maps `0` to `1`.

### C-17: clamping a float range with an open bound
- PRD FP-05, Normal behavior (line 197): "Clamp is only allowed when both bounds are closed." Boundary (line 208): "Float range refuses clamp when a bound is open (declaration error)."
- Contract §5 `FloatRange`: "With `clamp=True` and an open bound, a value beyond that bound becomes the bound."
- **Built:** `FloatRange` with `clamp=True` and an open bound raises `ValueError` when constructed.

### C-18: tilde with `resolve_path`
- PRD FP-09 (line 292): "resolve to an absolute path (symlinks resolved to their real target; a leading tilde is not expanded)."
- Contract §5 `Path`: "With `resolve_path=True`, a leading `~` is first expanded to the home directory."
- **Built:** no tilde expansion (PRD). `resolve_path` uses `os.path.realpath`.

### C-19: application config directory on Unix
- PRD FP-11 (line 339): "it sits under the user's config home (`$XDG_CONFIG_HOME` when that variable is set, otherwise `.config`...)."
- Contract §7 `get_app_dir`: "On Unix the directory is always under `~/.config`."
- **Built:** `$XDG_CONFIG_HOME` when it is set and non-empty (PRD).

### C-20: option names for an empty completion token
- PRD FP-12 (line 358): "Options are listed only once at least a dash has been typed."
- Contract §8: "the suggestions for an empty token are the subcommand names followed by the option names."
- **Built:** no option names for an empty token (PRD). Subcommands are listed.

### C-21: interactive session with piped stdin and terminal stdout
- PRD Terminology (line 32): "A run whose standard input is attached to a terminal (PTY), or whose standard input or standard output is a TTY. A piped standard input without a terminal is not interactive."
- **Built:** interactive when stdin **or** stdout is a TTY. Piped stdin alone is not interactive. This governs pause, pager, and `getchar`.

### C-22: callback for an omitted parameter
- PRD Terminology, Callback (line 28): "A parameter callback is not called for a parameter that was omitted and received no value from any source."
- PRD FP-03 (line 145): "A missing parameter still runs its callback, so that callback can default from an earlier parameter's value."
- **Built:** callbacks run for every declared parameter, omitted or not, and receive `None`, `()` or the absent value. The FP-03 rule is the specific one.

### C-23: default map versus environment
- PRD FP-03 (line 143): the order is command line, environment, default map, declared default.
- Contract §6 `default_map`: "its values take precedence over environment variables."
- **Built:** the PRD order. The environment beats the default map.

### C-24: group given only options, with no subcommand
- PRD FP-06 (line 234): "group options or arguments only ... they do not use the no-arguments help page."
- PRD FP-02 (line 118) and FP-13 (line 380): a group invoked with no subcommand under no-args-is-help prints the help page.
- **Built:** the help page (exit 2) is shown only for an invocation with no arguments at all. Options or arguments without a subcommand give "Missing command." (exit 2), with no help page.

### C-25: removal of the isolated working directory
- PRD FP-14 (line 403): "When no parent is given, the runner removes that directory on exit." The same bullet: "The new directory is always left in place after the block ends."
- **Built:** removed on exit when no parent is given. Left in place when a parent path is given.

### X-01: default for a repeatable option that is omitted
- PRD FP-01 (line 84): "A repeatable option that was omitted and has no default is passed as an absent value."
- PRD FP-03 (line 138) and Contract §6 table: "the callback receives an empty tuple, not an absent value" / `()`.
- **Built:** `()`.

### X-02: date-time format directives
- Contract §5 `DateTime(formats=None)`: "a sequence of `strftime` format strings."
- PRD FP-05 (line 195) describes the same formats as parsing formats.
- **Built:** the formats are used with `datetime.strptime`, which is the parsing counterpart of the same directives.

### X-03: `prompt_required` is not defined in the PRD
- Contract §4 lists `prompt_required` without a definition. PRD FP-08 only describes the two behaviours.
- **Built:** see C-10.

## Choices the specification leaves open

- **Feature-switch groups** (several options sharing a destination): the most explicit source wins (prompt > command line > environment > default map > declared default). A flag's implicit `False` default ranks lowest. Ties go to the option declared last. Among command-line flags, the source rank decides, not the order typed.
- **Chaining** (`chain=True`): each subcommand's options must come before its arguments. A subcommand hands its unconsumed tokens to the next command name. Unknown names are an error, reported when reached.
- **Group arguments** take fixed-size chunks of the tokens before the subcommand name. A variadic group argument is not supported.
- **`invoke` / `forward`**: `invoke` fills omitted declared parameters with their declared defaults. `forward` passes this context's values, filtered to the target's parameters.
- **Completion protocol**: one suggestion per line. Path requests are the lines `__optlyn_path_file__ <token>` and `__optlyn_path_dir__ <token>`. Zsh and Fish append `\t<help>`. An unknown instruction prints nothing on stdout, a message on stderr, and exits 1.
- **Standard streams for `-`** are non-closing proxies. Closing them only flushes.
- **`CliRunner(capture="fd")`** redirects descriptors 1 and 2 to temporary files. `Result.output` is stdout followed by stderr, because the relative order of the two descriptors cannot be recovered.
- **`CliRunner` input echo**: prompts echo their typed line into the captured output. With `echo_stdin=True`, every line read from stdin is echoed.
- **Deprecation warnings** go to stderr as `DeprecationWarning: ...`. They are emitted for a command on invocation, and for an option or argument only when the user supplied it.
- **`version_option`** without a version string uses the installed distribution named by `package_name`, falling back to the distribution that provides that import name. If neither works, the identity says `unknown`.
- **`pause` and `getchar`** on POSIX read `/dev/tty` when it exists, so a piped stdin is not consumed. Without a terminal, `getchar` reads stdin.
- **`launch`** on Linux runs `xdg-open`. It returns 127 when the opener is missing.
- **`edit`** runs the editor on a temporary file with the given extension. With `require_save` and no change, it returns `None`.

## Not implemented or only partly implemented

- Windows-only behaviour is not implemented: glob, home-directory and environment-variable expansion of argument tokens, and `msvcrt`-based `getchar`. Windows is not exercised in this environment.
- Multi-character single-dash option names are not supported (they are read as a stack of single-character flags, as specified).
- `ignore_unknown_options` on a group only drops unknown options before the subcommand name. Unknown options after it go to the child.
- The completion scripts are minimal. They were not run inside real shells. Suggestion output was checked with `*_complete` instructions.
- `PAGER` unset in an interactive session writes to stdout instead of starting a default pager.

## Verification

- Ad-hoc smoke scripts (kept outside the repository, under `/tmp`) exercised: commands and groups, help layout, option and argument sources (command line, environment, auto-prefix, default map, prompts, confirmation, password), types and ranges, file and path handling, chaining and result callbacks, `invoke` and `forward`, eager help and version ordering, deprecation, completion for Bash, Zsh and Fish, runner capture in `sys` and `fd` modes, and isolated filesystems.
- The smoke scripts run under Python 3.13 and 3.11. The output matches except for one traceback message wording. `pyflakes` reports no issues.
- No test suite is included in the repository.
