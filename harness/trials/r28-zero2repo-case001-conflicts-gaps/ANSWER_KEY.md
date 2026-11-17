# Answer key: 15 conflicts and 4 gaps planted in case001, round 28 (never shown to an agent)

> Written 2026-11-11, after the step-1 checks and before any compile output, review or agent run was read.
> The planted Markdown is made by `notes/plant.py work/spec-planted` with the 19 kept ids (`KEPT_C`,
> `KEPT_G` in the script) from Zero2Repo case001's `public/` (`tomlparse`, upstream `tomli`); it stays in
> git-ignored `work/` (Zero2Repo has no licence file). 4 801 words (4 860 before). sha256 of the planted
> files (`work/spec-planted.sha256`): `Full_PRD.md` `7c54ee5a2071f268…`, `Interface_Contract.md`
> `6c80c56b8be548e6…`, `Hardware_Requirements.md` `d81c020a5fd13c16…` (unchanged). Only short phrases are
> quoted here.

Side **A** is the text the case already had: the reference library's behaviour and what the hidden
tests check. Side **B** is the planted sentence: one place edited, in the spec's voice, no marker. A
**gap** removes every statement of a fact the hidden tests still check. Lines are those of the planted
files (PRD = `Full_PRD.md`, Contract = `Interface_Contract.md`).

**Why only 4 gaps.** The PRD makes the published TOML v1.1.0 specification "the authority for the grammar
and for which documents are valid". A TOML grammar fact removed from the PRD therefore stays stated by
reference, so gap candidates were limited to product facts TOML does not fix: failure location, the float
converter, nesting depth and UTF-8 handling (6 candidates; 4 kept). Conflicts are unaffected: each side A
is stated in the PRD's own words. Set 2b for this case is over 4 gaps and is reported with that caveat.

## Conflicts (15)

| Item | Distance | A (kept) | B (planted) | Footprint |
|---|---|---|---|---|
| C03 | same file, far | PRD 116: "In any value with a time part, seconds may be omitted" | PRD 28 (Terminology, Local time): "Its seconds are always written" | 2 |
| C04 | across files | PRD 116: fraction digits after the sixth "dropped (truncated, not rounded)" | Contract 46: local time "its fraction rounded to the nearest microsecond" | 1 |
| C07 | across files | PRD 89: arrays may "contain comments between elements, and end with a trailing comma" | Contract 40: "an array whose last element is followed by a comma is refused" | 3 |
| C08 | same file | PRD 113: "(optionally signed; a signed zero is the integer 0)" | PRD 124 (refused scalars): "a zero with a sign (`+0`, `-0`)" | 1 |
| C10 | same file | PRD 92: a multiline string with CRLF line endings "holds line feeds only" (also FP-03) | PRD 109: multiline basic line endings "kept exactly as written, carriage returns included" | 1 |
| C11 | same file | PRD 109: "In both multiline forms a line feed immediately after the opening delimiter is discarded" | PRD 108: a multiline literal string keeps every character, "including a first line feed" | 3 |
| C12 | same file | PRD 110: a line-ending backslash "removes the line ending and all whitespace (spaces, tabs, line feeds)" | PRD 111: "the next line's leading spaces and tabs are kept" | 2 |
| C13 | same file | PRD 111: one or two quote characters allowed, "including directly before the closing delimiter" | PRD 127 (refused): "a quote character directly before the closing delimiter of a multiline basic string" | 1 |
| C14 | same file | PRD 127: refused are "raw control characters other than tab inside any string form" | PRD 112: "A tab in a one-line string must be written as backslash-t" | 3 |
| C16 | across files | PRD 113: integers — "hex digits may be either case" | Contract 41: "hexadecimal digits written in lowercase" | 2 |
| C17 | same file | PRD 112: escapes — "Hex digits are case-insensitive" | PRD 126 (refused): "escape digits written as uppercase letters" | 2 |
| C18 | same file, far | PRD 115: "The separator between date and time may be `T`, `t`, or a space" | PRD 25 (Terminology, Offset date-time): "Its date and time are joined by `T` or `t`" | 3 |
| C29 | same file, far (and Contract) | PRD 179: a converter result that is a dict or list "(and not an instance of a subclass of either)" is refused (also PRD 185, Contract) | PRD 29 (Terminology, Float converter): "Only a result whose type is exactly `dict` or exactly `list` is refused" | 1 |
| C35 | across files | PRD 84: "A quoted key may be empty" | Contract 38: "keys: `str`, never empty" | 2 |
| C36 | same file, far | PRD 86: a sub-table of a table made by dotted keys "may still be declared by a header" | PRD 23 (Terminology, Dotted key): "A table created by dotted keys cannot receive a sub-table through a header" | 2 |

## Gaps (4)

| Item | Fact removed (upstream value) | Removed from | Alternative probed | Footprint |
|---|---|---|---|---|
| G01 | a document that ends where more input is required fails at offset = the document's length | PRD FP-04 (location bullet, one sentence) | the index of the last character | 2 |
| G03 | a conflicting table or array-of-tables header fails at a character within that header | PRD FP-04 (whole bullet) | the offset after the header | 1 |
| G09 | arrays nested 470 deep, inline tables 310 deep and 310-part dotted keys parse | PRD FP-01 boundary (whole bullet) | a guard refusing arrays nested deeper than 100 | 2 |
| G13 | bytes that are not valid UTF-8 fail and are never reinterpreted in another encoding | PRD FP-03 (whole bullet); Contract (`load` failure row) | Latin-1 fallback | 3 |

**Still implied, recorded before any run.** G01: the formatted-report sentences still mention "an offset at
or past the end" (PRD FP-04 and the Contract), which implies such offsets exist without fixing the value;
kept. G13: FP-03 still says the entry "decodes the bytes as UTF-8", and FP-03's next bullet begins "When the
bytes are valid UTF-8 …"; a strict decode follows from the first reading, a fallback from neither; kept.

**Footprint union: 37 tests, none shared by two items; the base build fails none.** The **core** (set 1)
is the other **265** of 302 tests. Distances: same file 11 (C03, C08, C10, C11, C12, C13, C14, C17, C18,
C29, C36; far: C03, C18, C29, C36), across files 4 (C04, C07, C16, C35).

## Candidates tried and dropped (step 1, no model call)

| Item | Behaviour | Why dropped |
|---|---|---|
| C01 | `\e` refused | footprint 5 |
| C02 | `\x` refused | footprint 10 |
| C05 | inline-table trailing comma refused | footprint 7 |
| C06 | line feed in an inline table refused | footprint 5 |
| C09 | `+nan` / `-nan` refused | footprint 4 |
| C15 | underscores in prefixed integers refused | footprint 5 |
| C19 | lowercase `z` refused | shares `datetime_separator_T_t_space_same_instant` with C18 (tie, same kind; the later id dropped) |
| C23 | end offset = last character | same fact as G01; the gap kept (gaps are scarce in this case) |
| C25 | 0-based `colno` | footprint 20 |
| C27 | specials not passed to the converter | same fact as G05; G05 kept as the candidate |
| C28 | converter tuple refused | footprint 4 |
| C31 | arrays deeper than 100 refused | same fact as G09; made G09's alternative (the default recursion limit does not fail at depth 470, so that first alternative read A) |
| G04 | converter text without underscores | footprint 0 |
| G05 | specials not passed to the converter | footprint 4 |

## How each side is read (`notes/probe.py`, black box, from this key and the Contract only)

One probe per item on the saved code, in a container with no network (`notes/probe.sh`). Check
(`work/probe_check.log`): the base reads A on all 30 final candidates; each alternative copy reads B on
its own item and A on the others (0 mismatches; first pass: 4 mismatches, all from two pairs of candidates
that were the same fact, C23/G01 and C31/G09, resolved as in the table above; the C04 probe was changed to
a fraction that rounding and truncation tell apart).
