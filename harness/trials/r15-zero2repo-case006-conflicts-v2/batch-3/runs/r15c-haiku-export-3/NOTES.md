# Optlyn — implementation notes

## Layout

- Package: `src/optlyn/` (import with `PYTHONPATH=src`; `pyproject.toml` builds it with zero runtime dependencies).
- Modules: `core.py` (Context, Parameter/Option/Argument, option parser, Command/Group/CommandCollection),
  `decorators.py`, `types.py`, `termui.py`, `formatting.py`, `shell_completion.py`, `testing.py`
  (`CliRunner`), `exceptions.py`, `_files.py`, `_local.py`.
- Tests: `tests/test_optlyn.py` (112 behavioural tests, grouped by feature point). Run with
  `PYTHONPATH=src python3 -m pytest tests/`.
- `spec/` is unchanged.

## Conflicts in the specification and what was built

The export lists six unsettled contradictions (`--allow-open`). Each was resolved as follows:

| Id | Disagreement | Built |
|---|---|---|
| CF-000146 | Deprecation warning: PRD FP-01 says standard output; Contract §2 channel table says standard error (N-000081 vs N-000803). | Standard error, per the Contract's channel table. |
| CF-000151 | `confirm` with an answer other than yes/no/empty: PRD FP-08 says asks again; Contract §9 says counts as no. | Asks again (PRD). |
| CF-000155 | Default max content width: FP-02 says 80 (N-000127); FP-11 says 100 (N-001014). | Help pages cap auto-detected width at 80 (`max_content_width`, FP-02 is the help-specific rule). `wrap_text` with no width uses min(terminal, 100). An explicit `terminal_width` is used as-is. |
| CF-000150 | Precedence of environment vs default map: FP-03 ranks command line > environment > default map > declared default; Contract §6 says default map beats environment. | Environment beats default map (FP-03 ranking). |
| CF-000152 | Integer option metavar: N-000326 says type name uppercased (`INTEGER`); N-001013 example shows `--count COUNT`. | Type name uppercased (`INTEGER`). |
| CF-000153 | Isolated filesystem with no parent: N-000732 says removed on exit; N-001015 says always left in place. | Removed on exit when no parent is given (the more specific clause); left in place when a parent is given. |

Other choices where the spec is silent, ambiguous, or internally inconsistent:

- **Callbacks for omitted parameters.** Terminology says a callback is not called for an omitted parameter with no value; FP-03 says a missing parameter still runs its callback. Built: callbacks run (FP-03 is the more specific rule). A *required* parameter that is still missing raises before its callback.
- **Prompt semantics.** `prompt=` prompts when omitted by default (`prompt_required=True`). With `prompt_required=False` it prompts only when the flag is given without a value. Prompt defaults come from the default map, then the declared default (callables invoked).
- **Confirmation option.** `confirmation_option` is a flag that asks when omitted; a decline raises `Abort` (exit 1).
- **Feature-switch ties.** Several options sharing a destination: highest source rank wins (prompt > command line > environment > default map > declared default); explicit defaults beat auto-derived ones; otherwise the last declared wins.
- **Chained subcommands** parse with interspersed arguments off, and their leftover tokens feed the next command. Their files close when the subcommand returns.
- **Default map.** Nested by subcommand name for groups; keyed by destination on a leaf. A string for a repeatable option with one value per occurrence is refused (usage error), per FP-07.
- **Exit statuses.** Standalone mode: 0 success/intentional help/version; 2 usage errors including missing-subcommand help; 1 abort, general errors, and file-open failures at first I/O. Non-standalone mode returns the callback value; an author `exit()` returns `None`.
- **Shell completion wire format** (implementer's choice per the Contract): suggestions print one per line; zsh and fish append `\t<help>`. Path requests print `\x1f<file|dir>\x1f<incomplete>`, which the generated scripts expand with `compgen`/`_files`. An unknown `_<PROG>_COMPLETE` instruction prints nothing and exits 1.
- **Pager** uses `$PAGER` when set, otherwise `less`. Pager and progress-bar rendering are terminal-only; with no terminal they fall back to plain output.
- **Editor** is `$VISUAL`, then `$EDITOR`, then `vi` (or `notepad` on Windows). `launch` uses `xdg-open` on Linux and returns 127 when it is missing.
- **Help layout**: `Usage:` line, description, `Positional arguments` (only arguments with help), `Options`, `Commands` (groups), epilog. Deprecated commands show `(Deprecated)` under the usage line. Option choices render as `[a|b]` metavars.
- **Version option** detects the version via `importlib.metadata` from the distribution name, falling back to the distribution that provides the import name.

## Not done

- **Windows argv expansion** (glob, home-directory and environment-variable expansion of the process argument list, N-000045 to N-000049 platform bullet): not implemented. The target is Linux, and the code is portable otherwise. `main(windows_expand_args=...)` is not accepted.

## Checklist status

`spec/CHECKLIST.md` lists 1015 ids (N-000001 to N-001015 in pack order). The file is part of the spec and was not edited, so status is recorded here by pack range. Ids inside each pack form a contiguous range, and the status was checked against that pack's text and the tests named below. It was not traced one id at a time, so the per-id state is inferred from the pack, not individually verified.

| Pack | Ids | Status |
|---|---|---|
| 01 | none | n/a |
| 02–04 | N-000761–N-000775 | implemented (pure Python, zero dependencies, Python 3.10+, `src/` layout) |
| 05 | N-000776–N-000787 | implemented (exports in `optlyn/__init__.py`, `optlyn.formatting.wrap_text`, `optlyn.testing.CliRunner`) |
| 06 | N-000788–N-000833 | implemented; tested in `test_optlyn.py` help/exit/version tests |
| 07 | N-000834–N-000867 | implemented; tested in FP-01/FP-06 tests |
| 08 | N-000868–N-000922 | implemented; tested in FP-03 and FP-04 tests |
| 09 | N-000923–N-000931 | implemented; tested in FP-05 tests |
| 10 | N-000932–N-000962 | implemented; tested in FP-07 tests |
| 11 | N-000963–N-000982 | implemented; tested in FP-11 tests |
| 12 | N-000983–N-001005 | implemented; tested in FP-12 tests |
| 13 | N-001006–N-001012 | implemented; tested in FP-14 tests |
| 14–18 | N-000001–N-000072 | implemented, except N-000045 to N-000049 (Windows argv expansion, see Not done) |
| 19 | N-000073–N-000102 | implemented; tested in FP-01 tests |
| 20 | N-000103–N-000164 | implemented; tested in FP-02 tests |
| 21 | N-000165–N-000272 | implemented; tested in FP-03 tests |
| 22 | N-000273–N-000317 | implemented; tested in FP-04 tests |
| 23 | N-000318–N-000374 | implemented; tested in FP-05 tests |
| 24 | N-000375–N-000423 | implemented; tested in FP-06 tests |
| 25 | N-000424–N-000473 | implemented; tested in FP-07 tests |
| 26 | N-000474–N-000517 | implemented; tested in FP-08 tests |
| 27 | N-000518–N-000581 | implemented; tested in FP-09 tests |
| 28 | N-000582–N-000607 | implemented; tested in FP-06/FP-10 tests |
| 29 | N-000608–N-000676 | implemented; tested in FP-11 tests |
| 30 | N-000677–N-000703 | implemented; tested in FP-12 tests |
| 31 | N-000704–N-000723 | implemented; tested in FP-13 tests |
| 32 | N-000724–N-000749 | implemented; tested in FP-14 tests |
| 33 | N-000750–N-000760 | implemented; tested in FP-02/FP-03/FP-06 tests |

Caveat: the choices in the conflict table decide several outcomes (deprecation channel, confirm re-ask, environment vs default-map precedence, runner directory removal, help width). If the spec is settled differently, each is a local change in the module that implements it (`core.py` for precedence, `termui.py` for confirm, `testing.py` for the runner, `formatting.py` and `core.py` for width).
