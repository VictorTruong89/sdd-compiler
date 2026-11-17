# NOTES

Package: `httpwire/` (`_common.py`, `_events.py`, `_connection.py`). No build step.

## Spec disagreements and what I built

1. **Content-Length max digits.** PRD FP-01: values up to 18 digits accepted, limit chosen 18–32. Interface Contract (Events): "longer than 16 digits is refused". Built: PRD, limit 18 (19+ refused).
2. **Default incomplete-event limit.** PRD FP-05: default at least 14 KiB and under 18 KiB. Contract (`Connection` signature): default 8 KiB. Built: 16 KiB (PRD).
3. **Chunk-size digits.** PRD FP-03 says "up to 64 hex digits", and elsewhere "at most 16–32 digits, more refused". Built: 32 max.
4. **Chunk-size line whitespace.** PRD allows "spaces or tabs" after an extension and refuses "whitespace after the chunk size". Built: an optional `;ext` (which swallows the rest of the line), then CRLF; whitespace directly after the size is refused.
5. **`client_is_waiting_for_100_continue` and HTTP version.** PRD FP-07: only HTTP/1.1 requests set it, HTTP/1.0 does not. Contract: "whatever its HTTP version". Built: PRD (version >= 1.1).
6. **`they_are_waiting...` Expect matching.** PRD: case-insensitive token. Contract: exactly lowercase token. Built: case-insensitive.
7. **Lone LF and missing reason phrase.** Contract: "every received line must end with CRLF" and a status line without a reason is illegal. PRD FP-02: lone LF accepted, missing reason accepted (reason empty). Built: PRD. Chunk-size lines and chunk terminators still require CRLF.
8. **Obsolete line folding.** PRD FP-02 accepts it when reading, but the same section's error list says a continuation line is refused. Built: accepted and unfolded; a continuation line with no preceding header is refused.
9. **CONNECT acceptance status.** PRD FP-07 says any 2xx accepts; its boundary section says only 200 accepts. Built: any 2xx accepts.
10. **Response to HEAD framing headers.** PRD FP-02: "written with no framing headers". PRD FP-03: same framing headers as GET (chunked for 1.1 peer). Built: FP-03.
11. **Content-Length: 0 on responses.** FP-03 says the header is kept on the wire including N=0, and also says it is sent without that header. Built: header kept.
12. **Both framing headers.** PRD FP-01: Content-Length decides. FP-03 (responses): Transfer-Encoding wins. Built: Request -> Content-Length decides; Response -> Transfer-Encoding wins (CL removed when sending).

## Unstated details (assumptions)

- A reason phrase is written as `HTTP/1.1 200 \r\n` when empty (trailing space).
- Header value normalization of Content-Length keeps the first piece's original digits.
- Received version strings accept any `[0-9].[0-9]`; sending requires exactly `1.1`.
- Non-ASCII `str` or non-bytes-like argument types raise `LocalProtocolError`.
- Invalid `Connection` role raises `ValueError`; feeding after close raises `RuntimeError`.
- Size limit also applies to unfinished chunk-size lines and trailers.
- `send` of `ConnectionClosed` returns `b""`; passthrough returns `[]`.
- `their_http_version` and 100-continue flags reset on `start_next_cycle`.
