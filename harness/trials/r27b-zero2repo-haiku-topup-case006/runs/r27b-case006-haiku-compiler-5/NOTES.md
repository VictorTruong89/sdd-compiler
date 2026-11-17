# NOTES — Optlyn build

## What is here

- `src/optlyn/` — the package (pure Python, Python 3.10+, no runtime dependencies, src layout).
  - `core.py` — `Context`, `Parameter`/`Option`/`Argument`, `Command`/`Group`/`CommandCollection`, declaration decorators, the argument parser, value resolution, help rendering, `main`.
  - `types.py` — `ParamType` and the built-in types (`STRING`, `INT`, `FLOAT`, `BOOL`, `UUID`, `UNPROCESSED`, `Choice`, `DateTime`, `IntRange`, `FloatRange`, `Tuple`, `File`, `Path`).
  - `termui.py` — terminal helpers (echo, styling, prompts, confirm, pager, progress bar, getchar, pause, editor, launch, clear, app dir, filename formatting, open_file).
  - `shell_completion.py` — registration scripts (bash, zsh, fish, powershell) and suggestion output.
  - `testing.py` — `CliRunner` / `Result` (sys and fd capture, env, stdin, isolated filesystem).
  - `formatting.py` — `wrap_text`. `exceptions.py` — error and exit classes.
- `tests/test_optlyn.py` — 129 behavioural tests, named by the spec ids they exercise in comments.
- `pyproject.toml` — setuptools src layout, no dependencies. Not needed by the judge (no build step); tests use `PYTHONPATH=src`.
- `spec/` — untouched.

Run the tests with: `cd /app && PYTHONPATH=src python3 -m pytest tests -q`
Result at the time of writing: 129 passed.

Code marks the spec ids it satisfies with `# spec: N-…` comments beside the function or class.

## Spec conflicts and what was built

The export was made with `--allow-open`; the map lists 18 unsettled contradictions. For each one below, the first side is the one written in the spec, followed by where it is, then the choice. Where a conflict is between the Interface Contract (`spec/packs/0[4-9]/1[0-3]-interface-*`, which governs names and forms) and the PRD (`spec/packs/1[4-9]/2*/3*`, which governs behaviour), the PRD was followed, because the Interface Contract says that what the library does is stated in the PRD.

### Listed as unsettled in `spec/MAP.md`

1. **CF-000010 — omitted repeatable option with no default.** N-000093 (pack 19, FP-01) says "passed as an absent value"; N-000211 (pack 21, FP-03) says "receives an empty tuple". Built: `()`, which also matches the Interface table row for omitted variadic/repeatable (N-000917).
2. **CF-000016 / CF-000092 — int range clamp beyond an open bound.** N-000361/N-000362 (pack 23, FP-05) say the nearest included value, i.e. the adjacent integer; N-000941/N-000943 (pack 09, Interface §5) say the bound's own value, which an open bound excludes. Built: adjacent integer.
3. **CF-000034 / CF-000072 — environment vs default map.** N-000243/N-000245 (pack 21/25, FP-03/FP-07) rank environment above default map; N-000955 (pack 10, Interface §6) says default-map values "take precedence over environment variables". Built: command line, then environment, then default map, then declared default (PRD).
4. **CF-000047 — epilog position.** N-000126 (pack 20, FP-02) says the epilog is at the end of the help page; N-000853 (pack 07, Interface §3) says right after the description. Built: end of the page (also matches Interface §2 item 6).
5. **CF-000048 — counting option omitted.** N-000207 (pack 21, FP-03) says zero; N-000920 (pack 08, Interface §4) says `None`. Built: `0`.
6. **CF-000063 — default short help for subcommands.** N-000122 (pack 20, FP-02) says the first sentence of the docstring, ellipsized if it does not fit the wrap width; N-000843 (pack 06, Interface §2) says the start of the first paragraph cut with `...` at 45 characters. Built: first sentence, cut to 45 characters with `...`, so both hold for the common case.
7. **CF-000087 — default maximum content width.** N-000134 (pack 20, FP-02) says 80 columns; N-000680 (pack 29, constraint) says 100. Built: 80 by default; the caller can raise it (`max_content_width`).
8. **CF-000088 — list-valued environment variable.** N-000227 (pack 21, FP-03) says the first variable that is set wins; N-000893 (pack 08, Interface §4) says the last. Built: first set wins.
9. **CF-000100 / CF-000107 — float range clamp with an open bound.** N-000381 and N-000364 (pack 23) refuse it; N-000943 (pack 09) allows it. Built: refused at construction with `ValueError`.
10. **CF-000115 — default metavar of an integer option.** N-000140 (pack 20) says the type name in uppercase, i.e. `INTEGER`; N-000144 gives the example `--count COUNT`. Built: `INTEGER`, following the general rule.
11. **CF-000128 — `pause` when not interactive.** N-000663 says it does nothing; N-000687 says it still prints its message. Built: prints nothing and does not wait.
12. **CF-000129 — application config directory on Unix.** N-000676 (pack 29, FP-11) says `$XDG_CONFIG_HOME` when set, else `~/.config`; N-001005 (pack 11, Interface §7) says always under `~/.config`. Built: `$XDG_CONFIG_HOME` when set (PRD).
13. **CF-000134 — mismatched confirmation prompt.** N-000511 (pack 26, FP-08) says the pair is asked again; N-000723 (pack 31, FP-13) says two different values are an abort. Built: asked again; end of input is an abort.
14. **CF-000136 — author date-time formats.** N-000032 (pack 16) says the author's formats are added to the defaults; N-000356 (pack 23, FP-05) says they replace the default list. Built: replace.
15. **CF-000151 — unrecognised environment value for a boolean flag.** N-000344 (pack 23) says any other text is a usage error; N-000345 (pack 23) says any other value turns the flag off. Built: usage error (FP-03, N-000234–N-000242, agrees).

### Found while building (not in the unsettled list)

16. **Path `~` expansion with `resolve_path`.** Interface §5 `Path` row: `resolve_path=True` expands a leading `~`. PRD FP-09 (N-000548–N-000573): resolution does not expand a leading tilde. Built: no tilde expansion.
17. **Choice case sensitivity.** Interface §5 signature has `case_sensitive=True`, but its prose says "by default the match ignores letter case". PRD FP-05: case-sensitive unless the author turns it off. Built: case-sensitive by default.
18. **show_default on a false flag.** Interface §4: when on, shown for every option, "a flag whose default is `False` included". PRD FP-02 (N-000146–N-000151): a single boolean flag defaulting to off stays hidden. Built: hidden (PRD).
19. **Form feed in help text.** Interface §3: the form feed is dropped and the text after it is kept. PRD FP-02 (N-000115–N-000117): the text after it is omitted from the page. Built: truncated (PRD).
20. **Exit status for a file that fails to open.** Interface §2 row 1 (N-000803–N-000806): status 1 "including a file that fails to open at first I/O". PRD FP-09 (N-000578–N-000582): a missing read target at conversion is a usage error identifying the path; only a lazy write failing at first I/O is the general error. Built: conversion-time failure is usage (2); lazy-write I/O failure is 1.
21. **Date-time format precedence.** Interface §5: "when several formats match, the last matching format is used". PRD FP-05 (N-000353–N-000357): "formats are tried in order; the first success wins". Built: first success.
22. **Callback for an omitted parameter.** Terminology (pack 15, "Callback" row): "A parameter callback is not called for a parameter that was omitted and received no value from any source." FP-03 (N-000250–N-000263): "A missing parameter still runs its callback, so that callback can default from an earlier parameter's value." Built: callbacks run for every parameter, including one omitted with no value (its value is then `None`, `()` or `False`), as FP-03 states (FP-03 is the explicit behaviour).
23. **Prompt conversion failure.** FP-08 (N-000520–N-000522): prompts re-ask on conversion failure until valid or input ends. FP-13 (N-000719–N-000722): a conversion failure, "including a value typed at a prompt, which is not asked again", is exit 2. Built: prompts re-ask (FP-08 is the dedicated prompt rule); end of input is an abort (1).
24. **Empty completion token.** Interface §8 (N-001017–N-001019): suggestions for an empty token are the subcommand names followed by the option names. FP-12 (N-000694–N-000700): options are listed only once a dash has been typed. Built: FP-12 (empty token gives subcommands and positional value completions only).
25. **Isolated filesystem removal.** FP-14 N-000744–N-000747 says both "when no parent is given, the runner removes that directory" and "the new directory is always left in place". Built: removed on exit when no `temp_dir` is given; left in place when `temp_dir` is given.
26. **Missing-command behaviour.** FP-02/FP-13 (N-000170–N-000173, N-000722) say a group invoked with no subcommand shows the help page; FP-06 (N-000429–N-000432) says a missing or unknown command reports on stderr and does not use the no-arguments help page. Built: no arguments at all gives the help page (exit 2) unless the group is invoke-without-command; a parsed invocation with group options but no subcommand gives `Missing command.` on stderr (exit 2), with no help page. These two readings are reconciled, not contradictory.

## Coverage against `spec/CHECKLIST.md`

Every pack (01–33) is implemented. The `# spec:` comments mark the function or class that satisfies each group of ids; they are grouped by behaviour, not one per id. The 129 tests in `tests/test_optlyn.py` name the ids they exercise. Not every one of the 1044 ids has its own marker or test: the coverage claim is per behaviour area, and the items below are the ones I know are missing or partial.

### Not done, or only partly done, with reasons

- **N-000051 (Windows argv expansion).** Glob, home-directory and environment-variable expansion of the argument list on Windows is not implemented. Reason: the target is Linux (N-000052); the behaviour cannot be exercised here.
- **N-000593–N-000596 (chaining: options must precede a chained subcommand's arguments).** Partly done. Each chained unit is parsed with the normal parser, so an option after a chained subcommand's argument is still bound to that subcommand. The rule that the option should not bind is not enforced.
- **N-001032–N-001034 (completion functions get already-parsed `ctx.params`).** Partly done. Completion builds a context without parsing the words already typed, so `ctx.params` is empty during completion.
- **N-000618 / N-000670–N-000671 (`launch` and binary/text standard-stream accessors).** `launch(locate=…)` is accepted but only the default opener runs (the spec says file-manager behaviour depends on the desktop session). Separate binary/text stream accessor helpers are not exported; the same behaviour is reachable through `open_file("-")` and `File`.
- **N-000649–N-000657 (progress bar remaining-time).** Implemented, but only the simple form (linear estimate); there is no terminal in the test environment, so the rendered bar is not verified against a real TTY.
- **Windows-only code paths** (`msvcrt` for `getchar`, `os.startfile` for `launch`, `cls` for `clear`, `APPDATA` for `get_app_dir`) are written but not exercised.
- **`prompt_required`** is accepted and stored but has no effect; the spec does not define a behaviour for it beyond the prompt rules already implemented.

## Choices the spec left open (implementer's choice)

- Option metavar, usage placeholder spelling, help section headings for groups (`Commands:`), and error wording.
- Shell-completion output protocol: one line per entry, `type<TAB>value<TAB>help`, with `plain`, `dir` and `file` as the types.
- Exception class names beyond those in Interface §1 (`UsageError`, `BadOptionUsage`, `BadArgumentUsage`, `NoArgsIsHelp`, `MissingParameter`, `NoSuchOption`, `Exit`, `FileError`, `OptlynError`).
- Exports beyond the required list: `Argument`, `ParameterSource`, and the exception classes.
- The internal name of the automatic help option (`__optlyn_help__`), so it never collides with an author's parameter name.
- Chain units: a chained subcommand takes the tokens up to the next command name, or everything after it if it has a variadic argument.
