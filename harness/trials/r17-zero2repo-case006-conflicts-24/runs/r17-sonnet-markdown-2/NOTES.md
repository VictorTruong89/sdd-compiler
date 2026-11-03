# Notes

Package: `src/optlyn` (pure Python, no dependencies, no build step).

## Spec disagreements and the choice made

| Topic | Disagreement | Built |
| --- | --- | --- |
| Env var list on an option | PRD: first set wins; Contract: last set wins | Options: last non-empty wins (Contract). Arguments: first wins (PRD). |
| Counting option omitted | PRD: `0`; Contract: `None` | `None` when omitted (Contract). |
| Show default for a False flag | PRD: hidden; Contract: shown | Shown (`default: False`) when show-default is on (Contract). |
| Bool flag env value, unknown text | FP-05: turns flag off; FP-03: usage error | Usage error (FP-03). |
| DateTime with several matching formats | PRD: first wins; Contract: last wins | Last matching format; custom list replaces the defaults. |
| Form feed in help | PRD: text after is omitted; Contract: dropped, text after kept | Docstring-derived help is cut at the form feed; an explicit `help=` just drops the character. |
| Epilog position | Contract (command attrs): before options; Contract (help page list) and PRD: last | Printed last. |
| Enum `Choice` case | Contract: enum match ignores case by default | List choices are case-sensitive by default; enum choices ignore case unless `case_sensitive=` is passed. |
| `Path(resolve_path=True)` and `~` | PRD: not expanded; Contract: expanded | Expanded, then `realpath`. |
| Completion of empty token | PRD: options only after a dash; Contract: subcommands then options | Empty token: subcommands, then options. Non-empty alphanumeric token: subcommands only. |
| Parameter callback on omitted value | Terminology: not called; FP-03: called with `None` | Called (with `None`/`()`). |
| Prompt conversion failure | FP-13: not asked again; FP-08: re-ask | Re-asks until valid or EOF (EOF aborts). |
| Max content width | FP-02: 80; FP-11: 100 | 80. |
| `get_app_dir` on Unix | Contract: always `~/.config`; PRD: honours `XDG_CONFIG_HOME` | Honours `XDG_CONFIG_HOME`, else `~/.config`. |
| `isolated_filesystem` cleanup | PRD says both "removed when no parent" and "always left" | Removed when no `temp_dir` is given; kept otherwise. |
| Chaining group return with standalone off | Contract: list of child returns even with a result callback | Returns the list; the result callback still runs. |
| Boolean flag with `default=True` | PRD: present yields true | `flag_value` defaults to `True`; it is not inverted. |
| Interactive session | PRD: stdin or stdout is a TTY | `isatty(stdin) or isatty(stdout)`. |
| Default option metavar | PRD example shows `COUNT`; text says type name | Type name upper-cased (`INTEGER`, `TEXT`, ...). |
