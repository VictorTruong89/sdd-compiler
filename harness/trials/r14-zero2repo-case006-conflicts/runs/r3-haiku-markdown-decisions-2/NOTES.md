# Implementation notes

Optlyn is built from `spec/` as a pure-Python library in `src/optlyn`
(no runtime dependencies, Python 3.10+). `pyproject.toml` describes the
src-layout PEP 517 build; the hidden tests import from `src` via `PYTHONPATH`.

## Spec conflicts and how they were resolved

### Decided by `spec/DECISIONS.md` (implemented as written)

1. **Isolated filesystem** (`CliRunner.isolated_filesystem`) never removes its
   directory, even without a parent (PRD FP-14 said it would; DECISIONS wins).
2. **Deprecation warnings:** a deprecated *command* warns on standard output,
   before its own output. Deprecated *option* and *argument* warnings go to
   standard error. Option and argument warnings only fire when the user supplied
   the parameter.
3. **Value order:** command line, then default map, then environment, then
   declared default. (The PRD's prompt rule still applies: a prompt shows the
   default-map value as its default, and an environment value skips a prompt
   that would otherwise run.)
4. **Standalone confirm:** `y`/`yes` is yes, `n`/`no` is no, empty takes the
   default, and any other answer counts as no. It is not asked again.

### Conflicts within the spec that I resolved

5. **Help width versus wrap width.** FP-02 sets the help page's maximum content
   width to 80 columns, while FP-11 says help and wrapped text use 100. I used
   80 for help pages (`max_content_width` default, caps auto-detected width) and
   100 as the default width of `wrap_text`. An explicit `terminal_width` is used
   as-is.
6. **Callback on an omitted parameter.** The terminology says a callback is not
   called for an omitted parameter with no value from any source. FP-03 says a
   missing parameter still runs its callback. I used: the callback runs when the
   parameter has a declared default (including an explicit `default=None`);
   without any declared default and no source, it is not called and the value is
   `None` (or `()` for repeatable/variadic).
7. **`Context.invoke(command, ...)`.** FP-07 says invoke supplies "exactly the
   caller's chosen values". I fill any missing declared parameters with their
   default (or `None`) so the target callback can run; `forward` passes the
   current values.
8. **Feature-switch groups** (several options sharing one destination): an
   explicit declared default beats an auto-derived one (a bare flag's implicit
   `False`); remaining ties go to the last declared option. Command-line
   occurrences: the later one wins.
9. **Flags with `flag_value`.** `flag_value=` without `is_flag=` makes a flag (as
   in Click). An optional-value option needs `is_flag=False` with `flag_value=`:
   the bare flag yields `flag_value`, a following token yields that token, and
   omitting it yields the default. A flag's presence yields `flag_value` (default
   `True`), whatever its default.
10. **Chaining group.** `ctx.invoked_subcommand` is `"*"` while chained children
    run.
11. **Author exit in non-standalone mode.** `main(standalone_mode=False)` returns
    the exit code given to `ctx.exit(n)` (0 by default) instead of raising.

### Choices where the spec leaves the form open

- **Completion protocol.** Suggestions are one line each: `type,value`, with an
  optional tab and help text. `type` is `plain`, `file`, or `dir` (path
  requests carry the incomplete token). Scripts exist for bash, zsh, fish, and
  PowerShell. An unrecognised instruction prints nothing and exits 1; a valid
  one exits 0.
- **Completion variable.** Derived from the program name exactly as the spec
  says (`_<NAME>_COMPLETE`, dashes to underscores). A name containing a dot
  (e.g. `app.py`) therefore gets `_APP.PY_COMPLETE`.
- **Exception names.** `OptlynError`, `UsageError`, `BadParameter`,
  `MissingParameter`, `NoSuchOption`, `BadOptionUsage`, `BadArgumentUsage`,
  `NoArgsIsHelpError`, `FileError`, `Abort`, `Exit`. Exit statuses: 0 success,
  1 abort or general error, 2 usage error.
- **Parameter identity in errors.** Options show all declared names (e.g.
  `'--shout' / '--no-shout'`); arguments show their name in uppercase.
- **Chain and group error messages.** `Missing command.` (exit 2, no help page)
  for a group with no subcommand when `no_args_is_help` is off; `No such command
  'x'.` for an unknown name.
- **Pager.** Uses `$PAGER`, or `less` when unset. Non-interactive sessions write
  straight to standard output.
- **`edit`.** Returns `None` when the text is unchanged and `require_save` is set.
- **`launch`.** Uses `xdg-open` on Linux, `open` on macOS, `os.startfile` on
  Windows. Returns 0 when started, 127 when no opener exists.
- **`getchar`.** Reads from `/dev/tty` when it can be opened, otherwise from
  standard input.
- **Runner capture.** `capture="fd"` captures OS-level writes to descriptors
  1 and 2. `Result.output` lists standard output then standard error, since their
  relative write order is not recorded at the descriptor level.

## Known gaps

- The Windows-specific paths (`msvcrt`, `os.startfile`, the PowerShell script)
  are written but were not run; only Linux was exercised.
- Completion of option values is offered only when the immediately preceding
  token is a value-taking option; the argument position is approximated from the
  count of positional tokens.
- Progress bars render a simple bar and ETA; they do not implement Click-style
  item display callbacks.
- Help layout uses `len()` for column widths, so wide Unicode characters may
  misalign.
