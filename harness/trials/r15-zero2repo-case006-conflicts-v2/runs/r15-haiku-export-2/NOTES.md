# Optlyn: implementation notes

Built from `spec/` (export `store_hash` `sha256:2dfeba1c…`, 33 packs, 1015 checklist ids).
`spec/` is unchanged. The package is `src/optlyn`; run with `PYTHONPATH=src`.
Tests: `PYTHONPATH=src python3 -m pytest tests/` (54 tests, all passing).

## Spec disagreements and what was built

The export was made with `--allow-open`; these six contradictions have no human verdict
(`CF-000146`, `CF-000150`, `CF-000151`, `CF-000152`, `CF-000153`, `CF-000155`).

| Conflict | Where it disagrees | Built |
| --- | --- | --- |
| CF-000146 | deprecation warning on stdout (N-000081, FP-01) vs stderr (N-000803, channel table) | **stderr** |
| CF-000150 | environment ranked above default map (N-000230, FP-03 ranking) vs default map "takes precedence over environment" (N-000937, Context table) | **environment above default map**, so the ranking holds: command line, prompt, environment, default map, declared default |
| CF-000151 | a confirm answer other than yes/no/blank "asks again" (N-000495, FP-08) vs "counts as no" (N-001016, terminal helpers) | **asks again** |
| CF-000152 | integer option `--count` shows its type name, `COUNT` in N-001013 acceptance criterion vs `INTEGER` from "type name in uppercase" (N-000326) | **`--count COUNT`** (the acceptance criterion). Built-in types use the destination name uppercased; a custom `ParamType` subclass uses its `name` uppercased; a `Choice` shows `[a|b]` |
| CF-000153 | `isolated_filesystem` with no parent removes the directory on exit (N-000732) vs "always left in place" (N-001015) | **removed on exit when no parent is given**; kept when a parent path is given |
| CF-000155 | default maximum content width 80 (N-000127, FP-02) vs 100 (N-001014, constraint) | **80** caps auto-detected width; an explicit `terminal_width` is used as-is |

## Interpretation calls where the spec left room

- **Callbacks run for omitted parameters.** The terminology sentence says a callback is not called for an omitted parameter. FP-03 says "a missing parameter still runs its callback" so it can default from an earlier value. FP-03 is followed.
- **`ctx.invoke(cmd, **values)` fills declared defaults** for parameters not given, so the target callback can run. `forward` passes the current parameters.
- **`make_pass_decorator` / `pass_obj` lookup** matches with `isinstance`, walking up from the current context.
- **Completion wire format** (implementer's choice): one line per suggestion, `type,value`, where type is `plain`, `file`, or `dir`. zsh and fish append `\t` and the help text. Path requests are `file,<incomplete>` or `dir,<incomplete>`. The registration scripts are my own (they were not executed in this environment).
- **Unknown completion instruction** prints a message to stderr and exits 1. No script or suggestions are printed and the callback does not run.
- **Group with no arguments** (`no_args_is_help` default) prints help to stderr and exits 2. A group given only its own options gets `Missing command.` on stderr, not the help page.
- **Option destination** is inferred as: the first long name whose stripped form is an identifier (dashes become underscores), then the first short name.
- **Prompts always show the default** (declared or default-map) and use it on an empty answer. `prompt_required=False` prompts only when the flag is given without a value.
- **Version option package detection** with no `package_name` uses the top-level package of the root command's callback module.
- **Style errors**: an invalid color raises `InvalidColorError`, a subclass of both `TypeError` and `ValueError`.
- **`echo_via_pager`** uses `PAGER` (default `less`) only when interactive.
- **Confirmation option** is not eager (`is_eager=False`) and asks only when the flag is omitted.
- **`CommandCollection`**: when two sources define the same name, the first source wins.
- **`getchar`** reads from `sys.stdin` (raw mode when it is a terminal). It does not open `/dev/tty` when stdin is a pipe, so that part of N-000648 is not met.
- **`CliRunner(capture="fd")`** redirects fds 1 and 2 to temporary files. Stdout and stderr are reported as separate blocks, so their interleaving is not preserved in `output`.

## Coverage by pack

Every pack is implemented at feature level. Status: **T** = exercised by a test in `tests/test_optlyn.py`, **I** = implemented but only smoke-checked by hand, **—** = not exercised.

| Pack | Area | Module | Status |
| --- | --- | --- | --- |
| 01–03 | hardware / runtime constraints | `pyproject.toml`, `src/` layout, zero dependencies | I |
| 04–05 | package layout and exports | `__init__.py` | T |
| 06 | exit statuses, channels, help page, version identity | `core.py`, `exceptions.py`, `formatting.py` | T |
| 07 | `command`, `group`, `Group`, `CommandCollection` | `decorators.py`, `core.py` | T |
| 08 | `option`, `argument`, ready-made options, `BadParameter` | `core.py`, `decorators.py` | T |
| 09 | parameter types (`Choice`, `DateTime`, ranges, `Tuple`, `File`, `Path`, `ParamType`) | `types.py` | T |
| 10 | `Context`, callbacks, `get_current_context` | `core.py`, `_state.py` | T |
| 11 | terminal helpers | `termui.py`, `utils.py` | T (echo, style, progressbar); I (pager, edit, launch, getchar, pause, clear) |
| 12 | shell completion | `shell_completion.py` | T (bash path); I (zsh, fish, powershell) |
| 13 | `CliRunner` surface | `testing.py` | T |
| 14–18 | product overview, terminology, surface, non-functional, non-goals | all | I |
| 19–21 | FP-01 command declaration, FP-02 help, FP-03 options | `core.py`, `parser.py` | T |
| 22 | FP-04 positional arguments | `core.py` | T |
| 23 | FP-05 types and conversion | `types.py` | T |
| 24 | FP-06 groups, nesting, lazy loading | `core.py` | T (nesting, collection); lazy custom lookup I |
| 25 | FP-07 context, defaults, env prefix, value sources | `core.py` | T |
| 26 | FP-08 prompts, confirmation, hidden input | `core.py`, `termui.py` | T |
| 27 | FP-09 file and path parameters | `types.py`, `utils.py` | T (read, write, `-`, path checks); I (atomic, lazy failure at I/O) |
| 28 | FP-10 chaining | `core.py` | T |
| 29 | FP-11 terminal output | `termui.py`, `formatting.py` | T (partly, see 11) |
| 30 | FP-12 shell completion | `shell_completion.py` | T |
| 31 | FP-13 exit status and abort | `core.py`, `exceptions.py` | T |
| 32 | FP-14 in-process runner | `testing.py` | T (interpreter capture); I (`capture="fd"`, checked by hand, not in tests) |
| 33 | cross-cutting refinements | `core.py` | T (hidden names, chaining, prompts) |

Per-id `# spec:` markers were not added to the code. The checklist ids are covered at the pack
level above. The checklist in `spec/CHECKLIST.md` was not ticked, because `spec/` must stay as it is.

## Not done / not verified

- No per-id `# spec:` markers in the source (see above).
- Not exercised in this environment: real pager, editor and launcher commands, `getchar` on a
  terminal, Windows and macOS paths, zsh/fish/PowerShell scripts run in their shells, atomic
  file replacement under concurrent readers.
- `CliRunner` does not implement a true interleaved `output` for `capture="fd"`.
