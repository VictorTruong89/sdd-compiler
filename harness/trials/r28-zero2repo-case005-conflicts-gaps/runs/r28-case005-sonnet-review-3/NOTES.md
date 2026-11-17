# NOTES

Package: `/app/httpwire` (`__init__.py` re-exports; implementation in `_impl.py`). No build step; put `/app` on the import path.

## Spec conflicts and what I built
1. **Content-Length max digits.** PRD FP-01: values of at most 18 digits accepted (limit chosen from 18..32). Contract "Events": longer than 16 digits refused. Built: PRD. Max 18 digits; 19+ refused.
2. **Default incomplete-event limit.** PRD FP-05: at least 14 KiB and under 18 KiB. Contract `Connection` signature: 8 KiB. Built: 16 KiB (PRD). An explicit second argument is used as given.
3. **Chunk-size hex digits.** PRD FP-03 says "up to 64 digits" in one place, and 16..32 as the implementer's choice in another. Built: max 32 digits, more is refused.
4. **Whitespace after chunk size.** PRD FP-03 normal behavior allows spaces/tabs before the line ending; the Boundary list says whitespace after the size is refused. Built: spaces/tabs accepted (before `;ext` or the CRLF).
5. **Lone LF.** PRD FP-02 accepts lone LF (or mixed) line endings in header blocks; the Contract `receive_data` says every line must end CRLF. Built: PRD, so LF and CRLF are both accepted in header blocks. Chunk-size lines and chunk terminators still require CRLF.
6. **Status line without reason.** PRD accepts it (reason empty); Contract says it is illegal. Built: accepted.
7. **Obsolete line folding.** PRD FP-02 normal: accepted and joined with a single space. PRD FP-02 boundary: continuation line refused. Built: accepted. A continuation line before any header is refused.
8. **Control bytes in header values.** PRD FP-01 normal: anything except NUL, CR, LF, FF, VT is allowed. Boundary: control bytes other than tab refused. Built: the normal rule. Only NUL/CR/LF/FF/VT are refused, plus leading or trailing space/tab.
9. **Response to HEAD.** PRD FP-02: no framing headers. PRD FP-03: same framing headers as GET. Built: FP-03. Chunked for an HTTP/1.1 peer, `Connection: close` for 1.0 or an unknown peer. The body is empty.
10. **`Content-Length: 0` on a response.** PRD FP-03 has one bullet saying the header is kept, and another saying it is dropped. Built: kept.
11. **Both framing headers.** PRD FP-01: Content-Length decides. PRD FP-03: for a response, Transfer-Encoding wins and Content-Length is not sent. Built: responses (sent or received) use Transfer-Encoding first. Requests use Content-Length first. Event header lists keep both headers.
12. **`100-continue` case.** PRD says case-insensitive; Contract says exact lowercase. Built: case-insensitive.
13. **`Expect` on HTTP/1.0.** PRD says no flag; Contract says any version sets it. Built: no flag for 1.0.
14. **Body ends the wait?** PRD FP-07 has one bullet saying body events do not end the wait, and another saying a client data event or end-of-message turns the flags off. Built: they turn off, so any data event, end-of-message or server response clears them. This means a bodiless `Expect` request followed at once by end-of-message clears the flag.
15. **Which 2xx accepts CONNECT.** PRD says any 2xx accepts; the boundary says only 200. Built: any 2xx accepts.
16. **Feeding after close following a switch.** Built: a non-empty feed after an empty feed always raises `RuntimeError`.
17. **Repeated `Transfer-Encoding`.** PRD FP-01 says repeated `chunked` headers collapse to one. A later bullet refuses a second TE header with 501 even when both are `chunked`. Built: refused with 501. This applies to received headers too.

## Unstated items and my assumptions
- The HTTP version is not validated at `Request`/`Response` construction. It is only refused at send time if it is not `1.1`. Sending such an event puts our state in ERROR. The peer's state has already been advanced, as in h11.
- A server-IDLE connection that is sent `InformationalResponse` is refused. It must be in SEND_RESPONSE.
- `send()` returns `None` for a connection-closed event; `send_with_data_passthrough()` returns `[]`.
- A response with an empty reason is written as `HTTP/1.1 200 \r\n`.
- A rewritten `Connection` header on responses is emitted as separate lowercase `connection` headers, one per token, sorted.
- A `ConnectionClosed` event can also be sent or pulled from CLOSED (it stays CLOSED).
- After any protocol error, `Connection: close` is added to later responses (keep-alive is disabled).
- If the server accepts a switch while the client is still in SEND_BODY, the client moves to SWITCHED_PROTOCOL once it reaches DONE.
- `their_http_version` is `None` until a peer request or response is seen, and is kept across cycles.
- `Request.http_version` is not checked for format when constructed locally.
- `Data.data` is stored unchanged. `chunk_start` and `chunk_end` are coerced to `bool`.
