# NOTES

Package: `src/optlyn` (pure Python, no dependencies). Run with `PYTHONPATH=src`.
Every id in `spec/CHECKLIST.md` is treated as implemented unless listed under "Not done" below.
The specification is a Click-like CLI toolkit; the spec disagrees with itself in places. For each
disagreement I chose one side, as listed here.

## Conflicts and what I built

Policy: where the Interface Contract (`Interface_Contract.md`) is specific about a form, I followed it over the PRD prose.

| Id | Side A | Side B | Built |
|---|---|---|---|
| CF-000010 | FP-01: omitted repeatable option "is passed as an absent value" | FP-03 and Contract "Delivered values": omitted repeatable option is `()` / "receives an empty tuple" | `()` |
| CF-000016, CF-000092 | FP-05: IntRange clamp on an open bound gives "the adjacent integer inside the range" | Contract §5: "a value beyond an open bound becomes that bound's value" | the bound's value |
| CF-000100, CF-000107 | FP-05: FloatRange "refuses clamp when a bound is open" / "Clamp only allowed when both bounds are closed" | Contract §5: clamp with an open bound turns an out-of-range value into the bound | clamp is allowed; value becomes the bound. FloatRange raises `DeclarationError` only when `min > max` |
| CF-000034, CF-000072 | FP-03/FP-07: ranking env, then default map | Contract §6: default-map values take precedence over environment variables | order: command line, default map, environment, declared default (a prompt runs after those, as in FP-08) |
| CF-000047 | FP-02: epilog printed at the end of the help page | Contract §3 `attrs`: epilog "printed right after the description, before the options" | at the end. Contract §2 "Help page" item 6 lists the epilog last |
| CF-000048 | FP-03: counting option "zero if omitted" | Contract: `None` when the option was omitted | `None` (an explicit `default=0` still works) |
| CF-000063 | FP-02: short help is the first sentence | Contract §2: start of first paragraph, cut with `...` at 45 characters | 45-character cut, stopping at the first sentence end |
| CF-000087 | FP-02: max content width 80 | FP-11: 100 | 100. `CliRunner` forces terminal width 80 as in a plain test run |
| CF-000088 | FP-03: with an envvar list "first one set wins" | Contract §4: "the last name that is set wins" | last wins for options. Arguments use first-set-wins (FP-04) |
| CF-000115 | FP-02: default metavar is the type name upper-cased | FP-02 example: `--count COUNT` for an integer option | type name (`--count INTEGER`) |
| CF-000128 | FP-11: non-interactive pause "does nothing" | FP-11 boundary: it "still prints its message" | prints the message, never blocks |
| CF-000129 | FP-11: `$XDG_CONFIG_HOME` if set | Contract §7: on Unix always under `~/.config` | always `~/.config/<name>` on Unix |
| CF-000134 | FP-08: a mismatched confirmation asks the pair again | FP-13: mismatch is an abort | asks again; EOF is an abort |
| CF-000136 | Overview: author formats "added to" the defaults | FP-05/Contract: replace the list | replace |
| CF-000151 | FP-05: other boolean text is a usage error | FP-05: env boolean flag "any other value turns the flag off" | usage error everywhere, matching FP-03. Empty or whitespace-only env value deactivates a bool flag |

## Disagreements the export did not list

* Form feed in help: PRD FP-02 truncates a docstring at it. Contract §3 `help=` says the character is dropped and the following text kept. Built: docstrings truncate; an explicit `help=` keeps the text and drops the character.
* `show_default` on a bool flag whose default is false: PRD FP-02 hides it. Contract §4 says it is shown. Built: shown (Contract).
* Completion for an empty token: PRD FP-12 lists options only after a dash. Contract §8 says the empty-token suggestions are subcommand names followed by option names. Built: Contract (a group with an empty token yields subcommands, then options).
* `Path(resolve_path=True)`: PRD FP-09 says `~` is not expanded. Contract §5 says it is expanded first. Built: expanded (Contract).
* `DateTime` with several matching formats: PRD FP-05 says the first success wins. Contract §5 says the last matching format is used. Built: last (Contract).
* `Choice(enum)` case matching: Contract §5 says an enum match ignores case by default. PRD FP-05 says matching is case-sensitive unless turned off. Built: `case_sensitive=None` means insensitive for enums and sensitive for other choices.
* Parameter callback for an omitted parameter: Terminology says it is not called. FP-03 says a missing parameter still runs its callback. Built: it runs (FP-03).
* `isolated_filesystem`: FP-14 says the directory is removed on exit when no parent is given. The same bullet also says it is always left in place. Built: removed when `temp_dir` is None, kept when a parent is given.
* A bool flag with `default=True` and no explicit `flag_value`: FP-03 says "present yields true". I used `flag_value = not default` as the Click lineage does. This is unverified against the spec.
* "Interactive session" for pager and pause: stdin is a TTY or stdout is a TTY.
* Exception class names beyond Contract §1 are my choice. Declaration-time failures raise `DeclarationError`, which subclasses `TypeError`, `ValueError` and `RuntimeError`.

## Not done

* Windows glob/env expansion of `argv` (PRD Non-functional constraints, parenthetical). Linux is the supported target.
* `capture="fd"`: OS-level writes are ordered correctly relative to interpreter writes in `Result.output`. Writes made by child processes inherit the redirected descriptors.
