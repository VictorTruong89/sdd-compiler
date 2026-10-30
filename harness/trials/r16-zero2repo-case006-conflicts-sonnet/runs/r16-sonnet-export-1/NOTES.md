# Notes

Package: `src/optlyn` (pure Python, no dependencies). Modules: `core` (Context, Command, Group,
CommandCollection, Parameter/Option/Argument), `parser`, `types`, `formatting`, `termui`, `utils`,
`_compat`, `decorators`, `shell_completion`, `testing` (CliRunner), `exceptions`, `globals`.
The design follows the conventional decorator-based CLI toolkit model the spec describes; every pack
(01-33) is covered by these modules. Wording/layout the Contract leaves to the implementer is my choice.

## Spec disagreements and what I built

The six open contradictions from `MAP.md` (CF-000146/150/151/152/153/155):

1. **CF-000146 deprecation warning channel** (FP-01 says stdout, Contract channel table says stderr):
   built **stderr**.
2. **CF-000150 default map vs environment** (FP-03/FP-07 list env above default map; Contract section 6 says
   default_map beats env): built **command line > environment > default map > declared default**, the
   ranking stated in FP-03 and the cross-cutting section.
3. **CF-000151 standalone `confirm` with an unrecognised answer** (FP-08 "asks again"; Contract "counts as no"):
   built **ask again**; empty answer takes the default; EOF aborts.
4. **CF-000152 default metavar** (type name uppercased vs the example `--count COUNT`): built the type name
   uppercased, so an int option shows `--count INTEGER`; choice types show `[a|b]`.
5. **CF-000153 `isolated_filesystem`**: built "removed on exit when no `temp_dir` is given, left in place when
   a parent `temp_dir` is supplied".
6. **CF-000155 max content width** (80 vs 100): built **80**. Inside `CliRunner.invoke` the wrap width is fixed
   at 80 so help output is deterministic.

Other choices:
- Declaration errors (invalid option/argument combos, nesting a group under a chaining group, `FloatRange`
  clamp with open bounds) raise `optlyn.DeclarationError`, which subclasses `TypeError`, `ValueError` and
  `RuntimeError`.
- Invalid `style` colours raise `optlyn.termui.ColorError` (a `TypeError`/`ValueError`/`KeyError`).
- A parameter callback runs even for an omitted parameter (FP-03), despite the Terminology wording.
- Interactive session = stdin is a TTY or stdout is a TTY (pager, pause).
- Usage-error help for groups invoked with no args goes to stderr with exit status 2.
- In `CliRunner`, a prompt that hits end of input raises EOFError (-> Abort).
- Optional-value options: `is_flag=False` + `flag_value`; prompt options with `prompt_required=False`.
- Not done: Windows-specific argument globbing and console colour support (target is Linux).
