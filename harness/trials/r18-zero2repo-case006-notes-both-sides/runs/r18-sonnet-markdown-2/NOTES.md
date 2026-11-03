# NOTES

Package: `src/optlyn` (pure Python, no dependencies). No build step; use `PYTHONPATH=src`.

## Specification disagreements and what was built

Where the Interface Contract (IC) and the PRD disagree I followed the PRD, which also matches
the conventional behaviour of this style of CLI toolkit, except where noted.

1. **Counting option when omitted.** IC §4 "Delivered values": counting option is "an `int`, or `None` when the option was omitted". PRD FP-03: "A counting option yields how many times it occurred (zero if omitted)". Built: `0`.
2. **DateTime with several matching formats.** IC §5: "the last matching format is used". PRD FP-05: "Formats are tried in order; the first success wins". Built: first success wins.
3. **FloatRange clamp with an open bound.** IC §5: with `clamp=True` and an open bound the value becomes the bound. PRD FP-05: "Clamp is only allowed when both bounds are closed" / "Float range refuses clamp when a bound is open (declaration error)". Built: constructing raises `TypeError`.
4. **Form feed in help text.** IC §3 `command` attrs: a form-feed is dropped "and the text after it is kept". PRD FP-02: text after the form feed "is omitted from the help page". Built: text after is omitted.
5. **Epilog position.** IC §3: epilog "printed right after the description, before the options". IC §2 Help page item 6 and PRD FP-02: epilog is last. Built: last.
6. **Environment variable list.** IC §4 `envvar`: "with a list, the last name that is set wins". PRD FP-03/FP-04: "first one set wins". Built: first set wins.
7. **Path `resolve_path` and `~`.** IC §5: a leading `~` is expanded first. PRD FP-09: "a leading tilde is not expanded". Built: `~` is not expanded; the path is resolved with `realpath`.
8. **get_app_dir on Unix.** IC §7: "always under `~/.config`". PRD FP-11: under `$XDG_CONFIG_HOME` when set, else `~/.config`; POSIX-forced mode uses `~/.<name>`. Built: PRD.
9. **Shell completion options for an empty token.** IC §8: suggestions for an empty token are subcommand names followed by option names. PRD FP-12: "Options are listed only once at least a dash has been typed". Built: PRD (options only after a dash).
10. **Maximum content width.** PRD FP-02: default 80. PRD FP-11: "Help pages and wrapped text use a maximum content width of 100". Built: help pages 80; `wrap_text` default width 78.
11. **Show-default for a flag whose default is false.** IC §4 `show_default`: shown "a flag whose default is `False` included". PRD FP-02: stays hidden. Built: hidden (PRD).
12. **Pause when not interactive.** PRD FP-11 normal: "does nothing"; boundary: "still prints its message". Built: does nothing and does not block.
13. **Isolated filesystem directory.** PRD FP-14: removed on exit when no parent given, but also "always left in place after the block ends". Built: removed when no `temp_dir`; left in place when `temp_dir` is given.
14. **Parameter callback for a parameter that received no value.** PRD Terminology: not called. PRD FP-03: "A missing parameter still runs its callback". Built: callback runs (receives `None`/`()`).
15. **Boolean flag env var with unrecognised text.** PRD FP-05: "any other value turns the flag off". PRD FP-03: a non-empty unrecognised string is a conversion usage error. Built: usage error (FP-03).
16. **Prompt re-ask vs. "not asked again".** PRD FP-13 says a value typed at a prompt that fails conversion is not asked again; FP-08 says prompts re-ask on conversion failure. Built: re-ask on conversion failure; a parameter callback refusal is a usage error (no re-ask).
17. **Integer option default metavar.** PRD FP-02 example shows `--count COUNT` but also says the metavar is the type name in uppercase. Built: type name (`INTEGER`).
18. **Choice over an Enum and case.** IC §5 says enum matching ignores case "by default"; the signature default is `case_sensitive=True`. Built: case-sensitive unless `case_sensitive=False`.
19. **Short help length.** PRD: ellipsized to fit the line; IC §2: cut at 45 characters. Built: 45.
