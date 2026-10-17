# Implementation notes

Optlyn is built from `spec/` as a pure-Python package under `src/optlyn`. Run with
`PYTHONPATH=src`. There is no build step; `pyproject.toml` is provided for an optional editable install.

## Conflicts in the specification and what was built

Decisions from `spec/DECISIONS.md` were applied as written:

1. **Isolated filesystem (FP-14 vs DECISIONS 1).** The FP-14 text would remove the directory when no parent is
   given. DECISIONS says it is never removed. Built: `CliRunner.isolated_filesystem` never removes it.
2. **Command deprecation warning (FP-01 vs channels table).** Built: the command warning goes to stdout, ahead of
   the command's output. Option and argument warnings go to stderr.
3. **Default map vs environment (Interface Contract §6 vs FP-03/FP-07).** Built: command line, then default map,
   then environment, then declared default.
4. **Standalone confirm (Interface Contract §7 vs FP-08).** Built: an answer other than yes, no, or an empty line
   counts as no and is not asked again. `confirm(..., abort=True)` aborts on that result.

Other conflicts, decided by me:

5. **Callbacks for omitted parameters (FP-01/glossary vs FP-03).** The glossary says a parameter callback is not
   called when it is omitted and has no value. FP-03 says a missing parameter still runs its callback so it can
   default from an earlier parameter. Built: the callback runs for every declared parameter, and it receives
   `None` when no source supplied a value. This keeps the "default from an earlier parameter" use case working.
6. **Help wrap width (FP-02 vs FP-11).** FP-02 says the maximum content width defaults to 80. FP-11 says 100.
   Built: 80 for help pages, which is the more specific rule. `wrap_text` itself defaults to 78 columns.
7. **Module name `types`.** The package module is `optlyn/param_types.py`, so it cannot shadow the standard
   library `types` when the package directory is on `sys.path`.
8. **Windows application directory.** The spec does not give one. Built: `%APPDATA%\<app name>`.
9. **Internal names of built-in help and version flags.** They use the destinations `__optlyn_help__` and
   `__optlyn_version__`, so that an author parameter named `help` does not collide with them.

## Known gaps

- `CliRunner(capture="fd")` is accepted, but it uses interpreter-stream capture. OS-level descriptor capture is not
  implemented.
- Feature-switch groups (several options sharing one destination) are not resolved by explicitness. The last
  declared one wins.
- Completion output for path requests uses the form `__optlyn_path_file__ TOKEN` or
  `__optlyn_path_dir__ TOKEN`. The shell scripts do not translate these into native path completion.
- `edit`, `launch`, pager, and `getchar` are minimal and were not exercised beyond basic smoke checks.
- Chained subcommand arguments are split at the first positional token that the arguments cannot consume.
