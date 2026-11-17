"""Make one alternative copy of a built httpwire per candidate, for the footprint runs and the probe check.

    python3 notes/sides.py work/base-app work/sides [C01 ...]        (from the trial folder)

Round 28, case005 (new for this case; the method of ../r21-zero2repo-case016-conflicts-gaps/notes/sides.py).
Two kinds of candidate share one list:
  - C.. **conflict** candidates: the original spec states side A (the upstream behaviour); a planted
    sentence will state side B. The copy builds side B.
  - G.. **gap** candidates: a stated fact that may be removed from the spec. The copy builds a plausible
    alternative an agent could invent once the fact is gone.
The base build (round 13b `haiku-case005-1`, 395 / 395 on round 13b's task and on this round's
`case005-markdown-orig`) takes the upstream value on every candidate; each patch is the smallest change
that moves that one behaviour. Every anchor must occur exactly once, so a patch never applies silently
to the wrong place. Writes work/sides/<id>/ (a full copy) and work/sides/<id>.tgz, plus
work/sides/BASE.tgz. Written from the spec and the base code only, never from the hidden tests (only
their names were read).
"""
import shutil
import sys
import tarfile
from pathlib import Path

CN, EV, HD, UT = "httpwire/_connection.py", "httpwire/_events.py", "httpwire/_headers.py", "httpwire/_util.py"

PATCHES = {
    # ---- conflicts: side B built
    # C01 Content-Length: every value of up to 18 digits accepted (A) -> more than 16 digits refused (B)
    "C01": [(HD, "MAX_CONTENT_LENGTH_DIGITS = 18", "MAX_CONTENT_LENGTH_DIGITS = 16")],
    # C02 chunk-size line: at most 16-32 hex digits (A; base 20) -> up to 64 accepted (B)
    "C02": [(CN, "MAX_CHUNK_SIZE_DIGITS = 20", "MAX_CHUNK_SIZE_DIGITS = 64")],
    # C03 default incomplete-event limit 14-18 KiB (A; base 16) -> 8 KiB (B)
    "C03": [(CN, "DEFAULT_MAX_INCOMPLETE_EVENT_SIZE = 16 * 1024", "DEFAULT_MAX_INCOMPLETE_EVENT_SIZE = 8 * 1024")],
    # C04 obsolete line folding joined when reading (A) -> refused as a remote protocol error (B)
    "C04": [(CN, '            if not pairs:\n                raise RemoteProtocolError("header continuation line with no header")',
             '            if True:\n                raise RemoteProtocolError("obsolete line folding is refused")')],
    # C05 lone LF line endings accepted (A) -> refused (B)
    "C05": [(CN, "            line = bytes(buf[pos:newline])\n            if line.endswith(b\"\\r\"):\n                line = line[:-1]",
             "            line = bytes(buf[pos:newline])\n            if not line.endswith(b\"\\r\"):\n"
             "                raise RemoteProtocolError(\"line ending without carriage return\")\n            line = line[:-1]")],
    # C06 status line without a reason phrase accepted (A) -> refused (B)
    "C06": [(CN, '_STATUS_LINE_RE = re.compile(rb"HTTP/([0-9]\\.[0-9]) ([0-9]{3})(?: (.*))?")',
             '_STATUS_LINE_RE = re.compile(rb"HTTP/([0-9]\\.[0-9]) ([0-9]{3}) (.*)")')],
    # C07 Host written first when encoding a request (A) -> caller's order (B)
    "C07": [(CN, "    return line + _header_lines(host + rest) + b\"\\r\\n\"", "    return line + _header_lines(pairs) + b\"\\r\\n\"")],
    # C08 original name casing written (A) -> lowercase names written (B)
    "C08": [(CN, 'return b"".join(name + b": " + value + b"\\r\\n" for name, value in pairs)',
             'return b"".join(name.lower() + b": " + value + b"\\r\\n" for name, value in pairs)')],
    # C09 spaces or tabs after the chunk size accepted (A) -> refused (B)
    "C09": [(CN, '_CHUNK_SIZE_RE = re.compile(rb"([0-9A-Fa-f]+)(?:;.*)?[ \\t]*")', '_CHUNK_SIZE_RE = re.compile(rb"([0-9A-Fa-f]+)(?:;.*)?")')],
    # C10 response with both Transfer-Encoding: chunked and Content-Length: transfer-encoding wins (A) -> Content-Length wins (B)
    "C10": [(CN, "            if has_cl and not has_te:\n                choice = \"length\"",
             "            if has_cl:\n                choice = \"length\"\n"
             "                pairs = [p for p in pairs if p[0].lower() != b\"transfer-encoding\"]"),
            (CN, "    if method == b\"HEAD\" or status in (204, 304):\n        return _Framing(\"empty\")\n    if headers.get_all(b\"transfer-encoding\"):\n        return _Framing(\"chunked\")\n    lengths = headers.get_all(b\"content-length\")\n    if lengths:\n        return _Framing(\"length\", int(lengths[0]))\n    return _Framing(\"close\")",
             "    if method == b\"HEAD\" or status in (204, 304):\n        return _Framing(\"empty\")\n    lengths = headers.get_all(b\"content-length\")\n    if lengths:\n        return _Framing(\"length\", int(lengths[0]))\n    if headers.get_all(b\"transfer-encoding\"):\n        return _Framing(\"chunked\")\n    return _Framing(\"close\")")],
    # C11 a response's Content-Length is kept on the wire, also when 0 (A) -> Content-Length: 0 is left out (B)
    "C11": [(CN, "            if has_cl and not has_te:\n                choice = \"length\"",
             "            if has_cl and not has_te:\n                choice = \"length\"\n"
             "                pairs = [p for p in pairs if not (p[0].lower() == b\"content-length\" and int(p[1]) == 0)]")],
    # C12 Connection token close matched as a whole element (A) -> anywhere in the value (B)
    "C12": [(CN, "                token = piece.strip(b\" \\t\").lower()\n                if token:\n                    tokens.add(token)",
             "                token = piece.strip(b\" \\t\").lower()\n                if token:\n                    tokens.add(token)\n"
             "                if lower_name == b\"connection\" and b\"close\" in token:\n                    tokens.add(b\"close\")")],
    # C13 Expect: 100-continue on an HTTP/1.0 request sets no flag (A) -> sets the flags on any version (B)
    "C13": [(CN, 'if event.http_version == b"1.1" and b"100-continue" in _tokens(event.headers, b"expect"):',
             'if b"100-continue" in _tokens(event.headers, b"expect"):')],
    # C14 the 100-continue token is matched case-insensitively (A) -> exactly, lowercase (B)
    "C14": [(CN, 'if event.http_version == b"1.1" and b"100-continue" in _tokens(event.headers, b"expect"):',
             'if event.http_version == b"1.1" and b"100-continue" in [p.strip(b" \\t") for n, v in event.headers '
             'if n == b"expect" for p in v.split(b",")]:')],
    # C15 a client data event or end-of-message clears the waiting flags (A) -> only the server's response does (B)
    "C15": [(CN, "        elif kind is Data:\n            if sender is CLIENT:\n                self._client_waiting = False",
             "        elif kind is Data:\n            if False:\n                self._client_waiting = False"),
            (CN, "        elif kind is EndOfMessage:\n            if sender is CLIENT:\n                self._client_waiting = False",
             "        elif kind is EndOfMessage:\n            if False:\n                self._client_waiting = False")],
    # C16 CONNECT accepted by any 2xx final response (A) -> only by 200 (B)
    "C16": [(CN, "if _CONNECT in self._pending and 200 <= event.status_code < 300:", "if _CONNECT in self._pending and event.status_code == 200:")],
    # C17 incomplete-event limit exceeded suggests 431 (A) -> 413 (B)
    "C17": [(CN, '                    raise RemoteProtocolError(\n                        "incomplete event exceeds the size limit", 431\n                    )',
             '                    raise RemoteProtocolError(\n                        "incomplete event exceeds the size limit", 413\n                    )'),
            (CN, 'raise RemoteProtocolError("incomplete event exceeds the size limit", 431)',
             'raise RemoteProtocolError("incomplete event exceeds the size limit", 413)')],
    # C18 a second Transfer-Encoding header is refused even when both are chunked (A) -> accepted when all are chunked (B)
    "C18": [(HD, '    if len(te_positions) > 1:\n        raise LocalProtocolError("more than one Transfer-Encoding header", 501)',
             '    if len(te_positions) > 1 and any(triples[i][2].lower() != b"chunked" for i in te_positions):\n'
             '        raise LocalProtocolError("more than one Transfer-Encoding header", 501)\n'
             '    if len(te_positions) > 1:\n'
             '        triples = [t for i, t in enumerate(triples) if i not in te_positions[1:]]\n'
             '        te_positions = te_positions[:1]')],
    # C19 a server in IDLE may send a final response with no request (A) -> refused (B)
    "C19": [(CN, "        if kind is Response:\n            if state is IDLE:\n                return SEND_BODY",
             "        if kind is Response:\n            if state is IDLE:\n                return None")],
    # C20 header values may hold control bytes other than NUL CR LF FF VT (A) -> every control byte but tab refused (B)
    "C20": [(HD, '_BAD_VALUE_RE = re.compile(rb"[\\x00\\r\\n\\x0b\\x0c]")', '_BAD_VALUE_RE = re.compile(rb"[\\x00-\\x08\\x0a-\\x1f\\x7f]")')],
    # C21 a response to HEAD gets the framing headers GET would get (A) -> no framing headers (B)
    "C21": [(CN, "        choice = None\n        if status not in (204, 304):", "        choice = None\n        if status not in (204, 304) and self._request_method != b\"HEAD\":")],
    # ---- gaps: plausible alternative built
    # G01 default suggested status 400 -> 500
    "G01": [(UT, "    def __init__(self, msg, error_status_hint=400):", "    def __init__(self, msg, error_status_hint=500):")],
    # G03 HTTP/1.0 Connection: keep-alive is not honoured -> honoured
    "G03": [(CN, '            if event.http_version != b"1.1" or b"close" in _tokens(event.headers, b"connection"):\n                self._keep_alive = False',
             '            if (event.http_version != b"1.1" and b"keep-alive" not in _tokens(event.headers, b"connection")) '
             'or b"close" in _tokens(event.headers, b"connection"):\n                self._keep_alive = False'),
            (CN, '                if (\n                    event.http_version != b"1.1"\n                    or b"close" in _tokens(event.headers, b"connection")',
             '                if (\n                    (event.http_version != b"1.1" and b"keep-alive" not in _tokens(event.headers, b"connection"))\n'
             '                    or b"close" in _tokens(event.headers, b"connection")')],
    # G05 a space or control byte where a start line is expected fails at once -> waits for a line ending
    "G05": [(CN, '        if buf[0] < 33:\n            raise RemoteProtocolError("request must start with a method token")\n', ""),
            (CN, '        if buf[0] < 33:\n            raise RemoteProtocolError("status line must not start with a space or control byte")\n', "")],
    # G06 bytes held while paused are not counted against the limit -> counted
    "G06": [(CN, "        if state is DONE and buf:\n            return PAUSED",
             "        if state is DONE and buf:\n            if len(buf) > self._max_incomplete:\n"
             "                raise RemoteProtocolError(\"incomplete event exceeds the size limit\", 431)\n            return PAUSED")],
    # G07 framed body bytes never count against the limit -> counted
    "G07": [(CN, "        if fr.mode == \"length\":\n            if not buf:\n                return self._need_more()",
             "        if fr.mode == \"length\":\n            if len(buf) > self._max_incomplete:\n"
             "                raise RemoteProtocolError(\"incomplete event exceeds the size limit\", 431)\n"
             "            if not buf:\n                return self._need_more()")],
    # G08 the whole unfinished line plus headers counts -> only the unfinished line counts
    "G08": [(CN, "            if newline < 0:\n                if len(buf) > self._max_incomplete:\n                    raise RemoteProtocolError(\n",
             "            if newline < 0:\n                if len(buf) - pos > self._max_incomplete:\n                    raise RemoteProtocolError(\n")],
    # G09 an empty data event on a chunked body encodes as no bytes -> as a zero-size chunk
    "G09": [(CN, "            if size == 0:\n                return [], event\n            return [b\"%x\\r\\n\" % size",
             "            if size == 0:\n                return [b\"0\\r\\n\\r\\n\"], event\n            return [b\"%x\\r\\n\" % size")],
    # G14 feeding further empty chunks after the close never fails -> a second empty chunk raises
    "G14": [(CN, "        if view.nbytes == 0:\n            self._receive_closed = True",
             "        if view.nbytes == 0:\n            if self._receive_closed:\n"
             "                raise RuntimeError(\"the peer already closed its side\")\n            self._receive_closed = True")],
    # G16 the peer HTTP version stays after the next cycle starts -> reset
    "G16": [(CN, "        self._client_waiting = False\n        return None", "        self._client_waiting = False\n        self._their_http_version = None\n        return None")],
    # G21 the product never invents a reason phrase -> standard phrase written when none is given
    "G21": [(CN, '    line = b"HTTP/1.1 %d %s\\r\\n" % (event.status_code, event.reason)',
             '    phrases = {100: b"Continue", 101: b"Switching Protocols", 200: b"OK", 201: b"Created", 204: b"No Content",\n'
             '               304: b"Not Modified", 400: b"Bad Request", 404: b"Not Found", 408: b"Request Timeout",\n'
             '               500: b"Internal Server Error"}\n'
             '    line = b"HTTP/1.1 %d %s\\r\\n" % (event.status_code, event.reason or phrases.get(event.status_code, b""))')],
    # G22 bytes from a peer in MUST_CLOSE are a remote protocol error -> held (paused)
    "G22": [(CN, '        if state is MUST_CLOSE and buf:\n            raise RemoteProtocolError("peer sent data after committing to close")',
             "        if state is MUST_CLOSE and buf:\n            return PAUSED")],
    # G31 when keep-alive is disabled the added Connection: close drops a keep-alive token -> keeps it
    "G31": [(CN, "            conn_tokens = [t for t in conn_tokens if t and t.lower() != b\"keep-alive\"]",
             "            conn_tokens = [t for t in conn_tokens if t]")],
    # G33 marking a send as failed twice has the same result -> the second call is refused
    "G33": [(CN, "    def send_failed(self):\n        self._mark_error(self._our_role)",
             "    def send_failed(self):\n        if self._states[self._our_role] is ERROR:\n"
             "            raise LocalProtocolError(\"send already marked as failed\")\n        self._mark_error(self._our_role)")],
    # G34 sending connection-closed again when CLOSED is allowed -> refused
    "G34": [(CN, "            if state in (IDLE, DONE, MUST_CLOSE, CLOSED):\n                return CLOSED",
             "            if state in (IDLE, DONE, MUST_CLOSE):\n                return CLOSED")],
    # G47 header order kept as the caller gave it -> Host moved first at construction
    "G47": [(HD, "        self._items = tuple(_normalize(headers))",
             "        items = _normalize(headers)\n        self._items = tuple([t for t in items if t[1] == b\"host\"] + "
             "[t for t in items if t[1] != b\"host\"])")],
    # G48 whitespace around the commas of a Content-Length list is allowed -> refused
    "G48": [(HD, "                piece = piece.strip(_OWS)\n", "")],
    # G49 an integer-valued enumeration status is stored as a plain int -> stored as given
    "G49": [(EV, "    return code\n", "    return value\n")],
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
