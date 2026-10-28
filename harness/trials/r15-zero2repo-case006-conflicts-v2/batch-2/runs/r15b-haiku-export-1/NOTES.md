# Optlyn: implementation notes

The package lives in `src/optlyn` (src layout, zero runtime dependencies, Python 3.10+).
`pyproject.toml` declares a setuptools PEP 517 build, but nothing needs to be built:
the tests run with `PYTHONPATH=src`. `spec/` is unchanged.

## Layout

| Module | Covers (spec packs) |
|---|---|
| `core.py` | Context, Parameter/Option/Argument, option parser, Command/Group/CommandCollection, dispatch, chaining, help rendering, `main()` (FP-01, FP-02, FP-03, FP-04, FP-06, FP-07, FP-10, FP-13; Contract §3, §4, §6) |
| `paramtypes.py` | Built-in and custom types, File, Path, Choice, DateTime, ranges, Tuple (FP-05, FP-09; Contract §5) |
| `decorators.py` | `command`, `group`, `option`, `argument`, `pass_context`, `pass_obj`, `make_pass_decorator`, `help_option`, `version_option`, `custom_version_option`, `password_option`, `confirmation_option` (Contract §3–4, §6; FP-02, FP-08) |
| `termui.py` | prompt, confirm, getchar, pause, edit, launch, clear, progressbar, pager (FP-08, FP-11; Contract §7) |
| `utils.py` | echo, secho, style, unstyle, open_file, LazyFile, format_filename, get_app_dir, get_current_context (FP-09, FP-11) |
| `formatting.py` | `wrap_text` and help-text rewrapping (FP-02, FP-11) |
| `shell_completion.py` | bash/zsh/fish/PowerShell registration scripts and suggestion engine (FP-12; Contract §8) |
| `testing.py` | `CliRunner`, `Result`, `isolated_filesystem` (FP-14; Contract §9) |
| `globals.py` | thread-local current-context stack |

Tests: `tests/test_optlyn.py` (104 tests, run with `PYTHONPATH=src python3 -m pytest tests`).
The one acceptance criterion in the spec (N-001013, the `--count COUNT` help line) is
`test_AC_N_001013_count_metavar`.

## Spec conflicts and what I built

These are the six unsettled contradictions listed in `spec/MAP.md`, plus two conflicts I found while reading.

1. **Deprecation warning channel** (CF-000146; pack 06 channel table vs pack 19 FP-01).
   The channel table says standard error; FP-01 says standard output. **Built: standard error.**
2. **Default map vs environment precedence** (CF-000150; pack 10 `default_map` key vs pack 21 FP-03 ranking, also pack 25).
   The Contract says the map beats the environment; the PRD's explicit ranking (prompt, command line, environment, default map, declared default) says the reverse. **Built: the PRD ranking (environment before default map)**, since the Contract defers behaviour to the PRD.
3. **Confirm answers other than yes/no/empty** (CF-000151; pack 11 `confirm` vs pack 26 FP-08).
   **Built: ask again** (PRD). The Contract's "counts as no" is not implemented.
4. **Default metavar** (CF-000152; pack 20 FP-02 rule "type name in uppercase" vs its acceptance criterion `--count COUNT`).
   **Built: the destination name in uppercase** (so `--count` shows `COUNT`, satisfying the acceptance criterion). A choice type keeps its own placeholder `[a|b]`.
5. **Isolated filesystem cleanup** (CF-000153; pack 32 FP-14). One sentence says the directory is removed when no parent is given; another says it is always left in place.
   **Built: removed on exit when no parent is given; left in place when a parent path is given.**
6. **Maximum content width** (CF-000155; pack 20 FP-02 says 80 columns for help vs pack 29 FP-11 says 100 for help and wrapped text).
   **Built: help pages cap at 80 columns by default** (`max_content_width`), and `wrap_text` defaults to 100 columns.
7. **Callbacks for omitted parameters** (not in the unsettled list; pack 15 glossary says a callback is not called for an omitted parameter; pack 21 FP-03 says "a missing parameter still runs its callback").
   **Built: the FP-03 rule**, so callbacks run for omitted parameters too and can read earlier values.
8. **`Context.invoke` values** (pack 10 says invoke supplies "exactly the caller's chosen values"; the Contract and FP-07 leave unspecified what happens to parameters the caller omits). **Built: omitted parameters take their declared defaults**, so the callee receives all its arguments. Values from the calling command are *not* forwarded by `invoke`; `forward` does forward them.

## Interpretations where the spec was silent

- **Optional-value options** have no keyword in the Contract. Built as `is_flag=False, flag_value=...`.
- **Flag names:** an option declared `--on/--off` or `/x` or `+x` is recognised by its prefix character. Only single-character short names stack.
- **Feature switches:** a shared destination with no declared default yields `None` when the flag values are not booleans, and `False` when they are.
- **Required with a declared default:** a required option or argument must come from the command line, the environment, the default map, or a prompt. A declared default alone does not satisfy `required`, following the wording in FP-03.
- **Prompts:** a prompting option is asked when it is required (and not supplied by the environment or default map) or when its flag appears without a value. A declared default is shown and used on an empty answer.
- **Chaining:** the children are parsed and checked before the group callback runs, so an unknown name fails before anything runs. Each child's parameters are then parsed one after another; an option after a child's argument is left over for the next child name.
- **Non-standalone mode:** an author `exit` or intentional help returns `None`; usage errors and aborts propagate as exceptions.
- **Completion output:** each line is `kind,value`, where `kind` is `plain`, `file` or `dir`. For zsh and fish a help string follows a tab. The registration scripts for zsh, fish and PowerShell are written but were not run (no shell is installed here besides bash). The bash script was checked end to end.
- **`version_option`** with a package that cannot be found prints `unknown` as the version (the spec does not say what to do).
- **STRING type name** is `text`. Choice metavar is `[a|b]`. DateTime metavar lists its formats.
- **Dest inference** keeps the case of the declared name, so `--Name` gives destination `Name` (the spec's rule, not a lowercase rule).

## Not done

- Windows argv expansion (glob, home directory, environment tokens) when run as a program. The target is Linux, and the spec says this applies only to Windows.
- `getchar` reads `/dev/tty` when standard input is not a terminal. This is untested.
- Hidden-input echo suppression on a real terminal (termios) is untested here.
- `echo_stdin` in the runner echoes prompt lines only, not every `getchar` read.
- `launch` and `edit` are minimally tested (edit has one test; launch is untested).
- Zsh, fish and PowerShell completion scripts are untested.

## Spec checklist accounting

`spec/CHECKLIST.md` boxes were not ticked, because `spec/` must stay as it is. Accounting is by pack, not by id:
every pack that carries claims (02–33) is implemented in the modules above, and the tests exercise the main behaviour of each feature point. I did not add a `# spec: <id>` marker for each of the 1015 ids. The "Not done" list above is the set of known gaps.
