# NOTES — httpwire build

This file records where the specification in `spec/` disagrees with itself, what was built for each
disagreement, and what the specification leaves unstated. "PRD" means `spec/Full_PRD.md`; "Interface"
means `spec/Interface_Contract.md`.

## 1. Conflicts and the choice made

### C1. Content-Length digit limit
- PRD FP-01, Normal behavior: "Every value of at most 18 digits is accepted; the maximum digit count is a
  fixed number of the implementer's choice, from 18 to 32 inclusive."
- Interface, Events section (the `headers` row): "A `Content-Length` value longer than 16 digits is refused."
- **Built:** 16 digits (`_events.MAX_CONTENT_LENGTH_DIGITS`). The Interface's concrete limit wins over the
  PRD's range. A 17- or 18-digit value is refused.

### C2. Chunk-size digit limit
- PRD FP-03, Normal behavior (chunked bullet): "A received size line may carry up to 64 hexadecimal digits."
- PRD FP-03, chunk-size paragraph: the maximum is "a fixed number ... from 16 to 32 inclusive"; FP-03
  Boundary: more digits than that maximum are refused.
- **Built:** 32 digits (`connection.MAX_CHUNK_SIZE_DIGITS`). The 64 figure falls outside the 16–32 rule the
  spec sets for the implementer's choice.

### C3. Default incomplete-event size limit
- Interface, `Connection` signature: "When it is omitted, the limit is 8 kibibytes."
- PRD FP-05: "The default is a fixed value ... at least 14 kibibytes and less than 18 kibibytes."
- **Built:** 8 KiB (`connection.DEFAULT_MAX_INCOMPLETE_EVENT_SIZE`). The explicit signature default wins.
  Passing `max_incomplete_event_size` overrides it.

### C4. Lone line feed on receive
- PRD FP-02, Normal behavior: "Received header blocks that use a lone line feed ... are accepted."
- Interface, `receive_data`/`next_event`: "every received line must end with a carriage return and line feed."
- **Built:** lone LF accepted in header blocks and chunk-size lines. A chunk's data must be followed by exactly
  CRLF (PRD FP-03 Boundary).

### C5. Control bytes in header values
- PRD FP-01, Normal behavior: values may hold "any byte other than NUL, carriage return, line feed, form feed,
  and vertical tab, including other control bytes."
- PRD FP-01, Boundary: "Control bytes other than tab are refused in header values."
- **Built:** the Normal rule. Only NUL, CR, LF, VT, and FF are refused, plus leading or trailing space/tab.

### C6. Obsolete line folding on read
- PRD FP-02, Normal behavior: continuation lines are "joined to the previous header's value."
- PRD FP-02, Boundary: "A continuation line ... is refused."
- **Built:** accepted and joined with one space. A continuation line with no previous header is refused.

### C7. Repeated `Transfer-Encoding` headers
- PRD FP-01, Normal behavior: "Repeated `Transfer-Encoding: chunked` headers collapse to one."
- PRD FP-01, Boundary, and FP-05: a second `Transfer-Encoding` header is refused with status 501 "even when both
  values are `chunked`."
- **Built:** refused with suggested status 501. The Boundary wording is stated twice.

### C8. CONNECT acceptance status
- PRD FP-07, Normal behavior: "a 2xx response accepts CONNECT."
- PRD FP-07, Boundary: "Only status 200 accepts a CONNECT proposal; other 2xx statuses deny it."
- **Built:** only 200 accepts CONNECT. Other 2xx statuses are a denial, and HTTP/1.1 continues.

### C9. Status line with no reason phrase
- PRD FP-02, Normal behavior: "A response status line that omits the reason phrase is accepted and the reason is empty."
- Interface, `next_event`: "A received status line with no reason phrase after its status code is illegal."
- **Built:** accepted, with an empty reason. Both `HTTP/1.1 200` and `HTTP/1.1 200 ` parse.

### C10. Framing headers on a response to HEAD
- PRD FP-02, Normal behavior: "A response to HEAD is written with no framing headers."
- PRD FP-03: "A server answering HEAD writes the same framing headers it would have used for GET: chunked when the
  peer is HTTP/1.1, and connection-close framing when the peer is HTTP/1.0."
- **Built:** FP-03. The HEAD response gets the GET framing headers (`Transfer-Encoding: chunked` for an HTTP/1.1
  peer). Its body is always empty, and end-of-message writes no bytes.

### C11. `Content-Length: 0` on responses
- PRD FP-03, Normal behavior: "The `Content-Length` header is kept on the wire, including when N is 0."
- PRD FP-03, empty-body paragraph: "A response with `Content-Length: 0` is sent without that header, since its body
  is empty."
- **Built:** both rules, each in its own context. Ordinary responses keep `Content-Length: 0`. The header is dropped
  only for the empty-body situations (HEAD, 204, 304), where the spec puts the sentence.

### C12. Client's 100-continue flag and its own body
- PRD FP-07, Normal behavior: "The client stays waiting for 100-continue until the server answers; its own body
  events do not end the wait."
- PRD FP-07, flag paragraph: flags "turn off ... when the client sends any data event or its end-of-message."
- **Built:** on the client-role connection, `client_is_waiting_for_100_continue` stays True through the client's own
  body. On the server-role connection, `they_are_waiting_for_100_continue` clears when the server pulls the
  client's data or end-of-message. `client_is_waiting_for_100_continue` on the server side also stays True until
  the server answers.

### C13. Case rules for `Expect: 100-continue`
- PRD FP-07: the token is "matched case-insensitively."
- Interface, `they_are_waiting_for_100_continue`: "The `Expect` value must be exactly the lowercase token `100-continue`."
- **Built:** `client_is_waiting_for_100_continue` is case-insensitive. `they_are_waiting_for_100_continue` requires the
  exact lowercase token. A request with `Expect: 100-Continue` therefore sets only the client flag.

### C14. Whitespace in chunk-size lines
- PRD FP-03, chunk-size paragraph: the size line is hex, "optionally followed by a chunk extension ..., optionally
  followed by spaces or tabs, then the line ending."
- PRD FP-03, Boundary: "Whitespace after the chunk size is refused."
- **Built:** whitespace directly after the hex digits is refused. Whitespace after a `;` extension is allowed,
  since the extension is discarded.

### C15. Which framing header wins
- PRD FP-01: "When an event carries both framing headers, the Content-Length decides how the body is framed."
- PRD FP-03, response rule: "If a response is constructed with both `Transfer-Encoding: chunked` and `Content-Length`,
  transfer-encoding wins."
- **Built:** Content-Length decides for requests and for every received message. For a response we send, we follow
  the response rule: the wire gets `Transfer-Encoding` only, and `Content-Length` is dropped.
  For a request that carries both, the wire keeps both headers and framing follows Content-Length. The spec says
  nothing about dropping either header there.

## 2. Gaps: things the spec does not state

- **Receive-side whitespace.** Optional whitespace around a header value is stripped on read (RFC 7230 §3.2.4).
  Only values the caller constructs are refused for leading or trailing whitespace.
- **Upgrade proposal.** Any request carrying an `Upgrade` header (any HTTP version) proposes a switch. The
  `Connection: upgrade` token is not required. A 101 with no pending Upgrade proposal is an ordinary informational
  response.
- **Acceptance timing.** A server may accept CONNECT or Upgrade before the client has finished sending its body.
  Acceptance then moves both sides to SWITCHED_PROTOCOL.
- **Unknown peer version.** Until a request has been seen, the peer version is unknown. Responses are then sent
  close-delimited with `Connection: close`, because keep-alive requires both sides to speak HTTP/1.1.
- **Response framing.** A response to an HTTP/1.1 peer with no framing headers is sent chunked. For HTTP/1.0 peers
  it is close-delimited with `Connection: close`. A received response with neither framing header (other than
  HEAD, 204, 304, or 1xx) is close-delimited regardless of its version (RFC 7230 §3.3.3).
- **Trailers.** Trailing headers are refused whenever the body is not chunked (including empty bodies) and whenever
  the peer is HTTP/1.0. Trailers go through the same normalization as other headers.
- **Content-Length canonical form.** Stored as a canonical integer string. Duplicate values are compared numerically,
  so `05` and `5` agree. The first Content-Length header keeps its position.
- **Connection header rewrite.** When keep-alive is disabled on a response, all `Connection` headers collapse into one
  placed where the first one was. Its tokens are the old ones minus `keep-alive`, plus `close`.
- **Received versions.** Only `HTTP/1.0` and `HTTP/1.1` are accepted in received start lines. Other versions are a
  remote protocol error.
- **Empty reason.** An empty reason is written as `HTTP/1.1 200 \r\n` (trailing space), following the status-line
  grammar.
- **Non-bytes-like Data.** `send()` refuses a non-bytes-like payload with `LocalProtocolError`.
  `send_with_data_passthrough()` returns the object itself as one piece.
- **Non-event argument.** `send()` with a non-event raises `TypeError`, which is not a protocol error.
  A bad role raises `ValueError`.
- **No-bytes passthrough.** `send_with_data_passthrough()` returns `[]` for events that produce no bytes.
- **Unsolicited response.** A client-role connection parses a response when the server is IDLE (the server may send
  an unsolicited final response, PRD FP-04).
- **Paused and closed.** When the peer is DONE or MUST_CLOSE and bytes are stored, pulls return PAUSED. With nothing
  stored and the receive side closed, pulls return ConnectionClosed. A close while the peer is expected to
  respond is a remote protocol error.
- **Chunk-size line length.** With no line feed yet, a chunk-size line is limited to the same
  `max_incomplete_event_size` as a header block (the spec does not state a limit for chunk-size lines).
- **Request framing.** A request carries no body unless it has `Content-Length` or `Transfer-Encoding: chunked`.
  Without either, the body is empty and an end-of-message is pulled immediately.
- **Keep-alive after HTTP/1.0 response.** A pulled HTTP/1.0 response disables keep-alive for the cycle, so both sides
  end in MUST_CLOSE when they reach DONE.
- **Error status hints.** Protocol errors default to 400. Transfer-Encoding problems use 501, and the size limit uses
  431.
- **Bytes after receive close.** Feeding non-empty data after an empty chunk raises `ReceiveClosedError`, a
  `RuntimeError` subclass that is neither a local nor a remote protocol error.
- **Error after failed pull.** After a remote protocol error the peer side is ERROR. Its local side is not changed,
  and the next send still works and carries `Connection: close`.

## 3. Layout and testing

- `httpwire/` is the importable package at the repository root. `pyproject.toml` builds it with setuptools and has
  no runtime dependencies.
- `tests/test_httpwire.py` covers events, normalization, framing, keep-alive, errors, and protocol switching.
  Run with `python3 -m pytest tests/` or `python3 -m unittest discover -s tests`.
- The code is written for Python 3.8+ (no `match`, no runtime generics). It was tested only on Python 3.13 in
  this environment.
