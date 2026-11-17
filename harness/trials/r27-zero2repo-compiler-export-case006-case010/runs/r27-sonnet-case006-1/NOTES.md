# NOTES

Package `optlyn` lives in `src/optlyn` (pure Python, no dependencies, Python >= 3.10).
Run with `PYTHONPATH=src`. Smoke tests: `tests/test_smoke.py`.

Modules: `core` (Context, Command, Group, CommandCollection, Parameter, Option, Argument),
`decorators`, `types`, `parser`, `formatting`, `termui`, `utils`, `shell_completion`,
`testing` (CliRunner), `exceptions`, `globals_`.

## Checklist accounting

Every id in `spec/CHECKLIST.md` is addressed by the implementation below; requirement ids were
implemented as written unless listed here. Decision ids that say "implementer's choice"
(N-000790, N-000802, N-000811, N-000822, N-000824, N-000830, N-000841, N-000845, N-000848,
N-001029, N-001030, N-001037, ...) are satisfied by the choices described in this file.

Not done / partially done:
- Windows-only behaviour (glob/`~`/env expansion of argv on Windows, Windows color support):
  not implemented; the supported target is Linux. `get_app_dir` does have a Windows branch.
- `PAGER`-less pager fallbacks (`less`/`more`) are not tried; without `PAGER` text goes to stdout.
- `getchar` has only the Unix implementation.

## Spec disagreements and what I built

Where the spec contradicts itself I followed the behaviour of the classic option-parser toolkit
this spec describes (first-listed PRD behaviour where the PRD is explicit), and recorded each:

1. **Omitted repeatable option, no default** — PRD FP-01 (pack 19/N-000093) "passed as an absent
   value" vs FP-03 / Contract "Delivered values" (N-000211): `()`. Built: `()`.
2. **IntRange clamp past an open bound** — PRD FP-05 (N-000362) "adjacent integer inside the range"
   vs Contract §5 (N-000941) "that bound's value". Built: adjacent integer inside the range.
3. **FloatRange clamp with an open bound** — PRD (N-000364, N-000381) "clamp only allowed when both
   bounds closed / declaration error" vs Contract §5 (N-000943) "becomes the bound". Built: raises
   `TypeError` at construction.
4. **Counting option omitted** — PRD FP-03 (N-000207) "zero" vs Contract (N-000920) `None`.
   Built: `0`.
5. **Environment vs default map** — PRD FP-03 (N-000243/N-000245) command line > env > default map >
   default vs Contract §6 (N-000955) "default map takes precedence over environment". Built: env wins.
6. **Envvar list** — PRD (N-000227) "first one set wins" vs Contract §4 (N-000893) "last name set
   wins". Built: first set wins.
7. **Epilog position** — PRD FP-02 (N-000126) end of page vs Contract §3 (N-000853) "right after the
   description". Built: end of the help page.
8. **Subcommand short help** — PRD (N-000122) first sentence vs Contract §2 (N-000843) start of
   first paragraph cut with `...` at 45 characters. Built: Click-style `make_default_short_help`
   with a 45 character limit (stops at the first sentence end if it fits, else `...`).
9. **Max content width** — PRD FP-02 (N-000134) 80 vs FP-11 (N-000680) 100. Built: 80 for help pages
   (`HelpFormatter`); `wrap_text` default width is 78. An explicit `terminal_width` is used as-is.
10. **Default metavar** — PRD (N-000140) type name upper-cased vs example `--count COUNT`
    (N-000144). Built: type name upper-cased (`--count INTEGER`; text -> `TEXT`; choice -> `[a|b]`).
11. **Pause when not interactive** — PRD (N-000663) does nothing vs (N-000687) still prints its
    message. Built: never blocks, prints the message (plus newline) and returns.
12. **App dir** — PRD FP-11 (N-000676) honours `$XDG_CONFIG_HOME` vs Contract §7 (N-001005) always
    `~/.config`. Built: `$XDG_CONFIG_HOME` when set and non-empty.
13. **Confirmation mismatch** — PRD FP-08 (N-000511) re-ask the pair vs FP-13 (N-000723) abort.
    Built: re-ask; end of input aborts (exit 1).
14. **DateTime formats** — PRD overview (N-000032) "added to defaults" and Contract §5 "last
    matching format used" vs FP-05 (N-000356) "replaces the default list", first success wins.
    Built: custom list replaces defaults; first match wins.
15. **Boolean flag from env, bad text** — PRD (N-000344) usage error vs (N-000345) "turns the flag
    off". Built: usage error naming the option (FP-03 detail); for a flag with a non-boolean
    flag-value, unrecognised text is treated as unset.
16. **Form feed in help** — Contract §3 `help=`: "form-feed dropped, text after kept" vs PRD FP-02
    "text after it omitted". Built: a docstring is truncated at the form feed; an explicit `help=`
    string only has the character removed.
17. **`show_default` on a False flag** — Contract §4 "a flag whose default is False included" vs
    PRD FP-02 "stays hidden". Built: hidden (PRD).
18. **Choice over an Enum** — Contract §5 "by default ignores letter case" vs signature
    `case_sensitive=True` and PRD "case-sensitive unless turned off". Built: case-sensitive by default.
19. **Path `resolve_path` and `~`** — Contract §5 "leading `~` expanded first" vs PRD FP-09 "tilde not
    expanded". Built: `~` is expanded (Contract), then symlinks are resolved.
20. **Completion for an empty token** — Contract §8 "subcommand names followed by option names" vs
    PRD FP-12 "options only once a dash is typed". Built: options only after a dash.
21. **Isolated filesystem cleanup** — PRD FP-14 says both "removed when no parent given" and "always
    left in place". Built: removed on exit when no `temp_dir`, kept when `temp_dir` is given.
22. **Parameter callback for omitted parameters** — Terminology says not called, FP-03 says a
    missing parameter still runs its callback. Built: always called.
23. **Prompt conversion failure** — FP-08 re-asks; FP-13 says "not asked again". Built: re-ask.
24. **`CliRunner` exit code with `standalone_mode=False`** — a raised exception gives exit code 1.

Other choices (spec says "implementer's choice"): usage placeholder `[OPTIONS]`; help sections
`Positional arguments`, `Options`, `Commands`; extras rendered as `[default: x; env var: X;
required]`; deprecation mark `(Deprecated)`/`(DEPRECATED)`; `invoked_subcommand` on a chaining group
is `"*"`; parameter sources are members of `optlyn.ParameterSource`; completion entries are
`type,value` lines (`dir`/`file` for path requests); declaration errors raise `DeclarationError`
(subclass of both `ValueError` and `TypeError`); attaching a group under a chaining group raises
`RuntimeError`.
