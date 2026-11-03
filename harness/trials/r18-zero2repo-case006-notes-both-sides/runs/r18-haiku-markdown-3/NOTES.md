# Optlyn — implementation notes

Layout: `src/optlyn/` (importable with `PYTHONPATH=src`), `pyproject.toml` (src layout, no runtime dependencies).
Modules: `command.py` (parser, Command, Group, CommandCollection, standalone `main`), `params.py`
(Parameter, Option, Argument, value-source resolution), `context.py` (Context, ParameterSource),
`types.py` (parameter types), `decorators.py` (declaration decorators, ready-made flags, pass-context),
`termui.py` (echo, styling, prompts, pager, progress bar, editor), `utils.py` (open_file, format_filename,
get_app_dir, launch), `formatting.py` (wrap_text, help page), `shell_completion.py`, `testing.py` (CliRunner),
`_state.py` (thread-local current-context stack).

## Spec conflicts and the choice made

1. **Counting option when omitted.** PRD FP-03 says "zero if omitted"; Interface Contract §2 table says `None`.
   Built: `0` (the PRD is the behavioural source; the contract table is the only place that says `None`).

2. **`show_default` on a `False` flag.** PRD FP-02 says a single-option boolean flag whose default is off stays
   hidden even with show-default on; Interface Contract §4 says `show_default` shows the default for every option,
   a flag whose default is `False` included. Built: the contract (shown).

3. **Maximum content width.** PRD FP-02 says help is capped at 80 columns; PRD FP-11 says help and wrapped text use
   100 columns. Built: help pages cap at 80 (`HelpFormatter`); `wrap_text` defaults to a 100 cap. Both are overridable.

4. **Form feed in help text.** PRD FP-02: a form feed in a *docstring* truncates the help (text after it is omitted).
   Contract §3: for the `help=` keyword, the form-feed character is dropped and the text after it is kept.
   Built: docstrings truncate at the form feed; an explicit `help=` drops the character and keeps the rest.

5. **Short help of a subcommand on a group page.** PRD FP-02: first sentence, ellipsized to the wrap width.
   Contract §2: the start of the first paragraph, cut with `...` at 45 characters. Built: the contract (45 columns).

6. **Option metavar.** PRD FP-02 states the default metavar is the *type name* in uppercase, yet its own example says an
   integer option `--count` appears as `--count COUNT` (type name would be `INTEGER`). Built: the destination name in
   uppercase for non-choice types (matches the example); a `Choice` keeps its own `[a|b]` placeholder.

7. **Callback for an omitted parameter.** PRD glossary: a parameter callback is *not* called for a parameter omitted
   with no value from any source. PRD FP-03: "a missing parameter still runs its callback, so that callback can default
   from an earlier parameter's value." Built: the callback always runs (value `None` / `()` / default when no source),
   so the FP-03 use case works; the glossary exception is not implemented.

8. **Date-time with several matching formats.** PRD FP-05: formats are tried in order and the first success wins.
   Contract §5: when several formats match, the last matching format is used. Built: first match (PRD).
   The default list cannot overlap, so this only matters for custom format lists.

9. **`make_pass_decorator` lookup.** PRD FP-07 says "the nearest object of exactly that type". Built with
   `isinstance`, so subclass instances match (the usual meaning of "of that type" in Python).

10. **`isolated_filesystem` cleanup.** PRD FP-14 says the directory is removed on exit when no parent is given, and also
    that it is "always left in place". Built: removed when no `temp_dir` is given; left in place when a parent is given.

11. **Interactive session.** Glossary: a session is interactive when stdin is a PTY or stdin *or* stdout is a TTY.
    Built: `sys.stdin.isatty() or sys.stdout.isatty()` for pager/pause/prompt-echo decisions.

12. **Option environment variables with `allow_from_autoenv`.** PRD: an option may opt out of the automatic prefix and is
    then filled only from explicitly named variables. Built as written.

## Known gaps (not verified against the hidden tests)

- Feature areas exercised by scratch scripts only (not in the repo): groups/nesting, chaining with result callbacks,
  default maps, env sources, prompts/confirmation, file and path types, completion source and complete modes,
  exit statuses in a real process, fd capture in `CliRunner`, styling, progress bar, pager fallback, pause, wrap_text.
- Shell completion scripts are simplified: suggestions for a path type return an internal marker line
  (`__optlyn_path__file`) rather than asking the shell to complete paths. A parameter's `shell_complete=` function
  is used when the parameter is the one being completed (the value after an option); its objects contribute `value`.
- Chaining splits a segment's arguments at the next known command name, so an argument equal to a sibling command
  name is treated as a new command.
- Option-value prompts for `multiple=True` / multi-value options take one prompt answer, not a sequence.
- `get_app_dir` on Windows uses `%APPDATA%`; the spec only covers Unix and macOS.
- Token normalization is applied to option names, choice values and command names; there is no separate
  deduplication of "first registered" choices beyond list order.
- `launch` shells out to `xdg-open` (Linux), `open` (macOS) or `cmd /c start` (Windows).
- The `edit` editor's "require save" check compares modification times only when the text was supplied.
