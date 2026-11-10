# Notes

Implementation notes for Optlyn. The specification lives in `spec/` and was not modified.

Where the PRD (`spec/Full_PRD.md`, cited as FP-xx) and the Interface Contract (`spec/Interface_Contract.md`, cited as §) disagree, or where one part of the spec contradicts itself, the table below states both sides, where each side is, and what was built. The reviewer's list in `spec/CONFLICTS.md` (C-01 … C-25) is used as the identifier; each entry quotes the conflicting text.

## Spec conflicts and resolutions

### C-01 Form feed in a docstring
- **PRD, FP-02, Normal behavior (line 102):** "A form-feed character in the docstring truncates the help: text after that character is omitted from the help page."
- **Contract, §3 `command`, `attrs`:** "`help` (description text; a form-feed character in it is dropped and the text after it is kept)."
- **Built:** the PRD behavior. Text after the first form feed is removed (`formatting.clean_help`); the form feed itself is not shown.

### C-02 Short help for subcommands on a group page
- **PRD, FP-02, Normal behavior (line 104):** "the short help is the first sentence of the docstring by default, ellipsized if it cannot fit on one line at the wrap width."
- **Contract, §2 "Help page", item 5:** "by default the start of the child's first paragraph, cut with `...` at 45 characters."
- **Built:** both rules together. The first sentence is used, and it is cut with `...` at 45 characters (`formatting.short_help_text`).

### C-03 Epilog position
- **PRD, FP-02, Normal behavior (line 105):** "The epilog is printed at the end of the help page, after everything else on it."
- **Contract, §3 `command`, `attrs`:** "`epilog` (printed right after the description, before the options)."
- **Built:** the PRD position, at the end of the page.

### C-04 Default maximum content width
- **PRD, FP-02, Normal behavior (line 107):** "a maximum content width that defaults to 80 columns."
- **PRD, FP-11, Normal behavior (line 340):** "Help pages and wrapped text use a maximum content width of 100 columns unless the caller sets another."
- **Built:** help pages cap auto-detected width at 80 (`max_content_width` default). The standalone `wrap_text` helper defaults to 100. Those are two different surfaces, so they do not conflict in the code, but the help-page rule in FP-11 is not followed.

### C-05 Default metavar rule versus its own example
- **PRD, FP-02, Normal behavior (line 108):** "the default metavar is the type name in uppercase ... an integer option `--count` appears on the help page as `--count COUNT`."
- **Built:** the rule. The integer type's name is `integer`, so the metavar is `INTEGER`. The example's `COUNT` is not produced.

### C-06 Showing a default of `False` on a boolean flag
- **PRD, FP-02, Normal behavior (line 110):** "For a single-option boolean flag whose default is off (false), that default remains hidden even if show-default is on."
- **Contract, §4 `option`, `show_default`:** "when on, the default is shown for every option, a flag whose default is `False` included."
- **Built:** the PRD. A flag whose default is `False` shows no default, even with show-default on.

### C-07 Value of a counting option when omitted
- **PRD, FP-03, Normal behavior (line 137):** "A counting option yields how many times it occurred (zero if omitted)."
- **Contract, §4 "Delivered values":** "counting option | an `int`, or `None` when the option was omitted."
- **Built:** `0`, the PRD value.

### C-08 Which environment variable wins when several are listed
- **PRD, FP-03, Normal behavior (line 141):** "an option may name one variable or a list of names (first one set wins)."
- **Contract, §4 `option`, `envvar`:** "with a list, the last name that is set wins."
- **Built:** the first name that is set wins (PRD).

### C-09 Unrecognised environment value for a boolean flag
- **PRD, FP-03, Normal behavior (line 142):** "Any other non-empty string is a conversion usage error, not a silent deactivation."
- **PRD, FP-05, Built-in types, Boolean (line 192):** "For a boolean flag read from an environment variable, any other value turns the flag off."
- **Built:** the FP-03 rule. An unrecognised non-empty value is a usage error. A flag with a custom flag value treats an unrecognised value as unset, as FP-03 also says.

### C-10 Prompt when a non-required prompting option is fully omitted
- **PRD, FP-08, Normal behavior (line 268):** "An option with prompting enabled, if not supplied on the command line, reads a line from the user."
- **PRD, FP-08, Normal behavior (line 269):** "the option does not prompt when fully omitted; it prompts when the flag is present without a value."
- **Built:** the `prompt_required` keyword decides it. Its default is `True`, so an omitted prompting option asks. `prompt_required=False` means an omitted option does not ask, and a present-without-value option asks. A required prompting option asks when omitted (FP-08).

### C-11 Mismatched confirmation entries
- **PRD, FP-08, Normal behavior (line 272):** "A confirmation prompt ... asks twice and rejects a mismatch by asking the pair again; mismatched values are not delivered."
- **PRD, FP-13, Normal behavior (line 381):** "Abort — ... two different values typed into a confirmation prompt ... yields a non-zero abort-class exit (1)."
- **Built:** the FP-08 rule. A mismatch asks the pair again. An abort (exit 1) happens only when input ends during the prompt (FP-08 boundary rule).

### C-12 Re-asking after a conversion failure at a prompt
- **PRD, FP-08, Normal behavior (line 274):** "Prompts re-ask on conversion failure until a valid value is given or the input stream ends."
- **PRD, FP-13, Normal behavior (line 380):** "conversion failure (including a value typed at a prompt, which is not asked again)."
- **Built:** the FP-08 rule. A bad value is asked again.

### C-13 Date-time format precedence
- **PRD, FP-05, Built-in types, Date-time (line 195):** "Formats are tried in order; the first success wins."
- **Contract, §5 `DateTime(formats=None)`:** "When several formats match a value, the last matching format is used."
- **Built:** the first matching format wins (PRD). The result differs only when two formats both match one value.

### C-14 Whether an author date-time format list extends the defaults
- **PRD, Public surface inventory (line 40):** "an author's date-time format list is added to the default formats."
- **PRD, FP-05, Built-in types, Date-time (line 195):** "Authors may supply their own list of format strings, which replaces the default list (it does not extend it)."
- **Built:** replace. An author list replaces the defaults (`DateTime.__init__`).

### C-15 Case sensitivity default for enumeration choices
- **Contract, §5 `Choice` row:** "`Choice(choices, case_sensitive=True)` ... (members are matched by name; by default the match ignores letter case)."
- **PRD, FP-05, Built-in types, Choice (line 194):** "Matching is case-sensitive unless the author turns that off."
- **Built:** `case_sensitive=True` for every choice, including enumerations. Enumeration members match by name, case-sensitively by default.

### C-16 Clamping an integer range at an open bound
- **PRD, FP-05, Built-in types, Integer range (line 196):** "a value outside the range (including a value equal to an open bound) is replaced by ... the adjacent integer inside the range for an open bound."
- **Contract, §5 `IntRange`:** "with `clamp=True`, a value beyond an open bound becomes that bound's value."
- **Built:** the PRD. A clamped value at an open bound becomes the adjacent integer inside the range.

### C-17 Clamping a float range with an open bound
- **PRD, FP-05, Built-in types, Float range (line 197):** "Clamp is only allowed when both bounds are closed."
- **PRD, FP-05, Boundary (line 208):** "Float range refuses clamp when a bound is open (declaration error)."
- **Contract, §5 `FloatRange`:** "With `clamp=True` and an open bound, a value beyond that bound becomes the bound; any other invalid combination raises when constructed."
- **Built:** refused at construction (`FloatRange` raises `ValueError`), as both PRD statements say.

### C-18 Tilde expansion with `resolve_path`
- **PRD, FP-09, Normal behavior (line 292):** "resolve to an absolute path (symlinks resolved to their real target; a leading tilde is not expanded)."
- **Contract, §5 `Path`:** "With `resolve_path=True`, a leading `~` is first expanded to the home directory."
- **Built:** the contract. `resolve_path=True` expands a leading `~`. Without `resolve_path`, nothing is expanded.

### C-19 Application config directory on Unix
- **PRD, FP-11, Normal behavior (line 339):** "On Unix ... it sits under the user's config home (`$XDG_CONFIG_HOME` when that variable is set, otherwise `.config` in the home directory)."
- **Contract, §7 `get_app_dir`:** "On Unix the directory is always under `~/.config`."
- **Built:** the PRD. `$XDG_CONFIG_HOME` is used when set.

### C-20 Option suggestions for an empty completion token
- **PRD, FP-12, Normal behavior (line 358):** "Options are listed only once at least a dash has been typed."
- **Contract, §8 "Inputs in complete mode":** "the suggestions for an empty token are the subcommand names followed by the option names."
- **Built:** the PRD. An empty token gets subcommand names only.

### C-21 Interactive session with piped stdin and a terminal stdout
- **PRD, Terminology, "Interactive session" (line 32):** "A run whose standard input is attached to a terminal (PTY), or whose standard input or standard output is a TTY. A piped standard input without a terminal is not interactive."
- **Built:** a session is interactive when stdin or stdout is a TTY (the first clause). A piped stdin with a TTY stdout therefore counts as interactive. The last sentence is not applied to that case.

### C-22 Whether a callback runs for an omitted parameter
- **PRD, Terminology, "Callback" (line 28):** "A parameter callback is not called for a parameter that was omitted and received no value from any source."
- **PRD, FP-03, Normal behavior (line 145):** "A missing parameter still runs its callback, so that callback can default from an earlier parameter's value."
- **Built:** the FP-03 rule. Callbacks run for omitted parameters too, with `None` (or `()` for repeatable ones).

### C-23 Source ranking of the default map versus the environment
- **PRD, FP-03, Normal behavior (line 143):** "A value is filled from command line, then environment, then the default map ... the first of those that produces a value wins."
- **Contract, §6 `Context`, `default_map`:** "its values take precedence over environment variables."
- **Built:** the PRD ranking. The environment is consulted before the default map. The contract sentence is not followed.

### C-24 No-subcommand help for a group given only options
- **PRD, FP-06, Boundary (line 234):** a group given only options, with no subcommand, is "a usage error ... they do not use the no-arguments help page."
- **PRD, FP-13 (line 380)** and **FP-02 (line 118):** the no-arguments help page is shown for "group invoked with no subcommand".
- **Built:** a group invoked with no arguments at all shows its help page on stderr with exit 2 (`NoArgsHelp`). A group given options but no subcommand gives a "Missing command." usage error without a help page (`MissingCommand`).

### C-25 Removal of the isolated working directory
- **PRD, FP-14, Normal behavior (line 403):** "When no parent is given, the runner removes that directory on exit."
- **PRD, FP-14, same bullet:** "The new directory is always left in place after the block ends, so its files can still be inspected."
- **Built:** the first statement. With no `temp_dir`, the directory is removed on exit; with `temp_dir`, it is created under that path and left in place.

## Other choices

- Destination names: a prefixed option takes its destination from its first long name, otherwise its first short name, with the prefix stripped and dashes turned into underscores. `--verbose`/`-v` is `verbose`. A declaration without a prefix is taken as the destination itself.
- Eager flags (`--help`, `--version`) are handled in the order they are typed; the first one takes effect.
- Parameter callbacks run in declaration order, and each sees the values already bound through `ctx.params`.
- `count` values, flags, and feature-switch groups: the last occurrence on the command line wins.
- Group callback runs before the subcommand is parsed, so `group sub --help` runs the group callback and then shows the subcommand's help (FP-06).
- The auto environment prefix is `PREFIX_<SUBCOMMANDS>_<DEST>`, uppercased, with dashes turned into underscores. The top-level command name is not included.
- The completion variable is `_<PROG>_COMPLETE` with the program name uppercased and dashes turned into underscores, as the contract states. A program named `tool.py` therefore uses `_TOOL.PY_COMPLETE`.

## Known gaps

These parts of the spec are only partly implemented or not implemented:

- Options with an optional value (a flag alone yields one value, a flag with a token yields another).
- Mixing group options after the subcommand name (`allow_interspersed_args` on a group).
- Completion of file and path parameters (filesystem completion requests) and of zsh/fish help text.
- Pager, progress bar, and editor helpers are minimal. The progress bar draws a simple one-line bar. `launch` returns the process status.
- `get_app_dir(roaming=...)` ignores `roaming`.
- Custom deprecation notes are shown; deprecation marks appear on help pages.
