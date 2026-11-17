# httpwire — implementation notes

This file records where the specification (`spec/`) disagrees with itself, what
was not stated, and what the implementation assumes. `spec/` is unchanged.

Rule used throughout: `Full_PRD.md` governs *behaviour* and
`Interface_Contract.md` governs the *public surface* (names, signatures, forms of
returned values). The contract says so itself (its Product overview: "What the
product does, and under which conditions, is specified in the PRD"). Where the
contract states a behaviour that the PRD contradicts, the PRD wins.

Code layout: `httpwire/` (package), `pyproject.toml` (setuptools, zero
dependencies), `tests/test_httpwire.py` (unittest; run with
`python3 -m unittest tests.test_httpwire` from `/app`).

---

## Conflicts listed in `spec/CONFLICTS.md`

### 1. Maximum Content-Length digits
- **PRD FP-01, Boundary (line 105):** "Every value of at most 18 digits is accepted; the maximum digit count is … from 18 to 32 inclusive."
- **Contract, Events (line 46):** "A `Content-Length` value longer than 16 digits is refused."
- **Built:** 18 digits (`MAX_CONTENT_LENGTH_DIGITS` in `headers.py`). Longer values are refused. Chosen because it is the PRD's behaviour rule. Values of 17–18 digits are accepted, which the contract would refuse.

### 2. Default incomplete-event size limit
- **PRD FP-05, Normal (line 210):** default "at least 14 kibibytes and less than 18 kibibytes."
- **Contract, `Connection` signature (line 76):** "When it is omitted, the limit is 8 kibibytes."
- **Built:** 16 KiB (`DEFAULT_MAX_INCOMPLETE_EVENT_SIZE`). Passing an explicit value still overrides it.

### 3. Hexadecimal digits in a chunk-size line
- **PRD FP-03, chunked bullet (line 151):** "A received size line may carry up to 64 hexadecimal digits."
- **PRD FP-03, Normal (line 161) and Boundary (line 168):** the maximum is "a fixed number … from 16 to 32 inclusive"; more digits are refused.
- **Built:** 32 digits. Line 151 conflicts with the implementer-choice range that lines 161 and 168 define, and 32 is the largest value inside that range.

### 4. Whitespace after a chunk size
- **PRD FP-03, Normal (line 161):** the size line may be "optionally followed by spaces or tabs, then the line ending."
- **PRD FP-03, Boundary (line 168):** "Whitespace after the chunk size is refused."
- **Built:** accepted, following line 161, which is the grammar. Blanks are allowed after the size or after an extension, but not between the size and a `;`. Chunk `1a \r\n` is accepted; `1a ;x\r\n` is refused.

### 5. Lone line feed as a line ending
- **PRD FP-02, Normal (line 129):** a header block using lone LF line endings "is accepted."
- **Contract, `receive_data` (line 98):** "every received line must end with a carriage return and line feed."
- **Built:** LF and CRLF are both accepted (PRD). A CR before the LF is removed.

### 6. Status line without a reason phrase
- **PRD FP-02, Normal (line 129):** "A response status line that omits the reason phrase is accepted and the reason is empty."
- **Contract, `next_event()` (line 100):** "A received status line with no reason phrase after its status code is illegal."
- **Built:** accepted with an empty reason (PRD). Outgoing status lines always carry the SP before the reason, so an empty reason is sent as `HTTP/1.1 204 \r\n`.

### 7. Obsolete line folding
- **PRD FP-02, Normal (line 130):** continuation lines "are joined to the previous header's value."
- **PRD FP-02, Boundary (line 136):** "A continuation line … is refused."
- **Built:** folding is accepted and joined with one space. Line 136 starts "allowing only the leniencies stated above", which covers folding. A continuation with no preceding header is refused.

### 8. Control bytes in header values
- **PRD FP-01, Normal (line 95):** values may contain "other control bytes."
- **PRD FP-01, Boundary (line 102):** "Control bytes other than tab are refused in header values."
- **Built:** the boundary rule. Bytes 0x00–0x08, 0x0A–0x1F and 0x7F are refused (tab is allowed between other bytes). Bytes 0x80–0xFF are allowed. The regex is `VALUE_RE` in `headers.py`.

### 9. Framing headers on a response to HEAD
- **PRD FP-02, Normal (line 122):** "A response to HEAD is written with no framing headers."
- **PRD FP-03, Normal (line 159):** "A server answering HEAD writes the same framing headers it would have used for GET."
- **Built:** line 159. The framing headers are chosen as for GET (`Transfer-Encoding: chunked` for an HTTP/1.1 peer; close framing and `Connection: close` otherwise). The body is always empty and end-of-message writes nothing.

### 10. `Content-Length: 0` on a response
- **PRD FP-03, Normal (line 152):** "The `Content-Length` header is kept on the wire, including when N is 0."
- **PRD FP-03, Normal (line 158):** "A response with `Content-Length: 0` is sent without that header."
- **Built:** kept (line 152), because line 152 is the rule for Content-Length responses and names N=0 explicitly.

### 11. Which framing header wins on a response
- **PRD FP-01, Normal (line 94):** "When an event carries both framing headers, the `Content-Length` decides how the body is framed."
- **PRD FP-03, Normal (line 156):** for a response with both, "transfer-encoding wins: Content-Length is not sent."
- **Built:** responses: Transfer-Encoding wins, on send and on receive (`_plan_response`, `_framing_for_response`). Requests: Content-Length decides (`_framing_for_request`). When a request carries both, both headers stay on the wire as the caller gave them.

### 12. Case sensitivity of `100-continue`
- **PRD FP-07, Normal (line 249):** the token is "matched case-insensitively."
- **Contract, `Connection` attributes (line 89):** "The `Expect` value must be exactly the lowercase token `100-continue`."
- **Built:** case-insensitive token match (PRD).

### 13. `Expect: 100-continue` on HTTP/1.0 requests
- **PRD FP-07, Normal (line 249):** "An `Expect: 100-continue` header on an HTTP/1.0 request does not set either flag."
- **Contract, `Connection` attributes (line 88):** "any request with `Expect: 100-continue` sets it, whatever its HTTP version."
- **Built:** no flag for HTTP/1.0 (PRD).

### 14. Whether the client's body ends the 100-continue wait
- **PRD FP-07, Normal (line 248):** "The client stays waiting for 100-continue until the server answers; its own body events do not end the wait."
- **PRD FP-07, Normal (line 250):** the flags turn off "when the client sends any data event or its end-of-message."
- **Built:** line 248. The client's flag is cleared only when a server informational or final response is sent or pulled. Body events do not clear it. The server-role `they_are_waiting_for_100_continue` follows the same flag.

### 15. Which 2xx status accepts CONNECT
- **PRD FP-07, Normal (lines 252, 254):** acceptance is "a final response whose status is in the 2xx range."
- **PRD FP-07, Boundary (line 263):** "Only status 200 accepts a CONNECT proposal; other 2xx statuses deny it."
- **Built:** only 200 accepts CONNECT. Other 2xx statuses are denials (the boundary line is the more specific statement).

### 16. Feeding bytes after a switch acceptance
- **PRD FP-07, Normal (line 257):** after acceptance, bytes "fed after the accepting response … accumulate, in order, in trailing data."
- **PRD FP-02, Boundary (line 138) and FP-06, Boundary (line 238):** feeding a non-empty chunk after an empty chunk "is refused at feed time as a runtime error."
- **Built:** the runtime error (`ReceiveAfterCloseError`) in every case. An empty chunk closes the receive side, and any later non-empty chunk is refused, including after an accepted switch. Bytes fed before the empty chunk accumulate in `trailing_data`.

---

## Conflict not listed in `spec/CONFLICTS.md`

### 17. Repeated `Transfer-Encoding` headers
- **PRD FP-01, Normal (line 94):** "Repeated `Transfer-Encoding: chunked` headers collapse to one, like repeated equal `Content-Length` values."
- **PRD FP-01, Boundary (line 106)** and **FP-05, Normal (line 203):** "A second `Transfer-Encoding` header is refused with suggested status 501, even when both values are `chunked`."
- **Built:** refused with 501 (two places say so; line 94 is the outlier). Repeated Content-Length values still collapse as stated.

---

## Assumptions where the spec is silent

Parsing and wire form
- Wire header values have leading and trailing SP/HT stripped (RFC 7230 §3.2.4). The FP-01 refusal of leading or trailing blanks applies to values given to constructors, not to bytes read from the peer.
- A chunk-size line is also subject to the incomplete-event size limit, with status 431. The spec's limit only names request/status lines and header blocks.
- Trailer headers in a chunked body are normalized and validated the same way as other headers (including the Content-Length and Transfer-Encoding rules, with 501 for Transfer-Encoding).
- A response with neither framing header is close-delimited for any peer version, not only HTTP/1.0 (RFC 7230 §3.3.3). Such a response also disables keep-alive, since the connection cannot be reused.
- Peer versions other than 1.0 and 1.1 are parsed. They disable keep-alive. Nothing else is said about them, so the protocol-error status stays at 400 (not 505).
- Upgrade and CONNECT proposals are recognized whatever the HTTP version of the request.
- The peer version is recorded from a pulled request (server role) or pulled final response (client role). Informational responses do not record it.
- A client-role connection with its peer in IDLE does not parse incoming bytes (`NEED_DATA`), because it has no request outstanding.
- A server that sends a response before any request has been seen, or whose peer is HTTP/1.0, uses close-delimited framing and adds `Connection: close`.
- A 204 or 304 response keeps the caller's headers unchanged and sends no body. The response is not given framing headers, though keep-alive still applies.
- An accepted CONNECT or 101 response is written with the caller's headers only (no framing headers, no Connection rewrite).
- `Connection: close` is written by rewriting the Connection header: `keep-alive` tokens are removed, `close` is added, and tokens are lower-cased.
- Sending trailing headers to an HTTP/1.0 peer is refused whenever the peer's version is known to be 1.0.

Events and API
- Role argument: anything other than `CLIENT` or `SERVER` raises `ValueError`.
- `max_incomplete_event_size` must be a positive int; otherwise `ValueError`.
- `send(ConnectionClosed())` and `send` for other no-byte events return `b""`. `send_with_data_passthrough` returns `[]` for them.
- `send()` on a Data event whose payload is not bytes-like converts it with `bytes(memoryview(...))`. A non-buffer object raises `TypeError` before any state change, and so does a `str` payload. Passthrough keeps non-bytes-like payloads by identity and uses `len()` for their length.
- Header names and values given as `str` are encoded as latin-1. Method, target and version must be valid bytes after encoding.
- A reason phrase containing CR, LF or NUL is refused at construction. Other bytes are allowed.
- HTTP version text must match `d.d` (for example `1.1`). Versions are stored as bytes like `b"1.1"`, not `b"HTTP/1.1"`.
- `Request.headers`, `InformationalResponse.headers` and `Response.headers` are required arguments. `EndOfMessage.headers` defaults to empty.
- `Connection.states` returns a fresh dict keyed by `CLIENT` and `SERVER`.
- `trailing_data` returns `(bytes, bool)`, copying the stored bytes.
- `start_next_cycle()` requires both sides to be DONE. Any other combination raises `LocalProtocolError` and changes nothing.
- A pulled event that violates the protocol moves the peer's side to ERROR and raises `RemoteProtocolError` (status 400, or 501 for Transfer-Encoding, or 431 for the size limit). Every later pull also raises.

Behaviour notes
- A DONE or MUST_CLOSE side with stored bytes returns `PAUSED`. Once stored bytes are empty and the peer has closed, it returns `ConnectionClosed`.
- Pipelined data after a close is handled one cycle at a time before the close is reported.
- Keep-alive is recomputed for each cycle from the request and the response. It is also turned off by any ERROR state, which is how the server marks its error response with `Connection: close`.

## Not tested

- Only CPython 3.13 is available in this environment. The code uses only features available from Python 3.8 (bytes `%` formatting, `re.fullmatch`, `collections.abc.Sequence`), but it has not been run on 3.8 or on PyPy.
- No network I/O, no sockets, and no third-party dependencies are used anywhere in the package.
