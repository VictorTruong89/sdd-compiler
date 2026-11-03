# Notes

Optlyn is built from `spec/` as a pure-Python library in `src/optlyn`. There is no build step.
Run the suite with `PYTHONPATH=src python -m pytest tests` (or plain `python -m pytest tests`,
since `tests/conftest.py` puts `src` on the path).

- `COVERAGE.md` accounts for every id in `spec/CHECKLIST.md` (1044 ids): tested, implemented,
  or not done with a reason.
- `# spec: <id>` comments mark the code that satisfies a claim. They sit beside the classes and
  functions that carry the behaviour; the pack-level mapping is in `COVERAGE.md`.
- The export has no acceptance-criteria labels (every pack shows `AC: none`), so tests are named
  after the node id (`test_N_000850_…`) or the feature point (`test_FP06_…`).

## 1. Disagreements inside the specification

The export was made with `--allow-open`, so 28 contradictions have no human verdict. Each is
listed in `spec/MAP.md` and in the `## Conflicts` section of the pack named below. For each one
I chose a side and built it. "A" and "B" are the two claims as the export states them.

| Id | Where (pack) | A says | B says | Built |
|---|---|---|---|---|
| CF-000010 | 19 (FP-01); 21 (FP-03) | N-000093 (pack 19): an omitted repeatable option with no default "is passed as an absent value" | N-000211 (pack 19): "receives an empty tuple, not an absent value" | Empty tuple `()`. The contract delivery table (N-000917, pack 08) agrees. |
| CF-000016 | 09 (types) | N-000361: with clamp, a value beyond an open bound "is replaced by the nearest included value" | N-000943: "a value beyond that bound becomes the bound" | PRD behaviour: for an open integer bound the nearest included integer is used (bound ± 1). |
| CF-000034 | 10 (context); 21 (FP-03) | N-000243: env is consulted before the default map | N-000955: default-map values "take precedence over environment variables" | Environment ranks above the default map (the FP-03 order: command line, environment, default map, declared default). |
| CF-000047 | 07; 20 (FP-02) | N-000126: the epilog "is printed at the end of the help page" | N-000853: the epilog is "printed right after the description, before the options" | End of the help page. |
| CF-000048 | 08 (params); 21 (FP-03) | N-000207: a counting option omitted yields zero | N-000920: "`None` when the option was omitted" | Zero. |
| CF-000063 | 06; 20 (FP-02) | N-000122: short help is the first sentence of the docstring | N-000843: the start of the first paragraph, cut with `...` at 45 characters | First sentence of the first paragraph. A sentence of 45 characters or fewer is shown whole; a longer one is cut at a word boundary with `...` so the result is at most 45 characters. |
| CF-000072 | 10; 21 (FP-03) | N-000245: rank is prompt, command line, environment, default map, declared default | N-000955: default-map values take precedence over environment variables | Same as CF-000034: environment above default map. |
| CF-000087 | 20 (FP-02); 29 (FP-11) | N-000134: maximum content width "defaults to 80 columns" | N-000680: help and wrapped text use "100 columns unless the caller sets another" | 80 by default, for help pages and `wrap_text`; the caller can change it with `max_content_width` / `width`. |
| CF-000088 | 08; 21 (FP-03) | N-000227: "first one set wins" for a list of env names | N-000893: "the last name that is set wins" | First set name wins; explicit names are tried before the automatic prefix name. |
| CF-000092 | 09 (types) | N-000362: beyond an open bound with clamp, "the adjacent integer inside the range" | N-000941: "becomes that bound's value" | Adjacent integer inside the range (same as CF-000016). |
| CF-000100 | 09; 23 (FP-05) | N-000381: a float range refuses clamp when a bound is open | N-000943: clamp with an open bound makes beyond-bound values the bound | Refused at construction (`OptlynDeclarationError`, a `TypeError` and `ValueError`). |
| CF-000107 | 09; 23 (FP-05) | N-000364: clamp only when both bounds are closed | N-000943 (as above) | Clamp requires both bounds closed (same as CF-000100). |
| CF-000115 | 20 (FP-02) | N-000140: the default metavar is the type name in uppercase | N-000144: an integer option `--count` appears as `--count COUNT` | Type-name rule: `--count INTEGER`. The `COUNT` example is not followed. |
| CF-000128 | 29 (FP-11) | N-000663: a non-interactive pause "does nothing" | N-000687: "it still prints its message there" | The message is printed and the call does not block. |
| CF-000129 | 11 (helpers); 29 | N-000676: the app directory is under `$XDG_CONFIG_HOME` when set, otherwise `~/.config` | N-001005: on Unix "always under `~/.config`" | `$XDG_CONFIG_HOME` when set, otherwise `~/.config`; `force_posix=True` gives `~/.<app>`. |
| CF-000134 | 26 (FP-08); 31 (FP-13) | N-000511: a mismatched confirmation asks the pair again | N-000723: two different values are an abort (exit 1) | Ask the pair again. End of input during a pair is an abort. |
| CF-000136 | 16; 23 (FP-05) | N-000032: an author's date-time format list "is added to the default formats" | N-000356: it "replaces the default list (it does not extend it)" | Replaces the defaults. |
| CF-000151 | 23 (FP-05) | N-000344: text boolean conversion: "anything else is a usage error" | N-000345: for an env boolean flag, "any other value turns the flag off" | Usage error (FP-03 N-000238 agrees; see CF-000157). |
| CF-000154 | 32 (FP-14) | N-000745: without a parent, the runner "removes that directory on exit" | N-000747: the directory is "always left in place after the block ends" | Without a parent the directory is removed; with a parent it is left in place. |
| CF-000155 | 15 (terminology); 19 (FP-03) | N-000022: a parameter callback "is not called for a parameter that was omitted" | N-000260: "a missing parameter still runs its callback" | The callback runs for a missing parameter (value `None`). |
| CF-000156 | 07; 20 (FP-02) | N-000115: a form feed in the docstring: text after it "is omitted from the help page" | N-000853: a form feed in `help=` "is dropped and the text after it is kept" | Both hold by scope: a form feed in a docstring truncates the help; in an explicit `help=` string the character is dropped and the text is kept. |
| CF-000157 | 21 (FP-03) | N-000238: a non-empty env value that is not a boolean word is a conversion usage error | N-000345: "any other value turns the flag off" | Usage error (exit 2). |
| CF-000158 | 09; 23 (FP-05) | N-000354: formats are tried in order and the first success wins | N-000939: "the last matching format is used" | First success wins. |
| CF-000159 | 26 (FP-08); 31 (FP-13) | N-000520: prompts re-ask on conversion failure | N-000719: a value typed at a prompt "is not asked again" | Prompts re-ask until a valid value or end of input. |
| CF-000160 | 09; 27 (FP-09) | N-000558 (FP-09): a leading tilde "is not expanded" | N-000947: `resolve_path=True` "first expands" a leading `~` | Not expanded, as FP-09 and the usual path type do. |
| CF-000161 | 12 (contract); 30 (FP-12) | N-000700: options are listed only once a dash has been typed | N-001019: an empty token suggests subcommands "followed by the option names" | Empty token: subcommand names only. |
| CF-000162 | 08; 20 (FP-02) | N-000149: a flag whose default is off stays hidden even with show-default on | N-000906: show-default shows the default "a flag whose default is `False` included" | Hidden for a boolean flag whose default is off; a flag whose default is on shows it. |
| CF-000163 | 09 (types) | N-000348: matching is case-sensitive unless the author turns that off | N-000937: "by default the match ignores letter case" | Case-sensitive by default, matching the `Choice(choices, case_sensitive=True)` signature in the contract. |

## 2. Readings I chose where the spec is silent or unclear

These are not in the export's conflict list.

1. **Interactive session.** Terminology says a session is interactive when stdin is attached to a
   terminal, "or whose standard input or standard output is a TTY", and also that "a piped standard
   input without a terminal is not interactive". I used stdin and stdout both TTY, which satisfies
   the second sentence. Pager and prompt-pause behaviour follow from this.
2. **Required option with a declared default.** FP-03 lists the value sources in order (command
   line, environment, default map, declared default), so a declared default counts as a source. A
   required option that has a default is therefore not a usage error. Required options without a
   default are.
3. **`Context.invoke(command, **values)`.** The spec says invoke "supplies exactly the caller's chosen
   values". For a plain callback that is what happens. For a `Command` target the missing parameters
   get their declared values, because the target's callback cannot run without them.
4. **No-arguments help on a leaf command.** Help goes to stderr and the exit status is 2. FP-02 says
   "similar no-args-is-help paths" use the usage-error class.
5. **Unknown completion instruction.** `_PROG_COMPLETE` set to an unrecognised value prints nothing
   and exits 1 (standalone). The spec says neither script nor suggestions are printed but gives no
   status.
6. **Completion output format.** One line per suggestion: `plain,<value>`; zsh and fish add
   `\t<help>`; path requests are `file,<incomplete>` or `dir,<incomplete>`.
7. **Chained groups.** `invoked_subcommand` is the sentinel `CHAIN_SUBCOMMAND`, which is neither
   `None` nor a child name. Children are parsed after the group callback runs; an unknown name in
   the chain is reported at that point.
8. **Metavars and extras.** Choice metavar is `[a|b]`. Show-default prints `[default: …]`, env names
   print `[env var: …]`. Deprecated items carry `(DEPRECATED)` on the command help page and a
   `DeprecationWarning:` line on stderr when used.
9. **Shared destinations (feature switches).** Among options that share a destination the winner is
   the most explicit source; then an explicit declared default beats an automatic one; then the last
   declared option wins. All callbacks still run.
10. **Count option omitted** gives `0` (CF-000048), and a flag omitted gives `False` unless its
    declared default is a truthy value.
11. **Variadic arguments.** At most one per command, refused at declaration (FP-04 allows either
    refusal or never running the callback).
12. **Windows argument expansion** (N-000051) is applied only when running as a program on Windows.
    It is not run on Windows here.
13. **Prompt and confirm text** loses ANSI styles when the output is not a terminal (FP-08).
14. **Exit status for a stopped-with-status callback** in standalone mode is the status given;
    non-standalone returns the status from `main`.

## 3. Not done

Each is a non-goal in the spec (pack 18). They are listed here so the checklist is complete.

- N-000070: general-purpose argument parser unrelated to command dispatch.
- N-000071: redesigning help-page layout (wording is customisable; layout is not).
- N-000072: a remote server, GUI or web framework.
- N-000077: thread-safe mutation of an invocation context.
- N-000078: guaranteed colour on every Windows console.

## 4. What is verified and what is not

- The test suite (247 tests) covers commands, groups, chaining, parameters and types, value
  sources, prompts, files and paths, the help page, exit statuses, completion, the in-process runner
  and the context.
- The bash completion script is exercised end to end with a real `bash` in the suite (skipped when
  bash is absent). zsh, fish and PowerShell scripts are generated and their suggestion protocol is
  tested, but the scripts themselves were not run in those shells.
- `getchar`, `edit`, `launch`, progress-bar rendering on a terminal, and the pager on a real terminal
  need a terminal or desktop session and are implemented but not run by the suite.
- Nothing was run on Windows or macOS.
