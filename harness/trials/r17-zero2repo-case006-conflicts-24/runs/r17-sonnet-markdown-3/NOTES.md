# Notes

Optlyn lives in `src/optlyn` (pure Python, no dependencies). Run tests with
`PYTHONPATH=src python -m pytest tests`.

## Spec disagreements and the choice made

Where `Full_PRD.md` and `Interface_Contract.md` (or two parts of the PRD) disagree, the PRD's
behavioural statement was followed unless noted.

| # | Disagreement | Built |
|---|---|---|
| 1 | Env var list on an option: contract says "last name set wins"; PRD says "first one set wins". | First set wins (options and arguments). |
| 2 | `DateTime` with several matching formats: contract "last matching"; PRD "first success wins". | First success wins. |
| 3 | `Path(resolve_path=True)`: contract expands leading `~`; PRD says tilde is not expanded. | No tilde expansion (symlinks resolved). |
| 4 | Counting option omitted: contract `None`; PRD "zero if omitted". | `0`. |
| 5 | `show_default` on a single bool flag defaulting to false: contract shows it; PRD hides it. | Hidden (a true default is shown). |
| 6 | `FloatRange` clamp with an open bound: contract clamps to the bound; PRD says declaration error. | `TypeError` at construction. |
| 7 | `IntRange` clamp with open bound: contract "that bound's value"; PRD "adjacent integer inside". | Adjacent integer inside the range. |
| 8 | `Choice` over an Enum: contract says case-insensitive by default; PRD says case-sensitive unless turned off. | Case-sensitive unless `case_sensitive=False`. |
| 9 | Epilog position: contract (command attrs) says right after description; help-page list and PRD say last. | Printed last. |
| 10 | Group short help: contract "cut at 45 characters"; PRD "first sentence, ellipsized at the wrap width". | First sentence, limit derived from the width (45 when `get_short_help_str()` is called with no limit). |
| 11 | Max content width: PRD FP-02 says 80, FP-11 says 100. | 80 (`HelpFormatter`; `wrap_text` default width 78). Inside `CliRunner` the width is 80. |
| 12 | Form feed in `help`: contract "text after it is kept"; PRD "text after is omitted". | Text after the form feed is omitted, the form feed itself is dropped. |
| 13 | Show options for an empty incomplete token: contract says subcommands then options; PRD says options only after a dash. | Options only once a dash is typed. |
| 14 | `get_app_dir` on Unix: contract "always under ~/.config"; PRD honours `XDG_CONFIG_HOME`. | `XDG_CONFIG_HOME` when set. |
| 15 | Date-time formats: inventory says author formats are added to defaults; FP-05 says they replace. | Replace. |
| 16 | Bool flag env value: FP-03 says an unknown non-empty string is a usage error; FP-05 says it turns the flag off. | Usage error (whitespace-only deactivates). |
| 17 | Parameter callback on an omitted parameter: Terminology says not called; FP-03 says it still runs (value `None`). | Called with `None`. |
| 18 | `pause()` when not interactive: FP-11 normal says does nothing; boundary says it still prints the message. | Prints the message, does not wait. |
| 19 | `isolated_filesystem`: "removed when no parent" vs "always left in place". | Removed when no `temp_dir`; kept when a parent is given. |
| 20 | Interactive session definition (stdin TTY, or stdin/stdout TTY, but piped stdin is not). | Interactive when stdin or stdout is a TTY. |
| 21 | Integer option metavar: PRD example `--count COUNT`, rule "type name uppercase". | Type name: `--count INTEGER`. |
| 22 | `ctx.invoke(cmd, **values)`: "exactly the caller's values" vs filling declared defaults. | Missing parameters of the target are filled with their defaults. |
| 23 | Boolean flag with default `True` and no `flag_value`: PRD says present yields true. | `flag_value` is `True`. |
