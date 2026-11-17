"""Make one alternative copy of a built pathsel per candidate, for the footprint runs and the probe check.

    python3 notes/sides.py work/base-app work/sides [C01 ...]        (from the trial folder)

Round 28, case011 (new for this case; the method of ../r28-zero2repo-case005-conflicts-gaps/notes/sides.py).
Two kinds of candidate share one list:
  - C.. **conflict** candidates: the original spec states side A (the upstream behaviour); a planted
    sentence will state side B. The copy builds side B.
  - G.. **gap** candidates: a stated fact that may be removed from the spec. The copy builds a plausible
    alternative an agent could invent once the fact is gone.
The base build (round 13b `haiku-case011-1`, 321 / 321) takes the upstream value on every candidate; each
patch is the smallest change that moves that one behaviour. Every anchor must occur exactly once. Writes
work/sides/<id>/ and work/sides/<id>.tgz, plus work/sides/BASE.tgz. Written from the spec and the base
code only, never from the hidden tests (only their names were read).
"""
import shutil
import sys
import tarfile
from pathlib import Path

FN, IN, PA, VA, AP = "pathsel/functions.py", "pathsel/interpreter.py", "pathsel/parser.py", "pathsel/values.py", "pathsel/api.py"

PATCHES = {
    # ---- conflicts: side B built
    # C01 avg of the empty array: null (A) -> 0 (B)
    "C01": [(FN, "        if not items:\n            return None\n        return sum(items) / float(len(items))",
             "        if not items:\n            return 0\n        return sum(items) / float(len(items))")],
    # C02 join of the empty array: the empty string (A) -> null (B)
    "C02": [(FN, "        return separator.join(items)", "        return separator.join(items) if items else None")],
    # C03 merge: a later key overwrites an earlier one (A) -> the first occurrence is kept (B)
    "C03": [(FN, "        for item in objects:\n            result.update(item)",
             "        for item in objects:\n            for key in item:\n                result.setdefault(key, item[key])")],
    # C04 max / min of the empty array: null (A) -> invalid-type refusal (B)
    "C04": [(FN, "        return max(items) if items else None", "        if not items:\n            raise InvalidTypeError(\"max() of an empty array\")\n        return max(items)"),
            (FN, "        return min(items) if items else None", "        if not items:\n            raise InvalidTypeError(\"min() of an empty array\")\n        return min(items)")],
    # C05 not_null: an empty array or string is not null (A) -> skipped like null (B)
    "C05": [(FN, "            if value is not None:\n                return value", "            if value is not None and value != \"\" and value != []:\n                return value")],
    # C06 map keeps nulls (A) -> drops nulls like a projection (B)
    "C06": [(FN, "        return [reference.evaluate(item) for item in items]",
             "        return [r for r in (reference.evaluate(item) for item in items) if r is not None]")],
    # C07 max_by / min_by: the first element on ties (A) -> the last (B)
    "C07": [(FN, "            if keys[index] > keys[best]:", "            if keys[index] >= keys[best]:"),
            (FN, "            if keys[index] < keys[best]:", "            if keys[index] <= keys[best]:")],
    # C08 length of a string counts Unicode characters (A) -> UTF-8 bytes (B)
    "C08": [(FN, "    def _func_length(self, value):\n        return len(value)",
             "    def _func_length(self, value):\n        if isinstance(value, str):\n            return len(value.encode(\"utf-8\"))\n        return len(value)")],
    # C09 ordering of two strings in code-point order (A) -> only numbers are ordered; strings yield null (B)
    "C09": [(VA, "    ordered = ((is_comparable_number(left) and is_comparable_number(right))\n               or (isinstance(left, str) and isinstance(right, str)))",
             "    ordered = (is_comparable_number(left) and is_comparable_number(right))")],
    # C10 host decimals take part in ordering as numbers (A) -> a decimal side yields null (B)
    "C10": [(VA, "    ordered = ((is_comparable_number(left) and is_comparable_number(right))",
             "    ordered = ((is_number(left) and is_number(right))")],
    # C11 multiselect hash stores null under a key whose value is null (A) -> the key is omitted (B)
    "C11": [(IN, "        for pair in node.children:\n            result[pair.value] = self.visit(pair.children[0], value)",
             "        for pair in node.children:\n            item = self.visit(pair.children[0], value)\n            if item is not None:\n                result[pair.value] = item")],
    # C12 multiselect list whose current value is null yields null (A) -> a list of the element results (B)
    "C12": [(IN, "    def _visit_multi_list(self, node, value):\n        if value is None:\n            return None\n",
             "    def _visit_multi_list(self, node, value):\n")],
    # C13 a slice that selects nothing is the empty array (A) -> null (B)
    "C13": [(IN, "        return [value[index] for index in _slice_range(len(value), start, stop, step)]",
             "        picked = [value[index] for index in _slice_range(len(value), start, stop, step)]\n        return picked if picked else None")],
    # C14 a slice on a non-array yields null (A) -> the empty array (B)
    "C14": [(IN, "    def _visit_slice(self, node, value):\n        if not is_array(value):\n            return None",
             "    def _visit_slice(self, node, value):\n        if not is_array(value):\n            return []")],
    # C15 a filter on a non-array yields null (A) -> the empty array (B)
    "C15": [(IN, "        base = self.visit(subject, value)\n        if not is_array(base):\n            return None\n        return [item for item",
             "        base = self.visit(subject, value)\n        if not is_array(base):\n            return []\n        return [item for item")],
    # C16 a list wildcard on a non-array yields null (A) -> the empty array (B)
    "C16": [(PA, "        if token.type == 'star' and self._peek_type() == 'rbracket':\n            self._advance()\n            self._advance()\n            return Node('projection', [subject, self._projection_rhs(_STAR)])",
             "        if token.type == 'star' and self._peek_type() == 'rbracket':\n            self._advance()\n            self._advance()\n            return Node('list_projection', [subject, self._projection_rhs(_STAR)])"),
            (IN, "    def _visit_value_projection(self, node, value):",
             "    def _visit_list_projection(self, node, value):\n        left, right = node.children\n        base = self.visit(left, value)\n"
             "        if not is_array(base):\n            return []\n        return self._collect(right, base)\n\n    def _visit_value_projection(self, node, value):")],
    # C17 an object wildcard on a non-object yields null (A) -> the empty array (B)
    "C17": [(IN, "        base = self.visit(left, value)\n        if not is_object(base):\n            return None\n        return self._collect(right, list(base.values()))",
             "        base = self.visit(left, value)\n        if not is_object(base):\n            return []\n        return self._collect(right, list(base.values()))")],
    # C18 an index on a string yields null (A) -> the character at that index (B)
    "C18": [(IN, "    def _visit_index(self, node, value):\n        if not is_array(value):\n            return None",
             "    def _visit_index(self, node, value):\n        if not (is_array(value) or isinstance(value, str)):\n            return None")],
    # C19 a raw string processes no JSON escapes (A) -> JSON escapes such as \\u0041 are decoded (B)
    "C19": [(PA, "    return ''.join(characters), end + 1\n\n\ndef _json_literal",
             "    text_value = ''.join(characters)\n    if '\\\\u' in text_value:\n        try:\n            text_value = json.loads('\"%s\"' % text_value)\n        except ValueError:\n            pass\n"
             "    return text_value, end + 1\n\n\ndef _json_literal")],
    # C20 a zero slice step is refused as its own kind (A) -> an empty array (B)
    "C20": [(PA, "        if step == 0:\n            raise ZeroSliceStepError('slice step cannot be zero')\n        return Node('slice', value=(start, stop, step))",
             "        if step == 0:\n            return Node('literal', value=[])\n        return Node('slice', value=(start, stop, step))")],
    # C21 a quoted identifier followed by an argument list is a syntax failure (A) -> it calls that function (B)
    "C21": [(PA, "            if self._current().type == 'lparen':\n                raise _syntax(self._current())",
             "            if self._current().type == 'lparen':\n                return self._function(token.value)")],
    # C22 a bare expression reference yields a non-null value (A) -> null (B)
    "C22": [(PA, "    return _Parser(tokenize(expression)).parse()",
             "    node = _Parser(tokenize(expression)).parse()\n    if node.kind == 'expref':\n        return Node('literal', value=None)\n    return node")],
    # C23 compiling a call to an unknown name succeeds; the search refuses (A) -> the compile refuses (B)
    "C23": [(PA, "        return Node('function', arguments, name)\n\n    def _multi_list",
             "        _check_name(name)\n        return Node('function', arguments, name)\n\n    def _multi_list"),
            (PA, "def parse(expression):",
             "def _check_name(name):\n    from .functions import BUILTINS\n    from .errors import UnknownFunctionError\n"
             "    if name not in BUILTINS:\n        raise UnknownFunctionError('unknown function %s()' % name)\n\n\ndef parse(expression):")],
    # C24 a lone `=` is a token-level syntax failure (A) -> a grammar-level one (plain syntax kind) (B)
    "C24": [(PA, "        elif character in _SIMPLE_TOKENS:\n            tokens.append(Token(_SIMPLE_TOKENS[character], None, position))\n            position += 1",
             "        elif character in _SIMPLE_TOKENS:\n            tokens.append(Token(_SIMPLE_TOKENS[character], None, position))\n            position += 1\n"
             "        elif character == '=':\n            tokens.append(Token('equals', None, position))\n            position += 1")],
    # C25 an unquoted hyphen is a token-level syntax failure (A) -> a grammar-level one (B)
    "C25": [(PA, "        elif character == '-':\n            raise TokenSyntaxError('hyphen begins no token', position)",
             "        elif character == '-':\n            tokens.append(Token('hyphen', None, position))\n            position += 1")],
    # C26 to_number: an integer numeral becomes an integer (A) -> every numeral becomes a float (B)
    "C26": [(FN, "            if _INTEGER_NUMERAL.fullmatch(value):\n                return int(value)",
             "            if _INTEGER_NUMERAL.fullmatch(value):\n                return float(value)")],
    # C27 to_string writes non-ASCII characters as \\uXXXX escapes (A) -> as they are (B)
    "C27": [(FN, "            return json.dumps(value, separators=(\",\", \":\"))",
             "            return json.dumps(value, separators=(\",\", \":\"), ensure_ascii=False)")],
    # ---- gaps: the alternative built
    # G03 sort of the empty array: the empty array (alt: null)
    "G03": [(FN, "        _require_numbers_or_strings(items, \"sort\")\n        return sorted(items)",
             "        _require_numbers_or_strings(items, \"sort\")\n        return sorted(items) if items else None")],
    # G04 sort_by is stable on equal keys (alt: equal keys in reverse input order)
    "G04": [(FN, "        order = sorted(range(len(items)), key=keys.__getitem__)",
             "        order = sorted(range(len(items)), key=lambda i: (keys[i], -i))")],
    # G07 to_string compact, no space after `,` or `:` (alt: the host encoder's default separators)
    "G07": [(FN, "            return json.dumps(value, separators=(\",\", \":\"))", "            return json.dumps(value)")],
    # G22 ordering with an array, object, boolean or null side yields null (alt: false)
    "G22": [(VA, "    if not ordered:\n        return None", "    if not ordered:\n        return False")],
    # G25 raw string: a backslash pair other than \\' is kept as written (alt: \\\\ stands for one backslash)
    "G25": [(PA, "            characters.append(\"'\" if following == \"'\" else character + following)",
             "            characters.append(following if following in \"'\\\\\" else character + following)")],
    # G27 to_string of a non-JSON host value: its text as a JSON string encoding (alt: the plain text)
    "G27": [(FN, "            return json.dumps(str(value))", "            return str(value)")],
    # G28 a host decimal is refused where a function needs a number (alt: accepted)
    "G28": [(VA, "    'number': is_number,", "    'number': is_comparable_number,")],
    # G29 merge returns the host's ordinary mapping whatever the options (alt: the supplied mapping type)
    "G29": [(FN, "    def _func_merge(self, *objects):\n        result = {}",
             "    def _func_merge(self, *objects):\n        result = type(objects[0])() if type(objects[0]) is not dict and isinstance(objects[0], dict) else {}")],
    # G34 the supplied mapping type builds every multiselect hash at any depth (alt: only the outermost)
    "G34": [(IN, "        result = self._dict_cls() if self._dict_cls is not None else {}\n",
             "        result = self._dict_cls() if self._dict_cls is not None and not getattr(self, '_inner', False) else {}\n"
             "        self._inner, outer = True, getattr(self, '_inner', False)\n"
             "        try:\n            return self._fill_hash(node, value, result)\n        finally:\n            self._inner = outer\n\n"
             "    def _fill_hash(self, node, value, result):\n")],
    # G35 hash keys inserted in declaration order (alt: sorted keys)
    "G35": [(IN, "        for pair in node.children:\n            result[pair.value] = self.visit(pair.children[0], value)",
             "        for pair in sorted(node.children, key=lambda p: p.value):\n            result[pair.value] = self.visit(pair.children[0], value)")],
    # G54 a backslash-backtick inside a JSON literal stands for a backtick (alt: no such escape; the backslash stays)
    "G54": [(PA, "    lexeme = ''.join(characters).replace('\\\\`', '`')", "    lexeme = ''.join(characters)")],
    # G60 sum of the empty array: 0 (alt: null)
    "G60": [(FN, "        _require_numbers(items, \"sum\")\n        return sum(items)", "        _require_numbers(items, \"sum\")\n        return sum(items) if items else None")],
    # G61 sort_by of the empty array: the empty array (alt: null)
    "G61": [(FN, "        keys = _sort_keys(items, reference, \"sort_by\")",
             "        if not items:\n            return None\n        keys = _sort_keys(items, reference, \"sort_by\")")],
    # G69 options apply to their own search only (alt: a parsed expression keeps the last options it was given)
    "G69": [(AP, "        dict_cls = getattr(options, 'dict_cls', None)\n        provider = getattr(options, 'custom_functions', None)",
             "        if options is not None:\n            self._last = options\n        options = options if options is not None else getattr(self, '_last', None)\n"
             "        dict_cls = getattr(options, 'dict_cls', None)\n        provider = getattr(options, 'custom_functions', None)")],
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
