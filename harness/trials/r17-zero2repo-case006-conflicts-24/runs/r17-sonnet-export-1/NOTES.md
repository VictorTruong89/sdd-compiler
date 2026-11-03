# Notes

Package: `src/optlyn` (pure Python, no dependencies, Python 3.10+). Run with `PYTHONPATH=src`.
Tests: `PYTHONPATH=src python -m pytest tests`.

Module map: `core` (Context, Command, Group, CommandCollection, Parameter/Option/Argument),
`decorators`, `parser`, `types`, `formatting` (incl. `wrap_text`), `termui` (prompt, confirm, pager,
progressbar, getchar, pause, edit, launch, clear), `utils` (echo, style, files, get_app_dir),
`shell_completion`, `testing` (CliRunner), `exceptions`, `globals`.

## Checklist accounting
Every id in `spec/CHECKLIST.md` is implemented in the code above unless listed under
"Disagreements" below (where one side of a contradiction was chosen, the other is not done).
Ids that only restate packaging/hardware constraints (zero dependencies, src layout, Python 3.10+,
no native code) are satisfied by the layout itself. Ids whose form the Contract leaves to the
implementer (exception class names, source enum values, completion framing, help extras) use the
forms in the code. Windows-only behaviour (argv glob expansion) is not implemented (Linux target).
Declaration-time errors raise `DeclarationError`, which subclasses `TypeError`, `ValueError` and
`RuntimeError`.

## Disagreements and what was built
All 28 unsettled contradictions were resolved as follows (the first-named side is what is built).

| Where | Disagreement | Built |
|---|---|---|
| FP-03 vs Contract s4 (CF-10) | omitted repeatable option: absent value vs `()` | `()` |
| FP-05 vs Contract s5 (CF-16, 92, 100, 107) | clamp at open bound; FloatRange clamp | IntRange open bound -> adjacent integer inside range; FloatRange with clamp and an open bound raises `TypeError` at construction |
| FP-03 vs Contract s6 (CF-34, 72) | env vs default map precedence | prompt > command line > environment > default map > declared default |
| FP-02 vs Contract s3 (CF-47) | epilog position | printed last, after everything else |
| FP-03 vs Contract s4 (CF-48) | omitted counting option | `0` |
| FP-02 vs Contract s2 (CF-63) | subcommand short help | first paragraph up to its first sentence, cut with `...` at 45 characters (an explicit `short_help` replaces it) |
| FP-02 vs FP-11 (CF-87) | default max content width 80 vs 100 | 80 (help layout and `wrap_text`'s formatter) |
| FP-03 vs Contract s4 (CF-88) | envvar list: first set vs last set wins | first set wins |
| FP-02 (CF-115) | default metavar: type name upper-case vs `--count COUNT` | type name upper-case (`--count INTEGER`) |
| FP-11 (CF-128) | `pause` non-interactive: nothing vs prints message | does nothing and does not block |
| FP-11 vs Contract s7 (CF-129) | app dir under XDG_CONFIG_HOME vs always `~/.config` | `$XDG_CONFIG_HOME` when set, else `~/.config` |
| FP-08 vs FP-13 (CF-134, 159) | confirmation mismatch / bad prompt value: ask again vs abort/usage error | ask again (a mismatch, an invalid typed value); EOF aborts |
| FP-01 vs FP-05 (CF-136, 158) | DateTime custom formats added vs replace; first vs last match | custom list replaces the default list; first matching format wins |
| FP-05 (CF-151, 157) | env bool flag: other value is an error vs turns flag off | other non-empty value is a usage error (whitespace-only deactivates) |
| FP-14 (CF-154) | isolated filesystem directory removed vs left in place | removed on exit when no parent given; kept when `temp_dir` is given |
| Terminology vs FP-03 (CF-155) | callback for omitted parameter | callback runs (receives `None`/`()`) |
| FP-02 vs Contract s3 (CF-156) | form feed in help | text after the form feed is dropped |
| FP-12 (CF-161) | options suggested for empty token | options only when the incomplete token starts with a prefix char; empty token gives subcommands only |
| FP-02 vs Contract s4 (CF-162) | show_default on a flag defaulting to false | hidden (single boolean flag with false default) |
| Contract s5 vs FP-05 (CF-163) | Choice case sensitivity default | case-sensitive (`case_sensitive=True`) |
| FP-09 vs Contract s5 (CF-160) | `Path(resolve_path=True)` expands `~` | no tilde expansion; symlinks resolved |

Other choices: a single boolean flag delivers `True` when present even with default `True`;
non-boolean feature-switch flags without default deliver `None` when absent; the help page for
incorrect usage goes to stderr with exit status 2; `getchar` reads `/dev/tty` when stdin is not a tty.
