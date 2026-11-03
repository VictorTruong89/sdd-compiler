# Notes on the Optlyn build

Build: pure Python package under `src/optlyn`, no runtime dependencies, Python 3.10+.
Run with `PYTHONPATH=src`. `pyproject.toml` is provided for a PEP 517 install but nothing needs it.
Tests: `PYTHONPATH=src python3 -m pytest tests` (98 tests, all passing).
`spec/` is unchanged. `# spec: N-xxxxxx` comments mark code that satisfies specific claims.

## Spec disagreements and what was built

The export was made with `--allow-open`, so 28 contradictions are unsettled. Each one below records
which reading was built. Where the sources were pack-level text, the feature-point (FP) text in
`Full_PRD.md` was preferred over the Interface Contract when the FP text was more specific.

| Contradiction | Disagreement | Built |
|---|---|---|
| CF-000010 | Omitted repeatable option (or variadic argument) with no default: "absent value" (FP-01) vs "empty tuple, not absent" (FP-03) | Delivers `()`. |
| CF-000016, CF-000092 | `IntRange` clamp beyond an open bound: "adjacent integer inside the range" vs "the bound itself" | Adjacent integer inside the range (`min+1` / `max-1`). |
| CF-000100, CF-000107 | `FloatRange` with an open bound and `clamp=True`: refused (FP-05) vs allowed (Interface) | Refused at construction with `DeclarationError`. |
| CF-000034, CF-000072 | Environment vs default map precedence | Command line, then environment, then default map, then declared default (FP-03 ranking). |
| CF-000047 | Epilog position: end of page (Interface section 2, FP-02) vs right after description (Interface attrs) | End of the help page. |
| CF-000156 | Form feed: docstring text after it is omitted (FP-02) vs kept (Interface, `help=` keyword) | Docstring: truncated at the form feed. Explicit `help=` keyword: the form feed is dropped and the text after it is kept. |
| CF-000048 | Counting option when omitted: 0 (FP-03) vs `None` (Interface) | 0 (or the declared default). |
| CF-000088 | Environment name list: first set wins (FP-03) vs last set wins (Interface) | First set wins. |
| CF-000162 | `show_default` on a boolean flag whose default is False | Hidden (FP-02). |
| CF-000063 | Subcommand short help: first sentence (FP-02) vs first paragraph cut at 45 chars (FP-02 / Interface) | First sentence of the docstring; if longer than 45 characters, cut to 42 + `...`. An explicit `short_help` is used as given. |
| CF-000087 | Default maximum content width: 80 (FP-02) vs 100 (FP-11 / constraint) | 80 for help pages. `wrap_text` has its own width argument (default 78). |
| CF-000115 | Option metavar: type name in uppercase (`INTEGER`) vs example `--count COUNT` | Type name (`--count INTEGER`), following the general rule. The example was not followed. |
| CF-000129 | Application directory: honour `XDG_CONFIG_HOME` (FP-11) vs always `~/.config` (Interface) | Honour `XDG_CONFIG_HOME` when set. |
| CF-000128 | `pause` when not interactive: does nothing (FP-11) vs prints its message (FP-11 boundary) | Prints the message and does not block. |
| CF-000161 | Completion of an empty token: subcommand names then option names (Interface) vs options only after a dash (FP-12) | Subcommand names only for an empty token. Options are listed only once a dash has been typed. |
| CF-000157, CF-000151 | Boolean flag from environment with an unrecognised non-empty value: usage error (FP-03, FP-05) vs turns the flag off (FP-05) | Usage error for boolean flags. For a flag with a non-boolean flag value, an unrecognised value counts as unset. |
| CF-000158 | Date-time formats: first success wins (FP-05) vs last matching format (Interface) | First success wins. |
| CF-000160 | `Path(resolve_path=True)` and a leading `~`: expanded (Interface) vs not expanded (FP-09) | Not expanded (realpath only). |
| CF-000163 | `Choice` matching: case-sensitive by default (signature, FP-05) vs ignores case by default (Interface note) | Case-sensitive by default. |
| CF-000134 | Confirmation mismatch: ask the pair again (FP-08) vs two different values abort (FP-13) | Ask the pair again. End of input during the pair aborts. |
| CF-000159 | Conversion failure at a prompt: prompt re-asks (FP-08) vs not asked again (FP-13) | Prompt re-asks. Conversion failures from other sources are usage errors (exit 2). |
| CF-000154 | `isolated_filesystem` without a parent: removed on exit (FP-14 first sentence) vs always left in place (FP-14 last sentence) | Always left in place. |
| CF-000136 | Custom date-time format list: added to defaults (FP-03 public surface) vs replaces defaults (FP-05, Interface) | Replaces the defaults. |
| CF-000155 | Callback for an omitted parameter: not called (terminology) vs runs and may default from earlier values (FP-03) | Runs for every parameter, including omitted ones. |

Other choices where the spec left the form to the implementer:

- Help layout: `Usage:` line, description, `Positional arguments:`, `Options:`, `Commands:`, epilog.
  Option entries list names, then metavar, then help, then bracketed extras (`[default: x]`,
  `[env var: X]`). Deprecated items carry `(Deprecated)`.
- Usage line: `[OPTIONS]` appears when there is a visible option. Groups show `COMMAND [ARGS]...`,
  `[COMMAND] [ARGS]...` when they can run without a subcommand, and the chained form when chaining.
- Completion protocol: suggestions are one per line. Zsh and fish add `<TAB>help`. Path requests are
  `@@file:<token>` or `@@dir:<token>`. Unknown `_<PROG>_COMPLETE` instructions print an error to
  standard error and exit 1.
- Parameter source values are the `ParameterSource` enum members (five distinct values).
- Feature-switch groups (several options sharing one destination): the most explicit source wins.
  Ties go to an explicit default over an auto-derived one, then to the last declared option.
- `getchar` reads `/dev/tty` in raw mode and falls back to standard input when that is not available.
- Result of `CliRunner(capture="fd")`: standard output and standard error are captured through
  descriptors, so their relative order is not preserved in `output`.
- Chaining group `invoke()` returns the list of subcommand return values (with standalone mode off),
  whether or not a result callback is registered. The result callback still runs.

## Coverage against `spec/CHECKLIST.md`

All 33 packs were read and implemented. `spec/CHECKLIST.md` is unchanged, as instructed, so the
per-id state is recorded here rather than in the checklist. Coverage by pack:

- Packs 01–03 (hardware and execution profiles): pure Python, no runtime dependencies, src layout,
  `pyproject.toml` with a PEP 517 backend. Implemented.
- Packs 04–13 (Interface Contract): implemented. The package exports are in `optlyn/__init__.py`.
  `optlyn.testing.CliRunner` and `optlyn.formatting.wrap_text` are present.
- Packs 14–18 (PRD overview, terminology, inventory, non-functional constraints, non-goals): covered
  by the implementation as a whole. Non-goals are respected (no server, GUI, aliases, or config
  format).
- Packs 19–33 (FP-01 to FP-14 and cross-cutting refinements): implemented. The tests in
  `tests/test_optlyn.py` are grouped by feature point.

Known gaps and things that were not exercised:

- Windows-only behaviour is not implemented: expansion of globs, home directories and environment
  tokens in `argv` (N-000051 to N-000055), and the `os.startfile` path in `launch` is untested.
  The target is Linux.
- Not tested on a real terminal: raw-mode `getchar`, the real pager (`PAGER`/`less`), and
  `echo` behaviour on a TTY (colour kept).
- Shell completion scripts for zsh, fish and PowerShell were only checked for generation, not run in
  their shells. Bash was not run either.
- `edit` depends on an editor on the path. There is no test for it.
- `version_option()` without a version or package name infers the package from the calling module. A
  distribution that is not installed cannot be detected (`RuntimeError` at callback time).
- The Context is thread-local (FP-07 threading), but no test checks another thread's view.
- The progress bar's remaining-time estimate is approximate.
- Claims not individually traced to code: the `MAY` and `example` claims. Their behaviour is implemented
  where the FP text describes it, but there is no separate id-level audit.
