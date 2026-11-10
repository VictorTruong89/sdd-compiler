# Specification conflicts

Each entry names two statements in `spec/` that cannot both hold for the same case. Line numbers refer to the files as they are now.

## C-01: Omitted repeatable option — absent value or empty tuple?

- **Full_PRD.md, FP-01, line 84:** "A repeatable option that was omitted and has no default is passed as an absent value."
- **Full_PRD.md, FP-03, line 138:** "If it is omitted and has no default, the callback receives an empty tuple, not an absent value."
- **Why they conflict:** For the same case (repeatable option, omitted, no default) one says the callback receives an absent value and the other says it receives `()`, so both cannot hold.

## C-02: Counting option when omitted — zero or `None`?

- **Full_PRD.md, FP-03, line 137:** "A counting option yields how many times it occurred (zero if omitted)."
- **Interface_Contract.md, section 4 (Delivered values table):** "counting option | an `int`, or `None` when the option was omitted".
- **Why they conflict:** An omitted counting option must deliver either `0` or `None`, and the two documents name different values.

## C-03: Help-text form-feed — text after it kept or dropped?

- **Full_PRD.md, FP-02, line 102:** "A form-feed character in the docstring truncates the help: text after that character is omitted from the help page; text before it remains."
- **Interface_Contract.md, section 3 (`command` attrs):** "`help` (description text; a form-feed character in it is dropped and the text after it is kept)".
- **Why they conflict:** For a help text containing a form-feed, one says the text after it is omitted and the other says it is kept.

## C-04: Epilog position on the help page

- **Full_PRD.md, FP-02, line 105:** "The epilog is printed at the end of the help page, after everything else on it."
- **Interface_Contract.md, section 3 (`command` attrs):** "`epilog` (printed right after the description, before the options)".
- **Interface_Contract.md, section 2 (Help page, item 6):** "The epilog, when set." (listed last, after the options and group children).
- **Why they conflict:** The epilog cannot be both the last thing on the page (after the options) and printed directly after the description, before the options.

## C-05: Short help for subcommands listed on a group page

- **Full_PRD.md, FP-02, line 104:** "the short help is the first sentence of the docstring by default, ellipsized if it cannot fit on one line at the wrap width".
- **Interface_Contract.md, section 2 (Help page, item 5):** "by default the start of the child's first paragraph, cut with `...` at 45 characters."
- **Why they conflict:** The default short help is defined as the first sentence cut to the wrap width in one document and as the first paragraph cut at 45 characters in the other, so the same docstring gives different output.

## C-06: `show_default` for a boolean flag whose default is False

- **Full_PRD.md, FP-02, line 110:** "For a single-option boolean flag whose default is off (false), that default remains hidden even if show-default is on".
- **Interface_Contract.md, section 4 (`option` attrs, `show_default`):** "when on, the default is shown for every option, a flag whose default is `False` included".
- **Why they conflict:** With show-default on, a False-default flag is either shown or hidden, and the two documents say opposite things.

## C-07: Default for `envvar` with several names — first or last set wins?

- **Full_PRD.md, FP-03, line 141:** "an option may name one variable or a list of names (first one set wins)."
- **Interface_Contract.md, section 4 (`option` attrs, `envvar`):** "with a list, the last name that is set wins".
- **Why they conflict:** When two listed variables are both set, the first and last one are different variables, so only one of the two rules can apply.

## C-08: Precedence of default map versus environment variable

- **Full_PRD.md, FP-03, line 143:** the value order is "command line, then environment, then the default map ... then the parameter's declared default; the first of those that produces a value wins."
- **Interface_Contract.md, section 6 (`Context` settings, `default_map`):** "its values take precedence over environment variables".
- **Why they conflict:** When both an environment variable and a default-map entry are set, the PRD makes the environment value win and the Interface Contract makes the default-map value win.

## C-09: Boolean flag environment value that is not recognized

- **Full_PRD.md, FP-03, line 142:** "Any other non-empty string is a conversion usage error, not a silent deactivation."
- **Full_PRD.md, FP-05, line 192:** "For a boolean flag read from an environment variable, any other value turns the flag off."
- **Why they conflict:** For an unrecognized non-empty environment value on a boolean flag, one rule makes it a usage error and the other makes it turn the flag off.

## C-10: Date-time format list — first match or last match?

- **Full_PRD.md, FP-05, line 195:** "Formats are tried in order; the first success wins."
- **Interface_Contract.md, section 5 (`DateTime`):** "When several formats match a value, the last matching format is used."
- **Why they conflict:** When more than one format parses a value, the result comes from the first in one document and the last in the other.

## C-11: `Choice` default case sensitivity

- **Interface_Contract.md, section 5 (`Choice` row):** signature `Choice(choices, case_sensitive=True)`, and the same row says "by default the match ignores letter case".
- **Full_PRD.md, FP-05, line 194:** "Matching is case-sensitive unless the author turns that off."
- **Why they conflict:** The default is case-sensitive in the signature and in the PRD, but the Interface Contract's own row says the default ignores case.

## C-12: `IntRange` clamp at an open bound

- **Full_PRD.md, FP-05, line 196:** with clamp, a value at an open bound is replaced "by the adjacent integer inside the range for an open bound".
- **Interface_Contract.md, section 5 (`IntRange`):** "with `clamp=True`, a value beyond an open bound becomes that bound's value".
- **Why they conflict:** For a value equal to or beyond an open bound, one document gives the adjacent integer inside the range and the other gives the bound itself, which is outside the range because the bound is open.

## C-13: `FloatRange` clamp with an open bound

- **Full_PRD.md, FP-05, line 197:** "Clamp is only allowed when both bounds are closed".
- **Full_PRD.md, FP-05, line 208:** "Float range refuses clamp when a bound is open (declaration error)."
- **Interface_Contract.md, section 5 (`FloatRange`):** "With `clamp=True` and an open bound, a value beyond that bound becomes the bound; any other invalid combination raises when constructed."
- **Why they conflict:** The PRD makes clamp with an open bound a declaration error, while the Interface Contract makes it a valid construction with defined clamping.

## C-14: `Path` tilde expansion with `resolve_path`

- **Full_PRD.md, FP-09, line 292:** "resolve to an absolute path (symlinks resolved to their real target; a leading tilde is not expanded)".
- **Interface_Contract.md, section 5 (`Path`):** "With `resolve_path=True`, a leading `~` is first expanded to the home directory."
- **Why they conflict:** With `resolve_path` on, a leading `~` is either expanded or left unexpanded, and the two documents say different things.

## C-15: Application config directory on Unix

- **Full_PRD.md, FP-11, line 339:** "On Unix ... it sits under the user's config home (`$XDG_CONFIG_HOME` when that variable is set, otherwise `.config` in the home directory)."
- **Interface_Contract.md, section 7 (`get_app_dir`):** "On Unix the directory is always under `~/.config`."
- **Why they conflict:** When `XDG_CONFIG_HOME` is set to another path, the PRD places the directory there while the Interface Contract always places it under `~/.config`.

## C-16: Help and wrap width (maximum content width)

- **Full_PRD.md, FP-02, line 107:** "a maximum content width that defaults to 80 columns and can be raised by the caller caps auto-detected width only".
- **Full_PRD.md, FP-11, line 340:** "Help pages and wrapped text use a maximum content width of 100 columns unless the caller sets another."
- **Why they conflict:** The same default for help pages (maximum content width) is 80 in one place and 100 in another.

## C-17: Shell completion of an empty token

- **Full_PRD.md, FP-12, line 358:** "Options are listed only once at least a dash has been typed."
- **Interface_Contract.md, section 8:** "the suggestions for an empty token are the subcommand names followed by the option names".
- **Why they conflict:** For an empty incomplete token, the PRD suggests only subcommand names and the Interface Contract also suggests option names.

## C-18: Mixing options and arguments on a chained subcommand

- **Full_PRD.md, FP-03, line 134:** "On a leaf command, options and positional arguments may be mixed: an option after an argument is parsed the same as before it."
- **Full_PRD.md, Non-functional constraints, line 56 (Parsing conventions):** "Leaf commands, by default, also allow an option to appear after a positional argument".
- **Full_PRD.md, FP-10, line 310:** "Each subcommand's options must appear before its arguments: ... an option token placed after a chained subcommand's argument is not bound to that subcommand's option."
- **Full_PRD.md, FP-10, line 319:** "Leaf commands can be attached" to a chaining group.
- **Why they conflict:** A chained subcommand is a leaf, so an option after its argument must be bound to it under the leaf rule and must not be bound to it under the chaining rule.

## C-19: Prompt on an omitted option with prompting enabled

- **Full_PRD.md, FP-08, line 268:** "An option with prompting enabled, if not supplied on the command line, reads a line from the user (standard input) and uses that as the value".
- **Full_PRD.md, FP-08, line 269:** "If the author does not require a prompt merely because the option was omitted, the option does not prompt when fully omitted; it prompts when the flag is present without a value."
- **Why they conflict:** An optional prompting option that is omitted from the command line either reads input (line 268) or does not prompt (line 269).

## C-20: Conversion failure at a prompt — re-ask or usage error?

- **Full_PRD.md, FP-08, line 274:** "Prompts re-ask on conversion failure until a valid value is given or the input stream ends".
- **Full_PRD.md, FP-13, line 380:** usage errors include "conversion failure (including a value typed at a prompt, which is not asked again)" and yield exit status 2.
- **Why they conflict:** A value typed at a prompt that fails conversion is either asked again or ends the run with exit status 2.

## C-21: Mismatched confirmation-prompt values — re-ask or abort?

- **Full_PRD.md, FP-08, line 272:** "A confirmation prompt ... rejects a mismatch by asking the pair again; mismatched values are not delivered."
- **Full_PRD.md, FP-13, line 381:** abort class includes "two different values typed into a confirmation prompt", exit status 1.
- **Why they conflict:** Two different values typed into a confirmation prompt either lead to asking the pair again or to an abort with exit status 1.

## C-22: Isolated filesystem — removed on exit or left in place?

- **Full_PRD.md, FP-14, line 403:** "When no parent is given, the runner removes that directory on exit".
- **Full_PRD.md, FP-14, line 403 (same bullet):** "The new directory is always left in place after the block ends, so its files can still be inspected."
- **Why they conflict:** Within the same bullet, a new directory created with no parent must both be removed on exit and be left in place after the block ends.
