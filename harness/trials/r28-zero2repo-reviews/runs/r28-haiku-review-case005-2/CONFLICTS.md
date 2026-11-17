# Specification conflicts

Each entry names two statements in `spec/` that cannot both hold for the same case. File and line numbers refer to the spec files as they currently exist. Ordering is by topic, not by severity.

## 1. Maximum Content-Length digits

- **Full_PRD.md, FP-01 "Boundary / error behavior", line 105:** "Every value of at most 18 digits is accepted; the maximum digit count is a fixed number of the implementer's choice, from 18 to 32 inclusive, and a longer value is refused."
- **Interface_Contract.md, `Events` section, line 46:** "A `Content-Length` value longer than 16 digits is refused."

Both cannot hold: a 17- or 18-digit value is required to be accepted by the PRD and refused by the Interface Contract.

## 2. Maximum hexadecimal digits in a chunk-size line

- **Full_PRD.md, FP-03 "Normal behavior", line 151:** "A received size line may carry up to 64 hexadecimal digits."
- **Full_PRD.md, FP-03 "Normal behavior", line 161:** "A chunk-size line is a hexadecimal number of at most a fixed number of digits of the implementer's choice, from 16 to 32 inclusive."

Both cannot hold: the first allows 64 digits as a guaranteed limit, while the second makes any limit above 32 digits a violation of the implementer's allowed range.

## 3. Default incomplete-event size limit

- **Full_PRD.md, FP-05 "Normal behavior", line 210:** "The default is a fixed value of the implementer's choice, at least 14 kibibytes and less than 18 kibibytes."
- **Interface_Contract.md, `Connection` section, line 76:** "When it is omitted, the limit is 8 kibibytes."

Both cannot hold: 8 KiB is below the 14 KiB minimum the PRD sets for the default.

## 4. Repeated `Transfer-Encoding: chunked` headers

- **Full_PRD.md, FP-01 "Normal behavior", line 94:** "Repeated `Transfer-Encoding: chunked` headers collapse to one."
- **Full_PRD.md, FP-01 "Boundary / error behavior", line 106:** "A second `Transfer-Encoding` header is refused with suggested status 501, even when both values are `chunked`."

Both cannot hold: the same input of two `Transfer-Encoding: chunked` headers is either collapsed into one header or refused.

## 5. Control bytes in header values

- **Full_PRD.md, FP-01 "Normal behavior", line 95:** "Header values may contain any byte other than NUL, carriage return, line feed, form feed, and vertical tab, including other control bytes and non-ASCII bytes."
- **Full_PRD.md, FP-01 "Boundary / error behavior", line 102:** "Control bytes other than tab are refused in header values."

Both cannot hold: line 95 allows control bytes such as BEL or ESC in header values, and line 102 refuses every control byte other than tab.

## 6. Obsolete line folding on receive

- **Full_PRD.md, FP-02 "Normal behavior", line 130:** "Obsolete line folding (RFC 7230 §3.2.4) is accepted when **reading** headers: each continuation line … is joined to the previous header's value."
- **Full_PRD.md, FP-02 "Boundary / error behavior", line 136:** "A continuation line (a header line that begins with a space or tab) is refused."

Both cannot hold: a received continuation line is either accepted and joined, or refused.

## 7. Bare line feed as a line ending

- **Full_PRD.md, FP-02 "Normal behavior", line 129:** "Received header blocks that use a lone line feed, or a mix of carriage-return/line-feed and lone line feed, as line endings are accepted."
- **Interface_Contract.md, `Connection` methods, `receive_data(data)`, line 98:** "every received line must end with a carriage return and line feed."

Both cannot hold: a received header line ending in a lone LF is either accepted (PRD) or must be rejected because it lacks CRLF (Interface Contract).

## 8. Status line without a reason phrase

- **Full_PRD.md, FP-02 "Normal behavior", line 129:** "A response status line that omits the reason phrase is accepted and the reason is empty."
- **Interface_Contract.md, `Connection` methods, `next_event()`, line 100:** "A received status line with no reason phrase after its status code is illegal."

Both cannot hold: the same received status line is either accepted with an empty reason or raises `RemoteProtocolError`.

## 9. Whitespace after a chunk-size value

- **Full_PRD.md, FP-03 "Normal behavior", line 161:** the chunk-size line may be "optionally followed by spaces or tabs, then the line ending."
- **Full_PRD.md, FP-03 "Boundary / error behavior", line 168:** "Whitespace after the chunk size is refused."

Both cannot hold: a chunk-size line with trailing spaces or tabs is either explicitly allowed or explicitly refused.

## 10. Framing headers on a response carrying both Content-Length and Transfer-Encoding

- **Full_PRD.md, FP-01 "Normal behavior", line 94:** "When an event carries both framing headers, the `Content-Length` decides how the body is framed."
- **Full_PRD.md, FP-03 "Normal behavior", line 156:** "If a response is constructed with both `Transfer-Encoding: chunked` and `Content-Length`, transfer-encoding wins: Content-Length is not sent."

Both cannot hold: for a response carrying both headers, FP-01 says Content-Length determines the framing while FP-03 says Transfer-Encoding determines it.

## 11. Framing headers on a response to HEAD

- **Full_PRD.md, FP-02 "Normal behavior", line 122:** "A response to HEAD is written with no framing headers."
- **Full_PRD.md, FP-03 "Normal behavior", line 159:** "A server answering HEAD writes the same framing headers it would have used for GET: chunked when the peer is HTTP/1.1, and connection-close framing when the peer is HTTP/1.0."

Both cannot hold: a HEAD response from an HTTP/1.1 peer is either sent with no framing headers or with `Transfer-Encoding: chunked`.

## 12. Response with `Content-Length: 0`

- **Full_PRD.md, FP-03 "Normal behavior", line 152:** "The `Content-Length` header is kept on the wire, including when N is 0."
- **Full_PRD.md, FP-03 "Normal behavior", line 158:** "A response with `Content-Length: 0` is sent without that header, since its body is empty."

Both cannot hold: a response with `Content-Length: 0` is either sent with that header (line 152) or without it (line 158). Line 158 sits in a bullet about HEAD, 204 and 304 responses, but its final sentence is stated as a general rule, so the two statements still collide for a 200 response with N = 0.

## 13. Case sensitivity of the `100-continue` token

- **Full_PRD.md, FP-07 "Normal behavior", line 249:** "whose `Expect` header contains the token `100-continue` (matched case-insensitively)".
- **Interface_Contract.md, `Connection` attributes, `they_are_waiting_for_100_continue`, line 89:** "The `Expect` value must be exactly the lowercase token `100-continue`."

Both cannot hold: a request with `Expect: 100-Continue` is recorded as waiting by the PRD and not recorded by the Interface Contract.

## 14. `Expect: 100-continue` on an HTTP/1.0 request

- **Full_PRD.md, FP-07 "Normal behavior", line 249:** "An `Expect: 100-continue` header on an HTTP/1.0 request does not set either flag."
- **Interface_Contract.md, `Connection` attributes, `client_is_waiting_for_100_continue`, line 88:** "any request with `Expect: 100-continue` sets it, whatever its HTTP version."

Both cannot hold: for an HTTP/1.0 request with `Expect: 100-continue`, the PRD says the flag stays false and the Interface Contract says it becomes true.

## 15. Which 2xx status accepts a CONNECT proposal

- **Full_PRD.md, FP-07 "Normal behavior", lines 252 and 254:** "acceptance is a final response whose status is in the 2xx range"; "a 2xx response accepts CONNECT".
- **Full_PRD.md, FP-07 "Boundary / error behavior", line 263:** "Only status 200 accepts a CONNECT proposal; other 2xx statuses deny it."

Both cannot hold: a 201 or 204 final response to CONNECT is an acceptance under lines 252 and 254 and a denial under line 263.
