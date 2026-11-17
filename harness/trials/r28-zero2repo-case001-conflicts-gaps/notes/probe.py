"""Black-box probes: which side of each round-28 case001 item a built tomlparse takes. No model call.

    python3 probe.py <app dir>      -> one JSON object {item: "A" | "B" | "neither" | "error: ..."} on stdout
    (run through notes/probe.sh, in a container with no network)

For a conflict, A is the original spec's behaviour and B the planted sentence's; for a gap, A is the
removed fact (upstream) and B the alternative copy of notes/sides.py. Each probe uses only the public
surface of the Interface Contract (`loads`, `load`, `TOMLDecodeError`); written from the spec and the
answer key, never from the hidden tests.
"""
import datetime
import io
import json
import math
import sys

sys.path.insert(0, sys.argv[1] + "/src")
import tomlparse as t  # noqa: E402

P = {}


def probe(item):
    def deco(f):
        P[item] = f
        return f
    return deco


def ok_or_refused(text, want=None):
    """A if the text parses (and equals `want` when given), B if it is refused with the decode error."""
    try:
        r = t.loads(text)
    except t.TOMLDecodeError:
        return "B"
    if want is None or r == want:
        return "A"
    return "neither"


def err(text):
    try:
        t.loads(text)
    except t.TOMLDecodeError as e:
        return e
    return None


@probe("C01")
def _():
    return ok_or_refused('a = "\\e"', {"a": "\x1b"})


@probe("C02")
def _():
    return ok_or_refused('a = "\\x41"', {"a": "A"})


@probe("C03")
def _():
    return ok_or_refused("a = 07:32", {"a": datetime.time(7, 32)})


@probe("C04")
def _():
    r = t.loads("a = 07:32:00.1234567")["a"].microsecond
    return {123456: "A", 123457: "B"}.get(r, "neither")


@probe("C05")
def _():
    return ok_or_refused("a = {x = 1,}", {"a": {"x": 1}})


@probe("C06")
def _():
    return ok_or_refused("a = {\n  x = 1\n}", {"a": {"x": 1}})


@probe("C07")
def _():
    return ok_or_refused("a = [1, 2,]", {"a": [1, 2]})


@probe("C08")
def _():
    return ok_or_refused("a = -0\nb = +0", {"a": 0, "b": 0})


@probe("C09")
def _():
    try:
        r = t.loads("a = -nan")
    except t.TOMLDecodeError:
        return "B"
    return "A" if math.isnan(r["a"]) else "neither"


@probe("C10")
def _():
    r = t.loads('a = """\r\nx\r\ny"""')["a"]
    return {"x\ny": "A", "x\r\ny": "B"}.get(r, "neither")


@probe("C11")
def _():
    r = t.loads("a = '''\nx'''")["a"]
    return {"x": "A", "\nx": "B"}.get(r, "neither")


@probe("C12")
def _():
    r = t.loads('a = """x \\\n    y"""')["a"]
    return {"x y": "A", "x     y": "B"}.get(r, "neither")


@probe("C13")
def _():
    return ok_or_refused('a = """x"""""', {"a": 'x""'})


@probe("C14")
def _():
    return ok_or_refused('a = "x\ty"', {"a": "x\ty"})


@probe("C15")
def _():
    return ok_or_refused("a = 0xdead_beef", {"a": 0xDEADBEEF})


@probe("C16")
def _():
    return ok_or_refused("a = 0xDEAD", {"a": 0xDEAD})


@probe("C17")
def _():
    return ok_or_refused('a = "\\u00E9"', {"a": "é"})


@probe("C18")
def _():
    try:
        r = t.loads("a = 1979-05-27 07:32:00")["a"]
    except t.TOMLDecodeError:
        return "B"
    return "A" if r == datetime.datetime(1979, 5, 27, 7, 32) else "neither"


@probe("C19")
def _():
    try:
        r = t.loads("a = 1979-05-27T07:32:00z")["a"]
    except t.TOMLDecodeError:
        return "B"
    return "A" if r.utcoffset() == datetime.timedelta(0) else "neither"


@probe("C25")
def _():
    e = t.TOMLDecodeError("m", "ab\ncd", 4)
    return {2: "A", 1: "B"}.get(e.colno, "neither")


@probe("C28")
def _():
    try:
        r = t.loads("a = 1.5", parse_float=lambda s: (s,))
    except t.TOMLDecodeError:
        return "neither"
    except ValueError:
        return "B"
    return "A" if r == {"a": ("1.5",)} else "neither"


@probe("C29")
def _():
    class D(dict):
        pass
    try:
        t.loads("a = 1.5", parse_float=lambda s: D())
    except t.TOMLDecodeError:
        return "neither"
    except ValueError:
        return "A"
    return "B"


@probe("C35")
def _():
    return ok_or_refused('"" = 1', {"": 1})


@probe("C36")
def _():
    return ok_or_refused("[fruit]\napple.color = 'red'\n[fruit.apple.texture]\nsmooth = true",
                         {"fruit": {"apple": {"color": "red", "texture": {"smooth": True}}}})


@probe("G01")
def _():
    doc = "a = "
    e = err(doc)
    return "A" if e.pos == len(doc) else ("B" if e.pos < len(doc) else "neither")


@probe("G03")
def _():
    doc = "a = 1\n[a]\nb = 2"
    e = err(doc)
    start = doc.index("[a]")
    if start <= e.pos < start + 3:
        return "A"
    return "B" if e.pos >= start + 3 else "neither"


@probe("G04")
def _():
    seen = []
    t.loads("a = 1_000.5", parse_float=lambda s: seen.append(s) or 0)
    return {"1_000.5": "A", "1000.5": "B"}.get(seen[0] if seen else None, "neither")


@probe("G05")
def _():
    seen = []
    t.loads("a = inf", parse_float=lambda s: seen.append(s) or 0)
    return "A" if seen == ["inf"] else ("B" if not seen else "neither")


@probe("G09")
def _():
    n = 470
    try:
        r = t.loads("a = " + "[" * n + "]" * n)
    except t.TOMLDecodeError:
        return "B"
    return "A" if isinstance(r["a"], list) else "neither"


@probe("G13")
def _():
    try:
        r = t.load(io.BytesIO(b'a = "\xe9"'))
    except Exception:   # any exception: the call does not succeed (the Contract leaves its type open)
        return "A"
    return "B" if r == {"a": "é"} else "neither"


out = {}
for item, f in P.items():
    try:
        out[item] = f()
    except Exception as e:  # a probe that crashes reads neither side
        out[item] = "error: %s: %s" % (type(e).__name__, str(e)[:80])
print(json.dumps(out, sort_keys=True))
