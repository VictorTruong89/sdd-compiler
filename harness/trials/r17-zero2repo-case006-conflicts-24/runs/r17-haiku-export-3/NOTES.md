# NOTES — Optlyn implementation

This directory `/app` now holds the Optlyn library built from `spec/` (the spec itself is unchanged).

## Layout

- `pyproject.toml` — setuptools PEP 517 build, src layout, zero runtime dependencies, Python ≥ 3.10.
- `src/optlyn/` — the package (import with `PYTHONPATH=src`):
  - `__init__.py` — public exports (Contract §1).
  - `core.py` — `Context`, `Parameter`/`Option`/`Argument`, the option/argument parser, `Command`, `Group`, `CommandCollection`, invocation and help.
  - `decorators.py` — `command`, `group`, `option`, `argument`, `help_option`, `version_option`, `custom_version_option`, `password_option`, `confirmation_option`, `pass_context`, `pass_obj`, `make_pass_decorator`.
  - `paramtypes.py` — `ParamType` and the built-in types, `File`, `Path`, `open_file`.
  - `termui.py` — echo/style/prompts/pager/progress/editor/launch/app-dir helpers.
  - `formatting.py` — `wrap_text` and help-layout helpers.
  - `exceptions.py` — `UsageError` (exit 2), `BadParameter`, `MissingParameter`, `NoSuchOption`, `Abort` (exit 1), `Exit`, `FileError`.
  - `shell_completion.py` — completion mode (`_<PROG>_COMPLETE`).
  - `testing.py` — `CliRunner` (`capture="sys"` and `"fd"`) and `Result`.
- `tests/` — `test_optlyn.py`, `test_optlyn_more.py` (128 tests; run `PYTHONPATH=src python3 -m pytest tests`).

Module named `paramtypes.py` (not `types.py`): a module called `types.py` shadows the standard library when Python runs from inside `src/optlyn`.

Each `# spec: N-…` comment in the code marks one implementation point; the id is a representative of the block that describes the feature.

## Conflicts in the spec and what was built

The export was made with `--allow-open`, so 28 contradictions have no human verdict (listed in `spec/MAP.md`). For each, the choice below was made. Where a PRD feature point and the Interface Contract disagree, the PRD's more specific feature statement was followed unless noted.

| Id | Disagreement | What was built |
|---|---|---|
| CF-000010 | Omitted repeatable option with no default: "absent value" (FP-01) vs "empty tuple, not absent" (FP-03) | `()` (empty tuple), per FP-03 |
| CF-000016, CF-000092 | `IntRange` clamp beyond an open bound: "nearest included value" vs "the bound itself" | adjacent integer inside the range (FP-05) |
| CF-000034, CF-000072 | Environment vs default map precedence: Contract says default map beats env; FP-03 ranks env above default map | environment wins over default map (FP-03 ranking) |
| CF-000047 | Epilog placement: "end of page" (FP-02) vs "right after description" (Contract) | end of the help page (FP-02) |
| CF-000048 | Counting option omitted: `0` (FP-03) vs `None` (Contract) | `0` |
| CF-000063 | Default short help: first sentence (FP-02) vs first paragraph cut at 45 (Contract) | first sentence, cut at 45 characters with `...` |
| CF-000087 | Default maximum content width: 80 (FP-02) vs 100 (FP-11) | help pages use 80 (`max_content_width`); `wrap_text` default width is 100 (FP-11) |
| CF-000088 | Environment name list: first set wins (FP-03) vs last set wins (Contract) | first set wins |
| CF-000100, CF-000107 | `FloatRange` clamp with an open bound: refused (FP-05) vs allowed (Contract) | refused with `TypeError` at construction |
| CF-000115 | Default metavar of an integer option: `INTEGER` (rule) vs `COUNT` (example) | `INTEGER` (the stated rule) |
| CF-000128 | Pause when not interactive: "does nothing" vs "still prints its message" | prints the message, does not wait |
| CF-000129 | Application config dir on Unix: honour `XDG_CONFIG_HOME` (FP-11) vs always `~/.config` (Contract) | honours `XDG_CONFIG_HOME` |
| CF-000134 | Confirmation mismatch: re-ask the pair (FP-08) vs abort (FP-13) | re-asks the pair (FP-08); the FP-13 abort case is not applied |
| CF-000136 | Date-time format list: replaces the defaults (FP-05) vs added to them (FP-16) | replaces the defaults |
| CF-000151, CF-000157 | Boolean flag env value that is not recognised: usage error (FP-03) vs turns the flag off (FP-05) | plain boolean flag: usage error; a flag with a non-boolean flag value: unrecognised text is treated as unset (FP-03) |
| CF-000154 | `isolated_filesystem`: removed on exit (no parent) vs always left in place | removed when no `temp_dir` is given; left in place when one is (the clause about the parent case) |
| CF-000155 | Callback for an omitted parameter: runs (FP-03) vs not run (terminology) | runs (FP-03) |
| CF-000156 | Form feed in a docstring: text after it omitted (FP-02) vs kept (Contract) | text after it omitted; the form feed itself removed |
| CF-000158 | Date-time formats: first match wins (FP-05) vs last match (Contract) | first match wins |
| CF-000159 | Prompt conversion failure: re-ask (FP-08) vs not asked again (FP-13) | re-asks (FP-08) |
| CF-000160 | `Path(resolve_path=True)` and `~`: not expanded (FP-09) vs expanded (Contract) | not expanded |
| CF-000161 | Completion of an empty token: subcommands only, options once a dash is typed (FP-12) vs subcommands then options (Contract) | FP-12 behaviour |
| CF-000162 | `show_default` on a `False` flag: hidden (FP-02) vs shown (Contract) | hidden |
| CF-000163 | `Choice` matching case: sensitive by default (FP-05) vs insensitive (Contract, for enum names) | case-sensitive by default; `case_sensitive=False` turns it off |

Other choices where the spec leaves room or the statements interact:

- `prompt_required` defaults to `True`: an omitted prompting option asks. `password_option` therefore asks when omitted; `confirmation_option` asks when the flag is omitted (declined → `Abort`).
- `Context.invoke(cmd, **values)` passes the caller's values and fills the target's omitted parameters with their defaults (so the callback signature still works); `forward` merges the current parameters first.
- All tokens are parsed before any eager flag runs, so a usage error anywhere beats `--help`; eager flags then run in the order typed.
- A group's callback runs after the subcommand name is resolved and before the child's own arguments are parsed. In chain mode the children are parsed first, then the group callback runs.
- Help shown for a no-argument command with `no_args_is_help` (groups by default, leaves if configured) prints to stderr and exits 2, per FP-02.
- Destination inference keeps the case of the name and only turns `-` into `_` (so `--Name` gives `Name`); a long name is preferred.
- A second variadic argument on one command is refused at declaration (`TypeError`), as the PRD allows.
- `token_normalize_func` applies to option names, choice values and command names.

## Checklist accounting

`spec/CHECKLIST.md` was not edited (the instructions say to keep `spec/` as it is). The 1044 ids are in 33 contiguous runs, one per pack (pack 01 has none). Every pack is marked `implemented` below; ids of packs 14, 15 and 18 are informational or non-goals and are marked as satisfied by design. Ids that describe platform or interactive behaviour are only partly exercised, and the caveats say which.

| Pack | Unit | Ids | Where | Status |
|---|---|---|---|---|
| 02 | Hardware requirements · Summary | N-000775–N-000779 (5) | pyproject.toml; no runtime deps | implemented |
| 03 | Hardware requirements · Execution profiles | N-000780–N-000789 (10) | pyproject.toml (src layout, setuptools PEP 517) | implemented; Linux only exercised; macOS/Windows branches (get_app_dir, launch, argv expansion) not run |
| 04 | Interface Contract (decision) | N-000790 | — | implemented |
| 05 | Contract §1 Package and modules | N-000791–N-000802 (12) | src/optlyn/__init__.py; testing.py; formatting.py | implemented |
| 06 | Contract §2 Global output forms | N-000803–N-000849 (47) | core.py Command.format_help, Context exits; exceptions.py; decorators.py version options | implemented |
| 07 | Contract §3 Declaring commands and groups | N-000850–N-000880 (31) | core.py Command, Group, CommandCollection; decorators.py command/group | implemented |
| 08 | Contract §4 Parameters | N-000881–N-000935 (55) | core.py Parameter, Option, Argument, _OptionParser; decorators.py option/argument | implemented |
| 09 | Contract §5 Parameter types | N-000936–N-000949 (14) | paramtypes.py | implemented |
| 10 | Contract §6 Invocation context | N-000950–N-000980 (31) | core.py Context; decorators.py pass_context/pass_obj/make_pass_decorator | implemented |
| 11 | Contract §7 Terminal helpers | N-000981–N-001012 (32) | termui.py; formatting.py | implemented; partly exercised (pager, progress drawing, editor/launch on Linux only) |
| 12 | Contract §8 Shell completion | N-001013–N-001037 (25) | shell_completion.py | implemented |
| 13 | Contract §9 In-process runner | N-001038–N-001044 (7) | testing.py | implemented |
| 14 | PRD product overview | N-000001–N-000014 (14) | whole package (pure Python, no I/O at import) | satisfied |
| 15 | PRD terminology | N-000015–N-000024 (10) | whole package | satisfied |
| 16 | PRD public surface | N-000025–N-000044 (20) | __init__.py exports | implemented |
| 17 | PRD non-functional constraints | N-000045–N-000069 (25) | whole package; core.py thread-local context stack (_utils.py) | implemented; Windows argv expansion (windows_expand_args) implemented but not run on Windows |
| 18 | PRD non-goals | N-000070–N-000078 (9) | not built (non-goals) | satisfied by omission |
| 19 | FP-01 Command declaration, naming, invocation | N-000079–N-000109 (31) | core.py Command.invoke/make_context; decorators.py command() | implemented |
| 20 | FP-02 Automatic help and eager flags | N-000110–N-000177 (68) | core.py help/usage; decorators.py help/version options | implemented |
| 21 | FP-03 Options | N-000178–N-000284 (107) | core.py Option, _OptionParser, Command._process | implemented |
| 22 | FP-04 Positional arguments | N-000285–N-000329 (45) | core.py Argument, _distribute_arguments | implemented |
| 23 | FP-05 Parameter types and conversion | N-000330–N-000383 (54) | paramtypes.py | implemented |
| 24 | FP-06 Groups, nesting, deferred loading | N-000384–N-000433 (50) | core.py Group, CommandCollection | implemented |
| 25 | FP-07 Invocation context, defaults, env | N-000434–N-000483 (50) | core.py Context, Parameter sources, auto env prefix | implemented |
| 26 | FP-08 Prompts, confirmation, hidden input | N-000484–N-000527 (44) | termui.py prompt/confirm; core.py Option.resolve; decorators.py password/confirmation options | implemented |
| 27 | FP-09 File and path parameters | N-000528–N-000590 (63) | paramtypes.py File, Path, open_file | implemented |
| 28 | FP-10 Chaining and pipelines | N-000591–N-000617 (27) | core.py Group._invoke_chain | implemented |
| 29 | FP-11 Terminal output and helpers | N-000618–N-000688 (71) | termui.py (echo, style, pager, progressbar, getchar, pause, edit, launch, clear, get_app_dir) | implemented; partly exercised: interactive TTY paths (getchar via /dev/tty, pager, progress drawing, pause wait) are not run here |
| 30 | FP-12 Shell completion | N-000689–N-000715 (27) | shell_completion.py | implemented; partly exercised: bash path tested; zsh/fish/PowerShell scripts are written but not run in a shell |
| 31 | FP-13 Usage failures, abort, exit status | N-000716–N-000735 (20) | exceptions.py; core.py Command.main | implemented |
| 32 | FP-14 In-process runner | N-000736–N-000763 (28) | testing.py | implemented |
| 33 | Cross-cutting refinements | N-000764–N-000774 (11) | formatting/ paramtypes/ core.py (cross-cutting) | implemented |

## Not exercised here

- Windows and macOS branches: `get_app_dir` (APPDATA, Library/Application Support), `launch` (`os.startfile`, `open -R`), argv glob/`~`/`%VAR%` expansion, and the `windows` profile in the hardware spec.
- Interactive terminal paths: `getchar` via `/dev/tty`, pager through `PAGER`, progress-bar drawing, and the wait in `pause`; prompts that use `getpass` on a real TTY.
- Shell scripts for zsh, fish and PowerShell are written from the contract but were not run in those shells; bash completion was exercised through the environment interface (`COMP_WORDS`, `COMP_CWORD`).
- `CliRunner(capture="fd")` works in a quick check but has only the basic test.

## Not built

Nothing in the spec is deliberately left out. The non-goals (remote server, GUI, plugin discovery, aliases, config-file syntax, thread-safe mutation) are respected by design rather than implemented.
