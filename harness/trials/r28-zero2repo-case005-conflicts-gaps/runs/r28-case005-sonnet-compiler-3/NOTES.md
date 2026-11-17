# NOTES

Implementation: package `httpwire/` (`_events.py`, `_states.py`, `_errors.py`, `_connection.py`, re-exported from `__init__.py`). No build step; zero dependencies. All checklist ids (N-000413 … N-000522 and the PRD packs 09–20) are implemented in that package as specified, except where a conflict below picks one side. I wrote no per-id `# spec:` markers and no tests, and I ran only a short smoke script (request/response, chunked, Upgrade).

## Contradictions (spec disagrees with itself) and what I built

- **CF-000003** (FP-01 N-000096 "Content-Length decides framing" vs FP-03 N-000207 "transfer-encoding wins"): built TE wins; a response with both gets no Content-Length and is chunked.
- **CF-000005** (FP-02 N-000166 "status line without reason accepted, reason empty" vs Interface N-000516 "illegal"): built the Interface rule: `HTTP/1.1 200\r\n` is a RemoteProtocolError. `HTTP/1.1 200 \r\n` (space, empty reason) is accepted. Sent status lines always carry the trailing space.
- **CF-000026** (N-000097 "any byte except NUL CR LF FF VT" vs N-000108 "control bytes other than tab refused"): built the explicit forbidden list (NUL, CR, LF, FF, VT); other control bytes are allowed.
- **CF-000048** (N-000317 default 14–18 KiB vs N-000479 8 KiB): built 16 KiB (inside the PRD range).
- **CF-000050** (N-000137 HEAD response has no framing headers vs N-000219 same framing headers as GET): built N-000219; the body is empty either way.
- **CF-000074** (N-000165 lone LF accepted vs N-000510 every line ends CRLF): header blocks accept lone LF; request/status/chunk-size lines in chunked bodies and the chunk terminator are CRLF-strict where practical.
- **CF-000075/76** (N-000168/169 obs-fold joined vs N-000176 continuation refused): obs-fold is joined (leading whitespace becomes one space). A continuation line with no preceding header is refused.
- **CF-000083** (N-000357 HTTP/1.0 `Expect` sets no flag vs N-000491 sets it for any version): built the PRD rule: only HTTP/1.1 requests set the flag. `Expect` is matched case-insensitively.

Conflicts not flagged by the export, found while building:
- Content-Length digit limit: Interface says more than 16 digits is refused; FP-01 says at most 18 digits are accepted and the limit is 18–32. Built 18.
- Chunk-size digit limit: FP-03 says "up to 64 hex digits" in one bullet and "16 to 32" in another. Built 32.
- Response `Content-Length: 0`: FP-03 says it is kept on the wire and also that it is sent without it. Built: kept.
- CONNECT acceptance: FP-07 says 2xx accepts in one bullet and "only 200 accepts" in the boundary bullet. Built 2xx.
- Whitespace after a chunk size: FP-03 says optional spaces/tabs are allowed and also that whitespace is refused. Built: allowed (before `;ext` or the CRLF).

## Unstated details (assumed)
- Invalid `role` raises `ValueError`. Bytes fed after close raise `RuntimeError`.
- Invalid event constructor types (e.g. a non-bytes method) raise `LocalProtocolError`.
- `states` is a dict `{CLIENT: ..., SERVER: ...}`. `their_http_version` is `None` until recorded, and resets to `None` on `start_next_cycle`.
- `send()` returns `None` for ConnectionClosed and `bytes` (possibly empty) otherwise.
- A 101 informational response with no pending Upgrade proposal is a local protocol error.
- Non-1xx/204/304 status checks for the incomplete-event limit use `len(buffer) > limit` when a pull would return NEED_DATA.
- Python 3.8, Linux, CPU only; no package metadata beyond a minimal `pyproject.toml`.
