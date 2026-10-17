# Optlyn — implementation notes

Pure-Python package `optlyn` under `src/optlyn`, Python 3.10+, no runtime
dependencies. Import with `PYTHONPATH=src` (or an editable install).

## Spec conflicts and the choice made

1. **Deprecation warning channel.** `Interface_Contract.md` (channel table)
   says standard error; `Full_PRD.md` FP-01 says standard output. Built:
   **standard error**, so stdout stays clean for command output.
2. **Callbacks for omitted parameters.** The PRD glossary says a parameter
   callback is not called for a parameter omitted with no value from any
   source. FP-03 says a missing parameter still runs its callback so it can
   default from an earlier value. Built: **the callback runs** (FP-03 is the
   more specific rule).
3. **Isolated filesystem.** FP-14 says the runner removes the directory when
   no parent is given, and also that the directory is "always left in place".
   Built: **removed on exit when no `temp_dir` is given; left in place when a
   parent is given.**
4. **Chained groups.** Subcommands are parsed (split from the line) before the
   group callback runs, so a usage error in any subcommand stops the chain
   before any callback. For non-chained groups the group callback runs before
   the child is parsed, so child help is shown after the group callback
   (FP-06).
5. **Feature-switch winner.** Among command-line occurrences of options that
   share a destination, the last one on the line wins. Ties in the default tier
   fall back to declaration order as the PRD states.
6. **Prompting.** A prompt runs when the flag is given without a value, or when
   the option is required and no command-line or environment value exists. An
   omitted, non-required prompting option does not prompt and uses its default.
   Declared defaults and default-map values are shown as the prompt default.
7. **Eager flags.** Eager parameters are processed first, in the order the user
   typed them. A help or version flag that exits therefore wins over missing
   required options.
8. **Flag defaults.** A bare flag yields `True` when present, regardless of its
   default; the default only applies when the flag is omitted.

## Interface choices not fixed by the contract

- Module `types.py` is named `param_types.py`. A module named `types` inside the
  package shadows the standard library when a script is run from that directory.
- `Group.result_callback()` is the decorator the contract names. The registered
  function is stored in `Group.result_callback_func`.
- A plain tuple of types, such as `type=(str, int)`, is accepted as shorthand
  for `Tuple((str, int))`.
- The automatic help option has the internal destination `_optlyn_help`, so it
  cannot collide with a parameter named `help`.
- A group allows option mixing when its context setting
  `allow_interspersed_args=True` is given. Leaf commands mix options and
  arguments by default.
- `ctx.invoke(cmd, **values)` passes exactly the given values and fills nothing
  in. `ctx.forward(cmd, **values)` fills the target from this context's values.
- Completion output is one suggestion per line as `type,value`. Zsh and fish
  append `\t<help>`. `type` is `plain`, `file` or `dir`. An unrecognised
  `_<PROG>_COMPLETE` value prints nothing and exits with status 1.
- In non-standalone mode, `Command.main` returns the exit code of an
  `Exit` (for example after help) instead of raising.

## Known limits

- `CliRunner(capture="fd")` is accepted but uses the same interpreter-stream
  capture as `"sys"`; OS-level descriptor capture is not implemented.
- `progressbar` is a minimal text bar (no ETA formatting refinements).
- `edit` and `launch` use the editor and opener command lines and do not
  implement Windows-specific handling beyond `os.startfile`.
- On Windows, glob and home-directory expansion of the argument list is not
  performed.
- `getchar` reads from `/dev/tty` and falls back to standard input when no
  controlling terminal is available.
