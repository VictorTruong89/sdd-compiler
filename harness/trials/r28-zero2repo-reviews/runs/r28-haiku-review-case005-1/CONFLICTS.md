# Specification conflicts

Each entry is a pair of statements inside `spec/` that cannot both hold for the same case. Line numbers refer to the files as they are now.

## 1. Maximum Content-Length digits

- **Full_PRD.md, FP-01, Boundary (line 105):** "Every value of at most 18 digits is accepted; the maximum digit count is a fixed number of the implementer's choice, from 18 to 32 inclusive."
- **Interface_Contract.md, Events (line 46):** "A `Content-Length` value longer than 16 digits is refused."

Both cannot hold: a 17- or 18-digit Content-Length must be accepted by the PRD's "at most 18 digits" rule but refused by the contract's 16-digit limit.

## 2. Default incomplete-event size limit

- **Full_PRD.md, FP-05, Normal behavior (line 210):** the default is "at least 14 kibibytes and less than 18 kibibytes."
- **Interface_Contract.md, `Connection`, Signature (line 76):** "When it is omitted, the limit is 8 kibibytes."

Both cannot hold: 8 KiB is below the 14 KiB minimum the PRD requires for the default.

## 3. Hexadecimal digits in a chunk-size line

- **Full_PRD.md, FP-03, Normal behavior, chunked bullet (line 151):** "A received size line may carry up to 64 hexadecimal digits."
- **Full_PRD.md, FP-03, Normal behavior (line 161):** the chunk-size line is "a hexadecimal number of at most a fixed number of digits of the implementer's choice, from 16 to 32 inclusive," and FP-03 Boundary (line 168) refuses a size line with "more hexadecimal digits than that maximum."

Both cannot hold: a 40-digit size line is accepted by line 151 and refused by lines 161 and 168.

## 4. Whitespace after a chunk size

- **Full_PRD.md, FP-03, Normal behavior (line 161):** the size line may be "optionally followed by spaces or tabs, then the line ending."
- **Full_PRD.md, FP-03, Boundary (line 168):** "Whitespace after the chunk size is refused."

Both cannot hold: a size line such as `1a \r\n` is accepted by line 161 and refused by line 168.

## 5. Lone line feed as a line ending

- **Full_PRD.md, FP-02, Normal behavior (line 129):** "Received header blocks that use a lone line feed ... as line endings are accepted."
- **Interface_Contract.md, `receive_data` (line 98):** "every received line must end with a carriage return and line feed."

Both cannot hold: a received header line ending in a bare LF is accepted by the PRD and must be rejected by the contract.

## 6. Status line without a reason phrase

- **Full_PRD.md, FP-02, Normal behavior (line 129):** "A response status line that omits the reason phrase is accepted and the reason is empty."
- **Interface_Contract.md, `next_event()` (line 100):** "A received status line with no reason phrase after its status code is illegal."

Both cannot hold: the same status line is accepted by one and must raise `RemoteProtocolError` according to the other.

## 7. Obsolete line folding

- **Full_PRD.md, FP-02, Normal behavior (line 130):** obsolete line folding "is accepted when reading headers: each continuation line ... is joined to the previous header's value."
- **Full_PRD.md, FP-02, Boundary (line 136):** "A continuation line (a header line that begins with a space or tab) is refused."

Both cannot hold: a header line beginning with a space or tab is required to be joined by line 130 and refused by line 136.

## 8. Control bytes in header values

- **Full_PRD.md, FP-01, Normal behavior (line 95):** header values "may contain any byte other than NUL, carriage return, line feed, form feed, and vertical tab, including other control bytes and non-ASCII bytes."
- **Full_PRD.md, FP-01, Boundary (line 102):** "Control bytes other than tab are refused in header values."

Both cannot hold: a value containing, for example, byte 0x01 is stated to be allowed by line 95 and refused by line 102.

## 9. Framing headers on a response to HEAD

- **Full_PRD.md, FP-02, Normal behavior (line 122):** "A response to HEAD is written with no framing headers."
- **Full_PRD.md, FP-03, Normal behavior (line 159):** "A server answering HEAD writes the same framing headers it would have used for GET: chunked when the peer is HTTP/1.1, and connection-close framing when the peer is HTTP/1.0."

Both cannot hold: a HEAD response to an HTTP/1.1 peer is required to have no framing headers by line 122 and to carry `Transfer-Encoding: chunked` by line 159.

## 10. Content-Length: 0 on a response

- **Full_PRD.md, FP-03, Normal behavior (line 152):** "The `Content-Length` header is kept on the wire, including when N is 0."
- **Full_PRD.md, FP-03, Normal behavior (line 158):** "A response with `Content-Length: 0` is sent without that header, since its body is empty."

Both cannot hold: the same response with `Content-Length: 0` is required to keep the header by line 152 and to omit it by line 158.

## 11. Which framing header wins on a response

- **Full_PRD.md, FP-01, Normal behavior (line 94):** "When an event carries both framing headers, the `Content-Length` decides how the body is framed."
- **Full_PRD.md, FP-03, Normal behavior (line 156):** "If a response is constructed with both `Transfer-Encoding: chunked` and `Content-Length`, transfer-encoding wins: Content-Length is not sent."

Both cannot hold: a response carrying both headers is framed by Content-Length according to line 94 and by Transfer-Encoding according to line 156.

## 12. Case sensitivity of `100-continue`

- **Full_PRD.md, FP-07, Normal behavior (line 249):** a request whose `Expect` header "contains the token `100-continue` (matched case-insensitively)" sets the waiting flag.
- **Interface_Contract.md, `Connection` attributes (line 89):** "The `Expect` value must be exactly the lowercase token `100-continue`."

Both cannot hold: `Expect: 100-Continue` sets the flag under the PRD's case-insensitive rule and does not under the contract's exact-lowercase rule.

## 13. `Expect: 100-continue` on HTTP/1.0 requests

- **Full_PRD.md, FP-07, Normal behavior (line 249):** "An `Expect: 100-continue` header on an HTTP/1.0 request does not set either flag."
- **Interface_Contract.md, `Connection` attributes (line 88):** "any request with `Expect: 100-continue` sets it, whatever its HTTP version."

Both cannot hold: an HTTP/1.0 request with that header leaves the client flag unset under the PRD and sets it under the contract.

## 14. Whether the client's body ends the 100-continue wait

- **Full_PRD.md, FP-07, Normal behavior (line 248):** "The client stays waiting for 100-continue until the server answers; its own body events do not end the wait."
- **Full_PRD.md, FP-07, Normal behavior (line 250):** the waiting flags turn off "when the client sends any data event or its end-of-message."

Both cannot hold: after the client sends a data event, the flag is required to remain set by line 248 and to be cleared by line 250.

## 15. Which 2xx status accepts CONNECT

- **Full_PRD.md, FP-07, Normal behavior (lines 252 and 254):** "acceptance is a final response whose status is in the 2xx range"; "a 2xx response accepts CONNECT."
- **Full_PRD.md, FP-07, Boundary (line 263):** "Only status 200 accepts a CONNECT proposal; other 2xx statuses deny it."

Both cannot hold: a `201` answer to CONNECT is an acceptance under lines 252 and 254 and a denial under line 263.

## 16. Feeding bytes after a switch acceptance

- **Full_PRD.md, FP-07, Normal behavior (line 257):** after acceptance, "Bytes stored or fed after the accepting response are never parsed as HTTP; they accumulate, in order, in trailing data."
- **Full_PRD.md, FP-02, Boundary (line 138), and FP-06, Boundary (line 238):** feeding a non-empty chunk after an empty chunk "is refused at feed time as a runtime error."

Both cannot hold: after an accepted switch, if an empty chunk is fed (which sets the closed flag, line 258) and then non-empty bytes are fed, line 257 requires them to accumulate while lines 138 and 238 require a runtime error.
