# httpwire: build notes

httpwire is a pure-Python, bring-your-own-I/O HTTP/1.1 wire library. The code is the flat package
`httpwire/` at the repository root, built from `spec/` (`spec/MAP.md`, `spec/CHECKLIST.md`, and the
packs in `spec/packs/`). `spec/` is unchanged.

## Layout

| Path | Contents |
| --- | --- |
| `httpwire/__init__.py` | Public surface (the names in `__all__`). |
| `httpwire/_connection.py` | `Connection`: send, receive, pull, state machine, framing, switches. |
| `httpwire/_events.py` | The six event types. |
| `httpwire/_headers.py` | Header list container and normalization (Content-Length, Transfer-Encoding). |
| `httpwire/_state.py` | Role, state and sentinel objects (distinct identity objects). |
| `httpwire/_errors.py` | `LocalProtocolError`, `RemoteProtocolError`, `ReceiveClosedError`. |
| `pyproject.toml` | setuptools metadata: flat layout, `requires-python >= 3.8`, zero dependencies. |
| `tests/` | `unittest`-style tests, runnable with `python3 -m pytest tests` or `python3 -m unittest`. |
| `tools/spec_trace.py` | Builds `TRACEABILITY.md` from `# spec:` markers; `--check` verifies coverage. |
| `TRACEABILITY.md` | Each of N-000001..N-000522 with its implementation and test marker locations. |

## Status

- All 522 checklist ids carry an implementation marker (`# spec:` beside the code or docstring that
  carries the behaviour) and a test marker. `python3 tools/spec_trace.py --check` reports zero
  missing ids.
- Test run: `python3 -m pytest tests` gives 146 passed on Python 3.13.18.
- Not run here: Python 3.8 through 3.12 and PyPy (no interpreter for them in this environment); macOS
  and Windows (N-000042, N-000420). The code avoids syntax newer than 3.8 (no walrus, no
  `removeprefix`, no PEP 585 generics), but this was checked by reading, not by running on 3.8.
- No acceptance criteria exist in this spec (`AC: 0` in every pack), so tests are named by
  behaviour and carry `# spec: <id>` comments instead of `test_AC_...` names.

## Unsettled contradictions (19) and what was built

The export lists 19 unsettled contradictions (`--allow-open`). Each is treated as an open question
and settled below. Quotes are from the pack and claim named in brackets.

1. **CF-000003: framing when both Content-Length and Transfer-Encoding are present.**
   Side A, Content-Length decides [N-000096, pack 14, FP-01]: "When an event carries both framing
   headers, the `Content-Length` decides how the body is framed." Side B, transfer-encoding wins
   [N-000207, pack 16, FP-03]: "If a response is constructed with both ... transfer-encoding wins."
   *Built:* for requests (sent or pulled) and for trailers, Content-Length decides and any
   Transfer-Encoding is left off the wire when sending. For responses, Transfer-Encoding wins and
   Content-Length is not sent (the more specific statement).

2. **CF-000005: response status line with no reason phrase.**
   Side A, accepted [N-000166, pack 15, FP-02]: "A response status line that omits the reason phrase
   is accepted and the reason is empty." Side B, illegal [N-000516, pack 08, `next_event()`]: "A
   received status line with no reason phrase after its status code is illegal."
   *Built:* accepted, reason empty. `HTTP/1.1 200OK` (no space) is refused.

3. **CF-000026: other control bytes in header values.**
   Side A [N-000097, pack 14]: values may contain "other control bytes and non-ASCII bytes". Side B
   [N-000108, pack 14]: "Control bytes other than tab are refused in header values."
   *Built:* tab, printable ASCII and bytes 0x80..0xFF are allowed. NUL, the other C0 controls, and DEL
   are refused.

4. **CF-000048: default incomplete-event size limit.**
   Side A [N-000317, pack 18, FP-05]: the default is "at least 14 kibibytes and less than 18
   kibibytes". Side B [N-000479, pack 08, `Connection(...)` signature]: "When it is omitted, the
   limit is 8 kibibytes."
   *Built:* 8 KiB (8192 bytes) when the argument is omitted, because the interface states the value
   for that exact case. Consequence: an unfinished head over 8 KiB gets a 431 by default. A caller
   who wants 14-18 KiB passes `max_incomplete_event_size` explicitly.

5. **CF-000050: framing headers on a response to HEAD.**
   Side A [N-000137, pack 15, FP-02]: "A response to HEAD is written with no framing headers." Side B
   [N-000219, pack 16, FP-03]: "A server answering HEAD writes the same framing headers it would have
   used for GET."
   *Built:* side B. Framing headers match what GET would get (chunked for an HTTP/1.1 peer; no framing
   headers plus `Connection: close` for an HTTP/1.0 or unknown peer; a caller's Content-Length is kept).
   The body is always empty, so the end-of-message emits no bytes.

6. **CF-000074: lone line feed as a line ending.**
   Side A [N-000165, pack 15, FP-02]: lone-LF and mixed header block endings "are accepted". Side B
   [N-000510, pack 08]: "every received line must end with a carriage return and line feed."
   *Built:* side A for request, status, header and chunk-size lines (LF or CRLF). The chunk-data
   terminator stays strict CRLF, as N-000245 says ("must be exactly CRLF").

7. **CF-000075, CF-000076, CF-000100: obsolete line folding.**
   Side A [N-000167..N-000169, pack 15]: folding "is accepted when reading headers"; each continuation
   is joined to the previous value with leading whitespace replaced by a single space. Side B
   [N-000176, pack 15]: "A continuation line ... is refused."
   *Built:* side A. A continuation line is joined. Side B's refusal applies only to a continuation line
   with no header before it.

8. **CF-000083: `Expect: 100-continue` on an HTTP/1.0 request.**
   Side A [N-000357, pack 20, FP-07]: such a header "does not set either flag". Side B [N-000491,
   pack 08]: sets `client_is_waiting_for_100_continue` "whatever its HTTP version".
   *Built:* side A. Only HTTP/1.1 requests set the waiting flags.

9. **CF-000098: maximum Content-Length digit count.**
   Side A [N-000116, pack 14, FP-01]: "Every value of at most 18 digits is accepted; the maximum digit
   count ... from 18 to 32 inclusive." Side B [N-000462, pack 06]: "A `Content-Length` value longer than
   16 digits is refused."
   *Built:* 18 digits. Side B's 16 is outside the range side A allows. Values of up to 18 digits are
   accepted, 19 or more are refused.

10. **CF-000099: chunk-size digit count.**
    Side A [N-000194, pack 16]: "A received size line may carry up to 64 hexadecimal digits." Side B
    [N-000228, pack 16]: "from 16 to 32 inclusive."
    *Built:* 32 hex digits maximum (inside side B's range). Longer size lines are refused.

11. **CF-000101: whitespace after the chunk size.**
    Side A [N-000230, pack 16]: the size line may be "optionally followed by spaces or tabs, then the
    line ending." Side B [N-000243, pack 16]: "Whitespace after the chunk size is refused."
    *Built:* side B. `3 \r\n` is a remote protocol error. Anything after `;` (the extension) is
    discarded, as N-000231 says.

12. **CF-000102: `Content-Length: 0` on a response.**
    Side A [N-000199, pack 16]: the header "is kept on the wire, including when N is 0." Side B
    [N-000218, pack 16]: such a response "is sent without that header."
    *Built:* side A for ordinary and HEAD responses. Side B's rule is applied only to 204 and 304, where
    the body is always empty and the product drops Content-Length and Transfer-Encoding from the wire.

13. **CF-000103: which `Connection` values turn keep-alive off.**
    Side A [N-000021, pack 10, Keep-alive term]: "Any `Connection` value that contains `close` turns it
    off." Side B [N-000262, pack 17]: "as a whole element of the comma-separated `Connection` value."
    *Built:* side B. `Connection: closed-later` does not turn keep-alive off.

14. **CF-000104: case of the `Expect` token.**
    Side A [N-000354, pack 20]: the token is matched "case-insensitively". Side B [N-000493, pack 08]:
    "must be exactly the lowercase token `100-continue`."
    *Built:* side A. `Expect: 100-Continue` sets the flags.

15. **CF-000105: whether the client's body events end its 100-continue wait.**
    Side A [N-000353, pack 20]: "The client stays waiting for 100-continue until the server answers; its
    own body events do not end the wait." Side B [N-000359, pack 20]: the flags turn off "when the client
    sends any data event or its end-of-message."
    *Built:* side A. Only the server's informational or final response clears the flags (N-000358).

16. **CF-000106: which 2xx answer accepts CONNECT.**
    Side A [N-000364, N-000371, N-000395, pack 20]: "a 2xx response accepts CONNECT". Side B [N-000396,
    pack 20]: "Only status 200 accepts a CONNECT proposal; other 2xx statuses deny it."
    *Built:* any 2xx accepts CONNECT (three statements agree; one differs).

17. **CF-000107: repeated `Transfer-Encoding: chunked` headers.**
    Side A [N-000093, pack 14]: repeated chunked headers "collapse to one". Side B [N-000121, pack 14]:
    a second Transfer-Encoding header "is refused with suggested status 501, even when both values are
    `chunked`."
    *Built:* side B. Two Transfer-Encoding headers are refused with hint 501.

(The 19 ids are CF-000003, -005, -026, -048, -050, -074, -075, -076, -083, -098, -099, -100, -101,
-102, -103, -104, -105, -106, -107. Item 7 covers three of them, so the 17 items above cover all 19.)

## Gaps the spec does not state, and what was assumed

Each item names what is not stated and what the code does.

- **Header value whitespace on the wire.** The spec forbids leading or trailing space or tab in a
  constructed value ("refused, not stripped", N-000099). For header lines read from the peer, the code
  strips optional whitespace around the value, as RFC 7230 §3.2.4 says a field value excludes it.
- **Response framing when neither Content-Length nor Transfer-Encoding is present.** The spec covers
  this only for HTTP/1.0 peers (close-delimited). The code treats every received response like that,
  including from HTTP/1.1 peers. On the send side, an HTTP/1.1 peer gets chunked framing and any other
  peer gets close-delimited framing.
- **Status line and version parsing.** Only HTTP/1.0 and HTTP/1.1 are accepted when reading. Status codes
  are exactly three digits; codes below 100 are refused. Reason phrases may contain obs-text and tab.
  A request or response event may be constructed with another version, but sending it is refused.
- **Keep-alive before a response is known (client).** The client is DONE after its own end-of-message,
  not MUST_CLOSE, until the response shows `close` or a non-1.1 version.
- **Keep-alive when the peer version is unknown (server).** A server that has not pulled a request is
  not keep-alive, so a response it sends gets `Connection: close`.
- **Request with both Content-Length and Transfer-Encoding.** Content-Length decides (see CF-000003), and
  the Transfer-Encoding header is left off the wire. The `headers` attribute still lists both.
- **Trailers.** They are allowed only with chunked framing. They are refused for bodies with a declared
  length, for close-delimited bodies, and for empty bodies. They go through the same header rules as
  other headers.
- **101 and CONNECT acceptance timing.** A 101 accepts an Upgrade proposal only after the client has
  finished its request (MIGHT_SWITCH_PROTOCOL). Earlier, it is an ordinary informational response. A
  2xx to CONNECT is handled the same way.
- **Informational responses while IDLE.** Refused: a server may send them only inside SEND_RESPONSE.
- **Accepted-switch response.** It is written as given, with no framing headers and no keep-alive
  changes, because the connection leaves HTTP.
- **204 and 304.** The product drops Content-Length and Transfer-Encoding from the wire (see CF-000102).
  Received 204, 304, 1xx and HEAD responses have empty bodies.
- **Empty-reason status line.** Written as `HTTP/1.1 200 \r\n` (trailing space), following the RFC 7230
  status-line grammar with an empty reason-phrase.
- **Wire spelling.** Headers go out with the caller's name spelling (raw items). A collapsed
  Content-Length uses the spelling of its first occurrence. A Transfer-Encoding header keeps its name
  spelling, and its value is normalized to lowercase `chunked`.
- **Byte arguments.** Non-ASCII `str` is refused with LocalProtocolError, not encoded. Bytes-like
  objects are copied to `bytes`.
- **Data payloads.** A `str` payload is refused. Other objects that have `len()` are accepted and passed
  through by identity in passthrough send. `send()` converts them with `bytes()`.
- **Return values.** `send()` returns `b""` for an event that produces no bytes, and `None` for
  connection-closed. `send_failed()` and `start_next_cycle()` return `None`.
- **Refused sends.** Any refused send makes our side ERROR (FP-05), including a refused connection-closed
  send and any send after a switch.
- **Error hints.** Default 400. 501 for Transfer-Encoding refusals (N-000120, N-000121). 431 for the
  incomplete-event size limit on a request or status line or header block, and on a trailer block. An
  over-long chunk-size line (no line ending within the limit) gets 400, because the spec's 431 is stated
  for request, response and header lines only.
- **Runtime error class.** The spec only says the feed-after-close error is not a protocol error. The
  code uses `httpwire.ReceiveClosedError`, a subclass of `RuntimeError`. The class name is the
  implementer's choice (N-000475).
- **Pulling while MUST_CLOSE with bytes buffered.** Returns PAUSED, not an error. The spec says nothing
  here; PAUSED keeps the bytes for trailing data.
- **Remote errors are sticky.** After a remote protocol error, every later pull raises
  RemoteProtocolError with the first error's hint. Sends still work.
- **Invalid role.** `Connection(role)` with anything other than CLIENT or SERVER raises
  LocalProtocolError (the spec says only "an exception").
- **Headers equality.** `Headers` compares equal to a list or tuple of ordinary `(lowercased name,
  value)` pairs, and equal to another `Headers` when the raw items match.
- **Expect header parsing.** Values are split on commas and compared case-insensitively, after trimming
  spaces and tabs (see CF-000104).
- **Chunk extensions.** Parsed and discarded: only the part before `;` is checked against the size rule.
  An extension is not validated further (the spec does not say how).

## Where I looked

Only the spec in `/app/spec` was used: `MAP.md`, `CHECKLIST.md`, `export.meta.json`, and all 20 packs.
No network access, no existing httpwire or h11 source. The 522 checklist ids are all `N-000001` to
`N-000522`, and the checklist and the packs agree on the set of ids (checked by script).
