# NOTES

What was built: `httpwire`, a pure-Python, sans-IO HTTP/1.1 wire library, in
`/app/httpwire/`. Tests are in `/app/tests/test_httpwire.py` (101 tests, all
passing on Python 3.13). `SPEC_TRACE.md` maps every checklist id to code and
tests. `spec/` is unchanged.

Layout:

- `httpwire/__init__.py`: the package-root surface.
- `httpwire/_constants.py`: role and state sentinels, `NEED_DATA`, `PAUSED`, default size limit.
- `httpwire/_errors.py`: `LocalProtocolError`, `RemoteProtocolError` (siblings), `ReceiveClosedError` (runtime error for bytes after end-of-receive).
- `httpwire/_events.py`: the six event classes, the `Headers` list, construction-time checks.
- `httpwire/_wire.py`: line-level parsing of received bytes.
- `httpwire/_connection.py`: `Connection`, the state machine, framing, and encoding.
- `pyproject.toml`: setuptools metadata for a flat layout. No build step is needed to use the code from `/app`.

Verification: the test suite passes on Python 3.13. The package also parses under the Python 3.8 grammar (`ast.parse(..., feature_version=(3, 8))`). It has not been run on 3.8, PyPy, Windows, or macOS, because only Python 3.13 is installed here.

## Spec conflicts

All 19 contradictions in `spec/export.meta.json` (`unsettled_ids`) have no human verdict. The export was made with `--allow-open`, so I chose one side of each. Behaviour is governed by the PRD (`Full_PRD.md`, packs 09–20). The Interface Contract (`Interface_Contract.md`, packs 04–08) governs the shape of values and calls. Where the two disagree on behaviour, I followed the PRD.

Each entry gives the two sides, then what I built.

1. **CF-000003, requests and responses with both framing headers.** For requests, FP-01 (pack 14, N-000096): "When an event carries both framing headers, the `Content-Length` decides how the body is framed." For responses, FP-03 (pack 16, N-000207): "transfer-encoding wins: Content-Length is not sent." Built: a request framed by Content-Length, with Transfer-Encoding left off the wire. A response framed by Transfer-Encoding, with Content-Length left off the wire. Both the sending and receiving sides follow this.

2. **CF-000005, status line without a reason phrase.** FP-02 (pack 15, N-000166): "is accepted and the reason is empty." Interface (pack 08, N-000516): "is illegal." Built: accepted, with an empty reason (PRD governs behaviour).

3. **CF-000026, control bytes in header values.** FP-01 (pack 14, N-000097): "including other control bytes and non-ASCII bytes" may appear. N-000108: "Control bytes other than tab are refused in header values." Built: every control byte except tab is refused (including DEL, 0x7F). Non-ASCII bytes (0x80–0xFF) are accepted.

4. **CF-000048, default incomplete-event size limit.** PRD FP-05 (pack 18, N-000317): "at least 14 kibibytes and less than 18 kibibytes." Interface (pack 08, N-000479): "When it is omitted, the limit is 8 kibibytes." Built: 16 KiB (`DEFAULT_MAX_INCOMPLETE_EVENT_SIZE`). That value sits inside the PRD range, and the 8 KiB figure does not.

5. **CF-000050, response to HEAD.** FP-02 (pack 15, N-000137): "A response to HEAD is written with no framing headers." FP-03 (pack 16, N-000219): "writes the same framing headers it would have used for GET." Built: the FP-03 rule. Framing headers are the GET ones (chunked for an HTTP/1.1 peer, close-delimited for HTTP/1.0). The body is empty, and a data event is refused.

6. **CF-000074, lone line feed.** PRD (pack 15, N-000165): lone-LF header blocks "are accepted." Interface (pack 08, N-000510): "every received line must end with a carriage return and line feed." Built: lone LF is accepted on the request, status, header, and chunk-size lines. The CRLF after chunk data must be exactly CRLF (N-000245).

7. **CF-000075, CF-000076, CF-000100, obsolete line folding.** PRD (pack 15, N-000167 to N-000169): folding is accepted and joined. N-000176: "A continuation line … is refused." Built: folding is accepted. A continuation line is joined to the previous value with one space, and a continuation with no previous header is refused.

8. **CF-000083, Expect on HTTP/1.0.** PRD (pack 17/20, N-000357): an `Expect: 100-continue` on HTTP/1.0 "sets neither flag." Interface (pack 08, N-000491): any request with the header "sets it, whatever its HTTP version." Built: the PRD. No flag is set for HTTP/1.0.

9. **CF-000098, Content-Length digit cap.** FP-01 (pack 14, N-000116): "Every value of at most 18 digits is accepted"; the cap is an implementer choice from 18 to 32 (N-000116). Interface (pack 06, N-000462): "longer than 16 digits is refused." Built: 18 digits. Values of up to 18 digits are accepted, and longer ones are refused.

10. **CF-000099, chunk-size digit cap.** FP-03 (pack 16, N-000194): "up to 64 hexadecimal digits." N-000228: a cap "from 16 to 32 inclusive." Built: 32 digits. Longer size lines are refused.

11. **CF-000101, whitespace after the chunk size.** N-000230: a size line may be "followed by spaces or tabs, then the line ending." N-000243: "Whitespace after the chunk size is refused." Built: spaces and tabs are allowed, following the chunk-size grammar in N-000230.

12. **CF-000102, Content-Length: 0 on responses.** N-000199: the header "is kept on the wire, including when N is 0." N-000218: "A response with Content-Length: 0 is sent without that header." Built: the header is kept for ordinary responses. For 204, 304, and HEAD, framing headers are stripped or kept according to the rules for those cases. N-000218 is read as applying to the empty-body cases only.

13. **CF-000103, Connection: close token.** Terms (pack 10, N-000021): "Any Connection value that contains close turns it off." FP-04 (pack 17, N-000262): "as a whole element of the comma-separated Connection value." Built: whole-element match, case-insensitive. A value such as `closed-later` does not disable keep-alive.

14. **CF-000104, Expect token case.** N-000354 (pack 20): matched case-insensitively. N-000493 (pack 08): "must be exactly the lowercase token." Built: case-insensitive, as in N-000354.

15. **CF-000105, whether client body events end the 100-continue wait.** N-000353 (pack 20): "its own body events do not end the wait." N-000359: the flags "turn off … when the client sends any data event or its end-of-message." Built: N-000359. The client's data or end-of-message clears the flags.

16. **CF-000106, CONNECT acceptance.** N-000364 (pack 20) and N-000369–372: a 2xx final response accepts CONNECT. N-000396: "Only status 200 accepts a CONNECT proposal." Built: any 2xx accepts, matching the three statements that say so.

17. **CF-000107, repeated Transfer-Encoding.** FP-01 (pack 14, N-000093): repeated `chunked` headers "collapse to one." N-000121: a second Transfer-Encoding header "is refused with suggested status 501, even when both values are chunked." Built: refused with 501.

Disagreements I found that are not in the unsettled list:

18. **Client receiving a response with no framing headers from an HTTP/1.1 peer.** The PRD (pack 16, N-000208) covers only HTTP/1.0 peers ("A response with neither framing header from an HTTP/1.0 peer is close-delimited"). Built: close-delimited for any peer. This is the usual reading of RFC 7230 §3.3.3.

## Things the spec does not state (assumptions)

- **Chunk-size and Content-Length limits:** 32 hex digits for a chunk-size line, 18 decimal digits for Content-Length (see conflicts 9 and 10).
- **Pulled header values:** leading and trailing space or tab are stripped, as the RFC 7230 OWS grammar allows. On construction they are refused, not stripped, as FP-01 says.
- **Pulled versions and status codes:** only `HTTP/1.0` and `HTTP/1.1` are accepted. Status codes are three digits with a value of at least 100. Any other peer violation gets suggested status 400, because the spec names only three exceptions to the default 400 (501 for Transfer-Encoding, 431 for the size limit).
- **Version on construction:** `Request`, `Response`, and `InformationalResponse` accept any `N.N` version, but only `1.1` can be sent (FP-05 says so for requests, and I applied it to responses too).
- **Reason phrase:** not described by the spec for validation. I refuse control bytes other than tab (including CR and LF), to prevent line injection.
- **Empty reason on send:** the status line is written as `HTTP/1.1 200 ` with a trailing space, which is valid per RFC 7230.
- **Connection: close on responses:** added only to final responses (not to 1xx) when keep-alive is off, and it replaces any keep-alive token. The `close` token is appended last.
- **Responses with a Transfer-Encoding and no Content-Length**, to an HTTP/1.1 peer: chunked. To an HTTP/1.0 or unknown peer: close-delimited.
- **Requests with neither framing header:** the body is empty, as if Content-Length were 0. A Data event is refused, and on the receive side the request is followed directly by end-of-message.
- **send() with a non-bytes-like payload:** refused with `LocalProtocolError`. Only `send_with_data_passthrough()` accepts an object with a length, and it keeps that object by identity. A `str` payload is refused in both methods.
- **Refused sends:** any `LocalProtocolError` raised while sending (including bad body lengths, not only illegal state transitions) puts our side into ERROR, as FP-05 says for sends in general.
- **`Data.chunk_start` / `chunk_end`:** default to `False` (the Interface gives no default).
- **Event constructors:** `headers` defaults to empty. The Interface lists it as required, so this only loosens the signature.
- **`bool` status codes:** refused, since bool is a subclass of int and is not a status code.
- **Tab in header values:** allowed between other bytes, as FP-01 says. A tab at the start or end is refused.
- **Client pulling an unsolicited response:** allowed when the server is in IDLE (FP-04 allows an unsolicited final response), so the client does not reject it.
- **Accepting response** (101, or a 2xx to CONNECT): no framing headers are added and no `Connection: close` is added, even if keep-alive is off.
- **Trailers in chunked requests:** allowed, because the peer version is unknown on the sending side. Refused when the peer is known to be HTTP/1.0.
- **`Connection(role, max_incomplete_event_size)`:** a bad role or a negative or non-int limit raises `LocalProtocolError`. The spec does not give an exception type for these.
- **Start of next cycle:** clears switch proposals, the request method, and the waiting flags. `their_http_version` is kept across cycles, and it is replaced when the next request or response is pulled.

## Known limits

- No I/O, so nothing here exercises a real socket.
- Not tested on any Python other than 3.13. Only the 3.8 grammar was checked.
- The hidden acceptance tests were not read (none were looked for or fetched).
