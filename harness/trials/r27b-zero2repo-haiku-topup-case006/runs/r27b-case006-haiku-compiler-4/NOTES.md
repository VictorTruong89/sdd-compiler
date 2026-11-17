# Optlyn: implementation notes

This project implements the Optlyn specification in `spec/` (33 packs, 1044 claim ids).
`spec/` is unchanged. Code lives in `src/optlyn` (src layout, zero runtime dependencies,
Python 3.10+). The hidden tests run with `PYTHONPATH=src`, so no build or install step is needed.

## Layout

| Module | Covers |
| --- | --- |
| `src/optlyn/core.py` | parameters (`Option`, `Argument`), the parser, `Context`, `Command`, `Group`, `CommandCollection`, help layout, `main` |
| `src/optlyn/decorators.py` | `command`, `group`, `option`, `argument`, ready-made options, pass decorators |
| `src/optlyn/parameter_types.py` | built-in and custom types, `Choice`, `DateTime`, ranges, `Tuple`, `File`, `Path` |
| `src/optlyn/termui.py` | echo, styling, prompts, confirm, getchar, pause, pager, progress bar, editor, launch, clear |
| `src/optlyn/utils.py` | `open_file` (lazy and atomic modes, dash streams), `format_filename`, `get_app_dir` |
| `src/optlyn/formatting.py` | `wrap_text`, short-help truncation, two-column layout |
| `src/optlyn/shell_completion.py` | registration scripts (bash, zsh, fish, PowerShell) and the suggestion protocol |
| `src/optlyn/testing.py` | `CliRunner` (sys and fd capture), `Result`, isolated filesystem |
| `src/optlyn/exceptions.py` | `BadParameter`, `UsageError`, `Abort`, and the rest of the error classes |
| `tests/` | pytest suite, one file per feature point (`python3 -m pytest tests`, 155 tests, all passing) |

Every checklist id is referenced by a `# spec: N-...` marker in the code or a test docstring.
A marker shows where an id is implemented; it does not prove the behaviour in full. The
behaviour is checked by the tests named in each feature file.

## Disagreements in the specification

The compiler flagged 18 unsettled contradictions (`spec/MAP.md`). I also found 6 more that it did not flag.
For each one I built a single behaviour. Where the two sides are of different kinds
(behaviour versus form), I followed the one that states the behaviour (the PRD).

### Flagged by the compiler (unsettled)

1. **CF-000010**: an omitted repeatable option or variadic argument with no default.
   - Pack 19/21 (FP-01 N-000093, FP-03): "is passed as an absent value".
   - Pack 21 (FP-03 N-000211) and Pack 08 (Interface N-000917, delivered-values table): "receives an empty tuple, not an absent value"; the table gives `()`.
   - **Built:** `()`.

2. **CF-000016 and CF-000092**: integer range clamp with an open bound.
   - Pack 23 (FP-05 N-000361, N-000362): closed bound replaced by the bound; open bound replaced by the adjacent integer inside the range.
   - Pack 09 (Interface N-000941, N-000943): "becomes that bound's value", which an open bound excludes.
   - **Built:** the PRD rule. Closed bound gives the bound; open bound gives the adjacent integer.

3. **CF-000034 and CF-000072**: precedence of environment variables over the default map.
   - Pack 25 (FP-03 N-000243, N-000245): command line, then environment, then default map, then declared default.
   - Pack 10 (Interface N-000955): "its values take precedence over environment variables".
   - **Built:** the PRD order. Environment is consulted before the default map.

4. **CF-000047**: placement of the epilog.
   - Pack 20 (FP-02 N-000126): printed at the end of the help page, after everything else.
   - Pack 07 (Interface N-000853): "printed right after the description, before the options".
   - **Built:** end of the page. The Interface's own help-page list (N-000844) also puts it last.

5. **CF-000048**: counting option when omitted.
   - Pack 21 (FP-03 N-000207): "zero if omitted".
   - Pack 08 (Interface N-000920): "`None` when the option was omitted".
   - **Built:** `0`.

6. **CF-000063**: default short help for subcommands.
   - Pack 20 (FP-02 N-000122): the first sentence of the docstring, ellipsized to fit the wrap width.
   - Pack 06 (Interface N-000843): the start of the first paragraph, cut with `...` at 45 characters.
   - **Built:** the first sentence of the first paragraph, cut at 45 characters with `...`.

7. **CF-000087**: default maximum content width.
   - Pack 20 (FP-02 N-000133 to N-000138): defaults to 80 columns.
   - Pack 29 (FP-11 N-000680): 100 columns unless the caller sets another.
   - **Built:** help pages cap the auto-detected width at 80 (`_help_width`). `wrap_text` has no default cap and takes an explicit width.

8. **CF-000088**: environment list with several names.
   - Pack 21 (FP-03 N-000227): the first name that is set wins.
   - Pack 08 (Interface N-000893): the last name that is set wins.
   - **Built:** first set wins.

9. **CF-000100 and CF-000107**: clamp on a float range.
   - Pack 23 (FP-05 N-000364, N-000381): clamp is allowed only with both bounds closed; a clamp with an open bound is refused at declaration.
   - Pack 09 (Interface N-000943): with clamp and an open bound, a value beyond it becomes the bound.
   - **Built:** the PRD rule. Clamp with an open bound (or a missing bound) raises `DeclarationError` when constructed. The Interface rule "any other invalid combination raises when constructed" supports this.

10. **CF-000115**: default metavar for an integer option.
    - Pack 20 (FP-02 N-000139 to N-000144): the type name in uppercase, so `INTEGER`.
    - The same block's example: "`--count` appears on the help page as `--count COUNT`".
    - **Built:** the type-name rule, so `--count INTEGER`.

11. **CF-000128**: pause when not interactive.
    - Pack 29 (FP-11 N-000662, N-000663): "does nothing and does not block".
    - Pack 29 (FP-11 N-000686, N-000687): "must not block ... it still prints its message".
    - **Built:** print the message, do not block (the boundary rule is the more specific statement).

12. **CF-000129**: application config directory on Unix.
    - Pack 29 (FP-11 N-000676): under `$XDG_CONFIG_HOME` when that is set, otherwise `~/.config`.
    - Pack 29 (Interface N-001005): "always under `~/.config`".
    - **Built:** the PRD rule (`XDG_CONFIG_HOME` honoured).

13. **CF-000134**: confirmation prompt with two different values.
    - Pack 26 (FP-08 N-000511): asks the pair again and rejects the mismatch.
    - Pack 31 (FP-13 N-000723): "two different values typed into a confirmation prompt" is an abort with exit 1.
    - **Built:** re-ask. A mismatch is an error message and the pair is asked again. An abort happens only on end of input.

14. **CF-000136**: author date-time formats.
    - Pack 16 (public surface N-000032): "is added to the default formats".
    - Pack 23 (FP-05 N-000356): "replaces the default list (it does not extend it)".
    - **Built:** replaces the defaults.

15. **CF-000151**: unrecognized text in an environment variable used for a boolean flag.
    - Pack 23 (FP-05 N-000344, N-000345): "any other value turns the flag off".
    - Pack 21 (FP-03 N-000234 to N-000242): any other non-empty string is a usage error; only for non-boolean flag values are unrecognized strings treated as unset.
    - **Built:** usage error for boolean flags. Whitespace-only strips to empty and turns the flag off. Empty means not supplied.

### Found while building (not flagged)

16. **Form feed in help text.**
    - Pack 07 (Interface N-000853, `help=`): "a form-feed character is dropped and the text after it is kept".
    - Pack 20 (FP-02 N-000114 to N-000117, docstrings): the text after the form feed is omitted.
    - **Built:** docstrings are truncated at the form feed (PRD). The `help=` keyword drops the character and keeps the text (Interface). Both statements are satisfied.

17. **Choice matching by default.**
    - Pack 09 (Interface, Choice row): an enum "members are matched by name; by default the match ignores letter case", while the same row's signature is `case_sensitive=True`.
    - Pack 23 (FP-05 N-000349): "Matching is case-sensitive unless the author turns that off".
    - **Built:** case-sensitive by default for every `Choice`, enums included.

18. **DateTime with overlapping formats.**
    - Pack 09 (Interface, DateTime row): "When several formats match a value, the last matching format is used".
    - Pack 23 (FP-05 N-000353): "Formats are tried in order; the first success wins".
    - **Built:** first success wins.

19. **Tilde in `Path(resolve_path=True)`.**
    - Pack 09 (Interface, Path row): "a leading `~` is first expanded to the home directory".
    - Pack 27 (FP-09): "resolve to an absolute path (symlinks resolved ...; a leading tilde is not expanded)".
    - **Built:** the tilde is expanded, as the Interface row states it for this parameter.

20. **Isolated filesystem cleanup.**
    - Pack 32 (FP-14 N-000744 to N-000747): the runner removes the directory on exit when no parent is given, and in the same paragraph "The new directory is always left in place".
    - **Built:** removed on exit when no `temp_dir` is given; left in place when a parent path is given.

21. **Callback for an omitted parameter.**
    - Pack 15 (Terminology, Callback row): "A parameter callback is not called for a parameter that was omitted and received no value from any source".
    - Pack 21 (FP-03 N-000250 to N-000263): "A missing parameter still runs its callback, so that callback can default from an earlier parameter's value".
    - **Built:** the callback runs with `None` (or `()`). Both the default-from-earlier-parameter use and the FP-03 rule need it.

22. **Completion suggestions for an empty word.**
    - Pack 12 (Interface N-001017 to N-001019): "the suggestions for an empty token are the subcommand names followed by the option names".
    - Pack 30 (FP-12 N-000694 to N-000697): "Options are listed only once at least a dash has been typed".
    - **Built:** the PRD rule. An empty word lists subcommands (or positional choices) only.

Two other points are interpretations rather than conflicts:
- `invoke_without_command` group with a chaining group: the result callback receives `[]` (FP-10).
- A chaining group returns the list of subcommand return values with standalone mode off, whether or not a result callback is registered (FP-10 N-000603, N-000604). A non-chaining group returns the result callback's value when one is registered.

## Coverage of the checklist

- **Referenced:** all 1044 ids appear in a `# spec:` marker or a test docstring.
- **Implemented and tested:** the feature areas FP-01 to FP-14, the Interface contract sections 1 to 9, and the hardware and packaging rules, are exercised by `tests/`.
- **Not done, with reasons:**
  - `N-001032`: completion functions receive a context whose `params` is empty, not the values already parsed. Parsing the preceding words would run callbacks and prompts during completion, so I did not do it.
  - `N-000055`: an assumption, not behaviour. The Unix shell expands arguments before the process starts; nothing to implement.
  - `N-000070` to `N-000078`: non-goals (no aliases, plugin discovery, configuration syntax, server, GUI). They are satisfied by absence.
  - `N-000756`, `N-000757`: the runner is documented as not thread-safe. No lock is added.
- **Partly done (not verified in this sandbox):**
  - The fish, zsh and PowerShell registration scripts are minimal. Only the bash script was reviewed; none was run in a real shell.
  - Windows-only paths are untested here: argv glob expansion (N-000054, implemented), `getchar` (falls back to standard input when no `/dev/tty` exists, not `msvcrt`), and the `APPDATA` directory.
  - Interactive terminal behaviour (PTY, raw-mode `getchar`, hidden input via termios, pager, progress-bar rendering on a TTY, `clear`) was not exercised; the sandbox has no TTY.
  - `launch` depends on `xdg-open` (Linux), `open` (macOS) or `os.startfile` (Windows).

## Decisions beyond the conflicts

- Version identity: `version_option()` with no `version` detects it from the distribution named by `package_name`, or from the calling module's top-level package. If neither exists, invoking the flag raises.
- Option prefixes: `-`, `/` and `+` are recognized when a declared option uses them. A declared whole name with a non-dash prefix (for example `/verbose`) matches as one option; a single-dash token is always a stack of flags.
- Option and argument types inferred from a default: `bool`, `int`, `float`, and otherwise text. A list or tuple default uses its first element's type.
- Prompts: a value option with `prompt=` reads from standard input. A default-map value or declared default still prompts and is used on an empty answer. Environment and command-line values skip the prompt. A flag with `prompt=` asks a yes/no question.
- The runner echoes a visible typed answer into captured output. Hidden answers are not echoed. `echo_stdin=True` also echoes every standard-input read (not hidden reads).
- `ctx.invoke(cmd, **kwargs)` passes only the caller's values to the callback. `ctx.forward` merges in the current parameter values.
- Group callbacks run before a child's own parsing, as in the Click family of libraries. An unknown child name is rejected before the group callback runs.

## Known gaps and risks

- Shell completion for `file` and `dir` requests relies on the shell's own path completion. This has not been tested with a real shell.
- A `version_option()` detecting the version from the calling package will not find it when that package is not installed (for example in a test module). Pass `version=` or `package_name=` explicitly in that case.
- The help width is taken from `shutil.get_terminal_size`. Tests that need stable output should pass `terminal_width=`.
