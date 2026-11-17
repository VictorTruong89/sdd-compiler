# httpwire implementation notes

Layout: `httpwire/` is the importable package (flat layout at the repo root, `pyproject.toml` for setuptools). Zero runtime dependencies. Tests are in `tests/test_httpwire.py` (`python3 -m pytest tests/`, 53 passing at the time of writing).

Line numbers below refer to the lines of `spec/Full_PRD.md` ("PRD") and `spec/Interface_Contract.md` ("Contract") as printed by a plain read of those files.

## Conflicts between the specification files, and what was built

Where the spec disagrees with itself, the choice is the one listed under "Built". Where a choice is not obvious, the reason is given.

1. **Content-Length digit limit.**
   - PRD line 105: "Every value of at most 18 digits is accepted; the maximum digit count is ... from 18 to 32 inclusive."
   - Contract line 46: "A `Content-Length` value longer than 16 digits is refused."
   - **Built:** 16 digits (1 to 16 accepted, 17 or more refused). The Contract states a concrete value on the public surface, so it wins.

2. **Default incomplete-event size limit.**
   - PRD line 210: "The default is a fixed value ... at least 14 kibibytes and less than 18 kibibytes."
   - Contract line 76: "When it is omitted, the limit is 8 kibibytes."
   - **Built:** 8 KiB (8192 bytes) when the constructor argument is omitted. The Contract gives the exact default for the constructor. The explicit argument is honored as given.

3. **HEAD response framing headers.**
   - PRD line 122: "A response to HEAD is written with no framing headers."
   - PRD line 159: "A server answering HEAD writes the same framing headers it would have used for GET: chunked when the peer is HTTP/1.1, and connection-close framing when the peer is HTTP/1.0."
   - **Built:** line 159. HEAD gets the GET framing headers, but no body, and end-of-message encodes as empty.

4. **Repeated `Transfer-Encoding: chunked` headers.**
   - PRD line 94: "Repeated `Transfer-Encoding: chunked` headers collapse to one."
   - PRD line 106 and line 203: "A second `Transfer-Encoding` header is refused with suggested status 501, even when both values are `chunked`."
   - **Built:** refused with status 501 (lines 106 and 203 are the more specific statements, and line 203 repeats them).

5. **`Content-Length: 0` on a response.**
   - PRD line 152: "The `Content-Length` header is kept on the wire, including when N is 0."
   - PRD line 158: "A response with `Content-Length: 0` is sent without that header, since its body is empty."
   - **Built:** kept on the wire (line 152). Line 158 sits inside the 204/304/HEAD bullet, so I did not drop the header there.

6. **Client body events and the 100-continue wait.**
   - PRD line 248: "The client stays waiting for 100-continue until the server answers; its own body events do not end the wait."
   - PRD line 250: the waiting flags turn off "when the client sends any data event or its end-of-message."
   - **Built:** line 250. The client's own data or end-of-message clears the flag on both connection objects. The flag clears on any server informational or final response too. Line 248 is a narrative sentence, and line 250 is the explicit list of turn-off events.

7. **Expect: 100-continue on an HTTP/1.0 request.**
   - PRD line 249: "An `Expect: 100-continue` header on an HTTP/1.0 request does not set either flag."
   - Contract line 88: `client_is_waiting_for_100_continue` is set by "any request with `Expect: 100-continue`... whatever its HTTP version."
   - **Built:** any version sets the flag (Contract). This is a deliberate choice of the Contract over the PRD.

8. **Expect token case.**
   - PRD line 249: matched case-insensitively.
   - Contract line 89: "The `Expect` value must be exactly the lowercase token `100-continue`" (in the `they_are_waiting_for_100_continue` row).
   - **Built:** case-insensitive for both attributes, as the PRD describes the matching. This departs from the Contract's wording for `they_are_waiting_for_100_continue`.

9. **Status line with no reason phrase.**
   - PRD line 129: "A response status line that omits the reason phrase is accepted and the reason is empty."
   - Contract line 100: "A received status line with no reason phrase after its status code is illegal."
   - **Built:** a reconciliation. `HTTP/1.1 200\r\n` (no space after the code) is refused. `HTTP/1.1 200 \r\n` (a space, empty reason) is accepted, with reason `b""`. Sending an empty reason writes the trailing space, so our own round trip parses.

10. **Bare LF line endings on receive.**
    - PRD line 129: a header block using a lone LF is accepted.
    - Contract line 98: "every received line must end with a carriage return and line feed."
    - **Built:** the PRD. Lone LF is accepted for request, status, header, trailer, and chunk-size lines. Chunk data terminators must be exactly CRLF (PRD line 168).

11. **Obsolete line folding on receive.**
    - PRD line 130: continuation lines are joined to the previous value.
    - PRD line 136: "A continuation line (a header line that begins with a space or tab) is refused."
    - **Built:** folding is accepted, as line 130 describes it as a stated leniency. A continuation with no previous header is refused.

12. **Control bytes in header values.**
    - PRD line 95: values may contain "any byte other than NUL, carriage return, line feed, form feed, and vertical tab, including other control bytes."
    - PRD line 102: "Control bytes other than tab are refused in header values."
    - **Built:** refused: NUL, all C0 controls except tab (which covers CR, LF, VT, FF), and DEL (0x7F). I took line 102 as the stricter, explicit rule. Non-ASCII bytes (0x80 to 0xFF) are allowed.

13. **Chunk-size hex digits.**
    - PRD line 151: "A received size line may carry up to 64 hexadecimal digits."
    - PRD line 161: the maximum is "a fixed number ... from 16 to 32 inclusive."
    - **Built:** 64. Line 151 is the concrete receive requirement, and no width inside 16 to 32 can accept it.

14. **Whitespace after the chunk size.**
    - PRD line 161: "optionally followed by spaces or tabs, then the line ending."
    - PRD line 168: "Whitespace after the chunk size is refused."
    - **Built:** refused. Whitespace is accepted only inside a chunk extension (after `;`), which is parsed and discarded.

15. **CONNECT acceptance.**
    - PRD line 252: "acceptance is a final response whose status is in the 2xx range."
    - PRD line 263: "Only status 200 accepts a CONNECT proposal; other 2xx statuses deny it."
    - **Built:** only 200 accepts (line 263 is the more specific rule). Other 2xx statuses are denials, and the client returns to DONE.

16. **Transfer-Encoding and Content-Length both present.**
    - PRD line 94 (FP-01): "When an event carries both framing headers, the `Content-Length` decides how the body is framed."
    - PRD line 156 (FP-03): on a response constructed with both, "transfer-encoding wins: Content-Length is not sent."
    - **Built:** on send, a response with both uses chunked (or close, for a 1.0 peer) and drops Content-Length (line 156). On send, a request with both uses Content-Length and drops the Transfer-Encoding header from the wire. On receive, Content-Length decides for requests and responses, as line 94 says.

## Assumptions (things the spec does not state)

- **Close-delimited responses.** PRD line 155 and 157 tie close-delimited framing to HTTP/1.0 peers. The server, however, writes its own status line as `HTTP/1.1`. So a close-delimited response from our server has a 1.1 status line. For round trips to work, the receiver treats a response with no framing headers as close-delimited whatever its version (the RFC 7230 rule). Requests with no framing headers are an empty body, as PRD line 149 states.
- **Empty-body responses.** A 204 or 304 response gets no framing headers added; the caller's own headers are kept. A HEAD response gets GET framing headers, but no body; its end-of-message is empty.
- **Peer version unknown.** A server response sent before any request has been pulled (or after a remote error) is close-delimited and carries `Connection: close`, as PRD lines 180 and 206 imply.
- **Keep-alive.** Keep-alive is disabled when a request or response has version 1.0, when a `Connection` header contains `close` (any case, as a whole token), or when a close-delimited body is used. A side that would enter DONE with keep-alive disabled enters MUST_CLOSE. Until a disabling signal appears, a side may sit in DONE, so a client does not turn MUST_CLOSE before the response's version is known. When the server writes a response with keep-alive disabled, it adds `Connection: close` and removes any `keep-alive` token.
- **Trailers.** Trailer headers are validated as ordinary headers (name, value, and Content-Length/Transfer-Encoding normalization apply). They are only allowed with chunked framing.
- **Response 1.0 versus 1.1 on send.** Only HTTP/1.1 requests and responses can be sent; anything else is a local error (PRD line 126).
- **Received values.** Optional whitespace around a header value (after the colon, before the line end) is stripped as grammar. That is distinct from constructed values, which are refused if they begin or end with space or tab (PRD line 95, "refused, not stripped").
- **Received version.** Only `HTTP/1.0` and `HTTP/1.1` are accepted on receive; anything else is a remote error.
- **Chunk-size line length.** No separate limit beyond the buffer; the incomplete-event limit covers request/status lines and header blocks only (PRD line 210).
- **Passthrough.** `send_with_data_passthrough` keeps a non-buffer payload object by identity; `send` converts it with `bytes()`. Empty data events produce no bytes.
- **Content-Length normalization.** A collapsed or single Content-Length is stored as the canonical decimal (so `05` becomes `5`) under the name `Content-Length`. A single Transfer-Encoding keeps the caller's name spelling, with the value lowercased to `chunked`.
- **Trailing data.** `trailing_data` returns `(bytes, closed_flag)`; bytes after an accepted switch accumulate there.
- **Next cycle.** Both sides must be DONE to start the next cycle. `their_http_version` is kept across cycles until a new request or response is pulled.
- **Errors.** `Connection(role)` with a role other than CLIENT or SERVER raises `ValueError`. Feeding non-empty bytes after an empty chunk raises `httpwire._connection.ReceiveAfterCloseError`, a `RuntimeError` subclass that is not a protocol error (Contract line 64). `LocalProtocolError` and `RemoteProtocolError` are independent `Exception` subclasses.
- **Remote error state.** After a remote error the peer side is ERROR, and every further pull raises `RemoteProtocolError` with the original status hint.
- **Switch proposal.** A proposal is either a CONNECT request (method exactly `CONNECT`) or a request with an `Upgrade` header. The client enters MIGHT_SWITCH_PROTOCOL after its end-of-message if either is present. A 101 informational response accepts an Upgrade proposal; a 200 final response accepts a CONNECT proposal. Any other final response to a proposal is a denial, and the client returns to DONE.
- **Not specified, implemented as read.** `Data` construction does not validate its payload; `chunk_start` and `chunk_end` default to `False`; `EndOfMessage()` has no trailers.
