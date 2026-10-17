# Notes

## Status

The `optlyn` package is in `src/optlyn`. It imports with `PYTHONPATH=src` and passes pyflakes. Smoke runs covered: nested groups, chaining with a result callback, options and arguments (including `--`, variadic, multiple, tuple), environment and automatic prefix, default map, prompts, confirmation, deprecation, eager version and help, standalone exit codes, the in-process `CliRunner`, and file types.

Not covered by tests yet. No test suite was written. Parts are approximate (see "Known gaps").

## Layout

- `exceptions.py`: exit classes (`UsageError` 2, `Abort`/general 1), `BadParameter`, `MissingParameter`, `NoSuchCommand`, `Exit`.
- `types.py`: built-in parameter types and `convert_type`.
- `fileio.py`: `open_file` with stdin/stdout dash, lazy and atomic write modes.
- `context.py`: `Context`, `ParameterSource`, `get_current_context`, `pass_context`, `pass_obj`, `make_pass_decorator`.
- `params.py`: `Parameter`, `Option`, `Argument`, declaration parsing.
- `command.py`: `Command` (parsing, value resolution, callbacks, help, standalone `main`).
- `group.py`: `Group` (dispatch, chaining, lazy lookup) and `CommandCollection`.
- `decorators.py`: `command`, `group`, `option`, `argument`, ready-made help, version, password, confirmation options.
- `terminal.py`: echo, style, prompt, confirm, pager, progress bar, getchar, pause, edit, launch, clear, app dir, filename formatting.
- `formatting.py`: `wrap_text`, `ellipsize`.
- `completion.py`: `_PROG_COMPLETE` source and complete modes for bash, zsh, fish, powershell.
- `testing.py`: `CliRunner` and `Result`.

## Spec conflicts and choices

Choices made by `spec/DECISIONS.md` (these hold over the other spec parts):

1. **Isolated filesystem (PRD FP-14):** the directory is always left in place after the block, with or without a parent. It is never removed.
2. **Command deprecation warning (PRD FP-01 vs Interface Contract §2 channels):** written to standard output, ahead of the command's output. Option and argument deprecation warnings go to standard error.
3. **Default map vs environment (Interface Contract §6 vs PRD FP-03/FP-07):** precedence is command line, default map, environment, declared default.
4. **Standalone confirm (Interface Contract §7 vs PRD FP-08):** an answer other than yes, no, or an empty line counts as no and is not asked again.

Other conflicts and how they were resolved:

- **Callbacks for omitted parameters (PRD glossary vs FP-03):** the glossary says a parameter callback does not run when no source supplied a value. FP-03 says "a missing parameter still runs its callback". Built to FP-03: callbacks run for every parameter, with `None` or `()` when nothing supplied it.
- **Prompt on omitted option (PRD FP-08):** `prompt_required` defaults to True, so an omitted prompting option prompts. Setting `prompt_required=False` suppresses that; the prompt still runs when the flag is given without a value.
- **Usage-error help channel (Interface Contract §2 vs PRD FP-13):** the contract puts the missing-subcommand help page on standard error, which matches the PRD. Built to that.
- **Confirm default (PRD FP-08 vs Interface Contract §7):** an empty answer returns the caller's `default`. `confirm` defaults to False, so an empty answer is no.

## Known gaps

- Group option mixing (PRD FP-03): with mixing enabled, options after the subcommand name are not routed back to the group. They are passed to the subcommand.
- Chained subcommand boundary (PRD FP-10): a chunk ends at the next known command name, not at the first option-after-argument.
- Group arguments with a fixed arity are bound before the subcommand name. Optional or variadic group arguments are not handled specially.
- `prompt` on arguments exists, but the prompt re-ask on a bad value happens only inside the prompt helper.
- Shell completion: command and option names are suggested. Choice values, file/path completion requests, and per-parameter `shell_complete` functions are not implemented.
- Pager, progress bar, and the platform launchers (`launch`, `edit`) are minimal and only checked by reading.
- `optlyn.testing` `echo_stdin` is accepted but does not echo the reads.
- Windows environment-token expansion is not implemented.

## Next steps

1. Add a test suite under `tests/` that runs with `PYTHONPATH=src`.
2. Implement per-parameter shell completion and path completion.
3. Route post-name group options when mixing is enabled.
