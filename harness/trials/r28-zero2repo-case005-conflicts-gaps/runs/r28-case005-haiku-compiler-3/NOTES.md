# NOTES: httpwire build

This file records (1) where the specification disagrees with itself and which side I built,
(2) what the specification leaves unstated and what I assumed, and (3) how the 522 ids in
`spec/CHECKLIST.md` are accounted for. The spec in `spec/` is unchanged.

Layout built: `httpwire/` (package, flat layout at the repo root), `pyproject.toml`
(setuptools, no runtime dependencies), `tests/test_httpwire.py` (59 tests).
Verified: all 59 tests pass on Python 3.13 and 3.11. Python 3.8 is the documented floor; no
3.8 interpreter is installed here, so 3.8 is not tested. The code avoids syntax newer than 3.8.

`spec/MAP.md` lists 9 unsettled contradictions (CF-000003, 005, 026, 048, 050, 074, 075, 076,
083). Each has a verdict below. Where a verdict is given, the choice is mine; the spec does not
settle it.

---

## 1. Conflicts and what I built

Each entry gives both sides with their location (`pack NN N-xxxxxx`), then the choice.

### 1.1 Unsettled contradictions (listed in MAP.md)

**CF-000003: framing when both Content-Length and Transfer-Encoding are present.**
- Pack 14 N-000096 (FP-01, normal): "When an event carries both framing headers, the
  `Content-Length` decides how the body is framed."
- Pack 16 N-000207 (FP-03, normal): "If a response is constructed with both `Transfer-Encoding:
  chunked` and `Content-Length`, transfer-encoding wins: Content-Length is not sent."
- **Built:** a *request* with both uses Content-Length (the Transfer-Encoding header is dropped
  from the wire, but stays in `headers`). A *response* with both uses Transfer-Encoding
  (Content-Length is dropped from the wire). The receive side applies the same rules.

**CF-000005: status line with no reason phrase.**
- Pack 15 N-000166 (FP-02, normal): "A response status line that omits the reason phrase is
  accepted and the reason is empty."
- Pack 08 N-000516 (Interface, `next_event`): a status line with no reason "is illegal".
- **Built:** accepted, reason is `b""`. The PRD behavior is the more specific statement.

**CF-000026: control bytes in header values.**
- Pack 14 N-000097: values may contain "other control bytes and non-ASCII bytes".
- Pack 14 N-000108: "Control bytes other than tab are refused in header values."
- **Built:** refused. Every byte below 0x20 except tab is refused, and so is 0x7F (DEL).
  Non-ASCII bytes (0x80 to 0xFF) are allowed.

**CF-000048: default incomplete-event size limit.**
- Pack 18 N-000317 (FP-05): the default is "at least 14 kibibytes and less than 18".
- Pack 08 N-000479 (Interface, `Connection(role)`): "When it is omitted, the limit is 8
  kibibytes."
- **Built:** 8 KiB (8192 bytes) when omitted. The interface states the default concretely.

**CF-000050: framing headers on a response to HEAD.**
- Pack 15 N-000137 (FP-02): "A response to HEAD is written with no framing headers."
- Pack 16 N-000219 (FP-03): "A server answering HEAD writes the same framing headers it would
  have used for GET."
- **Built:** the GET-equivalent framing headers are written (Transfer-Encoding: chunked for a
  1.1 peer; nothing plus `Connection: close` for a 1.0 peer). The body is always empty, so no
  chunk terminator is written.

**CF-000074: line endings in received header blocks.**
- Pack 15 N-000165 (FP-02): lone LF, or mixed CRLF and LF, "as line endings are accepted".
- Pack 08 N-000510 (Interface): "every received line must end with a carriage return and line
  feed".
- **Built:** lone LF accepted in request, status, and header lines. Chunk framing (the CRLF
  after each chunk's data) is strict and requires exactly CRLF.

**CF-000075 and CF-000076: obsolete line folding.**
- Pack 15 N-000168 and N-000169 (FP-02): a continuation line "is joined to the previous header's
  value" with its leading whitespace "replaced by a single space".
- Pack 15 N-000176 (FP-02): a continuation line "is refused".
- **Built:** joined. Only the leading run of spaces and tabs is replaced by one space, so
  interior tabs are kept.

**CF-000083: Expect: 100-continue on an HTTP/1.0 request.**
- Pack 20 N-000357 (FP-07): an `Expect: 100-continue` header on an HTTP/1.0 request "does not
  set either flag".
- Pack 08 N-000491 (Interface): any request with that header "sets
  client_is_waiting_for_100_continue, whatever its HTTP version".
- **Built:** the PRD rule. The flags are set only for HTTP/1.1 requests.

### 1.2 Conflicts not listed in MAP.md

**Content-Length digit limit.**
- Pack 06 N-000462 (Interface): "A `Content-Length` value longer than 16 digits is refused."
- Pack 14 N-000114..N-000119 (FP-01): values of at most 18 digits are accepted; the maximum is
  "from 18 to 32 inclusive".
- **Built:** 16 digits. This is the only value that satisfies the Interface MUST NOT, and the
  PRD's 18-digit acceptance cannot hold at the same time.

**Chunk-size digit limit.**
- Pack 16 N-000192 (FP-03, normal, MAY): a size line "may carry up to 64 hexadecimal digits".
- Pack 16 N-000228 (FP-03, MUST): "at most a fixed number of digits ... from 16 to 32 inclusive".
- **Built:** 32 digits (the MUST range). Larger size lines are refused. This does not implement
  the MAY-64 form.

**Repeated Transfer-Encoding headers.**
- Pack 14 N-000094 (FP-01, normal): repeated `Transfer-Encoding: chunked` "collapse to one".
- Pack 14 N-000121 (FP-01, boundary): "A second `Transfer-Encoding` header is refused with
  suggested status 501, even when both values are `chunked`."
- **Built:** refused with hint 501 (the boundary rule, which is more specific). Repeated
  Content-Length values still collapse.

**Which CONNECT response accepts the switch.**
- Pack 20 N-000364, N-000365, N-000371, N-000395 and pack 20 N-000369..N-000372 say a 2xx final
  response accepts CONNECT.
- Pack 20 N-000394 and N-000398 (boundary): "Only status 200 accepts a CONNECT proposal; other
  2xx statuses deny it."
- **Built:** only 200 accepts. The boundary rule uses "only" and is the more specific statement.

**Matching `100-continue`.**
- Pack 20 N-000354 (FP-07): the token is "matched case-insensitively".
- Pack 08 attribute table, `they_are_waiting_for_100_continue`: "The Expect value must be exactly
  the lowercase token `100-continue`."
- **Built:** case-insensitive (the behavior rule). A header of `Expect: 100-Continue` sets the
  flag.

**Whether client body events end the 100-continue wait.**
- Pack 20 N-000351 (FP-07, normal): "The client stays waiting for 100-continue until the server
  answers; its own body events do not end the wait."
- Pack 20 N-000358 and N-000359 (FP-07, MUST): the flags turn off when "the client sends any data
  event or its end-of-message".
- **Built:** the client's Data and EndOfMessage clear the flag (N-000358/359). The client may
  still send its body either way; only the flag differs.

**Content-Length: 0 on a response.**
- Pack 16 N-000199 (FP-03): the Content-Length header "is kept on the wire, including when N is
  0".
- Pack 16 N-000218 (FP-03, empty-body bullet): "A response with `Content-Length: 0` is sent
  without that header".
- **Built:** kept for normal responses (N-000199). For responses with an always-empty body
  (204, 304), all framing headers are removed, which is the reading I took from N-000218. HEAD
  keeps its Content-Length as written.

**Whitespace after a chunk size.**
- Pack 16 N-000232 (FP-03): a chunk-size line may be "optionally followed by spaces or tabs"
  after the optional extension.
- Pack 16 N-000244 and N-000245 (FP-03): "Whitespace after the chunk size is refused."
- **Built:** whitespace directly after the size digits is refused. Anything after `;` (the
  extension) is accepted and discarded.

---

## 2. Unstated items and my assumptions

- **Received header values.** Leading and trailing spaces and tabs around a received value are
  stripped (RFC OWS). The value rules from FP-01 then apply to the stored result.
- **Received start lines.** Single-space separators. A request line needs exactly three fields.
  A status line needs `HTTP/1.x`, a three-digit code, and an optional reason after one space.
  `HTTP/1.1 200` (no space after the code) is accepted. Only `HTTP/1.0` and `HTTP/1.1` are
  accepted as received versions.
- **Version strings** must match `<digit>.<digit>` (for example `1.1`).
- **Reason phrase** may not contain CR, LF, or NUL. Other bytes are accepted.
- **Status line written when the reason is empty** is `HTTP/1.1 <code> ` with a trailing space,
  matching the form `HTTP/<v> <code> <reason>` in RFC 7230. Example: `HTTP/1.1 204 \r\n`.
- **Responses with neither framing header** are close-delimited on the receive side for any peer
  version. The spec states this only for HTTP/1.0 peers (pack 16 N-000208). For a 1.1 peer I
  followed RFC 7230 §3.3.3.
- **Responses received with Transfer-Encoding** are read as chunked whatever the peer version.
- **Responses sent to an unknown peer** (no request pulled yet, or a 1.0 peer) use close-delimited
  framing if they have no Content-Length or Transfer-Encoding. A Content-Length response keeps
  its length, and keep-alive is disabled either way.
- **Trailers** on a chunked body are read with the same header rules and the same size limit as
  a header block. Chunk-size lines and body bytes are not counted against the size limit.
- **Informational responses** write no framing headers. A 101 that does not answer an Upgrade
  proposal is an ordinary informational response.
- **Switch proposals.** An `Upgrade` header of any value is a proposal. `CONNECT` is a proposal
  when the method is exactly `CONNECT`. An accepted switch writes no framing headers.
- **Keep-alive** is disabled by a Connection token `close` on either side's message, by any
  HTTP/1.0 message, by a close-delimited response, by a remote protocol error, and by an unknown
  peer version when sending a response. It is evaluated after every state change.
- **start_next_cycle** clears the recorded peer version. The next response is sent as if no
  request had been seen, until the next request is pulled.
- **Passthrough send.** A payload that is bytes-like is passed as a buffer. A payload that is
  not bytes-like but has a length is passed as the same object. The plain `send` path converts
  a bytes-like payload to bytes and refuses anything else with LocalProtocolError.
- **Bad role.** `Connection("client")` and similar raise an exception that is both a
  `LocalProtocolError` and a `ValueError`, so either handler catches it.
- **Feeding bytes after the receive side closed** raises `httpwire._errors.ReceiveAfterCloseError`,
  a RuntimeError. The spec leaves the class to the implementer (pack 07 N-000475).
- **Passing an event's `headers` as a list** is accepted; `Headers` objects are copied.
- **Refused sends** put the sending side into ERROR. This applies to every LocalProtocolError
  raised by `send`, including a client sending a second request, as stated in pack 18 N-000307.
- **`error_status_hint`** defaults to 400. The hint is 501 for a bad or duplicated
  Transfer-Encoding and 431 for the incomplete-event size limit.
- **`max_incomplete_event_size=None`** is treated as the default.

---

## 3. Checklist accounting (`spec/CHECKLIST.md`, 522 ids)

I did not trace each id to a line of code. The table below accounts for the ids by pack and by
the module that implements their feature point. Every pack's behavior is implemented. The
ids I did not implement are listed by number in section 3.2.

### 3.1 By pack

| Pack | Ids | Topic | Implemented in | Tested by |
|---|---|---|---|---|
| 01 | (no ids; constraints N-000003, 022, 037, 038, 047, 049, 052, 069, 126, 430, 431) | hardware, no I/O, no CLI | whole package (stdlib `re` only); `pyproject.toml` | import tests |
| 02 | N-000413..417 | summary: pure Python, zero deps, Python 3.8+ | `pyproject.toml`; no compiled code | not tested on 3.8 |
| 03 | N-000418..428 | execution profiles, build | `pyproject.toml` (flat `httpwire` package) | editable import works |
| 04 | N-000429..432 | importable library, no CLI, no config | `httpwire/__init__.py` | `TestSurface` |
| 05 | N-000433..449 | public surface and package-root names | `httpwire/__init__.py`, `_sentinels.py`, `_events.py`, `_errors.py` | `TestSurface` |
| 06 | N-000450..471 | event constructor fields, bytes normalization, header list, raw items | `_events.py`, `_headers.py` | `TestEventConstruction`, `TestSurface` |
| 07 | N-000472..475 | `error_status_hint`, `str(error)`, feed-after-close exception | `_errors.py` | `TestErrors` |
| 08 | N-000476..522 | Connection signature, attributes, send/passthrough/receive/next_event/start_next_cycle/send_failed | `_connection.py` | `TestBasicCycle`, `TestErrors`, `TestKeepAliveAndClose`, `TestExpectAndSwitch` |
| 09 | N-000001..009 | product overview: library, no I/O, protocol error on violation | `_connection.py`, `_errors.py` | throughout |
| 10 | N-000010..021 | terminology: states, send, feed, pull, paused, need-data, cycle, keep-alive, trailing data | `_connection.py` | throughout |
| 11 | N-000022..036 | public surface inventory by feature point | the feature points below | by feature point |
| 12 | N-000037..058 | non-functional: zero deps, Python 3.8+, no I/O, own parser, HTTP/1.1 only on the wire | whole package; `_connection.py` refuses non-1.1 sends | `test_non_11_cannot_be_sent` |
| 13 | N-000059..069 | non-goals: no I/O, no HTTP/2, no 1.0 keep-alive, only `chunked` TE, extensions discarded, no CLI | `_headers.py` (TE refusal), `_wire.py` (extensions discarded), `_connection.py` | `TestEventConstruction.test_framing_header_rules`, `TestBodies.test_chunk_size_line_rules` |
| 14 | N-000070..121 | FP-01: six events, normalization, refusals | `_events.py`, `_headers.py` | `TestEventConstruction` |
| 15 | N-000122..182 | FP-02: connection, states, send, feed/pull, line rules, first-byte rule, feed-after-close | `_connection.py`, `_wire.py` | `TestBasicCycle`, `TestErrors`, `TestResponseFraming` |
| 16 | N-000183..246 | FP-03: framing for requests and responses, chunked, close-delimited, passthrough, chunk size | `_connection.py`, `_wire.py`, `_headers.py` | `TestBodies`, `TestResponseFraming` |
| 17 | N-000247..289 | FP-04: cycle, keep-alive, pipelining, paused, start_next_cycle refusal | `_connection.py` (`_post`, `_keep_alive_disabled`, `start_next_cycle`) | `TestPipelining`, `TestKeepAliveAndClose` |
| 18 | N-000290..331 | FP-05: local/remote errors, hints, ERROR, send_failed, 431 size limit | `_connection.py` (`_fail_side`, `_read_head`), `_errors.py` | `TestErrors` |
| 19 | N-000332..348 | FP-06: close, CLOSED, MUST_CLOSE, pulled close, close mid-message | `_connection.py` (`_transition`, `_post`, `_next_event_unchecked`) | `TestErrors`, `TestKeepAliveAndClose` |
| 20 | N-000349..412 | FP-07: 1xx, 100-continue, CONNECT/Upgrade switches, trailing data | `_connection.py` (`_transition`, `_commit`, `_response_pieces`) | `TestExpectAndSwitch`, `TestInformationalAndHeaders` |

"no node" blocks (40 of them) are documentation, quoted in the packs. Each is covered by the
behavior it describes in the feature point above.

### 3.2 Ids not implemented, with reasons

These ids conflict with another id that I followed instead. Each is listed in section 1.

- N-000097 (MAY: other control bytes allowed in values). Conflicts with N-000108; refused.
- N-000192 (MAY: size lines up to 64 digits). Conflicts with N-000228; 32 digits.
- N-000137 (HEAD response with no framing headers). Conflicts with N-000219; GET-equivalent headers.
- N-000218, the Content-Length-0 clause for normal responses. Conflicts with N-000199; kept.
- N-000244 and N-000245 (whitespace after a size line refused). Partly conflicts with N-000232;
  whitespace after an extension is allowed.
- N-000094 (repeated Transfer-Encoding collapses). Conflicts with N-000121; refused.
- N-000364, N-000365, N-000369..N-000372, N-000395 (2xx accepts CONNECT). Conflicts with
  N-000394 and N-000398; only 200 accepts.
- N-000351 (body events do not end the 100-continue wait). Conflicts with N-000358/359.

Ids N-000475 and N-000449 are implementer's choice (the feed-after-close class and "other names
may exist"); I chose RuntimeError and exported no extra names. I found no other id that I left
out, but I checked this by pack and feature point, not id by id, so an individual id could still
be missing a code path. Treat the table in 3.1 as the accounting, not a line-level trace.

### 3.3 Other notes

- `spec/MAP.md` reports one acceptance criterion for pack 17, but the pack text says "AC labels:
  none". No `test_AC_...` names were possible, so my tests are named after the spec ids they
  exercise instead.
- MAP.md reports "No foundation pack". Nothing in the spec was read as a foundation document.
- The hidden tests are not visible to me. I wrote the tests from the spec alone and did not fetch
  any existing implementation.
