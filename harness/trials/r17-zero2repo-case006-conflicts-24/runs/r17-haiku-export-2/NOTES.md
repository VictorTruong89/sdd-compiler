# Optlyn — implementation notes

Build of the specification in `spec/` (33 packs, 1044 ids). `spec/` is untouched.

- Package: `src/optlyn/` (src layout, Python 3.10+, standard library only).
- Packaging: `pyproject.toml` (PEP 517, setuptools, no runtime dependencies).
- Tests: `tests/test_optlyn.py` (135 behavioural tests, one group per feature point).
  Run with `PYTHONPATH=src python3 -m pytest tests`.

## Module map

| Module | Responsibility | Packs |
|---|---|---|
| `__init__.py` | root exports (`from optlyn import …`) | 05 |
| `exceptions.py` | usage / bad-parameter / missing / abort / exit / file errors; exit statuses | 06, 08, 31 |
| `core.py` | `Parameter`, `Option`, `Argument`, `Context`, `Command`, `Group`, `CommandCollection`; parsing pipeline; help page; `main` | 07, 08, 10, 19–24, 31, 32 |
| `parser.py` | POSIX option tokenizer (stacking, `--`, `=`, alternate prefixes, unknown-option handling) | 21, 17 |
| `decorators.py` | `command`, `group`, `option`, `argument`, ready-made options, `pass_*`, `make_pass_decorator` | 07, 08, 10 |
| `paramtypes.py` | `ParamType`, built-in types, `Choice`, `DateTime`, `IntRange`, `FloatRange`, `Tuple`, `File`, `Path` | 09, 23, 27 |
| `termui.py` | echo/styling/prompt/confirm/getchar/pause/edit/launch/clear/pager/progress | 11, 29 |
| `utils.py` | file opening (lazy/atomic/dash), `get_app_dir`, `format_filename`, stream accessors | 11, 27, 29 |
| `formatting.py` | `wrap_text` (backspace rule, any string), definition-list layout | 06, 11, 20, 29 |
| `shell_completion.py` | `_<PROG>_COMPLETE` handling, `{shell}_source` / `{shell}_complete` for bash/zsh/fish/powershell | 12, 30 |
| `testing.py` | `CliRunner`, `Result`, `isolated_filesystem` | 13, 32 |
| `_globals.py` | thread-local current-context stack | 10, 17 |

## Coverage by pack

Every id is covered at the level of its pack. No id is marked "not done" for the core behaviour. Known gaps are listed under "Not verified or partial".

- **Packs 01–03 (hardware, profiles):** pure Python, zero runtime dependencies, src layout, PEP 517 build. Importing does no I/O.
- **Pack 04 (N-000790):** the form of anything the contract leaves open is my choice (listed below).
- **Pack 05 (N-000791–802):** package root exports, `optlyn.testing.CliRunner`, `optlyn.formatting.wrap_text`; additional exports are my choice.
- **Pack 06 (N-000803–849):** exit statuses (0 / 1 / 2 / author status); standalone mode raises `SystemExit`, non-standalone raises or returns; stream channels (stdout for intentional help, stderr for usage/abort/errors/deprecation, completion on stdout); help-page order (usage, description, Positional arguments, Options, Commands, epilog); version identity page.
- **Pack 07 (N-000850–880):** `command`, `group`, `Group`, `CommandCollection`, `add_command`, `command()`/`group()` child helpers, `result_callback()`, `list_commands`/`get_command` override points, `main`/`__call__`.
- **Pack 08 (N-000881–935):** `option` and `argument` keywords, on/off pairs, delivered-value table (scalar, tuple, `()`, `None`, flag, count), `BadParameter`, ready-made `help_option`, `version_option`, `custom_version_option`, `password_option`, `confirmation_option`.
- **Pack 09 (N-000936–949):** all listed types and `ParamType` subclassing (`convert(value, param=None, ctx=None)`).
- **Pack 10 (N-000950–980):** `Context` settings and members, `pass_context`, `pass_obj`, `make_pass_decorator`, `get_current_context(silent=…)`, per-thread stack.
- **Pack 11 (N-000981–1012):** all terminal helpers; `echo` to stdout/stderr/file; styling; pager via `PAGER`; progress bar; `getchar`; `pause`; `edit`; `launch`; `clear`; `get_app_dir`; `format_filename`; `open_file`.
- **Pack 12 (N-001013–1037):** completion variable name, instructions, COMP_WORDS/COMP_CWORD handling, suggestion output, `shell_complete` on options and types, `CompletionItem` (`value`, `help`, `type`).
- **Pack 13 (N-001038–1044):** `CliRunner.invoke` (args, input, env with `None` unset, extra context settings), `Result` attributes, `isolated_filesystem`.
- **Packs 14–18 (PRD overview, terminology, surface, non-functional, non-goals):** the feature set above. Non-goals are respected: no built-in aliases, plugin discovery, config-file syntax, server/GUI, or thread-safe mutation of contexts.
- **FP-01 … FP-14 (packs 19–32) and cross-cutting refinements (pack 33):** implemented in `core.py` (parsing, groups, chaining, help, eager flags, prompts, value sources, exit classes), `paramtypes.py`, `utils.py`, `termui.py`, `shell_completion.py`, `testing.py`.

## Conflicts and the choice I made

The export was made with `--allow-open`, so 28 contradictions have no verdict. Each is resolved below. Where the PRD and the Interface Contract disagree on behaviour, I followed the PRD, as the contract defers behaviour to it (pack 04).

| Id | Disagreement | Built |
|---|---|---|
| CF-000010 | Omitted repeatable option: absent value vs empty tuple | Empty tuple `()` (PRD FP-03, contract table) |
| CF-000016, CF-000092 | Clamp past an open integer bound: adjacent integer vs bound | Adjacent integer inside the range (`IntRange`) |
| CF-000100, CF-000107 | `FloatRange` clamp with an open bound: allowed vs refused | Refused at construction (`ValueError`) |
| CF-000034, CF-000072 | Source precedence: environment above default map, or the reverse | Command line > prompt > environment > default map > declared default (PRD FP-03) |
| CF-000047 | Epilog position: end of page vs after description | End of the help page (PRD FP-02) |
| CF-000048 | Counting option omitted: `0` vs `None` | `0` (PRD FP-03) |
| CF-000063 | Subcommand short help: first sentence vs first paragraph cut at 45 | First sentence; cut to 42 characters plus `...` when longer than 45 |
| CF-000087 | Default maximum content width: 80 vs 100 | 80 for auto-detected width; an explicit terminal width is used as given |
| CF-000088 | Environment name list: first set wins vs last set wins | First set wins (PRD FP-03); the automatic prefix name is tried last |
| CF-000115 | Metavar of `--count` with an integer type: `INTEGER` vs `COUNT` | The type name uppercased (`INTEGER`); the example in the PRD is not followed |
| CF-000128 | Non-interactive `pause`: does nothing vs prints its message | Prints the message; does not block |
| CF-000129 | Application directory on Unix: `$XDG_CONFIG_HOME` vs always `~/.config` | `$XDG_CONFIG_HOME` when set, else `~/.config` (PRD) |
| CF-000134, CF-000159 | Confirmation mismatch and conversion failure at a prompt: re-ask vs abort/not asked again | Re-ask (PRD FP-08). Command-line conversion failures remain usage errors |
| CF-000136 | Date-time formats: added to the defaults vs replace them | Replace the defaults (PRD FP-05) |
| CF-000151, CF-000157 | Boolean flag from an environment variable with an unrecognized value: usage error vs "turns the flag off" | Usage error for an unrecognized non-empty value. A flag with a non-boolean flag value treats an unrecognized value as unset |
| CF-000154 | Isolated filesystem: removed on exit vs always left in place | Always left in place (so files can be inspected) |
| CF-000155 | Callback for a missing parameter: runs vs not called | Runs (PRD FP-03: a missing parameter still runs its callback, so it can default from earlier values) |
| CF-000156 | Form feed in a docstring: text after it kept vs omitted | Text after the form feed is omitted (PRD FP-02) |
| CF-000158 | Date-time format match: first success vs last matching format | First success wins (PRD FP-05) |
| CF-000160 | `Path(resolve_path=True)` and a leading `~`: expanded vs not | Not expanded (PRD FP-09) |
| CF-000161 | Completion of an empty token: subcommands then options vs subcommands only | Subcommands only; options appear once a dash is typed (PRD FP-12) |
| CF-000162 | Show-default on a `False` flag default | Hidden (PRD FP-02) |
| CF-000163 | Choice matching: case-insensitive by default vs case-sensitive | Case-sensitive unless `case_sensitive=False` (PRD FP-05) |

Choices where the spec leaves the form open (contract and PRD "implementer's choice"):

- Help layout details: section headings are `Positional arguments:`, `Options:` and `Commands:`; option names are shown as declared (`--a/--b` for on/off pairs, `-v, --verbose` for aliases); the default is shown as `[default: …]`, env var as `[env var: …]`, deprecation as `(deprecated)`; a deprecated command's page begins with `(Deprecated)`.
- Usage: `[OPTIONS]` placeholder; `[ARGS]...` / `NAME...` for variadic; `COMMAND [ARGS]...` for groups; `[COMMAND] [ARGS]...` when the group can run without a subcommand; chaining groups use `COMMAND [ARGS]... [COMMAND [ARGS]...]...`.
- Error reports: `Usage: …`, `Try '<prog> --help' for help.`, then `Error: …`. Argument identities use the declared name as written.
- `invoked_subcommand` in a chaining group is a private sentinel that is neither `None` nor a child name.
- Context settings: `invoke` supplies the callee's defaults for parameters the caller does not pass; `forward` passes the caller's values.
- Completion output: `@path:file:<token>` / `@path:dir:<token>` for path requests, `value\thelp` for zsh and fish; unknown instruction → message on stderr, exit 2, callback not run.
- Deprecation warnings: `DeprecationWarning: …` on stderr.
- Version identity: `%(prog)s, version %(version)s` unless a message is given. The version is detected from the given distribution name, falling back to the distribution providing that import name.
- Exceptions other than the ones named in the spec are my own (`UsageError`, `BadParameter`, `MissingParameter`, `NoSuchOption`, `FileError`, `Abort`, `Exit`).

## Not verified or partial

These were written but not exercised in a real environment:

- **`getchar`** reads from standard input. The spec asks for the controlling terminal even when stdin is a pipe; I did not implement raw terminal mode. The interrupt and end-of-file keys map to `KeyboardInterrupt` / `EOFError`.
- **Hidden input** uses `getpass` on a real terminal; that path is untested here (no TTY in this environment). Under the runner, hidden input is read normally and not echoed.
- **Shell completion scripts** for zsh, fish and PowerShell were not run in their shells. Bash's script is the most straightforward and was checked only by its text.
- **`launch`, `edit`, `get_app_dir`**: the macOS and Windows branches are written but untested; `launch` uses `xdg-open` on Linux.
- **Pager**: uses `PAGER` only when the session is interactive; otherwise writes to standard output.
- **Progress bar**: draws a simple bar with a remaining-time estimate when standard output is a terminal; the appearance is not tuned.
- **`version_option`** without an explicit version infers the package from the caller's module name; this is an approximation of "the author's package".
- **`ParamType` shell completion for `Path`/`File`** only asks the shell for a path (file or directory); it does not list entries.

## Traceability

I did not put `# spec: <id>` comments in the code. I tried, but I could not verify each id-to-text mapping from the export, so I removed the guesses rather than leave misleading markers. The pack-level map above is the traceability record.
