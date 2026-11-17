# NOTES

Implementation: `src/tomlparse/` (`_parser.py`, re-exported in `__init__.py`). Every checklist id is covered by
the parser/error class/entries, or is a "MUST NOT" constraint (no writer, no CLI, no deps, no stdlib tomllib) satisfied by absence.
Ad-hoc checks were run; no test suite is shipped.

## Spec disagreements (the 20 unsettled conflicts) and what I built
I followed TOML v1.1.0 wherever the two sides disagree.
- CF-000001: Full_PRD FP-02 "may contain one or two of their own quote characters ... directly before the closing delimiter" vs "a quote character directly before the closing delimiter of a multiline basic string" refused. Built: allowed (up to two, TOML rule); three or more in a row close the string, and a run longer than 5 is refused.
- CF-000008: "holds line feeds only" vs "carriage returns included". Built: CRLF is normalised to LF everywhere; a lone CR in a string is refused.
- CF-000009: multiline literal "keeps ... a first line feed" vs a first line feed "discarded in both multiline forms". Built: discarded in both.
- CF-000012: "A table created by dotted keys cannot receive a sub-table through a header" vs "a sub-table ... not itself defined may still be declared by a header". Built: `[a.b]` after dotted keys defined `b` is refused. A deeper sub-table such as `[a.b.c]` is allowed.
- CF-000015: backslash line-ending strips the next line's leading whitespace vs "leading spaces and tabs are kept". Built: stripped (TOML).
- CF-000028 / CF-000035 / CF-000071: "A tab in a one-line string must be written as backslash-t" vs literal strings/raw control chars other than tab allowed. Built: raw tabs are allowed in all string forms.
- CF-000037: hex digits either case vs "written in lowercase". Built: either case accepted; the result is an int, so case does not matter.
- CF-000045 / CF-000069: fraction truncated to 6 digits vs rounded. Built: truncated, for every time-bearing value (local time included).
- CF-000059: array trailing comma allowed vs refused. Built: allowed.
- CF-000062: local time seconds always written vs may be omitted. Built: omitted seconds accepted (TOML 1.1).
- CF-000065: signed zero accepted vs refused. Built: `+0` and `-0` accepted as 0.
- CF-000068: offset date-time separator T/t only vs T, t or space. Built: space also accepted.
- CF-000072: hex escape digits case-insensitive vs uppercase refused. Built: either case accepted.
- CF-000023 / CF-000032 / CF-000073: converter result "exactly dict/list" vs "or a subclass instance". Built: `isinstance(result, (dict, list))` is refused with ValueError.
- CF-000074: empty quoted key allowed vs "keys never empty". Built: `"" = 1` accepted.

## Not stated
- Invalid UTF-8 bytes in `load`: the spec gives no failure kind. Built: TOMLDecodeError (pos 0, doc decoded with replacement chars). A UTF-8 BOM is not stripped.
- `TOMLDecodeError` default args: the constructor has defaults for all three args; the spec only shows required args.
- Offset for errors in CRLF documents: mapped back to the original text. The error `doc` is the original text.
- DEL (0x7f) is treated as a forbidden control character in strings and comments (as in TOML).
- Excessive nesting (RecursionError) is reported as TOMLDecodeError.
- Offset date-time with an offset hour over 23 or minute over 59 is refused.
- Key names like `a.b` implicit by `[a.b.c]` can be defined later by their own header; dotted keys can't write into header-created tables.
