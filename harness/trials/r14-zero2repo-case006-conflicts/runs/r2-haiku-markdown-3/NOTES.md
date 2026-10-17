# NOTES

## Status: partial implementation

This is a small, partial core of Optlyn, written under a nearly exhausted budget. It is not the full spec.

### Implemented (in `src/optlyn/__init__.py`)
- `command` / `group` decorators, with the name derivation rule (lowercase, underscores to dashes, `_command`/`_cmd`/`_group`/`_grp` suffix stripped).
- `option` (long options `--name value` / `--name=value`, boolean flags, defaults, `required`) and `argument` (single-token positional).
- `Command.main` with standalone exit codes: 0 success, 2 usage error (`BadParameter`), 1 abort.
- `BadParameter`, `Abort`.
- Groups: `Group.add_command`, `Group.command`, and dispatch to one child by name. The group callback runs before the child. Group options come before the subcommand name.
- Boolean flags default to `False` when omitted.
- Smoke-tested: group dispatch, argument binding, flag default, usage error exit 2.

### Not implemented (spec gaps)
- Nested groups beyond one level are untested. `CommandCollection`, `invoke_without_command`, and chaining are not implemented.
- Short options, option stacking, `/` and `+` prefixes, `--`-based flags on-off pairs, counting, repeatable, nargs, multi-value.
- Help pages (FP-02), including `--help`, and the version options.
- Types (FP-05), prompts (FP-08), file and path types (FP-09), chaining (FP-10).
- Context, default map, env vars, value sources (FP-07).
- Terminal helpers (FP-11), shell completion (FP-12), `CliRunner` (FP-14), and the `optlyn.testing` / `optlyn.formatting` modules.
- Missing exports from the Interface Contract: `help_option`, `version_option`, `custom_version_option`, `password_option`, `confirmation_option`, `pass_context`, `pass_obj`, `make_pass_decorator`, `Context`, `Parameter`, `ParamType`, `CommandCollection`, and the type constants.

### Spec choices
- `Command.main` raises `SystemExit` with status 0 on success when `standalone_mode=True`, and returns the callback's value otherwise.
- The `Group` class is a stub. Its behavior is undefined until dispatch is written.
