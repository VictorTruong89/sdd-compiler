# NOTES

Layout: package `httpwire/` (flat, pure Python, no deps). Modules: `_events.py` (events, header
normalisation), `_connection.py` (state machine, readers/writers, `Connection`), `_states.py`,
`_errors.py`. Importing needs only `/app` on the path (a `pyproject.toml` is also provided).

## Checklist accounting
All N-ids in `spec/CHECKLIST.md` (packs 02–20) are implemented in the code above, except where a
conflict below says otherwise (the losing side of each conflict is "not done", with reason given).
Non-code / non-goal claims (no network I/O, no CLI, no config file, no deps, CPU-only, Python >=3.8,
no HTTP/2, no chunked-extension preservation, no `Connection: keep-alive` for HTTP/1.0, no non-chunked
transfer codings) are satisfied by absence. Free-text claims (error message wording N-000473/N-000058,
class of the "bytes after close" exception N-000475) are the implementer's choice: `RuntimeError`.
Constructing with a bad role raises `ValueError`.

## Contradictions and what I built
- CF-000003 (N-000096 "Content-Length decides" vs N-000207 "transfer-encoding wins"): TE wins in
  framing (requests and responses); event header lists keep both headers; on send of a Response the
  Content-Length is dropped.
- CF-000005 (N-000166 no-reason status line accepted vs N-000516 illegal): accepted, reason empty.
- CF-000026 (N-000097 other control bytes allowed vs N-000108 refused): refused set is exactly NUL,
  CR, LF, FF, VT (N-000097/N-000099); other control bytes, including tab inside, are accepted.
  N-000108 not done.
- CF-000048 (N-000317 14–18 KiB vs N-000479 8 KiB): default 16 KiB (16384).
- CF-000050 (N-000137 HEAD no framing headers vs N-000219 same framing headers as GET): same as GET.
- CF-000074 (N-000165 lone LF accepted vs N-000510 CRLF required): lone LF accepted in request/status
  line and header/trailer blocks. Chunk-size lines require CRLF.
- CF-000075/76 (N-000168/169 fold joined vs N-000176 refused): folding accepted (joined with a single
  space); a continuation line as the first header line is refused.
- CF-000083 (N-000357 HTTP/1.0 sets neither flag vs N-000491 whatever the version): only HTTP/1.1
  requests set the flag. Also the Interface says the `Expect` value must be exactly lowercase
  `100-continue` while FP-07 says case-insensitive: case-insensitive, token inside a comma list.

Unlisted disagreements I found:
- Repeated `Transfer-Encoding: chunked` "collapse to one" (N-000092..95) vs "second Transfer-Encoding
  header refused, status 501" (N-000121): refused.
- Content-Length max digits: Interface "longer than 16 refused" vs FP-01 "<=18 accepted, max 18–32":
  18 is the maximum.
- Chunk size digits: FP-03 "up to 64 hex digits" (N-000194) vs "16–32 fixed" (N-000228): 32.
- Whitespace after chunk size: refused only before `;` ; allowed after size/extension (grammar in N-000228).
- CONNECT acceptance "2xx" (N-000364) vs "only 200 accepts, other 2xx deny" (N-000397): only 200 accepts.
- Response with `Content-Length: 0` "sent without that header" (N-000218) vs "kept on the wire including 0"
  (N-000199): kept.
- Interface `send` of an event with no bytes: returns `None` for ConnectionClosed, `b""` otherwise.

## Unstated, assumed
- `Request/Response` http_version must match `[0-9].[0-9]`. Bool is not accepted as a status code.
- Connection role validation exception type: ValueError.
- After a remote protocol error, a server Response always gets `Connection: close`.
- `Connection.start_next_cycle` also resets the remembered request method.
- `states` returns a dict keyed by CLIENT/SERVER.
- Sending ConnectionClosed from CLOSED is allowed (idempotent).
