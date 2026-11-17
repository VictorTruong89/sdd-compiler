# NOTES

Package: `httpwire/` (pure Python, no build step; put `/app` on the import path). Design follows the PRD; where the spec disagrees with itself I chose as below.

## Disagreements (what each side says, what I built)

1. **Max Content-Length digits.** PRD FP-01 Boundary: at most 18 digits accepted, limit is implementer's choice 18–32. Interface_Contract "Events": "longer than 16 digits is refused". Built: limit 18 (19+ refused).
2. **Default incomplete-event limit.** PRD FP-05: ≥14 KiB and <18 KiB. Contract `Connection` signature: 8 KiB. Built: 16 KiB (16384); an explicit second argument overrides it.
3. **Chunk-size hex digits.** PRD FP-03 says "up to 64 hex digits"; the same FP says a fixed maximum of 16–32 and refuses more. Built: 32 max.
4. **Whitespace after chunk size.** PRD FP-03 allows spaces/tabs after size/extension; FP-03 Boundary says whitespace after chunk size is refused. Built: spaces/tabs accepted before the CRLF (`1a \r\n`, `1a;ext \r\n`); anything else after the digits refused.
5. **Lone LF line endings.** PRD FP-02 accepts them; Contract `receive_data` says every line must end CRLF. Built: lone LF (and mixed) accepted in header blocks. Chunk-size lines and the bytes after chunk data require CRLF.
6. **Status line without reason.** PRD accepts (reason empty); Contract `next_event` says illegal. Built: accepted, reason `b""`.
7. **Obsolete line folding.** PRD FP-02 Normal: accepted and joined with one space; FP-02 Boundary: continuation line refused. Built: folding accepted; a continuation line with no previous header (first line after the start line) is refused.
8. **Control bytes in header values.** PRD FP-01 Normal: all bytes except NUL, CR, LF, FF, VT allowed; Boundary: control bytes other than tab refused. Built: the Normal rule (only those five bytes refused, plus leading/trailing space/tab).
9. **Framing headers on HEAD response.** PRD FP-02: none written; FP-03: same as GET (chunked for 1.1 peer, close for 1.0). Built: FP-03 (the body is empty and no data may be sent).
10. **`Content-Length: 0` on a response.** FP-03 two bullets disagree (keep vs omit). Built: kept on the wire.
11. **Both framing headers.** FP-01: Content-Length decides; FP-03: Transfer-Encoding wins on responses. Built: Transfer-Encoding wins for body framing (responses lose Content-Length when sent; requests likewise frame as chunked).
12. **`100-continue` case.** PRD: case-insensitive; Contract: exactly lowercase. Built: case-insensitive.
13. **`Expect` on HTTP/1.0.** PRD: no flags set; Contract: any version sets it. Built: only HTTP/1.1 requests set the flag.
14. **Client body ends 100-continue wait?** FP-07 lines say both "body events do not end the wait" and "flags turn off when client sends data/EOM". Built: flags turn off on client data/EOM, or any server 1xx/final response.
15. **Which 2xx accepts CONNECT.** PRD: any 2xx; Boundary: only 200. Built: any 2xx accepts.
16. **Feeding after close on a switched connection.** Built: non-empty feed after an empty feed always raises `RuntimeError`.

Additional internal PRD inconsistency: FP-01 says repeated `Transfer-Encoding: chunked` collapse to one, but FP-01 Boundary / FP-05 say a second TE header is refused with 501. Built: refused (501).

## Unstated details / assumptions
- `their_http_version` is `None` until recorded; it is retained across `start_next_cycle`.
- `states` returns a dict `{CLIENT: ..., SERVER: ...}`.
- Invalid role to `Connection` raises `ValueError`. Feed-after-close raises `RuntimeError`.
- An event whose TE/CL is both absent on a received response (even HTTP/1.1) is close-delimited and disables keep-alive.
- A server response sent after a remote protocol error gets `Connection: close`.
- HTTP version must be `<digit>.<digit>`. Status line code must be 3 digits; `0xx` is a remote error.
- A server may send any final Response in IDLE; a 101 or CONNECT-accepting response without a pending proposal is a local error.
