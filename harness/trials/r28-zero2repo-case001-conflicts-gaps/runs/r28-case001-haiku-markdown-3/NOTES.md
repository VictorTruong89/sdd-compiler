# Implementation notes

Tomlparse 2.4.0 is a pure-Python TOML v1.1.0 parser in `src/tomlparse/`
(`__init__.py` exports `loads`, `load`, `TOMLDecodeError`; the parser is
`_parser.py`, the exception is `_errors.py`). Unit tests are in
`tests/test_tomlparse.py`; run them from `/app` with
`PYTHONPATH=src python3 -m unittest tests.test_tomlparse`.

Spec files are referred to as: PRD = `spec/Full_PRD.md`, Contract =
`spec/Interface_Contract.md`, HW = `spec/Hardware_Requirements.md`. Line
numbers are from those files.

## Conflicts between the specification documents

Each entry gives what each side says, then what the code does.

1. **Seconds in local times.** PRD Terminology (line 28): "Local time ... Its
   seconds are always written." PRD FP-02 (line 116): "In any value with a
   time part, seconds may be omitted", and PRD Non-goals (line 64) accepts
   "date-times whose seconds are omitted". **Built:** seconds may be omitted
   (second = 0), as TOML v1.1.0 allows.

2. **Fractional seconds in local times.** Contract, return shape (line 46):
   "local time: ... its fraction rounded to the nearest microsecond." PRD FP-02
   (line 116): fractions are "truncated, not rounded". **Built:** truncated
   (the PRD gives the detailed rule). The same truncation applies to offset
   date-times and local date-times.

3. **Trailing comma in arrays.** Contract (line 40): "an array whose last
   element is followed by a comma is refused." PRD FP-01 (line 89): arrays
   "end with a trailing comma" (accepted), and TOML allows it. **Built:**
   accepted.

4. **Signed zero.** PRD FP-02 Normal behavior (line 113): "a signed zero is the
   integer 0". PRD FP-02 Boundary (line 124): "a zero with a sign (`+0`, `-0`)"
   is refused. These contradict each other inside the PRD. **Built:** `+0`
   and `-0` are accepted as the integer 0, following the Normal behavior and
   TOML.

5. **Quote characters before the closing delimiter of a multiline string.**
   PRD FP-02 Normal behavior (line 111): one or two quote characters "including
   directly before the closing delimiter" are allowed. PRD FP-02 Boundary (line
   127) refuses "a quote character directly before the closing delimiter of a
   multiline basic string". **Built:** runs of 3 to 5 quotes at the end close
   the string and keep 0 to 2 quotes in the value (TOML behavior). Runs of 6 or
   more quotes are refused. This applies to both multiline forms.

6. **Converter results that are subclasses of dict or list.** PRD Terminology
   (line 29): "Only a result whose type is exactly `dict` or exactly `list` is
   refused." PRD FP-05 (line 183) and Contract (line 56): dict and list
   subclass instances are refused too. **Built:** `isinstance` check, so
   subclasses are refused with a plain `ValueError`.

7. **Sub-tables under tables made by dotted keys.** PRD Terminology (line 23):
   "A table created by dotted keys cannot receive a sub-table through a
   header." PRD FP-01 (line 86): a sub-table of a dotted-key table that has
   not been defined itself "may still be declared by a header". **Built:**
   the FP-01 rule, which matches the TOML example
   `[fruit.apple.texture]` after `apple.color = ...`. A header cannot name a
   dotted-key table itself (`[fruit.apple]` is refused).

8. **Separator in date-times.** PRD Terminology (line 25): offset date-times
   are "joined by `T` or `t`". PRD FP-02 (line 115): the separator "may be `T`,
   `t`, or a space". **Built:** all three are accepted, for every date-time
   kind.

9. **Lowercase hexadecimal digits.** Contract line 41 says integers have
   "hexadecimal digits written in lowercase". A Python `int` has no digit
   spelling, so this cannot apply to the returned values. **Built:** plain
   `int` values; the spelling of the source document does not matter.

## Points the specification does not state

- **Control characters in comments.** Only "non-ASCII text is allowed in
  comments" is stated. **Assumed:** TOML's rule applies. A control character
  other than tab, a lone carriage return, or DEL (U+007F) in a comment is
  refused.
- **DEL (U+007F).** Not stated for strings either. **Assumed:** it is a
  control character and is refused in every string form.
- **Byte-order mark.** Not stated. **Assumed:** a leading U+FEFF is refused
  (it cannot start a key or value).
- **Invalid UTF-8 in `load`.** The PRD says the bytes are decoded as UTF-8 but
  does not say what happens on failure. **Built:** `TOMLDecodeError` whose `doc`
  is the text decoded with `errors="replace"`, and whose `pos` is the
  character index of the first invalid byte in that text.
- **Year 0000.** Not stated. Python's `date` starts at year 1, so `0000-…`
  dates are refused as out-of-range dates.
- **Leap seconds.** PRD FP-02 (line 128) limits seconds to 0 to 59. **Built:**
  `:60` is refused, as the PRD says.
- **Dotted keys into implicit tables.** A table that exists only because a
  header implied it (for example, `b` in `[a.b.c]`) can receive dotted keys
  when a later `[a]` body writes `b.x = 1`. The specification's rule covers
  only tables defined by a `[table]` header. **Assumed:** allowed. A table
  defined by a header, or by dotted keys, cannot be extended by dotted keys.
- **Error positions.** The specification fixes only the offset rules. For an
  unterminated string, the offset is the end of the document or the offending
  character. For duplicate keys and tables, it is the key or header start.
- **Escapes.** `\xHH` accepts any two hex digits (00 to FF), which is the same
  as the PRD's rule. Bare keys use ASCII letters, digits, `_`, and `-`.
- **Surrogate code points in Python `str` input** are not checked. The string
  parser accepts them; the input is not required to be valid Unicode.
- **Nesting depth.** The parser is recursive, so nesting is limited by the
  Python recursion limit. Nesting of 400 levels parses. Deeper nesting raises
  `RecursionError`, which is not a `TOMLDecodeError`.
- **`parse_float` validation.** `loads` and `load` raise `TypeError` if
  `parse_float` is not callable, even when the document has no floats.
- **`load` reads the whole file.** It calls `read()` once. For a text-mode file
  the text is read first and then refused, so the file position moves.

## Verification

- Unit tests (`tests/test_tomlparse.py`): 39 tests covering scalars, strings,
  integers, floats, date-times, structure, invalid documents, error locations,
  `load`, and `parse_float`. All pass on Python 3.13.
- Differential check: results match the standard library's `tomllib` on 22
  documents (valid and invalid) that are also valid TOML 1.0. This was a
  scratch check outside the repository. The product does not use `tomllib`.
- Not tested: Python 3.8 through 3.12, PyPy, macOS, and Windows. The code avoids
  syntax newer than 3.8 but has not been run on those versions.
