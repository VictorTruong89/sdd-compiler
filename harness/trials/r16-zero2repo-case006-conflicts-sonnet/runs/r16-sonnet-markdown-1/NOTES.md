# Notes: specification conflicts and choices

Optlyn is a src-layout pure-Python package (`src/optlyn`), no build step.

Where the spec files disagree, this is what was built:

1. **Deprecation warning channel.** PRD FP-01 says standard output; Interface Contract section 2
   says standard error. Built: standard error (the Contract's channel table), emitted before the
   command's own output.
2. **`confirm` with an unrecognised answer.** Contract section 7 says it counts as no; PRD FP-08 says
   it asks again. Built: asks again (PRD); EOF while asking aborts.
3. **Maximum content width.** PRD FP-02 says 80 columns, FP-11 says 100. Built: 80 for help pages and
   wrapping (an explicit `terminal_width` is used as-is).
4. **Callbacks for omitted parameters.** PRD Terminology says a parameter callback is not called when
   nothing supplied a value; FP-03 says a missing parameter still runs its callback (so it can default
   from earlier values). Built: the callback runs with `None`.
5. **Default metavar example.** PRD FP-02 says the default metavar is the type name upper-cased but
   gives `--count COUNT` as the example for an int option. Built: the rule (`--count INTEGER`).
6. **`isolated_filesystem`.** PRD FP-14 says the directory is both removed (no parent given) and
   "always left in place". Built: removed when `temp_dir` is None, left in place otherwise.
7. **Interactive session** (pager, pause): interactive when stdin or stdout is a TTY (PRD definition).
8. **Single-flag default.** A flag with `default=True` yields `True` when given (PRD), rather than
   inverting it.
9. **Help layout.** Section headings are `Usage:`, `Positional arguments:`, `Options:`, `Commands:`;
   options are listed short-name first (`-c, --count INTEGER`).
