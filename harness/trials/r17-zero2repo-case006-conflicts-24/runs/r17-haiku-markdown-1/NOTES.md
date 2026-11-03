# Implementation notes

Package: `optlyn`, in `src/optlyn/` (import with `PYTHONPATH=src`). Pure Python 3.10+,
no runtime dependencies. `spec/` is unchanged.

Layout:

| module | role |
| --- | --- |
| `core.py` | `Context`, `Parameter`/`Option`/`Argument`, `Command`/`Group`/`CommandCollection`, parser, value pipeline, declaration decorators |
| `param_types.py` | parameter types (`STRING`, `INT`, `Choice`, `File`, `Path`, ...) |
| `termui.py` | echo, styling, prompts, confirm, pager, progress bar, editor, launch |
| `formatting.py` | usage line, help page, `wrap_text` |
| `shell_completion.py` | registration scripts (`<shell>_source`) and suggestion output (`<shell>_complete`) |
| `testing.py` | `CliRunner`, `Result`, `isolated_filesystem` |
| `utils.py` | file helpers (`open_file`, lazy and atomic files, `-` streams), `get_app_dir`, `format_filename` |
| `exceptions.py` | `UsageError` (exit 2), `Abort` (exit 1), `Exit`, `FileError` (exit 1) |

Module naming: the type module is `param_types.py`, not `types.py`, so it does not shadow
the standard library `types` when Python runs from inside the package directory.

## Where the spec disagrees, and what was built

1. **Omitted counting option.** PRD FP-03 says zero when omitted; Interface §2 says `None`.
   Built: `0` (or the author's integer default).
2. **Callback for an omitted parameter.** PRD glossary says a parameter callback is not called
   when the parameter got no value from any source; FP-03 says "a missing parameter still runs
   its callback". Built: the callback runs for every parameter, receiving `None`, `()` or the
   default.
3. **Default metavar for typed options.** PRD FP-02 gives `--count COUNT` as the example, but
   its rule says "the type name in uppercase". Built: the rule, so an integer option shows
   `--count INTEGER`.
4. **Help width.** FP-02 says the maximum content width is 80; FP-11 says 100. Built: 80.
5. **App config directory on Unix.** FP-11 honours `$XDG_CONFIG_HOME`; Interface §7 says always
   `~/.config`. Built: `$XDG_CONFIG_HOME` when set, otherwise `~/.config`.
6. **`IntRange` clamp on an open bound.** PRD: the adjacent integer inside the range.
   Interface: the bound's value. Built: the PRD behaviour (e.g. `min_open` clamps `0` to `1`).
7. **`FloatRange` clamp with an open bound.** PRD: a declaration error. Interface: clamp to the
   bound. Built: `ValueError` at construction.
8. **`DateTime` with several matching formats.** PRD: the first success wins. Interface: the last
   matching format. Built: first match wins.
9. **`Path(resolve_path=True)` and `~`.** PRD: a leading tilde is not expanded. Interface: it is
   expanded. Built: not expanded.
10. **Docstring form feed.** PRD: text after `\f` is omitted from help. Interface: the `\f`
    is dropped and the text kept. Built: truncate at `\f` (PRD).
11. **`show_default` on a flag whose default is off.** PRD: hidden. Interface: shown for every
    option. Built: hidden (PRD).
12. **Group listing short help.** PRD: the first sentence, ellipsized at the wrap width.
    Interface: the first paragraph, cut with `...` at 45 characters. Built: the first sentence,
    cut to 45 characters with `...`.
13. **Completion of an empty token.** Interface §8 lists option names after subcommand names
    for an empty token; PRD FP-12 lists options only after a dash has been typed. Built: PRD.
14. **`CliRunner.isolated_filesystem` cleanup.** The spec says the runner "removes that directory
    on exit" when no parent is given, and also that the directory is "always left in place after
    the block ends". Built: left in place after the block; with no `temp_dir` it is removed at
    interpreter exit (`atexit`), and with `temp_dir` it is kept.
15. **`pause` when not interactive.** PRD: does nothing. FP-11: prints its message and does not
    block. Built: prints the message and does not block.
16. **`Context.invoke` / `forward` values.** Declared parameters supplied to `invoke` are passed
    through unconverted and tagged `COMMANDLINE`; `forward` copies the caller's current values.

## Limitations

- `capture="fd"` in `CliRunner` records descriptor writes, but its `output` is stdout followed by
  stderr, not interleaved in write order.
- Windows argv glob and environment expansion (PRD NFC) and the Windows single-key input path are
  not implemented; `getchar` uses `/dev/tty` with a raw read and falls back to stdin.
- The shell completion scripts are minimal and were not run in real bash, zsh, fish or PowerShell.
  The suggestion stream was checked directly.
- Interactive helpers (`edit`, `launch`, `pager`, `getchar`) are implemented but only exercised
  in non-interactive form.
