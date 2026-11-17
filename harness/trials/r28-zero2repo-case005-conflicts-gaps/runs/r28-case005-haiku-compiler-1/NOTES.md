# httpwire — implementation notes

Built from `spec/` (compiled export; `spec/MAP.md`, `spec/CHECKLIST.md`, packs under `spec/packs/`).
`spec/` is unchanged. Code is in `httpwire/`, my own tests in `tests/`.

## Layout

| File | Contents |
|---|---|
| `httpwire/__init__.py` | Package-root surface (exact list from Interface Contract > Shape of the public surface) |
| `httpwire/_sentinels.py` | CLIENT, SERVER, NEED_DATA, PAUSED, and the nine state objects |
| `httpwire/_errors.py` | LocalProtocolError, RemoteProtocolError (`error_status_hint`), ReceiveClosedError |
| `httpwire/_headers.py` | Byte coercion, header value/name rules, Content-Length and Transfer-Encoding normalization, `Headers` |
| `httpwire/_events.py` | Request, InformationalResponse, Response, Data, EndOfMessage, ConnectionClosed |
| `httpwire/_parse.py` | Start-line and header-line parsing, incomplete-event size limit |
| `httpwire/_framing.py` | Body readers (pull) and writers (send) for Content-Length, chunked, close-delimited, and empty bodies |
| `httpwire/_connection.py` | `Connection`: send, passthrough send, feed/pull, cycles, failure marking, switch and 100-continue flags |
| `tests/test_httpwire.py`, `tests/test_no_io.py` | My tests (59 cases, all passing with `python3 -m pytest tests`) |
| `pyproject.toml` | setuptools flat layout, zero dependencies |

No build step is needed: with `/app` as the working directory `import httpwire` works.

## Conflicts between spec parts, and what was built

For each, "A" and "B" are the two statements. The compiler listed CF-000003, -005, -026, -048, -050, -074, -075, -076 and -083 as UNSETTLED; the others I found by reading the packs.

1. **Content-Length vs Transfer-Encoding when both are present** (CF-000003)
   - A: FP-01 (`spec/packs/14-…`, N-000096): "When an event carries both framing headers, the Content-Length decides how the body is framed."
   - B: FP-03 (`spec/packs/16-…`, N-000207): a response built with both "transfer-encoding wins: Content-Length is not sent".
   - Built: on receive, Content-Length decides for any event. When sending a constructed **response** with both, Transfer-Encoding wins and Content-Length is dropped (B). When sending a **request** with both, Content-Length decides and Transfer-Encoding is dropped from the wire (A).

2. **Status line without a reason phrase** (CF-000005)
   - A: FP-02 (`spec/packs/15-…`, N-000166): "is accepted and the reason is empty".
   - B: Interface Contract `next_event` (`spec/packs/08-…`, N-000516): "A received status line with no reason phrase … is illegal."
   - Built: accepted (A). The PRD states the behaviour; the interface line sits in a method description. Sent responses with an empty reason are written `HTTP/1.1 200 \r\n` (trailing space, as in h11).

3. **Control bytes in header values** (CF-000026)
   - A: FP-01 (`spec/packs/14-…`, N-000097): values may contain "other control bytes and non-ASCII bytes".
   - B: FP-01 (N-000108): "Control bytes other than tab are refused in header values."
   - Built: B. All control bytes (0x00–0x1F and 0x7F) except tab are refused; non-ASCII is allowed. A already lists NUL, CR, LF, FF and VT as refused, so B is the stricter reading.

4. **Default incomplete-event size limit** (CF-000048)
   - A: FP-05 (`spec/packs/18-…`, N-000317): default "at least 14 kibibytes and less than 18 kibibytes".
   - B: Interface Contract `Connection` (`spec/packs/08-…`, N-000479): "When it is omitted, the limit is 8 kibibytes."
   - Built: **8 KiB** (B). This is the concrete value a caller sees in the constructor, but it is outside A's range. Changing one constant (`DEFAULT_MAX_INCOMPLETE_EVENT_SIZE`) switches to any value in A's range.

5. **Framing headers on a response to HEAD** (CF-000050)
   - A: FP-02 (`spec/packs/15-…`, N-000137): "A response to HEAD is written with no framing headers."
   - B: FP-03 (`spec/packs/16-…`, N-000219): "writes the same framing headers it would have used for GET".
   - Built: B. A HEAD response gets the framing headers GET would get: Content-Length kept if non-zero, `Transfer-Encoding: chunked` for an HTTP/1.1 peer, `Connection: close` for an HTTP/1.0 or unknown peer. No body bytes are sent, and end-of-message writes nothing.

6. **Lone LF line endings** (CF-000074)
   - A: FP-02 (`spec/packs/15-…`, N-000165): lone LF or mixed line endings "are accepted".
   - B: Interface Contract `receive_data` (`spec/packs/08-…`, N-000510): "every received line must end with a carriage return and line feed."
   - Built: A for the header block and start line, which keeps the PRD's explicit leniency. Chunk data terminators must be exactly CRLF (FP-03 N-000245), a separate rule that B does not reach.

7. **Obsolete line folding** (CF-000075, CF-000076)
   - A: FP-02 (`spec/packs/15-…`, N-000168, N-000169): a continuation line is "joined to the previous header's value", with its leading run replaced by one space.
   - B: FP-02 (N-000176): "A continuation line … is refused."
   - Built: A. Folding is accepted when reading. The refusal applies only when there is no earlier header to continue.

8. **Expect: 100-continue on an HTTP/1.0 request** (CF-000083)
   - A: FP-07 (`spec/packs/20-…`, N-000357): an HTTP/1.0 request with that header "does not set either flag".
   - B: Interface Contract (`spec/packs/08-…`, N-000491): `client_is_waiting_for_100_continue` is set "whatever its HTTP version".
   - Built: A. Only HTTP/1.1 requests set the flags.

9. **Case of the `100-continue` token** (not in the compiler's list)
   - A: FP-07 (`spec/packs/20-…`, N-000354): matched case-insensitively.
   - B: Interface Contract (`spec/packs/08-…`, N-000492, N-000493): "The Expect value must be exactly the lowercase token `100-continue`."
   - Built: A, case-insensitive.

10. **Content-Length digit limit**
    - A: Interface Contract (`spec/packs/06-…`, N-000462): a value "longer than 16 digits is refused".
    - B: FP-01 (`spec/packs/14-…`, N-000114..N-000119): every value of at most 18 digits is accepted; the limit is a fixed choice from 18 to 32.
    - Built: **18 digits**. This is the only value that keeps B's MUST (accept up to 18 digits) and stays inside B's choice range. It breaks A's refusal of 17- and 18-digit values.

11. **Chunk-size digit count and the 64-digit statement**
    - A: FP-03 (`spec/packs/16-…`, N-000192, a MAY): "A received size line may carry up to 64 hexadecimal digits."
    - B: FP-03 (N-000228, N-000242): at most a fixed number of digits, from 16 to 32, implementer's choice; more is refused.
    - Built: **32 digits**. B's range is the one that binds; A is a permission to the peer, and 64 is outside B's range.

12. **Which 2xx accepts CONNECT**
    - A: FP-07 (`spec/packs/20-…`, N-000364, N-000371, N-000395): "a 2xx response accepts CONNECT".
    - B: FP-07 boundary (N-000394 to N-000398): "Only status 200 accepts a CONNECT proposal; other 2xx statuses deny it."
    - Built: **B, only 200 accepts**. B is the more specific sentence. Other 2xx responses to CONNECT are denials and HTTP continues.

13. **Content-Length: 0 on responses**
    - A: FP-03 (`spec/packs/16-…`, N-000198, N-000199): on a response, "The Content-Length header is kept on the wire, including when N is 0."
    - B: FP-03 (N-000215..N-000218): "A response with Content-Length: 0 is sent without that header, since its body is empty."
    - Built: both, scoped. Content-Length: 0 is kept on ordinary responses. It is dropped for HEAD responses, which have an empty body (B). For 204 and 304, Content-Length and Transfer-Encoding are dropped entirely, since those responses have no body.

14. **Whitespace after a chunk size**
    - A: FP-03 (`spec/packs/16-…`, N-000228..N-000232): size "optionally followed by spaces or tabs, then the line ending".
    - B: FP-03 (N-000244): "Whitespace after the chunk size is refused."
    - Built: B for whitespace directly after the hex digits. Spaces and tabs inside a chunk extension (after `;`) are allowed, since extensions are discarded.

15. **Response with neither framing header from an HTTP/1.1 peer**
    - The PRD (FP-03 N-000208..N-000214) describes close-delimited bodies only for HTTP/1.0 peers.
    - Built: on receive, close-delimited for any version (as RFC 7230 §3.3.3 does). On send to an HTTP/1.1 peer, chunked is used, so the product never sends this form to an HTTP/1.1 peer.

## Gaps (not stated in the spec) and what I assumed

- **Incomplete-event limit scope.** The PRD names request/status lines and header blocks. I also apply it to trailer blocks (431). A chunk-size line that grows past the limit without a line ending is refused as 400.
- **Pulls while the peer is in MUST_CLOSE.** The spec does not say what a pull does when the peer sent bytes after it must close. I raise RemoteProtocolError.
- **Unsolicited responses.** A server in IDLE may send a final response (FP-04). I allow a client to pull one.
- **Data events on bodies that cannot have one** (HEAD, 204, 304, and requests with no framing). Zero-length data is a no-op. Non-empty data is a LocalProtocolError, which also puts the sender in ERROR as for any refused send.
- **Non-bytes payloads.** `send()` accepts payloads that support the buffer protocol. Other objects with a length are refused by `send()` and accepted by `send_with_data_passthrough()`, which keeps them by identity.
- **`str` payloads** in `Data` are ASCII-encoded. Non-ASCII text is refused.
- **Role errors.** `Connection("client")` raises `_InvalidRoleError`, a subclass of both LocalProtocolError and ValueError.
- **`ReceiveClosedError`** is a RuntimeError subclass. The spec leaves its class to the implementer. It is importable from `httpwire._errors` but is not in the package-root list.
- **Keep-alive and cycles.** Any side that is DONE when keep-alive turns off becomes MUST_CLOSE. `start_next_cycle` resets keep-alive and the per-message state, but keeps the recorded peer HTTP version.
- **Send refusal sets ERROR.** Every LocalProtocolError raised by `send()` (including data exceeding Content-Length) moves our state to ERROR, as FP-05 requires for every refused send. A refused `start_next_cycle` changes nothing.
- **Interface states mapping.** `states` is a mapping keyed by CLIENT and SERVER, and also accepts 0 and 1 as indexes.
- **Reason phrase on send.** Written as `HTTP/1.1 <3-digit code> <reason>\r\n`, with the trailing space when the reason is empty.
- **Trailers** are normalized like headers when pulled, and written raw when sent.

## Checklist coverage

Every id in `spec/CHECKLIST.md` maps to code in the module listed. Tests in `tests/` cover the behaviour by area; a given id may not have its own dedicated test. The table below is by pack.

| Pack | Ids | Status | Where |
|---|---|---|---|
| 01 | (none) | n/a | — |
| 02 | N-000413..417 | Implemented; no-I/O and zero-dependency checks in `tests/test_no_io.py` | pure Python; `pyproject.toml` has no dependencies |
| 03 | N-000418..428 | Implemented (CPU-only, flat layout, no native code) | `pyproject.toml` (`packages = ["httpwire"]`) |
| 04 | N-000429..432 | Implemented (importable library; no CLI, no config file, no exit codes) | `httpwire/__init__.py` |
| 05 | N-000433..449 | Implemented; tested (`test_package_root_names_present`, state and error-class tests) | `httpwire/__init__.py`, `_sentinels.py`, `_errors.py` |
| 06 | N-000450..471 | Implemented; tested (events, header list, raw items, Content-Length and TE tests) | `_events.py`, `_headers.py` |
| 07 | N-000472..475 | Implemented; tested (error hints; receive-closed error) | `_errors.py` |
| 08 | N-000476..522 | Implemented; tested (roles, attributes, send, next_event, start_next_cycle, send_failed, trailing data) | `_connection.py` |
| 09 | N-000001..009 | Implemented (sans-I/O design; protocol errors carry hints) | whole package |
| 10 | N-000010..021 | Implemented (terms: connection, events, need-data, paused, cycles, send failure, trailing data) | `_connection.py`, `_events.py` |
| 11 | N-000022..036 | Implemented (inventory of the surfaces above) | whole package |
| 12 | N-000037..058 | Implemented; error text is free (N-000058, no requirement). Platform support (N-000042) is by construction (pure Python). | whole package |
| 13 | N-000059..069 | Non-goals. Implemented as refusals: gzip/deflate transfer encodings (N-000064, N-000065), chunk extensions discarded (N-000066, N-000067), HTTP/1.0 keep-alive off (N-000062, N-000063). Absent by design: network I/O, TLS, DNS, HTTP/2 or HTTP/3, URL routing, CLI, server, benchmark (N-000059, N-000060, N-000061, N-000068, N-000069). | `_framing.py`, `_connection.py`, `_headers.py` |
| 14 | N-000070..121 | Implemented; tested (FP-01 construction and header rules) | `_events.py`, `_headers.py`, `_connection.py` |
| 15 | N-000122..182 | Implemented; tested (FP-02 states, send, feed and pull, lone LF, folding, refusals) | `_connection.py`, `_parse.py` |
| 16 | N-000183..246 | Implemented; tested (FP-03 framings, chunk marks, passthrough, refusals) | `_framing.py`, `_connection.py` |
| 17 | N-000247..289 | Implemented; tested (FP-04 keep-alive, cycles, pipelining, paused) | `_connection.py` |
| 18 | N-000290..331 | Implemented; tested (FP-05 errors, ERROR states, send_failed, size limit) | `_connection.py`, `_parse.py`, `_errors.py` |
| 19 | N-000332..348 | Implemented; tested (FP-06 close, MUST_CLOSE, receive-close handling) | `_connection.py` |
| 20 | N-000349..412 | Implemented; tested (FP-07 100-continue flags, CONNECT and Upgrade accept and deny, trailing data) | `_connection.py` |

Known gaps against the checklist: none that I am aware of. The judgement calls are in the conflicts list above (items 4, 10, 11, and 12 are the ones with a concrete value a test could check).

## Not verified

- The hidden acceptance tests were not seen, as the task requires. My tests are my own reading of the spec.
- Interoperability with real HTTP peers was not tested.
- Tested locally on Python 3.13 with pytest 8.4. The code avoids features newer than 3.8 (no f-strings, no `match`, no `removeprefix`), but I have not run it on 3.8 or PyPy.
