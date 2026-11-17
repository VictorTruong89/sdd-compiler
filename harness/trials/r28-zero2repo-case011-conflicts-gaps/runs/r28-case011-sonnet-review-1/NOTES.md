# NOTES

Package: `pathsel/` (flat layout). Exceptions in `pathsel/exceptions.py`: all derive from `ValueError`;
`EmptyExpressionError`, `IncompleteExpressionError`, `ParseError` (grammar syntax), `LexerError` (subclass of ParseError, token-level),
`ZeroSliceStepError`, `UnknownFunctionError`, `ArityError`, `InvalidTypeError`. Syntax/incomplete carry `lex_position`.

## Spec conflicts (CONFLICTS.md C-01..C-14) and what I built
- C-01 bare expression reference: Terminology says null; FP-05 and Interface Contract say non-null. Built: non-null `ExprRef` object.
- C-02 `not_null` with ""/[]: Terminology (line 23) says they count as null; FP-07 (line 252) says not null. Built: they are NOT null (only None is skipped).
- C-03 object wildcard on non-object: Terminology says `[]`; FP-04 says null. Built: null.
- C-04 filter on non-array: FP-04 says null; FP-06 says `[]`. Built: null.
- C-05 slice on non-array: FP-03 line 138 says null; line 148 says `[]`. Built: null.
- C-06 slice step 0: FP-03 line 133 says empty array; line 146 and Interface Contract say refusal. Built: refusal (`ZeroSliceStepError`, raised at compile/parse time, so both entries refuse).
- C-07 lone `=`: Terminology says grammar-level; FP-06 says token-level. Built: token-level (`LexerError`).
- C-08 `join([])`: FP-07 paragraph says null; the function definition says "". Built: "".
- C-09 `to_number`: Terminology says always float; FP-07 says integer numeral gives int. Built: integer numerals -> int, other numerals -> float.
- C-10 string length: Terminology says UTF-8 bytes; FP-07 `length` says characters. Built: characters (`len(str)`).
- C-11 multiselect list on null: line 187 says builds element per expression; line 188 says yields null. Built: null for both list and hash.
- C-12 `length` arity: built as one argument.
- C-13 `[ ]` with whitespace: flatten only when `[]` is adjacent; `[ ]` is a syntax error (`[` then `]`).
- C-14 trailing dot (`foo.`): built as grammar-level syntax error (the spec names the end of text after a dot explicitly as syntax), position = text length. Other end-of-text positions needing an operand/closer are Incomplete.

## Unstated items / assumptions
- Numbers are not expression operands: a bare `1` (e.g. `f(1)`) is a syntax error; use backtick literals. Numbers only appear in brackets.
- Empty hash `{}` is a syntax error.
- Quoted-identifier JSON decoding uses strict `json.loads` (raw control characters are rejected).
- `type()` / `to_string()` of a non-JSON host value (or of an expression reference) raise invalid-type.
- Object args accept any `collections.abc.Mapping` and instances of the supplied `dict_cls`. `merge` returns a plain `dict`.
- Raw-string `\uXXXX` is decoded (surrogate pairs combined); `\'` is a quote.
- Custom function `signature` also accepts `"variadic": True` on the last spec (extension); the internal builtin type names `any`, `array-number`, `array-string`, `expref`, `boolean` are also understood.
- If a provider is not a `Functions` subclass, built-ins still fall back to the default provider.
- Comparators with incomparable operand types (`<` on string vs number) return null (a false value).
- `avg` uses true division; `sum([])` is 0.
