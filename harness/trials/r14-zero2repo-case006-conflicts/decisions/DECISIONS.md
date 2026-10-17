# Decisions

The product owner has settled these disagreements in the specification. Where a decision below and
another part of the specification differ, the decision holds.

1. **Isolated filesystem (Full PRD, FP-14).** The directory is always left in place after the block
   ends, with or without a parent; it is never removed.
2. **Deprecation warning of a command (Full PRD, FP-01, against the Interface Contract's channels
   table).** A deprecated command's warning is written to standard output, ahead of the command's own
   output. Option and argument deprecation warnings stay on standard error.
3. **Default map and environment (Interface Contract §6, against Full PRD FP-03 and FP-07).** A
   default-map value takes precedence over an environment variable. The order is: command line,
   default map, environment, declared default.
4. **Standalone confirm (Interface Contract §7, against Full PRD FP-08).** An answer other than yes,
   no or an empty line counts as no; it is not asked again.
