# Optlyn — implementation notes

Layout: `src/optlyn/` (pure Python, no runtime dependencies, Python 3.10+).
Tests: `tests/test_optlyn.py` (run with `PYTHONPATH=src python -m pytest tests`).

## Where the specification disagrees, and what was built

| # | Where | What disagrees | What was built |
| --- | --- | --- | --- |
| 1 | Interface Contract §4 (`envvar`) vs. PRD FP-03 | Contract: a list of env names, "the last name that is set wins". PRD: "first one set wins". | PRD (first set wins). The PRD is the behavioural authority; the contract only fixes shape. |
| 2 | Contract §5 (`Path`, `resolve_path`) vs. PRD FP-09 | Contract: a leading `~` is expanded when `resolve_path=True`. PRD: "a leading tilde is not expanded". | Contract (`~` is expanded before resolving). |
| 3 | PRD FP-02 vs. PRD FP-11 (width) | FP-02: help pages cap auto-detected width at 80 columns. FP-11: help pages and wrapped text use 100 columns. | Help pages use the context's `max_content_width` (default 80). `formatting.wrap_text` defaults to 100, as FP-11 says for wrapped text. |
| 4 | Contract §3 (`command` attrs `epilog`) vs. Contract §2 help layout and PRD FP-02 | The `command` attrs text places the epilog right after the description, before the options. The help-page layout and FP-02 place it last. | Epilog is printed last on the help page. |
| 5 | Contract §5 (`Choice`, `case_sensitive=True`) vs. the same entry's note on enums | The signature defaults to case-sensitive, but the enum note says enum matching ignores case by default. | `case_sensitive` defaults to `None`: enum choices match ignoring case, list choices match case-sensitively. An explicit `True` or `False` is always honoured. |
| 6 | Contract §8 (completion, empty token) vs. PRD FP-12 | Contract: for an empty token, subcommand names are followed by option names. PRD: options are listed only once at least a dash has been typed. | PRD. An empty token lists subcommands only. |
| 7 | PRD terminology (callbacks) vs. PRD FP-03 | Terminology: a parameter callback is not called for an omitted parameter with no value. FP-03: a missing parameter still runs its callback so it can default from an earlier value. | FP-03. Callbacks run for every parameter, including omitted ones. |
| 8 | PRD FP-02 vs. FP-13 (no-args help) | Both describe the no-args group case. | The help page is written to standard error and the exit status is 2. |

## Other choices (where the spec leaves the form to the implementer)

- Chaining groups set `ctx.invoked_subcommand` to `"*"` while children run (not a child name, not `None`).
- Completion: an unrecognised `_<PROG>_COMPLETE` instruction exits with status 1 and prints nothing.
  Path requests are emitted as `_path:dir:<token>` / `_path:file:<token>` lines; the bash script expands them with `compgen`.
- Zsh and Fish suggestion lines carry `value<TAB>help`.
- Sub-commands in group listings are sorted by name.
- Default option metavars: `TEXT` for strings, `INTEGER` for ints, `FLOAT`, `BOOLEAN`, `UUID`, `DATETIME`; choices show `[a|b]`.
- Feature-switch groups (several options with one destination): highest source rank wins, then an explicit declared default over an auto-derived one, then the last declared option.
- A `DeprecationWarning:` line on standard error is used for deprecated commands, options and arguments.
- The completion variable uses the program name with `-` replaced by `_`, upper-cased (`_MYTOOL_COMPLETE`).
- Missing-command and no-args-help usage errors use exit status 2; intentional help uses 0.
- `CliRunner` defaults `prog_name` to `cli`.

## Known gaps

- Windows-only argument expansion (glob / `~` / environment tokens in the argument list) is not implemented.
- `edit`, `launch`, `getchar` and `pause` are implemented with simple, platform-basic behaviour and are only smoke-tested (no TTY in this environment).
- `echo_via_pager` / `get_pager_file` only pipe to `$PAGER` (or `less`) when the session is interactive; not exercised in tests.
- `CliRunner(capture="fd")` is accepted and maps to the same in-process capture; OS-level descriptor capture is not implemented.
- Multi-value (`nargs`) options combined with `multiple=True` are supported; a variadic argument combined with a later fixed argument takes the tokens left after reserving the later ones.
