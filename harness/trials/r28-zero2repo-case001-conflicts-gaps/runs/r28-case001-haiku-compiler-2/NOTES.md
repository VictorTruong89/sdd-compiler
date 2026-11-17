# Tomlparse — implementation notes

Pure-Python TOML v1.1.0 parser, built from `spec/` (export of `sdd/specs/*`, compiled with `--allow-open`).

- Package: `src/tomlparse/` (src layout). Public names: `loads`, `load`, `TOMLDecodeError`.
- Internal layout (N-000273): `_errors.py` (decode error), `_parser.py` (grammar, scalars, redefinition rules), `api.py` (`loads`/`load`), `__init__.py`.
- Build metadata: `pyproject.toml` (setuptools PEP 517 backend, `requires-python >= 3.8`, no dependencies).
- Tests: `tests/test_tomlparse.py` (pytest). Run: `cd /app && PYTHONPATH=src python -m pytest tests`. Result at time of writing: 157 passed.
- Verified on: Python 3.13 (pytest), Python 3.11 (smoke run). Python 3.8 is covered only by an `ast.parse(..., feature_version=(3, 8))` syntax check; no 3.8 interpreter was available. Not run on macOS or Windows.
- Not verified: `pip wheel` / editable install. `setuptools` is not installed in this environment and the sandbox has no network, so the PEP 517 build could not be run.

## 1. Specification conflicts and what was built

The export reports 16 unsettled contradictions (`CF-…`). Each is listed below with the two sides and the choice. Where I found a contradiction that the export did not report, it is marked **(not flagged by export)**.

For TOML-grammar questions, pack 06 (product overview) names TOML v1.1.0 as the authority for the grammar and for which documents are valid. I used the TOML rule when the product text was otherwise silent.

| Id | Side A (location) | Side B (location) | Built |
|---|---|---|---|
| CF-000001 | Quote before a multiline closing delimiter allowed: N-000135 (pack 12, FP-02 strings) | Quote directly before the closing delimiter of a multiline basic string refused: N-000178 (pack 12, FP-02 boundary) | **Allowed** (one or two quotes, for either multiline form). Three to five quotes at the end close the string; six or more are refused. TOML grammar allows this. |
| CF-000008 | CR LF inside a multiline string holds line feeds only: N-000112 (pack 12, FP-01, stated "everywhere, including inside string values") | Line endings kept as written, carriage returns included: N-000133 (pack 12, FP-02) | **LF only.** Every CR LF pair is read as one LF before parsing, so no CR survives in a string. A lone CR is still refused. |
| CF-000009 | Multiline literal keeps every character after the opening delimiter, "including a first line feed": N-000130 | LF right after the opening delimiter is discarded in both multiline forms: N-000131 | **Discarded** for both multiline forms (TOML grammar). |
| CF-000012 | Table created by dotted keys cannot receive a sub-table through a header: N-000021 (pack 07) | A sub-table of it not yet defined may be declared by a header: N-000098 (pack 12) | **Both hold.** A dotted-key table cannot itself be defined by a header (`[a]` after `a.b = 1` is refused), but `[a.b.c]` may create a new sub-table below it. This is the TOML 1.x example reading. |
| CF-000015 | Line-ending backslash removes the next line's leading whitespace: N-000134 | "The next line's leading spaces and tabs are kept": N-000136 | **Removed** (TOML grammar, and N-000134 is the more specific rule). |
| CF-000023, CF-000032 | Only results of exactly type `dict` or `list` are refused: N-000029 (pack 07, Terms) | Converter results that are `dict`/`list` or subclass instances are refused: N-000296 (pack 03), N-000232 (pack 12), N-000038 (pack 08) | **Subclasses are refused too** (`isinstance` check). Three claims state the subclass rule; only the glossary states the exact-type rule. |
| CF-000028, CF-000035 | Tab in a one-line string must be written as `\t`: N-000143 (pack 12) | Raw tab allowed; only other control characters refused: N-000178 (pack 12); escapes never processed in literal strings: N-000129 | **Raw tab allowed** in every one-line string, literal ones included (TOML grammar). `\t` still works in basic strings. |
| CF-000037 | Hex digits may be either case: N-000146 (integers) | Hexadecimal digits written in lowercase: N-000285 (pack 03, return shape) | **Input accepts either case.** The `0x`/`0o`/`0b` prefix is lowercase only (N-000145). The result is an `int`, so digit case is not observable in the output. |
| CF-000045, CF-000069 | Fraction's first six digits read as microseconds; later digits truncated: N-000156, N-000157 (pack 12, FP-02) | Fraction "rounded to the nearest microsecond": N-000292 (pack 03, return shape) | **Truncated** (FP-02 is the more specific rule and states "not rounded" explicitly). |
| CF-000059 | Arrays may end with a trailing comma: N-000106 (pack 12) | An array whose last element is followed by a comma is refused: N-000282 (pack 03) | **Accepted** (trailing comma allowed; TOML grammar). `[,]` and `[1,,2]` are refused. |
| CF-000062 | Local time seconds always written: N-000028 (pack 07) | Seconds may be omitted in any value with a time part: N-000154 (pack 12) | **Seconds optional** for local times and date-times. Non-goals (N-000069–N-000071) name omitted seconds as a v1.1 feature. |
| CF-000065 | Signed zero is the integer 0: N-000144 (pack 12, FP-02, normal) | A zero with a sign (`+0`, `-0`) refused: N-000168 (pack 12, FP-02, boundary) | **Accepted** as 0 (TOML grammar allows `+0`, `-0`). |
| CF-000068 | Offset date-time joined by `T` or `t`: N-000024 (pack 07) | Separator may be `T`, `t` or a space: N-000153 (pack 12) | **All three separators** accepted for every date-time kind (TOML allows a space). |
| (not flagged by export) | "Hex digits are case-insensitive" for escapes: N-000139 (pack 12, FP-02) | "escape digits written as uppercase letters" refused: N-000177 (pack 12, FP-02 boundary) | **Uppercase escape digits accepted** (`\u00E9` and `\u00e9` both valid). N-000139 is the normal-behaviour rule and the TOML `HEXDIG` rule is case-insensitive. |
| (not flagged by export) | "keys: str, never empty": N-000279 (pack 03, return shape) | A quoted key "may be empty": N-000090 (pack 12, FP-01) | **Empty quoted keys allowed** (`"" = 1` gives `{"": 1}`). N-000090 is the specific rule and TOML allows empty quoted keys. |

Additional conflict noted but not a contradiction in practice: the text "Behaviors that exist only in older Tomlparse releases … text-mode file objects as parse input are not this product" (N-000050) agrees with the refusal of text-mode files (N-000190). No action needed.

## 2. Things the specification does not state (assumptions)

- **Empty document / whitespace / comment only** → `{}`, with or without a final line feed.
- **Byte-order mark**: not stripped. A leading U+FEFF is an invalid character and raises `TOMLDecodeError`.
- **Invalid UTF-8 in `load`**: not specified. Raised as `TOMLDecodeError` with message "invalid UTF-8 byte sequence"; `doc` is the text decoded with replacement characters and `pos` is the offset of the first invalid byte in that text.
- **`load` input detection**: refused up front if the object is an `io.TextIOBase`. A `read()` that returns `str` is also refused with `TypeError`. A path string has no `read()` and is refused with `TypeError`.
- **`load` reads the whole stream** with `read()` and does not seek.
- **Date range**: years 0000 are refused (Python's `date` starts at year 1). Leap second `:60` is refused (N-000180 says seconds 0–59).
- **UTC offsets**: hours 00–23 and minutes 00–59. `+24:00` is refused.
- **Fractions**: any number of fraction digits is accepted; only the first six are kept.
- **Control characters in comments** are refused (TOML grammar; the spec says only that comments may hold non-ASCII text, N-000109). DEL (U+007F) is refused everywhere outside strings as well.
- **Escapes**: `\u0000` and other control-code escapes produce the character; no restriction beyond scalar-value validity.
- **Large integers**: decimal literals longer than Python's `int()` digit limit are converted in chunks, so every valid TOML integer is exact.
- **Converter (`parse_float`)**: called as `parse_float(text)` with the characters as written (underscores included, e.g. `1_0.5e+2`). Exceptions it raises propagate unchanged. Its return value is not inspected other than the dict/list check. Non-callable `parse_float` raises `TypeError`.
- **Inline tables** are frozen after their closing brace. Dotted keys may still extend a super-table created implicitly by a header (for example `[a.b.c]` followed by `[a]` then `b.d = 1`), since the spec does not forbid it and the table was not defined by a header.
- **Nesting depth**: the parser is recursive, so nesting deeper than about a few hundred levels raises Python's `RecursionError`. This is not a `TOMLDecodeError` (the spec forbids that conversion, N-000308). Documented here as a known limit.
- **Error location for CR LF input**: `doc` is the caller's original text and `pos` is an offset into it, so `doc[pos]` is the character that failed.
- **Message wording** is free (N-000053, N-000298, N-000323). Messages are short and include the location.
- **`__version__ = "2.4.0"`** and the matching `pyproject.toml` version. The spec says "2.4.0 and later"; the package reports the first compatible version.
- **Extra dunders**: `TOMLDecodeError.__reduce__` (so the error pickles from its three constructor arguments) and `__module__ = "tomlparse"`. These are not new public names.

## 3. Checklist coverage (all 323 ids)

Status key: **I** = implemented; **T** = implemented and exercised by a test in `tests/test_tomlparse.py`; **D** = decided (conflict resolved in section 1, see the table; the claim it conflicts with is not built); **N/A** = documentation or process constraint with no code; **C** = satisfied by construction and not run here (see notes).

Exact sentence-to-id correspondence inside a bullet is taken from the pack's `Related`/`Claims` lists; where the pack does not say which claim a sentence is, the whole bullet's ids are listed together. The code markers `# spec: N-…` in `src/tomlparse/` point to the functions that carry each id.

### Pack 01 — Interface Contract, product overview (N-000255–N-000265)
- 255–257 parser only, no writer, comments not preserved — **T** (`test_no_write_or_cli_surface`, `test_comments_never_become_values_and_allow_non_ascii`).
- 258 TOML v1.1.0 grammar — **T** (`_parser.py`; tests across FP-01/FP-02).
- 259 entries return or raise, no print/file/env — **T** (`test_parse_entries_print_nothing_and_leave_environment_alone`).
- 260–261 no dump, no CLI, no `python -m` — **T** (`test_no_write_or_cli_surface`).
- 262 pure Python, zero runtime dependencies — **T** (`test_package_has_version_and_no_third_party_imports`).
- 263 Python 3.8+ — **C** (ast feature-version check; run on 3.11 and 3.13).
- 264 Linux, macOS, Windows — **C** (no OS-specific code; only Linux run).
- 265 CPU-only — **I** (no accelerator code).

### Pack 02 — public surface (N-000266–N-000273)
- 266 src-layout package `tomlparse` — **I** (`src/tomlparse/`, `pyproject.toml`).
- 267 default path has no compiled extensions — **I**.
- 268 importing performs no I/O, starts no process, opens no socket — **I** (`__init__.py` imports only internal modules).
- 269 MUST NOT start processes or sockets — **I** (no such imports; checked by the import test).
- 270 names importable from the root — **T** (`test_public_names_importable_from_root`).
- 271 `loads` — **T**. 272 `load` — **T**.
- 273 internal layout is the implementer's choice (decision) — **D** (`_errors`, `_parser`, `api`).

### Pack 03 — `tomlparse.loads` (N-000274–N-000298)
- 274 positional `s` — **T**. 275 keyword-only `parse_float` (MAY) — **T** (`test_loads_parse_float_is_keyword_only`).
- 276 converter receives the float's text — **T** (`test_converter_called_with_text_everywhere_for_floats_only`).
- 277 default is builtin float — **T** (`test_floats_default_and_special`).
- 278 success returns a dict, never None — **T**.
- 279 keys are `str`, never empty — **D** (empty quoted keys allowed; table in section 1).
- 280 tables and inline tables are dicts with `str` keys — **T**.
- 281 arrays are lists in document order — **T**.
- 282 trailing comma after last element refused — **D** (CF-000059: accepted instead; `test_arrays_mixed_nested_multiline_trailing_comma_comments`).
- 283 strings are `str` — **T**. 284 integers are `int`, never `bool` — **T** (`test_integers_all_bases`).
- 285 hex digits written lowercase — **D** (CF-000037: input either case; output is `int`).
- 286 booleans are `bool` — **T** (`test_booleans`).
- 287 floats are `float` or the converter's value — **T**.
- 288 offset date-time is tz-aware with the written offset — **T** (`test_offset_date_times_utc_and_numeric`).
- 289 local date-time is naive — **T**. 290 local date is `date` — **T**.
- 291 local time is naive `time` — **T** (`test_local_time_naive_and_fraction_truncated`).
- 292 fraction rounded to nearest microsecond — **D** (CF-000045/069: truncated).
- 293 empty document → empty dict — **T** (`test_empty_and_comment_only_documents`).
- 294 non-`str` input → `TypeError` — **T** (`test_loads_refuses_non_text_with_type_error`).
- 295 invalid TOML → `TOMLDecodeError` — **T** (`test_structural_conflicts_are_refused` and the scalar tests).
- 296 converter returns dict/list (or subclass) → `ValueError`, not decode error — **T** (`test_value_error_from_parse_float_is_not_decode_error`).
- 297 no mapping returned on failure — **T** (exceptions raised, no partial result).
- 298 message wording is the implementer's choice — **N/A** (decision; wording is free).

### Pack 04 — `tomlparse.load` (N-000299–N-000306)
- 299 accepts a binary file object — **T** (`test_load_from_binary_buffer_equals_loads`, `test_load_reads_disk_binary_file`).
- 300 reads contents; never takes a path — **T** (`test_load_takes_a_file_object_never_a_path`).
- 301 `parse_float` as for `loads` — **T** (`test_load_parse_float_applies_like_loads`).
- 302 same dict form as `loads` — **T**. 303 no bytes → empty dict — **T** (`test_load_empty_file_yields_empty_dict`).
- 304 text-mode file → `TypeError` — **T** (`test_load_refuses_text_mode_file_whatever_it_holds`).
- 305 decode error `doc` is decoded text — **T** (`test_load_decode_error_carries_decoded_text_and_position`).
- 306 converter dict/list → `ValueError` — **T**.

### Pack 05 — `tomlparse.TOMLDecodeError` (N-000307–N-000323)
- 307 `ValueError` subclass — **T** (`test_decode_error_is_value_error_only`).
- 308 not a subclass of `TypeError` or `RecursionError` — **T** (same test).
- 309–313 constructor `(msg, doc, pos)`; parse entries raise instances built the same way — **T** (`test_decode_error_constructor_and_attributes`, `test_caller_constructed_error_matches_rules`).
- 314–319 attributes `msg`, `doc`, `pos`, `lineno`, `colno` on every instance — **T**.
- 320 `str(err)` contains reason and location — **T**.
- 321 interior offset → line and column in report — **T** (`test_decode_error_location_for_interior_offset`).
- 322 offset at or past end → mention of end of document — **T** (`test_decode_error_end_of_document_report`, `test_decode_error_location_for_end_offset`).
- 323 report wording is the implementer's choice (decision) — **N/A**.

### Pack 06 — Full PRD, product overview (N-000001–N-000011)
- 001–003 parser only: no writing, no comment preservation — **T** (see 255–257).
- 004 TOML v1.1.0 compatible — **I** (grammar in `_parser.py`).
- 005 the language implemented is TOML v1.1.0 — **I**.
- 006 compatible with version 2.4.0 and later — **I** (`__version__`, `pyproject.toml`).
- 007 integrator gets plain mappings, sequences and scalars — **T**.
- 008 specification scope is observable behaviour — **N/A** (documentation constraint).
- 009 exact symbol names belong in the Interface Contract — **N/A** (documentation constraint; the public names follow the contract).
- 010 every feature point is real product behaviour — **T** (each FP has tests).
- 011 feature points ordered by dependency — **N/A** (documentation ordering).

### Pack 07 — Terminology (N-000012–N-000030)
- 012 a TOML document is one call's text; one document per call — **T**.
- 013 string-parse entry — **T**. 014 binary-file entry — **T**.
- 015 document mapping: `str` keys, native values — **T**.
- 016–017 table, including dotted and inline — **T** (`test_dotted_keys_create_nested_mappings`, `test_inline_tables_empty_dotted_multiline_trailing_comma`).
- 018 array of tables — **T** (`test_array_of_tables_appends_and_attaches_subtables`).
- 019 bare key: letters, digits, `_`, `-` (MAY) — **T**.
- 020 dotted key: two or more parts — **T**.
- 021 dotted-key table cannot receive a header (CF-000012) — **D** (`test_dotted_key_table_can_receive_subtable_via_header`, `test_structural_conflicts_are_refused` row `a.b = 1` / `[a.b]`).
- 022 inline table namespace frozen after it is written — **T** (`test_structural_conflicts_are_refused` rows `t = {…}`).
- 023 offset date-time: tz-aware — **T**.
- 024 date and time joined by `T`/`t` (CF-000068) — **D** (space also accepted).
- 025 local date-time: naive — **T**. 026 local date: `date` — **T**.
- 027 local time: constructed as `time` — **T**.
- 028 seconds always written (CF-000062) — **D** (seconds optional).
- 029 converter: only exact `dict`/`list` refused (CF-000023/032) — **D** (subclasses refused too).
- 030 decode error is a value error — **T**.

### Pack 08 — public surface inventory (N-000031–N-000039)
- 031 library, installed as a package — **I**.
- 032 no CLI, writer or config file — **T** (`test_no_write_or_cli_surface`).
- 033 parse one TOML document from text into a mapping — **T**.
- 034 construct TOML scalars as native values — **T**.
- 035 parse from a binary file, UTF-8 — **T**.
- 036 refuse invalid TOML and wrong Python type — **T**.
- 037 optional converter for floats (MAY) — **T**.
- 038 dicts and lists forbidden as conversion results — **T** (`test_value_error_from_parse_float_is_not_decode_error`).
- 039 no extra product surfaces — **T** (`test_package_has_version_and_no_third_party_imports` and the surface tests; `__version__` is metadata).

### Pack 09 — non-functional constraints (N-000040–N-000056)
- 040 pure Python, zero runtime dependencies — **T**.
- 041 optional compiled wheels (MAY) — **N/A** (none built; not required).
- 042 default path has no compiled extensions — **I**.
- 043 Python 3.8 or newer, CPython and PyPy — **C** (syntax check on 3.8 feature version; PyPy not run).
- 044 Linux, macOS, Windows — **C** (Linux only run).
- 045 Linux is the reference platform — **C**.
- 046 CPU-only — **I**. 047 no GPU or accelerator — **I**.
- 048 imported from this repository's source tree — **T** (tests run with `PYTHONPATH=src`).
- 049 TOML v1.1.0 — **I**.
- 050 v1.0.0-only behaviour and text-mode input are not this product — **T** (`test_load_refuses_text_mode_file_whatever_it_holds`; 1.1 features accepted).
- 051 successful parses return plain mappings, sequences and scalars — **T**.
- 052 no custom node types — **T**.
- 053 decode-error wording is free (MAY) — **N/A** (decision).
- 054 success vs failure, exception kind and location are guaranteed — **T**.
- 055 exception kind and location rules are fixed — **T** (`test_decode_error_location_for_interior_offset`).
- 056 MUST NOT promise a particular sentence — **N/A**.

### Pack 10 — real parser (global) (N-000057–N-000062)
- 057 every feature point is a capability of a real parser — **I**.
- 058 parser written in this product, no delegation to another TOML parser — **T** (`test_parser_does_not_use_stdlib_toml`).
- 059 parses the whole TOML v1.1.0 language — **I** (tests across FP-01 to FP-05).
- 060 MUST NOT delegate to another parser, including the stdlib — **T** (same test).
- 061 CPU baseline only — **I**.
- 062 no GPU, accelerator or extra service — **I**.

### Pack 11 — non-goals (N-000063–N-000076)
- 063 no encoding or writing — **T**. 064 no dump, write or encode entry — **T**.
- 065 no comment-preserving round trip — **T** (`test_comments_never_become_values_and_allow_non_ascii`).
- 066 results are plain builtin/stdlib values — **T**.
- 067 MUST NOT be TOML v1.0.0-only — **T** (1.1 features accepted: inline-table newlines and trailing commas, `\e`, `\x`, omitted seconds).
- 068 accepts TOML v1.1.0 documents — **T**.
- 069 inline tables may span lines, contain comments, end with trailing comma — **T** (`test_inline_tables_empty_dotted_multiline_trailing_comma`).
- 070 `\e` and `\x` string escapes — **T** (`test_basic_string_escapes`).
- 071 date-times whose seconds are omitted — **T** (`test_seconds_may_be_omitted_in_times`).
- 072 no command-line program, web server or config framework — **T** (`test_no_write_or_cli_surface`).
- 073 no throughput guarantee — **N/A**.
- 074 speed is a design goal (no claim) — **N/A**.
- 075 repository scripts are not product capabilities — **I** (no scripts were added).
- 076 no fallback import of stdlib `tomllib` — **T** (`test_parser_does_not_use_stdlib_toml`).

### Pack 12 — feature points (N-000077–N-000233)

FP-01 structure:
- 077–079 public entry; binary entry gives same mapping; converter does not change structure — **T** (`test_load_from_binary_buffer_equals_loads`, `test_converter_called_with_text_everywhere_for_floats_only`).
- 080 structure follows TOML v1.1.0 — **T**.
- 081 every document TOML allows is accepted — **T** (grammar tests); nesting limit noted in section 2.
- 082 empty, whitespace-only and comment-only text → empty mapping — **T**.
- 083–084 root pairs and table pairs — **T**.
- 085–086 keys always strings; numeric/boolean/float-like keys stay strings — **T** (`test_keys_are_strings_even_when_number_or_keyword_like`).
- 087 bare key characters; distinct spellings are distinct keys — **T**.
- 088 letter case significant — **T** (`test_keys_are_case_sensitive`).
- 089–091 basic or literal quoted keys; empty and non-ASCII allowed; dots inside a quoted key are part of the name — **T** (`test_quoted_keys_including_empty_and_dots`).
- 092 literal quoted key is its interior unchanged — **T**.
- 093–095 dotted keys make nested mappings; whitespace around dots insignificant; implicit tables take further dotted keys — **T** (`test_dotted_keys_create_nested_mappings`, `test_dotted_key_into_implicit_table_is_allowed`).
- 096–098 headers create missing parents; super-tables declared later; sub-table of dotted table via header — **T** (`test_header_creates_missing_parents_and_super_table_later_defined`, `test_dotted_key_table_can_receive_subtable_via_header`).
- 099–102 array-of-tables appends; nested headers attach to latest item; implied parents are plain tables; later declaration allowed — **T** (`test_array_of_tables_appends_and_attaches_subtables`, `test_array_of_tables_implies_plain_parent_tables`).
- 103–104 inline tables are mappings; may be empty, dotted, multi-line, trailing comma — **T**.
- 105–106 arrays are ordered sequences; empty, mixed, nested, multi-line, commented, trailing comma — **T** (106 per CF-000059, **D**).
- 107–109 comments run to end of line; never become values; non-ASCII allowed — **T**.
- 110 indentation insignificant — **T** (`test_indentation_insignificant`).
- 111 CR LF is one line feed everywhere — **T** (`test_crlf_is_single_line_feed_everywhere`).
- 112 CR LF inside a multiline string holds LF only (CF-000008) — **T** (same test; the CR-preserving reading is **D**).
- 113–122 structural constructs refused with the decode error: duplicate keys, table defined twice, reopened header/dotted tables, value replaced by table or array, inline table extended, array of tables extended by dotted key, pair without key or value, multiline key or table name, unclosed header, header sharing a line with a pair — **T** (`test_structural_conflicts_are_refused`, `test_dotted_key_into_header_defined_table_refused`).

FP-02 scalars:
- 123 scalar construction; same entries — **T**.
- 124–125 booleans are `bool`, not 0/1 — **T** (`test_booleans`).
- 126 booleans are not strings — **T**.
- 127 four string forms — **T** (`test_basic_string_escapes`, `test_literal_string_no_escapes`, `test_multiline_basic_trims_first_newline_and_keeps_others`, `test_multiline_literal_trims_first_newline`).
- 128 escapes processed in basic and multiline basic only — **T**.
- 129 literal and multiline literal never processed — **T** (`test_literal_string_no_escapes`).
- 130 multiline literal keeps a first LF (CF-000009) — **D** (discarded).
- 131 LF right after opening delimiter discarded in both multiline forms — **T** (`test_multiline_literal_trims_first_newline`).
- 132 later LFs kept — **T** (`test_multiline_basic_trims_first_newline_and_keeps_others`).
- 133 line endings kept with CR (CF-000008) — **D** (LF only).
- 134 line-ending backslash removes whitespace and line endings — **T** (`test_line_ending_backslash_trims_whitespace_including_newlines`).
- 135 one or two quotes allowed before closing delimiter of either multiline form (CF-000001) — **T** (`test_quotes_before_multiline_closing_delimiter`).
- 136 next line's leading whitespace kept (CF-000015) — **D** (trimmed).
- 137 basic escape set (`\b \t \n \f \r \e \" \\`) — **T** (`test_basic_string_escapes`).
- 138 `\x`, `\u`, `\U` escapes insert the code point — **T**.
- 139 hex digits case-insensitive (escape digits) — **T** (`test_hex_escape_digits_either_case`). See section 1, (not flagged) row for uppercase digits.
- 140 quoted basic key undergoes escape processing — **T** (`test_basic_quoted_key_uses_escapes_literal_does_not`).
- 141 literal quoted key does not — **T** (same test).
- 142 two spellings may be different keys (MAY) — **T** (same test).
- 143 tab in one-line string must be `\t` (CF-000028/035) — **D** (raw tab allowed).
- 144 integers: decimal, hex, octal, binary become `int` — **T** (`test_integers_all_bases`).
- 145 prefix letters lowercase only — **T** (`test_invalid_numbers_refused`: `0X`, `0O`, `0B`).
- 146 hex digits either case (MAY) — **T** (`test_integers_all_bases`: `0xDEADBEEF`).
- 147 single underscores between digits in every base (MAY) — **T** (`test_integers_all_bases`).
- 148 floats with fraction or exponent become `float` — **T** (`test_floats_default_and_special`).
- 149 `inf`, `+inf`, `-inf`, `nan`, `+nan`, `-nan` are floats — **T**.
- 150 signed NaN constructs a NaN — **T**.
- 151 offset date-time is tz-aware with the written offset — **T**.
- 152 local date-time naive, local date, local time — **T**.
- 153 date/time separator `T`, `t` or space (MAY) — **D** (CF-000068; all three accepted).
- 154 seconds may be omitted (MAY) — **T** (`test_seconds_may_be_omitted_in_times`); see CF-000062, **D**.
- 155 fractional second becomes the microsecond field — **T** (`test_local_time_naive_and_fraction_truncated`).
- 156 first six digits read as microseconds, padded on the right — **T** (`v = 07:32:00.1234567` → 123456; `u = …00.1` → 100000).
- 157 digits after the sixth dropped (truncated) — **T** (`t = …00.999999999` → 999999). CF-000045/069 rounding reading is **D**.
- 158 no fraction → microsecond 0 — **T**.
- 159 valid calendar dates including Feb 29 in leap years — **T** (`test_leap_day_2024_accepted_and_not_in_1900`).
- 160–161 parsed values copy, deep-copy and compare — **T** (`test_parsed_values_copy_and_compare_as_usual`).
- 162 any scalar TOML forbids refused with the decode error — **T**.
- 163 no mapping returned on scalar failure — **T**.
- 164 scalar failure is the decode error (needs 307) — **T**.
- 165 no other exception kind for scalar failures — **T**.
- 166 booleans other than lowercase `true`/`false` refused — **T** (`test_non_lowercase_booleans_refused`).
- 167 leading zero refused (decimal integer and float integer part) — **T**.
- 168 zero with sign refused (CF-000065) — **D** (`+0`/`-0` accepted).
- 169 uppercase base prefixes refused — **T**.
- 170 leading, trailing or doubled underscores refused — **T**.
- 171 signs on hex/octal/binary refused — **T**.
- 172 digits outside the base refused — **T**.
- 173 floats without a digit on both sides of the point refused — **T** (`test_invalid_numbers_refused`).
- 174 escapes outside the set refused — **T** (`test_invalid_strings_refused`).
- 175 incomplete or non-hex `\x`, `\u`, `\U` refused — **T**.
- 176 uppercase escape digits refused — **D** (conflicts with N-000139; accepted; see section 1, not flagged).
- 177 non-scalar escape code points (surrogates, above U+10FFFF) refused — **T**.
- 178 raw control characters other than tab; lone CR; line-ending backslash without line ending; unclosed strings; quote before multiline closing delimiter — **T** for every part except the last, which is **D** (CF-000001).
- 179 date-shaped values that are not real dates refused — **T** (`test_invalid_date_times_refused`).
- 180 hour, minute or second out of range refused — **T**.

FP-03 binary file:
- 181 binary-file entry — **T**. 182 takes a file object opened for binary reading — **T**.
- 183 reads contents, decodes UTF-8, behaves like string entry — **T** (`test_load_from_binary_buffer_equals_loads`).
- 184 same result as string entry for the same characters — **T**.
- 185 binary-mode disk files and in-memory binary buffers accepted — **T** (`test_load_reads_disk_binary_file`, `BytesIO` tests).
- 186 UTF-8 decoding; invalid UTF-8 handled — **T** (`test_load_invalid_utf8_is_decode_error`). Exact claim text is not identifiable from the pack's references.
- 187 bytes-like reads (bytearray, memoryview) — **T** (`test_load_accepts_bytearray_and_memoryview_reads`).
- 188 empty file → empty mapping — **T**.
- 189 disk binary and in-memory buffers both accepted — **T**.
- 190 text-mode file refused with `TypeError` — **T**.
- 191 no mapping returned for text-mode file — **T**.
- 192 text-mode refusal is not a decode error — **T**.
- 193 valid UTF-8 but invalid TOML → decode error with decoded text — **T**.
- 194 location for file errors is the string entry's location — **T** (`test_load_decode_error_carries_decoded_text_and_position`).
- 195 same location rule as string entry — **T**.
- 196 string entry refuses file objects and bytes (FP-04) — **T** (`test_loads_refuses_non_text_with_type_error`).

FP-04 rejection:
- 197 both entries reject invalid input — **T**.
- 198 invalid document: no mapping, not even partial — **T**.
- 199 no partial mapping on converter failure — **T**.
- 200 decode error is a value error — **T** (`test_decode_error_is_value_error_only`).
- 201 callers catching value errors also catch parse failures — **T**.
- 202 caller catching only decode error does not catch type errors — **T** (`test_loads_refuses_non_text_with_type_error`).
- 203 decode error carries msg, doc, pos separately — **T**.
- 204 1-based line and column derived from offset — **T**.
- 205 line = 1 + line feeds before offset — **T** (`test_decode_error_location_for_interior_offset`).
- 206 column = 1 + characters since last LF — **T**.
- 207 interior offset points to the failing character — **T**.
- 208 formatted report includes line and column (interior) — **T**.
- 209 formatted report mentions end of document at or past end — **T**.
- 210 caller constructs error from reason, text and offset — **T**.
- 211 constructed error carries exactly those values — **T**.
- 212 constructed error's report includes location — **T**.
- 213–215 wrong Python type → `TypeError` — **T**.
- 216 text-mode file → `TypeError` — **T**.
- 217 decode error is not a recursion error or type error — **T**.
- 218 report wording free (MAY) — **N/A** (decision).
- 219 exception kind and location rules fixed — **T**.

FP-05 converter:
- 220 converter on both entries; default when not supplied — **T** (`test_load_parse_float_applies_like_loads`).
- 221 converter applies to floats only; default float when absent — **T**.
- 222 does not change integers, strings, booleans, date-times, tables, arrays — **T**.
- 223 called for every float wherever it appears — **T** (`test_converter_called_with_text_everywhere_for_floats_only`).
- 224 special spellings also passed to converter — **T**.
- 225 `inf`, `nan` and signed forms passed — **T**.
- 226 converter receives characters as written (sign, underscores, exponent) — **T**.
- 227 return value stored in place of the float — **T**.
- 228 integers, strings, booleans, dates never passed to converter — **T**.
- 229 non-float values built as without converter — **T**.
- 230 any callable accepted (MAY) — **T** (`test_converter_returning_non_container_values_is_bound`).
- 231 non-dict/list result bound as returned — **T**.
- 232 dict or list result (or subclass) → `ValueError`, not decode error — **T** (`test_value_error_from_parse_float_is_not_decode_error`).
- 233 illegal converter result always that value error — **T**.

### Pack 13–15 — hardware requirements (N-000234–N-000254)
- 234 runs on the listed hardware; CPU profile provided by the product itself — **I**.
- 235 MUST NOT substitute a fallback for a mandatory profile — **I** (no fallback).
- 236 default path: no compiled extensions, no runtime dependencies, no GPU — **I**.
- 237 Python 3.8 or newer — **C** (see pack 01 263).
- 238 installable from source on x86_64/arm64 Linux, macOS, Windows — **C** (install not run).
- 239 optional compiled wheels not required — **I**.
- 240 CPU baseline: parse a TOML document from the source tree into native values — **T**.
- 241 profile id `cpu_baseline` (L4) — **N/A** (identifier only; recorded here, no code surface).
- 242 platforms linux, darwin, windows — **C** (Linux only run).
- 243 required on Linux — **T** (test suite runs on Linux).
- 244 parser imported from the source tree, not a published wheel — **T** (`PYTHONPATH=src`).
- 245 parses an in-memory document into native values — **T**.
- 246 setup: Python 3.8 or newer, zero runtime dependencies — **C** / **T** (no dependencies, `pyproject.toml`).
- 247 zero runtime third-party dependencies — **T**.
- 248 optional compiled-extension wheels (assumption) — **N/A** (none built).
- 249 compiled wheels not required for this profile — **I**.
- 250 no extra system libraries beyond a normal interpreter — **I**.
- 251 no native compile step — **I**.
- 252 src-layout package with a PEP 517 backend — **I** (`pyproject.toml`; the backend could not be run here, see header).
- 253 editable install or source directory on import path is enough — **T** (import via `PYTHONPATH=src`); editable install not run.
- 254 MAY — no compiled wheels; the optional clause is **N/A**.

## 4. Per-id status (all 323 checklist ids)

Legend: **I** implemented · **T** implemented and tested · **D** decided (conflicting claim not built; see section 1) · **C** satisfied by construction, not run here · **N** not applicable (documentation or process constraint, or identifier only).

Each id below is a checklist id from `spec/CHECKLIST.md`.

### Pack 01 — interface contract, product overview

```
N-000255  T
N-000256  T
N-000257  T
N-000258  T
N-000259  T
N-000260  T
N-000261  T
N-000262  T
N-000263  C
N-000264  C
N-000265  I
```

### Pack 02 — public surface

```
N-000266  I
N-000267  I
N-000268  I
N-000269  I
N-000270  T
N-000271  T
N-000272  T
N-000273  D
```

### Pack 03 — tomlparse.loads

```
N-000274  T
N-000275  T
N-000276  T
N-000277  T
N-000278  T
N-000279  D
N-000280  T
N-000281  T
N-000282  D
N-000283  T
N-000284  T
N-000285  D
N-000286  T
N-000287  T
N-000288  T
N-000289  T
N-000290  T
N-000291  T
N-000292  D
N-000293  T
N-000294  T
N-000295  T
N-000296  T
N-000297  T
N-000298  N
```

### Pack 04 — tomlparse.load

```
N-000299  T
N-000300  T
N-000301  T
N-000302  T
N-000303  T
N-000304  T
N-000305  T
N-000306  T
```

### Pack 05 — TOMLDecodeError

```
N-000307  T
N-000308  T
N-000309  T
N-000310  T
N-000311  T
N-000312  T
N-000313  T
N-000314  T
N-000315  T
N-000316  T
N-000317  T
N-000318  T
N-000319  T
N-000320  T
N-000321  T
N-000322  T
N-000323  N
```

### Pack 06 — PRD product overview

```
N-000001  T
N-000002  T
N-000003  T
N-000004  I
N-000005  I
N-000006  I
N-000007  T
N-000008  N
N-000009  N
N-000010  T
N-000011  N
```

### Pack 07 — terminology

```
N-000012  T
N-000013  T
N-000014  T
N-000015  T
N-000016  T
N-000017  T
N-000018  T
N-000019  T
N-000020  T
N-000021  D
N-000022  T
N-000023  T
N-000024  D
N-000025  T
N-000026  T
N-000027  T
N-000028  D
N-000029  D
N-000030  T
```

### Pack 08 — public surface inventory

```
N-000031  I
N-000032  T
N-000033  T
N-000034  T
N-000035  T
N-000036  T
N-000037  T
N-000038  T
N-000039  T
```

### Pack 09 — non-functional constraints

```
N-000040  T
N-000041  N
N-000042  I
N-000043  C
N-000044  C
N-000045  C
N-000046  I
N-000047  I
N-000048  T
N-000049  I
N-000050  T
N-000051  T
N-000052  T
N-000053  N
N-000054  T
N-000055  T
N-000056  N
```

### Pack 10 — real parser (global)

```
N-000057  I
N-000058  T
N-000059  I
N-000060  T
N-000061  I
N-000062  I
```

### Pack 11 — non-goals

```
N-000063  T
N-000064  T
N-000065  T
N-000066  T
N-000067  T
N-000068  T
N-000069  T
N-000070  T
N-000071  T
N-000072  T
N-000073  N
N-000074  N
N-000075  I
N-000076  T
```

### Pack 12 — feature points FP-01..FP-05

```
N-000077  T
N-000078  T
N-000079  T
N-000080  T
N-000081  T
N-000082  T
N-000083  T
N-000084  T
N-000085  T
N-000086  T
N-000087  T
N-000088  T
N-000089  T
N-000090  T
N-000091  T
N-000092  T
N-000093  T
N-000094  T
N-000095  T
N-000096  T
N-000097  T
N-000098  T
N-000099  T
N-000100  T
N-000101  T
N-000102  T
N-000103  T
N-000104  T
N-000105  T
N-000106  D
N-000107  T
N-000108  T
N-000109  T
N-000110  T
N-000111  T
N-000112  T
N-000113  T
N-000114  T
N-000115  T
N-000116  T
N-000117  T
N-000118  T
N-000119  T
N-000120  T
N-000121  T
N-000122  T
N-000123  T
N-000124  T
N-000125  T
N-000126  T
N-000127  T
N-000128  T
N-000129  T
N-000130  D
N-000131  T
N-000132  T
N-000133  D
N-000134  T
N-000135  T
N-000136  D
N-000137  T
N-000138  T
N-000139  T
N-000140  T
N-000141  T
N-000142  T
N-000143  D
N-000144  T
N-000145  T
N-000146  T
N-000147  T
N-000148  T
N-000149  T
N-000150  T
N-000151  T
N-000152  T
N-000153  D
N-000154  T
N-000155  T
N-000156  T
N-000157  T
N-000158  T
N-000159  T
N-000160  T
N-000161  T
N-000162  T
N-000163  T
N-000164  T
N-000165  T
N-000166  T
N-000167  T
N-000168  D
N-000169  T
N-000170  T
N-000171  T
N-000172  T
N-000173  T
N-000174  T
N-000175  T
N-000176  D
N-000177  T
N-000178  T
N-000179  T
N-000180  T
N-000181  T
N-000182  T
N-000183  T
N-000184  T
N-000185  T
N-000186  T
N-000187  T
N-000188  T
N-000189  T
N-000190  T
N-000191  T
N-000192  T
N-000193  T
N-000194  T
N-000195  T
N-000196  T
N-000197  T
N-000198  T
N-000199  T
N-000200  T
N-000201  T
N-000202  T
N-000203  T
N-000204  T
N-000205  T
N-000206  T
N-000207  T
N-000208  T
N-000209  T
N-000210  T
N-000211  T
N-000212  T
N-000213  T
N-000214  T
N-000215  T
N-000216  T
N-000217  T
N-000218  N
N-000219  T
N-000220  T
N-000221  T
N-000222  T
N-000223  T
N-000224  T
N-000225  T
N-000226  T
N-000227  T
N-000228  T
N-000229  T
N-000230  T
N-000231  T
N-000232  T
N-000233  T
```

### Packs 13–15 — hardware requirements

```
N-000234  I
N-000235  I
N-000236  I
N-000237  C
N-000238  C
N-000239  I
N-000240  T
N-000241  N
N-000242  C
N-000243  T
N-000244  T
N-000245  T
N-000246  C
N-000247  T
N-000248  N
N-000249  I
N-000250  I
N-000251  I
N-000252  I
N-000253  T
N-000254  N
```
