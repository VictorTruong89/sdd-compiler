# Implementation notes

Optlyn is built as a pure-Python package in `src/optlyn`, importable with `PYTHONPATH=src`.
There is no build step. Tests live in `tests/test_optlyn.py` (run with `PYTHONPATH=src python3 -m pytest tests`).

## Where the specification disagrees, and what was built

1. **Deprecation warning channel.** The PRD (FP-01) says the warning goes to standard output. The
   Interface Contract (section 2, Channels) says standard error. Built: standard error, following the
   Contract, since it is the more specific document about output channels.

2. **Maximum help width.** FP-02 says help content caps auto-detected width at 80 columns by default.
   FP-11 says help pages and wrapped text use 100 columns. Built: help pages cap at 80 (FP-02);
   `optlyn.formatting.wrap_text` defaults to 100 (FP-11).

3. **Isolated filesystem cleanup.** FP-14 says the runner removes the directory on exit when no parent
   is given, and also says the directory is always left in place. Built: removed on exit when no parent
   is given, left in place when a parent path is supplied.

4. **Callbacks for omitted parameters.** The PRD's callback definition says a parameter callback is not
   called for a parameter omitted with no value from any source. FP-03 says a missing parameter still
   runs its callback so it can default from an earlier parameter. Built: the callback always runs
   (receiving `None` or the empty default when nothing was supplied), so the second rule holds.
   Required parameters with no source fail before their callback runs.

5. **Destination name inference.** FP-03 says a name that is already a valid identifier wins, then the
   first long name, then the first short name. Built literally: the prefix-stripped flag names are
   checked for identifier validity in declaration order first. So `-v --verbose` gives destination `v`.

6. **Contract `main()` on success.** Standalone success calls `sys.exit(0)`. Non-standalone returns the
   callback's return value.

7. **Contract-required but unspecified forms.** Where the Contract leaves a form to the implementer, the
   choices are: `--help` is printed as `--help`; version identity is `"<prog>, version <v>"`; style
   codes are standard SGR; the completion scripts and suggestion lines are plain text with
   `value<TAB>help`. Path completion requests use a `\x00path` / `\x00dir` marker line.

## Known gaps

- **Feature-switch groups** (several flags sharing one destination): the last occurrence on the command
  line wins. The PRD's "most explicit source, then last declared" tiebreak is not implemented.
- **Chaining group options after an argument** follow the PRD's "options before arguments" rule, but
  mixing (group options after the subcommand name, with `allow_interspersed` enabled on a group) is not
  implemented; such tokens go to the subcommand.
- **Optional-value options** (a flag alone yields one value, flag plus token yields another) are not
  implemented because the Contract gives no keyword for them.
- **Shell completion for bash and zsh path arguments** emits the path marker but the generated
  registration scripts do not translate it into native path completion; the scripts simply forward the
  suggestion lines.
- **Completion of positional arguments** is not implemented; only option values and command names are
  completed.
- **Multi-value default-map strings** for fixed-arity (`nargs > 1`) non-repeatable options are split
  flat rather than chunked by arity.
- **Path completion and `launch`/`edit` on Windows** are untested; the Linux path is the target.
- **Pager output** uses `PAGER` only when both stdin and stdout are terminals.
- **Progress bar rendering** is a simple single-line renderer, not the full styled bar.
