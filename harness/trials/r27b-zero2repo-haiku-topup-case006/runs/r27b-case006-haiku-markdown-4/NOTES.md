# Implementation notes

Optlyn is built from `spec/Full_PRD.md` (cited as **PRD**, by feature point
such as FP-03) and `spec/Interface_Contract.md` (cited as **Contract**, by
section number). Where the two disagree, or where one part of a document
contradicts another, the choice made and the reason are listed below.

Layout: package `src/optlyn/` (importable with `PYTHONPATH=src`),
`pyproject.toml` (src-layout, setuptools backend, no runtime dependencies).

## Spec conflicts and the choice made

1. **Form feed in a docstring.**
   - PRD FP-02 (Automatic help pages): "A form-feed character in the docstring
     truncates the help: text after that character is omitted from the help
     page; text before it remains."
   - Contract §3 (`command`, `help` attribute): "a form-feed character in it is
     dropped and the text after it is kept."
   - **Built:** the PRD rule. Text after the first form feed is removed; the
     form feed itself never appears.

2. **Epilog position.**
   - Contract §3 (`command` attributes): `epilog` is "printed right after the
     description, before the options."
   - Contract §2 (help page, item 6) and PRD FP-02: the epilog is printed at the
     end of the help page, after everything else.
   - **Built:** the end of the page (Contract §2 and PRD agree on this).

3. **Maximum content width for help and wrapping.**
   - PRD FP-02: a maximum content width "that defaults to 80 columns" caps
     auto-detected width for help pages.
   - PRD FP-11 (`wrap_text`): "Help pages and wrapped text use a maximum content
     width of 100 columns unless the caller sets another."
   - **Built:** help pages use 80 (the FP-02 rule, which is specific to help
     pages). `optlyn.formatting.wrap_text` defaults to 100 (the FP-11 rule for
     wrapped text). An explicit `terminal_width` is used as-is in both cases.

4. **Config directory under XDG.**
   - Contract §7 (`get_app_dir`): "On Unix the directory is always under
     `~/.config`."
   - PRD FP-11 (Application directory): `$XDG_CONFIG_HOME` is used when that
     variable is set, otherwise `~/.config`.
   - **Built:** the PRD rule. The forced-POSIX mode still ignores
     `XDG_CONFIG_HOME`, as the PRD says.

5. **Tilde with `Path(resolve_path=True)`.**
   - Contract §5 (`Path`): with `resolve_path=True`, a leading `~` "is first
     expanded to the home directory."
   - PRD FP-09 (Path type): resolve to an absolute path with symlinks resolved;
     "a leading tilde is not expanded."
   - **Built:** the PRD rule. `resolve_path=True` does not expand `~`.

6. **Date-time formats.**
   - Contract §5 (`DateTime`): `formats` are "`strftime` format strings"; "when
     several formats match a value, the last matching format is used."
   - PRD FP-05 (Date-time): "Formats are tried in order; the first success
     wins."
   - **Built:** the formats are parsing formats for `datetime.strptime`
     (`strftime` is the wrong name for a parser), and the first matching format
     wins (PRD).

7. **Choice matching case for enumerations.**
   - Contract §5 (`Choice`): for an enum, "by default the match ignores letter
     case."
   - PRD FP-05 (Choice): "Matching is case-sensitive unless the author turns
     that off."
   - **Built:** case-sensitive by default for both lists and enums
     (`case_sensitive=True`). Enum members are matched by name.

8. **Range clamping with open bounds.**
   - Contract §5: with `clamp=True`, `IntRange` turns a value beyond an open
     bound into "that bound's value"; `FloatRange` with `clamp=True` and an open
     bound turns the value into "the bound."
   - PRD FP-05 (Integer range): for an open bound, clamp uses "the adjacent
     integer inside the range." PRD FP-05 (Float range): "Clamp is only allowed
     when both bounds are closed," and FP-05 Boundary: "Float range refuses clamp
     when a bound is open (declaration error)."
   - **Built:** the PRD rules. `IntRange` clamps an open bound to the adjacent
     integer inside the range. `FloatRange(clamp=True)` with an open bound raises
     `ValueError` at construction.

9. **Counting option when omitted.**
   - Contract §4 (Delivered values table): a counting option is "an `int`, or
     `None` when the option was omitted."
   - PRD FP-03 (Options): "A counting option yields how many times it occurred
     (zero if omitted)."
   - **Built:** `0` when omitted (PRD).

10. **`show_default` for a flag whose default is off.**
    - Contract §4 (`show_default`): "when on, the default is shown for every
      option, a flag whose default is `False` included."
    - PRD FP-02 (Help): "For a single-option boolean flag whose default is off
      (false), that default remains hidden even if show-default is on."
    - **Built:** the PRD rule. A flag whose default is `False` is not shown.
      Flags whose default is `True` are shown.

11. **Precedence of the default map against environment variables.**
    - Contract §6 (`default_map`): "its values take precedence over environment
      variables."
    - PRD FP-03 (value sources) and the cross-cutting note: command line, then
      environment, then default map, then declared default.
    - **Built:** the PRD order. The default map is consulted after environment
      variables. Note that a prompt (when it runs) ranks above all of them.

12. **Boolean flag read from an environment variable with an unrecognised
    value.**
    - PRD FP-03 (Options): "Any other non-empty string is a conversion usage
      error, not a silent deactivation."
    - PRD FP-05 (Boolean): "For a boolean flag read from an environment variable,
      any other value turns the flag off."
    - **Built:** the FP-03 rule. An unrecognised value is a usage error (exit 2).
      Empty and whitespace-only values follow the FP-03 rules (empty means unset;
      whitespace-only means off). Flags whose `flag_value` is not a boolean treat
      unrecognised values as unset, as FP-03 says.

13. **Default metavar of an integer option.**
    - PRD FP-02 (Help): "the default metavar is the type name in uppercase ...
      for example, an integer option `--count` appears on the help page as
      `--count COUNT`."
    - The example's `COUNT` is the destination name, not the type name, and it
      contradicts the general rule that comes before it.
    - **Built:** the general rule. An integer option shows `INTEGER`
      (`--count INTEGER`). Author `metavar=` replaces it.

14. **Running a parameter callback for an omitted parameter.**
    - PRD glossary (Callback): "A parameter callback is not called for a
      parameter that was omitted and received no value from any source."
    - PRD FP-03 (Options): "A missing parameter still runs its callback, so that
      callback can default from an earlier parameter's value."
    - **Built:** the callback runs in every case (FP-03 is the more specific
      rule). Callbacks receive `None`, `()`, or `False` when nothing supplied a
      value.

15. **Options in the empty-token completion list.**
    - PRD FP-12: "Options are listed only once at least a dash has been typed."
    - Contract §8 (note on `COMP_CWORD`): "the suggestions for an empty token are
      the subcommand names followed by the option names."
    - **Built:** the PRD rule. An empty token suggests subcommand names (for
      groups) and no options.

16. **Isolated filesystem cleanup.**
    - PRD FP-14 (Isolated filesystem): "When no parent is given, the runner
      removes that directory on exit," and, in the same paragraph, "The new
      directory is always left in place after the block ends."
    - **Built:** the directory is removed on exit when no parent directory is
      given, and left in place when `temp_dir` is given. The "always left in
      place" sentence is taken to describe the parent-given case.

## Choices the spec left open

- **Completion framing.** A plain value is printed verbatim on a line. For zsh
  and fish, a help string follows after a tab. A path request is printed as
  `\x1ffile\x1f<incomplete>` (any path) or `\x1fdir\x1f<incomplete>`
  (directories only). Registration scripts are provided for bash, zsh, fish,
  and PowerShell. The bash, zsh, and fish scripts are not tested against those
  shells.
- **Unrecognised completion instruction.** It prints an error line to stderr,
  nothing on stdout, and exits 1 in standalone mode.
- **`prompt_required` default.** `True`, so a prompting option with no value
  prompts when omitted (Click-compatible). Setting it to `False` prompts only
  when the flag is present without a value. A required prompting option always
  prompts.
- **Parameter sources.** `ParameterSource` has five members. An undeclared name
  returns `None`. A value that was omitted and has no default has source `None`
  (and no source for a required-missing check).
- **Chain children.** Children of a chaining group parse with interspersed
  arguments off and `allow_extra_args` on, so the leftover tokens name the next
  command.
- **Feature-switch groups** (several options sharing one destination): the last
  command-line occurrence wins; otherwise the last declared option with an
  environment value; otherwise an option with an explicit default; otherwise the
  last declared option.
- **Environment variables for options** are checked in this order: the explicit
  names (first non-empty wins), then the automatic prefix name when
  `allow_from_autoenv` is on. Arguments use only the names the author gives.
- **Option values that look like options.** A token that starts with a prefix
  character is not taken as a value, except a negative number (`-1`, `-2.5`).
  So `--count -1` works, but `--name --other` is "requires an argument".
- **Deprecation warnings** go to stderr with the text `DeprecationWarning: ...`.
  An author note is appended verbatim.
- **Help page layout.** The usage line, then description, positional arguments
  (only those with help), options, commands, and epilog. Long option names
  (over 30 columns) put their help text on the next line.
- **`Option` with `is_flag=False` and a `flag_value`** takes an optional value.
  A bare flag yields `flag_value`; a following token that is not option-shaped
  is consumed as the value.
- **`version_option` without a version or package name** detects the package
  from the caller's module. The version is looked up as a distribution name
  first, then as an import name through `packages_distributions()`. If neither
  works, it prints `unknown`.
- **Fd capture in the runner** (`capture="fd"`) redirects OS-level file
  descriptors 1 and 2 into temporary files. The combined output is stdout
  followed by stderr, because write order across the two descriptors is not
  recorded.

## Not implemented

- Glob, home-directory, and environment-variable expansion of the argument list
  on Windows (PRD, non-functional constraints). The target platform is Linux,
  and the library does not change the argument list.
- Ready-made interactive shells: the completion scripts are written but not
  run in bash, zsh, fish, or PowerShell here.
- Full terminal-width detection tests and a real pager were not exercised
  (no TTY in the build environment); the code paths for them are present.
