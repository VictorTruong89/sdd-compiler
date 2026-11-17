# Implementation notes

The package is `src/tomlparse` (`loads`, `load`, `TOMLDecodeError`). It is a
hand-written TOML v1.1.0 parser; no other TOML parser is used. Run tests with
`PYTHONPATH=src python -m unittest discover -s tests`.

Each entry below names the two sides of a disagreement, then what was built.
Section references are to `spec/Full_PRD.md` (PRD), `spec/Interface_Contract.md`
(Contract) and `spec/Hardware_Requirements.md` (Hardware).

## Conflicts from `spec/CONFLICTS.md` and the choice made

The reviewer's list is not part of the specification; each item below was
checked against the spec text itself.

### C-01 Omitted seconds in local times
- PRD Terminology "Local time" (line 28): "Its seconds are always written."
- PRD FP-02 "Seconds and fractions" (line 116): seconds "may be omitted, in which
  case the second is 0"; PRD Non-goals (line 64) also accepts omitted seconds.
- **Built:** seconds may be omitted in every time value, including local times
  (`07:32` is `datetime.time(7, 32)`). The FP-02 rule and the Non-goals line agree
  with each other; the Terminology row is the outlier.

### C-02 Rounding of fractional seconds
- PRD FP-02 (line 116): the fraction is read as microseconds, "any digits after
  the sixth are dropped (truncated, not rounded)."
- Contract `loads` return shape (line 46): a local time's fraction is "rounded
  to the nearest microsecond."
- **Built:** truncation, for every time value (`07:32:00.1234567` gives
  microsecond 123456). The PRD states it as a normative rule for any value with a
  fraction and says it explicitly; the Contract mentions rounding only for local
  times. This is a judgment call.

### C-03 Trailing comma in arrays
- PRD FP-01 (line 89): arrays "end with a trailing comma."
- Contract `loads` return shape (line 40): an array whose last element is
  followed by a comma "is refused."
- **Built:** accepted (`[1, 2,]` is `[1, 2]`). TOML permits this, and the Contract
  sentence contradicts the TOML grammar that the PRD defers to.

### C-04 Subclasses returned by `parse_float`
- PRD Terminology (line 29): "Only a result whose type is exactly `dict` or
  exactly `list` is refused."
- PRD FP-05 (line 183), Contract `loads` and `load` Failures tables: a `dict`
  or `list`, "or an instance of a subclass of either," is refused.
- **Built:** `isinstance` check, so subclasses are refused with `ValueError`
  (not `TOMLDecodeError`). Two places agree on this; the Terminology row is the
  outlier.

### C-05 Header sub-table of a table created by dotted keys
- PRD Terminology "Dotted key" (line 23): "A table created by dotted keys cannot
  receive a sub-table through a header."
- PRD FP-01 (line 86): a sub-table "that has not itself been defined may still be
  declared by a header, as TOML v1.1.0 allows."
- **Built:** the FP-01 rule. `fruit.apple.color = "red"` followed by
  `[fruit.apple.texture]` is accepted. Redefining the dotted-key table itself
  with a header (`[fruit.apple]`) is refused, as the TOML spec requires.

### C-06 Empty quoted keys
- Contract `loads` return shape (line 38): keys are `str`, "never empty."
- PRD FP-01 (line 84): "A quoted key may be empty."
- **Built:** `"" = 1` gives the key `""`. Only the quoted form can be empty; a
  bare key is always at least one character.

### C-07 Quote characters before a multiline closing delimiter
- PRD FP-02 (line 111): one or two quotes may sit directly before the closing
  delimiter.
- PRD FP-02 (line 127): refused: "a quote character directly before the closing
  delimiter of a multiline basic string."
- **Built:** the PRD normal rule. `"""a""""` is `a"` and `"""a"""""` is `a""`.
  A run of six or more quotes is refused. Both multiline forms behave the same.

### C-08 Line feed right after a multiline opening delimiter
- PRD FP-02 (line 108): a multiline literal "keeps every character after its
  opening delimiter, including a first line feed."
- PRD FP-02 (line 109): "In both multiline forms a line feed immediately after
  the opening delimiter is discarded."
- **Built:** the first line feed is discarded for both multiline forms, as the
  TOML spec says and as line 109 states. Line 108 is overridden for that point.

### C-09 Raw tab in one-line strings
- PRD FP-02 (line 112): "A tab in a one-line string must be written as backslash-t."
- PRD FP-02 (line 126): refused control characters are those "other than tab."
- **Built:** a raw tab is accepted in every string form (line 126's exception and
  the TOML spec both allow it). The `\t` escape also works.

### C-10 Case of hex digits in `\x`, `\u`, `\U`
- PRD FP-02 (line 112): "Hex digits are case-insensitive."
- PRD FP-02 (line 126): refused: "escape digits written as uppercase letters."
- **Built:** case-insensitive (`"é"` and `"é"` both give `é`).

### C-11 Whitespace after a line-ending backslash
- PRD FP-02 (line 110): the backslash "removes the line ending and all whitespace
  (spaces, tabs, line feeds) up to the next non-whitespace character or the
  closing delimiter."
- PRD FP-02 (line 111): "After a line-ending backslash, the next line's leading
  spaces and tabs are kept."
- **Built:** line 110. Spaces and tabs at the start of the next line are removed.
  Line 111's sentence is read as about text that follows the removed whitespace
  (which the TOML spec also says).

### C-12 Carriage returns in multiline basic strings
- PRD FP-01 (line 92): a CRLF pair is "a single line feed everywhere, including
  inside string values."
- PRD FP-02 (line 109): "Line endings inside a multiline basic string are kept
  exactly as written, carriage returns included."
- **Built:** CRLF folds to LF everywhere, including inside multiline basic
  strings. FP-03 ("a carriage-return/line-feed pair is one line feed") agrees with
  FP-01. A lone CR is still refused as a control character.

### C-13 Signed zero integers
- PRD FP-02 (line 113): "a signed zero is the integer 0."
- PRD FP-02 (line 124): refused: "a zero with a sign (`+0`, `-0`)."
- **Built:** accepted; `+0` and `-0` are the integer `0`.

### C-14 Space separator in offset date-times
- PRD Terminology (line 25): an offset date-time's "date and time are joined by
  `T` or `t`."
- PRD FP-02 (line 115): "The separator between date and time may be `T`, `t`, or a
  space."
- **Built:** a space is accepted as the separator for every date-time kind,
  including offset ones (`1979-05-27 07:32:00Z`). FP-02 is the detailed rule.

## Other things the specification does not state

- **Byte order mark.** Not stated. `loads` and `load` reject a leading U+FEFF,
  since it is not TOML whitespace. `load` decodes with plain `utf-8`, not
  `utf-8-sig`, as FP-03 says.
- **Invalid UTF-8 in `load`.** The spec only covers valid UTF-8. The parser raises
  `TOMLDecodeError` with `doc` set to the bytes decoded with replacement characters,
  and `pos` at the first bad byte.
- **Text-mode detection in `load`.** Detection is by the return type of
  `read()`. The file is read before the `TypeError` is raised, so a text-mode
  file object is consumed.
- **Comments.** Control characters other than tab are refused in comments, as the
  TOML grammar requires. The spec does not mention this.
- **Years.** The year must be 1 to 9999, the range of Python's `date`. Year `0000`
  is refused as an invalid date.
- **Leap seconds.** Second 60 is refused, since `datetime.time` cannot represent it.
- **Offsets.** Offset hours must be 0 to 23 and minutes 0 to 59.
- **Nesting depth.** The spec does not give a limit. A `RecursionError` from
  deep nesting is converted to a `TOMLDecodeError` (`"document is nested too
  deeply"`) so that the spec's "a decode error is not a recursion error" holds for
  the documents the parser cannot handle.
- **Error positions.** The spec fixes the rules for `lineno`, `colno`, and the end
  of document, but not which character a parser reports. Duplicate keys and table
  conflicts report the start of the key or header name. Value errors report the
  start of the token. Unterminated strings, arrays, and inline tables report the
  end of the document. Positions are reported against the original text, so a
  CRLF counts as two characters.
- **Formatted report.** The format is `message (line L, column C)`; the end of
  document form adds `, at end of document`.
- **Float converter.** `parse_float` receives the token text as written, with
  sign and underscores. An exception raised by the converter propagates unchanged.
  Integers, strings, booleans, and date-times never reach the converter.
  The default converter is `float()` on the text with underscores removed.
- **Table-definition kinds.** The parser keeps a record of how each table was
  made (by header, implicitly as a parent, by dotted keys, as an inline table,
  or as an array of tables). These records enforce the TOML rules for reopening
  tables. Implicit tables created by a header may still receive dotted keys in
  the rare case where the TOML grammar allows it.
- **Contract wording.** The Contract's "hexadecimal digits written in lowercase"
  (line 41) is not applied: integer values are plain Python `int`s and have no
  digit case.
- **Packaging.** `pyproject.toml` is a setuptools src-layout build with no
  dependencies. The judge runs no build, so `PYTHONPATH=src` is what makes the
  package importable.
