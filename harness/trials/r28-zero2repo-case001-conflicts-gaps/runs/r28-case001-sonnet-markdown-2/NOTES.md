# NOTES

## Spec disagreements (and what was built)
1. Local-time fraction: Interface_Contract ("Return shape") says the fraction is "rounded to the nearest microsecond"; PRD FP-02 says digits after the sixth are "truncated, not rounded". Built: truncation.
2. Trailing comma in arrays: Interface_Contract says "an array whose last element is followed by a comma is refused"; PRD FP-01 says arrays "may ... end with a trailing comma" (and TOML 1.1.0 allows it). Built: accepted.
3. Empty keys: Interface_Contract says keys are "never empty"; PRD FP-01 says "A quoted key may be empty". Built: empty quoted keys accepted.
4. Signed zero: PRD FP-02 says "a signed zero is the integer 0" but the error list also refuses "a zero with a sign (`+0`, `-0`)". Built: `+0`/`-0` accepted (TOML 1.1.0 allows them).
5. Carriage returns in multiline basic strings: PRD says line endings are "kept exactly as written, carriage returns included" but also that CRLF is "a single line feed everywhere, including inside string values". Built: CRLF becomes LF; a lone CR is an error.
6. Quote before closing `"""`: PRD says a multiline basic string may end in one or two quote characters, but also lists "a quote character directly before the closing delimiter" as an error. Built: up to two extra quotes accepted; 6 or more consecutive quotes is an error.
7. Contract says hex digits are "written in lowercase" in integer results; ints are plain Python ints, so this has no meaning. Ignored.

## Unstated details (assumptions)
- Invalid UTF-8 bytes in `load` raise `UnicodeDecodeError` (a ValueError), not TOMLDecodeError. A BOM is not stripped.
- A RecursionError from extremely deep nesting is reported as TOMLDecodeError.
- Error offsets are reported against the original text (before CRLF normalization).
- `load` accepts any object whose `read()` returns bytes/bytearray; a `str` result gives TypeError.
- Offset validation: offset hour 0-23, minute 0-59.
