# NOTES

Layout: package `httpwire/` (`_util.py` errors/sentinels/validation, `_events.py` events + header list,
`_connection.py` state machine, parser, writers). No build step; `pyproject.toml` is provided for setuptools.
Every checklist id is implemented by the behaviour described in its pack, except those marked "not done" below.
Non-goal/constraint ids (no I/O, no CLI, no deps, no HTTP/2, no non-chunked TE, etc.) are satisfied by absence.
Smoke script: `tests/smoke_extra.py` (a smoke script, not a formal test suite).

## Spec disagreements (the 19 unsettled conflicts) and what I built

- CF-000003 N-000096 (pack 14) "the Content-Length decides how the body is framed" vs N-000207 (pack 16) "transfer-encoding wins".
  Built: Transfer-Encoding: chunked wins for framing (requests, responses, received messages); both headers stay in the event's header list, Content-Length is dropped only when a response is sent.
- CF-000005 N-000166 (pack 15) status line without reason "is accepted and the reason is empty" vs N-000516 (pack 08) "is illegal". Built: accepted, reason is `b""`. Sending writes `HTTP/1.1 200 ` (trailing space) when reason is empty.
- CF-000026 N-000097 (pack 14) values may contain "other control bytes" vs N-000108 "Control bytes other than tab are refused". Built: only NUL, CR, LF, FF, VT are refused; leading/trailing space/tab refused.
- CF-000048 N-000317 (pack 18) default limit 14–18 KiB vs N-000479 (pack 08) 8 KiB. Built: 16384 bytes.
- CF-000050 N-000137 (pack 15) HEAD response has no framing headers vs N-000219 (pack 16) same framing headers as GET. Built: same headers as for GET (chunked for 1.1 peers), body empty.
- CF-000074 N-000165 (pack 15) lone LF accepted vs N-000510 (pack 08) every line must end CRLF. Built: lone LF accepted in header blocks and chunk-size lines.
- CF-000075/76/100 N-000167–169 (pack 15) obsolete folding accepted/joined vs N-000176 continuation line refused. Built: accepted, joined with one space. A continuation as the first header line is refused.
- CF-000083 N-000357 (pack 20) HTTP/1.0 request with Expect sets neither flag vs N-000491 (pack 08) any version sets it. Built: any version sets `client_is_waiting_for_100_continue` (contract wins).
- CF-000098 N-000116 (pack 14) ≤18 digits accepted vs N-000462 (pack 06) >16 refused. Built: max 18 digits (19+ refused).
- CF-000099 N-000194 (pack 16) up to 64 hex digits vs N-000228 16–32. Built: max 32.
- CF-000101 N-000230 (pack 16) trailing whitespace after chunk size allowed vs N-000243 refused. Built: allowed (spaces/tabs before line end).
- CF-000102 N-000199 (pack 16) keep Content-Length 0 on response vs N-000218 omit it. Built: kept as given.
- CF-000103 N-000021 (pack 10) any Connection value containing `close` vs N-000262 (pack 17) whole comma element. Built: whole element, case-insensitive.
- CF-000104 N-000354 (pack 20) Expect token case-insensitive vs N-000493 (pack 08) exactly lowercase. Built: case-insensitive token in comma list.
- CF-000105 N-000353 (pack 20) body events don't end wait vs N-000359 they do. Built: client data/end-of-message clears the flag.
- CF-000106 N-000364 (pack 20) any 2xx accepts CONNECT vs N-000396 only 200. Built: any 2xx accepts.
- CF-000107 N-000093 (pack 14) repeated TE chunked collapse vs N-000121 second TE header refused with 501. Built: refused with 501.

## Unstated items and assumptions
- Role validation: invalid role raises `ValueError`. Feeding data after close raises `RuntimeError`.
- Empty header values are allowed. Content-Length is stored normalized as decimal (`007` -> `7`).
- `send` returns `None` for ConnectionClosed, otherwise `bytes`.
- `Connection.states` is a dict `{CLIENT: ..., SERVER: ...}`.
- Event http_version must match `[0-9].[0-9]`. `bool` is not accepted as a status code.
- A server accepting an Upgrade/CONNECT before the client finished its request is not specially handled.
- Chunk header lines with no newline are only bounded loosely; the incomplete-event limit applies only to start line + headers.
- Not done: N-000043 / platform items (Windows/macOS) and PyPy support are untested; code uses only portable stdlib.
