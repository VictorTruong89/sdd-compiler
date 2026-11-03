# Notes

Package: `src/optlyn` (pure Python >= 3.10, no dependencies). Modules: `core` (Context, Command, Group,
CommandCollection, Parameter/Option/Argument), `decorators`, `parser`, `types`, `termui`, `utils`,
`formatting`, `shell_completion`, `testing`, `exceptions`, `globals`.

Every checklist id (N-000775 … N-001044) is implemented in code, by the feature the pack describes;
nothing is deliberately left undone except the spec's own optional items ("MAY": Windows glob/arg
expansion, macOS/Windows-specific paths are only minimally handled). Where the spec leaves a form to the
implementer (reports wording, completion framing, session values, etc.) I chose click-like forms.

## Disagreements in the spec and what I built

Packs are referenced by number (Interface Contract = packs 04-13, PRD = packs 14-33).

1. CF-000010 – Omitted repeatable option, no default. FP-01 (pack 19, N-000093): "is passed as an absent
   value"; FP-03 (pack 21, N-000211): "receives an empty tuple, not an absent value"; Contract §4 (pack 08)
   also `()`. Built: `()`.
2. CF-000016 / CF-000092 – IntRange clamp on open bound. FP-05 (pack 23, N-000361/362): "the adjacent integer
   inside the range"; Contract §5 (pack 09, N-000941): "becomes that bound's value". Built: adjacent integer.
3. CF-000100 / CF-000107 – FloatRange clamp with open bound. FP-05 (N-000381, N-000364): refused/only allowed
   when both bounds closed; Contract §5 (N-000943): open bound clamps to the bound. Built: `TypeError` at
   construction.
4. CF-000034 / CF-000072 – Environment vs default map. FP-03 (pack 21, N-000243/245): command line, env,
   default map, default; Contract §6 (pack 10, N-000955): default_map "takes precedence over environment
   variables". Built: PRD order (env before default map).
5. CF-000047 – Epilog placement. FP-02 (pack 20, N-000126): at the end after everything; Contract §3
   (pack 07, N-000853): "right after the description, before the options" (but Contract §2 help list puts
   it last). Built: last.
6. CF-000048 – Omitted counting option. FP-03 (N-000207): zero; Contract §4 (N-000920): `None`. Built: `0`.
7. CF-000063 – Short help of children. FP-02 (N-000122): first sentence; Contract §2 (pack 06, N-000843):
   first paragraph cut with `...` at 45 characters. Built: click's rule — first paragraph, stops at the first
   sentence end, otherwise cut with `...` at 45 characters.
8. CF-000087 – Default max content width. FP-02 (N-000134): 80; FP-11 (pack 29, N-000680): 100. Built: 80.
9. CF-000088 – envvar list. FP-03/FP-04 (N-000227): first set wins; Contract §4 (N-000893): last set wins.
   Built: first set wins.
10. CF-000115 – default option metavar. FP-02 (N-000140): type name uppercase; same pack (N-000144) example
   `--count COUNT`. Built: type name upper-case (`--count INTEGER`) unless an author metavar is given.
11. CF-000128 – `pause` when not interactive. FP-11 (N-000663): does nothing; (N-000687): prints message but
   doesn't block. Built: prints the message, doesn't wait.
12. CF-000129 – app dir on Unix. FP-11 (N-000676): `$XDG_CONFIG_HOME` honoured; Contract §7 (N-001005): always
   under `~/.config`. Built: XDG honoured when set.
13. CF-000134 / CF-000159 – confirmation mismatch & invalid prompt answers. FP-08 (N-000511, N-000520):
   re-ask; FP-13 (pack 31, N-000723/N-000719): two different values abort / "not asked again". Built: re-ask
   on mismatch and conversion failure; EOF aborts (exit 1).
14. CF-000136 / CF-000158 – DateTime formats. Pack 14/16 (N-000032): author list "added to" defaults; FP-05
   (N-000356): replaces. Built: replaces. Contract (N-000939) "last matching format"; FP-05 (N-000354) "first
   success". Built: first success.
15. CF-000151 / CF-000157 – bool flag env value unrecognised. FP-03 (N-000238/344): usage error; FP-05
   (N-000345): turns flag off. Built: usage error (whitespace-only deactivates).
16. CF-000154 – isolated_filesystem. FP-14 (pack 32, N-000745): removed on exit when no parent given;
   (N-000747): always left in place. Built: removed when no `temp_dir`; left in place when `temp_dir` given.
17. CF-000155 – parameter callback for omitted param. Terminology (pack 15, N-000022): not called;
   FP-03 (N-000260): still runs. Built: runs (receives `None`/`()`).
18. CF-000156 – form feed. FP-02 (N-000115): text after is omitted; Contract §3 (N-000853 area): dropped and
   rest kept. Built: docstrings truncate at `\f`; an explicit `help=` string just loses the `\f` character.
19. CF-000160 – `Path(resolve_path=True)` tilde. FP-09 (N-000558): not expanded; Contract §5 (N-000947):
   expanded first. Built: not expanded.
20. CF-000161 – completion for empty token. FP-12 (N-000700): options only after a dash; Contract §8
   (N-001019): empty token gives subcommands then options. Built: subcommands only for empty token.
21. CF-000162 – show_default for a False single flag. FP-02 (N-000149): hidden; Contract §4 (N-000906):
   shown. Built: hidden.
22. CF-000163 – Choice case sensitivity. FP-05 (N-000348): case-sensitive by default; Contract §5
   (N-000937): enum matching ignores case by default. Built: case-sensitive by default (signature default).
