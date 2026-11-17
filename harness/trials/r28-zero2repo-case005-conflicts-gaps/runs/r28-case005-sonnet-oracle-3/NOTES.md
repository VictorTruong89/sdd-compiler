# NOTES

Implementation: `httpwire/__init__.py` (public surface) and `httpwire/_impl.py` (everything else).
Pure Python, no I/O, no dependencies; `pyproject.toml` is a flat setuptools layout (no build step needed;
put `/app` on the import path). Every checklist id is covered by the behavior described in the spec packs;
nothing is knowingly left unimplemented. No separate test suite was written (only ad-hoc smoke checks).

## Disagreements in the spec, and what I built
(All 19 were marked UNSETTLED. Where one side is a PRD feature-point bullet and the other a contract line, I picked the one below.)

- CF-000003 Content-Length vs Transfer-Encoding when both present. FP-01 (pack 14) says "the Content-Length decides"; FP-03 (pack 16) says "transfer-encoding wins". Built: Transfer-Encoding wins; a sent response with both drops Content-Length and is chunked (or close-delimited for HTTP/1.0 peers).
- CF-000026 FP-01 "any byte other than NUL, CR, LF, FF, VT ... including other control bytes" vs "Control bytes other than tab are refused". Built: only NUL/CR/LF/FF/VT are refused; other control bytes allowed.
- CF-000098 Content-Length digits: FP-01 "at most 18 digits accepted" vs Interface "longer than 16 digits is refused". Built: max 18 digits (19+ refused).
- CF-000107 Repeated Transfer-Encoding: FP-01 "collapse to one" vs "second TE header refused, 501 even when both chunked". Built: refused, status hint 501.
- CF-000005 Status line without reason: FP-02 "accepted, reason empty" vs Interface "is illegal". Built: accepted, reason `b""`.
- CF-000048 Default incomplete-event limit: FP-05 "14 KiB to <18 KiB" vs Interface "8 KiB". Built: 16 KiB (16384).
- CF-000074 Lone LF line endings: FP-02 accepts; Interface says every line must end CRLF. Built: lone LF accepted when reading headers (chunk-size lines still need CRLF).
- CF-000075/76/100 Obsolete line folding: FP-02 normal behavior joins continuation lines (leading whitespace -> one space); FP-02 boundary says continuation line is refused. Built: accepted and joined. (A continuation as the very first header line is refused.)
- CF-000083 Expect on HTTP/1.0: FP-07 "does not set either flag" vs Interface "whatever its HTTP version". Built: only HTTP/1.1 requests set the flag.
- CF-000104 Expect token case: FP-07 case-insensitive vs Interface exactly lowercase. Built: case-insensitive, whole comma element.
- CF-000105 Waiting-for-100-continue cleared by client body events: FP-07 first bullet says body events don't end the wait; later bullet says data/EOM turn it off. Built: cleared on client Data/EndOfMessage, and on any server 1xx/final response.
- CF-000106 CONNECT acceptance: any 2xx vs only 200. Built: any 2xx accepts.
- CF-000103 Keep-alive `close`: "contains close" vs "whole element of comma-separated value". Built: whole element, case-insensitive.
- CF-000050 Response to HEAD framing headers: "no framing headers" vs "same framing headers as GET". Built: same as GET (chunked / close), body empty.
- CF-000099 Chunk-size digits: "up to 64" vs "16 to 32 implementer's choice". Built: 32.
- CF-000101 Whitespace after chunk size: accepted (optional spaces/tabs) vs refused. Built: accepted.
- CF-000102 Response `Content-Length: 0`: kept on wire vs sent without. Built: kept.

## Not stated / assumed
- Chunk-extension grammar: `;` followed by anything up to CRLF, discarded.
- `send()` on ConnectionClosed returns `b""`; passthrough returns `[]`.
- Bytes-like `Data.data` is passed through as the given object in passthrough pieces; `send` joins via `bytes()`.
- `http_version` must match `[0-9].[0-9]` at construction, else LocalProtocolError. Non-ASCII str/ wrong types in constructors -> LocalProtocolError. bool is not accepted as a status code.
- `states` is a dict keyed by CLIENT/SERVER (a copy). `their_http_version` is `None` until recorded, reset by `start_next_cycle`.
- Invalid `role` raises `ValueError`. Feeding data after an empty feed raises `RuntimeError`.
- Any error (local send failure, remote parse failure, send_failed) also disables keep-alive so later responses carry `Connection: close`.
- Switch acceptance sets both sides to SWITCHED_PROTOCOL immediately, even if the client had not yet finished its request.
- Content-Length values are normalized to canonical decimal (leading zeros dropped).
