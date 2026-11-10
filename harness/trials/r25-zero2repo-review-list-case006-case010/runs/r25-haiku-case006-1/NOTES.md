# Implementation notes

Package: `src/optlyn` (import `optlyn`, `PYTHONPATH=src`). Pure Python, no runtime dependencies, Python 3.10+.

Where the specification disagrees with itself, I picked one side per point. Each entry gives both sides with their location, then what was built. Section numbers refer to `spec/Interface_Contract.md`; `FP-xx` refers to `spec/Full_PRD.md`.

## Conflicts and decisions

### C-01 Form feed in a docstring
- **PRD, FP-02 "Normal behavior" (line 102):** "A form-feed character in the docstring truncates the help: text after that character is omitted from the help page; text before it remains."
- **Contract §3 `command`, `attrs`:** "`help` ... a form-feed character in it is dropped and the text after it is kept."
- **Built:** the PRD. Text from the form feed onward is removed, and the form feed itself is not shown (`formatting.truncate_at_formfeed`, used by `Command._clean_help`).

### C-02 Short help for subcommands on a group page
- **PRD, FP-02 (line 104):** "the short help is the first sentence of the docstring by default, ellipsized if it cannot fit on one line at the wrap width."
- **Contract §2 "Help page" item 5:** "by default the start of the child's first paragraph, cut with `...` at 45 characters."
- **Built:** the first sentence of the docstring, cut with `...` at 45 characters. This keeps the PRD's first-sentence rule and the Contract's 45-character limit. The two limits are not combined into one rule.

### C-03 Epilog position
- **PRD, FP-02 (line 105):** "The epilog is printed at the end of the help page, after everything else on it."
- **Contract §3 `command`, `attrs`:** "`epilog` (printed right after the description, before the options)."
- **Built:** the PRD. The epilog is the last thing on the help page.

### C-04 Default maximum content width
- **PRD, FP-02 (line 107):** "a maximum content width that defaults to 80 columns."
- **PRD, FP-11 (line 340):** "Help pages and wrapped text use a maximum content width of 100 columns unless the caller sets another."
- **Built:** help pages cap auto-detected width at 80 (`Context.max_content_width` defaults to 80). `formatting.wrap_text` defaults to 100 for other wrapped text, as FP-11 says.

### C-05 Default metavar rule versus its example
- **PRD, FP-02 (line 108):** the default metavar is the uppercased type name, "for example, an integer option `--count` appears on the help page as `--count COUNT`."
- **Built:** the rule. An integer option shows `INTEGER` (the uppercased type name). The example's `COUNT` is not used, because the rule and the example cannot both hold.

### C-06 Showing a default of `False` on a boolean flag
- **PRD, FP-02 (line 110):** "For a single-option boolean flag whose default is off (false), that default remains hidden even if show-default is on."
- **Contract §4 `option`, `show_default`:** "when on, the default is shown for every option, a flag whose default is `False` included."
- **Built:** the PRD. A flag whose default is false never shows `[default: False]`, even with show-default on.

### C-07 Value of a counting option when omitted
- **PRD, FP-03 (line 137):** "A counting option yields how many times it occurred (zero if omitted)."
- **Contract §4 "Delivered values":** "counting option | an `int`, or `None` when the option was omitted."
- **Built:** the PRD. An omitted counting option delivers `0`.

### C-08 Which environment variable wins when several are listed
- **PRD, FP-03 (line 141):** "an option may name one variable or a list of names (first one set wins)."
- **Contract §4 `option`, `envvar`:** "with a list, the last name that is set wins."
- **Built:** the PRD. The first listed name that is set and non-empty wins.

### C-09 Unrecognised environment value for a boolean flag
- **PRD, FP-03 (line 142):** "Any other non-empty string is a conversion usage error, not a silent deactivation."
- **PRD, FP-05 "Boolean" (line 192):** "For a boolean flag read from an environment variable, any other value turns the flag off."
- **Built:** the FP-03 rule, which is the more specific of the two. An unrecognised non-empty value is a usage error. A flag with a non-boolean flag-value treats unrecognised text as unset, as FP-03 also says.

### C-10 Prompt when a non-required prompting option is fully omitted
- **PRD, FP-08 (line 268):** "An option with prompting enabled, if not supplied on the command line, reads a line from the user."
- **PRD, FP-08 (line 269):** "the option does not prompt when fully omitted; it prompts when the flag is present without a value."
- **Built:** the second line, which is the more specific rule. A prompting option that is fully omitted does not prompt unless it is required (or `prompt_required=True` is passed explicitly). Presence without a value always prompts.

### C-11 Mismatched confirmation entries
- **PRD, FP-08 (line 272):** "A confirmation prompt ... asks twice and rejects a mismatch by asking the pair again."
- **PRD, FP-13 (line 381):** "two different values typed into a confirmation prompt ... yields ... abort-class exit (1)."
- **Built:** re-ask (FP-08). The pair is asked again on a mismatch. An abort happens only if input ends during the re-ask (end-of-file is an abort, FP-08).

### C-12 Re-asking after a conversion failure at a prompt
- **PRD, FP-08 (line 274):** "Prompts re-ask on conversion failure until a valid value is given or the input stream ends."
- **PRD, FP-13 (line 380):** "conversion failure (including a value typed at a prompt, which is not asked again)."
- **Built:** re-ask (FP-08). A prompt re-asks until a valid value arrives or input ends.

### C-13 Date-time format precedence
- **PRD, FP-05 "Date-time" (line 195):** "Formats are tried in order; the first success wins."
- **Contract §5 `DateTime(formats=None)`:** "When several formats match a value, the last matching format is used."
- **Built:** the PRD. The first matching format is used. The default formats are mutually exclusive in practice, so this only matters for author formats.

### C-14 Whether an author date-time format list extends the defaults
- **PRD, "Public surface inventory" (line 40):** "an author's date-time format list is added to the default formats."
- **PRD, FP-05 "Date-time" (line 195):** "Authors may supply their own list of format strings, which replaces the default list (it does not extend it)."
- **Built:** replacement (FP-05, the detailed rule). An author list replaces the defaults.

### C-15 Case sensitivity default for enumeration choices
- **Contract §5 `Choice` row:** "`Choice(choices, case_sensitive=True)` ... (members are matched by name; by default the match ignores letter case)."
- **PRD, FP-05 "Choice" (line 194):** "Matching is case-sensitive unless the author turns that off."
- **Built:** `case_sensitive=True` as the default, for enumerations too, consistent with the signature and the PRD. Enum members are matched by name.

### C-16 Clamping an integer range at an open bound
- **PRD, FP-05 "Integer range" (line 196):** "a value equal to an open bound ... is replaced by ... the adjacent integer inside the range for an open bound."
- **Contract §5 `IntRange`:** "with `clamp=True`, a value beyond an open bound becomes that bound's value."
- **Built:** the PRD. An open bound clamps to the adjacent integer inside the range.

### C-17 Clamping a float range with an open bound
- **PRD, FP-05 "Float range" (line 197):** "Clamp is only allowed when both bounds are closed."
- **PRD, FP-05 "Boundary" (line 208):** "Float range refuses clamp when a bound is open (declaration error)."
- **Contract §5 `FloatRange`:** "With `clamp=True` and an open bound, a value beyond that bound becomes the bound."
- **Built:** the PRD. `FloatRange(..., clamp=True)` with an open bound raises `DeclarationError` at construction.

### C-18 Tilde expansion with `resolve_path`
- **PRD, FP-09 (line 292):** "resolve to an absolute path (symlinks resolved to their real target; a leading tilde is not expanded)."
- **Contract §5 `Path`:** "With `resolve_path=True`, a leading `~` is first expanded to the home directory."
- **Built:** the PRD. `resolve_path=True` resolves symlinks and makes the path absolute, but does not expand `~`.

### C-19 Application config directory on Unix
- **PRD, FP-11 (line 339):** "On Unix ... (`$XDG_CONFIG_HOME` when that variable is set, otherwise `.config` in the home directory)."
- **Contract §7 `get_app_dir`:** "On Unix the directory is always under `~/.config`."
- **Built:** the PRD. `$XDG_CONFIG_HOME` is used when set.

### C-20 Option suggestions for an empty completion token
- **PRD, FP-12 (line 358):** "Options are listed only once at least a dash has been typed."
- **Contract §8 "Inputs in complete mode":** "the suggestions for an empty token are the subcommand names followed by the option names."
- **Built:** the PRD. For an empty token, only subcommand names are offered. Option names appear once the token starts with `-`.

### C-21 Interactive session with piped stdin and a terminal stdout
- **PRD, Terminology "Interactive session" (line 32):** "A run whose standard input is attached to a terminal (PTY), or whose standard input or standard output is a TTY. A piped standard input without a terminal is not interactive."
- **Built:** a run is interactive when stdin or stdout is a TTY (`termui.is_interactive`). This follows the "or" clause. Piped stdin with a TTY stdout therefore counts as interactive, and the last sentence is not applied to that case.

### C-22 Whether a callback runs for an omitted parameter
- **PRD, Terminology "Callback" (line 28):** "A parameter callback is not called for a parameter that was omitted and received no value from any source."
- **PRD, FP-03 (line 145):** "A missing parameter still runs its callback, so that callback can default from an earlier parameter's value."
- **Built:** FP-03. The callback runs for an omitted parameter, with the empty value (`None`, `()`, `0`, or `False`).

### C-23 Source ranking of the default map versus the environment
- **PRD, FP-03 (line 143):** "A value is filled from command line, then environment, then the default map ... the first of those that produces a value wins."
- **Contract §6 `Context`, `default_map`:** "its values take precedence over environment variables."
- **Built:** the PRD ranking. Command line, then environment, then default map, then declared default.

### C-24 No-subcommand help for a group given only options
- **PRD, FP-06 (line 234):** a group invocation that leaves no subcommand name, "group options or arguments only", "report[s] a missing or unknown command on standard error; they do not use the no-arguments help page."
- **PRD, FP-02 (line 118) and FP-13 (line 380):** a group invoked with no subcommand under no-args-is-help shows the help page with the usage exit.
- **Built:** the two cases are split. With no arguments at all, the help page is printed on stderr and the exit status is 2 (no-args-is-help). With options or arguments but no subcommand, the message "Missing command." goes to stderr and the exit status is 2, with no help page.

### C-25 Removal of the isolated working directory
- **PRD, FP-14 (line 403):** "When no parent is given, the runner removes that directory on exit ... The new directory is always left in place after the block ends."
- **Built:** the first clause. Without a parent the directory is removed on exit. With a parent it is created under that parent and left in place.

## Not implemented or approximate

- `CliRunner(capture="fd")` is accepted but behaves like `capture="sys"`. OS-level descriptor capture is not implemented.
- `CliRunner(echo_stdin=...)` is accepted but not wired to anything. Visible prompt lines are still echoed to captured output, as FP-14 requires.
- `get_app_dir(roaming=...)` is accepted and ignored.
- Shell completion scripts for zsh, fish and PowerShell are minimal. Bash and the complete modes were checked by hand. Path completion is emitted as the sentinel lines `__optlyn_path_file__` / `__optlyn_path_dir__`, which is allowed because the form is the implementer's choice.
- Progress bars are simple: a single-line text bar, with no remaining-time estimate.
- Pager output uses `PAGER` (default `less`) when interactive; no pager behaviour was tested.
- `edit()` and `launch()` depend on `$EDITOR` / `xdg-open` being present; they were not exercised in tests.
- The `help_option` decorator and the automatic `--help` both print help and exit 0; if the automatic help option is dropped (author declares every help name), the author's option wins, as FP-02 requires.
