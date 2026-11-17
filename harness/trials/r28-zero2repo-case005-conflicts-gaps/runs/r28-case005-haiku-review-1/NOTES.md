# httpwire implementation notes

This file records where the specification in `spec/` disagrees with itself, where it is silent,
and what the code does in each case. `spec/` itself is unchanged.

Line numbers below refer to the spec files as they are in `spec/`.

## Layout

- `httpwire/` — the package (`_util.py` sentinels and errors, `_events.py` events and header
  normalization, `_connection.py` the state machine, `__init__.py` the public names).
- `pyproject.toml` — setuptools metadata for a flat layout, zero dependencies.
- `conftest.py` — empty marker at the repo root so pytest puts `/app` on `sys.path` and `import httpwire` works.
- `tests/test_httpwire.py` — behavioral tests. Run with `python3 -m pytest tests` or `PYTHONPATH=/app python3 tests/test_httpwire.py` (54 tests, all passing).

## Conflicts between spec files

Where two statements cannot both hold, the rule used is: the PRD's explicit behavior wins over the
Interface Contract's incidental values, and the more specific statement wins over a general one.
Where the spec gives an allowed range, the chosen value sits inside that range.

### C1. Maximum Content-Length digits
- `Full_PRD.md` FP-01 Boundary, line 105: "Every value of at most 18 digits is accepted; the maximum digit count is a fixed number ... from 18 to 32 inclusive."
- `Interface_Contract.md` Events, line 46: "A `Content-Length` value longer than 16 digits is refused."
- **Built:** 18 digits. 16 is outside the PRD's allowed range of 18–32, and the PRD says every value of at most 18 digits must be accepted. Values of 19+ digits are refused (`LocalProtocolError`).

### C2. Default incomplete-event size limit
- `Full_PRD.md` FP-05 Normal, line 210: "The default is a fixed value ... at least 14 kibibytes and less than 18 kibibytes."
- `Interface_Contract.md` `Connection` Signature, line 76: "When it is omitted, the limit is 8 kibibytes."
- **Built:** 16 KiB default (16384 bytes), within the PRD range. An explicit `max_incomplete_event_size` argument is used as given.

### C3. Hexadecimal digits in a chunk-size line
- `Full_PRD.md` FP-03 Normal, chunked bullet, line 151: "A received size line may carry up to 64 hexadecimal digits."
- `Full_PRD.md` FP-03 Normal, line 161: "at most a fixed number of digits ..., from 16 to 32 inclusive"; FP-03 Boundary, line 168: refuses "more hexadecimal digits than that maximum."
- **Built:** 32 digits (the top of the 16–32 range). A size line with 33 or more digits is a remote protocol error. 64 digits is not accepted.

### C4. Whitespace after a chunk size
- `Full_PRD.md` FP-03 Normal, line 161: the size line may be "optionally followed by spaces or tabs, then the line ending."
- `Full_PRD.md` FP-03 Boundary, line 168: "Whitespace after the chunk size is refused."
- **Built:** whitespace is allowed (line 161 defines the grammar; line 168 is the boundary list). `1a \r\n` parses as size `0x1a`. Chunk extensions are parsed and discarded.

### C5. Lone line feed as a line ending
- `Full_PRD.md` FP-02 Normal, line 129: "Received header blocks that use a lone line feed ... are accepted."
- `Interface_Contract.md` `receive_data`, line 98: "every received line must end with a carriage return and line feed."
- **Built:** lone LF is accepted in request, status, and header lines (and trailers, and chunk-size lines). Chunk *data* must be followed by exactly CRLF (`Full_PRD.md` FP-03 Boundary, line 168), so a bare LF there is refused.

### C6. Status line without a reason phrase
- `Full_PRD.md` FP-02 Normal, line 129: "A response status line that omits the reason phrase is accepted and the reason is empty."
- `Interface_Contract.md` `next_event()`, line 100: "A received status line with no reason phrase after its status code is illegal."
- **Built:** accepted, with an empty reason (the PRD's explicit statement, and consistent with C5).

### C7. Obsolete line folding
- `Full_PRD.md` FP-02 Normal, line 130: folding "is accepted when reading headers".
- `Full_PRD.md` FP-02 Boundary, line 136: "A continuation line (a header line that begins with a space or tab) is refused."
- **Built:** folding is accepted. The continuation is joined to the previous value with one space, and its leading whitespace is removed. A continuation with no preceding header is refused. The explicit allowance in line 130 is more specific than the general refusal in line 136.

### C8. Control bytes in header values
- `Full_PRD.md` FP-01 Normal, line 95: values "may contain any byte other than NUL, carriage return, line feed, form feed, and vertical tab, including other control bytes".
- `Full_PRD.md` FP-01 Boundary, line 102: "Control bytes other than tab are refused in header values."
- **Built:** the boundary rule. Control bytes (0x00–0x1F except HTAB) and DEL (0x7F) are refused in header values, reason phrases, and request targets. Non-ASCII bytes (0x80–0xFF) are allowed. This matches RFC 7230's field-value grammar.

### C9. Framing headers on a response to HEAD
- `Full_PRD.md` FP-02 Normal, line 122: "A response to HEAD is written with no framing headers."
- `Full_PRD.md` FP-03 Normal, line 159: "A server answering HEAD writes the same framing headers it would have used for GET: chunked when the peer is HTTP/1.1, and connection-close framing when the peer is HTTP/1.0."
- **Built:** line 159 (the more specific framing rule). For HEAD, the server writes the framing headers it would write for GET: `Transfer-Encoding: chunked` for a 1.1 peer, or no framing header plus `Connection: close` for a 1.0 peer. The body is always empty, so no body bytes are written and `EndOfMessage` encodes as nothing.

### C10. `Content-Length: 0` on a response
- `Full_PRD.md` FP-03 Normal, line 152: "The `Content-Length` header is kept on the wire, including when N is 0."
- `Full_PRD.md` FP-03 Normal, line 158: "A response with `Content-Length: 0` is sent without that header, since its body is empty."
- **Built:** kept (line 152 is the explicit rule for responses with a Content-Length).

### C11. Which framing header wins on a response
- `Full_PRD.md` FP-01 Normal, line 94: "When an event carries both framing headers, the `Content-Length` decides how the body is framed."
- `Full_PRD.md` FP-03 Normal, line 156: "If a response is constructed with both `Transfer-Encoding: chunked` and `Content-Length`, transfer-encoding wins: Content-Length is not sent."
- **Built:** both rules, each for its own message type. On a *response* (send), Transfer-Encoding wins and Content-Length is dropped from the wire. On a *request* (send), Content-Length decides and Transfer-Encoding is dropped from the wire. On receive, a request's Content-Length decides and a response's Transfer-Encoding decides. The Event keeps both headers as the caller set them.

### C12. Case sensitivity of `100-continue`
- `Full_PRD.md` FP-07 Normal, line 249: the `Expect` token is "matched case-insensitively".
- `Interface_Contract.md` `Connection` attributes, line 89: "The `Expect` value must be exactly the lowercase token `100-continue`."
- **Built:** case-insensitive (PRD). `Expect: 100-Continue` sets the flags.

### C13. `Expect: 100-continue` on HTTP/1.0 requests
- `Full_PRD.md` FP-07 Normal, line 249: "An `Expect: 100-continue` header on an HTTP/1.0 request does not set either flag."
- `Interface_Contract.md` `Connection` attributes, line 88: "any request with `Expect: 100-continue` sets it, whatever its HTTP version."
- **Built:** the PRD. The flag is set only for HTTP/1.1 requests. Since httpwire only sends HTTP/1.1, this case can only arrive from a peer.

### C14. Whether the client's body ends the 100-continue wait
- `Full_PRD.md` FP-07 Normal, line 248: "The client stays waiting for 100-continue until the server answers; its own body events do not end the wait."
- `Full_PRD.md` FP-07 Normal, line 250: the flags turn off "when the client sends any data event or its end-of-message."
- **Built:** line 250. The client's flag is cleared when it sends (or pulls) a data or end-of-message event. This is a judgment call. Line 250 is the enumerated list of clearing events and matches the purpose of the flag: once the body is sent, the client is no longer waiting.

### C15. Which 2xx status accepts CONNECT
- `Full_PRD.md` FP-07 Normal, lines 252 and 254: "acceptance is a final response whose status is in the 2xx range"; "a 2xx response accepts CONNECT."
- `Full_PRD.md` FP-07 Boundary, line 263: "Only status 200 accepts a CONNECT proposal; other 2xx statuses deny it."
- **Built:** only 200 accepts CONNECT. Other 2xx responses are a denial. Line 263 is the more specific rule.

### C16. Feeding bytes after a switch acceptance
- `Full_PRD.md` FP-07 Normal, line 257: after acceptance, bytes "fed after the accepting response ... accumulate, in order, in trailing data."
- `Full_PRD.md` FP-02 Boundary, line 138, and FP-06 Boundary, line 238: feeding a non-empty chunk after an empty chunk "is refused at feed time as a runtime error." `Interface_Contract.md` `receive_data`, line 99, says the same.
- **Built:** after an accepted switch, bytes accumulate (line 257, which is specific to the switch). Before any switch, feeding after end-of-receive raises `RuntimeError`.

### C17 (not in CONFLICTS.md). Repeated `Transfer-Encoding` headers
- `Full_PRD.md` FP-01 Normal, line 94: "Repeated `Transfer-Encoding: chunked` headers collapse to one, like repeated equal `Content-Length` values."
- `Full_PRD.md` FP-01 Boundary, line 106, and FP-05 Normal, line 203: a second `Transfer-Encoding` header "even when both values are `chunked`" is refused with suggested status 501.
- **Built:** refused with 501. Two sources (lines 106 and 203) agree on this, and line 94 is the only one that says otherwise.

## Gaps: things the spec does not state

- **Default argument values for event constructors.** `headers` defaults to empty on every event type; `reason` defaults to `b""`; `http_version` defaults to `b"1.1"`; `Data` chunk marks default to `False`.
- **Empty reason phrase on the wire.** A response with an empty reason is written as `HTTP/1.1 200 \r\n` (with a trailing space), so the status line always has the same shape.
- **Received header values.** Leading and trailing spaces and tabs are stripped from received header values (RFC 7230 OWS). Construction still refuses them, as the spec says.
- **HTTP versions on receive.** Only `HTTP/1.0` and `HTTP/1.1` are accepted in request and status lines. Anything else is a remote protocol error with the default suggested status 400, not 505.
- **Requests with both Content-Length and Transfer-Encoding on the wire.** Resolved as in C11. Dropping the other header keeps the wire unambiguous.
- **Response to a 1.1 peer with no framing headers, when received.** The spec gives close-delimited framing only for HTTP/1.0 peers. The code treats a response with neither framing header as close-delimited for any peer, as RFC 7230 §3.3.3 requires. The send side still uses chunked for 1.1 peers.
- **Chunk-size line length.** A chunk-size line that has not ended, and is longer than the incomplete-event size limit, is a remote protocol error with suggested status 400 (not 431, since the limit in FP-05 is for request/response lines and header blocks).
- **Trailer block length.** Trailers that have not ended and exceed the incomplete-event limit are refused with suggested status 431.
- **Chunk-extension grammar.** An extension is `;` followed by any visible or non-ASCII bytes, plus spaces and tabs. Control bytes are refused.
- **Zero-length data events.** A zero-length `Data` event writes no bytes in any framing mode. In chunked mode it must not write a `0\r\n` chunk, because that would end the body.
- **Trailers with non-chunked framing.** Trailers on an end-of-message are refused for Content-Length, close-delimited, and empty-body framing.
- **Passthrough and `send()` payload types.** `send_with_data_passthrough` accepts any bytes-like payload, or any object with `__len__`, which is passed through by identity. `send()` requires a bytes-like payload. `str` payloads are refused in both.
- **Return values.** `send()` returns `b""` for events that write nothing, including `ConnectionClosed`. `send_with_data_passthrough()` returns `[]` for those. `send_failed()` returns `None`.
- **Refused sends.** The spec says a send refused as a local protocol error makes the sending side ERROR (FP-05). Consequently a refused `ConnectionClosed` send also makes the side ERROR.
- **Pulled 101 without an Upgrade proposal.** Treated as an ordinary informational response. Only a 101 that answers an `Upgrade` proposal accepts the switch.
- **Remote protocol errors and keep-alive.** After any remote protocol error, the keep-alive flag is cleared. A later error response from the server carries `Connection: close`.
- **Exception types not named by the spec.** Constructing a connection with a bad role or a bad size limit raises `ValueError`. Feeding bytes after end-of-receive raises `RuntimeError`.
- **Keep-alive header rewriting.** When keep-alive is off, the server's `Connection` header is rebuilt: `keep-alive` tokens are dropped and `close` is added once.
- **Peer HTTP version across cycles.** `their_http_version` is kept until the next request or response is pulled. `start_next_cycle()` does not clear it.
- **Pipelined requests after DONE with stored bytes.** Stored bytes are paused, not parsed, until the next cycle starts (FP-04). If the peer half-closes while requests are still stored, `ConnectionClosed` is pulled only after those requests are consumed (FP-06).
