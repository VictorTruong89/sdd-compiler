# Optlyn — implementation notes

Built from `spec/` (not modified). Package: `src/optlyn`. Tests: `tests/test_optlyn.py`
(run with `PYTHONPATH=src python -m pytest tests`; 19 pass). Zero runtime dependencies,
Python ≥ 3.10, src layout with `pyproject.toml` (PEP 517).

## Spec disagreements and what was built

The export was made with `--allow-open`; `spec/MAP.md` lists 28 contradictions with no
human verdict. Each one is listed below with both sides, where each side is, and the
choice made. "A" and "B" are the two claims as quoted in the pack's *Conflicts* section.

1. **CF-000010** — repeatable option omitted with no default. A (FP-01 N-000093): "is passed as an absent value". B (FP-03 N-000211): "receives an empty tuple, not an absent value". **Built: `()`** (B, the more specific FP-03 rule).

2. **CF-000016 / CF-000092** — integer range, clamp, value beyond an *open* bound. A (FP-05 N-000361/N-000362): "the nearest included value … the adjacent integer inside the range for an open bound". B (Interface §5 N-000941/N-000943): "becomes that bound's value". **Built: adjacent integer inside the range (A).**

3. **CF-000034 / CF-000072** — value precedence, environment vs default map. A (FP-07/FP-03 N-000243, N-000245): "then environment, then the default map"; ranking "command line, environment, default map, declared default". B (Interface §6 N-000955): default-map values "take precedence over environment variables". **Built: environment before default map (A).** The default map still beats the declared default.

4. **CF-000047** — epilog placement. A (FP-02 N-000126): "printed at the end of the help page, after everything else on it". B (Interface §3 N-000853): "printed right after the description, before the options". **Built: end of the page (A).**

5. **CF-000048** — counting option when omitted. A (FP-03 N-000207): "zero if omitted". B (Interface §4 N-000920): "`None` when the option was omitted". **Built: `0` (A).**

6. **CF-000063** — default short help for subcommands. A (FP-02 N-000122): "the first sentence of the docstring". B (Interface §2 N-000843): "the start of the child's first paragraph, cut with `...` at 45 characters". **Built: first sentence, cut with `...` at 45 characters** (satisfies both where they overlap).

7. **CF-000087** — default maximum content width. A (FP-02 N-000134): "defaults to 80 columns". B (N-000680, pack 29 and others): "a maximum content width of 100 columns unless the caller sets another". **Built: help auto-detected width capped at 80 (A); `wrap_text` default width 100 (B), since it is a direct helper.**

8. **CF-000088** — list-valued envvar. A (FP-03 N-000227): "first one set wins". B (Interface §4 N-000893): "the last name that is set wins". **Built: first set wins (A).**

9. **CF-000100 / CF-000107** — float range clamp with an open bound. A (FP-05 N-000381, N-000364): clamp refused / "only allowed when both bounds are closed". B (Interface §5 N-000943): clamp with open bound valid. **Built: refused at construction with `ValueError` (A).**

10. **CF-000115** — default metavar for an integer option. A (FP-02 N-000140): "the type name in uppercase". B (FP-02 N-000144): "`--count COUNT`". **Built: type name, so `--count INTEGER` (A).**

11. **CF-000128** — non-interactive `pause`. A (FP-11 N-000663): "when not interactive it does nothing". B (FP-11 N-000687): "it still prints its message there". **Built: does nothing (A).**

12. **CF-000129** — application config directory on Unix. A (FP-11 N-000676): under `$XDG_CONFIG_HOME` when set, otherwise `~/.config`. B (Interface §7 N-001005): "always under `~/.config`". **Built: A.**

13. **CF-000134 / CF-000159** — confirmation mismatch and prompt conversion failure. A (FP-08 N-000511, N-000520): mismatch "asking the pair again"; conversion failure "re-ask". B (FP-13 N-000723, N-000719): two different confirmation values → abort; a prompt value that fails conversion "is not asked again". **Built: A (mismatch re-asks the pair; conversion failure at a prompt re-asks; EOF is still an abort).**

14. **CF-000136** — author date-time formats. A (FP-05 N-000032): "added to the default formats". B (FP-05 N-000356): "replaces the default list (it does not extend it)". **Built: replaces (B).**

15. **CF-000151 / CF-000157** — unrecognized boolean text. A (FP-05 N-000344, FP-03 N-000238): text conversion "anything else is a usage error"; environment flag "any other non-empty string is a conversion usage error". B (FP-05 N-000345): env flag "any other value turns the flag off". **Built: text conversion of a BOOL *parameter* is a usage error (A, N-000344). Environment flags follow the FP-03 final bullet: unrecognized or empty values are treated as unset and the next source wins (neither error nor off).**

16. **CF-000154** — isolated filesystem cleanup. A (Interface §9 / FP-14 N-000745): "the runner removes that directory on exit" when no parent is given. B (FP-14 N-000747): "always left in place after the block ends". **Built: removed on exit when no parent is given; left in place when a parent path is given (A).**

17. **CF-000155** — callback for an omitted parameter. A (Terminology N-000022, FP-05 pass-through): "callback is not called for a parameter that was omitted". B (FP-03 N-000260): "A missing parameter still runs its callback". **Built: callbacks run for omitted parameters too (B, the more specific FP-03 rule); they receive `None`/default.**

18. **CF-000156** — form feed in help text. A (FP-02 N-000115): "text after that character is omitted from the help page". B (Interface §3 N-000853, `help` attr): "the text after it is kept". **Built: text after the form feed is dropped (A), for docstrings and the `help=` attribute alike.**

19. **CF-000158** — date-time format matching. A (FP-05 N-000354): "Formats are tried in order; the first success wins". B (Interface §5 N-000939): "the last matching format is used". **Built: first success wins (A).**

20. **CF-000160** — leading tilde on `Path(resolve_path=True)`. A (FP-09 N-000558): "a leading tilde is not expanded". B (Interface §5 N-000947): "a leading `~` is first expanded". **Built: expanded when `resolve_path=True` (B, the parameter-specific interface rule); not expanded otherwise.**

21. **CF-000161** — completion with an empty incomplete token. A (FP-12 N-000700): "Options are listed only once at least a dash has been typed". B (Interface §8 N-001019): "the subcommand names followed by the option names". **Built: A (no options until a dash is typed; subcommand names are offered).**

22. **CF-000162** — show-default for a `False` flag. A (Interface §4 N-000149 / FP-02): default "remains hidden even if show-default is on". B (Interface §4 N-000906): "a flag whose default is `False` included". **Built: hidden for a False flag default (A).**

23. **CF-000163** — choice matching case. A (FP-05 N-000348): "Matching is case-sensitive unless the author turns that off". B (Interface §5 N-000937): "by default the match ignores letter case". **Built: case-insensitive by default (B); `case_sensitive=True` restores exact matching.**

The 28 ids in `spec/MAP.md` are CF-000010, 016, 034, 047, 048, 063, 072, 087, 088, 092, 100, 107, 115, 128, 129, 134, 136, 151, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163. Items 1–23 above cover all of them (CF-000134/159, 151/157, and 016/092, 034/072, 100/107 are shared between two entries).

## Checklist accounting

`spec/CHECKLIST.md` was not edited. Accounting is at **pack level**: every pack from 02 to 33 is addressed by code, and the ids in the pack's claims are implemented unless listed under *Not done* below. I did not verify each of the 1044 ids individually against code, so per-id boxes are not ticked. Pack 01 has no ids.

- Packs 02–03 (hardware / execution profiles, N-000775–N-000789): zero dependencies, src layout, Python ≥ 3.10 in `pyproject.toml`, pure Python.
- Pack 04–05 (contract shell, package and exports, N-000790–N-000802): `src/optlyn/__init__.py` exports every name in §1; `optlyn.testing.CliRunner`, `optlyn.formatting.wrap_text`.
- Pack 06 (output forms, exit statuses, channels, help page, version identity): `help.py`, `exceptions.py`, `core.py` (`main`).
- Pack 07 (command, group, Group, CommandCollection): `core.py`.
- Pack 08 (parameters): `params.py`.
- Pack 09 (parameter types): `types.py`.
- Pack 10 (invocation context): `context.py`, `_context_stack.py`.
- Pack 11 (terminal helpers): `termui.py`.
- Pack 12 (shell completion): `completion.py`.
- Pack 13 (in-process runner): `testing.py`.
- Packs 14–18 (product overview, terminology, surface, non-functional, non-goals): covered by the modules above; non-goals not built (no server, GUI, aliases, config syntax).
- Packs 19–33 (FP-01 to FP-14 and cross-cutting refinements): covered by `core.py`, `params.py`, `types.py`, `fileio.py`, `termui.py`, `completion.py`, `testing.py`.

### Not done (known gaps)

- **Option optional value** (FP-03: flag alone yields the flag-value, flag plus token yields the token). Not implemented; a value option without a value is a usage error (or a prompt when `prompt` is set). No contract keyword exists for it.
- **Group option mixing** (FP-03: an author may enable mixing a group's own options after the subcommand name). Not implemented; group options must come before the subcommand name.
- **Feature-switch groups** (several options sharing one destination, FP-03 precedence by source tier). Only the last-resolved parameter wins; the tiered tie-break is not implemented.
- **Declaration-time refusals for `Option`**: `deprecated` with `required` or `prompt` is refused for `Argument` only; the `Option` case is not refused.
- **Chaining segmentation** (FP-10): each chained subcommand's tokens are split at the next known subcommand name; the spec's option-before-argument rule is not enforced beyond that.
- **Completion scripts** (FP-12): bash, zsh, fish and PowerShell scripts are minimal and were not tested in those shells. Path requests use a custom line format (`__optlyn_path__file`), which the spec allows.
- **Progress bar, pager, editor, launch**: behavior follows the spec's rules at a basic level (ASCII bar, `$PAGER`, `$VISUAL`/`$EDITOR`, `xdg-open`/`open`). Not exercised on a real terminal or on Windows.
- **Prompt on `getchar`** uses `/dev/tty` where available; the piped-stdin fallback reads `sys.stdin`. Windows is not handled.
- **`ctx.invoke` / `forward`** with a plain callable (not a `Command`) only calls it inside the context.
- **Type `split` of environment values for `File`/`Path`** uses `os.pathsep` as specified.
