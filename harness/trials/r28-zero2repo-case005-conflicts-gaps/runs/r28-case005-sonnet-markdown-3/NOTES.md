# NOTES

Code: `httpwire/__init__.py` (exports), `httpwire/_core.py` (everything). No build step.

## Spec disagreements and what was built
1. **Content-Length max digits**: PRD FP-01 says every value of <=18 digits is accepted (limit chosen 18..32); Interface_Contract "Events" says longer than 16 digits is refused. Built: limit 18.
2. **Default incomplete-event size**: PRD FP-05 says >=14 KiB and <18 KiB; Contract `Connection` says 8 KiB. Built: 16 KiB.
3. **Chunk-size digits**: PRD FP-03 says "up to 64 hex digits" and also "at most 16..32 digits". Built: 32 max.
4. **Chunk-size whitespace**: FP-03 rule allows spaces/tabs after size/extension; the error list says whitespace after chunk size is refused. Built: trailing spaces/tabs allowed.
5. **Control bytes in header values**: FP-01 says any byte except NUL/CR/LF/FF/VT is allowed "including other control bytes"; the error list says control bytes other than tab are refused. Built: the permissive rule.
6. **Repeated Transfer-Encoding**: FP-01 normal says repeated `chunked` collapse to one; FP-01 errors/FP-05 say a second TE header is refused with 501. Built: refused (501).
7. **Obsolete line folding**: FP-02 normal accepts it; FP-02 errors say a continuation line is refused. Built: accepted (but a continuation as the first header line is refused).
8. **Lone-LF line endings / missing reason phrase**: PRD accepts both; Contract says every line must end in CRLF and a status line without reason is illegal. Built: PRD (accepted).
9. **CONNECT acceptance**: FP-07 normal says any 2xx accepts; boundary says only 200. Built: any 2xx accepts.
10. **100-continue**: PRD requires HTTP/1.1 and case-insensitive match; Contract says any version sets `client_is_waiting...` and `they_are_waiting...` needs lowercase token. Built: HTTP/1.1 only, case-insensitive, for both.
11. **Content-Length: 0 on a response**: FP-03 says it is kept on the wire, and also that it is sent without that header. Built: kept.
12. **HEAD response framing**: FP-02 says written with no framing headers; FP-03 says same framing headers as GET. Built: as GET (chunked for 1.1 peers, none + close for 1.0/unknown).
13. **Both Content-Length and Transfer-Encoding**: FP-01 says Content-Length decides; FP-03 says transfer-encoding wins for responses. Built: Content-Length decides for requests, Transfer-Encoding wins for responses (send and receive).

## Unstated, assumed
- Invalid role passed to `Connection` raises `ValueError`; bytes after close raises `RuntimeError`.
- Empty header values are allowed. Invalid event construction argument types raise `LocalProtocolError`.
- HTTP version strings must match `[0-9].[0-9]`; Host is required for versions >= 1.1.
- Sending `ConnectionClosed` from CLOSED is allowed (needed for repeated pulled closes).
- `send()` of a no-byte event returns `None`; `states` is a dict keyed by CLIENT/SERVER.
- Response gets `Connection: close` also when the peer is in ERROR.
