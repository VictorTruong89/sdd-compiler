# Specification conflicts

PRD = spec/Full_PRD.md, IC = spec/Interface_Contract.md.

1. **Group child short help**
   - PRD, FP-02: the short help is "the first sentence of the docstring by default, ellipsized if it cannot fit on one line at the wrap width".
   - IC, section 2 Help page, item 5: "the start of the child's first paragraph, cut with `...` at 45 characters".
   - Why: the first sentence cut at the wrap width and the first paragraph cut at 45 characters give different text for the same docstring.

2. **Epilog position**
   - PRD, FP-02: the epilog "is printed at the end of the help page, after everything else on it".
   - IC, section 3 `command` attrs: `epilog` is "printed right after the description, before the options".
   - Also IC, section 2 Help page lists the epilog last (item 6), after Options and the child list, which contradicts the IC `epilog` attribute text.
   - Why: the epilog cannot be both last on the page and placed before the options.

3. **Default maximum content width**
   - PRD, FP-02: the maximum content width "defaults to 80 columns".
   - PRD, FP-11 (last Normal-behavior bullet): "Help pages and wrapped text use a maximum content width of 100 columns unless the caller sets another".
   - Why: the same default cannot be both 80 and 100.

4. **Form-feed in help text**
   - PRD, FP-02: a form feed truncates the help, so "text after that character is omitted".
   - IC, section 3 `command` `help`: "a form-feed character in it is dropped and the text after it is kept".
   - Why: the text after the form feed is either omitted or kept.

5. **Value delivered for an omitted counting option**
   - PRD, FP-03: a counting option "yields how many times it occurred (zero if omitted)".
   - IC, section 4 Delivered values: a counting option delivers "an `int`, or `None` when the option was omitted".
   - Why: an omitted counting option delivers either 0 or None.

6. **Value delivered for an omitted repeatable option with no default**
   - PRD, FP-01: "A repeatable option that was omitted and has no default is passed as an absent value".
   - PRD, FP-03 and IC, section 4 Delivered values: it is an empty tuple `()`, "not an absent value".
   - Why: the delivered value cannot be both None and `()`.

7. **Which environment variable wins when several are listed**
   - PRD, FP-03 and FP-04: with a list of names, "first one set wins".
   - IC, section 4 `option` `envvar`: "with a list, the last name that is set wins".
   - Why: when two listed variables are set, the first and the last cannot both win.

8. **Unrecognized boolean environment value**
   - PRD, FP-05 Boolean: "For a boolean flag read from an environment variable, any other value turns the flag off".
   - PRD, FP-03: "Any other non-empty string is a conversion usage error, not a silent deactivation".
   - Why: an unrecognized value either turns the flag off or is a usage error.

9. **Default map versus environment precedence**
   - PRD, FP-03 and FP-07: the order is command line, then environment, then default map, then declared default.
   - IC, section 6 `default_map`: its "values take precedence over environment variables".
   - Why: when both are set, the environment cannot be both above and below the default map.

10. **Several matching DateTime formats**
    - PRD, FP-05 Date-time: "Formats are tried in order; the first success wins".
    - IC, section 5 `DateTime`: "When several formats match a value, the last matching format is used".
    - Why: the first and the last matching format can give different results for the same value.

11. **Author date-time formats: added or replacing**
    - PRD, Public surface inventory: "an author's date-time format list is added to the default formats".
    - PRD, FP-05 Date-time: an author list "replaces the default list (it does not extend it)".
    - Why: the default formats are either kept or dropped when the author supplies a list.

12. **Choice case sensitivity default**
    - PRD, FP-05 Choice: "Matching is case-sensitive unless the author turns that off".
    - IC, section 5 `Choice`: for an Enum, members are matched by name and "by default the match ignores letter case", although the signature has `case_sensitive=True`.
    - Why: for an enum choice with default settings, matching is either case-sensitive or case-insensitive.

13. **Clamping an IntRange value past an open bound**
    - PRD, FP-05 Integer range: with an open bound, the value is replaced by "the adjacent integer inside the range".
    - IC, section 5 `IntRange`: "a value beyond an open bound becomes that bound's value".
    - Why: the clamped value is either the excluded bound or the integer next to it.

14. **FloatRange clamp with an open bound**
    - PRD, FP-05 Float range and its Boundary section: clamp "is only allowed when both bounds are closed", and an open bound is a declaration error.
    - IC, section 5 `FloatRange`: "With `clamp=True` and an open bound, a value beyond that bound becomes the bound".
    - Why: clamp with an open bound is either refused at declaration or accepted and applied.

15. **Tilde expansion in Path with resolve_path**
    - PRD, FP-09 Path: resolving to an absolute path happens with "a leading tilde ... not expanded".
    - IC, section 5 `Path`: "With `resolve_path=True`, a leading `~` is first expanded to the home directory".
    - Why: a leading `~` is either expanded or not.

16. **show_default for a boolean flag whose default is off**
    - PRD, FP-02: for a single boolean flag whose default is false, "that default remains hidden even if show-default is on".
    - IC, section 4 `option` `show_default`: "the default is shown for every option, a flag whose default is `False` included".
    - Why: the False default of a flag is either hidden or shown when show_default is on.

17. **Application directory on Unix**
    - PRD, FP-11: on Unix the directory is under `$XDG_CONFIG_HOME` when that is set, otherwise `~/.config`.
    - IC, section 7 `get_app_dir`: "On Unix the directory is always under `~/.config`".
    - Why: with `XDG_CONFIG_HOME` set, the directory cannot be both under it and under `~/.config`.

18. **Pause when not interactive**
    - PRD, FP-11 Normal: when not interactive, pause "does nothing and does not block".
    - PRD, FP-11 Boundary: "Pause must not block in non-interactive runs; it still prints its message there".
    - Why: pause either prints nothing or prints its message in a non-interactive run.

19. **Isolated filesystem cleanup**
    - PRD, FP-14: "When no parent is given, the runner removes that directory on exit".
    - PRD, FP-14, same bullet: "The new directory is always left in place after the block ends".
    - Why: the directory is either removed or left in place when the block ends.

20. **Invalid prompt input: re-ask or usage error**
    - PRD, FP-08: "Prompts re-ask on conversion failure until a valid value is given or the input stream ends".
    - PRD, FP-13: a conversion failure, "including a value typed at a prompt, which is not asked again", is a usage error.
    - Why: an invalid prompt answer either causes a re-ask or ends the run with a usage error.

21. **Option suggestions for an empty token**
    - PRD, FP-12: "Options are listed only once at least a dash has been typed".
    - IC, section 8: the suggestions for an empty incomplete token "are the subcommand names followed by the option names".
    - Why: for an empty token, options are either excluded or included.
