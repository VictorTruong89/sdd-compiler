# httpwire — build notes

Implementation of the spec in `spec/` (export `spec/MAP.md`, checklist `spec/CHECKLIST.md`).
Layout: `httpwire/` is the importable package (flat layout at the repo root, `pyproject.toml`
for setuptools, zero runtime dependencies). Tests: `tests/test_httpwire.py` (run with `pytest`).
Code is marked `# spec: <id>` next to what satisfies an id.

The export was made with `--allow-open`, so 19 contradictions are unsettled. Each one is
listed below with both sides, where each side is, and what was built. Where the spec does
not say something the code needs, that is listed under "Gaps and assumptions".

## Contradictions (19, all unsettled in the export)

Rule used for every pick: the more specific statement wins over a general one, and
where two statements are equally specific the one that matches RFC 7230/7231 behaviour
is chosen. Each pick is stated below.

1. **CF-000003: framing when both Content-Length and Transfer-Encoding are present.**
   - PRD FP-01, `spec/packs/14-…` normal behaviour: "When an event carries both framing headers, the `Content-Length` decides how the body is framed."
   - PRD FP-03, `spec/packs/16-…`: "If a response is constructed with both `Transfer-Encoding: chunked` and `Content-Length`, transfer-encoding wins."
   - **Built:** both. Pulled messages and requests use Content-Length (FP-01). A response we construct with both: Transfer-Encoding wins and Content-Length is not sent (FP-03 is the more specific rule for responses).

2. **CF-000005: response status line with no reason phrase.**
   - PRD FP-02, `spec/packs/15-…`: "A response status line that omits the reason phrase is accepted and the reason is empty."
   - Interface `next_event`, `spec/packs/08-…`: "A received status line with no reason phrase after its status code is illegal."
   - **Built:** accepted, reason empty (the PRD's normal-behaviour sentence is the explicit one).

3. **CF-000026: control bytes in header values.**
   - PRD FP-01 normal behaviour, `spec/packs/14-…`: values may contain "other control bytes and non-ASCII bytes".
   - PRD FP-01 boundary, same pack: "Control bytes other than tab are refused in header values."
   - **Built:** control bytes (0x00–0x1F except tab, and 0x7F) are refused; non-ASCII bytes are allowed. This matches RFC 7230 field-content.

4. **CF-000048: default incomplete-event size limit.**
   - PRD FP-05, `spec/packs/18-…`: "at least 14 kibibytes and less than 18 kibibytes".
   - Interface `Connection`, `spec/packs/08-…`: "When it is omitted, the limit is 8 kibibytes."
   - **Built:** 16 KiB. It is the only value that satisfies the PRD range, and the 8 KiB figure is outside it. The explicit constructor argument still overrides it.

5. **CF-000050: framing headers on a response to HEAD.**
   - PRD FP-02, `spec/packs/15-…`: "A response to HEAD is written with no framing headers."
   - PRD FP-03, `spec/packs/16-…`: "A server answering HEAD writes the same framing headers it would have used for GET."
   - **Built:** the FP-03 rule (same framing headers as GET, chunked for a 1.1 peer, close-delimited for a 1.0 peer). No body bytes and no chunk terminator are emitted for HEAD.

6. **CF-000074: lone LF line endings.**
   - PRD FP-02, `spec/packs/15-…`: received header blocks with lone LF line endings "are accepted".
   - Interface `receive_data`, `spec/packs/08-…`: "every received line must end with a carriage return and line feed".
   - **Built:** lone LF is accepted in header blocks and chunk-size lines (the PRD's explicit leniency). Chunk data terminators must be exactly CRLF (FP-03).

7. **CF-000075 / CF-000076 / CF-000100: obsolete line folding.**
   - PRD FP-02, `spec/packs/15-…` normal behaviour: folding "is accepted when reading headers", continuation joined with one space.
   - PRD FP-02, same pack, boundary: "A continuation line … is refused."
   - **Built:** folding is accepted and joined (the explicit normal-behaviour rule). A continuation line with no previous header is refused.

8. **CF-000083: `Expect: 100-continue` on an HTTP/1.0 request.**
   - PRD FP-07, `spec/packs/20-…`: an Expect header "on an HTTP/1.0 request does not set either flag".
   - Interface `client_is_waiting_for_100_continue`, `spec/packs/08-…`: "any request with `Expect: 100-continue` sets it, whatever its HTTP version."
   - **Built:** HTTP/1.0 sets neither flag (the PRD names this exact case).

9. **CF-000098: Content-Length digit limit.**
   - PRD FP-01, `spec/packs/14-…`: "the maximum digit count is a fixed number of the implementer's choice, from 18 to 32 inclusive". Also "Every value of at most 18 digits is accepted."
   - Interface Event table, `spec/packs/06-…`: "A `Content-Length` value longer than 16 digits is refused."
   - **Built:** 18 digits. 16 is outside the PRD's 18–32 range.

10. **CF-000099: chunk-size hexadecimal digit limit.**
    - PRD FP-03, `spec/packs/16-…` framing bullet: a received size line "may carry up to 64 hexadecimal digits".
    - PRD FP-03, same pack, chunk-size bullet: "a fixed number of the implementer's choice, from 16 to 32 inclusive".
    - **Built:** 32 digits. The 64 figure is in a framing bullet, the 16–32 range is the stated rule for the chunk-size line.

11. **CF-000101: whitespace after the chunk size.**
    - PRD FP-03, `spec/packs/16-…`: the size line is "optionally followed by spaces or tabs, then the line ending".
    - PRD FP-03, same pack, boundary: "Whitespace after the chunk size is refused."
    - **Built:** spaces and tabs before the line ending are accepted (the chunk-size definition is the rule that describes the line itself).

12. **CF-000102: Content-Length: 0 on a response.**
    - PRD FP-03, `spec/packs/16-…`: the header is kept "including when N is 0".
    - PRD FP-03, same pack, empty-body bullet: "A response with `Content-Length: 0` is sent without that header."
    - **Built:** kept on the wire. The first is the direct framing rule for Content-Length responses; the second sits in the empty-body bullet.

13. **CF-000103: which Connection values turn keep-alive off.**
    - PRD glossary, `spec/packs/10-…`: "Any `Connection` value that contains `close` turns it off."
    - PRD FP-04, `spec/packs/17-…`: `close` must be "a whole element of the comma-separated `Connection` value".
    - **Built:** whole-element, case-insensitive matching (the FP-04 feature-point rule). `closed-later` does not disable keep-alive.

14. **CF-000104: case of the `Expect` token.**
    - PRD FP-07, `spec/packs/20-…`: `100-continue` "matched case-insensitively".
    - Interface `they_are_waiting_for_100_continue`, `spec/packs/08-…`: "must be exactly the lowercase token".
    - **Built:** case-insensitive, consistent with the HTTP token rule used for `Connection`.

15. **CF-000105: whether a client's body events end the 100-continue wait.**
    - PRD FP-07, `spec/packs/20-…` normal behaviour: "its own body events do not end the wait".
    - PRD FP-07, same pack, flag rules: the flags turn off "when the client sends any data event or its end-of-message".
    - **Built:** the explicit flag-off rule. Client Data and EndOfMessage clear the flag on both connection objects.

16. **CF-000106: which 2xx answers accept CONNECT.**
    - PRD FP-07, `spec/packs/20-…`: acceptance is "a final response whose status is in the 2xx range" (stated several times).
    - PRD FP-07, same pack, boundary: "Only status 200 accepts a CONNECT proposal; other 2xx statuses deny it."
    - **Built:** any 2xx accepts CONNECT. The 2xx rule is restated across the feature point, and it matches RFC 7231.

17. **CF-000107: repeated `Transfer-Encoding: chunked` headers.**
    - PRD FP-01, `spec/packs/14-…`: "Repeated `Transfer-Encoding: chunked` headers collapse to one".
    - PRD FP-01, same pack, boundary: a second Transfer-Encoding header "is refused with suggested status 501, even when both values are `chunked`" (also repeated in FP-05).
    - **Built:** refused with status 501. The "even when both values are chunked" sentence addresses this exact case.

19 ids in total: CF-000003 (1), 005 (2), 026 (3), 048 (4), 050 (5), 074 (6), 075/076/100 (7), 083 (8), 098 (9), 099 (10), 101 (11), 102 (12), 103 (13), 104 (14), 105 (15), 106 (16), 107 (17).

## Gaps and assumptions (not stated in the spec)

- **Invalid role** to `Connection(...)`: raises `LocalProtocolError` (the spec says "an exception"). A non-positive or non-int size limit raises `ValueError`.
- **Refused sends** (any `LocalProtocolError` from `send`, including ConnectionClosed in a bad state) set our side to ERROR, per FP-05. A refused `start_next_cycle` changes nothing, per FP-04.
- **`send()` of a non-bytes-like Data payload** raises `TypeError` before any state change. Only `send_with_data_passthrough` accepts such objects. A payload with `__len__` counts that many body bytes.
- **Data in an empty-body message** (HEAD, 204, 304, or a Content-Length: 0 request) is refused as exceeding a zero-length body; a zero-length Data event is a no-op.
- **Empty-body responses (HEAD, 204, 304)**: the framing headers are chosen exactly as for GET, but no body and no chunk terminator are written. The client side does not read a body for these.
- **Response framing** (server role): Content-Length kept if given; otherwise chunked for a 1.1 peer; otherwise close-delimited with `Connection: close`. "No request seen" counts as an unknown (close-delimited) peer.
- **Keep-alive rewriting**: when keep-alive is disabled the server response's Connection header is rewritten to include `close` and any `keep-alive` token is dropped. A remote protocol error also forces `Connection: close` on the next response, since the peer can no longer be kept alive (FP-05, N-000305–N-000306).
- **Request with both framing headers** (sent or pulled): framed by Content-Length; both headers are written as given.
- **Close-delimited responses from 1.1 peers** (neither framing header) are treated the same way as 1.0 peers and force `MUST_CLOSE`.
- **Reason phrase on the wire**: `HTTP/1.1 <code> <reason>\r\n` with an empty reason gives `HTTP/1.1 200 \r\n`.
- **Chunk-size line** is limited to 32 hex digits, also when the line is not yet complete. Chunk extensions are parsed and discarded.
- **Incomplete-event limit** applies to the start line plus header block and to a trailer block; body bytes never count. A limit breach is a remote error with status 431.
- **Trailers** to an HTTP/1.0 peer are refused (FP-03), and are refused for Content-Length and close-delimited framing.
- **Paused vs. closed**: with leftover bytes, a peer in DONE or MUST_CLOSE gives PAUSED, not ConnectionClosed, and the close is held (FP-04, FP-07).
- **Switch proposals**: a request proposes a switch if its method is CONNECT or it has an Upgrade header. The client moves to MIGHT_SWITCH_PROTOCOL after its end-of-message; a final denial moves the client to DONE.
- **`states`** is a tuple (client, server) that also supports lookup by role (`states[CLIENT]`), by 0/1, and `keys()/items()/values()/get()`, plus equality with a dict keyed by role.
- **`ReceiveClosedError`** (in `httpwire._errors`) is the runtime error for bytes fed after an empty feed. It is not exported at the package root.
- **Python**: written for 3.8+ (no `match`, no 3.9+ generics). Only Python 3.13 was available here, and the test suite was run on it only.
- **Hidden tests**: no acceptance-criteria labels exist in this export (AC count 0), so tests are named after the spec ids they check, in `tests/test_httpwire.py`.

## Traceability

Every checklist id is listed below as **implemented** (with its location) or **not done** (with the reason). The location is the module that holds the behaviour; `tests/test_httpwire.py` exercises the feature point as a whole and names tests after the ids they check. The ids are generated from `spec/CHECKLIST.md`.

### Pack 01 — 0 ids

- **Implemented** at httpwire/_constants.py (no-I/O by construction): none


### Pack 02 — 5 ids

- **Implemented** at pyproject.toml (zero dependencies); httpwire/ (pure Python): N-000413, N-000414, N-000415, N-000416, N-000417


### Pack 03 — 11 ids

- **Implemented** at pyproject.toml (flat layout, setuptools); httpwire/ (CPU only): N-000418, N-000419, N-000420, N-000421, N-000422, N-000423, N-000424, N-000425, N-000426, N-000427, N-000428


### Pack 04 — 4 ids

- **Implemented** at httpwire/__init__.py (library, no CLI, no config): N-000429, N-000430, N-000431, N-000432


### Pack 05 — 17 ids

- **Implemented** at httpwire/__init__.py, httpwire/_constants.py: N-000433, N-000434, N-000435, N-000436, N-000437, N-000438, N-000439, N-000440, N-000441, N-000442, N-000443, N-000444, N-000445, N-000446, N-000447, N-000448, N-000449


### Pack 06 — 22 ids

- **Implemented** at httpwire/_events.py: N-000450, N-000451, N-000452, N-000453, N-000454, N-000455, N-000456, N-000457, N-000458, N-000459, N-000460, N-000461, N-000463, N-000464, N-000465, N-000466, N-000467, N-000468, N-000469, N-000470, N-000471

- **Not done** `N-000462`: superseded by CF-000098 (18-digit limit, N-000116)

### Pack 07 — 4 ids

- **Implemented** at httpwire/_errors.py: N-000472, N-000473, N-000474, N-000475


### Pack 08 — 47 ids

- **Implemented** at httpwire/_connection.py, httpwire/_wire.py: N-000476, N-000477, N-000478, N-000480, N-000481, N-000482, N-000483, N-000484, N-000485, N-000486, N-000487, N-000488, N-000489, N-000490, N-000492, N-000494, N-000495, N-000496, N-000497, N-000498, N-000499, N-000500, N-000501, N-000502, N-000503, N-000504, N-000505, N-000506, N-000507, N-000508, N-000509, N-000511, N-000512, N-000513, N-000514, N-000515, N-000517, N-000518, N-000519, N-000520, N-000521, N-000522

- **Not done** `N-000479`: superseded by CF-000048 (16 KiB default, N-000317)
- **Not done** `N-000491`: HTTP/1.0 part superseded by CF-000083 (N-000357); 1.1 part implemented
- **Not done** `N-000493`: superseded by CF-000104 (case-insensitive Expect token, N-000354)
- **Not done** `N-000510`: superseded by CF-000074 (lone LF accepted, N-000165)
- **Not done** `N-000516`: superseded by CF-000005 (reason-less status line accepted, N-000166)

### Pack 09 — 9 ids

- **Implemented** at httpwire/_connection.py (no I/O), whole package: N-000001, N-000002, N-000003, N-000004, N-000005, N-000006, N-000007, N-000008, N-000009


### Pack 10 — 12 ids

- **Implemented** at httpwire/_connection.py: N-000010, N-000011, N-000012, N-000013, N-000014, N-000015, N-000016, N-000017, N-000018, N-000019, N-000020

- **Not done** `N-000021`: superseded by CF-000103 (whole-element Connection token, N-000262)

### Pack 11 — 15 ids

- **Implemented** at httpwire/__init__.py, httpwire/_events.py, httpwire/_connection.py: N-000022, N-000023, N-000024, N-000025, N-000026, N-000027, N-000028, N-000029, N-000030, N-000031, N-000032, N-000033, N-000034, N-000035, N-000036


### Pack 12 — 22 ids

- **Implemented** at pyproject.toml, httpwire/ (no I/O, no sockets, HTTP/1.1 only on the wire): N-000037, N-000038, N-000039, N-000040, N-000041, N-000042, N-000043, N-000044, N-000045, N-000046, N-000047, N-000048, N-000049, N-000050, N-000051, N-000052, N-000053, N-000054, N-000055, N-000056, N-000057, N-000058


### Pack 13 — 11 ids

- **Implemented** at httpwire/_events.py (gzip/deflate refused), httpwire/_wire.py (extensions discarded): N-000059, N-000060, N-000061, N-000062, N-000063, N-000064, N-000065, N-000066, N-000067, N-000068, N-000069


### Pack 14 — 52 ids

- **Implemented** at httpwire/_events.py: N-000070, N-000071, N-000072, N-000073, N-000074, N-000075, N-000076, N-000077, N-000078, N-000079, N-000080, N-000081, N-000082, N-000083, N-000084, N-000085, N-000086, N-000087, N-000088, N-000089, N-000090, N-000091, N-000092, N-000094, N-000095, N-000096, N-000098, N-000099, N-000100, N-000101, N-000102, N-000103, N-000104, N-000105, N-000106, N-000107, N-000108, N-000109, N-000110, N-000111, N-000112, N-000113, N-000114, N-000115, N-000116, N-000117, N-000118, N-000119, N-000120, N-000121

- **Not done** `N-000093`: superseded by CF-000107 (second chunked TE refused with 501, N-000121)
- **Not done** `N-000097`: control-byte part superseded by CF-000026 (N-000108); other rules implemented

### Pack 15 — 61 ids

- **Implemented** at httpwire/_connection.py, httpwire/_wire.py: N-000122, N-000123, N-000124, N-000125, N-000126, N-000127, N-000128, N-000129, N-000130, N-000131, N-000132, N-000133, N-000134, N-000135, N-000136, N-000138, N-000139, N-000140, N-000141, N-000142, N-000143, N-000144, N-000145, N-000146, N-000147, N-000148, N-000149, N-000150, N-000151, N-000152, N-000153, N-000154, N-000155, N-000156, N-000157, N-000158, N-000159, N-000160, N-000161, N-000162, N-000163, N-000164, N-000165, N-000166, N-000167, N-000168, N-000169, N-000170, N-000171, N-000172, N-000173, N-000174, N-000175, N-000177, N-000178, N-000179, N-000180, N-000181, N-000182

- **Not done** `N-000137`: superseded by CF-000050 (HEAD framing per N-000219)
- **Not done** `N-000176`: continuation-line refusal superseded by CF-000075/076/100 (folding accepted, N-000167..N-000169)

### Pack 16 — 64 ids

- **Implemented** at httpwire/_connection.py (framing), httpwire/_events.py (CL/TE normalization): N-000183, N-000184, N-000185, N-000186, N-000187, N-000188, N-000189, N-000190, N-000191, N-000192, N-000193, N-000195, N-000196, N-000197, N-000198, N-000199, N-000200, N-000201, N-000202, N-000203, N-000204, N-000205, N-000206, N-000207, N-000208, N-000209, N-000210, N-000211, N-000212, N-000213, N-000214, N-000215, N-000216, N-000217, N-000219, N-000220, N-000221, N-000222, N-000223, N-000224, N-000225, N-000226, N-000227, N-000228, N-000229, N-000230, N-000231, N-000232, N-000233, N-000234, N-000235, N-000236, N-000237, N-000238, N-000239, N-000240, N-000241, N-000242, N-000244, N-000245, N-000246

- **Not done** `N-000194`: 64-digit size line superseded by CF-000099 (32 digits, N-000228)
- **Not done** `N-000218`: superseded by CF-000102 (Content-Length: 0 kept, N-000199)
- **Not done** `N-000243`: superseded by CF-000101 (trailing whitespace allowed, N-000230)

### Pack 17 — 43 ids

- **Implemented** at httpwire/_connection.py (keep-alive, pipelining, cycle): N-000247, N-000248, N-000249, N-000250, N-000251, N-000252, N-000253, N-000254, N-000255, N-000256, N-000257, N-000258, N-000259, N-000260, N-000261, N-000262, N-000263, N-000264, N-000265, N-000266, N-000267, N-000268, N-000269, N-000270, N-000271, N-000272, N-000273, N-000274, N-000275, N-000276, N-000277, N-000278, N-000279, N-000280, N-000281, N-000282, N-000283, N-000284, N-000285, N-000286, N-000287, N-000288, N-000289


### Pack 18 — 42 ids

- **Implemented** at httpwire/_connection.py, httpwire/_errors.py: N-000290, N-000291, N-000292, N-000293, N-000294, N-000295, N-000296, N-000297, N-000298, N-000299, N-000300, N-000301, N-000302, N-000303, N-000304, N-000305, N-000306, N-000307, N-000308, N-000309, N-000310, N-000311, N-000312, N-000313, N-000314, N-000315, N-000316, N-000317, N-000318, N-000319, N-000320, N-000321, N-000322, N-000323, N-000324, N-000325, N-000326, N-000327, N-000328, N-000329, N-000330, N-000331


### Pack 19 — 17 ids

- **Implemented** at httpwire/_connection.py (shutdown): N-000332, N-000333, N-000334, N-000335, N-000336, N-000337, N-000338, N-000339, N-000340, N-000341, N-000342, N-000343, N-000344, N-000345, N-000346, N-000347, N-000348


### Pack 20 — 64 ids

- **Implemented** at httpwire/_connection.py (100-continue, switching, trailing data): N-000349, N-000350, N-000351, N-000352, N-000354, N-000355, N-000356, N-000357, N-000358, N-000359, N-000360, N-000361, N-000362, N-000363, N-000364, N-000365, N-000366, N-000367, N-000368, N-000369, N-000370, N-000371, N-000372, N-000373, N-000374, N-000375, N-000376, N-000377, N-000378, N-000379, N-000380, N-000381, N-000382, N-000383, N-000384, N-000385, N-000386, N-000387, N-000388, N-000389, N-000390, N-000391, N-000392, N-000393, N-000394, N-000395, N-000397, N-000398, N-000399, N-000400, N-000401, N-000402, N-000403, N-000404, N-000405, N-000406, N-000407, N-000408, N-000409, N-000410, N-000411, N-000412

- **Not done** `N-000353`: superseded by CF-000105 (N-000359 flag-off rule)
- **Not done** `N-000396`: superseded by CF-000106 (any 2xx accepts CONNECT, N-000364)

