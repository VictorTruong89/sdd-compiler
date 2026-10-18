# Optlyn — implementation notes

Optlyn is a pure-Python library (no runtime dependencies) for composable command-line
interfaces. The package is `src/optlyn`; it is imported with `PYTHONPATH=src`.
Python 3.10 or newer.

## Layout

| Path | Contents |
| --- | --- |
| `src/optlyn/core.py` | Parameters, `Context`, `Command`, `Group`, `CommandCollection`, the parser and value resolution |
| `src/optlyn/decorators.py` | `command`, `group`, `option`, `argument`, ready-made options, `pass_*` helpers |
| `src/optlyn/types.py` | Built-in and custom parameter types, `File`, `Path`, `Choice`, ranges |
| `src/optlyn/termui.py` | Styling, prompts, confirmation, pager, progress bar, editor, pause, clear |
| `src/optlyn/utils.py` | `echo`, `open_file`, `format_filename`, `get_app_dir`, `launch` |
| `src/optlyn/shell_completion.py` | Registration scripts (bash, zsh, fish, PowerShell) and suggestion output |
| `src/optlyn/testing.py` | `CliRunner` and `Result` |
| `src/optlyn/formatting.py` | `wrap_text` and help-layout helpers |
| `src/optlyn/exceptions.py` | `UsageError`, `BadParameter`, `MissingParameter`, `Abort`, `Exit`, ... |
| `tests/test_optlyn.py` | Behavioural tests, grouped by feature point |

Run the tests with `PYTHONPATH=src python -m pytest tests`. At the time of writing: 128 passed.

## Spec coverage

The spec has 1015 checklist ids (`spec/CHECKLIST.md`). Coverage here is by feature point and
contract section, not by individual id: each module carries `# spec:` comments naming the id
ranges it implements, and `tests/test_optlyn.py` exercises each feature point. I did not tick the
per-id boxes in `spec/`, which I left unchanged, and I did not write a test for every single id.
Ids that are knowingly not done or only partly done are listed under "Not done or partial" below.

## Decisions where the spec disagrees with itself

The export was made with `--allow-open`, so six contradictions (CF-000146, CF-000150, CF-000151,
CF-000152, CF-000153, CF-000155) have no human verdict. For each one I picked a reading and
recorded it here.

1. **Deprecation warning channel (CF-000146).** The output-channel table (N-000803) says standard
   error; N-000081 says standard output. I used **standard error**, so a deprecation warning never
   mixes into the command's stdout.

2. **Environment vs default map (CF-000150).** FP-03 and FP-07 rank the sources as command line,
   environment, default map, declared default (N-000230). The contract's Context table
   (N-000937) says default-map values beat environment variables. The PRD owns behaviour and the
   contract only fixes forms, so I used **environment above default map**.

3. **Confirm answers other than yes/no (CF-000151).** FP-08 (N-000495) says an unrecognised
   answer asks again. The contract (N-001016) says it counts as no. I used **ask again**. An empty
   answer still takes the default.

4. **Default metavar for value options (CF-000152).** The rule (N-000326) says the type name in
   uppercase. The acceptance example (N-001013) says `--count` shows as `--count COUNT`. I followed
   the **acceptance example**: a value option's default metavar is its destination name in
   uppercase. A choice type shows its values as `[a|b]`, and an author `metavar` overrides both.

5. **Isolated filesystem (CF-000153).** N-000732 says the directory is removed on exit when no
   parent is given. N-001015 says it is always left in place. I used **always left in place**, the
   later and more specific sentence. `isolated_filesystem(temp_dir=...)` creates the directory as a
   child of that path, as specified.

6. **Maximum content width (CF-000155).** N-000127 says 80 columns; N-001014 says 100. I used
   **80 by default**. The caller can raise it with `max_content_width`. An explicit `terminal_width`
   is used as the wrap width unchanged, as specified.

7. **Callback for an omitted parameter (not listed as a contradiction).** The glossary (N-000018)
   says a parameter callback is not called when the parameter was omitted and got no value. FP-03
   says "a missing parameter still runs its callback, so that callback can default from an earlier
   parameter's value." I followed **FP-03**: the callback runs and receives `None`.

8. **Group option mixing.** The spec says authors may enable mixing on a group but names no
   keyword. I expose it through the context setting `allow_interspersed_args`. With mixing on, group
   options after the subcommand name still go to the group, and the rest is forwarded to the child.

9. **Chaining sentinel.** On a chaining group, `ctx.invoked_subcommand` is `"*"` while children
   run. The contract leaves the value to the implementer; it is `None` when no child runs.

10. **Feature-switch groups.** When several options share a destination, the winner is the most
    explicit source. Ties in the default tier go to an explicit declared default over an
    auto-derived one (bare flags), then to the last declared option.

11. **Prefixes.** `/` and `+` are supported for exact flag names (for example `/force` or
    `+x`). Short-option stacking only applies to `-`.

12. **Validation at declaration.** These raise `DeclarationError` (a `TypeError`): a deprecated
    option that is also required or prompting, a deprecated required argument, a second variadic
    argument on one command, a `FloatRange` clamp with open or missing bounds, and a group added
    beneath a chaining group (raised as `TypeError`).

## Not done or partial

- **Windows argv expansion (N-000045 area).** Glob, home-directory and environment expansion of
  the process argument list on Windows is not implemented. The required target is Linux, and no
  Windows branch of this code has been exercised.
- **`getchar` (N-000648–N-000651).** Reads one character from standard input. It does not open the
  controlling terminal when stdin is a pipe, so piped bytes are consumed.
- **Pager default.** When `PAGER` is unset, output goes straight to standard output and no default
  pager such as `less` is started (N-000631 area).
- **Completion in real shells.** I ran the generated bash script under bash (`eval` of the
  source output, then the completion function) and it returned the expected suggestions. The zsh,
  fish and PowerShell scripts are generated and checked for their key parts only, not run. The
  `type,value` line format is my own choice (section 8 allows it).
- **Progress bar.** The remaining-time estimate is simple and only drawn on a terminal.
- **Editor and launch.** `edit` passes the file path as the last argument to the editor command.
  `launch` runs `xdg-open` on Linux and `open` on macOS. `locate` is honoured only as `open -R` on
  macOS.
- **Platform branches.** The macOS and Windows branches (application directory, launch, version
  detection) are written but untested here.
- **Packaging.** `pyproject.toml` declares a setuptools src-layout build with no runtime
  dependencies. I did not build or install the wheel. The judge uses `PYTHONPATH=src`, which the
  tests use as well.
