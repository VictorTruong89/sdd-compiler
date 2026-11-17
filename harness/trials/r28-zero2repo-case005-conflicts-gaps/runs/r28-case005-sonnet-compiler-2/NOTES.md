# NOTES

Implementation: `httpwire/__init__.py` (public surface) and `httpwire/_core.py` (everything else).
Pure Python, no dependencies, no I/O. Every checklist id is covered by the library behaviour
described in the spec packs; ids that are pure non-goals/constraints (no CLI, no sockets, no HTTP/2,
no non-chunked transfer encodings, no keep-alive for 1.0) are satisfied by absence.
Not separately tested: platform claims (macOS/Windows/PyPy) — N-000041–N-000043.

## Spec disagreements and what I built

- CF-000003 (CL vs TE when both present): FP-01 N-000096 "Content-Length decides"; FP-03 N-000207
  "transfer-encoding wins" for a response. Built: both headers are stored; for a *response*
  chunked wins (Content-Length stripped on send); for a *request* Content-Length decides.
- CF-000005 (status line without reason): FP-02 N-000166 accepts it; Interface N-000516 says illegal.
  Built: illegal (`HTTP/1.1 200\r\n` refused; `HTTP/1.1 200 \r\n` accepted with empty reason).
- CF-000026 (control bytes in values): N-000097 allows other control bytes; N-000108 refuses control
  bytes other than tab. Built: the explicit rule — refuse only NUL CR LF FF VT and leading/trailing SP/HT.
- CF-000048 (default incomplete-event limit): N-000317 14–<18 KiB vs N-000479 8 KiB. Built: 16 KiB.
- CF-000050 (HEAD framing headers): N-000137 none vs N-000219 same as GET. Built: same as GET
  (chunked for 1.1 peer, close-delimited for 1.0 peer; explicit Content-Length kept); body is empty.
- CF-000074 (lone LF): N-000165 accepts vs N-000510 CRLF only. Built: lone LF accepted.
- CF-000075/76 (obs-fold): N-000168/169 join vs N-000176 refuse. Built: joined with a single space;
  a continuation line as the first header line is refused.
- CF-000083 (Expect on HTTP/1.0): N-000357 sets neither flag vs N-000491 sets whatever the version.
  Built: only HTTP/1.1 requests set the flag.

Unflagged disagreements:
- Content-Length max digits: Interface N-000462 "longer than 16 digits refused" vs PRD N-000118/119
  (≤18 accepted, limit 18–32). Built: limit 18 digits.
- Chunk-size digits: N-000195 "up to 64 hex digits" vs N-000228 (16–32). Built: 32.
- Repeated `Transfer-Encoding: chunked`: N-000092 collapse vs N-000121/N-000295 refuse with 501. Built: refuse.
- CONNECT acceptance: N-000364 any 2xx vs N-000397 only 200. Built: any 2xx.
- N-000218 "Content-Length: 0 response sent without that header" vs N-000199 "kept on the wire
  including 0": built keeps the header as supplied.
- Whitespace after chunk size: refused unless part of a `;ext` (extension text swallows trailing spaces).

## Unstated, assumed
- Invalid role → `ValueError`; bytes fed after close → `RuntimeError`.
- Non-int/bool status, non-ASCII str, wrong types in events → `LocalProtocolError`.
- `Content-Length` collapsed values keep the first piece's text. `states` is a dict.
- Connection after any protocol error sets keep-alive off (so responses carry `Connection: close`).
- `send` returns `None` for ConnectionClosed, otherwise bytes.
