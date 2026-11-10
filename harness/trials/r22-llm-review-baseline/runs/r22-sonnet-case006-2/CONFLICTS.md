# Specification conflicts

Abbreviations: PRD = spec/Full_PRD.md, IC = spec/Interface_Contract.md.

1. **Default maximum content width**
   - PRD FP-02 (help wrapping): "a maximum content width that defaults to 80 columns".
   - PRD FP-11 (Text wrapping): "Help pages and wrapped text use a maximum content width of 100 columns unless the caller sets another."
   - Why: the default width for help pages is either 80 or 100, not both.

2. **Subcommand short help in group listing**
   - PRD FP-02: the short help is "the first sentence of the docstring by default, ellipsized if it cannot fit on one line at the wrap width".
   - IC §2 Help page item 5: "the start of the child's first paragraph, cut with `...` at 45 characters".
   - Why: one rule cuts at the first sentence and at the line width, the other cuts the first paragraph at 45 characters, so the same docstring gives different text.

3. **Epilog position**
   - PRD FP-02: "The epilog is printed at the end of the help page, after everything else on it." IC §2 Help page item 6 agrees, putting the epilog last.
   - IC §3 `command` attrs: `epilog` is "printed right after the description, before the options".
   - Why: the epilog cannot be both last on the page and before the options section. This is also an inconsistency within IC.

4. **Form-feed in help text**
   - PRD FP-02: a form feed in the docstring "truncates the help: text after that character is omitted from the help page".
   - IC §3 `command` `help`: "a form-feed character in it is dropped and the text after it is kept".
   - Why: the text after the form feed is either omitted or kept.

5. **Environment value for a boolean flag that is not a recognised boolean token**
   - PRD FP-03: "Any other non-empty string is a conversion usage error, not a silent deactivation."
   - PRD FP-05 (Boolean): "For a boolean flag read from an environment variable, any other value turns the flag off."
   - Why: an unrecognised value such as `maybe` is either a usage error or silently turns the flag off.

6. **Several environment names on one option**
   - PRD FP-03 (Environment variables): "a list of names (first one set wins)". PRD FP-04 says the same for arguments.
   - IC §4 `option` `envvar`: "with a list, the last name that is set wins".
   - Why: when two listed variables are set, the winner is either the first or the last.

7. **Precedence of the default map versus environment**
   - PRD FP-03: a value is filled "from command line, then environment, then the default map ... then the declared default".
   - IC §6 `Context` `default_map`: "its values take precedence over environment variables".
   - Why: the environment cannot both outrank and be outranked by the default map.

8. **Counting option when omitted**
   - PRD FP-03: a counting option "yields how many times it occurred (zero if omitted)".
   - IC §4 Delivered values: "counting option: an `int`, or `None` when the option was omitted".
   - Why: an omitted counting option delivers either 0 or `None`.

9. **Repeatable option omitted with no default**
   - PRD FP-01: "A repeatable option that was omitted and has no default is passed as an absent value."
   - PRD FP-03 says "an empty tuple, not an absent value", and IC §4 Delivered values says `()`.
   - Why: the delivered value is either an absent value or an empty tuple.

10. **Showing the default of a boolean flag whose default is false**
    - PRD FP-02: "For a single-option boolean flag whose default is off (false), that default remains hidden even if show-default is on".
    - IC §4 `show_default`: "when on, the default is shown for every option, a flag whose default is `False` included".
    - Why: with show-default on, the default of a false-default flag is either hidden or shown.

11. **Choice case sensitivity with an Enum**
    - PRD FP-05 (Choice): "Matching is case-sensitive unless the author turns that off", with no exception for enumerations.
    - IC §5 `Choice`: for an `enum.Enum` subclass, "members are matched by name; by default the match ignores letter case".
    - Why: for an Enum choice with default settings, matching is either case-sensitive or case-insensitive. The same IC signature has `case_sensitive=True` as the default.

12. **Date-time when several formats match**
    - PRD FP-05 (Date-time): "Formats are tried in order; the first success wins."
    - IC §5 `DateTime`: "When several formats match a value, the last matching format is used."
    - Why: the first matching format and the last matching format give different results.

13. **Integer-range clamp at an open bound**
    - PRD FP-05 (Integer range): for an open bound, a clamped value becomes "the adjacent integer inside the range".
    - IC §5 `IntRange`: "a value beyond an open bound becomes that bound's value".
    - Why: the clamped value is either the bound itself, which is excluded, or the integer next to it.

14. **Float-range clamp with an open bound**
    - PRD FP-05 (Float range and Boundary): "Clamp is only allowed when both bounds are closed"; "Float range refuses clamp when a bound is open (declaration error)".
    - IC §5 `FloatRange`: "With `clamp=True` and an open bound, a value beyond that bound becomes the bound".
    - Why: `clamp=True` with an open bound is either a declaration error or a valid, working combination.

15. **Tilde with `resolve_path`**
    - PRD FP-09 (Path type): resolve to an absolute path, "a leading tilde is not expanded".
    - IC §5 `Path`: "With `resolve_path=True`, a leading `~` is first expanded to the home directory."
    - Why: a leading `~` is either expanded or not.

16. **Application config directory on Unix**
    - PRD FP-11 (Application directory): the folder sits under `$XDG_CONFIG_HOME` when that variable is set, otherwise under `~/.config`.
    - IC §7 `get_app_dir`: "On Unix the directory is always under `~/.config`".
    - Why: with `XDG_CONFIG_HOME` set, the directory is either under it or under `~/.config`.

17. **Pause in a non-interactive run**
    - PRD FP-11 Normal behavior: when not interactive, pause "does nothing and does not block".
    - PRD FP-11 Boundary: "Pause must not block in non-interactive runs; it still prints its message there."
    - Why: the pause does nothing, or it prints its message.

18. **Isolated filesystem cleanup**
    - PRD FP-14: "When no parent is given, the runner removes that directory on exit".
    - PRD FP-14, next sentence: "The new directory is always left in place after the block ends".
    - Why: with no parent given, the directory is either removed or left in place. This is also an inconsistency within PRD.

19. **Option suggestions for an empty token**
    - PRD FP-12: "Options are listed only once at least a dash has been typed."
    - IC §8 Inputs: "the suggestions for an empty token are the subcommand names followed by the option names".
    - Why: for an empty incomplete token, option names are either absent from the suggestions or present.

20. **Default metavar of a value option**
    - PRD FP-02: "the default metavar is the type name in uppercase ... for example, an integer option `--count` appears on the help page as `--count COUNT`".
    - Why: the type name of an integer option is not `COUNT`, which is the destination name. The rule and its example give different placeholders. The IC §5 `ParamType` `name` rule, "shown upper-cased as the default metavar", follows the type-name rule.

21. **Definition of an interactive session**
    - PRD Terminology (Interactive session): "A run whose standard input is attached to a terminal (PTY), or whose standard input or standard output is a TTY. A piped standard input without a terminal is not interactive."
    - Why: a run with piped standard input and a TTY standard output is interactive under the second clause and not interactive under the third sentence.
