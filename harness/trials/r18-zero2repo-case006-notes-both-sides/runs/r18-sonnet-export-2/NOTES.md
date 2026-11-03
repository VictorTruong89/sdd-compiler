# Optlyn build notes

Implementation: pure-Python package in `src/optlyn` (no dependencies, Python >= 3.10). Run with `PYTHONPATH=src`.
Modules: `core` (Context/Command/Group/CommandCollection/Parameter/Option/Argument), `parser`, `types`,
`decorators`, `utils` (echo/style/files), `termui` (prompt/confirm/pager/progress/edit/launch/getchar/pause/clear),
`formatting` (HelpFormatter, `wrap_text`), `shell_completion`, `testing` (`CliRunner`), `exceptions`, `globals`.
Own tests: `tests/test_basic.py`.

## Rule used to settle contradictions
The Interface Contract (`Interface_Contract.md`, packs 04-13) wins over the PRD feature points when they disagree.
When the Contract is silent, the more specific PRD statement wins, and otherwise the conventional behaviour
of a Click-style toolkit. All 28 UNSETTLED conflicts are decided below.

| CF | Sides (pack) | Built |
|---|---|---|
| CF-000010 | FP-01 (pack 19) "A repeatable option that was omitted and has no default is passed as an absent value" vs FP-03 (pack 21) "receives an empty tuple, not an absent value"; Contract §4 says omitted repeatable -> `()` | `()` |
| CF-000016 / 092 / 100 / 107 | FP-05 (pack 23): IntRange clamp gives "the adjacent integer inside the range for an open bound"; FloatRange "Clamp is only allowed when both bounds are closed" / "refuses clamp when a bound is open"; Contract §5 (pack 09) says clamp on an open bound yields the bound's own value, and FloatRange accepts clamp with an open bound | clamp returns the bound's value for both range types; open bound + clamp is accepted for FloatRange (no construction error; only `min > max` raises) |
| CF-000034 / 072 | FP-03/FP-07 (packs 21, 25): precedence "command line, environment, default map, default"; Contract §6 (pack 10): default_map values take precedence over environment | command line > default map > environment > declared default (prompt above all). Feature-switch ranking uses the same order |
| CF-000047 / 156 | FP-02 (pack 20): epilog "at the end of the help page" and text after a form feed is omitted; Contract §3 (pack 07): epilog "right after the description, before the options", form feed "dropped and the text after it is kept" | epilog printed after description, before "Positional arguments"/"Options"/"Commands"; form-feed char removed, all text kept. (Contract §2 help list also names epilog last; the §3 attrs wording was chosen) |
| CF-000048 | FP-03 (pack 21) counting option "zero if omitted"; Contract §4 (pack 08) `None` when omitted | `None` |
| CF-000063 | FP-02 (pack 20) subcommand short help is the first sentence; Contract §2 (pack 06) start of first paragraph cut with `...` at 45 chars | Click-style: first paragraph, stops at a sentence end, otherwise cut with `...` so the text is <= 45 chars |
| CF-000087 | FP-02 (pack 20) max content width 80; FP-11 (pack 29) 100 | default 100 (cap on auto-detected width only; an explicit `terminal_width` is used as is). `CliRunner` forces width 80 inside its isolation unless `terminal_width` is passed |
| CF-000088 | FP-03 (pack 21) envvar list "first one set wins"; Contract §4 "the last name that is set wins" | last set name wins |
| CF-000115 | FP-02 (pack 20) default metavar is the upper-cased type name but its example shows `--count COUNT`; Contract §5 `ParamType.name` "shown upper-cased as the default metavar" | type name upper-cased (`--count INTEGER`) |
| CF-000128 | FP-11 (pack 29) `pause` "does nothing" when non-interactive vs "still prints its message" | prints the message, does not block when not interactive |
| CF-000129 | FP-11 (pack 29) `$XDG_CONFIG_HOME` honoured; Contract §7 "always under ~/.config" | always `~/.config/<name>` on Unix (POSIX-forced mode `~/.<name>`, macOS `Library/Application Support`, `sys.platform` decides) |
| CF-000134 | FP-08 (pack 26) confirmation mismatch re-asks the pair; FP-13 (pack 31) lists two different values as abort | re-ask the pair (Contract silent; FP-08 is the detailed statement). EOF is an abort |
| CF-000136 / 158 | FP-05 (pack 23) DateTime formats replace defaults / first success wins; Public surface inventory (pack 16) "added to defaults"; Contract §5 last matching format used | author list replaces the defaults; every format is tried and the last match is used |
| CF-000151 / 157 | FP-05 (pack 23) "For a boolean flag read from an environment variable, any other value turns the flag off" vs FP-03 (pack 21) "Any other non-empty string is a conversion usage error" | usage error (FP-03 text is the detailed one); whitespace-only deactivates, truly empty is unset |
| CF-000154 | FP-14 (pack 32) isolated_filesystem removes dir on exit vs "always left in place" | removed when no `temp_dir` given; left in place when `temp_dir` parent is supplied |
| CF-000155 | Terminology (pack 15) callback not called for omitted parameter vs FP-03 (pack 21) "A missing parameter still runs its callback" | callback runs (with `None`/`()`) |
| CF-000159 | FP-08 (pack 26) prompts re-ask on conversion failure vs FP-13 (pack 31) "not asked again" | re-ask until valid or EOF (EOF aborts) |
| CF-000160 | FP-09 (pack 27) "a leading tilde is not expanded" vs Contract §5 `resolve_path` expands `~` first | `~` expanded then resolved |
| CF-000161 | FP-12 (pack 30) options listed only once a dash is typed; Contract §8 empty token gives subcommands then options | empty token -> commands then option names; a dash prefix -> options only |
| CF-000162 | FP-02 (pack 20) False-default flag stays hidden even with show_default; Contract §4 shows it | shown (`[default: False]`) |
| CF-000163 | FP-05 (pack 23) Choice case-sensitive by default; Contract §5 enum choices ignore case by default (and `case_sensitive=True` signature) | list choices case-sensitive by default; `Enum` choices always match ignoring case |

## Other choices / known gaps
* Contract wording "Exception class names other than those in section 1 are the implementer's choice": the
  exceptions are `OptlynException`, `UsageError`, `BadParameter`, `MissingParameter`, `NoSuchOption`,
  `FileError`, `Exit`, plus `DeclarationError` (subclass of both `TypeError` and `ValueError`) for invalid declarations.
  Chaining-group nesting violations raise `RuntimeError`.
* Declaration errors are raised when the decorator is applied (the `Option`/`Argument` is built then).
* Missing/unknown subcommand in a *chaining* group runs the group callback first (children are resolved after it).
* `CliRunner(capture="fd")`: stdout and stderr are captured separately from real descriptors 1/2; `output` is
  stdout followed by stderr rather than strictly interleaved.
* Not implemented: Windows-only argument glob expansion and Windows console color (Linux is the supported target).
* `help_option_names` filtering keeps the declared order; the PowerShell script is untested against a real shell.
* `get_pager_file`/`echo_via_pager` use a pager only when stdin or stdout is a TTY and `PAGER` is set.

## Checklist coverage
Every id in `spec/CHECKLIST.md` is covered by the modules above, mapped by pack:
packs 01-05 (package layout, exports, hardware/runtime constraints): `__init__.py`, `pyproject.toml`;
pack 06 (exit statuses, channels, help page, version page): `core.py`, `exceptions.py`, `decorators.py`;
packs 07-08, 19-22 (commands, groups, options, arguments): `core.py`, `decorators.py`, `parser.py`;
packs 09, 23 (types): `types.py`; packs 10, 25 (context): `core.py`, `globals.py`;
packs 11, 29 (terminal helpers): `utils.py`, `termui.py`, `formatting.py`; packs 12, 30 (completion): `shell_completion.py`;
packs 13, 32 (runner): `testing.py`; packs 24, 28 (groups/chaining): `core.py`; packs 26, 27 (prompts, files): `termui.py`, `types.py`, `utils.py`;
packs 31, 33 (exit status, cross-cutting): `core.py`. Items marked "decision" (implementer's choice) are resolved
by the forms chosen above. Tests exist for a representative subset (`tests/test_basic.py`); the rest are implemented without a dedicated test.
