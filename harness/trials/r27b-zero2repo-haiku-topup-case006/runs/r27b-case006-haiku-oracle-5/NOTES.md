# Optlyn — implementation notes

Optlyn is a pure-Python library for composable command line interfaces. The
implementation lives in `src/optlyn/` (importable from `/app/src`, so run with
`PYTHONPATH=src`). `spec/` is unchanged.

| Module | Contents |
|---|---|
| `optlyn/__init__.py` | package-root exports (Interface Contract §1) |
| `optlyn/core.py` | `Command`, `Group`, `CommandCollection`, `Option`, `Argument`, parser and dispatch, decorators, ready-made options, `pass_*` |
| `optlyn/context.py` | `Context`, `ParameterSource`, thread-local `get_current_context` |
| `optlyn/paramtypes.py` | `ParamType` and the built-in types (`Choice`, `DateTime`, `IntRange`, `FloatRange`, `Tuple`, `File`, `Path`, …) |
| `optlyn/termui.py` | echo, styling, prompts, confirm, pager, progress bar, getchar, pause, edit, launch, clear |
| `optlyn/utils.py` | file opening (lazy and atomic writes, `-` as stdin/stdout), filename formatting, app directory lookup |
| `optlyn/formatting.py` | `wrap_text` and help-layout helpers |
| `optlyn/completion.py` | shell completion: registration scripts and suggestions |
| `optlyn/exceptions.py` | `UsageError` (2), `BadParameter`, `Abort` and other errors (1), `Exit` |
| `optlyn/testing.py` | `CliRunner`, `Result`, `isolated_filesystem` |

Packaging: `pyproject.toml` (setuptools, PEP 517, src layout, zero runtime
dependencies, Python ≥ 3.10).

Tests: `tests/test_optlyn.py` (114 tests, grouped by feature point). Run with
`cd /app && PYTHONPATH=src python -m pytest tests`. All pass on Linux with
Python 3.13. Nothing was run on Python 3.10 or on macOS/Windows.

Traceability: the `# spec: <id>` markers sit next to the code for the main
behaviours. Coverage by pack is below. Statuses are per pack (the checklist
ids of a pack are contiguous), and each pack's behaviour is covered by the
tests named in the table. This is not a claim-by-claim verification of all
1044 ids.

## Traceability

| Pack | Checklist ids | Status | Where / tested by |
|---|---|---|---|
| 01 | none | n/a (no claims) | — |
| 02, 03 | N-000775..N-000789 | implemented | `pyproject.toml` (zero deps, `>=3.10`, src layout). Only Linux was exercised. |
| 04 | N-000790 | implemented (decision) | form choices recorded below |
| 05 | N-000791..N-000802 | implemented | `optlyn/__init__.py`; `test_package_exports_contract_names` |
| 06 | N-000803..N-000849 | implemented | exit statuses (`exceptions.py`, `Command.main`), channels, help page (`Command.get_help`), version identity; FP-02 and FP-13 tests |
| 07 | N-000850..N-000880 | implemented | `command`, `group`, `Group`, `CommandCollection`, `add_command`; FP-01 and FP-06 tests |
| 08 | N-000881..N-000935 | implemented | `option`, `argument`, ready-made options, `BadParameter`; FP-03 and FP-04 tests |
| 09 | N-000936..N-000949 | implemented | `paramtypes.py`; FP-05 tests |
| 10 | N-000950..N-000980 | implemented | `context.py`; FP-07 and FP-01 tests |
| 11 | N-000981..N-001012 | implemented; partly untested | `termui.py`, `utils.py`. `getchar` on a real TTY, `launch` (no opener in this sandbox returns 127), `edit` with a real editor, and the real pager are not exercised. |
| 12 | N-001013..N-001037 | implemented; scripts approximate | `completion.py`; suggestions tested. The bash script is the most complete. zsh, fish and PowerShell scripts were not run in real shells. |
| 13 | N-001038..N-001044 | implemented | `testing.py`; FP-14 tests. `capture="fd"` was checked by hand only. |
| 14, 15, 16, 17 | N-000001..N-000069 | implemented (descriptive packs) | behaviour covered by the feature-point packs; Windows argv expansion in `core._expand_windows_argv` (untested off Windows) |
| 18 | N-000070..N-000078 | not done, by design (non-goals) | server, GUI, plugin discovery, config-file syntax, thread-safe mutation are out of scope |
| 19 .. 33 (FP-01 .. FP-14, cross-cutting) | N-000079..N-000774 | implemented | feature-point sections of `tests/test_optlyn.py` |

Not done or only partly done:
- Shell completion scripts for zsh, fish and PowerShell are minimal and were not run in those shells. The path-request markers are handled by the bash script only. The PowerShell script sets `COMP_CWORD` to the token text rather than an index.
- `CliRunner(capture="fd")` is exercised by a manual check only.
- `Group.subcommand_metavar` is stored but not used in the usage line.
- `Option` with `count=True` does not read environment variables.
- Thread-safety is not provided (the spec says so).

## Conflicts in the specification and what was built

The export was made with `--allow-open`, so 28 contradictions carry no human
verdict. Each is listed below with both sides and the choice made. Ids are
`CF-…` from `spec/MAP.md`; "pack" refers to `spec/packs/`.

1. **CF-000010 — omitted repeatable option with no default.** FP-01 (pack 19, N-000093): "is passed as an absent value". FP-03 (pack 21, N-000211): "receives an empty tuple, not an absent value". Built: `()`, which matches the Interface Contract delivered-values table (pack 08, N-000914..N-000920).
2. **CF-000016 and CF-000092 — integer clamp beyond an open bound.** Interface §5 (pack 09, N-000361): "replaced by the nearest included value"; N-000362: "the adjacent integer inside the range for an open bound". Interface §5 (pack 09, N-000941): "becomes that bound's value", which an open bound excludes. Built: the adjacent integer inside the range.
3. **CF-000100 and CF-000107 — float clamp with an open bound.** Pack 09, N-000943: clamp with an open bound "becomes the bound". Pack 09, N-000364 and FP-05 (pack 23, N-000381): clamp is refused when a bound is open. Built: `FloatRange` raises `ValueError` at construction when `clamp=True` and a bound is open.
4. **CF-000034 and CF-000072 — environment versus default map.** Pack 05 and FP-03 (pack 21, N-000243, N-000245): command line, then environment, then default map, then declared default. Pack 10, N-000955: default-map values "take precedence over environment variables". Built: the PRD order (environment first).
5. **CF-000047 — epilog position.** Pack 20, N-000126: the epilog is "printed at the end of the help page". Pack 07, N-000853: "printed right after the description, before the options". Built: at the end.
6. **CF-000048 — counting option when omitted.** Pack 21, N-000207: "zero if omitted". Pack 08, N-000920: "`None` when the option was omitted". Built: `0`.
7. **CF-000063 — default short help for subcommands.** Pack 20, N-000122: the first sentence of the docstring. Pack 06, N-000843: the first paragraph, cut with `...` at 45 characters. Built: the first sentence of the first paragraph, cut at 45 characters with `...` when longer.
8. **CF-000087 — maximum content width.** Pack 20, N-000134: 80 columns. Pack 29, N-000680 (FP-11): 100 columns. Built: 80, the default for help and for `wrap_text`.
9. **CF-000088 — list-valued environment names.** Pack 21, N-000227: "first one set wins". Pack 08, N-000893: "the last name that is set wins". Built: first set name wins.
10. **CF-000115 — default metavar of an integer option.** Pack 20, N-000140: the type name in uppercase. Pack 20, N-000144: the example `--count COUNT`. Built: the type name (`--count, -c INTEGER`), because the rule is general and the example is not.
11. **CF-000128 — `pause` when not interactive.** FP-11 (pack 29, N-000663): "does nothing". Boundary (N-000687): "still prints its message there". Built: prints the message and does not block.
12. **CF-000129 — application config directory.** Pack 29, N-000676: under `$XDG_CONFIG_HOME` when that variable is set. Pack 11, N-001005: "always under `~/.config`". Built: `$XDG_CONFIG_HOME` when set, otherwise `~/.config`.
13. **CF-000134 — confirmation mismatch.** FP-08 (pack 26, N-000511): the pair is asked again. FP-13 (pack 31, N-000723): "two different values typed into a confirmation prompt" is an abort. Built: asks the pair again (FP-08), so an abort happens only at end of input.
14. **CF-000136 — author date-time formats.** Pack 16, N-000032: "added to the default formats". FP-05 (pack 23, N-000356): "replaces the default list (it does not extend it)". Built: replaces.
15. **CF-000151 and CF-000157 — unrecognised boolean text.** FP-05 (pack 23, N-000344): "anything else is a usage error". FP-05 (N-000345) and FP-03 (pack 21, N-000238): "any other value turns the flag off". Built: a usage error for any non-empty unrecognised value, for both text conversion and environment flags. Empty and whitespace-only text deactivates an environment flag, as FP-03 states.
16. **CF-000154 — isolated filesystem cleanup.** FP-14 (pack 32, N-000745): the runner removes the directory on exit when no parent is given. N-000747: "always left in place". Built: removed when no parent is given, left in place when a parent is given.
17. **CF-000155 — callback of an omitted parameter.** Glossary (pack 15, N-000022): "not called for a parameter that was omitted". FP-03 (pack 21, N-000260): "A missing parameter still runs its callback". Built: the callback runs with the default (or `None`/empty value), so it can fill from earlier parameters.
18. **CF-000156 — form feed in help text.** Pack 20, N-000115: text after the form feed is omitted. Pack 07, N-000853 (`command` attrs): "the text after it is kept". Built: truncated at the form feed, for docstrings and explicit `help=` text.
19. **CF-000158 — date-time format order.** Pack 23, N-000354: first success wins. Pack 23, N-000939: the last matching format is used. Built: the first format that parses.
20. **CF-000159 — prompt after a conversion failure.** FP-08 (pack 26, N-000520): prompts re-ask. FP-13 (pack 31, N-000719): a value typed at a prompt "is not asked again". Built: re-asks until a valid value or end of input (an abort).
21. **CF-000160 — leading `~` in paths.** FP-09 (pack 27, N-000558): not expanded. Interface §5 (pack 09, N-000947): expanded when `resolve_path=True`. Built: expanded only with `resolve_path=True`, which then also resolves symlinks.
22. **CF-000161 — completion of an empty token.** FP-12 (pack 30, N-000700): options are listed only once a dash has been typed. Interface §8 (pack 12, N-001019): subcommand names followed by option names. Built: an empty token lists subcommands only.
23. **CF-000162 — `show_default` on a flag whose default is `False`.** FP-02 (pack 20, N-000149): that default stays hidden. Interface §4 (pack 08, N-000906): shown. Built: hidden.
24. **CF-000163 — choice matching case.** FP-05 (pack 23, N-000348): case-sensitive unless the author turns that off. Interface §5 (pack 09, N-000937): ignores case by default. Built: case-sensitive by default; `case_sensitive=False` ignores case.

Disagreements not flagged in the export:

25. **Variadic argument without a default.** FP-04 (pack 22): a variadic argument omitted "yields an empty sequence unless it was marked required". FP-04 also says an argument "with neither a default nor an optional marking counts as required". Built: a variadic argument is optional unless `required=True` is given explicitly.
26. **Prompt when an option is omitted.** FP-08 (pack 26, first bullet): an option with prompting enabled "reads a line" when not supplied. FP-08 (second bullet): an option whose prompt is not required "does not prompt when fully omitted". Built: `prompt_required` (default `True`) decides. When `True`, an omitted option prompts. When `False`, it prompts only when the flag is present without a value. Declared defaults still prompt.
27. **Exit status for a file that cannot be opened.** Interface §2 (pack 06): exit `1` "including a file that fails to open at first I/O". FP-09 (pack 27): a read target or an eager write that cannot be opened is a usage error. Built: usage error (2) when the parameter converts, and general error (1) when a lazy write fails at its first I/O.

## Choices where the specification leaves the form to the implementer

- Help layout: `Usage:` line, then description, then `Positional arguments:`, `Options:` and `Commands:` sections, then the epilog. Option entries show `[default: …]`, `[env var: …]`, `[choices: …]`, `[required]` and `(Deprecated)`.
- Choice metavar `[a|b]`; the default metavar is the uppercase type name (`INTEGER`, `TEXT`, `FLOAT`, `BOOLEAN`, `PATH`, `FILENAME`).
- Exception classes beyond the contract's list: `UsageError`, `BadOptionUsage`, `BadArgumentUsage`, `NoSuchOption`, `NoSuchCommand`, `NoArgsIsHelp`, `MissingParameter`, `FileError`, `OptlynError`.
- `ParameterSource` enum: `COMMANDLINE`, `ENVIRONMENT`, `DEFAULT_MAP`, `DEFAULT`, `PROMPT`. `invoked_subcommand` is `None`, the child's name, or a `CHAINED_SUBCOMMAND` marker in a chain.
- Completion: path requests are emitted as `__optlyn_path__:file:<token>` or `__optlyn_path__:dir:<token>`. Zsh and fish lines carry a tab and the help text.
- `edit` returns `None` when the text is unchanged and `require_save` is set. `launch` returns the opener's status (127 when no opener exists).
- Declaration-time errors raise `ValueError` (for example, a deprecated option that is also required or prompts).
- A file's lazy default: reading opens at once, writing is lazy unless `lazy=False`.
- Counting option default: `0`. Repeatable option default: `()`. Flag default: `False`.
- Environment flags accept `true/1/yes/on/t/y` and `false/0/no/off/f/n`, case-insensitively, after stripping whitespace. An empty value is treated as unset.
- `CliRunner.isolated_filesystem()` removes its directory on exit when no parent is given.
- `echo` writes to a stream whose encoding cannot take Unicode by encoding the text as UTF-8 to the underlying buffer.
