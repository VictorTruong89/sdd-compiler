# Notes: specification conflicts and choices

Where the spec files disagree, this lists each side and what was built.
Rule used: the detailed behaviour in `spec/Full_PRD.md` wins over a one-line statement in
`spec/Interface_Contract.md`, unless the PRD itself contradicts itself.

1. **Form feed in help.** Contract §3 `command`: "a form-feed character in it is dropped and the text after it is kept". PRD FP-02: text after the form feed is omitted. Built: PRD (text after `\f` is dropped).
2. **Epilog position.** Contract §3 `epilog`: "printed right after the description, before the options". Contract §2 help order and PRD FP-02: epilog is last. Built: epilog last.
3. **Env var list.** Contract §4 `envvar`: "with a list, the last name that is set wins". PRD FP-03/FP-04: first one set wins. Built: first set wins.
4. **Counting option omitted.** Contract §4 "Delivered values": `None` when omitted. PRD FP-03: zero if omitted. Built: `0`.
5. **show_default on a bool flag whose default is False.** Contract §4 `show_default`: shown for a flag whose default is False. PRD FP-02: stays hidden. Built: hidden for a single bare flag (an on/off pair shows the name of its default flag).
6. **DateTime with several matching formats.** Contract §5: last matching format wins. PRD FP-05: formats tried in order, first success wins. Built: first success. Also PRD "Public surface" says custom formats are "added to" the defaults, FP-05 says they replace them; built: replace.
7. **FloatRange / IntRange clamp with open bounds.** Contract §5 says a value beyond an open bound becomes "that bound's value" (and allows float clamp with open bound). PRD FP-05: IntRange uses the adjacent integer inside the range; FloatRange refuses clamp with an open bound (TypeError at construction). Built: PRD.
8. **Choice over an Enum.** Contract §5: match ignores letter case by default. PRD FP-05: case-sensitive unless turned off. Built: case-sensitive by default (`case_sensitive=False` to relax).
9. **Path `resolve_path` and `~`.** Contract §5: leading `~` expanded first. PRD FP-09: tilde is not expanded. Built: `~` is expanded before resolving (Contract), since it is the more specific statement of the option's signature behaviour.
10. **`get_app_dir` on Unix.** Contract §7: always under `~/.config`. PRD FP-11: `$XDG_CONFIG_HOME` when set. Built: PRD.
11. **Completion on an empty token.** Contract §8: suggestions for an empty token are subcommand names followed by option names. PRD FP-12: options only once a dash was typed. Built: PRD (subcommands only; options after a dash).
12. **Max content width.** PRD FP-02: default 80. PRD FP-11: help pages and wrapped text use 100. Built: 80 for help pages (`wrap_text` takes an explicit width, default 78).
13. **Option metavar example.** PRD FP-02 says an integer option `--count` appears as `--count COUNT` but the same bullet says the default is the type name upper-cased. Built: type name (`--count INTEGER`).
14. **Parameter callback for an omitted parameter.** PRD Terminology: not called when nothing supplied a value. PRD FP-03: a missing parameter still runs its callback (so it can default from earlier values). Built: callback is called (with `None`).
15. **Prompt conversion failure.** PRD FP-13: a bad value typed at a prompt is a usage error "not asked again". PRD FP-08: prompts re-ask on conversion failure. Built: conversion failures re-ask; a parameter callback refusing a prompted value is a (non-repeated) usage error.
16. **`isolated_filesystem` cleanup.** PRD FP-14: removed on exit when no parent given; also "always left in place after the block". Built: removed when `temp_dir` is None, left in place when a parent is given.
17. **Completion variable name.** Contract: upper-case with `-` replaced by `_`. Built exactly that (`.` is not replaced).
18. **Flag with default True.** A bare flag always yields `True` when present (PRD FP-03), it does not toggle.
