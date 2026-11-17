# Specification conflicts

Each entry is a pair of statements in `spec/` that cannot both hold for the same case. Line numbers refer to the lines of the named file.

## 1. Content-Length digit limit

- **A:** `spec/Full_PRD.md`, FP-01 "Boundary / error behavior", line 105: "Every value of at most 18 digits is accepted; the maximum digit count is a fixed number of the implementer's choice, from 18 to 32 inclusive."
- **B:** `spec/Interface_Contract.md`, "Events", bullet on `headers`: "A `Content-Length` value longer than 16 digits is refused."
- **Why:** A 17- or 18-digit Content-Length must be accepted by A and refused by B.

## 2. Maximum hexadecimal digits in a chunk-size line

- **A:** `spec/Full_PRD.md`, FP-03 "Normal behavior", line 151: "A received size line may carry up to 64 hexadecimal digits."
- **B:** `spec/Full_PRD.md`, FP-03 "Normal behavior", line 161: the maximum is "a fixed number of digits of the implementer's choice, from 16 to 32 inclusive"; and FP-03 "Boundary / error behavior", line 168: a size line with "more hexadecimal digits than that maximum" is refused.
- **Why:** A 33- to 64-digit chunk-size line is required by A and refused by B, since B caps the maximum at 32.

## 3. Default incomplete-event size limit

- **A:** `spec/Interface_Contract.md`, "`Connection` > Signature", bullet on `max_incomplete_event_size`: "When it is omitted, the limit is 8 kibibytes."
- **B:** `spec/Full_PRD.md`, FP-05 "Normal behavior", line 210: "The default is a fixed value of the implementer's choice, at least 14 kibibytes and less than 18 kibibytes."
- **Why:** A default of 8 KiB is below the 14 KiB minimum that B requires, so both cannot hold for an omitted limit.

## 4. Status line with no reason phrase

- **A:** `spec/Full_PRD.md`, FP-02 "Normal behavior", line 129: "A response status line that omits the reason phrase is accepted and the reason is empty."
- **B:** `spec/Interface_Contract.md`, "`Connection` > Methods", `next_event()`: "A received status line with no reason phrase after its status code is illegal."
- **Why:** The same received status line must be accepted under A and raise `RemoteProtocolError` under B.

## 5. Bare line feed as a line ending

- **A:** `spec/Full_PRD.md`, FP-02 "Normal behavior", line 129: "Received header blocks that use a lone line feed ... as line endings are accepted."
- **B:** `spec/Interface_Contract.md`, "`Connection` > Methods", `receive_data(data)`: "every received line must end with a carriage return and line feed."
- **Why:** A header block with lone-LF line endings is accepted by A and rejected by B.

## 6. Obsolete line folding

- **A:** `spec/Full_PRD.md`, FP-02 "Normal behavior", line 130: "Obsolete line folding (RFC 7230 §3.2.4) is accepted when reading headers: each continuation line ... is joined to the previous header's value."
- **B:** `spec/Full_PRD.md`, FP-02 "Boundary / error behavior", line 136: "A continuation line (a header line that begins with a space or tab) is refused."
- **Why:** A continuation line must be joined under A and refused under B.

## 7. Whitespace after a chunk-size line

- **A:** `spec/Full_PRD.md`, FP-03 "Normal behavior", line 161: a chunk-size line is "optionally followed by spaces or tabs, then the line ending."
- **B:** `spec/Full_PRD.md`, FP-03 "Boundary / error behavior", line 168: "Whitespace after the chunk size is refused."
- **Why:** A chunk-size line with trailing spaces or tabs and no extension is allowed by A and refused by B.

## 8. Repeated `Transfer-Encoding: chunked` headers

- **A:** `spec/Full_PRD.md`, FP-01 "Normal behavior", line 94: "Repeated `Transfer-Encoding: chunked` headers collapse to one."
- **B:** `spec/Full_PRD.md`, FP-01 "Boundary / error behavior", line 106: "A second `Transfer-Encoding` header is refused with suggested status 501, even when both values are `chunked`."
- **Why:** Two `Transfer-Encoding: chunked` headers are collapsed to one under A and refused under B.

## 9. Both framing headers on a response

- **A:** `spec/Full_PRD.md`, FP-01 "Normal behavior", line 94: "When an event carries both framing headers, the `Content-Length` decides how the body is framed."
- **B:** `spec/Full_PRD.md`, FP-03 "Normal behavior", line 156: "If a response is constructed with both `Transfer-Encoding: chunked` and `Content-Length`, transfer-encoding wins: Content-Length is not sent."
- **Why:** For a response carrying both headers, A says Content-Length decides the framing and B says Transfer-Encoding decides it, so the two cannot both hold.

## 10. Content-Length: 0 on a response

- **A:** `spec/Full_PRD.md`, FP-03 "Normal behavior", line 152: "The `Content-Length` header is kept on the wire, including when N is 0."
- **B:** `spec/Full_PRD.md`, FP-03 "Normal behavior", line 158: "A response with `Content-Length: 0` is sent without that header, since its body is empty."
- **Why:** A response with `Content-Length: 0` is required to keep the header under A and to omit it under B.

## 11. Framing headers on a response to HEAD

- **A:** `spec/Full_PRD.md`, FP-02 "Normal behavior", line 122: "A response to HEAD is written with no framing headers."
- **B:** `spec/Full_PRD.md`, FP-03 "Normal behavior", line 159: "A server answering HEAD writes the same framing headers it would have used for GET: chunked when the peer is HTTP/1.1, and connection-close framing when the peer is HTTP/1.0."
- **Why:** A HEAD response to an HTTP/1.1 peer must carry no framing headers under A and must carry `Transfer-Encoding: chunked` under B.

## 12. Control bytes in header values

- **A:** `spec/Full_PRD.md`, FP-01 "Normal behavior", line 95: a header value may contain "any byte other than NUL, carriage return, line feed, form feed, and vertical tab, including other control bytes and non-ASCII bytes."
- **B:** `spec/Full_PRD.md`, FP-01 "Boundary / error behavior", line 102: "Control bytes other than tab are refused in header values."
- **Why:** A value containing a control byte such as 0x01 is allowed by A and refused by B.

## 13. `Expect: 100-continue` on HTTP/1.0 requests

- **A:** `spec/Full_PRD.md`, FP-07 "Normal behavior", line 249: a request "of HTTP version `1.1` whose `Expect` header contains the token `100-continue` ... makes the connection record that the client is waiting"; "An `Expect: 100-continue` header on an HTTP/1.0 request does not set either flag."
- **B:** `spec/Interface_Contract.md`, "`Connection` > Attributes", `client_is_waiting_for_100_continue`: "any request with `Expect: 100-continue` sets it, whatever its HTTP version."
- **Why:** An HTTP/1.0 request with `Expect: 100-continue` must leave the flag unset under A and set it under B.

## 14. Case sensitivity of the `Expect` token

- **A:** `spec/Full_PRD.md`, FP-07 "Normal behavior", line 249: the token is "matched case-insensitively."
- **B:** `spec/Interface_Contract.md`, "`Connection` > Attributes", `they_are_waiting_for_100_continue`: "The `Expect` value must be exactly the lowercase token `100-continue`."
- **Why:** A request with `Expect: 100-Continue` sets the flag under A and does not under B.

## 15. Whether the client's body clears the 100-continue wait

- **A:** `spec/Full_PRD.md`, FP-07 "Normal behavior", line 248: "The client stays waiting for 100-continue until the server answers; its own body events do not end the wait."
- **B:** `spec/Full_PRD.md`, FP-07 "Normal behavior", line 250: the flags turn off "when the client sends any data event or its end-of-message."
- **Why:** Sending a data event leaves the client waiting under A and turns the waiting flag off under B.

## 16. Which 2xx status accepts CONNECT

- **A:** `spec/Full_PRD.md`, FP-07 "Normal behavior", line 252: "acceptance is a final response whose status is in the 2xx range"; line 254: "a 2xx response accepts CONNECT."
- **B:** `spec/Full_PRD.md`, FP-07 "Boundary / error behavior", line 263: "Only status 200 accepts a CONNECT proposal; other 2xx statuses deny it."
- **Why:** A 201 or 204 answer to CONNECT is an acceptance under A and a denial under B.

## 17. Matching of the `close` token in `Connection`

- **A:** `spec/Full_PRD.md`, Terminology table, "Keep-alive", line 36: "Any `Connection` value that contains `close` turns it off."
- **B:** `spec/Full_PRD.md`, FP-04 "Normal behavior", line 181: the token is matched "as a whole element of the comma-separated `Connection` value."
- **Why:** For `Connection: closed`, A turns keep-alive off because the value contains `close` as a substring, while B leaves it on because `closed` is not the token `close`.
