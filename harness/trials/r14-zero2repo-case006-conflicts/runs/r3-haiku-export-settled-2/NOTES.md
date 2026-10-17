# Optlyn — implementation notes

Build: pure Python package at `src/optlyn`, zero runtime dependencies, Python 3.10+.
Tests: `tests/` (run with `PYTHONPATH=src python -m pytest tests`).
Each implemented spec id carries a `# spec: N-xxxxxx` comment beside the code that satisfies it.

## Settled conflicts (spec's own rulings applied)

- CF-000146 (deprecated command warning): written to **stdout**, ahead of the command's output.
  Option and argument deprecation warnings stay on stderr.
- CF-000150 (value order): command line, then **default map**, then environment, then declared default
  (the Contract's `default_map` row wins over the PRD's ranking).
- CF-000151 (standalone `confirm`): an answer other than yes/no/empty counts as **no** and is not asked again.
- CF-000152 (isolated filesystem): the directory is always left in place, with or without a parent.

## Choices where the spec is open or conflicting

- **Callbacks for omitted parameters.** Terminology says a parameter callback is not called when a parameter is
  omitted with no value; FP-03 says "a missing parameter still runs its callback". Built: callbacks run (FP-03,
  the more specific rule, and it lets a callback default from an earlier parameter).
- **Max content width.** FP-02 says help defaults to 80 columns; N-001013 says help and wrapped text use 100.
  Built: help pages cap at 80 (FP-02 is the feature point for help, and the Contract defers defaults to the PRD);
  `wrap_text` caps at 100 when its width is not given.
- **Default metavar.** The rule is "the type name in uppercase" (`INT` renders `INTEGER`). The example in
  FP-02 shows `--count COUNT`, which that rule does not produce. Built: the rule.
- **Prompt triggers.** `prompt_required=True` (default) prompts when the value is omitted; `prompt_required=False`
  prompts only when the flag is given without a value, or when the option is also required. A value from the
  environment skips the prompt. A declared or default-map value is shown as the prompt default.
- **`invoke` defaults.** `ctx.invoke(cmd, **values)` fills declared parameters that were not supplied with their
  defaults (so the callback can be called) and does not convert or track the supplied values.
- **`getchar`** reads `/dev/tty` on POSIX even when stdin is piped. With no controlling terminal it raises
  `EOFError`. Under `CliRunner` it reads from the runner's input.
- **Chaining group return value.** In non-standalone mode a chaining group returns the list of child return
  values whether or not a result callback is registered.
- **Hidden-input prompts** write a newline (no value) to the output when stdin is not a terminal.
- **Max content width** is a caller setting (`max_content_width`). Explicit `terminal_width` is the wrap width as-is.
- **Eager flags.** Eager parameters are processed first, in the order typed. A required option that is missing
  does not stop an eager help or version flag from running.
- **Feature switches.** Options that share a destination pick a winner by source rank (prompt, command line,
  environment, default map, declared default), then non-auto default, then last declared.
- **Truthy default on a non-boolean flag** selects that flag's `flag_value` (Click's feature-switch rule).
- **Argument `required`** defaults to true unless a default is given or the arity is variadic (`-1`).
- **`--` handling.** `--` ends option parsing. For non-interspersed commands, a `--` that appears after the first
  positional stays a positional token (the parser stops at the first positional there).
- **Usage-error exit class** is 2 for every usage failure, including a group or command run with no arguments
  under no-args-is-help (the help page goes to standard error first).
- **Prompts in shell completion** are suppressed while parsing for completion (resilient parsing).
- **Shell completion output** is one `kind,value` line per suggestion (`plain`, `file`, `dir`), with a tab-separated
  help string for zsh and fish. Script syntax is ours.
- **Windows-only behaviour.** `os.startfile`, `msvcrt.getwch` and the APPDATA lookup are written but not exercised
  here. The argv glob, home and environment expansion that pack 17 describes for Windows is **not implemented**.
  The target is Linux.

## Implementation status

- Pure Python 3.10+ package in `src/optlyn`, zero runtime dependencies, `pyproject.toml` with a setuptools backend.
- Test suite: `tests/` (83 tests). Run `python3 -m pytest -q tests` from `/app`.
- Checklist ledger: `SPEC_COVERAGE.md`. Every id is listed by pack with the modules that implement it. Code comments
  anchor 295 of the 1014 ids directly. The one id marked not done is the Windows argv expansion in pack 17.
