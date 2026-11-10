# Specification conflicts

Each entry names two statements in `spec/` that cannot both hold for the same case. Line numbers refer to the file as read. "PRD" is `spec/Full_PRD.md`, "IC" is `spec/Interface_Contract.md`, "HW" is `spec/Hardware_Requirements.md`.

## 1. Maximum help/wrap width default
- **PRD, FP-02 "Normal behavior", line 107:** the maximum content width "defaults to 80 columns" and caps auto-detected width.
- **PRD, FP-11 "Normal behavior", line 340:** "Help pages and wrapped text use a maximum content width of 100 columns unless the caller sets another."
- **Why:** With no caller setting, help pages cannot be capped at both 80 and 100 columns.

## 2. Value of a counting option that was omitted
- **PRD, FP-03 "Normal behavior", line 137:** "A counting option yields how many times it occurred (zero if omitted)."
- **IC, §2 "Delivered values", line 177:** a counting option gives "an `int`, or `None` when the option was omitted."
- **Why:** An omitted counting option must deliver either `0` or `None`, not both.

## 3. Value delivered for an omitted repeatable option with no default
- **PRD, FP-01 "Normal behavior", line 84:** "A repeatable option that was omitted and has no default is passed as an absent value."
- **PRD, FP-03 "Normal behavior", line 138:** in that case "the callback receives an empty tuple, not an absent value." (IC line 174 agrees with FP-03.)
- **Why:** The callback cannot receive both an absent value and an empty tuple for the same omitted option.

## 4. Precedence of environment variables versus the default map
- **PRD, FP-03 "Normal behavior", line 143:** the ranking is "command line, environment, default map, declared default," so the environment outranks the default map.
- **IC, §6 "Context" table, `default_map` row, line 234:** the map's values "take precedence over environment variables."
- **Why:** A value from the environment cannot both win over and lose to a default-map value for the same parameter.

## 5. Non-boolean text in a boolean flag's environment variable
- **PRD, FP-05 "Built-in types", Boolean bullet, line 192:** "For a boolean flag read from an environment variable, any other value turns the flag off."
- **PRD, FP-03 "Normal behavior", line 142:** "Any other non-empty string is a conversion usage error, not a silent deactivation."
- **Why:** The same unrecognised non-empty value must either deactivate the flag or be a usage error, and it cannot be both.

## 6. Re-asking after a conversion failure at a prompt
- **PRD, FP-08 "Normal behavior", line 274:** "Prompts re-ask on conversion failure until a valid value is given or the input stream ends."
- **PRD, FP-13 "Normal behavior", line 380:** a conversion failure, "including a value typed at a prompt, which is not asked again," yields exit status 2.
- **Why:** A prompt value that fails conversion is either asked again or not asked again, and the spec does not allow both.

## 7. Mismatched confirmation-prompt values
- **PRD, FP-08 "Normal behavior", line 272:** a confirmation prompt "rejects a mismatch by asking the pair again."
- **PRD, FP-13 "Normal behavior", line 381:** "two different values typed into a confirmation prompt" yields an abort (exit 1).
- **Why:** After a mismatch the program either asks again or aborts, and it cannot do both.

## 8. Whether an option that is not supplied prompts
- **PRD, FP-08 "Normal behavior", line 268:** an option with prompting enabled, "if not supplied on the command line, reads a line from the user."
- **PRD, FP-08 "Normal behavior", line 269:** if the author does not require a prompt, "the option does not prompt when fully omitted."
- **Why:** For a non-required prompting option that is omitted, the spec says both that it reads a line and that it does not prompt.

## 9. Pause in a non-interactive run
- **PRD, FP-11 "Normal behavior", line 335:** when not interactive, pause "does nothing and does not block."
- **PRD, FP-11 "Boundary / error behavior", line 346:** "Pause must not block in non-interactive runs; it still prints its message there."
- **Why:** In a non-interactive run pause either prints its message or does nothing, and the two statements disagree on that.

## 10. Callback for an omitted parameter with no value
- **PRD, Terminology "Callback", line 28:** "A parameter callback is not called for a parameter that was omitted and received no value from any source."
- **PRD, FP-03 "Normal behavior", line 145:** "A missing parameter still runs its callback, so that callback can default from an earlier parameter's value."
- **Why:** A parameter callback for a missing parameter is either called or not called, and the spec gives both answers.

## 11. Which date-time format is used when several match
- **PRD, FP-05 "Built-in types", DateTime bullet, line 195:** "Formats are tried in order; the first success wins."
- **IC, §5 "Parameter types", `DateTime` row, line 211:** "When several formats match a value, the last matching format is used."
- **Why:** A value that matches two formats cannot be parsed by both the first match and the last match.

## 12. Whether custom date-time formats extend or replace the defaults
- **PRD, Public surface inventory, line 40:** "an author's date-time format list is added to the default formats."
- **PRD, FP-05 "Built-in types", DateTime bullet, line 195:** an author's list "replaces the default list (it does not extend it)."
- **Why:** The default formats are either still accepted alongside custom ones or they are not, and the two PRD statements disagree.

## 13. Clamping an integer range against an open bound
- **PRD, FP-05 "Built-in types", Integer range bullet, line 196:** with clamp, a value at an open bound "is replaced by ... the adjacent integer inside the range for an open bound."
- **IC, §5 "Parameter types", `IntRange` row, line 212:** with clamp, "a value beyond an open bound becomes that bound's value."
- **Why:** An open bound is excluded, so the value cannot become "that bound's value" and also become the adjacent integer inside the range.

## 14. Clamping a float range against an open bound
- **PRD, FP-05 "Built-in types", Float range bullet, line 197:** "Clamp is only allowed when both bounds are closed." Also PRD, FP-05 "Boundary / error behavior", line 208: "Float range refuses clamp when a bound is open (declaration error)."
- **IC, §5 "Parameter types", `FloatRange` row, line 213:** "With `clamp=True` and an open bound, a value beyond that bound becomes the bound."
- **Why:** A `FloatRange` with clamp and an open bound is either a declaration error or a valid clamped range, and the spec gives both.

## 15. Whether a leading `~` is expanded for `Path` resolution
- **PRD, FP-09 "Normal behavior", Path bullet, line 292:** "resolve to an absolute path (symlinks resolved ...; a leading tilde is not expanded)."
- **IC, §5 "Parameter types", `Path` row, line 216:** "With `resolve_path=True`, a leading `~` is first expanded to the home directory."
- **Why:** With resolution on, a leading `~` is either expanded or left as is, and the two statements give different answers.

## 16. Default case sensitivity of `Choice`
- **PRD, FP-05 "Built-in types", Choice bullet, line 194:** "Matching is case-sensitive unless the author turns that off."
- **IC, §5 "Parameter types", `Choice` row, line 210:** the signature default is `case_sensitive=True`, but the same row says enum members are matched "by default the match ignores letter case."
- **Why:** The `Choice` row gives both case-sensitive and case-insensitive matching as the default for enum choices.

## 17. Placement of the epilog on the help page
- **PRD, FP-02 "Normal behavior", line 105:** "The epilog is printed at the end of the help page, after everything else on it."
- **IC, §3 "`command`" attributes, line 74:** `epilog` is "printed right after the description, before the options."
- **IC, §2 "Help page", item 6, line 56:** the epilog comes last, after the group section.
- **Why:** The epilog cannot be both after everything else and directly after the description, before the options.

## 18. Text after a form feed in a docstring or `help`
- **PRD, FP-02 "Normal behavior", line 102:** "text after that character is omitted from the help page."
- **IC, §3 "`command`" attributes, line 74:** "a form-feed character in it is dropped and the text after it is kept."
- **Why:** The text after the form feed is either removed from the page or kept on it.

## 19. Showing the default for a boolean flag that defaults to off
- **PRD, FP-02 "Normal behavior", line 110:** "For a single-option boolean flag whose default is off (false), that default remains hidden even if show-default is on."
- **IC, §4 "`option`" attributes, `show_default` row, line 150:** when on, "the default is shown for every option, a flag whose default is `False` included."
- **Why:** A flag whose default is `False` is either shown or hidden when `show_default` is on, and the two statements disagree.

## 20. Which name wins in an environment-variable list
- **PRD, FP-03 "Normal behavior", line 141:** an option may name "a list of names (first one set wins)."
- **PRD, FP-04 "Normal behavior", line 169:** arguments take "one name or a list; first set wins."
- **IC, §4 "`option`" attributes, `envvar` row, line 137:** "with a list, the last name that is set wins."
- **Why:** When two listed variables are both set, the first or the last one is used, and the spec does not allow both.

## 21. Config directory base on Unix
- **PRD, FP-11 "Normal behavior", line 339:** on Unix the folder sits "under the user's config home (`$XDG_CONFIG_HOME` when that variable is set, otherwise `.config`)."
- **IC, §7 "Terminal helpers", `get_app_dir` row, line 292:** "On Unix the directory is always under `~/.config`."
- **Why:** When `XDG_CONFIG_HOME` is set, the directory is either under that variable or always under `~/.config`.

## 22. Completion suggestions for an empty token
- **PRD, FP-12 "Normal behavior", line 358:** "Options are listed only once at least a dash has been typed."
- **IC, §8 "Shell completion", line 306:** for an empty incomplete token, "the suggestions ... are the subcommand names followed by the option names."
- **Why:** For an empty token, option names are either suggested or not suggested, and the two statements disagree.

## 23. Short help for a subcommand listed on a group page
- **PRD, FP-02 "Normal behavior", line 104:** short help is "the first sentence of the docstring by default, ellipsized if it cannot fit on one line at the wrap width."
- **IC, §2 "Help page", item 5, line 55:** the default is "the start of the child's first paragraph, cut with `...` at 45 characters."
- **Why:** The default text is either the first sentence cut to the wrap width or the first paragraph cut at 45 characters, and it cannot be both.

## 24. Isolated filesystem cleanup
- **PRD, FP-14 "Normal behavior", line 403:** "When no parent is given, the runner removes that directory on exit."
- **PRD, FP-14 "Normal behavior", line 403 (same bullet):** "The new directory is always left in place after the block ends."
- **Why:** With no parent given, the directory is either removed on exit or left in place, and the same bullet says both.

## 25. Callback of a nested group invoked with no subcommand
- **PRD, FP-06 "Normal behavior", line 224:** "A group may be configured to run even when no subcommand is named. Then the group callback runs."
- **PRD, FP-06 "Normal behavior", line 226:** naming a nested group with nothing after it "shows that nested group's own help page ... the nested group's callback does not run."
- **Why:** Line 226 has no condition, so for a nested group configured to run without a subcommand it contradicts line 224, which says that callback runs.
