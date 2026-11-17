# httpwire — implementation notes

This file records where the specification disagrees with itself, and what was
not stated and had to be assumed. Section references are to the files in
`spec/`.

Layout: `httpwire/` (package), `pyproject.toml` (setuptools, flat layout),
`tests/test_httpwire.py` (unittest; run `python3 -m unittest tests.test_httpwire`
from `/app`). Python 3.8+ syntax only; verified here on Python 3.13.

## Conflicts between spec documents

For each one: what each side says, where it is, and what was built.

**C1. Content-Length digit limit.**
- `Interface_Contract.md`, Events section: "A `Content-Length` value longer than 16 digits is refused."
- `Full_PRD.md`, FP-01 Normal/Boundary: "Every value of at most 18 digits is accepted; the maximum digit count is … from 18 to 32 inclusive."
- **Built:** 18 digits. This is the only value that satisfies the PRD's stated range. `MAX_CONTENT_LENGTH_DIGITS` in `httpwire/_headers.py`.

**C2. Default incomplete-event size limit.**
- `Interface_Contract.md`, `Connection` signature: "When it is omitted, the limit is 8 kibibytes."
- `Full_PRD.md`, FP-05: "The default is a fixed value … at least 14 kibibytes and less than 18 kibibytes."
- **Built:** default 16 KiB. An explicit second argument is used as given. `httpwire/_connection.py`.

**C3. Chunk-size digit limit.**
- `Full_PRD.md`, FP-03 Normal: "A received size line may carry up to 64 hexadecimal digits."
- `Full_PRD.md`, FP-03 Normal (chunk-size bullet): "a hexadecimal number of at most a fixed number of digits … from 16 to 32 inclusive."
- **Built:** 32 digits (inside the stated implementer's-choice range). `MAX_CHUNK_SIZE_DIGITS` in `httpwire/_wire.py`.

**C4. Line endings.**
- `Interface_Contract.md`, `receive_data` / `next_event`: "every received line must end with a carriage return and line feed."
- `Full_PRD.md`, FP-02 Normal: "Received header blocks that use a lone line feed … are accepted."
- **Built:** request, status, header, and trailer blocks accept LF or CRLF. Chunk-size lines and the CRLF after chunk data require CRLF exactly, because FP-03 says "exactly CRLF".

**C5. Obsolete line folding.**
- `Full_PRD.md`, FP-02 Normal: "Obsolete line folding (RFC 7230 §3.2.4) is accepted when reading headers."
- `Full_PRD.md`, FP-02 Boundary: "A continuation line … is refused."
- **Built:** accepted and joined, following the explicit Normal-section rule. A continuation with no preceding header is refused.

**C6. Status line with no reason phrase.**
- `Full_PRD.md`, FP-02 Normal: "A response status line that omits the reason phrase is accepted and the reason is empty."
- `Interface_Contract.md`, `next_event`: "A received status line with no reason phrase after its status code is illegal."
- **Built:** accepted, reason empty (PRD).

**C7. Expect token matching.**
- `Full_PRD.md`, FP-07: the token `100-continue` "(matched case-insensitively)".
- `Interface_Contract.md`, `they_are_waiting_for_100_continue`: "The `Expect` value must be exactly the lowercase token `100-continue`."
- **Built:** case-insensitive, whole-token match as the PRD says.

**C8. Expect on HTTP/1.0 requests.**
- `Full_PRD.md`, FP-07: "An `Expect: 100-continue` header on an HTTP/1.0 request does not set either flag."
- `Interface_Contract.md`, `client_is_waiting_for_100_continue`: "any request with `Expect: 100-continue` sets it, whatever its HTTP version."
- **Built:** PRD rule (HTTP/1.1 only).

**C9. Control bytes in header values.**
- `Full_PRD.md`, FP-01 Normal: a value "may contain any byte other than NUL, carriage return, line feed, form feed, and vertical tab, including other control bytes."
- `Full_PRD.md`, FP-01 Boundary: "Control bytes other than tab are refused in header values."
- **Built:** refused: 0x00–0x08, 0x0A–0x1F, 0x7F. HTAB allowed. Also applied to reason phrases.

**C10. Repeated `Transfer-Encoding: chunked`.**
- `Full_PRD.md`, FP-01 Normal: repeated `Transfer-Encoding: chunked` headers "collapse to one".
- `Full_PRD.md`, FP-01 Boundary: "A second `Transfer-Encoding` header is refused with suggested status 501, even when both values are `chunked`."
- **Built:** refused (501). The Boundary rule is the more specific statement.

**C11. Both `Content-Length` and `Transfer-Encoding` present.**
- `Full_PRD.md`, FP-01 Normal: "When an event carries both framing headers, the `Content-Length` decides how the body is framed."
- `Full_PRD.md`, FP-03 (responses): "If a response is constructed with both … transfer-encoding wins."
- **Built:** requests: Content-Length decides the framing, and both headers are still emitted as given. Responses: Transfer-Encoding wins and Content-Length is dropped. Received responses use the same rule.

**C12. Which 2xx accepts CONNECT.**
- `Full_PRD.md`, FP-07 Normal: acceptance is "a final response whose status is in the 2xx range."
- `Full_PRD.md`, FP-07 Boundary: "Only status 200 accepts a CONNECT proposal; other 2xx statuses deny it."
- **Built:** only 200 accepts. Other statuses, 2xx included, are denials.

**C13. Framing headers on HEAD responses.**
- `Full_PRD.md`, FP-02 Normal: "A response to HEAD is written with no framing headers."
- `Full_PRD.md`, FP-03 Normal: "A server answering HEAD writes the same framing headers it would have used for GET."
- **Built:** FP-03. HEAD responses carry the GET-style framing header, the body is always empty, and the end-of-message writes nothing.

**C14. Content-Length: 0 on responses.**
- `Full_PRD.md`, FP-03 Normal: "The `Content-Length` header is kept on the wire, including when N is 0."
- `Full_PRD.md`, FP-03 Normal (empty-body bullet): "A response with `Content-Length: 0` is sent without that header."
- **Built:** kept for ordinary bodies. Dropped for HEAD responses and 204/304 responses. For 204 and 304, both framing headers are dropped.

## Things the spec does not state (assumptions)

- **G1. Receive HTTP versions.** Only `HTTP/1.0` and `HTTP/1.1` are accepted on receive. Anything else is a remote error with status 400. Versions are validated as one digit, dot, one digit on construction.
- **G2. Empty reason phrase on send.** The status line is written as `HTTP/1.1 200 \r\n` (the space is kept). FP-02 says "followed by the reason the caller supplied", so the space is kept.
- **G3. Trailers and the size limit.** Trailers after a chunked body count against the incomplete-event size limit, because they are a header block. The PRD only names request/response lines and header blocks.
- **G4. 101 without an Upgrade proposal.** Refused: a local error on send and a remote error on receive. The spec does not say.
- **G5. Accepted switch.** The accepting response carries no framing headers. Its end-of-message is never sent, because the connection is SWITCHED.
- **G6. Refused sends.** Every refused send sets our side to ERROR, including `ConnectionClosed` in a bad state, as FP-05 requires for sends.
- **G7. Data on empty-body responses.** A non-empty `Data` on a HEAD, 204, or 304 response is refused as a local error.
- **G8. Passthrough vs send.** `send()` accepts only buffer-protocol payloads and refuses others as local errors. Only `send_with_data_passthrough()` accepts any object with a length.
- **G9. Close-delimited responses.** A response with neither framing header is close-delimited, including from an HTTP/1.1 peer. Such a response also disables keep-alive.
- **G10. Unsolicited responses.** A server may send a final response while IDLE only when the client is IDLE or in ERROR (FP-04 says "without any request having arrived"). A response whose peer version is unknown is close-delimited.
- **G11. Repeated `Content-Length`.** Equal repeats collapse into the first header, with the first spelling and first value.
- **G12. Keep-alive rewrite.** When keep-alive is off, every `keep-alive` token is removed from the Connection header(s), and `close` is added to a single Connection header. If there is none, one is appended.
- **G13. Argument types.** Wrong argument types on event construction (for example a non-integer status) raise `LocalProtocolError`, since FP-01 says such constructions are refused. Connection with a bad role raises `ValueError`.
- **G14. Feeding after close.** A second empty chunk is a no-op. Feeding non-empty bytes after an empty chunk raises `httpwire._errors.ReceiveAfterCloseError`, a `RuntimeError` subclass, which is neither protocol-error class.
- **G15. Leading CRLF.** A leading CRLF before a request line is refused at once (the first byte is a control byte, FP-02).
- **G16. Chunk extensions.** Any bytes after `;` up to CRLF are accepted and discarded, but whitespace may not appear between the size digits and the `;` or CRLF.
- **G17. Name and value types.** Header names must be RFC 7230 tokens. Non-ASCII `str` input is refused at construction, while non-ASCII bytes in values are accepted.

## Verification status

- 34 unit tests in `tests/test_httpwire.py` pass on Python 3.13. Only this interpreter was available. The code uses no 3.9+ syntax, but 3.8 was not run.
- The hidden acceptance tests were not seen and were not consulted. Behaviour was derived from the three spec documents only.
