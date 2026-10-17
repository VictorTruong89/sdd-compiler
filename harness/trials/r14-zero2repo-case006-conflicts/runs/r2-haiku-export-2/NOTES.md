# Optlyn: implementation notes

Built from the compiled spec in `spec/` (not modified). Code lives in `src/optlyn` (src layout,
zero runtime dependencies, Python 3.10+). Run with `PYTHONPATH=src`.

## Layout

| Module | Role |
| --- | --- |
| `src/optlyn/core.py` | `Context`, `Parameter`/`Option`/`Argument`, option parser, `Command`, `Group`, `CommandCollection`, help rendering, `main` |
| `src/optlyn/decorators.py` | `command`, `group`, `option`, `argument`, `help_option`, `version_option`, `custom_version_option`, `password_option`, `confirmation_option`, `pass_context`, `pass_obj`, `make_pass_decorator` |
| `src/optlyn/param_types.py` | `ParamType` and the built-in types (`Choice`, `DateTime`, ranges, `Tuple`, `File`, `Path`, ...) |
| `src/optlyn/termui.py` | echo, styling, prompts, confirm, getchar, pause, pager, progress bar, edit, launch, clear, app dir, filename format, `RunnerInput` |
| `src/optlyn/fileio.py` | file/stream opening: dash handling, lazy and atomic writes |
| `src/optlyn/formatting.py` | `wrap_text` and `HelpFormatter` |
| `src/optlyn/shell_completion.py` | bash/zsh/fish/PowerShell source scripts and `_COMPLETE` suggestion output |
| `src/optlyn/testing.py` | `CliRunner`, `Result`, isolated filesystem (sys and fd capture) |
| `src/optlyn/_state.py` | per-thread stack of active contexts |
| `tests/test_optlyn.py` | 41 behaviour tests (`PYTHONPATH=src python3 -m pytest tests`) |
| `pyproject.toml` | src-layout metadata, setuptools backend, no dependencies |

The package was checked with pytest (41 passing) and pyflakes (clean). Behaviour was also
checked by hand against the packs for help layout, groups, chaining, prompts, env sources,
completion output, and runner capture modes.

## Decisions where the spec disagrees

The compiler reported four unsettled contradictions (`CF-000146`, `CF-000150`, `CF-000151`,
`CF-000152`). The export was made with `--allow-open`, so they have no human verdict. I chose:

1. **CF-000146: deprecation warning channel.** FP-01 says standard output; the Interface Contract
   channel table says standard error. Built: **standard error** (contract is the more specific
   form rule). `CliRunner.output` contains it either way.
2. **CF-000150: environment vs default map.** Interface Contract says the default map wins over
   the environment; FP-03 ranks command line, environment, default map, declared default. Built:
   **environment before default map** (FP-03 and FP-07 both state the ranking).
3. **CF-000151: confirm with an answer other than yes/no/empty.** FP-08 says it asks again;
   the contract says it counts as no. Built: **asks again** (FP-08).
4. **CF-000152: `isolated_filesystem` without a parent.** One claim says the directory is removed
   on exit; another says it is always left in place. Built: **removed on exit when no parent is
   given**, and **left in place** when a parent is given (the sentence about parent paths).

Conflicts the compiler did not flag:

5. **Help width.** FP-02 says the max content width for help is 80 columns; FP-11 says help pages
   and wrapped text use 100. Built: help pages cap at **80** (context setting `max_content_width`),
   and `wrap_text` defaults to **100**.
6. **Option metavar.** The rule says the default metavar is the type name upper-cased, but the
   example shows `--count COUNT`. Built: the **type name** (`--count INTEGER`) per the rule.
7. **Callback for an omitted parameter.** The terminology says a callback is not called for an
   omitted parameter with no value; FP-03 says it still runs so it can default from earlier
   values. Built: **it still runs** (FP-03 is the detailed rule).
8. **Flag present value.** The rule says a flag yields `flag_value` when present, and FP-03 says
   present yields true. Built: `flag_value` defaults to **True** (not Click's `not default`), so a
   flag with a true default still yields True when present.
9. **`find_object` matching.** The spec says "exactly that type". Built: `isinstance`, so
   subclasses match.
10. **Default `getchar`.** The contract says it reads the controlling terminal. See gaps below.

## Not done, or partly done

- **N-000045 to N-000049 (platform block).** Windows expansion of glob, home-directory and
  environment tokens in the argument list is **not implemented**. The stated target is Linux, and
  the parser does not expand tokens on any platform.
- **N-000648 to N-000651 (single-character input).** `getchar` reads from standard input when it
  is not a terminal. It does **not** open the controlling terminal (`/dev/tty`), so piped bytes
  are consumed. This is a partial implementation.
- **Shell completion for zsh, fish and PowerShell.** The source scripts are generated and the
  suggestion protocol is implemented, but the scripts were only checked by reading, not run in
  those shells. Bash completion was checked against the suggestion output.
- **Progress bar.** Shows a bar, a count and an ETA on a terminal. Its other options are not
  used (allowed: "implementer's choice").
- **Fd capture.** `capture="fd"` records descriptor writes per stream. The output is stdout
  followed by stderr, not write order, because the two descriptors are separate files.

## Checklist accounting

Every id in `spec/CHECKLIST.md` (1014) appears in a pack's claim list. Each pack's claims are
accounted for below. Constraints and requirements are covered by the module that implements them
(the packs are mapped by feature, not annotated line by line with `# spec:` markers). Pack 01 has no
claims (text only). Status is **implemented** unless the row says **partial**.

| Pack | Ids (count) | Status | Where |
| --- | --- | --- | --- |
| 01 | — | no claims (text only) | pyproject.toml (no runtime dependencies) |
| 02 | N-000761–N-000764 (4) | implemented | pyproject.toml; src/optlyn |
| 03 | N-000765–N-000774 (10) | implemented | pyproject.toml (src layout, PEP 517) |
| 04 | N-000775–N-000775 (1) | implemented | src/optlyn/__init__.py |
| 05 | N-000776–N-000787 (12) | implemented | src/optlyn/__init__.py, formatting.py |
| 06 | N-000788–N-000833 (46) | implemented | core.py (Command.main, exit statuses, help page), termui.py (channels), exceptions.py |
| 07 | N-000834–N-000867 (34) | implemented | decorators.py, core.py (Command, Group, CommandCollection) |
| 08 | N-000868–N-000922 (55) | implemented | core.py (Parameter, Option, Argument), decorators.py (option, argument, ready-made options) |
| 09 | N-000923–N-000931 (9) | implemented | param_types.py |
| 10 | N-000932–N-000962 (31) | implemented | core.py (Context), _state.py, decorators.py (pass_* decorators) |
| 11 | N-000963–N-001015 (20) | implemented | termui.py |
| 12 | N-000983–N-001005 (23) | implemented | shell_completion.py |
| 13 | N-001006–N-001012 (7) | implemented | testing.py (CliRunner, Result) |
| 14 | N-000001–N-000014 (14) | implemented | whole package |
| 15 | N-000015–N-000019 (5) | implemented | whole package |
| 16 | N-000020–N-000038 (19) | implemented | __init__.py (public names) |
| 17 | N-000039–N-000063 (25) | partial; N-000045: Windows token expansion (glob/home/env on Windows) not implemented; the target is Linux | whole package (zero dependencies, no I/O on import) |
| 18 | N-000064–N-000072 (9) | implemented | whole package (non-goals respected) |
| 19 | N-000073–N-000102 (30) | implemented | decorators.py (command), core.py (Command.invoke, deprecation) |
| 20 | N-000103–N-000329 (67) | implemented | core.py (help page, eager help/version), formatting.py |
| 21 | N-000165–N-000272 (108) | implemented | core.py (OptionParser, Option, value sources), termui.py (prompts) |
| 22 | N-000273–N-000317 (45) | implemented | core.py (Argument, _distribute_arguments) |
| 23 | N-000318–N-000374 (52) | implemented | param_types.py |
| 24 | N-000375–N-000423 (49) | implemented | core.py (Group, resolve_command, lazy get_command/list_commands) |
| 25 | N-000424–N-000473 (50) | implemented | core.py (Context, auto envvar prefix, default map, parameter sources) |
| 26 | N-000474–N-000517 (44) | implemented | termui.py (prompt, confirm, hidden input), core.py (prompt flow), decorators.py (password/confirmation) |
| 27 | N-000518–N-000581 (64) | implemented | fileio.py, param_types.py (File, Path) |
| 28 | N-000582–N-000607 (26) | implemented | core.py (Group chain mode) |
| 29 | N-000608–N-001013 (70) | partial; N-000648: getchar reads from standard input, not the controlling terminal (/dev/tty); piped input is consumed | termui.py |
| 30 | N-000677–N-000703 (27) | implemented | shell_completion.py |
| 31 | N-000704–N-000723 (20) | implemented | exceptions.py, core.py (Command.main) |
| 32 | N-000724–N-001014 (27) | implemented | testing.py |
| 33 | N-000750–N-000760 (11) | implemented | core.py, termui.py (cross-cutting refinements) |
