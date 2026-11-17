"""Black-box probes: which side of each round-28 case005 item a built httpwire takes. No model call.

    python3 probe.py <app dir>      -> one JSON object {item: "A" | "B" | "neither" | "error: ..."} on stdout
    (run through notes/probe.sh, in a container with no network)

For a conflict, A is the original spec's behaviour and B the planted sentence's; for a gap, A is the
removed fact (upstream) and B the alternative copy of notes/sides.py. Each probe uses only the public
surface of the Interface Contract; written from the spec and the answer key, never from the hidden tests.
"""
import json
import sys

sys.path.insert(0, sys.argv[1])
import httpwire as h  # noqa: E402

H = [("Host", "a")]


def server_with(raw, size=None):
    c = h.Connection(h.SERVER) if size is None else h.Connection(h.SERVER, size)
    c.receive_data(raw)
    return c


def client_sent(req, size=None):
    c = h.Connection(h.CLIENT) if size is None else h.Connection(h.CLIENT, size)
    c.send(req)
    return c


def b(x):
    return bytes(x) if x is not None else b""


def pulls(c, n=8):
    out = []
    for _ in range(n):
        e = c.next_event()
        out.append(e)
        if e is h.NEED_DATA or e is h.PAUSED:
            break
    return out


def raises(f, exc=Exception):
    try:
        f()
    except exc:
        return True
    return False


def full_get_cycle(version=b"1.1", extra=b""):
    c = server_with(b"GET / HTTP/" + version + b"\r\nHost: a\r\n" + extra + b"\r\n")
    pulls(c)
    c.send(h.Response(status_code=200, headers=[("Content-Length", "2")]))
    c.send(h.Data(data=b"ok"))
    c.send(h.EndOfMessage())
    return c


P = {}


def probe(item):
    def deco(f):
        P[item] = f
        return f
    return deco


@probe("C01")
def _():
    return "B" if raises(lambda: h.Request(method="GET", target="/", headers=H + [("Content-Length", "1" * 17)]), h.LocalProtocolError) else "A"


@probe("C02")
def _():
    c = server_with(b"POST / HTTP/1.1\r\nHost: a\r\nTransfer-Encoding: chunked\r\n\r\n" + b"0" * 39 + b"1\r\nx\r\n0\r\n\r\n")
    try:
        ev = pulls(c)
    except h.RemoteProtocolError:
        return "A"
    return "B" if any(isinstance(e, h.Data) and e.data == b"x" for e in ev) else "neither"


@probe("C03")
def _():
    c = server_with(b"GET / HTTP/1.1\r\nHost: a\r\nX: " + b"a" * 12000)
    try:
        return "A" if c.next_event() is h.NEED_DATA else "neither"
    except h.RemoteProtocolError:
        return "B"


@probe("C04")
def _():
    c = server_with(b"GET / HTTP/1.1\r\nHost: a\r\nX: b\r\n c\r\n\r\n")
    try:
        ev = c.next_event()
    except h.RemoteProtocolError:
        return "B"
    return "A" if (b"x", b"b c") in list(ev.headers) else "neither"


@probe("C05")
def _():
    c = client_sent(h.Request(method="GET", target="/", headers=H))
    c.receive_data(b"HTTP/1.1 200 OK\nContent-Length: 0\n\n")
    try:
        ev = c.next_event()
    except h.RemoteProtocolError:
        return "B"
    return "A" if isinstance(ev, h.Response) and ev.status_code == 200 else "neither"


@probe("C06")
def _():
    c = client_sent(h.Request(method="GET", target="/", headers=H))
    c.receive_data(b"HTTP/1.1 200\r\nContent-Length: 0\r\n\r\n")
    try:
        ev = c.next_event()
    except h.RemoteProtocolError:
        return "B"
    return "A" if isinstance(ev, h.Response) and ev.reason == b"" else "neither"


@probe("C07")
def _():
    out = b(h.Connection(h.CLIENT).send(h.Request(method="GET", target="/", headers=[("Foo", "1"), ("Host", "a")]))).lower()
    i, j = out.find(b"host:"), out.find(b"foo:")
    return "A" if 0 <= i < j else ("B" if 0 <= j < i else "neither")


@probe("C08")
def _():
    out = b(h.Connection(h.CLIENT).send(h.Request(method="GET", target="/", headers=[("Host", "a"), ("X-Foo", "1")])))
    return "A" if b"X-Foo: 1" in out else ("B" if b"x-foo: 1" in out else "neither")


@probe("C09")
def _():
    c = server_with(b"POST / HTTP/1.1\r\nHost: a\r\nTransfer-Encoding: chunked\r\n\r\n5 \r\nhello\r\n0\r\n\r\n")
    try:
        ev = pulls(c)
    except h.RemoteProtocolError:
        return "B"
    return "A" if any(isinstance(e, h.Data) and e.data == b"hello" for e in ev) else "neither"


@probe("C10")
def _():
    c = server_with(b"GET / HTTP/1.1\r\nHost: a\r\n\r\n")
    pulls(c)
    out = b(c.send(h.Response(status_code=200, headers=[("Transfer-Encoding", "chunked"), ("Content-Length", "5")]))).lower()
    if b"transfer-encoding: chunked" in out and b"content-length" not in out:
        return "A"
    if b"content-length: 5" in out and b"transfer-encoding" not in out:
        return "B"
    return "neither"


@probe("C11")
def _():
    c = server_with(b"GET / HTTP/1.1\r\nHost: a\r\n\r\n")
    pulls(c)
    out = b(c.send(h.Response(status_code=200, headers=[("Content-Length", "0")]))).lower()
    return "A" if b"content-length: 0" in out else "B"


@probe("C12")
def _():
    c = server_with(b"GET / HTTP/1.1\r\nHost: a\r\nConnection: foo-close\r\n\r\n")
    pulls(c)
    out = b(c.send(h.Response(status_code=200, headers=[("Content-Length", "0")]))).lower()
    return "B" if b"connection: close" in out else "A"


@probe("C13")
def _():
    c = server_with(b"POST / HTTP/1.0\r\nExpect: 100-continue\r\nContent-Length: 1\r\n\r\n")
    c.next_event()
    return "B" if c.they_are_waiting_for_100_continue else "A"


@probe("C14")
def _():
    c = server_with(b"POST / HTTP/1.1\r\nHost: a\r\nExpect: 100-Continue\r\nContent-Length: 1\r\n\r\n")
    c.next_event()
    return "A" if c.they_are_waiting_for_100_continue else "B"


@probe("C15")
def _():
    c = client_sent(h.Request(method="POST", target="/", headers=H + [("Expect", "100-continue"), ("Content-Length", "2")]))
    if not c.client_is_waiting_for_100_continue:
        return "neither"
    c.send(h.Data(data=b"x"))
    return "A" if not c.client_is_waiting_for_100_continue else "B"


@probe("C16")
def _():
    c = client_sent(h.Request(method="CONNECT", target="a:443", headers=H))
    c.send(h.EndOfMessage())
    c.receive_data(b"HTTP/1.1 201 Created\r\n\r\n")
    c.next_event()
    return "A" if c.our_state is h.SWITCHED_PROTOCOL else "B"


@probe("C17")
def _():
    c = server_with(b"GET / HTTP/1.1\r\nHost: a\r\nX: " + b"a" * 300, 100)
    try:
        c.next_event()
    except h.RemoteProtocolError as e:
        return {431: "A", 413: "B"}.get(e.error_status_hint, "neither")
    return "neither"


@probe("C18")
def _():
    try:
        h.Request(method="POST", target="/", headers=H + [("Transfer-Encoding", "chunked"), ("Transfer-Encoding", "chunked")])
    except h.LocalProtocolError:
        return "A"
    return "B"


@probe("C19")
def _():
    try:
        h.Connection(h.SERVER).send(h.Response(status_code=408, headers=[]))
    except h.LocalProtocolError:
        return "B"
    return "A"


@probe("C20")
def _():
    try:
        h.Request(method="GET", target="/", headers=H + [("X", b"a\x01b")])
    except h.LocalProtocolError:
        return "B"
    return "A"


@probe("C21")
def _():
    c = server_with(b"HEAD / HTTP/1.1\r\nHost: a\r\n\r\n")
    pulls(c)
    out = b(c.send(h.Response(status_code=200, headers=[]))).lower()
    return "A" if b"transfer-encoding: chunked" in out else "B"


@probe("G01")
def _():
    try:
        h.Request(method="GET", target="/", headers=[])
    except h.LocalProtocolError as e:
        return {400: "A", 500: "B"}.get(e.error_status_hint, "neither")
    return "neither"


@probe("G03")
def _():
    c = full_get_cycle(b"1.0", b"Connection: keep-alive\r\n")
    return "A" if c.our_state is h.MUST_CLOSE else ("B" if c.our_state is h.DONE else "neither")


@probe("G05")
def _():
    c = server_with(b"\x16\x03\x01")
    try:
        return "B" if c.next_event() is h.NEED_DATA else "neither"
    except h.RemoteProtocolError:
        return "A"


@probe("G06")
def _():
    c = server_with(b"GET / HTTP/1.1\r\nHost: a\r\n\r\n", 100)
    pulls(c)
    c.send(h.Response(status_code=200, headers=[("Content-Length", "2")]))
    c.send(h.Data(data=b"ok"))
    c.send(h.EndOfMessage())
    c.receive_data(b"GET / HTTP/1.1\r\nX: " + b"a" * 200)
    try:
        return "A" if c.next_event() is h.PAUSED else "neither"
    except h.RemoteProtocolError:
        return "B"


@probe("G07")
def _():
    c = server_with(b"POST / HTTP/1.1\r\nHost: a\r\nContent-Length: 300\r\n\r\n" + b"x" * 300, 100)
    try:
        ev = pulls(c)
    except h.RemoteProtocolError:
        return "B"
    return "A" if any(isinstance(e, h.Data) for e in ev) else "neither"


@probe("G08")
def _():
    c = server_with(b"GET / HTTP/1.1\r\nA: " + b"a" * 50 + b"\r\nB: " + b"b" * 50 + b"\r\n", 100)
    try:
        return "B" if c.next_event() is h.NEED_DATA else "neither"
    except h.RemoteProtocolError:
        return "A"


@probe("G09")
def _():
    c = client_sent(h.Request(method="POST", target="/", headers=H + [("Transfer-Encoding", "chunked")]))
    out = b(c.send(h.Data(data=b"")))
    return "A" if out == b"" else ("B" if out.startswith(b"0\r\n") else "neither")


@probe("G14")
def _():
    c = h.Connection(h.SERVER)
    c.receive_data(b"")
    try:
        c.receive_data(b"")
    except Exception:
        return "B"
    return "A"


@probe("G16")
def _():
    c = server_with(b"GET / HTTP/1.1\r\nHost: a\r\n\r\n")
    pulls(c)
    c.send(h.Response(status_code=200, headers=[("Content-Length", "2")]))
    c.send(h.Data(data=b"ok"))
    c.send(h.EndOfMessage())
    c.start_next_cycle()
    v = c.their_http_version
    return "A" if v in (b"1.1", "1.1") else "B"


@probe("G21")
def _():
    c = server_with(b"GET / HTTP/1.1\r\nHost: a\r\n\r\n")
    pulls(c)
    out = b(c.send(h.Response(status_code=200, headers=[("Content-Length", "0")])))
    line = out.split(b"\r\n", 1)[0]
    return "A" if line.rstrip() == b"HTTP/1.1 200" else ("B" if line.startswith(b"HTTP/1.1 200 ") and line.rstrip() != b"HTTP/1.1 200" else "neither")


@probe("G22")
def _():
    c = full_get_cycle(b"1.0")
    c.receive_data(b"GET / HTTP/1.1\r\nHost: a\r\n\r\n")
    try:
        e = c.next_event()
    except h.RemoteProtocolError:
        return "A"
    return "B" if e is h.PAUSED else "neither"


@probe("G31")
def _():
    c = server_with(b"GET / HTTP/1.1\r\nHost: a\r\nConnection: close\r\n\r\n")
    pulls(c)
    out = b(c.send(h.Response(status_code=200, headers=[("Connection", "keep-alive"), ("Content-Length", "0")]))).lower()
    return "B" if b"keep-alive" in out else "A"


@probe("G33")
def _():
    c = h.Connection(h.CLIENT)
    c.send_failed()
    try:
        c.send_failed()
    except Exception:
        return "B"
    return "A" if c.our_state is h.ERROR else "neither"


@probe("G34")
def _():
    c = h.Connection(h.CLIENT)
    c.send(h.ConnectionClosed())
    try:
        c.send(h.ConnectionClosed())
    except h.LocalProtocolError:
        return "B"
    return "A"


@probe("G47")
def _():
    r = h.Request(method="GET", target="/", headers=[("Foo", "1"), ("Host", "a")])
    first = list(r.headers)[0][0]
    return "A" if first == b"foo" else ("B" if first == b"host" else "neither")


@probe("G48")
def _():
    try:
        h.Request(method="GET", target="/", headers=H + [("Content-Length", "0, 0")])
    except h.LocalProtocolError:
        return "B"
    return "A"


@probe("G49")
def _():
    import enum

    class S(enum.IntEnum):
        OK = 200
    r = h.Response(status_code=S.OK, headers=[])
    return "A" if type(r.status_code) is int else "B"


out = {}
for item, f in P.items():
    try:
        out[item] = f()
    except Exception as e:  # a probe that crashes reads neither side
        out[item] = "error: %s: %s" % (type(e).__name__, str(e)[:80])
print(json.dumps(out, sort_keys=True))
