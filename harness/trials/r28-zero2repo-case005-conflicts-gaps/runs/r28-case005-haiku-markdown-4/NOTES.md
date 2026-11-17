# httpwire — implementation notes

Locations: `PRD` = `spec/Full_PRD.md`, `IC` = `spec/Interface_Contract.md`, `HW` = `spec/Hardware_Requirements.md`.
Line numbers are the line numbers in those files.

**Precedence rule used throughout:** where the PRD and the Interface Contract disagree on *behaviour*
(what is accepted, refused, or defaulted), the PRD governs. Where they disagree on *shape* (names,
types, return forms), the Interface Contract governs. Every conflict below was resolved this way or by
the more specific of two statements, as noted.

## 1. Conflicts between spec parts

### C1 — maximum Content-Length digits
- PRD line 105: "Every value of at most 18 digits is accepted; the maximum digit count is … from 18 to 32 inclusive".
- IC line 46: "A `Content-Length` value longer than 16 digits is refused."
- **Built:** 18 digits (`MAX_CONTENT_LENGTH_DIGITS` in `httpwire/_events.py`). 16 is outside the PRD's allowed range and would refuse values the PRD requires to be accepted.

### C2 — default incomplete-event size limit
- PRD line 210: "The default is a fixed value … at least 14 kibibytes and less than 18 kibibytes."
- IC line 76: "When it is omitted, the limit is 8 kibibytes."
- **Built:** 16 KiB default (`DEFAULT_MAX_INCOMPLETE_EVENT_SIZE`). 8 KiB is outside the PRD's range. A caller-supplied value is used as given.

### C3 — `Expect: 100-continue` on HTTP/1.0 requests
- PRD line 249: "An `Expect: 100-continue` header on an HTTP/1.0 request does not set either flag."
- IC line 88: "any request with `Expect: 100-continue` sets it, whatever its HTTP version."
- **Built:** PRD. Only HTTP/1.1 requests set the waiting flag.

### C4 — matching of the `Expect` token
- PRD line 249: the token is matched "case-insensitively".
- IC line 89: "The `Expect` value must be exactly the lowercase token `100-continue`."
- **Built:** case-insensitive, as a whole comma-separated token.

### C5 — status line with no reason phrase
- PRD line 129: "A response status line that omits the reason phrase is accepted and the reason is empty."
- IC line 100: "A received status line with no reason phrase after its status code is illegal."
- **Built:** accepted, reason empty (`HTTP/1.1 200` and `HTTP/1.1 200 ` both work).

### C6 — line endings on received data
- PRD line 129: "Received header blocks that use a lone line feed … are accepted."
- IC line 98: "every received line must end with a carriage return and line feed".
- **Built:** lone LF is accepted in request/status lines, header blocks, trailers, and chunk-size lines. Chunk data must be followed by exactly CRLF (PRD line 168).

### C7 — control bytes in header values
- PRD line 95: values may contain "any byte other than NUL, carriage return, line feed, form feed, and vertical tab, including other control bytes".
- PRD line 102: "Control bytes other than tab are refused in header values."
- **Built:** the later and more specific statement. Bytes 0x00–0x08, 0x0A–0x1F (except HTAB) and 0x7F are refused. Non-ASCII bytes 0x80–0xFF are allowed.

### C8 — repeated `Transfer-Encoding: chunked`
- PRD line 94: "Repeated `Transfer-Encoding: chunked` headers collapse to one".
- PRD line 106: "A second `Transfer-Encoding` header is refused with suggested status 501, even when both values are `chunked`."
- **Built:** refused (501), because line 106 names this exact case. Repeated `Content-Length` values still collapse.

### C9 — obsolete line folding
- PRD line 130: continuation lines are joined to the previous header value when reading.
- PRD line 136: "A continuation line … is refused."
- **Built:** joined, per the detailed rule at line 130. Folding as the first header line is refused.

### C10 — which 2xx accepts a CONNECT
- PRD line 252: "acceptance is a final response whose status is in the 2xx range"; line 254: "a 2xx response accepts CONNECT".
- PRD line 263: "Only status 200 accepts a CONNECT proposal; other 2xx statuses deny it."
- **Built:** only 200 accepts (line 263 is the more specific statement). Other 2xx finals deny the proposal.

### C11 — framing headers on a response to HEAD
- PRD line 122: "A response to HEAD is written with no framing headers."
- PRD line 159: "A server answering HEAD writes the same framing headers it would have used for GET."
- **Built:** line 159, the body-framing section. A HEAD response gets the GET framing headers, but no body bytes are ever sent and end-of-message writes nothing.

### C12 — chunk-size digit limit
- PRD line 151: "A received size line may carry up to 64 hexadecimal digits."
- PRD line 161: "at most a fixed number of digits … from 16 to 32 inclusive".
- **Built:** 64 (`MAX_CHUNK_SIZE_DIGITS`). Line 151 is the concrete requirement on received lines.

### C13 — whitespace in a chunk-size line
- PRD line 161: the size may be "optionally followed by spaces or tabs, then the line ending".
- PRD line 168: "Whitespace after the chunk size is refused."
- **Built:** whitespace directly after the hex digits is refused. Whitespace after a chunk extension (`;…`) is allowed.

### C14 — whether the client's body clears the 100-continue wait
- PRD line 248: "The client stays waiting for 100-continue until the server answers; its own body events do not end the wait."
- PRD line 250: the flags turn off "when the client sends any data event or its end-of-message."
- **Built:** line 250, the explicit list of turn-off events. Sending any Data or EndOfMessage on the client clears `client_is_waiting_for_100_continue`.

### C15 — `Content-Length: 0` on a response
- PRD line 152: "The `Content-Length` header is kept on the wire, including when N is 0."
- PRD line 158: "A response with `Content-Length: 0` is sent without that header, since its body is empty."
- **Built:** line 152 for ordinary responses. Line 158 applies only to the empty-body situations it lists (HEAD, 204, 304), where a zero Content-Length is dropped.

## 2. Assumptions (not stated in the spec)

- **Response with neither framing header from an HTTP/1.1 peer:** treated as close-delimited (RFC 7230 §3.3.3 rule 7). The spec only defines the HTTP/1.0 case (PRD line 157). Such a response also disables keep-alive.
- **Request with both Content-Length and Transfer-Encoding:** Content-Length decides the framing (PRD line 94). Transfer-Encoding is not written on the wire. For responses, Transfer-Encoding wins (PRD line 156).
- **Unsupported HTTP version when reading** (anything other than 1.0 or 1.1): RemoteProtocolError with suggested status 400, not 505.
- **Reason phrase validation:** the spec gives no rule. Tab, space, visible ASCII, and non-ASCII bytes are accepted. Other controls (including CR and LF) are refused.
- **Written status line with an empty reason:** `HTTP/1.1 200 \r\n` (with the trailing space), so the format is always `HTTP/1.1 <code> <reason>`.
- **Headers httpwire adds on the wire:** `Connection` (when keep-alive is disabled), `Transfer-Encoding: chunked`. They are written with those canonical capitalisations.
- **Keep-alive is disabled** by any HTTP/1.0 message or `Connection: close` in the cycle, by a close-delimited body, or by a remote protocol error. When disabled, the response we send gets `Connection: close` and has any `keep-alive` token removed (PRD lines 181–182).
- **Responses that accept a switch** (200 for CONNECT, 101 for Upgrade) get no framing headers and no body. Connection is not rewritten for them.
- **Trailing headers on an end-of-message** are validated like other headers. They are refused with Content-Length, close-delimited, and empty framings (PRD line 166).
- **Data sent on an empty-body response** (HEAD, 204, 304) is accepted and silently produces no bytes (PRD line 158, "No data is sent"). Data on a request without framing is refused, because such a request is equivalent to Content-Length 0 (PRD line 149).
- **Data payload types:** `send()` requires bytes-like payloads. A non-bytes-like payload is a LocalProtocolError, which also moves our side to ERROR. `send_with_data_passthrough()` accepts any object with `len()`.
- **Incomplete-event size limit:** applies to the request/status line plus header block, and also to chunked trailer blocks. It does not apply to chunk-size lines or body bytes. An unfinished chunk-size line has no length cap, only the 64-digit cap.
- **Leading CR/LF before a request line** is a remote error (the first byte is a control byte, PRD line 137). Leading blank lines are not skipped.
- **Remote protocol errors** that come from pulled bytes are reported with the suggested status from the rule that failed (400 by default; 501 for Transfer-Encoding; 431 for the size limit).
- **Refused-send state rule:** every send refused as a LocalProtocolError moves our side to ERROR (PRD line 207), including a second request on a client and sends in MIGHT_SWITCH_PROTOCOL.
- **Feeding bytes after the peer closed** raises `RuntimeError` (IC line 64 leaves the class open).
- **`send()` given something that is not an event** raises `TypeError` and changes no state.
- **Event equality:** events compare equal by type and fields, and `Headers` compares by its ordinary (lowercased) view. The spec does not require this, but it makes tests and comparisons convenient.
- **`their_http_version`** is set when a request or response is pulled, and reset by `start_next_cycle()`. It is `None` until recorded.
- **`states`** returns a fresh `dict` keyed by `CLIENT` and `SERVER`.
- **Import path:** `httpwire/` is a flat package at `/app`. `conftest.py` at the root is empty; it only makes pytest put `/app` on `sys.path`. `pyproject.toml` is provided for setuptools, but no build is run (HW line 20; the judge runs no build step).
- **Tests:** `tests/test_httpwire.py` contains 69 behavioural tests written from the spec (run with `python3 -m pytest -q` from `/app`). They are not the hidden acceptance tests.
