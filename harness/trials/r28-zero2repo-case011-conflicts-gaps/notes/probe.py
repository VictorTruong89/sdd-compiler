"""Black-box probes: which side of each round-28 case011 item a built pathsel takes. No model call.

    python3 probe.py <app dir>      -> one JSON object {item: "A" | "B" | "neither" | "error: ..."} on stdout
    (run through notes/probe.sh, in a container with no network)

For a conflict, A is the original spec's behaviour and B the planted sentence's; for a gap, A is the
removed fact (upstream) and B the alternative copy of notes/sides.py. Each probe uses only the public
surface of the Interface Contract (`search`, `compile`, `Functions`, `signature`, options as any object
with `dict_cls` and `custom_functions`); written from the spec and the answer key, never from the hidden
tests. Failure kinds are told apart by the raised type, as the Contract fixes.
"""
import collections
import json
import sys
import types
from decimal import Decimal

sys.path.insert(0, sys.argv[1])
import pathsel as p  # noqa: E402
from pathsel.functions import Functions, signature  # noqa: E402

P = {}


def probe(item):
    def deco(f):
        P[item] = f
        return f
    return deco


def raises(expr, data=None):
    try:
        p.search(expr, data)
    except ValueError as e:
        return e
    return None


def ab(value, a, b):
    if value == a and type(value) is type(a):
        return "A"
    if value == b and type(value) is type(b):
        return "B"
    return "neither"


SYNTAX = type(raises("foo..bar", {}))          # grammar-level syntax type


def opts(dict_cls=None, custom=None):
    return types.SimpleNamespace(dict_cls=dict_cls, custom_functions=custom)


@probe("C01")
def _():
    return ab(p.search("avg(@)", []), None, 0)


@probe("C02")
def _():
    return ab(p.search("join(',', @)", []), "", None)


@probe("C03")
def _():
    return ab(p.search("merge(a, b)", {"a": {"k": 1}, "b": {"k": 2}})["k"], 2, 1)


@probe("C04")
def _():
    e = raises("max(@)", [])
    if e is None:
        return "A" if p.search("max(@)", []) is None and p.search("min(@)", []) is None else "neither"
    return "B" if e is not None and type(e) is not SYNTAX else "neither"


@probe("C05")
def _():
    return ab(p.search("not_null(a, b)", {"a": [], "b": 1}), [], 1)


@probe("C06")
def _():
    return ab(p.search("map(&x, @)", [{"x": 1}, {}, {"x": 3}]), [1, None, 3], [1, 3])


@probe("C07")
def _():
    d = [{"k": 1, "n": "first"}, {"k": 1, "n": "second"}]
    r = (p.search("max_by(@, &k).n", d), p.search("min_by(@, &k).n", d))
    return {("first", "first"): "A", ("second", "second"): "B"}.get(r, "neither")


@probe("C08")
def _():
    return ab(p.search("length(@)", "hé€"), 3, 6)


@probe("C09")
def _():
    return ab(p.search("a < b", {"a": "apple", "b": "banana"}), True, None)


@probe("C10")
def _():
    return ab(p.search("a < b", {"a": Decimal("1.5"), "b": 2}), True, None)


@probe("C11")
def _():
    r = p.search("{a: a, z: z}", {"a": 1})
    if r == {"a": 1, "z": None}:
        return "A"
    return "B" if r == {"a": 1} else "neither"


@probe("C12")
def _():
    return ab(p.search("[a, b]", None), None, [None, None])


@probe("C13")
def _():
    return ab(p.search("[5:9]", [1, 2, 3]), [], None)


@probe("C14")
def _():
    return ab(p.search("a[0:2]", {"a": {"x": 1}}), None, [])


@probe("C15")
def _():
    return ab(p.search("a[?b]", {"a": {"b": 1}}), None, [])


@probe("C16")
def _():
    return ab(p.search("a[*]", {"a": {"b": 1}}), None, [])


@probe("C17")
def _():
    return ab(p.search("a.*", {"a": [1, 2]}), None, [])


@probe("C18")
def _():
    return ab(p.search("a[0]", {"a": "xyz"}), None, "x")


@probe("C19")
def _():
    return ab(p.search("'\\u0041'", None), "\\u0041", "A")


@probe("C20")
def _():
    e = raises("[::0]", [1, 2])
    if e is None:
        return "B" if p.search("[::0]", [1, 2]) == [] else "neither"
    return "A" if not isinstance(e, SYNTAX) else "neither"


@probe("C21")
def _():
    e = raises('"length"(@)', "abc")
    if e is None:
        return "B" if p.search('"length"(@)', "abc") == 3 else "neither"
    return "A" if type(e) is SYNTAX else "neither"


@probe("C22")
def _():
    r = p.search("&a", {"a": 1})
    if r is None:
        return "B"
    return "A" if r != 1 and r != {"a": 1} else "neither"


@probe("C23")
def _():
    try:
        p.compile("no_such_fn(@)")
    except ValueError:
        return "B"
    return "A"


@probe("C24")
def _():
    e = raises("a = b", {})
    if e is None:
        return "neither"
    if type(e) is SYNTAX:
        return "B"
    return "A" if isinstance(e, SYNTAX) else "neither"


@probe("C25")
def _():
    e = raises("foo-bar", {})
    if e is None:
        return "neither"
    if type(e) is SYNTAX:
        return "B"
    return "A" if isinstance(e, SYNTAX) else "neither"


@probe("C26")
def _():
    return ab(p.search("to_number(@)", "42"), 42, 42.0)


@probe("C27")
def _():
    return ab(p.search("to_string(@)", ["é"]), '["\\u00e9"]', '["é"]')


@probe("G03")
def _():
    return ab(p.search("sort(@)", []), [], None)


@probe("G04")
def _():
    d = [{"k": 1, "n": "a"}, {"k": 0, "n": "b"}, {"k": 1, "n": "c"}]
    return ab(p.search("sort_by(@, &k)[*].n", d), ["b", "a", "c"], ["b", "c", "a"])


@probe("G07")
def _():
    return ab(p.search("to_string(@)", {"a": [1, 2]}), '{"a":[1,2]}', '{"a": [1, 2]}')


@probe("G22")
def _():
    return ab(p.search("a < b", {"a": 1, "b": None}), None, False)


@probe("G25")
def _():
    return ab(p.search("'a\\\\b'", None), "a\\\\b", "a\\b")


@probe("G27")
def _():
    class Thing:
        def __str__(self):
            return "thing"
    return ab(p.search("to_string(@)", Thing()), '"thing"', "thing")


@probe("G28")
def _():
    e = raises("abs(@)", Decimal("-2"))
    if e is None:
        return "B"
    return "A" if not isinstance(e, SYNTAX) else "neither"


@probe("G29")
def _():
    r = p.search("merge({a: `1`}, {b: `2`})", {}, opts(collections.OrderedDict))
    if type(r) is dict:
        return "A"
    return "B" if type(r) is collections.OrderedDict else "neither"


@probe("G34")
def _():
    r = p.search("{a: {b: `1`}}", {}, opts(collections.OrderedDict))
    t = (type(r), type(r["a"]))
    if t == (collections.OrderedDict, collections.OrderedDict):
        return "A"
    return "B" if t == (collections.OrderedDict, dict) else "neither"


@probe("G35")
def _():
    r = p.search("{z: `1`, a: `2`}", {})
    k = list(r.keys())
    return {("z", "a"): "A", ("a", "z"): "B"}.get(tuple(k), "neither")


@probe("G54")
def _():
    e = raises("`\"a\\`b\"`", None)
    if e is not None:
        return "B"
    r = p.search("`\"a\\`b\"`", None)
    return "A" if r == "a`b" else "neither"


@probe("G60")
def _():
    return ab(p.search("sum(@)", []), 0, None)


@probe("G61")
def _():
    return ab(p.search("sort_by(@, &k)", []), [], None)


@probe("G69")
def _():
    c = p.compile("{a: `1`}")
    c.search({}, opts(collections.OrderedDict))
    t = type(c.search({}))
    return "A" if t is dict else ("B" if t is collections.OrderedDict else "neither")


out = {}
for item, f in P.items():
    try:
        out[item] = f()
    except Exception as e:  # a probe that crashes reads neither side
        out[item] = "error: %s: %s" % (type(e).__name__, str(e)[:80])
print(json.dumps(out, sort_keys=True))
