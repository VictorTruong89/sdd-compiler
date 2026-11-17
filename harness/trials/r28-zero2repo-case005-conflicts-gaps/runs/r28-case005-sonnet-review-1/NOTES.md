# NOTES

Package: `httpwire/` (flat layout; code in `httpwire/_core.py`). No build step.

## Conflicts between spec files and what was built

1. **Max Content-Length digits.** PRD FP-01 (line 105): at most 18 digits accepted, limit 18–32. Contract (Events): longer than 16 refused. Built: limit 18 (PRD); 17/18 digits accepted, 19+ refused.
2. **Default incomplete-event limit.** PRD FP-05: 14 to <18 KiB. Contract (Connection signature): 8 KiB. Built: 16 KiB (PRD).
3. **Hex digits in chunk-size line.** PRD FP-03 says "up to 64" in one bullet, 16–32 max with refusal beyond in another. Built: max 32 digits, more refused.
4. **Whitespace after chunk size.** PRD normal behaviour: spaces/tabs allowed; Boundary: refused. Built: allowed.
5. **Lone LF line endings.** PRD FP-02: accepted. Contract `receive_data`: every line must end CRLF. Built: lone LF accepted in header blocks (chunk-size lines and chunk terminators still need CRLF).
6. **Status line without reason.** PRD: accepted, reason empty. Contract `next_event`: illegal. Built: accepted.
7. **Obsolete line folding.** PRD normal: joined with a single space. PRD boundary: continuation refused. Built: joined (a fold at the very start of the headers is refused).
8. **Control bytes in header values.** PRD FP-01 normal: anything except NUL, CR, LF, FF, VT allowed. PRD boundary: control bytes other than tab refused. Built: allowed per the normal rule; leading/trailing space or tab refused.
9. **Framing headers on HEAD response.** PRD FP-02: none. PRD FP-03: same as GET (chunked for 1.1 peer). Built: same as GET.
10. **Content-Length: 0 on response.** FP-03 line 152 keeps it; line 158 omits it. Built: kept.
11. **Both CL and TE.** FP-01 says Content-Length decides; FP-03 says TE wins, CL not sent. Built: TE wins (response: Content-Length removed). Note FP-01 also says a second Transfer-Encoding header collapses, while its boundary section refuses it with 501; built: refused (501).
12. **Case of `100-continue`.** PRD: case-insensitive; Contract: exact lowercase. Built: case-insensitive.
13. **HTTP/1.0 request with Expect.** PRD: flags not set; Contract: set for any version. Built: not set for 1.0.
14. **Client body ends 100-continue wait?** FP-07 line 248 says no; line 250 says data/EOM clears it. Built: cleared by client Data/EndOfMessage.
15. **Which 2xx accepts CONNECT.** Built: any 2xx accepts.
16. **Feeding after close in switched state.** Built: non-empty feed after an empty feed always raises `RuntimeError`.

## Unstated items / assumptions

- Header-name case in headers the library adds (`Transfer-Encoding`, `Connection`): written Title-Case.
- Missing/unknown constructor keywords on events raise `LocalProtocolError`.
- `send` of an event producing no bytes returns `b""`; `send_with_data_passthrough` returns `[]`.
- `states` is a dict keyed by CLIENT/SERVER.
- Bytes after a chunk's data must be exactly CRLF (checked, unlike a plain discard).
- After a remote error, a server response gets `Connection: close` (their side is ERROR).
- Event `http_version` format is not validated at construction; only version `1.1` can be sent.
- A bad `role` raises `ValueError`.
