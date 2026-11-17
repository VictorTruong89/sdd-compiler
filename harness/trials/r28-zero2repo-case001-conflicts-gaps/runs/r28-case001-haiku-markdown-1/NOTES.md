# NOTES

Implementation notes for `tomlparse` (TOML v1.1.0 parser, pure Python, `src/tomlparse/`).
Where the specification disagrees with itself, this file records what each side says, where
it says it, and what was built. Where the specification is silent, the assumption is recorded.

Tie-break rule used throughout: the PRD states that the TOML v1.1.0 specification is the
authority for which documents are valid, so when a PRD or Contract statement contradicts
TOML v1.1.0 and a more specific statement agrees with TOML, the TOML-consistent reading was built.

## Spec conflicts and choices

1. **Local time fraction: truncate or round?**
   - `Full_PRD.md` FP-02, "Seconds and fractions": the fraction's first six digits are read as
     microseconds, "any digits after the sixth are dropped (truncated, not rounded)".
   - `Interface_Contract.md`, `loads` "Return shape": local time is "its fraction rounded to the
     nearest microsecond".
   - **Built:** truncation (PRD). The Contract says it states only the "shell" and that behavior
     "is specified in the PRD", and the PRD's wording is explicit.

2. **Trailing comma in arrays.**
   - `Interface_Contract.md`, `loads` "Return shape": "an array whose last element is followed by a
     comma is refused".
   - `Full_PRD.md` FP-01, "Normal behavior": arrays "end with a trailing comma"; the PRD's
     Non-goals say TOML v1.1.0 allows what v1.0.0 forbids; TOML v1.0.0 and v1.1.0 both allow it.
   - **Built:** accepted.

3. **Empty keys.**
   - `Interface_Contract.md`, `loads` "Return shape": keys are "`str`, never empty".
   - `Full_PRD.md` FP-01, "Normal behavior": "A quoted key may be empty".
   - **Built:** `""` is a valid (empty) quoted key. Bare keys cannot be empty.

4. **Signed zero.**
   - `Full_PRD.md` FP-02, "Normal behavior": "optionally signed; a signed zero is the integer 0".
   - `Full_PRD.md` FP-02, "Boundary / error behavior": refused: "a zero with a sign (`+0`, `-0`)".
   - **Built:** `+0` and `-0` are accepted as `0` (matches the normal behavior and TOML v1.1.0).

5. **Case of hex digits in `\u`, `\U`, `\x` escapes.**
   - `Full_PRD.md` FP-02, "Basic-string escapes": "Hex digits are case-insensitive."
   - `Full_PRD.md` FP-02, "Boundary / error behavior": refused: "escape digits written as uppercase
     letters".
   - **Built:** both cases accepted (matches TOML v1.1.0 and the normal behavior).

6. **Quote characters before the closing delimiter of multiline strings.**
   - `Full_PRD.md` FP-02, "Normal behavior": "Both multiline forms may contain one or two of their
     own quote characters next to each other, including directly before the closing delimiter".
   - `Full_PRD.md` FP-02, "Boundary / error behavior": refused: "a quote character directly before
     the closing delimiter of a multiline basic string".
   - **Built:** one or two quotes directly before the closing delimiter are content (e.g.
     `"""x""""` is `x"`). Runs of six or more quotes are refused. The same rule applies to
     multiline literal strings. This follows TOML v1.1.0.

7. **Raw tab inside one-line strings.**
   - `Full_PRD.md` FP-02, "Basic-string escapes": "A tab in a one-line string must be written as
     backslash-t."
   - `Full_PRD.md` FP-02, "Boundary / error behavior": refused: "raw control characters **other
     than tab** inside any string form", which implies a raw tab is allowed.
   - **Built:** raw tab is allowed in all string forms (TOML v1.1.0 allows it).

8. **Date-time separator.**
   - `Full_PRD.md` Terminology: an offset date-time's "date and time are joined by `T` or `t`".
   - `Full_PRD.md` FP-02, "Date-time values": "The separator between date and time may be `T`,
     `t`, or a space."
   - **Built:** `T`, `t` or a space for all date-time kinds (the more specific, later statement, and
     it matches TOML v1.1.0).

9. **Seconds in local times.**
   - `Full_PRD.md` Terminology: a local time's "seconds are always written".
   - `Full_PRD.md` FP-02, "Seconds and fractions": "In any value with a time part, seconds may be
     omitted".
   - **Built:** seconds optional in every time value (TOML v1.1.0 allows this).

10. **Which float-converter results are refused.**
    - `Full_PRD.md` Terminology, "Float converter": "Only a result whose type is exactly `dict` or
      exactly `list` is refused."
    - `Full_PRD.md` FP-05 and `Interface_Contract.md` `parse_float` failures: a result that is a
      `dict` or `list` "(or an instance of a subclass of either)" is refused.
    - **Built:** `isinstance` check, so subclass instances are refused too (two of the three
      statements, including the Contract, say this).

11. **Dotted keys and sub-tables declared by header.**
    - `Full_PRD.md` Terminology, "Dotted key": "A table created by dotted keys cannot receive a
      sub-table through a header."
    - `Full_PRD.md` FP-01, "Normal behavior": "After dotted keys have created a nested table, a
      sub-table of it that has not itself been defined may still be declared by a header."
    - **Built:** the FP-01 rule. A header may not define a table that dotted keys created, but may
      declare a new sub-table under it (the TOML v1.0.0/v1.1.0 `[fruit.apple.texture]` example). The
      Terminology line is read as "cannot be defined through a header".

12. **Integer "hexadecimal digits written in lowercase" (Contract, `loads` "Return shape").**
    - A Python `int` has no spelling, so this statement has no observable effect on parsed values.
    - **Built:** nothing special. Hex digits in the document may be either case (PRD FP-02).

13. **Float converter: call timing and errors.** Not stated anywhere. **Assumed:** the converter
    is called as each float token is parsed, so an illegal result raises the `ValueError`
    immediately, and an exception raised by the converter propagates unchanged.

## Gaps the specification does not cover (assumptions made)

- **Control characters in comments.** The PRD does not mention them. TOML v1.1.0 forbids control
  characters other than tab in comments, so the parser refuses them (including DEL, U+007F).
- **DEL (U+007F)** is refused in strings and comments, following TOML v1.1.0.
- **Bare carriage return** outside a CRLF pair is refused everywhere (it is not a line ending).
- **Bare keys** are ASCII only (`A-Za-z0-9_-`), as the PRD's "Latin letters" reads.
- **Byte-order mark.** The UTF-8 BOM is not stripped; a leading U+FEFF is an unexpected
  character and is refused. The PRD says only "decodes the bytes as UTF-8".
- **Invalid UTF-8 in `load`.** Not specified. Raised as `TOMLDecodeError`, with `doc` set to the
  text decoded with U+FFFD replacement characters and `pos` at the first bad byte's character
  offset. (It is a `ValueError`, not a `TypeError`.)
- **`load` input checks.** A text-mode file (`io.TextIOBase`, including `io.StringIO`) is refused
  with `TypeError` before reading. A `read()` that returns `str` is also refused with `TypeError`.
  An object with no `read()` gets `TypeError`. `loads` accepts `str` subclasses.
- **Dates.** Year `0000` is refused (Python's `datetime` cannot represent it, and the PRD asks for
  real calendar dates). Leap second `:60` is refused (the PRD says seconds are 0-59).
- **UTC offsets.** Hours must be 0-23 and minutes 0-59. `Z`/`z` gives `datetime.timezone.utc`;
  a numeric offset gives a fixed `datetime.timezone`. `-00:00` is an ordinary zero offset.
- **Table redefinition through dotted keys.** Dotted keys that walk through an *implicit* table
  (one created only as a parent of a header) convert it to a dotted-defined table, so a later
  header cannot define it. This is the reading of "defined by dotted keys". Dotted keys walking
  through header-defined, inline, or array-of-tables values are refused.
- **Error positions.** Duplicate keys are reported at the key's first character. Table-redefinition
  errors are reported at the header's name. A single-line string that hits a line break is reported at the
  line break; a string that runs to end-of-document is reported at its opening quote.
- **Very long decimal integers.** Digits are converted in chunks, so the Python 3.11+ int-from-str
  digit limit does not reject them.
- **Escapes.** `\xHH` inserts the code point U+00HH (0x00-0xFF). `\uXXXX` and `\UXXXXXXXX` reject
  surrogates (U+D800-U+DFFF) and values above U+10FFFF.
- **Array-of-tables element identity.** Keys are looked up by table identity (`id`) bookkeeping
  during one parse; the parser keeps no state between calls.
- **Error text.** Wording of messages is free (PRD FP-04). `TOMLDecodeError` exposes `msg`, `doc`,
  `pos`, `lineno` and `colno`, and its pickle round-trip rebuilds it from `(msg, doc, pos)`.

## Not done / out of scope

- No writer, no CLI, no comment preservation (PRD Non-goals).
- The stdlib `tomllib` is not used anywhere in the product (PRD "Real parser").
- Performance is not tuned (PRD: speed is a design goal, not a requirement).
- `tests/test_tomlparse.py` is a unittest suite I wrote from the spec. It is not the hidden
  acceptance suite. Run it with `PYTHONPATH=src python3 -m unittest tests.test_tomlparse`.
