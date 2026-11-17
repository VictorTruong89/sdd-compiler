# httpwire — implementation notes

This file records where the specification in `spec/` disagrees with itself
(including the items in `spec/CONFLICTS.md`, plus some it does not list), and
what the code does for each. It also lists behavior the specification does not
state, with the assumption made.

Layout: the package is `httpwire/` at the repository root
(`_util.py` sentinels, errors, validators; `_events.py` events and header
normalization; `_connection.py` the `Connection` state machine, parser and
serializer; `__init__.py` the public names). `pyproject.toml` builds it with
setuptools. There are no runtime dependencies. Behavioral tests:
`python3 -m unittest discover -s tests` (from `/app`).

Abbreviations: "PRD" = `spec/Full_PRD.md`, "Contract" = `spec/Interface_Contract.md`.
Line numbers are the ones in `spec/CONFLICTS.md`.

---

## A. Conflicts listed in `spec/CONFLICTS.md`

### A1. Maximum Content-Length digits
- PRD FP-01, Boundary (line 105): "Every value of at most 18 digits is accepted; the maximum digit count is a fixed number ... from 18 to 32 inclusive."
- Contract, Events (line 46): "A `Content-Length` value longer than 16 digits is refused."
- **Built:** 18 digits. Values of 1–18 digits are accepted; 19 or more are refused. The 18 is the lowest value the PRD allows, and the PRD states the "at most 18 digits are accepted" guarantee outright.

### A2. Default incomplete-event size limit
- PRD FP-05, Normal (line 210): default "at least 14 kibibytes and less than 18 kibibytes."
- Contract, `Connection` signature (line 76): "When it is omitted, the limit is 8 kibibytes."
- **Built:** 16 KiB (16384 bytes). It is inside the PRD range. The size check applies only to an unfinished request/status line or header block, as the PRD specifies. It counts all unparsed bytes while the head is incomplete, and it raises a remote error with hint 431.

### A3. Hexadecimal digits in a chunk-size line
- PRD FP-03, chunked bullet (line 151): "A received size line may carry up to 64 hexadecimal digits."
- PRD FP-03, Normal (line 161): "at most a fixed number of digits ... from 16 to 32 inclusive"; Boundary (line 168) refuses more than that maximum.
- **Built:** 32 digits. A size line with more than 32 hex digits is a remote error. 64 is outside the 16–32 range that line 161 sets, so it cannot be used.

### A4. Whitespace after a chunk size
- PRD FP-03, Normal (line 161): the size line may be "optionally followed by spaces or tabs, then the line ending."
- PRD FP-03, Boundary (line 168): "Whitespace after the chunk size is refused."
- **Built:** accepted, following the normal-behavior grammar (line 161). `1a \r\n` and `1a ;ext\r\n` both parse. Chunk extensions are parsed and discarded. This is looser than RFC 7230's chunk grammar, which has no whitespace there.

### A5. Lone line feed as a line ending
- PRD FP-02, Normal (line 129): lone-LF header blocks "are accepted."
- Contract, `receive_data` (line 98): "every received line must end with a carriage return and line feed."
- **Built:** accepted for request/status lines, header lines, trailer lines and chunk-size lines. The CRLF after a chunk's data must be exactly CRLF (PRD line 168). The contract sentence is treated as wrong because it contradicts the PRD's explicit leniency.

### A6. Status line without a reason phrase
- PRD FP-02, Normal (line 129): "A response status line that omits the reason phrase is accepted and the reason is empty."
- Contract, `next_event()` (line 100): "A received status line with no reason phrase after its status code is illegal."
- **Built:** accepted; the reason is `b""`. `HTTP/1.1 204\r\n` parses.

### A7. Obsolete line folding
- PRD FP-02, Normal (line 130): folding "is accepted when reading headers."
- PRD FP-02, Boundary (line 136): "A continuation line ... is refused."
- **Built:** accepted. A continuation line is joined to the previous value with one space, and its leading spaces/tabs are removed. A continuation with no previous header is a remote error.

### A8. Control bytes in header values
- PRD FP-01, Normal (line 95): values may contain "any byte other than NUL, carriage return, line feed, form feed, and vertical tab, including other control bytes."
- PRD FP-01, Boundary (line 102): "Control bytes other than tab are refused in header values."
- **Built:** the Normal rule (line 95). Values may contain any byte except NUL, CR, LF, FF and VT. Tab is allowed. A value that begins or ends with space or tab is refused, as the PRD requires.

### A9. Framing headers on a response to HEAD
- PRD FP-02, Normal (line 122): "A response to HEAD is written with no framing headers."
- PRD FP-03, Normal (line 159): a server answering HEAD "writes the same framing headers it would have used for GET: chunked when the peer is HTTP/1.1, and connection-close framing when the peer is HTTP/1.0."
- **Built:** line 159. For HEAD, the response gets the GET framing headers (`Transfer-Encoding: chunked` for a 1.1 peer, `Connection: close` and no framing header for a 1.0 peer, or the caller's `Content-Length`). The body is always empty: no data is accepted, and end-of-message writes no bytes.

### A10. `Content-Length: 0` on a response
- PRD FP-03, Normal (line 152): "The `Content-Length` header is kept on the wire, including when N is 0."
- PRD FP-03, Normal (line 158): "A response with `Content-Length: 0` is sent without that header."
- **Built:** line 152. The header is kept. Line 158 reads as an added sentence in a list about empty-body statuses, and it conflicts with the more general rule.

### A11. Which framing header wins on a response
- PRD FP-01, Normal (line 94): "When an event carries both framing headers, the `Content-Length` decides how the body is framed."
- PRD FP-03, Normal (line 156): "If a response is constructed with both `Transfer-Encoding: chunked` and `Content-Length`, transfer-encoding wins: Content-Length is not sent."
- **Built:** Transfer-Encoding wins, as in RFC 7230 §3.3.3. This applies to responses (line 156) and also to requests, both sent and received. When TE is chunked, a Content-Length header is removed from the wire. Line 94's general rule is treated as the one that conflicts with RFC 7230.

### A12. Case sensitivity of `100-continue`
- PRD FP-07, Normal (line 249): "contains the token `100-continue` (matched case-insensitively)."
- Contract, `Connection` attributes (line 89): "The `Expect` value must be exactly the lowercase token `100-continue`."
- **Built:** case-insensitive, per the PRD. `Expect: 100-Continue` sets the flags.

### A13. `Expect: 100-continue` on HTTP/1.0 requests
- PRD FP-07, Normal (line 249): an Expect header on an HTTP/1.0 request "does not set either flag."
- Contract, `Connection` attributes (line 88): "any request with `Expect: 100-continue` sets it, whatever its HTTP version."
- **Built:** the PRD. The flag is set only for HTTP/1.1 requests.

### A14. Whether the client's body ends the 100-continue wait
- PRD FP-07, Normal (line 248): "its own body events do not end the wait."
- PRD FP-07, Normal (line 250): the flags turn off "when the client sends any data event or its end-of-message."
- **Built:** line 250. The client's data or end-of-message, sent or pulled, clears `client_is_waiting_for_100_continue`. Line 248 is read as describing the server's wait for the response, not the client's own sending.

### A15. Which 2xx status accepts CONNECT
- PRD FP-07, Normal (lines 252 and 254): "a final response whose status is in the 2xx range"; "a 2xx response accepts CONNECT."
- PRD FP-07, Boundary (line 263): "Only status 200 accepts a CONNECT proposal; other 2xx statuses deny it."
- **Built:** any 2xx accepts CONNECT (lines 252 and 254). Non-2xx final responses deny it.

### A16. Feeding bytes after a switch acceptance
- PRD FP-07, Normal (line 257): after acceptance, bytes "fed after the accepting response ... accumulate, in order, in trailing data."
- PRD FP-02 (line 138) and FP-06 (line 238): feeding a non-empty chunk after an empty chunk "is refused at feed time as a runtime error."
- **Built:** the runtime error (two places plus the contract's `receive_data` text). Any non-empty feed after an empty feed raises `RuntimeError`, including after an accepted switch. Bytes fed before the empty feed stay in trailing data, in order.

---

## B. Conflicts not listed in `spec/CONFLICTS.md`

### B1. Repeated `Transfer-Encoding` headers
- PRD FP-01, Normal (line 94): "Repeated `Transfer-Encoding: chunked` headers collapse to one, like repeated equal `Content-Length` values."
- PRD FP-01, Boundary (line 106) and FP-05 (line 203): "A second `Transfer-Encoding` header is refused with suggested status 501, even when both values are `chunked`."
- **Built:** refused with hint 501 (lines 106 and 203). The "collapse" rule at line 94 is not implemented.

---

## C. Behavior the specification does not state (assumptions)

- **Status line with no reason.** A response with an empty reason is written as `HTTP/1.1 200 \r\n` (the space is kept, as RFC 7230 grammar requires).
- **Wire header values.** On parsing, leading and trailing SP/HT are stripped (RFC 7230 OWS). The "refuse rather than strip" rule applies only to values the caller constructs.
- **Header normalization on trailers.** Trailers in `EndOfMessage` use the same normalization as other headers. A `Content-Length` or `Transfer-Encoding` inside trailers is not refused specially.
- **Data payload types.** `send()` requires a bytes-like payload; a `str` is refused. `send_with_data_passthrough()` also accepts any object with `len()`, and returns that object by identity. A `str` payload is refused on both paths.
- **Empty data and empty framings.** A zero-length `Data` event writes nothing (no empty chunk, which would look like the terminator). A non-empty `Data` under empty framing (HEAD, 204, 304, `Content-Length: 0`) is a local protocol error.
- **204 and 304 responses.** Their headers are written exactly as given; no framing header is added or removed.
- **Close-delimited responses in the client role.** A response with no framing headers is close-delimited whatever its HTTP version. The body ends at the empty feed, then end-of-message, then connection-closed; keep-alive is off.
- **Keep-alive.** Keep-alive is off when either message is not HTTP/1.1 or carries a `Connection` token `close`. A response sent with keep-alive off has its `Connection` header rewritten: `keep-alive` tokens are removed and `close` is added. Peer version unknown (no request seen yet) also counts as keep-alive off.
- **Requests with `Transfer-Encoding: chunked`.** The `Content-Length` header is not sent on the wire.
- **Protocol versions.** Requests and responses that are not HTTP/1.0 or HTTP/1.1 are a remote error with hint 400 (not 505, since the PRD gives 400 as the default). Upgrade proposals are recognized on any HTTP version.
- **Upgrade proposals.** A `101` with no pending Upgrade proposal is an ordinary informational response and does not switch protocol. A request with both CONNECT and Upgrade: a 2xx final response accepts CONNECT; a `101` accepts Upgrade; any other final response denies both.
- **Switch acceptance before the client's end-of-message.** If the server accepts a switch before the client has finished sending, the client becomes SWITCHED_PROTOCOL when its end-of-message is sent or pulled, not earlier.
- **Ordering of pulls around a close.** A pulled connection-closed event is returned again on every later pull (PRD FP-06). Pauses (pipelining, switch) take priority over a pending close; close is returned only after stored bytes are consumed.
- **Reset on next cycle.** `start_next_cycle()` clears per-cycle state (keep-alive, proposal, flags, framing) but keeps the stored bytes and the peer's last recorded HTTP version.
- **Chunk-size line too long.** A chunk-size line that has no line ending and is longer than the incomplete-event limit is a remote error with hint 400. Digit-count overflow is also hint 400. Hint 431 is only for the request/status/header block, as the PRD states.
- **Start-of-message bytes.** If the first byte where a request or status line is expected is a space or a byte below 33, the pull fails immediately (PRD FP-02), so a leading blank line is an error.
- **Constructor arguments.** `Request`, `Response` and `InformationalResponse` require `headers`; `EndOfMessage` defaults to no trailers; `http_version` defaults to `b"1.1"`. Constructors accept positional or keyword arguments in the order the contract lists.
- **Non-ASCII text.** Byte-valued arguments given as `str` must be ASCII; otherwise `LocalProtocolError`.
- **Reason phrase.** Any byte except NUL, CR and LF is allowed.
- **Method, target, version.** Method must be a token; target must be visible ASCII (33–126); version must match `digit.digit`.
- **Error classes.** `LocalProtocolError` and `RemoteProtocolError` both derive from a private `_ProtocolError(Exception)` base; neither derives from the other. `error_status_hint` defaults to 400.
- **Role argument.** Any role other than `CLIENT`/`SERVER` raises `ValueError`.
- **States container.** `Connection.states` returns a `dict` keyed by `CLIENT` and `SERVER`.
- **`trailing_data`.** Returns `(bytes, bool)`; the bytes are a copy.
- **`send()` return value.** Always `bytes`; `b""` when no bytes are produced.
- **Refused sends.** Any `send()` refused as a local protocol error also moves our side to ERROR (PRD FP-05), including sends refused because the connection is already in ERROR or SWITCHED_PROTOCOL.
- **Receive after our own error.** Pulls keep working after our side is in ERROR, so the peer's already-sent bytes can still be read.
- **Empty feed twice.** Feeding an empty chunk after an empty chunk is a no-op, not an error.
- **Peer HTTP version.** Recorded only from pulled requests (server role) and pulled responses (client role), never from our own sends.
