# NOTES

Build of `httpwire` from `spec/` (export with 9 unsettled contradictions, `--allow-open`).
`spec/` is unchanged. Code is in `httpwire/`, tests in `tests/test_httpwire.py`, packaging in `pyproject.toml`.

Run the tests: `PYTHONPATH=/app python3 -m pytest -q tests` (90 pass on Python 3.13).

Nothing was verified on Python 3.8 or PyPy, or on macOS/Windows. The code uses no 3.9+ syntax.

## 1. Conflicts and what I built

Each entry names the two sides (pack and claim id) and the choice. The first nine are the
`UNSETTLED` contradictions listed in `spec/MAP.md`. The rest are conflicts the export did not flag.

### Flagged as unsettled (CF-…)

| Id | Side A | Side B | Built |
|---|---|---|---|
| CF-000003 | pack 14 N-000096: when an event carries both framing headers, "the `Content-Length` decides how the body is framed." | pack 16 N-000207: a response built with both `Transfer-Encoding: chunked` and `Content-Length` — "transfer-encoding wins". | Both rules, by context. A **constructed response** with TE chunked drops Content-Length (TE wins, as FP-03 says). **Every other case** (request, received message) uses Content-Length (FP-01 rule). |
| CF-000005 | pack 15 N-000166: a response status line without a reason phrase "is accepted and the reason is empty." | pack 08 N-000516: a received status line without a reason "is illegal." | **Accepted**, reason empty (FP-02 normal behaviour). |
| CF-000026 | pack 14 N-000097: header values may contain "other control bytes". | pack 14 N-000108: "Control bytes other than tab are refused in header values." | **Refused**: any byte below 0x20 except tab, and 0x7F (DEL). NUL, CR, LF, FF, VT are refused under both readings. |
| CF-000048 | pack 18 N-000317: default incomplete-event limit is "at least 14 KiB and less than 18 KiB". | pack 08 N-000479: when omitted, the limit "is 8 kibibytes". | **16 KiB** (16384). It meets the FP-05 range. Passing `None` also means the default. |
| CF-000050 | pack 15 N-000137: "A response to HEAD is written with no framing headers." | pack 16 N-000219: a server answering HEAD "writes the same framing headers it would have used for GET". | **GET framing headers** (chunked for an HTTP/1.1 peer, close framing for HTTP/1.0). The body stays empty, so no chunk bytes follow. This follows N-000219, the more specific claim. |
| CF-000074 | pack 15 N-000165: lone-LF and mixed line endings "are accepted." | pack 08 N-000510: every received line "must end with CRLF." | **Accepted** in head and trailer blocks and chunk-size lines. Chunk **data** terminators must be exactly CRLF (pack 16 N-000244/245). |
| CF-000075 / CF-000076 | pack 15 N-000168/169: obsolete line folding is joined, leading whitespace becomes one space. | pack 15 N-000176: a continuation line "is refused." | **Accepted** (folded). This matches the "allowing only the leniencies stated above" wording in N-000174. |
| CF-000083 | pack 08 N-000491 / pack 20 N-000357: `Expect: 100-continue` on an HTTP/1.0 request — one side says it sets `client_is_waiting` "whatever its HTTP version", the other says it sets neither flag. | | **Not set** for HTTP/1.0. This is the FP-07 wording. Only HTTP/1.1 requests set the flag. |

### Not flagged by the export (found while building)

1. **Repeated `Transfer-Encoding: chunked`.** pack 14 N-000092..N-000096 says repeated TE headers "collapse to one". Pack 14 N-000120/121 and pack 18 N-000294/295 say a second TE header is refused with 501, "even when both values are `chunked`". **Built: refuse with 501.** The two boundary rules say so twice; the collapse rule is only in the normal behaviour.
2. **Content-Length 0 on a response.** pack 16 N-000199: the header "is kept on the wire, including when N is 0." Pack 16 N-000218: "A response with `Content-Length: 0` is sent without that header." **Built: kept** (N-000199 is a general rule, N-000218 sits in the HEAD/204/304 bullet).
3. **Content-Length digit limit.** Pack 06 N-000462 (Interface): a value "longer than 16 digits is refused." Pack 14 N-000114..N-000117 (PRD): every value of at most **18** digits "is accepted", and the limit is the implementer's choice from 18 to 32. **Built: 18 digits.** A 17- or 18-digit value is accepted, as the PRD MUST requires.
4. **Chunk-size digits.** Pack 16 N-000192 (MAY): a size line "may carry up to 64" hex digits. Pack 16 N-000228..N-000232: the limit is the implementer's choice from 16 to 32. **Built: 32** (N-000192 is a MAY, and 64 is outside the implementer range).
5. **Whitespace in chunk-size lines.** Pack 16 N-000228: "optionally followed by spaces or tabs, then the line ending" (after the size and extension). Pack 16 N-000242: "Whitespace after the chunk size is refused." **Built:** whitespace is refused directly after the hex digits. It is accepted after a `;extension`, which is discarded.
6. **Expect token case.** Pack 08 (Interface `they_are_waiting_for_100_continue`): "The `Expect` value must be exactly the lowercase token `100-continue`." Pack 20 N-000354 (FP-07): the token is "matched case-insensitively". **Built: case-insensitive.**
7. **CONNECT acceptance status.** Pack 20 N-000364, N-000371, N-000395: "a 2xx response accepts CONNECT." Pack 20 N-000398: "Only status 200 accepts a CONNECT proposal; other 2xx statuses deny it." **Built: any 2xx accepts** (three claims against one).

## 2. Gaps the spec does not state, and my assumptions

- **Default limit** is 16 KiB (see CF-000048). A limit passed explicitly is used as given.
- **Connection(role)** with a bad role raises `LocalProtocolError`. The spec only says "an exception".
- **Refused send ⇒ ERROR.** Every send refused as a local protocol error puts our side in ERROR, as FP-05 says, including an illegal `ConnectionClosed` send and a refused `Data`/`EndOfMessage`.
- **Construction errors** are not sends. They raise and leave the connection untouched.
- **Ordering of pulls.** `ERROR` on the peer raises `RemoteProtocolError` (hint 400) on every later pull. Pull order is: ERROR, then PAUSED (switch states), then CLOSED, then DONE/MUST_CLOSE, then body reader, then header block. A byte before the header block that is a space or control byte fails at once.
- **Peer in MUST_CLOSE with buffered bytes** returns `PAUSED` (not stated). A pull after the peer's ConnectionClosed (CLOSED) returns `ConnectionClosed` again.
- **Close while the peer is IDLE with bytes buffered** is parsed as a message. A partial message followed by a close is a remote error.
- **Received response with neither framing header** is close-delimited for **any** peer version, not only HTTP/1.0. This follows RFC 7230 §3.3.3. The spec only states the HTTP/1.0 case. The connection is then MUST_CLOSE after the body.
- **Received request target/version.** Request and status lines accept HTTP/1.0 and HTTP/1.1 only. Other versions are a remote error.
- **Request and status line format.** Written as `METHOD SP target SP HTTP/1.1` and `HTTP/1.1 SP code SP reason`. With an empty reason the status line keeps the trailing space (`HTTP/1.1 200 `).
- **Reason phrase** may contain tab, visible ASCII and bytes 0x80..0xFF. CR, LF and other controls are refused. The spec does not say.
- **Content-Length canonical form.** The stored value is the canonical decimal (leading zeros dropped). A collapsed header keeps the first occurrence's name spelling.
- **Request with no framing headers** writes no Content-Length. The spec says the body is empty, so no header is needed.
- **Data on an empty-body response** (HEAD, 204, 304). Non-empty data is refused as a local error. Empty data is a no-op. The spec says "no data is sent" but does not say whether the call is refused.
- **Trailing headers on an empty-body message** are refused.
- **Switch proposals.** A proposal is a CONNECT request or any request with an `Upgrade` header. An accept (2xx for CONNECT, 101 for Upgrade) counts only while the client is MIGHT_SWITCH_PROTOCOL, i.e. after its end-of-message. A final response sent before the client's end-of-message is a plain response, and the proposal is dropped.
- **Denial** moves the client straight to DONE when the server's final response arrives (FP-07 N-000378).
- **Keep-alive** is judged at each end-of-message. Requests from the client can still get a `Connection: close` from the server later. Both sides are then forced to MUST_CLOSE by the pairing rules.
- **Close-delimited body end.** When the peer's side closes, the next pull yields `EndOfMessage()` and then `ConnectionClosed()`.
- **Passthrough** returns bytes-like payloads and non-bytes objects with a length unchanged, by identity. `send()` joins only bytes-like payloads; a non-bytes object raises a local error from `send()` (and marks ERROR).
- **Event equality** compares fields (type-checked). `Data` compares bytes content and the two marks. This is not in the spec; it only makes tests easier.
- **`ProtocolError`** is an extra common base class of the two protocol-error kinds. It is not exported.
- **`ReceiveClosedError`** (a `RuntimeError`) is the "bytes after end-of-receive" error. It is not exported.
- **Packaging.** `pyproject.toml` has a setuptools flat layout (`packages = ["httpwire"]`, no dependencies). I did not build or install it, so the build metadata is unchecked.

## 3. Coverage by checklist id

`spec/CHECKLIST.md` is not edited (the spec stays as-is). Coverage is recorded here. A check mark means implemented in the named module and exercised by the test name prefix. "Verified by reading" means implemented but not executed here.

| Ids | Pack / feature | Where | Status |
|---|---|---|---|
| N-000001..N-000009 | 09 PRD product overview | `_connection.py` (no sockets); `_events.py` | implemented; N-000003 (no I/O) by construction |
| N-000010..N-000021 | 10 terminology | `_state.py`, `_connection.py` | implemented |
| N-000022..N-000036 | 11 public surface inventory | `__init__.py` and the feature points | implemented |
| N-000037..N-000058 | 12 non-functional | `pyproject.toml`; `_connection.py` | N-000040/41 (3.8+), N-000042/43 (platforms), N-000426..428 (packaging): **verified by reading only** |
| N-000059..N-000069 | 13 non-goals | rejected: non-chunked TE, HTTP/2 versions, 1.0 keep-alive | implemented (negative behaviour) |
| N-000070..N-000121 | 14 FP-01 events and headers | `_events.py` | implemented; tests `test_*request*`, `test_header_*`, `test_content_length_*`, `test_transfer_encoding_rules`, `test_status_ranges_and_types` |
| N-000122..N-000182 | 15 FP-02 connection | `_connection.py` | implemented; tests `test_request_bytes_*`, `test_two_step_*`, `test_round_trip_*`, `test_remote_error_*`, `test_feeding_after_close_*` |
| N-000183..N-000246 | 16 FP-03 framing | `_framing.py`, `_connection.py` | implemented; tests `test_chunked_*`, `test_chunk_*`, `test_content_length_*`, `test_response_to_*`, `test_head_*`, `test_204_304_*`, `test_received_close_delimited_*` |
| N-000247..N-000289 | 17 FP-04 lifecycle | `_connection.py` (`_plan`, `_install`, `start_next_cycle`) | implemented; tests `test_keep_alive_*`, `test_connection_close_*`, `test_http10_*`, `test_pipelined_*`, `test_start_next_cycle_*` |
| N-000290..N-000331 | 18 FP-05 errors and limit | `_errors.py`, `_connection.py`, `_framing.take_block` | implemented; tests `test_incomplete_event_size_limit_431`, `test_send_failed_*`, `test_remote_error_*` |
| N-000332..N-000348 | 19 FP-06 shutdown | `_connection.py` | implemented; tests `test_client_closes_idle_*`, `test_close_*`, `test_pulled_close_*` |
| N-000349..N-000412 | 20 FP-07 1xx, 100-continue, switch | `_connection.py` (proposal flags, `_plan`) | implemented; tests `test_informational_*`, `test_expect_*`, `test_connect_*`, `test_upgrade_101_*`, `test_client_cannot_send_request_while_might_switch` |
| N-000413..N-000417 | 02 hardware summary | no compiled code, no deps | verified by reading only (no install run) |
| N-000418..N-000428 | 03 execution profiles | flat layout, `pyproject.toml` | verified by reading only |
| N-000429..N-000432 | 04 interface overview | library only; no `__main__`, no CLI, no exit codes | implemented |
| N-000433..N-000449 | 05 public surface | `__init__.py` names exactly as listed | implemented; `test_package_root_names_and_identity` |
| N-000450..N-000471 | 06 events interface | `_events.py` | implemented; header list tests |
| N-000472..N-000475 | 07 errors interface | `_errors.py` | implemented |
| N-000476..N-000522 | 08 Connection interface | `_connection.py` | implemented; the attribute, send/pull and `start_next_cycle`/`send_failed` tests |

Nothing in the checklist is left "not done". The items marked "verified by reading only" were not run on other
interpreters or platforms, and the build was not exercised.

## 4. Known limits

- The 100-continue flag is one conversation-level flag, read from both roles. Client-role connections report `they_are_waiting_for_100_continue` as False, as the spec says.
- No timeouts, no I/O, no threads. A slow body is simply `NEED_DATA`.
- Long chunk-size lines without a line ending are checked for digit count and invalid bytes, but are not bounded by the incomplete-event size limit. The spec limits only request/response lines and header blocks.
