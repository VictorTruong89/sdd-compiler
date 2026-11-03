# Implementation notes (Optlyn)

Where the specification disagrees with itself, the choice made and the reason are listed
below. Spec locations are given as `spec/<file>` plus the section or feature point.

## Spec conflicts and choices

1. **Omitted counting option value.**
   - `spec/Full_PRD.md` FP-03: "A counting option yields how many times it occurred (zero if omitted)."
   - `spec/Interface_Contract.md` §2 "Delivered values": "counting option | an `int`, or `None` when the option was omitted."
   - **Built:** `None` when omitted and no default is declared (the interface contract's table), and the count otherwise. A declared `default` is delivered when the option is omitted.

2. **Maximum content width.**
   - `spec/Full_PRD.md` FP-02: help is wrapped to the terminal width, "a maximum content width that defaults to 80 columns".
   - `spec/Full_PRD.md` FP-11: "Help pages and wrapped text use a maximum content width of 100 columns unless the caller sets another."
   - **Built:** help pages use 80 as the cap on detected width (FP-02). `optlyn.formatting.wrap_text` defaults to 100 (FP-11). An explicit `terminal_width` is used as-is for both.

3. **Epilog position.**
   - `spec/Interface_Contract.md` §3 `command` attrs: `epilog` is "printed right after the description, before the options".
   - `spec/Interface_Contract.md` §2 help-page order (item 6) and `spec/Full_PRD.md` FP-02: the epilog is printed at the end of the page.
   - **Built:** the end of the page. The page-order list is the more specific statement about the help layout.

4. **Short help for group listings.**
   - `spec/Interface_Contract.md` §2 help page item 5: "by default the start of the child's first paragraph, cut with `...` at 45 characters."
   - `spec/Full_PRD.md` FP-02: "the first sentence of the docstring by default, ellipsized if it cannot fit on one line at the wrap width."
   - **Built:** the first sentence of the docstring, then cut to 45 characters with `...` (`formatting.short_help_text`). This satisfies both the 45-character limit and the first-sentence rule.

5. **`Choice` case sensitivity.**
   - `spec/Interface_Contract.md` §5: `Choice(choices, case_sensitive=True)`, and for enumerations "by default the match ignores letter case".
   - `spec/Full_PRD.md` FP-05: "Matching is case-sensitive unless the author turns that off."
   - **Built:** case-sensitive by default for both lists and enumerations. The `case_sensitive` argument turns it off.

6. **Integer option metavar.**
   - `spec/Full_PRD.md` FP-02 states the rule: the default metavar is "the type name in uppercase". The same paragraph's example says an integer option `--count` appears as `--count COUNT`.
   - **Built:** the rule. An integer option shows `INTEGER` (type name). Authors can set `metavar=` to change it.

7. **`isolated_filesystem` cleanup.**
   - `spec/Full_PRD.md` FP-14: "When no parent is given, the runner removes that directory on exit; when a parent path is supplied, the new directory is created as a child under that parent and is left in place." The same paragraph then says "The new directory is always left in place after the block ends."
   - **Built:** the first two sentences are the mechanic, so the directory is removed when no `temp_dir` is given and left in place when one is. The final sentence was not applied.

8. **File open failure exit class.**
   - `spec/Interface_Contract.md` §2: exit `1` covers "a file that fails to open at first I/O".
   - `spec/Full_PRD.md` FP-09: a file that cannot be opened while converting the parameter is a usage error (exit 2). A lazy write that fails when I/O starts is a general error (exit 1).
   - **Built:** both. Conversion-time open failures produce exit 2 with the path named. I/O-time failures of lazy files produce exit 1.

9. **Help-page `Options` section includes `--help`.**
   - The PRD does not say whether the automatic help flag is listed. Completion must include it (FP-12), so it is listed in the Options section of the help page as well.

10. **Group option mixing.**
    - `spec/Full_PRD.md` FP-03 allows an author to enable mixing for a group. It is not specified how mixing interacts with a subcommand that shares option names.
    - **Built:** mixing is not implemented. Group options must precede the subcommand name.

## Known gaps

- `CliRunner(capture="fd")`: OS-level writes are captured through a temporary file, but stdout and stderr are two files, so `Result.output` is stdout followed by stderr rather than strict write order.
- `CliRunner(echo_stdin=True)` is accepted but does not echo unread input.
- `allow_mixing` on groups is not implemented (see conflict 10).
- Progress bar rendering is basic: a single line with a percentage-style bar and an ETA. Keyword `options` are accepted and ignored.
- `launch(..., locate=True)` opens the default application only on macOS (`open -R`); on Linux it calls `xdg-open` with the path.
- Windows glob expansion of argv is not implemented.
- Completion scripts are minimal. Bash and zsh use simple word splitting, and PowerShell and fish are untested.
- Packaging: `pyproject.toml` declares the src-layout package. The judge imports from `/app/src` via `PYTHONPATH=src`, so no install step is needed.
