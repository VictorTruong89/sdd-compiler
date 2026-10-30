# Optlyn: implementation notes

Optlyn is a pure-Python library (`src/optlyn`, Python 3.10+, no runtime dependencies).
Run the tests from `/app` with `PYTHONPATH=src python -m pytest tests`
(92 tests, all passing on Python 3.13).

## Layout

| Module | Covers |
|---|---|
| `optlyn/core.py` | `Context`, `Parameter`/`Option`/`Argument`, `Command`, `Group`, `CommandCollection`; value sources, conversion, dispatch, chaining, help layout |
| `optlyn/parser.py` | option tokenizer: prefixes, stacking, `--`, values, positional limit for groups |
| `optlyn/paramtypes.py` | built-in and custom parameter types, `File`, `Path`, `Choice`, ranges, `Tuple` |
| `optlyn/decorators.py` | `command`, `group`, `option`, `argument`, ready-made options, `pass_*` decorators |
| `optlyn/termui.py` | styling, echo-adjacent output, prompts, confirm, pager, progress bar, editor, launch |
| `optlyn/utils.py` | `echo`, ASCII-safe writes, `open_file`/`LazyFile`, `format_filename`, `get_app_dir` |
| `optlyn/formatting.py` | `wrap_text` and definition-list layout |
| `optlyn/shell_completion.py` | `_<PROG>_COMPLETE` source and complete modes for bash, zsh, fish, powershell |
| `optlyn/testing.py` | `CliRunner` (`capture="sys"` or `"fd"`), `Result`, `isolated_filesystem` |
| `optlyn/exceptions.py` | exit-status classes (usage 2, abort/general 1, author stop `n`) |
| `optlyn/_state.py` | thread-local context stack, interactivity and colour detection |

The module is `paramtypes.py` rather than `types.py` so that it never shadows the
standard library when a file in the package directory is run directly.

## Spec conflicts and what was built

The export marks six contradictions as unsettled (`--allow-open`). Each was resolved as below.

| Id | Disagreement | Built |
|---|---|---|
| CF-000146 | Deprecation warning on stdout (FP-01) vs stderr (Interface Contract channel table) | **stderr**, following the channel table. Command, option and argument warnings all go there. |
| CF-000150 | Environment before default map (FP-03 precedence list) vs default-map values beating environment (Interface Contract, section 6) | **environment before default map**, following FP-03's explicit ranking. |
| CF-000151 | Confirm: "any other answer asks again" (FP-08) vs "counts as no" (Interface Contract, section 7) | **asks again**, following FP-08. |
| CF-000152 | Integer option metavar: "type name in uppercase" (`INTEGER`) vs the example `--count COUNT` | **`INTEGER`**, following the stated rule. |
| CF-000153 | Isolated filesystem: removed on exit when no parent is given vs "always left in place" | **removed when no `temp_dir` is given**; created under `temp_dir` and left in place when one is. |
| CF-000155 | Maximum content width 80 (FP-02) vs 100 (FP-11) | **80** for help pages (`max_content_width` default); a caller's `terminal_width` is used as given. |

Other choices where the spec leaves room or is ambiguous:

- **Parameter callbacks always run**, including when a parameter received no value. FP-03 says a
  missing parameter's callback still runs, which is the reading used here. The FP-01 terminology
  entry says otherwise; this follows FP-03.
- **Confirm/prompt EOF** raises `Abort` (exit 1). Prompts re-ask on conversion failure.
- **Completion path requests** are emitted as `@@file@@<token>` and `@@dir@@<token>` lines; the
  generated bash script expands them with `compgen`.
- **Unrecognised completion instruction** (e.g. `tcsh_source`) prints nothing and exits 1 without
  running the callback.
- **Eager flags**: processed in the order the user typed them, so the first one wins.
- **Feature-switch ties**: explicit commandline > environment > default map > declared default;
  among defaults, an explicit default beats an auto-derived flag default; then the last declared wins.
- **`Context.invoke`** fills undeclared-by-caller parameters with their declared defaults (not converted).
- **`get_parameter_source`** reports `COMMANDLINE` for values passed in through `invoke`.
- **Group callback ordering**: the group callback runs before the child is parsed, so a child's usage
  error appears after the group callback has run (as FP-06 requires).
- **`find_object`** uses `isinstance` (subclasses match) rather than exact type.
- **`BadParameter` identity**: an option is named by its declared flags joined with ` / `, so
  `--count` appears in the message; an argument by its name in uppercase.
- **Pager output** keeps styles unless colour is forced off.

## Checklist accounting

`spec/CHECKLIST.md` lists 1015 ids in 33 packs. Each pack is implemented as follows. Status is
"implemented" unless marked otherwise. Behavioural coverage is in `tests/test_optlyn.py`, whose
test names cite the spec ids (`# spec: FP-xx ...`).

Coverage is recorded at pack granularity. The ids are not marked one by one in the code.

| Pack(s) | Subject | Where | Tested |
|---|---|---|---|
| 01–03 | Hardware, CPU baseline, pure Python, zero dependencies, Python 3.10+, src layout | `pyproject.toml` (`requires-python`, empty `dependencies`, `src` packaging) | by construction |
| 04–05 | Interface contract shell, package and exports | `optlyn/__init__.py`, `optlyn/formatting.py` (`wrap_text`), `optlyn/testing.py` | every test imports through the package exports |
| 06 | Exit statuses, channels, help page layout, version page | `core.py` (`main`, `get_help`, `format_usage`), `exceptions.py`, `decorators.py` | `test_AC_help…`, version and usage tests |
| 07 | `command`, `group`, `Group`, `CommandCollection` members | `decorators.py`, `core.py` | group, collection and dispatch tests |
| 08 | Options, arguments, delivered values, ready-made options | `core.py` (`Option`, `Argument`, `handle_parse_result`), `parser.py`, `decorators.py` | option, argument and eager tests |
| 09 | Parameter type table | `paramtypes.py` | type tests |
| 10 | `Context`, callback decorators, `get_current_context` | `core.py` (`Context`), `_state.py`, `decorators.py` | context and invoke tests |
| 11 | Terminal helpers | `termui.py`, `utils.py` | styling, pager, progress, prompt, runner tests |
| 12 | Shell completion | `shell_completion.py` | completion tests |
| 13 | `CliRunner`, `Result` | `testing.py` | runner tests |
| 14–18 | Overview, terminology, surface, non-functional constraints, non-goals | design-level; no code of their own | — |
| 19 | Command declaration, naming, invocation | `decorators.py` (`_default_name`), `core.py` (`Command.main`) | naming, standalone, deprecation tests |
| 20 | Automatic help, eager documentation flags | `core.py` (help option, `get_help`), `decorators.py` (version options) | help and version tests |
| 21 | Options | `core.py`, `parser.py` | option tests |
| 22 | Positional arguments | `core.py` (`_assign_arguments`, `Argument`) | argument tests |
| 23 | Parameter types and conversion | `paramtypes.py` | type tests |
| 24 | Groups, nesting, deferred loading | `core.py` (`Group`, `resolve_command`, `list_commands`/`get_command`) | nesting and collection tests |
| 25 | Context, defaults, environment prefix, value sources | `core.py` (`lookup_default`, `auto_envvar_name`, `_from_env`, `_fallback`) | env, default map and source tests |
| 26 | Prompts, confirmation, hidden input | `termui.py` (`prompt`, `confirm`), `core.py` (`_prompt`), `decorators.py` | prompt and confirmation tests |
| 27 | File and path parameters | `paramtypes.py` (`File`, `Path`), `utils.py` (`LazyFile`, `open_file`, `_AtomicWriter`) | file and path tests |
| 28 | Chaining and pipelines | `core.py` (`Group._invoke_chain`, `_process_result`) | chain tests |
| 29 | Terminal output and interaction helpers | `termui.py`, `utils.py` | terminal tests |
| 30 | Shell completion (FP) | `shell_completion.py` | completion tests |
| 31 | Usage failures, abort, exit status | `exceptions.py`, `core.py` (`main`) | exit status tests |
| 32 | In-process runner | `testing.py` | runner tests |
| 33 | Cross-cutting refinements | applied across `core.py` (precedence, chaining, hidden names) | covered by the tests above |

## Not done, or partial, and why

- **Windows argv expansion.** FP-17 says glob and home-directory expansion of the argument list on
  Windows, unless disabled. `main(windows_expand_args=...)` is accepted but ignored. The spec's
  required platform is Linux, so this is not implemented.
- **Completion scripts** for zsh, fish and PowerShell are simple and have not been run in those shells.
  Only the bash path is exercised by the tests. The complete-mode logic is shared by all four shells.
- **`getchar`** reads `/dev/tty` in raw mode. With no controlling terminal it falls back to standard
  input, so it cannot be tested here.
- **Unlisted chaining restriction.** FP-10 says a variadic argument on a non-last chained command is
  "not refused at declaration". It is not refused, and that is intentional.
- **Custom lazy loading.** Optlyn provides the `list_commands`/`get_command` extension points. It does
  not ship a plugin loader, as FP-06 and the non-goals require.
- **Thread-safety** of contexts is not a goal (FP-14, non-goals). The current context is thread-local.
