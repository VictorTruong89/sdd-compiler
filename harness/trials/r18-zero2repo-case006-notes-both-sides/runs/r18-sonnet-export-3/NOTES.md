# Optlyn build notes

Package: `src/optlyn` (pure Python, no dependencies, Python 3.10+). Run with `PYTHONPATH=src`.
Tests: `PYTHONPATH=src python -m pytest tests`.

Module map (spec pack -> code):
- packs 04-05 (package/exports): `__init__.py`
- packs 06, 20 (output forms, help, version): `core.py` (Command/Group help), `formatting.py`, `decorators.py`
- packs 07, 19, 24, 28 (commands, groups, chaining, collections): `core.py`, `decorators.py`
- packs 08, 21, 22 (options, arguments): `core.py`, `parser.py`
- packs 09, 23, 27 (types, files, paths): `types.py`, `utils.py`
- packs 10, 25 (context, sources, env prefix, default map): `core.py`, `globals.py`
- packs 11, 26, 29 (terminal helpers, prompts): `termui.py`, `utils.py`
- packs 12, 30 (completion): `shell_completion.py`
- packs 13, 32 (runner): `testing.py`
- packs 31 (exit codes): `core.Command.main`, `exceptions.py`
- packs 01-03, 14-18, 33: constraints / overview, satisfied by layout (src layout, no deps, no I/O on import).

Not individually traced: I did not annotate code with `# spec: <id>` markers and did not map each of the
1044 checklist ids one by one. Coverage is by pack, from reading every pack's text. Known gaps / approximations:
- Windows-only argument glob expansion is not implemented (target is Linux).
- Completion scripts for the four shells follow the usual shape but were not run in real shells.
- Progress bar rendering/ETA is a straightforward implementation; exact look is implementer's choice.

## Contradictions (28 unsettled) and what I built

Rule used: where the Interface Contract (`Interface_Contract.md`) states a concrete form and the PRD says
otherwise, I followed the Contract. Exceptions are listed explicitly.

- CF-000010 (omitted repeatable option): FP-01 "is passed as an absent value" vs FP-03 "receives an empty tuple".
  Built: `()`  (Contract "Delivered values": omitted repeatable option -> `()`).
- CF-000016, CF-000092 (clamp beyond an open bound, IntRange): FP-05 "nearest included value / adjacent integer"
  vs Contract "a value beyond an open bound becomes that bound's value". Built: the bound's own value.
- CF-000100, CF-000107 (FloatRange clamp with open bound): FP-05 "refuses clamp when a bound is open" vs Contract
  "With clamp=True and an open bound, a value beyond that bound becomes the bound". Built: allowed; becomes the bound.
  Only min > max raises at construction.
- CF-000034, CF-000072 (default map vs environment): FP-03 ranks environment above default map; Contract section 6
  says default-map values take precedence over environment. Built: command line > default map > environment > declared default
  (prompt, when it runs, is above all).
- CF-000047 (epilog position): FP-02 "end of help page" vs Contract attrs "right after the description, before the options".
  The Contract's own help-page list puts the epilog last (item 6). Built: epilog printed last.
- CF-000048 (counting option omitted): FP-03 "zero if omitted" vs Contract "None when the option was omitted". Built: `None`.
- CF-000063 (short help): FP-02 "first sentence, ellipsized to wrap width" vs Contract "start of first paragraph, cut with `...` at 45".
  Built: Click-style algorithm with limit 45 (stops at a sentence end if it fits, else `...`). Explicit `short_help` replaces it.
- CF-000087 (max content width 80 vs 100): FP-02 says 80, FP-11 says 100. Built: 80 for auto-detected width
  (explicit `terminal_width` is used as-is); in a default environment the terminal fallback width is 80 anyway.
- CF-000088 (envvar list): FP-03 "first one set wins" vs Contract "last name that is set wins". Built: last set wins.
- CF-000115 (default metavar): FP-02 "type name uppercase" vs example `--count COUNT`. Built: type name uppercase (`--count INTEGER`).
- CF-000128 (pause when not interactive): "does nothing" vs "still prints its message". Built: prints the message, never blocks.
- CF-000129 (app dir): FP-11 `$XDG_CONFIG_HOME` vs Contract "always under `~/.config`". Built: always `~/.config/<name>` on Unix.
- CF-000134 (confirmation mismatch): FP-08 "asks the pair again" vs FP-13 "abort". Built: ask the pair again (EOF still aborts).
- CF-000136 (DateTime formats): FP-05 "replaces the default list" vs the PRD inventory "added to the defaults". Built: replaces.
- CF-000151, CF-000157 (boolean text): FP-05 "any other value turns env flag off" vs FP-03/Type text "usage error".
  Built: unrecognised non-empty text is a usage error for typed values and for bool flags read from env;
  whitespace-only env value deactivates; non-bool `flag_value` flags treat unrecognised env text as unset.
- CF-000154 (isolated_filesystem): "removes directory" vs "always left in place". Built: removed unless `temp_dir` is given.
- CF-000155 (callback on missing parameter): Terminology "not called" vs FP-03 "still runs its callback". Built: runs (value `None`/`()`).
- CF-000156 (form feed): FP-02 "text after is omitted" vs Contract "dropped and text after is kept". Built: the character is dropped, text after is kept.
- CF-000158 (DateTime match): FP-05 "first success" vs Contract "last matching format". Built: last matching format.
- CF-000159 (prompt conversion failure): FP-08 "re-ask" vs FP-13 "not asked again". Built: re-ask until valid or EOF (EOF aborts).
- CF-000160 (`~` in Path resolve): FP-09 "not expanded" vs Contract "expanded first". Built: expanded.
- CF-000161 (options in completion of empty token): FP-12 "only after a dash" vs Contract "subcommand names followed by option names".
  Built: empty token lists subcommands then options; a dash-prefixed token lists options only.
- CF-000162 (show_default for False flag): FP-02 hidden vs Contract shown. Built: shown (`default: False`).
- CF-000163 (Choice case): FP-05 case-sensitive by default vs Contract "enum members matched by name, ignoring case by default",
  while the Contract signature says `case_sensitive=True`. Built: `case_sensitive=None` means sensitive for iterables,
  insensitive for Enum classes; explicit True/False is honoured.
