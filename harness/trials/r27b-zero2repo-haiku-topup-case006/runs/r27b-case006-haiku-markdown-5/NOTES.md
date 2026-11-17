# Implementation notes

This file records where the specification disagrees with itself, the choice made for each case,
and the known gaps in this implementation. Locations are `file §section` or `file FP-xx`.

## Spec conflicts and the choice made

1. **Counting option when omitted.**
   - `spec/Full_PRD.md` FP-03 (line 137): "A counting option yields how many times it occurred (zero if omitted)."
   - `spec/Interface_Contract.md` §4 "Delivered values" table: "counting option | an `int`, or `None` when the option was omitted".
   - Built: `0` when omitted (PRD behaviour).

2. **Integer range clamp at an open bound.**
   - `spec/Full_PRD.md` FP-05 (line 196): with clamp, a value equal to an open bound is replaced "by the adjacent integer inside the range for an open bound".
   - `spec/Interface_Contract.md` §5 `IntRange`: "with `clamp=True`, a value beyond an open bound becomes that bound's value" (which would be outside the range).
   - Built: adjacent integer inside the range (PRD). `IntRange(1, 10, max_open=True, clamp=True)` maps 15 and 10 to 9.

3. **Float range clamp with open bounds.**
   - `spec/Full_PRD.md` FP-05 (lines 197, 208): clamp only when both bounds are closed; clamp with an open bound is a declaration error.
   - `spec/Interface_Contract.md` §5 `FloatRange`: "With `clamp=True` and an open bound, a value beyond that bound becomes the bound".
   - Built: `FloatRange` raises `TypeError` at construction for clamp with any open bound, or clamp with a missing bound (PRD).

4. **Date-time format precedence.**
   - `spec/Full_PRD.md` FP-05 (line 195): "Formats are tried in order; the first success wins."
   - `spec/Interface_Contract.md` §5 `DateTime`: "When several formats match a value, the last matching format is used."
   - Built: first matching format wins (PRD).

5. **Choice case sensitivity by default.**
   - `spec/Full_PRD.md` FP-05 (line 194): "Matching is case-sensitive unless the author turns that off."
   - `spec/Interface_Contract.md` §5 `Choice`: for enums, "by default the match ignores letter case".
   - Built: case-sensitive by default for lists and enums alike (PRD). `Choice(..., case_sensitive=False)` ignores case.

6. **`Path(resolve_path=True)` and tilde.**
   - `spec/Full_PRD.md` FP-09 (line 292): resolve to an absolute path, "a leading tilde is not expanded".
   - `spec/Interface_Contract.md` §5 `Path`: "With `resolve_path=True`, a leading `~` is first expanded to the home directory."
   - Built: no tilde expansion; `resolve_path=True` applies `os.path.realpath` only (PRD).

7. **`show_default` on a boolean flag whose default is off.**
   - `spec/Full_PRD.md` FP-02 (line 110): "For a single-option boolean flag whose default is off (false), that default remains hidden even if show-default is on."
   - `spec/Interface_Contract.md` §4 `show_default`: "when on, the default is shown for every option, a flag whose default is `False` included".
   - Built: hidden for a flag defaulting to `False` (PRD).

8. **Subcommand short help on a group page.**
   - `spec/Full_PRD.md` FP-02 (line 104): the first sentence of the docstring, ellipsized "if it cannot fit on one line at the wrap width".
   - `spec/Interface_Contract.md` §2 item 5: "by default the start of the child's first paragraph, cut with `...` at 45 characters".
   - Built: the Interface rule (first paragraph, cut at 45 characters with `...`), since it is the more concrete form.

9. **Help wrap width.**
   - `spec/Full_PRD.md` FP-02 (line 107): the maximum content width "defaults to 80 columns".
   - `spec/Full_PRD.md` FP-11 (line 340): "Help pages and wrapped text use a maximum content width of 100 columns unless the caller sets another."
   - Built: 80 for help pages (FP-02 is the help-specific rule). `max_content_width` can be raised by the caller.

10. **Form feed in help text.**
    - `spec/Full_PRD.md` FP-02 (line 102): for a docstring, text after a form feed is omitted from the help page.
    - `spec/Interface_Contract.md` §3 `command`: for the `help` keyword, "a form-feed character in it is dropped and the text after it is kept".
    - Built: a docstring is truncated at the form feed (PRD). An explicit `help=` has the form feed removed and the following text kept (Interface).

11. **Callbacks for omitted parameters.**
    - `spec/Full_PRD.md` Terminology (line 28): "A parameter callback is not called for a parameter that was omitted and received no value from any source."
    - `spec/Full_PRD.md` FP-03 (line 145): "A missing parameter still runs its callback, so that callback can default from an earlier parameter's value."
    - Built: callbacks run for every declared parameter, including omitted ones, so they can supply a value (the more specific rule, FP-03).

12. **Directory of `CliRunner.isolated_filesystem` without a parent.**
    - `spec/Full_PRD.md` FP-14 (line 403): "When no parent is given, the runner removes that directory on exit," and then "The new directory is always left in place after the block ends".
    - Built: removed on exit when no `temp_dir` is given; left in place when a `temp_dir` parent is supplied.

13. **Default metavar for an integer option.**
    - `spec/Full_PRD.md` FP-02 (line 108): "the default metavar ... is the type name in uppercase"; the example is "`--count COUNT`".
    - The type name of `INT` is `integer`, so the rule gives `INTEGER`, not the `COUNT` in the example.
    - Built: the rule (`INTEGER`). Authors can set `metavar=` to get any other spelling.

## Known gaps (specified, not fully implemented)

- **Feature-switch groups** (several options sharing one destination, FP-03): each option is resolved separately and the later one overwrites. The "most explicit source wins" rule is not implemented.
- **Mixing group options after the subcommand name** (FP-03, "authors may enable mixing"): not implemented; groups always stop at the subcommand name.
- **Optional-value options** (FP-03, an option whose value may be omitted and yields `flag_value`): not implemented. A value option given with no value raises a usage error (or prompts when prompting is enabled).
- **Windows argument expansion** of glob, home, and environment tokens (FP-01/NFC): not implemented.
- **`CliRunner(capture="fd")`**: accepted for API compatibility, but descriptor-level capture is not implemented; the runner always captures through the interpreter streams.
- **Token normalization for choice values**: applied to option names and command names only.
- **Pager and editor helpers** are minimal: the pager uses `PAGER` through a pipe with no style-aware handling, and `edit` does not compare file contents when deciding whether it was saved.
- **Completion**: Bash, Zsh, Fish, and PowerShell scripts are minimal and are not tested in their native shells. Suggestions and the path/directory request markers follow the spec, but the framing is simplified.
- Verified by ad-hoc scripts only; no automated test suite is included.
