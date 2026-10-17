# Optlyn — implementation notes

Layout: `src/optlyn/` (pure Python, no runtime dependencies, Python 3.10+).
Tests: `tests/test_optlyn.py` (run with `PYTHONPATH=src python3 -m pytest tests`).

## Where the spec disagrees with itself, and what was built

| # | Where | Disagreement | Built |
|---|-------|--------------|-------|
| 1 | PRD FP-01 vs Interface Contract §2 (channels) | PRD says a deprecation warning goes to standard output; the channel table says standard error. | Standard error (`echo(..., err=True)`), so the command's own output stays clean. |
| 2 | PRD FP-08 vs Interface Contract §7 (`confirm`) | Contract: an answer other than yes/no/empty counts as no. PRD: any other answer asks again. | Asks again (PRD). The Contract itself defers behaviour to the PRD. |
| 3 | PRD FP-02 vs FP-11 (maximum content width) | FP-02 says 80 columns; FP-11 says 100. | Help pages cap auto-detected width at 80 (`max_content_width` default). `wrap_text` defaults to 100 (FP-11). Both can be changed by the caller. |
| 4 | PRD terminology and FP-03 (callback for an omitted parameter) | Terminology: a callback is not called for an omitted parameter with no value from any source. FP-03: a missing parameter still runs its callback so it can default from an earlier one. | Callbacks run for every declared parameter, with `None` (or `()` for repeatable/variadic) when there is no value. This keeps the FP-03 feature working. |
| 5 | PRD FP-02 (default metavar) | The rule says the type name in uppercase; the example says `--count COUNT`. | Type name: `--count INTEGER` (`TEXT`, `FLOAT`, `BOOLEAN`, `UUID`; choices show `[a|b]`). An author `metavar=` replaces it. |
| 6 | PRD FP-14 (isolated filesystem) | "Removed on exit when no parent" vs "always left in place". | Removed when no `temp_dir` is given (as the first sentence says); with `temp_dir` the directory is created under it and left in place. |
| 7 | Interface Contract §6 (`Context.invoke`) | "Supplies exactly the caller's chosen values" vs a callee that needs its other parameters. | `invoke` fills the declared defaults of the target's parameters that the caller did not pass (not converted, no source reported). `forward` passes the caller's values. |
| 8 | PRD FP-08 (`prompt_required`) | Wording does not give a default. | `prompt_required=True` (prompt when the option is omitted), matching the common reading; `prompt_required=False` prompts only when the flag is given without a value. |
| 9 | PRD FP-12 (unknown completion instruction) | Says the process prints neither script nor suggestions; exit status not stated. | Prints nothing, returns status 1 (the callback does not run). |
| 10 | Interface Contract §8 (completion output) | Output form is the implementer's choice. | `type,value` lines (`plain`, `file`, `dir`), with a tab and the help text for zsh and fish. |

## Other choices

- Exception classes: `UsageError` (exit 2) with `BadParameter`, `MissingParameter`, `NoSuchOption`, `BadOptionUsage`, `BadArgumentUsage`, `NoArgsIsHelpError`; `FileError` and `OptlynError` (exit 1); `Abort`; `Exit`. Invalid declarations raise `TypeError`; an invalid colour raises `TypeError`.
- Usage errors name the parameter by its declared flags (`'--a' / '--b'`) or its argument name (`'name'`).
- Group subcommands are listed sorted. Hidden commands and options are omitted from help and completion but still parse.
- A group with `allow_interspersed_args` passes unknown option tokens on to its subcommand instead of failing.
- Token normalization (`token_normalize_func`) applies to option names, choice values and command names.
- Chaining: `ctx.invoked_subcommand` is `CHAIN_SUBCOMMAND` (not a child name) when a chain is running.
- The completion variable is `_<PROG>_COMPLETE` (upper-case, `-` becomes `_`); `complete_var=` overrides it.
- `CliRunner(capture="fd")` records OS-level writes to descriptors 1 and 2. The combined `output` is stdout followed by stderr, because the two cannot be interleaved in order.

## Known limits

- `launch`, `edit` and `getchar` depend on the desktop and terminal; `getchar` reads `/dev/tty` when standard input is the real one, otherwise standard input.
- The progress bar is a plain text bar (no custom widths or styles).
- Windows argument globbing is basic (`glob` on tokens that contain wildcards).
- Completion scripts are compact: they cover the suggestion flow, not every shell feature (for example, PowerShell completes only plain values).
