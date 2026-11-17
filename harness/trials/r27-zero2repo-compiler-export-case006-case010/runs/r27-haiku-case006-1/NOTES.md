# Optlyn — build notes

Implementation of the Optlyn specification in `spec/` (1044 checklist ids, 33 packs). `spec/` is untouched.

## Layout

| Path | Contents |
| --- | --- |
| `pyproject.toml` | src-layout, setuptools PEP 517 backend, no runtime dependencies (Python >= 3.10) |
| `src/optlyn/__init__.py` | package-root exports (declaration names, classes, types, terminal helpers) |
| `src/optlyn/core.py` | `Context`, `Parameter` / `Option` / `Argument`, argument parser, `Command` / `Group` / `CommandCollection`, chaining |
| `src/optlyn/decorators.py` | `command`, `group`, `option`, `argument`, ready-made options, `pass_*` decorators |
| `src/optlyn/param_types.py` | built-in types (`STRING`, `INT`, ..., `Choice`, `DateTime`, ranges, `Tuple`, `File`, `Path`), custom types |
| `src/optlyn/exceptions.py` | `BadParameter`, `MissingParameter`, `UsageError` family, `Abort`, `Exit`, `FileError` |
| `src/optlyn/termui.py` | `echo`, `style`, prompts, confirm, getchar, pause, pager, progress bar, editor, launch, clear |
| `src/optlyn/utils.py` | `open_file` / lazy and atomic files, standard-stream wrappers, `get_app_dir`, `format_filename`, `launch` |
| `src/optlyn/formatting.py` | `wrap_text`, definition-list layout for help pages |
| `src/optlyn/shell_completion.py` | bash / zsh / fish / PowerShell registration scripts and suggestion output |
| `src/optlyn/testing.py` | `CliRunner`, `Result`, `isolated_filesystem` |
| `src/optlyn/_state.py` | thread-local context stack, `get_current_context` |
| `tests/test_optlyn.py` | behavioural tests (90), grouped by feature point |

Code is marked with `# spec: <ids>` beside what implements them (the ids are the `↳` ranges of each pack).
Run the tests with `PYTHONPATH=src python -m pytest tests`.

## Conflicts and what was built

Precedence rule used: where the Interface Contract (packs 04–13) and the PRD (packs 14–33) disagree on
**behaviour or defaults**, the PRD wins (the contract itself defers behaviour and defaults to the PRD,
pack 04, N-000790). Where two PRD statements disagree, the more specific feature point wins.

### A. The 18 unsettled contradictions listed in `spec/MAP.md`

1. **CF-000010** — value of an omitted repeatable option with no default.
   - Side 1: `19-…fp-01…` N-000093 "is passed as an absent value".
   - Side 2: `21-…fp-03…` N-000211 "receives an empty tuple, not an absent value"; also the Contract `08-…` value table (N-000914–N-000920).
   - **Built:** empty tuple `()`.
2. **CF-000016, CF-000092** — `IntRange` with `clamp=True` and a value beyond an open bound.
   - Side 1: `23-…fp-05…` N-000361/N-000362 "replaced by the nearest included value" / "the adjacent integer inside the range".
   - Side 2: Contract `09-…` N-000941/N-000943 "becomes that bound's value".
   - **Built:** adjacent integer inside the range (the open bound itself is excluded).
3. **CF-000100, CF-000107** — `FloatRange` with `clamp` and an open bound.
   - Side 1: `23-…fp-05…` N-000381 "refuses clamp when a bound is open"; N-000364 "clamp only when both bounds are closed".
   - Side 2: Contract `09-…` N-000943 (clamp with an open bound turns out-of-range values into the bound).
   - **Built:** `ValueError` at construction for clamp with an open bound.
4. **CF-000034, CF-000072** — environment variable versus default map.
   - Side 1: `21-…fp-03…` N-000243–N-000245 and `25-…fp-07…` N-000450–N-000462: order is command line, environment, default map, declared default.
   - Side 2: Contract `10-…` N-000955 "its values take precedence over environment variables".
   - **Built:** environment ranks above default map.
5. **CF-000047** — epilog placement.
   - Side 1: `20-…fp-02…` N-000126 "printed at the end of the help page"; Contract `06-…` N-000844 lists the epilog last.
   - Side 2: Contract `07-…` N-000853 "printed right after the description, before the options".
   - **Built:** epilog last.
6. **CF-000048** — counting option when omitted.
   - Side 1: `21-…fp-03…` N-000207 "zero if omitted".
   - Side 2: Contract `08-…` N-000920 "`None` when the option was omitted".
   - **Built:** `0`.
7. **CF-000063** — default short help of a subcommand.
   - Side 1: `20-…fp-02…` N-000122 "the first sentence of the docstring … ellipsized if it cannot fit".
   - Side 2: Contract `06-…` N-000843 "the start of the child's first paragraph, cut with `...` at 45 characters".
   - **Built:** first sentence of the first paragraph, cut to 45 characters with `...` (satisfies both).
8. **CF-000087** — default maximum content width.
   - Side 1: `20-…fp-02…` N-000134 "defaults to 80 columns" (help pages).
   - Side 2: `29-…fp-11…` N-000680 "Help pages and wrapped text use … 100 columns unless the caller sets another".
   - **Built:** help pages 80 (`max_content_width`); `wrap_text` default width 100.
9. **CF-000088** — list of environment names.
   - Side 1: `21-…fp-03…` N-000227 "first one set wins".
   - Side 2: Contract `08-…` N-000893 "the last name that is set wins".
   - **Built:** first set wins.
10. **CF-000115** — default metavar of an integer option.
    - Side 1: `20-…fp-02…` N-000139–N-000144 "the type name in uppercase"; the same bullet's example says `INTEGER`.
    - Side 2: the example's `--count COUNT` in N-000144.
    - **Built:** `--count INTEGER` (the general rule; the `COUNT` example is not followed).
11. **CF-000128** — `pause` when not interactive.
    - Side 1: `29-…fp-11…` N-000663 "when not interactive it does nothing".
    - Side 2: N-000687 "it still prints its message there" (and "must not block").
    - **Built:** prints the message and does not block.
12. **CF-000129** — application config directory on Unix.
    - Side 1: `29-…fp-11…` N-000676 "`$XDG_CONFIG_HOME` when that variable is set".
    - Side 2: Contract `11-…` N-001005 "On Unix the directory is always under `~/.config`".
    - **Built:** `$XDG_CONFIG_HOME` when set, otherwise `~/.config`.
13. **CF-000134** — mismatched confirmation prompt.
    - Side 1: `26-…fp-08…` N-000511 "rejects a mismatch by asking the pair again".
    - Side 2: `31-…fp-13…` N-000723 "two different values typed into a confirmation prompt" → abort, exit 1.
    - **Built:** re-ask the pair (FP-08 is the feature point that owns prompts; FP-13 lists the abort cases generally).
14. **CF-000136** — author date-time format list.
    - Side 1: `16-…public-surface…` N-000032 "is added to the default formats".
    - Side 2: `23-…fp-05…` N-000356 "replaces the default list (it does not extend it)".
    - **Built:** replaces the defaults.
15. **CF-000151** — environment value for a boolean flag that is neither true nor false.
    - Side 1: `23-…fp-05…` N-000344 "anything else is a usage error".
    - Side 2: `23-…fp-05…` N-000345 "any other value turns the flag off".
    - **Built:** usage error (FP-03 N-000234–N-000242 states the rule for flag environment values specifically).

### B. Disagreements not in the map's list

16. **Callbacks for omitted parameters.**
    - Side 1: glossary (`15-…terminology…`, "Callback" row): "A parameter callback is not called for a parameter that was omitted and received no value from any source."
    - Side 2: `21-…fp-03…` N-000263 "A missing parameter still runs its callback, so that callback can default from an earlier parameter's value".
    - **Built:** callbacks run for every declared parameter, receiving `None` (or `()`) when no source supplied a value.
17. **Choice matching case.**
    - Side 1: Contract `09-…` table: for an enumeration "by default the match ignores letter case".
    - Side 2: Contract signature `Choice(choices, case_sensitive=True)`; PRD `23-…fp-05…` N-000348 "case-sensitive unless the author turns that off".
    - **Built:** case-sensitive by default.
18. **`Path(resolve_path=True)` and a leading `~`.**
    - Side 1: Contract `09-…` "a leading `~` is first expanded to the home directory".
    - Side 2: `27-…fp-09…` N-000548–N-000573 "a leading tilde is not expanded".
    - **Built:** not expanded (PRD).
19. **`DateTime` when several formats match.**
    - Side 1: Contract `09-…` "the last matching format is used".
    - Side 2: `23-…fp-05…` N-000353–N-000357 "Formats are tried in order; the first success wins".
    - **Built:** first success wins.
20. **Completion of an empty word.**
    - Side 1: Contract `12-…` N-001017–N-001019 "the suggestions for an empty token are the subcommand names followed by the option names".
    - Side 2: `30-…fp-12…` N-000694–N-000700 "Options are listed only once at least a dash has been typed".
    - **Built:** empty word offers subcommands and arguments, and options only after a dash (PRD).
21. **Isolated filesystem cleanup.**
    - Side 1: `32-…fp-14…` N-000744 "When no parent is given, the runner removes that directory on exit".
    - Side 2: same bullet, N-000747 "The new directory is always left in place after the block ends".
    - **Built:** removed when no `temp_dir` is given; left in place when one is given.
22. **Form feed in help text** (reconciled, not really in conflict). Contract `07-…` N-000853: a form feed in an explicit `help=` is dropped and the text after it kept. PRD `20-…fp-02…` N-000114–N-000117: in a docstring, text after a form feed is omitted. **Built:** both, for their respective inputs.

## Checklist status

Every id in `spec/CHECKLIST.md` is accounted for. Status is at pack granularity: the ids of a pack are one contiguous block, and each pack is implemented in the modules named below. "Covered by tests" means the behaviours described by the pack are exercised by `tests/test_optlyn.py`; I did not write one test per id.

| Pack | Ids | Status | Where |
| --- | --- | --- | --- |
| 01 | none | no claims | — |
| 02 | N-000775–N-000779 | implemented | `pyproject.toml`, `src/optlyn` (no runtime deps) |
| 03 | N-000780–N-000789 | implemented; Linux only verified | `pyproject.toml` (src layout, PEP 517); Windows/macOS not run here |
| 04 | N-000790 | implemented | whole package (form left to implementer) |
| 05 | N-000791–N-000802 | implemented | `__init__.py` (exports), `formatting.py` (`wrap_text`) |
| 06 | N-000803–N-000849 | implemented; covered by tests | `core.py` (`Command.main`, help), `exceptions.py`, `termui.py`, `decorators.py` (version) |
| 07 | N-000850–N-000880 | implemented; covered by tests | `decorators.py` (`command`, `group`), `core.py` (`Command`, `Group`, `CommandCollection`) |
| 08 | N-000881–N-000935 | implemented; covered by tests | `core.py` (`Option`, `Argument`, `_Parser`), `decorators.py` |
| 09 | N-000936–N-000949 | implemented; covered by tests | `param_types.py` |
| 10 | N-000950–N-000980 | implemented; covered by tests | `core.py` (`Context`), `decorators.py` (`pass_*`), `_state.py` |
| 11 | N-000981–N-001012 | implemented; partly covered | `termui.py`, `formatting.py`, `utils.py` |
| 12 | N-001013–N-001037 | implemented; output checked, shells not run | `shell_completion.py` |
| 13 | N-001038–N-001044 | implemented; covered by tests | `testing.py` |
| 14 | N-000001–N-000014 | overview; satisfied by the package as a whole | — |
| 15 | N-000015–N-000024 | terminology; used throughout | — |
| 16 | N-000025–N-000044 | implemented; no console script shipped (N-000044 says authors ship scripts, not Optlyn) | — |
| 17 | N-000045–N-000069 | implemented; Windows arg expansion in `core.py` (`_expand_windows_args`) untested | `core.py`, `_state.py` (thread-local context) |
| 18 | N-000070–N-000078 | non-goals; satisfied by omission (no aliases, plugins, server, GUI, config syntax, thread-safe context) | — |
| 19 | N-000079–N-000109 | implemented; covered by tests | `decorators.py` (naming), `core.py` (`Command.main`, `_process_params`) |
| 20 | N-000110–N-000177 | implemented; covered by tests | `core.py` (`format_help`, `get_help_option`), `decorators.py` (version), `formatting.py` |
| 21 | N-000178–N-000284 | implemented; covered by tests | `core.py` (`Option`, `_Parser`, `Option.gather`) |
| 22 | N-000285–N-000329 | implemented; covered by tests | `core.py` (`Argument`, `_Parser.bind_arguments`) |
| 23 | N-000330–N-000383 | implemented; covered by tests | `param_types.py` |
| 24 | N-000384–N-000433 | implemented; covered by tests | `core.py` (`Group`, `resolve_command`, `CommandCollection`) |
| 25 | N-000434–N-000483 | implemented; covered by tests (prefix, default map, sources) | `core.py`, `decorators.py` (`make_pass_decorator`) |
| 26 | N-000484–N-000527 | implemented; prompts covered via input; no real TTY | `termui.py` (`prompt`, `confirm`), `core.py` (`Option._prompt_value`), `decorators.py` |
| 27 | N-000528–N-000590 | implemented; covered by tests (atomic and lazy checked manually) | `param_types.py` (`File`, `Path`), `utils.py` |
| 28 | N-000591–N-000617 | implemented; covered by tests | `core.py` (`Group._invoke_chain`) |
| 29 | N-000618–N-000688 | implemented; pager/getchar/edit/progress partly checked | `termui.py`, `formatting.py`, `utils.py` |
| 30 | N-000689–N-000715 | implemented; completion output checked, shells not run | `shell_completion.py` |
| 31 | N-000716–N-000735 | implemented; covered by tests | `exceptions.py`, `core.py` (`Command.main`) |
| 32 | N-000736–N-000763 | implemented; fd capture only lightly tested | `testing.py` |
| 33 | N-000764–N-000774 | implemented; covered by tests | `core.py`, `decorators.py` |

Not done, with reasons: none of the ids is left undone. Items I could not check here are listed below.

## Not verified here

- Windows and macOS: `get_app_dir` (Windows/macOS branches), `launch`, Windows argument expansion, and console colour were not run.
- No real terminal in the environment: hidden password input, `getchar` on `/dev/tty`, the pager, and the progress-bar rendering were exercised only through their non-interactive paths.
- Shell completion: the bash script output was checked, but zsh, fish and PowerShell scripts were not loaded into their shells.
- `CliRunner(capture="fd")`: stdout and stderr are kept in separate files, so `Result.output` is stdout followed by stderr rather than true interleaved write order.
- Group option mixing (`allow_interspersed_args=True` on a group) is implemented roughly, with no dedicated test.
