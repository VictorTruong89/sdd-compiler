# NOTES

Implementation of Optlyn (`src/optlyn`), built from `spec/`. `spec/` is untouched.

Run from `/app`: `PYTHONPATH=src python -m pytest tests` (12 tests pass).

## Spec conflicts and the choice made

The export has four unsettled contradictions (`spec/MAP.md`, `--allow-open`), plus one more
disagreement found while reading. Each choice is listed with where it appears.

| Id | Disagreement | Built |
|---|---|---|
| CF-000146 | Deprecation warning on stdout (N-000081, pack 19 FP-01) vs stderr (N-000803, pack 06 channel table) | **stderr**. The channel table is the normative form; see `core._warn_deprecated`. |
| CF-000150 | Default map above env (N-000230, FP-03 ranking) vs default map beating env (N-000937, pack 10) | **env above default map**, following the explicit FP-03 ranking `prompt > command line > environment > default map > declared default`. See `resolution.resolve_param`. |
| CF-000151 | Confirm: an invalid answer re-asks (N-000495, FP-08) vs counts as no (N-001015, pack 11) | **re-asks** until yes, no, or empty (empty takes the default). See `termui.confirm`. |
| CF-000152 | Isolated filesystem removed on exit when no parent (N-000732) vs always left in place (N-001014) | **always left in place**. See `testing.CliRunner.isolated_filesystem`. |
| (extra) | Help max content width: default 80 (FP-02) vs 100 (N-001013, FP-11 and constraints) | **default 80** for help width; the caller may raise it. `core.DEFAULT_MAX_CONTENT_WIDTH`. |
| (extra) | A missing parameter's callback: runs (FP-03 "still runs its callback") vs not called (terminology, N-000019) | **runs** with the resolved value (possibly `None`/`()`). See `resolution._finish`. |
| (extra) | Option destination inference: "a name that is already a valid identifier wins" read literally, so `-v` alone gives `v`, not `verbose`. | Literal reading, per FP-03. Declare `--verbose` first or pass an explicit destination if you want `verbose`. |

Other choices the spec leaves open:

- Deprecation warning text: `DeprecationWarning: The command 'x' is deprecated.` plus the custom note.
- Completion script syntax per shell, and the suggestion line format
  (`value`, `value<TAB>help` for zsh/fish, `__file__:`/`__dir__:` markers for path requests).
- Group arguments are bound from the tokens before the subcommand name; variadic group arguments are not supported.
- Chain mode: each child parses its own options first, then its arguments, and the next command name follows.
- Help is written to stdout for an intentional `--help` (exit 0), and to stderr for missing-subcommand help (exit 2).
- `get_app_dir` on Windows uses `%APPDATA%` (the spec gives no Windows rule).

## Checklist accounting

`spec/CHECKLIST.md` lists 1014 ids (N-000001 to N-001015). I have
**not** edited the checklist. Status:

- **Implemented:** every pack 01–33 feature is present in code at the level of its normal and
  error behaviour, with `# spec:` comments on the non-obvious rules.
- **Tested:** only a sample. `tests/test_optlyn.py` covers 12 flows: command names, option and
  argument delivery, usage errors, group no-args, help exit codes, env prefix and default map,
  chaining with result callback, prompts, confirmation, choices, completion, and wrapping.
  Individual ids were **not** checked one by one, so "implemented" is not a per-id claim of
  verification.

## Known gaps (not done, or done partially)

- `CliRunner(capture="fd")` is accepted but does not capture OS-level writes on descriptors 1 and 2; only interpreter writes are recorded.
- Progress bar: no remaining-time estimate, no terminal redraw beyond a counter; `**options` are ignored.
- Mixing group options after the subcommand name (opt-in, N-000186) is not implemented.
- Feature-switch groups (several options sharing a destination): simplified rule, last present occurrence wins, then last declared. The full tier ranking is not implemented.
- Optional-value options are only recognised when `is_flag=False` and `flag_value=` is given explicitly.
- Windows argument glob expansion is not implemented.
- Lazy write errors: the general error class is raised at first I/O, but work-skipping after such a failure is not fully checked.
- Pager: runs `$PAGER` as a subprocess; style handling is a simple strip-or-keep.
- Completion scripts are minimal. Path requests are emitted as `__file__:`/`__dir__:` lines, but the generated scripts do not act on those markers (bash uses `-o default`, which gives file completion).
- `launch` uses `xdg-open` on Linux and `open` on macOS; `locate` is ignored.
- `prompt` does not implement `value_proc`.
- Parameter types: `Tuple` with `multiple` works; `Path` `executable` checks are basic.
