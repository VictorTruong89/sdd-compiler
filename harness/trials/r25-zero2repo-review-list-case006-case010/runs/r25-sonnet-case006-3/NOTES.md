# Optlyn implementation notes

Package: `src/optlyn` (pure Python, no dependencies, Python 3.10+). Run with `PYTHONPATH=src`.
Modules: `core` (Context/Command/Group/Parameter/Option/Argument), `parser`, `types`,
`decorators`, `termui`, `utils`, `formatting`, `shell_completion`, `testing`, `exceptions`.

## Spec disagreements and what was built

General rule: where the PRD and the Interface Contract disagree, the PRD wins (it describes
behaviour; the Contract is a shell), except where noted.

- **C-01 form feed.** PRD FP-02: text after `\f` is omitted. Contract §3 `command`: "dropped and
  the text after it is kept". Built: PRD — help text is truncated at the form feed.
- **C-02 short help.** PRD FP-02: first sentence, ellipsized if it does not fit the wrap width.
  Contract §2: first paragraph cut with `...` at 45 characters. Built: PRD — first sentence,
  cut with `...` at (page width - 6 - longest command name) characters.
- **C-03 epilog.** PRD: printed at the end of the page. Contract §3: "right after the description,
  before the options". Built: at the end.
- **C-04 max content width.** PRD FP-02 says 80, FP-11 says 100. Built: 80 for help pages and
  `HelpFormatter`; `wrap_text` default width is 78. An explicit `terminal_width` is used as-is.
- **C-05 default metavar.** PRD rule: type name upper-cased; its example says `--count COUNT`.
  Built: the rule — an int option shows `--count INTEGER`, text shows `TEXT`.
- **C-06 show-default of a False flag.** PRD: hidden; Contract §4: shown. Built: PRD (hidden for a
  single-name boolean flag whose default is false; shown when true).
- **C-07 omitted counting option.** PRD: `0`; Contract: `None`. Built: `0`.
- **C-08 envvar list.** PRD: first set wins; Contract: last set wins. Built: first set wins.
- **C-09 bad env value for a boolean flag.** PRD FP-03: usage error; FP-05: flag turns off.
  Built: usage error (a whitespace-only value deactivates).
- **C-10 prompt when omitted.** Both kept: a prompting option prompts when omitted by default
  (`prompt_required=True`); with `prompt_required=False` it prompts only when given with no value.
- **C-11 mismatched confirmation.** FP-08: ask the pair again; FP-13: abort. Built: ask again
  (abort only on EOF/interrupt).
- **C-12 conversion failure at a prompt.** FP-08: re-ask; FP-13: not re-asked. Built: re-ask.
- **C-13 DateTime precedence.** PRD: first matching format; Contract: last. Built: first.
- **C-14 author format list.** Inventory: extends defaults; FP-05: replaces. Built: replaces.
- **C-15 Choice case sensitivity.** Built: case-sensitive unless `case_sensitive=False`, enums too.
- **C-16 IntRange clamp at open bound.** PRD: adjacent integer inside; Contract: the bound itself.
  Built: adjacent integer inside the range.
- **C-17 FloatRange clamp with open bound.** PRD: declaration error; Contract: accepted. Built:
  declaration error (`DeclarationError`, a `TypeError`/`ValueError`).
- **C-18 `resolve_path` and `~`.** PRD: not expanded; Contract: expanded. Built: not expanded.
- **C-19 `get_app_dir` on Unix.** PRD: honours `$XDG_CONFIG_HOME`; Contract: always `~/.config`.
  Built: XDG variable when set and non-empty, else `~/.config`.
- **C-20 option names for an empty completion token.** PRD: only after a dash; Contract: listed.
  Built: only once a dash has been typed.
- **C-21 interactive session.** Built: interactive when stdin **or** stdout is a TTY.
- **C-22 callback of an omitted parameter.** Terminology: not called; FP-03: called. Built: called
  (with `None`/`()`), so callbacks can default from earlier values.
- **C-23 default map vs environment.** PRD: command line, environment, default map, default.
  Contract: default map before environment. Built: PRD order.
- **C-24 group invoked with only options.** Empty invocation of a group with default
  no-args-is-help prints help to stderr and exits 2. A non-empty invocation without a subcommand
  reports "Missing command." and exits 2 with no help page.
- **C-25 isolated filesystem.** Built: the directory is removed on exit when no `temp_dir` is given;
  with `temp_dir` the new directory is kept.

Other points the spec leaves contradictory:
- `pause()` prints its message even when not interactive (FP-11 l.346) and never blocks.
- Declaration errors (invalid keyword combinations) raise `optlyn.exceptions.DeclarationError`,
  a subclass of both `TypeError` and `ValueError`; invalid `style` colors raise `ColorError`
  (same two bases).
