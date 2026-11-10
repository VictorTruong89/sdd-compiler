# Optlyn implementation notes

Package: `src/optlyn` (pure Python, no dependencies; run with `PYTHONPATH=src`).
Modules: `core` (Context, Parameter/Option/Argument, Command/Group/CommandCollection), `parser`,
`types`, `formatting`, `utils` (echo/style/files/pager), `termui` (prompt/confirm/progress/editor...),
`decorators`, `shell_completion`, `testing` (CliRunner).

## Spec disagreements and what was built

Chosen sides are marked **Built**.

1. **Form feed in help (C-01)** – PRD FP-02: text after `\f` is omitted. Contract §3 `command`: the `\f` is dropped and the text after it kept. **Built:** PRD (truncate at `\f`).
2. **Short help on a group page (C-02)** – PRD: first sentence, ellipsized at wrap width. Contract §2: first paragraph, cut with `...` at 45 characters. **Built:** first paragraph, stopped at the first sentence end, cut with `...` when longer than the available width (page width minus name column). An explicit `short_help` replaces it.
3. **Epilog position (C-03)** – PRD: last thing on the page. Contract: right after the description. **Built:** PRD, at the end.
4. **Max content width (C-04)** – PRD FP-02: 80. PRD FP-11: 100. **Built:** 80 for help pages (auto width = min(terminal, 80) − 2, min 50; an explicit `terminal_width` is used as-is). `CliRunner` forces 80 as the wrap width. `wrap_text` default width is 78.
5. **Default metavar example (C-05)** – PRD says the type name uppercased, but its example shows `--count COUNT` for an int. **Built:** the rule: `--count INTEGER` (`TEXT`, `FLOAT`, `BOOLEAN`, ...); a Choice shows `[a|b]`.
6. **show_default for a False flag (C-06)** – PRD FP-02: stays hidden. Contract §4: shown. **Built:** Contract (shown, e.g. `[default: False]`) when show-default is on.
7. **Omitted counting option (C-07)** – PRD: 0. Contract: `None`. **Built:** 0 (PRD).
8. **Env var list (C-08)** – PRD: first set wins. Contract: last set wins. **Built:** first set wins (PRD).
9. **Unrecognised env value for a bool flag (C-09)** – PRD FP-03: usage error. PRD FP-05: turns the flag off. **Built:** usage error naming the option (whitespace-only/empty after strip deactivates).
10. **Prompt when fully omitted (C-10)** – with `prompt_required=True` (default) an omitted option prompts; with `prompt_required=False` only a bare flag prompts and a fully omitted option uses its default.
11. **Mismatched confirmation (C-11)** – PRD FP-08 re-asks the pair; FP-13 says abort. **Built:** re-ask (FP-08).
12. **Conversion failure at a prompt (C-12)** – FP-08 re-asks; FP-13 says it is not asked again. **Built:** re-ask until valid or EOF (EOF aborts).
13. **DateTime precedence (C-13)** – PRD first match wins; Contract last match. **Built:** first match wins.
14. **Author datetime formats (C-14)** – inventory says extend defaults; FP-05 says replace. **Built:** replace.
15. **Enum Choice case (C-15)** – Contract says case-insensitive for enums by default; `case_sensitive=True` is the default. **Built:** case-sensitive unless `case_sensitive=False`; enum members matched by name.
16. **IntRange clamp at an open bound (C-16)** – PRD: adjacent inside integer; Contract: the bound's value. **Built:** PRD (`bound ± 1`).
17. **FloatRange clamp with open bound (C-17)** – PRD: refused at declaration. Contract: accepted. **Built:** `TypeError` at construction.
18. **`~` with `resolve_path` (C-18)** – PRD: not expanded. Contract: expanded. **Built:** not expanded (PRD); `os.path.realpath` only.
19. **`get_app_dir` on Unix (C-19)** – PRD honours `XDG_CONFIG_HOME`; Contract says always `~/.config`. **Built:** PRD (empty/unset `XDG_CONFIG_HOME` falls back to `~/.config`).
20. **Option suggestions for an empty token (C-20)** – PRD: only after a dash. Contract: subcommands then options. **Built:** PRD; an empty token yields subcommand names only (arguments' path requests for argument slots).
21. **Interactive session (C-21)** – Terminology is self-contradictory. **Built:** interactive means both stdin and stdout are TTYs (pager, pause).
22. **Callback for omitted parameter (C-22)** – Terminology: not called. FP-03: called. **Built:** called (with `None`/`()`), so it can default from earlier values.
23. **Default map vs environment (C-23)** – PRD: command line, environment, default map, default. Contract: default map over environment. **Built:** PRD order.
24. **Group with only options (C-24)** – no-args help only triggers when the argument list is empty (usage error, exit 2, help on stderr). Options with no subcommand give `Missing command.` without the help page.
25. **Isolated filesystem dir (C-25)** – removed on exit when no `temp_dir` was given; left in place when a parent is supplied.

Additional internal PRD inconsistencies:
- **`pause` when not interactive** – FP-11 says "does nothing" and later "still prints its message". **Built:** prints the message, does not wait.
- **Heading names** – the spec fixes `Positional arguments` and `Options`; the group list is headed `Commands`.
- **Flag with default True** – a plain `--flag` always delivers `True` when present (`flag_value` defaults to `True`).
- **Fd capture ordering** – with `capture="fd"` the combined `output` interleaves stdout/stderr by arrival at the capture reader, which is approximate across streams.
