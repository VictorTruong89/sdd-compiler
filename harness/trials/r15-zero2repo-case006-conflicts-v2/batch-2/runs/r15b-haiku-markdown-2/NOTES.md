# Implementation notes

Optlyn is built from scratch under `src/optlyn` (src layout, zero runtime
dependencies, Python 3.10+). `pyproject.toml` is a PEP 517 setuptools build.
Nothing is installed or built by the judge; `PYTHONPATH=src` is enough.

Where the specification disagrees with itself, the choice below was made.

## Conflicts between spec documents

1. **Deprecation warning channel.** PRD FP-01 says standard output; the
   Interface Contract channel table says standard error. Built: standard
   error (the contract's channel table is the more specific statement).

2. **Parameter callbacks for omitted parameters.** The PRD glossary says a
   parameter callback is *not* called when a parameter was omitted and had no
   value; FP-03 says "a missing parameter still runs its callback, so that
   callback can default from an earlier parameter's value". Built: the callback
   always runs (with `None`, `()`, `False` or `0` for an omitted parameter),
   which is what FP-03's explicit example needs.

3. **Integer metavar.** FP-02 says the default metavar is the type name in
   uppercase and gives `--count COUNT` as the example for an integer option. The
   rule and the example disagree. Built: the rule, so an integer option shows
   `--count INTEGER`.

4. **Maximum content width.** FP-02 says help uses 80 columns by default; FP-11
   says help pages and `wrap_text` use 100. Built: `max_content_width` defaults
   to 80 for help pages (the more specific statement), and `wrap_text` defaults
   to a width of 100.

5. **`confirm` with an unrecognized answer.** The contract says any answer
   other than yes/no/empty counts as no. PRD FP-08 says any other answer asks
   again. Built: re-ask (PRD).

6. **`isolated_filesystem`.** The PRD says the directory is removed when no
   parent is given, and also that it is "always left in place". Built: removed
   on exit when no `temp_dir` is given; left in place when one is given.

7. **Default for `prompt_required`.** FP-08 describes omitted prompting options
   as prompting, and also describes the `prompt_required=False` case. Built:
   `prompt_required=True` by default, so an omitted prompting option asks.

8. **`Context.find_object`.** The PRD says "exactly that type"; the Click-style
   convention is `isinstance`. Built: `isinstance`, so a subclass instance
   matches a request for its base type.

9. **Prompt source.** When a user accepts a prompt's default with an empty
   line, the value's source is reported as `PROMPT`, because the prompt ran.

10. **`Context.invoke` argument filling.** The contract says `invoke` supplies
    exactly the caller's values. Built: values the caller does not supply are
    filled with the target's declared default (otherwise the target's callback
    would fail with a `TypeError` on a missing keyword). `forward` passes this
    context's values merged with any overrides.

11. **Required option with a declared default.** A declared default counts as a
    source, so a required option with a default is not a missing-option error
    (Click behaviour; the PRD lists environment, prefix and default map only).

## Other choices where the spec leaves form open

- Help layout: `Usage:` line, then description, `Positional arguments:` (only
  when an argument has help), `Options:`, `Commands:` (groups), epilog.
- Option entries show `[default: ...]`, `[env var: ...]` and `[DEPRECATED]`
  when those switches are enabled; a boolean flag whose default is false never
  shows its default.
- Group usage: `COMMAND [ARGS]...`; with `invoke_without_command`, the command
  token is bracketed; for chaining it is `COMMAND [ARGS]... [COMMAND [ARGS]...]...`.
- Completion output lines are `kind,value[<TAB>help]`, where kind is `plain`,
  `file` or `dir`. Scripts are generated for bash, zsh, fish and PowerShell.
  Unknown instructions print nothing, do not run the callback, and exit 1 in
  standalone mode.
- Abort prints `Aborted!` on standard error and exits 1. Exit codes: success 0,
  usage 2, abort or general error 1.
- `CliRunner.Result.exception` is set to `SystemExit` for a non-zero status from
  a usage error, as Click does, and is `None` otherwise.
- Chained subcommands are parsed with options before arguments only. Options
  that follow a chained subcommand's arguments belong to the next command in
  the chain, not to the one before it.
- Path existence checks are skipped for a missing path when existence is not
  required, as the PRD says; `resolve_path` still applies.
- The in-process runner's `fd` capture mode writes stdout and stderr to
  separate buffers, so the combined `output` is stdout followed by stderr,
  not true interleaved write order.
