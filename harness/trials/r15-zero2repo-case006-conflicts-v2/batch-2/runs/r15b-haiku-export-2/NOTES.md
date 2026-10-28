# Implementation notes

Package: `src/optlyn` (src-layout, zero runtime dependencies, Python 3.10+).
Tests: `tests/test_optlyn_basics.py` (run with `PYTHONPATH=src python3 -m pytest tests`).
Spec ids are cited in docstrings and comments as `# spec: N-xxxxxx`.

## Module map

| module | contents |
|---|---|
| `optlyn/__init__.py` | package-root exports (Contract 1) |
| `optlyn/commands.py` | `Command`, `Group`, `CommandCollection`, declaration decorators, ready-made option decorators, `pass_*` helpers, standalone `main` |
| `optlyn/core.py` | `Context`, `Parameter`, `Option`, `Argument`, `ParameterSource` |
| `optlyn/parser.py` | token parsing, argument assignment, value-source resolution, callbacks |
| `optlyn/paramtypes.py` | parameter types (renamed from `types.py` so it does not shadow the stdlib module) |
| `optlyn/termui.py` | terminal helpers, `open_file` and lazy/atomic file wrappers |
| `optlyn/formatting.py` | usage line, help page, `wrap_text` |
| `optlyn/shell_completion.py` | `{shell}_source` scripts and `{shell}_complete` suggestions |
| `optlyn/testing.py` | `CliRunner`, `Result`, `isolated_filesystem` |
| `optlyn/exceptions.py` | `OptlynError`, `UsageError`, `BadParameter`, `MissingParameter`, `NoSuchOption`, `Abort`, `Exit`, `FileError` |

## Choices where the spec disagrees or leaves room

Unsettled contradictions listed in `spec/MAP.md` (no human verdict; `--allow-open` export):

- **CF-000146 (deprecation warning channel).** N-000081 says stdout, N-000803 (channel table) says stderr. Chose **stderr**.
- **CF-000150 (env vs default map).** N-000230 ranks environment above the default map; N-000937 says default-map values beat environment. Chose **environment, then default map** (the FP-03 ranking), so `RETRIES=7` beats `default_map={"retries": 9}`.
- **CF-000151 (confirm answer that is neither yes nor no).** N-000495 says ask again; N-001016 says it counts as no. Chose **counts as no** (N-001016).
- **CF-000152 (default metavar for an integer option).** N-000326 says the type name (`INTEGER`); N-001013 (acceptance criterion) says `--count COUNT`. Chose the **destination name uppercased** (`COUNT`), matching the criterion. Choice types show their values as the metavar.
- **CF-000153 (isolated filesystem cleanup).** N-000732 says the directory is removed when no parent is given; N-001015 says it is always left in place. Chose **removed when no parent is given; left in place when a parent path is supplied**.
- **CF-000155 (default maximum content width).** FP-02 says 80; N-001014 says 100. Chose **80** (the more specific FP-02 statement). Set with `max_content_width`.

Other choices:

- **Confirmation prompts and `prompt_required`.** `prompt_required=True` (default) prompts when the option is omitted; `prompt_required=False` prompts only when the flag is given with no value (the spec's "does not require a prompt merely because omitted").
- **Chained subcommand arguments** end at the next token that names a subcommand of the chaining group.
- **Help and version callbacks** return the value they receive, so the flag's stored value stays boolean.
- **Deprecated parameters and commands** print a `DeprecationWarning:` line to stderr when the user supplies them.
- **Automatic help option** is placed first in the active parameter list, so an author option that reuses a help name wins that name and the other help names still print help.

## Known gaps

- **Feature-switch groups** (several options sharing one destination, FP-03): not implemented. The later declaration overwrites the earlier one.
- **`CliRunner(capture="fd")`** is accepted but behaves like `capture="sys"`; OS-level descriptor capture is not implemented.
- **Pager, editor, launch, and progress bar** helpers are minimal: they follow the stated contract on the paths exercised, but were not tested on a real terminal.
- **Group-level option mixing** (`allow_interspersed_args` on groups) is only exposed as the class attribute `interspersed_args`, not as a declaration keyword.
- **Wrapping** uses `textwrap`; the first-sentence ellipsis for short help is not implemented (the first sentence is used as is).
- **Checklist status.** The `spec/CHECKLIST.md` boxes are not ticked. Coverage is by implementation plus `# spec:` markers; the 10 tests cover the main paths, not every id. Ids without a marker should be treated as not individually verified.
