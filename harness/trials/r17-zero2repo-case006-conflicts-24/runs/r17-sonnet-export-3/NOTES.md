# Notes

Implementation: pure-Python package `optlyn` in `src/optlyn` (no dependencies, no build step).
Tests: `PYTHONPATH=src python -m pytest tests`.

## Spec contradictions and the choice made for each

The spec has 28 unsettled contradictions (CF ids). Choices:

| CF | disagreement | built |
|---|---|---|
| 10 | omitted repeatable option: absent value vs empty tuple | empty tuple `()` |
| 16, 92 | IntRange clamp at an open bound: "adjacent integer" (PRD) vs "the bound" (contract) | adjacent integer inside the range (PRD) |
| 100, 107 | FloatRange clamp with open bound: refused (PRD) vs clamps to the bound (contract) | `TypeError` at construction (PRD) |
| 34, 72 | default map vs environment precedence | command line > environment > default map > declared default (PRD) |
| 47 | epilog position | printed last on the help page (PRD item list, contract help-page order) |
| 48 | counting option omitted: 0 vs None | `0` |
| 63 | short help of children: first sentence vs 45-char cut | first sentence, cut with `...` at 45 characters (both rules applied) |
| 87 | max content width 80 vs 100 | 80 (the runner also forces an 80 column width unless `terminal_width` is given) |
| 88 | env var list: first set vs last set | first set wins |
| 115 | metavar "type name" vs `--count COUNT` | built-in scalar types show the parameter's destination name upper-cased (`--count COUNT`); custom `ParamType` shows its `name` upper-cased; Choice shows `[a|b]` |
| 128 | pause when not interactive | prints its message, does not block |
| 129 | app dir: `XDG_CONFIG_HOME` vs always `~/.config` | `XDG_CONFIG_HOME` honoured when set |
| 134, 159 | prompt confirmation / re-ask | invalid prompt values re-ask; EOF and declined confirmation abort (exit 1) |
| 136 | DateTime formats extend vs replace | a supplied list replaces the defaults |
| 151, 157 | bool env value other than known tokens: error vs off | usage error (whitespace-only value is off) |
| 154 | isolated_filesystem cleanup | directory removed on exit when no `temp_dir` given; kept when a parent is supplied |
| 155 | callback for omitted parameter | callback is called with the absent value (so it can default from earlier params) |
| 156 | form feed in help | text after the form feed is dropped |
| 158 | DateTime: first vs last matching format | first matching format |
| 160 | Path `resolve_path` and `~` | leading `~` is expanded, then realpath (contract) |
| 161 | options listed only after a dash vs after an empty token | an empty token lists subcommands then options; a token starting with a dash lists matching options only |
| 162 | show_default with a False flag | the default is shown (`default: False`) when show_default is on (contract) |
| 163 | Choice case sensitivity default | case-sensitive by default (signature `case_sensitive=True`); enum members matched by name |

Other choices: a group invoked with no arguments (default policy) prints its help to stderr and exits 2
(`NoArgsIsHelpError`). Declaration errors raise `DeclarationError` (subclass of both `ValueError` and `TypeError`).
Completion output lines: `type,value` (bash/powershell/fish; fish adds `\thelp`), zsh uses three lines per item;
path requests have type `dir` or `file` carrying the incomplete token.

## Checklist accounting

Every id in `spec/CHECKLIST.md` is covered by the modules in `src/optlyn` (the `# spec:` markers were not added
per id; the packs map one-to-one onto modules: parameters/commands/groups/context in `core.py`, types in
`types.py`, parsing in `parser.py`, help in `formatting.py`, terminal helpers in `termui.py`/`utils.py`,
completion in `shell_completion.py`, runner in `testing.py`).

Not done / not verified:
- Windows-only behaviour (argument glob expansion, `%APPDATA%` handling beyond a basic fallback).
- `getchar` on a real terminal and `launch`/`edit` against a real desktop are only exercised with stand-in programs.
