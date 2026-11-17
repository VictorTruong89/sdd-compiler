# NOTES — httpwire build

Build of the httpwire library from `spec/` (packs 01–20, `spec/CHECKLIST.md` ids N-000001..N-000522).

Layout:

- `httpwire/` — the package (flat layout at the repo root, as `spec/packs/03` requires)
  - `__init__.py` — public surface (Pack 05 list)
  - `_events.py` — six event types (FP-01)
  - `_headers.py` — header list, normalization, framing-header rules (FP-01)
  - `_errors.py` — `LocalProtocolError`, `RemoteProtocolError`, `error_status_hint`; the "bytes after end-of-receive" runtime error (FP-02/05/06)
  - `_state.py` — roles, the nine states, `NEED_DATA`, `PAUSED`
  - `_connection.py` — `Connection`: state machine, send side, framing on send (FP-02..FP-07)
  - `_receive.py` — receive side: feed, pull, head/body/chunked/trailer parsing (FP-02..FP-07)
- `tests/test_httpwire.py` — 44 tests, named by feature point; run with `python3 -m pytest tests`
- `pyproject.toml` — setuptools metadata, zero runtime dependencies, `requires-python >= 3.8`

Verification: `python3 -m pytest -q tests` → 44 passed on this machine (Python 3.x). No compiled code, no third-party runtime deps.

## 1. Conflicts in the spec

### 1a. The nine unsettled contradictions (`spec/MAP.md`, `export.meta.json`)

The export was made with `--allow-open`, so these have no human verdict. For each, the two sides and my choice:

| Id | Side A | Side B | What I built |
|---|---|---|---|
| CF-000003 | FP-01 `spec/packs/14` N-000096: "the `Content-Length` decides how the body is framed" (when an event carries both) | FP-03 `spec/packs/16` N-000207: a response built with both `Transfer-Encoding: chunked` and `Content-Length` uses transfer-encoding | Two rules, one per direction. **Requests** received or sent with both: Content-Length decides (A). **Responses** sent or received with both: Transfer-Encoding wins (B). Both sentences are satisfied as written, since A names the event header list in general and B names the response case. |
| CF-000005 | FP-02 `spec/packs/15` N-000166: a response status line without a reason phrase "is accepted and the reason is empty" | Interface `spec/packs/08` N-000516: a received status line without a reason phrase "is illegal" | Accepted (A). Reason is empty. `next_event` on the client side accepts `HTTP/1.1 200` with no reason. |
| CF-000026 | FP-01 `spec/packs/14` N-000097: header values may contain "other control bytes and non-ASCII bytes" | FP-01 N-000108: "Control bytes other than tab are refused in header values" | Refused (B). Control bytes other than tab (and DEL) are rejected; non-ASCII bytes ≥ 0x80 are accepted. |
| CF-000048 | FP-05 `spec/packs/18` N-000317: default limit "at least 14 KiB and less than 18 KiB" | Interface `spec/packs/08` N-000479: "When it is omitted, the limit is 8 kibibytes" | 8 KiB (B). The interface is the one place that defines the constructor default. |
| CF-000050 | FP-02 `spec/packs/15` N-000137: "A response to HEAD is written with no framing headers" | FP-03 `spec/packs/16` N-000219: a server answering HEAD "writes the same framing headers it would have used for GET" | Same framing headers as GET (B), with an empty body and no body bytes. FP-03 is the framing feature point. |
| CF-000074 | FP-02 N-000165: header blocks with lone-LF line endings "are accepted" | Interface N-000510: "every received line must end with a carriage return and line feed" | Lone LF accepted on receive (A). The interface rule is about *received* lines; I accept both CRLF and LF there. |
| CF-000075 | FP-02 N-000168: a continuation line "is joined to the previous header's value" | FP-02 N-000176: a continuation line "is refused" | Refused (B). Obsolete line folding is rejected on receive. |
| CF-000076 | FP-02 N-000169: leading whitespace of a continuation line "replaced by a single space" | FP-02 N-000176: the same continuation line "is refused" | Refused (B), same as CF-000075. |
| CF-000083 | FP-07 `spec/packs/20` N-000357: an `Expect: 100-continue` on an HTTP/1.0 request "sets neither flag" | Interface N-000491: any request with that header sets `client_is_waiting_for_100_continue` "whatever its HTTP version" | HTTP/1.0 sets neither flag (A). FP-07 is the feature point that defines the flag behavior; the interface line is a summary. |

### 1b. Conflicts not listed in the export

These are contradictions inside the text that the compiler did not flag:

1. **Chunk-size digit limit.** `spec/packs/16` N-000192 (FP-03): a received size line "may carry up to 64 hexadecimal digits". N-000228 (FP-03): the digit maximum is an implementer's choice "from 16 to 32 inclusive", and N-000242 refuses anything longer. *Built:* 32 digits. N-000192 is a MAY-level claim about what peers may send, and it cannot be satisfied together with the 16–32 rule, so 32 is the top of the implementer's range.
2. **Whitespace after the chunk size.** N-000228 (FP-03): the size line may be "optionally followed by spaces or tabs, then the line ending". N-000242 (FP-03): "Whitespace after the chunk size is refused." *Built:* whitespace directly after the hex digits is refused. Spaces/tabs are accepted only after a `;` chunk extension. (A literal reading of both sentences can only hold if the whitespace is after the extension.)
3. **CONNECT acceptance status.** FP-07 N-000364/N-000371/N-000395: "a 2xx response accepts CONNECT". FP-07 N-000394–N-000398 (boundary): "Only status 200 accepts a CONNECT proposal; other 2xx statuses deny it." *Built:* only 200 accepts (the boundary rule is the more specific statement).
4. **Expect value matching.** FP-07 N-000354: the `100-continue` token is matched case-insensitively. Interface `spec/packs/08` row 9 (`they_are_waiting_for_100_continue`): "The `Expect` value must be exactly the lowercase token `100-continue`." *Built:* case-insensitive for both flags, following FP-07.
5. **Keep-alive on error responses.** FP-05 says the response after a remote error carries `Connection: close`; I also set keep-alive off on remote error so this holds. Not a conflict, noted for completeness.

## 2. Things the spec does not state (my assumptions)

- **Receive-side framing for a response with neither Content-Length nor Transfer-Encoding** from a *1.1* peer. FP-03 (N-000208–N-000214) covers only HTTP/1.0 peers. *Assumed:* close-delimited (read until the receive side closes), and keep-alive is disabled.
- **Send-side framing for a response with neither header from a *1.1* peer.** FP-03 says the product writes chunked for a 1.1 peer (N-000202). Followed.
- **204 and 304 responses.** FP-03 says the body is always empty. Not stated: whether framing headers are sent. *Assumed:* Content-Length and Transfer-Encoding are stripped from 204/304 responses.
- **Content-Length: 0 on an empty-body response.** Stripped (N-000218). Content-Length: 0 on a normal response is kept (N-000199).
- **Status line on send with no reason.** `HTTP/1.1 200 ` (space, then empty reason, then CRLF). FP-02 says the status line "followed by the reason the caller supplied"; an empty reason needs a defined form, so the trailing space is kept.
- **Reason phrase content.** Not stated. *Assumed:* CR and LF in a reason are refused as a local protocol error.
- **Header value whitespace on receive.** FP-01 refuses values that *begin or end* with space or tab on construction. On the wire, optional whitespace after the colon and before the line end is standard syntax, so I strip it on receive (not on construction).
- **Peer HTTP version on receive.** Only `HTTP/1.0` and `HTTP/1.1` are accepted in a peer's start line. Other versions are a remote protocol error. Not stated.
- **Request target / method on receive.** Validated by the same rules as construction (FP-01). Constructor errors on receive are converted to remote protocol errors.
- **Trailing headers on requests sent with chunked framing to a peer whose version is not known.** Allowed; the 1.0 refusal applies only when the peer version is known to be 1.0 (FP-03 N-000241).
- **Data events with a non-bytes payload in `send()`** (not the passthrough call): joined with `b"".join`, which requires a buffer object; a non-buffer raises `TypeError` from join. Not stated.
- **`states` return type.** Interface allows a mapping or a pair. I return a `dict` keyed by `CLIENT` and `SERVER`.
- **`states` after a switch and `send_failed`.** Follows FP-05/FP-07 directly.
- **`start_next_cycle` and `their_http_version`.** Not stated whether the recorded peer version resets. *Assumed:* retained until the next request or response is pulled.
- **Incomplete-event size limit.** Applies to the start line plus header block (and trailing header block after chunked data). Chunk-size lines are bounded by the digit limit instead. Not stated.
- **Default `max_incomplete_event_size` of 8 KiB** (CF-000048 resolved toward the interface).
- **Error text.** Free text, per PRD N-000058 and Interface N-000473.
- **Error class for "feed after end-of-receive".** `BytesAfterEndOfReceive(RuntimeError)`, defined in `_errors.py`. It is not on the package-root list (the list is the complete public surface), so it is reachable only as `httpwire._errors.BytesAfterEndOfReceive`. Callers see it as a `RuntimeError`.
- **Local error ERROR state on invalid construction.** Construction failures produce no connection change (FP-05 N-000297–N-000299), so they do not set ERROR.
- **Pulled `ConnectionClosed` from a peer in a state that does not allow it.** Treated as a remote protocol error that sets the peer's state to ERROR (FP-06 N-000347). Not specified whether our side changes; it does not.
- **Pausing for a MUST_CLOSE peer with buffered bytes.** `next_event` returns `PAUSED` (the peer cannot send more HTTP). Not stated.

## 3. Checklist accounting (`spec/CHECKLIST.md`, 522 ids)

Every id is accounted for. Ids are grouped by pack; the spec's `CHECKLIST.md` is kept as-is, as the build contract requires.

| Pack | Ids | Status | Where |
|---|---|---|---|
| 01 Hardware requirements (no claims; broad constraints) | (no node) | implemented: no I/O, no runtime deps, no native code, no CLI | `pyproject.toml`, all modules (pure Python, stdlib imports only: `re`) |
| 02 Hardware summary | N-000413–417 | implemented (no I/O, no native code, zero runtime deps, Python ≥ 3.8 floor) | `pyproject.toml` (`requires-python`, `dependencies = []`) |
| 03 Execution profiles | N-000418–428 | implemented (CPU-only, flat layout, setuptools; no compile step) | `pyproject.toml`, package at repo root |
| 04 Interface product overview | N-000429–432 | implemented (importable library; no CLI, no config file, no exit codes, no `__main__`) | `httpwire/__init__.py` |
| 05 Public surface | N-000433–449 | implemented and tested: the 22 names are exported from the package root, the nine states are distinct singleton objects, `LocalProtocolError` and `RemoteProtocolError` are unrelated classes | `httpwire/__init__.py`, `httpwire/_state.py`, `httpwire/_errors.py`; `test_roles_and_initial_states` |
| 06 Events | N-000450–471 | implemented and tested: constructor keywords, bytes storage, `Content-Length` digit limit, header list with `raw_items()`, invalid construction raises `LocalProtocolError` | `httpwire/_events.py`, `httpwire/_headers.py`; `test_request_default_version_and_bytes_storage`, `test_content_length_and_transfer_encoding_normalization`, `test_data_chunk_marks_and_constructor_defaults` |
| 07 Errors | N-000472–475 | implemented and tested: `error_status_hint` is `int`, `str(error)` is the message, feed-after-end-of-receive is a `RuntimeError` | `httpwire/_errors.py`; `test_feed_after_close_is_runtime_error_not_protocol` |
| 08 `Connection` | N-000476–522 | implemented and tested: signature, attributes (incl. `trailing_data`, 100-continue flags), `send`, `send_with_data_passthrough`, `receive_data`, `next_event`, `start_next_cycle`, `send_failed` | `httpwire/_connection.py`, `httpwire/_receive.py`; `test_roles_and_initial_states`, `test_request_round_trip_and_host_first`, `test_passthrough_keeps_object_identity`, `test_trailing_data_reports_leftover`, `test_send_failed_marks_error`, `test_start_next_cycle_refused_when_not_done_is_recoverable` |
| 09 PRD product overview | N-000001–009 | implemented by design (the library turns events into bytes and back; no network I/O; feature points are behavior) | all modules; the no-I/O property is by construction (no imports of socket/os/subprocess) |
| 10 Terminology | N-000010–021 | implemented and tested (send, passthrough send, pull, need-data, paused, mark-send-as-failed, keep-alive, trailing data, suggested status default 400) | `_connection.py`, `_receive.py`, `_errors.py`; `test_default_error_status_is_400`, `test_keep_alive_two_cycles` |
| 11 Public surface inventory | N-000022–036 | implemented and tested (FP-01..FP-07 surfaces, one per feature point) | see FP-specific rows |
| 12 Non-functional constraints | N-000037–058 | implemented by design (zero deps, CPU-only, Python 3.8+ syntax, no sockets/processes, own parser/serializer, HTTP/1.1 on the wire only, no HTTP/2) | `pyproject.toml`; no `socket`/`subprocess`/`http` imports anywhere |
| 13 Non-goals | N-000059–069 | implemented as absent: no I/O, no HTTP/2, no HTTP/1.0 keep-alive, `gzip`/`deflate` refused (`test_content_length_and_transfer_encoding_normalization`), chunk extensions parsed and discarded (`test_chunked_request_and_marks`), no CLI or server | `_headers.py` (TE rule), `_receive.py` (extension regex) |
| 14 FP-01 events and headers | N-000070–121 | implemented and tested | `_events.py`, `_headers.py`; `test_request_default_version_and_bytes_storage`, `test_http11_request_requires_single_host`, `test_status_ranges_and_defaults`, `test_content_length_and_transfer_encoding_normalization`, `test_header_value_rules` |
| 15 FP-02 connection | N-000122–182 | implemented and tested | `_connection.py`, `_receive.py`; `test_request_round_trip_and_host_first`, `test_feed_then_pull_with_partial_event`, `test_lone_lf_accepted_on_receive`, `test_obsolete_folding_refused`, `test_space_first_byte_fails_immediately`, `test_feed_after_close_is_runtime_error_not_protocol`, `test_response_status_line_without_reason_accepted` |
| 16 FP-03 body framing | N-000183–246 | implemented and tested | `_connection.py` (`_serialize_response`, `_encode_data`, `_encode_end`), `_receive.py` (`_pull_body`, `_pull_trailers`); `test_content_length_body_round_trip`, `test_content_length_overrun_refused`, `test_chunked_request_and_marks`, `test_chunk_marks_single_piece_both`, `test_chunk_size_whitespace_refused_and_bad_crlf`, `test_close_mid_body_is_remote_error`, `test_http10_close_delimited_response`, `test_head_response_is_empty_body`, `test_chunked_response_for_http11_peer`, `test_passthrough_keeps_object_identity` |
| 17 FP-04 lifecycle | N-000247–289 | implemented and tested | `_connection.py` (`_transition`, `_settle`, `start_next_cycle`), `_receive.py` (`next_event` PAUSED branch); `test_keep_alive_two_cycles`, `test_connection_close_disables_keep_alive`, `test_pipelined_request_paused_until_next_cycle`, `test_send_refusal_moves_to_error_and_stays` |
| 18 FP-05 protocol errors | N-000290–331 | implemented and tested | `_errors.py`, `_receive.py` (`_remote_error`), `_connection.py` (`_fail_send`, `send_failed`), `_receive.py` (size limit, 431); `test_default_suggested_status_and_431_on_huge_head`, `test_default_error_status_is_400`, `test_remote_error_server_can_still_send_and_response_closes` |
| 19 FP-06 shutdown | N-000332–348 | implemented and tested | `_connection.py` (`ConnectionClosed` transition, `_settle`), `_receive.py` (`_emit_closed`); `test_close_handshake`, `test_send_close_in_send_response_refused` |
| 20 FP-07 informational, 100-continue, switching | N-000349–412 | implemented and tested | `_connection.py` (`_transition`: proposal flags, accept/deny, 100-continue flags), `_receive.py` (PAUSED for switch); `test_expect_100_flags`, `test_connect_accepted_with_200_switches`, `test_connect_denied_allows_next_cycle`, `test_upgrade_101_switches` |

Items that are descriptive (overview, non-goals, non-functional) are "implemented by design" as shown above. None is listed as not done.

## 4. Known gaps

- **Per-id `# spec:` markers** are not on every line; this file is the id-to-code map. Tests are named by feature point rather than the `test_AC_*` form, because the export has no acceptance criteria (`AC: 0` for all but one pack).
- **Test coverage** is 44 tests over the main behaviors. Less-exercised paths: `send_with_data_passthrough` for chunked framing, `Upgrade` denial, `CONNECT` with a 2xx other than 200 (denial), and the 431 limit for chunk-size lines.
- **No socket or I/O tests**, by design.
