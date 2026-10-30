# Optlyn build notes

Package: `src/optlyn` (pure Python, no dependencies, Python >= 3.10). No build step; tests run with `PYTHONPATH=src`.
Own tests: `tests/` (`PYTHONPATH=src python -m pytest tests`).

## Module map (where each spec area lives)
| spec area (packs) | module |
|---|---|
| 05, 07, 08, 10, 19-22, 24, 25, 28, 31 (commands, groups, params, context, chaining, exit codes) | `core.py`, `decorators.py`, `parser.py`, `exceptions.py`, `_context_stack.py` |
| 06, 20 (help layout, version identity) | `core.py`, `formatting.py`, `decorators.py` |
| 09, 23, 27 (types, File/Path) | `types.py`, `utils.py` |
| 11, 26, 29 (terminal helpers, prompts) | `termui.py`, `utils.py` |
| 12, 30 (completion) | `shell_completion.py` |
| 13, 32 (runner) | `testing.py` |

## Contradictions in the spec and what I built
These are the six open conflicts from `MAP.md` (no human verdict) plus judgement calls.

1. **CF-000146 deprecation warning channel** (N-000081 stdout vs N-000803 stderr): built **standard error**
   (the Interface Contract channel table), emitted before the callback runs.
2. **CF-000155 max content width** (N-000127 80 vs N-001014 100): built **80**. Explicit
   `terminal_width` is used as-is; the runner pins the width to 80 as well.
3. **CF-000150 env vs default map** (N-000230 env first vs N-000937 default map beats env): built
   **command line > environment > default map > declared default** (FP-03 ordering).
4. **CF-000151 standalone confirm with other answer** (N-000495 asks again vs N-001016 counts as no): built **asks again**
   (prints an error and re-prompts; end of input aborts). Empty answer takes the default.
5. **CF-000152 metavar of an int option** (N-000326 type name `INTEGER` vs N-001013 `--count COUNT`): built
   **type name upper-cased** (`--count INTEGER`); an author `metavar` replaces it.
6. **CF-000153 isolated_filesystem cleanup** (N-000732 vs N-001015): built **removed on exit when no
   `temp_dir` is given; left in place when a parent `temp_dir` is given**.

Other choices where the text is loose:
- A single boolean flag that is present always yields `True` (flag_value defaults to `True` even with `default=True`), per FP-03.
- Env value of a non-boolean-flag-value flag: matching flag value or a true token activates; false/other tokens are treated as unset.
- `invoked_subcommand` on a chaining group about to run children is the string `"*"`.
- `main()` on a chaining group with standalone mode off returns the list of child return values even when a result callback exists (result callback is still called).
- Argument placeholder defaults to the upper-cased name (not a Choice's `{a|b}` form).
- Usage line for a group that may run without a subcommand: `[COMMAND] [ARGS]...`.
- Interactive session (pager, pause) = stdin or stdout is a TTY.
- Declaration errors raise `DeclarationError`, which subclasses `TypeError`, `ValueError` and `RuntimeError`.
- Auto help/version/help_option flags use private destinations (`__optlyn_help`, `__optlyn_version`) so an
  argument named `help` or `version` does not collide.
- Windows-only behaviour (argument glob expansion, console colour) is not implemented; Linux is the target.

## Checklist accounting
All ids in `spec/CHECKLIST.md` are treated as implemented (behaviour is in the modules above and exercised
by `tests/`) except:
- Platform/packaging statements for macOS and Windows (packs 02, 03, 17: N-000764, N-000766 partially, N-000774) – code is
  portable pure Python but only Linux was exercised; Windows argument-expansion text in pack 17 is **not done**.
- The unsettled alternatives rejected above (N-000081, N-000127/N-001014 (100), N-000937, N-001016, N-001013, N-001015): **not done** on purpose.
- The runner's "echo exactly the input read" mode is implemented via `_CHUNK_SIZE=1` on the echoing stdin wrapper.
