# Notes

Implementation of Optlyn from `spec/`. Code lives in `src/optlyn/`; tests in `tests/`.
Run tests with `PYTHONPATH=src python3 -m pytest tests`.

## Conflicts and choices

The export lists six unsettled contradictions (`spec/MAP.md`, `CF-000146`, `150`–`153`, `155`).
Each was resolved as follows.

| Id | Disagreement | Built |
|---|---|---|
| CF-000146 | Deprecation warning on stdout (N-000081, FP-01) vs stderr (N-000803, channel table) | **stderr**, following the Interface Contract channel table. Usage errors and abort indications also go to stderr. |
| CF-000150 | Env ranks above default map (N-000230, FP-03 ranking) vs default map beats env (N-000937) | **env above default map**, following FP-03's explicit ranking. `Context.default_map` still feeds the default-map tier. |
| CF-000151 | Confirm: unrecognised answer asks again (N-000495) vs counts as no (N-001016) | **asks again**, following FP-08. Empty answer takes the default. |
| CF-000152 | Integer option metavar: type name `INTEGER` (N-000326) vs example `--count COUNT` (N-001013) | **type name** (`INTEGER`), following the general rule. Authors override with `metavar=`. |
| CF-000155 | Max content width: 80 (N-000127) vs 100 (N-001014) | **80** is the default cap on auto-detected width; the caller may raise it with `max_content_width`. Text wrapping with no explicit width uses that cap. |
| CF-000153 | Runner removes the isolated directory when no parent is given (N-000732) vs always leaves it (N-001015) | **always left in place**, following the later, explicit claim. |

Other choices where the spec was silent or underspecified:

- **Callback on omitted parameters.** A parameter callback runs when some source produced a value, including a declared default. It is skipped when the parameter was omitted and nothing supplied a value (PRD terminology, "Callback").
- **Group callback order.** For a dispatched subcommand, the group callback runs before the child is parsed. Child help or usage errors therefore happen after the group callback, as FP-06 requires.
- **Prompt rules.** `prompt=True` with the default `prompt_required=True` prompts when omitted. `prompt_required=False` prompts only when the flag appears without a value.
- **Help for flag pairs.** The entry shows `--a / --b`.
- **Completion without a shell.** The four registration scripts are simple templates. Only the `*_complete` suggestion stream was exercised, not a real shell.
- **Unknown completion instruction.** Prints nothing and exits 1.
- **Chaining.** Chained subcommand segments are split at each token that names a command. A variadic argument on a non-last chained command therefore only sees its own segment.
- **Author clean stop with standalone mode off.** `ctx.exit(code)` ends the call without raising; `main(standalone_mode=False)` returns `None`.

## Spec-to-module map

| Pack(s) | Area | Module(s) |
|---|---|---|
| 01–05 | Hardware, package layout, exports | `pyproject.toml`, `src/optlyn/__init__.py` |
| 06 | Exit statuses, channels, help page, version identity | `core.py` (exit handling in `Command.main`), `helpfmt.py`, `decorators.py` (version flags) |
| 07 | `command`, `group`, `Group`, `CommandCollection` | `decorators.py`, `core.py` |
| 08 | `option`, `argument`, ready-made options, `BadParameter` | `params.py`, `decorators.py`, `exceptions.py` |
| 09 | Parameter types | `types.py` |
| 10 | `Context`, pass decorators, `get_current_context` | `core.py`, `decorators.py`, `_state.py` |
| 11 | Terminal helpers | `utils.py`, `formatting.py` (`wrap_text`) |
| 12 | Shell completion | `completion.py` |
| 13 | `CliRunner` | `testing.py` |
| 14–18 | Product overview, terminology, surface, non-functional constraints, non-goals | Covered by the modules above |
| 19 (FP-01) | Declaration and naming, deprecation, invocation | `decorators.py`, `core.py` |
| 20 (FP-02) | Help pages, eager flags, help option names | `helpfmt.py`, `parser.py`, `decorators.py` |
| 21 (FP-03) | Options, flags, counts, repeats, env, value ranking | `params.py`, `parser.py`, `core.py` |
| 22 (FP-04) | Positional arguments | `params.py`, `parser.py` |
| 23 (FP-05) | Types and conversion | `types.py` |
| 24 (FP-06) | Groups, nesting, lazy lookup, collections | `core.py` (`Group`, `CommandCollection`) |
| 25 (FP-07) | Context, auto env prefix, default map, sources, invoke/forward | `core.py`, `params.py` |
| 26 (FP-08) | Prompts, confirmation, password | `utils.py`, `decorators.py`, `params.py` |
| 27 (FP-09) | File and path types, dash, lazy and atomic open | `types.py`, `utils.py` |
| 28 (FP-10) | Chaining and result callbacks | `core.py` (`Group._invoke_chain`) |
| 29 (FP-11) | Echo, style, pager, progress, getchar, pause, edit, launch, app dir | `utils.py` |
| 30 (FP-12) | Shell completion | `completion.py` |
| 31 (FP-13) | Exit classes, abort, interrupt | `exceptions.py`, `core.py` |
| 32 (FP-14) | In-process runner | `testing.py` |
| 33 | Cross-cutting refinements | Covered by the modules above |

`# spec:` markers were not added per checklist id (1015 ids). The mapping above is the traceability record.

## Status

- Implemented: the surface listed in packs 05–13 and FP-01 through FP-14.
- Tested: `tests/test_optlyn.py` (28 tests) covers command and group dispatch, help, option parsing and stacking, value ranking, prompts, eager flags, chaining, standalone-off returns, types and ranges, files and paths, the isolated filesystem, collections, and styling.
- Not tested: completion scripts in a real shell, pager and `getchar` on a real terminal, `launch`, `edit`, lazy group loading, and `fd` capture mode in `CliRunner`.

## Known gaps

- **Feature-switch groups.** Several options sharing one destination: the last declared wins. The spec's source-tier precedence between them (FP-03, N-000233–236) is not implemented.
- **`fd` capture.** `CliRunner(capture="fd")` is accepted but records only interpreter streams, not OS-level descriptor writes.
- **Shell completion** for PowerShell and Fish is a template, unverified against those shells.
- **`launch(locate=True)`** ignores `locate`.
- **Lazy subcommands.** `get_command` and `list_commands` are overridable, and lookup happens only when needed. No built-in loader ships, as the spec requires.
