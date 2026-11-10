# Implementation notes

This project implements **Optlyn** under `src/optlyn/`, from the specification in `spec/`.
The spec itself is unchanged.

## Resolution rule

Where the specification disagrees with itself, the rule is:

- The **PRD** (`spec/Full_PRD.md`) defines behaviour. The Contract says so itself
  ("What the library does with those inputs ... is stated in the PRD").
- The **Interface Contract** (`spec/Interface_Contract.md`) defines names, signatures and the
  shape of output where the PRD does not fix them.
- When two PRD statements disagree, the more specific statement (the one closer to the feature
  it describes, or the one that spells out a detail) wins.

Each entry below quotes both sides, then states what was built. Entries marked **C-nn** are
listed in `spec/CONFLICTS.md`. Entries marked **X-nn** are disagreements I found that
`CONFLICTS.md` does not list.

---

## C-01 Form feed in a docstring

- PRD FP-02 (l.102): "A form-feed character in the docstring truncates the help: text after that character is omitted from the page."
- Contract §3 `command`, `help`: "a form-feed character in it is dropped and the text after it is kept."

**Built:** PRD. The text from the form feed onward is omitted; the form feed itself does not appear.

## C-02 Short help for subcommands on a group page

- PRD FP-02 (l.104): "the short help is the first sentence of the docstring by default, ellipsized if it cannot fit on one line at the wrap width."
- Contract §2 item 5: "by default the start of the child's first paragraph, cut with `...` at 45 characters."

**Built:** PRD. The first sentence of the first paragraph is used; it is cut with `...` to the space left on the line (see `formatting.make_default_short_help`). The fixed 45-character cut is not used.

## C-03 Epilog position

- PRD FP-02 (l.105): "The epilog is printed at the end of the help page, after everything else on it."
- Contract §3 `command`, `epilog`: "printed right after the description, before the options."

**Built:** PRD, and also Contract §2 item 6, which lists the epilog last. The epilog comes last.

## C-04 Default maximum content width

- PRD FP-02 (l.107): "a maximum content width that defaults to 80 columns."
- PRD FP-11 (l.340): "Help pages and wrapped text use a maximum content width of 100 columns unless the caller sets another."

**Built:** Help pages cap at 80 columns (`Context.max_content_width` defaults to 80). The `wrap_text` helper caps detected width at 100 columns, which FP-11 names for wrapped text. An explicit `terminal_width` setting is used as-is.

## C-05 Default metavar rule versus its own example

- PRD FP-02 (l.108): "the default metavar is the type name in uppercase ... for example, an integer option `--count` appears on the help page as `--count COUNT`."

**Built:** The rule. The integer type's name is `integer`, so the metavar is `INTEGER` (`--count INTEGER`). The example's `COUNT` is the destination name, not the type name, so it is not used.

## C-06 Showing a default of `False` on a boolean flag

- PRD FP-02 (l.110): "For a single-option boolean flag whose default is off (false), that default remains hidden even if show-default is on."
- Contract §4 `option`, `show_default`: "a flag whose default is `False` included."

**Built:** PRD. A flag whose default is `False` shows no default even when show-default is on.

## C-07 Value of a counting option when omitted

- PRD FP-03 (l.137): "A counting option yields how many times it occurred (zero if omitted)."
- Contract §4 table: "counting option | an `int`, or `None` when the option was omitted."

**Built:** PRD. An omitted counting option delivers `0`.

## C-08 Which environment variable wins when several are listed

- PRD FP-03 (l.141): "an option may name one variable or a list of names (first one set wins)."
- Contract §4 `option`, `envvar`: "with a list, the last name that is set wins."

**Built:** PRD. The first listed name that is set (and non-empty) wins.

## C-09 Unrecognised environment value for a boolean flag

- PRD FP-03 (l.142): "Any other non-empty string is a conversion usage error, not a silent deactivation."
- PRD FP-05 (l.192): "For a boolean flag read from an environment variable, any other value turns the flag off."

**Built:** FP-03. An unrecognised non-empty value for a boolean flag is a usage error (exit 2) that names the variable and the option. Flags whose flag value is not a boolean keep the FP-03 rule that unrecognised values are unset.

## C-10 Prompt when a non-required prompting option is fully omitted

- PRD FP-08 (l.268): "An option with prompting enabled, if not supplied on the command line, reads a line from the user."
- PRD FP-08 (l.269): "If the author does not require a prompt merely because the option was omitted, the option does not prompt when fully omitted; it prompts when the flag is present without a value."

**Built:** Both statements, read through the Contract keyword `prompt_required`. The default is `prompt_required=True`, so an omitted prompting option prompts. With `prompt_required=False` an omitted option does not prompt, but a bare flag (present without a value) still does. A required prompting option prompts whether or not it was omitted. A value from the environment skips the prompt (FP-08 l.270).

## C-11 Mismatched confirmation entries

- PRD FP-08 (l.272): "A confirmation prompt ... asks twice and rejects a mismatch by asking the pair again; mismatched values are not delivered."
- PRD FP-13 (l.381): "Abort — ... two different values typed into a confirmation prompt ... yields ... abort-class exit (**1**)."

**Built:** FP-08. A mismatch prints an error and asks the pair again. End of input during a prompt aborts (exit 1).

## C-12 Re-asking after a conversion failure at a prompt

- PRD FP-08 (l.274): "Prompts re-ask on conversion failure until a valid value is given or the input stream ends."
- PRD FP-13 (l.380): "conversion failure (including a value typed at a prompt, which is not asked again)."

**Built:** FP-08. A prompt re-asks on conversion failure.

## C-13 Date-time format precedence

- PRD FP-05 (l.195): "Formats are tried in order; the first success wins."
- Contract §5 `DateTime`: "When several formats match a value, the last matching format is used."

**Built:** PRD. The first format that parses the value wins.

## C-14 Whether an author date-time format list extends the defaults

- PRD "Public surface inventory" (l.40): "an author's date-time format list is added to the default formats."
- PRD FP-05 (l.195): "Authors may supply their own list of format strings, which replaces the default list (it does not extend it)."

**Built:** FP-05. An author list replaces the defaults.

## C-15 Case sensitivity default for enumeration choices

- Contract §5 `Choice`: "`Choice(choices, case_sensitive=True)` ... (members are matched by name; by default the match ignores letter case)."
- PRD FP-05 (l.194): "Matching is case-sensitive unless the author turns that off."

**Built:** `case_sensitive=True` by default, for enumerations too. The signature and the PRD agree on that default; the parenthetical in the Contract is ignored.

## C-16 Clamping an integer range at an open bound

- PRD FP-05 (l.196): "a value outside the range (including a value equal to an open bound) is replaced by ... the adjacent integer inside the range for an open bound."
- Contract §5 `IntRange`: "with `clamp=True`, a value beyond an open bound becomes that bound's value."

**Built:** PRD. With an open bound, the clamped value is the adjacent integer inside the range (`min+1` or `max-1`). The bound itself is excluded, so it cannot be the clamped value.

## C-17 Clamping a float range with an open bound

- PRD FP-05 (l.197): "Clamp is only allowed when both bounds are closed."
- PRD FP-05 (l.208): "Float range refuses clamp when a bound is open (declaration error)."
- Contract §5 `FloatRange`: "With `clamp=True` and an open bound, a value beyond that bound becomes the bound."

**Built:** PRD. `FloatRange(..., clamp=True)` with any open bound raises `ValueError` at construction.

## C-18 Tilde expansion with `resolve_path`

- PRD FP-09 (l.292): "resolve to an absolute path (symlinks resolved to their real target; a leading tilde is not expanded)."
- Contract §5 `Path`: "With `resolve_path=True`, a leading `~` is first expanded to the home directory."

**Built:** PRD. `resolve_path=True` makes the path absolute and resolves symlinks. A leading `~` is not expanded.

## C-19 Application config directory on Unix

- PRD FP-11 (l.339): "On Unix ... (`$XDG_CONFIG_HOME` when that variable is set, otherwise `.config` in the home directory)."
- Contract §7 `get_app_dir`: "On Unix the directory is always under `~/.config`."

**Built:** PRD. `XDG_CONFIG_HOME` is honoured when it is set. `force_posix=True` uses `~/.<folder>` regardless.

## C-20 Option suggestions for an empty completion token

- PRD FP-12 (l.358): "Options are listed only once at least a dash has been typed."
- Contract §8: "the suggestions for an empty token are the subcommand names followed by the option names."

**Built:** PRD. For an empty token only subcommand names (and argument values) are suggested. Option names need a leading dash.

## C-21 Interactive session with piped stdin and a terminal stdout

- PRD Terminology (l.32): "A run whose standard input is attached to a terminal (PTY), or whose standard input or standard output is a TTY. A piped standard input without a terminal is not interactive."

**Built:** A session is interactive when stdin **or** stdout is a terminal. This follows the first clause. A pipe with no terminal on either side is not interactive.

## C-22 Whether a callback runs for an omitted parameter

- PRD Terminology (l.28): "A parameter callback is not called for a parameter that was omitted and received no value from any source."
- PRD FP-03 (l.145): "A missing parameter still runs its callback, so that callback can default from an earlier parameter's value."

**Built:** FP-03. Callbacks run for omitted parameters too, with the value `None` (or `()` for repeatable and variadic parameters). This is what makes "default from an earlier parameter" possible.

## C-23 Source ranking of the default map versus the environment

- PRD FP-03 (l.143): "A value is filled from command line, then environment, then the default map ... the first of those that produces a value wins."
- Contract §6 `Context`, `default_map`: "its values take precedence over environment variables."

**Built:** PRD. The environment is consulted before the default map. The ranking is prompt, command line, environment, default map, declared default.

## C-24 No-subcommand help for a group given only options

- PRD FP-06 (l.234): "a parsed invocation that leaves no subcommand name (group options or arguments only) ... report a missing or unknown command on standard error; they do not use the no-arguments help page."
- PRD FP-02 (l.118) and FP-13 (l.380): help is shown when a group is invoked with no subcommand under the default policy.

**Built:** Both, split by what was typed. With **no arguments at all**, the default no-args-is-help policy shows the help page on stderr and exits 2. With **options only** (no subcommand name), the result is `Error: Missing command.` on stderr and exit 2, with no help page.

## C-25 Removal of the isolated working directory

- PRD FP-14 (l.403): "When no parent is given, the runner removes that directory on exit."
- PRD FP-14 (l.403), same bullet: "The new directory is always left in place after the block ends, so its files can still be inspected."

**Built:** The first sentence. With no parent, `CliRunner.isolated_filesystem()` removes the directory on exit. With a parent, the directory is created under it and left in place. The "always" sentence is treated as the error, because the first sentence is the specific one.

---

## Further disagreements (not in CONFLICTS.md)

### X-01 Omitted repeatable option with no default

- PRD FP-01 (l.84): "A repeatable option that was omitted and has no default is passed as an absent value."
- PRD FP-03 (l.138): "If it is omitted and has no default, the callback receives an empty tuple, not an absent value."
- Contract §4 "Delivered values": "omitted variadic argument or repeatable option | `()`."

**Built:** FP-03 and the Contract. The callback receives `()`.

### X-02 Pause when not interactive

- PRD FP-11 (l.335): "Pause prints a short message and waits for a key when the session is interactive; when not interactive it does nothing and does not block."
- PRD FP-11 boundary (l.346): "Pause must not block in non-interactive runs; it still prints its message there."

**Built:** The boundary statement. The message is printed in non-interactive runs, and nothing blocks.

### X-03 Chaining with standalone mode off and a result callback

- PRD FP-10 (l.312): "With standalone mode off, invoking a chaining group returns the list of the dispatched subcommands' return values in command-line order, whether or not a result callback is registered."
- PRD FP-10 (l.311): "The group's result callback ... runs after the chain."

**Built:** Both. The result callback runs, and the call still returns the list of subcommand return values.

### X-04 Prompt default and confirmation

- PRD FP-08 (l.270): "A declared default (static or callable) and a default-map value still prompt ... used if the user answers with an empty line."

**Built:** The prompt shows the default and accepts an empty answer as the default. The empty-answer path does not ask for confirmation a second time. Confirmation applies only to non-empty answers.

---

## Implementation layout

- `src/optlyn/core.py`: `Context`, `Parameter`/`Option`/`Argument`, the argument parser, `Command`/`Group`/`CommandCollection`, and the decorators.
- `src/optlyn/paramtypes.py`: parameter types (`STRING`, `INT`, `Choice`, `File`, `Path`, ...). Named `paramtypes` so that it does not shadow the standard-library `types`.
- `src/optlyn/termui.py`: echo, style, prompt, confirm, progress bar, pager, getchar, pause, clear, edit, launch.
- `src/optlyn/utils.py`: file opening (including lazy and atomic writes), `format_filename`, `get_app_dir`.
- `src/optlyn/formatting.py`: help layout and `wrap_text`.
- `src/optlyn/shell_completion.py`: registration scripts and suggestion output for bash, zsh, fish and PowerShell.
- `src/optlyn/testing.py`: `CliRunner` (sys and fd capture) and `Result`.
- `src/optlyn/exceptions.py`: usage (2), abort (1), file (1) and exit classes.
- `tests/test_optlyn.py`: regression tests for the behaviour above.

## Known gaps

- `launch()` runs `xdg-open` (Linux), `open` (macOS) or `os.startfile` (Windows); whether a window appears depends on the desktop session.
- Shell completion scripts have been checked by reading and by running the suggestion mode. They have not been exercised in a real bash, zsh, fish or PowerShell session.
- The pager uses only the `PAGER` environment variable. With no `PAGER` set, output is written directly.
- Windows-specific argument expansion (glob and environment tokens) is not implemented; the code paths for Windows are untested.
