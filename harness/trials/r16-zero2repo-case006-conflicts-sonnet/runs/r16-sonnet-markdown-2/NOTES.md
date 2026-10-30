# Notes

Optlyn lives in `src/optlyn` (no build step, no dependencies). Where the specification disagrees
with itself, these are the choices made.

| Disagreement | Where | Built |
| --- | --- | --- |
| Deprecation warning channel: PRD FP-01 says standard output, Contract §2 says standard error | PRD FP-01 vs Contract "Channels" | Standard error (Contract). Emitted before the callback runs. |
| Default map vs environment precedence: Contract §6 says default-map values beat environment variables; PRD FP-03/FP-07 rank command line > environment > default map > declared default | Contract §6 vs PRD FP-03 | PRD order (environment beats default map). |
| Parameter callback on an omitted parameter: PRD glossary says it is not called; FP-03 says a missing parameter still runs its callback (to default from earlier values) | PRD Terminology vs FP-03 | The callback runs with `None` (FP-03). |
| Maximum content width default: FP-02 says 80, FP-11 says 100 | PRD | 80. An explicit `terminal_width` is used as-is; auto-detected width is `min(terminal, max_content_width) - 2` (at least 50). |
| Default metavar of a valued option: "type name in uppercase" vs example `--count COUNT` for an integer option | PRD FP-02 | Type name upper-cased (`--count INTEGER`); a custom `ParamType` shows its own `name`. |
| `confirm` with an unrecognised answer: PRD FP-08 says ask again, Contract §7 says it counts as no | PRD vs Contract | Ask again; if input then runs out, the result is `False` instead of an abort. EOF with no earlier invalid answer aborts. |
| `isolated_filesystem`: "removed on exit when no parent is given" vs "always left in place" | PRD FP-14 | Removed when `temp_dir` is `None`, kept when a parent is given. |
| Chaining group with standalone mode off: PRD says it returns the list of child return values whether or not a result callback is registered | PRD FP-10 | `main()` returns that list; the result callback still runs. |
| Declaration errors (deprecated+required, deprecated+prompt, open-bound clamp, chain nesting, ...) | PRD FP-03/04/05/10 | `DeclarationError`, a subclass of `TypeError`, `ValueError` and `RuntimeError`. |
| Auto help option name | PRD FP-02 (argument called `help` must keep working) | The automatic help flag uses an internal destination name so it cannot collide with an argument named `help`. |
