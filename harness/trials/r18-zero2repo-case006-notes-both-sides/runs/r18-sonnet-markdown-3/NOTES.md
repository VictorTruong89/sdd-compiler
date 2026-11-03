# Optlyn build notes

Pure-Python package in `src/optlyn` (run with `PYTHONPATH=src`). No build step.

## Specification disagreements and what was built

Format: where each side says it → choice made.

1. **Max content width.** PRD FP-02: "a maximum content width that defaults to 80 columns". PRD FP-11: "Help pages and wrapped text use a maximum content width of 100 columns". → Built 80 (help formatter). `wrap_text` takes an explicit width (default 78).
2. **FloatRange clamp with an open bound.** Interface §5: "With clamp=True and an open bound, a value beyond that bound becomes the bound". PRD FP-05: "Float range refuses clamp when a bound is open (declaration error)". → Built PRD: `TypeError` at construction.
3. **DateTime with several matching formats.** Interface §5: "the last matching format is used". PRD FP-05: "Formats are tried in order; the first success wins". → Built PRD: first success wins.
4. **Env var list.** Interface §4 `envvar`: "with a list, the last name that is set wins". PRD FP-03: "first one set wins". → Built first set wins.
5. **Counting option omitted.** Interface §4: counting option delivers "`None` when the option was omitted". PRD FP-03: "(zero if omitted)". → Built zero.
6. **show_default with off flag.** Interface §4: "a flag whose default is `False` included". PRD FP-02: the default of a single boolean flag that is off "remains hidden even if show-default is on". → Built PRD (hidden).
7. **Epilog position.** Interface §3 `command` attrs: "epilog (printed right after the description, before the options)". Interface §2 help page list and PRD FP-02: epilog is last. → Built: epilog printed last.
8. **Form feed in help.** Interface §3: "a form-feed character in it is dropped and the text after it is kept" (for `help=`). PRD FP-02: a form feed in the docstring truncates. → Built both: a docstring is truncated at `\f`; an explicit `help=` string just loses the `\f` character.
9. **Completion for empty token.** Interface §8: suggestions for an empty token are "the subcommand names followed by the option names". PRD FP-12: "Options are listed only once at least a dash has been typed". → Built PRD: only subcommands for an empty token.
10. **Application directory on Unix.** Interface §7: "On Unix the directory is always under `~/.config`". PRD FP-11: uses `$XDG_CONFIG_HOME` when set. → Built PRD.
11. **Path `resolve_path` and `~`.** Interface §5: "a leading `~` is first expanded". PRD FP-09: "a leading tilde is not expanded". → Built PRD (no expansion; `realpath` only).
12. **Pause when not interactive.** PRD FP-11 normal: "when not interactive it does nothing". PRD FP-11 boundary: "it still prints its message there". → Built: message printed (stdout, or stderr if `err`), no waiting.
13. **Isolated filesystem cleanup.** PRD FP-14: removed on exit when no parent is given, but also "always left in place after the block ends". → Built: removed when `temp_dir` is None; left in place when a parent is given.
14. **Prompt conversion failure.** PRD FP-08: prompts re-ask on conversion failure. PRD FP-13: a value typed at a prompt that fails conversion is a usage error "not asked again". → Built: type conversion failures re-ask; a refusal by the parameter's own callback is a (non-repeated) usage error.
15. **Parameter callback on omitted parameter.** PRD terminology: callback "not called for a parameter that was omitted and received no value". PRD FP-03: "A missing parameter still runs its callback". → Built: callback runs (with `None`).
16. **Boolean env var, invalid text.** PRD FP-05: "any other value turns the flag off". PRD FP-03: any other non-empty string is a conversion usage error. → Built FP-03 (usage error).
17. **Default metavar.** PRD FP-02: "type name in uppercase", with example `--count COUNT`. → Built type name (`--count INTEGER`).
18. **Short help limit.** Interface §2: cut at 45 characters. PRD FP-02: "ellipsized if it cannot fit on one line at the wrap width". → Built: first paragraph, limited to the available line width (as Click does), so 45 only when the line is that narrow.
19. **Interactive session.** PRD terminology: stdin on a PTY, or stdin/stdout a TTY. → Built: interactive if stdin or stdout is a TTY.
20. **Completion variable name.** Interface §8: upper-cased, `-` → `_`. Only `-` is replaced.
