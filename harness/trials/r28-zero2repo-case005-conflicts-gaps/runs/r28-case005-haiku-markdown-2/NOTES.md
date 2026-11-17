# NOTES — httpwire implementation

This file records where the specification disagrees with itself, what the
specification leaves unstated, and what the code does in each case. Line
numbers refer to the files in `spec/` as delivered.

Layout: package `httpwire/` at the repository root (flat layout, setuptools,
`pyproject.toml`). Tests: `tests/test_httpwire.py`, run with
`python3 -m unittest tests.test_httpwire` from `/app`.

## Part 1 — Conflicts between spec statements

For each conflict: what each side says, where, and what was built.

### C1. Maximum Content-Length digits
- `spec/Interface_Contract.md` line 46: "A `Content-Length` value longer than 16 digits is refused."
- `spec/Full_PRD.md` line 105 (FP-01): "Every value of at most 18 digits is accepted; the maximum digit count is a fixed number of the implementer's choice, from 18 to 32 inclusive."
- **Built:** 18 digits. Values of up to 18 digits are accepted; 19 or more are refused. This follows the PRD, which requires 18-digit values to be accepted. Values of 17 and 18 digits therefore differ from the Interface Contract.

### C2. Default incomplete-event size limit
- `spec/Interface_Contract.md` line 76: "When it is omitted, the limit is 8 kibibytes."
- `spec/Full_PRD.md` line 210 (FP-05): "The default is a fixed value ... at least 14 kibibytes and less than 18 kibibytes."
- **Built:** 8 KiB when the argument is omitted, because the Interface Contract states the exact value for that call form. Passing an explicit value is honored as given. A request for the PRD's 14–18 KiB default is not met.

### C3. Control bytes in header values
- `spec/Full_PRD.md` line 95 (FP-01 normal behavior): values may contain "any byte other than NUL, carriage return, line feed, form feed, and vertical tab, including other control bytes".
- `spec/Full_PRD.md` line 102 (FP-01 boundary): "Control bytes other than tab are refused in header values."
- **Built:** the boundary rule. Bytes 0x00–0x08, 0x0A–0x1F and 0x7F are refused in header values. Tab is allowed between other bytes. Bytes 0x80–0xFF are allowed.

### C4. Chunk-size digit limit
- `spec/Full_PRD.md` line 151 (FP-03): "A received size line may carry up to 64 hexadecimal digits."
- `spec/Full_PRD.md` line 161 (FP-03): the maximum is "a fixed number of the implementer's choice, from 16 to 32 inclusive".
- **Built:** 32 digits, the upper end of the range in line 161. Size lines with more digits are refused.

### C5. Whitespace after the chunk size
- `spec/Full_PRD.md` line 161 (FP-03): the size line is "optionally followed by a chunk extension (starting with `;`), optionally followed by spaces or tabs, then the line ending".
- `spec/Full_PRD.md` line 168 (FP-03): "Whitespace after the chunk size is refused."
- **Built:** a reconciliation. Whitespace directly after the hex digits is refused (`5 \r\n` fails). Spaces and tabs after a `;` extension are accepted (`5;x \r\n` is fine).

### C6. Content-Length: 0 on a response
- `spec/Full_PRD.md` line 152 (FP-03): "The `Content-Length` header is kept on the wire, including when N is 0."
- `spec/Full_PRD.md` line 158 (FP-03): "A response with `Content-Length: 0` is sent without that header, since its body is empty."
- **Built:** kept on the wire (line 152). Line 158 sits in a paragraph about HEAD/204/304, so it reads as a special case rather than a general rule. This is the less surprising reading, but it is a judgment call.

### C7. Framing headers on a response to HEAD
- `spec/Full_PRD.md` line 122 (FP-02): "A response to HEAD is written with no framing headers."
- `spec/Full_PRD.md` line 159 (FP-03): "A server answering HEAD writes the same framing headers it would have used for GET: chunked when the peer is HTTP/1.1, and connection-close framing when the peer is HTTP/1.0."
- **Built:** the FP-03 rule. The headers follow the GET rules. No body bytes are written, and the end-of-message encodes nothing.

### C8. Bare LF line endings
- `spec/Interface_Contract.md` line 98 (`receive_data`): "every received line must end with a carriage return and line feed".
- `spec/Full_PRD.md` line 129 (FP-02): "Received header blocks that use a lone line feed ... are accepted."
- **Built:** the PRD. Lone LF and mixed CRLF/LF are accepted in header blocks and in status and request lines. Chunk terminators must be exactly CRLF, as FP-03 requires.

### C9. Status line without a reason phrase
- `spec/Full_PRD.md` line 129 (FP-02): "A response status line that omits the reason phrase is accepted and the reason is empty."
- `spec/Interface_Contract.md` line 100 (`next_event`): "A received status line with no reason phrase after its status code is illegal."
- **Built:** accepted, with an empty reason (the PRD's behavior statement).

### C10. Obsolete line folding
- `spec/Full_PRD.md` line 130 (FP-02): folding "is accepted when reading headers".
- `spec/Full_PRD.md` line 136 (FP-02): "A continuation line (a header line that begins with a space or tab) is refused."
- **Built:** a reconciliation. A continuation line joins the preceding field, with the leading whitespace replaced by one space. A continuation line with no preceding field in the block (the first line) is refused.

### C11. Matching `Expect: 100-continue`
- `spec/Full_PRD.md` line 249 (FP-07): the token is "matched case-insensitively".
- `spec/Interface_Contract.md` line 89: "The `Expect` value must be exactly the lowercase token `100-continue`."
- **Built:** case-insensitive (the PRD). Tokens are matched inside a comma-separated list.

### C12. `Expect: 100-continue` on HTTP/1.0 requests
- `spec/Full_PRD.md` line 249 (FP-07): "An `Expect: 100-continue` header on an HTTP/1.0 request does not set either flag."
- `spec/Interface_Contract.md` line 88: "any request with `Expect: 100-continue` sets it, whatever its HTTP version."
- **Built:** the PRD. A 1.0 request does not set the flag. Only the client-role send path can produce a 1.0 request, and that path refuses it, so this only matters for requests pulled from a peer.

### C13. Which 2xx status accepts CONNECT
- `spec/Full_PRD.md` line 252 (FP-07): "acceptance is a final response whose status is in the 2xx range".
- `spec/Full_PRD.md` line 263 (FP-07): "Only status 200 accepts a CONNECT proposal; other 2xx statuses deny it."
- **Built:** 200 only. Any other 2xx is a denial, and the connection continues as HTTP.

### C14. Which framing header wins
- `spec/Full_PRD.md` line 94 (FP-01): "When an event carries both framing headers, the `Content-Length` decides how the body is framed."
- `spec/Full_PRD.md` line 156 (FP-03): for a response built with both, "transfer-encoding wins: Content-Length is not sent".
- **Built:** both rules, in their own contexts. Receiving a message (request or response) and sending a request: Content-Length decides. Sending a response: Transfer-Encoding wins, and Content-Length is dropped.

## Part 2 — Gaps (not stated in the spec) and what was assumed

- **Reason phrases.** No validation rule is stated. Control bytes other than tab are refused. Leading and trailing spaces are kept as given.
- **Default reason on responses.** The PRD says it defaults to empty. A response sent with no reason is written as `HTTP/1.1 200 ` followed by CRLF (the trailing space follows the RFC grammar).
- **Peer HTTP version.** Only `1.0` and `1.1` are accepted from a peer. Any other version is a remote protocol error with status 400. The RFC would say 505; the spec does not state this.
- **Default suggested status.** 400 for all remote errors, except 501 (Transfer-Encoding) and 431 (size limit), as the spec states.
- **Chunk-size and trailer lines and the size limit.** The incomplete-event limit applies to a chunk-size line (overflow is a remote error with status 400) and to the trailer block (overflow is 431). The spec only mentions request/response lines and header blocks.
- **Close-delimited responses on HTTP/1.1.** The spec describes close-delimited bodies only for HTTP/1.0 peers. A response with neither framing header from an HTTP/1.1 peer is also read until close, following RFC 7230 §3.3.3. Such a connection is not kept alive.
- **Content-Length value formatting.** Whitespace around comma-separated pieces is stripped. An empty piece is refused. The stored value is the first piece as written, so `00005` stays as written.
- **Send of non-bytes payloads.** `send()` accepts only bytes-like payloads. `send_with_data_passthrough()` also accepts any object with a length, and returns that same object as a piece. Text payloads are refused in both.
- **`send()` with a non-event.** Refused with `LocalProtocolError`, and the send side enters ERROR like any other refused send.
- **Data on empty-body responses.** Data sent for a HEAD, 204, or 304 response is refused as a local protocol error. Empty data is accepted and produces no bytes.
- **Response headers for 204, 304 and HEAD.** A 204 gets no framing headers added (its headers are sent as the caller gave them). A 304 and a HEAD response follow the GET rules, since FP-03 requires that for HEAD.
- **Connection close and keep-alive.** Keep-alive is enabled only when both sides speak 1.1 and neither sent `close`. A response sent before any request was seen, or to a 1.0 peer, always gets `Connection: close`. When keep-alive is disabled, `keep-alive` tokens are removed from the response and `close` is added.
- **Proposals before the body finishes.** If the server denies a CONNECT or Upgrade before the client sends its end-of-message, the client goes to DONE at its end-of-message rather than to MIGHT_SWITCH_PROTOCOL. If the server accepts before the client finishes, both sides go to SWITCHED_PROTOCOL immediately and the client's later sends are refused.
- **Upgrade detection.** A request carries an Upgrade proposal if it has any `Upgrade` header, whatever its value.
- **Requests received while not idle.** A request pulled while the server side is not IDLE is a remote error.
- **Response received while idle.** A client that pulls bytes before it has sent a request (and the server is IDLE) gets a remote error. Nothing is expected from the server then.
- **`ReceiveClosedError`.** The error for bytes fed after the receive side closed is a `RuntimeError` subclass. The spec lets the class be the implementer's choice.
- **`their_http_version`.** This attribute persists across cycles. The per-cycle peer version is tracked separately, so that a server with no request in the current cycle is treated as "peer unknown".
- **`states`.** Returns a fresh dict keyed by `CLIENT` and `SERVER`.
- **Headers view.** `Headers` is a read-only sequence. Iterating or indexing it gives `(lowercase_name, value)` tuples. Slicing returns a tuple. `raw_items()` returns a list. Equality with a list of pairs compares the ordinary view.
- **Connection role.** An invalid role raises `ValueError`. An invalid `max_incomplete_event_size` (non-int, bool, or < 1) also raises `ValueError`.
- **Constructor arguments.** Event constructors accept positional or keyword arguments. Invalid construction always raises `LocalProtocolError`, including for wrong argument types.
- **Method and CONNECT matching.** The method `CONNECT` is matched case-sensitively, as RFC 7230 method tokens are.
- **Trailers.** Trailer fields pass through the same name, value and framing-header normalization as other headers. No further trailer checks are specified.

## Part 3 — Verification

- `python3 -m unittest tests.test_httpwire`: 56 tests, all pass. They cover event construction and header normalization, framing (Content-Length, chunked, close-delimited, HEAD), keep-alive and pipelining, Expect/100-continue, CONNECT and Upgrade (accept and deny), error kinds and states, and the incomplete-event size limit.
- A mutation fuzz run (30,000 mutated inputs, random feed splits, random sends) raised no exception other than `LocalProtocolError`, `RemoteProtocolError`, or the documented feed-after-close error. The fuzz script is not part of the repository.
- The code was run on Python 3.13 only. It uses no 3.9+ syntax or library calls (no `str.removeprefix`, no `match`, no PEP 585 generics), but it has not been run on 3.8.
