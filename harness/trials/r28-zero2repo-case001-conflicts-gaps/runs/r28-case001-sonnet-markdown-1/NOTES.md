# Notes

## Spec disagreements (and what was built)
- Trailing comma in arrays: Interface_Contract ("an array whose last element is followed by a comma is refused") vs Full_PRD FP-01 ("may ... end with a trailing comma") and TOML v1.1.0. Built: trailing comma accepted.
- Local time fraction: Interface_Contract says "fraction rounded to the nearest microsecond"; PRD FP-02 says digits after the sixth are truncated. Built: truncation.
- Empty keys: Contract says keys are "never empty"; PRD FP-01 says a quoted key may be empty. Built: empty quoted keys accepted.
- Multiline literal first newline: PRD FP-02 says both multiline forms discard a first line feed, but another bullet says a multiline literal "keeps ... including a first line feed". Built: discarded (TOML 1.1.0).
- Tab in one-line strings: PRD FP-02 says a tab "must be written as backslash-t", but also lists tab as allowed among control characters and TOML allows a raw tab. Built: raw tab accepted.
- Quote before closing delimiter of multiline basic: PRD lists it as an error but also allows 1-2 quotes before the closing delimiter. Built: TOML rules (up to 2 extra quotes accepted; 3+ extra refused).
- Converter result check: PRD terminology says only exact `dict`/`list` is refused; FP-05 and Contract say subclasses too. Built: isinstance check (subclasses refused).
- Seconds 60 are refused (PRD: second 0-59).

## Unstated assumptions
- CRLF is normalized to LF before parsing, so `TOMLDecodeError.doc`/`pos` refer to the normalized text.
- Invalid UTF-8 in `load` raises `TOMLDecodeError` (pos = byte offset of bad byte, doc decoded with replacement).
- Excessive nesting (RecursionError) is reported as `TOMLDecodeError`.
- `load` accepts any object whose `read()` returns bytes; one returning `str` gives `TypeError`.
