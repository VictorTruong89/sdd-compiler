# Notes: specification conflicts and the choice made

Where the PRD and the Interface Contract (or the PRD with itself) disagree, the Contract wins
(it is the more specific document); otherwise the more detailed PRD sentence wins.

| Conflict | Choice |
| --- | --- |
| Counting option omitted: PRD "zero", Contract "`None`" | `None` (an explicit `default=` is honoured). |
| `show_default` on a flag with default `False`: PRD hides it, Contract shows it | Shown. |
| `DateTime`: PRD "first success wins", Contract "last matching format" | Last matching format. Custom formats replace the default list. |
| `Path(resolve_path=True)`: PRD "no tilde expansion", Contract "expand `~` first" | Expand, then `realpath`. |
| `envvar` list: PRD "first set wins", Contract "last set wins" | Last set wins (options and arguments share the code). |
| `get_app_dir` on Unix: PRD honours `XDG_CONFIG_HOME`, Contract "always under `~/.config`" | Always `~/.config`. |
| Completion of an empty token: PRD "options only after a dash", Contract "subcommands then options" | Subcommands then options. |
| `help=` with a form feed: PRD (docstring) truncates, Contract (`help` keyword) drops the character and keeps the rest | Docstrings are truncated at `\f`; an explicit `help=` only loses the `\f` character. |
| Epilog position: Contract `command` attrs "after description", help-page section "last" | Last on the page (PRD). |
| Default `max_content_width`: PRD FP-02 80, FP-11 100 | 80. Under `CliRunner` the width is forced to 80. |
| Choice with an `Enum`: Contract "matched ignoring case by default", signature `case_sensitive=True` | Exact name match first, then a case-insensitive fallback for enums; plain choices are case-sensitive unless `case_sensitive=False`. |
| Boolean flag env var with junk text: FP-03 usage error, FP-05 "turns flag off" | Usage error. |
| Parameter callback for an omitted parameter: Terminology "not called", FP-03 "still runs" | Called (with `None`), so it can derive a default from earlier values. |
| Integer option metavar: PRD example `--count COUNT`, rule "type name upper-case" | Type name: `--count INTEGER`. |
| `pause` when not interactive: "does nothing" vs "still prints its message" | Prints the message, never blocks. |
| `isolated_filesystem`: directory removed vs "always left in place" | Removed when no parent is given; kept when `temp_dir` is given. |
| Chaining group, `standalone_mode=False` | Returns the list of child return values even when a result callback exists (the callback is still called). |
| Short help in group listings | First sentence / first paragraph, cut with `...` at 45 characters. |
| Pager "interactive" | stdin **or** stdout is a TTY (PRD terminology). |

Declaration errors (invalid keyword combinations, bad style colors, clamped open `FloatRange`)
raise `optlyn.exceptions.DeclarationError`, which subclasses `TypeError`, `ValueError` and `KeyError`.
