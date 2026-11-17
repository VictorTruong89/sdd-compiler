# NOTES

Package: `httpwire/` (pure Python, flat layout; put `/app` on the import path). Code is in `httpwire/_core.py`.

## Spec disagreements and what was built

1. **Default incomplete-event limit.** PRD FP-05: "at least 14 KiB and less than 18 KiB". Interface_Contract `Connection`: "the limit is 8 kibibytes". Built: 16 KiB (PRD).
2. **Content-Length max digits.** PRD FP-01: values of at most 18 digits accepted, limit chosen from 18 to 32. Contract (headers): "longer than 16 digits is refused". Built: 18 (PRD).
3. **Chunk-size digits.** PRD FP-03 says "up to 64 hexadecimal digits" in one bullet and "from 16 to 32" in another. Built: 32.
4. **Line endings.** PRD FP-02: lone LF / mixed endings accepted. Contract `receive_data`: "every received line must end with CRLF". Built: lone LF accepted (PRD).
5. **Status line without reason.** PRD FP-02: accepted, reason empty. Contract `next_event`: illegal. Built: accepted (PRD).
6. **Obsolete line folding.** PRD FP-02 says continuation lines are accepted and joined; the same section (boundary) says a continuation line is refused. Built: refused (remote protocol error).
7. **Header value control bytes.** PRD FP-01: any byte except NUL CR LF FF VT allowed "including other control bytes"; also "Control bytes other than tab are refused". Built: only NUL/CR/LF/FF/VT refused (others allowed), leading/trailing space/tab refused.
8. **Repeated Transfer-Encoding.** FP-01 says repeated `chunked` collapse to one; FP-01 boundary and FP-05 say a second TE header is refused with 501. Built: refused with 501.
9. **Both framing headers.** FP-01: Content-Length decides. FP-03 (response): Transfer-Encoding wins. Built: on requests Content-Length wins; on responses Transfer-Encoding wins.
10. **HEAD response framing.** FP-02: "written with no framing headers"; FP-03: same framing headers as GET. Built: FP-03 (chunked for 1.1 peer, close framing for 1.0).
11. **Content-Length: 0 on a response.** FP-03 says kept on wire; also says sent without that header. Built: kept.
12. **CONNECT acceptance.** FP-07 says any 2xx accepts; the FP-07 boundary says only 200 accepts. Built: any 2xx accepts.
13. **100-continue flags.** Contract: any request with `Expect: 100-continue` sets the flag whatever its version, and `they_are_waiting` needs the exact lowercase token. PRD FP-07: HTTP/1.1 only, case-insensitive. Built: PRD.

## Unstated choices
- `Connection(role)` with an invalid role raises `ValueError`; feeding after close raises `RuntimeError`.
- Header names added by httpwire (`connection`, `transfer-encoding`) are written lowercase.
- Sending `ConnectionClosed` in CLOSED is allowed (idempotent). A response with empty reason is written as `HTTP/1.1 200 \r\n`.
- Received HTTP versions of the form `d.d` are accepted; status codes 100–999.
- An error in either direction disables keep-alive, so later responses carry `Connection: close`.
