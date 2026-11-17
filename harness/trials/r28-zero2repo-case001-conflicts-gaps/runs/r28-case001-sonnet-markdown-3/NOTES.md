# Notes

## Spec disagreements
- Trailing comma in arrays: Interface_Contract ("an array whose last element is followed by a comma is refused") vs Full_PRD FP-01 ("may ... end with a trailing comma", TOML 1.1). Built: accepted.
- Local time fraction: Interface_Contract says "rounded to the nearest microsecond"; PRD FP-02 says truncated after six digits. Built: truncation.
- Empty keys: Contract says keys are "never empty"; PRD FP-01 says a quoted key may be empty. Built: empty quoted keys accepted.
- Signed zero: PRD FP-02 normal behavior says signed zero is integer 0; the error list says `+0`/`-0` are refused. Built: accepted (TOML 1.1).
- Quotes before a multiline basic closing delimiter: PRD says both multiline forms may end with 1-2 quote characters, but the error list refuses "a quote character directly before the closing delimiter". Built: 1-2 quotes before the delimiter are content; a run of 6+ quotes is an error.
- CRLF in multiline basic strings: PRD says CRLF becomes LF everywhere, but also "line endings kept exactly as written, carriage returns included". Built: CRLF normalized to LF; a lone CR is an error. Error offsets are mapped back to the original text.

## Unstated
- Invalid UTF-8 in `load`: raises TOMLDecodeError (doc = lossy-decoded text, pos = bad byte offset).
- Nesting deep enough to cause RecursionError is reported as TOMLDecodeError (pos 0).
- Float converter is invoked with the token text; a dict/list result raises ValueError.
