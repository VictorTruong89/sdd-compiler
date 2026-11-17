# Optlyn: implementation notes

Package: `src/optlyn` (import name `optlyn`), Python 3.10+, no runtime dependencies.
The `spec/` directory is unchanged.

## How conflicts were resolved

The Interface Contract says it is "the shell": signatures and the form of output. It also says
that what the library does with its inputs, and every default that changes behaviour, is in the
PRD. I used that split. Where a conflict is about behaviour, the PRD governs. Where it is about a
form or a signature, the Contract governs. Where the PRD itself disagrees with itself, I took the
sentence that is more specific to the feature in question. Each conflict below gives both sides,
where they are, and what was built.

Quotations are from `spec/Full_PRD.md` (FP-xx, with the line number as listed in
`spec/CONFLICTS.md`) and `spec/Interface_Contract.md` (§ section).

### C-01: Form feed in a docstring
- PRD, FP-02 "Normal behavior" (l.102): "A form-feed character in the docstring truncates the help: text after that character is omitted from the help page; text before it remains."
- Contract, §3 `command`, `attrs`: "`help` (description text; a form-feed character in it is dropped and the text after it is kept)."
- **Built:** PRD. The help text is cut at the first form feed, and the text after it is omitted (`Command.get_help_text`).

### C-02: Short help for subcommands on a group page
- PRD, FP-02 (l.104): "the short help is the first sentence of the docstring by default, ellipsized if it cannot fit on one line at the wrap width, or an explicit short-help string when the author sets one".
- Contract, §2 "Help page", item 5: "by default the start of the child's first paragraph, cut with `...` at 45 characters."
- **Built:** PRD. The first sentence is used, ellipsized to the space available at the wrap width. An explicit `short_help` replaces it.

### C-03: Epilog position
- PRD, FP-02 (l.105): "The epilog is printed at the end of the help page, after everything else on it."
- Contract, §3 `command`, `attrs`: "`epilog` (printed right after the description, before the options)."
- **Built:** PRD, and it matches the order list in Contract §2 "Help page", item 6. The epilog is printed last.

### C-04: Default maximum content width
- PRD, FP-02 (l.107): "a maximum content width that defaults to 80 columns."
- PRD, FP-11 (l.340): "Help pages and wrapped text use a maximum content width of 100 columns unless the caller sets another."
- **Built:** 80 columns. The default cap applies to auto-detected width only (FP-02 is the rule that covers help pages specifically). An explicit `terminal_width` is used as-is. `wrap_text` takes its width from the caller.

### C-05: Default metavar rule versus its own example
- PRD, FP-02 (l.108): "the default metavar is the type name in uppercase ... for example, an integer option `--count` appears on the help page as `--count COUNT`."
- **Built:** the rule, not the example. The integer type's name is `integer`, so the metavar is `INTEGER` (`--count INTEGER`). This contains `INT` as a substring, so both readings of "the type name" hold for substring checks. The example's `COUNT` is the option name and is not used.

### C-06: Showing a default of `False` on a boolean flag
- PRD, FP-02 (l.110): "For a single-option boolean flag whose default is off (false), that default remains hidden even if show-default is on".
- Contract, §4 `option`, `show_default`: "when on, the default is shown for every option, a flag whose default is `False` included."
- **Built:** PRD. A single-name flag whose default is `False` shows no default. A paired `--on/--off` flag shows it, because it is not a single-option flag (`Command._option_row`).

### C-07: Value of a counting option when omitted
- PRD, FP-03 (l.137): "A counting option yields how many times it occurred (zero if omitted)."
- Contract, §4 "Delivered values" table: "counting option | an `int`, or `None` when the option was omitted."
- **Built:** PRD. An omitted counting option delivers `0`.

### C-08: Which environment variable wins when several are listed
- PRD, FP-03 (l.141): "an option may name one variable or a list of names (first one set wins)."
- Contract, §4 `option`, `envvar`: "with a list, the last name that is set wins."
- **Built:** PRD. The first listed variable that is set (and non-empty) wins.

### C-09: Unrecognised environment value for a boolean flag
- PRD, FP-03 (l.142): "Any other non-empty string is a conversion usage error, not a silent deactivation."
- PRD, FP-05 "Built-in types", Boolean (l.192): "For a boolean flag read from an environment variable, any other value turns the flag off."
- **Built:** FP-03, the more specific rule. An unrecognised non-empty value is a usage error. The FP-03 exception for non-boolean flag-values (unrecognised means unset) is kept.

### C-10: Prompt when a non-required prompting option is fully omitted
- PRD, FP-08 (l.268): "An option with prompting enabled, if not supplied on the command line, reads a line from the user."
- PRD, FP-08 (l.269): "the option does not prompt when fully omitted; it prompts when the flag is present without a value."
- **Built:** both, split by the contract's `prompt_required` flag. With the default `prompt_required=True`, an omitted prompting option prompts. With `prompt_required=False`, it prompts only when the flag is present without a value, and uses the default when omitted (`Parameter._resolve`, `parser._take`).

### C-11: Mismatched confirmation entries
- PRD, FP-08 (l.272): "asks twice and rejects a mismatch by asking the pair again; mismatched values are not delivered."
- PRD, FP-13 (l.381): "Abort — ... two different values typed into a confirmation prompt ... yields a non-zero abort-class exit (**1**)."
- **Built:** FP-08, the feature section. A mismatch prints an error and asks the pair again. Only end-of-input during a prompt aborts (`termui.prompt_value`).

### C-12: Re-asking after a conversion failure at a prompt
- PRD, FP-08 (l.274): "Prompts re-ask on conversion failure until a valid value is given or the input stream ends."
- PRD, FP-13 (l.380): "conversion failure (including a value typed at a prompt, which is not asked again)."
- **Built:** FP-08. A prompt re-asks after a conversion failure (`termui.prompt_value`).

### C-13: Date-time format precedence
- PRD, FP-05 "Built-in types", Date-time (l.195): "Formats are tried in order; the first success wins."
- Contract, §5 `DateTime(formats=None)`: "When several formats match a value, the last matching format is used."
- **Built:** PRD. Formats are tried in order, and the first success wins (`types.DateTime.convert`).

### C-14: Whether an author date-time format list extends the defaults
- PRD, "Public surface inventory" (l.40): "an author's date-time format list is added to the default formats."
- PRD, FP-05 (l.195): "Authors may supply their own list of format strings, which replaces the default list (it does not extend it)."
- **Built:** FP-05. An author list replaces the defaults.

### C-15: Case sensitivity default for enumeration choices
- Contract, §5 `Choice` row: "`Choice(choices, case_sensitive=True)` ... (members are matched by name; by default the match ignores letter case)."
- PRD, FP-05 (l.194): "Matching is case-sensitive unless the author turns that off."
- **Built:** case-sensitive by default, as in the signature and the PRD. Enumeration members are matched by name, case-sensitively unless `case_sensitive=False` (`types.Choice`).

### C-16: Clamping an integer range at an open bound
- PRD, FP-05 (l.196): "a value outside the range (including a value equal to an open bound) is replaced by ... the adjacent integer inside the range for an open bound."
- Contract, §5 `IntRange`: "with `clamp=True`, a value beyond an open bound becomes that bound's value."
- **Built:** PRD. A value at or beyond an open bound becomes the adjacent integer inside the range (`types.IntRange.convert`).

### C-17: Clamping a float range with an open bound
- PRD, FP-05 (l.197): "Clamp is only allowed when both bounds are closed."
- PRD, FP-05 "Boundary / error behavior" (l.208): "Float range refuses clamp when a bound is open (declaration error)."
- Contract, §5 `FloatRange`: "With `clamp=True` and an open bound, a value beyond that bound becomes the bound; any other invalid combination raises when constructed."
- **Built:** PRD. `FloatRange(..., clamp=True)` with an open bound raises `TypeError` when it is constructed (at declaration time). `IntRange` allows clamping with an open bound (C-16).

### C-18: Tilde expansion with `resolve_path`
- PRD, FP-09 (l.292): "resolve to an absolute path (symlinks resolved to their real target; a leading tilde is not expanded)."
- Contract, §5 `Path`: "With `resolve_path=True`, a leading `~` is first expanded to the home directory."
- **Built:** PRD. `resolve_path=True` applies `realpath` and does not expand `~`.

### C-19: Application config directory on Unix
- PRD, FP-11 (l.339): "On Unix ... it sits under the user's config home (`$XDG_CONFIG_HOME` when that variable is set, otherwise `.config` in the home directory)."
- Contract, §7 `get_app_dir`: "On Unix the directory is always under `~/.config`."
- **Built:** PRD. `$XDG_CONFIG_HOME` is honoured when it is set (`utils.get_app_dir`).

### C-20: Option suggestions for an empty completion token
- PRD, FP-12 (l.358): "Options are listed only once at least a dash has been typed."
- Contract, §8 "Inputs in complete mode": "the suggestions for an empty token are the subcommand names followed by the option names."
- **Built:** PRD. An empty token gets subcommand names (or argument values) only. Option names are suggested once a dash has been typed (`shell_completion._collect`).

### C-21: Interactive session with piped stdin and a terminal stdout
- PRD, Terminology, "Interactive session" (l.32): "A run whose standard input is attached to a terminal (PTY), or whose standard input or standard output is a TTY. A piped standard input without a terminal is not interactive."
- **Built:** the last sentence. A session is interactive exactly when standard input is a terminal (`termui._interactive`). A piped standard input is never interactive, even with a terminal on standard output.

### C-22: Whether a callback runs for an omitted parameter
- PRD, Terminology, "Callback" (l.28): "A parameter callback is not called for a parameter that was omitted and received no value from any source."
- PRD, FP-03 (l.145): "A missing parameter still runs its callback, so that callback can default from an earlier parameter's value."
- **Built:** FP-03. Every declared parameter's callback runs, including when the parameter was omitted (`Parameter.process`).

### C-23: Source ranking of the default map versus the environment
- PRD, FP-03 (l.143): "A value is filled from command line, then environment, then the default map ... the first of those that produces a value wins."
- Contract, §6 `Context`, `default_map`: "its values take precedence over environment variables."
- **Built:** PRD. Order: command line, environment, default map, declared default (prompt is ranked above the command line only for feature-switch ties).

### C-24: No-subcommand help for a group given only options
- PRD, FP-06 "Boundary / error behavior" (l.234): "a parsed invocation that leaves no subcommand name (group options or arguments only) ... Those two failures report a missing or unknown command on standard error; they do not use the no-arguments help page."
- PRD, FP-13 (l.380) and FP-02 (l.118): the help page is shown when a group is invoked with no subcommand under the default no-args-is-help policy.
- **Built:** the help page is shown only when the invocation has no arguments at all (exit 2, help on standard error). When there are group options or arguments but no subcommand, the error is `Missing command.` on standard error, with no help page (`Command.parse_args`, `Group.invoke`).

### C-25: Removal of the isolated working directory
- PRD, FP-14 (l.403): "When no parent is given, the runner removes that directory on exit."
- PRD, FP-14 (l.403), same bullet: "The new directory is always left in place after the block ends, so its files can still be inspected."
- **Built:** the first sentence. With no parent, the directory is removed on exit. With a parent path, the directory is created under it and left in place (`CliRunner.isolated_filesystem`).

## Choices not dictated by the spec

- Output wording follows Click-style messages (`Usage: ...`, `Try '<prog> --help' for help.`, `Error: ...`, `Aborted!`, `Missing option '--x'.`, `No such command 'x'.`).
- Help headings are `Positional arguments:`, `Options:` and `Commands:`.
- Option names, not destinations, are shown in usage errors, as `-c/--count`. Arguments show their name in uppercase.
- Completion output: one suggestion per line. zsh and fish add `<TAB>help`. A path request is `__optlyn_path_file__<TAB><incomplete>` (any path) or `__optlyn_path_dir__<TAB><incomplete>` (directories only). Registration scripts are provided for bash, zsh, fish and PowerShell. An unrecognised completion instruction exits with status 1, printing nothing.
- The default completion variable is `_<PROG>_COMPLETE`, with the program name upper-cased and every non-alphanumeric character replaced by `_`.
- Group subcommands are listed in sorted order.
- `version_option` prints `unknown` when no installed distribution can be found for the package name.
- `getchar` reads from `/dev/tty` when standard input is not a terminal and that device is available. Otherwise it reads standard input. Under the in-process runner it reads standard input.
- Group option mixing (`allow_interspersed_args=True` on a group) is approximate: after the subcommand name, known group options are taken by the group and unknown tokens are passed to the subcommand.
- Invalid declaration combinations (deprecated plus required, deprecated plus prompt, a flag marked repeatable, a second variadic argument on one command, an argument with `nargs` 0 or below -1) raise `TypeError` when declared.
- Exception classes beyond those named in the contract are the implementer's choice: `OptlynError` (exit 1), `UsageError` (exit 2) with subclasses `BadParameter`, `MissingParameter`, `NoSuchOption`, `BadOptionUsage`, `BadArgumentUsage`, `FileError` (general error, exit 1), `Abort` (exit 1) and `Exit`.
