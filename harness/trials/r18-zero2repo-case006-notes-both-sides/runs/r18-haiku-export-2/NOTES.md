# Optlyn — implementation notes

Implementation of the Optlyn specification in `spec/` (exported with `--allow-open`).
Package: `src/optlyn/` (Python 3.10+, no runtime dependencies). Tests: `tests/` (run with
`PYTHONPATH=src python -m pytest tests`).

Layout:

| Module | Contents (spec pack) |
|---|---|
| `optlyn/core.py` | Context, Parameter/Option/Argument, token parser, Command/Group/CommandCollection, declaration decorators, help rendering, pass_* decorators (packs 07–10, 19–22, 24–25) |
| `optlyn/param_types.py` | ParamType and built-in types, File/Path, lazy and atomic file opening (packs 09, 23, 27) |
| `optlyn/termui.py` | Terminal helpers: echo, style, pager, progressbar, prompt, confirm, getchar, pause, edit, launch, clear, get_app_dir, format_filename (packs 11, 26, 29) |
| `optlyn/formatting.py` | `wrap_text`, short-help truncation, form-feed rule (packs 06, 20, 29) |
| `optlyn/shell_completion.py` | Completion instructions, suggestion protocol, registration scripts (packs 12, 30) |
| `optlyn/testing.py` | `CliRunner`, `Result`, `isolated_filesystem` (packs 13, 32) |
| `optlyn/_state.py` | Thread-local current-context stack |
| `optlyn/exceptions.py` | Usage, abort, exit, file and general error classes (packs 06, 31) |

## Conflicts in the specification

The export lists 28 unsettled contradictions (`spec/MAP.md`, "UNSETTLED"). None has a human
verdict. Each entry gives both sides, where they are (pack and claim id), and the choice built.
Rule applied throughout: the Interface Contract says where behaviour is "stated in the PRD"
(`spec/packs/04-*`); where both sides are behavioural, the more specific PRD statement was
preferred over the Contract's form-level statement.

1. **CF-000010 — omitted repeatable option with no default.**
   A: pack 19 (FP-01), N-000093: "A repeatable option that was omitted and has no default is passed as an absent value."
   B: pack 21 (FP-03), N-000211: "If it is omitted and has no default, the callback receives an empty tuple, not an absent value."
   Built: empty tuple `()` (B is the more specific statement; the Contract table also gives `()`).

2. **CF-000016 — IntRange clamp beyond an open bound.**
   A: pack 23 (FP-05), N-000361: "a value outside the range ... is replaced by the nearest included value".
   B: pack 09 (Contract §5), N-000943: "a value beyond that bound becomes the bound's value".
   Built: the adjacent integer inside the range for an open bound, the bound itself for a closed bound (A, plus N-000362 in FP-05).

3. **CF-000034 — environment versus default map precedence.**
   A: pack 21 (FP-03), N-000243: "then environment, then the default map on the invocation context".
   B: pack 10 (Contract §6), N-000955: "its values take precedence over environment variables".
   Built: environment before default map (A; also the ranking in N-000245).

4. **CF-000072 — same conflict, ranking statement.**
   A: pack 21, N-000245: ranks "prompt, command line, environment, default map, declared default".
   B: pack 10, N-000955 (as above). Built: as in (3).

5. **CF-000047 — epilog placement.**
   A: pack 20 (FP-02), N-000126: "The epilog is printed at the end of the help page, after everything else on it."
   B: pack 06 (Contract §2 / attrs in §3), N-000853: "epilog (printed right after the description, before the options)".
   Built: end of the help page (A; §2 item 6 also lists it last).

6. **CF-000048 — counting option when omitted.**
   A: pack 21, N-000207: "yields how many times it occurred (zero if omitted)".
   B: pack 08 (Contract §4), N-000920: "`None` when the option was omitted".
   Built: `0` (A).

7. **CF-000063 — default short help of a subcommand.**
   A: pack 06 / Contract §2 related, N-000122 (pack 20 FP-02): "the short help is the first sentence of the docstring by default".
   B: pack 06 (Contract §2), N-000843: "by default the start of the child's first paragraph, cut with `...` at 45 characters".
   Built: first sentence of the docstring, cut to 45 characters total with `...` when longer (satisfies both where the sentence fits).

8. **CF-000087 — maximum content width.**
   A: pack 20 (FP-02), N-000134: "a maximum content width that defaults to 80 columns".
   B: pack 29 (FP-11), N-000680: "a maximum content width of 100 columns unless the caller sets another".
   Built: 80 by default; the cap applies only to auto-detected width; an explicit `terminal_width` is used as-is (A's more specific rule).

9. **CF-000088 — environment list of names.**
   A: pack 21, N-000227: "first one set wins".
   B: pack 08, N-000893: "the last name that is set wins".
   Built: first set name wins (A).

10. **CF-000092 — IntRange clamp beyond an open bound.** See (2). Built: adjacent integer.

11. **CF-000100 — FloatRange clamp with an open bound.**
    A: pack 23, N-000381: "Float range refuses clamp when a bound is open (declaration error)".
    B: pack 09, N-000943: "With `clamp=True` and an open bound, a value beyond that bound becomes the bound".
    Built: refused at construction (`ValueError`), per A.

12. **CF-000107 — same as (11).** Clamp is only allowed when both bounds are closed (N-000364, pack 23) vs B above. Built: refused at construction.

13. **CF-000115 — default metavar of an integer option.**
    A: pack 20 (FP-02), N-000140: "the default metavar is the type name in uppercase".
    B: pack 20, N-000144: "an integer option `--count` appears on the help page as `--count COUNT`".
    Built: the type name in uppercase, so `--count INTEGER` (A's rule; B reads as an example that uses the parameter name, which the rule does not give).

14. **CF-000128 — Pause when not interactive.**
    A: pack 29, N-000663: "when not interactive it does nothing and does not block".
    B: pack 29, N-000687: "it still prints its message there".
    Built: the message is printed, and nothing blocks (both halves of each statement that can hold together).

15. **CF-000129 — application config directory on Unix.**
    A: pack 29, N-000676: "`$XDG_CONFIG_HOME` when that variable is set, otherwise `.config` in the home directory".
    B: pack 11 (Contract §7), N-001005: "On Unix the directory is always under `~/.config`".
    Built: `$XDG_CONFIG_HOME` when set (A, the behavioural rule).

16. **CF-000134 — confirmation prompt mismatch.**
    A: pack 26 (FP-08), N-000511: "asks twice and rejects a mismatch by asking the pair again".
    B: pack 31 (FP-13), N-000723: "two different values typed into a confirmation prompt" is an abort (exit 1).
    Built: mismatch asks the pair again (A). End of input during the pair is still an abort.

17. **CF-000136 — author date-time formats.**
    A: pack 16 (public surface), N-000032: "an author's date-time format list is added to the default formats".
    B: pack 23 (FP-05), N-000356: "which replaces the default list (it does not extend it)".
    Built: replaces the default list (B, the detailed behavioural rule).

18. **CF-000151 — boolean environment value not recognised.**
    A: pack 23 (FP-05), N-000344: "anything else is a usage error" (text conversion).
    B: pack 23, N-000345 / pack 21 (FP-03): "any other value turns the flag off" (environment flag).
    Built: for boolean flags read from the environment, an unrecognised non-empty value is a usage error (FP-03, N-000238); a whitespace-only value deactivates.

19. **CF-000154 — isolated filesystem cleanup.**
    A: pack 32 (FP-14), N-000745: "the runner removes that directory on exit" (no parent given).
    B: pack 32, N-000747: "always left in place after the block ends".
    Built: the directory is always left in place (B, which states the reason: files can be inspected).

20. **CF-000155 — callback for an omitted parameter.**
    A: pack 15 (terminology), N-000022: "A parameter callback is not called for a parameter that was omitted and received no value from any source."
    B: pack 21 (FP-03), N-000260: "A missing parameter still runs its callback, so that callback can default from an earlier parameter's value".
    Built: callbacks run for omitted parameters (B, the more specific behavioural rule); they receive the missing value (`None`, `()`, `False`, or `0`).

21. **CF-000156 — help text after a form feed.**
    A: pack 20 (FP-02), N-000115: "text after that character is omitted from the help page".
    B: pack 07 (Contract §3), N-000853: "a form-feed character in it is dropped and the text after it is kept".
    Built: text after the form feed is omitted (A).

22. **CF-000157 — boolean environment value (non-recognised).** Same as (18), other side: pack 21, N-000238 "Any other non-empty string is a conversion usage error" vs N-000345 "any other value turns the flag off". Built: usage error.

23. **CF-000158 — date-time format matching.**
    A: pack 23, N-000354: "Formats are tried in order; the first success wins".
    B: pack 09 (Contract §5), N-000939: "When several formats match a value, the last matching format is used".
    Built: first success wins (A).

24. **CF-000159 — prompt conversion failure.**
    A: pack 26 (FP-08), N-000520: "Prompts re-ask on conversion failure until a valid value is given".
    B: pack 31 (FP-13), N-000719: "conversion failure (including a value typed at a prompt, which is not asked again)".
    Built: prompts re-ask (A, the prompt-specific rule). Command-line conversion failures remain usage errors.

25. **CF-000160 — leading tilde with path resolution.**
    A: pack 27 (FP-09), N-000558: "a leading tilde is not expanded" (under resolve-to-absolute).
    B: pack 09 (Contract §5), N-000947: "With `resolve_path=True`, a leading `~` is first expanded".
    Built: no tilde expansion (A).

26. **CF-000161 — empty token completion.**
    A: pack 30 (FP-12), N-000700: "Options are listed only once at least a dash has been typed".
    B: pack 12 (Contract §8), N-001019: "the suggestions for an empty token are the subcommand names followed by the option names".
    Built: an empty token suggests subcommand names only (A).

27. **CF-000162 — show-default on a boolean flag with default off.**
    A: pack 20 (FP-02), N-000149: "that default remains hidden even if show-default is on".
    B: pack 08 (Contract §4), N-000906: "the default is shown for every option, a flag whose default is `False` included".
    Built: hidden for flags whose default is off (A).

28. **CF-000163 — choice matching case.**
    A: pack 23 (FP-05), N-000348: "Matching is case-sensitive unless the author turns that off".
    B: pack 09 (Contract §5), N-000937: "by default the match ignores letter case" (enumeration members).
    Built: case-sensitive by default for `Choice` and enumerations (A, and the `case_sensitive=True` signature in the same Contract section).

## Other choices made where the specification leaves the form open

- Help layout: `Usage:` line, description, `Positional arguments:`, `Options:`, `Commands:`, epilog. Option entries show `[required]`, `[default: …]`, `[env var: …]`, `(deprecated)`. Metavar of a closed choice is `[a|b]`.
- Deprecation warnings are written to stderr as `DeprecationWarning: …`. The help page of a deprecated command carries `(DEPRECATED)`.
- Shell completion suggestion lines are `<kind>\t<value>\t<help>` with kind `plain`, `file` or `dir`. Registration scripts are provided for bash, zsh, fish and PowerShell. They are generated but were not run inside those shells.
- Destination inference keeps the case of the declared name (`--Name` → `Name`).
- A conversion function that raises `ValueError` is refused as a usage error.
- `Context.invoke(cmd, **values)` supplies the caller's values and fills the target's declared defaults for parameters the caller did not pass.
- Declaration errors raise `TypeError` (options/arguments), `ValueError` (range types), and a second variadic argument raises `TypeError` when the command is created.
- Eager flags are processed in the order typed; untyped eager flags follow.
- Option prompts: following FP-08 literally, a `prompt=` option is asked for when its flag is given without a value, or when it is required and omitted. An omitted, non-required prompt option uses its default and does not ask. `password_option()` therefore asks only when `--password` is given bare (or when it is made required). Callers who want an always-ask password pass `required=True`.
- `ctx.exit()` inside a non-standalone run returns the status instead of raising.
- Feature-switch groups (several options sharing a destination) resolve to the option typed last; without command-line input, an explicit default beats an auto-derived flag default.
- Chained subcommands: each subcommand's options must precede its arguments. An option-shaped token after a chained subcommand's arguments is a usage error.

## Gaps and things not verified

- Not verified in real shells: the bash/zsh/fish/PowerShell registration scripts and the completion round-trip under a live shell.
- Pager and `launch`/`edit` are implemented but only the non-interactive paths and error fallbacks are exercised. `getchar` on a real terminal (via `/dev/tty`) was not tested.
- `progressbar` implements a simple bar and ETA for a terminal; no tests cover the rendering.
- Windows-specific behaviour (glob expansion of arguments, `os.startfile`, APPDATA config lookup) is written but not exercised; the target is Linux.
- Thread isolation of the current context is implemented with thread-local storage; not separately tested across threads.
- The `spec/` directory and `spec/CHECKLIST.md` were left unchanged, so no checklist boxes are ticked. Coverage is by feature: the behaviours the packs describe are implemented and the tests in `tests/` exercise the main paths, but not every one of the 1044 checklist ids has a dedicated test.

## Verification

`PYTHONPATH=src python -m pytest tests` — 64 tests pass (declaration, parsing, help, prompts,
chaining, completion, file/path types, terminal helpers, and in-process runner behaviour).
