# Optlyn — implementation notes

Package: `src/optlyn` (import path `optlyn`, resolved via `PYTHONPATH=src`). Pure Python, zero runtime
dependencies, Python 3.10+. Tests: `tests/` (run `python3 -m pytest -q tests/`, 118 passing).

Modules:

| module | contents |
|---|---|
| `optlyn/core.py` | `Context`, `Parameter`/`Option`/`Argument`, option parser, `Command`, `Group`, `CommandCollection`, declaration decorators, ready-made option decorators |
| `optlyn/paramtypes.py` | `ParamType`, built-ins (`STRING`, `INT`, `FLOAT`, `BOOL`, `UUID`, `UNPROCESSED`), `Choice`, `DateTime`, `IntRange`, `FloatRange`, `Tuple`, `File`, `Path` |
| `optlyn/exceptions.py` | `OptlynException`, `UsageError` (exit 2), `BadParameter`, `MissingParameter`, `NoSuchOption`, `Abort` (exit 1), `Exit`, `FileError` |
| `optlyn/termui.py` | `echo`, `secho`, `style`, `unstyle`, pager, `progressbar`, `prompt`, `confirm`, `getchar`, `pause`, `edit`, `launch`, `clear`, stream accessors |
| `optlyn/formatting.py` | `wrap_text`, `HelpFormatter` |
| `optlyn/utils.py` | `open_file`, lazy/atomic file objects, `format_filename`, `get_app_dir` |
| `optlyn/completion.py` | registration scripts (bash, zsh, fish, powershell) and suggestion output |
| `optlyn/testing.py` | `CliRunner`, `Result`, isolated filesystem |
| `optlyn/_state.py` | thread-local context stack |

Spec ids are cited in comments (`# spec: N-…`) beside the code that satisfies them. `spec/` is unchanged.

## Spec disagreements and what was built

Eighteen contradictions are marked UNSETTLED in `spec/MAP.md` (no human verdict). For each, the
rule used was: behaviour is governed by the PRD where the two sides differ, and the more specific
statement wins when both are in the same source. Where a source's own example contradicts its
rule, the rule won.

1. **CF-000010 — omitted repeatable option with no default.** N-000093 (PRD FP-01): "passed as an
   absent value". N-000211 (PRD FP-03): "receives an empty tuple, not an absent value"; the
   Interface Contract table (`pack 08`, N-000917): `()`. **Built:** `()`.
2. **CF-000016 / CF-000092 — clamp beyond an *open* bound.** N-000361 / N-000362 (PRD FP-05):
   "the nearest included value" / "the adjacent integer inside the range". Contract (N-000943):
   "becomes that bound's value". **Built:** `IntRange` clamps to the adjacent integer inside an
   open bound; closed bounds clamp to the bound itself. The contract's "bound's own value" is not
   applied to open bounds (that value is excluded by the bound).
3. **CF-000034 / CF-000072 — environment vs default map.** N-000243, N-000245 (PRD FP-03): ranked
   command line, environment, default map, declared default. Contract N-000955 (`default_map`
   row): "its values take precedence over environment variables". **Built:** the PRD ranking
   (environment beats default map).
4. **CF-000047 — epilog placement.** N-000126 (PRD FP-02): "printed at the end of the help page,
   after everything else". N-000853 (contract `command` attrs): "printed right after the
   description, before the options". **Built:** end of the page.
5. **CF-000048 — counting option omitted.** N-000207 (PRD FP-03): "zero if omitted". N-000920
   (contract table): "`None` when the option was omitted". **Built:** `0`.
6. **CF-000063 — default short help for subcommands.** N-000122 (PRD FP-02): first sentence of the
   docstring. N-000843 (PRD FP-02 help page): start of the first paragraph cut with `...` at 45
   characters. **Built:** first sentence of the first paragraph, cut at 45 characters including the
   `...` (both rules apply).
7. **CF-000087 — default maximum content width.** N-000134 (PRD FP-02): 80 columns. N-000680
   (PRD FP-11 and repeated as a cross-cutting constraint): 100 columns. **Built:** 80 by default
   (the rule in the section that describes the mechanism); callers can raise it. An explicit
   `terminal_width` is used as-is.
8. **CF-000088 — list-valued environment variable.** N-000227 (PRD FP-03): first set name wins.
   N-000893 (contract `envvar` row): last name that is set wins. **Built:** first set name wins.
9. **CF-000100 / CF-000107 — float range with clamp and an open bound.** N-000381 (PRD FP-05):
   refuses clamp when a bound is open. N-000364: clamp only when both bounds are closed. N-000943
   (contract): with an open bound, the value becomes the bound. **Built:** `FloatRange(...,
   clamp=True)` with an open bound raises at construction.
10. **CF-000115 — default metavar of an integer option.** N-000140 (PRD FP-02): the type name in
    uppercase. N-000144 (its own example): `--count COUNT`. **Built:** the rule, giving
    `--count INTEGER` (the example does not match its rule).
11. **CF-000128 — `pause` when not interactive.** N-000663 (PRD FP-11): "does nothing and does not
    block". N-000687: "does not block; it still prints its message". **Built:** prints its message,
    waits only when interactive.
12. **CF-000129 — application config directory on Unix.** N-000676 (PRD FP-11): `$XDG_CONFIG_HOME`
    when set, otherwise `~/.config`. N-001005 (contract): always under `~/.config`. **Built:** the
    PRD rule (XDG when set).
13. **CF-000134 — confirmation prompt mismatch.** N-000511 (PRD FP-08): mismatch asks the pair
    again. N-000723 (PRD FP-13): two different values typed into a confirmation prompt give an
    abort. **Built:** re-ask on mismatch; end of input still aborts.
14. **CF-000136 — author date-time formats.** N-000032 (PRD public surface): added to the defaults.
    N-000356 (PRD FP-05): replaces the default list. **Built:** replaces.
15. **CF-000151 — boolean environment value that is not recognised.** N-000344 (PRD FP-05): usage
    error for text conversion. N-000345: turns the flag off. FP-03 env rule: "any other non-empty
    string is a conversion usage error". **Built:** usage error for environment booleans.
16. **Not flagged — `Choice` case sensitivity.** Contract `Choice` row: the enumeration match
    "ignores letter case by default", but the signature is `case_sensitive=True`. **Built:**
    case-sensitive by default for enumerations as for lists; `case_sensitive=False` ignores case.
17. **Not flagged — parameter callback on a missing parameter.** Terminology (PRD N-000018): "a
    parameter callback is not called for a parameter that was omitted and received no value from any
    source". FP-03 (N-000262 area): "a missing parameter still runs its callback, so that callback
    can default from an earlier parameter's value". **Built:** the callback runs (FP-03 is the
    specific behavioural rule).
18. **Not flagged — `DateTime` when several formats match.** Contract (N-000938): "the last matching
    format is used". PRD FP-05 (N-000353/N-000354): "formats are tried in order; the first success
    wins". **Built:** first success wins (the two rules agree whenever only one format matches).
19. **Not flagged — help text form feed.** Contract `command` attr `help`: "a form-feed character in
    it is dropped and the text after it is kept". PRD FP-02 (N-000115/N-000116): a docstring form feed
    "truncates the help: text after that character is omitted". **Built:** the docstring is truncated
    at the form feed; the explicit `help=` attribute only loses the character (contract wording).
20. **Not flagged — `Path(resolve_path=True)` and `~`.** Contract `Path` row: "a leading `~` is first
    expanded". PRD FP-09 (N-000548–N-000573): "resolve to an absolute path (symlinks resolved…; a
    leading tilde is not expanded)". **Built:** no tilde expansion (PRD).
21. **Not flagged — option names in shell completion for an empty token.** Contract (N-001019): "the
    suggestions for an empty token are the subcommand names followed by the option names". PRD FP-12
    (N-000698): "Options are listed only once at least a dash has been typed". **Built:** PRD rule.
22. **Not flagged — isolated filesystem cleanup.** Runner text (N-000744–N-000747) says the directory
    is removed on exit when no parent is given, and also that it is "always left in place". **Built:**
    removed when no parent is given; left in place when a parent path is supplied.

## Choices where the spec left the form open

- Usage error wording: `Usage: …`, `Try '<prog> --help' for help.`, `Error: …`, `Missing option '--x'.`
  Option identities in messages are the declared flag names; argument identities are the declared
  argument name in quotes.
- Help page: usage line, description (indented), `Positional arguments:` (when an argument has help),
  `Options:`, `Commands:` (groups), epilog last. Option extras: `[default: …]`, `[env var: …]`,
  `(DEPRECATED)`. Choice metavar `[a|b]`.
- Completion output: one suggestion per line as `type,value`; zsh/fish append `\t` and the help text.
  Path requests are `file,<incomplete>` and `dir,<incomplete>`. Unknown completion instruction exits 1
  with a message on stderr.
- `getchar` reads `/dev/tty` in raw mode; with no terminal it raises `EOFError` (the runner's stdin is
  read directly when a runner is in use).
- `launch` uses `xdg-open` (`open` on macOS, `os.startfile` on Windows); it returns the process status
  when waiting and `0` otherwise.
- `echo_via_pager` / `get_pager_file` use `$PAGER` (or `less`) only when interactive; otherwise they
  write to stdout.
- `ctx.exit()` in non-standalone mode returns the status from `main()`; intentional help is status 0,
  missing-subcommand help is status 2.
- Declared default for a flag with no default is `False` (an automatic default); the feature-switch
  tie-break therefore prefers an explicit declared default.
- `prompt_required` defaults to `True` (an omitted prompting option prompts), matching the PRD wording
  "does not prompt when fully omitted" only when set to `False`.

## Coverage against `spec/CHECKLIST.md`

Every pack (01–33) is implemented or is a constraint satisfied by design:

- Packs 01–05 (hardware, package layout, top-level exports): implemented in `pyproject.toml` and
  `src/optlyn/__init__.py`; no runtime dependencies; no import-time I/O. Non-goals (N-000070–078) are
  satisfied by omission (no server, GUI, aliasing, plugin discovery, config syntax, thread-safe context).
- Packs 06–13 (interface contract): implemented; the Contract's delivered-value table, exit statuses,
  channels, help layout, version identity, declaration/parameter keywords, parameter types,
  invocation context, terminal helpers, shell completion, and `CliRunner` are covered.
- Packs 14–33 (PRD and feature points FP-01…FP-14): implemented, with the disagreements above resolved as
  listed. Tests in `tests/` exercise the main behaviours of each feature point.

Known limitations (honest status, not hidden):

- Windows: the code paths exist (`os.startfile`, msvcrt `getchar`, `APPDATA`) but were not exercised; only
  Linux was run.
- `getchar`, `edit` with a real interactive editor, `launch` and the pager were checked only in
  non-interactive form (their side effects were not observed in a terminal).
- Per-id verification is by feature, not one test per id; the `# spec:` comments mark where each id is
  implemented. Where an id's wording is only partly covered, the closest behaviour is implemented.
