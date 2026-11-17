# Optlyn: implementation notes

This is the implementation of the specification in `spec/` (33 packs, 1044 checklist ids).
`spec/` is unchanged. Code lives in `src/optlyn/` (src layout, zero runtime dependencies,
Python 3.10+). Tests are in `tests/test_optlyn.py`.

Run the tests with:

    PYTHONPATH=src python3 -m pytest tests -q

Result at the time of writing: **120 passed**.

## Layout

| File | Contents |
| --- | --- |
| `src/optlyn/core.py` | `Context`, `Parameter`/`Option`/`Argument`, the option and argument parser, `Command`, `Group`, `CommandCollection`, help rendering, `main()` |
| `src/optlyn/decorators.py` | `command`, `group`, `option`, `argument`, `help_option`, `version_option`, `custom_version_option`, `password_option`, `confirmation_option`, `pass_context`, `pass_obj`, `make_pass_decorator` |
| `src/optlyn/paramtypes.py` | `ParamType` and the built-in types (`STRING`, `INT`, `FLOAT`, `BOOL`, `UUID`, `UNPROCESSED`, `Choice`, `DateTime`, `IntRange`, `FloatRange`, `Tuple`, `File`, `Path`) |
| `src/optlyn/termui.py` | `echo`, `secho`, `style`, `unstyle`, prompts, `confirm`, `getchar`, `pause`, pager, progress bar, `edit`, `launch`, `clear`, `get_app_dir`, `format_filename`, `open_file` |
| `src/optlyn/formatting.py` | `wrap_text` and help-text helpers |
| `src/optlyn/shell_completion.py` | registration scripts for bash, zsh, fish and PowerShell, and the suggestion engine |
| `src/optlyn/testing.py` | `CliRunner` and `Result` |
| `src/optlyn/_files.py`, `_context.py`, `exceptions.py` | file helpers, thread-local context stack, exception and exit-status classes |
| `pyproject.toml` | PEP 517 metadata (setuptools, src layout) |

Every `# spec: N-…` comment marks the code that implements those ids. Module docstrings carry
the blocks that cover several ids at once.

## Spec disagreements and what was built

The export says 18 contradictions have no human verdict (`--allow-open`). Each one is listed
below with both sides and the choice made. The tie-break used throughout: where a PRD feature
point describes behaviour and the Interface Contract gives a form or signature, the PRD
behaviour wins. The Contract's own preamble says "What the library does with those inputs,
and every default value that changes behaviour, is stated in the PRD".

### Listed as UNSETTLED in `spec/MAP.md`

1. **CF-000010: omitted repeatable option with no default.** Pack 19 N-000093 says it is "passed
   as an absent value". Pack 21 N-000211 says it "receives an empty tuple, not an absent value".
   *Built:* `()`, the empty tuple (also the Contract's delivered-values table, pack 08 N-000917).

2. **CF-000016 and CF-000092: IntRange clamp beyond an open bound.** Pack 23 N-000361 and
   N-000362 say the value becomes "the nearest included value" / "the adjacent integer inside the
   range". Pack 09 N-000941 and N-000943 say it "becomes that bound's value". *Built:* the adjacent
   integer for an open bound (PRD). A closed bound still clamps to the bound.

3. **CF-000034 and CF-000072: environment versus default map.** Pack 21 N-000243 and N-000245 rank
   the sources as prompt, command line, environment, default map, declared default. Pack 10
   N-000955 says default-map values "take precedence over environment variables". *Built:* the PRD
   ranking (environment before default map).

4. **CF-000047: where the epilog goes.** Pack 20 N-000126 says "at the end of the help page, after
   everything else". Pack 07 N-000853 says "right after the description, before the options".
   *Built:* the end of the page. Pack 06 N-000844 (the Contract's help-page order) agrees with this.

5. **CF-000048: counting option when omitted.** Pack 21 N-000207 says zero. Pack 08 N-000920 says
   `None`. *Built:* `0` (or the declared default if one is given).

6. **CF-000063: default short help for subcommands.** Pack 20 N-000122 says the first sentence of
   the docstring. Pack 06 N-000843 says the start of the first paragraph, cut with `...` at 45
   characters. *Built:* the first sentence, cut to 45 characters with `...` when longer. This
   satisfies the 45-character rule in full; a first sentence over 45 characters is therefore shown
   truncated rather than in full.

7. **CF-000087: default maximum content width.** Pack 20 N-000134 says 80 columns. The repeated
   constraint N-000680 (pack 29, repeated in many packs) says 100. *Built:* 80, the default of the
   more specific help-wrapping rule. Callers may raise it through `max_content_width`.

8. **CF-000088: environment list, first or last set wins.** Pack 21 N-000227 says the first set
   name wins. Pack 08 N-000893 says the last. *Built:* the first set name wins.

9. **CF-000100 and CF-000107: FloatRange with clamp and an open bound.** Pack 23 N-000381 and
   N-000364 say clamp is refused when a bound is open (or unless both bounds are closed). Pack 09
   N-000943 says clamp with an open bound is valid. *Built:* refused at construction with
   `DeclarationError`.

10. **CF-000115: metavar of an integer option.** Pack 20 N-000140 gives the type name in uppercase
    (`INTEGER`). The example in N-000144 shows `--count COUNT`. *Built:* the rule, so `--count
    INTEGER`. The example is the odd one out, since the rule is the general statement.

11. **CF-000128: `pause` when not interactive.** Pack 29 N-000663 says it does nothing. N-000687
    says it still prints its message. *Built:* it prints the message and never blocks.

12. **CF-000129: application config directory on Unix.** Pack 29 N-000676 says
    `$XDG_CONFIG_HOME` when set, otherwise `~/.config`. Pack 11 N-001005 (Contract) says always
    under `~/.config`. *Built:* the PRD rule (`$XDG_CONFIG_HOME` when set).

13. **CF-000134: confirmation prompt mismatch.** Pack 26 N-000511 says a mismatch asks the pair
    again. Pack 31 N-000723 lists "two different values typed into a confirmation prompt" as an
    abort. *Built:* a mismatch asks the pair again. End of input during a prompt aborts (N-000524).

14. **CF-000136: date-time format list.** Pack 16 N-000032 says the author's list "is added to the
    default formats". Pack 23 N-000356 says it "replaces the default list (it does not extend it)".
    *Built:* replaces (FP-05 is the detailed statement).

15. **CF-000151: environment value for a boolean flag, such as `maybe`.** Pack 23 N-000345 says
    any other value turns the flag off. Pack 23 N-000344 and pack 21 N-000234 to N-000242 say an
    unrecognised non-empty value is a usage error. *Built:* a usage error.

### Not listed in `spec/MAP.md`, found while building

16. **Callbacks for omitted parameters.** The glossary (pack 15 N-000023) says a parameter callback
    "is not called for a parameter that was omitted and received no value from any source". FP-03
    (pack 21 N-000263) says "a missing parameter still runs its callback, so that callback can
    default from an earlier parameter's value". *Built:* the callback always runs (with `None` or
    the default). A required parameter with no value raises `MissingParameter` before its callback.

17. **Choice matching for enumerations.** Contract section 5 (pack 09 N-000937 row) says that for
    an `enum.Enum`, members are "matched by name; by default the match ignores letter case".
    FP-05 (pack 23 N-000348 to N-000352) says matching "is case-sensitive unless the author turns
    that off". *Built:* case-sensitive by default for every `Choice`, enumerations included;
    `case_sensitive=False` turns it off.

18. **DateTime format precedence.** Contract section 5 (pack 09, DateTime row) says that when
    several formats match, "the last matching format is used". FP-05 (pack 23 N-000353 to
    N-000357) says "formats are tried in order; the first success wins". *Built:* first success.

19. **Path `resolve_path` and a leading tilde.** Contract section 5 (pack 09 N-000945) says a
    leading `~` is expanded first. FP-09 (pack 27 N-000548 to N-000573) says a leading tilde is not
    expanded. *Built:* not expanded (the PRD).

20. **`isolated_filesystem` cleanup.** FP-14 (pack 32 N-000744 to N-000747) says the directory is
    removed on exit when no parent is given, and also that it "is always left in place after the
    block ends". *Built:* removed when no `temp_dir` is given, kept when one is given. The first
    statement is the specific one.

21. **Prompt semantics for omitted options.** Pack 26 N-000488 to N-000491 says an option with
    prompting "if not supplied on the command line, reads a line". N-000492 to N-000496 describe an
    option that "does not prompt when fully omitted" when the author does not require the prompt.
    *Built:* `prompt_required` (default `True`). When true, an omitted option prompts. When false,
    it prompts only when the flag is given without a value, and uses the default when omitted. This
    reads both statements as the two modes of one flag.

### Interpretations where the spec is silent

- A required option or argument that has a default (or a default-map or environment value) is
  satisfied by that value. It is an error only when nothing supplies a value.
- An argument with no default is required unless `required=False` is given. A variadic argument
  (`nargs=-1`) is optional unless `required=True`.
- `help_option()` with no names uses `--help`. `version_option()` uses `--version`.
- A non-standalone clean stop (`ctx.exit(n)`) returns `n` from `main`. The callback's return value
  is returned for a normal run.
- A chained command's return values are always returned as a list in non-standalone mode.
- `CliRunner(capture="fd")` reports output as standard output followed by standard error. Two
  separate descriptors cannot be interleaved exactly.
- Choice values, option names and command names all match exactly unless a
  `token_normalize_func` is installed.

## Not done, and why

There are 1044 checklist ids. 1026 are marked with a `# spec:` comment in the code, and the 18 below
are not.

| Ids | Status | Reason |
| --- | --- | --- |
| N-000054 | not done | Windows argv expansion (globs, `~`, environment tokens) when run as a program. The target is Linux, and this cannot be tested here. |
| N-000055 | assumption | States that a Unix shell already expands arguments before the process starts. Nothing to implement. |
| N-000069, N-000070 to N-000078 | non-goal, not built | Spec non-goals: thread-safe context mutation, general-purpose parsing outside dispatch, redesignable help layout, remote server, GUI or web framework, built-in aliases or plugin discovery, an Optlyn configuration-file syntax, guaranteed colour on every Windows console. |
| N-000121 | not done | Marked `MAY`: naming arguments in the docstring is an author concern, not a feature. |
| N-000004, N-000011 to N-000014 | scope statements | Assumption and documentation-scope statements about the specification itself. They have no runtime behaviour. |

Other parts that are only partly done:

- `CliRunner` `capture="fd"`: descriptor capture works (see the test), but output is stdout then
  stderr rather than interleaved.
- `getchar` reads from `/dev/tty` when it can and falls back to standard input otherwise.
- `edit` and `launch` call the platform editor or opener. They are not exercised in the test suite.
- `echo_via_pager` uses `$PAGER` when the session is interactive, and otherwise writes straight to
  standard output. There is no pydoc fallback.
- Shell completion generates scripts for all four shells, but only the suggestion logic is tested.
  The scripts were not run under the real shells.
- `progressbar` shows a bar on a terminal. Its formatting and remaining-time estimate are
  simple.

## Testing

`tests/test_optlyn.py` has 120 tests. They cover declaration and invocation, help and version,
options (short stacks, pairs, counting, multiple, nargs, optional values, feature switches),
arguments (variadic, envvar, defaults), every built-in type and its failure cases, file and path
parameters (lazy and atomic writes, dash streams), groups and nesting, command collections, chaining
and result callbacks, context sources and default maps, prompts, confirmation and password options,
terminal helpers, the in-process runner (both capture modes), and shell completion.

The tests were written from the spec, not from a reference implementation. The export contains no
acceptance criteria (every pack's "Acceptance criteria" section is `None`), so there are no
`test_AC_…` names; the tests are named by behaviour.
