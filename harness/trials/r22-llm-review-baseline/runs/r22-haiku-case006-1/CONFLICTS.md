# Specification conflicts

Scope: `spec/Full_PRD.md` (PRD, cited as FP-xx and its sub-bullet), `spec/Interface_Contract.md` (Contract, cited by section §), and `spec/Hardware_Requirements.md` (no conflicts found there). Line numbers refer to the files as they are now.

Each entry gives both sides and one sentence explaining why they cannot both hold.

---

### C-01: Form feed in a docstring
- **PRD, FP-02 "Normal behavior" (l.102):** "A form-feed character in the docstring truncates the help: text after that character is omitted from the help page."
- **Contract, §3 `command`, `attrs`:** "`help` (description text; a form-feed character in it is dropped and the text after it is kept)."
- **Why:** For the same input, the text after a form feed is either omitted from the page or kept on it, not both.

### C-02: Short help for subcommands on a group page
- **PRD, FP-02 "Normal behavior" (l.104):** "the short help is the first sentence of the docstring by default, ellipsized if it cannot fit on one line at the wrap width."
- **Contract, §2 "Help page", item 5:** "by default the start of the child's first paragraph, cut with `...` at 45 characters."
- **Why:** The default cannot be both the first sentence cut at wrap width and the first paragraph cut at a fixed 45 characters.

### C-03: Epilog position
- **PRD, FP-02 "Normal behavior" (l.105):** "The epilog is printed at the end of the help page, after everything else on it."
- **Contract, §3 `command`, `attrs`:** "`epilog` (printed right after the description, before the options)."
- **Why:** An epilog cannot be both the last thing on the page and printed before the options.

### C-04: Default maximum content width
- **PRD, FP-02 "Normal behavior" (l.107):** "a maximum content width that defaults to 80 columns."
- **PRD, FP-11 "Normal behavior" (l.340):** "Help pages and wrapped text use a maximum content width of 100 columns unless the caller sets another."
- **Why:** With no caller setting, help pages cannot be capped at both 80 and 100 columns.

### C-05: Default metavar rule versus its own example
- **PRD, FP-02 "Normal behavior" (l.108):** "the default metavar is the type name in uppercase ... for example, an integer option `--count` appears on the help page as `--count COUNT`."
- **Why:** The uppercased type name of an integer is `INT` (or `INTEGER`), not `COUNT`, so the rule and its example contradict each other.

### C-06: Showing a default of `False` on a boolean flag
- **PRD, FP-02 "Normal behavior" (l.110):** "For a single-option boolean flag whose default is off (false), that default remains hidden even if show-default is on."
- **Contract, §4 `option`, `show_default`:** "when on, the default is shown for every option, a flag whose default is `False` included."
- **Why:** The default for such a flag is either hidden or shown when show-default is on, not both.

### C-07: Value of a counting option when omitted
- **PRD, FP-03 "Normal behavior" (l.137):** "A counting option yields how many times it occurred (zero if omitted)."
- **Contract, §4 "Delivered values" table:** "counting option | an `int`, or `None` when the option was omitted."
- **Why:** An omitted counting option delivers either `0` or `None`, not both.

### C-08: Which environment variable wins when several are listed
- **PRD, FP-03 "Normal behavior" (l.141):** "an option may name one variable or a list of names (first one set wins)."
- **Contract, §4 `option`, `envvar`:** "with a list, the last name that is set wins."
- **Why:** When two listed variables are both set, only the first or only the last can supply the value.

### C-09: Unrecognised environment value for a boolean flag
- **PRD, FP-03 "Normal behavior" (l.142):** "Any other non-empty string is a conversion usage error, not a silent deactivation."
- **PRD, FP-05 "Built-in types", Boolean (l.192):** "For a boolean flag read from an environment variable, any other value turns the flag off."
- **Why:** An unrecognised non-empty value for a boolean flag is either a usage error or a silent deactivation, not both.

### C-10: Prompt when a non-required prompting option is fully omitted
- **PRD, FP-08 "Normal behavior" (l.268):** "An option with prompting enabled, if not supplied on the command line, reads a line from the user."
- **PRD, FP-08 "Normal behavior" (l.269):** "the option does not prompt when fully omitted; it prompts when the flag is present without a value."
- **Why:** A fully omitted prompting option either reads a line from the user or does not prompt, and the spec states both.

### C-11: Mismatched confirmation entries
- **PRD, FP-08 "Normal behavior" (l.272):** "A confirmation prompt ... asks twice and rejects a mismatch by asking the pair again; mismatched values are not delivered."
- **PRD, FP-13 "Normal behavior" (l.381):** "Abort — ... two different values typed into a confirmation prompt ... yields a non-zero abort-class exit (**1**)."
- **Why:** Two different typed values either re-ask the pair and continue, or abort the program with exit 1.

### C-12: Re-asking after a conversion failure at a prompt
- **PRD, FP-08 "Normal behavior" (l.274):** "Prompts re-ask on conversion failure until a valid value is given or the input stream ends."
- **PRD, FP-13 "Normal behavior" (l.380):** "conversion failure (including a value typed at a prompt, which is not asked again)."
- **Why:** A value that fails conversion at a prompt is either asked again or not asked again.

### C-13: Date-time format precedence
- **PRD, FP-05 "Built-in types", Date-time (l.195):** "Formats are tried in order; the first success wins."
- **Contract, §5 `DateTime(formats=None)`:** "When several formats match a value, the last matching format is used."
- **Why:** When two formats both match a value, the spec picks either the first or the last of them, not both.

### C-14: Whether an author date-time format list extends the defaults
- **PRD, "Public surface inventory" (l.40):** "an author's date-time format list is added to the default formats."
- **PRD, FP-05 "Built-in types", Date-time (l.195):** "Authors may supply their own list of format strings, which replaces the default list (it does not extend it)."
- **Why:** A value matched only by a default format (such as `2026-11-09`) is accepted when the author list extends the defaults and refused when it replaces them, so both cannot hold.

### C-15: Case sensitivity default for enumeration choices
- **Contract, §5 `Choice` row:** "`Choice(choices, case_sensitive=True)` ... (members are matched by name; by default the match ignores letter case)."
- **PRD, FP-05 "Built-in types", Choice (l.194):** "Matching is case-sensitive unless the author turns that off."
- **Why:** The same row gives `case_sensitive=True` as the default and also says that enumeration matching ignores case by default.

### C-16: Clamping an integer range at an open bound
- **PRD, FP-05 "Built-in types", Integer range (l.196):** "a value outside the range (including a value equal to an open bound) is replaced by ... the adjacent integer inside the range for an open bound."
- **Contract, §5 `IntRange`:** "with `clamp=True`, a value beyond an open bound becomes that bound's value."
- **Why:** An open bound is replaced by the adjacent integer inside the range in one statement and by the bound's own value in the other.

### C-17: Clamping a float range with an open bound
- **PRD, FP-05 "Built-in types", Float range (l.197):** "Clamp is only allowed when both bounds are closed."
- **PRD, FP-05 "Boundary / error behavior" (l.208):** "Float range refuses clamp when a bound is open (declaration error)."
- **Contract, §5 `FloatRange`:** "With `clamp=True` and an open bound, a value beyond that bound becomes the bound; any other invalid combination raises when constructed."
- **Why:** A clamp with an open bound is either refused at declaration or accepted, not both.

### C-18: Tilde expansion with `resolve_path`
- **PRD, FP-09 "Normal behavior" (l.292):** "resolve to an absolute path (symlinks resolved to their real target; a leading tilde is not expanded)."
- **Contract, §5 `Path`:** "With `resolve_path=True`, a leading `~` is first expanded to the home directory."
- **Why:** With resolution turned on, a leading `~` is either expanded or left unexpanded.

### C-19: Application config directory on Unix
- **PRD, FP-11 "Normal behavior" (l.339):** "On Unix ... it sits under the user's config home (`$XDG_CONFIG_HOME` when that variable is set, otherwise `.config` in the home directory)."
- **Contract, §7 `get_app_dir`:** "On Unix the directory is always under `~/.config`."
- **Why:** When `XDG_CONFIG_HOME` is set, the directory is either under that path or always under `~/.config`, not both.

### C-20: Option suggestions for an empty completion token
- **PRD, FP-12 "Normal behavior" (l.358):** "Options are listed only once at least a dash has been typed."
- **Contract, §8 "Inputs in complete mode":** "the suggestions for an empty token are the subcommand names followed by the option names."
- **Why:** For an empty token, the option names are either listed or not listed.

### C-21: Interactive session with piped stdin and a terminal stdout
- **PRD, Terminology, "Interactive session" (l.32):** "A run whose standard input is attached to a terminal (PTY), or whose standard input or standard output is a TTY. A piped standard input without a terminal is not interactive."
- **Why:** With piped stdin and a TTY stdout, the first clause makes the run interactive and the last sentence makes it non-interactive.

### C-22: Whether a callback runs for an omitted parameter
- **PRD, Terminology, "Callback" (l.28):** "A parameter callback is not called for a parameter that was omitted and received no value from any source."
- **PRD, FP-03 "Normal behavior" (l.145):** "A missing parameter still runs its callback, so that callback can default from an earlier parameter's value."
- **Why:** A missing parameter's callback is either not called or called.

### C-23: Source ranking of the default map versus the environment
- **PRD, FP-03 "Normal behavior" (l.143):** "A value is filled from command line, then environment, then the default map ... the first of those that produces a value wins."
- **Contract, §6 `Context`, `default_map`:** "its values take precedence over environment variables."
- **Why:** When both an environment variable and a default-map entry are present, only one of them can supply the value.

### C-24: No-subcommand help for a group given only options
- **PRD, FP-06 "Boundary / error behavior" (l.234):** "a parsed invocation that leaves no subcommand name (group options or arguments only) ... Those two failures report a missing or unknown command on standard error; they do not use the no-arguments help page."
- **PRD, FP-13 "Normal behavior" (l.380):** "When the error is 'group invoked with no subcommand' under default no-args-is-help, the help page is also shown."
- **PRD, FP-02 "Normal behavior" (l.118):** "Help shown because the user invoked a group with no subcommand under the default 'no arguments means help' policy ... the help page is printed."
- **Why:** For a group with options but no subcommand under default settings, the spec says both "help page shown" and "no help page used".

### C-25: Removal of the isolated working directory
- **PRD, FP-14 "Normal behavior" (l.403):** "When no parent is given, the runner removes that directory on exit."
- **PRD, FP-14 "Normal behavior" (l.403), same bullet:** "The new directory is always left in place after the block ends, so its files can still be inspected."
- **Why:** With no parent given, the directory is either removed on exit or always left in place.
