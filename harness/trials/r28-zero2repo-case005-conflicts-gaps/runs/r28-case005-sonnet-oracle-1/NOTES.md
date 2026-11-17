# NOTES

Layout: `httpwire/` (flat package at repo root, `pyproject.toml` for setuptools; no build step needed, put `/app` on the import path).
`_util.py` errors/sentinels, `_events.py` events + header normalization, `_connection.py` state machine, framing, parser, serializer.
Design follows the spec's sans-I/O model. Every checklist id (N-000413..N-000522 and the PRD ids N-000001..N-000412) is addressed by the implementation
or is a pure constraint (no I/O, no dependencies, Python 3.8+, flat layout, no CLI) which holds by construction. Nothing is knowingly left undone.
The "may" items (N-000417, 000449, 000475, ...) are implementer choices.

## Contradictions in the spec and what I built (all 19 are UNSETTLED in MAP.md)

- CF-000003 (N-000096 "Content-Length decides framing" vs N-000207 "transfer-encoding wins"): built TE wins. Event headers keep both; framing (`_body_framing`) checks TE first; a response sent with chunked TE drops Content-Length.
- CF-000005 (N-000166 status line without reason accepted vs N-000516 illegal): built a compromise: `HTTP/1.1 200 ` (space, empty reason) is accepted with reason `b""`; `HTTP/1.1 200` (no space) is RemoteProtocolError.
- CF-000026 (N-000097 other control bytes allowed vs N-000108 refused): built N-000097: only NUL, CR, LF, FF, VT are refused, plus leading/trailing space/tab; other control bytes (and tab inside) are allowed.
- CF-000048 (N-000317 14..18 KiB vs N-000479 8 KiB default): built 16384 bytes (satisfies N-000317; N-000479 not followed).
- CF-000050 (N-000137 HEAD response no framing headers vs N-000219 same framing as GET): built N-000219 (headers chosen as for GET; body is empty).
- CF-000074 (N-000165 lone LF accepted vs N-000510 CRLF required): built accept lone LF (and mixed).
- CF-000075/76/100 (obs-fold joined vs continuation line refused, N-000167-169 vs N-000176): built fold acceptance: continuation joined to the previous value with one space. A continuation as the very first header line is refused.
- CF-000083 (N-000357 HTTP/1.0 sets no flag vs N-000491 any version): built N-000357: only HTTP/1.1 requests set the flag.
- CF-000098 (N-000116 up to 18 digits vs N-000462 more than 16 refused): built max 18 digits; 19+ refused. (A 17/18-digit value is accepted, against N-000462.)
- CF-000099 (N-000194 64 hex digits vs N-000228 16..32): built max 20 hex digits in a chunk-size line.
- CF-000101 (N-000230 whitespace after size allowed vs N-000243 refused): built allowed (spaces/tabs after size/extension); other junk refused.
- CF-000102 (N-000199 keep `Content-Length: 0` vs N-000218 drop): built keep (header is never removed from a Content-Length response).
- CF-000103 (N-000021 contains `close` vs N-000262 whole token): built whole comma-separated token, case-insensitive.
- CF-000104 (N-000354 case-insensitive vs N-000493 lowercase only): built case-insensitive.
- CF-000105 (N-000353 body events don't end the wait vs N-000359 they do): built N-000359 (data or end-of-message from the client clears the flag).
- CF-000106 (N-000364 any 2xx vs N-000396 only 200): built any 2xx accepts CONNECT.
- CF-000107 (N-000093 repeated chunked TE collapse vs N-000121 refuse with 501): built refuse with 501.

## Unstated items / assumptions

- Invalid role to `Connection(...)`: spec says only "an exception". Raises a class that subclasses both `LocalProtocolError` and `ValueError`.
- `send()` of a ConnectionClosed returns `b""`; passthrough returns `[]`.
- `Request`/responses accept omitted `headers` (treated as empty); a 1.1 request still needs Host.
- `their_http_version` is `None` until recorded and is kept across `start_next_cycle`.
- HTTP version strings must match `\d.\d`; a reason phrase may not contain CR/LF.
- Header names with a space before the colon are refused when parsing.
- After a remote error, a response sent by the server gets `Connection: close`.
- Chunk data terminator must be exactly CRLF (checked, partial prefixes wait for more bytes).
- The incomplete-event limit is checked whenever a pull would return NEED_DATA with more than the limit stored (body bytes are consumed so never count).
