# httpwire — build notes

Implementation of the httpwire spec in `spec/` (not modified). Layout:

- `httpwire/` — the importable package (`_common.py` sentinels/roles/states/errors,
  `_events.py` event types and header normalization, `_parse.py` byte-level parsing,
  `_connection.py` the state machine, `__init__.py` package-root exports).
- `pyproject.toml` — setuptools packaging (zero runtime dependencies, Python >= 3.8).
- `tests/test_httpwire.py` — my own unit tests (`python3 -m pytest tests`, or `python3 -m unittest`).

Where the spec disagrees with itself, the choice made is below. "PRD" is `spec/Full_PRD.md`,
"Contract" is `spec/Interface_Contract.md`. Line numbers are as the files are now.

## Conflicts between spec statements

Where the PRD's behavioral statement and the Contract's surface statement disagree, I followed
the PRD's behavior. The Contract is followed for names, signatures and types, which no PRD
statement contradicts.

### 1. Maximum Content-Length digits
- PRD FP-01, Boundary (line 105): "Every value of at most 18 digits is accepted; the maximum digit count is … from 18 to 32 inclusive."
- Contract, Events (line 46): "A `Content-Length` value longer than 16 digits is refused."
- **Built:** 18 digits. Values of up to 18 digits are accepted and longer ones are refused. (16 is outside the PRD's own 18–32 range, and the PRD says at most 18 must be accepted.)

### 2. Default incomplete-event size limit
- PRD FP-05, Normal (line 210): "The default is a fixed value … at least 14 kibibytes and less than 18 kibibytes."
- Contract, `Connection` signature (line 76): "When it is omitted, the limit is 8 kibibytes."
- **Built:** 16 KiB default (inside the PRD range). `Connection(role, max)` still uses `max` when given.

### 3. Hexadecimal digits in a chunk-size line
- PRD FP-03, Normal, chunked bullet (line 151): "A received size line may carry up to 64 hexadecimal digits."
- PRD FP-03, Normal (line 161) and Boundary (line 168): a fixed maximum "from 16 to 32 inclusive"; more digits are refused.
- **Built:** 32 digits. Line 151's 64 is outside the range that lines 161 and 168 set.

### 4. Whitespace after a chunk size
- PRD FP-03, Normal (line 161): the size line may be "optionally followed by spaces or tabs, then the line ending."
- PRD FP-03, Boundary (line 168): "Whitespace after the chunk size is refused."
- **Built:** spaces and tabs after the size (and any extension) are accepted, following the grammar in line 161. `1a \r\n` parses as 0x1a.

### 5. Lone line feed as a line ending
- PRD FP-02, Normal (line 129): received header blocks that use a lone LF "are accepted."
- Contract, `receive_data` (line 98): "every received line must end with a carriage return and line feed."
- **Built:** lone LF is accepted in request/status lines, header blocks, trailers and chunk-size lines. The CRLF after chunk data is still required exactly.

### 6. Status line without a reason phrase
- PRD FP-02, Normal (line 129): "A response status line that omits the reason phrase is accepted and the reason is empty."
- Contract, `next_event()` (line 100): "A received status line with no reason phrase after its status code is illegal."
- **Built:** accepted; `reason` is `b""`. Outgoing status lines always have the space: `HTTP/1.1 200 ` plus the reason, which is empty when none was given.

### 7. Obsolete line folding
- PRD FP-02, Normal (line 130): folding "is accepted when reading headers."
- PRD FP-02, Boundary (line 136): "A continuation line … is refused."
- **Built:** folding is accepted on read, joining with one space. Refusal of continuation lines is not implemented, because the Normal statement describes the feature in detail.

### 8. Control bytes in header values
- PRD FP-01, Normal (line 95): values may contain "any byte other than NUL, carriage return, line feed, form feed, and vertical tab, including other control bytes."
- PRD FP-01, Boundary (line 102): "Control bytes other than tab are refused in header values."
- **Built:** refused. Any control byte (0x00–0x1F and 0x7F) other than tab is refused, along with leading or trailing space/tab. Obs-text (0x80–0xFF) is allowed.

### 9. Framing headers on a response to HEAD
- PRD FP-02, Normal (line 122): "A response to HEAD is written with no framing headers."
- PRD FP-03, Normal (line 159): "A server answering HEAD writes the same framing headers it would have used for GET: chunked when the peer is HTTP/1.1, and connection-close framing when the peer is HTTP/1.0."
- **Built:** line 159, which is the more specific rule. A HEAD response gets the GET framing header (`Transfer-Encoding: chunked` for a 1.1 peer, none plus `Connection: close` for a 1.0 peer). No body bytes are ever produced for HEAD: the end-of-message is empty, and Data is refused as a local protocol error.

### 10. `Content-Length: 0` on a response
- PRD FP-03, Normal (line 152): the Content-Length header "is kept on the wire, including when N is 0."
- PRD FP-03, Normal (line 158): "A response with `Content-Length: 0` is sent without that header, since its body is empty."
- **Built:** line 152, which states the general rule for Content-Length framing. The header is kept. (Line 158 is applied only to 204/304 and HEAD, which have an empty body regardless: for 204/304, all framing headers are dropped from the wire.)

### 11. Which framing header wins on a response
- PRD FP-01, Normal (line 94): "When an event carries both framing headers, the `Content-Length` decides how the body is framed."
- PRD FP-03, Normal (line 156): "If a response is constructed with both `Transfer-Encoding: chunked` and `Content-Length`, transfer-encoding wins."
- **Built:** on responses (constructed or received), Transfer-Encoding wins and Content-Length is not sent. On requests, Content-Length decides; Transfer-Encoding is then not sent on the wire. The FP-01 rule is applied to requests and line 156 to responses, since 156 is the more specific statement.

### 12. Case sensitivity of `100-continue`
- PRD FP-07, Normal (line 249): an `Expect` header that "contains the token `100-continue` (matched case-insensitively)" sets the flag.
- Contract, `Connection` attributes (line 89): "The `Expect` value must be exactly the lowercase token `100-continue`."
- **Built:** case-insensitive, as in the PRD.

### 13. `Expect: 100-continue` on HTTP/1.0 requests
- PRD FP-07, Normal (line 249): "An `Expect: 100-continue` header on an HTTP/1.0 request does not set either flag."
- Contract, `Connection` attributes (line 88): "any request with `Expect: 100-continue` sets it, whatever its HTTP version."
- **Built:** the PRD. Neither flag is set for HTTP/1.0 requests.

### 14. Whether the client's body ends the 100-continue wait
- PRD FP-07, Normal (line 248): "The client stays waiting for 100-continue until the server answers; its own body events do not end the wait."
- PRD FP-07, Normal (line 250): flags turn off "when the client sends any data event or its end-of-message."
- **Built:** line 248. The client's flag stays set until the server sends an informational or final response. Sending body data does not clear it.

### 15. Which 2xx status accepts CONNECT
- PRD FP-07, Normal (lines 252 and 254): "acceptance is a final response whose status is in the 2xx range"; "a 2xx response accepts CONNECT."
- PRD FP-07, Boundary (line 263): "Only status 200 accepts a CONNECT proposal; other 2xx statuses deny it."
- **Built:** any 2xx accepts CONNECT. Non-2xx final responses deny it. (This follows the Normal statements and RFC 7231 semantics; line 263 would make 201 a denial.)

### 16. Feeding bytes after a switch acceptance
- PRD FP-07, Normal (line 257): after acceptance, bytes "fed after the accepting response are never parsed as HTTP; they accumulate, in order, in trailing data."
- PRD FP-02, Boundary (line 138) and FP-06, Boundary (line 238): feeding non-empty bytes after an empty chunk "is refused at feed time as a runtime error."
- **Built:** after acceptance, non-empty feeds accumulate in trailing data even when the receive side was already closed. The runtime error applies in every other state.

### 17. Repeated `Transfer-Encoding: chunked` headers
- PRD FP-01, Normal (line 94): "Repeated `Transfer-Encoding: chunked` headers collapse to one."
- PRD FP-01, Boundary (line 106): "A second `Transfer-Encoding` header is refused with suggested status 501, even when both values are `chunked`."
- **Built:** refused with status 501. This is an additional conflict not listed in `spec/CONFLICTS.md`. Line 106 is the explicit boundary case.

## Assumptions where the spec is silent

- **Response framing with no framing headers:** a response to a 1.1 peer uses chunked (the PRD says so when the caller gives neither header). For a 1.0 peer, or before any request has been seen, it is close-delimited and gets `Connection: close`.
- **Received responses with neither framing header:** close-delimited, for any HTTP version (RFC 7230 §3.3.3). Received 204, 304 and responses to HEAD have an empty body.
- **Keep-alive:** evaluated per cycle. Any HTTP/1.0 message, any `Connection: close` token, or a close-delimited response disables it. A response that disables it gets its `Connection` header rewritten to one header that ends in `close`, with `keep-alive` tokens removed. A server response is also treated as disabled when the request was not seen, or when the received request was in error (remote protocol error).
- **Remote protocol error during a message:** the server may still send a response. It goes out with `Connection: close` (see FP-05).
- **Upgrade proposal:** any request carrying an `Upgrade` header counts, whatever its value. A 101 accepts it only when it was requested. An informational 101 without a pending proposal is an ordinary informational response.
- **Switch-related states:** when the server accepts, both roles are set to SWITCHED_PROTOCOL in the same Connection object. When the client pulls the accepting response, the client's own state changes too.
- **Client EOM with a pending proposal:** the client goes to MIGHT_SWITCH_PROTOCOL only if the server has not yet answered. Otherwise it goes to DONE.
- **Status code range:** received status codes are 100–999 (three digits). Constructed 1xx responses must be 100–199, and final responses 200–999.
- **Received version:** only HTTP/1.0 and HTTP/1.1 are accepted on the wire, as a remote protocol error (status 400) otherwise. Constructed events accept any `d.d` version, but only 1.1 can be sent (a refused send).
- **Chunk-size line:** not subject to the incomplete-event size limit, since it is not a request/response line or header block. Trailer blocks after the last chunk are subject to the limit.
- **Empty chunks:** a zero-length `Data` is not written for chunked framing, because it would terminate the body. Zero-length data sends nothing in any framing.
- **Send of non-buffer payloads:** `send()` requires bytes-like Data payloads (TypeError otherwise). `send_with_data_passthrough()` accepts any object with a length and returns it by identity.
- **Request framing:** a received request with both framing headers uses Content-Length. Received requests without framing headers have an empty body.
- **Trailers:** received trailers are normalized like headers. Trailers may not be sent to an HTTP/1.0 peer, or with Content-Length or close-delimited framing.
- **Exceptions:** `Connection(role)` with a bad role raises `ValueError`. Feeding bytes after the receive side closed raises `httpwire.ReceiveAfterCloseError` (a `RuntimeError` subclass). `LocalProtocolError` and `RemoteProtocolError` derive from a private `ProtocolError` base, which is not a package-root name.
- **Headers container:** `Headers` iterates as lowercase pairs and supports indexing, `len`, comparison with a list of pairs, and `raw_items()`. It is reachable as `event.headers` and is not a package-root name.
- **Event equality:** events compare by type and fields. This is a convenience beyond the spec.
- **Python 3.8 compatibility:** the code avoids 3.9+ syntax and APIs. It was run on Python 3.13 only (see below).

## Verification

- `python3 -m pytest tests/` — 33 tests covering construction rules, header normalization, round trips, chunking and chunk marks, passthrough identity, Content-Length and chunked framing, HEAD, 1.0 and close-delimited bodies, keep-alive and cycle reuse, pipelining, 100-continue flags, CONNECT/Upgrade acceptance and denial, protocol errors, the size limit, and close handling. All pass on Python 3.13.
- The packaging metadata parses as TOML. I did not run a build or editable install.
