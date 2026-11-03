# Notes

## Status

This is a partial implementation. Only a core subset of the specification is built:

- Commands and groups via `command` / `group` decorators, with `add_command`, `command`/`group` child decorators, and name derivation (`_command`/`_cmd`/`_group`/`_grp` suffix stripping).
- Options (`option`) with `--long`/`-s` names, flags, `multiple`, `required`, defaults, and conversion functions or types.
- Positional arguments (`argument`) with fixed arity or variadic (`nargs=-1`).
- `main(args, prog_name, standalone_mode)` with exit statuses 0 (success/help), 2 (usage), 1 (abort).
- Help page with usage line, description, positional-arguments section, options, and group command listing.
- Chaining groups refuse nested groups at `add_command`.

Not implemented (from `spec/`): prompts, confirmation/password options, eager version
options, environment variable sources, default map, file/path types, terminal helpers,
shell completion, `CliRunner`, lazy loading, context object plumbing (`pass_context`,
`pass_obj`), deprecation marks beyond a single stderr warning, and the choice/date/range types.

## Spec disagreements and choices

- **Usage-error exit vs. "standalone off" return:** the spec says standalone-off returns the callback value; the implementation returns `None` on `--help` in standalone-off mode, since help has no callback value.
- **Help on a group with no args:** the spec says the no-args help is a usage failure (exit 2) and says "not zero". Implemented as stderr help plus exit 2.
- **Name derivation:** a `_key` helper applies the spec's suffix stripping and dash conversion. The spec does not say whether suffix stripping applies after lowercasing; it is applied after lowercasing.
- **Interspersed args:** leaf commands mix options and positional arguments. Groups stop option parsing at the first positional token, which names the subcommand (options must precede the subcommand name).
- **Help exit:** intentional help writes to stdout and exits 0; the spec's `--help` error channel rule (stderr when shown due to incorrect usage) is followed.
