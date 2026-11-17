# Optlyn — build notes

Pure-Python implementation of the Optlyn specification in `spec/` (33 packs, 1044 checklist ids).
Code lives in `src/optlyn/`; tests live in `tests/`. Nothing in `spec/` was modified.

Run the tests: `PYTHONPATH=src python -m pytest -q tests` (80 tests, all passing at the time of writing).

Module map:

| Module | Contents |
|---|---|
| `optlyn/__init__.py` | public exports (Interface §1) |
| `optlyn/core.py` | `Context`, `Parameter`/`Option`/`Argument`, option parser, `Command`, `Group`, `CommandCollection`, `main()` |
| `optlyn/decorators.py` | `command`, `group`, `option`, `argument`, `help_option`, `version_option`, `custom_version_option`, `password_option`, `confirmation_option`, `pass_context`, `pass_obj`, `make_pass_decorator` |
| `optlyn/param_types.py` | `ParamType` and the built-in types (`STRING` … `Path`, `Tuple`, ranges, `Choice`, `DateTime`) |
| `optlyn/exceptions.py` | `UsageError` (exit 2), `BadParameter`, `MissingParameter`, `NoSuchOption`, `NoSuchCommand`, `Abort` (exit 1), `FileError` (general, exit 1), `Exit` |
| `optlyn/formatting.py` | `wrap_text` (exported from `optlyn.formatting`), `HelpFormatter` |
| `optlyn/termui.py` | `prompt`, `confirm`, `getchar`, `pause`, `edit`, `launch`, `clear`, `progressbar`, `echo_via_pager`, `get_pager_file` |
| `optlyn/utils.py` | `echo`, `secho`, `style`, `unstyle`, `open_file`, `format_filename`, `get_app_dir`, binary/text stream accessors |
| `optlyn/shell_completion.py` | `_<PROG>_COMPLETE` handling; bash/zsh/fish/powershell source and complete modes |
| `optlyn/testing.py` | `CliRunner`, `Result`, `isolated_filesystem` |

Module names avoid clashing with the standard library (the module is `param_types`, not `types`).

## Spec disagreements

The export was made with `--allow-open`; 28 contradictions have no human verdict (`spec/MAP.md`).
For each one below: side A (claim, where), side B (claim, where), and what was built. Where a
conflict pits a Contract (Interface) statement against a PRD (feature point) statement, the PRD
governs behaviour and the Contract governs form. Several conflicts were resolved that way.

1. **CF-000010 — omitted repeatable option with no default.**
   A: N-000093 (pack 19, FP-01) "passed as an absent value". B: N-000211 (pack 21, FP-03)
   "receives an empty tuple, not an absent value"; Interface §4 table also says `()`.
   **Built:** `()`.

2. **CF-000016 / CF-000092 — clamp beyond an open integer bound.**
   A: N-000361 (pack 23, FP-05) "replaced by the nearest included value"; N-000362 "the adjacent
   integer inside the range for an open bound". B: N-000943 (pack 09, Interface §5) "becomes that
   bound's value". **Built:** closed bound → the bound; open bound → the adjacent integer inside the range (FP-05).

3. **CF-000034 / CF-000072 — precedence of environment vs default map.**
   A: N-000243 (pack 21, FP-03) and N-000245 "environment, then the default map";
   B: N-000955 (pack 10, Interface §6 `default_map`) "its values take precedence over environment
   variables". **Built:** environment before default map (PRD ranking); the default map is consulted after environment.

4. **CF-000047 / CF-000156 — epilog position; form-feed truncation.**
   A: N-000126 (pack 20, FP-02) "epilog is printed at the end of the help page"; B: N-000853
   (pack 07, Interface §3 attrs) "printed right after the description, before the options".
   **Built:** epilog last (also Interface §2 help-page order).
   Form feed: A: N-000115 (pack 20) "text after that character is omitted"; B: N-000853 "the text after it is kept".
   **Built:** text after the form feed is omitted; the form feed itself is removed.

5. **CF-000048 — counting option when omitted.**
   A: N-000207 (pack 21, FP-03) "zero if omitted"; B: N-000920 (pack 08, Interface §4)
   "`None` when the option was omitted". **Built:** `0`.

6. **CF-000063 — default short help for subcommands.**
   A: N-000122 (pack 20, FP-02) "first sentence of the docstring"; B: N-000843 (pack 06, Interface §2)
   "start of the first paragraph, cut with `...` at 45 characters". **Built:** the first sentence,
   ellipsized (`...`) only when it does not fit on one line at the wrap width (FP-02 wording).

7. **CF-000087 — default maximum content width.**
   A: N-000134 (pack 20, FP-02) "defaults to 80 columns"; B: N-000680 (pack 29, FP-11) and the pack-06
   constraint "100 columns unless the caller sets another". **Built:** 80 for help pages (FP-02 is the
   help-specific statement). `max_content_width` can still be set by the caller.

8. **CF-000088 — list-valued environment variables.**
   A: N-000227 (pack 21, FP-03) "first one set wins"; B: N-000893 (pack 08, Interface §4) "the last name
   that is set wins". **Built:** first set wins.

9. **CF-000100 / CF-000107 — clamp with an open FloatRange bound.**
   A: N-000381 (pack 23) "Float range refuses clamp when a bound is open" and N-000364 "clamp only when
   both bounds are closed"; B: N-000943 (pack 09) "with clamp=True and an open bound, a value beyond that bound
   becomes the bound". **Built:** `FloatRange(..., clamp=True)` with an open bound raises `TypeError` at construction.

10. **CF-000115 — default metavar of an integer option.**
    A: N-000140 (pack 20) "the default metavar is the type name in uppercase" (Interface §5 says a
    ParamType's name is shown upper-cased as its metavar); B: N-000144 (pack 20) "an integer option `--count`
    appears as `--count COUNT`". **Built:** `--count INTEGER` (the rule, not the example).

11. **CF-000128 — pause when not interactive.**
    A: N-000663 (pack 29) "when not interactive it does nothing"; B: N-000687 "it still prints its message there".
    **Built:** prints the message, does not wait for a key.

12. **CF-000129 — application config directory on Unix.**
    A: N-000676 (pack 29, FP-11) "`$XDG_CONFIG_HOME` when that variable is set, otherwise `~/.config`";
    B: N-001005 (pack 11, Interface §7) "always under `~/.config`". **Built:** XDG rule (PRD).

13. **CF-000134 / CF-000159 — confirmation mismatch and conversion failure at a prompt.**
    CF-000134: A: N-000511 (pack 26, FP-08) mismatch "rejects a mismatch by asking the pair again";
    B: N-000723 (pack 31, FP-13) "two different values typed into a confirmation prompt" is an abort.
    CF-000159: A: N-000520 (pack 26) "prompts re-ask on conversion failure"; B: N-000719 (pack 31)
    "a value typed at a prompt, which is not asked again". **Built:** both re-ask (FP-08, the detailed
    prompt rule). Standalone EOF during a prompt is still an abort.

14. **CF-000136 — author date-time formats.**
    A: N-000032 (pack 16) "is added to the default formats"; B: N-000356 (pack 23, FP-05) "replaces the default list".
    **Built:** replaces (FP-05).

15. **CF-000151 / CF-000157 — non-recognized boolean text.**
    CF-000151: N-000344 (pack 23) boolean text conversion: anything else is a usage error;
    N-000345 (pack 23) boolean env flag: "any other value turns the flag off".
    CF-000157: N-000238 (pack 21, FP-03) "any other non-empty string is a conversion usage error";
    N-000345 "any other value turns the flag off". **Built:** usage error in both cases (the FP-03 env
    rule says "not a silent deactivation"). Empty env values are "unset"; whitespace-only deactivates.

16. **CF-000154 — isolated filesystem removal.**
    N-000745 (pack 32, FP-14) "when no parent is given, the runner removes that directory on exit";
    N-000747 "always left in place after the block ends". **Built:** removed when no parent is given;
    left in place when a parent is given (the first, more specific clause).

17. **CF-000155 — callback for an omitted parameter.**
    A: N-000022 (pack 15) "a parameter callback is not called for a parameter that was omitted and
    received no value from any source"; B: N-000260 (pack 21, FP-03) "a missing parameter still runs its
    callback, so that callback can default from an earlier parameter's value". **Built:** callbacks run for
    omitted parameters with value `None`/`()` (FP-03; required parameters still fail before the callback).

18. **CF-000158 — date-time format matching.**
    A: N-000354 (pack 23, FP-05) "formats are tried in order; the first success wins"; B: N-000939 (pack 09)
    "the last matching format is used". **Built:** first success wins.

19. **CF-000160 — `resolve_path` and a leading tilde.**
    A: N-000558 (pack 27, FP-09) "a leading tilde is not expanded"; B: N-000947 (pack 09)
    "a leading `~` is first expanded". **Built:** not expanded (PRD).

20. **CF-000161 — completion of an empty token.**
    A: N-000700 (pack 30, FP-12) "options are listed only once at least a dash has been typed";
    B: N-001019 (pack 12, Interface §8) "the suggestions for an empty token are the subcommand names followed by
    the option names". **Built:** empty token → subcommand names only (no options).

21. **CF-000162 — `show_default` on a flag whose default is False.**
    A: N-000149 (pack 20, FP-02) "that default remains hidden even if show-default is on";
    B: N-000906 (pack 08, Interface §4) "a flag whose default is `False` included". **Built:** hidden (FP-02).

22. **CF-000163 — `Choice` letter case.**
    A: N-000348 (pack 23, FP-05) "matching is case-sensitive unless the author turns that off";
    B: N-000937 (pack 09, Interface §5) "by default the match ignores letter case" (its own signature says
    `case_sensitive=True`). **Built:** case-sensitive by default (matches the signature and FP-05).

Further points the compiler did not flag (choices, not conflicts):

- `FP-07` says `invoke` supplies "exactly the caller's chosen values". **Built:** values passed to `ctx.invoke` are
  used as given; parameters the caller omitted receive their declared defaults, so a command can still be
  invoked with partial values.
- `FP-14` isolated-filesystem and `FP-13` missing-command wording: a group invoked with no tokens shows the help
  page (exit 2); a group given only group options gets "Missing command." on stderr (exit 2), as FP-06 requires.
- A declaration that the spec says is refused (deprecated + required, deprecated + prompt, deprecated required
  argument, FloatRange clamp with an open bound, multi-character short names, two variadic arguments) raises
  `TypeError` at declaration. `FloatRange(min > max)` raises `ValueError`.

## Other choices where the spec leaves the form open

- Error and help wording, section headings (`Options:`, `Positional arguments:`, `Commands:`), and the
  `[default: …]`, `[env var: …]`, `[choices: …]`, `[required]` extras.
- Exception class names beyond those in Interface §1: `NoSuchOption`, `NoSuchCommand`, `BadOptionUsage`,
  `BadArgumentUsage`, `MissingParameter`, `NoArgsIsHelpError`, `FileError`, `OptlynError`.
- Completion output: one suggestion per line; zsh/fish append `\t` + help; path requests are `@@file\t<token>`
  and `@@dir\t<token>`. Registration scripts are shell-specific; only generation was checked, bash was not executed here.
- `CHAIN_SUBCOMMAND` is the value of `ctx.invoked_subcommand` on a chaining group (distinct from None and any name).
- `getchar` reads the terminal (`/dev/tty` when stdin is not a terminal). If no terminal can be opened it falls back to
  reading the process's standard input; this consumes piped bytes, which the spec forbids. It is a documented
  deviation for environments with no controlling terminal.
- Interactive means stdin or stdout is a terminal (Terminology). Pager command: `$PAGER`, else `less`.
- Options named with several flags share one destination (the first long name, else the first short name).
- Auto environment-variable prefix: explicit `envvar` names are tried first, then the prefix-built name.

## Coverage of the checklist

Every id in `spec/CHECKLIST.md` (N-000001 … N-001044) is accounted for below. "Implemented" means code
exists and carries a `# spec:` marker; "tested" means `tests/test_optlyn.py` exercises the behaviour.
I did not tick the checklist file (it is part of `spec/`).

| Pack | Ids | Status | Where |
|---|---|---|---|
| 01 Hardware (no claims) | — | n/a | — |
| 02–03 Hardware: summary, profiles | N-000775 … N-000789 | implemented; tested (import from `src`, zero deps). N-000789 (editable install) is implemented by `pyproject.toml` but not exercised here | `pyproject.toml`, `src/optlyn/` |
| 04 Interface contract (form decision) | N-000790 | implemented (choices listed above) | all modules |
| 05 Package & modules | N-000791 … N-000802 | implemented; tested (`test_N_000795_to_N_000801_package_exports`, `test_N_000800_…`) | `__init__.py`, `testing.py` |
| 06 Global output forms | N-000803 … N-000849 | implemented; tested (exit statuses, channels, help page order, version identity) | `core.py` (`Command.main`), `exceptions.py`, `formatting.py`, `utils.py` |
| 07 Declaring commands & groups | N-000850 … N-000880 | implemented; tested | `core.py`, `decorators.py` |
| 08 Parameters | N-000881 … N-000935 | implemented; tested | `core.py` (`Option`, `Argument`, parser), `decorators.py` |
| 09 Parameter types | N-000936 … N-000949 | implemented; tested | `param_types.py` |
| 10 Invocation context | N-000950 … N-000980 | implemented; tested | `core.py` (`Context`), `decorators.py` |
| 11 Terminal helpers | N-000981 … N-001012 | implemented; tested for echo, styles, prompt, confirm, edit, pause, pager (non-TTY), file helpers. Progress bar rendering and `getchar` on a real TTY are not exercised (no TTY here) | `utils.py`, `termui.py` |
| 12 Shell completion | N-001013 … N-001037 | implemented; tested (suggestions, source modes, unknown instruction, path requests, parsed-params). Bash/zsh/fish/PowerShell scripts were generated, not executed | `shell_completion.py` |
| 13 In-process runner | N-001038 … N-001044 | implemented; tested (captured streams, exceptions, env restore, echo stdin, isolated filesystem) | `testing.py` |
| 14 PRD overview | N-000001 … N-000014 | implemented (design principles and feature list) | — |
| 15 Terminology | N-000015 … N-000024 | implemented; tested through `test_FP02`/`test_FP06`/`test_FP08` behaviours | `core.py` |
| 16 Public surface inventory | N-000025 … N-000044 | implemented; tested (`test_N_000795_…` exports) | `__init__.py` |
| 17 Non-functional constraints | N-000045 … N-000069 | implemented: pure Python, zero runtime deps, no I/O or processes on import, ASCII-safe echo (tested), thread-local context | all |
| 18 Non-goals | N-000070 … N-000078 | not done, by design: these are scope limits (no server/GUI, no built-in aliases or plugin discovery, no config syntax, no thread-safe context mutation) | — |
| 19 FP-01 declaration, naming, invocation | N-000079 … N-000109 | implemented; tested (`test_FP01_*`, deprecated command) | `decorators.py`, `core.py` |
| 20 FP-02 help & eager doc | N-000110 … N-000177 | implemented; tested (`test_FP02_*`) | `formatting.py`, `core.py`, `decorators.py` |
| 21 FP-03 options | N-000178 … N-000284 | implemented; tested (`test_FP03_*`) | `core.py` |
| 22 FP-04 positional arguments | N-000285 … N-000329 | implemented; tested (`test_FP04_*`) | `core.py` |
| 23 FP-05 types & conversion | N-000330 … N-000383 | implemented; tested (`test_FP05_*`) | `param_types.py` |
| 24 FP-06 groups & deferred loading | N-000384 … N-000433 | implemented; tested (`test_FP06_*`) | `core.py` |
| 25 FP-07 context, defaults, env prefix | N-000434 … N-000483 | implemented; tested (`test_FP07_*`) | `core.py` |
| 26 FP-08 prompts & confirmation | N-000484 … N-000527 | implemented; tested (`test_FP08_*`) | `termui.py`, `core.py`, `decorators.py` |
| 27 FP-09 file & path parameters | N-000528 … N-000590 | implemented; tested (`test_FP09_*`) | `param_types.py`, `utils.py` |
| 28 FP-10 chaining & pipelines | N-000591 … N-000617 | implemented; tested (`test_FP10_*`) | `core.py` |
| 29 FP-11 terminal output & helpers | N-000618 … N-000688 | implemented; tested (`test_FP11_*`) | `utils.py`, `termui.py`, `formatting.py` |
| 30 FP-12 shell completion | N-000689 … N-000715 | implemented; tested (`test_FP12_*`) | `shell_completion.py` |
| 31 FP-13 usage failures & exit status | N-000716 … N-000735 | implemented; tested (`test_FP13_*`) | `core.py`, `exceptions.py` |
| 32 FP-14 in-process runner | N-000736 … N-000763 | implemented; tested (`test_FP14_*`) | `testing.py` |
| 33 Cross-cutting refinements | N-000764 … N-000774 | implemented (hidden names, FP-02/FP-13 exit split, source precedence) | `core.py` |

Known gaps (not claimed as tested):

- Progress bar drawing, pager on a live terminal, `getchar` from a real TTY, and `pause` blocking.
- Bash/zsh/fish/PowerShell completion scripts are not run under their shells.
- `launch` and `edit` are exercised only through a fake editor (`sh -c`) and not through a desktop opener.
