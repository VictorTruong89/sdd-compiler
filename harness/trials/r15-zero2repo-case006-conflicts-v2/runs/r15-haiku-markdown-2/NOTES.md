# Optlyn — implementation notes

Optlyn is a pure-Python library under `src/optlyn` (import package `optlyn`, no runtime
dependencies, Python 3.10+). Tests run with `PYTHONPATH=src`; `tests/test_optlyn.py` holds
a focused regression set (`PYTHONPATH=src python -m pytest tests`).

Layout:

| module | role |
| --- | --- |
| `exceptions.py` | usage / abort / general / exit classes and their exit statuses |
| `param_types.py` | built-in types, `Choice`, `DateTime`, ranges, `Tuple`, `File`, `Path`, `convert_type` |
| `utils.py` | echo/style/prompt/confirm/getchar/progress/edit/launch/app dirs/file opening/pager, thread-local context stack |
| `formatting.py` | `wrap_text` and two-column help layout |
| `core.py` | `Context`, `Parameter`/`Option`/`Argument`, `Command`, `Group`, `CommandCollection`, parser, value resolution, help |
| `decorators.py` | `command`, `group`, `option`, `argument`, ready-made options, `pass_*` |
| `shell_completion.py` | completion instructions, suggestions, registration scripts |
| `testing.py` | `CliRunner` and `isolated_filesystem` |

## Where the specification disagrees, and what was built

1. **Deprecation warning channel.** PRD FP-01 puts it on standard output; the Interface
   Contract's channel table puts it on standard error. Built: standard error (the contract
   is the more specific interface statement).
2. **Help width.** PRD FP-02 says help caps the auto-detected width at 80 columns; PRD FP-11
   says help pages and wrapped text use 100. Built: help pages cap at 80 (`max_content_width`
   default), an explicit `terminal_width` overrides the cap; the `wrap_text` helper defaults to 100.
3. **Default option metavar.** PRD FP-02 says "the type name in uppercase", but its own
   example renders an integer `--count` as `--count COUNT`. Built: the destination name in
   uppercase (matching the example); choice types show `[a|b]`; an author `metavar` overrides.
4. **Callbacks for omitted parameters.** The PRD Terminology section says a parameter callback
   is not called for a parameter omitted with no value from any source; FP-03 says a missing
   parameter still runs its callback so it can default from earlier values. Built: FP-03.
   Every declared parameter's callback runs; it receives `None` (or `()`, `0`, `False`) when
   no source supplied a value.
5. **Isolated filesystem.** The runner spec says the directory is removed on exit when no
   parent is given and also that it is "always left in place". Built: removed when no
   `temp_dir` is given; left in place when a parent path is supplied.
6. **Prompt triggering.** A prompting option prompts when its flag is present without a value,
   or when it is required and no environment, default-map, or declared default supplies a value.
   A fully omitted, non-required prompting option uses its default and does not prompt.
   An environment value always skips the prompt. Declared and default-map values are shown as
   the prompt default when a prompt does run.
7. **Missing command vs. no-args help.** Group with no tokens under the default policy prints
   help to stderr and exits 2 with no extra error line. Group options with no subcommand report
   `Missing command.`, not the help page (FP-06 vs FP-02 wording), exit 2.
8. **Feature-switch groups.** Options sharing one destination resolve by source rank
   (prompt > command line > environment > default map > declared default > auto-derived flag
   default), and ties go to the later declaration.
9. **Declaration errors.** Invalid combinations (deprecated + required/prompt, deprecated
   required argument, clamp with an open float bound, nested group under a chaining group)
   raise at declaration. `TypeError` for option/argument refusals, `ValueError` for the
   clamp-bound combination.
10. **Completion wire format** (implementer's choice, documented here):
    plain suggestions are one value per line; zsh adds `:help`, fish adds a tab and help;
    path requests are `<file> <incomplete>` or `<dir> <incomplete>` lines.
    An unknown `_<PROG>_COMPLETE` value prints an error to stderr and exits 1.
11. **Version detection.** `version_option` uses the installed distribution named by
    `package_name` (defaulting to the program name); if that is not a distribution name it
    is treated as an import name and resolved via `importlib.metadata.packages_distributions()`.
    A module's own `__version__` is not consulted.

## Known gaps (not implemented)

- `CliRunner(capture="fd")` is accepted but behaves like `"sys"`: OS-level descriptor
  capture is not implemented.
- Group mixing (`allow_interspersed_args=True` on a group) is not implemented: group
  options still must precede the subcommand name even when mixing is enabled.
- Windows glob / home / environment expansion of argv tokens is not implemented.
- `edit`, `launch`, `echo_via_pager`, and `getchar` are implemented against the platform
  tools but only exercised for their non-interactive paths.
- The completion scripts are compact and exercised only through the `*_complete` side;
  they are not tested in a real shell.
