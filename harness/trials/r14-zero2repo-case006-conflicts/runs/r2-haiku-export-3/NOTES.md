# Optlyn: build notes

Implementation of the Optlyn specification in `spec/` (33 packs, 1014 claim ids).
Code lives in `src/optlyn/`, tests in `tests/`. Run with `PYTHONPATH=src python3 -m pytest tests`.

## Status

- Built: the public surface in Interface Contract §1 (all listed names exported), declaration
  (`command`, `group`, `option`, `argument`, ready-made options), parsing, value sources and
  ranking, defaults, environment variables, default map, callbacks, eager help/version,
  groups with lazy `get_command`, command collections, chaining with result callbacks,
  types (`Choice`, `DateTime`, `IntRange`, `FloatRange`, `Tuple`, `File`, `Path`, custom
  `ParamType`), prompts and confirmation, terminal helpers, invocation context, shell
  completion (registration and suggestion modes), and `optlyn.testing.CliRunner`.
- Tests: 29 in `tests/test_optlyn.py`, each named after the node id it covers. All pass.
- Not every one of the 1014 ids is individually verified. Several areas are approximate or
  missing; see "Not done or partial" below. `spec/` is untouched; I did not tick
  `CHECKLIST.md`.
- `# spec:` markers are at module level (docstrings), not beside each satisfying line.

## Choices where the spec disagrees with itself or leaves a form open

Unsettled contradictions (the export marked these open):

1. **CF-000146, deprecation warning channel.** N-000081 says stdout, N-000803 (Interface §2
   channels table) says stderr. Built: **stderr**, following the channel table.
2. **CF-000150, environment vs default map.** N-000230 (FP-03 ranking) puts environment
   above the default map. N-000937 (Interface §6) says default-map values take precedence over
   environment. Built: **FP-03 ranking** (prompt, command line, environment, default map,
   declared default).
3. **CF-000151, confirm with an answer other than yes/no/empty.** N-000495 says ask again;
   N-001015 says count it as no. Built: **ask again** (N-000495).
4. **CF-000152, isolated filesystem removal.** N-000732 says remove a no-parent directory on
   exit; N-001014 says always leave it in place. Built: **always leave it in place**.

Other choices:

5. **Max content width.** FP-02 says 80 by default; the cross-cutting constraint N-001013 says
   100. Built: default **80**. The caller can raise it through `max_content_width`. An explicit
   `terminal_width` is used as-is.
6. **Callback for an omitted parameter with no value.** The Terminology glossary says the
   callback is not called; FP-03 says it is. Built: **the callback runs** (FP-03 behaviour).
7. **Destination inference.** The spec says an identifier-valid name wins, in declaration order.
   So `-v, --verbose` gives destination `v`, and `--verbose, -v` gives `verbose`. Built as
   written.
8. **Optional-value options.** The spec has no keyword for them. Built: a non-flag option with
   `flag_value=` takes an optional value. Alone it yields `flag_value`. With one token it yields
   that token.
9. **`prompt_required`.** The spec does not say whether a prompting option prompts when fully
   omitted. Built: default **False** (no prompt when omitted). `password_option` sets it True.
   A required prompting option prompts when omitted.
10. **Feature-switch ties.** Built: the most explicit source wins, and a tie goes to the last
    declared option. The "auto-derived default loses to explicit default" refinement is not
    implemented.
11. **Chaining argument boundaries.** A chained child takes tokens up to the next command name.
    A child with a variadic argument takes the rest of the line.
12. **Standalone exit codes.** Success exits `SystemExit(0)`. Clean stop uses its status. Usage
    errors exit 2. Abort and file errors exit 1. With standalone mode off, a clean stop returns
    its status as an int.
13. **Help headings.** `Positional arguments:`, `Options:`, `Commands:` (text is the
    implementer's choice).
14. **Completion wire format.** Path requests are lines `__optlyn_path__:<dir|file>:<incomplete>`.
    Zsh and fish lines are `value<TAB>help`.
15. **Env prefix path.** The prefix path uses subcommand names below the top command, per FP-07.

## Not done or partial

- Windows argv glob and environment expansion (N-000045 area): not implemented.
- A lazy write file that fails at first I/O raises a raw `OSError`. It should become a general
  `FileError` naming the path (FP-09).
- Completion scripts are written but have not been run in real shells. Bash and zsh logic is the
  least verified.
- `progressbar`: a basic bar with ETA. Extra `**options` are ignored.
- `launch`: only `open` (macOS) and `xdg-open` (others) are wired. `locate` is honoured only on
  macOS.
- `edit`: uses `$VISUAL`, `$EDITOR`, then `vi`. The `require_save` check compares contents.
- `getchar`: reads `/dev/tty` where available, else stdin. Piped stdin is not consumed in the tty
  path.
- Pager: runs `$PAGER` through a shell only when interactive. It does not strip styles per
  destination.
- Interactive-session detection (N-000982 area) is the stdin/stdout tty check only.
- Thread-local current context works. Entering a context on another thread is supported by
  `with ctx:`, but not tested.
- `Parameter` callbacks are run for every resolved parameter, including those that receive no
  value. Deprecation messages for options and arguments are generic.
