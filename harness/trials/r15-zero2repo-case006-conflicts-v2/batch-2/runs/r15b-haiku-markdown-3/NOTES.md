# Optlyn — implementation notes

The package lives in `src/optlyn` (import with `PYTHONPATH=src`). It has no runtime
dependencies and needs Python 3.10 or newer.

## Layout

| module | contents |
| --- | --- |
| `optlyn/core.py` | `Context`, `Parameter`/`Option`/`Argument`, option parser, `Command`, `Group`, `CommandCollection` |
| `optlyn/decorators.py` | `command`, `group`, `option`, `argument`, help/version/password/confirmation options, pass-context helpers |
| `optlyn/types.py` | built-in parameter types (`STRING`, `INT`, `Choice`, `File`, `Path`, …), `CompletionItem` |
| `optlyn/termui.py` | echo, styling, prompts, confirm, pager, progress bar, editor, pause, clear |
| `optlyn/utils.py` | file opening (lazy and atomic), app-dir lookup, filename formatting, launch |
| `optlyn/formatting.py` | `wrap_text` and the help formatter |
| `optlyn/shell_completion.py` | bash/zsh/fish/PowerShell registration scripts and suggestion output |
| `optlyn/testing.py` | `CliRunner` (sys and fd capture) and `Result` |

## Where the specification disagrees with itself, and what was built

1. **Deprecation warning channel.** FP-01 says the command deprecation warning goes to
   standard output. The Interface Contract's channel table says standard error. Built:
   standard error, for commands, options and arguments alike.

2. **Callbacks for omitted parameters.** The terminology says a parameter callback is not
   called when the parameter was omitted and received no value. FP-03 says a missing
   parameter still runs its callback, so the callback can default from an earlier
   parameter. Built: every parameter's callback runs, with `None` (or `()`) when it has no
   value. Eager parameters run first, then the rest in declaration order.

3. **Confirm answers other than yes/no/empty.** Contract §7 says such an answer counts as
   "no". FP-08 says it asks again. Built: asks again (the PRD governs behaviour; the
   contract governs shape).

4. **Maximum content width.** FP-02 says help uses 80 columns by default. FP-11 says help
   and wrapped text use 100. Built: help pages cap auto-detected width at 80
   (`Context.max_content_width` overrides it); `wrap_text` defaults to 100.

5. **Isolated filesystem.** The runner section says the directory is removed on exit when
   no parent is given, and also that it is "always left in place". Built: removed on exit
   when `temp_dir` is not given; left in place when `temp_dir` is given. The working
   directory is restored in both cases.

6. **Version of an undetectable package.** Built: `version_option` prints `unknown` when
   neither the distribution nor a providing distribution can be found. Without a
   `package_name` the lookup uses the program name.

7. **Completion-variable name.** The variable is built literally from the program name
   (upper-cased, dashes to underscores). A name with a dot, such as `tool.py`, therefore
   gives `_TOOL.PY_COMPLETE`, which a shell cannot set. Console-script names have no
   extension, so this does not arise in practice.

## Known limitations

- Completion functions receive a context whose `params` is empty. Values parsed earlier on
  the command line are not yet available to them.
- In `CliRunner(capture="fd")` the combined `output` is stdout followed by stderr; their
  interleaving order is not preserved.
- Windows-only behaviour (glob expansion of arguments, `startfile` launching, PowerShell
  registration) is written but was not exercised in this environment.
- Chained subcommands are parsed before the group callback runs, so a chained child's
  prompt or parse error appears before the group callback output.
