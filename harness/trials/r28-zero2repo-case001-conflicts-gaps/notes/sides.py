"""Make one alternative copy of a built tomlparse per candidate, for the footprint runs and the probe check.

    python3 notes/sides.py work/base-app work/sides [C01 ...]        (from the trial folder)

Round 28, case001 (new for this case; the method of ../r28-zero2repo-case005-conflicts-gaps/notes/sides.py).
  - C.. **conflict** candidates: the original spec states side A (the upstream behaviour); a planted
    sentence will state side B. The copy builds side B.
  - G.. **gap** candidates: a stated fact that may be removed from the spec. The copy builds a plausible
    alternative an agent could invent once the fact is gone. The PRD makes TOML v1.1.0 the authority for
    the grammar, so a TOML grammar fact stays implied after removal: gap candidates are product facts
    TOML v1.1.0 does not fix (failure location, the float converter, nesting depth, UTF-8 handling).
The base build (round 13b `haiku-case001-1`, 302 / 302) takes the upstream value on every candidate; each
patch is the smallest change that moves that one behaviour. Every anchor must occur exactly once. Writes
work/sides/<id>/ and work/sides/<id>.tgz, plus work/sides/BASE.tgz. Written from the spec and the base
code only, never from the hidden tests (only their names were read).
"""
import shutil
import sys
import tarfile
from pathlib import Path

PR, ER, IN = "src/tomlparse/_parser.py", "src/tomlparse/_errors.py", "src/tomlparse/__init__.py"

PATCHES = {
    # ---- conflicts: side B built
    # C01 `\e` is an escape for code point 27 (A) -> not an escape; refused (B)
    "C01": [(PR, "    'e': '\\x1b',\n", "")],
    # C02 `\xHH` inserts that code point (A) -> not an escape; refused (B)
    "C02": [(PR, "_ESCAPE_DIGITS = {'x': 2, 'u': 4, 'U': 8}", "_ESCAPE_DIGITS = {'u': 4, 'U': 8}")],
    # C03 a local time may omit its seconds (A) -> a local time must have seconds (B)
    "C03": [(PR, "    def _time(self, m, start):\n", "    def _time(self, m, start):\n        if m.group(3) is None:\n            raise self._err('local time without seconds', start)\n")],
    # C04 fractional seconds beyond six digits truncated (A) -> rounded to the nearest microsecond (B)
    "C04": [(PR, "        micro = int((frac or '')[:6].ljust(6, '0'))",
             "        micro = min(999999, int(round(float('0.' + frac) * 1000000))) if frac else 0")],
    # C05 a trailing comma after the last pair of an inline table is allowed (A) -> refused (B)
    "C05": [(PR, "            self.i += 1\n            self._skip_ws_nl()\n            if self.i < self.n and self.s[self.i] == '}':\n                self.i += 1\n                return table",
             "            self.i += 1\n            self._skip_ws_nl()\n            if self.i < self.n and self.s[self.i] == '}':\n                raise self._err('trailing comma in inline table', self.i)")],
    # C06 an inline table may span lines (A) -> a line feed inside an inline table is refused (B)
    "C06": [(PR, "    def _inline_table(self):\n        self.i += 1\n        table = self._new_dict('inline')\n        self._skip_ws_nl()",
             "    def _inline_table(self):\n        self.i += 1\n        table = self._new_dict('inline')\n        self._skip_ws_inline()"),
            (PR, "            self._keyval(table)\n            self._skip_ws_nl()", "            self._keyval(table)\n            self._skip_ws_inline()"),
            (PR, "            if c != ',':\n                raise self._err(\"expected ',' or '}'\", self.i)\n            self.i += 1\n            self._skip_ws_nl()",
             "            if c != ',':\n                raise self._err(\"expected ',' or '}'\", self.i)\n            self.i += 1\n            self._skip_ws_inline()"),
            (PR, "    def _scalar(self):", "    def _skip_ws_inline(self):\n        self._skip_ws()\n        if self.i < self.n and self.s[self.i] in '\\r\\n#':\n"
             "            raise self._err('line break in inline table', self.i)\n\n    def _scalar(self):")],
    # C07 an array may end with a trailing comma (A) -> refused (B)
    "C07": [(PR, "            self.i += 1\n            self._skip_ws_nl()\n            if self.i < self.n and self.s[self.i] == ']':\n                self.i += 1\n                return items",
             "            self.i += 1\n            self._skip_ws_nl()\n            if self.i < self.n and self.s[self.i] == ']':\n                raise self._err('trailing comma in array', self.i)")],
    # C08 a signed zero (`+0`, `-0`) is the integer 0 (A) -> refused (B)
    "C08": [(PR, "        if _INT_DEC.fullmatch(token):\n", "        if token in ('+0', '-0'):\n            raise self._err('signed zero', i)\n        if _INT_DEC.fullmatch(token):\n")],
    # C09 `+nan` and `-nan` are accepted and construct NaN (A) -> only unsigned `nan` (B)
    "C09": [(PR, "_SPECIAL_FLOATS = frozenset(['inf', '+inf', '-inf', 'nan', '+nan', '-nan'])",
             "_SPECIAL_FLOATS = frozenset(['inf', '+inf', '-inf', 'nan'])")],
    # C10 CRLF inside a multiline basic string holds a line feed (A) -> kept as CRLF (B)
    "C10": [(PR, "                    raise self._err('bare carriage return in string', i)\n                buf.append('\\n')",
             "                    raise self._err('bare carriage return in string', i)\n                buf.append('\\r\\n')")],
    # C11 a multiline literal string drops the line feed right after its opening delimiter (A) -> keeps it (B)
    "C11": [(PR, "    def _ml_literal_string(self):\n        s = self.s\n        i = self.i + 3\n        if s.startswith('\\r\\n', i):\n            i += 2\n        elif s.startswith('\\n', i):\n            i += 1\n",
             "    def _ml_literal_string(self):\n        s = self.s\n        i = self.i + 3\n")],
    # C12 a line-ending backslash removes the line ending and all whitespace after it (A) -> only the line ending; the next line's indentation is kept (B)
    "C12": [(PR, "                if k < self.n and (s[k] == '\\n' or s.startswith('\\r\\n', k)):\n                    i = self._skip_line_ending_whitespace(k)",
             "                if k < self.n and (s[k] == '\\n' or s.startswith('\\r\\n', k)):\n                    i = k + (2 if s[k] == '\\r' else 1)")],
    # C13 a multiline basic string may end with one or two quotes before its closing delimiter (A) -> refused (B)
    "C13": [(PR, "                    if j - i > 5:\n                        raise self._err('too many quotes in string', i)\n                    buf.append('\"' * (j - i - 3))",
             "                    if j - i > 3:\n                        raise self._err('too many quotes in string', i)\n                    buf.append('\"' * (j - i - 3))")],
    # C14 a raw tab is allowed in a one-line string (A) -> refused (B)
    "C14": [(PR, "_BASIC_RUN = re.compile(r'[^\"\\\\\\x00-\\x08\\x0a-\\x1f\\x7f]+')", "_BASIC_RUN = re.compile(r'[^\"\\\\\\x00-\\x1f\\x7f]+')")],
    # C15 a single underscore may separate digits in every base (A) -> only in decimal integers (B)
    "C15": [(PR, "            base = {'x': 16, 'o': 8, 'b': 2}[token[1]]\n",
             "            base = {'x': 16, 'o': 8, 'b': 2}[token[1]]\n            if '_' in token:\n                raise self._err('underscore in a prefixed integer', i)\n")],
    # C16 hexadecimal integer digits may be either case (A) -> lowercase only, like the prefix (B)
    "C16": [(PR, "    r'0(?:x[0-9A-Fa-f](?:_?[0-9A-Fa-f])*'", "    r'0(?:x[0-9a-f](?:_?[0-9a-f])*'")],
    # C17 hex digits of `\x`, `\u`, `\U` escapes are case-insensitive (A) -> uppercase hex letters refused (B)
    "C17": [(PR, "            if len(digits) == width and all(c in _HEX for c in digits):",
             "            if len(digits) == width and all(c in '0123456789abcdef' for c in digits):")],
    # C18 a space may separate date and time (A) -> only `T` or `t` (B)
    "C18": [(PR, "    r'(?:[Tt ]([0-9]{2}):", "    r'(?:[Tt]([0-9]{2}):")],
    # C19 `z` (lowercase) is UTC like `Z` (A) -> only uppercase `Z` (B)
    "C19": [(PR, "    r'([Zz]|[+-][0-9]{2}:[0-9]{2})?)?')", "    r'(Z|[+-][0-9]{2}:[0-9]{2})?)?')")],
    # C25 colno is 1-based (A) -> 0-based (B)
    "C25": [(ER, "        self.colno = pos - doc.rfind('\\n', 0, pos)", "        self.colno = pos - doc.rfind('\\n', 0, pos) - 1")],
    # C28 a converter returning a tuple is allowed (A) -> refused like a list (B)
    "C28": [(PR, "        if isinstance(value, (dict, list)):", "        if isinstance(value, (dict, list, tuple)):")],
    # C29 subclasses of dict / list are refused too (A) -> only exact dict / list (B)
    "C29": [(PR, "        if isinstance(value, (dict, list)):", "        if type(value) in (dict, list):")],
    # C35 a quoted key may be empty (A) -> refused (B)
    "C35": [(PR, "        if c == '\"':\n            if self.s.startswith('\"\"\"', i):\n                raise self._err('multiline string is not a valid key', i)\n            return self._basic_string()",
             "        if c == '\"':\n            if self.s.startswith('\"\"\"', i):\n                raise self._err('multiline string is not a valid key', i)\n"
             "            if self.s.startswith('\"\"', i):\n                raise self._err('empty key', i)\n            return self._basic_string()"),
            (PR, "            if self.s.startswith(\"'''\", i):\n                raise self._err('multiline string is not a valid key', i)\n            return self._literal_string()",
             "            if self.s.startswith(\"'''\", i):\n                raise self._err('multiline string is not a valid key', i)\n"
             "            if self.s.startswith(\"''\", i):\n                raise self._err('empty key', i)\n            return self._literal_string()")],
    # C36 a header may declare a sub-table of a table made by dotted keys (A) -> refused (B)
    "C36": [(PR, "            elif isinstance(value, dict) and self._kind_of(value) in (\n                    'table', 'implicit', 'dotted', 'elem'):\n                cur = value",
             "            elif isinstance(value, dict) and self._kind_of(value) in (\n                    'table', 'implicit', 'elem'):\n                cur = value")],
    # ---- gaps: the alternative built
    # G01 unfinished document: offset = the document's length (alt: the index of the last character)
    "G01": [(PR, "            raise self._err('unterminated array', self.n)", "            raise self._err('unterminated array', self.n - 1)"),
            (PR, "            raise self._err('unterminated inline table', self.n)", "            raise self._err('unterminated inline table', self.n - 1)"),
            (PR, "    def _value(self):\n        s = self.s\n        i = self.i\n        if i >= self.n:\n            raise self._err('expected a value', i)",
             "    def _value(self):\n        s = self.s\n        i = self.i\n        if i >= self.n:\n            raise self._err('expected a value', max(i - 1, 0))")],
    # G03 a conflicting header fails at a character within the header (alt: at the end of the header line)
    "G03": [(PR, "        self.i += 1\n        return self._header_table(root, parts, start)",
             "        self.i += 1\n        try:\n            return self._header_table(root, parts, start)\n        except TOMLDecodeError as e:\n"
             "            raise self._err(e.msg, self.i) from None")],
    # G04 the converter gets the float's characters exactly as written, underscores included (alt: underscores removed)
    "G04": [(PR, "        value = self.parse_float(token)", "        value = self.parse_float(token.replace('_', ''))")],
    # G05 the converter is called for the inf / nan spellings too (alt: only for numerals)
    "G05": [(PR, "        if token in _SPECIAL_FLOATS:\n            return self._float(token)",
             "        if token in _SPECIAL_FLOATS:\n            return float(token)")],
    # G09 inline arrays nested 470 deep parse (alt: a nesting guard that refuses arrays nested deeper than 100)
    "G09": [(PR, "    def _array(self):\n        self.i += 1\n",
             "    def _array(self):\n        self.depth = getattr(self, 'depth', 0) + 1\n        if self.depth > 100:\n            raise self._err('arrays nested too deeply', self.i)\n"
             "        try:\n            return self._array_body()\n        finally:\n            self.depth -= 1\n\n    def _array_body(self):\n        self.i += 1\n")],
    # G13 bytes that are not UTF-8 are never reinterpreted in another encoding (alt: Latin-1 fallback)
    "G13": [(IN, "    return parse_document(data.decode('utf-8'), parse_float)",
             "    try:\n        text = data.decode('utf-8')\n    except UnicodeDecodeError:\n        text = data.decode('latin-1')\n    return parse_document(text, parse_float)")],
}


def main():
    base, out = Path(sys.argv[1]), Path(sys.argv[2])
    ids = sys.argv[3:] or sorted(PATCHES)
    out.mkdir(parents=True, exist_ok=True)
    with tarfile.open(out / "BASE.tgz", "w:gz") as tf:
        tf.add(base, arcname=".")
    for v in ids:
        d = out / v
        if d.exists():
            shutil.rmtree(d)
        shutil.copytree(base, d)
        for f, old, new in PATCHES[v]:
            p = d / f
            text = p.read_text()
            n = text.count(old)
            assert n == 1, f"{v}: anchor occurs {n} times in {f}: {old[:70]!r}"
            p.write_text(text.replace(old, new))
        with tarfile.open(out / f"{v}.tgz", "w:gz") as tf:
            tf.add(d, arcname=".")
        print(v, "ok")


if __name__ == "__main__":
    main()
