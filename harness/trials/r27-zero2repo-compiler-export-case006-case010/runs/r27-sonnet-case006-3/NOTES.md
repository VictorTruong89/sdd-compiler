# Notes

Package: `src/optlyn` (pure Python, no dependencies, Python >= 3.10). Run with `PYTHONPATH=src`.
All checklist ids are implemented in the package unless listed below under "Not done".
Modules: `core` (Context/Command/Group/Parameter/Option/Argument), `parser`, `types`, `termui`,
`utils`, `formatting`, `shell_completion`, `decorators`, `testing`, `exceptions`, `globals`.

## Spec disagreements and what was built

Rule of thumb: where the Interface Contract (shell) states a concrete form, it wins over the PRD.

Flagged conflicts (CF ids):
- CF-000010 (omitted repeatable option: N-000093 "absent value" vs N-000211 / Contract "empty tuple"): built `()`.
- CF-000016/92/100/107 (clamp with open bound; N-000361/362/381/364 "nearest included value / adjacent integer / FloatRange refuses clamp with open bound" vs Contract N-000941/943 "becomes the bound"): built the Contract: clamp returns the bound's own value; FloatRange accepts clamp with open bounds. FloatRange raises only when min > max.
- CF-000034/72 (N-000243/245 env above default map vs N-000955 "default map takes precedence over env"): built command line > default map > environment > declared default; prompt (when it runs) is most explicit.
- CF-000047 (epilog: N-000126 end of page vs N-000853 "right after the description"): built end of the page (also the Contract help-page order, item 6).
- CF-000048 (counting option omitted: N-000207 zero vs N-000920 `None`): built `None`.
- CF-000063 (short help: N-000122 first sentence vs N-000843 first paragraph cut with `...` at 45 chars): built the 45-char cut (a short first sentence is used whole).
- CF-000087 (max content width 80 vs 100): built 100; auto-detected width = min(terminal, 100) - 2; explicit `terminal_width` is used as-is.
- CF-000088 (envvar list: N-000227 first wins vs N-000893 last wins): options use the last set name (Contract); arguments use the first set name (PRD FP-04, no conflict recorded for arguments).
- CF-000115 (metavar N-000140 type name vs N-000144 `--count COUNT`): built-in types (str/int/float/bool/UUID/Path/File/...) show the upper-cased destination name (`--count COUNT`); Choice shows `[a|b]`; a custom `ParamType` shows its `name` upper-cased.
- CF-000128 (pause non-interactive: N-000663 does nothing vs N-000687 prints message): prints the message, never blocks.
- CF-000129 (app dir: N-000676 XDG_CONFIG_HOME vs N-001005 always `~/.config`): built `~/.config` (XDG ignored).
- CF-000134 (confirmation mismatch: N-000511 ask again vs N-000723 abort): built ask again; EOF is an abort.
- CF-000136 (DateTime formats: N-000032 added vs N-000356 replaces): built replace.
- CF-000151 (bool conversion: N-000344 error vs N-000345 other value turns flag off): built usage error for text and for env values of a bool flag (FP-03 says conversion error).

Unflagged disagreements:
- Form feed in help: Contract says an explicit `help=` keeps the text after `\f` (only the char is dropped); PRD says a docstring is truncated at `\f`. Built both: docstrings truncate, explicit `help=` only drops the character.
- DateTime with several matching formats: Contract "last matching format is used" vs PRD "first success wins". Built the Contract (last match).
- `show_default` for a bool flag whose default is False: Contract "shown ... a flag whose default is False included" vs PRD "stays hidden". Built the Contract (shown).
- `Path(resolve_path=True)`: Contract "a leading `~` is first expanded" vs PRD "a leading tilde is not expanded". Built the Contract (expanded).
- Parameter callback for an omitted parameter: Terminology says it is not called; FP-03 says a missing parameter still runs its callback. Built: callback always runs (receives `None`/`()`).
- `CliRunner.isolated_filesystem`: PRD says the directory is removed when no parent is given AND that it is "always left in place". Built: removed when `temp_dir` is None, kept when a parent is supplied.
- Completion for an empty token: Contract says subcommand names then option names; PRD says options only after a dash. Built the Contract (empty token -> commands, then options; non-empty token not starting with a prefix -> commands only).
- Enum `Choice`: Contract says "by default the match ignores letter case"; the signature says `case_sensitive=True`. Built `case_sensitive` as given (default True) for enums and lists alike.
- Chaining group with `standalone_mode=False` returns the list of child return values even if a result callback is registered (PRD FP-10); the result callback is still called.
- Second variadic argument: refused (TypeError) when the command is parsed, not at declaration.

## Not done
- Windows-only glob expansion of argv is a simple best-effort (`os.name == "nt"` only); not testable on Linux.
- `capture="fd"`: `output` interleaves interpreter writes in order; if OS-level writes occurred, `output` is stdout bytes followed by stderr bytes.
