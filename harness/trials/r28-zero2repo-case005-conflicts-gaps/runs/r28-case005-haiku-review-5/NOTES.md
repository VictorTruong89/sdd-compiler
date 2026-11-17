# httpwire build notes

This file records where the specification in `spec/` disagrees with itself, what
the code does for each disagreement, and what the specification leaves unstated.
Line numbers refer to the files as they are in `spec/` (the same numbers that
`spec/CONFLICTS.md` uses). `spec/` itself has not been changed.

Layout: the package is `httpwire/` at the repository root (flat layout, per
`spec/Hardware_Requirements.md`). `pyproject.toml` is a minimal setuptools
build with no runtime dependencies. Modules:

- `httpwire/_sentinels.py`: roles, the nine states, `NEED_DATA`, `PAUSED`.
- `httpwire/_errors.py`: `LocalProtocolError`, `RemoteProtocolError` (both carry `error_status_hint`).
- `httpwire/_headers.py`: header normalization, `Headers` (ordinary and raw views).
- `httpwire/_events.py`: the six event types and their construction checks.
- `httpwire/_connection.py`: `Connection` (send, receive, parsing, framing, state machine).

---

## Conflicts between spec files

### 1. Maximum Content-Length digits
- `Full_PRD.md` FP-01, Boundary (line 105): "Every value of at most 18 digits is accepted; the maximum digit count is a fixed number of the implementer's choice, from 18 to 32 inclusive."
- `Interface_Contract.md`, Events (line 46): "A `Content-Length` value longer than 16 digits is refused."
- **Built:** the limit is 18 digits (`MAX_CONTENT_LENGTH_DIGITS` in `httpwire/_headers.py`). The PRD says any value of at most 18 digits must be accepted, and 18 is the lowest value its range allows. A 17- or 18-digit value is accepted; a 19-digit value is refused.

### 2. Default incomplete-event size limit
- `Full_PRD.md` FP-05, Normal behavior (line 210): the default is "at least 14 kibibytes and less than 18 kibibytes."
- `Interface_Contract.md`, `Connection` signature (line 76): "When it is omitted, the limit is 8 kibibytes."
- **Built:** the default is 16 KiB (`DEFAULT_MAX_INCOMPLETE_EVENT_SIZE` in `httpwire/_connection.py`). The contract's 8 KiB is below the PRD's stated minimum for the default. An explicit `max_incomplete_event_size` argument is used as given.

### 3. Hexadecimal digits in a chunk-size line
- `Full_PRD.md` FP-03, chunked bullet (line 151): "A received size line may carry up to 64 hexadecimal digits."
- `Full_PRD.md` FP-03, Normal behavior (line 161): the limit is "a fixed number of digits of the implementer's choice, from 16 to 32 inclusive"; Boundary (line 168) refuses "more hexadecimal digits than that maximum."
- **Built:** 32 digits (`MAX_CHUNK_SIZE_DIGITS`). Two statements (lines 161 and 168) agree on a range of 16 to 32, and 32 is the top of that range. A size line of 33 or more digits is refused as a remote protocol error.

### 4. Whitespace after a chunk size
- `Full_PRD.md` FP-03, Normal behavior (line 161): the size line may be "optionally followed by spaces or tabs, then the line ending."
- `Full_PRD.md` FP-03, Boundary (line 168): "Whitespace after the chunk size is refused."
- **Built:** spaces and tabs after the size are allowed, as line 161 describes the accepted grammar. A chunk extension (`;...`) is parsed and discarded.

### 5. Lone line feed as a line ending
- `Full_PRD.md` FP-02, Normal behavior (line 129): "Received header blocks that use a lone line feed ... as line endings are accepted."
- `Interface_Contract.md`, `receive_data` (line 98): "every received line must end with a carriage return and line feed."
- **Built:** lone LF is accepted in request, status, and header lines (the PRD's leniency). Chunk framing (`CRLF` after chunk data) is strict, because the PRD requires exactly CRLF there.

### 6. Status line without a reason phrase
- `Full_PRD.md` FP-02, Normal behavior (line 129): "A response status line that omits the reason phrase is accepted and the reason is empty."
- `Interface_Contract.md`, `next_event()` (line 100): "A received status line with no reason phrase after its status code is illegal."
- **Built:** accepted, with `reason == b""`. Both `HTTP/1.1 200` and `HTTP/1.1 200 ` are accepted. The PRD's normal-behavior statement is the more specific one.

### 7. Obsolete line folding
- `Full_PRD.md` FP-02, Normal behavior (line 130): folding "is accepted when reading headers: each continuation line ... is joined to the previous header's value."
- `Full_PRD.md` FP-02, Boundary (line 136): "A continuation line (a header line that begins with a space or tab) is refused."
- **Built:** accepted when reading (`_parse_field_lines`). The continuation is joined to the previous value with one space. A folded line with no preceding header is refused.

### 8. Control bytes in header values
- `Full_PRD.md` FP-01, Normal behavior (line 95): values "may contain any byte other than NUL, carriage return, line feed, form feed, and vertical tab, including other control bytes and non-ASCII bytes."
- `Full_PRD.md` FP-01, Boundary (line 102): "Control bytes other than tab are refused in header values."
- **Built:** refused. Bytes 0x00-0x1F except tab, and 0x7F (DEL), are refused. Non-ASCII bytes 0x80-0xFF are allowed. I chose the boundary rule because it matches the RFC 7230 field-content grammar. The refused set is a superset of the PRD's named exclusions (NUL, CR, LF, FF, VT), so every byte the PRD names is still refused. The same check applies to trailers, and the reason phrase uses the same set of refused control bytes.

### 9. Framing headers on a response to HEAD
- `Full_PRD.md` FP-02, Normal behavior (line 122): "A response to HEAD is written with no framing headers."
- `Full_PRD.md` FP-03, Normal behavior (line 159): "A server answering HEAD writes the same framing headers it would have used for GET: chunked when the peer is HTTP/1.1, and connection-close framing when the peer is HTTP/1.0."
- **Built:** the FP-03 rule. The framing headers are chosen as for GET (`Transfer-Encoding: chunked` for an HTTP/1.1 peer, `Connection: close` for an HTTP/1.0 peer). No body bytes are sent and the end-of-message is empty. FP-03 is the section that addresses framing directly. A `Content-Length` that the caller set is kept.

### 10. Content-Length: 0 on a response
- `Full_PRD.md` FP-03, Normal behavior (line 152): "The `Content-Length` header is kept on the wire, including when N is 0."
- `Full_PRD.md` FP-03, Normal behavior (line 158): "A response with `Content-Length: 0` is sent without that header, since its body is empty."
- **Built:** kept (line 152). Line 158 sits in the bullet about HEAD, 204, and 304, which are already empty-body cases, so it reads as a statement about those situations. Line 152 is the general rule for Content-Length responses.

### 11. Which framing header wins on a response
- `Full_PRD.md` FP-01, Normal behavior (line 94): "When an event carries both framing headers, the `Content-Length` decides how the body is framed."
- `Full_PRD.md` FP-03, Normal behavior (line 156): "If a response is constructed with both `Transfer-Encoding: chunked` and `Content-Length`, transfer-encoding wins: Content-Length is not sent."
- **Built:** on send, a response with both headers uses chunked framing and drops Content-Length (line 156 is response-specific). On receive, Content-Length decides for all pulled events, including responses (line 94). Requests with both headers are framed by Content-Length on send and on receive, and both headers are written as the caller gave them.

### 12. Case sensitivity of `100-continue`
- `Full_PRD.md` FP-07, Normal behavior (line 249): the token `100-continue` is "matched case-insensitively."
- `Interface_Contract.md`, `Connection` attributes (line 89): "The `Expect` value must be exactly the lowercase token `100-continue`."
- **Built:** case-insensitive, as line 249 says.

### 13. `Expect: 100-continue` on HTTP/1.0 requests
- `Full_PRD.md` FP-07, Normal behavior (line 249): "An `Expect: 100-continue` header on an HTTP/1.0 request does not set either flag."
- `Interface_Contract.md`, `Connection` attributes (line 88): "any request with `Expect: 100-continue` sets it, whatever its HTTP version."
- **Built:** an HTTP/1.0 request does not set either flag (the PRD).

### 14. Whether the client's body ends the 100-continue wait
- `Full_PRD.md` FP-07, Normal behavior (line 248): "The client stays waiting for 100-continue until the server answers; its own body events do not end the wait."
- `Full_PRD.md` FP-07, Normal behavior (line 250): the flags turn off "when the client sends any data event or its end-of-message."
- **Built:** the flag stays set until the server sends an informational or final response (line 248). Client data does not clear it. Line 250 lists the server-side triggers as well, and both are implemented there. Only the client-data trigger is dropped.

### 15. Which 2xx status accepts CONNECT
- `Full_PRD.md` FP-07, Normal behavior (lines 252 and 254): "acceptance is a final response whose status is in the 2xx range"; "a 2xx response accepts CONNECT."
- `Full_PRD.md` FP-07, Boundary (line 263): "Only status 200 accepts a CONNECT proposal; other 2xx statuses deny it."
- **Built:** only 200 accepts CONNECT. Any other final response, including 201 through 299, is a denial. The boundary statement is the more specific one and uses the word "only".

### 16. Feeding bytes after a switch acceptance
- `Full_PRD.md` FP-07, Normal behavior (line 257): after acceptance, "Bytes stored or fed after the accepting response are never parsed as HTTP; they accumulate, in order, in trailing data."
- `Full_PRD.md` FP-02, Boundary (line 138), and FP-06, Boundary (line 238): feeding a non-empty chunk after an empty chunk "is refused at feed time as a runtime error."
- **Built:** after an accepted switch, non-empty bytes accumulate in trailing data, even after an empty chunk has been fed. The switch-specific statement (line 257) overrides the general runtime-error rule. Before any switch is accepted, the runtime error applies as written.

---

## Points the specification does not state (assumptions)

- **Keep-alive and close handling.** Keep-alive needs both sides to be HTTP/1.1, with no `Connection: close` token on either request or response. A server response to a request it has not yet pulled (no request seen) counts as "not keep-alive", so `Connection: close` is added and the state goes to MUST_CLOSE.
- **Response rewriting for close.** When keep-alive is off, the server's response gets `Connection: close`. Any `keep-alive` token is removed, and other tokens (such as `Upgrade`) are kept. The rewritten header is written with the canonical name `Connection`.
- **Added framing headers.** A response whose body length is unknown gets `Transfer-Encoding: chunked` (HTTP/1.1 peer) or no framing header plus `Connection: close` (HTTP/1.0 peer). Added names are canonical: `Transfer-Encoding`, `Connection`.
- **Close-delimited responses on receive.** A response with neither framing header is close-delimited for every peer version (RFC 7230 §3.3.3), not only HTTP/1.0 peers. Empty-body responses (HEAD, 204, 304) are body-less regardless of headers. A response to HEAD does not record a body.
- **Trailers on empty bodies.** Trailers on an end-of-message for a body-less response, a Content-Length body, or a close-delimited body are refused as local protocol errors.
- **HTTP version on read.** Only `HTTP/1.0` and `HTTP/1.1` are accepted when reading. Other versions are refused with suggested status 400. A status code below 100 or above 999 is refused.
- **Status-line regex.** The status code must be exactly three digits. Reason bytes that are control bytes (other than tab) are refused.
- **Request-line target.** The target must be visible ASCII (bytes 0x21-0x7E). A request line that does not match is refused with status 400.
- **Chunk framing limits.** A chunk-size line with no line feed in the buffer, longer than the incomplete-event limit, is refused as a remote protocol error (status 400). Trailer blocks that exceed the limit get status 431.
- **Chunk marks.** `chunk_start` is set on the first piece of a chunk and `chunk_end` on the piece that completes it. A zero-size chunk is the final chunk, and its end-of-message carries any trailers.
- **Close-delimited body end.** The end of a close-delimited body is an end-of-message, followed by a connection-closed event when the peer's close is pulled again.
- **Data-type handling.** `send()` requires a bytes-like payload. A payload that is a non-bytes object with a length is accepted only by `send_with_data_passthrough()`. Calling `send()` with such an object raises `TypeError`, not a protocol error, and changes no state. A `str` payload is refused as a local protocol error.
- **Protocol-error state changes.** Any `LocalProtocolError` raised by `send` moves our side to ERROR (the spec's rule for refused sends). Any `RemoteProtocolError` raised by a pull moves their side to ERROR and makes later pulls fail with the same status hint.
- **Switch details.** On CONNECT acceptance or Upgrade acceptance, the accepting response gets no added framing headers and no body. Denial (any final response for a pending proposal) clears both proposal flags; a client still in MIGHT_SWITCH_PROTOCOL then moves to DONE.
- **Expect flags across cycles.** The 100-continue flags are per cycle and reset by `start_next_cycle()`. `their_http_version` is kept across cycles and overwritten by the next pulled request (server) or response (client).
- **Peer HTTP version on the client.** The client records the peer's version from a pulled final response, the same way the server records it from a pulled request.
- **Requests with both framing headers.** Both headers are written as given. Framing (on send and on receive) uses Content-Length.
- **Host header.** A request whose method or target is unusual is still checked for exactly one Host when the version is 1.1. Host is written first on the wire; the other headers keep the caller's order.
- **Reason phrase.** The status line is always written as `HTTP/1.1 <code> <reason>` followed by CRLF. With an empty reason this gives a trailing space (`HTTP/1.1 200 `). The parser accepts both that and the form without the space.
- **Header value bytes.** A value's leading and trailing space or tab is refused (not stripped) when constructing events. On read, values are stripped of leading and trailing space and tab, as RFC 7230 OWS allows.
- **Duplicate Content-Length.** Duplicate values, or comma-separated pieces that are all equal as integers, collapse to one header. The first occurrence's name spelling is kept, and its value text is kept as given. Empty list elements are ignored.
- **Event equality.** Event instances compare equal when they have the same type and field values (header comparison uses the raw spelling).
- **Pulling with an empty buffer after end-of-receive.** When the peer's close is fed and nothing else is stored, an idle or done peer yields a connection-closed event. A peer that is in the middle of a message (a head, a Content-Length body, or a chunked body) gives a remote protocol error.
- **Paused states.** After a remote error, a further pull raises the same kind of error again. Pulls return PAUSED when the peer is in DONE or MUST_CLOSE with bytes stored, or in MIGHT_SWITCH_PROTOCOL, or after a switch. Pulls return the connection-closed event again once the peer has closed.
- **`start_next_cycle` refusal.** The refusal raises `LocalProtocolError` and changes nothing (the spec's rule). Both sides must be DONE for the refusal not to happen.
- **Constructor role check.** `Connection(role)` with a role other than `CLIENT` or `SERVER` raises `ValueError`. No object is returned.
- **Error hints.** The `error_status_hint` on errors from event construction is 400, except for a Transfer-Encoding value other than exactly `chunked` (or a second Transfer-Encoding header), which is 501. The incomplete-event limit gives 431.
- **Python version.** The code avoids syntax newer than Python 3.8 (no walrus operator, no `match`, no builtin generics). Testing was done on Python 3.13 only.
