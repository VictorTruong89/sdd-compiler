# Answer key: 17 conflicts and 11 gaps planted in case005, round 28 (never shown to an agent)

> Written 2026-11-11, after the step-1 checks and before any compile, review or agent run. The planted
> Markdown is made by `notes/plant.py work/spec-planted` with the 28 kept ids (`KEPT_C`, `KEPT_G` in
> the script) from Zero2Repo case005's `public/` (`httpwire`, upstream `h11`); it stays in git-ignored
> `work/` (Zero2Repo has no licence file). 7 916 words (7 915 before). sha256 of the planted files
> (`work/spec-planted.sha256`): `Full_PRD.md` `e3be00f43856d7b8…`, `Interface_Contract.md`
> `0d322a35cd35cd10…`, `Hardware_Requirements.md` `33735a6f591ee082…` (unchanged). Only short phrases are
> quoted here.

Side **A** is the text the case already had: the reference library's behaviour and what the hidden
tests check. Side **B** is the planted sentence: one place edited, in the spec's voice, no marker. A
**gap** removes every statement of a fact the hidden tests still check. Lines are those of the planted
files (PRD = `Full_PRD.md`, Contract = `Interface_Contract.md`).

## Conflicts (17)

| Item | Distance | A (kept) | B (planted) | Footprint |
|---|---|---|---|---|
| C01 | across files | PRD 105: Content-Length "Every value of at most 18 digits is accepted" (maximum 18–32) | Contract 46: "longer than 16 digits is refused" | 3 |
| C02 | same file | PRD 161: chunk-size digits, a maximum "from 16 to 32 inclusive" | PRD 151: "A received size line may carry up to 64 hexadecimal digits" | 2 |
| C03 | across files | PRD 210: default limit "at least 14 kibibytes and less than 18 kibibytes" | Contract 76: "When it is omitted, the limit is 8 kibibytes" | 2 |
| C04 | same file | PRD 130: "Obsolete line folding (RFC 7230 §3.2.4) is accepted" when reading | PRD 136: "A continuation line (a header line that begins with a space or tab) is refused" | 2 |
| C05 | across files | PRD 129: header blocks that "use a lone line feed" (or a mix) are accepted | Contract 98: "every received line must end with a carriage return and line feed" | 3 |
| C06 | across files | PRD 129: a status line that "omits the reason phrase is accepted" | Contract 100: a status line "with no reason phrase after its status code is illegal" | 1 |
| C09 | same file | PRD 161: chunk size "optionally followed by spaces or tabs" | PRD 168: "Whitespace after the chunk size is refused" | 2 |
| C10 | same file, far | PRD 156: response with both headers, "transfer-encoding wins" | PRD 94: "the `Content-Length` decides how the body is framed" | 3 |
| C11 | same file | PRD 152: Content-Length kept on the wire, "including when N is 0" | PRD 158: a `Content-Length: 0` response "is sent without that header" | 1 |
| C12 | same file, far | PRD 181: `close` matched "as a whole element of the comma-separated `Connection` value" | PRD 36 (Terminology): "Any `Connection` value that contains `close` turns it off" | 2 |
| C13 | across files | PRD 249: `Expect: 100-continue` "on an HTTP/1.0 request does not set either flag" | Contract 88: "`Expect: 100-continue` sets it, whatever its HTTP version" | 2 |
| C14 | across files | PRD 249: "contains the token `100-continue` (matched case-insensitively)" | Contract 89: "must be exactly the lowercase token `100-continue`" | 2 |
| C15 | same file | PRD 250: the flags turn off "when the client sends any data event or its end-of-message" | PRD 248: the client stays waiting; "its own body events do not end the wait" | 3 |
| C16 | same file | PRD 252: CONNECT accepted by a final response "whose status is in the 2xx range" (also PRD 254) | PRD 263: "Only status 200 accepts a CONNECT proposal" | 2 |
| C18 | same file | PRD 106: a second Transfer-Encoding "is refused with suggested status 501, even when both values are `chunked`" (also PRD 203) | PRD 94: "Repeated `Transfer-Encoding: chunked` headers collapse to one" | 2 |
| C20 | same file | PRD 95: header values may hold any byte but NUL, CR, LF, FF, VT, "including other control bytes and non-ASCII bytes" | PRD 102: "Control bytes other than tab are refused in header values" | 2 |
| C21 | same file | PRD 159: a server answering HEAD "writes the same framing headers it would have used for GET" | PRD 122: "A response to HEAD is written with no framing headers" | 1 |

## Gaps (11)

| Item | Fact removed (upstream value) | Removed from | Alternative probed | Footprint |
|---|---|---|---|---|
| G06 | bytes held while a pull is paused do not count against the incomplete-event limit until a later cycle parses them | PRD FP-05 (limit bullet, last sentence) | counted at once (431 while paused) | 2 |
| G09 | an empty data event on a chunked body encodes as no bytes | PRD FP-03 (chunked bullet) | encoded as a zero-size chunk | 2 |
| G14 | feeding further empty chunks after the close never fails | PRD FP-02 boundary; FP-06 (close bullet) | a second empty chunk raises | 2 |
| G16 | the peer HTTP version stays after the next cycle starts | PRD FP-02 (last bullet; "for the rest of this connection" also cut); FP-04 (next-cycle bullet) | reset at the next cycle | 2 |
| G21 | the product never invents a reason phrase; an empty reason is written when none is supplied | PRD Non-goals (reason-phrase table bullet); FP-01 (status bullet); FP-02 (status-line bullet) | a standard phrase written (`200 OK`) | 3 |
| G22 | bytes from a peer in MUST_CLOSE are a remote protocol error | PRD FP-06 boundary | held (pull returns paused) | 3 |
| G33 | marking a send as failed twice has the same result | PRD FP-05 (mark-send bullet) | the second call is refused | 1 |
| G34 | connection-closed may be sent again when already CLOSED (idempotent) | PRD FP-06 ("or CLOSED" and the idempotent sentence) | the second send is refused | 2 |
| G47 | header order is kept as the caller gave it at construction | PRD FP-01 (headers bullet) | Host moved first at construction | 3 |
| G48 | whitespace around the commas of a Content-Length list is allowed | PRD FP-01 (normalization bullet) | `0, 0` refused | 3 |
| G49 | an integer-valued enumeration status is stored as a plain `int` | PRD FP-01 (status bullet); Contract (`status_code` bullet, "The stored value is exactly of type `int`") | stored as given (the enum member) | 2 |

**Still implied, recorded before any run.** G14: the Contract's `receive_data` says it raises "when a
non-empty chunk follows an empty one", which implies an empty one does not; kept (no sentence states
it). G06: "The limit applies only while a pull cannot complete the current event because a … line, or
its header block, is unfinished" can be read either way while paused; kept.

**Footprint union: 60 tests, none shared by two items; the base build fails none.** The **core** (set 1)
is the other **335** tests. Distances: same file 11 (C02, C04, C09, C10, C11, C12, C15, C16, C18, C20,
C21; C10 and C12 far apart), across files 6 (C01, C03, C05, C06, C13, C14).

## Candidates tried and dropped (step 1, no model call)

| Item | Behaviour | Why dropped |
|---|---|---|
| C07 | Host written first when encoding | shares `host_is_written_before_foo_even_when_not_first` with C08 and G47 (G47 kept) |
| C08 | raw name casing written | the same shared test |
| C17 | 431 for an oversize incomplete event | footprint 11 |
| C19 | a server may send a final response from IDLE | footprint 9 |
| G01 | default suggested status 400 | footprint 27 |
| G03 | HTTP/1.0 `Connection: keep-alive` not honoured | still stated ("only when both sides speak HTTP/1.1"; "An HTTP/1.0 peer cannot be kept alive") |
| G05 | a control byte where a start line is expected fails at once | footprint 5 |
| G07 | framed body bytes never count against the limit | still stated ("applies only while … line, or its header block, is unfinished") |
| G08 | the whole unfinished head counts, not one value | still stated ("the stored unparsed bytes") |
| G31 | the added `Connection: close` drops a `keep-alive` token | footprint 0 |

## How each side is read (`notes/probe.py`, black box, from this key and the Contract only)

One probe per item on the saved code, in a container with no network (`notes/probe.sh`). Check
(`work/probe_check.log`): the base reads A on all 38 candidates; each alternative copy reads B on its own
item and A on the other 37 (0 mismatches).
