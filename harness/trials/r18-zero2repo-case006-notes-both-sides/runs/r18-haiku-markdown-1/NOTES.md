# Implementation notes

Package: `src/optlyn` (import with `PYTHONPATH=src`). Pure Python, no runtime dependencies,
Python 3.10+. Importing does no I/O.

## Spec conflicts and what was built

Each item names both sides and where they are, then the choice made.

1. **Form-feed in a command docstring / `help`.**
   - `spec/Full_PRD.md` FP-02, line 102: "text after that character is omitted from the help page".
   - `spec/Interface_Contract.md` §3, `command` attrs (line 74): "a form-feed character in it is dropped and the text after it is kept".
   - Built: the PRD behaviour. Text after the form feed is cut; the form feed is removed.

2. **Maximum help width.**
   - `spec/Full_PRD.md` FP-02, line 107: maximum content width defaults to 80 columns.
   - `spec/Full_PRD.md` FP-11, line 340: "Help pages and wrapped text use a maximum content width of 100 columns unless the caller sets another."
   - Built: 80 by default for help pages (`Context.max_content_width`), overridable by the caller. The 100 default from FP-11 is not applied to help.

3. **Short help for subcommands on a group help page.**
   - `spec/Full_PRD.md` FP-02, line 104: first sentence of the docstring, ellipsized to the wrap width, unless an explicit short help is set.
   - `spec/Interface_Contract.md` §2, line 55: the start of the first paragraph, cut with `...` at 45 characters.
   - Built: explicit `short_help` if set, otherwise the first sentence, ellipsized at 45 characters. This takes the sentence from the PRD and the 45-character cut from the contract.

4. **Counting option when omitted.**
   - `spec/Full_PRD.md` FP-03, line 137: "zero if omitted".
   - `spec/Interface_Contract.md` §4, delivered values (line 177): "an `int`, or `None` when the option was omitted".
   - Built: `0` (the PRD), or the declared default when one is given.

5. **Integer range clamp at an open bound.**
   - `spec/Full_PRD.md` FP-05, line 196: with clamp, a value at or beyond an open bound becomes "the adjacent integer inside the range for an open bound".
   - `spec/Interface_Contract.md` §5, `IntRange` (line 212): "a value beyond an open bound becomes that bound's value".
   - Built: the PRD (adjacent integer). For `min_open` the result is `min + 1`; for `max_open` it is `max - 1`.

6. **Date-time format precedence.**
   - `spec/Full_PRD.md` FP-05, line 195: "Formats are tried in order; the first success wins."
   - `spec/Interface_Contract.md` §5, `DateTime` (line 211): "When several formats match a value, the last matching format is used."
   - Built: the PRD (first match wins).

7. **Path `resolve_path` and a leading tilde.**
   - `spec/Full_PRD.md` FP-09, line 292: resolve to an absolute path, "a leading tilde is not expanded".
   - `spec/Interface_Contract.md` §5, `Path` (line 216): "With `resolve_path=True`, a leading `~` is first expanded to the home directory."
   - Built: the PRD (no tilde expansion, even with `resolve_path=True`).

8. **Parameter callback for an omitted parameter.**
   - `spec/Full_PRD.md` glossary, line 28: a parameter callback "is not called for a parameter that was omitted and received no value from any source".
   - `spec/Full_PRD.md` FP-03, line 145: "A missing parameter still runs its callback, so that callback can default from an earlier parameter's value".
   - Built: the callback runs for every non-eager parameter, including omitted ones (receiving `None` or `()`), so the FP-03 defaulting use case works.

9. **Choice matching case sensitivity.**
   - `spec/Interface_Contract.md` §4, line 210: for an enum, "by default the match ignores letter case".
   - `spec/Interface_Contract.md` §5, line 213 and `spec/Full_PRD.md` FP-05, line 194: `case_sensitive=True` by default; "case-sensitive unless the author turns that off".
   - Built: case-sensitive by default for all choices, including enums. `case_sensitive=False` turns folding on.

10. **Showing the default of a flag whose default is off.**
    - `spec/Full_PRD.md` FP-02, line 110: for a single boolean flag whose default is off, the default stays hidden even when show-default is on.
    - `spec/Interface_Contract.md` §4, `show_default` (line 150): "a flag whose default is `False` included".
    - Built: the PRD (hidden).

## Known gaps

- Options with an optional value (`flag_value` plus a token) are not implemented. The contract does not list that form, so it is absent.
- Multi-value options with repetition get a flat token split from the environment or default map, not per-occurrence chunks.
- Token normalization applies to option names and choice values. It is not applied to subcommand names.
- File-descriptor capture in `CliRunner` redirects OS-level descriptors 1 and 2 to temporary files. The interpreter streams report fd 1 and 2 but are wrappers over in-memory buffers.
- `progressbar`, `getchar` and `launch` are minimal. `getchar` uses termios when available and falls back to reading standard input.
- `get_app_dir` on Windows uses `APPDATA`; this path was not exercised here.
- The completion scripts for fish and PowerShell were written but not run in their shells.
