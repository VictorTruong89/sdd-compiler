# Specification conflicts

Files: PRD = `spec/Full_PRD.md`, IC = `spec/Interface_Contract.md`.

1. **Short help of a listed subcommand**
   - PRD FP-02: the short help is "the first sentence of the docstring by default, ellipsized if it cannot fit on one line at the wrap width".
   - IC §2 Help page, item 5: "the start of the child's first paragraph, cut with `...` at 45 characters".
   - A docstring whose first sentence differs from its first paragraph, or one that fits on the line but is longer than 45 characters, gets two different short helps.

2. **Default maximum content width**
   - PRD FP-02: the maximum content width "defaults to 80 columns".
   - PRD FP-11 (Text wrapping): "a maximum content width of 100 columns unless the caller sets another".
   - The default cannot be both 80 and 100.

3. **Boolean flag with an unrecognised environment value**
   - PRD FP-03 (environment values for boolean flags): "Any other non-empty string is a conversion usage error, not a silent deactivation".
   - PRD FP-05 (Boolean): "For a boolean flag read from an environment variable, any other value turns the flag off".
   - The same unrecognised value cannot both raise a usage error and deactivate the flag.

4. **Counting option when omitted**
   - PRD FP-03: a counting option yields "how many times it occurred (zero if omitted)".
   - IC §4 Delivered values: a counting option delivers "an `int`, or `None` when the option was omitted".
   - An omitted counting option cannot deliver both 0 and `None`.

5. **Isolated filesystem cleanup**
   - PRD FP-14: "When no parent is given, the runner removes that directory on exit".
   - The same bullet then says: "The new directory is always left in place after the block ends".
   - With no parent, the directory cannot be both removed and left in place.

6. **Date-time format selection**
   - PRD FP-05 (Date-time): "Formats are tried in order; the first success wins".
   - IC §5 `DateTime`: "When several formats match a value, the last matching format is used".
   - A value matching several formats cannot be parsed by both the first and the last.

7. **Author date-time formats: replace or extend the defaults**
   - PRD "Public surface inventory": "an author's date-time format list is added to the default formats".
   - PRD FP-05 (Date-time): the author's list "replaces the default list (it does not extend it)".
   - A custom format list cannot both extend and replace the defaults.

8. **Tilde with `resolve_path`**
   - PRD FP-09 (Path type): resolve to an absolute path, with "a leading tilde is not expanded".
   - IC §5 `Path`: "With `resolve_path=True`, a leading `~` is first expanded to the home directory".
   - A `~` path cannot both be expanded and left unexpanded.

9. **Application directory on Unix**
   - PRD FP-11 (Application directory): the folder is under `$XDG_CONFIG_HOME` when that is set, otherwise `~/.config`.
   - IC §7 `get_app_dir`: "On Unix the directory is always under `~/.config`".
   - With `XDG_CONFIG_HOME` set, the directory cannot be both under it and under `~/.config`.

10. **Environment variable list: which name wins**
    - PRD FP-03 and FP-04: with a list of names, "first one set wins".
    - IC §4 `envvar`: "with a list, the last name that is set wins".
    - When two listed variables are set, the winner cannot be both the first and the last.

11. **Default map versus environment precedence**
    - PRD FP-03 (value resolution): the order is command line, then environment, then default map, then declared default.
    - IC §6 `default_map`: "its values take precedence over environment variables".
    - When both supply a value, either the environment or the default map wins, not both.

12. **Choice case sensitivity by default**
    - PRD FP-05 (Choice): "Matching is case-sensitive unless the author turns that off".
    - IC §5 `Choice`: for an enum, "by default the match ignores letter case". The same entry's signature has `case_sensitive=True`.
    - For an enum choice with default settings, matching cannot be both case-insensitive and case-sensitive.

13. **Clamping an integer range at an open bound**
    - PRD FP-05 (Integer range): clamping at an open bound gives "the adjacent integer inside the range".
    - IC §5 `IntRange`: "a value beyond an open bound becomes that bound's value".
    - The clamped value is either the adjacent inner integer or the bound itself, which the open bound excludes.

14. **Float range clamping with an open bound**
    - PRD FP-05 (Float range and Boundary): "Clamp is only allowed when both bounds are closed" and "Float range refuses clamp when a bound is open (declaration error)".
    - IC §5 `FloatRange`: "With `clamp=True` and an open bound, a value beyond that bound becomes the bound".
    - `clamp=True` with an open bound cannot both raise at construction and clamp.

15. **Position of the epilog**
    - PRD FP-02: the epilog "is printed at the end of the help page, after everything else on it". IC §2 Help page item 6 also puts it last.
    - IC §3 `command` attrs: `epilog` is "printed right after the description, before the options".
    - The epilog cannot be both last and directly after the description.

16. **Show-default for a boolean flag whose default is off**
    - PRD FP-02: for a single boolean flag whose default is false, "that default remains hidden even if show-default is on".
    - IC §4 `show_default`: "when on, the default is shown for every option, a flag whose default is `False` included".
    - The default of a false-default flag cannot be both hidden and shown.

17. **Omitted repeatable option with no default**
    - PRD FP-01: "A repeatable option that was omitted and has no default is passed as an absent value".
    - PRD FP-03 and IC §4 Delivered values: it is "an empty tuple, not an absent value" (`()`).
    - The callback cannot receive both an absent value and `()`.

18. **Pause when not interactive**
    - PRD FP-11 Normal behavior: when not interactive, pause "does nothing and does not block".
    - PRD FP-11 Boundary: pause "still prints its message there". IC §2 Channels lists the pause message on standard output.
    - Pause cannot both do nothing and print its message in a non-interactive run.

19. **Option names offered for an empty incomplete token**
    - PRD FP-12: "Options are listed only once at least a dash has been typed".
    - IC §8: for an empty incomplete token, "the suggestions for an empty token are the subcommand names followed by the option names".
    - For an empty token, option names cannot be both omitted and included.

20. **Conversion failure at a prompt**
    - PRD FP-08: "Prompts re-ask on conversion failure until a valid value is given or the input stream ends".
    - PRD FP-13: a usage error includes "conversion failure (including a value typed at a prompt, which is not asked again)".
    - A badly typed prompt value cannot be both re-asked and failed at once with exit status 2.
