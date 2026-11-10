# NOTES — spec conflicts and the choices made

Where the PRD (`spec/Full_PRD.md`) and Contract (`spec/Interface_Contract.md`) disagree, I generally followed the PRD's stated behaviour (it describes the full behaviour), except where noted.

1. **C-01 form feed in help.** PRD FP-02: text after `\f` is omitted. Contract §3 `command`: text after it is kept. *Built:* truncate at `\f` (PRD).
2. **C-02 short help on group page.** PRD: first sentence, ellipsized to fit the wrap width. Contract §2: first paragraph, cut with `...` at 45 characters. *Built:* first sentence of the first paragraph, cut with `...` at `width - 6 - longest command name` (PRD). `Command.get_short_help_str(limit=45)` still defaults to 45 when called directly.
3. **C-03 epilog position.** PRD: last on the page. Contract §3 `epilog`: right after the description; Contract §2 list item 6 also puts it last. *Built:* epilog printed last.
4. **C-04 max content width.** PRD FP-02: 80; PRD FP-11: 100. *Built:* 80 (an explicit `terminal_width` is used as-is).
5. **C-05 default metavar.** PRD rule: upper-cased type name; its example says `--count COUNT`. *Built:* the rule: `--count INTEGER` (types are named text, integer, float, boolean, uuid, filename, path...).
6. **C-06 show-default for a False flag.** PRD: hidden; Contract: shown. *Built:* hidden for a single-option boolean flag whose default is false (PRD); shown when true.
7. **C-07 omitted counting option.** PRD: 0; Contract: `None`. *Built:* `0`.
8. **C-08 envvar list.** PRD: first set wins; Contract: last set wins. *Built:* first set wins.
9. **C-09 bad bool env value.** PRD FP-03: usage error; PRD FP-05: flag turns off. *Built:* usage error (whitespace-only deactivates; non-bool flag_value flags treat unrecognised values as unset).
10. **C-10 prompt on fully omitted prompting option.** PRD FP-08 first bullet: prompts; second bullet: not when `prompt_required=False`. *Built:* prompts by default (`prompt_required=True`); with `prompt_required=False` it prompts only when the flag is given without a value.
11. **C-11 mismatched confirmation.** PRD FP-08: re-ask the pair; FP-13: abort. *Built:* re-ask.
12. **C-12 conversion failure at a prompt.** PRD FP-08: re-ask; FP-13: not asked again. *Built:* re-ask until valid, EOF aborts.
13. **C-13 DateTime format precedence.** PRD: first success; Contract: last match. *Built:* first matching format.
14. **C-14 author formats extend defaults?** PRD inventory: extend; FP-05: replace. *Built:* replace.
15. **C-15 enum Choice case sensitivity.** Contract: enum matching ignores case by default; PRD: case-sensitive unless turned off. *Built:* case-sensitive by default for all choices (`case_sensitive=False` to relax).
16. **C-16 IntRange clamp at open bound.** PRD: adjacent integer inside; Contract: the bound's value. *Built:* adjacent integer inside the range.
17. **C-17 FloatRange clamp with open bound.** PRD (x2): refused at declaration; Contract: accepted. *Built:* `TypeError` at construction.
18. **C-18 `~` with `resolve_path`.** PRD: not expanded; Contract: expanded. *Built:* not expanded (`os.path.realpath`).
19. **C-19 app dir on Unix.** PRD: `$XDG_CONFIG_HOME` when set; Contract: always `~/.config`. *Built:* honours `XDG_CONFIG_HOME`, else `~/.config`.
20. **C-20 options for empty completion token.** PRD: only after a dash; Contract: subcommands then options for empty token. *Built:* options only when the incomplete token starts with a dash.
21. **C-21 interactive session.** PRD terminology is self-contradictory. *Built:* interactive = stdin is a TTY and stdout is a TTY.
22. **C-22 callback for omitted parameter.** PRD Terminology: not called; FP-03: called. *Built:* called (with `None`/empty value).
23. **C-23 default map vs environment.** PRD: environment before default map; Contract: default map wins. *Built:* command line > environment > default map > declared default.
24. **C-24 group given only options.** PRD FP-06: "Missing command" error, no no-args help; FP-13/FP-02: help shown. *Built:* the no-args help page (stderr, exit 2) only when the argument list is completely empty; options-only gives `Missing command.` (usage line + error, exit 2).
25. **C-25 isolated filesystem cleanup.** PRD: removed when no parent given, yet "always left in place". *Built:* removed on exit when `temp_dir` is None; left in place when a parent is given.

Other choices not covered by the conflict list: `pause()` prints its message but never blocks when not interactive (FP-11 boundary bullet) even though the FP-11 body says it "does nothing"; an unrecognised completion instruction exits with status 1 and prints nothing.
